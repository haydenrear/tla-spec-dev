"""Immutable spec-evolution history helpers."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SNAPSHOT_SUFFIXES = {".tla", ".cfg", ".yaml", ".yml", ".toml", ".md"}
IGNORED_COPY_NAMES = {".DS_Store", "__pycache__", ".tla-spec-evolution"}


def utc_close_id(prefix: str, subject: str | None = None) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    parts = [prefix]
    if subject:
        parts.append(safe_segment(subject))
    parts.append(stamp)
    return "-".join(parts)


def safe_segment(value: str) -> str:
    rendered = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    rendered = rendered.strip(".-")
    if not rendered:
        raise SystemExit("ERROR: close ids and ticket ids must contain at least one safe character")
    return rendered


def resolve_workflow_path(path: Path, specs_dir: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    cwd_candidate = (Path.cwd() / path).resolve()
    if cwd_candidate.exists() or (path.parts and path.parts[0] == specs_dir.name):
        return cwd_candidate
    return (specs_dir / path).resolve()


def copy_ignore(_directory: str, names: list[str]) -> set[str]:
    return {name for name in names if name in IGNORED_COPY_NAMES}


def copy_snapshot(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, destination, ignore=copy_ignore)
    else:
        shutil.copy2(source, destination)


def unique_child(parent: Path, name: str) -> Path:
    candidate = parent / name
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    index = 2
    while True:
        next_candidate = parent / f"{stem}-{index}{suffix}"
        if not next_candidate.exists():
            return next_candidate
        index += 1


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


def default_spec_paths(specs_dir: Path) -> list[Path]:
    if not specs_dir.exists():
        return []
    paths: list[Path] = []
    for path in sorted(specs_dir.iterdir()):
        if path.name in {"desired_program_model", "current", ".tla-spec-evolution"}:
            continue
        if path.is_file() and path.suffix in SNAPSHOT_SUFFIXES:
            paths.append(path)
    return paths


def find_ticket_files(ticket_ids: list[str], tickets_dir: Path, explicit_files: list[Path], specs_dir: Path) -> tuple[list[Path], list[str]]:
    found: list[Path] = []
    missing: list[str] = []
    for file_path in explicit_files:
        resolved = resolve_workflow_path(file_path, specs_dir)
        if resolved.exists():
            found.append(resolved)
        else:
            missing.append(str(file_path))
    resolved_tickets_dir = tickets_dir if tickets_dir.is_absolute() else (Path.cwd() / tickets_dir)
    for ticket_id in ticket_ids:
        matches = sorted(resolved_tickets_dir.glob(f"{ticket_id}*.md")) if resolved_tickets_dir.exists() else []
        if matches:
            found.extend(path.resolve() for path in matches)
        else:
            missing.append(ticket_id)
    deduped: list[Path] = []
    seen: set[Path] = set()
    for path in found:
        resolved = path.resolve()
        if resolved not in seen:
            seen.add(resolved)
            deduped.append(resolved)
    return deduped, missing


def add_copied_path(records: list[dict[str, Any]], *, role: str, source: Path, destination_root: Path) -> None:
    source = source.resolve()
    record: dict[str, Any] = {"role": role, "source": rel(source), "exists": source.exists()}
    if source.exists():
        destination = unique_child(destination_root, source.name)
        copy_snapshot(source, destination)
        record["snapshot"] = rel(destination)
    records.append(record)


def write_summary(entry_dir: Path, *, title: str, close_id: str, summary: str, tickets: list[str], results: list[dict[str, Any]]) -> None:
    lines = [
        f"# {title}\n\n",
        f"- Close id: `{close_id}`\n",
    ]
    if tickets:
        lines.append(f"- Tickets: {', '.join(f'`{ticket}`' for ticket in tickets)}\n")
    lines.append("\n")
    lines.append("## Summary\n\n")
    lines.append(summary.strip() or "No summary supplied.")
    lines.append("\n\n")
    lines.append("## Evidence\n\n")
    if results:
        for result in results:
            lines.append(f"- `{result['source']}` -> `{result.get('snapshot', 'missing')}`\n")
    else:
        lines.append("- No result paths supplied.\n")
    lines.append("\n")
    lines.append("## Follow-up\n\n")
    lines.append("Review this immutable entry, then commit the spec, tickets, and evolution history together.\n")
    (entry_dir / "summary.md").write_text("".join(lines))


def create_evolution_entry(
    *,
    kind: str,
    specs_dir: Path,
    close_id: str | None,
    tickets: list[str],
    summary: str,
    result_paths: list[Path],
    spec_paths: list[Path],
    ticket_files: list[Path],
    tickets_dir: Path,
    desired_path: Path,
    current_path: Path,
    remove_active: bool = False,
) -> Path:
    specs_dir = specs_dir.resolve()
    history_root = specs_dir / ".tla-spec-evolution"
    if kind == "ticket":
        if len(tickets) != 1:
            raise SystemExit("ERROR: ticket close history requires exactly one ticket id")
        ticket_id = safe_segment(tickets[0])
        resolved_close_id = close_id or utc_close_id("ticket", ticket_id)
        entry_dir = history_root / "tickets" / ticket_id / safe_segment(resolved_close_id)
        title = f"Ticket close: {ticket_id}"
    elif kind == "workflow":
        resolved_close_id = close_id or utc_close_id("workflow")
        entry_dir = history_root / "workflows" / safe_segment(resolved_close_id)
        title = "Spec workflow close"
    else:
        raise SystemExit(f"ERROR: unsupported evolution entry kind: {kind}")

    if entry_dir.exists():
        raise SystemExit(f"ERROR: refusing to overwrite immutable evolution entry: {entry_dir}")
    entry_dir.mkdir(parents=True)

    desired = resolve_workflow_path(desired_path, specs_dir)
    current = resolve_workflow_path(current_path, specs_dir)
    resolved_spec_paths = [resolve_workflow_path(path, specs_dir) for path in spec_paths] if spec_paths else default_spec_paths(specs_dir)
    resolved_results = [resolve_workflow_path(path, specs_dir) for path in result_paths]
    resolved_ticket_files, missing_ticket_files = find_ticket_files(tickets, tickets_dir, ticket_files, specs_dir)

    snapshots: list[dict[str, Any]] = []
    add_copied_path(snapshots, role="desired_program_model", source=desired, destination_root=entry_dir / "snapshots")
    add_copied_path(snapshots, role="current", source=current, destination_root=entry_dir / "snapshots")
    for path in resolved_spec_paths:
        add_copied_path(snapshots, role="spec", source=path, destination_root=entry_dir / "snapshots" / "spec")

    results: list[dict[str, Any]] = []
    for path in resolved_results:
        add_copied_path(results, role="result", source=path, destination_root=entry_dir / "results")

    copied_ticket_files: list[dict[str, Any]] = []
    for path in resolved_ticket_files:
        add_copied_path(copied_ticket_files, role="ticket", source=path, destination_root=entry_dir / "tickets")

    removed_active_paths: list[str] = []
    if remove_active:
        for path in [desired, current]:
            if path.exists():
                removed_active_paths.append(rel(path))
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()

    manifest = {
        "schema_version": 1,
        "kind": kind,
        "close_id": resolved_close_id,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "specs_dir": rel(specs_dir),
        "history_root": rel(history_root),
        "tickets": tickets,
        "summary": summary,
        "snapshots": snapshots,
        "results": results,
        "ticket_files": copied_ticket_files,
        "missing_ticket_files": missing_ticket_files,
        "remove_active": remove_active,
        "removed_active_paths": removed_active_paths,
        "git": git_metadata(),
    }
    (entry_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    write_summary(entry_dir, title=title, close_id=resolved_close_id, summary=summary, tickets=tickets, results=results)
    return entry_dir


def print_commit_recommendation(entry_dir: Path, message: str) -> None:
    print(f"recorded immutable spec evolution entry: {entry_dir}")
    print("recommended next step:")
    print(f"  git add {rel(entry_dir)} specs tickets")
    print(f"  git commit -m {message!r}")
