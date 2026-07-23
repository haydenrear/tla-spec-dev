# Ticket snapshot: MF-038

- Workflow: `modular-fuzzing-epic`
- Entry: `ticket-020-MF-038`
- Ticket: `MF-038`

## Summary

MF-038 kill-rate probe: control GREEN on the reduced runnable corpus; kill rate 4/13=0.308; all 9 subtle content/value/field bugs SURVIVED, only 4 structural directory/tree bugs killed. Cases are existence-and-exit-code oracles, not content oracles. Zero model delta. Recommendation: not yet ship-worthy as case-advising until file/field content is projected into model variables.

## Snapshots

- `program_model`: `specs/.history/modular-fuzzing-epic/ticket-020-MF-038/snapshots/program_model`
- `desired_program_model`: `specs/.history/modular-fuzzing-epic/ticket-020-MF-038/snapshots/desired_program_model`
- `current`: `specs/.history/modular-fuzzing-epic/ticket-020-MF-038/snapshots/current`
- `ticket_workdir`: `specs/.history/modular-fuzzing-epic/ticket-020-MF-038/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
