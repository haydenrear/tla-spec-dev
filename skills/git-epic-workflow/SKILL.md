---
name: git-epic-workflow
description: >-
  Use when planning, starting, scheduling, rescoping, retiring work from,
  resuming or finalizing a multi-ticket Git epic on an `epic/*` branch backed by
  one shared spec-double-compiler workflow, and when a GitHub issue carries a
  `git-epic-workflow:assignment` block to implement against an epic branch rather
  than the default branch. Trigger on "plan an epic", "dispatch the next wave",
  "merge this wave", "retire a ticket", "finalize the epic", or an issue
  containing the assignment marker.
skill-imports:
  - unit: tla-spec-dev
    path: skills/git-issue/SKILL.md
    reason: Epic issues retain the discovery, references, spec decision, and validation work-order structure authored by git-issue.
  - unit: tla-spec-dev
    path: skills/git-issue-workflow/SKILL.md
    reason: Ticket agents execute epic assignments through the implementer workflow with the epic overrides defined here.
  - unit: tla-spec-dev
    path: skills/spec-double-2/references/spec_evolution.md
    reason: Defines ticket-local current/desired state, append-only ticket close history, promotion, and whole-workflow closeout.
  - unit: tla-spec-dev
    path: skills/test-graph/references/workflows.md
    reason: Defines graph discovery, execution, evidence, and the smart failure loop used by every ticket and by epic finalization.
  - unit: skt
    path: skills/skill-manager/references/workflows.md
    reason: Defines how installed dependent skills and their managed tools are resolved at runtime.
---

# git-epic-workflow

Coordinate several GitHub issues through one `epic/<slug>` branch and one shared
desired/current TLA+ workflow. The epic branch is the integration branch; ticket
branches start from it and target it. The default branch changes only through the
final epic PR.

Four roles, each with its page: **plan and schedule**
(`references/plan-and-schedule.md`, `references/goals-and-evaluation.md`),
**perform one ticket** (`references/epic-ticket.md`, read before creating a
worktree), **integrate and review a wave** (`references/human-review.md`,
`references/worktree-lifecycle.md`), and **finalize** (`references/finalize.md`).

## Load-bearing rules

Each rule is the instruction. Where the reasoning is long it lives on the page
the rule names — moved, not dropped.

1. **The plan is canonical.** The complete schedule lives in
   `specs/desired_program_model/ticket_plan.yaml`. Issues mirror it; they never
   replace it.
2. **One epic, one branch, one workflow.** Create one `epic/<slug>` from the
   current default-branch tip; scaffold the workflow once under a unique stable
   name. Never force-push the epic branch.
3. **Dispatched identities are immutable, including retired work.** Never delete,
   reorder, rename or reuse a ticket ID after publishing assignments — delivery
   histories and retirement-receipt paths depend on the original zero-based
   ordinal and ID. Adding scope creates a new ticket; removing scope keeps the
   entry with `status: retired`, bumps `schedule_revision`, and records a
   retirement receipt and goal disposition.
4. **The epic assignment wins.** Its marker-delimited block overrides ordinary
   `git-issue` instructions that branch from or merge to the default branch.
5. **The epic agent owns the model; ticket agents move `current` toward it.**
   Before dispatch it scaffolds each ticket's `desired` and `current`, validates
   them, and runs TLC. At wave merge it closes and promotes the spec ticket,
   applies the model delta, and places every attribution anchor.

   A ticket agent **does not run** `open ticket`, `close ticket`,
   `close_tickets.py`, or `--accept-new`. It moves ticket-local `current` toward
   `desired`, runs the spec tests its assignment names, and records evidence. A
   **small** correction to `desired` is the ticket's; a **structural** change
   comes back in the PR body. A small correction is a debt the epic agent then
   owes `specs/current`, `program_model` and `desired_program_model`
   (`references/epic-ticket.md` §3). Record the reversal in the plan as
   `planning_rules.model_ownership_rule` and restate it in every assignment.
6. **Parallel work; serialized promotion.** `depends_on` controls when work may
   start; a separate total `promotion_predecessor` order controls when a ticket
   may rebase onto the epic tip, close/promote, and enter the branch. Promotion
   order must be a topological extension of `depends_on`, and two promotions
   never integrate concurrently.
7. **Ticket agents stop at PR open; the epic agent merges the wave.** A ticket
   agent stops after pushing a sealed branch and opening a PR based on the epic
   branch — it does not merge its own PR, merge to the default branch, or close
   the issue, because it cannot see the wave. The epic agent merges in promotion
   order, one at a time, without waiting for a human. A merge conflict is a stop,
   not a task: it goes back to its agent, mechanical conflicts included.
8. **Only finalization closes the workflow.** After every delivered ticket PR is
   on the epic branch and every retired ticket has its verified no-delivery
   receipt, the finalizer runs integrated validation, promotes the accepted
   model, closes the workflow, and opens the epic PR.
9. **Out-of-scope findings are deferred, not chased.** Agree a deferment policy
   when the branch is created; ticket agents append out-of-scope failures to the
   backlog rather than widening scope (`references/deferment.md`).
10. **A ticket's Skill Manager home is not carried by its PR.** Every worktree has
    its own gitignored `<worktree>/.skill-manager`; nothing inside it appears in
    any PR. It reaches the tier above only through `skill-manager home sync`, and
    the unit's own repository only through `skill-manager unit publish`. An epic
    cannot finalize until every worktree has been through `skill-manager home
    close-out`. **The epic agent owns that change management**: a ticket agent
    runs the read-only gate and reports its verdict, never syncing into the
    project home; the epic agent reconciles each home at wave close, serialized.

    The declared worktree+home pair is one command — `skt ticket new <ticket>
    --base "$commit_oid" --path <declared-worktree>`. **Test the resulting path,
    not the exit code**: it has rolled a worktree back and still exited 0.
    Reaching the by-hand pair when `skt` resolved is itself a finding — name
    which of five cases you were in and file it against the skill owning the
    door (`references/worktree-lifecycle.md` § *The front door*).
11. **The epic owns whether the homes are CURRENT, and checks before scheduling.**
    Every worktree home is a copy of the project home, which is a copy of the
    root; copies do not update themselves. Before scheduling, run `skt check` in
    the root home **and** with `SKILL_MANAGER_HOME=<repo>/.skill-manager` in the
    project home, and sync anything behind its merged source, in dependency
    order — a worktree cloned from a stale project home carries the staleness
    into work you then redo. Other checkouts with their own homes are stale too
    and nothing fans out to them; say so in the kickoff notes. "Current" is about
    unit bytes, not derived artifacts: do not schedule rebuilds for a fresh
    home's `artifacts stale` count (`references/plan-and-schedule.md` §2).
12. **Every epic states measurable goals; every ticket relates to one.** Ask the
    user what should be measurably better before scaffolding. Record each goal
    with metric, harness, baseline and target; schedule the terminal evaluation
    tickets that decide them; give every other ticket a contribution, expected
    effect and local signal (`references/goals-and-evaluation.md`).
13. **Every wave boundary produces a review, and by default it is a gate.** After
    merging a wave and before handing out any issue URL from the next, commit a
    review artifact and walk the user through it, then stop and wait. Its fourth
    section carries **five named blocks** — model delta applied, anchors placed,
    the improvement-card row, every proposed skill change applied or declined,
    and the model corrections merged tickets still owe. Write each even when the
    answer is `none`; `none` is a claim and an absent block is not one. The user
    may change the cadence or drop the gate; record that as `review_policy`.
14. **Worktrees stand until the epic ends, then all go in one sweep.** Keep every
    ticket worktree through review; remove them all in one pass once the
    default-branch merge is verified. Unit state merges **early**, at wave close;
    worktrees are deleted **late**, together. Removal must never be the step that
    carries the merge. Measure the sweep with free space, never `du`. The epic is
    not finished while a worktree it created stands without a recorded reason.

## Preconditions

Use this workflow only in a repository onboarded to both dependencies:
`specs/program_model` is a complete accepted baseline with Internal and External
views, adapter mappings and append-only `specs/.history`; `test_graph/` exists
and its affected graphs can be discovered; no unrelated workflow is active on the
proposed branch; `gh` auth and the default branch are verified. If a baseline is
missing, stop and onboard through `spec-double-compiler` and `test-graph` — epic
kickoff is not onboarding. If `INTEGRATION.md` and `integration.toml` identify an
integration repository, stop.

## Scheduling model

What every planned ticket declares — IDs, `depends_on`/`blocks`, wave, conflict
keys, `promotion_order` and `promotion_predecessor`, schedule revision and plan
commit, validation commands, evidence destinations and goals — and the retirement
semantics are `references/plan-and-schedule.md`.

A ticket may **start** only when every dependency PR is merged into
`origin/epic/<slug>` and the preceding wave's review gate is answered. Tickets
share a wave only when neither reaches the other in the DAG and their conflict
keys are disjoint. A ticket may **promote** only when its promotion predecessor
is merged and its branch has reconciled against that tip. Evaluation tickets are
ordinary tickets whose slice is measurement, depending on every ticket
contributing to the goals they own.

`depends_on` is planning metadata and `tla-spec-dev` does not enforce the DAG:
validate missing references, self-dependencies, cycles, readiness and conflict
keys before dispatch, and validate each assignment against its plan entry before
starting and again before promotion.

## Operating flow

- **Start or resume:** `references/plan-and-schedule.md`. Agree goals before
  scaffolding, author issues through `git-issue`, agree and record the deferment
  policy and review cadence, validate every rendered assignment with
  `scripts/validate_assignment.py` before handing out its URL, and push the epic
  branch first. Run those scripts with `uv run --script`, never `python3`.
- **Work an epic issue:** read the issue before touching git; on the markers
  follow `references/epic-ticket.md`. Read the goals before implementing, run the
  local signal before close, wait for the promotion predecessor, reconcile the
  epic tip, open the PR, stop.
- **Integrate and review a wave:** merge in promotion order, reconcile each home,
  update the ledger, commit the review artifact, render the diff, walk the user
  through it, wait (`references/human-review.md`).
- **Finalize:** `references/finalize.md`. Verify each delivered ticket's merged PR
  and close-history entry separately from each retired ticket's receipt; never
  infer completion from open PRs or local branches. Report every goal as baseline
  → measured → target with a verdict or retirement disposition. A silently
  unmeasured goal is not an acceptable close.

## Boundaries

- Do not launch or monitor ticket agents. Return ready issue URLs.
- Do not silently alter dependencies, ticket order or conflict ownership after
  dispatch, and do not delete a dispatched ticket or mark it `carried`,
  `superseded` or `abandoned` as though those were delivery statuses.
- Do not invent goals, targets or baselines the user did not agree to, and never
  edit a target so a measured result passes. Report the run that happened.
- Do not use `--accept-new` for ticket close or workflow finalization.
- Do not use closing keywords in ticket PRs. Use `Refs #<issue>`.
- Do not bypass branch protection or external review gates. Merging the epic PR
  into the default branch is the user's, and needs explicit authorization.
- Do not dispatch the next wave before the review `review_policy` declares, and
  do not treat silence as approval.
- Do not fix on the epic branch what a review surfaces, or implement the
  architectural changes it recommends. Both re-enter as tickets.
- Do not remove a worktree before the default-branch merge is verified, or one
  whose home is unreconciled or whose tree still holds uncommitted, stashed,
  unpushed or epic-unmerged work. Never `rm -rf` a worktree, never reach for
  `wt close --force` to finish faster, and do not leave the sweep undone.

## Reference map

| Task | Read |
| --- | --- |
| Create/resume branch, workflow, DAG, issues; what a ticket declares; home staleness; retirement | `references/plan-and-schedule.md` |
| Agree goals, baselines, and evaluation tickets | `references/goals-and-evaluation.md` |
| Author or execute the epic assignment; the model-ownership debt | `references/epic-ticket.md` |
| Merge a wave, build the review artifact, walk the user through it | `references/human-review.md` |
| The front door and its five miss cases; reconcile homes; ledger; sweep; what "artifact" means here | `references/worktree-lifecycle.md` |
| Validate, promote, close, and open the epic PR | `references/finalize.md` |
| Classify, defer, batch, and triage failure cases | `references/deferment.md` |
| Whether a ticket home's `declared-only` artifacts need rebuilding | the skt plugin's `skills/skt/references/derived-artifacts.md` — absent in a home without skt; `references/plan-and-schedule.md` §2 names the fallback |
