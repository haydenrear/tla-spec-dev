# MF-027 complexity delta, retention evidence, and refinement search

Standing objective (MF-019): record the complexity delta **jointly** with the
retention evidence that justifies it, and run the refinement search.

## The delta

Measured on this ticket's branch, epic tip `3ede31e`. Baseline re-measured here
rather than quoted, per instruction.

| Metric | Baseline (`specs/current`) | MF-027 (`specs/tickets/MF-027/current`) | Delta |
|---|---|---|---|
| Variables | 8 | 8 | **0** |
| Actions | unchanged | unchanged | **0** |
| Declared state-space bound | 139,968 | 174,960 | +34,992 (+25.0%) |
| TLC states generated | 678,724 | 1,067,828 | +389,104 (+57.3%) |
| TLC distinct states | 38,241 | 49,875 | +11,634 (+30.4%) |
| TLC depth | 24 | 24 | **0** |
| `max_distinct_states` budget | 500,000 | 500,000 | within cap (10.0% used) |

The whole delta comes from **one** change: the `effect_conformance` variable's
domain grows from 4 values (`unknown`, `clean`, `gaps`, `dead_surface`) to 5
(`+ unobservable`). The bound arithmetic confirms there is nothing else in it:
139,968 x 5/4 = 174,960 exactly. No variable was added, no action was added,
and the depth is unchanged.

TLC: `Model checking completed. No error has been found.` in 02s.

## Retention evidence — why the fifth value earns its place

`references/architecture_tractability.md` requires every element of the model to
earn its place by supporting an invariant, carrying an effect, or killing a
mutant. `unobservable` does the first two:

1. **Supports an invariant.** It is a member of `effect_conformance`'s domain in
   `TypeInvariant`, and it is one of the values excluded by
   `SpecUnitTestsRequireMeasuredEffects` — a ticket must not reach
   `TicketSpecUnitTestsPassed` on a target the oracle could not see. Without the
   value in the domain, that exclusion cannot be stated, because the state it
   excludes would not be representable.

2. **Carries an externally-visible effect.** The verdict selects a distinct
   `result.next` string and a distinct CLI exit path
   (`scripts/effect_conformance_report.py`, exit 1 with an `unobservable`
   verdict). It is listed against `effect_conformance` in the manifest's
   per-variable justification table as
   `CliWorkflowResult.effect_conformance_verdict`.

3. **Kill test:** deferred with the rest of the epic to MF-023 (#30) /
   MF-016 (#17). Recorded as deferred, not as satisfied.

The decisive argument for modeling it rather than leaving it to the
implementation: the verdict is externally-visible behavior of a modeled command.
Omitting it would leave the model blind to a real outcome of `RunEffectConformance`
and `RunSpecUnitTests` — which is precisely the defect class the verdict itself
exists to report. Not modeling it would have been the cheap move this epic keeps
purging.

## Refinement search — searched, and a reduction WAS found

Searched for a representation of the same behavior at lower state cost.

**Rejected — collapse `unobservable` into `gaps`.** Cost-free, but wrong: the two
have different remedies (declare a port vs. run the target in-process or check
the boundary another way) and different `result.next` values. More importantly it
asserts evidence of a defect where there is only absence of evidence. This is the
same reasoning MF-013 used to keep `gaps` and `dead_surface` apart.

**Rejected — do not model the verdict at all.** See retention evidence above.

**FOUND, not applied — collapse all three failure verdicts into one `fail`.**
Measured directly (variant built in scratch, TLC run to completion):

| Variant | Generated | Distinct | Depth |
|---|---|---|---|
| MF-027 as shipped (5 values) | 1,067,828 | 49,875 | 24 |
| Collapsed `{unknown, clean, fail}` | 375,096 | 26,607 | 24 |

That is a **47% reduction in distinct states** versus this ticket, and 30% below
the epic baseline of 38,241 — a real and substantial saving, verified by TLC
rather than projected.

**It is NOT applied here**, for two reasons:

1. It deletes externally-visible distinctions. `result.next` differs per verdict,
   and each verdict has a different remedy. Flattening them makes the model stop
   describing the CLI's actual behavior — a complexity reduction bought by
   dropping a boundary, which `architecture_tractability.md` names as the cheap
   way to minimize complexity and which the constraint set exists to catch.
2. It is an **architectural move**, so per the standing objective it is a
   **recommendation requiring owner approval**, not an agent decision. It also
   reverses a deliberate MF-013 design choice.

Recorded here so the owner can decide with the number in hand. If the owner
judges `result.next` granularity not worth 23,268 distinct states, the change is
mechanical.

## Live findings — NOT worked around

`analyze complexity` VERDICT: **FAIL**, unchanged from the epic tip:

```
- component C1 is touched by 13 actions, exceeding max_component_actions 8
```

This is a true finding about the undecomposed single-module baseline. No budget
was renegotiated and `--allow-over-budget` was not used. Resolved at the root by
MF-023 (#30).

The `SUGGESTED MOVE: ABSTRACT` recommendation (project `lastCommand` and
`result`, which no configured invariant reads) is also unchanged from the
baseline and is not this ticket's to take — it is an owner-approval architectural
recommendation, and its own output marks the gain as PROJECTED/UNVERIFIED pending
the kill test.

## Negotiated budget

`max_distinct_states: 500000` (negotiated 2026-07-19, raised from the documented
default 50000) and its full derivation comments were carried from `specs/current`
into this ticket's `desired/` and `current/` trees, and verified present in
`specs/current` again after promotion. See `budget-retention.md`.
