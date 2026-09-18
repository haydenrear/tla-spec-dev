# Wave 3 — merge record

Range `994f650c` → `7c5d34a6`. Five tickets, 171 files changed.

| PR | ticket | planned order | actual position | merge commit |
|---|---|---|---|---|
| #353 | SI-04 | 30 | 1 | `6701bece` |
| #354 | SI-05 | 40 | 2 | `56c7658f` |
| #355 | SI-10 | 60 | **3** | `93dd3fac` |
| #352 | SI-06 | 50 | **4** | `c987fcf7` |
| #356 | SI-11 | 65 | 5 | `985bd0db` |

Merged with `gh pr merge --merge` throughout; never `--squash`.

## The one deviation from the declared lane

SI-10 (order 60) was merged **before** SI-06 (order 50), deliberately. SI-06 and
SI-10 have no dependency edge between them — both depend only on SI-02 — so the
lane order between them encodes serialization, not sequence. SI-10 had finished
its reconcile and was clean against the tip while SI-06 was still reconciling;
holding it would have cost an extra reconcile round-trip on a purely mechanical
conflict and delayed nothing real. The promotion lane's actual guarantee, that
two promotions never integrate concurrently, held throughout.

## Every ticket reconciled, and that was the epic agent's fault

Four of five PRs conflicted after the first merge, all on one path:
`specs/results/deferred_findings_final.yaml`. Four branches each appended rows to
the end of the same 45-row cumulative ledger from the same base, so collision was
certain. Per `human-review.md` §1 each conflict went back to its agent rather
than being resolved on the epic branch.

| ticket | reconciles | onto | final rows |
|---|---|---|---|
| SI-05 | 0 (clean) | — | — |
| SI-10 | 1 | `56c7658f` | 50 |
| SI-06 | **2** | `56c7658f`, then `93dd3fac` | 53 |
| SI-11 | 1 | `c987fcf7` | 58 |

SI-06 reconciled twice because the epic agent merged SI-10 mid-flight, moving the
tip under it. SI-11 was told to hold until SI-06 landed so it reconciled once
instead of twice; it had already prepared a reconcile onto the stale tip and
hard-reset it away rather than let it collide.

**The resolutions were deterministic, not hand-merged.** SI-06 established the
method and SI-11 copied it: prove both sides are pure tail-appends over the
45-row base (`head -n <base-lines>` byte-identical on each side), re-derive your
own block from your pre-reconcile commit, then produce literally `tip ++
my_block`. Verified each time with `diff <(git show <parent>:<file>) <file> |
grep -c '^<'` returning **0 against both parents** — a row count alone cannot
catch a swap.

Final: **58 rows, 58 unique ids**, zero conflict markers, YAML parses.

## Checks at merge time

DCO **fails on all five PRs**, and on the three merged before the epic agent
thought to run `gh pr checks` at all. Neither `main` nor the epic branch is
protected, so DCO is advisory and nothing was bypassed — but the omission was
real and SI-06 caught it, not the epic agent. GitGuardian passes on all five.
The wider state: 258 commits on the epic branch since `main`, 55 carrying
`Signed-off-by`. The bot's remedy rewrites sealed evidence commits and
force-pushes an epic branch, both forbidden. It is an owner decision at the epic
PR (§6).

## Integrated validation, on the merged tip

Run after all five merges and after the epic agent's model corrections
(`7c5d34a6`), not per-branch:

- **Repository suite: 10 failed / 1627 passed / 6 skipped** — the same ten
  failure NAMES as the pre-wave baseline. **Zero new across the entire wave.**
- **Graphs: all three green** — `specWorkflow` 9/9, `cliWorkflow` 2/2,
  `effectProviderExamples` 1/1, each `BUILD SUCCESSFUL` exit 0.
- **TLC on `specs/current`**: 17,234 states generated, 1,321 distinct, depth 14 —
  unchanged, as SI-05 predicted for a string-and-comment delta.
- **`BuildSkillCli`: `accepted: true`** — false between SI-11's branch and the
  epic agent's correction, true once both landed.

## Home reconciliation

| worktree | verdict |
|---|---|
| wt-337, wt-338, wt-339, wt-343, wt-351 | ✓ clean — "holds nothing that removing it would destroy" |
| wt-335 | ✓ clean |
| wt-334 | ✗ exit 1 — "3 unit(s) would be lost" |

**wt-334 is a stale home, not lost work, and must NOT be synced.** The three
units are `skill:discovery`, `skill:git-epic-workflow`, `skill:git-issue`,
flagged `would-create` because the project home no longer carries them as
standalone units — which is the point of SI-02. Verified: all three are clean,
have **zero unpushed commits**, sit at exactly their upstream SHAs (`b4ee30e`,
`031a5a1`, `1f91074`), and are already present inside the nested plugin on the
epic tip. The same report shows `removed-upstream plugin:tla-spec-dev`,
confirming the home predates the plugin. Running the suggested `home sync` would
re-create the six standalone skills the migration removed and undo
`GOAL-one-unit`. Disposition: leave it, remove with the end-of-epic sweep, reason
recorded here as `worktree-lifecycle.md` requires.
