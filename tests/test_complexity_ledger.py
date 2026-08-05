"""MF-019 -- tests for the mechanized standing objective.

The anti-gaming cases here are NOT hypothetical. Each of the four scenarios in
`TestHistoricalCases` is a real event from this epic's own history, with the
measured figures the ticket recorded. They are the regression suite for the
mechanization: the ledger must reach the same verdict a careful human reached
by hand, on the same numbers.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import complexity_ledger as cl


def make_input(**overrides):
    """A ledger input that PASSES every gate, as the base for negative tests.

    CD-09: the validated-refactor basis is part of the all-green base -- it is
    what licenses a decrease. The fuzzing-era retention block stays present
    (recorded, non-gating) with the measured verdicts the manual ledgers used.
    """
    payload = {
        "retention": {
            "kill_rate": {"status": "pass", "evidence": "results/kill-test.json"},
            "effect_conformance": {"status": "clean", "evidence": "results/effects.txt"},
            "external_coverage": {"status": "pass", "evidence": "results/coverage.txt"},
        },
        "validated_refactor": {
            "tlc_before": {"status": "green", "evidence": "results/tlc_before.txt"},
            "tlc_after": {"status": "green", "evidence": "results/tlc_current.txt"},
            "behavior_tests": {"status": "pass", "evidence": "results/repo_unit_tests.txt"},
            "descriptor_comparison": {
                "status": "recorded",
                "evidence": "results/model_before_after_descriptors.txt",
            },
        },
        "justification": "",
        "refinement": {"searched": True, "outcome": "none"},
        "narrative": "results/complexity-ledger.md",
    }
    payload.update(overrides)
    return payload


def metrics(**overrides):
    base = {
        "variables": 9,
        "actions": 14,
        "bound": 699840,
        "distinct_states": 231621,
        "generated_states": 5619356,
        "depth": 25,
    }
    base.update(overrides)
    return base


def previous(**overrides):
    return {"scope_id": "PREV", "verdict": "recorded", "metrics": metrics(**overrides)}


def _write_partially_resolved_model(tmp_path: Path) -> tuple[Path, Path]:
    """A two-variable model where the TypeInvariant sizes only one of them.

    RP-04 / CM-01-DF-03: the smallest shape that reproduces the defect the
    shipped example hit at 1-of-10 -- a bound of 2 that is a product over half
    the representation.
    """
    tla = tmp_path / "Partial.tla"
    tla.write_text(
        "---- MODULE Partial ----\n"
        "VARIABLES flag, free\n"
        "TypeInvariant ==\n"
        "  /\\ flag \\in BOOLEAN\n"
        "Init == /\\ flag = FALSE /\\ free = 0\n"
        "Step == /\\ flag' = ~flag /\\ free' = free + 1\n"
        "Next == Step\n"
        "====\n",
        encoding="utf-8",
    )
    cfg = tmp_path / "MC.cfg"
    cfg.write_text("INIT Init\nNEXT Next\nINVARIANT TypeInvariant\n", encoding="utf-8")
    return tla, cfg


def evaluate(current, prev, ledger_input):
    return cl.evaluate(
        scope="ticket",
        scope_id="MF-TEST",
        workflow="wf",
        metrics=current,
        ledger_input=ledger_input,
        previous=prev,
    )


# ---------------------------------------------------------------------------
# Delta reporting
# ---------------------------------------------------------------------------


class TestDelta:
    def test_zero_delta_is_accepted_and_reported_as_zero(self):
        verdict = evaluate(metrics(), previous(), make_input())
        assert not verdict.rejected
        assert verdict.entry["delta"]["direction"] == "zero"

    def test_first_entry_establishes_a_baseline(self):
        verdict = evaluate(metrics(), None, make_input())
        assert not verdict.rejected
        assert verdict.entry["delta"]["direction"] == "baseline"

    def test_delta_is_always_recorded_jointly_with_retention(self):
        """The doctrine's core requirement: never one without the other.

        CD-09: the joint requirement is the validated-refactor basis; the
        fuzzing-era members are recorded right beneath it, non-gating.
        """
        verdict = evaluate(metrics(), previous(), make_input())
        assert verdict.entry["delta"]
        assert set(verdict.entry["retention"]) == set(cl.RETENTION_MEMBERS)
        assert set(verdict.entry["validated_refactor"]) == set(cl.VALIDATED_REFACTOR_MEMBERS)
        # And in the human-readable report, adjacently.
        report = cl.render_report(verdict)
        assert "delta:" in report and "validated-refactor basis (joint requirement" in report
        assert "retention (fuzzing-era, experimental" in report

    def test_percentages_are_recorded(self):
        verdict = evaluate(metrics(distinct_states=171039), previous(), make_input())
        assert verdict.entry["delta"]["metrics"]["distinct_states"]["percent"] == -26.2

    def test_rejected_entries_do_not_become_the_baseline(self):
        """A refused close must not quietly reset the reference point."""
        ledger = {
            "entries": [
                {"scope_id": "GOOD", "verdict": "recorded", "metrics": metrics()},
                {"scope_id": "BAD", "verdict": "rejected", "metrics": metrics(bound=1)},
            ]
        }
        assert cl.previous_entry(ledger)["scope_id"] == "GOOD"


# ---------------------------------------------------------------------------
# Increase requires justification
# ---------------------------------------------------------------------------


class TestIncreaseJustification:
    def test_increase_without_justification_is_refused(self):
        verdict = evaluate(metrics(), previous(variables=8, bound=174960), make_input())
        assert verdict.rejected
        assert any("INCREASED" in e and "no recorded justification" in e for e in verdict.errors)

    def test_increase_with_justification_is_allowed_and_still_recorded(self):
        """The justification documents behavior; it does not erase the number."""
        verdict = evaluate(
            metrics(),
            previous(variables=8, bound=174960),
            make_input(justification="kill_test carries the mutation verdict, oracle 4."),
        )
        assert not verdict.rejected
        assert verdict.entry["delta"]["direction"] == "increase"
        assert verdict.entry["delta"]["metrics"]["variables"]["delta"] == 1
        assert verdict.entry["justification"]

    def test_template_sentinel_does_not_count_as_a_justification(self):
        verdict = evaluate(
            metrics(),
            previous(variables=8, bound=174960),
            make_input(justification="TODO"),
        )
        assert verdict.rejected


# ---------------------------------------------------------------------------
# Anti-gaming: a decrease with degraded retention is REJECTED
# ---------------------------------------------------------------------------


class TestAntiGaming:
    """CD-09: the anti-gaming gate reads the validated-refactor basis. A
    reduction still cannot be bought with silence -- what changed is WHICH
    evidence licenses it (TLC before/after, behavior tests, descriptor
    comparison) rather than the demoted fuzzing-era members."""

    def test_decrease_without_the_validated_refactor_basis_is_rejected(self):
        """Leaving the block out entirely cannot skip the gate."""
        payload = make_input()
        del payload["validated_refactor"]
        verdict = evaluate(metrics(distinct_states=171039, bound=524880), previous(), payload)
        assert verdict.rejected
        assert any("UNVERIFIED" in e and "validated-refactor" in e for e in verdict.errors)

    def test_decrease_with_unknown_basis_member_is_rejected(self):
        """Absent evidence is not passing evidence."""
        payload = make_input()
        payload["validated_refactor"]["tlc_before"]["status"] = "unknown"
        verdict = evaluate(metrics(bound=524880), previous(), payload)
        assert verdict.rejected
        assert any("UNVERIFIED" in e for e in verdict.errors)

    def test_missing_fuzzing_member_no_longer_rejects_but_stays_visible(self):
        """CD-09 flips the old missing-retention rejection: the fuzzing-era
        members are recorded (unverified when absent), never gating."""
        verdict = evaluate(metrics(bound=524880), previous(), make_input(retention={}))
        assert not verdict.rejected, verdict.errors
        assert set(verdict.entry["retention"]) == set(cl.RETENTION_MEMBERS)
        assert all(
            member["classification"] == "unverified"
            for member in verdict.entry["retention"].values()
        )
        assert any("non-gating" in n for n in verdict.notes)

    def test_unobservable_is_still_not_clean_in_the_record(self):
        """MF-027: the effect oracle refuses what it cannot see. The member no
        longer gates a decrease, but its classification never softens."""
        payload = make_input()
        payload["retention"]["effect_conformance"]["status"] = "unobservable"
        verdict = evaluate(metrics(bound=524880), previous(), payload)
        assert not verdict.rejected, verdict.errors
        member = cl.parse_retention(payload["retention"])["effect_conformance"]
        assert member.degraded and not member.retained
        assert "unobservable IS NOT clean" in member.describe()
        assert verdict.entry["retention"]["effect_conformance"]["classification"] == "degraded"

    def test_unrecognized_basis_verdict_refuses_rather_than_passes(self):
        """MF-027's polarity lesson: pass only on positive evidence."""
        payload = make_input()
        payload["validated_refactor"]["behavior_tests"]["status"] = "probably_fine"
        verdict = evaluate(metrics(bound=524880), previous(), payload)
        assert verdict.rejected
        member = cl.parse_validated_refactor(payload["validated_refactor"])["behavior_tests"]
        assert member.unverified and not member.retained

    def test_degraded_basis_alone_does_not_block_a_zero_delta(self):
        """The anti-gaming rule targets reductions bought with behavior.

        TLC and behavior-test verdicts are owned by their own validation steps;
        this gate fires on the CONJUNCTION with a decrease, so it must not
        silently become a second TLC gate.
        """
        payload = make_input()
        payload["validated_refactor"]["tlc_after"]["status"] = "fail"
        verdict = evaluate(metrics(), previous(), payload)
        assert not verdict.rejected

    def test_there_is_no_override_for_the_anti_gaming_gate(self):
        payload = make_input(override=True, allow_degraded=True, force=True)
        payload["validated_refactor"]["behavior_tests"]["status"] = "fail"
        verdict = evaluate(metrics(bound=524880), previous(), payload)
        assert verdict.rejected


# ---------------------------------------------------------------------------
# The self-loop red flag (MF-020)
# ---------------------------------------------------------------------------


class TestSelfLoopRedFlag:
    def test_generated_drop_at_constant_distinct_is_rejected(self):
        verdict = evaluate(
            metrics(generated_states=3184),
            previous(generated_states=3664),
            make_input(),
        )
        assert verdict.rejected
        assert any("STRUCTURALLY BLIND" in e for e in verdict.errors)

    def test_red_flag_is_accepted_only_with_an_inspected_transition_diff(self):
        verdict = evaluate(
            metrics(generated_states=3184),
            previous(generated_states=3664),
            make_input(transition_diff="results/transition-diff.md: 480 removed re-fires"),
        )
        assert not verdict.rejected
        assert any("transition diff" in n for n in verdict.notes)

    def test_generated_drop_with_state_change_is_not_red_flagged(self):
        verdict = evaluate(
            metrics(generated_states=3981016, distinct_states=171039, bound=524880),
            previous(),
            make_input(),
        )
        assert not any("STRUCTURALLY BLIND" in e for e in verdict.errors)


# ---------------------------------------------------------------------------
# The refinement loop record
# ---------------------------------------------------------------------------


class TestRefinementRecord:
    def test_missing_refinement_record_is_refused(self):
        verdict = evaluate(metrics(), previous(), make_input(refinement={}))
        assert verdict.rejected
        assert any("no recursive refinement record" in e for e in verdict.errors)

    def test_silence_is_not_searched_found_none(self):
        verdict = evaluate(
            metrics(), previous(), make_input(refinement={"searched": True, "outcome": ""})
        )
        assert verdict.rejected

    def test_searched_found_none_is_accepted(self):
        verdict = evaluate(
            metrics(), previous(), make_input(refinement={"searched": True, "outcome": "none"})
        )
        assert not verdict.rejected
        assert "searched, found none" in cl.render_report(verdict)

    def test_found_requires_detail(self):
        verdict = evaluate(
            metrics(), previous(), make_input(refinement={"searched": True, "outcome": "found"})
        )
        assert verdict.rejected

    def test_applied_recommendation_requires_a_recorded_approver(self):
        """Recommendations are advisory and user-approved, never auto-applied."""
        verdict = evaluate(
            metrics(),
            previous(),
            make_input(
                refinement={
                    "searched": True,
                    "outcome": "found",
                    "detail": "collapse the gates",
                    "applied": True,
                }
            ),
        )
        assert verdict.rejected
        assert any("without a recorded approver" in e for e in verdict.errors)

    def test_found_but_not_applied_is_reported_as_advisory(self):
        verdict = evaluate(
            metrics(),
            previous(),
            make_input(
                refinement={
                    "searched": True,
                    "outcome": "found",
                    "detail": "collapse three failure verdicts",
                    "measured": True,
                }
            ),
        )
        assert not verdict.rejected
        assert "owner approval required" in cl.render_report(verdict)


# ---------------------------------------------------------------------------
# The narrative section
# ---------------------------------------------------------------------------


class TestNarrative:
    def test_narrative_is_required(self):
        verdict = evaluate(metrics(), previous(), make_input(narrative=""))
        assert verdict.rejected

    def test_narrative_is_preserved_verbatim_and_never_parsed(self):
        """The eleven manual ledgers share no schema; the narrative carries them."""
        prose = "## Part 1 -- attribution\n| Quantity | M0 | After |\n outdegree 1/8/6"
        verdict = evaluate(metrics(), previous(), make_input(narrative=prose))
        assert verdict.entry["narrative"] == prose


# ---------------------------------------------------------------------------
# The four historical cases -- real events, real measured figures
# ---------------------------------------------------------------------------


class TestHistoricalCases:
    def test_mf027_refused_47_percent_reduction(self):
        """MF-027 measured a 47% distinct-state reduction and REFUSED it.

        Collapsing the three failure verdicts deleted externally-visible
        result.next distinctions -- i.e. the refactor was NOT validated: the
        reduction deleted behavior, so no honest validated-refactor evidence
        set could exist for it. Replayed without one, the ledger must refuse
        the reduction rather than book it (kill_rate stays recorded as the
        deferred value it historically had).
        """
        payload = make_input()
        del payload["validated_refactor"]
        payload["retention"]["kill_rate"]["status"] = "deferred"
        verdict = evaluate(
            metrics(distinct_states=26607, bound=139968),
            previous(distinct_states=49875, bound=174960),
            payload,
        )
        assert verdict.rejected
        assert any("UNVERIFIED" in e for e in verdict.errors)
        # The measured 47% is still recorded -- refusing is not forgetting.
        assert verdict.entry["delta"]["metrics"]["distinct_states"]["percent"] == pytest.approx(
            -46.7, abs=0.5
        )

    def test_mf016_refused_26_2_percent_reduction(self):
        """MF-016 measured a 26.2% reduction and refused it on the MF-027 standard.

        Its retention evidence was that all four kill_test values are
        individually TLC-reachable -- i.e. a cheaper representation exists but
        it is not a RE-representation. Recorded via the narrative + refinement
        record, with the reduction NOT applied.
        """
        payload = make_input(
            refinement={
                "searched": True,
                "outcome": "found",
                "measured": True,
                "applied": False,
                "detail": (
                    "collapse kill_test 4 -> 3 values gives distinct 231,621 -> 171,039 "
                    "(-26.2%), generated 5,619,356 -> 3,981,016, depth unchanged at 25. "
                    "REFUSED: all four values are individually TLC-reachable, so the "
                    "4-value domain represents the reachable set exactly."
                ),
            }
        )
        verdict = evaluate(metrics(), previous(), payload)
        assert not verdict.rejected
        assert verdict.entry["refinement"]["measured"] is True
        assert verdict.entry["refinement"]["applied"] is False
        assert "26.2%" in verdict.entry["refinement"]["detail"]

    def test_mf020_withdrawn_projection_is_caught_by_the_red_flag(self):
        """MF-020's projected -13.1% generated-states reduction.

        It required deleting a legitimate idempotent re-fire transition. The
        distinct-state gate was structurally blind: distinct (919) and depth
        (21) were unchanged. This is the case the red flag exists for.
        """
        verdict = evaluate(
            metrics(variables=11, bound=393216, distinct_states=919, generated_states=3184, depth=21),
            previous(variables=11, bound=393216, distinct_states=919, generated_states=3664, depth=21),
            make_input(),
        )
        assert verdict.rejected
        message = " ".join(verdict.errors)
        assert "STRUCTURALLY BLIND" in message and "self-loop" in message
        # And it is NOT booked as a reduction: direction is zero on the
        # direction metrics, so no "improvement" is recorded anywhere.
        assert verdict.entry["delta"]["direction"] == "zero"

    def test_mf016_spurious_perfect_kill_rate_is_not_a_free_pass(self):
        """MF-016 nearly shipped a spurious 7/7 kill rate.

        The corpus was already failing before any mutant was seeded, so every
        mutant was 'killed' by that pre-existing failure. A retention metric can
        be maximally wrong exactly when it looks best -- which is half of why
        the 2026-07-21 pivot demoted it. CD-09: the corrected below_floor
        verdict stays RECORDED with its value, but what refuses the reduction
        now is the absent validated-refactor basis, not the kill rate; a
        perfect-looking rate never licensed a decrease and still does not.
        """
        payload = make_input()
        del payload["validated_refactor"]
        payload["retention"]["kill_rate"] = {
            "status": "below_floor",
            "value": 0.571,
            "evidence": "results/kill-test-report.json (control_green=true)",
        }
        verdict = evaluate(metrics(distinct_states=171039, bound=524880), previous(), payload)
        assert verdict.rejected
        assert any("UNVERIFIED" in e and "validated-refactor" in e for e in verdict.errors)
        assert verdict.entry["retention"]["kill_rate"]["value"] == 0.571
        assert verdict.entry["retention"]["kill_rate"]["classification"] == "degraded"


# ---------------------------------------------------------------------------
# Template
# ---------------------------------------------------------------------------


class TestTemplate:
    def test_scaffolded_template_cannot_be_closed_through(self, tmp_path):
        path = tmp_path / "complexity_ledger.yaml"
        cl.write_template(path)
        payload = cl.load_input(path)
        verdict = evaluate(metrics(), previous(), payload)
        assert verdict.rejected
        # It fails for the substantive reasons, not by accident of parsing.
        message = " ".join(verdict.errors)
        assert "refinement" in message and "narrative" in message

    def test_missing_input_is_a_hard_error(self, tmp_path):
        with pytest.raises(cl.LedgerError):
            cl.load_input(tmp_path / "absent.yaml")

    def test_template_is_not_overwritten_if_present(self, tmp_path):
        path = tmp_path / "complexity_ledger.yaml"
        path.write_text("narrative: mine\n")
        cl.write_template(path)
        assert path.read_text() == "narrative: mine\n"


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------


class TestPersistence:
    def test_entries_append_and_never_overwrite(self, tmp_path):
        path = tmp_path / "complexity_ledger.yaml"
        cl.append_entry(path, {"scope_id": "A", "verdict": "recorded", "metrics": metrics()})
        cl.append_entry(path, {"scope_id": "B", "verdict": "recorded", "metrics": metrics()})
        ledger = cl.load_ledger(path)
        assert [e["scope_id"] for e in ledger["entries"]] == ["A", "B"]

    def test_budget_utilization_is_recorded_as_percent_of_cap(self):
        util = cl._budget_utilization(
            {
                "bound": 699840,
                "bound_complete": True,
                "bound_resolved_variables": 9,
                "variables": 9,
                "distinct_states": 231621,
            },
            {"max_state_space_bound": 1000000, "max_distinct_states": 500000},
        )
        assert util["max_state_space_bound"]["percent"] == 70.0
        assert util["max_state_space_bound"]["within_cap"] is True
        assert util["max_distinct_states"]["percent"] == 46.3
        assert util["max_distinct_states"]["within_cap"] is True


# ---------------------------------------------------------------------------
# RP-04 / CM-01-DF-03 -- a percent-of-cap over an INCOMPLETE bound
# ---------------------------------------------------------------------------
#
# The percent above is a measurement only when the bound is a product over the
# WHOLE declared representation. Before RP-04 the ledger computed `within_cap`
# as a plain `used <= cap` regardless, which is how a bound of 4 taken over 1
# of 10 variables was recorded as "0.0% of 1,000,000, within cap" for a model
# TLC measures at 49,386 distinct states -- while the descriptor TEXT beside it
# correctly named the nine excluded variables.


class TestBoundCompleteness:
    def test_incomplete_bound_under_the_cap_refuses_the_within_cap_claim(self):
        util = cl._budget_utilization(
            {
                "bound": 4,
                "bound_complete": False,
                "bound_resolved_variables": 1,
                "bound_unresolved_variables": ["accounts", "carts"],
                "variables": 10,
                "distinct_states": None,
            },
            {"max_state_space_bound": 1000000, "max_distinct_states": 500000},
        )
        entry = util["max_state_space_bound"]
        assert entry["within_cap"] is None, "an incomplete bound is not 'within cap'"
        assert entry["percent"] is None, "percent-of-cap over an incomplete bound"
        assert entry["percent_lower_bound"] == 0.0
        assert entry["bound_complete"] is False
        assert "1 of 10 declared variables" in entry["caveat"]
        assert "not a measurement" in entry["caveat"]

    def test_incomplete_bound_over_the_cap_keeps_the_sound_direction(self):
        """Over the cap stays over the cap: the complete bound is only larger."""
        util = cl._budget_utilization(
            {
                "bound": 2799360,
                "bound_complete": False,
                "bound_resolved_variables": 8,
                "bound_unresolved_variables": ["lastCommand", "result"],
                "variables": 10,
            },
            {"max_state_space_bound": 1000000, "max_distinct_states": 500000},
        )
        entry = util["max_state_space_bound"]
        assert entry["within_cap"] is False
        assert entry["percent"] is None
        assert entry["percent_lower_bound"] == 279.9
        assert "LOWER BOUND" in entry["caveat"]

    def test_unrecorded_completeness_is_not_a_licence_to_claim_within_cap(self):
        """Pre-RP-04 entries carry no completeness; unknown is not complete."""
        util = cl._budget_utilization(
            {"bound": 699840, "variables": 9},
            {"max_state_space_bound": 1000000, "max_distinct_states": 500000},
        )
        entry = util["max_state_space_bound"]
        assert entry["within_cap"] is None
        assert entry["percent"] is None
        assert "not recorded" in entry["caveat"]

    def test_measured_distinct_states_are_unaffected_by_bound_completeness(self):
        """TLC counted them; there is no partial-resolution question to ask."""
        util = cl._budget_utilization(
            {"bound": 4, "bound_complete": False, "distinct_states": 49386},
            {"max_state_space_bound": 1000000, "max_distinct_states": 500000},
        )
        assert util["max_distinct_states"]["percent"] == 9.9
        assert util["max_distinct_states"]["within_cap"] is True

    def test_collect_metrics_publishes_bound_completeness(self, tmp_path):
        tla, cfg = _write_partially_resolved_model(tmp_path)
        collected = cl.collect_metrics(tla, cfg, None)
        assert collected["bound_complete"] is False
        assert collected["bound_resolved_variables"] == 1
        assert collected["bound_unresolved_variables"] == ["free"]
        assert (
            collected["budget_utilization"]["max_state_space_bound"]["within_cap"] is None
        )

    def test_report_never_prints_an_incomplete_bound_without_saying_so(self):
        verdict = evaluate(
            metrics(
                bound=4,
                bound_complete=False,
                bound_resolved_variables=1,
                bound_unresolved_variables=["carts"],
                variables=10,
                budget_utilization=cl._budget_utilization(
                    {
                        "bound": 4,
                        "bound_complete": False,
                        "bound_resolved_variables": 1,
                        "bound_unresolved_variables": ["carts"],
                        "variables": 10,
                    },
                    {"max_state_space_bound": 1000000},
                ),
            ),
            None,
            make_input(),
        )
        rendered = cl.render_report(verdict)
        assert "INCOMPLETE: 1/10 variables resolved" in rendered
        assert "cap comparison UNKNOWN -- incomplete bound" in rendered
        assert "within cap)" not in rendered

    def test_bound_delta_across_a_completeness_change_is_marked_not_comparable(self):
        delta = cl.compute_delta(
            {"scope_id": "prev", "metrics": {"bound": 1000, "bound_complete": True}},
            {"bound": 4, "bound_complete": False},
        )
        bound = delta["metrics"]["bound"]
        assert bound["delta"] == -996
        assert bound["comparable"] is False
        assert "completeness CHANGED" in bound["note"]

    def test_bound_delta_between_two_complete_bounds_is_comparable(self):
        delta = cl.compute_delta(
            {"scope_id": "prev", "metrics": {"bound": 1000, "bound_complete": True}},
            {"bound": 500, "bound_complete": True},
        )
        assert delta["metrics"]["bound"]["comparable"] is True
        assert "note" not in delta["metrics"]["bound"]

    # -- the same pattern, two rows over ---------------------------------
    # Found while auditing the two files RP-04 owns for other places where the
    # descriptor's prose is scrupulous and the recorded artifact is not.

    def test_an_unfinished_tlc_run_does_not_claim_within_cap_either(self, tmp_path):
        """`analyze` checks max_distinct_states only when report.complete."""
        util = cl._budget_utilization(
            {"distinct_states": 49386, "tlc_run_complete": False},
            {"max_distinct_states": 500000},
        )
        entry = util["max_distinct_states"]
        assert entry["within_cap"] is None
        assert entry["percent"] is None
        assert entry["percent_lower_bound"] == 9.9
        assert "did not finish" in entry["caveat"]

    def test_an_unfinished_tlc_run_over_the_cap_keeps_the_sound_claim(self):
        util = cl._budget_utilization(
            {"distinct_states": 900000, "tlc_run_complete": False},
            {"max_distinct_states": 500000},
        )
        assert util["max_distinct_states"]["within_cap"] is False

    def test_collect_metrics_records_whether_the_tlc_run_finished(self, tmp_path):
        tla, cfg = _write_partially_resolved_model(tmp_path)
        truncated = tmp_path / "tlc.txt"
        truncated.write_text(
            "1,234 states generated, 567 distinct states found, 89 states left on queue.\n",
            encoding="utf-8",
        )
        collected = cl.collect_metrics(tla, cfg, None, tlc_report=truncated)
        assert collected["distinct_states"] == 567
        assert collected["tlc_run_complete"] is False

    def test_a_fallback_action_count_carries_its_attribution(self, tmp_path):
        """The descriptor says FALLBACK in prose; the ledger recorded a count."""
        tla = tmp_path / "NoNext.tla"
        tla.write_text(
            "---- MODULE NoNext ----\n"
            "VARIABLES flag\n"
            "TypeInvariant == flag \\in BOOLEAN\n"
            "Toggle == flag' = ~flag\n"
            "====\n",
            encoding="utf-8",
        )
        cfg = tmp_path / "MC.cfg"
        cfg.write_text("INVARIANT TypeInvariant\n", encoding="utf-8")
        collected = cl.collect_metrics(tla, cfg, None)
        assert collected["actions_from_fallback_heuristic"] is True
        assert collected["action_attribution"].startswith("FALLBACK")
        verdict = evaluate(metrics(**collected), None, make_input())
        assert "FALLBACK primes heuristic" in cl.render_report(verdict)

    def test_bound_delta_over_pre_rp04_entries_is_marked_unknown(self):
        """Every historical entry lacks completeness; the delta says so."""
        delta = cl.compute_delta(
            {"scope_id": "prev", "metrics": {"bound": 699840}}, {"bound": 2799360}
        )
        bound = delta["metrics"]["bound"]
        assert bound["comparable"] is False
        assert "unrecorded" in bound["note"]
        # The direction rules are deliberately UNCHANGED: relaxing a gate is a
        # policy call for the owner, not a side effect of a reporting fix.
        assert delta["direction"] == "increase"


# ---------------------------------------------------------------------------
# Reproducing the eleven manual ledgers
# ---------------------------------------------------------------------------


#: The figures each of the eleven manual ledgers actually recorded, as
#: (before, after) pairs with the delta direction the human recorded. Sourced
#: from specs/.history/modular-fuzzing-epic/*/results/.
#:
#: NOTE ON THE CHAIN. These are per-ticket (before, after) pairs, NOT a single
#: chain, because the manual record is not one either: ledgers keyed their
#: baseline variously to a git SHA (MF-015), a tree path (MF-027), the previous
#: ticket by id, and in one case to a ticket that promoted later (MF-014 cites
#: an "MF-017 tip" although MF-017 promoted after it). Reconstructing one global
#: chain from them is not possible without inventing figures. That is a finding
#: about the manual record, and it is exactly what the mechanized ledger fixes:
#: previous_entry() reads the actual preceding recorded entry, so the chain is
#: derived rather than cited.
MANUAL_LEDGERS = {
    # ticket: (before, after, recorded_direction, has_justification)
    "MF-012": (
        {"variables": 12, "distinct_states": 917, "generated_states": 3660, "depth": 20},
        {"variables": 13, "distinct_states": 919, "generated_states": 3664, "depth": 21},
        "increase",
        True,
    ),
    "MF-020": (
        {"variables": 13, "bound": 3145728, "distinct_states": 919, "generated_states": 3664, "depth": 21},
        {"variables": 11, "bound": 393216, "distinct_states": 919, "generated_states": 3664, "depth": 21},
        "decrease",
        False,
    ),
    "MF-021": (
        {"variables": 11, "bound": 393216, "distinct_states": 919, "generated_states": 3664, "depth": 21},
        {"variables": 11, "bound": 393216, "distinct_states": 919, "generated_states": 3664, "depth": 21},
        "zero",
        True,  # justified in lines of code, not model dimensions
    ),
    "MF-011": (
        {"variables": 11, "bound": 393216, "distinct_states": 919, "generated_states": 3664, "depth": 21},
        {"variables": 12, "bound": 1179648, "distinct_states": 2923, "generated_states": 18720, "depth": 23},
        "increase",
        True,
    ),
    "MF-022": (
        {"variables": 12, "bound": 1179648, "distinct_states": 2923, "generated_states": 18720, "depth": 23},
        {"variables": 8, "bound": 221184, "distinct_states": 2923, "generated_states": 18720, "depth": 23},
        "decrease",
        False,
    ),
    "MF-017": (
        {"variables": 8, "bound": 221184, "distinct_states": 2923, "generated_states": 18720, "depth": 23},
        {"variables": 8, "bound": 221184, "distinct_states": 2923, "generated_states": 18720, "depth": 23},
        "zero",
        False,
    ),
    "MF-014": (
        {"variables": 8, "bound": 221184, "distinct_states": 2923},
        {"variables": 9, "bound": 663552, "distinct_states": 9011},
        "increase",
        True,
    ),
    "MF-013": (
        {"variables": 9, "bound": 663552, "distinct_states": 9011},
        {"variables": 10, "bound": 2654208, "distinct_states": 38241},
        "increase",
        True,
    ),
    "MF-025": (
        {"variables": 10, "bound": 663552, "distinct_states": 9011},
        {"variables": 8, "bound": 34992, "distinct_states": 9011},
        "decrease",
        False,
    ),
    "MF-015": (
        {"variables": 8, "bound": 139968, "distinct_states": 38241},
        {"variables": 8, "bound": 139968, "distinct_states": 38241},
        "zero",
        False,
    ),
    "MF-027": (
        {"variables": 8, "bound": 139968, "distinct_states": 38241, "generated_states": 800000, "depth": 24},
        {"variables": 8, "bound": 174960, "distinct_states": 49875, "generated_states": 1067828, "depth": 24},
        "increase",
        True,
    ),
    "MF-016": (
        {"variables": 8, "bound": 174960, "distinct_states": 49875, "generated_states": 1067828, "depth": 24},
        {"variables": 9, "bound": 699840, "distinct_states": 231621, "generated_states": 5619356, "depth": 25},
        "increase",
        True,
    ),
}


class TestReproducesTheElevenManualLedgers:
    """The eleven hand-written ledgers are the regression suite for the format."""

    def test_all_eleven_directions_are_reproduced(self):
        mismatches = []
        for ticket, (before, after, recorded, _) in MANUAL_LEDGERS.items():
            delta = cl.compute_delta({"scope_id": "prev", "metrics": before}, after)
            if delta["direction"] != recorded:
                mismatches.append(f"{ticket}: computed {delta['direction']}, recorded {recorded}")
        assert not mismatches, "; ".join(mismatches)

    def test_every_manual_entry_passes_or_fails_the_gate_as_the_human_decided(self):
        """Each entry, replayed with the retention evidence and justification it carried."""
        for ticket, (before, after, recorded, justified) in MANUAL_LEDGERS.items():
            payload = make_input(
                justification=("recorded in the manual ledger" if justified else ""),
                refinement={"searched": True, "outcome": "none"},
            )
            verdict = evaluate(after, {"scope_id": "prev", "metrics": before}, payload)
            # Every manual ledger was accepted at post-merge review, so with its
            # own justification and a green retention set none may be refused.
            assert not verdict.rejected, f"{ticket} refused: {verdict.errors}"

    def test_increases_without_their_justification_would_all_be_refused(self):
        """The six increases are exactly the entries the gate depends on.

        Each of these tickets recorded a justification naming the new essential
        behavior by hand. Without it the mechanized gate refuses the close, so
        the requirement is enforced rather than merely documented.
        """
        refused = []
        for ticket, (before, after, recorded, justified) in MANUAL_LEDGERS.items():
            if recorded != "increase":
                continue
            verdict = evaluate(after, {"scope_id": "prev", "metrics": before}, make_input())
            if verdict.rejected:
                refused.append(ticket)
        assert set(refused) == {"MF-012", "MF-011", "MF-014", "MF-013", "MF-027", "MF-016"}

    def test_the_three_decreases_require_the_validated_refactor_basis(self):
        """MF-020, MF-022 and MF-025 all reduced complexity.

        Each proved its reduction with TLC before/after at identical distinct
        states and depth -- which IS the validated-refactor basis, applied by
        hand. Under a degraded basis the mechanized gate refuses them, which is
        the anti-gaming rule those tickets applied.
        """
        for ticket in ("MF-020", "MF-022", "MF-025"):
            before, after, _, _ = MANUAL_LEDGERS[ticket]
            payload = make_input()
            payload["validated_refactor"]["tlc_after"]["status"] = "fail"
            verdict = evaluate(after, {"scope_id": "prev", "metrics": before}, payload)
            assert verdict.rejected, f"{ticket} should be refused under a degraded basis"

    def test_mf020_generated_states_correction_is_preserved(self):
        """MF-020's generated states were unchanged at 3,664, not -13.1%.

        The withdrawn projection is not representable as a recorded reduction,
        and must not be: the ledger records the measured figure only.
        """
        before, after, _, _ = MANUAL_LEDGERS["MF-020"]
        delta = cl.compute_delta({"scope_id": "prev", "metrics": before}, after)
        assert delta["metrics"]["generated_states"]["delta"] == 0

    def test_fields_the_core_cannot_express_are_carried_by_the_narrative(self):
        """The honest limit of the machine-checked core, stated as a test.

        These are real fields from the manual ledgers. None is expressible in
        the core schema, and none should be -- a schema that validated all of
        them would validate nothing. They ride in the narrative, verbatim.
        """
        unrepresentable = [
            "per-part attribution of one delta to two independent changes (MF-022)",
            "per-value TLC reachability proof for a 4-valued domain (MF-016)",
            "average/max/p95 outdegree and bound density percentage (MF-025)",
            "complexity measured in lines of code and persisted fields (MF-021)",
            "negotiated-budget provenance and cross-tree propagation (MF-027)",
            "a missed-target root cause that retro-corrects a prior ledger (MF-020)",
            "a domain-cardinality justification tied to result.next strings (MF-013)",
            "an acceptance-criteria conflict escalated to the owner (MF-022)",
        ]
        narrative = "\n".join(f"- {item}" for item in unrepresentable)
        verdict = evaluate(metrics(), previous(), make_input(narrative=narrative))
        assert not verdict.rejected
        assert verdict.entry["narrative"] == narrative


# ---------------------------------------------------------------------------
# MF-026 -- the coverage audit gate recorded in the ledger
# ---------------------------------------------------------------------------


def evaluate_scoped(scope, ledger_input, current=None, prev=None):
    return cl.evaluate(
        scope=scope,
        scope_id="MF-TEST" if scope == "ticket" else "wf",
        workflow="wf",
        metrics=current if current is not None else metrics(),
        ledger_input=ledger_input,
        previous=prev if prev is not None else previous(),
    )


class TestCoverageAuditIsAlwaysVisible:
    """MF-026. The four oracles check FIDELITY and are all bounded to what is
    modeled. Unmodeled surface is invisible to every one of them while they
    report green, so the completeness verdict is recorded separately -- and,
    critically, recorded even when it is absent.

    RETIRED AS A GATE 2026-08-04 (owner direction). It refused a workflow close
    on anything but `pass`, with no override. It is now an OPTIONAL agent-run
    review: the verdict is recorded and printed at every close, including
    `fail` and `incomplete`, and refuses none of them. The reason is not that
    the audit was useless -- it is the only sweep in this toolchain that looks
    at UNMODELED surface, and it found `generate cases` with no action, no port
    and no CLI subcommand at all (G-6), plus two shipped port globs that could
    never fail (F-7, F-8). The reason is that its verdict is a word the audited
    party types about a sweep the audited party performed, and a gate with that
    input is a place to type `pass` rather than a check.

    What these tests now pin is the RECORDING, in both directions: the verdict
    is never forgiven into a pass, and it never refuses a close.
    """

    @staticmethod
    def _audit_note(verdict) -> str:
        matches = [n for n in verdict.notes if "coverage audit" in n]
        assert matches, verdict.notes
        return " ".join(matches)

    def test_absent_block_is_recorded_as_not_run_never_omitted(self):
        """An omitted block is not forgiven into a pass. It becomes a visible
        `not_run`, which is the whole point: an epic that skipped the audit must
        be legible from the ledger alone."""
        verdict = evaluate_scoped("ticket", make_input())
        assert verdict.entry["coverage_audit"]["status"] == "not_run"
        assert verdict.entry["coverage_audit"]["passing"] is False
        assert "coverage audit" in cl.render_report(verdict)

    def test_not_run_is_reported_and_refuses_neither_scope(self):
        """The audit is an END-OF-EPIC step, and since 2026-08-04 it refuses
        nothing at either scope. Its absence is a NOTE at every close, which is
        the strongest claim the record honestly supports."""
        for scope in ("ticket", "workflow"):
            verdict = evaluate_scoped(scope, make_input())
            assert not verdict.rejected, (scope, verdict.errors)
            assert "not_run" in self._audit_note(verdict), scope
            assert not any("coverage audit" in e for e in verdict.errors), scope

    def test_fail_is_recorded_and_does_not_refuse_the_workflow_close(self):
        """It refused here until 2026-08-04. It now records and closes through,
        and the entry still says `fail` -- non-gating is not unrecorded."""
        payload = make_input(coverage_audit={"status": "fail", "in_scope_gaps": 3})
        verdict = evaluate_scoped("workflow", payload)
        assert not verdict.rejected, verdict.errors
        assert verdict.entry["coverage_audit"]["status"] == "fail"
        assert verdict.entry["coverage_audit"]["passing"] is False
        assert "fail" in self._audit_note(verdict)
        assert "does not pass" in cl.render_report(verdict)

    def test_incomplete_IS_NOT_pass(self):
        """MF-027's polarity lesson, applied one level up: a sweep that did not
        walk the surface carries no information about it. Promoting that to a
        pass would dress an absence of evidence as a measurement.

        Retiring the REFUSAL did not retire this DISTINCTION, which is the half
        that was ever load-bearing: `incomplete` is still not `passing`, still
        prints its flag, and still reads as an absence of evidence in the
        entry."""
        payload = make_input(coverage_audit={"status": "incomplete"})
        assert not cl.parse_coverage_audit(payload["coverage_audit"]).passing
        verdict = evaluate_scoped("workflow", payload)
        assert not verdict.rejected, verdict.errors
        assert verdict.entry["coverage_audit"]["passing"] is False
        assert "incomplete" in self._audit_note(verdict)

    def test_pass_allows_the_workflow_close_and_records_the_report_path(self):
        payload = make_input(
            coverage_audit={
                "status": "pass",
                "report": "results/coverage_audit_report.md",
                "in_scope_gaps": 0,
                "scope_source": "ticket_plan.yaml:449-464",
            }
        )
        verdict = evaluate_scoped("workflow", payload)
        assert not verdict.rejected
        assert verdict.entry["coverage_audit"]["report"] == "results/coverage_audit_report.md"
        assert "results/coverage_audit_report.md" in cl.render_report(verdict)

    def test_unrecognized_verdict_never_passes(self):
        """Same polarity as the retention set: a status nobody enumerated is
        normalized to `not_run` rather than silently passing. `justified` and
        `accept_as_is` are exactly the dispositions the prompt forbids --
        neither becomes a pass by being written into the ledger instead.

        This survives the gate's retirement unchanged. It never was a refusal
        rule; it is a READING rule, and reading a word nobody defined as good
        news is the failure mode with or without a gate behind it."""
        for bogus in ("justified", "accept_as_is", "waived", "approved", "green", "ok"):
            record = cl.parse_coverage_audit({"status": bogus})
            assert record.normalized == "not_run", bogus
            assert not record.passing, bogus
            verdict = evaluate_scoped("workflow", make_input(coverage_audit={"status": bogus}))
            assert verdict.entry["coverage_audit"]["passing"] is False, bogus

    def test_template_sentinel_does_not_pass(self):
        payload = make_input(coverage_audit={"status": "TODO", "report": "TODO"})
        record = cl.parse_coverage_audit(payload["coverage_audit"])
        assert not record.passing
        assert record.report == ""

    def test_scaffolded_template_carries_the_block_defaulted_to_not_run(self):
        """`open ticket` must scaffold the block, or the first thing every
        ticket does is omit it."""
        assert "coverage_audit:" in cl.TEMPLATE
        parsed = cl._load_structured(cl.TEMPLATE)
        assert cl.parse_coverage_audit(parsed["coverage_audit"]).normalized == "not_run"


# ---------------------------------------------------------------------------
# CD-09 -- the validated-refactor retention basis (owner-approved 2026-07-22)
# ---------------------------------------------------------------------------


def make_validated_refactor(**overrides):
    """A fully-verified validated-refactor evidence set (CD-02 basis)."""
    payload = {
        "tlc_before": {"status": "green", "evidence": "results/tlc_before.txt"},
        "tlc_after": {"status": "green", "evidence": "results/tlc_current.txt"},
        "behavior_tests": {"status": "pass", "evidence": "results/repo_unit_tests.txt"},
        "descriptor_comparison": {
            "status": "recorded",
            "evidence": "results/model_before_after_descriptors.txt",
        },
    }
    payload.update(overrides)
    return payload


def not_run_fuzzing_retention():
    """The honest post-pivot record: experimental members recorded, not run."""
    return {
        name: {"status": "not_run", "evidence": "experimental since the 2026-07-21 pivot"}
        for name in ("kill_rate", "effect_conformance", "external_coverage")
    }


class TestValidatedRefactorBasis:
    """CD-09: a complexity DECREASE is licensed by the validated-refactor basis
    (TLC green before/after, behavior tests green, before/after descriptor
    comparison recorded, transition-level diff inspected when the red flag
    fires). The fuzzing-era members stay RECORDED but no longer gate: they were
    demoted by the 2026-07-21 pivot after measuring kill 0.31 vs floor 0.8 and
    0/9 content bugs caught."""

    def test_cd09_regression_validated_decrease_with_not_run_fuzzing_members_is_recorded(self):
        """THE regression for the amendment: fails pre-amendment, passes after.

        Pre-amendment the ledger rejected every decrease whose kill_rate /
        effect_conformance / external_coverage were not green -- but post-pivot
        `not_run` is the HONEST record for all three, so an honest validated
        refactor could never close. Post-amendment the validated-refactor
        basis licenses it.
        """
        payload = make_input(
            validated_refactor=make_validated_refactor(),
            retention=not_run_fuzzing_retention(),
        )
        verdict = evaluate(metrics(bound=524880), previous(), payload)
        assert not verdict.rejected, verdict.errors
        assert verdict.entry["delta"]["direction"] == "decrease"

    def test_decrease_with_missing_descriptor_comparison_is_rejected(self):
        """Degraded-evidence handling for the NEW basis: an absent member of the
        validated-refactor set cannot witness retention, so it cannot license a
        decrease. Fails pre-amendment (the old gate never read this block)."""
        vr = make_validated_refactor()
        del vr["descriptor_comparison"]
        payload = make_input(validated_refactor=vr)
        verdict = evaluate(metrics(bound=524880), previous(), payload)
        assert verdict.rejected
        assert any("descriptor_comparison" in e for e in verdict.errors)

    def test_decrease_with_failed_tlc_after_is_rejected(self):
        payload = make_input(
            validated_refactor=make_validated_refactor(tlc_after={"status": "fail"})
        )
        verdict = evaluate(metrics(bound=524880), previous(), payload)
        assert verdict.rejected
        assert any("DEGRADED" in e for e in verdict.errors)

    def test_decrease_with_failed_behavior_tests_is_rejected(self):
        payload = make_input(
            validated_refactor=make_validated_refactor(behavior_tests={"status": "fail"})
        )
        verdict = evaluate(metrics(bound=524880), previous(), payload)
        assert verdict.rejected
        assert any("DEGRADED" in e for e in verdict.errors)

    def test_unrecognized_validated_refactor_status_refuses(self):
        """MF-027's polarity lesson applies to the new basis unchanged."""
        payload = make_input(
            validated_refactor=make_validated_refactor(tlc_before={"status": "probably_fine"})
        )
        verdict = evaluate(metrics(bound=524880), previous(), payload)
        assert verdict.rejected

    def test_degraded_fuzzing_member_no_longer_blocks_a_validated_decrease(self):
        """The demotion itself: a below-floor kill rate is RECORDED, visibly,
        but does not reject a decrease that carries the validated-refactor
        evidence. Fails pre-amendment (the old gate rejected it)."""
        retention = not_run_fuzzing_retention()
        retention["kill_rate"] = {"status": "below_floor", "value": 0.31}
        payload = make_input(
            validated_refactor=make_validated_refactor(), retention=retention
        )
        verdict = evaluate(metrics(bound=524880), previous(), payload)
        assert not verdict.rejected, verdict.errors
        assert verdict.entry["retention"]["kill_rate"]["classification"] == "degraded"

    def test_fuzzing_members_remain_recorded_in_entry_and_report(self):
        """Non-gating is not unrecorded: `not_run` stays visible everywhere."""
        payload = make_input(
            validated_refactor=make_validated_refactor(),
            retention=not_run_fuzzing_retention(),
        )
        verdict = evaluate(metrics(bound=524880), previous(), payload)
        assert set(verdict.entry["retention"]) == set(cl.RETENTION_MEMBERS)
        report = cl.render_report(verdict)
        assert "kill_rate=not_run" in report

    def test_red_flag_gate_is_retained_exactly_as_is(self):
        """The transition-diff obligation survives the amendment untouched: a
        generated-states drop at constant distinct states and depth REJECTS
        without an inspected transition-level diff, even when the full
        validated-refactor evidence set is green."""
        payload = make_input(validated_refactor=make_validated_refactor())
        verdict = evaluate(
            metrics(generated_states=3184),
            previous(generated_states=3664),
            payload,
        )
        assert verdict.rejected
        assert any("STRUCTURALLY BLIND" in e for e in verdict.errors)

    def test_red_flag_still_accepted_only_with_the_transition_diff(self):
        payload = make_input(
            validated_refactor=make_validated_refactor(),
            transition_diff="results/transition_diff.md: duplicate override bindings removed",
        )
        verdict = evaluate(
            metrics(generated_states=3184),
            previous(generated_states=3664),
            payload,
        )
        assert not verdict.rejected
        assert any("transition diff" in n for n in verdict.notes)

    def test_validated_refactor_block_is_recorded_in_the_entry(self):
        payload = make_input(validated_refactor=make_validated_refactor())
        verdict = evaluate(metrics(bound=524880), previous(), payload)
        assert set(verdict.entry["validated_refactor"]) == set(cl.VALIDATED_REFACTOR_MEMBERS)
        for member in verdict.entry["validated_refactor"].values():
            assert member["classification"] == "retained"

    def test_template_scaffolds_the_validated_refactor_block(self):
        assert "validated_refactor:" in cl.TEMPLATE
        parsed = cl._load_structured(cl.TEMPLATE)
        members = cl.parse_validated_refactor(parsed["validated_refactor"])
        assert all(m.unverified for m in members.values())


# ---------------------------------------------------------------------------
# AC-04 -- the architecture delta member: REMOVED 2026-08-04 (owner direction)
#
# Five test classes stood here (TestArchitectureDeltaIsRecordedAndNeverGates,
# TestTheDeltaIsDerivedNotTyped, TestTheMF020RuleAppliedToStructure,
# TestTheMapIdentityIsPartOfTheRecord, TestTheTemplateCarriesTheDeltaBlock).
# They pinned three properties of a ledger member whose input was a JSON report
# only `analyze architecture --baseline` could produce. That command and the two
# scanner modules behind it are gone, so the member could never again be
# anything but `not_run`, and a test suite for a field with no producer is the
# dead surface this project keeps writing tools to find.
#
# Two of the three properties were never about architecture and are not lost:
#
#   * DERIVED, NOT TYPED -- "a member whose verdict is typed in by the author
#     being graded is not a measurement". That is now the argument for retiring
#     the coverage-audit gate (see TestCoverageAuditIsAlwaysVisible above), and
#     it is written down at references/architecture_advice.md rather than
#     enforced on one field.
#   * MF-020 APPLIED TO STRUCTURE -- "a drop whose disappeared edges are not
#     enumerated is unverified". The COMPLEXITY half of that rule is still
#     mechanised, by the transition-diff gate in `evaluate`, and is still tested
#     in this file. What went is the structural half, which had nothing left to
#     measure.
# ---------------------------------------------------------------------------
