# Ticket snapshot: MF-032

- Workflow: `modular-fuzzing-epic`
- Entry: `ticket-018-MF-032`
- Ticket: `MF-032`

## Summary

Give run() to InstallLocalCli, ScaffoldWorkflow, RecordBudgets, OpenTicket (4 adapters now execute cases); promote the shared before-state builder/projector as module adapter_case_runtime.py (not a base class); fix the runner all-or-nothing == to per-field honoring UNCHECKED. Remaining adapters stay apply()-only for structural reasons (reported). Executability 7.8%->9.8% (both axes), re-measured. Zero TLA+ delta.

## Snapshots

- `program_model`: `specs/.history/modular-fuzzing-epic/ticket-018-MF-032/snapshots/program_model`
- `desired_program_model`: `specs/.history/modular-fuzzing-epic/ticket-018-MF-032/snapshots/desired_program_model`
- `current`: `specs/.history/modular-fuzzing-epic/ticket-018-MF-032/snapshots/current`
- `ticket_workdir`: `specs/.history/modular-fuzzing-epic/ticket-018-MF-032/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
