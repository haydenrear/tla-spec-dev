#!/usr/bin/env python3
"""RP-02: re-run the reconstructed 12-mutant catalog against ex4.

Three instruments per mutant, exactly the three columns the ex4-run3 table has:

  ARM A   the 330-case whole-view corpus alone
  ARM B   the same corpus plus the content-asserting LedgerStorePort provider
  pytest  the fixture's own hand-written behavioural suite

Every mutant is applied by verbatim find/replace with a `finally` restore, and
the whole run ends with a `git status` check on the fixture. A run that leaves
the tree dirty has corrupted its own measurement.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path

FIXTURE = Path("/Users/hayde/IdeaProjects/wt-rp02-oracle-leakage/examples/validation/ex4_pipeline_coherent")
REPO = Path("/Users/hayde/IdeaProjects/wt-rp02-oracle-leakage")
SCRATCH = Path(__file__).resolve().parent
CORPUS = SCRATCH / "after-gen/spec-unit/pipeline_cases"


def run_arm(mapping: str) -> tuple[bool, str]:
    env = {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin",
        "HOME": str(Path.home()),
        "PYTHONPATH": f"{REPO}:{FIXTURE / 'generated'}",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    proc = subprocess.run(
        [
            sys.executable,
            str(REPO / "scripts/run_generated_case_adapters.py"),
            str(CORPUS),
            "--mapping",
            f"specs/program_model/{mapping}",
            "--spec-dir",
            "specs/program_model",
            "--view",
            "internal",
            "--batch",
            "--import-root",
            ".",
        ],
        cwd=FIXTURE,
        capture_output=True,
        text=True,
        env=env,
    )
    return proc.returncode == 0, (proc.stdout + proc.stderr)[-1200:]


def run_pytest() -> tuple[bool, str]:
    env = {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin",
        "HOME": str(Path.home()),
        "PYTHONPATH": str(FIXTURE),
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-q"],
        cwd=FIXTURE,
        capture_output=True,
        text=True,
        env=env,
    )
    return proc.returncode == 0, (proc.stdout + proc.stderr)[-600:]


def main() -> int:
    catalog = tomllib.loads((SCRATCH / "mutants.toml").read_text())["mutants"]
    results = []

    print("=== CONTROL (unmutated) ===")
    control = {
        "arm_a": run_arm("case_adapters_corpus_only.toml"),
        "arm_b": run_arm("case_adapters.toml"),
        "pytest": run_pytest(),
    }
    for name, (ok, tail) in control.items():
        print(f"  {name}: {'GREEN' if ok else 'RED'}")
        if not ok:
            print(tail)
            print("CONTROL IS NOT GREEN -- no kill number from this run means anything.")
            return 2

    for mutant in catalog:
        target = FIXTURE / mutant["path"]
        original = target.read_text()
        if mutant["find"] not in original:
            print(f"{mutant['id']}: STALE PATTERN -- refusing to score")
            return 2
        patched = original.replace(mutant["find"], mutant["replace"], 1)
        assert patched != original, mutant["id"]
        try:
            target.write_text(patched)
            a_ok, a_tail = run_arm("case_adapters_corpus_only.toml")
            b_ok, b_tail = run_arm("case_adapters.toml")
            p_ok, p_tail = run_pytest()
        finally:
            target.write_text(original)
        row = {
            "id": mutant["id"],
            "fault_class": mutant["fault_class"],
            "arm_a": "KILLED" if not a_ok else "SURVIVED",
            "arm_b": "KILLED" if not b_ok else "SURVIVED",
            "pytest": "KILLED" if not p_ok else "SURVIVED",
            "arm_a_tail": a_tail if not a_ok else "",
            "pytest_tail": p_tail if not p_ok else "",
        }
        results.append(row)
        print(
            f"{row['id']:>4} {row['fault_class']:<26} "
            f"ARM A {row['arm_a']:<9} ARM B {row['arm_b']:<9} pytest {row['pytest']}"
        )

    status = subprocess.run(
        ["git", "status", "--porcelain", "examples/validation/ex4_pipeline_coherent/pipeline"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    print("\nfixture restored (git status on pipeline/):", repr(status.stdout.strip()) or "clean")
    (SCRATCH / "mutant_matrix.json").write_text(
        json.dumps({"control": {k: v[0] for k, v in control.items()}, "mutants": results}, indent=2)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
