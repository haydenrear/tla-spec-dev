# Distributed Ecommerce History Example

This example shows the internal/external view split for a small ecommerce
backend. The model describes account, cart, checkout, outbox, and fulfillment
projection behavior. Internal cases run against local Python adapters. External
cases run through Test Graph against a running service and assert projected
cluster state.

The example is intentionally small, but it uses the same seams as a larger
distributed system:

- `specs/program_model/Core.tla` defines shared ecommerce semantics.
- `specs/program_model/Internal.tla` exposes fine-grained component actions.
- `specs/program_model/External.tla` wraps the internal model in public API and
  worker-observation actions.
- `specs/program_model/adapters.py` contains unit adapters, HTTP/Test Graph
  adapters, setup/teardown hooks, a state projector, and a projected-state
  assertion adapter.
- `test_graph/` deploys the example service and runs the external cases.

There are two runtime topologies:

- Local Test Graph mode starts one monolith process. This keeps spec adapter
  iteration fast and deterministic.
- k3d Test Graph mode deploys the full distributed topology:
  `gateway-service`, `account-service`, `cart-service`, `checkout-service`,
  `worker-service`, `database-service`, and `queue-service`. The public Test
  Graph adapters hit the gateway, while setup/teardown and projected-state
  assertions flow through the gateway into the database and queue services.

Run the local adapter checks:

```bash
python3 ../../scripts/run_generated_case_adapters.py \
  specs/generated/spec_unit/ecommerce_internal_cases \
  --mapping specs/program_model/case_adapters.toml \
  --view internal \
  --batch \
  --import-root .

ECOMMERCE_BASE_URL=http://127.0.0.1:18080 \
python3 ../../scripts/run_generated_case_adapters.py \
  specs/generated/testgraph/ecommerce_external_cases \
  --mapping specs/program_model/testgraph_bindings.yml \
  --view external \
  --batch \
  --import-root .
```

The second command expects a running service. The Test Graph deployment node
starts one automatically in local mode.

Run the Test Graph:

```bash
../../../../.skill-manager/skills/test-graph/scripts/discover.py \
  --test-graph-root test_graph

../../../../.skill-manager/skills/test-graph/scripts/run.py ecommerceExternal \
  --test-graph-root test_graph
```

The graph defaults to local mode for repeatable development. To exercise k3d,
install `docker`, `k3d`, and `kubectl`, then run with:

```bash
ECOMMERCE_TEST_MODE=k3d \
../../../../.skill-manager/skills/test-graph/scripts/run.py ecommerceExternal \
  --test-graph-root test_graph
```

The k3d scripts live in `scripts/` and the Kubernetes manifests live in
`deploy/k8s/`.
