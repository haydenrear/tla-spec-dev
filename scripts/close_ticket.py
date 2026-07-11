#!/usr/bin/env python3
"""Record append-only history for one closed ticket in desired_program_model/ticket_plan.yaml."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from .spec_evolution import create_ticket_history_entry, print_commit_recommendation
except ImportError:  # pragma: no cover - direct script execution
    from spec_evolution import create_ticket_history_entry, print_commit_recommendation


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticket", help="Ticket id from desired_program_model/ticket_plan.yaml, or a zero-based ticket index.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root.")
    parser.add_argument("--spec-root", type=Path, default=Path("specs"), help="Spec root under the repository.")
    parser.add_argument("--workflow-name", help="Override ticket_plan.yaml name/status.workflow for the history directory.")
    parser.add_argument("--entry-name", help="Override the default ticket-NNN-id history entry name.")
    parser.add_argument("--summary", default="", help="Human-readable summary of the ticket-specific change.")
    parser.add_argument("--result", action="append", type=Path, default=[], help="TLC, generated-case, adapter, or test result path to snapshot.")
    parser.add_argument("--allow-open", action="store_true", help="Allow snapshotting a ticket whose status is not closed/done.")
    parser.add_argument("--ticket-root", type=Path, default=Path("tickets"), help="Ticket directory root, relative to spec root by default.")
    parser.add_argument("--no-promote-current", action="store_true", help="Do not replace project current/ with ticket desired/ during ticket close.")
    parser.add_argument(
        "--accept-new",
        action="store_true",
        help="Accept the ticket desired/ as the new current/: skip the current==desired check and overwrite current/ from desired/ before promotion.",
    )
    args = parser.parse_args()

    result = create_ticket_history_entry(
        repo_root=args.repo_root.resolve(),
        spec_root=args.spec_root,
        ticket_ref=args.ticket,
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


if __name__ == "__main__":
    raise SystemExit(main())
