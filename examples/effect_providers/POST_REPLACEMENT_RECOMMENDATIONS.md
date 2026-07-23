# Post-replacement effect-provider recommendation

## Decision

Ship the Python V0 as one generic, agent-authored
`EffectProvider.bind(context)` interface. Do not ship filesystem, HTTP, queue,
outbox, notifier, Kafka, SMTP, or temporary-root implementations.

The three independent EP-06 reviews show that the generic boundary is viable
for arbitrary repositories, not just this repository's host TLA+ model. Each
project generated its own typed ports from its own model, and an agent supplied
all concrete behavior, state, installation, assertions, and cleanup. No
framework code interpreted a filesystem, HTTP response, clock, queue, or
notification.

This is a credible V0, but it is not yet the low-cost gold standard. The
remaining distance is mostly authoring ergonomics around semantic effect
expectations and correlated point state, not a missing catalog of domain
adapters.

## Fresh aggregate result

The accepted repository run is
`evidence/validation-runs/ep06-central-20260722-v2/aggregate.json`.

| Project | Binding | Generated cases | Control points | Mutant executions | Exact replays | Cleanup | External cases | Time |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| atomic publisher | explicit, one port | 14 | 224 | 24/24 | 12/12 | 392/392 | 7 | 9.69s |
| legacy payment HTTP | self-installed patch | 112 | 1,792 | 12/12 | 13/13 | 2,477/2,477 | 56 | 40.63s |
| reminder worker | explicit, four correlated ports | 14 | 175 | 12/12 | 12/12 | 271/271 | 7 | 6.47s |
| **Aggregate** |  | **140** | **2,191** | **48/48** | **37/37** | **3,140/3,140** | **70** | **59.92s** |

There are 36 unique fixed mutants; the atomic project deliberately scores its
12-mutation catalog across two repetitions. All prior EP-03 evidence remained
byte-identical. Failed EP-06 attempts are retained: they distinguish sandbox
listener denial, stale evidence digests, inaccurate channel declarations, and
shared-worktree audit assumptions from model or application failures.

## What the measurements actually support

- Atomic's hand-written baseline killed 10/12 mutants; the complete generated
  outcome set plus provider journal killed 12/12.
- Reminder's four-scenario baseline killed 8/12; seven generated outcomes plus
  correlated provider assertions killed 12/12.
- HTTP's hand-written baseline already killed 12/12. Its value was systematic
  cross-product execution, deterministic variation, isolation, exact replay,
  and a real boundary—not a higher mutation score.
- Reminder killed every mutant in fuzz iteration zero. Atomic's additional
  kills also came from semantic outcome coverage. These catalogs therefore do
  not yet prove that later arbitrary data discovers more bugs. Later iterations
  currently prove representative robustness and replay stability.
- HTTP's 56-case real loopback rung consumed about 32.7 of 40.6 seconds. The
  expensive boundary tier, not provider execution, dominated recurring cost.

The modular structure does earn its keep: output equality, projected state,
provider-owned call journals, passive bypass probes, and real-boundary checks
caught different defect classes. But future claims about fuzzing lift need
data-dependent and cross-product-dependent mutants that iteration zero cannot
kill.

## Stable ownership boundary

The framework should own only:

- generated typed port Protocols and exact signature preflight;
- provider discovery and fail-closed action/port mapping;
- point lifecycle, reverse cleanup, immutable case oracles, deterministic
  per-port seeds, diagnostics, and exact replay; and
- the small common result/usage schema and non-overwriting aggregate gate.

TLA+ should own distinctions that change allowed output, state, effect
cardinality, or ordering. It should not enumerate concrete paths, status-code
representatives, response bytes, exception subclasses, message text, or patch
mechanics.

The repository provider should own concrete representatives, response
materialization, local state, installation, effect-specific assertions,
projection of concrete values to modeled classes, bypass limits, and cleanup.
That means TLA+ supplies a semantic response class; the provider supplies every
concrete response for every fuzzed point within that class.

## Highest-value follow-up research

1. **Generate abstract effect expectations per case.** Atomic and reminder both
   duplicate semantic rules outside the generated case. A compact expectation
   should be able to name an operation, symbolic response class, cardinality,
   partial-order constraints, and relevant state delta. The provider would map
   that expectation to deterministic concrete values. Do not generate a
   concrete mock call script.
2. **Measure a point-local shared scope before adding it.** Reminder needed an
   ad hoc registry, correlated seed bundle, and four-binding reference count.
   A framework-owned point identity, shared mapping, and cleanup stack could
   remove that machinery, but only one current consumer requires it. Validate
   the pattern in another correlated repository before expanding the interface.
3. **Separate fast semantic and expensive boundary tiers.** Keep the real
   boundary mandatory for release confidence, but schedule it independently
   from quick provider/case feedback. HTTP shows why the two costs should be
   visible rather than conflated.
4. **Add collect/continue and shrinking only with decision-grade cases.** A
   collect mode would measure sensitivity after first discovery; shrinking
   would reduce a failing concrete representative. Neither should precede a
   catalog capable of demonstrating incremental data-driven discovery.
5. **Treat self-installed providers as compatibility-only.** A provider that
   yields `None` cannot receive generated method-signature conformance. Require
   an explicit bypass list, non-overlap assumptions for process-global patches,
   passive probes, and a real external rung.

The three project validators are intentionally evidence-heavy: 333, 356, and
546 lines, plus the 343-line aggregate runner. Much of that code records a
fixed research catalog, provenance, timings, raw artifacts, and failure
history; it is not the minimum provider authoring cost. The repeated generic
mechanics—append-only run creation, subprocess bounds, common result writing,
and snapshot-based no-rescue auditing—are candidates for later factoring.
Concrete provider behavior is not.

## Java direction

Do not try to reuse Python monkey patches across runtimes. A Java V1 should
consume serialized generated cases plus the same abstract effect expectations,
bind native typed Java providers, run a thin application entrypoint, and return
a normalized semantic result/effect trace for comparison. This preserves one
model and oracle while keeping interception, state, and cleanup native to the
application runtime.

Proceed Python-first. Revisit Java after abstract effect expectations and one
additional correlated-state consumer establish the minimal cross-language
contract.
