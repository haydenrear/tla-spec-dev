"""SV-07: the candidate bar carrying demonstrated refutability, and its price.

## What is under test, and what the failing input is

`scripts/candidate_note_bar.py` derives a candidate bar from the card at run time
and prices it. Everything asserted here is a property of THAT derivation, and the
two properties that matter are the two the epic put teeth on:

- **the served surface must not grow** -- asserted as bytes and as rungs, against
  the shipped card rather than against a number written down here; and
- **no anchor moves** -- asserted as the anchors digest being byte-identical,
  which is the executable form of *"do not add a rung"*. A candidate that grew a
  rung would move that digest and fail here before anyone read its prose.

**The demonstrated failing input is on real sealed cards, not on a fixture**
(`R1`): `test_the_note_prompt_is_inside_both_seals` puts the candidate prompt
into the card WITHOUT the version row the change rule requires and shows the
card's own rule refusing it, and then shows the two real version-5 cards in
`specs/results/scorecards/close-the-loop-cl03-v5/` -- which agree with the
shipped bar today -- drifting against the candidate. That is the measurement
behind `SV-07-DF-01`: **the recorded-note prompt is cheap in bytes and is not
free**, because it sits inside both of the card's seals and a change to it costs
the same version bump that SV-02's byte table used to reject a scored rung.

Nothing here adopts the candidate.
`test_the_shipped_card_is_untouched_by_all_of_this` is the guard on that, and it
is deliberately the shortest test in the file.

## What this file does not state

The card is the one home for a dimension, an anchor or a scoring rule
(`tests/test_card_has_one_home.py`). Every needle below is read out of the card
or out of the generator at run time; no bar is spelled here.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
CARD = REPO_ROOT / "references" / "eval_scorecard.md"
GENERATOR = REPO_ROOT / "scripts" / "candidate_note_bar.py"
SCORE_TOOLS = REPO_ROOT / "examples" / "validation" / "scorecards" / "score_tools.py"

#: The two real sealed cards that were served the CURRENT bar. Named rather than
#: globbed: a card that stops being served the shipped bytes is a fact this test
#: should report, not one it should quietly stop looking at.
V5_CARDS = [
    REPO_ROOT / "specs/results/scorecards/close-the-loop-cl03-v5/toolchain_removal"
    / "20260811-cl03v5-CL-p1/scorecard.json",
    REPO_ROOT / "specs/results/scorecards/close-the-loop-cl03-v5/toolchain_removal"
    / "20260811-cl03v5-CL-p2/scorecard.json",
]


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def st():
    return _load(SCORE_TOOLS, "sv07_st")


@pytest.fixture(scope="module")
def gen():
    return _load(GENERATOR, "sv07_gen")


@pytest.fixture(scope="module")
def built(gen, st):
    return gen.build(st, CARD.read_text())


def test_the_candidate_does_not_grow_the_served_surface(built):
    """The epic's surface metric, asserted against the card and not against a literal."""
    _, f = built
    assert f["served_after"] <= f["served_before"], f
    assert f["served_after"] - f["served_before"] == -15, (
        "SV-02 priced this carrier at -15 bytes with the real renderer. A different "
        "number here means the card moved under the price, and the price is the "
        "argument -- re-derive it before changing this assertion.")


def test_the_candidate_adds_no_rung_and_moves_no_anchor(built):
    """`An anchor is permanent` -- so the candidate must not touch one, executably."""
    _, f = built
    assert f["rungs_after"] == f["rungs_before"], f
    assert f["anchors_digest_after"] == f["anchors_digest_before"], (
        "the candidate changed an anchor. It is a NOTE prompt and nothing else; a "
        "carrier that moves the anchors digest is the rung SV-02 rejected, arriving "
        "without being argued for.")


def test_exactly_one_thing_a_judge_reads_moves(built, st):
    """A note prompt, and nothing else. Both sides come out of the parse."""
    _, f = built
    assert len(f["served_diff"]) == 1, f["served_diff"]
    old, new = f["served_diff"][0]
    assert old == f["prompt_before"]
    assert new == f["prompt_after"]


def test_the_candidate_asks_nothing_about_where_a_case_came_from(built):
    """Provenance-blind BY CONSTRUCTION, which is the whole claim being carried.

    The property SV-02 found is that the artifact's own checking has a
    demonstrated red and a named green region. A prompt that asks who or what
    wrote the cases is the retired clause returning under a new name, which the
    work order names as the trap.
    """
    _, f = built
    prompt = f["prompt_after"].lower()
    for word in ("generated", "generator", "model-derived", "hand-written",
                 "property-based", "fuzz", "tlc", "tla", "corpus", "spec",
                 "projection", "descriptor"):
        assert word not in prompt, (
            f"the candidate prompt names {word!r}. Where a case came from is not an "
            f"input to this property; a prompt that asks for a provenance is D1's "
            f"retired clause with the ladder taken off.")


def test_the_note_prompt_is_inside_both_seals(gen, st, tmp_path):
    """`SV-07-DF-01`, demonstrated on REAL sealed cards rather than on a fixture.

    Two halves. First the card's own change rule, executed against a card that
    carries the candidate prompt and NOTHING ELSE -- no bumped declaration, no
    version row. Second, the two real version-5 cards, which agree with the
    shipped bar today and stop agreeing with the candidate. Together they are the
    measurement: a recorded-note prompt is not outside the seals, so editing one
    costs a version bump.
    """
    st_card = st.load_rubric(CARD)
    version = st_card["card_version"]
    key = st.NOTE_KEY[st.RETIRED_DIMS[0]]
    pattern = gen.note_bullet_pattern(st, key, st_card["notes"][key]["name"])
    text = CARD.read_text()
    unbumped = pattern.sub(
        lambda m: m.group(0).replace(m.group(1), gen.CANDIDATE_PROMPT, 1), text, count=1)
    assert unbumped != text

    copy = tmp_path / "eval_scorecard.md"
    copy.write_text(unbumped)
    problems = st.version_history_problems(st.load_rubric(copy))
    assert any("changing silently" in p for p in problems), problems
    assert not st.version_history_problems(st_card), (
        "the shipped card satisfies its own change rule; if this fails the tree is "
        "already red and the assertion above proves nothing")

    # And on the record. `served_digest` is what a card writes down about the
    # bytes it was handed, so a prompt edit re-bases every card that recorded the
    # current one -- here, two real ones.
    candidate, _ = gen.build(st, text)
    cand_path = tmp_path / "candidate.md"
    cand_path.write_text(candidate)
    cand = st.load_rubric(cand_path)
    shipped_served = st.served_digest(st_card, version)
    candidate_served = st.served_digest(cand, version + 1)
    assert shipped_served != candidate_served
    for path in V5_CARDS:
        card = json.loads(path.read_text())
        assert card["scorecard_version"] == version, path
        recorded = card["rubric"]["served_digest"]
        assert recorded == shipped_served, (
            f"{path} no longer records the bytes the shipped card serves; the drift "
            f"below would then be about something else")
        _, notes = st.check(card, str(path), cand)
        assert any("SERVED-DRIFT" in n for n in notes), (path, notes)
        # the same card against the shipped bar does not drift -- so the drift is
        # a fact about the candidate and not about the card (R2)
        _, clean = st.check(card, str(path), st_card)
        assert not any("SERVED-DRIFT" in n for n in clean), (path, clean)


def test_the_generator_refuses_a_card_it_cannot_derive_from(gen, st, monkeypatch):
    """`R1` for the generator itself: a demonstrated failing input.

    Everything the substitution keys on is read out of the card, so a card that
    renamed the note must make this raise rather than edit the wrong bullet or
    silently edit nothing. The needle is built from the parse, so the failing
    input is built the same way.
    """
    card = st.load_rubric(CARD)
    key = st.NOTE_KEY[st.RETIRED_DIMS[0]]
    name = card["notes"][key]["name"]
    text = CARD.read_text().replace(f"**{key} — {name}.**", f"**{key} — {name} x.**", 1)
    with pytest.raises(gen.CandidateError):
        gen.build(st, text)


def test_the_candidate_is_a_bar_that_can_actually_be_served(built, st, tmp_path):
    """It has to survive `serve`'s own refusals, or the re-score cannot be run."""
    text, f = built
    path = tmp_path / "candidate.md"
    path.write_text(text)
    cand = st.load_rubric(path)
    assert cand["card_version"] == f["candidate_version"]
    assert f["candidate_version"] in st.supported_versions(cand)
    assert st.version_history_problems(cand) == []
    assert st.rubric_leak_problems(cand) == []
    served = st.served_rubric(cand, cand["card_version"])
    assert len(served.encode()) + 1 == f["served_after"]


def test_the_shipped_card_is_untouched_by_all_of_this(st):
    """Nothing in this ticket adopts the candidate. This is the guard on that."""
    card = st.load_rubric(CARD)
    assert card["card_version"] == 5
    assert len(st.served_rubric(card, 5).encode()) + 1 == 6281
    assert st.version_history_problems(card) == []
