# RM-01 — the instrument can return non-zero, and the thing that made it zero was not what the epic was told

**Ticket:** [#209](https://github.com/haydenrear/tla-spec-dev/issues/209) ·
**epic:** `portable-substrate` · **parent:** `2c0d94e` · **goal:**
`GOAL-removal-can-be-priced`.

---

## 0. The four sentences

1. **A real removal has been priced non-zero.** `SM-03`'s cut of the
   thirteen-path enumeration literal took a detection away, measured
   `DIES` at `bf0fb29~1` and `SURVIVES` at `bf0fb29`, with `pytest-full`
   running whole at both trees and a positive control dying at both.
2. **The charter's diagnosis is right about the rule and wrong about which
   rule.** Re-runnability does exclude discriminating faults. But the fault
   that priced this removal **was always re-runnable** — its anchor outlives
   the cut. It was excluded one level further in, by
   `removal_census.py discriminate`, which classifies a fault
   `NON-DISCRIMINATING` — *"DIES after the cut was entailed before the cut was
   made"* — whenever a killing **detector name** survives. **A detector can
   survive by name and lose the kill**, and `SM-03` is exactly that case.
   `RM-01-DF-01`, **blocking, and it binds RM-03.**
3. **`SM-04-GM-T1` reproduces**, `CAUGHT` → `UNCAUGHT`, from an independent
   implementation driving the shipped CLI against the two real trees.
4. **The re-priced historical removals still come back at zero**, now measured
   over kill sets rather than detector names. RD-02's `0 of 9` survives a finer
   reading, and exactly one kill in the whole sealed table is lost to a removal.
   **The zero was real. The instrument that produced it was not able to produce
   anything else.**

---

## 1. THE CHARACTERISATION — why re-runnability excludes the discriminating faults

### 1.1 Stated exactly

`run_gap_mutants.py` measures a fault by applying a find/replace to a staged
tree. A price is `verdict(before)` → `verdict(after)`, so the fault must be
applied to **both** trees, and `apply_mutant` refuses unless the anchor occurs
exactly once. Therefore:

> **every priceable fault's anchor must lie in `before ∩ after`** — the part of
> the code the removal did **not** touch.

Discrimination needs the opposite. A fault prices a removal only if the removal
takes its kill away, and the code a removal deletes is the code that read the
surface the removal deletes. So a fault only the removed mechanism catches
usually lives in `before \ after`, which the rule forbids.

`gap_mutants.toml` says the collision out loud in its own `[[not_seedable]]`
row for the `fake =` fault: *"the table is deleted with the machinery, so there
is no post-removal tree the mutant could be re-applied to."*

### 1.2 The smallest change that admits them — and it is one word

**Survivorship over a before-table is sound towards `SURVIVES` and unsound
towards `DIES`.**

* If **no** killing `(detector, node)` survives the cut, every kill the fault
  had is gone. That is a **proof from the before-run alone** that the removal
  took the detection away. It is the direction a **price** lives in.
* If **some** killing `(detector, node)` survives, **nothing follows.** The
  survivor may have been weakened. The honest verdict is `UNDECIDED`.

So a fault that cannot be **re-run** after a cut can still be **evaluated**
after a cut: *proving `SURVIVES` never needed the after-tree.* The
re-runnability requirement bought nothing on the priceable side and cost the
entire class of faults whose surface dies with the mechanism.

`price_removal.py entail` implements exactly that and has **no verdict meaning
"it will still die"**; a test asserts the string `ENTAILED-DIES` does not occur
in it.

**The bound, stated with the verdict rather than left for a sweep:**
`ENTAILED-SURVIVES` proves the removal took away every kill the fault **had**.
It cannot see a kill the after tree **added**. It is an upper bound on the
price; only `price` against a measured after-table settles it.

### 1.3 And the exclusion is NOT what produced the zero

This is the part the ticket did not predict and it is the more useful half.

`removal_census.py discriminating()`:

```python
surviving = [d for d in kills if d not in deleted_detectors]
if surviving:  ->  "NON-DISCRIMINATING ... DIES after the cut was entailed"
```

Two things are wrong with reading a surviving detector **name** as a surviving
**kill**.

**(a) `pytest-full` is the whole suite, and no removal has ever deleted it.**
Any fault it kills is `NON-DISCRIMINATING` by arithmetic before anything runs.
Over the sealed before-table:

| why the row could not price | rows |
|---|---|
| killed by `pytest-full`, which no removal deletes | **5** |
| killed by `instrument-registry`, which no removal deletes | **1** |
| no kill at all | **3** |
| **total** | **9** |

`denominator_rule`: nothing moved here — this is a re-partition of RD-02's own
nine rows by cause, not a new count. The numerator of "could have priced" is
still 0 and the denominator is still 9.

**(b) A detector can survive by name and lose the kill.** A removal can leave a
node id in place and replace its **body**. `SM-03` did:
`tests/test_instrument_demonstrations.py::test_the_named_instruments_are_all_enumerated`
has the same file, the same function name and the same node id at `bf0fb29~1`
and `bf0fb29` — and a different check inside it. Every survivorship test at
**detector** granularity and at **node** granularity says that detector
outlived the cut. Both are right and neither is the question.

RD-02 wrote this down in one line — *"the literal lived INSIDE the
`registry-enumeration` node, whose name survived and got a new body"* — and read
it as a reason nothing about SM-03 could be priced. It is the opposite: it is
the reason SM-03's removal is the one that **can** be.

---

## 2. THE DEMONSTRATED `DIES` → `SURVIVES`, ON A REAL REMOVAL

### 2.1 The fault, and why it is the fault

`RM-01-RF-1` — **a registered instrument outside the derived enumeration scope
silently loses its row.** One edit, in `examples/validation/instruments/instruments.toml`:

```
- paths = ["tests/test_code_complexity.py"]
+ paths = []
```

The file keeps working. Only the registry stops naming it. That is precisely
what the deleted literal caught: its own docstring says *"IT IS A RENAME GUARD
AND NOTHING MORE"*, and a rename guard's job is to notice a path leaving the
registry.

Three of the thirteen `required` paths lie outside
`[registry.enumeration].roots = ["scripts", "examples/validation"]`:

```
specs/results/scorecards/ports-as-adapters/GOAL-port-reach/measure/run_port_swap.py
specs/results/scorecards/ports-as-adapters/measure/make_blind_copies.py
tests/test_code_complexity.py
```

and the third is additionally invisible to the discovery predicate, which needs
a `__main__` guard and a nonzero exit path that no pytest file has.

### 2.2 The measurement

<!--MEASUREMENT-->

### 2.3 The control, which is the fault with one property changed

`RM-01-RF-CTRL` is the **same fault class** on `scripts/code_complexity.py` —
a path **inside** `roots`. Same catalogue, same detectors, same trees, same
code path. It must die at **both** trees, and it does. Without it,
`RM-01-RF-1`'s `SURVIVES` at `bf0fb29` is undecided rather than a price: it
could mean the after-tree's detector is dead for every input.

**One property differs between the two rows and the verdicts separate on it.**

### 2.4 What the shipped classifier says about the same fault

`removal_census.discriminating`, run unmodified over the same sealed
artifacts, with SM-03's real `deletes_detectors = []`:

> `NON-DISCRIMINATING` — *"killed by a detector the removal does not touch, so
> DIES after the cut was entailed before the cut was made"*

It is wrong, on a real removal, about a fault that was measured at both trees.
That is `R1`: **a demonstrated failing input on a real subject, and the subject
is a shipped instrument.**
`tests/test_price_removal.py::test_the_shipped_classifier_calls_a_real_priced_removal_entailed`.

---

## 3. `SM-04-GM-T1` REPRODUCES

The known positive, and an instrument that cannot reproduce it is not working.

`SM-04-GM-T1` lives inside `tests/test_score_tools.py` and reads both sides in
one process at one commit, using that file's own helpers. It has never been
produced by anything else.

`altered_score_probe.py` drives the tree's **shipped CLI** — `scaffold`, then
`check` twice — imports nothing from the suite, and decides a kill by
**subtraction**: the problems the second run reports that the first did not.

| tree | card version | verdict | the new problem |
|---|---|---|---|
| `6aac1ec~1` | 2 | **CAUGHT** | `total 8 does not equal the sum of dimensions (6)` |
| `6aac1ec` | 3 | **UNCAUGHT** | — |

`DIES` → `SURVIVES`, replicated. Raw: `sm04-gm-t1-before.json`,
`sm04-gm-t1-after.json`.

### 3.1 The probe's first design was confounded, and both runs are in the tree

The first version raised `D3` from 1 to 3. That trips a **citation** rule —
`D3 scored 3 with NO citation -- rule 2 caps it at 1` — at **both** trees, so
the probe read `CAUGHT` everywhere for a reason with nothing to do with the
checksum. The fix is what `SM-04-GM-T1` itself does: start at a **cited 4** and
move **down** to 2, so the citation rule is satisfied at both ends and the only
thing that changes is the score and the sum over the scores.

`sm04-gm-t1-before-confounded.json` and `sm04-gm-t1-after-confounded.json` are
committed, and a test asserts they are. **A correction nobody can see is
indistinguishable from a number that was tuned.**

---

## 4. THE RE-PRICED HISTORICAL REMOVALS — AND THEY COME BACK AT ZERO

RD-02 computed `0 of 9` over **detector names**. This recomputes it over the
**kill set**: a killing node counts as surviving only if the node still exists
at the removal's head.

| removal | mutant | `discriminate` | `price_removal entail` | measured | agrees |
|---|---|---|---|---|---|
| `ports-binding-machinery` | `SM-GM-P1` | NON-DISCRIMINATING | UNDECIDED | FREE | yes |
| `ports-binding-machinery` | `SM-GM-P2` | NON-DISCRIMINATING | UNDECIDED | FREE | yes |
| `ports-binding-machinery` | `SM-GM-P3` | NON-DISCRIMINATING | UNDECIDED | FREE | yes |
| `hardcoded-enumeration-literal` | `SM-GM-I1` | NO-KILL-TO-LOSE | NO-KILL-TO-LOSE | NO-KILL-TO-LOSE | yes |
| `hardcoded-enumeration-literal` | `SM-GM-I2` | NO-KILL-TO-LOSE | NO-KILL-TO-LOSE | NO-KILL-TO-LOSE | yes |
| `hardcoded-enumeration-literal` | `SM-GM-I3` | NO-KILL-TO-LOSE | NO-KILL-TO-LOSE | NO-KILL-TO-LOSE | yes |
| `hardcoded-enumeration-literal` | `SM-GM-I4` | NON-DISCRIMINATING | UNDECIDED | FREE | yes |
| `hardcoded-enumeration-literal` | `SM-GM-I5` | NON-DISCRIMINATING | UNDECIDED | FREE | yes |
| `hardcoded-enumeration-literal` | `SM-GM-I6` | NON-DISCRIMINATING | UNDECIDED | FREE | yes |
| `dead-port-binding-report-detector` | `SM-GM-P2` | NON-DISCRIMINATING | UNDECIDED | FREE | yes |

**0 of 10 rows disagree with the measurement. 0 rows come back `PRICED`.**

Three kills in the whole sealed table are lost to a removal:

| lost kill | reason |
|---|---|
| `corpus-port-swap:fake` on `SM-GM-P1` | `DETECTOR-REMOVED` |
| `port-binding-report` on `SM-GM-P2` | `DETECTOR-REMOVED` |
| `tests/test_port_adapter_binding.py::test_a_bound_port_the_manifest_declares_is_reported_as_declared` on `SM-GM-P2` | **`NODE-REMOVED`** |

and **zero** are `DETECTOR-WEAKENED`.

**Say this loudly and in the unflattering direction:** the shipped classifier
is right on all ten rows of the sealed record. Its unsoundness is real and the
record **does not exhibit it**, because the record contains no fault of the
weakening class. RM-01 had to construct one. A future round must not read §2 as
*"`discriminate` is usually wrong"* — a test asserts both halves so neither can
be quoted alone.

**And the re-priced removals came back at zero.** That is not the result the
ticket hoped for and it is the result.

---

## 5. WHAT I REJECTED

Every one of these would have improved a number.

1. **Reading `RM-01-RF-1`'s `SURVIVES` as the price of the whole SM-03
   removal.** It is the price of **one fault** on **three named paths**. SM-03
   also closed `SM-GM-I3` and `SM-GM-I1`, both of which went `SURVIVES` →
   `DIES`. The removal was a net strengthening with a narrow measured cost, and
   a headline saying *"SM-03 cost something"* without that sentence would be
   this project's own recurring error (`R-H2`, `SM-05-DF-01`).
2. **Restoring the `required` literal.** It would make `RM-01-RF-1` die again
   and give me a repair to report beside the finding. Declined: the shape was
   rejected twice on the record for a reason that still holds — a literal
   edited by the same person who forgot to register the instrument is a second
   thing to forget — and `measurement_rule` forbids fixing during a
   measurement. Filed as `RM-01-DF-03` and escalated, because the repair
   decision binds RM-03.
3. **Seeding the `fake =` fault to claim the famous exclusion had been
   defeated.** It is the single most quotable thing available to this ticket.
   Measured on the merits instead: once re-runnability is dropped the exclusion
   no longer applies, and the fault **still** does not price, because the
   `[ports.*]` table, `--wiring fake` and `render_oracle_statement`'s port half
   were deleted **together**. The fault class is **EXTINCT**, not **UNWATCHED**.
   Recorded in `residual_faults.toml`'s `[[not_seedable]]` row and filed as
   `RM-01-DF-04`. **P6 held, and it means the charter's marquee example would
   have priced at zero anyway.**
4. **Choosing detectors that would not have caught `RM-01-RF-1`.** The cheap
   run is `registry-enumeration` alone — one node, seconds. `pytest-full` was
   run **whole at both trees** precisely because the claim *"nothing else
   catches it"* is the claim the price rests on, and the 1300-node suite is
   where a counterexample would have been.
5. **Quietly fixing the probe's confound.** Both runs are committed and a test
   asserts the confounded one is there.
6. **Classifying `price_removal.py` as "product" rather than "proof"** to
   improve §6's ratio. `PREDICTIONS-RM-01.md` §P7 sealed the temptation before
   it arrived. Declined; §6 has one classification and it is the unflattering
   one.
7. **Editing `discriminating()` in place.** It is RD-02's instrument in a file
   this ticket does not own, and editing a target during a measurement is the
   thing `measurement_rule` names. The sound reading ships **beside** it, with
   the unsound one still running and visible, so the disagreement is
   inspectable rather than asserted.

---

## 6. WHAT RM-01 COST, IN THE CURRENCY IT ASKS OF EVERYONE ELSE

`denominator_rule`, and no total across removals.

```
$ git diff --numstat 2c0d94e..HEAD
```

<!--COST-->

**RM-01 removes nothing.** It is an instrument ticket, and every line of it is
in the *proof* column by the census's own definition — lines whose only job is
to show what a removal did. There is no denominator, so there is no ratio, and
`—` is the honest cell exactly as it was for `SM-03`.

**P7, sealed before the work: *"I predict RM-01 adds more lines than any
removal it prices, and I predict I will be tempted to classify my own
instrument as product rather than proof."*** Both held. RD-02's own ticket was
`+1403 / −33`; this one deletes **zero**.

`SUBTRACT-TO-MEASURE` was net `+1677` and called itself the great
simplification. This ticket is the same shape and is not calling itself
anything.

---

## 7. HOW THE PREDICTIONS CAME OUT

Sealed at `2c0d94e` in `PREDICTIONS-RM-01.md`, before any number existed.

| | prediction | outcome |
|---|---|---|
| **P1** | the shortcut is unsound; a real fault exists that it calls entailed and that goes `DIES`→`SURVIVES` | **HELD** — `RM-01-RF-1` |
| **P2** | `RM-01-RF-1` dies at `bf0fb29~1`, survives at `bf0fb29`, and `pytest-full` catches it at neither | <!--P2--> |
| **P3** | node granularity still gives 0 of 9 | **HELD** — exactly one node lost, `SM-GM-P2` still dies |
| **P4** | `SM-04-GM-T1` reproduces from an independent implementation | **HELD** |
| **P5** | at least one cell in the record where survivorship predicts DIES and measurement says SURVIVES | **FALSIFIED.** Zero. The shipped classifier is right on all ten published rows; the record contains no fault of the weakening class. The counterexample had to be built. Second half held: no cell where survivorship predicts SURVIVES and measurement says DIES. |
| **P6** | the `fake =` fault is EXTINCT, not UNWATCHED, and would have priced zero anyway | **HELD** — §5.3 |
| **P7** | RM-01 is net-additive and I will be tempted to reclassify my own lines | **HELD** — §6 |

**Two of seven falsified or partly falsified.** The standing rule says an
alarm is every prediction passing; this round did not clear that bar cleanly,
and **P5 is the one that matters**, because it is the prediction that would
have let me report `discriminate` as broadly wrong.

---

## 8. `scope` OVER MY OWN WRITING (R3), AND WHICH BOUND APPLIES

R3 binds this ticket. I ran it and **it refused nothing, because it cannot see
any of this document.**

```
$ python3 examples/validation/scorecards/score_tools.py scope --path RESULT.md
0 counted figure(s): 0 REFUTED, 0 COUNT-MOVED, 0 HOLDS, 0 UNREACHABLE
```

This document carries at least a dozen counted figures — *0 of 9*, *5 of 9*,
*0 of 10*, *3 of the 13*, *two of seven*, *0 of 4 rows disagree* — and the
check reports it contains **none**. Not refused, and not `UNREACHABLE` either,
which is the count that exists so a claim the checker cannot reach is not
mistaken for one that holds.

**The bound that applies is the first one: `RD-02-DF-01`.** `scope` is keyed on
`\bD[1-5]\b`, so a counted figure that does not name a dimension is invisible
to it. Demonstrated rather than inferred — `scope-probe.md`, four lines:

| line | reached? |
|---|---|
| `D2 = 2 on 27 of 27 cards ever written.` | **REFUTED**, with counterexamples named |
| `0 of 9 catalogue mutants could have priced a removal.` | invisible |
| `3 of the 13 required paths lie outside the derived roots.` | invisible |
| `0 of 10 published rows disagree with the measurement.` | invisible |

`1 counted figure(s)` out of four.

**The other two bounds do not apply here.** `RD-04-DF-01`, the ≤3-word
qualifier window, cannot fire on a document with zero reached figures.
`RD-05` §7.1 — the checker cannot tell a claim from a *mention* of a claim —
would be live if anything here were reached, because §7 and this section both
**quote** `D2 = 2 on 27 of 27` in order to talk about it; it is not reached, so
it does not fire, and that is a coincidence of bound 1 rather than a property
of the writing.

**I am not fixing it.** It is RD-01's instrument, this is a measurement ticket,
and `RD-02-DF-01` is already open against exactly this.

---

## 9. SUITE NUMBERS, EACH WITH ITS TREE

`RD-01-DF-02`: *"the suite is green" has never been true in a ticket
worktree* — `test_card_has_one_home.py` and `test_code_complexity.py` walk the
gitignored `.claude/` and `.skill-manager/` homes that `wt new` itself creates.
**No number below is reported as green.**

<!--SUITE-->

**And the standing warning:** the `git archive` figures below, where present,
are **not tree properties**. Those trees have no `.git`, and the tests that
read git history fail there for that reason alone. Nine of ten historical
"archive failures" were exactly this.

---

## 10. FINDINGS FILED, NONE FIXED

Budget 5, spent 4. One is **blocking** and is escalated because the decision it
forces binds `RM-03`.

| id | severity | finding |
|---|---|---|
| `RM-01-DF-01` | **blocking** | `discriminate` is unsound in the direction it is used: a surviving detector NAME is not a surviving kill. Demonstrated on a real removal. **If RM-03 prices its cuts from `discriminate`, every removal prices zero again.** |
| `RM-01-DF-02` | major | `run_gap_mutants.py` crashes at report-writing time on a relative `--catalogue` and discards a completed measurement. It cost this ticket one full staged `pytest-full` pass. |
| `RM-01-DF-03` | major | SM-03's derived enumeration is **narrower than what it replaced** on three named paths, and the gap is live today. Do NOT repair by restoring the literal. |
| `RM-01-DF-04` | minor | `[[not_seedable]]` conflates EXTINCT / UNWATCHED / UNMEASURABLE / NO-GAP under one heading. Only UNWATCHED is a price. |

**Nothing was fixed.** `discriminating()` still ships unchanged and still
reports `NON-DISCRIMINATING` about a fault that was measured to cost something.

---

## 11. REPRODUCE

```bash
# the sealed record, shipped classifier against measurement -- no new runs
python3 examples/validation/gap_mutants/price_removal.py audit

# the price of SM-03's removal, from the two measured tables
python3 examples/validation/gap_mutants/price_removal.py price \
  --removal hardcoded-enumeration-literal --head bf0fb29 \
  --before  specs/results/scorecards/portable-substrate/GOAL-removal-can-be-priced/RM-01/residual-before-bf0fb29p.json \
  --after   specs/results/scorecards/portable-substrate/GOAL-removal-can-be-priced/RM-01/residual-after-bf0fb29.json

# and what the before-table alone is entitled to conclude
python3 examples/validation/gap_mutants/price_removal.py entail \
  --removal hardcoded-enumeration-literal --head bf0fb29 \
  --before  specs/results/scorecards/portable-substrate/GOAL-removal-can-be-priced/RM-01/residual-before-bf0fb29p.json

# the measurement itself -- ABSOLUTE --catalogue, see RM-01-DF-02
python3 "$PWD/examples/validation/gap_mutants/run_gap_mutants.py" \
  --catalogue "$PWD/examples/validation/gap_mutants/residual_faults.toml" \
  --family staged --ref 'bf0fb29~1' --out /tmp/before.json

# the known positive
git archive 6aac1ec | tar -x -C /tmp/after-tree
python3 examples/validation/gap_mutants/altered_score_probe.py --tree /tmp/after-tree
```
