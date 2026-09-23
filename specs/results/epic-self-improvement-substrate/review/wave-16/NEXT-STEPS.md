# Next steps and open decisions

State as of 2026-09-23, `epic/self-improvement-substrate` at `ee0d4705`,
identical to `tla-spec-dev-plugin/main` plus this session's commits. Tree clean.

This is the decision document. Everything below the "Refreshed" section is a
choice that is yours, not mine, and each one states what it costs either way.

---

## Refreshed — done and verified

| item | result |
|---|---|
| Pulled skill-manager's 13 commits | fast-forward `2a9fef7c..6b89943f`, zero overlap with waves 13–15 |
| Eval pin | `c405cba3` → **`fd4bdf78`**, verified by materialising: *"the CLI says: skill-manager 0.28.1+gfd4bdf7865d6"*, drift clean |
| Eight renamed remotes | repointed to canonical names; each confirmed to exist and resolve |
| Subtree pulls | **none owed** — all 7 constituent tips are already ancestors of HEAD |
| Build/venv residue | cleared (`test_graph/build`, `skills/skt/.venv`), both gitignored, 0 tracked |
| Repo-root suite | **the known ten, by name** — nothing new, nothing lost |
| skt's own suite | **327 passed / 3 skipped** |
| Graphs | specWorkflow 9/9, cliWorkflow 2/2, effectProviderExamples 1/1, sktHooks 3/3 — all PASSED |
| `skt.status-tiers` | **100 assertions, 0 failed** — the node repaired in SI-25, where their `status.py` change lands |
| Tree after every graph run | **clean** |

**One regression found and fixed** (`58af0470`): their skt-pin retirement was
correct, but `tests/test_eval_toolchain_pin.py` still required skt and nobody
updated it. The presence check is now INVERTED, so re-pinning skt fails with
the reason rather than passing silently.

**`sktSurface` remains ERRORED**, unchanged: `skt.ticket-roundtrip` fails the
same 13 of 39 assertions, name for name. `SI-25-DF-06` and `-DF-07` reproduce.

---

## Decision 1 — the eval staging ceiling is the hard blocker

**Measured today, with `run.sh`'s own exclude list: 360,230 entries against a
20,000 ceiling.** A full eval run would be refused. Two contributors, and
neither is "the repository is too big":

| contributor | entries | tracked |
|---|---|---|
| `test_graph/build` | 294,611 | 0 — build output |
| `examples/*/evidence` | ~56,500 | 1,520 of 58,079 — the rest gitignored run output |
| everything else | ~9,000 | — |

**Root cause: the view is enumerated with `find` and copied with `rsync
--exclude`, neither of which respects `.gitignore`.** `git status` reports
**zero untracked** files under `examples/effect_providers` — every one of those
56,500 entries is *ignored*, and the view stages them anyway.

The decisive number: **tracked files, minus `specs/.history` (which `run.sh`
already excludes), is 6,730.** The lock's own comment says this repository
*"already spends 6,264 of"* the ceiling — so ~6,264 was always the intended
size, and the gap is entirely residue.

**Option A — enumerate the view from `git ls-files`.** Fixes both contributors
at once and cannot regress when someone adds a new ignored directory. This is
the same conclusion `SI-25-DF-08` reached about `verify.sh`: *git ls-files is
the honest enumeration for a git repository*. Cost: `rsync` needs a file list
rather than an exclude list; a handful of deliberately-untracked-but-needed
paths (if any) must be named explicitly.

**Option B — add `test_graph/build` and `examples/*/evidence` to the exclude
list.** Two lines, lands today. Cost: it is the third time this epic has added
an exclude after the fact, and the next ignored directory repeats it.

**Recommendation: A**, with B as the stopgap if evals must run this week.

## Decision 2 — 28 findings were never consolidated into the ledger

`specs/results/deferred_findings_final.yaml` holds **87** rows. The per-ticket
files under `specs/results/deferred/` hold **28 more that are not in it**:

| file | rows absent |
|---|---|
| `SI-08.yaml` | 11 |
| `SI-16.yaml` + `SI-16-dispatch.yaml` | 6 |
| `SI-15.yaml` | 5 |
| `SI-17.yaml` | 5 |
| `EPIC-AGENT.yaml` | 1 |

The true total is **115**. This is not academic: I cited `SI-16-DF-02` and
`-DF-03` repeatedly this session as the eval blockers, and a ledger query
returned NOT FOUND for both — they were real, in a file the ledger never
absorbed. Anyone planning from the ledger alone has been planning from 76% of
the findings.

**Decision: consolidate the 28, or declare the per-ticket files authoritative
and stop treating `_final.yaml` as the ledger.** Either is defensible; the
current split is what produced a wrong answer.

## Decision 3 — one eval blocker is closed, one is not

**`SI-16-DF-03` is CLOSED by their work.** Its fix said *"either drop
`[units.skt]` from the lock and say the suite grades the branch, or keep the
pin and stage it somewhere a case can reach"*. `eb740669` did the first, with
the reasoning written out. No action.

**`SI-16-DF-02` is OPEN and still bites.** `evals/run.sh:141` does
`cp "$here/hooks/hooks.json" "$view/hooks/hooks.json"`, overwriting the
plugin's now-committed `hooks/hooks.json`. So **an eval run does not exercise
the shipped hooks, and the suite is not evidence about them.** Its own fix
offers two paths: compose the view's hooks.json from both sources, or keep the
overwrite and say in `evals/README.md` that shipped hooks are out of scope.

**This one should be decided before any scored run**, because it determines
whether hook behaviour is inside or outside what the scores mean.

## Decision 4 — PR #397 and the pin, sequenced

Nothing needs pushing to skill-manager's epic branch: they consume the plugin
by bare coord tracking `main`, already current, and vendoring is gone
(`skill-publisher-skill`, `skills/test_graph`, `skill-manager-skill` all zero).

The pin now names `fd4bdf78` on `feature/si18-adopt-unified-plugin`. That is
**correct while the PR is open** — the previous pin predated SI-18 entirely, so
pinning their epic branch would grade a CLI that knows nothing about the
migration.

**The sequencing hazard:** `toolchain.py` fetches the pinned sha directly, so it
resolves only while some ref keeps that commit alive. If #397 merges and the
branch is deleted before the pin moves, the pin dangles.

**Recommendation:** move the pin as PART of the merge, not after —
1. merge #397 into their `epic/self-improvement-substrate`;
2. in the same sitting, set the pin to the resulting epic tip and
   `ref_when_pinned = "epic/self-improvement-substrate"`, restoring SI-14's
   owner instruction;
3. then the release;
4. then the eval ladder against a pin that names a durable ref.

## Decision 5 — this worktree's home carries the duplication the epic removes

The worktree home (`<worktree>/.skill-manager`, tier `worktree`) holds **27
units, 8 of which the plugin also contains**: discovery, git-epic-workflow,
git-integration-repo, git-issue, git-issue-workflow, plugin-repository, skt,
test-graph — including the **standalone `skt` PLUGIN at 0.8.2**. `skt check`
reports 4 stale units, one of which is the retired `spec-double-compiler`.

This is pre-migration residue in a disposable home. It does not affect the
graphs (which passed) and evals stage their own view, but it is the exact shape
`GOAL-one-unit` clause 1 measures, and an eval or manual test that resolves
from this home resolves duplicates.

**Decision: rebuild this worktree home the way SI-24 rebuilt root, or accept it
and record why.** I have not touched it — no home is synced or rebuilt without
your say-so.

---

## Suggested order

1. **Decide 1 (ceiling)** — nothing scored can run until the view fits.
2. **Decide 3 (hooks)** — determines what eval scores mean.
3. **Consolidate the findings (2)** — cheap, and everything downstream plans
   from that ledger.
4. **Merge #397 + move the pin in one sitting (4)**, then the release.
5. **Then** the eval ladder: SI-19 → SI-22, then SI-23.
6. **Decision 5** whenever convenient; it gates nothing today.

## What is NOT verified

- **No eval has been run.** The ceiling refuses one today.
- **`sktSurface` stays red** on `skt.ticket-roundtrip` — two named causes,
  neither fixed, both this repository's own findings.
- **Manual testing has not been re-run** since the pull. SI-26's 15 transcripts
  predate these 13 commits, and `skt status` output changed among them.
