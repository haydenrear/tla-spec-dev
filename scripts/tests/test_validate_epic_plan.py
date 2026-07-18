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
    return {
        "deferment_policy": {
            "mode": "batch",
            "blocking": "escalate",
            "budget": 5,
            "backlog": "specs/desired_program_model/deferred_findings.yaml",
        },
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
            },
            {
                "id": "EPIC-3",
                "depends_on": ["EPIC-1", "EPIC-2"],
                "blocks": [],
                "wave": 2,
                "promotion_order": 30,
                "promotion_predecessor": "EPIC-2",
                "conflict_keys": empty_conflicts,
            },
        ]
    }


class EpicPlanValidatorTests(unittest.TestCase):
    def assert_invalid(self, plan: dict, diagnostic: str) -> None:
        errors = validator.validate_plan(plan)
        self.assertTrue(errors)
        self.assertIn(diagnostic, "\n".join(errors))

    def test_accepts_valid_parallel_schedule(self) -> None:
        self.assertEqual(validator.validate_plan(valid_plan()), [])

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
        errors = "\n".join(validator.validate_plan(plan))
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
            self.assertIn("3 tickets across 2 waves", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
