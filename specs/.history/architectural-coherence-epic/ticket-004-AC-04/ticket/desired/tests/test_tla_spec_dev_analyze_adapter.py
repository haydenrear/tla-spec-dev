"""Spec-unit conformance for the AnalyzeComplexity action.

MF-036: complexity is advisory, not a gate. The TLA+ model's AnalyzeComplexity
action always succeeds (``result' = CommandResult(TRUE, ...)``) and merely
records a pass/fail verdict in ``complexity_gate``. CD-01: the command is a
DESCRIPTOR -- facts, not judgment -- with no suggested move and no
recommendations. This runs the real CLI against fixture specs on both sides of
the threshold and checks the production behavior matches: both sides exit 0,
the over-threshold side emits a warning-bearing REPORT that names a target and
states the fact, and case generation advises rather than refuses.
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
    assert result["over_budget_warns_with_facts"] is True
    # Case generation advises and proceeds; it does not refuse.
    assert result["generation_advises_not_refused"] is True
    assert result["accepted"] is True, result


def test_descriptor_makes_no_suggestions(tmp_path: Path) -> None:
    """CD-01: no suggested move, no recommendations, no projected gains.

    Validation project 1 showed the suggested-move chooser confidently wrong on
    standard TLA+ (an aliased invariant made it recommend projecting away every
    variable), so the machinery was removed. The descriptor states facts.
    """
    adapters = load_adapters()
    result = adapters.AnalyzeComplexityAdapter().apply(tmp_path)
    assert result["descriptor_makes_no_suggestions"] is True


def test_output_reports_measured_facts(tmp_path: Path) -> None:
    """Every figure is [MEASURED]; nothing projected remains in the output."""
    adapters = load_adapters()
    result = adapters.AnalyzeComplexityAdapter().apply(tmp_path)
    assert result["reports_measured_facts"] is True


# --------------------------------------------------------------------------
# AC-01: AnalyzeArchitecture
# --------------------------------------------------------------------------


def test_analyze_architecture_describes_the_structure_and_never_blocks(
    tmp_path: Path,
) -> None:
    """The model's AnalyzeArchitecture action, checked against production.

    ``AnalyzeArchitecture`` sets ``result' = CommandResult(TRUE, ...)``
    unconditionally and merely records a verdict in ``architecture_scan``; no
    action in the model guards on that variable. Production must match: both a
    model that decomposes and one that does not exit 0, and the descriptor
    names components, per-variable writers, single-writer violations, ports,
    and spanning actions.
    """
    adapters = load_adapters()
    result = adapters.AnalyzeArchitectureAdapter().apply(tmp_path)

    assert result["decomposing_exit_code"] == 0, result["stderr"]
    assert result["blob_exit_code"] == 0, result["stderr"]
    assert result["names_components_ownership_ports_and_span"] is True
    assert result["describes_ports_and_span"] is True
    assert result["blocks_nothing"] is True
    assert result["accepted"] is True, result


def test_a_model_that_resists_clustering_is_not_given_an_invented_cut(
    tmp_path: Path,
) -> None:
    """The refusal, and the false clean it exists to prevent.

    A model whose interaction graph is one blob has no components. Handed a
    one-component partition, every variable is trivially "written inside its
    component" and the descriptor would report a flawless single-writer
    architecture. It reports NOT MEASURABLE instead, and tells its consumers
    the partition is not usable as an architecture.
    """
    adapters = load_adapters()
    result = adapters.AnalyzeArchitectureAdapter().apply(tmp_path)
    assert result["refuses_to_invent_a_cut"] is True


def test_architecture_scan_is_never_coherent_without_a_code_side(
    tmp_path: Path,
) -> None:
    """MF-027, applied to ``architecture_scan``.

    ``analyze architecture`` measures the MODEL. With no production code
    supplied there is nothing for the code to be coherent with, and a clean
    report on a target that was never observed is indistinguishable from a
    clean report on one that was. The verdict is ``unmappable``.
    """
    adapters = load_adapters()
    result = adapters.AnalyzeArchitectureAdapter().apply(tmp_path)
    assert result["never_coherent_without_code"] is True


def test_architecture_descriptor_makes_no_suggestions(tmp_path: Path) -> None:
    """CD-01 binds here too: facts, no proposed cut, no refactor."""
    adapters = load_adapters()
    result = adapters.AnalyzeArchitectureAdapter().apply(tmp_path)
    assert result["descriptor_makes_no_suggestions"] is True
    assert result["reports_measured_facts"] is True
