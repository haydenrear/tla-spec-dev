"""Path helpers for spec-relative scripts."""

from __future__ import annotations

from pathlib import Path


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def resolve_existing_from_cwd(path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (Path.cwd() / path).resolve()


def resolve_spec_dir(tla_path: Path) -> Path:
    resolved = resolve_existing_from_cwd(tla_path)
    if not resolved.exists():
        raise SystemExit(f"ERROR: spec not found: {resolved}")
    return resolved.parent.resolve()


def resolve_existing_spec_input(path: Path, spec_dir: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    cwd_candidate = (Path.cwd() / path).resolve()
    if cwd_candidate.exists():
        return cwd_candidate
    spec_candidate = (spec_dir / path).resolve()
    if spec_candidate.exists():
        return spec_candidate
    return cwd_candidate


def resolve_spec_relative_path(path: Path, spec_dir: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    spec_dir = spec_dir.resolve()
    cwd_candidate = (Path.cwd() / path).resolve()
    if is_relative_to(cwd_candidate, spec_dir):
        return cwd_candidate
    return (spec_dir / path).resolve()
