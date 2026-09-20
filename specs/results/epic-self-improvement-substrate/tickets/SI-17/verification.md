# SI-17 — what was run, and what each run establishes

Base `d4c91275` (see *Base* below — it is NOT the `afa4addd` the brief named).
Every number here was read from the run's own output, with the process exit code
taken **directly** and never through a pipe.

## Base: the brief is wrong about the base, and the measurement wins

The brief and the assignment block both say `base_sha:
afa4addd17faa1ef05c4c41a3fcfd36a02ce92df`. At dispatch
`origin/epic/self-improvement-substrate` was already one commit further on, at
`d4c91275` ("run-graphs: --only can reach an OPT-IN graph"). The same assignment
also says to start "from the latest `origin/epic/self-improvement-substrate`".
Those two instructions disagree, so this worktree took the published tip —
`d4c91275`, a strict descendant of `afa4addd` on the same branch. Stated here
because every baseline below was measured at `d4c91275` and not at `afa4addd`.

## The move

Four tracked paths, all by `git mv` so history follows them:

| from | to |
|---|---|
| `skills/git-issue-workflow/scripts/wt` | `skills/skt/scripts/wt` |
| `skills/git-issue-workflow/src/git_issue_workflow/wt.py` | `skills/skt/src/skt/wt.py` |
| `skills/git-issue-workflow/.github/scripts/wt_smoke.sh` | `skills/skt/.github/scripts/wt_smoke.sh` |
| `skills/git-issue-workflow/tests/test_wt_wrapper.py` | `skills/skt/tests/test_wt_wrapper.py` |

The fourth was **not** in the issue's list of three. It is the suite whose only
subject is `wt.py`; leaving it behind would have left git-issue-workflow running
pytest against a module it no longer ships. Reported as a scope correction
rather than done silently.

`git ls-files -s` after the move confirms the executable bits survived:
`100755` on `wt` and on `wt_smoke.sh`, `100644` on the two Python files.

## The part that is NOT a move, and is the whole risk

`wt` sources `lib.sh` and dispatches to `new-change.sh` / `close-change.sh`.
Those three did **not** move — they hold the policy, and git-issue-workflow owns
it. So `wt` gained a resolver (`$GIT_ISSUE_WORKFLOW_SCRIPTS`, then the checkout
sibling, then `skills/` and `plugins/*/skills/` in a home), and `lib.sh` gained
`wt_bin()` so that the `CLOSE` key and four `FIX` lines stop spelling a front
door that moved. `WORKTREE_LIB_ABI` 1 → 2 for the new function.

## Failure sets compared by NAME, not by count

| suite | base `d4c91275` | this branch | verdict |
|---|---|---|---|
| repository unit (`pytest tests`, `--ignore=test_score_tools.py`) | 10 failed / 1710 passed / 8 skipped | 10 failed / 1710 passed / 8 skipped | **identical set of 10 names**, diffed |
| `skills/skt/tests` | 307 passed / 3 skipped, rc 0 | 325 passed / 3 skipped, rc 0 | +18 = the moved wrapper suite, intact |
| git-issue-workflow wrapper suite | 18 passed, rc 0 | *(unit ships no Python)* | subject moved to skt |
| `wt_smoke.sh` | 25 passed / 0 failed, rc 0 | 25 passed / 0 failed, rc 0 | unchanged from its new location |
| spec-unit `--ticket SI-17` | rc 1, 7 failed / 49 passed | rc 1, 7 failed / 49 passed | identical (diff empty but for runtime) |
| `check_units.py --root .` | rc 1, 3 problems | rc 1, 3 problems | **identical set**, diffed; all 3 pre-existing |
| `cliWorkflow` graph | rc 0, BUILD SUCCESSFUL | rc 0, BUILD SUCCESSFUL | unchanged |
| shellcheck (both CI spellings) | — | rc 0 / rc 0 | clean |

The ten repository failures were diffed as sorted name lists, not compared as a
number; the diff is empty. The three `check_units` problems were diffed the same
way. None of the three is this ticket's: two are eval fixtures malformed on
purpose, and the third is `skills/skt/skill-project.toml`, which SI-16 left
without a `[project]` table (filed here as SI-17-DF-02).

## The PATH, not the exit code

`wt info` on a real fixture worktree, reading the emitted key rather than a
return value:

```
CLOSE      /…/wt-366-wt-into-skt/skills/skt/scripts/wt close KEY-2
```

- the key's **first token** is executable on disk — `test -x`, after `awk
  '{print $1}'`. (The first attempt at this check ran `test -e` against the
  whole `"<path> close KEY-2"` string and reported a false FAILURE; the check
  was wrong, not the product, and it was re-run rather than reported.)
- it names `skills/skt/scripts/wt`;
- **negative control**: `test -x` on the retired
  `skills/git-issue-workflow/scripts/wt` is false, so the assertion above is not
  vacuous.

## Negative control: seen to fail

`wt` copied to a scratch directory with no git-issue-workflow sibling, `HOME`
redirected to an empty tree and `SKILL_MANAGER_HOME` / `GIT_ISSUE_WORKFLOW_SCRIPTS`
unset:

```
exit=1
error: git-issue-workflow's scripts/ could not be resolved — `wt` is the front
door, but new-change.sh, close-change.sh and lib.sh are the lifecycle, and they
are not beside it
fix: GIT_ISSUE_WORKFLOW_SCRIPTS=/path/to/git-issue-workflow/scripts /…/wt
```

Refused, named the cause, and offered a runnable override.

## The rung real installs use

The checkout sibling is the easy rung and the one the smoke exercises. The rung
an installed home actually takes is `plugins/*/skills/` — skt and
git-issue-workflow are both CONTAINED skills. Measured separately: `wt` copied
to a directory with **no** sibling (`sibling rung present? no`), a fake home
carrying git-issue-workflow only at
`plugins/tla-spec-dev/skills/git-issue-workflow/scripts`:

```
exit=0
created worktree /…/repo-PLUG-1
```

So both the standalone-absent and contained-present case resolve.

## Acceptance

1. **No caller resolves `wt` at its git-issue-workflow path.** Swept over all
   25,846 tracked files, excluding `specs/results` and `specs/.history`
   (evidence archives) and `specs/desired_program_model` + `specs/tickets` (the
   epic agent's plan, which still describes the move in the future tense and is
   not a ticket agent's to edit). **One hit remains**:
   `PORTS-AS-ADAPTERS-STARTER-PROMPT.md:51`, a dated starter prompt for a closed
   2026-08 epic that also names `~/.claude/skills/`, a home layout that has not
   existed for several epics. Left as the historical record it is.
   *Negative control for that sweep*: the same pattern returns 5 hits inside
   `skills/skt/scripts/wt`, so the pattern and path scope do match real content.
2. **Card bodies**, pinned instrument, `awk` frontmatter-stripped:

   | card | SI-09 | now | delta |
   |---|---|---|---|
   | discovery | 996 | 996 | +0 |
   | git-epic-workflow | 1820 | 1820 | +0 |
   | git-integration-repo | 1343 | 1349 | +6 |
   | git-issue | 1499 | 1499 | +0 |
   | git-issue-workflow | 1775 | 1788 | +13 |
   | plugin-repository | 1466 | 1472 | +6 |
   | spec-double-2 (control) | 1499 | 1499 | +0 |
   | test-graph | 1332 | 1332 | +0 |
   | **total** | **11730** | **11755** | **+25** |

   `skt` is not in SI-09's table (SI-16 added it): 2214 at this ticket's base →
   **2242**, +28.

   **The control disagrees with the brief, and the brief is wrong.** The brief
   pins `spec-double-2 = 1,839`. SI-09's own `word-counts-AFTER.txt` records
   1839 as the **before** and 1499 as the **after** of its own cut. The
   instrument reproduces 1499 exactly. 1,839 is a pre-SI-09 number quoted as if
   it were current.

   The +25/+28 is stated rather than waved through. A first pass measured +113
   on git-issue-workflow and +70 on skt; that is the wrong direction for a
   *guard* goal, so the explanatory prose was moved into
   `references/worktrees.md`, which the instrument does not count and which is
   where the resolver spelling already lived. What remains on the cards is the
   one fact a reader cannot derive: which unit ships `wt`.
3. **`wt_smoke.sh` runs from its new location** — 25 passed / 0 failed, rc 0
   taken directly.

## Boundaries

- Root home `/Users/hayde/.skill-manager` **not modified**: `plugins/` mtime
  `Sep 20 14:10:26`, before this ticket started.
- `skills/skill-manager/` — **0 files changed**. The skill-manager repository
  was not touched; SI-18 owns it.
- `close ticket`, `close_tickets.py`, `open ticket`, `--accept-new`: none run.
  `specs/` carries no change from this ticket.
- **Home close-out: nothing to close out.** This worktree has no
  `.skill-manager` — the front door was broken at dispatch (SI-16-DF-00), so it
  was created with `git worktree add` by hand and no ticket-local home was ever
  bootstrapped.

## For SI-18: the invocation path DID change

`GitHistoryInternal.tla:251` in the skill-manager repository carries
`@command wt close / skt ticket close`. **The command spellings are unchanged** —
`wt close <T>` and `skt ticket close <T>` both still work and mean the same
thing. What changed is the **path** `wt` resolves at:

- was `$SKILL_MANAGER_HOME/{skills,plugins/*/skills}/git-issue-workflow/scripts/wt`
- now `$SKILL_MANAGER_HOME/{skills,plugins/*/skills}/skt/scripts/wt`

Any citation that names the *command* is still correct. Any that names the
*path* needs the unit swapped.
