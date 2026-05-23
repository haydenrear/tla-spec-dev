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
spec for a meaningful stateful feature, and wants generated Python
artifacts that make that truth cheap to execute in ordinary tests.

This skill does not compile arbitrary TLA+ into arbitrary Python. It
supports a constrained, annotated TLA+ profile plus a
`spec_manifest.yaml` that maps TLA+ concepts into Python concepts.

## Mental Model

Keep these layers distinct:

- Product narrative: why the feature exists.
- TLA+ spec: the canonical state machine and source of semantic truth.
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
  reproduces the behavior, edge cases, and invariants of a feature.
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

## When To Use

Use this workflow when the feature has meaningful state, edge cases
matter, correctness is expensive, concurrency or interleavings matter,
multiple adapters exist, AI agents need compact reliable context, or
production machinery obscures business semantics. It fits permissions,
billing, scheduling, workflow, inventory, ordering, lifecycle, and
distributed behavior.

Do not use it when the feature is mostly static, behavior is not yet
understood, state space is trivial, generated artifacts would not be used
in tests, or maintenance cost exceeds semantic-drift risk.

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

1. Write or update the TLA+ model first.
2. Run TLC against a finite model config.
3. Review invariants and counterexamples.
4. Update `spec_manifest.yaml` if commands, state fields, results, ports,
   generators, or invariants changed.
5. Regenerate Python artifacts.
6. Review generated diffs.
7. Run spec-double self-tests.
8. Run adapter conformance tests.
9. Update production adapters only after the generated boundary is clear.

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
- Do not assume every feature deserves TLA+.
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
