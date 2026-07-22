# EP-03 validation summary

## Decision

Ship Python V0 as an opt-in experimental harness, with conditions. The three
preregistered projects validate the architecture's central split: a generated
TLA+ case selects a semantic outcome, while a project-owned provider selects
deterministic concrete representatives and validates effect-local protocol.
They do not validate exhaustive fuzzing, universal interception, or automatic
generation of service behavior.

The fixed catalogs killed 36/36 mutants versus 30/36 for three separate
hand-written baselines. The six added kills came from explicit filesystem and
four-provider state/order boundaries; legacy HTTP added no mutation-score gain
over its ordinary baseline. Attribution was 15 TLA-derived case-oracle kills,
20 provider/shared-journal kills, and one passive bypass-detector kill.

## Acceptance evidence

- Three independent project shapes required zero framework changes:
  explicit injected atomic filesystem, self-installed legacy HTTP patch, and
  four ordered correlated providers for a reminder outbox.
- Preregistration was committed at `141e63b` before implementation; its digest
  remains `970ade21dcf9e460a60cdb1e70396b5b5507c460983e7001cb1bceff5fe9390b`.
- Each project has two accepted deterministic repetitions, green controls,
  fixed mutants, content/value assertions, replay evidence, cleanup/isolation,
  Internal and External TLC evidence, generated-corpus provenance, and a
  separate ordinary baseline.
- Fresh-checkout project validation is in `fresh-checkout-validation.md`.
  Each validated project subtree is byte-identical through code/docs candidate
  `c46aef126600312daf20210448c7b844ef3e5996`.
- The final aggregate graph passed 22/22 assertions, 36/36 mutants, 2,079
  control points per accepted repetition, and 70 external cases in 36,707 ms
  (`effect-provider-graph-final.md`).
- Host repository suite: 615/615 passed (`repository-unit-tests.md`).
- Host spec units: 63 current + 60 ticket-current passed
  (`spec-unit-tests.md`).
- Host TLC retained 5,619,356 generated / 231,621 distinct / depth 25 with no
  error (`tlc-current.md`); current and desired are byte-identical
  (`zero-model-delta.md`).
- Host Test Graph `specWorkflow` 8/8 and `cliWorkflow` 2/2 passed after the new
  node's discovery-portability defect was found and fixed (`host-graphs.md`).
- Branch-local skill publish/install dry-runs passed; no global sync occurred
  (`skill-validation.md`).
- Complexity analysis records bound 699,840 and modularity 0.011742 with the
  inherited component-actions advisory; EP-03 adds zero host-model complexity
  (`analyze-complexity.json`, `complexity_ledger.yaml`).

## Cost-benefit findings

- Atomic publishing is the best low-cost signal: 12/12 versus 10/12 baseline,
  and a real-filesystem rung found a staging cleanup bug during review.
- HTTP is compatibility-only: 12/12 versus 12/12 baseline, `urllib`/raw socket
  bypasses, and a replay environment defect. Its patch and loopback guard are
  useful, but explicit injection is preferable for new code.
- The reminder workflow has the highest semantic gain and modeling cost: 12/12
  versus 8/12 baseline, but its provider duplicates ordering, cardinality,
  response-class, command, and projection rules missing from terminal cases.
- Every mutant died at iteration zero. The experiments prove fixed-catalog
  oracle coverage, not that later arbitrary representatives discover more
  bugs. A collect/continue campaign with data-dependent mutants is needed to
  measure that claim.

## Prioritized recommendation

1. Fix dependency-invariant manifest parsing/generation (`DEF-002`).
2. Generate a normalized semantic effect plan and small correlated
   bundle/journal/snapshot utilities; keep concrete service values and domain
   assertions project-owned.
3. Enforce provider signature/annotation conformance (`DEF-003`).
4. Preserve the originating virtualenv interpreter in replay (`DEF-001`).
5. Add collect/continue measurement and data-dependent mutants.
6. Standardize compatibility/bypass declarations and stronger real-service or
   process/network validation rungs.
7. Defer a universal response-plan DSL until common semantic fields are proven
   across more domains.
8. Add Java through JVM-native typed providers and an external entrypoint only
   after priorities 1-4 stabilize; do not make Python a universal Java effect
   service.

Full counts, frozen authoring/retrieval footprints, limitations, raw evidence,
and per-project recommendations are in
`examples/effect_providers/RESULTS.md` and `RESULTS.json`.

Coverage audit remains `not_run` at ticket close by workflow design. The epic
owner runs the amended, declared-scope audit after this ticket merges and before
workflow close.
