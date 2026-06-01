# Spec Evolution History

`specs/.tla-spec-evolution/` is append-only history for TLA+ program-model work.
It exists so active context can stay small while old decisions remain auditable.

## Mentality

The active workspace is mutable:

- `specs/desired_program_model`: intended whole-program end state.
- `specs/current`: currently implemented slice and adapters.
- `specs/results`: current TLC, generated-case, adapter, and graph evidence.

The evolution directory is immutable:

- Never edit an existing close entry.
- Never overwrite a close id.
- Create a new close id when new evidence or a correction is needed.
- Commit close entries with the related spec and ticket changes.

This gives two kinds of history: filesystem snapshots for fast local retrieval
and git commits for durable ordering and review.

## Layout

Per-ticket closes:

```text
specs/.tla-spec-evolution/
  tickets/
    <ticket-id>/
      <close-id>/
        manifest.json
        summary.md
        snapshots/
        results/
        tickets/
```

Whole-workflow closes:

```text
specs/.tla-spec-evolution/
  workflows/
    <close-id>/
      manifest.json
      summary.md
      snapshots/
      results/
      tickets/
```

`manifest.json` is the machine-readable index. `summary.md` is the human
overview. The copied snapshots are evidence, not active state.

## Per-Ticket Close

```bash
python scripts/close-ticket.py 010-add-per-ticket-close-history \
  --summary "Captured ticket-level desired/current history" \
  --result specs/results/tlc.txt \
  --result specs/results/adapter.txt
```

Use this after the ticket's TLC and adapter evidence exists and before moving
`specs/current` to the next slice.

## Whole-Workflow Close

```bash
python scripts/close-spec-workflow.py \
  --close-id billing-migration-001 \
  --ticket 008-run-tla-workflows-from-specs-directory \
  --ticket 009-record-spec-evolution-on-close \
  --remove-active
```

Use this when the desired/current loop has been mapped back into the durable
program model. `--remove-active` removes `desired_program_model` and `current`
only after they are snapshotted.

## Searching History

Start with summaries and manifests:

```bash
rg -n "LimitInvariant|CreateWorkspace|ticket-id|close-id" specs/.tla-spec-evolution
find specs/.tla-spec-evolution -name manifest.json
```

Then open only the copied snapshot paths referenced by relevant manifests.
Avoid reading every historical snapshot by default; the point of the immutable
log is selective retrieval.

## Commit Rule

After each close:

```bash
git add specs tickets
git commit -m "close spec ticket <ticket-id>"
```

For whole-workflow close-out, commit the final spec, closed tickets, and
evolution entry together. The close scripts print a recommended command, but the
reviewer should still inspect the staged scope before committing in production
repositories.
