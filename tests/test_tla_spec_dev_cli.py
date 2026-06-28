import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import tla_spec_dev


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


def test_planned_commands_fail_with_next_ticket_guidance() -> None:
    result = run_cli("--spec-root", "project_specs", "run", "spec-unit-tests")

    assert result.returncode == 2
    assert "spec root: project_specs" in result.stderr
    assert "CLI-005" in result.stderr


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
    assert (tmp_path / "project_specs/program_model/CliProject.tla").exists()
    assert (tmp_path / "project_specs/current/CliProject.tla").exists()
    assert (tmp_path / "project_specs/desired_program_model/CliProject.tla").exists()
    assert not (tmp_path / "project_specs/current/tests/test_program_model_onboarding.py").exists()
    assert not (tmp_path / "project_specs/desired_program_model/tests/test_program_model_onboarding.py").exists()
    assert "CLI-123" in (tmp_path / "project_specs/desired_program_model/ticket_plan.yaml").read_text(encoding="utf-8")


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
    assert (ticket_dir / "desired" / "CliProject.tla").exists()
    assert (ticket_dir / "current" / "CliProject.tla").exists()

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
    assert (history_dir / "ticket" / "desired" / "CliProject.tla").exists()
    assert (tmp_path / "project_specs" / "current" / "CliProject.tla").exists()


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
