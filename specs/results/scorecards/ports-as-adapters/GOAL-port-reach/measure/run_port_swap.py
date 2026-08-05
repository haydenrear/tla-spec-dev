"""The fake/real swap, run as an instrument. PA-04's headline measurement.

One case list. Two implementations of one declared port. Every adapter-internal
mutant in the catalogue applied to a working copy of the ported reference, and
every instrument asked what it saw.

    corpus-port-swap:real    the generated port corpus, port-bound, FileJournal
    corpus-port-swap:fake    the SAME cases, port-bound, InMemoryJournal
    corpus-action-bound      the SAME cases, bound to ACTIONS -- the pre-PA-04
                             world, in which `--wiring fake` has nothing to swap
    suite-real / suite-fake  PA-01's hand-written columns, for contrast

WHAT THIS DOES NOT DO

It does not seed anything. Every mutant is read from the sealed catalogue with
its own `find`/`replace`, applied exactly once, and reverted. If a column is
zero it is reported as zero: a fault seeded to make a number is not a
measurement, and this epic prefers a measured miss to a flattering pass.

It runs each cell in a FRESH INTERPRETER. See `port_corpus_run.py` for why.

Two runs over an identical corpus must produce byte-identical output. The one
nondeterministic field either instrument produces -- pytest's elapsed time --
is removed rather than excused: an elapsed time is not evidence about a mutant.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[5]
AB = REPO_ROOT / "examples/validation/ab"
SUITE = AB / "tests/test_behavior.py"
TREE = "reference_ports"

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

KILLED = "KILLED"
SURVIVED = "SURVIVED"
CONTROL_RED = "CONTROL_RED"

RERUN = REPO_ROOT / "specs/results/scorecards/hexagonal-prompting-rerun"

#: What can be measured, and with what. Every field is here rather than on the
#: command line so that a run is reproducible from its own artifact.
#:
#:   source      the tree copied whole; mutants apply to the copy
#:   subdir      catalogue paths are relative to this, inside the copy
#:   binding     how the shared oracle reaches the tree's internals
#:   catalogues  read as declared; nothing is seeded by this script
#:   corpus      instrument name -> (mapping file, wiring)
#:   suites      instrument name -> composition point the suite imports
SUBJECTS: dict[str, dict[str, Any]] = {
    "reference_ports": {
        "source": AB / "reference_ports",
        "subdir": "reference_ports",
        "binding": "ports_binding",
        "catalogues": [AB / "seeded_faults.toml"],
        "corpus": {
            "corpus-port-swap:real": ("case_adapters.port-swap.toml", "real"),
            "corpus-port-swap:fake": ("case_adapters.port-swap.toml", "fake"),
            "corpus-action-bound:real": ("case_adapters.action-only.toml", "real"),
            "corpus-action-bound:fake": ("case_adapters.action-only.toml", "fake"),
        },
        "suites": {"suite-real": "quota_ledger", "suite-fake": "quota_ledger_fake"},
    },
    "arm_a": {
        "source": RERUN / "arms/arm_a",
        "subdir": ".",
        "binding": "rerun_arm_a_binding",
        "catalogues": [RERUN / "measure/catalogue_arm_a.toml", RERUN / "measure/controls_arm_a.toml"],
        "corpus": {
            "corpus-action-bound": ("case_adapters.arm-action.toml", "real"),
            "corpus-port-swap:real": ("case_adapters.arm-a-port.toml", "real"),
            "corpus-port-swap:fake": ("case_adapters.arm-a-port.toml", "fake"),
        },
        "suites": {},
    },
    "arm_b": {
        "source": RERUN / "arms/arm_b",
        "subdir": ".",
        "binding": "rerun_arm_b_binding",
        "catalogues": [RERUN / "measure/catalogue_arm_b.toml", RERUN / "measure/controls_arm_b.toml"],
        "corpus": {
            "corpus-action-bound": ("case_adapters.arm-action.toml", "real"),
            "corpus-port-swap:real": ("case_adapters.arm-b-port.toml", "real"),
            "corpus-port-swap:fake": ("case_adapters.arm-b-port.toml", "fake"),
        },
        "suites": {},
    },
}


def run_corpus(tree: Path, cases: Path, mapping: str, wiring: str, binding: str) -> dict[str, Any]:
    import os

    environment = dict(os.environ, QUOTA_LEDGER_BINDING=binding)
    completed = subprocess.run(
        [
            sys.executable, str(HERE / "port_corpus_run.py"),
            "--cases", str(cases), "--tree", str(tree),
            "--mapping", str(HERE / mapping), "--wiring", wiring,
        ],
        capture_output=True, text=True, cwd=str(REPO_ROOT), env=environment,
    )
    if completed.returncode != 0:
        return {
            "total_ran": 0, "total_failed": 0, "harness_error": True,
            "failures": completed.stderr.strip().splitlines()[-3:],
        }
    return json.loads(completed.stdout)


def run_suite(tree: Path, impl: str) -> dict[str, Any]:
    import os

    environment = dict(os.environ, QUOTA_LEDGER_DIR=str(tree), QUOTA_LEDGER_IMPL=impl)
    completed = subprocess.run(
        ["uv", "run", "--with", "pytest", "python", "-m", "pytest", str(SUITE), "-q"],
        cwd=str(REPO_ROOT), env=environment, capture_output=True, text=True,
    )
    tail = [line for line in completed.stdout.splitlines() if line.strip()][-1:]
    tail = [re.sub(r" in \d+\.\d+s$", "", line) for line in tail]
    return {"total_failed": int(completed.returncode != 0), "failures": tail}


def observe(subject: dict[str, Any], tree: Path, cases: Path) -> dict[str, dict[str, Any]]:
    observed: dict[str, dict[str, Any]] = {}
    for name, (mapping, wiring) in subject["corpus"].items():
        observed[name] = run_corpus(tree, cases, mapping, wiring, subject["binding"])
    for name, impl in subject["suites"].items():
        observed[name] = run_suite(tree, impl)
    return observed


def render(report: dict[str, Any]) -> str:
    instruments = report["instruments"]
    rows = ["| mutant | " + " | ".join(instruments) + " |",
            "|---|" + "---|" * len(instruments)]
    for mutant in report["per_mutant"]:
        cells = [report["per_mutant"][mutant]["cells"][name] for name in instruments]
        rows.append(f"| {mutant} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subject", choices=sorted(SUBJECTS), required=True)
    parser.add_argument("--cases", type=Path, required=True, help="Generated port corpus package")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    subject = SUBJECTS[args.subject]
    instruments = list(subject["corpus"]) + list(subject["suites"])
    prefix = subject["subdir"]

    mutants: list[dict[str, Any]] = []
    for path in subject["catalogues"]:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
        for entry in document.get("mutants", []):
            declared = str(entry.get("path", ""))
            if prefix == ".":
                mutants.append({**entry, "relative": declared})
            elif declared.startswith(f"{prefix}/"):
                mutants.append({**entry, "relative": declared[len(prefix) + 1:]})

    workspace = Path(tempfile.mkdtemp(prefix="pa04-swap-tree-"))
    tree = workspace / "tree"
    shutil.copytree(subject["source"], tree, ignore=shutil.ignore_patterns("__pycache__", "tests"))
    # The arm-B fake composition point is a MEASUREMENT artifact and must be
    # importable beside the arm without being written into it. The arm on disk
    # is never touched; only this throwaway copy gains a file.
    if args.subject == "arm_b":
        shutil.copy2(HERE / "arm_b_fake.py", tree / "arm_b_fake.py")
    pristine = {path: path.read_text(encoding="utf-8") for path in tree.rglob("*.py")}

    try:
        controls = observe(subject, tree, args.cases)
        control_failed = {
            name: bool(record.get("total_failed") or record.get("harness_error"))
            for name, record in controls.items()
        }

        per_mutant: dict[str, Any] = {}
        for mutant in mutants:
            target = tree / mutant["relative"]
            original = pristine[target]
            occurrences = original.count(mutant["find"])
            mutated = original.replace(mutant["find"], mutant["replace"], 1)
            target.write_text(mutated, encoding="utf-8")
            for cache in tree.rglob("__pycache__"):
                shutil.rmtree(cache, ignore_errors=True)
            try:
                observed = observe(subject, tree, args.cases)
            finally:
                target.write_text(original, encoding="utf-8")
                for cache in tree.rglob("__pycache__"):
                    shutil.rmtree(cache, ignore_errors=True)
            per_mutant[mutant["id"]] = {
                "fault_class": mutant.get("fault_class"),
                "path": mutant["path"],
                "control_role": mutant.get("control_role"),
                "occurrences_of_find": occurrences,
                "applied_exactly_once": occurrences == 1 and mutated != original,
                "cells": {
                    name: (
                        CONTROL_RED if control_failed[name]
                        else (KILLED if record.get("total_failed") else SURVIVED)
                    )
                    for name, record in observed.items()
                },
                "evidence": {
                    name: {
                        key: record.get(key)
                        for key in ("total_ran", "total_failed", "total_skipped", "failures")
                        if key in record
                    }
                    for name, record in observed.items()
                },
            }

        report = {
            "instruments": instruments,
            "subject": args.subject,
            "tree": str(Path(subject["source"]).relative_to(REPO_ROOT)),
            "binding": subject["binding"],
            "cases": str(args.cases.name),
            "catalogues": [str(path.relative_to(REPO_ROOT)) for path in subject["catalogues"]],
            "controls_on_unmutated_code": controls,
            "control_red": sorted(name for name, red in control_failed.items() if red),
            "per_mutant": dict(sorted(per_mutant.items())),
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(render(report))
        print(f"\nwrote {args.out}")
        return 0
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
