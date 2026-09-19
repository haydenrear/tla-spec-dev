# Regression, compared by failure NAME (never by count)

## Repository suite
`uv run --python 3.12 --with pytest --with pyyaml --with jinja2 --with hypothesis python -m pytest tests -q --ignore=tests/test_score_tools.py`

BASELINE (taken before the first edit): 10 failed, 1647 passed, 6 skipped.
AFTER:                                  10 failed, 1653 passed, 6 skipped.

Identical names, both runs:
  test_architecture_tags::test_the_same_tag_control_holds
  test_corpus_diagnostics::test_cli_passes_on_the_committed_example_corpus
  test_example_drivers_write_inside_spec_tree::test_a_validation_run_does_not_generate_over_a_committed_corpus
  test_instrument_demonstrations::test_every_fast_demonstration_reproduces
  test_negative_corpus_adapter_conformance::test_the_negative_corpus_names_its_arguments_as_the_committed_corpus_does
  test_source_citations::test_every_line_citation_resolves_to_the_line_it_cites[specs/current/spec_manifest.yaml]
  test_source_citations::test_every_line_citation_resolves_to_the_line_it_cites[specs/desired_program_model/spec_manifest.yaml]
  test_source_citations::test_every_line_citation_resolves_to_the_line_it_cites[specs/program_model/spec_manifest.yaml]
  test_ticket_retirement::test_repository_canonical_delivered_plan_has_matching_close_receipts
  test_verdict_schema::test_the_corpus_gate_states_its_verdict_as_data

NEW FAILURES: none. The 10 are the epic owner's known set.

## Spec-unit (--ticket SI-09)
BASELINE: 7 failed, 49 passed.   AFTER: 7 failed, 49 passed. Identical names:
  test_tla_spec_dev_budgets_adapter::test_record_budgets_adapter_emits_defaults_and_prompt
  test_tla_spec_dev_complexity_ledger_adapter::test_close_records_delta_jointly_with_retention_and_refinement
  test_tla_spec_dev_complexity_ledger_adapter::test_unfilled_ledger_template_refuses_the_close
  test_tla_spec_dev_complexity_ledger_adapter::test_decrease_with_degraded_validated_refactor_evidence_is_rejected
  test_tla_spec_dev_complexity_ledger_adapter::test_validated_decrease_with_not_run_fuzzing_members_is_recorded
  test_tla_spec_dev_ticket_adapter::test_open_ticket_adapter_drives_cli_ticket_workspace
  test_tla_spec_dev_update_ticket_adapter::test_update_ticket_current_executes_case_end_to_end

## Test graphs: UNMEASURABLE in a ticket worktree
cliWorkflow, specWorkflow, effectProviderExamples cannot run here, and are NOT
reported green. Measured cause: test_graph/settings.gradle.kts:2 declares
`includeBuild("build-logic")`, while test_graph/build-logic is gitignored
(test_graph/.gitignore:30), tracked by 0 files, and absent from disk. No
workaround was attempted (SI-12-DF-05).
