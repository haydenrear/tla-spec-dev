# tla-spec-dev Test Graph

This graph validates the `tla-spec-dev` workflow against a disposable git
repository created under `test_graph/build/validation-reports/<runId>/`.

Run it from the repository root with the Test Graph skill wrappers:

```bash
# NOT `~/.skill-manager`: the test-graph unit lives in the home THIS checkout is
# bound to (a project or worktree `.skill-manager`), and only that copy matches
# the units this checkout was resolved against. See
# references/runtime_requirements.md, "Which Skill Manager home those tools come from".
"$SKILL_MANAGER_HOME"/skills/test-graph/scripts/discover.py specWorkflow
"$SKILL_MANAGER_HOME"/skills/test-graph/scripts/run.py specWorkflow
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

## The nested probe build must own every process it starts

`spec.workflow.failure_cleanup_probe` is the only node that runs a *nested*
Gradle build, so it is the only node that has to think about the executor's
process-ownership contract: when a node launcher exits while any descendant is
still alive, the executor reaps the tree and reports the node as errored with
`node launcher exited with live descendants: <pids>`.

The default Kotlin Gradle plugin compile strategy breaks that contract here.
The probe recopies the project on every run (`copy_probe_project` ignores
`build/`), so the nested build always compiles `build-logic` from scratch, and
the default `daemon` strategy forks
`KotlinCompileDaemon --daemon-autoshutdownIdleSeconds=7200`. That daemon is a
shared, deliberately persistent, user-scoped service — but it is forked as a
descendant of this node's launcher, so it outlives the node and the contract
correctly flags it. The daemon is also shared with the *outer* build, so the
executor's reap of it is not harmless.

The probe therefore pins `kotlin.compiler.execution.strategy=in-process` on
both channels — the `-P` project property (which propagates into the
`build-logic` included build) and the `-D` system property in `GRADLE_OPTS`.
The nested Kotlin compile then happens inside the process tree the node owns
and can reap. Do not drop either flag; the graph goes red at this node without
them.

The node also asserts `nested probe build left no live descendants` directly,
after a bounded drain for processes that are genuinely shutting down (Gradle's
single-use daemon closes its sockets before its exit is observable). That is a
strictly narrower window than the executor's own check, and it exists so a
future regression is reported with the offending command lines in
`node-logs/spec.workflow.failure_cleanup_probe.lingering-descendants.log`
instead of as bare PIDs in a build failure. The executor's check remains the
authority.
