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
prose. **`SS-03` kept that rule**: it repointed this epic's own five goals at
their sealed raw command output and wrote **no test asserting that they are
compliant**.

WHAT `SS-03` CHANGED HERE, AND WHY
----------------------------------
Section 7 carries the two kickoff defects `SS-00-DF-02` and `SS-00-DF-03`, each
with a demonstrated failing input on a real subject, plus the absent-input case
`r1_now_requires_an_absent_input` demands. Neither repair refuses anything and
the classifier still has no failing exit path.

**Section 3's `R1` subject moved, and this file says where.** The demonstration
read the goal out of the LIVE plan by id. When this epic's plan became the live
plan the lookup raised `KeyError: 'GOAL-loop-reaches-the-program'` -- an
exception, not a red assertion, so a test whose whole job is to hold a failing
input on the record reported its subject's absence as a crash. **The subject did
not move; the live plan did.** `GOAL-loop-reaches-the-program` is still declared,
sealed and unedited in `score-drives-validation-epic`'s plans under
`specs/.history`, still verdict `directory`, still citing a folder with zero
cards. The demonstration now reads the WHOLE record keyed by `(workflow, id)`,
which pins the subject where it actually lives. Filed as `SS-03-DF-01`: a test
that pins an `R1` subject by live-plan lookup loses it at every epic rollover,
and loses it as an error rather than as a finding.
"""

from __future__ import annotations

import copy
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

    SS-03 MOVED IT AND SAYS WHERE. It did not go green -- it raised KeyError,
    because it read the subject out of `LIVE_PLAN` and the live plan rolled over
    to `stabilize-substrate`'s. The subject is unchanged and unedited; it is read
    here from the WHOLE record, keyed `(workflow, id)`, which is where it lives.

    The verdict is taken FROM THE GOAL ALONE -- no resolution index -- because
    that is the property the third branch is about: *given only the goal*, can
    you open the card? SS-03's additive index can locate these cards; it is
    reported as `card-via-index` and it does not make this goal compliant.
    """
    goals = classifier.distinct_goals(classifier.every_plan(REPO_ROOT))
    goal = goals[("score-drives-validation-epic", "GOAL-loop-reaches-the-program")]
    verdict, why = classifier.classify(REPO_ROOT, goal)
    assert verdict == "directory", why
    cited = REPO_ROOT / "specs/results/scorecards/close-the-loop"
    assert cited.is_dir()
    assert list(cited.rglob("scorecard.json")) == [], (
        "the cited directory has acquired cards; the demonstration needs restating")


def test_no_goal_in_the_whole_record_has_a_re_openable_baseline(classifier):
    """The measurement behind the proposal, over every plan on disk.

    Reported as a COUNT and never as a gate. The denominator is the judged
    goals, not all goals: the goals that declare a COMMAND kind name no judged
    instrument and the rule does not apply to them, which is a correction to
    SV-06's 0-of-27 framing rather than a disagreement with its numerator.

    SS-03: the denominator now comes from the DECLARED `kind` field rather than
    from keywords in the harness prose (`SS-00-DF-03`), and `card-via-index` is
    excluded from `card` on purpose -- an index entry is SS-03's assertion about
    a sealed number, not an epic writing a compliant goal, so it may never move
    this numerator.
    """
    plans = classifier.every_plan(REPO_ROOT)
    goals = classifier.distinct_goals(plans)
    verdicts = {k: v for k, (v, _why) in classifier.census(
        REPO_ROOT, goals, classifier.load_index(REPO_ROOT)).items()}
    judged = {k: v for k, v in verdicts.items()
              if v not in ("not-judged", "undecided", "id-collision")}
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
    """SS-03 changed the first assertion, and the change IS the repair.

    An empty goal used to be classified `not-judged` -- a confident answer about
    an input that declared nothing. `r1_now_requires_an_absent_input`: the
    correct answer to an absent input is UNDECIDED, never a pass in either
    direction. `set[str] -> set[str] | None` is the same shape.
    """
    assert classifier.classify(REPO_ROOT, {})[0] == "undecided"
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


# ---------------------------------------------------------------------------
# 7. SS-03 -- the two kickoff defects in this instrument, each with a
#    demonstrated failing input on a real subject, and the absent-input case
# ---------------------------------------------------------------------------


def test_a_reused_goal_id_is_named_and_never_collapsed(classifier):
    """`SS-00-DF-02`, `R1`. The failing input is THIS EPIC'S OWN FIRST DRAFT.

    The kickoff drafted this plan reusing the predecessor's
    `GOAL-four-results-stand`, and the census reported 35 distinct goals where
    36 exist -- no warning, no refusal, no ambiguity line, and undefined which
    of the two baselines the surviving row reported. That draft was never
    committed, so the subject is reconstructed over the WHOLE REAL RECORD by
    renaming exactly the one id the kickoff renamed and then backed out.
    Nothing on disk is touched.

    THE DIRECTION IS THE DEFECT: a collision SHRINKS the denominator, which
    INFLATES the compliance rate this instrument exists to compute.
    """
    plans = classifier.every_plan(REPO_ROOT)
    renamed = 0
    drafted = []
    for path, plan in plans:
        if classifier.plan_workflow(plan) != "stabilize-substrate-epic":
            drafted.append((path, plan))
            continue
        draft = copy.deepcopy(plan)
        for goal in draft.get("epic_goals") or []:
            if goal.get("id") == "GOAL-four-results-still-stand":
                goal["id"] = "GOAL-four-results-stand"
                goal.pop("continues", None)
                renamed += 1
        drafted.append((path, draft))
    # `renamed` GROWS AS TICKETS CLOSE, and pinning it to 1 was this test's own
    # instance of `SS-03-DF-01`. Every `close ticket` writes a snapshot of this
    # epic's plan under `specs/.history`; each snapshot declares the same
    # workflow and carries the same goal, so `renamed` was 1 when SS-03 wrote
    # this line and 2 the moment SS-01 merged. Filed as `SS-03-DF-08`. The
    # demonstration is about the COLLAPSE, not about how many plan files happen
    # to carry the subject, so only the subject's presence is pinned here.
    assert renamed >= 1, "no plan on disk carries this demonstration's subject any more"

    collided = classifier.distinct_goals(drafted)
    old_key = {gid for _wf, gid in collided}
    assert len(old_key) == len(collided) - 1, (
        "the OLD key must lose exactly the collided row -- if it does not, the "
        "demonstration needs restating, not deleting")
    collisions = classifier.id_collisions(collided)
    assert "GOAL-four-results-stand" in collisions, collisions
    assert sorted(collisions["GOAL-four-results-stand"]) == [
        "cut-the-apparatus-epic", "stabilize-substrate-epic"], collisions


def test_the_record_declares_no_reused_goal_id_at_this_tree(classifier):
    """The check `SS-00-DF-02` demanded: is this only about the future?

    Answer at this tree: yes. Zero collisions across every plan on disk, live
    and sealed, so the census's distinct-goal count is not currently understated
    -- and the `continues:` field on `GOAL-four-results-still-stand` is why.
    That field is the workaround the finding forced; this is the instrument that
    makes a future reuse visible instead of silently shrinking a denominator.
    """
    goals = classifier.distinct_goals(classifier.every_plan(REPO_ROOT))
    collisions = classifier.id_collisions(goals)
    assert collisions == {}, (
        "a goal id is now declared by two workflows -- that is a finding to "
        f"REPORT, not to resolve: {collisions}")
    assert len({gid for _wf, gid in goals}) == len(goals)


def test_judged_classification_reads_a_declared_field_not_prose(classifier):
    """`SS-00-DF-03`, `R1`. Real subjects on BOTH sides of the retired matcher.

    `GOAL-tree-stabilizes` declares `kind: quality` and a pytest command, and
    its prose contains `card` and `sealed`: the keyword matcher called it judged
    (over-reach). `GOAL-price-means-something` declares `kind: eval` and its
    prose contains none of the keywords: the keyword matcher called it
    not-judged (under-reach). Both were wrong, in OPPOSITE directions -- which
    is why the repair could not have been fitted to a known answer.
    """
    goals = classifier.distinct_goals(classifier.every_plan(REPO_ROOT))

    over = goals[("stabilize-substrate-epic", "GOAL-tree-stabilizes")]
    assert classifier.keyword_judged(over) is True
    assert classifier.instrument_kind(over)[0] == "command"
    assert classifier.classify(REPO_ROOT, over)[0] == "not-judged"

    # THE UNDER-REACH SIDE IS NOT SIMPLY RE-ADMITTED. The SS-03 review pointed at
    # SV-03-DF-02, which names nine goals as naming no judged instrument, and six
    # of them declare `kind: eval`. Declared field and prior finding disagree, so
    # the shipped rule answers UNDECIDED rather than picking one.
    under = goals[("close-the-loop-epic", "GOAL-price-means-something")]
    assert classifier.keyword_judged(under) is False
    assert classifier.instrument_kind_by_field_only(under) == "judged"
    assert classifier.instrument_kind(under)[0] == "undecided"
    assert classifier.classify(REPO_ROOT, under)[0] == "undecided"


#: `SV-03-DF-02`'s own list, quoted from the ledger at this tree. Six of its
#: nine declare `kind: eval`; the other three declare a command kind, where the
#: field and the finding agree.
SV_03_DF_02_NAMED = {
    "GOAL-cheaper", "GOAL-removal-is-measured", "GOAL-removal-can-be-priced",
    "GOAL-price-means-something", "GOAL-instruments-can-fail",
    "GOAL-fixture-can-diverge", "GOAL-scope-loss-catchable",
    "GOAL-dead-weight-gone", "GOAL-apparatus-priced",
}


def test_what_the_rule_refuses_is_exactly_the_prior_findings_disputed_goals(classifier):
    """The veto is not arbitrary: it reproduces a filed finding's own list.

    `SV-03-DF-02` names nine goals that "name no judged instrument at all --
    they are decided by seeded mutants, a bench, or findings-per-token". Every
    goal this rule refuses is one of those nine, and the three of the nine it
    does not refuse are the three declaring a command kind, where the field and
    the finding agree.

    The issue asked what the proposed rule refuses when run against the sealed
    record. This is the answer, executed rather than described.
    """
    goals = classifier.distinct_goals(classifier.every_plan(REPO_ROOT))
    undecided = {gid for (_wf, gid), g in goals.items()
                 if classifier.instrument_kind(g)[0] == "undecided"}
    assert undecided, "a rule that refuses nothing has not been shown able to refuse"
    assert undecided <= SV_03_DF_02_NAMED, undecided - SV_03_DF_02_NAMED
    agreed = {gid for (_wf, gid), g in goals.items()
              if gid in SV_03_DF_02_NAMED and classifier.instrument_kind(g)[0] == "command"}
    assert undecided | agreed == SV_03_DF_02_NAMED, SV_03_DF_02_NAMED - (undecided | agreed)


def test_wrong_shaped_input_is_answered_and_never_raised(classifier):
    """`classify`'s docstring said "NEVER raises". It raised.

    A `baseline:` that is a scalar or a list is valid YAML and the wrong shape;
    it reached `.get` on a `str`, raised `AttributeError` out of `main`, printed
    a traceback and EXITED 1 with half the report unwritten. That made the
    instrument a gate on malformed input, which the issue forbids outright.
    """
    judged = {"id": "G", "kind": "eval", "metric": "D3 on the card"}
    for baseline in ("measured last week", ["a", "b"], 3, 0.5, True):
        verdict, why = classifier.classify(REPO_ROOT, dict(judged, baseline=baseline))
        assert verdict in classifier.VERDICTS and why, baseline
    for evidence in (["a.json"], {"path": "a"}, 7):
        verdict, _why = classifier.classify(REPO_ROOT, dict(judged, baseline={"evidence": evidence}))
        assert verdict == "no-evidence", (evidence, verdict)
    for goal in ("GOAL-a-string", ["GOAL-a"], None, 3):
        verdict, _why = classifier.classify(REPO_ROOT, goal)
        assert verdict == "undecided", (goal, verdict)


def test_a_goal_a_parsed_plan_declares_but_cannot_be_keyed_is_named(classifier):
    """`SS-03-DF-06`, one schema level below the plan parse.

    A plan that parses perfectly can declare `epic_goals` as a mapping, as a
    list of strings, or as goals with no `id`. Each counted as ZERO goals while
    `plans that DID NOT PARSE` read 0 — a silent drop, and that is the direction
    `SS-00-DF-02` is about.
    """
    for plan in ({"epic_goals": {"GOAL-a": {}}},
                 {"epic_goals": ["GOAL-a", "GOAL-b"]},
                 {"epic_goals": [{"kind": "eval"}]}):
        pair = [(Path("synthetic.yaml"), plan)]
        assert classifier.distinct_goals(pair) == {}
        problems = classifier.unreadable_goals(pair)
        assert problems, plan
        assert all(why for _path, why in problems)
    assert classifier.unreadable_goals([(Path("x.yaml"), {"epic_goals": []})]) == []
    assert classifier.unreadable_goals([(Path("x.yaml"), {})]) == []
    assert classifier.unreadable_goals(classifier.every_plan(REPO_ROOT)) == []


def test_an_unreadable_resolution_index_is_named_never_swallowed(classifier, tmp_path):
    """`SS-03-DF-06` — `SS-03-DF-02`'s own sentence handed back to its author.

    `load_index` swallowed every exception and returned `{}`: a corrupt index
    silently changed the verdict class of every goal it would have located and
    exited 0 without a word. The real index reads clean, so the failing input is
    synthesised — but at the real path, in a real root, through the real reader.
    """
    root = tmp_path
    (root / "references").mkdir()
    (root / "references" / "eval_scorecard.md").write_text("stub", encoding="utf-8")
    target = root / classifier.INDEX_PATH
    target.parent.mkdir(parents=True)

    assert classifier.load_index(root) == {}
    assert any("absent" in p for p in classifier.index_problems(root))

    target.write_text("entries: [\n  - broken: (", encoding="utf-8")
    assert classifier.load_index(root) == {}
    problems = classifier.index_problems(root)
    assert problems and "Error" in problems[0], problems

    target.write_text("entries:\n  - a string entry\n  - goal: G\n", encoding="utf-8")
    assert classifier.load_index(root) == {}
    assert len(classifier.index_problems(root)) == 2, classifier.index_problems(root)

    target.write_text("entries: 3\n", encoding="utf-8")
    assert classifier.load_index(root) == {}
    assert classifier.index_problems(root)

    assert classifier.index_problems(REPO_ROOT) == []


def test_the_two_verdict_columns_are_not_interchangeable(classifier):
    """Clause (d), and the comment that used to claim otherwise.

    `card-via-index` is DRAWN FROM `directory`/`summary`/`unresolvable`, not
    added beside them, so the with-index table is not comparable line for line
    to the `0 of 20` baseline. Both are printed; this pins that they differ and
    that the difference is exactly the index's contribution.
    """
    goals = classifier.distinct_goals(classifier.every_plan(REPO_ROOT))
    with_index = classifier.census(REPO_ROOT, goals, classifier.load_index(REPO_ROOT))
    without = classifier.census(REPO_ROOT, goals, None)

    def counts(c):
        out = {v: 0 for v in classifier.VERDICTS}
        for verdict, _why in c.values():
            out[verdict] += 1
        return out

    a, b = counts(with_index), counts(without)
    assert b["card-via-index"] == 0
    assert a["card-via-index"] > 0
    moved = sum(b[v] - a[v] for v in ("directory", "summary", "unresolvable", "prose", "no-evidence"))
    assert moved == a["card-via-index"], (moved, a["card-via-index"])
    assert a["card"] == b["card"] == 0
    # the two populations are identical; only the classes differ
    assert sum(a.values()) == sum(b.values()) == len(goals)


def test_a_harness_that_cannot_be_classified_from_declared_data_is_undecided(classifier):
    """The ABSENT-INPUT case, `r1_now_requires_an_absent_input`.

    UNDECIDED, never PASS and never a confident `not-judged`. A goal declaring
    no `kind` has told this instrument nothing, and "read and found nothing" is
    not "read nothing". Prose cannot rescue it: the last case below is loud with
    judged vocabulary and is still UNDECIDED.
    """
    assert classifier.instrument_kind({})[0] == "undecided"
    assert classifier.classify(REPO_ROOT, {})[0] == "undecided"
    assert classifier.classify(REPO_ROOT, {"kind": "vibes"})[0] == "undecided"
    assert classifier.classify(REPO_ROOT, {"kind": ""})[0] == "undecided"
    loud = {"kind": None, "harness": "scored against the card by two blind judges"}
    assert classifier.classify(REPO_ROOT, loud)[0] == "undecided"


def test_the_resolution_index_is_its_own_class_and_never_a_card(classifier):
    """An index entry is `SS-03`'s assertion, not the goal's.

    `R-H4` seals `specs/.history` and every judged goal in this record is
    declared only there, so the index is the only way to point one at its cards
    without editing sealed history. It must never move the `card` numerator:
    that number is about epics writing compliant goals, and no additive file
    beside the record can do that on their behalf.
    """
    index = classifier.load_index(REPO_ROOT)
    assert index, "the index is absent -- report that rather than passing vacuously"
    goals = classifier.distinct_goals(classifier.every_plan(REPO_ROOT))
    verdicts = classifier.census(REPO_ROOT, goals, index)
    assert any(v == "card-via-index" for v, _why in verdicts.values())
    assert all(v != "card" for v, _why in verdicts.values())
    for entry in index.values():
        for card in entry.get("cards") or []:
            path = REPO_ROOT / card
            assert path.is_file() and path.name == "scorecard.json", card
            json.loads(path.read_text(encoding="utf-8"))
