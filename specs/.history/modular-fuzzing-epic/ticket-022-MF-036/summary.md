# Ticket snapshot: MF-036

- Workflow: `modular-fuzzing-epic`
- Entry: `ticket-022-MF-036`
- Ticket: `MF-036`

## Summary

Made complexity advisory: analyze complexity and case generation no longer block or refuse over threshold (exit 0 with warnings + recommendations); only an unanalyzable model (ModuleResolutionError) still exits nonzero. Fixed the v'=v frame-condition R/W over-count. Zero TLA delta; TLC 231,621 distinct/depth 25.

## Snapshots

- `program_model`: `specs/.history/modular-fuzzing-epic/ticket-022-MF-036/snapshots/program_model`
- `desired_program_model`: `specs/.history/modular-fuzzing-epic/ticket-022-MF-036/snapshots/desired_program_model`
- `current`: `specs/.history/modular-fuzzing-epic/ticket-022-MF-036/snapshots/current`
- `ticket_workdir`: `specs/.history/modular-fuzzing-epic/ticket-022-MF-036/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
