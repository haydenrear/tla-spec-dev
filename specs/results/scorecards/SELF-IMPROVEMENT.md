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
- **And only across an unchanged instrument.** This is not a fourth bullet of
  advice; it is the thing this file got wrong. See below.

### Do not compare two rows out of this file by hand (PA-05, 2026-08-05)

Every number here was measured on an instrument, and this project has now twice
read one forward across a repair that changed what it measured. `INSTRUMENT-LOG.toml`
beside this file records the instrument changes, the corrections that sit
**beside** sealed cards rather than editing them, and the ledger claims that are
not scorecard rows. Read a history with the changes marked between the rows:

```
python3 examples/validation/scorecards/score_tools.py history --example ab_quota_ledger
python3 examples/validation/scorecards/score_tools.py audit
```

The rendering for `ab_quota_ledger` is committed as `HISTORY-ab_quota_ledger.md`.
The reading rules are `references/eval_scorecard.md` § **Reading history**
(R-H1..R-H4) and each one is executed by `audit`, because a reading rule nothing
executes drifts exactly like the numbers it is about.

**Four things in this file are now marked, and none of them is edited:**

- the HP-06 rows and the EVAL-RERUN rows are in **different eras** —
  `EVAL-STABLE` sits between them, and `EVAL-SUPPRESS` post-dates **both**, so
  every rerun number came from a driver repaired afterwards;
- **`guard relaxation 0 → 3 of 3` is a real mechanism gain**, and the reason is
  structural rather than lucky: both ends were measured *in one run* on two
  instruments (`delta_basis = "within_run"`), not at two points in time;
- **`D1 = 3` is an attribution correction, not a gain.** HP-06 recorded it as a
  treatment effect; on the repaired instrument it is on both arms. Nothing about
  bug detection improved between the rounds;
- **`controls green on both arms` is known-wrong for arm B**, recorded beside the
  two arm-B cards that were judged against a packet that said otherwise.

**Two findings were filed while building the view. One was right, one was wrong,
and both are on the record:**

- **`PA-05-DF-01` — upheld.** The epic document's D5 baseline had the
  attribution inverted: the best-ever 4 went to the *treatment* under the rerun,
  not the control. The owner has corrected it, and the D1 row of the same table
  with it.
- **`PA-05-DF-02` — central claim REFUTED, general hazard DISCHARGED.** PA-05
  said the 56-of-56 baseline was contaminated because `EVAL-SUPPRESS`'s one
  flipped cell sits inside the comparable set. **It does not.** "Strictly
  comparable" is the rerun's own rule — *the same diff on both arms* — which
  excludes M07 (arm B's seeding is a declared substitute), M08 and M10 (seeded
  by addition): 8 rows × 7 instruments = **56**, and M07 was never in the
  denominator. Of all 11 × 7 = 77 cells of the repaired tables, exactly **two**
  differ between the arms and **both are M07**. The owner refuted it from the
  sealed raw data; PA-05 reproduced the refutation. The *general* hazard it
  raised — pre-`EVAL-SUPPRESS` baselines not re-affirmed — was real when filed,
  and PA-03's re-derivation has now discharged it: **zero cells moved on either
  arm** over the 77 shared cells.

  The wrong finding is kept as `status = "refuted"` in the log rather than
  deleted, with `refuted_by` and its `filed_as` intact. **A finding that turned
  out to be wrong is evidence about this epic's own review process**, and what
  caught it was a person reading raw JSON — not the suite, and not a check.
  `audit` was right that the claim straddled an unreaffirmed change and *cannot*
  tell whether the change touched the cells the claim is about. **A straddle is
  a prompt to go and look, never a finding on its own.**

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
| ab_quota_ledger | **B (treatment)** | 1 blind | 3 | 2 | **4** | 3 | 3 | **15**/20 | 2026-08-04 |
| ab_quota_ledger | **B (treatment)** | 2 blind | 3 | 2 | **4** | 3 | 3 | **15**/20 | 2026-08-04 |
| ab_quota_ledger | **A (control)** | 1 blind | 3 | 2 | 2 | 2 | 4 | **13**/20 | 2026-08-04 |
| ab_quota_ledger | **A (control)** | 2 blind | 2 | 2 | 2 | 2 | 3 | **11**/20 | 2026-08-04 |
| ab_quota_ledger | A (control) — **EVAL-RERUN** | 1 blind | 3 | 2 | 2 | 2 | 3 | **12**/20 | 2026-08-04 |
| ab_quota_ledger | A (control) — **EVAL-RERUN** | 2 blind | 3 | 2 | 2 | 2 | 2 | **11**/20 | 2026-08-04 |
| ab_quota_ledger | **B (treatment)** — **EVAL-RERUN** | 1 blind | 3 | 2 | **4** | 3 | **4** | **16**/20 | 2026-08-04 |
| ab_quota_ledger | **B (treatment)** — **EVAL-RERUN** | 2 blind | 3 | 2 | **4** | 2 | 3 | **14**/20 | 2026-08-04 |

**The EVAL-RERUN rows are a DIFFERENT PAIR OF ARTIFACTS**, produced by
re-dispatching the same two prompt files verbatim to fresh agents after the
instrument was repaired. They are comparable to the HP-06 rows as *arms of the
same experiment on the same fixture*, not as re-scorings of the same code.

**Pre-treatment reading.** D1 = 0 because no model-derived case exists yet — the
model ships and TLC is green, but the corpus is HP-03's work; the hand-written
suite's 10-of-10 is D4 and mechanical-block material, not D1. D3 = 1 because the
domain imports `pathlib` and writes the ledger file itself, so there is no port
and no swap. **Both floors are the intended ones**: they are exactly the two
numbers the epic's goals target, and a control that already scored well would
have left the experiment nothing to measure.

**HP-06 closed the epic. Zero contested dimensions; maximum spread across ten
independent scores is 1. Unblinding key and the two ways the blinding leaked:
`hexagonal-prompting/UNBLINDING.md`.**

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
  > **OVERTURNED IN PART BY EVAL-RERUN (2026-08-04).** The 10 of 10 is partly an
  > artifact of what was seeded: the replacement negative control **N01 survives
  > the hand-written suite too**. On the repaired instrument the union of the
  > generated instruments **ties** the suite, 10 of 11, on both arms and on a
  > fresh blind catalogue — though no *single* generated instrument gets past 7
  > against the suite's 10, so the tie is an aggregate effect. Quote the bar with
  > the N01 clause and the single-instrument number, or not at all.
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

**HP-06 — the epic's own measurement, and it is mixed on purpose.**

**Two of the three goals are `met` and the third is `missed`, and the two `met`
verdicts each carry a caveat that must never be separated from them.**

`GOAL-hexagonal-in-fact`: **`met`. D3 = 4 from both judges on the treatment arm,
against 2 from both on the control.** This is the first 4 the project has ever
recorded on any dimension other than D5, and the first time D3 has passed 3. Both
judges earned it by RUNNING the artifact's real-adapter/fake parity suite rather
than believing its notes, and both checked specifically for the hole HP-02's
pilot found in an earlier draft of the same prompt (`scenario(fake) ==
scenario(real)`, which cannot fail for any fault in the rules). HP-02 added one
sentence to close it and deliberately did not re-measure; **this was that
sentence's first measurement and it held.**

> **SUPERSEDED BY EVAL-RERUN (2026-08-04): D1 = 3 from both judges on BOTH
> arms, under a positive control that is green on the faithfully seeded arm.
> The verdict is unchanged; the caveat below is not.**

`GOAL-catch-bugs`: **`met`. D1 = 3 from both judges on the treatment arm** —
against a baseline where nothing reached 3 on either judge on any example —
carried entirely by the negative corpus, whose controls are green. Guard
relaxation **3 of 3** on the seeded catalogue and **1 of 1** on a fresh,
independently authored one, against 0 of 3 under every other generated
instrument.

`GOAL-simpler-same-behavior`: **`missed`. D2 = 2 from all four judges on both
arms.** The target was not moved. It was missed for a reason nobody predicted:
**neither arm made a simplification and measured one**, because both implemented
the same specification from scratch. The owner's amendment proposed reading the
arm pair as the before/after, that reading was supplied to every judge, and **no
judge accepted it** — two independent artifacts are a comparison, not a
refactoring. **D2 as written cannot be scored above 2 by an A/B at all**
(HP-06-DF-05). That is a finding about the card, not about the arms.

**DID D5 HOLD? YES — and it did not move in the direction that would have
mattered.** D1 rose from a ceiling of 2 to 3 while D5 stayed at 3–4, and the
higher D5 (a 4) went to the CONTROL arm, not the treatment. A rise in D1 bought
by a fall in D5 would be the toolchain learning to overclaim; that did not
happen. Sealed N03 predicted D5 would not separate and it passed.

**DID ANY SCORE MOVE WITHOUT AN ARTIFACT MOVING? NO — the mechanical block and
the judgement AGREE, and where they disagreed the block was wrong.** D3 = 4 rests
on a `Protocol` port, a real adapter, a working fake and a parity suite that all
exist in the tree and were executed by both judges. Where measurement and
judgement diverged it was the *measurement* that failed: the block's `branches`
figure said the treatment arm was simpler, and an adversarial pass decomposed the
entire delta into behavior the treatment arm does not implement plus one
predicate written on the other side of a `for` — **on matched behavior the two
trees have identical decision counts.** Its `state_writers` figure is a constant
2 across all three trees and discriminates nothing.

**FINDINGS BY CHANNEL — 0 : 17 : 13.** Suite re-run **zero** (1130 + 143 tests
and 56 shared-suite assertions, all green). Fresh adversarial attack **17**, six
of which falsified a claim HP-06 had already written down. Blind author **13**,
and once again its **REJECTED** section was the most valuable thing produced.
Sealed N06 passes for the third round running. **Say it plainly, as HP-01 asked:
the suite has stopped being informative.**

**FOUR OF THIRTEEN SEALED PREDICTIONS WERE WRONG, AND THREE OF THE FOUR ARE
NEGATIVES.** P05 (the positive control dies everywhere) — **FAIL**, it survives
every generated instrument on the control arm, for the same reason HP-05 recorded
one ticket earlier. P03 (the mapping reproduces its 30%) — **FAIL**; the
direction now replicates five times on five fixtures and the magnitude has failed
to reproduce four times. N01 (the treatment's descriptor is not lower) — **FAIL**;
it is lower on lines, and HP-02's pilot had recorded N01 as confirmed against an
EARLIER DRAFT of the prompt. N02 (ordering stays zero on every corpus) — **FAIL**,
reproducing HP-03's retraction on two arms.

**THE UNFLATTERING HALF, and there is a lot of it.**

- **The hand-written suite still beats the generator, and a catalogue nobody
  tuned beats them both down.** Seeded catalogue: suite 10 of 10, generated
  corpora 9 of 10, and the one survivor is the positive control. **Fresh
  independently authored catalogue: corpora 8 of 13, suite 9 of 13, and FOUR
  whole classes invisible to every instrument including the suite.** A catalogue
  written by the author of the mechanisms flatters both instruments by roughly a
  quarter. **On this fixture the generated corpus is still worse than a suite a
  competent engineer writes in an afternoon**, and that sentence is now two
  epics old.
- **The prompt produced the structure and the structure caught nothing.** Every
  per-mutant verdict is identical between the arms on **49 of 49 comparable
  cells**.
  > **REPLICATED AND WIDENED BY EVAL-RERUN**, on a fresh pair of artifacts and a
  > catalogue that seeds all ten mutants on both arms rather than eight:
  > **56 of 56 strictly comparable cells identical.** On an independently
  > authored 15-mutant catalogue the only two differing cells are the two rows
  > its author declared non-parallel. A port did not detect one additional fault, and the treatment arm's
  own 41 tests appear nowhere in any kill table — both judges said so and both
  capped D1 for it.
- **The guard-relaxation zero is not what the sealed catalogue says it is.** This
  model spells refusals out as first-class actions, so the whole-view corpus DOES
  contain refusal cases — 39,688 of 43,128 — and HP-06's own oracle skips all of
  them. The 3-of-3 under the negative corpus survives adversarial tracing; the
  framing of the zeros beside it does not.
- **The one measured edge the epic has is a patch over a model that does not
  refine its own specification.** The blind author found that the model's COMMIT
  record has three fields where the feature's has four: **R2's running-total
  clause is absent from the state machine entirely**, and the manifest's own port
  description describes a line the model never constructs. That is why the
  durable-content mutant needs the content mapping's hand-written sentence.
- **The port has a cost nobody predicted.** A fault in the treatment arm's
  in-memory adapter survives every instrument including the hand-written suite.
  The control arm has no counterpart. **The structure removes places for some
  faults to live and creates a region no shared oracle reaches** — the fake that
  earned the D3 = 4 is verified by nothing outside that arm's own tests.
- **The two arms differ in UNMUTATED code on crash consistency**, and nothing in
  this fixture can see it. The control appends then updates memory and R2 holds
  under a failing write; the treatment updates then appends and R2 breaks. The
  treatment arm's whole architecture is an injected port, which makes it the
  easier arm to test for exactly this, and it does not.
- **HP-06 corrected six of its own written claims** after an adversarial pass,
  and filed twelve `HP-06-DF-*`. **None was fixed.**
- **Blinding leaked**, on the control arm, and the judge who found it disclosed it
  unprompted. It was not re-judged, because discarding cards after seeing scores
  is the thing this ticket may not do.

**And one thing to carry into the next round before anything else.** Fixing the
red positive control — repairing `Reserve` argument recovery — is the obvious
next move, and HP-06-DF-11 says it will turn a **second** control red, because
the oracle re-derives a reservation id the model does not allocate that way. That
is the order of work, not an objection to doing it.

> **DONE, AND HP-06-DF-11 FIRED EXACTLY AS PREDICTED — with a broader cause than
> it reasoned about.** Recovery is 4,028 of 4,028 and arm A's M07 is green. The
> id problem was not repaired but *declared and counted*: 294 of 588 `Reserve`
> cases are skipped. EVAL-RERUN then found that DF-11's own explanation covers
> only **28 of the 294** — for the other 266 the id the API would allocate is
> outside the model's `ResIds` entirely. The suggested fix (installing the id
> counter from the case's own `r`) was rejected on principle without running it,
> because it would configure the program to produce the id the oracle compares.

## POST-EVALUATION CORRECTION (2026-08-04) — read before citing any number above

The eval instrument was repaired **after** HP-06 measured, and the repair
invalidates part of what HP-06 recorded. Both facts are kept: the sealed
scorecards are not edited, and this section says which of their numbers no longer
describe the instrument.

**The red positive control was a missing regex.** `Reserve(t, a, r)` writes
`amt' = [amt EXCEPT ![r] = a]`. All four parameter-recovery mechanisms looked at
*indices* and *whole variables*; **none looked at the value written into a
function entry**. So the amount was `UNRECOVERABLE`, **0 of 588** positive
`Reserve` cases carried an argument, every one was skipped, and M07 — seeded
inside `reserve` — could not be reached by anything. A fifth mechanism
(`except-value`, ordered last so it can only reclassify an already-unrecoverable
parameter) took recovery to **4,028 of 4,028**.

Note what the repair refused to do: it rejects an RHS that merely *mentions* the
parameter (`![t] = @ - a`), because matching that would have read `available'[t]`
and called it the amount — and every downstream comparison would then have agreed
with a number the oracle invented.

**WE HAD NO VALID NEGATIVE CONTROL FOR TWO ROUNDS.** M09 reverses a *sequence*,
and this model's ledger **is** a sequence — projected as a tuple, compared
positionally. It was never negative here. It is retired as a control (it still
runs, still scored in the `ordering` row) and replaced by **N01**, seeded against
a set-typed collection, surviving all seven instruments, with a **reality
witness** run against both trees so that "survived" is not silently "equivalent
mutant".

**The finding that most changes how to read the record: N01 survives the
hand-written suite too.** The suite that scores **10 of 10** has no assertion on
the order of two or more live ids. So the standing bar this whole epic was
measured against — *"the generator is still worse than a suite written in an
afternoon"* — rests on a catalogue containing **no mutant that suite could
miss**. The 10-of-10 was partly an artifact of what was seeded. Quote it with
that clause or not at all.

**Reach is smaller than the record claims, and is now printed beside the
verdict rather than inferable by nobody:**

- `corpus-whole` executes **3,734 of 43,128** cases (**8.7%**). The other 91% is
  39,100 refusal edges carrying no arguments — nothing to call.
- **Half of `Reserve` is structurally unreachable**: 294 of 588 cases fail on
  *unmutated* code, because the model chooses an id where the API allocates one.
  HP-06-DF-11 predicted this and reasoned about an id outside the declared set;
  the common case is simpler and broader.
- HP-06-DF-11's own suggested fix was **rejected on principle without running
  it**: installing the id counter from the case's own `r` would configure the
  program to produce the id the oracle then compares — a tautology one level
  below MF-028.

**Numbers above that no longer describe the instrument:** arm A's `wrong_value`
row, and the "union of every generated instrument: 9 of 10, survivor M07" line.
Both describe an instrument that executed **zero** `Reserve` cases. The repaired
instrument decides M07 on 5 of 7 instruments, with the other two recorded as
declared limitations carrying verified witnesses rather than as failures.

**This is why the epic does not close on HP-06's run.** The instrument changed
after the measurement; the measurement has to be taken again on the repaired one,
and whatever it says is what gets recorded.

## EVAL-RERUN — the re-measurement the correction above demanded (2026-08-04)

**Two goals `met`, one `missed` — the same verdicts HP-06 reached, on an
instrument whose controls now work, from a different pair of artifacts.** The
two `met` verdicts each carry a caveat that must never be separated from them,
and the caveats are not the ones HP-06 carried.

Full record: `specs/results/scorecards/hexagonal-prompting-rerun/`.

| goal | baseline | measured | target | verdict |
|---|---|---|---|---|
| `GOAL-catch-bugs` | D1 = 2/2/2/1/0; nothing reached 3 on either judge on any example; guard relaxation 0 of 3 and 0 of 4 | **D1 = 3 from both judges on BOTH arms.** Guard relaxation **3 of 3 under `corpus-neg`** on the seeded catalogue on both arms and **1 of 1** on a fresh blind one, against 0 under every other generated instrument | D1 ≥ 3 from both judges on some example, and guard-relaxation kills > 0 on both catalogues | **`met`** |
| `GOAL-simpler-same-behavior` | highest D2 is 3, both judges withholding 4 for the same reason | **D2 = 2 from all four judges on both arms.** Arm A 122 lines / 10 branches / 1 module; arm B 129 / 11 / 4 | an arm-B artifact scores D2 = 4 from both judges | **`missed`** |
| `GOAL-hexagonal-in-fact` | D3 = 1/1–2/3/1/0–1; one 3, never a 4 | **arm B D3 = 4 from both judges**, both earned by executing the swap; arm A 2 from both | prompt arm ≥ 3 from both judges on the majority, with at least one 4 | **`met`** |

**No target was edited.**

### THE POSITIVE CONTROL IS FIXED — on the arm where it could be seeded faithfully

`P05` was HP-06's most consequential failure: M07 survived all six generated
instruments, because **0 of 588** positive `Reserve` cases carried an argument.
On the repaired generator, recovery is **4,028 of 4,028**, **294 accepted
`Reserve` cases execute**, and arm A's M07 — byte-for-byte the sealed
catalogue's seeding — **has no `SURVIVED` cell anywhere.** `P05` flips **FAIL →
PASS**.

**And an adversarial pass showed the arm-B half of that row is worth nothing.**
It built `corpus-noreserve` — the whole-view corpus with every `Reserve` case
deleted, reproducing HP-06's regression exactly — and ran it: arm A's control
correctly went **SURVIVED/red**; **arm B's stayed KILLED.** Arm B's declared
broader-reach substitute inflates a computation that runs on every read, so it is
detectable through `CloseTenant` on a state with no live reservation at all.
**"Both controls are green on both arms" is true and means two different things.**

### THE `NOT_DECIDABLE` MECHANISM IS AN UNAUDITED SUPPRESSION KEY

The shipped driver decides `NOT_DECIDABLE` **before** consulting the mutated run
and never checks whether the cell it suppresses would have been `KILLED`. Proved
twice on this round's own data: copying one arm's limitation onto the other turns
a **demonstrated kill** into `NOT_DECIDABLE` with `verified: true`, `green:
true`, exit 0 and no trace; and a witness naming an action **that appears nowhere
in the model** also "verifies", erasing two genuine kills and collapsing a class
denominator to `0 of 0`. `scripts/kill_test.py`'s 19 `SUPPRESSION_KEYS` do not
include it and `run_controls.py` never invokes that scan.

**This applies to the sealed reference run in `examples/validation/ab/eval/results/`
as much as to this one.** Filed as EVAL-RERUN-DF-02, not fixed.

### THE 10-OF-10 BAR, RE-DERIVED RATHER THAN INHERITED

| | arm A | arm B |
|---|---|---|
| hand-written suite | **10 of 11** | **10 of 11** |
| union of six generated instruments | **10 of 11** | **10 of 11** |
| best SINGLE generated instrument | 7 | 7 |
| fresh blind catalogue: suite / union | **11 of 15 / 11 of 15** | **10 of 15 / 10 of 15** |

**The corpora now tie the suite** — on the seeded catalogue and on a catalogue
nobody tuned. Three clauses travel with that and none may be dropped:

1. **N01 survives the hand-written suite too.** The suite asserts
   `outstanding_ids() == ["r1"]` and compares a book against itself across a
   rejection. **The 10-of-10 that set the bar rested on a catalogue containing no
   mutant that suite could miss**, and any citation of "the generator is worse
   than a suite written in an afternoon" now needs that clause.
2. **The tie is the FORBIDDEN AGGREGATE.** Delete N01 and it is still 10 to 10 —
   so the tie is produced by unioning six instruments, five of which are not
   independent, and **no single generated instrument gets past 7 against the
   suite's 10.** Instrument for instrument the suite still wins comfortably.
3. **A catalogue written by the mechanisms' author still flatters both
   instruments by roughly a quarter** (10 of 11 against 11 of 15 / 10 of 15).

### REACH, PRINTED BESIDE EVERY KILL

`corpus-whole` executes **3,734 of 43,128 (8.66%)** — CloseTenant 1,872, Commit
784, Release 784, Reserve 294 — identical on both arms. **39,100 refusal edges
carry no arguments.** `corpus-neg` executes 94 of 118 and **0 accepting
`Reserve`**. The slices execute 320 of 2,438 and 10 of 56.

**And the round's own explanation of the `Reserve` skips was wrong for 266 of
294.** Only 28 are "a case naming a different id"; for the other 266 the id the
API would allocate is **outside the model's `ResIds` entirely**, so no case could
ever have been expressible. **"Exactly half" is a coincidence of `|ResIds| = 2`,
not a property of the refinement.** A further **252 executed cases (6.7%) run
from before-states the API can never reach and are not counted at all.**

### THE PROMPT PRODUCED THE STRUCTURE AND THE STRUCTURE CAUGHT NOTHING — again

**All 56 strictly comparable per-mutant cells are identical between the arms**
(the loose count of 76 was corrected in place; three of eleven rows are not the
same diff). On the fresh blind catalogue the two cells that differ are **exactly
the two rows its author declared non-parallel**. Where the mutants are the same,
the arms are identical; where the arms differ, the catalogue differs.

**And the D3 = 4 still cannot be attributed to hexagonality.** 16 unique prompt
lines to 105 — **6.6x**, recomputed on the shipped files. Two rounds have now
reached D3 = 4 without once testing "hexagonal" against "longer and more
specific".

### N01 THE PREDICTION FLIPPED FROM THE SAME PROMPT TEXT

HP-06 measured its treatment arm at **123 production lines against 147** and
scored sealed prediction N01 **FAIL**. This round measures **129 against 122** —
the other way — and scores it **PASS**. Same two files, same feature, same
rubric, four different agents. **The descriptor delta between one pair of
artifacts is noise at this scale and must not be quoted in either direction.**
The judged half has now held twice: D2 flat at 2 across eight independent judges.

### D5 SEPARATED, AND THE SEALED FILE SAYS TO SUSPECT THE JUDGES FIRST

N03 flips **PASS → FAIL**: arm A 3 / 2, arm B 4 / 3. The instructed first
explanation — the judges guessed the arm — does not fit. Both arm-B judges
declined to infer the arm and recorded treating polish as grounds for suspicion.
The separation is driven by the **control** arm being marked DOWN on executed
evidence: two judges independently instrumented its flagship 400-step randomized
sweep and found it accepts about **1 reserve, 1 commit, 0–1 releases and 3
closes** before every tenant closes, so its own anti-degeneracy guard passes on
the degenerate run it was written to prevent. Arm B's 4 was earned by a judge
reproducing all four of its self-declared limits, including breaking R2 with an
injected raising `Journal`; the judge who gave 3 instead **falsified** one of its
claims (the real adapter and the fake are not contract-equivalent).

**D5 separated because one artifact certified something false about itself and
the other did not, and both were checked by running them.**

### FINDINGS BY CHANNEL — 0 : 15 : 19, and the first counter-example in three rounds

Suite re-run **0** (986 repo tests, 28 + 28 shared, 32 + 53 the arms' own, all
green). Fresh adversarial attack **15**, three SEVERE, five of them falsifying a
claim this round had already written down. Blind catalogue author **19**, and for
the fourth round running its **REJECTED** section was the most valuable thing
produced. A fourth channel not in HP-06's ratio — the four judges, all of whom
built their own mutants rather than scoring the packet — produced **4** more.

**Sealed N06 passes for the fourth round running. And for the first time it has a
counter-example that should be recorded as loudly as the zero:** the hand-written
suite **as a kill-table instrument** caught this round's first defect
(EVAL-RERUN-DF-01, a stale module reference that made all eleven mutants execute
against pristine code and report SURVIVED). Six generated instruments missed it.
A green positive control missed it. **The disagreement between the hand-written
column and the generated columns caught it.**

### SIX OF THIS ROUND'S OWN CLAIMS WERE FALSE AND ARE CORRECTED IN PLACE

The controls headline, the witness-verification claim, the `Reserve` skip cause,
the "76 comparable cells" denominator, the attribution of the bar's
non-reproduction to N01, and the determinism provenance. Each is marked in
`hexagonal-prompting-rerun/GOAL-catch-bugs/README.md` and attributed to the
channel that broke it. **Four `EVAL-RERUN-DF-*` are filed and none is fixed.**

### THE OTHER UNFLATTERING HALF

- **The answer key leaks into files blind roles are ALLOWED to read.**
  `QuotaLedger.tla`'s header names six of the ten seeded mutants and where they
  are seeded; `spec_manifest.yaml` describes one verbatim and quotes prior
  scores. **Two of the blind author's thirty mutants are not independent
  evidence.**
- **The model still does not refine its own specification**, found again
  independently: the COMMIT record has three fields where the feature's has four,
  `unknown_tenant` is in the reason vocabulary and no action can produce it,
  `RejectionIsInert` does not check inertness, and the model cannot express a
  negative amount.
- **The two implementations differ in exactly one observable across 3,600
  measured slots** — whether `commit`/`release` return the reservation id. The
  prompt moved the shape enormously and the behavior by one ambiguous field.
- **The port's cost replicated and grew.** A judge found the real adapter and the
  fake are not contract-equivalent, falsifying a claim the artifact makes about
  itself; the blind author found a genuine defect living entirely inside the fake
  and declined to seed it because the control arm has no counterpart.
- **The one measurable consequence of the architectural difference is still not
  measured**: the arms order the durable write against the memory update
  oppositely — in the opposite directions from HP-06's pair — and nothing in the
  fixture can price it.

### CAN THE INSTRUMENT BE TRUSTED NOW? PARTLY, AND ITS REACH IS SMALLER THAN THE RECORD CLAIMS

What is now trustworthy and was not: the **positive control on a faithful
seeding**, **parameter recovery**, **determinism** (independently reproduced from
regenerated corpora on both arms, all seven instruments), **kill attribution**
(every retained failure string is an `AssertionError` naming the mutant's own
semantic), and **the negative control**, which now has a reality witness.

What is not: **any cell scoped by a declared limitation**, because the
suppression is unaudited and demonstrably able to erase a kill; **arm B's
positive control**, which does not detect its own failure mode; and **any
statement about what the whole-view corpus "cannot see"**, because 91.3% of it
never executes and the reason it does not was mis-stated for 266 of 294 cases.

**"Its reach is smaller than the record claims" remains the true answer.** What
changed is that the reach is now *printed* — per instrument, per action, per skip
rule — instead of being inferable by nobody.

## FINAL CORRECTION (2026-08-05) — the controls were the part that was lying

The eval re-run found three severe defects, **all three in the controls** — the
part whose entire job is to say when the rest of the instrument is lying. Three
rounds shipped before anything caught them, and what caught them was the
**adversarial channel**, not the suite and not a green control.

**A declaration could erase a demonstrated kill.** `run_controls.py` computed
`NOT_DECIDABLE` *before* the mutated run was consulted, so a declared limitation
converted a cell that the instrument had actually KILLED — reporting
`verified: true`, `green: true`, exit 0. Nothing audited it: the catalogue
promised its suppression keys were "scanned for and reported loudly", and that
promise was **false for the one mechanism that could hide a cell**. The mutated
run now decides first; a limitation may only convert a SURVIVED cell; over a kill
it is reported `contradicted_by_evidence` and the run exits nonzero.

**A limitation could verify against nothing.** `.get(key, 0)` made a *missing*
count and a *measured zero* the same number. Every witness now carries a
`witness_basis`, and an action no instrument ever accounted for verifies nothing.

**Exactly one cell changed** when this round's data went back through the
repaired driver: arm B's `M07 / corpus-slice-led`, `NOT_DECIDABLE → SURVIVED`,
its control green → **red**, exit 0 → 1. **No `NOT_DECIDABLE` became a `KILLED`
anywhere** — the erasure is real and reproducible on demand, but it did not fire
on this round's data or on the sealed reference run. Every suppressed cell was a
genuine survival.

**One sealed number is therefore known-wrong: EVAL-RERUN's "controls green on
both arms" is false for arm B.** Under the repaired driver arm B's positive
control is correctly red on its own catalogue. `GOAL-catch-bugs` is untouched by
this — its `met` verdict is carried by `corpus-neg`'s guard-relaxation result,
whose controls are green and independently reproduced.

**The honest closing verdict, in the instrument's own words:** trust the number,
cite the control that backs it, and keep the adversarial channel. **It is now
honest about what it did not decide; it is not yet an instrument that finds its
own defects.** The strongest new check is a *consistency* check — it catches a
limitation the run's own other instruments contradict — and it would not have
caught the erasure on data where nothing else disagreed.

## READ THIS BEFORE COMPARING ANY D1, D4 OR D5 ROW ACROSS EPICS

**Added at the close of `ports-as-adapters`, 2026-08-05. Owner-verified against
both sealed card sets. Source: `PA-06-DF-06`, carried as
[issue #145](https://github.com/haydenrear/tla-spec-dev/issues/145).**

This file exists so that the **delta** is the measurement. A dimension that moves
on unchanged input cannot carry a delta, and three of the five now demonstrably do.

PA-06 re-scored arms A and B as **byte-identical trees** to the ones EVAL-RERUN
judged. **Four dimension-points moved anyway**: arm A D4 2/2 → 4/4 and D5 3/2 →
4/4; arm B D4 3/2 → 4/4 and D5 4/3 → 4/4; D1 3/3 → 4/3 on both.
**D2 and D3 moved zero points on either arm.**

The mechanism is identified and **it is not the rubric**: both PA-06 judges
recorded independently that they seeded and ran their own faults rather than
scoring the evidence packet, and D4 anchor 4 can only be awarded by a judge who
executes one. The card's top anchors track **judging practice**, which nothing
mandates and nothing records.

So, when reading every table in this file:

- **A D1, D4 or D5 movement of ≤ 2 points per judge across rounds is within
  demonstrated noise.** Name what the judges did, or do not call it improvement.
- **D2 and D3 have held still on unchanged input.** They are the dimensions about
  the artifact's shape rather than about what the judge did, and they are where a
  cross-epic claim is safest. It is why `ports-as-adapters` rests its headline on D3.
- **"Zero contested" does not mean stable.** It measures two same-family judges
  agreeing *within* a round. Across-round stability was never measured until now,
  and the first time it was measured, it failed.

This is item three on the "evidence we are fooling ourselves" list below, and it
happened. See `references/eval_scorecard.md` § R-H5.

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

---

# PA-06 — ports-as-adapters, the evaluation (2026-08-05)

Full record: `specs/results/scorecards/ports-as-adapters/RESULTS.md`, with
`PREDICTIONS-SCORED.md`, `UNBLINDING.md`, `DETERMINISM.md` and six judged cards
beside it. **Three arms this time**, and the third is the point.

**READ THE ERA BOUNDARY BEFORE COMPARING ANY ROW BELOW WITH ANY ROW ABOVE.**
Between EVAL-RERUN and this round the instrument changed twice —
`PA-03-corpus-port` added an eighth column and `PA-04-port-swap-columns` added
two more *and modified the adapter-execution path the original seven run
through* — the rubric gained R-H1..R-H4 at PA-05, and the judging practice
changed (see "the two dimensions that moved"). R-H1: name the change or do not
compare. It is named.

## The goals

| goal | baseline | measured | target | verdict |
|---|---|---|---|---|
| `GOAL-port-reach` **clause 1** | a fault in the treatment arm's in-memory adapter SURVIVED EVERY INSTRUMENT (`BA-B14`; the plan cites `HP-06-DF-10`, which is a different finding — `PA-01-DF-01`) | `PA-M12`, seeded inside a **fake** adapter, is **KILLED on `corpus-port-swap:fake`** and SURVIVED on the other three corpus columns and `suite-real`. Reproduced at this tip, 0 cells moved from PA-04's sealed run | the same adapter-internal fault dies on at least one generated instrument | **`met`** |
| `GOAL-port-reach` **clause 2** | one positive control already red at dispatch | **`M07` is RED on three columns of ALL THREE ARMS and `PA-M14` on four columns of the ported reference**, each with `witness_ran_accepting: 294`. `N01` is green everywhere | *"and no positive control is red"* | **`missed`** |
| `GOAL-cases-drive-ports` | per-mutant verdicts identical on **56 of 56** strictly comparable cells (`b3a0199`); **64 of 64** after PA-03 added a column | **64 of 64 identical on every pairing** — A vs B, A vs C, B vs C. **88 of 88** over ALL rows for A vs C. One cell diverges in the port-binding columns and it is a fault the hexagonal arm LOST | the arms DIVERGE on ≥ 1 cell, attributable to a port rather than to prompt length | **`missed`** on the metric the goal names; the attribution half is **met** and arm C is what earns it |
| `GOAL-complexity-measurable` | **no such instrument exists**; D2 = 2 from all four judges last round for that reason | the instrument runs over produced Python, exits 0 on every input, and separates all three arms on 11 figures | figures differ between arms; **no target on the number** | **`met`** |

**No target was edited. No number was re-run until it passed.** The verdicts
above are the run that happened.

**THREE THINGS BOUND THE TWO `met` VERDICTS AND MUST NEVER BE SEPARATED FROM
THEM.**

1. **Clause 1 is met on a FIXTURE, not on an arm.** Every `adapter_internal`
   mutant in this project lives on `reference_ports/`, which the sealed
   predictions declare "is not an arm" and whose mutants and code share an
   author. **No arm carries an adapter-internal fault at all.** `PA-06-DF-04`.
2. **The port machinery added no kill anything else did not already have.** No
   instrument in any 8-instrument arm table has a unique kill; `corpus-action-bound`
   — the declared pre-PA-04 world — kills exactly what `corpus-port-swap` kills on
   every arm; and **`suite-fake` strictly dominates `corpus-port-swap:fake`**,
   killing everything it kills plus `PA-M13`. The measured result is carried by a
   four-line composition point and the pre-existing hand-written suite.
   `PA-06-DF-09`.
3. **`GOAL-complexity-measurable` being met is not a claim that anything got
   simpler.** See the mechanical block.

## The scorecard

| artifact | arm | D1 | D2 | D3 | D4 | D5 | total |
|---|---|---|---|---|---|---|---|
| `T` | **B** hexagonal | 4 / 3 | 2 / 2 | **4 / 4** | 4 / 4 | 4 / 4 | 18 / 17 |
| `U` | **A** ordinary | 4 / 3 | 2 / 2 | 2 / 2 | 4 / 4 | 4 / 4 | 16 / 15 |
| `W` | **C** length-matched control | 3 / 3 | 2 / 2 | **1 / 1** | 3 / 3 | 4 / 4 | 13 / 13 |

Maximum spread over thirty independent scores: **1**. Zero contested dimensions,
third round running.

**`D1 = 4` and `D4 = 4` are the first 4s on those dimensions in this project's
history, and the ledger's own self-improvement list names D1 crossing 3 as the
thing that "has never happened".** Do not read them as a mechanism gain. Both
judges say in their own cards what earned them, and it is not an artifact: each
seeded its own faults and ran them against each author's own suite instead of
scoring the packet. See below.

## ARM C SETTLES THE PREDECESSOR'S CONFOUND, AND IT SETTLES IT FOR THE PROMPT

The predecessor's headline was D3 = 1 → 4 on the hexagonal arm, and its own
report said the win could not be attributed to "hexagonal" rather than to a
**6.6× longer prompt**. Arm C is a prompt matched to arm B in unique content —
**124 lines against 105 as actually dispatched — +18.1%, with 4 of 124
architectural terms against arm B's 44 of 105, and two of those four are paths
PA-06 itself introduced.** (The sealed `--arms` measure reports +3.8% and 0 of
109; it measures the file on disk, and PA-06 dispatched it with four additions
and did not preserve what it sent. `PA-06-DF-10`. The tolerance claim is
retracted; the conclusion is strengthened, because arm C was even longer.)

**Arm C is longer than arm B and scored D3 = 1 from both judges — below arm A,
whose prompt is a sixth of the length.** Length does not produce structure here.

And the strongest evidence is not a number. Asked what it REJECTED, arm C's
author named the seam arm B built and declined it on merit
(`ports-as-adapters/arms/arm_c/REJECTED.md:77-88`): *"introducing a second class
to wrap one method would be a layer with no second implementation behind it and
no test that needs to swap one in."* **The agent considered the port and said
no.** The variable is what the prompt says.

**What it does not settle**, per the sealed confound honoured rather than argued
away: arm C controls for LENGTH, not for SUBJECT. And because arm C came out
*longer* — by 18%, not 3.8% — the residual makes the case against length weaker
still, which is the reading the sealed file fixed in advance, before anyone could
pick it. **PA-06 also leaked the epic's name into arm C's dispatch**, in the
working directory and the forbidden list. That points against the conclusion too:
an author told the round is about ports and adapters is *more* likely to build
one, and arm C built none and wrote down why.

## THE STRUCTURE ARRIVED, AGAIN, AND CAUGHT NOTHING — AND NOW IT LOSES ONE

Third round with the same result, on a wider apparatus and a third arm.

**64 of 64 strictly comparable cells identical on every pairing.** Eight
instruments. The two arms that differ most in D3 (4 versus 1) produced
**identical verdicts on all 88 cells**, and their evidence packets are literally
byte-identical apart from one column header in the mechanical block — verified by
`diff`. Both judges found that independently and both named it as the round's
central problem: *"an apparatus that separates three materially different
artifacts by three cells out of ninety-nine is either measuring something the
artifacts do not vary in, or it is not measuring."*

**The one cell that diverges is a LOSS.** Arm B's `M09` — an ordering fault
inside its real driven adapter — is `KILLED` under `corpus-action-bound` and
`corpus-port-swap:real` and **`SURVIVED` under `corpus-port-swap:fake`**, because
swapping in arm B's own fake takes the mutated file off the executed path
entirely. Arms A and C, which have no fake, kill it on all three columns.

**AND THE NULL WAS ENTAILED, WHICH IS THE ROUND'S MOST IMPORTANT
METHODOLOGICAL RESULT.** The adversarial channel built an exhaustive
observational fingerprint — 28,561 command sequences, full projection after every
step, per arm per mutant — and measured the three arms' MUTATED trees to be
identical on **10 of 11 rows**. Two trees with the same fingerprint cannot be
told apart by any black-box instrument, so **the identity of the verdict tables
is a consequence of the re-anchoring succeeding, and this experiment can only
produce a divergence where the re-anchoring FAILS.** The rival explanation — that
the trees are too similar — is measured false. **The catalogue rule that produces
this is the RIGHT rule**, adopted at EVAL-RERUN so that "a per-arm score compares
two implementations rather than two catalogues"; it is correct for comparing
DETECTION and makes comparing VALIDATION-SHAPE impossible in the same table.
`PA-06-DF-08` is the first thing the next round has to solve.

**Arm C is what makes the one divergence attributable.** PA-04 recorded, against its own
interest, that a skeptic could call the divergence an artifact of `M09` being
re-anchored into a different file on arm B, and said a reader who rejects its
argument should score the divergence unattributed. **This reader has a third
re-anchoring PA-04 did not have** — arm C's `M09`, a genuinely different
`find`/`replace` in a third tree — and it lands on arm A's verdict. A third
independent anchoring had an even chance of producing a third answer and did not.
The variable that tracks the verdict is whether the arm has a second
implementation.

So `PA-M12` and `M09` are one finding seen from both ends: the pair **reaches** a
region a single wiring never did, and a single wiring **loses** a fault the other
holds. A table reporting only the first over-reads.

## THE CONTROLS ARE STILL THE PART THAT IS LYING, AND NOW IT IS MEASURED ON EVERY ARM

`M07` SURVIVES `corpus-port` on all three arms, and `corpus-action-bound`,
`corpus-port-swap:real` and `corpus-port-swap:fake` on all three arms — twelve
red control/instrument pairs, each having executed **294 accepting `Reserve`
cases**, so this is demonstrated insensitivity and not an execution gap.
`PA-M14` is red on all four corpus columns of the ported reference.

**Every port-scoped kill number in this epic is a FLOOR.** `PA-M12`'s kill is a
demonstrated kill and stands on its own; the `SURVIVED` cells beside it cannot be
told apart from a broken instrument.

**`PA-03-DF-03` / `PA-04-DF-01` — seed an in-region positive control — was
DECLINED, for the third time and by the ticket they were assigned to.** The
reason is the same one PA-04 gave and it applies to PA-06 more strongly: PA-01
`schedule_revision 2` permits repairing an instrument *before* a measurement and
forbids it *after* an unflattering signal, and PA-06 **is** the measurement.
There is no ordering in which the deciding ticket seeds the control before seeing
the result. It stays red, and the work is carried forward with its protocol
spelled out.

**The repair PA-01 did make works, and moved nothing.** `PA-M14`'s accept-path
property was re-anchored onto all three arms by the property rather than by the
bytes, and **HOLDS on all three** — including arm C, whose cell was `UNMEASURED`
when the prediction was sealed, and arm B, where `M07`'s own semantic is BROKEN.
Measured before/after on the control's own row: **zero of six cells moved**, and
the other ten rows' find/replace are byte-identical across the repair so no cell
of theirs could have. **`verdicts_moved = 0` is an answer that had to be measured
and was.** This is R-H3's converse for the third time: a repair can move no
number and still change what the numbers mean.

## THE MECHANICAL BLOCK DISAGREES WITH D2, AND THE DISAGREEMENT IS THE FINDING

`role=code`, implementation modules only:

```
                                     arm A   arm B   arm C
  modules                                1       4       1
  code_lines                           151     202      78
  public_surface                        20      25      11
  classes                                4       6       2
  branch_points                         10      11      10
  max_depth                              1       1       1
  declared_interfaces                    0       1       0
  internal_import_edges                  0       3       0
  branch_points_in_effectful_modules    10       1      10
```

**The produced-code figures support NO simplification claim for any arm**
(`PA-02-DF-01`, filed before this round ran and confirmed on a third arm). The
ported arm is LARGER on every size figure and FLAT on branching, worst callable
and depth. **The smallest artifact on every size figure is arm C — the control
that got no architectural guidance at all.** The one figure that separates the
designs rather than their size is where the effects sit: 1 against 10 and 10.

D2's anchors 3 and 4 both require *"a simplification was made and its effect
measured"*. **All six cards scored D2 = 2** and both judges gave the same reason:
a from-scratch implementation of one spec has no *before*, so anchor 3 is
unreachable by construction. One judge stated it as a finding about the card:
**"D2 contributed nothing to this comparison and will contribute nothing to the
next one under the same task design."**

Both judges also recorded, unprompted, that they refused to convert the
mechanical block into a D2 score, and one noted that the figure a naive reading
would reward arm C for *"is bought by folding the I/O into the domain, which is
precisely what costs it D3."*

## FINDINGS BY CHANNEL — 1 : 12 : 4 : 2, and the ratio IS the result

| channel | findings | what it cost |
|---|---|---|
| **suite re-run** | **1** | one command, already in the acceptance list |
| **fresh adversarial attack** | **12** | one agent, 94 tool calls, ~25 minutes |
| **blind judges, asked what they REJECTED** | **4** | free -- it is a section of the card |
| **blind author, asked what it REJECTED** | **2** | free -- one extra paragraph in the prompt |

**The three channels that ask an agent what it REJECTED, or tell it to attack,
produced 18 of this round's 19 findings. The suite produced 1 -- and that 1 is
the first it has produced in four rounds.**

**The alarm the ledger set fired in the good direction.** "A suite-only round
means the suite has stopped being informative" was the alarm; what happened is
the opposite. `tests/test_code_complexity.py::test_nothing_executable_reads_this_instrument`
went red against PA-06's own evidence-packet builder. **`N06` predicted zero from
the suite and FAILS.** It is filed and not fixed: repairing a check during the
measurement it watches is the forbidden act, and evading it by renaming a string
would be the six-lines-of-YAML defeat this epic exists to prevent, performed by
the ticket that exists to catch it.

**AND THE ADVERSARIAL CHANNEL IS THE REASON THIS ROUND'S HEADLINES ARE READABLE
AT ALL.** Four of its twelve findings changed the result document, and two of
them corrected numbers this ticket had already written down:

1. **The null was ENTAILED.** An exhaustive observational fingerprint -- 28,561
   command sequences, full projection after every step, per arm per mutant --
   measures the three arms' MUTATED trees to be identical on 10 of 11 rows. Two
   trees with the same fingerprint cannot be told apart by any black-box
   instrument, so **"the arms do not diverge" is a consequence of the
   re-anchoring succeeding, and the experiment can only diverge where it fails.**
   The rival explanation -- that the trees are too similar -- is measured false
   (78 vs 151 vs 202 code lines, three different representations of a held
   reservation). `PA-06-DF-08`.
2. **The repaired positive control is unobservable in one step on three of the
   four trees**, and the probe that certifies it **cannot fail** -- a no-op
   mutant reports HOLDS. `PA-01-DF-05`'s subject is that nothing ever checked a
   control against the property that makes it one; PA-01 built the check and the
   check is one-sided. `P07`'s row named this in advance as "this epic's worst
   possible own goal". `PA-06-DF-07`, severity blocking.
3. **The port machinery added no unique kill anywhere in the round**, and
   `suite-fake` strictly dominates `corpus-port-swap:fake` -- it kills everything
   that column kills plus `PA-M13`. The measured "port reach" is produced by a
   four-line composition point plus the pre-existing hand-written suite.
   `PA-06-DF-09`.
4. **The length-match headline was measured on the wrong file.** PA-06 dispatched
   arm C's prompt with four additions and did not preserve what it sent. Real
   figures: **+18.1%, outside the declared tolerance, 4 of 124 architectural hits
   rather than 0 of 109** -- two of them paths PA-06 introduced, which told the
   arm what the epic is called. `PA-06-DF-10`.

**What the channel could NOT break** is recorded too, because that is the other
half of its value: zero equivalent mutants in the arm-C catalogue (every row
observable on every arm, verified by running); `PA-M12` dies for the reason
claimed, separated from every alternative by a mirror experiment; determinism
byte-identical over three runs; and an injected harness fault is LOUD -- it turns
the whole column `CONTROL_RED` rather than reporting kills.

## AGAINST THE "EVIDENCE WE ARE FOOLING OURSELVES" LIST, ITEM BY ITEM

**"Every prediction passing."** — Did not happen. **Five of fifteen FAILED**
(`P02`, `P04`, `N03`, `N05`, `N06`), one is `SUPERSEDED` (`N08`), and three of the
five failures are NEGATIVE predictions, which is where the information is. `N03`
failed and *named the cell it asked to be named*. `N05` failed against data that
already falsified it when it was sealed.

**"Findings arriving only from the suite."** — Not this round, and for the first
time the inverse question is live: the suite produced its first finding in four
rounds. The ratio is **1 : 12 : 4 : 2** — one from the suite against eighteen
from the three channels that ask an agent what it REJECTED or tell it to attack.
It has moved off zero without inverting.

**"A score moving without an artifact moving."** — **THIS HAPPENED AND IT IS THE
ROUND'S WORST RESULT ABOUT ITSELF.** Arms A and B are byte-identical to the trees
EVAL-RERUN judged. Arm A's D4 went **2/2 → 4/4** and its D5 **3/2 → 4/4**; arm B's
D4 went **3/2 → 4/4**. Four dimension-points on arm A alone, on a tree nobody
touched. R-H1 forbids reading it as improvement and this ledger does not: the era
boundary is named above, and the mechanism is named in the judges' own cards —
**they executed mutations instead of reading the packet.** D2 and D3, the two
dimensions about the artifact's shape, did not move by a single point on either
arm. Filed as `PA-06-DF-06`.

**"A withheld case passing that its siblings failed."** — Did not arise; nothing
was repaired this round, so nothing was measured on the instrument that found it.

## WHAT WOULD COUNT AS SELF-IMPROVEMENT — SCORED AGAINST ITS OWN LIST

- **"D1 crossing 3 on any example — this has never happened."** It happened:
  D1 = 4 from one judge on arms A and B. **It is not a mechanism gain.** The
  other judge held both at 3 and gave the reason: the positive control is
  `green: false` with `deciding: []`, so the top of the scale is not reachable
  while the column's zeros are floors. Read the 4 as one judge's crediting rule
  about an artifact's own hand-written cases, not as generated cases catching
  more.
- **"D2 reaching 4."** No. All six cards are 2, and anchor 3 is now known to be
  unreachable by construction under this task design.
- **"D3 reaching 4 — never reached."** Reached again, arm B, both judges, both
  earned by *executing* a swap rather than reading one. **And arm C now says it
  is the prompt's content that produced it.**
- **"D5 holding. A rise in D1 bought by a fall in D5 is the toolchain learning to
  overclaim."** D5 = **4 from both judges on all three arms** — the flattest and
  highest honesty column this project has recorded. `N04` predicted no separation
  and PASSES. Nothing was bought at D5's expense. The uncomfortable half is that
  D5 no longer separates anything at all.

---

# FI-03 — THE FIRST TIME THIS FILE'S OWN QUESTION WAS MEASURED (2026-08-06)

Full record, with every number re-derived from the cards by a committed script:
`specs/results/scorecards/falsifiable-instruments/GOAL-scorecard-carries-a-delta/RESULT.md`.
Byte-identity of the scored trees is verified in `BYTE-IDENTITY.md` beside it,
at the git-tree-object level and per file, rather than asserted.

**The section above headed "READ THIS BEFORE COMPARING ANY D1, D4 OR D5 ROW
ACROSS EPICS" ends by pointing at `references/eval_scorecard.md` § R-H5. That
section did not exist when the pointer was written** — the caveat was
deliberately left unnumbered because `R-H` ids are what `audit` executes and it
had no check. **It exists now**, with a check, and the pointer resolves.

## The answer, in one paragraph

Three sealed, byte-identical artifacts were re-scored by two fresh blind judges
under the current card. **Against the sealed PA-06 row the worst movement is
1 dimension-point per judge on every dimension, in BOTH arms — the target is met
on that comparison. Against EVAL-RERUN, the same bytes and the same card version
one round further back, D4 moves 2 in both arms and D5 moves 2 in the version 2
arm, and the target is missed.** Both comparisons sit in the same table in this
file, so the second is not a stretch: it is the comparison a reader of this file
would make.

> **`GOAL-scorecard-carries-a-delta` is MISSED. It is missed on D4, and on D5.**

> **AND THE OTHER HALF OF THE SAME MEASUREMENT: D2 AND D3 MOVED ZERO POINTS.**
> Not "within target" — **zero**, on every one of the 60 judge-scores, across
> four independent pairs of judges, two card versions, three artifacts and two
> sealed baselines. Not one point, in either direction, in any comparison.
>
> **This is the strongest stability evidence this project has ever produced
> about anything**, and it is what makes `ports-as-adapters` resting its
> headline on D3 a safe decision rather than a lucky one: D3 = `4 / 2 / 1`
> across the three artifacts has now been produced by four independent pairs on
> byte-identical bytes, two of whom executed the adapter swap themselves and two
> of whom did not.
>
> **A reader skimming for the missed goal must not skim past this.** The card
> works. It works on the two dimensions that are about the artifact's shape, and
> it fails on the two that are about what the judge did.

## What can and cannot carry a delta, stated so it can be used

Worst movement per judge, on 60 judge-scores from two fresh judge pairs.

| dimension | vs PA-06 (30 + 30) | vs EVAL-RERUN (20 + 20) | can it carry a delta? |
|---|---|---|---|
| **D1** bug detection | worst 1, 2 of 6 moved in each arm | **worst 0, 0 of 4 in each arm** | **yes** |
| **D2** complexity | **worst 0, 0 of 6 in each arm** | **worst 0, 0 of 4 in each arm** | **yes** |
| **D3** modularity | **worst 0, 0 of 6 in each arm** | **worst 0, 0 of 4 in each arm** | **yes** |
| **D4** behavior preservation | worst 1 | **worst 2 in BOTH arms** | **NO** |
| **D5** honesty | worst 1 | **worst 2 in the v2 arm** | **NO** |

**D4 on arm A, four independent pairs of same-family blind judges,
byte-identical code: `2 / 2` → `4 / 4` → `3 / 4` → `4 / 4`.** A two-point range
with no artifact underneath it. Do not read a D4 movement in this file as a
result.

**D2 and D3 moved zero points on all 60 judge-scores** — two judge pairs, two
card versions, three artifacts, two sealed baselines, not one point in either
direction. `ports-as-adapters` rested its headline on D3 and that decision is
now vindicated by measurement rather than by argument: `4 / 2 / 1` across the
three artifacts has been produced by four independent pairs of judges, two of
whom executed the swap themselves and two of whom did not.

**D1 has joined them.** It moved zero against EVAL-RERUN in both arms, and the
two 1-point movements against PA-06 are both PA-06's pass-1 judge giving a 4
where every other judge in three rounds gave a 3. **This file's own list says
"D1 crossing 3 on any example — this has never happened"; PA-06 recorded it
happening, and it has not replicated.**

## The card changed, and the change is recorded rather than assumed

`scorecard_version 2`. The anchors are byte-unchanged and the rubric declares an
anchors-only digest for both versions that `score_tools.py check` recomputes, so
"keep the old anchors" is a machine statement. What is new is that **what the
judge DID is a required field**: `judging_practice.executed_own_faults` and
`what_was_run`. `false` is legal and is recorded as `PACKET-ONLY`; the one
consequence is that **D4 = 4 is not awardable when it says `false`**, which is
D4's own anchor text made checkable.

**One of FI-03's v1 judges wrote, in its own REJECTED section, that it had
declined to seed any fault — and awarded `D4 = 4` on all three artifacts
anyway.** Under version 2 that card is rejected by `check`. The gate is not
hypothetical and it was not invented for the ticket.

### And the practice diagnosis is confirmed rather than repeated

`PA-06-DF-06` said the movement tracks judging practice. It could not test that,
because nothing recorded the practice. FI-03 recorded it:

| round | arm A D4 | practice |
|---|---|---|
| EVAL-RERUN | `2 / 2` | unrecorded |
| PA-06 | `4 / 4` | both judges executed — disclosed in prose |
| FI-03 **v1** | `3 / 4` | both judges packet-only — disclosed in prose |
| FI-03 **v2** | `4 / 4` | both judges executed — **recorded on the card** |

**The arm whose recorded practice matches PA-06's is the arm whose numbers match
PA-06's**: 5 dimension-points of total movement against the packet-only arm's 9,
on the same artifacts, on the same day, from the same model. And **FI-03's v2
pass-2 judge reproduced PA-06's sealed pass-2 row exactly — 15 of 15
dimension-scores across all three artifacts.**

**D5 does not fit that story, and it is a separate problem.** Both v2 judges
executed their own faults and still split 3 against 4 on the same artifact, over
whether an artifact's own disclosure of a limitation counts as *a result
unflattering to the thing being scored*. **D4's instability was an unrecorded
practice and now has a mechanism; D5's is an ambiguous anchor and has none.**
Rewriting D5's anchor 4 would put a second discontinuity into the same version
bump, on a dimension that was not this ticket's subject. Not done, and named.

**The discontinuity of the version bump itself: 4 dimension-points over 30
judge-scores, worst 1 per judge**, measured by re-scoring the same three
artifacts under both versions on the same day. That is what the card's change
rule asks for, and it is the first time it has been done.

**What none of this buys.** Recording the practice explains the instability; it
does not remove it, and it cannot remove it backwards. Every movement from a
version 1 row has one end that never said what its judge did, which is why R-H5
marks all of them `readable = false` permanently. **The card becomes able to
carry a D4 delta only between two version 2 rounds, and exactly one version 2
round exists.**

### What the judges produced that nobody asked for — the ratio, again

For the fifth round running the REJECTED question outperformed everything else.
Four judges, **zero** findings from re-running any suite, and:

- a judge that would have scored `W` D4 = 4 off the packet and **ran a
  cross-aspect fault that `W`'s own eleven cases reported `11 passed` under**,
  and lowered the score — D4's anchor 4 doing exactly what it says;
- an independent replication of EVAL-RERUN's degeneracy finding: `U`'s flagship
  400-command sweep, replayed on its own seed, accepts **1 reserve, 1 commit, 0
  releases and 3 closes**, so the single COMMIT line it writes is
  `COMMIT acme 7 7` and a transposition is structurally invisible to it;
- three of four judges independently reporting that `artifact_U/EVIDENCE.md` and
  `artifact_W/EVIDENCE.md` differ in exactly two lines, both header;
- all four reporting the same `NOTES.md` blinding leak — **four rounds, the same
  disclosure, no fix**;
- a self-contradicting control block in all three sealed packets
  (`FI-03-DF-03`).

## Five things that go against all of the above

1. **The v1 arm is not a replication of the card PA-06's judges held, and the
   digest says it is.** The rubric gained the "Known instability" section
   *after* PA-06 scored, and the parsed digest is identical across that change —
   `sha256:e33638087c4191da` on both sides — because it covers the anchors and
   the numbered rules and no prose. **Both v1 judges cited that section as their
   reason for not executing.** Part of the stability above was bought by a
   paragraph the digest cannot see, and **any comparison treating the v1 arm as
   a replication is comparing two different rubrics under one hash.**
   `FI-03-DF-02`.
2. **No round before this one preserved its judge prompt**, so every movement
   here carries an unmeasurable component: the difference between PA-06's
   dispatch and FI-03's reconstruction of it from `UNBLINDING.md`'s prose. The
   artifact is verified byte-identical; the instruction is not, and cannot be.
   `FI-03-DF-01`. FI-03's own prompts are committed, which is the first time.
3. **Twelve cards, one model family.** Agreement between two `claude-opus-5[1m]`
   judges reading the same anchors is weaker evidence than it looks, for the
   fourth round running. The exact reproduction of PA-06's pass-2 row is the
   strongest result above **and** the strongest illustration of this objection.
4. **The repository was modified while blind judges were reading it.** FI-03
   edited this file and `INSTRUMENT-LOG.toml` during the v2 pass, and the v2
   pass-2 judge noticed and reported it unprompted. Neither file is a scored
   artifact and both were on its forbidden list, so nothing it scored moved —
   but a measurement should not have a moving floor and this one did.
5. **One accidental read, self-disclosed.** The v2 pass-1 judge chose a scratch
   filename already occupied by a leftover script from the v1 round and read
   fifteen lines of it before stopping and renaming. It saw no score and no
   label, but it learned that a v1 round existed. Recorded, not re-run.

---

# FI-06 — falsifiable-instruments, the evaluation (2026-08-06)

Full record: `specs/results/scorecards/falsifiable-instruments/RESULTS.md`, with
`channels/ADVERSARIAL.md`, three per-goal RESULT files and the measure artifacts
beside it. Measured on the integrated epic tip `30d033e` from a worktree at
`6c05d22`. **Suite: 1335 passed, 0 failed.** **FI-06 fixed nothing; it filed
twelve findings.**

**READ `FI-06-DF-04` BEFORE QUOTING ANY D2 OR D3 NUMBER FROM THE FI-03 SECTION
ABOVE.** The rubric FI-03's four judges were instructed to read contained, at
`51fe73d:361` and `:376`, the statement *"D2 and D3 are the dimensions that have
held still on unchanged input"* and a table of the prior sealed scores. PA-06's
judges did not have it (`git show 930fa57:references/eval_scorecard.md | grep -c
"held still on unchanged input"` → **0**). *"Four independent pairs"* is **two
uncontaminated pairs and two that were shown the conclusion.**

## The goals

| goal | baseline | measured | target | verdict |
|---|---|---|---|---|
| `GOAL-instruments-can-fail` | roughly 0 of ~9 | **26 of 35** as the harness reports it; **at most ~11 of ~43** once the enumeration is swept and the demonstrations attacked. 12 demonstrated blind spots, 0 reproduction failures | no target on the ratio; **"nothing is silently omitted"** | **`missed`** — on the only clause it targets |
| `GOAL-scorecard-carries-a-delta` | 4 dimension-points on byte-identical trees | max **1** vs the adjacent sealed row; max **2** vs the row before it, on D4 and D5 | at most 1 per judge, every dimension | **`missed`** |
| `GOAL-fixture-can-diverge` | NULL ENTAILED (64/64, 88/88) | metric retired with reasoning **and** one divergence demonstrated, re-derived byte-identically and re-run from a regenerated corpus with zero cells moved | a demonstrated divergence **or** an explicit retirement | **`met`**, narrowly |

**No target was edited. No number was re-run until it passed.**

## THREE ROWS THAT MUST STOP BEING CITED, AND ONE THAT SURVIVES

- **D2 — STOP CITING IT AS ANYTHING.** `D2 = 2` on **27 of 27** cards ever
  written about `ab_quota_ledger`, counting every sealed `.history` snapshot:
  five rounds, two card versions, three arms, every judge. **It has never taken a
  second value.** Anchor 3 requires a before/after pair these greenfield
  artifacts cannot have, and the judges say so in their own rationales. **A
  dimension that has never moved cannot be shown stable by not moving.** D4 and
  D5 cannot carry a delta because they are noisy; **D2 cannot because it has no
  signal**, and this file reports the two as one good-news line. `:1069` already
  contains the refutation of `:1122` and `:1144`. `FI-06-DF-05`.
- **`total` — the worst column in this file.** It sums a constant with two
  dimensions that cannot carry a delta, and it moved **+4 of 20 — 20% of the
  scale — on byte-identical code**. It is bolded in every table, in a file whose
  first line is *"The metric is the delta, not the total."*
- **The `architectural-coherence` baseline table.** Those ten cards were scored
  at `ab0dfee`, where `references/eval_scorecard.md` **is not in the tree**; they
  carry no `anchors` block and no `rubric` key. They are not on this card. They
  are also the only evidence anywhere that D2 is capable of moving.
- **D3 SURVIVES, and it is the only one.** `4 / 2 / 1`, perfectly discriminating,
  reproduced across rounds, card versions and judging practices. Attacked on
  floor/ceiling pinning, coarse anchors, judge-family collapse and artifact size;
  none held. Two corrections: it was produced by **three** blind pairs, not four
  (`W` was built at PA-06 and did not exist at EVAL-RERUN), and two of those
  pairs read a rubric that told them D3 holds still.

**The target is a `max` statistic and cannot detect drift.** The measured
movement is directional — `8 of 9` negative on one leg, `9 of 9` positive on
another. Four more rounds of "MET at −1" walks D5 from 4 to 0 with every step
certified within target. **And MET against one sealed baseline while MISSED
against another, over the same bytes, means the delta is a property of the pair
of reading sessions rather than of the pair of artifacts.**

## The instrument count, and why it is not a ratio

**40 enumerated · 5 not-an-instrument · 35 instruments · 26 with a demonstrated
failing input · 9 without · 12 with a demonstrated blind spot · 0 reproduction
failures.** The charter's baseline said *"roughly 0 of ~9"*; **the enumeration
found 35, so this project did not know its own toolchain size to within a factor
of four.** That is the epic's clearest win.

**The goal's only target is "nothing is silently omitted", and nothing enforces
it.** `FI-04-DF-04` was filed inside the epic and not closed; it failed three
more times with the suite fully green. FI-06's adversarial channel found **at
least eight more omissions**, including `run_arm_swap.py` — shipped by FI-04 in
the same reconcile as the instrument it registered by hand while writing that
finding — and `demonstrate.py`, the enumerator itself. One of the eight,
`scripts/extract_spec_manifest.py`, is **red on the shipped tree right now**.

**And the numerator is a ceiling.** All **twelve** `kind = "pytest"` failing
slots declare `expect_exit = 0` and nothing else, so a wholly **skipped** test
reports `ok` — the `R-H5` staleness failure generalised (`FI-06-DF-02`). Two rows
have `failing.nodes == passing.nodes` and no seeded break at all
(`FI-06-DF-03`).

## Findings by channel — **0 : 16 : 1 : 1 : 12**

| channel | findings |
|---|---|
| suite re-run | **0** |
| the building ticket auditing its own instrument | **16** |
| blind judge asked what it REJECTED | 1 |
| blind judges' unprompted disclosure | 1 |
| fresh adversarial attack (FI-06, four parallel agents) | **12** |
| **total** | **30** |

**Stated as a result: all thirty came from asking an agent what its own
instrument cannot report, or from telling one to attack. The suite produced
ZERO** — for the fifth round in six — **and it was green throughout, while three
instruments were missing from the enumeration, twelve demonstrations could report
`ok` for a test that never ran, and one shipped validator was red on the
repository's own model.**

The predecessor ran **1 : 12 : 4 : 2**. **The new channel is this epic's real
methodological product**: *build the instrument, then ask what it cannot report*
produced 16 of 30, is cheaper than an adversarial agent, and found the structural
defects. The adversarial channel found the ones the builder could not see because
they were about the builder's own frame.

## AGAINST THE "EVIDENCE WE ARE FOOLING OURSELVES" LIST

**"Every prediction passing."** — **TRUE ON ONE CHANNEL AND REPORTED AS TRUE.**
FI-04's eight sealed predictions are **8 of 8**, and four of the four negatives
are structurally unfalsifiable: one is a determinism check wearing an
architecture check's label, one is entailed by four lines of arm B's source, and
two are decided by literals FI-04 typed. Not true of the epic as a whole — two
goals missed and the generator answer moved twice in opposite directions.

**"Findings arriving only from the suite."** — **FALSE, and the inverse is now
the standing alarm.** Zero of thirty.

**"A score moving without an artifact moving."** — **TRUE, and worse than this
file records.** Five separate demonstrations on trees verified byte-identical at
the tree-object level: EVAL-RERUN→PA-06 (+13/20), PA-06→v1 (−7/30), PA-06→v2
(−5/30), EVAL-RERUN→v2 (+8/20), and the version bump (4/30). This file marks it
as having happened once.

**"A withheld case passing that its siblings failed."** — **DID NOT ARISE.**
FI-06 fixed nothing, by rule.

**A FIFTH ITEM BELONGS ON THIS LIST AND IS CURRENTLY TRUE: a judge being handed
the result before scoring.** `FI-06-DF-04`. Proposed rather than added, because
the list is the ledger's.

## Does anything we generate beat a hand-written suite yet? — the answer moved twice

The epic opened citing *"the generated corpus is still worse than a suite a
competent engineer writes in an afternoon"*; the owner **overturned** it mid-epic
on blind-authored catalogues; **and FI-06 found a second blind-authored catalogue
on which the suite strictly dominates.**

`specs/results/scorecards/hexagonal-prompting/GOAL-catch-bugs/kill-table-blind-author-arm-{a,b}.json`
— same channel, same protocol, sealed since `1a2b65f`:

```
blind-HP06 / arm A   13 rows   generated union 8   suite 9   generated-only []   SUITE STRICTLY DOMINATES
blind-HP06 / arm B   14 rows   generated union 8   suite 9   generated-only []   SUITE STRICTLY DOMINATES
```

**And it is the same fault class.** `BA-A10` (`id_allocation`) is SURVIVED by
every column including the suite. `BA-P11`, the one kill that saves the
generator, is the same semantic drawn by a different blind author.
**`QuotaLedger.cfg:8` declares `ResIds = {r1, r2}` and `holder'` is assigned at
exactly one place, so no behaviour of this model contains more than two
`Reserve` actions.** `BA-P11` reuses an id at allocation **#2** — inside the
ceiling. `BA-A10` at **#4** — outside it. `oracle.py:86-101` already defines
`STATE_NOT_EXPRESSIBLE` for this and counts **266 of 294** skips against it, on
every run, for three epics. `FI-06-DF-07`, `FI-06-DF-08`.

> **The repository holds two blind draws of one fault class and they disagree
> completely. n is 2, not 1, and the error bar is bigger than the effect.**

**Also true and unchanged: no generated instrument has a unique kill on ANY
catalogue, blind ones included.** The suite is the only column anywhere with one.
No single generated column has ever matched the suite; the tie is six-against-one.
`map-checking ∪ corpus-neg` exactly equals the entire generated union on every
table — **four of six columns have never earned a cell.**

**Funding, committed to.** `corpus-neg` (the `modular-fuzzing` purchase): zero
unique kills anywhere, and every kill it has is inside the suite's set.
`corpus-port*` (the `ports-as-adapters` purchase): zero unique kills anywhere,
strictly dominated on its own home fixture, **absent from every blind table**,
and the only family that returns a wrong verdict on a declared positive control.
**The two mechanisms the last two epics bought contribute zero to the one
comparison that controls for authorship.** Defund the `[ports.*]` binding
machinery. Fund exactly one thing next: the blind-author experiment with the
constants enlarged and the port columns included.

## The claim this epic carried forward and did not check

`FALSIFIABLE-INSTRUMENTS-EPIC.md:94-98` restates, under *"Established, and worth
building on"*, that arm C was *"a length-matched control … with no architectural
vocabulary"* and that *"the predecessor's 6.6× confound is retired"*. Measured at
the tip against the bytes the epic itself now preserves as dispatched:
**1.181 (+18.1%), outside the declared ±10% tolerance, with 4 of 124 unique lines
carrying architectural vocabulary including the epic's own name** — and
`check_catalogue.py` goes `CATALOGUE INTEGRITY FAILED` saying *"if it asks for
structure it is a second treatment and the confound is not settled."*

`PA-06` measured this honestly and filed `PA-06-DF-10`; the retraction is at
`ports-as-adapters/RESULTS.md:121-125`. **It is in the sealed record and in
neither document that hands the result forward.** The D3 result survives — 1/1
against 4/4 is far outside what either defect accounts for. The tolerance claim
and the "0 of 109" do not. `FI-06-DF-06`.

## Did this epic make the numbers mean more? — yes, and less than it reports

**More:** thirty-five instruments are named and twelve carry a written,
re-runnable statement of what they cannot see, six of them failing toward green.
The scorecard's delta question is answered rather than assumed, and the answer
subtracts three dimensions and the total from what this file claimed. The
generator question has an error bar for the first time.

**Less:** **every count this epic produced is a count over a set nothing
enforces.** The goal's only target is *"nothing is silently omitted"* and the
mechanism that would meet it was never built. A number whose denominator has no
lower bound and whose numerator has no upper bound is not more meaningful than no
number — **it is a number with a false precision the previous rounds did not
have.**

**And the epic did to itself, twice, what it was written to stop.** Its charter
restated as settled fact two claims the sealed record had already retracted — the
generator sentence (§2, corrected by the owner mid-epic) and the arm C
length-match (§3, still uncorrected). **The document that exists to warn against
reading a row forward without checking it contains two rows read forward without
checking.** The mechanisms are better and the reading discipline is not, and the
reading discipline is what every one of these failures has been.

---

# SM-05 — subtract-to-measure, the evaluation (2026-08-07)

**Commit scored `f49a1c9`. Two subjects, four judges each, two model tiers, one
round. Nothing was fixed.**

## The headline — D2 separates on the SUBJECT, at both tiers

| subject | tier | D1 | **D2** | D3 | D4 | D5 |
|---|---|---|---|---|---|---|
| greenfield `ab_quota_ledger` | high | 3, 3 | **2, 2** | 2, 2 | 2, 2 | 3, 3 |
| greenfield `ab_quota_ledger` | low | 3, 3 | **2, 2** | 1, 2 | 3, 3 | 2, 2 |
| **toolchain removal** | high | 2, 3 | **3, 3** | 2, 2 | 2, 2 | 4, 4 |
| **toolchain removal** | low | 3, 2 | **4, 3** | 4, 3 | 3, 2 | 4, 4 |

**D2 = 2 on 4 of 4 greenfield cards and >= 3 on 4 of 4 removal cards, with no
overlap and no tier effect.** The evidence supports **explanation (b)**: the card
can measure complexity and had never been given a subject with a before. Judges
in both arms gave the mechanism unprompted — greenfield: *"anchors 3-4 need a
'before' a greenfield artifact cannot have"*; removal: *"a simplification was
made and both before/after figures are recorded."*

**D1 and D2 show no tier effect. D3 and D5 each move one point at the lower
tier.** All 41 prior cards were judged at the high tier, so the axis only runs
downward and says nothing about a judge stronger than `claude-opus-5[1m]`.

## AND THE PREMISE THAT JUSTIFIED THIS EPIC WAS ALREADY FALSE

**Read this before citing "D2 has never moved" again.** The epic opened on *"D2 =
2 on 27 of 27 cards ever written"* and *"every subject this project has ever
scored was greenfield … no greenfield artifact can reach D2 anchor 3, ever."*

**41 cards carry a D2 score, across six examples, and D2 has taken three values:
1 (`ex6_jenga`), 2 (four examples), and 3 (`ex3_over_complex`).** `ex3` was
blind-judged on 2026-08-03 and **both judges scored D2 = 3**, citing before and
after descriptors, both declining 4 for the MF-020 reason. In the one round that
scored five *different* fixtures, D2 discriminated across three values with
**perfect inter-judge agreement on all five**. The anchors digest is identical at
v1, v2 and v3, so those cards were scored against the same bar.

The "27 of 27" figure is a true fact about **one example** — the only one ever
re-scored — restated **unscoped** as a fact about the instrument, in the charter,
in the plan's `purpose`, and in the issue. `R-H2` forbids AVERAGING across
examples; **nothing forbids generalising from one**, and `history` requires
`--example`, so the spread is visible only to someone who already suspects it.
**That is the error that actually occurred, five epics running.**
`SM-05-DF-01`.

## D3 did not hold, and that outranks the headline

On the removal, D3 scored 2, 2, 4, 3 — **`contested` under scoring rule 5**, and
the rule's remedy cannot reach it. Both judges state the disagreement is about
**what the artifact is**, not about the evidence: one refused D3 = 4 that its own
execution supported, because the port lives in a *test fixture*, not the
toolchain. The other named the cause independently — *"the 2->3 seam, where 'the
domain' silently changes referent."*

**D3 holds still on single-artifact fixtures and spans two points on a
repository-scale subject.** `ports-as-adapters` rests its headline on D3 and this
file recommends D3 for cross-epic claims. That recommendation now carries a
scope. `SM-05-DF-06`.

## What the removals cost — zero, and one cost nothing could price

Nine gap mutants re-run on the integrated tip, both positive controls green on
every surviving detector, `mutants_not_applied: []`. **Zero mutants went `DIES` →
`SURVIVES`. Two went `SURVIVES` → `DIES`** (SM-03's repairs). Four mechanisms had
no seedable gap and are named rather than omitted.

**The cost with no mutant able to price it:** the four `corpus-*` columns report
`CONTROL_RED`, because SM-02 deleted `apply_wiring` while a sealed driver still
imports it. Two judges read that as a real price — *"the cut also broke the only
model-derived check pointed at it."* Not repaired: fix nothing during a
measurement.

## The subtraction epic is net ADDITIVE

`3f58aca` → `f49a1c9`: `scripts/` **−225**, `tests/` **+982**,
`examples/validation/` **+920** — **net +1677 `code_lines`**, 4948 insertions
against 1020 deletions. **Roughly seven lines of measurement apparatus per line
removed.** Two judges reached this independently and let it cap their score. The
D2 = 3 survives it only because anchor 3 asks for a *measured* simplification with
both figures recorded, not for a net reduction.

## FINDINGS BY CHANNEL — 0 suite : 3 blind-judge : 4 census, over seven filed

**The suite produced zero findings for the sixth round in seven.** The
blind-judge channel produced the round's best material at **0.26 findings per
100k judge-tokens**, **including both of the round operator's own redaction
errors** — one of which a judge showed had moved a dimension-point in its own
card, and disclosed rather than absorbed. The operator's errors are not counted
as findings; they are round-conduct defects, and the class they belong to is
`SM-05-DF-02`.

**`GOAL-cheaper` is MISSED and the expansion caused it.** 1,162,275 subagent
tokens across eight judges, against SM-04's ~420k for four — the removal subject
is a repository and costs ~60% more per judge than a 200-line fixture. The
per-channel clause of the target is met; the "costs less per finding" clause is
not — **0.60 findings per 100k against the predecessor's ~1.15, about half the
rate.** **The round bought the epic's only decisive result and paid above the going
rate for it.** Keep funding blind judges and the census channel; **the suite is
not a finding channel and should stop being reported as one.**

## Did this epic make the numbers mean more?

**D2 means more** — cited for five epics as a constant, now demonstrated to
discriminate across three values and to separate two subjects in one round at two
tiers. What changed is not the card: it is that the card was finally given
something to measure, and the citation was finally checked.

**D3 means less than it was claimed to.** **The instrument counts mean less** —
"33 of 47" is 18 observed refusals plus 16 assertions added together, and it was
taken in the wrong worktree; measured at the scored commit it is 34 of 48.

**And the durable lesson is a reading habit, not a figure.** The premise that
justified an entire epic was checkable in one command against this repository's
own sealed cards, and five epics restated it without running it.

---

# CA-05 — cut-the-apparatus: consumption, and the four epics missing from this file (2026-08-13)

**This is not an epic evaluation.** `CA-08` decides `cut-the-apparatus`. This
section exists because `CA-05` went looking for why consumption is 1 in 41 and
found the answer partly **in this file's own table of contents**.

## Four epics are missing from this file, and it is the same four

Scroll up. The evaluation sections end at **`SM-05`, 2026-08-07**. `git log` on
this file agrees: last touched `73ebeb6`, 2026-08-07. **Four epics have merged
since and none of them wrote a section here** — reading-discipline (08-10),
portable-substrate (08-10), close-the-loop (08-11), score-drives-validation
(08-12).

Now put that beside the disposition state of the findings ledger, measured by
`scripts/disposition.py --all` over all 220 rows:

| epic | merged | section in this file | findings disposed |
|---|---|---|---|
| ports-as-adapters | 2026-08-05 | **yes** (`PA-06`) | 26 of 28 — *and both refusals are FALSE, the record is in another key* |
| falsifiable-instruments | 2026-08-06 | **yes** (`FI-03`, `FI-06`) | **30 of 30** |
| subtract-to-measure | 2026-08-07 | **yes** (`SM-05`) | **30 of 30** — *but only after `CA-05-DF-06`; it was a FALSE pass* |
| reading-discipline | 2026-08-10 | no | **0 of 46** |
| portable-substrate | 2026-08-10 | no | **0 of 28** |
| close-the-loop | 2026-08-11 | no | **0 of 17** |
| score-drives-validation | 2026-08-12 | no | **1 of 31** |
| cut-the-apparatus | in flight | no | **6 of 22** — `CA-05`'s own rows |

**`CA-05` originally called this "an exact correlation across eight epics in
both directions". THAT IS WITHDRAWN**, at the instruction of PR #265's
independent reviewer, who was right:

- **They are not two independent registers.** `d3f483d` writes
  `deferred_findings.yaml` **and** this file **in one commit**. They are two
  outputs of the **same close-out ritual by the same actor**, so their co-lapse
  is *definitional*, not evidential.
- **It is one observation, not eight** — two step functions sharing a single
  changepoint.
- **And the date was wrong.** "Stopped dead on 2026-08-08" named a day on which
  nothing happened. The boundary is **2026-08-07 → 2026-08-10**.

The row above is kept because it **locates the ritual that lapsed**, which is
useful. It corroborates nothing.

## So the premise behind `GOAL-consumption-obligatory` is half wrong

The goal was written from *"consumption is 1 of 38 because nothing requires
it."* The first half holds. **The second half does not.** A disposition practice
existed, ran for three consecutive epics, routed **61 findings into successors
OUTSIDE the filing epic** — including five purpose-built carry-forward issues,
**#144–#148, still open today** — and then **stopped, between 2026-08-07 and
2026-08-10, without one line of discussion in any record.**

*(83 `carried` rows in total; **22 self-route** to a ticket of the epic that
filed them and routed nothing anywhere. `CA-05` first published 83 as though it
were all routing. The reviewer of PR #265 computed 54 from rows that
`CA-05-DF-06` has since repaired; honouring `#188` gives 61 — PA 14, FI 29,
SM 18.)*

**A practice that lapses silently is a worse failure mode than one that never
existed**, because the first one was working and nobody was watching. That is
the finding, and it is not the one this ticket was sent to get.

**The exact boundary, and it is slightly cruel:** `reading-discipline` is the
epic that **consumed its predecessor's deferrals** (11 `SM` rows routed into
`RD-02`, #189) **and deferred none of its own.** The last epic to receive a
handoff is the first that made none.

## Findings by channel — now a field, not a hand classification

Six epics of tables in this file and in `NEXT-EPIC.md` have been produced by
hand-classifying free text, because **the ledger had no `channel` field**.
`CA-02` and `CA-05` populate one. Vocabulary and the reconciliation with
`CA-02`'s free-text shape: `references/consumption.md`.

**This does not retro-classify the 210 rows filed before the field existed**,
and `CA-05` declined to do it — assigning a channel to somebody else's finding
from its prose is exactly the hand classification the field exists to end, and
doing it in bulk would manufacture a clean history that was never measured.
**Every table above this line remains a hand count and should be quoted as one.**

## The consumption rate, restated

**1 of 41 (2.4%)** consumed into program validation — class `A1`, by `SV-04`,
unchanged. The denominator rose from 38 because `CA-05` appended the three
classes `SV-01-DF-05` filed to the ledger and never to the register; **the
numerator did not move.** Working, and its bounds:
`specs/results/scorecards/close-the-loop/GOAL-loop-closes-once/CL-03/HARVEST-CL-03.md`,
addendum.

**And 41 is a floor.** The sweep read 83 cards; the tree holds **95**. Twelve
cards have never been swept.
