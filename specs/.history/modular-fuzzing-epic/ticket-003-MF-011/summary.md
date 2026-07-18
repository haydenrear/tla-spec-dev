# Ticket snapshot: MF-011

- Workflow: `modular-fuzzing-epic`
- Entry: `ticket-003-MF-011`
- Ticket: `MF-011`

## Summary

Add tla-spec-dev analyze complexity: dimension table, state-space upper bound, R/W matrix, graph-modularity score with near-decomposable clusters and candidate port-crossing actions, unjustified-variable flags, and a suggested move (abstract/decompose/refactor) labeled a recommendation requiring user approval. Budget-gated nonzero exit; case generation refuses above the gate with an explicit --allow-over-budget override. Absorbs the two MF-020 findings: measured-vs-projected labeling throughout, and a RED FLAG for generated-states drops at constant distinct states (deleted self-loops). Model gains complexity_gate + AnalyzeComplexity.

## Snapshots

- `program_model`: `specs/.history/modular-fuzzing-epic/ticket-003-MF-011/snapshots/program_model`
- `desired_program_model`: `specs/.history/modular-fuzzing-epic/ticket-003-MF-011/snapshots/desired_program_model`
- `current`: `specs/.history/modular-fuzzing-epic/ticket-003-MF-011/snapshots/current`
- `ticket_workdir`: `specs/.history/modular-fuzzing-epic/ticket-003-MF-011/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
