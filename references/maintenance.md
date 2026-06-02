# Maintenance

The generated Python is not the canonical source of truth. TLA+ defines
the truth. Python makes that truth executable in tests.

## Changing Behavior

1. Treat `specs/desired_program_model` as both the target formal model and the
   plan of action. Keep ticket breakdown, steps, dependencies, status metadata,
   acceptance criteria, validation commands, and adapter coverage expectations
   there. If the repository does not have the desired/current structure yet,
   run `scripts/new_ticket_workflow.py TICKET-123 "Ticket title" --repo-root .`.
2. Ensure `specs/current` starts from the entire accepted
   `specs/program_model`. It is a whole-program working copy, not a feature
   slice or ticket-local projection.
3. Implement one ticket or slice.
4. Update `specs/current` to represent the whole program now implemented,
   preserving all existing modeled behavior unless production behavior changed.
5. Run TLC for `specs/current`.
6. Review invariants and counterexamples.
7. Update the manifest or adjacent status files if new commands, state fields,
   results, ports, adapters, invariants, or plan metadata are needed.
8. Regenerate Python artifacts for the current model.
9. Review generated diffs and the baseline/current/desired relationship.
10. Run spec-double self-tests.
11. Run adapter conformance tests.
12. For ticketed spec work, write an append-only close record and commit it with
    the spec and ticket changes before moving active desired/current state
    forward.
13. When `specs/current` equals `specs/desired_program_model`, promote the
    converged model to `specs/program_model` and remove `specs/current` plus
    `specs/desired_program_model` once they no longer carry distinct planning
    state.
    `scripts/close_tickets.py --repo-root .` validates matching current,
    desired, and promoted program-model semantic files, checks that all tickets
    in `ticket_plan.yaml` are closed, and removes `specs/current` plus
    `specs/desired_program_model` after promotion. Record a workflow close entry
    before or during final cleanup so the promoted history is append-only.

See `references/typical_workflow.md` for the complete onboarding, ticket, and
closeout sequence.

## Changing Implementation Only

1. Do not change the TLA+ model.
2. Do not change generated spec semantics.
3. Update the production adapter.
4. Run conformance tests.
5. If conformance breaks, decide whether the implementation is wrong or
   the spec needs a formal semantic change.

## Review Checklist

- Does the product narrative explain why the behavior exists?
- Does `specs/desired_program_model` contain the current plan breakdown with
  tickets, steps, dependencies, status, and acceptance criteria?
- Does each completed ticket update `specs/current` to the implemented
  repository state?
- Does `specs/current` still contain the whole program from
  `specs/program_model` plus landed semantic changes?
- Are tests, graph nodes, integration harnesses, CI jobs, and validation
  scripts recorded only as evidence/status, not as TLA+ state or actions?
- Does the TLA+ model capture the canonical state machine?
- Does the manifest expose the minimum reproducible contract?
- Do generated files have deterministic diffs?
- Are production concerns kept out of the fake?
- Are refinement mappings explicit and reviewable?
- Do adapter tests compare against the spec double rather than only
  checking interactions?
- Did TLC counterexamples become traces when useful?
- Did production bugs become model changes, validator changes, or
  regression traces?
- Was ticket or workflow history recorded under `specs/.history/<workflow-name>/`
  before active desired/current state moved on?

## Append-Only Close Records

Use `scripts/close-ticket.py` after each ticket is marked closed in
`specs/desired_program_model/ticket_plan.yaml`. It reads the ticket from that
YAML file and snapshots `specs/program_model`, `specs/desired_program_model`,
`specs/current`, and supplied result evidence into
`specs/.history/<workflow-name>/ticket-NNN-<ticket-id>/`.

Use `scripts/close_tickets.py` when a desired/current workflow is complete. It
validates convergence and writes
`specs/.history/<workflow-name>/closed-snapshot/` before removing active
`current` and `desired_program_model` directories.

Do not edit close entries after they are written. If new information appears,
create another close id. Git history supplies ordering across append-only
entries.

## Drift Warnings

- Do not edit generated files directly unless a file marks an extension
  point.
- Do not let generated code drift from the TLA+ model.
- Do not treat Python as replacing TLA+.
- Do not let tests bypass the spec double when conformance is the point.
- Do not confuse centralized semantic state with centralized production
  architecture.

## Useful Slogans

- The spec should generate the mock.
- TLA+ defines the truth; Python makes it executable in tests.
- The spec double is the minimum reproducible contract.
- The implementation may be distributed; the spec state is centralized.
- Production adapters are free to optimize, not reinterpret.
- The fake is not a shortcut around the spec. The fake is generated from
  the spec.
- Code is not automatically truth; reviewed executable contracts are
  truth-bearing artifacts.
