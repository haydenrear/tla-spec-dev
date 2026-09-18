# GOAL-blockers-propose — local signal: NOT RUN, and exactly why

Declared signal (assignment `goals[0].local_signal`):

> rerun one wide-lane refusal case against this checkout with `--keep` and read
> the response for the section

Classification reported in the PR: **no measurable movement — the signal was not
run.** This file is the record of what was checked instead of running it, so a
reader can tell "declined, with a reason" from "nobody ran it".

## What the lane actually is, verified

The wide lane is not in this repository. It is
`haydenrear/skill-manager` → `specs/evals/harness/`, checked out on this machine
at `/Users/hayde/IdeaProjects/skill-manager`. Verified by reading it:

- the refusal cases named in the issue exist —
  `harness/evals/w-giw-wt-refusal-quotes-subject/`,
  `w-giw-wt-close-no-force-on-unpublished/`, `w-giw-wt-new-dirty-ok/`,
  `w-giw-wt-stale-branch-point/`, and the `w-sdc-*` set;
- `harness/wide/run.sh` takes the `--keep` flag the signal names, and defaults to
  `EVAL_MAX_COST_USD=25`, `EVAL_CONCURRENCY=3`, via `eval_run_case`;
- the checkout-override mechanism the kickoff note calls for does exist:
  `harness/wide/setup.sh` reads `evals/w-*/units-override.txt` lines of the form
  `unit=checkout`, places that checkout over the unit, and even prints
  `, UNCOMMITTED changes` when the override is dirty. So pointing the lane at
  *this* worktree is mechanically possible.

## Why it was not run

Two reasons, both about scope rather than difficulty:

1. **It bills a real round.** `run.sh` launches `claude plugin eval` agent
   sessions with a $25 cap and concurrency 3. That is an operator spend, not an
   in-worktree command, and nothing in this ticket needs it: the signal is
   advisory and decides nothing (`git-issue-workflow/references/goal-signal.md`,
   "Precedence"). `GOAL-blockers-propose` is decided by **SI-08**, whose harness
   is the improvement card over these same cases — run once, on the integrated
   epic tip, which is the tree the measurement is supposed to be about.
2. **Running it would mutate a repository outside this ticket.** No
   `units-override.txt` exists in any case directory today, and
   `git check-ignore` in `haydenrear/skill-manager` reports the path is **not
   ignored** — creating one leaves an uncommitted file in a sibling repository
   that is not in this ticket's conflict keys and not in this PR. The deferment
   policy says defer, do not widen.

One run of one case would also not be evidence under the lane's own rules: its
README records four runs of one case going 14 → 10 → 9 → 8 Bash calls where
"every reduction was a defect in this harness, not in a skill", and
`spec-double-2/references/plugin_evals.md` §0 habit 6 says a number you cannot
reproduce is a claim.

## The command that would run it

For SI-08, or for an operator who wants it now:

```bash
cd /Users/hayde/IdeaProjects/skill-manager/specs/evals/harness
printf 'git-issue-workflow=%s\n' \
  /Users/hayde/IdeaProjects/wt-339-skills-propose/skills/git-issue-workflow \
  > evals/w-giw-wt-refusal-quotes-subject/units-override.txt
./wide/setup.sh                       # $0.00; prints the override + its dirty state
./wide/run.sh 'w-giw-wt-*' --keep     # billed; read the response, not the score
```

What to read for: whether the response carries a `## Skill changes proposed`
section, or names the unit and the change it would make. The round of
2026-09-15 produced none, because nothing asked.

Filed as `SI-06-DF-01` so the epic owner decides it rather than this ticket.
