#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[2]
SPEC_DIR = PROJECT_ROOT / "specs" / "program_model"
GENERATED_DIR = SPEC_DIR / "generated"
CASE_ROOT = GENERATED_DIR / "cases"


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate typed port and TLC-derived atomic publisher cases.")
    parser.add_argument("--tlc2", default=os.environ.get("TLC2", "tlc2"))
    args = parser.parse_args()

    targets = [
        GENERATED_DIR / "atomic_publisher_contract",
        CASE_ROOT / "spec-unit" / "atomic_internal_cases",
        CASE_ROOT / "testgraph" / "atomic_external_cases",
    ]
    for target in targets:
        if target.exists():
            shutil.rmtree(target)

    run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "generate_python.py"),
            str(SPEC_DIR / "spec_manifest.yaml"),
            "--out",
            str(GENERATED_DIR),
        ]
    )

    records: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="atomic-publisher-tlc-") as raw_tmp:
        tmp = Path(raw_tmp)
        for view, module, package, lane in (
            ("internal", "Internal", "atomic_internal_cases", "spec-unit"),
            ("external", "External", "atomic_external_cases", "testgraph"),
        ):
            completed = run(
                [
                    sys.executable,
                    str(REPO_ROOT / "scripts" / "generate_cases_from_tlc_dump.py"),
                    str(SPEC_DIR / f"{module}.tla"),
                    str(SPEC_DIR / f"{module}.cfg"),
                    "--out",
                    str(CASE_ROOT),
                    "--package",
                    package,
                    "--view",
                    view,
                    "--actions-metadata",
                    str(SPEC_DIR / "actions.yml"),
                    "--tlc2",
                    args.tlc2,
                    "--dot",
                    str(tmp / f"{module}.dot"),
                    "--state-projector",
                    "specs.program_model.tlc_projection:project_state",
                    "--output-projector",
                    "specs.program_model.tlc_projection:project_output",
                    "--dedupe",
                    "projected",
                    "--labeler",
                    "specs.program_model.tlc_projection:outcome_label",
                ],
                timeout=120,
            )
            package_dir = CASE_ROOT / lane / package
            cases = load_cases(package_dir)
            records[view] = parse_generation_output(
                completed.stdout,
                cases,
                wall_seconds=float(getattr(completed, "measured_wall_seconds")),
            )

    expected_internal_actions = {
        "CreateSuccess",
        "ValidUpdate",
        "IdempotentRetry",
        "StaleRevision",
        "ReadFailure",
        "StagedWriteFailure",
        "ReplaceFailure",
    }
    observed = set(records["internal"]["actions"])
    if observed != expected_internal_actions:
        raise AssertionError(
            f"generated action collapse or coverage gap: expected {sorted(expected_internal_actions)}, observed {sorted(observed)}"
        )
    if records["internal"]["action_outcome_coverage"] != 7:
        raise AssertionError("internal generator did not preserve all seven semantic outcomes")

    sources = [
        "Core.tla",
        "Internal.tla",
        "Internal.cfg",
        "External.tla",
        "External.cfg",
        "actions.yml",
        "spec_manifest.yaml",
        "tlc_projection.py",
    ]
    provenance = {
        "case_source": "TLC reachable action-labeled transitions",
        "generator": "scripts/generate_cases_from_tlc_dump.py",
        "model_digests": {name: sha256(SPEC_DIR / name) for name in sources},
        "typed_port_generator": "scripts/generate_python.py",
        "views": records,
    }
    (GENERATED_DIR / "provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(provenance, indent=2, sort_keys=True))
    return 0


def run(command: list[str], *, timeout: int = 30) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    setattr(completed, "measured_wall_seconds", time.perf_counter() - started)
    print("$ " + " ".join(command))
    print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, file=sys.stderr, end="")
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return completed


def load_cases(package_dir: Path) -> list[Any]:
    sys.path.insert(0, str(package_dir.parent))
    try:
        importlib.invalidate_caches()
        module = importlib.import_module(f"{package_dir.name}.cases")
    finally:
        sys.path.remove(str(package_dir.parent))
    return list(module.CASES)


def parse_generation_output(
    output: str,
    cases: list[Any],
    *,
    wall_seconds: float,
) -> dict[str, Any]:
    state_match = re.search(r"(\d+) states generated, (\d+) distinct states found", output)
    depth_match = re.search(r"depth of the complete state graph search is (\d+)", output)
    action_outcomes = sorted(
        {
            (str(case.input.action), str(case.after["outcome"]))
            for case in cases
        }
    )
    return {
        "action_outcome_coverage": len(action_outcomes),
        "action_outcomes": [list(value) for value in action_outcomes],
        "actions": sorted({str(case.input.action) for case in cases}),
        "distinct_states": int(state_match.group(2)) if state_match else None,
        "generated_cases": len(cases),
        "generated_states": int(state_match.group(1)) if state_match else None,
        "search_depth": int(depth_match.group(1)) if depth_match else None,
        "wall_seconds": round(wall_seconds, 6),
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
