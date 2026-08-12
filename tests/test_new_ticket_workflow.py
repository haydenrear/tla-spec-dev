import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.new_ticket_workflow import scaffold, scaffold_ticket_directory
from scripts.close_tickets import close_ticket_workflow, validate_equivalent
from scripts.spec_evolution import create_ticket_history_entry
from conftest import write_ticket_ledger_input, write_workflow_ledger_input


def stub_program_model(marker: str) -> str:
    """A COMPLETE ProgramModel carrying a per-fixture marker.

    CM-01: the complexity ledger refuses a pair whose cfg names a
    SPECIFICATION, invariant, or constant the module does not define -- that is
    the CM-F1 defect, "I could not measure this" instead of a silent
    ``bound = None``. These fixtures previously wrote a one-line module beside
    the real ``MC.cfg``, and the ledger dutifully measured 0 variables and 0
    actions for it. The marker keeps each fixture's identity; the module is now
    something MC.cfg actually configures.
    """
    return f"""---- MODULE ProgramModel ----
EXTENDS Naturals, TLC

CONSTANTS Items
VARIABLES seen
vars == << seen >>
Init == seen = {{}}
Add(i) == seen' = seen \\cup {{i}}
Next == \\E i \\in Items: Add(i)
SeenKnown == seen \\subseteq Items
Spec == Init /\\ [][Next]_vars
{marker} == TRUE
====
"""


def write_successful_ticket_receipt(
    specs_dir: Path,
    ticket_id: str,
    *,
    ticket_index: int = 0,
    workflow: str = "spec-workflow",
    status: str = "done",
) -> Path:
    """Write the minimal successful-close identity contract used by closeout tests."""
    manifest_path = (
        specs_dir
        / ".history"
        / workflow
        / f"ticket-{ticket_index:03d}-{ticket_id}"
        / "manifest.json"
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "kind": "ticket",
                "workflow_name": workflow,
                "ticket_index": ticket_index,
                "ticket_id": ticket_id,
                "ticket_status": status,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest_path


def test_skill_requires_two_minute_case_generation_budget() -> None:
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    generation_modes = (ROOT / "references" / "generation_modes.md").read_text(encoding="utf-8")

    assert "hard 120-second timeout" in skill
    assert "Do not simply raise the timeout" in skill
    assert "perform bounded discovery of the state explosion" in skill
    assert "accidental complexity" in skill
    assert "Provide concrete recommendations" in skill
    assert "discuss the tradeoff with the user" in skill
    # RP-05 (CM-01-DF-01/AC-DF-01): this used to assert the literal prose
    # "hard two-minute budget", which the c72d03a docs refresh rewrote to
    # "hard wall-time budget: `budgets.tlc_seconds` ... default 120 seconds" --
    # naming the actual config knob instead of hardcoding a sentence that
    # drifts the moment someone rewords the page. Assert the durable fact the
    # budget is documented as (the config key and its value), not exact prose.
    assert "budgets.tlc_seconds" in generation_modes
    assert "hard wall-time budget" in generation_modes
    assert "120 seconds" in generation_modes
    assert "Distinguish compressible modeling detail from" in generation_modes
    assert "concrete options for lowering" in generation_modes


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
    onboarding_test = program_model / "tests" / "test_program_model_onboarding.py"
    onboarding_test.parent.mkdir()
    onboarding_test.write_text(
        "def test_onboarding_only():\n    assert False, 'must not be copied into ticket workflow models'\n",
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
    assert not (tmp_path / "specs/current/tests/test_program_model_onboarding.py").exists()
    assert not (tmp_path / "specs/desired_program_model/tests/test_program_model_onboarding.py").exists()


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
    assert ticket_state["promotion"]["on_close"] == (
        "promote ticket desired/ onto project current/ (removing only seeded paths this ticket "
        "dropped, preserving unseeded current-only paths) and merge Test Graph artifacts into project specs/"
    )
    # MF-021: `open` records exactly what it seeded so promotion can tell a
    # deliberate deletion from a file the ticket was never given.
    seed = ticket_state["seed_manifest"]
    assert seed["excluded"] == ["tests/test_current_ticket_workflow.py"]
    assert "ProgramModel.tla" in seed["desired"]
    assert "tests/test_current_ticket_workflow.py" not in seed["desired"]


def test_start_ticket_records_custom_ticket_root_in_close_guidance(tmp_path: Path) -> None:
    write_program_model(tmp_path)
    scaffold(tmp_path, "AUTH-131", "Custom ticket root", force=False, dry_run=False)

    scaffold_ticket_directory(
        tmp_path,
        "AUTH-131",
        force=False,
        dry_run=False,
        ticket_root=Path("work/items"),
    )

    ticket_dir = tmp_path / "specs" / "work" / "items" / "AUTH-131"
    ticket_state = json.loads((ticket_dir / "ticket.yaml").read_text(encoding="utf-8"))
    readme = (ticket_dir / "README.md").read_text(encoding="utf-8")

    assert (
        ticket_state["promotion"]["close_command"]
        == "tla-spec-dev --spec-root specs close ticket AUTH-131 --ticket-root work/items"
    )
    assert "close ticket AUTH-131 --ticket-root work/items" in readme


def test_close_ticket_moves_ticket_directory_to_history_and_promotes_desired(tmp_path: Path) -> None:
    write_program_model(tmp_path)
    scaffold(tmp_path, "AUTH-128", "Close parallel ticket", force=False, dry_run=False)

    # MF-021: promotion decides removals by provenance, so this file must exist
    # before the workspace is seeded. It is offered to the ticket, the ticket
    # drops it, and promotion is therefore entitled to remove it.
    seeded_stale = tmp_path / "specs" / "current" / "seeded_stale_adapter.py"
    seeded_stale.write_text("DROPPED_BY_THE_TICKET = True\n", encoding="utf-8")

    scaffold_ticket_directory(tmp_path, "AUTH-128", force=False, dry_run=False)
    ticket_dir = tmp_path / "specs" / "tickets" / "AUTH-128"
    for model_dir in ["current", "desired"]:
        (ticket_dir / model_dir / "seeded_stale_adapter.py").unlink()
    finished_tla = stub_program_model("Finished")
    (ticket_dir / "current" / "ProgramModel.tla").write_text(finished_tla, encoding="utf-8")
    (ticket_dir / "desired" / "ProgramModel.tla").write_text(finished_tla, encoding="utf-8")
    for model_dir in ["current", "desired"]:
        adapter = ticket_dir / model_dir / "adapters" / "unit" / "finished_adapter.py"
        adapter.parent.mkdir(parents=True, exist_ok=True)
        adapter.write_text("ADAPTER_READY = True\n", encoding="utf-8")
        test_file = ticket_dir / model_dir / "tests" / "test_finished_adapter.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("def test_adapter_ready():\n    assert True\n", encoding="utf-8")
    (ticket_dir / "testgraph").mkdir()
    (ticket_dir / "testgraph" / "report.json").write_text('{"passed": true}\n', encoding="utf-8")
    for model_dir in ["current", "desired"]:
        states = ticket_dir / model_dir / "states"
        states.mkdir()
        (states / "large-state-dump.json").write_text('{"generated": true}\n', encoding="utf-8")
    for model_dir in ["program_model", "current", "desired_program_model"]:
        states = tmp_path / "specs" / model_dir / "states"
        states.mkdir()
        (states / "large-state-dump.json").write_text('{"generated": true}\n', encoding="utf-8")
    # MF-021: written to project current/ AFTER the workspace was seeded, so
    # the ticket was never offered it and recorded no decision about it. This
    # is the shape of the loss that destroyed MF-012's budgets retention test
    # and MF-020's refinement-probe/ directory. It must survive.
    unseeded_current_only = tmp_path / "specs" / "current" / "unseeded_adapter.py"
    unseeded_current_only.write_text("MUST_SURVIVE_PROMOTION = True\n", encoding="utf-8")
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

    write_ticket_ledger_input(ticket_dir)

    result = create_ticket_history_entry(
        repo_root=tmp_path,
        spec_root=Path("specs"),
        ticket_ref="AUTH-128",
        summary="closed",
        result_paths=[],
    )
    manifest = json.loads((result.entry_dir / "manifest.json").read_text(encoding="utf-8"))

    assert not ticket_dir.exists()
    assert not list((tmp_path / "specs").glob("*/states"))
    assert (result.entry_dir / "ticket" / "current" / "ProgramModel.tla").read_text(encoding="utf-8") == finished_tla
    assert (result.entry_dir / "ticket" / "testgraph" / "report.json").exists()
    assert not list(result.entry_dir.rglob("states"))
    assert (tmp_path / "specs" / "current" / "ProgramModel.tla").read_text(encoding="utf-8") == finished_tla
    assert (tmp_path / "specs" / "current" / "adapters" / "unit" / "finished_adapter.py").exists()
    assert (tmp_path / "specs" / "current" / "tests" / "test_finished_adapter.py").exists()
    # specs/current stays a whole-program working copy: a path the ticket was
    # given and deliberately dropped is still removed.
    assert not seeded_stale.exists()
    # ...but it is not an accumulating union either -- and never a graveyard:
    # a path the ticket never saw is preserved, not silently destroyed.
    assert unseeded_current_only.exists()
    assert unseeded_current_only.read_text(encoding="utf-8") == "MUST_SURVIVE_PROMOTION = True\n"

    current_promotion = next(item for item in manifest["promotion"]["merged"] if item["role"] == "current")
    assert current_promotion["removed"] == ["seeded_stale_adapter.py"]
    assert "unseeded_adapter.py" in current_promotion["preserved"]
    assert current_promotion["seed_recorded"] is True

    assert (tmp_path / "specs" / "testgraph" / "report.json").exists()
    assert manifest["promotion"]["operation"] == "replace project current with ticket desired and merge ticket artifacts into project specs"
    assert str(result.entry_dir) in result.git_add_command
    assert str(tmp_path / "specs" / "current") in result.git_add_command
    assert str(tmp_path / "specs" / "testgraph") in result.git_add_command

    ledger_path = tmp_path / "specs" / "results" / "complexity_ledger.json"
    ledger_before_replay = ledger_path.read_bytes()
    try:
        create_ticket_history_entry(
            repo_root=tmp_path,
            spec_root=Path("specs"),
            ticket_ref="AUTH-128",
            summary="replayed close",
            result_paths=[],
        )
    except SystemExit as exc:
        assert "refusing to overwrite existing history entry" in str(exc)
    else:
        raise AssertionError("expected replay of an existing close entry to refuse")
    assert ledger_path.read_bytes() == ledger_before_replay


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


def test_close_ticket_accept_new_promotes_divergent_desired(tmp_path: Path) -> None:
    write_program_model(tmp_path)
    scaffold(tmp_path, "AUTH-131", "Accept new ticket", force=False, dry_run=False)
    scaffold_ticket_directory(tmp_path, "AUTH-131", force=False, dry_run=False)
    ticket_dir = tmp_path / "specs" / "tickets" / "AUTH-131"
    (ticket_dir / "current" / "ProgramModel.tla").write_text("stale current\n", encoding="utf-8")
    desired_tla = stub_program_model("Accepted")
    (ticket_dir / "desired" / "ProgramModel.tla").write_text(desired_tla, encoding="utf-8")
    (tmp_path / "specs" / "desired_program_model" / "ticket_plan.yaml").write_text(
        """tickets:
  - id: AUTH-131
    status: done
""",
        encoding="utf-8",
    )

    write_ticket_ledger_input(ticket_dir)

    result = create_ticket_history_entry(
        repo_root=tmp_path,
        spec_root=Path("specs"),
        ticket_ref="AUTH-131",
        summary="accepted new",
        result_paths=[],
        accept_new=True,
    )
    manifest = json.loads((result.entry_dir / "manifest.json").read_text(encoding="utf-8"))

    assert manifest["accept_new"] is True
    assert manifest["accept_new_promotion"]["operation"] == "replace ticket current with ticket desired (accept-new)"
    # ticket current/ was overwritten from desired/ before being moved to history
    assert (result.entry_dir / "ticket" / "current" / "ProgramModel.tla").read_text(encoding="utf-8") == desired_tla
    # project current/ was promoted from the accepted desired state
    assert (tmp_path / "specs" / "current" / "ProgramModel.tla").read_text(encoding="utf-8") == desired_tla


def test_close_ticket_divergence_error_explains_how_to_prepare(tmp_path: Path) -> None:
    write_program_model(tmp_path)
    scaffold(tmp_path, "AUTH-132", "Divergent ticket guidance", force=False, dry_run=False)
    scaffold_ticket_directory(tmp_path, "AUTH-132", force=False, dry_run=False)
    ticket_dir = tmp_path / "specs" / "tickets" / "AUTH-132"
    (ticket_dir / "current" / "ProgramModel.tla").write_text("current\n", encoding="utf-8")
    (ticket_dir / "desired" / "ProgramModel.tla").write_text("desired\n", encoding="utf-8")
    (tmp_path / "specs" / "desired_program_model" / "ticket_plan.yaml").write_text(
        """tickets:
  - id: AUTH-132
    status: done
""",
        encoding="utf-8",
    )

    try:
        create_ticket_history_entry(
            repo_root=tmp_path,
            spec_root=Path("specs"),
            ticket_ref="AUTH-132",
            summary="closed",
            result_paths=[],
        )
    except SystemExit as exc:
        message = str(exc)
        assert "semantic file differs: ProgramModel.tla" in message
        assert "--accept-new" in message
        assert "How to prepare this ticket for promotion" in message
    else:
        raise AssertionError("expected divergent ticket to block close with guidance")


def test_close_ticket_requires_ticket_adapters_to_match_desired(tmp_path: Path) -> None:
    write_program_model(tmp_path)
    scaffold(tmp_path, "AUTH-130", "Reject divergent adapter", force=False, dry_run=False)
    scaffold_ticket_directory(tmp_path, "AUTH-130", force=False, dry_run=False)
    ticket_dir = tmp_path / "specs" / "tickets" / "AUTH-130"
    current_adapter = ticket_dir / "current" / "adapters" / "unit" / "adapter.py"
    desired_adapter = ticket_dir / "desired" / "adapters" / "unit" / "adapter.py"
    current_adapter.parent.mkdir(parents=True, exist_ok=True)
    desired_adapter.parent.mkdir(parents=True, exist_ok=True)
    current_adapter.write_text("VALUE = 'current'\n", encoding="utf-8")
    desired_adapter.write_text("VALUE = 'desired'\n", encoding="utf-8")
    (tmp_path / "specs" / "desired_program_model" / "ticket_plan.yaml").write_text(
        """tickets:
  - id: AUTH-130
    status: done
""",
        encoding="utf-8",
    )

    try:
        create_ticket_history_entry(
            repo_root=tmp_path,
            spec_root=Path("specs"),
            ticket_ref="AUTH-130",
            summary="closed",
            result_paths=[],
        )
    except SystemExit as exc:
        assert "semantic file differs: adapters/unit/adapter.py" in str(exc)
    else:
        raise AssertionError("expected divergent ticket adapter to block close")


def test_scaffold_ticket_workflow_requires_program_model_baseline(tmp_path: Path) -> None:
    try:
        scaffold(tmp_path, "AUTH-126", "No baseline", force=False, dry_run=False)
    except SystemExit as exc:
        assert "Run 'tla-spec-dev scaffold project' first" in str(exc)
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
        (directory / "ProgramModel.tla").write_text(stub_program_model("Stub"), encoding="utf-8")
        (directory / "MC.cfg").write_text("SPECIFICATION Spec\n", encoding="utf-8")
        states = directory / "states"
        states.mkdir()
        (states / "large-state-dump.json").write_text('{"generated": true}\n', encoding="utf-8")
    (desired / "ticket_plan.yaml").write_text(
        """tickets:
  - id: AUTH-123
    status: done
""",
        encoding="utf-8",
    )

    write_workflow_ledger_input(tmp_path / "specs")
    write_successful_ticket_receipt(tmp_path / "specs", "AUTH-123")

    removed = close_ticket_workflow(tmp_path, Path("specs"), dry_run=False)

    entry_dir = tmp_path / "specs" / ".history" / "spec-workflow" / "closed-snapshot"
    manifest = json.loads((entry_dir / "manifest.json").read_text(encoding="utf-8"))

    assert removed == [current, desired]
    assert not current.exists()
    assert not desired.exists()
    assert not (program / "states").exists()
    assert not list(entry_dir.rglob("states"))
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
        (directory / "ProgramModel.tla").write_text(stub_program_model("Stub"), encoding="utf-8")
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
        message = str(exc)
        assert "semantic file differs: ProgramModel.tla" in message
        assert "--accept-new" in message
        assert "How to prepare this workflow for closeout" in message
    else:
        raise AssertionError("expected unpromoted program_model to block closeout")


def test_close_ticket_workflow_accept_new_promotes_desired_into_program_model(tmp_path: Path) -> None:
    program = tmp_path / "specs" / "program_model"
    current = tmp_path / "specs" / "current"
    desired = tmp_path / "specs" / "desired_program_model"
    for directory in [program, current, desired]:
        directory.mkdir(parents=True)
        (directory / "MC.cfg").write_text("SPECIFICATION Spec\n", encoding="utf-8")
    (program / "ProgramModel.tla").write_text("stale program\n", encoding="utf-8")
    (current / "ProgramModel.tla").write_text("stale current\n", encoding="utf-8")
    accepted_tla = stub_program_model("Accepted")
    (desired / "ProgramModel.tla").write_text(accepted_tla, encoding="utf-8")
    (desired / "ticket_plan.yaml").write_text(
        """tickets:
  - id: AUTH-133
    status: done
""",
        encoding="utf-8",
    )

    write_workflow_ledger_input(tmp_path / "specs")
    write_successful_ticket_receipt(tmp_path / "specs", "AUTH-133")

    removed = close_ticket_workflow(tmp_path, Path("specs"), dry_run=False, accept_new=True)

    # program_model adopts the accepted desired semantic files; planning files are not promoted
    assert (program / "ProgramModel.tla").read_text(encoding="utf-8") == accepted_tla
    assert not (program / "ticket_plan.yaml").exists()
    # current and desired are removed after the snapshot, program_model remains the baseline
    assert removed == [current, desired]
    assert not current.exists()
    assert not desired.exists()
    assert program.exists()


def test_close_ticket_workflow_accept_new_still_requires_closed_tickets(tmp_path: Path) -> None:
    desired = tmp_path / "specs" / "desired_program_model"
    desired.mkdir(parents=True)
    (desired / "ProgramModel.tla").write_text("desired\n", encoding="utf-8")
    (desired / "ticket_plan.yaml").write_text(
        """tickets:
  - id: AUTH-134
    status: next
""",
        encoding="utf-8",
    )

    try:
        close_ticket_workflow(tmp_path, Path("specs"), dry_run=True, accept_new=True)
    except SystemExit as exc:
        assert "ticket AUTH-134 is not closed" in str(exc)
    else:
        raise AssertionError("expected accept-new to still require closed tickets")


def test_scaffold_workflow_carries_accepted_manifest_semantics(tmp_path, monkeypatch):
    """MR-DF-01: scaffold workflow must not regenerate a bare manifest.

    The accepted program_model manifest carries negotiated budgets, effects,
    and justification blocks; the workflow scaffold's template previously
    overwrote them with defaults (boundaries dropped 22->13 the day it
    happened). The semantic tail must be carried verbatim under the fresh
    status header.
    """
    from scripts.new_ticket_workflow import carry_manifest_semantic_tail

    template = (
        "module: X\n"
        "package: current_program_cases\n"
        "status:\n"
        "  workflow: fresh\n"
        "# Per-program complexity and case budgets -- advisory thresholds read by\n"
        "budgets:\n"
        "  max_distinct_states: 50000\n"
    )
    accepted = tmp_path / "spec_manifest.yaml"
    accepted.write_text(
        "module: X\n"
        "status:\n"
        "  workflow: old\n"
        "# Per-program complexity and case budgets. NEGOTIATED SENTINEL.\n"
        "budgets:\n"
        "  max_distinct_states: 500000\n"
        "effects:\n"
        "  components: {}\n",
        encoding="utf-8",
    )
    carried = carry_manifest_semantic_tail(template, accepted)
    assert "workflow: fresh" in carried          # fresh header wins
    assert "workflow: old" not in carried
    assert "NEGOTIATED SENTINEL" in carried      # semantic tail carried
    assert "max_distinct_states: 500000" in carried
    assert "effects:" in carried
    assert "max_distinct_states: 50000\n" not in carried
    # no accepted manifest -> template unchanged
    assert carry_manifest_semantic_tail(template, tmp_path / "missing.yaml") == template
