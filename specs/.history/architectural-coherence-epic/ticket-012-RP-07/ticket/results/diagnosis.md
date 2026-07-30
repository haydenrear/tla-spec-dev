# RP-07 — `spec.workflow.failure_cleanup_probe` diagnosis

**Verdict: outcome 1 — a real defect, in the probe node, fixed.**
Not flakiness, not a wrong assertion, not an unsatisfiable environment
assumption. The executor's process-ownership contract was correct and the node
was genuinely violating it.

## Reproduction

Worktree `/Users/hayde/IdeaProjects/wt-rp07-specworkflow-probe`, branched from
`epic/architectural-coherence` @ `b2d3a35`, probe source unmodified:

```
$ cd test_graph && ./gradlew specWorkflow --console=plain
> node spec.workflow.failure_cleanup_probe errored: node launcher exited with
  live descendants: 15805,15831
BUILD FAILED in 55s

$ cd test_graph && ./gradlew specWorkflow --console=plain
> node spec.workflow.failure_cleanup_probe errored: node launcher exited with
  live descendants: 16844
BUILD FAILED in 42s
```

Matches EV-02's report (`specs/.history/architectural-coherence-epic/`
`ticket-006-EV-02/ticket/results/test-graphs.txt`): same node, same message,
different PIDs each run.

## What the surviving PIDs are

The second run was taken with a 0.4s `ps -eo pid,ppid,lstart,state,comm,args`
sampler running alongside it. PID 16844 resolves, and its ancestry chain
reconstructs to:

```
22673  java ... org.gradle.launcher.daemon.bootstrap.GradleDaemon 8.14.3   (outer build)
 16778  perl -e ... POSIX setsid ...                    (SDK process-group supervisor)
  16779  uv run sources/spec_workflow_failure_cleanup_probe.py ...   <-- NODE LAUNCHER
   16788  python3 spec_workflow_failure_cleanup_probe.py
    16792  java -Xmx64m -Dorg.gradle.daemon=false ... GradleWrapperMain   (nested probe build)
     16807  java ... GradleDaemon                       (single-use daemon)
      16844  java ... org.jetbrains.kotlin.daemon.KotlinCompileDaemon
             --daemon-runFilesPath ~/Library/Application Support/kotlin/daemon
             --daemon-autoshutdownIdleSeconds=7200      <-- SURVIVOR
```

The survivor is the **Kotlin compile daemon**. It is a shared, user-scoped
service with a two-hour idle shutdown — designed to outlive the build that
started it. It is forked as a descendant of this node's launcher, so when the
launcher exits the daemon is still alive and the executor reports it, correctly,
as a leaked descendant.

The two-PID variant of the failure adds PID `…31`, Gradle's own single-use
daemon: with `--no-daemon` Gradle 8 forks a single-use daemon that stops itself
after the build, and it is sometimes still shutting down at the instant the
launcher's exit becomes observable. That is the source of the run-to-run
variation in the PID count; it is not the primary cause.

## Why the node forks a Kotlin daemon on every single run

`copy_probe_project` deletes and recopies the whole project each run with
`shutil.ignore_patterns("build", ".gradle", ...)`, so the nested build compiles
the `build-logic` Kotlin plugin **from scratch every time**. The Kotlin Gradle
plugin's default execution strategy is `daemon`, so every run forks a fresh
`KotlinCompileDaemon`.

Controlled A/B on an isolated copy of the probe project, all Kotlin daemons
killed before each arm, harness `descendant-contract-harness.py` (accumulates
every descendant PID ever observed, then reports which are still alive after
the launcher exits — the same inventory the executor builds with
`ProcessHandle.descendants()`):

| Arm | Nested build invocation | Observed descendants | Live after launcher exit |
|---|---|---|---|
| warm project (`build/` retained, no Kotlin compile) | as shipped | 71 | **0** |
| fresh copy (Kotlin compile happens) | as shipped | 69 | **1** — `KotlinCompileDaemon` |
| fresh copy (Kotlin compile happens) | `+ kotlin.compiler.execution.strategy=in-process` | 68 | **0** |

The warm-project arm is the control that isolates the cause: identical command,
identical project, no Kotlin compilation, no leak. One observed descendant
disappears between the second and third arms, and it is the daemon.

## Why this is not a false alarm from the contract

The daemon is not merely *reported*; the executor **reaps** it
(`terminateObservedTree` sends TERM then unconditional KILL). That daemon is
keyed on `~/Library/Application Support/kotlin/daemon` and is shared with the
*outer* Gradle build, so the reap reaches outside the node. A node that forks a
shared machine-scoped service into its own process tree is doing something the
contract is right to refuse.

## Why the probe was green before, on the same machine

`git log` on `test_graph/build-logic/.../exec/Executors.kt`: the last green run
of this node recorded in the repo is MF-027's, 2026-07-19
(`specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-*`). At that
commit `awaitWithTimeout` was a plain `process.waitFor(timeout)` with **no
descendant inventory at all** — the leak existed and was invisible. Commit
`0e3f00c` (2026-07-23, "chore: upgrade test graph observability scaffold")
replaced `test_graph/build-logic` and `test_graph/sdk` with symlinks into
`$SKILL_MANAGER_HOME/skills/test-graph/project_sdk_sources/`, which brought in
the POSIX process-group supervisor and the descendant contract. Nothing about
the probe's behavior changed on 2026-07-23; the instrument that can see it
arrived. The red is a newly *detected* defect, not a newly *introduced* one.

## Fix

In `test_graph/sources/spec_workflow_failure_cleanup_probe.py`, the nested
Gradle invocation now pins `kotlin.compiler.execution.strategy=in-process` on
both channels:

- `-Pkotlin.compiler.execution.strategy=in-process` on the command line —
  command-line project properties propagate into the `build-logic` **included
  build**, which is where the Kotlin compilation happens;
- `-Dkotlin.compiler.execution.strategy=in-process` in `GRADLE_OPTS`, alongside
  the pre-existing `-Dorg.gradle.daemon=false`.

The nested Kotlin compile then runs inside the process tree the node owns and
can reap. Verified that `build-logic/build/classes/kotlin/main/…` is populated
by the run, i.e. the compile really happened and was not simply skipped.

The node additionally asserts `nested probe build left no live descendants`
itself, after a bounded 20s drain that exists only for processes already
shutting down (Gradle's single-use daemon). Residue, if any, is written to
`node-logs/spec.workflow.failure_cleanup_probe.lingering-descendants.log` with
full command lines and **fails the assertion**.

### On evidence integrity

Nothing was weakened. The seven pre-existing probe assertions are unchanged and
all still pass; one assertion was **added**. The new in-node check is
deliberately *narrower* than the executor's — it drains for up to 20s where the
executor allows none, and it inspects only descendants of the node body rather
than of the launcher. It is a diagnostic that names the offending command lines,
not a replacement gate. The executor's `ProcessContractViolation` check is
untouched and remains the authority; if the in-node check were ever wrong, the
executor still fails the node.

Nothing under `$SKILL_MANAGER_HOME` was edited. `test_graph/build-logic` and
`test_graph/sdk` are symlinks into the installed skill; the contract lives there
and was left exactly as-is.

## Residual known behavior (not a defect)

Killing all Kotlin daemons and then running the graph leaves 2 Kotlin daemons
alive afterwards. They belong to the **outer** Gradle daemon (PID 22673 in the
trace above), which is not a descendant of any node launcher and is outside the
graph's ownership. The node's own subtree is empty at exit, which is what the
contract requires and what the new assertion measures.

## Files

- `test_graph/sources/spec_workflow_failure_cleanup_probe.py` — the fix
- `test_graph/README.md` — "The nested probe build must own every process it
  starts", so the flags are not silently dropped by a future edit
- `results/test-graphs.txt` — before/after graph runs
- `results/descendant-ancestry.txt` — the raw `ps` ancestry for the survivor
- `results/descendant-contract-harness.py` — the A/B harness
