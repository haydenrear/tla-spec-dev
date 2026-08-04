# PREDICTIONS — hexagonal-prompting epic

**Sealed at dispatch. HP-06 scores these and may not amend them.**

Committed by HP-01 *before* HP-02, HP-03, HP-04 or HP-05 is dispatched. Every
row has an **ID**, the **instrument** that settles it, and an **expected
direction**. A prediction with no instrument is an opinion, and an opinion
cannot be wrong in a way anyone notices.

## Why this file exists, and why a third of it predicts nothing moving

The predecessor epic's **RP-02** closed a real oracle leak. Parameter recovery
went from 0 of 5 to 5 of 5 — a large, correct, well-evidenced repair. It moved
the seeded-mutant matrix by **zero cells**. Nobody predicted that, and because
nobody predicted it, round 1's explanation for its own zero ("the corpus can't
recover the argument") had been recorded as fact for an entire epic while being
false. The negative predictions below exist so that outcome is *scored* this
time instead of discovered.

The bar the negatives set: **at least three predictions in this file must be
about something NOT moving**, and they must be things a reader would plausibly
expect to move. Six are recorded (N01–N06). Predicting that an unrelated number
stays flat is not a negative prediction; it is padding.

## Ground rules

- Agents implementing the arms are **never shown this file**, before or during
  their run.
- Findings during measurement are **FILED, never fixed** — a fix during a
  measurement destroys the measurement.
- Every number is reported **per arm and per class**. A kill rate with no arm
  named is uninterpretable; that is the predecessor's DP-8 rule and it is why
  it has a 4/6 and a 6/6 rather than one misleading average.
- **Never average across examples or across arms.**
- Scoring vocabulary at HP-06: `PASS`, `FAIL`, `SUPERSEDED` (the instrument
  itself turned out not to measure what the prediction assumed — must cite
  which instrument and why), or `UNMEASURED` (the instrument did not run —
  must say why). `UNMEASURED` is not a pass.

## The measured baseline these are predictions against

From the sealed predecessor scorecards
(`specs/.history/architectural-coherence-epic/closed-snapshot/results/scorecards/`),
two blind judges, zero contested dimensions:

| | ex1 | ex3 | ex4 | ex5 | ex6 |
|---|---|---|---|---|---|
| **D1** bug detection | 2 | 2 | 2 | 1 | 0 |
| **D2** complexity | ≤3 | 3 | ≤3 | ≤3 | ≤3 |
| **D3** modularity | 1 | 1–2 | 3 | 1 | 0–1 |

**Nothing reached 3 on D1 anywhere. Nothing reached 4 on any dimension.**
Guard relaxation 0 of 3 on both arms and 0 of 4 on a blind catalogue. Ordering
0 of 2 on everything, including the hand-written suite.

### And one baseline measured at HP-01, which is unflattering to this epic

`check_catalogue.py --verify-suite`, run on the reference implementation with a
green control: **the hand-written suite kills 10 of 10 mutants in this
catalogue, including the ordering negative control.**

That is the bar the generated corpus has to clear, and it is a high one. If a
model-derived corpus scores below 10 of 10 on this fixture, **the generator is
worse here than a suite a competent engineer writes in an afternoon**, and
HP-06 must report that in those words rather than reporting the corpus's kills
in isolation where they will read as a success.

It also fixes how every row below must be read: the interesting quantity is
never "how many died" but **which instrument saw which class.** A number that
merges the `suite` row into the `corpus` rows destroys the only comparison this
round exists to make.

*Declared bias:* that 10 of 10 is an upper bound, not a typical result. The
suite was written before the catalogue but by the same author who chose the
fault classes. Nobody should cite it as "hand-written suites catch everything".

## The arms

| Arm | Prompt file | Instrument under test |
|---|---|---|
| **A** | `examples/validation/ab/arm_a/PROMPT.md` | an ordinary implementation ask |
| **B** | `examples/validation/ab/arm_b/PROMPT.md` | the hexagonal + minimize-complexity ask (HP-02) |

Same feature (`examples/validation/ab/FEATURE.md`), same model, same seeded
catalogue (`examples/validation/ab/seeded_faults.toml`), same two blind judges.

---

## Positive predictions

### P01 — the prompt produces modularity in fact
**Instrument:** two judges, blind to arm, D3, per `references/eval_scorecard.md`.
**Direction:** UP for arm B relative to arm A.
Arm B scores **D3 ≥ 3 from both judges** on the majority of its produced
artifacts, where arm A scores 1–2. Baseline: D3 = 1 / 1–2 / 3 / 1 / 0–1, only
one example at 3, nothing at 4.
**This is the epic's central hypothesis.** If D3 does not separate, the prompt
is decoration and the epic must say so in those words.

### P02 — guard relaxation moves off zero, for the first time
**Instrument:** the seeded catalogue's `guard_relaxation` class (M01, M02, M03)
under the **`corpus-neg`** instrument specifically — HP-03's negative corpus —
reported per arm.
**Direction:** UP from a measured, replicated zero.
At least one of M01/M02/M03 is killed **by a generated corpus** on at least one
arm. Baseline is 0 of 3 in round 1, 0 of 3 in round 2 on **both** arms, and 0
of 4 on an independent blind catalogue.

**The instrument is named this precisely on purpose.** All three guard mutants
are already killed by the hand-written suite (measured at HP-01, see
`seeded_faults.toml [measured_suite_baseline]`). A round that reported "guard
relaxation: 3 of 3" without naming the instrument would look like the epic's
headline result while actually being a fact about a pytest file. **A kill by
`suite` does not settle P02. Only a kill by `corpus-neg` or `corpus-whole`
does.**

**If this stays at zero, that is the epic's most valuable finding**, and it
means the class needs a profile change rather than a generator.

### P03 — the mapping choice reproduces its measured 30% of the yield
**Instrument:** the `durable_content` class (M04, M05, M08) scored twice — once
under a content-asserting mapping, once under a silent one.
**Direction:** a large gap between mappings; near-zero gap between arms.
The durable-content mutants die under the checking mapping and survive under
the silent one, reproducing the predecessor's 3 of 3 vs 0 of 3.
**Corollary predicted at the same time:** the arm makes little difference here
and the *mapping* makes almost all of it.

### P04 — the cross-aspect mutant separates the slice from the whole view
**Instrument:** M08 and M03, run under an aspect-slice corpus and under the
whole-view corpus, reported per slice.
**Direction:** M08 survives the slice, dies under the whole view.
Round 1 concluded "case modules kill exactly what the whole view kills." That
conclusion was an artifact of a catalogue containing no cross-aspect mutant;
when one was deliberately placed, the claim fell to 9 of 10. M08 and M03 are
that mutant, placed on purpose.

### P05 — the positive control dies everywhere
**Instrument:** M07 (`wrong_field`), every arm, every mapping.
**Direction:** killed, 100%.
M07 exists so a total of zero can be distinguished from a broken instrument. If
M07 survives, **every other number in the round is void** and HP-06 reports the
instrument as unciteable rather than reporting kills.

### P06 — some example finally reaches the D1 bar
**Instrument:** two blind judges, D1 anchor 3, both judges agreeing.
**Direction:** UP, from a ceiling of 2.
At least one artifact scores **D1 ≥ 3 from both judges**, carried by a kill in
M01–M03 or M08 — a class the whole-view corpus structurally cannot reach.
This is `GOAL-catch-bugs`'s stated target.

### P07 — both arms actually finish
**Instrument:** the shared behavioral suite in `examples/validation/ab/`, and D4.
**Direction:** both arms ≥ 2 on D4.
Both arms produce code passing the same behavioral suite, so any D1/D2/D3
separation is a property of the instrument and not of one arm having run out of
budget. **If either arm fails this, the round is not an A/B** and HP-06 says so
rather than reporting the difference.

---

## Negative predictions — what will NOT move

These are the rows this file exists for.

### N01 — D2 will not separate in arm B's favor, and may separate against it
**Instrument:** D2 from both judges, plus `analyze complexity` descriptors of
both arms' artifacts.
**Direction:** NO separation, or separation the WRONG way.
"Minimize complexity" and "make it hexagonal" pull in opposite directions:
ports, adapters, and an inversion boundary are *more* parts, more indirection,
and a larger descriptor, not fewer. The predecessor's own measurement is that
adding surface costs ~1.5 coverage gaps and ~8× state space.
**Predicted:** arm B's measured descriptor is **not lower** than arm A's.
If arm B nevertheless scores D2 = 4, check first that nothing was deleted —
MF-020, a metric can improve because an edge was deleted, and both judges
withheld a 4 from ex3 for exactly that reason.

### N02 — ordering stays at zero on every *generated corpus*, on both arms
**Instrument:** M09, the declared negative control, under `corpus-whole`,
`corpus-slice`, `corpus-neg`, and both mappings.
**Direction:** FLAT at zero **for every corpus instrument.**
Sets in the model, ordered lists in the code, `sorted()` at every oracle layer.
The predecessor measured ordering invisible to all five corpus instruments.

**Measured at HP-01 and stated up front so this prediction is not read as
wider than it is: the hand-written suite DOES kill M09**
(`test_r5_the_ledger_is_append_only_and_ordered` compares the line list
positionally). So N02 predicts a **split**, not a universal zero — and the
split is the point. M09 is the sharpest single measurement in the catalogue of
what a generated corpus structurally cannot see but a person writing tests
sees without trying, and it feeds HP-06's findings-by-channel report directly.

M09 is seeded even though the plan puts ordering out of scope, because the
predecessor recorded exactly this kind of claim as a caveat, never ran it, and
was later shown wrong about a different never-run caveat — EV-01 declined to
seed a wrong-item fault as "unmeasurable", and when RP-02 finally seeded two,
**both died**, on the pre-fix instrument as well as the post-fix one. **An
unrun caveat is not a result.** A survivor here confirms a documented limit; a
kill by a corpus retracts one. Both are results.

### N03 — D5 will not separate between arms
**Instrument:** D5 from both judges.
**Direction:** FLAT.
Neither prompt says anything about refusing, about naming blind spots, or about
`unobservable` beating a false clean. D5 measures the *toolchain's* reports,
which are identical across arms.
**This is also the round's blindness check:** if D5 separates, the most likely
explanation is not that one prompt produced a more honest program — it is that
the judges worked out which arm they were reading. HP-06 must consider that
explanation before any other.

### N04 — the prompt will not move D1
**Instrument:** D1 per arm, and the per-class kill table per arm.
**Direction:** arm A and arm B within ±1 on D1; per-class kill counts differ by
at most one cell.
The prompt changes the **code**; the cases come from the **model**, which is
identical across arms. Whatever moves D1 this epic will come from HP-03's
negative corpus, HP-04's oracle repair, and HP-05's default mapping — not from
the prompt.
**Arm B must also not REDUCE D1** (that is HP-02's declared `guard`). A prompt
producing prettier code whose adapters catch less has failed.

### N05 — HP-04's oracle repair will move the mutant matrix by zero cells
**Instrument:** the seeded catalogue run before and after HP-04, same corpus,
same mapping, per class.
**Direction:** FLAT — zero cells.
This is the RP-02 shape recorded as a prediction instead of as a surprise.
HP-04 fixes three measured defects (`sys.path`, `can_run`, a 43% nondeterminism
spread) and takes the oracle from 8 of 18 actions to 18 of 18. Coverage of
*actions* is not detection of *faults*: the ten actions the oracle newly sees
are the ones whose adapters were apply()-only, and an apply()-only adapter
asserts nothing about the durable side. **Predicted: recovery-style metrics
improve substantially and the kill table does not move.**
If it does move, the cell that moved is the finding, and it should be named.

### N06 — the suite will produce none of this epic's findings
**Instrument:** HP-06's findings-by-channel table (suite re-run / fresh
adversarial attack / blind author), with counts.
**Direction:** ZERO from the suite channel.
Both predecessor rounds produced their best finding from an agent asked what it
**rejected**, and zero findings from re-running the suite. Predicted to repeat.
**If it repeats, HP-06 must say plainly that the suite has stopped being
informative** — that alarm exists to fire *before* the tool silently gets worse,
not after. If the suite does produce a finding, that is good news and should be
reported as an improvement in the suite.

---

## Stated confounds — read before attributing any win

These are not predictions. They are limits on what this experiment can
conclude, written down now so no one argues them away later.

1. **Prompt length and effort are not controlled.** Arm B's prompt is longer and
   asks for more. If arm B wins on any dimension, this round **cannot**
   distinguish "hexagonal guidance helped" from "a longer, more specific ask
   helped." Any claim that hexagonality specifically caused the win requires a
   third arm this epic does not run.
2. **The reference implementation is not an arm.** `examples/validation/ab/reference/`
   exists so the catalogue's `find`/`replace` pairs have an exact anchor and the
   exactly-once harness has something to assert against. It is not judged, not
   scored, and its numbers are never placed in a table beside an arm's.
3. **`n = 1` feature.** One feature specification, two arms. A dimension that
   moves is a signal about this feature, not a property of prompting.
4. **The judges are agents.** Two of them, blind to each other and blind to arm,
   scoring artifacts with `file:line` citations — but agents. Rule 4 of the card
   (prose quality is never an input) is the one rule nothing mechanical can
   enforce, and arm B's prompt asks for structure that tends to read well.

## Scoring template for HP-06

| ID | Prediction | Instrument | Expected | Observed | Verdict |
|---|---|---|---|---|---|
| P01 | D3 separates, arm B ≥ 3 both judges | 2 blind judges | UP | | |
| P02 | guard relaxation kills > 0 | M01–M03 under **corpus-neg**, never `suite` | UP from 0 | | |
| P03 | mapping gap ≫ arm gap on durable content | M04/M05/M08 × 2 mappings | large gap | | |
| P04 | M08 survives slice, dies whole-view | per-slice kill table | separates | | |
| P05 | M07 dies everywhere | catalogue, all arms/mappings | 100% killed | | |
| P06 | some artifact reaches D1 ≥ 3 both judges | 2 blind judges | UP from 2 | | |
| P07 | both arms pass the behavioral suite | shared suite + D4 | both ≥ 2 | | |
| **N01** | D2 does not separate for arm B | D2 + descriptors | FLAT or reversed | | |
| **N02** | ordering stays zero on every corpus | M09 under each corpus (suite kills it, measured) | FLAT at 0 for corpus | | |
| **N03** | D5 does not separate | D5, both judges | FLAT | | |
| **N04** | the prompt does not move D1 | D1 + per-class table | within ±1 | | |
| **N05** | HP-04 moves the matrix zero cells | catalogue before/after HP-04 | FLAT | | |
| **N06** | the suite produces no findings | findings-by-channel | ZERO from suite | | |
