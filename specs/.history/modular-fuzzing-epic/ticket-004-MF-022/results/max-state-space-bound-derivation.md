# Deriving the `max_state_space_bound` default

MF-022 Part 1. This file states the reasoning **before** the value was applied,
so the choice can be audited against the rule the ticket sets: do not
reverse-engineer a number that makes this repository pass.

## What the two quantities actually measure

`state_space_bound` (`scripts/analyze_complexity.py`) is the product of the
declared cardinality of every bounded dimension in `TypeInvariant`:

```python
bound = 1
for dimension in dimensions:
    if dimension.bounded:
        bound *= int(dimension.cardinality or 1)
```

It is a **Cartesian over-approximation of the declared representation**. It
ignores every action guard, so it counts combinations the program can never
occupy. On this repository it over-approximates by ~400x (1,179,648 declared
vs 2,923 reachable).

`max_distinct_states` is a cap on **actual reachable states**, measured by TLC
after the fact.

These are not the same units. Gating a Cartesian over-approximation against a
reachable-state cap is a category error, which is the defect MF-022 Part 1
fixes. `max_distinct_states` is retained unchanged for its correct purpose:
post-TLC comparison against actual reachable states.

## The anchor: the bound gate is a TLC-capacity question

`SKILL.md` already fixes the doctrine:

> A case-generating diagram is acceptable only when it completes within 120
> seconds.

and `tlc_seconds: 120` is the budget that encodes it. So the honest question
the static bound answers is **not** "is this model small?" but:

> If the declared type invariant were tight — i.e. every declared combination
> actually reachable — could TLC still finish exhaustive checking inside
> `tlc_seconds`?

That is a worst-case capacity question about the representation, and it is
exactly what a Cartesian over-approximation is fit to answer. A model whose
declared space exceeds what TLC can enumerate in the budget is one whose
tractability depends entirely on guards the analyzer cannot see — which is
precisely the situation the gate should flag for a human.

## Measurement

Both runs on this machine, via `scripts/run_tlc.sh`.

**1. Trivial-cost upper bound.** Four mod-N counters, N=32, fully reachable,
no guards or function updates:

| | |
|---|---|
| distinct states | 1,048,576 |
| generated states | 4,194,305 |
| wall clock | ~2s |
| throughput | ~500,000 distinct states/sec |

This is a best case and is not representative — the successor computation is a
single addition.

**2. Realistic-cost measurement.** This repository's own `TlaSpecDevCli.tla`,
unmodified, with `Tickets` scaled from 3 to 5 elements so the run is long
enough to time. Same expression shapes as the real model: function updates
(`EXCEPT`), set union/difference, quantifiers over constants, record
construction.

| | |
|---|---|
| distinct states | 128,827 |
| generated states | 1,130,024 |
| wall clock | 8s |
| throughput | ~16,000 distinct states/sec (~141,000 generated/sec) |
| generated:distinct | ~8.8x |

Realistic per-state cost is ~30x higher than the trivial model. The generated
figure matters more than the distinct figure, because TLC pays for successor
computation on every generated state.

**Extrapolation to the budget:** 16,000 distinct/sec x 120s ≈ **1.9M distinct
states** exhaustively checkable within `tlc_seconds` for a model of this
expression cost.

## The chosen default

```yaml
max_state_space_bound: 1000000   # static over-approximation ceiling
```

Rounded **down** from the measured ~1.9M to 10^6, deliberately:

- The measurement is on one fast machine (135% CPU, JIT warm). The default
  ships to unknown hardware.
- `TlaSpecDevCli.tla` is a small module with cheap guards. Models with
  expensive quantification, larger constant domains, or nested set
  comprehensions cost more per state, moving the real ceiling downward.
- The gate is pre-flight advice, not a hard stop: `--allow-over-budget` exists
  for a model whose owner has understood the cost. A conservative default
  costs a recommendation; a permissive one costs a 120s timeout during case
  generation, which is the failure mode the doctrine exists to prevent.
- 10^6 is round, memorable, and documentable — a threshold nobody has to
  reverse-engineer to understand.

It sits ~20x above `max_distinct_states: 50000`, which is the correct
relationship: the bound over-approximates reachable states, so its ceiling
must be looser than the reachable-state cap, and the two remain independently
meaningful.

## Non-gaming check — the honest default FAILS this repository today

This is the load-bearing check the ticket demands, so it is recorded
explicitly:

| Model state | Bound | vs 1,000,000 |
|---|---|---|
| MF-022 baseline (12 variables, pre-collapse) | 1,179,648 | **FAIL** |
| After Part 2 setup_phase collapse (8 variables) | 221,184 | PASS |

**The default chosen here does not make this repository pass.** At the moment
it was derived, the repository was still 1.18x over it. The repository passes
only after Part 2 delivers a genuine structural reduction that removes 26
unreachable declared combinations. Had Part 2 not been in scope, the correct
report would have been "the honest default fails here" — and the number would
not have been adjusted.

A default reverse-engineered to pass would have been placed just above
1,179,648 (e.g. 1,200,000 or 2,000,000, both of which the ~1.9M extrapolation
could have been used to justify). It was not.
