from pathlib import Path


SPEC_ROOT = Path(__file__).resolve().parents[1]


def test_program_model_onboarding_scaffold_has_program_model_files() -> None:
    assert (SPEC_ROOT / "TlaSpecDevCli.tla").exists()
    assert (SPEC_ROOT / "spec_manifest.yaml").exists()
