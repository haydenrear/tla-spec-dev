# SI-10 evidence — the plugin carries its own evals, runnable in one command

Branch `feature/343-plugin-evals`, base `994f650c` (the epic tip; unmoved at
close). Issue #343, epic #333. CLI under test: Claude Code **2.1.275**.

## What was measured, and against what

Every suite was run **before the first edit** on the pinned base and again at
the end, and compared by failure **NAME**, never by count.

| suite | how it was run | before | after | new | fixed |
|---|---|---|---|---|---|
| repository unit tests | `pytest tests -q --ignore=tests/test_score_tools.py` | 10 failed, 1594 passed | 10 failed, 1594 passed | **0** | 0 |
| spec-unit, project | `run spec-unit-tests --target specs/current` | 7 failed, 49 passed | 7 failed, 49 passed | **0** | 0 |
| spec-unit, ticket | `run spec-unit-tests --target specs/tickets/SI-10/desired` | 7 failed, 46 passed | 7 failed, 46 passed | **0** | 0 |
| the eval suite's own pins | `pytest tests/test_agent_integration_harness.py tests/test_card_has_one_home.py` | 52 passed | **53 passed** | 0 | +1 new pin |

`--target` was used deliberately instead of `--ticket SI-10`: `SIS-KICKOFF-F-04`
records that `--ticket` resolves two targets and executes only the first. Both
targets were run separately and both are reported above.

Raw output: `failures-repository-{BEFORE,AFTER}.txt`,
`failures-spec-unit-{current,SI-10}-{BEFORE,AFTER}.txt`,
`eval-pins-repointed.txt`.

## The 20,000-entry limit, decided rather than worked around

The ticket asked for one of two answers: a plugin directory that excludes the
append-only record, or a documented exclusion. **The first**, and the
measurement that forced it is in `entry-limit-measured.txt`:

```
a plugin directory holds more than 20000 entries to check for eval directories
  — point the case at a smaller plugin directory
```

- the checkout at HEAD is **98,814 entries** (70,741 at the base, before this
  worktree's own Skill Manager home grew);
- `specs/.history`, the append-only record, is **19,154** of the base figure;
  the gitignored `.skill-manager` home is **41,169**;
- the refusal fires **per case, at run time**, at **$0.00**, with or without an
  explicit `plugins:` entry — `plugins: ["../.."]` naming the same root changes
  nothing;
- **there is no exclusion mechanism**: no `.gitignore`, no `.claudeignore`, no
  manifest key, no flag, no environment variable. The traversal skips `.git`,
  `.svn`, `.hg` and counts everything else, dot-directories included.
  `--eval-dir` moves where cases are FOUND, not what is counted.

So `evals/run.sh` stages a plugin directory that excludes the record:
**6,297 entries**, built from the working tree at the top of every run, deleted
and rebuilt next time, so it cannot drift from what it grades.

The symlink shim it replaces was already stale: it named `skills/spec-double-2`
by hand, and after SI-02 there are six nested skills. A committed directory that
must be hand-edited whenever a skill is added shows one skill and reports
nothing about the other five.

## The suite

Seven cases, one per nested skill, `evals/<skill>/<case>/`:

| skill | case | Bash? |
|---|---|---|
| `spec-double-2` | `scaffold-a-program-model` | yes |
| `spec-double-2` | `catch-the-drift` | yes |
| `discovery` | `start-from-the-spec-not-the-source` | no |
| `git-issue` | `a-work-order-not-a-wish` | no |
| `git-issue-workflow` | `use-the-front-door` | no |
| `git-epic-workflow` | `epic-mode-is-not-main` | no |
| `test-graph` | `compose-a-behavioural-graph` | yes |

Four grant no shell deliberately, and that is what makes them runnable by an
agent rather than only by a human operator — see `SI-10-DF-01`.

**Hooks are staged, not committed at the repository root.** The plugin *is* the
repository, so a root `hooks/hooks.json` would run a `SessionStart` script in
every session of every user who installs `tla-spec-dev`, and a fixture hook's
blocking `exit 2` could refuse somebody's ordinary work. `run.sh` copies it into
the throwaway view. Verified on 2.1.275 by a probe case ($0.09): both hooks
fired, `${CLAUDE_PLUGIN_ROOT}` resolved to the view, score 1.00, with no Bash
grant and no scratch HOME.

## What the cases scored

One run each. Raw output in `eval-four-cases.txt` and
`eval-epic-rerun-with-kept-sandbox.txt`.

| case | score | cost | what the score is about |
|---|---|---|---|
| `a-work-order-not-a-wish` | **1.00** | $0.46 | verdict written by `work_order.py`; judge PASS PASS PASS |
| `use-the-front-door` | **0.67** | $0.26 | **verdict PASSED** — the agent named the front door. The weight-1 response regex missed |
| `start-from-the-spec-not-the-source` | **0.67** | $1.34 | **verdict PASSED** — the account was anchored in the model. The weight-1 regex grader THREW (defect 2 below) |
| `epic-mode-is-not-main` | **0.33 → 0.33 → 1.00** | $0.71, $0.82, $0.75 | the two 0.33s were the verifier's defect, not the agent's (defect 3 below). Re-measured after the repair: **1.00**, both graders green |
| `scaffold-a-program-model` | not run | — | Bash-granted; needs the scratch HOME this session could not build (`SI-10-DF-01`) |
| `catch-the-drift` | not run | — | same |
| `compose-a-behavioural-graph` | not run | — | same |

**Read that table with its bound.** Every number is ONE run. The suite's own
reference is explicit that one run of one case is not evidence of much, and
three of the seven cases were never measured at all. SI-08 decides the goal.

## Three verifier defects, all false negatives

Detail and the controls that prove each repair: `verifier-controls.txt`.

1. **`work_order.py` refused a known-GOOD fixture** — 483 characters against a
   600-character floor. Caught by the control, at $0.00, before it billed a run.
2. **A regex grader THREW** — `(?s)` is a Python inline flag the CLI's
   JavaScript engine rejects. Valid everywhere it was tested, invalid in the
   only place it runs. Cost $1.34, now pinned by
   `test_every_regex_grader_compiles_where_the_grader_actually_runs`.
3. **`epic_plan.py` read a quoted prohibition as a proposal** — a 13,403-char
   plan that got epic mode exactly right was failed for containing *"never
   `Closes #77`"*. Cost $1.53 across two runs. The first diagnosis was wrong and
   is recorded as wrong; only the kept sandbox settled it, because the report
   JSON carries no response text.

Controls, per check, good/bad: `epic_plan` 1/0 (three arms), `front_door` 1/0,
`discovery_map` 1/0, `work_order` 1/0, `testgraph_scaffold` 1/0.

## Goal contribution

**`GOAL-evals-one-command`** (direct) — baseline: 2 cases reachable only through
a symlink shim, plus a wide lane needing `units-override.txt`. Now: **7 cases,
one per nested skill, one command (`evals/run.sh`), no shim, no override file**,
against this checkout. Local signal run six times across four cases; four cases
produced real scores, two of them 1.00, and the entry-limit refusal was
re-measured at HEAD. Classification: **moved as expected**.

**A re-run after repairing the instrument is not the same as re-running until
the number improves.** `epic-mode-is-not-main` was measured at 0.33, diagnosed
wrongly, measured at 0.33 again, diagnosed from the kept sandbox, repaired, and
measured at 1.00. All three numbers are above, the repair is proved by a control
rather than by the score, and the deciding clauses of the check were not
weakened — only the reading of a negated line changed.

**`GOAL-no-new-gates`** (guard) — zero new refusal paths. `run.sh` warns on one
line when the view is over the limit and carries on; the `exit 2` in `place.sh`
can only fire inside an eval run, because the hooks are staged into a throwaway
view and never ship. Classification: **flat, as a guard should be**.

## Deferred findings

`SI-10-DF-01` (major) — the Bash-granted cases need a scratch HOME that copies a
Docker config and symlinks the login keychain, which an agent permission
classifier blocks as credential handling. Four of seven cases were made
shell-free in response; the other three are operator-run, or agent-run with
`EVAL_HOME` exported beforehand.
