# The current→desired validation loop

After implementation starts, this is the loop that finishes the ticket. Its goal
is to land the ticket's `desired/` model and get the named graphs green, then
promote. It composes two things you already have — spec-double-compiler's ticket
close and test-graph's smart failure loop — into one close-out.

**It is bounded.** Two laps per layer, then stop: record the failure as
evidence, close the spec ticket with `--force`, and report what stayed red in
the PR body. A third lap has never turned a red layer green in this
programme's evals; what it did was spend the ticket's remaining tokens. The
spec ticket is a planning artifact, not the deliverable; the code and the
regression graphs are.

**Parent-only:** for an integration repo, every command here runs at the
integration **parent** worktree, which holds all constituent files as plain
files. Do not run per-constituent specs or graphs during the ticket — that happens
after fan-out, per `references/agent-tag-pr.md`.

## The four validation layers

Each iteration proves the slice at up to four layers. Run the ones the ticket
has; a project without the optional spec layer (no `case_adapters.toml`, no
`specWorkflow` graph) runs layers 2 and 3 only:

1. **Spec unit tests** — the generated spec-double self-tests / spec-unit adapters
   for the ticket.
   ```bash
   tla-spec-dev --spec-root specs run spec-unit-tests --ticket <ticket>
   ```
2. **Unit tests** — the repo's own suite for the changed code (its normal runner:
   `pytest`, `./gradlew test`, etc.).
3. **Test graph** — the named regression graphs from the issue, run via the
   test-graph scripts.
   ```bash
   TG=<test-graph-skill>/scripts
   $TG/discover.py <graph>      # confirm composition before running
   $TG/run.py <graph>           # one graph; or: $TG/run.py --all
   ```
4. **Spec graph (tla-spec-dev spec graph)** — the graph that exercises the
   generated spec doubles against the real adapters, so a spec/impl divergence
   fails loudly. Always include it when the ticket has a spec workflow.
   ```bash
   $TG/discover.py specWorkflow
   $TG/run.py specWorkflow
   ```

## The fifth layer: the goal signal (advisory, never a gate)

When the work order declares a goal — an epic assignment's `goals:` block or an
ordinary issue's `## Goals & evaluation` section — there is one more thing to run
before close, and it is deliberately **not** one of the four above:

```bash
<the declared local_signal>          # store its output under the evidence root
```

It sits outside the four layers because it answers a different question. The four
layers ask *did this land correctly*, and each one is pass/fail. The goal signal
asks *did this move what the work was for*, and it has no pass state at all —
only a measurement and a classification: moved as expected, moved less than
expected, no measurable movement, or moved the wrong way. Record it, do not gate
on it.

Keeping it a separate layer is the whole point. Folded into the four, it becomes
a fifth thing to make green, and an agent will start tuning to the metric,
re-running until a number improves, or reaching outside the slice to move it —
which is how a set of individually-defensible tickets ends up optimizing proxies
instead of delivering the outcome. The REQUIRED matrix decides pass/fail; the
named evaluation ticket decides the goal. Details, classifications, and the
reporting format: `references/goal-signal.md`.

## The loop, per slice

At most two laps:

1. **Advance the model.** Update ticket-local `desired/` with anything learned
   from the last slice (ticket breakdown, status, validation commands). There is
   no ticket-local `current/` unless the ticket was opened with `--with-current`;
   `desired/` is the whole-program model after this ticket.
2. **Update adapters/tests first.** Add or update the ticket-local spec-unit
   adapters and, if the observable surface moved, the External/Internal test-graph
   adapters and nodes — before or alongside the code.
3. **Run TLC + the four layers** (above) for the slice. Prefer the **narrow graph**
   for the slice while iterating; run the full named set before close-out.
4. **On a graph failure, don't blindly rerun the whole graph.** Use test-graph's
   smart failure loop: read `build/validation-reports/<runId>/report.md`, rerun the
   single failed node from its saved context (`run.py <graph> --resume-from-build
   <dir> --run-only-node <id>`), iterate on that node, then rerun the whole graph
   once from the start to confirm ordering and fresh context.
5. **Close the slice's ticket.** Record evidence and close:
   ```bash
   tla-spec-dev --spec-root specs close ticket <ticket> \
     --result <evidence-path> --summary "<what landed>"
   ```
   Close moves the ticket dir to history, replaces project `specs/current` with the
   ticket's `desired/`, and merges ticket-local test-graph artifacts into project
   specs. If it refuses, rerun with `--force` and say why in the summary; never
   edit the plan's status to get past it.
6. **Commit** the spec change, close record, and evidence together.

## Convergence and promotion

When every slice's ticket has closed and the named graph set is green, or
when the two-lap bound is spent and the reds are recorded, promote the model
into the accepted baseline and clean up the workflow directories:

```bash
python <tla-spec-dev>/scripts/close_tickets.py --repo-root . \
  --summary "Promoted desired/current into program_model"
```

Promotion writes the workflow close record, replaces `program_model` with the
converged model, and removes `specs/current` + `specs/desired_program_model` once
they carry no distinct planning state. After this, the spec workflow is closed and
you return to `references/complete.md` to finish the PR and issue.

## Definition of done for the loop

- [ ] Spec unit tests green (`run spec-unit-tests --ticket <ticket>`), when the project has them
- [ ] Repo unit tests green
- [ ] Named test_graph graphs green (smart-failure-loop clean, full rerun clean)
- [ ] tla-spec-dev spec graph green (`specWorkflow`), when the project has one
- [ ] Every ticket closed in `ticket_plan.yaml` (forced closes recorded in the summary)
- [ ] Model promoted into `program_model`; workflow dirs cleaned
- [ ] Evidence recorded and committed

The goal signal has its own definition of done, and "green" is not part of it:

- [ ] Every declared `local_signal` run once (or `N/A: <reason>` recorded)
- [ ] Its output stored under the evidence root and classified
- [ ] The classification reported in the PR body — including "no measurable
      movement" and "moved the wrong way"

**Recorded and reported**, not green. A signal that moved the wrong way leaves
this loop done; it is reported and, where it shows the goal is unreachable from
this slice, filed as a deferred finding. It never blocks close, and it is never
grounds for another lap.
