#!/usr/bin/env python3
"""Transitive import closure of the shipped CLI entrypoint.

RC-01's G-6 finding was that `scripts/generate_cases_from_tlc_dump.py` was
reachable only by running the file directly, so "an import-closure walk of
build_parser never saw it". This script performs that walk mechanically, over
`scripts/tla_spec_dev.py`, following both top-level and function-local imports
(the CLI imports lazily inside each handler, so a top-level-only walk finds
almost nothing).

Usage: python3 cli_closure.py <repo_root>
Writes: cli-closure-reachable.txt, cli-closure-unreachable.txt
"""
import ast
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
SCRIPTS = ROOT / "scripts"


def module_imports(path: Path) -> set[str]:
    """Every `scripts.X` / bare `X` import anywhere in the file, incl. nested."""
    names: set[str] = set()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[-1])
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod in {"scripts", ""}:
                for alias in node.names:
                    names.add(alias.name)
            else:
                names.add(mod.split(".")[-1])
    return {n for n in names if (SCRIPTS / f"{n}.py").is_file()}


def main() -> int:
    out = Path(__file__).parent
    seen: set[str] = set()
    stack = ["tla_spec_dev"]
    while stack:
        mod = stack.pop()
        if mod in seen:
            continue
        seen.add(mod)
        stack.extend(module_imports(SCRIPTS / f"{mod}.py"))

    all_scripts = {p.stem for p in sorted(SCRIPTS.glob("*.py"))}
    reachable = sorted(seen)
    unreachable = sorted(all_scripts - seen)
    (out / "cli-closure-reachable.txt").write_text("\n".join(reachable) + "\n")
    (out / "cli-closure-unreachable.txt").write_text("\n".join(unreachable) + "\n")
    print(f"scripts total\t{len(all_scripts)}")
    print(f"reachable\t{len(reachable)}")
    print(f"unreachable\t{len(unreachable)}")
    print("\nUNREACHABLE FROM `tla-spec-dev`:")
    for m in unreachable:
        print(f"  scripts/{m}.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
