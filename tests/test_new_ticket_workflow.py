from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.new_ticket_workflow import scaffold


def test_scaffold_ticket_workflow_creates_current_and_desired_models(tmp_path: Path) -> None:
    program_model = tmp_path / "specs" / "program_model"
    program_model.mkdir(parents=True)
    (program_model / "ProgramModel.tla").write_text(
        """----------------------------- MODULE ProgramModel -----------------------------
EXTENDS Naturals, TLC

CONSTANTS Items
VARIABLES seen
vars == << seen >>
Init == seen = {}
Add(i) == seen' = seen \\cup {i}
Next == \\E i \\in Items: Add(i)
SeenKnown == seen \\subseteq Items
Spec == Init /\\ [][Next]_vars
=============================================================================
""",
        encoding="utf-8",
    )
    (program_model / "MC.cfg").write_text(
        """SPECIFICATION Spec
CONSTANTS Items = {i1}
INVARIANTS SeenKnown
""",
        encoding="utf-8",
    )
    (program_model / "spec_manifest.yaml").write_text(
        """module: ProgramModel
package: program_model_cases
""",
        encoding="utf-8",
    )

    written = scaffold(tmp_path, "AUTH-123", "Add account lock", force=False, dry_run=False)

    assert tmp_path / "specs/current/spec_manifest.yaml" in written
    assert tmp_path / "specs/desired_program_model/ticket_plan.yaml" in written
    current_manifest = (tmp_path / "specs/current/spec_manifest.yaml").read_text(encoding="utf-8")
    desired_manifest = (tmp_path / "specs/desired_program_model/spec_manifest.yaml").read_text(encoding="utf-8")
    ticket_plan = (tmp_path / "specs/desired_program_model/ticket_plan.yaml").read_text(encoding="utf-8")

    assert "status:" in current_manifest
    assert "status:" in desired_manifest
    assert "AUTH-123" in ticket_plan
    assert "not only migrations" in ticket_plan
    assert (tmp_path / "specs/current/ProgramModel.tla").exists()
    assert (tmp_path / "specs/desired_program_model/ProgramModel.tla").exists()


def test_scaffold_ticket_workflow_preserves_existing_files(tmp_path: Path) -> None:
    existing = tmp_path / "specs" / "desired_program_model" / "ticket_plan.yaml"
    existing.parent.mkdir(parents=True)
    existing.write_text("keep: true\n", encoding="utf-8")

    scaffold(tmp_path, "T-1", "Keep existing", force=False, dry_run=False)

    assert existing.read_text(encoding="utf-8") == "keep: true\n"
