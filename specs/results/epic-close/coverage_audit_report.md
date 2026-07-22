# Coverage Audit Report

- **Epic / workflow:** `complexity-descriptor-epic` (workflow close; tickets CD-01, CD-02, CD-03, all done)
- **Scope source:** `specs/desired_program_model/ticket_plan.yaml` (lines `534-549` service_catalog; `1996-1999`, `2073-2075`, `2143-2147` ticket implementation_scope; `516-525` planning_rules used for out-of-scope placement)
- **Model audited:** `specs/current/TlaSpecDevCli.tla` @ `a749cf1`
- **Date:** `2026-07-22`
- **Verdict:** `FAIL` — 7 in-scope gaps

> This audit checks **completeness of what is modeled**, not fidelity. The four
> oracles are bounded to what is already represented and cannot see this class
> of defect. See `prompts/coverage_audit.md`. Previous full audit (run 1,
> MF-026, 2026-07-19): `specs/.history/modular-fuzzing-epic/ticket-013-MF-026/results/coverage_audit_report.md`
> — used for comparison only; every enumeration below was re-run fresh.

---

## 0. Declared scope (quoted verbatim from the plan)

```yaml
# specs/desired_program_model/ticket_plan.yaml:534-549
service_catalog:
  existing_boundaries:
    - tla-spec-dev CLI (scaffold/open/run/close)
    - scripts/generate_cases_from_tlc_dump.py case generation
    - scripts/run_generated_case_adapters.py adapter runner
    - spec_manifest.yaml / actions.yml / testgraph_bindings.yml schemas
  desired_boundaries:
    - budgets block in spec_manifest.yaml read by all gates
    - analyze complexity pre-TLC gate
    - sandboxed effect observation in the adapter runner
    - channel-authentic Test Graph bindings with double|real port configurations
  adapter_boundaries:
    - specs/program_model/production_adapters.py spec-unit adapters
    - test_graph specWorkflow / cliWorkflow graphs
  known_gaps:
    - "This repository's baseline is a single TlaSpecDevCli.tla module without the Internal/External view split that SKILL.md mandates for onboarded projects. Originally recorded as out of scope for this epic. Owner direction 2026-07-18: it is now IN scope but scheduled LAST, as MF-023 at promotion_order 85, after every mechanism ticket has landed. [...] See references/migration.md and tickets/023-decompose-via-dogfooding.md."
```

```yaml
# specs/desired_program_model/ticket_plan.yaml:1996-1999 (CD-01)
    implementation_scope:
      - scripts/analyze_complexity.py (remove suggestion machinery; F1 alias resolution; F3 bound honesty)
      - tests/test_analyze_complexity.py (F1 regression test failing pre-fix; F3 coverage)
      - SKILL.md and references/architecture_tractability.md (descriptor is the surface)
```

```yaml
# specs/desired_program_model/ticket_plan.yaml:2073-2075 (CD-02)
    implementation_scope:
      - references/complexity_intuition.md (new doc)
      - SKILL.md (wire the refactor-input framing into the workflow)
```

```yaml
# specs/desired_program_model/ticket_plan.yaml:2143-2147 (CD-03)
    implementation_scope:
      - scripts/fitness_functions.py (primitives + composition + evaluation; lean)
      - scripts/analyze_complexity.py (load per-project rules; surface fired rules in the report)
      - tests/test_fitness_functions.py
      - SKILL.md and references/fitness_functions.md (how an agent adds rules; advisory semantics)
```

```yaml
# specs/desired_program_model/ticket_plan.yaml:520 (planning_rules.semantic_model_rule)
  semantic_model_rule: Do not add test graph nodes, pytest jobs, CI workflow steps, integration harnesses, or validation scripts as TLA+ program state/actions. The CLI's own workflow commands (scaffold, analyze, generate, close) ARE program behavior for this repository.
```

```yaml
# specs/desired_program_model/ticket_plan.yaml:524 (planning_rules.case_execution_rule, first sentence)
  case_execution_rule: HISTORICAL (modular-fuzzing epic; retained for the record). For the complexity-descriptor epic the fuzzing machinery is EXPERIMENTAL and not product validation — do not run case generation, the corpus, effect conformance, or the kill test as ticket validation. [...]
```

| Scope line | Covers |
|---|---|
| `ticket_plan.yaml:1997` / `:2145` | `scripts/analyze_complexity.py` — in scope (exact path) |
| `ticket_plan.yaml:1998` | `tests/test_analyze_complexity.py` — in scope as change surface (exact path); modeling excluded by `:520` |
| `ticket_plan.yaml:1999` / `:2075` / `:2147` | `SKILL.md`, `references/architecture_tractability.md`, `references/complexity_intuition.md`, `references/fitness_functions.md` — docs; not code surface, in scope as shipped doc surface |
| `ticket_plan.yaml:2144` | `scripts/fitness_functions.py` — in scope (exact path) |
| `ticket_plan.yaml:2146` | `tests/test_fitness_functions.py` — in scope as change surface (exact path); modeling excluded by `:520` |
| `ticket_plan.yaml:538` | `scripts/generate_cases_from_tlc_dump.py` — in scope (exact path in service_catalog) |
| `ticket_plan.yaml:539` | `scripts/run_generated_case_adapters.py` — in scope (exact path in service_catalog) |
| `ticket_plan.yaml:546` | `specs/program_model/production_adapters.py` — in scope (exact path in service_catalog) |
| `ticket_plan.yaml:520` | places test graph nodes, pytest jobs, integration harnesses, validation scripts OUT of the modeled surface; names scaffold/analyze/generate/close as program behavior |
| `ticket_plan.yaml:537`, `:540-544`, `:547`, `:549` | NOT exact paths — every row they would cover is an ESCALATION (see §6.3) |

**Closure rule applied:** an `implementation_scope`/catalog entry naming a FILE
scopes that file only. No entry in this plan writes a directory or a glob, so
no directory closure was granted anywhere.

**Escalations (ambiguous boundary):** see §6.3. Summary: the service_catalog
was inherited verbatim from the previous epic and never re-declared for this
one; 56 of 332 Sweep-1 rows have no plan line that classifies them.

---

## 1. Model representation index

**Definitions.** Mandated command
`grep -nE '^[A-Za-z_][A-Za-z0-9_]*(\(.*\))? ==' specs/current/*.tla` -> **N = 37**.
**Prompt defect found (attestation §8.6):** the mandated regex requires exactly
one space before `==` and silently missed the 5 alignment-padded stage
constants (`TicketUnopened == 0` etc., TlaSpecDevCli.tla:186-190). Corrected
command `grep -nE '^[A-Za-z_][A-Za-z0-9_]*(\(.*\))?[[:space:]]+==' ...` ->
**N = 42**; the index below uses the corrected enumeration.

| Kind | Name | `file:line` |
|---|---|---|
| Action | `BuildSkillCli` | `specs/current/TlaSpecDevCli.tla:215` |
| Action | `InstallLocalCli` | `specs/current/TlaSpecDevCli.tla:231` |
| Action | `ScaffoldProject(root)` | `specs/current/TlaSpecDevCli.tla:248` |
| Action | `RecordBudgets(root)` | `specs/current/TlaSpecDevCli.tla:269` |
| Action | `ScaffoldWorkflow(root)` | `specs/current/TlaSpecDevCli.tla:287` |
| Action | `OpenTicket(root, ticket)` | `specs/current/TlaSpecDevCli.tla:305` |
| Action | `UpdateTicketDesired(ticket)` | `specs/current/TlaSpecDevCli.tla:328` |
| Action | `UpdateTicketCurrent(ticket)` | `specs/current/TlaSpecDevCli.tla:345` |
| Action | `AnalyzeComplexity(root)` | `specs/current/TlaSpecDevCli.tla:370` |
| Action | `AnalyzeCorpus(root)` | `specs/current/TlaSpecDevCli.tla:402` |
| Action | `RunEffectConformance(root)` | `specs/current/TlaSpecDevCli.tla:439` |
| Action | `RunKillTest(root)` | `specs/current/TlaSpecDevCli.tla:492` |
| Action | `RunSpecUnitTests(root, ticket, override)` | `specs/current/TlaSpecDevCli.tla:519` |
| Action | `CloseTicket(root, ticket)` | `specs/current/TlaSpecDevCli.tla:580` |
| Action | `Stutter` | `specs/current/TlaSpecDevCli.tla:597` |
| Non-action defs | `vars`, 6 stage constants, `ActiveTickets`, `ClosedTickets`, `CommandResult`, `Init`, `Next`, `Spec`, 14 invariants (`TypeInvariant` :629 ... `KillTestVerdictRequiresBudgets` :766) | `specs/current/TlaSpecDevCli.tla:173-769` |
| Port | `spec_tree` (filesystem.write `**/specs/**`) | `specs/current/spec_manifest.yaml:154-156` |
| Port | `evidence_report` (filesystem.write `**/results/**`) | `specs/current/spec_manifest.yaml:157-159` |
| Port | `cli_artifact` (filesystem.write `**/.venv/**`) | `specs/current/spec_manifest.yaml:160-162` |
| Port | `tlc_process` (process.spawn `*java*`) | `specs/current/spec_manifest.yaml:163-165` |
| Port | `test_process` (process.spawn `*pytest*`) | `specs/current/spec_manifest.yaml:166-168` |
| Action->port map | 13 actions mapped (RecordBudgets and Stutter absent) | `specs/current/spec_manifest.yaml:169-182` |
| Binding | 11 adapter bindings (`BuildSkillCli`...`AnalyzeCorpus`) | `specs/current/case_adapters.toml:2-33` (discovered via `spec_manifest.yaml:184`) |
| Binding | `actions.yml` / `testgraph_bindings.yml` outside examples/ | **none exist** — `find . -name 'actions.yml' -o -name 'testgraph_bindings.yml' \| grep -v '^./examples/'` returned nothing |

**Index desyncs (all previously reported by MF-026, re-verified fresh, all still open):**

1. `spec_manifest.yaml:111-113` references `../program_model/Core.tla`, `Internal.tla`, `External.tla` — **all three still missing**; nothing fails.
2. The `@port` annotations in the TLA file (`TlaSpecDevCliPort.build_skill_cli` ... `close_ticket`, TlaSpecDevCli.tla:214-579) and the declared ports (`spec_tree`...`test_process`, manifest:154-168) still have **empty intersection** — two vocabularies, nothing checks they refer to each other.
3. `state_fields: []`, `actions: []`, `ports: {}` at manifest:120-122 while the model has 9 variables and 15 actions.
4. **New this run:** `case_adapters.toml` binds `ValidateTestGraphCli`, which is not a model action; `UpdateTicketDesired`, `UpdateTicketCurrent`, `RunEffectConformance`, `RunKillTest` have adapter classes (production_adapters.py:147,156,1563,1655) but no binding. See gap G5.

---

## 2. Sweep 1 — Program surface

**Enumeration commands and raw counts** (filter stated below):

```bash
git ls-files '*.py'   | wc -l   # 2068 raw
git ls-files '*.kt'   | wc -l   #  546 raw
git ls-files '*.kts'  | wc -l   #  130 raw
git ls-files '*.java' | wc -l   #  312 raw
git ls-files '*.sh'   | wc -l   #    5 raw
# single filter applied to each: grep -v '^specs/\.history/'
# py 175, kt 84, kts 20, java 48, sh 5  ->  N = 332
```

**Filter statement (checked against the declared scope):** exactly one filter —
`specs/.history/**` (the append-only sealed history tree; 1893 py + 462 kt +
110 kts + 264 java files dropped). No `implementation_scope` or
`service_catalog` line names a `.history` path as surface (plan mentions of
`.history` at :850, :1526-1533 are archived evidence citations, none matched by
these globs). `tests/` was deliberately NOT filtered because :1998 and :2146
name test files. `.tla` files are the audited model itself, not program
surface; `*.json/yaml/toml/cfg/md/j2` are not enumerated as program surface
(recorded in attestation §8.2).

**Row-set discipline:** enumerated **N = 332**; table rows **M = 332**; `N == M`: yes.
Classification is mechanical (rules R1/R2a/R2b/R2c/R3 below, applied by a
recorded script); dispositions per row:
**in-scope 7** (rows tagged `in`, incl. 2 also matching R2a) / **out-of-scope 269** (R2a pytest jobs 53, R2b test-graph/harness 214, R2c validation scripts 2, per `:520`) / **ESCALATION 56** (no plan line).

Rules: R1 exact path named by a quoted plan line (§0 table). R2 out per `:520`:
R2a basename `test_*.py`/`conftest.py` or a `tests` path component ("pytest
jobs"); R2b a `test_graph` or `graph-reports` path component ("test graph
nodes"/"integration harnesses"; `graph-reports` trees are archived copies of
test-graph node sources kept as evidence); R2c the two `examples/*validation*`
entry scripts ("validation scripts"). R3 everything else escalates.

Verdicts: default polarity `unrepresented`; `represented`/`partial` only with a
cited action/binding. Rows not listed in §8.3 as READ were dispositioned from
path + the Step-1 binding index.

| # | Module | In/Out | Plan line | Verdict | Evidence |
|---|---|---|---|---|---|
| 1 | `examples/distributed_history/ecommerce_backend/__init__.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 2 | `examples/distributed_history/ecommerce_backend/domain.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 3 | `examples/distributed_history/ecommerce_backend/service.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 4 | `examples/distributed_history/scripts/regenerate_tlc_cases.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 5 | `examples/distributed_history/specs/__init__.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 6 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/__init__.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 7 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/cases.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 8 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/types.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 9 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/validators.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 10 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/__init__.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 11 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/cases.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 12 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/types.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 13 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/validators.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 14 | `examples/distributed_history/specs/program_model/__init__.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 15 | `examples/distributed_history/specs/program_model/adapters.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 16 | `examples/distributed_history/specs/program_model/tests/test_ecommerce_adapters.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 17 | `examples/distributed_history/specs/program_model/tlc_projection.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 18 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/__init__.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 19 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/context_item.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 20 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/context.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 21 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/node_spec.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 22 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/procs.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 23 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/result.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 24 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/runner.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 25 | `examples/distributed_history/test_graph/sources/cleanup_ecommerce.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 26 | `examples/distributed_history/test_graph/sources/collect_evidence.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 27 | `examples/distributed_history/test_graph/sources/deploy_ecommerce.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 28 | `examples/distributed_history/test_graph/sources/run_external_cases.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 29 | `examples/distributed_history/tests/test_ecommerce_backend.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 30 | `examples/run_distributed_history_validation.py` | out | ticket_plan.yaml:520 (validation scripts) | unrepresented | validation script; default polarity, not read |
| 31 | `examples/validate_split_desired_workflow.py` | out | ticket_plan.yaml:520 (validation scripts) | unrepresented | validation script; default polarity, not read |
| 32 | `examples/validation/ex1_scaffold_only/taskq/taskq.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 33 | `examples/validation/ex1_scaffold_only/taskq/tests/test_taskq.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 34 | `examples/validation/ex3_over_complex/order_hub/order_hub.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 35 | `examples/validation/ex3_over_complex/order_hub/tests/test_order_hub.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 36 | `examples/validation/runs/ex3-run1/artifacts/order_hub_after.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 37 | `scripts/analyze_complexity.py` | in | ticket_plan.yaml:1997 (CD-01), :2145 (CD-03) | partial | AnalyzeComplexity TlaSpecDevCli.tla:370-382; ports manifest:177; binding case_adapters.toml:29-30. UNCOVERED: (a) CD-03 fitness evaluation+notification (analyze_complexity.py:1194-1203,1402-1432); (b) silent manifest-degrade except->None (:1046-1052); (c) declared tlc_process port never performed on the analyze path (no subprocess in file) |
| 38 | `scripts/budgets.py` | ESCALATION | no plan line classifies this path | partial | RecordBudgets TlaSpecDevCli.tla:269 + budgets block manifest:96-108 read by gates. UNCOVERED: load/fallback semantics not modeled |
| 39 | `scripts/close_spec_workflow.py` | ESCALATION | no plan line classifies this path | partial | CloseTicket-family close-out; TlaSpecDevCli.tla:580. UNCOVERED: workflow-level snapshot rmtree (:49); --allow-open flag branch |
| 40 | `scripts/close_ticket.py` | ESCALATION | no plan line classifies this path | partial | CloseTicket TlaSpecDevCli.tla:580. UNCOVERED: --allow-open / --no-promote-current / --no-skill-feedback flags are unmodeled config branches on a modeled action |
| 41 | `scripts/close_tickets.py` | ESCALATION | no plan line classifies this path | partial | CloseTicket TlaSpecDevCli.tla:580 (batch form; plan :523 forbids ticket agents running it). UNCOVERED: destructive unlink/rmtree (:127,:232) with no filesystem.delete port |
| 42 | `scripts/close-spec-workflow.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 43 | `scripts/close-ticket.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 44 | `scripts/complexity_ledger.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 45 | `scripts/corpus_diagnostics.py` | ESCALATION | no plan line classifies this path | partial | AnalyzeCorpus TlaSpecDevCli.tla:402 via dispatch tla_spec_dev.py:147 |
| 46 | `scripts/effect_conformance_report.py` | ESCALATION | no plan line classifies this path | partial | RunEffectConformance TlaSpecDevCli.tla:439 via dispatch tla_spec_dev.py:159 |
| 47 | `scripts/effect_conformance.py` | ESCALATION | no plan line classifies this path | partial | RunEffectConformance TlaSpecDevCli.tla:439-448. UNCOVERED: the sandbox patching mechanism itself (:692,:760-788) and its observability limits |
| 48 | `scripts/export_testgraph_cases.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 49 | `scripts/extract_spec_manifest.py` | ESCALATION | no plan line classifies this path | unrepresented | manifest-parsing infrastructure used by every gate (incl. hand-rolled no-PyYAML parser, MF-014 finding); no action represents parsing |
| 50 | `scripts/fitness_functions.py` | in | ticket_plan.yaml:2144 (CD-03) | unrepresented | no action, port, binding, or manifest entry names it; new rules-file input surface (fitness_functions.py:271-361) and notification output (:363-428) |
| 51 | `scripts/generate_cases_from_tlc_dump.py` | in | ticket_plan.yaml:538 (service_catalog.existing_boundaries) | unrepresented | no case-generation action exists; plan :520 names `generate` as program behavior; performs the repo's only real TLC java spawn (:95), metadir rmtree (:97), advisory proceed-on-gate-fail (:866-882) that contradicts the model's blocking guard (TlaSpecDevCli.tla:528-531) |
| 52 | `scripts/generate_docs.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 53 | `scripts/generate_python.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 54 | `scripts/infer_action_params.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 55 | `scripts/kill_test.py` | ESCALATION | no plan line classifies this path | partial | RunKillTest TlaSpecDevCli.tla:492. UNCOVERED: corpus child run outside sandbox (:600-617) child effects; timeout kill path (:614) |
| 56 | `scripts/new_ticket_workflow.py` | ESCALATION | no plan line classifies this path | partial | ScaffoldWorkflow TlaSpecDevCli.tla:287, OpenTicket :305 via dispatch tla_spec_dev.py:102,:124 |
| 57 | `scripts/onboard_program_model.py` | ESCALATION | no plan line classifies this path | partial | ScaffoldProject TlaSpecDevCli.tla:248 via dispatch tla_spec_dev.py:64. UNCOVERED: uv/install child spawn (:1188) child effects |
| 58 | `scripts/run_generated_case_adapters.py` | in | ticket_plan.yaml:539 (service_catalog.existing_boundaries) | partial | RunSpecUnitTests TlaSpecDevCli.tla:519, RunEffectConformance :439 (incl. unobservable :442). UNCOVERED: standalone invocation; SPEC_DOUBLE_BATCH_REEXEC re-exec branch (:971,:990-998); per-field unobservable declarations (:469-530); per-case python children's own effects (process-boundary rule) |
| 59 | `scripts/run_kill_test.py` | ESCALATION | no plan line classifies this path | partial | RunKillTest TlaSpecDevCli.tla:492 via dispatch tla_spec_dev.py:172 |
| 60 | `scripts/scaffold_spec_workflow.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 61 | `scripts/scaffold_spec.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 62 | `scripts/skill_feedback.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 63 | `scripts/spec_evolution.py` | ESCALATION | no plan line classifies this path | partial | CloseTicket TlaSpecDevCli.tla:580 promotion/history effect via dispatch tla_spec_dev.py:178. UNCOVERED: destructive deletes (:154,:385,:477) have NO declared filesystem.delete port; git metadata spawn (:99) undeclared; history-entry timestamps (:770,:883) |
| 64 | `scripts/spec_paths.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 65 | `scripts/start_ticket.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 66 | `scripts/testgraph_channels.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 67 | `scripts/tla_spec_dev.py` | ESCALATION | no plan line classifies this path | partial | all 9 subcommands dispatch to modeled actions (parser :387-663; dispatch imports :64-203; actions TlaSpecDevCli.tla:248-596; manifest:169-182). UNCOVERED: `run spec-unit-tests` env pass-through spawn (:271,:358) whose child effects are unrepresented; no `generate` subcommand although :520 lists generate as program behavior |
| 68 | `spec_double_compiler/__init__.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 69 | `spec_double_compiler/runtime.py` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 70 | `specs/current/adapter_case_runtime.py` | ESCALATION | no plan line classifies this path | unrepresented | generated-case runtime shim; no action names it |
| 71 | `specs/current/production_adapters.py` | ESCALATION | no plan line classifies this path | partial | working copy of the bound adapter set (bindings case_adapters.toml:2-33); same uncovered parts as specs/program_model/production_adapters.py |
| 72 | `specs/current/tests/test_current_ticket_workflow.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 73 | `specs/current/tests/test_tla_spec_dev_analyze_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 74 | `specs/current/tests/test_tla_spec_dev_budgets_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 75 | `specs/current/tests/test_tla_spec_dev_case_execution_run.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 76 | `specs/current/tests/test_tla_spec_dev_cli_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 77 | `specs/current/tests/test_tla_spec_dev_close_promotion_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 78 | `specs/current/tests/test_tla_spec_dev_complexity_ledger_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 79 | `specs/current/tests/test_tla_spec_dev_corpus_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 80 | `specs/current/tests/test_tla_spec_dev_effect_conformance_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 81 | `specs/current/tests/test_tla_spec_dev_kill_test_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 82 | `specs/current/tests/test_tla_spec_dev_run_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 83 | `specs/current/tests/test_tla_spec_dev_scaffold_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 84 | `specs/current/tests/test_tla_spec_dev_skill_feedback_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 85 | `specs/current/tests/test_tla_spec_dev_test_graph_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 86 | `specs/current/tests/test_tla_spec_dev_ticket_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 87 | `specs/current/tests/test_tla_spec_dev_update_ticket_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 88 | `specs/desired_program_model/production_adapters.py` | ESCALATION | no plan line classifies this path | partial | desired-tree copy of the bound adapter set; same binding citations |
| 89 | `specs/desired_program_model/tests/test_tla_spec_dev_cli_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 90 | `specs/desired_program_model/tests/test_tla_spec_dev_run_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 91 | `specs/desired_program_model/tests/test_tla_spec_dev_scaffold_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 92 | `specs/desired_program_model/tests/test_tla_spec_dev_test_graph_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 93 | `specs/desired_program_model/tests/test_tla_spec_dev_ticket_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 94 | `specs/program_model/production_adapters.py` | in | ticket_plan.yaml:546 (service_catalog.adapter_boundaries) | partial | 11 bindings case_adapters.toml:2-33 to named actions. UNCOVERED: UpdateTicketDesired/UpdateTicketCurrent/RunEffectConformance/RunKillTest adapters exist (:147,:156,:1563,:1655) but are UNBOUND; binding ValidateTestGraphCli (toml:23-24) names a non-action; AnalyzeComplexityAdapter python spawns (:1317,:1335) match no declared spawn target |
| 95 | `specs/program_model/tests/test_tla_spec_dev_cli_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 96 | `specs/program_model/tests/test_tla_spec_dev_run_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 97 | `specs/program_model/tests/test_tla_spec_dev_scaffold_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 98 | `specs/program_model/tests/test_tla_spec_dev_test_graph_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 99 | `specs/program_model/tests/test_tla_spec_dev_ticket_adapter.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 100 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/__init__.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 101 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/context_item.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 102 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/context.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 103 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/node_spec.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 104 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/procs.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 105 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/result.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 106 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/runner.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 107 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_cleanup.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 108 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_close_ticket.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 109 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_complete_ticket.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 110 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_create_repo.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 111 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_failure_cleanup_probe.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 112 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_force_failure.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 113 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_spec_units.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 114 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_start_ticket.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 115 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/tla_spec_dev_cli_help.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 116 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/tla_spec_dev_cli_install.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 117 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/__init__.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 118 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/context_item.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 119 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/context.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 120 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/node_spec.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 121 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/procs.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 122 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/result.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 123 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/runner.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 124 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_cleanup.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 125 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_close_ticket.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 126 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_complete_ticket.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 127 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_create_repo.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 128 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_failure_cleanup_probe.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 129 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_force_failure.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 130 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_spec_units.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 131 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_start_ticket.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 132 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/tla_spec_dev_cli_help.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 133 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/tla_spec_dev_cli_install.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 134 | `test_graph/sdk/python/src/testgraphsdk/__init__.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 135 | `test_graph/sdk/python/src/testgraphsdk/context_item.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 136 | `test_graph/sdk/python/src/testgraphsdk/context.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 137 | `test_graph/sdk/python/src/testgraphsdk/node_spec.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 138 | `test_graph/sdk/python/src/testgraphsdk/procs.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 139 | `test_graph/sdk/python/src/testgraphsdk/result.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 140 | `test_graph/sdk/python/src/testgraphsdk/runner.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 141 | `test_graph/sources/spec_workflow_cleanup.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 142 | `test_graph/sources/spec_workflow_close_ticket.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 143 | `test_graph/sources/spec_workflow_complete_ticket.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 144 | `test_graph/sources/spec_workflow_create_repo.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 145 | `test_graph/sources/spec_workflow_failure_cleanup_probe.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 146 | `test_graph/sources/spec_workflow_force_failure.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 147 | `test_graph/sources/spec_workflow_spec_units.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 148 | `test_graph/sources/spec_workflow_start_ticket.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 149 | `test_graph/sources/tla_spec_dev_cli_help.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 150 | `test_graph/sources/tla_spec_dev_cli_install.py` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 151 | `tests/conftest.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 152 | `tests/corpus_fixtures.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 153 | `tests/effect_adapter_fixtures.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 154 | `tests/test_analyze_complexity.py` | in (change surface) / out of modeling per :520 | ticket_plan.yaml:1998 (CD-01); ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; modeling excluded per ticket_plan.yaml:520 |
| 155 | `tests/test_budgets.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 156 | `tests/test_case_adapter_runtime.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 157 | `tests/test_complexity_ledger.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 158 | `tests/test_corpus_diagnostics.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 159 | `tests/test_effect_conformance_cli.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 160 | `tests/test_effect_conformance_runner.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 161 | `tests/test_effect_conformance.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 162 | `tests/test_export_testgraph_cases.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 163 | `tests/test_extract_spec_manifest.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 164 | `tests/test_fitness_functions.py` | in (change surface) / out of modeling per :520 | ticket_plan.yaml:2146 (CD-03); ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; modeling excluded per ticket_plan.yaml:520 |
| 165 | `tests/test_generate_cases_from_tlc_dump.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 166 | `tests/test_infer_action_params.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 167 | `tests/test_kill_test.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 168 | `tests/test_new_ticket_workflow.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 169 | `tests/test_onboard_program_model.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 170 | `tests/test_promotion_preserves_current.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 171 | `tests/test_scaffold_spec_views.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 172 | `tests/test_skill_feedback.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 173 | `tests/test_spec_yaml_valid.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 174 | `tests/test_testgraph_channels.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 175 | `tests/test_tla_spec_dev_cli.py` | out | ticket_plan.yaml:520 (pytest jobs) | unrepresented | pytest job; default polarity, not read |
| 176 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Context.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 177 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Executors.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 178 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/JBangExecutor.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 179 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/PlanExecutor.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 180 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/TimeoutParser.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 181 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/UvExecutor.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 182 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphAssembler.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 183 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphModel.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 184 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/MiniJson.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 185 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/NodeDescribeLoader.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 186 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/InspectionTasks.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 187 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunReportWriter.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 188 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunTestGraphTask.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 189 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/ValidationReportTask.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 190 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/TestGraphSpec.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 191 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/Toolchain.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 192 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphExtension.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 193 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphPlugin.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 194 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationNodeSpec.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 195 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationRuntime.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 196 | `examples/distributed_history/test_graph/build-logic/src/test/kotlin/com/hayden/testgraphsdk/exec/PlanExecutorResumeHarnessTest.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 197 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Context.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 198 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Executors.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 199 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/JBangExecutor.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 200 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/PlanExecutor.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 201 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/TimeoutParser.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 202 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/UvExecutor.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 203 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphAssembler.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 204 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphModel.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 205 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/MiniJson.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 206 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/NodeDescribeLoader.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 207 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/InspectionTasks.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 208 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunReportWriter.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 209 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunTestGraphTask.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 210 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/ValidationReportTask.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 211 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/TestGraphSpec.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 212 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/Toolchain.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 213 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphExtension.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 214 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphPlugin.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 215 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationNodeSpec.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 216 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationRuntime.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 217 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/test/kotlin/com/hayden/testgraphsdk/exec/PlanExecutorResumeHarnessTest.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 218 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Context.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 219 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Executors.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 220 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/JBangExecutor.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 221 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/PlanExecutor.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 222 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/TimeoutParser.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 223 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/UvExecutor.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 224 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphAssembler.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 225 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphModel.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 226 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/MiniJson.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 227 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/NodeDescribeLoader.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 228 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/InspectionTasks.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 229 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunReportWriter.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 230 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunTestGraphTask.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 231 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/ValidationReportTask.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 232 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/TestGraphSpec.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 233 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/Toolchain.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 234 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphExtension.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 235 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphPlugin.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 236 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationNodeSpec.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 237 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationRuntime.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 238 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/test/kotlin/com/hayden/testgraphsdk/exec/PlanExecutorResumeHarnessTest.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 239 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Context.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 240 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Executors.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 241 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/JBangExecutor.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 242 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/PlanExecutor.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 243 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/TimeoutParser.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 244 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/UvExecutor.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 245 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphAssembler.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 246 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphModel.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 247 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/MiniJson.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 248 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/NodeDescribeLoader.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 249 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/InspectionTasks.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 250 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunReportWriter.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 251 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunTestGraphTask.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 252 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/ValidationReportTask.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 253 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/TestGraphSpec.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 254 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/Toolchain.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 255 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphExtension.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 256 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphPlugin.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 257 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationNodeSpec.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 258 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationRuntime.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 259 | `test_graph/build-logic/src/test/kotlin/com/hayden/testgraphsdk/exec/PlanExecutorResumeHarnessTest.kt` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 260 | `examples/distributed_history/test_graph/build-logic/build.gradle.kts` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 261 | `examples/distributed_history/test_graph/build-logic/settings.gradle.kts` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 262 | `examples/distributed_history/test_graph/build.gradle.kts` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 263 | `examples/distributed_history/test_graph/sdk/java/build.gradle.kts` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 264 | `examples/distributed_history/test_graph/settings.gradle.kts` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 265 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/build.gradle.kts` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 266 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/settings.gradle.kts` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 267 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build.gradle.kts` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 268 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/build.gradle.kts` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 269 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/settings.gradle.kts` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 270 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/build.gradle.kts` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 271 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/settings.gradle.kts` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 272 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build.gradle.kts` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 273 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/build.gradle.kts` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 274 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/settings.gradle.kts` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 275 | `test_graph/build-logic/build.gradle.kts` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 276 | `test_graph/build-logic/settings.gradle.kts` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 277 | `test_graph/build.gradle.kts` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 278 | `test_graph/sdk/java/build.gradle.kts` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 279 | `test_graph/settings.gradle.kts` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 280 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextItem.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 281 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextSerde.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 282 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Json.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 283 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/JsonMapper.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 284 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Node.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 285 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeBody.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 286 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeContext.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 287 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeResult.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 288 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeSpec.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 289 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeStatus.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 290 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ProcessRecord.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 291 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Procs.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 292 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextItem.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 293 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextSerde.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 294 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Json.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 295 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/JsonMapper.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 296 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Node.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 297 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeBody.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 298 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeContext.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 299 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeResult.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 300 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeSpec.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 301 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeStatus.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 302 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ProcessRecord.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 303 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Procs.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 304 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextItem.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 305 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextSerde.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 306 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Json.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 307 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/JsonMapper.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 308 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Node.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 309 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeBody.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 310 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeContext.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 311 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeResult.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 312 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeSpec.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 313 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeStatus.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 314 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ProcessRecord.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 315 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Procs.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 316 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextItem.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 317 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextSerde.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 318 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Json.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 319 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/JsonMapper.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 320 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Node.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 321 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeBody.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 322 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeContext.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 323 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeResult.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 324 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeSpec.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 325 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeStatus.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 326 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ProcessRecord.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 327 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Procs.java` | out | ticket_plan.yaml:520 (test graph nodes / integration harnesses) | unrepresented | test-graph node/harness surface; default polarity, not read |
| 328 | `examples/distributed_history/scripts/k3d-up.sh` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 329 | `examples/distributed_history/scripts/k8s-deploy.sh` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 330 | `scripts/run_tlc.sh` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 331 | `skill-scripts/install-tla-spec-dev.sh` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |
| 332 | `skill-scripts/install-tlc2.sh` | ESCALATION | no plan line classifies this path | unrepresented | no positive evidence; default polarity, not read |

**Sweep close:** enumerated N = 332, table rows M = 332, N == M. Verdict counts:
partial 18, unrepresented 314, represented 0 — coverage was granted only where
an action + dispatch/binding could be cited, and NO row earned unqualified
`represented` (every mapped module carries at least one named uncovered part).

---

## 3. Sweep 2 — Effects, by category

Search surface: **all 332 Sweep-1 files** (`$SURFACE`), never a subdirectory.
Raw outputs: `specs/results/epic-close/sweep-raw/<category>.txt`. Patterns are
the prompt's word-boundary-anchored sets, run per category with
`xargs grep -nE <pattern> < ca-surface-all.txt`.

**Grouping rule (all categories, stated once):** every raw hit is partitioned
by (AREA, CLASS): AREA = first matching path prefix in {scripts/->prod-scripts,
spec_double_compiler/->prod-runtime, specs/{current,program_model,desired_program_model}
non-tests->adapters, .../tests/->spec-tests, tests/->repo-tests,
test_graph/->testgraph, specs/tickets/->archived-evidence, examples/->examples,
skill-scripts/}; CLASS (filesystem only) = first matching regex in
{destructive: `rmtree|os\.remove|\.unlink\(|os\.rename|os\.replace|deleteRecursively|Files\.delete`,
tempdir: `tempfile|mkdtemp|NamedTemporaryFile|TemporaryDirectory`,
write: `write_text|write_bytes|mkdir|makedirs|copytree|copy2?\(|open\([^)]*["'][wax]`,
other}. Every raw hit lands in exactly one group; group totals were
machine-checked equal to raw N for every category. A reader applying this rule
to the raw files reproduces these groups. Destructive hits are additionally
enumerated **per-site** (never grouped) in §3.1a.

Scope/plan-line and port columns are stated per group; verdict semantics:
`declared` (cited port covers the group) / `undeclared` / `partial` (port
covers part; remainder named).

### 3.1 Filesystem — raw `2312`, groups `24` (group totals sum to 2312)

| # | Group (area/class) | Hits | Effect performed | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | prod-scripts/write | 73 | spec-tree scaffold/open/close writes; report/evidence writes; doc generation | ESCALATION except 4 named files | :537 not a path | `spec_tree` :154, `evidence_report` :157 | partial — writes under `**/specs/**` and `**/results/**` covered; writes elsewhere (e.g. generated docs, `analyze --out` to arbitrary paths, analyze_complexity.py:1621-1625) match no port glob |
| 2 | prod-scripts/destructive | 8 | see §3.1a | mixed | — | **none** | **undeclared** — no `filesystem.delete` port exists in the manifest |
| 3 | prod-scripts/tempdir | 2 | temp workdirs for sandbox/generation | ESCALATION | — | none | undeclared |
| 4 | prod-scripts/other | 586 | reads (manifest/cfg/TLA/rules), `Path` construction, prose | ESCALATION | — | n/a — reads are not observable effect types (manifest:144-148) | undeclared-unobservable: every config read (incl. the CD-03 `fitness_functions.yaml` read, fitness_functions.py:271-297) is an unmodeled INPUT; `unobservable` is not `clean` |
| 5 | prod-runtime/other | 6 | spec_double_compiler runtime path handling | ESCALATION | — | none | undeclared |
| 6 | adapters/write | 77 | fixture spec trees + evidence under adapter work dirs | in via :546 (program_model copy); copies escalate | :546 | `spec_tree`/`evidence_report` when under the globs | partial — fixture writes to temp target repos fall outside both globs |
| 7 | adapters/other | 236 | reads + path probing in adapters | :546 / ESCALATION | :546 | n/a | undeclared-unobservable (inputs) |
| 8 | spec-tests/write, 9 spec-tests/other | 7+125 | spec-unit test fixtures | out | :520 | n/a | inventory per :520 |
| 10 | repo-tests/write, /destructive, /tempdir, /other | 236+6+5+441 | pytest fixtures/asserts | out | :520 | n/a | inventory per :520 (destructive sites listed in §3.1a) |
| 14 | testgraph/write, /destructive, /other | 26+3+96 | graph node repo setup/cleanup | out | :520 | n/a | inventory per :520 |
| 17 | archived-evidence/write, /destructive, /other | 48+6+184 | archived copies of graph-node sources | out | :520 (R2b) | n/a | inventory per :520 |
| 20 | examples/write, /destructive, /tempdir, /other | 28+3+5+103 | example apps + validation fixtures | out (R2b/R2c) / ESCALATION (app sources) | :520 / none | n/a | inventory / escalation E1 |
| 24 | skill-scripts/write | 2 | installer writes | ESCALATION | — | none | undeclared |

### 3.1a Destructive filesystem effects — per-site, never grouped (raw 26, sites 26)

| # | Site | Effect | In/Out | Declared port | Verdict |
|---|---|---|---|---|---|
| 1 | `scripts/spec_evolution.py:154` | `shutil.rmtree(state_dir)` | ESCALATION (E5) | none | **undeclared** |
| 2 | `scripts/spec_evolution.py:385` | `shutil.rmtree(dst)` in `replace_tree` — the MF-021 promotion-loss site, now preserve-aware | ESCALATION (E5) | none | **undeclared** |
| 3 | `scripts/spec_evolution.py:477` | `target.unlink()` promotion removal (enumerated at close) | ESCALATION (E5) | none | **undeclared** |
| 4 | `scripts/close_tickets.py:127` | `dst_files[relative].unlink()` | ESCALATION | none | **undeclared** |
| 5 | `scripts/close_tickets.py:232` | `shutil.rmtree(directory)` | ESCALATION | none | **undeclared** |
| 6 | `scripts/close_spec_workflow.py:49` | `shutil.rmtree(path)` workflow snapshot | ESCALATION | none | **undeclared** |
| 7 | `scripts/generate_cases_from_tlc_dump.py:97` | `shutil.rmtree(metadir, ignore_errors=True)` | **in** :538 | none | **undeclared** (part of gap G3) |
| 8 | `scripts/effect_conformance.py:692` | patches `shutil.rmtree` to OBSERVE `filesystem.delete` — instrument, not a delete | ESCALATION | n/a | instrument; noted because the observer supports a type no port declares |
| 9-10 | `examples/run_distributed_history_validation.py:400,402` | cleanup rmtree | out :520 (R2c) | n/a | inventory |
| 11 | `examples/distributed_history/scripts/regenerate_tlc_cases.py` (1 site) | metadir rmtree | ESCALATION | n/a | escalation E1 |
| 12-17 | `tests/test_effect_conformance.py:129,824`, `tests/test_kill_test.py:938`, `tests/test_new_ticket_workflow.py:201`, `tests/test_promotion_preserves_current.py:4`, `tests/test_skill_feedback.py:229` | pytest fixture deletes | out :520 | n/a | inventory |
| 18-20 | `test_graph/sources/spec_workflow_cleanup.py:32`, `spec_workflow_create_repo.py:36`, `spec_workflow_failure_cleanup_probe.py:47` | graph-node cleanup | out :520 | n/a | inventory |
| 21-26 | same three sites in the two archived `specs/tickets/MF-027/.../graph-reports` copies | archived copies | out :520 (R2b) | n/a | inventory |

**Category finding:** the manifest supports `filesystem.delete` as an
observable type (spec_manifest.yaml:144-148) and the sandbox observes it
(effect_conformance.py:692), but **no port of that type is declared** — every
destructive site above, including promotion's own deletes on the modeled
CloseTicket path, is an undeclared effect. In-scope portion: site 7 (gap G3);
the promotion sites are escalation E5.

### 3.2 Subprocess — raw `976`, collapsed `93`, rule: keep only true spawn primitives (`subprocess\.(run|Popen|check_output|check_call|call)|ProcessBuilder|Runtime\.getRuntime|\bexecv|os\.system`); the 883 discarded hits are the word-boundary matches of `run`/`call`/`spawn` as ordinary identifiers/prose (re-derivable from the raw file)

| # | Site / group | Effect | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `scripts/tla_spec_dev.py:358` | spawns pytest batch for `run spec-unit-tests` (env pass-through :271) | ESCALATION (E2) | :537 | `test_process` :166-168 | **partial** — spawn declared; the child pytest process's own effects are not (process-boundary rule) |
| 2 | `scripts/generate_cases_from_tlc_dump.py:95` | spawns TLC (**the repository's only real `*java*` spawn**) | **in** :538 | :538 | `tlc_process` :163-165 declared for AnalyzeComplexity, NOT for any generation action | **undeclared for its action** — gap G3/G4 |
| 3 | `scripts/kill_test.py:609` | corpus run child (pytest-family), outside sandbox by design (:600-606) | ESCALATION | — | `test_process` | partial — child effects unrepresented; timeout kill path :614 unmodeled |
| 4 | `scripts/spec_evolution.py:99` | `git rev-parse/branch` metadata | ESCALATION (E5) | — | none | **undeclared** |
| 5 | `scripts/onboard_program_model.py:1188` | scaffold-time uv/install child | ESCALATION | — | none | undeclared |
| 6 | `scripts/run_generated_case_adapters.py:992,998` | batch re-exec + per-case python children | **in** :539 | :539 | none matches (`*python*` not declared) | **undeclared** — gap G7 |
| 7 | `scripts/effect_conformance.py:760-771` | patches `subprocess.Popen` to OBSERVE spawns | ESCALATION | — | n/a | instrument |
| 8 | `specs/program_model/production_adapters.py:258,267,343,454,1065,1317,1335,1489,1610,1742` (10 sites; + 10 in the specs/current copy, 5 in desired copy) | adapters spawn uv/python CLI children (incl. AnalyzeComplexityAdapter :1317,:1335) | **in** :546 (copies escalate) | :546 | `*java*`/`*pytest*` only | **undeclared** — python spawns match no declared target; gap G4 |
| 9 | repo-tests group (24 sites in 10 files) | tests spawning the CLI | out | :520 | n/a | inventory |
| 10 | testgraph + archived + examples groups (sdk `procs.py`/`Procs.java` runners, deploy scripts; 6+6+13 sites) | graph node / example spawns (kubectl, k3d, uv) | out (R2b) / ESCALATION (example scripts) | :520 | n/a | inventory / E1 |
| 11 | `skill-scripts/install-tlc2.sh` (1 site) | installer exec | ESCALATION | — | none | undeclared |

### 3.3 Network — raw `60`, collapsed `10` real sites, rule: keep lines invoking a network primitive (`urlopen|socket\.socket|\.connect\(|curl|wget`); discard imports, prose, and the sandbox's own patch/observation code (all discards re-derivable from raw)

| # | Site | Effect | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `examples/distributed_history/ecommerce_backend/service.py:61` | HTTP call (example app) | ESCALATION (E1) | — | none (no network port exists) | undeclared |
| 2 | `examples/distributed_history/specs/program_model/adapters.py:107,119` | HTTP to example app | ESCALATION (E1) | — | none | undeclared |
| 3 | `examples/.../test_graph/sources/deploy_ecommerce.py:153` + urlopen sites; `collect_evidence.py` urlopen | readiness probe + evidence fetch | out | :520 | n/a | inventory |
| 4 | `examples/run_distributed_history_validation.py:411` | port probe socket | out | :520 (R2c) | n/a | inventory |
| 5 | `examples/distributed_history/specs/program_model/tests/test_ecommerce_adapters.py` urlopen | test | out | :520 | n/a | inventory |
| 6 | `scripts/effect_conformance.py:775-788` | patches `socket.connect` to OBSERVE | ESCALATION | — | n/a | instrument |
| 7 | `skill-scripts/install-tlc2.sh:12+` | curl download | ESCALATION | — | none | undeclared |

**Category finding:** zero real network effects in the repository's own
modeled program surface (scripts/ performs none); consistent with the manifest
declaring no network port. All real network I/O lives in example/harness
surface.

### 3.4 Environment — raw `314`, collapsed `8` real accessor sites in non-excluded surface, rule: keep `os\.environ|getenv|expanduser` accessor calls in prod/adapter areas; discard `argv`, `PATH` prose, setdefault-on-dicts, and all R2-excluded areas (313-8 accounted in groups: prod-scripts 22 raw -> 4 real, adapters 9 -> 1, others in excluded areas)

| # | Site | Effect | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `scripts/run_generated_case_adapters.py:971` | `SPEC_DOUBLE_BATCH_REEXEC` gate on re-exec | **in** :539 | :539 | none | **undeclared** config input — gap G7 |
| 2 | `scripts/run_generated_case_adapters.py:990` | env copy into child | **in** :539 | :539 | none | undeclared |
| 3 | `scripts/tla_spec_dev.py:271` | env copy into pytest child | ESCALATION (E2) | — | none | undeclared |
| 4 | `specs/program_model/production_adapters.py:252` | env pass-through to uv child | **in** :546 | :546 | none | undeclared |
| 5-8 | example/testgraph accessors (service.py 9 raw, deploy/cleanup 4, Toolchain.kt 1, procs.py 1) | example/harness config | out / ESCALATION | :520 / — | n/a | inventory / E1 |

### 3.5 Clock — raw `272`, collapsed `4` real sites in non-excluded surface, rule: keep `datetime.now|time.time|monotonic|perf_counter|sleep|strftime|timestamp()` calls outside R2-excluded areas; discard prose/identifier matches (`time` as a word) — excluded-area real sites (test_graph timers/sleeps, example waits) are inventoried by their area groups

| # | Site | Effect | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `scripts/complexity_ledger.py:705` | `recorded_at_utc` timestamp into ledger | ESCALATION | — | none | undeclared input (clock) |
| 2 | `scripts/skill_feedback.py:86` | feedback timestamp | ESCALATION | — | none | undeclared input |
| 3 | `scripts/spec_evolution.py:770` | history entry `created_at_utc` | ESCALATION (E5) | — | none | undeclared input |
| 4 | `scripts/spec_evolution.py:883` | history entry timestamp | ESCALATION (E5) | — | none | undeclared input |

### 3.6 Randomness — raw `5`, collapsed `0`, rule: all 5 hits are the words `random`/`sample` in comments/docstrings/assertion strings (fitness_functions.py:228, kill_test.py:171, test_corpus_diagnostics.py:90,94,117); no randomness primitive is called anywhere in the enumerated surface

No table — zero real sites. (kill_test.py:171 documents that mutation is
deliberately NOT random.)

### 3.7 Persistent store — raw `87`, collapsed `1` real user, rule: a real store effect requires a DB-module import; `xargs grep -lE 'import (sqlite3|psycopg|pymysql|redis|boto3)|from (sqlalchemy|sqlite3)'` over the full surface returns exactly one file; remaining 86 hits are `execute`/`commit`/`cursor`/`session` as ordinary identifiers or git-commit prose

| # | Site | Effect | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `examples/distributed_history/ecommerce_backend/domain.py` (32 hits, sqlite) | example app store | ESCALATION (E1) | — | none | undeclared (example surface) |

---

## 4. Sweep 3 — Behaviors

Search surface: all 332 Sweep-1 files. **Deviation from the prompt recorded in
§8.6:** Step 4's literal commands hardcode `scripts/ spec_double_compiler/`;
per the Step-3 warning (a run-1 finding) they were run over `$SURFACE`
instead. Raw outputs: `specs/results/epic-close/sweep-raw/beh-<class>.txt`.
Area-grouping rule identical to §3.

### 4.1 Error paths — raw `754`, groups `8` (by area; every hit accounted: prod-scripts 355, adapters 34, prod-runtime 13, spec-tests 3, repo-tests 49, testgraph 56, archived 112, examples 132)

| # | Behavior group | Trigger | In/Out | Plan line | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|
| 1 | prod-scripts failure semantics: parse/validation errors exit nonzero with named reason (355 hits across 27 scripts) | malformed TLA/cfg/manifest/plan | 4 files in; rest ESCALATION | :1997,:2144,:538,:539 / E1 | `result.accepted=FALSE` + `CommandResult` reasons model per-command refusal (TlaSpecDevCli.tla:197-198, guards per action); most concrete failure reasons have no distinct model reason value | partial — the model has ONE nondeterministic failure shape per command; the program's distinct failure classes (unparsable spec, missing manifest, bad ticket id, ...) are not distinguished |
| 2 | silent-degrade guards in prod-scripts | `analyze_complexity.py:1046-1052`; `generate_cases_from_tlc_dump.py:869-871`; `fitness_functions.py:284-295` | **in** | :1997,:538,:2144 | none | **unrepresented — gap G6** |
| 3 | adapters' error surfacing (34) | adapter asserts real-command failures into case verdicts | in :546 | :546 | conformance oracle territory | partial — adapter failure taxonomy not modeled |
| 4 | prod-runtime (13) | spec_double_compiler runtime raises | ESCALATION | E1 | none | unrepresented |
| 5 | repo-tests (49) + spec-tests (3) | pytest assertions | out | :520 | n/a | inventory |
| 6 | testgraph (56) + archived (112) | node failure handling (Kotlin/Java try/catch) | out | :520 | n/a | inventory |
| 7 | examples (132) | example app + validation error paths (incl. HTTPError handling service.py:63-65) | out/ESCALATION | :520/E1 | none | inventory / E1 |
| 8 | `run spec-unit-tests` gate-refusal errors | tla_spec_dev.py:517 doctrine text; kill/corpus no-waiver docs (kill_test.py:282, run_kill_test.py) | ESCALATION | E2 | modeled as guards (TlaSpecDevCli.tla:528-539, invariants :696-747) | represented at guard level — the one behavior class where model and program refusal semantics align |

### 4.2 Retries — raw `95`, real retry loops in non-excluded surface: `0` (prod-scripts 2 hits are prose — kill_test.py:282 'an attempt to add a waiver', run_kill_test doc; all loop-shaped retry lives in testgraph/example wait-for-ready polls, out per :520)

No unmodeled retry behavior in the modeled program: the CLI performs no
retries. Nothing to represent; consistent with the model having no retry
transitions.

### 4.3 Timeouts — raw `205`, real sites in non-excluded surface: `6`

| # | Behavior | Trigger | In/Out | Plan line | Spec action | Verdict |
|---|---|---|---|---|---|---|
| 1 | corpus child killed on timeout | `scripts/kill_test.py:614` | ESCALATION | E1 | RunKillTest :492 has no timeout outcome | **unrepresented** |
| 2 | `--timeout` arg plumbed to runner | `scripts/run_kill_test.py:198` | ESCALATION | E1 | none | unrepresented |
| 3-6 | adapter 180s subprocess timeouts | `production_adapters.py:1339,1493,1614,1748` | **in** :546 | :546 | none — a TimeoutExpired in an adapter is a distinct failure the model cannot express | unrepresented (folded into G7's runner/child semantics) |

### 4.4 Fallbacks — raw `182`, groups `6` (prod-scripts 112, adapters 3, prod-runtime 0/13 err-class, repo-tests 9, testgraph 14, archived 28, examples 16)

| # | Behavior | Trigger | In/Out | Plan line | Spec action | Verdict |
|---|---|---|---|---|---|---|
| 1 | **guard-passes-when-input-absent (the recurring class):** broken manifest -> `None` -> justification + manifest-sourced fitness rules silently disabled | `analyze_complexity.py:1046-1052` | **in** | :1997 | none | **unrepresented — gap G6** |
| 2 | scan-crash-must-not-block: unanalyzable model -> warning -> generation proceeds ungated | `generate_cases_from_tlc_dump.py:869-871` | **in** | :538 | model forbids this transition (:528-531) | **unrepresented — gaps G2/G6** |
| 3 | broken fitness rules doc -> INVALID advisory, never a failure; absent rules -> silently no section | `fitness_functions.py:284-295`; `analyze_complexity.py:1195-1203` | **in** | :2144 | none | **unrepresented — gap G1/G6** (deliberate per :2162; see E6) |
| 4 | import fallback for direct-script execution | `generate_cases_from_tlc_dump.py:860-863` | in :538 | :538 | none | unrepresented (benign dual-entry path; named for completeness) |
| 5 | hand-rolled YAML parser when PyYAML absent (MF-014's silent-defaults incident site, now loud) | `scripts/extract_spec_manifest.py` | ESCALATION | E1 | none | unrepresented |
| 6 | remaining `default=`/`or None` argparse defaults (residue of the 112 prod hits) + excluded-area fallbacks | various | ESCALATION / out | E1 / :520 | none | unrepresented / inventory |

### 4.5 Concurrency / interleaving — raw `22`, real concurrency primitives in non-excluded surface: `0` (all 5 prod-script hits are prose — 'synchronized' in scaffold text new_ticket_workflow.py:545,685,693, 'await' in docstrings onboard:660/scaffold_spec:415; real parallelism lives in test_graph Kotlin executors, out per :520)

The modeled program is single-threaded and the model's interleaving is
command-level only. No gap: no unrepresented concurrency exists in-scope.

### 4.6 Config-driven branches — raw `639`, groups `7` (prod-scripts 316, adapters 88, prod-runtime 3, repo-tests 26, spec-tests 3, testgraph 41, archived 72, examples 90)

| # | Behavior | Trigger | In/Out | Plan line | Spec action | Verdict |
|---|---|---|---|---|---|---|
| 1 | fitness rules present/absent branch (per-project persisted config) | `analyze_complexity.py:1194-1203`; `fitness_functions.py:299-361` | **in** | :2144,:2145 | none | **unrepresented — gap G1** |
| 2 | `--allow-open`, `--no-promote-current`, `--no-skill-feedback` on close | `close_ticket.py`, `close_tickets.py`, `close_spec_workflow.py`, `tla_spec_dev.py:648-656` | ESCALATION | E1/E5 | CloseTicket :580 has no flag inputs | unrepresented (escalated scope) |
| 3 | `--no-batch` / `SPEC_DOUBLE_BATCH_REEXEC` execution-mode branch | `tla_spec_dev.py` run_spec_units arg; `run_generated_case_adapters.py:971` | **in** :539 (runner) / E2 (CLI) | :539 | RunSpecUnitTests :519 models `override` only | **unrepresented — gap G7** |
| 4 | `--no-infer-params` generation branch | `generate_cases_from_tlc_dump.py` | **in** :538 | :538 | none (no generation action) | unrepresented — folded into G3 |
| 5 | budgets block values steering every gate | manifest:96-108 read via `scripts/budgets.py` | ESCALATION | E1 (budgets.py unnamed; :541 not a path) | RecordBudgets :269; gate guards consume verdicts, not budget values | partial — budget VALUES as model constants absent; verdict-level representation only |
| 6 | `override` parameter (model side) with NO surviving program input | TlaSpecDevCli.tla:519,:528-539 | **in** (model surface of :1997 boundary) | :1997 | `override` models the withdrawn --allow-over-budget flag | **over-representation — gap G2** |
| 7 | excluded-area config (testgraph toolchain, example env) | various | out | :520 | n/a | inventory |

---

## 5. Sweep 4 — Views, reported separately

Enumeration: `ls specs/current/*.tla` -> exactly one module,
`TlaSpecDevCli.tla`. `spec_manifest.yaml:111-113` references
`../program_model/Core.tla`, `Internal.tla`, `External.tla` — all three
missing (re-verified this run). SKILL.md mandates the Internal/External split
for onboarded projects (known_gaps :549). **A single module is not a merged
view; it is a missing one.**

### 5.1 Internal — verdict: `unrepresented by construction (no Internal view module)`

| Surface item | Verdict | Evidence |
|---|---|---|
| Component decomposition (which variables/actions form components) | unrepresented | no Internal.tla; the C1 monolith finding (11-14 actions on one component) has stood since MF-011 |
| Component-internal interleaving (scaffold pipeline vs ticket lifecycle vs gate machinery as separate components) | unrepresented | single flat `Next` (TlaSpecDevCli.tla:600-627) |
| Internal state detail present in the merged module (setup_phase, ticket_state, 4 gate variables) | present but unattributed to a view | TlaSpecDevCli.tla:163-172; counted as merged-module content, not as an Internal view |

### 5.2 External — verdict: `unrepresented by construction (no External view module)`

| Surface item | Verdict | Evidence |
|---|---|---|
| Public driver surface (9 CLI subcommands + args/flags) | commands present in merged module; the flag surface (--allow-open, --no-batch, --out, --format, ...) absent | parser tla_spec_dev.py:387-663 vs actions :248-596 |
| Observable projection (exit codes, stdout/stderr reports, fired fitness notifications) | unrepresented as a channel contract | `CommandResult` :197 models accepted/reason/next only |
| External channel enforcement (Test Graph `channel` bindings, MF-015) | unrepresented | manifest:14-54 describes it; no External.tla exists to carry it |
| External case generation surface | unrepresented | `export_testgraph_cases.py`, `testgraph_channels.py` map to no action |

Scope: whether the missing views are in THIS epic's scope is escalation E4 —
the quoted :549 text assigns them to a ticket of the concluded epic. The
finding itself is not escalated: both views are missing, so every behavior
belonging to each view is unrepresented by construction.

---

## 6. Dispositions

### 6.1 In-scope gaps — HARD, block promotion

| # | Gap | Sweep | Disposition | Proposed remediation (advisory) |
|---|---|---|---|---|
| G1 | CD-03 fitness-function subsystem entirely unrepresented: scripts/fitness_functions.py (rule loading from manifest `fitness_functions:` / sibling fitness_functions.yaml|json, three-valued evaluation, agent notification) plus its integration in scripts/analyze_complexity.py:1194-1203,1402-1432. New input file surface and new observable report surface with no action, state, or port. | Sweep 1 | model it | Add a rules-source input and fired/holds/unknown outcome to AnalyzeComplexity (or a fitness_rules fact + report field), OR amend service_catalog once to place advisory descriptor/fitness reporting outside the modeled lifecycle (see escalation E6). |
| G2 | The model represents a BLOCKING complexity gate the program no longer has: RunSpecUnitTests guard `complexity_gate="pass" \/ (fail /\ override)` (TlaSpecDevCli.tla:528-531) and the `override` parameter model the withdrawn --allow-over-budget flag; the shipped program proceeds on gate fail with a warning and has NO override input (generate_cases_from_tlc_dump.py:866-882; no allow-over-budget flag anywhere in the CLI; AnalyzeComplexityAdapter asserts 'no over-budget override flag to honor', production_adapters.py:1369-1374). The actual advisory proceed-on-fail behavior is unrepresentable in the current model. | Sweeps 1+3 | model it | Replace the blocking guard + override input with the advisory semantics the epic shipped (gate verdict recorded, never blocking). This is the epic's own pivot, unreflected in the model. |
| G3 | Case generation has no model action: scripts/generate_cases_from_tlc_dump.py is a named existing boundary (:538) and plan :520 names `generate` as program behavior; it performs the repository's only real TLC java spawn (:95) and a destructive metadir rmtree (:97). Invisible to all four oracles. | Sweep 1 | model it | Add a GenerateCases action (spec_tree + tlc_process ports) or a generate subcommand binding; at minimum move the tlc_process port declaration to the action that actually spawns TLC. |
| G4 | Dead port declaration: manifest:177 declares AnalyzeComplexity -> [evidence_report, tlc_process], but the analyze path spawns nothing (scripts/analyze_complexity.py contains no subprocess; the adapter spawns python CLIs at production_adapters.py:1317,:1335 matching neither *java* nor *pytest*). By the manifest's own rule (spec_manifest.yaml:131-136) a declared port no case exercises is DEAD MODEL SURFACE; the adapter's real spawns are undeclared. | Sweep 2 (subprocess) | change the program | Remove tlc_process from AnalyzeComplexity's declared ports (it moved to case generation, see G3) and declare the python spawn the adapter actually performs — or make analyze complexity actually run TLC. |
| G5 | Binding desync on the adapter boundary (:546): specs/current/case_adapters.toml binds 11 labels; the model has 14 actions. UpdateTicketDesired, UpdateTicketCurrent, RunEffectConformance, RunKillTest are unbound although adapter classes exist (production_adapters.py:147,:156,:1563,:1655); ValidateTestGraphCli (toml:23-24) is bound but is not a model action. Same class as MF-026 finding (4), still open, now with fresh line numbers. | Step 1 index / Sweep 1 | change the program | Bind the four missing actions and remove or model ValidateTestGraphCli; add a check that binding labels equal model actions. |
| G6 | Silent-degrade guards on in-scope surface (the recurring 'guard that silently passes when its input is absent' class): analyze_complexity.py:1046-1052 (broken manifest -> except Exception -> None -> justification table AND manifest-sourced fitness rules silently disabled); generate_cases_from_tlc_dump.py:869-871 (scan crash -> warning -> generation proceeds ungated); fitness_functions.py:284-295 (broken rules doc -> advisory error list, never a failure — deliberate, but the disabled path is a behavior). None of these disabled paths is represented. | Sweep 3 (fallbacks) | model it | Model the degraded verdict (e.g. complexity_gate/fitness 'unknown' on unreadable input) or make the manifest-degrade loud; the MF-015 precedent is that silent fallback on the file every gate reads is the highest-risk class in this repo. |
| G7 | Runner behaviors unrepresented on the :539 boundary: scripts/run_generated_case_adapters.py batch re-exec env branch (SPEC_DOUBLE_BATCH_REEXEC, :971,:990-998), per-field unobservable declarations honored by the comparator (:469-530), and per-case python children whose own effects the sandbox is the subject of (MF-027 process-boundary rule). | Sweeps 1+3 | model it | Either widen RunSpecUnitTests/RunEffectConformance result semantics to carry the per-field unobservable distinction, or record via escalation E6 that runner internals are out of the modeled surface. |

Gaps G1, G6 (fitness-related part), and G7 carry a caveat the dispositions
table cannot express (see §6.3 E6): the plan's own acceptance text mandates
zero model delta for exactly this behavior. Per the audit doctrine that is an
argument that the plan's scope declaration should change — escalated, not
resolved here. The gaps stand until the owner amends the boundary once.

### 6.2 Out-of-scope inventory — does not gate

269 Sweep-1 rows and their effect/behavior groups, all placed by one quoted
line — `ticket_plan.yaml:520`: "Do not add test graph nodes, pytest jobs, CI
workflow steps, integration harnesses, or validation scripts as TLA+ program
state/actions."

| # | Surface | Quoted plan line |
|---|---|---|
| 1 | 53 pytest-job files (rule R2a: `tests` component or `test_*.py`/`conftest.py`), incl. the two in-scope-as-change-surface test files :1998/:2146 | :520 ("pytest jobs") |
| 2 | 214 test-graph/harness files (rule R2b: `test_graph` or `graph-reports` component) across test_graph/, examples/**/test_graph/, specs/tickets/**/graph-reports/ | :520 ("test graph nodes", "integration harnesses") |
| 3 | 2 validation entry scripts (rule R2c) | :520 ("validation scripts") |
| 4 | their effect/behavior hits (§3-§4 area groups repo-tests/spec-tests/testgraph/archived-evidence + examples R2 rows) | :520 |

### 6.3 Scope escalations — owner amends the plan, once

| # | Row | Plan line that should change | Argument |
|---|---|---|---|
| E1 | 56 Sweep-1 rows (all of scripts/ except the four exactly-named files, spec_double_compiler/*, specs adapter copies, specs/current/adapter_case_runtime.py, the example app sources, run_tlc.sh, skill-scripts/*) | service_catalog (:534-549) was inherited unchanged from the modular-fuzzing epic and never re-declared for this epic | No plan line classifies these paths in or out. The catalog predates the epic under audit; the owner should re-declare it once for the complexity-descriptor workflow. |
| E2 | scripts/tla_spec_dev.py | ticket_plan.yaml:537 | 'tla-spec-dev CLI (scaffold/open/run/close)' names a program, not a path. Exact-path closure cannot classify the file; amend to the literal path. |
| E3 | spec_manifest.yaml / actions.yml / testgraph_bindings.yml instances | ticket_plan.yaml:540 | Bare filenames with no directory. The repo has these names in specs/current/, specs/program_model/, examples/**. Which instances are the boundary? |
| E4 | Internal/External view split (Sweep 4) | ticket_plan.yaml:549 (known_gaps) | The quoted text scopes the split to MF-023 of the CONCLUDED epic; MF-023 closed as dogfooding/docs and the views were never produced (specs/current has a single module; manifest:111-113 still references three missing files). Whether the missing views are in the complexity-descriptor epic's scope is undeclared. |
| E5 | scripts/spec_evolution.py, scripts/close_ticket.py destructive-delete findings | ticket_plan.yaml:688 (previous_epic_tickets MF-021 implementation_scope) | Only a previous-epic ticket entry names these files. The prompt scopes by 'in-flight ticket' implementation_scope; whether the immutable MF record still confers scope is unstated. |
| E6 | G1/G6/G7 disposition | ticket_plan.yaml:2013-2017, :2093, :2162-2165 (zero-model-delta acceptance assertions) | The plan MANDATES zero TLA+ model delta for CD-01/02/03 while the audit doctrine makes their unrepresented behavior in-scope gaps. If the owner intends advisory descriptor/fitness surface to stay unmodeled, amend service_catalog once (one reviewable boundary decision); the per-ticket zero-delta assertions cannot serve as N per-finding waivers. |

---

## 7. Verdict

- In-scope gaps: **7** (G1-G7)
- Out-of-scope inventoried: **269 files** + their effect/behavior groups (all per :520)
- Escalations: **6 escalation issues covering 56 unclassifiable files + 4 boundary questions**
- **Verdict: `FAIL`**

`FAIL` blocks promotion until every in-scope gap is closed by modeling it or
changing the program — or until the owner amends the scope declaration once
(E1/E6), which would reclassify G1/G6/G7 and part of G2; G3/G4/G5 are concrete
model/manifest/binding desyncs that no scope amendment dissolves.

Comparison to run 1 (MF-026, 2026-07-19): verdict INCOMPLETE, 19 in-scope
gaps, 145/160 rows escalated. Desyncs (1) missing Core/Internal/External, (2)
@port vocabulary empty intersection, (3) missing views, (4)
manifest-describes-absent-surface are ALL STILL OPEN and re-verified fresh
(§1). This run's surface is larger (332 vs 160: validation examples and
archived graph-report trees landed since), its escalation count is lower
because :520 was applied as the out-of-scope authority, and its verdict is
FAIL rather than INCOMPLETE because every enumerated surface was swept and the
gaps are concrete.

---

## 8. Attestation

1. **Row-count reconciliation per sweep:**
   - Step 1 index: mandated regex N=37 (defective — see item 6); corrected N=42; ports 5; action-port rows 13; bindings 11. Table reflects corrected enumeration.
   - Sweep 1: N=332 (2068+546+130+312+5 raw, minus the one stated `.history` filter), M=332. **N == M.**
   - Sweep 2: raw N per category 2312/976/60/314/272/5/87; every raw hit machine-partitioned into groups (group sums verified equal to N per category by the partition script); collapsed counts and collapsing rules stated per category; destructive sites enumerated per-site 26/26.
   - Sweep 3: raw N 754/95/205/182/22/639; same partition accounting; real-site collapses stated with rules (retry 95->0, concurrency 22->0, timeout 205->6, clock-style discards re-derivable from raw files).
   - Sweep 4: view modules N=1 (ls), table covers both views.
2. **Surface NOT walked:** `specs/.history/**` (stated filter; 1893 py + ~840 other-language files — sealed history copies); non-code config/template surface (`*.yaml/json/toml/cfg/md/j2` — including `templates/` j2 files, 12 files, which ARE scaffold-output-shaping program surface and were only checked via the manifest they emit — this is the closest thing to un-swept in-scope-adjacent surface); `*.tla` files as program surface (they are the audited model); jars; the two `.dot` state graphs. Kotlin/Java/kts were enumerated in Sweep 1 and grouped in Sweeps 2-3 by the same area rules but their per-line effect patterns were only the Python-pattern set plus `ProcessBuilder|Runtime.getRuntime|File(`-class matches falling out of the shared regexes; a Kotlin-specific pattern pass was NOT run separately (all such files are out per :520, but per the prompt, a category searched only in Python is a category not fully swept for those files).
3. **Rows-READ vs rows-INFERRED (Sweep 1):** READ (sections read in this session, cited by line): 10 — analyze_complexity.py, fitness_functions.py, generate_cases_from_tlc_dump.py, run_generated_case_adapters.py, specs/program_model/production_adapters.py, tla_spec_dev.py, spec_evolution.py, kill_test.py, effect_conformance.py (grep-level + patch sites), close_ticket-family flag surfaces (argparse lines only). INFERRED from path/name + Step-1 binding index: **322 of 332**, including every out-per-:520 row and every archived-evidence row. The `partial` verdicts on onboard_program_model.py, budgets.py, new_ticket_workflow.py, corpus_diagnostics.py, effect_conformance_report.py, run_kill_test.py, close_*.py and the two adapter copies rest on the verified CLI dispatch imports (tla_spec_dev.py:64-203) and binding file, not on reading those files' bodies — these are the least reliable rows in this report.
4. **Rows whose scope was decided by reasoning rather than a quoted line:** none knowingly — ambiguity was pushed to escalations E1-E6. Two judgment calls that a reviewer should audit: (a) treating `graph-reports` archived copies as ":520 test graph nodes" (they are literal copies of test-graph node sources, but :520 does not say 'archived copies'); (b) treating the two `examples/*validation*.py` entry scripts as ":520 validation scripts" by their names. Both are flagged here precisely because they sit at the edge of classification vs inference; moving them to escalations would raise the escalation file count from 56 to 95 and change no gap.
5. **Can a reader reproduce this row set from the recorded commands?** yes — every enumeration command, filter, classification rule, partition rule, and collapse rule is stated inline; raw grep outputs are committed at `specs/results/epic-close/sweep-raw/`; the classifier and partitioner logic is fully described in §2/§3 headers (rule text is the spec; the scripts are mechanical applications of it).
6. **Findings about this prompt** (required):
   - **The Step-1 mandated regex is defective:** `'^[A-Za-z_][A-Za-z0-9_]*(\(.*\))? =='` requires exactly ONE space before `==` and silently dropped the 5 alignment-padded constant definitions (TlaSpecDevCli.tla:186-190). Same failure genus as the run-1 parameterized-definition finding the prompt already fixed: the regex under-enumerates in a way that looks rigorous. Fix: `[[:space:]]+==`.
   - **Step 4's literal commands contradict Step 3's own warning:** they hardcode `scripts/ spec_double_compiler/` — exactly the narrower-than-surface defect Step 3 documents as a run-1 finding. Followed the warning, not the literal commands; the prompt should update Step 4 to `$SURFACE`.
   - **The 'in-flight ticket' scope wording is stale at workflow close:** at epic close no ticket is in-flight; whether the concluded previous epic's `implementation_scope` entries (e.g. :688 naming spec_evolution.py) still confer scope is undecidable from the prompt (escalation E5).
   - **Where a plausible report could have been produced without walking:** the group-disposition allowance (§3) legitimately lets whole 200-hit categories be dispositioned from path-area partitions — honest here because the partition is machine-checked and stated, but the area rule is coarse enough that a lazy agent could hide an interesting site inside a big 'other' group; the per-site destructive rule is the only structural protection, and it worked. The rows-INFERRED count (322/332) is the honest price of a 332-row surface under this prompt's row-set discipline; a reader should treat §6.1's gaps (all read-verified) as load-bearing and the bulk unrepresented verdicts as default-polarity, not as read findings.
   - The zero-model-delta acceptance assertions (:2017/:2093/:2165) collide with this gate's disposition vocabulary by design (no fourth disposition), which is correct — but the prompt gives no way to record 'the plan mandates non-representation' other than an escalation, so an owner reading only §6.1 without §6.3/E6 would over-read G1/G6/G7 as unqualified defects. Recorded here so the report's own reliability is legible.
