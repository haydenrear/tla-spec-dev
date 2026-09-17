---
name: git-epic-workflow
description: >-
  Use when planning, starting, scheduling, rescoping, retiring work from,
  resuming, or finalizing a multi-ticket Git epic on an epic/* branch backed by
  one shared spec-double-compiler workflow.
  Also use when a GitHub issue contains a git-epic-workflow assignment and must
  be implemented against an epic branch instead of the default branch. Agrees
  measurable epic goals with the user up front, relates every ticket to a final
  evaluation/perf/integration ticket that decides them, and composes git-issue
  issue authoring, git-issue-workflow ticket execution, tla-spec-dev ticket
  promotion, and Test Graph validation while allowing dependency-aware parallel
  work and serialized integration. Merges each wave into the epic branch itself
  and then stops at the wave boundary to hand the user a committed review
  artifact, a rendered diff, and a short walkthrough covering hot spots,
  decisions made implicitly, guardrails overridden, suspected bugs,
  architectural changes worth making to the epic's own machinery, and
  recommended next steps. Epic and ticket worktrees are branched by
  hand from the declared epic branch and then given their own per-checkout Skill
  Manager home with git-issue-workflow's `scripts/bootstrap-home.sh`; teardown
  is that skill's `scripts/wt close <ticket>`. A bare `git worktree add` with no
  home step leaves the ticket agent writing the operator's global home. The epic
  agent owns change management for those homes, reconciling each ticket's home
  into the project home at wave close, and sweeps every worktree it created in
  one pass once the epic's merge is verified, so the disk cost of an epic goes
  back to zero instead of onto the next one.
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
- **Integrate and review a wave:** merge the wave's ticket PRs into the epic
  branch in promotion order, reconcile each ticket worktree's Skill Manager home
  into the project home, then stop and hand the user the review artifact, the
  rendered diff, and the walkthrough. Read `references/human-review.md` and
  `references/worktree-lifecycle.md`.
- **Finalize:** validate the integrated epic, promote the accepted program
  model, close the shared spec workflow, open the epic PR, and — once its merge
  is verified — sweep every worktree the epic created. Read
  `references/finalize.md` and `references/worktree-lifecycle.md`.

## Load-bearing rules

1. **The plan is canonical.** Keep the complete schedule in
   `specs/desired_program_model/ticket_plan.yaml`. GitHub issues mirror it for
   handoff; they do not replace it.
2. **One epic, one branch, one workflow.** Create one `epic/<slug>` from the
   current default-branch tip and scaffold the spec workflow once. Give the
   workflow a unique stable name. Never force-push the epic branch.
3. **Dispatched identities are immutable, including retired work.** Do not
   delete, reorder, rename, or reuse a ticket ID after publishing issue
   assignments; delivery histories and retirement-receipt paths depend on the
   original zero-based plan ordinal and ID. Adding scope creates a new ticket.
   Removing scope preserves the original entry with `status: retired`, bumps
   `schedule_revision`, and records an explicit retirement receipt and affected
   goal disposition (`references/plan-and-schedule.md`).
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
7. **Ticket agents stop at PR open; the epic agent merges the wave.** A ticket
   agent stops after pushing a sealed branch and opening a PR whose base is the
   epic branch. It does not merge its own PR, merge to the default branch, or
   close the GitHub issue — it cannot see the wave, so it cannot know whether
   the promotion lane held or a sibling landed on the same file. The **epic
   agent** merges those PRs into `epic/<slug>` in promotion order, one at a
   time, without waiting for a human: the epic branch is an integration branch,
   the merge is reversible, and finalize.md §3 still gates everything before it
   reaches the default branch. A merge conflict is a stop, not a task — it means
   the ticket closed against a tree that no longer exists, so it goes back to
   its agent to reconcile. Read `references/human-review.md` §1.
8. **Only finalization closes the workflow.** After all delivered ticket PRs are
   on the epic branch and every retired ticket has its verified no-delivery
   receipt, the finalizer runs integrated validation, promotes the accepted
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

    **The epic agent owns that change management.** A ticket agent runs the
    read-only gate and reports its verdict; it never syncs into the project
    home, because that is one shared destination and a ticket agent cannot see
    the tickets it would be racing. The epic agent reconciles each worktree's
    home into `<main-working-tree>/.skill-manager` at wave close — serialized, one
    worktree at a time, reading `held-back` and `conflicted` as decisions rather
    than retries — and is responsible for every worktree being emptied of
    unmerged work before anything is deleted. Read
    `references/worktree-lifecycle.md`.

    **That home does not appear on its own.** The epic branch and every ticket
    worktree path are *declared* by the plan and the assignment — the one case
    the conventional front door's derived path cannot serve. In a home carrying
    the `skt` plugin, one command does the declared pair — worktree at the
    declared path, pinned to the resolved base, WITH its own home, rolled back
    together if the bootstrap fails:

    ```bash
    # skt lives in bin/cli of the home, NOT in skills/ -- it is a plugin.
    SKT="${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/bin/cli/skt"
    [ -x "$SKT" ] || SKT="$(command -v skt)"          # or on PATH
    "$SKT" ticket new <ticket> --base "$commit_oid" --path <declared-worktree>
    ```

    **Check for it at that path.** Measured twice by eval: an agent looked for
    `skt` under `skills/`, did not find it there because it is a plugin, and
    fell through to the hand-run pair below -- reading `wt` and
    `bootstrap-home.sh` and replaying their steps. Both runs had a working
    `skt` in `bin/cli` the whole time. `ls skills/` is the wrong question, and
    the answer to the right one is one `-x` test.

    It applies the index-base pinning conventions (clean slate, OIDs resolved
    once, create-only retention ref, branch from the pinned commit) and refuses
    a retention-ref conflict rather than repinning. Without skt, the same pair
    is two hand-run steps — and `git worktree add` on its own leaves the agent
    writing the operator's global home:

    ```bash
    SKILLS="$(for d in "${SKILL_MANAGER_HOME:-$HOME/.skill-manager}"/skills/git-issue-workflow "${SKILL_MANAGER_HOME:-$HOME/.skill-manager}"/plugins/*/skills/git-issue-workflow; do [ -d "$d" ] && { printf %s "$d"; break; }; done)/scripts"

    # ONE chained command, deliberately: the add alone produces a worktree
    # with NO home — the exact hazard measured live in the W2 eval.
    git worktree add <declared-worktree> -b <declared-branch> "$commit_oid" \
      && "$SKILLS/bootstrap-home.sh" --root <declared-worktree>
    ```

    Teardown is one command in every case, because it resolves a ticket by
    searching rather than by the path convention: `skt ticket close <ticket>`,
    or `"$SKILLS/wt" close <ticket>` where skt is absent. A repository that has
    never been given a home makes `bootstrap-home.sh` the *first* thing run in
    it, which is the same one-time per-repository step `wt new` prints as its
    `fix:` line elsewhere.

    **Reaching that by-hand pair is itself a finding — report it.** It is
    written for a home that genuinely has no `skt`, and it *works*, which is
    the whole problem: an agent that merely could not FIND the front door lands
    on it, produces a plausible worktree, and leaves no trace but four tool
    calls where one would have done. Measured four times across the eval suite,
    for four different reasons, and none of the four reported anything. So run
    the `-x` test above first. If it did not resolve, the by-hand pair is
    correct and there is nothing to report. If it resolved and you are on the
    by-hand pair anyway, say which of these you were in:

    - `skt` is installed but was not on `PATH`;
    - you looked where a plugin never is (`skills/`);
    - you found it and it **failed** — quote its `error:` line verbatim;
    - you found it and could not read the home it pointed at.

    All four are front-door defects, not facts about the repository. An epic
    agent has two places to put that line — the wave review artifact
    (`references/human-review.md`) for its own provisioning, and the ticket's
    PR body when a ticket agent reports it — and files it against the skill
    that owns the door: `git-epic-workflow` for the declared-path route above,
    `git-issue-workflow` for `wt`, `skt` for the plugin.
11. **The epic owns whether the homes are CURRENT, and checks before scheduling
    anything.** Every ticket worktree is a *copy* of the project home, and the
    project home is a copy of the root `~/.skill-manager`. Copies do not update
    themselves. So a skill fixed and merged yesterday is still absent from a
    home cloned the day before, and every ticket agent the epic deploys inherits
    that staleness — silently in a home without skt; with the skt plugin
    installed, the session hooks surface it, but the epic must not assume every
    home has them.

    The tool answers this now: `skt check` compares each change-managed unit's
    installed hash against its source's tip and names what is stale and the
    command that pulls it. (`home drift` answers "did anything change *in* this
    home" and exits 0 on a stale one; `home verify` answers "does everything in
    it *resolve*" — neither answers "is this home *current*", which is why the
    check exists.) The epic is still the last point where one check covers every
    ticket that follows, so BEFORE scheduling, run it in both tiers:

    ```bash
    skt check                                     # in the root home
    SKILL_MANAGER_HOME=<repo>/.skill-manager skt check    # and the project home
    ```

    Where skt is not installed, the same comparison by hand:

    ```bash
    for f in "${SKILL_MANAGER_HOME:-$HOME/.skill-manager}"/installed/*.json; do
      n=$(basename "$f" .json); case "$n" in *.projections) continue;; esac
      python3 -c "import json;d=json.load(open('$f'));print('$n', (d.get('gitHash') or 'none')[:8])"
    done
    ```

    Any unit behind its merged source gets `skt sync <unit>` (or `skill-manager
    sync <unit>`) in the root home **and** in the project home before the first
    ticket is scheduled —
    not after, because a worktree cloned from a stale project home carries the
    staleness into work you will then have to redo. Sync in dependency order:
    a unit whose `skill-imports` name a file added by another unit fails
    validation with exit 11 if that other unit has not been synced yet, and the
    violation is an artifact of the order, not a real one.

    If the repository has other checkouts with their own homes, they are stale
    too and no command fans out to them. Say so in the epic's kickoff notes
    rather than letting a ticket agent discover it.

    **"Current" is about unit bytes, not derived artifacts, and do not conflate
    the two.** A ticket home *inherits* the artifacts its parent holds and
    *declares* the rest, so `skill-manager artifacts stale` reporting a nonzero
    count in a fresh clone is not staleness this rule is about, and scheduling a
    rebuild for it wastes every ticket's provisioning. The contract — including
    when `skill-manager build <id>` is the right move, and the two wrong
    diagnoses that have already been reached by reading the source instead — is
    stated once at
    `${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/plugins/skt/skills/skt/references/derived-artifacts.md`
    -- which is absent in a home that does not have the skt plugin installed,
    **including, very likely, the project home you are standing in**. When it is
    not there: the page is `skills/skt/references/derived-artifacts.md` in
    `github.com/haydenrear/skill-publisher-skill`, and `skill-manager install
    github:haydenrear/skill-publisher-skill` puts it in the home. Point ticket
    agents at it, and do not paraphrase it into an epic's kickoff notes -- but do
    not leave an agent with a dead link and a prohibition either, which is what
    this paragraph did before the fallback was named.
12. **Every epic states measurable goals; every ticket relates to one.** Ask the
    user what should be measurably better before scaffolding the workflow.
    Record each goal with its metric, harness command, baseline, and target;
    schedule terminal evaluation/perf/integration tickets that decide them; and
    give every other ticket an explicit contribution, expected effect, and local
    signal. The goal relation is the context a ticket agent aims at, so keep it
    specific. Read `references/goals-and-evaluation.md`.
13. **Every wave boundary produces a review, and by default it is a gate.**
    After merging a wave and before handing out any issue URL from the next one,
    write a committed review artifact and walk the user through it: hot spots in
    what landed, decisions made implicitly and guardrails overridden, where the
    bugs probably are, architectural changes worth making — including to the
    epic's own machinery, which lives in gitignored homes and reaches nothing by
    being merged — and the recommended next steps read together with the
    deferred-findings backlog. Then stop and wait. The user may change the
    cadence, drop the gate, or take the merges back; that answer is recorded as
    `review_policy` in the canonical plan, because at finalization a review
    nobody chose to skip is indistinguishable from one that never happened.
    Read `references/human-review.md`.
14. **Worktrees stand until the epic ends, then all of them go in one sweep.**
    Keep every ticket worktree through review — that is what makes the review
    model work — and then remove all of them in one deliberate pass once the
    default-branch merge is verified. The two clocks are deliberate and
    opposite: unit state merges **early**, at wave close, while its author is
    reachable; worktrees are deleted **late**, together. Removal must never be
    the step that carries the merge, because `git worktree remove` deletes a
    gitignored home without asking and succeeds just as quietly whether it held
    a week of skill edits or nothing. Size the disk cost honestly: a home is
    cloned copy-on-write, so a new worktree is nearly free (measured here, 33.7
    MB real for a home `du` calls 1.1 GB), and the real space goes to per-home
    venvs, tools, and divergence as work happens in it. Measure the sweep with
    free space, never with `du`. The epic is not finished while a worktree it
    created is still standing without a recorded reason. Read
    `references/worktree-lifecycle.md`.

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
`origin/epic/<slug>` and the review gate on the preceding wave has been answered
(`references/human-review.md` §2). Tickets may share a wave only when neither
reaches the other in the dependency DAG and their conflict keys are disjoint. A ticket is
ready to **promote** only when its promotion predecessor is merged into the
epic branch and the ticket branch has reconciled against that latest tip.

A `retired` ticket remains at its original ordinal as append-only planning
history but is absent from the active dependency, conflict, and promotion
graphs. No undelivered non-retired ticket may depend on, block, or name it as
promotion predecessor. A delivered ticket retains its sealed historical edges,
including edges to a ticket retired by a later amendment; new work skips the
retired entry. `retired` means the owner deliberately removed the work; it is
not synonymous with `done`, and `carried`, `superseded`, or `abandoned` belong
in `retirement.resolution`, never directly in `status`.

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
   the canonical plan (`references/deferment.md`). In the same conversation,
   agree the review cadence, whether the wave review gates the next wave, and
   who merges ticket PRs into the epic branch; record that as `review_policy`
   (`references/human-review.md` §2).
5. Validate every rendered assignment before handing out its issue URL, against
   the issue body as GitHub now holds it:
   `uv run --script "<skill base directory>/scripts/validate_assignment.py" --assignment <issue-body.md> --expect-ticket <id> --expect-epic-branch epic/<slug>`
   (or pipe `gh issue view <n> --json body -q .body` into it). The skill base
   directory is printed as `Base directory for this skill:` when the skill
   loads — use it, don't search for the scripts. The scripts declare their own
   dependencies: run them with `uv run --script`, never `python3` (which lacks
   PyYAML). `validate_assignment.py` reads `--assignment <file>` or stdin,
   never a positional path; `validate_epic_plan.py` takes the plan path
   positionally. Both take the same three flags, so there is nothing to find in
   `--help` or the source: `--force` (exit 0 past blocking errors, same as
   `SKILL_GATES=off`), `--strict` (every rule is an error), `--verbose` (list
   every warning). The schema is
   specified here, rendered by `git-issue`, and parsed by `git-issue-workflow`,
   so a `pr_base` that is not the epic branch fails here and an omitted policy
   block or placeholder shows up as a short warning. Only wrong-branch,
   wrong-ticket, and missing-location errors block; `--force` (or
   `SKILL_GATES=off`) passes those too when you have decided they do not apply.
   Never rewrite a plan or re-scope a ticket just to silence a warning.
6. Commit and push the epic branch before handing out any issue URL.
7. Report the epic branch/tip, workflow name, the goal table, and a table of
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
4. Stop at PR open. Treat the committed close record and evidence as sealed; a
   semantic review change becomes an explicit amendment ticket rather than an
   edit to append-only history.

### Integrate and review a wave

1. Merge the wave's ticket PRs into `epic/<slug>` in promotion order, one at a
   time, verifying checks and assignment/plan equality before each merge. Stop
   and return the ticket to its agent on a conflict, a failing REQUIRED matrix
   entry, or a pending blocking finding.
2. Reconcile each ticket worktree's Skill Manager home into the project home,
   one worktree at a time, and check every worktree for uncommitted, stashed,
   unpushed, or epic-unmerged work. Update the worktree ledger
   (`references/worktree-lifecycle.md` §3–§4). Leave the worktrees standing.
3. Build the review artifact over the whole wave range and commit it under the
   plan's `review_policy.artifact_root`, with the diff stat, the patch, the
   merge record, and the ledger beside it.
4. Render the diff visualization and walk the user through it quickly — what the
   wave was for, the design decisions, the intuition, where the bugs probably
   are, what was decided for them, and the ask.
5. Wait for the user's answer unless the plan waived the gate, then record that
   answer in the artifact and dispatch the next wave — amended if the review
   changed the plan. Read `references/human-review.md`.

### Finalize an epic

Follow `references/finalize.md`. Do not infer that “all agents are done” from
open PRs or local branches: verify each delivered ticket's merged PR and
close-history entry separately from each retired ticket's canonical retirement
receipt. A PR/history cannot substitute for a retirement receipt, and a receipt
cannot be presented as delivered work. Report every declared goal as baseline
→ measured → target with a verdict or its explicit retirement disposition; a
missed goal is a decision for the user, and a silently unmeasured goal is not an
acceptable close.

## Boundaries

- Do not launch or monitor ticket agents. Return ready issue URLs; the user
  starts agents and invokes this skill again for status or finalization.
- Do not silently alter dependencies, ticket order, or conflict ownership after
  dispatch.
- Do not delete an unwanted dispatched ticket or mark it `carried`,
  `superseded`, or `abandoned` as though those were delivery statuses. Retire it
  through the canonical plan amendment and receipt flow.
- Do not invent goals, targets, or baselines the user did not agree to, and do
  not edit a target so a measured result passes. Report the run that happened.
- Do not use `--accept-new` for ticket close or workflow finalization. Reconcile
  current and desired explicitly so validation proves the promoted state.
- Do not use closing keywords in ticket PRs. Use `Refs #<issue>` and reserve
  issue-closing references for the final epic PR.
- Do not bypass branch protection or external review gates. Merging a ticket PR
  into the epic branch is the epic agent's job; merging the epic PR into the
  default branch is the user's, and needs their explicit authorization.
- Do not dispatch the next wave before the review the plan's `review_policy`
  declares, and do not treat silence as approval.
- Do not fix on the epic branch what a review surfaces, and do not implement the
  architectural changes a review recommends. Both re-enter as tickets.
- Do not remove a worktree before the epic's default-branch merge is verified,
  and do not remove one whose home has not been reconciled or whose tree still
  holds uncommitted, stashed, unpushed, or epic-unmerged work. Never `rm -rf` a
  worktree, and never reach for `wt close --force` to finish faster.
- Do not leave the sweep undone. An epic that skips it has moved its disk cost
  onto the next epic, which is the one that will run out of space.

## Reference map

| Task | Read |
| --- | --- |
| Create/resume branch, workflow, DAG, and issues | `references/plan-and-schedule.md` |
| Agree goals, baselines, and evaluation tickets | `references/goals-and-evaluation.md` |
| Author or execute the epic assignment | `references/epic-ticket.md` |
| Merge a wave, build the review artifact, walk the user through it | `references/human-review.md` |
| Reconcile ticket homes, keep the ledger, sweep the worktrees | `references/worktree-lifecycle.md` |
| Validate, promote, close, and open the epic PR | `references/finalize.md` |
| Classify, defer, batch, and triage failure cases | `references/deferment.md` |
| Deciding whether a ticket home's `declared-only` artifacts need rebuilding | `${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/plugins/skt/skills/skt/references/derived-artifacts.md` — skt owns it; this skill does not restate it, and it is absent in a home without skt |

**One word, two meanings — do not confuse them.** In *this* skill "artifact"
almost always means the **wave review artifact** under `review.artifact_root`,
which a human reads. A **derived artifact** is a thing a Skill Manager home
produced — a CLI shim, a venv, a projection — and it is the skt page above.
Nothing in the review artifact's lifecycle is affected by `artifacts list`, and
"rebuild the artifact" is never an instruction this skill gives.
