# MF-011 — design decisions

## 1. What the command measures, and what it deliberately refuses to measure

`analyze complexity` is a **static** analysis: it parses the `.tla` + `.cfg`
and never runs TLC. That is the whole point — the command exists so an agent
has a number *before* the model checker is invoked, rather than discovering
state explosion by timing out.

Consequences that shaped the implementation:

- **Domains come from `TypeInvariant`, cardinalities from the `.cfg`.** A
  variable the type invariant does not constrain is reported as `unknown` and
  **excluded from the bound**, with the exclusion printed. Inventing a
  plausible domain would produce a number that looks measured and is not.
  On this repository's own model that correctly flags `lastCommand` and
  `result`.
- **The bound is an upper bound on declared states, not reachable states.**
  It is labeled as such. Reachable-state counts only come from TLC.

Calibration: the command reproduces **393,216** for the 11-variable
post-MF-020 shape — exactly the figure the MF-020 close recorded — which is
asserted as a unit test (`test_repository_own_model_reproduces_the_recorded_state_space_bound`).

## 2. Model impact: `complexity_gate` and `AnalyzeComplexity`

One new variable and one new action:

- `complexity_gate \in {"unknown", "pass", "fail"}` — a **global** fact about
  the program, not a per-ticket map. The gate describes the model as a whole,
  so a per-ticket function would have been transcription rather than a fact.
- `AnalyzeComplexity(root)` sets it nondeterministically to `pass` or `fail`,
  because the verdict depends on the model being analyzed, which is outside
  this state machine.

`RunSpecUnitTests` gained an `override` input and this guard:

```tla
/\ \/ complexity_gate = "pass"
   \/ /\ complexity_gate = "fail"
      /\ override
```

**The refusal is modeled as the absence of an enabled transition.** When the
gate is `"unknown"` there is no `RunSpecUnitTests` step at all. That is the
faithful representation: an unanalyzed model is exactly the one that exhausts
TLC, and the CLI refuses rather than starting.

New invariant `SpecUnitTestsRequireAnalyzedGate` states the property that
matters: no ticket reaches phase 3 while the gate is `"unknown"`. Case
generation is never silently unanalyzed.

Rejected alternative: two separate actions (`RunSpecUnitTests` /
`RunSpecUnitTestsOverride`). One externally visible commitment happens either
way — spec-unit cases run — so per atomicity fidelity that is one action with
an input, not two actions.

## 3. Where the gate hooks into case generation

`enforce_complexity_gate` is called in `generate_cases_from_tlc_dump.main()`
**immediately before `run_tlc_dump`**, which is the expensive step. Refusing
after a TLC run would defeat the purpose.

- Gate fails, no override → dominant dimensions + suggested move to stderr,
  `SystemExit(2)`.
- Gate fails, `--allow-over-budget` → same diagnostic, then `PROCEEDING
  ANYWAY`, and generation runs.
- Gate cannot parse the model → warn and continue. A diagnostic that cannot
  read a spec must not become a hard blocker on generation.

## 4. Modularity

Newman-Girvan modularity `Q` over a variable-interaction graph where an edge
weight is the number of actions touching both variables, maximized by greedy
agglomerative merging (CNM-style). Pure stdlib — this repository has no graph
dependency and gains none. Merging is deterministic (ties break on sorted
keys) so the same model always produces the same recommendation; a
recommendation that moved between runs would be unusable as evidence.

## 5. Suggested-move ordering

`abstract → decompose → refactor`, following
`references/architecture_tractability.md`: change the representation before
cutting the model, and cut the model before asking for a production change.
Every path is labeled `RECOMMENDATION -- REQUIRES USER APPROVAL, NOT
AUTO-APPLIED`, and the output states plainly that a poor score is not a
verdict.

## 6. Absorbing the two MF-020 findings

**Finding 1 — the distinct-state count is blind to deleted self-loops.**
`--tlc-report` / `--baseline-tlc` compare two TLC runs. Generated states down
while distinct states and depth are unchanged ⇒ `RED FLAG`, with an explicit
instruction to inspect the transition-level diff. Verified against the exact
withdrawn MF-020 signature (3664 → 3185 at constant 919 / 21 = -13.1%):
`test_generated_drop_at_constant_distinct_states_is_a_red_flag`.

**Finding 2 — projected reductions are unverified.** Every figure carries a
`[MEASURED]` or `[PROJECTED]` tag, there is a legend at the top of the report,
and the JSON payload sets `projected.verified = false`. The suggested move
splits `evidence_measured` from `gain_projected`. No projection is ever
presented as a finding.

## 7. Justification table

Format introduced by this ticket (none previously existed), optional by
design since the criterion is "when a justification table is present":

```yaml
justification:
  <variable>:
    invariants: [...]
    effects: [...]
    kill_tests: [...]
```

A variable absent from the table, or present with all three lists empty, is
flagged as dead weight. When the block is missing entirely the analysis is
skipped with a note rather than flagging everything.

The ticket-local manifest now carries a complete table for all 12 variables,
so the model's own report flags nothing — the accurate result. Dead-weight
flagging is exercised on fixtures in `tests/test_analyze_complexity.py`.
