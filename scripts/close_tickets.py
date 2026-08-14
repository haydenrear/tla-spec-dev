#!/usr/bin/env python3
"""Close a ticket workflow after current, desired, and program models converge.

This script is intentionally limited to workflow cleanup. Promote the converged
model to ``program_model`` and close every ticket in ``ticket_plan.yaml`` before
running it.
"""

from __future__ import annotations

import argparse
import filecmp
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

try:
    from .spec_evolution import (
        create_workflow_closed_snapshot,
        live_receipt_manifests,
        print_commit_recommendation,
        validate_workflow_ticket_completion,
        workflow_name as resolve_workflow_name,
    )
except ImportError:  # pragma: no cover - direct script execution
    from spec_evolution import (
        create_workflow_closed_snapshot,
        live_receipt_manifests,
        print_commit_recommendation,
        validate_workflow_ticket_completion,
        workflow_name as resolve_workflow_name,
    )


SEMANTIC_SUFFIXES = {".tla", ".cfg", ".yaml", ".yml"}
#: Files that live in a model directory but are NOT part of the program model:
#: the schedule, the desired-state note, and the deferment backlog. They are
#: never compared for convergence and never promoted between trees.
#:
#: `deferred_findings.yaml` is the git-epic-workflow deferment backlog
#: (`references/deferment.md`), and it sits beside `ticket_plan.yaml` in
#: `desired_program_model/`. Classifying it as semantic made it a promotion
#: SUBJECT: it exists in `desired_program_model/` alone, so a convergence
#: promotion would have deleted the epic's entire findings ledger as a file
#: "the source no longer has", and `--accept-new` would have copied the backlog
#: into the promoted program model as though it were part of the specification.
#: It is bookkeeping about the work, not a statement about the program.
PLANNING_FILES = {
    "README.md",
    "ticket_plan.yaml",
    "desired_state.yaml",
    "deferred_findings.yaml",
}
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
        "program_model/ to match, every delivered ticket to have one matching successful-close receipt, "
        "and every retired ticket to have its exact retirement receipt.\n"
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


def validate_ticket_plan_closed(
    ticket_plan: Path,
    *,
    repo_root: Path | None = None,
    workflow: str | None = None,
) -> list[str]:
    if not ticket_plan.exists():
        return [f"missing ticket plan: {ticket_plan}"]
    plan = _load_yaml(ticket_plan)
    specs_dir = ticket_plan.resolve().parent.parent
    resolved_repo_root = (repo_root or specs_dir.parent).resolve()
    return validate_workflow_ticket_completion(
        repo_root=resolved_repo_root,
        specs_dir=specs_dir,
        plan=plan,
        workflow=workflow,
    )


def ticket_plan_has_retirements(ticket_plan: Path) -> bool:
    plan = _load_yaml(ticket_plan)
    tickets = plan.get("tickets")
    return isinstance(tickets, list) and any(
        isinstance(ticket, dict)
        and str(ticket.get("status", "")).strip().lower() == "retired"
        for ticket in tickets
    )


def _exact_snapshot_files(root: Path) -> dict[Path, Path]:
    return {
        path.relative_to(root): path
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and not any(part in IGNORED_EXACT_SNAPSHOT_NAMES for part in path.relative_to(root).parts)
    }


IGNORED_EXACT_SNAPSHOT_NAMES = {
    ".DS_Store",
    "__pycache__",
    ".history",
    ".tla-spec-evolution",
    ".gradle",
    ".pytest_cache",
    "build",
    "states",
}


def validate_exact_snapshot(left: Path, right: Path) -> list[str]:
    """Compare every archived planning and semantic byte, excluding snapshot ignores."""
    if not left.is_dir():
        return [f"missing desired program directory: {left}"]
    if not right.is_dir():
        return [f"missing terminal ticket desired snapshot: {right}"]
    left_files = _exact_snapshot_files(left)
    right_files = _exact_snapshot_files(right)
    errors: list[str] = []
    for relative in sorted(set(left_files) - set(right_files)):
        errors.append(f"file exists only in current desired_program_model: {relative}")
    for relative in sorted(set(right_files) - set(left_files)):
        errors.append(f"file exists only in terminal ticket desired snapshot: {relative}")
    for relative in sorted(set(left_files) & set(right_files)):
        if not filecmp.cmp(left_files[relative], right_files[relative], shallow=False):
            errors.append(f"terminal ticket desired snapshot differs: {relative}")
    return errors


def _terminal_delivered_ticket(plan: dict[str, Any]) -> tuple[int, dict[str, Any]] | None:
    tickets = plan.get("tickets")
    if not isinstance(tickets, list):
        return None
    delivered = [
        (index, ticket)
        for index, ticket in enumerate(tickets)
        if isinstance(ticket, dict)
        and str(ticket.get("status", "")).strip().lower()
        in {"accepted", "closed", "complete", "completed", "done"}
    ]
    if not delivered:
        return None
    ordered = [
        item
        for item in delivered
        if type(item[1].get("promotion_order")) is int
    ]
    if ordered:
        maximum = max(ticket["promotion_order"] for _, ticket in ordered)
        terminal = [item for item in ordered if item[1]["promotion_order"] == maximum]
        return terminal[0] if len(terminal) == 1 else None
    return delivered[-1]


def validate_retirement_accept_new_authority(
    *,
    repo_root: Path,
    specs_dir: Path,
    desired_dir: Path,
    plan: dict[str, Any],
    workflow: str | None,
) -> list[str]:
    """Prove withdrawn desired state came through the terminal delivered ticket."""
    terminal = _terminal_delivered_ticket(plan)
    if terminal is None:
        return [
            "retired-ticket --accept-new requires one terminal successfully closed "
            "non-retired ticket"
        ]
    terminal_index, terminal_ticket = terminal
    terminal_id = str(terminal_ticket.get("id", f"ticket-{terminal_index}"))
    resolved_workflow = resolve_workflow_name(plan, workflow)
    history_root = specs_dir / ".history" / resolved_workflow
    # Superseded receipts stay on disk but do not count: see the
    # SUPERSEDED_MARKER_KEY note in spec_evolution.
    candidates = live_receipt_manifests(history_root, kind="ticket", ticket_id=terminal_id)
    if len(candidates) != 1:
        return [
            f"terminal delivered ticket {terminal_id} must have exactly one successful "
            f"close receipt, found {len(candidates)}"
        ]
    manifest_path, manifest = candidates[0]
    errors: list[str] = []
    if manifest.get("ticket_index") != terminal_index:
        errors.append(
            f"terminal ticket {terminal_id} close receipt has the wrong immutable ordinal"
        )
    if manifest.get("workflow_name") != resolved_workflow:
        errors.append(f"terminal ticket {terminal_id} close receipt names another workflow")
    if str(manifest.get("ticket_status", "")).strip().lower() not in {
        "accepted",
        "closed",
        "complete",
        "completed",
        "done",
    }:
        errors.append(f"terminal ticket {terminal_id} receipt is not a successful close")
    guard = manifest.get("guard_weakening")
    if not isinstance(guard, dict) or guard.get("weakened") is not False:
        errors.append(
            f"terminal ticket {terminal_id} receipt was not an unweakened successful close"
        )
    if manifest.get("accept_new") is not False:
        errors.append(
            f"terminal ticket {terminal_id} receipt used accept-new and cannot authorize "
            "retirement closeout"
        )
    snapshots = manifest.get("snapshots")
    desired_records = [
        record
        for record in snapshots if isinstance(record, dict) and record.get("role") == "desired_program_model"
    ] if isinstance(snapshots, list) else []
    if len(desired_records) != 1:
        errors.append(
            f"terminal ticket {terminal_id} receipt must contain exactly one desired snapshot"
        )
        return errors
    snapshot_value = desired_records[0].get("snapshot")
    if not isinstance(snapshot_value, str) or not snapshot_value:
        return errors + [f"terminal ticket {terminal_id} desired snapshot path is missing"]
    snapshot_dir = Path(snapshot_value)
    if not snapshot_dir.is_absolute():
        snapshot_dir = repo_root / snapshot_dir
    receipt_dir = manifest_path.parent.resolve()
    expected_snapshot_dir = receipt_dir / "snapshots" / "desired_program_model"
    if snapshot_dir.resolve() != expected_snapshot_dir:
        errors.append(
            f"terminal ticket {terminal_id} desired snapshot is not the canonical "
            "snapshots/desired_program_model directory"
        )
        return errors
    errors.extend(validate_exact_snapshot(desired_dir, snapshot_dir))
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
        ticket_plan = desired_dir / "ticket_plan.yaml"
        errors = validate_ticket_plan_closed(
            ticket_plan,
            repo_root=repo_root,
            workflow=workflow_name,
        )
        if ticket_plan_has_retirements(ticket_plan):
            plan = _load_yaml(ticket_plan)
            retirement_errors = validate_retirement_accept_new_authority(
                repo_root=repo_root,
                specs_dir=resolved_spec_root,
                desired_dir=desired_dir,
                plan=plan,
                workflow=workflow_name,
            )
            if retirement_errors:
                errors.extend(retirement_errors)
                raise SystemExit(
                    "cannot close ticket workflow with --accept-new: the plan contains "
                    "retired tickets, so desired state must exactly match the archived "
                    "desired snapshot of the terminal unweakened successful ticket:\n"
                    + "\n".join(f"- {error}" for error in errors)
                )
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
        errors.extend(
            validate_ticket_plan_closed(
                desired_dir / "ticket_plan.yaml",
                repo_root=repo_root,
                workflow=workflow_name,
            )
        )
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
        help="Accept desired_program_model/ as the new current/ and program_model/: skip the semantic-equivalence checks and overwrite them from desired_program_model/ before the snapshot. Ticket receipts are still required; with retirement, desired must exactly match the terminal delivered ticket's archived desired snapshot.",
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
