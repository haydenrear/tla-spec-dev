# Wave 1 — merge record

| PR | ticket | head | merge commit | planned promotion_order | actual position |
|---|---|---|---|---|---|
| #349 | SI-01 | `5b929e17` | `058beb3d` | 10 | 1 of 1 |

Merged with `gh pr merge --merge` (never `--squash`): the migration commit
`09d8108d`, the confirmatory evidence commit `5b9816f8` and the reconcile merge
`5b929e17` are separate facts the finalizer's audit reads.

## The lane held, with one epic-agent-caused reconcile

SI-01 has no `promotion_predecessor` (wave 1, first in the lane), so nothing was
waiting on it. The reconcile was not a lane failure: `56227e50` appended a row to
`specs/results/deferred_findings_final.yaml` after SI-01 branched, and SI-01 had
appended two rows to the same cumulative file. One content conflict, returned to
its agent under `human-review.md` §1 rather than resolved on the epic branch.

Verified after the reconcile, before the merge:

- `git merge-tree` exit 0, tree `bad0db85` — clean
- backlog 38 rows; 0 deleted-or-changed lines against either parent; 0 conflict markers
- `SIS-KICKOFF-F-03`, `SI-01-DF-01`, `SI-01-DF-02` all present exactly once
