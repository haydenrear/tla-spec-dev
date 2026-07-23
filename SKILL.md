---
name: spec-double-compiler
description: 'Use when creating or maintaining Python spec doubles generated from a constrained, annotated TLA+ state-machine specification, including manifests, generated fakes, ports, validators, Hypothesis strategies, traces, internal/external Test Graph integration cases, and adapter conformance tests.'
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

## What Is Shipped And What Is Experimental

Read this before trusting any claim below. The workflow has two layers, and they
have very different maturity. Do not conflate them.

**SHIPPED — the complexity descriptor (`analyze complexity`).** This is the
working, validated product. Point it at a spec + cfg and it reports, from the
model alone: a per-variable dimension table with each variable's domain, the
static state-space upper bound and its dominant dimensions (or an **explicit
"unknown"** when no domain can be resolved from a TypeInvariant/TypeOK or the
configured invariants — never a silent 1), the variables x actions read/write
matrix, the graph-modularity score with near-decomposable clusters and
candidate port-crossing actions, dense-row / god-state and dense-column
detection, variables no configured invariant reads (with invariant
aliasing/composition — `INVARIANT Inv`, `Inv == RealInv` — resolved
transitively), and unjustified variables. It is a **descriptor: facts, not
judgment** — it makes no suggestions. (An earlier suggested-move output was
removed after validation showed it confidently wrong on standard TLA+;
suggestions may return later, earned from real-app observations.) It is
**advisory**: it names *what* is dense and *where*, and **never blocks
promotion, never refuses case generation, and never changes its exit code**
because a model is complex (it exits nonzero only when it genuinely cannot
parse the model). A reader should expect it to show where the complexity
lives; deciding what to do about it is the owner's design work. The working
framing is: **take this complexity descriptor to consider how to refactor
complexity out of the app** — the descriptor is refactoring *input* the agent
reads and judges, never automated moves. How to read a descriptor — what good
and bad shapes look like, with worked examples — is
`references/complexity_intuition.md`; the advisory stance is in "Complexity
Budgets Are Advisory" below and in
`references/architecture_tractability.md`, "Advisory, Not Blocking". The
descriptor also evaluates the project's **self-configured fitness functions**
(experimental, CD-03): composable and/or/not rules over the descriptor's
facts that the project's agent writes and that persist with the project; any
rule that does not hold on a scan FIRES as a notification to future agents —
advisory, never blocking, and there are no built-in rules. See
`references/fitness_functions.md`.

**SHIPPED — the agent-authored effect-provider interface.** The framework
generates repository-specific typed ports, resolves one project provider per
declared port, scopes it around one generated case/iteration, supplies stable
seeds, and emits exact replay evidence. The repository agent supplies every
effect implementation. The framework does not ship domain providers. Read
`references/effect_providers.md` before implementing or reviewing one.

**EXPERIMENTAL — the modular-fuzzing machinery (oracles, corpus, mutation kill
test).** The differential-fuzzing framing (TLA+ as oracle, generated cases,
effect conformance, the mutation kill test as a value floor) is real
infrastructure and is retained as the honest record of what was built and learned.
It is **not validated for catching bugs.** The MF-038 kill probe measured exactly
that: with a green control run, generated cases caught **0 of 9 subtle
content/value/field/count bugs — kill rate 4/13 = 0.31** — because the oracles read
file *existence and process exit codes*, not file *content*. Separately, the design
is two-armed (TLC exhaustive + Hypothesis random) but **only the exhaustive arm
exists; the Hypothesis randomized-generation arm is a stub, not implemented.** So:
do NOT expect the fuzzing to find bugs. Use it as a research surface and a
representation-modelling aid, not as a bug detector. Every section below that
describes oracles, effect conformance, corpus discipline, or the kill test is
describing this experimental layer and is labeled accordingly.

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

## Modular Representation Rule

Represent the program as components, each described as a pure function plus
declared side effects:

- Local state owned by the component alone.
- A pure transition `(state, input) -> (state', output, effects)`.
- Declared effects on named ports — the only way anything leaves the
  component. One component's effects are another component's inputs, or
  externally observable behavior.

The **decomposition method** below — modeling components as pure transitions
plus declared port effects, and cutting along the read/write matrix — is sound
guidance that the shipped scanner directly supports: the R/W matrix and
modularity score are exactly what tell you where a component boundary is.

The **differential-fuzzing framing around it is EXPERIMENTAL** (see "What Is
Shipped And What Is Experimental"). It casts TLC and Hypothesis as input
generators, the spec double as reference, adapters as harness, and invariants
plus projected-state and effect conformance as sanitizers, and it proposes to
judge a representation "by the seeded bugs it kills." That value system is **not
validated**: the MF-038 kill probe caught 0 of 9 content bugs (kill rate 0.31),
and the Hypothesis arm is a stub. Do not rely on it to catch bugs, and do not
treat a passing kill test as proof a baseline is validated.

Read `references/modular_fuzzing.md` before authoring or reviewing any baseline.
It defines the decomposition method (read/write matrix, port cuts, contract
environments, interface model) — useful and shipped — and, clearly marked
experimental, the per-program budgets, the four oracles including effect
conformance and the mutation kill test, and the strict External content rule.
Read `references/effect_providers.md` before implementing a project-owned
effect provider or running a deterministic representative campaign. It defines
the single `EffectProvider.bind(context)` interface, the TLA
semantic-outcome/provider-representation boundary, provider lifecycle, usage
descriptor, seed and exact-replay protocol, and current isolation limits.
Implement the generated port in repository code; do not look for or add a
framework-owned domain adapter. A provider must be an object whose `bind`
returns a standard context manager. Record its binding style, state scope, fuzz
dimensions, assertions, cleanup, and bypass limits in
`effect_provider_usage.yaml`. The provider decides which deterministic
representatives to enumerate from `context.derived_seed`; the harness schedules
and replays them. Implement every entered binding method with the exact
generated parameter shape and parameter/return annotations; runtime preflight
rejects method-name-only lookalikes before adapter setup. Keep manifests within
the dependency-invariant constrained YAML profile (indented mappings, plus
single-line inline mappings with scalar values — the fitness-rule leaf syntax
— and no nesting inside them), and run recorded replay commands without replacing their
originating virtualenv interpreter.
For moving an existing repository onto this shape, read `references/migration.md`.

## Onboarding to effectful fuzzing + complexity minimization

Once the spec workflow is green, the composed path — measure complexity with
the descriptor, judge it with `references/complexity_intuition.md`, take any
validated refactor the judgment earns, lock the shape in with fitness
functions, then declare effect ports and implement agent-authored providers
for deterministic content-asserting fuzz campaigns — is a single ordered
walk. Read `references/effectful_onboarding.md` and follow its stages in
order: complexity minimization comes FIRST (a provider written against
god-state actions duplicates every coupled rule, and representation-heavy
state multiplies per-point campaign cost for nothing), effects second,
one boundary at a time. Existing onboarded repositories migrate additively —
with no `role: effect` port and no `[effect_providers.*]` table configured,
every legacy path is preserved exactly.

## Internal/External Test Graph Views

**Every project uses one semantic authority with two generated views. This is
not conditional on the project looking "integration-heavy."**

- Internal view: fine-grained program/component behavior for spec-unit
  adapters.
- External view: public or harness-driven behavior for Test Graph adapters.

Test Graph adapters are foundational to every project. A model with only an
internal view generates no Test Graph cases, so the repository's public surface
is never validated — which is the entire point of the workflow. There is no such
thing as a project too small, too local, or too single-process for an External
view.

External does not mean distributed. It means the behavior a test harness can
drive or observe outside the modeled internals: HTTP calls, CLI commands,
browser actions, filesystem changes, queue operations, admin/debug endpoints,
or Kubernetes fault injection. A CLI project can use External to generate
command invocations and assertions without running a cluster. A library whose
public surface is observable filesystem behavior — paths, envelopes, sidecars —
has an External view that *is* the library, not an add-on to it.

The External content rule is strict: External contains exactly the public
input surface and the externally observable projection of composed state,
nothing component-level. An External adapter drives the program as deployed —
separate process or real deployment, through a declared channel, observing
only externally visible state. An adapter that imports the production package
in-process is a spec-unit adapter wearing an External badge; rebind it as
Internal or fix it. See `references/modular_fuzzing.md` for the port binding
ladder that connects the two views.

**MF-015: that rule is now verified, not merely asserted.** Both the runner and
the exporter refuse to proceed unless every external binding declares a
`channel` (http/cli/fs/queue/k8s), no adapter/projector/expected_projection/
assertion module imports the declared `external.production_package` — checked
by static import analysis, transitively, so laundering it through a helper does
not evade the check — and `external.port_bindings` names each port `double` or
`real` with at least one `real`, since an all-doubles configuration exercises
nothing real and is a spec-unit run rather than a Test Graph node. Violations
report the adapter, the offending import, and the remediation. There is no
override flag, and an absent declaration fails rather than skipping the check.

Read `references/testgraph_adapters.md` **before authoring any spec baseline**,
not later when wiring the graph. Onboarding is when the Internal/External split
gets decided; by the time you are "wiring the graph" the decision is already
made. When selecting edge cases and negative public behaviors for External, read
`references/edge-cases.md`. The worked example in
`examples/distributed_history/` shows an External model that records public
service routes and bounded input data, then lets TLC expand those declarations
into hundreds of Test Graph cases executed against k3d.

Graph nodes are end-to-end External-view executions only. TLC runs and spec-unit
runs are direct `tla-spec-dev` commands, never Test Graph nodes.

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

Before authoring any baseline, read `references/testgraph_adapters.md` and
`references/edge-cases.md`, and list `examples/distributed_history/specs/program_model/`.
Onboarding is exactly when the Internal/External split gets decided; it is not a
later concern. Deferring those references is how a baseline ends up as a single
module that can never be validated.

To onboard an existing repository for the first time, use:

```bash
tla-spec-dev --spec-root specs scaffold project --name ProjectName
```

Use `--name SkillManager` or another explicit module name when the repository
directory name is not the desired TLA+ module name. Use the same `--spec-root`
on every `tla-spec-dev` command when the repository keeps specs somewhere other
than `specs`.

### The baseline is not complete until it has all of these

The scaffold emits placeholder files to restructure. It is not the answer, and a
filled-in single module is not a baseline. `specs/program_model/` is done only
when it has:

- [ ] `Core.tla` — shared constants and operators.
- [ ] `Internal.tla` + `Internal.cfg` — internal view. Generates spec-unit cases.
- [ ] `External.tla` + `External.cfg` — external view. Generates Test Graph cases.
- [ ] `actions.yml` — per-action layer, controllability, and what it generates.
- [ ] `adapters.py` — spec-unit adapters AND Test Graph adapters, projector,
      expected projection, and projected-state assertion.
- [ ] `providers.py` — agent-authored implementations of generated effect
      ports using the single `EffectProvider.bind(context)` interface.
- [ ] `effect_provider_usage.yaml` — reviewable provider state scope, fuzz
      dimensions, assertions, cleanup, and known bypass limits.
- [ ] `case_adapters.toml` — internal action -> spec-unit adapter.
- [ ] `testgraph_bindings.yml` — external action -> Test Graph adapter.
- [ ] `tlc_projection.py` — TLC state -> generated-case shapes.
- [ ] `spec_manifest.yaml` — ports, invariants, finite model, onboarding status.
- [ ] TLC passes on **both** cfgs.
- [ ] A `test_graph` project exists in the repository.

**Test Graph adapters are foundational to every project.** They are not an
add-on for distributed systems. Without `External.tla` and its adapters, the
repository's public surface is never validated and the workflow delivers
nothing. If the library's public surface is observable filesystem behavior, then
the External view *is* the library.

Before calling onboarding done, diff your tree against
`examples/distributed_history/specs/program_model/`. That 30-second structural
diff catches every omission this checklist exists to prevent.

The External view, the bindings, and the skeleton adapters are **onboarding
deliverables**. Tickets own per-slice adapter *implementations*, not the
structure itself. Do not defer the structure to a ticket.

If a template, ticket, or issue names files your repository does not have (for
example `Internal.tla` / `External.tla`), that is a **stop-and-reconcile
checkpoint**, not a copyediting task. Ask why the template expects files you did
not create instead of rewording the template to fit a thinner model.

After `specs/program_model` exists, later behavior tickets may use
`tla-spec-dev --spec-root specs scaffold workflow` to create `specs/current`
and `specs/desired_program_model` from that accepted baseline.

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
- `specs/tickets/<ticket-id>`: one active ticket workspace with its own
  `current/`, `desired/`, `results/`, and copied Test Graph configuration when
  present. The ticket `desired/` is the whole-program state after that ticket,
  not the whole project destination.

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
3. Start each implementation ticket from the plan with
   `tla-spec-dev --spec-root specs open ticket <ticket-id>`. This copies project
   `current/` into `specs/tickets/<ticket-id>/current` and `desired`, plus
   ticket-local results and Test Graph assets.
4. Edit the ticket-local `desired/` first. It should describe the
   whole-program ending state after that ticket, including TLA+, configs,
   spec-unit adapters/tests, and Test Graph bindings/adapters when applicable.
5. Implement the ticket in production code, then update ticket-local `current/`
   to the behavior that actually landed.
6. Run TLC, generated/adapted case tests, and relevant Test Graph runs from the
   ticket directory. Keep evidence under the ticket `results/` directory or pass
   it to close commands. Use
   `tla-spec-dev --spec-root specs run spec-unit-tests --ticket <ticket-id>` for
   spec-unit validation through the shipped CLI.
7. Keep `specs/desired_program_model` updated as the plan changes. If a ticket
   splits, merges, changes order, gains a dependency, or changes acceptance
   criteria, record that there instead of leaving the plan in chat or ad hoc
   notes.
8. When ticket-local `current/` semantically equals ticket-local `desired/`,
   mark the ticket closed in the global `ticket_plan.yaml` and run
   `tla-spec-dev --spec-root specs close ticket <ticket-id>`. The close moves
   the ticket directory into history, replaces project `specs/current` with
   ticket `desired/`, and merges ticket-local Test Graph artifacts into project
   specs.
9. Repeat until `specs/current` semantically equals
   `specs/desired_program_model`.
10. Promote the converged model into `specs/program_model`, regenerate accepted
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
tla-spec-dev --spec-root specs scaffold workflow TICKET-123 "Ticket title"
```

The scaffold resolves all workflow directories under `--spec-root`, which
defaults to `specs`. It copies the existing `program_model` baseline into
`current` and `desired_program_model` where useful, then adds ticket workflow
metadata, `ticket_plan.yaml`, and `status` sections to the workflow manifests.
The generated comments are intentionally instructional; replace them with the
project's actual state, actions, adapter boundaries, tests, and evidence as the
ticket is refined. Do not use this for first project onboarding.

To start work on a planned ticket, scaffold its ticket-local workspace:

```bash
tla-spec-dev --spec-root specs open ticket TICKET-123
```

This creates `specs/tickets/TICKET-123/current`, `desired`, `results`, and
copied Test Graph configuration when present. Update `desired/` first to the
ticket ending state, then update `current/` as implementation lands. Work there
until local `current == desired`, then close the ticket:

```bash
tla-spec-dev --spec-root specs close ticket TICKET-123
```

The close command validates ticket-local `current == desired`, replaces
project-level `specs/current` with ticket `desired/`, merges ticket-local Test
Graph artifacts into project specs, and moves `specs/tickets/TICKET-123` into
history.

Prepare for promotion before closing. The close promotes the ticket `desired/`
into `specs/current`, so ticket `current/` must first semantically match
`desired/` (comparing `.tla`, `.cfg`, `.yaml`/`.yml`, `.py`, `.toml`, `.json`
files; planning files and `status`/`notes`/`promotion` metadata are ignored —
they need to be semantically equal, not byte-identical). Either edit `current/`
until it matches `desired/` and re-run the spec-unit validations, or accept the
ticket `desired/` as the new `current/` directly:

```bash
tla-spec-dev --spec-root specs close ticket TICKET-123 --accept-new
```

`--accept-new` overwrites ticket `current/` from `desired/` and skips the
`current == desired` check, so the ticket's proposed desired state is promoted
as-is. `scripts/close_tickets.py` accepts the same `--accept-new` flag to adopt
`specs/desired_program_model` as the new `specs/current` and
`specs/program_model` during whole-workflow closeout.

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

## Complexity Budgets Are Advisory

The standing objective of this workflow is **reducing program complexity while
retaining every behavior**. The shipped complexity scanner provides the metric;
design becomes the place you spend it — look for complexity reductions on every
ticket, not only when the scanner warns. Whenever a descriptor is produced,
take it to consider how to refactor complexity out of the app: read it with
`references/complexity_intuition.md` (what good and bad descriptor shapes look
like, how complex a program should be, and the reading order for deciding
whether/how to refactor — intuitions the agent judges with, not automated
moves). A **validated** refactor that lowers complexity — model green under
TLC and tests, behavior preserved, before/after descriptors compared — is
encouraged as normal practice, not an exceptional event. Never game the metric
by under-representing the program: a complexity drop is only evidence when
reported jointly with behavior-retention evidence. See "The Standing
Objective" in `references/architecture_tractability.md`.

**Budgets are advisory thresholds, not gates.** They are per-program and set with
the user during scaffolding: propose the defaults in
`references/modular_fuzzing.md`, ask which to adjust for this program, and record
the agreed values with a one-line rationale under `budgets:` in
`spec_manifest.yaml`. Budgets cover TLC wall time, distinct states per component
model, case caps per view, component-size heuristics, and — in the experimental
layer — the mutation kill-rate floor. The experimental fuzzing-era keys
(`kill_rate_floor`, `max_symmetric_instances`) are optional: a manifest that
omits them scans with no missing-keys warning, and the kill test falls back to
the documented default floor when invoked. When the scanner finds a model over one of
these thresholds it emits a **warning that names the component/variable/action
and states the measured fact**. It does **not** recommend a move, block
promotion, refuse case generation, or change its exit code. Complexity is a
scanner, not a gate (`references/architecture_tractability.md`, "Advisory, Not
Blocking"). The owner decides, with the user, whether to act on each warning.

**How to read a warning.** A warning is a pointer, not a verdict. "Component C1 is
touched by 14 actions, exceeding max_component_actions 8" means the scanner found a
dense cluster and is showing you *where* the coupling is — it is evidence for the
owner, not a refusal and not advice. Some components score badly
and still need to exist in that form (performance paths, protocol-mandated shapes,
irreducible domain complexity); the scanner says so in its own output. The
`tlc_seconds` timeout below is the one hard operational limit, and it is about wall
time, not complexity.

**Fitness functions (experimental, CD-03).** When you have read a project's
descriptor and settled the shape it should keep, **add fitness functions for
this complexity descriptor so future agents are notified** if a later change
breaks that shape: one or two composed and/or/not rules over the descriptor's
facts (`bound < X`, `god_state_count == 0`, `modularity >= Q`,
`variable_domain(v) <= D`, ...), written under `fitness_functions:` in
`spec_manifest.yaml` or in a `fitness_functions.yaml` next to the spec, so
they persist with the project. Every later `analyze complexity` run evaluates
them and surfaces any rule that does not hold as a FIRED notification. Same
advisory stance as everything above: firings report, never block, never change
the exit code — and the tool ships with no built-in rules; only the project's
agent configures them. Schema, facts catalog, and semantics:
`references/fitness_functions.md`.

Apply a hard 120-second timeout (the `tlc_seconds` default) to every TLC
model-check or diagram run that generates cases from a reachable state graph.
Never let an agent wait longer in the hope that state-space exploration will
finish. Use an external timeout around the TLC command so this limit still
applies when TLC itself remains responsive.

If the run does not finish within two minutes, treat the model as too large for
case generation. Do not simply raise the timeout or retry the same diagram.
Before changing the model, perform bounded discovery of the state explosion:
inspect the modeled variables, constant-domain cardinalities, action branching,
interleavings, symmetry, and the last available TLC progress output. Separate
accidental complexity that can be abstracted away from essential complexity
that the program actually requires, and identify which dimensions multiply the
state count. Record these findings instead of reporting only that TLC timed out.

Then introduce another diagram or refinement abstraction with a smaller state
space while preserving the behavior and invariants needed by the ticket. The
rigorous method is decomposition, not domain-shrinking: build the variables x
actions read/write matrix, cut along minimum-interaction edges into component
models with contract environments at the ports, and keep a thin interface
model — see `references/modular_fuzzing.md`. Narrowing constants alone is the
last resort. (The experimental mutation kill-rate floor was intended to catch
models shrunk past usefulness; because it is not validated for bug-catching, do
not rely on it to police shrinking — use human review of the R/W matrix and the
retained behavior instead.)

Tractability is an architectural fitness function: a scanner warning is a
review finding about the program, not a tooling inconvenience. When neither
abstraction nor decomposition works, the program itself may need refactoring
— but that diagnosis is a **recommendation the user approves, adjusts, or
vetoes**, never a decision the agent takes alone. Some pieces score poorly
and still need to exist in that form; those get creative representations
instead. Read `references/architecture_tractability.md` for the three moves,
their diagnostics, and the grow-the-model-by-evidence loop.

If a smaller abstraction would omit behavior whose inclusion is a material
product or correctness decision, stop and discuss the tradeoff with the user.
Explain which dimensions cause the state explosion and ask how to reduce the
program's modeled complexity. Provide concrete recommendations, including the
expected coverage tradeoff and which program or model dimensions each option
removes. A case-generating diagram is acceptable only when it completes within
120 seconds; record the bounded command, discovery findings, recommendation,
and result as validation evidence.

## Standard Workflow

0. For first onboarding of a repository with no accepted model, create
   `specs/program_model` with
   `tla-spec-dev --spec-root specs scaffold project --name ProjectName`. The
   scaffold emits placeholders to restructure, not a finished baseline: complete
   **both** the Internal and External views plus **both** adapter mappings before
   moving on. See the completeness checklist in "First Project Onboarding
   Workflow" — onboarding is not done until TLC passes on both cfgs and a
   `test_graph` project exists. Do not create `specs/current`,
   `specs/desired_program_model`, or `ticket_plan.yaml` during first onboarding.
1. For later behavior changes, create or refresh `specs/desired_program_model` with
   both the target model and the implementation plan: ticket breakdown, steps,
   dependencies, status metadata, acceptance criteria, and validation commands.
   Use `tla-spec-dev --spec-root specs scaffold workflow TICKET-123 "Ticket title"`
   when the repository does not have this ticket workflow structure yet but
   already has `specs/program_model`.
2. Ensure `specs/current` starts from the entire accepted
   `specs/program_model`, not only the behavior being changed.
3. For each ticket, run `tla-spec-dev --spec-root specs open ticket <ticket-id>`
   to create `specs/tickets/<ticket-id>/current` and `desired`.
4. Update ticket-local `desired/` first so it shows the whole-program ending
   state after the ticket, including spec adapters/tests and Test Graph assets
   when applicable.
5. Update production code and ticket-local `current/` until the local ticket
   model reaches its desired end state.
6. Run TLC against the ticket current finite model config.
7. Review invariants and counterexamples.
8. Update `spec_manifest.yaml` or adjacent status files if commands, state
   fields, results, ports, generators, invariants, adapters, or plan metadata
   changed.
9. Regenerate Python artifacts for the ticket current or desired model.
10. Review generated diffs plus the `program_model` -> project `current` ->
   ticket `current` -> ticket `desired` -> project `desired_program_model`
   relationship.
   The diff should show semantic program changes, not integration-test
   scaffolding modeled as state-machine behavior.
11. Run spec-double self-tests.
12. Run adapter conformance tests and relevant Test Graph validation.
13. Mark the ticket closed and run
    `tla-spec-dev --spec-root specs close ticket <ticket-id>` to move the ticket
    directory to history, replace project current with ticket desired, and merge
    ticket-local Test Graph artifacts into project specs.
14. Continue until `specs/current` equals `specs/desired_program_model`, then
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

- `specs/cases` or `examples/<name>/cases`: generated TLC edge cases.
- `specs/generated` or `examples/<name>/generated`: generated Python
  packages.
- `specs/results`: TLC, adapter, and test evidence.
- `specs/.history/<workflow-name>`: append-only workflow history.

For Test Graph integration examples, prefer regenerating TLC-derived case
packages into the graph build or report directory when they are only runtime
IR for adapters. The semantic source of truth should remain the TLA+ model,
action metadata, adapter bindings, and report manifest, not checked-in
`cases.py` files.

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
2. Start the ticket workspace with
   `tla-spec-dev --spec-root specs open ticket <ticket-id>`.
3. Update the ticket-local desired model first with the whole-program state
   that should be true after the ticket.
4. Update the ticket-local current model to include the whole program as
   currently implemented for that ticket, preserving baseline behavior from the
   project current unless production behavior changed.
5. Add or update ticket-local adapters and unit tests first. These tests should
   validate the control surface, rendering, or refinement mapping without
   requiring the full integration graph unless that is the slice under test.
6. Run TLC and the ticket current adapter/unit tests.
7. Add the behavior to the test graph with explicit external assertions. Do
   not rely only on a wrapper exit code when Helm, Kubernetes, databases,
   queues, files, or services are the actual boundary. Assert with the real
   external tool (`kubectl`, `helm`, SQL, Kafka admin, filesystem inspection,
   HTTP, etc.) and publish useful endpoint/context data for downstream nodes.
8. Run the narrow graph for the slice.
9. Mark the ticket closed in `specs/desired_program_model/ticket_plan.yaml`,
   record run ids and evidence paths, then close the ticket with
   `tla-spec-dev --spec-root specs close ticket <ticket-id> --result <evidence-path>`.
10. Sync the desired model metadata to mark the refined boundary as done.
11. Commit the ticket close record, spec changes, and evidence together.

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

Per-ticket start and close:

```bash
tla-spec-dev --spec-root specs open ticket TICKET-123
tla-spec-dev --spec-root specs close ticket TICKET-123 --summary "Recorded ticket-level history" --result specs/results/adapter.txt
```

Whole-workflow close:

```bash
python scripts/close_tickets.py --repo-root . --summary "Promoted desired/current into program_model"
```

Each entry includes a machine-readable `manifest.json`, a human-readable
`summary.md`, snapshots of `program_model`, `desired_program_model`, and
project `current` when present, the moved ticket work directory, the ticket
mapping from `ticket_plan.yaml`, and optional result evidence. The close command
recommends a git commit because git is the durable mechanism for ordering
append-only filesystem entries over time.

The repository-level Test Graph contains `specWorkflow`, an end-to-end
integration check for this lifecycle. It creates a disposable git repository in
the graph build directory, runs the real `tla-spec-dev` scaffold/open/run/close
commands, verifies promotion and history movement, and removes the temporary
repo:

```bash
/Users/hayde/.skill-manager/skills/test-graph/scripts/discover.py specWorkflow
/Users/hayde/.skill-manager/skills/test-graph/scripts/run.py specWorkflow
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
3. Effect conformance **(EXPERIMENTAL — not validated for bug-catching)**: the
   real component, run in a sandbox, produces only declared side effects.
   Undeclared observed effects are representation gaps; declared-but-never-observed
   effects are dead model surface. See `references/modular_fuzzing.md`. This and
   layer 4 are the experimental fuzzing machinery; the MF-038 kill probe caught 0
   of 9 content bugs (kill rate 0.31) because these oracles observe effect
   *existence and shape*, not the *content* a bug corrupts. Run them to model and
   study a program's boundaries, not to certify it bug-free.

   **Observable scope — read this before onboarding a non-Python project.**
   The effect sandbox observes the **in-process CPython runtime only**. It
   works by monkeypatching `builtins.open`, the `os`/`shutil`/`pathlib`
   mutators, `subprocess`, and `socket.connect` inside the interpreter running
   the harness. **No patch crosses a process boundary.** Therefore:

   - A **Java or Kotlin adapter in a separate JVM is not observed.**
   - **Exported Test Graph cases are not observed** — they run in JBang/uv
     nodes in their own processes, and receive no effect checking at all.
   - A **spawned subprocess is not observed**; only the spawn itself is.

   The oracle **refuses** rather than reporting clean in each of these cases:
   the verdict is `unobservable` and the run **fails**, naming the target and
   why. This is deliberate — a clean report on something the sandbox could not
   see would be indistinguishable from a real one. Observability is granted
   only when an adapter is resolved to a live Python object and called
   in-process; an unrecognised runtime refuses rather than defaulting to
   observable.

   No flag, annotation, manifest entry, or environment variable downgrades an
   `unobservable` verdict to a pass. If your target is not in-process Python,
   this oracle does not cover it, and you must check that boundary another
   way. JVM-capable observation is tracked in
   [issue #44](https://github.com/haydenrear/tla-spec-dev/issues/44).
4. Mutation kill tests **(EXPERIMENTAL — not validated for bug-catching)**:
   seeded production faults — at minimum one per port and one per invariant — are
   run against the generated cases and a kill rate is reported against the
   `kill_rate_floor` from the budgets. **This was intended to be the value floor
   that certifies a baseline, and it does not work for that yet.** The MF-038
   probe ran it on this repository with a green control and measured kill rate
   4/13 = 0.31, with all 9 subtle content/value/field/count bugs surviving,
   because the oracles read existence and exit codes, not content. So a passing
   kill test does **not** mean a baseline catches bugs. The `run kill-test` command
   still exits nonzero below the floor as built, but this does not gate promotion —
   `close ticket` and `run spec-unit-tests` do not invoke it. Treat the number as a
   research signal about where the representation is coarse, not as validation. (The design is two-armed — TLC
   exhaustive plus Hypothesis random — but only the exhaustive arm exists; the
   Hypothesis arm is a stub.)

   Run it with `tla-spec-dev run kill-test --corpus-command "<corpus>"`, and
   declare the faults in `<spec-dir>/kill_mutants.toml`. The required boundary
   set is re-derived from the port declarations and the model configs on every
   run, so an uncovered boundary refuses (exit 2) and computes no rate — adding
   a port breaks the kill test until you seed a fault for it. The corpus is run
   unmutated first as a control, because a corpus that already fails would kill
   every mutant and report a meaningless 1.0.

   As built, the command has no `--allow-below-floor`, no `--accept-survivors`,
   and no expected-to-survive annotation; suppression-shaped keys are reported and
   never honored. That anti-suppression discipline is worth keeping as evidence
   integrity. The command still exits nonzero below the floor, but per doctrine the
   floor **does not gate promotion** — it advises. MF-038 showed it does not yet
   measure bug-catching (0 of 9 content bugs killed), so it cannot be the "value
   floor that keeps every cost cap honest" it was designed to be; until real-app
   validation earns it that role (MF-037), read it as a diagnostic, not a
   certification.

   A surviving mutant names the model variable and action to refine — treat it
   as a pointer to the place the representation is too abstract, not as a score.
   Use `--baseline`/`--compare` to validate an abstraction: a revision that
   kills fewer mutants deleted behavior rather than re-representing it.
5. Regression tests from counterexamples: TLC counterexamples,
   Hypothesis failures, and production bugs become named Python traces,
   TLA+ model changes, or validator improvements.
6. **Coverage audit — completeness, not fidelity. Required once per epic.**

   Layers 1-4 are all bounded to what is **already modeled**: conformance
   checks cases that exist, effect conformance checks a corpus generated *from
   the model*, and the kill test seeds faults one per port and one per
   invariant — modeled boundaries only. Unmodeled program surface is never
   generated into a case, never adapted, never mutated. **A subsystem with no
   representation is invisible to every layer above while all of them report
   green.** Fidelity and completeness are independent properties.

   **Ordering — a required end-of-epic step: after every mechanism ticket has
   landed, and before final end-to-end integration.** After the mechanisms, so
   it measures the model as the epic actually leaves it; before integration,
   because it is a promotion gate rather than a report.

   Dispatch `prompts/coverage_audit.md` to a sub-agent; it fills
   `templates/coverage_audit_report.md`. Four sweeps — program surface, effects
   **by category**, behaviors (error paths, retries, timeouts, fallbacks,
   concurrency, config branches), and Internal/External **reported separately**
   — each a table whose row set comes from a recorded enumeration command, with
   per-row verdicts and `file:line` evidence.

   **In-scope gaps are HARD**: model it, or change the program. No third
   option, and the prompt offers no "justified"/"accept as-is" disposition for
   one. Out-of-scope surface is inventoried and does not gate. **The scope is
   read from the plan, declared once and reviewed once — never waived per
   finding**; N per-finding justifications would be the escape hatch that one
   reviewable boundary decision is not.

   The verdict is recorded in the complexity ledger's `coverage_audit` block so
   an epic that skipped the audit is visible. It defaults to `not_run` and
   refuses the workflow close at anything but `pass`; `incomplete` is not a
   pass. See `references/coverage_audit.md`.

When example or repository tests need pytest but the project does not have a
managed Python environment, make the test file directly runnable with a PEP 723
uv header and a `pytest.main([__file__])` entry point. Document
`uv run path/to/test_file.py` so agents do not depend on ambient pytest.

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
- `references/testgraph_adapters.md`: internal/external Test Graph adapter
  onboarding, hook order, projected-state assertions, and example commands.
- `references/modular_fuzzing.md`: modular pure-function/side-effect
  representations, decomposition method, budgets, oracles, corpus
  discipline, and the External content rule.
- `references/effectful_onboarding.md`: the ordered onboarding/migration walk
  onto effectful fuzzing + complexity minimization — descriptor first,
  fitness lock-in, then effect ports, providers, and deterministic campaigns.
- `references/effect_providers.md`: project-owned provider interfaces,
  the domain-neutral agent contract, deterministic representative campaigns,
  exact replay, usage evidence, and honest isolation/validation limits.
- `references/coverage_audit.md`: the end-of-epic completeness gate — why
  the four oracles cannot see unmodeled surface, the required ordering
  (after mechanisms land, before final integration), and the gate semantics.
  Procedure: `prompts/coverage_audit.md`; report shape:
  `templates/coverage_audit_report.md`.
- `references/architecture_tractability.md`: the owner's three design moves
  when the descriptor shows a squeeze (the descriptor itself suggests
  nothing), user-approval rules, creative representations for irreducible
  pieces, and the grow-by-evidence modeling loop.
- `references/complexity_intuition.md`: how to read a complexity descriptor
  as refactoring input — good vs bad descriptor shapes with worked real-run
  examples, how complex a program should be (proportional to essential
  behavior), the validated-refactor practice, and the reading order for
  deciding whether/how to refactor. Intuitions to judge with, never
  automated suggestions.
- `references/fitness_functions.md`: self-configured, composable fitness
  functions over the complexity descriptor (experimental, CD-03) — rule
  schema, facts catalog, per-project persistence, and the advisory
  fired-rule notification.
- `references/migration.md`: migrating an existing repository onto modular
  representations, invited source refactors, and the skill feedback loop.
- `references/edge-cases.md`: how to choose generated integration edge cases
  for External views without assuming a distributed deployment.
- `references/ai_retrieval.md`: AI context selection.
- `references/maintenance.md`: review and regeneration rules.
- `references/examples.md`: checked-in examples and when to use them.
- `references/spec_evolution.md`: append-only history and search guidance.
- `references/workflows.md`: project, spec, ticket, and close-out workflows.
- `examples/distributed_history/`: fully worked internal/external Test Graph
  example with local and k3d modes.
