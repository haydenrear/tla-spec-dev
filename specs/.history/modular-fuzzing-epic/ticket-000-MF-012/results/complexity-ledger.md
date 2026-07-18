# MF-012 Complexity Ledger

Manual ledger per the standing objective in `references/architecture_tractability.md`
("Programming As Complexity Minimization"). The mechanized ledger arrives with
MF-019; until then this is recorded by hand. The complexity delta is reported
**jointly** with behavior-retention evidence, never on its own.

Model: `TlaSpecDevCli` (single-module baseline; the Internal/External split is a
recorded known gap, out of epic scope).

## 1. Measured delta introduced by this ticket

| Metric | Baseline (epic tip `cc765f6`) | After MF-012 | Delta |
|---|---|---|---|
| Distinct states | 917 | 919 | **+2 (+0.22%)** |
| States generated | 3660 | 3664 | +4 |
| Search depth | 20 | 21 | +1 |
| State variables | 12 | 13 | +1 (`budgets_recorded`) |
| Actions | 9 | 10 | +1 (`RecordBudgets`) |
| Invariants | 8 | 10 | +2 |

Commands:

```
bash scripts/run_tlc.sh specs/tickets/MF-012/current/TlaSpecDevCli.tla \
                        specs/tickets/MF-012/current/MC.cfg
```

The increase is +2 distinct states rather than a doubling because
`budgets_recorded` is a **sequential gate**, not a free-floating flag:
`RecordBudgets` is enabled only after `ScaffoldProject`, and `ScaffoldWorkflow`
requires it. The two new invariants (`BudgetsRequireProject`,
`WorkflowRequiresBudgets`) pin that ordering, so the flag never combines freely
with the rest of the state.

This is a genuine behavior addition (budgets become per-program program state),
so a small complexity increase is expected and is not a regression.

## 2. Behavior retention evidence (joint requirement)

| Constraint | Evidence | Result |
|---|---|---|
| All invariants hold | `results/tlc-current.txt` | 10/10, no error found |
| Program represented in entirety | All 9 baseline actions retained; 1 added | no action removed |
| Spec-unit conformance | `results/spec-unit-tests.txt` | 8 + 10 passed (2 targets) |
| Repository units | `results/repository-unit-tests.txt` | 117 passed (106 baseline + 11 new) |
| External surface (Test Graph) | `results/graph-reports/specWorkflow-*` | 8/8 nodes passed |
| CLI surface (Test Graph) | `results/graph-reports/cliWorkflow-*` | 2/2 nodes passed |
| Kill rate | n/a | mutation kill test arrives with MF-016 |

No behavior was dropped, no domain narrowed, no boundary removed. The
complexity number went **up** by 2 states and is reported as such — this ticket
does not claim a reduction from its own delta.

## 3. Standing-objective search: reduction found (recommendation, NOT applied)

Searched for a design retaining every behavior at lower measured complexity.
**One real reduction was found and measured.** It is an architectural
representation change, so per `references/architecture_tractability.md` it is a
**recommendation requiring explicit user approval** and has deliberately been
left unapplied on this branch.

### Finding: collapse three parallel progress flags into one ordinal

`desired_ready`, `current_ready`, and `spec_unit_tests_passed` are three
parallel `[Tickets -> BOOLEAN]` functions constrained into a strict total order
by `CurrentRequiresDesired` and `SpecUnitTestsRequireCurrent`. Only 4 of their
8 per-ticket combinations are reachable; the other 4 exist in the declared
state space purely to be excluded by invariants.

Replacing them with a single ordinal `ticket_phase \in [Tickets -> 0..3]`
(0=open, 1=desired, 2=current, 3=spec-units-passed) makes the ordering
**structural** rather than invariant-enforced.

Measured on a scratch variant (`MC.cfg` unchanged, 3 tickets):

| Metric | MF-012 as landed | Ordinal variant | Delta |
|---|---|---|---|
| State variables | 13 | 11 | **-2** |
| Distinct states | 919 | 919 | 0 (unchanged) |
| States generated | 3664 | 3184 | **-480 (-13.1%)** |
| Search depth | 21 | 21 | 0 |
| Declared state-space bound | 3,145,728 | 393,216 | **-87.5% (8x)** |
| Invariants holding | 10/10 | 10/10 | retained |

The declared-bound figure is the product of the variable domains excluding
`lastCommand`/`result`: the three 2^3 flag functions (512) become one 4^3
ordinal (64).

**Why this is not gaming the metric:** the reachable-state count is *identical*
(919) and the search depth is *identical* (21) — every behavior of the program
is still represented and still explored. What shrinks is the unreachable
declared space and the redundant generated transitions. No action, domain, or
boundary is removed. This is exactly the "same behaviors, cheaper
representation" case the standing objective asks for.

**Cost/risk:** it touches `CurrentRequiresDesired`,
`SpecUnitTestsRequireCurrent`, and `ClosedTicketsPassedSpecUnitTests`, whose
ordinal forms become near-tautological; a reviewer may prefer the explicit
boolean flags for readability, and the three named spec-unit adapter surfaces
map 1:1 onto the current flags. It also conflicts with the `tla` conflict key
of MF-011/MF-014/MF-016, which are already scheduled against this module.

**Recommendation:** defer to the epic owner. If accepted, it is best applied as
its own amendment ticket after the wave-2 tickets land, not folded into MF-012.

Scratch variant used for measurement is not committed; it is reproducible from
the description above.
