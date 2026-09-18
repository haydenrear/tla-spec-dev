# Wave 4 — merge record

Range `21a71448` → `e9b04917`. Two tickets, 76 files changed.

| PR | ticket | planned order | actual position | merge commit |
|---|---|---|---|---|
| #358 | SI-03 | 70 | 1 | `e31bce75` |
| #357 | SI-07 | 80 | 2 | `e9b04917` |

Merged with `gh pr merge --merge`; never `--squash`.

## The lane held, and this time it mattered semantically

Wave 3 merged four of five out of declared order or after a reconcile. Wave 4
did neither: **planned order equals actual order, and neither PR needed a
reconcile.** SI-07 still merged cleanly onto the tip after SI-03 landed
(`merge-tree` exit 0, verified before merging).

The order was not arbitrary here. SI-07's required artifact blocks reference
SI-03's improvement card **by name**, so merging SI-07 first would have put the
reference ahead of the referent. Unlike SI-06/SI-10 in wave 3 — which had no
dependency edge and were deliberately swapped — these two have a real ordering
reason, and it was honoured.

## Why no backlog conflict this time

Wave 3's four reconciles were all the same collision: several tickets appending
to the end of `specs/results/deferred_findings_final.yaml`. Wave 4 avoided it
without any new machinery, and not by luck:

- **SI-03 filed nothing.** Its `skt ticket new` failure was already filed twice
  (`SI-06-DF-02`, `SI-11-DF-04`); it recorded the corroboration in its own
  `FRONT-DOOR.md` instead of adding a 59th row. It touched the file **not at
  all** — verified: 0-line diff against the tip.
- **SI-07 filed two** (`SI-07-DF-01`, `SI-07-DF-02`), taking 58 → 60 as a pure
  tail-append with 0 deleted lines.

One ticket appending is not a collision. That is the whole of the fix, and it is
why `per_ticket_backlog` — which SI-07's validator now recommends automatically —
is the right shape rather than a merge driver.

## Checks at merge time

DCO fails on both, as on every PR in this repository (258 commits since `main`,
55 signed). Both branches unprotected, so advisory; GitGuardian passes on both.
Unchanged owner decision at the epic PR. **This time `gh pr checks` was run
before merging** — wave 3's record notes it was not.

## Integrated validation, on the merged tip `e9b04917`

- **Repository suite: 10 failed / 1639 passed / 6 skipped** — the same ten
  failure NAMES as every prior wave. **Zero new.**
- **Graphs: all three green** — `specWorkflow`, `cliWorkflow`,
  `effectProviderExamples`, each `BUILD SUCCESSFUL`.
- **Scorecard `check`: 332 problems, unchanged** from the epic base `994f650c`
  and from the pre-wave tip, while cards went 95 → 97. Wave 4 added zero.
- **Scorecard `audit`: 0 violations**, with `R-I1`–`R-I3` executing on the two
  new improvement cards.
- **Sealed eval cards: 133 → 137**, and **zero of the pre-existing 133 altered** —
  the safety property of introducing a new card *kind* rather than a new version.
- **`BuildSkillCli`: `accepted: true`** — the model still agrees with the tree.

## Home reconciliation

| worktree | verdict |
|---|---|
| wt-336-improvement-card | ✓ clean — "holds nothing that removing it would destroy" |
| wt-340-epic-owns-model | ✓ clean |

Both exit 0, nothing published, no `home sync` needed. Every change in this wave
is a tracked repository file — which is the point `worktree-lifecycle.md` now
makes explicit, as of SI-07.
