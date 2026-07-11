# Examples

The repository keeps examples for skill development and for users who need a
small concrete model before applying the workflow to a production repository.

## Distributed History Ecommerce

`examples/distributed_history/` is the fully worked example for the current
internal/external Test Graph adapter workflow.

It shows:

- an accepted closed `specs/program_model` with `Core.tla`, `Internal.tla`, and
  `External.tla`;
- no `Desired.tla` in the accepted program model;
- active desired-view scaffolding through `DesiredCore.tla`,
  `DesiredInternal.tla`, and `DesiredExternal.tla`;
- internal/spec-unit generated cases and adapters;
- external/Test Graph generated cases and HTTP adapters;
- TLC regeneration through `scripts/regenerate_tlc_cases.py`;
- external edge cases for duplicate, missing-resource, empty-cart, and idle
  worker behavior;
- an External model that records public service routes and finite input data,
  then lets TLC generate hundreds of reachable integration cases;
- batch setup/teardown hooks for cleaning deployed state;
- per-case setup/teardown hooks for loading and clearing case state;
- projected-state assertions that compare expected TLA program state to actual
  deployed state;
- a Test Graph project that runs locally or against k3d;
- a k3d topology with gateway, account, cart, checkout, worker, database, and
  queue services.

Run the workflow contract check:

```bash
python3 examples/validate_split_desired_workflow.py
```

Run the distributed example against k3d:

```bash
python3 examples/run_distributed_history_validation.py
```

That wrapper regenerates internal and external case packages from TLC before
running adapters and Test Graph. Generated case packages are written under
`test_graph/build/` or the validation report, not kept as source files.
With the current bounds, the example emits 93 internal/spec-unit cases and 732
external/Test Graph cases after projected-state dedupe.

Run it in local monolith mode:

```bash
python3 examples/run_distributed_history_validation.py --mode local
```

The validation script checks that the internal cases run, all generated
external Test Graph cases run, projected-state assertion files are written for
each external trace, a deliberate wrong projection is rejected, and k3d
deployments plus service-level REST traffic are verified in the default mode.

## Tutorial Scaffolding

`scripts/scaffold_spec.py` creates standalone tutorial/example specs:

```bash
python3 scripts/scaffold_spec.py request-flow --root /tmp
```

It emits the same accepted baseline shape as `tla-spec-dev scaffold project`,
because there is only one accepted shape:

```
Core.tla
Internal.tla  Internal.cfg    internal view -> spec-unit cases
External.tla  External.cfg    external view -> Test Graph cases
actions.yml
adapters.py                   spec-unit adapters AND Test Graph adapters
case_adapters.toml            internal action -> spec-unit adapter
testgraph_bindings.yml        external action -> Test Graph adapter
tlc_projection.py
spec_manifest.yaml
```

Both views are always emitted; there is no view-less scaffold. A spec with no
External view generates no Test Graph cases, so it can never be validated
against its public surface.

It also creates the active desired overlays `DesiredCore.tla`,
`DesiredInternal.tla`, and `DesiredExternal.tla`. These belong to an open spec
workflow; promote them into the baseline and delete them at closeout. An
accepted, closed `program_model` must not retain them.

For production onboarding, use
`tla-spec-dev --spec-root specs scaffold project --name ProjectName` so only
the accepted `specs/program_model` baseline is created.
