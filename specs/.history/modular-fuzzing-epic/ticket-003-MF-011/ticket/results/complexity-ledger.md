# MF-011 — complexity ledger (standing objective, `references/architecture_tractability.md`)

Recorded **jointly** with behavior-retention evidence, per the standing
objective. Retention first — a complexity number without it is meaningless.

## 1. Behavior retention

| Gate | Result | Evidence |
|---|---|---|
| TLC (ticket-local current, 120s cap) | 2923 distinct / 18720 generated / depth 23 / **0 errors**, all 11 invariants | `tlc-current.txt` |
| Spec-unit tests (MF-011) | passed, 2 targets (15 + 15 tests) | `spec-unit-tests.txt` |
| Repository unit tests | **151 passed** (123 baseline + 28 new) | `repository-unit-tests.txt` |
| Test Graph `specWorkflow` | 8/8 nodes passed, BUILD SUCCESSFUL | `testgraph-specWorkflow/` |
| Test Graph `cliWorkflow` | 2/2 nodes passed, BUILD SUCCESSFUL | `testgraph-cliWorkflow/` |
| `analyze complexity` on this repo's own model | exit 1 (over budget — correct) | `analyze-complexity-self.txt`, `.json` |

No baseline behavior was removed. The 123 pre-existing repository tests all
still pass.

## 2. Model complexity delta: **UP, deliberately, with justification**

| Metric | Baseline (MF-021) | MF-011 | Delta |
|---|---|---|---|
| State variables | 11 | 12 | **+1** |
| Declared state-space bound | 393,216 | 1,179,648 | **x3** |
| Distinct states | 919 | 2,923 | **+2,004** |
| Generated states | 3,664 | 18,720 | +15,056 |
| Search depth | 21 | 23 | +2 |
| Actions | 10 | 11 | +1 |

**Per the recursive refinement loop, complexity up requires a recorded
justification naming the new essential behavior. Here it is.**

The ticket's entire purpose is a new gate on case generation. That gate is a
real, externally visible program fact — the CLI genuinely refuses to generate
cases against an unanalyzed or over-budget model — so it must appear in the
model. Representing it costs exactly one three-valued variable
(`complexity_gate`) and one action (`AnalyzeComplexity`).

The x3 bound is precisely `3` (the gate's domain) and nothing else; no other
dimension moved. The distinct-state growth beyond that comes from the
`override` input on `RunSpecUnitTests` and from `AnalyzeComplexity` being
re-runnable.

**On the re-fire self-loops specifically:** `AnalyzeComplexity` can fire
again from a state where the gate already holds that value, producing a
self-loop. That is a legitimate idempotent re-fire — re-running the analysis
is a real thing a user does — and per the MF-020 correction it was **kept**.
Deleting it would have shaved generated states while leaving distinct states
and depth untouched, which is exactly the anti-pattern this ticket's own
diagnostics now flag as a RED FLAG. Removing it to make this ledger look
better would have been gaming the metric.

Cheaper representations were considered and rejected as unfaithful: a boolean
gate cannot distinguish "never analyzed" from "analyzed and failed", and the
"never analyzed" state is the one the refusal exists for.

## 3. Refinement search — findings

Searched. **Found two, applied neither** — both are recommendations requiring
owner approval.

**(a) The `setup_phase` ordinal collapse — INDEPENDENTLY REDISCOVERED.**

This is the useful validation signal. Without being told it exists, the new
command surfaced the already-measured open owner decision, from the model
alone:

```
latching booleans [cli_built, cli_installed, project_scaffolded,
budgets_recorded, workflow_scaffolded] are pinned into a total order by their
own action guards, so only 6 of 32 combinations are reachable
```

The detection is derived, not hardcoded: the tool identifies booleans
initialized `FALSE` and only ever assigned `TRUE`, then reads each writing
action's guard to build the implication order, then checks that order is
total. On the 11-variable shape it projects **393,216 → 73,728 at 11 → 7
variables** — matching the owner's recorded figure exactly.

**Not implemented**, per the ticket's explicit instruction; it remains an open
owner decision. Its rediscovery is evidence the metric works, not a licence to
apply it.

**(b) `lastCommand` and `result` are projection candidates — RECOMMENDATION.**

No configured invariant reads either variable, and neither is constrained by
`TypeInvariant`. Move 1 permits projecting variables no invariant reads.

**Not applied**, and it should not be applied on this evidence alone. Both
variables carry the CLI's user-visible result payload, which is why they have
`effects` linkage in the justification table rather than `invariants` linkage.
Per doctrine, an abstraction is legitimate **iff the kill rate holds after
it** — and the mutation kill test is MF-016, which has not landed. Projecting
them now would be exactly the unverified move MF-020 warns about. Recorded for
the owner and for MF-016 to settle empirically.

**Deferred, not touched:** the `setup_phase` collapse remains deferred by owner
decision, as instructed.

## 4. Complexity added by this ticket, stated honestly

- `scripts/analyze_complexity.py`: ~1,000 lines, new.
- `scripts/tla_spec_dev.py`: +~40 lines (subcommand wiring).
- `scripts/generate_cases_from_tlc_dump.py`: +~45 lines (gate).
- `tests/test_analyze_complexity.py`: 28 tests, new.
- Model: +1 variable, +1 action, +1 invariant.

This is a substantial addition, and it includes a hand-written TLA+ parser —
inherently approximate, covering the constrained profile in
`references/tla_profile.md` and no more. Where it cannot determine a domain it
reports `unknown` rather than guessing, so its failure mode is silence, not a
wrong number.

The justification is that this is the epic's measurement instrument. Every
other ticket's complexity claim is measured against it, and MF-019 (the
standing minimization objective) is built directly on top. An epic whose
premise is "complexity is measurable" needs the measurement to exist and to be
honest about its own limits — including, per §2, honestly reporting that this
very ticket increased complexity.

## 5. One caveat this ledger should carry

The command's own report on this repository's model **exits 1** — the model is
over budget (1,179,648 vs `max_distinct_states` 50,000, and component C1 is
touched by 11 actions vs a budget of 8). That is not a bug and it was not
worked around. It is the accurate finding, and per doctrine gate failures are
recorded as findings rather than silently accommodated. The suggested move for
it is §3(a), which is the owner's to approve.
