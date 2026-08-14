# Closed workflow snapshot

- Workflow: `cut-the-apparatus-epic`
- Entry: `closed-snapshot`

## Summary

Workflow close for cut-the-apparatus-epic. Eight delivered tickets, none retired, --accept-new used nowhere. CA-05 carries two close receipts by design; the earlier one is marked superseded_by the reconciled one and is excluded from the count, not deleted. The cumulative findings ledger (278 rows) is archived at closed-snapshot/deferred_findings.yaml and recorded in this manifest under findings_ledger; disposition.py reads it from there. GOAL-apparatus-cut is MISSED and awaits the owner's recorded acceptance on PR #272.

## Snapshots

- `program_model`: `specs/.history/cut-the-apparatus-epic/closed-snapshot/snapshots/program_model`
- `desired_program_model`: `specs/.history/cut-the-apparatus-epic/closed-snapshot/snapshots/desired_program_model`
- `current`: `specs/.history/cut-the-apparatus-epic/closed-snapshot/snapshots/current`

## Findings ledger

The cumulative findings ledger `specs/desired_program_model/deferred_findings.yaml` was archived to `specs/.history/cut-the-apparatus-epic/closed-snapshot/deferred_findings.yaml`. The close removed the directory it lived in; this copy is the record. Read it with `python3 scripts/disposition.py --ledger specs/.history/cut-the-apparatus-epic/closed-snapshot/deferred_findings.yaml --all`.

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
