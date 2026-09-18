# SI-07 — evidence

Ticket `SI-07` (#340), wave 4 of `epic/self-improvement-substrate`.
Branch `feature/340-epic-owns-model`, based on `21a71448`.

**The spec ticket was not opened or closed by this ticket.** The epic agent owns
the TLA+ work for this epic (`planning_rules.model_ownership_rule`), so
`open ticket`, `close ticket`, `close_tickets.py` and `--accept-new` were never
run. `specs/tickets/SI-07/desired` was scaffolded by the epic agent and needed
**no correction**, so this ticket owes nothing to the new *model corrections
owed by merged tickets* block.

## Baseline discipline

A baseline was recorded **before the first edit** and every comparison below is
by failure **NAME**, never by count — a count cannot tell a fixed failure from a
new one that replaced it.

## Results

| Suite | Before | After | New | Fixed |
|---|---|---|---|---|
| repository (`pytest tests --ignore=tests/test_score_tools.py`) | 10 failed / 1639 passed / 6 skipped | 10 failed / 1639 passed / 6 skipped | **0** | 0 |
| spec-unit `--target specs/current` | 7 failed / 49 passed | 7 failed / 49 passed | **0** | 0 |
| spec-unit `--target specs/tickets/SI-07/desired` | 7 failed / 46 passed | 7 failed / 46 passed | **0** | 0 |
| `scripts/tests/test_validate_epic_plan.py` | 74 tests | **86 tests, OK** | — | — |
| `scripts/tests/test_validate_assignment.py` | 70 tests | **81 tests, OK** | — | — |

The failure **sets are identical**, not merely equal in size: `comm` over the
sorted names returns 0 in both directions for all three suites. All 10
repository failures and both sets of 7 spec-unit failures are the epic's known
pre-existing sets.

## Which spec-unit command was run, and why

`--target specs/current` and `--target specs/tickets/SI-07/desired`, run
separately.

The assignment names `run spec-unit-tests --ticket SI-07`. That is
`SIS-KICKOFF-F-04` — it resolves both targets, **executes only the first**, and
prints both. Running the weak form would have reported a target it never ran, in
the PR of the ticket whose job is to stop the matrix recommending it.

## Not run, and why

- **TLC** — `N/A` by the assignment: the epic agent owns the model and runs TLC
  on the desired state it scaffolds. This ticket changed no `.tla` or `.cfg`.
- **Test graphs** (`cliWorkflow`, `specWorkflow`, `effectProviderExamples`) — not
  run. This ticket's entire diff is `skills/git-epic-workflow/**` plus evidence
  and backlog rows: no production code, no adapter, no graph node, no binding.
  Declaring that is more honest than three greens that measure nothing.

## Attribution

`UNMODELED/skill-composition`, disposition `DEFERRED`
(`spec-double-2/references/bug_attribution.md` §7c). Every defect this ticket
addresses lives in the composition of skill instructions and their validators.
No test-graph binding can drive that today — a named missing capability, not a
mood. Nothing gates on this.

## Files

| File | What it is |
|---|---|
| `repo-suite-BEFORE.txt` / `repo-suite-AFTER.txt` | full repository suite logs |
| `failures-repository-BEFORE.txt` / `-AFTER.txt` | sorted failure NAMES, the compared artifact |
| `specunit-current-BEFORE.txt` / `-AFTER.txt` | spec-unit against `specs/current` |
| `specunit-SI-07-desired-BEFORE.txt` / `-AFTER.txt` | spec-unit against the ticket workspace |
| `failures-spec-unit-*` | sorted failure NAMES for each target |
| `validator-suites-AFTER.txt` | both validator suites, 86 + 81 tests |
| `local-signal-GOAL-no-new-gates.txt` | default, `--strict` and `SKILL_GATES=off` — all exit 0 |
| `local-signal-GOAL-epic-owns-the-model.txt` | waves 1–3 rendered through the new template |
| `home-close-out.txt` | the read-only gate verdict |

## Local signals

**`GOAL-no-new-gates`** (guard — expected flat, and is). The validator prints
four new diagnostics and exits **0** in all three modes: default, `--strict`
(which promotes advisory *errors*, but these are *warnings*), and
`SKILL_GATES=off`. Zero new `sys.exit` / `raise` / `return 1` paths in the diff;
the only grep hits are prose asserting the opposite. The guarantee is
structural, not remembered: the diagnostics are appended to the report's
`warnings` list and `validate_plan` only ever promotes `errors`, so no flag or
combination of flags can turn a missing block into a refusal.

**`GOAL-epic-owns-the-model`** (direct). Waves 1–3 scored through the new
template: **0/5, 0/5, 1/5**. Wave 3's single block is *model corrections owed by
merged tickets* — its §6, "The standing debt nothing tracks", which the epic
agent wrote once, unprompted, because that wave forced it. The schema is what
makes it happen every wave instead of once. Second metric: **0** files under
`specs/` outside `results/` in this PR.

**This is a baseline, not a result.** Wave 4 is the first wave the schema
governs and `SI-08` decides the goal on the integrated epic. A count from one
wave is not a fact about the schema.

## Known blind spot in what this ticket ships

The block check reports only on artifacts that **exist** — a wave that merged
and produced no `review.md` at all is invisible to it. Filed as `SI-07-DF-02`
against my own change rather than left for someone else to find.
