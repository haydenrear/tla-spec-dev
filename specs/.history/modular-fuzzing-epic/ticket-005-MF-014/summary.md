# Ticket snapshot: MF-014

- Workflow: `modular-fuzzing-epic`
- Entry: `ticket-005-MF-014`
- Ticket: `MF-014`

## Summary

Corpus diagnostics and hard case caps. Case caps are hard gates in the shape of MF-011's state-space bound: over budget reports and exits nonzero, never trims. No code path drops, filters, samples, or truncates a case to fit a budget. Diagnostics report count per (action, label class), dominant and starved strata, and what varies across the redundant group, classified into unconstrained ordering / interchangeable values / action enabled across equivalent states. Labelers repurposed to diagnostic strata; remediation is a recommendation requiring user approval; named regression traces always retained. Accept path is raising the cap in spec_manifest.yaml with a recorded rationale. Model delta: corpus_gate + AnalyzeCorpus, 8->9 vars, 11->12 actions, deviating from the stale DistillCorpus/corpus_distilled plan fields.

## Snapshots

- `program_model`: `specs/.history/modular-fuzzing-epic/ticket-005-MF-014/snapshots/program_model`
- `desired_program_model`: `specs/.history/modular-fuzzing-epic/ticket-005-MF-014/snapshots/desired_program_model`
- `current`: `specs/.history/modular-fuzzing-epic/ticket-005-MF-014/snapshots/current`
- `ticket_workdir`: `specs/.history/modular-fuzzing-epic/ticket-005-MF-014/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
