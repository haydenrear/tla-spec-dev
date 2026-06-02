# Record Spec Evolution On Close

Status: Done

When the desired/current migration loop is closed and mapped back into the
program model, write an append-only history entry under
`specs/.history/<workflow-name>/closed-snapshot/`.

Each close should preserve enough context to understand how the graph evolved:
the current spec/program model, the desired and current working models, the TLC
and adapter results that justified the close, and the tickets included in that
close. This turns the close operation into an auditable checkpoint instead of a
destructive cleanup step.

The intuition is that active context should stay small while historical context
stays available. The current desired/current state can be rewritten or removed
after close, but the append-only evolution entry gives us a durable history that
can be inspected later without carrying all previous state in the active prompt
or workspace.

Acceptance criteria:

- Closing the desired/current loop creates a new directory under
  `specs/.history/<workflow-name>/closed-snapshot/`.
- The close directory name is explicit, such as a supplied close id, ticket
  batch id, timestamped run id, or other deterministic identifier.
- The close entry records the current spec/program model snapshot.
- The close entry records the desired and current working-model snapshots used
  for the close.
- The close entry records TLC, generated-case, and adapter/test results used as
  evidence.
- The close entry records the tickets from
  `specs/desired_program_model/ticket_plan.yaml`.
- Existing evolution entries are append-only; the close workflow refuses to
  overwrite an existing entry.
- Close instructions recommend committing the resulting spec, ticket, and
  evolution-entry changes with git after the close.

Implementation:

- Added `scripts/spec_evolution.py` with append-only manifest, snapshot, result,
  ticket-plan, summary, and git-metadata capture helpers.
- Updated workflow close-out to record whole-workflow entries under
  `specs/.history/<workflow-name>/closed-snapshot/`.
- Added documentation for append-only history and close-out workflows.
