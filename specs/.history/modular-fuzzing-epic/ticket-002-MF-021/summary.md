# Ticket snapshot: MF-021

- Workflow: `modular-fuzzing-epic`
- Entry: `ticket-002-MF-021`
- Ticket: `MF-021`

## Summary

MF-021: promotion is provenance-aware. open ticket records a seed_manifest of what it copied from specs/current; close removes only seeded paths the ticket dropped and preserves (and enumerates) current-only paths it was never given. Fixes the silent rmtree data loss that destroyed MF-012's budgets retention test twice. TLC 919/21 unchanged; 123 repo tests; regression suite fails 4/6 pre-fix.

## Snapshots

- `program_model`: `specs/.history/modular-fuzzing-epic/ticket-002-MF-021/snapshots/program_model`
- `desired_program_model`: `specs/.history/modular-fuzzing-epic/ticket-002-MF-021/snapshots/desired_program_model`
- `current`: `specs/.history/modular-fuzzing-epic/ticket-002-MF-021/snapshots/current`
- `ticket_workdir`: `specs/.history/modular-fuzzing-epic/ticket-002-MF-021/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
