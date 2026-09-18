# Epic assignment — author one shared-workflow ticket

Use this mode only when an epic owner has already created and pushed an
`epic/<slug>` branch, scaffolded one shared spec workflow there, and planned the
ticket in `specs/desired_program_model/ticket_plan.yaml`. `git-issue` authors the
work order; it does not create those workflow-wide artifacts.

Each GitHub issue maps to exactly one stable spec ticket. Keep the ordinary
Summary, Goals & evaluation, References, Discovery notes, Worktree & branch,
Spec workflow, and Regression & close-out sections, then add this bounded
assignment after the completed Summary section and before the
`## Goals & evaluation` section. Its presence selects epic mode and overrides
every ordinary instruction to branch from, open a PR against, merge to, or close
against the default branch.

The prose `## Goals & evaluation` section is rendered *from* this block rather
than agreed separately with the user — the epic already agreed the goals and
recorded them in its canonical plan. This block is the machine-readable copy the
ticket agent reads; the prose section restates it for a human and must not
introduce a metric, baseline, target, or contribution the plan does not carry.

## Assignment block

Render every field; do not leave placeholders in a dispatched issue. Goal fields
and their names come from
`<git-epic-workflow-skill>/references/goals-and-evaluation.md` and the plan
schema `<git-epic-workflow-skill>/scripts/validate_epic_plan.py` enforces — a
rename on either side breaks the assignment↔plan equality check below.

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
  mode: "external"          # external TO THIS AGENT — do not change this value
  ticket_agent_stops_after: "pr_open"
  merged_by: "epic-owner"   # never this agent; never the default branch
  cadence: "wave"           # when the human review happens, epic-side
  artifact_root: "results/epic-<slug>/review"
deferment:
  mode: "batch"          # batch | ask | inline
  blocking: "escalate"   # escalate | ask
  budget: 5
  backlog: "specs/desired_program_model/deferred_findings.yaml"
```

This issue belongs to an existing shared spec workflow. The epic assignment
overrides ordinary instructions to branch from or target the default branch.

`review.mode` stays `external` because that is what the field means to the
ticket agent — the review is not that agent's, and `git-issue-workflow`'s
`references/epic-ticket.md` §1 refuses an assignment whose mode is anything
else. `merged_by` and `cadence` are additive: they say who performs the merge
the ticket agent is already forbidden to perform, and when the human sees the
result. Do not encode the cadence in `mode`.

- Read `goals` before implementing. The `expected_effect` is the result this
  change is aiming at; the ticket named in `decided_by` decides the goal on the
  integrated epic. Run `local_signal` before close, record the number under the
  evidence root, and report it against `expected_effect` — including "no
  measurable movement".
- A local signal is a signal, not a gate. A missed one is reported, never
  hidden, and never justifies weakening the REQUIRED validation matrix, tuning
  to the metric, or working outside this ticket's conflict keys.
- Start the worktree from the latest `origin/epic/<slug>` after all
  `depends_on` PRs are merged.
- Run `tla-spec-dev --spec-root specs open ticket <stable-ticket-id>`; never
  scaffold another workflow.
- Before close, wait for `promotion_predecessor`, reconcile the latest epic tip,
  and rerun the validation matrix.
- Mark and close only this spec ticket with every evidence path. Never run the
  whole-workflow close script and never use `--accept-new`.
- Defects found outside this ticket's conflict keys and semantic delta are
  **deferred, not fixed**: record them in the backlog under the epic's deferment
  policy and keep working the assigned slice. Escalate blocking out-of-scope
  findings instead of widening scope. List each backlog ID filed, with its
  severity and a one-line summary, under `## Deferred findings` in the PR body,
  or `None`.
- The worktree has its own Skill Manager home (`<worktree>/.skill-manager`,
  gitignored, a real copy of the project home), and **nothing changed inside it
  is in this PR**. Before stopping, run
  `skill-manager home close-out --home <worktree>/.skill-manager --into <main-working-tree>/.skill-manager`
  — the **main working tree's** home, not `$PWD`'s nearest git toplevel, which
  from inside the worktree names the worktree's own home — and state the verdict
  in the PR body, then list every unit changed and why under `## Review input` →
  *Machinery friction*.
  `skill-manager unit publish <unit> --ticket <ticket>` is allowed for the
  agent's own edits — that reaches the unit's own repository and contends with
  nothing. Do **not** run `home sync` into the project home: that is one shared
  destination, this agent cannot see the other tickets writing it, and the epic
  agent reconciles every worktree's home there in serial at wave close.
- Commit and push everything to be kept — evidence, backlog entries, close
  history. Leave the worktree standing; the epic agent removes every worktree in
  one sweep at the end of the epic, after checking that nothing uncommitted,
  stashed, unpushed, or unmerged is left in it.
- The PR body is **review input**, not only a delivery record. The epic owner
  merges it and then builds one review over the whole wave for a human, so it
  carries a `## Review input` section: the hot spots created, the decisions made
  that nobody asked for, any guardrail overridden, where the agent would look
  for bugs in its own change, and what about the tooling or skills slowed it
  down. The ticket agent is the only one who still knows the last two.
- Push the sealed ticket branch and open its PR with base `epic/<slug>` and
  `Refs #<issue-number>`. Stop for external review. The epic owner merges this
  PR into the epic branch; do not merge it, do not merge to the default branch,
  and do not close the GitHub issue.
<!-- git-epic-workflow:assignment:end -->
````

## Evaluation-ticket variant

A ticket that *decides* one or more goals rather than contributing to them sets
`role: evaluation`, lists `owns_goals`, and replaces the per-goal contribution
block with the harness it must run:

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

`owns_goals` must list every goal whose canonical `evaluation_ticket` is this
ticket — no more and no fewer. Its issue body states, in addition to the shared
assignment rules:

- run each owned `harness` from a fresh start on the reconciled epic tip, after
  every contributing ticket has merged, and write results to `evidence_root`;
- report baseline → measured → target and a verdict (`met` / `missed` /
  `unmeasured` with a reason) per goal in the PR body;
- never edit a target to match a result and never re-run selectively until a
  number passes — report the run that happened;
- file regressions and shortfalls as deferred findings for the epic owner
  instead of fixing them in this ticket.

## Validate before dispatch

- `epic.branch` exists remotely, `base_sha` and `plan_commit` are reachable
  from it, and
  `ticket.pr_base` exactly equals `epic.branch`.
- `epic.workflow` names the existing shared workflow, and `ticket.spec_id`
  identifies exactly one entry in its canonical ticket plan. The GitHub issue
  URL is recorded on that same entry.
- `schedule_revision`, `depends_on`, `blocks`, `wave`, conflict keys,
  `promotion_order`, `promotion_predecessor`, `role`, the goal relations, the
  validation matrix, and the evidence root exactly match the canonical plan
  entry. The assignment does not silently revise workflow-wide planning data.
- **Goal relations are copied, not authored.** Every entry under `goals:` comes
  from the canonical plan: `goal` is a goal ID declared in the plan's
  `epic_goals`, and `contribution`, `expected_effect` and `local_signal` equal
  that plan entry's `goals` relation field for field. `kind`, `statement`,
  `metric`, `baseline`, and `target` are the plan's `epic_goals` values for that
  ID, and `decided_by.ticket` / `decided_by.harness` are that goal's
  `evaluation_ticket` and `harness`. A value that exists only in the issue is a
  dispatch error, not a local refinement — fix the plan, then re-render.
- `contribution` is one of `direct`, `enabling`, or `guard`, and
  `expected_effect` is non-empty in every case (`none — enabling only` plus what
  it unblocks, for `enabling`). `local_signal` is a runnable command or
  `N/A: <reason>`, never an empty string. A `direct` contribution with no local
  signal is allowed but is worth questioning: nothing then predicts the final
  measurement from inside the worktree.
- `ticket.role` is `implementation` or `evaluation`. When it is `evaluation`,
  `owns_goals` lists exactly the goals whose `evaluation_ticket` is this ticket,
  each goal entry carries `harness` and `evidence_root`, and the ticket promotes
  after every contributor to those goals. When it is `implementation`,
  `owns_goals` is absent.
- The prose `## Goals & evaluation` section elsewhere in the body agrees with
  this block. The assignment is authoritative; a disagreement is fixed before
  dispatch rather than left for the ticket agent to adjudicate.
- `validation.tlc`, `validation.spec_unit`, and `validation.repository_unit` are
  exact runnable commands; an inapplicable command is `N/A: <reason>`, never an
  empty string. `validation.graphs` contains exact repository graph names and
  `validation.spec_graph` names the repository's spec-conformance graph or an
  explicit N/A reason. `specWorkflow` is the tla-spec-dev toolchain's own graph
  and appears only when that repository is the target. The evidence root is a
  ticket-specific destination for reports and close evidence.
- Review remains external and the stop point remains `pr_open`. `merged_by` is
  the epic owner — never the ticket agent, never the default branch — and
  `cadence` and `artifact_root` say when and where the epic-side human review
  happens. Never encode the cadence in `mode`: `git-issue-workflow`'s
  `references/epic-ticket.md` §1 refuses an assignment whose mode is anything
  but `external`.
- The `deferment:` block is copied from the canonical plan's `deferment_policy`
  — mode, blocking rule, budget, and backlog path — not authored here. See
  `<git-epic-workflow-skill>/references/deferment.md` for what those values
  mean.
- The body contains exactly one start marker and one end marker.

For a new issue, create the ordinary work order first, capture its number and
URL, write the URL into the canonical ticket plan, then render the final branch,
worktree, and assignment fields and update the body. For an existing issue,
preserve its body and replace only the bounded assignment. Never append a second
copy when resuming an epic.
