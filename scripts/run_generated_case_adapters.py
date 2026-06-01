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
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from .spec_paths import resolve_existing_from_cwd, resolve_existing_spec_input, resolve_spec_relative_path
except ImportError:  # pragma: no cover - direct script execution
    from spec_paths import resolve_existing_from_cwd, resolve_existing_spec_input, resolve_spec_relative_path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore


@dataclass(frozen=True)
class AdapterMapping:
    label: str
    adapter: str
    output_projection: str | None = None
    order: int = 0


def load_cases(cases_dir: Path):
    cases_dir = cases_dir.resolve()
    sys.path.insert(0, str(cases_dir.parent))
    return importlib.import_module(cases_dir.name)


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
    loaded = load_toml(path)
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
            mappings[str(label)] = AdapterMapping(
                label=str(label),
                adapter=adapter,
                output_projection=projection,
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
                    order=len(mappings),
                )

    if not mappings:
        raise ValueError(f"no adapter mappings found in {path}")
    return mappings


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


def validate_mapping_coverage(cases: list[Any], mappings: dict[str, AdapterMapping]) -> None:
    uncovered = [case.name for case in cases if adapter_for_case(case, mappings) is None]
    if uncovered:
        raise SystemExit(
            "ERROR: missing adapter mappings for cases: "
            + ", ".join(uncovered[:20])
            + (f" ... and {len(uncovered) - 20} more" if len(uncovered) > 20 else "")
            + "\nAdd entries such as [adapters.LabelName] adapter = \"module:Adapter\" for at least one label on each case."
        )


def selected_cases(cases: list[Any], labels: list[str], names: list[str], limit: int | None) -> list[Any]:
    selected = cases
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


def load_adapter(mapping: AdapterMapping, import_roots: list[Path]):
    ensure_import_roots(import_roots)
    from spec_double_compiler.runtime import instantiate, load_object

    return instantiate(load_object(mapping.adapter))


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
            rejected.append(f"{case.name}: no mapped label among {sorted(case.labels)}")
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
from spec_double_compiler.runtime import assert_case_result, call_adapter, instantiate, load_object


def main() -> int:
    case = CASES_BY_NAME[{case.name!r}]
    assert_case_replays(case)
    adapter = instantiate(load_object({mapping.adapter!r}))
    projector = None
    if {mapping.output_projection!r} is not None:
        projector = load_object({mapping.output_projection!r})
    assert_case_result(
        case=case,
        result=call_adapter(adapter, case, Path({str(case_work_dir.resolve())!r})),
        projector=projector,
    )
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


def execute_cases_in_batch(
    *,
    cases: list[Any],
    mappings: dict[str, AdapterMapping],
    work_dir: Path,
    import_roots: list[Path],
) -> None:
    ensure_import_roots(import_roots)
    from spec_double_compiler.runtime import assert_case_result, call_adapter, instantiate, load_object

    failures: list[str] = []
    adapter_cache: dict[str, Any] = {}
    projector_cache: dict[str, Any] = {}
    for case in cases:
        mapping = adapter_for_case(case, mappings)
        if mapping is None:
            failures.append(f"{case.name}: no mapped adapter")
            continue
        try:
            adapter = adapter_cache.get(mapping.adapter)
            if adapter is None:
                adapter = instantiate(load_object(mapping.adapter))
                adapter_cache[mapping.adapter] = adapter
            projector = None
            if mapping.output_projection:
                projector = projector_cache.get(mapping.output_projection)
                if projector is None:
                    projector = load_object(mapping.output_projection)
                    projector_cache[mapping.output_projection] = projector
            case_work_dir = work_dir / "case-work" / case.name
            case_work_dir.mkdir(parents=True, exist_ok=True)
            assert_case_result(
                case=case,
                result=call_adapter(adapter, case, case_work_dir),
                projector=projector,
            )
        except Exception as exc:
            failures.append(f"{case.name} via {mapping.label}: {type(exc).__name__}: {exc}")
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
    parser.add_argument("--label", action="append", default=[], help="Only generate/run cases with this label")
    parser.add_argument("--case", action="append", default=[], help="Only generate/run this case name")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--import-root", action="append", type=Path, default=[])
    parser.add_argument("--python", action="append", default=[], help="Python command used to run generated programs")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--validate-capabilities", action="store_true", help="Ask adapters whether they can run every selected case")
    parser.add_argument("--batch", action="store_true", help="Execute selected cases in this process instead of one generated program per case")
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
    validate_mapping_coverage(cases, mappings)
    runnable_cases = selected_cases(cases, args.label, args.case, args.limit)
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
            execute_cases_in_batch(
                cases=runnable_cases,
                mappings=mappings,
                work_dir=work_dir,
                import_roots=default_import_roots,
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
