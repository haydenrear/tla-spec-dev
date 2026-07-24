# Generation Modes

Spec Double Compiler has two related generation paths. Keep them distinct.

## Manifest-Driven Spec Doubles

Use `scripts/generate_python.py` when a reviewed `spec_manifest.yaml` defines
the Python API shape:

```bash
python scripts/generate_python.py path/to/spec_manifest.yaml --out path/to/generated
```

This mode generates:

- Python dataclasses for states, commands, results, and events.
- Protocols for ports.
- A deterministic fake/spec double from explicit manifest templates.
- Validators, strategies, traces, contract tests, and generated docs.

This is best when the boundary API is known and the manifest is the reviewed
bridge from TLA+ names to Python names.

## TLC State-Graph Cases

Use `scripts/generate_cases_from_tlc_dump.py` when TLC's reachable state graph
is the case source of truth:

```bash
python scripts/generate_cases_from_tlc_dump.py path/to/Model.tla path/to/MC.cfg --out path/to/generated --package model_cases
```

This mode generates:

- One `StateGraphCase` per action-labeled TLC edge.
- Generic before/input/output/after case descriptors.
- Recovered action `params` on each case input (on by default; MF-029).
  Unrecoverable arguments are the `UNCHECKED` sentinel, provenance is recorded
  in `params:*` labels and `param_recovery_audit.md`, and `--no-infer-params`
  reverts to `params={}`.
- A scripted transition double that accepts exactly the generated case input.
- Validators for structural replay.

`--view internal|external` with `--actions-metadata` generates view-aware
packages (`spec-unit/` and `testgraph/` output subdirectories); optional
`--state-projector`, `--output-projector`, `--dedupe projected`, and
`--labeler` hooks shape the emitted corpus.

The run prints the advisory complexity scan before TLC — findings to read,
never a refused build — and, after the complete package is written, checks the
corpus against the manifest case caps (`max_internal_cases_per_component`,
`max_external_cases_per_action`). Over cap it reports the distribution, asks a
redesign question, and exits nonzero without trimming a single case.

Repository-local adapters then map real production boundaries to these generic
case descriptors through `case_adapters.toml` and
`scripts/run_generated_case_adapters.py`.

Every TLC run used to produce this state graph has a hard wall-time budget:
`budgets.tlc_seconds` in `spec_manifest.yaml`, default 120 seconds. Wrap the
model-check command in an external timeout of that many seconds and stop it
when the budget expires. A timeout means the diagram is not a viable case-generation
abstraction. First inspect domain cardinalities, variable combinations, action
branching, interleavings, symmetry, and TLC progress output to identify what
multiplies the state count. Distinguish compressible modeling detail from
essential program complexity. Then introduce another diagram/refinement with
smaller bounded domains, less irrelevant state, or separated independent
lifecycles. Do not increase the timeout or wait for the same state space. When
essential complexity remains, give the user concrete options for lowering
program complexity, with the semantic and coverage tradeoff of each option,
before choosing what to omit.

## Relationship To Program Workflow

`program_model`, `current`, and `desired_program_model` are workflow roles, not
generation modes.

- `program_model` is the accepted baseline.
- `current` is the whole-program model implemented right now during active
  ticket work.
- `desired_program_model` is the target model plus ticket plan.

Either generation mode can be used from the appropriate workflow directory, but
for whole-program behavior changes the TLC state-graph case path is usually the
better fit because it keeps cases tied directly to the reachable model.
