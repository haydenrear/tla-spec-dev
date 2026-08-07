# SM-03 — the twelve slots were uncounted, not hollow

**Nothing was deleted.** The ticket's default was deletion and the measurement
refused it, so the headline has to be read the other way round: this is a
repair ticket that grew the denominator.

Artifacts: `after-state/instruments-after.json` (the registry's own run, exit 0),
`after-state/instrument-sweep-after.md` (the counts, derived by parsing the
registry), `after-state/gap-mutants-after.json` (SM-01's I-series, re-run).

---

## 1. The count, before against after

| figure | before | after | direction |
|---|---|---|---|
| enumerated rows | 40 | **57** | |
| instruments | 35 | **47** | denominator **+12** |
| with a demonstrated failing input | 26 | **33** | numerator **+7** |
| without one | 9 | **14** | |
| **the headline ratio** | **26 of 35 — 74.3%** | **33 of 47 — 70.2%** | **FELL** |
| pytest slots asserting only `expect_exit` | 12 | **0** | |
| rows where `failing` and `passing` run the same command | 2 | **0** | |

**`denominator_rule`, answered without being asked twice: the ratio did not
rise, and nothing was deleted, so no part of the movement is a denominator that
shrank.** Deletions and repairs, reported apart:

| change | numerator | denominator |
|---|---|---|
| **DELETIONS** | **0** | **0** |
| **REPAIRS** — the 12 uncounted slots and the 2 degenerate pairs | 0 | 0 |
| **REPAIRS** — 2 rows whose "cannot be demonstrated" was false | **+2** | 0 |
| **NEW ROWS** — 18 executables the enumeration could not see | **+5** | **+12** |

**The largest part of this ticket moves no figure in that table**, and that is
the honest thing to say about it. A slot that reported `ok` for the wrong reason
and now reports `ok` for the right one reads identically. The only evidence that
anything changed is a mutant: `SM-GM-I1` survived the registry at SM-01 and dies
against it now.

---

## 2. What the real hole turned out to be

The issue restates `FI-06`: twelve slots assert only `expect_exit = 0`, *"which
pytest returns for a passing run and a fully skipped one"*. `SM-01` seeded both
skip shapes rather than one:

| skip shape | collected | exit | the slot said |
|---|---|---|---|
| `pytest.skip(..., allow_module_level=True)` | nothing | **5** | **red already** |
| `pytestmark = pytest.mark.skip(...)` | all of them, then skipped | **0** | **`ok`** |

**So the blind spot is a demonstration that goes VACUOUS, not one that
DISAPPEARS.** The registry could already see a demonstration being removed. What
it could not see was one still sitting there, still collected, still exiting 0,
asserting nothing.

That changes the verdict on all twelve. **A hollow instrument should be deleted;
an uncounted one should be counted.** Deleting the twelve on FI-06's sentence as
written would have removed twelve repairable instruments — and improved the
headline ratio by shrinking the denominator, which is `MF-020` in this epic's
clothes and is precisely what `denominator_rule` was written to catch. **Zero
were deleted.**

The repair is one field. `run_pytest` reads pytest's own summary line and
`judge` gains `expect_passed` (exact, where the slot cites node ids) or
`expect_passed_at_least` (a floor, where it cites a whole file and an exact
count would go stale on an unrelated new test), with `expect_skipped` defaulting
to **0** on every pytest slot whether or not it asks. All 43 pytest slots now
carry a count and
`test_every_pytest_slot_declares_an_executable_count` makes it mandatory.

This is the same repair `SM-01-DF-01` asks for one layer down, where the
port-swap driver's suite columns carry no executable count and are therefore
structurally exempt from control checking. **Same defect, second location, found
by a mutant rather than by reading.**

### The two degenerate rows

`complexity-ledger` and `case-modules-validate` each ran
`pytest <the whole file>` for **both** slots — one observation reported as two
demonstrations. Both now cite the refusing nodes and the accepting nodes
separately, and a third cannot appear:
`test_no_pytest_slot_runs_the_same_command_as_its_own_passing_slot`. That test
compares the whole staged command, not the node list, because
`spec-yaml-tripwire` legitimately cites one file in both slots and breaks it in
only one of the two trees.

---

## 3. The gap-mutant table — my six, re-run

Run of record: `run_gap_mutants.py --family staged`, staged from the SM-03 tip.
Verdicts compare **failure sets** against the pristine staged tree, never exit
codes. **`mutants_not_applied: []`, `control_red: []`,
`detectors_with_a_red_control: []`** — every declared mutant applied exactly
once and the positive control died on the detector it declares.

Baselines on the pristine staged tree: `pytest-full` exit 1, **1377 executed, 9
failing** — the same nine git-history readers SM-01 recorded, which fail in a
`git archive` tree for that reason alone.

| mutant | `instrument-registry` | `registry-enumeration` | `spec-yaml-tripwire` | `pytest-full` | before → after |
|---|---|---|---|---|---|
| **`SM-GM-I1`** cited node collected and **skipped** | **DIES** 1 | — | — | SURVIVES 1304 | **SURVIVES → DIES** |
| **`SM-GM-I6`** cited node **not collected** | **DIES** 1 | — | — | SURVIVES 1304 | DIES → DIES |
| **`SM-GM-I2`** the instrument stops refusing | SURVIVES 1 | — | — | SURVIVES 1377 | SURVIVES → SURVIVES |
| **`SM-GM-I3`** an instrument never added to the registry | — | **DIES** 1 | — | **DIES** 1379 | **SURVIVES → DIES**, on both |
| **`SM-GM-I4`** a shipped spec YAML committed unparseable | **DIES** 1 | — | **DIES** 23 | **DIES** 1377 | DIES → DIES |
| **`SM-GM-I5`** the enumerator stops reporting a failure | SURVIVES 1 | — | — | **DIES** 1377 | unchanged |
| **`SM-GM-CTRL-B`** (positive control) | **DIES** 1 | — | — | — | DIES → DIES |

Row by row:

- **`SM-GM-I1` is the repair's target and it flipped.** It survived
  `instrument-registry` at SM-01 and dies now, reporting
  `0 test(s) passed, declared exactly 4` and `4 test(s) SKIPPED, declared 0`.
  **`pytest-full` still survives it and always will** — a skip is not a failure,
  so the suite is green either way, which is exactly why the registry had to be
  the thing repaired.
- **`SM-GM-I6` still dies**, and the pair is still read as a **difference, never
  a total**. One shape was always caught; the other never was. That contrast is
  the whole reason the repair is a repair rather than a rewrite.
- **`SM-GM-I2` still survives, and it is UNDER-POWERED by SM-01's own account.**
  It perturbs a *reported field* rather than the refusal path, which SM-01
  recorded as a defect in the mutant instead of reinterpreting it into a finding
  about the row. It is not evidence the row is hollow and it is not evidence the
  repair failed; it is a mutant that does not reach its subject.
- **`SM-GM-I3` flipped on BOTH detectors**, and the second one matters more than
  the first. `registry-enumeration` dying is the repair working. `pytest-full`
  dying too means the obligation now reaches the acceptance command every ticket
  already runs — an unregistered instrument cannot land green any more.
- **`SM-GM-I4` and `SM-GM-I5` are unchanged**, as they should be. Neither was a
  target; `SM-GM-I4`'s product was the diagnosis that made two other repairs
  possible.

**No mutant went from DIES to SURVIVES**, and no mutant could have: nothing was
removed. `removal_is_a_delta_rule`'s "load-bearing" column is empty because its
"removed" column is. What the table reports instead is **two flips from SURVIVES
to DIES**, which is the only evidence available that a repair repaired anything
— and it is the evidence the count in §1 structurally cannot give.

---

## 4. The registry's blind spot, and how it is fixed without a list

`test_the_named_instruments_are_all_enumerated` asserted `required <= enumerated`
over a literal of thirteen paths. That relation is one-directional: a new
instrument is not in `required`, so the subset stays true whether or not anyone
registered it. Its own docstring conceded it. `FI-04-DF-04` was confirmed four
times, including by FI-04 itself, which shipped `run_arm_swap.py` in the same
reconcile as the finding about exactly this.

**The literal is deleted, not lengthened** — that shape was rejected at
`EVAL-RERUN-DF-01` and again at `ARM_MODULE_PREFIXES`, and it is worse here than
anywhere, because the literal has to be edited by the same person who has just
forgotten to register the instrument.

`[registry.enumeration]` declares a **scope**: two roots, two exclusions, each
carrying a written reason. The **members are derived** by walking the tree for a
`__main__` guard plus a nonzero exit path — the definition the registry's own
preamble already used. **Adding a file cannot satisfy it; only adding a row
can.** `SM-GM-I3` flips to `DIES`.

Three properties, each with a test:

- it still catches the **rename** the literal caught, because a renamed file is
  a discovered candidate with no row;
- its **exclusion list cannot grow quietly** — both entries are pinned by name
  and each must carry at least twenty words of reason, the discipline
  `GATING_SCAN_EXEMPT` already gets;
- **it measures a tree it is handed**, never the one it lives in. SM-01 found
  the gap-mutant runner detecting itself because its catalogue check read
  anchors out of whichever tree it ran in; `discover_candidates(root, ...)`
  takes the root as an argument for that reason, and the demonstration points it
  at a staged tree.

### What it found: eighteen, not eight

`FI-06-DF-01` said "at least eight" and listed eight found by hand. The first
run of the derived check found **eighteen**, including `demonstrate.py` itself,
`run_gap_mutants.py` (shipped by SM-01 in this epic, **unregistered on arrival**
— the fifth occurrence of `FI-04-DF-04`) and `scripts/tla_spec_dev.py`, which is
the CLI the toolchain is named after. **A hand-enumerated floor was out by more
than a factor of two.**

### What it still cannot see, counted rather than closed

The predicate is a `__main__` guard plus a nonzero exit path. A repo tripwire
that is a **pytest file** has neither — so `test_code_complexity.py` and its four
siblings, the rows this registry leans on hardest, are exactly the five it would
never have asked anyone to add. Widening it to "every file under `tests/`" was
rejected: ~48 test files owing a row is a taxonomy nobody maintains and a
denominator that stops meaning anything. Declared as a blind spot, per R2.

It also **over-approximates on purpose**: `raise SystemExit(main())` reads as a
nonzero exit path even where `main()` only ever returns 0, so
`generator_vs_suite.py` is flagged despite being correctly not an instrument.
That is the right direction to be wrong in — a false positive costs one row with
a reason, a false negative is the silent omission the registry exists to prevent.

---

## 5. The four rows whose reason was about the runner

`SM-GM-I4` showed `no-demonstration-constructible` was, for four rows, a fact
about `demonstrate.py` shelling pytest at `REPO_ROOT` rather than at the tree it
had just staged. `run_pytest` now stages.

| row | after | note |
|---|---|---|
| `spec-yaml-tripwire` | **demonstrated-can-fail** | a shipped YAML broken in a staged tree, the SM-GM-I4 edit |
| `source-citation-tripwire` | **demonstrated-can-fail** | a stale `budgets.py:3 (anchor)` citation whose anchor is on line 217 |
| `port-declaration-tripwire` | still cannot | **`SM-03-DF-01`** — the demonstration is real and the runner cannot see it |
| `manifest-self-records-tripwire` | still cannot | needs three mutually-consistent manifest trees; not built here |

**Neither tripwire was touched.** Refactoring an instrument to be demonstrable
while it is watching the trees this ticket measures is the forbidden half of the
repair rule, and it is why the original classification was defensible even
though its stated reason was wrong. **Both stale reasons are replaced with true
ones**, including on the two rows still in the "cannot" column.

`SM-03-DF-01` is the load-bearing finding: `judge()` reads an **exit code**,
while `run_gap_mutants.py` one directory over runs each detector on the
**pristine** tree first and compares **failure sets**, because a staged tree has
pre-existing failures. Staging `test_port_declarations.py` and seeding a
degenerate `target: "**"` produces exactly one new failure and nothing else
moves — a genuine demonstration the runner cannot distinguish from the staging
shortfall, because both runs exit 1. **One layer of "the reason was about the
harness" was peeled off and another was found underneath.**

---

## 6. Two shipped tripwires caught this ticket

Neither was fixed by exemption. SM-01 reported the same thing one ticket ago and
this is the second consecutive round in which the repository's own instruments
found the ticket before the ticket found anything.

**1. `test_produced_code_prompt.py::test_the_prompt_mentions_it_only_as_prose`**
went red on a **comment** in `demonstrate.py` — the one listing what the new
enumeration check cannot see, which named the produced-code instrument in
passing. The tripwire's rule is that no Python file under `examples/` or
`prompts/` may name it, because *a mention is how a consumer arrives*. **Fixed
by not naming it**, which is exactly the call SM-01 made against the thermometer
tripwire, for the same reason: lengthening an exemption list was rejected at
`EVAL-RERUN-DF-01` and again at `ARM_MODULE_PREFIXES`, and is worse here because
that scan is one of the instruments this epic is judging.

**2. `test_gap_mutants.py::test_every_mutant_anchor_occurs_exactly_once_in_the_shipped_tree`**
reported `SM-GM-CTRL-B`'s anchor at **0x**. The anchor was the verbatim text of
`complexity-ledger`'s failing slot — one of the two degenerate rows — which this
ticket repaired, so the string no longer exists.

**The control was RE-ANCHORED and the move is recorded in the catalogue under
`re_anchor_note`, not done quietly**, because re-anchoring a positive control is
one step away from editing a target to match a result. Same mechanism, same
detector, same `must_die_on`, same `control_role` sentence; only the string it
attaches to moved, and it moved because the row underneath it was repaired. **R2
is why it was not simply reported unapplied**: a run whose positive control
cannot fire decides nothing, and every verdict in the after-table would be
undecided. SM-01's before-table is readable precisely because both its controls
died on every detector they declare.

SM-01 wrote that tripwire, and it caught SM-01 too.

---

## 7. What was REJECTED

- **Deleting the twelve `expect_exit = 0` slots.** The ticket's stated default,
  and it would have improved the headline ratio by shrinking the denominator.
  SM-01's measurement says they are uncounted, not hollow. All twelve repaired.
- **Deleting `ticket-state-agreement`** (`no-instrument-exists`, watches
  nothing, both `ticket.yaml` readers under append-only history — SM-01: *"the
  removal's cost is already paid in full"*). It is the single cheapest deletion
  available and it would have moved the ratio from 33/47 to 33/46 **for free, by
  arithmetic alone**. That is exactly the shape `denominator_rule` forbids, and
  a ticket that took it while reporting a falling ratio would have been laundering
  one number through another. The row stays and stays counted.
- **Cutting `scripts/code_complexity.py`** with the other rows that cannot be
  shown to fail. It correctly cannot fail: a thermometer, `EXIT_OK = 0` its only
  exit constant, refusing nothing by design. Kept, kept in the cannot-fail
  count, with the reason attached.
- **Deleting `SM-GM-I2` from the reading** because it still survives. It is
  under-powered by SM-01's own account — it perturbs a reported field, not the
  refusal path — and SM-01 recorded that as a defect in the mutant. Reporting it
  as a surviving gap would be reinterpreting a known-bad mutant into a finding.
- **Lengthening the `required` literal**, the obvious repair, rejected on
  precedent.
- **Putting the obligation on `close ticket`**, which is FI-04's own suggestion
  and the issue repeats it. It is a **new refusal on the workflow path** and
  `no_new_gates_rule` says four epics of static checking caught zero bugs. What
  shipped is a repair of a check that already existed, in the suite, refusing
  nothing about the product and consulted by no close path.
- **Widening the discovery predicate to `tests/`**, which would close the one
  blind spot the new check has, at the cost of ~48 rows of noise.
- **Fixing `scripts/extract_spec_manifest.py`**, which is red on the shipped
  tree. `measurement_rule`. It is now **registered**, so it is red in public
  rather than red and invisible. `SM-03-DF-02`.
- **Giving `run_pytest` a pristine-baseline pass** to close `SM-03-DF-01`. It is
  a second structural change to the program that produces the count this ticket
  reports, inside the ticket that reports it — the objection SM-01 raised
  against editing `run_port_swap.py` mid-epic, unchanged.
- **Adding `SM-GM-CTRL-B` to an exemption instead of re-anchoring it**, and
  equally **reporting it unapplied and running without a positive control**. The
  first hides a broken control; the second produces an after-table in which no
  verdict is decidable. The anchor was moved, the move is written into the
  catalogue beside the control, and nothing else about it changed.
- **Repairing `scripts/extract_spec_manifest.py`'s three missing manifest keys**
  by editing `specs/program_model/spec_manifest.yaml`, which would have made the
  red disappear without anyone deciding whether the requirement or the manifest
  is the defect — and would have edited an input to the close path this ticket
  has to run.

---

## 8. Reconcile onto SM-02 (`0342a3a`)

Merged at `f07ea7b`. **One number moved and it is not a registry number.**

| figure | before reconcile | after | why |
|---|---|---|---|
| acceptance suite | 1373 passed | **1366 passed** | SM-02 deleted `test_port_adapter_binding.py` (**21** collected nodes) and added `test_ports_binding_removed.py` (**14**). `1373 − 21 + 14 = 1366`, exactly |
| instruments | 47 | **47** | — |
| with a demonstrated failing input | 33 | **33** | — |
| headline ratio | 70.2% | **70.2%** | — |
| discovered candidates under the declared roots | 35 | **35** | — |
| unregistered | 0 | **0** | — |

Both node counts were **counted here, not quoted**: 21 by collecting the deleted
file out of a `git archive` of `f0c215d`, 14 by collecting the added file at the
tip. Nothing was re-run to make a number match.

**The check the epic owner asked for, and it was the one that mattered.** This
registry no longer uses a literal list — it walks the tree — so SM-02's
deletions could have moved my denominator without my touching anything, and
`denominator_rule` would then apply to a change I did not make. Tested as a
**set**, not a count: the candidate set discovered under
`[registry.enumeration] roots` at `f0c215d` and at `f07ea7b` is **identical —
35 both sides, zero lost, zero gained**. Every declared path still exists.
SM-02's "registry impact: none" is confirmed against the derived walk, not
merely against the literal it replaced.

Why nothing moved, stated so the next removal can predict it: SM-02's deletions
landed in `tests/`, `references/` and
`specs/results/scorecards/ports-as-adapters/`, and **none of those is a declared
root**. Its one edit inside a root — `scripts/run_generated_case_adapters.py`,
which lost the `[ports.*]` branch — left both halves of the predicate intact, so
the file is still a candidate and is still registered as `corpus-runner`.

**`SM-02-DF-02` reaches no figure here.** It reports SM-01's sealed
`produced-code-before.json` as 105 lines low on two of its four trees. No number
in this document, in `instrument-sweep-after.md`, or in `SM-03-DF-01..03` is
derived from that file — every count here comes from parsing `instruments.toml`
or from the registry's own run. Checked by grep, not by memory.

Registry re-run post-merge: **exit 0, every declared demonstration reproduced**,
counts identical to §1.

---

## 9. Findings

`SM-03-DF-01` … `SM-03-DF-03` in
`specs/desired_program_model/deferred_findings.yaml`. **Budget 5, spent 3, none
fixed.** All three came from the dominant channel the predecessor named — build
the instrument, then ask what it cannot report — applied to this ticket's own
repairs.
