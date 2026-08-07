"""PA-05: the scorecard scaffold, and the scorer that reads its own history.

Two halves, and the second matters more.

**The scaffold** exists because for two epics every card was hand-authored from
the rubric by whichever agent was judging. That is how a dimension key or the
`refuses_to_claim` requirement drifts, and it puts the burden of remembering
five sets of anchors on the judge. So these tests do not check that a skeleton
is produced -- they check the three properties that make it a MECHANISM rather
than a habit:

* the anchors in the card are the anchors in `references/eval_scorecard.md`,
  read from it rather than copied (`test_the_anchors_are_read_from_the_rubric`);
* blinding is the DEFAULT and reuses no label any prior round published
  (`test_scaffold_blinds_by_default`, `test_scaffold_never_reuses_a_label`);
* scaffolding twice REFUSES and writes nothing
  (`test_scaffold_refuses_to_overwrite_and_writes_nothing`).

And that the shipped `check` did not get weaker in the process: an uncited score
of 2 or more and a 4 with no `refuses_to_claim` are still rejected, and an
`unfilled` skeleton cannot smuggle a score past the schema by staying unfilled.

**The history reader** exists because a sealed row can go stale without anyone
noticing, which has now happened twice inside this epic's own paperwork. The
tests below pin the distinction the whole ticket is about:

* a real mechanism gain measured WITHIN one run survives an era boundary
  (`test_a_within_run_gain_is_not_flagged`);
* a number read forward across an instrument change is reported
  SUPERSEDED-UNMARKED (`test_a_current_claim_across_a_change_is_superseded_unmarked`);
* an attribution correction is not recorded as a gain
  (`test_history_separates_an_attribution_correction_from_a_gain`,
  `test_history_marks_the_inverted_d5_attribution`);
* a sealed card that was edited is detected (`test_editing_a_sealed_card_is_detected`);
* and every reading rule written into the rubric has a check behind it
  (`test_every_reading_rule_in_the_doc_has_a_check`) -- because a declaration
  nothing executes will drift, which is the exact class of artifact this epic
  keeps finding stale.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
TOOL = REPO_ROOT / "examples/validation/scorecards/score_tools.py"
RUBRIC = REPO_ROOT / "references/eval_scorecard.md"
SCORECARDS = REPO_ROOT / "specs/results/scorecards"


@pytest.fixture(scope="module")
def st():
    spec = importlib.util.spec_from_file_location("score_tools_pa05", TOOL)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def rubric(st):
    return st.load_rubric(RUBRIC)


def scaffold(st, epic_dir, **kw):
    argv = ["scaffold", str(epic_dir), "--example", kw.pop("example", "ab_quota_ledger"),
            "--arms", kw.pop("arms", "A,B,C"), "--judges", str(kw.pop("judges", 2)),
            "--run-date", kw.pop("run_date", "20260805")]
    for key, value in kw.items():
        flag = "--" + key.replace("_", "-")
        if value is True:
            argv.append(flag)
        elif value is not None:
            argv += [flag, str(value)]
    return st.main(argv)


def one_card(epic_dir):
    return sorted(epic_dir.rglob("scorecard.json"))[0]


# --------------------------------------------------------------------------
# half one: the scaffold
# --------------------------------------------------------------------------

def test_the_anchors_are_read_from_the_rubric(st, rubric, tmp_path, capsys):
    """The bar for a score is in the same file as the score, and it is THE bar.

    Not a copy of it. The anchors are parsed out of references/eval_scorecard.md
    at scaffold time, so there is one source of truth; a rubric transcribed into
    the tool is a rubric that drifts from the one judges are pointed at.
    """
    epic = tmp_path / "ports-as-adapters"
    assert scaffold(st, epic, seed=1) == 0
    capsys.readouterr()

    card = json.loads(one_card(epic).read_text())
    for dim in st.DIMS:
        entry = card["dimensions"][dim]
        assert entry["name"] == st.NAMES[dim]
        assert entry["anchors"] == rubric["dimensions"][dim]["anchors"], dim
        assert entry["score"] is None
    assert card["rubric"]["digest"] == rubric["digest"]
    assert card["rubric"]["scoring_rules"] == rubric["scoring_rules"]

    md = one_card(epic).with_name("scorecard.md").read_text()
    for dim in st.DIMS:
        for score in "01234":
            assert rubric["dimensions"][dim]["anchors"][score] in md
    assert "capped at 1" in md
    assert "refuses to claim" in md.lower()
    assert "never scored" in md.lower()  # the mechanical block


def test_a_stale_rubric_digest_blocks_a_skeleton_from_being_judged(st, tmp_path, capsys):
    epic = tmp_path / "ports-as-adapters"
    assert scaffold(st, epic, seed=1) == 0
    capsys.readouterr()
    path = one_card(epic)
    card = json.loads(path.read_text())
    card["rubric"]["digest"] = "sha256:deadbeefdeadbeef"
    path.write_text(json.dumps(card))

    problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC))
    assert any("re-scaffold" in p for p in problems)


def test_scaffold_blinds_by_default(st, tmp_path, capsys):
    """Both prior rounds blinded correctly by discipline. Discipline is not a
    mechanism: an eval that wants unblinded scoring must undo this deliberately."""
    epic = tmp_path / "ports-as-adapters"
    assert scaffold(st, epic, seed=7) == 0
    capsys.readouterr()

    labels = {json.loads(p.read_text())["arm"] for p in epic.rglob("scorecard.json")}
    assert labels.isdisjoint({"A", "B", "C"}), labels
    for p in epic.rglob("scorecard.json"):
        card = json.loads(p.read_text())
        assert card["judge"]["blind_to_arm"] is True
        # the real arm name appears nowhere the judge can see it
        assert "UNBLINDING" not in p.parent.name

    key = epic / "UNBLINDING.md"
    assert key.exists()
    assert "DO NOT GIVE THIS FILE TO A JUDGE" in key.read_text()
    # the mapping lives OUTSIDE every card directory
    assert key.parent == epic
    assert not any((d / "UNBLINDING.md").exists() for d in epic.rglob("*p1"))


def test_unblinding_is_deliberate_and_must_carry_a_reason(st, tmp_path, capsys):
    epic = tmp_path / "ports-as-adapters"
    assert scaffold(st, epic, unblinded=True) == 2
    assert "requires --reason" in capsys.readouterr().err

    assert scaffold(st, epic, unblinded=True, reason="owner tracking pass, pass 0") == 0
    capsys.readouterr()
    labels = {json.loads(p.read_text())["arm"] for p in epic.rglob("scorecard.json")}
    assert labels == {"A", "B", "C"}
    key = (epic / "UNBLINDING.md").read_text()
    assert "SCAFFOLDED UNBLINDED" in key
    assert "owner tracking pass, pass 0" in key
    card = json.loads(one_card(epic).read_text())
    assert card["judge"]["blind_to_arm"] is False


def test_scaffold_never_reuses_a_label_a_prior_round_published(st, tmp_path, capsys):
    """HP-06 used X/Y and published its key; EVAL-RERUN chose P/Q so a judge who
    stumbled into the sealed run could not read the arms off it. Mechanised."""
    root = tmp_path / "scorecards"
    for label in "DEFGHJKLMNRSTUVW":
        d = root / "prior" / "ex" / f"20260101-{label}-p1"
        d.mkdir(parents=True)
        (d / "scorecard.json").write_text(json.dumps({"arm": label}))
    # only Z is left in the pool
    assert scaffold(st, root / "epic", arms="A", judges=1) == 0
    capsys.readouterr()
    assert json.loads(one_card(root / "epic").read_text())["arm"] == "Z"

    assert st.used_labels(root) >= set("DEFGHJKLMNRSTUVW")
    # and with none left it refuses rather than colliding
    assert scaffold(st, root / "epic2", arms="A,B", judges=1) == 2
    assert "unused opaque labels remain" in capsys.readouterr().err


def test_scaffold_refuses_to_overwrite_and_writes_nothing(st, tmp_path, capsys):
    """A scaffold that clobbers a measurement is worse than no scaffold."""
    epic = tmp_path / "ports-as-adapters"
    assert scaffold(st, epic, labels="K,L,M") == 0
    capsys.readouterr()

    path = one_card(epic)
    card = json.loads(path.read_text())
    card["status"] = "filled"
    card["commit"] = "abc1234"
    card["verdict"] = "a real measurement that must not be destroyed"
    path.write_text(json.dumps(card, indent=2))
    before = {p: p.read_bytes() for p in epic.rglob("*") if p.is_file()}

    assert scaffold(st, epic, labels="K,L,M") == 3
    err = capsys.readouterr().err
    assert "REFUSED" in err and "Nothing was written" in err
    assert {p: p.read_bytes() for p in epic.rglob("*") if p.is_file()} == before

    # a single surviving card is enough to refuse the whole batch
    shutil.rmtree(sorted(epic.rglob("2026*"))[1])
    assert scaffold(st, epic, labels="K,L,M") == 3

    # and a fresh label draw does NOT sneak past it: new labels mean new
    # directories, which would otherwise be written beside a real measurement
    # and silently orphan its unblinding key.
    for d in sorted(epic.rglob("2026*")):
        shutil.rmtree(d)
    assert scaffold(st, epic) == 3
    assert "UNBLINDING.md alone is enough" in capsys.readouterr().err


# --------------------------------------------------------------------------
# the shipped rules did not get weaker
# --------------------------------------------------------------------------

def fill(card, practice=True, ran=("seeded a fault in commit() and ran the suite",),
         **scores):
    card["status"] = "filled"
    card["commit"] = "0123456"
    card["judge"]["model"] = "claude-opus-5[1m]"
    card["verdict"] = "a verdict"
    if card.get("scorecard_version", 1) >= 2:
        card["judging_practice"] = {"executed_own_faults": practice,
                                    "what_was_run": list(ran) if practice else []}
    version = card.get("scorecard_version", 1)
    total = 0
    for dim in st_dims():
        entry = card["dimensions"][dim]
        spec = scores.get(dim, {"score": 1})
        entry.update(spec)
        entry.setdefault("rationale", "because the artifact says so and I ran it")
        entry["rationale"] = entry["rationale"] or "because the artifact says so"
        total += entry["score"]
        # scorecard_version 3: the one anchor with two defensible readings says
        # which one it was scored under, at 3 and 4 where they can differ.
        if version >= 3 and dim == "D5" and entry["score"] in (3, 4):
            entry["anchor_reading"] = entry.get("anchor_reading") or "measured"
    if version < 3:
        card["total"] = total
    else:
        card.pop("total", None)
    return card


def st_dims():
    return ("D1", "D2", "D3", "D4", "D5")


def scaffolded(st, tmp_path, labels="K,L,M"):
    epic = tmp_path / "ports-as-adapters"
    scaffold(st, epic, labels=labels)
    path = one_card(epic)
    return path, json.loads(path.read_text())


def test_a_scaffolded_card_filled_in_properly_passes_check(st, tmp_path, capsys):
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    fill(card, D3={"score": 4, "citations": ["quota_ledger/domain.py:22-43"],
                   "refuses_to_claim": "that anything but the durable side is behind a port"})
    problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC))
    assert problems == []


def test_check_still_rejects_an_uncited_score_of_two_or_more(st, tmp_path, capsys):
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    fill(card, D1={"score": 3, "citations": []})
    problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC))
    assert any("D1 scored 3 with NO citation" in p and "rule 2 caps it at 1" in p
               for p in problems), problems


def test_check_still_rejects_a_four_with_no_refuses_to_claim(st, tmp_path, capsys):
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    fill(card, D3={"score": 4, "citations": ["domain.py:22-43"], "refuses_to_claim": None})
    problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC))
    assert any("D3 scored 4 without refuses_to_claim" in p for p in problems), problems


def test_an_unfilled_skeleton_cannot_smuggle_a_score_through(st, tmp_path, capsys):
    """`status: unfilled` is not a way to score without being checked."""
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    card["dimensions"]["D1"]["score"] = 4  # left 'unfilled'
    problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC))
    assert any("status is 'unfilled' but D1 carry a score" in p for p in problems), problems
    # and once it is treated as filled, every rule applies
    assert any("refuses_to_claim" in p for p in problems), problems


def test_check_rejects_a_drifted_dimension_name(st, tmp_path, capsys):
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    fill(card)
    card["dimensions"]["D3"]["name"] = "architecture"
    problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC))
    assert any("D3 is named 'architecture'" in p for p in problems), problems


def test_check_rejects_a_partial_set_of_inline_anchors(st, tmp_path, capsys):
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    fill(card)
    card["dimensions"]["D2"]["anchors"].pop("4")
    problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC))
    assert any("inline anchors but not all of 0-4" in p for p in problems), problems


def test_require_filled_is_what_a_close_runs(st, tmp_path, capsys):
    epic = tmp_path / "ports-as-adapters"
    scaffold(st, epic, labels="K,L,M")
    capsys.readouterr()
    assert st.main(["check", str(epic)]) == 0
    assert st.main(["check", str(epic), "--require-filled"]) == 1
    assert "unfilled skeleton" in capsys.readouterr().out


# --------------------------------------------------------------------------
# FI-03: scorecard_version 2 -- what the judge DID is a field, not a choice
#
# PA-06 re-scored byte-identical trees and four dimension-points moved. Both
# judges had privately decided to seed and run their own faults; the round
# before them had not; and no card said so either way. The card was measuring
# the judge and reporting it as the artifact.
# --------------------------------------------------------------------------

def test_scaffold_emits_the_current_card_version_with_a_practice_block(st, tmp_path, capsys):
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    assert card["scorecard_version"] == 3
    assert card["judging_practice"]["executed_own_faults"] is None
    assert card["judging_practice"]["what_was_run"] == []
    md = path.with_name("scorecard.md").read_text()
    assert "Judging practice" in md
    # SM-04: the sentence that used to sit here -- "two judges re-scored
    # byte-identical trees and four dimension-points moved" -- was a RESULT about
    # the dimensions the judge was about to score, served to every version 2
    # judge in their own card. It is gone, and `result_leaks` is why it cannot
    # come back.
    assert "byte-identical" not in md
    assert st.result_leaks(md) == []


def test_a_filled_version_2_card_must_say_what_the_judge_did(st, tmp_path, capsys):
    """The whole ticket in one assertion: the practice is a REQUIRED FIELD."""
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    fill(card)
    card.pop("judging_practice")
    problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC))
    assert any("missing required field 'judging_practice'" in p for p in problems), problems


def test_executed_own_faults_must_be_a_boolean_not_a_shrug(st, tmp_path, capsys):
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    fill(card)
    card["judging_practice"]["executed_own_faults"] = "some"
    problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC))
    assert any("executed_own_faults must be true or false" in p for p in problems), problems


def test_saying_you_ran_faults_requires_naming_them(st, tmp_path, capsys):
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    fill(card)
    card["judging_practice"]["what_was_run"] = []
    problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC))
    assert any("name what was run" in p for p in problems), problems


def test_scoring_the_packet_and_nothing_else_is_LEGAL_and_is_recorded(st, tmp_path, capsys):
    """R2's shape applied to a judge: the unflattering answer must be sayable.

    A field that only one answer passes is a field that collects the answer it
    wants. `executed_own_faults: false` is a valid card and is reported.
    """
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    fill(card, practice=False)
    problems, notes = st.check(card, str(path), st.load_rubric(RUBRIC))
    assert problems == []
    assert any("PACKET-ONLY" in n for n in notes), notes


def test_d4_anchor_4_is_not_awardable_by_a_judge_that_ran_nothing(st, tmp_path, capsys):
    """D4 = 4 asks for a behavior-breaking change SHOWN TO BE CAUGHT.

    A judge reading a kill table is repeating the artifact's claim. This is the
    anchor's own text, executed -- and it is the only one gated, because it is
    the only one that asks the judge to run something.
    """
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    fill(card, practice=False,
         D4={"score": 4, "citations": ["EVIDENCE.md:180-187"],
             "refuses_to_claim": "that the fake and the real adapter agree"})
    problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC))
    assert any("D4 scored 4 while judging_practice.executed_own_faults is false" in p
               for p in problems), problems
    # the same card from a judge that DID run one is fine
    fill(card, practice=True,
         D4={"score": 4, "citations": ["EVIDENCE.md:180-187"],
             "refuses_to_claim": "that the fake and the real adapter agree"})
    assert st.check(card, str(path), st.load_rubric(RUBRIC))[0] == []


def test_d1_and_d5_are_deliberately_not_gated(st, tmp_path, capsys):
    """D1, D4 and D5 all moved on unchanged input. Only D4's ANCHOR asks the
    judge to run something, so only D4 is gated. Gating the other two would be
    inventing a requirement rather than executing one."""
    assert st.PRACTICE_GATED_DIMS == ("D4",)
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    fill(card, practice=False,
         D1={"score": 4, "citations": ["EVIDENCE.md:111-119"],
             "refuses_to_claim": "any ordering fault on a set-typed collection"},
         D5={"score": 4, "citations": ["NOTES.md:136-141"],
             "refuses_to_claim": "that the fake is contract-equivalent"})
    assert st.check(card, str(path), st.load_rubric(RUBRIC))[0] == []


# --------------------------------------------------------------------------
# SM-04, scorecard_version 3. Four defects, none of them an anchor.
#
# 1. the digest was blind to what reached a judge
# 2. a judge was served the finding they were the instrument for
# 3. D5's anchor 4 is ambiguous and the ambiguity was invisible
# 4. `total` was printed while four of its five terms cannot carry a delta
# --------------------------------------------------------------------------

SEALED_V2_CARD = (SCORECARDS / "falsifiable-instruments-rescore-v2/ab_quota_ledger"
                  / "20260806-v2-U-p1/scorecard.md")


def test_the_cards_this_project_actually_dispatched_carried_the_result_they_measured(st):
    """THE DEMONSTRATED FAILING INPUT for defect 2, and it is not synthetic.

    FI-03's version 2 judges were handed, inside their own card, the sentence
    "D1, D4 and D5 all moved on unchanged input" and "four dimension-points
    moved" -- a result about the five dimensions they were about to score. It
    was in `_skeleton_md`, so it reached every judge in every round from version
    2 onward, and nobody had noticed because the leak everyone was looking at
    was in the rubric file.

    This card is sealed and is never edited, so this test is a fixed point: the
    detector shipped at SM-04 goes red on bytes this project really dispatched.
    """
    leaks = st.result_leaks(SEALED_V2_CARD.read_text())
    assert leaks, "the sealed version 2 card no longer trips the detector"
    assert any("dimension-points" in leak and "moved" in leak for leak in leaks), leaks
    assert any("'D4'" in leak and "moved" in leak for leak in leaks), leaks


def test_a_scaffolded_card_carries_no_result_about_the_dimensions_it_scores(st, tmp_path,
                                                                            capsys):
    """The same detector, on what the tool emits now. This is the fix."""
    path, _ = scaffolded(st, tmp_path)
    capsys.readouterr()
    assert st.result_leaks(path.with_name("scorecard.md").read_text()) == []
    assert st.rubric_leak_problems(st.load_rubric(RUBRIC)) == []


def test_the_reading_rules_cannot_reach_a_judge_because_nothing_emits_them(st, rubric):
    """The MECHANISM, as distinct from the backstop.

    `served_rubric` renders parsed structure only. `## Reading history`, the
    version history, the storage layout and anything a later editor adds are
    outside it by construction -- not by a rule someone has to remember. R-H5 is
    the section both FI-03 v1 judges cited back at the round measuring them.
    """
    served = st.served_rubric(rubric, 3)
    for forbidden in ("R-H1", "R-H2", "R-H3", "R-H4", "R-H5",
                      "Reading history", "Version history", "anchors digest",
                      "SELF-IMPROVEMENT", "INSTRUMENT-LOG", "EVAL-RERUN", "PA-06"):
        assert forbidden not in served, f"{forbidden!r} reaches a judge"
    # and it really is the rubric: every anchor of every dimension is in there
    for dim in st_dims():
        for score in "01234":
            assert rubric["dimensions"][dim]["anchors"][score] in served


def test_serve_refuses_a_rubric_that_would_hand_a_judge_a_result(st, tmp_path, capsys):
    """THE DEMONSTRATED FAILING INPUT for the refusal.

    The sentence pasted in is R-H5's own, moved from the part of the file no
    judge is served into the part every judge is.
    """
    copy = tmp_path / "eval_scorecard.md"
    copy.write_text(RUBRIC.read_text().replace(
        "**Anchor 4's phrase",
        "**D2 and D3 are the dimensions that have held still on unchanged input, "
        "and D4 and D5 move two points per judge.** Anchor 4's phrase", 1))
    assert st.main(["serve", "--rubric", str(copy)]) == 3
    err = capsys.readouterr().err
    assert "REFUSED" in err and "Nothing was written" in err
    # and the same refusal stops a whole round being scaffolded, writing nothing
    epic = tmp_path / "round"
    assert scaffold(st, epic, labels="K,L,M", rubric=str(copy)) == 3
    capsys.readouterr()
    assert not epic.exists(), "a refused scaffold left files behind"
    # `check` reports it too, so a close catches an edit no scaffold ran against
    assert any("has scored or moved" in p
               for p in st.rubric_leak_problems(st.load_rubric(copy)))


def test_the_served_digest_moves_when_anything_a_judge_reads_moves(st, rubric, tmp_path):
    """Defect 1. `The rubric digest changes when the rubric changes in any way
    that can reach a judge` -- the ticket's own acceptance assertion.

    Each edit below is one word, in a different served region, and each moves
    the served digest.
    """
    base = st.served_digest(rubric, 3)
    text = RUBRIC.read_text()
    edits = {
        "an anchor": ("- **0** — No boundary is discernible; state is written from "
                      "everywhere.",
                      "- **0** — No boundary is discernible; state is written from "
                      "anywhere."),
        "a caveat": ("**Import topology is not modularity.**",
                     "**Import topology is not modularity, ever.**"),
        "a preamble": ("Read the measured descriptor first",
                       "Read the measured descriptor FIRST"),
        "a scoring rule": ("**Prose quality is never an input.**",
                           "**Prose quality is never ever an input.**"),
        "a question": ("Is the design as simple as its behavior requires, and no simpler?",
                       "Is the design as simple as its behaviour requires, and no simpler?"),
    }
    for what, (old, new) in edits.items():
        assert text.count(old) == 1, what
        copy = tmp_path / f"{what.replace(' ', '_')}.md"
        copy.write_text(text.replace(old, new))
        assert st.served_digest(st.load_rubric(copy), 3) != base, (
            f"editing {what} left the served digest unmoved")


def test_prose_a_judge_never_sees_is_reported_but_does_not_invalidate(st, rubric, tmp_path,
                                                                      capsys):
    """The converse of defect 1, and the reason the fix is not a wider hash.

    `FI-03-DF-02` said it plainly: the digest is RIGHT to exclude prose from the
    scaffold-time check, because a rubric whose every typo re-scaffolds the round
    is unusable. What was missing was any record that the file changed at all.
    So: served digest unmoved, file digest moved, reported PROSE-DRIFT, never a
    problem.
    """
    copy = tmp_path / "eval_scorecard.md"
    copy.write_text(RUBRIC.read_text().replace(
        "## Reading history\n",
        "## Reading history\n\nAn editorial paragraph in a section no judge is served.\n",
        1))
    later = st.load_rubric(copy)
    assert st.served_digest(later, 3) == st.served_digest(rubric, 3)
    assert later["file_sha256"] != rubric["file_sha256"]

    epic = tmp_path / "e"
    scaffold(st, epic, labels="K,L,M")
    capsys.readouterr()
    path = one_card(epic)
    card = fill(json.loads(path.read_text()))
    problems, notes = st.check(card, str(path), later)
    assert problems == []
    assert any("PROSE-DRIFT" in n for n in notes), notes


def test_a_card_records_the_digest_of_the_bytes_it_was_served(st, tmp_path, capsys):
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    rubric = st.load_rubric(RUBRIC)
    assert card["rubric"]["served_digest"] == st.served_digest(rubric, 3)
    assert card["rubric"]["file_sha256"] == rubric["file_sha256"]
    # the card the judge reads carries the same bytes the digest is over
    assert st.served_rubric(rubric, 3) in path.with_name("scorecard.md").read_text()
    # a skeleton served a bar that has since moved is REFUSED, not noted
    card["rubric"]["served_digest"] = "sha256:0000000000000000"
    problems, _ = st.check(card, str(path), rubric)
    assert any("what a judge would read has changed" in p for p in problems), problems


def test_d5_scored_where_the_two_readings_differ_must_name_which(st, tmp_path, capsys):
    """Defect 3, and the demonstrated failing input for it.

    Both version 2 judges executed their own faults and still split 3 against 4
    on D5, so judging practice does not explain that one. THE ANCHOR IS NOT
    TOUCHED -- `anchors_digest` is asserted unmoved elsewhere in this file. What
    version 3 does is what version 2 did for practice: record the choice.
    """
    for score in (3, 4):
        path, card = scaffolded(st, tmp_path / f"s{score}")
        capsys.readouterr()
        fill(card, D5={"score": score, "citations": ["NOTES.md:136-141"],
                       "refuses_to_claim": "that the fake is contract-equivalent"})
        card["dimensions"]["D5"]["anchor_reading"] = None
        problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC))
        assert any("anchor_reading" in p for p in problems), (score, problems)
        # both readings are legal and neither is corrected
        for reading in st.ANCHOR_READINGS:
            card["dimensions"]["D5"]["anchor_reading"] = reading
            assert st.check(card, str(path), st.load_rubric(RUBRIC))[0] == []
        card["dimensions"]["D5"]["anchor_reading"] = "whichever"
        assert st.check(card, str(path), st.load_rubric(RUBRIC))[0] != []


def test_d5_below_the_boundary_needs_no_reading(st, tmp_path, capsys):
    """At 0, 1 and 2 the two readings cannot differ, so requiring the field there
    would be a bar nobody asked for."""
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    fill(card, D5={"score": 2, "citations": ["NOTES.md:136-141"],
                   "anchor_reading": None})
    assert st.check(card, str(path), st.load_rubric(RUBRIC))[0] == []


def test_a_version_3_card_has_no_total_and_a_version_2_card_still_checks_its_own(
        st, tmp_path, capsys):
    """Defect 4. Four of its five terms cannot carry a delta.

    Versions 1 and 2 keep theirs and the arithmetic is still checked: a sealed
    card is never edited, and a check that stops looking at one is a check that
    stopped working.
    """
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    assert "total" not in card
    assert "total" not in path.with_name("scorecard.md").read_text().lower()
    fill(card)
    assert st.check(card, str(path), st.load_rubric(RUBRIC))[0] == []
    card["total"] = 5
    assert any("There is no total from version 3" in p
               for p in st.check(card, str(path), st.load_rubric(RUBRIC))[0])

    epic2 = tmp_path / "v2"
    assert scaffold(st, epic2, labels="K,L,M", card_version=2) == 0
    capsys.readouterr()
    p2 = one_card(epic2)
    old = fill(json.loads(p2.read_text()))
    assert old["total"] == 5
    assert st.check(old, str(p2), st.load_rubric(RUBRIC))[0] == []
    old["dimensions"]["D3"]["score"] = 3
    assert any("does not equal the sum" in p
               for p in st.check(old, str(p2), st.load_rubric(RUBRIC))[0])


def test_neither_index_nor_history_prints_a_total(st, tmp_path, capsys):
    st.main(["history", "--example", "ab_quota_ledger", "--root", str(SCORECARDS)])
    out = capsys.readouterr().out
    assert "| total |" not in out
    assert "no total column" in out
    # a computed total never reaches a table row, on any card version
    assert not [l for l in out.splitlines() if l.startswith("| `2026") and "/20" in l]

    # `index` writes INDEX.md where it is pointed, so point it at a copy
    epic = tmp_path / "ports-as-adapters"
    shutil.copytree(SCORECARDS / "ports-as-adapters", epic)
    st.main(["index", str(epic)])
    idx = capsys.readouterr().out
    assert "| total |" not in idx
    assert not [l for l in idx.splitlines() if l.startswith("| ab_quota") and "/20" in l]
    assert "No total" in idx


def test_the_previous_card_version_can_still_be_scaffolded(st, tmp_path, capsys):
    """`Changing this card` requires a re-score under BOTH versions. A tool that
    can only emit the current one makes its own change rule unfollowable."""
    epic = tmp_path / "rescore-v1"
    assert scaffold(st, epic, labels="K,L,M", card_version=1) == 0
    capsys.readouterr()
    card = json.loads(one_card(epic).read_text())
    assert card["scorecard_version"] == 1
    assert "judging_practice" not in card
    assert "Judging practice" not in one_card(epic).with_name("scorecard.md").read_text()
    # and a v1 card filled in is still valid: old cards do not become invalid
    fill(card)
    assert st.check(card, str(one_card(epic)), st.load_rubric(RUBRIC))[0] == []


def test_the_version_bump_kept_the_anchors_and_says_so_in_a_digest(st, rubric):
    """`keep the old anchors in the file` is checkable or it is a promise.

    The anchors digest is over the anchors ALONE, so it is unmoved by a change
    to the scoring rules -- which is exactly what version 2 was.
    """
    declared = {v["version"]: v["anchors_digest"] for v in rubric["versions"]}
    assert declared, "the rubric declares no version history"
    assert rubric["card_version"] == 3
    assert declared[3] == rubric["anchors_digest"]
    assert declared[1] == declared[2] == declared[3], (
        "a version bump declares different anchors from its predecessor; every bump so "
        "far was supposed to change what a card RECORDS, not what a score MEANS")
    # SM-04's own prohibition, executed: D2, D4 and D5 stay on the card and NO
    # ANCHOR WAS TUNED. This is the machine statement of it.
    assert rubric["anchors_digest"] == "sha256:eeccf4576bc6fd85"
    assert set(rubric["dimensions"]) == {"D1", "D2", "D3", "D4", "D5"}
    assert st.version_history_problems(rubric) == []


def test_a_rubric_whose_anchors_moved_without_a_bump_is_reported(st, tmp_path, capsys):
    """The demonstrated failing input for the change rule itself."""
    copy = tmp_path / "eval_scorecard.md"
    copy.write_text(RUBRIC.read_text().replace(
        "- **0** — No boundary is discernible; state is written from everywhere.",
        "- **0** — No boundary is discernible, or the judge could not find one."))
    problems = st.version_history_problems(st.load_rubric(copy))
    assert any("the anchors in this file digest to" in p for p in problems), problems
    epic = tmp_path / "e"
    scaffold(st, epic, labels="K,L,M")
    capsys.readouterr()
    assert st.main(["check", str(epic), "--rubric", str(copy)]) == 1
    assert "changing silently" in capsys.readouterr().out


def test_a_version_history_that_drops_an_old_version_is_reported(st, tmp_path):
    copy = tmp_path / "eval_scorecard.md"
    text = RUBRIC.read_text()
    v1_row = next(l for l in text.splitlines() if l.startswith("| **1** |"))
    copy.write_text(text.replace(v1_row + "\n", ""))
    problems = st.version_history_problems(st.load_rubric(copy))
    assert any("drops version 1" in p for p in problems), problems


# --------------------------------------------------------------------------
# half two: reading history
# --------------------------------------------------------------------------

def write_log(root: Path, body: str) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "INSTRUMENT-LOG.toml").write_text(body)
    return root


def put_card(root: Path, round_dir: str, run_id: str, commit: str, example="ex", arm="P"):
    d = root / round_dir / example / run_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "scorecard.json").write_text(json.dumps({
        "scorecard_version": 1, "epic": round_dir, "example": example, "run_id": run_id,
        "arm": arm, "commit": commit,
        "judge": {"model": "m", "pass": 1, "blind_to_arm": True},
        "dimensions": {d_: {"score": 1, "citations": [], "rationale": "r"} for d_ in st_dims()},
        "total": 5, "contested": [], "verdict": "v",
    }))
    return d


CHANGE = """
schema_version = 1

[[change]]
id = "EVAL-SUPPRESS"
commit = "3e721a5"
date = "2026-08-05"
kind = "repair"
affects = ["ex"]
paths = ["examples/validation/ab/eval/run_controls.py"]
summary = "a declaration could erase a demonstrated kill"
"""


def test_a_current_claim_across_a_change_is_superseded_unmarked(st, tmp_path):
    """The failure this ticket exists to prevent, and it has happened twice.

    `GOAL-cases-drive-ports` was dispatched baselining 49 of 49 when a later run
    had already superseded it with 56 of 56. A superseded row was read forward
    as current through a whole dispatch, and nothing could say so.
    """
    root = write_log(tmp_path / "scorecards", CHANGE + """
[[claim]]
id = "cells-identical"
example = "ex"
status = "current"
delta_basis = "across_time"
measured_at = "24ed3fa"
date = "2026-08-04"
statement = "56 of 56 comparable cells identical"
""")
    put_card(root, "round-one", "20260804-P-p1", "24ed3fa")
    results, _ = st.run_audit(root)
    rh3 = [m for level, m in results["R-H3"] if level == st.VIOLATION]
    assert any("SUPERSEDED-UNMARKED" in m and "cells-identical" in m for m in rh3), rh3


def test_reaffirming_after_the_change_clears_it(st, tmp_path):
    root = write_log(tmp_path / "scorecards", CHANGE + """
[[claim]]
id = "cells-identical"
example = "ex"
status = "current"
delta_basis = "across_time"
measured_at = "24ed3fa"
date = "2026-08-04"
reaffirmed_at = "21da25b"
statement = "56 of 56 comparable cells identical"
""")
    put_card(root, "round-one", "20260804-P-p1", "24ed3fa")
    results, _ = st.run_audit(root)
    assert not [m for level, m in results["R-H3"] if level == st.VIOLATION]


def test_a_within_run_gain_is_not_flagged(st, tmp_path):
    """Guard relaxation 0 -> 3 of 3 is a REAL MECHANISM GAIN, and the reason is
    structural: both ends were measured in the SAME RUN on two instruments, not
    at two points in time, so no era boundary applies to it."""
    root = write_log(tmp_path / "scorecards", CHANGE + """
[[claim]]
id = "guard-relaxation"
example = "ex"
status = "current"
delta_basis = "within_run"
measured_at = "24ed3fa"
date = "2026-08-04"
statement = "3 of 3 under corpus-neg against 0 under every other instrument, same run"
""")
    put_card(root, "round-one", "20260804-P-p1", "24ed3fa")
    results, _ = st.run_audit(root)
    assert not [m for level, m in results["R-H3"] if level == st.VIOLATION]
    assert any("within-run" in m for _, m in results["R-H3"])


def test_under_review_requires_a_finding_that_actually_exists(st, tmp_path):
    """Otherwise `under_review` is just a quiet place to park a number."""
    root = write_log(tmp_path / "scorecards", CHANGE + """
[[claim]]
id = "parked"
example = "ex"
status = "under_review"
measured_at = "24ed3fa"
date = "2026-08-04"
statement = "something inconvenient"
""")
    put_card(root, "round-one", "20260804-P-p1", "24ed3fa")
    results, _ = st.run_audit(root)
    assert any("no `filed_as`" in m for level, m in results["R-H3"] if level == st.VIOLATION)

    root2 = write_log(tmp_path / "scorecards2", CHANGE + """
[[claim]]
id = "parked"
example = "ex"
status = "under_review"
filed_as = "NO-SUCH-DF-99"
measured_at = "24ed3fa"
date = "2026-08-04"
statement = "something inconvenient"
""")
    put_card(root2, "round-one", "20260804-P-p1", "24ed3fa")
    results2, _ = st.run_audit(root2)
    assert any("not an id in deferred_findings.yaml" in m
               for level, m in results2["R-H3"] if level == st.VIOLATION)


def test_a_refuted_finding_stays_on_the_record_with_its_filing(st, tmp_path):
    """PA-05-DF-02. A finding that turned out to be wrong is evidence about the
    review process, so it is recorded rather than deleted -- and `refuted` is
    not `known_wrong`: one is a measurement that stopped being true, the other
    an assertion someone made in review that was falsified from data."""
    root = write_log(tmp_path / "scorecards", CHANGE + """
[[claim]]
id = "the-cell-was-inside-the-set"
example = "ex"
status = "refuted"
measured_at = "24ed3fa"
date = "2026-08-04"
filed_as = "PA-05-DF-02"
refuted_by = "the epic owner, from the sealed raw kill tables"
statement = "the flipped cell is inside the comparable set"
why = "2 of 77 cells differ and both are a control that is out of the denominator"
""")
    put_card(root, "round-one", "20260804-P-p1", "24ed3fa")
    results, _ = st.run_audit(root)
    assert not [m for level, m in results["R-H3"] if level == st.VIOLATION]
    assert any("refuted by the epic owner" in m and "kept on the record" in m
               for _, m in results["R-H3"])


def test_a_refuted_claim_must_name_who_refuted_it(st, tmp_path):
    """Otherwise `refuted` becomes a way to withdraw a claim without recording
    that anybody checked it."""
    root = write_log(tmp_path / "scorecards", CHANGE + """
[[claim]]
id = "quietly-withdrawn"
example = "ex"
status = "refuted"
measured_at = "24ed3fa"
date = "2026-08-04"
statement = "something I would rather not talk about"
""")
    put_card(root, "round-one", "20260804-P-p1", "24ed3fa")
    results, _ = st.run_audit(root)
    assert any("`refuted_by`" in m and "`why`" in m
               for level, m in results["R-H3"] if level == st.VIOLATION)


def test_filed_as_is_verified_on_every_status_not_only_under_review(st, tmp_path):
    """A refuted or discharged finding must stay reachable from the ledger, so a
    dangling `filed_as` is a violation whatever the status says."""
    root = write_log(tmp_path / "scorecards", CHANGE + """
[[claim]]
id = "dangling"
example = "ex"
status = "refuted"
measured_at = "24ed3fa"
date = "2026-08-04"
filed_as = "NO-SUCH-DF-99"
refuted_by = "somebody"
statement = "s"
why = "w"
""")
    put_card(root, "round-one", "20260804-P-p1", "24ed3fa")
    results, _ = st.run_audit(root)
    assert any("not an id in deferred_findings.yaml" in m
               for level, m in results["R-H3"] if level == st.VIOLATION)


def test_a_repair_that_moved_nothing_is_a_measured_statement(st, tmp_path):
    """PA-04: `control_red = []` while a positive control had SURVIVED four
    columns that each ran 294 accepting Reserve cases. Executing the control's
    declared role moved ZERO verdicts across all 90 cells and the instrument
    still got materially more honest. R-H3 said a number that MOVED for
    instrument reasons is not improvement; this is the converse it did not say,
    and the record has to be able to state it."""
    root = write_log(tmp_path / "scorecards", """
schema_version = 1

[[change]]
id = "PA-04-control-role-executed"
commit = "3e721a5"
date = "2026-08-05"
kind = "repair"
affects = ["ex"]
paths = ["examples/validation/ab/eval/run_controls.py"]
verdicts_moved = 0
verdicts_scope = "all 90 cells across three subjects"
summary = "a role string could fail to raise a demonstrated control failure"
""")
    put_card(root, "round-one", "20260806-P-p1", "3e721a5")
    results, _ = st.run_audit(root)
    assert not [m for level, m in results["R-H3"] if level == st.VIOLATION]
    assert any("moved ZERO verdicts" in m and "not whether they moved" in m
               for _, m in results["R-H3"])


def test_a_repair_that_declares_no_verdict_count_is_reported(st, tmp_path):
    """"Nothing moved" has to be measured, and "cannot be measured" argued."""
    root = write_log(tmp_path / "scorecards", CHANGE)   # a repair, no verdicts_moved
    put_card(root, "round-one", "20260806-P-p1", "3e721a5")
    results, _ = st.run_audit(root)
    assert any("declaring neither" in m for level, m in results["R-H3"] if level == st.OPEN)

    root2 = write_log(tmp_path / "scorecards2", CHANGE.replace(
        'summary = "a declaration could erase a demonstrated kill"',
        'verdicts_unmeasurable = "the two sides scored different artifacts"\n'
        'summary = "a declaration could erase a demonstrated kill"'))
    put_card(root2, "round-one", "20260806-P-p1", "3e721a5")
    results2, _ = st.run_audit(root2)
    assert any("no verdict diff exists, and says why" in m for _, m in results2["R-H3"])
    assert not [m for level, m in results2["R-H3"] if level == st.OPEN]


# --------------------------------------------------------------------------
# SM-04's gap mutant: what removing `total` cost, measured rather than asserted.
#
# `removal_is_a_delta_rule`: a removal with no mutant in its gap is not a
# measurement. SM-01 seeded for the two cuts it knew about and neither is this
# one, so this gap is seeded here. Both ends are measured in ONE RUN -- the
# before-side detector is `check` on a version 2 card, which still exists at
# this commit -- so there is no instrument change between the two readings.
#
# THE GAP: `total` was a checksum over the five scores. `check`'s
# `total != running` was the only thing that noticed a score altered in
# `scorecard.json` after the card was written.
# --------------------------------------------------------------------------

def _mutate_a_score(card: dict) -> dict:
    """The mutant: D3 falls from 4 to 2, and nothing else in the card moves."""
    card = json.loads(json.dumps(card))
    assert card["dimensions"]["D3"]["score"] == 4
    card["dimensions"]["D3"]["score"] = 2
    return card


def _seal_and_audit(st, tmp_path, card: dict, name: str):
    """Seal a card, then mutate it on disk and ask `audit` R-H4 about it."""
    root = tmp_path / name / "scorecards"
    d = root / "round" / "ab_quota_ledger" / card["run_id"]
    d.mkdir(parents=True)
    path = d / "scorecard.json"
    path.write_text(json.dumps(card, indent=2))
    (root / "INSTRUMENT-LOG.toml").write_text("schema_version = 1\n")
    # `seal` records paths relative to REPO_ROOT, so it needs the card inside it
    digest = "sha256:" + __import__("hashlib").sha256(path.read_bytes()).hexdigest()[:16]
    rel = str(path)
    (root / "INSTRUMENT-LOG.toml").write_text(
        f'schema_version = 1\n\n[[sealed]]\npath = "{rel}"\nsha256 = "{digest}"\n')
    path.write_text(json.dumps(_mutate_a_score(card), indent=2))
    results, _ = st.run_audit(root)
    return [m for level, m in results["R-H4"] if level == st.VIOLATION]


def test_the_price_of_removing_total_measured_on_both_sides(st, tmp_path, capsys):
    """SM-04-GM-T1. Seeded in the gap `total` covered, read before and after.

    SEALED: still dies. The seal digest catches it, and a seal digest is
    strictly stronger than the sum -- it covers all five scores, every citation
    and every rationale. REDUNDANT, the cut was free.

    UNSEALED: NOW SURVIVES. That is the price and it is reported rather than
    absorbed. Nothing detects a score altered after the fact on an unsealed
    version 3 card, where the arithmetic used to. `audit` already reports OPEN
    when no seal digests exist at all, which is the only warning left.
    """
    four = {"score": 4, "citations": ["quota_ledger/domain.py:22-43"],
            "refuses_to_claim": "that anything but the durable side is behind a port"}

    # --- BEFORE: a version 2 card, `total` present -------------------------
    epic2 = tmp_path / "v2"
    assert scaffold(st, epic2, labels="K,L,M", card_version=2) == 0
    capsys.readouterr()
    p2 = one_card(epic2)
    v2 = fill(json.loads(p2.read_text()), D3=dict(four))
    assert st.check(v2, str(p2), st.load_rubric(RUBRIC))[0] == [], "control: card is clean"
    before_unsealed = [p for p in st.check(_mutate_a_score(v2), str(p2),
                                           st.load_rubric(RUBRIC))[0]
                       if "does not equal the sum" in p]
    before_sealed = _seal_and_audit(st, tmp_path, v2, "before")

    # --- AFTER: a version 3 card, no `total` -------------------------------
    path, card = scaffolded(st, tmp_path / "v3")
    capsys.readouterr()
    v3 = fill(card, D3=dict(four))
    assert st.check(v3, str(path), st.load_rubric(RUBRIC))[0] == [], "control: card is clean"
    after_unsealed = st.check(_mutate_a_score(v3), str(path), st.load_rubric(RUBRIC))[0]
    after_sealed = _seal_and_audit(st, tmp_path, v3, "after")

    # SEALED: dies before, dies after. The cut was free.
    assert before_sealed and any("HAS BEEN EDITED" in m for m in before_sealed)
    assert after_sealed and any("HAS BEEN EDITED" in m for m in after_sealed)

    # UNSEALED: died before, SURVIVES after. This is the price.
    assert before_unsealed, "the version 2 arithmetic did not catch the mutant"
    assert after_unsealed == [], (
        "something still catches an altered score on an unsealed version 3 card -- "
        "re-price the removal, the recorded verdict says nothing does")


def test_a_split_goal_verdict_is_two_claims_and_renders_as_two(st, capsys):
    """`GOAL-port-reach` is clause 1 met, clause 2 NOT met. A ledger that stores
    one token per goal has to choose, and it will choose the flattering one."""
    st.main(["history", "--example", "ab_quota_ledger", "--root", str(SCORECARDS)])
    out = capsys.readouterr().out
    one = next(l for l in out.splitlines() if l.startswith("| `goal-port-reach-clause-1` |"))
    two = next(l for l in out.splitlines() if l.startswith("| `goal-port-reach-clause-2` |"))
    assert "MET" in one and "NOT MET" in two
    assert one != two


def test_a_scorecard_verdict_is_free_text_not_a_token(st, tmp_path, capsys):
    """The card's own `verdict` never had to be one word either, so a split
    reads through the scaffold and the schema check unchanged."""
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    fill(card)
    card["verdict"] = "clause 1 met; clause 2 NOT met -- four positive controls are red"
    problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC))
    assert problems == []


def test_known_wrong_must_say_why(st, tmp_path):
    root = write_log(tmp_path / "scorecards", CHANGE + """
[[claim]]
id = "controls-green"
example = "ex"
status = "known_wrong"
measured_at = "24ed3fa"
date = "2026-08-04"
statement = "controls green on both arms"
""")
    put_card(root, "round-one", "20260804-P-p1", "24ed3fa")
    results, _ = st.run_audit(root)
    assert any("known_wrong with no `why`" in m
               for level, m in results["R-H3"] if level == st.VIOLATION)


def test_an_era_boundary_that_changed_no_instrument_is_a_violation(st, tmp_path):
    """A declared instrument change that touched none of its declared paths is
    a fictional boundary, and a fictional boundary is worse than none."""
    root = write_log(tmp_path / "scorecards", """
schema_version = 1

[[change]]
id = "MADE-UP"
commit = "3e721a5"
date = "2026-08-05"
kind = "repair"
affects = ["ex"]
paths = ["references/eval_scorecard.md"]
summary = "claims to have changed the rubric and did not"
""")
    put_card(root, "round-one", "20260806-P-p1", "3e721a5")
    results, _ = st.run_audit(root)
    assert any("touches NONE of its declared instrument paths" in m
               for level, m in results["R-H1"] if level == st.VIOLATION)


def test_a_row_on_the_wrong_side_of_a_change_with_no_note_is_reported(st, tmp_path):
    root = write_log(tmp_path / "scorecards", CHANGE)
    put_card(root, "round-one", "20260804-P-p1", "24ed3fa")
    results, _ = st.run_audit(root)
    assert any("carries no note" in m for level, m in results["R-H1"] if level == st.OPEN)


def test_a_note_about_a_card_that_does_not_exist_is_a_violation(st, tmp_path):
    root = write_log(tmp_path / "scorecards", CHANGE + """
[[note]]
id = "N-01"
about = "card:round-one/ex/does-not-exist"
kind = "note"
why = "about nothing"
""")
    put_card(root, "round-one", "20260804-P-p1", "24ed3fa")
    results, _ = st.run_audit(root)
    assert any("is not a card in this tree" in m
               for level, m in results["R-H2"] if level == st.VIOLATION)


def test_a_claim_over_more_than_one_example_is_a_violation(st, tmp_path):
    """Never average across examples: a deliberately incoherent fixture is
    SUPPOSED to score low on D3."""
    root = write_log(tmp_path / "scorecards", CHANGE + """
[[claim]]
id = "mean-of-everything"
example = ["ex", "ex6_jenga"]
status = "current"
measured_at = "24ed3fa"
statement = "mean D3 across the corpus is 2.4"
""")
    put_card(root, "round-one", "20260804-P-p1", "24ed3fa")
    results, _ = st.run_audit(root)
    assert any("number over more than one example" in m
               for level, m in results["R-H2"] if level == st.VIOLATION)


def test_history_has_no_cross_example_mode(st):
    with pytest.raises(SystemExit):
        st.main(["history", "--root", str(SCORECARDS)])


def test_editing_a_sealed_card_is_detected(st, tmp_path):
    root = tmp_path / "scorecards"
    d = put_card(root, "round-one", "20260804-P-p1", "24ed3fa")
    card = d / "scorecard.json"
    rel = "specs/results/scorecards/hexagonal-prompting/ab_quota_ledger/20260804-hp06-X-p1/scorecard.json"
    write_log(root, f"""
schema_version = 1

[[sealed]]
path = "{rel}"
sha256 = "sha256:0000000000000000"
""")
    results, _ = st.run_audit(root)
    assert any("HAS BEEN EDITED" in m for level, m in results["R-H4"] if level == st.VIOLATION)
    assert card.exists()


def test_seal_refuses_to_reseal_a_card_whose_contents_changed(st, tmp_path, capsys):
    """Sealing is how R-H4 becomes checkable at all, so re-sealing must not be a
    way to launder an edit into the record."""
    root = tmp_path / "scorecards"
    real = REPO_ROOT / "specs/results/scorecards/hexagonal-prompting"
    write_log(root, 'schema_version = 1\n\n[[sealed]]\npath = '
                    '"specs/results/scorecards/hexagonal-prompting/ab_quota_ledger/'
                    '20260804-hp06-X-p1/scorecard.json"\nsha256 = "sha256:ffffffffffffffff"\n')
    assert st.main(["seal", str(real), "--root", str(root)]) == 3
    err = capsys.readouterr().err
    assert "REFUSED" in err and "never edited" in err
    # nothing was appended: the refusal is total, not per-file
    assert "20260804-hp06-Y-p1" not in (root / "INSTRUMENT-LOG.toml").read_text()


# --------------------------------------------------------------------------
# the reading rules are executed, not merely written down
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# R-H5: a movement is a measurement only if the practice is recorded
# --------------------------------------------------------------------------

def put_card_v2(root: Path, round_dir: str, run_id: str, commit: str, example="ex",
                arm="P", scores=None, practice=True):
    d = root / round_dir / example / run_id
    d.mkdir(parents=True, exist_ok=True)
    scores = scores or {dim: 1 for dim in st_dims()}
    card = {
        "scorecard_version": 2, "epic": round_dir, "example": example, "run_id": run_id,
        "arm": arm, "commit": commit,
        "judge": {"model": "m", "pass": 1, "blind_to_arm": True},
        "dimensions": {k: {"score": v, "citations": [], "rationale": "r"}
                       for k, v in scores.items()},
        "total": sum(scores.values()), "contested": [], "verdict": "v",
    }
    if practice is not None:
        card["judging_practice"] = {"executed_own_faults": practice,
                                    "what_was_run": ["ran a fault"] if practice else []}
    (d / "scorecard.json").write_text(json.dumps(card))
    return d


MOVEMENT_LOG = """
schema_version = 1

[[movement]]
id = "{id}"
example = "ex"
dimension = "D4"
from_card = "{frm}"
to_card = "{to}"
points = {points}
readable = {readable}
"""


def _movement_audit(st, tmp_path, **kw):
    root = tmp_path / "scorecards"
    put_card(root, "round1", "20260805-P-p1", "3e721a5")            # v1: no practice
    put_card_v2(root, "round2", "20260806-P-p1", "3e721a5",
                scores={"D1": 1, "D2": 1, "D3": 1, "D4": 3, "D5": 1})
    put_card_v2(root, "round3", "20260806-Q-p1", "3e721a5",
                scores={"D1": 1, "D2": 1, "D3": 1, "D4": 4, "D5": 1})
    write_log(root, MOVEMENT_LOG.format(**kw))
    return st.run_audit(root)[0]["R-H5"]


def test_a_declared_movement_is_re_derived_from_the_cards_every_time(st, tmp_path):
    """A DEMONSTRATED FAILING INPUT for the rule: a row that stopped being true.

    The movement claims three points; the two cards it names say one. Nobody had
    to notice -- the audit recomputes it from the cards on every run.
    """
    found = _movement_audit(st, tmp_path, id="stale", frm="round2/ex/20260806-P-p1",
                            to="round3/ex/20260806-Q-p1", points=3, readable="true")
    assert any(level == st.VIOLATION and "declares `points = 3`" in msg and "(+1)" in msg
               for level, msg in found), found


def test_a_movement_read_across_a_card_that_says_nothing_about_its_judge(st, tmp_path):
    """The instability caveat, executed. The v1 card records no practice, so the
    movement across it is not readable however real it is."""
    found = _movement_audit(st, tmp_path, id="across-v1", frm="round1/ex/20260805-P-p1",
                            to="round3/ex/20260806-Q-p1", points=3, readable="true")
    assert any(level == st.VIOLATION and "records no `judging_practice`" in msg
               and "DO NOT READ THE MOVEMENT" in msg for level, msg in found), found


def test_the_same_movement_declared_unreadable_is_accepted_and_says_why(st, tmp_path):
    found = _movement_audit(st, tmp_path, id="across-v1", frm="round1/ex/20260805-P-p1",
                            to="round3/ex/20260806-Q-p1", points=3, readable="false")
    assert any(level == st.OK and "within demonstrated noise" in msg.lower()
               for level, msg in found), found


def test_a_movement_between_two_cards_that_both_say_so_is_readable(st, tmp_path):
    found = _movement_audit(st, tmp_path, id="both-ends", frm="round2/ex/20260806-P-p1",
                            to="round3/ex/20260806-Q-p1", points=1, readable="true")
    assert any(level == st.OK and "recorded at both ends -- readable" in msg
               for level, msg in found), found


def test_a_movement_naming_a_card_that_does_not_exist_is_a_violation(st, tmp_path):
    found = _movement_audit(st, tmp_path, id="ghost", frm="round9/ex/nope",
                            to="round3/ex/20260806-Q-p1", points=1, readable="false")
    assert any(level == st.VIOLATION and "is not a card in this tree" in msg
               for level, msg in found), found


def test_a_movement_that_does_not_say_whether_it_is_readable_is_a_violation(st, tmp_path):
    root = tmp_path / "scorecards"
    put_card_v2(root, "r1", "a", "3e721a5", scores={d: 1 for d in st_dims()})
    put_card_v2(root, "r2", "b", "3e721a5", scores={d: 2 for d in st_dims()})
    write_log(root, """
schema_version = 1

[[movement]]
id = "silent"
example = "ex"
dimension = "D4"
from_card = "r1/ex/a"
to_card = "r2/ex/b"
points = 1
""")
    found = st.run_audit(root)[0]["R-H5"]
    assert any(level == st.VIOLATION and "declares no `readable`" in msg
               for level, msg in found), found


def test_the_shipped_rh5_demonstration_still_goes_red(st):
    """R1: an instrument ships a DEMONSTRATED FAILING INPUT, and the
    demonstration is re-runnable rather than a paragraph.

    `demonstrate_rh5.py` copies the live scorecard tree, confirms `audit` is
    green on the copy, breaks it in the two ways R-H5 exists to catch, and exits
    non-zero if either break fails to produce a violation. Running it from the
    suite is what stops the demonstration from quietly stopping working, which
    is the class of artifact this epic is about.
    """
    script = (SCORECARDS / "falsifiable-instruments/GOAL-scorecard-carries-a-delta"
              / "measure/demonstrate_rh5.py")
    assert script.exists(), script
    proc = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "goes RED on both of the inputs it exists to catch" in proc.stdout


def test_every_reading_rule_in_the_doc_has_a_check(st, rubric):
    """A declaration that nothing executes will drift. The rubric's R-H rules
    and the audit's checks are the same set, in both directions."""
    declared = {r["id"] for r in rubric["reading_rules"]}
    assert declared, "references/eval_scorecard.md declares no R-H reading rules"
    assert declared == set(st.AUDIT_CHECKS), (declared, set(st.AUDIT_CHECKS))


def test_the_audit_fails_when_the_doc_declares_a_rule_with_no_check(st, tmp_path, capsys):
    rubric_copy = tmp_path / "eval_scorecard.md"
    text = RUBRIC.read_text().replace(
        "### R-H4 — A sealed card is never edited",
        "### R-H9 — A rule nobody implemented\n\nNothing executes this.\n\n"
        "### R-H4 — A sealed card is never edited")
    rubric_copy.write_text(text)
    assert st.main(["audit", "--root", str(SCORECARDS), "--rubric", str(rubric_copy),
                    "--quiet-ok"]) == 1
    assert "R-H9" in capsys.readouterr().out


# --------------------------------------------------------------------------
# over the real ledger: the five worked examples
# --------------------------------------------------------------------------

def test_the_repo_ledger_passes_its_own_audit(st, capsys):
    assert st.main(["audit", "--root", str(SCORECARDS), "--quiet-ok"]) == 0
    capsys.readouterr()


def test_history_marks_the_instrument_change_between_the_two_rounds(st, capsys):
    """HP-06's rows and EVAL-RERUN's rows are on opposite sides of EVAL-STABLE,
    and EVAL-SUPPRESS post-dates BOTH -- so the rerun's numbers came from a
    driver repaired afterwards."""
    assert st.main(["history", "--example", "ab_quota_ledger", "--root", str(SCORECARDS)]) == 0
    out = capsys.readouterr().out
    hp06 = out.index("20260804-hp06-X-p1")
    stable = out.index("INSTRUMENT CHANGE — `EVAL-STABLE`")
    rerun = out.index("20260804-rerun-Q-p1")
    suppress = out.index("INSTRUMENT CHANGE — `EVAL-SUPPRESS`")
    assert hp06 < stable < rerun < suppress
    assert "NOT COMPARABLE" in out
    assert out.index("`PA-01-three-arms`") > suppress


def test_history_separates_an_attribution_correction_from_a_gain(st, capsys):
    """The two worked examples that must never be read the same way: guard
    relaxation 0 -> 3 of 3 is a mechanism gain; D1 = 3 appearing on BOTH arms is
    an attribution correction."""
    st.main(["history", "--example", "ab_quota_ledger", "--root", str(SCORECARDS)])
    out = capsys.readouterr().out
    assert "REAL MECHANISM GAIN" in out
    assert "within_run" in out
    assert "AN ATTRIBUTION CORRECTION, NOT A GAIN" in out
    assert "under_review" in out


def test_history_marks_the_known_wrong_controls_row(st, capsys):
    """'controls green on both arms' is a sealed number known-wrong for one arm.
    The card is not edited; the ledger records which number and why, beside it."""
    st.main(["history", "--example", "ab_quota_ledger", "--root", str(SCORECARDS)])
    out = capsys.readouterr().out
    assert "controls-green-both-arms" in out
    assert "known_wrong" in out
    assert "KNOWN-WRONG FOR ONE ARM" in out
    # and the arm-B judges' cards carry the note beside them
    assert "PA-05-N-08" in out


def test_history_marks_the_superseded_49_of_49_baseline(st, capsys):
    """A superseded row read forward as current through a whole dispatch."""
    st.main(["history", "--example", "ab_quota_ledger", "--root", str(SCORECARDS)])
    out = capsys.readouterr().out
    assert "ab-cells-identical-49" in out
    assert "superseded" in out
    assert "ab-cells-identical-56" in out


def test_history_records_the_refuted_finding_beside_the_claim_it_doubted(st, capsys):
    """PA-05 filed PA-05-DF-02 claiming EVAL-SUPPRESS's one flipped cell was
    inside the 56 comparable cells. The owner refuted it from the sealed raw
    tables; the general hazard was then discharged by PA-03's re-derivation.
    Both halves are on the record: the baseline is `current` and re-affirmed,
    and the wrong assertion is kept as `refuted` rather than deleted."""
    st.main(["history", "--example", "ab_quota_ledger", "--root", str(SCORECARDS)])
    out = capsys.readouterr().out
    assert "df02-flipped-cell-inside-the-comparable-set" in out
    assert "refuted" in out and "the epic owner" in out
    assert "PA-05-DF-02" in out                      # the filing stays reachable
    assert "PA-05-N-11" in out                       # and its one arithmetic caveat
    # The baseline it doubted was re-affirmed by PA-03 -- and is parked AGAIN,
    # under a NEW and narrower finding, because PA-04 then added two more
    # instrument changes and nobody has re-derived the seven-column table since.
    # `reaffirmed_at` stays on the claim: it records that PA-03 did discharge
    # the original doubt, which is not the same as the claim being safe now.
    line = next(l for l in out.splitlines()
                if l.startswith("| `ab-cells-identical-56` |"))
    assert "**under_review** (PA-05-DF-03)" in line, line
    assert "PA-05-DF-02" not in line, "DF-02's doubt was discharged; do not re-hang it here"


def test_history_marks_the_inverted_d5_attribution(st, capsys):
    """PA-05-DF-01: PORTS-AS-ADAPTERS-EPIC.md section 6 says the best-ever
    D5 = 4 'went to the control, not the treatment'. True of HP-06's sealed run;
    false under the rerun, where it went to the TREATMENT and the control fell."""
    st.main(["history", "--example", "ab_quota_ledger", "--root", str(SCORECARDS)])
    out = capsys.readouterr().out
    assert "best-d5-4-went-to-control" in out
    assert "PA-05-N-10" in out
    assert "the 4 went to the TREATMENT" in out
    # and it is readable straight off the rows: control 4 in era 0, 3 in era 1
    assert out.index("20260804-hp06-Y-p1") < out.index("20260804-rerun-P-p1")


def test_the_committed_history_rendering_is_current(st, capsys, tmp_path):
    """The rendered view is committed beside the ledger so a reader does not
    have to run anything. A committed rendering that nothing regenerates is the
    same class of stale artifact this ticket is about."""
    out_path = tmp_path / "HISTORY.md"
    assert st.main(["history", "--example", "ab_quota_ledger", "--root", str(SCORECARDS),
                    "--write", str(out_path)]) == 0
    capsys.readouterr()
    committed = SCORECARDS / "HISTORY-ab_quota_ledger.md"
    assert committed.exists()
    assert out_path.read_text() == committed.read_text()
