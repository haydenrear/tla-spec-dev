# MF-022 complexity ledger

Standing objective: `references/architecture_tractability.md`. Every figure
below is tagged MEASURED or PROJECTED, and the two parts are measured
**separately** — this ticket's defining requirement.

All measurements taken on-branch, on
`feature/28-mf022-gate-recalibration-setup-phase`, from the pinned epic tip
`2d2e601`. No figure is quoted from an earlier ticket.

---

## Baseline established on-branch (M0)

Before any edit. `specs/tickets/MF-022/results/tlc-baseline.txt`,
`analyze-baseline.txt`.

| Quantity | Value |
|---|---|
| state variables | 12 |
| declared state-space bound | 1,179,648 |
| TLC generated states | 18,720 |
| TLC distinct states | 2,923 |
| TLC depth | 23 |
| gate verdict | FAIL |
| gate violations | bound 1,179,648 > `max_distinct_states` 50,000; C1 touched by 11 actions > `max_component_actions` 8 |

This reproduces the issue's stated baseline exactly. The issue's other quoted
figures (11 -> 7 variables, 393,216 -> 73,728) were measured on the pre-MF-011
model and are **not** used as a baseline anywhere in this ticket.

---

## Part 1 — gate recalibration (isolated)

Part 1 changes **what the bound is compared against**. It does not change the
model, so by construction it moves no state count.

Measured with Part 1 applied and Part 2 **not yet applied**
(`analyze-part1-only.txt`), so the two parts never share a measurement:

| Quantity | M0 (before Part 1) | After Part 1, before Part 2 | Delta |
|---|---|---|---|
| declared bound | 1,179,648 | 1,179,648 | **0** (unchanged, as expected) |
| TLC distinct states | 2,923 | 2,923 | **0** |
| TLC depth | 23 | 23 | **0** |
| bound gated against | `max_distinct_states` 50,000 | `max_state_space_bound` 1,000,000 | recalibrated |
| bound violation | present | **still present** | — |
| gate verdict | FAIL | FAIL | unchanged |

### The load-bearing honesty result

**Part 1 alone does not make this repository pass.** With the honest default of
1,000,000, the pre-collapse bound of 1,179,648 is still over by 1.18x and the
violation is still reported.

This is the evidence that the default was not reverse-engineered. The rule the
ticket set was "do not pick a number that makes this repository pass". The
number picked leaves the repository failing at the moment it was picked. See
`max-state-space-bound-derivation.md` for the derivation from measured TLC
throughput (~16,000 distinct states/sec on a model of realistic expression
cost, ~1.9M within the 120s `tlc_seconds` budget, rounded down to 10^6).

### Gate verdict change attributable to Part 1

Part 1's contribution is not a state-count delta. It is that
`max_distinct_states` was moved to the comparison it is actually fit for. With
a TLC report supplied it now reports:

```
INFO: TLC-measured 2,923 distinct reachable states is within max_distinct_states 50,000.
```

Before MF-022 that comparison was never made against reachable states at all.

---

## Part 2 — setup_phase collapse (isolated)

Part 2 changes **the bound itself**. Mapping and reachability argument:
`setup-phase-mapping.md`.

| Quantity | Before collapse | After collapse | Delta |
|---|---|---|---|
| state variables | 12 | 8 | **-4** |
| declared state-space bound | 1,179,648 | 221,184 | **-81.25%** (5.33x smaller) |
| declared setup combinations | 32 | 6 | -26 unreachable combinations removed |

Bound arithmetic: the five booleans contributed `2^5 = 32`; `setup_phase`
contributes `6`. `1,179,648 / 32 * 6 = 221,184`. This is exactly the figure
MF-011's analyzer projected from the model alone before the move was applied,
so the projection is now verified rather than merely asserted.

### Retention proof — MEASURED, the required deliverable

`tlc-baseline.txt` (pre-collapse) vs `tlc-current.txt` (post-collapse), same
`MC.cfg`, same constants:

| Quantity | Before | After | Delta |
|---|---|---|---|
| generated states | 18,720 | 18,720 | **0** |
| distinct states | 2,923 | 2,923 | **0** |
| depth | 23 | 23 | **0** |
| invariants checked | 11 | 11 | 0 |
| TLC result | no error | no error | — |

All three counts are **identical**. The collapse removed declared
representation only, not behavior.

**Self-loop trap explicitly checked and clear.** The failure mode the plan
warns about is a drop in *generated* states at constant *distinct* states —
the signature of a deleted idempotent re-fire, which a distinct-state gate
cannot see. Generated states here did not drop at all; they are identical.
The analyzer's own diagnostic confirms it independently:

```
OK: generated 18720 -> 18720, distinct 2923 -> 2923, depth 23 -> 23. No self-loop-deletion signature.
```

---

## Combined end state

| Quantity | M0 | Final | Attribution |
|---|---|---|---|
| state variables | 12 | 8 | Part 2 |
| declared bound | 1,179,648 | 221,184 | Part 2 |
| bound gated against | `max_distinct_states` 50,000 | `max_state_space_bound` 1,000,000 | Part 1 |
| bound violation | present | **cleared** | requires **both** parts |
| distinct states | 2,923 | 2,923 | neither — unchanged throughout |
| depth | 23 | 23 | neither — unchanged throughout |
| generated states | 18,720 | 18,720 | neither — unchanged throughout |
| component violation (C1, 11 actions) | present | **still present** | untouched, as required |

Note the bound violation clears only under **both** parts: Part 1 alone leaves
1,179,648 > 1,000,000, and Part 2 alone would leave 221,184 > 50,000. Neither
part is sufficient on its own, which is the honest reading and the reason the
owner bundled them.

The reachable-state count did not move anywhere in this ticket. Part 1's new
gate state adds no reachable behavior because `complexity_gate` already existed
from MF-011; MF-022 only changed which budget key it is compared against, which
is production-code behavior outside the state machine.

---

## Does `analyze complexity` now pass on this repository's model?

**The bound gate passes honestly. The overall verdict is still FAIL, on the
component heuristic.**

Final verdict (`analyze-complexity.txt`, exit 1):

```
VERDICT: FAIL -- budget exceeded:
  - component C1 is touched by 11 actions, exceeding max_component_actions 8
```

The bound violation is gone. What remains is the component-size finding, and
**that is required to remain**: the ticket states explicitly that "C1 is
touched by 11 actions, exceeding max_component_actions 8" is a genuine
architecture finding that must survive this ticket, and that the component
heuristics must be left untouched and still firing. They were not modified,
and it still fires.

Two acceptance criteria are therefore in genuine tension:

- "After both parts, `analyze complexity` passes on this repository's own model"
- "The component-size heuristics are untouched and still fire"

They cannot both hold, because the surviving finding is itself a gate
violation. This is reported rather than resolved: suppressing, reweighting, or
exempting the component heuristic to obtain a green verdict would be exactly
the metric-gaming the ticket forbids. **Flagged for owner decision.**

The pass that *was* required is honest and did land: the bound is within its
recalibrated budget, and actual reachable states (2,923) are 17x under
`max_distinct_states` (50,000) — verified against a real TLC run, not asserted.

---

## Refinement search for further reduction

Run as required by the standing objective. **Searched; found one candidate,
recorded as a recommendation, not applied.**

### Deferred, not re-litigated

The analyzer's remaining ABSTRACT suggestion is projecting `lastCommand` and
`result` (no configured invariant reads them). This is **already owned by
MF-016** and was deliberately not done here: abstraction is legitimate only if
the mutation kill rate holds afterwards, and that check belongs with the ticket
that owns it.

### New candidate — RECOMMENDATION, REQUIRES OWNER APPROVAL, NOT APPLIED

After the collapse, the dominant dimensions are the per-ticket ones:

| variable | cardinality | share of bound (log space) |
|---|---|---|
| `ticket_phase` | 64 (`4^3`) | 33.8% |
| `active_tickets` | 8 (`2^3`) | 16.9% |
| `closed_tickets` | 8 (`2^3`) | 16.9% |

These three are a **second instance of the exact pattern MF-020 and MF-022
just removed twice**, one level up. They are three parallel representations of
a single per-ticket fact, and they are already constrained against each other:

- `NoOpenClosedOverlap`: `active_tickets \cap closed_tickets = {}`
- `ClosedTicketsPassedSpecUnitTests`: a closed ticket has `ticket_phase >= 3`
- `OpenTicket` only admits tickets in neither set

Together they contribute `8 * 8 * 64 = 4,096` declared combinations per the
3-ticket config, of which only a small fraction is reachable. A single
per-ticket status function — `ticket_state \in [Tickets -> 0..5]` with
0 = untouched, 1..4 = open at lifecycle phase 0..3, 5 = closed — would
represent the same information in `6^3 = 216`.

[PROJECTED] — **UNVERIFIED**, requires the transition-level diff and a TLC
rerun before it may be recorded as a result:

| | Current | Projected |
|---|---|---|
| state variables | 8 | 6 |
| declared bound | 221,184 | 11,664 |

That would be a further ~19x reduction and would also likely resolve the
C1 component finding above, since it removes two of the variables C1's
11 actions touch.

**Not applied.** It is an architectural move on the whole ticket lifecycle,
well outside MF-022's assigned scope, and the standing objective is explicit
that any additional architectural move is a recommendation for owner approval
and never a unilateral change. Recorded here for the epic owner to schedule or
decline. The same caution that governed Part 2 applies: it must be validated by
unchanged distinct states and depth, with generated states checked for the
self-loop signature.

---

## Evidence

| File | Contents |
|---|---|
| `tlc-baseline.txt` | M0 TLC, pre-collapse (18,720 / 2,923 / depth 23) |
| `tlc-current.txt` | post-collapse ticket current TLC (identical counts) |
| `tlc-desired.txt` | ticket desired TLC (identical counts) |
| `analyze-baseline.txt` | M0 gate verdict, old miscalibrated comparison |
| `analyze-part1-only.txt` | Part 1 applied, Part 2 not — isolates the gate change |
| `analyze-complexity.txt` | final report, both parts, with TLC diagnostics |
| `max-state-space-bound-derivation.md` | derivation of the 1,000,000 default + non-gaming check |
| `setup-phase-mapping.md` | before/after guard and invariant mapping |
| `spec-unit-tests.txt` | spec-unit adapters (18 + 15 passed) |
| `pytest-repo.txt` | repository units (151 passed) |
| `graph-specWorkflow.txt` | specWorkflow graph (BUILD SUCCESSFUL) |
| `graph-cliWorkflow.txt` | cliWorkflow graph (BUILD SUCCESSFUL) |
