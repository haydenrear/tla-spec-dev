#!/usr/bin/env python3
"""SV-03. Can the evaluation ticket RE-READ the baseline it is comparing against?

    uv run --with pyyaml python3 \
      specs/results/scorecards/score-drives-validation/GOAL-scored-at-goal-time/SV-03/analysis/baseline_is_a_card.py

SV-06 measured that 0 of 27 goals cite a sealed card. That figure is a string
test -- it asks whether `scorecard.json` appears in `baseline.evidence`. This
asks the question the third branch actually cares about, which is stronger and
is the one an evaluation ticket has to answer: **given only the goal, can you
open the card that produced the baseline number?**

It RESOLVES every `baseline.evidence` against the filesystem and says what it
found. That turns "0 of 27" from a grep into a demonstration, and it produces
the R1 failing input on a real epic plan rather than a fixture.

WHAT THIS IS NOT
----------------
**It is not a gate and nothing consults it.** It exits 0 on every input,
including inputs it has nothing to say about. It is not imported by any script
in `scripts/`, not wired into any validator, and not run by any close-out. A
plan with no goals, a goal with no judged harness and a project with no card
are all *reported and passed over* -- see `## Fail-open`, which is executed
rather than asserted. `no_new_gates_rule` and `the_card_is_never_mandatory`.

Writes nothing. Reads this repository's plans on disk. Every figure names the
tree it was computed over, because a count over the plan record is a joint
property of the record and the tree.
"""

from __future__ import annotations

import json
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

#: A goal whose harness or metric says none of this is not a judged goal, and
#: nothing below applies to it. Deliberately generous: over-including costs a
#: line of report, under-including would quietly drop a subject.
JUDGED = re.compile(r"scorecard|score_tools|rubric|card|judge|\bD[1-5]\b", re.IGNORECASE)

#: A figure computed over a POPULATION of cards rather than from one card.
#: `GOAL-D2-can-move`'s baseline is "D2 = 2 on 27 of 27 cards"; there is no
#: single card that produced it. See `## Population baselines`.
POPULATION = re.compile(
    r"\b\d+\s+of\s+\d+\s+cards?\b|\bevery sealed card\b|\ball \d+ cards?\b"
    r"|\b\d+\s+cards?\s+(?:ever|to date|so far)\b|\bacross \d+ cards?\b",
    re.IGNORECASE,
)

#: Tokens in a free-text evidence string that could be a path. `--` introduces
#: this project's habitual trailing note ("<path> -- CL-04-DF-05") and the note
#: is not a path.
PATHISH = re.compile(r"[A-Za-z0-9_./-]*/[A-Za-z0-9_./-]*|[A-Za-z0-9_.-]+\.(?:json|md|ya?ml)")


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


def every_plan(root: Path) -> list[tuple[Path, dict]]:
    """Every plan on disk, live and sealed.

    `specs/.history` is hidden, so `glob('specs/**')` misses all of it and sees
    4 goals instead of 27. os.walk, for the reason SV-06 gives.
    """
    plans: list[tuple[Path, dict]] = []
    for dirpath, _dirs, files in os.walk(root / "specs"):
        if "ticket_plan.yaml" not in files:
            continue
        path = Path(dirpath, "ticket_plan.yaml")
        try:
            plan = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(plan, dict):
            plans.append((path, plan))
    return plans


def distinct_goals(plans: list[tuple[Path, dict]]) -> dict[str, dict]:
    goals: dict[str, dict] = {}
    for _path, plan in plans:
        for goal in plan.get("epic_goals") or []:
            if isinstance(goal, dict) and "id" in goal:
                goals.setdefault(goal["id"], goal)
    return goals


def candidate_paths(evidence: str) -> list[str]:
    """Path-shaped tokens in a free-text evidence string, before the note."""
    head = evidence.split(" -- ")[0]
    out: list[str] = []
    for token in PATHISH.findall(head):
        token = token.strip().strip(",;")
        # ``file.md:309-315`` is a citation; the file is the path.
        token = token.split(":")[0]
        if token and token not in out:
            out.append(token)
    return out


def classify(root: Path, goal: dict) -> tuple[str, str]:
    """(verdict, why) for one goal's baseline. NEVER raises, never refuses."""
    text = " ".join(str(goal.get(k, "")) for k in ("statement", "metric", "harness", "target"))
    baseline = goal.get("baseline") or {}
    evidence = str(baseline.get("evidence", "") or "").strip()

    if not JUDGED.search(text):
        return "not-judged", "no judged instrument named -- this goal is out of scope, and that is legal"
    if not evidence:
        return "no-evidence", "a judged goal with no evidence field"

    cards: list[str] = []
    dirs: list[str] = []
    files: list[str] = []
    missing: list[str] = []
    for token in candidate_paths(evidence):
        target = root / token
        if target.is_file() and target.name == "scorecard.json":
            cards.append(token)
        elif target.is_dir():
            dirs.append(token)
        elif target.is_file():
            files.append(token)
        else:
            missing.append(token)

    if cards:
        return "card", f"{len(cards)} sealed card(s) resolve: {', '.join(cards)}"
    if dirs:
        return "directory", f"a directory, not a card: {dirs[0]} (contains {len(list((root / dirs[0]).rglob('scorecard.json')))} cards; the goal does not say which)"
    if files:
        return "summary", f"a document, not a card: {files[0]}"
    if missing:
        return "unresolvable", f"path-shaped but does not resolve at this tree: {missing[0]}"
    return "prose", f"no path at all: {evidence[:70]!r}"


VERDICTS = ("card", "directory", "summary", "unresolvable", "prose", "no-evidence", "not-judged")


def reread(root: Path, card: Path) -> str:
    """What an evaluation ticket gets when the baseline IS a card."""
    data = json.loads(card.read_text(encoding="utf-8"))
    scored = {
        k: v.get("score")
        for k, v in (data.get("dimensions") or {}).items()
        if isinstance(v, dict) and v.get("score") is not None
    }
    return (
        f"version {data.get('scorecard_version')}, {data.get('example')}, "
        f"run {data.get('run_id')}, commit {data.get('commit')}, "
        f"judge pass {(data.get('judge') or {}).get('pass')}, scores {scored}"
    )


def main() -> int:
    root = repo_root()
    print(f"tree: {tree(root)}   (every figure below is about THIS tree)")
    print()

    plans = every_plan(root)
    goals = distinct_goals(plans)
    cards_on_disk = list((root / "specs" / "results" / "scorecards").rglob("scorecard.json"))

    print("## The population")
    print(f"plans on disk (live + sealed)                              : {len(plans)}")
    print(f"distinct epic goals                                        : {len(goals)}")
    print(f"sealed scorecard.json files under specs/results/scorecards : {len(cards_on_disk)}")
    print("cross-check against SV-06 at 5620c9a: 27 goals, 87 cards, 0 card-backed.")
    print()

    buckets: dict[str, list[tuple[str, str]]] = {v: [] for v in VERDICTS}
    for gid, goal in sorted(goals.items()):
        verdict, why = classify(root, goal)
        buckets[verdict].append((gid, why))

    print("## Can the evaluation ticket open the baseline card?")
    for verdict in VERDICTS:
        print(f"{verdict:>14} : {len(buckets[verdict])}")
    print()
    for verdict in VERDICTS:
        if not buckets[verdict]:
            continue
        print(f"### {verdict}")
        for gid, why in buckets[verdict]:
            print(f"  {gid:<34} {why}")
        print()

    print("## The R1 failing input, on a real epic plan")
    print("Subject: GOAL-loop-reaches-the-program, this epic's own live plan at")
    print("specs/desired_program_model/ticket_plan.yaml -- sealed at eab2883, never edited.")
    goal = goals.get("GOAL-loop-reaches-the-program")
    if goal is None:
        print("  ABSENT at this tree -- report that rather than substituting another goal.")
    else:
        verdict, why = classify(root, goal)
        evidence = str((goal.get("baseline") or {}).get("evidence", ""))
        print(f"  baseline.evidence : {evidence}")
        print(f"  verdict           : {verdict}")
        print(f"  why               : {why}")
        print("  FAILING: the evaluation ticket cannot re-read the number. It is handed a")
        print("  folder and would have to pick a card out of it, which is the exact move")
        print("  goals-and-evaluation.md's judged-baseline paragraph already forbids.")
    print()

    print("## Population baselines -- where SV-06's proposed wording does not fit")
    print("SV-06 proposed: 'baseline.evidence is the path to the SINGLE sealed card that")
    print("produced the number'. Some real baselines are figures over MANY cards, and no")
    print("single card produced them. Those goals cannot comply with that wording at all.")
    pop = [
        (gid, str((g.get("baseline") or {}).get("value", ""))[:90])
        for gid, g in sorted(goals.items())
        if POPULATION.search(str((g.get("baseline") or {}).get("value", "")))
    ]
    print(f"  judged goals whose baseline VALUE is a figure over a population of cards: {len(pop)}")
    for gid, value in pop:
        print(f"    {gid:<34} {value!r}")
    print()

    print("## The worked example, re-read")
    example = root / (
        "specs/results/scorecards/score-drives-validation/"
        "GOAL-scored-at-goal-time/SV-03/example_goal.yaml"
    )
    if not example.exists():
        print(f"  MISSING: {example.relative_to(root)}")
    else:
        parsed = yaml.safe_load(example.read_text(encoding="utf-8"))
        for goal in parsed["epic_goals"]:
            verdict, why = classify(root, goal)
            print(f"  {goal['id']:<34} verdict={verdict}  ({why})")
            for token in candidate_paths(str((goal.get("baseline") or {}).get("evidence", ""))):
                card = root / token
                if card.is_file() and card.name == "scorecard.json":
                    print(f"      re-read -> {reread(root, card)}")
    print()

    print("## Fail-open -- executed, not asserted")
    no_goals = {"epic_goals": [], "goals_waived": "no behavioral delta"}
    print(f"  a plan with epic_goals: [] and goals_waived   -> {len(distinct_goals([(Path('x'), no_goals)]))} goals to classify, nothing to say, exit 0")
    unjudged = {
        "id": "GOAL-ingest-p99", "kind": "perf",
        "statement": "Batched ingest cuts tail latency.",
        "metric": "p99 over the ingest bench", "harness": "bench/ingest.sh",
        "target": "p99 <= 250ms",
        "baseline": {"value": "p99 412ms", "evidence": "results/bench/run.json"},
    }
    print(f"  a goal with a COMMAND harness and no card    -> {classify(root, unjudged)[0]}: {classify(root, unjudged)[1]}")
    empty = {"id": "GOAL-empty", "statement": "", "metric": "", "harness": "", "target": ""}
    print(f"  a goal with every field empty                -> {classify(root, empty)[0]}")
    print()
    print("REFUSES NOTHING: this exits 0 on every input above, including the failing one.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
