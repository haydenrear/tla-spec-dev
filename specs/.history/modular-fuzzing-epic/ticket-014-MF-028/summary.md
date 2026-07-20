# Ticket snapshot: MF-028

- Workflow: `modular-fuzzing-epic`
- Entry: `ticket-014-MF-028`
- Ticket: `MF-028`

## Summary

Spike: measured the cost of case execution. One adapter (ScaffoldProject) executes one generated case end to end through the real runner -- before-state materialized by CLI prefix replay, action executed, after-state projected from the filesystem, 9 fields checked, 2 declared unchecked, 3 negative controls rejected. Before-state materialization -- the predicted hard part -- is cheap and ~100% shared. Found four structural blockers the ticket did not anticipate: all 57,617 cases carry empty action params (parameterized actions untestable); UpdateTicketDesired/UpdateTicketCurrent have no adapter, blocking 72.5% of the corpus; 16 adapters cover only 13 labels with 3 colliding on CloseTicket; and the effect oracle moved from 0 to 6 observed effects but still refuses as unobservable because every adapter shells out. run() alone does not restore oracle 3.

## Snapshots

- `program_model`: `specs/.history/modular-fuzzing-epic/ticket-014-MF-028/snapshots/program_model`
- `desired_program_model`: `specs/.history/modular-fuzzing-epic/ticket-014-MF-028/snapshots/desired_program_model`
- `current`: `specs/.history/modular-fuzzing-epic/ticket-014-MF-028/snapshots/current`
- `ticket_workdir`: `specs/.history/modular-fuzzing-epic/ticket-014-MF-028/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
