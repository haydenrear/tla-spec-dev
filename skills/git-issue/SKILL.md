---
name: git-issue
description: >-
  Use when creating a tracker issue that an agent will pick up and implement —
  especially GitHub issues via the `gh` CLI. Drives a discovery-first workflow:
  scan the repo before writing, embed a References section as the implementer's
  discovery starting point, name the measurable goal the change is aimed at and
  the instrument that decides it, tell the implementer to create a worktree and
  feature branch, optionally bind the issue to one ticket in an owner-created
  epic/* shared spec workflow, decide whether a TLA+ spec workflow is needed
  (Internal.tla / External.tla changes, test-graph and unit-test adapter updates
  opened with spec-double-compiler + tla-spec-dev), and spell out the regression
  test graphs, spec/unit tests, goal contribution, spec-ticket close-out, and
  commit/push that finish the work. Trigger on "file an issue", "create a
  ticket", "open a GitHub issue", scheduling an issue in an epic branch, or
  planning work that another agent will implement.
skill-imports:
  - unit: spec-double-compiler
    path: SKILL.md
    reason: When an issue needs a spec workflow, it drives Internal.tla/External.tla spec doubles and spec unit tests via the tla-spec-dev CLI.
  - unit: test-graph
    path: SKILL.md
    reason: The issue's regression section names test_graph graphs to run for regression, including tla-spec-dev spec-graph integrations.
  - unit: deploy-helm
    path: SKILL.md
    reason: Issues that touch deployable surfaces reference deploy-helm environments for validation.
  - unit: skt
    path: skills/skill-manager/references/workflows.md
    reason: This skill is installed and synced as a skill-manager unit.
---

# git-issue

Create issues that another agent can pick up and implement end-to-end without
re-discovering the whole repository. An issue produced by this skill is a
**work order**: it carries the discovery you already did, points the implementer
at a worktree/branch, names the measurable outcome the change is aimed at,
decides up front whether the change needs a TLA+ spec workflow, and lists
exactly which tests close it out.

An issue that says what it changes but not what should be measurably better
afterwards hands the implementer no result to aim at, and produces a PR whose
only claim is "tests pass". So goal linkage is part of every work order, not
only epic ones: a metric with a named instrument that decides it, never an
adjective. An issue with no measurable outcome says so explicitly
(`N/A: <reason>`) rather than dropping the section. The canonical contract for
goal kinds, baselines, contribution kinds, judged versus mechanical instruments,
and the evaluation-ticket role is
`<git-epic-workflow-skill>/references/goals-and-evaluation.md`; this skill
captures the same fields under the same names. Its worked example of a judged
instrument is `tla-spec-dev`'s `references/eval_scorecard.md`, which stays the
authority on that card — this skill adds no fields of its own for it.

**An issue names a rubric; it never copies one.** Write which rubric, which
version, how many judges, and where the evidence lands, then link the rubric. Do
not paste its dimensions, its anchors, its scoring rules or its comparability
rules into an issue body: the rubric's own repository versions those and runs
checks over them, and a copy in a tracker has nothing behind it. The failure is
measured rather than hypothetical — a charter in `tla-spec-dev` restated a table
of judged results and two of its rows were wrong, carried forward across a
change to the instrument before anyone caught them.

An issue may instead be one scheduled slice of an existing epic. In that mode,
keep the ordinary work-order sections and add the marker-delimited assignment
from `references/epic-assignment.md`. That assignment takes precedence over
ordinary default-branch worktree, PR-target, and issue-close instructions.

The core workflow is **tracker-agnostic**. GitHub via the `gh` CLI is the
default and only wired adapter; see `references/github-gh.md`. To target another
tracker, keep every step below and swap only the create/comment/close commands.

## The six moves

1. **Discover before you write.** Never open an issue from the title alone.
   Scan the repo to locate the code, specs, tests, and docs the change will
   touch — **and the measurement surface** that could decide whether it worked:
   benchmarks, eval datasets and scorers, perf-marked suites, end-to-end graphs,
   recorded baselines. See `references/discovery.md`.
2. **Capture the goal and what decides it.** Before writing the body, ask the
   user what should be measurably better after this issue, which instrument
   decides it — a command, or a judged procedure with its rubric — what it
   reports today, and which threshold counts as success (or that there
   deliberately is none). Then state this issue's relation to that goal —
   `direct`, `enabling`, or `guard` — with the effect it is expected to produce
   and a cheap local signal the implementer can run in its own worktree. A
   judged instrument is rarely the right local signal: judging is expensive, and
   a rubric's own noise can swamp one ticket's movement. Do not invent a metric, a
   baseline, or a target the user did not agree to: ask, or record
   `N/A: <reason>`. The measurement inventory from move 1 is what makes a
   specific goal writable instead of an adjective. In epic mode these fields are
   not asked for at all — they are copied from the epic's canonical plan through
   `references/epic-assignment.md`.
3. **Write the issue with a References section.** The issue body embeds the
   discovery output as a *starting point* for the implementer — concrete files,
   symbols, specs, and docs, each as `path:line` where possible. Create it with
   `gh issue create`. See `references/github-gh.md` and the template below.
4. **Instruct a worktree + feature branch.** The issue embeds **one command**
   that creates the worktree and its own Skill Manager home together — `wt new`,
   spelled as a path that resolves without the reader looking anything up — plus
   what to do about that home: that a skill edit inside it is in no diff, and
   that teardown is gated. Never instruct a bare `git worktree add`; it produces
   a worktree with no home. An epic assignment instead names the exact worktree
   and branch created from the epic branch, and is the one case that does branch
   by hand. See `references/worktree-branch.md` and
   `references/epic-assignment.md`.
5. **Decide the spec workflow.** During discovery, decide whether the change
   alters observable/internal state-machine behavior. If yes, the issue names
   the Internal.tla / External.tla edits, the test-graph and unit-test adapter
   updates, and tells the implementer to open the spec workflow with
   **spec-double-compiler + tla-spec-dev** at branch-creation time. For an epic,
   the owner scaffolds one shared workflow and each issue opens exactly its one
   planned ticket; the ticket agent never scaffolds again. See
   `references/spec-workflow.md`.
6. **Spell out close-out.** The issue lists which test graphs run for regression
   (including tla-spec-dev spec-graph integrations), tells the implementer to
   attach those reports to the spec ticket that closes in the repo, close that
   ticket via spec-double-compiler + tla-spec-dev, run spec unit tests and unit
   tests, **report the goal contribution in the PR body**, then commit and push
   to the feature branch. An epic work order supplies exact validation commands
   and evidence paths, targets its PR at the epic branch, and stops for external
   review. See `references/regression-close.md`.

## Before you create the issue

Run discovery (`references/discovery.md`) and answer these, because they change
what the issue body must contain:

- **What does this touch?** The file/symbol list becomes the References section.
- **What should be measurably better, and what decides it?** The metric, the
  deciding instrument, today's value, and the success threshold become the
  `## Goals & evaluation` section (move 2). Ask the user; do not derive a target
  from the codebase. If there is genuinely nothing to measure, the answer is
  `N/A: <reason>`, which is a recorded decision rather than a skipped question.
- **Does it change a named model element?** Decides the spec-workflow section
  (move 5). Default NOT REQUIRED; mark REQUIRED only when you can name the
  `Internal.tla` action, variable, or invariant that changes
  (`references/spec-workflow.md`).
- **What could it regress?** The affected test graphs become the close-out
  checklist (move 6).
- **Ordinary issue or epic assignment?** Epic mode is valid only after the epic
  owner has created and pushed the epic branch, scaffolded the shared workflow
  once, and planned the issue's one stable spec ticket. Collect the assignment
  fields in `references/epic-assignment.md`; do not invent or scaffold a second
  workflow while authoring the issue.

## One issue, or an epic?

The goal question is also the routing question. One issue can carry one goal it
either decides itself or contributes to. When the request is several slices that
only make sense together — they share one outcome, land in a sequence, or none
of them alone moves the metric — say so and route to **`git-epic-workflow`**
instead of filing them as loose issues. That skill agrees the goals with the
user, records them in the canonical plan, schedules the terminal
evaluation/perf/integration ticket that decides each one, and dispatches each
slice back here as an epic assignment.

Signals that this is an epic rather than an issue:

- the outcome is only measurable after several slices have landed together;
- one slice exists to build the harness or baseline the others are judged by;
- the deciding instrument has to run on an integrated branch, not in one
  worktree;
- the `## Goals & evaluation` section would name a "decided by" ticket that does
  not exist yet.

Do not let a single issue silently become an unscheduled epic. An issue whose
goal nothing is scheduled to measure is a goal nobody will decide — file the
epic, or narrow the issue until its own harness run decides its goal.

## Issue body template

Fill every section. Omit a section only when it is genuinely N/A, and say so
explicitly rather than deleting it — the implementer relies on the shape.

```markdown
## Summary
<one paragraph: the change and why it matters>

## Goals & evaluation
- **Goal**: <what should be measurably better after this issue>
- **Metric / harness**: <the instrument that decides it: an exact command, or a judged procedure and its rubric>
- **Baseline → target**: <today's value> → <threshold that counts as success>
- **This issue's contribution**: direct | enabling | guard — <expected effect>
- **Local signal**: <cheap command the implementer runs in its own worktree, or N/A: reason>
- **Decided by**: <final eval/perf/integration ticket or issue, or "this issue's own harness run">

## References  <!-- discovery starting point; not exhaustive -->
- `path/to/file.ext:LINE` — <why it's relevant>
- `path/to/Spec.tla` — <state machine this touches, if any>
- <doc / ADR / prior issue / PR links>

## Discovery notes
<what you learned scanning the repo: entry points, invariants, adjacent code,
open questions the implementer should resolve first>

## Worktree & branch
Create the worktree AND its own Skill Manager home with ONE command, from the
repo root. It is the same command for a plain repo and an integration repo:
`WT="${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/skills/git-issue-workflow/scripts/wt"`
`"$WT" new <issue-number>-<slug>`
It prints one line — `created worktree <path>`. **cd to the path it printed.**
That path is `<parent>/<repo-name>-<issue-number>-<slug>`, not `../wt-...`, so
do not guess it.
If it exits 3 saying "no project home yet", this repository has never been given
a home. Run the absolute `fix:` line it printed — a one-time, per-repository
step — then run the same `wt new` again.
If it exits 7 saying the base is **behind** its remote, the branch you named is a
local ref that has fallen behind `origin/<base>` — usual on an `epic/*` branch
whose ticket PRs were merged server-side. Run the `fix:` line, which branches
from the published tip; `--stale-base-ok` takes the local ref deliberately.
Do **not** substitute `git worktree add`: that produces a worktree with no home,
and an agent launched in it writes the operator's global `~/.skill-manager`.
Launch through `<worktree>/.skill-manager/bin/launch/{claude,codex,gemini}`.
Any skill edit you make inside that home is in no diff and is deleted with the
worktree — publish it with
`skill-manager unit publish <unit> --ticket <issue-number>`.
(see references/worktree-branch.md)

## Spec workflow — REQUIRED | NOT REQUIRED
<!-- Default NOT REQUIRED: state why in one line. REQUIRED only when the model element below is named. -->
On feature-branch creation, open the spec workflow with spec-double-compiler +
tla-spec-dev. Expected changes:
- **Internal.tla**: <state/vars/actions to add or change>
- **External.tla**: <observable behavior / interface to add or change>
- **Test graph**: <spec-graph nodes/cases to add or update>
- **Unit-test adapters**: <adapter conformance tests to add or update>

## Regression & close-out
Run these to close the issue:
- **Test graphs**: <named graphs>, including the tla-spec-dev spec-graph integration graph
- Attach the test-graph reports to the spec ticket that closes out in the repo
- Close the spec ticket via spec-double-compiler + tla-spec-dev
- Run spec unit tests and unit tests
- Commit and push to `feature/<issue-number>-<slug>`
- Report the goal contribution in the PR body (`## Goal contribution`): expected
  effect, measured local signal or `N/A: reason`, and what decides the goal
- Tear the worktree down with `"$WT" close <issue-number>-<slug>` — one command,
  same in both repo shapes. It runs the home close-out gate first and **refuses**
  while the worktree still holds skill work that removing it would destroy, then
  removes the worktree. Clear every blocker it names and re-run; never fall back
  to `git worktree remove`, which deletes the home without a word. Run it from
  inside any git repository (it resolves the ticket by search, so it need not be
  the repo that opened the worktree — but it must be *a* repo).
```

### Filling `## Goals & evaluation`

- Every bullet is filled or explicitly `N/A: <reason>`. Never delete the section
  and never leave a placeholder: an omitted section reads as "no goal was
  considered", which is exactly what this section exists to rule out.
- **Metric / harness** names the instrument that decides the goal. Usually that
  is a command someone can run; it may instead be a **judged procedure** — an
  artifact scored against a versioned rubric by judges who cite the artifact —
  or a mechanical block read beside a judged one. Write which, concretely. A
  goal nobody can decide is a slogan; a goal decided by judgement is not a
  slogan just because a human runs it. Either find the instrument in the
  measurement inventory (`references/discovery.md`), scope the issue to build
  it, or record the goal as `N/A: <reason>`.
- **Baseline → target** needs both halves. A target with no baseline is
  unfalsifiable; if the number has not been measured, write
  `unmeasured — <how the implementer measures it first>` rather than guessing.
  Two shapes are legitimately not a threshold, and both are written plainly
  rather than dressed up as one: a **multi-clause target**, whose clauses can
  settle differently and are reported one verdict each; and a goal that is
  **building the instrument**, whose target says there is deliberately no
  threshold on the number, because choosing one before anything can produce a
  number is inventing the answer. Where the instrument is a judged one, the
  baseline cites the prior scored run rather than a recollection.
- **Contribution** is one of `direct` (this change is expected to move the
  metric — give a directional or numeric effect), `enabling` (`none — enabling
  only`, plus what it unblocks), or `guard` (must not regress this metric while
  targeting something else — the local signal is the regression check).
- **Local signal** is a *signal, not a gate*. The implementer runs it, records
  the number, and reports it even when it moves the wrong way. It never
  justifies weakening a required test, tuning to the metric, or widening scope.
- **Decided by** names the run that settles the goal — this issue's own harness
  run for an ordinary issue, or the epic's evaluation ticket in epic mode.

For epic mode, retain every standard section above and insert the rendered
marker-delimited block from `references/epic-assignment.md` between the completed
Summary section and `## Goals & evaluation`, so the section order becomes
Summary → assignment → Goals & evaluation → References. The block is the
machine-readable override; do not merely describe the epic in prose.

Keep the `## Goals & evaluation` section in epic mode and render it **from the
assignment's `goals:` entries**, not from a fresh conversation with the user: the
epic already agreed those goals and recorded them in its canonical plan, so the
prose section restates them for a human reader and must not introduce a metric,
baseline, target, or contribution the assignment does not carry. Where the two
disagree, the assignment wins and the mismatch is a dispatch error to fix before
the issue is worked (`references/epic-assignment.md`).

## Operating order

1. Confirm `gh` is authenticated and the repo is right
   (`references/github-gh.md`).
2. Discover (`references/discovery.md`) → collect References, the measurement
   inventory, and regression scope.
3. Settle the goal: metric, deciding instrument, today's value, success
   threshold, this issue's contribution, and its local signal — asked of the
   user for an
   ordinary issue, copied from the assignment in epic mode, or recorded as
   `N/A: <reason>`. If the outcome needs several slices, route to
   `git-epic-workflow` instead of filing one issue.
4. Decide the spec workflow (`references/spec-workflow.md`). If the epic owner
   supplied a planned ticket, select epic mode and validate its assignment
   (`references/epic-assignment.md`).
5. Render the template, create the issue with `gh issue create`, capture the
   issue number/URL. For a new epic issue, use that number to finalize the
   feature branch and worktree fields, then edit the body with the complete
   assignment. For an existing issue, preserve its body and replace only the
   bounded assignment region.
6. For an ordinary required spec workflow, note that the implementer opens the
   in-repo ticket on branch creation. For an epic, verify the issue maps to one
   existing planned ticket and instruct the implementer to run only `open ticket
   <id>` against the already-scaffolded shared workflow.

## Boundaries

- This skill **creates and structures** issues; it does not implement them. The
  implementing agent follows the worktree/spec/close-out instructions the issue
  carries.
- It does not run test graphs or the spec workflow itself — it names them so the
  implementer runs them. The mechanics live in the referenced skills
  (test-graph, spec-double-compiler, deploy-helm).
- It does not close issues automatically; close-out is the implementer's final
  commit/push plus ticket close.
- **It does not invent goals, baselines, or targets.** Those are the user's to
  state. Ask for them; if the user has no measurable outcome, record
  `N/A: <reason>` rather than manufacturing a metric that will later be reported
  as if it had been agreed. In epic mode the values come from the canonical plan
  and are copied, never authored here.
- It does not run the harness or measure the baseline itself — it names the
  command so the implementer or the evaluation ticket runs it. A goal recorded
  with an unmeasured baseline says so.
- It does not schedule an epic's goals or its evaluation ticket. A request whose
  outcome spans several slices belongs to `git-epic-workflow`, which plans the
  goals and the ticket that decides them and dispatches the slices back here.
- It does not create an epic branch or scaffold a shared epic workflow. The epic
  owner supplies those artifacts and the canonical ticket plan before this
  skill writes an epic assignment.
- An epic ticket PR uses `Refs #<issue>`, targets the declared epic branch, and
  stops for external review. It does not close the GitHub issue or merge into
  either the epic or default branch: the epic-owner agent merges it into the
  epic branch at wave close, and issue close is epic finalization's.
