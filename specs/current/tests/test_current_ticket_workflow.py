from pathlib import Path

SPEC_ROOT = Path(__file__).resolve().parents[1].parent


def _active_ticket(manifest_text: str) -> str:
    for line in manifest_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("active_ticket:"):
            return stripped.split(":", 1)[1].strip().strip('"')
    raise AssertionError("current spec_manifest.yaml has no status.active_ticket")


def test_current_ticket_workflow_scaffold_points_to_desired_plan() -> None:
    """The promoted current manifest and the desired plan must name the same ticket.

    Generalized from a hardcoded ticket id so this survives promotion of each
    ticket in the epic instead of going stale after one of them lands.
    """
    manifest = SPEC_ROOT / "current/spec_manifest.yaml"
    plan = SPEC_ROOT / "desired_program_model/ticket_plan.yaml"

    assert manifest.exists()
    assert plan.exists()

    active = _active_ticket(manifest.read_text(encoding="utf-8"))
    assert active
    assert active in plan.read_text(encoding="utf-8"), (
        f"current manifest active_ticket {active!r} is not present in the desired ticket plan"
    )


def test_current_model_carries_the_budgets_gate() -> None:
    """MF-012 promoted budgets into the whole-program current model."""
    model = (SPEC_ROOT / "current/TlaSpecDevCli.tla").read_text(encoding="utf-8")
    manifest = (SPEC_ROOT / "current/spec_manifest.yaml").read_text(encoding="utf-8")

    assert "budgets_recorded" in model
    assert "RecordBudgets" in model
    assert "WorkflowRequiresBudgets" in model
    assert "budgets:" in manifest
