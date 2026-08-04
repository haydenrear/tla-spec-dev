"""MF-016 spec-unit conformance: `tla-spec-dev run kill-test` (oracle 4).

Each test asserts ONE claim the TLA+ model makes about `RunKillTest` and the
`kill_test` variable, by driving the real CLI through the production adapter.

Scope note, kept honest: kill-test runs over a real distilled corpus are
deferred epic-wide to MF-023. These fixtures prove the GATE -- that below the
floor fails, that a partial catalog refuses to produce a number, that no
waiver exists, and that a survivor points somewhere. They do NOT prove this
repository's own kill rate. See specs/tickets/MF-016/results/.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


def load_adapters():
    path = Path(__file__).resolve().parents[1] / "production_adapters.py"
    spec = importlib.util.spec_from_file_location("mf016_production_adapters", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def result(tmp_path_factory: pytest.TempPathFactory) -> dict:
    adapters = load_adapters()
    target = tmp_path_factory.mktemp("mf016-kill-test")
    return adapters.RunKillTestAdapter().apply(target)


class TestTheFloorGate:
    """`kill_test' \\in {"pass", "below_floor", "incomplete_catalog"}` and the
    result mapping in RunKillTest."""

    def test_a_complete_catalog_at_or_above_the_floor_passes(self, result: dict) -> None:
        assert result["pass_verdict"] == "pass", result
        assert result["pass_exit_code"] == 0, result
        assert result["pass_kill_rate"] == 1.0, result

    def test_below_the_floor_fails_with_a_nonzero_exit(self, result: dict) -> None:
        """The load-bearing one.

        If this ever passes silently, every cost cap in this epic becomes
        gameable: shrink the model toward nothing and all of them pass while
        the representation stops catching bugs.
        """

        assert result["below_floor_verdict"] == "below_floor", result
        assert result["below_floor_exit_code"] == 1, result
        assert result["below_floor_fails"] is True, result

    def test_the_sub_floor_rate_is_reported_not_hidden(self, result: dict) -> None:
        """Recording the finding is evidence, never a substitute for failing."""

        assert result["below_floor_kill_rate"] == 0.5, result


class TestAPartialExperimentYieldsNoNumber:
    """The `incomplete_catalog` verdict."""

    def test_a_declared_port_with_no_seeded_fault_refuses(self, result: dict) -> None:
        assert result["uncovered_verdict"] == "incomplete_catalog", result
        assert result["uncovered_exit_code"] == 2, result

    def test_no_kill_rate_is_computed_over_an_uncovered_surface(self, result: dict) -> None:
        """Not 1.0 over the mutants that happen to exist.

        Same discipline MF-027 applied to `unobservable`: a number derived
        from a surface nobody covered asserts something the run has no
        evidence for.
        """

        assert result["uncovered_kill_rate_is_absent"] is True, result

    def test_the_uncovered_boundary_is_named(self, result: dict) -> None:
        uncovered = result["uncovered_boundaries"]
        assert uncovered, result
        assert {"kind": "invariant", "ref": "TypeInvariant"} in uncovered, result


class TestNothingWaivesTheFloor:
    """The inverse test the degeneracy audit requires.

    There is deliberately no fixture proving a waiver works, because no
    waiver exists.
    """

    def test_a_recorded_waiver_does_not_change_the_verdict(self, result: dict) -> None:
        assert result["waiver_does_not_change_the_verdict"] is True, result
        assert result["waived_verdict"] == "below_floor", result
        assert result["waived_exit_code"] == 1, result

    def test_the_waiver_attempt_is_reported_not_honored(self, result: dict) -> None:
        assert result["waiver_reported_not_honored"] is True, result


class TestASurvivorIsAPointer:
    """The reason the oracle is worth running: a survivor says what to fix."""

    def test_the_survivor_names_the_model_variable_to_refine(self, result: dict) -> None:
        assert result["survivor_names_variable"] == "demo_var", result

    def test_the_survivor_names_the_model_action_to_refine(self, result: dict) -> None:
        assert result["survivor_names_action"] == "DemoAction", result

    def test_the_survivor_names_the_boundary_it_perturbed(self, result: dict) -> None:
        assert result["survivor_names_boundary"] == "TypeInvariant", result


class TestEvidenceLayout:
    """`RunKillTest: [evidence_report, mutation_write, corpus_process]` in the manifest (CD-11 R4-1)."""

    def test_the_kill_matrix_is_written_for_every_run(self, result: dict) -> None:
        """Including the failing ones -- a report that only appears when the
        news is good is not evidence."""

        assert result["report_written_as_evidence"] is True, result

    def test_the_kill_matrix_carries_one_row_per_mutant(self, result: dict) -> None:
        assert result["kill_matrix_rows"] == 2, result
