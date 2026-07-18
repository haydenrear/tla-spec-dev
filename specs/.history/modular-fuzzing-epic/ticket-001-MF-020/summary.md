# Ticket snapshot: MF-020

- Workflow: `modular-fuzzing-epic`
- Entry: `ticket-001-MF-020`
- Ticket: `MF-020`

## Summary

MF-020: collapse desired_ready/current_ready/spec_unit_tests_passed into ticket_phase ordinal 0..3. Pure representation change: no CLI surface, no new behavior. Retention proven by equality — 919 distinct states, depth 21, 10/10 invariants, identical to MF-012 baseline. Complexity: 13 -> 11 state variables, declared bound 3,145,728 -> 393,216 (8x). Generated-states target of 3,183 NOT met (shipped 3,664); reaching it needs a guard tightening that deletes the spec-unit re-run transition, recorded as a finding rather than applied. Refinement search found a further setup_phase collapse (11 -> 7 vars), prototyped and left as a recommendation.

## Snapshots

- `program_model`: `specs/.history/modular-fuzzing-epic/ticket-001-MF-020/snapshots/program_model`
- `desired_program_model`: `specs/.history/modular-fuzzing-epic/ticket-001-MF-020/snapshots/desired_program_model`
- `current`: `specs/.history/modular-fuzzing-epic/ticket-001-MF-020/snapshots/current`
- `ticket_workdir`: `specs/.history/modular-fuzzing-epic/ticket-001-MF-020/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
