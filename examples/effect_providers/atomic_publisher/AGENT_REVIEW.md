# Fresh agent review: atomic publisher

## Outcome

An agent can implement and validate this repository's effect boundary through
the one generic `EffectProvider.bind(context)` interface. The framework does
not need filesystem semantics. `FilesystemPort` is generated from this
project's manifest; `AtomicFilesystemProvider` is project code that selects
concrete representatives, yields a typed binding, asserts its local protocol,
and cleans up its point-local state.

The canonical passing evidence is
`evidence/validation-runs/agent-ep06-atomic-v2/result.json`. The initial `v1`
run is intentionally retained: macOS sandboxing denied TLC's local RMI
listener before model checking, and the non-overwriting runner recorded that
environment failure. Re-running `v2` with local-listener permission required
no code or model change.

## Measured validation

| Measure | Result |
| --- | --- |
| Complete validation | 9.712 seconds |
| Regeneration | 1.855 seconds; 120-second hard bound |
| Generated cases | 14 total: 7 internal and 7 external |
| Green control points | 224 across two scored repetitions |
| Fixed mutations | 24/24 killed across two repetitions |
| First-discovery replay | 12/12 exact, including clean provider exit |
| Cleanup | 392/392 points clean; zero leaked paths |
| Real filesystem rung | 7/7 modeled outcomes matched |
| Focused tests | 7/7 passed in 3.414 seconds |
| Framework changes during the example run | 0 |

The two repetitions produced identical transcript and verdict digests. The
provider point runtime was about 3.9--4.1 ms at p50 and 6.2--6.5 ms at p95.
The four-scenario handwritten baseline killed 10/12 mutations; generated
failure outcomes supplied the two missing detectors.

## Oracle ownership

TLA+ owns:

- the seven semantic outcome classes;
- status, revision, and idempotence;
- the symbolic record state; and
- the ordered effect trace, including application-owned staging cleanup.

The repository provider owns:

- Unicode, whitespace, multiline, and control-character representatives;
- concrete paths, payloads, unrelated files, insertion order, and the
  `OSError` subclass within a modeled failure class;
- the canonical-byte refinement back to symbolic record state;
- the strict read/write/replace/delete journal; and
- point-local state acquisition, active-binding accounting, and cleanup.

Passive or external observation owns:

- detection of physical-file bypasses under the bounded provider root;
- the separate real-`TemporaryDirectory` conformance rung; and
- the child-process CLI projection of result and filesystem artifacts.

This separation is the useful design pressure. TLA+ does not become a script
for operating a filesystem, while the provider cannot redefine a modeled
outcome to make a concrete run pass.

## Cost and benefit

The measured application is 146 lines. Its effect implementation is 336 lines,
the case adapter is 79 lines, and the model/manifest/action metadata measured
306 lines. The preregistered mutation and regeneration machinery is much
larger than the application because it records detector attribution, exact
replay, provenance, cleanup, real-boundary conformance, and a fixed research
catalog. This is deliberately an information-rich experiment, not a claim
that every repository needs a mutation-study harness of this size.

EP-06 added a 323-line repeatable evidence wrapper and a 23-line usage
descriptor. That wrapper is substantial duplicated mechanics: subprocess
bounds, append-only evidence, result normalization, and failure recording.
If the same pattern survives the other examples, the generic evidence runner
is a candidate for reuse. The concrete filesystem binding is not: its path
rules, protocol journal, symbolic projection, and fault representatives are
application semantics.

The benefit is also more than the two additional mutation kills. Output
equality caught response defects, projected state caught byte/content defects,
and the provider journal caught atomic-write protocol defects that could leave
the same final bytes. Exact replay and per-point cleanup make those failures
cheap for a later agent to reproduce.

## Limitations

- The passive audit observes only in-process physical files under the
  provider-owned root. It does not intercept native code, child processes, or
  arbitrary host paths.
- The adapter still maps each scenario to `expected_revision`; the generated
  case does not carry a normalized application command plan. This is semantic
  duplication outside the provider.
- Sixteen deterministic representatives amplify an oracle; they are not
  exhaustive search and provide no automatic shrinking.
- The real filesystem rung injects bounded errors rather than inducing every
  operating-system failure mode.
- TLC needs permission to create its local listener in this environment. The
  failed `v1` evidence distinguishes that host constraint from a model error.

## Recommendations

1. Keep the library boundary at the single generic provider interface. Do not
   promote this filesystem implementation.
2. Watch the repeated non-overwriting evidence-wrapper pattern across all
   three projects. Promote only stable, domain-neutral orchestration and result
   validation after comparing those uses.
3. Consider generated command-plan metadata when application inputs are
   otherwise reconstructed from a scenario. That would remove the adapter's
   duplicated `expected_revision` mapping without moving implementation
   details into TLA+.
4. Preserve provider-local journals as explicit repository oracles. Final
   output and state alone cannot establish effect ordering or call cardinality.
5. Keep bypass claims bounded and machine-readable in
   `effect_provider_usage.yaml`; process and native boundaries require their
   own real integration rung.
