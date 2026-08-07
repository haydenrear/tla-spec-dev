# Judge dispatch — SM-04 re-score, scorecard_version 2 against 3

**This file is the prompt. It is IDENTICAL for all four judges except for the
card path and the `{{VERSION}}` / `{{LABEL}}` / `{{PASS}}` substitutions.** The
v2 and v3 arms differ in the card, not in the dispatch, so the difference
between them is attributable to the card.

Two judges per arm, independently, in parallel, blind to each other and blind to
the other arm's existence.

**Scale, stated up front so it is not read as more than it is.** One artifact,
four judges, twenty judge-scores. FI-03 measured its version bump with three
artifacts and twelve judges. This is a quarter of that power and the reduced
power is part of the result.

**Deliberate, disclosed, non-random choice of artifact.** `artifact_U` is the
artifact on which the D5 disagreement version 3 addresses was demonstrated. It
was chosen for that reason. Any D5 result here is therefore not a random sample.

---

You are a **blind judge**. You score one software artifact against a fixed
rubric and you write your scores into a card that has already been scaffolded
for you.

## What you score

- `specs/results/scorecards/ports-as-adapters/blind/artifact_{{LABEL}}/`

That directory holds the artifact's implementation, that author's own tests,
that author's `NOTES.md`, and an `EVIDENCE.md` packet (shared-suite result,
the per-mutant per-instrument kill table with a `seeded_by` column, the
per-class block, the port-binding columns, the executability table and the
control status unabridged including every red one).

The label `{{LABEL}}` in your card is **opaque**. It is not the artifact's real
name and the mapping is not in any directory you may read. Do not go looking for
it. If you work out which it is, say so in your Disclosures — a disclosed leak
is recorded, never grounds to discard a card.

## Where your card is

- `{{CARD_DIR}}/scorecard.md` — fill this in.
- `{{CARD_DIR}}/scorecard.json` — mirror your scores into it.

**`scorecard.md` carries the entire rubric you are scoring against.** The five
dimensions, all five anchors of each, the caveats and the scoring rules are
reproduced in the same file you write your score into. There is nothing else to
read.

Set `status` to `"filled"`, `commit` to `{{COMMIT}}`, and `judge.model` to your
model id. Follow the `how_to_fill` list in the JSON.

## What else you may read

- `examples/validation/ab/FEATURE.md` — the shared specification the author was
  given.
- `examples/validation/ab/tests/test_behavior.py` — the shared behavioral suite.

## What you may NOT read

- **`references/eval_scorecard.md`.** Your rubric is in your card. That file
  additionally carries reading rules, a version history and prior results about
  the same five dimensions you are scoring, and a judge who reads them is being
  handed conclusions about the instrument they are the instrument for.
- `examples/validation/ab/arm_a/`, `arm_b/`, `arm_c/` — the prompts.
- `examples/validation/ab/README.md`, `seeded_faults.toml`,
  `check_catalogue.py`, `reference/`, `reference_ports/`.
- Anything named `PREDICTIONS*`.
- **Everything under `specs/results/scorecards/` except the
  `ports-as-adapters/blind/artifact_{{LABEL}}/` directory named above and your
  own card directory.** In particular: no `UNBLINDING.md`, no `RESULTS.md`, no
  `RESULT.md`, no `INDEX.md`, no `SELF-IMPROVEMENT.md`, no `INSTRUMENT-LOG.toml`,
  no `HISTORY-*.md`, no `rubric_*_frozen.md`, no other round's cards, no
  `measure/`, no `arms/`, no `channels/`, no `blind/artifact_*` other than
  yours.
- Everything under `specs/.history/`.
- Every `*EPIC*.md` at the repository root, and `specs/desired_program_model/`.
- `specs/desired_program_model/deferred_findings.yaml`.
- Any other judge's output. Specifically, do not read any directory whose name
  ends `-p{{OTHER_PASS}}`, and do not read any directory under
  `subtract-to-measure-sm04-rescore-{{OTHER_VERSION}}`.
- `examples/validation/scorecards/score_tools.py` and `tests/test_score_tools.py`.

## You may run things

You may copy the artifact to a scratch tree outside the repository, seed your
own faults and run them. You may also decline to and score the evidence packet.
**Both are legal and neither is the right answer.** Record which in
`judging_practice`, and list what you ran. Do not modify anything inside the
repository.

## Your Disclosures section is not optional

Say what you saw that you were not meant to see, what you ran, and **what you
REJECTED** — a score you nearly gave and did not, a piece of evidence you
decided did not count, a reading of an anchor you considered and put aside. For
three rounds running the best finding in this project came from that last
question and zero came from re-running the suite.
