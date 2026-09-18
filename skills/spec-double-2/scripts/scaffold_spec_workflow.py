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
    history = specs_dir / ".history"
    results = specs_dir / "results"

    # SF-304: every project this skill scaffolds inherits comment-heavy
    # manifests, and a repository that cites LINE NUMBERS in durable comments
    # will always drift -- three consecutive tickets were charged with "shipping
    # a stale citation" before anything checked. The convention ships with the
    # scaffold so a new project starts on the side that does not rot.
    # The example below deliberately carries NO literal file-and-line pair. The
    # first version of this text spelled one out to show what not to write, and
    # this repository's own citation check resolved it, found no anchor, and went
    # red: a convention against line citations that contained a line citation.
    # Same shape as SF-305, where a narrative quoting the ledger's own template
    # sentinel was silently eaten by the ledger.
    citation_convention = (
        "\n## Citing source in this tree\n\n"
        "Cite SYMBOLS, not line numbers: write `scripts/foo.py::bar` rather than\n"
        "that same path followed by a colon and a bare line number. Line citations\n"
        "in durable comments drift silently as soon as anything above them moves,\n"
        "and nothing goes red when they do. Where one is unavoidable, anchor it to\n"
        "a token quoted from that line so a checker can find it again.\n"
    )
    write_if_missing(
        desired / "README.md",
        "# Desired Program Model\n\nDescribe the intended whole-program end state here.\n"
        + citation_convention,
    )
    write_if_missing(
        current / "README.md",
        "# Current Program Model\n\nDescribe the implemented slice and active adapters here.\n"
        + citation_convention,
    )
    write_if_missing(
        history / "README.md",
        "# Spec Workflow History\n\nThis directory is append-only history. Do not edit existing close entries.\n",
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
