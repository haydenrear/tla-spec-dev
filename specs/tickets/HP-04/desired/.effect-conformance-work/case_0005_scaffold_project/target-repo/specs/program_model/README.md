# Program Model

Accepted whole-program TLA+ model for this repository. It is the semantic
baseline for future ticket workflows.

## Completion target

This directory is a SCAFFOLD. The completion target — a real, working baseline
with both views wired end to end — is:

    examples/distributed_history/specs/program_model/

Diff your tree against that one before calling onboarding done. Read
`references/testgraph_adapters.md` first: it is where the Internal/External
split and the adapter contract are actually specified.

## The baseline is not complete until it has all of these

| File | Purpose |
| --- | --- |
| `Core.tla` | shared constants and helper operators |
| `Internal.tla` / `Internal.cfg` | internal view: fine-grained program state |
| `External.tla` / `External.cfg` | external view: publicly observable behavior |
| `actions.yml` | per-action layer, controllability, and what it generates |
| `adapters.py` | spec-unit adapters AND Test Graph adapters/projector/assertion |
| `providers.py` | agent-authored generated-port effect providers |
| `effect_provider_usage.yaml` | provider state, fuzz, assertion, cleanup, and bypass evidence |
| `case_adapters.toml` | internal action -> spec-unit adapter |
| `testgraph_bindings.yml` | external action -> Test Graph adapter |
| `tlc_projection.py` | TLC state -> generated-case shapes |
| `spec_manifest.yaml` | ports, invariants, finite model, onboarding status |

A single-module baseline is NOT valid. Without `External.tla` plus Test Graph
adapters the project has no generative integration testing, which is the point
of the workflow.

## Two views, one semantic authority

- **Internal view** (`Internal.tla`) is fine-grained program/component state.
  Generates spec-unit cases, run by the spec-unit adapters in `adapters.py`.
- **External view** (`External.tla`) is what a test harness can drive or observe
  from outside. Generates Test Graph cases, run by the Test Graph adapters.

External does not mean distributed. For an HTTP service it is requests; for a
CLI, command invocations and filesystem assertions; for a library, the public
API surface and the files it writes. If the public surface is observable
filesystem behavior, then the External view *is* the library — not an add-on.

## Validate both views

```bash
scripts/run_tlc.sh specs/program_model/Internal.tla specs/program_model/Internal.cfg
scripts/run_tlc.sh specs/program_model/External.tla specs/program_model/External.cfg
tla-spec-dev --spec-root specs run spec-unit-tests
```

Test Graph nodes are end-to-end External-view executions only. TLC runs and
spec-unit runs are direct `tla-spec-dev` commands, never graph nodes.

Use `specs/current` and `specs/desired_program_model` only after this
baseline exists and a later ticket needs a planned destination. First onboarding
should not create those directories.
