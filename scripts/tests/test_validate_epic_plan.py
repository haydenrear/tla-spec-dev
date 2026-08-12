#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "PyYAML>=6.0.2,<7",
# ]
# ///

from __future__ import annotations

import copy
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest

import yaml


SCRIPT = Path(__file__).parents[1] / "validate_epic_plan.py"
SPEC = importlib.util.spec_from_file_location("validate_epic_plan", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


def valid_plan() -> dict:
    empty_conflicts = {
        "production": [],
        "tla": [],
        "adapters": [],
        "test_graph": [],
        "workflow": [],
    }
    def link(contribution: str = "direct", signal: str = "bench --quick") -> list[dict]:
        return [
            {
                "goal": "GOAL-1",
                "contribution": contribution,
                "expected_effect": "-120ms p99",
                "local_signal": signal,
            }
        ]

    return {
        "name": "example-epic-workflow",
        "schedule_revision": 1,
        "deferment_policy": {
            "mode": "batch",
            "blocking": "escalate",
            "budget": 5,
            "backlog": "specs/desired_program_model/deferred_findings.yaml",
        },
        "epic_goals": [
            {
                "id": "GOAL-1",
                "kind": "perf",
                "statement": "Batched ingest cuts tail latency.",
                "metric": "p99 ingest latency (ms) at 5k rps",
                "harness": "bench --profile epic",
                "baseline": {
                    "value": "p99 412ms",
                    "measured_at": "abc123",
                    "evidence": "results/epic/baseline/ingest.json",
                },
                "target": "p99 <= 250ms",
                "evaluation_ticket": "EPIC-3",
                "evidence_root": "results/epic/goals/GOAL-1",
            }
        ],
        "tickets": [
            {
                "id": "EPIC-1",
                "depends_on": [],
                "blocks": ["EPIC-3"],
                "wave": 1,
                "promotion_order": 10,
                "promotion_predecessor": None,
                "conflict_keys": {
                    **empty_conflicts,
                    "production": ["src/one.py"],
                },
                "goals": link(),
            },
            {
                "id": "EPIC-2",
                "depends_on": [],
                "blocks": ["EPIC-3"],
                "wave": 1,
                "promotion_order": 20,
                "promotion_predecessor": "EPIC-1",
                "conflict_keys": {
                    **empty_conflicts,
                    "production": ["src/two.py"],
                },
                "goals": link("enabling", "N/A: plumbing only"),
            },
            {
                "id": "EPIC-3",
                "role": "evaluation",
                "owns_goals": ["GOAL-1"],
                "depends_on": ["EPIC-1", "EPIC-2"],
                "blocks": [],
                "wave": 2,
                "promotion_order": 30,
                "promotion_predecessor": "EPIC-2",
                "conflict_keys": empty_conflicts,
                "goals": link("guard", "N/A: this ticket is the measurement"),
            },
        ]
    }


def retire_ticket(
    plan: dict,
    index: int,
    *,
    resolution: str = "carried",
    disposition: str = "carried",
) -> None:
    """Retire one fixture ticket using the canonical receipt contract."""
    ticket = plan["tickets"][index]
    retirement = {
        "schedule_revision": plan["schedule_revision"],
        "resolution": resolution,
        "reason": "The owner narrowed the local MVP scope.",
        "decided_by": "owner@example.test",
        "decided_at": "2026-08-12T03:00:00Z",
        "receipt": (
            "specs/.history/example-epic-workflow/"
            f"retired-ticket-{index:03d}-{ticket['id']}/manifest.json"
        ),
        "affected_goals": [
            {
                "goal": "GOAL-1",
                "disposition": disposition,
                "reason": "The goal moves with the deferred work.",
            }
        ],
    }
    if resolution == "carried":
        retirement["successor_issue"] = "EPIC-99"
        retirement["successor_workflow"] = "next-epic-workflow"
    if disposition == "carried":
        retirement["affected_goals"][0]["successor_issue"] = "EPIC-99"
        retirement["affected_goals"][0][
            "successor_workflow"
        ] = "next-epic-workflow"
    ticket["status"] = "retired"
    ticket["retirement"] = retirement


def fully_retired_plan() -> dict:
    plan = valid_plan()
    plan["schedule_revision"] = 2
    for index in range(len(plan["tickets"])):
        retire_ticket(plan, index)
    return plan


class EpicPlanValidatorTests(unittest.TestCase):
    def assert_invalid(self, plan: dict, diagnostic: str) -> None:
        report = validator.validate_plan(plan)
        self.assertTrue(report.errors)
        self.assertIn(diagnostic, "\n".join(report.errors))

    def assert_warns(self, plan: dict, diagnostic: str) -> None:
        """Warnings are advisory: they must not fail the plan."""
        report = validator.validate_plan(plan)
        self.assertEqual(report.errors, [])
        self.assertIn(diagnostic, "\n".join(report.warnings))

    def test_accepts_valid_parallel_schedule(self) -> None:
        report = validator.validate_plan(valid_plan())
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])

    def test_rejects_missing_or_non_positive_schedule_revision(self) -> None:
        plan = valid_plan()
        del plan["schedule_revision"]
        self.assert_invalid(plan, "schedule_revision must be a positive integer")

        plan["schedule_revision"] = 0
        self.assert_invalid(plan, "schedule_revision must be a positive integer")

    def test_accepts_canonical_retirement_receipts(self) -> None:
        report = validator.validate_plan(fully_retired_plan())
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])

    def test_accepts_delivered_work_with_an_explicit_unmeasured_retirement(self) -> None:
        plan = valid_plan()
        plan["schedule_revision"] = 2
        plan["tickets"][0]["status"] = "closed"
        plan["tickets"][1]["status"] = "closed"
        retire_ticket(
            plan,
            2,
            resolution="abandoned",
            disposition="accepted_unmeasured",
        )
        # Canonical-plan shape: delivered tickets retain their sealed historical
        # `blocks` edges to the later-retired evaluation ticket.
        report = validator.validate_plan(plan)
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])

    def test_accepts_delivered_evaluator_with_an_accepted_miss(self) -> None:
        plan = valid_plan()
        plan["schedule_revision"] = 2
        retire_ticket(
            plan,
            0,
            resolution="abandoned",
            disposition="accepted_missed",
        )
        plan["tickets"][1]["status"] = "closed"
        plan["tickets"][2]["status"] = "closed"
        # Delivered tickets retain historical dependency and predecessor edges
        # to a ticket retired by a later schedule amendment.
        report = validator.validate_plan(plan)
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])

    def test_rejects_retired_status_without_retirement_receipt(self) -> None:
        plan = valid_plan()
        plan["tickets"][0]["status"] = "retired"
        self.assert_invalid(plan, "status retired requires a retirement mapping")

    def test_rejects_noncanonical_retired_status_spelling(self) -> None:
        plan = fully_retired_plan()
        plan["tickets"][0]["status"] = "Retired"
        self.assert_invalid(plan, "retirement status must be written exactly as 'retired'")

    def test_rejects_retirement_metadata_on_active_ticket(self) -> None:
        plan = valid_plan()
        plan["tickets"][0]["retirement"] = {}
        self.assert_invalid(
            plan, "retirement metadata is allowed only with status: retired"
        )

    def test_rejects_resolution_as_a_direct_ticket_status(self) -> None:
        plan = valid_plan()
        plan["tickets"][0]["status"] = "carried"
        self.assert_invalid(plan, "status 'carried' is not a retirement receipt")

    def test_accepts_sealed_retirement_after_later_plan_revision(self) -> None:
        plan = fully_retired_plan()
        plan["schedule_revision"] = 3
        report = validator.validate_plan(plan)
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])

    def test_accepts_canonical_closed_edges_and_new_lane_across_retirements(
        self,
    ) -> None:
        """Closed CDC-MVP-002 keeps old edges; new work skips retired entries."""

        def conflicts() -> dict[str, list]:
            return {
                "production": [],
                "tla": [],
                "adapters": [],
                "test_graph": [],
                "workflow": [],
            }

        def retired(
            ticket_id: str,
            index: int,
            order: int,
            predecessor: str,
        ) -> dict:
            return {
                "id": ticket_id,
                "status": "retired",
                "depends_on": ["CDC-MVP-002"],
                "blocks": [],
                "wave": index + 2,
                "promotion_order": order,
                "promotion_predecessor": predecessor,
                "conflict_keys": conflicts(),
                "retirement": {
                    "schedule_revision": 8,
                    "resolution": "abandoned",
                    "reason": "Owner removed this work from the local MVP.",
                    "decided_by": "owner@example.test",
                    "decided_at": "2026-08-12T03:00:00Z",
                    "receipt": (
                        "specs/.history/cdc-polyglot-relation-mvp-workflow/"
                        f"retired-ticket-{index:03d}-{ticket_id}/manifest.json"
                    ),
                    "affected_goals": [],
                },
            }

        plan = {
            "name": "cdc-polyglot-relation-mvp-workflow",
            "schedule_revision": 9,
            "deferment_policy": {
                "mode": "batch",
                "blocking": "escalate",
                "budget": 5,
                "backlog": "specs/desired_program_model/deferred_findings.yaml",
            },
            "epic_goals": [],
            "goals_waived": "scheduling regression fixture",
            "tickets": [
                {
                    "id": "CDC-MVP-002",
                    "status": "closed",
                    "depends_on": [],
                    "blocks": ["CDC-MVP-020", "CDC-MVP-003", "CDC-MVP-004"],
                    "wave": 2,
                    "promotion_order": 20,
                    "promotion_predecessor": None,
                    "conflict_keys": conflicts(),
                },
                retired("CDC-MVP-020", 1, 30, "CDC-MVP-002"),
                retired("CDC-MVP-003", 2, 40, "CDC-MVP-020"),
                retired("CDC-MVP-004", 3, 50, "CDC-MVP-003"),
                {
                    "id": "CDC-MVP-005",
                    "status": "planned",
                    "depends_on": [],
                    "blocks": [],
                    "wave": 6,
                    "promotion_order": 60,
                    "promotion_predecessor": "CDC-MVP-002",
                    "conflict_keys": conflicts(),
                },
            ],
        }
        report = validator.validate_plan(plan)
        self.assertEqual(report.errors, [])

    def test_rejects_retirement_revision_newer_than_root(self) -> None:
        plan = fully_retired_plan()
        plan["tickets"][0]["retirement"]["schedule_revision"] = 3
        self.assert_invalid(
            plan,
            "sealed decision revision and cannot exceed current root "
            "schedule_revision 2",
        )

    def test_rejects_unknown_retirement_fields(self) -> None:
        plan = fully_retired_plan()
        plan["tickets"][0]["retirement"]["delivery_claim"] = True
        self.assert_invalid(
            plan, "retirement: unknown fields are forbidden: ['delivery_claim']"
        )

    def test_rejects_unknown_affected_goal_fields(self) -> None:
        plan = fully_retired_plan()
        plan["tickets"][0]["retirement"]["affected_goals"][0][
            "verdict"
        ] = "met"
        self.assert_invalid(
            plan,
            "retirement.affected_goals[0]: unknown fields are forbidden: "
            "['verdict']",
        )

    def test_rejects_retirement_receipt_with_rewritten_ordinal(self) -> None:
        plan = fully_retired_plan()
        plan["tickets"][0]["retirement"]["receipt"] = (
            "specs/.history/example-epic-workflow/"
            "retired-ticket-002-EPIC-1/manifest.json"
        )
        self.assert_invalid(plan, "must preserve immutable ticket ordinal 0")

    def test_rejects_carried_retirement_without_successor_identity(self) -> None:
        plan = fully_retired_plan()
        del plan["tickets"][0]["retirement"]["successor_issue"]
        del plan["tickets"][0]["retirement"]["affected_goals"][0][
            "successor_workflow"
        ]
        errors = "\n".join(validator.validate_plan(plan).errors)
        self.assertIn("retirement.successor_issue must be a non-empty string", errors)
        self.assertIn("successor_workflow must be a non-empty string", errors)

    def test_rejects_carried_ticket_with_accepted_goal(self) -> None:
        plan = fully_retired_plan()
        goal = plan["tickets"][0]["retirement"]["affected_goals"][0]
        goal["disposition"] = "accepted_unmeasured"
        goal.pop("successor_issue")
        goal.pop("successor_workflow")
        self.assert_invalid(
            plan,
            "disposition must be carried when ticket retirement.resolution is carried",
        )

    def test_rejects_carried_goal_with_different_successor(self) -> None:
        plan = fully_retired_plan()
        plan["tickets"][0]["retirement"]["affected_goals"][0][
            "successor_issue"
        ] = "EPIC-100"
        self.assert_invalid(
            plan,
            "carried successor must exactly match ticket retirement "
            "successor_issue/successor_workflow",
        )

    def test_rejects_abandoned_ticket_with_carried_goal(self) -> None:
        plan = fully_retired_plan()
        retirement = plan["tickets"][0]["retirement"]
        retirement["resolution"] = "abandoned"
        retirement.pop("successor_issue")
        retirement.pop("successor_workflow")
        self.assert_invalid(
            plan,
            "carried disposition contradicts ticket retirement.resolution "
            "'abandoned'",
        )

    def test_rejects_noncarried_ticket_successor_fields(self) -> None:
        plan = valid_plan()
        plan["schedule_revision"] = 2
        retire_ticket(
            plan,
            0,
            resolution="abandoned",
            disposition="accepted_missed",
        )
        retirement = plan["tickets"][0]["retirement"]
        retirement["successor_issue"] = "EPIC-99"
        retirement["successor_workflow"] = "next-epic-workflow"
        errors = "\n".join(validator.validate_plan(plan).errors)
        self.assertIn(
            "retirement.successor_issue must be absent unless "
            "retirement.resolution is carried",
            errors,
        )
        self.assertIn(
            "retirement.successor_workflow must be absent unless "
            "retirement.resolution is carried",
            errors,
        )

    def test_rejects_noncarried_goal_successor_fields(self) -> None:
        plan = valid_plan()
        plan["schedule_revision"] = 2
        retire_ticket(
            plan,
            0,
            resolution="superseded",
            disposition="accepted_unmeasured",
        )
        goal = plan["tickets"][0]["retirement"]["affected_goals"][0]
        goal["successor_issue"] = "EPIC-99"
        self.assert_invalid(
            plan,
            "successor_issue must be absent when ticket retirement.resolution "
            "is not carried",
        )

    def test_rejects_missing_affected_goal_disposition(self) -> None:
        plan = fully_retired_plan()
        plan["tickets"][0]["retirement"]["affected_goals"] = []
        self.assert_invalid(
            plan,
            "retirement.affected_goals must exactly preserve every goal relation",
        )

    def test_rejects_retired_tickets_that_disagree_on_goal_disposition(self) -> None:
        plan = fully_retired_plan()
        plan["tickets"][0]["retirement"]["affected_goals"][0].update(
            {
                "disposition": "accepted_missed",
            }
        )
        self.assert_invalid(plan, "retired tickets disagree on affected-goal disposition")

    def test_rejects_active_dependency_on_retired_ticket(self) -> None:
        plan = fully_retired_plan()
        plan["tickets"][2].pop("status")
        plan["tickets"][2].pop("retirement")
        self.assert_invalid(
            plan, "non-delivered depends_on cannot reference retired ticket"
        )

    def test_rejects_active_block_edge_to_retired_ticket(self) -> None:
        plan = fully_retired_plan()
        plan["tickets"][0].pop("status")
        plan["tickets"][0].pop("retirement")
        self.assert_invalid(
            plan, "non-delivered blocks cannot reference retired ticket"
        )

    def test_rejects_active_promotion_predecessor_that_is_retired(self) -> None:
        plan = fully_retired_plan()
        plan["tickets"][1].pop("status")
        plan["tickets"][1].pop("retirement")
        self.assert_invalid(
            plan,
            "non-delivered promotion_predecessor cannot reference retired ticket",
        )

    def test_rejects_active_evaluator_for_a_retired_goal(self) -> None:
        plan = fully_retired_plan()
        plan["tickets"][2].pop("status")
        plan["tickets"][2].pop("retirement")
        self.assert_invalid(plan, "active evaluation ticket 'EPIC-3'")

    def test_rejects_active_undelivered_ticket_for_a_retired_goal(self) -> None:
        plan = fully_retired_plan()
        plan["tickets"][0].pop("status")
        plan["tickets"][0].pop("retirement")
        plan["tickets"][0]["blocks"] = []
        plan["tickets"][0]["promotion_predecessor"] = None
        self.assert_invalid(plan, "retirement disposition conflicts with active tickets")

    def test_rejects_plan_without_a_deferment_policy(self) -> None:
        plan = valid_plan()
        del plan["deferment_policy"]
        self.assert_invalid(plan, "plan must declare deferment_policy")

    def test_rejects_unknown_deferment_mode(self) -> None:
        plan = valid_plan()
        plan["deferment_policy"]["mode"] = "whenever"
        self.assert_invalid(plan, "deferment_policy.mode must be one of")

    def test_rejects_unknown_blocking_disposition(self) -> None:
        plan = valid_plan()
        plan["deferment_policy"]["blocking"] = "ignore"
        self.assert_invalid(plan, "deferment_policy.blocking must be one of")

    def test_rejects_non_positive_deferment_budget(self) -> None:
        plan = valid_plan()
        plan["deferment_policy"]["budget"] = 0
        self.assert_invalid(plan, "deferment_policy.budget must be a positive integer")

    def test_rejects_missing_backlog_path(self) -> None:
        plan = valid_plan()
        plan["deferment_policy"]["backlog"] = ""
        self.assert_invalid(plan, "deferment_policy.backlog must be a non-empty path")

    def test_reports_deferment_error_even_when_tickets_are_missing(self) -> None:
        self.assert_invalid({"tickets": []}, "plan must declare deferment_policy")

    def test_rejects_duplicate_and_unstable_ticket_ids(self) -> None:
        plan = valid_plan()
        plan["tickets"].append(copy.deepcopy(plan["tickets"][0]))
        plan["tickets"].append({"id": "not stable"})
        errors = "\n".join(validator.validate_plan(plan).errors)
        self.assertIn("duplicate ticket ID 'EPIC-1'", errors)
        self.assertIn("id must be a stable string", errors)

    def test_rejects_unknown_and_self_dependencies(self) -> None:
        plan = valid_plan()
        plan["tickets"][0]["depends_on"] = ["EPIC-1", "MISSING"]
        self.assert_invalid(plan, "cannot depend on itself")
        self.assert_invalid(plan, "depends_on references unknown ticket 'MISSING'")

    def test_rejects_dependency_cycle(self) -> None:
        plan = valid_plan()
        plan["tickets"][0]["depends_on"] = ["EPIC-3"]
        plan["tickets"][2]["blocks"] = ["EPIC-1"]
        self.assert_invalid(plan, "dependency cycle detected")

    def test_rejects_blocks_that_are_not_exact_reverse(self) -> None:
        plan = valid_plan()
        plan["tickets"][0]["blocks"] = []
        self.assert_invalid(plan, "blocks must be the exact reverse of depends_on")

    def test_rejects_dependency_not_in_earlier_wave(self) -> None:
        plan = valid_plan()
        plan["tickets"][2]["wave"] = 1
        self.assert_invalid(plan, "which is not earlier than wave 1")

    def test_rejects_same_wave_conflict(self) -> None:
        plan = valid_plan()
        plan["tickets"][1]["conflict_keys"]["production"] = ["src/one.py"]
        self.assert_invalid(plan, "share conflict keys ['production:src/one.py']")

    def test_rejects_duplicate_promotion_order(self) -> None:
        plan = valid_plan()
        plan["tickets"][1]["promotion_order"] = 10
        self.assert_invalid(plan, "promotion_order 10 is not unique")

    def test_rejects_promotion_order_that_violates_dependency_dag(self) -> None:
        plan = valid_plan()
        plan["tickets"][2]["promotion_order"] = 5
        self.assert_invalid(plan, "promotion_order is not a topological extension")

    def test_rejects_inexact_promotion_predecessor_chain(self) -> None:
        plan = valid_plan()
        plan["tickets"][2]["promotion_predecessor"] = "EPIC-1"
        self.assert_invalid(plan, "promotion_predecessor must be 'EPIC-2'")

    def test_cli_returns_nonzero_for_invalid_plan(self) -> None:
        plan = valid_plan()
        plan["tickets"][0]["blocks"] = []
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ticket_plan.yaml"
            path.write_text(yaml.safe_dump(plan, sort_keys=False), encoding="utf-8")
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                self.assertEqual(validator.main([str(path)]), 1)
            self.assertIn("INVALID:", stderr.getvalue())

    def test_cli_returns_zero_for_valid_plan(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ticket_plan.yaml"
            path.write_text(
                yaml.safe_dump(valid_plan(), sort_keys=False), encoding="utf-8"
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(validator.main([str(path)]), 0)
            self.assertIn(
                "3 tickets, 0 retired, 3 active/delivered across 2 waves, 1 goal",
                stdout.getvalue(),
            )

    def test_cli_warns_but_succeeds_without_goals(self) -> None:
        plan = valid_plan()
        del plan["epic_goals"]
        for ticket in plan["tickets"]:
            ticket.pop("goals", None)
            ticket.pop("owns_goals", None)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ticket_plan.yaml"
            path.write_text(yaml.safe_dump(plan, sort_keys=False), encoding="utf-8")
            stderr = io.StringIO()
            with redirect_stderr(stderr), redirect_stdout(io.StringIO()):
                self.assertEqual(validator.main([str(path)]), 0)
            self.assertIn("WARNING: plan declares no epic_goals", stderr.getvalue())

    def test_warns_when_goals_are_waived(self) -> None:
        plan = valid_plan()
        plan["epic_goals"] = []
        plan["goals_waived"] = "pure refactor; no behavioral delta"
        for ticket in plan["tickets"]:
            ticket.pop("goals", None)
            ticket.pop("owns_goals", None)
        self.assert_warns(plan, "epic_goals is waived: pure refactor")

    def test_warns_when_no_ticket_declares_an_evaluation_role(self) -> None:
        plan = valid_plan()
        plan["tickets"][2].pop("role")
        self.assert_warns(plan, "no ticket declares role: evaluation")

    def test_warns_on_unmeasured_baseline(self) -> None:
        plan = valid_plan()
        plan["epic_goals"][0]["baseline"] = {"value": "unmeasured"}
        self.assert_warns(plan, "baseline is unmeasured")

    def test_warns_when_a_direct_contribution_has_no_local_signal(self) -> None:
        plan = valid_plan()
        plan["tickets"][0]["goals"][0]["local_signal"] = "N/A: no cheap check"
        self.assert_warns(plan, "has no local signal")

    def test_rejects_ticket_with_no_goal_relation(self) -> None:
        plan = valid_plan()
        del plan["tickets"][0]["goals"]
        self.assert_invalid(plan, "must relate to at least one epic goal")

    def test_rejects_unknown_goal_reference(self) -> None:
        plan = valid_plan()
        plan["tickets"][0]["goals"][0]["goal"] = "GOAL-nope"
        self.assert_invalid(plan, "goals references unknown goal 'GOAL-nope'")

    def test_rejects_unknown_contribution_kind(self) -> None:
        plan = valid_plan()
        plan["tickets"][0]["goals"][0]["contribution"] = "vibes"
        self.assert_invalid(plan, "contribution must be one of")

    def test_rejects_goal_missing_required_fields(self) -> None:
        plan = valid_plan()
        del plan["epic_goals"][0]["harness"]
        plan["epic_goals"][0]["kind"] = "hunch"
        errors = "\n".join(validator.validate_plan(plan).errors)
        self.assertIn("harness must be a non-empty string", errors)
        self.assertIn("kind must be one of", errors)

    def test_rejects_goal_with_no_contributing_ticket(self) -> None:
        plan = valid_plan()
        plan["epic_goals"].append(
            {
                **copy.deepcopy(plan["epic_goals"][0]),
                "id": "GOAL-2",
            }
        )
        plan["tickets"][2]["owns_goals"] = ["GOAL-1", "GOAL-2"]
        self.assert_invalid(plan, "goal 'GOAL-2': no implementation ticket contributes")

    def test_rejects_evaluation_ticket_that_skips_a_contributor(self) -> None:
        plan = valid_plan()
        plan["tickets"][2]["depends_on"] = ["EPIC-1"]
        plan["tickets"][1]["blocks"] = []
        self.assert_invalid(plan, "must depend on contributor 'EPIC-2'")

    def test_rejects_evaluation_ticket_that_promotes_before_a_contributor(self) -> None:
        plan = valid_plan()
        plan["tickets"][2]["promotion_order"] = 15
        plan["tickets"][1]["promotion_order"] = 30
        plan["tickets"][1]["promotion_predecessor"] = "EPIC-3"
        plan["tickets"][2]["promotion_predecessor"] = "EPIC-1"
        self.assert_invalid(plan, "must promote after contributor 'EPIC-2'")

    def test_rejects_owns_goals_that_disagrees_with_the_goal(self) -> None:
        plan = valid_plan()
        plan["tickets"][2]["owns_goals"] = []
        self.assert_invalid(plan, "owns_goals must list every goal it decides")

    def test_rejects_evaluation_ticket_reference_to_an_implementation_ticket(
        self,
    ) -> None:
        plan = valid_plan()
        plan["epic_goals"][0]["evaluation_ticket"] = "EPIC-1"
        errors = "\n".join(validator.validate_plan(plan).errors)
        self.assertIn("must declare role: evaluation", errors)


if __name__ == "__main__":
    unittest.main()
