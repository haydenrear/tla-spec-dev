# Judge dispatch — FI-03 re-score, scorecard_version 2

**This file is the prompt, and it is IDENTICAL to `JUDGE-DISPATCH-v1.md`
except for the card paths and the one section marked NEW below.** That is the
point: the v1 and v2 arms differ in the card, not in the dispatch, so the
difference between them is attributable.

Two judges receive the text below, independently, in parallel, blind to each
other. `{{PASS}}` is `1` or `2`. Nothing else differs between them.

---

You are a **blind judge**. You score three software artifacts against a fixed
rubric and you write your scores into cards that have already been scaffolded
for you.

## What you score

Three complete artifacts, all implementing the same specification:

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/`

Each directory holds that artifact's implementation, that author's own tests,
that author's `NOTES.md`, and an `EVIDENCE.md` packet (shared-suite result,
full per-mutant per-instrument kill table with a `seeded_by` column, the
per-class block, the port-binding columns, the executability table, the control
status unabridged including every red one, and a mechanical block covering all
three artifacts, neutrally labelled).

The labels `T`, `U`, `W` are **opaque**. They are not the artifacts' real names
and the mapping is not in any directory you may read. Do not go looking for it.
If you work out which is which, say so in your Disclosures — a disclosed leak
is recorded, never grounds to discard a card.

## What else you may read

- `references/eval_scorecard.md` — the rubric. Read it.
- `examples/validation/ab/FEATURE.md` — the shared specification both authors
  were given.
- `examples/validation/ab/tests/test_behavior.py` — the shared behavioral suite.

## What you may NOT read

- `examples/validation/ab/arm_a/`, `arm_b/`, `arm_c/` — the prompts.
- `examples/validation/ab/README.md`, `seeded_faults.toml`,
  `check_catalogue.py`, `reference/`, `reference_ports/`.
- Anything named `PREDICTIONS*`.
- **Everything under `specs/results/scorecards/` except the three
  `blind/artifact_*/` directories named above and your own card directories**,
  including everything under `falsifiable-instruments-rescore-v1/` and
  `falsifiable-instruments/`.
  In particular: no `UNBLINDING.md`, no `RESULTS.md`, no `INDEX.md`, no
  `SELF-IMPROVEMENT.md`, no `INSTRUMENT-LOG.toml`, no `HISTORY-*.md`, no other
  round's cards, no `measure/`, no `arms/`, no `channels/`.
- Everything under `specs/.history/`.
- Every `*EPIC*.md` at the repository root, and `specs/desired_program_model/`.
- Any other judge's output. Specifically, do not read any directory whose name
  ends `-p{{OTHER_PASS}}`.

If you open one of these by accident, **say so in your Disclosures**. It is
recorded; it is not held against you and the card is not discarded.

## What you write

Three cards, already scaffolded, one per artifact:

```
specs/results/scorecards/falsifiable-instruments-rescore-v2/ab_quota_ledger/20260806-v2-T-p{{PASS}}/
specs/results/scorecards/falsifiable-instruments-rescore-v2/ab_quota_ledger/20260806-v2-U-p{{PASS}}/
specs/results/scorecards/falsifiable-instruments-rescore-v2/ab_quota_ledger/20260806-v2-W-p{{PASS}}/
```

Each holds `scorecard.json`, `scorecard.md` and `mechanical.json`. **The anchors
are already written into both files** — the bar for a score sits in the same
file as the score. Leave the `anchors` blocks exactly as scaffolded.

In each `scorecard.json`:

- set `status` to `"filled"`,
- set `commit` to `51fe73d`,
- set `judge.model` to `claude-opus-5[1m]`,
- fill `judging_practice` (see below),
- fill `score`, `citations`, `rationale` and `refuses_to_claim` for D1..D5,
- set `total` to the sum,
- write a one-sentence `verdict` a reader can act on.

Mirror the same scores, citations, `refuses_to_claim` and rationale into
`scorecard.md`, and fill its **Verdict** and **Disclosures** sections.

Leave `mechanical.json` alone unless you measured something; it is recorded and
never scored.

## Judging practice — a required field on this card *(NEW in version 2)*

This card is **scorecard_version 2**, and it asks you to record something
version 1 did not: **whether you seeded a fault of your own and ran it against
the artifact, or scored the evidence packet.**

- Fill `judging_practice.executed_own_faults` with `true` or `false`, and
  `judging_practice.what_was_run` with what you actually ran.
- **Both answers are legal and neither is the right one.** `false` is recorded,
  not corrected. Do not change what you do in order to produce a particular
  value in this field, and do not change the field to match what you wish you
  had done.
- The one consequence: **D4's anchor 4 is only awardable when this says
  `true`**, because that anchor asks for a behavior-breaking change *shown to
  be caught*. The schema check enforces it.
- Decide how you want to judge first, then record it. Read the rubric's rule 8
  and its R-H5 section for why the field exists.

## The rules you score under

They are reproduced inside every `scorecard.md`. The ones that get broken most:

1. **Score artifacts, never claims.** A summary saying "the adapters assert
   content" is not evidence; the adapter code is.
2. **Every score ≥ 2 cites `file:line`.** An uncited 2-or-more is capped at 1
   mechanically by the schema check, so an uncited score is a wasted score.
   Cite paths as they appear from the repository root.
3. **Every score of 4 additionally names something the artifact refuses to
   claim**, in `refuses_to_claim`. A 4 with a null there fails the check.
4. **Prose quality is never an input.** Say so in the rationale if the writing
   tempted you.
5. **Score the LOWEST anchor the artifact fully satisfies.** When torn between
   two, take the lower and say why.
6. **The mechanical block is recorded, never scored.** Where the block and your
   judgement disagree, that disagreement is a finding — write it down rather
   than splitting the difference.

## Verifying your cards

When you are done, run:

```
python3 examples/validation/scorecards/score_tools.py check \
    specs/results/scorecards/falsifiable-instruments-rescore-v2/ab_quota_ledger/20260806-v2-T-p{{PASS}} \
    specs/results/scorecards/falsifiable-instruments-rescore-v2/ab_quota_ledger/20260806-v2-U-p{{PASS}} \
    specs/results/scorecards/falsifiable-instruments-rescore-v2/ab_quota_ledger/20260806-v2-W-p{{PASS}} \
    --require-filled
```

It must report `0 problem(s)`. Do not change a score to make the check pass —
add the citation or the `refuses_to_claim` it is asking for, or lower the score
because you could not support it, and say which you did.

## Disclosures

Every card's `scorecard.md` ends with a Disclosures section. Fill it. It asks
for three things and all three matter:

- anything you saw that you were not meant to see,
- **anything you ran**, and whether it changed anything on disk,
- and anything you **REJECTED** — a score you nearly gave and did not, a piece
  of evidence you decided not to count, a conclusion you talked yourself out
  of. For four rounds running, the single most valuable output of this project
  has come from that question, and zero has come from re-running the suite.

## Report back

A short summary: the fifteen scores, your `judging_practice` values, the one thing that most nearly changed
your mind on each artifact, and what you rejected. Do not report anything you
were forbidden to read.
