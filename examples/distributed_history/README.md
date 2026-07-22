# Distributed Ecommerce History Example

This example shows the internal/external view split for a small ecommerce
backend. The model describes account, cart, checkout, outbox, and fulfillment
projection behavior. Internal cases run against local Python adapters. External
cases run through Test Graph against a running service and assert projected
program state.

The example is intentionally small, but it uses the same seams as a larger
distributed system:

- `specs/program_model/Core.tla` defines shared ecommerce semantics.
- `specs/program_model/Internal.tla` exposes fine-grained component actions.
- `specs/program_model/External.tla` wraps the internal model in public API and
  worker-observation actions. In this example External is HTTP, but for another
  project it could be CLI commands, filesystem operations, or another public
  harness surface. It records service routes such as
  gateway/account/database, gateway/cart/database, and
  gateway/checkout/database/queue as model data on generated cases.
- The accepted `program_model` intentionally has no `Desired.tla`. Active
  ticket workflows should keep desired changes in `DesiredCore.tla`,
  `DesiredInternal.tla`, and `DesiredExternal.tla`, then delete those desired
  files after promotion into `program_model`.
- `specs/program_model/adapters.py` contains unit adapters, HTTP/Test Graph
  adapters, setup/teardown hooks, a state projector, and a projected-state
  assertion adapter.
- `test_graph/` deploys the example service and runs the external cases.

The generated external cases include both happy paths and public edge cases:
duplicate create, duplicate cart mutation, missing-account cart mutation,
missing-account checkout, empty-cart checkout, duplicate checkout, fulfillment
worker drain, and idle worker drain. `External.tla` declares these public
actions over bounded clients, SKUs, orders, and reachable internal states; TLC
expands that into the external Test Graph corpus after projected-state dedupe.
The exact state and case counts for the current model are recorded in the
generated package's `docs.md` (for example
`test_graph/build/generated/manual/testgraph/ecommerce_external_cases/docs.md`
after the regeneration command below) rather than hardcoded here. The
per-action case caps those counts are gated against live in
`specs/program_model/spec_manifest.yaml` under `budgets:`, with a recorded
rationale for every value that differs from the documented defaults.
Each case uses adapter `setup` to load its modeled `before` state and adapter
`teardown` to clear residue afterward.

There are two runtime topologies:

- k3d Test Graph mode deploys the full distributed topology:
  `gateway-service`, `account-service`, `cart-service`, `checkout-service`,
  `worker-service`, `database-service`, and `queue-service`. The public Test
  Graph adapters hit the gateway, while setup/teardown and projected-state
  assertions flow through the gateway into the database and queue services.
- Local Test Graph mode starts one monolith process. This keeps spec adapter
  iteration fast and deterministic when explicitly selected.

Run the local adapter checks:

```bash
uv run tests/test_ecommerce_backend.py
uv run specs/program_model/tests/test_ecommerce_adapters.py

uv run scripts/regenerate_tlc_cases.py --out test_graph/build/generated/manual

# TLA_SPEC_DEV_ROOT points at the tla-spec-dev toolchain checkout. It defaults
# to ../.. here, which is correct for this embedded copy; a standalone checkout
# of the example must set it.
python3 "${TLA_SPEC_DEV_ROOT:-../..}/scripts/run_generated_case_adapters.py" \
  test_graph/build/generated/manual/spec-unit/ecommerce_internal_cases \
  --mapping specs/program_model/case_adapters.toml \
  --view internal \
  --batch \
  --import-root .

ECOMMERCE_BASE_URL=http://127.0.0.1:18080 \
python3 "${TLA_SPEC_DEV_ROOT:-../..}/scripts/run_generated_case_adapters.py" \
  test_graph/build/generated/manual/testgraph/ecommerce_external_cases \
  --mapping specs/program_model/testgraph_bindings.yml \
  --view external \
  --batch \
  --import-root .
```

The second command expects a running service. The Test Graph deployment node
starts one automatically when running the graph; use
`ECOMMERCE_TEST_MODE=local` when you want that target to be a local monolith.

The regeneration script drives TLC for you. If you run `tlc2` by hand against
`specs/program_model/Internal.tla` or `External.tla`, pass `-deadlock`: the
bounded models have terminal states by design, and without the flag TLC
reports a spurious deadlock error.

When this example lives in a standalone checkout (not embedded in the
tla-spec-dev repository), set `TLA_SPEC_DEV_ROOT` to the toolchain checkout so
the scripts above can find the generator, exporter, and adapter runner:

```bash
TLA_SPEC_DEV_ROOT=/path/to/tla-spec-dev \
uv run scripts/regenerate_tlc_cases.py --out test_graph/build/generated/manual
```

Run the Test Graph:

```bash
test_graph/gradlew --no-daemon -p test_graph ecommerceExternal
```

Or run the example validation wrapper from the repository root:

```bash
python3 examples/run_distributed_history_validation.py
```

The wrapper regenerates cases from TLC before running adapters and Test Graph.
The graph also regenerates external cases inside each Test Graph report under
`generated/`, so checked-in files are not the case source of truth. The graph
defaults to k3d mode. Install `docker`, `k3d`, and `kubectl`, then run:

```bash
test_graph/gradlew --no-daemon -p test_graph ecommerceExternal
```

The validation wrapper runs the same k3d path and verifies assertion artifacts:

```bash
python3 examples/run_distributed_history_validation.py
```

Use local mode explicitly for fast iteration without Kubernetes:

```bash
python3 examples/run_distributed_history_validation.py --mode local
```

The wrapper accepts an optional target example path, defaulting to this
embedded copy, so it can also validate a standalone checkout:

```bash
python3 examples/run_distributed_history_validation.py /path/to/distributed_history --mode local
```

The k3d cleanup node deletes the cluster by default. Set
`ECOMMERCE_KEEP_K3D=1` or pass `--keep-k3d` to the wrapper when debugging a
cluster after a run:

```bash
python3 examples/run_distributed_history_validation.py --keep-k3d
```

The k3d scripts live in `scripts/` and the Kubernetes manifests live in
`deploy/k8s/`.

Each external case writes `program-state.json` under the Test Graph report's
`external-case-work/case-work/<case>/` directory. The evidence node aggregates
those files into `projected-program-states.json` and fails the graph if any
expected program state differs from the projected cluster state. The
`ecommerce.external_cases` envelope publishes the executed case names as
`caseNames`, the generated trace names as `expectedCaseNames`, and the
generated trace manifest path as `traceManifest` (case counts appear only as
node metrics, not as envelope keys), so a fast run is still auditable.
