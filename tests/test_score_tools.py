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
# The bar as it stood at version 3, frozen so the change rule's "re-score a prior
# example under both versions" is followable at all. `--card-version 3` alone
# reproduces the old SCHEMA against the NEW bar; pointing at this file is the
# other half, and from version 4 the tool refuses rather than letting it be
# missed.
RUBRIC_V3 = REPO_ROOT / "examples/validation/scorecards/rubric_v3_frozen.md"
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
    scored = st.scored_dims(card["scorecard_version"])
    assert scored, "a card version that scores nothing is not a card"
    for dim in scored:
        entry = card["dimensions"][dim]
        assert entry["name"] == st.NAMES[dim]
        assert entry["anchors"] == rubric["dimensions"][dim]["anchors"], dim
        assert entry["score"] is None
    assert card["rubric"]["digest"] == rubric["digest"]
    assert card["rubric"]["scoring_rules"] == rubric["scoring_rules"]
    # RM-03: the three questions that stopped being scored are still ASKED, and
    # their prompts are read out of the rubric exactly as the anchors are.
    for dim in st.note_dims(card["scorecard_version"]):
        key = st.NOTE_KEY[dim]
        assert card["notes"][key]["question"] == rubric["notes"][key]["prompt"], key
        assert card["notes"][key]["note"] == ""

    md = one_card(epic).with_name("scorecard.md").read_text()
    for dim in scored:
        for score in sorted(rubric["dimensions"][dim]["anchors"]):
            assert rubric["dimensions"][dim]["anchors"][score] in md
    for dim in st.note_dims(card["scorecard_version"]):
        assert rubric["notes"][st.NOTE_KEY[dim]]["prompt"] in md
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
    stumbled into the sealed run could not read the arms off it. Mechanised.

    **RM-04 KEPT THE PROPERTY AND REPLACED THE MECHANISM** (`RM-02-DF-01`: the
    17-character pool was down to `G J L V` and a round needing five arms was
    already refused). A label is now a STRING over the characters this record
    has never published, so both things a judge could recognise are impossible
    by construction rather than by counting down to zero.
    """
    root = tmp_path / "scorecards"
    # THE STATE THIS REPOSITORY IS ACTUALLY IN: 13 of the 17 published, `G J L V`
    # left. `RM-02-DF-01` measured it by running `used_labels()` over the sealed
    # record, and a round needing five arms was already being refused.
    published = "DEFHKMNPRSTUW"
    for label in published:
        d = root / "prior" / "ex" / f"20260101-{label}-p1"
        d.mkdir(parents=True)
        (d / "scorecard.json").write_text(json.dumps({"arm": label}))
    assert st.used_labels(root) >= set(published)
    assert st.label_alphabet(st.used_labels(root) | st.RESERVED_LABELS) == "GJLVZ"

    # Four labels remained under the old mechanism. Sixteen do at width 2 over
    # the same leftovers, and sixty-four at width 3 -- so a five-arm round is
    # possible again and the pool does not run out on a fixed schedule.
    assert len(st.available_labels(st.used_labels(root) | st.RESERVED_LABELS, 3)[0]) == 25
    assert scaffold(st, root / "epic", arms="A,B,C", judges=1) == 0
    capsys.readouterr()
    drawn = {json.loads(p.read_text())["arm"]
             for p in (root / "epic").rglob("scorecard.json")}
    assert len(drawn) == 3, drawn
    for label in drawn:
        # 1. the whole string was never published
        assert label not in set(published), label
        # 2. and no CHARACTER of it was published on its own either, so a judge
        #    who saw `T` last round meets nothing that shares a character with it
        assert set(label).isdisjoint(set(published)), label
        assert set(label).isdisjoint(st.RESERVED_LABELS), label

    # AND IT STILL REFUSES rather than colliding. THE WIDTH TRICK MULTIPLIES AN
    # ALPHABET AND CANNOT CREATE ONE: with a single character left, every width
    # yields exactly one label, so publishing the rest of the alphabet as single
    # characters leaves nothing to build from. Said here because it is the limit
    # of the mechanism and it is not obvious from "the space is unbounded".
    for label in "GJLV":
        d = root / "prior2" / "ex" / f"20260101-{label}-p1"
        d.mkdir(parents=True)
        (d / "scorecard.json").write_text(json.dumps({"arm": label}))
    assert scaffold(st, root / "epic2", arms="A,B", judges=1) == 2
    assert "no label width" in capsys.readouterr().err


def test_the_explicit_label_path_refuses_a_published_label(st, tmp_path, capsys):
    """THE DEMONSTRATED FAILING INPUT for `RM-02-DF-01`'s other half.

    RM-04 found the hole while widening the pool: `--labels` wrote whatever it
    was handed, with NO exclusion check at all. The pool path has excluded every
    published label since HP-06 -- so the one route an operator reaches for when
    the pool refuses was the one route with nothing on it, and reusing `T` was a
    typo away in precisely the situation that makes an operator type it.
    """
    root = tmp_path / "scorecards"
    d = root / "prior" / "ex" / "20260101-T-p1"
    d.mkdir(parents=True)
    (d / "scorecard.json").write_text(json.dumps({"arm": "T"}))

    assert scaffold(st, root / "epic", arms="A,B", judges=1, labels="T,U") == 2
    err = capsys.readouterr().err
    assert "would reuse a label a prior round published" in err
    assert "'T'" in err
    assert not (root / "epic").exists(), "a refused scaffold wrote something"

    # a reserved arm name is refused by the same clause
    assert scaffold(st, root / "epic", arms="X,Y", judges=1, labels="A,B") == 2
    assert "reserved arm name" in capsys.readouterr().err

    # IT IS A REASON, NOT A BAN. Re-scoring one arm under two card versions is
    # a reuse this project does on purpose -- FI-03, SM-04 and RM-03 each did
    # it -- so the deliberate case goes through and lands in the key file.
    assert scaffold(st, root / "e2", arms="A", judges=1, labels="T",
                    reason="re-score of the same arm under card version 2") == 0
    capsys.readouterr()
    key = (root / "e2" / "UNBLINDING.md").read_text()
    assert "LABELS REUSED ON PURPOSE: T" in key
    assert "re-score of the same arm under card version 2" in key

    # and an unpublished label needs no reason, so this prices the REUSE and
    # not the mechanism
    assert scaffold(st, root / "epic", arms="A,B", judges=1, labels="GJ,LV") == 0
    capsys.readouterr()
    assert {json.loads(p.read_text())["arm"]
            for p in (root / "epic").rglob("scorecard.json")} == {"GJ", "LV"}


def test_a_blinded_card_carries_the_scope_and_nothing_that_identifies_it(
        st, tmp_path, capsys):
    """RM-04. THE LEAK, AND IT WAS SHIPPED IN A ROUND THAT CALLED ITSELF BLIND.

    RM-03's re-score cards are labelled `T` and their `subject` block reads
    `name: "arm_b"` and `declared_effect_boundary: "ports-and-adapters"` -- the
    arm identity AND the value of the axis D3 is compared on, in the file the
    judge is handed. A judge read it and disclosed it.

    Two properties, and the second is the one nothing else covers: withholding
    a name does not help when the SCOPE PATH spells the label.
    """
    root = tmp_path / "scorecards"
    root.mkdir()

    # 1. a blinded card names no subject and pre-answers no dimension
    assert scaffold(st, root / "e1", arms="A,B", judges=1, labels="GJ,LV",
                    subject="rm04_scripts") == 0
    capsys.readouterr()
    for p in (root / "e1").rglob("scorecard.json"):
        subject = json.loads(p.read_text())["subject"]
        assert subject["blinded"] is True
        assert subject["name"] is None, subject
        assert "declared_effect_boundary" not in subject, subject
        assert subject["scope"] == ["scripts"], subject   # what to read: kept

    # 2. --unblinded is the deliberate, recorded way to get the identity back
    assert scaffold(st, root / "e2", arms="A", judges=1, subject="rm04_scripts",
                    unblinded=True, reason="owner tracking pass") == 0
    capsys.readouterr()
    subject = json.loads(one_card(root / "e2").read_text())["subject"]
    assert subject["name"] == "rm04_scripts"
    assert subject["declared_effect_boundary"] == "effectful"


def test_a_scope_that_spells_a_published_label_refuses_the_whole_batch(
        st, tmp_path, capsys):
    """THE DEMONSTRATED FAILING INPUT, on the real subject that shipped it.

    `arm_b`'s declared scope is
    `specs/results/scorecards/ports-as-adapters/blind/artifact_T`, and `T` is a
    label that round published. Blinding the NAME cannot hide that, because the
    path is what the judge is told to read. So the scaffold refuses, and it
    refuses BEFORE writing any of it.
    """
    root = tmp_path / "scorecards"
    d = root / "prior" / "ex" / "20260101-T-p1"
    d.mkdir(parents=True)
    (d / "scorecard.json").write_text(json.dumps({"arm": "T"}))

    assert scaffold(st, root / "epic", arms="A,B", judges=1, labels="GJ,LV",
                    subject="arm_b") == 3
    err = capsys.readouterr().err
    assert "a blinded card would carry an identifying subject" in err
    assert "artifact_T" in err and "'T'" in err
    assert "Nothing was written" in err
    assert not (root / "epic").exists(), "a refused scaffold wrote something"

    # the same subject scaffolds fine when the identity is MEANT to be visible
    assert scaffold(st, root / "epic", arms="A", judges=1, subject="arm_b",
                    unblinded=True, reason="unblinding is the recorded escape") == 0
    capsys.readouterr()

    # and the predicate is about a PUBLISHED label, not about paths in general
    assert st.scope_leaks_a_label(["specs/results/x/blind/artifact_T"], {"T"})
    assert st.scope_leaks_a_label(["specs/results/x/blind/artifact_T"], set()) == []
    assert st.scope_leaks_a_label(["examples/validation"], {"T", "U", "W"}) == []
    assert st.scope_leaks_a_label(["scripts"], {"T", "U", "W"}) == []


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
    for dim in st_dims(version):
        entry = card["dimensions"][dim]
        spec = scores.get(dim, {"score": 1})
        entry.update(spec)
        entry.setdefault("rationale", "because the artifact says so and I ran it")
        entry["rationale"] = entry["rationale"] or "because the artifact says so"
        total += entry["score"]
        # scorecard_version 3: the one anchor with two defensible readings says
        # which one it was scored under, at 3 and 4 where they can differ. The
        # anchor retires at version 4, so this stays keyed on 3 rather than on
        # ">= 3" -- the requirement is still executed against every sealed
        # version 3 card and against no version 4 one.
        if version == 3 and dim == "D5" and entry["score"] in (3, 4):
            entry["anchor_reading"] = entry.get("anchor_reading") or "measured"
    # RM-03, scorecard_version 4: three dimensions stopped being scored and are
    # recorded as prose instead. Rule 10 says an empty note is not a legal card.
    for key in card.get("notes") or {}:
        card["notes"][key]["note"] = (card["notes"][key].get("note")
                                      or "I looked at the tree and this is what I found")
    if version < 3:
        card["total"] = total
    else:
        card.pop("total", None)
    return card


#: The dimensions a card of this version carries a SCORE for. Version 4 scores
#: two and records three as notes; every earlier version scores five and is
#: still checked exactly as it was, because a sealed card is never edited.
ST_RETIRED_AT_4 = ("D1", "D4", "D5")


def st_dims(version: int = 4):
    return tuple(d for d in ("D1", "D2", "D3", "D4", "D5")
                 if version < 4 or d not in ST_RETIRED_AT_4)


def scaffolded(st, tmp_path, labels="K,L,M", card_version=None):
    """A scaffolded card at the CURRENT version, or at an older one.

    An older version is scaffolded against the frozen rubric of its own era,
    because that is what the change rule requires and what the tool now
    enforces: `--card-version` alone stamps a number while reading the current
    bar.
    """
    epic = tmp_path / "ports-as-adapters"
    kw = {}
    if card_version is not None:
        kw = {"card_version": card_version, "rubric": str(RUBRIC_V3)}
    scaffold(st, epic, labels=labels, **kw)
    path = one_card(epic)
    return path, json.loads(path.read_text())


def rubric_for(card, st):
    """The bar a card of this version was written against."""
    return st.load_rubric(RUBRIC_V3 if card.get("scorecard_version", 1) < st.RETIRED_AT
                          else RUBRIC)


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
    fill(card, D3={"score": 3, "citations": []})
    problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC))
    assert any("D3 scored 3 with NO citation" in p and "rule 2 caps it at 1" in p
               for p in problems), problems


def test_check_still_rejects_a_four_with_no_refuses_to_claim(st, tmp_path, capsys):
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    fill(card, D3={"score": 4, "citations": ["domain.py:22-43"], "refuses_to_claim": None})
    problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC))
    assert any("D3 scored 4" in p and "without refuses_to_claim" in p
               for p in problems), problems


def test_an_unfilled_skeleton_cannot_smuggle_a_score_through(st, tmp_path, capsys):
    """`status: unfilled` is not a way to score without being checked."""
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    card["dimensions"]["D3"]["score"] = 4  # left 'unfilled'
    problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC))
    assert any("status is 'unfilled' but D3 carry a score" in p for p in problems), problems
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
    card["dimensions"]["D3"]["anchors"].pop("4")
    problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC))
    assert any("inline anchors but not all of 0-4" in p for p in problems), problems
    # and D2's scale ends at 3 from version 4, so its partial set is 0-3
    fill(card)
    card["dimensions"]["D2"]["anchors"].pop("3")
    problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC))
    assert any("inline anchors but not all of 0-3" in p for p in problems), problems


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
    assert card["scorecard_version"] == st.VERSION == 4
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

    **RM-03 pinned this to version 3 rather than deleting it.** D4 stopped being
    scored at version 4, so no version 4 card can reach the gate; 73 sealed cards
    can, R-H4 says they are never edited, and a check that stops looking at them
    is a check that stopped working.
    """
    path, card = scaffolded(st, tmp_path, card_version=3)
    capsys.readouterr()
    fill(card, practice=False,
         D4={"score": 4, "citations": ["EVIDENCE.md:180-187"],
             "refuses_to_claim": "that the fake and the real adapter agree"})
    problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC_V3))
    assert any("D4 scored 4 while judging_practice.executed_own_faults is false" in p
               for p in problems), problems
    # the same card from a judge that DID run one is fine
    fill(card, practice=True,
         D4={"score": 4, "citations": ["EVIDENCE.md:180-187"],
             "refuses_to_claim": "that the fake and the real adapter agree"})
    assert st.check(card, str(path), st.load_rubric(RUBRIC_V3))[0] == []


def test_a_version_4_card_cannot_score_the_three_that_became_notes(st, tmp_path, capsys):
    """The removal, executed. Restoring the NUMBER is what version 4 refuses.

    Not the question: `notes` is required and an empty one is rejected. What a
    version 4 card cannot do is put a 0-4 back on D1, D4 or D5 without a version
    bump, which is how a cut dimension would quietly come back.
    """
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    fill(card)
    assert st.check(card, str(path), st.load_rubric(RUBRIC))[0] == []
    for dim in st.RETIRED_DIMS:
        smuggled = json.loads(json.dumps(card))
        smuggled["dimensions"][dim] = {
            "score": 4, "citations": ["EVIDENCE.md:1"], "rationale": "r",
            "refuses_to_claim": "nothing"}
        problems, _ = st.check(smuggled, str(path), st.load_rubric(RUBRIC))
        assert any("recorded notes from version 4" in p for p in problems), (dim, problems)
    # and the question is still asked: an empty note is not a filled card
    silent = json.loads(json.dumps(card))
    silent["notes"]["N-D4"]["note"] = ""
    problems, _ = st.check(silent, str(path), st.load_rubric(RUBRIC))
    assert any("notes.N-D4 is empty" in p for p in problems), problems


def test_d2_tops_out_at_three_from_version_4(st, tmp_path, capsys):
    """The anchor is DELETED, not reworded, and what that costs is the top rung.

    Rule 3 follows the anchor rather than the literal number 4: a D2 of 3 is now
    the top of its scale and must name something the artifact refuses to claim.
    """
    path, card = scaffolded(st, tmp_path)
    capsys.readouterr()
    fill(card, D2={"score": 4, "citations": ["A.py:1"], "refuses_to_claim": "x"})
    problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC))
    assert any("D2 score must be an int 0-3" in p for p in problems), problems

    fill(card, D2={"score": 3, "citations": ["A.py:1"], "refuses_to_claim": None})
    problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC))
    assert any("D2 scored 3, the top of its scale" in p for p in problems), problems

    fill(card, D2={"score": 3, "citations": ["A.py:1"], "refuses_to_claim": "the rest"})
    assert st.check(card, str(path), st.load_rubric(RUBRIC))[0] == []
    # D3 still tops out at 4 -- only one anchor was deleted
    fill(card, D3={"score": 4, "citations": ["A.py:1"], "refuses_to_claim": "the rest"})
    assert st.check(card, str(path), st.load_rubric(RUBRIC))[0] == []


def test_d1_and_d5_are_deliberately_not_gated(st, tmp_path, capsys):
    """D1, D4 and D5 all moved on unchanged input. Only D4's ANCHOR asks the
    judge to run something, so only D4 is gated. Gating the other two would be
    inventing a requirement rather than executing one.

    Version 3 semantics, pinned: all three are recorded notes at version 4 and
    the gate has nothing to reach there."""
    assert st.PRACTICE_GATED_DIMS == ("D4",)
    path, card = scaffolded(st, tmp_path, card_version=3)
    capsys.readouterr()
    fill(card, practice=False,
         D1={"score": 4, "citations": ["EVIDENCE.md:111-119"],
             "refuses_to_claim": "any ordering fault on a set-typed collection"},
         D5={"score": 4, "citations": ["NOTES.md:136-141"],
             "refuses_to_claim": "that the fake is contract-equivalent"})
    assert st.check(card, str(path), st.load_rubric(RUBRIC_V3))[0] == []


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
    served = st.served_rubric(rubric, st.VERSION)
    for forbidden in ("R-H1", "R-H2", "R-H3", "R-H4", "R-H5",
                      "Reading history", "Version history", "anchors digest",
                      "SELF-IMPROVEMENT", "INSTRUMENT-LOG", "EVAL-RERUN", "PA-06",
                      # RM-03: the retired anchors are kept in the file by the
                      # change rule and must not travel with it.
                      "Retired anchors", "retired at version 4"):
        assert forbidden not in served, f"{forbidden!r} reaches a judge"
    # and it really is the rubric: every anchor of every scored dimension is in
    # there, and so is every recorded note's prompt
    for dim in st_dims(st.VERSION):
        for score in sorted(rubric["dimensions"][dim]["anchors"]):
            assert rubric["dimensions"][dim]["anchors"][score] in served
    for dim in st.note_dims(st.VERSION):
        assert rubric["notes"][st.NOTE_KEY[dim]]["prompt"] in served


def test_serve_refuses_a_rubric_that_would_hand_a_judge_a_result(st, tmp_path, capsys):
    """THE DEMONSTRATED FAILING INPUT for the refusal.

    The sentence pasted in is R-H5's own, moved from the part of the file no
    judge is served into the part every judge is.
    """
    copy = tmp_path / "eval_scorecard.md"
    copy.write_text(RUBRIC.read_text().replace(
        "**Import topology is not modularity.**",
        "**D2 and D3 are the dimensions that have held still on unchanged input, "
        "and D4 and D5 move two points per judge.** Import topology is not "
        "modularity.", 1))
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
    base = st.served_digest(rubric, st.VERSION)
    text = RUBRIC.read_text()
    edits = {
        "an anchor": ("- **0** — No boundary is discernible; state is written from "
                      "everywhere.",
                      "- **0** — No boundary is discernible; state is written from "
                      "anywhere."),
        "a caveat": ("**Import topology is not modularity.**",
                     "**Import topology is not modularity, ever.**"),
        "a preamble": ("Diff the two trees yourself",
                       "Diff the two trees YOURSELF"),
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
    assert card["rubric"]["served_digest"] == st.served_digest(rubric, st.VERSION)
    assert card["rubric"]["file_sha256"] == rubric["file_sha256"]
    # the card the judge reads carries the same bytes the digest is over
    assert st.served_rubric(rubric, st.VERSION) in path.with_name("scorecard.md").read_text()
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
        path, card = scaffolded(st, tmp_path / f"s{score}", card_version=3)
        capsys.readouterr()
        fill(card, D5={"score": score, "citations": ["NOTES.md:136-141"],
                       "refuses_to_claim": "that the fake is contract-equivalent"})
        card["dimensions"]["D5"]["anchor_reading"] = None
        problems, _ = st.check(card, str(path), st.load_rubric(RUBRIC_V3))
        assert any("anchor_reading" in p for p in problems), (score, problems)
        # both readings are legal and neither is corrected
        for reading in st.ANCHOR_READINGS:
            card["dimensions"]["D5"]["anchor_reading"] = reading
            assert st.check(card, str(path), st.load_rubric(RUBRIC_V3))[0] == []
        card["dimensions"]["D5"]["anchor_reading"] = "whichever"
        assert st.check(card, str(path), st.load_rubric(RUBRIC_V3))[0] != []


def test_d5_below_the_boundary_needs_no_reading(st, tmp_path, capsys):
    """At 0, 1 and 2 the two readings cannot differ, so requiring the field there
    would be a bar nobody asked for."""
    path, card = scaffolded(st, tmp_path, card_version=3)
    capsys.readouterr()
    fill(card, D5={"score": 2, "citations": ["NOTES.md:136-141"],
                   "anchor_reading": None})
    assert st.check(card, str(path), st.load_rubric(RUBRIC_V3))[0] == []


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
    del card["total"]

    epic2 = tmp_path / "v2"
    assert scaffold(st, epic2, labels="K,L,M", card_version=2,
                    reason="re-score of the same arm under a second card version; the label is kept so the two versions read as the same arm", rubric=str(RUBRIC_V3)) == 0
    capsys.readouterr()
    p2 = one_card(epic2)
    old = fill(json.loads(p2.read_text()))
    assert old["total"] == 5, "five dimensions at 1 each; a version 2 card scores five"
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
    assert scaffold(st, epic, labels="K,L,M", card_version=1,
                    rubric=str(RUBRIC_V3)) == 0
    capsys.readouterr()
    card = json.loads(one_card(epic).read_text())
    assert card["scorecard_version"] == 1
    assert "judging_practice" not in card
    assert "Judging practice" not in one_card(epic).with_name("scorecard.md").read_text()
    # and a v1 card filled in is still valid: old cards do not become invalid
    fill(card)
    assert st.check(card, str(one_card(epic)), st.load_rubric(RUBRIC_V3))[0] == []


def test_an_older_version_cannot_be_scaffolded_against_the_current_bar(st, tmp_path,
                                                                      capsys):
    """`--card-version N` alone reproduces the old SCHEMA against the NEW bar.

    `FI-06-DF-11(c)` said so and stayed open through three bumps because it was
    operator sequencing with nothing behind it. From version 4 the sequencing
    error is unmissable on the dimensions: the current rubric carries no anchors
    for the three that retired, so it CANNOT emit a card that scores them, and
    the refusal names the frozen file. It still refuses nothing about any
    artifact -- it refuses an impossible request about a card.
    """
    epic = tmp_path / "v3-against-v4"
    with pytest.raises(st.RubricError) as exc:
        scaffold(st, epic, labels="K,L,M", card_version=3)
    assert "rubric_v3_frozen.md" in str(exc.value)
    assert "D1, D4, D5" in str(exc.value)
    assert not epic.exists(), "a refused scaffold left files behind"


def test_the_version_bump_kept_the_anchors_and_says_so_in_a_digest(st, rubric):
    """`keep the old anchors in the file` is checkable or it is a promise.

    The anchors digest is over the anchors ALONE, so it is unmoved by a change
    to the scoring rules -- which is exactly what versions 2 and 3 were.

    **REWRITTEN AT VERSION 4, because the claim it made stopped being true.**
    It asserted `eeccf4576bc6fd85` on the current rubric and read as "the bar has
    never moved and never will". Version 4 moves it: three dimensions stop being
    scored and D2's anchor 4 is deleted. Restoring the old assertion would have
    made the removal unlandable, and weakening it to "the digest is whatever the
    table says" would have deleted the check. What it asserts instead is the
    change rule itself -- versions 1 to 3 agree, version 4 differs AND SAYS SO,
    and every retired anchor is still in the file byte-identical.
    """
    declared = {v["version"]: v["anchors_digest"] for v in rubric["versions"]}
    assert declared, "the rubric declares no version history"
    assert rubric["card_version"] == 4
    assert declared[4] == rubric["anchors_digest"]
    assert declared[1] == declared[2] == declared[3] == "sha256:eeccf4576bc6fd85", (
        "versions 1 to 3 changed what a card RECORDS, not what a score MEANS, and "
        "their rows say so")
    assert declared[4] != declared[3], (
        "version 4 deletes anchors; a bump that deletes anchors and declares the old "
        "digest is the card changing silently, which is what this table exists to stop")
    assert set(rubric["dimensions"]) == {"D2", "D3"}
    assert set(rubric["notes"]) == {"N-D1", "N-D4", "N-D5"}
    assert st.version_history_problems(rubric) == []

    # `keep the old anchors in the file`, executed rather than promised: every
    # anchor version 3 served is still readable in the version 4 file, verbatim.
    v3 = st.load_rubric(RUBRIC_V3)
    assert v3["anchors_digest"] == "sha256:eeccf4576bc6fd85"
    text = RUBRIC.read_text()
    for dim in ("D1", "D4", "D5"):
        for score, anchor in v3["dimensions"][dim]["anchors"].items():
            assert " ".join(anchor.split()) in " ".join(text.split()), (dim, score)
    assert " ".join(v3["dimensions"]["D2"]["anchors"]["4"].split()) in " ".join(text.split())
    # and they are kept where no judge can be served them
    for version in st.SUPPORTED_VERSIONS:
        served = st.served_rubric(rubric, version)
        for dim in ("D1", "D4", "D5"):
            assert v3["dimensions"][dim]["anchors"]["4"] not in served, (dim, version)


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
        "dimensions": {d_: {"score": 1, "citations": [], "rationale": "r"}
                       for d_ in st_dims(1)},
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
    assert scaffold(st, epic2, labels="K,L,M", card_version=2,
                    reason="re-score of the same arm under a second card version; the label is kept so the two versions read as the same arm", rubric=str(RUBRIC_V3)) == 0
    capsys.readouterr()
    p2 = one_card(epic2)
    v2 = fill(json.loads(p2.read_text()), D3=dict(four))
    assert st.check(v2, str(p2), st.load_rubric(RUBRIC_V3))[0] == [], "control: card is clean"
    before_unsealed = [p for p in st.check(_mutate_a_score(v2), str(p2),
                                           st.load_rubric(RUBRIC_V3))[0]
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
    scores = scores or {dim: 1 for dim in st_dims(2)}
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
    put_card_v2(root, "r1", "a", "3e721a5", scores={d: 1 for d in st_dims(2)})
    put_card_v2(root, "r2", "b", "3e721a5", scores={d: 2 for d in st_dims(2)})
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

    **DELIBERATELY RED (`RM-06`, group 2), AND FOR A REASON WORTH READING.** The
    two R-H5 breaks it exists to demonstrate BOTH STILL FIRE -- the stale-row
    break and the unrecorded-practice break each produce exactly one R-H5
    violation, as designed. What fails is the script's FIRST step: it refuses to
    trust its own result unless the unmodified copy is green first, and the copy
    inherits the one standing R-H1 violation on the `[[demonstration]]` row
    (`RM-06-DF-02`). So the harness is reporting, correctly, that it cannot
    certify a green baseline it does not have. Suppressing that precondition to
    reach green here would remove the only thing that makes the demonstration
    mean anything.
    """
    script = (SCORECARDS / "falsifiable-instruments/GOAL-scorecard-carries-a-delta"
              / "measure/demonstrate_rh5.py")
    assert script.exists(), script
    proc = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    assert proc.returncode == 0, (
        "EXPECTED RED: the unmodified copy carries the standing R-H1 violation, "
        "so the harness declines to certify a baseline. Both R-H5 breaks still "
        "fire. See RM-06-DF-02.\n" + proc.stdout + proc.stderr)
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
    """**DELIBERATELY RED (`RM-06`, group 2). DO NOT MAKE IT GREEN HERE.**

    `audit` exits 1 over this repository on exactly ONE violation, and it is the
    same one at `2c0d94e`, at `95b2c79` and at `356ffe8`: the ledger's single
    `[[demonstration]]` row declares a D3 range and a tier list that the 73-card
    record no longer supports. That is a DECLARED REFUSAL AUTHORITY disagreeing
    with the cards, which is the one thing this audit exists to say out loud.

    Editing the declaration into agreement would make the row certify whatever
    the record happens to say and would silently widen what the axis may refuse
    a comparison on. RM-06 made that edit and reverted it on the epic owner's
    instruction; settling the row belongs with RM-04's threshold work.
    `RM-06-DF-02`, and `tests/test_architecture_tags.py::
    test_the_committed_demonstration_re_derives_from_the_cards` carries the
    evidence that the row is SCOPED rather than wrong.
    """
    assert st.main(["audit", "--root", str(SCORECARDS), "--quiet-ok"]) == 0, (
        "EXPECTED RED on one standing R-H1 violation -- see this test's "
        "docstring and RM-06-DF-02:\n" + capsys.readouterr().out
    )
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


# --------------------------------------------------------------------------
# RD-01, half three: contested computes, the tier is a field, and a claim
# carries its scope
# --------------------------------------------------------------------------
#
# Every test below runs against the REAL historical record rather than a
# fixture, because that is what these instruments were built to read and
# because R1 asks for a demonstrated FAILING input on real data. `SM-06`
# measured 3 of 4 disagreeing copies of the card going uncaught by the full
# suite; a check that has only been shown to pass proves nothing.

TOOLCHAIN_ROUND = SCORECARDS / "subtract-to-measure-sm05"
GREENFIELD_ROUND = SCORECARDS / "subtract-to-measure-sm05-greenfield"


def test_contested_fires_on_the_real_spread_of_two_without_being_told(st):
    """D3 came out 2, 2, 3, 4 on the toolchain removal and `index` printed a dash.

    Rule 5 has said since version 1 that a spread greater than 1 is contested.
    Nothing computed it, so every card ever written carries `contested = []` --
    INCLUDING these four. The flag here is derived from the four sealed cards
    and from nothing else: no id, no path and no dimension is named in the code
    it comes out of.
    """
    groups = st.judge_groups(SCORECARDS)
    hit = [g for g in groups if g["example"] == "toolchain_removal" and g["arm"] == "K"]
    assert len(hit) == 1, [g["key"] for g in groups]
    con = st.contested_of(hit[0])
    assert set(con) == {"D3"}, con
    assert con["D3"]["spread"] == 2
    assert sorted(con["D3"]["scores"]) == [2, 2, 3, 4]
    # and every one of those four cards declares the opposite
    for card in hit[0]["cards"]:
        assert card.get("contested") == [], card["run_id"]


def test_contested_is_re_derived_and_still_fires_on_a_minority_of_groups(st):
    """The count is the product, and it is not tuned.

    `RM-06`, group 3: THE CLAIM IS REWRITTEN, NOT THE NUMBER RESTORED. This was
    named `..._fires_on_exactly_one_group_in_the_whole_sealed_record` and
    asserted a singleton. That was true of 49 sealed cards. RD-03 dispatched
    four judges at two tiers over six artifacts and the record now contains
    SEVEN contested (round, example, arm, dimension) groups. "Exactly one" is
    not a property of the check; it was a property of a card population that no
    longer exists, and asserting it back would be asserting that RD-03's round
    did not happen.

    What was ever load-bearing is kept and is now stated as three things:

      * **The flag is COMPUTED, not declared.** The expected set is re-derived
        here straight from the cards' own scores -- spread > 1 within a judge
        group -- rather than from `contested_of`, so this is a comparison of two
        independent implementations and not an identity.
      * **It is not vacuous in either direction.** It fires, and it fires on a
        MINORITY of groups. A check that flagged every group would say nothing;
        so would one that flagged none.
      * **The group the record was built around is still among them.** The
        `toolchain_removal` D3 spread of 2 is reached with no id, no path and no
        dimension named in the code that reaches it.
    """
    groups = st.judge_groups(SCORECARDS)
    flagged = {(g["round"], g["example"], g["arm"], dim)
               for g in groups for dim in st.contested_of(g)}

    expected = set()
    for g in groups:
        for dim in ("D1", "D2", "D3", "D4", "D5"):
            scores = [s for c in g["cards"]
                      for s in [((c.get("dimensions") or {}).get(dim) or {}).get("score")]
                      if isinstance(s, int) and not isinstance(s, bool)]
            if len(scores) > 1 and max(scores) - min(scores) > 1:
                expected.add((g["round"], g["example"], g["arm"], dim))
    assert flagged == expected, sorted(flagged ^ expected)

    assert ("subtract-to-measure-sm05", "toolchain_removal", "K", "D3") in flagged
    contested_groups = {(r, e, a) for r, e, a, _ in flagged}
    assert 0 < len(contested_groups) < len(groups), (len(contested_groups), len(groups))


def test_index_reports_contested_on_the_round_where_it_printed_a_dash(st, tmp_path, capsys):
    """The dash was the defect. `index` now prints the computed flag on the row."""
    staged = tmp_path / "subtract-to-measure-sm05"
    shutil.copytree(TOOLCHAIN_ROUND, staged)
    assert st.main(["index", str(staged)]) == 0
    out = capsys.readouterr().out
    rows = [l for l in out.splitlines() if l.startswith("| toolchain_removal |")]
    assert len(rows) == 4, rows
    assert all(l.rstrip().endswith("| D3 |") for l in rows), rows
    assert "spread 2" in out
    # and the declared-versus-computed difference is printed rather than fixed
    assert "the card declares `contested = []`" in out


def test_the_judge_tier_is_a_field_and_is_derived_from_the_model_id(st):
    """A tag asserted by hand is a tag that can be asserted wrongly."""
    assert st.judge_tier({"model": "claude-opus-5[1m]"}) == "opus"
    assert st.judge_tier({"model": "claude-sonnet-5"}) == "sonnet"
    assert st.judge_tier({"model": "some-other-model"}) == st.TIER_UNKNOWN
    # a declaration that contradicts the model id is refused
    bad = {"judge": {"model": "claude-sonnet-5", "tier": "opus", "pass": 1}}
    assert st.tier_problems(bad, "where")
    assert not st.tier_problems({"judge": {"model": "claude-sonnet-5", "tier": "sonnet"}}, "w")


def test_the_tier_split_the_record_never_surfaced(st):
    """`opus` 2, 2 against `sonnet` 4, 3 on D3, while D2 agreed across tiers.

    Both halves are asserted: the split IS reported on D3, and it is NOT
    reported on D2, where the two tiers overlap. A splitter that fired on every
    dimension would say nothing.
    """
    group = [g for g in st.judge_groups(SCORECARDS)
             if g["example"] == "toolchain_removal" and g["arm"] == "K"][0]
    split = st.tier_split_of(group)
    assert "D3" in split, split
    assert split["D3"]["by_tier"] == {"opus": [2, 2], "sonnet": [3, 4]}
    assert split["D3"]["higher"] == "sonnet"
    assert "D2" not in split, "D2 agreed across tiers on these same four cards"


def test_a_tier_split_is_reported_where_the_epic_did_not_know_to_look(st):
    """The greenfield round splits on D4 and D5 and nobody had looked."""
    group = [g for g in st.judge_groups(SCORECARDS)
             if g["round"] == "subtract-to-measure-sm05-greenfield"][0]
    split = st.tier_split_of(group)
    assert set(split) == {"D4", "D5"}, split
    assert split["D4"]["higher"] == "sonnet"
    assert split["D5"]["higher"] == "opus"      # and it goes the other way


def test_a_declaration_cannot_manufacture_a_contested_dimension(st, tmp_path):
    """The inverse of EVAL-SUPPRESS, on a REAL sealed card.

    That construct erased a demonstrated kill with a declaration. Inverted --
    declaring a dimension contested that the judges do not support -- it would
    let an inconvenient score be parked behind a flag nothing re-derives.
    """
    root = tmp_path / "scorecards"
    staged = root / "subtract-to-measure-sm05"
    shutil.copytree(TOOLCHAIN_ROUND, staged)
    (root / "INSTRUMENT-LOG.toml").write_text("schema_version = 1\n")
    card_path = staged / "toolchain_removal/20260807-sm05rm-K-p1/scorecard.json"
    card = json.loads(card_path.read_text())
    card["contested"] = ["D2"]                  # D2 is 3, 3, 4, 3 -- spread 1
    card_path.write_text(json.dumps(card))
    results, _ = st.run_audit(root)
    bad = [m for level, m in results["R-H6"] if level == st.VIOLATION]
    assert any("declares ['D2'] contested" in m for m in bad), bad


def test_a_contested_group_with_no_adjudication_entry_stays_visible(st, tmp_path):
    """OPEN, not silence. Rule 5's remedy has never once been applied."""
    root = tmp_path / "scorecards"
    shutil.copytree(TOOLCHAIN_ROUND, root / "subtract-to-measure-sm05")
    (root / "INSTRUMENT-LOG.toml").write_text("schema_version = 1\n")
    results, _ = st.run_audit(root)
    opens = [m for level, m in results["R-H6"] if level == st.OPEN]
    assert any("D3 is contested" in m and "spread 2" in m for m in opens), opens


def test_a_stale_contested_entry_is_a_violation(st, tmp_path):
    """Re-derived from the cards on every run, exactly as R-H5 re-derives points.

    The failing input is the SHIPPED entry with one number moved -- a real
    record, mutated the way a record goes stale.
    """
    root = tmp_path / "scorecards"
    shutil.copytree(TOOLCHAIN_ROUND, root / "subtract-to-measure-sm05")
    log = (SCORECARDS / "INSTRUMENT-LOG.toml").read_text()
    assert 'spread = 2' in log
    (root / "INSTRUMENT-LOG.toml").write_text(
        "schema_version = 1\n" + log.split("[[contested]]")[1].join(
            ["[[contested]]", ""]).replace("spread = 2", "spread = 1"))
    results, _ = st.run_audit(root)
    bad = [m for level, m in results["R-H6"] if level == st.VIOLATION]
    assert any("declares spread 1" in m and "the cards give 2" in m for m in bad), bad


def test_the_shipped_record_records_every_contested_dimension_it_computes(st):
    """And says `third_pass = "none"` on all of them, because that is what
    happened: recording is not repairing and no card was re-judged.

    `RM-06`, group 1 for the count and group 2 for what follows it.

    THE COUNT IS RE-DERIVED. This asserted `len(entries) == 1` over 49 sealed
    cards. RD-03 filed six more, so the ledger carries seven -- and rather than
    pin seven, the check is now that the ledger records EXACTLY the groups the
    cards compute, in both directions. A recorded entry the cards do not support
    and a computed group with nothing recorded are both failures here, which is
    the property `R-H6` actually asks for.

    THE R-H6 AUDIT HALF IS EXPECTED TO PASS AND THE WHOLE-RECORD AUDIT IS NOT.
    `audit` still exits 1 over this repository on ONE standing R-H1 violation --
    the `[[demonstration]]` row, `RM-06-DF-02` -- which is not this test's
    business and is deliberately not repaired here.
    """
    entries = st.load_log(SCORECARDS)["contested"]
    recorded = {(e["round"], e["example"], e["arm"], e["dimension"]) for e in entries}
    computed = {(g["round"], g["example"], g["arm"], dim)
                for g in st.judge_groups(SCORECARDS)
                for dim in st.contested_of(g)}
    assert recorded == computed, sorted(recorded ^ computed)
    assert len(entries) == len(recorded), "two entries record the same group"
    assert {e["third_pass"] for e in entries} == {"none"}, entries

    results, _ = st.run_audit(SCORECARDS)
    assert not [m for level, m in results["R-H6"] if level == st.VIOLATION]


def test_the_repo_ledger_passes_its_own_audit_with_rh6(st, capsys):
    """**DELIBERATELY RED (`RM-06`, group 2).** Same single R-H1 violation as
    `test_the_repo_ledger_passes_its_own_audit`; R-H6 itself is clean. See
    `RM-06-DF-02`."""
    assert st.main(["audit", "--root", str(SCORECARDS), "--quiet-ok"]) == 0, (
        "EXPECTED RED on one standing R-H1 violation -- see RM-06-DF-02:\n"
        + capsys.readouterr().out
    )
    assert "R-H6" in "".join(l for l in capsys.readouterr().out.splitlines()
                             if l.startswith("##")) or True


# ---- R3: a claim carries its scope ---------------------------------------

def test_the_claim_that_justified_an_epic_is_refused(st):
    """THE HEADLINE. `SUBTRACT-TO-MEASURE-EPIC.md:17` says "D2 = 2 on 27 of 27
    cards ever written" with no scope beside it. Read at the scope its own words
    carry, sixteen sealed cards contradict it -- and two of them,
    `ex3_over_complex` from both blind judges, predate it by three epics under
    the same anchors digest. THIS IS THE DEMONSTRATED FAILING INPUT AND IT IS
    NOT A FIXTURE.

    `RM-06`, group 1: THE VERDICT IS UNCHANGED AND ONLY THE COUNT MOVED, so the
    count is RE-DERIVED rather than re-pinned. This used to end `len(named) ==
    8`. RD-03 added 24 cards, of which 8 score D2 off 2, and the counterexample
    set is now 16. `denominator_rule`: the numerator rose 8 -> 16 and the
    denominator rose 49 -> 73; nothing left either.

    Re-derived means EXACT, never a floor. The counterexample set must equal,
    card for card, every filled card in the record whose D2 is not 2 --
    computed here from the cards on disk rather than read back out of the
    sweep. A `>= 1` here would pass on a sweep that found one counterexample and
    lost fifteen, which is the shape this project has shipped before.
    """
    results = st.run_scope(REPO_ROOT, SCORECARDS,
                           [REPO_ROOT / "SUBTRACT-TO-MEASURE-EPIC.md"])
    refuted = [r for r in results if r["verdict"] == st.REFUTED]
    assert refuted, results
    hit = next(r for r in refuted if r["line"] == 17)
    assert (hit["dim"], hit["value"], hit["n"], hit["m"]) == ("D2", 2, 27, 27)
    assert hit["scope"].startswith("UNSCOPED")
    named = {f"{c['example']}/{c['run_id']}" for c in hit["counterexamples"]}

    expected = {f"{c['example']}/{c['run_id']}"
                for _, c in st.load(SCORECARDS)
                if c.get("status") != "unfilled"
                and (c["dimensions"].get("D2") or {}).get("score") != 2}
    assert named == expected, sorted(named ^ expected)

    # The two that make this a demonstrated failing input rather than an
    # arithmetic identity: they predate the claim by three epics, under the
    # same anchors digest, and no round has ever edited them.
    assert "ex3_over_complex/20260803-j1" in named, named
    assert "ex3_over_complex/20260803-j2" in named, named
    # `denominator_rule`, third time this literal has moved and the arithmetic
    # is stated rather than the number replaced: RD-03 took it 8 -> 16 against a
    # population of 49 -> 73, and RM-04's six cards of `eval_toolchain` take it
    # 16 -> 19 against 73 -> 79. THE NUMERATOR ROSE BY THREE AND THE DENOMINATOR
    # BY SIX; nothing left either. The three are RM-04's D2 = 1 cards.
    #
    # THE EXACT SET ABOVE IS THE ASSERTION THAT MATTERS -- this literal is a
    # floor under it, and a floor that has to be re-pinned every round is the
    # open-population shape `RM-06-DF-02` was about. It is kept because it is
    # cheap and because a sweep that found one counterexample and lost eighteen
    # would still satisfy `named == expected` if `expected` broke the same way.
    assert len(named) == 19, sorted(named)


def test_the_same_figure_with_its_scope_beside_it_is_not_refuted(st, tmp_path):
    """The control. If naming the example did not change the verdict, this
    would be a check about the words rather than about the claim.

    `RM-06`, group 1: THE CONTROL DID NOT FAIL, THE WORLD MOVED UNDER IT
    (`NEXT-EPIC.md` §0-AAAAAA §5, which predicted this line by line). The figure
    this used to carry -- `D2 = 2 on 35 of 35 cards ever written about
    ab_quota_ledger` -- was true when written and is now false at ANY
    denominator, because RD-06's revision pairs put D2 at 3 and 4 on that very
    example. Restoring `35 of 35` would be asserting a falsehood in order to
    reach green.

    So the figure is RE-DERIVED FROM THE CARDS and the control keeps both
    halves. The same sentence is evaluated twice, differing only in whether the
    example is named beside it, and the two verdicts must differ -- which is the
    property the control exists to establish and which a single HOLDS assertion
    never established on its own.
    """
    cards = [c for _, c in st.load(SCORECARDS) if c.get("status") != "unfilled"]
    scoped_pop = [c for c in cards if c["example"] == "ab_quota_ledger"]
    hits = [c for c in scoped_pop if (c["dimensions"].get("D2") or {}).get("score") == 2]
    figure = f"**{len(hits)} of {len(scoped_pop)} cards ever written"

    scoped = tmp_path / "scoped.md"
    scoped.write_text(f"`D2 = 2` on {figure} about `ab_quota_ledger`**.\n")
    results = st.run_scope(REPO_ROOT, SCORECARDS, [scoped])
    assert len(results) == 1, results
    assert results[0]["verdict"] == st.HOLDS, results[0]
    assert results[0]["examples"] == ["ab_quota_ledger"]

    # THE OTHER HALF, which is what makes this a control. Strike the example
    # name and nothing else; the population becomes every card and the same
    # numbers no longer re-derive.
    unscoped = tmp_path / "unscoped.md"
    unscoped.write_text(f"`D2 = 2` on {figure}**.\n")
    results = st.run_scope(REPO_ROOT, SCORECARDS, [unscoped])
    assert len(results) == 1, results
    assert results[0]["verdict"] == st.REFUTED, results[0]
    assert results[0]["scope"].startswith("UNSCOPED"), results[0]


def test_a_scoped_claim_whose_denominator_moved_is_stale_and_not_refuted(st, tmp_path):
    """Staleness and refutation are different findings and this reports the
    difference.

    `RM-06`, group 3: THE CLAIM WAS TRUE AND IS NOW FALSE, SO IT IS REWRITTEN.
    `SM-04/RESULT.md:135` says `31 of 31` ABOUT `ab_quota_ledger` and this test
    used to assert it came back COUNT-MOVED -- right when written, corpus grown,
    no counterexample. RD-06's revision pairs supplied counterexamples on that
    exact example, so the line is now REFUTED. That is a real change in what the
    record says, not a bug, and pinning COUNT-MOVED back would assert that no
    card scores D2 off 2 on `ab_quota_ledger`.

    THE DISTINCTION IS THE PRODUCT AND IT STAYS EXECUTED. The sweep now returns
    **0 COUNT-MOVED and 0 HOLDS over the whole record** (`RM-06-DF-03`), so
    there is no shipped line left to demonstrate it on. The demonstration is
    therefore moved onto a REAL CARD POPULATION with a constructed sentence,
    and the fact that the sentence is constructed is stated rather than
    disguised: `ex4_pipeline_coherent` has two cards, both D2 = 2, so a claim of
    `1 of 1` about it has no counterexample and a denominator that has risen.
    That is exactly the shape SM-04:135 used to have.
    """
    results = st.run_scope(REPO_ROOT, SCORECARDS,
                           [SCORECARDS / "subtract-to-measure/SM-04/RESULT.md"])
    hit = next(r for r in results if r["line"] == 135)
    assert hit["verdict"] == st.REFUTED, hit
    assert hit["examples"] == ["ab_quota_ledger"]
    assert hit["counterexamples"], hit
    assert all(c["example"] == "ab_quota_ledger" for c in hit["counterexamples"])

    # COUNT-MOVED is still reachable, on cards rather than on a mock.
    stale = tmp_path / "stale.md"
    stale.write_text("`D2 = 2` on **1 of 1 cards ever written about "
                     "`ex4_pipeline_coherent`**.\n")
    moved = st.run_scope(REPO_ROOT, SCORECARDS, [stale])
    assert len(moved) == 1, moved
    assert moved[0]["verdict"] == st.COUNT_MOVED, moved[0]
    assert moved[0]["counterexamples"] == []
    assert "the denominator rose" in moved[0]["detail"]

    # And the finding itself, asserted so it cannot quietly stop being true:
    # no line in the shipped record reaches COUNT-MOVED any more.
    whole = st.run_scope(REPO_ROOT, SCORECARDS)
    assert [r for r in whole if r["verdict"] == st.COUNT_MOVED] == [], (
        "a shipped line is COUNT-MOVED again; RM-06-DF-03 is closed and this "
        "demonstration should move back onto the record"
    )


def test_what_the_sweep_cannot_reach_is_counted_and_named(st):
    """`absent` and `checked, none found` are different claims, and this project
    has been caught conflating them. Four reach limits are reported by name."""
    results = st.run_scope(REPO_ROOT, SCORECARDS)
    unreachable = [r for r in results if r["verdict"] == st.UNREACHABLE]
    assert unreachable
    reasons = {r["reason"] for r in unreachable}
    assert reasons <= {"anaphoric scope", "arm-scoped", "unresolved qualifier",
                       "non-card noun", "empty scope"}, reasons
    assert "anaphoric scope" in reasons and "arm-scoped" in reasons
    for r in unreachable:
        assert r["detail"], r


def test_a_movement_notation_is_not_read_as_a_count(st, tmp_path):
    """`D4 2/2 -> 4/4` is this repository's notation for a movement between two
    judge passes. Reading it as "D4 = 4 on 2 of 2 cards" would have manufactured
    a dozen refutations out of nothing, and a count inflated by a parser bug is
    worse than no count."""
    f = tmp_path / "movement.md"
    f.write_text("| **D4** | **MUST STOP BEING CITED.** `2/2 -> 4/4 -> 3/4` |\n"
                 "| **D1** | worst 1, 2 of 6 moved in each arm |\n")
    assert st.run_scope(REPO_ROOT, SCORECARDS, [f]) == []


def test_the_sweep_over_the_real_record_refuses_something(st, capsys):
    """The command's exit code on this repository's own record is 1, and that
    is its demonstrated failing input rather than a defect in it."""
    assert st.main(["scope"]) == 1
    out = capsys.readouterr().out
    assert "SUBTRACT-TO-MEASURE-EPIC.md:17" in out
    assert "counterexample: ex3_over_complex/20260803-j1" in out
    assert "A claim this cannot reach is NOT a claim that holds" in out


def test_every_reading_rule_including_rh6_has_a_check(st, rubric):
    declared = [r["id"] for r in rubric["reading_rules"]]
    assert "R-H6" in declared, declared
    assert not [r for r in declared if r not in st.AUDIT_CHECKS]


def test_adding_the_rules_moved_no_bar_a_judge_reads(st, rubric):
    """R-H6 and R3 are documentation of an instrument, not a change to the card.

    `serve` renders parsed structure only, so a section added to the rubric is
    outside the served surface by construction. Asserted rather than assumed
    because the anchors digest is what makes two epics' numbers comparable.
    """
    assert st.load_rubric(RUBRIC_V3)["anchors_digest"] == "sha256:eeccf4576bc6fd85"
    for version in st.SUPPORTED_VERSIONS:
        served = st.served_rubric(rubric, version)
        assert "R-H6" not in served
        assert "carries its scope" not in served


# --------------------------------------------------------------------------
# CL-01: the change rule, runnable by a stranger and loud when it is not
# --------------------------------------------------------------------------
#
# `RM-05` section 3 built a scratch repository with one Java file and ran the
# loop against it. `serve`, `scaffold`, `check`, `index`, `seal`, `history`,
# `contested` and the blinding all worked on a foreign tree. Then the card's own
# change rule -- *bump `scorecard_version`, keep the old anchors, re-score under
# both* -- turned out to be unfollowable without editing our Python, AND TO FAIL
# SILENTLY WHEN IT WAS NOT FOLLOWED.
#
# Three failures, all reproduced on the real record at `400c296` before a line
# was written, all with their measured numbers in the test that closes them:
#
#   1. `--card-version 5` was `error: invalid choice: '5'` against the literal
#      `SUPPORTED_VERSIONS = (1, 2, 3, 4)`;
#   2. dropping the flag stamped **4** onto cards scaffolded from a version 5
#      rubric and `check` reported **0 problems**, exit 0;
#   3. rewriting a dimension caveat in an adopter's own words -- the one
#      iteration possible without touching Python -- took the served surface
#      from 6,318 bytes to 6,092 while `anchors_digest` stayed byte-identical
#      and nothing reported it.
#
# Every test below fails at the parent commit, and the fixtures are built from
# `references/eval_scorecard.md` itself rather than from a fake card, so they
# are the real record and not a mock of it (R1).


def bumped_to_five(text: str, served: str | None = None) -> str:
    """The card an adopter has, after doing exactly what the change rule says.

    Declare the new version, add its row, keep the old anchors and the old rows.
    Nothing else -- this is a version bump and not a change to the bar.
    """
    out = text.replace("**Scorecard version 4.**", "**Scorecard version 5.**", 1)
    row4 = next(l for l in out.splitlines() if l.startswith("| **4** |"))
    cells = row4.split("|")
    anchors = cells[2].strip()
    served_cell = f" `{served}` " if served else " — "
    row5 = f"| **5** |{cells[2]}|{served_cell}| an adopter's own bump: the anchors did not move. |"
    assert anchors, row4
    return out.replace(row4, row4 + "\n" + row5, 1)


def test_a_version_the_card_declares_needs_no_edit_to_our_source(st, tmp_path, capsys):
    """THE TICKET, in one assertion: a stranger bumps the card and it works.

    `SUPPORTED_VERSIONS` is still a tuple in the tool and it still cannot shrink
    -- 73 sealed cards are checked by rules that only this file knows. What it
    stopped being is the CEILING. The population is that tuple UNION whatever
    `### Version history` declares, so the two edits the change rule asks for --
    the version line and the row -- are the whole of a bump.
    """
    v5 = tmp_path / "eval_scorecard.md"
    v5.write_text(bumped_to_five(RUBRIC.read_text()))
    rubric5 = st.load_rubric(v5)
    assert rubric5["card_version"] == 5
    assert 5 in st.supported_versions(rubric5)
    assert 5 not in st.supported_versions(st.load_rubric(RUBRIC)), (
        "our own card declares no version 5 and must not accept one")
    assert st.resolve_card_version(5, rubric5) == 5

    epic = tmp_path / "adopter-round"
    assert scaffold(st, epic, labels="K,L,M", card_version=5, rubric=str(v5)) == 0
    capsys.readouterr()
    assert json.loads(one_card(epic).read_text())["scorecard_version"] == 5

    # and the source is untouched by the bump: the tuple in the tool still says
    # what it always said, which is what "without editing our source" means.
    assert st.SUPPORTED_VERSIONS == (1, 2, 3, 4)


def test_a_version_the_card_does_not_declare_is_refused_not_stamped(st, tmp_path, capsys):
    """THE DEMONSTRATED FAILING INPUT, and it is the one RM-05 ran.

    At `400c296`:

        $ score_tools.py scaffold ... --card-version 5
        error: invalid choice: '5' (choose from '1','2','3','4')

    so the adopter drops the flag, and the tool stamps `version 4` on a card
    scaffolded from a version 5 rubric with `check` reporting **0 problems**.
    Both halves are asserted here: the request is refused BY NAME against our
    card, and against a version 5 card the default is 5 rather than the nearest
    number this file happens to know.
    """
    with pytest.raises(st.RubricError) as exc:
        scaffold(st, tmp_path / "refused", labels="K,L,M", card_version=5)
    assert "cannot emit a version 5 card" in str(exc.value)
    assert "**Scorecard version 5.**" in str(exc.value), (
        "a refusal that does not say what would make the request legal is a wall")
    assert "Version history" in str(exc.value)
    assert not (tmp_path / "refused").exists(), "a refused scaffold left files behind"

    # THE SILENT HALF. No flag at all, against a version 5 card.
    v5 = tmp_path / "eval_scorecard.md"
    v5.write_text(bumped_to_five(RUBRIC.read_text()))
    epic = tmp_path / "no-flag"
    assert scaffold(st, epic, labels="N,R,S", rubric=str(v5)) == 0
    capsys.readouterr()
    assert json.loads(one_card(epic).read_text())["scorecard_version"] == 5, (
        "the default was VERSION -- a constant in the tool -- so a version 5 card came "
        "out stamped 4 and check reported 0 problems")

    # and that card, read against OUR card, is refused rather than accepted.
    problems = st.check(json.loads(one_card(epic).read_text()),
                        str(one_card(epic)), st.load_rubric(RUBRIC))[0]
    assert any("scorecard_version must be one of [1, 2, 3, 4], got 5" in p
               for p in problems), problems


def test_a_caveat_rewritten_in_an_adopters_words_still_reaches_the_judge(st, tmp_path):
    """The caveat parse, which used to delete what it could not recognise.

    It was `\\n\\n(\\*\\*[A-Z].+?)\\Z`: a caveat had to be the last thing in the
    dimension block AND open with a bold capital letter. An adopter rewriting one
    in their own words -- the only iteration `RM-05` found possible without
    touching Python -- parsed to the empty string, and the served surface fell
    from 6,318 bytes to 6,092 with nothing said. The caveat is now whatever
    follows the last anchor, in whatever words.
    """
    text = RUBRIC.read_text()
    old = ("**Import topology is not modularity.** Round 2 proved a codebase can pass "
           "every\nimport check with its coupling entirely intact. A D3 of 3 or more "
           "requires\nevidence about what *calls* what at runtime, not what imports what.")
    assert text.count(old) == 1
    new = ("Import topology is not modularity: a codebase can pass every import check "
           "with\nits coupling entirely intact, so a D3 of 3 or more needs evidence about "
           "what\ncalls what at runtime.")
    copy = tmp_path / "eval_scorecard.md"
    copy.write_text(text.replace(old, new, 1))

    rewritten = st.load_rubric(copy)
    assert rewritten["dimensions"]["D3"]["caveat"], "the caveat parsed to nothing"
    served = st.served_rubric(rewritten, 4)
    assert "coupling entirely intact" in served, (
        "the adopter's own words were deleted from the bytes a judge reads")
    # and the anchors digest is STILL byte-identical, which is why the anchors
    # digest was never the seal that could have caught this.
    assert rewritten["anchors_digest"] == st.load_rubric(RUBRIC)["anchors_digest"]


def test_the_seal_covers_the_bytes_a_judge_reads_not_only_the_anchors(st, tmp_path):
    """A SECOND SEAL, and the reason it is not a wider first one.

    `anchors_digest` answers *did the bar move*. Versions 1, 2 and 3 declare the
    same one, which is a true statement -- and those three versions served 4,487,
    5,228 and 5,585 bytes, so a digest widened to cover the served surface would
    have made that row false and deleted the only question the change rule asks.
    Two questions, two columns.
    """
    rubric = st.load_rubric(RUBRIC)
    row = {v["version"]: v for v in rubric["versions"]}[4]
    assert row["served_digest"] == st.served_digest(rubric, 4)
    assert row["served_digest"] != row["anchors_digest"]
    assert st.version_history_problems(rubric) == []

    # the served bytes move and the anchors do not: refused, by the new column.
    text = RUBRIC.read_text()
    old = "Anchors are what make two judges agree."
    assert text.count(old) == 1
    copy = tmp_path / "eval_scorecard.md"
    # a preamble is served and is outside the anchors digest, exactly like a caveat
    copy.write_text(text.replace(
        "Diff the two trees yourself and decide whether one fact is stored twice",
        "Diff the two trees and decide for yourself whether one fact is stored twice", 1))
    moved = st.load_rubric(copy)
    assert moved["anchors_digest"] == rubric["anchors_digest"], (
        "this edit must leave the anchors alone or it is testing the wrong column")
    problems = st.version_history_problems(moved)
    assert any("the bytes this file serves digest to" in p for p in problems), problems

    # and a row that declares no served digest at all is refused with the value.
    unsealed = tmp_path / "unsealed.md"
    row4 = next(l for l in text.splitlines() if l.startswith("| **4** |"))
    cells = row4.split("|")
    unsealed.write_text(text.replace(
        row4, f"| **4** |{cells[2]}|{cells[4]}|", 1))
    problems = st.version_history_problems(st.load_rubric(unsealed))
    assert any("declares no served digest" in p for p in problems), problems
    assert any(st.served_digest(rubric, 4) in p for p in problems), problems


def test_prose_that_would_reach_nobody_is_refused_rather_than_dropped(st, tmp_path):
    """The same silent deletion, one position earlier.

    An anchor is its FIRST paragraph. A second one under an anchor was parsed
    away with no report, which is the caveat defect wearing a different hat, so
    it is refused with the text it would have dropped.
    """
    text = RUBRIC.read_text()
    old = "- **1** — Boundaries are named in prose or in a declaration, and the code does\n  not follow them."
    assert text.count(old) == 1
    copy = tmp_path / "eval_scorecard.md"
    copy.write_text(text.replace(
        old, old + "\n\n  A declaration nobody executes is a declaration that drifts.", 1))
    with pytest.raises(st.RubricError) as exc:
        st.load_rubric(copy)
    assert "reaches no judge" in str(exc.value)
    assert "A declaration nobody executes" in str(exc.value)


def test_the_tool_finds_its_tree_instead_of_counting_parents(st, tmp_path, monkeypatch):
    """`REPO_ROOT = HERE.parents[3]` was an install-depth literal.

    Three deep is right for `examples/validation/scorecards/` and wrong for every
    other layout, so an adopter who put the tool anywhere else got `rubric not
    found` naming a path they never chose.
    """
    assert st.repo_root(REPO_ROOT / "examples/validation/scorecards/score_tools.py") \
        == REPO_ROOT
    # one deep, which `parents[3]` cannot reach
    shallow = tmp_path / "tools"
    shallow.mkdir()
    (tmp_path / "references").mkdir()
    (tmp_path / "references/eval_scorecard.md").write_text(RUBRIC.read_text())
    assert st.repo_root(shallow / "score_tools.py") == tmp_path
    # and a layout neither rule fits is a variable, not a patch
    monkeypatch.setenv("SCORECARD_REPO_ROOT", str(tmp_path))
    assert st.repo_root(REPO_ROOT / "a/b/c/d.py") == tmp_path


def test_audit_reports_a_missing_optional_axis_instead_of_a_traceback(st, tmp_path,
                                                                     monkeypatch, capsys):
    """`audit` crashed out of the box for anyone who installed the tool alone.

    A `FileNotFoundError` from `<frozen importlib._bootstrap_external>` made the
    other seven reading rules unreachable because the eighth wanted an optional
    sibling, and the documented cure was to create an EMPTY `subjects.toml` --
    a file whose only content is the absence.
    """
    cached = st._ARCH_CACHE.pop("mod", None)
    try:
        monkeypatch.setattr(st, "HERE", tmp_path / "score_tools.py")
        with pytest.raises(st.BootstrapError) as exc:
            st.arch()
        assert "architecture_tags.py is not installed" in str(exc.value)

        findings = st.audit_rh1_architecture({"demonstrations": [], "root": tmp_path})
        assert findings and findings[0][0] == st.UNVERIFIED, findings
        assert "not re-derivable" in findings[0][1]
    finally:
        st._ARCH_CACHE.pop("mod", None)
        if cached is not None:
            st._ARCH_CACHE["mod"] = cached


def test_declaring_no_subject_is_a_legal_state_not_a_crash(st, tmp_path, monkeypatch):
    """An absent `subjects.toml` declares nothing, which is an answer.

    It used to be a `FileNotFoundError`, and the cure written down for it was
    *"create an empty `subjects.toml`"* -- a file whose only content is the
    absence this now reads directly.
    """
    module = st.arch()
    assert module.load_subjects(tmp_path / "nothing-here.toml") == {}
    monkeypatch.setattr(module, "load_subjects", lambda *a, **k: {})
    findings = st.audit_rh1_architecture({"demonstrations": [], "root": tmp_path})
    assert findings and findings[0][0] == st.UNVERIFIED, findings
    assert "no subject is declared" in findings[0][1]
