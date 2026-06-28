# Workflows

This reference describes the operational paths for projects that use an
evolving TLA+ program spec plus generated Python spec doubles.

## Scaffold A Project

Use this when a repository is adopting the desired/current loop after it already
has or is about to create an accepted `program_model`.

```bash
python scripts/scaffold_spec_workflow.py --root .
```

This creates:

- `specs/desired_program_model`
- `specs/current`
- `specs/results`
- `specs/.history`

For first onboarding of a repository with no accepted baseline, prefer
`scripts/onboard_program_model.py` so only `specs/program_model` is created.

## Scaffold A Spec

Use this when creating a concrete TLA+ model and manifest.

```bash
python scripts/scaffold_spec.py workspace --root specs/current
```

For example specs, `--root examples` remains fine. For production desired/current
work, keep project state under `specs/current`, keep the planned project
destination under `specs/desired_program_model`, and keep tickets in
`specs/desired_program_model/ticket_plan.yaml`.

## Work A Ticket

1. Update `specs/desired_program_model` with the intended whole-program state.
2. Update `specs/desired_program_model/ticket_plan.yaml` with the ticket id,
   status, dependencies, validation commands, and evidence slots.
3. Start the ticket workspace:

```bash
python scripts/start_ticket.py <ticket-id> --repo-root .
```

4. Update production code plus `specs/tickets/<ticket-id>/current` and
   `specs/tickets/<ticket-id>/desired`. The ticket desired model is the
   whole-program state after this ticket.
5. Run TLC and generated/adapted case tests for the selected slice.
6. Store evidence under the ticket `results/` directory or another referenced
   evidence path.
7. Mark the ticket closed in `ticket_plan.yaml`.
8. Close the ticket:

```bash
python scripts/close-ticket.py <ticket-id> \
  --summary "What changed and why" \
  --result specs/results/tlc.txt \
  --result specs/results/adapter.txt
```

The close operation validates ticket-local `current == desired`, moves
`specs/tickets/<ticket-id>` to
`specs/.history/<workflow-name>/ticket-NNN-<ticket-id>/ticket/`, and promotes
ticket `desired/` to project `specs/current`.

## Complete A Spec Workflow

Use this when the desired/current loop has been mapped back into the durable
program model.

1. Confirm every ticket in `specs/desired_program_model/ticket_plan.yaml` has a
   closed status.
2. Confirm project `specs/current` and `specs/desired_program_model`
   semantically match.
3. Promote the converged model into `specs/program_model`.
4. Record a closed-workflow snapshot and remove temporary workflow directories:

```bash
python scripts/close_tickets.py \
  --repo-root . \
  --summary "Final mapping from desired/current into program_model"
```

The close record is written to
`specs/.history/<workflow-name>/closed-snapshot/`.

## Search Before Reading

For historical questions, search manifests and summaries first:

```bash
rg -n "<ticket-id>|<action>|<invariant>|<resource>" specs/.history
```

Open snapshots only after the manifest or summary proves relevance. This keeps
AI-assisted maintenance focused on the current state plus a small number of
append-only historical entries.
