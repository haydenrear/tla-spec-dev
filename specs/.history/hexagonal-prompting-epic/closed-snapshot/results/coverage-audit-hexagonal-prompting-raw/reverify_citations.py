#!/usr/bin/env python3
"""MF-026 re-verification at 0a05eed: are the closure's new citations true?

RC-02's `tests/test_source_citations.py` requires citations be file-qualified
AND content-anchored -- `file.py:116 (subprocess.run)` -- so a one-line shift
fails where a "does the line exist" check would pass. The owner reports three of
their own new citations were rejected by it and fixed. This re-derives every
`path:line (anchor)` citation in the three manifests and the three model files
INDEPENDENTLY of that test, so the check is not being graded by the thing it
grades.

Usage: python3 reverify_citations.py <repo_root>
"""
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
CITE = re.compile(r"\b((?:scripts|specs|skill-scripts|tests)/[\w./-]+?):(\d+)\s*\(([^)]+)\)")

TARGETS = [
    "specs/current/spec_manifest.yaml",
    "specs/program_model/spec_manifest.yaml",
    "specs/desired_program_model/spec_manifest.yaml",
    "specs/current/TlaSpecDevCli.tla",
    "specs/program_model/TlaSpecDevCli.tla",
    "specs/desired_program_model/TlaSpecDevCli.tla",
]

# Citations introduced by the G-1/G-2 closure (commit b9836f7).
NEW = {
    ("scripts/effect_conformance.py", 1685),
    ("scripts/effect_conformance.py", 1809),
    ("scripts/run_generated_case_adapters.py", 2178),
}


def main() -> int:
    cache: dict[str, list[str]] = {}
    total = bad = 0
    print("=== every content-anchored citation in the 3 manifests + 3 model files ===")
    for t in TARGETS:
        text = (ROOT / t).read_text(encoding="utf-8")
        for path, line, anchor in CITE.findall(text):
            total += 1
            src = cache.setdefault(path, (ROOT / path).read_text(encoding="utf-8").splitlines()
                                  if (ROOT / path).is_file() else [])
            n = int(line)
            present = bool(src) and 1 <= n <= len(src) and anchor.strip() in src[n - 1]
            tag = "NEW " if (path, n) in NEW else "    "
            if not present:
                bad += 1
                print(f"  {tag}STALE  {t}: {path}:{n} ({anchor})")
                if src and 1 <= n <= len(src):
                    print(f"            line {n} is: {src[n-1].strip()[:90]}")
            elif (path, n) in NEW:
                print(f"  {tag}OK     {path}:{n} ({anchor})  ->  {src[n-1].strip()[:80]}")
    print(f"\n  total citations checked: {total}   stale: {bad}")

    print("\n=== the closure's three NEW citations, resolved ===")
    for path, n in sorted(NEW):
        src = (ROOT / path).read_text(encoding="utf-8").splitlines()
        print(f"  {path}:{n}  ->  {src[n-1].strip()}")

    print("\n=== ticket_plan.yaml citations (NOT covered by test_source_citations.py) ===")
    plan = (ROOT / "specs/desired_program_model/ticket_plan.yaml").read_text(encoding="utf-8")
    for path, line, anchor in CITE.findall(plan):
        src = (ROOT / path).read_text(encoding="utf-8").splitlines() if (ROOT / path).is_file() else []
        n = int(line)
        present = bool(src) and 1 <= n <= len(src) and anchor.strip() in src[n - 1]
        print(f"  {'OK   ' if present else 'STALE'} {path}:{n} ({anchor})")
    # bare file:line-range citations with no anchor -- the class the checker cannot see
    for m in re.finditer(r"\b((?:scripts|specs)/[\w./-]+?):(\d+)(?:-(\d+))?(?!\s*\()", plan):
        path, a, b = m.group(1), int(m.group(2)), m.group(3)
        src = (ROOT / path).read_text(encoding="utf-8").splitlines() if (ROOT / path).is_file() else []
        print(f"  UNANCHORED {path}:{a}{'-' + b if b else ''}"
              f"   line {a} is: {src[a-1].strip()[:70] if src and a <= len(src) else '<out of range>'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
