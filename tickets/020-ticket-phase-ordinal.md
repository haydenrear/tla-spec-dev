# Collapse Ticket Phase Booleans Into An Ordinal

Status: Open

The MF-012 complexity ledger surfaced an architectural move, and the
repository owner approved it. `desired_ready`, `current_ready`, and
`spec_unit_tests_passed` are three parallel boolean functions over `Tickets`
that the invariants already hold in a strict total order, so only 4 of their 8
per-ticket combinations are reachable. The other 4 are declared state the
program can never occupy — accidental complexity, not essential behavior.

Replace them with a single ordinal `ticket_phase \in [Tickets -> 0..3]`.

This is the "abstract" move from `references/architecture_tractability.md`,
applied to a case where the reduction is provable rather than estimated.

Measured on the MF-012 model before scheduling:

| Metric | Before | After | Delta |
|---|---|---|---|
| State variables | 13 | 11 | **-2** |
| Declared state-space bound | 3,145,728 | 393,216 | **8x smaller** |
| States generated | 3,664 | 3,183 | **-13.1%** |
| Reachable distinct states | 919 | 919 | **0 (identical)** |
| Search depth | 21 | 21 | **0 (identical)** |

The identical reachable-state count and depth are the point: they are the
evidence that this is a representation change and not a behavior deletion. A
complexity drop with *fewer* reachable states would be the gaming pattern the
standing objective rejects.

Scheduled at promotion_order 15, between MF-012 and MF-011, so that MF-011's
`analyze complexity` gate is built and calibrated against the model shape the
epic intends to keep. Building the metric against a shape already slated for
removal would force recalibration and would make MF-011's own ledger entry
meaningless.

Acceptance criteria:

- `desired_ready`, `current_ready`, and `spec_unit_tests_passed` are removed;
  `ticket_phase` carries the ordering.
- Every invariant expressed over the three booleans has an equivalent
  expressed over `ticket_phase`. None is silently dropped — enumerate the
  before/after invariant mapping in the ticket evidence.
- TLC on the ticket-local current model reports **919 distinct states and
  depth 21**, matching the MF-012 baseline exactly. Any divergence means
  behavior was changed, not merely re-represented, and must be explained or
  reverted.
- Declared state-space bound drops to 393,216 and state variables drop by 2.
- `production_adapters.py` and the spec-unit adapters read `ticket_phase`;
  no adapter still references a removed boolean.
- The complexity ledger for this ticket records the reduction jointly with
  retention evidence (invariants, spec-unit, repository units, both graphs),
  per the standing objective.
