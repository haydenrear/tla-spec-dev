---
name: spec-double-2
description: 'Use when a repository keeps a TLA+ program model under specs/ and a ticket must read, extend, check, or close it through the tla-spec-dev CLI: scaffold a baseline, open or close a spec ticket, run TLC, read the complexity descriptor, render an implementation brief, or attribute a bug to the action it happened inside. Also the home of the organizational standards for evals, bug attribution, and blind dispatch — see the reference map.'
skill-imports:
  - unit: tla-spec-dev
    path: skills/skill-manager/references/cli.md
    reason: Explains how skill-manager exposes declared CLI tools such as tlc2, pytest, and jinja2.
    section: runtime
  - unit: tla-spec-dev
    path: skills/unit-authoring/references/skills.md
    reason: Explains installable skill layout and skill-manager.toml validation.
    section: schema
---

# Spec Double Compiler

Core slogan: **The spec should generate the mock.**

The program model is a small executable meta-model of the program: state,
actions, invariants, and the ports where effects leave. It exists so an agent can
plan a change against a checkable picture of the program, take a descriptor of
where the complexity lives, and name the action a bug happened inside. It is
context and a planning substrate. It is not a test suite you owe the ticket.

## Nothing here blocks

Read this first; it overrides any older wording you find in a reference.

- **No command in this skill should stop you.** Every gate is advisory. If one
  refuses, rerun with `--force` (or `SKILL_GATES=off`), which records the
  override in the receipt, and continue. Never rewrite a ticket's status in the
  plan to get past a refusal.
- **Nothing needs agreeing with the user before you model.** Budgets carry
  documented defaults; change one only when `analyze complexity` warns, and
  note why.
- **A file a template names and your repository lacks is optional.** Do not build
  it. The minimum baseline is four files (below); the rest is the `--full` layer,
  added on purpose and never to satisfy a list.
- **Spend a bounded amount on the spec.** Model the boundary the ticket touches,
  run TLC once, close. If TLC does not finish, do one bounded discovery pass
  (below) and either shrink the model or close with `--force`, saying why. Never
  loop on the model.
- **Read only what the task needs.** The reference map says which page goes with
  which task. The previous 1,400-line version of this file is
  `references/skill_history.md` — open it for history, not before a ticket.

## Orientation

In homes carrying the `skt` plugin, `skt status` runs at session start; its
`spec` line names the active workflow, its open tickets, and whether this
branch's ticket is in the plan. A ticket in the plan opens with `tla-spec-dev
--spec-root specs open ticket <id>`; one not in the plan gets a plan entry under
`specs/desired_program_model/ticket_plan.yaml` first. Do not stop to reconcile.

## The commands

All take `--spec-root specs` (or wherever the repository keeps its specs).

| Command | What it does |
| --- | --- |
| `scaffold project --name X [--full]` | First onboarding: `specs/program_model` with the minimum baseline. `--full` adds the optional layer. |
| `scaffold workflow <ticket> "<title>"` | Creates `specs/current`, `specs/desired_program_model` and `ticket_plan.yaml`. Once per workflow. |
| `open ticket <id>` | Creates `specs/tickets/<id>/desired` as a copy of project current, plus `results/`. `--with-current` for the older two-directory loop. |
| `run spec-unit-tests --ticket <id>` | Runs the generated spec-unit adapters, when the project has the optional layer. |
| `analyze complexity <tla> <cfg>` | The descriptor: per-variable domains, state-space bound, read/write matrix, modularity, dense rows. Advisory. |
| `close ticket <id> [--force]` | Promotes ticket `desired/` into project `current`, writes the append-only history entry, records the ledger. |
| `retire ticket <id>` | Owner-directed withdrawal of a ticket. Promotes nothing. |
| `python scripts/close_tickets.py` | Workflow close: promotes the converged model into `program_model` and removes the workflow directories. |

`scripts/run_tlc.sh <tla> <cfg>` runs TLC from the spec directory with the
`tlc_seconds` budget as an external timeout.

## The minimum baseline

`specs/program_model/` is a baseline when it has `Core.tla` (shared constants and
operators), `Internal.tla` + `Internal.cfg` (the state machine and its finite
model), and `spec_manifest.yaml` (module, ports, invariants, finite model,
budgets) — and TLC passes. That is what the descriptor, brief and bug
attribution read.

Keep it small: one evolving program spec extended per ticket, not one per
feature. Do not model tests, CI jobs, graph nodes or harnesses as state or
actions, and keep databases, queues, retries and timeouts out unless they are the
semantics.

**The optional layer** (`scaffold project --full`) generates cases and runs them
against real adapters through a `test_graph` project. Add it only when the ticket
asks: the machinery is **not validated for catching bugs** (the kill probe caught
0 of 9) — `references/testgraph_adapters.md`, `references/skill_history.md`.
The TLA+ subset is `references/tla_profile.md`.

## The ticket loop

1. `open ticket <id>`. You get `desired/`, a copy of the project's current model.
2. Edit `desired/` so it describes the whole program after this ticket: the new
   or changed state, actions and invariants. Run `scripts/run_tlc.sh` on it once.
3. Implement the ticket in production code.
4. Mark the ticket `done` in `ticket_plan.yaml` and
   `close ticket <id> --summary "<what landed>" --result <evidence>`. The close
   promotes `desired/` into `current`, snapshots into `specs/.history/`, and
   records the complexity ledger. The ledger input is optional; an unfilled or
   rejected one is recorded as rejected and the close proceeds. A close
   printing `WARNING: complexity ledger ... rejected` **has closed the ticket** —
   do not run it again; a rerun refuses to overwrite the entry it just wrote.
5. Before closing, **attribute what the ticket hit**: for each regression or
   defect, name the TLA+ action it happened inside (`<Module>.<Action>`, or
   `UNMODELED/<bin>`), and report it in the PR.
   `references/bug_attribution.md`. Nothing gates on it.

There is no ticket-local `current/` unless you asked for one, so there is no
convergence loop; if you opened with `--with-current` and the two diverge, the
close accepts `desired/` and says so. When project `current` matches
`desired_program_model`, run `scripts/close_tickets.py` to promote into
`program_model`. `specs/.history/` is append-only — never edit an entry.

## TLC and the 120-second budget

Apply a hard 120-second timeout (the `tlc_seconds` default) to every TLC run,
through an external timeout so it holds even when TLC stays responsive. If the
run does not finish, treat the model as too large for case generation.
Do not simply raise the timeout or retry the same diagram. Instead, once,
perform bounded discovery of the state explosion: modeled variables,
constant-domain cardinalities, action branching, interleavings, symmetry, and
the last TLC progress output. Separate accidental complexity that can be
abstracted away from the essential complexity the program requires, and record
which dimensions multiply the state count.

Then shrink by decomposition rather than by narrowing constants: cut along the
read/write matrix into component models with a thin interface model
(`references/architecture_tractability.md`). If a smaller abstraction would drop
behavior that is a material product decision, then in the close summary
record the tradeoff for the user and continue: name the dimensions that cause
the explosion. Provide concrete recommendations with the coverage each one gives
up. Do not wait on an answer.

## The descriptor and the brief

`analyze complexity` reports facts and exits nonzero only when it cannot parse
the model. Budgets in `spec_manifest.yaml` are advisory and
block nothing. The `prompts/` briefs turn one action and one declared partition
into a constrained ask, and are not validated for changing what a coding agent
produces. Reading a descriptor, fitness functions, the briefs:
`references/complexity_intuition.md`, `references/fitness_functions.md`,
`references/hexagonal_prompting.md`.

## Anti-patterns

- Do not stop a ticket because a spec command refused, a template named a file
  you lack, or a budget was not agreed. Force, record, continue.
- Do not treat generated Python as the source of truth or edit generated files
  outside marked extension points.
- Do not let a fake import production services or carry database, network, queue
  or cache logic.
- Do not create disconnected TLA+ specs per feature.
- Do not rewrite append-only history entries.
- Do not use TLA+ ceremony for trivial CRUD or exploratory UI work.
- Do not build a mechanical architecture or coherence check and let it gate
  anything (`references/architecture_advice.md`).
- Do not expect the experimental surface — generated cases, effect conformance,
  the kill test, the coverage audit — to find bugs, or treat a clean report as
  validation.

## Reference map

Open a page when the task in the left column is what you are doing.

| Task | Read |
| --- | --- |
| Writing or reviewing a `.tla` | `references/tla_profile.md`, `templates/tla/annotations.md` |
| Onboarding, ticket commands, promotion, closeout | `references/typical_workflow.md`, `references/workflows.md` |
| Reading a descriptor | `references/complexity_intuition.md`, then `references/architecture_tractability.md` for the moves |
| Adding fitness rules | `references/fitness_functions.md` |
| Rendering a constrained ask for a coding agent | `prompts/implementation_brief.md`, `prompts/hexagonal_implementation.md`, `references/hexagonal_prompting.md` |
| Attributing a defect to an action | `references/bug_attribution.md` |
| Adding the optional layer: External view and Test Graph adapters | `references/testgraph_adapters.md`, `references/edge-cases.md`, `examples/distributed_history/` |
| Writing an effect provider | `references/effect_providers.md`, `examples/effect_providers/` |
| Generated packages, manifest schema, generation modes | `references/codegen_contract.md`, `references/generation_modes.md`, `references/conformance_testing.md` |
| Case modules (optional BDD slices) | `references/case_modules.md`, `prompts/aspect_decomposition.md` |
| Decomposition method, oracles, kill test (experimental) | `references/modular_fuzzing.md`, `references/effectful_onboarding.md`, `references/coverage_audit.md` |
| Migrating an existing repository | `references/migration.md` |
| History entries, retirement, receipts | `references/spec_evolution.md` |
| Runtime, CLI dependencies, which Skill Manager home resolves them | `references/runtime_requirements.md` |
| Preparing context for AI-assisted analysis | `references/ai_retrieval.md` |
| Writing or running an eval against any skill | `references/plugin_evals.md` |
| Reviewing your own work, blind dispatch | `references/blind_dispatch.md` |
| The scorecard rubric and scoring validation | `references/eval_scorecard.md`, `references/scoring_validation.md`, `references/portable_scorecard.md` |
| Everything this skill learned, epic by epic, and what the experimental surface measured | `references/skill_history.md` |
