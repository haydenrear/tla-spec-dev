# Wave 3 review — epic/self-improvement-substrate

Range: `994f650c` → `7c5d34a6`. Five tickets — SI-04 (#337), SI-05 (#338),
SI-06 (#339), SI-10 (#343), SI-11 (#351) — the widest wave of the epic.

**Not a gate.** `milestones: [2, 4, 6]`. The artifact is produced and wave 4
dispatches without waiting. The next stop is after wave 4.

## 1. What landed

- **One improvement record** (SI-04). `skill_change: none | proposed(<unit>, <ref>)
  | applied(<commit>) | declined(<reason>)` plus a `goal:` link, carried by all
  four record files, read by **one** reader — `improvement_ledger.py` wraps
  `disposition.py` rather than duplicating it, pinned by a test that also asserts
  `safe_load` never appears in the ledger.
- **The close-out disposes of findings** (SI-05). `recorded-local` **13 → 0**:
  7 applied, 2 declined, 4 proposed with diffs. `close ticket` names every
  finding that owes a change and **proceeds** — one warning line, never a refusal.
- **Blocked agents propose** (SI-06). `## Skill changes proposed` in one canonical
  wording across the ticket-side skills, plus the ticket-agent half of the
  model-ownership boundary.
- **The plugin carries its own evals** (SI-10). Seven cases, one per nested skill,
  run by `evals/run.sh` against the checkout — no symlink shim, no
  `units-override.txt`.
- **Every script and binding resolves under the plugin layout** (SI-11), and
  `SIS-W2-F-05` is fixed: `cli: 15 installed, 2 failed` → **17 installed, 0
  failed** into a fresh home.

## 2. Verified, not accepted

Every load-bearing claim re-checked against the tree, by failure **name** rather
than count. All five: **zero new failures**.

| ticket | repository | spec-unit | graphs | backlog |
|---|---|---|---|---|
| SI-04 | 10→10 (1594→1613 passed, +19 its tests) | 7/7 both targets | ✅ | 49 rows, 0 lost |
| SI-05 | 10→10 (1594→1601, +7) | 7/7 | ✅ | untouched, deliberately |
| SI-06 | 10→10 (1594 passed) | 7/7 | ✅ | 48 rows, 0 lost |
| SI-10 | 10→10 | 7/7 both targets | ✅ | 46 rows, 0 lost |
| SI-11 | 10→10 (1601, +7) | 7/7 | ✅ | 50 rows, 0 lost |

Integrated, on `7c5d34a6`: **10 failed / 1627 passed / 6 skipped**, same ten
names; all three graphs green; TLC unchanged at 1,321 distinct states.

Three claims were **wrong and are recorded as wrong**:

- SI-11: "`wt-337`, `wt-338`, `wt-339`, `wt-343` have no `.skill-manager`". All
  eight worktrees have homes. SI-11 reconstructed it itself: it looked at 07:42
  while those homes were created between 07:42:45 and 07:47:01 — **a race it
  mistook for a property**, and it filed that as the same class its own ticket
  owns.
- SI-11's two `improvement_ledger.py` citation failures: from a void run on a
  discarded tree. They do not reproduce on the integrated tip.
- SI-10's entry counts (98,814 / 6,296) versus the epic agent's (70,721 / 7,345):
  different trees at different times. The conclusion holds — the checkout is
  3–5× over the 20,000 limit, the staged view comfortably under — the exact
  figures are tree-specific and should not be quoted as universal.

## 3. Epic-agent errors this wave

Four, all mine, none of which reached a committed artifact but three of which
produced a false statement first.

1. **I raised a false alarm and then falsely retracted a true finding.** A buggy
   shell `case` printed the loop's last path instead of each URL, so I announced
   that the whole clone's `origin` pointed at a worktree. It did not, at that
   moment — but SI-04 and SI-05 had *independently* observed exactly that
   earlier, and SI-05 had repaired it with `git remote set-url` before my probe
   ran. So `SI-04-DF-04` is real and corroborated; my "cannot reproduce" was an
   artifact of arriving after the fix, and my dismissal of my own alarm was
   itself wrong.
2. **I merged three PRs without running `gh pr checks`.** DCO was failing on all
   of them. Advisory, nothing bypassed — but SI-06 caught it, not me.
3. **Three greps too broad, three near-miss false findings**: SI-04 reported as
   touching SI-11's territory (it touched its own declared keys), SI-10 likewise,
   and `github-action.py` reported as unfixed when my pattern had matched the
   *comment explaining the fix*.
4. **Two blank results I nearly reported as failures** — the graph runner and
   `home close-out` both worked; my filters discarded their output. The graph
   entry point is `skills/test-graph/scripts/run.py`, and the close-out verdict
   reads "holds nothing that removing it would destroy", which none of my grep
   terms matched.

The pattern in my own errors is the same one the wave kept finding in the
substrate: **a check whose negative result is indistinguishable from not having
looked.**

## 4. The shape this wave found three times

Three defects, one structure: **a shared mutable namespace with no per-agent
partition, where collision is certain rather than careless.**

- **The cumulative backlog.** Four tickets appending to one file's end. My
  instruction to re-fetch stopped them overwriting each other — every branch
  showed zero deleted lines — but could not stop them colliding. `conflict_keys`
  cannot express it, because each ticket legitimately owns only *its own rows*.
- **`.git/info/exclude`** (`SI-06-DF-03`). `bootstrap-home.sh` wrote `/specs/`
  and `/evals/` into the clone's shared exclude. All nine worktrees silently
  stopped seeing new files under those paths. **52 files across three tickets**
  were hidden, including SI-10's entire 40-file deliverable. Found mid-wave,
  repaired, recovered; SI-11 took the guard and proved it against the **index**
  rather than the working tree.
- **The scratchpad.** Several agents wrote the generic name `pr-body.md`;
  SI-11's overwrote SI-06's at 08:32. Caught only because SI-06 grepped the file
  before using it. One `gh pr edit --body-file` would have silently replaced its
  PR body with SI-11's. SI-06 deliberately did **not** file it — filing would
  have handed the epic agent a 54th-row conflict mid-merge.

SI-06's judgement on the remedy is the one to take: prefer a **per-ticket
findings file merged at wave close** over a union merge driver, because a union
driver "silently produces a valid-looking file when it is wrong" — the exact
failure mode `SI-06-DF-03` was about. A per-ticket file makes the merge a no-op
instead of a resolution.

## 5. Where the bugs probably are

1. **The known-10 failures are load-bearing and nobody owns them.** Ten per
   manifest of the surviving `spec_manifest.yaml` citations are cases the checker
   *refuses to guess* — the anchor appears on 0, 2, 3 or 4 lines. `--fix` repaired
   15; these ten cannot be repaired mechanically, and choosing among candidate
   lines is authoring. They will fail every wave until someone decides them.
2. **`skill-script:` deps on a contained skill have no working spelling**
   (`SI-11-DF-01`). The resolver probes `<home>/skills/<unit>/` and
   `<home>/plugins/<unit>/` and nothing else; contained-skill names never reach
   it. SI-11 worked around it by moving the installers to the plugin root. The
   resolver gap is unfixed and lives in skill-manager, outside this repository.
3. **A failing graph node deleted 27 tracked files of `test_graph/` itself**
   (SI-11), taking the next two graphs with it. Restored, root cause fixed, but a
   harness that deletes its own project on failure deserves its own ticket.
4. **`selftest.sh` died at step 15 of 30 and exited 0** on bash 3.2. Two new
   sections had been validating vacuously. Same silent-vacuity shape as the
   exclude bug and the push that never left the machine.
5. **`skt ticket new` failed for four of five agents**, rolling back the worktree
   and branch, with the three unreachable units being exactly the three this epic
   moved into the plugin. All four fell back to the documented by-hand route and
   all four reported it, as rule 10 requires.

## 6. The standing debt nothing tracks

Twice now — SI-01 and SI-11 — a ticket agent has corrected the **epic-owned**
workspace so its ticket could run, obliging the epic agent to make the matching
change to `specs/current`, `specs/program_model` and `specs/desired_program_model`.
That change can only be committed *after* the ticket merges, so between the two
there is a window where the model and the tree disagree: `BuildSkillCli` reported
`accepted: false` for exactly that interval.

The rule works. What is missing is a ledger: **"model corrections owed by merged
tickets"** belongs as an explicit block in the wave-close checklist, beside the
four SI-07 is adding. Recommended, not implemented.

## 7. Suggested next steps

**Wave 4, ready:** SI-03 (#336) the improvement card, and SI-07 (#340) the epic
agent owns the model. SI-07 now has five findings addressed to it
(`SIS-KICKOFF-F-01`, `-F-03`, `-F-04`, plus the debt above and the wave-review
blocks), which is more than its issue anticipated.

**Deferred findings: 25 pending of 58 rows.** Wave 3 filed 13 — SI-04 four,
SI-06 three, SI-10 one, SI-11 five. None blocking.

**Goal trajectory.** `GOAL-findings-become-changes` moved for the first time:
`recorded-local` 13 → 0 on the branch, and its instrument exists.
`GOAL-one-unit` clause 3 is now satisfiable — the plugin installs from
`github:haydenrear/tla-spec-dev-plugin` with `SOURCE: git`, no
`NEEDS_GIT_MIGRATION`, and 17 change-managed units.
`GOAL-evals-one-command` has its seven cases. `GOAL-blockers-propose` has its
shape but not yet its card — SI-03 builds that in wave 4.
`GOAL-no-new-gates` held: no guardrail was overridden by any of the five.

**Standing worktrees:** eight. Seven clean, `wt-334` stale-but-safe (§merges.md).
All swept together after the epic's default-branch merge.
