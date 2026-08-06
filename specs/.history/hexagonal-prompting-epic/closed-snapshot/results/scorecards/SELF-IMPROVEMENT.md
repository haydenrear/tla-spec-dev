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
