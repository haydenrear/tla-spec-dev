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

SS-03 REPAIRED TWO DEFECTS IN THIS INSTRUMENT (stabilize-substrate)
-------------------------------------------------------------------
Both were found by this epic's kickoff, both mis-reported *in a direction*, and
both are repaired here with a demonstrated failing input printed by this script.

**`SS-00-DF-02` -- a goal id reused across epics was silently COLLAPSED into one
census row.** `distinct_goals` keyed on the goal id alone and `setdefault` kept
the first plan walked. Two epics declaring the same id with two different
baselines became one row, it was undefined which baseline that row reported,
and the distinct-goal line read **one fewer goal than the plans declare**. The
direction is why it matters: a collision SHRINKS the denominator, which INFLATES
the compliance rate this instrument exists to compute. Repaired by keying on the
DECLARED `(workflow, goal id)` pair -- `status.workflow`, falling back to
`epic.id` -- and by reporting a reused id as its own verdict class,
`id-collision`, rather than resolving it. The census never resolves a collision;
it names it and leaves it to a human.

**`SS-00-DF-03` -- the judged-instrument recogniser was a KEYWORD MATCHER over
harness prose.** `JUDGED = re.compile("scorecard|score_tools|rubric|card|judge|
D[1-5]")` was run over `statement + metric + harness + target`, so a goal decided
by a shell command that happens to *read* sealed cards was counted as a judged
goal. All five of this epic's goals declare COMMAND harnesses and four of the
five were classified judged, on words like `card` and `sealed` appearing in a
description of what the command reads. That is `CA-08-DF-01` from the other
side: there a recogniser bound by sentence form reached nothing, here one bound
by vocabulary reached too much. Repaired by classifying on the DECLARED `kind`
field, whose meanings are fixed by
`git-epic-workflow/references/goals-and-evaluation.md` ("Goal kinds"):
`eval` is the judged/scored kind, `quality`/`perf`/`integration` each name a
deciding command. A goal that declares no recognised `kind` is **UNDECIDED** --
never PASS, never a confident classification, per `r1_now_requires_an_absent_input`.

The retired keyword recogniser is kept as `keyword_judged()` and reported as a
DIAGNOSTIC beside the declared answer, never as the answer, so that every goal
where the two disagree is on the record by name instead of inside the number.
"""

from __future__ import annotations

import copy
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

#: RETIRED as a classifier, kept as a diagnostic. This is `SS-00-DF-03`: it is a
#: keyword matcher over harness PROSE, and it decides nothing here any more.
#: `keyword_judged()` is the only caller and its result is printed beside the
#: declared answer so the disagreement is visible rather than absorbed.
JUDGED = re.compile(r"scorecard|score_tools|rubric|card|judge|\bD[1-5]\b", re.IGNORECASE)

#: The DECLARED classifier (`SS-00-DF-03`'s repair). `kind` is a required field
#: of the plan schema and its four values are defined by
#: `goals-and-evaluation.md`: `eval` is "judged against a fixed artifact set ...
#: for a judged instrument, a pinned rubric version and a stated judging setup",
#: while `quality` is "an invariant/coverage/robustness property with a deciding
#: command", `perf` "needs a baseline run", and `integration` names a graph.
#: Anything else -- absent, empty, misspelled, a kind this table does not know --
#: is UNDECIDED. Adding a value here is a schema decision, not a tuning knob.
DECLARED_KIND = {
    "eval": "judged",
    "quality": "command",
    "perf": "command",
    "integration": "command",
}

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

#: ADDITIVE, and it is NOT a compliant goal. `R-H4` seals `specs/.history`, and
#: every judged goal in this record is declared in a sealed plan, so the only
#: way to point one at its exact cards without editing history is to say so
#: BESIDE the record. An index entry is SS-03's assertion about which cards
#: produced somebody else's sealed number; a compliant goal is the epic that
#: wrote the number saying so itself. The two are reported as different verdict
#: classes and are never added together.
INDEX_PATH = (
    "specs/results/scorecards/stabilize-substrate/GOAL-judged-goals-compliant/"
    "baseline_resolution_index.yaml"
)


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


def _walk_plans(root: Path) -> tuple[list[tuple[Path, dict]], list[tuple[Path, str]]]:
    """(plans that parsed, plans that did NOT) -- both returned, neither hidden.

    `specs/.history` is hidden, so `glob('specs/**')` misses all of it and sees
    4 goals instead of 27. os.walk, for the reason SV-06 gives.

    `SS-03-DF-02`, FOUND BY COMMITTING IT. This used to `continue` on any parse
    failure. SS-03 broke the LIVE plan with an unquoted `: ` inside an evidence
    string, and the census reported 31 goals where 36 exist -- five goals gone,
    no warning, no error, no line saying a plan had been skipped. That is
    `SS-00-DF-02`'s direction exactly: an unreadable plan SHRINKS the
    denominator, which INFLATES the compliance rate this instrument computes.
    A parse failure is now counted, named and printed.
    """
    plans: list[tuple[Path, dict]] = []
    unreadable: list[tuple[Path, str]] = []
    for dirpath, _dirs, files in os.walk(root / "specs"):
        if "ticket_plan.yaml" not in files:
            continue
        path = Path(dirpath, "ticket_plan.yaml")
        try:
            plan = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:  # reported, never raised -- this is not a gate
            first = str(exc).splitlines()[0] if str(exc) else ""
            unreadable.append((path, f"{type(exc).__name__}: {first[:120]}"))
            continue
        if isinstance(plan, dict):
            plans.append((path, plan))
        else:
            unreadable.append((path, f"parsed to {type(plan).__name__}, not a mapping"))
    return plans, unreadable


def every_plan(root: Path) -> list[tuple[Path, dict]]:
    """Every plan on disk that parses. `unreadable_plans` has the rest."""
    return _walk_plans(root)[0]


def unreadable_plans(root: Path) -> list[tuple[Path, str]]:
    """Every `ticket_plan.yaml` this instrument could NOT read, with the reason.

    A census that drops a plan is reporting a smaller population than the record
    holds, and until `SS-03` it did that in silence.
    """
    return _walk_plans(root)[1]


def plan_workflow(plan: dict) -> str:
    """The workflow a plan DECLARES it belongs to. `SS-00-DF-02`.

    `status.workflow` is the field every plan in this record carries; `epic.id`
    is the fallback. A plan that declares neither is `UNDECLARED` -- which is a
    key like any other, so its goals are still counted and can still collide.
    Never inferred from the path: a snapshot can be filed under one epic's
    history directory and belong to another's workflow.
    """
    status = plan.get("status")
    if isinstance(status, dict) and status.get("workflow"):
        return str(status["workflow"])
    epic = plan.get("epic")
    if isinstance(epic, dict) and epic.get("id"):
        return str(epic["id"])
    return "UNDECLARED"


def distinct_goals(plans: list[tuple[Path, dict]]) -> dict[tuple[str, str], dict]:
    """Every declared goal, keyed on `(workflow, goal id)`. `SS-00-DF-02`.

    Keying on the id alone collapsed two epics' goals into one row and reported
    a SMALLER denominator than the plans declare. The pair cannot do that: the
    same id in two workflows is two rows, and `id_collisions` names it.
    """
    goals: dict[tuple[str, str], dict] = {}
    for _path, plan in plans:
        workflow = plan_workflow(plan)
        for goal in plan.get("epic_goals") or []:
            if isinstance(goal, dict) and "id" in goal:
                goals.setdefault((workflow, str(goal["id"])), goal)
    return goals


def id_collisions(goals: dict[tuple[str, str], dict]) -> dict[str, list[str]]:
    """Goal ids declared by more than one workflow -- reported, never resolved.

    `goals-and-evaluation.md`'s plan schema says an id is "stable, never reused,
    never renamed", so a reused id is a violation of the schema and not a thing
    for a census to paper over. It is undefined which baseline a collapsed row
    would report, so this instrument reports neither and names both workflows.
    """
    seen: dict[str, list[str]] = {}
    for workflow, gid in goals:
        seen.setdefault(gid, []).append(workflow)
    return {gid: sorted(wfs) for gid, wfs in seen.items() if len(wfs) > 1}


def keyword_judged(goal: dict) -> bool:
    """The RETIRED recogniser. Diagnostic only -- `SS-00-DF-03`.

    Kept so that every goal where prose and declared data disagree can be named
    in the report. Nothing in `classify` calls it.
    """
    text = " ".join(str(goal.get(k, "")) for k in ("statement", "metric", "harness", "target"))
    return bool(JUDGED.search(text))


def instrument_kind(goal: dict) -> tuple[str, str]:
    """('judged' | 'command' | 'undecided', why) from the DECLARED `kind` field.

    `SS-00-DF-03`'s repair. No prose is read. A goal that declares no recognised
    kind is UNDECIDED: the correct answer to an input that cannot be classified
    from declared data is a refusal to classify, never a confident answer in
    either direction (`r1_now_requires_an_absent_input`).
    """
    raw = goal.get("kind")
    key = str(raw).strip().lower() if raw is not None else ""
    if key in DECLARED_KIND:
        which = DECLARED_KIND[key]
        if which == "judged":
            return "judged", f"declared kind '{key}' -- the judged/scored kind, so the card rule applies"
        return "command", (
            f"declared kind '{key}' names a deciding command (goals-and-evaluation.md, 'Goal kinds') "
            "-- the card rule does not apply, and that is legal"
        )
    shown = repr(raw) if raw is not None else "absent"
    return "undecided", (
        f"kind is {shown}: not one of {sorted(DECLARED_KIND)} -- this instrument cannot classify "
        "the harness from declared data and refuses to guess from prose (SS-00-DF-03)"
    )


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


def load_index(root: Path) -> dict[tuple[str, str], dict]:
    """The additive resolution index, keyed like the census. Absent is legal."""
    path = root / INDEX_PATH
    if not path.is_file():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(data, dict):
        return {}
    out: dict[tuple[str, str], dict] = {}
    for entry in data.get("entries") or []:
        if isinstance(entry, dict) and entry.get("workflow") and entry.get("goal"):
            out[(str(entry["workflow"]), str(entry["goal"]))] = entry
    return out


def classify(
    root: Path,
    goal: dict,
    workflow: str | None = None,
    index: dict[tuple[str, str], dict] | None = None,
) -> tuple[str, str]:
    """(verdict, why) for one goal's baseline. NEVER raises, never refuses."""
    kind, why_kind = instrument_kind(goal)
    if kind == "command":
        return "not-judged", why_kind
    if kind == "undecided":
        return "undecided", why_kind

    baseline = goal.get("baseline") or {}
    evidence = str(baseline.get("evidence", "") or "").strip()
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

    entry = (index or {}).get((str(workflow), str(goal.get("id"))))
    if entry:
        listed = [str(c) for c in (entry.get("cards") or [])]
        present = [c for c in listed if (root / c).is_file() and Path(c).name == "scorecard.json"]
        if listed and len(present) == len(listed):
            return "card-via-index", (
                f"{len(present)} card(s) named by {INDEX_PATH}, NOT by the goal: "
                f"{', '.join(present[:3])}{' ...' if len(present) > 3 else ''}"
            )

    if dirs:
        return "directory", f"a directory, not a card: {dirs[0]} (contains {len(list((root / dirs[0]).rglob('scorecard.json')))} cards; the goal does not say which)"
    if files:
        return "summary", f"a document, not a card: {files[0]}"
    if missing:
        return "unresolvable", f"path-shaped but does not resolve at this tree: {missing[0]}"
    return "prose", f"no path at all: {evidence[:70]!r}"


#: The six classes of the `0 of 20` baseline are the first six and are
#: comparable line for line (clause (d)). `card-via-index`, `undecided` and
#: `id-collision` are SS-03's additions and are reported separately by name --
#: `card-via-index` is never added to `card`.
VERDICTS = (
    "card", "directory", "summary", "unresolvable", "prose", "no-evidence", "not-judged",
    "card-via-index", "undecided", "id-collision",
)
BASELINE_VERDICTS = ("card", "directory", "summary", "unresolvable", "prose", "no-evidence")


def census(root: Path, goals: dict[tuple[str, str], dict], index: dict | None = None) -> dict[tuple[str, str], tuple[str, str]]:
    """Classify every goal, then OVERRIDE colliding ids to `id-collision`.

    A collision is decided over the population, not over one goal, which is why
    it cannot live inside `classify`. `SS-00-DF-02`.
    """
    collisions = id_collisions(goals)
    out: dict[tuple[str, str], tuple[str, str]] = {}
    for (workflow, gid), goal in goals.items():
        if gid in collisions:
            out[(workflow, gid)] = (
                "id-collision",
                f"id declared by {len(collisions[gid])} workflows {collisions[gid]} -- "
                "two baselines, one id; this census names it and resolves nothing (SS-00-DF-02)",
            )
            continue
        out[(workflow, gid)] = classify(root, goal, workflow, index)
    return out


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


def _bucket(verdicts: dict[tuple[str, str], tuple[str, str]]) -> dict[str, list[tuple[tuple[str, str], str]]]:
    buckets: dict[str, list[tuple[tuple[str, str], str]]] = {v: [] for v in VERDICTS}
    for key, (verdict, why) in sorted(verdicts.items()):
        buckets.setdefault(verdict, []).append((key, why))
    return buckets


def main() -> int:
    root = repo_root()
    print(f"tree: {tree(root)}   (every figure below is about THIS tree)")
    print()

    plans = every_plan(root)
    goals = distinct_goals(plans)
    index = load_index(root)
    cards_on_disk = list((root / "specs" / "results" / "scorecards").rglob("scorecard.json"))
    collisions = id_collisions(goals)

    unreadable = unreadable_plans(root)

    print("## The population")
    print(f"plans on disk (live + sealed)                              : {len(plans)}")
    print(f"plans that DID NOT PARSE and were dropped (SS-03-DF-02)    : {len(unreadable)}")
    for path, why in unreadable:
        print(f"    {path.relative_to(root)}  {why}")
    print(f"distinct epic goals, keyed (workflow, id)                  : {len(goals)}")
    print(f"distinct goal IDS, ignoring workflow (the OLD key)         : {len({gid for _wf, gid in goals})}")
    print(f"goal ids declared by more than one workflow (COLLISION)    : {len(collisions)}")
    for gid, wfs in sorted(collisions.items()):
        print(f"    {gid:<38} {wfs}")
    print(f"sealed scorecard.json files under specs/results/scorecards : {len(cards_on_disk)}")
    print(f"resolution-index entries (ADDITIVE, not compliant goals)   : {len(index)}")
    print("cross-check against SV-06 at 5620c9a: 27 goals, 87 cards, 0 card-backed.")
    print("SS-00-DF-02: the two goal counts above MUST NOT DIFFER SILENTLY. When they do,")
    print("the old key was reporting FEWER goals than the plans declare, which shrinks the")
    print("denominator below and INFLATES every compliance rate computed from it.")
    print()

    verdicts = census(root, goals, index)
    buckets = _bucket(verdicts)

    print("## Can the evaluation ticket open the baseline card?")
    for verdict in VERDICTS:
        note = ""
        if verdict == "card-via-index":
            note = "   <- SS-03's assertion, NOT the goal's; never added to `card`"
        if verdict == "undecided":
            note = "   <- kind not declared: refused rather than guessed"
        if verdict == "id-collision":
            note = "   <- reported, never resolved"
        print(f"{verdict:>14} : {len(buckets[verdict])}{note}")
    judged_total = sum(len(buckets[v]) for v in BASELINE_VERDICTS) + len(buckets["card-via-index"])
    print()
    print(f"JUDGED GOALS (declared kind: eval)                    : {judged_total}")
    print(f"  of which the evaluation can re-open FROM THE GOAL   : {len(buckets['card'])}")
    print(f"  of which only the additive index can locate         : {len(buckets['card-via-index'])}")
    print(f"COMMAND GOALS (declared kind: quality/perf/integration): {len(buckets['not-judged'])}")
    print(f"  of which baseline.evidence resolves to a re-readable file:"
          f" {sum(1 for (wf, gid), g in goals.items() if verdicts[(wf, gid)][0] == 'not-judged' and _resolves_to_file(root, g))}")
    print()
    for verdict in VERDICTS:
        if not buckets[verdict]:
            continue
        print(f"### {verdict}")
        for (workflow, gid), why in buckets[verdict]:
            print(f"  {gid:<38} [{workflow}] {why}")
        print()

    print("## SS-00-DF-03: where the RETIRED keyword recogniser disagrees with declared data")
    print("Reported by name so the residual risk is on the record instead of inside the number.")
    print("Nothing below changes a verdict; `keyword_judged` decides nothing.")
    over = [(wf, gid) for (wf, gid), g in sorted(goals.items())
            if keyword_judged(g) and instrument_kind(g)[0] != "judged"]
    under = [(wf, gid) for (wf, gid), g in sorted(goals.items())
             if not keyword_judged(g) and instrument_kind(g)[0] == "judged"]
    print(f"  prose says judged, declared kind says COMMAND (over-reach) : {len(over)}")
    for wf, gid in over:
        print(f"      {gid:<38} [{wf}]")
    print(f"  prose says not judged, declared kind says JUDGED (under-reach) : {len(under)}")
    for wf, gid in under:
        print(f"      {gid:<38} [{wf}]")
    print(f"  keyword recogniser would have counted {sum(1 for g in goals.values() if keyword_judged(g))} judged goals;"
          f" declared data counts {judged_total}.")
    print()

    print("## The R1 failing input, on a real epic plan")
    print("SS-03 MOVED THIS DEMONSTRATION AND SAYS WHICH. The original subject,")
    print("GOAL-loop-reaches-the-program, was read out of the LIVE plan; the live plan is now")
    print("stabilize-substrate's and the subject raised KeyError. It did not vanish -- it is")
    print("still declared, sealed and unedited, in score-drives-validation-epic's plans. The")
    print("demonstration now reads the whole record keyed by (workflow, id), which is the")
    print("repair for the fragility as well as for SS-00-DF-02.")
    subject = goals.get(("score-drives-validation-epic", "GOAL-loop-reaches-the-program"))
    if subject is None:
        print("  ABSENT at this tree -- report that rather than substituting another goal.")
    else:
        verdict, why = verdicts[("score-drives-validation-epic", "GOAL-loop-reaches-the-program")]
        evidence = str((subject.get("baseline") or {}).get("evidence", ""))
        print(f"  baseline.evidence : {evidence}")
        print(f"  verdict           : {verdict}")
        print(f"  why               : {why}")
        print("  FAILING: the evaluation ticket cannot re-read the number. It is handed a")
        print("  folder and would have to pick a card out of it, which is the exact move")
        print("  goals-and-evaluation.md's judged-baseline paragraph already forbids.")
    print()

    print("## SS-00-DF-02, demonstrated on the real record")
    print("The kickoff's first plan draft reused the predecessor's id and was never committed,")
    print("so the subject is RECONSTRUCTED over the WHOLE REAL RECORD: every plan on disk is")
    print("walked as-is, and the live plan's GOAL-four-results-still-stand is renamed back to")
    print("the predecessor's GOAL-four-results-stand -- the one rename the kickoff made and")
    print("then backed out. Nothing on disk is touched; the rename happens in memory.")
    live = [(p, plan) for p, plan in plans if plan_workflow(plan) == "stabilize-substrate-epic"]
    if live:
        renamed = 0
        drafted: list[tuple[Path, dict]] = []
        for path, plan in plans:
            if plan_workflow(plan) != "stabilize-substrate-epic":
                drafted.append((path, plan))
                continue
            draft = copy.deepcopy(plan)
            for goal in draft.get("epic_goals") or []:
                if isinstance(goal, dict) and goal.get("id") == "GOAL-four-results-still-stand":
                    goal["id"] = "GOAL-four-results-stand"
                    goal.pop("continues", None)
                    renamed += 1
            drafted.append((path, draft))
        new = distinct_goals(drafted)
        old_key = len({gid for _wf, gid in new})
        print(f"  ids renamed in the in-memory draft                 : {renamed}")
        print(f"  OLD key (id alone)  -> distinct goals              : {old_key}")
        print(f"  NEW key (workflow, id) -> distinct goals           : {len(new)}")
        print(f"  collisions named rather than collapsed             : {sorted(id_collisions(new))}")
        print("  The kickoff measured exactly this: 35 where 36 goals exist, with no warning,")
        print("  no refusal and no ambiguity line. The old key reports a SMALLER denominator;")
        print("  the new key cannot report fewer goals than the plans declare.")
    else:
        print("  UNAVAILABLE: this tree does not carry the live plan -- report that, do not fake it.")
    print()

    print("## Population baselines -- where SV-06's proposed wording does not fit")
    print("SV-06 proposed: 'baseline.evidence is the path to the SINGLE sealed card that")
    print("produced the number'. Some real baselines are figures over MANY cards, and no")
    print("single card produced them. Those goals cannot comply with that wording at all.")
    pop = [
        (gid, str((g.get("baseline") or {}).get("value", ""))[:90])
        for (_wf, gid), g in sorted(goals.items())
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
    print(f"  a goal with every field empty                -> {classify(root, empty)[0]}: {classify(root, empty)[1]}")
    prose_only = dict(unjudged, kind="quality", harness="scored against the card by two blind judges")
    print(f"  a COMMAND-kind goal whose prose says 'card'  -> {classify(root, prose_only)[0]} (prose decides nothing)")
    mystery = dict(unjudged, kind="vibes")
    print(f"  a goal whose kind is not in the schema       -> {classify(root, mystery)[0]}: {classify(root, mystery)[1]}")
    noworkflow = {"epic_goals": [{"id": "GOAL-x", "kind": "eval"}]}
    print(f"  a plan that declares no workflow             -> keyed {sorted(distinct_goals([(Path('x'), noworkflow)]))} (counted, never dropped)")
    print()
    print("REFUSES NOTHING: this exits 0 on every input above, including the failing one.")
    return 0


def _resolves_to_file(root: Path, goal: dict) -> bool:
    """Does this goal's evidence resolve to a file an evaluation can re-open?

    For a COMMAND goal the compliant artifact is the sealed raw output of the
    command, not a card -- `GOAL-judged-goals-compliant` clause (a).
    """
    evidence = str((goal.get("baseline") or {}).get("evidence", "") or "")
    return any((root / t).is_file() for t in candidate_paths(evidence))


if __name__ == "__main__":
    raise SystemExit(main())
