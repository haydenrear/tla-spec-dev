"""SI-05: a finding that targets this repository owes this repository a change.

The load-bearing claim is NOT "a warning appears". It is that the warning names
the findings that owe a change, stays silent about the ones that do not, and
**never turns into a gate** -- the close proceeds either way. The epic's
GOAL-no-new-gates is decided on exactly that, and the finding this ticket
consumes (SF-203) is a close that printed a warning nobody could act on.
"""

import json
import sys
from pathlib import Path

import pytest

from conftest import write_workflow_ledger_input

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "spec-double-2"
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

import skill_feedback as sf  # noqa: E402
import spec_evolution as evolution  # noqa: E402

MINIMAL_MODULE = """---- MODULE M ----
VARIABLE x
Init == x = 0
Next == x' = x
Spec == Init /\\ [][Next]_x
====
"""

#: Targets this repository and proposes nothing -- the case that must warn.
UNPROPOSED = (
    "\n### SF-901 — the close-out warning said nothing actionable\n"
    "- category: profile-schema-cli\n"
    "- target: scripts/spec_evolution.py::create_ticket_history_entry\n"
    "- observed_on: tla-spec-dev @ SI-05\n"
    "- evidence: specs/results/skill_feedback.md\n"
    "- severity: friction\n"
    "- root_cause: tool\n"
    "- recommendation: somebody should probably look at this\n"
    "- status: recorded-local\n"
)

#: Same target, but carries a disposition -- must NOT warn.
PROPOSED = (
    "\n### SF-902 — already disposed\n"
    "- category: profile-schema-cli\n"
    "- target: scripts/new_ticket_workflow.py::ticket_readme\n"
    "- observed_on: tla-spec-dev @ SI-05\n"
    "- evidence: specs/results/skill_feedback.md\n"
    "- severity: friction\n"
    "- root_cause: tool\n"
    "- recommendation: applied in this PR\n"
    "- skill_change: applied(abc1234)\n"
    "- status: applied\n"
)

#: Names something this repository does not carry -- must NOT warn.
FOREIGN = (
    "\n### SF-903 — not our surface\n"
    "- category: profile-schema-cli\n"
    "- target: the operator's shell prompt\n"
    "- observed_on: tla-spec-dev @ SI-05\n"
    "- evidence: specs/results/skill_feedback.md\n"
    "- severity: friction\n"
    "- root_cause: target\n"
    "- recommendation: nothing to do here\n"
    "- status: recorded-local\n"
)


def append(path: Path, block: str) -> None:
    path.write_text(path.read_text(encoding="utf-8") + block, encoding="utf-8")


def seed(specs: Path, *blocks: str) -> dict:
    record = sf.emit_skill_feedback(specs, scope="ticket", scope_id="SI-05", workflow="wf")
    path = sf.skill_feedback_path(specs)
    for block in blocks:
        append(path, block)
    return record


def test_a_finding_that_owes_a_change_and_proposes_none_is_named(tmp_path, capsys):
    record = seed(tmp_path / "specs", UNPROPOSED)

    evolution.print_skill_change_proposals(record)

    out = capsys.readouterr().out
    assert "SF-901" in out
    assert "proposes no change" in out
    assert "skill_change:" in out, "the warning must name the field that fixes it"


def test_the_close_proceeds_and_nothing_refuses(tmp_path, capsys):
    """GOAL-no-new-gates: this prints and returns. It raises nothing."""
    record = seed(tmp_path / "specs", UNPROPOSED)

    assert evolution.print_skill_change_proposals(record) is None

    out = capsys.readouterr().out
    assert "PROCEEDED" in out
    assert "never refused" in out


def test_a_disposed_finding_is_not_named(tmp_path, capsys):
    record = seed(tmp_path / "specs", PROPOSED)

    evolution.print_skill_change_proposals(record)

    assert "SF-902" not in capsys.readouterr().out


def test_a_finding_against_another_repository_is_not_named(tmp_path, capsys):
    record = seed(tmp_path / "specs", FOREIGN)

    evolution.print_skill_change_proposals(record)

    assert "SF-903" not in capsys.readouterr().out


def test_one_line_per_owing_finding(tmp_path, capsys):
    record = seed(tmp_path / "specs", UNPROPOSED, PROPOSED, FOREIGN)

    evolution.print_skill_change_proposals(record)

    out = capsys.readouterr().out
    assert len([line for line in out.splitlines() if line.strip().startswith("!")]) == 1
    assert "1 finding(s) target this repository" in out


def test_prose_only_is_not_a_proposal(tmp_path):
    """"Somebody should look at this" is the state this ticket exists to stop."""
    assert not evolution._finding_has_proposal(
        {"target": "scripts/x.py", "recommendation": "we should really fix this one day"}
    )
    assert evolution._finding_has_proposal(
        {"target": "scripts/x.py", "recommendation": "ticket https://example.invalid/1"}
    )
    assert evolution._finding_has_proposal(
        {"target": "scripts/x.py", "skill_change": "declined(target removed)"}
    )
    assert not evolution._finding_has_proposal(
        {"target": "scripts/x.py", "skill_change": "none"}
    )


def test_a_real_ticket_close_with_an_unproposed_finding_still_closes(tmp_path, capsys):
    """SI-05's declared local signal for GOAL-no-new-gates, as a test.

    A close carrying a finding that owes a change and proposes none completes,
    writes its history entry, and reports the warning. Nothing raises.
    """
    specs_dir = tmp_path / "specs"
    (specs_dir / "current").mkdir(parents=True)
    (specs_dir / "current" / "M.tla").write_text(MINIMAL_MODULE, encoding="utf-8")
    (specs_dir / "current" / "MC.cfg").write_text("SPECIFICATION Spec\n", encoding="utf-8")
    write_workflow_ledger_input(specs_dir)
    (specs_dir / "desired_program_model").mkdir(parents=True)
    (specs_dir / "desired_program_model" / "ticket_plan.yaml").write_text(
        "version: 1\nname: fixture-workflow\ntickets:\n  - id: T-1\n    status: done\n",
        encoding="utf-8",
    )

    result = evolution.create_ticket_history_entry(
        repo_root=tmp_path,
        spec_root=Path("specs"),
        ticket_ref="T-1",
        summary="close with an unproposed finding",
        result_paths=[],
    )
    append(sf.skill_feedback_path(specs_dir), UNPROPOSED)

    evolution.print_commit_recommendation(result)

    out = capsys.readouterr().out
    assert "SF-901" in out
    assert "PROCEEDED" in out
    manifest = json.loads((result.entry_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["ticket_id"] == "T-1", "the close completed and recorded its entry"
