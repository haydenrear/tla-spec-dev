# CD-10 manifest reconciliation — audit run 3 gaps R3-2, R3-3, CD09-DF-2, CD09-DF-3

Ticket: CD-10 (GitHub #85). Report resolved against:
`specs/results/epic-close/coverage_audit_report_run3.md`. Zero TLA+ model
delta: `TlaSpecDevCli.tla`, `MC.cfg`, and `MCsmall.cfg` are byte-identical to
the CD-09 baseline. Every claim below was re-verified in code before the
manifest was changed.

## R3-2 — CloseTicket's destructive deletes: port `spec_tree_delete`

New port on `TlaSpecDevCliPort`: `spec_tree_delete`, type
`filesystem.delete`, target `**/specs/**`, attached to `CloseTicket`.

Verified sites (all reached from the shipped `close` dispatch,
`tla_spec_dev.py` dispatch table; all three named per the audit's
"destructive sites are never grouped" rule):

| Site | What it deletes | Reached via |
|---|---|---|
| `scripts/spec_evolution.py:154` (`shutil.rmtree(state_dir)` in `remove_state_directories`) | TLC `states/` scratch dirs under the spec tree | `:707` (ticket close), `:851` (workflow close) |
| `scripts/spec_evolution.py:385` (`shutil.rmtree(dst)` in `replace_tree`) | project `current/` before promotion — the GitHub #22 data-loss mechanism | promotion path (`:528`) |
| `scripts/spec_evolution.py:477` (`target.unlink()`) | seeded paths the ticket dropped | promotion path |

All three targets live under the spec tree, so one honest
`**/specs/**` delete port covers them; the schema distinguishes
`filesystem.delete` from `filesystem.write` precisely so these could not
keep hiding under `spec_tree`.

## R3-3a — RunSpecUnitTests' case-runner spawn: port `runner_process`

New port `runner_process`, type `process.spawn`, target
`*run_generated_case_adapters*`, attached to `RunSpecUnitTests` alongside
`test_process`.

Verified: `scripts/tla_spec_dev.py:313-339` builds the command
`[sys.executable, .../scripts/run_generated_case_adapters.py, ...]` for each
generated case package and `:358` executes it (`subprocess.run`). That
command line does not match `test_process`'s `*pytest*` — only the
`uv run --with pytest -m pytest` child built at `:296-303` does. A separate
port was chosen over widening `test_process`'s target because the two spawns
are different programs with different failure modes; a `*` -shaped widening
would be dishonest.

## R3-3b — CloseTicket's git spawn: port `git_metadata`

New port `git_metadata`, type `process.spawn`, target `git rev-parse*`,
attached to `CloseTicket`.

Verified: `scripts/spec_evolution.py:99` (`subprocess.run(["git", *args],
...)` in `git_value`) is reached from `git_metadata()` at `:801` (ticket
close manifest) and `:903` (workflow close manifest). Every query is a
`git rev-parse` variant (`--is-inside-work-tree`, `--abbrev-ref HEAD`,
`HEAD`), so the target is exact, not a wildcard-everything. The fail-open
branch on git error remains out-of-model per the amended scope; the spawn
itself is now declared.

## No dead port, no remaining undeclared spawn/delete

- Grep-level sweep of the shipped dispatch surface: the only subprocess
  sites reached from modeled actions are the `-m pytest` child
  (`test_process`), the case-runner spawn (`runner_process`), TLC-free
  analyze (no spawn — CD-09 G4 removal stands), and the git provenance
  spawn (`git_metadata`). The only delete sites reached from modeled
  actions are the three R3-2 sites (`spec_tree_delete`).
- Every declared port maps to a real code path of an action it is declared
  for: `spec_tree`/`evidence_report`/`cli_artifact`/`test_process`
  (pre-existing, re-verified by audit run 3), `spec_tree_delete`,
  `runner_process`, `git_metadata` (added here, sites above).
- The standalone wrapper scripts (`close_tickets.py` etc.) carrying their
  own deletes remain outside the declared "shipped CLI dispatch" scope —
  ESC-3 is an owner escalation recorded by the audit, not widened here.

## DF-2 — `RecordBudgets` row in effects.actions

Added `RecordBudgets: []` — an EMPTY row, not an absent one; the two are
different claims and only "performs no distinct effect" is true.
Verified: `budget_prompt` (`scripts/budgets.py:74-94`) only returns text,
printed at `tla_spec_dev.py:91` and `:118`; the `budgets:` block itself is
emitted at scaffold time under `ScaffoldProject`/`ScaffoldWorkflow`'s
`spec_tree`; recording user-negotiated values is an agent edit of the
manifest, not a program effect. This records the owner decision ESC-4 said
was still owed. `effects.actions` now covers all 14 modeled actions.

## DF-3 — dangling source_model references removed

Removed `program_model_core`, `program_model_internal`,
`program_model_external` (`spec_manifest.yaml:111-113`): the referenced
`../program_model/Core.tla`, `Internal.tla`, `External.tla` do not exist
(verified against `specs/program_model/`). Per the amended known_gaps
(ticket_plan.yaml, 2026-07-22/ESC-2): the MF-023 dogfooding decision NOT to
decompose stands (Q=0.012, no clean cut); the view split is unscoped future
work. The surviving references (`program_model_manifest`,
`desired_ticket_plan`) both resolve from `specs/current/`.

Note (deferred, not widened): `specs/program_model/spec_manifest.yaml` and
`specs/desired_program_model/spec_manifest.yaml` carry the same dangling
lines; they are outside this ticket's declared conflict surface
(`specs/current/*`) and are reconciled by the epic owner's
finalization/workflow-close step, as with CD-09 (`195b07d`).

## Kill catalog seeding

One fault per new port, verified `find` appears verbatim exactly once, and
`kill_test.required_boundaries` reports zero missing boundaries over the
amended manifest (7 ports + 14 invariants, all seeded):

- `port-runner_process` — the runner is spawned with `--validate-only`
  injected, so cases validate but never execute.
- `port-spec_tree_delete` — `replace_tree` never clears the destination, so
  dropped files persist as ghost state (the inverse of #22).
- `port-git_metadata` — provenance queries answered by `git --version`, so
  branch/commit provenance silently degrades.

Retention members remain non-gating and honestly `not_run` (CD-09 ruling);
the seeding keeps the catalog complete so a kill run over the amended
boundary refuses nothing.

## Budgets carry-through

`max_distinct_states: 500000` with the 2026-07-19 negotiated rationale block
is unchanged in ticket `desired/` and `current/` and is verified
post-promotion in project `specs/current/spec_manifest.yaml`. TLC on the
unchanged model: 283,805 distinct states (≤ 500,000), green —
`specs/tickets/CD-10/results/tlc_current.txt`.
