# Wave 5 review — epic/self-improvement-substrate

Range: `9a06cdeb` → `39dd6d3c`. One ticket: SI-12 (#359), PR #363, nesting the
last two dependent skills.

**This wave is NOT a gate.** `review_policy.milestones: [2, 4, 6]`. Wave 6
(SI-09) is the next stop.

This artifact follows the five-block schema SI-07 made mandatory, which its own
`validate_epic_plan.py --repo-root` checks.

---

## Block 1 — Model delta applied

**None owed, and that is measured rather than assumed.**

- Files under `specs/` outside `results/` touched by SI-12: **0** (checked with
  `git diff --name-only` across the merge range).
- No TLA+ action, state or invariant change was proposed; the issue declared the
  spec workflow NOT REQUIRED, and the ticket honoured it.
- `specs/tickets/SI-12/`, `specs/current`, `specs/desired_program_model` and
  `specs/program_model` are all untouched on the merged tip.

Wave 3's corrections remain the last model delta and are still correct here.

## Block 2 — Anchors placed

**None placed. All six findings attributed to `UNMODELED/` bins.**

SI-12 attributed its defects to `UNMODELED/substrate-tooling`,
`UNMODELED/validation-harness` and `UNMODELED/home-resolution` — none sat inside
a `TlaSpecDevCli` action. That is the correct disposition under
`references/bug_attribution.md`: these are plumbing defects in resolution rungs,
a gitignored build directory and a CLI flag asymmetry, not behaviour the model
describes. The matrix is unchanged.

## Block 3 — Improvement-card row

**No round run this wave, deliberately.** The card's first probe was wave 4's
owner tracking pass on PR #352. Wave 5 is a single implementation ticket, and
scoring one PR against it here would add a row that decides nothing while
consuming a judge budget SI-08 needs. SI-08 runs the blind rounds that decide
`GOAL-blockers-propose`.

Worth recording for that ticket: PR #363 would score well on I2 (six blockers
met, three applied with commit SHAs, three proposed as backlog rows with
`suggested_fix`) and on I5 — it has a *"What I could NOT verify"* section that
names five unverified claims, including one where it changed an assertion it
could not exercise. That is the honesty dimension behaving as intended.

## Block 4 — Skill changes applied or declined

| proposal | disposition |
|---|---|
| `integration-lib.sh` resolved `git-issue-workflow`'s `lib.sh` at the standalone rung only | **applied** (`1baad7f8`) — closes `SI-02-DF-05`; verified both directions, plugin rung resolves alone, standalone still wins when both exist |
| `new-change.sh`'s `propagate_command` lost the fan-out silently once the unit was contained | **applied, OUTSIDE its conflict keys, disclosed** — see the override note below |
| `plugin-repository` README + two refusals named duplicate-installing coords | **applied** (`1baad7f8`) — both now name the bundle |
| widen `test_plugin_layout_resolution.py` beyond `skills/*/scripts` | **declined, filed `SI-12-DF-03`** — widening it inside this ticket would have turned 10 pre-existing lines red inside the very ticket whose claim is "no new failures by name" |
| track `build-logic` or bootstrap it | **declined, filed `SI-12-DF-05`** — see below; it is the most consequential finding of the wave |
| `skill-manager remove` should accept `--yes` | **declined, filed `SI-12-DF-06`** — upstream in `skt`, not this repo |

**The scope override, reviewed and upheld.** SI-12 edited two files in
`skills/git-issue-workflow/scripts/` which are not in its conflict keys. I read
both diffs rather than taking the disclosure on trust. `new-change.sh` is a real
code change, not a comment: it adds a genuine `plugins/*/skills/` rung to
`propagate_command`'s resolution loop and repoints the fallback from
`github:haydenrear/git-integration-skill` to the bundle coord. Without it,
nesting silently broke the fan-out — the loop found nothing and fell through to
telling an integration repo that *had* the unit to install it. Upheld on SI-02's
precedent: **fix what silently breaks, file what is prose.** It drew that line
itself and filed the four prose sites as `SI-12-DF-01` rather than smuggling a
documentation rewrite into a nesting ticket.

## Block 5 — Model corrections owed by merged tickets

**None outstanding.** SI-12 made no edit to any epic-owned workspace under
`specs/tickets/SI-12/`, so nothing is owed forward. Second consecutive wave with
a clean slate on this debt.

---

## What the wave produced

`git-integration-repo` and `plugin-repository` are constituents, nested by
`git subtree` with full history and no `--squash`. The plugin now contains
**eight** skills; `integration.toml` lists seven constituents. Four
`skill-imports` were rewritten to `unit: tla-spec-dev`, and coords were
**removed rather than repointed** — correct, because a git coord still resolves
after bundling and repointing installs a second standalone copy.

## Verified, not accepted

| claim | how checked | result |
|---|---|---|
| 0 new failures | failure **NAMES**, suite run by me on the merged tip | 10 → 10, **same ten names**, 0 new |
| subtree integrity | `git ls-tree` for mode 160000; path scan; log scan | **0 gitlinks, 0 stray `.git`, 0 squash markers** |
| no model trespass | `git diff --name-only` over the range | **0** `specs/` files outside `results/` |
| backlog delta | row count both sides + pyyaml parse + duplicate-id scan | 60 → **66**, parses, **no duplicates** |
| root home untouched | mtimes + plugin list + standalone list | Sep 13/17 mtimes predate today; **no `tla-spec-dev` plugin**; standalone copies still present by design |
| `GOAL-one-unit` clause 1 | **measured directly**, not via the reported command | ticket home's standalone `skills/` holds 10 units, **none of the 8 contained**; all 8 under `plugins/tla-spec-dev/skills/` |
| the graphs finding | base-control comparison | **identical failure at the pinned base** — pre-existing, not introduced |

**The `deps --who-imports` command measured nothing, twice, in my hands.** The
first invocation hit the shim's home-binding refusal; the second returned no
verdict lines because my filter matched none. I am not reporting a number from
it. The structural check above establishes clause 1 without it, and reporting
the check that worked is better than reporting a number I did not obtain.

## Where the bugs probably are

1. **`SI-12-DF-05` is the finding that matters most, and it reaches my own
   reporting.** `test_graph/build-logic` is an included build that is gitignored
   (`test_graph/.gitignore:30`) and tracked by **zero** files, so the three
   graphs every epic ticket is told to run as its regression gate **cannot run in
   any fresh ticket worktree**. I confirmed it: present in the epic worktree,
   absent in SI-12's, and failing identically at the pinned base control.
   **Every "three graphs green" in waves 1–4 was therefore measured from the epic
   worktree, never from a ticket's.** Those claims were true about the place I
   ran them and did not say so. SI-13 now has a concrete first target.
2. `SI-12-DF-03` — the layout guard scans `skills/*/scripts` only, so a sweep of
   all 1,348 tracked files finds 10 offending lines while the test reports 9
   passed. A guard whose negative result is indistinguishable from not looking:
   the epic's signature defect, now in a check the epic itself shipped.
3. `SI-12-DF-04` — `skills/discovery/skill-project.toml` still declares a coord
   for a skill the bundle contains, which re-materialises a standalone copy in
   any home that resolves it. That is precisely what `GOAL-one-unit` clause 1
   measures, so it is a live threat to the goal this wave just advanced.
4. `SI-02-DF-01` remains **open and was honestly reported as such** —
   `verify.sh` now runs but still exits 1, with 1,147 of 1,666 lines from inside
   the gitignored home. Nesting did not close it, and the ticket said so instead
   of claiming the adjacent win.
5. Two changes ship **unexercised**: an assertion edit in
   `git-integration-repo/scripts/selftest.sh:582`, and roughly ten hand-written
   `plugins/*/skills/` rungs in markdown that no guard reads (that gap is
   DF-03). Verified once behaviourally, then reused by hand.

## My own errors this wave

Four waves running, the same class. This wave: `echo "EXIT=$?"` after a pipe
captured `tail`'s status and reported **rc=0 under a traceback**; a `diff`
against a non-existent `current/` errored beneath a pre-written "(no output
above = identical)"; the zsh `:s` history-modifier bug bit a `git show` for the
second time this epic, **after I had recorded it in memory**; and
`deps --who-imports` returned nothing twice while I was using it to verify
someone else's claim. SI-12's agent reported the identical class independently —
a zsh glob that aborted a `find` and reported "none" having scanned nothing, an
`awk` that died on every file, and `$?` after a pipe again.

**That two independent agents produced the same failure mode in the same wave,
on a substrate whose stated purpose is self-improvement, is the finding.** The
remedy SI-12 names is right and belongs in the repository's own checks: rewrite
the sweep in Python with an **explicit non-vacuity assert**, so a check that
scanned nothing cannot report clean.

## Suggested next steps

**Wave 6, the next gate:** SI-09 (#342), progressive disclosure — now across
**eight** cards, with `git-integration-repo` and `plugin-repository` added to the
set by this wave.

**Deferred findings: 66 rows.** `per_ticket_backlog` still not adopted; wave 5
was a single ticket so it cost nothing again, and waves 6 onward are single
tickets too — but SI-08 files against **eight** goals now, and that is the run
where the shared file collides.

**Goal trajectory.** `GOAL-one-unit` clause 1 moves from *unsatisfiable* to
*satisfied in the project tier* — the measurement that justified this ticket now
returns zero. Clauses 2 and 3 are unchanged: clause 2 cannot be evaluated while
`SI-12-DF-05` stands, which is a result about the instrument rather than the
goal. `GOAL-no-new-gates` held — no refusal path added.

**Standing worktrees:** eleven. `wt-359` is clean and can be swept with the rest
after the epic's default-branch merge.

**DCO fails on PR #363** as on every PR in this repository (258+ commits since
main, 55 signed). Advisory here, branches unprotected. Owner decision at the epic
PR.
