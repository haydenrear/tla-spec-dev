# Ticket snapshot: MF-022

- Workflow: `modular-fuzzing-epic`
- Entry: `ticket-004-MF-022`
- Ticket: `MF-022`

## Summary

MF-022: gate recalibration + setup_phase collapse. Part 1: added max_state_space_bound (default 1,000,000, derived from measured TLC throughput) and gated the static bound against it; max_distinct_states now checked against actual reachable states post-TLC. The honest default still fails the pre-collapse model (1,179,648 > 1,000,000), proving it was not reverse-engineered. Part 2: collapsed five setup booleans into setup_phase in 0..5; 12->8 variables, bound 1,179,648->221,184 (-81.25%) at IDENTICAL 18,720 generated / 2,923 distinct / depth 23. Deltas measured and reported separately. Component heuristics untouched and still firing (C1, 11 actions) - which leaves the overall verdict FAIL, recorded as an open finding for the owner rather than gamed.

## Snapshots

- `program_model`: `specs/.history/modular-fuzzing-epic/ticket-004-MF-022/snapshots/program_model`
- `desired_program_model`: `specs/.history/modular-fuzzing-epic/ticket-004-MF-022/snapshots/desired_program_model`
- `current`: `specs/.history/modular-fuzzing-epic/ticket-004-MF-022/snapshots/current`
- `ticket_workdir`: `specs/.history/modular-fuzzing-epic/ticket-004-MF-022/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
