# FI-01 — narrative ledger

**A positive control inside the port's region, and a probe that can fail.**
Goes first and alone; nothing else in the epic dispatches until this is sealed,
because a control seeded after its numbers are known is not a control.

`model_delta_expectation: none expected`, and the measured delta is
`direction=zero (vs PA-06)`. No TLA+ model, `.cfg`, manifest or production
module changed. Everything below is the A/B fixture and its instruments.

---

## 1. What was wrong, measured rather than argued

`corpus-port` executes **1855 port cases** against `reference_ports` — 388
`Commit`, 669 `Reserve`, 294 of them accepting — and reported **both** declared
positive controls `SURVIVED`, with
`polarities_with_no_deciding_control: ["positive"]`. It was not failing to reach
the tree.

A port case narrows its expected `after` to the port's **derived region**, which
the generator prints for this fixture as

```
ledger.LedgerAppendPort: 1855 case(s); region {closed, committed, ledger}
```

`M07` lands on `available`. `PA-M14` lands on the amount recorded on a
reservation. Neither is in that set, so **no port-scoped instrument could have
decided either one**, and every port-scoped kill number the predecessor epic
produced is a floor under a red control — including its headline.

And the probe that certified the control could not fail. `PA-06-DF-07`: it
tested only *"invisible before an accepted reserve"*, so a mutant whose
`replace` was the identical line plus a comment reported `HOLDS`. Measured
again here on the parent commit `d25c467`, with the probe exactly as it shipped:

| input | parent probe |
|---|---|
| a no-op (line + comment) | `HOLDS` |
| `PA-M14`, the shipped control | `HOLDS` |
| a fault landing outside the port's region | `HOLDS` |

Three broken controls, three passes. Fixing the control without fixing the probe
re-creates the defect with the sign flipped, which is what PA-01 did and what
`PREDICTIONS-PA.md` P07 named in advance as *"this epic's worst possible own
goal"*.

---

## 2. What was built

**The probe runs both halves.** A declared property now carries an `absent`
plan (must show no difference), a `present` plan (must show one, in **one step**,
because every generated corpus case is single-action) and a `region` (at least
one moved observable must be inside it). Verdicts: `HOLDS`, `BROKEN` (leaks
before its own path), `INERT` (invisible after it too — the no-op case),
`OUT_OF_REGION`, `ERROR`.

**Region is an INCLUSION test, never a confinement test.** That is
`PA-06-DF-07`'s lesson applied rather than repeated. Arm B derives `available()`
from `committed`, so a fault on `committed` moves `available` there and moves
nothing outside the region on a tree that stores it. A confinement test would
call the same control fine on one tree and broken on another for a reason about
data structures. The probe reports the full moved set beside every verdict, so
confinement is visible as a measurement and decides nothing.

**R1 — the demonstrated failing input.** `probe_demonstrations.toml` holds five
controls, four broken on purpose and one correct, each declaring the verdict the
probe must return. `check_catalogue.py --demonstrate` passes only if the probe
reports every broken one broken. The rows are the defects that actually
happened, not invented ones: the no-op (`PA-06-DF-07 b`), a control observable
from construction (arm B's `M07`), one outside the port's region
(`PA-03-DF-03`), and `PA-M14`'s own two-step mutation verbatim.

**FI-M15, the in-region control**, seeded on the two trees that declare a port —
`reference_ports/domain.py` and arm B's `quota_ledger/domain.py`. `commit`
credits one unit more than the reservation held, so `committed(t)` and the
COMMIT line's running total are both wrong, and nothing at all differs until an
accepted `commit` executes. It is in **nobody's** gap by construction: it moves
a projected state variable (so a silent mapping still sees it) *and* the durable
line (so a content-asserting one sees it twice), and it needs one action.

**`extends` is executable** (`PA-06-DF-02`). `[pa_control_properties]` is read
through the parent a catalogue names. Arm B's control file declares **no**
property table and resolves correctly; a test asserts it still declares none, so
the inheritance cannot rot into another copied table.

---

## 3. What it measured

| | corpus-port-swap:real | :fake | corpus-action-bound:real | :fake | suite-real | suite-fake |
|---|---|---|---|---|---|---|
| **FI-M15** | KILLED | KILLED | KILLED | KILLED | KILLED | KILLED |
| **PA-M14** | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED | KILLED |

`run_port_swap.py` (PA-04's driver, unmodified, fresh interpreter per cell), on
a port corpus generated at this commit. `FI-M15`'s control verdict is **GREEN**;
`PA-M14` is **RED on all four corpus columns**, each of which executed 294
accepting `Reserve` cases. The prediction `predicted_corpus_port = KILLED` was
committed at `2cce78c`, before any of it ran.

Arm B, through the shipped `port_corpus_run.py`: clean **1543 ran / 0 failed**;
with `FI-M15` applied **384 failed**, all of them `Commit`, first message
`committed: expected {'t1': 1, 't2': 0}, actual {'t1': 2, 't2': 0}` — a name
inside the port's declared region.

`PA-M11`, `PA-M12` and `PA-M13` reproduce PA-04's and PA-06's sealed cells
exactly. FI-01 added a **row**; it moved no **cell**.

---

## 4. R2 — the control that could not be made to work

`PA-M14` is measured **INERT** on `reference_ports`: invisible after one
accepted reserve as well as before one, because no query exposes a reservation's
amount and this tree stores `available` rather than deriving it. Two actions are
needed and every generated case runs one.

It is **not deleted, not re-seeded, not re-anchored and not excused.** It still
runs, is still declared a positive control, is still probed on every `--controls`
run, and prints `INERT` every time. `check_catalogue.py --controls` exits 1 on
the shipped catalogue because of it, and that is the correct output.

The per-tree rule moved from *"exactly one positive control"* to *"at least one,
and at least one that HOLDS its property when probed"*. That is a
strengthening: one **broken** control satisfied "exactly one" perfectly, which is
the state `PA-06-DF-07` found. Deleting a broken control to keep a count at one
is how a measured defect disappears.

---

## 5. What this does NOT show

- It does **not** show the port machinery catches anything the hand-written
  suite does not. `FI-M15` dies to every column including both suites — which is
  what a control in nobody's gap is supposed to do, and it adds no evidence
  either way to `PA-06-DF-09`.
- It does **not** retroactively convert any earlier port-scoped number from a
  floor into a count. Those runs had no deciding positive control; that is a
  fact about them.
- It does **not** show that any *arm* carries an in-region fault of interest.
  `FI-M15` is a control, deliberately blatant, and `PA-06-DF-04` — no arm
  carries an adapter-internal fault at all — is untouched.
- The fixture and the mutants seeded into it still share an author.

---

## 6. Findings filed, not fixed

`FI-01-DF-01` **(blocking)** — `run_controls.py` cannot measure the ported tree:
its module purge is keyed on the name `quota_ledger`, so `domain`,
`journal_file` and `journal_memory` stay cached and every mutant seeded in them
executes against unmutated code. It reports **15 of 15 SURVIVED** with no error.
`EVAL-RERUN-DF-01` recurring in the one place that finding's repair does not
reach. No sealed number is contaminated — PA-04 and PA-06 used fresh
interpreters — and FI-01 measured with `run_port_swap.py` for that reason.

`FI-01-DF-02` (minor) — `check_integrity` makes a measurement catalogue's
obligations of a supplement catalogue, so probing one control on one arm prints
sixteen true-but-misdirected complaints.

`FI-01-DF-03` (minor) — the second half of `PA-06-DF-02`'s fix (delete the three
duplicated property tables) is not taken: they are sealed evidence under
`specs/results/`, which FI-01 does not write.

`FI-01-DF-04` (minor) — **self-audit.** `PORT_REGION` is a transcription of the
generator's output, not a reading of it. It is the one declaration FI-01 added
that nothing executes against its source. The failure direction is the safe one
(a false RED, not a false green) and it is still the shape of the rule this
ticket quotes three times.
