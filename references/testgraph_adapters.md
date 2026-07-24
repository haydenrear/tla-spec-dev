# Test Graph Adapters

This reference describes the External/Test Graph adapter path. Use
`examples/distributed_history/` as the concrete reference implementation.

Read this **before authoring any spec baseline**. Test Graph adapters are
foundational to every project, not an add-on for distributed systems. A baseline
without an External view and its adapters generates no Test Graph cases, so the
repository's public surface is never validated.

## What the scaffold gives you

`tla-spec-dev scaffold project` emits the full baseline shape:

```
specs/program_model/
  Core.tla                 shared constants and operators
  Internal.tla  Internal.cfg   internal view  -> spec-unit cases
  External.tla  External.cfg   external view  -> Test Graph cases
  actions.yml              per-action layer, controllability, what it generates
  adapters.py              spec-unit adapters AND Test Graph adapters
  providers.py             agent-authored generated-port effect providers
  effect_provider_usage.yaml  provider state, fuzz, assertion, and bypass evidence
  case_adapters.toml       internal action -> spec-unit adapter
  testgraph_bindings.yml   external action -> Test Graph adapter
  tlc_projection.py        TLC state -> generated-case shapes
  spec_manifest.yaml       ports, invariants, finite model, status
```

These are placeholders to restructure, not a finished baseline. Onboarding is
done only when both views model-check under TLC, both adapter mappings cover
every action of their layer, and the repository has a `test_graph` project.
Diff your tree against `examples/distributed_history/specs/program_model/`
before calling it done.

The External view, the bindings, and the skeleton adapters are **onboarding
deliverables**. Tickets own per-slice adapter implementations, not the structure.

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

## External Channel Enforcement

Added by MF-015. External-ness used to be asserted structurally and never
verified, so a Test Graph adapter could import the production package and
quietly degenerate into a spec-unit adapter. Three hard gates now verify it.
Both `scripts/run_generated_case_adapters.py` and
`scripts/export_testgraph_cases.py` apply them, and both refuse to proceed on
violation. There is no override flag anywhere in this path.

### 1. Every binding declares a channel

```yaml
actions:
  SubmitCheckout:
    channel: http          # http | cli | fs | queue | k8s
    adapter: specs.program_model.adapters:CheckoutHttpAdapter
```

A binding whose author did not say how the program is driven has not declared
an external channel. Absence fails; there is no default and no inference from
the adapter name.

To drive a transport beyond the base five, name it explicitly in the contract:

```yaml
external:
  additional_channels: [grpc]
```

That is a visible per-program declaration, in the same shape as raising a
budget in the manifest. It widens the accepted set. It can never excuse a
binding that declares no channel at all.

### 2. Adapters may not import the production package

```yaml
external:
  production_package: ecommerce
```

The `adapter`, `projector`, `expected_projection` and `assertion` modules of
every external binding are parsed with `ast` and checked for any import of the
declared package. All four roles run inside the harness process, so all four
are isolated. The analysis is **transitive** across first-party modules: an
adapter that imports a local helper which imports the production package is
running production code in-process just the same, and only following direct
imports would make the gate trivially evadable. Dynamic
`importlib.import_module("pkg")` and `__import__("pkg")` with literal arguments
are covered too.

Note what is *not* an offense: importing `spec_double_compiler.runtime` for
`CaseRunResult` is the adapter harness contract, not the program under test.
The gate targets exactly the declared `production_package`.

A violation reports the adapter, the offending import, and the remediation:

```text
ERROR: external channel enforcement failed for 1 binding(s) in .../testgraph_bindings.yml
  action SubmitCheckout
    adapter:     specs.program_model.adapters:CheckoutHttpAdapter
    problem:     adapter module specs.program_model.adapters imports production
                 package 'ecommerce'; a Test Graph adapter that imports the
                 program under test is running it in-process, not over the
                 declared http channel
    remediation: rebind this action as a spec-unit adapter in
                 case_adapters.toml, or drive the declared channel instead of
                 calling the production package in-process
```

### 3. Port binding configurations declare the integration-ladder rung

```yaml
external:
  port_bindings:
    HistoryPort: real
    OrderPort: real
    ClockPort: double
```

Each port is bound to exactly `double` or `real`. This is what lets a graph run
say which rung of the integration ladder it occupies; the exported
`manifest.json` carries it as `integration_rung`.

**At least one port must be `real`.** With every port doubled nothing real is
under test, which is a spec-unit run — all-doubles is never a graph node. That
matches the binding ladder in `references/modular_fuzzing.md`.

### No degenerate escapes

Every absent declaration **fails**; none of them skips the check. A missing
`external:` block, a missing `production_package`, and a missing `port_bindings`
are each violations in their own right. A gate that silently disables itself
when its input is absent is the degeneracy
`references/architecture_tractability.md` forbids, so this module contains no
`when present` conditional, no fallback default, and no override parameter.


## Projected-State Assertions

External assertions compare the expected program state from the generated case
to actual deployed state projected back into the TLA model shape.

The binding file wires this:

```yaml
actions:
  SubmitCheckout:
    channel: http
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
test_graph/build/validation-reports/<run>/external-case-work/case-work/<opaque-case-key>/program-state.json
```

The JSON payload carries the original case name. Work-directory components are
stable opaque digests so generated names cannot traverse or alias the report
root.

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
  --out test_graph/build/generated/manual
```

This writes a Python case package that materializes TLC graph edges for adapter
execution. The package is generated IR, not hand-maintained test source. Test
Graph runs regenerate the external package inside each validation report. The
current bounded model emits 93 internal/spec-unit cases and 732 external/Test
Graph cases after projected-state dedupe. The external manifest is the source
of truth:

```text
examples/distributed_history/test_graph/build/validation-reports/<run>/generated/testgraph/traces/manifest.json
```

The generated external cases cover these public action families:

- account creation and duplicate account creation;
- cart mutation, duplicate cart mutation, and missing-account cart rejection;
- checkout success, duplicate checkout, empty-cart rejection, and
  missing-account checkout rejection;
- fulfillment worker drain and idle worker drain.

`External.tla` also records service routes in action params, such as
gateway/account/database for account creation and
gateway/checkout/database/queue for accepted checkout. Those routes are model
data used by the generated cases and evidence, not manually curated test names.

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
  external trace;
- in k3d mode, every ecommerce deployment is ready and each web service records
  the expected REST request/response statuses.

The wrapper defaults to the full k3d topology:

```bash
python3 examples/run_distributed_history_validation.py
```

Use local monolith mode explicitly for fast iteration:

```bash
python3 examples/run_distributed_history_validation.py --mode local
```

k3d mode deploys separate gateway, account, cart, checkout, worker, database,
and queue services. It still uses the same projected-state assertion path and
deletes the cluster during cleanup unless `--keep-k3d`,
`ECOMMERCE_KEEP_K3D=1`, or `ECOMMERCE_DELETE_K3D=0` is set.
