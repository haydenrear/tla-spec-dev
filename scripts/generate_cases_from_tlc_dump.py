#!/usr/bin/env python3
"""Generate Python transition cases from a TLC DOT state graph dump.

This script is intentionally generic: it does not know product domains or
Python fake templates. It treats TLC as the case source of truth:

    TLC states and action-labeled edges -> Python case descriptors.
"""

from __future__ import annotations

import argparse
import ast
import importlib
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from . import case_modules
    from .corpus_diagnostics import enforce_case_cap
    from .extract_spec_manifest import load_manifest
    from .infer_action_params import UNCHECKED, ActionRecipe, CorpusMeasurement, build_recipes, build_recipes_from_path, infer_params, measure_recovery, render_audit, unchecked_param_names
    from .spec_paths import is_relative_to, resolve_existing_from_cwd, resolve_existing_spec_input, resolve_spec_dir, resolve_spec_relative_path
except ImportError:  # pragma: no cover - direct script execution
    import case_modules  # type: ignore[no-redef]
    from corpus_diagnostics import enforce_case_cap
    from extract_spec_manifest import load_manifest
    from infer_action_params import UNCHECKED, ActionRecipe, CorpusMeasurement, build_recipes, build_recipes_from_path, infer_params, measure_recovery, render_audit, unchecked_param_names
    from spec_paths import is_relative_to, resolve_existing_from_cwd, resolve_existing_spec_input, resolve_spec_dir, resolve_spec_relative_path


NODE_RE = re.compile(r'^\s*(-?\d+) \[label="(.*)"(?:,style = filled)?\];?$')
EDGE_RE = re.compile(r'^\s*(-?\d+) -> (-?\d+) \[label="([^"]+)"')
TRACE_SCHEMA_VERSION = "tla-testgraph.trace.v1"
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


def run_tlc_dump(
    tla_path: Path,
    cfg_path: Path,
    dot_path: Path,
    tlc2: str,
    search_path: "case_modules.ModuleSearchPath | None" = None,
) -> None:
    """Explore ``tla_path`` with TLC and dump the state graph.

    EV-02-DF-02: TLC runs with cwd = the ``.tla``'s directory and resolves
    ``EXTENDS`` against that directory and the ``TLA-Library`` search path --
    never against the current directory. A module that extends a view in another
    directory therefore needs the view's directory on that path, which
    ``search_path`` supplies. Without it the failure is a
    ``tla2sany.semantic.AbortException`` and a ``CalledProcessError`` traceback,
    which is why the caller resolves the hierarchy BEFORE getting here.
    """
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
    env = case_modules.tlc_environment(search_path)
    try:
        subprocess.run(command, check=True, cwd=spec_dir, env=env)
    except subprocess.CalledProcessError as error:
        lines = [
            f"ERROR: TLC exited {error.returncode} exploring {tla_path.name} "
            f"(config {cfg_path.name}).",
            f"  working directory: {spec_dir}",
        ]
        if search_path is not None and not search_path.is_self_contained:
            lines.append(
                "  module search path (TLA-Library): "
                + ", ".join(str(directory) for directory in search_path.directories)
            )
            lines.append(f"  EXTENDS resolved elsewhere: {search_path.describe()}")
        else:
            lines.append(
                "  module search path: the spec directory only -- every EXTENDS "
                "resolved beside the module."
            )
        lines.append(
            "  TLC's own message is above. It is not a case-generation failure: "
            "nothing was written."
        )
        raise SystemExit("\n".join(lines)) from error
    finally:
        shutil.rmtree(metadir, ignore_errors=True)


def load_dot(path: Path) -> tuple[dict[str, dict[str, Any]], list[Edge]]:
    states: dict[str, dict[str, Any]] = {}
    edges: list[Edge] = []
    for line in path.read_text().splitlines():
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


def params_for_case(
    edge: Edge,
    raw_before: dict[str, Any],
    raw_after: dict[str, Any],
    view: str,
    param_recipes: dict[str, ActionRecipe] | None,
) -> dict[str, Any]:
    """Determine an edge's action arguments.

    An explicit action marker in the model wins when one exists -- a model that
    states its own arguments is authoritative. Otherwise MF-029 recovers them
    from the case's own before/after pair. Recovery derives from the BEFORE
    state and the transition; where it cannot, the parameter is ``UNCHECKED``
    rather than a fabricated value that would make a comparison succeed.
    """
    declared = params_from_action_marker(edge, raw_after, view)
    if declared:
        return declared
    return infer_params(edge.action, raw_before, raw_after, param_recipes)


def param_provenance_labels(params: dict[str, Any]) -> list[str]:
    """Labels recording how trustworthy an emitted case's arguments are.

    These exist so an unrecoverable parameter is MARKED AND KEPT. No case is
    ever dropped, filtered, or skipped for failing recovery -- the corpus is
    complete either way, and the label is how a consumer tells the difference.
    """
    if not params:
        return []
    unchecked = unchecked_param_names(params)
    if not unchecked:
        return ["params:recovered"]
    labels = ["params:unchecked"]
    labels.extend(f"params:unchecked:{name}" for name in unchecked)
    if len(unchecked) < len(params):
        labels.append("params:partial")
    return labels


def case_name(index: int, action: str) -> str:
    snake = re.sub(r"(?<!^)([A-Z])", r"_\1", action).lower()
    snake = re.sub(r"[^a-z0-9_]+", "_", snake).strip("_")
    return f"case_{index:04d}_{snake}"


def py_repr(value: Any) -> str:
    if value is UNCHECKED:
        # Rendered as the imported sentinel, never as a literal. A generated
        # case must not be able to state an argument it does not know.
        return "UNCHECKED"
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
    param_recipes: dict[str, ActionRecipe] | None = None,
) -> list[PreparedCase]:
    prepared: list[PreparedCase] = []
    seen: set[Any] = set()
    for edge in edges:
        raw_before = states[edge.source]
        raw_after = states[edge.target]
        before = call_state_projector(state_projector, raw_before)
        after = call_state_projector(state_projector, raw_after)
        # MF-029: recovery reads the RAW states, not the projected ones. A
        # projector may drop or rename fields, and a parameter recovered from a
        # projection would be recovered from something other than the model.
        params = params_for_case(edge, raw_before, raw_after, view, param_recipes)
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
        if dedupe == "projected":
            signature = freeze_for_signature(
                {
                    "action": edge.action,
                    "params": params,
                    "before": before,
                    "after": after,
                    "output": output_value,
                }
            )
            if signature in seen:
                continue
            seen.add(signature)
        labels = labels_for_case(before=before, action=edge.action, after=after, changes=changes, labelers=labelers)
        for provenance in param_provenance_labels(params):
            if provenance not in labels:
                labels.append(provenance)
        metadata = action_metadata_for(edge.action, view, action_metadata)
        prepared.append(
            PreparedCase(
                name=case_name(len(prepared) + 1, edge.action),
                edge=edge,
                before=before,
                after=after,
                params=params,
                output_value=output_value,
                output_expression=output_expression,
                changes=changes,
                labels=tuple(labels),
                metadata=metadata,
            )
        )
    return prepared


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
    param_recipes: dict[str, ActionRecipe] | None = None,
) -> list[PreparedCase]:
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
        param_recipes=param_recipes,
    )
    package_dir.mkdir(parents=True, exist_ok=True)
    write(package_dir / "__init__.py", render_init())
    write(package_dir / "types.py", render_types())
    write(package_dir / "cases.py", render_cases(module, states, prepared_cases, view))
    write(package_dir / "doubles.py", render_doubles())
    write(package_dir / "validators.py", render_validators())
    write(package_dir / "docs.md", render_docs(module, view, len(states), len(prepared_cases), len(emitted_edges), len(edges), dedupe))
    # Every prepared case has now been written. The caller gates the corpus
    # AFTER this point, so a failing cap gate never removes anything -- the
    # package on disk is complete either way (MF-014).
    return prepared_cases


def render_init() -> str:
    return (
        "from .cases import CASES, CASES_BY_NAME, SOURCE_MODULE, SOURCE_VIEW\n"
        "from .doubles import ScriptedTransitionDouble\n"
        "from .types import UNCHECKED, StateGraphCase, StateGraphInput, StateGraphOutput\n"
        "from .validators import assert_case_replays\n\n"
        "__all__ = [\n"
        "    \"CASES\",\n"
        "    \"CASES_BY_NAME\",\n"
        "    \"SOURCE_MODULE\",\n"
        "    \"SOURCE_VIEW\",\n"
        "    \"UNCHECKED\",\n"
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
        "class Unchecked:\n"
        "    \"\"\"An action argument this corpus could not recover from the state pair.\n\n"
        "    MF-029. It is NOT None, \"\" or 0 -- those are values a model could\n"
        "    legitimately produce, so an adapter comparing against one could pass by\n"
        "    coincidence. UNCHECKED equals only itself, so any check expecting a\n"
        "    concrete argument fails against it instead of passing vacuously.\n\n"
        "    A case carrying UNCHECKED is still a real case and is never dropped: the\n"
        "    sentinel marks the argument, it does not disqualify the transition.\n"
        "    \"\"\"\n\n"
        "    _instance = None\n\n"
        "    def __new__(cls):\n"
        "        if cls._instance is None:\n"
        "            cls._instance = super().__new__(cls)\n"
        "        return cls._instance\n\n"
        "    def __repr__(self) -> str:\n"
        "        return \"UNCHECKED\"\n\n"
        "    def __bool__(self) -> bool:\n"
        "        return False\n\n"
        "    def __eq__(self, other: Any) -> bool:\n"
        "        return other is self\n\n"
        "    def __ne__(self, other: Any) -> bool:\n"
        "        return other is not self\n\n"
        "    def __hash__(self) -> int:\n"
        "        return hash(\"tla-spec-dev.UNCHECKED\")\n\n\n"
        "UNCHECKED = Unchecked()\n\n\n"
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
        "from .types import UNCHECKED, ActionMetadata, StateGraphCase, StateGraphInput, StateGraphOutput\n\n\n",
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


def resolve_module_search_path(
    tla_path: Path, extra_roots: list[Path]
) -> "case_modules.ModuleSearchPath | None":
    """Resolve the EXTENDS hierarchy and report where each module came from.

    EV-02-DF-02. Returns None when the hierarchy cannot be resolved statically
    AND the operator has already supplied a ``TLA-Library`` of their own -- in
    that case this resolver is not the authority and generation proceeds with
    whatever the environment says. In every other case an unresolvable EXTENDS
    is fatal HERE, with the module named, because TLC will fail on it anyway and
    its message is thirty lines lower.
    """
    try:
        search_path = case_modules.resolve_search_path(tla_path, extra_roots)
    except case_modules.ModuleSearchError as error:
        if f"-D{case_modules.TLA_LIBRARY_PROPERTY}" in os.environ.get("JAVA_TOOL_OPTIONS", ""):
            print(
                f"warning: {error}\n"
                f"  JAVA_TOOL_OPTIONS already sets {case_modules.TLA_LIBRARY_PROPERTY}, so "
                "the environment is the authority here and generation proceeds.",
                file=sys.stderr,
            )
            return None
        raise SystemExit(f"ERROR: {error}") from error
    if not search_path.is_self_contained:
        print(
            f"module search path: {', '.join(str(d) for d in search_path.directories)}\n"
            f"  EXTENDS resolved outside {search_path.root.parent}: {search_path.describe()}"
        )
    return search_path


def build_recipes_for_hierarchy(
    tla_path: Path, search_path: "case_modules.ModuleSearchPath | None"
) -> dict[str, "ActionRecipe"]:
    """MF-029 recipes over the whole EXTENDS hierarchy, base modules first.

    A case module declares no VARIABLES and no actions -- every action it enters
    is defined in the view it EXTENDS -- so reading only its own text produced
    recipes for nothing, every case carried no argument, and the adapters then
    refused the entire corpus with ``no usable argument for `i```. Measured on
    the ex4 fixture: the view's own corpus recovered 330/330 arguments while its
    two case modules recovered 0/50 and 0/6 from the same actions.

    The recipes must come from the same module set TLC explored, which is
    exactly what the search path resolved. On a single-file spec that extends
    only standard modules this is the module's own text and nothing changes.
    """
    files = search_path.files_base_first if search_path is not None else (Path(tla_path),)
    return build_recipes(
        "\n".join(Path(path).read_text(encoding="utf-8") for path in files)
    )


def report_out_resolution(requested: Path, resolved: Path, spec_dir: Path) -> None:
    """Say out loud where a relative ``--out`` landed, when it is not obvious.

    EV-02: `--out generated` from a repo root silently created
    ``<spec dir>/generated``. The resolution rule is deliberate (a spec-relative
    default keeps generated corpora beside their spec), but it is a surprise the
    first time, and the run that hit it only found the directory afterwards.
    """
    if Path(requested).is_absolute():
        return
    cwd_candidate = (Path.cwd() / requested).resolve()
    if cwd_candidate == resolved or is_relative_to(resolved, cwd_candidate):
        return
    print(
        f"note: --out {requested} resolved to {resolved} -- a relative --out is "
        f"resolved against the SPEC DIRECTORY ({spec_dir}), not the current "
        f"directory ({Path.cwd()}). Pass an absolute path to control it."
    )


def advise_complexity(
    tla_path: Path,
    cfg_path: Path,
    spec_dir: Path,
    search_path: "case_modules.ModuleSearchPath | None" = None,
) -> None:
    """Print the complexity scan as ADVICE before generating cases (MF-036).

    Complexity is a scanner, not a gate
    (references/architecture_tractability.md, "Advisory, Not Blocking").
    Generation ALWAYS proceeds: a dense model is a finding the agent should
    read, not a blocked build. The scan runs first only so its findings
    appear before the (potentially long) TLC exploration, never
    to refuse it. A model the scan cannot analyze is surfaced the same way --
    reported, not refused -- because TLC may handle a model the static scanner
    cannot.
    """
    manifest_path = case_modules.resolve_manifest_path(spec_dir, search_path)
    try:
        from scripts.analyze_complexity import gate_report
    except ImportError:  # direct-script import, where sys.path[0] is scripts/
        from analyze_complexity import gate_report  # type: ignore[no-redef]

    try:
        clean, message = gate_report(
            tla_path,
            cfg_path,
            manifest_path if manifest_path.is_file() else None,
            search_path=list(search_path.directories) if search_path is not None else None,
        )
    except Exception as exc:  # a scan that cannot parse must not block generation
        print(f"warning: complexity scan could not analyze {tla_path}: {exc}", file=sys.stderr)
        return

    if clean:
        print(message)
        return
    print(message, file=sys.stderr)
    print(
        "\nProceeding with case generation -- complexity is advisory and does not block. "
        "Read the findings above (references/architecture_tractability.md, "
        "'Advisory, Not Blocking').",
        file=sys.stderr,
    )


def report_param_recovery(
    prepared: list[PreparedCase],
    param_recipes: dict[str, ActionRecipe],
    package_dir: Path,
) -> CorpusMeasurement:
    """Write the recoverability audit FROM THE CORPUS IT AUDITS, and report it.

    RP-02. The audit used to be rendered from ``param_recipes`` alone -- a
    reading of the module's syntax -- so it printed "Every parameter of every
    action is recoverable from its state pair" over a run that had just
    reported ``0/38 cases carry arguments`` (EV-02-DF-03). A mechanism NAMED is
    not an argument RECOVERED, and only the corpus knows which happened.

    Nothing here filters, samples or truncates: every prepared case is counted,
    including the ones whose arguments failed to recover, because an
    unrecovered argument is a finding to report and not a case to drop.
    """
    audit_path = package_dir / "param_recovery_audit.md"
    measurement = measure_recovery((case.edge.action, case.params) for case in prepared)
    write(audit_path, render_audit(param_recipes, measurement))
    with_params = sum(1 for case in prepared if case.params)
    recovered = sum(
        1 for case in prepared if case.params and not unchecked_param_names(case.params)
    )
    unchecked = sum(1 for case in prepared if unchecked_param_names(case.params))
    print(
        f"parameter recovery: {with_params}/{len(prepared)} cases carry arguments, "
        f"{recovered} carry a fully recovered argument set, "
        f"{unchecked} carry at least one UNCHECKED argument (kept, never dropped); "
        f"audit written to {audit_path}"
    )
    for item in measurement.unrecovered:
        print(
            f"  UNRECOVERABLE on this corpus: {item.action}({item.param}) -- "
            f"0 of {item.cases} cases carry an argument"
        )
    for item in measurement.partial:
        print(
            f"  PARTIAL on this corpus: {item.action}({item.param}) -- "
            f"{item.recovered} of {item.cases} cases carry an argument"
        )
    return measurement


def report_action_coverage(
    prepared: list[PreparedCase],
    *,
    module: str,
    view: str,
    action_metadata: dict[str, ActionMetadata],
    package_dir: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    """Report per-action coverage for the corpus just written, and record it.

    Two things happen here, both advisory:

    * **R4-DF-04** -- a declared view action that generated ZERO cases is a
      silent coverage hole, most often caused by a pure alias wrapper
      (``CliAdd(t) == AddTask(t)``): TLC attributes such edges to the inner
      action's definition site, so the wrapper never appears in the dump.
    * **CM-F2** -- when the module is declared in the manifest's
      ``case_modules:`` block, that warning is scoped to the actions the module
      says it enters. A slice deliberately does not enter the rest of the view,
      and warning about them diagnosed a design decision as a defect: a
      four-action slice of an eleven-action view emitted seven wrong warnings,
      which is how a real warning stops being read.

    Nothing here can refuse a generation; the corpus is already on disk.
    """
    emitted_counts: dict[str, int] = {}
    for case in prepared:
        emitted_counts[case.edge.action] = emitted_counts.get(case.edge.action, 0) + 1
    declared_for_view = {
        name for name, meta in action_metadata.items() if should_emit_action(meta, view)
    }

    declaration = case_modules.declaration_for(manifest_path, module, warn_stream=sys.stderr)
    if declaration is None:
        reportable = declared_for_view
    else:
        scope = set(declaration.actions)
        reportable = declared_for_view & scope
        out_of_view = sorted(scope - declared_for_view)
        out_of_scope = sorted(set(emitted_counts) - scope)
        print(
            f"case module {module}: declared {declaration.form} of {declaration.extends} "
            f"with {len(scope)} action(s) in scope; "
            f"{len(declared_for_view - scope)} other declared {view} action(s) are outside "
            "this aspect and are NOT reported as coverage holes "
            f"(spec_manifest.yaml {case_modules.CASE_MODULES_KEY}:)"
        )
        if declaration.form == "given" and declaration.claim:
            print(f"case module {module}: recorded Given claim -- {declaration.claim}")
        for name in out_of_view:
            print(
                f"warning: case module {module} declares {name!r} in its action scope, "
                f"but actions.yml does not declare it as a {view} action.",
                file=sys.stderr,
            )
        for name in out_of_scope:
            print(
                f"warning: case module {module} generated {emitted_counts[name]} case(s) for "
                f"{name!r}, which is not in its declared `actions:` scope. The declaration "
                "is out of date, and the coverage report is reading it.",
                file=sys.stderr,
            )

    for silent in sorted(reportable - set(emitted_counts)):
        print(
            f"warning: declared {view} action {silent!r} generated ZERO cases. "
            "If it is a pure alias wrapper (Wrapper(x) == Inner(x)), TLC "
            "attributes its transitions to the inner action -- add a semantic "
            "no-op anchoring conjunct so the wrapper owns its edges, or remove "
            "the action from actions.yml if it is not a real view action.",
            file=sys.stderr,
        )

    record = case_modules.coverage_record(
        module=module,
        view=view,
        action_counts=emitted_counts,
        declared_view_actions=declared_for_view,
        declaration=declaration,
        source=str(package_dir),
    )
    path = case_modules.write_coverage_record(package_dir, record)
    print(f"per-action coverage recorded to {path}")
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tla", type=Path)
    parser.add_argument("cfg", type=Path)
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help=(
            "Output ROOT for the generated package. An absolute path is used as "
            "given. A RELATIVE path is resolved against the SPEC DIRECTORY (the "
            ".tla's own directory), not the current directory -- unless it already "
            "points inside the spec directory. `--out generated` run from a repo "
            "root therefore writes <spec dir>/generated, which is rarely what was "
            "meant; the resolved root is printed before generation starts. Pass an "
            "absolute path when you want cwd-relative behavior."
        ),
    )
    parser.add_argument(
        "--module-path",
        action="append",
        type=Path,
        default=[],
        metavar="DIR",
        help=(
            "Directory to search for the modules this .tla EXTENDS, ahead of the "
            "directories beside it. Repeatable. TLC resolves EXTENDS against the "
            ".tla's own directory and the TLA-Library search path -- never against "
            "the current directory -- so a case module in specs/case_modules/ that "
            "extends a view in specs/program_model/ needs the view's directory on "
            "this path. Sibling directories of the .tla that contain .tla files are "
            "searched automatically, so the documented layout needs no flag; use "
            "this when the view is somewhere else or when two siblings define the "
            "same module."
        ),
    )
    parser.add_argument("--package", default="tlc_state_graph_cases")
    parser.add_argument("--view", choices=sorted(SUPPORTED_VIEWS), help="Generate a view-aware case package.")
    parser.add_argument("--actions-metadata", type=Path, help="YAML file with actions.<ActionName> layer/controllability/generates.")
    parser.add_argument("--tlc2", default="tlc2")
    parser.add_argument("--dot", type=Path)
    parser.add_argument(
        "--state-projector",
        help="Optional module:function that projects raw TLC states before rendering cases.",
    )
    parser.add_argument(
        "--output-projector",
        help="Optional module:function that derives adapter expected output from a TLC transition.",
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
    parser.add_argument(
        "--no-infer-params",
        action="store_true",
        help=(
            "Emit params={} instead of recovering action arguments from each case's "
            "before/after state pair. The MF-029 revert switch: parameter inference is "
            "experimental and generator-side, so turning it off must not require a "
            "model or spec change."
        ),
    )
    args = parser.parse_args()

    tla_path = resolve_existing_from_cwd(args.tla)
    spec_dir = resolve_spec_dir(args.tla)
    cfg_path = resolve_existing_spec_input(args.cfg, spec_dir)
    if not cfg_path.exists():
        raise SystemExit(f"ERROR: config not found: {cfg_path} (spec directory: {spec_dir})")
    view = args.view or "internal"
    out_path = resolve_spec_relative_path(args.out, spec_dir)
    if args.view is not None:
        out_path = out_path / VIEW_OUTPUT_DIRS[view]
    dot_path = resolve_spec_relative_path(args.dot, spec_dir) if args.dot else out_path / f"{tla_path.stem}.dot"
    report_out_resolution(args.out, out_path, spec_dir)

    for root in [Path.cwd(), Path(__file__).resolve().parents[1], spec_dir]:
        resolved = str(root.resolve())
        if resolved not in sys.path:
            sys.path.insert(0, resolved)

    # EV-02-DF-02: resolve the EXTENDS hierarchy BEFORE anything expensive runs,
    # so a module that extends a view in another directory either gets that
    # directory on the search path or gets one sentence saying which module is
    # missing and where it was looked for -- not a SANY AbortException stack
    # underneath a complexity paragraph about a bound that could not be measured.
    search_path = resolve_module_search_path(tla_path, args.module_path)
    manifest_path = case_modules.resolve_manifest_path(spec_dir, search_path)

    # Complexity scan (MF-011, made advisory in MF-036). Runs BEFORE
    # run_tlc_dump only so the warnings and recommendations print ahead of the
    # TLC exploration. It never refuses generation -- complexity is advisory.
    advise_complexity(tla_path, cfg_path, spec_dir, search_path)

    run_tlc_dump(tla_path, cfg_path, dot_path, args.tlc2, search_path)
    states, edges = load_dot(dot_path)
    if not states:
        raise SystemExit(f"ERROR: no states parsed from {dot_path}")
    action_metadata = load_action_metadata(args.actions_metadata, spec_dir)

    # MF-029: recover action arguments from each case's own state pair. The
    # recipes come from the SAME module TLC just explored, so the recovery and
    # the corpus can never describe different actions.
    param_recipes = (
        None if args.no_infer_params else build_recipes_for_hierarchy(tla_path, search_path)
    )

    prepared = render_python_package(
        module=tla_path.stem,
        states=states,
        edges=edges,
        package_dir=out_path / args.package,
        view=view,
        action_metadata=action_metadata,
        labelers=[load_object(path) for path in args.labeler],
        state_projector=load_object(args.state_projector) if args.state_projector else None,
        output_projector=load_object(args.output_projector) if args.output_projector else None,
        dedupe=args.dedupe,
        param_recipes=param_recipes,
    )
    print(f"spec directory: {spec_dir}")
    print(f"generated {view} transition cases from {len(states)} states into {out_path / args.package}")

    report_action_coverage(
        prepared,
        module=tla_path.stem,
        view=view,
        action_metadata=action_metadata,
        package_dir=out_path / args.package,
        manifest_path=manifest_path,
    )

    if param_recipes is not None:
        report_param_recovery(prepared, param_recipes, out_path / args.package)

    # Case-cap hard gate (MF-014). Runs AFTER the complete package is written:
    # the corpus is never trimmed to pass, so the artifacts on disk hold every
    # generated case whether this gate passes or fails. Over cap it reports the
    # distribution and what varies across the redundant group, then exits
    # nonzero -- fix the diagram, or raise the cap with a recorded rationale.
    enforce_case_cap(
        prepared,
        view=view,
        manifest_path=manifest_path,
        source=str(out_path / args.package),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
