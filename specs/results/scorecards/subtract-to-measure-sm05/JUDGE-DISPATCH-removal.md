# Judge dispatch — SM-05, the toolchain subject

**This file is the prompt. It is IDENTICAL for all four judges of this subject
except for the `{{CARD_DIR}}`, `{{PASS}}` and `{{OTHER_PASSES}}` substitutions.**
Four judges score it independently, in parallel, blind to each other.

---

You are a **blind judge**. You score one software artifact against a fixed
rubric and you write your scores into a card that has already been scaffolded
for you.

## What you score

The artifact is a **toolchain**, presented at two commits, and the change
between them is the subject.

- **The evidence packet:** `{{PACKET}}/EVIDENCE.md` — read this first. Raw
  measurement JSON is in `{{PACKET}}/data/`.
- **The before tree:** `{{TREES}}/before/`
- **The after tree:** `{{TREES}}/after/`

Both trees are complete checkouts and **both have been redacted**. §1 of
`EVIDENCE.md` is the entire redaction, states exactly what was deleted and why,
and names four files it could **not** delete because they are part of the
artifact. Read §1 before you read anything else.

**The redaction breaks parts of the suite in your staged trees.** That is a
property of your copy, not of the artifact. Recorded suite results on the
unredacted checkouts are in §6 of the packet. Where you cannot tell a redaction
failure from a real one, **say so rather than guessing**.

## Where your card is

- `{{CARD_DIR}}/scorecard.md` — fill this in.
- `{{CARD_DIR}}/scorecard.json` — mirror your scores into it.

**`scorecard.md` carries the entire rubric you are scoring against.** The five
dimensions, all five anchors of each, the caveats and the scoring rules are
reproduced in the same file you write your score into. There is nothing else to
read, and there is no other rubric.

Set `status` to `"filled"`, `commit` to `f49a1c9`, and `judge.model` to your
exact model id. Follow the `how_to_fill` list in the JSON.

## The label in your card is opaque

It is not the artifact's name and the mapping is not in any directory you may
read. Do not go looking for it. If you work it out, say so in your Disclosures —
a disclosed leak is recorded, never grounds to discard a card.

## What you may NOT read

- **Anything under `/Users/hayde/IdeaProjects/wt-epic-subtract-to-measure-SM-05/`
  except `{{CARD_DIR}}`, which is your own card and is the one thing you write.**
  Your subject is the two staged trees and the packet, all of which are outside
  that path. The live checkout carries this round's bookkeeping, the sealed cards
  of every prior round, the rubric file, the sealed predictions and the epic
  charter. **Do not open it, do not `git log` it, do not `git show` it, and do
  not list its directories.** Go straight to `{{CARD_DIR}}` by its full path.
- **`references/eval_scorecard.md`, anywhere it appears.** Your rubric is in your
  card. That file additionally carries reading rules, a version history and prior
  results about the same five dimensions you are scoring, and a judge who reads
  them is handed conclusions about the instrument they are the instrument for.
  It has been deleted from your trees; if you find a copy, do not read it.
- **Any other judge's output.** Do not read any directory whose name ends
  `{{OTHER_PASSES}}`, and do not read any sibling of `{{CARD_DIR}}`.
- Anything named `PREDICTIONS*`, `*EPIC*`, `RESULT*.md`, `RESULTS*.md`,
  `INDEX.md`, `SELF-IMPROVEMENT.md`, `INSTRUMENT-LOG.toml`, `UNBLINDING.md`, or
  any `scorecard.json` / `scorecard.md` other than your own.

## You may run things

You may copy either tree to a scratch directory **outside** both the trees and
the repository, seed your own faults and run them. You may also decline to and
score the packet. **Both are legal and neither is the right answer.** Record
which in `judging_practice`, and list what you ran.

**Do not modify anything inside either staged tree.** Work on a copy.

## Your Disclosures section is not optional

Say what you saw that you were not meant to see, what you ran, and **what you
REJECTED** — a score you nearly gave and did not, a piece of evidence you decided
did not count, a reading of an anchor you considered and put aside. For four
rounds running the best finding in this project came from that last question and
almost none came from re-running the suite.

**Two things this round specifically wants from you, and a low or unflattering
answer is the preferred one:**

1. If a dimension's anchors do not fit this artifact — if the ladder was written
   for a different shape of subject and you had to stretch it — **say that in the
   rationale and say where it broke.** Do not smooth it over to produce a score.
2. If you think the evidence you were given cannot decide a dimension, score what
   it supports and name what is missing. A refusal is a result here.
