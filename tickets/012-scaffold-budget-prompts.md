# Scaffold-Time Budget Prompts

Status: Open

Budgets are per-program and should be agreed with the user during
scaffolding, not hardcoded. Today the 120-second TLC rule is the only budget
and it lives in prose.

Add budget capture to `tla-spec-dev scaffold project`.

Acceptance criteria:

- Scaffold emits a `budgets:` block in `spec_manifest.yaml` with the
  defaults from `references/modular_fuzzing.md` (tlc_seconds,
  max_distinct_states, case caps, component-size heuristics,
  kill_rate_floor).
- Scaffold instructions tell the agent to propose the defaults to the user,
  ask which to adjust for this program, and record a one-line rationale per
  changed value.
- `analyze complexity`, case generation, and the adapter runner read their
  gates from the manifest budgets instead of hardcoded values.
- Missing budgets fall back to the documented defaults with a warning.
