#!/usr/bin/env python3
"""Generate Python transition cases from a TLC DOT state graph dump.

This script is intentionally generic: it does not know product domains or
Python fake templates. It treats TLC as the case source of truth:

    TLC states and action-labeled edges -> Python case descriptors.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib
import inspect
import json
import math
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

try:
    import resource
except ImportError:  # pragma: no cover - Unix is the supported runtime
    resource = None  # type: ignore[assignment]

try:
    from .extract_spec_manifest import load_manifest
    from .spec_paths import resolve_existing_from_cwd, resolve_existing_spec_input, resolve_spec_dir, resolve_spec_relative_path
except ImportError:  # pragma: no cover - direct script execution
    from extract_spec_manifest import load_manifest
    from spec_paths import resolve_existing_from_cwd, resolve_existing_spec_input, resolve_spec_dir, resolve_spec_relative_path


NODE_RE = re.compile(r'^\s*(-?\d+) \[label="(.*)"(?:,style = filled)?\];?$')
EDGE_RE = re.compile(r'^\s*(-?\d+) -> (-?\d+) \[label="([^"]+)"')
TRACE_SCHEMA_VERSION = "tla-testgraph.trace.v1"
CASE_MANIFEST_SCHEMA_VERSION = "cdc.case-manifest.v1"
CASE_ENVELOPE_SCHEMA_VERSION = "cdc.case-envelope.v1"
STREAM_PROTOCOL_VERSION = "cdc.tlc-case-stream.v1"
SELECTION_POLICY = "stable-hash-stratified"
DEFAULT_MAX_CASES = 10_000
DEFAULT_MAX_OUTPUT_BYTES = 128 * 1024 * 1024
DEFAULT_MAX_RSS_MIB = 512.0
DEFAULT_MAX_SECONDS = 120.0
LEGACY_GENERATED_FILES = (
    "__init__.py",
    "types.py",
    "cases.py",
    "doubles.py",
    "validators.py",
    "docs.md",
)
VIEW_OUTPUT_DIRS = {"internal": "spec-unit", "external": "testgraph"}
VIEW_GENERATES = {"internal": "spec_unit", "external": "testgraph"}
DEFAULT_CONTROLLABILITY = {"internal": "unit_direct", "external": "e2e_direct"}
SUPPORTED_VIEWS = frozenset(VIEW_GENERATES)
SUPPORTED_CONTROLLABILITY = frozenset({"unit_direct", "e2e_direct", "environment", "observable", "hidden"})


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    action: str


@dataclass(frozen=True)
class ActionMetadata:
    name: str
    layer: str
    controllability: str
    generates: tuple[str, ...]
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class PreparedCase:
    name: str
    edge: Edge
    before: dict[str, Any]
    after: dict[str, Any]
    params: dict[str, Any]
    output_value: Any
    output_expression: str
    changes: dict[str, dict[str, Any]]
    labels: tuple[str, ...]
    metadata: ActionMetadata


@dataclass(frozen=True)
class CaseBudgets:
    max_cases: int = DEFAULT_MAX_CASES
    max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES
    max_rss_mib: float = DEFAULT_MAX_RSS_MIB
    max_seconds: float = DEFAULT_MAX_SECONDS

    def __post_init__(self) -> None:
        for name in ("max_cases", "max_output_bytes"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        for name in ("max_rss_mib", "max_seconds"):
            value = getattr(self, name)
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or value <= 0
            ):
                raise ValueError(f"{name} must be positive")

    def as_dict(self) -> dict[str, int | float]:
        return {
            "max_cases": self.max_cases,
            "max_output_bytes": self.max_output_bytes,
            "max_rss_mib": self.max_rss_mib,
            "max_seconds": self.max_seconds,
        }


@dataclass
class GenerationAccounting:
    state_count: int = 0
    observed_transition_count: int = 0
    eligible_transition_count: int = 0
    candidate_case_count: int = 0
    selected_case_count: int = 0
    staged_case_count: int = 0
    emitted_case_count: int = 0
    output_bytes: int = 0


@dataclass(frozen=True)
class StreamingGenerationResult:
    manifest_path: Path
    cases_path: Path
    manifest: dict[str, Any]
    exit_code: int


class BudgetExceeded(RuntimeError):
    def __init__(self, budget: str, limit: int | float, observed: int | float, stage: str):
        super().__init__(f"{budget} exceeded during {stage}: observed {observed}, limit {limit}")
        self.budget = budget
        self.limit = limit
        self.observed = observed
        self.stage = stage

    def as_dict(self) -> dict[str, Any]:
        return {
            "type": "budget_exceeded",
            "budget": self.budget,
            "limit": self.limit,
            "observed": self.observed,
            "stage": self.stage,
        }


class ResourceBudget:
    def __init__(self, budgets: CaseBudgets, started_at: float | None = None):
        self.budgets = budgets
        self.started_at = started_at if started_at is not None else time.monotonic()

    def elapsed_seconds(self) -> float:
        return max(0.0, time.monotonic() - self.started_at)

    def peak_rss_mib(self) -> float:
        if resource is None:
            return 0.0
        peak = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        if sys.platform == "darwin":
            return peak / (1024.0 * 1024.0)
        return peak / 1024.0

    def check(self, stage: str) -> None:
        elapsed = self.elapsed_seconds()
        if elapsed > self.budgets.max_seconds:
            raise BudgetExceeded("max_seconds", self.budgets.max_seconds, elapsed, stage)
        peak_rss = self.peak_rss_mib()
        if peak_rss > self.budgets.max_rss_mib:
            raise BudgetExceeded("max_rss_mib", self.budgets.max_rss_mib, peak_rss, stage)


def run_tlc_dump(
    tla_path: Path,
    cfg_path: Path,
    dot_path: Path,
    tlc2: str,
    *,
    timeout_seconds: float | None = None,
) -> None:
    dot_path.parent.mkdir(parents=True, exist_ok=True)
    spec_dir = tla_path.parent.resolve()
    metadir = dot_path.parent / ".tlc-states" / tla_path.stem
    command = [
        tlc2,
        "-cleanup",
        "-deadlock",
        "-fp",
        "1",
        "-metadir",
        str(metadir.resolve()),
        "-config",
        str(cfg_path.resolve()),
        "-dump",
        "dot,actionlabels",
        str(dot_path.resolve()),
        str(tla_path.resolve()),
    ]
    try:
        subprocess.run(command, check=True, cwd=spec_dir, timeout=timeout_seconds)
    finally:
        shutil.rmtree(metadir, ignore_errors=True)


def load_dot(path: Path) -> tuple[dict[str, dict[str, Any]], list[Edge]]:
    states: dict[str, dict[str, Any]] = {}
    edges: list[Edge] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            node_match = NODE_RE.match(line)
            if node_match:
                node_id, raw_label = node_match.groups()
                states[node_id] = parse_state_label(raw_label)
                continue
            edge_match = EDGE_RE.match(line)
            if edge_match:
                source, target, action = edge_match.groups()
                edges.append(Edge(source=source, target=target, action=action))
    return states, edges


def load_dot_states(
    path: Path,
    guard: ResourceBudget,
    accounting: GenerationAccounting,
) -> dict[str, dict[str, Any]]:
    """Load only state records; transition arrays stay on disk."""

    states: dict[str, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            node_match = NODE_RE.match(line)
            if node_match:
                node_id, raw_label = node_match.groups()
                states[node_id] = parse_state_label(raw_label)
            elif EDGE_RE.match(line):
                accounting.observed_transition_count += 1
            if line_number % 256 == 0:
                guard.check("dot-state-scan")
    accounting.state_count = len(states)
    guard.check("dot-state-scan")
    return states


def iter_dot_edges(path: Path) -> Iterator[tuple[int, Edge]]:
    """Yield edges in source order without retaining the transition graph."""

    ordinal = 0
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            edge_match = EDGE_RE.match(line)
            if not edge_match:
                continue
            ordinal += 1
            source, target, action = edge_match.groups()
            yield ordinal, Edge(source=source, target=target, action=action)


def parse_state_label(raw_label: str) -> dict[str, Any]:
    state: dict[str, Any] = {}
    raw_label = raw_label.replace(r"\"", '"')
    current: tuple[str, str] | None = None
    for raw_part in raw_label.split(r"\n"):
        part = raw_part.strip()
        while part.startswith(("/", "\\")):
            part = part[1:].strip()
        if " = " not in part:
            if current is not None and part:
                current = (current[0], f"{current[1]} {part}")
            continue
        if current is not None:
            state[current[0]] = parse_tlc_value(current[1].strip())
        name, value = part.split(" = ", 1)
        current = (name.strip(), value.strip())
    if current is not None:
        state[current[0]] = parse_tlc_value(current[1].strip())
    return state


def parse_tlc_value(value: str) -> Any:
    if value == "{}":
        return frozenset()
    if value.startswith("{") and value.endswith("}"):
        body = value[1:-1].strip()
        if not body:
            return frozenset()
        return frozenset(freeze_set_member(parse_tlc_value(part.strip())) for part in split_top_level(body, ","))
    if value.startswith("[") and value.endswith("]") and "|->" in value:
        return parse_tlc_record(value)
    if value.startswith("(") and value.endswith(")") and ":>" in value:
        return parse_tlc_function(value)
    if value.startswith("<<") and value.endswith(">>"):
        body = value[2:-2].strip()
        if not body:
            return ()
        return tuple(parse_tlc_value(part.strip()) for part in split_top_level(body, ","))
    return parse_atom(value)


def parse_tlc_function(value: str) -> dict[str, Any]:
    body = value[1:-1].strip()
    result: dict[str, Any] = {}
    for part in split_top_level(body, "@@"):
        split = split_top_level_once(part, ":>")
        if split is None:
            continue
        key, raw_value = split
        result[str(parse_atom(key.strip()))] = parse_tlc_value(raw_value.strip())
    return result


def parse_tlc_record(value: str) -> dict[str, Any]:
    body = value[1:-1].strip()
    result: dict[str, Any] = {}
    if not body:
        return result
    for part in split_top_level(body, ","):
        split = split_top_level_once(part, "|->")
        if split is None:
            continue
        key, raw_value = split
        result[str(parse_atom(key.strip()))] = parse_tlc_value(raw_value.strip())
    return result


def freeze_set_member(value: Any) -> Any:
    if isinstance(value, dict):
        return frozenset((key, freeze_set_member(inner)) for key, inner in value.items())
    if isinstance(value, list):
        return tuple(freeze_set_member(inner) for inner in value)
    if isinstance(value, tuple):
        return tuple(freeze_set_member(inner) for inner in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(freeze_set_member(inner) for inner in value)
    return value


def split_top_level_once(value: str, separator: str) -> tuple[str, str] | None:
    parts = split_top_level(value, separator, maxsplit=1)
    if len(parts) != 2:
        return None
    return parts[0], parts[1]


def split_top_level(value: str, separator: str, maxsplit: int = -1) -> list[str]:
    parts: list[str] = []
    start = 0
    index = 0
    splits = 0
    stack: list[str] = []
    in_string = False
    while index < len(value):
        if in_string:
            if value[index] == '"' and not is_escaped(value, index):
                in_string = False
            index += 1
            continue

        if value[index] == '"':
            in_string = True
            index += 1
            continue

        if value.startswith("<<", index):
            stack.append(">>")
            index += 2
            continue

        if stack and value.startswith(stack[-1], index):
            index += len(stack.pop())
            continue

        if value[index] in "({[":
            stack.append({"(": ")", "{": "}", "[": "]"}[value[index]])
            index += 1
            continue

        if stack and value[index] == stack[-1]:
            stack.pop()
            index += 1
            continue

        if not stack and value.startswith(separator, index) and (maxsplit < 0 or splits < maxsplit):
            parts.append(value[start:index].strip())
            index += len(separator)
            start = index
            splits += 1
            continue

        index += 1

    parts.append(value[start:].strip())
    return parts


def is_escaped(value: str, index: int) -> bool:
    slash_count = 0
    cursor = index - 1
    while cursor >= 0 and value[cursor] == "\\":
        slash_count += 1
        cursor -= 1
    return slash_count % 2 == 1


def parse_atom(value: str) -> Any:
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value == "TRUE":
        return True
    if value == "FALSE":
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


def normalize_string_list(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(str(item) for item in value)
    raise ValueError(f"expected string or list of strings, got {value!r}")


def default_action_metadata(action: str, view: str) -> ActionMetadata:
    return ActionMetadata(
        name=action,
        layer=view,
        controllability=DEFAULT_CONTROLLABILITY[view],
        generates=(VIEW_GENERATES[view],),
    )


def load_action_metadata(path: Path | None, spec_dir: Path | None = None) -> dict[str, ActionMetadata]:
    if path is None:
        return {}
    metadata_path = resolve_existing_spec_input(path, spec_dir) if spec_dir is not None else resolve_existing_from_cwd(path)
    loaded = load_manifest(metadata_path)
    raw_actions = loaded.get("actions", loaded)
    if not isinstance(raw_actions, dict):
        raise ValueError(f"action metadata root must be a mapping: {metadata_path}")

    metadata: dict[str, ActionMetadata] = {}
    for action, raw_spec in raw_actions.items():
        if raw_spec is None:
            raw_spec = {}
        if not isinstance(raw_spec, dict):
            raise ValueError(f"action metadata for {action} must be a mapping")
        layer = str(raw_spec.get("layer", "internal"))
        if layer not in SUPPORTED_VIEWS:
            raise ValueError(f"unsupported layer for {action}: {layer}")
        controllability = str(raw_spec.get("controllability", DEFAULT_CONTROLLABILITY[layer]))
        if controllability not in SUPPORTED_CONTROLLABILITY:
            raise ValueError(f"unsupported controllability for {action}: {controllability}")
        metadata[str(action)] = ActionMetadata(
            name=str(action),
            layer=layer,
            controllability=controllability,
            generates=normalize_string_list(raw_spec.get("generates", (VIEW_GENERATES[layer],))),
            tags=normalize_string_list(raw_spec.get("tags", ())),
        )
    return metadata


def action_metadata_for(action: str, view: str, metadata: dict[str, ActionMetadata]) -> ActionMetadata:
    return metadata.get(action) or default_action_metadata(action, view)


def should_emit_action(action_metadata: ActionMetadata, view: str) -> bool:
    return action_metadata.layer == view and VIEW_GENERATES[view] in set(action_metadata.generates)


def changed_fields(before: dict[str, Any], after: dict[str, Any]) -> dict[str, dict[str, Any]]:
    fields = sorted(set(before) | set(after))
    return {
        field: {"before": before.get(field), "after": after.get(field)}
        for field in fields
        if before.get(field) != after.get(field)
    }


def to_plain_value(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): to_plain_value(inner) for key, inner in sorted(value.items(), key=lambda item: repr(item[0]))}
    if isinstance(value, tuple):
        return [to_plain_value(inner) for inner in value]
    if isinstance(value, (set, frozenset)):
        return [to_plain_value(inner) for inner in sorted(value, key=repr)]
    return value


def freeze_for_signature(value: Any) -> Any:
    if isinstance(value, dict):
        return tuple((str(key), freeze_for_signature(inner)) for key, inner in sorted(value.items(), key=lambda item: repr(item[0])))
    if isinstance(value, (list, tuple)):
        return tuple(freeze_for_signature(inner) for inner in value)
    if isinstance(value, (set, frozenset)):
        return tuple(sorted((freeze_for_signature(inner) for inner in value), key=repr))
    return value


def params_from_action_marker(edge: Edge, after: dict[str, Any], view: str) -> dict[str, Any]:
    marker_name = "lastExternalAction" if view == "external" else "lastInternalAction"
    marker = after.get(marker_name)
    if not isinstance(marker, dict) or marker.get("name") != edge.action:
        return {}
    params = marker.get("params", {})
    if params in (None, (), [], frozenset()):
        return {}
    if not isinstance(params, dict):
        return {}
    return dict(to_plain_value(params))


def case_name(index: int, action: str) -> str:
    snake = re.sub(r"(?<!^)([A-Z])", r"_\1", action).lower()
    snake = re.sub(r"[^a-z0-9_]+", "_", snake).strip("_")
    return f"case_{index:04d}_{snake}"


def py_repr(value: Any) -> str:
    if isinstance(value, frozenset):
        if not value:
            return "frozenset()"
        items = ", ".join(py_repr(item) for item in sorted(value, key=repr))
        return f"frozenset([{items}])"
    if isinstance(value, tuple):
        items = ", ".join(py_repr(item) for item in value)
        if len(value) == 1:
            items += ","
        return f"({items})"
    if isinstance(value, dict):
        items = ", ".join(f"{key!r}: {py_repr(inner)}" for key, inner in sorted(value.items(), key=lambda item: repr(item[0])))
        return "{" + items + "}"
    return repr(value)


def load_object(path: str) -> Any:
    module_name, sep, object_name = path.partition(":")
    if not sep:
        raise ValueError(f"object path must be module:object, got {path!r}")
    module = importlib.import_module(module_name)
    obj: Any = module
    for part in object_name.split("."):
        obj = getattr(obj, part)
    return obj


def labels_for_case(
    *,
    before: dict[str, Any],
    action: str,
    after: dict[str, Any],
    changes: dict[str, dict[str, Any]],
    labelers: list[Any],
) -> list[str]:
    labels = [action]
    for labeler in labelers:
        try:
            produced = labeler(before=before, action=action, after=after, changed=changes)
        except TypeError as exc:
            if "keyword" not in str(exc) and "argument" not in str(exc):
                raise
            produced = labeler(before, action, after, changes)
        if isinstance(produced, str):
            produced = [produced]
        if produced is None:
            continue
        for label in produced:
            rendered = str(label)
            if rendered and rendered not in labels:
                labels.append(rendered)
    return labels


def call_state_projector(projector: Any | None, state: dict[str, Any]) -> dict[str, Any]:
    if projector is None:
        return state
    try:
        projected = projector(state=state)
    except TypeError as exc:
        if "keyword" not in str(exc) and "argument" not in str(exc):
            raise
        projected = projector(state)
    if not isinstance(projected, dict):
        raise TypeError(f"state projector must return a dict, got {type(projected).__name__}")
    return projected


def call_output_projector(
    projector: Any | None,
    *,
    before: dict[str, Any],
    after: dict[str, Any],
    projected_before: dict[str, Any],
    projected_after: dict[str, Any],
    action: str,
    params: dict[str, Any],
    changed: dict[str, dict[str, Any]],
    view: str,
) -> tuple[Any, str]:
    if projector is None:
        return changed, f"StateGraphOutput(changed={py_repr(changed)})"
    try:
        output = projector(
            before=before,
            after=after,
            projected_before=projected_before,
            projected_after=projected_after,
            action=action,
            params=params,
            changed=changed,
            view=view,
        )
    except TypeError as exc:
        if "keyword" not in str(exc) and "argument" not in str(exc):
            raise
        output = projector(before, action, after, params)
    return output, py_repr(output)


def prepare_case(
    *,
    name_index: int,
    states: dict[str, dict[str, Any]],
    edge: Edge,
    view: str,
    action_metadata: dict[str, ActionMetadata],
    labelers: list[Any],
    state_projector: Any | None,
    output_projector: Any | None,
) -> PreparedCase:
    try:
        raw_before = states[edge.source]
        raw_after = states[edge.target]
    except KeyError as exc:
        raise ValueError(
            f"transition {edge.source}->{edge.target} ({edge.action}) references missing state {exc.args[0]}"
        ) from exc
    before = call_state_projector(state_projector, raw_before)
    after = call_state_projector(state_projector, raw_after)
    params = params_from_action_marker(edge, raw_after, view)
    changes = changed_fields(before, after)
    output_value, output_expression = call_output_projector(
        output_projector,
        before=raw_before,
        after=raw_after,
        projected_before=before,
        projected_after=after,
        action=edge.action,
        params=params,
        changed=changes,
        view=view,
    )
    labels = labels_for_case(before=before, action=edge.action, after=after, changes=changes, labelers=labelers)
    return PreparedCase(
        name=case_name(name_index, edge.action),
        edge=edge,
        before=before,
        after=after,
        params=params,
        output_value=output_value,
        output_expression=output_expression,
        changes=changes,
        labels=tuple(labels),
        metadata=action_metadata_for(edge.action, view, action_metadata),
    )


def prepare_cases(
    *,
    states: dict[str, dict[str, Any]],
    edges: list[Edge],
    view: str,
    action_metadata: dict[str, ActionMetadata],
    labelers: list[Any],
    state_projector: Any | None,
    output_projector: Any | None,
    dedupe: str,
) -> list[PreparedCase]:
    prepared: list[PreparedCase] = []
    seen: set[Any] = set()
    for edge in edges:
        case = prepare_case(
            name_index=len(prepared) + 1,
            states=states,
            edge=edge,
            view=view,
            action_metadata=action_metadata,
            labelers=labelers,
            state_projector=state_projector,
            output_projector=output_projector,
        )
        if dedupe == "projected":
            signature = freeze_for_signature(
                {
                    "action": edge.action,
                    "params": case.params,
                    "before": case.before,
                    "after": case.after,
                    "output": case.output_value,
                }
            )
            if signature in seen:
                continue
            seen.add(signature)
        prepared.append(case)
    return prepared


def canonical_value(value: Any) -> Any:
    """Return the language-neutral JSON value used by the streaming protocol."""

    if isinstance(value, dict):
        return {
            str(key): canonical_value(inner)
            for key, inner in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, (set, frozenset)):
        members = [canonical_value(inner) for inner in value]
        return sorted(members, key=canonical_json_bytes)
    if isinstance(value, (list, tuple)):
        return [canonical_value(inner) for inner in value]
    if isinstance(value, Path):
        encoded = base64.urlsafe_b64encode(os.fsencode(value)).decode("ascii").rstrip("=")
        return {"$path_bytes_base64url": encoded}
    if isinstance(value, bytes):
        encoded = base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")
        return {"$bytes_base64url": encoded}
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non-finite floats are not valid canonical JSON")
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"unsupported canonical JSON value: {type(value).__name__}")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        canonical_value(value),
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def sha256_digest(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def callable_identity(callback: Any | None, declared: str | None = None) -> str | None:
    if declared:
        return declared
    if callback is None:
        return None
    return f"{getattr(callback, '__module__', '<unknown>')}:{getattr(callback, '__qualname__', repr(callback))}"


def callable_fingerprint(callback: Any | None, declared: str | None = None) -> dict[str, Any] | None:
    identity = callable_identity(callback, declared)
    if callback is None:
        return None
    target = callback if inspect.isfunction(callback) or inspect.ismethod(callback) else type(callback)
    try:
        source_file = inspect.getsourcefile(target)
    except TypeError:
        source_file = None
    if source_file and Path(source_file).is_file():
        implementation_digest = file_sha256(Path(source_file))
    else:
        try:
            implementation_digest = sha256_digest(inspect.getsource(target).encode("utf-8"))
        except (OSError, TypeError):
            implementation_digest = sha256_digest(repr(target).encode("utf-8"))
    return {
        "identity": identity,
        "implementation_digest": implementation_digest,
    }


def call_outcome_projector(projector: Any | None, case: PreparedCase) -> str:
    if projector is not None:
        try:
            outcome = projector(
                before=case.before,
                action=case.edge.action,
                after=case.after,
                params=case.params,
                output=case.output_value,
                changed=case.changes,
            )
        except TypeError as exc:
            if "keyword" not in str(exc) and "argument" not in str(exc):
                raise
            outcome = projector(case.before, case.edge.action, case.after, case.output_value)
        return render_outcome(outcome)

    for container in (case.output_value, case.after):
        if not isinstance(container, dict):
            continue
        for key in ("outcome", "status", "result", "kind", "code"):
            if key in container:
                return f"{key}:{render_outcome(container[key])}"
    changed_names = ",".join(sorted(case.changes)) or "none"
    return f"changes:{changed_names}"


def render_outcome(value: Any) -> str:
    canonical = canonical_value(value)
    if canonical is None:
        return "null"
    if isinstance(canonical, bool):
        return "true" if canonical else "false"
    if isinstance(canonical, (str, int, float)):
        return str(canonical)
    return sha256_digest(canonical_json_bytes(canonical))


def semantic_case_payload(case: PreparedCase, view: str) -> dict[str, Any]:
    return {
        "view": view,
        "action": case.edge.action,
        "tlc_source_id": case.edge.source,
        "tlc_target_id": case.edge.target,
        "before": canonical_value(case.before),
        "input": {
            "action": case.edge.action,
            "params": canonical_value(case.params),
        },
        "expected_output": canonical_value(case.output_value),
        "after": canonical_value(case.after),
        "expected_projection": canonical_value(case.after),
    }


def projection_digest(
    *,
    view: str,
    dedupe: str,
    state_projector: Any | None,
    output_projector: Any | None,
    outcome_projector: Any | None,
    declared_state_projector: str | None,
    declared_output_projector: str | None,
    declared_outcome_projector: str | None,
) -> str:
    return sha256_digest(
        canonical_json_bytes(
            {
                "view": view,
                "dedupe": dedupe,
                "state_projector": callable_fingerprint(state_projector, declared_state_projector),
                "output_projector": callable_fingerprint(output_projector, declared_output_projector),
                "outcome_projector": callable_fingerprint(outcome_projector, declared_outcome_projector),
            }
        )
    )


def stable_candidate_hash(
    *,
    seed: str,
    action: str,
    outcome: str,
    semantic_digest: str,
    ordinal: int,
) -> str:
    return hashlib.sha256(
        canonical_json_bytes(
            {
                "seed": seed,
                "action": action,
                "outcome": outcome,
                "semantic_digest": semantic_digest,
                "transition_ordinal": ordinal,
            }
        )
    ).hexdigest()


def stable_stratum_hash(seed: str, action: str, outcome: str) -> str:
    return hashlib.sha256(
        canonical_json_bytes({"seed": seed, "action": action, "outcome": outcome})
    ).hexdigest()


def case_envelope(
    *,
    case: PreparedCase,
    view: str,
    tier: str,
    seed: str,
    ordinal: int,
    selection_index: int,
    outcome: str,
    stable_hash: str,
    budgets: CaseBudgets,
    source_digests: dict[str, str],
) -> tuple[dict[str, Any], str]:
    semantic = semantic_case_payload(case, view)
    semantic_digest = sha256_digest(canonical_json_bytes(semantic))
    case_id = sha256_digest(
        canonical_json_bytes(
            {
                "source_digests": source_digests,
                "transition_ordinal": ordinal,
                "semantic_digest": semantic_digest,
            }
        )
    )
    record: dict[str, Any] = {
        "schema_version": CASE_ENVELOPE_SCHEMA_VERSION,
        "case_id": case_id,
        "view": view,
        "action": case.edge.action,
        "outcome": outcome,
        "labels": sorted(set(str(label) for label in case.labels)),
        "tlc_source_id": case.edge.source,
        "tlc_target_id": case.edge.target,
        "before": semantic["before"],
        "input": semantic["input"],
        "expected_output": semantic["expected_output"],
        "after": semantic["after"],
        "expected_projection": semantic["expected_projection"],
        "tier": tier,
        "selection": {
            "policy": SELECTION_POLICY,
            "seed": seed,
            "selection_index": selection_index,
            "transition_ordinal": ordinal,
            "stable_hash": stable_hash,
            "stratum": {
                "action": case.edge.action,
                "outcome": outcome,
            },
        },
        "budgets": budgets.as_dict(),
        "source_digests": source_digests,
    }
    record["record_digest"] = sha256_digest(canonical_json_bytes(record))
    return record, semantic_digest


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _manifest_bytes(manifest: dict[str, Any]) -> bytes:
    payload = dict(manifest)
    payload.pop("manifest_digest", None)
    payload["manifest_digest"] = sha256_digest(canonical_json_bytes(payload))
    manifest.clear()
    manifest.update(payload)
    return canonical_json_bytes(payload) + b"\n"


def _finalize_manifest_bytes(
    manifest: dict[str, Any],
    cases_output_bytes: int,
) -> tuple[bytes, int]:
    total = -1
    encoded = b""
    for _ in range(8):
        manifest["total_output_bytes"] = max(0, total)
        encoded = _manifest_bytes(manifest)
        updated = cases_output_bytes + len(encoded)
        if updated == total:
            return encoded, updated
        total = updated
    manifest["total_output_bytes"] = total
    encoded = _manifest_bytes(manifest)
    return encoded, cases_output_bytes + len(encoded)


def _resource_evidence(guard: ResourceBudget) -> dict[str, float]:
    return {
        "elapsed_seconds": round(guard.elapsed_seconds(), 6),
        "peak_rss_mib": round(guard.peak_rss_mib(), 3),
    }


def _base_manifest(
    *,
    module: str,
    view: str,
    tier: str,
    seed: str,
    budgets: CaseBudgets,
    source_digests: dict[str, str],
    accounting: GenerationAccounting,
) -> dict[str, Any]:
    return {
        "schema_version": CASE_MANIFEST_SCHEMA_VERSION,
        "case_schema_version": CASE_ENVELOPE_SCHEMA_VERSION,
        "protocol_version": STREAM_PROTOCOL_VERSION,
        "source_module": module,
        "view": view,
        "tier": tier,
        "complete": False,
        "status": "incomplete",
        "budget_outcome": None,
        "selection_policy": SELECTION_POLICY,
        "seed": seed,
        "budgets": budgets.as_dict(),
        "source_digests": source_digests,
        "state_count": accounting.state_count,
        "observed_transition_count": accounting.observed_transition_count,
        "eligible_transition_count": accounting.eligible_transition_count,
        "candidate_case_count": accounting.candidate_case_count,
        "selected_case_count": accounting.selected_case_count,
        "emitted_case_count": accounting.emitted_case_count,
        "staged_case_count": accounting.staged_case_count,
        "output_bytes": accounting.output_bytes,
        "cases_path": "cases.jsonl",
        "cases_digest": None,
    }


def _write_incomplete_manifest(
    *,
    manifest_path: Path,
    cases_path: Path,
    module: str,
    view: str,
    tier: str,
    seed: str,
    budgets: CaseBudgets,
    source_digests: dict[str, str],
    accounting: GenerationAccounting,
    guard: ResourceBudget,
    outcome: dict[str, Any],
) -> dict[str, Any]:
    cases_path.unlink(missing_ok=True)
    staged_output_bytes = accounting.output_bytes
    accounting.emitted_case_count = 0
    accounting.output_bytes = 0
    manifest = _base_manifest(
        module=module,
        view=view,
        tier=tier,
        seed=seed,
        budgets=budgets,
        source_digests=source_digests,
        accounting=accounting,
    )
    manifest["budget_outcome"] = outcome
    manifest["staged_output_bytes"] = staged_output_bytes
    manifest["resource_usage"] = _resource_evidence(guard)
    encoded, _ = _finalize_manifest_bytes(manifest, 0)
    _atomic_write(manifest_path, encoded)
    return manifest


def _open_selection_database(package_dir: Path) -> tuple[sqlite3.Connection, Path]:
    descriptor, raw_path = tempfile.mkstemp(
        prefix=".case-selection-",
        suffix=".sqlite3",
        dir=package_dir,
    )
    os.close(descriptor)
    path = Path(raw_path)
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA journal_mode=OFF")
    connection.execute("PRAGMA synchronous=OFF")
    connection.execute("PRAGMA temp_store=FILE")
    connection.execute("PRAGMA cache_size=-8192")
    connection.executescript(
        """
        CREATE TABLE candidates (
            ordinal INTEGER PRIMARY KEY,
            source TEXT NOT NULL,
            target TEXT NOT NULL,
            action TEXT NOT NULL,
            outcome TEXT NOT NULL,
            semantic_digest TEXT NOT NULL,
            stable_hash TEXT NOT NULL,
            stratum_hash TEXT NOT NULL
        );
        CREATE INDEX candidates_stratum_rank
            ON candidates(action, outcome, stable_hash, ordinal);
        CREATE TABLE selected (
            selection_index INTEGER PRIMARY KEY,
            ordinal INTEGER NOT NULL UNIQUE,
            source TEXT NOT NULL,
            target TEXT NOT NULL,
            action TEXT NOT NULL,
            outcome TEXT NOT NULL,
            semantic_digest TEXT NOT NULL,
            stable_hash TEXT NOT NULL
        );
        CREATE INDEX selected_stratum ON selected(action, outcome);
        """
    )
    return connection, path


def _install_sqlite_budget_guard(
    connection: sqlite3.Connection,
    guard: ResourceBudget,
    stage: str,
) -> list[BudgetExceeded]:
    interrupted: list[BudgetExceeded] = []

    def progress() -> int:
        try:
            guard.check(stage)
        except BudgetExceeded as exc:
            interrupted.append(exc)
            return 1
        return 0

    connection.set_progress_handler(progress, 1000)
    return interrupted


def _raise_interrupted_budget(
    exc: sqlite3.OperationalError,
    interrupted: list[BudgetExceeded],
) -> None:
    if interrupted:
        raise interrupted[0] from exc
    raise exc


def render_streaming_case_protocol(
    *,
    module: str,
    tla_path: Path,
    cfg_path: Path,
    dot_path: Path,
    package_dir: Path,
    view: str = "internal",
    action_metadata: dict[str, ActionMetadata] | None = None,
    labelers: list[Any] | None = None,
    state_projector: Any | None = None,
    output_projector: Any | None = None,
    outcome_projector: Any | None = None,
    declared_state_projector: str | None = None,
    declared_output_projector: str | None = None,
    declared_outcome_projector: str | None = None,
    dedupe: str = "none",
    budgets: CaseBudgets | None = None,
    seed: str = "0",
    tier: str = "model",
    started_at: float | None = None,
) -> StreamingGenerationResult:
    """Generate resource-bounded JSONL without transition/case arrays in RAM."""

    if tier not in {"gold", "model", "fuzz"}:
        raise ValueError(f"unsupported corpus tier: {tier}")
    budget_values = budgets or CaseBudgets()
    metadata = action_metadata or {}
    case_labelers = labelers or []
    package_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = package_dir / "case-manifest.json"
    cases_path = package_dir / "cases.jsonl"
    partial_path = package_dir / ".cases.jsonl.partial"
    for stale in (
        manifest_path,
        cases_path,
        partial_path,
        *(package_dir / name for name in LEGACY_GENERATED_FILES),
    ):
        stale.unlink(missing_ok=True)

    guard = ResourceBudget(budget_values, started_at)
    accounting = GenerationAccounting()
    source_digests = {
        "spec": file_sha256(tla_path),
        "config": file_sha256(cfg_path),
        "projection": projection_digest(
            view=view,
            dedupe=dedupe,
            state_projector=state_projector,
            output_projector=output_projector,
            outcome_projector=outcome_projector,
            declared_state_projector=declared_state_projector,
            declared_output_projector=declared_output_projector,
            declared_outcome_projector=declared_outcome_projector,
        ),
        "dot": file_sha256(dot_path),
    }
    connection: sqlite3.Connection | None = None
    database_path: Path | None = None
    try:
        guard.check("start")
        states = load_dot_states(dot_path, guard, accounting)
        if not states:
            raise ValueError(f"no states parsed from {dot_path}")

        connection, database_path = _open_selection_database(package_dir)
        if dedupe == "projected":
            connection.execute(
                "CREATE TABLE seen_semantics (semantic_digest TEXT PRIMARY KEY)"
            )

        candidate_insert = (
            "INSERT INTO candidates "
            "(ordinal, source, target, action, outcome, semantic_digest, stable_hash, stratum_hash) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        )
        for ordinal, edge in iter_dot_edges(dot_path):
            action_spec = action_metadata_for(edge.action, view, metadata)
            if not should_emit_action(action_spec, view):
                continue
            accounting.eligible_transition_count += 1
            case = prepare_case(
                name_index=accounting.eligible_transition_count,
                states=states,
                edge=edge,
                view=view,
                action_metadata=metadata,
                labelers=case_labelers,
                state_projector=state_projector,
                output_projector=output_projector,
            )
            semantic_digest = sha256_digest(
                canonical_json_bytes(semantic_case_payload(case, view))
            )
            if dedupe == "projected":
                inserted = connection.execute(
                    "INSERT OR IGNORE INTO seen_semantics (semantic_digest) VALUES (?)",
                    (semantic_digest,),
                ).rowcount
                if not inserted:
                    continue
            outcome = call_outcome_projector(outcome_projector, case)
            stable_hash = stable_candidate_hash(
                seed=seed,
                action=edge.action,
                outcome=outcome,
                semantic_digest=semantic_digest,
                ordinal=ordinal,
            )
            connection.execute(
                candidate_insert,
                (
                    ordinal,
                    edge.source,
                    edge.target,
                    edge.action,
                    outcome,
                    semantic_digest,
                    stable_hash,
                    stable_stratum_hash(seed, edge.action, outcome),
                ),
            )
            accounting.candidate_case_count += 1
            if accounting.eligible_transition_count % 128 == 0:
                guard.check("candidate-scan")
        connection.commit()
        guard.check("candidate-scan")

        interrupted = _install_sqlite_budget_guard(connection, guard, "case-selection")
        selection_query = """
            WITH ranked AS (
                SELECT
                    ordinal,
                    source,
                    target,
                    action,
                    outcome,
                    semantic_digest,
                    stable_hash,
                    stratum_hash,
                    ROW_NUMBER() OVER (
                        PARTITION BY action, outcome
                        ORDER BY stable_hash, ordinal
                    ) AS stratum_rank
                FROM candidates
            )
            SELECT
                ordinal,
                source,
                target,
                action,
                outcome,
                semantic_digest,
                stable_hash
            FROM ranked
            ORDER BY stratum_rank, stratum_hash, stable_hash, ordinal
            LIMIT ?
        """
        try:
            cursor = connection.execute(selection_query, (budget_values.max_cases,))
            for selection_index, row in enumerate(cursor, start=1):
                connection.execute(
                    "INSERT INTO selected "
                    "(selection_index, ordinal, source, target, action, outcome, semantic_digest, stable_hash) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (selection_index, *row),
                )
                accounting.selected_case_count += 1
            connection.commit()
        except sqlite3.OperationalError as exc:
            _raise_interrupted_budget(exc, interrupted)
        finally:
            connection.set_progress_handler(None, 0)
        guard.check("case-selection")

        cases_digest = hashlib.sha256()
        with partial_path.open("wb") as output:
            rows = connection.execute(
                "SELECT selection_index, ordinal, source, target, action, outcome, "
                "semantic_digest, stable_hash FROM selected ORDER BY selection_index"
            )
            for (
                selection_index,
                ordinal,
                source,
                target,
                action,
                outcome,
                stored_semantic_digest,
                stable_hash,
            ) in rows:
                edge = Edge(source=source, target=target, action=action)
                case = prepare_case(
                    name_index=selection_index,
                    states=states,
                    edge=edge,
                    view=view,
                    action_metadata=metadata,
                    labelers=case_labelers,
                    state_projector=state_projector,
                    output_projector=output_projector,
                )
                record, semantic_digest = case_envelope(
                    case=case,
                    view=view,
                    tier=tier,
                    seed=seed,
                    ordinal=ordinal,
                    selection_index=selection_index,
                    outcome=outcome,
                    stable_hash=stable_hash,
                    budgets=budget_values,
                    source_digests=source_digests,
                )
                if semantic_digest != stored_semantic_digest:
                    raise RuntimeError(
                        "projectors or labelers changed between selection and emission; "
                        f"transition ordinal {ordinal} is not deterministic"
                    )
                line = canonical_json_bytes(record) + b"\n"
                projected_bytes = accounting.output_bytes + len(line)
                if projected_bytes > budget_values.max_output_bytes:
                    raise BudgetExceeded(
                        "max_output_bytes",
                        budget_values.max_output_bytes,
                        projected_bytes,
                        "case-emission",
                    )
                output.write(line)
                cases_digest.update(line)
                accounting.output_bytes = projected_bytes
                accounting.staged_case_count += 1
                if selection_index % 64 == 0:
                    guard.check("case-emission")
            output.flush()
            os.fsync(output.fileno())
        guard.check("case-emission")

        strata: list[dict[str, Any]] = []
        strata_bytes = 0
        for index, (action, outcome, candidate_count, selected_count) in enumerate(
            connection.execute(
                """
                SELECT
                    candidates.action,
                    candidates.outcome,
                    COUNT(*) AS candidate_count,
                    COALESCE(selected_counts.selected_count, 0) AS selected_count
                FROM candidates
                LEFT JOIN (
                    SELECT action, outcome, COUNT(*) AS selected_count
                    FROM selected
                    GROUP BY action, outcome
                ) AS selected_counts
                ON selected_counts.action = candidates.action
                AND selected_counts.outcome = candidates.outcome
                GROUP BY candidates.action, candidates.outcome
                ORDER BY candidates.action, candidates.outcome
                """
            ),
            start=1,
        ):
            stratum = {
                "action": action,
                "outcome": outcome,
                "candidate_case_count": candidate_count,
                "selected_case_count": selected_count,
                "emitted_case_count": selected_count,
            }
            strata_bytes += len(canonical_json_bytes(stratum)) + 1
            if accounting.output_bytes + strata_bytes > budget_values.max_output_bytes:
                raise BudgetExceeded(
                    "max_output_bytes",
                    budget_values.max_output_bytes,
                    accounting.output_bytes + strata_bytes,
                    "manifest-strata",
                )
            strata.append(stratum)
            if index % 128 == 0:
                guard.check("manifest-strata")
        guard.check("manifest-render")
        accounting.emitted_case_count = accounting.selected_case_count
        manifest = _base_manifest(
            module=module,
            view=view,
            tier=tier,
            seed=seed,
            budgets=budget_values,
            source_digests=source_digests,
            accounting=accounting,
        )
        manifest.update(
            {
                "complete": True,
                "status": "complete",
                "budget_outcome": (
                    {
                        "type": "bounded_selection",
                        "budget": "max_cases",
                        "limit": budget_values.max_cases,
                        "observed": accounting.candidate_case_count,
                    }
                    if accounting.candidate_case_count > budget_values.max_cases
                    else {"type": "within_budget"}
                ),
                "cases_digest": f"sha256:{cases_digest.hexdigest()}",
                "strata": strata,
                "resource_usage": _resource_evidence(guard),
            }
        )
        manifest_bytes, total_output_bytes = _finalize_manifest_bytes(
            manifest,
            accounting.output_bytes,
        )
        if total_output_bytes > budget_values.max_output_bytes:
            raise BudgetExceeded(
                "max_output_bytes",
                budget_values.max_output_bytes,
                total_output_bytes,
                "manifest-render",
            )
        os.replace(partial_path, cases_path)
        _atomic_write(manifest_path, manifest_bytes)
        return StreamingGenerationResult(
            manifest_path=manifest_path,
            cases_path=cases_path,
            manifest=manifest,
            exit_code=0,
        )
    except BudgetExceeded as exc:
        partial_path.unlink(missing_ok=True)
        manifest = _write_incomplete_manifest(
            manifest_path=manifest_path,
            cases_path=cases_path,
            module=module,
            view=view,
            tier=tier,
            seed=seed,
            budgets=budget_values,
            source_digests=source_digests,
            accounting=accounting,
            guard=guard,
            outcome=exc.as_dict(),
        )
        return StreamingGenerationResult(
            manifest_path=manifest_path,
            cases_path=cases_path,
            manifest=manifest,
            exit_code=2,
        )
    finally:
        partial_path.unlink(missing_ok=True)
        if connection is not None:
            connection.close()
        if database_path is not None:
            database_path.unlink(missing_ok=True)


def render_python_package(
    *,
    module: str,
    states: dict[str, dict[str, Any]],
    edges: list[Edge],
    package_dir: Path,
    view: str = "internal",
    action_metadata: dict[str, ActionMetadata] | None = None,
    labelers: list[Any] | None = None,
    state_projector: Any | None = None,
    output_projector: Any | None = None,
    dedupe: str = "none",
) -> None:
    metadata = action_metadata or {}
    emitted_edges = [
        edge
        for edge in edges
        if should_emit_action(action_metadata_for(edge.action, view, metadata), view)
    ]
    prepared_cases = prepare_cases(
        states=states,
        edges=emitted_edges,
        view=view,
        action_metadata=metadata,
        labelers=labelers or [],
        state_projector=state_projector,
        output_projector=output_projector,
        dedupe=dedupe,
    )
    package_dir.mkdir(parents=True, exist_ok=True)
    write(package_dir / "__init__.py", render_init())
    write(package_dir / "types.py", render_types())
    write(package_dir / "cases.py", render_cases(module, states, prepared_cases, view))
    write(package_dir / "doubles.py", render_doubles())
    write(package_dir / "validators.py", render_validators())
    write(package_dir / "docs.md", render_docs(module, view, len(states), len(prepared_cases), len(emitted_edges), len(edges), dedupe))


def render_init() -> str:
    return (
        "from .cases import CASES, CASES_BY_NAME, SOURCE_MODULE, SOURCE_VIEW\n"
        "from .doubles import ScriptedTransitionDouble\n"
        "from .types import StateGraphCase, StateGraphInput, StateGraphOutput\n"
        "from .validators import assert_case_replays\n\n"
        "__all__ = [\n"
        "    \"CASES\",\n"
        "    \"CASES_BY_NAME\",\n"
        "    \"SOURCE_MODULE\",\n"
        "    \"SOURCE_VIEW\",\n"
        "    \"ScriptedTransitionDouble\",\n"
        "    \"StateGraphCase\",\n"
        "    \"StateGraphInput\",\n"
        "    \"StateGraphOutput\",\n"
        "    \"assert_case_replays\",\n"
        "]\n"
    )


def render_types() -> str:
    return (
        "from __future__ import annotations\n\n"
        "from dataclasses import dataclass\n"
        "from dataclasses import field\n"
        "from typing import Any\n\n\n"
        "@dataclass(frozen=True)\n"
        "class StateGraphInput:\n"
        "    action: str\n"
        "    source_node: str\n"
        "    target_node: str\n"
        "    params: dict[str, Any] = field(default_factory=dict)\n\n\n"
        "@dataclass(frozen=True)\n"
        "class ActionMetadata:\n"
        "    layer: str = \"internal\"\n"
        "    controllability: str = \"unit_direct\"\n"
        "    generates: frozenset[str] = frozenset((\"spec_unit\",))\n"
        "    tags: frozenset[str] = frozenset()\n\n\n"
        "@dataclass(frozen=True)\n"
        "class StateGraphOutput:\n"
        "    changed: dict[str, dict[str, Any]]\n\n\n"
        "@dataclass(frozen=True)\n"
        "class StateGraphCase:\n"
        "    name: str\n"
        "    before: dict[str, Any]\n"
        "    input: StateGraphInput\n"
        "    output: Any\n"
        "    after: dict[str, Any]\n"
        "    labels: frozenset[str]\n"
        f"    schema_version: str = {TRACE_SCHEMA_VERSION!r}\n"
        "    view: str = \"internal\"\n"
        "    layer: str = \"internal\"\n"
        "    controllability: str = \"unit_direct\"\n"
        "    generates: frozenset[str] = frozenset((\"spec_unit\",))\n"
        "    tags: frozenset[str] = frozenset()\n"
        "    metadata: ActionMetadata = field(default_factory=ActionMetadata)\n"
    )


def render_cases(
    module: str,
    states: dict[str, dict[str, Any]],
    cases: list[PreparedCase],
    view: str,
) -> str:
    lines = [
        "from __future__ import annotations\n\n",
        "from .types import ActionMetadata, StateGraphCase, StateGraphInput, StateGraphOutput\n\n\n",
        f'SCHEMA_VERSION = {TRACE_SCHEMA_VERSION!r}\n',
        f'SOURCE_MODULE = {module!r}\n',
        f'SOURCE_VIEW = {view!r}\n',
        f"STATE_COUNT = {len(states)}\n",
        f"TRANSITION_COUNT = {len(cases)}\n\n",
        "CASES = [\n",
    ]
    for case in cases:
        edge = case.edge
        metadata = case.metadata
        lines.extend(
            [
                "    StateGraphCase(\n",
                f"        name={case.name!r},\n",
                f"        before={py_repr(case.before)},\n",
                "        input=StateGraphInput(\n",
                f"            action={edge.action!r},\n",
                f"            source_node={edge.source!r},\n",
                f"            target_node={edge.target!r},\n",
                f"            params={py_repr(case.params)},\n",
                "        ),\n",
                f"        output={case.output_expression},\n",
                f"        after={py_repr(case.after)},\n",
                f"        labels=frozenset({py_repr(case.labels)}),\n",
                "        schema_version=SCHEMA_VERSION,\n",
                "        view=SOURCE_VIEW,\n",
                f"        layer={metadata.layer!r},\n",
                f"        controllability={metadata.controllability!r},\n",
                f"        generates=frozenset({py_repr(metadata.generates)}),\n",
                f"        tags=frozenset({py_repr(metadata.tags)}),\n",
                "        metadata=ActionMetadata(\n",
                f"            layer={metadata.layer!r},\n",
                f"            controllability={metadata.controllability!r},\n",
                f"            generates=frozenset({py_repr(metadata.generates)}),\n",
                f"            tags=frozenset({py_repr(metadata.tags)}),\n",
                "        ),\n",
                "    ),\n",
            ]
        )
    lines.extend(["]\n\n", "CASES_BY_NAME = {case.name: case for case in CASES}\n"])
    return "".join(lines)


def render_doubles() -> str:
    return (
        "from __future__ import annotations\n\n"
        "from typing import Any\n\n"
        "from .types import StateGraphCase, StateGraphInput\n\n\n"
        "class ScriptedTransitionDouble:\n"
        "    def __init__(self, case: StateGraphCase):\n"
        "        self.case = case\n"
        "        self._state = case.before\n"
        "        self._called = False\n\n"
        "    def snapshot(self):\n"
        "        return self._state\n\n"
        "    def input(self) -> StateGraphInput:\n"
        "        return self.case.input\n\n"
        "    def call(self, value: StateGraphInput) -> Any:\n"
        "        if value != self.case.input:\n"
        "            raise AssertionError(f\"unexpected input for {self.case.name}: {value!r}\")\n"
        "        if self._called:\n"
        "            raise AssertionError(f\"case already consumed: {self.case.name}\")\n"
        "        self._called = True\n"
        "        self._state = self.case.after\n"
        "        return self.case.output\n"
    )


def render_validators() -> str:
    return (
        "from __future__ import annotations\n\n"
        "from .types import StateGraphCase\n\n\n"
        "def assert_case_replays(case: StateGraphCase) -> None:\n"
        "    changed = {\n"
        "        field: {\"before\": case.before.get(field), \"after\": case.after.get(field)}\n"
        "        for field in sorted(set(case.before) | set(case.after))\n"
        "        if case.before.get(field) != case.after.get(field)\n"
        "    }\n"
        "    if hasattr(case.output, \"changed\"):\n"
        "        assert case.output.changed == changed\n"
    )


def render_docs(
    module: str,
    view: str,
    state_count: int,
    transition_count: int,
    emitted_transition_count: int,
    total_transition_count: int,
    dedupe: str,
) -> str:
    return (
        f"# {module} TLC Cases\n\n"
        "Generated from a TLC DOT state graph dump.\n\n"
        f"- View: `{view}`\n"
        f"- States: `{state_count}`\n"
        f"- Transitions: `{transition_count}`\n\n"
        f"- Emitted transitions before dedupe: `{emitted_transition_count}`\n"
        f"- TLC transitions before view filtering: `{total_transition_count}`\n\n"
        f"- Dedupe mode: `{dedupe}`\n\n"
        "Each case is one action-labeled edge in the reachable state graph.\n"
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tla", type=Path)
    parser.add_argument("cfg", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--package", default="tlc_state_graph_cases")
    parser.add_argument(
        "--format",
        dest="output_format",
        choices=["legacy-python", "streaming-jsonl"],
        default="legacy-python",
        help="Keep legacy generated Python or emit bounded case-manifest.json/cases.jsonl.",
    )
    parser.add_argument("--view", choices=sorted(SUPPORTED_VIEWS), help="Generate a view-aware case package.")
    parser.add_argument("--actions-metadata", type=Path, help="YAML file with actions.<ActionName> layer/controllability/generates.")
    parser.add_argument("--tlc2", default="tlc2")
    parser.add_argument("--dot", type=Path)
    parser.add_argument(
        "--input-dot",
        type=Path,
        help="Consume an existing TLC action-labeled DOT file instead of running TLC.",
    )
    parser.add_argument(
        "--state-projector",
        help="Optional module:function that projects raw TLC states before rendering cases.",
    )
    parser.add_argument(
        "--output-projector",
        help="Optional module:function that derives adapter expected output from a TLC transition.",
    )
    parser.add_argument(
        "--outcome-projector",
        help="Optional module:function that derives the action/outcome selection stratum.",
    )
    parser.add_argument(
        "--dedupe",
        choices=["none", "projected"],
        default="none",
        help="Optionally collapse duplicate projected transitions.",
    )
    parser.add_argument(
        "--labeler",
        action="append",
        default=[],
        help="Optional module:function returning extra labels for before/action/after/changed",
    )
    parser.add_argument("--max-cases", type=int, default=DEFAULT_MAX_CASES)
    parser.add_argument("--max-output-bytes", type=int, default=DEFAULT_MAX_OUTPUT_BYTES)
    parser.add_argument("--max-rss-mib", type=float, default=DEFAULT_MAX_RSS_MIB)
    parser.add_argument("--max-seconds", type=float, default=DEFAULT_MAX_SECONDS)
    parser.add_argument("--seed", default="0")
    parser.add_argument("--tier", choices=["gold", "model", "fuzz"], default="model")
    args = parser.parse_args()

    if args.dot and args.input_dot:
        parser.error("--dot and --input-dot are mutually exclusive")
    tla_path = resolve_existing_from_cwd(args.tla)
    spec_dir = resolve_spec_dir(args.tla)
    cfg_path = resolve_existing_spec_input(args.cfg, spec_dir)
    if not cfg_path.exists():
        raise SystemExit(f"ERROR: config not found: {cfg_path} (spec directory: {spec_dir})")
    view = args.view or "internal"
    out_path = resolve_spec_relative_path(args.out, spec_dir)
    if args.view is not None:
        out_path = out_path / VIEW_OUTPUT_DIRS[view]
    if args.input_dot:
        dot_path = resolve_existing_spec_input(args.input_dot, spec_dir)
    else:
        dot_path = resolve_spec_relative_path(args.dot, spec_dir) if args.dot else out_path / f"{tla_path.stem}.dot"
    package_dir = out_path / args.package

    for root in [Path.cwd(), Path(__file__).resolve().parents[1], spec_dir]:
        resolved = str(root.resolve())
        if resolved not in sys.path:
            sys.path.insert(0, resolved)
    labelers = [load_object(path) for path in args.labeler]
    state_projector = load_object(args.state_projector) if args.state_projector else None
    output_projector = load_object(args.output_projector) if args.output_projector else None
    outcome_projector = load_object(args.outcome_projector) if args.outcome_projector else None
    action_metadata = load_action_metadata(args.actions_metadata, spec_dir)

    if args.output_format == "streaming-jsonl":
        budgets = CaseBudgets(
            max_cases=args.max_cases,
            max_output_bytes=args.max_output_bytes,
            max_rss_mib=args.max_rss_mib,
            max_seconds=args.max_seconds,
        )
        started_at = time.monotonic()
        if not args.input_dot:
            try:
                run_tlc_dump(
                    tla_path,
                    cfg_path,
                    dot_path,
                    args.tlc2,
                    timeout_seconds=budgets.max_seconds,
                )
            except subprocess.TimeoutExpired:
                package_dir.mkdir(parents=True, exist_ok=True)
                for stale in (
                    package_dir / "cases.jsonl",
                    *(package_dir / name for name in LEGACY_GENERATED_FILES),
                ):
                    stale.unlink(missing_ok=True)
                guard = ResourceBudget(budgets, started_at)
                accounting = GenerationAccounting()
                source_digests = {
                    "spec": file_sha256(tla_path),
                    "config": file_sha256(cfg_path),
                    "projection": projection_digest(
                        view=view,
                        dedupe=args.dedupe,
                        state_projector=state_projector,
                        output_projector=output_projector,
                        outcome_projector=outcome_projector,
                        declared_state_projector=args.state_projector,
                        declared_output_projector=args.output_projector,
                        declared_outcome_projector=args.outcome_projector,
                    ),
                }
                manifest = _write_incomplete_manifest(
                    manifest_path=package_dir / "case-manifest.json",
                    cases_path=package_dir / "cases.jsonl",
                    module=tla_path.stem,
                    view=view,
                    tier=args.tier,
                    seed=str(args.seed),
                    budgets=budgets,
                    source_digests=source_digests,
                    accounting=accounting,
                    guard=guard,
                    outcome=BudgetExceeded(
                        "max_seconds",
                        budgets.max_seconds,
                        guard.elapsed_seconds(),
                        "tlc-state-graph-generation",
                    ).as_dict(),
                )
                print(
                    f"ERROR: max_seconds exceeded; incomplete manifest: "
                    f"{package_dir / 'case-manifest.json'}",
                    file=sys.stderr,
                )
                return 2
        result = render_streaming_case_protocol(
            module=tla_path.stem,
            tla_path=tla_path,
            cfg_path=cfg_path,
            dot_path=dot_path,
            package_dir=package_dir,
            view=view,
            action_metadata=action_metadata,
            labelers=labelers,
            state_projector=state_projector,
            output_projector=output_projector,
            outcome_projector=outcome_projector,
            declared_state_projector=args.state_projector,
            declared_output_projector=args.output_projector,
            declared_outcome_projector=args.outcome_projector,
            dedupe=args.dedupe,
            budgets=budgets,
            seed=str(args.seed),
            tier=args.tier,
            started_at=started_at,
        )
        print(f"spec directory: {spec_dir}")
        if result.exit_code:
            outcome = result.manifest["budget_outcome"]
            print(
                f"ERROR: {outcome['budget']} exceeded; incomplete manifest: "
                f"{result.manifest_path}",
                file=sys.stderr,
            )
        else:
            print(
                f"generated {result.manifest['emitted_case_count']} bounded {view} "
                f"case records into {result.cases_path}"
            )
        return result.exit_code

    if not args.input_dot:
        run_tlc_dump(tla_path, cfg_path, dot_path, args.tlc2)
    states, edges = load_dot(dot_path)
    if not states:
        raise SystemExit(f"ERROR: no states parsed from {dot_path}")
    render_python_package(
        module=tla_path.stem,
        states=states,
        edges=edges,
        package_dir=package_dir,
        view=view,
        action_metadata=action_metadata,
        labelers=labelers,
        state_projector=state_projector,
        output_projector=output_projector,
        dedupe=args.dedupe,
    )
    print(f"spec directory: {spec_dir}")
    print(f"generated {view} transition cases from {len(states)} states into {package_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
