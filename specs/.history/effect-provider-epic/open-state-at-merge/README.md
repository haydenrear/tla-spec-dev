# effect-provider-epic — open workflow state preserved at merge (2026-07-22)

The effect-provider epic merged into epic/complexity-descriptor with its spec
workflow still OPEN: EP-01..EP-06 done, coverage audit recorded FAIL with 12
in-scope hard gaps (all in the examples/effect_providers application models,
not the SDK), and **promotion_blocked: true** — the branch itself declares the
effect-provider example models must NOT be promoted into specs/program_model
as-is. That record is preserved verbatim here (the merged live workflow files
belong to complexity-descriptor-main-readiness). Audit report:
specs/results/coverage_audit_report.md (their lineage); contract reduction:
specs/results/effect_provider_contract_reduction.md. The 12 gaps stand
unwaived; repeated example validation must keep reporting both SDK behavior
and per-application costs.
