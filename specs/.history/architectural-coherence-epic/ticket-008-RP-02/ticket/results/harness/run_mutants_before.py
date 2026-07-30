#!/usr/bin/env python3
"""RP-02: the same reconstructed 12-mutant catalog, on the PRE-RP-02 instrument.

Swaps in the adapter as it stood at HEAD (the one that diffed `case.after` for
its argument) and the corpus generated before the fix (`params={'i': UNCHECKED}`),
so the after-table has a measured before-table to sit next to instead of an
argument about what would have happened.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path

REPO = Path("/Users/hayde/IdeaProjects/wt-rp02-oracle-leakage")
FIXTURE = REPO / "examples/validation/ex4_pipeline_coherent"
SCRATCH = Path(__file__).resolve().parent
CORPUS = SCRATCH / "before-gen/spec-unit/pipeline_cases"
ADAPTERS = FIXTURE / "specs/program_model/adapters.py"


def run_arm(mapping: str) -> bool:
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
    return proc.returncode == 0


def main() -> int:
    catalog = tomllib.loads((SCRATCH / "mutants.toml").read_text())["mutants"]
    new_adapter = ADAPTERS.read_text()
    old_adapter = subprocess.run(
        ["git", "show", "HEAD:examples/validation/ex4_pipeline_coherent/specs/program_model/adapters.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    results = []
    try:
        ADAPTERS.write_text(old_adapter)
        print("=== CONTROL (pre-RP-02 instrument, unmutated) ===")
        for name, mapping in (("arm_a", "case_adapters_corpus_only.toml"), ("arm_b", "case_adapters.toml")):
            ok = run_arm(mapping)
            print(f"  {name}: {'GREEN' if ok else 'RED'}")
            if not ok:
                return 2
        for mutant in catalog:
            target = FIXTURE / mutant["path"]
            original = target.read_text()
            assert mutant["find"] in original, mutant["id"]
            try:
                target.write_text(original.replace(mutant["find"], mutant["replace"], 1))
                a_ok = run_arm("case_adapters_corpus_only.toml")
                b_ok = run_arm("case_adapters.toml")
            finally:
                target.write_text(original)
            row = {
                "id": mutant["id"],
                "fault_class": mutant["fault_class"],
                "arm_a": "KILLED" if not a_ok else "SURVIVED",
                "arm_b": "KILLED" if not b_ok else "SURVIVED",
            }
            results.append(row)
            print(f"{row['id']:>4} {row['fault_class']:<26} ARM A {row['arm_a']:<9} ARM B {row['arm_b']}")
    finally:
        ADAPTERS.write_text(new_adapter)
    (SCRATCH / "mutant_matrix_before.json").write_text(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
