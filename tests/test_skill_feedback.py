"""MF-017: close-out emits the Phase 6 skill-feedback retro and records filing status.

The load-bearing claim of this ticket is not "a file appears". It is that the
template's fields can capture the inadequacies a real migration finds, and that
close-out can tell mechanically whether they were filed. The
``test_captures_real_epic_finding_*`` cases assert exactly that against the four
findings this epic produced before the template existed.
"""

import importlib

import importlib.util

from conftest import write_workflow_ledger_input
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import skill_feedback as sf  # noqa: E402


@pytest.fixture
def specs(tmp_path: Path) -> Path:
    return tmp_path / "specs"


def append_finding(path: Path, block: str) -> None:
    path.write_text(path.read_text(encoding="utf-8") + block, encoding="utf-8")


def set_declared_status(path: Path, status: str) -> None:
    text = path.read_text(encoding="utf-8")
    head, _, tail = text.rpartition("- feedback_status: unreviewed")
    path.write_text(head + f"- feedback_status: {status}" + tail, encoding="utf-8")


# --------------------------------------------------------------------------
# Emission
# --------------------------------------------------------------------------


def test_close_out_emits_template_with_the_four_prompt_sections(specs: Path) -> None:
    record = sf.emit_skill_feedback(specs, scope="ticket", scope_id="MF-017", workflow="wf")

    path = sf.skill_feedback_path(specs)
    assert path.is_file()
    assert path == specs / "results" / "skill_feedback.md"
    assert record["template_emitted"] is True

    text = path.read_text(encoding="utf-8")
    assert [slug for slug, _ in sf.PROMPT_SECTIONS] == record["prompt_sections"]
    assert len(sf.PROMPT_SECTIONS) == 4
    for slug, title in sf.PROMPT_SECTIONS:
        assert slug in text
        assert title in text


def test_template_instructs_filing_against_spec_double_compiler(specs: Path) -> None:
    sf.emit_skill_feedback(specs, scope="ticket", scope_id="MF-017", workflow="wf")
    text = sf.skill_feedback_path(specs).read_text(encoding="utf-8")

    assert "spec-double-compiler" in text
    assert "gh issue create" in text
    assert "ticket or PR" in text


def test_second_close_appends_and_never_clobbers_filled_content(specs: Path) -> None:
    sf.emit_skill_feedback(specs, scope="ticket", scope_id="MF-017", workflow="wf")
    path = sf.skill_feedback_path(specs)
    append_finding(path, "\n### SF-001 — human wrote this\n- category: surviving-mutants\n")

    second = sf.emit_skill_feedback(specs, scope="ticket", scope_id="MF-014", workflow="wf")

    text = path.read_text(encoding="utf-8")
    assert second["template_emitted"] is False, "template must be written once, then appended to"
    assert "human wrote this" in text, "an existing finding was destroyed by the next close"
    assert "Close-out ticket MF-017" in text
    assert "Close-out ticket MF-014" in text
    assert second["close_out_entries"] == 2


def test_workflow_close_uses_the_same_document(specs: Path) -> None:
    sf.emit_skill_feedback(specs, scope="ticket", scope_id="MF-017", workflow="wf")
    record = sf.emit_skill_feedback(specs, scope="workflow", scope_id="wf", workflow="wf")

    assert record["close_out_entry"] == "Close-out workflow wf"
    assert record["template_emitted"] is False


def test_deferred_validations_are_recorded_on_the_close_out_entry(specs: Path) -> None:
    record = sf.emit_skill_feedback(
        specs,
        scope="ticket",
        scope_id="MF-017",
        workflow="wf",
        deferred=["mutation kill test -> MF-023"],
    )
    text = sf.skill_feedback_path(specs).read_text(encoding="utf-8")
    assert "deferred_validation: mutation kill test -> MF-023" in text
    assert record["deferred_validation"] == ["mutation kill test -> MF-023"]


# --------------------------------------------------------------------------
# Filing status
# --------------------------------------------------------------------------


def test_unreviewed_close_out_is_not_resolved(specs: Path) -> None:
    record = sf.emit_skill_feedback(specs, scope="ticket", scope_id="MF-017", workflow="wf")
    assert record["declared_status"] == "unreviewed"
    assert record["resolved"] is False
    assert record["filed"] is False


def test_searched_found_none_is_a_first_class_answer(specs: Path) -> None:
    sf.emit_skill_feedback(specs, scope="ticket", scope_id="MF-017", workflow="wf")
    path = sf.skill_feedback_path(specs)
    set_declared_status(path, "none-found")

    status = sf.filing_status(path.read_text(encoding="utf-8"))
    assert status["resolved"] is True
    assert status["findings_total"] == 0
    assert status["filed"] is False


def test_finding_without_a_recommendation_is_reported_unfiled(specs: Path) -> None:
    sf.emit_skill_feedback(specs, scope="ticket", scope_id="MF-017", workflow="wf")
    path = sf.skill_feedback_path(specs)
    set_declared_status(path, "items-recorded")
    append_finding(
        path,
        "\n### SF-001 — generator cannot reach the guard\n"
        "- category: surviving-mutants\n"
        "- recommendation: (none yet)\n"
        "- status: open\n",
    )

    status = sf.filing_status(path.read_text(encoding="utf-8"))
    assert status["findings_total"] == 1
    assert status["findings_unfiled"] == ["SF-001"]
    assert status["resolved"] is False


def test_filed_finding_records_where_it_was_filed(specs: Path) -> None:
    sf.emit_skill_feedback(specs, scope="ticket", scope_id="MF-017", workflow="wf")
    path = sf.skill_feedback_path(specs)
    set_declared_status(path, "items-recorded")
    append_finding(
        path,
        "\n### SF-001 — generator cannot reach the guard\n"
        "- category: surviving-mutants\n"
        "- recommendation: ticket https://github.com/haydenrear/tla-spec-dev/issues/99\n"
        "- status: filed\n",
    )

    status = sf.filing_status(path.read_text(encoding="utf-8"))
    assert status["filed"] is True
    assert status["resolved"] is True
    assert status["findings_filed"] == 1
    assert status["filed_where"] == ["https://github.com/haydenrear/tla-spec-dev/issues/99"]


def test_status_filed_without_a_reference_does_not_count_as_filed(specs: Path) -> None:
    """"filed" with nowhere to point at is the failure mode this loop exists to stop."""
    sf.emit_skill_feedback(specs, scope="ticket", scope_id="MF-017", workflow="wf")
    path = sf.skill_feedback_path(specs)
    append_finding(
        path,
        "\n### SF-001 — vague\n- category: surviving-mutants\n"
        "- recommendation: TBD\n- status: filed\n",
    )

    status = sf.filing_status(path.read_text(encoding="utf-8"))
    assert status["findings_unfiled"] == ["SF-001"]
    assert status["resolved"] is False


def test_wontfix_finding_does_not_block_resolution(specs: Path) -> None:
    sf.emit_skill_feedback(specs, scope="ticket", scope_id="MF-017", workflow="wf")
    path = sf.skill_feedback_path(specs)
    append_finding(
        path,
        "\n### SF-001 — declined\n- category: friction\n"
        "- recommendation: none\n- status: wontfix\n",
    )

    status = sf.filing_status(path.read_text(encoding="utf-8"))
    assert status["findings_unfiled"] == []
    assert status["resolved"] is True


def test_worked_examples_are_excluded_from_filing_status(specs: Path) -> None:
    """The shipped SF-000x calibration examples must not masquerade as real findings."""
    record = sf.emit_skill_feedback(specs, scope="ticket", scope_id="MF-017", workflow="wf")
    text = sf.skill_feedback_path(specs).read_text(encoding="utf-8")
    assert "SF-000a" in text and "SF-000d" in text
    assert record["findings_total"] == 0


# --------------------------------------------------------------------------
# The template must be able to capture what this epic actually found.
# Each case reproduces a real finding recorded in ticket_plan.yaml notes.
# --------------------------------------------------------------------------

REAL_EPIC_FINDINGS = {
    # 2026-07-18: the withdrawn -13.1% projection. A "complexity reduction"
    # that only reproduced by deleting a legitimate idempotent transition.
    "projected-reduction-deleted-behavior": (
        "\n### SF-001 — projected complexity reduction required deleting real behavior\n"
        "- category: budget-and-metric\n"
        "- target: scripts/analyze_complexity.py projected-reduction reporting\n"
        "- observed_on: tla-spec-dev @ MF-020\n"
        "- evidence: specs/tickets/MF-020/results/tlc-current.txt\n"
        "- severity: wrong-result\n"
        "- root_cause: tool\n"
        "- gated_quantity: distinct reachable states\n"
        "- measured_quantity: generated states\n"
        "- metric_blind_spot: deleted self-loops score as re-representation wins\n"
        "- workaround_applied: transition-level diff by hand; projection withdrawn\n"
        "- recommendation: ticket https://github.com/haydenrear/tla-spec-dev/issues/31\n"
        "- status: filed\n",
        {"category": "budget-and-metric", "root_cause": "tool", "severity": "wrong-result"},
    ),
    # GitHub #22 / MF-021: promotion rmtree'd specs/current and destroyed
    # regression tests on three separate closes.
    "promotion-destroyed-regression-tests": (
        "\n### SF-002 — ticket-close promotion destroyed files unique to specs/current\n"
        "- category: profile-schema-cli\n"
        "- target: scripts/spec_evolution.py::replace_tree\n"
        "- observed_on: tla-spec-dev @ MF-012, MF-020, MF-021\n"
        "- evidence: tests/test_promotion_preserves_current.py\n"
        "- severity: silent-data-loss\n"
        "- root_cause: tool\n"
        "- surface: tla-spec-dev close ticket\n"
        "- forced_workaround: restore deleted regression tests from git history\n"
        "- data_loss: yes\n"
        "- recommendation: ticket https://github.com/haydenrear/tla-spec-dev/issues/22\n"
        "- status: filed\n",
        {"category": "profile-schema-cli", "root_cause": "tool", "severity": "silent-data-loss"},
    ),
    # The PATH wrapper that ran pre-epic code for the entire epic.
    "path-wrapper-ran-pre-epic-code": (
        "\n### SF-003 — PATH wrapper executed pre-epic code for the whole epic\n"
        "- category: profile-schema-cli\n"
        "- target: tla-spec-dev PATH wrapper -> ~/.skill-manager/skills/spec-double-compiler\n"
        "- observed_on: tla-spec-dev @ modular-fuzzing epic\n"
        "- evidence: specs/desired_program_model/ticket_plan.yaml toolchain_rule\n"
        "- severity: wrong-result\n"
        "- root_cause: tool\n"
        "- surface: skill installation / PATH shim\n"
        "- forced_workaround: pin every lifecycle command to python3 scripts/tla_spec_dev.py\n"
        "- data_loss: yes\n"
        "- recommendation: ticket https://github.com/haydenrear/tla-spec-dev/issues/32\n"
        "- status: filed\n",
        {"category": "profile-schema-cli", "root_cause": "tool", "severity": "wrong-result"},
    ),
    # MF-011 -> MF-022: the bound gate compared incommensurable quantities.
    # Note root_cause: spec — the implementation was correct.
    "bound-gate-incommensurable": (
        "\n### SF-004 — bound gate compared incommensurable quantities\n"
        "- category: budget-and-metric\n"
        "- target: scripts/analyze_complexity.py state-space bound gate\n"
        "- observed_on: tla-spec-dev @ MF-011\n"
        "- evidence: specs/tickets/MF-011/results/analyze-complexity.txt\n"
        "- severity: blocks-migration\n"
        "- root_cause: spec\n"
        "- budget_key: max_distinct_states\n"
        "- default_value: 50000\n"
        "- value_used: added max_state_space_bound\n"
        "- gated_quantity: static state-space upper bound 1179648\n"
        "- measured_quantity: reachable distinct states 2923\n"
        "- metric_blind_spot: the tool's own recommended optimum still failed the gate\n"
        "- workaround_applied: none\n"
        "- recommendation: ticket https://github.com/haydenrear/tla-spec-dev/issues/28\n"
        "- status: filed\n",
        {"category": "budget-and-metric", "root_cause": "spec", "severity": "blocks-migration"},
    ),
}


@pytest.mark.parametrize("name", sorted(REAL_EPIC_FINDINGS))
def test_captures_real_epic_finding(specs: Path, name: str) -> None:
    """Each of the four findings this epic produced round-trips through the template."""
    block, expected = REAL_EPIC_FINDINGS[name]
    sf.emit_skill_feedback(specs, scope="ticket", scope_id="MF-017", workflow="wf")
    path = sf.skill_feedback_path(specs)
    set_declared_status(path, "items-recorded")
    append_finding(path, block)

    status = sf.filing_status(path.read_text(encoding="utf-8"))
    assert status["findings_total"] == 1
    (finding,) = status["findings"]

    for key, value in expected.items():
        assert finding[key] == value, f"{name}: {key}"
    assert finding["category"] in sf.CATEGORY_SLUGS
    assert finding["severity"] in sf.SEVERITIES
    assert finding["root_cause"] in sf.ROOT_CAUSES
    assert finding["filed"] is True
    assert finding["reference"].startswith("https://")
    assert finding["target"] and finding["observed_on"] and finding["evidence"]
    assert status["resolved"] is True


def test_captures_all_four_real_findings_together(specs: Path) -> None:
    sf.emit_skill_feedback(specs, scope="ticket", scope_id="MF-017", workflow="wf")
    path = sf.skill_feedback_path(specs)
    set_declared_status(path, "items-recorded")
    for block, _ in REAL_EPIC_FINDINGS.values():
        append_finding(path, block)

    status = sf.filing_status(path.read_text(encoding="utf-8"))
    assert status["findings_total"] == 4
    assert status["findings_filed"] == 4
    assert status["resolved"] is True
    assert len(set(status["filed_where"])) == 4
    # Both "the tool is broken" and "the spec was wrong" are representable.
    assert {f["root_cause"] for f in status["findings"]} == {"tool", "spec"}
    # All four required prompt categories are exercised by real material.
    assert {f["category"] for f in status["findings"]} == {"budget-and-metric", "profile-schema-cli"}


# --------------------------------------------------------------------------
# History integration
# --------------------------------------------------------------------------


def load_spec_evolution():
    """Import the real close path (scripts/ is already on sys.path above)."""
    return importlib.import_module("spec_evolution")


def test_history_manifest_records_feedback_filing_status(tmp_path: Path) -> None:
    """The append-only history entry must say whether feedback was filed and where."""
    evolution = load_spec_evolution()

    specs_dir = tmp_path / "specs"
    (specs_dir / "current").mkdir(parents=True)
    (specs_dir / "current" / "M.tla").write_text("---- MODULE M ----\n====\n", encoding="utf-8")
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
        summary="fixture close",
        result_paths=[],
    )

    assert result.skill_feedback is not None
    manifest = json.loads((result.entry_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["skill_feedback"]["path"].endswith("results/skill_feedback.md")
    assert manifest["skill_feedback"]["close_out_entry"] == "Close-out ticket T-1"
    assert manifest["feedback_filed"] is False
    assert manifest["feedback_filed_where"] == []
    assert Path(manifest["skill_feedback"]["path"]).is_file()


def test_history_manifest_records_where_feedback_was_filed(tmp_path: Path) -> None:
    evolution = load_spec_evolution()

    specs_dir = tmp_path / "specs"
    (specs_dir / "current").mkdir(parents=True)
    (specs_dir / "current" / "M.tla").write_text("---- MODULE M ----\n====\n", encoding="utf-8")
    (specs_dir / "current" / "MC.cfg").write_text("SPECIFICATION Spec\n", encoding="utf-8")
    write_workflow_ledger_input(specs_dir)
    (specs_dir / "desired_program_model").mkdir(parents=True)
    (specs_dir / "desired_program_model" / "ticket_plan.yaml").write_text(
        "version: 1\nname: fixture-workflow\ntickets:\n  - id: T-1\n    status: done\n"
        "  - id: T-2\n    status: done\n",
        encoding="utf-8",
    )

    evolution.create_ticket_history_entry(
        repo_root=tmp_path, spec_root=Path("specs"), ticket_ref="T-1",
        summary="first close", result_paths=[],
    )
    feedback = sf.skill_feedback_path(specs_dir)
    set_declared_status(feedback, "items-recorded")
    append_finding(feedback, REAL_EPIC_FINDINGS["promotion-destroyed-regression-tests"][0])

    result = evolution.create_ticket_history_entry(
        repo_root=tmp_path, spec_root=Path("specs"), ticket_ref="T-2",
        summary="second close", result_paths=[],
    )

    manifest = json.loads((result.entry_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["feedback_filed"] is True
    assert manifest["feedback_filed_where"] == ["https://github.com/haydenrear/tla-spec-dev/issues/22"]


def test_no_skill_feedback_opt_out(tmp_path: Path) -> None:
    evolution = load_spec_evolution()

    specs_dir = tmp_path / "specs"
    (specs_dir / "current").mkdir(parents=True)
    (specs_dir / "current" / "M.tla").write_text("---- MODULE M ----\n====\n", encoding="utf-8")
    (specs_dir / "current" / "MC.cfg").write_text("SPECIFICATION Spec\n", encoding="utf-8")
    write_workflow_ledger_input(specs_dir)
    (specs_dir / "desired_program_model").mkdir(parents=True)
    (specs_dir / "desired_program_model" / "ticket_plan.yaml").write_text(
        "version: 1\nname: fixture-workflow\ntickets:\n  - id: T-1\n    status: done\n",
        encoding="utf-8",
    )

    result = evolution.create_ticket_history_entry(
        repo_root=tmp_path, spec_root=Path("specs"), ticket_ref="T-1",
        summary="fixture close", result_paths=[], emit_feedback=False,
    )

    assert result.skill_feedback is None
    assert not sf.skill_feedback_path(specs_dir).exists()
