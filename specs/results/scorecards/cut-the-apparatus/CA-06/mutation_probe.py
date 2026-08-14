#!/usr/bin/env python3
"""CA-06 cost/catch probe on a real subject: examples/distributed_history.

MF-020 COMPLIANCE, stated before the code so it can be checked against it:
the mutant population is ENUMERATED from a fixed grammar over every eligible
AST site in the subject's domain module. No mutant is chosen, named, skipped
or ordered by the author, and no mutant was written after looking at what any
instrument catches. The grammar is fixed below and applied exhaustively.

Two instruments are compared on the SAME population:

  suite      the subject's hand-written test  (tests/test_ecommerce_backend.py)
  corpus     the TLC-derived case corpus run through the adapter path
             (scripts/run_generated_case_adapters.py)

A mutant is KILLED by an instrument when that instrument exits non-zero on the
mutated tree while exiting zero on the pristine tree.
"""

from __future__ import annotations

import ast
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

SCRATCH = Path(__file__).resolve().parent
TREE = SCRATCH / "dh"
TARGET_REL = "ecommerce_backend/domain.py"
CORPUS = SCRATCH / "dh/specs/probegen/spec-unit/ecommerce_internal_cases"
WORKTREE = Path(os.environ["CA06_WORKTREE"])

CMP_SWAP = {
    ast.Eq: ast.NotEq, ast.NotEq: ast.Eq,
    ast.Lt: ast.LtE, ast.LtE: ast.Lt,
    ast.Gt: ast.GtE, ast.GtE: ast.Gt,
    ast.In: ast.NotIn, ast.NotIn: ast.In,
    ast.Is: ast.IsNot, ast.IsNot: ast.Is,
}


def enumerate_mutants(source: str) -> list[tuple[str, str]]:
    """Every site of the fixed grammar, in source order. Returns (id, code)."""
    tree = ast.parse(source)
    str_pool = sorted({
        n.value for n in ast.walk(tree)
        if isinstance(n, ast.Constant) and isinstance(n.value, str)
    })
    sites: list[tuple[str, callable]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and len(node.ops) == 1:
            op = type(node.ops[0])
            if op in CMP_SWAP:
                sites.append((f"CMP:{node.lineno}:{node.col_offset}:{op.__name__}",
                              ("cmp", node.lineno, node.col_offset)))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            sites.append((f"NOT:{node.lineno}:{node.col_offset}",
                          ("not", node.lineno, node.col_offset)))
        elif isinstance(node, ast.BoolOp):
            sites.append((f"BOOL:{node.lineno}:{node.col_offset}",
                          ("bool", node.lineno, node.col_offset)))
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                sites.append((f"BOOLC:{node.lineno}:{node.col_offset}",
                              ("boolc", node.lineno, node.col_offset)))
            elif isinstance(node.value, int):
                sites.append((f"INT:{node.lineno}:{node.col_offset}:{node.value}",
                              ("int", node.lineno, node.col_offset)))
            elif isinstance(node.value, str) and len(str_pool) > 1:
                sites.append((f"STR:{node.lineno}:{node.col_offset}",
                              ("str", node.lineno, node.col_offset)))

    sites.sort(key=lambda s: (s[1][1], s[1][2], s[0]))
    out: list[tuple[str, str]] = []
    for mid, (kind, lineno, col) in sites:
        mutated = _apply(source, kind, lineno, col, str_pool)
        if mutated is not None and mutated != source:
            out.append((mid, mutated))
    return out


class _Mutator(ast.NodeTransformer):
    def __init__(self, kind, lineno, col, str_pool):
        self.kind, self.lineno, self.col, self.str_pool = kind, lineno, col, str_pool
        self.hit = False

    def _at(self, node):
        return getattr(node, "lineno", None) == self.lineno and \
               getattr(node, "col_offset", None) == self.col

    def visit_Compare(self, node):
        self.generic_visit(node)
        if self.kind == "cmp" and self._at(node) and len(node.ops) == 1:
            op = type(node.ops[0])
            if op in CMP_SWAP:
                node.ops = [CMP_SWAP[op]()]
                self.hit = True
        return node

    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        if self.kind == "not" and self._at(node) and isinstance(node.op, ast.Not):
            self.hit = True
            return node.operand
        return node

    def visit_BoolOp(self, node):
        self.generic_visit(node)
        if self.kind == "bool" and self._at(node):
            node.op = ast.Or() if isinstance(node.op, ast.And) else ast.And()
            self.hit = True
        return node

    def visit_Constant(self, node):
        if not self._at(node):
            return node
        v = node.value
        if self.kind == "boolc" and isinstance(v, bool):
            self.hit = True
            return ast.Constant(value=not v)
        if self.kind == "int" and isinstance(v, int) and not isinstance(v, bool):
            self.hit = True
            return ast.Constant(value=v + 1)
        if self.kind == "str" and isinstance(v, str):
            pool = self.str_pool
            nxt = pool[(pool.index(v) + 1) % len(pool)]
            if nxt != v:
                self.hit = True
                return ast.Constant(value=nxt)
        return node


def _apply(source, kind, lineno, col, str_pool):
    tree = ast.parse(source)
    m = _Mutator(kind, lineno, col, str_pool)
    new = m.visit(tree)
    if not m.hit:
        return None
    ast.fix_missing_locations(new)
    try:
        return ast.unparse(new)
    except Exception:
        return None


def run_suite() -> int:
    r = subprocess.run(
        ["uv", "run", "--with", "pytest", "-m", "pytest", "tests/test_ecommerce_backend.py", "-q"],
        cwd=TREE, capture_output=True, text=True, timeout=300,
    )
    return r.returncode


def run_corpus() -> int:
    r = subprocess.run(
        [sys.executable, str(WORKTREE / "scripts/run_generated_case_adapters.py"),
         str(CORPUS), "--mapping", "specs/program_model/case_adapters.toml",
         "--view", "internal", "--batch", "--import-root", "."],
        cwd=TREE, capture_output=True, text=True, timeout=600,
    )
    return r.returncode


def main() -> int:
    target = TREE / TARGET_REL
    pristine = target.read_text()
    # A mechanical grammar applied to the source AS UNPARSED, so that a
    # mutant differs from its own baseline only by the mutation. The baseline
    # for every run below is therefore the unparsed pristine source.
    baseline_src = ast.unparse(ast.parse(pristine))

    target.write_text(baseline_src)
    t0 = time.time()
    base_suite = run_suite()
    base_suite_s = time.time() - t0
    t0 = time.time()
    base_corpus = run_corpus()
    base_corpus_s = time.time() - t0
    print(f"pristine (unparsed): suite={base_suite} ({base_suite_s:.1f}s) "
          f"corpus={base_corpus} ({base_corpus_s:.1f}s)", flush=True)
    if base_suite != 0 or base_corpus != 0:
        target.write_text(pristine)
        print("ABORT: an instrument is not green on the pristine tree")
        return 1

    mutants = enumerate_mutants(pristine)
    print(f"enumerated {len(mutants)} mutants from the fixed grammar", flush=True)

    rows = []
    try:
        for i, (mid, code) in enumerate(mutants, 1):
            target.write_text(code)
            s = run_suite()
            c = run_corpus()
            rows.append({"id": mid, "suite_killed": s != 0, "corpus_killed": c != 0})
            print(f"[{i}/{len(mutants)}] {mid:38s} suite={'KILL' if s else 'live'} "
                  f"corpus={'KILL' if c else 'live'}", flush=True)
    finally:
        target.write_text(pristine)

    both = [r for r in rows if r["suite_killed"] and r["corpus_killed"]]
    only_s = [r for r in rows if r["suite_killed"] and not r["corpus_killed"]]
    only_c = [r for r in rows if r["corpus_killed"] and not r["suite_killed"]]
    neither = [r for r in rows if not r["suite_killed"] and not r["corpus_killed"]]

    summary = {
        "subject": "examples/distributed_history (ecommerce_backend/domain.py)",
        "mutants": len(rows),
        "killed_by_both": len(both),
        "unique_to_suite": len(only_s),
        "unique_to_corpus": len(only_c),
        "killed_by_neither": len(neither),
        "unique_to_suite_ids": [r["id"] for r in only_s],
        "unique_to_corpus_ids": [r["id"] for r in only_c],
        "survivor_ids": [r["id"] for r in neither],
        "pristine_seconds": {"suite": round(base_suite_s, 2), "corpus": round(base_corpus_s, 2)},
        "rows": rows,
    }
    (SCRATCH / "kill-table.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
