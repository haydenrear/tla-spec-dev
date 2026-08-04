# Agent-authored effect providers

The framework ships one effect extension point. A repository agent implements
it against the typed ports generated from that repository's
`spec_manifest.yaml`.

## Content assertion is the default, and the alternative is loud

Read this before anything else on this page, because it decides what a kill
number from this repository means.

**The measurement.** Content-asserting effect providers caught 2 of 6 seeded
faults that nothing else caught -- the two durable-side ones -- reproduced cell
for cell across two rounds, then independently replicated by a blind agent on a
fresh 16-mutant catalogue: 3 of 3 durable-write mutants died under the checking
mapping and 0 of 3 under the silent one. That is roughly 30% of the
instrument's entire yield riding on which provider a mapping file names.
HP-05 reproduced the split a third time on a different fixture, at 2 of 2
against 1 of 2 (`specs/.history/hexagonal-prompting-epic/ticket-004-HP-05/`).

**What changed at HP-05.** Codegen now writes the provider and binds it:

- `generate_python.py` emits `effect_providers.py` into the generated package
  for every manifest port with `role: effect`, containing a **content-asserting
  provider** and a **silent** one;
- it adds an `[effect_providers.<Port>]` table naming the content-asserting
  provider to `case_adapters.toml` for any effect port that has none. It is
  additive and never rewrites a table somebody already wrote, so a deliberate
  choice survives regeneration;
- it prints an audit of the resulting mapping, unprompted, on every run.

Before this, `scaffold project` shipped a `raise NotImplementedError` provider
stub and a commented-out binding, and the author wrote the assertion -- or, in
the measured case, did not. A round-2 blind agent authored a mapping to get a
slice running and did not realise until afterwards that the instrument it had
built was strictly weaker than the one it thought it had.

**Nothing here refuses.** An unbound port, a silent provider, and a port with
no `content:` block all run. All three are announced. This is a report, not a
gate.

### Declaring what a durable write refines

An after-state comparison structurally cannot see a durable write: the
in-memory projection can be perfect while the persisted bytes are wrong. To
compare them, something must say what the bytes refine. That is `content:`, and
it is one line per checked field:

```yaml
ports:
  LedgerAppendPort:
    role: effect
    kind: durable_write
    methods:
      append:
        command: AppendLedgerLine
        result: str
    content:
      append:
        total: "committed[tenant]"
```

Read as: *every `append` crossing carries a `total`, and it must equal the
modeled after-state's `committed`, indexed by that same crossing's `tenant`.*
The grammar is deliberately two productions -- `variable` and
`variable[payload_field]` -- because a third would be the beginning of an
expression language, and this is a comparison, not an analyzer.

The framework does not and cannot infer this sentence. On the HP-01 quota-ledger
fixture the modeled ledger element is `<< "COMMIT", tenant, amount >>` and
carries **no running total at all**, so no amount of corpus generation reaches a
corrupted total; but the total the implementation writes is a refinement of
`committed[tenant]`, which the model does have. Somebody writes that down once.
What HP-05 changed is that the provider around it is generated and bound, and
that its absence is announced instead of assumed.

### What a run says

Every bound generated provider announces itself once, on stdout, the first time
it binds -- no flag, no report subcommand. Two shapes, and only two:

```text
[effect-mapping] DURABLE-WRITE ORACLE ACTIVE: LedgerAppendPort (kind: durable_write)
  is bound to <provider> under mapping <path>, asserting 1 content field(s)
  against the modeled after-state: append.total == committed[tenant]
```

```text
[effect-mapping] NO DURABLE-WRITE ORACLE: LedgerAppendPort (kind: durable_write)
  is bound to the SILENT provider <provider> under mapping <path>. Nothing
  compares what crossed this port against the model, so kills counted under
  this mapping are a FLOOR, not a total, and a green run over-reads.
```

The second wording is also emitted when a content-asserting provider is bound to
a port that declares no `content:` block, and by the codegen audit for a port
that is declared `role: effect` and bound to nothing, and for a boundary
declared under `effects:` that has no `ports:` entry and therefore no Protocol
any provider could implement. All four are the same fact -- *this run has no
durable-write oracle for this boundary* -- and they say it in the run's own
output rather than only here.

**Naming the mapping.** The framework does not hand a provider its mapping path,
so the announcement resolves the name from `TLA_SPEC_DEV_MAPPING` if set, then
from the run's own `--mapping` argument, and otherwise says
`<unnamed mapping: set TLA_SPEC_DEV_MAPPING to name it>`. An unnamed mapping is
itself worth announcing: a kill number whose mapping cannot be named is a kill
number nobody can reproduce.

**The boundary of this, stated rather than glossed.** A provider announces its
own binding, so a mapping that names a *hand-written* provider the framework did
not generate announces nothing, and the framework cannot tell from inside
whether it asserts content. The codegen audit reports what the mapping file
says; the run-time announcement reports what generated code was bound. Between
them they cover the shipped paths and not the third-party one.

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

Codegen writes this table for you, naming the generated content-asserting
provider, if the port has no table yet. Replacing it with a repository-owned
provider is the supported path -- the sections below are about writing one --
and so is naming the generated `silent_*_provider`, which announces on every
run that this mapping carries no durable-write oracle.

Keep hand-written provider source outside `generated/`. Generation owns the port
Protocols, the cases, and the default providers; repository code owns anything
richer than a recorded crossing compared against the model.

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
packages are installed. Its profile: indented mappings, plus single-line
inline mappings with scalar values (the fitness-rule leaf syntax, as mapping
values or sequence items); nested or multi-line inline mappings are rejected
with an instruction to use indented mappings. Replay commands retain the
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
