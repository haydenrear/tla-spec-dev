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
conflict_keys:
  production: []
  tla: []
  adapters: []
  test_graph: []
  workflow: []
```

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
- each `promotion_predecessor` names the preceding ticket in that total order.

Run the bundled validator before dispatch and whenever the schedule changes:

```bash
uv run <git-epic-workflow-skill>/scripts/validate_epic_plan.py \
  specs/desired_program_model/ticket_plan.yaml
```

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
dependencies, blocks, wave, promotion order/predecessor, conflict keys,
validation matrix, and evidence root. An older ancestor `plan_commit` alone is
not freshness proof; the copied scheduling fields must still match.

## 7. Commit, push, and dispatch

Review the desired model and plan, then commit and push `epic/<slug>` before
dispatch. Each assignment records an epic base SHA that is already reachable
from the remote epic branch.

Return a schedule such as:

| Issue | Spec ticket | Start dependencies | Wave | Promote after | State |
| --- | --- | --- | --- | --- | --- |

An issue is ready to hand off only when every dependency PR is merged into the
remote epic branch. An open or green PR is not a satisfied dependency.

This version does not start agents or poll them. The user passes ready issue
URLs to ticket agents, then invokes the epic workflow again to refresh readiness
or finalize.
