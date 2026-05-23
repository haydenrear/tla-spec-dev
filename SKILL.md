---
name: spec-double-compiler
description: 'Use when creating or maintaining Python spec doubles generated from a constrained, annotated TLA+ state-machine specification, including manifests, generated fakes, ports, validators, Hypothesis strategies, traces, and adapter conformance tests.'
skill-imports:
  - unit: skill-manager
    path: references/cli.md
    reason: Explains how skill-manager exposes declared CLI tools such as tlc2, pytest, and jinja2.
    section: runtime
  - unit: skill-publisher
    path: references/skills.md
    reason: Explains installable skill layout and skill-manager.toml validation.
    section: schema
---

# Spec Double Compiler

Core slogan: **The spec should generate the mock.**

Use this skill when a developer wants TLA+ to be the canonical semantic
spec for an evolving program, especially a distributed program whose real
behavior is spread across processes, queues, files, databases, and external
services. The goal is one durable program model that grows over time, not a
pile of disconnected feature specs.

This skill does not compile arbitrary TLA+ into arbitrary Python. It
supports a constrained, annotated TLA+ profile plus a
`spec_manifest.yaml` that maps TLA+ concepts into Python concepts.

## Mental Model

Keep these layers distinct:

- Program narrative: what the system is and what must remain true as it
  evolves.
- TLA+ program spec: the canonical state machine and source of semantic truth.
- Generated Python spec double: executable fake, validators, strategies,
  traces, ports, and contract tests.
- Production implementation: optimized, distributed, real-world machinery.
- Conformance harness: tests proving production adapters preserve the
  spec behavior.

Correct frame:

```text
TLA+ defines the truth.
Python makes that truth cheap to execute in ordinary tests.
Production code conforms to the generated Python boundary.
```

Vocabulary to use consistently:

- Spec double: a generated Python fake/mock-like object that implements
  a port and embodies the TLA+ model semantics.
- Minimum reproducible contract: the smallest executable boundary that
  reproduces a slice of the program behavior, edge cases, and invariants.
- Program spec: the single evolving TLA+ model of the application-level state
  machine. Add actions, variables, invariants, and resource boundaries to this
  model as the program grows.
- Feature slice: a bounded projection of the program spec used for a local
  test, adapter, trace, or generated double. A feature slice should refine back
  to the program spec; it should not become a separate source of truth.
- Centralized semantic state: the TLA+ model's simplified state, even
  when production uses databases, queues, caches, services, or workers.
- Port: a Python Protocol or interface representing a boundary.
- Adapter: a real implementation of a port, such as Postgres, Redis,
  Kafka, an HTTP service, Rust, Go, TypeScript, or an external API.
- Conformance test: a reusable test verifying a real adapter behaves
  like the spec double.
- Validator: generated Python code checking state invariants and
  transition correctness.
- Strategy: generated Hypothesis/Faker-style data generation logic.
- Trace: a model-checked sequence of states/actions that can become a
  replayable test.
- Refinement mapping: a function mapping production state/results/events
  into simplified spec state/results/events.

## Boundary Modeling Rule

For distributed applications, model external resources as semantic ports in the
TLA+ state before writing adapters. Kafka topics, filesystem append logs,
database tables, object-store paths, notification queues, locks, checkpoints,
and process queues should not appear only as incidental setup code inside a
Python adapter when their behavior is part of correctness.

The right pattern is:

1. Model the resource in TLA+ at the level that matters for correctness.
   Example variables: `topics`, `topic_offsets`, `acked_offsets`,
   `append_log_files`, `file_manifests`, `published_keys`,
   `notification_queue`, `in_progress_runs`.
2. Define actions at the real boundary: `ProduceTopic`, `ConsumeTopic`,
   `AppendFileRow`, `CompactFileRows`, `AckNotification`,
   `StartTrainingRun`, `CompleteTrainingRun`.
3. Generate cases from those actions.
4. Use Python adapters to materialize the modeled pre-state into fake Kafka,
   temp files, in-memory stores, or test databases.
5. Observe the real production boundary after the call and refine it back to the
   modeled state.

Adapter code may write files or enqueue messages to set up a case, but those
files/messages should correspond to named TLA variables. If an adapter creates
or checks an external side effect that is not represented in the spec, record it
as a coverage gap and either model it or explicitly justify why it is outside
the semantic contract.

Do not stop at a single action like `RunRetrain` when the value is in the
distributed path. Prefer explicit lifecycle actions such as notification
emitted, notification consumed, retrain request derived, dataset exported,
training started, training completed, duplicate suppressed, and failure
dead-lettered.

## Program Spec Rule

For a real repository, default to one program spec that evolves with the
system. Do not create one TLA+ module per feature just because work arrives as
feature requests. The program spec is the semantic map of the whole application;
individual generated doubles and adapter tests are selected slices of that map.

Add new behavior by extending the program spec:

- Add or refine state variables for new program facts or resources.
- Add named actions for new process boundaries or lifecycle steps.
- Add invariants that connect the new behavior to existing program state.
- Regenerate cases and update adapter mappings.
- Use labels, labelers, and selected case execution to test the relevant slice.

Create a separate spec only when the model is genuinely a different program or
when it has an explicit refinement relationship back to the main program spec.
Small tutorial specs are acceptable for examples, but production repositories
should avoid accumulating twenty unrelated TLA+ modules that each describe one
feature and disagree about shared state.

## Program Model Planning Workflow

For repository feature work, tickets, and behavior changes, use the spec tree
as both the formal model and the plan of action:

- `specs/program_model`: the accepted baseline whole-program model. At the
  start of a change, this is the semantic truth the repository already claims.
- `specs/desired_program_model`: the planned destination. This is not only a
  future TLA+ model; it is also the structured implementation plan. It should
  carry phases, tickets, steps, dependencies, acceptance criteria, owner/status
  metadata, validation commands, adapter coverage expectations, and the target
  invariants/actions/state the repository is moving toward.
- `specs/current`: the executable model of the repository state that is
  implemented right now while work is in progress. This starts equivalent to
  `specs/program_model` for the affected behavior and advances as tickets land.

This workflow is not reserved for large migrations. Use it for ordinary
implementation tickets whenever repository behavior should be represented in
the program spec. The benefit is that each ticket updates living executable
documentation and produces spec-derived unit tests while preserving a visible
diff between baseline, current implementation, and desired outcome.

Lifecycle:

1. Before implementation, confirm `specs/current` represents the starting
   repository state and matches `specs/program_model` for the behavior being
   changed.
2. Create or update `specs/desired_program_model` with the target
   whole-program model and the plan breakdown: phases, tickets, steps,
   dependencies, status metadata, acceptance criteria, and validation evidence
   expected for each slice.
3. Implement one ticket or slice in production code.
4. Update `specs/current` to describe what is now implemented, including TLA+
   actions, manifests, adapter mappings, generated cases, tests, and progress
   metadata for the completed slice.
5. Run TLC and generated/adapted case tests for `specs/current`; treat these as
   unit tests for the current repository behavior.
6. Keep `specs/desired_program_model` updated as the plan changes. If a ticket
   splits, merges, changes order, gains a dependency, or changes acceptance
   criteria, record that there instead of leaving the plan in chat or ad hoc
   notes.
7. Repeat until `specs/current` semantically equals
   `specs/desired_program_model`.
8. Promote the converged model into `specs/program_model`, regenerate accepted
   artifacts, and delete `specs/desired_program_model` once it is equal to the
   new program model and no longer carries distinct planning state.

During this lifecycle, `specs/program_model` answers "where did we start?",
`specs/desired_program_model` answers "where are we going and by which
verified tickets?", and `specs/current` answers "what does the repository
currently implement and test?"

## When To Use

Use this workflow when the program has meaningful state, edge cases matter,
correctness is expensive, concurrency or interleavings matter, multiple
adapters exist, AI agents need compact reliable context, or production
machinery obscures business semantics. It fits distributed applications,
pipelines, permissions, billing, scheduling, workflow, inventory, ordering,
lifecycle, and continual processes.

Do not use it as a paperwork exercise for static code with no meaningful
state, for behavior that is not yet understood well enough to model, or when
generated artifacts would not be used in tests. If only one small part of the
program is mature enough to model, add that slice to the evolving program spec
and leave explicit gaps rather than starting an unrelated feature spec.

## TLA+ Profile

Supported v0 profile:

- `CONSTANTS`
- `VARIABLES`
- `Init`
- one action per command
- `Next` as a disjunction of actions
- invariants
- finite TLC model configs
- simple sets
- simple maps/functions
- records
- booleans
- enums encoded as sets
- bounded integers
- action guards
- state transitions
- explicit operation/result concepts through annotations or manifest
  entries

Avoid production concerns in the TLA+ model unless they are semantically
relevant: databases, queues, timeouts, retries, network protocols,
logging, caches, and deployment topology usually belong outside the
spec.

Read `references/tla_profile.md` before writing or reviewing a spec. Read
`templates/tla/annotations.md` before designing the manifest.

## Standard Workflow

1. For behavior changes, create or refresh `specs/desired_program_model` with
   both the target model and the implementation plan: phases, tickets, steps,
   dependencies, status metadata, acceptance criteria, and validation commands.
2. Ensure `specs/current` starts from the accepted `specs/program_model` state
   for the behavior being changed.
3. For each ticket or slice, update production code and then update
   `specs/current` to the implemented repository state.
4. Run TLC against the current finite model config.
5. Review invariants and counterexamples.
6. Update `spec_manifest.yaml` or adjacent status files if commands, state
   fields, results, ports, generators, invariants, adapters, or plan metadata
   changed.
7. Regenerate Python artifacts for the current model.
8. Review generated diffs plus the `program_model` -> `current` ->
   `desired_program_model` relationship.
9. Run spec-double self-tests.
10. Run adapter conformance tests.
11. Continue until `specs/current` equals `specs/desired_program_model`, then
    promote the converged model to `specs/program_model` and remove
    `specs/desired_program_model` once it no longer differs.

Example commands:

```bash
python scripts/scaffold_spec.py workspace
python scripts/run_tlc.sh examples/workspace/Workspace.tla examples/workspace/MC.cfg
python scripts/generate_python.py examples/workspace/spec_manifest.yaml --out examples/workspace/generated
python scripts/generate_cases_from_tlc_dump.py examples/workspace/Workspace.tla examples/workspace/MC.cfg --out examples/workspace/generated --package workspace_cases
python scripts/run_generated_case_adapters.py examples/workspace/generated/workspace_cases --mapping examples/workspace/case_adapters.toml --validate-only
pytest examples/workspace/tests
```

## Generated Artifacts

Generated packages should include:

- `types.py`: dataclasses and aliases for state, commands, results, and
  events.
- `ports.py`: generated Protocol interfaces.
- `fake.py`: deterministic in-memory spec doubles.
- `validators.py`: invariant, transition, and trace validators with
  clear assertion messages.
- `strategies.py`: Hypothesis strategies for bounded model domains.
- `traces.py`: replayable named traces from TLC or curated examples.
- `contract_tests.py`: reusable conformance tests for adapters.
- `docs.md`: metadata for humans and AI retrieval.

For whole-program case generation, generated packages may instead include:

- `types.py`: generic state-graph case dataclasses.
- `cases.py`: one explicit case per TLC action-labeled transition.
- `doubles.py`: scripted transition doubles that accept exactly one case input.
- `validators.py`: checks that case outputs match the before/after state delta.
- `docs.md`: state and transition counts plus source metadata.

These whole-program case fixtures are generated from TLC's reachable state graph,
not from Python behavior templates.

Adapter mappings are repository-local. A TOML mapping connects generated case
labels to adapter entrypoints:

```toml
[adapters.CompactDataset]
adapter = "my_project.spec_adapters:CompactDatasetAdapter"

[[adapter]]
labels = ["PublishMetadata", "LoadMarket"]
adapter = "my_project.spec_adapters:KafkaComponentAdapter"
output_projection = "my_project.spec_adapters:project_kafka_output"
```

Mappings are checked per case: at least one label on every selected case must
map to an adapter. If a case has both a coarse action label and a fine-grained
edge label, the first matching TOML entry wins, so put fine-grained mappings
before coarse fallback mappings.

`scripts/run_generated_case_adapters.py` validates coverage, can optionally ask
adapters whether they support every selected case with `--validate-capabilities`,
writes one executable Python program per selected case into a temporary work
directory, and then runs those generated programs unless `--validate-only` is
set. Use `--batch` to execute many cases in one interpreter; combine it with
`--python path/to/venv/bin/python` when the adapter needs a project venv.

Adapters live outside generated files and expose:

```python
class Adapter:
    def can_run(self, case): ...  # optional; bool or (bool, reason)
    def validate(self, case): ...
    def run(self, case, work_dir): ...
```

`run` may return `spec_double_compiler.runtime.CaseRunResult`,
`{"output": case.output, "after": case.after, "semantic_output": ...}`, or an
object with equivalent attributes. If structural `output` or `after` is omitted
or `None`, that comparison is skipped. If `output_projection` is configured, the
runner calls it with the case and compares the adapter's `semantic_output` to
the projected value.

Extra case labels can be generated with one or more `--labeler module:function`
arguments to `generate_cases_from_tlc_dump.py`. Labelers receive
`before/action/after/changed` and return a string or iterable of strings.
generic runner skips that comparison for that field.

Generated files must include a header saying TLA+ and the manifest are
the source of truth and that generated files should not be edited
directly.

Extension points should live outside generated files where possible:

```text
workspace_spec_ext/
  adapter_mapping.py
  custom_strategies.py
  production_factories.py
```

## Adapter Rule

A production adapter conforms if it implements the generated Protocol,
exposes a snapshot or observation function that maps production state to
generated spec state, returns results that normalize into generated
result types, passes generated conformance tests, and passes validators
over observed state and transitions.

Refinement mappings are first-class reviewable artifacts:

```python
def observe_adapter_state(adapter) -> WorkspaceState:
    ...

def normalize_adapter_result(result) -> CreateWorkspaceResult:
    ...

def normalize_event(event) -> SpecEvent:
    ...
```

These mappings are where distributed production machinery is related
back to centralized semantic state.

## Testing Layers

1. Spec-double self-tests: the generated fake satisfies validators,
   traces replay correctly, and strategies produce valid states and
   commands.
2. Adapter conformance tests: real adapters produce the same results as
   the spec double for generated traces, preserve invariants, and expose
   observable state that validates.
3. Regression tests from counterexamples: TLC counterexamples,
   Hypothesis failures, and production bugs become named Python traces,
   TLA+ model changes, or validator improvements.

Read `references/conformance_testing.md` for the adapter harness pattern.

## AI Retrieval Rule

Retrieve the smallest executable contract that explains the boundary.

When modifying a Postgres adapter for `WorkspacePort`, retrieve:

- `Workspace.tla` action definitions
- `spec_manifest.yaml`
- generated `types.py`
- generated `ports.py`
- generated `fake.py`
- generated `validators.py`
- generated `contract_tests.py`
- the Postgres adapter under modification

Read `references/ai_retrieval.md` when preparing context for AI-assisted code
analysis.

## Anti-Patterns

- Do not treat generated Python as the canonical source of truth.
- Do not edit generated files manually unless explicitly marked as
  extension points.
- Do not compile arbitrary TLA+ directly to Python without the
  constrained profile.
- Do not let the fake import production services.
- Do not let the fake contain database, network, queue, cache, or
  external API logic.
- Do not use interaction mocks where semantic conformance is the goal.
- Do not let generated spec doubles become production dependencies.
- Do not hide refinement mappings.
- Do not create disconnected TLA+ specs per feature in a production repository.
- Do not use TLA+ ceremony for trivial CRUD or early exploratory UI work.
- Do not confuse centralized semantic state with centralized production
  architecture.

## References

- `README.md`: quick start and file tree.
- `references/tla_profile.md`: constrained TLA+ subset.
- `references/codegen_contract.md`: manifest schema and generator behavior.
- `references/conformance_testing.md`: production adapter conformance.
- `references/ai_retrieval.md`: AI context selection.
- `references/maintenance.md`: review and regeneration rules.
- `examples/workspace/`: fully worked example.
- `examples/subscription/`: partial state-machine example.
