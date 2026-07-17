"""Ticket-local adapters for the shipped tla-spec-dev CLI entrypoint."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "skill-manager.toml").is_file() and (parent / "scripts" / "tla_spec_dev.py").is_file():
            return parent
    raise RuntimeError("could not locate tla-spec-dev repository root")


class BuildSkillCliAdapter:
    action_name = "BuildSkillCli"

    def apply(self) -> dict[str, object]:
        root = repo_root()
        entrypoint = root / "scripts" / "tla_spec_dev.py"
        installer = root / "skill-scripts" / "install-tla-spec-dev.sh"
        return {
            "accepted": entrypoint.is_file() and installer.is_file(),
            "entrypoint": str(entrypoint),
            "installer": str(installer),
        }


class InstallLocalCliAdapter:
    action_name = "InstallLocalCli"

    def apply(self, bin_dir: Path, cache_dir: Path) -> dict[str, object]:
        root = repo_root()
        env = {
            **os.environ,
            "SKILL_MANAGER_BIN_DIR": str(bin_dir),
            "SKILL_MANAGER_CACHE_DIR": str(cache_dir),
            "SKILL_DIR": str(root),
            "SKILL_NAME": "spec-double-compiler",
        }
        install = subprocess.run(
            ["bash", str(root / "skill-scripts" / "install-tla-spec-dev.sh")],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        wrapper = bin_dir / "tla-spec-dev"
        version = subprocess.run(
            [str(wrapper), "--version"],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        ) if wrapper.exists() else None
        return {
            "accepted": install.returncode == 0 and version is not None and version.returncode == 0,
            "install_exit_code": install.returncode,
            "version_exit_code": None if version is None else version.returncode,
            "version": "" if version is None else version.stdout.strip(),
            "wrapper": str(wrapper),
        }


class ScaffoldProjectAdapter:
    action_name = "ScaffoldProject"

    def apply(self, target_repo: Path, *, spec_root: str = "specs", name: str = "CliProject") -> dict[str, object]:
        root = repo_root()
        result = subprocess.run(
            [
                sys.executable,
                str(root / "scripts" / "tla_spec_dev.py"),
                "--spec-root",
                spec_root,
                "scaffold",
                "project",
                "--name",
                name,
            ],
            cwd=target_repo,
            text=True,
            capture_output=True,
            check=False,
        )
        return {
            "accepted": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "program_model": str(target_repo / spec_root / "program_model" / f"{name}.tla"),
        }


class ScaffoldWorkflowAdapter:
    action_name = "ScaffoldWorkflow"

    def apply(
        self,
        target_repo: Path,
        *,
        spec_root: str = "specs",
        ticket_id: str = "CLI-123",
        title: str = "CLI scaffold ticket",
    ) -> dict[str, object]:
        root = repo_root()
        result = subprocess.run(
            [
                sys.executable,
                str(root / "scripts" / "tla_spec_dev.py"),
                "--spec-root",
                spec_root,
                "scaffold",
                "workflow",
                ticket_id,
                title,
            ],
            cwd=target_repo,
            text=True,
            capture_output=True,
            check=False,
        )
        return {
            "accepted": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "current": str(target_repo / spec_root / "current"),
            "desired": str(target_repo / spec_root / "desired_program_model"),
        }


def run_cli(root: Path, target_repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "tla_spec_dev.py"), *args],
        cwd=target_repo,
        text=True,
        capture_output=True,
        check=False,
    )


def prepare_ticket_workflow(
    root: Path,
    target_repo: Path,
    *,
    spec_root: str,
    ticket_id: str,
    title: str,
) -> list[subprocess.CompletedProcess[str]]:
    return [
        run_cli(root, target_repo, "--spec-root", spec_root, "scaffold", "project", "--name", "CliProject"),
        run_cli(root, target_repo, "--spec-root", spec_root, "scaffold", "workflow", ticket_id, title),
    ]


class OpenTicketAdapter:
    action_name = "OpenTicket"

    def apply(
        self,
        target_repo: Path,
        *,
        spec_root: str = "specs",
        ticket_id: str = "CLI-124",
        title: str = "CLI ticket lifecycle",
    ) -> dict[str, object]:
        root = repo_root()
        setup = prepare_ticket_workflow(root, target_repo, spec_root=spec_root, ticket_id=ticket_id, title=title)
        result = run_cli(root, target_repo, "--spec-root", spec_root, "open", "ticket", ticket_id)
        ticket_dir = target_repo / spec_root / "tickets" / ticket_id
        return {
            "accepted": all(record.returncode == 0 for record in setup)
            and result.returncode == 0
            and (ticket_dir / "desired" / "CliProject.tla").is_file()
            and (ticket_dir / "current" / "CliProject.tla").is_file()
            and "Edit" in result.stdout
            and "desired" in result.stdout,
            "setup_exit_codes": [record.returncode for record in setup],
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "ticket_dir": str(ticket_dir),
        }


class CloseTicketAdapter:
    action_name = "CloseTicket"

    def apply(
        self,
        target_repo: Path,
        *,
        spec_root: str = "specs",
        ticket_id: str = "CLI-125",
        title: str = "CLI close ticket lifecycle",
    ) -> dict[str, object]:
        root = repo_root()
        setup = prepare_ticket_workflow(root, target_repo, spec_root=spec_root, ticket_id=ticket_id, title=title)
        opened = run_cli(root, target_repo, "--spec-root", spec_root, "open", "ticket", ticket_id)
        plan_path = target_repo / spec_root / "desired_program_model" / "ticket_plan.yaml"
        if plan_path.exists():
            plan_path.write_text(plan_path.read_text(encoding="utf-8").replace("status: next", "status: done", 1), encoding="utf-8")
        result = run_cli(
            root,
            target_repo,
            "--spec-root",
            spec_root,
            "close",
            "ticket",
            ticket_id,
            "--summary",
            "closed from ticket lifecycle adapter",
        )
        ticket_dir = target_repo / spec_root / "tickets" / ticket_id
        history_dir = target_repo / spec_root / ".history" / "desired-ticket-workflow" / f"ticket-000-{ticket_id}"
        return {
            "accepted": all(record.returncode == 0 for record in setup)
            and opened.returncode == 0
            and result.returncode == 0
            and not ticket_dir.exists()
            and (history_dir / "manifest.json").is_file()
            and (target_repo / spec_root / "current" / "CliProject.tla").is_file(),
            "setup_exit_codes": [record.returncode for record in setup],
            "open_exit_code": opened.returncode,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "history_dir": str(history_dir),
        }


class RunSpecUnitTestsAdapter:
    action_name = "RunSpecUnitTests"

    def apply(
        self,
        target_repo: Path,
        *,
        spec_root: str = "specs",
        ticket_id: str = "CLI-126",
        title: str = "CLI run spec-unit tests",
    ) -> dict[str, object]:
        root = repo_root()
        setup = prepare_ticket_workflow(root, target_repo, spec_root=spec_root, ticket_id=ticket_id, title=title)
        opened = run_cli(root, target_repo, "--spec-root", spec_root, "open", "ticket", ticket_id)
        ticket_current = target_repo / spec_root / "tickets" / ticket_id / "current"
        test_path = ticket_current / "tests" / "test_spec_unit_cli.py"
        test_path.parent.mkdir(parents=True, exist_ok=True)
        test_path.write_text("def test_spec_unit_cli():\n    assert True\n", encoding="utf-8")
        result = run_cli(root, target_repo, "--spec-root", spec_root, "run", "spec-unit-tests")
        return {
            "accepted": all(record.returncode == 0 for record in setup)
            and opened.returncode == 0
            and result.returncode == 0
            and str(ticket_current) in result.stdout
            and "spec-unit validation passed" in result.stdout,
            "setup_exit_codes": [record.returncode for record in setup],
            "open_exit_code": opened.returncode,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "ticket_current": str(ticket_current),
        }


class TestGraphCliAdapter:
    action_name = "ValidateTestGraphCli"

    def apply(self) -> dict[str, object]:
        root = repo_root()
        build = root / "test_graph" / "build.gradle.kts"
        readme = root / "test_graph" / "README.md"
        required_sources = [
            root / "test_graph" / "sources" / "tla_spec_dev_cli_install.py",
            root / "test_graph" / "sources" / "spec_workflow_create_repo.py",
            root / "test_graph" / "sources" / "spec_workflow_start_ticket.py",
            root / "test_graph" / "sources" / "spec_workflow_complete_ticket.py",
            root / "test_graph" / "sources" / "spec_workflow_spec_units.py",
            root / "test_graph" / "sources" / "spec_workflow_close_ticket.py",
            root / "test_graph" / "sources" / "spec_workflow_failure_cleanup_probe.py",
            root / "test_graph" / "sources" / "spec_workflow_cleanup.py",
        ]
        build_text = build.read_text(encoding="utf-8") if build.exists() else ""
        readme_text = readme.read_text(encoding="utf-8") if readme.exists() else ""
        required_fragments = [
            "testGraph(\"specWorkflow\")",
            "sources/tla_spec_dev_cli_install.py",
            "sources/spec_workflow_start_ticket.py",
            "sources/spec_workflow_spec_units.py",
            "sources/spec_workflow_close_ticket.py",
            "sources/spec_workflow_failure_cleanup_probe.py",
            "sources/spec_workflow_cleanup.py",
        ]
        return {
            "accepted": all(path.is_file() for path in required_sources)
            and all(fragment in build_text for fragment in required_fragments)
            and "tla-spec-dev --spec-root specs run spec-unit-tests" in readme_text
            and "cleanup after both passing and failing" in readme_text,
            "build": str(build),
            "readme": str(readme),
            "required_sources": [str(path) for path in required_sources],
            "missing_sources": [str(path) for path in required_sources if not path.is_file()],
        }
