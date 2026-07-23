# MF-015 complexity delta and behavior-retention evidence

Recorded jointly, per the standing objective in
`references/architecture_tractability.md`. The mechanized ledger arrives with
MF-019; this is the manual record until then.

## Complexity delta: ZERO, measured

Baseline taken from the epic tip at branch time (58f5477), not from any quoted
figure. Measured before and after the ticket's implementation on the same
ticket-local model.

| figure | baseline (58f5477) | after MF-015 | delta |
|---|---|---|---|
| state variables | 7 | 7 | 0 |
| declared state-space bound | 34,992 | 34,992 | 0 |
| budget | 1,000,000 | 1,000,000 | — |
| TLC states generated | 87,464 | 87,464 | 0 |
| TLC distinct states | 9,011 | 9,011 | 0 |
| search depth | 24 | 24 | 0 |
| actions | 12 | 12 | 0 |
| graph modularity Q | 0.000 | 0.000 | 0 |

Evidence: `tlc.txt`, `complexity.txt`.

The delta is zero because the model delta is zero. That is a deliberate,
reasoned decision rather than an omission, and the reasoning is recorded in
`specs/tickets/MF-015/current/spec_manifest.yaml` under
`status.current_slice.model_change` and `deviation_from_planned_scope`.

Short form: MF-015's three gates live in
`scripts/run_generated_case_adapters.py` (external view) and
`scripts/export_testgraph_cases.py`, both of which the **Test Graph** invokes.
No command modeled by `TlaSpecDevCli.tla` reaches them — `run spec-unit-tests`
drives `--view internal` against `case_adapters.toml`, and no modeled CLI
command reads a `testgraph_bindings.yml`. Modeling a `channel_enforcement`
variable would have required inventing a `tla-spec-dev` subcommand that does
not exist in order to have something to set it, at a cost of roughly 3x on the
declared bound, for a fact no modeled command can observe.

The issue anticipated a gate and noted the headroom to afford one. The
measured answer is that this ticket's gates are not gates *on the modeled
program*. Reporting 0 is the measurement, not an avoidance of it.

## Behavior retention

No behavior was removed, so retention is total. Positive evidence:

| check | result |
|---|---|
| TLC on ticket-local current | 87,464 generated / 9,011 distinct / depth 24, no error — identical to baseline in all three figures |
| all 12 invariants | retained by name, none weakened |
| repository unit suite | 226 passed (196 baseline + 30 new) |
| spec-unit tests (MF-015) | 27 + 24 passed across 2 targets |
| specWorkflow graph | 8/8 nodes passed |
| cliWorkflow graph | 2/2 nodes passed |

Identical generated-state and distinct-state counts together rule out the
deleted-self-loop signature that a distinct-state check alone cannot see.

The three pre-existing repository unit tests that changed
(`test_non_batch_generated_program_runs_projected_state_assertion`, and the two
corpus-diagnostics export tests) were migrated, not weakened: each now supplies
the external contract the new schema requires, and each still asserts exactly
the behavior it asserted before (projected-state mismatch; cap-gate refusal
before selection; cap-gate pass). `test_export_external_case_as_testgraph_trace`
gained assertions rather than losing any.

## Refinement search

Searched. The only reduction `analyze complexity` reports is:

> projecting `[lastCommand, result]` removes them from the model; legitimate
> IFF the mutation kill rate holds afterwards

That move is **explicitly owned by MF-016** and is deferred by owner direction:
it is legitimate only once a kill rate exists to hold, and kill-test runs are
deferred epic-wide to MF-023. It is not implemented here.

Beyond it: **searched, found none.** No further reduction exists within this
ticket's scope. The two standing findings —

- `C1 has 7 variables, exceeding max_component_variables 6`
- `C1 is touched by 12 actions, exceeding max_component_actions 8`

— are unchanged and were neither worked around nor renegotiated. Both are true
findings about the undecomposed single-module baseline and are resolved at the
root by MF-023's Internal/External decomposition. The budget gate remains FAIL,
exactly as it was at the epic tip.

## Architectural recommendations (owner approval required, not applied)

1. **A shared external-contract module already paid off.** The gates live in a
   new `scripts/testgraph_channels.py` rather than being duplicated across the
   two entry points, so the runner and the exporter cannot drift into enforcing
   different rules. Recommend the same treatment for any future gate that more
   than one entry point must apply.
2. **`external.production_package` is per-bindings-file today.** If MF-023's
   decomposition introduces multiple external views, this may want to move to
   `spec_manifest.yaml` so one program declares one production package. Not
   done here: it would couple this ticket to the manifest schema for no
   present benefit, and MF-023 is where the view structure is decided.

Neither is applied. Both are recommendations for the owner.

## Complexity NOT added — the anti-gaming note

The zero delta was not obtained by under-representing the program. What MF-015
adds is real and is fully covered by tests: 30 new repository unit tests, of
which the load-bearing one writes a Test Graph adapter that illegally imports
the production package and asserts the gate catches it with the adapter, the
offending import, and the remediation. The work is represented in test
evidence and documentation rather than in model dimensions because it is not
behavior of the modeled program.
