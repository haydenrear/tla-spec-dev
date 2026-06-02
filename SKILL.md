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

## First Project Onboarding Workflow

When a repository does not yet have a TLA+ program model, do not start with
`specs/current` or `specs/desired_program_model`. Those directories are for a
later ticket workflow after an accepted baseline exists.

First onboarding creates only:

- `specs/program_model`: the accepted whole-program semantic baseline.

This baseline is the initial source of truth for the project. It should model
the repository's current behavior, including state variables, actions,
invariants, resource boundaries, manifests, adapter mappings, and validation
evidence needed to generate and run spec-derived cases. It is not a desired
future state and it is not a ticket plan.

To onboard an existing repository for the first time, use:

```bash
python path/to/tla-spec-dev/scripts/onboard_program_model.py --repo-root .
```

Use `--name SkillManager` or another explicit module name when the repository
directory name is not the desired TLA+ module name. Use `--spec-root` when the
repository keeps specs somewhere other than `specs`.

After `specs/program_model` exists, later behavior tickets may use
`new_ticket_workflow.py` to create `specs/current` and
`specs/desired_program_model` from that accepted baseline.

Use `specs/current` and `specs/desired_program_model` only while planning and
executing active ticketed behavior changes. They are not first-onboarding
directories and they are not general reference folders for ordinary spec
browsing.

For the end-to-end flow, read `references/typical_workflow.md`. It covers
first onboarding, feature-ticket scaffolding, incremental current-model
updates, promotion, and closeout.

## Program Model Ticket Workflow

For repository feature work, tickets, and behavior changes, use the spec tree
as both the formal model and the plan of action:

- `specs/program_model`: the accepted baseline whole-program model. At the
  start of a change, this is the semantic truth the repository already claims.
- `specs/desired_program_model`: the planned destination. This is not only a
  future TLA+ model; it is also the structured implementation plan. It should
  carry phases, tickets, steps, dependencies, acceptance criteria, owner/status
  metadata, validation commands, adapter coverage expectations, and the target
  invariants/actions/state the repository is moving toward.
- `specs/current`: the executable whole-program model of the repository state
  that is implemented right now while work is in progress. Treat it as a
  working copy of `specs/program_model`, not as a ticket-local projection. It
  starts equivalent to the entire accepted program model and advances as tickets
  land, preserving every existing modeled behavior unless the ticket explicitly
  changes that behavior.

This workflow is normal development practice for model-worthy behavior. Use it
for ordinary implementation tickets whenever repository behavior should be
represented in the program spec. The benefit is that each ticket updates living
executable documentation and produces spec-derived unit tests while preserving a
visible diff between baseline, current implementation, and desired outcome.

Lifecycle:

1. Before implementation, confirm `specs/current` represents the starting
   repository state and matches the entire `specs/program_model`. Do not copy
   only the feature or boundary being changed.
2. Create or update `specs/desired_program_model` with the target
   whole-program model and the plan breakdown: phases, tickets, steps,
   dependencies, status metadata, acceptance criteria, and validation evidence
   expected for each slice.
3. Implement one ticket or slice in production code.
4. Update `specs/current` to describe the whole program as now implemented,
   including TLA+ actions, manifests, adapter mappings, generated cases, tests,
   and progress metadata for the completed slice. Existing state, actions, and
   invariants from `specs/program_model` remain present unless the production
   behavior itself changed.
5. Run TLC and generated/adapted case tests for `specs/current`; treat these as
   unit tests for the current repository behavior.
6. Keep `specs/desired_program_model` updated as the plan changes. If a ticket
   splits, merges, changes order, gains a dependency, or changes acceptance
   criteria, record that there instead of leaving the plan in chat or ad hoc
   notes.
7. Repeat until `specs/current` semantically equals
   `specs/desired_program_model`.
8. Promote the converged model into `specs/program_model`, regenerate accepted
   artifacts, and delete `specs/current` plus `specs/desired_program_model`
   once they no longer carry distinct planning state.

During this lifecycle, `specs/program_model` answers "where did we start?",
`specs/desired_program_model` answers "where are we going and by which
verified tickets?", and `specs/current` answers "what does the repository
currently implement and test?"

Hard rule: do not model tests, test runners, graph nodes, integration harnesses,
or validation workflow mechanics as TLA+ state/actions in `specs/current`,
`specs/program_model`, or `specs/desired_program_model`. Test graph nodes,
pytest commands, CI jobs, and integration scripts are evidence for a semantic
program action; they are not program behavior. Keep them in manifests,
ticket_plan evidence, status sections, or adapter validation commands.

To start this ticket structure in a repository that already has
`specs/program_model`, use:

```bash
python path/to/tla-spec-dev/scripts/new_ticket_workflow.py TICKET-123 "Ticket title" --repo-root .
```

The scaffold resolves all workflow directories under `--spec-root`, which
defaults to `specs`. It copies the existing `program_model` baseline into
`current` and `desired_program_model` where useful, then adds ticket workflow
metadata, `ticket_plan.yaml`, and `status` sections to the workflow manifests.
The generated comments are intentionally instructional; replace them with the
project's actual state, actions, adapter boundaries, tests, and evidence as the
ticket is refined. Do not use this for first project onboarding.

After `specs/current` semantically equals `specs/desired_program_model`,
promote the converged model into `specs/program_model`, regenerate accepted
artifacts, and then remove the workflow directories. `close_tickets.py` can do
the final cleanup after validating that current, desired, and promoted
program-model semantic files match and that all tickets in `ticket_plan.yaml`
are closed:

```bash
python path/to/tla-spec-dev/scripts/close_tickets.py --repo-root .
```

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
`references/generation_modes.md` before choosing between manifest-driven fake
generation and TLC state-graph case generation. Read
`templates/tla/annotations.md` before designing the manifest.

## Standard Workflow

0. For first onboarding of a repository with no accepted model, create
   `specs/program_model` with `scripts/onboard_program_model.py`. Do not create
   `specs/current`, `specs/desired_program_model`, or `ticket_plan.yaml` during
   first onboarding.
1. For later behavior changes, create or refresh `specs/desired_program_model` with
   both the target model and the implementation plan: ticket breakdown, steps,
   dependencies, status metadata, acceptance criteria, and validation commands.
   Use `scripts/new_ticket_workflow.py` when the repository does not have this
   ticket workflow structure yet but already has `specs/program_model`.
2. Ensure `specs/current` starts from the entire accepted
   `specs/program_model`, not only the behavior being changed.
3. For each ticket or slice, update production code and then update
   `specs/current` to the implemented whole-program repository state.
4. Run TLC against the current finite model config.
5. Review invariants and counterexamples.
6. Update `spec_manifest.yaml` or adjacent status files if commands, state
   fields, results, ports, generators, invariants, adapters, or plan metadata
   changed.
7. Regenerate Python artifacts for the current model.
8. Review generated diffs plus the `program_model` -> `current` ->
   `desired_program_model` relationship.
   The diff should show semantic program changes, not integration-test
   scaffolding modeled as state-machine behavior.
9. Run spec-double self-tests.
10. Run adapter conformance tests.
11. For ticketed desired/current work, write an append-only close record before
    moving the active context forward.
12. Continue until `specs/current` equals `specs/desired_program_model`, then
    promote the converged model to `specs/program_model`, write a workflow
    close record, and remove `specs/current` plus `specs/desired_program_model`
    once they no longer carry distinct planning state. Use
    `scripts/close_tickets.py` for validated cleanup after promotion.

Example commands:

See `references/typical_workflow.md` for repository onboarding, feature-ticket
workflow, promotion, and closeout commands. See
`references/generation_modes.md` for generation commands.

## Spec-Relative Execution Rule

Treat the spec directory as the artifact boundary. TLC should run with the spec
directory as its working directory, and relative outputs such as `cases/`,
`generated/`, result files, and adapter work directories should resolve under
that spec directory unless the caller supplied an explicit path already inside
it.

This keeps active state local:

- `specs/cases` or `examples/workspace/cases`: generated TLC edge cases.
- `specs/generated` or `examples/workspace/generated`: generated Python
  packages.
- `specs/results`: TLC, adapter, and test evidence.
- `specs/.history/<workflow-name>`: append-only workflow history.

Do not rely on the repository root as the implicit output location for TLA
artifacts. If a workflow is launched from the repository root, pass the TLA file
or `--spec-dir` so scripts can resolve outputs back to the spec directory.

## Desired/Current Migration Loop

For large migrations, keep two coordinated spec views around the accepted
baseline:

- `specs/program_model`: the accepted whole-program baseline.
- `specs/desired_program_model`: the intended whole-program end state and
  implementation plan.
- `specs/current`: the executable whole-program model of the repository state
  currently implemented while work is in progress.

Use this loop for each slice:

1. Update the desired program model with what was learned from the previous
   slice, including ticket breakdown, status metadata, validation commands, and
   done, in-progress, and pending boundaries.
2. Update the current program model to include the whole program as currently
   implemented, preserving baseline behavior from `specs/program_model` unless
   production behavior changed.
3. Add or update current adapters and unit tests first. These tests should
   validate the control surface, rendering, or refinement mapping without
   requiring the full integration graph unless that is the slice under test.
4. Run TLC and the current adapter/unit tests.
5. Add the behavior to the test graph with explicit external assertions. Do
   not rely only on a wrapper exit code when Helm, Kubernetes, databases,
   queues, files, or services are the actual boundary. Assert with the real
   external tool (`kubectl`, `helm`, SQL, Kafka admin, filesystem inspection,
   HTTP, etc.) and publish useful endpoint/context data for downstream nodes.
6. Run the narrow graph for the slice.
7. Mark the ticket closed in `specs/desired_program_model/ticket_plan.yaml`,
   record run ids and evidence paths, then close the ticket with
   `python scripts/close-ticket.py <ticket-id> --result <evidence-path>`.
8. Sync the desired model metadata to mark the refined boundary as done.
9. Commit the ticket close record, spec changes, and evidence together.

This loop keeps the desired model honest, the current model executable, and
the behavioral graph anchored to externally observable facts.

## Append-Only Spec Evolution History

`specs/.history/<workflow-name>/` is append-only history for a specific
desired/current workflow. Do not edit an existing close entry; create another
entry name only when a ticket or workflow needs another checkpoint. This lets an
agent retrieve only active state plus selected history entries instead of
repeatedly reading every prior desired/current version.

The ticket source of truth is
`specs/desired_program_model/ticket_plan.yaml`. Do not invent repository-level
Markdown ticket files for this workflow.

Per-ticket close:

```bash
python scripts/close-ticket.py TICKET-123 --summary "Recorded ticket-level history" --result specs/results/adapter.txt
```

Whole-workflow close:

```bash
python scripts/close_tickets.py --repo-root . --summary "Promoted desired/current into program_model"
```

Each entry includes a machine-readable `manifest.json`, a human-readable
`summary.md`, snapshots of `program_model`, `desired_program_model`, and
`current` when present, the ticket mapping from `ticket_plan.yaml`, and optional
result evidence. The close command recommends a git commit because git is the
durable mechanism for ordering append-only filesystem entries over time.

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

For historical questions, search `specs/.history/**/manifest.json` and
`summary.md` first, then open only the referenced snapshots needed for the
current change.

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
- Do not rewrite append-only spec history entries.
- Do not use TLA+ ceremony for trivial CRUD or early exploratory UI work.
- Do not confuse centralized semantic state with centralized production
  architecture.

## References

- `README.md`: development notes for this skill repository.
- `references/typical_workflow.md`: onboarding, feature-ticket workflow,
  promotion, and closeout.
- `references/generation_modes.md`: manifest-driven generation vs TLC
  state-graph cases.
- `references/runtime_requirements.md`: CLI dependencies, TLC wrapper, and
  local runtime expectations.
- `references/tla_profile.md`: constrained TLA+ subset.
- `references/codegen_contract.md`: manifest schema and generator behavior.
- `references/conformance_testing.md`: production adapter conformance.
- `references/ai_retrieval.md`: AI context selection.
- `references/maintenance.md`: review and regeneration rules.
- `references/examples.md`: checked-in examples and when to use them.
- `references/spec_evolution.md`: append-only history and search guidance.
- `references/workflows.md`: project, spec, ticket, and close-out workflows.
- `examples/workspace/`: fully worked example.
- `examples/subscription/`: partial state-machine example.
