# MF-014 complexity ledger

Standing objective, `references/architecture_tractability.md`: lower measured
complexity while retaining behavior, and record the delta **jointly** with
behavior-retention evidence. A reduction bought by under-representing the
program is gaming the metric.

## Measured delta

| Measure | Baseline (MF-017 tip) | MF-014 | Delta |
|---|---|---|---|
| State variables | 8 | 9 | **+1** (`corpus_gate`) |
| Actions | 11 | 12 | **+1** (`AnalyzeCorpus`) |
| Declared state-space bound | 221,184 | 663,552 | x3 |
| TLC distinct states | 2,923 | 9,011 | x3.08 |
| Search depth | 23 | 24 | +1 |
| Invariants checked | 11 | 12 | +1 (`SpecUnitTestsRequireMeasuredCorpus`) |

Both bounded figures stay inside their budgets: 663,552 < `max_state_space_bound`
1,000,000, and 9,011 < `max_distinct_states` 50,000.

## This ticket ADDS complexity, deliberately

There is no reduction to claim here, and the honest record is that the model
grew. The growth is the ticket: a hard gate that is not represented is not a
gate. `corpus_gate` carries a verdict the program genuinely computes and acts
on, and `AnalyzeCorpus` is a real user-facing command (`tla-spec-dev analyze
corpus`). Leaving either unmodeled to hold the variable and action counts down
would be exactly the under-representation this ticket's own doctrine forbids —
the corpus analogue of dropping cases to fit a budget.

`corpus_gate` earns its place under the "grow the model by evidence" rule: it
is read by `TypeInvariant` and `SpecUnitTestsRequireMeasuredCorpus`, and it
carries the `analyze corpus` verdict effect. `analyze complexity` confirms the
justification linkage is complete — no dead weight.

## Deviation from the planned model change (plan fields are stale)

The `MF-014` plan entry prescribes `desired_actions: [DistillCorpus]` and
`model_state: [corpus_distilled]`. Both are **withdrawn and not implemented**.
The ticket's scope was replaced on 2026-07-18 by owner direction; distillation
no longer exists, so there is nothing named `DistillCorpus` to model and no
`corpus_distilled` fact to record. Those fields predate the replacement and are
not binding (the staleness class is tracked as #33). What shipped is a hard
gate, not a selection step, and `corpus_gate`/`AnalyzeCorpus` model that.

This follows the precedent MF-017 set: record the deviation with reasoning in
the ticket outcome rather than inventing a model change to satisfy a stale
field.

## Behavior retention (recorded jointly, per the standing objective)

- TLC: 12/12 invariants hold, no deadlock, 9,011 distinct states at depth 24
  (`tlc-current.txt`). Every baseline invariant is retained by name and still
  passes; none were deleted or weakened.
- Repository unit tests: 196 passed, up from 171 on the epic tip — **+25 new,
  0 regressions** (`repository-unit-tests.txt`).
- Spec-unit adapters: 21 + 24 passed across both targets
  (`spec-unit-tests.txt`), including 6 new `AnalyzeCorpus` conformance tests.
- Test Graph `specWorkflow` (8/8) and `cliWorkflow` (2/2) green
  (`graph-specWorkflow/`, `graph-cliWorkflow/`).
- Case counts: unchanged, and that is the point. The committed example corpus
  holds 4 internal + 4 external cases before and after this ticket. No code
  path added by MF-014 removes a case; `test_no_api_removes_cases_to_satisfy_a_cap`
  and `test_generation_writes_every_case_even_when_the_gate_fails` assert this
  structurally.
- Kill rate: not measurable until MF-016 lands (mutation kill test). Deferred.

## Reductions searched for, and what was found

**Searched. One genuine candidate found; recorded as a recommendation, not
applied.**

### Candidate: collapse `complexity_gate` + `corpus_gate` into one gate function

`gate_status = [g \in {"complexity", "corpus"} |-> {"unknown","pass","fail"}]`
would hold the variable count at 8 instead of 9 while representing the same
information. `analyze complexity` already clusters both gates into C1, so they
are structurally adjacent.

**Not applied, and I recommend against it as stated.** The two gates differ in
a load-bearing way: `RunSpecUnitTests` consults `override` for
`complexity_gate` and deliberately does *not* for `corpus_gate`, because the
complexity gate has an explicit `--allow-over-budget` escape and the case caps
have none. Collapsing them into one symbol invites a future edit that gives
both the same override semantics, which would silently create the bypass this
ticket exists to prevent. The saving is one variable and zero state-space
reduction (3 x 3 either way). Per the user-approval rule this is recorded for
the owner rather than taken unilaterally.

### Rejected: the two moves `analyze complexity` itself suggests

`analyze complexity` recommends projecting `lastCommand`/`result`. That is the
standing deferred item named in the assignment and is **not** implemented here.

### Not attempted

The `ticket_state` collapse — known and deferred by owner direction.

## The C1 action-count finding got one worse

`analyze complexity` exits 1 with:

    component C1 is touched by 12 actions, exceeding max_component_actions 8

This was 11 actions on the epic tip; `AnalyzeCorpus` makes it 12. It is a
**true finding about the undecomposed single-module baseline**, not a
miscalibration. It was not worked around with `--allow-over-budget` and the
component budgets were not renegotiated. MF-023 (#30) resolves it at the root
via the Internal/External decomposition.
