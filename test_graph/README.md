# tla-spec-dev Test Graph

This graph validates the `tla-spec-dev` workflow against a disposable git
repository created under `test_graph/build/validation-reports/<runId>/`.

Run it from the repository root with the Test Graph skill wrappers:

```bash
/Users/hayde/.skill-manager/skills/test-graph/scripts/discover.py specWorkflow
/Users/hayde/.skill-manager/skills/test-graph/scripts/run.py specWorkflow
```

The `specWorkflow` graph performs the workflow end to end:

1. `spec.workflow.repo` creates a temporary git repository with
   no spec model yet and publishes the installed `tla-spec-dev` path.
2. `spec.workflow.start` runs `tla-spec-dev scaffold project`,
   `tla-spec-dev scaffold workflow`, and then the lower-level ticket-open
   script until CLI-004 lands.
3. `spec.workflow.complete` updates ticket-local `desired/` first, mirrors it
   into `current/`, adds spec adapter/test files, adds Test Graph artifacts, and
   marks the ticket done.
4. `spec.workflow.close` runs `scripts/close_ticket.py`, asserts ticket
   `current/ == desired/` closed correctly, verifies project `specs/current`
   and Test Graph artifacts were merged, and commits the close in the temp repo.
5. `spec.workflow.cleanup` removes the disposable git repository from the build
   directory.

The graph is intentionally external to the unit tests: it proves the CLI
work when invoked from a real git-backed repository, including history movement,
promotion, adapter/test merging, and cleanup.
