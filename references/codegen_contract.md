# Codegen Contract

The v0 generator is manifest-driven. The manifest is a reviewed bridge
between TLA+ semantics and generated Python API shape.

## Required Manifest Keys

```yaml
module: Workspace
package: workspace_spec
state: {}
types: {}
commands: {}
results: {}
ports: {}
invariants: []
```

## Manifest Concepts

- `module`: TLA+ module name. The generator expects `<module>.tla` next
  to the manifest.
- `package`: Python package name to generate.
- `state`: generated state dataclasses and field mappings to TLA+
  variables/constants.
- `types`: Python aliases for finite TLA+ domains or scalar types.
- `commands`: generated command dataclasses and TLA+ action references.
- `results`: generated result dataclasses.
- `ports`: generated Protocols and method mappings.
- `invariants`: invariant names to validate.
- `finite_model`: finite domains mirrored from TLC config for strategies.
- `generators`: strategy and trace settings.
- `fake`: explicit v0 action templates for generated spec doubles.
- `invariant_templates`: explicit v0 templates for validators.
- `example_traces`: replayable Python command traces.

## v0 Flow

1. Read `spec_manifest.yaml`.
2. Validate that referenced TLA+ module, action names, and invariant
   names exist with textual checks.
3. Generate dataclasses from manifest state, command, and result
   declarations.
4. Generate Protocols from manifest ports.
5. Generate `fake.py` using simple action templates.
6. Generate `validators.py` from manifest invariants and invariant
   templates.
7. Generate `strategies.py` from finite domains.
8. Generate `contract_tests.py` from ports and commands.
9. Generate `docs.md` from manifest metadata.
10. Optionally ingest TLC traces when available.

## Whole-Program Case Flow

For distributed applications, the preferred source of generated doubles is the
evolving program spec. Generated cases are selected edges from TLC's reachable
state graph, not independent feature models and not hand-coded behavioral
fakes.

1. Run TLC with `-dump dot,actionlabels`.
2. Parse DOT nodes as complete semantic states.
3. Parse DOT edges as action-labeled transitions.
4. Generate one Python `StateGraphCase` per edge:
   - `before`: full pre-state
   - `input`: action label plus source/target node ids
   - `output`: structural state delta
   - `after`: full post-state
   - `labels`: stable selectors such as action names
5. Generate `ScriptedTransitionDouble`, which accepts exactly the case input and
   returns exactly the generated output.
6. Adapter-specific mapping code, outside generated files, translates real
   Kafka records, HTTP requests, database rows, files, or process outputs to and
   from these generic case descriptors.
7. A repository-local TOML file maps case labels to adapter import paths.
8. `scripts/run_generated_case_adapters.py` validates mapping coverage, writes
   one Python program per selected case into a work directory, or executes the
   selected cases in one process with `--batch`.

The key rule is that Python cases come from TLC output. The generator should not
encode product-specific transition behavior.

Case generation and adapter execution are spec-relative. TLC runs with the spec
directory as its working directory, and relative output paths such as `cases/`
or `generated/` resolve under that spec directory unless the caller supplied a
path that already points inside it. This prevents a repository-root `cases/`
directory from becoming an accidental second source of generated state.

The second key rule is that new behavior should usually extend the existing
program model. A generated double may focus on one feature slice or adapter, but
the case must still come from the shared program state. Use labels and selected
execution to narrow tests; do not fork the semantic source of truth into a new
feature spec unless it is explicitly a separate program or a named refinement
layer.

## Distributed Boundary Modeling

Whole-program specs should model external resources that participate in
correctness. It is acceptable to abstract them, but they need a named semantic
state so adapters can materialize and observe them consistently.

Recommended resource variables:

- Kafka-like topics: `topics`, keyed by topic name, containing ordered records
  with key, event type, payload identity, partition/offset if relevant.
- Consumer progress: `consumer_offsets`, `acked_offsets`, `dead_letters`.
- Filesystem append logs: `append_log_files`, `file_manifests`,
  `compactor_state`, `published_keys`.
- Notification systems: `notifications`, `subscriber_reports`,
  `retrain_requests`.
- Training lifecycle: `in_progress_runs`, `completed_runs`, `failed_runs`,
  `checkpoints`.

Recommended action shape:

```text
Production component action ==
  consume modeled input resource
  validate preconditions
  update modeled output resource
  update semantic business state
```

Adapters should then:

1. Materialize `case.before` resource variables into temp files, fake Kafka,
   in-memory stores, or test databases.
2. Call the production boundary.
3. Observe the same resources after the call.
4. Return structural `after` and, where useful, `semantic_output`.

If adapter setup writes files or queues messages that are not represented by a
TLA variable, the spec is under-modeled. Either add the resource to the spec or
document why that side effect is outside the contract. Hidden adapter setup is a
warning sign because it means generated cases cannot vary that resource or
check its edge cases.

Adapter mapping format:

```toml
[adapters.ActionLabel]
adapter = "package.module:AdapterClass"
output_projection = "package.module:expected_semantic_output"

[[adapter]]
labels = ["AnotherLabel", "ThirdLabel"]
adapter = "package.module:adapter_factory"
```

The workspace example uses `examples/workspace/case_adapters.toml` to map the
TLC `Create` action label to `examples/workspace/case_adapters.py`.

The generic runner requires every generated case to have at least one mapped
label before it runs anything. This prevents silently ignoring new TLA actions
while still allowing fine-grained labels to override coarse action mappings.
Mappings are considered in TOML order.

Adapters may expose `can_run(case) -> bool | tuple[bool, str]`. With
`--validate-capabilities`, the runner checks selected cases against the mapped
adapter before generating or executing programs. This catches labels whose
adapter is present but cannot handle every edge shape under that label.

`output_projection` is optional. It points at a repository function that derives
semantic expected output from a generated case. The adapter returns
`semantic_output`, and the runner compares it to the projection. Structural
`output` and `after` comparisons remain available.

Use `--batch` for large case sets. It runs cases in one interpreter while still
reporting failures by case name and mapped label. If an adapter needs a project
venv, pass `--python path/to/python`; the runner re-executes the batch under
that interpreter.

If adapter execution is launched from the repository root with spec-local case
paths, pass `--spec-dir specs` or a mapping path inside the spec directory so
relative work directories and fallback imports resolve to the same spec-local
layout.

Use `generate_cases_from_tlc_dump.py --labeler package.module:function` to add
stable labels such as `ready_one_record`, `partial_context`, or
`already_exported`. Labelers receive `before/action/after/changed` and must stay
repository-local so the skill remains domain-neutral.

## v1 Flow

1. Add a TLA+ AST or structured extraction layer.
2. Extract action guards and transitions for the constrained subset.
3. Generate fake transition functions more directly from TLA+
   expressions.
4. Export TLC state graphs and traces.
5. Convert counterexamples into Python regression tests.
6. Support richer refinement mapping scaffolds.

## Determinism

Generated output must be deterministic:

- Preserve manifest ordering.
- Use stable import ordering.
- Use stable file headers.
- Avoid timestamps.
- Keep generated code formatting predictable.

Header:

```python
# Generated by Spec Double Compiler.
# Source of truth:
#   - Workspace.tla
#   - spec_manifest.yaml
# Do not edit this file directly.
# Extension points are marked explicitly.
```

## Extension Points

Keep user-authored code outside generated packages when possible:

```text
workspace_spec_ext/
  adapter_mapping.py
  custom_strategies.py
  production_factories.py
```

Expected hooks:

- `observe_adapter_state`
- `normalize_adapter_result`
- `normalize_event`
- adapter factories
- custom strategy constraints
- custom invariant explanations

These hooks are reviewable artifacts. They should not be hidden inside
generated files.
