# Effect-provider experiment results

## Outcome

Ship the Python V0 as an opt-in experimental harness, with conditions. All
three preregistered projects passed their green controls and killed their fixed
catalogs without framework changes, but the experiments do not support calling
this a general fuzzing gold standard yet. Broad typed-contract claims also need
the shared dependency-sensitive manifest parser fixed (`DEF-002`); the reminder
project neutralizes that syntax locally and proves typed forced-fallback
reproducibility. A separate manual diagnostic established the PyYAML/fallback
split; the unit test does not assume PyYAML is installed.
The aggregate graph separately compares the complete normalized parse trees
through PyYAML and the fallback, including null result semantics.

Across the three fixed catalogs, generated cases plus providers killed 36/36
mutants. The separate hand-written baselines killed 30/36: atomic publishing
added two kills, the reminder workflow added four, and the legacy HTTP catalog
added none. That aggregate is descriptive, not a pooled statistical comparison,
because each hand baseline covers a different set of ordinary scenarios.

The strongest result is architectural: TLA+ can remain semantic while a
project-owned provider chooses deterministic concrete representatives. The
weak spot is also clear: terminal-state cases do not yet carry enough normalized
effect-plan metadata, so complex providers duplicate order, cardinality,
response-class, command, and projection rules.

## Comparison

| Project | Boundary | Cases × control iterations | Effectful | Hand baseline | Additional kills | Verdict |
|---|---|---:|---:|---:|---:|---|
| Atomic publisher | Explicit injected filesystem | 7 × 16 = 112 | 12/12 | 10/12 | +2 | Go |
| Legacy payment HTTP | Self-installed `Session.send` patch | 56 × 32 = 1,792 | 12/12 | 12/12 | +0 | Conditional legacy use |
| Reminder worker | Four correlated injected providers | 7 × 25 = 175 | 12/12 | 8/12 | +4 | Go for high-value workflows |

Every accepted result has two deterministic repetitions, cleanup/isolation
evidence, source provenance, and zero framework-file changes. HTTP and reminder
replay every first discovery in both repetitions. Atomic replays every first
discovery exactly in repetition one, then proves repetition-two stability with
equal transcript and verdict digests instead of duplicating replay work. Killed
mutants stop after the first complete failing iteration: seven points for
atomic/reminder and 56 for HTTP at iteration zero in these runs. Only green
controls exercised every representative. Thus 36/36 measures oracle coverage
for the fixed catalog, not that later fuzz values discovered the bugs.

## Where the kills came from

Attribution below uses each preregistered expected detector exactly once, not
every secondary detector that happened to fire.

| Oracle owner | Atomic | HTTP | Reminder | Total |
|---|---:|---:|---:|---:|
| TLA-derived output/projected-state oracle | 8 | 2 | 5 | 15 |
| Provider assertion or shared journal | 3 | 10 | 7 | 20 |
| Passive bypass detector | 1 | 0 | 0 | 1 |

This is the main design conclusion. TLA+ described outcomes well enough to
drive 15 kills directly. Providers earned another 20 by validating concrete
requests and cross-effect protocols that the generated terminal-state cases do
not express. That is useful, but it means the provider is partly an oracle and
response implementation today. More random data cannot repair an omitted
oracle.

## Cost and benefit by project

| Project | Provider LOC | Adapter LOC | Interface LOC | Experiment LOC | Frozen onboarding files / lines | Retrieval files / lines |
|---|---:|---:|---:|---:|---:|---:|
| Atomic | 332 | 324 | 81 | 826 | 48 / 3,779 | 28 / 5,934 |
| HTTP | 402 | 165 | 75 | 1,597 | 51 / 6,911 | 32 / 7,701 |
| Reminder | 328 | 106 | 107 | 1,122 | 22 / 2,363 | 18 / 3,639 |

The raw wall clocks are not directly comparable: each agent recorded a
different elapsed-time scope and concurrent work is included. Component LOC is
current through accepted evidence; the files/lines and retrieval columns are
frozen onboarding measurements taken before the first scored campaign. Exact
scopes, edit/run loops, TLC counts, runtimes, and source digests are in
[`RESULTS.json`](RESULTS.json) and the per-project evidence.

Atomic publishing gave the cleanest value signal. Explicit injection covered
real filesystem state, added two kills over the ordinary baseline, and the
real-filesystem validation exposed a genuine staging-file cleanup bug during
review. Its adapter still hard-codes expected revision because the case lacks a
normalized command plan.

The legacy HTTP patch worked, but it is not the default design for new code.
The hand baseline already killed all 12 mutants; `urllib` and raw sockets bypass
`Session.send`; and replay exposed a virtualenv-symlink defect that required an
explicit dependency import root. The socket guard blocked the probes and the
real loopback/process rung passed all 56 external cases, so this remains useful
as an honest compatibility option.

The reminder workflow produced the largest incremental gain: four state/order
bugs absent from the four-scenario baseline. It also exposed the largest
semantic duplication. The provider hard-codes `stage < send < mark < ack`, one
clock read, duplicate-send rejection, notifier response classes, and a manual
state projection. A direct clock read bypassed its port and a raw network path
required a separate passive guard. Fresh-checkout review also found that valid
inline YAML maps produced typed contracts only when optional PyYAML happened to
be installed. The project expanded all 26 maps, committed the intended typed
tree, and now regenerates and compares the whole tree both normally and under
`python -S`. Two new post-correction campaigns retained the same `9c5131bb…`
verdict digest, 12/12 score, 8/12 baseline, replay, cleanup, and source hashes.
The shared fallback parser remains a major deferred defect.

The fresh-checkout correction is not included in reminder's frozen 22 / 2,363
onboarding figure. It separately touched seven tracked project files (+298/-52
lines): five generated files, the normalized manifest, and a 65-line
reproduction test. It changed no framework file; final interface LOC remains
107, while model LOC is 564 and experiment LOC is 1,122.

## Recommended architecture

1. Make manifest parsing and contract generation dependency-invariant. Support
   valid inline maps in the constrained parser or pin a YAML implementation and
   fail closed; compare complete typed output trees across both parser paths.
2. Generate a normalized semantic effect plan from modeled transition
   annotations: response class, effect order/cardinality, semantic command
   fields, and projection obligations. Add a generic point-scoped correlated
   bundle, monotonic journal, and snapshot-composition utility; keep domain
   assertions and concrete bytes, paths, exceptions, headers, and opaque values
   project-owned. Do not generate a byte-level call script from TLA+.
3. Generate explicit provider signature/annotation conformance and add a static
   type-check rung. Python `runtime_checkable` Protocols prove method presence,
   not command arity or result types (`DEF-003`).
4. Fix replay provenance so commands preserve the originating virtualenv
   interpreter without resolving its symlink; test with a dependency-bearing
   provider.
5. Add an optional collect/continue mode and data-dependent mutants. Preserve
   exact first-failure replay while measuring whether later representatives
   actually add discovery power.
6. Standardize compatibility declarations, passive bypass probes, and stronger
   process/network or real-service validation rungs. A monkey patch must never
   imply universal interception.
7. Defer a universal response-plan DSL. First standardize only semantic fields
   proven common across more domains; otherwise the schema merely moves service
   implementation detail into TLA+.
8. Add Java after parser parity, semantic-plan, Python signature-conformance,
   and replay contracts stabilize. Use
   JVM-native typed providers plus an external entrypoint protocol. A Python
   adapter service should not be the default Java architecture because it adds
   process entrypoints and loses native interception/type fidelity.

These priorities preserve the property the user wants: application code stays
modular because every modeled effect must pass through an explicit boundary,
while each generated case is self-validating. The next investment should
reduce duplicated semantic intuition in providers, not increase arbitrary data
volume.

## Evidence and limits

- Preregistration: [`PREREGISTRATION.yaml`](PREREGISTRATION.yaml), SHA-256
  `970ade21dcf9e460a60cdb1e70396b5b5507c460983e7001cb1bceff5fe9390b`,
  committed before project implementation at `141e63b`.
- Atomic: [`atomic-publisher-raw.json`](atomic_publisher/evidence/atomic-publisher-raw.json).
- HTTP: [`reviewed-local-repetition-1.json`](legacy_payment_http/evidence/reviewed-local-repetition-1.json)
  and [`reviewed-local-repetition-2.json`](legacy_payment_http/evidence/reviewed-local-repetition-2.json).
- Reminder: [`reviewed-parser-parity-1/results.json`](reminder_worker/evidence/runs/reviewed-parser-parity-1/results.json)
  and [`reviewed-parser-parity-2/results.json`](reminder_worker/evidence/runs/reviewed-parser-parity-2/results.json).

The retained superseded/failed runs remain visible and unscored. This work does
not claim exhaustive values, Hypothesis shrinking, arbitrary TLA+ response
synthesis, universal interception, or equivalence with production services.
Fresh-checkout validation is recorded in the EP-03 ticket evidence after the
final Test Graph run.
