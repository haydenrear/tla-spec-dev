# EP-02 validation summary

## Contract exercised

- `--fuzz-runs`, `--seed`, and exact `--fuzz-iteration` replay run bounded,
  deterministic case/iteration campaigns. SHA-256-derived per-port seeds are
  stable across processes, filtering, ordering, and Python hash seeds.
- Every provider-bearing execution point receives fresh adapter/shared caches,
  bindings, immutable effect mappings, singleton batch hooks, sandbox, and
  stable opaque case/kind work paths. Raw generated names remain only in
  diagnostics and cannot traverse or alias work roots.
- Whole-corpus provider configuration and lazy binding preflight remains
  fail-closed before any application hook. Runtime provider scopes enter in
  declaration order and exit in reverse order on every tested path.
- Provider acquisition/cleanup is harness lifecycle outside passive effect
  observation. Adapter setup/run/assertion/teardown remains inside both the
  active providers and passive observation, so explicit bindings and installed
  patches are observed without temporary-root setup/cleanup becoming false
  application effects.
- `context_provider` and `temporary_root_provider` are lazy, fresh, and cleanup
  safe. Ordinary installer+cleanup failures retain a structured primary and all
  cleanup errors; control-flow `BaseException` primaries remain primary.
- Every retained failure phase emits structured seed/provider diagnostics and
  an absolute shell-safe command that reproduces exactly one case/iteration,
  including concrete provider-generated values.
- Project scaffolds place editable `providers.py` outside generated code and
  map it without framework changes. Documentation keeps TLA semantic outcomes
  separate from provider-owned concrete representations/state and states the
  limits: no universal interception, exhaustive cross-product, shrinking,
  service equivalence, or Java support is claimed.

## Results

- Repository suite: 615 passed in 11.30s (`repository-unit-tests.txt`).
- Focused provider correction: 5/5 passed; EP-01/EP-02 coexistence: 85/85.
- Independent re-review: 113 focused plus dynamic overlapping-patch, reverse
  multi-cleanup, hostile-path, BaseException, and evidence-reader reproductions
  passed (`review-correction.txt`).
- Spec units: 63 project-current + 60 EP-02-current passed across two targets
  (`spec-unit-tests.txt`).
- TLC, externally bounded to 120s: 5,619,356 generated / 231,621 distinct /
  depth 25 / no errors / 11s (`tlc-current.txt`).
- Test Graph `specWorkflow`: 8/8 nodes passed, run
  `specWorkflow-20260722-041253-08d64314`.
- Test Graph `cliWorkflow`: 2/2 nodes passed, run
  `cliWorkflow-20260722-041256-1050cff0`.
- Skill publish and local-install validation both passed in dry-run mode at
  `5b52a1d`; no global sync occurred (`skill-validation.txt`).
- Ticket `current/` equals `desired/`; rationale is in
  `zero-model-delta.md`.

## Intentional boundary

Fuzz depth and legal concrete response/state generation belong to each project
provider. EP-02 deliberately does not add a central response DSL, a universal
monkeypatch layer, Hypothesis shrinking/exhaustive claims, real Kafka/SMTP
services, or a Java runner. EP-03 measures this boundary with three diverse
projects before the epic recommends any broader abstraction.

Deferred findings: none.
