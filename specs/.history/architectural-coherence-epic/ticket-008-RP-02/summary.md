# Ticket snapshot: RP-02

- Workflow: `architectural-coherence-epic`
- Entry: `ticket-008-RP-02`
- Ticket: `RP-02`

## Summary

RP-02: set-membership parameter recovery closes the ex4 oracle leak (EV-01-DF-01) and the audit now reports what the run measured (EV-02-DF-03). A fourth mechanism recovers the element that entered or left a set, cross-checked across every such conjunct of the action; ex4 goes 0 of 5 -> 5 of 5 parameters and all 330 cases carry a real argument where every one carried UNCHECKED. The adapter reads case.input.params and never touches case.after; an unrecovered argument is a hard failure there. Generation stays deterministic (two regenerations byte-identical). The audit is rendered from the corpus it audits: the sentence 'Every parameter of every action is recoverable from its state pair' is gone, nine tests assert it cannot return, an unmeasured audit declares itself STATIC, a class that recovered nothing is UNRECOVERABLE ON THIS CORPUS whatever the syntax promised, and marker-declared arguments are reported as model-declared rather than credited as recovered. THE HONEST NEGATIVE: the reconstructed 12-mutant catalog is identical before and after -- guard relaxation still 0 of 3 by corpus, 3 of 3 by hand-written tests -- because all 330 recovered arguments are arguments the guard ACCEPTS and 0 are rejected inputs (220 refusable pairs exist that a state graph can never emit). Removing the leakage half of EV-02's two causes moves nothing, so the whole remaining failure is the structural half. Separately, the wrong-item class seeded_faults.toml declined to seed as unmeasurable is killed on BOTH instruments; that caveat was a prediction never run and is amended in place. Zero TLA+ model delta.

## Snapshots

- `program_model`: `specs/.history/architectural-coherence-epic/ticket-008-RP-02/snapshots/program_model`
- `desired_program_model`: `specs/.history/architectural-coherence-epic/ticket-008-RP-02/snapshots/desired_program_model`
- `current`: `specs/.history/architectural-coherence-epic/ticket-008-RP-02/snapshots/current`
- `ticket_workdir`: `specs/.history/architectural-coherence-epic/ticket-008-RP-02/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
