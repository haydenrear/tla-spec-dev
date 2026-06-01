#!/usr/bin/env python3
"""Record immutable history for a completed desired/current spec workflow."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

try:
    from .spec_evolution import create_workflow_closed_snapshot, print_commit_recommendation, resolve_spec_root
except ImportError:  # pragma: no cover - direct script execution
    from spec_evolution import create_workflow_closed_snapshot, print_commit_recommendation, resolve_spec_root


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root.")
    parser.add_argument("--spec-root", type=Path, default=Path("specs"), help="Spec root under the repository.")
    parser.add_argument("--workflow-name", help="Override ticket_plan.yaml name/status.workflow for the history directory.")
    parser.add_argument("--entry-name", default="closed-snapshot", help="History entry name under the workflow directory.")
    parser.add_argument("--summary", default="", help="Human-readable summary of the workflow close.")
    parser.add_argument("--result", action="append", type=Path, default=[], help="TLC, generated-case, adapter, or test result path to snapshot.")
    parser.add_argument("--allow-open", action="store_true", help="Allow snapshotting when ticket_plan.yaml still has open tickets.")
    parser.add_argument("--remove-active", action="store_true", help="Remove desired/current after they have been snapshotted.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    result = create_workflow_closed_snapshot(
        repo_root=repo_root,
        spec_root=args.spec_root,
        summary=args.summary,
        result_paths=args.result,
        workflow=args.workflow_name,
        entry_name=args.entry_name,
        allow_open=args.allow_open,
    )
    if args.remove_active:
        specs_dir = resolve_spec_root(repo_root, args.spec_root)
        for name in ["current", "desired_program_model"]:
            path = specs_dir / name
            if path.exists():
                shutil.rmtree(path)
                print(f"removed {path}")
    print_commit_recommendation(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
