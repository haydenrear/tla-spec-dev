# MF-012 Validation Summary

Ticket: MF-012 — Scaffold-time budget prompts
Epic: modular-fuzzing (`epic/modular-fuzzing`), wave 1, `depends_on: []`
Branched from pinned epic tip `cc765f61dbcf72032266545f24f33dc54747dd6b`

## Validation matrix

| Step | Command | Result | Evidence |
|---|---|---|---|
| TLC (ticket current) | `timeout 120 bash scripts/run_tlc.sh specs/tickets/MF-012/current/TlaSpecDevCli.tla specs/tickets/MF-012/current/MC.cfg` | PASS — 919 distinct states, depth 21, no error | `tlc-current.txt` |
| Spec-unit | `tla-spec-dev --spec-root specs run spec-unit-tests --ticket MF-012` | PASS — 8 + 10 passed, 2 targets | `spec-unit-tests.txt` |
| Repository unit | `uv run --with pytest -m pytest tests -q` | PASS — 117 passed | `repository-unit-tests.txt` |
| Test Graph `specWorkflow` | `test-graph/scripts/run.py specWorkflow` | PASS — 8/8 nodes | `graph-reports/specWorkflow-20260718-153853-c3144c6b/` |
| Test Graph `cliWorkflow` | `test-graph/scripts/run.py cliWorkflow` | PASS — 2/2 nodes | `graph-reports/cliWorkflow-20260718-153934-857a0f5c/` |

TLC was wrapped in an external 120s timeout per the `tlc_seconds` budget.

## What changed

**TLA+ model** (`TlaSpecDevCli.tla` + `MC.cfg`, ticket desired then current):
- new state variable `budgets_recorded`
- new action `RecordBudgets(root)` — enabled after `ScaffoldProject`
- `ScaffoldWorkflow` now requires `budgets_recorded`, so budgets are
  established before any generation action
- `ScaffoldProject` next-step result now points at `RecordBudgets`
- new invariants `BudgetsRequireProject`, `WorkflowRequiresBudgets`

**Production code:**
- `scripts/budgets.py` (new) — single source of truth for the documented
  defaults, `budgets_block()` YAML emitter, `budget_prompt()` negotiation
  instructions, and `load_budgets()` with documented-default fallback plus a
  warning. Reuses `extract_spec_manifest.load_manifest`, which already handles
  the PyYAML-absent fallback.
- `scripts/onboard_program_model.py` — `scaffold project` manifest now carries
  the `budgets:` block.
- `scripts/new_ticket_workflow.py` — `scaffold workflow` emits the block into
  both `current/` and `desired_program_model/` manifests.
- `scripts/tla_spec_dev.py` — both scaffold commands print the budget
  negotiation prompt (propose defaults, ask what to adjust, record a one-line
  rationale per changed value).

**Adapters / tests:**
- `RecordBudgetsAdapter` — runs the real scaffold into a temp dir and asserts
  the budgets block, the defaults, and the prompt instructions.
- `case_adapters.toml` maps `RecordBudgets`.
- `specs/tickets/MF-012/*/tests/test_tla_spec_dev_budgets_adapter.py` (new).
- `tests/test_budgets.py` (new, 11 tests), including a drift guard that fails
  if the defaults diverge from `references/modular_fuzzing.md`.

## Defects found and fixed

1. **Numeric coercion of `kill_rate_floor` (found while implementing).**
   The repository's minimal YAML fallback parser (used when PyYAML is absent)
   does not recognise floats, so `kill_rate_floor: 0.8` was returned as the
   string `"0.8"`. Any downstream numeric comparison — precisely what MF-016's
   kill-rate gate will do — would have raised `TypeError`. `load_budgets` now
   coerces each budget to the type of its default and falls back with a warning
   on anything non-numeric. Covered by
   `test_kill_rate_floor_is_numeric_under_the_fallback_parser`.

2. **Pre-existing stale single-module assertions (blocked the matrix).**
   Three spec-unit tests failed on the *unmodified* epic tip `cc765f6`:
   `test_scaffold_project_and_workflow_adapters_use_cli`,
   `test_open_ticket_adapter_drives_cli_ticket_workspace`, and
   `test_close_ticket_adapter_drives_cli_history_promotion`. All three asserted
   a single-module `CliProject.tla` that `scaffold project` has never emitted —
   the scaffolded baseline is the three-module `Core`/`Internal`/`External`
   model, so the assertions were unsatisfiable (drift left by the
   Internal/External split). Because `open ticket` copies these tests into the
   ticket-local workspace, they blocked MF-012's own matrix. Fixed minimally by
   asserting `Internal.tla`, the module the scaffold actually produces. No
   coverage was weakened — the assertions now check a file that really exists.
   This was outside MF-012's nominal scope but unavoidable to get a green
   matrix; flagging it explicitly for post-merge review.

## Standing objective

See `complexity-ledger.md`. Summary: this ticket's own delta is **+2 distinct
states** (a real behavior addition, reported as an increase, not a reduction).
A separate reduction **was** found and measured — collapsing the three parallel
ticket-progress flags into one ordinal `ticket_phase` yields -2 variables,
-13.1% generated states, and an 8x smaller declared state-space bound at an
identical 919 reachable states and identical depth 21. It is an architectural
move, so it is recorded as a **recommendation for user approval** and was not
applied.
