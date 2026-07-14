---
name: git-epic-workflow
description: >-
  Use when planning, starting, scheduling, resuming, or finalizing a multi-ticket
  Git epic on an epic/* branch backed by one shared spec-double-compiler workflow.
  Also use when a GitHub issue contains a git-epic-workflow assignment and must
  be implemented against an epic branch instead of the default branch. Composes
  git-issue issue authoring, git-issue-workflow ticket execution, tla-spec-dev
  ticket promotion, and Test Graph validation while allowing dependency-aware
  parallel work and serialized integration.
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

- **Plan and schedule:** create the epic branch, shared spec workflow, ticket
  DAG, issues, and handoff metadata. Read `references/plan-and-schedule.md` and
  `references/epic-ticket.md`.
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
- exact validation commands and evidence destinations.

A ticket is ready to **start** only when every dependency PR is merged into
`origin/epic/<slug>`. Tickets may share a wave only when neither reaches the
other in the dependency DAG and their conflict keys are disjoint. A ticket is
ready to **promote** only when its promotion predecessor is merged into the
epic branch and the ticket branch has reconciled against that latest tip.

`depends_on` is planning metadata; `tla-spec-dev` does not enforce the DAG.
Validate missing references, self-dependencies, cycles, readiness, and conflict
keys before dispatch. Validate each issue assignment against its current
canonical plan entry before starting and again before promotion.

## Operating flow

### Start or resume an epic

1. Follow `references/plan-and-schedule.md`.
2. Use `git-issue` for discovery and issue authoring. For existing issues,
   preserve their bodies and replace only the marker-delimited epic assignment.
3. Commit and push the epic branch before handing out any issue URL.
4. Report the epic branch/tip, workflow name, and a table of issue URL, ticket
   ID, dependencies, wave, and promotion predecessor. Hand out only ready issue
   URLs.

### Work an epic issue

1. Read the issue before touching git. If it contains the epic assignment
   markers, follow `references/epic-ticket.md`; do not apply the ordinary
   default-branch closeout from `git-issue-workflow`.
2. Work and validate in the ticket worktree.
3. Wait for the declared promotion predecessor, reconcile the latest epic tip,
   close only the assigned spec ticket with evidence, push, and open the PR
   against the epic branch.
4. Stop for external review. Treat the committed close record and evidence as
   sealed; a semantic review change becomes an explicit amendment ticket rather
   than an edit to append-only history.

### Finalize an epic

Follow `references/finalize.md`. Do not infer that “all agents are done” from
open PRs or local branches: verify every planned PR is merged into the epic
branch and every spec ticket has a close-history entry.

## Boundaries

- Do not launch or monitor ticket agents. Return ready issue URLs; the user
  starts agents and invokes this skill again for status or finalization.
- Do not silently alter dependencies, ticket order, or conflict ownership after
  dispatch.
- Do not use `--accept-new` for ticket close or workflow finalization. Reconcile
  current and desired explicitly so validation proves the promoted state.
- Do not use closing keywords in ticket PRs. Use `Refs #<issue>` and reserve
  issue-closing references for the final epic PR.
- Do not bypass branch protection or external review gates.

## Reference map

| Task | Read |
| --- | --- |
| Create/resume branch, workflow, DAG, and issues | `references/plan-and-schedule.md` |
| Author or execute the epic assignment | `references/epic-ticket.md` |
| Validate, promote, close, and open the epic PR | `references/finalize.md` |
