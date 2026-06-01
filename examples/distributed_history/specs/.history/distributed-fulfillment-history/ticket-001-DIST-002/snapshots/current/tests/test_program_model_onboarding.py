from pathlib import Path


SPEC_ROOT = Path(__file__).resolve().parents[1]


def test_program_model_onboarding_scaffold_has_no_ticket_workflow_dirs() -> None:
    assert (SPEC_ROOT / "DistributedFulfillment.tla").exists()
    assert (SPEC_ROOT / "spec_manifest.yaml").exists()
    assert not (SPEC_ROOT.parent / "current").exists()
    assert not (SPEC_ROOT.parent / "desired_program_model").exists()
