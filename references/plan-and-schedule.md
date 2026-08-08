# Plan and schedule an epic

Use this reference when creating a new epic or reconciling a partially planned
one. Discovery and issue content still follow `git-issue`; this reference adds
the shared branch, spec workflow, and schedule.

## 1. Preflight

Confirm all of these before writing:

```bash
gh auth status
gh repo view --json nameWithOwner,defaultBranchRef
git status --short --branch
git fetch origin
ls specs/program_model specs/.history test_graph
```

Inspect `specs/program_model/spec_manifest.yaml`, both TLA+ views, action and
adapter mappings, active spec directories, the existing graph plans, and the
latest relevant history. Stop if the baseline is incomplete or an unrelated
`specs/current` / `specs/desired_program_model` workflow is active on the branch
lineage.

For a resumed epic, first read its remote branch, ticket plan, assignment blocks,
and ticket PRs. Reconcile those artifacts instead of scaffolding again.

## 2. Create the epic integration branch

### Worktree provisioning conventions (index-base pinning)

Every worktree this skill creates — the epic worktree here and every ticket
worktree in `epic-ticket.md` — follows these conventions so its base is
immutable and reproducible (index platforms such as commit-diff-context
snapshot branching consume these OIDs as base-snapshot identity):

1. **Clean slate** — `git status --porcelain` empty before provisioning;
   stop and reconcile otherwise.
2. **Resolve the base rev to object IDs once** — capture
   `commit_oid=$(git rev-parse <base-ref>)` and
   `tree_oid=$(git rev-parse "<base-ref>^{tree}")`; record them; never
   re-resolve the branch name afterwards.
3. **Retention ref** — create-only
   `git update-ref refs/index-bases/<repo-id>/<tree_oid> <commit_oid> ""`;
   an existing ref pointing at a different commit is a hard error. Reserved
   namespace, never public tags.
4. **Branch from the pinned commit**, not from the moving ref name.

Choose a short stable slug and create a dedicated epic worktree from the fetched
default-branch tip:

In a home carrying the `skt` plugin, one command applies every convention below
— clean-slate check, OIDs resolved once, create-only retention ref, branch from
the pinned commit — and gives the worktree its own home in the same breath,
rolling both back if the bootstrap fails:

```bash
git fetch origin
skt ticket new epic-<slug> --base origin/<default-branch> --path ../wt-epic-<slug>
cd ../wt-epic-<slug>
```

(The branch it creates is `feature/epic-<slug>`; rename with `git branch -m
epic/<slug>` if the plan declares the bare epic name, or pass the resolved
`commit_oid` as `--base`.) Without skt, the same conventions by hand:

```bash
git fetch origin
test -z "$(git status --porcelain)" || { echo "dirty tree — reconcile first"; exit 1; }
commit_oid=$(git rev-parse origin/<default-branch>)
tree_oid=$(git rev-parse "origin/<default-branch>^{tree}")
git update-ref "refs/index-bases/$(basename "$(git rev-parse --show-toplevel)")/${tree_oid}" "$commit_oid" ""
git worktree add ../wt-epic-<slug> -b epic/<slug> "$commit_oid"
cd ../wt-epic-<slug>
```

Record the starting SHA (`commit_oid`). Never create ticket branches from the
primary checkout or from the default branch once the epic exists. Never
force-push `epic/<slug>`.

### Skill Manager homes: what an epic is actually fanning out

An epic is the first place the three-tier home model becomes a *scheduling*
concern, so decide it here rather than discovering it at finalization.

```
root       ~/.skill-manager              where the operator installs
   |  copy
project    <repo>/.skill-manager         ONE per repository — the shared destination
   |  copy                               for every worktree below
worktree   <worktree>/.skill-manager     one per ticket, and one for the epic worktree
```

Each tier is a **real copy, not a symlink**, and that is the load-bearing part for
you: an epic runs several ticket agents at once, and a symlink farm would make
their homes one shared object, so two agents editing "their" copy of a skill would
be editing each other's, last writer winning silently. Copies buy you the
parallelism the whole scheduling model assumes.

Give the epic worktree its own home before running anything that installs, syncs,
binds, or resolves — those all write into whatever `SKILL_MANAGER_HOME` names, and
before the local home exists that is the operator's global home:

```bash
# the skt path above already did this; by hand it is:
"${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/skills/git-issue-workflow/scripts/bootstrap-home.sh" \
  --root ../wt-epic-<slug>
```

That path is the resolution, not a placeholder: an installed unit's files live at
`$SKILL_MANAGER_HOME/skills/<unit>/`, and the `:-` fallback makes the same line
work from a bare shell. If this repository has never been given a home of its own,
this is also the command that gives it one — run it with `--root <repo-root>`
first, once, then again for the worktree.

Then note two things about the schedule you are about to write:

- **`conflict_keys` do not cover units in a home.** They partition *tracked files*
  — production, TLA, adapters, test_graph, workflow. A skill unit lives in a home,
  which is gitignored, so two tickets in the same wave can have perfectly disjoint
  conflict keys and still both improve `test-graph` in their own homes. Neither
  edit is in either PR. Both will later try to reconcile into the one project home,
  and the second one is **held back and reported** rather than overwritten — a
  conflict a human resolves, not a silent loss. That is the designed outcome, but
  it is work you scheduled without meaning to. If you expect a wave to touch the
  same unit, say so in the assignment and have one ticket own it.
- **Publishing beats chaining.** `home sync` only moves an edit up one tier. An
  improvement that should reach other repositories has to go to the unit's own
  git repo via `skill-manager unit publish`; a chain-only route would need the same
  merge performed twice and would still never reach a sibling project.

## 3. Discover the whole change

Use the `git-issue` discovery sequence once for the epic and then refine it per
ticket. Identify:

- target program state, Internal/External actions, variables, and invariants;
- production paths and symbols;
- spec-unit adapters and conformance tests;
- Test Graph bindings, node IDs, composition, and context keys;
- acceptance commands and evidence paths;
- true ordering dependencies and potential write conflicts.

The desired model describes the final whole-program state. A ticket desired
model later describes the whole-program state after that ticket, not a feature
fragment.

While discovering, inventory what already measures this program: benchmark
scripts, eval datasets and scorers, perf-marked test suites, end-to-end Test
Graph graphs, and any dashboards or saved baselines. That inventory is the raw
material for the goals agreed in step 3a — goals are cheapest when an existing
harness already decides them.

## 3a. Agree the epic goals

Before scaffolding the workflow, ask the user what should be measurably better
when the epic is done. This is a required decision, like the deferment policy;
do not infer goals from the codebase and do not default them.

Ask for each outcome: the metric, the command that measures it, today's value,
and the threshold that counts as success. Then:

- write each answer as a goal in the schema from `goals-and-evaluation.md`;
- measure the baseline now, on the fresh epic branch, whenever the harness
  already exists, and commit it under the epic evidence root;
- schedule a wave-1 harness+baseline ticket when it does not;
- schedule the terminal evaluation ticket(s) that run the harnesses on the
  integrated epic and decide each goal;
- give every other ticket a goal relation — contribution kind, expected effect,
  and a local signal it can run in its own worktree.

If the user has no measurable outcome, record `epic_goals: []` with a
`goals_waived` reason rather than inventing a metric. Read
`references/goals-and-evaluation.md` for goal kinds, baselines, contribution
kinds, the evaluation-ticket contract, and reporting.

## 4. Scaffold the shared workflow once

Choose stable ticket IDs before scaffolding. Use the first ticket only as the
CLI seed:

```bash
tla-spec-dev --spec-root specs scaffold workflow <first-ticket-id> "<epic title>"
```

Then replace the placeholder planning data with the complete epic:

- set a unique workflow `name` / `status.workflow` derived from the epic slug;
- make `specs/current` the complete accepted starting model;
- author `specs/desired_program_model` as the complete target model;
- expand `ticket_plan.yaml` to every stable ticket;
- add an integer `schedule_revision` that changes whenever IDs, dependency
  edges, waves, promotion order, conflict ownership, or validation scope changes;
- add the `epic_goals` block agreed in step 3a;
- add the `deferment_policy` block agreed in step 4a;
- remove placeholder actions, scopes, commands, and assertions.

Do not run `open ticket` on the epic branch. Each ticket agent opens exactly its
own workspace on its ticket branch.

Keep the generated ticket schema and add these scheduling fields to each ticket:

```yaml
github_issue: "https://github.com/<owner>/<repo>/issues/<number>"
schedule_revision: 1
depends_on: []
blocks: []
wave: 1
promotion_order: 10
promotion_predecessor: null
role: implementation          # implementation | evaluation
conflict_keys:
  production: []
  tla: []
  adapters: []
  test_graph: []
  workflow: []
goals:
  - goal: "<goal-id>"
    contribution: direct      # direct | enabling | guard
    expected_effect: "<direction and magnitude, or 'none — enabling only'>"
    local_signal: "<cheap in-worktree command, or 'N/A: reason'>"
```

Evaluation tickets add `role: evaluation` and `owns_goals: ["<goal-id>"]`, and
depend on every ticket contributing to the goals they own.

## 4a. Agree the deferment policy

Before any issue is dispatched, ask the user how ticket agents must handle
failure cases they find outside their assigned slice. This is a required
decision, not a default to assume silently — unbounded in-ticket bug fixing is
the main way epic tickets lose their semantic boundary.

Ask one question with the concrete tradeoff:

> Ticket agents will find real defects outside their assigned slice. How should
> they handle them?
>
> - **batch** (recommended) — record to the backlog, keep working the assigned
>   slice, triage between waves and at finalization;
> - **ask** — record, then stop and ask you per finding whether to open a ticket
>   now or batch it;
> - **inline** — allowed to fix within their own conflict keys, still recorded.
>
> Blocking findings (the ticket's REQUIRED validation cannot pass without
> touching another surface) **escalate** to you by default; say so if you would
> rather be asked to authorize an inline fix instead.

Record the answer, a per-ticket deferral `budget`, and the backlog path in
`ticket_plan.yaml` using the schema in `deferment.md`. Create the empty backlog
file in the same commit:

```yaml
findings: []
```

Read `references/deferment.md` for scope classification, entry format, agent
behavior, and triage.

## 5. Validate the schedule

Treat `depends_on` as a directed graph and reject the plan unless:

- every referenced ticket exists and no ticket depends on itself;
- a topological ordering includes every ticket;
- `blocks` is the reverse of `depends_on`;
- tickets in the same wave have no dependency path between them;
- every dependency is in an earlier wave;
- tickets in the same wave have disjoint conflict keys;
- every ticket has an exact validation matrix or an explicit `N/A` reason;
- `promotion_order` is unique and total;
- promotion order is a topological extension of `depends_on`;
- each `promotion_predecessor` names the preceding ticket in that total order;
- every ticket relates to at least one declared goal, every goal has a
  contributing ticket, and each goal's evaluation ticket both depends on and
  promotes after every contributor.

Run the bundled validator before dispatch and whenever the schedule changes:

```bash
uv run <git-epic-workflow-skill>/scripts/validate_epic_plan.py \
  specs/desired_program_model/ticket_plan.yaml
```

The validator prints `WARNING:` lines and still exits 0 for a missing or waived
goal set, a missing evaluation ticket, an `unmeasured` baseline, or a `direct`
contribution with no local signal. Treat those as prompts to go back to the
user, not as noise. Inconsistencies inside a declared goal set are errors and
exit non-zero.

The total promotion order is an integration lane, not an implementation
dependency. Agents in one wave may implement and validate concurrently, but
only the next ticket in that lane may reconcile, close/promote, and enter the
epic branch.

Prefer an amendment/reconciliation ticket over assigning shared workflow-wide
metadata to a parallel ticket. Ticket agents own their plan entry and declared
semantic slice; the epic owner owns ticket order, dependency edges, and
workflow-wide status.

## 6. Create or schedule GitHub issues

Every scheduled issue maps to one spec ticket and retains the standard
`git-issue` sections: Summary, References, Discovery notes, Worktree & branch,
Spec workflow, and Regression & close-out.

### New issues

Use `git-issue` to create the work order, then add the assignment from
`epic-ticket.md`. Set the spec workflow to REQUIRED because the agent must open
and close its planned spec ticket. If a slice has no semantic delta, document
the no-op model result and its evidence; do not silently skip ticket closeout.

After issue creation, write its URL back to `ticket_plan.yaml` and update the
assignment with the final issue number, feature branch, and worktree path.
Commit and push the canonical plan, then record that commit plus the current
`schedule_revision` in every assignment.

### Existing issues

Read the existing body and preserve it. Add or replace only this bounded region:

```text
<!-- git-epic-workflow:assignment:start -->
...rendered assignment from epic-ticket.md...
<!-- git-epic-workflow:assignment:end -->
```

Use `gh issue edit --body-file`; do not append duplicate assignments on resume.
The assignment explicitly overrides any older instruction to branch from or
target the default branch.

### Mirror the dependency DAG in GitHub

After every issue number exists, mirror each `depends_on` edge with GitHub's
blocking relationship and verify both directions:

```bash
gh issue edit <ticket-issue> --add-blocked-by <dependency-issue>
gh issue view <ticket-issue> --json blockedBy,blocking
```

On resume, compare the GitHub relationships with `ticket_plan.yaml`; add missing
edges and remove stale edges with the corresponding `--remove-blocked-by` /
`--remove-blocking` flags. The plan remains canonical, but the tracker must show
the same readiness graph agents see in their assignments.

Before dispatch, render every assignment from its canonical plan entry and
compare the following fields exactly: ticket ID, schedule revision,
dependencies, blocks, wave, promotion order/predecessor, conflict keys, goal
relations, validation matrix, and evidence root. An older ancestor `plan_commit` alone is
not freshness proof; the copied scheduling fields must still match.

## 7. Commit, push, and dispatch

Review the desired model and plan, then commit and push `epic/<slug>` before
dispatch. Each assignment records an epic base SHA that is already reachable
from the remote epic branch.

Return the goals the epic is aiming at:

| Goal | Kind | Metric | Baseline | Target | Decided by |
| --- | --- | --- | --- | --- | --- |

and a schedule such as:

| Issue | Spec ticket | Start dependencies | Wave | Promote after | Goals | State |
| --- | --- | --- | --- | --- | --- | --- |

An issue is ready to hand off only when every dependency PR is merged into the
remote epic branch. An open or green PR is not a satisfied dependency.

Whenever you recommend the next ticket — at dispatch and on every resume — read
the deferred-findings backlog and present pending entries in the same report:

| ID | Found by | Severity | Summary | Blast radius | Disposition |
| --- | --- | --- | --- | --- | --- |

Ask the user, per pending finding, to promote it to a ticket now, keep it
batched, or close it `wontfix`. Recommend batching unless it blocks a planned
ticket. Promoting a finding is a plan change: new stable ID, dependency edges,
wave, promotion order, conflict keys, revalidated schedule, bumped
`schedule_revision`, new issue. Never retrofit it into a dispatched ticket.

This version does not start agents or poll them. The user passes ready issue
URLs to ticket agents, then invokes the epic workflow again to refresh readiness
or finalize.
