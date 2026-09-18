Refs #333

**Epic**: `self-improvement-substrate` · **branch**: `epic/self-improvement-substrate` · **workflow**: `self-improvement-substrate` · **spec ticket**: `SI-06` · **wave 3**

One shape in each ticket-side skill — a `## Skill changes proposed` PR section —
and the ticket-agent half of the new model-ownership boundary. Markdown only:
ten `.md` files under `skills/`, plus three rows on the deferred-findings
backlog. `debugging` is untouched, by owner decision.

## What landed

| Surface | Change |
|---|---|
| `git-issue-workflow/SKILL.md` | new card section *A blocker you met is a change you propose* (three columns, four rules); epic-mode bullet now names model ownership |
| `git-issue-workflow/references/complete.md` | new **§5a** — the section, `none met`, the two worked examples, "runs nothing new", "never a gate"; checklist row |
| `git-issue-workflow/references/validation-loop.md` | what stayed red in the *substrate* is a proposal, not a defect in your change |
| `git-issue-workflow/references/epic-ticket.md` | **§3** forks on `planning_rules.model_ownership_rule` (ticket-agent half); **§6** is skipped when the epic owns the model; **§7** requires the section; two checklist rows |
| `git-issue/SKILL.md` | issue template asks for it under *Regression & close-out*; move 5 and move 6 updated |
| `git-issue/references/regression-close.md` | new **§5a** (author's half: what to ask for, and that `none met` is expected); epic-override list and checklist |
| `git-issue/references/spec-workflow.md` | *Unless the epic owns the model* — what the issue must say instead |
| `git-issue/references/epic-assignment.md` | renders the Model-ownership note in place of the `open ticket` line; adds the PR-body bullet |
| `discovery/SKILL.md`, `test-graph/SKILL.md` | one section each: when this skill's own instruction did not work, say so rather than working around it |

Written for **SI-09**: the instruction is on each card, the rationale and the
worked examples are in the references.

## Dependency and promotion checks

- `depends_on: [SI-02]` — PR #350, **MERGED**, merge commit `a42e0f7e`, reachable from `origin/epic/self-improvement-substrate`.
- `base_sha` `994f650c` is an ancestor of the epic tip; branched from the tip itself (`994f650c`), re-verified unchanged at PR time.
- `promotion_predecessor: SI-05` — **not merged**, and deliberately not waited on: this ticket performs **no promotion**. The epic agent owns the model and closes the spec ticket at wave merge, so §5/§6 of `epic-ticket.md` do not apply here.
- No `open ticket`, `close ticket`, `close_tickets.py`, or `--accept-new` was run. Nothing under `specs/` outside `results/` was modified.
- **Close-history path: none** — this ticket closed no spec ticket. Evidence for the epic agent's close is under the evidence root.

## Validation

Evidence root: `specs/results/epic-self-improvement-substrate/tickets/SI-06/` (`README.md` there is the index).
**Baselines were taken before the first edit; every comparison is by failure NAME, not count.**

| Entry | Command | Result |
|---|---|---|
| `tlc` | — | `N/A` per the assignment (epic agent owns the model) |
| `spec_unit` | `python3 skills/spec-double-2/scripts/tla_spec_dev.py --spec-root specs run spec-unit-tests --ticket SI-06` | ran; **known-weak, reproduced** — see below |
| `spec_unit` (ticket target, explicit) | `... run spec-unit-tests --target specs/tickets/SI-06/desired` | 7 failed / 46 passed → **7 failed / 46 passed, same names** |
| `spec_unit` (project scope) | `... run spec-unit-tests --scope project` | 7 failed / 49 passed → **7 failed / 49 passed, same names** |
| `repository_unit` | `uv run --python 3.12 --with pytest --with pyyaml --with jinja2 --with hypothesis python -m pytest tests -q --ignore=tests/test_score_tools.py` | 10 failed / 1594 passed / 5 skipped → **10 failed / 1594 passed / 5 skipped, same ten names** (all pre-existing; listed in the evidence README) |
| `graphs: [cliWorkflow]` | `python3 skills/test-graph/scripts/run.py cliWorkflow` | **BUILD SUCCESSFUL**, exit 0 |
| `spec_graph: specWorkflow` | `python3 skills/test-graph/scripts/run.py specWorkflow` | **BUILD SUCCESSFUL**, exit 0, 9/9 nodes |

**Which spec-unit target I ran, and why it is spelled out.** `--ticket SI-06`
printed two `spec-unit target:` lines and executed only the first
(`specs/current`), returning on its non-zero exit — `SIS-KICKOFF-F-04` exactly,
reproduced here (`baseline-spec-unit-ticket-SI-06.txt`). I therefore ran both
targets explicitly with `--target` / `--scope` and report both rows above.

Ticket commit: `59142935639384257b6508b0d7555d44dbb3ae29`.

## Goal contribution

| Goal | Contribution | Expected effect | Measured local signal | Decided by |
| --- | --- | --- | --- | --- |
| `GOAL-blockers-propose` | direct | the section is present in every ticket PR of this epic; a wide-lane refusal case produces a proposal where the round of 2026-09-15 produced none | **Not run — no measurable movement recorded.** The wide lane is in a different repository (`haydenrear/skill-manager`, `specs/evals/harness`), its runner bills a `claude plugin eval` round (`EVAL_MAX_COST_USD=25`, concurrency 3), and pointing it at this checkout needs a `units-override.txt` that `git check-ignore` says is **not ignored** there — i.e. an uncommitted file in a repo outside this ticket's conflict keys. Reason, verification, and the exact command that would run it: `local-signal-GOAL-blockers-propose.md`; filed as `SI-06-DF-01` | SI-08 |
| `GOAL-epic-owns-the-model` | enabling | none — enabling only; it states the ticket-agent half of the boundary SI-07 enforces from the epic side | `N/A: the boundary is measured over ticket PRs by SI-08`. This PR is itself a data point for its second clause: **no file under `specs/` outside `results/` is in this diff** | SI-08 |

`GOAL-no-new-gates` is a guard on this ticket and is respected: every sentence
added says the section is advisory, required in shape, and never a gate on
merge. Nothing added a check, a validator, or a blocking condition.

## Deferred findings

| ID | Severity | Summary |
|---|---|---|
| `SI-06-DF-01` | minor | `GOAL-blockers-propose`'s `local_signal` is not an in-worktree command: the wide lane is in another repository, bills a round, and needs a `units-override.txt` that would dirty that repo |
| `SI-06-DF-02` | major | The worktree front door failed **and reported success**: `skt ticket new` → `bootstrap-home.sh` refused the home (`this home holds 15 skill(s) and an agent launched here can reach 12`), rolled the worktree back, and exited 0 |
| `SI-06-DF-03` | major | `bootstrap-home.sh` wrote `/specs/` into the clone's **shared** `.git/info/exclude` (and `/evals/` for wt-343), so every NEW file under `specs/` is invisible to `git status` / `git add -A` in every worktree — ticket evidence silently never reaches a PR |

**`SI-06-DF-03` is worth acting on before wave close, not at it.** Sibling wave-3
tickets are writing evidence under `specs/` right now, and `/evals/` is
excluded for SI-10 (#343) — whose own conflict-key directory that is. The
remedy each needs is one flag (`git add -f`); the fix is one guard in a script
SI-11 owns.

## Skill changes proposed

| Unit | What I hit | Proposed change |
| --- | --- | --- |
| `git-issue-workflow` (`scripts/bootstrap-home.sh`, `scripts/wt`) | `skt ticket new 339-skills-propose --base 994f650c --path ../wt-339-skills-propose` printed `error: this home holds 15 skill(s) and an agent launched here can reach 12`, rolled the worktree back, and still exited 0. The three unreachable units are exactly the three this epic moved into the plugin | **Not applied — `skills/*/scripts/**` is SI-11's conflict key.** Proposed: resolve a plugin-provided unit when projecting instead of reporting it missing; and never exit 0 from a run whose worktree was rolled back. Filed `SI-06-DF-02` with the verbatim output |
| `git-issue-workflow` (`scripts/bootstrap-home.sh`) | It wrote `/specs/` into the clone's shared `.git/info/exclude`, hiding all 13 of this ticket's evidence files from `git add -A` | **Not applied — SI-11's keys.** Proposed: guard `ensure_run_artifacts_ignored()` with `git ls-files --error-unmatch "$entry"` so a rule is never written for a path git already tracks, plus a selftest bootstrapping a worktree of a repo with a tracked top-level directory. Filed `SI-06-DF-03` |
| `spec-double-2` (`scripts/tla_spec_dev.py`) | `run spec-unit-tests --ticket SI-06` resolved both targets, executed only `specs/current`, and said nothing about the one it skipped — so the REQUIRED entry, as written, can only ever report project scope | **Not applied — outside my keys, and already filed as `SIS-KICKOFF-F-04`.** Proposed there: run every resolved target and aggregate the exit codes, or name the skipped targets. I worked around it with `--target` / `--scope` and said so in every row above |
| the epic's own plan (`goals[].local_signal`) | The declared local signal cannot be run from the worktree at all | **Not applied — plan data, the epic agent's.** Proposed: for a goal whose instrument lives in another repository, write `N/A: decided by <ticket> on the integrated tip`, or commit the `units-override.txt` convention the kickoff note already says the lane needs. Filed `SI-06-DF-01` |

Three of the four are blockers I was **forbidden to fix** — they sit in another
ticket's conflict keys — which is the behaviour this ticket's own new section
exists to make routine, and the reason the section says "blocked, reported, not
fixed" is a complete row.

## `home close-out` verdict

**Clean.** Run read-only, as the epic form requires:

```
skill-manager home close-out --home /Users/hayde/IdeaProjects/wt-339-skills-propose/.skill-manager \
                             --into /Users/hayde/IdeaProjects/tla-spec-dev/.skill-manager --json
→ {"safe": true, "exitCode": 0, "blockers": [], ...}  # 26 units, all "unchanged"
```

No blocking unit, nothing published with `unit publish`, no `home sync` into the
project home, worktree left standing. One caveat the epic agent should know when
it reconciles: this home was bootstrapped with **`--allow-unprojected`** and
reports *"3 of 15 skill(s) are not reachable from an agent launched here — this
home is NOT verified"* (`front-door-byhand-bootstrap.txt`). That is `SI-06-DF-02`,
not a change I made.

## Review input

**Hot spots**

- `skills/git-issue-workflow/references/epic-ticket.md` §3 and §6 — the model-ownership fork. §6 now begins "skip this whole section", which is the single most consequential sentence in this PR: read it against `planning_rules.model_ownership_rule` and against what **SI-07** writes on the epic side, since the two halves must agree and SI-07 has not landed yet.
- `skills/git-issue-workflow/SKILL.md` and `references/complete.md` §5a carry the canonical wording; the other seven files point at them. If the wording is wrong it is wrong in one place, by design.
- `skills/git-issue/references/epic-assignment.md` — I edited the **assignment renderer**. It is inside my conflict keys (`skills/git-issue/references/**`) and outside SI-07's (`skills/git-epic-workflow/**`), so there is no overlap, but it is the file most likely to want reconciling with SI-07 at wave close.
- No file in this PR is touched by a wave-3 sibling: SI-04/SI-05/SI-10/SI-11 keys are disjoint from mine, and I edited no `scripts/`.

**Decisions and overrides**

- **Did not run the declared `local_signal`**, and did not substitute one. Reasoning and the exact command are in the evidence; filed as a finding rather than silently omitted. Nobody asked me to skip it — this is the override.
- **Created the worktree by hand** (`git worktree add` + `bootstrap-home.sh --root … --allow-unprojected`) after the front door refused. This is the by-hand route `epic-ticket.md` §2 documents, and per that skill's own rule I am naming which of the four cases it was: **I found the front door, ran it, and it failed** — error quoted in `SI-06-DF-02`.
- **Used `git add -f`** to commit evidence, because `/specs/` is excluded in this clone (`SI-06-DF-03`). Without it this PR would have carried the skill edits and none of the evidence.
- **Ran `--target` / `--scope` instead of trusting `--ticket`**, and reported both targets separately rather than one summary line.
- Guardrails weakened: none. No test skipped, no matrix entry downgraded to `N/A` by me (the only `N/A` entries are the assignment's own), no gate forced, no `SKILL_GATES=off`.

**Where I'd look for bugs in my own change**

1. *Two `§5a` sections now exist* — one in `git-issue-workflow/references/complete.md` (implementer's half) and one in `git-issue/references/regression-close.md` (author's half). They must stay in step the way `## Goal contribution` already does. Cheapest check: diff the two column headers and the `none met` spelling; they are identical today.
2. *The §6 skip could be read too broadly.* An agent on an epic **without** a model-ownership rule must still close its ticket. I gated it on the rule being present, but the sentence is imperative and sits at the top of the section — worth one read by someone who has run an ordinary epic ticket.
3. *`epic-assignment.md` now tells the author to render a note "in place of" the `open ticket` line.* If SI-07 renders the same note from the epic side, a dispatched issue could carry it twice. Cheapest check: render one assignment after SI-07 lands and count the occurrences.
4. Suspicion only, not reproduced: `SI-06-DF-03`'s root cause. I measured the effect and the shared-file mechanism; I did **not** establish why the untracked snapshot selected `specs/` and `evals/`. Whoever fixes it should reproduce that first rather than trusting my account.

**Machinery friction**

- The front door cost the most: `skt ticket new` refused, rolled back, and exited 0, so the failure had to be diagnosed from a log rather than from a status (`SI-06-DF-02`).
- `.git/info/exclude` carrying `/specs/` cost the least time and was the closest call — I found it only because `git status --porcelain` showed no untracked files after I had written twelve. One flag recovered it; an agent that ran `git add -A` and moved on would have shipped an evidence-free PR and never known (`SI-06-DF-03`). It bites a second way, worth knowing before you hit it: `git add specs/results/deferred_findings_final.yaml` on an **already-tracked** file is refused outright (`The following paths are ignored by one of your .gitignore files: specs`), and the refusal aborts the whole `git add` invocation, so a staging command that names both a skill file and a spec file stages *neither*.
- `run spec-unit-tests --ticket <id>` silently running one of two resolved targets cost a re-run and a careful reading of the output (`SIS-KICKOFF-F-04`, reproduced).
- The declared local signal not being runnable from the worktree cost the time it took to establish that it is not (`SI-06-DF-01`).
- **I changed nothing inside my Skill Manager home.** The close-out gate reports 26 units, every one `unchanged`, so there is nothing in that home for the epic agent to reconcile — but it was bootstrapped unverified, as noted above.


---

## Reconciled onto the epic tip (2026-09-18)

This branch was reconciled **twice**, as wave-3 siblings landed ahead of it in
the promotion lane. **Merged both times, never rebased** — the branch is
published under this PR and a rebase would rewrite the sealed evidence commit
beneath it.

| | onto | after | rows |
|---|---|---|---|
| first | `56c7658f` | SI-04 (#353), SI-05 (#354) | 52 |
| second | `93dd3fac` | SI-10 (#355) | **53** |

Each time the same single path conflicted —
`specs/results/deferred_findings_final.yaml` — because four wave-3 branches each
appended to the end of one cumulative append-only ledger from the same 45-row
base. Resolved both times by **keeping every row from both sides**:

```
45 shared + SI-04's four (SI-04-DF-01..04) + SI-10's one (SI-10-DF-01)
          + SI-06's three (SI-06-DF-01..03)  =  53 rows
```

Nothing renumbered, nothing re-templated, no pre-existing row touched. The
resolution is deterministic rather than hand-merged: the tip's file was first
proven a pure tail-append over the base (its first 2678 lines byte-identical),
and SI-06's block was re-derived from this branch's pre-reconcile commit
`59142935`, whose file is base + SI-06 only.

**Verified with SI-10's stricter check, not a row count** — a count alone cannot
catch a swap:

```
diff <(git show <parent>:<file>) <file> | grep -c '^<'   →  0 against BOTH parents
```

plus 53 rows, 53 unique ids with no duplicates, zero conflict markers, the YAML
parsing (`uv run --with pyyaml`; plain `python3 -c "import yaml"` fails in these
worktrees), and my ten skill files and the SI-06 evidence directory
byte-identical to the pre-reconcile head.

Suites: the five that read the backlog were re-run after the first reconcile —
**60 passed, 5 skipped, identical to the pre-merge baseline by name**
(`premerge-backlog-tests.txt`, `postmerge-backlog-tests.txt`). Not re-run after
the second: a YAML append cannot reach them, and this ticket's evidence was
already verified (0 new failures by name, both graphs green).

Head: `12fb074dd421ccee090b60db87e07c244326a61b`, verified present on GitHub via
`gh api` rather than on `origin` (`SI-04-DF-04`).

Two notes for whoever merges, neither actionable by this agent:

- **DCO fails on this PR**, which is what makes it `UNSTABLE`. Neither commit
  carries a `Signed-off-by` trailer. The tool's own remedy is a rebase, which
  would rewrite the sealed evidence commit — so this is the epic owner's call.
  Note the already-merged #353 and #354 fail the same check, so it is not
  specific to this branch.
- **`SI-06-DF-03`'s repair has reached this worktree**: `/specs/` is no longer in
  the clone's shared exclude, and new evidence files now appear as untracked
  normally — the two re-run logs above were added without `-f`.

