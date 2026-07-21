#!/usr/bin/env python3
"""MF-038 kill-rate probe.

Measures the ONE number the modular-fuzzing value proposition rests on: do the
generated cases catch real bugs seeded into the production CLI implementations
that the runnable (~10%) corpus adapters exercise?

This is a MEASUREMENT, not a gate. It reuses the real MF-016 kill-test
instrument -- `kill_test.subprocess_case_runner` (which applies each mutant via
`kill_test.seeded()` and restores it), and `kill_test.control_run` (the
green-control safeguard) -- rather than the whole `run_kill_test.py` gate,
because the gate imposes the per-boundary coverage obligation that answers a
different question (representation quality per declared port/invariant). Here the
question is the corpus's kill power against realistic bugs, so the harness runs
control-first, then seeds each catalogued mutant and records killed/survived,
and computes killed/total with NO floor and NO waiver.

Usage:
    python3 specs/tickets/MF-038/results/measure_kill_rate.py <cases_dir> \
        [--out <report.json>] [--timeout N]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT))

from scripts.kill_test import (  # noqa: E402
    control_run,
    load_catalog,
    subprocess_case_runner,
)

# The reduced RUNNABLE selection: every runnable action that exercises real CLI
# implementation code, spanning the singletons plus several before-state variants
# of the multi-case actions. These are the ~10% filesystem-mutating commands
# (MF-031/MF-032). The denominator of the kill rate is the MUTANTS; these cases
# are the instrument.
RUNNABLE_CASES = [
    "case_0001_build_skill_cli",
    "case_0003_install_local_cli",
    "case_0005_scaffold_project",
    "case_0007_record_budgets",
    "case_0009_scaffold_workflow",
    "case_0035_scaffold_workflow",
    "case_0048_scaffold_workflow",
    "case_0022_open_ticket",
    "case_0191_open_ticket",
    "case_0204_open_ticket",
    "case_0178_update_ticket_desired",
    "case_1634_update_ticket_desired",
    "case_1621_update_ticket_current",
    "case_6612_update_ticket_current",
]

MAPPING = REPO_ROOT / "specs/tickets/MF-038/results/case_adapters_mf038.toml"
CATALOG = REPO_ROOT / "specs/tickets/MF-038/results/kill_mutants_mf038.toml"


def corpus_command(cases_dir: Path) -> list[str]:
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts/run_generated_case_adapters.py"),
        str(cases_dir),
        "--mapping",
        str(MAPPING),
        "--import-root",
        str(REPO_ROOT / "specs/current"),
        "--batch",
    ]
    for name in RUNNABLE_CASES:
        cmd += ["--case", name]
    return cmd


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cases_dir", type=Path)
    ap.add_argument("--out", type=Path, default=CATALOG.parent / "kill-rate-report.json")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args()

    catalog, suppressions = load_catalog(CATALOG)
    command = corpus_command(args.cases_dir.resolve())
    runner = subprocess_case_runner(command, root=REPO_ROOT, timeout=args.timeout)

    print(f"corpus command: {' '.join(command)}")
    print(f"runnable cases: {len(RUNNABLE_CASES)}")
    print(f"mutants: {len(catalog)}")
    print(f"ignored suppression-shaped keys: {suppressions or 'none'}")
    print()

    # THE CONTROL. Unmutated corpus must be GREEN, else no kill is attributable.
    print("=== control run (unmutated corpus) ===")
    green, control_detail = control_run(runner)
    print("control_green:", green)
    if not green:
        print("CONTROL FAILED -- the kill rate is meaningless. Corpus output tail:")
        print("\n".join(control_detail.splitlines()[-40:]))
        report = {
            "verdict": "control_failed",
            "control_green": False,
            "control_detail": control_detail[-4000:],
            "kill_rate": None,
            "runnable_cases": RUNNABLE_CASES,
            "corpus_command": " ".join(command),
        }
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(f"\nwrote {args.out}")
        return 2
    print("control is GREEN -- proceeding to seed mutants.\n")

    outcomes = []
    for mutant in catalog:
        killed, killed_by, detail = runner(mutant)
        status = "KILLED" if killed else "SURVIVED"
        print(f"{status:8}  {mutant.id:42}  ({mutant.boundary_ref})")
        outcomes.append(
            {
                "mutant_id": mutant.id,
                "description": mutant.description,
                "path": mutant.path,
                "boundary_ref": mutant.boundary_ref,
                "refine_variable": mutant.refine_variable,
                "refine_action": mutant.refine_action,
                "killed": killed,
                "killed_by": sorted(killed_by),
                "detail_tail": detail[-1500:],
            }
        )

    total = len(outcomes)
    killed_n = sum(1 for o in outcomes if o["killed"])
    survivors = [o for o in outcomes if not o["killed"]]
    kill_rate = killed_n / total if total else None

    report = {
        "verdict": "measured",
        "control_green": True,
        "kill_rate": kill_rate,
        "mutants_total": total,
        "mutants_killed": killed_n,
        "mutants_survived": len(survivors),
        "runnable_cases": RUNNABLE_CASES,
        "runnable_case_count": len(RUNNABLE_CASES),
        "corpus_command": " ".join(command),
        "ignored_suppression_keys": suppressions,
        "kill_matrix": outcomes,
        "survivors": [o["mutant_id"] for o in survivors],
    }
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print()
    print(f"KILL RATE: {killed_n}/{total} = {kill_rate:.3f}" if kill_rate is not None else "no mutants")
    print(f"survivors: {report['survivors']}")
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
