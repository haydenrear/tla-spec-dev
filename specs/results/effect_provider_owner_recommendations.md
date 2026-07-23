# Effect-provider epic: owner recommendation

## Decision

Ship the Python batch implementation as an **opt-in experimental V0**, after
dispositioning the formal coverage findings below. Do not describe it as the
testing gold standard yet.

The experiment supports the core architecture: a generated TLA+ case selects a
semantic outcome, the harness resolves the required typed effect ports, and a
project-owned provider installs deterministic concrete behavior around that
case. This gives application authors a useful modularity pressure without
turning TLA+ into a filesystem, HTTP, Kafka, or SMTP simulator.

It does not yet prove that the model owns every important behavior or that
later fuzz values find additional bugs. The mutation result is strong evidence
for fixed-catalog oracle coverage, not exhaustive behavior coverage.

| Completeness gate | Result |
|---|---|
| Formal audit verdict | `FAIL` — promotion blocked |
| In-scope hard-gap count | `12` |
| Evidence | [Coverage audit report](coverage_audit_report.md) |

The epic must not be promoted as complete if the formal audit reports an
in-scope hard gap. Every such gap needs an explicit model change or a deliberate
program-contract reduction; provider tests and successful mutants are not
substitutes for model coverage.

## What the three tickets delivered

- **EP-01:** fail-closed `case action -> semantic effect port -> provider`
  resolution; structural Protocol preflight; immutable case oracles; bindings
  exposed through the adapter context; ordered entry and reverse, failure-safe
  cleanup; explicit injection and self-installed patches; refusal of unsupported
  provider-bearing execution modes.
- **EP-02:** stable SHA-256-derived seeds for case, iteration, and port;
  bounded `--fuzz-runs`; exact single-iteration replay; isolation and opaque
  work paths; temporary-filesystem and generic context-provider helpers;
  generated project stubs and authoring guidance.
- **EP-03:** three preregistered Python projects spanning an injected real
  filesystem, legacy HTTP monkeypatching with passive bypass guards, and four
  correlated stateful providers; two deterministic accepted repetitions,
  mutation baselines, cleanup/replay evidence, real-boundary rungs, and a fresh
  checkout aggregate validation.

Fresh-checkout validation passed 611 repository tests, 63 spec units, host TLC
at 5,619,356 generated / 231,621 distinct states with no error, all host Test
Graph nodes, and the effect-provider graph with 22/22 assertions.

## Measured cost and benefit

| Project | Control points per repetition | External cases | Effectful kills | Hand baseline | Added kills | Provider + adapter LOC | Decision |
|---|---:|---:|---:|---:|---:|---:|---|
| Atomic publisher | 112 | 7 | 12/12 | 10/12 | +2 | 656 | Go; best low-cost signal |
| Legacy payment HTTP | 1,792 | 56 | 12/12 | 12/12 | +0 | 567 | Compatibility use only |
| Reminder worker | 175 | 7 | 12/12 | 8/12 | +4 | 434 | Go for high-value workflows |
| **Total** | **2,079** | **70** | **36/36** | **30/36** | **+6** | **1,657** | **Conditional Python V0** |

The projects changed 13,053 frozen-onboarding lines across 121 files and
required 29 recorded edit/run loops. Reported elapsed authoring measurements
were 38.6, 291.8, and 101.8 minutes, but their timing scopes differ and include
concurrent elapsed time, so LOC and loops are the more comparable cost signals.

The 30/36 baseline comparison is descriptive: each baseline covered a
different ordinary scenario set. All 36 mutants failed at iteration zero;
killed runs then stopped, while only green controls exercised every concrete
representative. Consequently, the experiment proves the fixed oracle catalog
can catch these defects, but does not show incremental discovery from later
fuzz values.

Expected-detector attribution is the clearest measure of the present boundary:

| Oracle owner | Kills |
|---|---:|
| TLA-derived output or projected-state oracle | 15 |
| Provider assertion or shared journal | 20 |
| Passive bypass detector | 1 |

## Ownership boundary

| Layer | Owns |
|---|---|
| TLA+ model and generated case | Legal semantic outcomes; before/input/output/after expectations; modeled state transitions, invariants, and refinements. A future normalized effect plan should also carry semantic response class, effect order/cardinality, command fields, and projection obligations. |
| Project provider | A deterministic concrete representative inside the selected outcome; local fake state; bytes, paths, headers, exceptions, opaque IDs, and service-specific assertions; installation and cleanup of the effect boundary. |
| Harness | Fail-closed lookup, lifecycle, isolation, immutable case protection, stable seed derivation, structured failure evidence, and exact replay. |
| Passive guard / real-boundary rung | Evidence that code escaped the declared boundary, plus validation that a monkeypatch did not imply universal interception. |

TLA+ therefore should not generate a byte-level response implementation. It
should select, for example, `approved`, `transient_failure`, or
`permanent_failure`; the provider chooses a legal concrete response in that
class and maintains only the state needed to realize it. If a concrete response
changes the semantic outcome, it requires another modeled case or an explicitly
independent oracle. Increasing random-data volume cannot repair a missing
semantic oracle.

## Coverage warning

The formal audit, strengthened by an independent cross-check, found twelve
hard model-completeness gaps:

- application CLI parsing, stdio, result-artifact writes, and error contracts
  are not visibly represented in both views;
- the HTTP models are terminal-outcome models, while request shape, retry
  sequences, response normalization, and session behavior remain largely
  provider-owned;
- the reminder models omit the intermediate `stage < send < mark < ack`
  protocol, order/cardinality, receipt correlation, crash/persistence states,
  and supported initial-outbox/notifier-outcome cross-products that the shared
  journal and providers currently assert;
- the atomic models do not own request/prestate-to-scenario guards, several
  serialization and malformed-state contracts, false effect results,
  staging cleanup, or cleanup-failure edge behavior.

These are exactly the weak spot exposed by the 20 provider-owned kills. A
provider may supply concrete behavior, but important semantic order and
cardinality rules should not exist only in provider code.

## Prioritized improvements

1. **Disposition every formal coverage gap.** Model the behavior in both views
   or simplify/narrow the application contract. Keep providers and tests from
   being counted as model coverage.
2. **Make manifest parsing dependency-invariant (`DEF-002`).** Support the
   constrained YAML surface identically with and without optional PyYAML, or
   require one parser and fail closed; compare the complete generated typed
   tree.
3. **Generate a normalized semantic effect plan.** Add response class,
   order/cardinality, semantic command fields, and projection obligations from
   modeled transition annotations. Supply a point-scoped correlated bundle,
   monotonic journal, and snapshot-composition helper, while leaving concrete
   service values and domain assertions project-owned.
4. **Enforce provider signatures (`DEF-003`).** Generate command/result
   signature checks and a static type-check rung; runtime-checkable Protocols
   currently prove method presence, not arity or result types.
5. **Fix replay environment provenance (`DEF-001`).** Preserve the originating
   virtualenv interpreter rather than resolving its symlink, and regress with a
   dependency-bearing provider.
6. **Measure actual fuzz contribution.** Add optional collect/continue runs and
   data-dependent mutants while preserving exact first-failure replay. Report
   discovery iteration and marginal kills beyond iteration zero.
7. **Standardize bypass declarations and stronger rungs.** Treat monkeypatches
   as compatibility boundaries, add passive probes, and use process/network or
   real-service validation where escaping the boundary matters.
8. **Defer a universal response-plan DSL.** Standardize only semantic fields
   that recur across additional domains; a universal wire-response schema would
   move implementation detail into TLA+.

## Java decision

Do Python first. Add Java only after coverage disposition, parser parity,
semantic effect plans, signature conformance, and replay provenance stabilize.
The preferred Java shape is JVM-native typed providers plus a small external
case-entrypoint protocol. Python may orchestrate or exchange a language-neutral
case envelope, but it should not be the default implementation of Java effects:
that would add process entrypoints while losing native interception and type
fidelity.

## Explicit limits of the recommendation

- Python batch execution only; no Java runner, streaming campaign, or universal
  cross-language interception is validated.
- Fixed preregistered mutant catalogs only; no exhaustive cross-product,
  Hypothesis shrinking, arbitrary TLA+ response synthesis, or statistically
  measured fuzz discovery power.
- Monkeypatch coverage is boundary-specific: `urllib` and raw sockets bypassed
  `requests.Session.send`; passive guards and a loopback/process rung made that
  limitation visible, not impossible.
- Providers can become duplicate semantic implementations when generated cases
  omit order, cardinality, command, response-class, or projection metadata.
- Python runtime Protocol checking is structurally incomplete, manifest
  generation is still dependency-sensitive in the shared path, and replay has
  a dependency-bearing virtualenv provenance defect.
- Real filesystem and HTTP loopback behavior were exercised; Kafka, SMTP, and
  production-service equivalence were not.
- The aggregate mutation score does not waive any gap in the formal coverage
  audit.

Detailed measurements and artifact provenance are in
[`examples/effect_providers/RESULTS.md`](../../examples/effect_providers/RESULTS.md)
and
[`examples/effect_providers/RESULTS.json`](../../examples/effect_providers/RESULTS.json).
