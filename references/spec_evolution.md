# Spec Workflow History

`specs/.history/<workflow-name>/` is append-only history for one
desired/current workflow. It exists so active context can stay small while old
decisions remain auditable.

## Mentality

The active workspace is mutable:

- `specs/program_model`: accepted whole-program baseline.
- `specs/desired_program_model`: target whole-program state and ticket plan.
- `specs/current`: executable whole-program state that has landed so far.
- `specs/tickets/<ticket-id>`: active ticket-local current/desired workspace
  for one parallelizable ticket.
- `specs/results`: current TLC, generated-case, adapter, and graph evidence.

The history directory is append-only by convention:

- Never edit an existing history entry.
- Never overwrite a ticket or closed-workflow snapshot.
- Create a new explicit entry only when new evidence needs another checkpoint.
- Commit history entries with the related spec changes.
- Close commands leave filesystem permissions writable so normal git operations
  keep working.

The ticket source of truth is
`specs/desired_program_model/ticket_plan.yaml`. Do not invent or require
repository-level Markdown files per ticket.

## Layout

Per-ticket closes:

```text
specs/.history/
  <workflow-name>/
    ticket-000-<ticket-id>/
      manifest.json
      summary.md
      snapshots/
        program_model/
        desired_program_model/
        current/
      ticket/
        current/
        desired/
        results/
        testgraph/
      results/
```

Whole-workflow close:

```text
specs/.history/
  <workflow-name>/
    closed-snapshot/
      manifest.json
      summary.md
      snapshots/
        program_model/
        desired_program_model/
        current/
      results/
```

`manifest.json` is the machine-readable index. `summary.md` is the human
overview. The copied snapshots are evidence, not active state.

## Per-Ticket Close

First create and work in a ticket-local directory:

```bash
python scripts/start_ticket.py TICKET-123
```

When `specs/tickets/TICKET-123/current` semantically equals
`specs/tickets/TICKET-123/desired`, mark the ticket closed in
`specs/desired_program_model/ticket_plan.yaml`. Then run:

```bash
python scripts/close-ticket.py TICKET-123 \
  --summary "Captured ticket-level desired/current history" \
  --result specs/results/tlc.txt \
  --result specs/results/adapter.txt
```

The command reads the matching ticket mapping from `ticket_plan.yaml`, writes it
into the manifest, snapshots the project model directories, moves the active
ticket directory into the history entry, promotes ticket `desired/` to project
`specs/current`, and recommends committing the created history entry.

## Whole-Workflow Close

After `current`, `desired_program_model`, and promoted `program_model` converge,
run:

```bash
python scripts/close_tickets.py \
  --repo-root . \
  --summary "Promoted desired/current into program_model"
```

This writes `closed-snapshot` under the workflow history directory before
removing `current` and `desired_program_model`.

## Searching History

Start with summaries and manifests:

```bash
rg -n "TICKET-123|CreateWorkspace|LimitInvariant|resource-name" specs/.history
find specs/.history -name manifest.json
```

Then open only the copied snapshot paths referenced by relevant manifests.
Avoid reading every historical snapshot by default; the point of the
append-only log is selective retrieval.

## Commit Rule

After each close, commit the specific history directory with the related spec
changes:

```bash
git add specs/.history/<workflow-name>/ticket-000-TICKET-123 specs
git commit -m "record spec history for TICKET-123"
```

For whole-workflow close-out, commit the final spec, closed ticket plan, and
`closed-snapshot` together. The scripts print a recommended command, but the
reviewer should still inspect the staged scope before committing in production
repositories.
