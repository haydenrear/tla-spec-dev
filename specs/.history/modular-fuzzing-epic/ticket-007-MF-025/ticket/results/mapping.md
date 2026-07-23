# MF-025 before/after mapping: three variables -> one ordinal

Required deliverable. Every site that mentioned `active_tickets`,
`closed_tickets` or `ticket_phase` is enumerated here with its `ticket_state`
equivalent, so that nothing was silently dropped.

## Lifecycle stages

| Ordinal | Name | Old combination (`active?`, `closed?`, `phase`) |
|---|---|---|
| 0 | `TicketUnopened` | (no, no, 0) |
| 1 | `TicketOpened` | (yes, no, 0) |
| 2 | `TicketDesiredReady` | (yes, no, 1) |
| 3 | `TicketCurrentReady` | (yes, no, 2) |
| 4 | `TicketSpecUnitTestsPassed` | (yes, no, 3) |
| 5 | `TicketClosed` | (no, yes, 3) |

Derived set readers, so every site that meant "the set of active tickets" still
says so:

```tla
ActiveTickets == {t \in Tickets : ticket_state[t] \in TicketOpened..TicketSpecUnitTestsPassed}
ClosedTickets == {t \in Tickets : ticket_state[t] = TicketClosed}
```

## Premise verification (measured, not argued)

The collapse is only legitimate because the three variables are one lifecycle.
Both directions were checked with TLC on the pre-collapse model:

- **No seventh combination.** A temporary invariant `SixCombinationsOnly`,
  asserting that every ticket's `(active?, closed?, phase)` triple is one of the
  six above, holds across all 9,011 reachable states. Evidence:
  `premise-probe/`.
- **All six are reachable.** For each ordinal *i*, the negated-reachability
  invariant `NotReach<i>` is violated, i.e. TLC finds a state reaching it. So
  the ordinal is neither padded nor lossy.

This is what distinguishes the move from bit-packing three independent facts:
of the 8 x 8 x 64 = 4,096 declared combinations, exactly 6 occur, and they are
totally ordered.

## Guards

| Action | Before | After |
|---|---|---|
| `OpenTicket` | `ticket \notin active_tickets` **and** `ticket \notin closed_tickets` | `ticket_state[ticket] = TicketUnopened` |
| `OpenTicket` (effect) | `active_tickets' = active_tickets \cup {ticket}`, `ticket_phase' = [... EXCEPT ![ticket] = 0]` | `ticket_state' = [... EXCEPT ![ticket] = TicketOpened]` |
| `UpdateTicketDesired` | `ticket \in active_tickets`, `ticket_phase[ticket] = 0` | `ticket \in ActiveTickets`, `ticket_state[ticket] = TicketOpened` |
| `UpdateTicketCurrent` | `ticket \in active_tickets`, `ticket_phase[ticket] = 1` | `ticket \in ActiveTickets`, `ticket_state[ticket] = TicketDesiredReady` |
| `RunSpecUnitTests` | `ticket \in active_tickets`, `ticket_phase[ticket] >= 2` | `ticket \in ActiveTickets`, `ticket_state[ticket] \in TicketCurrentReady..TicketSpecUnitTestsPassed` |
| `RunSpecUnitTests` (effect) | `IF corpus pass THEN phase := 3 ELSE ticket_phase` | `IF corpus pass THEN state := TicketSpecUnitTestsPassed ELSE ticket_state` |
| `CloseTicket` | `ticket \in active_tickets`, `ticket_phase[ticket] = 3`, remove from active **and** add to closed, `ticket_phase` UNCHANGED | `ticket \in ActiveTickets`, `ticket_state[ticket] = TicketSpecUnitTestsPassed`, `ticket_state' = [... = TicketClosed]` |

Two guards deserve explicit note because a careless mapping would change
behavior:

1. **`RunSpecUnitTests` stays a range, not an equality.** The old guard was
   `>= 2`, not `= 2`, which keeps the action re-runnable on an already-passing
   ticket. Restricted to active tickets that is phases 2..3, i.e. states 3..4.
   Collapsing it to `= TicketCurrentReady` would silently delete the idempotent
   re-run self-loop. A regression test pins the range.
2. **`OpenTicket`'s two guards become one.** `\notin active /\ \notin closed` is
   exactly "has not entered the lifecycle". The never-reopened property is now
   structural rather than checked.

## Invariants

Every invariant is retained **by name**, per the MF-020 / MF-022 precedent.

| Invariant | Before | After | Status |
|---|---|---|---|
| `TypeInvariant` | `active_tickets \subseteq Tickets`, `closed_tickets \subseteq Tickets`, `ticket_phase \in [Tickets -> 0..3]` | `ticket_state \in [Tickets -> 0..5]`, plus `ActiveTickets \subseteq Tickets` and `ClosedTickets \subseteq Tickets` retained as conjuncts | subset conjuncts now structurally true, retained |
| `NoOpenClosedOverlap` | `active_tickets \cap closed_tickets = {}` | `ActiveTickets \cap ClosedTickets = {}` | now a tautology, retained by name |
| `CurrentRequiresDesired` | `phase >= 2 => phase >= 1` | `state >= TicketCurrentReady => state >= TicketDesiredReady` | tautology before and after, retained |
| `SpecUnitTestsRequireCurrent` | `phase >= 3 => phase >= 2` | `state >= TicketSpecUnitTestsPassed => state >= TicketCurrentReady` | tautology before and after, retained |
| `SpecUnitTestsRequireAnalyzedGate` | `(\E t: ticket_phase[t] >= 3) => complexity_gate /= "unknown"` | `(\E t: ticket_state[t] >= TicketSpecUnitTestsPassed) => ...` | still does real work |
| `SpecUnitTestsRequireMeasuredCorpus` | `(\E t: ticket_phase[t] >= 3) => corpus_gate /= "unknown"` | `(\E t: ticket_state[t] >= TicketSpecUnitTestsPassed) => ...` | still does real work |
| `ClosedTicketsPassedSpecUnitTests` | `\A t \in closed_tickets: ticket_phase[t] >= 3` | `\A t \in ClosedTickets: ticket_state[t] >= TicketSpecUnitTestsPassed` | now a tautology, retained by name |

**The subtle one.** The two gate invariants quantified over
`ticket_phase[t] >= 3`, which was satisfied by **closed tickets too**, because
`CloseTicket` left the phase at 3. The faithful ordinal equivalent is therefore
`>= TicketSpecUnitTestsPassed` (states 4 **and** 5), not
`= TicketSpecUnitTestsPassed`. Mapping it to an equality would have weakened
both gates by letting a workflow whose only spec-unit-passing ticket had since
been closed escape the "gate was analyzed" requirement. `MC.cfg` is unchanged:
all twelve invariant names still exist and are still checked.

## Manifest justification linkage

`ticket_state` inherits the **union** of the three variables' invariant
linkages, so every named property they justified is still linked:
`TypeInvariant`, `NoOpenClosedOverlap`, `CurrentRequiresDesired`,
`SpecUnitTestsRequireCurrent`, `SpecUnitTestsRequireAnalyzedGate`,
`SpecUnitTestsRequireMeasuredCorpus`, `ClosedTicketsPassedSpecUnitTests`.
`analyze complexity` reports "every variable has a recorded justification
linkage".
