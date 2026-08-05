#!/usr/bin/env python3
"""HP-02 local signal: run the re-anchored catalogue against each arm.

NOT the HP-06 measurement, and not a shipped tool. Ticket evidence, living in
the ticket's results/ so it travels into .history with the close record. It
gates nothing.

Two instruments, and they must never be merged into one number:

  suite     the SHARED hand-written suite (examples/validation/ab/tests/
            test_behavior.py). Identical for both arms, so its row is a fact
            about the suite, not about an arm.
  arm-own   the arm's OWN tests, whatever the arm chose to write. This is the
            row HP-02's guard on GOAL-catch-bugs is actually about: a prompt
            that produces prettier code whose own checks catch less has failed.

A control run (no mutant) precedes everything. Without it a "kill" may be an
unrelated pre-existing failure.

    python3 specs/tickets/HP-02/results/pilot/run_pilot_kills.py
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[4]
SHARED_SUITE = REPO_ROOT / "examples/validation/ab/tests/test_behavior.py"

ARMS = {
    "A": {"dir": HERE / "arm_a", "own": ["test_quota_ledger.py"]},
    "B": {"dir": HERE / "arm_b", "own": ["tests"]},
}


def run(cmd: list[str], cwd: Path, env_extra: dict) -> bool:
    import os

    env = dict(os.environ, **env_extra)
    done = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)
    return done.returncode == 0


def instruments(arm_dir: Path, own: list[str]) -> dict:
    env = {"QUOTA_LEDGER_DIR": str(arm_dir), "QUOTA_LEDGER_IMPL": "quota_ledger"}
    pytest = ["uv", "run", "--with", "pytest", "python", "-m", "pytest", "-q", "-p", "no:cacheprovider"]
    return {
        "suite": lambda: run(pytest + [str(SHARED_SUITE)], REPO_ROOT, env),
        "arm-own": lambda: run(pytest + own, arm_dir, env),
    }


def main() -> int:
    rows: dict[str, dict[str, dict[str, str]]] = {}
    classes: dict[str, str] = {}

    for arm, spec in ARMS.items():
        arm_dir = spec["dir"]
        catalogue = HERE / f"catalogue_arm_{arm.lower()}.toml"
        mutants = tomllib.loads(catalogue.read_text())["mutants"]
        insts = instruments(arm_dir, spec["own"])

        print(f"\n===== ARM {arm} =====")
        print(f"tree:      {arm_dir.relative_to(REPO_ROOT)}")
        print(f"catalogue: {catalogue.relative_to(REPO_ROOT)}")

        control = {name: fn() for name, fn in insts.items()}
        print(f"control (no mutant): " + ", ".join(
            f"{n}={'GREEN' if ok else 'RED'}" for n, ok in control.items()))
        if not all(control.values()):
            print("  CONTROL FAILED -- every kill below would be that same failure.")
            return 1

        rows[arm] = {}
        for mutant in mutants:
            mid, path = mutant["id"], arm_dir / mutant["path"]
            classes[mid] = mutant["fault_class"]
            original = path.read_text()
            assert original.count(mutant["find"]) == 1, f"{arm}/{mid}: not exactly once"
            observed = {}
            try:
                path.write_text(original.replace(mutant["find"], mutant["replace"], 1))
                for name, fn in insts.items():
                    observed[name] = "KILLED" if not fn() else "SURVIVED"
            finally:
                path.write_text(original)
            assert path.read_text() == original, f"{arm}/{mid}: revert not byte-identical"
            rows[arm][mid] = observed
            print(f"  {mid:<42} " + "  ".join(
                f"{n}={v}" for n, v in observed.items()))

    print("\n\n===== PER-CLASS, PER-ARM, PER-INSTRUMENT =====")
    print("(never an aggregate rate: the classes exist because they behave differently)\n")
    header = f"{'mutant':<42} {'class':<18}"
    for arm in ARMS:
        header += f"  {'A' if arm=='A' else 'B'}:suite   {arm}:own   "
    print(header)
    print("-" * len(header))
    for mid in rows["A"]:
        line = f"{mid:<42} {classes[mid]:<18}"
        for arm in ARMS:
            o = rows[arm][mid]
            line += f"  {o['suite']:<9} {o['arm-own']:<9}"
        print(line)

    print("\nper-class totals (killed / seeded), per arm per instrument:")
    by_class: dict[str, list[str]] = {}
    for mid, cls in classes.items():
        by_class.setdefault(cls, []).append(mid)
    print(f"{'class':<18} {'A:suite':<9} {'A:own':<9} {'B:suite':<9} {'B:own':<9}")
    for cls in sorted(by_class):
        ids = by_class[cls]
        cells = []
        for arm in ARMS:
            for inst in ("suite", "arm-own"):
                n = sum(1 for m in ids if rows[arm][m][inst] == "KILLED")
                cells.append(f"{n}/{len(ids)}")
        print(f"{cls:<18} {cells[0]:<9} {cells[1]:<9} {cells[2]:<9} {cells[3]:<9}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
