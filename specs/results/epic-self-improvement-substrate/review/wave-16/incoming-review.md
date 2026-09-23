# Incoming review — what skill-manager pushed to the plugin, and PR #397

Reviewed 2026-09-23 by the epic agent, on `epic/self-improvement-substrate`
at `6b89943f`. Two separate things arrived and they need separating:

1. **13 commits pushed directly to `tla-spec-dev-plugin/main`** — now pulled.
2. **skill-manager PR #397**, `feature/si18-adopt-unified-plugin` →
   their `epic/self-improvement-substrate`. OPEN, MERGEABLE, deliberately held.

---

## The pull

Fast-forward `2a9fef7c..6b89943f`, 23 files, `+1080/−138`. **Zero overlap**
with the 49 files waves 13–15 touched, so nothing of mine was rewritten and
nothing needed reconciling. Tree clean; the branch is byte-identical to
`tla-spec-dev-plugin/main`.

| check | result |
|---|---|
| skt's own suite | **327 passed, 3 skipped** (was 325/3 — their `test_status.py` adds 2) |
| `run-graphs.py --list` | still classifies all 5 graphs correctly |
| `project_sdk_sources/{sdk,build-logic,standard-nodes}` | all **PRESENT** — skill-manager's `[[vendored]]` block resolves |
| `f16523ec`, which their manifest cites | **reachable from plugin main** |
| repo-root suite | see "Still unverified" below |

## What landed, and why it is good work

**They found a two-way drift nobody could see.** skill-manager's vendored copy
of the test-graph SDK was **223 lines behind** the plugin's and **37 lines
ahead** of it — including `TESTGRAPH_CONTINUE_AFTER_FAILURE`, which
skill-manager's own `build.gradle.kts` documented *twice* as the way to sweep
the `onboarding` graph and which the plugin did not have at all. They
reconciled **upstream first, in dependency order** (`test-graph 9c51b62` →
`tla-spec-dev f16523ec`) before deleting the copy, so the 37 lines were carried
rather than silently dropped.

**The sweep ledger fixes a defect this epic kept hitting.** `DEF-OUN-023`:
coverage was counted from `build/validation-reports/`, which keeps passing
reports from *earlier* runs, so a graph that never executed still looked green.
The ledger counts from what the init script recorded for that invocation. This
is the same class as `SI-25-DF-08` (verify.sh scanning build output) and the
73,487- and 328,508-entry build directories that took suite tests red twice.

**Two eval-harness defects found by the harness itself.** The `Stop` hook wrote
verdicts to a *relative* `.eval`, inheriting whatever directory the agent had
`cd`'d into — so verdicts were derived correctly, the hook logged `ok`, and the
case scored 0.00, which reads as "the agent did the wrong thing" when it did the
right thing. And `verify.sh` documents a real forgery defence: verdicts are
collected outside the workspace and `.eval/` is cleared *after* every line of
agent-authored code has run, because a blind review broke the first version by
importing an agent-edited module that wrote four verdicts at import time.

**A self-correction worth naming.** `9950511c` reverts their own coord sweep:
repointing `[plugins.skt]` in a *fixture* broke
`w-skt-not-installed-is-not-not-synced` (0.33, `installs` red). The rule they
state is the right one — *"there the coord WAS the answer the agent had to type,
so it had to move; here it is background scenery"* — and it matches the
bundle-site vs legitimate-reference distinction used on this branch. The new
`forbid` on `github:haydenrear/(skt|skill-publisher-skill)` locks it in.

**They corrected something I left.** I classified
`skills/git-issue/references/spec-workflow.md` as a legitimate skill reference
and left it. Their reasoning is better: the coord **resolves**, so following it
silently gives a home a second, separately-updatable copy of a capability the
bundle already carries. Inside a doc the plugin itself ships, naming the bundle
is right.

**`skt status` was both wrong and silent.** It advised installing
`github:haydenrear/skt` — the coordinate the migration removes — and had no
detector for `[plugins.skt]`, the commonest half-migrated shape, measured at
**14 of 86 skill projects** on one machine. This session's own startup hook
still prints the old advice, which is the defect in situ.

## PR #397 — held, and it looks right

20 commits, **+2,716 / −190,291 across 1,664 files**. Verified on the branch:
`skill-publisher-skill` **0 entries**, `skills/test_graph` **0 entries**,
`skill-manager-skill` **0 entries**. The vendoring is genuinely gone, and what
replaces it is a bare coord — `[plugins.tla-spec-dev] source =
"github:haydenrear/tla-spec-dev-plugin"` — with **no commit pin**.

A consequence they state plainly and I am repeating because it is a new
precondition: the SDK paths are now tracked symlinks into a gitignored
`.skill-manager`, so **a fresh clone of skill-manager cannot run graphs until
`project resolve` has run.**

## The decision you asked about: is there anything we owe their epic branch?

**No code.** The dependency is one-directional and unpinned: skill-manager
consumes the plugin by coord and tracks `main`, which the push already made
current. There is no commit, revision or lockfile on their side to advance.

**But the pin in the other direction is the thing to look at, and holding #397
is what keeps it fragile.** `evals/lib/toolchain.lock.toml` now reads:

```toml
[units.skill-manager]
commit = "c405cba36bd9e84e6520f82c3306c9570b72fc59"
ref_when_pinned = "feature/si18-adopt-unified-plugin"
```

Measured against GitHub's compare API: `c405cba3` is **ahead of both
`epic/self-improvement-substrate` and `main`**, and **behind
`feature/si18-adopt-unified-plugin`**. So the plugin's eval toolchain pins a
commit that exists **only on the unmerged PR branch**. Three consequences:

1. **It contradicts the plan.** `ticket_plan.yaml:1075` (SI-14) carries an owner
   instruction: the evals must reach *"the skill-manager CLI carried on
   skill-manager's `epic/self-improvement-substrate` branch"*. The pin names a
   PR branch instead.
2. **It is already 3 commits stale**, and one of them is `fd4bdf78`, which fixes
   an `insteadOf` rewrite that **wrote a live token into the home's git config**.
   Their own onboard graph caught it (`carrierRemote=false`, the runner masking
   the line because it contained the secret). A home whose git config holds a
   credential leaks it wherever the home goes, and `home-clone` exists to copy
   homes. The pinned eval CLI predates that fix.
3. **If the PR branch is deleted, the pin dangles.** `toolchain.py` fetches the
   commit sha directly, so it resolves only while some ref keeps it alive.

**The pin naming a PR branch is CORRECT right now, and I first wrote this
section as though it were a defect.** `eb740669` states the reason: *"Nothing
here has been evaluated against SI-18 / #40 / OUN-6, because the pin predates
all of it."* The previous pin, `6ffacb88`, is their epic tip from 2026-09-19 —
before the migration existed. Pinning the epic branch today would make the
evals judge a CLI that knows nothing about SI-18, which is measuring the wrong
thing. The PR branch IS the branch under test, and naming it is the honest
spelling while the migration is mid-flight.

So the contradiction with SI-14's instruction is real but TRANSITIONAL, and it
resolves the moment #397 lands. What remains actionable is narrower:

- **The pin is 3 commits stale within its own branch.** `c405cba3` predates
  `fd4bdf78`, the token fix. That is a one-line bump and does not wait on the
  merge.
- **If the PR branch is deleted before the pin moves, the pin dangles** —
  `toolchain.py` fetches the sha directly, so it resolves only while some ref
  keeps the commit alive.
- **After the merge**, the pin should move to the epic tip and
  `ref_when_pinned` back to `epic/self-improvement-substrate`, restoring SI-14.

They also retired `[units.skt]` rather than repointing it, with the right
reason: repointing at `tla-spec-dev-plugin` *"would pin this repository against
itself and grade the pin instead of the branch"*. The pinned skt shipped
exactly skill-manager, skt and unit-authoring — all three of which SI-16 nested
here — so every staging candidate collided and `staged_units` stayed empty: a
silent no-op that read as provisioning. And `toolchain.py`'s `--ref` matched
`name == "skt"`, so after the retirement it accepted a value it could never
apply; that dead path is fixed too.

Recommended order, once you are ready:
1. Merge #397 into their `epic/self-improvement-substrate`.
2. Move the plugin's pin to the resulting epic tip and set
   `ref_when_pinned = "epic/self-improvement-substrate"` — a one-line change in
   **this** repository, restoring SI-14's owner instruction.
3. Then the release, and then the eval ladder against a pin that names a
   durable ref.

## Other findings

**Six constituents were renamed upstream and nothing said so.** `git-epic-skill`
→ `git-epic-workflow`, `git-issue-skill` → `git-issue`, `discovery-skill` →
`discovery`, `test_graph_skill` → `test-graph`, and the two SI-12 added. The old
URLs **redirect**, so `git subtree pull` kept working and the rename was
invisible. `integration.toml` now records the canonical names — but **this
worktree's own git remotes still carry the old ones** (8 of 10). They work by
redirect; they should be repointed.

**Not a defect, checked and cleared:** `evals/README.md:131` and
`evals/bin/skill-manager:18` still cite `6ffacb88ff96`. That is dated example
output ("Measured 2026-09-19 against the materialised checkout"), not a live
pin — historical narration, same category as the frozen eval fixtures.

## Still unverified

- **Repo-root suite** — running at review time; compared by NAME against the
  recorded ten-failure baseline, result appended below when it lands.
- **The five test graphs have not been re-run** since the pull, and the pulled
  changes include `PlanExecutor.kt`, `run.py` (+277), a new `sweep.py` and a new
  init script. The graph surface is the thing most likely to move.
- **Evals have not been run.** Two eval defects from wave 11–12 remain open
  (`SI-16-DF-02`, `SI-16-DF-03`), and the staging ceiling was last measured at
  28,603 entries against a 20,000 limit.

---

## Suite result: three regressions, found and fixed

`13 failed, 1836 passed, 8 skipped` against a baseline of ten. Compared by NAME
against `review/wave-13-15/known-ten-baseline.txt`: **nothing left the baseline,
three joined it**, and all three were in one file.

```
tests/test_eval_toolchain_pin.py::test_every_pinned_unit_names_a_commit_and_never_a_branch
tests/test_eval_toolchain_pin.py::test_the_lock_is_reachable_by_the_runner_without_network
tests/test_eval_toolchain_pin.py::test_the_two_units_this_epic_runs_against_are_the_ones_pinned
```

**One root cause: the guard still encoded the invariant the skt retirement
removed.** `git log 2a9fef7c..HEAD -- tests/test_eval_toolchain_pin.py` is
empty — the lock changed and its guard did not.

| line | assertion | after the retirement |
|---|---|---|
| 68 | `len(units) >= 2` — *"expected the lock to pin skt and skill-manager"* | 1 unit |
| 79 | `"skt" in units` — *"it is the unit the loop resolves from the home"* | retired |
| 207 | `print-ref --unit skt` | `no unit 'skt' in the lock`, rc=1 |

The guard's own message names the rationale that expired: skt was *"the unit the
loop resolves from the home"*. SI-16 nested skt into this plugin, so the view IS
the plugin, which is precisely `eb740669`'s argument for retiring the pin.

**Fixed here, because it is this repository's file.** The count assertion was
incidental scaffolding — the property that test is about is the per-unit
40-hex-commit loop, which is untouched. The presence assertion is INVERTED
rather than deleted: `skt not in units` is the new invariant, so re-pinning skt
fails the guard and the reason is in the docstring. `print-ref` drops `--unit`
and exercises the sole-unit default that `eb740669` added, so the test no longer
hardcodes a unit name that can retire.

Verified: `tests/test_eval_toolchain_pin.py` **10 passed**, and
`toolchain.py print-ref` returns `c405cba3…`, 40 hex, matching the lock.

## Graphs after the pull: unchanged, and the repaired node held

Run from a clean tree at `58af0470`. Build output cleared first (0 tracked,
`.gitignore:67`), and **the tree was clean after every run** — SI-25's third
acceptance criterion still holds against their rewritten `run.py` and the new
sweep ledger.

| graph | verdict | nodes |
|---|---|---|
| specWorkflow | **PASSED** | 9/9 |
| cliWorkflow | **PASSED** | 2/2 |
| effectProviderExamples | **PASSED** | 1/1 |
| sktHooks | **PASSED** | 3/3 |
| sktSurface | **ERRORED** | 4/5 |

Each graph printed exactly once; the double-print fix survives their changes.

**`skt.status-tiers` held: 100 assertions, 0 failed.** This is the node whose
fixture I relocated in SI-25, and their `+88` lines in `skt/src/skt/status.py`
land directly on it. It is green with MORE coverage than before — their
`test_status.py` additions.

**`skt.ticket-roundtrip` fails 13 of 39, and they are the SAME thirteen** as the
SI-25 run, name for name: four worktree-creation assertions and nine refusal
WORDING assertions whose behavioural twins all pass. `SI-25-DF-06` and
`SI-25-DF-07` reproduce unchanged. Nothing in the 13 commits touched either,
and nothing was expected to — they are this repository's findings, not
skill-manager's.

**One detail to add to SI-25-DF-06.** The node published
`giwSource: clone:https://github.com/haydenrear/git-issue-workflow-skill.git`.
That is the OLD repository name — `git-issue-workflow-skill`, which
`49f67d2a` renamed to `git-issue-workflow` in `integration.toml`. The clone
succeeds only through GitHub's redirect, which is exactly the invisibility that
commit was written about. So `GIW_REMOTE` in
`test_graph/sources/skt_ticket_roundtrip.py` carries a stale coord on top of
resolving only one rung: fixing the rung removes the clone entirely, but if the
fallback is kept it should name the current repository.
