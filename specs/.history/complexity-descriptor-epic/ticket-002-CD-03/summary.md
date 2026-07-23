# Ticket snapshot: CD-03

- Workflow: `complexity-descriptor-epic`
- Entry: `ticket-002-CD-03`
- Ticket: `CD-03`

## Summary

CD-03: self-configurable composable fitness functions over the complexity descriptor — scripts/fitness_functions.py ({fact,op,value} leaves over published descriptor facts incl. parameterized variable_domain(v), composed with all/any/not under three-valued Kleene semantics); per-project persistence in spec_manifest.yaml fitness_functions: or sibling fitness_functions.yaml/.json (json is stdlib-only for the bare-python3 CLI); analyze complexity evaluates rules each scan and surfaces FIRED rules with leaf-level traces as notifications to future agents; advisory throughout (exit code unchanged; broken config is an advisory CONFIG ERROR); NO built-in rules; worked example recorded (two composed rules, later scan surfaces one firing); zero TLA model delta, TLC green 231,621 distinct

## Snapshots

- `program_model`: `specs/.history/complexity-descriptor-epic/ticket-002-CD-03/snapshots/program_model`
- `desired_program_model`: `specs/.history/complexity-descriptor-epic/ticket-002-CD-03/snapshots/desired_program_model`
- `current`: `specs/.history/complexity-descriptor-epic/ticket-002-CD-03/snapshots/current`
- `ticket_workdir`: `specs/.history/complexity-descriptor-epic/ticket-002-CD-03/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
