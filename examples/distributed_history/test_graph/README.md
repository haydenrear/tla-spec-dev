# Ecommerce External Test Graph

This graph deploys the ecommerce example and runs external generated cases
through the Test Graph adapter bindings in `../specs/program_model`.

Graph:

1. `ecommerce.deploy` deploys a k3d topology with gateway, account, cart,
   checkout, worker, database, and queue services by default. Set
   `ECOMMERCE_TEST_MODE=local` to run one local monolith process instead.
2. `ecommerce.external_cases` runs
   `scripts/run_generated_case_adapters.py` with the external Test Graph
   bindings. The cases include happy-path actions plus edge cases for duplicate
   commands, rejected commands, and idle worker behavior. The node fails unless
   every generated trace writes a per-case `program-state.json`; its envelope
   records `expectedCaseCount`, `executedCaseCount`, and the executed case
   names.
3. `ecommerce.evidence` captures the final projected state from the target.
   It also validates that each external case wrote a `program-state.json`
   projected-state assertion artifact and, in k3d mode, that every deployed web
   service received the expected REST requests and responses.
4. `ecommerce.cleanup` stops the local service or deletes the k3d cluster by
   default. Set `ECOMMERCE_KEEP_K3D=1` or `ECOMMERCE_DELETE_K3D=0` to leave the
   cluster running for debugging. Cleanup is tagged as a finalizer so it still
   runs after earlier node failures once deploy has completed.

Run:

```bash
../../../.skill-manager/skills/test-graph/scripts/run.py ecommerceExternal \
  --test-graph-root .
```

Use local mode:

```bash
ECOMMERCE_TEST_MODE=local \
../../../.skill-manager/skills/test-graph/scripts/run.py ecommerceExternal \
  --test-graph-root .
```
