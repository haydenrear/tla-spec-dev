from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.onboard_program_model import scaffold


def test_onboard_program_model_creates_only_program_model(tmp_path: Path) -> None:
    written = scaffold(tmp_path, "SkillManager", force=False, dry_run=False)

    assert tmp_path / "specs/program_model/spec_manifest.yaml" in written
    assert tmp_path / "specs/program_model/SkillManager.tla" in written
    assert (tmp_path / "specs/program_model/SkillManager.tla").exists()
    assert (tmp_path / "specs/program_model/MC.cfg").exists()
    assert (tmp_path / "specs/program_model/case_adapters.toml").exists()
    assert (tmp_path / "specs/program_model/production_adapters.py").exists()
    assert not (tmp_path / "specs/current").exists()
    assert not (tmp_path / "specs/desired_program_model").exists()

    manifest = (tmp_path / "specs/program_model/spec_manifest.yaml").read_text(encoding="utf-8")
    assert "workflow: project_onboarding" in manifest
    assert "model_role: accepted_program_model" in manifest


def test_onboard_program_model_preserves_existing_program_model_files(tmp_path: Path) -> None:
    existing = tmp_path / "specs" / "program_model" / "spec_manifest.yaml"
    existing.parent.mkdir(parents=True)
    existing.write_text("keep: true\n", encoding="utf-8")

    scaffold(tmp_path, "SkillManager", force=False, dry_run=False)

    assert existing.read_text(encoding="utf-8") == "keep: true\n"
