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
  role: implementation      # implementation | evaluation
  conflict_keys:
    production: []
    tla: []
    adapters: []
    test_graph: []
    workflow: []
goals:
  - goal: "<goal-id>"
    kind: "perf"            # perf | eval | integration | quality
    statement: "<what should be measurably better after the epic>"
    metric: "<measured quantity>"
    baseline: "<value + commit it was measured on, or 'unmeasured'>"
    target: "<threshold that counts as success>"
    decided_by:
      ticket: "<evaluation-ticket-id>"
      harness: "<command the evaluation ticket runs on the integrated epic>"
    contribution: "direct"  # direct | enabling | guard
    expected_effect: "<direction and magnitude this ticket should produce>"
    local_signal: "<cheap in-worktree command, or 'N/A: reason'>"
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
deferment:
  mode: "batch"          # batch | ask | inline
  blocking: "escalate"   # escalate | ask
  budget: 5
  backlog: "specs/desired_program_model/deferred_findings.yaml"
```

This issue belongs to an existing shared spec workflow. The epic assignment
overrides ordinary instructions to branch from or target the default branch.

- Read `goals` before implementing. The `expected_effect` is the result this
  change is aiming at; the named evaluation ticket decides the goal on the
  integrated epic. Run `local_signal` before close, record the number under the
  evidence root, and report it against `expected_effect` — including "no
  measurable movement".
- Start the worktree from the latest `origin/epic/<slug>` after all
  `depends_on` PRs are merged.
- Run `tla-spec-dev --spec-root specs open ticket <stable-ticket-id>`; never
  scaffold another workflow.
- Before close, wait for `promotion_predecessor`, reconcile the latest epic tip,
  and rerun the validation matrix.
- Mark and close only this spec ticket with every evidence path. Never run the
  whole-workflow close script and never use `--accept-new`.
- A local signal is a signal, not a gate. A missed one is reported, never
  hidden, and never justifies weakening the REQUIRED matrix or chasing the
  metric outside this ticket's conflict keys.
- Defects found outside this ticket's conflict keys and semantic delta are
  **deferred, not fixed**: record them in the backlog under the epic's
  deferment policy and keep working the assigned slice. Escalate blocking
  out-of-scope findings instead of widening scope.
- Your worktree has its own Skill Manager home
  (`<worktree>/.skill-manager`, gitignored, a real copy of the project home), and
  **nothing you change inside it is in this PR**. Before stopping, run
  `skill-manager home close-out --home <worktree>/.skill-manager --into <repo-root>/.skill-manager`
  and state the verdict in the PR body. Clear any blocker with the remedy it
  prints — `unit publish` for a skill improvement, `home sync --merge` to survive
  the teardown. Leave the worktree standing; the finalizer removes it.
- Push the sealed ticket branch and open its PR with base `epic/<slug>` and
  `Refs #<issue-number>`. Stop for external review; do not merge to the default
  branch or close the GitHub issue.
<!-- git-epic-workflow:assignment:end -->
````

## Evaluation-ticket variant

A ticket that decides one or more goals sets `role: evaluation`, lists
`owns_goals`, and replaces the per-goal `contribution` block with the harness it
must run:

```yaml
ticket:
  role: evaluation
  owns_goals: ["<goal-id>"]
goals:
  - goal: "<goal-id>"
    baseline: "<value + commit>"
    target: "<threshold>"
    harness: "<exact command run on the integrated epic tip>"
    evidence_root: "<results/epic-<slug>/goals/<goal-id>>"
    contribution: "guard"
    expected_effect: "decides the goal; adds no behavioral delta"
    local_signal: "N/A: this ticket is the measurement"
```

Its issue body states, in addition to the shared assignment rules:

- run each owned harness from a fresh start on the reconciled epic tip, after
  every contributing ticket has merged, and write results to `evidence_root`;
- report baseline → measured → target and a verdict (`met` / `missed` /
  `unmeasured` with a reason) per goal in the PR body;
- never edit a target to match a result and never re-run selectively until a
  number passes; report the run that happened;
- file regressions and shortfalls as deferred findings for the epic owner
  instead of fixing them in this ticket.

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
  order/predecessor, conflict keys, goal relations, validation matrix, and
  evidence root exactly match that canonical ticket entry;
- the feature branch is not already merged or owned by another worktree.

Do not treat a locally closed spec ticket, a green branch, or an open PR as a
satisfied dependency.

### 2. Create the worktree from the epic branch

Apply the index-base pinning conventions (see "Worktree provisioning
conventions" in `plan-and-schedule.md`): clean tree, resolve the epic branch
to `commit_oid`/`tree_oid` **once**, create-only
`refs/index-bases/<repo-id>/<tree_oid>` retention ref, branch from the pinned
commit. Never re-resolve `origin/epic/<slug>` after creation — a ref is a
symbolic name, not an identity.

```bash
git fetch origin
test -z "$(git status --porcelain)" || { echo "dirty tree — reconcile first"; exit 1; }
commit_oid=$(git rev-parse origin/epic/<slug>)
tree_oid=$(git rev-parse "origin/epic/<slug>^{tree}")
git update-ref "refs/index-bases/$(basename "$(git rev-parse --show-toplevel)")/${tree_oid}" "$commit_oid" ""
git worktree add ../wt-<issue-number>-<slug> \
  -b feature/<issue-number>-<slug> "$commit_oid"

# `git worktree add` alone leaves a checkout with NO Skill Manager home, so an
# agent launched here reads and writes the operator's global ~/.skill-manager —
# and an epic runs several ticket agents at once. Close that window now, before
# anything that installs, syncs, binds or resolves:
"${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/skills/git-issue-workflow/scripts/bootstrap-home.sh" \
  --root ../wt-<issue-number>-<slug>

cd ../wt-<issue-number>-<slug>
```

**Those first three lines are load-bearing, not tidiness.** `git fetch origin`
then `commit_oid=$(git rev-parse origin/epic/<slug>)` is what makes the branch
point the PUBLISHED tip. Branching a bare `epic/<slug>` instead resolves the
**local** ref — and in an epic whose ticket PRs are merged server-side with `gh
pr merge`, `origin/epic/<slug>` advances while your local `epic/<slug>` never
does, and neither does your local *copy* of the remote ref, because only a fetch
moves that. Measured once: a ticket branched **21 commits behind** and caught it
only because its work order carried a `base_sha` it thought to compare `HEAD`
against. It would otherwise have edited a superseded file and reported a true
sentence about the wrong tree.

`wt new` refuses that case now (exit 7, git-issue-workflow-skill#10) — but
**epic mode does not go through `wt new`**, it calls `git worktree add` directly,
which has no such gate. So in epic mode the fetch-and-resolve above *is* the
protection. Do not skip it, and do not substitute a bare branch name for
`"$commit_oid"`.

An ordinary (non-epic) ticket does both of those in one command, `wt new <ticket>
"$commit_oid"` — which is also a resolved SHA, and for the same reason. Epic mode
branches by hand because `wt` chooses the worktree path
(`<parent>/<repo>-<ticket>`) and an epic assignment **declares** it — the
assignment wins. The home the two routes produce is identical, and teardown is
the same single command either way:
`"${SKILL_MANAGER_HOME:-$HOME/.skill-manager}/skills/git-issue-workflow/scripts/wt" close <issue-number>-<slug>`,
which finds a hand-made `../wt-<issue-number>-<slug>` by search.

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

### 4a. Defer failure cases found outside the assigned slice

Validation and review will surface real defects this ticket did not cause. Do
not chase them. Read `deferment.md` and apply the policy from the **canonical
plan** (`deferment_policy` in `ticket_plan.yaml`); the assignment block mirrors
it, but the plan wins if they differ.

For each failure case:

1. Classify it. In scope — every touched surface is inside this ticket's
   `conflict_keys` and its desired model already implies the fix — then it is
   ordinary ticket work; fix it.
2. Out of scope and blocking this ticket's REQUIRED matrix: stop, file the
   backlog entry with `severity: blocking`, push without closing the spec ticket
   or opening a promotion PR, and return the ticket to the epic owner with the
   surfaces a fix would touch and the sibling tickets sharing those keys.
3. Out of scope and non-blocking: append a backlog entry, then follow
   `mode` — `batch` continue, `ask` ask the owner now-or-batch, `inline` fix
   only within this ticket's conflict keys and record it.

Stop implementing and report when deferred findings exceed `budget`: that many
out-of-scope defects means the ticket's premise is wrong, and the next fix will
not be the last one.

Backlog entries are planning data. Commit them with the ticket's normal commits;
never place them in ticket-local `desired/` or `current/`, and never offer them
as close evidence. A deferred finding never justifies weakening a REQUIRED
validation entry, loosening an invariant, skipping a test, or closing a ticket
whose equality gate fails.

### 4b. Record the goal signal

Run each declared `local_signal` in the ticket worktree and store its output
under the ticket evidence root. Compare it with `expected_effect` and record one
of: moved as expected, moved less than expected, no measurable movement, or
moved the wrong way. An evaluation ticket instead runs its owned `harness` on
the reconciled epic tip and records baseline → measured → target per goal.

The local signal never changes the ticket's pass/fail: the REQUIRED validation
matrix decides that, and the evaluation ticket decides the goal. Do not tune,
re-run selectively, or widen scope to make the number look better. If the signal
shows the goal is unreachable from this slice, finish the assigned semantic
delta, file a deferred finding describing what the goal would actually require,
and report it — that is plan feedback, not ticket work.

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
- the close-history path and resulting commit SHA;
- a `## Goal contribution` section with one row per declared goal — goal ID,
  contribution kind, expected effect, measured local signal (or `N/A: reason`),
  and the evaluation ticket that decides it;
- a `## Deferred findings` section listing each backlog ID filed by this ticket
  with its severity and one-line summary, or `None`;
- the `home close-out` verdict for this ticket's worktree, and — if it blocked —
  which units were published with `unit publish` or lifted with
  `home sync --merge`. The finalizer removes this worktree and cannot see inside
  its home; this line is the only place that fact is recorded.

Stop for external review. Do not self-merge, target the default branch, run
whole-workflow promotion, sync the primary checkout to the default branch, or
close the GitHub issue. The closed PR head is sealed; semantic review changes
require an explicit amendment ticket so append-only evidence stays truthful.
