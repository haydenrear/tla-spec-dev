"""Spec-unit conformance for the AnalyzeComplexity action.

MF-036: complexity is advisory, not a gate. The TLA+ model's AnalyzeComplexity
action always succeeds (``result' = CommandResult(TRUE, ...)``) and merely
records a pass/fail verdict in ``complexity_gate``. This runs the real CLI
against fixture specs on both sides of the threshold and checks the production
behavior matches: both sides exit 0, the over-threshold side emits a
warning-bearing REPORT that names a target and recommends a move, and case
generation advises rather than refuses.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def load_adapters():
    path = Path(__file__).resolve().parents[1] / "production_adapters.py"
    spec = importlib.util.spec_from_file_location("mf011_production_adapters", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_analyze_complexity_adapter_advises_both_sides_and_never_blocks(
    tmp_path: Path,
) -> None:
    adapters = load_adapters()
    result = adapters.AnalyzeComplexityAdapter().apply(tmp_path)

    # MF-036: a complex model is a finding, not a failure -- BOTH sides exit 0.
    assert result["under_budget_exit_code"] == 0, result["stderr"]
    assert result["over_budget_exit_code"] == 0, result["stderr"]
    assert result["prints_dimension_table"] is True
    assert result["over_budget_names_dominant_dimensions"] is True
    # The over-threshold model produces a warning-bearing REPORT, not a block.
    assert result["over_budget_warns_and_recommends"] is True
    # Case generation advises and proceeds; it does not refuse.
    assert result["generation_advises_not_refused"] is True
    assert result["accepted"] is True, result


def test_suggested_move_is_always_a_recommendation_never_auto_applied(
    tmp_path: Path,
) -> None:
    """Doctrine: architectural moves are recommendations the owner approves."""
    adapters = load_adapters()
    result = adapters.AnalyzeComplexityAdapter().apply(tmp_path)
    assert result["suggested_move_labeled_recommendation"] is True


def test_output_distinguishes_measured_figures_from_projected_ones(
    tmp_path: Path,
) -> None:
    """MF-020: an unverified projection propagated into a downstream ticket."""
    adapters = load_adapters()
    result = adapters.AnalyzeComplexityAdapter().apply(tmp_path)
    assert result["separates_measured_from_projected"] is True
