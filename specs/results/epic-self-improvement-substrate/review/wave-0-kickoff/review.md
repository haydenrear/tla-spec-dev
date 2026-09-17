# Kickoff review — epic/self-improvement-substrate

Range: `b7a7d203` (main tip, epic base) → `2d659978` (+ this commit).
Date: 2026-09-17. Policy in force: `review_policy.cadence: wave`, `gate: true`,
`merges: owner`. This is the pre-wave review; no ticket has been dispatched.

## 1. Decisions the owner has taken

| # | Decision | Where it now lives |
|---|---|---|
| 1 | The plugin is `tla-spec-dev`; the skill inside is `spec-double-2` | SI-01 scope; every assignment's conflict keys |
| 2 | `spec_double_compiler` (package) and `tla-spec-dev` (CLI) keep their names | SI-01 scope — 666 references, no payoff in churn |
| 3 | Only the five workflow skills nest. `debugging`, `git-integration-repo`, `plugin-repository` stay standalone | SI-02; SI-06 drops `debugging` from its scope |
| 4 | Upstreams frozen — **but the freeze happens after migration**, so upstream work must still reach this repo until then | `migration/pulling-upstream.md` |
| 5 | The **epic agent owns all TLA+ work**: it scaffolds desired/current per ticket, validates, closes, promotes, places anchors. Ticket agents move current toward desired and may make only small edits to desired | `planning_rules.model_ownership_rule`; the *Model ownership* block in all ten assignments; SI-07 writes it into the skill |
| 6 | Review gates every wave; the epic agent merges | `review_policy` |
| 7 | Deferment `batch`, budget 5, appending to the cumulative backlog | `deferment_policy` |
| 8 | The two orphan commits are pushed upstream first, then nested | Done — see §3 |

Decision 5 reverses `git-epic-workflow` SKILL.md rule 5 and restores the
two-directory loop **for epic tickets only**; standalone tickets stay
desired-only, as `fix/simpler-diagrams` left them.

## 2. What landed

- `epic/self-improvement-substrate` created and pushed. Kickoff `f896fce5`,
  follow-ups `2d659978`. Epic worktree at `../wt-epic-self-improvement-substrate`
  with its own Skill Manager home.
- Shared spec workflow scaffolded; both manifests retitled to the epic slug.
- Canonical plan: **10 tickets, 6 waves, 7 goals**, validator exit 0, no
  warnings.
- Ten assignments **rendered from the plan** by a script rather than by hand,
  pushed to #334–#343, each validated against what GitHub holds — all exit 0.
  Two new issues created: #342 (SI-09) and #343 (SI-10).
- The GitHub blocking DAG mirrors `depends_on` exactly.
- Kickoff baselines measured on `b7a7d203` before any ticket landed, after both
  homes were synced to their remote tips.
- Both homes synced fully (owner say-so, this kickoff only).

## 3. Machinery friction, and what was done about it

Four things went wrong or were found wrong while scaffolding. Two are fixed, two
are filed.

**Fixed during kickoff:**

- `skt ticket new` could not bootstrap the epic worktree's home: the only CLI
  candidate it found was the root home's entrypoint, which refuses to act on
  another home. Its own diagnostic named the remedy (unset `SKILL_MANAGER_HOME`
  first). The worktree rolled back cleanly — no stray branch, path or retention
  ref. Re-run with the environment unset, it worked, and the home it produced was
  verified to be a clone of the **project** home rather than the root home.
- `git-issue` `1f91074b` and `git-issue-workflow` `4eeb350d` existed only in the
  gitignored project home — the predecessor epic's "spec workflow NOT REQUIRED by
  default" and "no ticket-local `current/`" work. Both are now on their
  repositories' `main`, verified by `merge-base --is-ancestor` from the project
  root. `skt publish` refused them (it requires `--ticket` and would raise a
  review branch on repositories being retired), so the push was made with git and
  the units were synced one tier up first.

**Filed, `pending`, backlog 33 → 35 rows:**

- `SIS-KICKOFF-F-01` (minor) — the evaluation-ticket assignment schema drifts
  three ways. `git-epic-workflow/references/epic-ticket.md` and
  `git-issue/references/epic-assignment.md` both *show* `contribution: "guard"`,
  and the canonical plan requires it, while `validate_assignment.py` warns
  against exactly that. SI-08's correct assignment warns seven times, once per
  owned goal. Natural home: SI-07.
- `SIS-KICKOFF-F-02` (major) — `command -v tla-spec-dev` resolves to the
  operator's root-home shim, not this checkout, so any bare-command measurement
  may describe an installed clone. Known for eval runs; live in an ordinary
  working tree too. Candidate home: SI-10.

Neither was retrofitted into a dispatched ticket.

## 4. Upstream integration, verified

Five remotes were added to this repository so upstream skill work can be pulled
in from the project root alone. The mechanism was **proved, not asserted**: on a
throwaway worktree, `git subtree add --prefix=skills/discovery discovery main`
produced ordinary tracked files (no gitlink) and `git subtree pull` re-ran
clean. The probe worktree and its branch were removed. Full recipe and the
owner's remaining choices: `migration/pulling-upstream.md`.

No upstream repository currently holds work this home lacks. Every remote tip is
already in the project home; the only ref anywhere newer than `main` is
`test-graph/skill/def-005-env-timeout-test-graph` (`6c9c73d3`, Sep 10), which is
not on `main` and was left alone.

## 5. Where the risk is

- **Wave 3 is four tickets on one repository.** Their conflict keys are disjoint
  by file, but SI-04 defines the `skill_change` field while SI-05 writes
  dispositions using it, in the same wave with no dependency edge between them.
  That was deliberate — an edge would have forced them into separate waves — and
  it is the most likely place for a reconcile at merge.
- **SI-09 touches every card** the other tickets edit, which is why it runs last;
  if earlier waves slip, it is the ticket that absorbs the churn.
- **Two goals build their own instruments** (`GOAL-blockers-propose`,
  and the card `GOAL-findings-become-changes` depends on). Their baselines are
  honestly `unmeasured` / "no such instrument exists" and must stay that way
  until SI-03 and SI-04 land.
- **Six wave gates for ten tickets** is a lot of stopping. It is what the policy
  says; it is also the cheapest thing to change, and changing it is a recorded
  plan amendment rather than silence.

## 6. Open decisions

1. **Dispatch wave 1 (#334) now?** It is ready and validated.
2. **Keep six wave gates, or collapse to fewer?** Recommendation: gate waves 2,
   4 and 6 — after the migration, after the epic-agent rules, and at evaluation.
3. **`--squash` or full upstream history** when SI-02 nests each skill.
   Recommendation: full history, so `subtree pull` stays cheap until the freeze.
4. **Disposition of `SIS-KICKOFF-F-01` and `-F-02`**: promote to tickets now,
   keep batched, or `wontfix`. Recommendation: keep batched; both have named
   homes in SI-07 and SI-10.
5. **When the freeze starts** — after SI-02, on your word.

## 7. Standing worktrees and headroom

Two worktrees: the main checkout and the epic worktree. 88 GB free (up from 27 GB
at kickoff, after the probe cleanup and unrelated reclaim). No ticket worktrees
exist yet; each wave adds one per ticket, all swept at the end of the epic.
