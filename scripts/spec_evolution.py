"""Append-only spec-workflow history helpers."""

from __future__ import annotations

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


def promote_ticket_outputs(active_dir: Path, specs_dir: Path) -> dict[str, Any]:
    merged = [
        {
            "role": "current",
            "source": rel(active_dir / "desired"),
            "destination": rel(specs_dir / "current"),
            "operation": "replace",
            "files": replace_tree(active_dir / "desired", specs_dir / "current"),
        }
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
) -> HistoryEntryResult:
    specs_dir = resolve_spec_root(repo_root, spec_root)
    plan = load_ticket_plan(specs_dir)
    resolved_workflow = workflow_name(plan, workflow)
    index, ticket = find_ticket(plan, ticket_ref)
    resolved_ticket_id = ticket_id(ticket, index)
    status = ticket_status(ticket)
    if not allow_open and status not in TICKET_CLOSED_STATUSES:
        raise SystemExit(f"ERROR: ticket {resolved_ticket_id} is not closed in ticket_plan.yaml: status={status or '(missing)'}")

    active_dir = active_ticket_dir(specs_dir, resolved_ticket_id, ticket_root)
    ticket_close_errors: list[str] = []
    if active_dir.exists():
        ticket_close_errors.extend(
            validate_equivalent_model_dirs(
                active_dir / "current",
                active_dir / "desired",
                left_label=f"{active_dir.name}/current",
                right_label=f"{active_dir.name}/desired",
            )
        )
    if ticket_close_errors:
        raise SystemExit("ERROR: cannot close ticket-local workflow:\n" + "\n".join(f"- {error}" for error in ticket_close_errors))

    resolved_entry_name = safe_segment(entry_name) if entry_name else ticket_entry_name(index, ticket)
    make_history_appendable(specs_dir, resolved_workflow)
    entry_dir = history_root(specs_dir, resolved_workflow) / resolved_entry_name
    if entry_dir.exists():
        raise SystemExit(f"ERROR: refusing to overwrite existing history entry: {entry_dir}")
    entry_dir.mkdir(parents=True)

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
    close_result = commit_recommendation(
        entry_dir,
        f"record spec history for {resolved_ticket_id}",
        extra_paths=promoted_paths,
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
        "promotion": promotion_record,
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

    resolved_entry_name = safe_segment(entry_name)
    make_history_appendable(specs_dir, resolved_workflow)
    entry_dir = history_root(specs_dir, resolved_workflow) / resolved_entry_name
    if entry_dir.exists():
        raise SystemExit(f"ERROR: refusing to overwrite existing history entry: {entry_dir}")
    entry_dir.mkdir(parents=True)

    snapshots = snapshot_models(specs_dir, entry_dir)
    results = snapshot_results(specs_dir, entry_dir, result_paths)
    close_result = commit_recommendation(entry_dir, "close spec ticket workflow")
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


def print_commit_recommendation(result: HistoryEntryResult) -> None:
    print(f"recorded spec history entry: {result.entry_dir}")
    print(result.recommendation)
    print("recommended next step:")
    print(f"  {result.git_add_command}")
    print(f"  {result.git_commit_command}")
