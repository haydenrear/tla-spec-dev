# Effect providers and deterministic campaigns

Use semantic effect providers when a generated case requires a boundary such
as a filesystem, clock, HTTP client, SMTP client, Kafka producer, or queue. The
boundary is a generated runtime-checkable Protocol. The project owns the
provider that implements or installs that Protocol for one case execution.

The division of responsibility is strict: **TLA+ selects the semantic outcome;
the provider owns the concrete representatives**. A case still carries the
modeled `before`, input, output, `after`, and required effect-port names. The
provider receives that original case plus a deterministic seed and chooses a
concrete filename, byte string, response body, exception instance, timestamp,
or message envelope that belongs to the selected semantic class.

This is the answer to the response-generation boundary. TLA+ does not need to
become a byte-level filesystem, broker, or HTTP server. If content changes the
modeled outcome, put that content or its semantic projection in the model and
generated case. If two values are semantically interchangeable to the model,
leave them abstract and let the provider vary their concrete representation.
The provider is therefore a small, explicit refinement layer, not another
semantic authority.

## Minimal project contract

Declare an effect port in `spec_manifest.yaml`:

```yaml
ports:
  FilesystemPort:
    role: effect
    methods:
      write:
        result: None
```

Name every action's complete effect requirements in `actions.yml`, including an
explicit empty list when it has none:

```yaml
actions:
  Publish:
    layer: internal
    controllability: unit_direct
    generates: [spec_unit]
    effect_ports: [FilesystemPort]
```

Select the project-owned provider in `case_adapters.toml`:

```toml
[effect_providers.FilesystemPort]
provider = "specs.program_model.providers:filesystem_provider"
```

Keep `providers.py` outside `generated/`. Generation may replace port
Protocols and cases; it must never replace the project's concrete provider.
The runner resolves every selected action and provider before application hooks
run, refuses undeclared or missing ports, and checks non-`None` bindings against
the generated Protocol at runtime.

## Provider context and lifecycle

A provider implements `bind(context)` and returns a context manager. The
immutable `EffectProviderContext` contains:

- `port_name`, `action`, and the original generated `case` object;
- a point-qualified work directory;
- `iteration` and `root_seed`;
- a stable `derived_seed` for this case, iteration, and port;
- the seed protocol version.

`bind` should only construct a lazy binding. Acquire resources in `__enter__`,
return a generated-port implementation for explicit dependency injection, or
return `None` after installing a bounded patch. The adapter's `setup` hook can
read `context.effects["FilesystemPort"]`, store it on the adapter, and pass it
to production code. Cleanup runs in strict reverse provider order after adapter
teardown. A provider cannot suppress application failures with a truthy
`__exit__`, and cleanup failures are reported separately. If a helper installer
and partial cleanup both fail, the raised aggregate retains the installer
primary plus every nested cleanup error.

Configuration and lazy bindings for the whole selected corpus are prepared
before the first application hook, so a later bind failure prevents every
adapter hook. Runtime resources remain point-local. For provider-bearing runs,
the complete hook order for each singleton point batch is `setup_all`, provider
enter, passive observation around adapter setup/run/assert/teardown, provider
exit, then `teardown_all`. Provider allocation and cleanup are harness
lifecycle, so they are outside passive observation and cannot masquerade as
application effects. Calls made through an injected binding or installed patch
during the adapter lifecycle remain inside passive observation. Batch hooks
receive the singleton case plus `iteration` and `root_seed`; they do not run
inside active provider scopes and must not read per-case bound effects.

The shipped helpers make the two common forms small:

```python
from pathlib import Path
import random

from spec_double_compiler.effects import context_provider, temporary_root_provider


class FilesystemBinding:
    def __init__(self, root: Path, token: str):
        self.root = root
        self.token = token

    def write(self, value: str) -> None:
        (self.root / self.token).write_text(value, encoding="utf-8")


def build_filesystem(root, context):
    rng = random.Random(context.derived_seed)
    return FilesystemBinding(root, f"item-{rng.randrange(1_000_000)}.txt")


filesystem_provider = temporary_root_provider(build_filesystem)


def install_http_patch(context, stack):
    response = response_for_semantic_case(context.case, context.derived_seed)
    stack.enter_context(patch_project_http_client(response))
    return None


http_provider = context_provider(install_http_patch)
```

Both helpers acquire lazily, allocate a fresh resource stack for each binding,
restore partially installed nested patches when a later install fails, and
never suppress a failure. `temporary_root_provider` removes its fresh directory
on success and failure. It supplies a lifecycle root, not a fake operating
system; the project still defines the port behavior and assertions.

Provider state may live in the returned binding for one execution point. That
is enough for a stateful in-memory filesystem, broker, or transport double. Do
not share state across points unless cross-case state is itself the behavior
under test and is explicitly modeled. Ordinarily, state needed by correctness
belongs in the case's `before`/`after` and a new binding materializes it.

## Deterministic representative campaigns

Run multiple provider-owned representatives for every selected case:

```bash
tla-spec-dev --spec-root specs run spec-unit-tests \
  --fuzz-runs 100 --seed 20260721
```

Or call the case runner directly with `--batch`, `--fuzz-runs`, and `--seed`.
These controls require at least one `[effect_providers.<Port>]` table. The seed
protocol derives an independent integer from the version, root seed, case name,
iteration, and port name using SHA-256. It is stable across Python processes,
`PYTHONHASHSEED` values, case reordering, and filtered runs. Construct a local
RNG from `context.derived_seed`; do not use `hash()`, module-global randomness,
or traversal order.

Each case/iteration point gets a fresh adapter cache, shared singleton-batch
mapping, provider bindings, effect mapping and sandbox. Case and batch work
paths are point-qualified; the batch path uses a stable derived key rather than
embedding the raw case name, and case/kind components use stable opaque digest
keys. The original generated case is never copied or mutated. A reused explicit
campaign root may still contain residue from an earlier invocation.

On failure the runner emits one `EFFECT_FUZZ_FAILURE` JSON record per retained
failure. It includes the case, iteration, root seed, seed version, phase, active
provider/seed table, error, and an absolute shell-safe replay command. Phases
distinguish provider bind, enter, invalid binding, adapter setup/run/output
assertion/projected assertion/teardown, adapter/projection loading and
instantiation, singleton `setup_all`/`teardown_all`, and every provider exit
failure.

Run the recorded command from any directory to execute exactly that point. The
runner may still preflight mapping coverage for the generated corpus, but the
selected provider and application execute once:

```bash
python /absolute/run_generated_case_adapters.py /absolute/cases \
  --mapping /absolute/case_adapters.toml --batch --seed 20260721 \
  --fuzz-runs 1 --fuzz-iteration 37 --case 'Publish / unusual name'
```

`--fuzz-iteration` is an exact selector, not a request to run iterations zero
through that number. The flags survive `--python` interpreter re-execution and
the `tla-spec-dev run spec-unit-tests` wrapper.

## Modeling rule and oracle design

Define semantic equivalence before adding arbitrary data. For a filesystem
write, useful modeled classes might be success, already exists, permission
denied, partial write, and retryable failure. Within `success`, a provider may
vary path spelling, Unicode, payload encoding, or chunk sizes only when those
details are intentionally equivalent. If path normalization or exact bytes
matter, project them into TLA+ state/output and assert them; otherwise the
provider can generate values that the oracle never observes.

The adapter and provider must remain self-validating:

1. Materialize the modeled `before` state.
2. Supply or install every declared effect port.
3. Run the real application boundary.
4. Compare output and internal/projected state to the case oracle.
5. Assert the modeled effect payload or state, not merely file existence or a
   zero process exit.

Adding more representatives only amplifies these oracles. It cannot compensate
for an assertion that discards content, field values, counts, ordering, or
state. A provider must not rewrite the case to make its generated response
legal; change the provider representative or improve the semantic model.

## Honest isolation and current limits

Fresh point resources do not provide universal interception. The helper patch
stack only restores resources explicitly entered by the provider, and passive
effect observation only sees supported calls in the current CPython process.
It does not automatically intercept a child process, separate JVM, native
client, deployed Kafka broker, SMTP server, or remote service. Use explicit
dependency injection where possible; otherwise patch the exact project lookup
site and restore it through the provided stack.

The framework resets its adapter cache, shared mapping, bindings, and sandboxes,
and allocates per-point work-directory paths. Case names and adapter kinds are
retained in diagnostics but replaced by stable opaque digest components in
filesystem paths, so generated text cannot traverse or alias a work root.
Helpers clean the temporary roots they own; the framework does not clear a
user-reused explicit work directory.
Project code must remove residue it owns. The framework also cannot reset
application singletons, provider-module globals, imported third-party caches,
threads, child processes, or external services unless the project provider
does so. Treat those as visible design costs. A provider that needs a real
service may manage one, but doing so trades speed and isolation for fidelity;
it does not make monkey patching equivalent to the real service.

This campaign is deterministic enumeration driven by project providers. It is
not exhaustive over Python values, has no Hypothesis shrinking, does not infer
responses from arbitrary TLA+, and does not prove service equivalence. Java and
other runtimes need their own entrypoint/provider bridge; Python patches do not
cross a process boundary.

Most importantly, effectful bug-finding remains **not yet validated**. MF-038
caught **0/9** subtle content/value/field/count mutations because the available
oracles checked existence and exit status rather than content. The provider kit
fixes lifecycle, reproducibility, replay, and pluggability; it does not erase
that evidence. EP-03 must run diverse example-project validations and mutation
probes before the architecture can claim that effectful modeling earns its
cost. Until then, use this as a disciplined experimental harness and report
what its oracles actually distinguish.
