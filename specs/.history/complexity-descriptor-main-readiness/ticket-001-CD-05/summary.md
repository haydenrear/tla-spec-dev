# Ticket snapshot: CD-05

- Workflow: `complexity-descriptor-main-readiness`
- Entry: `ticket-001-CD-05`
- Ticket: `CD-05`

## Summary

Domain resolution sees operator-defined sets (VAL-06: _set_size expands zero-parameter operators transitively through EXTENDS, sizes [S -> T] as |T|^|S|), wrapped conjuncts (VAL-16: conjunct-wise constraint parsing via resolve_constraint_chunks), and multi-view invariant naming (VAL-17: per-variable domain-source merge in documented order TypeInvariant > TypeOK > cfg invariants). F3 explicit-UNKNOWN preserved; resolver coverage contract documented in references/architecture_tractability.md 'What The Domain Resolver Can And Cannot See', cited by scanner output. Three regression tests each proven failing pre-fix. Zero TLA+ model delta.

## Snapshots

- `program_model`: `specs/.history/complexity-descriptor-main-readiness/ticket-001-CD-05/snapshots/program_model`
- `desired_program_model`: `specs/.history/complexity-descriptor-main-readiness/ticket-001-CD-05/snapshots/desired_program_model`
- `current`: `specs/.history/complexity-descriptor-main-readiness/ticket-001-CD-05/snapshots/current`
- `ticket_workdir`: `specs/.history/complexity-descriptor-main-readiness/ticket-001-CD-05/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
