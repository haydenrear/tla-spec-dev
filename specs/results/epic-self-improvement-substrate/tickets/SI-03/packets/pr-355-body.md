Refs #333

Epic `self-improvement-substrate`, branch `epic/self-improvement-substrate`,
workflow `self-improvement-substrate`, spec ticket **SI-10**, wave 3.

**Dependencies.** `depends_on: [SI-02]` — merged as `a42e0f7e` and reachable
from the epic tip. `promotion_predecessor: SI-06` — **not merged**, so per the
assignment this ticket does not close or promote its spec ticket; the epic agent
does that at wave merge. Base `994f650c` was the epic tip at branch time. **Reconciled at `0095a750`**: SI-04 (#353) and SI-05 (#354) merged ahead in the promotion lane, so `origin/epic/self-improvement-substrate` (`56c7658f`) was **merged in, not rebased** -- the branch is published under this PR.

The merge had exactly one conflicted path, and the cause is structural rather than semantic: four wave-3 branches each appended to the end of the same 45-row cumulative `specs/results/deferred_findings_final.yaml`. Resolved by **keeping every row from both sides** -- the shared 45, SI-04's four, and SI-10's one -- with nothing renumbered, nothing re-templated and no pre-existing row touched. Verified: **50 rows**, zero conflict markers, **zero deleted lines against either parent**, ids unique, YAML parses.

Re-run only what the reconcile could disturb: `tests/test_agent_integration_harness.py` was **auto-merged** (their additions plus this ticket's repointed pins), so its suite was re-run -- **53 pass**. The eval cases were deliberately NOT re-run: they cost money and a YAML append cannot affect them.

**Model ownership.** The epic agent owns the TLA+ work. `open ticket`,
`close ticket` and `--accept-new` were **not** run. `specs/tickets/SI-10/desired`
was left as scaffolded: this ticket's semantic delta is `evals/**` and carries no
model actions (`desired_actions: []`).

## What landed

The eval suite moves out of the symlink shim into the plugin's own `evals/`:
**seven cases, one per nested skill**, run by `evals/run.sh` against this
checkout — no shim, no `units-override.txt`.

**The 20,000-entry limit is resolved, not worked around.** Measured at HEAD on
2.1.275: the checkout is 98,814 entries and `claude plugin eval` refuses it with
*"a plugin directory holds more than 20000 entries to check for eval
directories"*, at $0.00, per case, with or without an explicit `plugins:` entry.
There is no ignore file, flag or manifest key that excludes anything from that
count — the traversal skips `.git`, `.svn`, `.hg` and nothing else. So `run.sh`
**stages a plugin directory that excludes the append-only record**
(`specs/.history`, 19,154 entries; the gitignored `.skill-manager` home, 41,169):
6,297 entries, rebuilt from the working tree on every run so it cannot drift.

The shim it replaces had already gone stale — it named `skills/spec-double-2` by
hand, and after SI-02 there are six nested skills.

**Hooks are staged, never committed at the root.** The plugin *is* the
repository, so a root `hooks/hooks.json` would run a `SessionStart` script in
every session of every user who installs `tla-spec-dev`, and a fixture hook's
blocking `exit 2` could refuse ordinary work. `run.sh` copies it into the view.

## Validation

| entry | command | result |
|---|---|---|
| repository unit | `pytest tests -q --ignore=tests/test_score_tools.py` | 10 failed, 1594 passed — **identical by NAME** to the baseline |
| spec-unit, project | `run spec-unit-tests --target specs/current` | 7 failed, 49 passed — **identical by NAME** |
| spec-unit, ticket | `run spec-unit-tests --target specs/tickets/SI-10/desired` | 7 failed, 46 passed — **identical by NAME** |
| suite's own pins | `pytest tests/test_agent_integration_harness.py tests/test_card_has_one_home.py` | **53 passed** (52 repointed + 1 new) |
| TLC | — | `N/A`: the epic agent owns the model for this epic |

`--target` was used instead of `--ticket SI-10` because `SIS-KICKOFF-F-04`
records that `--ticket` resolves two targets and runs only the first. Both were
run. Evidence root:
`specs/results/epic-self-improvement-substrate/tickets/SI-10/`.

## Goal contribution

| goal | kind | expected effect | measured | classification | decided by |
|---|---|---|---|---|---|
| `GOAL-evals-one-command` | direct | 2 cases behind a shim → at least one per nested skill, one command | **7 cases, one per nested skill, `evals/run.sh`, no shim, no override**; four cases scored end to end; entry-limit refusal re-measured at HEAD | **moved as expected** | SI-08 |
| `GOAL-no-new-gates` | guard | an eval reports, it does not block a close | zero new refusal paths; `run.sh` warns on one line and continues; `place.sh`'s `exit 2` can only fire inside an eval because the hooks never ship | **flat, as a guard should be** | SI-08 |

Case scores, one run each — `eval-four-cases.txt`:

| case | score | cost | what the score is about |
|---|---|---|---|
| `a-work-order-not-a-wish` | 1.00 | $0.46 | verdict + judge PASS PASS PASS |
| `use-the-front-door` | 0.67 | $0.26 | **verdict passed**; weight-1 response regex missed |
| `start-from-the-spec-not-the-source` | 0.67 | $1.34 | **verdict passed**; weight-1 regex grader threw |
| `epic-mode-is-not-main` | 0.33 → 0.33 → **1.00** | $0.71, $0.82, $0.75 | the two 0.33s were the verifier's defect; re-measured after the repair |
| three Bash-granted cases | not run | — | `SI-10-DF-01` |

**Every number is one run**, and three of seven cases were never measured. SI-08
decides the goal.

A re-run after repairing the instrument is not re-running until the number
improves: all three `epic-mode` numbers are reported, the repair is proved by a
three-arm control rather than by the score, and the deciding clauses were not
weakened — only the reading of a negated line changed.

## Deferred findings

`SI-10-DF-01` — **major** — the Bash-granted cases need a scratch HOME that
copies a Docker config and symlinks the login keychain; an agent permission
classifier blocks that as credential handling, so those three cases are
operator-run (or agent-run with `EVAL_HOME` prepared beforehand). Four of the
seven cases were made shell-free in response. Filed on the tip re-fetched
immediately before appending.

## Skill changes proposed

**`spec-double-2` — `references/plugin_evals.md`, applied here** (+57/-6). This
repository is its organizational home and the page's advice was wrong after
SI-02:

- *"that is what the thin symlinked plugin is for"* replaced by **When the
  repository IS the plugin, and it is too big** — the three distinct 20,000-entry
  refusals, the measurement that there is no exclusion mechanism, and the two
  shapes with what each costs;
- new: **A plugin that is a repository must not commit `hooks/hooks.json`**;
- the worked example and the §3.5 cross-reference repointed from the deleted
  shim to `evals/` (two → seven cases).

No other unit was blocked on. `git-issue-workflow`'s front door behaved as
documented except as noted below.

## Review input

**Hot spots**
- `evals/run.sh` — the one command; it stages the view, the hooks and the
  `--allow-tools` grant. If it is wrong, every case is wrong together.
- `evals/lib/verify.sh` — the collect-outside-then-publish ordering is what makes
  a forged verdict impossible; the repository pins execute the original attack.
- `tests/test_agent_integration_harness.py` — **outside my declared conflict
  keys**. The shim's pins lived there and deleting the shim would have deleted
  six guards, so they were repointed rather than dropped. No sibling ticket
  claims this file (SI-04 claims two other test files).
- `.gitignore` — `bin/` would have swallowed `evals/bin/` exactly as it once
  swallowed the shim's.

**Decisions and overrides**
- **A staged copy instead of a committed symlink shim.** Reversing it is a
  ticket, not a patch. Rationale and the measurements are in `evals/README.md`.
- **Four of seven cases grant no Bash**, so they need no scratch HOME. This
  makes them agent-runnable and bounds what they can check to documents; every
  grader body says so in its own words.
- **`epic_plan.py`'s `Refs #` clause was made advisory** after a wrong diagnosis
  (below). The three deciding clauses were not weakened.
- **The old shim was deleted, not reduced.** It carried one of six skills.
- No guardrail was weakened, no test skipped, no matrix entry downgraded, and
  `SKILL_GATES` was never set.

**Where I'd look for bugs in my own change**
1. *The document-grading checkers are prose matchers.* Defect 3 below is one
   instance; there will be more. Cheapest experiment: run each case twice more
   and read every kept sandbox, not the scores.
2. *`run.sh`'s exclude list is hand-maintained.* A new large gitignored
   directory silently pushes the view back over 20,000. It warns, but nothing
   fails. Cheapest experiment: add a 20k-file directory and run it.
3. *The harvest copies results out of the view.* If two runs overlap on one view
   path they clobber each other; `SI10_VIEW` exists for that and nothing
   enforces it.
4. *`grant.py` parses `allowed_tools:` with a regex*, so a multi-line list would
   silently grant nothing.

**Machinery friction**
- **`skt ticket new` failed** and I fell back to the documented by-hand pair.
  Quoting it: `error: this home holds 15 skill(s) and an agent launched here can
  reach 12` — missing projections for `git-issue-workflow`,
  `spec-double-compiler` and `test-graph`. The worktree was rolled back. I
  re-created it with `git worktree add` chained to `bootstrap-home.sh
  --allow-unprojected`, per `epic-ticket.md` §2. This is the front-door defect
  the skill asks to have reported, and it is **case 3**: found it, ran it, it
  failed.
- **`.git/info/exclude` hid my entire deliverable.** `bootstrap-home.sh` wrote
  `/evals/` into the clone's SHARED exclude file, so `git add -A` silently
  skipped all 40 files while `git status` looked clean. The epic agent repaired
  it; SI-06 filed it as `SI-06-DF-03`; SI-11 owns the fix. **Nothing was lost
  here — I had not committed yet.** It is worth saying inside this ticket
  because it is precisely the silent-vacuity class the suite exists to catch: a
  harness writing into an excluded directory produces a green run and no
  artifacts.
- **The eval report JSON carries no response text**, so a failing response
  grader cannot be diagnosed without `--keep-temp` and chmod-ing the sealed
  tree. That cost one wrong diagnosis and one extra billed run.
- **The scratch-HOME recipe cannot be executed by an agent** — `SI-10-DF-01`.

**Home close-out.** `skill-manager home close-out --home <worktree>/.skill-manager
--into <main-working-tree>/.skill-manager --json` → **`safe: true`, `exitCode: 0`,
`blockers: []`, all 26 units `unchanged` (byte-identical to the source)**. No
skill edit was made inside the home — the one skill change in this ticket is a
tracked file in the worktree and is in this PR. Nothing was published with
`unit publish`; `home sync` was not run. The worktree is left standing.


