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
    """A ledger input that PASSES every gate, as the base for negative tests."""
    payload = {
        "retention": {
            "kill_rate": {"status": "pass", "evidence": "results/kill-test.json"},
            "effect_conformance": {"status": "clean", "evidence": "results/effects.txt"},
            "external_coverage": {"status": "pass", "evidence": "results/coverage.txt"},
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
        """The doctrine's core requirement: never one without the other."""
        verdict = evaluate(metrics(), previous(), make_input())
        assert verdict.entry["delta"]
        assert set(verdict.entry["retention"]) == set(cl.RETENTION_MEMBERS)
        # And in the human-readable report, adjacently.
        report = cl.render_report(verdict)
        assert "delta:" in report and "retention (joint requirement" in report

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
    def test_decrease_with_degraded_kill_rate_is_rejected(self):
        payload = make_input()
        payload["retention"]["kill_rate"]["status"] = "below_floor"
        verdict = evaluate(metrics(distinct_states=171039, bound=524880), previous(), payload)
        assert verdict.rejected
        assert any("REJECTED" in e and "DEGRADED" in e for e in verdict.errors)

    def test_decrease_with_unverified_retention_is_rejected(self):
        """Absent evidence is not passing evidence."""
        payload = make_input()
        payload["retention"]["kill_rate"]["status"] = "unknown"
        verdict = evaluate(metrics(bound=524880), previous(), payload)
        assert verdict.rejected
        assert any("UNVERIFIED" in e for e in verdict.errors)

    def test_decrease_with_missing_retention_member_is_rejected(self):
        """A gate cannot be skipped by leaving the field out."""
        verdict = evaluate(metrics(bound=524880), previous(), make_input(retention={}))
        assert verdict.rejected
        assert any("UNVERIFIED" in e for e in verdict.errors)

    def test_unobservable_is_not_clean(self):
        """MF-027: the effect oracle refuses what it cannot see. So does this."""
        payload = make_input()
        payload["retention"]["effect_conformance"]["status"] = "unobservable"
        verdict = evaluate(metrics(bound=524880), previous(), payload)
        assert verdict.rejected
        assert any("unobservable" in e for e in verdict.errors)
        member = cl.parse_retention(payload["retention"])["effect_conformance"]
        assert member.degraded and not member.retained
        assert "unobservable IS NOT clean" in member.describe()

    def test_unrecognized_verdict_refuses_rather_than_passes(self):
        """MF-027's polarity lesson: pass only on positive evidence."""
        payload = make_input()
        payload["retention"]["kill_rate"]["status"] = "probably_fine"
        verdict = evaluate(metrics(bound=524880), previous(), payload)
        assert verdict.rejected
        member = cl.parse_retention(payload["retention"])["kill_rate"]
        assert member.unverified and not member.retained

    def test_degraded_retention_alone_does_not_block_a_zero_delta(self):
        """The anti-gaming rule targets reductions bought with behavior.

        Other tickets' gates own retention in its own right; this gate fires on
        the CONJUNCTION, so it must not silently become a second kill-rate gate.
        """
        payload = make_input()
        payload["retention"]["kill_rate"]["status"] = "below_floor"
        verdict = evaluate(metrics(), previous(), payload)
        assert not verdict.rejected

    def test_there_is_no_override_for_the_anti_gaming_gate(self):
        payload = make_input(override=True, allow_degraded=True, force=True)
        payload["retention"]["kill_rate"]["status"] = "below_floor"
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
        result.next distinctions. Retention was not evidenced -- kill test was
        deferred -- so the ledger must refuse the reduction rather than book it.
        """
        payload = make_input()
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
        be maximally wrong exactly when it looks best. The ledger consumes the
        CORRECTED verdict (below_floor, 4/7), and must refuse a reduction under
        it -- a perfect-looking rate is not what licenses a decrease; a green
        control is, and that is the kill test's own gate to enforce upstream.
        """
        payload = make_input()
        payload["retention"]["kill_rate"] = {
            "status": "below_floor",
            "value": 0.571,
            "evidence": "results/kill-test-report.json (control_green=true)",
        }
        verdict = evaluate(metrics(distinct_states=171039, bound=524880), previous(), payload)
        assert verdict.rejected
        assert any("DEGRADED" in e for e in verdict.errors)
        assert verdict.entry["retention"]["kill_rate"]["value"] == 0.571


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

    def test_the_three_decreases_require_retention_evidence(self):
        """MF-020, MF-022 and MF-025 all reduced complexity.

        Each recorded identical distinct states and depth as its retention
        proof. Under degraded retention the mechanized gate refuses them, which
        is the anti-gaming rule those tickets applied by hand.
        """
        for ticket in ("MF-020", "MF-022", "MF-025"):
            before, after, _, _ = MANUAL_LEDGERS[ticket]
            payload = make_input()
            payload["retention"]["kill_rate"]["status"] = "below_floor"
            verdict = evaluate(after, {"scope_id": "prev", "metrics": before}, payload)
            assert verdict.rejected, f"{ticket} should be refused under degraded retention"

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
