# Kickoff baselines — epic/self-improvement-substrate

Measured 2026-09-17 on `b7a7d203` (the epic branch's base, before any ticket
lands), after both Skill Manager homes were synced to their remote tips. Every
number below is the `baseline` field of a goal in
`specs/desired_program_model/ticket_plan.yaml`; nothing here is a target.

## GOAL-one-unit — how many units the substrate is

```
ls .skill-manager/skills | wc -l      -> 18
ls .skill-manager/plugins | wc -l     ->  3
```

Seven of those are this epic's subject: `spec-double-compiler` (this repo, skill
surface at the repo root) plus the five workflow skills to nest
(`git-epic-workflow`, `git-issue-workflow`, `git-issue`, `discovery`,
`test-graph`), each its own repository and installed separately in the root home,
the project home, and every worktree home.

Not nested, by owner decision at kickoff: `debugging`, `git-integration-repo`,
`plugin-repository`.

## GOAL-findings-become-changes — findings that never became changes

```
grep -oE 'status: [a-z-]+' specs/results/skill_feedback.md | sort | uniq -c
   146 filed          11 items-recorded     52 none-found
    13 recorded-local 72 unreviewed          4 wontfix
grep -c '^### SF-' specs/results/skill_feedback.md              -> 37
grep -c '^  *- id:' specs/results/deferred_findings_final.yaml   -> 33
grep -c '^  *- id:' specs/results/epic-close/deferred_findings_next.yaml -> 6
```

13 `recorded-local` findings are the concrete backlog SI-05 consumes. The 39
deferred rows carry no field that says "this is a skill defect, here is the
change".

## GOAL-blockers-propose — unmeasured, deliberately

No such instrument exists; SI-03 builds it. Per
`goals-and-evaluation.md` § "Not every target is a number", the baseline is
recorded as "no such instrument exists" rather than a guessed figure, and the
goal is decided by whether the card runs and discriminates.

## GOAL-epic-owns-the-model — anchors placed, and by whom

```
grep -oE '(UNMODELED/[a-z-]+|[A-Z][A-Za-z]+\.[A-Z][A-Za-z]+)' \
  examples/validation/agent_rounds/SELF-IMPROVEMENT-MATRIX.md | sort | uniq -c
```

Largest unmodelled bins: `agent-harness` 8, `example-runners` 6, `yaml-parser` 4,
`record-keeping` 4, `skill-manager-home` 3, `instrument-registry` 3,
`skill-composition` 2. Modelled anchors are spread across
`TlaSpecDevCli.RunSpecUnitTests` / `.OpenTicket` / `.GenerateCases` /
`.CloseTicket` (4 each) and `.ScaffoldProject` (3).

The wave review artifact schema carries none of the four blocks this goal
requires; `references/human-review.md` §3.4 is prose.

## GOAL-progressive-disclosure — what loads, and when

Descriptions load into every session; card bodies load when the skill is used.

| unit | description words | card words | card lines |
|---|---|---|---|
| spec-double-compiler | 82 | 1,839 | 214 |
| git-epic-workflow | 247 | 4,114 | 447 |
| git-issue-workflow | 300 | 3,861 | 461 |
| git-issue | 148 | 2,969 | 315 |
| discovery | 91 | 933 | 142 |
| test-graph | 55 | 1,763 | 135 |
| **total (the six that become one plugin)** | **923** | **15,479** | |

Across all nine skills considered at planning time (including the three not
nested) the description total was 1,271 words.

## GOAL-evals-one-command — what running an eval costs today

Two cases (`scaffold-a-program-model`, `catch-the-drift`) under
`examples/agent_integration/eval-plugin`, which exists only because
`claude plugin eval` refuses a plugin directory over 20,000 entries and
`specs/` alone is 20,493. It carries the skill surface as symlinks. The
skill-manager wide lane needs a `units-override.txt` pointing at a checkout.

Both cases scored 1.00 on the predecessor branch; that is a prior run, not a
measurement of this epic.

## GOAL-no-new-gates — the state to preserve

The drop-gates work of 2026-09-14 is the baseline: `--force` / `SKILL_GATES=off`
exist everywhere, and the predecessor measured that a gate here is read by an
agent as a stop.

## One defect found while measuring

`command -v tla-spec-dev` in this checkout resolves to
`/Users/hayde/.skill-manager/bin/cli/tla-spec-dev` — the operator's root-home
shim, not this repository's code. The eval README documents this hazard for eval
runs; it is live in an ordinary working tree too. Filed as a deferred finding
rather than fixed here.
