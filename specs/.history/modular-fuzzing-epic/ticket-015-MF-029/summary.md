# Ticket snapshot: MF-029

- Workflow: `modular-fuzzing-epic`
- Entry: `ticket-015-MF-029`
- Ticket: `MF-029`

## Summary

MF-029: recover action parameters from each case's before/after state pair, generator-side. Zero TLA+ model delta. Audited all 14 action labels plus Stutter: 9 guard-pinned, 5 except-index, 1 written-through (ScaffoldProject, the only action that sacrifices an after-state check), 1 UNRECOVERABLE (RunSpecUnitTests override) marked UNCHECKED and never fabricated. 14/14 negative controls verified to fail; 6/6 implementation mutations caught after closing an initially-surviving before-vs-after mutation. No case dropped: 798,411 TLC transitions in, 798,411 cases out.

## Snapshots

- `program_model`: `specs/.history/modular-fuzzing-epic/ticket-015-MF-029/snapshots/program_model`
- `desired_program_model`: `specs/.history/modular-fuzzing-epic/ticket-015-MF-029/snapshots/desired_program_model`
- `current`: `specs/.history/modular-fuzzing-epic/ticket-015-MF-029/snapshots/current`
- `ticket_workdir`: `specs/.history/modular-fuzzing-epic/ticket-015-MF-029/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
