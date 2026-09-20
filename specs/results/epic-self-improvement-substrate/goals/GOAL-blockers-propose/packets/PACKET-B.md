======================================================================
SUBJECT: pull request #375 (ticket SI-15), subject_shape=ticket
======================================================================

ITEM 1 — THE PULL REQUEST BODY, VERBATIM
----------------------------------------------------------------------
## SI-15: one place for every eval

Refs #333. Moves skill-manager's eval cases into this plugin's `evals/`, so one
command runs the loop's whole suite against one environment.

**7 cases → 61**, in one `evals/` tree, run by `evals/run.sh`.

### The counts, corrected

The ticket briefed "63 cases" and told me to count sources rather than build
output. **63 *is* the build-output number.** Measured:

| `find specs/evals/harness/evals -name case.yaml` | 63 |
| …`-not -path '*/build/*'` | **55** |
| …`-path '*/build/*'` | 8 |

So: **55 sources**, 54 moved, 1 left behind with a reason, **61 here now**
(54 + this plugin's own 7). Filed as `SI-15-DF-01`. Case **names** are recorded
before and after and compared as sets, never as counts —
`tickets/SI-15/names-before.txt`, `names-after.txt`, `local-signal.txt`.

### The entry ceiling was never close

Briefed as "the likeliest thing to bite you", with the view "already at 17,370".
**Not reproducible at this base.** Measured by replicating `run.sh`'s own
tar-exclude list:

| staged view, before the move | **6,712** |
| after materialising + staging the toolchain | 6,848 |
| after all 54 cases moved in | **7,288** |
| final, including this ticket's evidence files | **8,099** (headroom **11,901**) |

The likely cause of the gap: `.toolchain/skill-manager` is 11,522 entries and
declares `stage_into_view = ""` — it is reached by PATH shim and deliberately
never staged. Only `skt` stages, at 183. A count over `.toolchain/` rather than
the view reads ~17–18k. `run.sh`'s header still claims 6,264, also stale; that
is prose, and the script computes the real figure at run time. `SI-15-DF-03`.

### No moved case declares `plugins:`

All 55 sources declared it; **0 of 61 cases do now**, asserted mechanically.
This was the measured hazard (`SI-14-DF-01`): a `plugins:` entry silently loses
the target plugin's hooks while **both arms still score 1.00**. Every fixture
here is placed by a `SessionStart` hook, so a surviving entry would have handed
the agent an empty workspace and scored it as a skill failure.

The unit a moved case is *about* is delivered by the view instead: `run.sh`
stages the **pinned** `skt`'s skills into `<view>/skills/`, so the 18 `w-skt`/
`w-sm` cases load their subject at the commit `toolchain.lock.toml` names rather
than whatever the operator's home holds — which is what SI-14 bought
(`GOAL-pinned-eval-toolchain`). It is cheap (183 entries) and safe: the pinned
skt ships **no** `case.yaml`, so it cannot contribute cases to our discovery the
way the 11,481-entry skill-manager checkout would. Staged, never committed.

### Which environment each case needs — the honest split

- **45 cases** are *transcript-graded*: they ask which command the agent reached
  for. `plugin eval` has no grader for that, so the wide lane's `expect.py` is
  **vendored** to `evals/lib/checks/expect.py` (self-test green under both
  `/usr/bin/python3` 3.9 and `python3`). One change: the lookup searches
  `evals/<unit>/<case>/expect.json` rather than a flat path. `verify.sh` reads
  the Stop hook's stdin **lazily** — an unconditional read would hang the
  repository's own forged-workspace control, which runs `sh verify.sh` directly.
- **6 cases need a real branched Skill Manager home** (~41,000 entries, ~5 GB).
  That is above the 20,000 plugin ceiling *by itself*. They move and are
  declared **UNDECIDED** — `place.sh` says so in the run's trace and
  `verify.sh` writes `.eval/UNDECIDED-needs-home`. They are **not** handed an
  empty workspace and scored 0, which would read as "the agent could not
  provision a home". `SI-15-DF-05`.
- **`sandbox-probe` did not move.** Its `the-workspace-is-writable` grader is a
  deliberate standing red reading `path: probe-write`, which
  `test_no_grader_reads_a_path_the_agent_can_simply_write` forbids here, and
  `tests/**` is outside my conflict keys. `SI-15-DF-02`.

### `units-template/` and `wide/` — decided, not omitted

- **`units-template/` is retired, not moved.** Its three units (`toolchain`,
  `fixture`, `verify`) exist *only* to deliver hooks through a case's
  `plugins:` key — the mechanism that silently disables the target plugin's
  hooks. This plugin already does all three jobs from its own staged
  `hooks/hooks.json`. Moving them would re-import the defect.
- **`wide/` is retired.** `wide/run.sh` + `wide/setup.sh` *are* the second
  harness the goal names. Its one piece of independent value, `expect.py`, is
  vendored here. `units-override.txt` machinery dies with `wide/setup.sh`, and
  **0** of the 55 sources carried one — so the override route is gone rather
  than merely unused, which is the target's "no units-override file" clause.

### Regression

- **Repository suite: identical failure NAMES before and after** — the same 10
  known failures, no new ones, none fixed. `baseline-repository-suite.txt` vs
  `final-repository-suite.txt`.
- **Graphs via the skill runner** (`python3 skills/test-graph/scripts/run.py`):
  `specWorkflow` **exit 0**, `cliWorkflow` **exit 0**, both BUILD SUCCESSFUL.
- 61/61 cases parse; every `EVAL_CASE` matches its directory; every case has an
  arm in **both** `place.sh` and `verify.sh` (the repository's own conservation
  check, asserted by the generator rather than discovered in CI).

**What I could NOT verify, stated as unverified:** I did **not execute** the 61
cases. A full suite is 61 billed agent runs; nothing here reports a score, and I
make no claim about whether any moved case is green. What is verified is that
they load, declare no `plugins:`, resolve their fixture and verdict arms, and
that the grant derives across the whole suite. The claim "each case reported
green, red or UNDECIDED" belongs to SI-08, which `decided_by` names.

### Deferred findings

Appended to **`specs/results/deferred/SI-15.yaml`** (the per-ticket backlog
adopted this wave), not to the cumulative file, which I left read-only:
`SI-15-DF-01` … `SI-15-DF-05`.

### Work in the other repository

**None.** No commit, branch or PR was made against `skill-manager`; its cases
were read and copied, and that checkout is untouched.

## Skill changes proposed

| unit | what I hit | proposed change |
|---|---|---|
| `skt` | `skt ticket new` printed "worktree rolled back" and **exited 0** — the 8th occurrence of `SI-11-DF-04` this epic. It failed because it resolved `bootstrap-home.sh` from the **project** home, which lacks `git-issue-workflow`, while the **root** home has it. | (1) exit non-zero on rollback; (2) fall back to the root home's `bootstrap-home.sh`, or declare `git-issue-workflow` in `skill-project.toml` so `project resolve` can rebuild the project home with it. Filed as `SI-15-DF-04`; the fix is upstream in the skt plugin, not in this worktree. |

## Review input

**Hot spots I created.** `evals/lib/verify.sh`'s lazy stdin read — if a future
edit hoists it to the top of the file it will hang the forged-workspace control.
The 54 generated arms in both hooks: they are correct now, but a case added by
hand without arms fails in the silent direction. `run.sh`'s skt staging skips a
unit when `<view>/skills/<name>` already exists; that guard is what stops a
pinned copy grading over a nested skill under review.

**Decisions and overrides nobody asked for.** Leaving `sandbox-probe` behind.
Retiring `units-template/` rather than porting it. Grouping cases by the unit
they exercise (`evals/<unit>/<case>/`) rather than flat. Parking two cases about
un-nested units under `evals/unnested/` so the fact is visible in the tree.
Deleting each moved case's `setup.sh`/`run.sh`, which sourced a `lib.sh` that
did not move and would otherwise be dead scripts that look runnable. Renaming
`spec-double-compiler` in five moved **fixtures** but deliberately **not** in
`place.sh`/`verify.sh`/`TOOLCHAIN.md`, where it names a real on-disk
`.spec-double-compiler/tla2tools.jar` path and a genuinely still-installed unit.

**Where I would look for bugs in my own change.** The regex re-quoting: 16
graders moved from double-quoted YAML to single-quoted, where backslashes stop
being escapes. I parse the value as YAML and assert it round-trips unchanged,
but these patterns are only truly exercised by a scored run, which I did not do.
Second: `expect.py`'s grouped lookup — if a case's `expect.json` is ever missed,
**no** verdicts are written and every grader below it reds for a reason that is
not the agent's; it writes `WHY-NO-VERDICTS.txt`, which is the only thing that
would say so. Third: the fixture/grader rename mismatch I caught late — graders
said `spec-double-2` while fixtures still said `spec-double-compiler`, which
would have reddened correct answers. I fixed the five I found by sweep; a
different spelling would have slipped past.

**Machinery friction.** `skt ticket new` costing a rollback and a 0 exit is the
single biggest one (above). The "63 cases" figure sent me to count the thing I
was told not to count. The "17,370 entries" figure framed the entry ceiling as
the main risk when the real headroom was ~12,000, which shaped a design against
a constraint that was not binding. `tests/test_agent_integration_harness.py`'s
requirement that every case have a literal `<name>)` arm in both hooks is a
*good* check but is discoverable only by reading the test — nothing in the eval
docs says a new case needs two arms.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01DUdxjqPbjrJ45Bpxw8uZeS



ITEM 2 — THE SUBJECT'S OWN COMMITS (git log --stat)
----------------------------------------------------------------------
commit 9ba955b7ef88f8c68dc0569c9186ca82a46a45e1
Author: hayden.rear <hayden.rear@gmail.com>
Date:   Sun Sep 20 09:41:43 2026 -0400

    SI-15: one place for every eval -- 54 cases move into the plugin's evals/
    
    The development loop's evals were split across two repositories and two
    harnesses that shared no runner: 7 cases here, and 55 sources in skill-manager
    run by eval_run_case() in a 43,330-byte lib.sh against a branched Skill Manager
    home built per case. Nothing ran them together. `claude plugin eval` runs on a
    PLUGIN -- this repository is one, skill-manager is not -- so the cases move
    here. 7 -> 61, in one tree, run by one command.
    
    THE COUNT. The ticket said 63 sources and told me not to count build output;
    63 IS the build-output number (55 sources + 8 build copies). Filed SI-15-DF-01.
    
    THE CEILING WAS NEVER CLOSE. Briefed as the likeliest hazard at "17,370
    entries". Measured on the view run.sh actually stages: 6,712 before, 6,848 with
    the toolchain, 7,288 after the move, 8,099 final -- 11,901 of headroom under
    20,000. Filed SI-15-DF-03.
    
    NO MOVED CASE DECLARES `plugins:`. All 55 sources did; 0 of 61 do now, asserted
    mechanically. A `plugins:` entry silently loses the target plugin's hooks while
    both arms still score 1.00 (SI-14-DF-01), and every fixture here is placed by a
    SessionStart hook -- so a survivor would have handed the agent an empty
    workspace and scored it as a skill failure. The unit a moved case is ABOUT is
    delivered by the view instead: run.sh stages the PINNED skt's skills into it, so
    those cases load their subject at the pinned commit rather than whatever the
    operator's home holds (GOAL-pinned-eval-toolchain).
    
    THE HONEST SPLIT, rather than a forced merge that quietly disables half the
    suite:
      * 45 cases are transcript-graded. The wide lane's expect.py is vendored to
        evals/lib/checks/expect.py (self-test green on python3.9 and python3);
        verify.sh reads the Stop hook's stdin LAZILY, because an unconditional read
        would hang the repository's own forged-workspace control.
      * 6 cases need a real branched Skill Manager home (~41,000 entries, above the
        ceiling by itself). They move and are declared UNDECIDED in the run's own
        trace, not handed an empty workspace and scored 0. Filed SI-15-DF-05.
      * sandbox-probe did not move: its grader is a deliberate standing red reading
        a path the agent writes, which a repository test forbids here, and tests/**
        is outside this ticket's conflict keys. Filed SI-15-DF-02.
    
    units-template/ and wide/ are RETIRED, not moved, and the reasons are recorded:
    units-template exists only to deliver hooks through `plugins:`, the mechanism
    that disables them; wide/ IS the second harness the goal names. 0 of 55 sources
    carried a units-override.txt, so that route is gone rather than merely unused.
    
    Every case has an arm in BOTH place.sh and verify.sh -- the repository's own
    conservation check, asserted by the generator rather than discovered in CI.
    
    Regression: repository suite failure NAMES identical before and after (the same
    10 known failures, 0 new, 0 fixed); specWorkflow and cliWorkflow both exit 0 via
    skills/test-graph/scripts/run.py. NOT VERIFIED: the 61 cases were not executed
    -- that is 61 billed agent runs, and no score is claimed here. SI-08 decides it.
    
    Refs #333
    
    Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
    Claude-Session: https://claude.ai/code/session_01DUdxjqPbjrJ45Bpxw8uZeS

 evals/README.md                                    |  62 +-
 .../epic-provisions-a-ticket-worktree/case.yaml    |  33 +
 .../front-door.conf                                |   5 +
 .../graders/issues-the-front-door-command.md       |  15 +
 .../nothing-outside-the-sandbox-was-touched.md     |  14 +
 .../graders/one-command-not-a-reconstruction.md    |  25 +
 .../graders/reaches-a-skill.md                     |  13 +
 .../graders/skill-before-shell.md                  |   9 +
 .../graders/the-command-it-chose-actually-works.md |  15 +
 .../graders/the-worktree-has-its-own-home.md       |  11 +
 .../case.yaml                                      |  23 +
 .../expect.json                                    |   9 +
 .../fixture/issue-142.md                           |  75 +++
 .../graders/does-not-force-a-wrong-base.md         |   8 +
 .../graders/names-pr-base.md                       |   7 +
 .../graders/runs-the-validator.md                  |   7 +
 .../graders/within-budget.md                       |   9 +
 .../w-epic-force-when-owner-decided/case.yaml      |  30 +
 .../w-epic-force-when-owner-decided/expect.json    |  19 +
 .../fixture/ticket_plan.yaml                       |  89 +++
 .../graders/does-not-rewrite-the-plan.md           |   8 +
 .../graders/uses-the-sanctioned-override.md        |   8 +
 .../graders/within-budget.md                       |  12 +
 .../w-epic-merged-by-is-epic-owner/case.yaml       |  25 +
 .../w-epic-merged-by-is-epic-owner/expect.json     |   5 +
 .../graders/assignment-keeps-epic-owner.md         |   8 +
 .../graders/plan-records-human.md                  |   8 +
 .../graders/stays-cheap.md                         |   8 +
 .../w-epic-plan-free-form-lane/case.yaml           |  24 +
 .../w-epic-plan-free-form-lane/expect.json         |  19 +
 .../fixture/ticket_plan.yaml                       |  79 +++
 .../graders/leaves-the-lanes-alone.md              |   8 +
 .../graders/reports-ready.md                       |   7 +
 .../graders/runs-the-validator.md                  |   7 +
 .../graders/within-budget.md                       |   9 +
 .../case.yaml                                      |  30 +
 .../expect.json                                    |   9 +
 .../fixture/ticket_plan.yaml                       |  99 +++
 .../graders/does-not-rescope.md                    |   9 +
 .../graders/runs-the-validator.md                  |   7 +
 .../graders/treats-it-as-advisory.md               |  19 +
 .../graders/within-budget.md                       |   9 +
 .../case.yaml                                      |  28 +
 .../expect.json                                    |  13 +
 .../fixture/bootstrap.txt                          |  12 +
 .../graders/does-not-upgrade-a-current-cli.md      |  10 +
 .../graders/names-the-home-mismatch.md             |  14 +
 .../graders/within-budget.md                       |  12 +
 .../w-giw-epic-ticket-plan-values-win/case.yaml    |  32 +
 .../w-giw-epic-ticket-plan-values-win/expect.json  |  13 +
 .../fixture/issue-141.md                           |  71 ++
 .../fixture/ticket_plan-CA-03.yaml                 |  15 +
 .../graders/lists-the-mismatch.md                  |  22 +
 .../graders/proceeds-to-provision.md               |   8 +
 .../graders/within-budget.md                       |   9 +
 .../case.yaml                                      |  29 +
 .../expect.json                                    |   9 +
 .../fixture/issue-141.md                           |  75 +++
 .../graders/names-pr-base.md                       |   8 +
 .../graders/read-the-assignment.md                 |   8 +
 .../graders/stops-before-provisioning.md           |   9 +
 .../graders/within-budget.md                       |   9 +
 .../case.yaml                                      |  32 +
 .../expect.json                                    |   9 +
 .../fixture/bootstrap.txt                          |  11 +
 .../fixture/demo-skill/SKILL.md                    |   8 +
 .../graders/does-not-chase-the-links.md            |   9 +
 .../graders/fixes-the-unit.md                      |   9 +
 .../graders/names-the-frontmatter.md               |   7 +
 .../graders/within-budget.md                       |   9 +
 .../case.yaml                                      |  30 +
 .../expect.json                                    |  20 +
 .../fixture/close.txt                              |  10 +
 .../graders/does-not-discard-the-work.md           |   9 +
 .../graders/read-the-refusal.md                    |   8 +
 .../graders/surfaces-the-blocker.md                |  15 +
 .../graders/within-budget.md                       |   9 +
 .../w-giw-wt-new-dirty-ok/case.yaml                |  31 +
 .../w-giw-wt-new-dirty-ok/expect.json              |  24 +
 .../w-giw-wt-new-dirty-ok/fixture/refusal.txt      |   7 +
 .../graders/issues-the-front-door.md               |   9 +
 .../graders/leaves-the-users-edits-alone.md        |   9 +
 .../graders/proceeds-past-the-dirty-tree.md        |   8 +
 .../w-giw-wt-new-dirty-ok/graders/within-budget.md |   9 +
 .../w-giw-wt-refusal-quotes-subject/case.yaml      |  23 +
 .../w-giw-wt-refusal-quotes-subject/expect.json    |   9 +
 .../graders/no-raw-removal.md                      |   9 +
 .../graders/reaches-the-gated-close-door.md        |   9 +
 .../graders/relays-the-subject-line.md             |  10 +
 .../graders/within-budget.md                       |   9 +
 .../w-giw-wt-stale-branch-point/case.yaml          |  29 +
 .../w-giw-wt-stale-branch-point/expect.json        |  19 +
 .../fixture/refusal.txt                            |   5 +
 .../graders/branches-from-published-tip.md         |  10 +
 .../graders/does-not-wave-off-the-check.md         |   9 +
 .../graders/within-budget.md                       |   9 +
 .../case.yaml                                      |  22 +
 .../expect.json                                    |   5 +
 .../graders/names-gated-close.md                   |   9 +
 .../graders/no-bare-worktree-remove.md             |  13 +
 .../graders/no-issue-created.md                    |   9 +
 .../w-misc-issue-names-rubric-not-copies/case.yaml |  23 +
 .../fixture/rubric.md                              |  16 +
 .../graders/does-not-copy-the-rubric.md            |  15 +
 .../graders/names-the-rubric.md                    |   9 +
 evals/harness/w-harness-smoke/case.yaml            |  24 +
 evals/harness/w-harness-smoke/expect.json          |   9 +
 evals/harness/w-harness-smoke/fixture/marker.txt   |   1 +
 .../w-harness-smoke/graders/no-writes-attempted.md |   9 +
 .../graders/the-command-was-recorded.md            |   9 +
 .../graders/the-fixture-was-placed.md              |  10 +
 .../graders/the-hook-found-the-case.md             |  10 +
 .../w-harness-smoke/graders/within-budget.md       |   8 +
 evals/lib/checks/expect.py                         | 279 ++++++++
 evals/lib/place.sh                                 | 263 ++++++++
 evals/lib/verify.sh                                | 277 ++++++++
 .../w-misc-plugin-repo-finalize-sh/case.yaml       |  28 +
 .../w-misc-plugin-repo-finalize-sh/expect.json     |   9 +
 .../fixture/.claude-plugin/plugin.json             |   1 +
 .../fixture/skill-manager-plugin.toml              |  13 +
 .../fixture/skills/alpha/SKILL.md                  |   6 +
 .../fixture/skills/beta/SKILL.md                   |   6 +
 .../graders/no-finalize-constituents.md            |   9 +
 .../graders/runs-finalize-sh.md                    |   9 +
 .../graders/within-budget.md                       |   8 +
 .../case.yaml                                      |  23 +
 .../expect.json                                    |   9 +
 .../graders/no-real-install.md                     |  10 +
 .../graders/says-not-sandboxed.md                  |   9 +
 .../graders/verdict-is-unsafe.md                   |  14 +
 evals/run.sh                                       |  46 ++
 .../bootstraps-a-home-for-a-repo/case.yaml         |  26 +
 .../bootstraps-a-home-for-a-repo/front-door.conf   |  10 +
 .../graders/a-real-home-appears.md                 |  10 +
 .../nothing-outside-the-sandbox-was-touched.md     |  11 +
 .../graders/one-command-not-a-reconstruction.md    |  10 +
 .../graders/reaches-a-skill.md                     |   9 +
 .../graders/reaches-the-bootstrap.md               |  12 +
 .../case.yaml                                      |  27 +
 .../front-door.conf                                |   3 +
 .../nothing-outside-the-sandbox-was-touched.md     |  11 +
 .../graders/one-command-not-a-reconstruction.md    |   9 +
 .../graders/reaches-a-skill.md                     |  10 +
 .../graders/reaches-close-out.md                   |  21 +
 .../syncs-a-stale-home-from-root/case.yaml         |  25 +
 .../syncs-a-stale-home-from-root/front-door.conf   |   3 +
 .../nothing-outside-the-sandbox-was-touched.md     |  11 +
 .../graders/one-command-not-a-reconstruction.md    |  14 +
 .../graders/reaches-a-skill.md                     |   9 +
 .../graders/reaches-the-currency-command.md        |  18 +
 .../case.yaml                                      |  26 +
 .../expect.json                                    |  21 +
 .../fixture/close.txt                              |  12 +
 .../graders/explains-ahead.md                      |  15 +
 .../graders/no-backwards-sync.md                   |  10 +
 .../graders/publishes.md                           |   9 +
 .../graders/within-budget.md                       |   7 +
 .../w-sm-cold-shim-means-build/case.yaml           |  27 +
 .../w-sm-cold-shim-means-build/expect.json         |   9 +
 .../fixture/jinja2-output.txt                      |   8 +
 .../graders/builds-the-artifact.md                 |   9 +
 .../graders/no-reinstall.md                        |   9 +
 .../graders/within-budget.md                       |   8 +
 evals/skill-manager/w-sm-drift-ack-once/case.yaml  |  27 +
 .../skill-manager/w-sm-drift-ack-once/expect.json  |   9 +
 .../w-sm-drift-ack-once/fixture/sync-output.txt    |   4 +
 .../w-sm-drift-ack-once/graders/acks-drift.md      |   9 +
 .../w-sm-drift-ack-once/graders/no-resync.md       |   8 +
 .../w-sm-drift-ack-once/graders/within-budget.md   |   8 +
 .../w-sm-sync-retired-name-redirects/case.yaml     |  27 +
 .../w-sm-sync-retired-name-redirects/expect.json   |  19 +
 .../graders/no-reinstall-retired.md                |  10 +
 .../graders/syncs.md                               |   9 +
 .../graders/within-budget.md                       |   8 +
 .../w-sm-sync-skt-when-absent/case.yaml            |  26 +
 .../w-sm-sync-skt-when-absent/expect.json          |  12 +
 .../fixture/sync-output.txt                        |   4 +
 .../graders/installs-skt.md                        |  10 +
 .../graders/within-budget.md                       |  11 +
 .../w-sm-verify-is-not-currency/case.yaml          |  23 +
 .../w-sm-verify-is-not-currency/expect.json        |   6 +
 .../graders/runs-a-currency-check.md               |   9 +
 .../graders/verdict-not-from-a-proxy.md            |  15 +
 .../graders/within-budget.md                       |   8 +
 evals/skt/ticket-agent-closes-a-ticket/case.yaml   |  25 +
 .../ticket-agent-closes-a-ticket/front-door.conf   |  14 +
 .../nothing-outside-the-sandbox-was-touched.md     |  11 +
 .../graders/one-command-not-a-reconstruction.md    |  12 +
 .../graders/reaches-a-skill.md                     |   9 +
 .../graders/reaches-the-gated-door.md              |  17 +
 .../graders/the-worktree-is-actually-gone.md       |  14 +
 evals/skt/ticket-agent-opens-a-ticket/case.yaml    |  28 +
 .../ticket-agent-opens-a-ticket/front-door.conf    |   5 +
 .../graders/issues-the-front-door-command.md       |  15 +
 .../no-declared-path-on-an-ordinary-ticket.md      |  13 +
 .../nothing-outside-the-sandbox-was-touched.md     |  11 +
 .../graders/one-command-not-a-reconstruction.md    |  13 +
 .../graders/the-command-it-chose-actually-works.md |  10 +
 .../graders/the-worktree-has-its-own-home.md       |   9 +
 .../skt/w-skt-check-pinned-is-not-stale/case.yaml  |  29 +
 .../w-skt-check-pinned-is-not-stale/expect.json    |  21 +
 .../fixture/check.txt                              |   5 +
 .../fixture/skill-project.toml                     |  10 +
 .../graders/explains-pin.md                        |  13 +
 .../graders/leaves-the-pin.md                      |  10 +
 .../graders/syncs-the-stale-unit.md                |   7 +
 .../graders/within-budget.md                       |   7 +
 .../case.yaml                                      |  30 +
 .../expect.json                                    |  19 +
 .../fixture/check-output.txt                       |   3 +
 .../fixture/record-vs-checkout.txt                 |   8 +
 .../graders/no-reconstruction.md                   |   7 +
 .../graders/syncs-the-unit.md                      |   8 +
 .../graders/within-budget.md                       |   7 +
 .../w-skt-check-unknown-is-not-current/case.yaml   |  24 +
 .../w-skt-check-unknown-is-not-current/expect.json |  19 +
 .../fixture/check-output.txt                       |   2 +
 .../graders/no-reconstruction.md                   |   8 +
 .../graders/read-the-output.md                     |   7 +
 .../graders/says-unknown.md                        |   9 +
 .../graders/within-budget.md                       |   7 +
 evals/skt/w-skt-is-a-plugin-not-a-skill/case.yaml  |  22 +
 .../skt/w-skt-is-a-plugin-not-a-skill/expect.json  |  16 +
 .../graders/answers-yes.md                         |   8 +
 .../graders/checked-the-cli.md                     |   8 +
 .../graders/no-manual-route.md                     |   7 +
 .../w-skt-migration-delete-project-block/case.yaml |  21 +
 .../expect.json                                    |  16 +
 .../fixture/skill-project.toml                     |   8 +
 .../fixture/status-output.txt                      |   3 +
 .../graders/declares-skt-plugin.md                 |   8 +
 .../graders/drops-the-skill-block.md               |  12 +
 .../graders/no-file-edits.md                       |   7 +
 .../graders/read-the-manifest.md                   |   7 +
 .../skt/w-skt-migration-no-import-edits/case.yaml  |  25 +
 .../w-skt-migration-no-import-edits/expect.json    |  24 +
 .../fixture/my-skill/SKILL.md                      |  10 +
 .../fixture/status-output.txt                      |   6 +
 .../graders/no-file-edits.md                       |   7 +
 .../graders/no-import-rewrite.md                   |   7 +
 .../graders/sync-skt.md                            |   7 +
 .../graders/within-budget.md                       |   7 +
 .../case.yaml                                      |  27 +
 .../expect.json                                    |  19 +
 .../fixture/installed-units.txt                    |   4 +
 .../fixture/ticket-output.txt                      |   3 +
 .../graders/installs.md                            |   8 +
 .../graders/not-sync.md                            |   7 +
 .../graders/within-budget.md                       |  10 +
 evals/skt/w-skt-remedy-without-origin/case.yaml    |  26 +
 evals/skt/w-skt-remedy-without-origin/expect.json  |  19 +
 .../graders/issued-front-door.md                   |   7 +
 .../graders/no-fetch.md                            |   9 +
 .../graders/within-budget.md                       |   7 +
 .../case.yaml                                      |  22 +
 .../expect.json                                    |  19 +
 .../fixture/artifact-report.txt                    |   8 +
 .../graders/calls-it-healthy.md                    |  12 +
 .../graders/no-rebuild.md                          |   7 +
 .../graders/read-the-report.md                     |   7 +
 .../graders/within-budget.md                       |   7 +
 evals/skt/w-skt-sweep-requires-epic/case.yaml      |  26 +
 evals/skt/w-skt-sweep-requires-epic/expect.json    |  19 +
 .../graders/names-the-epic.md                      |   8 +
 .../graders/no-bare-or-manual.md                   |   9 +
 .../graders/within-budget.md                       |   7 +
 .../w-skt-ticket-path-must-be-sibling/case.yaml    |  26 +
 .../w-skt-ticket-path-must-be-sibling/expect.json  |  19 +
 .../fixture/assignment.yaml                        |   8 +
 .../graders/not-inside-the-repo.md                 |   8 +
 .../graders/sibling-path.md                        |   7 +
 .../graders/within-budget.md                       |   7 +
 .../skt/w-skt-ticket-verb-help-is-scoped/case.yaml |  22 +
 .../w-skt-ticket-verb-help-is-scoped/expect.json   |   9 +
 .../graders/asked-the-verb.md                      |   9 +
 .../graders/names-path.md                          |   8 +
 .../graders/no-sweep-flags.md                      |  12 +
 .../w-sdc-attribution-before-close/case.yaml       |  26 +
 .../w-sdc-attribution-before-close/expect.json     |   7 +
 .../specs/desired_program_model/ticket_plan.yaml   |   6 +
 .../fixture/specs/tickets/T-7/current/Cart.tla     |   5 +
 .../fixture/specs/tickets/T-7/desired/Cart.tla     |   5 +
 .../fixture/specs/tickets/T-7/results/README.md    |   1 +
 .../graders/attribution-reported-before-close.md   |  14 +
 .../graders/closed-ticket.md                       |   8 +
 .../graders/consulted-attribution.md               |   8 +
 .../graders/wrote-attribution.md                   |  11 +
 .../w-sdc-close-ticket-delivered-status/case.yaml  |  26 +
 .../expect.json                                    |   8 +
 .../specs/desired_program_model/ticket_plan.yaml   |   6 +
 .../graders/close-ticket.md                        |   8 +
 .../graders/no-status-rewrite.md                   |  10 +
 .../case.yaml                                      |  24 +
 .../expect.json                                    |  16 +
 .../specs/desired_program_model/ticket_plan.yaml   |   9 +
 .../graders/close-tickets-script.md                |   9 +
 .../graders/no-close-workflow-verb.md              |   9 +
 .../w-sdc-complexity-ledger-is-advisory/case.yaml  |  27 +
 .../expect.json                                    |   9 +
 .../graders/no-ledger-fabrication.md               |   9 +
 .../graders/no-reclose.md                          |  10 +
 .../graders/read-the-log.md                        |   8 +
 .../graders/says-it-closed.md                      |  15 +
 .../w-sdc-eval-run-has-case-glob/case.yaml         |  25 +
 .../w-sdc-eval-run-has-case-glob/expect.json       |   9 +
 .../graders/did-not-run-the-eval.md                |   9 +
 .../graders/grants-the-tools.md                    |   9 +
 .../graders/names-the-case.md                      |  12 +
 .../case.yaml                                      |  30 +
 .../expect.json                                    |  16 +
 .../specs/desired_program_model/ticket_plan.yaml   |   6 +
 .../fixture/specs/tickets/T-3/current/Cart.tla     |   5 +
 .../fixture/specs/tickets/T-3/desired/Cart.tla     |   6 +
 .../graders/authorised-close.md                    |   9 +
 .../graders/names-guard-weakening.md               |   9 +
 .../graders/no-hand-sync.md                        |   9 +
 .../w-sdc-no-deferred-findings-at-root/case.yaml   |  27 +
 .../w-sdc-no-deferred-findings-at-root/expect.json |   8 +
 .../specs/results/deferred_findings_epic-cart.yaml |   5 +
 .../fixture/specs/tickets/T-6/results/README.md    |   1 +
 .../graders/no-root-ledger.md                      |  14 +
 .../graders/ticket-attribution.md                  |   9 +
 .../case.yaml                                      |  28 +
 .../expect.json                                    |  16 +
 .../specs/desired_program_model/ticket_plan.yaml   |   9 +
 .../graders/adds-plan-entry.md                     |  10 +
 .../graders/no-forced-reopen.md                    |  11 +
 .../w-sdc-out-path-is-absolute/case.yaml           |  28 +
 .../w-sdc-out-path-is-absolute/expect.json         |  14 +
 .../fixture/specs/program_model/Cart.tla           |   8 +
 .../fixture/specs/program_model/MC.cfg             |   1 +
 .../graders/absolute-out.md                        |  10 +
 .../graders/generate-cases.md                      |   8 +
 .../case.yaml                                      |  28 +
 .../expect.json                                    |   9 +
 .../fixture/specs/tickets/T-4/desired/adapters.py  |  18 +
 .../specs/tickets/T-4/desired/case_adapters.toml   |   7 +
 .../graders/bare-module.md                         |  11 +
 .../graders/binds-refund.md                        |   9 +
 .../graders/no-qualified-module.md                 |   9 +
 evals/unnested/w-misc-debug-bounded-wait/case.yaml |  23 +
 .../graders/bound-and-both-outcomes.md             |  14 +
 .../graders/fixes-the-bound.md                     |  10 +
 .../w-misc-otlp-endpoint-native-runner/case.yaml   |  22 +
 .../graders/gives-localhost.md                     |  10 +
 .../graders/no-cluster-dns.md                      |  13 +
 specs/results/deferred/SI-15.yaml                  | 200 ++++++
 .../tickets/SI-15/baseline-repository-suite.txt    | 725 +++++++++++++++++++++
 .../tickets/SI-15/entry-counts.txt                 |  28 +
 .../tickets/SI-15/final-repository-suite.txt       | 725 +++++++++++++++++++++
 .../tickets/SI-15/graph-cliWorkflow.txt            |  31 +
 .../tickets/SI-15/graph-specWorkflow.txt           |  45 ++
 .../tickets/SI-15/local-signal.txt                 |  22 +
 .../tickets/SI-15/names-after.txt                  |  61 ++
 .../tickets/SI-15/names-before.txt                 |  55 ++
 .../tickets/SI-15/placement.txt                    |  54 ++
 .../tickets/SI-15/spec-unit-tests-SI-15.txt        |  42 ++
 .../tickets/SI-15/worktree-front-door.txt          |  40 ++
 358 files changed, 7642 insertions(+), 2 deletions(-)


ITEM 3 — THE BACKLOG ROWS THIS SUBJECT FILED
----------------------------------------------------------------------
[
 {
  "id": "SI-15-DF-01",
  "found_by": "SI-15",
  "found_at_commit": "06df2b70",
  "schedule_revision": 4,
  "severity": "minor",
  "surface": {
   "production": [],
   "tla": [],
   "adapters": [],
   "test_graph": []
  },
  "summary": "The ticket, the issue body and the epic schedule all say skill-manager's harness holds \"63 cases\" and instruct the implementer to \"count 63 sources, not build output\". 63 IS the build-output number. Measured: `find specs/evals/harness/evals -name case.yaml` returns 63; the same find excluding `*/build/*` returns 55, and `-path '*/build/*'` returns exactly 8. So the source population is 55 and the instruction to exclude build output contradicts the count it is attached to. 54 moved (sandbox-probe stayed, SI-15-DF-02); the suite now holds 61, not 70.",
  "reproduction": "cd skill-manager && find specs/evals/harness/evals -name case.yaml | wc -l (63); add -not -path '*/build/*' (55); add -path '*/build/*' (8).",
  "evidence": [
   "specs/results/epic-self-improvement-substrate/tickets/SI-15/names-before.txt",
   "specs/results/epic-self-improvement-substrate/tickets/SI-15/names-after.txt"
  ],
  "why_out_of_scope": "The number is wrong in the issue body and the epic plan, which are the epic agent's to correct, not a ticket's. Recorded so the next reader of \"70 cases\" knows the real figure is 62 sources across both sides.",
  "suggested_fix": "Correct the epic plan and any successor issue to 55 skill-manager sources plus 7 here. A count taken with `find ... -name case.yaml` over that tree must exclude `build/`, which vendors copies of THIS repository's own example cases.",
  "blast_radius": "Planning arithmetic and any goal baseline quoting 70 cases."
 },
 {
  "id": "SI-15-DF-02",
  "found_by": "SI-15",
  "found_at_commit": "06df2b70",
  "schedule_revision": 4,
  "severity": "minor",
  "surface": {
   "production": [],
   "tla": [],
   "adapters": [],
   "test_graph": []
  },
  "summary": "`sandbox-probe` was NOT moved. It is a diagnostic of the other harness's sandbox rather than a skill test, and its `the-workspace-is-writable` grader is a DELIBERATE standing red declaring `path: probe-write` -- a path the agent writes. This repository's `test_no_grader_reads_a_path_the_agent_can_simply_write` requires every `file_exists` grader to read `.eval/`, so moving the case as written would turn a repository test red, and rewriting the grader would destroy the property the probe exists to measure (\"if this ever turns GREEN, plugin eval has changed\"). `tests/**` is outside this ticket's conflict keys (`production: [evals/**]`), so neither was mine to do.",
  "reproduction": "Read skill-manager specs/evals/harness/evals/sandbox-probe/graders/ the-workspace-is-writable.md against tests/test_agent_integration_harness.py ::test_no_grader_reads_a_path_the_agent_can_simply_write.",
  "evidence": [
   "evals/README.md"
  ],
  "why_out_of_scope": "Resolving it means either an exemption in a test outside my conflict keys or deleting a deliberate control. Both are decisions above a ticket.",
  "suggested_fix": "Either exempt a grader that declares itself an expected-red harness probe (an explicit `expected: red` key would make the intent machine-readable), or accept that harness self-probes live outside the skill suite.",
  "blast_radius": "One case; the suite is 61 rather than 62."
 },
 {
  "id": "SI-15-DF-03",
  "found_by": "SI-15",
  "found_at_commit": "06df2b70",
  "schedule_revision": 4,
  "severity": "minor",
  "surface": {
   "production": [],
   "tla": [],
   "adapters": [],
   "test_graph": []
  },
  "summary": "The 20,000-entry ceiling was briefed as \"the likeliest thing to bite you\", with the staged view \"already at 17,370 (SI-14-DF-03)\". That figure is not reproducible at this base. Measured on the staged view built by run.sh's own tar-exclude list at 06df2b70: 6,712 entries before the toolchain, 6,848 after materialising and staging it, and 7,288 after all 54 cases moved in. The ceiling was never within 12,000 entries of binding. The probable cause of the discrepancy is that `.toolchain/skt` stages at 183 entries while `.toolchain/skill-manager` (11,522) declares `stage_into_view = \"\"` and is deliberately NOT staged -- so a count taken over the cache rather than the view would read ~17-18k.",
  "reproduction": "Replicate run.sh's tar excludes into a temp dir and `find | wc -l`, then `python3 evals/lib/toolchain.py materialise --stage-into <view>` and count again. Both numbers are in entry-counts.txt.",
  "evidence": [
   "specs/results/epic-self-improvement-substrate/tickets/SI-15/entry-counts.txt"
  ],
  "why_out_of_scope": "It is a correction to an earlier ticket's recorded measurement, not a defect in this slice. run.sh's own header still claims 6,264, which is also stale; I left the header prose alone rather than widen scope.",
  "suggested_fix": "Re-measure and correct SI-14-DF-03, and replace run.sh's hardcoded 6,264 with the number the script already computes at run time.",
  "blast_radius": "Planning only -- but it cost this ticket a staging-less design it did not need, and a future ticket may cut cases to fit a ceiling that is not near."
 },
 {
  "id": "SI-15-DF-04",
  "found_by": "SI-15",
  "found_at_commit": "06df2b70",
  "schedule_revision": 4,
  "severity": "major",
  "surface": {
   "production": [],
   "tla": [],
   "adapters": [],
   "test_graph": []
  },
  "summary": "`skt ticket new` ROLLED THE WORKTREE BACK AND STILL EXITED 0 -- the eighth agent this epic to hit SI-11-DF-04. It printed \"error: bootstrap-home.sh not found in this home; worktree rolled back\" and `echo $?` was 0. The cause here is specific and fixable: `skt` resolved `bootstrap-home.sh` from the PROJECT home (`tla-spec-dev/.skill-manager`), which carries 10 skills and not `git-issue-workflow`, while the ROOT home does carry it at skills/git-issue-workflow/scripts/bootstrap-home.sh. So the front door failed on a file that exists one tier up.",
  "reproduction": "SKT=\"$HOME/.skill-manager/bin/cli/skt\"; \"$SKT\" ticket new SI-15 --base 06df2b70 --path ../wt-362-evals-one-place; echo \"EXIT=$?\"  -> prints the rollback error and EXIT=0; `test -e ../wt-362-evals-one-place` is false.",
  "evidence": [
   "specs/results/epic-self-improvement-substrate/tickets/SI-15/worktree-front-door.txt"
  ],
  "why_out_of_scope": "Fixing skt's exit status is an upstream change to the skt plugin, and installing git-issue-workflow into the project home mutates a home the epic agent owns and reconciles. I fell back to the by-hand pair (`git worktree add`) and say so plainly.",
  "suggested_fix": "Two independent repairs. (1) `skt ticket new` must exit non-zero when it rolls back -- eight agents have now tested the path instead of the exit code because of this. (2) Either declare git-issue-workflow in `skill-project.toml` so `project resolve` can rebuild the project home with it, or have skt fall back to the root home's copy of bootstrap-home.sh rather than failing.",
  "blast_radius": "Every ticket agent in this epic. An agent that trusts the exit code proceeds inside the primary checkout and writes the operator's home."
 },
 {
  "id": "SI-15-DF-05",
  "found_by": "SI-15",
  "found_at_commit": "06df2b70",
  "schedule_revision": 4,
  "severity": "major",
  "surface": {
   "production": [],
   "tla": [],
   "adapters": [],
   "test_graph": []
  },
  "summary": "Six moved cases cannot run in a plugin view and are declared UNDECIDED rather than silently red: bootstraps-a-home-for-a-repo, reconciles-a-worktree-into-the-project-home, syncs-a-stale-home-from-root, ticket-agent-opens-a-ticket, ticket-agent-closes-a-ticket, epic-provisions-a-ticket-worktree. Their fixture IS a real branched Skill Manager home (~41,000 entries, ~5 GB), which is above the 20,000-entry plugin ceiling by itself, and their graders depend on a replay verifier that re-issues the agent's front-door command against a throwaway clone. This is the honest half of the split: the staged view and the branched home exist for different reasons and one does not subsume the other.",
  "reproduction": "evals/run.sh --case 'ticket-agent-*' -- place.sh prints the UNDECIDED notice and verify.sh writes .eval/UNDECIDED-needs-home.",
  "evidence": [
   "evals/lib/place.sh",
   "evals/lib/verify.sh",
   "evals/README.md"
  ],
  "why_out_of_scope": "Carrying a Skill Manager home into an eval run needs a mechanism neither harness has: the view is capped at 20,000 entries and the sandbox's allowRead is the plugin dirs only. That is a design question for the epic, not a ticket-sized fix.",
  "suggested_fix": "Either give `claude plugin eval` a case-scoped scaffold that runs outside the entry count (`context.scaffold_script` under `--scaffold` DOES run -- re-measured in SI-14), or build the home into the workspace from a SessionStart hook, which runs unsandboxed and is not counted against the plugin directory. The second is the cheaper experiment.",
  "blast_radius": "Six of 61 cases. The home/worktree lifecycle -- the substrate's own front door -- is the part of the loop now measured least."
 }
]

ITEMS THAT DO NOT EXIST FOR THIS SUBJECT (absent, not withheld):
  close_summary
