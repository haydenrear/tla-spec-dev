"""Immutable spec-workflow history helpers."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
MODEL_DIRS = ("program_model", "desired_program_model", "current")
IGNORED_COPY_NAMES = {".DS_Store", "__pycache__", ".history", ".tla-spec-evolution"}
TICKET_CLOSED_STATUSES = {"accepted", "closed", "complete", "completed", "done"}


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
            "Review this immutable entry, then commit the history directory with the related spec changes.\n",
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
) -> Path:
    specs_dir = resolve_spec_root(repo_root, spec_root)
    plan = load_ticket_plan(specs_dir)
    resolved_workflow = workflow_name(plan, workflow)
    index, ticket = find_ticket(plan, ticket_ref)
    status = ticket_status(ticket)
    if not allow_open and status not in TICKET_CLOSED_STATUSES:
        raise SystemExit(f"ERROR: ticket {ticket_id(ticket, index)} is not closed in ticket_plan.yaml: status={status or '(missing)'}")

    resolved_entry_name = safe_segment(entry_name) if entry_name else ticket_entry_name(index, ticket)
    entry_dir = history_root(specs_dir, resolved_workflow) / resolved_entry_name
    if entry_dir.exists():
        raise SystemExit(f"ERROR: refusing to overwrite immutable history entry: {entry_dir}")
    entry_dir.mkdir(parents=True)

    snapshots = snapshot_models(specs_dir, entry_dir)
    results = snapshot_results(specs_dir, entry_dir, result_paths)
    manifest = {
        "schema_version": 1,
        "kind": "ticket",
        "workflow_name": resolved_workflow,
        "entry_name": resolved_entry_name,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "spec_root": rel(specs_dir),
        "ticket_plan": rel(ticket_plan_path(specs_dir)),
        "ticket_index": index,
        "ticket_id": ticket_id(ticket, index),
        "ticket_status": status,
        "ticket": ticket,
        "summary": summary,
        "snapshots": snapshots,
        "results": results,
        "git": git_metadata(),
    }
    write_manifest(entry_dir, manifest)
    write_summary(entry_dir, title=f"Ticket snapshot: {ticket_id(ticket, index)}", summary=summary, manifest=manifest)
    return entry_dir


def create_workflow_closed_snapshot(
    *,
    repo_root: Path,
    spec_root: Path,
    summary: str,
    result_paths: list[Path],
    workflow: str | None = None,
    entry_name: str = "closed-snapshot",
    allow_open: bool = False,
) -> Path:
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
    entry_dir = history_root(specs_dir, resolved_workflow) / resolved_entry_name
    if entry_dir.exists():
        raise SystemExit(f"ERROR: refusing to overwrite immutable history entry: {entry_dir}")
    entry_dir.mkdir(parents=True)

    snapshots = snapshot_models(specs_dir, entry_dir)
    results = snapshot_results(specs_dir, entry_dir, result_paths)
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
        "git": git_metadata(),
    }
    write_manifest(entry_dir, manifest)
    write_summary(entry_dir, title="Closed workflow snapshot", summary=summary, manifest=manifest)
    return entry_dir


def print_commit_recommendation(entry_dir: Path, message: str) -> None:
    print(f"recorded immutable spec history entry: {entry_dir}")
    print("recommended next step:")
    print(f"  git add {rel(entry_dir)}")
    print(f"  git commit -m {message!r}")
