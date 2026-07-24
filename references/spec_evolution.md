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
- `specs/results`: current TLC, generated-case, adapter, and graph evidence,
  plus the append-only `complexity_ledger.json` and the `skill_feedback.md`
  retro document written at close time.

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
        ticket.yaml
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

## Preparing For Promotion

A ticket close promotes the ticket `desired/` onto the project `current/`, so
before closing you must decide what the accepted state is. Promotion is not a
blind replace: a project-`current` path is removed only when it was seeded
into the ticket workspace (recorded in the ticket's `ticket.yaml` seed
manifest at `open ticket` time) and the ticket then dropped it. Current-only
paths the ticket was never seeded with are preserved, and every removal and
preservation is enumerated in the close output and manifest.

- The default close requires ticket-local `current/` to *semantically match*
  `desired/`. Semantic comparison covers `.tla`, `.cfg`, `.yaml`/`.yml`, `.py`,
  `.toml`, and `.json` files; planning files (`README.md`, `ticket_plan.yaml`,
  `desired_state.yaml`, `ticket.yaml`) and `status`/`notes`/`promotion`
  metadata keys are ignored. They do **not** need to be byte-identical — only
  semantically equal.
- To prepare, edit `current/` (the TLA+ modules, model `.yml`, adapters, and
  tests) until it matches `desired/`, re-run `tla-spec-dev run spec-unit-tests`,
  then close.
- If the ticket `desired/` already *is* the intended accepted state and you do
  not want to hand-reconcile `current/`, pass `--accept-new`. That overwrites
  ticket `current/` from `desired/` before promotion, so no divergence check is
  needed. The whole-workflow close accepts `--accept-new` the same way to adopt
  `desired_program_model/` as the new `current/` and `program_model/`.

The same applies to the whole-workflow close, which requires `current/`,
`desired_program_model/`, and the promoted `program_model/` to converge
(the whole-workflow comparison covers `.tla`, `.cfg`, `.yaml`/`.yml` files
only).

Both closes are additionally gated by the complexity ledger (MF-019): a
ticket close reads the ticket's `results/complexity_ledger.yaml` input
(scaffolded by `open ticket`), and the workflow close reads
`specs/results/complexity_ledger_input.yaml`. The gate runs before the
history entry is created, appends an entry (recorded or rejected) to
`specs/results/complexity_ledger.json`, and has no override flag. It refuses
when the input is missing or unfilled, when there is no refinement record or
narrative, when complexity increased without a recorded justification, when a
decrease lacks validated-refactor evidence, and — at workflow close only —
when the coverage-audit status is anything but `pass`.

## Per-Ticket Close

First create and work in a ticket-local directory:

```bash
tla-spec-dev --spec-root specs open ticket TICKET-123
```

When `specs/tickets/TICKET-123/current` semantically equals
`specs/tickets/TICKET-123/desired`, mark the ticket closed in
`specs/desired_program_model/ticket_plan.yaml`. Then run:

```bash
tla-spec-dev --spec-root specs close ticket TICKET-123 \
  --summary "Captured ticket-level desired/current history" \
  --result specs/results/tlc.txt \
  --result specs/results/adapter.txt
```

The command reads the matching ticket mapping from `ticket_plan.yaml`,
evaluates the complexity-ledger gate against the ticket's filled-in
`results/complexity_ledger.yaml`, writes the ticket mapping and ledger record
into the manifest, snapshots the project model directories, moves the active
ticket directory into the history entry, promotes ticket `desired/` onto
project `specs/current` (removing only seeded paths the ticket dropped,
preserving unseeded current-only paths), merges ticket-local Test Graph
artifacts into project specs, and recommends committing the created history
entry together with the ledger and skill-feedback files it wrote.

To accept the ticket `desired/` as the new `current/` without hand-reconciling
a divergent `current/`, add `--accept-new`:

```bash
tla-spec-dev --spec-root specs close ticket TICKET-123 --accept-new \
  --summary "Accepted ticket desired state as current"
```

`--accept-new` overwrites ticket `current/` from `desired/`, skips the
`current == desired` gate, and records `accept_new` in the entry manifest.

## Whole-Workflow Close

After `current`, `desired_program_model`, and promoted `program_model` converge,
run:

```bash
python scripts/close_tickets.py \
  --repo-root . \
  --summary "Promoted desired/current into program_model"
```

This writes `closed-snapshot` under the workflow history directory before
removing `current` and `desired_program_model`. It requires the
workflow-close ledger input at `specs/results/complexity_ledger_input.yaml`,
whose `coverage_audit` block must record `pass` — `not_run`, `incomplete`,
and `fail` all refuse the workflow close.

If `current`, `desired_program_model`, and `program_model` have not been
hand-reconciled but `desired_program_model` is the intended accepted state, pass
`--accept-new` to promote its semantic files into `current` and `program_model`
before the snapshot (tickets must still be marked closed):

```bash
python scripts/close_tickets.py --repo-root . --accept-new \
  --summary "Accepted desired_program_model as the new program_model"
```

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
