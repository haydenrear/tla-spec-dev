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
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None  # type: ignore


@dataclass(frozen=True)
class AdapterMapping:
    label: str
    adapter: str


def load_cases(cases_dir: Path):
    cases_dir = cases_dir.resolve()
    sys.path.insert(0, str(cases_dir.parent))
    return importlib.import_module(cases_dir.name)


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
            mappings[str(label)] = AdapterMapping(label=str(label), adapter=adapter)

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
                mappings[label] = AdapterMapping(label=label, adapter=adapter)

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
    labels = case_labels(cases)
    missing = sorted(labels - set(mappings))
    if missing:
        raise SystemExit(
            "ERROR: missing adapter mappings for labels: "
            + ", ".join(missing)
            + "\nAdd entries such as [adapters.LabelName] adapter = \"module:Adapter\"."
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


def adapter_for_case(case: Any, mappings: dict[str, AdapterMapping]) -> AdapterMapping:
    for label in sorted(str(label) for label in case.labels):
        if label in mappings:
            return mappings[label]
    raise AssertionError(f"no adapter mapping for case {case.name}: {sorted(case.labels)}")


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
    root_inserts = "\n".join(f"sys.path.insert(0, {str(root.resolve())!r})" for root in import_roots)
    content = f"""#!/usr/bin/env python3
from __future__ import annotations

import importlib
import sys
from pathlib import Path

sys.path.insert(0, {str(cases_dir.resolve().parent)!r})
{root_inserts}

from {cases_dir.name}.cases import CASES_BY_NAME
from {cases_dir.name}.validators import assert_case_replays


def load_object(path: str):
    module_name, sep, object_name = path.partition(":")
    if not sep:
        raise ValueError(f"adapter path must be module:object, got {{path!r}}")
    module = importlib.import_module(module_name)
    obj = module
    for part in object_name.split("."):
        obj = getattr(obj, part)
    return obj


def instantiate(obj):
    if isinstance(obj, type):
        return obj()
    if callable(obj) and not hasattr(obj, "run"):
        return obj()
    return obj


def normalize_result(result):
    if result is None:
        return {{"output": None, "after": None}}
    if isinstance(result, dict):
        return result
    output = getattr(result, "output", None)
    after = getattr(result, "after", None)
    return {{"output": output, "after": after}}


def call_adapter(adapter, case, work_dir: Path):
    validate = getattr(adapter, "validate", None)
    if validate is not None:
        validate(case)
    run = getattr(adapter, "run", None)
    if run is None:
        raise TypeError(f"adapter {{adapter!r}} does not define run(case, ...)")
    try:
        return run(case, work_dir=work_dir)
    except TypeError as exc:
        if "work_dir" not in str(exc):
            raise
        return run(case)


def main() -> int:
    case = CASES_BY_NAME[{case.name!r}]
    assert_case_replays(case)
    adapter = instantiate(load_object({mapping.adapter!r}))
    normalized = normalize_result(call_adapter(adapter, case, Path({str(case_work_dir.resolve())!r})))
    output = normalized.get("output")
    after = normalized.get("after")
    if output is not None and output != case.output:
        raise AssertionError(f"adapter output mismatch for {{case.name}}: {{output!r}} != {{case.output!r}}")
    if after is not None and after != case.after:
        raise AssertionError(f"adapter after-state mismatch for {{case.name}}")
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
    parser.add_argument("--work-dir", type=Path)
    parser.add_argument("--label", action="append", default=[], help="Only generate/run cases with this label")
    parser.add_argument("--case", action="append", default=[], help="Only generate/run this case name")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--import-root", action="append", type=Path, default=[])
    parser.add_argument("--python", action="append", default=[], help="Python command used to run generated programs")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    cases_module = load_cases(args.cases_dir)
    cases = list(cases_module.CASES)
    mappings = load_mappings(args.mapping)
    validate_mapping_coverage(cases, mappings)
    runnable_cases = selected_cases(cases, args.label, args.case, args.limit)
    if not runnable_cases:
        raise SystemExit("ERROR: no cases selected")

    work_dir = args.work_dir or Path(tempfile.mkdtemp(prefix="spec-double-cases-"))
    work_dir.mkdir(parents=True, exist_ok=True)
    programs = generate_programs(
        cases=runnable_cases,
        mappings=mappings,
        cases_dir=args.cases_dir,
        work_dir=work_dir,
        import_roots=args.import_root or [Path.cwd()],
    )
    print(f"validated {len(mappings)} adapter mappings for {len(case_labels(cases))} labels")
    print(f"generated {len(programs)} case programs in {work_dir / 'programs'}")
    if not args.validate_only:
        execute_programs(programs, args.python or [sys.executable])
        print(f"executed {len(programs)} case programs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
