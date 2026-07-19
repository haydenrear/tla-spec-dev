# MF-015 — validations deferred to MF-023 (#30)

Recorded explicitly so the dogfooding ticket knows what it must exercise, per
the epic-wide spec-case execution deferral (owner direction, 2026-07-18).

The mechanism, its unit tests, and its adapters were built and validated. The
following were **not run** by this ticket:

1. **Case generation over the reachable state graph.** No external case corpus
   was generated from `TlaSpecDevCli.tla`. The `AnalyzeComplexity` budget gate
   is FAIL on the undecomposed baseline and refuses generation for exactly the
   right reason; it was not overridden with `--allow-over-budget`.
2. **The distilled-corpus run.** No generated external corpus was exported
   through the new gate. `export_testgraph_cases.py --bindings` was exercised
   against synthesized case packages in tests, not against a corpus generated
   from this repository's model.
3. **Effect-conformance sweep.** Not run.
4. **Mutation kill test.** Not run. This matters specifically for MF-015:
   the kill rate is what would demonstrate that the channel gate catches
   degenerate adapters *in a real corpus*, as opposed to in the fixtures this
   ticket asserts against.

## What MF-023 must exercise for MF-015 specifically

- Generate an external corpus and export it with `--bindings`, confirming the
  gate passes on a real `testgraph_bindings.yml` for the decomposed model —
  including that `external.production_package` is correctly `spec_double_compiler`
  for this repository, and that no real Test Graph adapter imports it.
- Confirm the `integration_rung` block in the exported `manifest.json` names a
  meaningful rung for the decomposed views, i.e. that this repository's real
  ports can actually be bound `double|real` and that at least one is `real`.
- Confirm the transitive import analysis produces no false positive against the
  real adapter tree, where adapters legitimately import
  `spec_double_compiler.runtime` for `CaseRunResult` while the declared
  production package is the CLI itself. This is the one place the base/harness
  distinction could bite, and fixtures cannot prove it.
- Once a kill rate exists, confirm that removing the channel gate lowers it —
  i.e. that the gate kills mutants rather than only rejecting fixtures.

## What was fully validated here and needs no rerun

- The channel field is required and its absence fails with remediation.
- Static, transitive import analysis catches direct, laundered, and dynamic
  (`importlib.import_module` / `__import__`) production imports, in all four
  adapter roles.
- `double|real` port bindings are required, validated, and an all-doubles
  configuration is rejected.
- Absent declarations fail rather than skipping the check; no override, skip,
  or force parameter exists on the gate.
- Both entry points enforce, including when `--view external` is omitted.
