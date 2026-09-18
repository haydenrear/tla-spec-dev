# Ticket SI-06: Implementation skills propose a change when blocked, and stop editing the model

This directory is the active, ticket-local spec workflow for one ticket.

Layout:

- `ticket.yaml`: copied ticket-plan entry and lifecycle metadata.
- `desired/`: the whole-program state that should be true after this ticket.
- `testgraph/`: copied Test Graph bindings/selectors/assertions when present.
- `results/`: ticket-local TLC, adapter, Test Graph, and review evidence.

Workflow:

1. Edit `desired/`. It starts as a copy of the project current model; change
   its TLA+, configs and, when the project has them, generated-case metadata,
   spec adapters, tests, and Test Graph bindings so it represents the
   whole-program state after this ticket is done. Run TLC on it once.
2. Implement the ticket.
3. If this ticket adds spec-unit or Test Graph coverage, keep those adapters,
   tests, bindings, selectors, and assertions in the ticket directory.
4. Run TLC and, when the project has them, generated spec-unit adapters and
   Test Graph validation.
5. Mark the global ticket-plan entry done.
6. Run `tla-spec-dev --spec-root specs close ticket SI-06`. Closing replaces
   project `specs/current` with ticket `desired/`, merges ticket Test Graph
   config back into project specs, snapshots this directory into history, and
   removes the active ticket directory. If it refuses, rerun with `--force`
   and say why in `--summary`; never edit the plan's status to get past it.

Starting source: `/Users/hayde/IdeaProjects/wt-epic-self-improvement-substrate/specs/current`

Future worktree support should attach the ticket worktree here, but this
scaffold intentionally records only the spec-side state for now.
