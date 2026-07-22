#!/usr/bin/env python3
"""Generate and run adapter programs for TLC-derived cases.

The generated cases stay generic. A repository supplies a TOML file mapping
case labels, usually TLA action names, to adapter import paths. This script
validates coverage, writes one executable Python program per selected case into
a work directory, and optionally executes those programs.
"""

from __future__ import annotations

import argparse
import copy
from contextlib import ExitStack
import hashlib
import importlib
import inspect
import json
import os
import shlex
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Mapping

try:
    from .effect_conformance import (
        EffectDeclarationError,
        EffectRecorder,
        EffectSandbox,
        diff_effects,
        load_effect_declarations,
    )
    from .extract_spec_manifest import load_manifest
    from .spec_paths import resolve_existing_from_cwd, resolve_existing_spec_input, resolve_spec_relative_path
    from .testgraph_channels import ChannelEnforcementError, enforce_external_bindings
except ImportError:  # pragma: no cover - direct script execution
    from effect_conformance import (
        EffectDeclarationError,
        EffectRecorder,
        EffectSandbox,
        diff_effects,
        load_effect_declarations,
    )
    from extract_spec_manifest import load_manifest
    from spec_paths import resolve_existing_from_cwd, resolve_existing_spec_input, resolve_spec_relative_path
    from testgraph_channels import ChannelEnforcementError, enforce_external_bindings

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore


@dataclass(frozen=True)
class AdapterMapping:
    label: str
    adapter: str | None
    output_projection: str | None = None
    expected_projection: str | None = None
    view: str | None = None
    layer: str | None = None
    controllability: str | None = None
    projector: str | None = None
    assertion: str | None = None
    kind: str | None = None
    #: MF-015: the external channel this binding drives (http/cli/fs/queue/k8s).
    #: None on spec-unit bindings, which are in-process by contract. Every
    #: EXTERNAL binding must declare one -- see enforce_external_channels.
    channel: str | None = None
    order: int = 0


class EffectProviderConfigurationError(ValueError):
    """A semantic effect declaration cannot be resolved safely."""


@dataclass(frozen=True)
class ResolvedEffectProvider:
    port_name: str
    provider_reference: str
    provider: Any
    protocol: type[Any]


@dataclass(frozen=True)
class EffectProviderPlan:
    """Preflighted semantic providers, ordered per generated case action."""

    by_case: Mapping[str, tuple[ResolvedEffectProvider, ...]]
    configured: bool = False

    def for_case(self, case: Any) -> tuple[ResolvedEffectProvider, ...]:
        return self.by_case.get(str(case.name), ())


@dataclass(frozen=True, eq=False)
class ExecutionPoint:
    """One original generated case at one deterministic fuzz iteration."""

    case: Any
    iteration: int


class _EffectProviderPhaseFailure(RuntimeError):
    def __init__(
        self,
        *,
        point: ExecutionPoint,
        phase: str,
        binding: ResolvedEffectProvider,
        cause: BaseException,
    ) -> None:
        super().__init__(str(cause))
        self.point = point
        self.phase = phase
        self.binding = binding
        self.cause = cause


def load_cases(cases_dir: Path):
    cases_dir = cases_dir.resolve()
    sys.path.insert(0, str(cases_dir.parent))
    package_name = cases_dir.name
    for module_name in list(sys.modules):
        if module_name == package_name or module_name.startswith(f"{package_name}."):
            del sys.modules[module_name]
    return importlib.import_module(package_name)


def infer_spec_dir(cases_dir: Path, mapping: Path, explicit: Path | None) -> Path | None:
    if explicit is not None:
        return resolve_existing_from_cwd(explicit)
    mapping_candidate = mapping if mapping.is_absolute() else Path.cwd() / mapping
    if mapping_candidate.exists():
        return mapping_candidate.resolve().parent
    cases_candidate = cases_dir if cases_dir.is_absolute() else Path.cwd() / cases_dir
    if cases_candidate.exists():
        resolved = cases_candidate.resolve()
        if resolved.parent.name in {"cases", "generated"}:
            return resolved.parent.parent
        return resolved.parent
    return None


def resolve_runtime_path(path: Path, spec_dir: Path | None) -> Path:
    if spec_dir is None:
        return resolve_existing_from_cwd(path)
    return resolve_existing_spec_input(path, spec_dir)


def load_mappings(path: Path) -> dict[str, AdapterMapping]:
    loaded = load_mapping_data(path)
    mappings: dict[str, AdapterMapping] = {}

    adapter_tables = loaded.get("adapters")
    if isinstance(adapter_tables, dict):
        for label, spec in adapter_tables.items():
            if not isinstance(spec, dict):
                raise ValueError(f"[adapters.{label}] must be a table")
            adapter = spec.get("adapter")
            if not isinstance(adapter, str) or not adapter:
                raise ValueError(f"[adapters.{label}] must define adapter = \"module:object\"")
            projection = spec.get("output_projection")
            if projection is not None and not isinstance(projection, str):
                raise ValueError(f"[adapters.{label}] output_projection must be \"module:object\"")
            expected_projection = spec.get("expected_projection")
            if expected_projection is not None and not isinstance(expected_projection, str):
                raise ValueError(f"[adapters.{label}] expected_projection must be \"module:object\"")
            mappings[str(label)] = AdapterMapping(
                label=str(label),
                adapter=adapter,
                output_projection=projection,
                expected_projection=expected_projection,
                kind=spec.get("kind") if isinstance(spec.get("kind"), str) else None,
                order=len(mappings),
            )

    adapter_list = loaded.get("adapter")
    if isinstance(adapter_list, list):
        for index, spec in enumerate(adapter_list, start=1):
            if not isinstance(spec, dict):
                raise ValueError(f"[[adapter]] entry {index} must be a table")
            labels = spec.get("labels", spec.get("label"))
            adapter = spec.get("adapter")
            if not isinstance(adapter, str) or not adapter:
                raise ValueError(f"[[adapter]] entry {index} must define adapter = \"module:object\"")
            if isinstance(labels, str):
                labels = [labels]
            if not isinstance(labels, list) or not all(isinstance(label, str) for label in labels):
                raise ValueError(f"[[adapter]] entry {index} must define label or labels")
            for label in labels:
                mappings[label] = AdapterMapping(
                    label=label,
                    adapter=adapter,
                    output_projection=spec.get("output_projection") if isinstance(spec.get("output_projection"), str) else None,
                    expected_projection=spec.get("expected_projection") if isinstance(spec.get("expected_projection"), str) else None,
                    kind=spec.get("kind") if isinstance(spec.get("kind"), str) else None,
                    order=len(mappings),
                )

    action_tables = loaded.get("actions")
    if isinstance(action_tables, dict):
        for label, spec in action_tables.items():
            if not isinstance(spec, dict):
                raise ValueError(f"[actions.{label}] must be a table")
            adapter = spec.get("adapter")
            if adapter is not None and (not isinstance(adapter, str) or not adapter):
                raise ValueError(f"[actions.{label}] adapter must be \"module:object\"")
            projection = spec.get("output_projection")
            if projection is not None and not isinstance(projection, str):
                raise ValueError(f"[actions.{label}] output_projection must be \"module:object\"")
            expected_projection = spec.get("expected_projection")
            if expected_projection is not None and not isinstance(expected_projection, str):
                raise ValueError(f"[actions.{label}] expected_projection must be \"module:object\"")
            projector = spec.get("projector")
            if projector is not None and not isinstance(projector, str):
                raise ValueError(f"[actions.{label}] projector must be \"module:object\"")
            assertion = spec.get("assertion")
            if assertion is not None and not isinstance(assertion, str):
                raise ValueError(f"[actions.{label}] assertion must be \"module:object\"")
            mappings[str(label)] = AdapterMapping(
                label=str(label),
                adapter=adapter,
                output_projection=projection,
                expected_projection=expected_projection,
                view=spec.get("view") if isinstance(spec.get("view"), str) else None,
                layer=spec.get("layer") if isinstance(spec.get("layer"), str) else None,
                controllability=spec.get("controllability") if isinstance(spec.get("controllability"), str) else None,
                projector=projector,
                assertion=assertion,
                kind=spec.get("kind") if isinstance(spec.get("kind"), str) else None,
                channel=spec.get("channel") if isinstance(spec.get("channel"), str) else None,
                order=len(mappings),
            )

    if not mappings:
        raise ValueError(f"no adapter mappings found in {path}")
    return mappings


def load_mapping_data(path: Path) -> dict[str, Any]:
    if path.suffix.lower() in {".yaml", ".yml"}:
        return load_manifest(path)
    return load_toml(path)


def load_toml(path: Path) -> dict[str, Any]:
    text = path.read_text()
    if tomllib is not None:
        return tomllib.loads(text)
    return parse_simple_mapping_toml(text)


def parse_simple_mapping_toml(text: str) -> dict[str, Any]:
    loaded: dict[str, Any] = {}
    current: dict[str, Any] | None = None
    current_list: list[dict[str, Any]] | None = None
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line == "[[adapter]]":
            current_list = loaded.setdefault("adapter", [])
            current = {}
            current_list.append(current)
            continue
        if line.startswith("[adapters.") and line.endswith("]"):
            label = line[len("[adapters.") : -1]
            adapters = loaded.setdefault("adapters", {})
            if label in adapters:
                raise ValueError(f"duplicate [adapters.{label}] table")
            current = {}
            adapters[label] = current
            continue
        if line.startswith("[actions.") and line.endswith("]"):
            label = line[len("[actions.") : -1]
            actions = loaded.setdefault("actions", {})
            if label in actions:
                raise ValueError(f"duplicate [actions.{label}] table")
            current = {}
            actions[label] = current
            continue
        if line.startswith("[effect_providers.") and line.endswith("]"):
            port_name = line[len("[effect_providers.") : -1]
            providers = loaded.setdefault("effect_providers", {})
            if port_name in providers:
                raise ValueError(f"duplicate [effect_providers.{port_name}] table")
            current = {}
            providers[port_name] = current
            continue
        if "=" not in line or current is None:
            raise ValueError(f"unsupported TOML line: {raw_line!r}")
        key, raw_value = line.split("=", 1)
        key = key.strip()
        if key in current:
            raise ValueError(f"duplicate key {key!r} in TOML table")
        current[key] = parse_simple_toml_value(raw_value.strip())
    return loaded


def parse_simple_toml_value(value: str) -> Any:
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        body = value[1:-1].strip()
        if not body:
            return []
        return [parse_simple_toml_value(part.strip()) for part in body.split(",")]
    raise ValueError(f"unsupported TOML value: {value!r}")


def _case_action(case: Any) -> str:
    action = getattr(getattr(case, "input", None), "action", None)
    if not isinstance(action, str) or not action:
        raise EffectProviderConfigurationError(
            f"case {getattr(case, 'name', '<unnamed>')} has no string input.action for semantic effect lookup"
        )
    return action


_SEMANTIC_CASE_FIELDS = ("before", "input", "output", "after")


def _case_semantic_snapshot(case: Any) -> tuple[tuple[str, bool, Any], ...]:
    """Detach the generated oracle fields from any mutable nested values."""

    snapshot: list[tuple[str, bool, Any]] = []
    try:
        for field_name in _SEMANTIC_CASE_FIELDS:
            present = hasattr(case, field_name)
            value = copy.deepcopy(getattr(case, field_name)) if present else None
            snapshot.append((field_name, present, value))
    except Exception as exc:
        raise EffectProviderConfigurationError(
            f"case {getattr(case, 'name', '<unnamed>')} semantic fields could not be snapshotted: {exc}"
        ) from exc
    return tuple(snapshot)


def _assert_case_semantics_unchanged(
    case: Any,
    snapshot: tuple[tuple[str, bool, Any], ...],
    *,
    stage: str,
) -> None:
    changed: list[str] = []
    for field_name, was_present, expected in snapshot:
        is_present = hasattr(case, field_name)
        if is_present != was_present:
            changed.append(field_name)
            continue
        if is_present and getattr(case, field_name) != expected:
            changed.append(field_name)
    if changed:
        raise RuntimeError(
            f"{stage} mutated generated case semantic field(s) {', '.join(changed)}; "
            "effect providers and adapters must not rewrite the test oracle"
        )


def _semantic_provider_tables(mapping_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    raw = mapping_data.get("effect_providers")
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise EffectProviderConfigurationError("[effect_providers] must contain one table per typed port")
    providers: dict[str, dict[str, Any]] = {}
    for raw_name, raw_spec in raw.items():
        name = str(raw_name)
        if not name or name.strip() != name:
            raise EffectProviderConfigurationError("semantic effect provider port names must be non-empty and trimmed")
        if not isinstance(raw_spec, dict):
            raise EffectProviderConfigurationError(f"[effect_providers.{name}] must be a table")
        unknown_keys = sorted(set(raw_spec) - {"provider"})
        if unknown_keys:
            raise EffectProviderConfigurationError(
                f"[effect_providers.{name}] has unknown key(s): {', '.join(unknown_keys)}"
            )
        reference = raw_spec.get("provider")
        if not isinstance(reference, str) or not reference or reference.strip() != reference:
            raise EffectProviderConfigurationError(
                f"[effect_providers.{name}] must define provider = \"module:object\""
            )
        providers[name] = raw_spec
    return providers


def _load_generated_port_protocol(
    *,
    package: str,
    port_name: str,
    import_roots: list[Path],
) -> type[Any]:
    ensure_import_roots(import_roots)
    module_name = f"{package}.ports"
    try:
        module = importlib.import_module(module_name)
        protocol = getattr(module, port_name)
    except (ImportError, AttributeError) as exc:
        raise EffectProviderConfigurationError(
            f"could not load generated port {port_name} from {module_name}; "
            "generate the manifest package and add its parent with --import-root"
        ) from exc
    if not isinstance(protocol, type) or not getattr(protocol, "_is_protocol", False):
        raise EffectProviderConfigurationError(f"generated port {module_name}:{port_name} is not a Protocol")
    if not getattr(protocol, "_is_runtime_protocol", False):
        raise EffectProviderConfigurationError(
            f"generated port {module_name}:{port_name} is not runtime-checkable; regenerate it with EP-01 codegen"
        )
    return protocol


def _load_provider(reference: str) -> Any:
    from spec_double_compiler.runtime import load_object

    try:
        loaded = load_object(reference)
        provider = loaded() if isinstance(loaded, type) else loaded
    except Exception as exc:
        raise EffectProviderConfigurationError(f"could not load provider {reference!r}: {exc}") from exc
    if not callable(provider) and not callable(getattr(provider, "bind", None)):
        raise EffectProviderConfigurationError(
            f"provider {reference!r} must be callable or define bind(context)"
        )
    return provider


def load_effect_provider_plan(
    *,
    spec_dir: Path | None,
    mapping_path: Path,
    cases: list[Any],
    import_roots: list[Path],
) -> EffectProviderPlan:
    """Resolve case action -> declared typed ports -> project providers.

    This is a static preflight: every selected action, port, generated Protocol,
    and provider reference is checked before an adapter is instantiated or any
    application hook runs. Provider context managers themselves are constructed
    in a second batch preflight once case work directories are known.
    """

    try:
        mapping_data = load_mapping_data(mapping_path)
    except Exception as exc:
        raise EffectProviderConfigurationError(f"invalid provider mapping {mapping_path}: {exc}") from exc
    provider_specs = _semantic_provider_tables(mapping_data)
    if spec_dir is None:
        if provider_specs:
            raise EffectProviderConfigurationError(
                "semantic effect providers require --spec-dir with spec_manifest.yaml and actions.yml"
            )
        return EffectProviderPlan(MappingProxyType({}), configured=False)

    manifest_path = spec_dir / "spec_manifest.yaml"
    actions_path = spec_dir / "actions.yml"
    if not manifest_path.is_file() or not actions_path.is_file():
        if provider_specs:
            missing = [path.name for path in (manifest_path, actions_path) if not path.is_file()]
            raise EffectProviderConfigurationError(
                f"semantic effect providers require {', '.join(missing)} under {spec_dir}"
            )
        return EffectProviderPlan(MappingProxyType({}), configured=False)

    manifest = load_manifest(manifest_path)
    actions_document = load_manifest(actions_path)
    raw_ports = manifest.get("ports", {})
    raw_actions = actions_document.get("actions", {})
    if not isinstance(raw_ports, dict):
        raise EffectProviderConfigurationError("spec_manifest.yaml ports must be a mapping")
    if not isinstance(raw_actions, dict):
        raise EffectProviderConfigurationError("actions.yml actions must be a mapping")

    # An existing spec may carry actions.yml for passive observation while its
    # generated cases predate ``input.action``.  Empty/absent effect_ports and
    # no provider table mean EP-01 is not configured at all, so leave that
    # legacy path untouched.  Explicit malformed or non-empty declarations are
    # intentionally not treated as empty; they proceed to fail closed below.
    semantic_schema_present = bool(provider_specs)
    for raw_action_spec in raw_actions.values():
        if isinstance(raw_action_spec, dict) and "effect_ports" in raw_action_spec:
            semantic_schema_present = semantic_schema_present or raw_action_spec["effect_ports"] != []
    if not semantic_schema_present:
        return EffectProviderPlan(MappingProxyType({}), configured=False)

    effect_ports: dict[str, dict[str, Any]] = {}
    for raw_name, raw_spec in raw_ports.items():
        if isinstance(raw_spec, dict) and raw_spec.get("role") == "effect":
            name = str(raw_name)
            if not name or name.strip() != name:
                raise EffectProviderConfigurationError(
                    "manifest semantic effect port names must be non-empty and trimmed"
                )
            effect_ports[name] = raw_spec

    for port_name in provider_specs:
        if port_name not in effect_ports:
            raise EffectProviderConfigurationError(
                f"provider configured for unknown semantic effect port {port_name}; "
                "declare it under manifest ports with role: effect"
            )

    package = manifest.get("package")
    providers_by_reference: dict[str, Any] = {}
    protocols_by_port: dict[str, type[Any]] = {}
    by_case: dict[str, tuple[ResolvedEffectProvider, ...]] = {}
    used_provider_ports: set[str] = set()
    configured = bool(provider_specs)
    protocol_roots = [spec_dir / "generated", spec_dir, *import_roots]

    for case in cases:
        action = _case_action(case)
        if action not in raw_actions:
            raise EffectProviderConfigurationError(
                f"case {case.name} action {action} is not declared in actions.yml; "
                "declare it with effect_ports: [] when it requires no semantic providers"
            )
        raw_action_spec = raw_actions[action]
        if not isinstance(raw_action_spec, dict):
            raise EffectProviderConfigurationError(f"actions.yml action {action} must be a mapping")
        if "effect_ports" not in raw_action_spec:
            raise EffectProviderConfigurationError(
                f"actions.yml action {action} must declare effect_ports; use effect_ports: [] for none"
            )
        raw_required = raw_action_spec["effect_ports"]
        if not isinstance(raw_required, list) or not all(
            isinstance(name, str) and bool(name) and name.strip() == name for name in raw_required
        ):
            raise EffectProviderConfigurationError(f"actions.yml action {action} effect_ports must be a list of port names")
        configured = configured or bool(raw_required)
        seen: set[str] = set()
        resolved: list[ResolvedEffectProvider] = []
        for port_name in raw_required:
            if port_name in seen:
                raise EffectProviderConfigurationError(
                    f"action {action} declares duplicate semantic effect port {port_name}"
                )
            seen.add(port_name)
            if port_name not in effect_ports:
                raise EffectProviderConfigurationError(
                    f"action {action} references unknown semantic effect port {port_name}; "
                    "declare it under manifest ports with role: effect"
                )
            provider_spec = provider_specs.get(port_name)
            if provider_spec is None:
                raise EffectProviderConfigurationError(
                    f"action {action} is missing provider for semantic effect port {port_name}"
                )
            used_provider_ports.add(port_name)
            if not isinstance(package, str) or not package:
                raise EffectProviderConfigurationError(
                    f"manifest package is required to resolve generated port {port_name}"
                )
            protocol = protocols_by_port.get(port_name)
            if protocol is None:
                protocol = _load_generated_port_protocol(
                    package=package,
                    port_name=port_name,
                    import_roots=protocol_roots,
                )
                protocols_by_port[port_name] = protocol
            reference = str(provider_spec["provider"])
            provider = providers_by_reference.get(reference)
            if provider is None:
                provider = _load_provider(reference)
                providers_by_reference[reference] = provider
            resolved.append(
                ResolvedEffectProvider(
                    port_name=port_name,
                    provider_reference=reference,
                    provider=provider,
                    protocol=protocol,
                )
            )
        by_case[str(case.name)] = tuple(resolved)

    orphan_ports = sorted(set(provider_specs) - used_provider_ports)
    if orphan_ports:
        raise EffectProviderConfigurationError(
            "provider configured for semantic effect port(s) not required by any selected case: "
            + ", ".join(orphan_ports)
        )

    return EffectProviderPlan(MappingProxyType(by_case), configured=configured)


def validate_effect_provider_execution_mode(
    plan: EffectProviderPlan,
    *,
    batch: bool,
    validate_only: bool,
) -> None:
    if plan.configured and not batch and not validate_only:
        raise SystemExit(
            "ERROR: semantic effect providers require --batch in V0; "
            "non-batch generated programs and exported cases cannot silently ignore provider bindings"
        )


def case_labels(cases: list[Any]) -> set[str]:
    labels: set[str] = set()
    for case in cases:
        labels.update(str(label) for label in case.labels)
    return labels


def case_view(case: Any) -> str:
    return str(getattr(case, "view", "internal"))


def case_controllability(case: Any) -> str:
    return str(getattr(case, "controllability", "unit_direct"))


def case_generates(case: Any) -> set[str]:
    return {str(item) for item in getattr(case, "generates", frozenset({"spec_unit"}))}


def requires_action_adapter(case: Any) -> bool:
    controllability = case_controllability(case)
    if controllability == "hidden":
        return False
    if case_view(case) == "external" and controllability == "observable":
        return False
    return True


def requires_observation_binding(case: Any) -> bool:
    return case_view(case) == "external" and case_controllability(case) == "observable"


def uses_projected_state_assertion(case: Any, mapping: AdapterMapping) -> bool:
    return case_view(case) == "external" and bool(mapping.projector or mapping.expected_projection or mapping.assertion)


def validate_mapping_coverage(cases: list[Any], mappings: dict[str, AdapterMapping]) -> None:
    errors: list[str] = []
    for case in cases:
        mapping = adapter_for_case(case, mappings)
        if mapping is None:
            if requires_action_adapter(case) or requires_observation_binding(case):
                errors.append(f"{case.name}: no binding for labels {sorted(case.labels)}")
            continue
        if requires_action_adapter(case) and not mapping.adapter:
            errors.append(f"{case.name}: binding for {mapping.label} does not define adapter")
        if requires_observation_binding(case) or uses_projected_state_assertion(case, mapping):
            missing = []
            if not mapping.projector:
                missing.append("projector")
            if missing:
                errors.append(f"{case.name}: projected-state binding for {mapping.label} missing {', '.join(missing)}")
    if errors:
        raise SystemExit(
            "ERROR: missing adapter bindings for cases:\n"
            + "\n".join(errors[:20])
            + (f"\n... and {len(errors) - 20} more" if len(errors) > 20 else "")
            + "\nAdd entries such as [adapters.LabelName] adapter = \"module:Adapter\" for unit/direct actions "
            + "or [actions.LabelName] bindings for external observable actions."
        )


def enforce_external_channels(
    cases: list[Any],
    mappings: dict[str, AdapterMapping],
    mapping_path: Path,
    import_roots: list[Path],
) -> None:
    """MF-015: hold every EXTERNAL case's binding to the external contract.

    The gate is driven by the CASE's own view, not by a ``--view external``
    flag. A mixed corpus run without the flag would otherwise execute external
    cases with no channel check at all, which is exactly the silent degradation
    the doctrine forbids. Internal cases are untouched: a spec-unit adapter is
    in-process by contract and correctly imports the production package.
    """
    external_actions = {
        mapping.label
        for case in cases
        if case_view(case) == "external"
        for mapping in [adapter_for_case(case, mappings)]
        if mapping is not None
    }
    if not external_actions:
        return

    contract = enforce_external_bindings(
        mapping_path,
        import_roots=import_roots,
        actions=external_actions,
    )
    print(
        f"external channel enforcement passed for {len(external_actions)} binding(s); "
        f"integration rung {contract.rung()} "
        f"(real: {', '.join(contract.real_ports) or 'none'}; "
        f"double: {', '.join(contract.double_ports) or 'none'})"
    )


def selected_cases(
    cases: list[Any],
    labels: list[str],
    names: list[str],
    limit: int | None,
    view: str | None = None,
) -> list[Any]:
    selected = cases
    if view is not None:
        selected = [case for case in selected if case_view(case) == view]
    if labels:
        label_set = set(labels)
        selected = [case for case in selected if label_set.intersection(set(case.labels))]
    if names:
        name_set = set(names)
        selected = [case for case in selected if case.name in name_set]
    if limit is not None:
        selected = selected[:limit]
    return selected


def adapter_for_case(case: Any, mappings: dict[str, AdapterMapping]) -> AdapterMapping | None:
    labels = {str(label) for label in case.labels}
    candidates = [mapping for label, mapping in mappings.items() if label in labels]
    if not candidates:
        return None
    return sorted(candidates, key=lambda mapping: mapping.order)[0]


def adapter_kind(mapping: AdapterMapping) -> str:
    return mapping.kind or mapping.adapter or mapping.label


def load_adapter(mapping: AdapterMapping, import_roots: list[Path]):
    if mapping.adapter is None:
        raise TypeError(f"binding for {mapping.label} does not define an executable adapter")
    ensure_import_roots(import_roots)
    from spec_double_compiler.runtime import instantiate, load_object

    return instantiate(load_object(mapping.adapter))


def maybe_await(value: Any) -> Any:
    if inspect.isawaitable(value):
        import asyncio

        return asyncio.run(value)
    return value


def call_optional_hook(target: Any, name: str, context: Any) -> None:
    hook = getattr(target, name, None)
    if hook is None:
        return
    maybe_await(hook(context))


def instantiate_cached(path: str, cache: dict[str, Any]):
    from spec_double_compiler.runtime import load_object

    obj = cache.get(path)
    if obj is None:
        loaded = load_object(path)
        obj = loaded() if isinstance(loaded, type) else loaded
        cache[path] = obj
    return obj


def invoke_with_fallbacks(callable_obj: Any, candidates: list[tuple[Any, ...]]) -> Any:
    last_type_error: TypeError | None = None
    for args in candidates:
        try:
            return maybe_await(callable_obj(*args))
        except TypeError as exc:
            last_type_error = exc
    if last_type_error is not None:
        raise last_type_error
    raise TypeError(f"{callable_obj!r} is not callable")


def object_callable(obj: Any, method_names: tuple[str, ...]) -> Any:
    for name in method_names:
        method = getattr(obj, name, None)
        if method is not None:
            return method
    if callable(obj):
        return obj
    raise TypeError(f"{obj!r} is not callable and does not define one of {method_names}")


def expected_state_from_case(case_context: Any, mapping: AdapterMapping, object_cache: dict[str, Any]) -> Any:
    if mapping.expected_projection is None:
        return case_context.case.after
    projector = instantiate_cached(mapping.expected_projection, object_cache)
    callable_obj = object_callable(projector, ("project", "expected", "expected_state"))
    return invoke_with_fallbacks(
        callable_obj,
        [
            (case_context,),
            (case_context.case,),
            (case_context.case.before, case_context.case.input, case_context.case.after, case_context.case.output),
        ],
    )


def actual_state_from_cluster(assertion_context: Any, mapping: AdapterMapping, object_cache: dict[str, Any]) -> Any:
    if mapping.projector is None:
        raise AssertionError(f"projected-state assertion for {assertion_context.case.name} requires a projector")
    projector = instantiate_cached(mapping.projector, object_cache)
    callable_obj = object_callable(projector, ("observe", "project", "actual", "actual_state"))
    return invoke_with_fallbacks(
        callable_obj,
        [
            (assertion_context,),
            (assertion_context.case, assertion_context.result, assertion_context.work_dir),
            (assertion_context.case, assertion_context.result),
            (assertion_context.case,),
        ],
    )


def compare_fields_honoring_unchecked(
    expected: dict[str, Any],
    actual: dict[str, Any],
    unobservable: tuple[str, ...] = (),
) -> dict[str, list[Any]]:
    """Compare two state dicts field by field, honoring UNCHECKED fields.

    MF-032: this is the per-field replacement for the runner's old
    all-or-nothing ``==``. A field named in ``unobservable`` is reported as
    UNCHECKED -- never as an agreement and never as a disagreement -- because
    "this field cannot be observed" is a real and distinct outcome from "this
    field agrees". Every other field is compared on its own, so a run reports
    exactly which fields matched, which diverged, and which were not checked,
    instead of collapsing all of that into a single boolean. Reporting UNCHECKED
    honestly is the safeguard MF-028/MF-029 kept needing: an unobservable field
    that is silently treated as agreement is the tautology that hides a defect.
    """
    unobs = set(unobservable)
    agreements: list[str] = []
    disagreements: list[dict[str, Any]] = []
    unchecked: list[str] = []
    for field in sorted(set(expected) | set(actual)):
        if field in unobs:
            unchecked.append(field)
        elif expected.get(field) == actual.get(field):
            agreements.append(field)
        else:
            disagreements.append({"field": field, "expected": expected.get(field), "actual": actual.get(field)})
    return {"agreements": agreements, "disagreements": disagreements, "unchecked": unchecked}


def _unobservable_from_result(result: Any) -> tuple[str, ...]:
    """Fields an adapter declared unobservable, surfaced through semantic_output.

    An adapter that returns a real ``after`` dict can declare which of its
    fields could not be observed by listing them under
    ``semantic_output["unobservable"]``. The runner honors that list rather than
    forcing the adapter to either fail forever on an unobservable field or fake
    agreement by copying it out of the case -- the exact bind MF-028 recorded.
    """
    semantic = getattr(result, "semantic_output", None)
    if isinstance(semantic, dict):
        declared = semantic.get("unobservable")
        if isinstance(declared, (list, tuple)):
            return tuple(str(field) for field in declared)
    return ()


def assert_case_result_per_field(*, case: Any, result: Any, projector: Any | None = None) -> None:
    """Per-field replacement for ``runtime.assert_case_result``.

    MF-032 (deferred here by MF-031): the runner used to compare ``result.after``
    to ``case.after`` with ``==`` over the whole dict -- there was no way to say
    "this field is not observable", so an adapter with one unprojectable field
    had to return ``after=None`` and hand-roll its own comparison. This compares
    field by field and honors UNCHECKED, so an adapter can return a real
    ``after`` plus the fields it could not observe and get an honest verdict from
    the runner. Output and projector-semantic checks keep runtime's behavior.
    """
    if result.output is not None and result.output != case.output:
        raise AssertionError(f"adapter output mismatch for {case.name}: {result.output!r} != {case.output!r}")
    if result.after is not None:
        expected = dict(getattr(case, "after"))
        actual = dict(result.after)
        comparison = compare_fields_honoring_unchecked(expected, actual, _unobservable_from_result(result))
        if comparison["disagreements"]:
            detail = "; ".join(
                f"{item['field']}: expected {item['expected']!r}, actual {item['actual']!r}"
                for item in comparison["disagreements"]
            )
            raise AssertionError(f"adapter after-state mismatch for {case.name}: {detail}")
    if projector is not None:
        from spec_double_compiler.runtime import project_expected_output

        expected_output = project_expected_output(projector, case)
        if result.semantic_output != expected_output:
            raise AssertionError(
                f"adapter semantic output mismatch for {case.name}: {result.semantic_output!r} != {expected_output!r}"
            )


def assert_projected_state(assertion_context: Any, mapping: AdapterMapping, object_cache: dict[str, Any]) -> None:
    if mapping.assertion is None:
        expected = assertion_context.expected
        actual = assertion_context.actual
        unobservable = tuple(getattr(assertion_context, "unobservable", ()) or ())
        # MF-032: per-field comparison honoring UNCHECKED. Dict projections are
        # compared field by field so an unobservable field can be declared rather
        # than faked; non-dict projections keep whole-value equality.
        if isinstance(expected, dict) and isinstance(actual, dict):
            comparison = compare_fields_honoring_unchecked(expected, actual, unobservable)
            if comparison["disagreements"]:
                detail = "; ".join(
                    f"{item['field']}: expected {item['expected']!r}, actual {item['actual']!r}"
                    for item in comparison["disagreements"]
                )
                raise AssertionError(f"projected state mismatch for {assertion_context.case.name}: {detail}")
            return
        if actual != expected:
            raise AssertionError(
                f"projected state mismatch for {assertion_context.case.name}: "
                f"{actual!r} != {expected!r}"
            )
        return
    assertion = instantiate_cached(mapping.assertion, object_cache)
    callable_obj = object_callable(assertion, ("assert_state", "assert_projected_state", "assert_step"))
    result = invoke_with_fallbacks(
        callable_obj,
        [
            (assertion_context,),
            (assertion_context.expected, assertion_context.actual),
            (assertion_context.case, assertion_context.expected, assertion_context.actual),
        ],
    )
    if result is False:
        raise AssertionError(f"projected state assertion returned False for {assertion_context.case.name}")


def assert_projected_state_if_configured(case_context: Any, mapping: AdapterMapping, object_cache: dict[str, Any]) -> None:
    if case_view(case_context.case) != "external" or mapping.projector is None:
        return
    from spec_double_compiler.runtime import ProjectedStateAssertionContext

    assertion_context = ProjectedStateAssertionContext(
        kind=case_context.kind,
        case=case_context.case,
        work_dir=case_context.work_dir,
        mapping=case_context.mapping,
        shared=case_context.shared,
        result=case_context.result,
        effects=case_context.effects,
    )
    assertion_context.expected = expected_state_from_case(case_context, mapping, object_cache)
    assertion_context.actual = actual_state_from_cluster(assertion_context, mapping, object_cache)
    assert_projected_state(assertion_context, mapping, object_cache)


def ensure_import_roots(import_roots: list[Path]) -> None:
    skill_root = Path(__file__).resolve().parents[1]
    for root in [skill_root, *import_roots]:
        resolved = str(root.resolve())
        if resolved not in sys.path:
            sys.path.insert(0, resolved)


def validate_adapter_capabilities(
    *,
    cases: list[Any],
    mappings: dict[str, AdapterMapping],
    import_roots: list[Path],
) -> None:
    ensure_import_roots(import_roots)
    from spec_double_compiler.runtime import adapter_accepts_case

    adapter_cache: dict[str, Any] = {}
    rejected: list[str] = []
    for case in cases:
        mapping = adapter_for_case(case, mappings)
        if mapping is None:
            if not requires_action_adapter(case) and not requires_observation_binding(case):
                continue
            rejected.append(f"{case.name}: no mapped label among {sorted(case.labels)}")
            continue
        if not requires_action_adapter(case):
            continue
        if mapping.adapter is None:
            rejected.append(f"{case.name} via {mapping.label}: binding does not define adapter")
            continue
        adapter = adapter_cache.get(mapping.adapter)
        if adapter is None:
            adapter = load_adapter(mapping, import_roots)
            adapter_cache[mapping.adapter] = adapter
        accepted, reason = adapter_accepts_case(adapter, case)
        if not accepted:
            rejected.append(f"{case.name} via {mapping.label}: {reason or 'adapter rejected case'}")
    if rejected:
        details = "\n".join(rejected[:50])
        suffix = f"\n... and {len(rejected) - 50} more" if len(rejected) > 50 else ""
        raise SystemExit(f"ERROR: adapter capability validation failed for {len(rejected)} cases\n{details}{suffix}")


def write_case_program(
    *,
    case: Any,
    mapping: AdapterMapping,
    cases_dir: Path,
    program_path: Path,
    case_work_dir: Path,
    import_roots: list[Path],
) -> None:
    program_path.parent.mkdir(parents=True, exist_ok=True)
    case_work_dir.mkdir(parents=True, exist_ok=True)
    root_inserts = "\n".join(
        f"sys.path.insert(0, {str(root.resolve())!r})" for root in [Path(__file__).resolve().parents[1], *import_roots]
    )
    content = f"""#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, {str(cases_dir.resolve().parent)!r})
{root_inserts}

from {cases_dir.name}.cases import CASES_BY_NAME
from {cases_dir.name}.validators import assert_case_replays
from scripts.run_generated_case_adapters import AdapterMapping, adapter_kind, assert_case_result_per_field, assert_projected_state_if_configured
from spec_double_compiler.runtime import AdapterCaseContext, call_adapter, instantiate, load_object


MAPPING = AdapterMapping(
    label={mapping.label!r},
    adapter={mapping.adapter!r},
    output_projection={mapping.output_projection!r},
    expected_projection={mapping.expected_projection!r},
    view={mapping.view!r},
    layer={mapping.layer!r},
    controllability={mapping.controllability!r},
    projector={mapping.projector!r},
    assertion={mapping.assertion!r},
    kind={mapping.kind!r},
    channel={mapping.channel!r},
    order={mapping.order!r},
)


def main() -> int:
    case = CASES_BY_NAME[{case.name!r}]
    assert_case_replays(case)
    adapter = instantiate(load_object({mapping.adapter!r}))
    projector = None
    if MAPPING.output_projection is not None:
        projector = load_object(MAPPING.output_projection)
    case_work_dir = Path({str(case_work_dir.resolve())!r})
    result = call_adapter(adapter, case, case_work_dir)
    assert_case_result_per_field(
        case=case,
        result=result,
        projector=projector,
    )
    case_context = AdapterCaseContext(
        kind=adapter_kind(MAPPING),
        case=case,
        work_dir=case_work_dir,
        mapping=MAPPING,
        shared={{}},
        result=result,
    )
    assert_projected_state_if_configured(case_context, MAPPING, {{}})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""
    program_path.write_text(content)
    program_path.chmod(0o755)


def generate_programs(
    *,
    cases: list[Any],
    mappings: dict[str, AdapterMapping],
    cases_dir: Path,
    work_dir: Path,
    import_roots: list[Path],
) -> list[Path]:
    programs: list[Path] = []
    for case in cases:
        mapping = adapter_for_case(case, mappings)
        if mapping is None:
            raise AssertionError(f"no adapter mapping for case {case.name}: {sorted(case.labels)}")
        if mapping.adapter is None:
            raise SystemExit(f"ERROR: case {case.name} via {mapping.label} has no executable adapter")
        case_component = _opaque_path_component("case", case.name)
        program_path = work_dir / "programs" / f"{case_component}.py"
        case_work_dir = work_dir / "case-work" / case_component
        write_case_program(
            case=case,
            mapping=mapping,
            cases_dir=cases_dir,
            program_path=program_path,
            case_work_dir=case_work_dir,
            import_roots=import_roots,
        )
        programs.append(program_path)
    return programs


class _null_context:
    """No-op context used when effect conformance has nothing declared to check."""

    def __enter__(self) -> None:
        return None

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        return None


def _provider_context_manager(binding: ResolvedEffectProvider, context: Any) -> Any:
    from spec_double_compiler.runtime import EffectProviderBinding

    binder = getattr(binding.provider, "bind", None)
    semantic_snapshot = _case_semantic_snapshot(context.case)
    try:
        scope = binder(context) if callable(binder) else binding.provider(context)
    except Exception as exc:
        raise EffectProviderConfigurationError(
            f"provider {binding.provider_reference!r} could not bind {binding.port_name} "
            f"for case {context.case.name}: {exc}"
        ) from exc
    try:
        _assert_case_semantics_unchanged(
            context.case,
            semantic_snapshot,
            stage=f"provider {binding.provider_reference!r} binding",
        )
    except RuntimeError as exc:
        raise EffectProviderConfigurationError(str(exc)) from exc
    if not isinstance(scope, EffectProviderBinding):
        raise EffectProviderConfigurationError(
            f"provider {binding.provider_reference!r} for {binding.port_name} must return a context manager"
        )
    return scope


class _ProviderExitTracker:
    """Retain primary and cleanup failures across context-manager unwinding."""

    def __init__(self) -> None:
        self.primary_error: Exception | None = None
        self.cleanup_errors: list[tuple[ResolvedEffectProvider, Exception]] = []

    def observe_incoming(self, error: Exception | None) -> None:
        if error is None or self.primary_error is not None:
            return
        if any(error is cleanup_error for _binding, cleanup_error in self.cleanup_errors):
            return
        self.primary_error = error


class _NonSuppressingProviderScope:
    """Delegate provider cleanup while making truthy ``__exit__`` inert.

    Provider cleanup must receive the real exception so ordinary context
    managers can restore patches correctly.  Its return value, however, is not
    allowed to decide whether a framework/application failure survives.  Every
    cleanup exception is retained separately before normal ExitStack unwinding
    continues to the remaining providers in reverse order.
    """

    def __init__(
        self,
        scope: Any,
        tracker: _ProviderExitTracker,
        binding: ResolvedEffectProvider,
    ) -> None:
        self.scope = scope
        self.tracker = tracker
        self.binding = binding

    def __enter__(self) -> Any:
        return self.scope.__enter__()

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> bool:
        self.tracker.observe_incoming(exc if isinstance(exc, Exception) else None)
        try:
            self.scope.__exit__(exc_type, exc, traceback)
        except Exception as cleanup_error:
            self.tracker.cleanup_errors.append((self.binding, cleanup_error))
            raise
        return False


_WORK_PATH_KEY_VERSION = "tla-spec-dev/work-path/v1"


def _opaque_path_component(role: str, value: Any) -> str:
    """Return a stable, bounded filesystem identity without embedding input text."""

    payload = json.dumps(
        [_WORK_PATH_KEY_VERSION, str(role), str(value)],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return f"{role}-{hashlib.sha256(payload).hexdigest()[:32]}"


def _point_work_dir(work_dir: Path, point: ExecutionPoint, *, iteration_paths: bool) -> Path:
    case_root = work_dir / "case-work" / _opaque_path_component("case", point.case.name)
    if not iteration_paths:
        return case_root
    return case_root / f"iteration-{point.iteration:06d}"


def _provider_seed_rows(
    plan: EffectProviderPlan,
    point: ExecutionPoint,
    root_seed: int,
) -> list[dict[str, Any]]:
    from spec_double_compiler.effects import derive_effect_seed

    return [
        {
            "port": binding.port_name,
            "provider": binding.provider_reference,
            "derived_seed": derive_effect_seed(
                root_seed,
                str(point.case.name),
                point.iteration,
                binding.port_name,
            ),
        }
        for binding in plan.for_case(point.case)
    ]


def _structured_failure(
    *,
    point: ExecutionPoint,
    phase: str,
    error: BaseException,
    plan: EffectProviderPlan,
    root_seed: int,
    replay_command_factory: Callable[[ExecutionPoint], str] | None,
    binding: ResolvedEffectProvider | None = None,
) -> str:
    from spec_double_compiler.effects import (
        EFFECT_SEED_VERSION,
        EffectProviderEnterCleanupError,
    )

    providers = _provider_seed_rows(plan, point, root_seed)
    payload: dict[str, Any] = {
        "case": str(point.case.name),
        "iteration": point.iteration,
        "root_seed": root_seed,
        "seed_version": EFFECT_SEED_VERSION,
        "phase": phase,
        "providers": providers,
        "error_type": type(error).__name__,
        "error": str(error),
        "replay": replay_command_factory(point) if replay_command_factory is not None else "",
    }
    if binding is not None:
        payload["provider"] = next(
            row for row in providers if row["port"] == binding.port_name
        )
    if isinstance(error, EffectProviderEnterCleanupError):
        payload["primary_error"] = {
            "error_type": type(error.primary).__name__,
            "error": str(error.primary),
        }
        payload["cleanup_errors"] = [
            {"error_type": type(cleanup).__name__, "error": str(cleanup)}
            for cleanup in error.cleanup_errors
        ]
    return "EFFECT_FUZZ_FAILURE " + json.dumps(payload, ensure_ascii=False, sort_keys=True)


def prepare_effect_provider_scopes(
    *,
    plan: EffectProviderPlan,
    points: list[ExecutionPoint],
    work_dir: Path,
    root_seed: int = 0,
    iteration_paths: bool = False,
) -> Mapping[ExecutionPoint, tuple[tuple[ResolvedEffectProvider, Any], ...]]:
    """Construct every provider scope before any adapter/application hook runs."""

    # Preserve the pre-EP-01 execution path exactly when no semantic provider
    # table is configured.  In particular, passive ``effects:`` cases predate
    # generated action inputs and may legitimately carry ``input=None``.
    # Semantic action lookup belongs exclusively to a configured provider
    # plan; an empty plan must not make legacy cases satisfy that new schema.
    if not plan.configured:
        return MappingProxyType({})

    from spec_double_compiler.effects import EFFECT_SEED_VERSION, derive_effect_seed
    from spec_double_compiler.runtime import EffectProviderContext

    prepared: dict[ExecutionPoint, tuple[tuple[ResolvedEffectProvider, Any], ...]] = {}
    for point in points:
        case = point.case
        action = _case_action(case)
        context_work_dir = _point_work_dir(work_dir, point, iteration_paths=iteration_paths)
        context_work_dir.mkdir(parents=True, exist_ok=True)
        entries: list[tuple[ResolvedEffectProvider, Any]] = []
        for binding in plan.for_case(case):
            context = EffectProviderContext(
                port_name=binding.port_name,
                action=action,
                case=case,
                work_dir=context_work_dir,
                iteration=point.iteration,
                root_seed=root_seed,
                derived_seed=derive_effect_seed(
                    root_seed,
                    str(case.name),
                    point.iteration,
                    binding.port_name,
                ),
                seed_version=EFFECT_SEED_VERSION,
            )
            try:
                scope = _provider_context_manager(binding, context)
            except BaseException as exc:
                raise _EffectProviderPhaseFailure(
                    point=point,
                    phase="bind",
                    binding=binding,
                    cause=exc,
                ) from exc
            entries.append((binding, scope))
        prepared[point] = tuple(entries)
    return MappingProxyType(prepared)


def load_effect_declarations_for_spec(spec_dir: Path | None):
    """Read the ``effects:`` block from ``actions.yml`` or the manifest.

    ``actions.yml`` wins when it declares effects, because that is where the
    per-action surface lives; the manifest is the fallback home for
    repositories that keep one file. Absence of any declaration is not an
    error -- a program with no declared ports is checked as such, and any
    effect it emits is a gap.
    """
    from effect_conformance import load_effect_declarations as _load

    if spec_dir is None:
        return _load(None)
    for candidate in ("actions.yml", "spec_manifest.yaml"):
        path = spec_dir / candidate
        if not path.exists():
            continue
        data = load_manifest(path)
        if isinstance(data, dict) and data.get("effects"):
            return _load(data)
    return _load(None)


def _execute_points_in_batch(
    *,
    points: list[ExecutionPoint],
    mappings: dict[str, AdapterMapping],
    work_dir: Path,
    import_roots: list[Path],
    declarations: Any = None,
    effect_report_path: Path | None = None,
    effect_provider_plan: EffectProviderPlan | None = None,
    root_seed: int = 0,
    iteration_paths: bool = False,
    replay_command_factory: Callable[[ExecutionPoint], str] | None = None,
) -> None:
    ensure_import_roots(import_roots)
    from spec_double_compiler.runtime import AdapterBatchContext, AdapterCaseContext, call_adapter, instantiate, load_object
    effects_active = declarations is not None and bool(declarations.ports)
    provider_plan = effect_provider_plan or EffectProviderPlan(MappingProxyType({}), configured=False)
    try:
        prepared_provider_scopes = prepare_effect_provider_scopes(
            plan=provider_plan,
            points=points,
            work_dir=work_dir,
            root_seed=root_seed,
            iteration_paths=iteration_paths,
        )
    except _EffectProviderPhaseFailure as exc:
        diagnostic = _structured_failure(
            point=exc.point,
            phase=exc.phase,
            error=exc.cause,
            plan=provider_plan,
            root_seed=root_seed,
            replay_command_factory=replay_command_factory,
            binding=exc.binding,
        )
        raise SystemExit(f"ERROR: semantic effect provider bind failed\n{diagnostic}") from exc
    except EffectProviderConfigurationError as exc:
        raise SystemExit(f"ERROR: invalid semantic effect provider configuration: {exc}") from exc
    recorder = EffectRecorder()
    observed_case_actions: dict[str, str] = {}

    failures: list[str] = []
    adapter_cache: dict[str, Any] = {}
    projector_cache: dict[str, Any] = {}
    object_cache: dict[str, Any] = {}

    runnable_entries: list[tuple[ExecutionPoint, AdapterMapping]] = []
    for point in points:
        case = point.case
        mapping = adapter_for_case(case, mappings)
        if mapping is None:
            if requires_action_adapter(case):
                failures.append(f"{case.name}: no mapped adapter")
            continue
        if not requires_action_adapter(case) and not uses_projected_state_assertion(case, mapping):
            continue
        if mapping.adapter is None:
            if requires_action_adapter(case):
                failures.append(f"{case.name} via {mapping.label}: no executable adapter")
                continue
        runnable_entries.append((point, mapping))

    if provider_plan.configured:
        runnable_groups = [
            (adapter_kind(mapping), [(point, mapping)])
            for point, mapping in runnable_entries
        ]
    else:
        runnable_by_kind: dict[str, list[tuple[ExecutionPoint, AdapterMapping]]] = {}
        for point, mapping in runnable_entries:
            runnable_by_kind.setdefault(adapter_kind(mapping), []).append((point, mapping))
        runnable_groups = list(runnable_by_kind.items())

    for kind, entries in runnable_groups:
        if provider_plan.configured:
            adapter_cache.clear()
            projector_cache.clear()
            object_cache.clear()
        shared: dict[str, Any] = {}
        group_root = work_dir / "kind-work"
        if provider_plan.configured:
            from spec_double_compiler.effects import derive_effect_seed

            point = entries[0][0]
            point_key = derive_effect_seed(
                root_seed,
                str(point.case.name),
                point.iteration,
                "__adapter_batch__",
            )
            group_root = group_root / f"point-{point_key:032x}"
        elif iteration_paths:
            group_root = group_root / f"iteration-{entries[0][0].iteration:06d}"
        group_work_dir = group_root / _opaque_path_component("kind", kind)
        group_work_dir.mkdir(parents=True, exist_ok=True)
        group_cases = [point.case for point, _mapping in entries]
        group_adapters: list[tuple[Any, AdapterMapping]] = []
        initialization_failed = False
        for point, mapping in entries:
            if mapping.adapter is None:
                continue
            adapter = adapter_cache.get(mapping.adapter)
            if adapter is None:
                try:
                    adapter_object = load_object(mapping.adapter)
                except Exception as exc:
                    if not provider_plan.configured:
                        raise
                    failures.append(
                        _structured_failure(
                            point=point,
                            phase="adapter_load",
                            error=exc,
                            plan=provider_plan,
                            root_seed=root_seed,
                            replay_command_factory=replay_command_factory,
                        )
                    )
                    initialization_failed = True
                    continue
                try:
                    adapter = instantiate(adapter_object)
                except Exception as exc:
                    if not provider_plan.configured:
                        raise
                    failures.append(
                        _structured_failure(
                            point=point,
                            phase="adapter_instantiate",
                            error=exc,
                            plan=provider_plan,
                            root_seed=root_seed,
                            replay_command_factory=replay_command_factory,
                        )
                    )
                    initialization_failed = True
                    continue
                adapter_cache[mapping.adapter] = adapter
            if not any(existing_mapping.adapter == mapping.adapter for _adapter, existing_mapping in group_adapters):
                group_adapters.append((adapter, mapping))

        if initialization_failed:
            continue

        setup_all_failed = False
        for adapter, mapping in group_adapters:
            try:
                call_optional_hook(
                    adapter,
                    "setup_all",
                    AdapterBatchContext(
                        kind=kind,
                        cases=group_cases,
                        work_dir=group_work_dir,
                        mapping=mapping,
                        shared=shared,
                        iteration=entries[0][0].iteration,
                        root_seed=root_seed,
                    ),
                )
            except Exception as exc:
                setup_all_failed = True
                failures.append(
                    _structured_failure(
                        point=entries[0][0],
                        phase="setup_all",
                        error=exc,
                        plan=provider_plan,
                        root_seed=root_seed,
                        replay_command_factory=replay_command_factory,
                    )
                    if provider_plan.configured
                    else f"{kind} setup_all via {mapping.label}: {type(exc).__name__}: {exc}"
                )
        try:
            if not setup_all_failed:
                for point, mapping in entries:
                    case = point.case
                    adapter = adapter_cache.get(mapping.adapter) if mapping.adapter is not None else None
                    projector = None
                    if adapter is not None and mapping.output_projection:
                        projector = projector_cache.get(mapping.output_projection)
                        if projector is None:
                            try:
                                projector = load_object(mapping.output_projection)
                            except Exception as exc:
                                if not provider_plan.configured:
                                    raise
                                failures.append(
                                    _structured_failure(
                                        point=point,
                                        phase="output_projection_load",
                                        error=exc,
                                        plan=provider_plan,
                                        root_seed=root_seed,
                                        replay_command_factory=replay_command_factory,
                                    )
                                )
                                continue
                            projector_cache[mapping.output_projection] = projector
                    case_work_dir = _point_work_dir(work_dir, point, iteration_paths=iteration_paths)
                    case_work_dir.mkdir(parents=True, exist_ok=True)
                    sandbox = (
                        EffectSandbox(root=case_work_dir / "sandbox", recorder=recorder)
                        if effects_active
                        else None
                    )
                    if sandbox is not None:
                        # MF-027: assess BEFORE running. `adapter` is the live
                        # Python object the runner is about to call, which is
                        # the only evidence of in-process observability that
                        # counts. When it is absent, or when the binding names
                        # an out-of-process runtime, the refusal is recorded on
                        # the recorder here and no later step can clear it.
                        sandbox.require_observable(
                            mapping.adapter or mapping.label,
                            resolved=adapter,
                            runtime=getattr(mapping, "runtime", None),
                            kind=mapping.kind,
                            channel=mapping.channel,
                        )
                    case_context = AdapterCaseContext(
                        kind=kind,
                        case=case,
                        work_dir=case_work_dir,
                        mapping=mapping,
                        shared=shared,
                        sandbox=sandbox,
                    )
                    observed_case_actions[case.name] = mapping.label
                    # MF-013: the sandbox is entered around the adapter's own
                    # setup/run/teardown. Everything the adapter causes to cross
                    # a boundary in that window is recorded, whether or not the
                    # adapter knows it is being watched.
                    effect_scope = (
                        sandbox.observe(action=mapping.label, case=case.name)
                        if sandbox is not None
                        else _null_context()
                    )
                    sandbox_scope = sandbox if sandbox is not None else _null_context()
                    application_error: Exception | None = None
                    application_phase: str | None = None
                    teardown_error: Exception | None = None
                    escaped_error: Exception | None = None
                    escaped_phase: str | None = None
                    escaped_binding: ResolvedEffectProvider | None = None
                    semantic_mutation_error: Exception | None = None
                    semantic_snapshot = _case_semantic_snapshot(case)
                    provider_exit_tracker = _ProviderExitTracker()
                    try:
                        # Providers are harness setup: acquire them before passive
                        # observation and release them after it. The application
                        # still runs through every installed patch/binding, while
                        # provider allocation and cleanup cannot masquerade as an
                        # application effect. ExitStack supplies strict reverse
                        # cleanup on every failure path.
                        with ExitStack() as provider_stack:
                            bound_effects: dict[str, Any] = {}
                            for binding, provider_scope in prepared_provider_scopes.get(point, ()):
                                try:
                                    value = provider_stack.enter_context(
                                        _NonSuppressingProviderScope(
                                            provider_scope,
                                            provider_exit_tracker,
                                            binding,
                                        )
                                    )
                                    _assert_case_semantics_unchanged(
                                        case,
                                        semantic_snapshot,
                                        stage=f"provider {binding.provider_reference!r} enter",
                                    )
                                except Exception:
                                    escaped_phase = "enter"
                                    escaped_binding = binding
                                    raise
                                if value is not None and not isinstance(value, binding.protocol):
                                    escaped_phase = "invalid_binding"
                                    escaped_binding = binding
                                    raise TypeError(
                                        f"provider {binding.provider_reference!r} binding for {binding.port_name} "
                                        f"does not implement generated port {binding.port_name}"
                                    )
                                bound_effects[binding.port_name] = value
                            case_context.effects = MappingProxyType(bound_effects)

                            with sandbox_scope, effect_scope:
                                try:
                                    if adapter is not None:
                                        active_phase = "setup"
                                        call_optional_hook(adapter, "setup", case_context)
                                        _assert_case_semantics_unchanged(
                                            case,
                                            semantic_snapshot,
                                            stage=f"adapter {mapping.label} setup",
                                        )
                                        active_phase = "run"
                                        case_context.result = call_adapter(adapter, case, case_work_dir)
                                        _assert_case_semantics_unchanged(
                                            case,
                                            semantic_snapshot,
                                            stage=f"adapter {mapping.label} execution",
                                        )
                                        active_phase = "output_assert"
                                        assert_case_result_per_field(
                                            case=case,
                                            result=case_context.result,
                                            projector=projector,
                                        )
                                    active_phase = "projected_assert"
                                    assert_projected_state_if_configured(case_context, mapping, object_cache)
                                    _assert_case_semantics_unchanged(
                                        case,
                                        semantic_snapshot,
                                        stage=f"adapter {mapping.label} assertion",
                                    )
                                except Exception as exc:
                                    application_error = exc
                                    application_phase = active_phase
                                    case_context.error = exc
                                finally:
                                    # Teardown belongs to the active provider and
                                    # passive-observation scopes. This ordering is
                                    # part of the public EP-01 lifecycle contract.
                                    if adapter is not None:
                                        try:
                                            call_optional_hook(adapter, "teardown", case_context)
                                            _assert_case_semantics_unchanged(
                                                case,
                                                semantic_snapshot,
                                                stage=f"adapter {mapping.label} teardown",
                                            )
                                        except Exception as exc:
                                            teardown_error = exc
                                            if case_context.error is None:
                                                case_context.error = exc
                            if application_error is not None:
                                raise application_error
                            if teardown_error is not None:
                                raise teardown_error
                    except Exception as exc:
                        escaped_error = exc
                        if escaped_phase is None:
                            escaped_phase = application_phase or ("teardown" if teardown_error is not None else None)
                    try:
                        _assert_case_semantics_unchanged(
                            case,
                            semantic_snapshot,
                            stage="semantic provider lifecycle",
                        )
                    except Exception as exc:
                        semantic_mutation_error = exc
                        if escaped_error is None:
                            escaped_error = exc

                    # Provider truthy __exit__ values are ignored by the
                    # wrapper above. Classify the retained primary and every
                    # cleanup exception independently so no failure can replace
                    # or hide another during reverse-order unwinding.
                    reported_errors: list[Exception] = []
                    if application_error is not None:
                        if provider_plan.configured:
                            failures.append(
                                _structured_failure(
                                    point=point,
                                    phase=application_phase or "run",
                                    error=application_error,
                                    plan=provider_plan,
                                    root_seed=root_seed,
                                    replay_command_factory=replay_command_factory,
                                )
                            )
                        else:
                            failures.append(
                                f"{case.name} via {mapping.label}: "
                                f"{type(application_error).__name__}: {application_error}"
                            )
                        reported_errors.append(application_error)
                    if teardown_error is not None:
                        if provider_plan.configured:
                            failures.append(
                                _structured_failure(
                                    point=point,
                                    phase="teardown",
                                    error=teardown_error,
                                    plan=provider_plan,
                                    root_seed=root_seed,
                                    replay_command_factory=replay_command_factory,
                                )
                            )
                        else:
                            failures.append(
                                f"{case.name} teardown via {mapping.label}: "
                                f"{type(teardown_error).__name__}: {teardown_error}"
                            )
                        reported_errors.append(teardown_error)

                    lifecycle_error = provider_exit_tracker.primary_error
                    if lifecycle_error is None and escaped_error is not None:
                        escaped_is_cleanup = any(
                            escaped_error is cleanup_error
                            for _binding, cleanup_error in provider_exit_tracker.cleanup_errors
                        )
                        if not escaped_is_cleanup:
                            lifecycle_error = escaped_error
                    if lifecycle_error is not None and not any(
                        lifecycle_error is reported_error for reported_error in reported_errors
                    ):
                        case_context.error = lifecycle_error
                        if provider_plan.configured:
                            failures.append(
                                _structured_failure(
                                    point=point,
                                    phase=escaped_phase or "provider_lifecycle",
                                    error=lifecycle_error,
                                    plan=provider_plan,
                                    root_seed=root_seed,
                                    replay_command_factory=replay_command_factory,
                                    binding=escaped_binding,
                                )
                            )
                        else:
                            failures.append(
                                f"{case.name} provider lifecycle via {mapping.label}: "
                                f"{type(lifecycle_error).__name__}: {lifecycle_error}"
                            )
                        reported_errors.append(lifecycle_error)

                    for cleanup_binding, cleanup_error in provider_exit_tracker.cleanup_errors:
                        failures.append(
                            _structured_failure(
                                point=point,
                                phase="exit",
                                error=cleanup_error,
                                plan=provider_plan,
                                root_seed=root_seed,
                                replay_command_factory=replay_command_factory,
                                binding=cleanup_binding,
                            )
                            if provider_plan.configured
                            else (
                                f"{case.name} provider cleanup via {mapping.label}: "
                                f"{type(cleanup_error).__name__}: {cleanup_error}"
                            )
                        )
                        reported_errors.append(cleanup_error)
                    if semantic_mutation_error is not None and not any(
                        semantic_mutation_error is reported_error for reported_error in reported_errors
                    ):
                        failures.append(
                            _structured_failure(
                                point=point,
                                phase="oracle_integrity",
                                error=semantic_mutation_error,
                                plan=provider_plan,
                                root_seed=root_seed,
                                replay_command_factory=replay_command_factory,
                            )
                            if provider_plan.configured
                            else (
                                f"{case.name} semantic oracle integrity via {mapping.label}: "
                                f"{type(semantic_mutation_error).__name__}: {semantic_mutation_error}"
                            )
                        )
        finally:
            for adapter, mapping in reversed(group_adapters):
                try:
                    call_optional_hook(
                        adapter,
                        "teardown_all",
                        AdapterBatchContext(
                            kind=kind,
                            cases=group_cases,
                            work_dir=group_work_dir,
                            mapping=mapping,
                            shared=shared,
                            iteration=entries[0][0].iteration,
                            root_seed=root_seed,
                        ),
                    )
                except Exception as exc:
                    failures.append(
                        _structured_failure(
                            point=entries[0][0],
                            phase="teardown_all",
                            error=exc,
                            plan=provider_plan,
                            root_seed=root_seed,
                            replay_command_factory=replay_command_factory,
                        )
                        if provider_plan.configured
                        else f"{kind} teardown_all via {mapping.label}: {type(exc).__name__}: {exc}"
                    )

    # MF-013: effect conformance. The report is written unconditionally -- it is
    # ticket evidence whether the verdict is clean or not -- and every finding
    # is appended to `failures`, so a gap or a dead port fails the run exactly
    # like a broken assertion. Nothing between here and the raise consults a
    # justification, an annotation, or a manifest entry: recording a finding is
    # not an alternative to failing on it.
    if effects_active:
        report = diff_effects(
            declarations,
            recorder.effects,
            cases=[point.case.name for point in points],
            case_actions=observed_case_actions,
            unobservable=recorder.unobservable,
        )
        if effect_report_path is not None:
            written = report.write(effect_report_path)
            print(f"wrote effect conformance report to {written}")
        print(report.render())
        if not report.ok:
            failures.append(f"effect conformance {report.verdict}:\n{report.render()}")

    if failures:
        details = "\n".join(failures[:50])
        suffix = f"\n... and {len(failures) - 50} more" if len(failures) > 50 else ""
        raise SystemExit(f"ERROR: {len(failures)} batched case executions failed\n{details}{suffix}")


def execute_cases_in_batch(
    *,
    cases: list[Any],
    mappings: dict[str, AdapterMapping],
    work_dir: Path,
    import_roots: list[Path],
    declarations: Any = None,
    effect_report_path: Path | None = None,
    effect_provider_plan: EffectProviderPlan | None = None,
    fuzz_runs: int = 1,
    root_seed: int = 0,
    fuzz_iteration: int | None = None,
    replay_command_factory: Callable[[ExecutionPoint], str] | None = None,
) -> int:
    """Run a deterministic provider campaign with replayable point isolation.

    Provider-free defaults retain the legacy grouped batch lifecycle and work
    layout. Provider-bearing runs isolate every case/iteration point in its own
    batch so ``setup_all`` and ``teardown_all`` receive exactly the context an
    emitted replay command reconstructs. Each such point gets fresh adapter and
    shared caches, provider bindings, effect mappings, and sandboxes. Any
    nondefault fuzz control also selects an iteration-qualified work path.
    """

    if fuzz_runs < 1:
        raise SystemExit("ERROR: --fuzz-runs must be at least 1")
    if fuzz_iteration is not None and fuzz_iteration < 0:
        raise SystemExit("ERROR: --fuzz-iteration must be non-negative")

    provider_plan = effect_provider_plan or EffectProviderPlan(
        MappingProxyType({}),
        configured=False,
    )
    fuzz_requested = fuzz_runs != 1 or root_seed != 0 or fuzz_iteration is not None
    if fuzz_requested and not provider_plan.configured:
        raise SystemExit(
            "ERROR: effect fuzz controls require at least one [effect_providers.<Port>] mapping"
        )

    iterations = [fuzz_iteration] if fuzz_iteration is not None else list(range(fuzz_runs))
    iteration_paths = fuzz_requested
    for iteration in iterations:
        assert iteration is not None
        points = [ExecutionPoint(case=case, iteration=iteration) for case in cases]
        _execute_points_in_batch(
            points=points,
            mappings=mappings,
            work_dir=work_dir,
            import_roots=import_roots,
            declarations=declarations,
            effect_report_path=effect_report_path,
            effect_provider_plan=provider_plan,
            root_seed=root_seed,
            iteration_paths=iteration_paths,
            replay_command_factory=replay_command_factory,
        )
    return len(cases) * len(iterations)


def reexec_batch_if_needed(args: argparse.Namespace) -> int | None:
    if not args.batch or not args.python or os.environ.get("SPEC_DOUBLE_BATCH_REEXEC") == "1":
        return None
    command = [*args.python, str(Path(__file__).resolve()), str(args.cases_dir), "--mapping", str(args.mapping), "--batch"]
    if args.spec_dir is not None:
        command.extend(["--spec-dir", str(args.spec_dir)])
    if args.work_dir is not None:
        command.extend(["--work-dir", str(args.work_dir)])
    if args.view is not None:
        command.extend(["--view", args.view])
    for label in args.label:
        command.extend(["--label", label])
    for case_name in args.case:
        command.extend(["--case", case_name])
    if args.limit is not None:
        command.extend(["--limit", str(args.limit)])
    for root in args.import_root:
        command.extend(["--import-root", str(root)])
    if args.validate_only:
        command.append("--validate-only")
    if args.validate_capabilities:
        command.append("--validate-capabilities")
    if args.effect_report is not None:
        command.extend(["--effect-report", str(args.effect_report)])
    command.extend(["--fuzz-runs", str(args.fuzz_runs), "--seed", str(args.seed)])
    if args.fuzz_iteration is not None:
        command.extend(["--fuzz-iteration", str(args.fuzz_iteration)])
    env = os.environ.copy()
    env["SPEC_DOUBLE_BATCH_REEXEC"] = "1"
    return subprocess.run(command, env=env).returncode


def build_replay_command(
    *,
    args: argparse.Namespace,
    spec_dir: Path | None,
    import_roots: list[Path],
    point: ExecutionPoint,
) -> str:
    """Return an absolute, shell-safe command for exactly one failed point."""

    command = [
        str(Path(sys.executable).resolve()),
        str(Path(__file__).resolve()),
        str(args.cases_dir.resolve()),
        "--mapping",
        str(args.mapping.resolve()),
        "--batch",
        "--seed",
        str(args.seed),
        "--fuzz-runs",
        "1",
        "--fuzz-iteration",
        str(point.iteration),
        "--case",
        str(point.case.name),
    ]
    if spec_dir is not None:
        command.extend(["--spec-dir", str(spec_dir.resolve())])
    if args.view is not None:
        command.extend(["--view", args.view])
    for root in import_roots:
        command.extend(["--import-root", str(root.resolve())])
    return shlex.join(command)


def execute_programs(programs: list[Path], python: list[str]) -> None:
    failures: list[tuple[Path, int]] = []
    for program in programs:
        result = subprocess.run([*python, str(program)])
        if result.returncode != 0:
            failures.append((program, result.returncode))
    if failures:
        details = "\n".join(f"{path}: exit {code}" for path, code in failures)
        raise SystemExit(f"ERROR: {len(failures)} generated case programs failed\n{details}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cases_dir", type=Path, help="Generated case package directory")
    parser.add_argument("--mapping", type=Path, required=True, help="TOML label-to-adapter mapping")
    parser.add_argument("--spec-dir", type=Path, help="Spec directory used for resolving spec-relative paths")
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--view", choices=["internal", "external"], help="Only validate/run cases for this generated view")
    parser.add_argument("--label", action="append", default=[], help="Only generate/run cases with this label")
    parser.add_argument("--case", action="append", default=[], help="Only generate/run this case name")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--import-root", action="append", type=Path, default=[])
    parser.add_argument("--python", action="append", default=[], help="Python command used to run generated programs")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--validate-capabilities", action="store_true", help="Ask adapters whether they can run every selected case")
    parser.add_argument("--batch", action="store_true", help="Execute selected cases in this process instead of one generated program per case")
    parser.add_argument(
        "--effect-report",
        type=Path,
        help="Write the MF-013 effect conformance diff report (JSON) to this path.",
    )
    parser.add_argument(
        "--fuzz-runs",
        type=int,
        default=1,
        help="Run each selected case this many deterministic effect-provider iterations.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Root seed used to derive stable per-case, per-iteration, per-port seeds.",
    )
    parser.add_argument(
        "--fuzz-iteration",
        type=int,
        help="Run exactly this iteration (the replay selector; --fuzz-runs is ignored).",
    )
    args = parser.parse_args()

    spec_dir = infer_spec_dir(args.cases_dir, args.mapping, args.spec_dir)
    args.cases_dir = resolve_runtime_path(args.cases_dir, spec_dir)
    args.mapping = resolve_runtime_path(args.mapping, spec_dir)
    args.import_root = [resolve_runtime_path(root, spec_dir) for root in args.import_root]
    default_import_roots = args.import_root or ([Path.cwd(), spec_dir] if spec_dir is not None else [Path.cwd()])
    if args.work_dir is not None and spec_dir is not None:
        args.work_dir = resolve_spec_relative_path(args.work_dir, spec_dir)

    reexec_code = reexec_batch_if_needed(args)
    if reexec_code is not None:
        return reexec_code

    cases_module = load_cases(args.cases_dir)
    cases = list(cases_module.CASES)
    mappings = load_mappings(args.mapping)
    coverage_cases = selected_cases(cases, [], [], None, args.view)
    validate_mapping_coverage(coverage_cases, mappings)
    # MF-015: external bindings must declare a channel, must not import the
    # production package, and must name their port binding configuration.
    try:
        enforce_external_channels(coverage_cases, mappings, args.mapping, default_import_roots)
    except ChannelEnforcementError as exc:
        raise SystemExit(str(exc))
    runnable_cases = selected_cases(cases, args.label, args.case, args.limit, args.view)
    if not runnable_cases:
        raise SystemExit("ERROR: no cases selected")
    try:
        effect_provider_plan = load_effect_provider_plan(
            spec_dir=spec_dir,
            mapping_path=args.mapping,
            cases=coverage_cases,
            import_roots=default_import_roots,
        )
    except EffectProviderConfigurationError as exc:
        raise SystemExit(f"ERROR: invalid semantic effect provider configuration: {exc}") from exc
    validate_effect_provider_execution_mode(
        effect_provider_plan,
        batch=args.batch,
        validate_only=args.validate_only,
    )
    if args.fuzz_runs < 1:
        raise SystemExit("ERROR: --fuzz-runs must be at least 1")
    if args.fuzz_iteration is not None and args.fuzz_iteration < 0:
        raise SystemExit("ERROR: --fuzz-iteration must be non-negative")
    fuzz_requested = args.fuzz_runs != 1 or args.seed != 0 or args.fuzz_iteration is not None
    if fuzz_requested and not effect_provider_plan.configured:
        raise SystemExit(
            "ERROR: effect fuzz controls require at least one [effect_providers.<Port>] mapping"
        )
    if args.validate_capabilities:
        validate_adapter_capabilities(
            cases=runnable_cases,
            mappings=mappings,
            import_roots=default_import_roots,
        )

    work_dir = args.work_dir or Path(tempfile.mkdtemp(prefix="spec-double-cases-"))
    work_dir.mkdir(parents=True, exist_ok=True)
    print(f"validated {len(mappings)} adapter mappings for {len(case_labels(cases))} labels")
    if args.batch:
        if not args.validate_only:
            try:
                declarations = load_effect_declarations_for_spec(spec_dir)
            except EffectDeclarationError as exc:
                raise SystemExit(f"ERROR: malformed effect declarations: {exc}")
            executed_points = execute_cases_in_batch(
                cases=runnable_cases,
                mappings=mappings,
                work_dir=work_dir,
                import_roots=default_import_roots,
                declarations=declarations,
                effect_report_path=args.effect_report,
                effect_provider_plan=effect_provider_plan,
                fuzz_runs=args.fuzz_runs,
                root_seed=args.seed,
                fuzz_iteration=args.fuzz_iteration,
                replay_command_factory=lambda point: build_replay_command(
                    args=args,
                    spec_dir=spec_dir,
                    import_roots=default_import_roots,
                    point=point,
                ),
            )
            if args.fuzz_runs == 1 and args.fuzz_iteration is None:
                print(f"executed {len(runnable_cases)} cases in batch")
            else:
                print(f"executed {executed_points} effect-fuzz execution points")
    else:
        programs = generate_programs(
            cases=runnable_cases,
            mappings=mappings,
            cases_dir=args.cases_dir,
            work_dir=work_dir,
            import_roots=default_import_roots,
        )
        print(f"generated {len(programs)} case programs in {work_dir / 'programs'}")
    if not args.validate_only and not args.batch:
        execute_programs(programs, args.python or [sys.executable])
        print(f"executed {len(programs)} case programs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
