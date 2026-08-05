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

# MF-026: the workflow close records a coverage audit verdict. It REFUSED on
# anything but `pass` until 2026-08-04, which is why this fixture supplies a
# real one; the refusal is retired and the fixture is kept, because a workflow
# close carrying a real verdict is still the case worth exercising and because
# a fixture that stopped supplying one would silently stop covering the
# recording path. Deliberately appended only to the WORKFLOW fixture: a ticket
# close legitimately carries `not_run`, and writing a `pass` into the ticket
# fixture would hide that asymmetry from the very tests meant to exercise it.
COVERAGE_AUDIT_PASS = """\
coverage_audit:
  status: "pass"
  report: "results/coverage_audit_report.md"
  in_scope_gaps: 0
  scope_source: "ticket_plan.yaml (test fixture)"
"""


def write_ticket_ledger_input(ticket_dir: Path) -> Path:
    """Fill the scaffolded per-ticket complexity ledger input.

    No coverage-audit block: at ticket scope the audit is legitimately
    `not_run`, which is recorded and reported but does not refuse.
    """
    path = Path(ticket_dir) / "results" / "complexity_ledger.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(PASSING_LEDGER_INPUT, encoding="utf-8")
    return path


def write_workflow_ledger_input(specs_dir: Path) -> Path:
    """Fill the workflow-close complexity ledger input, coverage audit included."""
    path = Path(specs_dir) / "results" / "complexity_ledger_input.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(PASSING_LEDGER_INPUT + COVERAGE_AUDIT_PASS, encoding="utf-8")
    return path
