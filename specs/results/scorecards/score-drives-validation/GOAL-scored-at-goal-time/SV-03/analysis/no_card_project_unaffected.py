#!/usr/bin/env python3
"""SV-03. A project with no card is unaffected -- DEMONSTRATED, not asserted.

    python3 specs/results/scorecards/score-drives-validation/\\
GOAL-scored-at-goal-time/SV-03/analysis/no_card_project_unaffected.py

The claim under test is `the_card_is_never_mandatory`: after the four proposed
diffs, a project that has never heard of a scorecard runs epics exactly as it
does today. Asserting that is cheap and worthless, so this executes it:

1. Copies the three installed skill units to a ticket-specific temp directory,
   twice: PRISTINE and PATCHED. **The installed home is never written to** --
   proved at the end by re-hashing all three files against the hashes taken
   before anything ran.
2. Runs the epic plan validator from the PRISTINE copy and from the PATCHED
   copy over two plans: `no_card_plan.yaml` (a complete epic with two command
   harnesses, no rubric, no judge, no card) and this repository's own live
   plan. Compares exit codes and stdout byte for byte.
3. Prints the opening clause of every block the diffs add, because that is the
   structural reason the answer is yes: a reader who has no card never enters
   any of them.
4. Counts, on the patched files, the words a no-card reader is asked to read
   that they were not asked to read before.

Refuses nothing, changes nothing, exits 0 unless a comparison FAILS -- in
which case it says which, and that is the honest outcome.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

UNITS = {
    "git-epic-workflow": ["references/goals-and-evaluation.md"],
    "git-issue-workflow": ["references/goal-signal.md"],
    "git-issue": ["references/regression-close.md"],
}

PATCH_UNIT = {
    "01-git-epic-workflow-goals-and-evaluation-third-branch.patch": "git-epic-workflow",
    "02-git-epic-workflow-goals-and-evaluation-evidence-is-a-card.patch": "git-epic-workflow",
    "03-git-issue-workflow-goal-signal-subtraction.patch": "git-issue-workflow",
    "04-git-issue-regression-close-loop-outlet.patch": "git-issue",
}

#: An added block must OPEN with one of these. A block that does not is a
#: sentence a project with no card has to read and obey, and the whole design
#: rests on there being none of those. Checked again, on the patch files, by
#: tests/test_goal_baseline_is_a_card.py.
GUARDS = re.compile(r"^(Where\b|For a judged\b|Harness is judged\b)")


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "references" / "eval_scorecard.md").exists():
            return parent
    sys.exit("could not find the repository root")


def skill_home() -> Path:
    home = os.environ.get("SKILL_MANAGER_HOME")
    return Path(home) if home else Path.home() / ".claude"


def unit_dir(home: Path, unit: str) -> Path:
    base = home / "skills" / unit
    return base if base.exists() else home / unit


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def run(cmd: list[str], cwd: Path) -> tuple[int, str]:
    """Exit code and STDOUT. Stderr is deliberately excluded from the compared
    payload and reported separately: `uv run --script` writes its provisioning
    chatter there on a cold cache ("Installed 1 package"), so a stderr in the
    comparison makes the first run of the pair differ from the second for a
    reason that has nothing to do with either build. Measured, not assumed --
    it is what made the first version of this script report a false difference.
    """
    out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return out.returncode, out.stdout


def added_blocks(patch: Path) -> list[list[str]]:
    blocks: list[list[str]] = []
    cur: list[str] = []
    for line in patch.read_text(encoding="utf-8").splitlines():
        if line.startswith("+++"):
            continue
        if line.startswith("+"):
            cur.append(line[1:])
        else:
            if cur:
                blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    return blocks


def plain(text: str) -> str:
    """Markdown emphasis and list markers stripped, so a guard is visible."""
    return re.sub(r"^[-*]\s+", "", text.replace("**", "").replace("`", "")).strip()


def main() -> int:
    root = repo_root()
    home = skill_home()
    here = Path(__file__).resolve().parent.parent
    diffs = here / "proposed-skill-diffs"
    failures: list[str] = []

    before = {
        f"{u}/{f}": digest(unit_dir(home, u) / f)
        for u, files in UNITS.items() for f in files
    }
    print(f"skill home (READ ONLY): {home}")
    for key, value in before.items():
        print(f"  {value}  {key}")
    print()

    tmp = Path(tempfile.mkdtemp(prefix="SV-03-no-card-"))
    print(f"temp (ticket-specific): {tmp}")
    for label in ("pristine", "patched"):
        for unit in UNITS:
            shutil.copytree(unit_dir(home, unit), tmp / label / unit,
                            symlinks=True, ignore=shutil.ignore_patterns("__pycache__", ".git"))
    for name, unit in sorted(PATCH_UNIT.items()):
        code, out = run(["git", "apply", str(diffs / name)], tmp / "patched" / unit)
        print(f"  apply {name} -> exit {code} {out.strip()}")
        if code != 0:
            failures.append(f"patch {name} did not apply")
    print()

    print("## The validator, before and after, on a project with NO CARD")
    validator = "scripts/validate_epic_plan.py"
    plans = {
        "no_card_plan.yaml": here / "no_card_plan.yaml",
        "this repo's live plan": root / "specs/desired_program_model/ticket_plan.yaml",
    }
    print("  (the validator is run through its own `uv run --script` shebang, from each")
    print("   build in turn. The only normalisation is the build directory itself, which")
    print("   differs by construction; it is replaced by <BUILD> and nothing else is.)")
    for label, plan in plans.items():
        results = {}
        for build in ("pristine", "patched"):
            script = tmp / build / "git-epic-workflow" / validator
            code, out = run(["uv", "run", "--script", str(script), str(plan)], root)
            results[build] = (code, out.replace(str(tmp / build), "<BUILD>"))
        same = results["pristine"] == results["patched"]
        print(f"  {label}")
        print(f"    pristine: exit {results['pristine'][0]}  {results['pristine'][1].strip()[:100]}")
        print(f"    patched : exit {results['patched'][0]}  {results['patched'][1].strip()[:100]}")
        print(f"    IDENTICAL: {same}")
        if not same:
            failures.append(f"validator output differs on {label}")
    print()

    print("## Why: every added block opens with a conditional a no-card project fails")
    words_added = 0
    for name in sorted(PATCH_UNIT):
        for block in added_blocks(diffs / name):
            body = " ".join(line for line in block if line.strip())
            words_added += len(body.split())
            opening = plain(body)
            ok = bool(GUARDS.match(opening))
            print(f"  [{'guarded' if ok else 'UNGUARDED'}] {name[:2]}: {opening[:88]}...")
            if not ok:
                failures.append(f"{name} adds an unguarded block")
    print(f"\n  words added across all four files: {words_added}")
    print("  words a project with no card must obey: 0 -- every block above is inside a")
    print("  conditional it does not satisfy, so they read as sentences about somebody")
    print("  else's instrument, beside the ones already there.")
    print()

    print("## The installed home is byte-identical to before this ran")
    after = {
        f"{u}/{f}": digest(unit_dir(home, u) / f)
        for u, files in UNITS.items() for f in files
    }
    for key in before:
        same = before[key] == after[key]
        print(f"  {'UNCHANGED' if same else 'MODIFIED '}  {key}")
        if not same:
            failures.append(f"{key} was modified -- skills are READ, never edited")
    shutil.rmtree(tmp, ignore_errors=True)
    print()

    if failures:
        print("FAILURES:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("A project with no card is unaffected: demonstrated on two plans, both loaders")
    print("of the plan checked elsewhere, no gate added, and nothing applied to the home.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
