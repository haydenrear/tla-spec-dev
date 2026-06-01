#!/usr/bin/env python3
"""Record immutable history for a completed desired/current spec workflow."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from .spec_evolution import create_evolution_entry, print_commit_recommendation
except ImportError:  # pragma: no cover - direct script execution
    from spec_evolution import create_evolution_entry, print_commit_recommendation


def main() -> int:
    parser = argparse.ArgumentParser(description="Record immutable history for a completed spec workflow.")
    parser.add_argument("--specs-dir", type=Path, default=Path("specs"))
    parser.add_argument("--close-id", help="Explicit immutable close id. Defaults to a UTC timestamped id.")
    parser.add_argument("--ticket", action="append", default=[], help="Ticket id included in this workflow close")
    parser.add_argument("--summary", default="", help="Human-readable summary of the workflow close")
    parser.add_argument("--result", action="append", type=Path, default=[], help="TLC, generated-case, adapter, or test result path to snapshot")
    parser.add_argument("--spec-path", action="append", type=Path, default=[], help="Additional spec/program-model path to snapshot")
    parser.add_argument("--ticket-file", action="append", type=Path, default=[], help="Ticket file to snapshot when it cannot be inferred")
    parser.add_argument("--tickets-dir", type=Path, default=Path("tickets"))
    parser.add_argument("--desired", type=Path, default=Path("desired_program_model"))
    parser.add_argument("--current", type=Path, default=Path("current"))
    parser.add_argument("--remove-active", action="store_true", help="Remove desired/current after they have been snapshotted")
    args = parser.parse_args()

    entry_dir = create_evolution_entry(
        kind="workflow",
        specs_dir=args.specs_dir,
        close_id=args.close_id,
        tickets=args.ticket,
        summary=args.summary,
        result_paths=args.result,
        spec_paths=args.spec_path,
        ticket_files=args.ticket_file,
        tickets_dir=args.tickets_dir,
        desired_path=args.desired,
        current_path=args.current,
        remove_active=args.remove_active,
    )
    print_commit_recommendation(entry_dir, "close spec workflow")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
