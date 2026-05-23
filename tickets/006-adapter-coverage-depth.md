# Adapter Coverage Depth

Mapping validation currently verifies that every label has some adapter. It does
not prove the adapter can handle every shape under that label.

Add optional adapter capability validation.

Acceptance criteria:

- Adapters can declare `can_run(case)`.
- Validation reports cases rejected by their mapped adapter.
- `--validate-only` can fail before any generated programs execute.
