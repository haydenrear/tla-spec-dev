# PREDICTIONS — subtract-to-measure epic

**Sealed by SM-01, before SM-02, SM-03, SM-04 or SM-05 was dispatched, and
before the gap mutants were run. SM-05 scores these and may not amend them.**

The seeds are already committed (`68a826f`); the numbers are not. That ordering
is the whole point and git history carries it.

---

## Why this file has a harder bar than its predecessor

`FI-04` sealed eight predictions and scored **8 of 8, 0 FAIL, 0 SUPERSEDED** —
and `FI-06` correctly reported that as an **alarm**, not a result:

> **four of the four negatives are structurally unfalsifiable**, not merely
> biased … It is not surprise, and this round had none from this channel.

They failed in three distinct ways, and each one is a trap this file is written
to avoid:

- **VACUOUS** — *"arm A's and arm C's `:real` and `:fake` cells are IDENTICAL"*,
  when both columns resolve to the same adapter over the same cases. A
  determinism check wearing an architecture check's label.
- **ENTAILED** — true by reading four lines of source. No run required.
- **SELF-FULFILLING** — its truth-maker was that the sealer had written one
  `[[mutants]]` block per file.

**So every negative below states, in its own row, the exact observation that
would falsify it.** A prediction that cannot say what would refute it is not a
prediction, and it is marked as such rather than counted.

Two of the positives below are **ENTAILED and labelled ENTAILED**. That is
deliberate: `FI-06`'s complaint was not that entailed rows exist, it was that
they were scored as though they were surprises. An entailed row that says so
costs nothing and stops a later reader inflating the pass count.

## Ground rules

- **Findings are FILED, never fixed during a measurement.**
- **Never edit a target to match a result. Report the run that happened.**
- Every gap-mutant verdict is reported **per mutant, per detector, with the
  executable count**. Never a single rate, never a total across detectors.
- **`UNMEASURED` is not a pass.** A prediction whose instrument did not run is
  `UNMEASURED` and must say why.
- Scoring vocabulary at `SM-05`: `PASS`, `FAIL`, `SUPERSEDED` (the instrument
  turned out not to measure what the prediction assumed — must name which
  instrument and why), `UNMEASURED`.
- **If every prediction passes, SM-05 reports it as an ALARM.** A round where
  nothing was refuted measured nothing, and this file has been written so that
  outcome would be genuinely surprising rather than structural.

## What decides them

| instrument | what it settles |
|---|---|
| `examples/validation/gap_mutants/run_gap_mutants.py` | every `SM-GM-*` verdict, per detector, with executable counts |
| `scripts/code_complexity.py` over the four trees | the produced-code figures, before against after |
| `examples/validation/instruments/demonstrate.py` | the instrument counts, deletions reported separately from repairs |
| two blind judges on the card | `D2`, `D3` |
| `SM-05`'s channel accounting | findings per 100k subagent tokens, by channel |

---

# POSITIVES

### P01 — the fake-side port fault dies to the hand-written suite, not to the binding

- **Prediction:** `SM-GM-P1` (the fake journal records newest-first) reports
  `DIES` on `suite-fake` **and** on `pytest-full`, and `SURVIVES` on
  `suite-real`.
- **Instrument:** `run_gap_mutants.py`, detectors `suite-fake`, `suite-real`,
  `pytest-full`.
- **Direction:** DIES on two, SURVIVES on one.
- **ENTAILED**, and labelled so. `tests/test_ab_three_arms_and_port_faults.py::
  test_a_composition_point_wires_the_fake` asserts the exact ledger-line list
  through the fake composition point, and the fake is not on the real wiring's
  executed path. Both halves are readable without running anything. It is here
  because it is the contrast row for `N01`, not because it is news.

### P02 — the manifest-drift reconciliation is the machinery's one unique catch

- **Prediction:** `SM-GM-P2` (the manifest renames the port out from under the
  binding) reports `DIES` on `port-binding-report` and `SURVIVES` on
  `pytest-full`.
- **Instrument:** `run_gap_mutants.py`, detectors `port-binding-report`,
  `pytest-full`.
- **Direction:** DIES on the ports detector, SURVIVES everywhere else.
- **NOT entailed.** I have not established whether any of the 1335 tests reads
  `examples/validation/ab/model/spec_manifest.yaml` in a way a port rename would
  break. If one does, this fails, and the machinery's last unique claim goes
  with it.

### P03 — the `complexity-ledger` row is redundant with the suite, so DELETE is right

- **Prediction:** `SM-GM-I2` (the ledger records every close and refuses none)
  reports `DIES` on **both** `pytest-full` and `instrument-registry --only
  complexity-ledger`.
- **Instrument:** `run_gap_mutants.py`.
- **Direction:** DIES on both.
- **Consequence if it passes:** the row detects an instrument going soft, but
  only by way of a pytest file the acceptance suite already runs. `SM-03` should
  DELETE it as a demonstration and lose nothing, and must say that the loss is
  zero *because the suite covers it*, not because the row was hollow.

### P04 — the enumeration check cannot see an instrument that was never added

- **Prediction:** `SM-GM-I3` (a new executable under `scripts/` with no registry
  row) reports `SURVIVES` on `registry-enumeration` **and** on `pytest-full`.
- **Instrument:** `run_gap_mutants.py`.
- **Direction:** SURVIVES on both.
- **ENTAILED**, and labelled so. `required <= enumerated` is one-directional and
  the test's own docstring says it cannot catch this (`FI-04-DF-04`). Sealed
  anyway because `SM-03` must repair it, and this row is the demonstrated
  failing input the repair has to flip to `DIES`. **An entailed row that becomes
  a repair's acceptance test has earned its place; it is still not a surprise.**

### P05 — "no demonstration constructible" is a fact about the runner, not the tripwire

- **Prediction:** `SM-GM-I4` (a shipped spec YAML committed unparseable) reports
  `DIES` on `spec-yaml-tripwire`, while `instrument-registry --only
  spec-yaml-tripwire` reports `SURVIVES`.
- **Instrument:** `run_gap_mutants.py`.
- **Direction:** DIES on the tripwire, SURVIVES on the registry.
- **NOT entailed.** The claim under test is that four registry rows are declared
  `no-demonstration-constructible` for a reason — *"not without breaking a
  shipped file"* — that is actually a limitation of `demonstrate.py:150-162`,
  which runs every pytest slot against `REPO_ROOT` rather than against the tree
  it just staged. If the tripwire goes red in a throwaway tree, three or four of
  the nine "cannot be shown to fail" are misclassified and `SM-03` must not
  delete them on that reason.

### P06 — the twelve hollow slots are blind to a VACUOUS demonstration, not a missing one

- **Prediction:** `SM-GM-I1` (`pytestmark` skip, pytest exits 0) reports
  `SURVIVES` on `instrument-registry --only complexity-ledger`, while
  `SM-GM-I6` (`allow_module_level=True`, pytest exits 5) reports `DIES` on the
  same detector.
- **Instrument:** `run_gap_mutants.py`.
- **Direction:** a SPLIT — SURVIVES on one skip shape, DIES on the other.
- **NOT entailed**, and it sharpens `FI-06`. The finding says *"`expect_exit = 0`
  … which a fully skipped run satisfies"*. Two skip shapes exist and they exit
  differently; this predicts the finding is right about the mechanism and
  imprecise about its reach. **Read the difference between `SM-GM-I1` and
  `SM-GM-I6`, never their total** — a table that reports "1 of 2 skip mutants
  caught" destroys the only comparison they exist to make.

---

# NEGATIVES

Six. Each states its own falsifier.

### N01 — the `[ports.*]` machinery prices at ZERO on behaviour

- **Prediction:** for the two *behavioural* ports gap mutants (`SM-GM-P1`,
  `SM-GM-P3`), **every column that reports `DIES` today is matched by a `DIES` on
  a detector that outlives `SM-02`.** Neither will flip `DIES` → `SURVIVES` when
  `SM-05` re-runs them after the cut.
- **Instrument:** `run_gap_mutants.py`, before at SM-01 and after at SM-05.
- **Direction:** FLAT — zero mutants change verdict on the surviving detectors.
- **WHAT WOULD FALSIFY IT:** either ports mutant reporting `DIES` on some
  `corpus-port-swap:*` column at `SM-01` and `SURVIVES` on every one of
  `pytest-full`, `suite-real`, `suite-fake` at `SM-05`. One such cell refutes it
  and prices the machinery at more than zero.
- Deliberately scoped to the two behavioural rows. `SM-GM-P2` is excluded and
  predicted the other way by `P02`, so this is not the same claim twice.

### N02 — repairing the instruments will NOT make the suite a finding channel

- **Prediction:** the `suite` channel produces **zero findings** in this round,
  for the sixth round in seven.
- **Instrument:** `SM-05`'s per-channel findings accounting (`GOAL-cheaper`).
- **Direction:** FLAT at zero.
- **WHAT WOULD FALSIFY IT:** `SM-05` attributing one or more findings to the
  `suite` channel. The baseline is `0 : 16 : 1 : 1 : 12` over ~2.6M subagent
  tokens, and a reader would plausibly expect that an epic which *repairs the
  instruments* finally gets something out of running them. I predict it does
  not, and that the dominant channel is again *build the instrument, then ask
  what it cannot report*.

### N03 — the produced-code figures will NOT fall the way the deletion suggests

- **Prediction:** after `SM-02` and `SM-03`, `scripts/` `code_lines` falls by
  **fewer than 1063 lines** — under 5% of the before figure of **21252** — and
  `scripts/` stays above **20189**.
- **Instrument:** `scripts/code_complexity.py scripts --json`, the same command
  that produced `produced-code-before.json`.
- **Direction:** FLAT within 5%.
- **WHAT WOULD FALSIFY IT:** `scripts/` `code_lines` at `SM-05` being **≤
  20189**. A single number, one command, no interpretation.
- Why a reader would expect otherwise: `SM-02` cuts *the centrepiece of a whole
  epic*. The reason I predict it does not show is that the machinery is ~250
  lines of a 2717-line file, and the hollow instruments are TOML rows and test
  files, which `scripts/` does not contain. **If D2 moves, it will not be
  because this number moved much — and if the round argues D2 = 3 from a large
  `scripts/` drop, this row says that drop did not happen.**

### N04 — `D2` will not reach 4, whatever it does about 3

- **Prediction:** neither blind judge scores `D2 = 4` on the removal.
- **Instrument:** the card, two blind judges, `SM-05`.
- **Direction:** FLAT below 4.
- **WHAT WOULD FALSIFY IT:** either judge returning `D2 = 4`. Anchor 4 requires
  the simplification be *shown behaviour-preserving with `D4 ≥ 3`* — a
  model-derived check that the cut broke nothing. The gap mutants are model-
  adjacent but they are not that instrument, and no ticket in this epic is
  scheduled to build one. A judge who reads the existing corpus as satisfying
  `D4 ≥ 3` refutes this, and that judgement is entirely open to them.

### N05 — the gap mutants will move `D3` by nothing, in either direction

- **Prediction:** `D3` scores the same on the removal as its last sealed value,
  from both judges. Zero movement.
- **Instrument:** the card, two blind judges, `SM-05`.
- **Direction:** FLAT.
- **WHAT WOULD FALSIFY IT:** any `D3` cell differing from the last sealed value.
- **This is the one prediction whose failure outranks the epic's headline.**
  `D3` is the only dimension shown to discriminate (4/2/1) *and* hold still —
  zero movement across four rounds and 60 judge-scores. Removing a port-binding
  mechanism is precisely the kind of change that could move it. **A `D3`
  regression is a bigger result than any `D2` outcome and `SM-05` must report it
  first.**

### N06 — the enumerator's own verdict surface is watched by nothing

- **Prediction:** `SM-GM-I5` (`demonstrate.py` always returns 0) reports
  `SURVIVES` on `pytest-full`.
- **Instrument:** `run_gap_mutants.py`, detector `pytest-full`, over all 1335
  tests.
- **Direction:** SURVIVES — zero new failing nodes.
- **WHAT WOULD FALSIFY IT:** any new failing node in the full suite when the
  enumerator's only nonzero exit path is removed.
- **NOT entailed**: `tests/test_instrument_demonstrations.py` is 618 lines and I
  have not established that none of it asserts on that exit path. If it
  survives, then every count `SM-03` is about to report — 40 / 35 / 26 / 9 / 12
  — comes from a program whose verdict nothing checks, and `denominator_rule`
  has to be applied to the enumerator before it is applied to the enumerated.

---

## The scoring table SM-05 fills in

| ID | claim | instrument | direction | verdict | note |
|---|---|---|---|---|---|
| **P01** | fake-side fault dies to the suite, not the binding | gap mutants | DIES/DIES/SURVIVES | | ENTAILED |
| **P02** | manifest drift is the machinery's unique catch | gap mutants | DIES on ports only | | |
| **P03** | `complexity-ledger` is redundant with the suite | gap mutants | DIES on both | | |
| **P04** | enumeration check cannot see an omission | gap mutants | SURVIVES on both | | ENTAILED |
| **P05** | "not constructible" is about the runner | gap mutants | DIES/SURVIVES | | |
| **P06** | hollow slots are blind to VACUOUS, not to MISSING | gap mutants | a SPLIT | | |
| **N01** | the ports machinery prices at zero on behaviour | gap mutants, before vs after | FLAT, zero cells | | negative |
| **N02** | the suite yields zero findings again | channel accounting | FLAT at 0 | | negative |
| **N03** | `scripts/` `code_lines` stays above 20189 | `code_complexity.py` | FLAT within 5% | | negative |
| **N04** | `D2` does not reach 4 | 2 blind judges | FLAT below 4 | | negative |
| **N05** | `D3` moves zero cells | 2 blind judges | FLAT | | negative, **outranks D2** |
| **N06** | nothing watches the enumerator's exit code | gap mutants | SURVIVES | | negative |

**A low or unflattering result is the preferred outcome. An epic that closes
with only good news about itself has not been measured.**
