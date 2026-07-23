# MF-013 complexity delta, recorded jointly with behavior-retention evidence

Standing objective, `references/architecture_tractability.md`: minimize measured
complexity **while retaining every behavior**. A complexity drop achieved by
under-representing the program is gaming the metric. The two halves are
therefore recorded together, and the retention half comes first.

Baseline measured on the epic tip at branch time (`1dcce07`), not quoted from
the issue. Raw output: `tlc_baseline.txt`, `complexity_baseline.txt`.
Post-ticket: `tlc_current.txt`, `complexity_current.txt`.

## 1. Behavior retention

| Evidence | Baseline | After MF-013 |
|---|---|---|
| Repository unit tests | 226 passed | **279 passed** (+53, 0 regressions) |
| Ticket spec-unit tests | 24 passed | **28 passed** (+4) |
| TLC invariants | 12, all hold | **13, all hold** (+`SpecUnitTestsRequireMeasuredEffects`) |
| TLC result | No error found | **No error found** |
| Search depth | 24 | **24** (unchanged) |
| `specWorkflow` graph | green | **green (8/8)** |
| `cliWorkflow` graph | green | **green (2/2)** |

Every baseline invariant is retained **by name**; none was weakened or renamed.
No test was deleted, skipped, or relaxed. Depth is unchanged at 24, so no
behavior was truncated out of the reachable graph.

## 2. Complexity delta

| Measure | Baseline | After MF-013 | Delta |
|---|---|---|---|
| Variables | 7 | 8 | +1 (`effect_conformance`) |
| Actions | 12 | 13 | +1 (`RunEffectConformance`) |
| Declared state-space bound | 34,992 | **139,968** | **4.00x** |
| TLC distinct states | 9,011 | **38,241** | 4.24x |
| TLC generated states | 87,464 | **678,724** | 7.76x |
| Depth | 24 | 24 | unchanged |

The bound multiplier is exactly 4.00x — the cardinality of the new variable's
domain (`unknown`/`clean`/`gaps`/`dead_surface`). The issue anticipated ~3x for
a 3-valued gate; this gate is 4-valued for the reason given in §4.

### Hard gates: both PASS

- `max_state_space_bound` 1,000,000 — declared bound 139,968. **PASS** (14.0%).
- `max_distinct_states` 50,000 — measured 38,241. **PASS** (76.5%).

**Headroom warning for MF-023.** Distinct states now sit at 76.5% of the
`max_distinct_states` cap. One more 4-valued global gate on the undecomposed
module would breach it (38,241 x 4 = 152,964). This is a measurement inviting a
design decision, which is what the tools are for: the decomposition MF-023
performs is what creates room, not a raised cap.

### The two live findings: one RESOLVED STRUCTURALLY, one worsened by one

Baseline (`complexity_baseline.txt`) — a single undecomposed component:

```
graph modularity Q = 0.000
C1: complexity_gate, corpus_gate, lastCommand, result, setup_phase,
    spec_root, ticket_state  (7 variables, 12 actions)
VERDICT: FAIL
  - component C1 has 7 variables, exceeding max_component_variables 6
  - component C1 is touched by 12 actions, exceeding max_component_actions 8
```

After MF-013 (`complexity_current.txt`) — the module **decomposed**:

```
graph modularity Q = 0.009
C1: lastCommand, result, setup_phase, spec_root, ticket_state  (5 variables, 13 actions)
C2: complexity_gate, corpus_gate, effect_conformance           (3 variables,  4 actions)
candidate port-crossing actions:
  AnalyzeComplexity, AnalyzeCorpus, RunEffectConformance, RunSpecUnitTests
VERDICT: FAIL
  - component C1 is touched by 13 actions, exceeding max_component_actions 8
```

**`max_component_variables` is now satisfied (5 and 3, both under 6).** This was
NOT achieved by renegotiating a budget, passing `--allow-over-budget`, or
touching the measurement — the budgets are byte-identical and the thresholds
are unchanged. It happened structurally: `effect_conformance` is the third
member of a verdict-shaped cluster, and with three members the clustering
separates the gate/verdict concern (C2) from the CLI lifecycle concern (C1)
instead of lumping everything into one component. Adding a variable **lowered**
the component-size finding, which is rule 1 working as intended — complexity
pushed out by structure rather than accommodated.

**Do not overclaim this.** Q = 0.009 is barely above zero and four actions
cross the boundary, so the decomposition is real but weak — the tool is
detecting a seam, not certifying a clean split. It is evidence pointing at the
Internal/External decomposition, not a substitute for it.

**The action finding remains and this ticket worsened it by one**, honestly:
`RunEffectConformance` adds a 13th action to C1. Recorded rather than avoided.
It remains a true statement about the undecomposed single-module baseline and
is resolved at the root by MF-023 (#30). No budget was renegotiated and no
override was used.

## 3. Refinement search — searched, ONE candidate found, MEASURED, REJECTED

Not silence: a candidate exists, was measured rather than estimated, and is
recorded here as a recommendation the owner may take.

**Candidate: collapse `gaps` and `dead_surface` into a single `fail` verdict.**

Measured on a scratch variant with TLC (not projected):

| | Current (4-valued) | Collapsed (3-valued) | Reduction |
|---|---|---|---|
| Declared bound | 139,968 | 104,976 | 25.0% |
| Distinct states | 38,241 | 26,607 | 30.4% |
| Generated states | 678,724 | 375,096 | 44.7% |
| Depth | 24 | 24 | — |

**REJECTED, and not applied.** The reduction is real, but it is bought by
deleting a distinction the program actually makes. A gap and dead model surface
have different causes, different remedies, and different externally visible
`result.next` text (`"Declare the port, or change the program so it no longer
emits the effect"` vs `"Remove the dead port, or add a case that exercises
it"`). Collapsing them would make the number smaller by making the
representation less faithful — trimming the thing being measured, which rule 1
forbids. Recorded as an **owner-approval recommendation**: if the owner judges
the distinction better carried outside the model, the measured saving above is
what it is worth.

**Deferred, not searched:** projecting `lastCommand`/`result`, which
`analyze complexity` suggests as its ABSTRACT move. That belongs to MF-016 and
is legitimate only if the mutation kill rate holds afterwards; with kill-test
runs deferred to MF-023 the precondition cannot be evaluated here.

**A reduction WAS found and landed**, though not by searching for one: the
`max_component_variables` finding resolved structurally when the model
decomposed into C1/C2 (§2). It is recorded there rather than here because it
was a consequence of modeling the ticket's behavior faithfully, not a
refinement applied afterwards — which is the order rule 1 prescribes.

**The remaining reduction is structural and is MF-023's**: C1 still carries 13
actions against a budget of 8, and Q = 0.009 says the seam the tool found is
weak. Only the Internal/External decomposition addresses that, and nothing in
this ticket could achieve it without performing the work the epic assigns
elsewhere.

## 4. Why `effect_conformance` is 4-valued and not 3-valued

Recorded because it is the ticket's largest single complexity cost (4.00x on
the bound) and should be reviewable as a decision rather than an accident.

`gaps` and `dead_surface` are kept apart because they are not the same finding.
They differ in cause, in remedy, and in what the CLI prints as the next step.
Collapsing them costs 25% of the bound (measured, §3) and buys a model that can
no longer say which of two different failures occurred. Under rule 1 the
measurement is not what gets adjusted; §3 records the trade honestly and leaves
the call with the owner.
