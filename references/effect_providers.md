# Agent-authored effect providers

The framework ships one effect extension point. A repository agent implements
it against the typed ports generated from that repository's
`spec_manifest.yaml`.

The product boundary is strict:

- TLA+ selects the semantic outcome and the state transition.
- The generated case carries that outcome as the oracle.
- The repository provider owns concrete representatives, local state, setup,
  assertions, and cleanup.
- The framework owns discovery, typed-port binding, lifecycle, deterministic
  seeds, failure evidence, and exact replay.

The framework does not ship domain implementations. Validation examples are
evidence about the interface, not a reusable provider library.

## Declare the semantic port

Declare the repository's own abstraction in `spec_manifest.yaml`:

```yaml
commands:
  ApplyRepositoryEffect:
    fields:
      value:
        type: str
ports:
  RepositoryEffectPort:
    role: effect
    methods:
      apply:
        command: ApplyRepositoryEffect
        result: str
```

Every action in `actions.yml` names its complete effect requirements. Use an
explicit empty list for actions without effects:

```yaml
actions:
  Advance:
    layer: internal
    controllability: unit_direct
    generates: [spec_unit]
    effect_ports: [RepositoryEffectPort]
```

Map the port to a repository object in `case_adapters.toml`:

```toml
[effect_providers.RepositoryEffectPort]
provider = "specs.program_model.providers:effect_provider"
```

Keep provider source outside `generated/`. Generation owns the port Protocols
and cases; repository code owns the implementation.

## Implement the one interface

A provider is an object with:

```python
bind(context: EffectProviderContext) -> ContextManager[object | None]
```

Callable-only factories are not providers. `bind` must return a standard
context manager. It yields either:

- an object implementing the selected generated port, for explicit injection;
  or
- `None`, when the scope installs and restores a bounded repository
  integration itself.

A neutral provider shape is:

```python
from __future__ import annotations

from contextlib import contextmanager
from random import Random
from collections.abc import Iterator
from typing import Any

from spec_double_compiler.runtime import EffectProviderContext


class ProjectEffectProvider:
    @contextmanager
    def bind(self, context: EffectProviderContext) -> Iterator[Any | None]:
        rng = Random(context.derived_seed)
        binding = build_repository_binding(
            port_name=context.port_name,
            semantic_case=context.case,
            rng=rng,
        )
        try:
            yield binding
        finally:
            binding.close()


effect_provider = ProjectEffectProvider()
```

The immutable context contains `port_name`, `action`, the original generated
`case`, a point-qualified `work_dir`, `iteration`, `root_seed`,
`derived_seed`, and `seed_version`.

The provider must not rewrite the generated case. If a concrete value cannot
represent the modeled outcome, change the provider or improve the semantic
model; do not mutate the oracle.

## Bind it to the application

The adapter receives an immutable `context.effects` mapping. Its keys are the
generated port names selected by the action:

```python
class AdvanceAdapter:
    def setup(self, context):
        self.effect = context.effects["RepositoryEffectPort"]

    def run(self, case, work_dir=None):
        return run_application(case.input, effect=self.effect)
```

The runner preflights all selected actions, ports, generated Protocols, and
provider references before an application hook runs. A non-`None` entered
value must implement the selected generated Protocol. Every provider method
must also match the generated parameter names/kinds, parameter annotations, and
return annotation. A method-name-only object fails before adapter setup.

Record each provider's local contract in `effect_provider_usage.yaml`:

```yaml
version: 1
providers:
  - port: RepositoryEffectPort
    provider: specs.program_model.providers:effect_provider
    binding_style: explicit_injection
    state_scope: execution_point
    fuzz_dimensions: [representative]
    assertions: [modeled_result, projected_state]
    cleanup: context_manager
    bypass_limits: []
```

This file is review evidence, not executable configuration. It makes local
state, fuzz dimensions, assertions, and known bypasses visible without
promoting them into a framework library.

## Lifecycle and isolation

For each selected case and fuzz iteration the runner creates fresh adapter
caches, shared mappings, provider bindings, effect mappings, work paths, and
passive-observation state.

The point lifecycle is:

```text
setup_all
  provider enter (declared port order)
    adapter setup
    adapter run
    output/projected-state assertions
    adapter teardown
  provider exit (reverse order)
teardown_all
```

Resources should be acquired in context-manager entry, not while `bind`
constructs the scope. Provider cleanup always runs. A truthy `__exit__` cannot
suppress an application failure, and cleanup failures remain visible beside
the primary failure.

Provider allocation and cleanup are harness lifecycle, outside passive
observation. Calls made through the entered binding during application
execution remain observable. Point isolation cannot reset application globals,
third-party caches, threads, child processes, or external state; the repository
provider must own those costs explicitly.

## Deterministic representative campaigns

Run several repository-owned concrete representatives for every generated
semantic case:

```bash
tla-spec-dev --spec-root specs run spec-unit-tests \
  --fuzz-runs 100 --seed 20260721
```

The framework derives a stable per-port seed from the seed protocol version,
root seed, case name, iteration, and port name. Providers should construct
local random generators from `context.derived_seed`. Do not depend on
`hash()`, module-global randomness, traversal order, or shared mutable state.

On failure the runner emits `EFFECT_FUZZ_FAILURE` JSON with the case,
iteration, seeds, phase, active providers, error, and an absolute replay
command. `--fuzz-iteration` selects exactly one iteration:

```bash
python /absolute/run_generated_case_adapters.py /absolute/cases \
  --mapping /absolute/case_adapters.toml --batch --seed 20260721 \
  --fuzz-runs 1 --fuzz-iteration 37 --case 'Advance / unusual name'
```

The provider determines what “fuzzing” means. It may enumerate a finite set,
draw deterministic representatives, or delegate to a repository-owned
generator. The framework schedules and replays points; it does not infer
concrete responses from arbitrary TLA+.

## Model response classes, not implementation scripts

Put a distinction in TLA+ when it changes the allowed output, state,
cardinality, ordering, or retry behavior. Put interchangeable concrete
representations in the provider.

For each modeled outcome, the adapter/provider pair should:

1. materialize the modeled `before` state;
2. bind every declared port;
3. run the real application boundary;
4. compare output and projected state with the generated oracle;
5. assert semantically relevant effect values, counts, and ordering.

More representatives amplify those assertions. They cannot repair an oracle
that checks only existence or process success.

## Current limits

The interface is currently Python-native. Another runtime needs a native typed
provider and an explicit application entrypoint; a Python scope is not a
universal cross-process interception mechanism.

Runtime validation checks structural presence plus generated callable shapes
and annotations. It does not execute methods to prove that returned values
match annotations, and it does not prove behavioral substitutability; use the
generated contract tests and a repository static type-check rung for those
claims.

Manifest loading uses one constrained parser whether or not optional YAML
packages are installed. Inline mappings are outside that supported syntax and
fail with an instruction to use indented mappings. Replay commands retain the
originating interpreter path, including a dependency-bearing virtualenv, and
remain absolute so they work from another directory.

This is deterministic representative enumeration, not exhaustive value search.
It does not provide automatic shrinking, infer service semantics, or prove
equivalence to an external system.

## Validation evidence

`examples/effect_providers/` contains three deliberately different
repository-owned implementations. They test explicit injection, bounded legacy
integration, multiple correlated ports, local state, bypass probes, exact
replay, cleanup, and projected-state assertions. They are experimental
validation fixtures and must not be imported as public provider libraries.

EP-03's historical audit found twelve concrete gaps in those example
applications. That result remains preserved and valid. It measured example
model completeness, not whether the generic provider interface could be
implemented by an agent. The contract reduction does not waive any gap or
reclassify a failing example as framework success; repeated example validation
must continue to report both SDK behavior and application-specific costs.

Run all three projects against the current contract with fresh,
non-overwriting evidence:

```bash
python3 examples/effect_providers/run_validations.py --all --fresh-evidence
```

Use `--project <name>` for an independent project and `--run-id <id>` when a
stable external run identifier is useful. Each project owns the same
`validate.py --run-id <id>` entrypoint and writes a versioned common result;
the projects keep their own models, mutation catalogs, provider assertions,
and real-boundary rungs. The shared schema and preservation rules live in
`examples/effect_providers/VALIDATION_CONTRACT.md`.
