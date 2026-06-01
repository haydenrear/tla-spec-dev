# Distributed History Workflow Example

This example demonstrates the model-backed ticket workflow with immutable
history.

It models a distributed fulfillment path:

- an API accepts orders;
- ticket `DIST-001` adds a durable outbox and broker publish step;
- ticket `DIST-002` adds an idempotent projection worker and acknowledgement.

The checked-in `specs/.history/distributed-fulfillment-history/` directory was
created by the replay script:

```bash
python examples/distributed_history/run_workflow.py
```

The script intentionally uses the public workflow commands:

- `scripts/onboard_program_model.py`
- `scripts/new_ticket_workflow.py`
- `scripts/close-ticket.py`
- `scripts/close_tickets.py`

After replay, the active `specs/current` and `specs/desired_program_model`
directories are closed out. The durable state is `specs/program_model` plus the
immutable history entries.

History entries are made read-only by the close commands. The replay script
temporarily makes its own example tree writable only so it can regenerate the
example from scratch.
