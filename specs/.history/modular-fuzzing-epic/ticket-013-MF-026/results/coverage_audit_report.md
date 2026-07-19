# Coverage Audit Report

- **Epic / workflow:** `modular-fuzzing-epic`
- **Scope source:** `specs/desired_program_model/ticket_plan.yaml` (lines `449-464` service_catalog; 15 `implementation_scope` blocks at `486-490, 539-542, 599-601, 664-667, 720-724, 789-791, 885-888, 940-943, 1010-1013, 1075-1078, 1145-1148, 1215-1219, 1282-1286, 1329-1332, 1373-1377`)
- **Model audited:** `specs/current/TlaSpecDevCli.tla` @ `1176aa261bb164e5e621186e4c24db20fa456e2d`
- **Date:** `2026-07-19`
- **Verdict:** `INCOMPLETE`

> This audit checks **completeness of what is modeled**, not fidelity. The four
> oracles are bounded to what is already represented and cannot see this class
> of defect. See `prompts/coverage_audit.md`.

**Read this first.** Two independent conditions produce the `INCOMPLETE`:

1. **Step 0 HALT fired.** The plan's scope declaration is an *inclusion list of
   individual file paths*. It names 15 of the 160 files the Sweep-1 enumeration
   returned. It contains no exclusion rule, so for the remaining 145 files there
   is no plan line to quote in either direction. Per Step 0 those are
   escalations, not classifications.
2. **Three sweep categories could not be enumerated at the row granularity the
   prompt mandates** (Sweep 2 Filesystem = 225 rows; Sweep 3 Fallbacks = 196;
   Sweep 3 Config = 314). They are declared INCOMPLETE below with the honest
   reason rather than silently sampled.

The sweeps were still run and the surface is reported as an inventory, per the
dispatch instruction.

---

## 0. Declared scope (quoted verbatim from the plan)

```yaml
# specs/desired_program_model/ticket_plan.yaml:449-464
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
    - "This repository's baseline is a single TlaSpecDevCli.tla module without the Internal/External view split that SKILL.md mandates for onboarded projects. Originally recorded as out of scope for this epic. Owner direction 2026-07-18: it is now IN scope but scheduled LAST, as MF-023 at promotion_order 85, after every mechanism ticket has landed. The decomposition is to be performed by running the finished toolchain on this repository itself — analyze complexity for the cut, corpus distillation, effect conformance, External channel enforcement, and the mutation kill test — making it the epic's first end-to-end dogfooding test rather than a hand migration. It is therefore both the migration and the acceptance test of everything the epic built. See references/migration.md and tickets/023-decompose-via-dogfooding.md."
```

The 15 `implementation_scope` blocks, quoted verbatim:

```yaml
# ticket_plan.yaml:486-490 (MF-012)
    implementation_scope:
      - scripts/tla_spec_dev.py (scaffold project/workflow budget emission)
      - scripts/onboard_program_model.py
      - templates/ manifest templates
      - references/modular_fuzzing.md defaults kept in sync
# ticket_plan.yaml:539-542 (MF-020)
      - specs/program_model/TlaSpecDevCli.tla (variable and invariant rewrite)
      - specs/program_model/production_adapters.py (phase-aware adapters)
      - specs/current/tests (adapter assertions referencing the booleans)
# ticket_plan.yaml:599-601 (MF-021)
      - scripts/spec_evolution.py (replace_tree / promote_ticket_outputs)
      - scripts/close_ticket.py (close-time reporting of removals)
# ticket_plan.yaml:664-667 (MF-011)
      - scripts/analyze_complexity.py (new)
      - scripts/tla_spec_dev.py (analyze subcommand)
      - scripts/generate_cases_from_tlc_dump.py (gate integration)
# ticket_plan.yaml:720-724 (MF-022)
      - scripts/budgets.py (new max_state_space_bound default)
      - scripts/analyze_complexity.py (gate the bound against the new budget)
      - scripts/onboard_program_model.py (emit the new budget at scaffold time)
      - specs/program_model/TlaSpecDevCli.tla (setup_phase collapse)
# ticket_plan.yaml:789-791 (MF-014)
      - scripts/generate_cases_from_tlc_dump.py
      - scripts/export_testgraph_cases.py
# ticket_plan.yaml:885-888 (MF-013)
      - scripts/run_generated_case_adapters.py
      - spec_double_compiler/runtime.py
      - actions.yml / spec_manifest.yaml effect declarations
# ticket_plan.yaml:940-943 (MF-025)
      - specs/program_model/TlaSpecDevCli.tla (variable, guard and invariant rewrite)
      - specs/program_model/production_adapters.py (lifecycle-aware adapters)
      - specs/current/tests (adapter assertions referencing the removed variables)
# ticket_plan.yaml:1010-1013 (MF-015)
      - scripts/run_generated_case_adapters.py (testgraph path)
      - scripts/export_testgraph_cases.py
      - testgraph_bindings.yml schema
# ticket_plan.yaml:1075-1078 (MF-027)
      - scripts/effect_conformance.py (observability determination and refusal)
      - scripts/effect_conformance_report.py (unobservable verdict)
      - references/modular_fuzzing.md and SKILL.md (declared observable scope)
# ticket_plan.yaml:1145-1148 (MF-016)
      - scripts/run_kill_test.py (new) or documented procedure with runner support
      - examples/distributed_history/ worked kill test
      - references/modular_fuzzing.md kept in sync
# ticket_plan.yaml:1215-1219 (MF-017)
      - scripts/close_ticket.py
      - scripts/close_spec_workflow.py
      - scripts/close_tickets.py
      - references/migration.md kept in sync
# ticket_plan.yaml:1282-1286 (MF-019)
      - scripts/close_ticket.py and scripts/close_spec_workflow.py (ledger entry, delta report, anti-gaming check, refinement-loop record)
      - scripts/analyze_complexity.py (ledger-format output)
      - spec_manifest.yaml complexity_ledger schema
      - SKILL.md / references/architecture_tractability.md consistency check
# ticket_plan.yaml:1329-1332 (MF-026, this ticket)
      - a checked-in sub-agent prompt and report template
      - SKILL.md and epic doctrine updated with the required end-of-epic ordering
      - worked example run against this repository, included as evidence
# ticket_plan.yaml:1373-1377 (MF-023)
      - specs/program_model/ (Core.tla / Internal.tla / External.tla split)
      - specs/program_model/production_adapters.py (per-view adapters)
      - specs/program_model/spec_manifest.yaml (reconcile the MF-020/MF-022 desync recorded in epic notes)
      - test_graph specWorkflow / cliWorkflow bindings
```

One further scope-bearing line, quoted because three Sweep-3 findings depend on it:

```yaml
# ticket_plan.yaml:332-340
    SCOPE CORRECTION by owner, same day -- the audit over-corrected. The rule
    is do not codify the ALLOWANCE OF BAD CASES; it is not remove every
    override. An override someone types is an accepted cost, visible at the
    call site. A filter that quietly runs is a hidden loss. --allow-over-budget,
    the budgets fallback and the justification-table behavior all STAY. MF-024
    (which proposed purging them from shipped code) is WITHDRAWN and its issue
    closed; its residue -- confirming overrides are explicit, visible, recorded
    and never the default path -- is absorbed into MF-023, where the toolchain
    is actually driven end to end and where a silent default would show up.
```

| Scope line | Covers |
|---|---|
| `ticket_plan.yaml:451` | the tla-spec-dev CLI surface (scaffold/open/run/close) as an existing boundary |
| `ticket_plan.yaml:452` | `scripts/generate_cases_from_tlc_dump.py` |
| `ticket_plan.yaml:453` | `scripts/run_generated_case_adapters.py` |
| `ticket_plan.yaml:454` | `spec_manifest.yaml` / `actions.yml` / `testgraph_bindings.yml` schemas |
| `ticket_plan.yaml:456-459` | budgets block, analyze-complexity gate, sandboxed effect observation, channel-authentic bindings |
| `ticket_plan.yaml:461-462` | `production_adapters.py`; `test_graph specWorkflow / cliWorkflow graphs` |
| `ticket_plan.yaml:464` | the missing Internal/External split — explicitly **IN scope**, scheduled as MF-023 |
| `ticket_plan.yaml:487-1377` | the 15 individually-named implementation files listed above |

### HALT: the plan's scope declaration is insufficient to run this gate

**The owner must amend it.** Stated precisely, so the amendment is targeted:

1. **The declaration is an inclusion list with no closure rule.** It names
   individual files. It never says what the complement means. Sweep 1 returned
   **160** files; exact-path plan mentions cover **15**. For the other **145**
   there is no plan line to quote in either direction.
2. **I declined to infer directory closure.** A first pass treated
   "`scripts/tla_spec_dev.py` is named" as putting `scripts/` in scope, which
   moved 103 of 160 rows to `in-scope`. That inference is *reasoning, not
   quoting*, and Step 0 forbids it, so it was reverted. The strict result — 15
   in-scope, 145 escalations — is the honest one. The difference between the
   two runs (88 rows) is the size of the judgment call the prompt leaves open,
   and is recorded in Attestation §4.
3. **Two named scope lines are qualified in ways that cannot be resolved
   mechanically.** `ticket_plan.yaml:1147` reads
   "`examples/distributed_history/ worked kill test`" — it names a directory
   *and* a qualifier. Whether it scopes the whole 70-file example tree
   (including a `ThreadingHTTPServer`, k3d cluster provisioning, and a second
   byte-identical copy of the Test Graph engine) or only the kill-test artifact
   cannot be decided without interpreting. `ticket_plan.yaml:462` reads
   "`test_graph specWorkflow / cliWorkflow graphs`" under the heading
   `adapter_boundaries` — whether "adapter boundary" means in-scope-for-modeling
   or out-of-scope-because-adapter is exactly the interpretation Step 0 forbids.
4. **The scope as written does not cover surface plainly visible.** 42 Kotlin
   files, 24 Java files, 10 Gradle scripts and 5 shell scripts are program
   surface in the repository's own working tree, executed by `specWorkflow` and
   `cliWorkflow`, and named nowhere in any scope block.

Per Step 0 the correct output is: **the plan's scope declaration is
insufficient to run this gate — the owner must amend it.** The classification
column below is therefore *unresolvable for 145 of 160 rows* and is marked
`ESCALATION` rather than being resolved by the auditor.

**Escalations (ambiguous boundary):**

| Row | Why the plan text does not classify it |
|---|---|
| Sweep-1 rows 1-20, 68-71 (`examples/distributed_history/**`, 70 files) | `ticket_plan.yaml:1147` names the directory but qualifies it "worked kill test". Cannot decide whether the qualifier narrows the directory without interpreting. |
| Sweep-1 rows 21-67 (`examples/distributed_history/test_graph/**`) | Byte-identical fork of the root Test Graph engine (verified: all 22 `.kt` and 12 `.java` MD5-match). Falls under the same unresolvable `:1147` qualifier, and additionally under the `:462` `adapter_boundaries` ambiguity. |
| Sweep-1 rows 106-150 (`test_graph/build-logic/**`, `test_graph/sdk/**`) | `ticket_plan.yaml:462` names the *graphs*, not the engine or the SDKs that run them. No line names this surface. |
| Sweep-1 rows 151-160 (`test_graph/sources/*.py`) | These are the specWorkflow/cliWorkflow *nodes*. Whether `:462`'s "graphs" reaches the node sources is interpretation. |
| Sweep-1 rows 77-80, 86-89, 93-96, 98, 100, 104 (14 unnamed `scripts/*.py` + `spec_double_compiler/__init__.py`) | Sibling modules in a directory whose *other* members are named. No line names these. `scripts/complexity_ledger.py` is the sharpest case: MF-019's scope names `close_ticket.py`, `close_spec_workflow.py` and `analyze_complexity.py`, but not the ledger module those three delegate to. |
| Sweep-1 rows 102-103 (`skill-scripts/*.sh`) | `install-tla-spec-dev.sh` is the mechanism behind the modeled `InstallLocalCli` action, yet no scope line names it. Modeled but unscoped is a contradiction only the owner can resolve. |
| Sweep-1 row 84 (`scripts/extract_spec_manifest.py`) | `:454` scopes the "spec_manifest.yaml schema"; this module is its parser. Whether scoping a schema scopes its parser is interpretation. |

---

## 1. Model representation index

Commands run (Step 1, verbatim):

```bash
grep -n '^[A-Za-z_][A-Za-z0-9_]* ==' specs/current/*.tla          # -> 24 lines
grep -n 'ports\|effects\|channel' specs/current/spec_manifest.yaml # -> 24 lines
cat specs/current/actions.yml                                      # -> FAILED, no such file
cat specs/current/testgraph_bindings.yml                           # -> FAILED, no such file
```

**Two of the four Step-1 commands are not runnable in this repository, and a
third is wrong.** See Attestation §6; recorded here because it changes what the
index contains.

- `specs/current/actions.yml` and `specs/current/testgraph_bindings.yml` **do
  not exist**. `git ls-files` finds those filenames only under
  `examples/distributed_history/specs/program_model/`. The binding list the
  prompt asks for cannot be produced from the path it specifies.
- The action grep **undercounts by 13**. `^[A-Za-z_][A-Za-z0-9_]* ==` cannot
  match a parameterized definition, and in this model every state-changing
  action takes parameters. It returns 24 definitions and silently omits
  `ScaffoldProject(root)`, `RecordBudgets(root)`, `OpenTicket(root, ticket)`,
  `RunSpecUnitTests(root, ticket, override)`, `CloseTicket(root, ticket)` and 8
  more — **i.e. it omits almost exactly the set of things a coverage audit maps
  rows to.** The corrected pattern
  `^[A-Za-z_][A-Za-z0-9_]*(\(.*\))? ==` returns **37**. The index below uses the
  corrected pattern.

### Actions (15 state-changing; `specs/current/TlaSpecDevCli.tla`)

| Kind | Name | `file:line` |
|---|---|---|
| Action | `BuildSkillCli` | `TlaSpecDevCli.tla:215` |
| Action | `InstallLocalCli` | `TlaSpecDevCli.tla:231` |
| Action | `ScaffoldProject(root)` | `TlaSpecDevCli.tla:248` |
| Action | `RecordBudgets(root)` | `TlaSpecDevCli.tla:269` |
| Action | `ScaffoldWorkflow(root)` | `TlaSpecDevCli.tla:287` |
| Action | `OpenTicket(root, ticket)` | `TlaSpecDevCli.tla:305` |
| Action | `UpdateTicketDesired(ticket)` | `TlaSpecDevCli.tla:328` |
| Action | `UpdateTicketCurrent(ticket)` | `TlaSpecDevCli.tla:345` |
| Action | `AnalyzeComplexity(root)` | `TlaSpecDevCli.tla:370` |
| Action | `AnalyzeCorpus(root)` | `TlaSpecDevCli.tla:402` |
| Action | `RunEffectConformance(root)` | `TlaSpecDevCli.tla:439` |
| Action | `RunKillTest(root)` | `TlaSpecDevCli.tla:492` |
| Action | `RunSpecUnitTests(root, ticket, override)` | `TlaSpecDevCli.tla:519` |
| Action | `CloseTicket(root, ticket)` | `TlaSpecDevCli.tla:580` |
| Action | `Stutter` | `TlaSpecDevCli.tla:597` |

### Ports (5 declared; `specs/current/spec_manifest.yaml`)

| Kind | Name | Type / target | `file:line` |
|---|---|---|---|
| Port | `spec_tree` | `filesystem.write` `**/specs/**` | `spec_manifest.yaml:154-156` |
| Port | `evidence_report` | `filesystem.write` `**/results/**` | `spec_manifest.yaml:157-159` |
| Port | `cli_artifact` | `filesystem.write` `**/.venv/**` | `spec_manifest.yaml:160-162` |
| Port | `tlc_process` | `process.spawn` `*java*` | `spec_manifest.yaml:163-165` |
| Port | `test_process` | `process.spawn` `*pytest*` | `spec_manifest.yaml:166-168` |

Note `spec_manifest.yaml:122` also carries a top-level `ports: {}` — empty, and
distinct from the `effects.components` block above. Only the 5 above are live.

### Action→port bindings (13; `spec_manifest.yaml:169-182`)

`BuildSkillCli`→[cli_artifact]; `InstallLocalCli`→[cli_artifact];
`ScaffoldProject`→[spec_tree]; `ScaffoldWorkflow`→[spec_tree];
`OpenTicket`→[spec_tree]; `UpdateTicketDesired`→[spec_tree];
`UpdateTicketCurrent`→[spec_tree]; `AnalyzeComplexity`→[evidence_report,
tlc_process]; `AnalyzeCorpus`→[evidence_report];
`RunEffectConformance`→[evidence_report]; `RunKillTest`→[evidence_report,
test_process]; `RunSpecUnitTests`→[test_process, spec_tree];
`CloseTicket`→[spec_tree].

### Two index-level defects found while building this table

- **`RecordBudgets` is a modeled action with no entry in
  `effects.actions`.** The map at `spec_manifest.yaml:169-182` binds 13 of the
  14 non-stutter actions. `RecordBudgets` (`TlaSpecDevCli.tla:269`) is absent,
  so every effect it performs — it writes the `budgets:` block into
  `spec_manifest.yaml` — is undeclared by construction. Gap **G3**.
- **All 15 `@port` annotations in the TLA name ports that do not exist.** The
  module annotates each action with e.g. `@port TlaSpecDevCliPort.record_budgets`
  (`TlaSpecDevCli.tla:268`), `@port TlaSpecDevCliPort.close_ticket` (`:579`).
  The declared port set is `{spec_tree, evidence_report, cli_artifact,
  tlc_process, test_process}`. **The intersection is empty** — the model and the
  manifest use two disjoint naming schemes for the same concept, and nothing in
  the shipped toolchain cross-checks them. Gap **G4**.

---

## 2. Sweep 1 — Program surface

**Enumeration** (one per language present; `git ls-files | sed 's/.*\.//' | sort | uniq -c` used to establish the language set):

```bash
git ls-files '*.py'   | grep -v '^tests/' | grep -v '^specs/' | sort   # N =  79
git ls-files '*.java' | grep -v '^tests/' | grep -v '^specs/' | sort   # N =  24
git ls-files '*.kt'   | grep -v '^tests/' | grep -v '^specs/' | sort   # N =  42
git ls-files '*.kts'  | grep -v '^tests/' | grep -v '^specs/' | sort   # N =  10
git ls-files '*.sh'   | grep -v '^tests/' | grep -v '^specs/' | sort   # N =   5
```

raw count **N = 160**; table rows **M = 160**; `N == M`: ☑

> **A note on the prompt's exclusion filter, since it changes the row set.**
> `grep -v '^specs/'` is anchored, so it drops the repository's own `specs/`
> tree but *keeps* `examples/distributed_history/specs/**` (11 files, rows 7-20).
> The filter therefore excludes `specs/current/production_adapters.py` and
> `specs/desired_program_model/production_adapters.py` — which
> `ticket_plan.yaml:461` names as an explicit adapter boundary — while including
> the example's generated case modules. This asymmetry is the prompt's, not a
> local adaptation; the commands were run verbatim.

Verdicts: `represented` / `partial` (name the uncovered part) / `unrepresented`.
Default polarity is `unrepresented` — coverage is granted only on cited
positive evidence.

**Distribution: `represented` 0 · `partial` 19 · `unrepresented` 141.**
**Scope: `in-scope` 15 · `ESCALATION` 145.** No row earned `represented`: in
every case where a named action covers the module's command, at least one
behavior of that module is outside the action, which is `partial` by the
prompt's own rule.

| # | Module (`path`) | In/Out | Plan line | Spec action(s) representing it | Verdict | Evidence |
|---|---|---|---|---|---|---|
| 1 | `examples/distributed_history/ecommerce_backend/__init__.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 2 | `examples/distributed_history/ecommerce_backend/domain.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 3 | `examples/distributed_history/ecommerce_backend/service.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 4 | `examples/distributed_history/scripts/k3d-up.sh` | ESCALATION | **none** | — | `unrepresented` | — |
| 5 | `examples/distributed_history/scripts/k8s-deploy.sh` | ESCALATION | **none** | — | `unrepresented` | — |
| 6 | `examples/distributed_history/scripts/regenerate_tlc_cases.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 7 | `examples/distributed_history/specs/__init__.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 8 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/__init__.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 9 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/cases.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 10 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/types.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 11 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/validators.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 12 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/__init__.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 13 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/cases.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 14 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/types.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 15 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/validators.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 16 | `examples/distributed_history/specs/program_model/__init__.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 17 | `examples/distributed_history/specs/program_model/adapters.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 18 | `examples/distributed_history/specs/program_model/tests/test_ecommerce_adapters.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 19 | `examples/distributed_history/specs/program_model/tlc_projection.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 20 | `examples/distributed_history/test_graph/build-logic/build.gradle.kts` | ESCALATION | **none** | — | `unrepresented` | — |
| 21 | `examples/distributed_history/test_graph/build-logic/settings.gradle.kts` | ESCALATION | **none** | — | `unrepresented` | — |
| 22 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Context.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 23 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Executors.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 24 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/JBangExecutor.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 25 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/PlanExecutor.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 26 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/TimeoutParser.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 27 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/UvExecutor.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 28 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphAssembler.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 29 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphModel.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 30 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/MiniJson.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 31 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/NodeDescribeLoader.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 32 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/InspectionTasks.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 33 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunReportWriter.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 34 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunTestGraphTask.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 35 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/ValidationReportTask.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 36 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/TestGraphSpec.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 37 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/Toolchain.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 38 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphExtension.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 39 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphPlugin.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 40 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationNodeSpec.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 41 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationRuntime.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 42 | `examples/distributed_history/test_graph/build-logic/src/test/kotlin/com/hayden/testgraphsdk/exec/PlanExecutorResumeHarnessTest.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 43 | `examples/distributed_history/test_graph/build.gradle.kts` | ESCALATION | **none** | — | `unrepresented` | — |
| 44 | `examples/distributed_history/test_graph/sdk/java/build.gradle.kts` | ESCALATION | **none** | — | `unrepresented` | — |
| 45 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextItem.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 46 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextSerde.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 47 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Json.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 48 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/JsonMapper.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 49 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Node.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 50 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeBody.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 51 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeContext.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 52 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeResult.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 53 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeSpec.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 54 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeStatus.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 55 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ProcessRecord.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 56 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Procs.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 57 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/__init__.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 58 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/context_item.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 59 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/context.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 60 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/node_spec.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 61 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/procs.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 62 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/result.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 63 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/runner.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 64 | `examples/distributed_history/test_graph/settings.gradle.kts` | ESCALATION | **none** | — | `unrepresented` | — |
| 65 | `examples/distributed_history/test_graph/sources/cleanup_ecommerce.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 66 | `examples/distributed_history/test_graph/sources/collect_evidence.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 67 | `examples/distributed_history/test_graph/sources/deploy_ecommerce.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 68 | `examples/distributed_history/test_graph/sources/run_external_cases.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 69 | `examples/distributed_history/tests/test_ecommerce_backend.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 70 | `examples/run_distributed_history_validation.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 71 | `examples/validate_split_desired_workflow.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 72 | `scripts/analyze_complexity.py` | in-scope | L665 (`scripts/analyze_complexity.py`); L722 (`scripts/analyze_complexity.py`); L1284 (`scripts/analyze_complexity.py`) | AnalyzeComplexity — uncovered: justification-table-absent -> dead-weight analysis skipped (analyze_complexity.py:1084) unmodeled | `partial` | TlaSpecDevCli.tla:367-370 |
| 73 | `scripts/budgets.py` | in-scope | L721 (`scripts/budgets.py`) | RecordBudgets — uncovered: budgets-absent -> documented-default fallback path (budgets.py:157-190) unmodeled | `partial` | TlaSpecDevCli.tla:266-269 |
| 74 | `scripts/close_spec_workflow.py` | in-scope | L1217 (`scripts/close_spec_workflow.py`); L1283 (`scripts/close_spec_workflow.py`) | — | `unrepresented` | — |
| 75 | `scripts/close_ticket.py` | in-scope | L601 (`scripts/close_ticket.py`); L1216 (`scripts/close_ticket.py`); L1283 (`scripts/close_ticket.py`) | CloseTicket — uncovered: no CloseWorkflow action exists; workflow-close lifecycle unmodeled | `partial` | TlaSpecDevCli.tla:577-580 |
| 76 | `scripts/close_tickets.py` | in-scope | L1218 (`scripts/close_tickets.py`) | — | `unrepresented` | — |
| 77 | `scripts/close-spec-workflow.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 78 | `scripts/close-ticket.py` | ESCALATION | **none** | CloseTicket | `partial` | TlaSpecDevCli.tla:577-580 |
| 79 | `scripts/complexity_ledger.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 80 | `scripts/corpus_diagnostics.py` | ESCALATION | **none** | AnalyzeCorpus — uncovered: hard-cap refusal path unmodeled | `partial` | TlaSpecDevCli.tla:399-402 |
| 81 | `scripts/effect_conformance_report.py` | in-scope | L1077 (`scripts/effect_conformance_report.py`) | RunEffectConformance — uncovered: exit-code 1/2 discrimination unmodeled | `partial` | TlaSpecDevCli.tla:436-439 |
| 82 | `scripts/effect_conformance.py` | in-scope | L1076 (`scripts/effect_conformance.py`) | RunEffectConformance — uncovered: sandbox observes only in-process Python; JVM/Gradle runtime effects unobservable | `partial` | TlaSpecDevCli.tla:436-439 |
| 83 | `scripts/export_testgraph_cases.py` | in-scope | L791 (`scripts/export_testgraph_cases.py`); L1012 (`scripts/export_testgraph_cases.py`) | — | `unrepresented` | — |
| 84 | `scripts/extract_spec_manifest.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 85 | `scripts/generate_cases_from_tlc_dump.py` | in-scope | L452 (`scripts/generate_cases_from_tlc_dump.py`); L667 (`scripts/generate_cases_from_tlc_dump.py`); L790 (`scripts/generate_cases_from_tlc_dump.py`) | AnalyzeComplexity (gate only) — uncovered: shutil.rmtree of metadir (:95) unmodeled | `partial` | TlaSpecDevCli.tla:367-370 |
| 86 | `scripts/generate_docs.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 87 | `scripts/generate_python.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 88 | `scripts/kill_test.py` | ESCALATION | **none** | RunKillTest — uncovered: 600s per-mutant subprocess timeout (:592,:614) unmodeled | `partial` | TlaSpecDevCli.tla:489-492 |
| 89 | `scripts/new_ticket_workflow.py` | ESCALATION | **none** | OpenTicket | `partial` | TlaSpecDevCli.tla:302-305 |
| 90 | `scripts/onboard_program_model.py` | in-scope | L488 (`scripts/onboard_program_model.py`); L723 (`scripts/onboard_program_model.py`) | ScaffoldProject — uncovered: emits Core/Internal/External baseline this repo does not itself have | `partial` | TlaSpecDevCli.tla:245-248 |
| 91 | `scripts/run_generated_case_adapters.py` | in-scope | L453 (`scripts/run_generated_case_adapters.py`); L886 (`scripts/run_generated_case_adapters.py`); L1011 (`scripts/run_generated_case_adapters.py`) | RunSpecUnitTests — uncovered: asyncio adapter path (:389-391), tempfile work dir (:965), batch re-exec env (:875-896) unmodeled | `partial` | TlaSpecDevCli.tla:516-519 |
| 92 | `scripts/run_kill_test.py` | in-scope | L1146 (`scripts/run_kill_test.py`) | RunKillTest — uncovered: --timeout default 600 (:104,:198) unmodeled | `partial` | TlaSpecDevCli.tla:489-492 |
| 93 | `scripts/run_tlc.sh` | ESCALATION | **none** | AnalyzeComplexity (tlc_process port) | `partial` | spec_manifest.yaml:163-165 |
| 94 | `scripts/scaffold_spec_workflow.py` | ESCALATION | **none** | ScaffoldWorkflow | `partial` | TlaSpecDevCli.tla:284-287 |
| 95 | `scripts/scaffold_spec.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 96 | `scripts/skill_feedback.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 97 | `scripts/spec_evolution.py` | in-scope | L600 (`scripts/spec_evolution.py`) | CloseTicket — uncovered: git subprocess (:99-100) and datetime.now stamps (:770,:883) unmodeled | `partial` | TlaSpecDevCli.tla:577-580 |
| 98 | `scripts/spec_paths.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 99 | `scripts/start_ticket.py` | ESCALATION | **none** | OpenTicket | `partial` | TlaSpecDevCli.tla:302-305 |
| 100 | `scripts/testgraph_channels.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 101 | `scripts/tla_spec_dev.py` | in-scope | L487 (`scripts/tla_spec_dev.py`); L666 (`scripts/tla_spec_dev.py`) | BuildSkillCli/InstallLocalCli/Scaffold*/Open*/Update*/Analyze*/Run*/CloseTicket — uncovered: no action for `close workflow`; incomplete-command/exit-code paths unmodeled | `partial` | TlaSpecDevCli.tla:212-579 |
| 102 | `skill-scripts/install-tla-spec-dev.sh` | ESCALATION | **none** | InstallLocalCli | `partial` | TlaSpecDevCli.tla:228-231 |
| 103 | `skill-scripts/install-tlc2.sh` | ESCALATION | **none** | — | `unrepresented` | — |
| 104 | `spec_double_compiler/__init__.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 105 | `spec_double_compiler/runtime.py` | in-scope | L887 (`spec_double_compiler/runtime.py`) | — | `unrepresented` | — |
| 106 | `test_graph/build-logic/build.gradle.kts` | ESCALATION | **none** | — | `unrepresented` | — |
| 107 | `test_graph/build-logic/settings.gradle.kts` | ESCALATION | **none** | — | `unrepresented` | — |
| 108 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Context.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 109 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Executors.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 110 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/JBangExecutor.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 111 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/PlanExecutor.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 112 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/TimeoutParser.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 113 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/UvExecutor.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 114 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphAssembler.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 115 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphModel.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 116 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/MiniJson.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 117 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/NodeDescribeLoader.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 118 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/InspectionTasks.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 119 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunReportWriter.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 120 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunTestGraphTask.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 121 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/ValidationReportTask.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 122 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/TestGraphSpec.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 123 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/Toolchain.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 124 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphExtension.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 125 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphPlugin.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 126 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationNodeSpec.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 127 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationRuntime.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 128 | `test_graph/build-logic/src/test/kotlin/com/hayden/testgraphsdk/exec/PlanExecutorResumeHarnessTest.kt` | ESCALATION | **none** | — | `unrepresented` | — |
| 129 | `test_graph/build.gradle.kts` | ESCALATION | **none** | — | `unrepresented` | — |
| 130 | `test_graph/sdk/java/build.gradle.kts` | ESCALATION | **none** | — | `unrepresented` | — |
| 131 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextItem.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 132 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextSerde.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 133 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Json.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 134 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/JsonMapper.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 135 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Node.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 136 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeBody.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 137 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeContext.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 138 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeResult.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 139 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeSpec.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 140 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeStatus.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 141 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ProcessRecord.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 142 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Procs.java` | ESCALATION | **none** | — | `unrepresented` | — |
| 143 | `test_graph/sdk/python/src/testgraphsdk/__init__.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 144 | `test_graph/sdk/python/src/testgraphsdk/context_item.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 145 | `test_graph/sdk/python/src/testgraphsdk/context.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 146 | `test_graph/sdk/python/src/testgraphsdk/node_spec.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 147 | `test_graph/sdk/python/src/testgraphsdk/procs.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 148 | `test_graph/sdk/python/src/testgraphsdk/result.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 149 | `test_graph/sdk/python/src/testgraphsdk/runner.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 150 | `test_graph/settings.gradle.kts` | ESCALATION | **none** | — | `unrepresented` | — |
| 151 | `test_graph/sources/spec_workflow_cleanup.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 152 | `test_graph/sources/spec_workflow_close_ticket.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 153 | `test_graph/sources/spec_workflow_complete_ticket.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 154 | `test_graph/sources/spec_workflow_create_repo.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 155 | `test_graph/sources/spec_workflow_failure_cleanup_probe.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 156 | `test_graph/sources/spec_workflow_force_failure.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 157 | `test_graph/sources/spec_workflow_spec_units.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 158 | `test_graph/sources/spec_workflow_start_ticket.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 159 | `test_graph/sources/tla_spec_dev_cli_help.py` | ESCALATION | **none** | — | `unrepresented` | — |
| 160 | `test_graph/sources/tla_spec_dev_cli_install.py` | ESCALATION | **none** | — | `unrepresented` | — |

---

## 3. Sweep 2 — Effects, by category

All seven commands were run verbatim over `scripts/ spec_double_compiler/`.

> **Scope note that governs every category below.** The prompt hardcodes
> `scripts/ spec_double_compiler/` as the grep target, but Sweep 1 enumerated
> **160** files across five languages. Sweep 2 therefore covers a strictly
> smaller surface than Sweep 1 by construction. Re-running the same seven
> patterns over `test_graph/` and `examples/` returns **233 additional hits**
> (Filesystem 120, Subprocess 28, Network 20, Environment 31, Clock 27,
> Persistent store 7) that the prompt's Sweep 2 never sees. Those are reported
> as a supplementary category in §3.8 rather than dropped.

**Standing verdict rule for this repository.** The declared port set admits only
three filesystem globs (`**/specs/**`, `**/results/**`, `**/.venv/**`) and two
spawn globs (`*java*`, `*pytest*`). Any site outside those is `undeclared`.
Additionally, `spec_manifest.yaml:145-149` restricts `type` to
`filesystem.write | filesystem.delete | process.spawn | network.connect |
network.http`. **Environment reads, clock reads and randomness have no
expressible port type at all** — they are not merely undeclared, they are
undeclarable under the current schema. That is recorded as gap **G9**.

### 3.1 Filesystem — raw `225`, collapsed `—`, rule: `NOT COLLAPSED — SWEEP INCOMPLETE`

**This category is `INCOMPLETE`.** The enumeration returns 225 rows. The prompt
authorizes collapsing *only* for false positives, with a stated rule; it
authorizes no reduction for volume, and grouping is granted only to Sweep 3's
error paths. I will not present a reduced table as if it were the enumeration.
Declaring it INCOMPLETE is the honest option the prompt offers, and I take it.

What was walked, and is reported as partial evidence:

**(a) Per-file distribution of all 225 hits — this accounts for every raw row.**

| # | File | Hits | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `scripts/new_ticket_workflow.py` | 33 | ESCALATION | none | — | `undeclared` |
| 2 | `scripts/spec_evolution.py` | 22 | in-scope | L600 | `spec_tree` (partial) | `partial` |
| 3 | `scripts/tla_spec_dev.py` | 19 | in-scope | L487 | `spec_tree` (partial) | `partial` |
| 4 | `scripts/kill_test.py` | 16 | ESCALATION | none | — | `undeclared` |
| 5 | `scripts/effect_conformance.py` | 14 | in-scope | L1076 | `evidence_report` (partial) | `partial` |
| 6 | `scripts/analyze_complexity.py` | 14 | in-scope | L665 | `evidence_report` (partial) | `partial` |
| 7 | `scripts/run_generated_case_adapters.py` | 13 | in-scope | L886 | `spec_tree`,`test_process` (partial) | `partial` |
| 8 | `scripts/complexity_ledger.py` | 13 | ESCALATION | none | — | `undeclared` |
| 9 | `scripts/onboard_program_model.py` | 10 | in-scope | L488 | `spec_tree` (partial) | `partial` |
| 10 | `scripts/run_kill_test.py` | 9 | in-scope | L1146 | `evidence_report` (partial) | `partial` |
| 11 | `scripts/effect_conformance_report.py` | 9 | in-scope | L1077 | `evidence_report` (partial) | `partial` |
| 12 | `scripts/generate_cases_from_tlc_dump.py` | 7 | in-scope | L667 | — | `undeclared` |
| 13 | `scripts/corpus_diagnostics.py` | 7 | ESCALATION | none | — | `undeclared` |
| 14 | `scripts/close_tickets.py` | 7 | in-scope | L1218 | `spec_tree` (partial) | `partial` |
| 15 | `scripts/scaffold_spec.py` | 6 | ESCALATION | none | — | `undeclared` |
| 16 | `scripts/skill_feedback.py` | 5 | ESCALATION | none | — | `undeclared` |
| 17 | `scripts/generate_python.py` | 3 | ESCALATION | none | — | `undeclared` |
| 18 | `scripts/generate_docs.py` | 3 | ESCALATION | none | — | `undeclared` |
| 19 | `scripts/export_testgraph_cases.py` | 3 | in-scope | L791 | — | `undeclared` |
| 20 | `scripts/start_ticket.py` | 2 | ESCALATION | none | — | `undeclared` |
| 21 | `scripts/scaffold_spec_workflow.py` | 2 | ESCALATION | none | — | `undeclared` |
| 22 | `scripts/extract_spec_manifest.py` | 2 | ESCALATION | none | — | `undeclared` |
| 23 | `scripts/close_ticket.py` | 2 | in-scope | L601 | `spec_tree` (partial) | `partial` |
| 24 | `scripts/close_spec_workflow.py` | 2 | in-scope | L1217 | — | `undeclared` |
| 25 | `scripts/testgraph_channels.py` | 1 | ESCALATION | none | — | `undeclared` |
| 26 | `scripts/budgets.py` | 1 | in-scope | L721 | — | `undeclared` |

Sum of Hits column = 225 = raw N. No hit is unaccounted for; what is missing is
the per-*site* disposition, which is why the category is INCOMPLETE.

**(b) Every destructive site, fully enumerated (17 rows).** These were walked
individually because deletion and relocation are the sites where an
unrepresented effect is least recoverable.

| # | Site | Effect | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `scripts/new_ticket_workflow.py:219` | `shutil.copyfile` | ESCALATION | none | — | `undeclared` |
| 2 | `scripts/new_ticket_workflow.py:243` | `shutil.copyfile` | ESCALATION | none | — | `undeclared` |
| 3 | `scripts/new_ticket_workflow.py:275` | `shutil.copyfile` | ESCALATION | none | — | `undeclared` |
| 4 | `scripts/close_spec_workflow.py:49` | `shutil.rmtree` | in-scope | L1217 | none — no `filesystem.delete` port is declared anywhere | `undeclared` |
| 5 | `scripts/generate_cases_from_tlc_dump.py:95` | `shutil.rmtree(metadir)` | in-scope | L667 | none | `undeclared` |
| 6 | `scripts/close_tickets.py:132` | `shutil.copy2` | in-scope | L1218 | `spec_tree` if target under `specs/` | `partial` |
| 7 | `scripts/close_tickets.py:232` | `shutil.rmtree` | in-scope | L1218 | none | `undeclared` |
| 8 | `scripts/close_tickets.py:127` | `.unlink()` | in-scope | L1218 | none | `undeclared` |
| 9 | `scripts/spec_evolution.py:137` | `shutil.copytree` | in-scope | L600 | `spec_tree` (partial) | `partial` |
| 10 | `scripts/spec_evolution.py:139` | `shutil.copy2` | in-scope | L600 | `spec_tree` (partial) | `partial` |
| 11 | `scripts/spec_evolution.py:154` | `shutil.rmtree(state_dir)` | in-scope | L600 | none | `undeclared` |
| 12 | `scripts/spec_evolution.py:372` | `shutil.copy2` | in-scope | L600 | `spec_tree` (partial) | `partial` |
| 13 | `scripts/spec_evolution.py:385` | `shutil.rmtree(dst)` | in-scope | L600 | none | `undeclared` |
| 14 | `scripts/spec_evolution.py:477` | `.unlink()` | in-scope | L600 | none | `undeclared` |
| 15 | `scripts/spec_evolution.py:718` | `shutil.move` — relocates the active dir into history | in-scope | L600 | none | `undeclared` |
| 16 | `scripts/run_generated_case_adapters.py:965` | `tempfile.mkdtemp(prefix="spec-double-cases-")` — writes under the system temp dir | in-scope | L886 | **none — outside all three declared globs** | `undeclared` |
| 17 | `scripts/run_generated_case_adapters.py:18` | `import tempfile` | in-scope | L886 | n/a (import) | n/a |

**The structural finding in this table: there is no `filesystem.delete` port in
the manifest at all**, yet 8 sites delete. The schema supports the type
(`spec_manifest.yaml:145-149` lists `filesystem.delete` as valid); nothing
declares one. Every deletion in the toolchain is undeclared. Gap **G5a**.
`tempfile.mkdtemp` at `:965` is gap **G5b** — case programs are written and
executed under `/tmp`, outside `**/specs/**`, `**/results/**` and `**/.venv/**`.

### 3.2 Subprocess — raw `16`, collapsed `16`, rule: `none — all 16 rows presented`

> A `process.spawn` port declares the spawn, not what the child did. Sites whose
> child performs its own effects are `partial` at best.

| # | Site | Effect performed | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `scripts/run_generated_case_adapters.py:896` | `subprocess.run(command, env=env)` — batch re-exec of the Python interpreter | in-scope | L886 | `test_process` `*pytest*` matches only if the command names pytest; the batch command is a bare interpreter | `undeclared` |
| 2 | `scripts/run_generated_case_adapters.py:902` | `subprocess.run([*python, str(program)])` — runs a generated case program | in-scope | L886 | `test_process` (spawn only) | `partial` — the child writes case artifacts and imports adapters; none of the child's effects are declared |
| 3 | `scripts/kill_test.py:608` | `def _invoke()` signature | ESCALATION | none | — | n/a (declaration) |
| 4 | `scripts/kill_test.py:609` | `subprocess.run(..., timeout=timeout)` — runs the corpus per mutant | ESCALATION | none | `test_process` (spawn only) | `partial` — the child executes the mutated source tree; its effects are unmodeled |
| 5 | `scripts/onboard_program_model.py:1188` | `subprocess.run(command, check=True, cwd=REPO_ROOT)` | in-scope | L488 | none matching | `partial` — spawn undeclared and child effects unmodeled |
| 6 | `scripts/generate_cases_from_tlc_dump.py:93` | `subprocess.run(command, check=True, cwd=spec_dir)` — invokes TLC | in-scope | L667 | `tlc_process` `*java*` matches when TLC runs via `java -cp`; **does not match when `tlc2` is on PATH** (`scripts/run_tlc.sh` prefers `tlc2`) | `partial` |
| 7 | `scripts/spec_evolution.py:99` | `subprocess.run(["git", *args], capture_output=True)` | in-scope | L600 | **none — `git` matches neither `*java*` nor `*pytest*`** | `undeclared` |
| 8 | `scripts/spec_evolution.py:100` | `except (OSError, subprocess.CalledProcessError)` | in-scope | L600 | n/a (handler) | n/a |
| 9 | `scripts/tla_spec_dev.py:358` | `subprocess.run(command, cwd=repo_root, env=env)` — the CLI's generic sub-invocation | in-scope | L487 | none matching in general | `partial` — the spawned child is any lifecycle script; its effects are unmodeled |
| 10-16 | `scripts/effect_conformance.py:645,684,698,699,702,705,709` | the sandbox's own `check_output`/`Popen` patching | in-scope | L1076 | n/a — **observer, not observed** | n/a |

Collapsing rule for rows 10-16, stated so it is re-derivable: a hit inside
`scripts/effect_conformance.py` between lines 640 and 730 is the instrumentation
that *implements* observation (it assigns `self._originals[...]` and installs
`PatchedPopen`), not a spawn the program performs. Row 3 is a `def` line paired
with row 4. Net real spawn sites: **7** (rows 1,2,4,5,6,7,9).

**Every one of the 7 real spawn sites is `undeclared` or `partial`. None is
cleanly `declared`.** Gap **G6**.

### 3.3 Network — raw `6`, collapsed `0`, rule: `see below`

| # | Site | Effect performed | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `scripts/onboard_program_model.py:215` | the string `"For an HTTP service it is requests."` inside an emitted TLA template | in-scope | L488 | n/a | false positive |
| 2-6 | `scripts/effect_conformance.py:716,717,722,726,939` | the sandbox's own `socket.socket.connect` patching | in-scope | L1076 | n/a — observer | false positive |

Collapsing rule: a hit is a false positive if it is (a) inside a quoted template
string emitted as documentation, or (b) inside the sandbox's patch-installation
block. **Result: zero real network effects in `scripts/`.** No network port is
declared, and none is needed here — this is the one category where the absence
of a declaration is not a gap. (Contrast §3.8: `examples/` performs real HTTP.)

### 3.4 Environment — raw `3`, collapsed `3`, rule: `none — all 3 rows presented`

| # | Site | Effect performed | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `scripts/run_generated_case_adapters.py:875` | reads `SPEC_DOUBLE_BATCH_REEXEC` to decide whether to re-exec | in-scope | L886 | **no environment port type exists in the schema** | `undeclared` |
| 2 | `scripts/run_generated_case_adapters.py:894` | `os.environ.copy()` — builds the child env | in-scope | L886 | none | `undeclared` |
| 3 | `scripts/tla_spec_dev.py:271` | `os.environ.copy()` — builds the sub-invocation env | in-scope | L487 | none | `undeclared` |

Row 1 is also a Sweep-3 config-branch row (§4.6 row 1): an environment variable
selects between two execution topologies, and the model represents neither.

### 3.5 Clock — raw `4`, collapsed `4`, rule: `none — all 4 rows presented`

| # | Site | Effect performed | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `scripts/complexity_ledger.py:705` | `datetime.now(timezone.utc)` → `recorded_at_utc` in the ledger | ESCALATION | none | none — no clock port type exists | `undeclared` |
| 2 | `scripts/spec_evolution.py:770` | `datetime.now(timezone.utc)` → `created_at_utc` in a history snapshot | in-scope | L600 | none | `undeclared` |
| 3 | `scripts/spec_evolution.py:883` | `datetime.now(timezone.utc)` → `created_at_utc` | in-scope | L600 | none | `undeclared` |
| 4 | `scripts/skill_feedback.py:86` | `datetime.now(timezone.utc)` → retro entry timestamp | ESCALATION | none | none | `undeclared` |

All four write a wall-clock value into **append-only evidence** that later gates
read. The model has no clock, no time variable, and no port type that could
express one. Gap **G9**.

### 3.6 Randomness — raw `4`, collapsed `0`, rule: `see below`

| # | Site | Effect | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `scripts/generate_python.py:381` | emits the literal `st.sampled_from(...)` into generated Hypothesis strategies | ESCALATION | none | n/a | false positive (codegen text) |
| 2 | `scripts/corpus_diagnostics.py:16` | the word "samples" in a module docstring | ESCALATION | none | n/a | false positive (prose) |
| 3 | `scripts/corpus_diagnostics.py:620` | the word "sampled" in an output string | ESCALATION | none | n/a | false positive (prose) |
| 4 | `scripts/corpus_diagnostics.py:703` | the word "sampled" in an output string | ESCALATION | none | n/a | false positive (prose) |

Collapsing rule: a hit is a false positive if the matched token occurs inside a
docstring, a user-facing message string, or emitted code text rather than being
an executed call. **Result: zero real randomness in `scripts/`.** Worth stating
positively — this toolchain is deterministic by construction at the sites this
pattern reaches, which is a genuine (small) clean result.

### 3.7 Persistent store — raw `0`, collapsed `0`, rule: `n/a`

No hits. No table. `scripts/` and `spec_double_compiler/` touch no database.

### 3.8 Supplementary — the surface Sweep 2's hardcoded paths exclude

Not part of the prompt's Sweep 2; reported because Sweep 1 enumerated it and
leaving it out would make §3 look complete when it covers less than half the
program surface. Verified by direct reading (see Attestation §3).

| # | Site | Effect performed | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `test_graph/sdk/python/src/testgraphsdk/procs.py:70` | `subprocess.Popen(argv, stdout=fh, stderr=STDOUT)` — **the single spawn primitive behind every Test Graph node** | ESCALATION | none | none matching | `undeclared` |
| 2 | `test_graph/sources/tla_spec_dev_cli_install.py:44` | spawns `skill-scripts/install-tla-spec-dev.sh` | ESCALATION | none | none | `partial` — child writes a CLI wrapper and chmods it |
| 3 | `test_graph/sources/tla_spec_dev_cli_help.py:25,36` | 12 spawns of the installed CLI | ESCALATION | none | none | `partial` |
| 4 | `test_graph/sources/spec_workflow_create_repo.py:50` | spawns `git init` / `branch -M` / `config` | ESCALATION | none | none | `undeclared` |
| 5 | `test_graph/sources/spec_workflow_start_ticket.py:73` | spawns `scaffold project`, `scaffold workflow`, `open ticket` | ESCALATION | none | none | `partial` |
| 6 | `test_graph/sources/spec_workflow_complete_ticket.py:149` | spawns the CLI | ESCALATION | none | none | `partial` |
| 7 | `test_graph/sources/spec_workflow_spec_units.py:32` | spawns `run spec-unit-tests` | ESCALATION | none | none | `partial` |
| 8 | `test_graph/sources/spec_workflow_close_ticket.py:61` | spawns `close ticket` | ESCALATION | none | none | `partial` |
| 9 | `test_graph/sources/spec_workflow_close_ticket.py:130` | spawns `git add`/`commit`/`status` | ESCALATION | none | none | `undeclared` |
| 10 | `test_graph/sources/spec_workflow_close_ticket.py:132` | `subprocess.run(["git","status","--short"])` **bypassing the SDK** — the only spawn in the tree that produces no `node-logs/` entry and is absent from the result envelope's process list | ESCALATION | none | none | `undeclared` |
| 11 | `test_graph/sources/spec_workflow_failure_cleanup_probe.py:87` | spawns a nested `gradlew cleanupFailureProbe` — **a whole second Gradle/JVM graph execution** | ESCALATION | none | none | `undeclared` |
| 12 | `test_graph/sources/spec_workflow_cleanup.py` | `shutil.rmtree` of the fixture repo | ESCALATION | none | none — no `filesystem.delete` port | `undeclared` |
| 13 | `test_graph/build-logic/**` (22 Kotlin files incl. `JBangExecutor.kt`, `UvExecutor.kt`, `PlanExecutor.kt`) | JBang/uv process execution, report writing, plan orchestration | ESCALATION | none | **unobservable — non-Python runtime** | `undeclared` |
| 14 | `examples/run_distributed_history_validation.py:411,420` | raw `socket.socket` port probe; `urlopen(base_url + "/health")` | ESCALATION | none | none | `undeclared` |
| 15 | `examples/distributed_history/test_graph/sources/deploy_ecommerce.py:153,162,174` | socket probe + HTTP `/health`, `/debug/state` | ESCALATION | none | none | `undeclared` |
| 16 | `examples/distributed_history/test_graph/sources/collect_evidence.py:64,69` | HTTP `/debug/state`, `/debug/traffic` | ESCALATION | none | none | `undeclared` |
| 17 | `examples/distributed_history/specs/program_model/adapters.py:107,112,119,159` | `urllib.request.Request` | ESCALATION | none | none | `undeclared` |
| 18 | `examples/distributed_history/ecommerce_backend/service.py:6,57,61` | `ThreadingHTTPServer`; outbound `urllib.request` | ESCALATION | none | none | `undeclared` |
| 19 | `examples/distributed_history/scripts/k3d-up.sh` | creates a k3d cluster, builds and imports a Docker image | ESCALATION | none | none | `undeclared` |
| 20 | `examples/distributed_history/scripts/k8s-deploy.sh` | applies manifests, restarts 7 deployments, polls rollout | ESCALATION | none | none | `undeclared` |
| 21 | `skill-scripts/install-tlc2.sh` | `curl` download of `tla2tools.jar` from GitHub releases | ESCALATION | none | **none — a network fetch during install** | `undeclared` |

**Row 13 and row 21 are the MF-027 process-boundary rule in its sharpest form.**
`scripts/effect_conformance.py:939` states the sandbox observes "subprocess
spawns and `socket.connect` patched in THIS interpreter". The Test Graph engine
is Kotlin executed by Gradle in a JVM; the effect sandbox **could not have seen
any of row 13, and could not have seen the `curl` in row 21.** Per the prompt's
non-negotiable rule, these are `undeclared` until proven otherwise, and
`unobservable` is not `clean`. Gap **G16**.

---

## 4. Sweep 3 — Behaviors

### 4.1 Error paths — raw `347`, groups `9`, grouping rule: `by raised/caught exception type, from the two commands below`

Grouping rule, stated so a reviewer can re-derive it:

```bash
grep -rhoE "raise [A-Za-z_][A-Za-z0-9_.]*" --include='*.py' scripts/ spec_double_compiler/ | sort | uniq -c
grep -rhoE "except [A-Za-z_(][A-Za-z0-9_.,() ]*" --include='*.py' scripts/ spec_double_compiler/ | sed 's/ as .*//' | sort | uniq -c
```

Groups are exception *types*, not files — the prompt's "distinct failure
semantics". 5 raise-tokens are prose false positives (`raise the`, `raise on`,
`raise a`, `raise consults`, `raise last_type_error`), collapsed by the rule
"the token after `raise` must be a class name, not an English word".

| # | Behavior | Trigger (`file:line`) | In/Out | Plan line | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|
| 1 | `SystemExit` — CLI refusal, 66 sites | `tla_spec_dev.py`, all gate CLIs | in-scope | L487 | `result.accepted = FALSE` via `CommandResult` (`TlaSpecDevCli.tla:197`) | `partial` — the model has a single `accepted` boolean plus a `reason`; it does not distinguish exit code 1 (gap found) from 2 (malformed declaration), which `effect_conformance_report.py` returns distinctly |
| 2 | `ValueError` — malformed input, 41 sites | throughout | in-scope | L487 | none | `unrepresented` |
| 3 | `NotImplementedError` — unimplemented adapter/protocol, 24 sites | `spec_double_compiler/runtime.py`, generated stubs | in-scope | L887 | none | `unrepresented` |
| 4 | `AssertionError` — adapter conformance failure, 15 sites | adapters | ESCALATION | none | `RunSpecUnitTests` failure branch (`TlaSpecDevCli.tla:519`) | `partial` — the action models pass/fail, not which assertion |
| 5 | `KillTestCatalogError` — incomplete mutant catalog, 13 sites | `kill_test.py:246-250,807-810` | ESCALATION | none | none — `RunKillTest` (`:492`) models a verdict, not a catalog-integrity failure | `unrepresented` |
| 6 | `EffectDeclarationError` — malformed port declaration, 13 sites | `effect_conformance.py` | in-scope | L1076 | none — distinct exit code 2 is unmodeled | `unrepresented` |
| 7 | `ChannelEnforcementError` — binding lacks a channel / imports production, 4 sites | `testgraph_channels.py` | ESCALATION | none | `channel_enforcement` is described at `spec_manifest.yaml:33,54` as a *desired* variable; **no such variable exists in `TlaSpecDevCli.tla`'s VARIABLES block** | `unrepresented` |
| 8 | `LedgerError` — ledger schema violation, 2 sites | `complexity_ledger.py` | ESCALATION | none | none | `unrepresented` |
| 9 | `ImportError`/`ModuleNotFoundError` handlers — 24 sites | throughout | mixed | mixed | none | `unrepresented` — see §4.4 |

Group sum: 66+41+24+15+13+13+4+2+24 = 202 typed sites; remainder of the 347 raw
hits are bare `try:` lines and `raise`/`except` occurrences in comments and
docstrings, which carry no failure semantics of their own and are represented by
the group of the handler they belong to.

**Row 7 is a first-class finding.** `spec_manifest.yaml:33` and `:54` describe
modeling a `channel_enforcement` variable and an `EnforceExternalChannels`
action. Neither exists in the model. The manifest describes model surface the
model does not have. Gap **G17**.

### 4.2 Retries — raw `2`, real `0`, rule: `prose-only hits collapsed`

| # | Behavior | Trigger | In/Out | Plan line | Spec action | Verdict |
|---|---|---|---|---|---|---|
| 1 | the word "attempt" in a comment | `scripts/kill_test.py:131` | ESCALATION | none | n/a | false positive |
| 2 | the word "attempt" in a docstring | `scripts/kill_test.py:282` | ESCALATION | none | n/a | false positive |

**There is no retry logic in `scripts/`.** Complete, and clean. Note the Test
Graph SDK does expose a `retries` field (`node_spec.py`), which is §3.8 surface
this command's hardcoded path never reaches.

### 4.3 Timeouts — raw `5`, rows `5`, rule: `none — all presented`

| # | Behavior | Trigger (`file:line`) | In/Out | Plan line | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|
| 1 | per-mutant corpus timeout, default 600s | `scripts/kill_test.py:592` | ESCALATION | none | none | `unrepresented` |
| 2 | timeout passed to `subprocess.run` | `scripts/kill_test.py:614` | ESCALATION | none | none | `unrepresented` |
| 3 | `--timeout` CLI arg, default 600 | `scripts/run_kill_test.py:104` | in-scope | L1146 | none | `unrepresented` |
| 4 | timeout threaded into the case runner | `scripts/run_kill_test.py:198` | in-scope | L1146 | none | `unrepresented` |
| 5 | `tlc_seconds` described as "hard external timeout per TLC run" | `scripts/budgets.py:41` | in-scope | L721 | `RunKillTest`/`AnalyzeComplexity` read budgets, but **no action represents the timeout firing** | `unrepresented` |

**A mutant whose corpus run times out is a distinct outcome from a mutant that
survives, and the model represents only survived/killed.** `RunKillTest`
(`TlaSpecDevCli.tla:492`) computes a verdict against `kill_rate_floor` with no
timeout branch. A timed-out mutant silently becomes one of those two. Gap
**G7**.

### 4.4 Fallbacks — raw `196`, rows `—`, rule: `NOT COLLAPSED — SWEEP INCOMPLETE`

**This category is `INCOMPLETE`.** The command matches `default`, which appears
in every `argparse.add_argument(..., default=...)` and every
`field(default_factory=...)` in the repository. 196 rows cannot be honestly
grouped by a rule I can state, and the prompt grants grouping only to error
paths. The high-value subset below was walked directly and is complete *as a
subset*, not as the enumeration.

**The three owner-retained overrides** — the class the prompt names explicitly
("a guard that silently passes when its input is absent"). All three are live in
code, and `ticket_plan.yaml:332-340` records the owner's decision that they
**STAY**:

| # | Behavior | Trigger (`file:line`) | In/Out | Plan line | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|
| 1 | **budgets fallback** — a missing manifest, a missing `budgets:` block, or any missing individual key falls back to `DEFAULT_BUDGETS` and emits a warning to stderr | `scripts/budgets.py:157-164` (no manifest), `:166-175` (no block), `:177-189` (missing keys) | in-scope | L721 (`scripts/budgets.py`) | `RecordBudgets` (`:269`) and `WorkflowRequiresBudgets` (`:663`) model budgets as **present**. `BudgetsRequireProject` (`:657`) pins ordering. **No action or variable represents the budgets-absent path.** | `unrepresented` |
| 2 | **`--allow-over-budget`** — case generation proceeds past the complexity gate when the flag is typed | `scripts/generate_cases_from_tlc_dump.py:795-802,840`; `scripts/analyze_complexity.py:1143` | in-scope | L667 | **`RunSpecUnitTests(root, ticket, override)` (`:519`) models exactly this**, and `TlaSpecDevCli.tla:534-537` states the override reaches `complexity_gate` only | `represented` |
| 3 | **justification-table conditional** — dead-weight analysis is *skipped* when the manifest carries no `justification:` table | `scripts/analyze_complexity.py:1084` ("no justification: table in the manifest -- dead-weight analysis skipped."), gated by `load_justification` returning `None` at `:692-695` | in-scope | L665 | none — no variable represents "analysis skipped for want of input" | `unrepresented` |

Rows 1 and 3 are precisely the shape the prompt says to look for: **a check that
disables itself when its input is absent, where the disabled path is
unmodeled.** `scripts/testgraph_channels.py:30-31` states the doctrine in this
repository's own words — "A missing declaration is a failure, not a skipped
check -- a gate that disables itself when its input is absent is" degeneracy —
and `budgets.py` and `analyze_complexity.py` do the opposite. That is not a
contradiction I am asked to resolve; the owner retained them deliberately
(`:332-340`). But retained-and-unmodeled is still unmodeled: **the oracles
cannot see a path the model does not contain.** Gaps **G1** and **G2**.

Row 2 is the counter-example that shows the model *can* express this shape — it
already does, for the override. Rows 1 and 3 are the two that were not given the
same treatment.

**Import fallbacks** (24 sites, from the §4.1 row-9 group): `except ImportError`
19 sites + `except ModuleNotFoundError` 5 sites, chiefly the PyYAML-optional
path in `scripts/extract_spec_manifest.py` which silently degrades to a
hand-rolled YAML-subset parser. The two parsers are not equivalent, and which
one runs depends on the ambient interpreter. `unrepresented`; folded into
**G18**.

### 4.5 Concurrency / interleaving — raw `81`, collapsed `4`, rule: `word-boundary re-match`

Collapsing rule, re-derivable:

```bash
grep -rnE "\b(threading|Thread\(|asyncio|async def|await |Lock\(\)|concurrent\.futures|multiprocessing)\b" \
  --include='*.py' scripts/ spec_double_compiler/     # -> 4
```

77 of the 81 raw hits are substring false positives — overwhelmingly `lock`
inside `_parse_block` (`scripts/extract_spec_manifest.py:75,122,143,155,162,201`
and similar), plus "blocked"/"deadlock" in prose. This is a **95% false-positive
rate** and is reported in Attestation §6 as a prompt defect.

| # | Behavior | Trigger (`file:line`) | In/Out | Plan line | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|
| 1 | `import asyncio` | `scripts/run_generated_case_adapters.py:389` | in-scope | L886 | none | `unrepresented` |
| 2 | `asyncio.run(value)` — **an adapter may return a coroutine, which is then driven to completion** | `scripts/run_generated_case_adapters.py:391` | in-scope | L886 | `RunSpecUnitTests` (`:519`) models synchronous case execution only | `unrepresented` |
| 3 | the phrase "start/await the app" in a generated docstring | `scripts/scaffold_spec.py:415` | ESCALATION | none | n/a | false positive |
| 4 | same docstring, emitted by the onboarding path | `scripts/onboard_program_model.py:660` | in-scope | L488 | n/a | false positive |

**Row 2 is a real unmodeled execution mode.** Gap **G8**. Also note
`test_graph/build-logic/src/main/kotlin/.../exec/PlanExecutor.kt` orchestrates
node execution with a resume harness (there is a
`PlanExecutorResumeHarnessTest.kt`) — genuine interleaving in a runtime this
sweep's hardcoded paths never reach, and which the sandbox cannot observe.

### 4.6 Config-driven branches — raw `314`, rows `—`, rule: `NOT COLLAPSED — SWEEP INCOMPLETE`

**This category is `INCOMPLETE`.** The pattern includes `.get("` and `flag` and
`default`, which match nearly every dictionary read in the codebase. 314 rows
cannot be honestly grouped by a rule I can state. The subset below was walked
directly and is complete *as a subset*.

| # | Behavior | Trigger (`file:line`) | In/Out | Plan line | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|
| 1 | `SPEC_DOUBLE_BATCH_REEXEC=1` selects between in-process batch execution and re-exec into a fresh interpreter | `scripts/run_generated_case_adapters.py:875` | in-scope | L886 | none | `unrepresented` |
| 2 | `--batch` / `--python` change the case execution topology | `scripts/run_generated_case_adapters.py:875-902` | in-scope | L886 | `RunSpecUnitTests` models one execution mode | `partial` |
| 3 | `--work-dir` absent → `tempfile.mkdtemp` | `scripts/run_generated_case_adapters.py:965` | in-scope | L886 | none | `unrepresented` |
| 4 | `tlc2` on PATH → use it; else `java -cp $TLA2TOOLS_JAR` | `scripts/run_tlc.sh` | ESCALATION | none | `tlc_process` port targets `*java*` — **matches only the second branch** | `partial` |
| 5 | `--keep-k3d` suppresses cluster and image teardown | `examples/run_distributed_history_validation.py:406-407` | ESCALATION | none | none | `unrepresented` |
| 6 | `$TLA2TOOLS_URL` / `$TLA2TOOLS_VERSION` override the download source, default `latest` | `skill-scripts/install-tlc2.sh` | ESCALATION | none | none — **a "latest" default makes the installed toolchain version nondeterministic** | `unrepresented` |
| 7 | PyYAML present → real parser; absent → YAML-subset parser | `scripts/extract_spec_manifest.py` | ESCALATION | none | none | `unrepresented` |

Row 4 deserves emphasis: the `tlc_process` port declares target `*java*`, but
`scripts/run_tlc.sh` *prefers* `tlc2` when it is on PATH. **In the preferred
branch the spawn does not match the declared port**, so the effect oracle would
see an undeclared spawn — or, if TLC is never exercised in the observed run,
would see `tlc_process` as dead model surface. Either way the declaration and
the program disagree. Gap **G6b**.

---

## 5. Sweep 4 — Views, reported separately

**Finding of the highest order, per Step 5.** This project has **one** view
module: `specs/current/TlaSpecDevCli.tla`. There is no `Internal.tla` and no
`External.tla`.

```bash
git ls-files | grep -E 'Core\.tla|Internal\.tla|External\.tla'
# examples/distributed_history/specs/program_model/Core.tla
# examples/distributed_history/specs/program_model/External.tla
# examples/distributed_history/specs/program_model/Internal.tla
```

The split exists only in the *example*. The repository's own baseline has none.
Per Step 5 this is **not** reported as "N/A — single module"; a single module is
a missing view, not a merged one.

This is in scope on a quoted line: `ticket_plan.yaml:464` — *"it is now IN scope
but scheduled LAST, as MF-023 at promotion_order 85, after every mechanism
ticket has landed."* MF-023 is `status: pending`.

**Aggravating defect.** `specs/current/spec_manifest.yaml:110-113` declares:

```yaml
  program_model_core: ../program_model/Core.tla
  program_model_internal: ../program_model/Internal.tla
  program_model_external: ../program_model/External.tla
```

`ls specs/program_model/` returns `TlaSpecDevCli.tla` and no such files. **The
manifest points at three modules that do not exist**, and nothing in the shipped
toolchain fails on it. Gap **G15**.

### 5.1 Internal — verdict: `unrepresented (view absent)`

`TlaSpecDevCli.tla` is a single flat state machine over 9 variables. It is not
an Internal view: it has no component decomposition, so "the interleaving
between components" has no referent.

| Surface item | Verdict | Evidence |
|---|---|---|
| Component decomposition (which components exist) | `unrepresented` | no `Core.tla`; `TlaSpecDevCli.tla:157-171` declares one flat VARIABLES block |
| Per-component internal state | `unrepresented` | all 9 variables are global to the single module |
| Interleaving between components | `unrepresented` | `Next` (`TlaSpecDevCli.tla:600-627`) is a flat disjunction of 14 actions over one state; no component identity exists to interleave |
| Internal action detail for the case-generation pipeline (`generate_cases_from_tlc_dump` → `export_testgraph_cases` → `run_generated_case_adapters`) | `unrepresented` | the three stages collapse into `RunSpecUnitTests` (`:519`) |
| Internal action detail for the close pipeline (`spec_evolution` → `complexity_ledger` → `skill_feedback`) | `unrepresented` | collapse into `CloseTicket` (`:580`) |
| Ledger/feedback internal state | `unrepresented` | no variable; `complexity_ledger.py` and `skill_feedback.py` are both ESCALATION rows in Sweep 1 |

### 5.2 External — verdict: `unrepresented (view absent)`

**The entire External surface is unrepresented by construction.** There is no
External module, therefore no channel-typed public input surface and no declared
observable projection. Enumerated from the actual public surface
(`scripts/tla_spec_dev.py` argparse tree, verified by reading):

| Surface item | Verdict | Evidence |
|---|---|---|
| `scaffold project` | `unrepresented` (as External) | modeled internally as `ScaffoldProject` (`:248`); no External action, no channel |
| `scaffold workflow` | `unrepresented` (as External) | `ScaffoldWorkflow` (`:287`); no External action |
| `open ticket` | `unrepresented` (as External) | `OpenTicket` (`:305`); no External action |
| `run spec-unit-tests` | `unrepresented` (as External) | `RunSpecUnitTests` (`:519`); no External action |
| `run effect-conformance` | `unrepresented` (as External) | `RunEffectConformance` (`:439`); no External action |
| `run kill-test` | `unrepresented` (as External) | `RunKillTest` (`:492`); no External action |
| `analyze complexity` | `unrepresented` (as External) | `AnalyzeComplexity` (`:370`); no External action |
| `analyze corpus` | `unrepresented` (as External) | `AnalyzeCorpus` (`:402`); no External action |
| `close ticket` | `unrepresented` (as External) | `CloseTicket` (`:580`); no External action |
| **`close workflow` — no such subcommand** | `unrepresented` | workflow close is reachable only via `scripts/close_spec_workflow.py` / `close_tickets.py` run directly; it is in the program but in neither the CLI nor the model. Gap **G10** |
| Exit-code contract (0 / 1 / 2) | `unrepresented` | `effect_conformance_report.py` returns 1 for gaps and 2 for malformed declarations; `CommandResult` (`:197`) carries only a boolean |
| stdout/stderr observable projection | `unrepresented` | `cliWorkflow` asserts on stdout substrings (`test_graph/sources/tla_spec_dev_cli_help.py`), so stdout **is** an observed channel in practice; nothing in the model projects it |
| Warning-on-stderr channel | `unrepresented` | `budgets.py:158-189` emits warnings that are the *only* signal a fallback occurred |
| Channel typing on external bindings | `unrepresented` | `scripts/testgraph_channels.py` enforces http/cli/fs/queue/k8s; `spec_manifest.yaml:33,54` describes a `channel_enforcement` variable and `EnforceExternalChannels` action that **do not exist in the model** |
| Environment inputs (`SPEC_DOUBLE_BATCH_REEXEC`, `TLA2TOOLS_URL`, `TLA2TOOLS_VERSION`, `SKILL_MANAGER_BIN_DIR`, `SKILL_DIR`, `TLC2`) | `unrepresented` | all are caller-drivable inputs; §3.4 |

Gaps **G13** (Internal) and **G14** (External).

---

## 6. Dispositions

Only three exist. **No "justified" or "accept as-is" disposition is available
for an in-scope gap** — see `prompts/coverage_audit.md` §6.

### 6.1 In-scope gaps — HARD, block promotion

Every row here traces to a quoted plan line. Remediation is advisory; the gap is
not.

| # | Gap | Sweep | Disposition | Proposed remediation (advisory) |
|---|---|---|---|---|
| **G1** | Budgets-absent → `DEFAULT_BUDGETS` fallback path is unmodeled. `budgets.py:157-189` has three distinct fallback branches; the model represents only budgets-present. | 3 (§4.4) | **model it** | Add a `budgets_source \in {"declared","default"}` variable, thread it through `RecordBudgets`, and add an invariant that a gate verdict computed under `"default"` is distinguishable in evidence. This is the modeled form of the owner's `:332-340` requirement that an override "never be the default path". |
| **G2** | Justification-table-absent → dead-weight analysis silently skipped (`analyze_complexity.py:692-695,1084`). The disabled path is unmodeled. | 3 (§4.4) | **model it** | Give `AnalyzeComplexity` a third outcome alongside pass/fail — `not_assessed` — and an invariant that `not_assessed` cannot satisfy `SpecUnitTestsRequireAnalyzedGate` (`:696`). |
| **G3** | `RecordBudgets` is a modeled action absent from `spec_manifest.yaml`'s `effects.actions` map, so its writes are undeclared by construction. | 1 (§1) | **model it** | Add `RecordBudgets: [spec_tree]` at `spec_manifest.yaml:169-182`. |
| **G4** | All 15 `@port TlaSpecDevCliPort.<name>` annotations in the TLA name ports absent from the manifest; the two naming schemes are disjoint and nothing cross-checks them. | 1 (§1) | **change the program** | Either rewrite the annotations to the 5 real port names, or add a check in `scripts/effect_conformance.py` that every `@port` annotation resolves to a declared port. The second is preferable — it makes the class of defect impossible rather than fixing one instance. |
| **G5a** | 8 deletion sites; **no `filesystem.delete` port is declared anywhere**, though the schema supports the type. | 2 (§3.1) | **model it** | Declare a `spec_tree_delete` / `history_prune` port of type `filesystem.delete` and bind it to `CloseTicket`. |
| **G5b** | `tempfile.mkdtemp` (`run_generated_case_adapters.py:965`) writes case programs under the system temp dir, outside all three declared globs. | 2 (§3.1) | **model it** | Declare a `case_workdir` port with target `**/spec-double-cases-*/**`, or change the program to default the work dir under `**/results/**` where `evidence_report` already covers it. |
| **G6a** | 7 real spawn sites; none is cleanly `declared`. `git` (`spec_evolution.py:99`) matches neither `*java*` nor `*pytest*`. | 2 (§3.2) | **model it** | Declare a `git_process` port (`process.spawn`, `*git*`) bound to `CloseTicket`, and a `cli_subinvoke` port for `tla_spec_dev.py:358`. |
| **G6b** | `tlc_process` targets `*java*`, but `run_tlc.sh` prefers `tlc2` when on PATH — the declaration matches only the non-preferred branch. | 3 (§4.6) | **change the program** | Make `run_tlc.sh` always exec via `java -cp`, or widen the port target to `*(java|tlc2)*`. Prefer the former: one spawn shape is easier to model than two. |
| **G7** | Kill-test per-mutant timeout (600s) is unmodeled; a timed-out mutant is indistinguishable from a survivor in the verdict. | 3 (§4.3) | **model it** | Add a `timed_out` outcome to `RunKillTest` (`:492`) and an invariant that a run with any timed-out mutant cannot produce a `"measured"` verdict — a timeout is missing evidence, not a survival. |
| **G8** | Adapters may return coroutines, driven by `asyncio.run` (`run_generated_case_adapters.py:389-391`). This execution mode is unmodeled. | 3 (§4.5) | **model it** | Either represent sync/async adapter execution as a parameter of `RunSpecUnitTests`, or change the program to reject coroutine-returning adapters. The second is cheaper if no adapter currently uses it. |
| **G9** | 4 wall-clock reads write timestamps into append-only evidence. No clock port type exists in the schema (`spec_manifest.yaml:145-149`), so this is undeclarable, not merely undeclared. | 2 (§3.5) | **model it** | Extend the observable type set with `clock.read`, or change the program to inject timestamps from a single seam the sandbox can observe. |
| **G10** | Workflow close (`close_spec_workflow.py`, `close_tickets.py`) has **no spec action and no CLI subcommand**. The model has `CloseTicket` only. | 1, 4 (§5.2) | **model it** | Add a `CloseWorkflow(root)` action guarded on all tickets closed, plus a `close workflow` subparser so the modeled surface and the driveable surface coincide. |
| **G11** | `scripts/export_testgraph_cases.py` (in scope at L791, L1012) has no spec action representing it. | 1 | **model it** | Either give the export stage its own action or state in the manifest that it is an internal step of `RunSpecUnitTests` — currently neither is recorded. |
| **G12** | `spec_double_compiler/runtime.py` (in scope at L887) defines the adapter runtime contract; nothing in the model represents it. | 1 | **model it** | Represent the adapter contract as component state in the Internal view produced by MF-023. |
| **G13** | **The Internal view does not exist.** All component detail, per-component state and inter-component interleaving is unrepresented by construction. | 4 (§5.1) | **model it** | MF-023. |
| **G14** | **The External view does not exist.** The entire public input surface and observable projection — 9 subcommands, exit-code contract, stdout/stderr channels, 6 environment inputs — is unrepresented by construction. | 4 (§5.2) | **model it** | MF-023. |
| **G15** | `spec_manifest.yaml:110-113` points `program_model_core/internal/external` at three files that do not exist, and nothing fails on it. | 4 (§5) | **change the program** | Validate those paths in `scripts/extract_spec_manifest.py` so a dangling reference is a hard error. A manifest key that names a nonexistent file is exactly the silent-degradation shape `:332-340` warns about. |
| **G16** | The effect sandbox patches only the current Python interpreter (`effect_conformance.py:939`). The Kotlin/Gradle Test Graph engine and the `curl` in `install-tlc2.sh` are unobservable — and `unobservable` is not `clean`. | 2 (§3.8) | **model it** | MF-027 shipped an `unobservable` verdict; extend it so a run whose graph executed JVM nodes reports `unobservable` for that portion rather than a scoped-clean result. |
| **G17** | `spec_manifest.yaml:33,54` describe a `channel_enforcement` variable and an `EnforceExternalChannels` action. **Neither exists in `TlaSpecDevCli.tla`.** The manifest describes model surface the model does not have. | 3 (§4.1) | **model it** | Add the variable and action, or remove the manifest text. This is the MF-020/MF-022 desync `ticket_plan.yaml:1376` already flags for reconciliation. |
| **G18** | 24 import-fallback sites, chiefly PyYAML-optional degradation to a hand-rolled YAML-subset parser (`extract_spec_manifest.py`). The two parsers are not equivalent; which runs depends on the ambient interpreter. | 3 (§4.4) | **change the program** | Make PyYAML a hard dependency. A manifest parser that changes semantics based on what happens to be installed is an unmodeled input to every gate that reads the manifest. |

**In-scope gap count: 19.**

Note on G13/G14: MF-023 is the scheduled vehicle, and I have named it as the
advisory remediation. It is **not** a disposition — recording "tracked as
MF-023" in place of a disposition is forbidden by §6, and the gap remains open
and gating until the view exists. This audit runs *before* MF-023 by design, so
finding the view absent is the expected result, not an anomaly; what would be
wrong is reporting it as anything other than a gap.

### 6.2 Out-of-scope inventory — does not gate

**Empty.** No surface could be placed out of scope, because the plan contains no
line that puts anything out of scope. Every candidate that would ordinarily land
here — the `examples/` tree, the vendored Test Graph engine, the unnamed
`scripts/` siblings — is an escalation in §6.3 instead. This emptiness *is* the
Step-0 finding, restated: an inclusion-only scope declaration cannot produce an
out-of-scope inventory.

### 6.3 Scope escalations — owner amends the plan, once

| # | Row | Plan line that should change | Argument |
|---|---|---|---|
| E1 | 145 of 160 Sweep-1 rows | `service_catalog` (`:449-464`) | Add a closure rule. One sentence would resolve all 145: e.g. "surface not named in any `implementation_scope` block or `service_catalog` entry is out of scope for this epic" — or the opposite. Either is reviewable; silence is not. Without it, every future run of this gate reproduces these 145 escalations. |
| E2 | 70 `examples/distributed_history/**` rows | `:1147` `- examples/distributed_history/ worked kill test` | The line names a directory and then qualifies it. State whether the scope is the directory or the artifact. As written it can be read either way, and the readings differ by 69 files including an HTTP server and k3d provisioning. |
| E3 | 45 `test_graph/build-logic/**`, `test_graph/sdk/**` rows | `:462` `- test_graph specWorkflow / cliWorkflow graphs` | The line names the *graphs*; the engine and SDKs that execute them are unnamed. Since the engine is the one runtime the effect sandbox provably cannot observe (G16), whether it is in scope is consequential, not clerical. |
| E4 | 10 `test_graph/sources/*.py` rows | `:462` | Whether "graphs" reaches the node sources. These nodes spawn `git`, `gradlew`, `uv` and the CLI itself (§3.8), so their scope status determines whether G6a is understated. |
| E5 | 14 unnamed `scripts/*.py` + `spec_double_compiler/__init__.py` | the 15 `implementation_scope` blocks | The plan names files, and the file set has drifted. `scripts/complexity_ledger.py` is the clearest instance: MF-019's scope (`:1283-1286`) names the three modules that *call* the ledger but not the ledger itself. Either name them or adopt E1's closure rule. |
| E6 | `skill-scripts/install-tla-spec-dev.sh`, `skill-scripts/install-tlc2.sh` | any scope block | `install-tla-spec-dev.sh` is the mechanism behind the modeled `InstallLocalCli` action (`:231`), and `install-tlc2.sh` performs the only network fetch in the non-example tree. Modeled-but-unscoped is a contradiction only the owner can resolve. |
| E7 | `scripts/extract_spec_manifest.py` | `:454` `- spec_manifest.yaml / actions.yml / testgraph_bindings.yml schemas` | Scoping a schema may or may not scope its parser. Given G18 (the parser silently changes identity based on PyYAML availability), this matters. |
| E8 | `:454` names `actions.yml` and `testgraph_bindings.yml` as existing-boundary schemas | `:454` | **Neither file exists in this repository** — `git ls-files` finds them only under `examples/`. The `service_catalog` describes a boundary the repository does not have. |

---

## 7. Verdict

- In-scope gaps: **19**
- Out-of-scope inventoried: **0**
- Escalations: **8 classes covering 145 of 160 Sweep-1 rows**
- **Verdict: `INCOMPLETE`**

`INCOMPLETE` rather than `FAIL`, and the distinction is deliberate: 19 in-scope
gaps would independently make this a `FAIL`, but a `FAIL` asserts the surface was
walked and these are the findings. That assertion cannot be made here. Three
sweep categories (Sweep 2 Filesystem, Sweep 3 Fallbacks, Sweep 3 Config —
735 raw rows) were not enumerated at the mandated granularity, and 145 of 160
Sweep-1 rows could not be classified against the plan. **`INCOMPLETE` is not a
`PASS`**, and the 19 gaps gate promotion exactly as a `FAIL` would.

For the owner, in priority order:

1. **Amend the scope declaration** (E1). It is one sentence and it unblocks 145
   rows, this run and every future run.
2. **Fix the prompt's three unbounded sweeps** (Attestation §6) so the remaining
   735 rows become enumerable.
3. **Close the 19 gaps.** G13/G14 are MF-023's charter. G1, G2, G4, G15 and G17
   are small and independent of it — and G4, G15 and G17 are model/manifest
   desyncs that no oracle currently checks, which is the audit's own failure
   mode reproduced one level down.

---

## 8. Attestation

**1. Row-count reconciliation per sweep.**

| Sweep | Command | Raw N | Rows M | `N == M` |
|---|---|---|---|---|
| 1 Program surface | `git ls-files '*.py' '*.java' '*.kt' '*.kts' '*.sh' \| grep -v '^tests/' \| grep -v '^specs/'` (5 runs) | 79+24+42+10+5 = **160** | **160** | ☑ yes |
| 2.1 Filesystem | `grep -rn "open(\|Path(\|..." scripts/ spec_double_compiler/` | **225** | 26 aggregate + 17 destructive | ☒ **no — INCOMPLETE.** Aggregate accounts for all 225 hits by file (column sums to 225); per-site disposition was not produced. Not authorized to collapse for volume. |
| 2.2 Subprocess | `grep -rn "subprocess\.\|os\.system\|..."` | **16** | **16** | ☑ yes (7 net real after a stated collapsing rule) |
| 2.3 Network | `grep -rn "socket\.\|requests\.\|..."` | **6** | **6** | ☑ yes (0 net real) |
| 2.4 Environment | `grep -rn "os\.environ\|getenv\|..."` | **3** | **3** | ☑ yes |
| 2.5 Clock | `grep -rn "datetime\.\|time\.\|..."` | **4** | **4** | ☑ yes |
| 2.6 Randomness | `grep -rn "random\.\|uuid\.\|..."` | **4** | **4** | ☑ yes (0 net real) |
| 2.7 Persistent store | `grep -rn "sqlite3\|psycopg\|..."` | **0** | **0** | ☑ yes |
| 3.1 Error paths | `grep -rn "except\|raise\|try:"` | **347** | **9 groups** (202 typed sites) | ☑ grouped by exception type per a stated rule, as Step 4 permits |
| 3.2 Retries | `grep -rn "retry\|backoff\|..."` | **2** | **2** | ☑ yes (0 real) |
| 3.3 Timeouts | `grep -rn "timeout\|deadline\|..."` | **5** | **5** | ☑ yes |
| 3.4 Fallbacks | `grep -rn "fallback\|default\|..."` | **196** | 3 + 1 subset rows | ☒ **no — INCOMPLETE.** Grouping is granted only to error paths; I could state no rule for 196 rows. |
| 3.5 Concurrency | `grep -rn "thread\|async \|lock\|..."` | **81** | **4** | ☑ yes, via a stated word-boundary re-match rule; 77 substring false positives |
| 3.6 Config branches | `grep -rn "if.*config\|getenv\|\.get(\"\|..."` | **314** | 7 subset rows | ☒ **no — INCOMPLETE.** Same reason as 3.4. |
| 4 Views | `git ls-files \| grep -E 'Core\.tla\|Internal\.tla\|External\.tla'` | 3 (all under `examples/`) | 6 Internal + 15 External | ☑ reported as a missing-view finding per Step 5, not as N/A |

**2. Surface NOT walked.** Naming it precisely, as an assertion on the record:

- **Per-site disposition of 225 filesystem hits** (§3.1). Walked at file
  granularity and at destructive-site granularity; not at per-site granularity.
- **189 of 196 fallback hits** (§4.4) and **307 of 314 config hits** (§4.6).
  The subsets presented were selected by *reading for the pattern the prompt
  names* (guards that pass when input is absent), not by enumeration. They are
  the least reproducible rows in this report.
- **The bodies of the 42 Kotlin, 24 Java and 10 Gradle files.** Their identity
  and role were established (and byte-identity between the two copies verified
  by MD5), but I did not read `PlanExecutor.kt`, `JBangExecutor.kt` or
  `ValidationRuntime.kt` line by line. Their effects are asserted from role and
  filename, not from reading. G16 rests partly on this.
- **The 11 generated case modules** under
  `examples/distributed_history/specs/generated/**` (Sweep-1 rows 8-15). Machine-
  generated; not read.
- **`specs/` itself** — excluded by the prompt's filter, which also excludes
  `production_adapters.py`, named in scope at `:461`.
- **`tests/`** — excluded by the prompt's filter.
- No TLC run, no `analyze complexity` run, no oracle execution. This audit is
  static; it reports what the model does not contain, not what a run would show.

**3. Rows dispositioned from a file path or name rather than from reading code.**
These are the least reliable rows:

- **Sweep-1 rows 21-67 and 106-150** (the 76 Kotlin/Java/Gradle files). Verdict
  `unrepresented` is safe by default polarity, but the *scope* escalation rests
  on path, not content.
- **Sweep-1 rows 8-15** (generated case modules) — dispositioned from path.
- **Sweep-1 rows 143-149** (`test_graph/sdk/python/**`) — dispositioned from the
  subagent's one-line summaries, not from my own reading.
- **§3.8 rows 13, 19, 20** (Kotlin engine, k3d, k8s scripts) — effects asserted
  from role and filename.
- Everything under `scripts/` and `spec_double_compiler/` **was** read, directly
  or via a subagent that cited `file:line` for each claim, and the load-bearing
  findings (G1, G2, G3, G4, G5b, G6a, G6b, G7, G8, G15, G17) were each verified
  by me reading the cited lines.

**4. Rows whose scope was decided by reasoning rather than a quoted plan line.**

**None in the final tables — but only after a correction I want on the record.**
The first pass used ancestor-directory matching, so `scripts/tla_spec_dev.py`
being named at `:487` made all of `scripts/` in-scope. That produced **103
in-scope / 57 escalations**. It is reasoning, not quoting, so it was reverted to
exact-path matching: **15 in-scope / 145 escalations**.

**The 88-row difference between those two runs is the size of the discretion
this prompt leaves open**, and nothing in the prompt decides it. Two competent
agents will disagree here, and the tidier answer is the wrong one. Recorded as a
prompt finding in §6.

**5. Could a reader reproduce this report's row set from the recorded commands?**
☐ yes ☑ **no — partially.**

- Reproducible exactly: Sweeps 1, 2.2-2.7, 3.1, 3.2, 3.3, 3.5, and 4. Every
  command, raw count, and collapsing rule is recorded.
- **Not reproducible: §3.1's per-site rows, §4.4's and §4.6's subsets.** A reader
  can reproduce the raw hits but cannot re-derive which subset I selected,
  because I selected it by judgment. Those three categories are marked
  INCOMPLETE for exactly this reason.

Per Step 7 item 5, a sweep whose row set is not reproducible is INCOMPLETE
regardless of what its table says. That is why §7's verdict is `INCOMPLETE`.

**6. Findings about this prompt.**

This was the first execution. The prompt is strong in its polarity discipline
and its refusal of a justification escape hatch — the `unrepresented`-by-default
rule and the ban on a fourth disposition both did real work, and I reached for a
"reasonable exclusion" more than once and was correctly blocked. The
`FORBIDDEN` list in §6 is the single most load-bearing paragraph in the file.
Findings below are ordered by how much they threaten the gate's validity.

**(a) Yes — an agent could produce a plausible report without walking the
surface. The permitting step is Step 3's category commands.**
Filesystem returns 225 rows, Fallbacks 196, Config 314. The prompt demands
exactly-N-rows and authorizes collapsing only for false positives. Faced with
735 rows, the path of least resistance is to present a curated 15-20 rows per
category and let the reader assume enumeration — and nothing downstream catches
it, because the row-count check is *self-reported*. The prompt's central control
("every table's row set is produced by a command") is only as good as the
agent's willingness to report `N ≠ M` against itself. **Recommended fix:** make
the row-count reconciliation a computed artifact (have the sweep write its raw
output to `results/sweep-raw/<category>.txt` and require the report to cite the
file), and grant Step 3 the same explicit grouping allowance Step 4 gives error
paths, requiring a stated rule.

**(b) Step 1 is partly unrunnable and partly wrong, in this repository.**
- `cat specs/current/actions.yml` and `cat specs/current/testgraph_bindings.yml`
  both fail — no such files. They exist only under `examples/`. The prompt
  hardcodes a layout that this repository, which *is* the toolchain, does not
  use.
- `grep -n '^[A-Za-z_][A-Za-z0-9_]* ==' specs/current/*.tla` **cannot match a
  parameterized definition.** It returns 24 and omits 13, including
  `ScaffoldProject(root)`, `RecordBudgets(root)`, `OpenTicket(root, ticket)` and
  `CloseTicket(root, ticket)` — i.e. it omits almost exactly the set of actions a
  coverage audit maps rows against. An agent that trusted it would have built its
  representation index from 24 definitions of which only `BuildSkillCli`,
  `InstallLocalCli` and `Stutter` are actions, and would then have marked nearly
  everything `unrepresented`. The polarity means that *under*-claims rather than
  over-claims, so the gate fails safe — but it fails safe by accident, and the
  resulting report would be uniformly wrong in a way that looks rigorous.
  **Fix:** `^[A-Za-z_][A-Za-z0-9_]*(\(.*\))? ==`, and make the manifest/binding
  reads path-discovering rather than path-hardcoded.

**(c) Sweep 2's and Sweep 3's hardcoded paths are narrower than Sweep 1's
enumeration, and the prompt never says so.** Step 2 enumerates the whole
repository across every language; Steps 3 and 4 grep only
`scripts/ spec_double_compiler/`. In this repository that is 30 of 160 files.
Re-running the seven effect patterns over the excluded surface returns **233
additional hits**, including every network call in the repository and the only
spawn primitive behind the Test Graph nodes. An agent following the prompt
literally would report "0 real network effects" as a clean result — which is
true of `scripts/`, and false of the program. I caught this only because Sweep 1
had already shown me the file count. **Fix:** derive Steps 3-4's paths from
Step 2's enumeration rather than hardcoding them.

**(d) The grep patterns have a false-positive rate high enough to change
behavior.** Concurrency: 81 raw → **4 real**, a 95% FP rate, because `lock`
matches `_parse_block`. Randomness: 4 → 0. Network: 6 → 0. An agent that
dispositioned raw hits without reading would produce a table that is 95%
noise in one category; an agent that collapses aggressively might discard the
4 real hits with the 77 fake ones. Both failure directions are available.
**Fix:** ship word-boundary `grep -E` patterns.

**(e) Step 0's HALT is well-designed and it fired — but the prompt gives no
guidance for the overwhelmingly likely case, which is a *partial* scope
declaration.** Step 0 anticipates "no scope" or "too vague". This plan has a
precise scope that is simply *incomplete* — an inclusion list naming 15 of 160
files. The prompt offers no rule for whether naming `scripts/foo.py` scopes
`scripts/`. That single unstated rule moved 88 rows between classifications
(Attestation §4). **This is the most consequential ambiguity in the prompt**,
because it is invisible: both answers produce a confident-looking report, and
the difference is 55% of the surface. **Fix:** state the closure rule
explicitly — "an `implementation_scope` entry naming a file scopes that file
only; directory closure must be written as a trailing-slash path" — so the
plan's silence becomes an escalation by construction rather than by the
auditor's temperament.

**(f) "Exactly N rows" and "disposition every row" are in tension with reading
the code, and the prompt does not acknowledge the trade.** 160 Sweep-1 rows is
already at the limit of what can be *read* rather than pattern-matched; I met it
partly by dispositioning 76 files from path and role (Attestation §3). The
prompt's row-count discipline successfully prevents *silent sampling*, but it
creates pressure toward shallow rows, which is a quieter failure. Attestation
§3 is the right instrument and should be promoted: **require a per-sweep count
of rows-read-vs-rows-inferred**, not just a list.

**(g) A smaller thing worth fixing: the `grep -v '^specs/'` filter is
asymmetric.** Anchored at `^`, it drops the repository's own `specs/` tree —
including `production_adapters.py`, which `ticket_plan.yaml:461` names as an
explicit adapter boundary — while keeping `examples/distributed_history/specs/**`
(11 files). The filter excludes in-scope surface and includes escalation surface.

**(h) What worked, and should not be weakened.** The three-verdict vocabulary
with `partial` requiring a *named* uncovered part converted several
would-be hedges into concrete gaps (G1, G2, G7, G8 all started as "partial,
probably fine"). The `process.spawn` rule caught G6a and G16, which I would
otherwise have marked declared. Step 5's "a single module is not a merged view;
it is a missing one" is the reason §5 reports 21 rows instead of "N/A", and it
produced G13, G14 and G15. And the §6 `FORBIDDEN` list is what stopped G1 and
G2 from being written up as "known limitation, owner-retained per `:332-340`" —
which is exactly how I first drafted them, and exactly the suppression the gate
exists to catch.
