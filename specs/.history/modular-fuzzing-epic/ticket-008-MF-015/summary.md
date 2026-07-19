# Ticket snapshot: MF-015

- Workflow: `modular-fuzzing-epic`
- Entry: `ticket-008-MF-015`
- Ticket: `MF-015`

## Summary

MF-015: external channel enforcement. Required channel per Test Graph binding (http/cli/fs/queue/k8s, explicitly extensible), transitive static import analysis proving no Test Graph adapter imports the declared production package, violations reported with adapter/import/remediation, and required double|real port binding configurations with at least one real port so graph runs express integration-ladder rungs. Shared gate in scripts/testgraph_channels.py applied by both run_generated_case_adapters.py (external view) and export_testgraph_cases.py. Zero model delta, reasoned and recorded: the gates are Test-Graph-invoked and no modeled CLI command reaches them. TLC 87,464/9,011/depth 24 and bound 34,992 identical to baseline; 226 repository tests, 27+24 spec-unit, specWorkflow 8/8, cliWorkflow 2/2.

## Snapshots

- `program_model`: `specs/.history/modular-fuzzing-epic/ticket-008-MF-015/snapshots/program_model`
- `desired_program_model`: `specs/.history/modular-fuzzing-epic/ticket-008-MF-015/snapshots/desired_program_model`
- `current`: `specs/.history/modular-fuzzing-epic/ticket-008-MF-015/snapshots/current`
- `ticket_workdir`: `specs/.history/modular-fuzzing-epic/ticket-008-MF-015/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
