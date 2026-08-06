#!/usr/bin/env python3
"""Make the three blind artifact copies PA-06's judges are given, and prove the
sanitising pass changed nothing but comments and docstrings.

Descended from EVAL-RERUN's pass and written against the leak that one had:
HP-06 grepped for `arm A` and the file said `Arm A`. Everything here is
case-insensitive, and the result is verified by a second grep rather than by the
substitution having been written correctly.

WHAT IT DOES NOT DO. It does not touch the arms on disk. Every arm this round
judges is read-only input: two are a predecessor's sealed artifacts and the
third is a blind author's output that PA-06 must not edit after seeing it.

WHAT IT CANNOT DO, stated because EVAL-RERUN stated it and it has not changed.
An artifact whose author was asked to explain its design describes that design
in its own words. A judge reading a NOTES.md that talks about a declared port, a
fake and a composition point learns that THIS artifact was asked for a
structure. No substitution fixes that, and any round claiming a blind judgement
of an architecture prompt has to say so.
"""

from __future__ import annotations

import ast
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[4]
RERUN = REPO_ROOT / "specs/results/scorecards/hexagonal-prompting-rerun"
PA06 = REPO_ROOT / "specs/results/scorecards/ports-as-adapters"
OUT = PA06 / "blind"

#: opaque label -> source tree. THE MAPPING IS NOT PRINTED and lives in
#: UNBLINDING.md, which judges are not given. Labels are `score_tools.py
#: scaffold`'s, drawn from a pool excluding every label any prior round
#: published (HP-06 used X/Y, EVAL-RERUN used P/Q).
SOURCES = {
    "T": RERUN / "arms/arm_b",
    "U": RERUN / "arms/arm_a",
    "W": PA06 / "arms/arm_c",
}

#: Every pattern is applied case-insensitively. Order matters: the longer,
#: more specific forms go first so a shorter one cannot eat their prefix.
SUBSTITUTIONS: list[tuple[str, str]] = [
    (r"wt-epic-[A-Za-z0-9_.-]+", "<worktree>"),
    (r"/(?:private/)?tmp/[A-Za-z0-9_./-]*", "<scratch>"),
    (r"/Users/[A-Za-z0-9_./-]*", "<path>"),
    (r"specs/results/scorecards/[A-Za-z0-9_./-]*", "<results-path>"),
    (r"PREDICTIONS-[A-Z]+\.md", "<predictions-file>"),
    (r"\bEVAL-RERUN\b", "this round"),
    (r"\bEVAL-SUPPRESS\b", "this round"),
    (r"\bHP-\d+\b", "<ticket>"),
    (r"\bPA-\d+\b", "<ticket>"),
    (r"\barms?[ _-]?[abc]\b", "this artifact"),
    (r"\bthe (?:other|second|first) arm\b", "another artifact"),
    (r"\barms\b", "artifacts"),
    (r"\barm\b", "artifact"),
    (r"\bhexagonal\b", "structured"),
    (r"\btreatment\b", "variant"),
]

#: What the verification grep looks for afterwards. A hit is a failure.
FORBIDDEN = re.compile(
    r"arm[ _-]?[abc]\b|\barms?\b|hexagonal|treatment|control arm|EVAL-RERUN|"
    r"EVAL-SUPPRESS|\bHP-\d|\bPA-\d|ports-as-adapters|hexagonal-prompting",
    re.IGNORECASE,
)


def sanitise(text: str) -> str:
    for pattern, replacement in SUBSTITUTIONS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def strip_docstrings_and_comments(source: str) -> str:
    """An AST dump with every docstring blanked.

    The equality this proves is the one that matters: sanitising may rewrite
    prose and may not rewrite behaviour. Comments never reach the AST, so
    blanking docstrings is the whole of the difference the pass may make.
    """
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", None)
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                    and isinstance(body[0].value.value, str):
                body[0].value.value = ""
    return ast.dump(tree)


def main() -> int:
    failures: list[str] = []
    if OUT.exists():
        shutil.rmtree(OUT)
    for label, source in SOURCES.items():
        target = OUT / f"artifact_{label}"
        shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__"))
        # REJECTED.md IS WITHHELD, and the asymmetry is the reason. PA-06 asked
        # the one arm it dispatched itself for a rejected-designs file; the two
        # predecessor arms were never asked. Shipping it in one blind copy and
        # not the others would tell a judge which artifact this round produced,
        # which is a bigger leak than anything the file contains. It is read in
        # the findings-by-channel section instead, where its provenance is
        # stated.
        for stray in target.rglob("REJECTED.md"):
            stray.unlink()
        for path in sorted(target.rglob("*")):
            if path.suffix not in {".py", ".md"} or not path.is_file():
                continue
            original = path.read_text(encoding="utf-8")
            cleaned = sanitise(original)
            path.write_text(cleaned, encoding="utf-8")
            for line_number, line in enumerate(cleaned.splitlines(), start=1):
                if FORBIDDEN.search(line):
                    failures.append(f"LEAK {path.relative_to(OUT)}:{line_number}: {line.strip()[:90]}")
            if path.suffix == ".py":
                relative = path.relative_to(target)
                before = strip_docstrings_and_comments((source / relative).read_text(encoding="utf-8"))
                after = strip_docstrings_and_comments(cleaned)
                if before != after:
                    failures.append(f"AST DIFFERS {path.relative_to(OUT)}")
        print(f"artifact_{label}: {sum(1 for p in target.rglob('*') if p.is_file())} file(s)")
    for failure in failures:
        print(failure)
    print("VERIFY:", "clean" if not failures else f"{len(failures)} problem(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
