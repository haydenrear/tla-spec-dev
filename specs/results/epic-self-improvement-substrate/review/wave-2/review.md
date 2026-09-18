# Wave 2 review — epic/self-improvement-substrate

Range: `28ecf7e1` → `a42e0f7e`. One ticket, SI-02 (#335), merged as PR #350.

**This wave IS a gate.** `review_policy.milestones: [2, 4, 6]`. Wave 3 does not
dispatch until the owner answers.

## 1. What landed

The five workflow skills are constituents of the plugin. `skills/` holds
`spec-double-2`, `git-epic-workflow`, `git-issue-workflow`, `git-issue`,
`discovery`, `test-graph` — nested with `git subtree`, full history, no
`--squash`, as decided at kickoff. 1,235 files, +186,041/-52.

The homes were then migrated, which is the half that is not in any diff:

- the project home carries `plugin:tla-spec-dev` and **none** of the six
  standalone copies (`home sync` from the ticket worktree, then `uninstall` of
  the six — a sync will not delete, by design: "deleting a unit is not what a
  sync is for");
- `skt check`: all current, 16 change-managed, tier project;
- the root home is untouched and still carries the six. That is deliberate and
  it is a decision below.

## 2. Verified, not accepted

| Claim | Verdict |
|---|---|
| merges cleanly into the tip | ✅ `merge-tree` exit 0 |
| backlog appended, nothing lost | ✅ 44 rows, 0 deleted-or-changed lines |
| zero gitlinks, zero stray `.git` | ✅ 0 and 0 |
| the two orphan commits survive nesting | ✅ `1f91074b`, `4eeb350d` are ancestors |
| zero `skill-imports` naming a contained unit | ✅ 0 across six |
| zero live hardcoded store paths | ✅ 1 of 160 in executable code, a comment; 156 sealed record |
| 0 new failures, three suites | ✅ by name: 10/10, 7/7, 7/7 |
| three graphs green | ✅ all `BUILD SUCCESSFUL` |
| nested trees byte-identical to upstream | ❌ **all five differ — and they should** |

The last row is the wave's one wrong claim. The differences are precisely the
intra-bundle rewrites the ticket existed to perform. The work is correct; the
sentence would mislead the next person deciding whether a `subtree pull` is
safe, and it contradicts the same report's "14 imports, 12 coords, 47 paths
rewritten".

## 3. Decisions made, and guardrails

**No guardrail was overridden.** No `--force`, no `--allow-open`, no
`--accept-new`, no skipped test, no matrix entry downgraded.

**Decisions taken at this review, with the owner:**

| Decision | Disposition |
|---|---|
| `skill-project.toml` edited outside the ticket's conflict keys | **Kept.** It removed `[skills.test-graph]`; leaving the coord would silently install a second standalone copy of a contained skill |
| `[[vendored]] from_unit = "tla-spec-dev"` — the ticket's own highest-uncertainty line, never checked with `project resolve` | **Routed to SI-11** |
| `verify.sh` as `GOAL-one-unit`'s instrument | **Replaced.** See §4 |
| the ticket worktree home's 2 at-risk units | **Carried** into the project home, then the six standalone copies removed |

**Epic-agent errors this wave, both recorded rather than quietly fixed:** two of
my shell checks were broken by zsh treating `"$REF:path"` as a `:s` modifier,
which first reported five nested trees as empty and then as differing for the
wrong reason; and the earlier `--numstat` churn rollup mis-bucketed 101 renames
because `git` renders them as `{old => new}`. Neither reached a committed
artifact; both are the reason the verdicts above are stated with the command
that produced them.

## 4. The goal amendment

`GOAL-one-unit` changed in two ways, both recorded in the plan with reasons.

**Its instrument was unusable.** The declared local signal,
`plugin-repository/scripts/verify.sh`, cannot go green for two structural
reasons — it greps from `.` so it reads the gitignored home and sealed eval
transcripts (`SI-02-DF-01`), and after migration it will not start because
`git-integration-repo`'s `integration-lib.sh` resolves `git-issue-workflow/lib.sh`
at the standalone path with no plugin rung (`SI-02-DF-05`). Both skills are
outside the bundle by owner decision, so this epic cannot repair them. Replaced
by `skt status` plus `skill-manager list` reporting no outstanding errors.

**The migration falsified an assumption in its first clause.** The plugin
installed into the project home from a local path:

```
tla-spec-dev   plugin   0.1.0   ...   SOURCE: unknown
✗ NEEDS_GIT_MIGRATION: not git-tracked; file/local installs do not sync
```

The change-managed count fell 19 → 16 — `skt check` says "all current" only
because it stopped counting the plugin. The goal's sentence is that the
substrate "installs, **syncs** and improves as one plugin", and *syncs* is
currently false. A third clause now says so explicitly and SI-08 reports it
separately, rather than letting a unit count of 1 stand in for a sentence that
is not yet true.

## 5. Where the bugs probably are

1. **`test_graph/{sdk,build-logic,standard-nodes}` are ABSENT on disk.** They are
   generated from `provider-bindings.json`, which still names
   `../.skill-manager/skills/test-graph`. The graphs pass anyway, which means
   either a fallback is carrying them or the binding is unexercised — worth
   knowing which. SI-11.
2. **`selftest.sh` enumerates only the standalone layout** (`SI-02-DF-02`) and
   was not run this wave. The suite that would have caught items 1 and 3 is the
   one that cannot see the new layout.
3. **`github-action.py:320`** resolves `TEST_GRAPH_SKILL_HOME` at the standalone
   rung only, while its own docstring shows the two-rung form. SI-11.
4. **`install file://<checkout>` recurses into the checkout's own home**
   (`SI-02-DF-04`) — the home-migration path the README now documents.
5. **The migration can strand a home**: documented order is install-then-
   uninstall, and the install failed *after* the uninstall, leaving a home with
   neither. Repaired by hand this time; it should be transactional.

## 6. Suggested next steps

**Wave 3, ready on your answer:** SI-04 #337, SI-05 #338, SI-06 #339, SI-10
#343, and the new SI-11 #351. Five tickets, disjoint conflict keys, promotion
30→65. SI-11's workspace is scaffolded; the other four are scaffolded at
dispatch.

**Deferred findings — 11 pending, none blocking.** Four from kickoff
(`SIS-KICKOFF-F-01`…`F-04`), two from SI-01, five from SI-02
(`SI-02-DF-01`…`-05`). Backlog is 44 rows and cumulative.

**Goal trajectory.** `GOAL-one-unit` moved for the first time: 6 units → 1 in
the project home, clause 1 of 3 satisfied there. Clause 3 is **not** satisfied —
the plugin cannot sync. Clause 2 waits on SI-10's eval cases. No other goal has
moved; four are instrument-building and their instruments land in waves 3 and 4.

**What gets more expensive if deferred:** SI-11. Wave 3 is eval-heavy and every
failure it repairs is silent — a stale path resolves to nothing and the check
goes green. Running evals before the bindings are correct measures the wrong
tree.

**Decisions for the owner:**

1. **The root home still carries the six standalone skills.** `GOAL-one-unit`
   names *both* tiers. Migrating it touches `~/.skill-manager`, which your
   standing rule protects — say the word and I do it, or it waits for SI-08.
2. **The plugin's install source.** Making it change-managed means installing
   from `github:haydenrear/tla-spec-dev` rather than a local path, which
   reintroduces a published-coordinate dependency the epic was reducing. SI-11
   or SI-08 can own it; it needs a decision either way.
3. **Wave 3 width.** Five tickets at once is the widest this epic goes.

**Standing worktrees and headroom:** four — main, epic, SI-01's, SI-02's. Both
ticket worktrees stay until the epic-end sweep; SI-02's home has already been
reconciled, so nothing is at risk in it now.
