# Self-improvement ledger

**The metric is the delta, not the total.** One epic's scorecard says how good an
artifact is. This file says whether *we* are getting better, by carrying the same
dimensions across epic boundaries so the movement is visible.

Read `references/eval_scorecard.md` first — it defines the five dimensions, the
anchors, and the rules that make a judged score hard to game.

## How this file is maintained

- Every epic seals its scorecards into
  `specs/.history/<workflow>/closed-snapshot/results/scorecards/` at close. Those
  are immutable. This file is the index across them.
- Three kinds of pass exist and they are **not interchangeable**:
  - **`pass: 1` / `pass: 2`** — two judges, blind to each other and to arm.
    These decide goals. Only these.
  - **`pass: 0`** — an **owner tracking pass**, non-blind, single judge, taken
    mid-epic to keep a datapoint that would otherwise be lost. Never decides
    anything. Always labelled.
  - **adjudication** — a third pass, run only where two blind judges differed by
    more than 1, and required to cite **new** evidence rather than re-read the
    same lines.
- A row is only comparable to another row **on the same example**. Never average
  across examples: `ex6_jenga` is deliberately incoherent and is *supposed* to
  score low on D3.

## Baseline — architectural-coherence (sealed 2026-08-03, commit `ab0dfee`)

Two judges, blind, **zero contested dimensions** across 25 independent scores —
maximum spread 1, and D1 and D2 identical on all five examples.

| example | D1 bugs | D2 complexity | D3 modularity | D4 behavior | D5 honesty | total |
|---|---|---|---|---|---|---|
| ex1_scaffold_only | 2 / 2 | 2 / 2 | 1 / 1 | 3 / 2 | 3 / 3 | 11 / 10 |
| ex3_over_complex | 2 / 2 | 3 / 3 | 1 / 2 | 3 / 3 | 3 / 3 | 12 / 13 |
| ex4_pipeline_coherent | 2 / 2 | 2 / 2 | 3 / 3 | 3 / 4 | 4 / 3 | 14 / 14 |
| ex5_pipeline_divergent | 1 / 1 | 2 / 2 | 1 / 1 | 2 / 2 | 4 / 4 | 10 / 10 |
| ex6_jenga | 0 / 0 | 1 / 1 | 0 / 1 | 0 / 0 | 4 / 4 | 5 / 6 |

**The three facts that define the next epic's targets:**

1. **D1 never reached 3, anywhere, from either judge.** Every fixture stops at
   "content assertions catch content faults". Nothing reaches "catches a fault in
   a class the whole-view corpus structurally cannot reach on its own". Guard
   relaxation measured 0 of 3 on both arms and 0 of 4 on a blind catalogue;
   ordering 0 of 2 on everything, including the hand-written suite.
2. **D2 never reached 4**, and both judges withheld it for the *same* reason: the
   reduction was not shown behavior-preserving. The rubric makes D2 = 4 require
   D4 ≥ 3, so a simplification paid for in lost behavior cannot score.
3. **D3 reached 3 once and 4 never.** The predecessor also proved *why* import
   topology is not modularity: a 41-line re-export erased every divergence with
   the coupling proven live at runtime, and one fixture's seeded "absence" is a
   module taking a parameter instead of importing — strictly better decoupling
   that the check called dead architecture.

## In flight — hexagonal-prompting

| example | arm | pass | D1 | D2 | D3 | D4 | D5 | total | date |
|---|---|---|---|---|---|---|---|---|---|
| ab_quota_ledger | A (control) | 0 owner | 0 | 2 | 1 | 2 | 3 | **8**/20 | 2026-08-04 |

**Pre-treatment reading.** D1 = 0 because no model-derived case exists yet — the
model ships and TLC is green, but the corpus is HP-03's work; the hand-written
suite's 10-of-10 is D4 and mechanical-block material, not D1. D3 = 1 because the
domain imports `pathlib` and writes the ledger file itself, so there is no port
and no swap. **Both floors are the intended ones**: they are exactly the two
numbers the epic's goals target, and a control that already scored well would
have left the experiment nothing to measure.

Arm B has no row yet — HP-02 is authoring the prompt that produces it.

## What would count as self-improvement

Not a rising total. Specifically:

- **D1 crossing 3 on any example** — the first time generated cases catch a class
  the whole view cannot reach. This has never happened.
- **D2 reaching 4**, which by construction drags D4 to 3 with it: a
  simplification demonstrated behavior-preserving rather than asserted.
- **D3 reaching 4** — a driven port exercised by a real adapter *and* a fake with
  the same cases passing against both. Never reached.
- **D5 holding.** A rise in D1 bought by a fall in D5 is not improvement; it is
  the toolchain learning to overclaim. Watch this column when the others move.

## What would count as evidence we are fooling ourselves

Recorded here because it is easier to write down before the results than after:

- **Every prediction passing.** Six of the predecessor's were wrong and knowing
  which six was the whole value. A round where nothing surprises measured nothing.
- **Findings arriving only from the suite.** Both predecessor rounds produced
  their best finding from an agent asked what it *rejected*, and **zero** from
  re-running the suite. HP-06 reports findings by channel; a suite-only round
  means the suite has stopped being informative.
- **A score moving without an artifact moving.** The mechanical block sits beside
  the judgement precisely so this is visible. Measurement and judgement
  disagreeing is a finding, not a rounding error.
- **A withheld case passing that its siblings failed.** Whenever a fix is
  measured on the instrument that found the defect, it is fitting to the test set
  by construction — which is what the predecessor did on every repair ticket.
