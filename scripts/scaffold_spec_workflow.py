#!/usr/bin/env python3
"""Scaffold desired/current spec workflow directories."""

from __future__ import annotations

import argparse
from pathlib import Path


def write_if_missing(path: Path, content: str) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def scaffold(root: Path, specs_dir_name: str) -> Path:
    root = root.resolve()
    specs_dir = root / specs_dir_name
    desired = specs_dir / "desired_program_model"
    current = specs_dir / "current"
    history = specs_dir / ".tla-spec-evolution"
    results = specs_dir / "results"

    write_if_missing(
        desired / "README.md",
        "# Desired Program Model\n\nDescribe the intended whole-program end state here.\n",
    )
    write_if_missing(
        current / "README.md",
        "# Current Program Model\n\nDescribe the implemented slice and active adapters here.\n",
    )
    write_if_missing(
        history / "README.md",
        "# TLA Spec Evolution\n\nThis directory is append-only history. Do not edit existing close entries.\n",
    )
    write_if_missing(results / ".gitkeep", "")
    return specs_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold desired/current spec workflow directories.")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--specs-dir", default="specs")
    args = parser.parse_args()
    specs_dir = scaffold(args.root, args.specs_dir)
    print(f"scaffolded spec workflow at {specs_dir}")
    print("next: add the program spec, update desired/current, then close tickets with scripts/close-ticket.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
