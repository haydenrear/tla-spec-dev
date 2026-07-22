# Atomic publisher findings

## Decision

Formal result: **GO** — both preregistered repetitions passed every gate.

The preregistered go threshold is an unmutated green control, all seven
outcomes, AP-01..AP-08 killed by their expected detector, at least 10/12 total,
exact replay/cleanup, green real-filesystem conformance, and zero framework
changes.

## Measured result

| Measure | Result |
| --- | --- |
| Generated model | 14 generated / 14 distinct states, depth 2, 7 internal + 7 external cases |
| Effectful score | 12/12 in both repetitions; every expected detector fired |
| Hand-written four-scenario baseline | 10/12; AP-05 and AP-07 survive because their failure outcomes are absent |
| Generated points per control repetition | 112 (7 cases × 16 deterministic representatives) |
| Provider point runtime p50 / p95 | 3.303 / 5.504 ms; 3.211 / 5.354 ms |
| Deterministic repetition digests | transcript `784a96c0…` and verdict `35b89899…` identical twice |
| First-discovery replay | 12/12 exact transcript digests |
| Real `TemporaryDirectory` conformance | 7/7 outcomes green; directory removed after every scenario |
| Cleanup/isolation | 392 points checked, 8 bypass files detected/removed, zero leaked paths, all provider state clean |
| Forbidden framework changes since preregistration | 0 by diff + untracked audit against `141e63b` |

## Cost/benefit

The useful gain is not raw random data. It is the composition of three small,
independent oracles around one generated case:

1. output equality finds wrong statuses and revisions;
2. exact-byte-to-symbolic state projection finds content/state corruption;
3. the provider journal finds atomic-write protocol mistakes even when final
   bytes happen to be correct.

Explicit injection stayed local: the application imports only the generated
port, and the framework learned no filesystem semantics. Ten edit/run loops
covered terminal-state TLC config, portable YAML, canonical generated imports,
action-collapse proof, sampled detector attribution, replay evidence,
replay-proof hardening, and the final audit gate. The first green evidence
pass compared only replay transcript digests; review strengthened the accepted
pass to also require a nonzero return, identical structured failure, and clean
provider exit. That stronger gate then exposed two evidence defects before
integration: the checker selected the first of multiple same-point diagnostics,
and AP-12 error text contained its ephemeral work path. Exact diagnostic
selection and provider-relative paths made the proof reproducible without
changing a mutant, detector, case, or threshold. The ordinary baseline cannot kill AP-05 or AP-07 because no
hand-written scenario drives read or replace failure; generated outcome
coverage makes those gaps structural.

A second review found that cleanup evidence had been asserted after
`shutil.rmtree(..., ignore_errors=True)` and then reported from a constant empty
list. The accepted evidence removes silently only when removal succeeds,
records any actual survivors, makes replay depend on that observation, and
binds the raw result to digests of the measured application, provider, adapter,
and scorer sources.

Review also caught a production bug the original oracle omitted: replace
failure left the staging file behind, while real-filesystem conformance passed
only because `TemporaryDirectory` later erased the whole harness root. The
follow-up models `delete_stage` in the TLA-derived trace, deletes the stage in
production before returning, makes the strict provider reject a surviving
stage, and observes stage absence before real-filesystem teardown. Cleanup
semantics must live in generated effect plans/cases; harness teardown is not an
application cleanup oracle.

The adapter also duplicates one piece of semantics: it maps each scenario to
an expected revision because the generated case fixes terminal state but does
not carry a normalized application command plan. That is small here, but it is
the same architectural pressure that becomes response/order logic in the
multi-provider example. Generated effect-plan metadata should own this input
semantics so adapters translate data instead of reimplementing the outcome.

## Findings that remain visible

- AP-04 and AP-08 can trigger both projected-state and provider-journal
  detectors. Attribution records every detector; it does not hide redundancy.
- AP-09 and AP-10 may also yield response/state mismatches in failure cases,
  but their protocol violation remains independently visible.
- AP-12 proves only a bounded in-process filesystem bypass audit under the
  provider-owned root. It is not universal interception of child processes,
  native code, or arbitrary host paths.
- TLA+ selects the semantic class; the provider chooses representatives. New
  error semantics still require a new modeled outcome instead of more fuzz
  iterations.
- V0 stops a mutant campaign after its first complete failing iteration, so
  each killed mutant ran 7 points; the green control proves full 7×16 coverage.

## Recommendations

1. Keep explicit injection the preferred effect-provider path. It produced the
   lowest coupling and made cleanup/type checks straightforward.
2. Add opt-in collect/continue mode after a failing iteration so mutation runs
   can measure all 16 representatives; V0's seven-point early stop is not a
   score defect. Keep a stable point/detector evidence API, not a filesystem
   response DSL.
3. Make generated provenance and distinct action/outcome coverage a standard
   pre-campaign gate. This caught the class of helper-action collapse before a
   mutation score could become misleading.
4. Treat provider-local journals as first-class oracles alongside output and
   projected state. Final-state comparison alone cannot kill AP-09 or AP-11.
5. Report capability limits rather than promising universal monkeypatching.
   Process/JVM effects need a language/runtime bridge or real service boundary.
