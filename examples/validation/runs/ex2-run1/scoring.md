# ex2 run 1 — scored against PREDICTIONS.md (E2-*)

Run date 2026-07-21. A real order-cancellation ticket on a scratch copy of
`distributed_history`, staged via the example's documented Desired-file
convention, through to 1,520 external cases executed against the local
monolith and a 4/4 test-graph run. Owner spot-verified the descriptors, the
model delta, the manifest cap rationale, and findings 1 and the
suggested-move sighting in toolchain source.

| Prediction | Verdict | Evidence |
| --- | --- | --- |
| E2-P1 no complexity refusal; old C2 finding advisory only | **PASS** | Scanner exit 0 before and after; the component-actions warning surfaced as "FINDINGS … do NOT block promotion" and nothing complexity-related blocked. The workflow DID refuse once — the **corpus case-cap gate**, which is a hard gate by design and, decisively, already refuses the UNMODIFIED example (VAL-08): a pre-existing example defect, not a complexity gate and not caused by the ticket. |
| E2-P2 ticket completes, tests green | **PASS** | Model+adapters+production+tests landed; TLC green (Internal 224; External 109,236 distinct, 11s); 199 internal + 1,520 external cases executed; channel enforcement passed; test graph 4/4 with cancelled orders verifiably absent from projections. |
| E2-P3 bound=4 not misread | **PASS (exemplary)** | Agent: the bound is "a floor over a sliver of the state … says nothing about real size," cross-checked against measured 49,386→109,236 distinct states, and read the excluded-variables list correctly. |
| E2-P4 no complexity waivers/budget edits | **PASS with a nuance** | Complexity thresholds untouched. The agent raised `max_external_cases_per_action` 50→392 with a recorded rationale — but that is the corpus hard gate's own documented accept path, taken only after establishing the pristine baseline already fails it; and it explicitly did NOT apply the gate's suggested move. |

Bonus observation: modularity Q improved 0.170→0.187 and the clusters re-cut
along a cleaner order-lifecycle vs request/response seam — the descriptor
made a real refactor-relevant fact visible on a real model change.

## Findings filed from this run

- **VAL-08** (major): the pristine example fails its own documented
  regeneration path — manifest cap 50 vs the 732-case corpus it advertises
  (worst action 200). Pre-existing.
- **VAL-09**: `scripts/regenerate_tlc_cases.py` (example + toolchain copy)
  calls the exporter without the now-required `--bindings` (exit 2).
- **VAL-10**: `export_testgraph_cases.py` silently falls back to built-in cap
  50 when the corpus lives in a build dir and no `--manifest` is passed.
- **VAL-11**: example scripts hardcode the toolchain root as `parents[1]`;
  `examples/run_distributed_history_validation.py` cannot target a standalone
  checkout at all. Agent routed around with a `TLA_SPEC_DEV_ROOT` override.
- **VAL-12** (major, extends VAL-07): actions whose writes happen entirely
  through called operators (`RunFulfillmentWorker`, `HiddenInternalProgress`)
  have NO R/W matrix column while the helper `MarkExternal` is listed as an
  action — dense-row fractions are computed over a partially wrong action set.
- **VAL-13** (major, epic-relevant): **suggested-move output is still live**
  in the documented workflow — the corpus gate printed "Suggested move:
  Abstract the before-state… RECOMMENDATION REQUIRING USER APPROVAL"
  (`scripts/corpus_diagnostics.py:760`, plus `analyze corpus` help text).
  CD-01 removed suggestions from the scanner; the corpus path retains them
  and a real agent met one mid-ticket. The agent correctly did not apply it.
- **VAL-14** (minor): README doc drift — the external-cases envelope is
  documented as `expectedCaseCount`/`executedCaseCount` but publishes
  `caseNames`/`expectedCaseNames`.

## Toolchain verdict for this run

The path issue #62 called unusable now completes end to end, and the
descriptor was read correctly on the least-flattering real shape it has
(bound 4 with 9 exclusions). The friction that remains is all in the
experimental fuzzing surround (corpus gate calibration, exporter flags,
stale example wiring) — and it still speaks suggestion language (VAL-13).
