#!/usr/bin/env python3
"""Write the exact retrieval/authoring-cost ledger for this implementation."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUTHORING_STARTED = datetime.fromisoformat("2026-07-22T00:46:34+00:00")

READ_LEDGER: list[dict[str, Any]] = [
    {"path": "/Users/hayde/.skill-manager/skills/spec-double-compiler/SKILL.md", "ranges": "1-842", "lines": 842},
    {"path": "/Users/hayde/.skill-manager/skills/test-graph/SKILL.md", "ranges": "1-133", "lines": 133},
    {"path": "/Users/hayde/.codex/skills/python-skill/SKILL.md", "ranges": "1-8", "lines": 8},
    {"path": "/Users/hayde/.skill-manager/skills/debugging/SKILL.md", "ranges": "1-281", "lines": 281},
    {"path": "/Users/hayde/.skill-manager/skills/spec-double-compiler/references/testgraph_adapters.md", "ranges": "1-209", "lines": 209},
    {"path": "/Users/hayde/.skill-manager/skills/spec-double-compiler/references/edge-cases.md", "ranges": "1-124", "lines": 124},
    {"path": "/Users/hayde/.skill-manager/skills/spec-double-compiler/references/tla_profile.md", "ranges": "1-122", "lines": 122},
    {"path": "/Users/hayde/.skill-manager/skills/spec-double-compiler/references/generation_modes.md", "ranges": "1-93", "lines": 93},
    {"path": "/Users/hayde/.skill-manager/skills/spec-double-compiler/references/conformance_testing.md", "ranges": "1-89", "lines": 89},
    {"path": "examples/effect_providers/PREREGISTRATION.md", "ranges": "1-28", "lines": 28},
    {"path": "examples/effect_providers/PREREGISTRATION.yaml", "ranges": "1-330", "lines": 330},
    {"path": "examples/effect_providers/legacy_payment_http/README.md (initial stub)", "ranges": "1-11", "lines": 11},
    {"path": "references/effect_providers.md", "ranges": "1-247", "lines": 247},
    {"path": "spec_double_compiler/runtime.py", "ranges": "1-201", "lines": 201},
    {"path": "spec_double_compiler/effects.py", "ranges": "1-178", "lines": 178},
    {"path": "scripts/run_generated_case_adapters.py", "ranges": "1-620;820-2164", "lines": 1965},
    {"path": "examples/distributed_history/specs/program_model/Core.tla", "ranges": "1-20", "lines": 20},
    {"path": "examples/distributed_history/specs/program_model/Internal.tla", "ranges": "1-59", "lines": 59},
    {"path": "examples/distributed_history/specs/program_model/Internal.cfg", "ranges": "1-6", "lines": 6},
    {"path": "examples/distributed_history/specs/program_model/External.tla", "ranges": "1-167", "lines": 167},
    {"path": "examples/distributed_history/specs/program_model/External.cfg", "ranges": "1-7", "lines": 7},
    {"path": "examples/distributed_history/specs/program_model/actions.yml", "ranges": "1-80", "lines": 80},
    {"path": "examples/distributed_history/specs/program_model/spec_manifest.yaml", "ranges": "1-43", "lines": 43},
    {"path": "examples/distributed_history/specs/program_model/case_adapters.toml", "ranges": "1-15", "lines": 15},
    {"path": "examples/distributed_history/specs/program_model/testgraph_bindings.yml", "ranges": "1-130", "lines": 130},
    {"path": "examples/distributed_history/specs/program_model/tlc_projection.py", "ranges": "1-117", "lines": 117},
    {"path": "examples/distributed_history/scripts/regenerate_tlc_cases.py", "ranges": "1-115", "lines": 115},
    {"path": "tests/test_effect_provider_fuzzing.py", "ranges": "1-220;1230-1430", "lines": 421},
    {"path": "tests/test_effect_provider_runtime.py", "ranges": "1-230;280-325", "lines": 276},
    {"path": "scripts/generate_python.py", "ranges": "1-260;450-570", "lines": 381},
    {"path": "scripts/extract_spec_manifest.py", "ranges": "1-340", "lines": 340},
    {"path": "scripts/generate_cases_from_tlc_dump.py", "ranges": "300-820;860-1001", "lines": 663},
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, required=True)
    args = parser.parse_args()
    implementation_files = _implementation_files()
    changed_lines = sum(_line_count(path) for path in implementation_files)
    finished = datetime.now(timezone.utc)
    retrieval = {
        "method": (
            "Unique source-line ranges actually opened are counted once per file. "
            "Inventory/rg result snippets and post-write validation reads are excluded. "
            "Changed-file cost includes project implementation and regenerated source, "
            "but excludes .venv, caches, raw experiment evidence, TLC dot/log output, "
            "and this self-referential ledger."
        ),
        "retrieval_files_read": len(READ_LEDGER),
        "retrieval_lines_read": sum(row["lines"] for row in READ_LEDGER),
        "retrieval_files_changed": len(implementation_files),
        "retrieval_lines_changed": changed_lines,
        "read_ledger": READ_LEDGER,
        "changed_ledger": [
            {
                "path": str(path.relative_to(PROJECT_ROOT)),
                "lines": _line_count(path),
            }
            for path in implementation_files
        ],
    }
    authoring = {
        "authoring_started_utc": AUTHORING_STARTED.isoformat(),
        "authoring_finished_utc": finished.isoformat(),
        "authoring_wall_minutes": round(
            (finished - AUTHORING_STARTED).total_seconds() / 60.0, 2
        ),
        "authoring_edit_run_iterations": args.iterations,
    }
    evidence = PROJECT_ROOT / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "retrieval.json").write_text(
        json.dumps(retrieval, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (evidence / "authoring.json").write_text(
        json.dumps(authoring, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    rows = [
        "# Retrieval and authoring evidence",
        "",
        retrieval["method"],
        "",
        f"- Files read: {retrieval['retrieval_files_read']}",
        f"- Unique lines read: {retrieval['retrieval_lines_read']}",
        f"- Implementation/generated files changed: {retrieval['retrieval_files_changed']}",
        f"- Lines changed: {retrieval['retrieval_lines_changed']}",
        f"- Authoring wall minutes: {authoring['authoring_wall_minutes']}",
        f"- Edit/run iterations: {authoring['authoring_edit_run_iterations']}",
        "",
        "The exact per-file read and changed ledgers are in `evidence/retrieval.json`.",
        "Machine-readable authoring timing is in `evidence/authoring.json`.",
        "",
    ]
    (PROJECT_ROOT / "RETRIEVAL_EVIDENCE.md").write_text(
        "\n".join(rows), encoding="utf-8"
    )
    print(json.dumps({**authoring, **{key: retrieval[key] for key in (
        "retrieval_files_read", "retrieval_lines_read", "retrieval_files_changed", "retrieval_lines_changed"
    )}}, indent=2, sort_keys=True))
    return 0


def _implementation_files() -> list[Path]:
    excluded_names = {"RETRIEVAL_EVIDENCE.md"}
    files: list[Path] = []
    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(PROJECT_ROOT)
        if relative.name in excluded_names:
            continue
        if any(part in {".venv", "__pycache__", ".uv-cache"} for part in relative.parts):
            continue
        if path.suffix in {".pyc", ".dot", ".log", ".gz"}:
            continue
        if relative.parts and relative.parts[0] == "evidence":
            continue
        files.append(path)
    return sorted(files)


def _line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8").splitlines())


if __name__ == "__main__":
    raise SystemExit(main())
