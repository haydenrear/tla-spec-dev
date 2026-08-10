# Ticket snapshot: RM-01

- Workflow: `portable-substrate-epic`
- Entry: `ticket-000-RM-01`
- Ticket: `RM-01`

## Summary

RM-01: a gap mutant that goes DIES->SURVIVES on a real removal, and the shipped classifier that said it could not. The re-runnability rule does exclude discriminating faults, but the fault that priced SM-03's removal was always re-runnable -- it was excluded one level further in by removal_census discriminate, which reads a surviving detector NAME as a surviving kill. Survivorship over a before-table is sound towards SURVIVES and unsound towards DIES; there is no such thing as an entailed DIES. RM-01-RF-1 DIES at bf0fb29~1 and SURVIVES at bf0fb29 with pytest-full whole at both trees and a positive control dying at both; both lost kills are DETECTOR-WEAKENED, the class the sealed record contains none of. SM-04-GM-T1 reproduces CAUGHT->UNCAUGHT from an independent implementation. The re-priced historical removals still come back at ZERO. Four findings filed, none fixed; RM-01-DF-01 is blocking and binds RM-03.

## Snapshots

- `program_model`: `specs/.history/portable-substrate-epic/ticket-000-RM-01/snapshots/program_model`
- `desired_program_model`: `specs/.history/portable-substrate-epic/ticket-000-RM-01/snapshots/desired_program_model`
- `current`: `specs/.history/portable-substrate-epic/ticket-000-RM-01/snapshots/current`
- `ticket_workdir`: `specs/.history/portable-substrate-epic/ticket-000-RM-01/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
