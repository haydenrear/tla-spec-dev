# RD-03 — predictions, sealed before a single judge was dispatched

Committed with **24 unfilled skeletons on disk and not one score in existence**.
Every prediction below names the observation that would falsify it. **If every
one passes, that is an ALARM and is reported as one** — a round whose
expectations all hold has measured the round's author and not the artifacts.

The cards were scaffolded first so that this file could not be written after a
number was seen. `git log` is the check: the skeletons and this file land in one
commit, and every `scorecard.json` in it carries `"status": "unfilled"` with
every `score` `null`.

---

## A. The headline — D2 on the three before/after pairs

**P1. At least one after-tree is scored D2 = 2, not 3, by at least one judge**,
on the ground that a 2-line delta with branch points, state count and public
surface unchanged is not "a simplification was made". *Falsified if all 12
after-cards read D2 ≥ 3.*

**P2. `F` is the one most likely to be refused anchor 3**, because its revision
changed no implementation line at all — one added file and nothing else.
*Falsified if `F`'s D2 is greater than or equal to `M`'s and `D`'s on every
judge.*

**P3. D2 will be CONTESTED (spread > 1) on at least one after-tree.** Anchor 3
is reachable for the first time on the product side and the anchor's own words —
*"a simplification was made and its effect measured"* — do not say how large a
simplification must be. Two judges reading the same 158 → 156 can legitimately
land 2 and 3. *Falsified if no after-subject's judge group has a D2 spread
greater than 1.*

**P4. The before-trees `Z`, `E`, `N` are all scored D2 = 2.** They are
greenfield; anchor 3 is structurally unreachable for a subject with no before.
This is the prediction that is nearly certain and it is here as the control: if
a greenfield tree comes back D2 = 3 the anchor is being read in a way no prior
round read it, and that is a bigger result than anything else in this file.
*Falsified by any greenfield card with D2 ≠ 2.*

**P5. A tier split appears on at least one dimension.** Three exist in the
record, two of which nobody had looked for. *Falsified if `contested` reports
zero TIER-SPLIT rows across all six judge groups.*

**P6. D3 separates `E`/`F` from the other four**, in the direction the
`effect_boundary` demonstration row already carries — `ports-and-adapters` high,
`effectful` low. This one is EXPECTED to pass and passing it proves nothing new;
it is recorded so that **failing** it is reportable, because a failure would be
evidence against the axis the whole of RD-04/RD-05 rests on. *Falsified if any
`effectful` tree scores D3 ≥ 4, or `E`/`F` score D3 ≤ 2.*

## B. Negative predictions — each names its own falsifier

**P7. NO judge finds a bug in any of the six trees that the shared behavioural
suite does not already catch.** All six are 28/28 green on the shared contract,
and D1 asks about *seeded faults caught*, not about faults present. *Falsified
by any card whose `judging_practice.what_was_run` reports a fault it seeded that
the tree's own tests missed AND the shared suite missed.*

**P8. NO card scores D1 = 4.** Anchor 4 requires the catching cases to be
**derived from the model** rather than hand-written. These six trees were written
by an agent from a `FEATURE.md`; no model-derived corpus was generated for any of
them. *Falsified by any D1 = 4 with a citation to a model-derived case.*

**P9. The product-surface finding count this round is greater than zero.** The
predecessor rounds produced ZERO. This is the number the re-scope exists to move
and predicting it non-zero is the honest exposure. *Falsified if RD-03 closes
with zero findings whose subject is produced code rather than apparatus — in
which case the re-scope failed and the report says so.*

**P10. The suite produces ZERO findings again.** Six of seven rounds it has. *A
single suite-originated finding falsifies it, and would be the strongest
available argument for continuing to fund it.*

## C. The apparatus goals

**P11. `scope` run over RD-03's own writing reports a REFUTED that is a
*mention* rather than an assertion** — RD-05 §7.1's bound, hit again, because
this report must quote `D2 = 2 on 27 of 27` in order to report it as false.
*Falsified if `scope` over this round's files reports zero REFUTED.*

**P12. `scope`'s count over the record has MOVED since RD-01's 19/11/6/8.** RD-05
and RD-06 both wrote to swept files. Direction not predicted — predicting the
direction would be inventing the answer. *Falsified only by an unchanged 44-figure
split, which would itself be worth reporting.*

**P13. GOAL-apparatus-priced is CONFIRMED LOAD-BEARING** on RD-02's evidence and
not overturned. *Falsified if re-reading `discriminate` against the sealed
before-table shows any of the nine gap mutants could have gone `DIES` →
`SURVIVES`, or if `SM-04-GM-T1`'s `DIES` → `SURVIVES` fails to reproduce.*

## D. What would make me wrong about the whole round

**P14. The instruments point at the product and still say almost nothing about
the product.** My expectation is that this round's product answers are thin —
three verdicts, two of them "no effect measured" — and that the informative
result is the D2 one. *Falsified if any of the three original questions comes
back with a replicated, confounder-controlled effect.*
