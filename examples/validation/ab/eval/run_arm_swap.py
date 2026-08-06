"""FI-04's driver: PA-04's swap runner, pointed at FI-04's catalogues.

WHAT THIS IS NOT. It is not a second verdict-table driver. `PA-04-DF-02` and
`PA-04-DF-04` record that this project already has two of those and that "two
drivers is how a number gets quoted against the wrong instrument". So this file
contains NO verdict rule, NO control rule, NO accounting and NO mutation logic.
It imports `run_port_swap` and calls its `main()`. Every cell FI-04 reports was
computed by the same function that computed PA-04's and PA-06's and FI-01's.

WHAT IT CHANGES, exhaustively:

  1. the `catalogues` list on the three arm subjects, so the arms are measured
     against FI-04's adapter-fault rows instead of the predecessor's;
  2. the `suites` table on the three arm subjects, which PA-04 left EMPTY.

Both are data. Neither is logic. `run_port_swap.SUBJECTS` is a module-level
dict read inside `main()`, so replacing entries before calling it is the whole
mechanism.

WHY (2) MATTERS AND WHY IT IS NOT A NEW INSTRUMENT. The hand-written suite is
the instrument every generator claim in this project is measured against, and
for three epics it has been run against `reference_ports/` -- a tree the epic
authored -- and never against an arm. `examples/validation/ab/tests/test_behavior.py`
is unmodified and already parameterised by `QUOTA_LEDGER_DIR`/`QUOTA_LEDGER_IMPL`;
`run_port_swap.run_suite` already knows how to drive it. Nothing here is written.

ARM A AND ARM C GET NO `suite-fake`, ON PURPOSE. They have no second
composition point. Declaring one would silently re-run `suite-real` and report
it as a fake column, which is `AD-F6` with the sign flipped: a duplicated cell
read as an independent measurement. The absence is the arm's architecture and
`divergence.py` reports it as `NOT_APPLICABLE`, never as `SURVIVED`.

DO NOT USE `run_controls.py` ON ANY OF THESE SUBJECTS. `FI-01-DF-01` is
BLOCKING and open: that driver's module purge is keyed on the name
`quota_ledger`, so on arm B `domain`, `file_journal` and `memory_journal` stay
cached and every mutant seeded in them runs against unmutated code -- 15 of 15
false SURVIVED, no error, looking exactly like a clean measurement. Every cell
FI-04 reports comes from `run_port_swap.py`, which runs each cell in a FRESH
INTERPRETER for exactly this reason.

    python3 examples/validation/ab/eval/run_arm_swap.py \
        --subject arm_b --cases <port corpus package> --out <path>.json
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
MEASURE = REPO_ROOT / "specs/results/scorecards/ports-as-adapters/GOAL-port-reach/measure"

sys.path.insert(0, str(MEASURE))

import run_port_swap  # noqa: E402  (path must be set first)

#: subject -> (catalogue FI-04 measures it against, suite composition points).
#:
#: The composition point is a module name importable from the tree copy.
#: `arm_b_fake` is copied into the copy by `run_port_swap.main()` itself and is
#: never written into the arm; see `arm_b_fake.py`'s own docstring.
FI04: dict[str, tuple[str, dict[str, str]]] = {
    "arm_a": ("adapter_faults_arm_a.toml", {"suite-real": "quota_ledger"}),
    "arm_b": (
        "adapter_faults_arm_b.toml",
        {"suite-real": "quota_ledger", "suite-fake": "arm_b_fake"},
    ),
    "arm_c": ("adapter_faults_arm_c.toml", {"suite-real": "quota_ledger"}),
}


def apply_fi04_catalogues() -> None:
    """Replace the two DATA fields, loudly. Nothing else is touched."""
    for subject, (catalogue, suites) in FI04.items():
        entry = run_port_swap.SUBJECTS[subject]
        entry["catalogues"] = [HERE / catalogue]
        entry["suites"] = dict(suites)
        print(
            f"FI-04: subject {subject!r} measured against {catalogue}; "
            f"suite columns {sorted(suites)}",
            file=sys.stderr,
        )
    print(
        "FI-04: run_port_swap.py is UNMODIFIED. Only `catalogues` and `suites` "
        "were replaced, and both are data. See this file's docstring.",
        file=sys.stderr,
    )


if __name__ == "__main__":
    apply_fi04_catalogues()
    raise SystemExit(run_port_swap.main())
