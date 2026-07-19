"""Shared test helpers.

MF-019: closing a spec ticket requires a filled-in complexity ledger input.
That is deliberate and there is no bypass flag, so tests that exercise the
close path supply a real one. The helper below writes a ledger input that
passes every gate, which keeps unrelated close-path tests focused on what they
are actually testing while still going through the real gate.

Tests that exercise the ledger's own behavior live in test_complexity_ledger.py
and construct their inputs explicitly rather than using this helper.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


PASSING_LEDGER_INPUT = """\
retention:
  kill_rate:
    status: "pass"
    evidence: "results/kill-test.json"
  effect_conformance:
    status: "clean"
    evidence: "results/effect-conformance.txt"
  external_coverage:
    status: "pass"
    evidence: "results/external-coverage.txt"
justification: "Test fixture close; no model growth claimed."
refinement:
  searched: true
  outcome: "none"
  detail: ""
  measured: false
  applied: false
  approved_by: ""
transition_diff: ""
narrative: "Test fixture ledger narrative."
"""


def write_ticket_ledger_input(ticket_dir: Path) -> Path:
    """Fill the scaffolded per-ticket complexity ledger input."""
    path = Path(ticket_dir) / "results" / "complexity_ledger.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(PASSING_LEDGER_INPUT, encoding="utf-8")
    return path


def write_workflow_ledger_input(specs_dir: Path) -> Path:
    """Fill the workflow-close complexity ledger input."""
    path = Path(specs_dir) / "results" / "complexity_ledger_input.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(PASSING_LEDGER_INPUT, encoding="utf-8")
    return path
