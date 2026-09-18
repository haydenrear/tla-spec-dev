# Wave 2 — merge record

| PR | ticket | head | merge commit | planned promotion_order | actual position |
|---|---|---|---|---|---|
| #350 | SI-02 | `39e19a44`/`78dff9c3` | `a42e0f7e` | 20 | 1 of 1 |

Merged with `gh pr merge --merge`. The branch carried 2 commits plus 5 subtree
merges, and `--squash` would have collapsed five imported histories into one blob.

## Verified before the merge, by the epic agent

- `git merge-tree` against the then-current epic tip: exit 0, no conflicts
- backlog 44 rows, **0** deleted-or-changed lines against the epic parent
- **0** gitlinks (mode 160000), **0** tracked `.git` paths
- `1f91074b` and `4eeb350d` — the commits that existed only in a gitignored home
  at kickoff — are ancestors of the merged head
- **0** `skill-imports` naming any contained unit, across all six
- of 160 hardcoded store-path hits, **1** is in executable code and it is a
  comment; 156 are sealed record under `specs/.history` and `specs/results`
- **0 new failures by name**: repository 10→10, spec-unit `current` 7→7,
  spec-unit `SI-02/desired` 7→7
- all three graphs `BUILD SUCCESSFUL`

## One claim in the ticket's report was wrong

The report said each nested tree is "byte-identical to its upstream `main`
tree". All five differ, and they should: the diffs are the intra-bundle
rewrites the ticket existed to make — dropped `skill-manager.toml` dependency
entries, re-addressed imports, repointed store paths, and executable changes in
`agent-home.sh` and `selftest.sh`. The work is right; the sentence is not, and
it cannot coexist with the same report's "14 imports, 12 coords, 47 paths
rewritten". Recorded because "identical to upstream" is exactly the sentence a
future reader would trust when deciding whether a `subtree pull` is safe.
