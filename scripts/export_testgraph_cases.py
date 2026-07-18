#!/usr/bin/env python3
"""Export external generated cases as Test Graph trace JSON files."""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path
from typing import Any

try:
    from .corpus_diagnostics import enforce_case_cap
    from .generate_cases_from_tlc_dump import TRACE_SCHEMA_VERSION
    from .run_generated_case_adapters import (
        case_controllability,
        case_view,
        load_cases,
        selected_cases,
    )
    from .spec_paths import resolve_existing_from_cwd
except ImportError:  # pragma: no cover - direct script execution
    from corpus_diagnostics import enforce_case_cap
    from generate_cases_from_tlc_dump import TRACE_SCHEMA_VERSION
    from run_generated_case_adapters import case_controllability, case_view, load_cases, selected_cases
    from spec_paths import resolve_existing_from_cwd


def to_jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: to_jsonable(getattr(value, field.name))
            for field in dataclasses.fields(value)
        }
    if isinstance(value, dict):
        return {str(key): to_jsonable(inner) for key, inner in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (set, frozenset)):
        return [to_jsonable(inner) for inner in sorted(value, key=repr)]
    if isinstance(value, tuple):
        return [to_jsonable(inner) for inner in value]
    return value


def case_to_trace(case: Any, module: str | None = None) -> dict[str, Any]:
    if case_view(case) != "external":
        raise ValueError(f"case {case.name} is {case_view(case)!r}, not external")
    if case_controllability(case) == "hidden":
        raise ValueError(f"case {case.name} is hidden and must not be exported as a Test Graph step")

    step = {
        "index": 1,
        "action": case.input.action,
        "layer": getattr(case, "layer", "external"),
        "controllability": case_controllability(case),
        "params": to_jsonable(getattr(case.input, "params", {})),
        "pre": to_jsonable(case.before),
        "post": to_jsonable(case.after),
        "expected_response": to_jsonable(case.output),
        "raw": {
            "source_node": case.input.source_node,
            "target_node": case.input.target_node,
            "labels": sorted(str(label) for label in case.labels),
        },
    }
    return {
        "schema_version": getattr(case, "schema_version", TRACE_SCHEMA_VERSION),
        "view": "external",
        "trace_id": case.name,
        "source": {
            "module": module,
            "case": case.name,
        },
        "steps": [step],
    }


def export_cases(cases: list[Any], out_dir: Path, module: str | None = None) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for case in cases:
        trace = case_to_trace(case, module)
        path = out_dir / f"{case.name}.json"
        path.write_text(json.dumps(trace, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(path)
    manifest = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "view": "external",
        "trace_count": len(written),
        "traces": [path.name for path in written],
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    written.append(out_dir / "manifest.json")
    return written


def default_manifest_for(cases_dir: Path) -> Path | None:
    """Find the spec_manifest.yaml governing a generated case package.

    Packages land at ``<spec-dir>/generated/<view-dir>/<package>``, so walk up
    looking for the manifest rather than guessing a fixed depth.
    """
    for parent in [cases_dir, *cases_dir.parents]:
        candidate = parent / "spec_manifest.yaml"
        if candidate.is_file():
            return candidate
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cases_dir", type=Path, help="Generated external case package directory")
    parser.add_argument("--out", type=Path, required=True, help="Directory for Test Graph trace JSON files")
    parser.add_argument("--label", action="append", default=[], help="Only export cases with this label")
    parser.add_argument("--case", action="append", default=[], help="Only export this case name")
    parser.add_argument(
        "--limit",
        type=int,
        help=(
            "Limit how many selected cases are exported in THIS run. This is a "
            "user-driven selection for a focused run, not a budget mechanism: "
            "the case-cap gate below measures the full corpus before any "
            "selection applies, so --limit/--label can never bring a corpus "
            "under cap."
        ),
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="spec_manifest.yaml supplying the case caps. Defaults to the spec dir beside the case package.",
    )
    args = parser.parse_args()

    cases_dir = resolve_existing_from_cwd(args.cases_dir)
    sys.path.insert(0, str(cases_dir.parent))
    cases_module = load_cases(cases_dir)

    # Case-cap hard gate (MF-014), measured over the COMPLETE external corpus
    # and deliberately BEFORE --label/--case/--limit selection. Gating after
    # selection would let a narrow flag silently satisfy a budget, which is
    # exactly the trimming this ticket forbids.
    all_external = [case for case in cases_module.CASES if case_view(case) == "external"]
    enforce_case_cap(
        all_external,
        view="external",
        manifest_path=args.manifest or default_manifest_for(cases_dir),
        source=str(cases_dir),
    )

    cases = selected_cases(list(cases_module.CASES), args.label, args.case, args.limit, "external")
    if not cases:
        raise SystemExit("ERROR: no external cases selected")
    written = export_cases(cases, args.out, getattr(cases_module, "SOURCE_MODULE", None))
    print(f"exported {len(written) - 1} Test Graph traces into {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
