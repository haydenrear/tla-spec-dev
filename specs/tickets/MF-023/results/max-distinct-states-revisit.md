# MF-023 — the `max_distinct_states` revisit, with its measurement

The negotiated budget carries an explicit instruction:

> REVISIT AT MF-023: decomposition gives each component its own much smaller
> state space, and this should drop back toward the default then.

## The expectation is falsified by measurement

Decomposition made the **Internal** view much smaller. It did **not** make the
**External** view smaller, and it cannot -- External is the composition of
Internal plus the observable channel, so it retains the full pre-split state
space **by construction**. That is precisely what the exact-retention proof
means (`retention.md`): 231,621 distinct, identical to baseline.

| View | Distinct states (measured) | vs 50,000 default | vs 500,000 current |
|---|---|---|---|
| Internal | 42,861 | 85.7% -- fits, barely | 8.6% |
| **External** | **231,621** | **463% -- breaches** | 46.3% |

A cap must cover the **largest** view, not the smallest. Dropping to the 50,000
default would refuse the External view outright.

## Proposal: 300,000 (down from 500,000, −40%)

| | value | headroom on External (231,621) | headroom on Internal (42,861) |
|---|---|---|---|
| current | 500,000 | 2.16x | 11.7x |
| **proposed** | **300,000** | **1.30x** | 7.0x |
| default | 50,000 | 0.22x -- breach | 1.17x |

Rationale, derived rather than chosen to fit:

- The binding measurement is External at 231,621. 300,000 sits 1.30x above it.
- TLC completes the External view in ~30s against a `tlc_seconds: 120` budget,
  so wall time is not close to binding at this size.
- 500,000 was calibrated in MF-016 against a *growth trajectory* that assumed
  further gate variables would be added to a single module. That trajectory no
  longer applies: MF-019 established no new bounded variable fits under
  `max_state_space_bound` in a single module, and new state now goes into
  whichever view owns it rather than into one module. The headroom 500,000 was
  reserving is no longer needed in that shape.

## Not applied

500,000 is carried through this promotion unchanged, with its rationale
comments, exactly as the assignment requires. 300,000 is **recorded in the
manifest as a proposal for owner approval**, alongside the measurement that
produced it. Lowering a negotiated budget is an explicit recorded decision, not
something a ticket does to itself.

## Caveat that cuts against the proposal

`max_distinct_states` is checked only once TLC has measured, via `--tlc-report`.
The *static* companion gate, `max_state_space_bound`, is the one MF-019 found
binding at 70.0% -- and FINDING 1 shows that gate now reports `bound = 1` or
`bound = 3` on the decomposed views and cannot fail. So the static half of the
budget pair is currently inoperative on this repository's own model. **Tightening
the dynamic cap while the static cap is silently disabled would give a
misleading impression of control.** Fixing FINDING 1 should precede acting on
this proposal.
