# Workflows

This reference describes the operational paths for projects that use an
evolving TLA+ program spec plus generated Python spec doubles.

## Scaffold A Project

Use this when a repository is adopting the desired/current loop.

```bash
python scripts/scaffold_spec_workflow.py --root .
```

This creates:

- `specs/desired_program_model`
- `specs/current`
- `specs/results`
- `specs/.tla-spec-evolution`

Keep `specs/.tla-spec-evolution` append-only. The scaffolded README files are
orientation docs; close entries under that directory are immutable evidence.

## Scaffold A Spec

Use this when creating a concrete TLA+ model and manifest.

```bash
python scripts/scaffold_spec.py workspace --root specs/current
```

For example specs, `--root examples` remains fine. For production desired/current
work, put the active slice under `specs/current` and keep the desired end state
under `specs/desired_program_model`.

## Work A Ticket

1. Update `specs/desired_program_model` with the intended whole-program state.
2. Update `specs/current` with only the implemented slice for this ticket.
3. Run TLC and generate cases with paths that resolve under the spec directory.
4. Run adapter or graph evidence for the selected slice.
5. Store evidence under `specs/results`.
6. Close the ticket:

```bash
python scripts/close-ticket.py <ticket-id> \
  --summary "What changed and why" \
  --result specs/results/tlc.txt \
  --result specs/results/adapter.txt
```

7. Commit the ticket, spec changes, results worth keeping, and close entry.

The close record is the bridge between the mutable active context and durable
history.

## Complete A Spec Workflow

Use this when the desired/current loop has been mapped back into the durable
program model.

1. Confirm every included ticket has a per-ticket close entry.
2. Confirm the final TLA+ spec and manifest represent the accepted program
   model.
3. Record a workflow close:

```bash
python scripts/close-spec-workflow.py \
  --close-id <workflow-id> \
  --ticket <ticket-id> \
  --ticket <ticket-id> \
  --summary "Final mapping from desired/current into the program model" \
  --remove-active
```

4. Commit the final TLA+ spec, closed tickets, and workflow close entry.

Use `--remove-active` only when the active desired/current directories have been
snapshotted and are no longer needed. If there is any doubt, omit it and remove
them in a later explicit cleanup.

## Search Before Reading

For historical questions, search manifests and summaries first:

```bash
rg -n "<ticket-id>|<action>|<invariant>|<resource>" specs/.tla-spec-evolution
```

Open snapshots only after the manifest or summary proves relevance. This keeps
AI-assisted maintenance focused on the current state plus a small number of
immutable historical entries.
