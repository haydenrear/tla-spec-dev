# MF-020 — before/after mapping: three booleans -> `ticket_phase` ordinal

Enumerated **before** editing `TlaSpecDevCli.tla`, per the ticket method. This is
the artifact that proves no guard or invariant was silently dropped: every site
below comes from the baseline module at epic tip `09b34a1`
(`specs/tickets/MF-020/current/TlaSpecDevCli.tla`, the post-MF-012 whole-program
current, 13 variables / 10 invariants), and each has a named successor in the
ordinal model.

## Encoding

`ticket_phase \in [Tickets -> 0..3]` — the count of lifecycle milestones reached:

| phase | meaning | old boolean triple `(desired, current, unit)` |
|---|---|---|
| 0 | opened, nothing done | `(F, F, F)` |
| 1 | desired model updated | `(T, F, F)` |
| 2 | current model updated | `(T, T, F)` |
| 3 | spec-unit tests passed | `(T, T, T)` |

The baseline's own `CurrentRequiresDesired` and `SpecUnitTestsRequireCurrent` pin
the triple to a strict total order, so exactly these 4 of 8 combinations are
reachable. The other 4 — `(F,T,F)`, `(F,T,T)`, `(F,F,T)`, `(T,F,T)` — are
declared but unreachable. The ordinal is a **bijection onto the reachable set**,
which is why the reachable-state count must be unchanged.

Atom translation, used uniformly:

```
desired_ready[t]           ==  ticket_phase[t] >= 1
current_ready[t]           ==  ticket_phase[t] >= 2
spec_unit_tests_passed[t]  ==  ticket_phase[t] >= 3
~desired_ready[t]          ==  ticket_phase[t] = 0     (given the order invariant)
~current_ready[t]          ==  ticket_phase[t] <= 1
```

## 1. Declarations and state tuple

| Baseline (lines) | After |
|---|---|
| `VARIABLES ... desired_ready, current_ready, spec_unit_tests_passed, ...` (18-20) | single `ticket_phase` |
| `vars == << ... >>` (33-35) | single `ticket_phase` entry |

State variables 13 -> 11 (remove three, add one). **Measured 11.**

## 2. `Init`

Baseline (51-53), three conjuncts initialising each boolean to `FALSE`, collapse
to one: `/\ ticket_phase = [t \in Tickets |-> 0]`. `(F,F,F) -> 0` is exact.

## 3. Action guards and updates

| Action | Baseline guard / update | After | Note |
|---|---|---|---|
| `BuildSkillCli` | three in `UNCHANGED` (73-75) | `ticket_phase` in `UNCHANGED` | frame only |
| `InstallLocalCli` | three in `UNCHANGED` (94-96) | `ticket_phase` in `UNCHANGED` | frame only |
| `ScaffoldProject` | three in `UNCHANGED` (117-119) | `ticket_phase` in `UNCHANGED` | frame only |
| `RecordBudgets` (MF-012) | three in `UNCHANGED` (144-146) | `ticket_phase` in `UNCHANGED` | frame only |
| `ScaffoldWorkflow` | three in `UNCHANGED` (169-171) | `ticket_phase` in `UNCHANGED` | frame only |
| `OpenTicket` | sets all three `FALSE` (187-189) | `ticket_phase' = [ticket_phase EXCEPT ![ticket] = 0]` | reset preserved; frame has no boolean entries, so nothing to drop |
| `UpdateTicketDesired` | guard `~desired_ready[ticket]` (207); set `desired_ready := TRUE` (208); other two in `UNCHANGED` (218-219) | guard `ticket_phase[ticket] = 0`; set `= 1`; **`ticket_phase` removed from frame** | `~desired` forces the other two `FALSE` by the order invariant, so `(F,F,F) -> (T,F,F)` is exactly `0 -> 1` |
| `UpdateTicketCurrent` | guard `desired_ready /\ ~current_ready` (228-229); set `current_ready := TRUE` (230); other two in `UNCHANGED` (240-241) | guard `ticket_phase[ticket] = 1`; set `= 2`; **`ticket_phase` removed from frame** | `unit=F` forced by the order invariant, so `(T,F,F) -> (T,T,F)` is exactly `1 -> 2` |
| `RunSpecUnitTests` | guard `current_ready[ticket]` (253); set `spec_unit_tests_passed := TRUE` (254); other two in `UNCHANGED` (264-265) | guard `ticket_phase[ticket] >= 2`; set `= 3`; **`ticket_phase` removed from frame** | **`>=` not `=` is load-bearing** — see §7 |
| `CloseTicket` | guard `desired /\ current /\ unit` (277-279); three in `UNCHANGED` (290-292) | guard `ticket_phase[ticket] = 3`; `ticket_phase` in `UNCHANGED` | conjunction of all three is exactly phase 3; action does not write the phase, so the frame entry is correct here |

### Frame-list hazard (caught by the retention gate)

The three actions that *write* `ticket_phase` each listed the two booleans they
did not touch in `UNCHANGED`. Mechanically collapsing those into a `ticket_phase`
`UNCHANGED` entry contradicts the assignment in the same action. TLC reported
`variable ticket_phase was changed while it is specified as UNCHANGED` and the
state space fell to **23 distinct states at depth 9**. The fix is to drop the
frame entry entirely in exactly those three actions. `OpenTicket` and
`CloseTicket` are unaffected — the former's frame never listed the booleans, the
latter does not write the phase.

This is the failure mode the 919-state gate exists to catch, and it caught it.

## 4. Invariants — all 10 retained, none dropped

| Invariant | Baseline | After | Status |
|---|---|---|---|
| `TypeInvariant` | three `\in [Tickets -> BOOLEAN]` (327-329) | `ticket_phase \in [Tickets -> 0..3]` | retained, tightened |
| `CurrentRequiresDesired` | `current_ready[t] => desired_ready[t]` (353-355) | `ticket_phase[t] >= 2 => ticket_phase[t] >= 1` | retained, now structurally valid |
| `SpecUnitTestsRequireCurrent` | `spec_unit_tests_passed[t] => current_ready[t]` (357-359) | `ticket_phase[t] >= 3 => ticket_phase[t] >= 2` | retained, now structurally valid |
| `ClosedTicketsPassedSpecUnitTests` | `\A t \in closed_tickets: spec_unit_tests_passed[t]` (361-363) | `\A t \in closed_tickets: ticket_phase[t] >= 3` | retained, still substantive |
| `CliInstalledRequiresBuilt`, `WorkflowRequiresProject`, `BudgetsRequireProject`, `WorkflowRequiresBudgets`, `ProjectChoosesKnownSpecRoot`, `NoOpenClosedOverlap` | untouched | untouched | not in scope (6, incl. MF-012's two budget invariants) |

The two ordering invariants become tautologies over the ordinal. **They are
deliberately kept** in the module and in `MC.cfg` rather than deleted: keeping
them documents that the constraint still holds and was absorbed into the
representation rather than dropped. Their becoming unfalsifiable *is* the
complexity reduction — the illegal states are no longer expressible.

## 5. `MC.cfg`

`INVARIANTS` (all 10) and `CONSTANTS` are unchanged. **The declared bound is not
a literal anywhere in `MC.cfg`** — it is derived from the product of the variable
domains. Grep for `3145728` / `393216` / `bound` across `MC.cfg` and the
manifests returns nothing. The reduction is therefore structural, not an edit:
the per-ticket factor drops from `2^3 = 8` to `4`, i.e. `512 -> 64` across three
tickets, giving 3,145,728 -> 393,216 (8x). Recorded here because the issue's
phrasing ("shrink the declared bound in `MC.cfg`") implies a literal to edit, and
there is none.

## 6. Adapter surface

`specs/current/spec_manifest.yaml` carries `state_fields: []`, and **neither
`production_adapters.py` references any of the three booleans** (verified by
grep; both files are port/command adapters that shell out to the CLI and hold no
TLA state mapping). The only declarative state mapping naming the booleans is
`specs/program_model/spec_manifest.yaml` (lines 63-71), which belongs to the
frozen accepted baseline: MF-012 likewise left `specs/program_model/*` untouched
and it is promoted wholesale at epic finalization. Updating its manifest now
would desync it from its own module, which still declares the booleans.

Adapter-level retention is instead asserted by a new spec-unit test,
`test_current_model_carries_the_ticket_phase_ordinal`, mirroring MF-012's
`test_current_model_carries_the_budgets_gate`.

## 7. Finding: the `>= 2` guard and the generated-state target

`RunSpecUnitTests` has **no** `~spec_unit_tests_passed` guard in the baseline, so
it re-fires on an already-passing ticket — an idempotent re-run self-loop that
matches the real CLI (you can re-run spec-unit tests). `>= 2` preserves it.

Measured both ways, all else equal:

| Guard | Distinct | Depth | Generated |
|---|---|---|---|
| `>= 2` (faithful translation, shipped) | 919 | 21 | **3664** |
| `= 2` (tightened) | 919 | 21 | **3184** |

The MF-012 ledger's projected -13.1% generated-state drop (3664 -> 3184) is
reproducible **only** with the tightened `= 2` guard. That tightening removes the
re-run transition from the transition relation. It is invisible to the
distinct-state and depth gates — the self-loop returns to an already-known state
— which is precisely why it must not be adopted silently to hit a number.

**Shipped: `>= 2`.** This ticket is scoped as a pure representation change, so
the transition relation is preserved exactly. The `= 2` tightening is recorded in
the complexity ledger as a **recommendation for owner approval**, not applied.

## Retention result

Every guard above is an exact translation under a bijection on the reachable set.
TLC confirms: **919 distinct states, depth 21** — identical to baseline. Evidence:
`tlc-current.txt`.
