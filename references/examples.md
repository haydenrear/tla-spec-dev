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

Run it in local monolith mode:

```bash
python3 examples/run_distributed_history_validation.py --mode local
```

The validation script checks that the internal cases run, all generated
external Test Graph cases run, projected-state assertion files are written for
each external trace, a deliberate wrong projection is rejected, and k3d
deployments plus service-level REST traffic are verified in the default mode.

## Tutorial Scaffolding

`scripts/scaffold_spec.py` creates standalone tutorial/example specs. For
view-aware scaffolds, use:

```bash
python3 scripts/scaffold_spec.py request-flow --root /tmp --views internal,external
```

This creates `model/Core.tla`, `model/Internal.tla`, `model/External.tla`, and
active desired overlays `DesiredCore.tla`, `DesiredInternal.tla`, and
`DesiredExternal.tla`. The accepted `program_model` should not retain those
desired overlays after workflow closeout.

For production onboarding, use `scripts/onboard_program_model.py` so only the
accepted `specs/program_model` baseline is created.
