# Ecommerce External Test Graph

This graph deploys the ecommerce example and runs external generated cases
through the Test Graph adapter bindings in `../specs/program_model`.

Graph:

1. `ecommerce.deploy` starts the service in local mode by default, or deploys to
   k3d when `ECOMMERCE_TEST_MODE=k3d`.
2. `ecommerce.external_cases` runs
   `scripts/run_generated_case_adapters.py` with the external Test Graph
   bindings.
3. `ecommerce.evidence` captures the final projected state from the cluster.
4. `ecommerce.cleanup` stops the local service. In k3d mode it leaves the
   cluster running unless `ECOMMERCE_DELETE_K3D=1` is set.

Run:

```bash
../../../.skill-manager/skills/test-graph/scripts/run.py ecommerceExternal \
  --test-graph-root .
```

Use k3d:

```bash
ECOMMERCE_TEST_MODE=k3d \
../../../.skill-manager/skills/test-graph/scripts/run.py ecommerceExternal \
  --test-graph-root .
```
