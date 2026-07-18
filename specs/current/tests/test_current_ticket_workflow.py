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


def test_current_model_carries_the_ticket_phase_ordinal() -> None:
    """MF-020 collapsed three parallel lifecycle booleans into one ordinal.

    The three booleans were pinned to a strict total order by the invariants, so
    only 4 of their 8 combinations were reachable. ``ticket_phase`` represents
    exactly the reachable set: 0=open, 1=desired, 2=current, 3=units passed.
    """
    model = (SPEC_ROOT / "current/TlaSpecDevCli.tla").read_text(encoding="utf-8")

    assert "ticket_phase" in model
    assert "ticket_phase \\in [Tickets -> 0..3]" in model, (
        "TypeInvariant must bound the ordinal to 0..3"
    )

    # Check code lines only: the module carries an explanatory comment that
    # names the old booleans on purpose, to document the encoding.
    code = "\n".join(
        line for line in model.splitlines() if not line.lstrip().startswith("\\*")
    )
    for gone in ("desired_ready", "current_ready", "spec_unit_tests_passed"):
        assert gone not in code, f"{gone} survived the MF-020 collapse"

    # The ordering invariants are deliberately retained rather than deleted:
    # keeping them documents that the constraint still holds and was absorbed
    # into the representation instead of dropped.
    assert "CurrentRequiresDesired" in model
    assert "SpecUnitTestsRequireCurrent" in model
    assert "ClosedTicketsPassedSpecUnitTests" in model

    # RunSpecUnitTests must stay re-runnable on an already-passing ticket, which
    # is why its guard is `>= 2` and not `= 2`. Tightening it would delete the
    # idempotent re-run transition (measured: 3664 -> 3184 generated states).
    assert "/\\ ticket_phase[ticket] >= 2" in model, (
        "RunSpecUnitTests guard must remain >= 2 to preserve the re-run self-loop"
    )
