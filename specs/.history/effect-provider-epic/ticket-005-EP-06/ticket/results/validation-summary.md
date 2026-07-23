# EP-06 validation summary

- Repository tests: 616 passed.
- Spec units: current 63 passed; EP-06 ticket current 60 passed.
- Host TLC: no error; 5,619,356 generated, 231,621 distinct, depth 25,
  zero states left on the queue.
- Repository aggregate:
  `ep06-central-20260722-v2`, three projects passed in 59.92 seconds.
- Aggregate measurements: 140 generated cases, 2,191 green control
  points, 36 unique fixed mutants / 48 scored executions, 37 exact replays,
  3,140 clean lifecycle checks, and 70 real-boundary cases.
- `effectProviderExamples-20260722-234720-abf456cf`: 1/1 node and 8/8
  assertions passed; the graph performed another fresh three-project run.
- `specWorkflow-20260722-234842-c4973810`: 8/8 nodes and 64/64
  assertions passed.
- `cliWorkflow-20260722-234907-9fb449e5`: 2/2 nodes and 41/41
  assertions passed.
- Reusing the accepted aggregate run id failed immediately with the expected
  non-overwrite diagnostic.
- The common validator accepted every provider usage descriptor and proved
  that described ports exactly match each repository's generated effect ports.
- Frozen EP-03 preregistration, aggregate, and project evidence remained
  byte-identical across the repeatable runs.

The accepted aggregate is
`examples/effect_providers/evidence/validation-runs/ep06-central-20260722-v2/aggregate.json`.
The product recommendation is
`examples/effect_providers/POST_REPLACEMENT_RECOMMENDATIONS.md`.
