"""MF-019 spec-unit conformance: the standing objective is a gate on close.

Drives the shipped CLI end to end rather than the ledger functions in
isolation, so it covers the real seam between close-out, promotion, and the
append-only history entry. The four cases mirror what this epic did by hand:
record the delta jointly with retention, refuse an unfilled record, reject a
reduction bought with degraded retention, and refuse to read `unobservable` as
`clean`.
"""

import importlib.util
from pathlib import Path


def load_adapters():
    path = Path(__file__).resolve().parents[1] / "production_adapters.py"
    spec = importlib.util.spec_from_file_location("mf019_production_adapters", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_close_records_delta_jointly_with_retention_and_refinement(tmp_path: Path) -> None:
    adapters = load_adapters()
    result = adapters.ComplexityLedgerCloseOutAdapter().apply(
        tmp_path, spec_root="project_specs", ticket_id="CLI-140"
    )

    assert result["close_recorded"] is True, result["stderr"]
    assert result["ledger_file_written"] is True
    assert result["delta_and_retention_in_same_entry"] is True, (
        "a complexity delta must never be recorded without the retention evidence "
        "from the same run -- the number is meaningless alone"
    )
    assert result["refinement_recorded"] == "none", (
        "the refinement-loop record is required at every close: an approved "
        "recommendation, or an explicit 'searched, found none'"
    )


def test_unfilled_ledger_template_refuses_the_close(tmp_path: Path) -> None:
    """Silence is not an acceptable substitute for the record."""
    adapters = load_adapters()
    result = adapters.ComplexityLedgerCloseOutAdapter().apply(
        tmp_path, spec_root="project_specs", ticket_id="CLI-141"
    )

    assert result["template_scaffolded_with_sentinels"] is True
    assert result["unfilled_template_refuses_close"] is True, (
        "an unfilled ledger template must fail the close, not pass it silently"
    )
    assert result["unfilled_names_refinement_and_narrative"] is True


def test_decrease_with_degraded_retention_is_rejected(tmp_path: Path) -> None:
    """The anti-gaming rule, applied by hand on MF-016 and MF-027."""
    adapters = load_adapters()
    result = adapters.ComplexityLedgerCloseOutAdapter().apply(
        tmp_path, spec_root="project_specs", ticket_id="CLI-142"
    )

    assert result["degraded_decrease_rejected"] is True, (
        "a complexity reduction accompanied by a below-floor kill rate must be "
        "rejected at close, not recorded as an improvement"
    )
    assert result["degraded_message_says_rejected"] is True


def test_unobservable_retention_is_not_clean(tmp_path: Path) -> None:
    """MF-027: the effect oracle refuses what it cannot see; so does the ledger."""
    adapters = load_adapters()
    result = adapters.ComplexityLedgerCloseOutAdapter().apply(
        tmp_path, spec_root="project_specs", ticket_id="CLI-143"
    )

    assert result["unobservable_rejected"] is True, (
        "treating an unobservable effect-conformance result as passing retention "
        "would rebuild the exact silence MF-027 removed"
    )
    assert result["unobservable_is_not_clean"] is True
