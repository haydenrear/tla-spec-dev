# Ticket snapshot: RC-02

- Workflow: `architectural-coherence-epic`
- Entry: `ticket-015-RC-02`
- Ticket: `RC-02`

## Summary

Closed MF-026 round-3 N-1 (three unattached ports attached to InstallLocalCli in all three trees, with @port mirrors and two always-on consistency tests), N-2 (generate cases --out and --dot constrained through spec_paths.resolve_spec_tree_out, which constrains the metadir rmtree by construction), and N-3 (the stale citation fixed and a file-qualified, content-anchored citation check shipped, which found eight more stale citations). Ran run effect-conformance against this model for the first time: unobservable, 57 observed effects over 8 cases, 20 gaps, 9 dead ports, 15 unobservable targets, exit 1, nothing tuned; the N-1 counterfactual measures the fix at -2 gaps and -1 dead port. generation_status stays planned because this model's corpus is 3,678,217 cases at 18,391x its own cap. TLC unchanged at 10,331,543 distinct states, depth 26.

## Snapshots

- `program_model`: `specs/.history/architectural-coherence-epic/ticket-015-RC-02/snapshots/program_model`
- `desired_program_model`: `specs/.history/architectural-coherence-epic/ticket-015-RC-02/snapshots/desired_program_model`
- `current`: `specs/.history/architectural-coherence-epic/ticket-015-RC-02/snapshots/current`
- `ticket_workdir`: `specs/.history/architectural-coherence-epic/ticket-015-RC-02/ticket`

## Follow-up

Review this append-only entry, then commit the history directory with the related spec changes.
