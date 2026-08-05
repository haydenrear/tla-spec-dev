#!/usr/bin/env python3
"""The mechanical block: measured over both arms' trees, RECORDED AND NEVER SCORED.

`references/eval_scorecard.md` rule 7: the mechanical block "sits beside the
judgement so a reader can see when the two disagree -- and a disagreement is a
finding." The owner amendment at schedule_revision 2 makes this explicit for
GOAL-simpler-same-behavior: `analyze complexity` reads TLA+ and both arms
produce Python, so the mechanical half of that goal's harness is a size / state /
branch capture over the two produced trees.

Nothing here is a threshold and nothing here refuses. Every figure is a count a
reader can re-derive from the tree with the standard library.

WHAT EACH FIGURE IS, stated because a count nobody can interpret is worse than
no count:

  modules              importable .py files, tests excluded
  production_lines     non-blank, non-comment lines outside tests
  test_lines           the same, for the arm's OWN tests (the shared suite is
                       identical across arms and is therefore not counted)
  public_names         module-level and class-level names not starting with "_"
  mutable_state        assignments to `self.<name>` anywhere in the tree --
                       the pieces of state an instance carries and something
                       writes. A DERIVED value is not counted, which is the
                       whole point of measuring it.
  state_writers        (attribute -> number of distinct methods that assign it).
                       "State written from everywhere" is the shape arm B's
                       prompt names; this is the number behind it.
  branches             if / elif / for / while / and / or / ternary / except /
                       comprehension-if -- the decision points.
  imports              distinct imported top-level modules, tests excluded
  io_imports           of those, the ones that touch the outside world
"""

from __future__ import annotations

import argparse
import ast
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

IO_MODULES = {"os", "io", "pathlib", "socket", "subprocess", "time", "datetime",
              "random", "shutil", "tempfile", "sys"}


def _python_files(root: Path, *, tests: bool) -> list[Path]:
    found = []
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        is_test = "tests" in path.parts or path.name.startswith("test_") or path.name == "conftest.py"
        if is_test == tests:
            found.append(path)
    return found


def _significant_lines(path: Path) -> int:
    count = 0
    in_doc = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if in_doc:
            if line.endswith('"""') or line.endswith("'''"):
                in_doc = False
            continue
        if line.startswith('"""') or line.startswith("'''"):
            if not (len(line) > 3 and (line.endswith('"""') or line.endswith("'''"))):
                in_doc = True
            continue
        if line.startswith("#"):
            continue
        count += 1
    return count


BRANCH_NODES = (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.IfExp, ast.BoolOp)


def _measure(files: list[Path], root: Path) -> dict[str, Any]:
    public: list[str] = []
    branches = 0
    imports: set[str] = set()
    writers: dict[str, set[str]] = defaultdict(set)
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        relative = path.relative_to(root).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, BRANCH_NODES):
                branches += 1
            elif isinstance(node, ast.comprehension):
                branches += len(node.ifs)
            elif isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                imports.add(node.module.split(".")[0])
        for node in tree.body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and not node.name.startswith("_"):
                public.append(f"{relative}:{node.name}")
                if isinstance(node, ast.ClassDef):
                    public.extend(
                        f"{relative}:{node.name}.{item.name}"
                        for item in node.body
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and not item.name.startswith("_")
                    )
            elif isinstance(node, ast.Assign):
                public.extend(
                    f"{relative}:{target.id}" for target in node.targets
                    if isinstance(target, ast.Name) and not target.id.startswith("_")
                )
        for function in [n for n in ast.walk(tree)
                         if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            for node in ast.walk(function):
                targets: list[ast.expr] = []
                if isinstance(node, ast.Assign):
                    targets = list(node.targets)
                elif isinstance(node, (ast.AugAssign, ast.AnnAssign)):
                    targets = [node.target]
                for target in targets:
                    if (isinstance(target, ast.Attribute)
                            and isinstance(target.value, ast.Name)
                            and target.value.id == "self"):
                        writers[target.attr].add(f"{relative}:{function.name}")
    return {
        "public_names": sorted(public),
        "branches": branches,
        "imports": sorted(imports),
        "io_imports": sorted(imports & IO_MODULES),
        "mutable_state": sorted(writers),
        "state_writers": {name: sorted(where) for name, where in sorted(writers.items())},
    }


def measure_arm(root: Path) -> dict[str, Any]:
    production = _python_files(root, tests=False)
    tests = _python_files(root, tests=True)
    block = _measure(production, root)
    return {
        "root": str(root),
        "modules": [path.relative_to(root).as_posix() for path in production],
        "module_count": len(production),
        "production_lines": sum(_significant_lines(path) for path in production),
        "test_files": [path.relative_to(root).as_posix() for path in tests],
        "test_lines": sum(_significant_lines(path) for path in tests),
        "public_name_count": len(block["public_names"]),
        "mutable_state_count": len(block["mutable_state"]),
        "max_writers_of_one_attribute": max(
            (len(where) for where in block["state_writers"].values()), default=0
        ),
        **block,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", action="append", default=[], metavar="NAME=ROOT")
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()

    report = {"note": "RECORDED, NEVER SCORED (eval_scorecard.md rule 7).", "arms": {}}
    for entry in arguments.arm:
        name, _, root = entry.partition("=")
        report["arms"][name] = measure_arm(Path(root).resolve())
    arguments.out.parent.mkdir(parents=True, exist_ok=True)
    arguments.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
