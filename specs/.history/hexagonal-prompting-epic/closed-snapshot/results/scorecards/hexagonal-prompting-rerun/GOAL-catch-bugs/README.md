# GOAL-catch-bugs — the run record, on the REPAIRED instrument

**Both controls are GREEN on both arms — and, CORRECTED IN PLACE by this
round's adversarial channel (F1, SEVERE), that sentence means two different
things on the two arms.**

> On **arm A** the positive control works: delete every `Reserve` case from the
> corpus — reproducing HP-06's exact regression — and M07 goes SURVIVED, the
> control goes red, and the run is refused. **On arm B it stays green through
> the identical regression**, because arm B's declared broader-reach substitute
> inflates a computation that runs on every read and is therefore killed by
> `CloseTenant` cases on a state with no live reservation at all.
>
> So: **arm A's whole-view rows are backed by a control demonstrated to fail
> when its failure mode returns. Arm B's are not.** Filed as
> **EVAL-RERUN-DF-03**, not fixed. The first draft of this file said "both
> controls are GREEN on both arms … it is the only reason anything else on this
> page is citeable", full stop. That was too strong and an agent asked to break
> it broke it.

- **Positive control `M07`** — killed by every instrument that can execute the
  action it lives in; `NOT_DECIDABLE` on the two that cannot, each with a
  declared witness.

  **CORRECTED (adversarial F3, SEVERE).** "each with a witness the driver
  verified against this run's own executability counts" is FALSE for the
  `corpus-slice-led` cell on both arms. `verify_limitation` reads
  `counts.get(key, 0)`, and that instrument's control block has no `Reserve` key
  at all — the zero is the ABSENCE of a count, not a measured one. On arm B that
  is the only limitation declared, so **100% of arm B's declared limitations are
  "verified" by a missing key.** Worse, its stated cause — "it cannot execute
  the mutated line" — is false on arm B: regenerate the same slice with
  `available` in the projector and M07 dies. The only operative constraint there
  is the projection. Filed as **EVAL-RERUN-DF-04**, not fixed.
- **Negative control `N01`** — survives all seven instruments on both arms, with
  a **reality witness** run against the unmutated and the mutated tree that
  separates them. "Survived" here is not silently "equivalent mutant".
- **`M09` is RETIRED**, for the reason `examples/validation/ab/eval/controls.toml`
  gives in full: it reverses a *sequence* and this model's ledger *is* one. It
  still runs and is still scored in the `ordering` row. It decides nothing.

**And the mechanism that produces a `NOT_DECIDABLE` cell is a suppression key
the project's own tripwire does not scan for (adversarial F2, SEVERE).** The
driver decides `NOT_DECIDABLE` BEFORE consulting the mutated run and never
checks whether the cell it suppresses would have been `KILLED`. The channel
demonstrated it twice on this round's own data: copying arm A's `corpus-neg`
limitation onto arm B turns a demonstrated KILL into `NOT_DECIDABLE` with
`verified: true`, `green: true`, exit 0 and no trace that a kill was discarded;
and a witness naming an action that appears nowhere in the model also
"verifies", erasing two genuine kills and collapsing a class denominator to
`0 of 0`. `scripts/kill_test.py`'s 19 `SUPPRESSION_KEYS` do not include
`limitation`, `witness_ran_must_be` or `not_decidable`, and `run_controls.py`
never invokes that scan. **This is a defect in the SHIPPED driver, so it applies
to the sealed reference run as well as to this one.** Filed as
**EVAL-RERUN-DF-02**, not fixed.

## Executable cases, per instrument, per action — printed beside every kill

A `SURVIVED` cell over an action that never executed is not evidence. These are
the counts from each run's own control pass on unmutated code, and they are
**identical on both arms**.

| instrument | cases | executed | skipped | Reserve (accepting) | Commit | Release | CloseTenant | Refuse* |
|---|---|---|---|---|---|---|---|---|
| `corpus-whole` | 43,128 | **3,734 (8.66%)** | 39,394 | 294 (294) | 784 | 784 | 1,872 | **0 of 39,100** |
| `corpus-neg` | 118 | 94 (79.7%) | 24 | 64 (**0**) | 4 | 4 | 22 | n/a |
| `corpus-slice-res` | 2,438 | 320 (13.1%) | 2,118 | 100 (100) | — | 220 | — | 0 of 2,018 |
| `corpus-slice-led` | 56 | 10 (17.9%) | 46 | — | — | — | 10 | 0 of 46 |
| `map-silent` | 43,128 | 3,734 (8.66%) | 39,394 | 294 (294) | 784 | 784 | 1,872 | 0 of 39,100 |
| `map-checking` | 43,128 | 3,734 (8.66%) | 39,394 | 294 (294) | 784 | 784 | 1,872 | 0 of 39,100 |
| `suite` | 28 tests | 28 | 0 | — | — | — | — | — |

Two structural limits, counted rather than described:

1. **39,100 refusal edges carry no arguments.** The model spells refusals out as
   first-class actions (`RefuseReserveOverQuota` and six siblings) whose
   parameters appear nowhere in their bodies, so no recovery mechanism can
   recover an argument the state pair does not contain. There is no call to
   make. **90.7% of the whole-view corpus, zero executable cases** — while the
   negative-corpus generator produces the same refusals as 118 cases of which 94
   execute.
2. **294 of 588 `Reserve` cases are structurally unreachable** — half, and the
   half is a coincidence.

   **CORRECTED IN PLACE (adversarial F4).** The stated cause — "a case naming a
   different id" — is right for **28 of the 294 (9.5%)** and wrong for the other
   **266**. For those, the id the API would allocate next is `r3`, **outside the
   model's `ResIds = {r1, r2}` entirely**, so no choice of `r` could ever have
   been expressible. The real mismatch is that the model allocates ids in any
   order from a finite recycled domain while the API allocates a monotone
   prefix: **the before-state, not the argument, is what the API cannot reach.**
   And "exactly half" is a function of `|ResIds| = 2`, not a property of the
   refinement — it is two sub-populations landing on symmetric splits for
   different reasons.

   The skips are still counted under a named rule and still never netted out of
   anything, and the rejected repair still stands: installing the id counter
   from the case's own `r` would configure the program to produce the id the
   oracle then compares.

3. **252 executed cases (6.7%) run from before-states the API can never reach,
   and are NOT counted** — `Commit` 44, `Release` 44, `CloseTenant` 164
   (adversarial F5). The runs are legal; the accounting is not symmetric. This
   round declares the same refinement gap as a counted, per-action,
   never-netted-out limitation on `Reserve` and is silent about it on three
   other actions. Filed, not fixed.

**A clarification a previous round's evidence packet omitted, and a judge
correctly called the omission a contradiction (HP-06-DF-04).** Live reservations
are INSTALLED into the before-state by the harness, not built by calling
`reserve`. An instrument can therefore execute cases that need a live
reservation while executing few or no ACCEPTED `reserve` calls. Both statements
are true together. This round's packets say so; HP-06's did not, and that is a
**difference between the two rounds' packets**, not only between their
instruments. Any D1 comparison across the rounds carries it.

## The tables

Re-anchored: **10 of 10 sealed mutants on BOTH arms**, plus `N01`. Integrity
re-proved per arm with the shipped harness — every pattern exactly once, revert
byte-identical, every mutant parses, every required class and gap seeded
(`measure/catalogue-integrity-arm-{a,b}.txt`, both **EXIT 0**).

`seeded_by` says how the diff had to be written. It is a fact about the diff.

### Arm A — the ordinary implementation ask

| mutant | class | seeded_by | corpus-whole | corpus-neg | slice-res | slice-led | map-silent | map-checking | suite |
|---|---|---|---|---|---|---|---|---|---|
| M01-guard-zero-amount | guard_relaxation | perturbation | SURVIVED | **KILLED** | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED |
| M02-guard-over-quota | guard_relaxation | perturbation | SURVIVED | **KILLED** | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED |
| M03-guard-close-with-outstanding | guard_relaxation | perturbation | SURVIVED | **KILLED** | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED |
| M04-durable-stale-total | durable_content | perturbation | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | **KILLED** | KILLED |
| M05-durable-close-line-zero | durable_content | perturbation | KILLED | SURVIVED | SURVIVED | SURVIVED | KILLED | KILLED | KILLED |
| M06-wrong-status-on-release | output_oracle | perturbation | KILLED | SURVIVED | KILLED | SURVIVED | KILLED | KILLED | KILLED |
| M07-positive-control | wrong_value | perturbation | KILLED | *NOT_DECIDABLE* | KILLED | *NOT_DECIDABLE* | KILLED | KILLED | KILLED |
| M08-cross-aspect | cross_aspect | perturbation | KILLED | SURVIVED | SURVIVED | SURVIVED | KILLED | KILLED | KILLED |
| M09-ordering (retired) | ordering | perturbation | KILLED | SURVIVED | SURVIVED | KILLED | KILLED | KILLED | KILLED |
| M10-apply-only-double-refund | wrong_value | perturbation | KILLED | SURVIVED | KILLED | SURVIVED | KILLED | KILLED | KILLED |
| **N01-negative-control** | ordering | perturbation | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | **SURVIVED** |

### Arm B — the hexagonal + minimize-complexity ask

| mutant | class | seeded_by | corpus-whole | corpus-neg | slice-res | slice-led | map-silent | map-checking | suite |
|---|---|---|---|---|---|---|---|---|---|
| M01-guard-zero-amount | guard_relaxation | perturbation | SURVIVED | **KILLED** | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED |
| M02-guard-over-quota | guard_relaxation | perturbation | SURVIVED | **KILLED** | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED |
| M03-guard-close-with-outstanding | guard_relaxation | perturbation | SURVIVED | **KILLED** | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED |
| M04-durable-stale-total | durable_content | perturbation | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | **KILLED** | KILLED |
| M05-durable-close-line-zero | durable_content | perturbation | KILLED | SURVIVED | SURVIVED | SURVIVED | KILLED | KILLED | KILLED |
| M06-wrong-status-on-release | output_oracle | perturbation | KILLED | SURVIVED | KILLED | SURVIVED | KILLED | KILLED | KILLED |
| M07-positive-control | wrong_value | perturbation (**broader-reach substitute**) | KILLED | KILLED | KILLED | *NOT_DECIDABLE* | KILLED | KILLED | KILLED |
| M08-cross-aspect | cross_aspect | **addition** | KILLED | SURVIVED | SURVIVED | SURVIVED | KILLED | KILLED | KILLED |
| M09-ordering (retired) | ordering | perturbation | KILLED | SURVIVED | SURVIVED | KILLED | KILLED | KILLED | KILLED |
| M10-apply-only-double-refund | wrong_value | **addition** | KILLED | SURVIVED | KILLED | SURVIVED | KILLED | KILLED | KILLED |
| **N01-negative-control** | ordering | perturbation | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | **SURVIVED** |

### The arms differ on ONE cell out of 77, and it is the cell declared incomparable

`M07 / corpus-neg`: `NOT_DECIDABLE` on arm A, `KILLED` on arm B. That is not the
same mutant. Arm A's M07 inflates the STORED deduction inside `reserve`, so it
is reachable only through an accepted reserve, and the negative corpus executes
**64 `Reserve` cases of which 0 are accepting**. Arm B stores no reservations-
side quantity at all, so the nearest available seeding inflates the COMPUTATION
of the held total, which is observable after any command including a refusal.
The substitution is declared in `measure/catalogue_arm_b.toml` and the arm-A
limitation is declared and witness-verified in `measure/controls_arm_a.toml`.

**CORRECTED IN PLACE (adversarial F6).** The first draft said "76 comparable
cells". By this round's own rule that is too many: `catalogue_arm_b.toml` says
M07's arm-A and arm-B **cells** — plural, all seven — are not the same
experiment, and M08 and M10 are seeded by ADDITION rather than perturbation, so
three of eleven rows are not the same diff. **Strictly comparable is 8 x 7 = 56
cells.**

**On all 56 strictly comparable cells the two arms are identical**, and on the
21 loosely comparable ones they differ only in M07's `corpus-neg` cell. A port,
a Protocol, a fake and a parity suite did not detect one additional fault under
either denominator. The conclusion survives the correction; the number quoted
for it did not.

## What HP-06 could not measure and this round can: the denominator

HP-06 dropped M08 and M10 from arm B's catalogue on the grounds that they could
not be seeded, reported "8 of 8", and then had to disown the number in its own
run record — *"arm B's 8 of 8 is produced by removing from the denominator the
two mutants arm B could not be made to fail"*. Its blind-author channel proved
the faults ARE seedable by ADDITION and that both die.

This round carries the correction into the instrument: **all ten are seeded on
both arms, with `seeded_by = "addition"` on the two that needed an invented
statement.** The corrected claim, now measured directly rather than inferred
from a second catalogue, is:

> **The asymmetry is in SEEDABILITY, not in KILLABILITY.** In arm A, M08 and M10
> are a one-operand slip in an existing line. In arm B they require inventing a
> statement that mutates the quota. Both die on exactly the same four
> instruments in both designs. **A kill-count table cannot show that difference
> at all** — which is why it is a column and not a sentence.

## Re-deriving the standing bar, rather than inheriting it

**The bar this project has quoted for two epics — "the generated corpus is still
worse than a suite a competent engineer writes in an afternoon" — does not
reproduce on this catalogue.**

**CORRECTED IN PLACE (adversarial F7).** The first draft added "and the reason
is the negative control." That is supported by no cell. N01 is SURVIVED in all
seven columns on both arms, so it adds 1 to every denominator and 0 to every
numerator: **delete it and the suite still ties the union, 10 to 10.** The tie
is produced by the union AGGREGATE, which this file itself calls forbidden two
paragraphs below and which no single generated instrument approaches. What N01
does change is how the OLD number reads — see point 1 — and that is a different
claim from the one the draft made.

| | arm A | arm B |
|---|---|---|
| **hand-written suite** | **10 of 11** | **10 of 11** |
| union of the six generated instruments | **10 of 11** | **10 of 11** |
| the single best generated instrument (`map-checking`) | 7 of 11 | 7 of 11 |
| mutants no instrument at all kills | **1** (`N01`) | **1** (`N01`) |

Three things must be said in the same breath, and the first is the one that
changes how the older number reads:

1. **`N01` survives the hand-written suite too.** The suite asserts
   `outstanding_ids() == ["r1"]` — one element, where ascending and descending
   are the same list — and its `snapshot()` helper compares a book against
   *itself* across a rejection, so a consistently reversed order matches. **The
   10-of-10 that set the bar rested on a catalogue containing no mutant that
   suite could miss.** Every citation of the bar now needs that clause.
2. **The union is the forbidden aggregate**, and the objection travels with it:
   `seeded_faults.toml`'s header says no aggregate kill rate may be computed
   from it, "union" is a max over six columns of which `map-silent` is identical
   to `corpus-whole` on every cell by construction, and no single generated
   instrument reaches 10. It is computed only because HP-01's fixture README and
   this brief both require the generator-versus-suite comparison to be stated in
   those words.
3. **Instrument for instrument, the suite still wins comfortably: 10 against 7.**
   The tie exists only when six generated instruments are unioned against one
   hand-written file. Read the per-class table, not the union.

## Which instrument saw which class — the only quantity worth reporting

Identical on both arms except the `wrong_value` row, which contains M07.

| class | corpus-whole | corpus-neg | slice-res | slice-led | map-silent | map-checking | suite |
|---|---|---|---|---|---|---|---|
| guard_relaxation (3) | **0 of 3** | **3 of 3** | 0 of 3 | 0 of 3 | 0 of 3 | 0 of 3 | 3 of 3 |
| durable_content (2) | 1 of 2 | 0 of 2 | 0 of 2 | 0 of 2 | 1 of 2 | **2 of 2** | 2 of 2 |
| cross_aspect (1) | 1 of 1 | 0 of 1 | **0 of 1** | **0 of 1** | 1 of 1 | 1 of 1 | 1 of 1 |
| output_oracle (1) | 1 of 1 | 0 of 1 | 1 of 1 | 0 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| ordering (2: M09 retired + N01) | 1 of 2 | 0 of 2 | 0 of 2 | 1 of 2 | 1 of 2 | 1 of 2 | **1 of 2** |
| wrong_value — arm A (2) | 2 of 2 | 0 of 1 (1 ND) | 2 of 2 | 0 of 1 (1 ND) | 2 of 2 | 2 of 2 | 2 of 2 |
| wrong_value — arm B (2) | 2 of 2 | **1 of 2** | 2 of 2 | 0 of 1 (1 ND) | 2 of 2 | 2 of 2 | 2 of 2 |

* **Guard relaxation is 3 of 3 under `corpus-neg` and 0 of 3 under every other
  generated instrument, on both arms.** HP-03's headline reproduces on two fresh
  implementations. The framing correction from HP-06 (finding F1) still applies
  and is not retracted: the zeros in the other columns are **not** evidence that
  "a corpus cannot see refusals". This model spells refusals out as actions and
  the corpus contains 39,688 refusal cases; the oracle executes none of them,
  because they carry no arguments. The correct statement is the narrow one.
* **The mapping is worth exactly one mutant** (M04), on both arms, for the
  seventh fixture running. The *direction* replicates; the "30% of the
  instrument's yield" *magnitude* fails to reproduce for the fifth time and must
  never be quoted as a property of the mechanism.
* **Ordering is not invisible to corpora when the modelled thing is a sequence**
  (M09 dies under four instruments) **and is invisible when it is a set** (N01
  survives all seven). That is the retraction and its correct clause, measured on
  the same fixture in the same run — which is the first time the two halves have
  been demonstrated side by side.
* **The aspect slices lost what they were declared to be lost by**: M08 dies
  under the whole view and survives both slices, on both arms.

## Determinism — full coverage this time

Two complete runs of **all seven instruments on BOTH arms** are byte-identical:
per-action counts, skip rules, retained failure text and case order included.

**CORRECTED IN PLACE (adversarial F9, F10).** The first draft said the stored
pairs differ only in the `--label` string; in fact the labels were normalised
when the files were copied into this tree, so **the shipped pair is same-label
byte-identical and is therefore indistinguishable from a `cp`.** And
`reference-run.json` is *not* byte-identical to
`examples/validation/ab/eval/results/final-run-1.json` — it differs in `label`;
`per_mutant`, `controls_on_unmutated_code` and `evidence` are equal. That is the
same class of over-claim as HP-06-DF-09, which this file says it closed.

**The claim itself survives independently**: the adversarial channel regenerated
all four corpora from the `.tla` and re-ran `run_controls.py` end to end on both
arms, and reported "identical modulo label: True" for `per_mutant`,
`controls_on_unmutated_code`, `evidence`, `per_class` and `reality_witnesses`.
That reproduction, not the stored pair, is what carries determinism this round.

HP-06's determinism claim covered 2 of 6 instruments on 1 of 2 arms and was
corrected in place as an over-claim (HP-06-DF-09). **That defect is closed on
measurement**, and the reference tree's run reproduces
`examples/validation/ab/eval/results/final-run-1.json` byte-for-byte as well.

Files: `determinism-arm-{a,b}-run-2.json`, `reference-run.json`.

## A defect this round found in its own harness, filed and disclosed

**EVAL-RERUN-DF-01 — a stale module reference made every mutant survive.** The
driver purges `quota_ledger*` and a **fixed list** of binding module names
between mutants. This round's bindings are not on that list, so a module-level
`_impl = import_module("quota_ledger")` captured the PRISTINE tree once and every
mutant was then executed against unmutated code.

The first arm-A run is kept as `kill-table-arm-a-STALE-BINDING-DF-01.json`: **11
of 11 mutants SURVIVED all six generated instruments, with green controls**,
while the `suite` column killed 10 of 11. It was that disagreement between two
columns of the same table that exposed it — the exact use
`references/eval_scorecard.md` rule 7 puts a mechanical block beside a judgement
for.

The binding now looks the tree up on every call; the disclosure is in the
binding's own docstring. **The fix is to this round's binding, which is part of
the harness being built, not to the instrument under measurement** — no mutant
was re-seeded, no instrument re-run until a number improved, and the broken run
is published beside the good one.

Two things this should be read as saying about every kill table this project has
published: a green control did not catch it, and it would have been invisible
without a hand-written instrument in the same table to disagree with.

## Reproducing

```bash
# the four corpora (write outside the repo; the whole-view one is 66 MB)
python3 scripts/tla_spec_dev.py --spec-root specs generate cases \
  examples/validation/ab/model/QuotaLedger.tla examples/validation/ab/model/QuotaLedger.cfg \
  --out <scratch>/specs/corpus-whole --package quota_whole --view internal
#   ... --negative-cases only into corpus-neg, and the two Aspect_*.tla slices
#   with --module-path examples/validation/ab/model and
#   --state-projector aspect_projectors:project_reservations / project_ledger
#   (specs/results/scorecards/hexagonal-prompting/measure/, unchanged)

# integrity, per arm
python3 examples/validation/ab/check_catalogue.py \
  --root specs/results/scorecards/hexagonal-prompting-rerun/arms/arm_a \
  --catalogue specs/results/scorecards/hexagonal-prompting-rerun/measure/catalogue_arm_a.toml

# the table, per arm
PYTHONPATH=$PWD/specs/results/scorecards/hexagonal-prompting-rerun/measure \
python3 examples/validation/ab/eval/run_controls.py --label EVAL-RERUN-arm-A \
  --tree specs/results/scorecards/hexagonal-prompting-rerun/arms/arm_a --module-dir . \
  --binding rerun_arm_a_binding \
  --catalogue specs/results/scorecards/hexagonal-prompting-rerun/measure/catalogue_arm_a.toml \
  --catalogue specs/results/scorecards/hexagonal-prompting-rerun/measure/controls_arm_a.toml \
  --instrument corpus-whole=<scratch>/specs/corpus-whole/spec-unit/quota_whole \
  --instrument corpus-neg=<scratch>/specs/corpus-neg/spec-unit/quota_neg \
  --instrument corpus-slice-res=<scratch>/specs/corpus-slice-res/spec-unit/quota_slice_res \
  --instrument corpus-slice-led=<scratch>/specs/corpus-slice-led/spec-unit/quota_slice_led \
  --instrument map-silent=<scratch>/specs/corpus-whole/spec-unit/quota_whole:silent \
  --instrument map-checking=<scratch>/specs/corpus-whole/spec-unit/quota_whole:checking \
  --suite examples/validation/ab/tests/test_behavior.py --out <out>.json
```

## Not seeded, therefore not measured

* **Concurrency** — the specification declares none.
* **Cross-process effects** — the effect oracle is in-process CPython only, so a
  mutant there is dead on arrival.

Recorded as *not seeded*, never as *not caught*.

## The fresh, independently authored catalogue

An agent that had never seen `seeded_faults.toml`, this round's catalogues, or
any result authored **15 mutants per arm** from the two implementations, the
specification, the model and the shared suite. It proved each pattern occurs
exactly once with byte-identical revert, and — the part that matters — proved
**every** mutant separates the clean tree from the mutated one, dropping the
ones it could not and recording them in `REJECTED.md`. **Zero equivalent mutants
shipped.** Deliberately, it used the **same fifteen classes in the same order**
on both arms, holding `semantic` equal, so that a per-arm score compares two
implementations rather than two catalogues. It flagged the two rows where that
was impossible.

Run through the same seven instruments, controls green on both arms:

| | arm A | arm B |
|---|---|---|
| union of the six generated instruments | **11 of 15** | **10 of 15** |
| hand-written suite | **11 of 15** | **10 of 15** |
| invisible to EVERY instrument, suite included | **3** | **4** |

**The generated corpora tie the hand-written suite on a catalogue nobody
tuned**, on both arms — against HP-06's 8 of 13 versus 9 of 13. Both are far
below the seeded catalogue's 10 of 11, which reproduces the standing result that
**a catalogue written by the author of the mechanisms flatters both instruments
by roughly a quarter.**

**`corpus-neg` earns its keep three times over on a blind catalogue.** Three
mutants die to it and to nothing else generated: `guard_relaxation`,
`guard_basis_confusion` and (on arm A) `rejection_not_inert` — a refused call
that permanently damages state nobody diffs across a rejection. That is the
class R4 is actually about, and it is the second round running in which the
negative corpus caught it without anyone claiming it would.

**Invisible to everything, including the suite** — `guard_order_inversion` (a
call that trips two guards at once reports the wrong one),
`observation_order_violation` (order goes wrong only past ten live ids, and
`ResIds` caps the model at two), `construction_not_empty` (a ledger constructed
over an existing file inherits its lines), and on arm B `rejection_not_inert`.
Nothing in this fixture can see any of them.

**And the two cells where the arms differ are exactly the two rows the author
declared non-parallel** (`BA-*07` and `BA-*12`, both flagged "NOT byte-parallel"
in the catalogue because the designs differ). **Where the mutants are the same,
the arms are identical; where the arms differ, the catalogue differs.** That is
a cleaner statement of the round's central negative result than the sealed
catalogue can make.

Full record: `../channels/blind-author/`,
`kill-table-blind-author-arm-{a,b}.json`.
