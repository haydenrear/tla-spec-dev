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

EVERY RUN CARRIES ITS CONTROLS, AND THE EXIT CODE IS NOT THE CONTROL STATE.
`FI-02-DF-02`: `run_port_swap.py` computes `control_red`, writes it into its
JSON, and EXITS 0 ANYWAY -- its sibling `run_controls.py` exits nonzero for the
same condition. `swap-reference_ports.json` from the last epic carries four
`control_red` entries for `PA-M14`, each with `witness_ran_accepting: 294`, and
that run exited 0. So this file re-reads its own artifact after the run and
prints the control state, and every number FI-04 reports is quoted beside the
`control_red` list read OUT OF THE JSON rather than beside an exit code.

The first run of these catalogues carried NO control row at all, and the driver
printed "no control's declared role was violated on any instrument that reached
it" -- which is R2's own failure mode, a control statement that cannot fail
because there is nothing to violate. The per-arm control catalogues below are
the fix. They are the predecessors' own files, unchanged:

    arm A   controls_arm_a.toml            N01, negative, green at PA-06
    arm B   controls_arm_b.toml            N01, negative
            controls_port_region_arm_b.toml FI-01's FI-M15, POSITIVE and
                                            in-region -- the only positive
                                            control on any arm in this project
    arm C   controls_arm_c.toml            N01, negative

Arms A and C get no positive control and that is not an omission: FI-01
enumerated the trees and only `reference_ports` and arm B declare a port, so
only they have a port region to seed one inside. Their SURVIVED cells are
floors and FI-04 says so rather than quietly reading them as counts.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
MEASURE = REPO_ROOT / "specs/results/scorecards/ports-as-adapters/GOAL-port-reach/measure"
RERUN = REPO_ROOT / "specs/results/scorecards/hexagonal-prompting-rerun/measure"
PA06 = REPO_ROOT / "specs/results/scorecards/ports-as-adapters/measure"

sys.path.insert(0, str(MEASURE))
# `pa06_arm_c_binding` lives here rather than beside the other two; PA-06's own
# SUBJECTS comment says the CALLER puts this directory on the path. The first
# FI-04 run did not, and the driver reported CONTROL_RED on all three of arm C's
# corpus columns rather than a false SURVIVED. That is the instrument working.
sys.path.insert(0, str(PA06))
# ...and the SUBPROCESS needs it too. `run_port_swap.run_corpus` launches
# `port_corpus_run.py` with a copy of `os.environ`, so an in-process `sys.path`
# does not reach the interpreter that imports the binding. Putting both
# directories on PYTHONPATH here is what makes the run reproducible from one
# command line, which is the property PA-06's SUBJECTS comment asks the caller
# for and the property the first FI-04 run did not have.
os.environ["PYTHONPATH"] = os.pathsep.join(
    [str(MEASURE), str(PA06), *([os.environ["PYTHONPATH"]] if os.environ.get("PYTHONPATH") else [])]
)

import run_port_swap  # noqa: E402  (path must be set first)

#: subject -> (catalogues FI-04 measures it against, suite composition points).
#:
#: The composition point is a module name importable from the tree copy.
#: `arm_b_fake` is copied into the copy by `run_port_swap.main()` itself and is
#: never written into the arm; see `arm_b_fake.py`'s own docstring.
FI04: dict[str, tuple[list[Path], dict[str, str]]] = {
    "arm_a": (
        [HERE / "adapter_faults_arm_a.toml", RERUN / "controls_arm_a.toml"],
        {"suite-real": "quota_ledger"},
    ),
    "arm_b": (
        [
            HERE / "adapter_faults_arm_b.toml",
            RERUN / "controls_arm_b.toml",
            HERE / "controls_port_region_arm_b.toml",
        ],
        {"suite-real": "quota_ledger", "suite-fake": "arm_b_fake"},
    ),
    "arm_c": (
        [HERE / "adapter_faults_arm_c.toml", PA06 / "controls_arm_c.toml"],
        {"suite-real": "quota_ledger"},
    ),
}


def apply_fi04_catalogues() -> None:
    """Replace the two DATA fields, loudly. Nothing else is touched."""
    for subject, (catalogues, suites) in FI04.items():
        entry = run_port_swap.SUBJECTS[subject]
        entry["catalogues"] = list(catalogues)
        entry["suites"] = dict(suites)
        print(
            f"FI-04: subject {subject!r} measured against "
            f"{[path.name for path in catalogues]}; suite columns {sorted(suites)}",
            file=sys.stderr,
        )
    print(
        "FI-04: run_port_swap.py is UNMODIFIED. Only `catalogues` and `suites` "
        "were replaced, and both are data. See this file's docstring.",
        file=sys.stderr,
    )


def report_control_state(out: Path) -> int:
    """Read `control_red` OUT OF THE ARTIFACT. FI-02-DF-02.

    The driver's own exit code does not carry this and never has. Returning
    nonzero here is FI-04 declining to inherit that, for its own runs only --
    `run_port_swap.py` is not modified and other tickets' exit codes are
    unaffected.
    """
    report = json.loads(out.read_text(encoding="utf-8"))
    red = report.get("control_red", [])
    declared = sorted(
        row for row, record in report["per_mutant"].items() if record.get("control_role")
    )
    print("\nFI-04 CONTROL STATE, read from the artifact rather than from an exit code:")
    if not declared:
        print(
            "  RED -- NO ROW IN THIS RUN DECLARES A CONTROL ROLE. 'No control was "
            "violated' is vacuous when there is no control, which is R2's own failure "
            "mode. Every kill number from this run is a floor."
        )
        return 1
    print(f"  controls present: {declared}")
    if red:
        for entry in red:
            print(
                f"  RED  {entry['mutant']} on {entry['instrument']}: cell "
                f"{entry['observed_cell']}, must be {entry['must_be']}, "
                f"{entry['witness_ran_accepting']} accepting "
                f"{entry['witness_action']} case(s) executed"
            )
        print(
            f"  {len(red)} RED control/instrument pair(s). EVERY SURVIVED CELL FROM "
            "THOSE INSTRUMENTS IS A FLOOR."
        )
        return 1
    print("  no declared role was violated on any instrument its own witness proves it reached.")
    return 0


if __name__ == "__main__":
    apply_fi04_catalogues()
    status = run_port_swap.main()
    out = Path(sys.argv[sys.argv.index("--out") + 1])
    raise SystemExit(status or report_control_state(out))
