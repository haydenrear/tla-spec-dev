#!/usr/bin/env python3
"""Scaffold a ticket-local desired/current workflow from ticket_plan.yaml."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from .new_ticket_workflow import scaffold_ticket_directory
except ImportError:  # pragma: no cover - direct script execution
    from new_ticket_workflow import scaffold_ticket_directory


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticket", help="Ticket id from desired_program_model/ticket_plan.yaml, or a zero-based ticket index.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root.")
    parser.add_argument("--spec-root", type=Path, default=Path("specs"), help="Spec root under the repository.")
    parser.add_argument("--ticket-root", type=Path, default=Path("tickets"), help="Ticket directory root, relative to spec root by default.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing ticket-local files.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned writes without changing files.")
    args = parser.parse_args()

    written = scaffold_ticket_directory(
        args.repo_root.resolve(),
        args.ticket,
        force=args.force,
        dry_run=args.dry_run,
        spec_root=args.spec_root,
        ticket_root=args.ticket_root,
        print_next_steps=True,
    )
    print(f"scaffolded ticket-local workflow files: {len(written)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
