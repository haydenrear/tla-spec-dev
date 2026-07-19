#!/usr/bin/env python3
"""Progressive CLI entrypoint for the spec-double-compiler workflow."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    tomllib = None  # type: ignore[assignment]


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VERSION = "0.1.0"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def skill_version() -> str:
    manifest = ROOT / "skill-manager.toml"
    if tomllib is None or not manifest.exists():
        return DEFAULT_VERSION
    try:
        parsed = tomllib.loads(manifest.read_text(encoding="utf-8"))
    except Exception:
        return DEFAULT_VERSION
    skill = parsed.get("skill")
    if not isinstance(skill, dict):
        return DEFAULT_VERSION
    version = skill.get("version")
    return str(version) if version else DEFAULT_VERSION


class TlaSpecDevParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: error: {message}\n\nRun '{self.prog} --help' to see the next supported workflow step.\n")


def planned_command(args: argparse.Namespace) -> int:
    print(
        f"{args.command_path} is part of the modeled tla-spec-dev workflow, "
        "but its execution is scheduled for a later implementation ticket.",
        file=sys.stderr,
    )
    print(f"spec root: {args.spec_root}", file=sys.stderr)
    print(f"next: {args.next_step}", file=sys.stderr)
    return 2


def incomplete_command(args: argparse.Namespace) -> int:
    print(f"incomplete command: {args.command_path}", file=sys.stderr)
    print(f"spec root: {args.spec_root}", file=sys.stderr)
    print(f"next: {args.next_step}", file=sys.stderr)
    return 2


def run_scaffold_project(args: argparse.Namespace) -> int:
    from scripts import onboard_program_model

    repo_root = Path(args.repo_root).resolve()
    written = onboard_program_model.scaffold(
        repo_root=repo_root,
        name=args.name,
        force=args.force,
        dry_run=args.dry_run,
        spec_root=Path(args.spec_root),
    )
    spec_root = args.spec_root
    print(f"scaffolded program model files: {len(written)}")
    print(
        "\nThese are PLACEHOLDERS to restructure, not a finished baseline.\n"
        "The baseline is not complete until it has both views and both adapter mappings:\n"
        f"  - {spec_root}/program_model/Internal.tla + Internal.cfg  -> spec-unit cases\n"
        f"  - {spec_root}/program_model/External.tla + External.cfg  -> Test Graph cases\n"
        f"  - {spec_root}/program_model/case_adapters.toml           -> spec-unit adapters\n"
        f"  - {spec_root}/program_model/testgraph_bindings.yml       -> Test Graph adapters\n"
        f"  - {spec_root}/program_model/adapters.py                  -> both, plus projector/assertion\n"
        "\nTest Graph adapters are foundational to every project, not an add-on for\n"
        "distributed systems. Without the External view the public surface is never validated.\n"
        "\nRead references/testgraph_adapters.md, then diff your tree against\n"
        "examples/distributed_history/specs/program_model/ before calling onboarding done."
    )
    from scripts.budgets import budget_prompt

    print(budget_prompt(f"{spec_root}/program_model/spec_manifest.yaml"))
    print("next:")
    print("  1. Propose the budgets above to the user and record the agreed values.")
    print("  2. Replace the placeholder semantics with this repository's real behavior.")
    print(f"  3. scripts/run_tlc.sh {spec_root}/program_model/Internal.tla {spec_root}/program_model/Internal.cfg")
    print(f"  4. scripts/run_tlc.sh {spec_root}/program_model/External.tla {spec_root}/program_model/External.cfg")
    print(f"  5. tla-spec-dev --spec-root {spec_root} scaffold workflow")
    return 0


def run_scaffold_workflow(args: argparse.Namespace) -> int:
    from scripts import new_ticket_workflow

    repo_root = Path(args.repo_root).resolve()
    ticket_id = args.ticket_id or "TICKET-001"
    title = args.title or "Initial spec workflow"
    written = new_ticket_workflow.scaffold(
        repo_root=repo_root,
        ticket_id=ticket_id,
        title=title,
        force=args.force,
        dry_run=args.dry_run,
        spec_root=Path(args.spec_root),
    )
    from scripts.budgets import budget_prompt

    print(f"scaffolded ticket workflow files: {len(written)}")
    print(budget_prompt(f"{args.spec_root}/current/spec_manifest.yaml"))
    print(f"next: tla-spec-dev --spec-root {args.spec_root} open ticket {ticket_id}")
    return 0


def run_open_ticket(args: argparse.Namespace) -> int:
    from scripts.new_ticket_workflow import scaffold_ticket_directory

    repo_root = Path(args.repo_root).resolve()
    written = scaffold_ticket_directory(
        repo_root=repo_root,
        ticket_ref=args.ticket_name,
        force=args.force,
        dry_run=args.dry_run,
        spec_root=Path(args.spec_root),
        ticket_root=args.ticket_root,
        print_next_steps=True,
    )
    print(f"scaffolded ticket-local workflow files: {len(written)}")
    return 0


def run_analyze_complexity(args: argparse.Namespace) -> int:
    from scripts import analyze_complexity

    return analyze_complexity.run(args)


def run_analyze_corpus(args: argparse.Namespace) -> int:
    from scripts import corpus_diagnostics

    return corpus_diagnostics.run(args)


def run_effect_conformance_cmd(args: argparse.Namespace) -> int:
    """MF-013: report the declared-vs-observed effect diff.

    Exits nonzero on any finding. A gap and dead model surface are both
    failures -- the report is written either way, because recording a finding
    is evidence, never a substitute for failing on it.
    """
    from scripts import effect_conformance_report

    return effect_conformance_report.run(args)


def run_close_ticket(args: argparse.Namespace) -> int:
    from scripts.spec_evolution import create_ticket_history_entry, print_commit_recommendation

    result = create_ticket_history_entry(
        repo_root=Path(args.repo_root).resolve(),
        spec_root=Path(args.spec_root),
        ticket_ref=args.ticket_name,
        summary=args.summary,
        result_paths=args.result,
        workflow=args.workflow_name,
        entry_name=args.entry_name,
        allow_open=args.allow_open,
        ticket_root=args.ticket_root,
        promote_current=not args.no_promote_current,
        accept_new=args.accept_new,
    )
    print_commit_recommendation(result)
    return 0


def resolved_spec_root(repo_root: Path, spec_root: str) -> Path:
    path = Path(spec_root)
    return path if path.is_absolute() else repo_root / path


def active_ticket_id(specs_dir: Path) -> str | None:
    from scripts.extract_spec_manifest import load_manifest

    plan_path = specs_dir / "desired_program_model" / "ticket_plan.yaml"
    if not plan_path.exists():
        return None
    plan = load_manifest(plan_path)
    status = plan.get("status")
    if isinstance(status, dict) and status.get("active_ticket"):
        return str(status["active_ticket"])
    return None


def spec_unit_target_dirs(args: argparse.Namespace, specs_dir: Path) -> list[Path]:
    project_current = specs_dir / "current"
    if args.target is not None:
        target = Path(args.target)
        return [target if target.is_absolute() else (Path(args.repo_root).resolve() / target)]
    if args.scope == "project":
        return [project_current]
    if args.ticket:
        return unique_paths([project_current, specs_dir / "tickets" / args.ticket / "current"])
    ticket_id = active_ticket_id(specs_dir)
    if ticket_id:
        ticket_current = specs_dir / "tickets" / ticket_id / "current"
        if ticket_current.exists():
            return unique_paths([project_current, ticket_current])
    return [project_current]


def unique_paths(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return unique


def has_pytest_tests(path: Path) -> bool:
    return path.exists() and any(path.rglob("test_*.py"))


def spec_unit_cases_dirs(args: argparse.Namespace, specs_dir: Path) -> list[Path]:
    if args.cases_dir:
        return [Path(value) for value in args.cases_dir]
    discovered: list[Path] = []
    for root in [
        specs_dir / "generated" / "spec-unit",
        specs_dir / "generated" / "spec_unit",
    ]:
        if not root.exists():
            continue
        discovered.extend(sorted(path for path in root.iterdir() if (path / "cases.py").is_file()))
    return discovered


def run_spec_unit_tests(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    specs_dir = resolved_spec_root(repo_root, args.spec_root).resolve()
    target_dirs = [target.resolve() for target in spec_unit_target_dirs(args, specs_dir)]
    missing_targets = [target for target in target_dirs if not target.exists()]
    if missing_targets:
        print(f"ERROR: spec-unit target does not exist: {missing_targets[0]}", file=sys.stderr)
        return 2

    base_env = os.environ.copy()

    def command_env(target_dir: Path) -> dict[str, str]:
        env = base_env.copy()
        # ROOT carries spec_double_compiler, which the scaffolded adapters.py
        # imports (CaseRunResult). Without it, pytest collection of a spec dir in
        # a user repo dies on ModuleNotFoundError before running a single test.
        python_path = [str(target_dir), str(repo_root), str(ROOT), env.get("PYTHONPATH", "")]
        env["PYTHONPATH"] = os.pathsep.join(part for part in python_path if part)
        return env

    cases_dirs = spec_unit_cases_dirs(args, specs_dir)
    commands: list[tuple[str, list[str], dict[str, str]]] = []
    empty_targets: list[Path] = []
    for target_dir in target_dirs:
        target_command_count = 0
        tests_dir = Path(args.tests_dir) if args.tests_dir else target_dir / "tests"
        if not tests_dir.is_absolute():
            tests_dir = target_dir / tests_dir
        if has_pytest_tests(tests_dir):
            target_command_count += 1
            commands.append(
                (
                    f"pytest:{target_dir}",
                    [
                        "uv",
                        "run",
                        "--with",
                        "pytest",
                        "-m",
                        "pytest",
                        str(tests_dir),
                        *args.pytest_arg,
                    ],
                    command_env(target_dir),
                )
            )

        mapping = Path(args.mapping) if args.mapping else target_dir / "case_adapters.toml"
        for cases_dir in cases_dirs:
            target_command_count += 1
            command = [
                sys.executable,
                str(ROOT / "scripts" / "run_generated_case_adapters.py"),
                str(cases_dir),
                "--mapping",
                str(mapping),
                "--spec-dir",
                str(target_dir),
                "--view",
                "internal",
                "--import-root",
                str(target_dir),
            ]
            for label in args.label:
                command.extend(["--label", label])
            for case_name in args.case:
                command.extend(["--case", case_name])
            if args.limit is not None:
                command.extend(["--limit", str(args.limit)])
            if args.work_dir is not None:
                command.extend(["--work-dir", str(args.work_dir)])
            if args.validate_only:
                command.append("--validate-only")
            if args.validate_capabilities:
                command.append("--validate-capabilities")
            if not args.no_batch:
                command.append("--batch")
            commands.append((f"case-adapters:{target_dir}:{cases_dir.name}", command, command_env(target_dir)))
        if target_command_count == 0:
            empty_targets.append(target_dir)

    if empty_targets:
        for target_dir in empty_targets:
            print(f"ERROR: no spec-unit pytest tests or generated case packages found for {target_dir}", file=sys.stderr)
        return 2

    if not commands:
        targets = ", ".join(str(target) for target in target_dirs)
        print(f"ERROR: no spec-unit pytest tests or generated case packages found for {targets}", file=sys.stderr)
        return 2

    print(f"spec root: {specs_dir}")
    for target_dir in target_dirs:
        print(f"spec-unit target: {target_dir}")
    for label, command, env in commands:
        print(f"running {label}: {' '.join(command)}")
        result = subprocess.run(command, cwd=repo_root, env=env)
        if result.returncode != 0:
            return result.returncode
    print(f"spec-unit validation passed for {len(target_dirs)} target(s)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = TlaSpecDevParser(
        prog="tla-spec-dev",
        description="Work with a spec-double-compiler project through the modeled spec workflow.",
        epilog=(
            "Typical order: scaffold project -> scaffold workflow -> open ticket -> "
            "analyze complexity -> run spec-unit-tests -> close ticket."
        ),
        allow_abbrev=False,
    )
    parser.add_argument(
        "--spec-root",
        default="specs",
        help="Spec root under the repository. Defaults to %(default)s.",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root. Defaults to the current directory.",
    )
    parser.add_argument("--version", action="version", version=f"tla-spec-dev {skill_version()}")

    subparsers = parser.add_subparsers(dest="command", metavar="command")

    scaffold = subparsers.add_parser(
        "scaffold",
        help="Create spec workflow directories.",
        description="Create the modeled spec-double-compiler project or ticket workflow directories.",
        allow_abbrev=False,
    )
    scaffold.set_defaults(
        func=incomplete_command,
        command_path="tla-spec-dev scaffold",
        next_step="Choose a target: tla-spec-dev scaffold project or tla-spec-dev scaffold workflow.",
    )
    scaffold_sub = scaffold.add_subparsers(dest="scaffold_target", metavar="target")
    scaffold_project = scaffold_sub.add_parser(
        "project",
        help="Create the accepted program_model baseline.",
        description="Create specs/program_model as the accepted whole-program semantic baseline.",
        allow_abbrev=False,
    )
    scaffold_project.add_argument("--name", help="Program/module name. Defaults to the repository directory name.")
    scaffold_project.add_argument("--force", action="store_true", help="Overwrite existing program-model files.")
    scaffold_project.add_argument("--dry-run", action="store_true", help="Print planned writes without changing files.")
    scaffold_project.set_defaults(
        func=run_scaffold_project,
        command_path="tla-spec-dev scaffold project",
        next_step="tla-spec-dev scaffold workflow",
    )
    scaffold_workflow = scaffold_sub.add_parser(
        "workflow",
        help="Create current and desired workflow directories.",
        description="Create specs/current and specs/desired_program_model from an accepted baseline.",
        allow_abbrev=False,
    )
    scaffold_workflow.add_argument("ticket_id", nargs="?", help="Initial ticket id. Defaults to TICKET-001.")
    scaffold_workflow.add_argument("title", nargs="?", help="Initial ticket title. Defaults to 'Initial spec workflow'.")
    scaffold_workflow.add_argument("--force", action="store_true", help="Overwrite existing workflow files.")
    scaffold_workflow.add_argument("--dry-run", action="store_true", help="Print planned writes without changing files.")
    scaffold_workflow.set_defaults(
        func=run_scaffold_workflow,
        command_path="tla-spec-dev scaffold workflow",
        next_step="tla-spec-dev open ticket <ticket>",
    )

    open_parser = subparsers.add_parser(
        "open",
        help="Open a ticket-local spec workflow.",
        description="Open a ticket workspace with ticket-local current, desired, results, and Test Graph files.",
        allow_abbrev=False,
    )
    open_parser.set_defaults(
        func=incomplete_command,
        command_path="tla-spec-dev open",
        next_step="Choose a target: tla-spec-dev open ticket <ticket-name>.",
    )
    open_sub = open_parser.add_subparsers(dest="open_target", metavar="target")
    open_ticket = open_sub.add_parser(
        "ticket",
        help="Open a ticket by id or name.",
        description="Open a ticket and print desired-first implementation instructions.",
        allow_abbrev=False,
    )
    open_ticket.add_argument("ticket_name", help="Ticket id from desired_program_model/ticket_plan.yaml.")
    open_ticket.add_argument("--ticket-root", type=Path, default=Path("tickets"), help="Ticket directory root, relative to spec root by default.")
    open_ticket.add_argument("--force", action="store_true", help="Overwrite existing ticket-local files.")
    open_ticket.add_argument("--dry-run", action="store_true", help="Print planned writes without changing files.")
    open_ticket.set_defaults(
        func=run_open_ticket,
        command_path="tla-spec-dev open ticket",
        next_step="Edit ticket desired first, then update current to match.",
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Run spec workflow validations.",
        description="Run generated or adapter-backed validations from the selected spec root.",
        allow_abbrev=False,
    )
    run_parser.set_defaults(
        func=incomplete_command,
        command_path="tla-spec-dev run",
        next_step="Choose a target: tla-spec-dev run spec-unit-tests.",
    )
    run_sub = run_parser.add_subparsers(dest="run_target", metavar="target")
    run_spec_units = run_sub.add_parser(
        "spec-unit-tests",
        help="Run generated spec-unit adapter tests.",
        description="Run generated/adapted spec-unit tests for the selected spec root.",
        allow_abbrev=False,
    )
    run_spec_units.add_argument("--ticket", help="Run ticket-local current spec-unit tests for this ticket.")
    run_spec_units.add_argument(
        "--scope",
        choices=["auto", "project"],
        default="auto",
        help="Target active ticket current/ when present, otherwise project current/. Use project to force specs/current.",
    )
    run_spec_units.add_argument("--target", type=Path, help="Explicit spec directory to validate.")
    run_spec_units.add_argument("--tests-dir", type=Path, help="Test directory relative to the selected spec directory.")
    run_spec_units.add_argument("--cases-dir", action="append", help="Generated spec-unit case package directory.")
    run_spec_units.add_argument("--mapping", type=Path, help="Adapter mapping TOML/YAML. Defaults to target case_adapters.toml.")
    run_spec_units.add_argument("--work-dir", type=Path, help="Work directory for generated case adapter execution.")
    run_spec_units.add_argument("--label", action="append", default=[], help="Only run generated cases with this label.")
    run_spec_units.add_argument("--case", action="append", default=[], help="Only run this generated case name.")
    run_spec_units.add_argument("--limit", type=int, help="Limit generated cases.")
    run_spec_units.add_argument("--validate-only", action="store_true", help="Validate adapter coverage without executing generated cases.")
    run_spec_units.add_argument("--validate-capabilities", action="store_true", help="Ask adapters whether they can run selected cases.")
    run_spec_units.add_argument("--no-batch", action="store_true", help="Run generated cases as one Python program per case instead of batched hooks.")
    run_spec_units.add_argument(
        "--pytest-arg",
        action="append",
        default=["-q"],
        help="Argument passed to pytest. May be repeated. Defaults to -q.",
    )
    run_spec_units.set_defaults(
        func=run_spec_unit_tests,
        command_path="tla-spec-dev run spec-unit-tests",
        next_step="tla-spec-dev close ticket <ticket>",
    )

    run_effects = run_sub.add_parser(
        "effect-conformance",
        help="Diff observed adapter side effects against declared effect ports.",
        description=(
            "Execute component adapters in a sandbox (temp dirs, fake transports, recorded "
            "boundaries), collect the side effects that actually crossed a boundary, and diff "
            "them against the ports declared in actions.yml / spec_manifest.yaml. "
            "An observed effect with no declared port is a GAP; a declared port no case "
            "exercises is DEAD MODEL SURFACE. Both are recorded AND fail the command. "
            "Nothing suppresses a gap report -- there is no justification, waiver, or "
            "override flag, and out-of-contract justifications were withdrawn 2026-07-18."
        ),
        allow_abbrev=False,
    )
    run_effects.add_argument("--ticket", help="Use this ticket's current/ spec directory.")
    run_effects.add_argument("--target", type=Path, help="Explicit spec directory carrying the effect declarations.")
    run_effects.add_argument("--cases-dir", action="append", help="Generated spec-unit case package directory.")
    run_effects.add_argument("--mapping", type=Path, help="Adapter mapping TOML/YAML. Defaults to target case_adapters.toml.")
    run_effects.add_argument("--work-dir", type=Path, help="Work directory for sandboxed adapter execution.")
    run_effects.add_argument("--out", type=Path, help="Write the JSON diff report here (ticket results/ evidence).")
    run_effects.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    run_effects.set_defaults(
        func=run_effect_conformance_cmd,
        command_path="tla-spec-dev run effect-conformance",
        next_step="tla-spec-dev run spec-unit-tests --ticket <ticket>",
    )

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze model complexity against the budgets.",
        description="Analyze a spec + cfg for state-space complexity and gate it against manifest budgets.",
        allow_abbrev=False,
    )
    analyze_parser.set_defaults(
        func=incomplete_command,
        command_path="tla-spec-dev analyze",
        next_step="Choose a target: tla-spec-dev analyze complexity <spec.tla> [<cfg>].",
    )
    analyze_sub = analyze_parser.add_subparsers(dest="analyze_target", metavar="target")
    analyze_complexity_parser = analyze_sub.add_parser(
        "complexity",
        help="Print the dimension table, R/W matrix, modularity, and budget verdict.",
        description=(
            "Print the per-variable domain cardinality table, the state-space upper bound, "
            "the variables x actions read/write matrix, the graph-modularity score with "
            "near-decomposable clusters and candidate port-crossing actions, unjustified "
            "variables, and a suggested move (abstract/decompose/refactor) that is a "
            "RECOMMENDATION REQUIRING USER APPROVAL. Exits nonzero when the manifest budgets "
            "are exceeded."
        ),
        allow_abbrev=False,
    )
    from scripts.analyze_complexity import add_arguments as _add_analyze_arguments

    _add_analyze_arguments(analyze_complexity_parser)
    analyze_complexity_parser.set_defaults(
        func=run_analyze_complexity,
        command_path="tla-spec-dev analyze complexity",
        next_step="Record the report under the ticket results/ directory as evidence.",
    )

    analyze_corpus_parser = analyze_sub.add_parser(
        "corpus",
        help="Print the case distribution and gate it against the case caps.",
        description=(
            "Print the generated corpus distribution per (action, label class), which "
            "strata dominate, which are starved, and what varies across any redundant "
            "group -- the actionable part, since it points at symmetry reduction, a "
            "state constraint, or abstraction as the cause. Exits nonzero when a "
            "component or action exceeds its manifest case cap "
            "(max_internal_cases_per_component / max_external_cases_per_action). "
            "NOTHING IS EVER DROPPED, FILTERED, SAMPLED, OR TRUNCATED to fit a cap: "
            "over budget the gate reports and refuses, and the two ways forward are "
            "fixing the diagram or raising the cap with a recorded rationale. The "
            "suggested move is a RECOMMENDATION REQUIRING USER APPROVAL."
        ),
        allow_abbrev=False,
    )
    from scripts.corpus_diagnostics import add_arguments as _add_corpus_arguments

    _add_corpus_arguments(analyze_corpus_parser)
    analyze_corpus_parser.set_defaults(
        func=run_analyze_corpus,
        command_path="tla-spec-dev analyze corpus",
        next_step="Fix the diagram so the redundant cases are never generated, or raise the cap with a rationale.",
    )

    close_parser = subparsers.add_parser(
        "close",
        help="Close ticket or workflow history.",
        description="Close a ticket once current equals desired and validations pass.",
        allow_abbrev=False,
    )
    close_parser.set_defaults(
        func=incomplete_command,
        command_path="tla-spec-dev close",
        next_step="Choose a target: tla-spec-dev close ticket <ticket-name>.",
    )
    close_sub = close_parser.add_subparsers(dest="close_target", metavar="target")
    close_ticket = close_sub.add_parser(
        "ticket",
        help="Close a ticket by id or name.",
        description="Close a ticket, write append-only history, and promote ticket desired into project current.",
        allow_abbrev=False,
    )
    close_ticket.add_argument("ticket_name", help="Ticket id from desired_program_model/ticket_plan.yaml.")
    close_ticket.add_argument("--workflow-name", help="Override ticket_plan.yaml name/status.workflow for the history directory.")
    close_ticket.add_argument("--entry-name", help="Override the default ticket-NNN-id history entry name.")
    close_ticket.add_argument("--summary", default="", help="Human-readable summary of the ticket-specific change.")
    close_ticket.add_argument("--result", action="append", type=Path, default=[], help="TLC, generated-case, adapter, or test result path to snapshot.")
    close_ticket.add_argument("--allow-open", action="store_true", help="Allow snapshotting a ticket whose status is not closed/done.")
    close_ticket.add_argument("--ticket-root", type=Path, default=Path("tickets"), help="Ticket directory root, relative to spec root by default.")
    close_ticket.add_argument("--no-promote-current", action="store_true", help="Do not replace project current/ with ticket desired/ during ticket close.")
    close_ticket.add_argument(
        "--accept-new",
        action="store_true",
        help="Accept the ticket desired/ as the new current/: skip the current==desired check and overwrite current/ from desired/ before promotion.",
    )
    close_ticket.set_defaults(
        func=run_close_ticket,
        command_path="tla-spec-dev close ticket",
        next_step="Open the next ticket or close the workflow.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = getattr(args, "func", None)
    if handler is None:
        parser.print_help()
        return 0
    return int(handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
