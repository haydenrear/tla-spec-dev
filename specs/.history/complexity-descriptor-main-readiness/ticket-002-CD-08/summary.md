# Ticket snapshot: CD-08

- Workflow: `complexity-descriptor-main-readiness`
- Entry: `ticket-002-CD-08`
- Ticket: `CD-08`

## Summary

distributed_history example passes its own documented workflow out of the box: example manifest cap 50->200 set to measured worst action with recorded rationale (VAL-08, nothing trimmed); regenerate_tlc_cases.py passes --bindings/--manifest to the exporter (VAL-09); export_testgraph_cases.py resolves the cap manifest from the spec root holding --bindings or fails loudly naming --manifest, regression-tested (VAL-10); TLA_SPEC_DEV_ROOT override in the example's three root-deriving scripts and a target-example-path argument on the validation wrapper (VAL-11); READMEs document the real envelope keys caseNames/expectedCaseNames (VAL-14); README counts point at generated docs.md, command echoes flushed, manual tlc2 -deadlock documented (VAL-18). Pristine scratch copy completed the documented local non-k3d path end to end before and after reconciling epic tip 5b7d09f: 93 internal + 732 external cases, cap gate and channel enforcement green. Zero TLA model delta; deferred CD-08-DF-01 (local-mode wrapper kill-test step).

## Snapshots

- `program_model`: `specs/.history/complexity-descriptor-main-readiness/ticket-002-CD-08/snapshots/program_model`
- `desired_program_model`: `specs/.history/complexity-descriptor-main-readiness/ticket-002-CD-08/snapshots/desired_program_model`
- `current`: `specs/.history/complexity-descriptor-main-readiness/ticket-002-CD-08/snapshots/current`
- `ticket_workdir`: `specs/.history/complexity-descriptor-main-readiness/ticket-002-CD-08/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
