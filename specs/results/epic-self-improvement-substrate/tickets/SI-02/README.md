# SI-02 evidence — nest the five workflow skills, retire the standalone installs

Branch `feature/335-nest-workflow-skills`, base `28ecf7e1`. Issue #335, epic #333.

## What was measured, and against what

Every suite was run **before the first edit** on the pinned base and again at the
end, and compared by failure **NAME**, never by count (wave-1's rule).

| suite | how it was run | before | after | new | fixed |
|---|---|---|---|---|---|
| repository unit tests | `pytest tests -q --ignore=tests/test_score_tools.py` | 10 failed, 1563 passed | 10 failed, 1563 passed | **0** | 0 |
| spec-unit, project | `run spec-unit-tests --target specs/current` | 7 failed, 49 passed | 7 failed, 49 passed | **0** | 0 |
| spec-unit, ticket | `run spec-unit-tests --target specs/tickets/SI-02/desired` | 7 failed, 46 passed | 7 failed, 46 passed | **0** | 0 |

`--target` was used deliberately instead of `--ticket SI-02`. `SIS-KICKOFF-F-04`
records that `--ticket` resolves two targets and executes only the first, so the
ticket workspace would have been listed but never run. Both targets were run
here, separately, and both are reported above.

Graphs, all three green:

| graph | result |
|---|---|
| `specWorkflow` | BUILD SUCCESSFUL |
| `cliWorkflow` | BUILD SUCCESSFUL |
| `effectProviderExamples` | BUILD SUCCESSFUL |

## The nesting itself

`git subtree add --prefix=skills/<name> <remote> main`, full history, no
`--squash`, per the owner's decision in `../../migration/pulling-upstream.md`.

- **Zero** gitlinks (`git ls-tree -r HEAD | awk '$1=="160000"'` is empty).
- **Zero** stray `.git` under `skills/`.
- Each nested tree is **byte-identical** to its upstream `main` tree.
- The two commits that existed only in the gitignored project home —
  `git-issue 1f91074b`, `git-issue-workflow 4eeb350d` — were confirmed
  ancestors of each remote's `main` with `git merge-base --is-ancestor`
  **before** nesting, and are present after it by content and as ancestors of
  HEAD.

## The three classes of address that had to move

| class | count | verified |
|---|---|---|
| `skill-imports` naming a contained skill as a UNIT | 14 | 0 remain |
| `skill_references` git coords naming a bundled repo | 12 | 0 remain |
| hardcoded `$SKILL_MANAGER_HOME/skills/<unit>/` store paths | 47 | 0 remain |

`verify-repository-scoped.txt` is the replication of verify.sh's own two checks,
scoped to files this PR can own, and says 0 / 0.

## GOAL-one-unit, local signal

`local-signal-GOAL-one-unit.txt`. On this worktree's home: **6 standalone units
→ 1 plugin**, six contained skills on disk, and `show test-graph` answers
`unit not found`, which is the contained-skill semantics working. `skt check`
went from 3 notifications to 1, and the remaining one is an unrelated
skill-manager point release.

`expected_effect` was "installed units belonging to this substrate go from 6 to
1 in both home tiers". Met in the tier this ticket owns. The root and project
tiers are the epic agent's at wave close — this ticket changed no home but its
own, as the assignment requires.

## Files

| file | what it is |
|---|---|
| `repository-suite-{BEFORE,AFTER}.txt` | full pytest runs |
| `spec-unit-*-{BEFORE,AFTER}.txt` | both spec-unit targets, both ends |
| `failures-*-{BEFORE,AFTER}.txt` | sorted failure NAME sets, the thing compared |
| `graph-*.txt` | the three graph runs and their discovers |
| `verify-sh.txt` | verify.sh before the home migration — FAILED, see SI-02-DF-01 |
| `verify-sh-after-migration.txt` | verify.sh after — could not run, see SI-02-DF-05 |
| `verify-repository-scoped.txt` | the same two checks, scoped to files this PR owns: 0 / 0 |
| `local-signal-GOAL-one-unit.txt` | the home migration, 6 → 1 |
| `plugin-install.txt` | the successful plugin install from a clean stage |
| `skt-after-migration.txt` | `skt status` / `skt check` on the migrated home |

## Deferred findings raised here

`SI-02-DF-01` verify.sh scans the gitignored home, sealed evidence, and its own
prescribed rewrite, so it cannot go green. `SI-02-DF-02` a selftest fixture
enumerates only the standalone store layout. `SI-02-DF-03` the wide eval lane
the issue's metric names does not exist in this home. `SI-02-DF-04`
`install file://<checkout>` recurses into the checkout's own home.
`SI-02-DF-05` `git-integration-repo`'s `integration-lib.sh` has no plugin rung,
so verify/refresh/propagate stop working in a migrated home.

## `home close-out` verdict

```
skill-manager home close-out --home <worktree>/.skill-manager \
                             --into /Users/hayde/IdeaProjects/tla-spec-dev/.skill-manager
```

Exit 1, and the content is the migration itself rather than a problem:

- `would-create plugin:tla-spec-dev` — the bundle, which only this home has.
- `would-update plugin:skt` — destination clean and contained in the source, so
  it holds nothing of its own.
- six `removed-upstream skill:{discovery,git-epic-workflow,git-issue,git-issue-workflow,spec-double-compiler,test-graph}`
  — left in place, because "deleting a unit is not what a sync is for". Those
  six are precisely what this ticket retired in its own home.

**2 unit(s) would be lost if this worktree home were removed now.** The remedy
it prints is `home sync --from <worktree home> --to <project home>`, and this
ticket deliberately did **not** run it: the assignment reserves reconciliation
of every worktree home to the epic agent, in serial, at wave close. Flagged here
so that reconciliation is not a surprise — the project and root homes still
carry the six standalone units and still need the README sequence run against
them.
