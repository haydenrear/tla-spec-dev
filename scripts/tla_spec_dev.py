#!/usr/bin/env python3
"""Progressive CLI entrypoint for the spec-double-compiler workflow."""

from __future__ import annotations

import argparse
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
    print(f"scaffolded program model files: {len(written)}")
    print(f"next: tla-spec-dev --spec-root {args.spec_root} scaffold workflow")
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
    print(f"scaffolded ticket workflow files: {len(written)}")
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
    )
    print_commit_recommendation(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = TlaSpecDevParser(
        prog="tla-spec-dev",
        description="Work with a spec-double-compiler project through the modeled spec workflow.",
        epilog=(
            "Typical order: scaffold project -> scaffold workflow -> open ticket -> "
            "run spec-unit-tests -> close ticket."
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
    run_spec_units.set_defaults(
        func=planned_command,
        command_path="tla-spec-dev run spec-unit-tests",
        next_step="CLI-005 wires this command to generated spec-unit validation.",
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
