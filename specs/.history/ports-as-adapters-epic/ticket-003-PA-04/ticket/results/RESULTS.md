# PA-04 — Adapters bind to ports, and the fake/real swap becomes the instrument

**Ticket:** PA-04 · **issue:** #133 · **parent:** `a742624` (PA-01, PA-02, PA-03 merged)
**Corpus:** the PA-03 port corpus, `cases.py` sha1 `08265aff0d81f27f4dfc9694d2a69c3c5b6e695c`
— **byte-identical to PA-03's sealed value.** Same corpus, different binding.

---

## The headline

A fault behind a port, on the side nothing wires, **dies on a generated
instrument for the first time in this project.**

`PA-M12` is `BA-B14` reproduced in a fixture we control: the same semantic as
`PA-M11` ("the read-back hides every CLOSE line") seeded on the other side of one
port. Last epic it survived five corpus instruments, the effect oracle **and**
the hand-written suite — not because it was subtle, but because no composition
point wired that adapter, so nothing ran a line of it.

### Per-mutant, per-instrument, both wirings — `examples/validation/ab/reference_ports/`

1,855 generated port cases · **1,543 executed (83.2%)**, 312 skipped · every
control green on unmutated code (`control_red: []`).

| mutant | class | port-swap real | port-swap fake | action-bound real | action-bound fake | suite-real | suite-fake |
|---|---|---|---|---|---|---|---|
| **PA-M11** real adapter drops CLOSE | adapter_internal | **KILLED** | SURVIVED | **KILLED** | **KILLED** | **KILLED** | SURVIVED |
| **PA-M12** fake adapter drops CLOSE | adapter_internal | SURVIVED | **KILLED** | SURVIVED | SURVIVED | SURVIVED | **KILLED** |
| **PA-M13** fake drifts from real on write | adapter_internal | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | **KILLED** |
| **PA-M14** positive control (ports domain) | wrong_value | SURVIVED | SURVIVED | SURVIVED | SURVIVED | **KILLED** | **KILLED** |

Executable counts are the same for all four corpus columns because **the case
list is identical across them**: `ran = 1543` (1,462 accepting), `skipped = 312`,
`failed = 0` on unmutated code. Per action, real wiring:
`CloseTenant 362 (352 accepting)`, `Commit 388 (384)`, `Release 436 (432)`,
`Reserve 357 (294 accepting), 312 skipped`.

**Read the two `action-bound` columns first.** They are the pre-PA-04 world: the
same corpus, the same adapters, the same runner, and no `[ports.*]` table. With
nothing to swap, `--wiring fake` runs the real adapter, and **PA-M12 is
unreachable under any wiring.** The mapping is the only difference between that
pair of columns and the port-swap pair beside it.

`GOAL-port-reach` target — *"the same adapter-internal fault dies on at least one
generated instrument"* — **MET.** `PA-M12`, on `corpus-port-swap:fake`.

### What did NOT die, stated plainly

**`PA-M13` survives both port columns** and dies only on `suite-fake`. It is not
a reach failure, it is a **refinement gap with a name**: the model's ledger entry
is `<<kind, tenant, n>>` — three fields, no running total — while every tree
writes `COMMIT <tenant> <amount> <total>`. `PA-M13` truncates the fourth field.
Projecting back into the model discards the total, so a fault that corrupts only
the total is invisible to every corpus instrument here, exactly as
`examples/validation/ab/eval/oracle.py:48-52` discloses. The port binding did not
narrow this and could not have.

**`PA-M14`, the ports tree's declared positive control, survives every corpus
column.** This is `PA-03-DF-03` realized precisely as it was filed: `PA-M14`
inflates a held total and lands on `available`, while the port's derived region
is `{closed, committed, ledger}`. No positive control in the catalogue is seeded
inside a port's region, **so every port-scoped column in this table carries a red
positive control and its kill numbers are a FLOOR.**

`PA-03-DF-03`'s `suggested_fix` names PA-04 or PA-06 as the ticket that seeds an
in-region control. **PA-04 did not seed it**, and the reason is sequencing rather
than scope: the catalogue is the instrument under measurement, PA-04 has now seen
its own result, and adding to an instrument after an unflattering signal is the
forbidden act (PA-01 schedule_revision 2 draws exactly this line). Filed forward
as `PA-04-DF-01`; `PA-06` owns it.

---

## Do the arms diverge?

**Yes. One cell.** And it is attributable to a port rather than to prompt length.

### Comparability, stated before the number

Per the epic owner's correction of 2026-08-05 (PA-05's finding, verified against
the sealed source): the strictly comparable set is the **8 mutants that are NOT
{M07, M08, M10}** — the rule is *"not the same diff"*, because M07's per-arm
cells are not the same experiment and M08 and M10 are seeded by **addition**
rather than perturbation. **M09 and N01 ARE in the set.**

The standing baseline is **64 of 64 identical** (PA-03), which is 8 mutants × 8
instruments. It grew from the sealed 56 **because PA-03 added a COLUMN
(`corpus-port`), not because a verdict moved** — naming the instrument change is
required by PA-05's reading rules and this is it.

**PA-04 did not re-run PA-03's eight instruments.** The 64 of 64 is untouched by
this ticket. What follows is a NEW instrument set of three columns per arm, and
it must be read as an addition, never as an extension of that number.

### Harness calibration, before any claim

My `corpus-action-bound` column is an independently built reproduction of PA-03's
`corpus-port` column (subprocess-per-cell, driven through the shipped
`load_mappings`/`apply_wiring`/`adapter_for_case`). Against the sealed
`kill-table-arm-{a,b}.json`:

> **10 of 10 mutants, both arms, cell for cell identical.**

So a divergence below is not a harness artifact.

### The table — 8 comparable mutants × 3 new columns = 24 cells

| mutant | action-bound A | action-bound B | port-swap:real A | port-swap:real B | port-swap:fake A | port-swap:fake B |
|---|---|---|---|---|---|---|
| M01 guard zero amount | KILLED | KILLED | KILLED | KILLED | KILLED | KILLED |
| M02 guard over quota | KILLED | KILLED | KILLED | KILLED | KILLED | KILLED |
| M03 guard close w/ outstanding | KILLED | KILLED | KILLED | KILLED | KILLED | KILLED |
| M04 durable stale total | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED |
| M05 durable close line | KILLED | KILLED | KILLED | KILLED | KILLED | KILLED |
| M06 wrong status on release | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED |
| **M09** negative control, ledger order | KILLED | KILLED | KILLED | KILLED | **KILLED** | **SURVIVED** |
| N01 negative control, outstanding id order | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED |

Excluded by the comparability rule and reported separately: M07 SURVIVED on all
six of its cells; M08 SURVIVED on all six; M10 SURVIVED on all six. So the three
excluded rows would not have changed the count either way.

**23 of 24 comparable cells agree. One diverges: M09 under `corpus-port-swap:fake`.**

`N01` behaves as a negative control must — SURVIVED on every generated column on
both arms — so the row is valid rather than vacuous.

### Why M09 moves, and whether it is really the port

Arm B seeds M09 in `quota_ledger/file_journal.py` — **inside its real driven
adapter**, `boundary_kind = "port"`. Arm A seeds the same semantic in its one
flat module. Under the fake wiring arm B composes over its own `InMemoryJournal`,
so M09 is **not on the executed path at all**; arm A has no second implementation,
so its M09 is always on the path.

It is a port and not prompt length, for three reasons that are each checkable:

1. **The corpus is identical.** Same package, same sha1, same 1,543 executed
   cases on both arms, same skip counts. Nothing about generation differs.
2. **The `:real` column agrees on all 8.** The divergence appears only in the
   column that exists because arm B has a *second implementation* — i.e. only
   where the port is doing work.
3. **Arm A's own port table is present and produces no swap.** `case_adapters.arm-a-port.toml`
   binds the same declared port on arm A; the run reports
   `NO FAKE DECLARED, so --wiring fake ran its REAL adapter`. Arm A is not
   excluded from the instrument — it is bound to it and has nothing behind it.

**The honest objection, recorded:** M09 is anchored in different files on the two
arms, so a skeptic can call this a property of the catalogue's re-anchoring
rather than of the port. The answer is that the re-anchoring was **forced**:
arm B's durable write lives in its adapter, so there is nowhere else in arm B for
"prepend instead of append to the durable record" to be. The anchoring difference
*is* the architectural difference. A reader who rejects that argument should
score this divergence as unattributed; the data is in
`results/swap-arm-a.json` and `results/swap-arm-b.json` either way.

`GOAL-cases-drive-ports` target — *"verdicts diverge on at least one cell, and
the divergence is attributable to a port rather than to prompt length"* —
**MET on the new columns, with the caveat above.** PA-06 decides it.

---

## Determinism

Two full runs of every subject, byte-compared:

| subject | run 1 vs run 2 |
|---|---|
| `reference_ports` | **byte-identical** (`sha1 46fd980c…`) |
| `arm_a` | **byte-identical** |
| `arm_b` | **byte-identical** |

Each cell runs in a **fresh interpreter**. `EVAL-RERUN-DF-01` is why: a purge
keyed on a fixed list of binding-module names left a module holding a handle on
the pristine tree, every mutant executed against unmutated code, and the run
reported 11 of 11 SURVIVED with green controls. A subprocess cannot hold a stale
handle, so that class of bug is unreachable here by construction rather than by
a list being correct.

---

## Every run states its oracles

`results/runner-oracle-statement.txt`, both wirings, from the shipped CLI.

Widened from HP-04, which printed this **only when semantic providers were
configured** — so the runs carrying the fewest oracles were the ones that said
nothing. It now prints on every run, and names five: output-conformance,
projected-state-conformance, effect-conformance, mutation-kill-test and PA-04's
port-fake-real-swap. `mutation-kill-test` is in the NOT-CARRIED list on every
run, permanently: it is `scripts/kill_test.py`, and a green run here is not
evidence any fault would die.

A swap run also states the side it ran and refuses to speak for the other:

> `port-fake-real-swap on ledger.LedgerAppendPort: THIS RUN USED THE FAKE SIDE. One run
> decides one side of a port; a fault seeded in the other implementation is not on this
> run's executed path at all, so this column must be read beside its opposite wiring or
> not at all`

---

## What was REJECTED

1.  **A `[ports.*]` binding resolved by sniffing the `port:` label prefix.** It
    needs no schema and works today, because port cases already carry the label.
    Rejected: the acceptance criterion is that the binding is *readable from the
    mapping rather than inferred*, and a prefix convention is inference. Worse,
    with a prefix rule and no `binds` field, precedence between a port binding
    and an action binding falls back to insertion order — so which adapter drove
    every case in this ticket would have depended on which table someone typed
    first, with nothing on the page saying so.

2.  **`--wiring both`, running the pair in one invocation and reporting a merged
    verdict.** Convenient and wrong. A merged cell hides which side decided it,
    and the whole finding here is that `PA-M11` and `PA-M12` are decided by
    *different* sides. Two runs, two columns, and the run output says which side
    it was.

3.  **Refusing `--wiring fake` when a port declares no fake.** The obvious
    ergonomic choice and a new gate. It would make `--wiring` refuse based on how
    a codebase is shaped, which is `no_new_gates_rule` exactly; arm A would have
    become unrunnable rather than measurable, and "arm A has no second
    implementation" is the *result*, not an error condition.

4.  **Seeding an in-region positive control to make the port columns green.**
    `PA-03-DF-03` names PA-04 as a candidate and its `suggested_fix` even
    supplies the fault ("a COMMIT line written with the wrong tenant"). Rejected
    on sequencing: PA-04 has already seen its own numbers, and repairing an
    instrument *after* an unflattering signal is the forbidden act. Reported red;
    filed forward.

5.  **Adding a fake composition point to arm B's own tree.** Arm B is a sealed,
    judged artifact and its D3 = 4 was awarded for the shape it has. The fake
    wiring is composed in the *measurement* tree
    (`measure/arm_b_fake.py`) out of names arm B itself exports, and copied into
    a throwaway copy at run time. The arm on disk is byte-identical to what was
    judged.

6.  **Widening the port case into a `StateGraphPortInteraction`** — an expected
    output naming the port, the operation and the payload, asserting the port was
    invoked exactly once. PA-03 rejected it for want of an adapter that could
    produce it and said "PA-04 can widen it". Rejected again, for a better
    reason: it would have made the port column a *different* assertion from every
    other column, and the divergence measured above would then be confounded by
    the assertion having changed. The narrowed-`after` form keeps the assertion
    constant so that the only variable is the binding. It remains available and
    is now the strictly better next step, since the confound is spent.

7.  **Repairing the effect oracle's 8-of-18 reach.** It is offered as mine if it
    blocks me and it did not block me: the port instrument here is the corpus
    runner, not `effect_conformance.py`, and the swap needs no `run()` on any of
    the nine adapters that lack one. Touching it would have been an unbounded
    edit during a measurement.

---

## Reproduction

```bash
# the corpus (PA-03's, unchanged; exits 2 on the uncalibrated 200-case cap)
python3 scripts/tla_spec_dev.py --spec-root specs generate cases \
  examples/validation/ab/model/QuotaLedger.tla examples/validation/ab/model/QuotaLedger.cfg \
  --out <scratch>/specs/corpus-port --package quota_port --view internal \
  --negative-cases with-positive --port-cases only

# the swap, per subject
M=specs/results/scorecards/ports-as-adapters/GOAL-port-reach/measure
for S in reference_ports arm_a arm_b; do
  python3 $M/run_port_swap.py --subject $S \
    --cases <scratch>/specs/corpus-port/spec-unit/quota_port --out results/swap-$S.json
done

# the shipped runner, either side of the port
QUOTA_LEDGER_DIR=$PWD/examples/validation/ab/reference_ports QUOTA_LEDGER_BINDING=ports_binding \
python3 scripts/run_generated_case_adapters.py <scratch>/specs/corpus-port/spec-unit/quota_port \
  --mapping $M/case_adapters.port-swap.toml \
  --port-manifest examples/validation/ab/model/spec_manifest.yaml \
  --import-root $M --import-root <scratch>/specs/corpus-port/spec-unit \
  --wiring real --batch          # and --wiring fake
```

## Acceptance

```
uv run --with pytest --with pyyaml python -m pytest tests -q
# 1120 passed

python3 scripts/tla_spec_dev.py --spec-root specs run spec-unit-tests --scope project
# see specs/tickets/PA-04/results/
```

`model_delta_expectation: none expected` — **held.** No TLA+ state, action or
config changed. `[ports.*]` is a binding table; `--wiring` is a harness flag.
