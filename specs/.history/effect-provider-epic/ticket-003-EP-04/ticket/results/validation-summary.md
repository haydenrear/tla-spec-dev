# EP-04 validation summary

## Contract

- `EffectProvider.bind(context)` is the only accepted provider shape.
- Callable-only providers fail during configuration preflight.
- The entered value is checked against the selected generated port or may be
  `None` for a self-installed bounded integration.
- The framework retains deterministic seeds, lifecycle, cleanup, immutable
  case-oracle protection, diagnostics, and exact replay.
- Scaffolds and public instructions contain no framework-owned domain helper.
- `effect_provider_usage.yaml` records repository-local state, fuzz,
  assertions, cleanup, and bypass limits.

## Results

- Focused provider/scaffold suite: 120 passed.
- Repository suite on Python 3.14 with PyYAML: 608 passed.
- Spec units: current 63 passed; ticket current 60 passed.
- TLC: no error; 5,619,356 generated, 231,621 distinct, depth 25.
- `specWorkflow-20260722-225756-ae36ce03`: 8/8 nodes and 64/64
  assertions passed.
- `cliWorkflow-20260722-225818-b3761682`: 2/2 nodes and 41/41
  assertions passed.
- Skill-manager local install dry-run: exit 0, five planned effects, no
  mutations. Telemetry export was sandbox-blocked after validation and did not
  affect the result.

An unqualified repository-wide `pytest` invocation collected duplicated
workflow snapshots and failed during collection, as expected for this
repository layout. The supported `tests/` suite is the recorded repository
validation.

Running that suite through the host Python 3.10 `uv run` wrapper reproduced the
known child-interpreter dependency loss tracked as EP-05/DEF-001. The same
suite passed under Python 3.14, whose standard library supplies TOML parsing.
