"""SV-03. THE THIRD BRANCH: a judged baseline the evaluation ticket can re-open.

`git-epic-workflow/references/goals-and-evaluation.md` has two baseline
branches -- *harness exists* and *harness does not*. A judged instrument that
exists but has never been run on THIS subject falls between them, so an epic in
that position has no branch to follow. SV-06 measured what following no branch
looks like: **0 of 27 goals in this repository cite a sealed card**, against 87
sealed cards on disk.

SV-03 proposes the missing branch as four diffs against three skill files and
**escalates them rather than applying them** -- skills are READ from this
repository, never edited. The diffs are checked in under
`specs/results/scorecards/score-drives-validation/GOAL-scored-at-goal-time/SV-03/proposed-skill-diffs/`
and this file is what makes them more than a suggestion.

WHAT IS PINNED HERE, AND WHY EACH ONE CAN GO RED
------------------------------------------------
1. **The worked example is real.** Its `baseline.evidence` resolves to sealed
   cards that parse and carry the numbers its `baseline.value` claims. If a
   card moves or the prose drifts from the card, this goes red -- which is the
   entire property the third branch exists to create.
2. **Both loaders.** `yaml.safe_load` and
   `scripts/extract_spec_manifest.parse_simple_yaml` must agree exactly, on the
   example and on the no-card plan. A plan one loader accepts and the other
   does not is this repository's recorded silent failure (SF-004, SF-007).
3. **R1 -- THE DEMONSTRATED FAILING INPUT IS A REAL EPIC PLAN, NOT A FIXTURE.**
   `GOAL-loop-reaches-the-program` in `specs/desired_program_model/ticket_plan.yaml`
   cites a directory that holds **zero** sealed cards. Its baseline was sealed
   at `eab2883` and is never edited, so this is a stable subject rather than a
   moving one.
4. **Fail open.** A command harness, an empty goal and a plan with no goals are
   all classified and passed over. Nothing here refuses anything: the
   classifier has no failing exit path at all, is imported by nothing in
   `scripts/`, and is wired into no validator, no close-out and no gate.
5. **Absence is designed for, structurally.** Every block the four diffs add
   opens with a conditional a project without a card does not satisfy. The
   check that says so is shown FAILING on an unguarded block, so it cannot pass
   vacuously.
6. **Zero bytes to `serve`.** No proposed diff touches
   `references/eval_scorecard.md` or any file this repository ships.

WHAT IS DELIBERATELY NOT HERE
-----------------------------
**No test asserts that any goal complies.** The 0-of-27 is an argument for a
sentence, not for a checker (`no_new_gates_rule`, and seven epics of static
checking that caught zero bugs). A test that failed until every plan cited a
card would be the eighth gate, and it would be a gate on the epic owner's
prose.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

TICKET = (
    REPO_ROOT
    / "specs/results/scorecards/score-drives-validation"
    / "GOAL-scored-at-goal-time/SV-03"
)
EXAMPLE = TICKET / "example_goal.yaml"
NO_CARD_PLAN = TICKET / "no_card_plan.yaml"
DIFFS = TICKET / "proposed-skill-diffs"
CLASSIFIER = TICKET / "analysis/baseline_is_a_card.py"
NO_CARD_DEMO = TICKET / "analysis/no_card_project_unaffected.py"
LIVE_PLAN = REPO_ROOT / "specs/desired_program_model/ticket_plan.yaml"

#: The three files the proposal touches, and the only ones it may touch.
PROPOSED_FILES = {
    "01-git-epic-workflow-goals-and-evaluation-third-branch.patch": "references/goals-and-evaluation.md",
    "02-git-epic-workflow-goals-and-evaluation-evidence-is-a-card.patch": "references/goals-and-evaluation.md",
    "03-git-issue-workflow-goal-signal-subtraction.patch": "references/goal-signal.md",
    "04-git-issue-regression-close-loop-outlet.patch": "references/regression-close.md",
}

yaml = pytest.importorskip(
    "yaml",
    reason="PyYAML is not a runtime dependency; run with `uv run --with pyyaml` to enforce",
)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def classifier():
    return _load(CLASSIFIER, "sv03_baseline_is_a_card")


@pytest.fixture(scope="module")
def demo():
    return _load(NO_CARD_DEMO, "sv03_no_card_project_unaffected")


# ---------------------------------------------------------------------------
# 1. the worked example is a card, and the card says what the goal says
# ---------------------------------------------------------------------------


def test_the_worked_example_baseline_resolves_to_sealed_cards(classifier):
    """A baseline that IS a card: the evaluation ticket can open it.

    This is the property the third branch buys, asserted rather than described.
    """
    goals = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))["epic_goals"]
    judged = goals[0]
    verdict, why = classifier.classify(REPO_ROOT, judged)
    assert verdict == "card", why

    paths = classifier.candidate_paths(judged["baseline"]["evidence"])
    assert len(paths) == 2, paths
    for token in paths:
        card = REPO_ROOT / token
        assert card.is_file() and card.name == "scorecard.json", token
        data = json.loads(card.read_text(encoding="utf-8"))
        assert data["dimensions"]["D3"]["score"] == 4, (
            f"{token} no longer carries the D3 the example's baseline.value claims -- "
            "fix the prose to match the card, never the card to match the prose")
        assert data["rubric"]["digest"] == "sha256:497c16ca85adeb4a", token


def test_the_examples_prose_number_is_the_cards_number(classifier):
    """`R-H4`: the seal is what makes a baseline unable to drift.

    The number in `baseline.value` and the digest it names are both checked
    against the bytes on disk. A card that is re-scored under a new rubric gets
    a new file; this pair may not silently become a different measurement.
    """
    judged = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))["epic_goals"][0]
    assert "D3 = 4 and 4" in judged["baseline"]["value"]
    assert "sha256:497c16ca85adeb4a" in judged["baseline"]["value"]
    assert judged["baseline"]["measured_at"] == "a73186d"
    for token in classifier.candidate_paths(judged["baseline"]["evidence"]):
        data = json.loads((REPO_ROOT / token).read_text(encoding="utf-8"))
        assert data["commit"] == "a73186d", token


def test_the_example_adds_no_field_to_the_plan_schema():
    """`SV-06` section 8: cheap to add is not a reason to add.

    Every key in the worked example already exists. A `dimension:` field in
    particular is REFUSED: a dimension id indexes one project's rubric, and the
    keying lives in the free-text `metric` where 12 of 27 goals already put it.
    """
    allowed = {"id", "kind", "statement", "metric", "harness", "baseline",
               "target", "evaluation_ticket", "evidence_root"}
    for goal in yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))["epic_goals"]:
        assert set(goal) <= allowed, set(goal) - allowed
        assert set(goal["baseline"]) <= {"value", "measured_at", "evidence"}
        assert "dimension" not in goal
    assert "D3" in yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))["epic_goals"][0]["metric"]


# ---------------------------------------------------------------------------
# 2. both loaders
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("path", [EXAMPLE, NO_CARD_PLAN], ids=lambda p: p.name)
def test_loads_identically_with_both_loaders(path: Path):
    from scripts.extract_spec_manifest import parse_simple_yaml

    text = path.read_text(encoding="utf-8")
    assert yaml.safe_load(text) == parse_simple_yaml(text)


# ---------------------------------------------------------------------------
# 3. R1 -- the demonstrated failing input, on a real epic plan
# ---------------------------------------------------------------------------


def test_a_real_epic_plans_judged_baseline_cannot_be_re_opened(classifier):
    """R1. THE SUBJECT IS REAL AND ITS BASELINE IS SEALED.

    `GOAL-loop-reaches-the-program` cites `specs/results/scorecards/close-the-loop/`.
    That directory holds ZERO `scorecard.json` files -- the CL-03 cards are in
    two sibling directories -- so the evaluation ticket is handed a folder it
    cannot pick a card out of, and there is no card in it to pick.

    If this ever goes green, the baseline was edited after the fact. Move the
    demonstration to another failing goal and say which; do not delete it.
    """
    goals = {g["id"]: g for g in
             yaml.safe_load(LIVE_PLAN.read_text(encoding="utf-8"))["epic_goals"]}
    goal = goals["GOAL-loop-reaches-the-program"]
    verdict, why = classifier.classify(REPO_ROOT, goal)
    assert verdict == "directory", why
    cited = REPO_ROOT / "specs/results/scorecards/close-the-loop"
    assert cited.is_dir()
    assert list(cited.rglob("scorecard.json")) == [], (
        "the cited directory has acquired cards; the demonstration needs restating")


def test_no_goal_in_the_whole_record_has_a_re_openable_baseline(classifier):
    """The measurement behind the proposal, over every plan on disk.

    Reported as a COUNT and never as a gate. The denominator is the judged
    goals, not all goals: 9 of the 27 name no judged instrument and the rule
    does not apply to them, which is a correction to SV-06's 0-of-27 framing
    rather than a disagreement with its numerator.
    """
    plans = classifier.every_plan(REPO_ROOT)
    goals = classifier.distinct_goals(plans)
    verdicts = {gid: classifier.classify(REPO_ROOT, g)[0] for gid, g in goals.items()}
    judged = {gid: v for gid, v in verdicts.items() if v != "not-judged"}
    assert len(goals) >= 27, len(goals)
    assert judged, "a record with no judged goal would make this vacuous"
    assert sum(v == "card" for v in judged.values()) == 0, (
        "a goal now cites a sealed card -- update the figure this ticket reports, "
        f"and say which goal did it: {[g for g, v in judged.items() if v == 'card']}")


def test_the_classifier_never_raises_on_the_real_record(classifier):
    """Fail open on real input, not only on the three synthetic shapes below."""
    for goal in classifier.distinct_goals(classifier.every_plan(REPO_ROOT)).values():
        verdict, why = classifier.classify(REPO_ROOT, goal)
        assert verdict in classifier.VERDICTS
        assert why


# ---------------------------------------------------------------------------
# 4. fail open: the card is never mandatory
# ---------------------------------------------------------------------------


def test_a_goal_with_a_command_harness_is_out_of_scope(classifier):
    goal = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))["epic_goals"][1]
    verdict, _why = classifier.classify(REPO_ROOT, goal)
    assert verdict == "not-judged"


def test_an_empty_goal_and_an_empty_plan_are_legal(classifier):
    assert classifier.classify(REPO_ROOT, {})[0] == "not-judged"
    assert classifier.distinct_goals([(Path("x"), {"epic_goals": [], "goals_waived": "no delta"})]) == {}


def test_the_classifier_has_no_failing_exit_path(classifier):
    """No gate: it cannot refuse anything, so nothing can be blocked on it."""
    source = CLASSIFIER.read_text(encoding="utf-8")
    assert "return 1" not in source
    assert "sys.exit(1)" not in source
    assert source.count("raise SystemExit(main())") == 1


def test_nothing_shipped_consults_either_analysis_script():
    """A measurement nothing reads cannot become a gate by accident."""
    for name in ("baseline_is_a_card", "no_card_project_unaffected"):
        for path in sorted((REPO_ROOT / "scripts").glob("*.py")):
            assert name not in path.read_text(encoding="utf-8"), f"{path} reads {name}"


def test_the_no_card_plan_is_a_complete_epic_with_no_card_anywhere():
    text = NO_CARD_PLAN.read_text(encoding="utf-8")
    plan = yaml.safe_load(text)
    body = yaml.safe_dump(plan)
    for term in ("scorecard", "rubric", "judge", "score_tools"):
        assert term not in body.lower(), term
    assert len(plan["epic_goals"]) == 2 and len(plan["tickets"]) == 2


# ---------------------------------------------------------------------------
# 5. the proposed diffs: guarded, bounded, and escalated rather than applied
# ---------------------------------------------------------------------------


def test_every_proposed_diff_touches_only_its_named_file():
    assert {p.name for p in DIFFS.glob("*.patch")} == set(PROPOSED_FILES)
    for name, target in PROPOSED_FILES.items():
        text = (DIFFS / name).read_text(encoding="utf-8")
        headers = [l for l in text.splitlines() if l.startswith("diff --git")]
        assert headers == [f"diff --git a/{target} b/{target}"], headers


def test_no_proposed_diff_touches_anything_this_repository_ships():
    """0 bytes to `serve`, and no production file anywhere.

    The served surface is 6,281 bytes at 9 rungs and this ticket's whole
    proposal is prose in three skill files it does not own.
    """
    for path in sorted(DIFFS.glob("*.patch")):
        text = path.read_text(encoding="utf-8")
        for forbidden in ("eval_scorecard.md", "score_tools.py", "scripts/", ".py\n"):
            assert forbidden not in text, (path.name, forbidden)


def test_every_added_block_is_inside_a_conditional(demo):
    """Absence designed for, mechanically.

    A project with no card must not be handed one new obligation. Each block
    the diffs add has to OPEN with a conditional such a project fails.
    """
    seen = 0
    for path in sorted(DIFFS.glob("*.patch")):
        blocks = demo.added_blocks(path)
        assert blocks, path.name
        for block in blocks:
            opening = demo.plain(" ".join(l for l in block if l.strip()))
            assert demo.GUARDS.match(opening), (path.name, opening[:80])
            seen += 1
    assert seen >= 4, seen


def test_the_guard_check_FAILS_on_an_unguarded_block(demo):
    """Non-vacuity, and this check's own demonstrated failing input.

    A guard scan that passes whatever it is handed is worth nothing. This is
    the sentence that would make the card mandatory, and the check refuses it.
    """
    unguarded = "Every epic goal names a scorecard dimension and a sealed card."
    assert not demo.GUARDS.match(demo.plain(unguarded))
    assert demo.GUARDS.match(demo.plain("**For a judged goal**, name the card."))


def test_the_diffs_are_escalated_not_applied():
    """Skills are READ from this repository and never edited.

    The proposal exists here as patch files. The installed home is not touched
    by anything in this ticket, and no test in this file writes to it.
    """
    assert DIFFS.is_dir() and list(DIFFS.glob("*.patch"))
    escalation = TICKET / "ESCALATION.md"
    assert escalation.is_file()
    body = escalation.read_text(encoding="utf-8")
    assert "skill-manager sync" in body, "the escalation must say what must NOT be run"


# ---------------------------------------------------------------------------
# 6. the demonstrations, executed -- so the acceptance command runs them
# ---------------------------------------------------------------------------


def test_the_classifier_runs_over_the_real_record_and_exits_zero():
    out = subprocess.run(
        ["uv", "run", "--with", "pyyaml", sys.executable, str(CLASSIFIER)],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert out.returncode == 0, out.stderr[-2000:]
    assert "The R1 failing input, on a real epic plan" in out.stdout
    assert "REFUSES NOTHING" in out.stdout
