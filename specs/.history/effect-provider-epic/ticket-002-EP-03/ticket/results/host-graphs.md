# Host Test Graph validation

Candidate: `c46aef126600312daf20210448c7b844ef3e5996`.

- `specWorkflow-20260722-064415-8538b610`: 8/8 nodes passed. This includes
  ticket open/complete/spec-unit/close, history and promotion assertions, and
  the forced-failure cleanup finalizer.
- `cliWorkflow-20260722-064435-509c720f`: 2/2 nodes passed, including all 39
  CLI-help assertions.
- `effectProviderExamples-20260722-065116-d50c50d0`: 1/1 node and 22/22
  assertions passed; details are in `effect-provider-graph-final.md`.

The first post-integration `specWorkflow` run exposed a branch regression before
these green runs. Its copied cleanup-probe graph describes every Python source,
including nodes the probe does not select. `effect_provider_examples.py`
imported the repository-local manifest parser at module import time, so the
copy failed discovery before allocating its fixture. Commit `c46aef1` moved the
repository-only import into node execution. A direct isolated describe passed,
then the entire graph passed, proving the fix without weakening the cleanup
probe.

Raw local reports are under the ignored
`test_graph/build/validation-reports/<run-id>/` tree for this worktree.
