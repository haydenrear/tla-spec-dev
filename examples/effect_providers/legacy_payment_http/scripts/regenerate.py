#!/usr/bin/env python3
"""Regenerate the typed port and both case corpora, then gate provenance."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from time import perf_counter
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_ROOT.parents[2]
SPEC_DIR = PROJECT_ROOT / "specs" / "program_model"
GENERATED = PROJECT_ROOT / "specs" / "generated"
DEFAULT_EVIDENCE = PROJECT_ROOT / "evidence"

INTERNAL_ACTIONS = {
    "AuthorizeApproved",
    "AuthorizeDeclined",
    "AuthorizeBadRequest",
    "AuthorizeTransientThenApproved",
    "AuthorizeTimeoutThenDuplicateApproved",
    "AuthorizeExhaustedUnavailable",
    "AuthorizeMalformedResponse",
}
EXTERNAL_ACTIONS = {action.replace("Authorize", "Submit", 1) for action in INTERNAL_ACTIONS}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tlc2", default="tlc2")
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=DEFAULT_EVIDENCE,
        help="Directory for regeneration logs and provenance (default: historical evidence directory).",
    )
    args = parser.parse_args()
    evidence = args.evidence_dir.resolve()
    evidence.mkdir(parents=True, exist_ok=True)
    (GENERATED / "tlc").mkdir(parents=True, exist_ok=True)

    contract = SPEC_DIR / "generated" / "payment_http_contract"
    if contract.exists():
        shutil.rmtree(contract)
    _run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "generate_python.py"),
            str(SPEC_DIR / "spec_manifest.yaml"),
            "--out",
            str(SPEC_DIR / "generated"),
        ],
        timeout=120,
    )

    summaries: dict[str, Any] = {}
    for view, module, actions, package in [
        ("internal", "Internal", INTERNAL_ACTIONS, "payment_http_internal_cases"),
        ("external", "External", EXTERNAL_ACTIONS, "payment_http_external_cases"),
    ]:
        view_dir = "spec-unit" if view == "internal" else "testgraph"
        package_dir = GENERATED / view_dir / package
        if package_dir.exists():
            shutil.rmtree(package_dir)
        command = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "generate_cases_from_tlc_dump.py"),
            str(SPEC_DIR / f"{module}.tla"),
            str(SPEC_DIR / f"{module}.cfg"),
            "--out",
            str(GENERATED),
            "--package",
            package,
            "--view",
            view,
            "--actions-metadata",
            str(SPEC_DIR / "actions.yml"),
            "--tlc2",
            args.tlc2,
            "--dot",
            str(SPEC_DIR / "generated" / "tlc" / f"{module}.dot"),
            "--state-projector",
            "specs.program_model.tlc_projection:project_state",
            "--output-projector",
            "specs.program_model.tlc_projection:project_output",
            "--dedupe",
            "projected",
        ]
        started = perf_counter()
        completed = _run(command, timeout=120, capture=True)
        wall_seconds = perf_counter() - started
        log = completed.stdout + completed.stderr
        (evidence / f"tlc-{view}.log").write_text(log, encoding="utf-8")
        module_cases = _load_cases(package_dir)
        cases = list(module_cases.CASES)
        actual_actions = {str(case.input.action) for case in cases}
        if actual_actions != actions:
            raise SystemExit(
                f"ERROR: preregistered {view} actions collapsed or drifted: "
                f"expected {sorted(actions)}, generated {sorted(actual_actions)}"
            )
        missing_labels = [
            case.name for case in cases if str(case.input.action) not in set(case.labels)
        ]
        if missing_labels:
            raise SystemExit(
                f"ERROR: generated {view} cases missing their semantic action label: {missing_labels[:5]}"
            )
        coverage = {
            action: sum(case.input.action == action for case in cases)
            for action in sorted(actions)
        }
        summaries[view] = {
            **_parse_tlc(log),
            "wall_seconds": wall_seconds,
            "generated_cases": len(cases),
            "selected_cases": len(cases),
            "executed_cases": 0,
            "action_outcome_coverage": coverage,
            "actions": sorted(actual_actions),
            "package": str(package_dir.relative_to(PROJECT_ROOT)),
        }

    provenance = {
        "model_digests": {
            name: _sha256(SPEC_DIR / name)
            for name in (
                "Core.tla",
                "Internal.tla",
                "Internal.cfg",
                "External.tla",
                "External.cfg",
                "actions.yml",
                "spec_manifest.yaml",
            )
        },
        "generated_port": {
            "path": "specs/program_model/generated/payment_http_contract/ports.py",
            "sha256": _sha256(contract / "ports.py"),
        },
        "views": summaries,
    }
    (evidence / "tlc-generation.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(provenance, indent=2, sort_keys=True))
    return 0


def _run(
    command: list[str],
    *,
    timeout: int,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    if completed.returncode != 0:
        sys.stderr.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        raise SystemExit(completed.returncode)
    if not capture:
        sys.stdout.write(completed.stdout)
        sys.stderr.write(completed.stderr)
    return completed


def _load_cases(package_dir: Path) -> Any:
    sys.path.insert(0, str(package_dir.parent))
    for module_name in list(sys.modules):
        if module_name == package_dir.name or module_name.startswith(package_dir.name + "."):
            del sys.modules[module_name]
    return importlib.import_module(package_dir.name)


def _parse_tlc(text: str) -> dict[str, int | None]:
    counts = re.search(
        r"([\d,]+)\s+states generated,\s+([\d,]+)\s+distinct states found",
        text,
    )
    depth = re.search(r"depth of the complete state graph search is\s+(\d+)", text)
    return {
        "generated_states": int(counts.group(1).replace(",", "")) if counts else None,
        "distinct_states": int(counts.group(2).replace(",", "")) if counts else None,
        "search_depth": int(depth.group(1)) if depth else None,
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
