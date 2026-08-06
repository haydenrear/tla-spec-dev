#!/usr/bin/env python3
"""Close a ticket workflow after current, desired, and program models converge.

This script is intentionally limited to workflow cleanup. Promote the converged
model to ``program_model`` and close every ticket in ``ticket_plan.yaml`` before
running it.
"""

from __future__ import annotations

import argparse
import filecmp
import re
import shutil
import sys
from pathlib import Path
from typing import Any

try:
    from .spec_evolution import create_workflow_closed_snapshot, print_commit_recommendation
except ImportError:  # pragma: no cover - direct script execution
    from spec_evolution import create_workflow_closed_snapshot, print_commit_recommendation


SEMANTIC_SUFFIXES = {".tla", ".cfg", ".yaml", ".yml"}
PLANNING_FILES = {"README.md", "ticket_plan.yaml", "desired_state.yaml"}
TICKET_CLOSED_STATUSES = {"accepted", "closed", "complete", "completed", "done"}
SKILL_ROOT = Path(__file__).resolve().parents[1]

#: The three spec trees a module reference can name. A binding map names the
#: tree it lives in, so promoting one between trees requires RE-ROOTING, not a
#: byte copy.
MODEL_DIR_NAMES = ("current", "desired_program_model", "program_model")
_MODULE_PREFIX = re.compile(r"\bspecs\.(?:%s)\." % "|".join(MODEL_DIR_NAMES))

#: Only mapping files carry module references; .tla and .cfg files do not.
REROOTED_NAMES = {"testgraph_bindings.yml", "case_adapters.toml"}


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
    if left.name in REROOTED_NAMES and right.name == left.name:
        # These files are RE-ROOTED on promotion, not copied, so the two trees
        # are equivalent when they differ ONLY by which spec tree their module
        # references name. Comparing the bytes would make a correct promotion
        # look like a divergence and block closeout. Normalizing to a common
        # placeholder compares everything else strictly, so a real edit to a
        # binding still shows up as a difference.
        return _MODULE_PREFIX.sub("specs.<tree>.", left.read_text(encoding="utf-8")) == (
            _MODULE_PREFIX.sub("specs.<tree>.", right.read_text(encoding="utf-8"))
        )
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


def workflow_promotion_guidance() -> str:
    """Explain how to prepare current/desired/program_model for workflow closeout."""
    semantic_suffixes = ", ".join(sorted(SEMANTIC_SUFFIXES))
    return (
        "How to prepare this workflow for closeout:\n"
        "- Closeout requires the semantic files in current/, desired_program_model/, and the promoted "
        "program_model/ to match, and every ticket in ticket_plan.yaml to be closed.\n"
        f"- Compared semantic files: {semantic_suffixes} (planning files such as README.md, "
        "ticket_plan.yaml, and status/notes metadata are ignored).\n"
        "- Option A: reconcile the models by hand (finish landing current/, promote the converged model "
        "into program_model/, mark every ticket closed), then re-run this command.\n"
        "- Option B: re-run with --accept-new to accept desired_program_model/ as the new current/ and "
        "program_model/ automatically (their semantic files are overwritten from desired_program_model/ "
        "before the snapshot); tickets must still be marked closed."
    )


def reroot_module_prefixes(text: str, dst_name: str) -> tuple[str, int]:
    """Rewrite ``specs.<any-model-dir>.`` to ``specs.<dst_name>.``.

    Returns the new text and how many references actually MOVED -- a reference
    already naming the destination is not a change and is not counted.

    Bare module names carry no prefix and are left exactly as they are. That is
    the form that cannot rot on promotion, and the one to prefer when authoring.
    """
    replacement = f"specs.{dst_name}."
    moved = sum(1 for m in _MODULE_PREFIX.finditer(text) if m.group(0) != replacement)
    return _MODULE_PREFIX.sub(replacement, text), moved


def promote_semantic_files(src: Path, dst: Path) -> list[str]:
    """Make dst's semantic files identical to src's, preserving dst planning/metadata files.

    Binding maps are RE-ROOTED rather than copied byte-for-byte. Promotion moves
    a file between spec trees, and a module reference inside it names the tree it
    came from: ``desired_program_model/`` is promoted onto BOTH ``current/`` and
    ``program_model/``, so a reference to ``specs.current.adapters`` is correct in
    one destination and dangling in the other. The whole-workflow close then
    DELETES ``current/``, which turns the dangling half into a reference to a
    package that no longer exists.

    Measured before this was fixed: 88 such references across two constituents of
    the meta-orchestrator integration repo, every one naming
    ``specs.current.adapters`` from inside a promoted ``program_model/`` tree
    whose sibling ``current/`` the same close had removed. Nothing failed,
    because the node that would have imported them was blocked for an unrelated
    reason -- a binding that is never resolved cannot fail to resolve.
    """
    if not src.exists():
        return []
    dst.mkdir(parents=True, exist_ok=True)
    src_files = _semantic_files(src)
    dst_files = _semantic_files(dst)
    promoted: list[str] = []
    for relative in sorted(set(dst_files) - set(src_files)):
        dst_files[relative].unlink()
        promoted.append(f"removed {relative}")
    for relative in sorted(src_files):
        destination = dst / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        source = src_files[relative]
        if Path(relative).name in REROOTED_NAMES:
            rerooted, moved = reroot_module_prefixes(
                source.read_text(encoding="utf-8"), dst.name
            )
            destination.write_text(rerooted, encoding="utf-8")
            promoted.append(
                f"wrote {relative} (re-rooted {moved} module reference(s) "
                f"to specs.{dst.name}.)"
                if moved
                else f"wrote {relative}"
            )
        else:
            shutil.copy2(source, destination)
            promoted.append(f"wrote {relative}")
    return promoted


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


def close_ticket_workflow(
    repo_root: Path,
    spec_root: Path,
    *,
    dry_run: bool,
    summary: str = "",
    result_paths: list[Path] | None = None,
    workflow_name: str | None = None,
    history_entry: str = "closed-snapshot",
    accept_new: bool = False,
    emit_feedback: bool = True,
) -> list[Path]:
    resolved_spec_root = _resolve_spec_root(repo_root, spec_root)
    program_dir = resolved_spec_root / "program_model"
    current_dir = resolved_spec_root / "current"
    desired_dir = resolved_spec_root / "desired_program_model"

    if accept_new:
        if not desired_dir.exists():
            raise SystemExit(f"cannot accept new workflow state: missing model directory: {desired_dir}")
        errors = validate_ticket_plan_closed(desired_dir / "ticket_plan.yaml")
        if errors:
            raise SystemExit(
                "cannot close ticket workflow:\n"
                + "\n".join(f"- {error}" for error in errors)
                + "\n\n"
                + workflow_promotion_guidance()
            )
        if not dry_run:
            for relative in promote_semantic_files(desired_dir, current_dir):
                print(f"accept-new current: {relative}")
            for relative in promote_semantic_files(desired_dir, program_dir):
                print(f"accept-new program_model: {relative}")
        else:
            print("would accept desired_program_model as the new current and program_model")
    else:
        errors = validate_equivalent(current_dir, desired_dir)
        errors.extend(validate_ticket_plan_closed(desired_dir / "ticket_plan.yaml"))
        errors.extend(validate_equivalent(desired_dir, program_dir, label="program_model"))
        if errors:
            raise SystemExit(
                "cannot close ticket workflow:\n"
                + "\n".join(f"- {error}" for error in errors)
                + "\n\n"
                + workflow_promotion_guidance()
            )

    if not dry_run:
        result = create_workflow_closed_snapshot(
            repo_root=repo_root,
            spec_root=spec_root,
            summary=summary,
            result_paths=result_paths or [],
            workflow=workflow_name,
            entry_name=history_entry,
            emit_feedback=emit_feedback,
        )
        print_commit_recommendation(result)
        # MF-017: migration.md Phase 6 calls the retro part of the workflow, not
        # optional polish. Workflow close records the filing status rather than
        # gating on it, but it must never be quiet about an unresolved retro:
        # current/ and desired/ are removed just below, so this is the last
        # moment the omission is cheap to fix.
        feedback = result.skill_feedback
        if feedback and not feedback.get("resolved"):
            print(
                "WARNING: skill feedback is unresolved at workflow close. "
                f"Fill in {feedback['path']} and file each finding as a ticket or PR "
                f"against {feedback['feedback_repository']}; the close history records this as not filed."
            )

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
    parser.add_argument("--workflow-name", help="Override ticket_plan.yaml name/status.workflow for the history directory.")
    parser.add_argument("--history-entry", default="closed-snapshot", help="History entry name under the workflow directory.")
    parser.add_argument("--summary", default="", help="Human-readable summary for the closed workflow snapshot.")
    parser.add_argument("--result", action="append", type=Path, default=[], help="TLC, generated-case, adapter, or test result path to snapshot.")
    parser.add_argument(
        "--no-skill-feedback",
        action="store_true",
        help="Do not emit/append the references/migration.md Phase 6 skill-feedback retro into <spec-root>/results/skill_feedback.md.",
    )
    parser.add_argument(
        "--accept-new",
        action="store_true",
        help="Accept desired_program_model/ as the new current/ and program_model/: skip the semantic-equivalence checks and overwrite them from desired_program_model/ before the snapshot. Tickets must still be closed.",
    )
    args = parser.parse_args()

    close_ticket_workflow(
        args.repo_root.resolve(),
        args.spec_root,
        dry_run=args.dry_run,
        summary=args.summary,
        result_paths=args.result,
        workflow_name=args.workflow_name,
        history_entry=args.history_entry,
        accept_new=args.accept_new,
        emit_feedback=not args.no_skill_feedback,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
