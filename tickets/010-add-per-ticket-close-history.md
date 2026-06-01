# Add Per-Ticket Close History

Status: Done

Add a `close-ticket.py` workflow that runs after an individual ticket is
completed. It should write an immutable history entry for that ticket before the
active desired/current state moves on.

Each ticket close should capture the specifics of what changed for that ticket:
the ticket identity, the current and desired model state at the moment of close,
the relevant TLA/spec snapshots, and the TLC/generated-case/adapter results that
support the close. After that record is written, instructions should recommend a
git commit so each ticket has both filesystem history and version-control
history.

The intuition is that every ticket becomes a small, durable evolution step. We
can later walk the spec history ticket by ticket without keeping all prior
desired/current context live. At the end of a larger close-out, transient
desired/current files can be deleted or reset, while the immutable ticket
history and committed TLA spec remain as the durable record.

Acceptance criteria:

- A `close-ticket.py` command exists for closing one ticket at a time.
- The command requires a ticket id or otherwise records an unambiguous ticket
  identity.
- The command writes a new immutable entry under
  `specs/.tla-spec-evolution/`, grouped clearly by ticket id.
- The entry records current and desired working-model snapshots.
- The entry records the relevant current TLA/spec/program-model snapshot.
- The entry records TLC, generated-case, and adapter/test evidence for the
  ticket.
- The entry records a human-readable summary of the ticket-specific change and
  any important mapping decisions.
- The command refuses to overwrite an existing close record for the same ticket
  unless a new explicit close id is supplied.
- The command output recommends committing the ticket, spec, and evolution
  entry after the close.
- The final close-out workflow can aggregate ticket close records, remove
  transient desired/current state, and recommend a final commit for the TLA spec
  and closed tickets.

Implementation:

- Added `scripts/close_ticket.py` and `scripts/close-ticket.py`.
- Ticket close entries are written under
  `specs/.tla-spec-evolution/tickets/<ticket-id>/<close-id>/`.
- Each entry includes `manifest.json`, `summary.md`, copied desired/current
  snapshots, copied top-level spec files, optional result evidence, and copied
  ticket files when they can be inferred.
- Existing close records are never overwritten.
