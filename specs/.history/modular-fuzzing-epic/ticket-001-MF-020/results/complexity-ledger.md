# MF-020 complexity ledger — ticket_phase ordinal collapse

Standing objective: `references/architecture_tractability.md`. This ticket **is**
a complexity reduction, so the delta is recorded **jointly** with retention
evidence — a reduction without retention proof is the gaming pattern the
objective rejects.

Move type: **abstract** (re-represent, do not decompose or refactor).
Owner-approved before scheduling, via the MF-012 ledger.

## 1. Retention evidence (recorded first, deliberately)

The reduction below is only admissible because these numbers are unchanged.

| Retention metric | MF-012 baseline | MF-020 | Verdict |
|---|---|---|---|
| Reachable distinct states | 919 | **919** | identical |
| Search depth | 21 | **21** | identical |
| Invariants checked / holding | 10/10 | **10/10** | identical |
| TLC result | no error | **no error** | identical |

Baseline measured on this branch before editing (same command, same `MC.cfg`) and
after: both `3664 states generated, 919 distinct states found`, depth 21.
Evidence: `tlc-current.txt`, `tlc-desired.txt`.

Equality in **both** directions is the point. Fewer reachable states would mean
behavior was deleted; more would mean the ordinal admits states the booleans did
not. Neither occurred.

## 2. Complexity delta

| Metric | Before | After | Delta | Target | Met |
|---|---|---|---|---|---|
| State variables | 13 | **11** | -2 | -2 (13->11) | yes |
| Declared state-space bound | 3,145,728 | **393,216** | -87.5% (8x) | 393,216 | yes |
| States generated | 3,664 | **3,664** | 0 | 3,183 | **no — see §4** |
| Distinct states | 919 | 919 | 0 | 0 | yes |
| Search depth | 21 | 21 | 0 | 0 | yes |

Declared bound arithmetic (product of variable domains, excluding
`lastCommand`/`result`, 3 tickets, 2 spec roots):

```
common factors: cli_built 2 * cli_installed 2 * spec_root 3
              * project_scaffolded 2 * budgets_recorded 2 * workflow_scaffolded 2
              * active_tickets 2^3 * closed_tickets 2^3                 = 6,144
before: 6,144 * (2^3 * 2^3 * 2^3 = 512 three-boolean combos)  = 3,145,728
after:  6,144 * (4^3 =  64 ordinal combos)                    =   393,216
```

The unreachable-state elimination is exact: per ticket the booleans declared 8
combinations of which the ordering invariants permitted only 4.

**Note on `MC.cfg`:** the declared bound is *not* a literal in `MC.cfg` or any
manifest (grep for `3145728` / `393216` / `bound` returns nothing). It is derived
from the variable domains, so the 8x reduction is structural rather than an edit.
The issue's phrasing implied a literal to shrink; there is none. `MC.cfg` is
unchanged — all 10 invariants and all constants retained.

## 3. What was NOT done

- No action added, removed, or renamed. No CLI surface. No new behavior.
- No invariant dropped: all 10 retained in the module and in `MC.cfg`. The full
  site-by-site mapping is `invariant-mapping.md`.
- `specs/program_model/*` left untouched, matching the MF-012 precedent — it is
  the frozen accepted baseline, promoted wholesale at epic finalization. Its
  `spec_manifest.yaml` state block still names the three booleans and must be
  updated then; its module still declares them, so updating one without the other
  would desync it.
- Neither `production_adapters.py` references any of the three booleans (both are
  port/command adapters that shell out to the CLI and carry no TLA state
  mapping), so no adapter code change was required. Verified by grep.

## 4. Finding: the generated-states target was not met, and should not have been

The expected -13.1% generated-state drop (3,664 -> 3,183) **did not occur**.
Shipped model: 3,664 generated, unchanged.

Root cause, measured both ways with all else equal:

| `RunSpecUnitTests` guard | Distinct | Depth | Generated |
|---|---|---|---|
| `ticket_phase[ticket] >= 2` (shipped) | 919 | 21 | 3,664 |
| `ticket_phase[ticket] = 2` (tightened) | 919 | 21 | 3,184 |

The MF-012 ledger's projected reduction is reproducible **only** with the
tightened `= 2` guard. The baseline `RunSpecUnitTests` has no
`~spec_unit_tests_passed` guard, so it re-fires on an already-passing ticket — an
idempotent re-run self-loop that matches the real CLI (spec-unit tests are
re-runnable). Tightening to `= 2` deletes that transition from the transition
relation.

That deletion is **invisible to the retention gate**: the self-loop returns to an
already-known state, so distinct states and depth both stay at 919/21. It would
have hit the target number while quietly removing behavior — exactly the failure
the standing objective warns about, and exactly why it must not be adopted to
make a metric.

**Decision: shipped `>= 2`.** MF-020 is scoped as a pure representation change,
so the transition relation is preserved exactly. The `= 2` tightening is a
behavior change and is recorded in §6 as a recommendation, not applied.

The MF-012 ledger's own figure should be read as a *pure-representation* -0%
generated-state change plus a *separate, unlabelled* behavior tightening worth
-13.1%. That conflation is itself a finding for the owner.

## 5. Retention gate did real work

A mechanical collapse of the `UNCHANGED` frame lists left `ticket_phase` framed
in the three actions that assign it. TLC reported `variable ticket_phase was
changed while it is specified as UNCHANGED` and the state space collapsed to
**23 distinct states at depth 9**. Caught and fixed before close; recorded here
because it is direct evidence that the 919-state gate is load-bearing rather than
ceremonial.

## 6. Refinement search — further reduction FOUND (recommendation only)

Per the recursive refinement loop, the collapsed model was re-examined for the
same pattern. **A further reduction of the same kind exists and was prototyped
and measured.**

### Candidate A — `setup_phase` bootstrap chain (measured, recommended)

`cli_built`, `cli_installed`, `project_scaffolded`, `budgets_recorded`, and
`workflow_scaffolded` form a strict linear bootstrap chain, pinned by
`CliInstalledRequiresBuilt`, `BudgetsRequireProject`, `WorkflowRequiresBudgets`,
`WorkflowRequiresProject` and the action guards:

```
BuildSkillCli -> InstallLocalCli -> ScaffoldProject -> RecordBudgets -> ScaffoldWorkflow
```

Only 6 of their 2^5 = 32 combinations are reachable. Collapsing them into
`setup_phase \in 0..5` is the identical "abstract" move this ticket performs.

Prototyped and run under the ticket's own `MC.cfg`:

| Metric | MF-020 as shipped | `setup_phase` prototype | Delta |
|---|---|---|---|
| State variables | 11 | **7** | **-4** |
| Declared bound | 393,216 | **73,728** | **-81% (5.33x)** |
| Distinct states | 919 | **919** | 0 (retained) |
| Search depth | 21 | **21** | 0 (retained) |
| States generated | 3,664 | **3,664** | 0 |
| Invariants | 10/10 | 10/10 | retained |

Evidence: `refinement-probe/TlaSpecDevCli.tla`,
`refinement-probe/tlc-setup-phase-probe.txt`.

Combined with MF-020, this would take the original 13-variable / 3,145,728-bound
model to **7 variables / 73,728** — a 42.7x bound reduction — at identical
reachable behavior.

**Not applied.** This is an architectural move outside the assigned scope and
requires explicit owner approval. Recommended as a follow-up ticket. Note it
would touch `MC.cfg`'s invariant list semantics the same way MF-020 did (four
more invariants become structurally valid), and it should be scheduled with the
same MF-011 ordering logic that motivated MF-020 — before the complexity gate is
calibrated, not after.

### Candidate B — merge `active_tickets` / `closed_tickets` / `ticket_phase` (not prototyped)

`NoOpenClosedOverlap` makes the two sets disjoint, and `ticket_phase` is only
meaningful while a ticket is active. A single per-ticket lifecycle ordinal
`ticket_state \in [Tickets -> 0..5]` (untouched, active@0..3, closed) would
replace three variables with one: declared factor `8 * 8 * 64 = 4,096` becomes
`6^3 = 216`, a further ~19x on that factor.

Lower confidence than Candidate A: `active_tickets`/`closed_tickets` are used as
sets (membership, union, difference) rather than as flags, so the rewrite is less
mechanical and the readability cost is higher. **Not prototyped, not applied** —
recorded for the owner as a lead, not a recommendation.

### `= 2` guard tightening (recorded, explicitly NOT recommended as a complexity move)

Worth -480 generated states (-13.1%) at unchanged distinct/depth, but it removes
the idempotent spec-unit re-run transition (§4). If the owner decides the model
should forbid re-running spec-unit tests on a passing ticket, that is a
**behavior decision** to be ticketed as such — not a complexity reduction, and it
should not be counted as one in any ledger.

## 7. Summary

Complexity reduced (-2 variables, 8x declared bound) with retention proven by
exact equality of reachable states (919) and depth (21). One expected metric
(generated states) was not met, and the ledger records why meeting it would have
required deleting behavior. A further, larger reduction was found, prototyped,
measured, and left for owner approval rather than taken unilaterally.

## 8. Known repo issues encountered during close-out

Both were anticipated by the assignment; neither was fixed beyond what unblocked
this ticket.

**#22 — promotion silently drops files under `specs/current/tests/`.** Hit.
`tla-spec-dev close ticket MF-020` deleted
`specs/current/tests/test_current_ticket_workflow.py` during promotion. That file
held both MF-012's `test_current_model_carries_the_budgets_gate` and this
ticket's new `test_current_model_carries_the_ticket_phase_ordinal`. It was **not**
captured in the history seal either, so the on-disk copy was the only one. It was
restored from `HEAD` and the MF-020 test re-applied, then the full matrix was
re-run green against the promoted state. The same pattern also dropped the
`results/refinement-probe/` subdirectory from the sealed evidence (directories,
not just files), which was likewise restored.

Impact if unnoticed: MF-012's own retention test would have been silently deleted
by the next ticket's promotion. Worth raising the priority of #22 — it deletes
regression coverage rather than merely failing to copy it.

**#23 — history seal captures whole test-graph working trees.** Observed as
expected; the seal is large. Not this ticket's bug, not addressed.

## 9. Post-promotion revalidation

Full matrix re-run after promotion and after restoring the #22 casualty:

| Check | Result |
|---|---|
| TLC on promoted `specs/current` | 3,664 generated, **919 distinct, depth 21**, no error |
| `run spec-unit-tests` | 13 passed, validation passed |
| `pytest tests -q` | **117 passed** (no regression) |
| `specWorkflow` graph | BUILD SUCCESSFUL (8/8 nodes) |
| `cliWorkflow` graph | BUILD SUCCESSFUL (2/2 nodes) |
