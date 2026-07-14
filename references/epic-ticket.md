# Epic ticket assignment and execution

This block turns an ordinary `git-issue` work order into one ticket of a shared
epic. Keep it marker-delimited so an epic resume can update the assignment
without rewriting the issue's discovery.

## Assignment block

````markdown
<!-- git-epic-workflow:assignment:start -->
## Epic execution — REQUIRED

```yaml
version: 1
epic:
  id: "<epic-id>"
  workflow: "<unique-workflow-name>"
  branch: "epic/<slug>"
  base_sha: "<commit-reachable-from-origin-epic>"
  plan_commit: "<commit-containing-canonical-plan>"
  schedule_revision: 1
  default_branch: "<default-branch>"
ticket:
  spec_id: "<stable-ticket-id>"
  feature_branch: "feature/<issue-number>-<slug>"
  worktree: "../wt-<issue-number>-<slug>"
  pr_base: "epic/<slug>"
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
validation:
  tlc: "<exact command or N/A: reason>"
  spec_unit: "<exact command>"
  repository_unit: "<exact command or N/A: reason>"
  graphs: ["<affected-repository-graph>"]
  spec_graph: "<repository spec-conformance graph or N/A: reason>"
  toolchain_spec_workflow: "N/A unless this repository is tla-spec-dev"
  evidence_root: "<ticket-results-path>"
review:
  mode: "external"
  ticket_agent_stops_after: "pr_open"
```

This issue belongs to an existing shared spec workflow. The epic assignment
overrides ordinary instructions to branch from or target the default branch.

- Start the worktree from the latest `origin/epic/<slug>` after all
  `depends_on` PRs are merged.
- Run `tla-spec-dev --spec-root specs open ticket <stable-ticket-id>`; never
  scaffold another workflow.
- Before close, wait for `promotion_predecessor`, reconcile the latest epic tip,
  and rerun the validation matrix.
- Mark and close only this spec ticket with every evidence path. Never run the
  whole-workflow close script and never use `--accept-new`.
- Push the sealed ticket branch and open its PR with base `epic/<slug>` and
  `Refs #<issue-number>`. Stop for external review; do not merge to the default
  branch or close the GitHub issue.
<!-- git-epic-workflow:assignment:end -->
````

## Ticket-agent flow

The presence of the start marker selects epic mode before ordinary
`git-issue-workflow` provisioning.

### 1. Verify readiness

Fetch remote state and confirm:

- every `depends_on` ticket PR is merged into the declared epic branch;
- `base_sha` is an ancestor of `origin/epic/<slug>`;
- `plan_commit` is reachable from the epic branch;
- the workflow name and ticket ID still exist in `ticket_plan.yaml`;
- the assignment's schedule revision, dependencies, blocks, wave, promotion
  order/predecessor, conflict keys, validation matrix, and evidence root exactly
  match that canonical ticket entry;
- the feature branch is not already merged or owned by another worktree.

Do not treat a locally closed spec ticket, a green branch, or an open PR as a
satisfied dependency.

### 2. Create the worktree from the epic branch

```bash
git fetch origin
git worktree add ../wt-<issue-number>-<slug> \
  -b feature/<issue-number>-<slug> origin/epic/<slug>
cd ../wt-<issue-number>-<slug>
```

Resume the declared branch/worktree instead of creating another when it already
exists. Never use `origin/<default-branch>` in epic mode.

### 3. Open only the assigned ticket

```bash
tla-spec-dev --spec-root specs open ticket <stable-ticket-id>
```

Update ticket-local `desired/` first. It is the whole-program state after this
ticket. Then implement production code and advance ticket-local `current/` to
the behavior that actually landed. Include all assigned surfaces:

- Internal/External TLA+ actions, state, invariants, and configs;
- spec-unit adapters, generated cases, and conformance tests;
- Test Graph adapters, bindings, nodes, composition, and context contracts;
- repository code/tests and structured validation evidence.

Do not reorder tickets, edit another ticket's status, or change workflow-wide
dependencies from the ticket branch.

### 4. Run the ticket validation loop

Run every matrix entry marked REQUIRED. Discover each affected graph before
running it and use Test Graph's saved-context loop for isolated failures. At a
minimum, record:

```bash
tla-spec-dev --spec-root specs run spec-unit-tests --ticket <stable-ticket-id>
<test-graph-skill>/scripts/discover.py <graph>
<test-graph-skill>/scripts/run.py <graph>
```

Also run TLC, repository unit tests, the repository's assigned spec-conformance
graph, and any adapter commands from the issue. `specWorkflow` is the
spec-double-compiler repository's own CLI-lifecycle graph; run it only when the
plan explicitly targets that repository. Store reports under the evidence root.

### 5. Enter the serialized promotion lane

Parallel implementation ends here. Wait until the `promotion_predecessor` PR is
merged into the epic branch. Fetch and rebase or merge the latest epic tip into
the ticket branch before closing.

Re-read the canonical plan after fetching and repeat the complete assignment
equality check. A changed schedule revision or field mismatch returns the issue
to the epic owner; do not promote from stale assignment metadata.

Reconcile deliberately:

- preserve predecessor close-history entries and closed plan statuses;
- use the latest epic `specs/current` as the whole-program base;
- reapply this ticket's semantic delta to ticket-local desired/current;
- retain all sibling Test Graph artifacts and bindings;
- rerun the complete ticket validation matrix.

If reconciliation changes scope or reveals a semantic conflict, stop and ask
for an amendment/reconciliation ticket. Do not patch workflow-wide state
silently.

### 6. Close only this spec ticket

Mark only this plan entry closed/done, then run:

```bash
tla-spec-dev --spec-root specs close ticket <stable-ticket-id> \
  --summary "<what landed>" \
  --result <evidence-path> \
  --result <another-evidence-path>
```

The default equality gate must pass. Do not use `--accept-new`,
`--no-promote-current`, or the whole-workflow close script. Inspect and commit
the append-only history entry, promoted project current, graph artifacts, and
evidence together.

### 7. Open the ticket PR and stop

Push the feature branch and create a PR explicitly targeting the epic branch:

```bash
git push -u origin feature/<issue-number>-<slug>
gh pr create --base epic/<slug> --head feature/<issue-number>-<slug> \
  --title "<ticket-id>: <title>" --body-file <pr-body.md>
```

The PR body contains:

- `Refs #<issue-number>`;
- epic branch, workflow, and spec ticket ID;
- dependency and promotion-predecessor checks;
- exact commands run and report/evidence paths;
- the close-history path and resulting commit SHA.

Stop for external review. Do not self-merge, target the default branch, run
whole-workflow promotion, sync the primary checkout to the default branch, or
close the GitHub issue. The closed PR head is sealed; semantic review changes
require an explicit amendment ticket so append-only evidence stays truthful.
