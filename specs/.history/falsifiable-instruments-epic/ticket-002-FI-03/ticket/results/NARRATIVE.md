# FI-03 — can the scorecard carry a delta?

**Verdict: `GOAL-scorecard-carries-a-delta` is MISSED, on D4 and on D5.**

Full record and every number:
`specs/results/scorecards/falsifiable-instruments/GOAL-scorecard-carries-a-delta/RESULT.md`.
Byte-identity of the scored trees: `BYTE-IDENTITY.md` beside it. The judges'
prompts: `JUDGE-DISPATCH-v1.md` and `JUDGE-DISPATCH-v2.md`, the first ones this
repository has preserved.

## What was measured

Three sealed artifacts, verified byte-identical at the git-tree-object level and
per file, scored IN PLACE — no copy was made, so no copy could drift. Four fresh
blind judges in two pairs: one pair under `scorecard_version 1` (the card
unchanged, same rubric digest `sha256:e33638087c4191da` the sealed PA-06 cards
carry), one pair under `scorecard_version 2`. Twelve cards, sixty judge-scores.

| comparison | judge-scores | worst per judge | summed \|movement\| |
|---|---|---|---|
| EVAL-RERUN → PA-06 — **the epic's baseline, re-derived** | 20 | **2** | **13** |
| PA-06 → FI-03 v1 (both judges packet-only) | 30 | 1 | 9 |
| PA-06 → FI-03 v2 (both judges executed) | 30 | 1 | **5** |
| EVAL-RERUN → FI-03 v1 | 20 | **2** | 7 |
| EVAL-RERUN → FI-03 v2 | 20 | **2** | 10 |
| FI-03 v1 → v2 — the version bump | 30 | 1 | **4** |

**Met against the adjacent sealed row. Missed against the row before it**, where
D4 moves 2 in both arms and D5 moves 2 in the v2 arm.

**D2 and D3 moved zero on all 60 judge-scores. D1 moved zero against
EVAL-RERUN.** Those three can carry a delta. D4 and D5 cannot.

## What was built

1. **`judging_practice` is a required field** on every filled card from
   `scorecard_version 2` — `executed_own_faults` and `what_was_run`. `false` is
   legal and recorded as `PACKET-ONLY`; the one consequence is that **D4 = 4 is
   rejected by `check`** when it says false, which is D4's own anchor text made
   checkable. D1 and D5 are deliberately not gated.
2. **The instability caveat is `R-H5`**, with a check `audit` runs: a
   `[[movement]]` names two cards and `audit` re-derives its `points` from them
   on every run, and `readable = true` across a card with no recorded practice
   is a violation. `demonstrate_rh5.py` breaks the live ledger both ways and
   confirms it goes red; the suite runs it.
3. **`scorecard_version` 2, with the bump's own rule executed**: an
   anchors-only digest is declared per version in the rubric and recomputed by
   `check`, so "keep the old anchors" is a machine statement; and
   `scaffold --card-version 1` exists so the previous card can be reproduced,
   which is what made the both-versions re-score possible.

## Model delta

**None, as the plan expected.** `specs/tickets/FI-03/current` equals `desired`.
Nothing under `scripts/` or the TLA+ model changed; the work is entirely in
`examples/validation/scorecards/`, `references/` and `tests/`.

## Findings

`FI-03-DF-01` (no round ever preserved its judge prompt), `FI-03-DF-02` (the
rubric digest is blind to the prose that moved the judges), `FI-03-DF-03` (the
sealed evidence packets contradict themselves about their own controls),
`FI-03-DF-04` (the instrument log conflates the kill-table instrument with the
scorecard and has never recorded a change to the latter). **None fixed.**
