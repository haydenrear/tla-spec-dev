"""MF-028 evidence: the projection detail and the negative controls.

The runner reports pass/fail; this prints the field-by-field comparison behind
that verdict, plus the deliberately-corrupted cases that must FAIL. Without the
negative controls a green run proves nothing -- see MF-016.
"""
from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path

TICKET = Path(__file__).resolve().parents[1]
CORPUS = Path(sys.argv[1])
WORK = Path(sys.argv[2])

sys.path.insert(0, str(TICKET / "current"))
sys.path.insert(0, str(CORPUS.parent))

import production_adapters as pa  # noqa: E402
from tlc_state_graph_cases.cases import CASES_BY_NAME  # noqa: E402


def show(case_name: str, adapter) -> None:
    case = CASES_BY_NAME[case_name]
    print(f"=== {case_name} :: {type(adapter).__name__} ===")
    print(f"  before : {json.dumps(case.before, sort_keys=True)}")
    print(f"  action : {case.input.action}  params={case.input.params}")
    print(f"  after  : {json.dumps(case.after, sort_keys=True)}")
    result = adapter.run(case, work_dir=WORK / case_name)
    out = result["semantic_output"]
    print(f"  replay : {json.dumps(out['replay'])}")
    print(f"  projected(observed from the real repository): {json.dumps(out['projected'], sort_keys=True)}")
    comparison = out["comparison"]
    print(f"  CHECKED   ({len(comparison['agreements'])}): {comparison['agreements']}")
    print(f"  UNCHECKED ({len(comparison['unchecked'])}): {comparison['unchecked']}")
    print(f"  MISMATCH  ({len(comparison['disagreements'])}): {comparison['disagreements']}")
    print()


def negative_controls() -> None:
    print("=== NEGATIVE CONTROLS (each MUST be rejected) ===")
    case = CASES_BY_NAME["case_0005_scaffold_project"]
    corruptions = [
        ("setup_phase", "setup_phase", 4),
        ("ticket_state", "ticket_state", {"cli_entrypoint": 2}),
        ("result.accepted", "result", {"accepted": False, "next": "RecordBudgets", "reason": "NoReason"}),
    ]
    for label, field, value in corruptions:
        after = dict(case.after)
        after[field] = value
        corrupted = dataclasses.replace(case, after=after)
        try:
            pa.ScaffoldProjectAdapter().run(corrupted, work_dir=WORK / f"neg_{label.replace('.', '_')}")
        except AssertionError as exc:
            print(f"  REJECTED {label}: {str(exc).split('-- ', 1)[1]}")
        else:
            print(f"  *** NOT REJECTED {label} -- the check is vacuous ***")
    print()
    print("  NOTE: `spec_root` has no negative control because it is UNCHECKED.")
    print("  Every case in the corpus carries params={}, so the adapter cannot")
    print("  know which root the model chose. An earlier draft read it from")
    print("  case.after and echoed it back; the corruption test passed anyway,")
    print("  which is how the tautology was found. See ScaffoldProjectAdapter.run.")


if __name__ == "__main__":
    show("case_0001_build_skill_cli", pa.BuildSkillCliAdapter())
    show("case_0005_scaffold_project", pa.ScaffoldProjectAdapter())
    negative_controls()
