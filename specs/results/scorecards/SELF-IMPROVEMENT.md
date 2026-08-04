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

### Movement log (owner tracking, mid-epic)

Recorded as tickets land so the deltas are not reconstructed at the end.

**HP-03 — `GOAL-catch-bugs` moved, and this is the first time it ever has.**
Guard relaxation, the class that measured **0 of 3** (round 1), **0 of 3**
(round 2, both arms) and **0 of 4** (a blind agent's independent catalogue) —
three catalogues, five instruments, two rounds — now measures **3 of 3** on
HP-01's seeded catalogue and **5 of 5** on a fresh independently authored one.
Verified by the owner from the committed per-mutant table, not from the report:
M01, M02 and M03 each SURVIVED the whole-view corpus and each was KILLED by the
negative corpus, in the same run, against the same reference implementation.

Soundness is one-sided by construction — evaluation is three-valued and every
unimplemented construct is UNKNOWN, which never emits — so an unsupported
construct costs completeness and never soundness. Controls green on both corpora.

**What that does NOT yet mean.** It is not a D1 score: D1 asks what
model-derived cases catch on a scored artifact, and the arms do not exist yet.
It is a mechanism result on the reference implementation. HP-06 turns it into a
D1 number, or does not.

**Three facts that travel with it, all against the mechanism:**

- **The generator is still worse than the hand-written suite.** Suite **10 of
  10**; whole-view corpus **5 of 10**; both corpora together **8 of 10**. Below
  the bar a suite written in an afternoon clears.
- **A positive control survives.** M07 is seeded in nobody's gap and is supposed
  to die on every instrument; it survives the whole-view corpus, because
  `Reserve` contributes zero executable cases. Only **3,440 of 43,128** positive
  cases (8.0%) are executable at all.
- **The "profile change" route is measured and does not work.** The fixture
  already ships explicit `Refuse*` actions — 39,100 cases, **90.7% of the
  corpus, zero executable**, because their parameters appear nowhere in their
  bodies. The generator produces the same refusals as 118 executable cases.

**A doctrine claim was retracted by measurement.** The record has said since
round 1 that ordering is invisible to every layer. HP-03's M09 died on the
whole-view corpus, because this model represents its ledger as a **sequence**.
Ordering is invisible when the modelled thing is a **set** — a property of the
model, not a limit of corpora. Anything citing "ordering is structurally
invisible" now needs that clause.

**And the negative corpus found something no prior instrument could see.** The
fixture model guards a reservation id that its own API allocates, so 4 of 118
negative cases assert rejection of a call the unmutated reference correctly
accepts — a true statement about a model that does not refine its own
`FEATURE.md`. Filed as HP-03-DF-01. This is the shape the project has valued
most: a finding about the *specification*, surfaced by running something.

**HP-04 — a PREDICTED null, which is the methodologically valuable kind.**
The mutant matrix **moved by zero cells**. HP-01 sealed that as negative
prediction **N05** before dispatch, explicitly modelled on the predecessor's
RP-02 — which closed a real oracle leak, took a recovery metric 0 of 5 to 5 of
5, and moved nothing. The difference this time is that it was **predicted rather
than discovered**, which is what a prediction file is for.

**And the counterfactual says why, which is worth more than the null.** Bind the
same action to an adapter differing *only* in having a `run(case, work_dir)`,
and M10 goes from surviving to **dying 8 of 8**. **The oracle's reach was never
the limit** — 9 of 18 adapters have no `run()` at all, so the oracle drives 8 and
reports 18. The declared `expected_effect` of "18 of 18" is **not met** and could
not be from this slice; the nine live in `production_adapters.py`, outside the
ticket's edit scope. Filed as HP-04-DF-01 rather than quietly rescoped.

**A number this project nearly acted on was wrong.** RC-02 reported **9 dead
ports**; only **2** are actually dead. The other **7 were never dead** — every
action declaring them was skipped, so "dead" was an artifact of the run aborting
early. A manifest edit made on that column would have **removed live surface**.
This is the second time in two epics that a confident number about our own
bookkeeping turned out to be a measurement artifact.

**Two defects found only by running, neither of which anyone asked for:**

- **`EffectSandbox` never patched `Path.open`.** `path.open("a")` — the
  idiomatic durable append — was invisible while `open(path, "a")` was recorded.
  Surfaced because the oracle appeared to "kill" the **ordering negative
  control**: the mutant swaps that append for `write_text`, so the oracle had
  detected a change of *API*, not of behaviour. Patched; the control correctly
  survives again; observed effects rose 67 → 84.
- **`open ticket` snapshots the oracle's scratch tree into the ticket workspace**
  — 706 of 801 tracked files on HP-04's first workspace — and `close ticket`
  would promote it into the model. Filed as HP-04-DF-04.

**Recorded because it is unflattering and instructive:** HP-04's first
kill-table harness reported **10 of 10 killed on every class, including the
negative control**, because it was comparing reports carrying differently-named
temp directories. Its second reported the ordering control killed for the
`Path.open` reason above. Both wrong harnesses are kept in the ticket narrative
alongside the real table — **a reader of a 10-of-10 should know how easily one
is produced by accident.**

**Determinism, the one thing that did move cleanly:** the epic tip reported
20 / 19 / 19 gaps across three runs of an identical corpus; HP-04 reports
20 / 20 / 20, with the **whole report** byte-identical rather than merely the
count. MF026-R4-F-01 is closed on measurement.

**HP-05 — one cell moved, and two of the owner's own claims were corrected.**

`M04` (a durable running total goes stale) went SURVIVED / SURVIVED /
**KILLED** / KILLED across `map-none` / `map-silent` / `map-checking` / suite.
One corpus, three mappings differing by **one line of TOML**, and
`map-checking` is what codegen now writes by default. `map-none` was included
purely as a reproduction control — a seam that shifted the baseline would make
the checking column unreadable — and it reproduces HP-03's whole-view column in
all ten rows.

**Two corrections, both of claims the owner made in a ticket brief:**

- **`M05` was never suite-only.** The brief and the ticket objective both said
  it was. HP-03's committed table already recorded it killed by the whole-view
  corpus, and the reason is structural: the model's CLOSE element carries the
  total in its third slot, so the ordinary projected-state comparison already
  sees a zeroed one. Only COMMIT drops its total, and only M04 lives there.
  **One mutant moved, not two.**
- **The "30% of the instrument's yield" figure does not reproduce as a
  proportion.** 3 of 10 on ex4; 1 of 6 under the checking mapping here, 1 of 10
  overall. The **direction** has now replicated three times on three fixtures;
  the **magnitude** is fixture-dependent. It was quoted repeatedly as a property
  of the mechanism and it is not one.

**Where the generator now stands against the bar:** suite **10 of 10**;
whole-view corpus under the checking mapping **6 of 10**; whole-view plus HP-03's
negative corpus **9 of 10**, up from 8. Still behind a suite written in an
afternoon, by one mutant instead of two. The remaining survivor is **M07 — the
catalogue's declared positive control**, which is supposed to die on every
instrument and does not, because it is seeded inside `reserve()` and `Reserve`
contributes zero executable cases. **While that control is red, the
`wrong_value` row is not citeable as a clean kill measurement.**

Zero model surface: TLC enumerates 3,678,218 states / 118,573 distinct before
and after, argued rather than asserted.

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
