# Effect-provider epic

This epic tests one narrow claim: generated TLA+ cases become substantially
more useful when each case selects typed, project-owned effect providers that
supply stateful concrete behavior and deterministic fuzz values while the
existing adapter executes the application.

The branch is `epic/effect-providers`, pinned to modular-fuzzing commit
`dfd2a8004c10510f4819c5a9b17d652fd3baf8df`. It is a sibling of
`epic/complexity-descriptor`; neither branch consumes or modifies the other's
ticket lane.

## Responsibility boundary

```text
TLA+ transition
  -> generated case (before/input/output/after + action)
  -> actions.yml action.effect_ports
  -> spec_manifest.yaml typed semantic port
  -> case_adapters.toml project provider
  -> provider binding(s) + existing case adapter
  -> application execution
  -> output/state/provider-oracle validation
```

TLA+ chooses semantic outcomes: success versus conflict, retryable versus
permanent failure, approved versus declined, and the corresponding expected
state transition. A provider receives that immutable case and chooses concrete
representatives within its outcome: exact bytes, Unicode paths, an exception
subclass, JSON layout, a 502 versus 503, or a concrete timestamp on the modeled
side of a boundary.

A provider must not turn one semantic outcome into another or rewrite
`before`, `input`, `output`, or `after`. If concrete variants are not actually
equivalent, the model needs another TLA+ case or the project needs an
independent oracle. V0 therefore does not ask TLA+ to encode a call-by-call mock
script, and it does not ask the framework to be a real filesystem, broker, or
HTTP service.

The framework owns:

- fail-closed action-to-port-to-provider lookup;
- generated structural port contracts;
- provider entry/exit and adapter lifecycle ordering;
- deterministic run/case/iteration/port seeds and replay metadata;
- failure-safe cleanup and diagnostics.

The project provider owns:

- concrete responses, exceptions, and state;
- optional explicit dependency injection or a self-installed patch;
- provider-local operation assertions, snapshots, and transcripts;
- the strength and breadth of concrete fuzzing.

The generated case adapter remains the only application entrypoint. An
explicitly modular application consumes `context.effects[PortName]`; legacy
code can instead use a provider whose binding installs a patch and returns no
injected value.

The inherited passive `effects:` schema is not repurposed. It observes escaped
filesystem/process/network activity and remains useful for leak or bypass
detection. Semantic provider ports use the existing generated `ports`
contracts and are selected by `actions.yml`.

## V0 runtime shape

Illustrative declarations (the tickets own final syntax):

```yaml
# spec_manifest.yaml
ports:
  FilesystemPort:
    role: effect
    methods: ...
```

```yaml
# actions.yml
PublishDocument:
  effect_ports: [FilesystemPort]
```

```toml
# case_adapters.toml
[effect_providers.FilesystemPort]
provider = "providers:filesystem_provider"
```

Provider bindings are entered in declaration order before adapter `setup`.
Adapter `setup`, `run`, `assert_result`, and `teardown` all execute while the
bindings remain active. Providers exit in reverse order on every success or
failure path. Unknown ports, missing or duplicate providers, invalid binding
values, and provider-bearing unsupported execution modes fail before
application code runs. Legacy batches with no semantic effect ports continue
to work.

V0 supports Python batch execution. Java, streaming JSONL providers, universal
monkeypatch enforcement, exhaustive Cartesian fuzzing, shrinking, generated
per-call response plans, and production Kafka/SMTP implementations are not in
this epic.

## Ticket lane

1. `EP-01` — typed provider lookup, binding API, fail-closed preflight, and
   correct case lifecycle.
2. `EP-02` — minimal filesystem/patch helper kit, generated stubs,
   `--fuzz-runs`/`--seed`, replay diagnostics, and authoring documentation.
3. `EP-03` — three independently onboarded projects, predeclared mutation
   experiments, Test Graph validation, and a go/no-go recommendation.

Everything else from the inherited plan is complete or explicitly deferred.
The active lane is strictly ordered so each ticket starts from a reviewed merge
of its predecessor.

## Predeclared validation projects

### 1. Atomic publisher — favorable explicit-injection case

An application-owned filesystem protocol publishes versioned JSON documents
through staging plus atomic replace. Modeled outcomes cover create, valid
update, idempotent retry, revision conflict, read failure, stage-write failure,
and replace failure. One strict in-memory provider services generated cases;
a real temporary-directory implementation gets a smaller conformance run.

Fuzz dimensions include Unicode/space-heavy paths, unrelated files, concrete
I/O exception subclasses, enumeration order, and finite exact payloads. The
predeclared mutants include wrong/missing payload fields, double revision
increment, stale overwrite, read-error-as-missing, false success after a write
or replace failure, direct-final writes, reversed replace arguments, extra
writes, and a direct `Path.write_bytes` bypass.

Prediction: exact-byte projection and provider traces kill the shallow-oracle
content bugs found in MF-038; explicit DI keeps integration cost low. The
expensive part should be refinement/projection and the provider oracle, not
the application interface.

Decision target: all modeled outcome pairs execute, all content/value mutants
die, at least 80% of the complete fixed mutation catalog dies, replay is exact,
and the example changes no framework source.

### 2. Legacy payment HTTP — compatibility and bypass pressure

A payment service owns a module-level `requests.Session` and has no injection
seam. Its provider patches `Session.send` during binding, inspects real prepared
requests, returns real response objects or timeout exceptions, records the
attempt transcript, checks script exhaustion, and restores the patch.

Modeled scenarios cover approval, decline, bad request, timeout/unavailable
then approval, duplicate approval after timeout, retry exhaustion, and
malformed responses. Provider fuzzing varies JSON representation, headers,
502/503/504, connect versus read timeout where modeled equivalent, malformed
bytes, and replayable authorization references.

Twelve predeclared mutants cover method, endpoint, amount/type, missing or
regenerated idempotency key, timeout options, missing/illegal/extra retries,
early exhaustion, false approval, and corrupted authorization reference. A
non-scored alternate-client/raw-socket probe tests the monkeypatch ceiling.

Prediction: request/retry bugs are valuable and reproducible, but private patch
coupling and bypass detection cost more than explicit DI. A silent bypass makes
monkeypatch mode compatibility-only and strengthens the case for explicit
ports or process isolation.

Decision target: the 12 in-contract mutants die, 32 deterministic green seeds
have no false positives, a forced failure replays to the same transcript
digest, patches never leak, and no outbound socket succeeds.

### 3. Reminder worker — multi-provider ordering stress test

A designed-for-effects worker receives `Clock`, `Queue`, `Outbox`, and
`Notifier` ports. It claims one scheduled reminder, checks logical time, stages
an outbox entry, sends, records delivery state, and acknowledges or releases /
dead-letters according to the modeled outcome. Four in-memory providers share
one monotonic journal and one immutable concretization bundle.

Modeled families cover empty queue, not-due job, accepted delivery, retryable
failure, permanent failure, already-sent duplicate, and pending-outbox retry.
Provider fuzzing varies identifiers/content, boundary timestamps and offsets,
opaque receipt tokens, idempotency keys, exception subclasses, and repeated
clock reads while preserving the selected semantic class.

Twelve predeclared mutants cover acknowledge/send/stage/mark ordering,
acknowledging or failing to release after retryable failure, duplicate send,
the exact due-time boundary, inconsistent multiple clock reads, wrong
recipient/body/idempotency key, job-ID-versus-receipt confusion, and permanent
failure treated as retryable. Direct clock and network bypasses are recorded as
separate capability probes.

Prediction: this yields the strongest semantic benefit and the highest
modeling/composition cost. It should reveal whether the generic runtime later
needs a shared journal, correlated concretization bundle, snapshot composition,
or explicit normalized outcome metadata.

Decision target: 12/12 in-contract mutants die over 25 deterministic seeds,
failures replay from case ID plus seed, state does not leak between cases, and
independent onboarding modifies no framework file. Ten or eleven kills means
investigate one generic improvement; fewer than ten or inability to express
cross-provider order means redesign.

## Common measurements

The experiments record raw evidence, not only green/red summaries:

- TLC generated/distinct states, depth, generation time, selected cases, and
  action/outcome coverage;
- seed count, executions, runtime p50/p95, first-discovery seed, and exact
  replay success;
- control result and every fixed mutant's killed/survived status, attributed
  separately to output, projected state, provider-local assertion, shared
  journal, or passive leak detection;
- provider, interface, adapter, projection, and application LOC/files changed;
- framework edits (target zero), onboarding iterations, and authoring time;
- provider decisions not derivable from the generated case, duplicated
  concretization/projection logic, bypass attempts, leaked files/sockets/state,
  and run-to-run divergence;
- retrieval-cost proxy: the files/lines an agent needed to implement a new
  provider and whether `SKILL.md` plus its routed reference was sufficient.

Findings stay visible and are not fixed inside the measurement run. EP-03 ends
with an evidence-backed recommendation on whether to ship this architecture,
which generic improvements have earned follow-up tickets, and whether Java is
the next useful adapter or premature expansion.
