import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import tla_spec_dev


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "tla_spec_dev.py"), *args],
        cwd=ROOT,
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
    result = run_cli("--spec-root", "project_specs", "scaffold", "project")

    assert result.returncode == 2
    assert "spec root: project_specs" in result.stderr
    assert "CLI-003" in result.stderr


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
