---
name: git-epic-workflow
description: >-
  Use when planning, starting, scheduling, resuming, or finalizing a multi-ticket
  Git epic on an epic/* branch backed by one shared spec-double-compiler workflow.
  Also use when a GitHub issue contains a git-epic-workflow assignment and must
  be implemented against an epic branch instead of the default branch. Agrees
  measurable epic goals with the user up front, relates every ticket to a final
  evaluation/perf/integration ticket that decides them, and composes git-issue
  issue authoring, git-issue-workflow ticket execution, tla-spec-dev ticket
  promotion, and Test Graph validation while allowing dependency-aware parallel
  work and serialized integration. Epic and ticket worktrees are branched by
  hand from the declared epic branch and then given their own per-checkout Skill
  Manager home with git-issue-workflow's `scripts/bootstrap-home.sh`; teardown
  is that skill's `scripts/wt close <ticket>`. A bare `git worktree add` with no
  home step leaves the ticket agent writing the operator's global home.
skill-imports:
  - unit: git-issue
    path: SKILL.md
    reason: Epic issues retain the discovery, references, spec decision, and validation work-order structure authored by git-issue.
  - unit: git-issue-workflow
    path: SKILL.md
    reason: Ticket agents execute epic assignments through the implementer workflow with the epic overrides defined here.
  - unit: spec-double-compiler
    path: references/spec_evolution.md
    reason: Defines ticket-local current/desired state, append-only ticket close history, promotion, and whole-workflow closeout.
  - unit: test-graph
    path: references/workflows.md
    reason: Defines graph discovery, execution, evidence, and the smart failure loop used by every ticket and by epic finalization.
  - unit: skill-manager
    path: references/workflows.md
    reason: Defines how installed dependent skills and their managed tools are resolved at runtime.
---

# git-epic-workflow

Coordinate several GitHub issues through one `epic/<slug>` branch and one
shared desired/current TLA+ workflow. The epic branch is the integration branch;
ticket branches start from it and target it. The default branch changes only
through the final epic PR.

This skill has three roles:

- **Plan and schedule:** agree the epic's measurable goals, then create the epic
  branch, shared spec workflow, ticket DAG, evaluation tickets, issues, and
  handoff metadata. Read `references/goals-and-evaluation.md`,
  `references/plan-and-schedule.md`, and `references/epic-ticket.md`.
- **Perform one ticket:** detect the epic assignment in an issue and apply its
  overrides to `git-issue-workflow`. Read `references/epic-ticket.md` before
  creating a worktree.
- **Finalize:** validate the integrated epic, promote the accepted program
  model, close the shared spec workflow, and open the epic PR. Read
  `references/finalize.md`.

## Load-bearing rules

1. **The plan is canonical.** Keep the complete schedule in
   `specs/desired_program_model/ticket_plan.yaml`. GitHub issues mirror it for
   handoff; they do not replace it.
2. **One epic, one branch, one workflow.** Create one `epic/<slug>` from the
   current default-branch tip and scaffold the spec workflow once. Give the
   workflow a unique stable name. Never force-push the epic branch.
3. **Dispatched identities are immutable.** Do not reorder or rename ticket IDs
   after publishing issue assignments; close-history paths depend on plan order
   and IDs. Add a new ticket when scope changes.
4. **The epic assignment wins.** Its marker-delimited block overrides ordinary
   `git-issue` instructions that branch from or merge to the default branch.
5. **Ticket agents close one ticket only.** They run `open ticket <id>`, update
   the implementation, specs, spec-unit adapters, Test Graph adapters/nodes,
   record evidence, and run `close ticket <id>`. They never run
   `close_tickets.py` or promote the whole workflow.
6. **Parallel work; serialized promotion.** `depends_on` controls when work may
   start. A separate total `promotion_predecessor` order controls when a ticket
   may rebase onto the latest epic tip, close/promote its ticket, and enter the
   epic branch. The promotion order must be a topological extension of
   `depends_on`; two ticket promotions never integrate concurrently.
7. **External review is the default.** A ticket agent stops after pushing a
   sealed branch and opening a PR whose base is the epic branch. It does not
   merge the PR, merge to the default branch, or close the GitHub issue.
8. **Only finalization closes the workflow.** After all ticket PRs are on the
   epic branch, the finalizer runs integrated validation, promotes the accepted
   model, closes the workflow, and opens the epic PR against the default branch.
9. **Out-of-scope findings are deferred, not chased.** Agree a deferment policy
   with the user when the epic branch is created. Ticket agents report failure
   cases outside their declared slice to an append-only backlog instead of
   expanding scope to fix them. Read `references/deferment.md`.
10. **A ticket's Skill Manager home is not carried by its PR.** Every worktree an
    epic creates — the epic worktree and each ticket worktree — has its own
    `<worktree>/.skill-manager`, a real copy of the project home. It is
    gitignored, so nothing a ticket agent changed inside it appears in the ticket
    PR, in the epic branch, or in the epic PR. It reaches the tier above only
    through `skill-manager home sync`, and the unit's own repository only through
    `skill-manager unit publish`. An epic cannot finalize until every ticket
    worktree has been through `skill-manager home close-out` — see
    `references/plan-and-schedule.md` §2 and `references/finalize.md` §1b.

    **That home does not appear on its own.** An epic branches by hand, because
    the epic branch and every ticket worktree path are *declared* by the plan and
    the assignment — so the home is a second, explicit step, and `git worktree
    add` on its own leaves the agent writing the operator's global home:

    ```bash
    SKILLS="${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/skills/git-issue-workflow/scripts"

    git worktree add <declared-worktree> -b <declared-branch> "$commit_oid"
    "$SKILLS/bootstrap-home.sh" --root <declared-worktree>    # never skip this
    ```

    Teardown is one command in every case, because it resolves a ticket by
    searching rather than by the path convention:
    `"$SKILLS/wt" close <ticket>`. A repository that has never been given a home
    makes `bootstrap-home.sh` the *first* thing run in it, which is the same
    one-time per-repository step `wt new` prints as its `fix:` line elsewhere.
11. **Every epic states measurable goals; every ticket relates to one.** Ask the
    user what should be measurably better before scaffolding the workflow.
    Record each goal with its metric, harness command, baseline, and target;
    schedule terminal evaluation/perf/integration tickets that decide them; and
    give every other ticket an explicit contribution, expected effect, and local
    signal. The goal relation is the context a ticket agent aims at, so keep it
    specific. Read `references/goals-and-evaluation.md`.

## Preconditions

Use this workflow only in a repository already onboarded to both dependencies:

- `specs/program_model` is a complete accepted baseline with Internal and
  External views, adapter mappings, and append-only `specs/.history`.
- `test_graph/` exists and its affected graphs can be discovered.
- No unrelated desired/current workflow is active on the proposed epic branch.
- `gh` authentication and the repository/default branch have been verified.

If the spec baseline or Test Graph project is missing, stop and onboard through
`spec-double-compiler` and `test-graph`; epic kickoff is not onboarding.

Version 1 targets one ordinary Git repository. If `INTEGRATION.md` and
`integration.toml` identify an integration repository, stop rather than mixing
per-constituent fan-out with an unmerged epic branch.

## Scheduling model

Every planned ticket declares:

- stable spec ticket ID and GitHub issue URL;
- `depends_on` and `blocks`;
- a parallel wave;
- conflict keys for production, TLA+, adapters, Test Graph, and workflow data;
- a total `promotion_order` and `promotion_predecessor`;
- the immutable schedule revision and plan commit that produced the assignment;
- exact validation commands and evidence destinations;
- the epic goals it serves, with contribution kind, expected effect, and a
  local signal that predicts the final measurement.

A ticket is ready to **start** only when every dependency PR is merged into
`origin/epic/<slug>`. Tickets may share a wave only when neither reaches the
other in the dependency DAG and their conflict keys are disjoint. A ticket is
ready to **promote** only when its promotion predecessor is merged into the
epic branch and the ticket branch has reconciled against that latest tip.

Evaluation tickets are ordinary tickets whose slice is measurement. Each one
depends on every ticket contributing to the goals it owns and promotes after
them, so the harness runs on the integrated result rather than a partial one.

`depends_on` is planning metadata; `tla-spec-dev` does not enforce the DAG.
Validate missing references, self-dependencies, cycles, readiness, and conflict
keys before dispatch. Validate each issue assignment against its current
canonical plan entry before starting and again before promotion.

## Operating flow

### Start or resume an epic

1. Follow `references/plan-and-schedule.md`.
2. Ask the user what should be measurably better when the epic is done, before
   scaffolding the workflow. Turn the answers into goals with metrics,
   harnesses, baselines, and targets, and schedule the evaluation ticket(s)
   that decide them (`references/goals-and-evaluation.md`).
3. Use `git-issue` for discovery and issue authoring. For existing issues,
   preserve their bodies and replace only the marker-delimited epic assignment.
4. Agree the deferment policy with the user before dispatch and record it in
   the canonical plan (`references/deferment.md`).
5. Commit and push the epic branch before handing out any issue URL.
6. Report the epic branch/tip, workflow name, the goal table, and a table of
   issue URL, ticket ID, dependencies, wave, promotion predecessor, and goals
   served. Hand out only ready issue URLs. When recommending the next ticket,
   present pending deferred findings alongside it and triage them with the user.

### Work an epic issue

1. Read the issue before touching git. If it contains the epic assignment
   markers, follow `references/epic-ticket.md`; do not apply the ordinary
   default-branch closeout from `git-issue-workflow`.
2. Read the assignment's goal entries before implementing; the declared
   expected effect is the result the change is aiming at. Work and validate in
   the ticket worktree, run the declared local signal before close, and report
   it against the expected effect. Classify every failure case found in
   validation or review against the ticket's declared slice; defer, batch, or
   escalate out-of-scope findings under the epic's deferment policy rather than
   widening the ticket to fix them or to chase a metric.
3. Wait for the declared promotion predecessor, reconcile the latest epic tip,
   close only the assigned spec ticket with evidence, push, and open the PR
   against the epic branch.
4. Stop for external review. Treat the committed close record and evidence as
   sealed; a semantic review change becomes an explicit amendment ticket rather
   than an edit to append-only history.

### Finalize an epic

Follow `references/finalize.md`. Do not infer that “all agents are done” from
open PRs or local branches: verify every planned PR is merged into the epic
branch and every spec ticket has a close-history entry. Report every declared
goal as baseline → measured → target with a verdict; a missed goal is a decision
for the user, and a silently unmeasured goal is not an acceptable close.

## Boundaries

- Do not launch or monitor ticket agents. Return ready issue URLs; the user
  starts agents and invokes this skill again for status or finalization.
- Do not silently alter dependencies, ticket order, or conflict ownership after
  dispatch.
- Do not invent goals, targets, or baselines the user did not agree to, and do
  not edit a target so a measured result passes. Report the run that happened.
- Do not use `--accept-new` for ticket close or workflow finalization. Reconcile
  current and desired explicitly so validation proves the promoted state.
- Do not use closing keywords in ticket PRs. Use `Refs #<issue>` and reserve
  issue-closing references for the final epic PR.
- Do not bypass branch protection or external review gates.

## Reference map

| Task | Read |
| --- | --- |
| Create/resume branch, workflow, DAG, and issues | `references/plan-and-schedule.md` |
| Agree goals, baselines, and evaluation tickets | `references/goals-and-evaluation.md` |
| Author or execute the epic assignment | `references/epic-ticket.md` |
| Validate, promote, close, and open the epic PR | `references/finalize.md` |
| Classify, defer, batch, and triage failure cases | `references/deferment.md` |
