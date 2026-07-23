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
            {"bound": 699840, "distinct_states": 231621},
            {"max_state_space_bound": 1000000, "max_distinct_states": 500000},
        )
        assert util["max_state_space_bound"]["percent"] == 70.0
        assert util["max_distinct_states"]["percent"] == 46.3
        assert util["max_distinct_states"]["within_cap"] is True


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
    critically, recorded even when it is absent."""

    def test_absent_block_is_recorded_as_not_run_never_omitted(self):
        """An omitted block is not forgiven into a pass. It becomes a visible
        `not_run`, which is the whole point: an epic that skipped the audit must
        be legible from the ledger alone."""
        verdict = evaluate_scoped("ticket", make_input())
        assert verdict.entry["coverage_audit"]["status"] == "not_run"
        assert verdict.entry["coverage_audit"]["passing"] is False
        assert "coverage audit" in cl.render_report(verdict)

    def test_not_run_is_reported_but_does_not_refuse_a_ticket_close(self):
        """The audit is an END-OF-EPIC step. Failing it at every ticket close
        would force each ticket to run a whole-epic audit or to fake a verdict;
        both are worse than recording the absence."""
        verdict = evaluate_scoped("ticket", make_input())
        assert not verdict.rejected
        assert any("end-of-epic" in note for note in verdict.notes)

    def test_not_run_REFUSES_the_workflow_close(self):
        """At workflow close the epic is over and there is no later chance. A
        check that silently passes when its input is absent is not a check."""
        verdict = evaluate_scoped("workflow", make_input())
        assert verdict.rejected
        assert any("coverage audit" in e for e in verdict.errors)

    def test_fail_refuses_the_workflow_close(self):
        payload = make_input(coverage_audit={"status": "fail", "in_scope_gaps": 3})
        assert evaluate_scoped("workflow", payload).rejected

    def test_incomplete_IS_NOT_pass(self):
        """MF-027's polarity lesson, applied one level up: a sweep that did not
        walk the surface carries no information about it. Promoting that to a
        pass would dress an absence of evidence as a measurement."""
        payload = make_input(coverage_audit={"status": "incomplete"})
        assert not cl.parse_coverage_audit(payload["coverage_audit"]).passing
        assert evaluate_scoped("workflow", payload).rejected

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
        """Same polarity as the retention set: a status nobody enumerated
        refuses rather than silently passing. `justified` and `accept_as_is`
        are exactly the dispositions the prompt forbids -- neither becomes a
        pass by being written into the ledger instead."""
        for bogus in ("justified", "accept_as_is", "waived", "approved", "green", "ok"):
            record = cl.parse_coverage_audit({"status": bogus})
            assert record.normalized == "not_run", bogus
            assert not record.passing, bogus
            assert evaluate_scoped("workflow", make_input(coverage_audit={"status": bogus})).rejected

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
