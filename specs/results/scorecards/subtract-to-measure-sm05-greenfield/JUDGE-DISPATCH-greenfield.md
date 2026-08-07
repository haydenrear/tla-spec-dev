# Judge dispatch — SM-05, the greenfield-fixture subject

**This file is the prompt. It is IDENTICAL for all four judges of this subject
except for the `{{CARD_DIR}}`, `{{PASS}}` and `{{OTHER_PASSES}}` substitutions.**
Four judges score it independently, in parallel, blind to each other.

**It is deliberately the same dispatch, in the same words wherever the two
subjects allow it, as the one used for this round's other subject.** Where the
two differ, the difference is the subject and not the instructions.

---

You are a **blind judge**. You score one software artifact against a fixed
rubric and you write your scores into a card that has already been scaffolded
for you.

## What you score

- `/Users/hayde/IdeaProjects/wt-epic-subtract-to-measure-SM-05/specs/results/scorecards/ports-as-adapters/blind/artifact_U/`

That directory holds the artifact's implementation, that author's own tests,
that author's `NOTES.md`, and an `EVIDENCE.md` packet (shared-suite result, the
per-mutant per-instrument kill table with a `seeded_by` column, the per-class
block, the port-binding columns, the executability table and the control status
unabridged including every red one).

**The `U` in that path is a label from a PRIOR round.** It is not this round's
card label, it is not the artifact's real name, and it carries no information
about this round. It is left in place because the bytes of that directory are
sealed and this round will not edit them to tidy a path.

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

## What else you may read

- `examples/validation/ab/FEATURE.md` — the shared specification the author was
  given.
- `examples/validation/ab/tests/test_behavior.py` — the shared behavioral suite.

## What you may NOT read

- **`references/eval_scorecard.md`.** Your rubric is in your card. That file
  additionally carries reading rules, a version history and prior results about
  the same five dimensions you are scoring, and a judge who reads them is handed
  conclusions about the instrument they are the instrument for.
- `examples/validation/ab/arm_a/`, `arm_b/`, `arm_c/` — the prompts.
- `examples/validation/ab/README.md`, `seeded_faults.toml`, `check_catalogue.py`,
  `reference/`, `reference_ports/`.
- Anything named `PREDICTIONS*`.
- **Everything under `specs/results/` except the `ports-as-adapters/blind/artifact_U/`
  directory named above and your own card directory.** In particular: no
  `UNBLINDING.md`, no `RESULTS.md`, no `RESULT.md`, no `INDEX.md`, no
  `SELF-IMPROVEMENT.md`, no `INSTRUMENT-LOG.toml`, no `HISTORY-*.md`, no
  `complexity_ledger.json`, no `skill_feedback.md`, no `deferred_findings_*.yaml`,
  no `rubric_*_frozen.md`, no other round's cards, no `measure/`, no `arms/`, no
  `channels/`, no `blind/artifact_*` other than the one named above.
- Everything under `specs/.history/`.
- Every `*EPIC*.md` at the repository root, `PORTS-AS-ADAPTERS-STARTER-PROMPT.md`,
  `NEXT-EPIC.md`, `EPIC-HANDOFF.md`, and `specs/desired_program_model/`.
- `references/architecture_advice.md` and `references/hexagonal_prompting.md`.
- **Any other judge's output.** Do not read any directory whose name ends
  `{{OTHER_PASSES}}`, and do not read any sibling of `{{CARD_DIR}}`.
- `examples/validation/scorecards/score_tools.py`, `tests/test_score_tools.py`
  and `tests/test_card_has_one_home.py`.

## You may run things

You may copy the artifact to a scratch tree outside the repository, seed your own
faults and run them. You may also decline to and score the evidence packet.
**Both are legal and neither is the right answer.** Record which in
`judging_practice`, and list what you ran. Do not modify anything inside the
repository.

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
