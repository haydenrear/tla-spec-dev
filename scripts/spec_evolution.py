"""Append-only spec-workflow history helpers."""

from __future__ import annotations

import dataclasses
import json
import re
import shlex
import shutil
import subprocess
import sys
import stat
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from .skill_feedback import emit_skill_feedback, print_skill_feedback_report
except ImportError:  # pragma: no cover - direct script execution
    from skill_feedback import emit_skill_feedback, print_skill_feedback_report

try:
    from . import complexity_ledger
except ImportError:  # pragma: no cover - direct script execution
    import complexity_ledger


SKILL_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIRS = ("program_model", "desired_program_model", "current")
IGNORED_COPY_NAMES = {
    ".DS_Store",
    "__pycache__",
    ".history",
    ".tla-spec-evolution",
    ".gradle",
    ".pytest_cache",
    "build",
    "states",
}
TICKET_CLOSED_STATUSES = {"accepted", "closed", "complete", "completed", "done"}
SEMANTIC_SUFFIXES = {".tla", ".cfg", ".yaml", ".yml", ".py", ".toml", ".json"}
PLANNING_FILES = {"README.md", "ticket_plan.yaml", "desired_state.yaml", "ticket.yaml"}


@dataclass(frozen=True)
class HistoryEntryResult:
    entry_dir: Path
    recommendation: str
    git_add_command: str
    git_commit_command: str
    promotion: dict[str, Any] | None = None
    skill_feedback: dict[str, Any] | None = None
    complexity_ledger: dict[str, Any] | None = None


def _load_yaml(path: Path) -> dict[str, Any]:
    skill_root = str(SKILL_ROOT)
    if skill_root not in sys.path:
        sys.path.insert(0, skill_root)
    from scripts.extract_spec_manifest import load_manifest

    if not path.exists():
        return {}
    return load_manifest(path)


def resolve_spec_root(repo_root: Path, spec_root: Path) -> Path:
    return (spec_root if spec_root.is_absolute() else repo_root / spec_root).resolve()


def resolve_workflow_path(path: Path, specs_dir: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    cwd_candidate = (Path.cwd() / path).resolve()
    if cwd_candidate.exists() or (path.parts and path.parts[0] == specs_dir.name):
        return cwd_candidate
    return (specs_dir / path).resolve()


def safe_segment(value: str) -> str:
    rendered = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    rendered = rendered.strip(".-")
    if not rendered:
        raise SystemExit("ERROR: history path segments must contain at least one safe character")
    return rendered


def rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(resolved)


def git_value(*args: str) -> str | None:
    try:
        result = subprocess.run(["git", *args], check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    rendered = result.stdout.strip()
    return rendered or None


def git_metadata() -> dict[str, str | None]:
    inside = git_value("rev-parse", "--is-inside-work-tree")
    if inside != "true":
        return {"inside_work_tree": inside, "branch": None, "commit": None}
    return {
        "inside_work_tree": inside,
        "branch": git_value("branch", "--show-current"),
        "commit": git_value("rev-parse", "--short", "HEAD"),
    }


def copy_ignore(_directory: str, names: list[str]) -> set[str]:
    return {name for name in names if name in IGNORED_COPY_NAMES}


def make_directory_appendable(path: Path) -> None:
    if not path.exists():
        return
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)


def make_history_appendable(specs_dir: Path, workflow: str) -> None:
    history_dir = specs_dir / ".history"
    make_directory_appendable(history_dir)
    make_directory_appendable(history_dir / safe_segment(workflow))


def copy_snapshot(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, ignore=copy_ignore)
    else:
        shutil.copy2(source, destination)


def remove_state_directories(*roots: Path) -> list[Path]:
    """Remove generated TLC state directories before archiving workflow data."""
    removed: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        state_dirs = sorted(
            (path for path in root.rglob("states") if path.is_dir()),
            key=lambda path: len(path.parts),
            reverse=True,
        )
        for state_dir in state_dirs:
            shutil.rmtree(state_dir)
            removed.append(state_dir)
    return removed


def add_copied_path(records: list[dict[str, Any]], *, role: str, source: Path, destination: Path) -> None:
    source = source.resolve()
    record: dict[str, Any] = {"role": role, "source": rel(source), "exists": source.exists()}
    if source.exists():
        copy_snapshot(source, destination)
        record["snapshot"] = rel(destination)
    records.append(record)


def ticket_plan_path(specs_dir: Path) -> Path:
    return specs_dir / "desired_program_model" / "ticket_plan.yaml"


def active_ticket_dir(specs_dir: Path, ticket_ref: str, ticket_root: Path = Path("tickets")) -> Path:
    root = ticket_root if ticket_root.is_absolute() else specs_dir / ticket_root
    return root / safe_segment(ticket_ref)


def load_ticket_plan(specs_dir: Path) -> dict[str, Any]:
    path = ticket_plan_path(specs_dir)
    if not path.exists():
        raise SystemExit(f"ERROR: missing desired program ticket plan: {path}")
    plan = _load_yaml(path)
    if not isinstance(plan, dict):
        raise SystemExit(f"ERROR: ticket plan must be a mapping: {path}")
    if not isinstance(plan.get("tickets"), list):
        raise SystemExit(f"ERROR: ticket plan must contain a tickets list: {path}")
    return plan


def workflow_name(plan: dict[str, Any], explicit: str | None = None) -> str:
    if explicit:
        return safe_segment(explicit)
    if isinstance(plan.get("name"), str) and plan["name"].strip():
        return safe_segment(plan["name"])
    status = plan.get("status")
    if isinstance(status, dict) and isinstance(status.get("workflow"), str) and status["workflow"].strip():
        return safe_segment(status["workflow"])
    return "spec-workflow"


def ticket_status(ticket: dict[str, Any]) -> str:
    return str(ticket.get("status", "")).strip().lower()


def ticket_id(ticket: dict[str, Any], index: int) -> str:
    value = ticket.get("id")
    return str(value) if value is not None else f"ticket-{index}"


def find_ticket(plan: dict[str, Any], ticket_ref: str) -> tuple[int, dict[str, Any]]:
    tickets = plan.get("tickets")
    if not isinstance(tickets, list):
        raise SystemExit("ERROR: ticket plan has no tickets list")

    for index, ticket in enumerate(tickets):
        if isinstance(ticket, dict) and str(ticket.get("id", "")) == ticket_ref:
            return index, ticket

    normalized = ticket_ref.removeprefix("ticket-")
    if normalized.isdigit():
        index = int(normalized)
        if 0 <= index < len(tickets) and isinstance(tickets[index], dict):
            return index, tickets[index]

    raise SystemExit(f"ERROR: ticket {ticket_ref!r} was not found in desired_program_model/ticket_plan.yaml")


def ticket_entry_name(index: int, ticket: dict[str, Any]) -> str:
    return f"ticket-{index:03d}-{safe_segment(ticket_id(ticket, index))}"


def history_root(specs_dir: Path, workflow: str) -> Path:
    return specs_dir / ".history" / safe_segment(workflow)


def commit_recommendation(entry_dir: Path, message: str, *, extra_paths: list[Path] | None = None) -> HistoryEntryResult:
    paths = [entry_dir]
    for path in extra_paths or []:
        if path not in paths and path.exists():
            paths.append(path)
    git_add_command = "git add " + " ".join(shlex.quote(rel(path)) for path in paths)
    git_commit_command = f"git commit -m {message!r}"
    return HistoryEntryResult(
        entry_dir=entry_dir,
        recommendation=f"It is recommended to commit this history directory now: {rel(entry_dir)}",
        git_add_command=git_add_command,
        git_commit_command=git_commit_command,
    )


def write_manifest(entry_dir: Path, manifest: dict[str, Any]) -> None:
    (entry_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


def write_summary(entry_dir: Path, *, title: str, summary: str, manifest: dict[str, Any]) -> None:
    lines = [
        f"# {title}\n\n",
        f"- Workflow: `{manifest['workflow_name']}`\n",
        f"- Entry: `{manifest['entry_name']}`\n",
    ]
    if manifest.get("ticket_id"):
        lines.append(f"- Ticket: `{manifest['ticket_id']}`\n")
    lines.extend(
        [
            "\n## Summary\n\n",
            summary.strip() or "No summary supplied.",
            "\n\n## Snapshots\n\n",
        ]
    )
    for snapshot in manifest["snapshots"]:
        lines.append(f"- `{snapshot['role']}`: `{snapshot.get('snapshot', 'missing')}`\n")
    lines.extend(
        [
            "\n## Follow-up\n\n",
            "Review this append-only entry, then commit the history directory with the related spec changes.\n",
        ]
    )
    (entry_dir / "summary.md").write_text("".join(lines))


def snapshot_models(specs_dir: Path, entry_dir: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for name in MODEL_DIRS:
        add_copied_path(records, role=name, source=specs_dir / name, destination=entry_dir / "snapshots" / name)
    return records


def snapshot_results(specs_dir: Path, entry_dir: Path, result_paths: list[Path]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in result_paths:
        source = resolve_workflow_path(path, specs_dir)
        add_copied_path(records, role="result", source=source, destination=entry_dir / "results" / source.name)
    return records


def semantic_yaml(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: semantic_yaml(inner)
            for key, inner in value.items()
            if key not in {"status", "notes", "promotion"} and key != "package"
        }
    if isinstance(value, list):
        return [semantic_yaml(inner) for inner in value]
    return value


def semantic_files(root: Path) -> dict[Path, Path]:
    return {
        path.relative_to(root): path
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and path.suffix.lower() in SEMANTIC_SUFFIXES
        and path.relative_to(root).as_posix() not in PLANNING_FILES
    }


def semantic_file_matches(left: Path, right: Path) -> bool:
    if left.name == "spec_manifest.yaml" and right.name == "spec_manifest.yaml":
        return semantic_yaml(_load_yaml(left)) == semantic_yaml(_load_yaml(right))
    return left.read_bytes() == right.read_bytes()


def ticket_promotion_guidance(active_dir: Path) -> str:
    """Explain how to prepare a ticket for promotion when current/ diverges from desired/."""
    semantic_suffixes = ", ".join(sorted(SEMANTIC_SUFFIXES))
    return (
        "How to prepare this ticket for promotion:\n"
        f"- Closing promotes the ticket desired/ into the project current/, so ticket current/ "
        f"must first semantically match desired/ under {rel(active_dir)}.\n"
        f"- Compared semantic files: {semantic_suffixes} (planning files such as README.md, "
        "ticket_plan.yaml, and status/notes/promotion metadata are ignored).\n"
        "- Option A: edit current/ (the TLA+ .tla/.cfg, model .yml, adapters, and tests) until it "
        "matches desired/, re-run the spec-unit validations, then re-run the close.\n"
        "- Option B: re-run the close with --accept-new to accept the ticket desired/ as the new "
        "current/ automatically (current/ is overwritten from desired/ before promotion)."
    )


def validate_equivalent_model_dirs(left_dir: Path, right_dir: Path, *, left_label: str = "current", right_label: str = "desired") -> list[str]:
    errors: list[str] = []
    if not left_dir.exists():
        errors.append(f"missing model directory: {left_dir}")
    if not right_dir.exists():
        errors.append(f"missing model directory: {right_dir}")
    if errors:
        return errors
    left_files = semantic_files(left_dir)
    right_files = semantic_files(right_dir)
    if not left_files and not right_files:
        errors.append("no semantic model files found to compare")
        return errors
    for relative in sorted(set(left_files) - set(right_files)):
        errors.append(f"semantic file exists only in {left_label}: {relative}")
    for relative in sorted(set(right_files) - set(left_files)):
        errors.append(f"semantic file exists only in {right_label}: {relative}")
    for relative in sorted(set(left_files) & set(right_files)):
        if not semantic_file_matches(left_files[relative], right_files[relative]):
            errors.append(f"semantic file differs: {relative}")
    return errors


def merge_tree(src: Path, dst: Path) -> list[dict[str, Any]]:
    if not src.exists():
        return []
    copied: list[dict[str, Any]] = []
    for source in sorted(path for path in src.rglob("*") if path.is_file()):
        relative = source.relative_to(src)
        if any(part in IGNORED_COPY_NAMES for part in relative.parts):
            continue
        destination = dst / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied.append(
            {
                "source": rel(source),
                "destination": rel(destination),
                "relative": relative.as_posix(),
            }
        )
    return copied


def replace_tree(src: Path, dst: Path) -> list[dict[str, Any]]:
    if dst.exists():
        shutil.rmtree(dst)
    return merge_tree(src, dst)


def tree_relative_files(root: Path) -> set[str]:
    """Relative posix paths of every copyable file under ``root``."""
    if not root.exists():
        return set()
    found: set[str] = set()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if any(part in IGNORED_COPY_NAMES for part in relative.parts):
            continue
        found.add(relative.as_posix())
    return found


def load_ticket_seed_manifest(active_dir: Path) -> set[str] | None:
    """Paths the ticket workspace was seeded with, or None when unrecorded.

    ``open ticket`` records the exact set of project ``current/`` paths it
    copied into the ticket ``desired/`` tree. That set is the only evidence of
    what the ticket had the opportunity to delete. Tickets opened before this
    was recorded return None, which callers must treat as "no deletion intent
    is provable" rather than as an empty seed.
    """
    path = active_dir / "ticket.yaml"
    if not path.exists():
        return None
    # ticket.yaml is written by `open ticket` as JSON (a YAML subset); the
    # repository's minimal YAML reader cannot parse JSON, so try JSON first.
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        try:
            payload = _load_yaml(path)
        except Exception:  # noqa: BLE001 - an unreadable ticket.yaml means "no evidence"
            return None
    if not isinstance(payload, dict):
        return None
    seed = payload.get("seed_manifest")
    if not isinstance(seed, dict):
        return None
    desired = seed.get("desired")
    if not isinstance(desired, list):
        return None
    return {str(item) for item in desired}


def prune_empty_directories(root: Path) -> None:
    if not root.exists():
        return
    for path in sorted((p for p in root.rglob("*") if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        try:
            next(path.iterdir())
        except StopIteration:
            path.rmdir()


def promote_current_tree(src: Path, dst: Path, seed: set[str] | None) -> dict[str, Any]:
    """Promote ticket ``desired/`` onto project ``current/`` without silent loss.

    ``dst`` stays a whole-program working copy rather than becoming an
    accumulating union: a path the ticket genuinely deleted is still removed
    from ``dst``. The distinction is provenance, not existence. A path is only
    removed when it was seeded into the ticket workspace and the ticket then
    dropped it -- that is a recorded deletion decision. A path that was never
    seeded (excluded from the workspace by design, or added to project
    ``current/`` after the ticket was opened) carries no such decision, so
    promotion has no authority to delete it and preserves it instead.

    Every removal and every preservation is reported so that close output can
    enumerate them. Nothing leaves ``dst`` unannounced.
    """
    src_files = tree_relative_files(src)
    dst_files = tree_relative_files(dst)
    unmatched = dst_files - src_files

    if seed is None:
        removed = set()
        preserved = unmatched
        basis = "no seed manifest recorded for this ticket; preserving every current-only path"
    else:
        removed = unmatched & seed
        preserved = unmatched - seed
        basis = "seed manifest recorded at open; removing only seeded paths the ticket dropped"

    for relative in sorted(removed):
        target = dst / relative
        if target.is_file():
            target.unlink()
    prune_empty_directories(dst)

    return {
        "role": "current",
        "source": rel(src),
        "destination": rel(dst),
        "operation": "promote ticket desired onto project current, preserving unseeded current-only paths",
        "seed_basis": basis,
        "seed_recorded": seed is not None,
        "removed": sorted(removed),
        "preserved": sorted(preserved),
        "files": merge_tree(src, dst),
    }


def promote_ticket_outputs(active_dir: Path, specs_dir: Path) -> dict[str, Any]:
    merged = [
        promote_current_tree(
            active_dir / "desired",
            specs_dir / "current",
            load_ticket_seed_manifest(active_dir),
        )
    ]
    for name in ("testgraph", "test_graph"):
        source = active_dir / name
        if source.exists():
            merged.append(
                {
                    "role": name,
                    "source": rel(source),
                    "destination": rel(specs_dir / name),
                    "operation": "merge",
                    "files": merge_tree(source, specs_dir / name),
                }
            )
    return {
        "source": rel(active_dir),
        "destination": rel(specs_dir),
        "operation": "replace project current with ticket desired and merge ticket artifacts into project specs",
        "merged": merged,
    }


#: RC-01 (MF-026, owner decision 2026-08-01). The three guard-weakening flags
#: that reach `close ticket`, with what each one bypasses. The other three the
#: owner named -- `--validate-only` on the spec-unit run, `--force` and
#: `--dry-run` on scaffold/open -- weaken an EARLIER step and never reach this
#: function, which is a limit of what the close path can observe and is
#: recorded as such on TlaSpecDevCli.tla's CloseTicketWeakened.
CLOSE_GUARD_WEAKENING_FLAGS = {
    "--accept-new": "skips the ticket current == desired check and overwrites current/ from desired/",
    "--allow-open": "snapshots a ticket whose ticket_plan.yaml status is not closed/done",
    "--no-promote-current": "closes without promoting ticket desired/ into project current/",
}


def weakening_flags_record(
    *, accept_new: bool, allow_open: bool, promote_current: bool
) -> dict[str, Any]:
    """Name the guard-weakening flags this close was taken under.

    RC-01. `CloseTicket` in the model guards on the ticket having reached
    `TicketSpecUnitTestsPassed`, and `ClosedTicketsPassedSpecUnitTests` is an
    invariant TLC checks over the whole reachable state space -- while
    `--accept-new` and `--allow-open` exist precisely to get past that
    precondition. Before this record existed no modeled state and no artifact
    distinguished the two closes, so the strongest claim the model makes had a
    bypass that no oracle in this toolchain could see: the mutation kill test
    seeds faults per declared port and per invariant, i.e. only inside modeled
    boundaries.

    Reports, never refuses. The flags ship, they have legitimate uses, and a
    refusal the CLI does not perform would be a false assurance of the same
    kind. `weakened` is the fact the model's `TicketClosedWeakened` stage
    records.
    """
    used = []
    if accept_new:
        used.append("--accept-new")
    if allow_open:
        used.append("--allow-open")
    if not promote_current:
        used.append("--no-promote-current")
    return {
        "weakened": bool(used),
        "flags": used,
        "bypassed": [CLOSE_GUARD_WEAKENING_FLAGS[flag] for flag in used],
        "model_action": "CloseTicketWeakened" if used else "CloseTicket",
        "note": (
            "RC-01: a close taken under a guard-weakening flag is a different modeled "
            "state from one taken under the guard. Recorded, never refused."
        ),
    }


def accept_new_ticket_current(active_dir: Path) -> dict[str, Any]:
    """Overwrite ticket current/ with desired/ so the accepted outcome is the ticket desired state."""
    return {
        "role": "accept_new_current",
        "source": rel(active_dir / "desired"),
        "destination": rel(active_dir / "current"),
        "operation": "replace ticket current with ticket desired (accept-new)",
        "files": replace_tree(active_dir / "desired", active_dir / "current"),
    }


# The accepted baseline layout, outermost view first. External EXTENDS
# Internal EXTENDS Core, so External is the module whose cfg configures the
# whole program; measuring Core measures a module with no actions at all.
BASELINE_VIEW_PREFERENCE = ("External", "Internal", "Core")
MODEL_DECLARATION_KEY = "model"


class ModelSelectionError(Exception):
    """The measured model could not be identified, or the pair does not match.

    Raised instead of returning a model the ledger would silently mis-measure.
    "I could not measure this" is the only honest outcome here (CM-F1): the
    alternative -- pairing an arbitrary module with an arbitrary cfg -- reports
    ``bound = None, modularity = 0.0`` and looks like a measurement.
    """


@dataclass(frozen=True)
class ModelSelection:
    """The model the ledger measures, and why that one."""

    tla: Path
    cfg: Path
    manifest: Path | None
    source: str

    def describe(self) -> str:
        return f"{self.tla.name} + {self.cfg.name} ({self.source})"


def _model_candidates(model_dir: Path) -> list[Path]:
    """Non-MC ``*.tla`` files in a model directory, alphabetically."""
    return sorted(p for p in model_dir.glob("*.tla") if not p.name.startswith("MC"))


def _resolve_cfg(model_dir: Path, tla_path: Path, *, source: str) -> Path:
    """The cfg belonging to ``tla_path``: same stem, then MC.cfg, then a unique one."""
    stem_cfg = model_dir / f"{tla_path.stem}.cfg"
    if stem_cfg.is_file():
        return stem_cfg
    mc_cfg = model_dir / "MC.cfg"
    if mc_cfg.is_file():
        return mc_cfg
    candidates = sorted(model_dir.glob("*.cfg"))
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise ModelSelectionError(
            f"no TLC config found beside {tla_path.name} in {rel(model_dir)} "
            f"(selected by {source}). Expected {tla_path.stem}.cfg or MC.cfg."
        )
    raise ModelSelectionError(
        f"cannot tell which config belongs to {tla_path.name} in {rel(model_dir)} "
        f"(selected by {source}): found "
        + ", ".join(path.name for path in candidates)
        + f", and neither {tla_path.stem}.cfg nor MC.cfg is among them. "
        "Declare the pair explicitly in spec_manifest.yaml:\n"
        "  model:\n"
        f"    tla: {tla_path.name}\n"
        "    cfg: <the config that configures it>"
    )


def select_model_files(model_dir: Path) -> ModelSelection | None:
    """Identify the model a ledger measures, DECLARED before discovered (CM-F1).

    Resolution order, most explicit first:

    1. ``model: {tla: ..., cfg: ...}`` in ``spec_manifest.yaml``.
    2. The accepted three-module baseline: the outermost view present
       (External, else Internal, else Core) with its own cfg.
    3. A legacy single-module spec: ``<manifest module:>.tla``, else the only
       non-``MC*`` module in the directory.

    Returns None only when the directory holds no model at all. Ambiguity --
    several candidate modules and nothing declaring which one is measured --
    raises :class:`ModelSelectionError` rather than picking alphabetically,
    which is the defect this function replaces: on every Core/Internal/External
    baseline the alphabetical pick resolved to ``Core.tla`` paired with
    ``External.cfg`` and the ledger reported ``bound = None``.
    """
    model_dir = Path(model_dir)
    if not model_dir.is_dir():
        return None
    manifest_path = model_dir / "spec_manifest.yaml"
    manifest = _load_yaml(manifest_path) if manifest_path.is_file() else {}
    manifest_arg = manifest_path if manifest_path.is_file() else None

    declared = manifest.get(MODEL_DECLARATION_KEY)
    if isinstance(declared, dict) and declared:
        tla_name = str(declared.get("tla") or "").strip()
        cfg_name = str(declared.get("cfg") or "").strip()
        if not tla_name or not cfg_name:
            raise ModelSelectionError(
                f"spec_manifest.yaml in {rel(model_dir)} declares a `model:` block "
                "without both `tla:` and `cfg:`. A half-declared model is not a "
                "measurement; give both filenames."
            )
        tla_path = model_dir / tla_name
        cfg_path = model_dir / cfg_name
        missing = [path.name for path in (tla_path, cfg_path) if not path.is_file()]
        if missing:
            raise ModelSelectionError(
                f"spec_manifest.yaml in {rel(model_dir)} declares model "
                f"{tla_name} + {cfg_name}, but " + ", ".join(missing) + " is not there."
            )
        return ModelSelection(tla_path, cfg_path, manifest_arg, "declared in spec_manifest.yaml")

    candidates = _model_candidates(model_dir)
    if not candidates:
        return None

    by_name = {path.stem: path for path in candidates}
    if "Internal" in by_name:
        # The accepted baseline. Case modules and other satellites in the same
        # directory no longer change which model is measured.
        for view in BASELINE_VIEW_PREFERENCE:
            if view in by_name:
                tla_path = by_name[view]
                source = "accepted Core/Internal/External baseline (outermost view)"
                return ModelSelection(
                    tla_path, _resolve_cfg(model_dir, tla_path, source=source), manifest_arg, source
                )

    module_name = str(manifest.get("module") or "").strip()
    if module_name and module_name in by_name:
        tla_path = by_name[module_name]
        source = "spec_manifest.yaml `module:`"
        return ModelSelection(
            tla_path, _resolve_cfg(model_dir, tla_path, source=source), manifest_arg, source
        )

    if len(candidates) == 1:
        tla_path = candidates[0]
        source = "the only module in the directory"
        return ModelSelection(
            tla_path, _resolve_cfg(model_dir, tla_path, source=source), manifest_arg, source
        )

    raise ModelSelectionError(
        f"cannot tell which model the ledger measures in {rel(model_dir)}: found "
        + ", ".join(path.name for path in candidates)
        + ". Picking the alphabetically first one is how a ledger ends up measuring "
        "a module with no variables and no actions (CM-F1). Declare it:\n"
        "  model:\n"
        "    tla: <module>.tla\n"
        "    cfg: <config>.cfg"
    )


def validate_model_pair(selection: ModelSelection) -> list[str]:
    """Reasons the cfg does not configure the module, or [] when the pair matches.

    A cfg naming a SPECIFICATION, INIT/NEXT, invariant, or constant the module
    hierarchy does not declare is not a model -- it is two files in the same
    directory. Every finding here is "I could not measure this", never a
    complexity judgement.
    """
    skill_root = str(SKILL_ROOT)
    if skill_root not in sys.path:
        sys.path.insert(0, skill_root)
    from scripts import analyze_complexity

    try:
        resolved = analyze_complexity.resolve_module(selection.tla)
    except analyze_complexity.ModuleResolutionError as error:
        return [f"{selection.tla.name} cannot be resolved: {error}"]

    cfg_text = selection.cfg.read_text(encoding="utf-8")
    defined = {definition.name for definition in resolved.defs}
    problems: list[str] = []

    behavior_keys = [
        (key, analyze_complexity._parse_cfg_named_entry(cfg_text, key))
        for key in ("SPECIFICATION", "INIT", "NEXT")
    ]
    named = [(key, name) for key, name in behavior_keys if name]
    for key, name in named:
        if name not in defined:
            problems.append(
                f"{selection.cfg.name} configures {key} {name}, which "
                f"{selection.tla.name} (with everything it EXTENDS) does not define"
            )
    if not named:
        problems.append(
            f"{selection.cfg.name} names no SPECIFICATION, INIT, or NEXT, so there is "
            f"no behavior for {selection.tla.name} to be measured against"
        )

    # CM-01-DF-02 was a workaround here: parse_cfg_invariants used to hand back
    # the bare keyword line that ENDS an INVARIANT block ("INVARIANT Inv"
    # followed by a bare "CONSTANTS") as if it were another invariant name, so
    # this loop skipped TLC config keywords or it manufactured a mismatch on a
    # pair that matches. RP-04 fixed the parser and measured the skip as dead
    # code; RP-03 deleted it. The proof is
    # specs/.history/architectural-coherence-epic/ticket-009-RP-04/ticket/results/cm-01-df-02-workaround-is-now-dead.txt
    for invariant in analyze_complexity.parse_cfg_invariants(cfg_text):
        if invariant not in defined:
            problems.append(
                f"{selection.cfg.name} configures INVARIANT {invariant}, which "
                f"{selection.tla.name} does not define"
            )

    declared_constants = set(resolved.constants)
    for constant in analyze_complexity.parse_cfg_constants(cfg_text):
        if constant not in declared_constants:
            problems.append(
                f"{selection.cfg.name} assigns CONSTANT {constant}, which "
                f"{selection.tla.name} does not declare"
            )

    return problems


def find_model_files(model_dir: Path) -> tuple[Path, Path, Path | None] | None:
    """Locate (tla, cfg, manifest) inside a model tree, or None when absent.

    Returning None is NOT a pass. Callers treat an unlocatable model as a hard
    failure of the complexity ledger; the separation exists so the error message
    can name the directory it searched.
    """
    selection = select_model_files(model_dir)
    if selection is None:
        return None
    return selection.tla, selection.cfg, selection.manifest


def complexity_ledger_input_path(specs_dir: Path, active_dir: Path | None, scope: str) -> Path:
    """Deterministic location of the ledger input for this close.

    Deterministic on purpose: a path the caller can vary is a path the caller
    can point somewhere empty.
    """
    if scope == "ticket" and active_dir is not None:
        return active_dir / "results" / "complexity_ledger.yaml"
    return specs_dir / "results" / "complexity_ledger_input.yaml"


def record_complexity_ledger(
    specs_dir: Path,
    *,
    scope: str,
    scope_id: str,
    workflow: str,
    model_dir: Path,
    input_path: Path,
    tlc_report: Path | None = None,
) -> dict[str, Any]:
    """Evaluate the standing objective and refuse the close when it is not met.

    Called BEFORE the history entry is created and before promotion, so a
    refused close leaves the tree untouched.
    """
    try:
        selection = select_model_files(model_dir)
    except ModelSelectionError as error:
        raise SystemExit(
            f"ERROR: complexity ledger could not identify the model to measure in "
            f"{rel(model_dir)}.\n{error}"
        ) from error
    if selection is None:
        raise SystemExit(
            f"ERROR: complexity ledger cannot find a model to measure in {rel(model_dir)}.\n"
            "The ledger records measured complexity; it does not estimate and it does "
            "not skip. Point the close at a tree containing <module>.tla and MC.cfg."
        )
    mismatches = validate_model_pair(selection)
    if mismatches:
        raise SystemExit(
            f"ERROR: complexity ledger could not measure {selection.describe()} in "
            f"{rel(model_dir)}:\n"
            + "\n".join(f"- {problem}" for problem in mismatches)
            + "\n\nA config that does not configure the module is not a measurement. "
            "Declare the pair in spec_manifest.yaml:\n  model:\n    tla: <module>.tla\n"
            "    cfg: <config>.cfg"
        )
    print(f"complexity ledger model: {selection.describe()}")
    tla_path, cfg_path, manifest_path = selection.tla, selection.cfg, selection.manifest
    try:
        ledger_input = complexity_ledger.load_input(input_path)
    except complexity_ledger.LedgerError as error:
        raise SystemExit(f"ERROR: {error}") from error

    resolved_tlc = tlc_report
    if resolved_tlc is None:
        # Conventional per-ticket TLC evidence. When absent the reachable-state
        # figures stay null and are reported as unmeasured -- they are never
        # estimated, and never carried forward from the previous entry.
        for candidate in ("tlc-current.txt", "tlc.txt", "tlc-baseline.txt"):
            probe = input_path.parent / candidate
            if probe.exists():
                resolved_tlc = probe
                break

    metrics = complexity_ledger.collect_metrics(tla_path, cfg_path, manifest_path, resolved_tlc)
    path = complexity_ledger.ledger_path(specs_dir)
    ledger = complexity_ledger.load_ledger(path)
    verdict = complexity_ledger.evaluate(
        scope=scope,
        scope_id=scope_id,
        workflow=workflow,
        metrics=metrics,
        ledger_input=ledger_input,
        previous=complexity_ledger.previous_entry(ledger),
        # AC-04: the architecture-delta report is named relative to the ledger
        # input document, the way every other per-ticket evidence path is.
        input_dir=input_path.parent,
    )
    report = complexity_ledger.render_report(verdict)
    if verdict.rejected:
        # Append the rejection before refusing. The rejected entry is part of the
        # append-only record -- a refused close is evidence, not a non-event --
        # and previous_entry() skips rejections so it never becomes a baseline.
        complexity_ledger.append_entry(path, verdict.entry)
        raise SystemExit(
            report
            + "\nERROR: close refused by the complexity ledger (MF-019 standing objective).\n"
            "Complexity is minimized under behavior retention. There is no override flag."
        )
    print(report)
    complexity_ledger.append_entry(path, verdict.entry)
    record = dict(verdict.entry)
    record["ledger_path"] = rel(path)
    record["input_path"] = rel(input_path)
    return record


def create_ticket_history_entry(
    *,
    repo_root: Path,
    spec_root: Path,
    ticket_ref: str,
    summary: str,
    result_paths: list[Path],
    workflow: str | None = None,
    entry_name: str | None = None,
    allow_open: bool = False,
    ticket_root: Path = Path("tickets"),
    promote_current: bool = True,
    accept_new: bool = False,
    emit_feedback: bool = True,
) -> HistoryEntryResult:
    specs_dir = resolve_spec_root(repo_root, spec_root)
    plan = load_ticket_plan(specs_dir)
    resolved_workflow = workflow_name(plan, workflow)
    index, ticket = find_ticket(plan, ticket_ref)
    resolved_ticket_id = ticket_id(ticket, index)
    status = ticket_status(ticket)
    if not allow_open and status not in TICKET_CLOSED_STATUSES:
        raise SystemExit(f"ERROR: ticket {resolved_ticket_id} is not closed in ticket_plan.yaml: status={status or '(missing)'}")

    # RC-01 (MF-026, owner decision 2026-08-01): a close taken under a
    # guard-weakening flag is a DIFFERENT STATE from one taken under the guard
    # (TlaSpecDevCli.tla CloseTicketWeakened), and until this ticket the record
    # could not tell them apart. `--accept-new` and `--allow-open` exist
    # specifically to bypass the precondition TLC proves over 1,292,951 states;
    # the manifest recorded only `accept_new`, as an unlabeled boolean beside
    # fifty other keys, and nothing named what it meant. Recorded here so the
    # modeled distinction is externally observable in the append-only history --
    # a model may not represent a difference the program does not expose.
    guard_weakening_record = weakening_flags_record(
        accept_new=accept_new, allow_open=allow_open, promote_current=promote_current
    )
    active_dir = active_ticket_dir(specs_dir, resolved_ticket_id, ticket_root)
    accept_new_record: dict[str, Any] | None = None
    if active_dir.exists() and accept_new:
        accept_new_record = accept_new_ticket_current(active_dir)
    ticket_close_errors: list[str] = []
    if active_dir.exists() and not accept_new:
        ticket_close_errors.extend(
            validate_equivalent_model_dirs(
                active_dir / "current",
                active_dir / "desired",
                left_label=f"{active_dir.name}/current",
                right_label=f"{active_dir.name}/desired",
            )
        )
    if ticket_close_errors:
        raise SystemExit(
            "ERROR: cannot close ticket-local workflow:\n"
            + "\n".join(f"- {error}" for error in ticket_close_errors)
            + "\n\n"
            + ticket_promotion_guidance(active_dir)
        )

    # MF-019: the standing objective is a gate, and it runs BEFORE the history
    # entry exists and before promotion, so a refused close mutates nothing.
    # There is deliberately no flag, parameter, or environment variable that
    # skips this. When the ticket workdir is absent the ledger measures the
    # promoted whole-program model instead of skipping -- "no model here" must
    # never be a way to close without a ledger entry.
    _has_workdir = active_dir.exists()
    complexity_record = record_complexity_ledger(
        specs_dir,
        scope="ticket",
        scope_id=resolved_ticket_id,
        workflow=resolved_workflow,
        model_dir=(active_dir / "current") if _has_workdir else (specs_dir / "current"),
        input_path=complexity_ledger_input_path(
            specs_dir, active_dir if _has_workdir else None, "ticket"
        ),
    )

    resolved_entry_name = safe_segment(entry_name) if entry_name else ticket_entry_name(index, ticket)
    make_history_appendable(specs_dir, resolved_workflow)
    entry_dir = history_root(specs_dir, resolved_workflow) / resolved_entry_name
    if entry_dir.exists():
        raise SystemExit(f"ERROR: refusing to overwrite existing history entry: {entry_dir}")
    entry_dir.mkdir(parents=True)

    remove_state_directories(active_dir, *(specs_dir / name for name in MODEL_DIRS))

    ticket_workdir_record: dict[str, Any] | None = None
    promotion_record: dict[str, Any] | None = None
    if active_dir.exists() and promote_current:
        promotion_record = promote_ticket_outputs(active_dir, specs_dir)

    snapshots = snapshot_models(specs_dir, entry_dir)
    results = snapshot_results(specs_dir, entry_dir, result_paths)
    if active_dir.exists():
        ticket_history_dir = entry_dir / "ticket"
        shutil.move(str(active_dir), str(ticket_history_dir))
        ticket_workdir_record = {
            "role": "ticket_workdir",
            "source": rel(active_dir),
            "snapshot": rel(ticket_history_dir),
            "exists": True,
            "moved": True,
        }
        snapshots.append(ticket_workdir_record)
    promoted_paths: list[Path] = []
    if promotion_record is not None:
        promoted_paths = [specs_dir / "current"]
        for name in ("testgraph", "test_graph"):
            if (specs_dir / name).exists():
                promoted_paths.append(specs_dir / name)

    # MF-017: close-out runs the migration.md Phase 6 retro. The template is
    # emitted (once) and this close is appended to it, so the history entry can
    # record whether feedback was filed and where.
    skill_feedback_record: dict[str, Any] | None = None
    if emit_feedback:
        skill_feedback_record = emit_skill_feedback(
            specs_dir,
            scope="ticket",
            scope_id=resolved_ticket_id,
            workflow=resolved_workflow,
            summary=summary,
        )
        promoted_paths.append(Path(skill_feedback_record["path"]))

    # MF-019: the ledger is written by this close, so it belongs in the commit
    # the close recommends. Omitting it leaves the recorded delta uncommitted --
    # an append-only record that is not committed is not a record.
    if complexity_record is not None:
        promoted_paths.append(Path(complexity_record["ledger_path"]))

    close_result = commit_recommendation(
        entry_dir,
        f"record spec history for {resolved_ticket_id}",
        extra_paths=promoted_paths,
    )
    close_result = dataclasses.replace(
        close_result,
        promotion=promotion_record,
        skill_feedback=skill_feedback_record,
        complexity_ledger=complexity_record,
    )
    manifest = {
        "schema_version": 1,
        "kind": "ticket",
        "workflow_name": resolved_workflow,
        "entry_name": resolved_entry_name,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "spec_root": rel(specs_dir),
        "ticket_plan": rel(ticket_plan_path(specs_dir)),
        "ticket_index": index,
        "ticket_id": resolved_ticket_id,
        "ticket_status": status,
        "ticket": ticket,
        "summary": summary,
        "snapshots": snapshots,
        "results": results,
        "active_ticket_dir": rel(active_dir),
        "ticket_workdir": ticket_workdir_record,
        "accept_new": accept_new,
        "accept_new_promotion": accept_new_record,
        # RC-01: which guard-weakening flags this close was taken under, and
        # therefore whether it is a CloseTicket or a CloseTicketWeakened in the
        # model. Never a refusal -- the flags are shipped and have legitimate
        # uses. What changed is that the record now says so.
        "guard_weakening": guard_weakening_record,
        "promotion": promotion_record,
        "skill_feedback": skill_feedback_record,
        "feedback_filed": bool(skill_feedback_record and skill_feedback_record.get("resolved")),
        "feedback_filed_where": (skill_feedback_record or {}).get("filed_where", []),
        # MF-019: the complexity delta and its retention evidence are recorded
        # in the history entry together. Reading either alone is the failure the
        # standing objective forbids, so they are never stored apart.
        "complexity_ledger": complexity_record,
        "complexity_delta": (complexity_record or {}).get("delta"),
        "retention_evidence": (complexity_record or {}).get("retention"),
        "refinement_record": (complexity_record or {}).get("refinement"),
        "commit_recommendation": {
            "message": close_result.recommendation,
            "git_add": close_result.git_add_command,
            "git_commit": close_result.git_commit_command,
        },
        "history_policy": "append-only by convention; existing entries are not overwritten and filesystem permissions remain git-friendly",
        "git": git_metadata(),
    }
    write_manifest(entry_dir, manifest)
    write_summary(entry_dir, title=f"Ticket snapshot: {resolved_ticket_id}", summary=summary, manifest=manifest)
    return close_result


def create_workflow_closed_snapshot(
    *,
    repo_root: Path,
    spec_root: Path,
    summary: str,
    result_paths: list[Path],
    workflow: str | None = None,
    entry_name: str = "closed-snapshot",
    allow_open: bool = False,
    emit_feedback: bool = True,
) -> HistoryEntryResult:
    specs_dir = resolve_spec_root(repo_root, spec_root)
    plan = load_ticket_plan(specs_dir)
    resolved_workflow = workflow_name(plan, workflow)
    tickets = plan["tickets"]
    if not allow_open:
        open_tickets = [
            f"{ticket_id(ticket, index)}: {ticket_status(ticket) or '(missing)'}"
            for index, ticket in enumerate(tickets)
            if isinstance(ticket, dict) and ticket_status(ticket) not in TICKET_CLOSED_STATUSES
        ]
        if open_tickets:
            raise SystemExit("ERROR: cannot write closed workflow snapshot with open tickets:\n" + "\n".join(f"- {item}" for item in open_tickets))

    # MF-019: workflow close records a ledger entry too, measured against the
    # promoted whole-program model. Same gate, same refusal, evaluated before
    # the snapshot exists.
    complexity_record = record_complexity_ledger(
            specs_dir,
            scope="workflow",
            scope_id=resolved_workflow,
            workflow=resolved_workflow,
        model_dir=specs_dir / "current",
        input_path=complexity_ledger_input_path(specs_dir, None, "workflow"),
    )

    resolved_entry_name = safe_segment(entry_name)
    make_history_appendable(specs_dir, resolved_workflow)
    entry_dir = history_root(specs_dir, resolved_workflow) / resolved_entry_name
    if entry_dir.exists():
        raise SystemExit(f"ERROR: refusing to overwrite existing history entry: {entry_dir}")
    entry_dir.mkdir(parents=True)

    remove_state_directories(*(specs_dir / name for name in MODEL_DIRS))

    snapshots = snapshot_models(specs_dir, entry_dir)
    results = snapshot_results(specs_dir, entry_dir, result_paths)

    # MF-017: the workflow close is the last chance to run the Phase 6 retro,
    # so it emits/appends the same feedback document as ticket close.
    skill_feedback_record: dict[str, Any] | None = None
    extra_paths: list[Path] = []
    if emit_feedback:
        skill_feedback_record = emit_skill_feedback(
            specs_dir,
            scope="workflow",
            scope_id=resolved_workflow,
            workflow=resolved_workflow,
            summary=summary,
        )
        extra_paths.append(Path(skill_feedback_record["path"]))

    if complexity_record is not None:
        extra_paths.append(Path(complexity_record["ledger_path"]))
    close_result = commit_recommendation(entry_dir, "close spec ticket workflow", extra_paths=extra_paths)
    close_result = dataclasses.replace(
        close_result,
        skill_feedback=skill_feedback_record,
        complexity_ledger=complexity_record,
    )
    manifest = {
        "schema_version": 1,
        "kind": "workflow-close",
        "workflow_name": resolved_workflow,
        "entry_name": resolved_entry_name,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "spec_root": rel(specs_dir),
        "ticket_plan": rel(ticket_plan_path(specs_dir)),
        "tickets": tickets,
        "summary": summary,
        "snapshots": snapshots,
        "results": results,
        "complexity_ledger": complexity_record,
        "complexity_delta": (complexity_record or {}).get("delta"),
        "retention_evidence": (complexity_record or {}).get("retention"),
        "refinement_record": (complexity_record or {}).get("refinement"),
        "skill_feedback": skill_feedback_record,
        "feedback_filed": bool(skill_feedback_record and skill_feedback_record.get("resolved")),
        "feedback_filed_where": (skill_feedback_record or {}).get("filed_where", []),
        "commit_recommendation": {
            "message": close_result.recommendation,
            "git_add": close_result.git_add_command,
            "git_commit": close_result.git_commit_command,
        },
        "history_policy": "append-only by convention; existing entries are not overwritten and filesystem permissions remain git-friendly",
        "git": git_metadata(),
    }
    write_manifest(entry_dir, manifest)
    write_summary(entry_dir, title="Closed workflow snapshot", summary=summary, manifest=manifest)
    return close_result


def print_promotion_report(result: HistoryEntryResult) -> None:
    """Enumerate every path promotion removed or preserved. Never stay silent."""
    promotion = result.promotion
    if not promotion:
        return
    for record in promotion.get("merged", []):
        if record.get("role") != "current":
            continue
        removed = record.get("removed") or []
        preserved = record.get("preserved") or []
        print(f"promotion -> {record.get('destination')}")
        print(f"  basis: {record.get('seed_basis')}")
        if removed:
            print(f"  removed {len(removed)} path(s) this ticket dropped from its seeded workspace:")
            for relative in removed:
                print(f"    - {relative}")
        else:
            print("  removed 0 paths")
        if preserved:
            print(f"  preserved {len(preserved)} current-only path(s) the ticket never carried:")
            for relative in preserved:
                print(f"    = {relative}")


def print_complexity_ledger_report(record: dict[str, Any] | None) -> None:
    """Restate the recorded ledger location after a successful close.

    The full delta/retention report is printed by record_complexity_ledger at
    gate time, before anything is mutated. This is the pointer to the durable
    entry, printed alongside the other close-out records.
    """
    if not record:
        return
    delta = record.get("delta") or {}
    print(
        f"complexity ledger: {record.get('ledger_path')} "
        f"(delta {delta.get('direction')} vs {delta.get('previous_scope_id') or 'baseline'}, "
        f"refinement {(record.get('refinement') or {}).get('outcome')})"
    )


def print_commit_recommendation(result: HistoryEntryResult) -> None:
    print_promotion_report(result)
    print_complexity_ledger_report(result.complexity_ledger)
    print_skill_feedback_report(result.skill_feedback)
    print(f"recorded spec history entry: {result.entry_dir}")
    print(result.recommendation)
    print("recommended next step:")
    print(f"  {result.git_add_command}")
    print(f"  {result.git_commit_command}")
