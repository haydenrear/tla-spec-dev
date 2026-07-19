#!/usr/bin/env python3
"""Generate and run adapter programs for TLC-derived cases.

The generated cases stay generic. A repository supplies a TOML file mapping
case labels, usually TLA action names, to adapter import paths. This script
validates coverage, writes one executable Python program per selected case into
a work directory, and optionally executes those programs.
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from .effect_conformance import (
        EffectDeclarationError,
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
            current = {}
            adapters[label] = current
            continue
        if line.startswith("[actions.") and line.endswith("]"):
            label = line[len("[actions.") : -1]
            actions = loaded.setdefault("actions", {})
            current = {}
            actions[label] = current
            continue
        if "=" not in line or current is None:
            raise ValueError(f"unsupported TOML line: {raw_line!r}")
        key, raw_value = line.split("=", 1)
        current[key.strip()] = parse_simple_toml_value(raw_value.strip())
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


def assert_projected_state(assertion_context: Any, mapping: AdapterMapping, object_cache: dict[str, Any]) -> None:
    if mapping.assertion is None:
        if assertion_context.actual != assertion_context.expected:
            raise AssertionError(
                f"projected state mismatch for {assertion_context.case.name}: "
                f"{assertion_context.actual!r} != {assertion_context.expected!r}"
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
from scripts.run_generated_case_adapters import AdapterMapping, adapter_kind, assert_projected_state_if_configured
from spec_double_compiler.runtime import AdapterCaseContext, assert_case_result, call_adapter, instantiate, load_object


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
    assert_case_result(
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
        program_path = work_dir / "programs" / f"{case.name}.py"
        case_work_dir = work_dir / "case-work" / case.name
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


def execute_cases_in_batch(
    *,
    cases: list[Any],
    mappings: dict[str, AdapterMapping],
    work_dir: Path,
    import_roots: list[Path],
    declarations: Any = None,
    effect_report_path: Path | None = None,
) -> None:
    ensure_import_roots(import_roots)
    from spec_double_compiler.runtime import AdapterBatchContext, AdapterCaseContext, assert_case_result, call_adapter, instantiate, load_object
    from effect_conformance import EffectRecorder, EffectSandbox

    effects_active = declarations is not None and bool(declarations.ports)
    recorder = EffectRecorder()
    observed_case_actions: dict[str, str] = {}

    failures: list[str] = []
    adapter_cache: dict[str, Any] = {}
    projector_cache: dict[str, Any] = {}
    object_cache: dict[str, Any] = {}

    runnable_by_kind: dict[str, list[tuple[Any, AdapterMapping]]] = {}
    for case in cases:
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
        runnable_by_kind.setdefault(adapter_kind(mapping), []).append((case, mapping))

    for kind, entries in runnable_by_kind.items():
        shared: dict[str, Any] = {}
        group_work_dir = work_dir / "kind-work" / kind.replace("/", "_").replace(":", "_")
        group_work_dir.mkdir(parents=True, exist_ok=True)
        group_cases = [case for case, _mapping in entries]
        group_adapters: list[tuple[Any, AdapterMapping]] = []
        for _case, mapping in entries:
            if mapping.adapter is None:
                continue
            adapter = adapter_cache.get(mapping.adapter)
            if adapter is None:
                adapter = instantiate(load_object(mapping.adapter))
                adapter_cache[mapping.adapter] = adapter
            if not any(existing_mapping.adapter == mapping.adapter for _adapter, existing_mapping in group_adapters):
                group_adapters.append((adapter, mapping))

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
                    ),
                )
            except Exception as exc:
                setup_all_failed = True
                failures.append(f"{kind} setup_all via {mapping.label}: {type(exc).__name__}: {exc}")
        try:
            if not setup_all_failed:
                for case, mapping in entries:
                    adapter = adapter_cache.get(mapping.adapter) if mapping.adapter is not None else None
                    projector = None
                    if adapter is not None and mapping.output_projection:
                        projector = projector_cache.get(mapping.output_projection)
                        if projector is None:
                            projector = load_object(mapping.output_projection)
                            projector_cache[mapping.output_projection] = projector
                    case_work_dir = work_dir / "case-work" / case.name
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
                    try:
                        with sandbox_scope, effect_scope:
                            if adapter is not None:
                                call_optional_hook(adapter, "setup", case_context)
                                case_context.result = call_adapter(adapter, case, case_work_dir)
                                assert_case_result(
                                    case=case,
                                    result=case_context.result,
                                    projector=projector,
                                )
                            assert_projected_state_if_configured(case_context, mapping, object_cache)
                    except Exception as exc:
                        case_context.error = exc
                        failures.append(f"{case.name} via {mapping.label}: {type(exc).__name__}: {exc}")
                    finally:
                        if adapter is not None:
                            try:
                                call_optional_hook(adapter, "teardown", case_context)
                            except Exception as exc:
                                failures.append(f"{case.name} teardown via {mapping.label}: {type(exc).__name__}: {exc}")
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
                        ),
                    )
                except Exception as exc:
                    failures.append(f"{kind} teardown_all via {mapping.label}: {type(exc).__name__}: {exc}")

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
            cases=[case.name for case in cases],
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


def reexec_batch_if_needed(args: argparse.Namespace) -> int | None:
    if not args.batch or not args.python or os.environ.get("SPEC_DOUBLE_BATCH_REEXEC") == "1":
        return None
    command = [*args.python, str(Path(__file__).resolve()), str(args.cases_dir), "--mapping", str(args.mapping), "--batch"]
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
    env = os.environ.copy()
    env["SPEC_DOUBLE_BATCH_REEXEC"] = "1"
    return subprocess.run(command, env=env).returncode


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
            execute_cases_in_batch(
                cases=runnable_cases,
                mappings=mappings,
                work_dir=work_dir,
                import_roots=default_import_roots,
                declarations=declarations,
                effect_report_path=args.effect_report,
            )
            print(f"executed {len(runnable_cases)} cases in batch")
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
