# Wave 1 review — epic/self-improvement-substrate

Range: `56227e50` (epic tip before the wave's first merge) → `058beb3d`.
Wave 1 is a single ticket, SI-01 (#334), merged as PR #349.

**This wave is not a gate.** `review_policy.cadence: milestone`,
`milestones: [2, 4, 6]` — the artifact is produced and wave 2 dispatches without
waiting. The first stop is after wave 2.

## 1. The merge

| PR | ticket | merge commit | planned promotion | actual |
|---|---|---|---|---|
| #349 | SI-01 | `058beb3d` | 10 (first) | first |

Merged with `--merge`, not `--squash`: the migration commit, the confirmatory
evidence commit and the reconcile merge were committed as separate facts and the
finalizer's audit reads them.

One reconcile was required and **it was the epic agent's fault, not the ticket
agent's**. `56227e50` appended `SIS-KICKOFF-F-03` to
`specs/results/deferred_findings_final.yaml` after SI-01 had branched, and SI-01
had appended two rows to the same cumulative file. `git merge-tree` reported one
content conflict. Under `human-review.md` §1 a conflict returns to its agent, so
it did: the agent merged (rather than rebased, correctly — rebasing would have
rewritten sealed evidence commits under an open PR), took the epic file whole and
appended its two rows, and pushed `5b929e17`. Post-merge backlog: 38 rows, zero
deleted or changed lines against either parent, zero conflict markers.

## 2. What landed

The skill surface is a plugin. `.claude-plugin/plugin.json` and
`skill-manager-plugin.toml` at the root; `SKILL.md`, `references/`, `scripts/`,
`templates/`, `prompts/`, `spec_double_compiler/`, `skill-scripts/` and
`skill-manager.toml` now under `skills/spec-double-2/`. The root keeps `tests/`,
`specs/`, `examples/`, `test_graph/`. The `spec_double_compiler` package and the
`tla-spec-dev` CLI keep their names. 227 files, 101 renames, +3152/-508.

### Verified by the epic agent, not accepted as reported

Every load-bearing claim was re-checked against the tree rather than read off the
PR body. All of them held:

| Claim | How it was checked | Result |
|---|---|---|
| repository suite: same 10 failures as baseline | `comm` over sorted failure **names**, not counts | identical sets, **0 new** |
| spec-unit: same 7 failures | same method | identical sets, **0 new** |
| three graphs green | the combined log ends `BUILD FAILED` — that is the superseded `effectProviderExamples` attempt; the fixed run is a separate file | all three green |
| `test_score_tools` 116 passed | `score-tools-final-after-fix.txt`; the superseded `1 failed` run was kept beside it | confirmed |
| backlog appended, not re-templated | diff for deleted/changed lines against both parents | 0 |
| model ownership held | files under `specs/tickets/` and `specs/.history/` in the ticket's own commits | 0 and 0 |
| TLA+ unchanged | 14 changed lines across three model trees | 14 comments, 0 semantic |

The agent keeping the superseded score-tools log next to the fixed one is what
made the one discrepancy I found settleable in a single command. That is the
practice to keep.

## 3. Decisions made implicitly, and guardrails overridden

**Guardrail overrides: none.** No `--force`, no `SKILL_GATES=off`, no
`--allow-open`, no `--accept-new`, no skipped or xfailed test, no REQUIRED matrix
entry downgraded. The `home close-out` verdict was clean with no blockers.

**Implicit decisions, all four worth a reader's attention:**

| Decision | Where | Cost to reverse |
|---|---|---|
| The ticket agent corrected the epic agent's scaffolded `specs/tickets/SI-01/desired/` | 2 files, 34 lines, all path substitutions | one `git checkout` |
| Reconciled by **merge**, not rebase | `5b929e17` | would require rewriting a published PR head |
| A detached, home-less worktree was created for baseline measurement, then removed | `/private/tmp/.../base-wt` | n/a, already gone |
| The epic agent scaffolds ticket workspaces **per wave**, not all at once | SI-02 scaffolded at this close | n/a |

On the first: the agent invoked `model_ownership_rule`'s "a **small** correction
to it is yours to make". **Accepted, after verification rather than on the
argument.** Both files are now byte-identical to the fixed `program_model` and to
`current`; only 2 of my files were touched; every changed line is a path
substitution. One line looked like a deletion of `sys.path.insert(0, str(root))`
and is in fact a modification to `str(root / "skills" / "spec-double-2")`, which
is what keeps `from scripts.budgets import ...` resolving after the move. Without
the correction my scaffolded workspace produced 94 "could not locate
tla-spec-dev repository root" errors and could not run at all.

On the third: rule 10's hazard is that an agent launched in a home-less checkout
writes the operator's global home. The agent reports no session was ever launched
there — only its own `python3`/`pytest` invocations — which is what makes the
hazard not apply. It is recorded here rather than filed, and it motivates the
strongest recommendation in §5.

**A correction to the epic agent's own record.** The commit message on
`56227e50` says the backlog went "37 → 38". On the epic branch it went **35 →
36**; 38 is the post-merge total. The epic branch is never force-pushed, so the
correction lives here rather than in a rewritten commit.

## 4. Where the bugs probably are

1. **Silent vacuity in declared scopes** — the instrument registry's enumeration
   roots, the A/B forbidden-surface git pathspecs, `subjects.toml` scopes,
   `EXECUTABLE_SURFACES`, `CITATION_SCOPE`. A stale prefix does not fail; it
   matches nothing and the check goes green. Every one was repointed in this PR,
   but nothing proves a scope still resolves to a non-empty set. Cheapest
   experiment: assert non-emptiness at each site.
2. **Sealed analysis scripts under `specs/results/scorecards/**`** locate the
   repo by walking up for `references/eval_scorecard.md`, which moved.
   `SI-01-DF-01`; includes a `stage_judge_trees.sh` `rm -f` that now silently
   removes nothing.
3. **`PREREGISTRATION.yaml` and its guards disagree** — the document names
   pre-migration forbidden surfaces while the two live git-pathspec guards were
   repointed. `SI-01-DF-02`. The agent deliberately did not rewrite a
   preregistration after the fact, which is right.
4. **The pristine-checkout `effectProviderExamples` failure that did not
   reproduce here.** A baseline run on clean `4d563e2d` failed at
   `reminder_worker`; this branch does not reproduce it. Recorded, unexplained,
   and *not* evidence about the migration either way. Suspicion only.
5. **`run spec-unit-tests --ticket <id>` reports a target it never ran** —
   `SIS-KICKOFF-F-04`, confirmed at source.

## 5. Architectural changes worth making, including to the epic's own machinery

Four recommendations, three of them from the ticket agent and each backed by
something this wave measured. **Recommended, not implemented** — they re-enter as
tickets.

- **A supported throwaway-baseline primitive.** Comparing against the pre-change
  tree is what separated 26 self-inflicted regressions from 17 pre-existing
  failures, and it is the single highest-value thing the ticket did. Today the
  only way to get one is an undeclared, home-less worktree that rule 10 warns
  against, because `git archive` is unusable (validation calls `git rev-parse
  HEAD`, which exits 128 outside a repository). The substrate should offer this
  rather than leave agents to improvise it. → SI-07 or a new ticket.
- **A "markers this tree is located by" list.** The migration checklist is a
  grep, and a grep finds named paths. It does not find code that walks up for
  `references/eval_scorecard.md`, `skill-manager.toml`, or a sibling
  `spec_double_compiler/`. Those produced all 26 new failures, every one at a
  distance from the moved file. → SI-02 needs this before it moves five more
  skills.
- **Record a baseline before the first edit, as a matrix step.** Files excluded
  from the suite for runtime (`test_score_tools`) have no baseline at all, and
  the matrix never asks for one. Pre-existing failures were nearly reported as
  new, twice.
- **Never compare numbers produced by different commands.** A bogus citation
  delta appeared from two different `grep` patterns and only dissolved when the
  same tool was run on both trees.

Machinery friction reported and resolved: `skt ticket new` worked first time,
because the kickoff had already found the exported-`SKILL_MANAGER_HOME` trap and
the assignment documents the remedy. That is the loop working.

## 6. Suggested next steps

**Ready now:** SI-02 (#335), wave 2 — nest the five workflow skills. Its
workspace is scaffolded from the migrated `current` (verified byte-identical,
zero stale path references). Wave 2 **is** a gate: the next stop is after it
merges, and that is where the migration and the nesting are reviewed together
before the layout becomes permanent.

**Deferred findings — 6 pending, none blocking:**

| ID | Found by | Severity | Summary | Disposition |
|---|---|---|---|---|
| `SIS-KICKOFF-F-01` | epic kickoff | minor | evaluation-ticket schema drifts three ways | pending → SI-07 |
| `SIS-KICKOFF-F-02` | epic kickoff | major | `command -v tla-spec-dev` resolves to the root-home shim | pending → SI-10 |
| `SIS-KICKOFF-F-03` | SI-01 agent | major | ten assignments name `--ticket <id>` against workspaces only the epic agent creates | pending → SI-07 |
| `SIS-KICKOFF-F-04` | SI-01 agent | major | `run spec-unit-tests` resolves two targets, executes one, reports both | pending → SI-07 |
| `SI-01-DF-01` | SI-01 agent | minor | sealed scorecard scripts locate the repo by a marker that moved | pending |
| `SI-01-DF-02` | SI-01 agent | minor | preregistration and its guards disagree after the move | pending |

`SIS-KICKOFF-F-02` got sharper with this merge: the operator's root-home
`tla-spec-dev` shim now points at a path that no longer exists in an un-synced
home.

**Goal trajectory.** `GOAL-one-unit` is the only goal this wave touches, as
`enabling`. Expected effect was "none — it unblocks SI-02", and that is what
happened: the unit count is still 6 and moves in wave 2. The local signal
(`--help` from the checkout, three graphs green) passed. No goal is off track;
none is measurable yet either.

**What gets more expensive if deferred.** The marker-walking list, above — SI-02
moves five more skills and will hit the same class of failure at the same
distance, without the benefit of a pre-move baseline unless one is taken first.

**Standing worktrees and headroom.** Three: the main checkout, the epic
worktree, and SI-01's ticket worktree (left standing deliberately; swept with all
others at epic close). 88 GB free.

## 7. The thing this wave is actually evidence for

The epic's thesis is that the substrate does not improve because proposing a
change costs more than working around it. Wave 1 produced the opposite behaviour
twice, before the instrument that measures it exists:

- the ticket agent hit a defect it was **forbidden** to fix (`open ticket` is the
  epic agent's), reported it with evidence, and substituted a documented weaker
  measurement rather than silently using one;
- it then found a second defect in the same command, declined to file it because
  filing would have contradicted an explicit instruction about the backlog total,
  and handed it to the owner to file instead.

Both are now `SIS-KICKOFF-F-03` and `-F-04`, with SI-07 as their home. Neither
was retrofitted into a dispatched ticket.
