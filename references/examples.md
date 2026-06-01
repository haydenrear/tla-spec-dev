# Examples

The repository keeps examples for skill development and for users who need a
small concrete model before applying the workflow to a production repository.

## Workspace

`examples/workspace/` is the fully worked example.

It shows:

- a constrained TLA+ module;
- a `spec_manifest.yaml` for manifest-driven spec-double generation;
- generated Python artifacts under `examples/workspace/generated/workspace_spec`;
- TLC-derived whole-program cases under
  `examples/workspace/generated/workspace_cases`;
- adapter mapping through `case_adapters.toml`;
- conformance and adapter-mapping tests.

Use this example when changing generators, runtime behavior, adapter mappings,
or docs that describe the core workflow.

## Subscription

`examples/subscription/` is a partial lifecycle-state example.

It is useful for modeling shape and documentation, but it is not a fully worked
adapter/conformance example.

## Distributed History

`examples/distributed_history/` is a workflow-history example.

It shows:

- first-project onboarding into `specs/program_model`;
- opening a desired/current ticket workflow;
- a desired model that spans two distributed tickets;
- updating `specs/current` after each landed ticket;
- closing each ticket from `specs/desired_program_model/ticket_plan.yaml`;
- closing the workflow into `specs/.history/<workflow-name>/closed-snapshot`;
- a replay script that regenerates the example from the workflow commands.

## Tutorial Scaffolding

`scripts/scaffold_spec.py` creates standalone tutorial/example specs under
`examples/`. It is not the first-project onboarding path for production
repositories. For production onboarding, use `scripts/onboard_program_model.py`.
