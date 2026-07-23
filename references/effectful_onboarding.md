# Onboarding and migrating to effectful fuzzing + complexity minimization

This is the path an agent walks to take a repository from "has a spec
workflow" to "measures its complexity, locks the measurements in, and fuzzes
its real effect boundaries with content-level oracles." It composes the two
shipped surfaces — the **complexity descriptor + intuition + fitness
functions** (complexity minimization) and the **agent-authored effect-provider
interface** (effectful fuzzing) — in the order that makes each step's
evidence feed the next.

Prerequisite: the repository is onboarded to the spec workflow (SKILL.md
"Onboarding") — Internal/External views, TLC green, adapters mapped. If not,
do that first; nothing below substitutes for it.

## Why this order

Complexity work comes FIRST. The effect-provider runtime schedules one full
lifecycle per case × iteration; a model whose state space is representation
rather than behavior multiplies that cost for nothing, and providers written
against god-state actions duplicate every coupled rule. Minimize first,
lock it in, then make the effects real.

## Stage 1 — Measure: the complexity descriptor

```bash
python3 scripts/tla_spec_dev.py --spec-root specs analyze complexity \
  specs/program_model/External.tla specs/program_model/External.cfg \
  --manifest specs/program_model/spec_manifest.yaml
```

Read the output with `references/complexity_intuition.md`: take this
complexity descriptor to consider how to refactor complexity out of the app.
Judge proportionality (bound vs the distinctions behavior actually makes),
apply the write-only-state test to stamped variables, read the R/W matrix
(columns are the real next-state disjuncts), and treat every warning as
advisory. How complex should the program be? Proportional to its essential
behavior — and a **validated architectural refactor that lowers complexity is
encouraged as normal practice**: validated means TLC green before and after,
behavior tests untouched (or changes justified line by line), before/after
descriptors compared, and the transition-level diff inspected for the
red-flag pattern.

## Stage 2 — Lock it in: fitness functions

Write composable advisory rules over the descriptor facts you just judged, so
future agents are notified when the shape regresses
(`references/fitness_functions.md`):

```yaml
fitness_functions:
  - name: bound-stays-behavioral
    rule:
      all:
        - {fact: bound_known, op: ==, value: true}
        - {fact: bound, op: "<=", value: 10000}
  - name: no-new-bookkeeping-state
    rule:
      all:
        - {fact: unread_by_invariant_count, op: "<=", value: 1}
        - {fact: unjustified_count, op: ==, value: 0}
```

The manifest block is dependency-invariant (works with or without PyYAML);
`fitness_functions.json` is the sibling-file alternative. Rules report, never
block. There are no built-in rules — you configure what this project's shape
means.

## Stage 3 — Declare the effect surface

For each real boundary the program crosses (filesystem, HTTP, queue, clock…),
declare the repository's own semantic abstraction in `spec_manifest.yaml` and
name each action's complete effect requirements in `actions.yml` — an
explicit empty list for effect-free actions (`references/effect_providers.md`,
"Declare the semantic port"):

```yaml
# spec_manifest.yaml
ports:
  TaskStorePort:
    role: effect
    methods:
      persist:
        command: PersistTasks
        result: str
# actions.yml
actions:
  AddTask:
    effect_ports: [TaskStorePort]
  ListTasks:
    effect_ports: []
```

Model **response classes, not implementation scripts**: a distinction goes
into TLA+ only when it changes allowed output, state, cardinality, ordering,
or retry behavior. Interchangeable concrete representations belong in the
provider. Regenerate cases so the typed port Protocols exist.

## Stage 4 — Implement the provider

One interface: an object whose `bind(context)` returns a standard context
manager yielding either an implementation of the generated Protocol or `None`
(self-installed bounded integration). The framework preflights signatures
against the generated Protocol — names, kinds, annotations — before any
adapter runs. Wire it and record its contract:

```toml
# case_adapters.toml
[effect_providers.TaskStorePort]
provider = "specs.program_model.providers:effect_provider"
```

Record binding style, state scope, fuzz dimensions, assertions, cleanup, and
bypass limits in `effect_provider_usage.yaml` — review evidence, not config.
Providers must not rewrite the generated case: the modeled outcome is the
oracle. Assert **semantically relevant effect values, counts, and ordering** —
content-level assertions are where providers earn kills that
existence-and-exit-code oracles cannot (the measured attribution: 20 of 36
mutant kills came from provider assertions).

## Stage 5 — Run deterministic campaigns

```bash
python3 scripts/tla_spec_dev.py --spec-root specs run spec-unit-tests \
  --fuzz-runs 25 --seed 20260722
```

Seeds derive per (root seed, case, iteration, port); construct provider
randomness from `context.derived_seed` only. On failure the runner emits
`EFFECT_FUZZ_FAILURE` JSON with an absolute replay command;
`--fuzz-iteration N` re-runs exactly one point. More representatives amplify
your assertions — they cannot repair an oracle that checks only existence.

## Migrating an existing onboarded repository

1. Stages 1–2 as-is (no schema changes needed; purely additive).
2. Add `effect_ports: []` to every action in `actions.yml` — the explicit
   empty list is required once any provider is configured; absent lists fail
   the preflight. With no `[effect_providers.*]` table and no `role: effect`
   port, nothing changes: the legacy execution path is preserved exactly.
3. Migrate ONE boundary at a time: declare its port, implement its provider,
   run `--fuzz-runs 1` until green, then raise the iteration count.
4. Keep manifests inside the constrained dependency-invariant profile:
   indented mappings, single-line inline mappings with scalar values (the
   fitness-rule leaf syntax), floats supported, no nested inline mappings.

## Honesty rails

- The provider interface is SHIPPED; the surrounding modular-fuzzing
  machinery (corpus gate, effect conformance, kill test) remains
  EXPERIMENTAL. The corpus gate refuses over-cap corpora and asks a redesign
  question; it prescribes nothing.
- The three `examples/effect_providers/` projects are validation fixtures
  with 12 recorded, unwaived model-completeness gaps
  (`specs/.history/effect-provider-epic/open-state-at-merge/README.md`) —
  evidence about the interface, never a provider library to import.
- Complexity and effects compose, not excuse: a FIRED fitness rule or a
  god-state dense row is not answered by more fuzz iterations. Minimize
  first; then make the effects real.
