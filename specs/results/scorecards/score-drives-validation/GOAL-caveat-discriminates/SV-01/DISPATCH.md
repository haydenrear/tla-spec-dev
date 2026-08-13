# Judge dispatch — SV-01 (identical text for all four cards; only `CARD_DIR` differs)

You are a **blind judge**. You score one artifact against a rubric, and you have
no stake in the number.

## Your card

```
CARD_DIR = <<<CARD_DIR>>>
```

That directory holds three files:

- `scorecard.md` — **the rubric you score against is reproduced in full inside
  it.** Read it first, top to bottom. It carries the scoring rules, the anchor
  ladders for `D2` and `D3`, and the recorded notes `N-D1`, `N-D4`, `N-D5`.
- `scorecard.json` — the same card as data. **Your scores, citations,
  rationales, `refuses_to_claim`, `verdict`, `judging_practice` and `notes` go
  here**, and are mirrored into `scorecard.md` where it asks for them.
- `mechanical.json` — leave it alone unless you measure something worth putting
  in it. Rule 7: it is recorded and never scored.

You are scoring artifact **`GL`**. The label is opaque on purpose. **Do not go
looking for what it maps to.** If you work it out anyway, say so in your verdict
and in your report — a disclosed leak is recorded, never grounds to discard a
card.

## The artifact

```
ARTIFACT = /Users/hayde/IdeaProjects/wt-epic-score-drives-validation-SV-01/specs/results/scorecards/score-drives-validation/GOAL-caveat-discriminates/SV-01/blind/artifact_under_score
```

- `quota_ledger/` — the code.
- `tests/test_ledger.py` — the artifact's own suite.
- `NOTES.md` — **the author's own prose about what they built.** Scoring rule 1:
  score artifacts, never claims. If a claim in it matters to a score, check it
  against the code or run it.

Beside it, one level up in `.../SV-01/blind/`:

- `FEATURE.md` — the feature the artifact implements.
- `shared_suite/test_behavior.py` — a shared, hand-written behavioral suite that
  the artifact's author did not write and could not edit. It is a floor, not a
  result.

## Running things

The artifact's own suite:

```bash
cd "$ARTIFACT" && uv run --with pytest python -m pytest tests/test_ledger.py -q
```

The shared suite against this artifact (it needs to be told where the module is):

```bash
QUOTA_LEDGER_DIR="$ARTIFACT" QUOTA_LEDGER_IMPL=quota_ledger \
  uv run --with pytest python -m pytest \
  "/Users/hayde/IdeaProjects/wt-epic-score-drives-validation-SV-01/specs/results/scorecards/score-drives-validation/GOAL-caveat-discriminates/SV-01/blind/shared_suite/test_behavior.py" -q
```

**You may mutate the artifact to find out what its cases catch — but do it in a
COPY under your own scratch directory, never in the repository.** Copy it out,
break something deliberately, run the suite, record what died and what did not.
Scoring rule 8 requires you to say whether you did this. **Both answers are
legal and neither is the right one.** Do not choose one to look thorough.

## What you may read, and what you may NOT

**MAY:** your own `CARD_DIR`; everything under `.../SV-01/blind/`; anything you
write yourself in scratch.

**MAY NOT — and this is the whole of what makes the card worth anything:**

- `references/eval_scorecard.md` and
  `examples/validation/scorecards/rubric_v4_frozen.md`. **The rubric is already
  in your card, in full.** Those files also carry reading rules and *prior
  results about the very dimensions you are scoring*, and a judge who reads them
  is handed conclusions about the instrument they are the instrument for.
- **Any other scorecard, anywhere.** Nothing under
  `specs/results/scorecards/` except your own `CARD_DIR` and the `blind/`
  packet. Prior rounds have scored artifacts that may resemble yours.
- `specs/results/scorecards/score-drives-validation/GOAL-caveat-discriminates/SV-01/PREDICTIONS-SV-01.md`
  and anything else directly under that `SV-01/` directory. It states what this
  round expects you to say.
- `examples/validation/` other than the two packet copies given to you above;
  `examples/validation/scorecards/subjects.toml` in particular.
- Any `*-EPIC.md`, `NEXT-EPIC.md`, `SKILL.md`, `README.md` at the repository
  root; `specs/desired_program_model/`; `git log`, `git show`, `git diff`,
  `git blame`, or any other route into this repository's history.

If you read one of these by accident, **say so in your report.** It is recorded.
It is never grounds to discard a card.

## Filling the card

- **Score the LOWEST anchor the artifact fully satisfies.** Torn between two,
  take the lower and say why.
- **Every score ≥ 2 cites `file:line`**, as paths relative to `ARTIFACT` (e.g.
  `quota_ledger/domain.py:41`, `tests/test_ledger.py:244`). A score with no
  citation is capped at 1 by the schema check.
- **A score at the top of a scale must additionally name something the artifact
  refuses to claim** — put it in `refuses_to_claim`.
- `D2` and `D3` take scores. `N-D1`, `N-D4` and `N-D5` are **required and take
  no score**; *"I could not tell, and here is what I looked at"* is a correct
  answer and an empty note is not a legal card.
- Fill `judging_practice.executed_own_faults` (true/false) and
  `what_was_run` (a list of what you actually ran).
- Fill `verdict` with your one-paragraph summary.
- Set `"commit": "5e07dce"`.
- Set `judge.model` to the exact model id you are running as, and leave
  `judge.tier` as the empty string — it is derived.
- Leave `status` as `"unfilled"`; the round's operator sets it.

## Report back to whoever dispatched you

1. **`D2` and `D3`, with one sentence each.**
2. **Whether you seeded a fault and ran it, and what you ran.**
3. **The exact model id you are running as.**
4. **Anything you were exposed to that you should not have been**, or that you
   worked out about this artifact's provenance.
5. **WHAT YOU REJECTED** — the score you nearly gave and did not, the evidence
   you considered and set aside, the reading you rejected. This is asked of
   every blind agent in this project and it is often worth more than the score.

**A low score is not a bad outcome and a high score is not a good one.** The
number is a measurement. Write down what you found.
