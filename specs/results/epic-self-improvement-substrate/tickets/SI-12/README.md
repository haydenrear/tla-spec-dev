# SI-12 evidence — nest git-integration-repo and plugin-repository, and make one unit true

Branch `feature/359-nest-remaining-dependents`, base `9a06cdeb`. Issue #359, epic #333.

## What was measured, and against what

Every suite was run **before the first edit** on the pinned base and again at the
end, compared by failure **NAME**, never by count.

| suite | before | after | new | fixed |
|---|---|---|---|---|
| repository units | 10 failed, 1645 passed, 6 skipped (381.35s) | 10 failed, 1647 passed, 6 skipped (359.79s) | **0** | 0 |
| spec-unit `--target specs/current` | 7 failed, 49 passed | 7 failed, 49 passed | **0** | 0 |
| spec-unit `--target specs/tickets/SI-12/desired` | 7 failed, 46 passed | 7 failed, 46 passed | **0** | 0 |

The ten baseline repository failures matched the ten named in the work order
**exactly, name for name, with no extras**, so the comparison set is the known
set. The +2 passed is `tests/test_plugin_layout_resolution.py` parametrising
over 8 contained skills instead of 6 — the two this ticket added.

`--target` was used deliberately instead of `--ticket SI-12`: `SIS-KICKOFF-F-04`
records that `--ticket` resolves two targets and runs only the first. Both
targets were run separately and both are reported.

## Graphs: unmeasurable in a ticket worktree, and that is pre-existing

All three declared graphs — `specWorkflow`, `cliWorkflow`,
`effectProviderExamples` — fail in ~400ms with

    Included build '.../test_graph/build-logic' does not exist.

`test_graph/settings.gradle.kts:2` declares `includeBuild("build-logic")`;
`test_graph/.gitignore:30` ignores `/build-logic`; `git ls-files
test_graph/build-logic` returns **zero** files. The directory exists in the main
working tree and cannot exist in a fresh worktree.

**Control run, because "it failed" is not attributable on its own:** a detached
throwaway checkout at the pinned base `9a06cdeb` reproduces the identical
failure in 447ms (`graph-specWorkflow-AT-BASE.txt`). So this is **not caused by
SI-12**. Filed as `SI-12-DF-05`. The honest graph verdict for this ticket is
*unmeasurable here*, not *green* and not *regressed*.

## The nesting itself

`git subtree add --prefix=skills/<name> <remote> main`, FULL history, no
`--squash`, per the owner's decision in `../../migration/pulling-upstream.md`.

- Both nested trees **byte-identical to their upstream `main` trees**
  (`bdd764a7`, `ed25bd9d`) — `nesting-verification.txt`.
- **Zero** gitlinks, **zero** stray `.git` under `skills/`.
- **70 commits** added over base = 61 + 7 + 2 subtree merges. **Zero** squash.
- Before nesting, both upstream tips were confirmed clean and fully pushed in
  *both* the root home and the project home checkouts, so nesting reverted no
  home-only work (the check SI-02's "the one thing that must not be lost"
  prescribes).
- The mechanics were rehearsed in a throwaway repo first. That rehearsal's
  byte-identity assertion initially printed DIFFERENT because zsh does not
  word-split `$pair` — a broken check, re-run correctly before being believed.

`skills/` now carries 8 contained skills; `integration.toml` lists 7
constituents (`spec-double-2` is bundle-owned and deliberately not one).

## The classes of address that had to move

Measured with a Python sweep over **all 1348 tracked files under `skills/`**,
carrying an explicit non-vacuity assert:

| class | result |
|---|---|
| `skill-imports` naming a contained skill as a UNIT | **0 remain** |
| coords naming a bundled repo, in scope | **0 remain** |
| standalone-only store paths under `scripts/` | **0** — `layout-test-AFTER.txt`: 9 passed |
| standalone-only store paths in ALL tracked files | 10 lines remain, none in scope — `SI-12-DF-01/-02/-03` |

**Two earlier versions of this sweep were vacuous, and that is recorded here
rather than quietly fixed.** A zsh glob (`skills/*/skill-scripts`) matched
nothing, aborted the enclosing `find`, and the loop reported "none" having
scanned zero files — the layout test then found two real offenders it had just
declared clean. A second attempt died with `awk: giving up` on every file from
nested-quote mangling. Both were no-results presented as clean results, which is
this epic's named recurring defect. The numbers above come from the Python sweep
with the assert.

## SI-02-DF-05: CLOSED

`integration-lib.sh` resolved `git-issue-workflow`'s `lib.sh` at the standalone
path only, with zero `plugins/*/skills` rungs, so it refused at source time once
that skill was contained — taking `verify.sh`, `refresh.sh`, `propagate.sh` and
every `plugin-repository` script with it. It now has rung 2 and resolves:

    SOURCED OK -- lib resolved:
      .../.skill-manager/plugins/tla-spec-dev/skills/git-issue-workflow/scripts/lib.sh

Verified **behaviourally**, not by reading: with only the plugin rung present it
resolves there; with both present the standalone rung still wins, preserving the
documented precedence. Two idioms were avoided deliberately, both measured
broken in wave 2 — brace expansion does not happen inside double quotes, and
`ls -d | head -1` sorts and inverts the precedence. Every rung added here is an
explicit loop with `break`.

## SI-02-DF-01: NOT closed — measured, not assumed

The issue said nesting *may* close it and "do not assume it does — measure and
say." It does not.

`verify.sh` now **runs** (that is DF-05's fix working; previously it died at
source time) and still exits **1 / FAIL**. It reports 1666 `skills/` lines, of
which **1147 are inside the gitignored `.skill-manager/`** — DF-01's cause (a),
scanning the home, is untouched by anything this ticket did. Causes (b) sealed
evidence and (c) flagging its own prescribed rewrite are likewise unaffected.

`verify-sh.txt`. DF-05 unblocked verify.sh from running; DF-01 remains open.

## GOAL-one-unit, local signal

`expected_effect`: *standalone copies re-materialised by non-member dependents go
from 3 to 0; no external importer of any contained skill remains.*

**Met in the tier this ticket owns.**

| | before | after |
|---|---|---|
| contained skills with a NON-MEMBER importer | 3 (`test-graph`, `spec-double-compiler`, `git-issue-workflow`) | **0** |
| importers doing it | `git-integration-repo`, `plugin-repository` | none — both are now members |
| contained skills in the home's standalone `skills/` | — | **0 of 8** |
| contained skills in the plugin | 6 | **8** |

All eight contained skills now answer `deps <unit> --who-imports` with *"nothing
imports it directly — 0 unit(s) in total"*. `local-signal-BEFORE.txt` and
`local-signal-GOAL-one-unit.txt`.

Root and project home tiers are the epic agent's at wave close; this ticket
changed **no home but its own**.

## Model ownership

`specs/tickets/SI-12/`, `specs/current`, `specs/desired_program_model` and
`specs/program_model` are **untouched**. No `open ticket`, `close ticket`,
`close_tickets.py` or `--accept-new` was run. The scaffolded `desired` needed no
correction: this is bundle membership and import addressing, with no TLA+
action, state or invariant change.

## Operator homes

The root home `/Users/hayde/.skill-manager` was **not modified** — `installed/`
dated Sep 13, `units.lock.toml` Sep 17, both predating this session — and still
deliberately carries all eight standalone units. No `skt publish`, no
`home sync`, no write to the project home.

`home close-out` exits 1: five `removed-upstream` skills left in place
("deleting a unit is not what a sync is for") and `plugin:tla-spec-dev` as **1
unit that would be lost** if this home were removed now. The remedy it prints is
`home sync`, which this ticket deliberately did **not** run — the assignment
reserves home reconciliation to the epic agent, in serial, at wave close.

## Files

| file | what it is |
|---|---|
| `repository-suite-{BEFORE,AFTER}.txt` | full pytest runs |
| `failures-{BEFORE,AFTER}.txt` | sorted failure NAME sets — the thing compared |
| `spec-unit-*-{BEFORE,AFTER}.txt`, `failures-spec-unit-*` | both spec-unit targets, both ends |
| `graph-*.txt` | the three graph failures |
| `graph-specWorkflow-AT-BASE.txt` | the control proving they fail at the base too |
| `nesting-verification.txt` | byte-identity, gitlinks, history arithmetic |
| `store-path-sweep-AFTER.txt` | store paths, imports and coords, with the non-vacuity assert |
| `layout-test-AFTER.txt` | `tests/test_plugin_layout_resolution.py` — 9 passed |
| `local-signal-{BEFORE,GOAL-one-unit}.txt` | `deps --who-imports`, both ends |
| `verify-sh.txt` | verify.sh — runs now, still FAIL (SI-02-DF-01) |
| `plugin-install.txt`, `step-{uninstall,install}.txt` | the home migration, including its false start |

## Deferred findings raised here

`SI-12-DF-01` four prose sites in git-issue-workflow still naming the standalone
store path. `SI-12-DF-02` six further matches triaged as NOT defects (quoted
transcripts and warnings), recorded so nobody re-triages them.
`SI-12-DF-03` the layout guard scans only `scripts/`, so markdown and TOML
carrying the same broken resolver are invisible to it — 10 lines it cannot see.
`SI-12-DF-04` `discovery/skill-project.toml:74` still declares a coord naming a
contained repo, the silent-duplicate class. `SI-12-DF-05` the three declared
graphs cannot run in any ticket worktree. `SI-12-DF-06` `install` refuses to
replace an installed plugin and `remove` rejects `--yes`, so the documented
re-install path silently no-ops.
