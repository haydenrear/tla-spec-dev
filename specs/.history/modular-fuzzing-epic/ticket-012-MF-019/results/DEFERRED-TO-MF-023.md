# MF-019 — validations deferred to MF-023 (#30)

Per the epic-wide spec-case execution deferral (owner direction 2026-07-18),
this ticket built and unit-tested the mechanism but ran **no** generated spec
cases. Deferred here, required there.

## Not run by this ticket

- Case generation over the reachable state graph.
- The distilled-corpus run.
- The effect-conformance sweep.
- The mutation kill test.

## What MF-023 must exercise, specifically for MF-019

1. **Re-run the complexity-ledger gate with REAL retention verdicts.** This
   ticket recorded all three constraints as `deferred`, which is honest but
   means the anti-gaming gate has never fired on measured evidence in this
   repository. MF-023 is the first close that can supply real verdicts.

2. **Check that `unobservable` is refused, not read as `clean`.** MF-027
   recorded that this repository declares two `process.spawn` ports, so a real
   corpus sweep will report `unobservable` rather than `clean`. The ledger
   classifies `unobservable` as DEGRADED. If MF-023 claims any complexity
   reduction while effect conformance is `unobservable`, the close **must** be
   refused. Do not resolve that by relaxing the classification — route the
   targets through in-process adapters, or record it as a known limitation.

3. **Model the close-time refusal.** MF-019 adds a genuine externally-visible
   refusal to `close ticket` (the gate exits non-zero) and does **not** model
   it, because `max_state_space_bound` is at 70.0% with 1.43x headroom and any
   new bounded variable — even a boolean — breaches the cap. This is recorded
   as a gap, not as a judgment that the behavior is unmodelable. Once
   decomposition gives each component its own smaller declared space, the
   ledger gate should appear in the model.

## The blocking constraint MF-023 inherits

`max_state_space_bound` is the binding budget now, not `max_distinct_states`:

| Budget | Cap | Used | Headroom |
|---|---|---|---|
| `max_state_space_bound` | 1,000,000 | 699,840 (70.0%) | **1.43x** |
| `max_distinct_states` | 500,000 | 231,621 (46.3%) | 2.16x |

No new bounded state variable of any cardinality fits under the bound. The
epic's remaining model work is blocked on decomposition, not on the distinct
-state cap the schedule has been tracking.

Also still live and not worked around: `C1 is touched by 14 actions, exceeding
max_component_actions 8`.
