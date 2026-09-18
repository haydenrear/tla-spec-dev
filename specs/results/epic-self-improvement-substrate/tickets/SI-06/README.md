# SI-06 — validation evidence

Ticket `SI-06` (issue #339), branch `feature/339-skills-propose`, worktree
`/Users/hayde/IdeaProjects/wt-339-skills-propose`, branched from
`origin/epic/self-improvement-substrate` at **994f650c**.

The change is markdown-only: ten `.md` files under `skills/`, plus three rows
appended to `specs/results/deferred_findings_final.yaml`. Nothing under `specs/`
outside `results/` was touched, and no spec ticket was opened, closed, or
promoted — the epic agent owns the model for this epic
(`planning_rules.model_ownership_rule`).

**Baselines were recorded before the first edit** and every comparison below is
**by failure NAME, never by count.**

## The REQUIRED validation matrix

| Entry | Command | Result |
|---|---|---|
| `tlc` | — | `N/A` by the assignment: the epic agent owns the model and runs TLC on the desired state it scaffolds |
| `spec_unit` | `... run spec-unit-tests --ticket SI-06` | ran, and is **known-weak** — see below |
| `repository_unit` | `uv run --python 3.12 --with pytest --with pyyaml --with jinja2 --with hypothesis python -m pytest tests -q --ignore=tests/test_score_tools.py` | baseline 10 failed / 1594 passed / 5 skipped (461.92s) → after **10 failed / 1594 passed / 5 skipped** (390.99s), **same ten names** |
| `graphs: [cliWorkflow]` | `python3 skills/test-graph/scripts/run.py cliWorkflow` | **BUILD SUCCESSFUL**, exit 0 |
| `spec_graph: specWorkflow` | `python3 skills/test-graph/scripts/run.py specWorkflow` | **BUILD SUCCESSFUL**, exit 0, 9/9 nodes |

## The spec-unit entry, and which target actually ran

`run spec-unit-tests --ticket SI-06` is weak exactly as `SIS-KICKOFF-F-04`
describes, and this ticket reproduced it: the command printed **two**
`spec-unit target:` lines and executed only the first
(`specs/current`), returning on its non-zero exit. The ticket-local target was
never run by that command. Recorded verbatim in
`baseline-spec-unit-ticket-SI-06.txt`.

So both targets were run **explicitly**, and both are reported:

| Target | Command | Baseline | After |
|---|---|---|---|
| `specs/tickets/SI-06/desired` | `--target specs/tickets/SI-06/desired` | 7 failed / 46 passed | 7 failed / 46 passed |
| `specs/current` | `--scope project` (baseline came from the `--ticket` run, same target) | 7 failed / 49 passed | 7 failed / 49 passed |

**The same seven names, before and after, on both targets** — all pre-existing:

- `test_tla_spec_dev_budgets_adapter.py::test_record_budgets_adapter_emits_defaults_and_prompt`
- `test_tla_spec_dev_complexity_ledger_adapter.py::test_close_records_delta_jointly_with_retention_and_refinement`
- `test_tla_spec_dev_complexity_ledger_adapter.py::test_unfilled_ledger_template_refuses_the_close`
- `test_tla_spec_dev_complexity_ledger_adapter.py::test_decrease_with_degraded_validated_refactor_evidence_is_rejected`
- `test_tla_spec_dev_complexity_ledger_adapter.py::test_validated_decrease_with_not_run_fuzzing_members_is_recorded`
- `test_tla_spec_dev_ticket_adapter.py::test_open_ticket_adapter_drives_cli_ticket_workspace`
- `test_tla_spec_dev_update_ticket_adapter.py::test_update_ticket_current_executes_case_end_to_end`

## Repository unit — the ten pre-existing failures, by name

- `tests/test_architecture_tags.py::test_the_same_tag_control_holds`
- `tests/test_corpus_diagnostics.py::test_cli_passes_on_the_committed_example_corpus`
- `tests/test_example_drivers_write_inside_spec_tree.py::test_a_validation_run_does_not_generate_over_a_committed_corpus`
- `tests/test_instrument_demonstrations.py::test_every_fast_demonstration_reproduces`
- `tests/test_negative_corpus_adapter_conformance.py::test_the_negative_corpus_names_its_arguments_as_the_committed_corpus_does`
- `tests/test_source_citations.py::test_every_line_citation_resolves_to_the_line_it_cites[specs/current/spec_manifest.yaml]`
- `tests/test_source_citations.py::test_every_line_citation_resolves_to_the_line_it_cites[specs/desired_program_model/spec_manifest.yaml]`
- `tests/test_source_citations.py::test_every_line_citation_resolves_to_the_line_it_cites[specs/program_model/spec_manifest.yaml]`
- `tests/test_ticket_retirement.py::test_repository_canonical_delivered_plan_has_matching_close_receipts`
- `tests/test_verdict_schema.py::test_the_corpus_gate_states_its_verdict_as_data`

## Goal signal

`GOAL-blockers-propose`'s `local_signal` was **not run**, with the reason and the
exact command that would run it recorded in
`local-signal-GOAL-blockers-propose.md` and filed as `SI-06-DF-01`.
`GOAL-epic-owns-the-model` declares `N/A: the boundary is measured over ticket
PRs by SI-08`.

## Files

| File | What it is |
|---|---|
| `baseline-spec-unit-ticket-SI-06.txt` | the assignment's spec-unit command, before any edit — and the proof it ran one of two targets |
| `baseline-spec-unit-target-SI-06.txt` | ticket-local target, before |
| `after-spec-unit-target-SI-06.txt` | ticket-local target, after |
| `after-spec-unit-project.txt` | `specs/current`, after |
| `baseline-repository-unit.txt` / `after-repository-unit.txt` | repository suite, before and after |
| `graph-discover.txt` | the three registered graphs and their nodes |
| `graph-cliWorkflow.txt` / `graph-specWorkflow.txt` | the two REQUIRED graph runs |
| `local-signal-GOAL-blockers-propose.md` | why the local signal was not run, and what would run it |
| `front-door-refusal.txt` | `skt ticket new` refusing and rolling back, exiting 0 (`SI-06-DF-02`) |
| `front-door-byhand-bootstrap.txt` | the by-hand route that did work, with `--allow-unprojected` |
| `git-exclude-hides-evidence.txt` | `/specs/` in the clone's shared exclude hides all new evidence (`SI-06-DF-03`) |

Every file in this directory had to be committed with `git add -f`; see
`SI-06-DF-03`.
