# Collapse The Per-Ticket Lifecycle Into One Ordinal

Status: Open

Owner-approved architectural move. Third instance of the same pattern, after
MF-020 (`ticket_phase`) and MF-022 (`setup_phase`).

## Why now, not later

Each gate ticket adds a 3-valued fact and **triples the declared bound**:
221,184 → 663,552 with MF-014. The budget is 1,000,000.

| State | Bound | vs budget |
|---|---|---|
| Now (2 gates) | 663,552 | PASS |
| + one more gate | 1,990,656 | **BREACH** |
| + another | 5,971,968 | **BREACH** |

MF-015, MF-016 and MF-019 are all plausibly gate-adding. The next one likely
breaches. Per the standing objective the answer to a bad measurement is a
change of architecture, not a raised budget — so this lands **before** the
breach rather than under it.

## The move

Replace `active_tickets` (SUBSET Tickets), `closed_tickets` (SUBSET Tickets),
and `ticket_phase` ([Tickets -> 0..3]) with a single
`ticket_state \in [Tickets -> 0..5]`.

These three are not independent facts. They are one per-ticket lifecycle,
recorded three ways:

| Ordinal | Meaning |
|---|---|
| 0 | not yet opened |
| 1 | active, phase 0 (opened) |
| 2 | active, phase 1 (desired advanced) |
| 3 | active, phase 2 (current advanced) |
| 4 | active, phase 3 (spec-unit tests passed) |
| 5 | closed |

**Verified against the model before scheduling**, and this is what makes the
move legitimate rather than a packing trick:

- `OpenTicket` guards on `ticket \notin active_tickets /\ ticket \notin
  closed_tickets`, so a ticket is **never reopened**. The lifecycle is
  monotonic.
- `CloseTicket` leaves `ticket_phase` UNCHANGED, so a closed ticket retains
  phase 3. There is no closed-with-other-phase state to represent.
- `NoOpenClosedOverlap` already forbids a ticket being both active and closed.

So exactly **six** per-ticket combinations are reachable, and they are totally
ordered. The ordinal represents the reachable set exactly.

Declared-representation arithmetic (derived from the model, not quoted):

```
active_tickets  2^3 =   8
closed_tickets  2^3 =   8
ticket_phase    4^3 =  64
                     -----
combined            = 4,096   ->  ticket_state 6^3 = 216   =  18.96x
```

Projected bound 663,552 -> ~34,992. **That figure is derived, not measured.**
Measure it on-branch; this epic has twice been burned treating a projection as
a measurement.

## This must not become degeneracy

The whole point is *the same behavior with a simpler, more robust
implementation*. Two ways this could go wrong, and both are failures of this
ticket:

1. **Deleting behavior.** If reachable distinct states or depth change, the
   collapse removed something real. The retention proof is equality, not
   argument.
2. **Misrepresenting the architecture.** An ordinal that merely bit-packs three
   independent facts would shrink the variable count while making the model
   *less* intelligible — a metric win and an architecture loss. That is only
   avoided because the three genuinely are one lifecycle, which is why the
   verification above matters. If during implementation you find a reachable
   combination that does not fit the six, **stop and report it**: that finding
   means the premise is wrong and the collapse must not proceed.

## Acceptance criteria

- `active_tickets`, `closed_tickets` and `ticket_phase` are gone; `ticket_state`
  carries the lifecycle.
- **Reachable distinct states remain 9,011 and depth remains 24**, matching the
  MF-014 baseline exactly. Establish that baseline on-branch first. Divergence
  in either direction stops the ticket: fewer means behavior was deleted, more
  means the ordinal admits states the originals did not.
- Set-valued readers keep reading sets. Define derived operators —
  `ActiveTickets == {t \in Tickets : ticket_state[t] \in 1..4}`,
  `ClosedTickets == {t \in Tickets : ticket_state[t] = 5}` — so every site that
  meant "the set of active tickets" still says so. The model must read as a
  lifecycle, not as arithmetic on an integer.
- Every invariant and guard over the three has an equivalent over
  `ticket_state`, with the before/after mapping enumerated. Invariants that
  become structurally true are **retained by name**, per the precedent MF-020
  and MF-022 set — silently deleting a named safety property is
  indistinguishable at review from losing it.
- No adapter still references a removed variable.
- The declared bound drops to the measured value, reported separately from any
  other change in this ticket.
