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
            and (ticket_dir / "desired" / "Internal.tla").is_file()
            and (ticket_dir / "current" / "Internal.tla").is_file()
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
            and (target_repo / spec_root / "current" / "Internal.tla").is_file(),
            "setup_exit_codes": [record.returncode for record in setup],
            "open_exit_code": opened.returncode,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "history_dir": str(history_dir),
        }


class ClosePromotionPreservesCurrentAdapter:
    """MF-021: drive the shipped CLI and prove promotion does not destroy specs/current.

    Runs the real ``scaffold -> open ticket -> close ticket`` lifecycle against
    a throwaway repository. Between ``open`` and ``close`` it writes two kinds
    of path into project ``specs/current``:

    * ``unseeded_only.py`` -- created after the workspace was seeded, and
      ``probe-dir/note.txt`` inside a current-only directory. Neither was ever
      offered to the ticket, so promotion must preserve both. This is the exact
      shape of the loss that destroyed MF-012's budgets retention test and
      MF-020's ``refinement-probe/`` directory.
    * the project workflow test, which ``open ticket`` excludes from the ticket
      workspace by design and which promotion therefore must never delete.

    It also asserts the close output *enumerates* what it preserved: a silent
    survival would still leave the next regression undetectable.
    """

    action_name = "CloseTicket"

    def apply(
        self,
        target_repo: Path,
        *,
        spec_root: str = "specs",
        ticket_id: str = "CLI-127",
        title: str = "CLI close promotion preserves current",
    ) -> dict[str, object]:
        root = repo_root()
        setup = prepare_ticket_workflow(root, target_repo, spec_root=spec_root, ticket_id=ticket_id, title=title)
        opened = run_cli(root, target_repo, "--spec-root", spec_root, "open", "ticket", ticket_id)

        specs_current = target_repo / spec_root / "current"
        unseeded = specs_current / "unseeded_only.py"
        unseeded.write_text("MUST_SURVIVE_PROMOTION = True\n", encoding="utf-8")
        probe = specs_current / "probe-dir" / "note.txt"
        probe.parent.mkdir(parents=True, exist_ok=True)
        probe.write_text("current-only directory\n", encoding="utf-8")
        workflow_test = specs_current / "tests" / "test_current_ticket_workflow.py"
        workflow_test_existed = workflow_test.is_file()

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
            "closed from promotion-preservation adapter",
        )

        survived = unseeded.is_file() and probe.is_file()
        workflow_test_survived = (not workflow_test_existed) or workflow_test.is_file()
        enumerated = "unseeded_only.py" in result.stdout and "preserved" in result.stdout

        return {
            "accepted": all(record.returncode == 0 for record in setup)
            and opened.returncode == 0
            and result.returncode == 0
            and survived
            and workflow_test_survived
            and enumerated,
            "setup_exit_codes": [record.returncode for record in setup],
            "open_exit_code": opened.returncode,
            "exit_code": result.returncode,
            "current_only_file_survived": unseeded.is_file(),
            "current_only_directory_survived": probe.is_file(),
            "project_workflow_test_seeded": workflow_test_existed,
            "project_workflow_test_survived": workflow_test_survived,
            "preservation_enumerated_in_output": enumerated,
            "stdout": result.stdout,
            "stderr": result.stderr,
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


class RecordBudgetsAdapter:
    """Scaffolding establishes per-program budgets before any generation action.

    Runs the real scaffold into a temp dir and asserts the emitted manifest
    carries the budgets block with the documented defaults, and that the
    scaffold output instructs the agent to negotiate them with the user.
    """

    action_name = "RecordBudgets"

    def apply(self, target_repo: Path, *, spec_root: str = "specs", name: str = "BudgetProg") -> dict[str, object]:
        root = repo_root()
        sys.path.insert(0, str(root))
        from scripts.budgets import DEFAULT_BUDGETS, load_budgets

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

        manifest = Path(target_repo) / spec_root / "program_model" / "spec_manifest.yaml"
        manifest_text = manifest.read_text() if manifest.is_file() else ""
        recorded = load_budgets(manifest, warn=False) if manifest.is_file() else {}
        stdout = result.stdout

        prompt_phrases = (
            "Propose these defaults to the user",
            "Ask which to adjust for this program",
            "one-line rationale",
        )

        return {
            "accepted": (
                result.returncode == 0
                and "budgets:" in manifest_text
                and recorded == DEFAULT_BUDGETS
                and all(phrase in stdout for phrase in prompt_phrases)
            ),
            "exit_code": result.returncode,
            "budgets_block_emitted": "budgets:" in manifest_text,
            "budgets": recorded,
            "defaults_match": recorded == DEFAULT_BUDGETS,
            "prompts_user": all(phrase in stdout for phrase in prompt_phrases),
            "manifest": str(manifest),
            "stderr": result.stderr,
        }
