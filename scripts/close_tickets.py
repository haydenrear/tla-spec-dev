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

# Model directories that are also importable Python packages, so their names
# can appear inside a dotted module reference such as
# ``specs.current.adapters:StreamLiteFsAdapter``.  ``program_model`` is in the
# set so the pattern describes the whole token rather than only the stale
# halves of it; re-rooting it onto itself is a no-op.
MODEL_PACKAGES = ("current", "desired_program_model", "program_model")

# Text files under a promoted baseline that can carry one.  The bindings and
# the spec-unit adapter table are the ones that MATTER -- their values are
# imported at run time -- but a stale reference in a manifest or a README sends
# a reader to the same deleted package, so the sweep is not narrowed to two
# filenames.
MODULE_REF_SUFFIXES = {".yml", ".yaml", ".toml", ".py", ".md", ".txt", ".cfg", ".json"}

# The lookbehind keeps ``myspecs.current.`` and ``a.specs.current.`` out: only a
# reference that starts at ``specs`` is one of ours to re-root.
_MODEL_PACKAGE_RE = re.compile(
    r"(?<![\w.])specs\.(" + "|".join(MODEL_PACKAGES) + r")\."
)


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


def promote_semantic_files(src: Path, dst: Path) -> list[str]:
    """Make dst's semantic files identical to src's, preserving dst planning/metadata files."""
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
        shutil.copy2(src_files[relative], destination)
        promoted.append(f"wrote {relative}")
    return promoted


def reroot_module_references(root: Path, package: str = "program_model") -> list[str]:
    """Re-root dotted module references under ``root`` onto ``specs.<package>``.

    THE CLOSE DELETES THE PACKAGE THE BINDINGS NAME.  A workflow is authored
    against ``specs/current``, so ``testgraph_bindings.yml`` and
    ``case_adapters.toml`` name ``specs.current.adapters:...`` -- correct while
    the workflow is open.  Promotion copied those files into
    ``specs/program_model`` verbatim and the close then removed
    ``specs/current``, leaving every promoted binding pointing at a package
    that no longer exists.  Nothing failed at close time: the next Test Graph
    run over the promoted baseline is where it surfaces, as an import error
    with no obvious connection to a workflow that closed cleanly weeks earlier.

    Re-rooting is done here rather than inside :func:`promote_semantic_files`
    on purpose.  ``--accept-new`` is only one of the two ways a baseline gets
    promoted; the other is the by-hand promotion that
    :func:`workflow_promotion_guidance` describes as Option A, which this
    module never sees.  Running the sweep over the promoted tree at close time
    covers both, and covers a baseline promoted by an older version of this
    script.

    Returns one line per rewritten file.  Nothing is changed silently: the
    caller prints these, and a workflow that needed no rewriting says nothing.
    """
    if not root.exists():
        return []
    replacement = f"specs.{package}."
    notes: list[str] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        if path.suffix.lower() not in MODULE_REF_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        stale = {
            match.group(0)
            for match in _MODEL_PACKAGE_RE.finditer(text)
            if match.group(1) != package
        }
        if not stale:
            continue
        rewritten, count = _MODEL_PACKAGE_RE.subn(replacement, text)
        path.write_text(rewritten, encoding="utf-8")
        notes.append(
            f"re-rooted {', '.join(sorted(stale))} -> {replacement} "
            f"in {path.relative_to(root).as_posix()} ({count} references)"
        )
    return notes


def stale_module_references(root: Path, package: str = "program_model") -> list[str]:
    """The rewrites :func:`reroot_module_references` would make, without making them."""
    if not root.exists():
        return []
    notes: list[str] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        if path.suffix.lower() not in MODULE_REF_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        stale = {
            match.group(0)
            for match in _MODEL_PACKAGE_RE.finditer(text)
            if match.group(1) != package
        }
        if stale:
            notes.append(
                f"would re-root {', '.join(sorted(stale))} -> specs.{package}. "
                f"in {path.relative_to(root).as_posix()}"
            )
    return notes


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

    # Before the snapshot, so the history entry records the baseline that will
    # still resolve after current/ and desired/ are removed just below.
    if dry_run:
        for note in stale_module_references(program_dir):
            print(f"program_model: {note}")
    else:
        for note in reroot_module_references(program_dir):
            print(f"program_model: {note}")

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
