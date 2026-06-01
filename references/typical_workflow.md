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

1. Update production code.
2. Update `current` to represent the whole program as now implemented.
3. Keep `desired_program_model/ticket_plan.yaml` synchronized with changes in
   scope, order, dependencies, and acceptance criteria.
4. Run TLC and current-model adapter or unit tests.
5. Record validation evidence in manifests or ticket status.
6. When the ticket is closed in `ticket_plan.yaml`, snapshot the workflow
   history:

```bash
python scripts/close-ticket.py TICKET-123 --repo-root path/to/repo --result path/to/repo/specs/results/tlc.txt
```

Do not model tests, CI jobs, test graph nodes, integration harnesses, or
validation workflow mechanics as TLA+ program state/actions. Record them as
evidence for semantic program actions.

Repeat until `current` semantically equals `desired_program_model`.

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
