# RD-02 — the apparatus is load-bearing, and the epic was not a simplification

**Ticket:** [#189](https://github.com/haydenrear/tla-spec-dev/issues/189) ·
**epic:** `reading-discipline` · **parent:** `7514df0` · **goal:**
`GOAL-apparatus-priced`.

Both answers were acceptable. This is the one the evidence supports, and it is
the more expensive one to say out loud.

---

## 0. The three sentences

1. **Per removal, the apparatus cost between 1.07 and 14.78 lines of proof per
   line of production code cut** — and the removal with the *worst* ratio is the
   only one in the epic that was measured to cost anything.
2. **Not one of the nine mutants in `gap_mutants.toml` could have gone
   `DIES` → `SURVIVES`.** Each was already dying on a detector that outlived its
   own cut, or was not dying at all. The verdicts SM-02 and SM-05 re-ran and
   published were entailed by SM-01's before-table before either cut was made.
3. **"Zero `DIES` → `SURVIVES` across everything cut in two epics" is false, and
   it is false because of a scope this epic exists to catch.** It is a claim
   about one catalogue. `SM-04-GM-T1` was seeded under the same rule, by the same
   epic, as an executing test rather than a catalogue row — **and it went
   `DIES` → `SURVIVES`.**

---

## 0a. Round conduct, disclosed rather than buried

- **The after-cut gap-mutant re-run executed concurrently with another ticket's
  full suite.** `wt-epic-reading-discipline-RD-04` was running `pytest tests -q`
  on this machine when my `pytest-full` column started. SM-02 documented that
  machine contention yields a `DIES` indistinguishable from a real kill, and the
  expected verdict here **is** `DIES` — the worst case for that hazard. So the
  verdict is not read from the exit code: §4.2 compares the **new failing node
  set** against the before-run's, and the reading rests on those nodes being
  semantically on-target and matching, not on a red.
- **No process was killed.** The standing rule against `pkill` by name exists
  because sibling worktrees share this machine, and one was demonstrably in use
  for the whole of my measurement.
- **The before-run at `7514df0` was clean** — no concurrent suite, `control_red`
  empty, `mutants_not_applied` empty, every declared mutant applied exactly once.
- **Nothing in the record was edited to clear a result.** `scope` still exits 1
  over this repository and `RD-02-DF-01`..`-DF-05` are filed open, including one
  against RD-01's instrument and one against this ticket's own issue text.

---

## 1. THE PER-REMOVAL TABLE

Produced by `examples/validation/removal_census/removal_census.py census`,
re-measured from git on every run. Raw: `removal-census.json`.

| removal | ticket | scope | cut (production) | cut (its own tests) | cut (prose) | replacement | **proof** | proof / production | proof / all cut |
|---|---|---|---|---|---|---|---|---|---|
| `ports-binding-machinery` | SM-02 | `0342a3a^1..0342a3a` | 291 | 462 | 75 | 77 | **310** | **1.07** | 0.37 |
| `hardcoded-enumeration-literal` | SM-03 | `bf0fb29^1..bf0fb29` | 0 | 33 | 0 | 165 | **351** | — | **10.64** |
| `card-duplication` | SM-06 | `acbd577^1..acbd577` | 0 | 0 | 120 | 84 | **883** | — | **7.36** |
| `total-checksum-field` | SM-04 | `6aac1ec^1..6aac1ec` | 9 | 0 | 3 | 9 | **133** | **14.78** | 11.08 |
| `dead-port-binding-report-detector` | RD-02 | `7514df0..bfd04af` | 33 | 0 | 0 | 24 | **40** | **1.21** | 1.21 |

**There is no total row and the instrument refuses to print one.** `--total` and
`report_total = true` both exit 2. A total over removals is the shape of the
claim that hid the cost in the first place: `-225 lines from scripts/` was true,
and the same epic added **+1677 net `code_lines`** across the trees it touched.

**SCOPE, because these figures do not mean what the +1677 means.** Every number
above is a `git diff -U0` line count over the named paths at the named commit
range. `-225` and `+1677` are `code_lines` from `scripts/code_complexity.py`
over four trees. **Different instruments; the two are not interchangeable and no
row here claims to be the other** (`R-H1`, unchanged instrument).

### And the shared apparatus, which is NOT in any row above

| apparatus | lines | serves |
|---|---|---|
| `run_gap_mutants.py` | 633 | SM-02, SM-03 |
| `tests/test_gap_mutants.py` | 486 | SM-02, SM-03 |
| the catalogue's preamble and eight detector declarations | 130 | SM-02, SM-03 |
| `PREDICTIONS-SM.md`, sealed before any number existed | 260 | all four |

**Deliberately unallocated.** Splitting a shared runner across the removals it
serves needs a weighting the data does not supply, and an invented weighting is
how a per-removal figure becomes a total in disguise. Every ratio in §1 is
therefore a **lower bound** on what the removal cost, and says so.

### What the rows say, one at a time

- **SM-02 is the only removal that came close to paying for itself in
  production code**, at 1.07, and it is the largest cut in the epic — 291 lines
  of the case-adapter runner.
- **SM-03 removed a 33-line literal from a test file and shipped 351 lines of
  proof.** Its `proof / production` is undefined because it cut **no production
  code at all**: the thing removed lived in `tests/`. A removal whose
  denominator is zero is not a cheap removal, it is a removal in a different
  currency, and reporting `—` is the honest cell.
- **SM-06 shipped 883 lines of proof to delete 120 lines of duplicated prose.**
  That is the worst absolute figure in the table, and it is the removal whose
  before-measurement was most worth having: three of four disagreeing copies of
  the card were invisible to every instrument this repository ships. **The
  428-line tripwire is the only thing now standing between the tree and the
  state SM-06 found it in.** Expensive and load-bearing are not opposites.
- **SM-04 cut nine lines and spent 133 proving it.** 14.78 — the worst ratio in
  the table by an order of magnitude over SM-02 — **and it is the only removal
  in the epic that found a real price.** See §3.
- **RD-02's own cut is in the table on the same terms**, at 1.21, and it is
  there because a ticket that prices four removals and exempts its own has not
  measured anything.

### And this ticket is the same shape, at a worse ratio

The row above prices the **removal**. Here is the **ticket**, on the four trees
the predecessor's `+1677` was measured over:

```
$ git diff --numstat 7514df0..807b5bb -- scripts tests examples/validation references
   +1403  -33
```

**A ticket dispatched to price the cost of proving removals safe removed 33
lines and added 1403** — roughly **42 added per line removed**, worse than every
row in §1.

The defence available to me is the one that was available to
`subtract-to-measure`, and it is not nothing: 957 of those lines are the census
instrument and its manifest, which is the *product* of the ticket rather than
proof that a removal was safe, and the census's `proof` role excludes it for
exactly that reason. **But that is a classification I made about my own work, it
is the instrument's declared blind spot, and the ratio is what it is.**

Recorded because the standing rule is that an epic closing with only good news
about itself has not been measured — and because a census whose author exempts
himself from it measures nothing.

---

## 2. THE DENOMINATOR, AND A FREE 2.9× I DECLINED

`denominator_rule`. SM-02 deleted 828 lines: 291 of the mechanism, **462 of the
mechanism's own test file**, and 75 of its documentation. Both are real
deletions. They are not the same claim.

| what is in the denominator | SM-02's ratio | reads as |
|---|---|---|
| production code only | **1.07** | the proof cost slightly more than the mechanism |
| everything deleted | **0.37** | the removal cut nearly three times what it cost |

**Folding the two together improves the number by 2.9× for free**, and it is
free because `test_port_adapter_binding.py` stopped testing anything the moment
the mechanism went. `SM-03` declined a free ratio improvement for exactly this
reason and this census declines the same one: **both denominators are printed,
neither is averaged, and the instrument has no mode that emits only the
flattering one.**

---

## 3. DOES THE APPARATUS EARN ITS KEEP

### 3.1 The mutants could not have said otherwise, and that is computable

A gap mutant can report that a removal cost something **only if every detector
that killed it is a detector that removal deletes**. If one surviving detector
already kills it, the after-verdict is entailed by the before-table and the
re-run measures nothing about the removal.

Computed by `removal_census.py discriminate` against SM-01's sealed
`gap-mutants-before.json`. Raw: `discriminating-power.json`.

| removal | mutant | kills before the cut | kills that outlive it | verdict |
|---|---|---|---|---|
| `ports-binding-machinery` | `SM-GM-P1` | corpus-port-swap:fake, portswap-suite-fake, pytest-full, suite-fake | portswap-suite-fake, pytest-full, suite-fake | NON-DISCRIMINATING |
| `ports-binding-machinery` | `SM-GM-P2` | port-binding-report, pytest-full | pytest-full | NON-DISCRIMINATING |
| `ports-binding-machinery` | `SM-GM-P3` | pytest-full | pytest-full | NON-DISCRIMINATING |
| `hardcoded-enumeration-literal` | `SM-GM-I1` | — | — | NO-KILL-TO-LOSE |
| `hardcoded-enumeration-literal` | `SM-GM-I2` | — | — | NO-KILL-TO-LOSE |
| `hardcoded-enumeration-literal` | `SM-GM-I3` | — | — | NO-KILL-TO-LOSE |
| `hardcoded-enumeration-literal` | `SM-GM-I4` | instrument-registry, pytest-full, spec-yaml-tripwire | instrument-registry, pytest-full, spec-yaml-tripwire | NON-DISCRIMINATING |
| `hardcoded-enumeration-literal` | `SM-GM-I5` | pytest-full | pytest-full | NON-DISCRIMINATING |
| `hardcoded-enumeration-literal` | `SM-GM-I6` | instrument-registry | instrument-registry | NON-DISCRIMINATING |
| `dead-port-binding-report-detector` | `SM-GM-P2` | port-binding-report, pytest-full | pytest-full | NON-DISCRIMINATING |

**0 of 9 catalogue mutants — 0 of 10 rows, `SM-GM-P2` appearing under two
removals — could have gone `DIES` → `SURVIVES`.** Scope: the mutants declared in
`removals.toml`, against the before-table at
`specs/results/scorecards/subtract-to-measure/before-state/gap-mutants-before.json`.
This is **not** a statement about every mutant ever seeded under
`removal_is_a_delta_rule`; §3.3 is about the ones outside it, and one of them
fired.

Six of those rows are structural rather than incidental: **`SM-03` deleted no
detector at all.** The literal it removed lived inside `registry-enumeration`,
whose pytest node kept its name and got a new body. All six I-series mutants
were incapable of pricing that removal whatever they contained.

`tests/test_removal_census.py::test_no_catalogue_mutant_could_have_priced_a_removal_and_it_says_so`
asserts this, so that a future removal seeding a mutant that **is**
discriminating fails the suite — which is the right moment to re-read this
conclusion.

### 3.2 A fact about the mutants or about the removals? Both, and they separate

- **About the removals, for `P1` and `P2`.** Redundant coverage genuinely
  existed: `pytest-full` and `suite-fake` killed those faults independently of
  the machinery. `DIES` after the cut is a true statement about the removal. It
  was not news.
- **About the mutants, for the P-series' claim to have *priced* the machinery.**
  SM-01 itself named the one fault the machinery uniquely caught — dropping
  `fake =` from a `[ports.*]` table, *"caught today by
  `render_oracle_statement`"* — and declared it `not_seedable`, **because the
  table dies with the machinery so the mutant cannot be re-run afterwards.**
  That is a rule, not an oversight, and it was disclosed with its reason. But
  the rule *systematically excludes the faults that could go
  `DIES` → `SURVIVES`*, because a fault only the removed mechanism catches
  usually lives on a surface the removal deletes. **The exclusion was on the
  record and was never read as the reason the table could only come out one
  way.**
- **About the mechanism, for `P3` — the one result the apparatus bought that
  nothing else could have.** The machinery caught `P3` on **zero of four columns
  at 1543 executed cases per column**, while the positive control died on those
  same columns in the same run. A demonstrated failure of the mechanism in the
  fault class it existed for. It is the strongest evidence that cutting it was
  safe — **and it is entirely a before-table result. The re-run added nothing to
  it.**

### 3.3 The claim "zero `DIES` → `SURVIVES`" is scoped to one catalogue, and outside it, it is false

`removal_is_a_delta_rule` says *every removal ships with a mutant seeded in its
gap*. Three sets of mutants satisfy that rule in `subtract-to-measure`. Only one
is in `gap_mutants.toml`.

| mutant | seeded by | lives in | before → after |
|---|---|---|---|
| `SM-GM-*` (9 + 2 controls) | SM-01 | `gap_mutants.toml` | 2 `SURVIVES` → `DIES`, 0 `DIES` → `SURVIVES` |
| `SM-06-DUP-M1..M4` / `A1,A2` | SM-06 | `SM-06/run_dup_mutants.py` | 3 of 4 `UNCAUGHT` before; no kill to lose |
| **`SM-04-GM-T1`** | SM-04 | `tests/test_score_tools.py` | **`DIES` → `SURVIVES`** |

`SM-04-GM-T1` is the mutant for the `total` removal. `total` was a checksum over
the five scores and `check`'s `total != running` was the only thing that noticed
a score altered in a `scorecard.json` after the card was written.

> **SEALED: still dies** — the R-H4 seal digest catches it, and is strictly
> stronger. **UNSEALED: NOW SURVIVES.** Nothing detects a score altered after
> the fact on an unsealed version 3 card, where the arithmetic used to.

That is a load-bearing removal, priced, in a live assertion whose failure
message asks a future reader to re-price it. **It is the answer to "has the
apparatus ever fired": yes, once, in the one place a mutant was seeded where the
removed mechanism was the sole detector.** The two epic-level restatements —
this ticket's issue and `ticket_plan.yaml`'s `GOAL-apparatus-priced` baseline —
both say *"zero `DIES` → `SURVIVES` across everything cut in two epics"*, which
is the catalogue's scope worn as the rule's. `RD-02-DF-02`.

### 3.4 And "zero" survives only on a judgement call about one cell

`SM-GM-I1` on `pytest-full` reads **`SURVIVES`** in SM-01's before-table,
**`DIES`** in SM-02's re-run, and **`SURVIVES`** again in SM-03's. That is a
published `DIES` → `SURVIVES` in the record. SM-05 names it as *"the one cell
known to have flaked historically"* and attributes it to machine contention,
which is a reasonable attribution and is not what was reported afterwards:
**the figure has been restated as a flat zero, without the attribution it
depends on.** `RD-02-DF-03`.

### 3.5 THE DECISION

**LOAD-BEARING, in one half. NON-DISCRIMINATING AS RUN, in the other. And these
were not simplification epics.**

**What earns its keep is seeding the fault BEFORE the cut and reading the
before-table.** Every result the apparatus has produced that changed anyone's
mind came from a before-run:

- `P3`: the machinery caught nothing at 1543 cases per column (before);
- SM-06: three of four disagreeing copies of the card invisible to five
  surfaces (before) — **and the control was caught by `audit`, not by `check`
  as its author had predicted**, which is the apparatus catching the round
  operator;
- SM-03: `I1`/`I2`/`I3` surviving the registry, which turned a ticket
  dispatched to **delete** into a ticket that **repaired** — the single largest
  change of direction in the epic;
- `SM-04-GM-T1`: read before and after **in one run**, deliberately, *"so there
  is no instrument change between the two readings"* — and it is the one that
  fired.

**What does not earn its keep as currently designed is the staged after re-run.**
Two passes of roughly fifty minutes each, under a contention hazard the epic
documented itself, arithmetically incapable of changing a verdict on 9 of the
10 rows in §3.1 and on 13 of the 14 faults `subtract-to-measure` seeded under
`removal_is_a_delta_rule` — nine catalogue mutants, SM-06's four duplicate-card
mutants, and `SM-04-GM-T1`, which is the one.

**It is not deleted, and the reason is `MF-020` turned on myself:** removing the
instrument that prices removals removes the ability to detect that a removal was
harmful, and it would improve every future removal's ratio by deleting the thing
that makes the ratio measurable. What replaces the waste is a computation that
costs nothing per removal because the before-table already exists:
`discriminate` classifies each mutant's discriminating power up front, so an
entailed `DIES` can be **reported as entailed** instead of published as a
measurement. `subtract-to-measure` published *"the measured price of removing
the `[ports.*]` binding machinery is ZERO"*. The honest sentence was: *the price
is zero, and the before-table said so before the cut.*

**And the naming has to stop.** `subtract-to-measure` was a **re-instrumentation
epic that also removed four things.** It came out +1677 net `code_lines`, its
cheapest removal cost 1.07 lines of proof per line of production code cut and
its most expensive cost 14.78, and its most valuable removal was the one with
the worst ratio. Every one of those is a defensible outcome. **"The great
simplification" is not a description of it.** `RD-02-DF-05`.

---

## 4. RD-02'S OWN REMOVAL, PRICED THE SAME WAY

### 4.1 What was cut

`gap_mutants.toml`'s `port-binding-report` detector, and `SM-GM-P2`'s binding
to it.

Its `argv` passed `--port-manifest` to `scripts/run_generated_case_adapters.py`.
**SM-02 deleted that flag, in the same epic that declared the detector.** From
`067c5ea` onward the column exits 2 with `unrecognized arguments`, executes
nothing, and the runner reports `INERT`.

**The runner was never wrong about it.** `INERT` means *nothing executed,
decides nothing*, and is correctly not a survival — that refusal is exactly what
`FI-06` bought. The defect is one level up: **a column that has stopped being
able to speak reads, in the table, almost the same as one that had nothing to
say**, and it sat in the published tables of two epics as if it were a detector.
This is `R2` — *a control that cannot fail is worse than no control* — in the
file whose whole argument is `R2`.

### 4.2 The gap mutant, run FIRST

`SM-GM-P2` — a port renamed in the manifest while every binding still names the
old one — is the mutant seeded in exactly this column's gap. Re-run at the
parent commit `7514df0`, **before a line was deleted**:

| detector | before `7514df0` | after `bfd04af` |
|---|---|---|
| `port-binding-report` | **INERT**, executed 0, **exit 2** — `unrecognized arguments: --port-manifest` | *removed* |
| `pytest-full` | **DIES**, 1426 executed | **DIES**, 1438 executed |

`control_red` empty and `mutants_not_applied` empty in both runs. Raw:
`rd02-gap-mutant-before.json`, `rd02-gap-mutant-after.json`.

**The verdict is read from the kill set, not the exit code**, because §0a's
contention hazard makes a `DIES` the one verdict a loaded machine can
manufacture. The kill sets are **identical**:

```
new_failing_nodes, both runs, in order:
  tests/test_port_case_generation.py::test_a_port_declared_in_the_manifest_is_read_in_the_effect_port_shape
  tests/test_port_case_generation.py::test_the_ab_fixtures_port_region_is_the_ledger_aspect_derived
  tests/test_ports_binding_removed.py::test_the_generator_still_declares_ports_and_still_builds_port_labels
```

Three nodes, all of them about a port declared in the manifest — semantically
on-target for a mutant that renames a port in the manifest. **Contention does
not reproduce the same three nodes twice.**

**PRICE: ZERO, and it was entailed before the run.** `discriminate` classified
`SM-GM-P2` against this removal as `NON-DISCRIMINATING` *before* the cut —
`pytest-full` kills it and `pytest-full` outlives the cut — so `DIES` after was
the only arithmetic outcome. The run was made anyway, because a classifier whose
predictions are never checked is the shape of thing this epic keeps finding, and
**the prediction held.** That is the sentence SM-02 should have written: *the
price is zero, and the before-table said so before the cut.*

### 4.2a And the re-run found something the classifier could not predict

`baseline_failing_nodes` moved **10 → 16** between the two runs, and **all six
are mine**: the census's tests shell out to an instrument that measures from
git, and `run_gap_mutants.py` stages with `git archive`, so the tree every future
mutant is measured against has no `.git`.

**Six new baseline failures in a table where a baseline failure is noise every
future removal has to subtract.** Not caught by any test I wrote — caught by
running the apparatus, which is the argument for the apparatus, made against me.

Fixed in `7e99138`: the git-dependent tests skip where the census cannot run,
and `test_the_git_guard_does_not_fire_in_a_real_checkout` fails if the file ever
skips in a tree that has history — because a skip that turns a file green is
`FI-06` and this repository has bought it twice. Verified in a `git archive`
tree: **3 passed, 9 skipped, 0 failed.**

### 4.3 The price

| | lines |
|---|---|
| cut (production) | 33 |
| replacement — the `[[not_seedable]]` row recording what the column claimed | 24 |
| **proof** — the tripwire that refuses a detector whose entry point rejects its argv | **40** |
| **ratio** | **1.21** |

The removal is `[[not_seedable]]`-recorded rather than silently deleted, because
a detector that vanishes from a table is how a denominator shrinks.

### 4.4 R1 — the demonstrated failing input, on a real subject

`tests/test_gap_mutants.py::test_every_cli_detector_declares_flags_its_entry_point_still_accepts`.

| subject | result |
|---|---|
| the catalogue at `7514df0`, unmodified | **FAILS** — `port-binding-report` passes `--port-manifest`, rejected |
| the catalogue at `bfd04af` | passes; one cli detector remains and its flags are declared |

Registered as `gap-mutant-detector-argv`, with its failing input staging the
real catalogue and reinstating the real dead column. **Declared blind spot:** it
compares flag *names* against `add_argument` declarations. A flag still accepted
but now meaning something else, or a positional that moved, is invisible to it.
It catches the failure that actually happened and claims nothing wider.

`removal-census` is registered too, with `check` against a manifest whose
`expect_lines = 290` has been moved to `291` — the real manifest, mutated the
way a hand-maintained census goes stale.

---

## 5. WHAT I REJECTED

**Every one of these would have improved a number.**

1. **A total, or a net figure.** The single easiest headline in the ticket. The
   instrument refuses it in code, with the 1677 figure inside the refusal, and a
   test asserts no rendered row is one.
2. **Folding `cut_tests` into `cut_production`.** Moves SM-02 from 1.07 to
   0.37 — **a 2.9× improvement, free, and defensible in a sentence.** Declined;
   both denominators print. This is the `SM-03` precedent and it is the whole of
   `denominator_rule`.
3. **Deleting the staged after re-run**, which my own §3.1 shows was incapable
   of changing 13 of the 14 faults seeded under the rule. It is the largest
   apparatus in the epic (633 +
   486 + 130 lines) and cutting it would improve every future removal's ratio —
   by deleting the instrument that makes the ratio measurable. `MF-020` applied
   to myself.
4. **Deleting `tests/test_ports_binding_removed.py` (220 lines).** The single
   largest item in SM-02's proof column; removing it takes that row from 1.07 to
   **0.31**. It is the only thing keeping the machinery from being written
   again, and I could not seed a mutant showing anything else catches a
   reintroduction. Declined on the measurement, not on the argument.
5. **Deleting `PREDICTIONS-SM.md` (260 lines)** as apparatus for a closed epic.
   Four of its predictions were refuted, which is the strongest single piece of
   evidence in the record that the apparatus is not decoration. Deleting it cuts
   260 lines of "apparatus" at the price of the evidence that the apparatus
   works.
6. **Allocating the 1509 lines of shared apparatus across the four removals.**
   Would have given every row a fuller, more impressive ratio. Any allocation is
   invented, and an invented weighting is a total in disguise. Reported
   unallocated, and every ratio in §1 declared a lower bound.
7. **Claiming `-225` / `+1677` as figures of this census.** They are `code_lines`
   from a different instrument over four trees. Quoting them as if they were
   `git diff` counts would have let §1 and the epic's headline be read as one
   table. `R-H1`.
8. **Editing the charters that call this a simplification.** They are outside
   `RD-02`'s `implementation_scope` and this is a measurement ticket. Said
   plainly in §3.5, filed as `RD-02-DF-05`, not fixed.

---

## 5a. I RAN RD-01'S SCOPE CHECK OVER THIS DOCUMENT AND IT REFUSED NOTHING — BECAUSE IT CANNOT SEE ANY OF IT

R3 binds this ticket: *run `score_tools.py scope` over your own writing before
you seal. It refused a claim inside the section of the card that declares R3; it
will not spare you.*

It spared me completely, and the reason is not that my writing is scoped.

```
$ python3 examples/validation/scorecards/score_tools.py scope --path <this file>
0 counted figure(s): 0 REFUTED, 0 COUNT-MOVED, 0 HOLDS, 0 UNREACHABLE
```

**This document carries at least twelve counted figures** — *0 of 9 mutants*,
*3 of 4 copies*, *13 of 14*, *9 of the 10 rows*, *4 of 4* — and the check
reports it contains **none**. Not one is refused, and not one is even counted as
`UNREACHABLE`, which is the count that exists precisely so a claim the check
cannot reach is not mistaken for one that holds.

Demonstrated, not inferred. A three-line probe:

| line | reached? |
|---|---|
| `D2 = 2 on 27 of 27 cards` | **REFUTED**, with four counterexamples named |
| `0 of 9 mutants could have priced a removal` | invisible |
| `3 of 4 copies were invisible` | invisible |

`1 counted figure(s)` out of three.

**The check is keyed on a dimension's name.** `_ANOTHER_DIM = re.compile(r"D[1-5]")`.
A counted claim that does not say `D3` is not a counted claim to it.

**This is `SM-05-DF-02` living inside RD-01's own instrument.** SM-05 disclosed
the identical error about its own leak scanner: *"A result stated without the
dimension's name is invisible to a pattern keyed on the dimension's name."* The
epic that was opened to make scope-loss catchable by machine shipped a check
that catches it in the one sentence shape the scorecard happens to use.

**So RD-01's headline — 19 of 44 counted figures do not survive a check — carries
a scope of its own: 44 is the count of figures that name a dimension.** It is not
the count of counted figures in this repository, and this document alone would
have added twelve to a denominator it is not in. `RD-02-DF-01`.

I am not fixing it. It is `RD-01`'s instrument, it is a measurement round, and
`RD-03` sweeps it.

---

## 6. SUITE NUMBERS, WITH THE TREE THEY CAME FROM

`RD-01-DF-02`: *"the suite is green" has never been true in a ticket worktree.*
`test_card_has_one_home.py` and `test_code_complexity.py` walk the gitignored
`.claude/` and `.skill-manager/` homes **that `wt new` itself creates**.

Every number below is from **`/Users/hayde/IdeaProjects/wt-epic-reading-discipline-RD-02`,
a ticket worktree with both homes present.** They are not comparable to a number
from a tree without them, and no number here is reported as "green".

*(figures inserted at close-out — see `SUITE.md` in this directory)*

---

## 7. FINDINGS FILED, NONE FIXED

| id | finding |
|---|---|
| `RD-02-DF-01` | `score_tools.py scope` reaches only counted figures that NAME A DIMENSION (`_ANOTHER_DIM = re.compile(r"D[1-5]")`). Run over this document — twelve-plus counted figures — it reports `0 counted figure(s)`, with zero `UNREACHABLE`. RD-01's `19 of 44` is therefore scoped to dimension-named figures and is not a count of counted figures in the repository. §5a, with a demonstrated probe. |
| `RD-02-DF-02` | "Zero `DIES` → `SURVIVES` across everything cut in two epics" is a claim about `gap_mutants.toml` restated as a claim about `removal_is_a_delta_rule`. `SM-04-GM-T1` went `DIES` → `SURVIVES`. Live in issue #189 and in `ticket_plan.yaml`'s `GOAL-apparatus-priced` baseline. |
| `RD-02-DF-03` | `SM-GM-I1` on `pytest-full` reads `SURVIVES` → `DIES` → `SURVIVES` across three published tables. The "zero" depends on a contention attribution that later restatements dropped. |
| `RD-02-DF-04` | The seeding rule — a mutant must be re-runnable on the after tree — structurally excludes the faults that could price a removal. SM-01 named one such fault for the ports machinery and declared it `not_seedable`, with the reason, and nothing read that as the reason the table could only come out one way. |
| `RD-02-DF-05` | `subtract-to-measure` is described as a simplification in its charter, in `NEXT-EPIC.md` and in the plan. It came out +1677 net `code_lines` and its removals cost 1.07–14.78 lines of proof per line of production code cut. Out of this ticket's implementation scope; filed rather than edited. |

---

## 8. REPRODUCE

```bash
python3 examples/validation/removal_census/removal_census.py census
python3 examples/validation/removal_census/removal_census.py check
python3 examples/validation/removal_census/removal_census.py discriminate
python3 examples/validation/removal_census/removal_census.py census --total   # exits 2
```
