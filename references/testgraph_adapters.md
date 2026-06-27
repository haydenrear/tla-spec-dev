# Test Graph Adapters

This reference describes the External/Test Graph adapter path. Use
`examples/distributed_history/` as the concrete reference implementation.

## Views

The workflow uses one semantic authority with two executable views:

- Internal view: fine-grained program/component state. These cases run through
  spec-unit adapters.
- External view: public or harness-driven observable behavior over the internal
  semantics. These cases run through Test Graph adapters.

External does not necessarily mean distributed. For an HTTP service it may mean
requests. For a CLI it may mean commands and filesystem assertions. For a batch
processor it may mean input files, process runs, and output manifests. For a
distributed service it may include deployed API calls, queue operations, or
fault injection.

An accepted, closed `program_model` contains only promoted baseline files such
as `Core.tla`, `Internal.tla`, and `External.tla`. Active desired overlays use
`DesiredCore.tla`, `DesiredInternal.tla`, and `DesiredExternal.tla`, and should
be removed after promotion.

## Hook Order

`scripts/run_generated_case_adapters.py --batch` groups cases by adapter
`kind`. For each group it runs:

1. `setup_all(AdapterBatchContext)` once per unique adapter class.
2. For each selected case:
   - `setup(AdapterCaseContext)`
   - `run(case, work_dir=...)`
   - result/output validation
   - projected-state assertion, if configured
   - `teardown(AdapterCaseContext)`
3. `teardown_all(AdapterBatchContext)` once per unique adapter class in reverse
   adapter order.

Use `setup_all` and `teardown_all` for suite-wide external state such as
clearing shared tables, committing queue offsets, preparing a CLI workspace, or
checking cluster health. Use `setup` and `teardown` for per-case state such as
loading a TLA `before` state into debug/admin endpoints, writing CLI fixture
files, or clearing case fixtures.

In `examples/distributed_history/specs/program_model/adapters.py`:

- `_HttpAdapter.setup_all` waits for service health and resets deployed state.
- `_HttpAdapter.setup` resets state and loads `case.before`.
- `_HttpAdapter.teardown` resets state after the case.
- `_HttpAdapter.teardown_all` resets state after the batch.

## Projected-State Assertions

External assertions compare the expected program state from the generated case
to actual deployed state projected back into the TLA model shape.

The binding file wires this:

```yaml
actions:
  SubmitCheckout:
    adapter: specs.program_model.adapters:CheckoutHttpAdapter
    projector: specs.program_model.adapters:ClusterStateProjector
    expected_projection: specs.program_model.adapters:ExpectedClusterProjection
    assertion: specs.program_model.adapters:ProjectedStateAssertion
```

The runner computes:

- expected state: `expected_projection.expected_state(context)`, usually a
  projection of `case.after`;
- actual state: `projector.observe(context)`, usually from deployed admin/debug
  endpoints;
- comparison: `assertion.assert_state(context)`.

In the ecommerce example the projector calls `/debug/state`, normalizes the
visible abstract fields, and compares them with the generated case's expected
state. Each assertion writes a per-case evidence file:

```text
test_graph/build/validation-reports/<run>/external-case-work/case-work/<case>/program-state.json
```

The Test Graph evidence node aggregates these into:

```text
test_graph/build/validation-reports/<run>/projected-program-states.json
```

The graph fails if the set of projected-state files does not exactly match the
generated trace manifest or if any record has `matched: false`. The
`ecommerce.external_cases` envelope also publishes `caseNames` and records
`expectedCaseCount` / `executedCaseCount` metrics, so a fast run still leaves
explicit evidence that every generated case executed.

## Current Example Cases

The ecommerce example regenerates internal and external case packages from TLC:

```bash
uv run examples/distributed_history/scripts/regenerate_tlc_cases.py \
  --out examples/distributed_history/test_graph/build/generated/manual
```

This writes a Python case package that materializes TLC graph edges for adapter
execution. The package is generated IR, not hand-maintained test source. Test
Graph runs regenerate the external package inside each validation report. The
current bounded model emits four internal/spec-unit cases and 17 external/Test
Graph cases after projected-state dedupe. The external manifest is the source
of truth:

```text
examples/distributed_history/test_graph/build/validation-reports/<run>/generated/testgraph/traces/manifest.json
```

The current external trace ids are:

- `case_0001_submit_create_account`
- `case_0002_submit_add_cart_item_missing_account`
- `case_0003_submit_checkout_missing_account`
- `case_0004_run_fulfillment_worker_noop`
- `case_0005_submit_duplicate_create_account`
- `case_0006_submit_add_cart_item`
- `case_0007_submit_checkout_empty_cart`
- `case_0008_run_fulfillment_worker_noop`
- `case_0009_submit_duplicate_create_account`
- `case_0010_submit_checkout`
- `case_0011_run_fulfillment_worker_noop`
- `case_0012_submit_duplicate_create_account`
- `case_0013_submit_duplicate_checkout`
- `case_0014_run_fulfillment_worker`
- `case_0015_submit_duplicate_create_account`
- `case_0016_submit_duplicate_checkout`
- `case_0017_run_fulfillment_worker_noop`

These are one-transition TLC edges, not manually curated fixtures. Each case has
its own `before` state loaded during `setup`, one externally driven action, and
one projected-state assertion after the action. This makes invalid cluster
residue visible because setup must establish the abstract pre-state before each
case. See `references/edge-cases.md` for how to choose these boundary cases
without assuming the system is deployed or distributed.

The example cleanup node is tagged as a finalizer. If an earlier graph node
fails after deployment, the executor skips ordinary downstream nodes but still
runs cleanup nodes whose dependencies have completed before rethrowing the
original failure.

## Validating Bug Detection

Run:

```bash
python3 examples/run_distributed_history_validation.py
```

That script validates:

- internal cases execute through spec-unit adapters;
- a negative projected-state check fails when the expected projection is
  deliberately wrong;
- the Test Graph runs the external cases;
- every external case writes `program-state.json`;
- the aggregate projected-state evidence has one matched record per generated
  external trace.

Run the full distributed topology:

```bash
python3 examples/run_distributed_history_validation.py --mode k3d
```

k3d mode deploys separate gateway, account, cart, checkout, worker, database,
and queue services. It still uses the same projected-state assertion path.
