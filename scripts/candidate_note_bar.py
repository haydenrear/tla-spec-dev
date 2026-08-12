#!/usr/bin/env python3
"""SV-07. Build the CANDIDATE bar that carries demonstrated refutability, and price it.

## What this is, and what it deliberately is not

`references/scoring_validation.md` (SV-02) found one property that separates
well-validated code from badly-validated code without grading which tools made
the tests: **the artifact's own checking has a demonstrated red, and the region
where it stays green is named.** It priced three carriers for it against the real
renderer and defended the cheapest -- sharpening the recorded-note prompt that
already elicits the property, at **-15 bytes and no new rung.**

**SV-07 tried to ship that edit into the card and could not, and the reason is
the point.** The prompt a judge is served for a recorded note is inside BOTH of
the card's seals: `rubric["digest"]` (the notes are in its payload) and the
served digest that `## Version history` declares per version. Change one word of
it and the card's own change rule -- executed by
`score_tools.version_history_problems` -- says *"Bump the card, or restore the
text"*. Version 5's own row is the precedent: it moved no anchor, moved only
served bytes, and took a bump to do it.

So **the note is not free.** It is cheap in BYTES, which is the metric the epic
put on the surface, and it costs the same version bump that SV-02 used as the
decisive argument against restoring a scored rung. The two carriers the byte
table ranked -15 against +682 are not distinguished by the rule that actually
gates them. Filed as `SV-07-DF-01`.

**This script is what can ship without that bump.** It DERIVES a candidate bar
from the card at run time -- it is a generator, never a second copy -- applies
exactly one substitution, adds the version row the change rule requires, and
prices the result with the real renderer. It writes nothing unless `--out` is
given, changes nothing in the tree, is imported by no production code, and is
not a gate: it always exits 0 unless it cannot read the card.

**Nothing here adopts the candidate.** `references/eval_scorecard.md` stays at
its shipped version, `serve` emits the same bytes it emitted before this file
existed, and no adopter is affected. What the candidate is FOR is the one
experiment SV-02 says has to run before anybody restores anything
(`references/scoring_validation.md` section 9, first bullet): **a re-score of one
prior example under both wordings.** The card's change rule already names the
mechanism -- *"freeze the rubric file before you edit it, and scaffold the old
arm with `--rubric <the frozen copy> --card-version N`"* -- and three tickets have
done it by operator sequencing, which the card itself calls out as sequencing
rather than a mechanism (`FI-06-DF-11(c)`, open). The three prior freezes froze
the PAST bar. A both-wordings round also needs the FUTURE one, and that is the
half nothing produced.

## Why a generator and not a frozen file

`tests/test_card_has_one_home.py` measured what a second copy of the card costs:
four copies were made to disagree with it and three of the four were UNCAUGHT by
the whole suite. A checked-in candidate would be a fourth whole copy, exempt only
by an entry that promises somebody compares it -- and there is nothing yet to
compare a candidate against, because the row it would be compared to does not
exist in the card. Deriving it at run time removes the copy entirely: change the
card and the candidate changes with it, or this script stops matching and says
so.

## Run it

    python3 scripts/candidate_note_bar.py               # price only, writes nothing
    python3 scripts/candidate_note_bar.py --out /tmp/candidate.md

Then, to score an arm against it:

    python3 examples/validation/scorecards/score_tools.py serve --rubric /tmp/candidate.md
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import re
import sys
import tempfile

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
CARD = REPO_ROOT / "references" / "eval_scorecard.md"
SCORE_TOOLS = REPO_ROOT / "examples" / "validation" / "scorecards" / "score_tools.py"

#: The candidate prompt. SV-02's `P1`, which its section 6 defends by name, and
#: the ONLY string in this file that is not read out of the card at run time.
#:
#: Half of it is a DEDUPLICATION rather than an addition. The shipped prompt ends
#: by asking the judge to name a fault it seeded, and the served surface already
#: asks that twice before the notes are reached -- once in a numbered scoring
#: rule and once in the required judging-practice block. Those bytes are spent
#: here on the two things judges volunteer anyway when no ladder is under them:
#: the denominator of the artifact's own checking, and the reason the region it
#: stays green on is structural. That is where the -15 comes from.
#:
#: It names no tool. Hand-written, generated, property-based, fuzzed and
#: model-derived cases satisfy it or fail it identically, which is the whole
#: claim: provenance-blind by construction.
CANDIDATE_PROMPT = ("What went red when you broke it, with the denominator, and "
                    "what class stays green by construction?")

#: What the candidate declares it changed, for its `## Version history` row.
CANDIDATE_SUMMARY = (
    "**THE ANCHORS DID NOT MOVE AND THE SERVED BYTES DID, and they FELL.** The "
    "recorded note for the retired bug-detection question stops asking the judge "
    "to name a fault it seeded -- which the served surface already asks twice "
    "before the notes are reached -- and asks instead for the denominator of the "
    "artifact's own checking and the class it stays green on by construction. No "
    "rung, no anchor and no dimension added, deleted or reworded; nothing about "
    "where a case came from is asked."
)


class CandidateError(RuntimeError):
    """The card is not in the shape this generator can derive a candidate from."""


def load_score_tools():
    spec = importlib.util.spec_from_file_location("sv07_score_tools", SCORE_TOOLS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def note_bullet_pattern(st, key: str, name: str) -> re.Pattern:
    """The markdown bullet a note's prompt lives in, SPELLED BY THE CARD.

    `load_rubric` returns the prompt whitespace-flattened, which cannot be
    substituted back into a reflowed bullet, so the bullet has to be found in the
    raw text. Both halves of the needle -- the note key and the note's name --
    come out of the parse, so a card that renames either one makes this raise
    rather than silently edit the wrong bullet.
    """
    return re.compile(
        r"^- \*\*" + re.escape(key) + r" — " + re.escape(name) + r"\.\*\* (.+?)"
        r"(?=\n- \*\*" + re.escape(key[:3]) + r"|\n\n|\Z)", re.M | re.S)


def rungs(served: str) -> int:
    """A rung is an anchor line in the bytes a judge is handed."""
    return sum(1 for line in served.splitlines()
               if line.startswith("- **") and line[4:5].isdigit())


def build(st, card_text: str, key: str | None = None,
          prompt: str = CANDIDATE_PROMPT) -> tuple[str, dict]:
    """Return (candidate markdown, facts about it). Reads the card, writes nothing."""
    card = st.load_rubric(CARD)
    version = card["card_version"]
    if key is None:
        # The note whose prompt duplicates what the served surface already asks.
        key = st.NOTE_KEY[st.RETIRED_DIMS[0]]
    note = (card.get("notes") or {}).get(key)
    if note is None:
        raise CandidateError(
            f"{CARD} declares no recorded note {key}. This generator substitutes ONE "
            f"note prompt and derives which one from the card; a card that stopped "
            f"carrying that note is a card this script must not guess at.")

    pattern = note_bullet_pattern(st, key, note["name"])
    hits = pattern.findall(card_text)
    if len(hits) != 1:
        raise CandidateError(
            f"{CARD}: expected exactly one bullet for {key}, found {len(hits)}. The "
            f"prompt has one home and this generator refuses to edit a card where "
            f"that is no longer true.")

    text = pattern.sub(lambda m: m.group(0).replace(m.group(1), prompt, 1),
                       card_text, count=1)

    decl = re.compile(r"^\*\*Scorecard version " + str(version) + r"\.\*\*", re.M)
    if len(decl.findall(text)) != 1:
        raise CandidateError(
            f"{CARD}: the version declaration is not where the change rule says it is "
            f"(`**Scorecard version N.**` at the top), so this generator cannot bump it")
    text = decl.sub(f"**Scorecard version {version + 1}.**", text, count=1)

    # The row the change rule requires. Both digests are computed from the
    # candidate AFTER the substitution, by the real renderer, so the row is a
    # measurement of this file rather than a promise about it.
    with tempfile.TemporaryDirectory(prefix="SV-07-candidate-") as tmp:
        scratch = pathlib.Path(tmp) / "eval_scorecard.md"
        scratch.write_text(text)
        probe = st.load_rubric(scratch)
        row = (f"| **{version + 1}** | `{probe['anchors_digest']}` | "
               f"`{st.served_digest(probe, version + 1)}` | {CANDIDATE_SUMMARY} |")
        last_row = _last_version_row(text, version)
        text = text.replace(last_row, last_row + "\n" + row, 1)
        scratch.write_text(text)
        final = st.load_rubric(scratch)

    before = st.served_rubric(card, version)
    after = st.served_rubric(final, version + 1)
    facts = {
        "card_version": version,
        "candidate_version": version + 1,
        "note": key,
        "prompt_before": note["prompt"],
        "prompt_after": prompt,
        # `serve` prints the served string and a newline, so the surface metric
        # `serve | wc -c` is one byte more than the digested string. Both are
        # reported because the epic quotes the piped number.
        "served_before": len(before.encode()) + 1,
        "served_after": len(after.encode()) + 1,
        "rungs_before": rungs(before),
        "rungs_after": rungs(after),
        "anchors_digest_before": card["anchors_digest"],
        "anchors_digest_after": final["anchors_digest"],
        "served_digest_before": st.served_digest(card, version),
        "served_digest_after": st.served_digest(final, version + 1),
        "served_diff": _line_diff(before, after),
    }
    return text, facts


def _last_version_row(text: str, version: int) -> str:
    rows = [l for l in text.splitlines() if re.match(r"^\|\s*\*{0,2}\d+\*{0,2}\s*\|", l)]
    if not rows:
        raise CandidateError(f"{CARD}: no `## Version history` rows found")
    want = re.compile(r"^\|\s*\*{0,2}" + str(version) + r"\*{0,2}\s*\|")
    for row in rows:
        if want.match(row):
            return row
    raise CandidateError(f"{CARD}: version history carries no row for {version}")


def _line_diff(before: str, after: str) -> list[tuple[str, str]]:
    """Which SERVED lines differ. A candidate that moves more than one is a bug."""
    b, a = before.splitlines(), after.splitlines()
    if len(b) != len(a):
        return [("LINE COUNT MOVED", f"{len(b)} -> {len(a)}")]
    return [(x, y) for x, y in zip(b, a) if x != y]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="candidate_note_bar.py",
        description="Derive and PRICE the candidate bar carrying demonstrated "
                    "refutability. Writes nothing unless --out is given. Never a gate.")
    ap.add_argument("--out", default=None,
                    help="write the candidate here. Without it nothing is written.")
    ap.add_argument("--note", default=None,
                    help="which recorded note to substitute. Defaults to the one the "
                         "served surface already duplicates.")
    args = ap.parse_args(argv)

    st = load_score_tools()
    try:
        text, f = build(st, CARD.read_text(), key=args.note)
    except CandidateError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2

    print("## The candidate bar, priced by the real renderer")
    print(f"  card                      version {f['card_version']}   "
          f"{f['served_before']} bytes  {f['rungs_before']} rungs")
    print(f"  candidate                 version {f['candidate_version']}   "
          f"{f['served_after']} bytes  {f['rungs_after']} rungs   "
          f"delta {f['served_after'] - f['served_before']:+d} bytes, "
          f"{f['rungs_after'] - f['rungs_before']:+d} rungs")
    print()
    print(f"  anchors digest  {f['anchors_digest_before']} -> {f['anchors_digest_after']}"
          f"   {'UNCHANGED -- no rung, no anchor' if f['anchors_digest_before'] == f['anchors_digest_after'] else 'MOVED'}")
    print(f"  served  digest  {f['served_digest_before']} -> {f['served_digest_after']}")
    print()
    print(f"## What a judge would read differently ({len(f['served_diff'])} served line(s))")
    for old, new in f["served_diff"]:
        print(f"  - {old}")
        print(f"  + {new}")
    print()
    print("## What this did NOT do")
    print("  - it did not touch `references/eval_scorecard.md`")
    print("  - it did not bump the shipped card")
    print("  - it did not add, delete or reword an anchor")
    print("  - it is not a gate: nothing fails because of this file")
    if args.out:
        p = pathlib.Path(args.out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        print(f"\nwrote {p}", file=sys.stderr)
    return 0


if __name__ == "__main__":                          # pragma: no cover
    raise SystemExit(main())
