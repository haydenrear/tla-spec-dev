# EP-01 validation summary

## Contract exercised

- Strict lookup is `case.input.action` -> `actions.yml effect_ports` ->
  `spec_manifest.yaml` ports with `role: effect` ->
  `[effect_providers.<Port>] provider`.
- Generated port Protocols are runtime-checkable. Provider references, table
  shape, required/missing/orphan/duplicate/unknown ports, and every coverage
  case are preflighted before adapter instantiation.
- Provider scopes are constructed only after their per-case work directory
  exists, enter in declaration order, remain active through
  setup/run/assert/teardown, and exit in reverse order on success and all tested
  failure combinations. A provider `__exit__` cannot suppress a primary failure.
- `AdapterCaseContext.effects` and projected assertion effects are fresh,
  immutable mappings. Explicit binding values are structurally checked against
  the selected generated Protocol; `None` supports a self-installed patch.
- Generated case `before`, `input`, `output`, and `after` are deep-snapshotted
  and checked throughout binding and execution so a provider cannot mutate the
  oracle into a tautology.
- Empty semantic schemas preserve legacy cases (including `input=None`). The
  inherited passive `effects:` sandbox remains separate and is tested both alone
  and simultaneously with semantic providers.
- A real subprocess CLI test generates the Protocol package from a real manifest
  under the spec's generated root while keeping the case package/mapping outside
  the spec. It proves explicit `--spec-dir` survives batch re-exec, malformed
  unselected cases still fail coverage-wide preflight, and provider-bearing
  non-batch mode refuses before creating a program/work directory.

## Results

- Repository suite: 561 passed, 2 skipped in 8.37s
  (`repository-unit-tests.txt`).
- Ticket workflow spec-unit tests: 63 current + 60 EP-01-current passed
  (`spec-unit-tests.txt`).
- TLC, externally bounded to 120s: 5,619,356 generated / 231,621 distinct /
  depth 25 / no errors / 11s (`tlc-current.txt`).
- Test Graph `specWorkflow`: 8/8 nodes passed; run
  `specWorkflow-20260722-022801-d6bb9143`.
- Test Graph `cliWorkflow`: 2/2 nodes passed; run
  `cliWorkflow-20260722-022830-2e10191c`.
- Ticket `current/` equals `desired/`; rationale is in
  `zero-model-delta.md`.

## Intentional V0 boundaries

- An entered value can only be structurally checked immediately after
  `__enter__`, before per-case adapter setup/run. Static references, callables,
  and context-manager shape are preflighted before `setup_all`; pre-entering
  per-case monkeypatches would overlap cases or double-enter scopes.
- Response-plan/fuzz orchestration and authored library providers are EP-02.
- Provider-bearing non-batch/export and non-Python execution fail closed in V0.

Deferred findings: none beyond these planned EP-02/V0 boundaries.
