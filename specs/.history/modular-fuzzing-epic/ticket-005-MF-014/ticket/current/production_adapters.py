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


class SkillFeedbackCloseOutAdapter:
    """MF-017: drive the shipped CLI and prove close-out runs the Phase 6 retro.

    Closes a fixture workflow twice against a throwaway repository and asserts:

    * the first close emits ``<spec-root>/results/skill_feedback.md`` carrying
      all four prompt sections and the instruction to file each item as a
      ticket or PR against spec-double-compiler;
    * the history manifest records the filing status -- ``feedback_filed``
      false while the retro is unreviewed;
    * a finding filled in between the two closes survives the second close
      (the document accumulates; it is never regenerated over real content),
      and the second history entry records ``feedback_filed`` true together
      with *where* it was filed.
    """

    action_name = "CloseTicket"

    #: A real finding from this epic (GitHub #22): ticket-close promotion
    #: destroyed regression tests unique to specs/current.
    FINDING = (
        "\n### SF-001 — ticket-close promotion destroyed files unique to specs/current\n"
        "- category: profile-schema-cli\n"
        "- target: scripts/spec_evolution.py::replace_tree\n"
        "- observed_on: tla-spec-dev @ MF-012, MF-020, MF-021\n"
        "- evidence: tests/test_promotion_preserves_current.py\n"
        "- severity: silent-data-loss\n"
        "- root_cause: tool\n"
        "- surface: tla-spec-dev close ticket\n"
        "- forced_workaround: restore deleted regression tests from git history\n"
        "- data_loss: yes\n"
        "- recommendation: ticket https://github.com/haydenrear/tla-spec-dev/issues/22\n"
        "- status: filed\n"
    )

    def apply(
        self,
        target_repo: Path,
        *,
        spec_root: str = "specs",
        ticket_id: str = "CLI-129",
        title: str = "CLI close-out skill feedback",
    ) -> dict[str, object]:
        import json

        root = repo_root()
        setup = prepare_ticket_workflow(root, target_repo, spec_root=spec_root, ticket_id=ticket_id, title=title)
        plan_path = target_repo / spec_root / "desired_program_model" / "ticket_plan.yaml"

        def close(ticket: str) -> object:
            run_cli(root, target_repo, "--spec-root", spec_root, "open", "ticket", ticket)
            if plan_path.exists():
                plan_path.write_text(
                    plan_path.read_text(encoding="utf-8").replace("status: next", "status: done", 1),
                    encoding="utf-8",
                )
            return run_cli(
                root, target_repo, "--spec-root", spec_root,
                "close", "ticket", ticket, "--summary", "closed from skill-feedback adapter",
            )

        first = close(ticket_id)

        feedback = target_repo / spec_root / "results" / "skill_feedback.md"
        emitted = feedback.is_file()
        text = feedback.read_text(encoding="utf-8") if emitted else ""
        sections = ["surviving-mutants", "unmodelable-effects", "budget-and-metric", "profile-schema-cli"]
        has_sections = all(section in text for section in sections)
        instructs_filing = "spec-double-compiler" in text and "ticket or PR" in text

        history_root = target_repo / spec_root / ".history" / "desired-ticket-workflow"
        first_manifest_path = history_root / f"ticket-000-{ticket_id}" / "manifest.json"
        first_manifest = json.loads(first_manifest_path.read_text(encoding="utf-8")) if first_manifest_path.is_file() else {}

        # A second close proves the document accumulates rather than being
        # regenerated, so the fixture plan needs a second ticket entry.
        second_ticket = f"{ticket_id}-B"
        if plan_path.exists():
            plan_path.write_text(
                plan_path.read_text(encoding="utf-8")
                + f'  - id: {second_ticket}\n    title: "second close"\n    status: next\n    depends_on: []\n',
                encoding="utf-8",
            )

        # Fill in a real finding, then close that second ticket.
        if emitted:
            feedback.write_text(
                text.replace("- feedback_status: unreviewed", "- feedback_status: items-recorded", 1) + self.FINDING,
                encoding="utf-8",
            )
        second = close(second_ticket)

        after = feedback.read_text(encoding="utf-8") if feedback.is_file() else ""
        finding_survived = "SF-001" in after and "issues/22" in after
        second_manifest_path = history_root / f"ticket-000-{second_ticket}" / "manifest.json"
        if not second_manifest_path.is_file():
            candidates = sorted(history_root.glob(f"ticket-*-{second_ticket}/manifest.json"))
            second_manifest_path = candidates[0] if candidates else second_manifest_path
        second_manifest = json.loads(second_manifest_path.read_text(encoding="utf-8")) if second_manifest_path.is_file() else {}

        first_filed = first_manifest.get("feedback_filed")
        second_filed = second_manifest.get("feedback_filed")
        filed_where = second_manifest.get("feedback_filed_where", [])

        return {
            "accepted": all(record.returncode == 0 for record in setup)
            and first.returncode == 0
            and second.returncode == 0
            and emitted
            and has_sections
            and instructs_filing
            and first_filed is False
            and finding_survived
            and second_filed is True
            and filed_where == ["https://github.com/haydenrear/tla-spec-dev/issues/22"],
            "setup_exit_codes": [record.returncode for record in setup],
            "exit_code": first.returncode,
            "second_exit_code": second.returncode,
            "template_emitted": emitted,
            "feedback_path": str(feedback),
            "prompt_sections_present": has_sections,
            "instructs_filing_against_skill_repo": instructs_filing,
            "first_close_feedback_filed": first_filed,
            "finding_survived_second_close": finding_survived,
            "second_close_feedback_filed": second_filed,
            "feedback_filed_where": filed_where,
            "stdout": first.stdout,
            "second_stdout": second.stdout,
            "stderr": first.stderr,
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


UNDER_BUDGET_TLA = """---------------------------- MODULE UnderBudget ----------------------------
EXTENDS Naturals

CONSTANTS Slots

VARIABLES armed, fired

vars == << armed, fired >>

Init ==
  /\\ armed = FALSE
  /\\ fired = FALSE

Arm ==
  /\\ ~armed
  /\\ armed' = TRUE
  /\\ UNCHANGED << fired >>

Fire ==
  /\\ armed
  /\\ ~fired
  /\\ fired' = TRUE
  /\\ UNCHANGED << armed >>

Next == Arm \\/ Fire

TypeInvariant ==
  /\\ armed \\in BOOLEAN
  /\\ fired \\in BOOLEAN

Spec == Init /\\ [][Next]_vars
=============================================================================
"""

UNDER_BUDGET_CFG = """SPECIFICATION Spec

CONSTANTS
  Slots = {s1, s2}

INVARIANTS
  TypeInvariant
"""

OVER_BUDGET_TLA = """---------------------------- MODULE OverBudget ----------------------------
EXTENDS Naturals

CONSTANTS Nodes

VARIABLES a, b, c, d

vars == << a, b, c, d >>

Init ==
  /\\ a = [n \\in Nodes |-> 0]
  /\\ b = [n \\in Nodes |-> 0]
  /\\ c = {}
  /\\ d = {}

BumpA ==
  /\\ \\E n \\in Nodes: a' = [a EXCEPT ![n] = 1]
  /\\ UNCHANGED << b, c, d >>

BumpB ==
  /\\ \\E n \\in Nodes: b' = [b EXCEPT ![n] = 1]
  /\\ UNCHANGED << a, c, d >>

AddC ==
  /\\ \\E n \\in Nodes: c' = c \\cup {n}
  /\\ UNCHANGED << a, b, d >>

AddD ==
  /\\ \\E n \\in Nodes: d' = d \\cup {n}
  /\\ UNCHANGED << a, b, c >>

Next == BumpA \\/ BumpB \\/ AddC \\/ AddD

TypeInvariant ==
  /\\ a \\in [Nodes -> 0..9]
  /\\ b \\in [Nodes -> 0..9]
  /\\ c \\subseteq Nodes
  /\\ d \\subseteq Nodes

Spec == Init /\\ [][Next]_vars
=============================================================================
"""

OVER_BUDGET_CFG = """SPECIFICATION Spec

CONSTANTS
  Nodes = {n1, n2, n3, n4, n5, n6}

INVARIANTS
  TypeInvariant
"""

BUDGET_MANIFEST = """module: Fixture
budgets:
  max_distinct_states: 50000
  max_component_variables: 6
  max_component_actions: 8
"""

# Deliberately unmeetable budgets applied to the *small* fixture. This is how
# the generation refusal and its override are exercised: the gate must fail,
# but TLC must still finish instantly when the override lets it through. Using
# the genuinely huge OverBudget fixture here would hang forever -- which is
# precisely the failure this command exists to prevent.
TIGHT_MANIFEST = """module: Fixture
budgets:
  max_distinct_states: 2
  max_component_variables: 1
  max_component_actions: 1
"""


def _write_fixture(
    directory: Path, module: str, tla: str, cfg: str, manifest: str = BUDGET_MANIFEST
) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    tla_path = directory / f"{module}.tla"
    cfg_path = directory / "MC.cfg"
    tla_path.write_text(tla, encoding="utf-8")
    cfg_path.write_text(cfg, encoding="utf-8")
    (directory / "spec_manifest.yaml").write_text(manifest, encoding="utf-8")
    return tla_path, cfg_path


class AnalyzeComplexityAdapter:
    """`tla-spec-dev analyze complexity` gates a model against its budgets.

    Runs the REAL command against two fixture specs -- one comfortably under
    budget, one far over it -- and asserts the table output, the exit codes,
    and the case-generation refusal plus its explicit override path.

    The over-budget fixture is 6 nodes x two 0..9 functions x two powersets:
    10^6 * 10^6 * 2^6 * 2^6, which is far above the 50,000 default. It is
    chosen so the gate must refuse WITHOUT running TLC -- running TLC on it is
    exactly the timeout this command exists to prevent.
    """

    action_name = "AnalyzeComplexity"

    def apply(self, target_repo: Path, *, spec_root: str = "specs") -> dict[str, object]:
        root = repo_root()
        target_repo = Path(target_repo)

        under_tla, under_cfg = _write_fixture(
            target_repo / "under", "UnderBudget", UNDER_BUDGET_TLA, UNDER_BUDGET_CFG
        )
        over_tla, over_cfg = _write_fixture(
            target_repo / "over", "OverBudget", OVER_BUDGET_TLA, OVER_BUDGET_CFG
        )

        def cli(*args: str) -> subprocess.CompletedProcess:
            return subprocess.run(
                [sys.executable, str(root / "scripts" / "tla_spec_dev.py"),
                 "--spec-root", spec_root, "analyze", "complexity", *args],
                cwd=target_repo, text=True, capture_output=True, check=False,
            )

        under = cli(str(under_tla), str(under_cfg))
        over = cli(str(over_tla), str(over_cfg))

        # Case generation must refuse above the gate, and proceed with the
        # explicit override flag. Exercised against a SMALL model carrying
        # unmeetable budgets, so the override path terminates.
        tight_tla, tight_cfg = _write_fixture(
            target_repo / "tight", "UnderBudget", UNDER_BUDGET_TLA, UNDER_BUDGET_CFG,
            manifest=TIGHT_MANIFEST,
        )

        def generate(*extra: str) -> subprocess.CompletedProcess:
            return subprocess.run(
                [sys.executable, str(root / "scripts" / "generate_cases_from_tlc_dump.py"),
                 str(tight_tla), str(tight_cfg), "--out", str(target_repo / "generated"), *extra],
                cwd=target_repo, text=True, capture_output=True, check=False,
                timeout=180,
            )

        refused = generate()
        overridden = generate("--allow-over-budget")

        table_phrases = ("Dimension table", "State-space upper bound",
                         "read/write matrix", "SUGGESTED MOVE")
        under_has_table = all(phrase in under.stdout for phrase in table_phrases)
        recommendation_labeled = (
            "RECOMMENDATION -- REQUIRES USER APPROVAL, NOT AUTO-APPLIED" in under.stdout
        )
        measured_projected_split = "[MEASURED]" in under.stdout and "[PROJECTED]" in under.stdout
        over_names_dimensions = "dominant dimensions" in over.stdout.lower()

        refusal_ok = (
            refused.returncode != 0
            and "REFUSING to generate cases" in refused.stderr
            and "Dominant dimensions" in refused.stderr
            and "states generated" not in refused.stdout
        )
        override_ok = (
            "PROCEEDING ANYWAY -- overridden by --allow-over-budget" in overridden.stderr
            and "REFUSING to generate cases" not in overridden.stderr
        )

        return {
            "accepted": (
                under.returncode == 0
                and over.returncode == 1
                and under_has_table
                and recommendation_labeled
                and measured_projected_split
                and over_names_dimensions
                and refusal_ok
                and override_ok
            ),
            "under_budget_exit_code": under.returncode,
            "over_budget_exit_code": over.returncode,
            "prints_dimension_table": under_has_table,
            "suggested_move_labeled_recommendation": recommendation_labeled,
            "separates_measured_from_projected": measured_projected_split,
            "over_budget_names_dominant_dimensions": over_names_dimensions,
            "generation_refused_above_gate": refusal_ok,
            "generation_override_honored": override_ok,
            "stderr": under.stderr + over.stderr,
        }


# --------------------------------------------------------------------------
# MF-014: corpus diagnostics and hard case caps
# --------------------------------------------------------------------------

CORPUS_FIXTURE_CASES = '''
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class StateGraphInput:
    action: str
    source_node: str
    target_node: str
    params: dict = field(default_factory=dict)


@dataclass(frozen=True)
class StateGraphCase:
    name: str
    before: dict
    input: StateGraphInput
    output: Any
    after: dict
    labels: frozenset
    view: str = "external"
    layer: str = "external"


SOURCE_MODULE = "Fixture"
SOURCE_VIEW = "external"

CASES = [
    StateGraphCase(
        name="case_%04d_SubmitDuplicate" % i,
        before={"n": i % 7, "seen": True},
        input=StateGraphInput("SubmitDuplicate", str(1000 + i), str(2000 + i), {"client": "c%d" % i}),
        output={},
        after={"n": i % 7, "seen": True},
        labels=frozenset({"SubmitDuplicate", "duplicate_submission"}),
    )
    for i in range(__COUNT__)
] + [
    StateGraphCase(
        name="case_regression_promoted",
        before={"n": 0},
        input=StateGraphInput("SubmitOnce", "1", "2", {}),
        output={},
        after={"n": 1},
        labels=frozenset({"SubmitOnce", "regression:issue-41"}),
    )
]

CASES_BY_NAME = {c.name: c for c in CASES}
'''


def _write_corpus_fixture(target: Path, count: int, cap: int) -> tuple[Path, Path]:
    """A generated-package-shaped corpus with `count` cases of one action."""
    package = target / "generated" / "fixture_cases"
    package.mkdir(parents=True, exist_ok=True)
    (package / "__init__.py").write_text(
        "from .cases import CASES, CASES_BY_NAME, SOURCE_MODULE, SOURCE_VIEW\n", encoding="utf-8"
    )
    (package / "cases.py").write_text(
        CORPUS_FIXTURE_CASES.replace("__COUNT__", str(count)), encoding="utf-8"
    )
    manifest = target / "spec_manifest.yaml"
    manifest.write_text(
        f"module: Fixture\nbudgets:\n  max_external_cases_per_action: {cap}\n", encoding="utf-8"
    )
    return package, manifest


class AnalyzeCorpusAdapter:
    """`tla-spec-dev analyze corpus` gates a generated corpus against its caps.

    Runs the REAL command on both sides of the cap and asserts the model's
    central claim: over cap it REPORTS AND REFUSES, and the corpus is exactly
    as large afterwards as it was before. Nothing is dropped, filtered,
    sampled, or truncated to fit the budget -- so the same fixture that fails
    at cap 50 passes unchanged at cap 500, with every case still present.
    """

    action_name = "AnalyzeCorpus"

    def apply(self, target_repo: Path, *, spec_root: str = "specs") -> dict[str, object]:
        root = repo_root()
        target_repo = Path(target_repo)

        over_pkg, over_manifest = _write_corpus_fixture(target_repo / "over", count=200, cap=50)
        under_pkg, under_manifest = _write_corpus_fixture(target_repo / "under", count=200, cap=500)

        def cli(pkg: Path, manifest: Path) -> subprocess.CompletedProcess:
            return subprocess.run(
                [sys.executable, str(root / "scripts" / "tla_spec_dev.py"),
                 "--spec-root", spec_root, "analyze", "corpus", str(pkg),
                 "--view", "external", "--manifest", str(manifest)],
                cwd=target_repo, text=True, capture_output=True, check=False, timeout=180,
            )

        over = cli(over_pkg, over_manifest)
        under = cli(under_pkg, under_manifest)

        def case_count(pkg: Path) -> int:
            import re
            return len(re.findall(r"StateGraphCase\(", (pkg / "cases.py").read_text(encoding="utf-8")))

        # The same 201-case corpus, before and after a FAILING gate run.
        corpus_intact = case_count(over_pkg) == case_count(under_pkg)

        reports_distribution = "Distribution per (action, label class)" in over.stdout
        reports_dominant = "Strata that DOMINATE the corpus" in over.stdout
        reports_starved = "Strata that are STARVED" in over.stdout
        reports_variance = "What VARIES across the redundant group" in over.stdout
        names_cause = "Likely cause:" in over.stdout
        recommendation_labeled = (
            "RECOMMENDATION REQUIRING USER APPROVAL -- not applied automatically." in over.stdout
        )
        accept_path = (
            "ACCEPT PATH" in over.stdout
            and "source: negotiated" in over.stdout
            and "rationale:" in over.stdout
        )
        never_trims = (
            "Nothing was" in over.stdout
            and "trimmed" in over.stdout
            and "dropped, filtered, sampled, or truncated" in over.stdout
        )
        regression_retained = (
            "Named regression traces (always retained)" in over.stdout
            and "Named regression traces (always retained)" in under.stdout
        )
        no_trim_offered = "--distill" not in over.stdout and "--trim" not in over.stdout

        return {
            "accepted": (
                over.returncode == 1
                and under.returncode == 0
                and corpus_intact
                and reports_distribution
                and reports_dominant
                and reports_starved
                and reports_variance
                and names_cause
                and recommendation_labeled
                and accept_path
                and never_trims
                and regression_retained
                and no_trim_offered
            ),
            "over_cap_exit_code": over.returncode,
            "raised_cap_exit_code": under.returncode,
            "corpus_unchanged_by_failing_gate": corpus_intact,
            "reports_count_per_action_and_label_class": reports_distribution,
            "reports_dominant_strata": reports_dominant,
            "reports_starved_strata": reports_starved,
            "reports_what_varies_across_redundant_group": reports_variance,
            "names_representation_cause": names_cause,
            "remediation_labeled_recommendation": recommendation_labeled,
            "cap_raise_accept_path_offered": accept_path,
            "never_offers_to_trim": never_trims and no_trim_offered,
            "regression_traces_retained": regression_retained,
            "stdout": over.stdout,
            "stderr": over.stderr + under.stderr,
        }
