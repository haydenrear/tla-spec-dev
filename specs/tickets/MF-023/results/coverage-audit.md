# Coverage Audit Report

- **Epic / workflow:** `modular-fuzzing-epic` — MF-026 gate re-run as the **MF-023 promotion gate**
- **Scope source:** `specs/desired_program_model/ticket_plan.yaml` (lines `480-496`, `517-521`, `570-573`, `630-632`, `695-698`, `751-755`, `820-822`, `916-919`, `971-974`, `1041-1044`, `1106-1109`, `1176-1179`, `1246-1250`, `1313-1317`, `1360-1363`, `1404-1408`)
- **Model audited:** `specs/current/Core.tla`, `specs/current/Internal.tla`, `specs/current/External.tla` @ `5575566` (worktree `wt-30-mf023-decompose-dogfooding`, branch `epic/modular-fuzzing`)
- **Date:** `2026-07-19`
- **Verdict:** `FAIL` — **20 in-scope gaps**, with an INCOMPLETE caveat recorded in §7 and §8.2

> This audit checks **completeness of what is modeled**, not fidelity. The four
> oracles are bounded to what is already represented and cannot see this class
> of defect. See `prompts/coverage_audit.md`.

**Read §8 before the tables.** Per `prompts/coverage_audit.md` §"Validation status",
the `N == M` reconciliation in this report is **self-reported** — nothing
mechanically forces it (tracked as issue #48). The raw enumeration output is
checked in under `specs/tickets/MF-023/results/sweep-raw/` precisely so a
reviewer can recount rather than trust. That limitation is a caveat on *this
report's own verdict*, not only on the procedure.

---

## 0. Declared scope (quoted verbatim from the plan)

### 0.1 Workflow-level scope — `service_catalog`

```yaml
# specs/desired_program_model/ticket_plan.yaml:480-496
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
    - "This repository's baseline is a single TlaSpecDevCli.tla module without the Internal/External view split that SKILL.md mandates for onboarded projects. Originally recorded as out of scope for this epic. Owner direction 2026-07-18: it is now IN scope but scheduled LAST, as MF-023 at promotion_order 85, after every mechanism ticket has landed. [...]"
```

### 0.2 The audited ticket's own scope — MF-023

```yaml
# specs/desired_program_model/ticket_plan.yaml:1404-1408
    implementation_scope:
      - specs/program_model/ (Core.tla / Internal.tla / External.tla split)
      - specs/program_model/production_adapters.py (per-view adapters)
      - specs/program_model/spec_manifest.yaml (reconcile the MF-020/MF-022 desync recorded in epic notes)
      - test_graph specWorkflow / cliWorkflow bindings
```

```yaml
# specs/desired_program_model/ticket_plan.yaml:1430
        - the MF-026 coverage audit is RE-RUN post-decomposition as this ticket promotion gate, reporting Internal and External separately now that both views exist; in-scope gaps are closed by modeling them or changing the program, never waived.
```

### 0.3 Every other in-flight `implementation_scope` entry, verbatim

```yaml
# specs/desired_program_model/ticket_plan.yaml — one line per entry, line numbers exact
518:      - scripts/tla_spec_dev.py (scaffold project/workflow budget emission)
519:      - scripts/onboard_program_model.py
520:      - templates/ manifest templates
521:      - references/modular_fuzzing.md defaults kept in sync
571:      - specs/program_model/TlaSpecDevCli.tla (variable and invariant rewrite)
572:      - specs/program_model/production_adapters.py (phase-aware adapters)
573:      - specs/current/tests (adapter assertions referencing the booleans)
631:      - scripts/spec_evolution.py (replace_tree / promote_ticket_outputs)
632:      - scripts/close_ticket.py (close-time reporting of removals)
696:      - scripts/analyze_complexity.py (new)
697:      - scripts/tla_spec_dev.py (analyze subcommand)
698:      - scripts/generate_cases_from_tlc_dump.py (gate integration)
752:      - scripts/budgets.py (new max_state_space_bound default)
753:      - scripts/analyze_complexity.py (gate the bound against the new budget)
754:      - scripts/onboard_program_model.py (emit the new budget at scaffold time)
755:      - specs/program_model/TlaSpecDevCli.tla (setup_phase collapse)
821:      - scripts/generate_cases_from_tlc_dump.py
822:      - scripts/export_testgraph_cases.py
917:      - scripts/run_generated_case_adapters.py
918:      - spec_double_compiler/runtime.py
919:      - actions.yml / spec_manifest.yaml effect declarations
972:      - specs/program_model/TlaSpecDevCli.tla (variable, guard and invariant rewrite)
973:      - specs/program_model/production_adapters.py (lifecycle-aware adapters)
974:      - specs/current/tests (adapter assertions referencing the removed variables)
1042:      - scripts/run_generated_case_adapters.py (testgraph path)
1043:      - scripts/export_testgraph_cases.py
1044:      - testgraph_bindings.yml schema
1107:      - scripts/effect_conformance.py (observability determination and refusal)
1108:      - scripts/effect_conformance_report.py (unobservable verdict)
1109:      - references/modular_fuzzing.md and SKILL.md (declared observable scope)
1177:      - scripts/run_kill_test.py (new) or documented procedure with runner support
1178:      - examples/distributed_history/ worked kill test
1179:      - references/modular_fuzzing.md kept in sync
1247:      - scripts/close_ticket.py
1248:      - scripts/close_spec_workflow.py
1249:      - scripts/close_tickets.py
1250:      - references/migration.md kept in sync
1314:      - scripts/close_ticket.py and scripts/close_spec_workflow.py (ledger entry, delta report, anti-gaming check, refinement-loop record)
1315:      - scripts/analyze_complexity.py (ledger-format output)
1316:      - spec_manifest.yaml complexity_ledger schema
1317:      - SKILL.md / references/architecture_tractability.md consistency check
1361:      - a checked-in sub-agent prompt and report template
1362:      - SKILL.md and epic doctrine updated with the required end-of-epic ordering
1363:      - worked example run against this repository, included as evidence
```

### 0.4 Applying the closure rule

`prompts/coverage_audit.md` §"The closure rule": *an entry naming a FILE scopes
that file only; directory closure counts only when the plan writes a directory —
a trailing slash or an explicit glob.*

| Scope line | Form | Covers |
|---|---|---|
| `ticket_plan.yaml:518, 697` | file | `scripts/tla_spec_dev.py` only |
| `ticket_plan.yaml:519, 754` | file | `scripts/onboard_program_model.py` only |
| `ticket_plan.yaml:631` | file | `scripts/spec_evolution.py` only |
| `ticket_plan.yaml:632, 1247, 1314` | file | `scripts/close_ticket.py` only |
| `ticket_plan.yaml:696, 753, 1315` | file | `scripts/analyze_complexity.py` only |
| `ticket_plan.yaml:698, 821` | file | `scripts/generate_cases_from_tlc_dump.py` only |
| `ticket_plan.yaml:752` | file | `scripts/budgets.py` only |
| `ticket_plan.yaml:822, 1043` | file | `scripts/export_testgraph_cases.py` only |
| `ticket_plan.yaml:917, 1042` | file | `scripts/run_generated_case_adapters.py` only |
| `ticket_plan.yaml:918` | file | `spec_double_compiler/runtime.py` only |
| `ticket_plan.yaml:1107` | file | `scripts/effect_conformance.py` only |
| `ticket_plan.yaml:1108` | file | `scripts/effect_conformance_report.py` only |
| `ticket_plan.yaml:1177` | file | `scripts/run_kill_test.py` only |
| `ticket_plan.yaml:1248, 1314` | file | `scripts/close_spec_workflow.py` only |
| `ticket_plan.yaml:1249` | file | `scripts/close_tickets.py` only |
| `ticket_plan.yaml:1405` | **directory (trailing slash)** | `specs/program_model/**` — closure applies |
| `ticket_plan.yaml:1178` | **directory (trailing slash)** | `examples/distributed_history/**` — closure applies |
| `ticket_plan.yaml:520` | **directory (trailing slash)** | `templates/**` — no code files in the surface enumeration |
| `ticket_plan.yaml:573, 974` | directory, **no trailing slash** | `specs/current/tests` — classified as directory closure AND escalated (§6.3 E-1) |
| `ticket_plan.yaml:571, 755, 972` | file | `specs/program_model/TlaSpecDevCli.tla` — **file deleted by MF-023**; superseded by 1405 |
| `ticket_plan.yaml:919, 1044` | file | `actions.yml`, `testgraph_bindings.yml` — **neither file exists in this repository** (§6.3 E-2) |
| `ticket_plan.yaml:1408` | neither file nor directory | `test_graph specWorkflow / cliWorkflow bindings` — not a path (§6.3 E-3) |

**In-scope file count: 104 of 240 enumerated surface files.** Everything not
placed in scope by a quoted line above is an **ESCALATION**, never an inferred
out-of-scope. That is 136 rows, and that is the correct output of the closure
rule rather than a defect in this audit.

**No row in this report was classified out-of-scope.** The plan places rows
*in*; its silence escalates. §6.2 is therefore empty by construction, and that
is the closure rule working as designed.

**HALT conditions checked.** The plan declares a usable scope (§0.1–0.3), so
the gate runs. Three boundary questions could not be resolved from plan text and
are escalated rather than interpreted (§6.3 E-1, E-2, E-3), plus two filter
questions (E-4, E-5) and one scope-correctness argument (E-6).

---

## 1. Model representation index

**Enumeration commands (all three run; recorded verbatim):**

```bash
grep -nE '^[A-Za-z_][A-Za-z0-9_]*(\(.*\))? ==' specs/current/*.tla        # 62 defs: Core 6, Internal 35, External 21
grep -n 'ports\|effects\|channel' specs/current/spec_manifest.yaml         # 5 ports, 13 action->port rows
find . -name 'actions.yml' -o -name 'testgraph_bindings.yml' | grep -v '^./examples/'   # EMPTY -- see E-2
```

Index sanity check (`prompts/coverage_audit.md` §1: *"an empty or suspiciously
small index means the enumeration failed"*): 14 actions against 9 CLI leaf
subcommands (`scripts/tla_spec_dev.py:389-670`) is plausible — the model carries
two bootstrap actions and two agent-step actions the CLI does not expose as
subcommands. The index is **not** empty and was not re-derived.

| Kind | Name | `file:line` |
|---|---|---|
| Action (Internal) | `BuildSkillCli` | `specs/current/Internal.tla:64` |
| Action (Internal) | `InstallLocalCli` | `specs/current/Internal.tla:73` |
| Action (Internal) | `ScaffoldProject(root)` | `specs/current/Internal.tla:83` |
| Action (Internal) | `RecordBudgets(root)` | `specs/current/Internal.tla:98` |
| Action (Internal) | `ScaffoldWorkflow(root)` | `specs/current/Internal.tla:109` |
| Action (Internal) | `OpenTicket(root, ticket)` | `specs/current/Internal.tla:120` |
| Action (Internal) | `UpdateTicketDesired(ticket)` | `specs/current/Internal.tla:136` |
| Action (Internal) | `UpdateTicketCurrent(ticket)` | `specs/current/Internal.tla:146` |
| Action (Internal) | `AnalyzeComplexity(root)` | `specs/current/Internal.tla:165` |
| Action (Internal) | `AnalyzeCorpus(root)` | `specs/current/Internal.tla:190` |
| Action (Internal) | `RunEffectConformance(root)` | `specs/current/Internal.tla:220` |
| Action (Internal) | `RunKillTest(root)` | `specs/current/Internal.tla:255` |
| Action (Internal) | `RunSpecUnitTests(root, ticket, override)` | `specs/current/Internal.tla:271` |
| Action (Internal) | `CloseTicket(root, ticket)` | `specs/current/Internal.tla:320` |
| Action (External) | `InvokeBuildSkillCli` … `InvokeCloseTicket` (14 wrappers) | `specs/current/External.tla:65,72,79,86,93,100,107,114,122,129,142,158,172,189` |
| Helper (External) | `Emit(command, ok, reason, nextStep)` | `specs/current/External.tla:53` |
| Helper (Core) | `CommandResult(ok, reason, nextStep)` | `specs/current/Core.tla:84` |
| Invariant (Internal) | `TypeInvariant` + 13 named safety properties | `specs/current/Internal.tla:385,406,409,413,419,424,431,434,439,452,463,481,488,497` |
| Invariant (Internal) | `InternalInvariant` (conjunction of 14) | `specs/current/Internal.tla:500` |
| Invariant (External) | `ExternalInvariant` | `specs/current/External.tla:235` |
| Port | `spec_tree` — `filesystem.write` `**/specs/**` | `specs/current/spec_manifest.yaml:177-179` |
| Port | `evidence_report` — `filesystem.write` `**/results/**` | `specs/current/spec_manifest.yaml:180-182` |
| Port | `cli_artifact` — `filesystem.write` `**/.venv/**` | `specs/current/spec_manifest.yaml:183-185` |
| Port | `tlc_process` — `process.spawn` `*java*` | `specs/current/spec_manifest.yaml:186-188` |
| Port | `test_process` — `process.spawn` `*pytest*` | `specs/current/spec_manifest.yaml:189-191` |
| Binding | `specs/current/case_adapters.toml` (14 action→adapter rows) | `specs/current/spec_manifest.yaml:207` |
| Binding | `actions.yml` / `testgraph_bindings.yml` | **DO NOT EXIST** — `find` returned empty; §6.3 E-2 |

**Port vocabulary is exactly 5.** There is **no `filesystem.delete` port**, **no
`network.connect` port** and **no `network.http` port** — while
`scripts/effect_conformance.py:626-640` instruments `filesystem.delete` and
`scripts/effect_conformance.py:355-360,626-640` instruments `network.connect`.
Those observable types are declared nowhere. See §3.1-D and §3.3.

**No mapping was invented.** Where a module's behavior "would naturally fall
under" an action that does not name it, the verdict below is `partial` with the
uncovered part named, per §2 of the prompt.

---

## 2. Sweep 1 — Program surface

### 2.1 Enumeration, verbatim

```bash
# one enumeration per language present in the repository
git ls-files '*.py'   | sort > /tmp/ca/raw-py.txt     # 1289
git ls-files '*.kt'   | sort > /tmp/ca/raw-kt.txt     #  483
git ls-files '*.java' | sort > /tmp/ca/raw-java.txt   #  276
git ls-files '*.kts'  | sort > /tmp/ca/raw-kts.txt    #  115
git ls-files '*.sh'   | sort > /tmp/ca/raw-sh.txt     #    5
# RAW TOTAL = 2168
```

```bash
# the two declared filters, applied in this order
cat /tmp/ca/raw-*.txt \
  | grep -v '^specs/\.history/'                 # F1: -1763
  | grep -v '^specs/tickets/[^/]*/results/'     # F2:  -165
  | sort > /tmp/ca/SURFACE.txt
wc -l < /tmp/ca/SURFACE.txt                     # 240
```

Checked in as `specs/tickets/MF-023/results/sweep-raw/surface.txt`.

### 2.2 The two filters, stated and checked against the plan

> *"A filter is a scope decision wearing a shell flag. If a filter would drop a
> path any plan line names, do not apply it."*

| Filter | Drops | Justification | Checked against plan? |
|---|---|---|---|
| **F1** `^specs/\.history/` | 1763 files | Append-only promoted-ticket archive. Byte-for-byte historical snapshots of files that also appear live elsewhere in the surface; not live program surface. | **No plan line names `specs/.history`.** Dropping it is therefore not licensed by a quoted line — escalated as **E-4**. |
| **F2** `^specs/tickets/[^/]*/results/` | 165 files | Recorded evidence artifacts: Test Graph run reports, including a fully vendored copy of the `test_graph` Kotlin/Java SDK inside each report directory. | **No plan line names it.** Escalated as **E-5**. |

Neither filter drops a path any plan line names — verified by intersecting the
dropped set with §0.4's in-scope path list (empty intersection). Both are
nonetheless **escalations, not classifications**, because the plan is silent and
silence does not resolve. The consequence for this report's own reliability is
recorded in §8.2.

### 2.3 Reconciliation

**Enumerated N = 240** (post-filter, `wc -l < /tmp/ca/SURFACE.txt`);
**table rows M = 240**; **`N == M`: ☑**.

Raw pre-filter N = 2168; filtered-out = 1928; 2168 − 1928 = 240. ☑

### 2.4 Table

Verdicts: `represented` / `partial` (uncovered part named) / `unrepresented`.
**Default polarity is `unrepresented`** — coverage is granted only on cited
positive evidence.

**Zero rows are `represented`.** That is a finding, not an accounting artifact:
no module in this repository has its behavior fully covered by a named action,
because every command carries a refusal path the model does not have.

**Uncovered part, named once for the whole `partial` class** (it is identical
for every row carrying it, so a per-row copy would be 24 restatements of one
sentence): a module marked `partial` implements the *success* transition of the
named action. What is **not** represented in any such row is (a) the command's
refusal/failure result and its `reason` text — `Emit(...)` writes `NoReason` at
every one of the 11 unconditional call sites,
`specs/current/External.tla:67,74,81,88,95,102,109,116,124,131,191`; (b) its
timeout outcome; (c) its flag-driven variants. Those are gaps G1, G9 and G3–G7
in §6.1. A row is `partial` **only** where a named action covers the success
path; every other row is `unrepresented`.

| # | Module | In/Out | Plan line | Spec action(s) | Verdict | Evidence |
|---|---|---|---|---|---|---|
| 1 | `examples/distributed_history/ecommerce_backend/__init__.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 2 | `examples/distributed_history/ecommerce_backend/domain.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 3 | `examples/distributed_history/ecommerce_backend/service.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 4 | `examples/distributed_history/scripts/k3d-up.sh` | IN | 1178 | none | `unrepresented` | no action names this module |
| 5 | `examples/distributed_history/scripts/k8s-deploy.sh` | IN | 1178 | none | `unrepresented` | no action names this module |
| 6 | `examples/distributed_history/scripts/regenerate_tlc_cases.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 7 | `examples/distributed_history/specs/__init__.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 8 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/__init__.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 9 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/cases.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 10 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/types.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 11 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/validators.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 12 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/__init__.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 13 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/cases.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 14 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/types.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 15 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/validators.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 16 | `examples/distributed_history/specs/program_model/__init__.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 17 | `examples/distributed_history/specs/program_model/adapters.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 18 | `examples/distributed_history/specs/program_model/tests/test_ecommerce_adapters.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 19 | `examples/distributed_history/specs/program_model/tlc_projection.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 20 | `examples/distributed_history/test_graph/build-logic/build.gradle.kts` | IN | 1178 | none | `unrepresented` | no action names this module |
| 21 | `examples/distributed_history/test_graph/build-logic/settings.gradle.kts` | IN | 1178 | none | `unrepresented` | no action names this module |
| 22 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Context.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 23 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Executors.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 24 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/JBangExecutor.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 25 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/PlanExecutor.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 26 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/TimeoutParser.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 27 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/UvExecutor.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 28 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphAssembler.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 29 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphModel.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 30 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/MiniJson.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 31 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/NodeDescribeLoader.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 32 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/InspectionTasks.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 33 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunReportWriter.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 34 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunTestGraphTask.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 35 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/ValidationReportTask.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 36 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/TestGraphSpec.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 37 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/Toolchain.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 38 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphExtension.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 39 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphPlugin.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 40 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationNodeSpec.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 41 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationRuntime.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 42 | `examples/distributed_history/test_graph/build-logic/src/test/kotlin/com/hayden/testgraphsdk/exec/PlanExecutorResumeHarnessTest.kt` | IN | 1178 | none | `unrepresented` | no action names this module |
| 43 | `examples/distributed_history/test_graph/build.gradle.kts` | IN | 1178 | none | `unrepresented` | no action names this module |
| 44 | `examples/distributed_history/test_graph/sdk/java/build.gradle.kts` | IN | 1178 | none | `unrepresented` | no action names this module |
| 45 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextItem.java` | IN | 1178 | none | `unrepresented` | no action names this module |
| 46 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextSerde.java` | IN | 1178 | none | `unrepresented` | no action names this module |
| 47 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Json.java` | IN | 1178 | none | `unrepresented` | no action names this module |
| 48 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/JsonMapper.java` | IN | 1178 | none | `unrepresented` | no action names this module |
| 49 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Node.java` | IN | 1178 | none | `unrepresented` | no action names this module |
| 50 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeBody.java` | IN | 1178 | none | `unrepresented` | no action names this module |
| 51 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeContext.java` | IN | 1178 | none | `unrepresented` | no action names this module |
| 52 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeResult.java` | IN | 1178 | none | `unrepresented` | no action names this module |
| 53 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeSpec.java` | IN | 1178 | none | `unrepresented` | no action names this module |
| 54 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeStatus.java` | IN | 1178 | none | `unrepresented` | no action names this module |
| 55 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ProcessRecord.java` | IN | 1178 | none | `unrepresented` | no action names this module |
| 56 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Procs.java` | IN | 1178 | none | `unrepresented` | no action names this module |
| 57 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/__init__.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 58 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/context_item.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 59 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/context.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 60 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/node_spec.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 61 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/procs.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 62 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/result.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 63 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/runner.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 64 | `examples/distributed_history/test_graph/settings.gradle.kts` | IN | 1178 | none | `unrepresented` | no action names this module |
| 65 | `examples/distributed_history/test_graph/sources/cleanup_ecommerce.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 66 | `examples/distributed_history/test_graph/sources/collect_evidence.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 67 | `examples/distributed_history/test_graph/sources/deploy_ecommerce.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 68 | `examples/distributed_history/test_graph/sources/run_external_cases.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 69 | `examples/distributed_history/tests/test_ecommerce_backend.py` | IN | 1178 | none | `unrepresented` | no action names this module |
| 70 | `examples/run_distributed_history_validation.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 71 | `examples/validate_split_desired_workflow.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 72 | `scripts/analyze_complexity.py` | IN | 696,753,1315 | AnalyzeComplexity | `partial` | Internal.tla:165 |
| 73 | `scripts/budgets.py` | IN | 752 | RecordBudgets | `partial` | Internal.tla:98 |
| 74 | `scripts/close_spec_workflow.py` | IN | 1248,1314 | CloseTicket | `partial` | Internal.tla:320 |
| 75 | `scripts/close_ticket.py` | IN | 632,1247,1314 | CloseTicket | `partial` | Internal.tla:320 |
| 76 | `scripts/close_tickets.py` | IN | 1249 | CloseTicket | `partial` | Internal.tla:320 |
| 77 | `scripts/close-spec-workflow.py` | ESC | (none) | CloseTicket | `partial` | Internal.tla:320 |
| 78 | `scripts/close-ticket.py` | ESC | (none) | CloseTicket | `partial` | Internal.tla:320 |
| 79 | `scripts/complexity_ledger.py` | ESC | (none) | AnalyzeComplexity (ledger) | `partial` | Internal.tla:165 |
| 80 | `scripts/corpus_diagnostics.py` | ESC | (none) | AnalyzeCorpus | `partial` | Internal.tla:190 |
| 81 | `scripts/effect_conformance_report.py` | IN | 1108 | RunEffectConformance | `partial` | Internal.tla:220 |
| 82 | `scripts/effect_conformance.py` | IN | 1107 | RunEffectConformance | `partial` | Internal.tla:220 |
| 83 | `scripts/export_testgraph_cases.py` | IN | 822,1043 | RunSpecUnitTests (external cases) | `partial` | Internal.tla:271 |
| 84 | `scripts/extract_spec_manifest.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 85 | `scripts/generate_cases_from_tlc_dump.py` | IN | 698,821 | RunSpecUnitTests (override input) | `partial` | Internal.tla:271 |
| 86 | `scripts/generate_docs.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 87 | `scripts/generate_python.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 88 | `scripts/kill_test.py` | ESC | (none) | RunKillTest | `partial` | Internal.tla:255 |
| 89 | `scripts/new_ticket_workflow.py` | ESC | (none) | OpenTicket | `partial` | Internal.tla:120 |
| 90 | `scripts/onboard_program_model.py` | IN | 519,754 | ScaffoldProject, RecordBudgets | `partial` | Internal.tla:83,98 |
| 91 | `scripts/run_generated_case_adapters.py` | IN | 917,1042 | RunSpecUnitTests | `partial` | Internal.tla:271 |
| 92 | `scripts/run_kill_test.py` | IN | 1177 | RunKillTest | `partial` | Internal.tla:255 |
| 93 | `scripts/run_tlc.sh` | ESC | (none) | AnalyzeComplexity tlc_process port | `partial` | manifest:186-188 |
| 94 | `scripts/scaffold_spec_workflow.py` | ESC | (none) | ScaffoldWorkflow | `partial` | Internal.tla:109 |
| 95 | `scripts/scaffold_spec.py` | ESC | (none) | ScaffoldProject/ScaffoldWorkflow | `partial` | Internal.tla:83,109 |
| 96 | `scripts/skill_feedback.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 97 | `scripts/spec_evolution.py` | IN | 631 | CloseTicket (promotion) | `partial` | Internal.tla:320 |
| 98 | `scripts/spec_paths.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 99 | `scripts/start_ticket.py` | ESC | (none) | OpenTicket | `partial` | Internal.tla:120 |
| 100 | `scripts/testgraph_channels.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 101 | `scripts/tla_spec_dev.py` | IN | 518,697 | all 14 Invoke* / Internal actions | `partial` | External.tla:65-191 |
| 102 | `skill-scripts/install-tla-spec-dev.sh` | ESC | (none) | none | `unrepresented` | no action names this module |
| 103 | `skill-scripts/install-tlc2.sh` | ESC | (none) | none | `unrepresented` | no action names this module |
| 104 | `spec_double_compiler/__init__.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 105 | `spec_double_compiler/runtime.py` | IN | 918 | none | `unrepresented` | no action names this module |
| 106 | `specs/current/production_adapters.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 107 | `specs/current/tests/test_current_ticket_workflow.py` | IN | 573,974 | none | `unrepresented` | no action names this module |
| 108 | `specs/current/tests/test_tla_spec_dev_analyze_adapter.py` | IN | 573,974 | none | `unrepresented` | no action names this module |
| 109 | `specs/current/tests/test_tla_spec_dev_budgets_adapter.py` | IN | 573,974 | none | `unrepresented` | no action names this module |
| 110 | `specs/current/tests/test_tla_spec_dev_cli_adapter.py` | IN | 573,974 | none | `unrepresented` | no action names this module |
| 111 | `specs/current/tests/test_tla_spec_dev_close_promotion_adapter.py` | IN | 573,974 | none | `unrepresented` | no action names this module |
| 112 | `specs/current/tests/test_tla_spec_dev_complexity_ledger_adapter.py` | IN | 573,974 | none | `unrepresented` | no action names this module |
| 113 | `specs/current/tests/test_tla_spec_dev_corpus_adapter.py` | IN | 573,974 | none | `unrepresented` | no action names this module |
| 114 | `specs/current/tests/test_tla_spec_dev_effect_conformance_adapter.py` | IN | 573,974 | none | `unrepresented` | no action names this module |
| 115 | `specs/current/tests/test_tla_spec_dev_kill_test_adapter.py` | IN | 573,974 | none | `unrepresented` | no action names this module |
| 116 | `specs/current/tests/test_tla_spec_dev_run_adapter.py` | IN | 573,974 | none | `unrepresented` | no action names this module |
| 117 | `specs/current/tests/test_tla_spec_dev_scaffold_adapter.py` | IN | 573,974 | none | `unrepresented` | no action names this module |
| 118 | `specs/current/tests/test_tla_spec_dev_skill_feedback_adapter.py` | IN | 573,974 | none | `unrepresented` | no action names this module |
| 119 | `specs/current/tests/test_tla_spec_dev_test_graph_adapter.py` | IN | 573,974 | none | `unrepresented` | no action names this module |
| 120 | `specs/current/tests/test_tla_spec_dev_ticket_adapter.py` | IN | 573,974 | none | `unrepresented` | no action names this module |
| 121 | `specs/desired_program_model/production_adapters.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 122 | `specs/desired_program_model/tests/test_tla_spec_dev_cli_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 123 | `specs/desired_program_model/tests/test_tla_spec_dev_run_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 124 | `specs/desired_program_model/tests/test_tla_spec_dev_scaffold_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 125 | `specs/desired_program_model/tests/test_tla_spec_dev_test_graph_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 126 | `specs/desired_program_model/tests/test_tla_spec_dev_ticket_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 127 | `specs/program_model/production_adapters.py` | IN | 1405 | none | `unrepresented` | no action names this module |
| 128 | `specs/program_model/tests/test_tla_spec_dev_cli_adapter.py` | IN | 1405 | none | `unrepresented` | no action names this module |
| 129 | `specs/program_model/tests/test_tla_spec_dev_run_adapter.py` | IN | 1405 | none | `unrepresented` | no action names this module |
| 130 | `specs/program_model/tests/test_tla_spec_dev_scaffold_adapter.py` | IN | 1405 | none | `unrepresented` | no action names this module |
| 131 | `specs/program_model/tests/test_tla_spec_dev_test_graph_adapter.py` | IN | 1405 | none | `unrepresented` | no action names this module |
| 132 | `specs/program_model/tests/test_tla_spec_dev_ticket_adapter.py` | IN | 1405 | none | `unrepresented` | no action names this module |
| 133 | `specs/tickets/MF-023/current/production_adapters.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 134 | `specs/tickets/MF-023/current/tests/test_tla_spec_dev_analyze_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 135 | `specs/tickets/MF-023/current/tests/test_tla_spec_dev_budgets_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 136 | `specs/tickets/MF-023/current/tests/test_tla_spec_dev_cli_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 137 | `specs/tickets/MF-023/current/tests/test_tla_spec_dev_close_promotion_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 138 | `specs/tickets/MF-023/current/tests/test_tla_spec_dev_complexity_ledger_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 139 | `specs/tickets/MF-023/current/tests/test_tla_spec_dev_corpus_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 140 | `specs/tickets/MF-023/current/tests/test_tla_spec_dev_effect_conformance_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 141 | `specs/tickets/MF-023/current/tests/test_tla_spec_dev_kill_test_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 142 | `specs/tickets/MF-023/current/tests/test_tla_spec_dev_run_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 143 | `specs/tickets/MF-023/current/tests/test_tla_spec_dev_scaffold_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 144 | `specs/tickets/MF-023/current/tests/test_tla_spec_dev_skill_feedback_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 145 | `specs/tickets/MF-023/current/tests/test_tla_spec_dev_test_graph_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 146 | `specs/tickets/MF-023/current/tests/test_tla_spec_dev_ticket_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 147 | `specs/tickets/MF-023/desired/production_adapters.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 148 | `specs/tickets/MF-023/desired/tests/test_tla_spec_dev_analyze_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 149 | `specs/tickets/MF-023/desired/tests/test_tla_spec_dev_budgets_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 150 | `specs/tickets/MF-023/desired/tests/test_tla_spec_dev_cli_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 151 | `specs/tickets/MF-023/desired/tests/test_tla_spec_dev_close_promotion_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 152 | `specs/tickets/MF-023/desired/tests/test_tla_spec_dev_complexity_ledger_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 153 | `specs/tickets/MF-023/desired/tests/test_tla_spec_dev_corpus_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 154 | `specs/tickets/MF-023/desired/tests/test_tla_spec_dev_effect_conformance_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 155 | `specs/tickets/MF-023/desired/tests/test_tla_spec_dev_kill_test_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 156 | `specs/tickets/MF-023/desired/tests/test_tla_spec_dev_run_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 157 | `specs/tickets/MF-023/desired/tests/test_tla_spec_dev_scaffold_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 158 | `specs/tickets/MF-023/desired/tests/test_tla_spec_dev_skill_feedback_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 159 | `specs/tickets/MF-023/desired/tests/test_tla_spec_dev_test_graph_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 160 | `specs/tickets/MF-023/desired/tests/test_tla_spec_dev_ticket_adapter.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 161 | `specs/tickets/MF-023/tests/test_ticket_workflow.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 162 | `test_graph/build-logic/build.gradle.kts` | ESC | (none) | none | `unrepresented` | no action names this module |
| 163 | `test_graph/build-logic/settings.gradle.kts` | ESC | (none) | none | `unrepresented` | no action names this module |
| 164 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Context.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 165 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Executors.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 166 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/JBangExecutor.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 167 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/PlanExecutor.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 168 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/TimeoutParser.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 169 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/UvExecutor.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 170 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphAssembler.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 171 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphModel.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 172 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/MiniJson.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 173 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/NodeDescribeLoader.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 174 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/InspectionTasks.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 175 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunReportWriter.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 176 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunTestGraphTask.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 177 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/ValidationReportTask.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 178 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/TestGraphSpec.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 179 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/Toolchain.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 180 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphExtension.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 181 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphPlugin.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 182 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationNodeSpec.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 183 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationRuntime.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 184 | `test_graph/build-logic/src/test/kotlin/com/hayden/testgraphsdk/exec/PlanExecutorResumeHarnessTest.kt` | ESC | (none) | none | `unrepresented` | no action names this module |
| 185 | `test_graph/build.gradle.kts` | ESC | (none) | none | `unrepresented` | no action names this module |
| 186 | `test_graph/sdk/java/build.gradle.kts` | ESC | (none) | none | `unrepresented` | no action names this module |
| 187 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextItem.java` | ESC | (none) | none | `unrepresented` | no action names this module |
| 188 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextSerde.java` | ESC | (none) | none | `unrepresented` | no action names this module |
| 189 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Json.java` | ESC | (none) | none | `unrepresented` | no action names this module |
| 190 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/JsonMapper.java` | ESC | (none) | none | `unrepresented` | no action names this module |
| 191 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Node.java` | ESC | (none) | none | `unrepresented` | no action names this module |
| 192 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeBody.java` | ESC | (none) | none | `unrepresented` | no action names this module |
| 193 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeContext.java` | ESC | (none) | none | `unrepresented` | no action names this module |
| 194 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeResult.java` | ESC | (none) | none | `unrepresented` | no action names this module |
| 195 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeSpec.java` | ESC | (none) | none | `unrepresented` | no action names this module |
| 196 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeStatus.java` | ESC | (none) | none | `unrepresented` | no action names this module |
| 197 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ProcessRecord.java` | ESC | (none) | none | `unrepresented` | no action names this module |
| 198 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Procs.java` | ESC | (none) | none | `unrepresented` | no action names this module |
| 199 | `test_graph/sdk/python/src/testgraphsdk/__init__.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 200 | `test_graph/sdk/python/src/testgraphsdk/context_item.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 201 | `test_graph/sdk/python/src/testgraphsdk/context.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 202 | `test_graph/sdk/python/src/testgraphsdk/node_spec.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 203 | `test_graph/sdk/python/src/testgraphsdk/procs.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 204 | `test_graph/sdk/python/src/testgraphsdk/result.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 205 | `test_graph/sdk/python/src/testgraphsdk/runner.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 206 | `test_graph/settings.gradle.kts` | ESC | (none) | none | `unrepresented` | no action names this module |
| 207 | `test_graph/sources/spec_workflow_cleanup.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 208 | `test_graph/sources/spec_workflow_close_ticket.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 209 | `test_graph/sources/spec_workflow_complete_ticket.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 210 | `test_graph/sources/spec_workflow_create_repo.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 211 | `test_graph/sources/spec_workflow_failure_cleanup_probe.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 212 | `test_graph/sources/spec_workflow_force_failure.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 213 | `test_graph/sources/spec_workflow_spec_units.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 214 | `test_graph/sources/spec_workflow_start_ticket.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 215 | `test_graph/sources/tla_spec_dev_cli_help.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 216 | `test_graph/sources/tla_spec_dev_cli_install.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 217 | `tests/conftest.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 218 | `tests/corpus_fixtures.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 219 | `tests/effect_adapter_fixtures.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 220 | `tests/test_analyze_complexity.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 221 | `tests/test_budgets.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 222 | `tests/test_case_adapter_runtime.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 223 | `tests/test_complexity_ledger.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 224 | `tests/test_corpus_diagnostics.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 225 | `tests/test_effect_conformance_cli.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 226 | `tests/test_effect_conformance_runner.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 227 | `tests/test_effect_conformance.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 228 | `tests/test_export_testgraph_cases.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 229 | `tests/test_extract_spec_manifest.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 230 | `tests/test_generate_cases_from_tlc_dump.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 231 | `tests/test_kill_test.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 232 | `tests/test_new_ticket_workflow.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 233 | `tests/test_onboard_program_model.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 234 | `tests/test_promotion_preserves_current.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 235 | `tests/test_scaffold_spec_views.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 236 | `tests/test_skill_feedback.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 237 | `tests/test_source_model_references.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 238 | `tests/test_spec_yaml_valid.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 239 | `tests/test_testgraph_channels.py` | ESC | (none) | none | `unrepresented` | no action names this module |
| 240 | `tests/test_tla_spec_dev_cli.py` | ESC | (none) | none | `unrepresented` | no action names this module |

### 2.5 Sweep 1 summary

| | count |
|---|---|
| Rows (M) | 240 |
| In scope (quoted plan line) | 104 |
| Escalated (plan silent) | 136 |
| Out of scope | **0** |
| `represented` | **0** |
| `partial` | 24 (14 in scope, 10 escalated) |
| `unrepresented` | 216 (90 in scope, 126 escalated) |

---

## 3. Sweep 2 — Effects, by category

### 3.0 Enumeration protocol

```bash
SURFACE=$(cat /tmp/ca/SURFACE.txt)          # the 240 files Sweep 1 enumerated -- NOT a subdirectory
mkdir -p specs/tickets/MF-023/results/sweep-raw
/usr/bin/grep -nE "<pattern>" $SURFACE > specs/tickets/MF-023/results/sweep-raw/<category>.txt
wc -l < specs/tickets/MF-023/results/sweep-raw/<category>.txt
```

Patterns are word-boundary anchored per the prompt, and extended for Kotlin/Java
(`File`, `Files`, `ProcessBuilder`, `HttpClient`, `Instant`, `UUID`,
`currentTimeMillis`) so that no category is "searched only in Python in a
repository that is not only Python".

**`/usr/bin/grep` is used explicitly.** The interactive `grep` on this machine is
`ugrep`, which silently emitted a zero-line result for the same patterns. That is
itself a prompt finding — see §8.6, finding P-1.

Every category's raw output is checked in under
`specs/tickets/MF-023/results/sweep-raw/`, so `N` is an artifact a reviewer can
recount rather than an assertion.

**Grouping rule used for every category** (per the prompt's high-volume
allowance): *group by **distinct effect semantics**, where two hits belong to the
same group iff they perform the same boundary operation against the same
declared-port target class.* Every raw hit is accounted for in exactly one
group, and every group is dispositioned. **Destructive effects are enumerated
per-site and never grouped**, per the prompt.

### 3.1 Filesystem — raw `2378`, groups `9`, rule: distinct boundary operation × target class

`sweep-raw/filesystem.txt`. Raw hits by file bucket: `tests/**` 614,
`specs/tickets/MF-023/{current,desired,tests}/**` 357, `examples/**` 249,
`test_graph/**` 244, `specs/current/production_adapters.py` 117, the 15
plan-named `scripts/*.py` 476, `specs/current/tests/**` 67,
`specs/desired_program_model/**` 35, `specs/program_model/**` 20, remainder in
non-plan-named `scripts/*.py` 199.

| # | Site (group) | Effect performed | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| F1 | Writes under the spec tree — `scripts/spec_evolution.py:154-477`, `scripts/scaffold_spec.py`, `scripts/onboard_program_model.py:32 sites`, `scripts/new_ticket_workflow.py:87 sites`, `specs/current/production_adapters.py:117 sites` (1041 raw hits) | `filesystem.write` under `specs/**` | IN (partly) | 631, 519, 1405 | `spec_tree` (`spec_manifest.yaml:177-179`) | `partial` — the port covers the write; it does **not** cover the *delete* that accompanies replacement (group F9), nor writes outside `specs/**` (group F3) |
| F2 | Writes under a results/evidence tree — `scripts/complexity_ledger.py:25 sites`, `scripts/effect_conformance_report.py:20 sites`, `scripts/corpus_diagnostics.py:18 sites` (63) | `filesystem.write` under `results/**` | IN(1315) / ESC(corpus_diagnostics) | 1315 | `evidence_report` (`:180-182`) | `partial` — covers the write; the report path is also constructed from `$PWD`, which is unrepresented input (see §3.4) |
| F3 | Writes to a *temporary working directory* outside both globs — `scripts/run_generated_case_adapters.py:729` (`work_dir / "kind-work"`), `scripts/kill_test.py` mutant staging (37 hits), `tempfile`/`mkdtemp` uses across `tests/**` (614) | `filesystem.write` to `$TMPDIR/**` | IN(917) / ESC(kill_test.py, tests/) | 917 | **none** — no port's `target` glob (`**/specs/**`, `**/results/**`, `**/.venv/**`) matches a temp path | `undeclared` |
| F4 | Writes to the CLI virtualenv — `skill-scripts/install-tla-spec-dev.sh`, `skill-scripts/install-tlc2.sh` (jar into cache dir) | `filesystem.write` under `.venv/**` | ESC | (none) | `cli_artifact` (`:183-185`) | `partial` — `install-tlc2.sh` writes the tla2tools **jar to a cache dir, not `.venv`**; the glob does not match. The `BuildSkillCli`/`InstallLocalCli` actions have no other implementation in the surface. |
| F5 | Reads of the manifest / plan / budgets — `scripts/budgets.py:97-186`, `scripts/analyze_complexity.py:28 sites`, `scripts/extract_spec_manifest.py` (≈120) | `filesystem.read` | IN(752,696) / ESC(extract) | 752, 696 | **none** — no read port is declared for any type | `undeclared` — reads are unmodeled as effects *and* the model has no input variable carrying manifest contents |
| F6 | Vendored Test Graph SDK file I/O — `test_graph/build-logic/**` (244), `test_graph/sdk/**` | Kotlin/Java `File`/`Files` write, read, mkdirs | ESC | (none) | **none** | `undeclared` — and **the effect sandbox could not have seen these either**: `scripts/effect_conformance.py:355-360` patches only *this CPython interpreter*. `unobservable` is not `clean`. |
| F7 | Worked-example file I/O — `examples/distributed_history/**` (249) | write/read/mkdir | **IN** | **1178** | **none** | `undeclared` — see E-6; the example is a separate program with its own model |
| F8 | Ticket spec-double snapshots — `specs/tickets/MF-023/{current,desired,tests}/**` (357) | write/read (copies of the live adapters) | ESC | (none) | mirrors `spec_tree` | `undeclared` in their own right; they are copies of F1 |
| F9 | **DESTRUCTIVE — enumerated per-site below, never grouped** (13 in-scope sites) | `filesystem.delete` | see table | see table | **NO `filesystem.delete` PORT EXISTS** | `undeclared` |

Raw accounting: 1041 + 63 + 651 + 2 + 120 + 244 + 249 + 357 = 2727 ≥ 2378 because
groups F1/F3/F5 overlap on multi-token lines (a single line matching both `Path`
and `write_text` is one raw hit). The grouping rule assigns each *raw line* to its
**leftmost-matching** group in order F9 → F4 → F2 → F1 → F3 → F5 → F6 → F7 → F8;
under that rule the group sizes partition 2378 exactly. A reviewer applying that
stated order to `sweep-raw/filesystem.txt` lands on these nine groups.

#### 3.1-D Destructive filesystem effects — per-site, in-scope

Enumeration: `grep -nE '\b(rmtree|unlink|rmdir|truncate)\b|os\.remove|shutil\.rmtree|deleteRecursively|\.delete\(|\.rename\(|\.replace\(' $SURFACE` → **raw 95**, checked in as `sweep-raw/destructive.txt`.
Collapsing rule: **drop hits where the matched token is a string/dataclass method
rather than a filesystem operation** — `str.replace`, `dataclasses.replace`,
`re.Match.group().replace`. Collapsed 95 → **13 real filesystem-delete sites**,
of which 8 are in plan-named files.

| # | Site (`file:line`) | Effect performed | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| D1 | `scripts/spec_evolution.py:154` | `shutil.rmtree(state_dir)` — recursive delete of the TLC state dir | IN | 631 | none | `undeclared` |
| D2 | `scripts/spec_evolution.py:385` | `shutil.rmtree(dst)` — recursive delete of a destination tree before replacement | IN | 631 | none | `undeclared` |
| D3 | `scripts/spec_evolution.py:443` | `path.rmdir()` | IN | 631 | none | `undeclared` |
| D4 | `scripts/spec_evolution.py:477` | `target.unlink()` | IN | 631 | none | `undeclared` |
| D5 | `scripts/close_tickets.py:127` | `dst_files[relative].unlink()` — deletes files from project `current/` during promotion | IN | 1249 | none | `undeclared` |
| D6 | `scripts/close_tickets.py:232` | `shutil.rmtree(directory)` | IN | 1249 | none | `undeclared` |
| D7 | `scripts/close_spec_workflow.py:49` | `shutil.rmtree(path)` | IN | 1248 | none | `undeclared` |
| D8 | `scripts/generate_cases_from_tlc_dump.py:95` | `shutil.rmtree(metadir, ignore_errors=True)` — **and `ignore_errors=True` silently swallows every failure** | IN | 698, 821 | none | `undeclared` |
| D9 | `scripts/run_generated_case_adapters.py` (work-dir teardown) | recursive delete of the per-kind work dir | IN | 917 | none | `undeclared` |
| D10-D13 | `test_graph/sources/spec_workflow_cleanup.py`, `spec_workflow_create_repo.py`, `spec_workflow_complete_ticket.py`, `spec_workflow_failure_cleanup_probe.py` (1 site each) | recursive delete of fixture repos | ESC | (none) | none | `undeclared` |

> **Instrumentation is not declaration.** `scripts/effect_conformance.py:626,627,630,639,640`
> patches `os.unlink`, `os.rmdir`, `shutil.rmtree`, `Path.unlink`, `Path.rmdir`
> and classifies them as `filesystem.delete`. The oracle is *built* to observe
> exactly these 13 sites. The manifest declares no port of that type, so every
> one of them would report as an undeclared effect the moment a case could
> execute — which, per `findings.md` FINDING 4, no case can. **The dead corpus is
> what is currently hiding 13 undeclared destructive effects.** This is gap G12.

### 3.2 Subprocess — raw `751`, groups `5`, rule: distinct spawned child × target class

`sweep-raw/subprocess.txt`. By bucket: `examples/**` 167, `test_graph/**` 130,
`tests/**` 120, `specs/tickets/**` 70, `scripts/effect_conformance.py` 36,
`specs/current/production_adapters.py` 32, `scripts/kill_test.py` 32,
`scripts/onboard_program_model.py` 23, `scripts/tla_spec_dev.py` 22, remainder 119.

> **A `process.spawn` port declares the spawn, not what the child did.**

| # | Site (group) | Effect performed | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| S1 | `scripts/run_tlc.sh:32` — `exec java -cp "$TLA2TOOLS_JAR" tlc2.TLC -config ...` | `process.spawn` of the TLC JVM | ESC | (none) | `tlc_process` (`*java*`) | `partial` — the spawn matches; **the child writes a states directory, reads the .tla/.cfg, and allocates unbounded heap, none of which is represented.** Per MF-027's process-boundary rule the child's effects are listed as unrepresented. |
| S2 | `scripts/analyze_complexity.py` — **no spawn at all** (`grep -n 'subprocess\|timeout\|java' scripts/analyze_complexity.py` → 0 hits) | none | IN | 696, 753 | `tlc_process` declared for `AnalyzeComplexity` (`spec_manifest.yaml:200`) | **`dead_surface`, proven statically** — the action that declares `tlc_process` spawns nothing. This is gap G11 and it does **not** depend on the dead corpus. |
| S3 | `scripts/kill_test.py:592,614`, `scripts/run_kill_test.py:198`, `scripts/tla_spec_dev.py` (22 sites) — pytest / corpus-command subprocesses | `process.spawn` matching `*pytest*` | IN(518,1177) / ESC(kill_test.py) | 518, 1177 | `test_process` (`*pytest*`) | `partial` — the spawn matches; the child pytest process writes temp dirs, reads env, and **its 600 s timeout has no modeled outcome** (gap G9) |
| S4 | `test_graph/build-logic/**` `ProcessBuilder` (130), `test_graph/sdk/java/.../Procs.java` | `process.spawn` from a **Kotlin/JVM runtime the sandbox cannot enter** | ESC | (none) | none | `undeclared`, **and the shipped oracle could not have observed it either** — `effect_conformance.py` patches CPython only. `unobservable` is not `clean`. |
| S5 | `examples/**` (167), `specs/tickets/MF-023/**` snapshots (70), `tests/**` (120) | spawn of fixture CLIs, k3d, kubectl | IN(1178) / ESC | 1178 | none | `undeclared` |

Accounting: 1 + 1 + 199 + 130 + 357 = 688; the remaining 63 raw hits are the
prompt's own high-false-positive tokens (`run`, `call`, `exec`) matching
`run_id`, `caller`, `execute` in prose and identifiers. **Collapsed 751 → 688 by
the rule: drop hits where the matched token is not the head of a call to a
process-spawning API.** Every dropped hit is recoverable from the raw file.

### 3.3 Network — raw `52`, collapsed `26`, rule: drop hits in comments, docstrings and instrumentation-target strings

| # | Site (`file:line`) | Effect performed | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| N1 | `skill-scripts/install-tlc2.sh:37` — `curl -fL --retry 3 --retry-delay 1 "$JAR_URL" -o "$JAR_TMP"` | **HTTP GET to the TLA+ GitHub releases host**, with retry | ESC | (none) | **none — no `network.*` port exists** | `undeclared` |
| N2 | `test_graph/build-logic/.../Toolchain.kt:~60` — `ProcessBuilder("curl", "-fsSL", "-o", dest, url)` | HTTP GET downloading the JBang/uv toolchain | ESC | (none) | none | `undeclared`, **and unobservable** — a JVM-spawned curl is outside the CPython sandbox entirely |
| N3 | `examples/distributed_history/ecommerce_backend/service.py:*` — `urllib.request.urlopen(request, timeout=5)`, `urllib.error.HTTPError`, `URLError` (6 sites) | HTTP request/response | **IN** | **1178** | none | `undeclared` |
| N4 | `examples/distributed_history/specs/program_model/adapters.py` (6 sites) — `urlopen(..., timeout=5)` | HTTP request from a spec adapter | **IN** | **1178** | none | `undeclared` |
| N5 | `examples/distributed_history/test_graph/sources/{collect_evidence,deploy_ecommerce}.py` (5 sites) — `urlopen`, `socket.socket(AF_INET, SOCK_STREAM)` | TCP connect + HTTP | **IN** | **1178** | none | `undeclared` |
| N6 | `examples/run_distributed_history_validation.py:*` — `socket.socket`, `urlopen(..., timeout=1)` | TCP connect + HTTP | ESC | (none) | none | `undeclared` |
| N7 | `examples/distributed_history/specs/program_model/tests/test_ecommerce_adapters.py`, `tests/test_testgraph_channels.py` (3) | HTTP inside test fixtures | IN(1178)/ESC | 1178 | none | `undeclared` |

Collapsed-out (26 of 52): 11 in `scripts/effect_conformance.py` are the
*instrumentation* — the strings `"network.connect"`, the `socket.socket.connect`
patch target, and docstrings; 2 in `scripts/onboard_program_model.py` are prose
in a generated template; the rest are `import` lines already counted with their
call sites. Rule: **a hit is dropped only if it is a comment, a docstring, or the
literal name of a boundary being patched rather than crossed.**

> **The repository performs real network egress and declares no network port.**
> `findings.md` does not record this, because effect conformance never executed.

### 3.4 Environment — raw `183`, groups `3`, rule: distinct input channel

| # | Site (group) | Effect performed | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| E1 | `argv` / CLI argument parsing — `scripts/tla_spec_dev.py:387-670`, `scripts/run_kill_test.py:104`, `scripts/close_ticket.py:24-28`, `scripts/close_spec_workflow.py:24-27` | process input read | IN | 518, 1177, 632, 1248 | none | `undeclared` — and see §4.6: the *flags* read here are unrepresented branches |
| E2 | `os.environ` / `getenv` / `expanduser` — `scripts/run_generated_case_adapters.py` (6), `scripts/tla_spec_dev.py` (3), `scripts/corpus_diagnostics.py` (3), `scripts/run_kill_test.py` (2), `scripts/complexity_ledger.py` (2), `scripts/analyze_complexity.py` (2), `scripts/skill_feedback.py` (3), `specs/current/production_adapters.py` (4), `specs/program_model/production_adapters.py` (1) (26) | environment read | IN(917,518,1177,1315,696,1405) / ESC(corpus_diagnostics, skill_feedback) | 917, 518 | none | `undeclared` — `spec_root` is modeled as a free choice from `SpecRoots` (`Internal.tla:85`), not as an env/argv-derived input. **The model cannot express "the environment supplied a root the program did not expect".** Gap G15. |
| E3 | `examples/**` (73), `test_graph/**` (65), `tests/**` (10), ticket snapshots (8) | environment read in example/harness code | IN(1178)/ESC | 1178 | none | `undeclared` |

Accounting: 26 + 156 = 182; 1 raw hit is `PATH` inside a comment in
`scripts/onboard_program_model.py` and is dropped by the rule **drop hits whose
match is inside a comment or a generated-template string**.

### 3.5 Clock — raw `188`, groups `2`, rule: real time read vs. token false positive

| # | Site (group) | Effect performed | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| C1 | Timestamped identifiers and history entries — `scripts/spec_evolution.py` (5), `scripts/new_ticket_workflow.py` (3), `scripts/complexity_ledger.py` (2), `scripts/generate_cases_from_tlc_dump.py` (2), `scripts/skill_feedback.py` (3), `scripts/kill_test.py` (1), `scripts/effect_conformance.py` (1), `specs/current/production_adapters.py` (1) (18) | wall-clock read; the value **enters a filesystem path** (`graph-reports/specWorkflow-20260720-001724-...`) | IN(631,698,1315)/ESC | 631 | none | `undeclared` — a nondeterministic input the model has no variable for. Every history entry name is clock-derived, and `CloseTicket` (`Internal.tla:320`) writes no such value. |
| C2 | `examples/**` (96), `test_graph/**` (67, incl. `TimeoutParser.kt`), `tests/**` (5), snapshots (2) (170) | timeouts, elapsed-time reporting | IN(1178)/ESC | 1178 | none | `undeclared` |

Collapsing: the prompt's `time` token matched `timeout`, `runtime`, `sometimes`
in prose; those are inside groups C1/C2 and are recoverable from
`sweep-raw/clock.txt`. Rule: **a hit is real iff the matched token is the head of
a call returning a clock value.** 188 raw → 18 real in-scope + 170
example/harness.

### 3.6 Randomness — raw `8`, collapsed `1`, rule: drop non-generating matches

| # | Site (`file:line`) | Effect performed | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| R1 | `scripts/kill_test.py:~540` — mutant selection over the catalog | deterministic ordering, no RNG call | ESC | (none) | none | `undeclared` — but no nondeterministic source; the 7 remaining raw hits are `random` in prose, `sample` as a noun, and `UUID` in vendored Kotlin. |

**The toolchain is free of runtime randomness.** Recorded as a positive result,
granted on the enumeration rather than on impression.

### 3.7 Persistent store — raw `65`, collapsed `3`, rule: drop ORM-shaped tokens that are not database calls

| # | Site (`file:line`) | Effect performed | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| P1 | `examples/distributed_history/ecommerce_backend/domain.py` — `sqlite3.connect(self.db_path, check_same_thread=False)` | SQLite open + `cursor`/`execute`/`commit` | **IN** | **1178** | none | `undeclared` |
| P2 | `examples/distributed_history/**` remaining (38) — `cursor`, `execute`, `commit` against P1's connection | database write | **IN** | **1178** | none | `undeclared` |
| P3 | `scripts/spec_evolution.py` (6), `scripts/generate_cases_from_tlc_dump.py` (3), others (13) — `execute`/`commit` as *git* verbs and `session` as a dict key | **not a persistent-store effect** | IN | 631, 698 | n/a | collapsed out |

**This repository has no database.** The 39 real hits are all in the worked
example, which line 1178 places in scope — see E-6.

---

## 4. Sweep 3 — Behaviors

### 4.1 Error paths — raw `610`, groups `5`, grouping rule: distinct *failure semantics*, i.e. what the program does after the failure

Enumeration: `grep -nE '\b(except|raise|try|catch|throw)\b' $SURFACE` → 610,
`sweep-raw/b-errorpaths.txt`.

| # | Behavior | Trigger (`file:line`) | In/Out | Plan line | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|
| B1 | **Refuse loudly and exit non-zero** — the doctrine-mandated path | `scripts/kill_test.py:904,909` ("There is no flag that skips the control."), `scripts/generate_cases_from_tlc_dump.py:802`, `scripts/export_testgraph_cases.py:164`, `scripts/effect_conformance.py:884`, `scripts/spec_evolution.py:626` | IN | 698, 822, 1107, 631 | **none** | `unrepresented` — the model has **no failure transition whatsoever**. Every guard failure is modeled as "no enabled transition" (`Internal.tla:65,74,84,…`), which is silence, not refusal. The program prints a reason and exits 1/2. Gap G18. |
| B2 | **Swallow and continue with a default** | `scripts/budgets.py:116-186` (`_coerce` → `DEFAULT_BUDGETS[key]`), `scripts/generate_cases_from_tlc_dump.py:95` (`ignore_errors=True`) | IN | 752, 698 | none | `unrepresented` — gap G8 |
| B3 | **Swallow silently (no warning)** | `scripts/corpus_diagnostics.py:541` — `load_budgets(Path("__missing__"), warn=False)` | **ESC** | (none) | none | `unrepresented` — **and this is the class the doctrine keeps rediscovering.** See §4.4. |
| B4 | Propagate to the caller — the ≈470 remaining `raise`/`except`/`try` sites across `scripts/**`, `tests/**`, `test_graph/**`, `examples/**` | many | mixed | 1178, 1405, various | none | `unrepresented` |
| B5 | JVM `catch`/`throw` in the vendored Test Graph SDK (`test_graph/build-logic/**`, `test_graph/sdk/java/**`) | ~120 | ESC | (none) | none | `unrepresented`, **and unobservable** by the shipped oracle |

Accounting: 6 + 2 + 1 + 470 + 120 = 599; the remaining 11 are the token `try` in
prose ("try running…"). Rule: **drop hits where the match is an English word in a
comment or help string.** A reader applying "group by what happens *after* the
failure" to `sweep-raw/b-errorpaths.txt` lands on B1–B5.

### 4.2 Retries — raw `77`, real `1`

| # | Behavior | Trigger (`file:line`) | In/Out | Plan line | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|
| T1 | `curl --retry 3 --retry-delay 1` when downloading tla2tools | `skill-scripts/install-tlc2.sh:37` | **ESC** | (none) | `InstallLocalCli` (`Internal.tla:73`) is the nearest action and **does not name a retry** | `unrepresented` — a 3-attempt network retry with a delay is a behavior; the model has one atomic transition |

The other 76 raw hits are the word `attempt` in prose (`scripts/kill_test.py:131,282`)
and `attempts` in vendored Kotlin. Rule: **a hit is real iff it configures or
implements a repeat-on-failure loop.**

### 4.3 Timeouts — raw `138`, real `5` in the toolchain

| # | Behavior | Trigger (`file:line`) | In/Out | Plan line | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|
| T2 | Per-mutant corpus timeout, default 600 s | `scripts/kill_test.py:592`, `:614` | ESC | (none) | `RunKillTest` verdicts are `{"pass","below_floor","incomplete_catalog"}` (`Internal.tla:258`) | `unrepresented` — **there is no timeout verdict.** A timed-out mutant run has no modeled outcome. Gap G9. |
| T3 | `--timeout` CLI flag, default 600 | `scripts/run_kill_test.py:104`, `:198` | **IN** | **1177** | same as T2 | `unrepresented` — gap G9 |
| T4 | `tlc_seconds: 120` declared as "hard external timeout per TLC run" | `specs/current/spec_manifest.yaml:84`, `scripts/budgets.py:41` | **IN** | **752** | none | `unrepresented` **and unenforced** — `scripts/run_tlc.sh:32` `exec java ...` applies no timeout, and `scripts/analyze_complexity.py` spawns nothing at all. **A declared budget no code reads.** Gap G10. |
| T5 | `AnalyzeComplexity` verdict domain `{"pass","fail"}` | `specs/current/Internal.tla:168` | **IN** | **696** | `AnalyzeComplexity` | `unrepresented` — TLC exhausting `tlc_seconds` is neither pass nor fail; the model has no third outcome. Gap G9. |
| T6 | HTTP timeouts `timeout=1/3/5/10` | `examples/**` (≈15 sites), `test_graph/.../TimeoutParser.kt` | IN(1178)/ESC | 1178 | none | `unrepresented` |

### 4.4 Fallbacks — raw `245`, groups `3`

> *"Pay specific attention to the class this doctrine keeps rediscovering: a
> guard that silently passes when its input is absent."*

| # | Behavior | Trigger (`file:line`) | In/Out | Plan line | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|
| K1 | **`load_budgets` substitutes `DEFAULT_BUDGETS` when the manifest is missing, unreadable, or missing keys, then the gate proceeds and its VERDICT reads as authoritative** | `scripts/budgets.py:154-186` | **IN** | **752** | Every gate action guards on `setup_phase >= SetupBudgetsRecorded` (`Internal.tla:166,191,221,256`) | `unrepresented` — **the model asserts an ordering the program does not have.** In the model there is no path to `AnalyzeComplexity` without recorded budgets; in the program there is, and it is the *default* on a missing manifest. Gap G8. `ticket_plan.yaml:542` already WITHDREW this fallback ("a missing budgets block must fail"); the withdrawal has not landed. |
| K2 | **The same fallback with warnings suppressed entirely** | `scripts/corpus_diagnostics.py:541` — `load_budgets(Path("__missing__"), warn=False)`; also `specs/current/production_adapters.py:691` | **ESC** (corpus_diagnostics is named nowhere in an `implementation_scope`) / **IN** (production_adapters via 1405) | 1405 | none | `unrepresented` — **this is the guard that silently passes when its input is absent, in the literal form the prompt names.** `findings.md` "The escapes, tested" records the budgets fallback as *"Yes — always warns"*; that is **contradicted at `corpus_diagnostics.py:541`**, where `warn=False` is passed unconditionally. The audit reports the measurement, not the claim. |
| K3 | `or None` / `getattr` / `default=` argparse defaults across `scripts/**`, `tests/**`, `examples/**`, `test_graph/**` (≈240) | many | mixed | various | none | `unrepresented` |

### 4.5 Concurrency / interleaving — raw `11`, real `4`

| # | Behavior | Trigger (`file:line`) | In/Out | Plan line | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|
| X1 | `Thread.currentThread().interrupt()` on interrupted process wait | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Procs.java:87` | ESC | (none) | none | `unrepresented` |
| X2 | `java.util.concurrent.TimeUnit` in process wait | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Executors.kt:7,107`, `Toolchain.kt:5` | ESC | (none) | none | `unrepresented` |
| X3 | `sqlite3.connect(..., check_same_thread=False)` — **explicitly disables SQLite's cross-thread guard** | `examples/distributed_history/ecommerce_backend/domain.py` | **IN** | **1178** | none | `unrepresented` |
| X4 | "Suite-wide external setup: start/await the app" — generated template text describing concurrent app startup | `scripts/onboard_program_model.py:660`, `scripts/scaffold_spec.py:415` | IN(519)/ESC | 519 | none | `unrepresented` (template prose, no runtime behavior in this repo) |

The remaining 7 raw hits are `lock` inside `_parse_block`-shaped identifiers and
`Lock` in vendored imports — exactly the run-1 false-positive class the anchored
pattern was meant to suppress; the anchoring worked (11 raw, not 81).

**No concurrency in the Python toolchain itself.** Granted on the enumeration.

### 4.6 Config-driven branches — raw `101`, real `10` flags

| # | Behavior | Trigger (`file:line`) | In/Out | Plan line | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|
| G-a | `--allow-over-budget` — proceed past a failing complexity gate | `scripts/generate_cases_from_tlc_dump.py:797,802,840`; `scripts/analyze_complexity.py:1143` | IN | 698, 696 | `RunSpecUnitTests(root, ticket, override)` (`Internal.tla:271,280-282`) | **`represented`** — the only flag in the repository that is modeled. Cited positively. |
| G-b | **`--accept-new` — "skip the current==desired check and overwrite current/ from desired/"** | `scripts/tla_spec_dev.py:651-655` | **IN** | **518** | `CloseTicket` (`Internal.tla:320`) has **no override input**; its guard `ticket_state[ticket] = TicketSpecUnitTestsPassed` is unconditional | `unrepresented` — **a flag that skips a promotion precondition and overwrites `current/`.** Gap G3. |
| G-c | `--allow-open` — "Allow snapshotting a ticket whose status is not closed/done" | `scripts/tla_spec_dev.py:647`; `scripts/close_ticket.py:24`; `scripts/close_spec_workflow.py:24` | **IN** | **518, 632, 1248** | `CloseTicket` guard, as above | `unrepresented` — gap G4 |
| G-d | `--no-promote-current` — "Do not replace project current/ with ticket desired/" | `scripts/tla_spec_dev.py:649`; `scripts/close_ticket.py:26` | **IN** | **518, 632** | none | `unrepresented` — gap G5 |
| G-e | `--no-skill-feedback` | `scripts/close_ticket.py:28`; `scripts/close_spec_workflow.py:27`; `scripts/close_tickets.py:247` | **IN** | **632, 1248, 1249** | none — `skill_feedback` model state was removed (`ticket_plan.yaml:1281-1289`) | `unrepresented` — gap G6 |
| G-f | `--no-batch` — "Run generated cases as one Python program per case instead of batched" | `scripts/tla_spec_dev.py:494` | **IN** | **518** | `RunSpecUnitTests` | `unrepresented` — gap G7 |
| G-g | `--views` "additive" scaffold flag | `scripts/scaffold_spec.py:794` | ESC | (none) | `ScaffoldProject` | `unrepresented` |
| G-h | `--workflow-name` / `--entry-name` / `--ticket-root` overrides of the history path | `scripts/tla_spec_dev.py:644-648` | **IN** | **518** | none | `unrepresented` |
| G-i | `--result` (append) — which artifacts get snapshotted | `scripts/tla_spec_dev.py:646` | **IN** | **518** | none | `unrepresented` |
| G-j | **`close workflow` is advertised in help but has no subparser** — `close_parser` help reads "Close ticket or workflow history." yet `close_sub` registers only `"ticket"` | `scripts/tla_spec_dev.py:626,635-636` | **IN** | **518** | none | `unrepresented` — an advertised command that cannot be invoked. Gap G17. |

The other 91 raw hits are the word "flag" in doctrine prose ("there is no flag
that skips this") — 30 of them in `scripts/kill_test.py`, `scripts/tla_spec_dev.py`,
`scripts/effect_conformance.py`. Rule: **a hit is real iff it registers or reads a
runtime option.** Those 91 are, notably, the repository asserting that flags do
not exist; the enumeration found 10 that do, 9 of them unmodeled.

---

## 5. Sweep 4 — Views, reported separately

**Both view modules now exist**, so this section reports two independent verdicts
per `ticket_plan.yaml:1430` and `:1380`. They are **not** merged.

### 5.1 Internal — verdict: `FAIL` (7 in-scope gaps attributable to this view)

Internal is the component detail: internal actions, component state, and the
interleaving between components.

| Surface item | Verdict | Evidence |
|---|---|---|
| 7 state variables (`setup_phase`, `spec_root`, `ticket_state`, `complexity_gate`, `corpus_gate`, `effect_conformance`, `kill_test`) | `represented` | `Internal.tla:30-37`; all 7 constrained by `TypeInvariant` `Internal.tla:385-398` |
| 14 lifecycle actions | `represented` (success path only) | `Internal.tla:64,73,83,98,109,120,136,146,165,190,220,255,271,320` |
| 14 named safety invariants | `represented` | `Internal.tla:385-498`, conjoined at `:500-514` |
| `--allow-over-budget` override | `represented` | `Internal.tla:271,280-282` — the `override` input |
| Budgets precondition on every gate action | `represented` **in the model**, contradicted by the program | `Internal.tla:166,191,221,256` vs `scripts/budgets.py:154-186` — gap G8 |
| Refusal / non-zero-exit outcomes | `unrepresented` | no action in `Internal.tla` has a failure branch; disabledness is the only failure. Gap G18 |
| Timeout outcomes (`AnalyzeComplexity`, `RunKillTest`) | `unrepresented` | verdict domains `Internal.tla:168`, `:258` admit no timeout. Gap G9 |
| `--accept-new`, `--allow-open`, `--no-promote-current` on close | `unrepresented` | `CloseTicket` `Internal.tla:320-329` takes no override input. Gaps G3, G4, G5 |
| `--no-batch`, `--no-skill-feedback` | `unrepresented` | Gaps G6, G7 |
| Environment / argv as an input channel | `unrepresented` | `spec_root` is a free choice from `SpecRoots` (`Internal.tla:85`), not derived input. Gap G15 |
| Clock-derived history entry names | `unrepresented` | `CloseTicket` `Internal.tla:320` writes no timestamp; §3.5 C1 |
| `filesystem.delete` at 13 sites | `unrepresented` | no port of that type; §3.1-D. Gap G12 |
| Concurrency / interleaving between components | `unrepresented` — **and correctly so** | §4.5: the Python toolchain has none. Granted on the enumeration, not on impression. |
| Stutter self-loops removed | `represented`, retention proven | `Internal.tla:331-344`; 42,861 distinct at depth 24 with and without |

**Internal's structural strength is genuine**: 7 of 7 variables are
`TypeInvariant`-constrained, 14 invariants are conjoined and named, and the
`override` input is the one flag in the repository that is faithfully modeled.
**Internal's weakness is uniform**: it models only the *accepting* half of every
transition.

### 5.2 External — verdict: `FAIL` (6 in-scope gaps attributable to this view)

External is the public input surface and the observable projection: what a caller
can drive and what a caller can see.

| Surface item | Verdict | Evidence |
|---|---|---|
| `lastCommand`, `result` channel variables | `represented` | `External.tla:35-37`, `ChannelVars` `:50` |
| 14 `Invoke*` wrappers, one per Internal action | `represented` | `External.tla:65-191`, `ExternalNext:197-223` |
| Verdict-dependent `result.next` for 3 commands | `represented` | `External.tla:145-152` (4-way CASE), `:161-166`, `:175-184` |
| `ExternalInvariant` | `partial` | `External.tla:235-238` constrains `result.accepted` and `result.next` — **and says nothing whatsoever about `lastCommand`**, which is otherwise unconstrained by any invariant in either view |
| **Failure results for 11 of 14 commands** | `unrepresented` | `Emit(..., TRUE, NoReason, ...)` at `External.tla:67,74,81,88,95,102,109,116,124,131,191` — **every one of these commands succeeds unconditionally in the model.** Only `InvokeRunEffectConformance`, `InvokeRunKillTest` and `InvokeRunSpecUnitTests` can emit `FALSE`. Gap G1 |
| **`result.reason` is never populated** | `unrepresented` | `NoReason` is the `reason` argument at **every** `Emit`/`CommandResult` site in `External.tla`. The CLI's failure-reason output is a real observable channel with a modeled field that is constant. Gap G1 |
| **`incomplete_command`** — a partial invocation (`tla-spec-dev close`, `run`, `scaffold`, `open` with no target) prints help plus a `next_step` and returns non-zero | `unrepresented` | `scripts/tla_spec_dev.py:631-634` (`func=incomplete_command`, `next_step=...`), and the identical pattern at `:392`, `:436`, `:462`, `:568`. **Exercised by the shipped cliWorkflow graph** — `specs/tickets/MF-023/results/graph-reports/cliWorkflow-*/node-logs/spec.cli.help.incomplete-{close,open,run,scaffold}.log`. There is no `Invoke` action for it. Gap G2 |
| **Help and version output** | `unrepresented` | `main()` `scripts/tla_spec_dev.py:665-670` prints help and returns 0 when no handler resolves; the cliWorkflow graph exercises 10 distinct help/version nodes (`node-logs/spec.cli.help.{root,project,workflow,scaffold,open-ticket,close-ticket,run-spec-units}-help.log`, `.version.log`). **A caller-drivable command with observable output and no modeled action.** Part of gap G2 |
| **`close workflow`, advertised and unreachable** | `unrepresented` | `scripts/tla_spec_dev.py:626` vs `:635-636`. Gap G17 |
| Every flag in §4.6 except `--allow-over-budget` | `unrepresented` | Gaps G3–G7 |
| `HiddenInternalProgress` deliberately absent | `represented` (a justified absence) | `External.tla:24-32`; retention proof depends on it |
| Retention: 231,621 distinct at depth 25, matching pre-split baseline | `represented`, **proven** | `spec_manifest.yaml:40-43,53-54`; `results/tlc-external-desired.txt` |

**The External view's shape is the finding.** It faithfully models the *channel
mechanism* — a command name and a result record are written on every transition —
and then populates that mechanism with a constant success for 11 of 14 commands
and a constant `NoReason` for all 14. The observable surface a caller actually
sees on a bad invocation — a reason string, a non-zero exit, a help dump, a
refusal naming the flag — is **entirely outside the model**, in the view whose
entire job is the observable projection.

### 5.3 The two views compared

| | Internal | External |
|---|---|---|
| Verdict | `FAIL` | `FAIL` |
| In-scope gaps attributable | 7 (G3, G4, G5, G8, G9, G12, G15) | 6 (G1, G2, G6, G7, G17, G18) |
| Shared / cross-cutting | G10, G11, G13, G14, G19, G20, G21 (7) | same 7 |
| Variables | 7, all `TypeInvariant`-constrained | +2, **neither constrained by any invariant** |
| Actions | 14 | 14 wrappers, 1:1 |
| Failure modeling | none | 3 of 14 commands |
| Distinct states | 42,861 @ depth 24 | 231,621 @ depth 25 (exact retention) |

A behavior represented in one view and absent from the other is exactly what
merging would hide, and there is one: the `override` input is modeled in both
(`Internal.tla:271`, `External.tla:172`), while the *channel consequence* of an
overridden run — what `result.reason` says when `--allow-over-budget` was used —
exists in neither.

---

## 6. Dispositions

Only three dispositions exist. **No "justified" or "accept as-is" disposition is
available for an in-scope gap** — `prompts/coverage_audit.md` §6. None is used
below, in any wording.

### 6.1 In-scope gaps — HARD, block promotion

| # | Gap | Sweep | Disposition | Proposed remediation (advisory) |
|---|---|---|---|---|
| **G1** | 11 of 14 External commands emit `TRUE, NoReason` unconditionally; `result.reason` is constant across the whole module. The CLI's failure-result surface is unmodeled. | 4 (External), 1 | **model it** | Give `Emit` a failure form and let each `Invoke*` range over `{accepted, refused}` with a `reason` drawn from a Core-defined `Reasons` set. Constrain `result.reason` in `ExternalInvariant`. |
| **G2** | `incomplete_command` and the help/version surface — caller-drivable commands with observable output and no action. Exercised by the shipped cliWorkflow graph. | 4 (External) | **model it** | Add `InvokeIncompleteCommand` and `InvokeHelp` emitting `accepted=FALSE`/`TRUE` with the `next_step` the parser already carries. The Test Graph nodes exist; only the model action is missing. |
| **G3** | `--accept-new` skips the current==desired check and overwrites `current/` from `desired/`. | 3 (§4.6 G-b) | **model it** *or* **change the program** | Preferred: remove the flag — it bypasses the promotion precondition `CloseTicket` exists to enforce. If retained, add an `acceptNew` input to `CloseTicket` and a weakened guard disjunct, so the bypass is visible in the state graph. |
| **G4** | `--allow-open` permits closing/snapshotting a ticket whose status is not closed/done. | 3 (§4.6 G-c) | **model it** *or* **change the program** | Same shape as G3; an `allowOpen` input disjunct on `CloseTicket`'s `ticket_state` guard. |
| **G5** | `--no-promote-current` suppresses the desired→current promotion at close. | 3 (§4.6 G-d) | **model it** | `CloseTicket` currently has one outcome; add the non-promoting variant so the post-state differs. |
| **G6** | `--no-skill-feedback` suppresses the skill-feedback emission on three close paths. | 3 (§4.6 G-e) | **model it** *or* **change the program** | The `skill_feedback` model state was deliberately removed (`ticket_plan.yaml:1281-1289`); if it stays removed, remove the flag, otherwise the program has a switch for a fact the model denies exists. |
| **G7** | `--no-batch` changes spec-unit execution mode. | 3 (§4.6 G-f) | **model it** | Add the mode as an input to `RunSpecUnitTests`, or remove the flag if the modes are behaviorally identical (they are not — batching changes process count, which crosses `test_process`). |
| **G8** | `load_budgets` substitutes `DEFAULT_BUDGETS` on a missing/unreadable manifest and the gate proceeds; the model makes recorded budgets a hard precondition of all four gate actions. The model asserts an ordering the program does not have. | 3 (§4.4 K1), 4 | **change the program** | `ticket_plan.yaml:542` already withdrew this ("a missing budgets block must fail"); land the withdrawal. That makes `Internal.tla:166,191,221,256` true rather than aspirational. |
| **G9** | No timeout outcome exists in any verdict domain. `RunKillTest` ∈ {pass, below_floor, incomplete_catalog}; `AnalyzeComplexity` ∈ {pass, fail}. Real timeouts at `run_kill_test.py:104,198` (600 s) and the `tlc_seconds` budget. | 3 (§4.3 T2-T5) | **model it** | Add `"timed_out"` to `KillTestVerdicts` and `ComplexityVerdicts` in `Core.tla`, and a `result.next` case in External telling the caller to raise the budget. |
| **G10** | `tlc_seconds: 120`, documented as "hard external timeout per TLC run", is enforced by no code: `run_tlc.sh:32` execs java bare, `analyze_complexity.py` spawns nothing. | 3 (§4.3 T4) | **change the program** | Apply the budget in `run_tlc.sh` (`timeout "$TLC_SECONDS" java …`) or delete the budget. A budget nothing reads is dead manifest surface. |
| **G11** | `tlc_process` (`process.spawn`, `*java*`) is declared for `AnalyzeComplexity`, which spawns nothing at all — dead port proven **statically**, independent of the dead corpus. | 2 (§3.2 S2) | **change the program** *or* **model it** | Either make `analyze complexity` actually invoke TLC (which `findings.md` FINDING 1 argues it must, to resolve EXTENDS), or move `tlc_process` to whichever action wraps `run_tlc.sh`. |
| **G12** | 13 real `filesystem.delete` sites (8 in plan-named files) and **no `filesystem.delete` port declared**, while `effect_conformance.py:626-640` instruments exactly that type. | 2 (§3.1-D) | **model it** | Declare a `spec_tree_delete` port of type `filesystem.delete` targeting `**/specs/**` and bind it to `CloseTicket`, `RunSpecUnitTests` and the promotion path. Destructive effects are the category where a missed site is a data-loss defect. |
| **G13** | Real network egress with no `network.*` port declared anywhere: `urlopen`/`socket.connect` across `examples/distributed_history/**` (17 sites, in scope per line 1178) plus `sqlite3.connect`. | 2 (§3.3, §3.7) | **model it** | Declare `network.connect` / `network.http` ports for the example's model, or amend line 1178 (see E-6). |
| **G14** | Process-boundary: `tlc_process` and `test_process` declare the *spawn*; the children (TLC JVM, pytest) perform their own filesystem and environment effects, none represented. | 2 (§3.2 S1, S3) | **model it** | Per MF-027's process-boundary finding, either declare the child's effects explicitly or record the boundary as an observability limit in the manifest. Do not re-collapse it to `clean`. |
| **G15** | Environment and argv are unrepresented as an input channel. `spec_root` is a free choice from `SpecRoots` (`Internal.tla:85`), so the model cannot express "the environment supplied a root the program did not expect". | 2 (§3.4 E2) | **model it** | Add a `NoRoot`-adjacent `BadRoot` element to `SpecRoots`, or an explicit input action `ConfigureSpecRoot(root)` whose refusal branch is reachable. |
| **G17** | `close workflow` is advertised in the `close` help text and has no registered subparser — an advertised, unreachable command. | 3 (§4.6 G-j) | **change the program** | Register the subparser (the implementation exists at `scripts/close_spec_workflow.py`) or fix the help text. Then model it. |
| **G18** | The model has **no failure transition at all**. Every guard failure is "no enabled transition"; the program prints a reason and exits 1 or 2, and 6 of its refusal messages are load-bearing doctrine ("There is no flag that skips the control"). | 3 (§4.1 B1), 4 | **model it** | This is the root of G1 and G2. A refusal is a state transition with an observable output, not the absence of one. Modeling it makes the epic's refusal doctrine checkable by TLC rather than by comment. |
| **G19** | The whole of `examples/distributed_history/**` — 66 enumerated files, a complete second program with HTTP, SQLite and Kubernetes surface — is placed **in scope by `ticket_plan.yaml:1178`** and is wholly unrepresented by this repository's model. | 1, 2, 3 | **model it** (as written) — **and see E-6** | The honest reading of line 1178 as written makes 66 files in-scope gaps. This audit does not resolve that by reasoning; it reports the gap and escalates the plan line. |
| **G20** | `specs/program_model/**` (6 files, in scope per line 1405): `production_adapters.py` and its 5 adapter test modules have no representation of their own behavior beyond the actions they adapt. | 1 | **model it** | Adapters are the seam the corpus drives; per `findings.md` FINDING 4 none implements `run(case, …)`, so this gap and that finding are the same defect seen from two sides. |
| **G21** | `specs/current/tests/**` (14 files) is placed in scope by `ticket_plan.yaml:573, 974` and is unrepresented. | 1 | **model it** (as written) — **and see E-1** | The manifest's own `test_modeling_rule: do_not_model_tests_or_validation_harnesses_as_program_behavior` (`spec_manifest.yaml:16`) says these must NOT be modeled. That rule lives in the manifest, not the plan; the plan is the scope authority and it scopes them in. Escalated rather than resolved. |

**Count: 20 in-scope gaps** (G1–G15, G17–G21; there is no G16 — the retry
behavior at `install-tlc2.sh:37` is escalated, not in scope).

### 6.2 Out-of-scope inventory — does not gate

**Empty.** No row in this report was classified out-of-scope, because the closure
rule permits an out-of-scope classification only from a quoted plan line that
*excludes* a path, and this plan contains no exclusion rule. Everything the plan
does not name is escalated (§6.3), not excluded.

### 6.3 Scope escalations — owner amends the plan, once

| # | Row | Plan line that should change | Argument |
|---|---|---|---|
| **E-1** | `specs/current/tests/**` (14 files) | `ticket_plan.yaml:573`, `:974` — `specs/current/tests` written without a trailing slash | Two problems in one line. (a) The closure rule grants directory closure only on a trailing slash or glob; this has neither, though no *file* of that name exists. This audit classified it as a directory **and** escalates the classification. (b) The manifest's `test_modeling_rule` (`spec_manifest.yaml:16`) forbids modeling tests as program behavior, which directly contradicts scoping them in. The owner should write `specs/current/tests/` and state whether test modules are in the coverage boundary. |
| **E-2** | `actions.yml`, `testgraph_bindings.yml` | `ticket_plan.yaml:919`, `:1044`, and `service_catalog:485` | **Neither file exists anywhere outside `examples/`.** `find . -name 'actions.yml' -o -name 'testgraph_bindings.yml' \| grep -v '^./examples/'` returns empty. Three plan lines and the `service_catalog` name a schema this repository does not have; `case_adapters.toml` appears to have taken its place. Amend the lines or create the files. |
| **E-3** | `test_graph specWorkflow / cliWorkflow bindings` | `ticket_plan.yaml:1408`, `service_catalog:493` | Not a path — neither a file nor a directory. It plausibly means `test_graph/sources/**` (10 Python node sources) and/or `test_graph/build.gradle.kts`. Under the closure rule it scopes **nothing**, so 25 `test_graph/` files that MF-023 plainly touched sit unclassified. Write the paths. |
| **E-4** | `specs/.history/**` — **1763 files, 81% of the raw enumeration** | any `implementation_scope`, or a new `service_catalog.excluded_boundaries` | This audit applied filter F1 to exclude the append-only promoted-ticket archive. **No plan line licenses that.** The exclusion is defensible (byte-for-byte historical copies) but it is a scope decision the auditing agent made, which is exactly what this gate forbids. The owner must write an exclusion rule. Until then, §7's verdict carries the INCOMPLETE caveat in §8.2. |
| **E-5** | `specs/tickets/*/results/**` — 165 files, including a fully vendored Kotlin/Java Test Graph SDK inside each report directory | as E-4 | Same argument. Recorded evidence artifacts are not program surface, but the plan does not say so. |
| **E-6** | `examples/distributed_history/**` — 66 files, gap G19 | `ticket_plan.yaml:1178` — currently `examples/distributed_history/ worked kill test` | **This is a scope-correctness argument, not a disposition.** Read as written, the trailing slash grants directory closure over an entire second program — an e-commerce backend with HTTP, SQLite, Kubernetes deploy scripts, and its own Internal/External model — and makes all 66 files in-scope gaps against *this* repository's model. That is almost certainly not what MF-016 meant: the ticket's subject is the kill test, and the qualifier "worked kill test" suggests only the kill-test artifacts. Per §6 of the prompt, an in-scope gap this auditor believes should not be modeled is **not** something to waive row-by-row; it is an argument that the plan line is wrong. The owner should narrow line 1178 to the specific kill-test paths, or confirm the example is genuinely in the coverage boundary. **Until amended, G19 stands as 66 in-scope gap rows.** |
| **E-7** | `scripts/corpus_diagnostics.py` — the silent-fallback site (§4.4 K2), the `AnalyzeCorpus` implementation | MF-014's `implementation_scope`, `ticket_plan.yaml:820-822` | The file appears in the plan **only in a retrospective prose note** (`:860`, "What landed: scripts/corpus_diagnostics.py"), never in an `implementation_scope` list. A prose mention is not a scope declaration, so under the closure rule the sole implementation of the modeled `AnalyzeCorpus` action is unclassified — **and it contains the one fully silent budgets fallback in the repository** (`:541`, `warn=False`). If MF-014's scope had named it, K2 would be an in-scope hard gap. Add it. |
| **E-8** | `scripts/kill_test.py`, `scripts/complexity_ledger.py`, `scripts/testgraph_channels.py`, `scripts/skill_feedback.py`, `scripts/scaffold_spec.py`, `scripts/scaffold_spec_workflow.py`, `scripts/start_ticket.py`, `scripts/new_ticket_workflow.py`, `scripts/generate_python.py`, `scripts/generate_docs.py`, `scripts/extract_spec_manifest.py`, `scripts/spec_paths.py`, `scripts/close-ticket.py`, `scripts/close-spec-workflow.py`, `scripts/run_tlc.sh` | various `implementation_scope` lists | 15 toolchain modules, several of which implement modeled actions (`scripts/kill_test.py` is the engine behind the scoped `run_kill_test.py`; `scripts/run_tlc.sh` is the only thing that actually spawns the `tlc_process` port; `scripts/scaffold_spec.py` implements `ScaffoldProject`), are named in no `implementation_scope`. The plan scopes wrappers and omits engines. |
| **E-9** | `skill-scripts/install-tlc2.sh`, `skill-scripts/install-tla-spec-dev.sh` | any `implementation_scope` | These are the sole implementation of `BuildSkillCli`/`InstallLocalCli` (`Internal.tla:64,73`) and the only network egress in the toolchain proper (§3.3 N1, §4.2 T1). Two modeled actions whose implementation the plan does not scope. |
| **E-10** | `tests/**` (24 files), `spec_double_compiler/__init__.py`, `specs/desired_program_model/**` (6), `specs/tickets/MF-023/{current,desired,tests}/**` (29), `test_graph/**` (25) | as above | Remaining unclassified surface, listed for completeness. `spec_double_compiler/runtime.py` **is** scoped (`:918`) while its sibling `__init__.py` is not — the closure rule at its sharpest. |

---

## 7. Verdict

- In-scope gaps: **20**
- Out-of-scope inventoried: **0** (the plan contains no exclusion rule — §6.2)
- Escalations: **10** (E-1 … E-10), covering **136 of 240** Sweep-1 rows
- **Verdict: `FAIL`**
  - **Internal: `FAIL`** — 7 attributable in-scope gaps
  - **External: `FAIL`** — 6 attributable in-scope gaps
  - Cross-cutting: 7

**This is not a PASS, and the in-scope gaps are not waivable.** Each is closed by
modeling it or by changing the program. `prompts/coverage_audit.md` §6: *"the
existence of an in-scope gap is not negotiable and not yours to waive."* The
remediations in §6.1 are advisory; the gaps are not.

**INCOMPLETE caveat, recorded rather than folded into the verdict.** Two declared
filters (F1, F2) excluded 1928 files that no plan line classifies. `FAIL` is
reported because 20 hard gaps were found in the surface that *was* walked, and
FAIL already blocks promotion; but a reader should treat the sweep's boundary as
auditor-chosen in that one respect until E-4 and E-5 are answered. See §8.2.

**Relationship to `results/findings.md`.** This audit is the completeness
complement to that fidelity report, and the two intersect at three points, each
of which this audit reaches independently:

- FINDING 4 (no adapter implements `run(case, …)`; 0 observed effects, all 5
  ports dead) is the *reason* gaps G11, G12, G13 and G14 are currently invisible
  to the effect oracle. This audit finds them **statically**, without executing
  anything — which is precisely the class of defect the four oracles cannot see.
  G11 in particular is provable from `grep` alone: the action declaring
  `tlc_process` spawns no process.
- FINDING 1 (`analyze complexity` does not resolve `EXTENDS`) means the static
  bound gate scores External on 2 of 9 variables and returns PASS. That is a
  gate disabling itself on the mandated architecture; it does not change any
  verdict here, but it means **no complexity number reported for External is
  evidence of anything**, and §5.2 relies on TLC's measured 231,621 rather than
  on the tool's reported bound.
- FINDING 5 (the kill test's control run refused, correctly, and produced no
  rate) means the mutation oracle has never run on this repository. Every
  boundary in §3 is therefore unmutated as well as unobserved.

None of these three is smoothed over. They are the mechanism by which 20 gaps
coexisted with green gates.

---

## 8. Attestation

### 8.1 Row-count reconciliation per sweep

| Sweep | Enumeration command | Raw N | Table M | `N == M` |
|---|---|---|---|---|
| 1 — surface | `git ls-files '*.py' '*.kt' '*.java' '*.kts' '*.sh'` → 2168; filters F1 (−1763) + F2 (−165) → `wc -l < /tmp/ca/SURFACE.txt` | **240** | **240** | ☑ |
| 2.1 filesystem | `grep -nE '\b(open\|Path\|write_text\|…\|deleteRecursively)\b' $SURFACE` | 2378 | 9 groups | ☑ **grouped** — rule stated §3.1, leftmost-match order given, every raw hit in exactly one group |
| 2.1-D destructive | `grep -nE '\b(rmtree\|unlink\|rmdir\|truncate)\b\|os\.remove\|…'` | 95 | **13 per-site** | ☑ collapsed 95→13; rule: drop `str`/`dataclasses.replace`. **Not grouped**, per the prompt |
| 2.2 subprocess | `grep -nE '\b(subprocess\|Popen\|run\|…\|ProcessBuilder\|exec)\b'` | 751 | 5 groups (688 accounted, 63 collapsed) | ☑ rule stated §3.2 |
| 2.3 network | `grep -nE '\b(socket\|connect\|requests\|urlopen\|…\|URLConnection)\b'` | 52 | 7 rows (26 real, 26 collapsed) | ☑ rule stated §3.3 |
| 2.4 environment | `grep -nE '\b(environ\|getenv\|…\|PATH)\b'` | 183 | 3 groups (182 + 1 collapsed) | ☑ |
| 2.5 clock | `grep -nE '\b(datetime\|now\|…\|Instant)\b'` | 188 | 2 groups (18 real + 170) | ☑ |
| 2.6 randomness | `grep -nE '\b(random\|randint\|…\|UUID)\b'` | 8 | 1 row (7 collapsed) | ☑ |
| 2.7 persistent store | `grep -nE '\b(sqlite3\|psycopg\|…\|commit)\b'` | 65 | 3 rows (39 real + 26 collapsed) | ☑ |
| 3.1 error paths | `grep -nE '\b(except\|raise\|try\|catch\|throw)\b'` | 610 | 5 groups (599 + 11 collapsed) | ☑ rule stated §4.1 |
| 3.2 retries | `grep -nE '\b(retry\|retries\|backoff\|attempt\|attempts\|max_tries)\b'` | 77 | 1 row (76 collapsed) | ☑ |
| 3.3 timeouts | `grep -nE '\b(timeout\|timeoutMs\|deadline\|expires\|TimeoutError\|TimedOut)\b'` | 138 | 5 rows (real sites; remainder in T6's example bucket) | ☑ |
| 3.4 fallbacks | `grep -nE '(\bfallback\b\|\bdefaults?\b\|\bor None\b\|except.*pass\|\bImportError\b\|\bgetattr\b)'` | 245 | 3 groups | ☑ |
| 3.5 concurrency | `grep -nE '\b(thread\|Thread\|async\|await\|lock\|Lock\|concurrent\|multiprocessing\|coroutine\|runBlocking\|Semaphore)\b'` | 11 | 4 rows (7 collapsed) | ☑ |
| 3.6 config branches | `grep -nE '(--no-\|--allow\|\bflag\b\|\benabled\b\|\bgetenv\b)'` | 101 | 10 rows (91 collapsed) | ☑ |
| 4 — views | `grep -nE '^[A-Za-z_][A-Za-z0-9_]*(\(.*\))? ==' specs/current/*.tla` | 62 defs (Core 6, Internal 35, External 21) | 14 + 13 surface items | ☑ — Sweep 4 is a per-view surface table, not a 1:1 enumeration of defs |

**No inequality was found. That is an assertion I am making about my own
diligence, and per `prompts/coverage_audit.md` it is not mechanically enforced —
see §8.6 finding P-4.** Every raw file is checked in under
`specs/tickets/MF-023/results/sweep-raw/` so a reviewer can recount every N above.

### 8.2 Surface NOT walked

Naming it, because "none" would be false:

1. **`specs/.history/**` — 1763 files (81% of the raw enumeration).** Excluded by
   filter F1. Not walked at all. No plan line classifies it (E-4).
2. **`specs/tickets/*/results/**` — 165 files.** Excluded by filter F2. Not
   walked (E-5).
3. **Non-code surface entirely**: 319 `.md`, 185 `.yaml`, 146 `.toml`, 740
   `.json`, 118 `.tla`, 115 `.cfg`, 12 `.j2` tracked files were **not**
   enumerated as program surface. `templates/**` is scoped in by
   `ticket_plan.yaml:520` and consists of `.j2`/`.md` templates — **so an
   in-scope directory was not swept.** Recorded as a completeness limit of this
   run, not resolved.
4. **Binary/build outputs** under `test_graph/build-logic/build/**` (22 `.jar`,
   class files) — not source.
5. Within the walked surface, **the vendored Kotlin/Java Test Graph SDK (105
   `.kt` + 60 `.java`) was enumerated and dispositioned but not read
   line-by-line**; its rows are inferred (§8.3).

Item 3 is the most consequential: `templates/**` is named by a quoted plan line
and was outside every enumeration glob.

### 8.3 Rows dispositioned from path/name rather than from reading code

Reporting this honestly, per the prompt: a high inferred count is not a failure;
concealing it is.

| Sweep | Rows READ | Rows INFERRED | Inferred set |
|---|---|---|---|
| 1 — surface (240) | **31** | **209** | The 31 read: `scripts/tla_spec_dev.py` (parser section 387-670), `scripts/budgets.py` (full), `scripts/analyze_complexity.py` (grep-verified for spawn/timeout), `scripts/effect_conformance.py` (instrumentation section), `scripts/run_kill_test.py`, `scripts/kill_test.py` (timeout section), `scripts/spec_evolution.py` (destructive sites), `scripts/close_ticket.py`/`close_tickets.py`/`close_spec_workflow.py` (flag + delete sites), `scripts/generate_cases_from_tlc_dump.py` (override + rmtree), `scripts/corpus_diagnostics.py:541`, `scripts/run_tlc.sh`, `skill-scripts/install-tlc2.sh`, `specs/current/{Core,Internal,External}.tla` (full), `specs/current/spec_manifest.yaml` (full), plus 14 files read only at their grep-matched lines. **Inferred: all 66 `examples/**`, all 105 `.kt` + 60 `.java`, all 29 `specs/tickets/MF-023/**` snapshots, all 24 `tests/**`, `specs/desired_program_model/**`, and the remaining `scripts/*.py` I saw only through category greps.** |
| 2 — effects (7 categories) | grep-line level for every row | group rows are aggregate | Every §3 row cites `file:line` from a checked-in raw file. Rows F6, F7, F8, S4, S5, E3, C2, K3, B4, B5 are **aggregates over files I did not open**; their effect *type* is grep-derived, their effect *semantics* is inferred from the matched token. |
| 3 — behaviors (6 classes) | 18 sites read | ~1160 raw hits grouped | The 18 read sites are every row in §4.2, §4.3, §4.5 and §4.6 that carries a specific `file:line`, plus §4.4 K1/K2. Groups B4, B5, K3 are inferred. |
| 4 — views | **all 3 modules read in full** | 0 | `Core.tla`, `Internal.tla` (519 lines), `External.tla` (242 lines) were read end to end. Sweep 4 is this report's most reliable section. |

**Sweep 1's 209 inferred rows are this report's weakest evidence** and the reader
should weight them accordingly. The three view modules and the ~50 specific
`file:line` findings in §3 and §4 are the strong rows.

### 8.4 Rows whose scope was decided by reasoning rather than a quoted plan line

Three, all escalated rather than silently classified:

1. **`specs/current/tests` → directory closure.** The line has no trailing slash.
   I classified it as a directory because no file of that name exists. That is
   reasoning. → **E-1**, and gap **G21** is reported on the as-written reading.
2. **Filters F1 and F2.** Excluding `specs/.history/**` and
   `specs/tickets/*/results/**` is a scope decision I made, not one I read. →
   **E-4, E-5**, and the INCOMPLETE caveat in §7.
3. **`scripts/corpus_diagnostics.py` → escalated, not scoped in**, even though it
   implements the modeled `AnalyzeCorpus` action and contains the single most
   consequential silent fallback found (§4.4 K2). Scoping it in "because it
   obviously belongs" is exactly the inference the closure rule forbids, so it is
   escalated and K2 is reported as an escalated finding rather than as an
   in-scope gap. → **E-7**. *If the owner scopes it in, the in-scope gap count
   becomes 21.*

No other row's scope was reasoned. Every `IN` classification in §2.4 traces to a
quoted line in §0.4.

### 8.5 Can a reader reproduce this row set from the recorded commands?

**☑ yes, with one qualification.** Every `N` in §8.1 is reproducible by running
the quoted command; every category's raw output is checked in under
`specs/tickets/MF-023/results/sweep-raw/`, so the counts can be recounted rather
than trusted. Sweep 1's 240-row set is reproducible exactly from the three
commands in §2.1 plus the two declared filters.

The qualification: the **grouping** of Sweeps 2 and 3 is reproducible only if the
reader applies the stated rules, including §3.1's leftmost-match ordering. A
reader who groups differently will get different group counts over the same raw
hits. The raw counts are objective; the group boundaries are rule-derived, and
the rules are stated so that they can be disputed.

### 8.6 Findings about this prompt itself

Required, and more valuable than a clean report.

**P-1 — `grep` is not `grep`, and the failure is silent and total.** On this
machine the interactive `grep` is `ugrep`. Given the prompt's exact patterns with
a large `$SURFACE` argument list, it emitted **zero matching lines with exit 0**
and a warning stream that looked like output. Every category would have been
reported `raw = 0`, i.e. **"this repository performs no filesystem effects, no
subprocess spawns, and no network calls"** — a perfectly clean, perfectly
formatted, entirely false report, produced by following the prompt verbatim. I
caught it only because "0 filesystem effects in a program that scaffolds
directory trees" is absurd on its face. The prompt's own §1 sanity-check
instinct ("an empty index means the enumeration failed") exists for Step 1 and
**not** for Steps 2 and 3, which are where the damage would have been. *Fix:
require a non-zero-count assertion per category, or pin `/usr/bin/grep`.*

**P-2 — Step 2 mandates one row per file, and Steps 3–4 grant grouping. At this
repository's scale that combination is the pressure the prompt warns about.**
Raw Sweep 1 is 2168 files. Only two filters — neither licensed by the plan —
brought it to a walkable 240, and even 240 produced 209 inferred rows. The
prompt's grouping allowance was added for Sweep 2 after run 1; **Sweep 1 has no
equivalent**, so an agent facing 2168 files must either fabricate, filter (a
scope decision the same prompt forbids), or report INCOMPLETE on the entire
gate. *Fix: extend the grouping allowance to Sweep 1, or require the plan to
carry an explicit exclusion rule so filtering is a read decision rather than an
authored one.*

**P-3 — the closure rule is correct and it exposes that this plan scopes wrappers
while omitting engines.** Applied strictly, 136 of 240 rows escalate. More
pointedly: `scripts/run_kill_test.py` is scoped and `scripts/kill_test.py` (which
implements it) is not; `spec_double_compiler/runtime.py` is scoped and its
`__init__.py` is not; `AnalyzeCorpus` is modeled and `corpus_diagnostics.py`,
its only implementation, is scoped nowhere. This is the rule working — it made a
real structural defect in the plan visible instead of letting me paper over it —
but a reader should understand that **E-7 through E-10 are the finding**, not
bookkeeping.

**P-4 — the self-report limitation is real and I can demonstrate it from this
run.** Per `prompts/coverage_audit.md` §"Known-open" and issue #48, `N == M` is
an assertion the auditing agent makes about itself. Run 1 reported `N ≠ M`
against itself three times; **I report `N == M` everywhere**, which is exactly
what an agent that had curated its tables would also report. The only thing
separating those two cases is the checked-in
`specs/tickets/MF-023/results/sweep-raw/` output — which narrows the hole and
does not close it, because I also authored the grouping rules that map raw hits
to rows. **A reviewer should recount at least §3.1-D (13 destructive sites from
95 raw hits) and §4.6 (10 flags from 101 raw hits) before relying on this
report**, since those two tables carry the highest-severity gaps and the largest
collapse ratios. The mechanical inventory that would close this is the tracked
follow-up; until it exists, §8 is the load-bearing section of this report and
the tables are not.

**P-5 — Step 3's default enumeration commands are hardcoded to
`scripts/ spec_double_compiler/`** (`prompts/coverage_audit.md:311-316`), while
Step 2 was explicitly fixed after run 1 to search `$SURFACE`. The same defect the
prompt documents fixing for Sweep 2 is still present, unfixed, in Sweep 3's
literal command block. Following it verbatim would have searched 32 of 240 files
and missed **every** timeout in `test_graph/**`, the `check_same_thread=False`
concurrency site, and all 17 network sites in `examples/**` — the last of which
line 1178 places *in scope*. I substituted `$SURFACE` and recorded that
substitution; an agent following the block literally would produce a Sweep 3 that
is narrower than the surface it claims to cover, which is the run-1 finding
recurring one step later. *Fix: replace `scripts/ spec_double_compiler/` with
`$SURFACE` in Step 3's commands.*
