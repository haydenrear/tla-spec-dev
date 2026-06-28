import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.new_ticket_workflow import scaffold, scaffold_ticket_directory
from scripts.close_tickets import close_ticket_workflow, validate_equivalent
from scripts.spec_evolution import create_ticket_history_entry


def write_program_model(tmp_path: Path, spec_root: Path = Path("specs")) -> Path:
    program_model = tmp_path / spec_root / "program_model"
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
    return program_model


def test_scaffold_ticket_workflow_creates_current_and_desired_models(tmp_path: Path) -> None:
    write_program_model(tmp_path)

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


def test_scaffold_ticket_workflow_uses_custom_spec_root_and_copies_baseline_files(tmp_path: Path) -> None:
    spec_root = Path("project_specs")
    program_model = write_program_model(tmp_path, spec_root)
    (program_model / "case_adapters.toml").write_text("[adapters.Existing]\n", encoding="utf-8")
    (program_model / "nested" / "trace.json").parent.mkdir()
    (program_model / "nested" / "trace.json").write_text('{"keep": true}\n', encoding="utf-8")

    written = scaffold(
        tmp_path,
        "AUTH-124",
        "Custom root",
        force=False,
        dry_run=False,
        spec_root=spec_root,
    )

    assert tmp_path / "project_specs/current/spec_manifest.yaml" in written
    assert tmp_path / "project_specs/desired_program_model/ticket_plan.yaml" in written
    assert (tmp_path / "project_specs/current/case_adapters.toml").read_text(encoding="utf-8") == "[adapters.Existing]\n"
    assert (tmp_path / "project_specs/current/nested/trace.json").exists()
    ticket_plan = (tmp_path / "project_specs/desired_program_model/ticket_plan.yaml").read_text(encoding="utf-8")
    assert "project_specs/current" in ticket_plan


def test_scaffold_ticket_workflow_uses_nested_spec_root_in_generated_test(tmp_path: Path) -> None:
    spec_root = Path("project/specs")
    write_program_model(tmp_path, spec_root)

    scaffold(
        tmp_path,
        "AUTH-125",
        "Nested root",
        force=False,
        dry_run=False,
        spec_root=spec_root,
    )

    generated_test = (
        tmp_path / "project/specs/current/tests/test_current_ticket_workflow.py"
    ).read_text(encoding="utf-8")
    assert "SPEC_ROOT = Path(__file__).resolve().parents[1].parent" in generated_test


def test_start_ticket_scaffolds_ticket_local_current_and_desired_from_plan(tmp_path: Path) -> None:
    write_program_model(tmp_path)
    scaffold(tmp_path, "AUTH-127", "Parallel ticket", force=False, dry_run=False)
    (tmp_path / "specs" / "testgraph").mkdir()
    (tmp_path / "specs" / "testgraph" / "bindings.yml").write_text("actions: {}\n", encoding="utf-8")

    written = scaffold_ticket_directory(tmp_path, "AUTH-127", force=False, dry_run=False)
    ticket_dir = tmp_path / "specs" / "tickets" / "AUTH-127"

    assert ticket_dir / "ticket.yaml" in written
    assert (ticket_dir / "current" / "ProgramModel.tla").exists()
    assert (ticket_dir / "desired" / "ProgramModel.tla").exists()
    assert not (ticket_dir / "current" / "tests" / "test_current_ticket_workflow.py").exists()
    assert not (ticket_dir / "desired" / "tests" / "test_current_ticket_workflow.py").exists()
    assert (ticket_dir / "tests" / "test_ticket_workflow.py").exists()
    assert (ticket_dir / "testgraph" / "bindings.yml").read_text(encoding="utf-8") == "actions: {}\n"
    ticket_state = json.loads((ticket_dir / "ticket.yaml").read_text(encoding="utf-8"))
    assert ticket_state["ticket_id"] == "AUTH-127"
    assert ticket_state["promotion"]["on_close"] == "promote ticket desired/ to project current/"


def test_close_ticket_moves_ticket_directory_to_history_and_promotes_desired(tmp_path: Path) -> None:
    write_program_model(tmp_path)
    scaffold(tmp_path, "AUTH-128", "Close parallel ticket", force=False, dry_run=False)
    scaffold_ticket_directory(tmp_path, "AUTH-128", force=False, dry_run=False)
    ticket_dir = tmp_path / "specs" / "tickets" / "AUTH-128"
    finished_tla = "---- MODULE ProgramModel ----\nFinished == TRUE\n====\n"
    (ticket_dir / "current" / "ProgramModel.tla").write_text(finished_tla, encoding="utf-8")
    (ticket_dir / "desired" / "ProgramModel.tla").write_text(finished_tla, encoding="utf-8")
    (ticket_dir / "testgraph").mkdir()
    (ticket_dir / "testgraph" / "report.json").write_text('{"passed": true}\n', encoding="utf-8")
    (tmp_path / "specs" / "desired_program_model" / "ticket_plan.yaml").write_text(
        """version: 1
name: desired-ticket-workflow
tickets:
  - id: AUTH-128
    title: Close parallel ticket
    status: done
""",
        encoding="utf-8",
    )

    result = create_ticket_history_entry(
        repo_root=tmp_path,
        spec_root=Path("specs"),
        ticket_ref="AUTH-128",
        summary="closed",
        result_paths=[],
    )
    manifest = json.loads((result.entry_dir / "manifest.json").read_text(encoding="utf-8"))

    assert not ticket_dir.exists()
    assert (result.entry_dir / "ticket" / "current" / "ProgramModel.tla").read_text(encoding="utf-8") == finished_tla
    assert (result.entry_dir / "ticket" / "testgraph" / "report.json").exists()
    assert (tmp_path / "specs" / "current" / "ProgramModel.tla").read_text(encoding="utf-8") == finished_tla
    assert manifest["promotion"]["operation"] == "replace project current with ticket desired"


def test_close_ticket_requires_ticket_current_to_match_desired(tmp_path: Path) -> None:
    write_program_model(tmp_path)
    scaffold(tmp_path, "AUTH-129", "Reject divergent ticket", force=False, dry_run=False)
    scaffold_ticket_directory(tmp_path, "AUTH-129", force=False, dry_run=False)
    ticket_dir = tmp_path / "specs" / "tickets" / "AUTH-129"
    (ticket_dir / "current" / "ProgramModel.tla").write_text("current\n", encoding="utf-8")
    (ticket_dir / "desired" / "ProgramModel.tla").write_text("desired\n", encoding="utf-8")
    (tmp_path / "specs" / "desired_program_model" / "ticket_plan.yaml").write_text(
        """tickets:
  - id: AUTH-129
    status: done
""",
        encoding="utf-8",
    )

    try:
        create_ticket_history_entry(
            repo_root=tmp_path,
            spec_root=Path("specs"),
            ticket_ref="AUTH-129",
            summary="closed",
            result_paths=[],
        )
    except SystemExit as exc:
        assert "cannot close ticket-local workflow" in str(exc)
        assert "semantic file differs: ProgramModel.tla" in str(exc)
    else:
        raise AssertionError("expected divergent ticket current/desired to block close")


def test_scaffold_ticket_workflow_requires_program_model_baseline(tmp_path: Path) -> None:
    try:
        scaffold(tmp_path, "AUTH-126", "No baseline", force=False, dry_run=False)
    except SystemExit as exc:
        assert "Run onboard_program_model.py first" in str(exc)
    else:
        raise AssertionError("expected missing baseline to fail")


def test_scaffold_ticket_workflow_preserves_existing_files(tmp_path: Path) -> None:
    write_program_model(tmp_path)
    existing = tmp_path / "specs" / "desired_program_model" / "ticket_plan.yaml"
    existing.parent.mkdir(parents=True)
    existing.write_text("keep: true\n", encoding="utf-8")

    scaffold(tmp_path, "T-1", "Keep existing", force=False, dry_run=False)

    assert existing.read_text(encoding="utf-8") == "keep: true\n"


def test_close_ticket_workflow_removes_current_and_desired_after_semantic_match(tmp_path: Path) -> None:
    program = tmp_path / "specs" / "program_model"
    current = tmp_path / "specs" / "current"
    desired = tmp_path / "specs" / "desired_program_model"
    program.mkdir(parents=True)
    current.mkdir(parents=True)
    desired.mkdir(parents=True)
    for directory in [program, current, desired]:
        (directory / "ProgramModel.tla").write_text("---- MODULE ProgramModel ----\n====\n", encoding="utf-8")
        (directory / "MC.cfg").write_text("SPECIFICATION Spec\n", encoding="utf-8")
    (desired / "ticket_plan.yaml").write_text(
        """tickets:
  - id: AUTH-123
    status: done
""",
        encoding="utf-8",
    )

    removed = close_ticket_workflow(tmp_path, Path("specs"), dry_run=False)

    entry_dir = tmp_path / "specs" / ".history" / "spec-workflow" / "closed-snapshot"
    manifest = json.loads((entry_dir / "manifest.json").read_text(encoding="utf-8"))

    assert removed == [current, desired]
    assert not current.exists()
    assert not desired.exists()
    assert entry_dir.stat().st_mode & 0o200
    assert (entry_dir / "manifest.json").stat().st_mode & 0o200
    assert manifest["history_policy"].startswith("append-only by convention")
    assert "immutable_permissions" not in manifest


def test_close_ticket_workflow_reports_semantic_differences(tmp_path: Path) -> None:
    current = tmp_path / "specs" / "current"
    desired = tmp_path / "specs" / "desired_program_model"
    current.mkdir(parents=True)
    desired.mkdir(parents=True)
    (current / "ProgramModel.tla").write_text("current\n", encoding="utf-8")
    (desired / "ProgramModel.tla").write_text("desired\n", encoding="utf-8")

    assert validate_equivalent(current, desired) == ["semantic file differs: ProgramModel.tla"]


def test_close_ticket_workflow_requires_closed_tickets(tmp_path: Path) -> None:
    program = tmp_path / "specs" / "program_model"
    current = tmp_path / "specs" / "current"
    desired = tmp_path / "specs" / "desired_program_model"
    for directory in [program, current, desired]:
        directory.mkdir(parents=True)
        (directory / "ProgramModel.tla").write_text("---- MODULE ProgramModel ----\n====\n", encoding="utf-8")
        (directory / "MC.cfg").write_text("SPECIFICATION Spec\n", encoding="utf-8")
    (desired / "ticket_plan.yaml").write_text(
        """tickets:
  - id: AUTH-123
    status: next
""",
        encoding="utf-8",
    )

    try:
        close_ticket_workflow(tmp_path, Path("specs"), dry_run=True)
    except SystemExit as exc:
        assert "ticket AUTH-123 is not closed" in str(exc)
    else:
        raise AssertionError("expected open ticket to block closeout")


def test_close_ticket_workflow_requires_program_model_promotion(tmp_path: Path) -> None:
    program = tmp_path / "specs" / "program_model"
    current = tmp_path / "specs" / "current"
    desired = tmp_path / "specs" / "desired_program_model"
    for directory in [program, current, desired]:
        directory.mkdir(parents=True)
        (directory / "MC.cfg").write_text("SPECIFICATION Spec\n", encoding="utf-8")
    (program / "ProgramModel.tla").write_text("program\n", encoding="utf-8")
    (current / "ProgramModel.tla").write_text("converged\n", encoding="utf-8")
    (desired / "ProgramModel.tla").write_text("converged\n", encoding="utf-8")
    (desired / "ticket_plan.yaml").write_text(
        """tickets:
  - id: AUTH-123
    status: done
""",
        encoding="utf-8",
    )

    try:
        close_ticket_workflow(tmp_path, Path("specs"), dry_run=True)
    except SystemExit as exc:
        assert "semantic file differs: ProgramModel.tla" in str(exc)
    else:
        raise AssertionError("expected unpromoted program_model to block closeout")
