# MF-023 — MF-019 refinement loop on the finished decomposition

Recommendations for owner approval. None applied.

## Applied in this ticket (measured, exact retention)

**R0 — remove the explicit stutter disjunct.** Done. 42,861 fewer cases (4.3%
of the Internal corpus), identical 42,861 distinct states at identical depth 24.
See FINDING 7. Applied because retention is exact and provable, not projected.

## Recommended, requiring approval

**R1 — promote `setup_phase` and `spec_root` to a contract environment.**
The highest-value structural move available, and the only one that would make
the component heuristics meaningful.

Both are read as preconditions by nearly every command (`setup_phase` by 12 of
14 actions, `spec_root` by 10). They are not really per-command state: they are
the *environment* a command runs in. The issue text itself observes that the
component budgets "presuppose a decomposed model with contract environments at
the ports".

Projected effect: Internal's largest component drops from 14 actions toward the
ticket-lifecycle component's 5, and the gate would measure the cut rather than
the command count (FINDING 3). Also removes 6 x 3 = 18x from the declared bound.

**Not applied.** It is a scope change: it converts modeled bootstrap behavior
into an assumed environment, so retention would need re-proving from scratch and
the bootstrap sequence would leave the ticket component's reachable state space.
That is a design decision for the owner, not something to slip into a ticket
whose job was to measure.

**R2 — project the oracle verdict actions against a reduced state.**
`RunSpecUnitTests`, `RunEffectConformance`, `RunKillTest`, `AnalyzeComplexity`
and `AnalyzeCorpus` account for **86.8%** of the generated corpus
(`corpus-distribution-internal.txt`), while the bootstrap actions get 1-2 cases
each. Cause: each is enabled at nearly every reachable state with a free choice
of verdict, so it cross-multiplies against the entire lifecycle state space.

The generator emits one case per (state x verdict) even though each action's
behavior depends only on `setup_phase`, `spec_root` and its own gate variable.
Generating these against a projected state would collapse the dominant strata
without losing a distinguishable behavior. This is a **generator** change, not a
model change -- the model is right; the enumeration is naive.

**R3 — model MF-019's close-time refusal.** MF-019 recorded this as unmodeled
*because no bounded variable fit*, not because it is unmodelable
(`max_state_space_bound` at 70.0%, 1.43x headroom, a boolean breaches it).

Decomposition does now make it fit: Internal's measured bound is far below the
cap, and a boolean added to Internal costs 2x on Internal's bound alone.

**Still not applied, and the reason is a finding rather than a budget.** Per
FINDING 1 the static bound gate currently reports `bound = 3` for Internal --
it cannot see six of seven domains. So the headroom that would justify adding
the variable **cannot presently be measured by the tool that owns that
decision.** Adding state on the strength of a bound the tool computes as 3 would
be acting on a number known to be wrong. R3 should follow the FINDING 1 fix.

## Anti-gaming check (MF-019 ledger)

This ticket claims a complexity **reduction** (231,621 -> 42,861 on Internal),
so the anti-gaming gate requires retention evidence and a non-degraded effect
verdict.

- **Retention: PROVEN EXACT** (`retention.md`) -- External reproduces the
  baseline on all three figures.
- **Effect conformance: `dead_surface`** -- DEGRADED, not clean.

Per MF-019's rule, a complexity reduction claimed while effect conformance is
degraded must be refused. **The reduction claim is therefore withdrawn as a
credited reduction and recorded as measured-but-uncredited.** The `dead_surface`
verdict is not resolvable in this ticket (FINDING 4: no adapter implements the
`run(case, ...)` protocol, so no port can be observed by any case), and it was
not resolved by deleting the five declared ports, which would have been gaming
the metric by removing evidence.

This is the ledger gate firing on real measured evidence for the first time --
MF-019 recorded all three constraints as `deferred` and noted the gate had never
fired on measurement. It has now, and it fired **against this ticket**.
