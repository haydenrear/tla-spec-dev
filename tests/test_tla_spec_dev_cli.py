import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import tla_spec_dev
from scripts.generate_cases_from_tlc_dump import ActionMetadata, Edge, render_python_package


def run_cli(*args: str, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "tla_spec_dev.py"), *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def test_cli_version_uses_skill_manifest_version() -> None:
    result = run_cli("--version")

    assert result.returncode == 0
    assert result.stdout.strip() == f"tla-spec-dev {tla_spec_dev.skill_version()}"


def test_cli_root_help_progressively_exposes_workflow_commands() -> None:
    result = run_cli("--help")

    assert result.returncode == 0
    assert "--spec-root" in result.stdout
    assert "scaffold" in result.stdout
    assert "open" in result.stdout
    assert "run" in result.stdout
    assert "close" in result.stdout
    assert "scaffold project -> scaffold workflow -> open ticket" in result.stdout


def test_cli_subcommand_help_documents_external_command_surface() -> None:
    commands = [
        ("scaffold", "--help", "project", "workflow"),
        ("scaffold", "project", "--help", "program_model", "baseline"),
        ("scaffold", "workflow", "--help", "current", "desired_program_model"),
        ("open", "ticket", "--help", "ticket_name", "desired-first"),
        ("run", "spec-unit-tests", "--help", "generated/adapted", "spec root"),
        ("close", "ticket", "--help", "append-only history", "ticket_name"),
    ]

    for args in commands:
        *argv, first_expected, second_expected = args
        result = run_cli(*argv)
        assert result.returncode == 0
        assert first_expected in result.stdout
        assert second_expected in result.stdout


def test_run_spec_unit_tests_fails_when_no_spec_tests_exist(tmp_path: Path) -> None:
    result = run_cli("--spec-root", "project_specs", "run", "spec-unit-tests", cwd=tmp_path)

    assert result.returncode == 2
    assert "spec-unit target does not exist" in result.stderr


def test_incomplete_parent_commands_fail_with_next_step_guidance() -> None:
    for command in ["scaffold", "open", "run", "close"]:
        result = run_cli(command)

        assert result.returncode == 2
        assert f"incomplete command: tla-spec-dev {command}" in result.stderr
        assert "next:" in result.stderr


def test_cli_scaffold_project_and_workflow_use_spec_root(tmp_path: Path) -> None:
    result_project = run_cli(
        "--spec-root",
        "project_specs",
        "scaffold",
        "project",
        "--name",
        "CliProject",
        cwd=tmp_path,
    )
    result_workflow = run_cli(
        "--spec-root",
        "project_specs",
        "scaffold",
        "workflow",
        "CLI-123",
        "CLI scaffold ticket",
        cwd=tmp_path,
    )

    assert result_project.returncode == 0, result_project.stderr
    assert result_workflow.returncode == 0, result_workflow.stderr
    for view_file in ("Core.tla", "Internal.tla", "External.tla", "adapters.py", "testgraph_bindings.yml"):
        assert (tmp_path / "project_specs/program_model" / view_file).exists()
        assert (tmp_path / "project_specs/current" / view_file).exists()
        assert (tmp_path / "project_specs/desired_program_model" / view_file).exists()
    # The three-module baseline must not leave a single-module stand-in behind.
    assert not (tmp_path / "project_specs/current/CliProject.tla").exists()
    assert not (tmp_path / "project_specs/current/MC.cfg").exists()
    assert not (tmp_path / "project_specs/current/tests/test_program_model_onboarding.py").exists()
    assert not (tmp_path / "project_specs/desired_program_model/tests/test_program_model_onboarding.py").exists()
    assert "CLI-123" in (tmp_path / "project_specs/desired_program_model/ticket_plan.yaml").read_text(encoding="utf-8")


def test_cli_run_spec_unit_tests_uses_project_current_tests(tmp_path: Path) -> None:
    run_cli("--spec-root", "project_specs", "scaffold", "project", "--name", "CliProject", cwd=tmp_path)
    run_cli("--spec-root", "project_specs", "scaffold", "workflow", "CLI-201", "CLI unit tests", cwd=tmp_path)

    result = run_cli("--spec-root", "project_specs", "run", "spec-unit-tests", "--scope", "project", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert "spec-unit validation passed" in result.stdout
    assert "project_specs/current" in result.stdout


def test_cli_run_spec_unit_tests_targets_active_ticket_current(tmp_path: Path) -> None:
    ticket_id = "CLI-202"
    run_cli("--spec-root", "project_specs", "scaffold", "project", "--name", "CliProject", cwd=tmp_path)
    run_cli("--spec-root", "project_specs", "scaffold", "workflow", ticket_id, "CLI ticket unit tests", cwd=tmp_path)
    run_cli("--spec-root", "project_specs", "open", "ticket", ticket_id, cwd=tmp_path)
    ticket_test = tmp_path / "project_specs" / "tickets" / ticket_id / "current" / "tests" / "test_ticket_unit.py"
    ticket_test.parent.mkdir(parents=True, exist_ok=True)
    ticket_test.write_text("def test_ticket_unit():\n    assert True\n", encoding="utf-8")

    result = run_cli("--spec-root", "project_specs", "run", "spec-unit-tests", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert "project_specs/current" in result.stdout
    assert f"project_specs/tickets/{ticket_id}/current" in result.stdout


def test_cli_run_spec_unit_tests_auto_includes_project_current_tests(tmp_path: Path) -> None:
    ticket_id = "CLI-204"
    run_cli("--spec-root", "project_specs", "scaffold", "project", "--name", "CliProject", cwd=tmp_path)
    run_cli("--spec-root", "project_specs", "scaffold", "workflow", ticket_id, "CLI active ticket tests", cwd=tmp_path)
    run_cli("--spec-root", "project_specs", "open", "ticket", ticket_id, cwd=tmp_path)
    project_test = tmp_path / "project_specs" / "current" / "tests" / "test_project_current_failure.py"
    project_test.parent.mkdir(parents=True, exist_ok=True)
    project_test.write_text("def test_project_current_failure():\n    assert False\n", encoding="utf-8")
    ticket_test = tmp_path / "project_specs" / "tickets" / ticket_id / "current" / "tests" / "test_ticket_unit.py"
    ticket_test.parent.mkdir(parents=True, exist_ok=True)
    ticket_test.write_text("def test_ticket_unit():\n    assert True\n", encoding="utf-8")

    result = run_cli("--spec-root", "project_specs", "run", "spec-unit-tests", cwd=tmp_path)

    assert result.returncode != 0
    assert "project_specs/current" in result.stdout
    assert f"project_specs/tickets/{ticket_id}/current" in result.stdout
    assert "test_project_current_failure" in result.stdout


def test_cli_run_spec_unit_tests_fails_when_any_selected_target_has_no_validations(tmp_path: Path) -> None:
    ticket_id = "CLI-205"
    spec_root = tmp_path / "project_specs"
    (spec_root / "current").mkdir(parents=True)
    plan = spec_root / "desired_program_model" / "ticket_plan.yaml"
    plan.parent.mkdir(parents=True)
    plan.write_text(
        f"""status:
  active_ticket: {ticket_id}
tickets:
  - id: {ticket_id}
    status: next
""",
        encoding="utf-8",
    )
    ticket_test = spec_root / "tickets" / ticket_id / "current" / "tests" / "test_ticket_unit.py"
    ticket_test.parent.mkdir(parents=True)
    ticket_test.write_text("def test_ticket_unit():\n    assert True\n", encoding="utf-8")

    result = run_cli("--spec-root", "project_specs", "run", "spec-unit-tests", cwd=tmp_path)

    assert result.returncode == 2
    assert "project_specs/current" in result.stderr
    assert "no spec-unit pytest tests or generated case packages found" in result.stderr


def test_cli_run_spec_unit_tests_runs_generated_case_adapters(tmp_path: Path) -> None:
    spec_root = tmp_path / "project_specs"
    current = spec_root / "current"
    generated = spec_root / "generated" / "spec-unit" / "sample_cases"
    current.mkdir(parents=True)
    render_python_package(
        module="CliProject",
        states={"0": {"items": frozenset()}, "1": {"items": frozenset({"a"})}},
        edges=[Edge("0", "1", "Create")],
        package_dir=generated,
        view="internal",
        action_metadata={"Create": ActionMetadata("Create", "internal", "unit_direct", ("spec_unit",))},
    )
    (current / "case_adapters.toml").write_text(
        '[adapters.Create]\nadapter = "production_adapters:CreateAdapter"\n',
        encoding="utf-8",
    )
    (current / "production_adapters.py").write_text(
        """from spec_double_compiler.runtime import CaseRunResult


class CreateAdapter:
    def run(self, case, work_dir=None):
        return CaseRunResult(after=case.after, output=case.output)
""",
        encoding="utf-8",
    )

    result = run_cli("--spec-root", "project_specs", "run", "spec-unit-tests", "--scope", "project", cwd=tmp_path)

    assert result.returncode == 0, result.stderr
    assert "executed 1 cases in batch" in result.stdout


def test_cli_open_ticket_and_close_ticket_use_spec_root(tmp_path: Path) -> None:
    ticket_id = "CLI-200"
    result_project = run_cli(
        "--spec-root",
        "project_specs",
        "scaffold",
        "project",
        "--name",
        "CliProject",
        cwd=tmp_path,
    )
    result_workflow = run_cli(
        "--spec-root",
        "project_specs",
        "scaffold",
        "workflow",
        ticket_id,
        "CLI ticket lifecycle",
        cwd=tmp_path,
    )
    result_open = run_cli(
        "--spec-root",
        "project_specs",
        "open",
        "ticket",
        ticket_id,
        cwd=tmp_path,
    )

    assert result_project.returncode == 0, result_project.stderr
    assert result_workflow.returncode == 0, result_workflow.stderr
    assert result_open.returncode == 0, result_open.stderr
    assert "Edit" in result_open.stdout
    assert "desired" in result_open.stdout
    ticket_dir = tmp_path / "project_specs" / "tickets" / ticket_id
    assert (ticket_dir / "desired" / "External.tla").exists()
    assert (ticket_dir / "current" / "External.tla").exists()
    assert (ticket_dir / "desired" / "testgraph_bindings.yml").exists()

    plan_path = tmp_path / "project_specs" / "desired_program_model" / "ticket_plan.yaml"
    plan_path.write_text(plan_path.read_text(encoding="utf-8").replace("status: next", "status: done", 1), encoding="utf-8")
    result_close = run_cli(
        "--spec-root",
        "project_specs",
        "close",
        "ticket",
        ticket_id,
        "--summary",
        "closed from CLI test",
        cwd=tmp_path,
    )

    history_dir = tmp_path / "project_specs" / ".history" / "desired-ticket-workflow" / f"ticket-000-{ticket_id}"
    assert result_close.returncode == 0, result_close.stderr
    assert "recorded spec history entry" in result_close.stdout
    assert not ticket_dir.exists()
    assert (history_dir / "manifest.json").exists()
    assert (history_dir / "ticket" / "desired" / "External.tla").exists()
    assert (tmp_path / "project_specs" / "current" / "External.tla").exists()


def test_cli_open_ticket_records_custom_ticket_root_in_close_guidance(tmp_path: Path) -> None:
    ticket_id = "CLI-203"
    run_cli("--spec-root", "project_specs", "scaffold", "project", "--name", "CliProject", cwd=tmp_path)
    run_cli("--spec-root", "project_specs", "scaffold", "workflow", ticket_id, "Custom ticket root", cwd=tmp_path)

    result_open = run_cli(
        "--spec-root",
        "project_specs",
        "open",
        "ticket",
        ticket_id,
        "--ticket-root",
        "work/items",
        cwd=tmp_path,
    )

    ticket_state = (tmp_path / "project_specs" / "work" / "items" / ticket_id / "ticket.yaml").read_text(
        encoding="utf-8"
    )
    assert result_open.returncode == 0, result_open.stderr
    assert "close ticket CLI-203 --ticket-root work/items" in result_open.stdout
    assert "tla-spec-dev --spec-root project_specs close ticket CLI-203 --ticket-root work/items" in ticket_state


def test_skill_script_installs_tla_spec_dev_wrapper(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    cache_dir = tmp_path / "cache"
    env = {
        **os.environ,
        "SKILL_MANAGER_BIN_DIR": str(bin_dir),
        "SKILL_MANAGER_CACHE_DIR": str(cache_dir),
        "SKILL_DIR": str(ROOT),
        "SKILL_NAME": "spec-double-compiler",
    }

    install = subprocess.run(
        ["bash", str(ROOT / "skill-scripts" / "install-tla-spec-dev.sh")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )
    wrapper = bin_dir / "tla-spec-dev"
    installed = subprocess.run(
        [str(wrapper), "--version"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )

    assert install.returncode == 0, install.stderr
    assert wrapper.exists()
    assert os.access(wrapper, os.X_OK)
    assert installed.returncode == 0
    assert installed.stdout.strip() == f"tla-spec-dev {tla_spec_dev.skill_version()}"
