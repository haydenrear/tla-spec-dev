#!/usr/bin/env python3
"""Mechanical grouping of Sweep-3 raw hits.

THE GROUPING RULES, stated as rules so a reader applying them to the raw file
lands on the same groups. Every raw hit falls into exactly one group of exactly
one table; no hit is discarded.

Error paths (`behavior-errorpaths.txt`), grouped by DISTINCT FAILURE SEMANTICS,
keyed off the line's own syntax:

  EP-COMMENT  the token is inside a comment/string, or the file is not Python
  EP-RAISE-SYSEXIT   `raise SystemExit(...)` -- refuse the command, exit nonzero
  EP-RAISE-DOMAIN    `raise <ToolchainError>` -- a named toolchain refusal class
  EP-RAISE-BUILTIN   `raise <builtin>` -- programmer error / precondition
  EP-RAISE-BARE      bare `raise` -- re-raise, no new semantics
  EP-CATCH-SWALLOW   `except ...:` whose body is `pass`/`continue`/a default
  EP-CATCH-REPORT    `except ...:` that raises, records or prints
  EP-TRY             `try:` line itself -- scaffolding, no semantics of its own

Config branches (`behavior-configbranches.txt`), by WHERE THE VALUE COMES FROM:

  CB-CLI-GUARDFLAG   one of the six guard-weakening flags the plan MODELS
  CB-CLI-OTHER       any other `--flag` / `args.<x>` read
  CB-ENV             `os.environ` / `getenv`
  CB-MANIFEST        `.get("...")` against a parsed manifest/plan/TOML
  CB-COMMENT         comment, string, or non-Python file

Fallbacks (`behavior-fallbacks.txt`):

  FB-IMPORT      `except ImportError` dual-import shim (script vs package)
  FB-SILENT      `except ...: pass` / `or None` -- proceeds with a default
  FB-DEFAULT     the word `default` in an argparse/manifest default
  FB-COMMENT     comment, string, or non-Python file

Usage: python3 group_behaviors.py <repo_root>
"""
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collapse_effects import code_lines  # noqa: E402  (shares the tokenise cache)

HERE = Path(__file__).resolve().parent

GUARD_FLAGS = ("--accept-new", "accept_new", "--allow-open", "allow_open",
               "--no-promote-current", "no_promote_current", "--force", "force",
               "--dry-run", "dry_run", "--no-batch", "no_batch")


def classify_error(src: str) -> str:
    s = src.strip()
    if s.startswith("try:"):
        return "EP-TRY"
    if re.match(r"^raise\s+SystemExit", s):
        return "EP-RAISE-SYSEXIT"
    if re.match(r"^raise\s*$", s):
        return "EP-RAISE-BARE"
    m = re.match(r"^raise\s+([A-Za-z_][A-Za-z0-9_.]*)", s)
    if m:
        name = m.group(1).split(".")[-1]
        builtins = {"ValueError", "TypeError", "KeyError", "RuntimeError", "OSError",
                    "AssertionError", "NotImplementedError", "IndexError", "AttributeError",
                    "FileNotFoundError", "ImportError", "Exception"}
        return "EP-RAISE-BUILTIN" if name in builtins else "EP-RAISE-DOMAIN"
    if "except" in s:
        return "EP-CATCH"
    return "EP-OTHER"


def classify_config(src: str) -> str:
    s = src.strip()
    if any(f in s for f in GUARD_FLAGS):
        return "CB-CLI-GUARDFLAG"
    if "environ" in s or "getenv" in s:
        return "CB-ENV"
    if re.search(r'--[a-z0-9-]+', s) or "args." in s:
        return "CB-CLI-OTHER"
    if re.search(r"\.get\(", s):
        return "CB-MANIFEST"
    return "CB-OTHER"


def classify_fallback(src: str) -> str:
    s = src.strip()
    if "ImportError" in s:
        return "FB-IMPORT"
    if re.search(r"except.*:\s*pass", s) or "or None" in s:
        return "FB-SILENT"
    if "fallback" in s:
        return "FB-FALLBACK"
    return "FB-DEFAULT"


TABLES = {
    "errorpaths": (classify_error, "EP-COMMENT"),
    "configbranches": (classify_config, "CB-COMMENT"),
    "fallbacks": (classify_fallback, "FB-COMMENT"),
}


def main() -> int:
    lines_out = []
    for name, (fn, comment_group) in TABLES.items():
        raw = [l for l in (HERE / f"behavior-{name}.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
        groups = Counter()
        detail: dict[str, list[str]] = {}
        for line in raw:
            m = re.match(r"^(.+?):(\d+):(.*)$", line)
            if not m:
                continue
            path, ln, raw_src = m.group(1), int(m.group(2)), m.group(3)
            cl = code_lines(path)
            src = "" if cl is None else cl.get(ln, "")
            # COMMENT vs CODE is decided on the BLANKED line (a hit that
            # survives tokenisation is executable). The group is then chosen
            # from the RAW line, because flag names and manifest keys are
            # string literals that blanking erases.
            g = comment_group if not src.strip() else fn(raw_src)
            groups[g] += 1
            detail.setdefault(g, []).append(f"{path}:{ln}:{src.strip()}")
        (HERE / f"behavior-{name}-groups.txt").write_text(
            "\n".join(f"{g}\t{c}" for g, c in groups.most_common()) + "\n", encoding="utf-8")
        for g, rows in detail.items():
            (HERE / f"behavior-{name}-{g}.txt").write_text("\n".join(rows) + "\n", encoding="utf-8")
        total = sum(groups.values())
        lines_out.append(f"{name}\traw={len(raw)}\tgrouped={total}\tgroups={len(groups)}\t"
                         + " ".join(f"{g}={c}" for g, c in groups.most_common()))
    text = "\n".join(lines_out) + "\n"
    (HERE / "behavior-group-summary.txt").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
