#!/usr/bin/env python3
"""RP-02: seed the class EV-01 refused to seed, on BOTH instruments.

`seeded_faults.toml` states: "CLASSES THIS INSTRUMENT CANNOT MEASURE ... a
fault whose only symptom is ACTING ON THE WRONG ITEM ... No fault of that
class is seeded, because seeding one would produce a survivor that says
nothing about the corpus."

So seed one now and run it twice:

  BEFORE  the pre-RP-02 corpus (params={'i': UNCHECKED}) with the pre-RP-02
          adapter, which re-derived the argument from `case.after`
  AFTER   the RP-02 corpus (params={'i': 'i1'}) with the RP-02 adapter, which
          reads the argument off the case

A difference is the value of the fix. NO difference is also a result and is
reported as one.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/Users/hayde/IdeaProjects/wt-rp02-oracle-leakage")
FIXTURE = REPO / "examples/validation/ex4_pipeline_coherent"
SCRATCH = Path(__file__).resolve().parent
ADAPTERS = FIXTURE / "specs/program_model/adapters.py"

# One fault, one symptom: the action ignores the item it was asked to act on
# and picks one out of ambient state instead. Every write is otherwise correct.
MUTANTS = {
    "W1-accept-wrong-item": (
        FIXTURE / "pipeline/ingest/inbox.py",
        '        """`Accept(i)`: move an item from inbox to accepted."""\n',
        '        """`Accept(i)`: move an item from inbox to accepted."""\n'
        "        item = sorted(self._inbox)[0] if self._inbox else item  # MUTANT W1\n",
    ),
    "W2-record-wrong-item": (
        FIXTURE / "pipeline/ledger/journal.py",
        '        """`Record(i)`: a delivered item, not already recorded, is appended."""\n',
        '        """`Record(i)`: a delivered item, not already recorded, is appended."""\n'
        "        item = sorted(self._dispatcher.delivered)[0] if self._dispatcher.delivered else item  # MUTANT W2\n",
    ),
}


def run_arm(corpus: Path, mapping: str) -> bool:
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
            str(corpus),
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
    old_adapter = subprocess.run(
        ["git", "show", "HEAD:examples/validation/ex4_pipeline_coherent/specs/program_model/adapters.py"],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    new_adapter = ADAPTERS.read_text()

    arms = {
        "BEFORE (UNCHECKED corpus + oracle-diffing adapter)": (
            old_adapter,
            SCRATCH / "before-gen/spec-unit/pipeline_cases",
        ),
        "AFTER  (recovered corpus + case-argument adapter)": (
            new_adapter,
            SCRATCH / "after-gen/spec-unit/pipeline_cases",
        ),
    }

    table: dict[str, dict[str, str]] = {}
    try:
        for arm_name, (adapter_src, corpus) in arms.items():
            ADAPTERS.write_text(adapter_src)
            control = run_arm(corpus, "case_adapters_corpus_only.toml")
            table.setdefault("CONTROL", {})[arm_name] = "GREEN" if control else "RED"
            for mid, (path, find, replace) in MUTANTS.items():
                original = path.read_text()
                assert find in original, (mid, path)
                try:
                    path.write_text(original.replace(find, replace, 1))
                    ok = run_arm(corpus, "case_adapters_corpus_only.toml")
                finally:
                    path.write_text(original)
                table.setdefault(mid, {})[arm_name] = "SURVIVED" if ok else "KILLED"
    finally:
        ADAPTERS.write_text(new_adapter)

    width = max(len(k) for k in table)
    arm_names = list(arms)
    print(f"{'':<{width}}  " + "  ".join(f"{a:<50}" for a in arm_names))
    for row, values in table.items():
        print(f"{row:<{width}}  " + "  ".join(f"{values[a]:<50}" for a in arm_names))
    (SCRATCH / "wrong_item_probe.json").write_text(json.dumps(table, indent=2))

    status = subprocess.run(
        ["git", "status", "--porcelain", "examples/validation/ex4_pipeline_coherent"],
        cwd=REPO,
        capture_output=True,
        text=True,
    ).stdout.strip()
    print("\nfixture git status after the probe:")
    print(status or "  (only the RP-02 adapter edit, which is this ticket's)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
