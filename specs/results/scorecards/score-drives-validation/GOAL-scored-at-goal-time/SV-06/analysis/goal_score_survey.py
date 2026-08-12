#!/usr/bin/env python3
"""Re-derive every figure in `references/goal_score_wiring.md` (SV-06).

    uv run --with pyyaml python3 \
      specs/results/scorecards/score-drives-validation/GOAL-scored-at-goal-time/SV-06/analysis/goal_score_survey.py

Reads only this repository's plans on disk and the installed Skill Manager
home. Writes nothing. Every figure it prints names the tree it was computed
over (`git rev-parse --short HEAD`), because a count over the plan record is a
joint property of the record and the tree and moves when either does.

It DOES NOT edit or import any skill. `SKILL_MANAGER_HOME` is read-only here.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - operator error, not a defect
    sys.exit("needs pyyaml: uv run --with pyyaml python3 <this file>")

DIMENSION = re.compile(r"\bD[1-5]\b")

# The three skills the survey covers. Anything outside them is reported as an
# excluded population rather than silently dropped.
SURVEYED_SKILLS = ("git-epic-workflow", "git-issue-workflow", "git-issue")

# `dimension` is deliberately absent: a dimension id is an index into one
# project's rubric and is not a cross-skill term. See goal_score_wiring.md §5.
CARD_TERMS = re.compile(r"scorecard|score_tools|rubric", re.IGNORECASE)


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "references" / "eval_scorecard.md").exists():
            return parent
    sys.exit("could not find the repository root (no references/eval_scorecard.md above me)")


def tree(root: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=root, capture_output=True, text=True, check=True,
        )
        return out.stdout.strip()
    except Exception:
        return "UNKNOWN-TREE"


def every_plan_goal(root: Path) -> dict[str, dict]:
    """Every distinct epic goal in every plan on disk, live and sealed.

    `specs/.history` is a hidden directory, so a `glob('specs/**')` misses all
    of it and reports 4 goals instead of 27. os.walk is used for that reason.
    """
    goals: dict[str, dict] = {}
    for dirpath, _dirs, files in os.walk(root / "specs"):
        if "ticket_plan.yaml" not in files:
            continue
        try:
            plan = yaml.safe_load(Path(dirpath, "ticket_plan.yaml").read_text())
        except Exception:
            continue
        for goal in (plan or {}).get("epic_goals") or []:
            if isinstance(goal, dict) and "id" in goal:
                goals.setdefault(goal["id"], goal)
    return goals


def skill_surface(home: Path) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for skill in SURVEYED_SKILLS:
        base = home / "skills" / skill
        if not base.exists():
            base = home / skill  # a bare ~/.claude/skills layout
        found = []
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix not in {".md", ".py"}:
                continue
            # A skill's own installed dependencies are not its surface. Left
            # in as a named exclusion rather than a silent filter: without it
            # this count is 7 and the seventh is a pygments lexer.
            if {".venv", "__pycache__", "node_modules"} & set(path.parts):
                continue
            try:
                if CARD_TERMS.search(path.read_text(errors="ignore")):
                    found.append(str(path.relative_to(base)))
            except Exception:
                continue
        hits[skill] = found
    return hits


def main() -> int:
    root = repo_root()
    print(f"tree: {tree(root)}   (every figure below is about THIS tree)")
    print()

    goals = every_plan_goal(root)
    keyed = [
        gid for gid, g in sorted(goals.items())
        if DIMENSION.search(" ".join(str(g.get(k, "")) for k in
                                     ("statement", "metric", "harness", "target")))
    ]
    with_card_baseline = [
        gid for gid, g in sorted(goals.items())
        if "scorecard.json" in str((g.get("baseline") or {}).get("evidence", ""))
    ]
    evidences = sorted({
        str((g.get("baseline") or {}).get("evidence", "")).strip()
        for g in goals.values()
    })
    cards = list((root / "specs" / "results" / "scorecards").rglob("scorecard.json"))

    print("## The plan record")
    print(f"distinct epic goals across every ticket_plan.yaml on disk : {len(goals)}")
    print(f"  ... that name a scorecard dimension (D1-D5) in prose    : {len(keyed)}")
    print(f"  ... whose baseline.evidence points at a scorecard.json  : {len(with_card_baseline)}")
    print(f"distinct baseline.evidence values                         : {len(evidences)}")
    print(f"sealed scorecard.json files under specs/results/scorecards: {len(cards)}")
    print()
    print("dimension-keyed goals:")
    for gid in keyed:
        print(f"  {gid}")
    print()
    print("every distinct baseline.evidence value:")
    for e in evidences:
        print(f"  {e[:140]}")
    print()

    home = Path(os.environ.get("SKILL_MANAGER_HOME", Path.home() / ".claude"))
    print(f"## The skill surface  (read-only, home={home})")
    surface = skill_surface(home)
    total = sum(len(v) for v in surface.values())
    print(f"files in {len(SURVEYED_SKILLS)} skills matching /scorecard|score_tools|rubric/: {total}")
    for skill, files in surface.items():
        for f in files:
            print(f"  {skill}/{f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
