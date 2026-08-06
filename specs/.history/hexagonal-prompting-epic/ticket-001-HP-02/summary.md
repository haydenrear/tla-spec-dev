# Ticket snapshot: HP-02

- Workflow: `hexagonal-prompting-epic`
- Entry: `ticket-001-HP-02`
- Ticket: `HP-02`

## Summary

HP-02: the hexagonal + minimize-complexity ask ships as prompts/hexagonal_implementation.md, is inlined into arm B's HP-01 slot, and is documented in references/hexagonal_prompting.md. No checker, no threshold, no gate. Local pilot ran both arms end to end: hexagonality moved as expected, complexity moved the wrong way (declared instrument could not run -- HP-02-DF-01), and the catch-bugs guard moved the wrong way by one cell on an instrument whose positive control survives. The pilot also found a hole in the prompt (a real-vs-fake test that asserts nothing); one sentence was added afterwards and is UNMEASURED.

## Snapshots

- `program_model`: `specs/.history/hexagonal-prompting-epic/ticket-001-HP-02/snapshots/program_model`
- `desired_program_model`: `specs/.history/hexagonal-prompting-epic/ticket-001-HP-02/snapshots/desired_program_model`
- `current`: `specs/.history/hexagonal-prompting-epic/ticket-001-HP-02/snapshots/current`
- `ticket_workdir`: `specs/.history/hexagonal-prompting-epic/ticket-001-HP-02/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
