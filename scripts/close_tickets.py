#!/usr/bin/env python3
"""Close a ticket workflow after current, desired, and program models converge.

This script is intentionally limited to workflow cleanup. Promote the converged
model to ``program_model`` and close every ticket in ``ticket_plan.yaml`` before
running it.
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path
from typing import Any


SEMANTIC_SUFFIXES = {".tla", ".cfg", ".yaml", ".yml"}
PLANNING_FILES = {"README.md", "ticket_plan.yaml", "desired_state.yaml"}
TICKET_CLOSED_STATUSES = {"accepted", "closed", "complete", "completed", "done"}
SKILL_ROOT = Path(__file__).resolve().parents[1]


def _load_yaml(path: Path) -> dict[str, Any]:
    skill_root = str(SKILL_ROOT)
    if skill_root not in sys.path:
        sys.path.insert(0, skill_root)
    from scripts.extract_spec_manifest import load_manifest

    if not path.exists():
        return {}
    return load_manifest(path)


def _resolve_spec_root(repo_root: Path, spec_root: Path) -> Path:
    return spec_root if spec_root.is_absolute() else repo_root / spec_root


def _semantic_files(root: Path) -> dict[Path, Path]:
    return {
        path.relative_to(root): path
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and path.suffix.lower() in SEMANTIC_SUFFIXES
        and path.relative_to(root).as_posix() not in PLANNING_FILES
    }


def _semantic_yaml(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: _semantic_yaml(inner)
            for key, inner in value.items()
            if key not in {"status", "notes"} and key != "package"
        }
    if isinstance(value, list):
        return [_semantic_yaml(inner) for inner in value]
    return value


def _semantic_file_matches(left: Path, right: Path) -> bool:
    if left.name == "spec_manifest.yaml" and right.name == "spec_manifest.yaml":
        return _semantic_yaml(_load_yaml(left)) == _semantic_yaml(_load_yaml(right))
    return filecmp.cmp(left, right, shallow=False)


def validate_equivalent(current_dir: Path, desired_dir: Path, label: str = "desired_program_model") -> list[str]:
    errors: list[str] = []
    if not current_dir.exists():
        errors.append(f"missing model directory: {current_dir}")
    if not desired_dir.exists():
        errors.append(f"missing model directory: {desired_dir}")
    if errors:
        return errors

    current_files = _semantic_files(current_dir)
    desired_files = _semantic_files(desired_dir)
    if not current_files and not desired_files:
        errors.append("no semantic model files found to compare")
        return errors

    current_only = sorted(set(current_files) - set(desired_files))
    desired_only = sorted(set(desired_files) - set(current_files))
    for relative in current_only:
        errors.append(f"semantic file exists only in {current_dir.name}: {relative}")
    for relative in desired_only:
        errors.append(f"semantic file exists only in {label}: {relative}")

    for relative in sorted(set(current_files) & set(desired_files)):
        if not _semantic_file_matches(current_files[relative], desired_files[relative]):
            errors.append(f"semantic file differs: {relative}")
    return errors


def validate_ticket_plan_closed(ticket_plan: Path) -> list[str]:
    if not ticket_plan.exists():
        return [f"missing ticket plan: {ticket_plan}"]
    plan = _load_yaml(ticket_plan)
    tickets = plan.get("tickets")
    if not isinstance(tickets, list):
        return [f"ticket plan has no tickets list: {ticket_plan}"]
    errors: list[str] = []
    for index, ticket in enumerate(tickets, start=1):
        if not isinstance(ticket, dict):
            errors.append(f"ticket {index} is not a mapping")
            continue
        ticket_id = ticket.get("id", f"#{index}")
        status = str(ticket.get("status", "")).strip().lower()
        if status not in TICKET_CLOSED_STATUSES:
            errors.append(f"ticket {ticket_id} is not closed: status={status or '(missing)'}")
    return errors


def close_ticket_workflow(repo_root: Path, spec_root: Path, *, dry_run: bool) -> list[Path]:
    resolved_spec_root = _resolve_spec_root(repo_root, spec_root)
    program_dir = resolved_spec_root / "program_model"
    current_dir = resolved_spec_root / "current"
    desired_dir = resolved_spec_root / "desired_program_model"

    errors = validate_equivalent(current_dir, desired_dir)
    errors.extend(validate_ticket_plan_closed(desired_dir / "ticket_plan.yaml"))
    errors.extend(validate_equivalent(desired_dir, program_dir, label="program_model"))
    if errors:
        raise SystemExit("cannot close ticket workflow:\n" + "\n".join(f"- {error}" for error in errors))

    removed = [current_dir, desired_dir]
    for directory in removed:
        if dry_run:
            print(f"would remove {directory}")
        else:
            shutil.rmtree(directory)
            print(f"removed {directory}")
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root.")
    parser.add_argument("--spec-root", type=Path, default=Path("specs"), help="Spec root under the repository.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print removals without deleting files.")
    args = parser.parse_args()

    close_ticket_workflow(args.repo_root.resolve(), args.spec_root, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
