# Ticket snapshot: CA-02

- Workflow: `cut-the-apparatus-epic`
- Entry: `ticket-001-CA-02`
- Ticket: `CA-02`

## Summary

Cut the removal-pricing machinery, an instrument RM-05-DF-01/CL-02 measured able to return only ENTAILED-SURVIVES. Removed price_removal.py (838), altered_score_probe.py (177), residual_faults.toml (193), removal_census.py (429), removals.toml (712) and their two test files (888), each deletion naming its finding. examples/validation/ 15,901 -> 14,457 (-1,444); scripts/ unchanged at 27,652 because complexity_ledger.py has NO pricer coupling (CA-02-DF-01); card unchanged at 6,281 / sha256:2d7d4a0506d9b259. Registry rows retired not deleted (FI-04-DF-04); gap_mutants/ kept as a tombstone because it is sealed subject rm04_removal_pricer's declared scope, which went UNDERIVABLE and moved the tag derivation 17->16 of 21 (numerator fell, denominator held at 21). The deliberate pricer-grep red was DELETED WITH ITS SUBJECT, not repaired. Suite 6 failed / 1526 passed on both the pre-merge and reconciled trees, zero new reds. Price-table format established as plain markdown, no new code.

## Snapshots

- `program_model`: `specs/.history/cut-the-apparatus-epic/ticket-001-CA-02/snapshots/program_model`
- `desired_program_model`: `specs/.history/cut-the-apparatus-epic/ticket-001-CA-02/snapshots/desired_program_model`
- `current`: `specs/.history/cut-the-apparatus-epic/ticket-001-CA-02/snapshots/current`
- `ticket_workdir`: `specs/.history/cut-the-apparatus-epic/ticket-001-CA-02/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
