# Typical Workflow

Use one accepted whole-program model as the durable baseline. Use
`current` and `desired_program_model` only during active ticketed behavior
changes.

## 1. Onboard A New Repository

When a repository has no accepted program model yet, create only the baseline:

```bash
python scripts/onboard_program_model.py --repo-root path/to/repo --name ProjectName
```

This creates:

- `specs/program_model`: accepted whole-program semantic baseline.

Do not create `specs/current`, `specs/desired_program_model`, or
`ticket_plan.yaml` during first onboarding.

If the repository keeps specs outside `specs`, pass the same spec root to later
onboarding and ticket workflow commands:

```bash
python scripts/onboard_program_model.py --repo-root path/to/repo --name ProjectName --spec-root project_specs
python scripts/new_ticket_workflow.py TICKET-123 "Ticket title" --repo-root path/to/repo --spec-root project_specs
```

## 2. Start A Feature Or Behavior Change

After `program_model` exists, start the ticket workflow:

```bash
python scripts/new_ticket_workflow.py TICKET-123 "Ticket title" --repo-root path/to/repo
```

This resolves directories under `--spec-root`, defaulting to `specs`, and
creates:

- `specs/current`: executable whole-program model of what has landed so far.
- `specs/desired_program_model`: target whole-program model plus ticket plan.
- `specs/desired_program_model/ticket_plan.yaml`: phases, tickets,
  dependencies, acceptance criteria, validation commands, and evidence slots.

The scaffold copies useful baseline files from `program_model` into both
workflow directories before adding ticket metadata. `current` should start as
the whole accepted model, not as a feature-only projection.

## 3. Work Ticket By Ticket

For each ticket or implementation slice:

1. Scaffold a ticket-local workspace from the plan:

```bash
python scripts/start_ticket.py TICKET-123 --repo-root path/to/repo
```

This creates `specs/tickets/TICKET-123/current`, `desired`, `results`, and any
copied Test Graph configuration. Ticket `desired` is the whole-program state at
the end of this ticket, not the whole project destination.

2. Update production code.
3. Update `specs/tickets/TICKET-123/current` to represent the whole program as
   now implemented for this ticket.
4. Update `specs/tickets/TICKET-123/desired` to represent the expected
   post-ticket whole-program state.
5. Keep `desired_program_model/ticket_plan.yaml` synchronized with changes in
   scope, order, dependencies, and acceptance criteria.
6. Run TLC, generated adapter tests, and Test Graph validation as needed.
7. Record validation evidence in the ticket `results/` directory, manifests, or
   ticket status.
8. When ticket-local `current` semantically equals ticket-local `desired`, mark
   the ticket closed in `ticket_plan.yaml`, then close the ticket:

```bash
python scripts/close-ticket.py TICKET-123 --repo-root path/to/repo --result path/to/repo/specs/results/tlc.txt
```

Closing moves `specs/tickets/TICKET-123` into history and promotes its
`desired/` directory to project-level `specs/current`.

Do not model tests, CI jobs, test graph nodes, integration harnesses, or
validation workflow mechanics as TLA+ program state/actions. Record them as
evidence for semantic program actions.

Repeat until project `current` semantically equals `desired_program_model`.

## 4. Close The Ticket Workflow

When the desired model has landed:

1. Promote the converged model into `program_model`.
2. Regenerate accepted artifacts from `program_model`.
3. Run accepted program-model validation.
4. Close the temporary workflow directories and record `closed-snapshot` under
   `specs/.history/<workflow-name>/`:

```bash
python scripts/close_tickets.py --repo-root path/to/repo
```

Use the same `--spec-root` used to scaffold the workflow when it is not
`specs`.

`close_tickets.py` validates that:

- semantic model files in `current` and `desired_program_model` match;
- semantic model files in `desired_program_model` and `program_model` match,
  proving promotion happened;
- every ticket in `desired_program_model/ticket_plan.yaml` has a closed status.

It ignores planning/status-only fields for manifest comparison, but it does not
ignore open tickets.
