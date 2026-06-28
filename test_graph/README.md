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
2. `spec.workflow.start` runs `tla-spec-dev --spec-root specs scaffold project`,
   `tla-spec-dev --spec-root specs scaffold workflow`, and
   `tla-spec-dev --spec-root specs open ticket`.
3. `spec.workflow.complete` updates ticket-local `desired/` first, mirrors it
   into `current/`, adds spec adapter/test files, adds Test Graph artifacts, and
   marks the ticket done.
4. `spec.workflow.spec_units` runs
   `tla-spec-dev --spec-root specs run spec-unit-tests` against the
   ticket-local `current/` spec tests.
5. `spec.workflow.close` runs `tla-spec-dev --spec-root specs close ticket`,
   asserts ticket
   `current/ == desired/` closed correctly, verifies project `specs/current`
   and Test Graph artifacts were merged, and commits the close in the temp repo.
6. `spec.workflow.failure_cleanup_probe` creates a separate temporary Test Graph
   project, runs an intentionally failing graph after repository allocation, and
   asserts that the cleanup finalizer still removed that failed graph's fixture
   repo.
7. `spec.workflow.cleanup` removes the disposable git repository from the build
   directory.

The graph is intentionally external to the unit tests: it proves the CLI
work when invoked from a real git-backed repository, including history movement,
promotion, adapter/test merging, and cleanup after both passing and failing
downstream graph paths.
