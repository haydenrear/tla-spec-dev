# GOAL-catch-bugs — the run record

**The instrument's positive control is RED on arm A. Read that first; it fixes
how every other number on this page must be read.**

`M07` is the catalogue's declared positive control. It is seeded in nobody's
gap, it is blatant, and it exists so that a table of zeros can be told apart
from a broken instrument. The sealed predictions say so in the strongest terms
available to them: *"If M07 survives, every other number in the round is void
and HP-06 reports the instrument as unciteable rather than reporting kills"*
(`examples/validation/PREDICTIONS-HP.md`, P05).

On arm A, **M07 survives every one of the six generated instruments** and dies
only to the hand-written suite. The cause is known and is not new: the whole-view
corpus recovers no argument for `Reserve` — the generator's own audit reports
`UNRECOVERABLE on this corpus: Reserve(a) -- 0 of 588 cases carry an argument` —
so no case that calls `reserve` ever executes, and a fault seeded inside
`reserve` cannot be reached. HP-05 recorded the same red control on the fixture's
reference implementation. This round reproduces it on a real arm.

So: **arm A's corpus kill counts on this page are a floor reported under a
broken instrument, not a clean kill measurement.** They are printed because
suppressing them would be worse, and because the `guard_relaxation` row is
carried by `corpus-neg`, a different instrument whose own controls are green.

On arm B, M07 dies. That is **not** evidence that arm B's instrument is sound —
it is an artifact of re-anchoring, and the next section is about that.

## The re-anchoring, and why the two arms' raw counts are not comparable

The sealed catalogue anchors on a reference implementation that is not an arm.
Each mutant declares a `semantic` in arm-independent terms, and HP-06 wrote
arm-specific find/replace producing that semantic, re-proving exactly-once per
arm with the shipped harness:

```
python3 examples/validation/ab/check_catalogue.py \
    --root specs/results/scorecards/hexagonal-prompting/arms/arm_a \
    --catalogue specs/results/scorecards/hexagonal-prompting/measure/catalogue_arm_a.toml
  -> 10 mutants, every pattern occurs exactly once, apply/revert byte-identical,
     every mutant parses, every class and gap seeded. EXIT 0.

python3 examples/validation/ab/check_catalogue.py \
    --root specs/results/scorecards/hexagonal-prompting/arms/arm_b \
    --catalogue specs/results/scorecards/hexagonal-prompting/measure/catalogue_arm_b.toml
  -> 8 mutants. EXIT 1:
       no mutant in required class 'cross_aspect'
       no mutant declares a fault in the 'apply()-only' gap
```

That non-zero exit is the load-bearing evidence for the round's most interesting
structural result, and it was produced by the shipped harness rather than
asserted in prose.

**Three of the ten mutants do not exist on arm B.** All three are faults in
*maintaining a redundant stored count*, and arm B stores no such count —
`available` is computed from the committed totals and the live holds on every
read (`arms/arm_b/quota_ledger/domain.py:80` and `:149-154`). Arm A keeps `held` as a stored
counter that three commands mutate (`arms/arm_a/quota_ledger.py:77-90`, written at `:195`, `:216`), which is
an entirely ordinary design, and every one of the three seeds into it cleanly.

| mutant | arm A | arm B |
|---|---|---|
| M08 cross-aspect: commit refunds the hold | seeded | **NOT SEEDABLE by perturbing an existing statement** — see the correction below |
| M10 release credits back double | seeded | **NOT SEEDABLE by perturbing an existing statement** — see the correction below |
| M07 positive control: hold one too large | seeded, `held` counter inflated inside `reserve` | seeded with a **BROADER-REACH SUBSTITUTE** — the *computation* of the held total is inflated, so it is observable after any command rather than only after a reserve |

A not-seeded mutant is neither a kill nor a survival. **Arm B's evidence rests on
eight mutants where arm A's rests on ten, and M07 is not the same experiment on
the two arms. Raw kill counts between the arms must not be compared.**

Whether this is a point in arm B's favour is a judgement, not a measurement, and
this file does not make it.

### CORRECTION, from the blind-author channel, to the paragraph above

The first draft of this file said the three faults "cannot be written" against
arm B. **That was too strong, and an independent agent that had never seen this
catalogue proved it too strong.**

The blind author, working from the two implementations alone, reached the same
structural observation from scratch — arm B stores no reservations-side quantity,
so every *perturbation of an existing statement* pushes a symptom onto the ledger
aspect, and it printed the four candidates it tried and what each one broke. But
it then seeded the cross-aspect leak into arm B anyway, **by ADDING a
quota-inflating statement rather than changing one** (`BA-B05`), producing
exactly M08's declared observable: `available` inflated, `committed` correct,
every ledger line byte-correct. It died. Both arms score 1 of 1 on
`cross_aspect_leak` on its catalogue.

**So the corrected claim is: the asymmetry is in SEEDABILITY, not in
KILLABILITY.** In arm A the fault is a plausible one-operand slip; in arm B it
requires inventing a statement that mutates the quota. That is a real and
interesting difference in how likely the fault is to be written by a person, and
it is *not* the difference a kill-count table would show — the blind author said
so unprompted: "a kill-count table would hide it entirely."

HP-06's own catalogue was **not** re-seeded to add the arm-B variant. Adding a
mutant after seeing the results is fitting the catalogue to the run, and the
independent channel's measurement is the better evidence anyway. What is measured
here stands as: *on this feature, three of the ten sealed mutants have no
one-token form in one of the two designs.*

### And the cost side of the same structure, which nobody predicted

The blind author found the mirror image and it is arm B's alone: **`BA-B14`,
a fault in the in-memory journal adapter (`quota_ledger/journal_memory.py`),
survives every instrument including the hand-written suite.** Arm A has no
counterpart, because arm A has exactly one durable implementation and its
composition point is its constructor, so there is no code the shared contract
cannot reach.

The port removes places for some faults to live **and creates a region no shared
oracle can see**. The fake that earned arm B its D3 = 4 is itself unverified by
anything outside arm B's own tests.

## The fresh, independently authored catalogue

A second agent was given the two implementations, the specification, the model
and the shared suite, and was forbidden the sealed catalogue, HP-06's
re-anchored catalogues, and every HP-06 result. It authored **13 mutants for
arm A and 14 for arm B**, proved each pattern occurs exactly once with
byte-identical revert, and proved every survivor is a real defect rather than an
equivalent mutant. HP-06 re-keyed its file into the shipped parser's field names
and **changed no find/replace pair, id, class or description**, then ran it
through the same instruments.

### Arm A — 13 mutants authored blind

| mutant | class | corpus-whole | corpus-neg | map-checking | suite |
|---|---|---|---|---|---|
| BA-A01 | guard_relaxation | SURVIVED | KILLED | SURVIVED | KILLED |
| BA-A02 | outcome_misreport | SURVIVED | SURVIVED | SURVIVED | KILLED |
| BA-A03 | guard_order | SURVIVED | SURVIVED | SURVIVED | SURVIVED |
| BA-A04 | state_arithmetic | KILLED | SURVIVED | KILLED | KILLED |
| BA-A05 | cross_aspect_leak | KILLED | SURVIVED | KILLED | KILLED |
| BA-A06 | durable_content | SURVIVED | SURVIVED | KILLED | KILLED |
| BA-A07 | durable_cardinality | KILLED | SURVIVED | KILLED | KILLED |
| BA-A08 | durable_cardinality | KILLED | SURVIVED | KILLED | KILLED |
| BA-A09 | durable_extra_write | KILLED | SURVIVED | KILLED | KILLED |
| BA-A10 | id_allocation | SURVIVED | SURVIVED | SURVIVED | SURVIVED |
| BA-A11 | query_projection | SURVIVED | SURVIVED | SURVIVED | SURVIVED |
| BA-A12 | rejection_side_effect | SURVIVED | KILLED | SURVIVED | KILLED |
| BA-A13 | durable_encoding | SURVIVED | SURVIVED | SURVIVED | SURVIVED |

**Generated corpora, union: 8 of 13. Hand-written suite: 9 of 13.**
**Invisible to EVERY instrument including the suite (4): BA-A03 (guard_order), BA-A10 (id_allocation), BA-A11 (query_projection), BA-A13 (durable_encoding).**

### Arm B — 14 mutants authored blind

| mutant | class | corpus-whole | corpus-neg | map-checking | suite |
|---|---|---|---|---|---|
| BA-B01 | guard_relaxation | SURVIVED | KILLED | SURVIVED | KILLED |
| BA-B02 | outcome_misreport | SURVIVED | SURVIVED | SURVIVED | KILLED |
| BA-B03 | guard_order | SURVIVED | SURVIVED | SURVIVED | SURVIVED |
| BA-B04 | memory_ledger_divergence | KILLED | SURVIVED | KILLED | KILLED |
| BA-B05 | cross_aspect_leak | KILLED | SURVIVED | KILLED | KILLED |
| BA-B06 | durable_content | SURVIVED | SURVIVED | KILLED | KILLED |
| BA-B07 | durable_cardinality | KILLED | SURVIVED | KILLED | KILLED |
| BA-B08 | durable_cardinality | KILLED | SURVIVED | KILLED | KILLED |
| BA-B09 | durable_extra_write | KILLED | SURVIVED | KILLED | KILLED |
| BA-B10 | id_allocation | SURVIVED | SURVIVED | SURVIVED | SURVIVED |
| BA-B11 | query_projection | SURVIVED | SURVIVED | SURVIVED | SURVIVED |
| BA-B12 | rejection_side_effect | SURVIVED | KILLED | SURVIVED | KILLED |
| BA-B13 | durable_encoding | SURVIVED | SURVIVED | SURVIVED | SURVIVED |
| BA-B14 | unwired_adapter | SURVIVED | SURVIVED | SURVIVED | SURVIVED |

**Generated corpora, union: 8 of 14. Hand-written suite: 9 of 14.**
**Invisible to EVERY instrument including the suite (5): BA-B03 (guard_order), BA-B10 (id_allocation), BA-B11 (query_projection), BA-B13 (durable_encoding), BA-B14 (unwired_adapter).**


### What this catalogue says that the seeded one cannot

**It is markedly less flattering, and that is its value.** The seeded catalogue
was written by the author of the mechanisms; this one was not.

* **Guard relaxation moves off zero on a fresh blind catalogue too: 1 of 1 under
  `corpus-neg`, 0 of 1 under `corpus-whole` and `map-checking`, on both arms.**
  This is the clause `GOAL-catch-bugs`'s target names and it is now carried by a
  catalogue nobody tuned.
* **A SECOND class only the negative corpus sees, and nobody predicted it.**
  `rejection_side_effect` — a rejected call that performs a durable write — is
  1 of 1 under `corpus-neg` and 0 of 1 under every other generated instrument, on
  both arms. HP-03 built the negative corpus for guard relaxation; it also caught
  the class R4 is actually about. That is capability the epic did not claim.
* **Four whole classes are invisible to EVERY instrument, the hand-written suite
  included**: `guard_order`, `id_allocation`, `query_projection`,
  `durable_encoding` — plus `unwired_adapter` on arm B. Nothing in this fixture
  can currently see any of them.
* **The generated corpora reach 8 of 13 where the suite reaches 9 of 13.** The
  gap is one mutant, the same shape as the seeded catalogue's — but both numbers
  are far below the seeded catalogue's 9 of 10 and 10 of 10. **A catalogue
  written by the mechanisms' author flatters both instruments.**

## The tables

### Arm A (control prompt)

Mutants re-anchored: **10 of 10**.

| mutant | class | corpus-whole | corpus-neg | corpus-slice-res | corpus-slice-led | map-silent | map-checking | suite |
|---|---|---|---|---|---|---|---|---|
| M01-guard-zero-amount | guard_relaxation | SURVIVED | KILLED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED |
| M02-guard-over-quota | guard_relaxation | SURVIVED | KILLED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED |
| M03-guard-close-with-outstanding | guard_relaxation | SURVIVED | KILLED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED |
| M04-durable-stale-total | durable_content | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED | KILLED |
| M05-durable-close-line-zero-and-swallowed | durable_content | KILLED | SURVIVED | SURVIVED | SURVIVED | KILLED | KILLED | KILLED |
| M08-cross-aspect-commit-refunds-the-hold | cross_aspect | KILLED | SURVIVED | SURVIVED | SURVIVED | KILLED | KILLED | KILLED |
| M06-wrong-status-on-release | output_oracle | KILLED | SURVIVED | KILLED | SURVIVED | KILLED | KILLED | KILLED |
| M10-apply-only-double-refund | wrong_value | KILLED | SURVIVED | KILLED | SURVIVED | KILLED | KILLED | KILLED |
| M07-positive-control-wrong-hold | wrong_value | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED |
| M09-negative-control-ledger-order | ordering | KILLED | SURVIVED | SURVIVED | KILLED | KILLED | KILLED | KILLED |

| class | corpus-whole | corpus-neg | corpus-slice-res | corpus-slice-led | map-silent | map-checking | suite |
|---|---|---|---|---|---|---|---|
| cross_aspect | 1 of 1 | 0 of 1 | 0 of 1 | 0 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| durable_content | 1 of 2 | 0 of 2 | 0 of 2 | 0 of 2 | 1 of 2 | 2 of 2 | 2 of 2 |
| guard_relaxation | 0 of 3 | 3 of 3 | 0 of 3 | 0 of 3 | 0 of 3 | 0 of 3 | 3 of 3 |
| ordering | 1 of 1 | 0 of 1 | 0 of 1 | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| output_oracle | 1 of 1 | 0 of 1 | 1 of 1 | 0 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| wrong_value | 1 of 2 | 0 of 2 | 1 of 2 | 0 of 2 | 1 of 2 | 1 of 2 | 2 of 2 |

**Union of every generated instrument (suite excluded): 9 of 10 re-anchored mutants.** Survivors: M07-positive-control-wrong-hold.
**The hand-written suite: 10 of 10.**

### Arm B (hexagonal + minimize-complexity prompt)

Mutants re-anchored: **8 of 10**.

| mutant | class | corpus-whole | corpus-neg | corpus-slice-res | corpus-slice-led | map-silent | map-checking | suite |
|---|---|---|---|---|---|---|---|---|
| M01-guard-zero-amount | guard_relaxation | SURVIVED | KILLED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED |
| M02-guard-over-quota | guard_relaxation | SURVIVED | KILLED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED |
| M03-guard-close-with-outstanding | guard_relaxation | SURVIVED | KILLED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED |
| M04-durable-stale-total | durable_content | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED | KILLED |
| M05-durable-close-line-zero-and-swallowed | durable_content | KILLED | SURVIVED | SURVIVED | SURVIVED | KILLED | KILLED | KILLED |
| M06-wrong-status-on-release | output_oracle | KILLED | SURVIVED | KILLED | SURVIVED | KILLED | KILLED | KILLED |
| M07-positive-control-wrong-hold | wrong_value | KILLED | KILLED | KILLED | SURVIVED | KILLED | KILLED | KILLED |
| M09-negative-control-ledger-order | ordering | KILLED | SURVIVED | SURVIVED | KILLED | KILLED | KILLED | KILLED |

| class | corpus-whole | corpus-neg | corpus-slice-res | corpus-slice-led | map-silent | map-checking | suite |
|---|---|---|---|---|---|---|---|
| durable_content | 1 of 2 | 0 of 2 | 0 of 2 | 0 of 2 | 1 of 2 | 2 of 2 | 2 of 2 |
| guard_relaxation | 0 of 3 | 3 of 3 | 0 of 3 | 0 of 3 | 0 of 3 | 0 of 3 | 3 of 3 |
| ordering | 1 of 1 | 0 of 1 | 0 of 1 | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| output_oracle | 1 of 1 | 0 of 1 | 1 of 1 | 0 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| wrong_value | 1 of 1 | 1 of 1 | 1 of 1 | 0 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |

**Union of every generated instrument (suite excluded): 8 of 8 re-anchored mutants.** No survivor.
**The hand-written suite: 8 of 8.**


## An aggregate this file computes that the catalogue forbids

> **RAISED BY HP-06's adversarial channel (finding F13), and left standing with
> the objection attached.** `seeded_faults.toml`'s header says: *"There is no
> aggregate kill rate in this catalogue and none may be computed from it: an
> average over classes whose whole point is that they behave differently is a
> number about nothing."* The "union of every generated instrument" lines above
> are exactly that aggregate.
>
> They are kept because HP-06's brief, HP-01's fixture README, HP-03's close note
> and HP-05's close note all require the generator-versus-suite comparison to be
> reported in those words, and it cannot be stated without one. Three further
> objections travel with it and are not answered:
>
> 1. **"Union" is a max over six columns, five of which are not independent.**
>    `map-silent` is identical to `corpus-whole` on **18 of 18 cells** across both
>    arms — by construction, since a silent provider asserts nothing (F3). No
>    single instrument scores 9 of 10.
> 2. **Arm B's 8 of 8 is produced by removing from the denominator the two
>    mutants arm B could not be made to fail** — the exact operation
>    `catalogue_arm_b.toml` promises not to perform.
> 3. The whole-view half of it sits under a red positive control.
>
> **Read the per-class table, not the union.**

## The comparison the round exists to make

**The hand-written suite kills 10 of 10 on arm A and 8 of 8 on arm B — every
mutant that could be seeded into either.** The union of all six generated
instruments reaches 9 of 10 on arm A, and the one survivor is the positive
control.

**On this fixture the generated corpus is still worse than a suite a competent
engineer writes in an afternoon.** That is the sentence HP-01 asked for and it
is unchanged in substance from HP-03's and HP-05's, one epic later: suite 10 of
10, corpora 9 of 10, and the missing mutant is the one that proves the
instrument works.

The *declared bias* travels with it, from the sealed catalogue: the 10 of 10 is
an upper bound, not typical. The suite was written before the catalogue but by
the same author who chose the fault classes.

## Which instrument saw which class — the only quantity that matters

* `guard_relaxation` is **3 of 3 under `corpus-neg` and 0 of 3 under every other
  generated instrument, on both arms.** This is the class that measured 0 of 3,
  0 of 3 and 0 of 4 across three catalogues, five instruments and two rounds of
  the predecessor epic, now reproduced on two real implementations rather than on
  a fixture reference. The controls for `corpus-neg` are green on both arms (94
  of 118 cases executed, 0 failures on the unmutated arm), and the adversarial
  channel traced all three kills independently and confirmed them as real
  measurements that do not depend on any of the oracle defects below.

  > **THE ZERO IN THE OTHER COLUMNS IS NOT WHAT THE SEALED CATALOGUE SAYS IT IS.**
  > HP-06's adversarial channel (finding F1, severity SEVERE). The sealed
  > catalogue explains the guard-relaxation zero as *"a generated corpus replays
  > only ENABLED edges, so it never once asks the program to refuse."* **On this
  > model that explanation does not apply.** `QuotaLedger.tla:144-158` models
  > refusals as first-class actions in `Next`, TLC emits real edges for them, and
  > the whole-view corpus therefore *does* contain refusal cases — 39,688 of its
  > 43,128. The shared oracle skips every one of them
  > (`measure/arm_adapter.py:276-278`, "a modeled refusal with no recoverable
  > argument"), so `corpus-whole`, `map-silent` and `map-checking` execute only
  > `Commit`, `Release` and `CloseTenant`.
  >
  > Reconciling it with what is already on the record: HP-03 measured *why* those
  > cases are unrunnable — the `Refuse*` actions take `(t, a, r)` and use none of
  > them in their bodies, so no recovery mechanism can recover an argument the
  > state pair does not contain, and all 39,100 of them carry `params={}`. There
  > is no call to make. So the corpus contains refusal **edges** and no refusal
  > **calls**.
  >
  > **What this makes uncitable:** every `guard_relaxation` cell under
  > `corpus-whole`, `map-silent` and `map-checking` as evidence for *"a corpus
  > cannot see refusals"*. The correct statement is narrower and is HP-03's own:
  > **spelling refusals out as explicit actions produces 90.7% of a corpus and
  > zero executable cases, while the negative-corpus generator produces the same
  > refusals as 118 executable ones.** The 3-of-3 stands; the framing of the
  > zeros beside it does not. Filed as **HP-06-DF-10**.
* `durable_content` is **2 of 2 under `map-checking`, 1 of 2 under `map-silent`
  and 1 of 2 under the plain whole-view corpus, on both arms.** The mapping is
  worth exactly one mutant, M04, and the arm is worth nothing at all. HP-05's
  direction reproduces on a fourth and fifth fixture; its magnitude does not,
  again.
* `ordering` — M09, the declared negative control — dies under `corpus-whole`,
  `corpus-slice-led` and both mappings on both arms, and survives `corpus-neg`
  and `corpus-slice-res`. HP-03 already retracted the claim that ordering is
  structurally invisible to corpora: it is invisible when the modelled thing is
  a **set**, and this model represents its ledger as a **sequence**.
* `cross_aspect` — M08 on arm A dies under the whole view and survives **both**
  aspect slices, which is what the slices were declared to be lost by.
* `output_oracle` — M06 dies under every instrument that projects `status`.

## Not seeded, and therefore not measured

Recorded so silence is not read as a result:

* **Concurrency.** The specification declares none, so a mutant there would test
  a surface neither arm was asked to build.
* **Cross-process effects.** The effect oracle is in-process CPython only, so a
  fault of that class is dead on arrival and no added coverage moves it.

## Reproducing

```bash
# the three corpora (write outside the repo; the whole-view one is 66 MB)
python3 scripts/tla_spec_dev.py --spec-root specs generate cases \
  examples/validation/ab/model/QuotaLedger.tla examples/validation/ab/model/QuotaLedger.cfg \
  --out <scratch>/specs/corpus-whole --package quota_whole --view internal
python3 scripts/tla_spec_dev.py --spec-root specs generate cases \
  examples/validation/ab/model/QuotaLedger.tla examples/validation/ab/model/QuotaLedger.cfg \
  --out <scratch>/specs/corpus-neg --package quota_neg --view internal --negative-cases only
PYTHONPATH=$PWD/specs/results/scorecards/hexagonal-prompting/measure \
python3 scripts/tla_spec_dev.py --spec-root specs generate cases \
  specs/results/scorecards/hexagonal-prompting/measure/Aspect_Reservations.tla \
  specs/results/scorecards/hexagonal-prompting/measure/Aspect_Reservations.cfg \
  --out <scratch>/specs/corpus-slice-res --package quota_slice_res --view internal \
  --module-path $PWD/examples/validation/ab/model \
  --state-projector aspect_projectors:project_reservations
# ... and Aspect_Ledger.tla with aspect_projectors:project_ledger

# the effect-provider package, from SHIPPED codegen
python3 scripts/generate_python.py \
  specs/results/scorecards/hexagonal-prompting/measure/effects/spec_manifest.yaml \
  --out $PWD/specs/results/scorecards/hexagonal-prompting/measure/generated

# the table, per arm
python3 specs/results/scorecards/hexagonal-prompting/measure/run_arm_kill_table.py \
  --arm A --arm-root specs/results/scorecards/hexagonal-prompting/arms/arm_a \
  --binding arm_a_binding \
  --catalogue specs/results/scorecards/hexagonal-prompting/measure/catalogue_arm_a.toml \
  --instrument corpus-whole=<scratch>/specs/corpus-whole/spec-unit/quota_whole \
  --instrument corpus-neg=<scratch>/specs/corpus-neg/spec-unit/quota_neg \
  --instrument corpus-slice-res=<scratch>/specs/corpus-slice-res/spec-unit/quota_slice_res \
  --instrument corpus-slice-led=<scratch>/specs/corpus-slice-led/spec-unit/quota_slice_led \
  --instrument map-silent=<scratch>/specs/corpus-whole/spec-unit/quota_whole:silent \
  --instrument map-checking=<scratch>/specs/corpus-whole/spec-unit/quota_whole:checking \
  --suite examples/validation/ab/tests/test_behavior.py --out <out>.json
```

`determinism.txt`: two full runs of the `corpus-neg` and `corpus-slice-res`
instruments over **arm A** are byte-identical.

> **CORRECTED IN PLACE, by HP-06's adversarial channel (finding F12).** The first
> version of this line said "two full runs of the same instruments over the same
> arm", which reads as covering the run. It covers **2 of 6 instruments on 1 of 2
> arms**. NOT covered: `corpus-whole`, `map-silent`, `map-checking` — the
> 43,128-case corpus and both columns carrying the durable-content result —
> `corpus-slice-led`, the `suite` column (which shells out to pytest), and arm B
> entirely. And "recorded failure text included" over-claims even for the two it
> did run, because failure text is only ever retained for controls (F5). Filed as
> **HP-06-DF-09**, not re-run.

## Two runs, and which columns came from which

`merge_tables.py` says it in the file, and it is repeated here because a merged
table with an unstated provenance is exactly the shape a flattering number hides
in. Run 1 produced every column. Its two `corpus-slice-*` columns came back
`CONTROL_RED` **on the unmutated code, on both arms**, because the adapter
returned all nine model fields against cases whose projection carries five, and
the shipped comparator reads an unexpected actual field as a disagreement
against `None`. Run 2 re-ran only the two slice instruments after the adapter was
corrected to compare exactly the fields the case's own projection carries.

The whole-view, negative and mapping columns are taken from run 1 **unchanged** —
the correction is the identity on them, because their cases carry all nine
fields — and their controls were green in run 1. No column was taken from
whichever run produced the better number.
