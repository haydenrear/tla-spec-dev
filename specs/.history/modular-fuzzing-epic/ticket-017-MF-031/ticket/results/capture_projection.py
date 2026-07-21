#!/usr/bin/env python3
"""MF-031 evidence: field-by-field projection + negative controls per adapter.

Loads the two real generated cases the runner executed, runs each new adapter,
prints what was CHECKED / UNCHECKED, then runs deliberately corrupted
after-states and proves the check FAILS. A check that cannot fail is not a
check (MF-029's structural hazard).
"""
from __future__ import annotations

import copy
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
CORPUS = Path(sys.argv[1]) if len(sys.argv) > 1 else None
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "specs" / "tickets" / "MF-031" / "current"))
sys.path.insert(0, str(CORPUS.parent))

import production_adapters as pa  # noqa: E402
from tlc_state_graph_cases.cases import CASES_BY_NAME  # noqa: E402


def corrupt(case, mutate):
    """Return a shallow case clone whose `after` dict has been mutated."""
    after = copy.deepcopy(dict(case.after))
    mutate(after)
    return type(case)(**{**case.__dict__, "after": after}) if hasattr(case, "__dict__") else _replace_after(case, after)


def _replace_after(case, after):
    import dataclasses
    return dataclasses.replace(case, after=after)


def run_case(adapter, case):
    with tempfile.TemporaryDirectory(prefix="mf031-") as tmp:
        return adapter.run(case, work_dir=Path(tmp))


def show(title, adapter, case_name, controls):
    print("=" * 78)
    print(title)
    print("=" * 78)
    case = CASES_BY_NAME[case_name]
    print(f"case: {case_name}")
    print(f"before.ticket_state : {case.before['ticket_state']}")
    print(f"after.ticket_state  : {case.after['ticket_state']}")
    print(f"input.params        : {case.input.params}")
    ticket = pa.recover_ticket_except_index(case)
    print(f"recovered ticket (except-index on ticket_state) : {ticket!r}")

    result = run_case(adapter, case)
    comp = result["semantic_output"]["comparison"]
    print(f"\nPOSITIVE RUN (real generated case):")
    print(f"  CHECKED/agreements : {sorted(comp['agreements'])}")
    print(f"  UNCHECKED          : {sorted(comp['unchecked'])}")
    print(f"  disagreements      : {comp['disagreements']}")
    print(f"  observed ticket_state (from filesystem): {result['semantic_output']['projected']['ticket_state']}")
    assert comp["conformant"], "positive run should be conformant"
    print("  => conformant: PASS")

    print("\nNEGATIVE CONTROLS (deliberately wrong after-state must FAIL):")
    for label, mutate in controls:
        bad = corrupt(case, mutate)
        try:
            run_case(adapter, bad)
        except (AssertionError, pa.BeforeStateUnreachable) as exc:
            msg = str(exc)
            print(f"  [FAILS as required] {label}")
            print(f"      -> {type(exc).__name__}: {msg[:150]}")
        else:
            print(f"  [DID NOT FAIL] {label}  <-- BUG: check is vacuous")
            raise SystemExit(1)
    print()


def main() -> int:
    show(
        "UpdateTicketDesiredAdapter",
        pa.UpdateTicketDesiredAdapter(),
        "case_0178_update_ticket_desired",
        [
            ("after claims ticket stayed OPENED(1) not DESIRED_READY(2)",
             lambda a: a["ticket_state"].__setitem__("cli_entrypoint", pa.TICKET_OPENED)),
            ("after claims ticket jumped to CURRENT_READY(3)",
             lambda a: a["ticket_state"].__setitem__("cli_entrypoint", pa.TICKET_CURRENT_READY)),
            ("after claims a different lastCommand",
             lambda a: a.__setitem__("lastCommand", "WrongCommand")),
        ],
    )
    show(
        "UpdateTicketCurrentAdapter",
        pa.UpdateTicketCurrentAdapter(),
        "case_1621_update_ticket_current",
        [
            ("after claims ticket stayed DESIRED_READY(2) not CURRENT_READY(3)",
             lambda a: a["ticket_state"].__setitem__("cli_entrypoint", pa.TICKET_DESIRED_READY)),
            ("after claims a stale setup_phase(4)",
             lambda a: a.__setitem__("setup_phase", 4)),
            ("after claims a different lastCommand",
             lambda a: a.__setitem__("lastCommand", "UpdateTicketDesired")),
        ],
    )
    print("ALL POSITIVE RUNS CONFORMANT; ALL NEGATIVE CONTROLS FAILED AS REQUIRED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
