# Ticket snapshot: MF-030

- Workflow: `modular-fuzzing-epic`
- Entry: `ticket-016-MF-030`
- Ticket: `MF-030`

## Summary

Resolve EXTENDS in analyze_complexity: follow the module hierarchy and union VARIABLES/CONSTANTS/definitions; fail closed (named errors) on INSTANCE, WITH substitution, parameterized instantiation, LOCAL, and unresolved EXTENDS. Zero TLA+ model delta (TLC 231,621 distinct/depth 25; binding bound 699,840 unchanged). Regression proves bound moves 1->4 across an EXTENDS edge and fails pre-fix. Shipped example re-measured: External verdict diagnosis corrected from spurious 'C2 {responses} 9 actions' to true 'C1 13 actions' over all 10 variables (relevant to MF-037).

## Snapshots

- `program_model`: `specs/.history/modular-fuzzing-epic/ticket-016-MF-030/snapshots/program_model`
- `desired_program_model`: `specs/.history/modular-fuzzing-epic/ticket-016-MF-030/snapshots/desired_program_model`
- `current`: `specs/.history/modular-fuzzing-epic/ticket-016-MF-030/snapshots/current`
- `ticket_workdir`: `specs/.history/modular-fuzzing-epic/ticket-016-MF-030/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
