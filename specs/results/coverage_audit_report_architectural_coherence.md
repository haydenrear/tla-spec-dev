# Coverage Audit Report — architectural-coherence epic (MF-026 gate)

## VERDICT (stated plainly, per the dispatch)

- **Verdict:** **`incomplete`**
- **In-scope gaps:** **12** (each would independently be a `fail`; the sweep is
  reported `incomplete` because HALT conditions were met at Step 0 and a named
  part of the surface was not walked — see §7 and §8)
- **Out-of-scope inventory:** **0** — the plan contains no line that places any
  surface out of scope, so nothing could be inventoried. This is not a claim
  that nothing is out of scope; it is a claim that the plan does not say so.
- **Scope escalations:** **7**
- **`scope_source`:** `specs/desired_program_model/ticket_plan.yaml` —
  `planning_rules` **:22-29**, `service_catalog` **:147-162**, and the fourteen
  ticket `implementation_scope` blocks at **:206-211, :282-289, :377-381,
  :494-498, :605-608, :706-710, :783-785, :870-874, :964-967, :1076-1079,
  :1142-1145, :1208-1213, :1271-1272, :1363-1365**.

> **HALT.** Step 0 of `prompts/coverage_audit.md` HALTS when "the plan declares
> no scope, or the declaration is too vague to classify a given module in or
> out" or when "the scope as written does not cover surface you can plainly
> see." Both conditions are met (ESC-1, ESC-2, ESC-3, ESC-4). The correct
> output is: **the plan's scope declaration is insufficient to run this gate —
> the owner must amend it.** The tables below are published anyway because the
> enumerations are real and the counts are useful, but they are **not** a
> completed classification: 187 of 596 Sweep-1 rows carry `ESCALATION` rather
> than a disposition, and that includes 24 of the 34 files in `scripts/`.

- **Epic / workflow:** `architectural-coherence-epic`, branch
  `epic/architectural-coherence`
- **Model audited:** `specs/desired_program_model/TlaSpecDevCli.tla`, byte-identical
  to `specs/current/TlaSpecDevCli.tla` (`diff` exit 0). 10 variables, 16 actions.
- **Commit:** audit started at `e9ae135`; the owner's close-prep commit
  `3467051` landed mid-audit. Every enumeration was re-verified at `3467051`
  and the Sweep-1 surface is byte-identical across the pair (§8.7).
- **Date:** 2026-08-01
- **Raw outputs:** `specs/results/coverage-audit-arch-coherence-raw/`
- **Reproducer:** `specs/results/coverage-audit-arch-coherence-raw/cac_ac_classify.py`
  and `.../cac_ac_external_surface.py`. Every table row set in this report is
  the output of one of those two scripts over the committed raw files. Nothing
  in a table was hand-curated.

> This audit checks **completeness of what is modeled**, not fidelity. The four
> oracles are bounded to what is already represented and cannot see this class
> of defect. See `prompts/coverage_audit.md`.

---

## 0. Declared scope (quoted verbatim from the plan)

### 0.1 `planning_rules` — `specs/desired_program_model/ticket_plan.yaml:22-29`

```yaml
# ticket_plan.yaml:22-29
planning_rules:
  current_model_rule: Update specs/current after each production slice lands as a whole-program working copy of specs/program_model, not a ticket projection.
  unit_validation_rule: Run current-model TLC and adapter/unit tests before adding graph execution.
  graph_rule: Add graph or integration nodes only after current-model validation passes.
  semantic_model_rule: Do not add test graph nodes, pytest jobs, CI workflow steps, integration harnesses, or validation scripts as TLA+ program state/actions.
  evidence_rule: Record tests and graph runs as evidence for semantic program actions in manifests or ticket status.
  desired_sync_rule: Update this file and spec_manifest.yaml whenever scope, order, acceptance checks, or status changes.
  promotion_rule: When specs/current equals specs/desired_program_model, promote the converged model to specs/program_model.
```

### 0.2 `service_catalog` — `ticket_plan.yaml:147-162`

```yaml
# ticket_plan.yaml:147-162
service_catalog:
  existing_boundaries:
    - "analyze complexity: the shipped descriptor (dimension table, bound, R/W matrix, modularity, dense rows) -- the input the architecture view is derived from"
    - "generate_cases_from_tlc_dump.py: view-aware case generation, the surface case modules enter through"
    - "spec_evolution.record_complexity_ledger: the standing-objective ledger (see CM-F1)"
    - "prompts/coverage_audit.md: the precedent for a sub-agent prompt as a shipped artifact"
  desired_boundaries:
    - "analyze architecture: model-implied components, single-writer ownership, ports, and the reflexion diff against production code"
    - "case_modules: manifest block declaring per-aspect modules, the view each extends, and its action scope"
    - "prompts/implementation_brief.md: the constrained ask that carries component ownership into generation"
    - "prompts/aspect_decomposition.md: the BDD decomposition ask, from the user's perspective"
  adapter_boundaries:
    - "specs/current/tests/test_tla_spec_dev_analyze_adapter.py: conformance for the analyze command family, extended by AC-01"
  known_gaps:
    - "The reflexion extractor ships for Python only (AC-02). Non-Python targets report unmappable, never silently clean -- the MF-027 refusal shape."
    - "Neither lever has eval coverage before EV-01/EV-02. Until then every claim in this epic is a design claim, not a measurement."
```

**There is no `out_of_scope` key, no exclusion rule, and no `known_gaps` entry
that places any program surface outside the model's obligation.** The two
`known_gaps` entries are statements about the reflexion extractor and about
eval coverage. Neither classifies a module.

### 0.3 Ticket `implementation_scope` blocks (all fourteen, verbatim)

```yaml
# ticket_plan.yaml:206-211 (CM-01)          # ticket_plan.yaml:282-289 (AC-01)
    implementation_scope:                       implementation_scope:
      - scripts/spec_evolution.py                 - scripts/analyze_architecture.py
      - scripts/generate_cases_from_tlc_dump.py   - scripts/tla_spec_dev.py
      - scripts/budgets.py                        - specs/current/TlaSpecDevCli.tla
      - tests/                                    - specs/current/MC.cfg
      - references/case_modules.md                - specs/current/tests/
                                                  - references/architecture_coherence.md
                                                  - SKILL.md
```

```yaml
# ticket_plan.yaml:377-381 (AC-02)          # ticket_plan.yaml:494-498 (AC-03)
    implementation_scope:                       implementation_scope:
      - scripts/architecture_reflexion.py         - prompts/
      - scripts/analyze_architecture.py           - templates/
      - tests/                                    - references/case_modules.md
      - references/architecture_coherence.md      - SKILL.md
```

```yaml
# ticket_plan.yaml:605-608 (AC-04)          # ticket_plan.yaml:706-710 (EV-01)
    implementation_scope:                       implementation_scope:
      - scripts/complexity_ledger.py              - examples/validation/
      - scripts/architecture_reflexion.py         - examples/case_modules/
      - references/architecture_tractability.md   - examples/distributed_history/
                                                  - examples/effect_providers/
```

```yaml
# ticket_plan.yaml:783-785 (EV-02)          # ticket_plan.yaml:870-874 (RP-01)
    implementation_scope:                       implementation_scope:
      - examples/validation/runs/                 - scripts/architecture_reflexion.py
      - NEXT-EPIC.md                              - scripts/analyze_architecture.py
                                                  - tests/
                                                  - references/architecture_coherence.md
```

```yaml
# ticket_plan.yaml:964-967 (RP-02)          # ticket_plan.yaml:1076-1079 (RP-04)
    implementation_scope:                       implementation_scope:
      - scripts/infer_action_params.py            - scripts/analyze_complexity.py
      - scripts/generate_cases_from_tlc_dump.py   - scripts/complexity_ledger.py
      - tests/                                    - tests/
```

```yaml
# ticket_plan.yaml:1142-1145 (RP-05)        # ticket_plan.yaml:1208-1213 (RP-03)
    implementation_scope:                       implementation_scope:
      - tests/test_new_ticket_workflow.py         - scripts/case_modules.py
      - references/generation_modes.md            - scripts/generate_cases_from_tlc_dump.py
      - specs/program_model/architecture_components.yaml
                                                  - references/case_modules.md
                                                  - prompts/aspect_decomposition.md
                                                  - tests/
```

```yaml
# ticket_plan.yaml:1271-1272 (RP-07)        # ticket_plan.yaml:1363-1365 (EV-03)
    implementation_scope:                       implementation_scope:
      - test_graph/                               - examples/validation/
                                                  - NEXT-EPIC.md
```

### 0.4 The closure rule as applied

Applied exactly as `prompts/coverage_audit.md` Step 0 writes it: an entry
naming a **file** scopes that file only; directory closure counts only where
the plan writes a trailing slash; **anything else is an ESCALATION, never an
inference**. The rule is implemented in `cac_ac_classify.py::scope_of` — a
reader can re-run it.

| Scope line | Covers | Sweep-1 rows |
|---|---|---|
| `ticket_plan.yaml:710` (EV-01) | `examples/effect_providers/` (directory) | 189 |
| `ticket_plan.yaml:709` (EV-01) | `examples/distributed_history/` (directory) | 69 |
| `ticket_plan.yaml:707,784,1364` (EV-01/EV-02/EV-03) | `examples/validation/`, `examples/validation/runs/` (directories) | 67 |
| `ticket_plan.yaml:210,380,873,967,1079,1213` (six tickets) | `tests/` (directory) | 32 |
| `ticket_plan.yaml:287` (AC-01) | `specs/current/tests/` (directory) | 17 |
| `ticket_plan.yaml:1272` (RP-07) | `test_graph/` (directory) | 13 |
| `ticket_plan.yaml:496` (AC-03) | `templates/` (directory) | 12 |
| `ticket_plan.yaml:207,208,209,283,284,378,606,965,1077,1209` | ten named `scripts/*.py` files | 10 |
| `ticket_plan.yaml:708` (EV-01) | `examples/case_modules/` (directory) | 0 (no code files) |
| `ticket_plan.yaml:495` (AC-03), `:152,:156,:157` | `prompts/` (directory) | 0 (no code files) |
| — **no plan line** — | everything else | **187 ESCALATION** |

**409 in-scope / 187 escalation / 0 out-of-scope.** Note what that split is
made of: **325 of the 409 in-scope rows are example fixtures under
`examples/**`**, while **24 of the 34 files in `scripts/` — the CLI this model
represents — are unclassifiable.** See ESC-2.

### 0.5 Escalations (ambiguous or missing boundary)

| # | Row / surface | Why the plan text does not classify it |
|---|---|---|
| **ESC-1** | The whole modeled-surface boundary | The predecessor plan was made self-contained on 2026-07-23 at the previous audit's own request (ESC-C2-1): its `semantic_model_rule` folded in every recorded out-of-model ruling and its `known_gaps` restated them (`specs/.history/complexity-descriptor-main-readiness/closed-snapshot/snapshots/desired_program_model/ticket_plan.yaml:49-68` and `:98-103`). The architectural-coherence plan **truncates `semantic_model_rule` back to one sentence** (`:26`) and replaces `known_gaps` entirely (`:160-162`). Every ruling that made the previous audit a PASS — the `generate` limitation, the per-flag/refusal-branch limitation, the single-module view-split limitation, the effect-provider/harness out-of-model amendment — is **absent from the plan this gate must read**. Reading them across from the sealed predecessor would be an inference, which Step 0 forbids. **This is a regression of the exact escalation the last audit raised.** |
| **ESC-2** | The use of `implementation_scope` as the audit's scope at all | `implementation_scope` is an **edit-permission list** (which files a ticket may touch), not a **representation scope** (which program surface the model must represent). Applying it puts 189 `examples/effect_providers/` fixture files — separate programs with their own models, promotion-blocked and never entering `specs/program_model` — in scope for `TlaSpecDevCli.tla`, while leaving `scripts/kill_test.py`, `scripts/effect_conformance.py`, `scripts/run_generated_case_adapters.py`, `scripts/new_ticket_workflow.py`, `scripts/onboard_program_model.py`, `scripts/scaffold_spec.py`, `scripts/spec_paths.py`, `scripts/corpus_diagnostics.py`, `scripts/run_kill_test.py`, `scripts/effect_conformance_report.py` and 14 more named by no line. The plan needs a scope declaration that is about representation. |
| **ESC-3** | `tests/` (`:210`), `specs/current/tests/` (`:287`), `test_graph/` (`:1272`) — 62 rows | In scope by `implementation_scope`, and simultaneously **un-modelable by the plan's own `semantic_model_rule` (`:26`)**, which forbids adding test graph nodes, pytest jobs, integration harnesses or validation scripts as TLA+ state/actions. Those 62 rows are `unrepresented` with **no disposition available**: `model it` is forbidden by `:26`, `change the program` is absurd, and `inventory it` requires a quoted plan line that does not exist. This is a direct contradiction inside the plan. |
| **ESC-4** | `specs/desired_program_model/spec_manifest.yaml` (and its `current`/`program_model` twins) | **Every effect port in this system lives in that file**, and no `implementation_scope` entry names it. Sweep 2's entire verdict vocabulary (`declared` / `undeclared` / `partial`) is anchored on a file the scope does not classify. Gaps G-1, G-5 and G-6 are therefore filed against the in-scope model file `specs/current/TlaSpecDevCli.tla` (`:285`), which is the closest the plan allows. |
| **ESC-5** | `specs/.history/**` — 5,402 files in this surface | Named by no plan line. Excluded by stated filter F1 (§8.2) as sealed append-only history rather than live program surface. **Not walked.** Several tickets' `evidence` lists point into it (`:399-414`, `:515-529`, `:622-635`, `:726-731`, `:800-813`, `:984-997`, `:1100-1107`, `:1233-1241`), but an `evidence` path is not a scope declaration. |
| **ESC-6** | `skill-scripts/install-tlc2.sh:37` | `curl -fL --retry 3 --retry-delay 1 "$JAR_URL" -o "$JAR_TMP"` is a **real outbound network download** on the install path the model represents as `BuildSkillCli` / `InstallLocalCli`. **No `network.connect` or `network.http` port is declared anywhere in `spec_manifest.yaml`** — the nine declared ports are all `filesystem.*` or `process.spawn`. The file is named by no plan line, so this cannot be filed as an in-scope gap; the manifest's own `mutation_write` target comment (`spec_manifest.yaml:172-178`) nonetheless names `skill-scripts/install-tla-spec-dev.sh` as catalog surface, so the model does know the directory exists. |
| **ESC-7** | `spec_double_compiler/**` (3 rows), `scripts/run_generated_case_adapters.py`, `templates/python/ports.py.j2` | The predecessor plan's amended `known_gaps` ruled exactly this set out-of-model as "SHIPPED validation harness and toolchain plumbing" (`PS:102`). The current plan carries nothing equivalent, so all four are `ESCALATION` under the closure rule — including `templates/python/` which is *in* scope by `:496` and was *out* of model by `PS:102`, a straight contradiction between the two documents. |

---

## 1. Model representation index

Enumerated by `grep -nE '^[A-Za-z_][A-Za-z0-9_]*(\(.*\))? ==' specs/desired_program_model/*.tla`
(37 top-level definitions; raw at `index-actions-desired.txt`), cross-checked
against the `Next` disjunction at `TlaSpecDevCli.tla:667-696`, and against
`grep -n 'ports\|effects\|channel' specs/desired_program_model/spec_manifest.yaml`
(18 lines; raw at `index-ports-desired.txt`).

**Index sanity check:** 16 actions for a CLI with 15 leaf/group subcommands and
10 modeled variables — plausible, non-empty, and consistent with the plan's own
recorded figures (`ticket_plan.yaml:643-644`: "variables 10, actions 16").

| Kind | Name | `file:line` |
|---|---|---|
| Variable | `setup_phase`, `spec_root`, `ticket_state`, `lastCommand`, `result`, `complexity_gate`, `corpus_gate`, `effect_conformance`, `kill_test`, `architecture_scan` | `TlaSpecDevCli.tla:162-172` (10) |
| Action | `BuildSkillCli` | `TlaSpecDevCli.tla:228` |
| Action | `InstallLocalCli` | `TlaSpecDevCli.tla:245` |
| Action | `ScaffoldProject(root)` | `TlaSpecDevCli.tla:263` |
| Action | `RecordBudgets(root)` | `TlaSpecDevCli.tla:286` |
| Action | `ScaffoldWorkflow(root)` | `TlaSpecDevCli.tla:305` |
| Action | `OpenTicket(root, ticket)` | `TlaSpecDevCli.tla:324` |
| Action | `UpdateTicketDesired(ticket)` | `TlaSpecDevCli.tla:348` |
| Action | `UpdateTicketCurrent(ticket)` | `TlaSpecDevCli.tla:366` |
| Action | `AnalyzeComplexity(root)` | `TlaSpecDevCli.tla:393` |
| Action | `AnalyzeCorpus(root)` | `TlaSpecDevCli.tla:427` |
| Action | `RunEffectConformance(root)` | `TlaSpecDevCli.tla:466` |
| Action | `RunKillTest(root)` | `TlaSpecDevCli.tla:522` |
| Action | `RunSpecUnitTests(root, ticket)` | `TlaSpecDevCli.tla:561` |
| Action | `CloseTicket(root, ticket)` | `TlaSpecDevCli.tla:619` |
| Action | `AnalyzeArchitecture(root)` | `TlaSpecDevCli.tla:650` |
| Action | `Stutter` | `TlaSpecDevCli.tla:664` |
| Invariant | `TypeInvariant` … `KillTestVerdictRequiresBudgets` (12) | `TlaSpecDevCli.tla:698-843` |
| Port | `spec_tree` (`filesystem.write`, `**/specs/**`) | `spec_manifest.yaml:112-114` |
| Port | `evidence_report` (`filesystem.write`, `**/results/**`) | `spec_manifest.yaml:115-117` |
| Port | `cli_artifact` (`filesystem.write`, `**/.venv/**`) | `spec_manifest.yaml:118-120` |
| Port | `test_process` (`process.spawn`, `*pytest*`) | `spec_manifest.yaml:131-133` |
| Port | `runner_process` (`process.spawn`, `*run_generated_case_adapters*`) | `spec_manifest.yaml:142-144` |
| Port | `spec_tree_delete` (`filesystem.delete`, `**/specs/**`) | `spec_manifest.yaml:153-155` |
| Port | `git_metadata` (`process.spawn`, `git rev-parse*`) | `spec_manifest.yaml:161-163` |
| Port | `mutation_write` (`filesystem.write`, `*scripts/*`) | `spec_manifest.yaml:178-180` |
| Port | `corpus_process` (`process.spawn`, `*`) | `spec_manifest.yaml:189-191` |
| Action→port rows | 14 rows: `BuildSkillCli` … `CloseTicket` | `spec_manifest.yaml:193-239` |
| Action→port rows | **`AnalyzeArchitecture` — ABSENT** | — (**gap G-1**) |
| Binding | *none for this project* | `find . -name 'actions.yml' -o -name 'testgraph_bindings.yml' \| grep -v '^./examples/'` returned **0 rows** (raw: `index-bindings.txt`); all nine such files in the repository belong to `examples/**`. This project binds through `case_adapters.toml` (`spec_manifest.yaml:241`) with `case_codegen.generation_status: planned` (`spec_manifest.yaml:66`) — **no generated case package exists for this model, so no oracle has ever executed against it.** |

**Only the names above may appear in a Sweep-1 "Spec action(s)" cell.** No
mapping was invented; a module whose behavior "would naturally fall under" an
action that does not name it is `partial` at best, with the uncovered part named.

---

## 2. Sweep 1 — Program surface

**Enumeration (recorded, reproducible):**

```bash
git ls-files '*.py' '*.sh' '*.kt' '*.kts' '*.java' '*.j2' | sort            # 5,998
git ls-files '*.py' '*.sh' '*.kt' '*.kts' '*.java' '*.j2' \
  | grep -v '^specs/\.history/' | sort > sweep1-surface.txt                 # 596
wc -l < sweep1-surface.txt
```

Per language, post-filter: `.py` 460, `.kt` 63, `.java` 36, `.kts` 17, `.j2` 12,
`.sh` 8.

**Filters, each checked against the declared scope before applying (Step 2's rule):**

- **F1 — exclude `specs/.history/**` (5,402 files).** Sealed append-only history
  snapshots, not live program surface. **Checked:** no `implementation_scope`
  entry names it. Recorded as **ESC-5** and as un-walked surface in §8.2. This
  filter is the single largest reason the verdict is `incomplete` rather than
  `fail`.
- **F2 — no other filter.** In particular `tests/` and `examples/**` were **not**
  excluded, because plan lines `:210`, `:287`, `:707-710`, `:784`, `:1213`,
  `:1272`, `:1364` name them. Step 2's warning that "a filter is a scope
  decision wearing a shell flag" was the reason.

**N = 596; M = 596; `N == M` ✅** (asserted by `cac_ac_classify.py`, which
writes one row per line of `sweep1-surface.txt` and prints the reconciliation).

Verdict distribution: `represented` **2**, `partial` **5**, `unrepresented` **589**.
Default polarity is `unrepresented`; the 7 non-default rows are the only ones
granted coverage on cited positive evidence, and all 7 are in `scripts/`.

The full 596-row table follows. Column 3 is `in-scope` or `ESCALATION`
(never `out-of-scope` — no plan line excludes anything). **`CP:N` in the "Plan
line" column means `specs/desired_program_model/ticket_plan.yaml` line `N`** at
commit `3467051`; those citations are emitted by `cac_ac_classify.py::SCOPE_DIRS`
and `::SCOPE_FILES`, which transcribe §0.3 verbatim.

| # | Module (`path`) | In/Out of scope | Plan line | Spec action(s) representing it | Verdict | Evidence (`file:line`) |
|---|---|---|---|---|---|---|
| 1 | `examples/distributed_history/ecommerce_backend/__init__.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 2 | `examples/distributed_history/ecommerce_backend/domain.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 3 | `examples/distributed_history/ecommerce_backend/service.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 4 | `examples/distributed_history/scripts/k3d-up.sh` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 5 | `examples/distributed_history/scripts/k8s-deploy.sh` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 6 | `examples/distributed_history/scripts/regenerate_tlc_cases.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 7 | `examples/distributed_history/specs/__init__.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 8 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/__init__.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 9 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/cases.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 10 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/types.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 11 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/validators.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 12 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/__init__.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 13 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/cases.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 14 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/types.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 15 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/validators.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 16 | `examples/distributed_history/specs/program_model/__init__.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 17 | `examples/distributed_history/specs/program_model/adapters.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 18 | `examples/distributed_history/specs/program_model/tests/test_ecommerce_adapters.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 19 | `examples/distributed_history/specs/program_model/tlc_projection.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 20 | `examples/distributed_history/test_graph/build-logic/build.gradle.kts` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 21 | `examples/distributed_history/test_graph/build-logic/settings.gradle.kts` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 22 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Context.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 23 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Executors.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 24 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/JBangExecutor.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 25 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/PlanExecutor.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 26 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/TimeoutParser.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 27 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/UvExecutor.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 28 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphAssembler.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 29 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphModel.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 30 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/MiniJson.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 31 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/NodeDescribeLoader.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 32 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/InspectionTasks.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 33 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunReportWriter.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 34 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunTestGraphTask.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 35 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/ValidationReportTask.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 36 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/TestGraphSpec.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 37 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/Toolchain.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 38 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphExtension.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 39 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphPlugin.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 40 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationNodeSpec.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 41 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationRuntime.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 42 | `examples/distributed_history/test_graph/build-logic/src/test/kotlin/com/hayden/testgraphsdk/exec/PlanExecutorResumeHarnessTest.kt` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 43 | `examples/distributed_history/test_graph/build.gradle.kts` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 44 | `examples/distributed_history/test_graph/sdk/java/build.gradle.kts` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 45 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextItem.java` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 46 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextSerde.java` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 47 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Json.java` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 48 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/JsonMapper.java` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 49 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Node.java` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 50 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeBody.java` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 51 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeContext.java` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 52 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeResult.java` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 53 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeSpec.java` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 54 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeStatus.java` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 55 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ProcessRecord.java` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 56 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Procs.java` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 57 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/__init__.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 58 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/context_item.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 59 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/context.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 60 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/node_spec.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 61 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/procs.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 62 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/result.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 63 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/runner.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 64 | `examples/distributed_history/test_graph/settings.gradle.kts` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 65 | `examples/distributed_history/test_graph/sources/cleanup_ecommerce.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 66 | `examples/distributed_history/test_graph/sources/collect_evidence.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 67 | `examples/distributed_history/test_graph/sources/deploy_ecommerce.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 68 | `examples/distributed_history/test_graph/sources/run_external_cases.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 69 | `examples/distributed_history/tests/test_ecommerce_backend.py` | in-scope | CP:709 (EV-01) | none | `unrepresented` | - |
| 70 | `examples/effect_providers/atomic_publisher/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 71 | `examples/effect_providers/atomic_publisher/adapters.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 72 | `examples/effect_providers/atomic_publisher/application.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 73 | `examples/effect_providers/atomic_publisher/atomic_cli.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 74 | `examples/effect_providers/atomic_publisher/conformance.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 75 | `examples/effect_providers/atomic_publisher/external_adapter.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 76 | `examples/effect_providers/atomic_publisher/providers.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 77 | `examples/effect_providers/atomic_publisher/regenerate.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 78 | `examples/effect_providers/atomic_publisher/run_experiment.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 79 | `examples/effect_providers/atomic_publisher/specs/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 80 | `examples/effect_providers/atomic_publisher/specs/program_model/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 81 | `examples/effect_providers/atomic_publisher/specs/program_model/generated/atomic_publisher_contract/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 82 | `examples/effect_providers/atomic_publisher/specs/program_model/generated/atomic_publisher_contract/contract_tests.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 83 | `examples/effect_providers/atomic_publisher/specs/program_model/generated/atomic_publisher_contract/fake.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 84 | `examples/effect_providers/atomic_publisher/specs/program_model/generated/atomic_publisher_contract/ports.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 85 | `examples/effect_providers/atomic_publisher/specs/program_model/generated/atomic_publisher_contract/strategies.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 86 | `examples/effect_providers/atomic_publisher/specs/program_model/generated/atomic_publisher_contract/traces.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 87 | `examples/effect_providers/atomic_publisher/specs/program_model/generated/atomic_publisher_contract/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 88 | `examples/effect_providers/atomic_publisher/specs/program_model/generated/atomic_publisher_contract/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 89 | `examples/effect_providers/atomic_publisher/specs/program_model/generated/cases/spec-unit/atomic_internal_cases/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 90 | `examples/effect_providers/atomic_publisher/specs/program_model/generated/cases/spec-unit/atomic_internal_cases/cases.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 91 | `examples/effect_providers/atomic_publisher/specs/program_model/generated/cases/spec-unit/atomic_internal_cases/doubles.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 92 | `examples/effect_providers/atomic_publisher/specs/program_model/generated/cases/spec-unit/atomic_internal_cases/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 93 | `examples/effect_providers/atomic_publisher/specs/program_model/generated/cases/spec-unit/atomic_internal_cases/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 94 | `examples/effect_providers/atomic_publisher/specs/program_model/generated/cases/testgraph/atomic_external_cases/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 95 | `examples/effect_providers/atomic_publisher/specs/program_model/generated/cases/testgraph/atomic_external_cases/cases.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 96 | `examples/effect_providers/atomic_publisher/specs/program_model/generated/cases/testgraph/atomic_external_cases/doubles.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 97 | `examples/effect_providers/atomic_publisher/specs/program_model/generated/cases/testgraph/atomic_external_cases/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 98 | `examples/effect_providers/atomic_publisher/specs/program_model/generated/cases/testgraph/atomic_external_cases/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 99 | `examples/effect_providers/atomic_publisher/specs/program_model/tlc_projection.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 100 | `examples/effect_providers/atomic_publisher/test_atomic_publisher.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 101 | `examples/effect_providers/atomic_publisher/validate.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 102 | `examples/effect_providers/legacy_payment_http/generated/spec-unit/payment_http_internal_cases/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 103 | `examples/effect_providers/legacy_payment_http/generated/spec-unit/payment_http_internal_cases/cases.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 104 | `examples/effect_providers/legacy_payment_http/generated/spec-unit/payment_http_internal_cases/doubles.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 105 | `examples/effect_providers/legacy_payment_http/generated/spec-unit/payment_http_internal_cases/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 106 | `examples/effect_providers/legacy_payment_http/generated/spec-unit/payment_http_internal_cases/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 107 | `examples/effect_providers/legacy_payment_http/generated/testgraph/payment_http_external_cases/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 108 | `examples/effect_providers/legacy_payment_http/generated/testgraph/payment_http_external_cases/cases.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 109 | `examples/effect_providers/legacy_payment_http/generated/testgraph/payment_http_external_cases/doubles.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 110 | `examples/effect_providers/legacy_payment_http/generated/testgraph/payment_http_external_cases/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 111 | `examples/effect_providers/legacy_payment_http/generated/testgraph/payment_http_external_cases/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 112 | `examples/effect_providers/legacy_payment_http/legacy_payment_http_app/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 113 | `examples/effect_providers/legacy_payment_http/legacy_payment_http_app/__main__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 114 | `examples/effect_providers/legacy_payment_http/legacy_payment_http_app/application.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 115 | `examples/effect_providers/legacy_payment_http/payment_effects/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 116 | `examples/effect_providers/legacy_payment_http/payment_effects/adapters.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 117 | `examples/effect_providers/legacy_payment_http/payment_effects/baseline.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 118 | `examples/effect_providers/legacy_payment_http/payment_effects/external.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 119 | `examples/effect_providers/legacy_payment_http/payment_effects/probes.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 120 | `examples/effect_providers/legacy_payment_http/payment_effects/provider.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 121 | `examples/effect_providers/legacy_payment_http/scripts/regenerate.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 122 | `examples/effect_providers/legacy_payment_http/scripts/run_experiment.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 123 | `examples/effect_providers/legacy_payment_http/scripts/write_cost_evidence.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 124 | `examples/effect_providers/legacy_payment_http/specs/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 125 | `examples/effect_providers/legacy_payment_http/specs/program_model/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 126 | `examples/effect_providers/legacy_payment_http/specs/program_model/generated/payment_http_contract/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 127 | `examples/effect_providers/legacy_payment_http/specs/program_model/generated/payment_http_contract/contract_tests.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 128 | `examples/effect_providers/legacy_payment_http/specs/program_model/generated/payment_http_contract/fake.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 129 | `examples/effect_providers/legacy_payment_http/specs/program_model/generated/payment_http_contract/ports.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 130 | `examples/effect_providers/legacy_payment_http/specs/program_model/generated/payment_http_contract/strategies.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 131 | `examples/effect_providers/legacy_payment_http/specs/program_model/generated/payment_http_contract/traces.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 132 | `examples/effect_providers/legacy_payment_http/specs/program_model/generated/payment_http_contract/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 133 | `examples/effect_providers/legacy_payment_http/specs/program_model/generated/payment_http_contract/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 134 | `examples/effect_providers/legacy_payment_http/specs/program_model/tlc_projection.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 135 | `examples/effect_providers/legacy_payment_http/tests/test_project.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 136 | `examples/effect_providers/legacy_payment_http/validate.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 137 | `examples/effect_providers/reminder_worker/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 138 | `examples/effect_providers/reminder_worker/adapter.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 139 | `examples/effect_providers/reminder_worker/app.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 140 | `examples/effect_providers/reminder_worker/evidence/validation-runs/20260723T164419.199183Z-0a3080d79ed6-reminder_worker/generated/cases/spec-unit/reminder_internal_cases/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 141 | `examples/effect_providers/reminder_worker/evidence/validation-runs/20260723T164419.199183Z-0a3080d79ed6-reminder_worker/generated/cases/spec-unit/reminder_internal_cases/cases.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 142 | `examples/effect_providers/reminder_worker/evidence/validation-runs/20260723T164419.199183Z-0a3080d79ed6-reminder_worker/generated/cases/spec-unit/reminder_internal_cases/doubles.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 143 | `examples/effect_providers/reminder_worker/evidence/validation-runs/20260723T164419.199183Z-0a3080d79ed6-reminder_worker/generated/cases/spec-unit/reminder_internal_cases/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 144 | `examples/effect_providers/reminder_worker/evidence/validation-runs/20260723T164419.199183Z-0a3080d79ed6-reminder_worker/generated/cases/spec-unit/reminder_internal_cases/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 145 | `examples/effect_providers/reminder_worker/evidence/validation-runs/20260723T164419.199183Z-0a3080d79ed6-reminder_worker/generated/cases/testgraph/reminder_external_cases/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 146 | `examples/effect_providers/reminder_worker/evidence/validation-runs/20260723T164419.199183Z-0a3080d79ed6-reminder_worker/generated/cases/testgraph/reminder_external_cases/cases.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 147 | `examples/effect_providers/reminder_worker/evidence/validation-runs/20260723T164419.199183Z-0a3080d79ed6-reminder_worker/generated/cases/testgraph/reminder_external_cases/doubles.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 148 | `examples/effect_providers/reminder_worker/evidence/validation-runs/20260723T164419.199183Z-0a3080d79ed6-reminder_worker/generated/cases/testgraph/reminder_external_cases/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 149 | `examples/effect_providers/reminder_worker/evidence/validation-runs/20260723T164419.199183Z-0a3080d79ed6-reminder_worker/generated/cases/testgraph/reminder_external_cases/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 150 | `examples/effect_providers/reminder_worker/evidence/validation-runs/20260723T164419.199183Z-0a3080d79ed6-reminder_worker/generated/reminder_contract/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 151 | `examples/effect_providers/reminder_worker/evidence/validation-runs/20260723T164419.199183Z-0a3080d79ed6-reminder_worker/generated/reminder_contract/contract_tests.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 152 | `examples/effect_providers/reminder_worker/evidence/validation-runs/20260723T164419.199183Z-0a3080d79ed6-reminder_worker/generated/reminder_contract/fake.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 153 | `examples/effect_providers/reminder_worker/evidence/validation-runs/20260723T164419.199183Z-0a3080d79ed6-reminder_worker/generated/reminder_contract/ports.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 154 | `examples/effect_providers/reminder_worker/evidence/validation-runs/20260723T164419.199183Z-0a3080d79ed6-reminder_worker/generated/reminder_contract/strategies.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 155 | `examples/effect_providers/reminder_worker/evidence/validation-runs/20260723T164419.199183Z-0a3080d79ed6-reminder_worker/generated/reminder_contract/traces.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 156 | `examples/effect_providers/reminder_worker/evidence/validation-runs/20260723T164419.199183Z-0a3080d79ed6-reminder_worker/generated/reminder_contract/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 157 | `examples/effect_providers/reminder_worker/evidence/validation-runs/20260723T164419.199183Z-0a3080d79ed6-reminder_worker/generated/reminder_contract/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 158 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v1/generated/cases/spec-unit/reminder_internal_cases/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 159 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v1/generated/cases/spec-unit/reminder_internal_cases/cases.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 160 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v1/generated/cases/spec-unit/reminder_internal_cases/doubles.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 161 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v1/generated/cases/spec-unit/reminder_internal_cases/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 162 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v1/generated/cases/spec-unit/reminder_internal_cases/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 163 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v1/generated/cases/testgraph/reminder_external_cases/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 164 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v1/generated/cases/testgraph/reminder_external_cases/cases.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 165 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v1/generated/cases/testgraph/reminder_external_cases/doubles.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 166 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v1/generated/cases/testgraph/reminder_external_cases/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 167 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v1/generated/cases/testgraph/reminder_external_cases/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 168 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v1/generated/reminder_contract/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 169 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v1/generated/reminder_contract/contract_tests.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 170 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v1/generated/reminder_contract/fake.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 171 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v1/generated/reminder_contract/ports.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 172 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v1/generated/reminder_contract/strategies.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 173 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v1/generated/reminder_contract/traces.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 174 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v1/generated/reminder_contract/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 175 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v1/generated/reminder_contract/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 176 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v2/generated/cases/spec-unit/reminder_internal_cases/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 177 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v2/generated/cases/spec-unit/reminder_internal_cases/cases.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 178 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v2/generated/cases/spec-unit/reminder_internal_cases/doubles.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 179 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v2/generated/cases/spec-unit/reminder_internal_cases/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 180 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v2/generated/cases/spec-unit/reminder_internal_cases/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 181 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v2/generated/cases/testgraph/reminder_external_cases/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 182 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v2/generated/cases/testgraph/reminder_external_cases/cases.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 183 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v2/generated/cases/testgraph/reminder_external_cases/doubles.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 184 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v2/generated/cases/testgraph/reminder_external_cases/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 185 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v2/generated/cases/testgraph/reminder_external_cases/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 186 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v2/generated/reminder_contract/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 187 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v2/generated/reminder_contract/contract_tests.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 188 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v2/generated/reminder_contract/fake.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 189 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v2/generated/reminder_contract/ports.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 190 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v2/generated/reminder_contract/strategies.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 191 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v2/generated/reminder_contract/traces.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 192 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v2/generated/reminder_contract/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 193 | `examples/effect_providers/reminder_worker/evidence/validation-runs/agent-ep06-reminder-v2/generated/reminder_contract/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 194 | `examples/effect_providers/reminder_worker/evidence/validation-runs/ep06-central-20260722-v2-reminder_worker/generated/cases/spec-unit/reminder_internal_cases/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 195 | `examples/effect_providers/reminder_worker/evidence/validation-runs/ep06-central-20260722-v2-reminder_worker/generated/cases/spec-unit/reminder_internal_cases/cases.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 196 | `examples/effect_providers/reminder_worker/evidence/validation-runs/ep06-central-20260722-v2-reminder_worker/generated/cases/spec-unit/reminder_internal_cases/doubles.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 197 | `examples/effect_providers/reminder_worker/evidence/validation-runs/ep06-central-20260722-v2-reminder_worker/generated/cases/spec-unit/reminder_internal_cases/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 198 | `examples/effect_providers/reminder_worker/evidence/validation-runs/ep06-central-20260722-v2-reminder_worker/generated/cases/spec-unit/reminder_internal_cases/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 199 | `examples/effect_providers/reminder_worker/evidence/validation-runs/ep06-central-20260722-v2-reminder_worker/generated/cases/testgraph/reminder_external_cases/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 200 | `examples/effect_providers/reminder_worker/evidence/validation-runs/ep06-central-20260722-v2-reminder_worker/generated/cases/testgraph/reminder_external_cases/cases.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 201 | `examples/effect_providers/reminder_worker/evidence/validation-runs/ep06-central-20260722-v2-reminder_worker/generated/cases/testgraph/reminder_external_cases/doubles.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 202 | `examples/effect_providers/reminder_worker/evidence/validation-runs/ep06-central-20260722-v2-reminder_worker/generated/cases/testgraph/reminder_external_cases/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 203 | `examples/effect_providers/reminder_worker/evidence/validation-runs/ep06-central-20260722-v2-reminder_worker/generated/cases/testgraph/reminder_external_cases/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 204 | `examples/effect_providers/reminder_worker/evidence/validation-runs/ep06-central-20260722-v2-reminder_worker/generated/reminder_contract/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 205 | `examples/effect_providers/reminder_worker/evidence/validation-runs/ep06-central-20260722-v2-reminder_worker/generated/reminder_contract/contract_tests.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 206 | `examples/effect_providers/reminder_worker/evidence/validation-runs/ep06-central-20260722-v2-reminder_worker/generated/reminder_contract/fake.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 207 | `examples/effect_providers/reminder_worker/evidence/validation-runs/ep06-central-20260722-v2-reminder_worker/generated/reminder_contract/ports.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 208 | `examples/effect_providers/reminder_worker/evidence/validation-runs/ep06-central-20260722-v2-reminder_worker/generated/reminder_contract/strategies.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 209 | `examples/effect_providers/reminder_worker/evidence/validation-runs/ep06-central-20260722-v2-reminder_worker/generated/reminder_contract/traces.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 210 | `examples/effect_providers/reminder_worker/evidence/validation-runs/ep06-central-20260722-v2-reminder_worker/generated/reminder_contract/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 211 | `examples/effect_providers/reminder_worker/evidence/validation-runs/ep06-central-20260722-v2-reminder_worker/generated/reminder_contract/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 212 | `examples/effect_providers/reminder_worker/evidence/validation-runs/testgraph-1784764040160583000-reminder_worker/generated/cases/spec-unit/reminder_internal_cases/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 213 | `examples/effect_providers/reminder_worker/evidence/validation-runs/testgraph-1784764040160583000-reminder_worker/generated/cases/spec-unit/reminder_internal_cases/cases.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 214 | `examples/effect_providers/reminder_worker/evidence/validation-runs/testgraph-1784764040160583000-reminder_worker/generated/cases/spec-unit/reminder_internal_cases/doubles.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 215 | `examples/effect_providers/reminder_worker/evidence/validation-runs/testgraph-1784764040160583000-reminder_worker/generated/cases/spec-unit/reminder_internal_cases/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 216 | `examples/effect_providers/reminder_worker/evidence/validation-runs/testgraph-1784764040160583000-reminder_worker/generated/cases/spec-unit/reminder_internal_cases/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 217 | `examples/effect_providers/reminder_worker/evidence/validation-runs/testgraph-1784764040160583000-reminder_worker/generated/cases/testgraph/reminder_external_cases/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 218 | `examples/effect_providers/reminder_worker/evidence/validation-runs/testgraph-1784764040160583000-reminder_worker/generated/cases/testgraph/reminder_external_cases/cases.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 219 | `examples/effect_providers/reminder_worker/evidence/validation-runs/testgraph-1784764040160583000-reminder_worker/generated/cases/testgraph/reminder_external_cases/doubles.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 220 | `examples/effect_providers/reminder_worker/evidence/validation-runs/testgraph-1784764040160583000-reminder_worker/generated/cases/testgraph/reminder_external_cases/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 221 | `examples/effect_providers/reminder_worker/evidence/validation-runs/testgraph-1784764040160583000-reminder_worker/generated/cases/testgraph/reminder_external_cases/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 222 | `examples/effect_providers/reminder_worker/evidence/validation-runs/testgraph-1784764040160583000-reminder_worker/generated/reminder_contract/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 223 | `examples/effect_providers/reminder_worker/evidence/validation-runs/testgraph-1784764040160583000-reminder_worker/generated/reminder_contract/contract_tests.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 224 | `examples/effect_providers/reminder_worker/evidence/validation-runs/testgraph-1784764040160583000-reminder_worker/generated/reminder_contract/fake.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 225 | `examples/effect_providers/reminder_worker/evidence/validation-runs/testgraph-1784764040160583000-reminder_worker/generated/reminder_contract/ports.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 226 | `examples/effect_providers/reminder_worker/evidence/validation-runs/testgraph-1784764040160583000-reminder_worker/generated/reminder_contract/strategies.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 227 | `examples/effect_providers/reminder_worker/evidence/validation-runs/testgraph-1784764040160583000-reminder_worker/generated/reminder_contract/traces.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 228 | `examples/effect_providers/reminder_worker/evidence/validation-runs/testgraph-1784764040160583000-reminder_worker/generated/reminder_contract/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 229 | `examples/effect_providers/reminder_worker/evidence/validation-runs/testgraph-1784764040160583000-reminder_worker/generated/reminder_contract/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 230 | `examples/effect_providers/reminder_worker/external_adapter.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 231 | `examples/effect_providers/reminder_worker/generated/cases/spec-unit/reminder_internal_cases/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 232 | `examples/effect_providers/reminder_worker/generated/cases/spec-unit/reminder_internal_cases/cases.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 233 | `examples/effect_providers/reminder_worker/generated/cases/spec-unit/reminder_internal_cases/doubles.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 234 | `examples/effect_providers/reminder_worker/generated/cases/spec-unit/reminder_internal_cases/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 235 | `examples/effect_providers/reminder_worker/generated/cases/spec-unit/reminder_internal_cases/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 236 | `examples/effect_providers/reminder_worker/generated/cases/testgraph/reminder_external_cases/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 237 | `examples/effect_providers/reminder_worker/generated/cases/testgraph/reminder_external_cases/cases.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 238 | `examples/effect_providers/reminder_worker/generated/cases/testgraph/reminder_external_cases/doubles.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 239 | `examples/effect_providers/reminder_worker/generated/cases/testgraph/reminder_external_cases/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 240 | `examples/effect_providers/reminder_worker/generated/cases/testgraph/reminder_external_cases/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 241 | `examples/effect_providers/reminder_worker/generated/reminder_contract/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 242 | `examples/effect_providers/reminder_worker/generated/reminder_contract/contract_tests.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 243 | `examples/effect_providers/reminder_worker/generated/reminder_contract/fake.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 244 | `examples/effect_providers/reminder_worker/generated/reminder_contract/ports.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 245 | `examples/effect_providers/reminder_worker/generated/reminder_contract/strategies.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 246 | `examples/effect_providers/reminder_worker/generated/reminder_contract/traces.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 247 | `examples/effect_providers/reminder_worker/generated/reminder_contract/types.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 248 | `examples/effect_providers/reminder_worker/generated/reminder_contract/validators.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 249 | `examples/effect_providers/reminder_worker/providers.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 250 | `examples/effect_providers/reminder_worker/regenerate.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 251 | `examples/effect_providers/reminder_worker/reminder_cli.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 252 | `examples/effect_providers/reminder_worker/run_experiment.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 253 | `examples/effect_providers/reminder_worker/specs/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 254 | `examples/effect_providers/reminder_worker/specs/program_model/__init__.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 255 | `examples/effect_providers/reminder_worker/specs/program_model/tlc_projection.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 256 | `examples/effect_providers/reminder_worker/test_reminder_worker.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 257 | `examples/effect_providers/reminder_worker/validate.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 258 | `examples/effect_providers/run_validations.py` | in-scope | CP:710 (EV-01) | none | `unrepresented` | - |
| 259 | `examples/run_distributed_history_validation.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 260 | `examples/validate_split_desired_workflow.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 261 | `examples/validation/check_twins.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 262 | `examples/validation/ex1_scaffold_only/taskq/taskq.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 263 | `examples/validation/ex1_scaffold_only/taskq/tests/test_taskq.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 264 | `examples/validation/ex3_over_complex/order_hub/order_hub.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 265 | `examples/validation/ex3_over_complex/order_hub/tests/test_order_hub.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 266 | `examples/validation/ex4_pipeline_coherent/generated/pipeline_contract/__init__.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 267 | `examples/validation/ex4_pipeline_coherent/generated/pipeline_contract/contract_tests.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 268 | `examples/validation/ex4_pipeline_coherent/generated/pipeline_contract/fake.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 269 | `examples/validation/ex4_pipeline_coherent/generated/pipeline_contract/ports.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 270 | `examples/validation/ex4_pipeline_coherent/generated/pipeline_contract/strategies.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 271 | `examples/validation/ex4_pipeline_coherent/generated/pipeline_contract/traces.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 272 | `examples/validation/ex4_pipeline_coherent/generated/pipeline_contract/types.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 273 | `examples/validation/ex4_pipeline_coherent/generated/pipeline_contract/validators.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 274 | `examples/validation/ex4_pipeline_coherent/pipeline/dispatch/__init__.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 275 | `examples/validation/ex4_pipeline_coherent/pipeline/dispatch/delivery.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 276 | `examples/validation/ex4_pipeline_coherent/pipeline/dispatch/failures.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 277 | `examples/validation/ex4_pipeline_coherent/pipeline/ingest/__init__.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 278 | `examples/validation/ex4_pipeline_coherent/pipeline/ingest/inbox.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 279 | `examples/validation/ex4_pipeline_coherent/pipeline/ingest/queue.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 280 | `examples/validation/ex4_pipeline_coherent/pipeline/ledger/__init__.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 281 | `examples/validation/ex4_pipeline_coherent/pipeline/ledger/journal.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 282 | `examples/validation/ex4_pipeline_coherent/specs/__init__.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 283 | `examples/validation/ex4_pipeline_coherent/specs/program_model/__init__.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 284 | `examples/validation/ex4_pipeline_coherent/specs/program_model/adapters.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 285 | `examples/validation/ex4_pipeline_coherent/specs/program_model/providers.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 286 | `examples/validation/ex4_pipeline_coherent/specs/program_model/tlc_projection.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 287 | `examples/validation/ex4_pipeline_coherent/tests/driver.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 288 | `examples/validation/ex4_pipeline_coherent/tests/test_behavior.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 289 | `examples/validation/ex5_pipeline_divergent/generated/pipeline_contract/__init__.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 290 | `examples/validation/ex5_pipeline_divergent/generated/pipeline_contract/contract_tests.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 291 | `examples/validation/ex5_pipeline_divergent/generated/pipeline_contract/fake.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 292 | `examples/validation/ex5_pipeline_divergent/generated/pipeline_contract/ports.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 293 | `examples/validation/ex5_pipeline_divergent/generated/pipeline_contract/strategies.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 294 | `examples/validation/ex5_pipeline_divergent/generated/pipeline_contract/traces.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 295 | `examples/validation/ex5_pipeline_divergent/generated/pipeline_contract/types.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 296 | `examples/validation/ex5_pipeline_divergent/generated/pipeline_contract/validators.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 297 | `examples/validation/ex5_pipeline_divergent/pipeline/dispatch/__init__.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 298 | `examples/validation/ex5_pipeline_divergent/pipeline/dispatch/delivery.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 299 | `examples/validation/ex5_pipeline_divergent/pipeline/dispatch/failures.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 300 | `examples/validation/ex5_pipeline_divergent/pipeline/ingest/__init__.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 301 | `examples/validation/ex5_pipeline_divergent/pipeline/ingest/inbox.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 302 | `examples/validation/ex5_pipeline_divergent/pipeline/ingest/queue.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 303 | `examples/validation/ex5_pipeline_divergent/pipeline/ledger/__init__.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 304 | `examples/validation/ex5_pipeline_divergent/pipeline/ledger/journal.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 305 | `examples/validation/ex5_pipeline_divergent/tests/driver.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 306 | `examples/validation/ex5_pipeline_divergent/tests/test_behavior.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 307 | `examples/validation/ex6_jenga/hub/billing/__init__.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 308 | `examples/validation/ex6_jenga/hub/billing/audit.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 309 | `examples/validation/ex6_jenga/hub/notify/__init__.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 310 | `examples/validation/ex6_jenga/hub/notify/flags.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 311 | `examples/validation/ex6_jenga/hub/orders/__init__.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 312 | `examples/validation/ex6_jenga/hub/orders/lifecycle.py` | in-scope | CP:707 (EV-01), CP:1364 (EV-03) | none | `unrepresented` | - |
| 313 | `examples/validation/runs/ex1-run4/artifacts/providers.py` | in-scope | CP:784 (EV-02) | none | `unrepresented` | - |
| 314 | `examples/validation/runs/ex2-run4/artifacts/providers.py` | in-scope | CP:784 (EV-02) | none | `unrepresented` | - |
| 315 | `examples/validation/runs/ex3-run1/artifacts/order_hub_after.py` | in-scope | CP:784 (EV-02) | none | `unrepresented` | - |
| 316 | `examples/validation/runs/ex3-run4/artifacts/providers.py` | in-scope | CP:784 (EV-02) | none | `unrepresented` | - |
| 317 | `examples/validation/runs/ex4-run1/artifacts/df02_blast.py` | in-scope | CP:784 (EV-02) | none | `unrepresented` | - |
| 318 | `examples/validation/runs/ex4-run1/artifacts/kill_matrix.py` | in-scope | CP:784 (EV-02) | none | `unrepresented` | - |
| 319 | `examples/validation/runs/ex4-run1/artifacts/replay.py` | in-scope | CP:784 (EV-02) | none | `unrepresented` | - |
| 320 | `examples/validation/runs/ex4-run4/artifacts/case_modules_worked_example.sh` | in-scope | CP:784 (EV-02) | none | `unrepresented` | - |
| 321 | `examples/validation/runs/ex4-run4/artifacts/kill_matrix_round2.py` | in-scope | CP:784 (EV-02) | none | `unrepresented` | - |
| 322 | `examples/validation/runs/ex4-run5/artifacts/replay.py` | in-scope | CP:784 (EV-02) | none | `unrepresented` | - |
| 323 | `examples/validation/runs/ex4-run6/artifacts/mutant_run.py` | in-scope | CP:784 (EV-02) | none | `unrepresented` | - |
| 324 | `examples/validation/runs/ex4-run6/artifacts/sanitize_runB.py` | in-scope | CP:784 (EV-02) | none | `unrepresented` | - |
| 325 | `examples/validation/runs/ex5-run3/artifacts/df02_blast_round2.py` | in-scope | CP:784 (EV-02) | none | `unrepresented` | - |
| 326 | `examples/validation/runs/ex5-run4/artifacts/reexport_attack/shared.py` | in-scope | CP:784 (EV-02) | none | `unrepresented` | - |
| 327 | `examples/validation/runs/ex5-run4/artifacts/sanitize_runA.py` | in-scope | CP:784 (EV-02) | none | `unrepresented` | - |
| 328 | `scripts/analyze_architecture.py` | in-scope | CP:283 (AC-01), CP:379 (AC-02), CP:872 (RP-01) | AnalyzeArchitecture | `partial` | specs/desired_program_model/TlaSpecDevCli.tla:650 (action) vs analyze_architecture.py:1010 run(); UNCOVERED: the --out descriptor write (:1116-1117) has no declared port and no manifest actions row |
| 329 | `scripts/analyze_complexity.py` | in-scope | CP:1077 (RP-04) | AnalyzeComplexity | `partial` | specs/desired_program_model/TlaSpecDevCli.tla:393 vs analyze_complexity.py:2293-2294; UNCOVERED: --out accepts an arbitrary path, the declared evidence_report port targets only **/results/** |
| 330 | `scripts/architecture_reflexion.py` | in-scope | CP:378 (AC-02), CP:607 (AC-04), CP:871 (RP-01) | AnalyzeArchitecture | `partial` | specs/desired_program_model/TlaSpecDevCli.tla:650 vs architecture_reflexion.py compare/--out :2290-2291; UNCOVERED: the --out reflexion write and the --baseline delta write have no declared port |
| 331 | `scripts/budgets.py` | in-scope | CP:209 (CM-01) | RecordBudgets | `represented` | specs/desired_program_model/TlaSpecDevCli.tla:286; budgets.py has zero effect sites, matching spec_manifest.yaml's deliberately EMPTY RecordBudgets row (spec_manifest.yaml:204) |
| 332 | `scripts/case_modules.py` | in-scope | CP:1209 (RP-03) | none | `unrepresented` | standalone main() (case_modules.py:832+); not reachable from tla_spec_dev.py's parser (grep: no case_modules entry in build_parser) |
| 333 | `scripts/close_spec_workflow.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 334 | `scripts/close_ticket.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 335 | `scripts/close_tickets.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 336 | `scripts/close-spec-workflow.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 337 | `scripts/close-ticket.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 338 | `scripts/complexity_ledger.py` | in-scope | CP:606 (AC-04), CP:1078 (RP-04) | CloseTicket, ScaffoldWorkflow | `partial` | specs/desired_program_model/TlaSpecDevCli.tla:619/:305 via spec_evolution.record_complexity_ledger and new_ticket_workflow.py:1006; UNCOVERED: no action represents the architecture_delta ledger member AC-04 added |
| 339 | `scripts/corpus_diagnostics.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 340 | `scripts/effect_conformance_report.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 341 | `scripts/effect_conformance.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 342 | `scripts/export_testgraph_cases.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 343 | `scripts/extract_spec_manifest.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 344 | `scripts/fitness_functions.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 345 | `scripts/generate_cases_from_tlc_dump.py` | in-scope | CP:208 (CM-01), CP:966 (RP-02), CP:1210 (RP-03), CP:150 (service_catalog) | none | `unrepresented` | no `generate` subcommand exists in tla_spec_dev.py:385-731; spawns java (:115), rmtree (:139), writes packages (:881-882) |
| 346 | `scripts/generate_docs.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 347 | `scripts/generate_python.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 348 | `scripts/infer_action_params.py` | in-scope | CP:965 (RP-02) | none | `unrepresented` | standalone; writes the recovery audit at :825-826, no CLI subcommand |
| 349 | `scripts/kill_test.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 350 | `scripts/new_ticket_workflow.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 351 | `scripts/onboard_program_model.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 352 | `scripts/run_generated_case_adapters.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 353 | `scripts/run_kill_test.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 354 | `scripts/run_tlc.sh` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 355 | `scripts/scaffold_spec_workflow.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 356 | `scripts/scaffold_spec.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 357 | `scripts/skill_feedback.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 358 | `scripts/spec_evolution.py` | in-scope | CP:207 (CM-01) | CloseTicket | `partial` | specs/desired_program_model/TlaSpecDevCli.tla:619 vs spec_evolution.py create_ticket_history_entry; UNCOVERED: record_complexity_ledger (:770) and the workflow-close path have no action |
| 359 | `scripts/spec_paths.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 360 | `scripts/start_ticket.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 361 | `scripts/testgraph_channels.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 362 | `scripts/tla_spec_dev.py` | in-scope | CP:284 (AC-01) | BuildSkillCli, InstallLocalCli, ScaffoldProject, ScaffoldWorkflow, OpenTicket, AnalyzeComplexity, AnalyzeCorpus, AnalyzeArchitecture, RunEffectConformance, RunKillTest, RunSpecUnitTests, CloseTicket | `represented` | specs/desired_program_model/TlaSpecDevCli.tla:228-663 vs dispatcher tla_spec_dev.py:385-731 |
| 363 | `skill-scripts/install-tla-spec-dev.sh` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 364 | `skill-scripts/install-tlc2.sh` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 365 | `spec_double_compiler/__init__.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 366 | `spec_double_compiler/effects.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 367 | `spec_double_compiler/runtime.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 368 | `specs/current/adapter_case_runtime.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 369 | `specs/current/production_adapters.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 370 | `specs/current/tests/test_current_ticket_workflow.py` | in-scope | CP:287 (AC-01) | none | `unrepresented` | - |
| 371 | `specs/current/tests/test_tla_spec_dev_analyze_adapter.py` | in-scope | CP:159 (service_catalog.adapter_boundaries) | none | `unrepresented` | - |
| 372 | `specs/current/tests/test_tla_spec_dev_binding_reconciliation.py` | in-scope | CP:287 (AC-01) | none | `unrepresented` | - |
| 373 | `specs/current/tests/test_tla_spec_dev_budgets_adapter.py` | in-scope | CP:287 (AC-01) | none | `unrepresented` | - |
| 374 | `specs/current/tests/test_tla_spec_dev_case_execution_run.py` | in-scope | CP:287 (AC-01) | none | `unrepresented` | - |
| 375 | `specs/current/tests/test_tla_spec_dev_cli_adapter.py` | in-scope | CP:287 (AC-01) | none | `unrepresented` | - |
| 376 | `specs/current/tests/test_tla_spec_dev_close_promotion_adapter.py` | in-scope | CP:287 (AC-01) | none | `unrepresented` | - |
| 377 | `specs/current/tests/test_tla_spec_dev_complexity_ledger_adapter.py` | in-scope | CP:287 (AC-01) | none | `unrepresented` | - |
| 378 | `specs/current/tests/test_tla_spec_dev_corpus_adapter.py` | in-scope | CP:287 (AC-01) | none | `unrepresented` | - |
| 379 | `specs/current/tests/test_tla_spec_dev_effect_conformance_adapter.py` | in-scope | CP:287 (AC-01) | none | `unrepresented` | - |
| 380 | `specs/current/tests/test_tla_spec_dev_kill_test_adapter.py` | in-scope | CP:287 (AC-01) | none | `unrepresented` | - |
| 381 | `specs/current/tests/test_tla_spec_dev_run_adapter.py` | in-scope | CP:287 (AC-01) | none | `unrepresented` | - |
| 382 | `specs/current/tests/test_tla_spec_dev_scaffold_adapter.py` | in-scope | CP:287 (AC-01) | none | `unrepresented` | - |
| 383 | `specs/current/tests/test_tla_spec_dev_skill_feedback_adapter.py` | in-scope | CP:287 (AC-01) | none | `unrepresented` | - |
| 384 | `specs/current/tests/test_tla_spec_dev_test_graph_adapter.py` | in-scope | CP:287 (AC-01) | none | `unrepresented` | - |
| 385 | `specs/current/tests/test_tla_spec_dev_ticket_adapter.py` | in-scope | CP:287 (AC-01) | none | `unrepresented` | - |
| 386 | `specs/current/tests/test_tla_spec_dev_update_ticket_adapter.py` | in-scope | CP:287 (AC-01) | none | `unrepresented` | - |
| 387 | `specs/desired_program_model/adapter_case_runtime.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 388 | `specs/desired_program_model/production_adapters.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 389 | `specs/desired_program_model/tests/test_current_ticket_workflow.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 390 | `specs/desired_program_model/tests/test_tla_spec_dev_analyze_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 391 | `specs/desired_program_model/tests/test_tla_spec_dev_binding_reconciliation.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 392 | `specs/desired_program_model/tests/test_tla_spec_dev_budgets_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 393 | `specs/desired_program_model/tests/test_tla_spec_dev_case_execution_run.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 394 | `specs/desired_program_model/tests/test_tla_spec_dev_cli_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 395 | `specs/desired_program_model/tests/test_tla_spec_dev_close_promotion_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 396 | `specs/desired_program_model/tests/test_tla_spec_dev_complexity_ledger_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 397 | `specs/desired_program_model/tests/test_tla_spec_dev_corpus_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 398 | `specs/desired_program_model/tests/test_tla_spec_dev_effect_conformance_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 399 | `specs/desired_program_model/tests/test_tla_spec_dev_kill_test_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 400 | `specs/desired_program_model/tests/test_tla_spec_dev_run_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 401 | `specs/desired_program_model/tests/test_tla_spec_dev_scaffold_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 402 | `specs/desired_program_model/tests/test_tla_spec_dev_skill_feedback_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 403 | `specs/desired_program_model/tests/test_tla_spec_dev_test_graph_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 404 | `specs/desired_program_model/tests/test_tla_spec_dev_ticket_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 405 | `specs/desired_program_model/tests/test_tla_spec_dev_update_ticket_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 406 | `specs/program_model/adapter_case_runtime.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 407 | `specs/program_model/production_adapters.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 408 | `specs/program_model/tests/test_current_ticket_workflow.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 409 | `specs/program_model/tests/test_tla_spec_dev_analyze_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 410 | `specs/program_model/tests/test_tla_spec_dev_binding_reconciliation.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 411 | `specs/program_model/tests/test_tla_spec_dev_budgets_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 412 | `specs/program_model/tests/test_tla_spec_dev_case_execution_run.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 413 | `specs/program_model/tests/test_tla_spec_dev_cli_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 414 | `specs/program_model/tests/test_tla_spec_dev_close_promotion_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 415 | `specs/program_model/tests/test_tla_spec_dev_complexity_ledger_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 416 | `specs/program_model/tests/test_tla_spec_dev_corpus_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 417 | `specs/program_model/tests/test_tla_spec_dev_effect_conformance_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 418 | `specs/program_model/tests/test_tla_spec_dev_kill_test_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 419 | `specs/program_model/tests/test_tla_spec_dev_run_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 420 | `specs/program_model/tests/test_tla_spec_dev_scaffold_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 421 | `specs/program_model/tests/test_tla_spec_dev_skill_feedback_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 422 | `specs/program_model/tests/test_tla_spec_dev_test_graph_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 423 | `specs/program_model/tests/test_tla_spec_dev_ticket_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 424 | `specs/program_model/tests/test_tla_spec_dev_update_ticket_adapter.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 425 | `specs/results/coverage-audit-sweep-raw/verify_tables.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 426 | `specs/results/epic-close/sweep-raw-run4/ca4_classify.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 427 | `specs/results/epic-close/sweep-raw-run5/ca5_changed_enum.sh` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 428 | `specs/results/epic-close/sweep-raw-run5/ca5_delta_check.sh` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 429 | `specs/results/finalization/sweep-raw-close2/cac2_classify.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 430 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/build.gradle.kts` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 431 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/settings.gradle.kts` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 432 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Context.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 433 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Executors.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 434 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/JBangExecutor.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 435 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/PlanExecutor.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 436 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/TimeoutParser.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 437 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/UvExecutor.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 438 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphAssembler.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 439 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphModel.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 440 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/MiniJson.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 441 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/NodeDescribeLoader.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 442 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/InspectionTasks.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 443 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunReportWriter.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 444 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunTestGraphTask.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 445 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/ValidationReportTask.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 446 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/TestGraphSpec.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 447 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/Toolchain.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 448 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphExtension.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 449 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphPlugin.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 450 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationNodeSpec.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 451 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationRuntime.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 452 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/test/kotlin/com/hayden/testgraphsdk/exec/PlanExecutorResumeHarnessTest.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 453 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build.gradle.kts` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 454 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/build.gradle.kts` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 455 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextItem.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 456 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextSerde.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 457 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Json.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 458 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/JsonMapper.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 459 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Node.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 460 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeBody.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 461 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeContext.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 462 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeResult.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 463 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeSpec.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 464 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeStatus.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 465 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ProcessRecord.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 466 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Procs.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 467 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/__init__.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 468 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/context_item.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 469 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/context.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 470 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/node_spec.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 471 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/procs.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 472 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/result.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 473 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/runner.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 474 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/settings.gradle.kts` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 475 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_cleanup.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 476 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_close_ticket.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 477 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_complete_ticket.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 478 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_create_repo.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 479 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_failure_cleanup_probe.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 480 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_force_failure.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 481 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_spec_units.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 482 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_start_ticket.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 483 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/tla_spec_dev_cli_help.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 484 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/tla_spec_dev_cli_install.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 485 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/build.gradle.kts` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 486 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/settings.gradle.kts` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 487 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Context.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 488 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Executors.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 489 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/JBangExecutor.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 490 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/PlanExecutor.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 491 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/TimeoutParser.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 492 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/UvExecutor.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 493 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphAssembler.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 494 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphModel.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 495 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/MiniJson.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 496 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/NodeDescribeLoader.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 497 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/InspectionTasks.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 498 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunReportWriter.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 499 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunTestGraphTask.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 500 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/ValidationReportTask.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 501 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/TestGraphSpec.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 502 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/Toolchain.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 503 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphExtension.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 504 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphPlugin.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 505 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationNodeSpec.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 506 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationRuntime.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 507 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/test/kotlin/com/hayden/testgraphsdk/exec/PlanExecutorResumeHarnessTest.kt` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 508 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build.gradle.kts` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 509 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/build.gradle.kts` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 510 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextItem.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 511 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextSerde.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 512 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Json.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 513 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/JsonMapper.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 514 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Node.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 515 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeBody.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 516 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeContext.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 517 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeResult.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 518 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeSpec.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 519 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeStatus.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 520 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ProcessRecord.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 521 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Procs.java` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 522 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/__init__.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 523 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/context_item.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 524 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/context.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 525 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/node_spec.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 526 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/procs.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 527 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/result.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 528 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/runner.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 529 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/settings.gradle.kts` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 530 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_cleanup.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 531 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_close_ticket.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 532 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_complete_ticket.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 533 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_create_repo.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 534 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_failure_cleanup_probe.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 535 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_force_failure.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 536 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_spec_units.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 537 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_start_ticket.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 538 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/tla_spec_dev_cli_help.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 539 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/tla_spec_dev_cli_install.py` | ESCALATION | none - no plan line names it | none | `unrepresented` | - |
| 540 | `templates/python/contract_tests.py.j2` | in-scope | CP:496 (AC-03) | none | `unrepresented` | - |
| 541 | `templates/python/docs.md.j2` | in-scope | CP:496 (AC-03) | none | `unrepresented` | - |
| 542 | `templates/python/fake.py.j2` | in-scope | CP:496 (AC-03) | none | `unrepresented` | - |
| 543 | `templates/python/package_init.py.j2` | in-scope | CP:496 (AC-03) | none | `unrepresented` | - |
| 544 | `templates/python/ports.py.j2` | in-scope | CP:496 (AC-03) | none | `unrepresented` | - |
| 545 | `templates/python/pyproject.toml.j2` | in-scope | CP:496 (AC-03) | none | `unrepresented` | - |
| 546 | `templates/python/strategies.py.j2` | in-scope | CP:496 (AC-03) | none | `unrepresented` | - |
| 547 | `templates/python/traces.py.j2` | in-scope | CP:496 (AC-03) | none | `unrepresented` | - |
| 548 | `templates/python/types.py.j2` | in-scope | CP:496 (AC-03) | none | `unrepresented` | - |
| 549 | `templates/python/validators.py.j2` | in-scope | CP:496 (AC-03) | none | `unrepresented` | - |
| 550 | `templates/tla/MC.cfg.j2` | in-scope | CP:496 (AC-03) | none | `unrepresented` | - |
| 551 | `templates/tla/MODULE.tla.j2` | in-scope | CP:496 (AC-03) | none | `unrepresented` | - |
| 552 | `test_graph/build.gradle.kts` | in-scope | CP:1272 (RP-07) | none | `unrepresented` | - |
| 553 | `test_graph/settings.gradle.kts` | in-scope | CP:1272 (RP-07) | none | `unrepresented` | - |
| 554 | `test_graph/sources/effect_provider_examples.py` | in-scope | CP:1272 (RP-07) | none | `unrepresented` | - |
| 555 | `test_graph/sources/spec_workflow_cleanup.py` | in-scope | CP:1272 (RP-07) | none | `unrepresented` | - |
| 556 | `test_graph/sources/spec_workflow_close_ticket.py` | in-scope | CP:1272 (RP-07) | none | `unrepresented` | - |
| 557 | `test_graph/sources/spec_workflow_complete_ticket.py` | in-scope | CP:1272 (RP-07) | none | `unrepresented` | - |
| 558 | `test_graph/sources/spec_workflow_create_repo.py` | in-scope | CP:1272 (RP-07) | none | `unrepresented` | - |
| 559 | `test_graph/sources/spec_workflow_failure_cleanup_probe.py` | in-scope | CP:1272 (RP-07) | none | `unrepresented` | - |
| 560 | `test_graph/sources/spec_workflow_force_failure.py` | in-scope | CP:1272 (RP-07) | none | `unrepresented` | - |
| 561 | `test_graph/sources/spec_workflow_spec_units.py` | in-scope | CP:1272 (RP-07) | none | `unrepresented` | - |
| 562 | `test_graph/sources/spec_workflow_start_ticket.py` | in-scope | CP:1272 (RP-07) | none | `unrepresented` | - |
| 563 | `test_graph/sources/tla_spec_dev_cli_help.py` | in-scope | CP:1272 (RP-07) | none | `unrepresented` | - |
| 564 | `test_graph/sources/tla_spec_dev_cli_install.py` | in-scope | CP:1272 (RP-07) | none | `unrepresented` | - |
| 565 | `tests/conftest.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 566 | `tests/corpus_fixtures.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 567 | `tests/effect_adapter_fixtures.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 568 | `tests/test_analyze_architecture.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 569 | `tests/test_analyze_complexity.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 570 | `tests/test_architecture_reflexion.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 571 | `tests/test_budgets.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 572 | `tests/test_case_adapter_runtime.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 573 | `tests/test_case_modules.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 574 | `tests/test_complexity_ledger.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 575 | `tests/test_corpus_diagnostics.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 576 | `tests/test_effect_conformance_cli.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 577 | `tests/test_effect_conformance_runner.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 578 | `tests/test_effect_conformance.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 579 | `tests/test_effect_provider_example_validation.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 580 | `tests/test_effect_provider_fuzzing.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 581 | `tests/test_effect_provider_runtime.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 582 | `tests/test_export_testgraph_cases.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 583 | `tests/test_extract_spec_manifest.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 584 | `tests/test_fitness_functions.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 585 | `tests/test_generate_cases_from_tlc_dump.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 586 | `tests/test_infer_action_params.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 587 | `tests/test_kill_test.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 588 | `tests/test_new_ticket_workflow.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 589 | `tests/test_onboard_program_model.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 590 | `tests/test_promotion_preserves_current.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 591 | `tests/test_scaffold_spec_views.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 592 | `tests/test_skill_feedback.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 593 | `tests/test_spec_evolution.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 594 | `tests/test_spec_yaml_valid.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 595 | `tests/test_testgraph_channels.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |
| 596 | `tests/test_tla_spec_dev_cli.py` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) | none | `unrepresented` | - |

---

## 3. Sweep 2 — Effects, by category

**Search surface.** Every category was run against `$SURFACE` — the exact 596
files Sweep 1 enumerated — not against a hardcoded subdirectory. Command shape:

```bash
tr '\n' '\0' < sweep1-surface.txt | xargs -0 grep -nE "<pattern>" > effects-<cat>.txt
wc -l < effects-<cat>.txt
```

Patterns are the word-boundary-anchored ones in `prompts/coverage_audit.md`
Step 3, plus a JVM/native category (`File(`, `ProcessBuilder`, `HttpClient`,
`System.getenv`, `Files.`, `Paths.get`, `Runtime.getRuntime`) because 116 of the
596 files are Kotlin/Java/Gradle and a category searched only in Python is a
category not swept.

**Grouping, and the accounting contract.** Every category is dispositioned **by
group**, as Step 3 permits. The grouping rule is a machine-applied ordered
match list in `cac_ac_classify.py::EFFECT_RULES`: **first rule whose regex
matches the hit's text wins, and the script asserts that the sum of group sizes
equals the raw count** for every category (`assert assigned == len(hits)`). A
reader applying those regexes to the committed raw files lands on these exact
groups. Groups are by **distinct effect semantics**, never by file.

**The collapsing rule, stated once.** Every category carries a terminal `*-N`
group: *the token matched but the line performs no such effect* — `str.replace`,
`list.remove`, `def run(`, the word "time" in prose, an `argparse` `choices=`
list, an import line. `*-N` hits are **counted, not discarded**: raw count minus
`*-N` count is the collapsed count, and both are published. Step 3's warning
holds here — the raw filesystem sweep is 3,909 hits of which 2,060 (53%) are
lexical noise, and neither publishing the noise nor silently dropping it is
acceptable.

**Verdict per group:** `declared` / `undeclared` / `partial`. The two
non-negotiable rules were applied: a `process.spawn` port declares the spawn and
not what the child did, so every spawn group whose child performs its own
effects is `partial` at best; and a site in a runtime the effect sandbox cannot
observe is `undeclared`, with the note that the shipped oracle could not have
seen it either.

**A prior fact that bounds every verdict in this section:**
`spec_manifest.yaml:64-66` sets `case_codegen.generation_status: planned` and
`state_fields`/`actions`/`ports` are empty placeholders (`:78-80`). **No
generated case package exists for `TlaSpecDevCli`.** The effect-conformance
oracle therefore has never executed a single case against this model. Every
`declared` verdict below is a declaration that has never been *checked* against
an observation — which is precisely the structural hole this gate exists to
find.

### 3.1 Filesystem — raw **3,909**, collapsed **1,849**, rule: `FS-N` = lexical-only (2,060 hits)

| Group | Distinct effect semantics | Raw hits | in-scope | ESCALATION | Declared port | Verdict |
|---|---|---|---|---|---|---|
| `FS-D` | DESTRUCTIVE: delete / rename / overwrite-in-place of a real path | 54 | 36 | 18 | `spec_tree_delete` (`**/specs/**`) on `CloseTicket` | `partial` — enumerated per-site in §3.1.1 |
| `FS-W` | WRITE/CREATE: creates or overwrites a file or directory | 828 | 603 | 225 | `spec_tree`, `evidence_report`, `cli_artifact`, `mutation_write` | `partial` — the `--out` writes in `analyze_architecture.py:1116-1117` and `architecture_reflexion.py:2290-2291` match **no** declared port and belong to an action with **no manifest row** (G-1, G-2, G-3) |
| `FS-T` | TEMP WORKDIR: creates a temporary tree | 34 | 29 | 5 | none | `undeclared` — no port targets a temp root; the sandbox work tree under `spec_dir/.effect-conformance-work` is covered by `spec_tree` but `tempfile`/`mkdtemp` roots outside the spec tree are not |
| `FS-R` | READ / PATH CONSTRUCTION: no mutation of the filesystem | 933 | 555 | 378 | n/a | not an effect — reads are not among the sandbox-observable types (`spec_manifest.yaml:103-105`) |
| `FS-N` | LEXICAL ONLY | 2,060 | 1,157 | 903 | n/a | collapsed |

#### 3.1.1 Destructive sites — enumerated per-site, never grouped (54 rows)

Step 3: "Destructive effects (delete, rename, overwrite, truncate) are **always
enumerated per-site**." Rule for membership, machine-applied:
`rmtree|\.unlink\(|os\.remove\(|os\.rename\(|os\.replace\(|shutil\.move\(|replace_tree`.
Bare `remove`/`rename`/`replace` without a filesystem qualifier fell to `FS-N`
(that is the 95%-false-positive class Step 3 warns about: the unqualified
pattern returned 262 hits, of which 208 were `str.replace` / `list.remove` /
prose).

| # | Site | Line | In/Out | Plan line |
|---|---|---|---|---|
| 1 | `examples/distributed_history/scripts/regenerate_tlc_cases.py:58` | `shutil.rmtree(path)` | in-scope | CP:709 (EV-01) |
| 2 | `examples/effect_providers/atomic_publisher/conformance.py:82` | `os.replace(command.source, command.target)` | in-scope | CP:710 (EV-01) |
| 3 | `examples/effect_providers/atomic_publisher/conformance.py:91` | `path.unlink()` | in-scope | CP:710 (EV-01) |
| 4 | `examples/effect_providers/atomic_publisher/providers.py:180` | `shutil.rmtree(lifecycle_root)` | in-scope | CP:710 (EV-01) |
| 5 | `examples/effect_providers/atomic_publisher/regenerate.py:44` | `shutil.rmtree(target)` | in-scope | CP:710 (EV-01) |
| 6 | `examples/effect_providers/legacy_payment_http/scripts/regenerate.py:53` | `shutil.rmtree(contract)` | in-scope | CP:710 (EV-01) |
| 7 | `examples/effect_providers/legacy_payment_http/scripts/regenerate.py:73` | `shutil.rmtree(package_dir)` | in-scope | CP:710 (EV-01) |
| 8 | `examples/effect_providers/legacy_payment_http/scripts/run_experiment.py:794` | `path.unlink()` | in-scope | CP:710 (EV-01) |
| 9 | `examples/effect_providers/reminder_worker/regenerate.py:50` | `shutil.rmtree(path)` | in-scope | CP:710 (EV-01) |
| 10 | `examples/run_distributed_history_validation.py:430` | `shutil.rmtree(path)` | ESCALATION | none - no plan line names it |
| 11 | `examples/run_distributed_history_validation.py:432` | `shutil.rmtree(path)` | ESCALATION | none - no plan line names it |
| 12 | `examples/validation/runs/ex1-run4/artifacts/providers.py:102` | `shutil.rmtree(self.root)` | in-scope | CP:784 (EV-02) |
| 13 | `examples/validation/runs/ex4-run1/artifacts/kill_matrix.py:76` | `shutil.rmtree(pyc, ignore_errors=True)` | in-scope | CP:784 (EV-02) |
| 14 | `examples/validation/runs/ex4-run1/artifacts/kill_matrix.py:99` | `shutil.rmtree(pyc, ignore_errors=True)` | in-scope | CP:784 (EV-02) |
| 15 | `examples/validation/runs/ex4-run1/artifacts/kill_matrix.py:117` | `shutil.rmtree(pyc, ignore_errors=True)` | in-scope | CP:784 (EV-02) |
| 16 | `examples/validation/runs/ex4-run1/artifacts/replay.py:48` | `shutil.rmtree(pyc, ignore_errors=True)` | in-scope | CP:784 (EV-02) |
| 17 | `examples/validation/runs/ex4-run1/artifacts/replay.py:62` | `shutil.rmtree(pyc, ignore_errors=True)` | in-scope | CP:784 (EV-02) |
| 18 | `examples/validation/runs/ex4-run4/artifacts/kill_matrix_round2.py:59` | `shutil.rmtree(pyc, ignore_errors=True)` | in-scope | CP:784 (EV-02) |
| 19 | `examples/validation/runs/ex4-run5/artifacts/replay.py:48` | `shutil.rmtree(pyc, ignore_errors=True)` | in-scope | CP:784 (EV-02) |
| 20 | `examples/validation/runs/ex4-run5/artifacts/replay.py:62` | `shutil.rmtree(pyc, ignore_errors=True)` | in-scope | CP:784 (EV-02) |
| 21 | `scripts/close_spec_workflow.py:49` | `shutil.rmtree(path)` | ESCALATION | none - no plan line names it |
| 22 | `scripts/close_tickets.py:127` | `dst_files[relative].unlink()` | ESCALATION | none - no plan line names it |
| 23 | `scripts/close_tickets.py:232` | `shutil.rmtree(directory)` | ESCALATION | none - no plan line names it |
| 24 | `scripts/effect_conformance.py:692` | `self._patch_module(shutil, "rmtree", "filesystem.delete", 0)` | ESCALATION | none - no plan line names it |
| 25 | `scripts/generate_cases_from_tlc_dump.py:139` | `shutil.rmtree(metadir, ignore_errors=True)` | in-scope | CP:208 (CM-01), CP:966 (RP-02), CP:1210 (RP-03), CP:150 (service_catalog) |
| 26 | `scripts/spec_evolution.py:154` | `shutil.rmtree(state_dir)` | in-scope | CP:207 (CM-01) |
| 27 | `scripts/spec_evolution.py:383` | `def replace_tree(src: Path, dst: Path) -> list[dict[str, Any]]:` | in-scope | CP:207 (CM-01) |
| 28 | `scripts/spec_evolution.py:385` | `shutil.rmtree(dst)` | in-scope | CP:207 (CM-01) |
| 29 | `scripts/spec_evolution.py:477` | `target.unlink()` | in-scope | CP:207 (CM-01) |
| 30 | `specs/results/epic-close/sweep-raw-run4/ca4_classify.py:73` | `"scripts/close_spec_workflow.py": "close wrapper; rmtree :49 not performed by a modeled action, no port owed p` | ESCALATION | none - no plan line names it |
| 31 | `specs/results/epic-close/sweep-raw-run4/ca4_classify.py:75` | `"scripts/close_tickets.py": "batch close (promotion_rule :565 forbids ticket agents running it); unlink :127 /` | ESCALATION | none - no plan line names it |
| 32 | `specs/results/epic-close/sweep-raw-run4/ca4_classify.py:185` | `pat = re.compile(r"shutil\.rmtree|\.unlink\(|os\.remove\(")` | ESCALATION | none - no plan line names it |
| 33 | `specs/results/epic-close/sweep-raw-run5/ca5_changed_enum.sh:15` | `'\b(open|Path|write_text|read_text|write_bytes|mkdir|makedirs|remove|unlink|rename|replace|copy|copytree|rmtre` | ESCALATION | none - no plan line names it |
| 34 | `specs/results/epic-close/sweep-raw-run5/ca5_delta_check.sh:11` | `'\b(open|Path|write_text|read_text|write_bytes|mkdir|makedirs|remove|unlink|rename|replace|copy|copytree|rmtre` | ESCALATION | none - no plan line names it |
| 35 | `specs/results/finalization/sweep-raw-close2/cac2_classify.py:219` | `pat = re.compile(r"shutil\.rmtree|\.rmtree\(|\.unlink\(|os\.remove\(|rm -rf|deleteRecursively|Files\.delete|mk` | ESCALATION | none - no plan line names it |
| 36 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_cleanup.py:32` | `shutil.rmtree(repo)` | ESCALATION | none - no plan line names it |
| 37 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_create_repo.py:36` | `shutil.rmtree(repo_dir)` | ESCALATION | none - no plan line names it |
| 38 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_failure_cleanup_probe.py:47` | `shutil.rmtree(target)` | ESCALATION | none - no plan line names it |
| 39 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_cleanup.py:32` | `shutil.rmtree(repo)` | ESCALATION | none - no plan line names it |
| 40 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_create_repo.py:36` | `shutil.rmtree(repo_dir)` | ESCALATION | none - no plan line names it |
| 41 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_failure_cleanup_probe.py:47` | `shutil.rmtree(target)` | ESCALATION | none - no plan line names it |
| 42 | `test_graph/sources/spec_workflow_cleanup.py:32` | `shutil.rmtree(repo)` | in-scope | CP:1272 (RP-07) |
| 43 | `test_graph/sources/spec_workflow_create_repo.py:36` | `shutil.rmtree(repo_dir)` | in-scope | CP:1272 (RP-07) |
| 44 | `test_graph/sources/spec_workflow_failure_cleanup_probe.py:49` | `shutil.rmtree(target)` | in-scope | CP:1272 (RP-07) |
| 45 | `tests/test_architecture_reflexion.py:1746` | `(deleted / "pkg" / "deliver.py").unlink()` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) |
| 46 | `tests/test_effect_conformance.py:129` | `victim.unlink()` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) |
| 47 | `tests/test_effect_conformance.py:824` | `subprocess.run([sys.executable, "-c", f"import os; os.remove({str(victim)!r})"], check=True)` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) |
| 48 | `tests/test_effect_provider_fuzzing.py:1320` | `event_log.unlink()` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) |
| 49 | `tests/test_effect_provider_fuzzing.py:1369` | `event_log.unlink()` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) |
| 50 | `tests/test_effect_provider_runtime.py:1370` | `(spec_dir / "events.txt").unlink()` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) |
| 51 | `tests/test_kill_test.py:950` | `(spec_dir / "MC.cfg").unlink()` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) |
| 52 | `tests/test_new_ticket_workflow.py:236` | `(ticket_dir / model_dir / "seeded_stale_adapter.py").unlink()` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) |
| 53 | `tests/test_promotion_preserves_current.py:4` | ```shutil.rmtree``'d ``specs/current`` before copying the ticket's ``desired/``` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) |
| 54 | `tests/test_skill_feedback.py:244` | `# GitHub #22 / MF-021: promotion rmtree'd specs/current and destroyed` | in-scope | CP:210 (CM-01), CP:380 (AC-02), CP:873 (RP-01), CP:967 (RP-02), CP:1079 (RP-04), CP:1213 (RP-03) |

**Reading of the 54:** 36 are in scope. Of those, 5 are in the CLI's own close
path (`scripts/spec_evolution.py:154, :383, :385, :477` and
`scripts/generate_cases_from_tlc_dump.py:139`). The four `spec_evolution.py`
sites are `declared` — `spec_tree_delete` (`filesystem.delete`, `**/specs/**`)
on `CloseTicket`, and the manifest comment at `spec_manifest.yaml:145-152`
names `:154`, `:385` and `:477` explicitly. `generate_cases_from_tlc_dump.py:139`
(`shutil.rmtree(metadir)`) is **`undeclared`**: no action represents case
generation (G-10). The 31 remaining in-scope destructive sites are in
`examples/**`, `tests/` and `test_graph/sources/` — `unrepresented` with **no
available disposition** (ESC-2, ESC-3). The 18 escalation sites include
`scripts/close_spec_workflow.py:49` and `scripts/close_tickets.py:127,:232`,
which delete real trees on the workflow-close path and which no plan line
classifies.

### 3.2 Subprocess — raw **1,366**, collapsed **344**, rule: `SP-N` = no spawn primitive on the line (1,022 hits)

| Group | Distinct effect semantics | Raw hits | in-scope | ESCALATION | Declared port | Verdict |
|---|---|---|---|---|---|---|
| `SP-S` | REAL SPAWN: starts a child process | 344 | 197 | 147 | `test_process` (`*pytest*`), `runner_process` (`*run_generated_case_adapters*`), `git_metadata` (`git rev-parse*`), `corpus_process` (`*`) | **`partial`** |
| `SP-N` | LEXICAL ONLY: bare `run`/`call`/`system` | 1,022 | 476 | 546 | n/a | collapsed |

`partial`, and the reason is MF-027's process-boundary rule, which is not
re-collapsed here: **the four spawn ports declare the spawn, not what the child
did.** `test_process` declares that a `*pytest*` child starts; the child then
writes files, spawns further children and reads the environment, and none of
that is represented. `corpus_process` has target `*` — it declares that *some*
process starts, which is the weakest possible claim. Concretely undeclared in
scope: `scripts/generate_cases_from_tlc_dump.py:115` (`subprocess.run(command,
...)` — the java/TLC spawn) belongs to no modeled action (G-10), and the manifest
comment at `spec_manifest.yaml:124-130` says so while citing a scope amendment
the current plan does not carry (G-6). Escalation-class spawns that no plan line
classifies include `scripts/kill_test.py` (3 sites),
`scripts/run_generated_case_adapters.py` (3), `scripts/onboard_program_model.py`
(2) and `scripts/effect_conformance.py` (15).

### 3.3 Network — raw **145**, collapsed **105**, rule: `NW-N` = `connect`/`requests` as a word (40 hits)

| Group | Distinct effect semantics | Raw hits | in-scope | ESCALATION | Declared port | Verdict |
|---|---|---|---|---|---|---|
| `NW-S` | REAL NETWORK: opens or issues a network connection | 105 | 84 | 21 | **none — no `network.*` port exists** | **`undeclared`** |
| `NW-N` | LEXICAL ONLY | 40 | 34 | 6 | n/a | collapsed |

**`undeclared`, and this is the category the prompt's Run-1 warning predicted.**
The nine declared ports are all `filesystem.*` or `process.spawn`; there is no
`network.connect` or `network.http` port anywhere in `spec_manifest.yaml`,
although `scripts/effect_conformance.py:106` lists `network.connect` among the
observable types and `:775-788` monkeypatches `socket.socket.connect` to record
it. So the sandbox *can* see network effects and the model declares none.

Where the 105 are: 84 in scope, all in `examples/**` (the `legacy_payment_http`
fixture's HTTP provider, 24 sites) and `tests/` — separate programs, unrepresented
by construction (ESC-2). The 21 escalation hits include the one that matters:
**`skill-scripts/install-tlc2.sh:37`, a real `curl -fL "$JAR_URL"` download on
the install path the model represents as `BuildSkillCli`/`InstallLocalCli`**
(ESC-6). The `scripts/effect_conformance.py` hits are the sandbox's own
interception machinery, not outbound calls. **The modeled CLI itself makes no
network call from Python; it makes one from shell, and no port covers it.**

### 3.4 Environment — raw **394**, collapsed **167**, rule: `EN-N` = `dict.setdefault`, `PATH` in prose, an argparse dest (227 hits)

| Group | Distinct effect semantics | Raw hits | in-scope | ESCALATION | Declared port | Verdict |
|---|---|---|---|---|---|---|
| `EN-S` | REAL ENVIRONMENT READ/WRITE: `os.environ`, `getenv`, `expanduser`, `sys.argv` | 167 | 132 | 35 | none | **`undeclared`** |
| `EN-N` | LEXICAL ONLY | 227 | 94 | 133 | n/a | collapsed |

`undeclared`, with the qualification that environment reads are **not among the
five sandbox-observable types** (`spec_manifest.yaml:103-105`: `filesystem.write`,
`filesystem.delete`, `process.spawn`, `network.connect`, `network.http`). A port
whose type cannot be observed can never be checked, so the schema cannot
express these. That is a real limit of the effect model, not an oversight of
this epic — but `unobservable` is not `clean`, and the model represents no
environment dependency at all despite 167 real sites, including
`JAVA_TOOL_OPTIONS` manipulation in `scripts/generate_cases_from_tlc_dump.py:900`
and `case_modules.tlc_environment` (`:113`), which is the mechanism RP-03 shipped.

### 3.5 Clock — raw **384**, collapsed **129**, rule: `CL-N` = the words time/now/today, a `timeout` identifier, an import (255 hits)

| Group | Distinct effect semantics | Raw hits | in-scope | ESCALATION | Declared port | Verdict |
|---|---|---|---|---|---|---|
| `CL-S` | REAL CLOCK READ / SLEEP | 129 | 87 | 42 | none | **`undeclared`** |
| `CL-N` | LEXICAL ONLY | 255 | 158 | 97 | n/a | collapsed |

`undeclared`, same observability limit as §3.4. Consequential because the epic's
own determinism aim (`ticket_plan.yaml:133-137`, "BE RERUNNABLE AND
DETERMINISTIC") is a claim about exactly this class, and the model carries no
representation of a clock read anywhere — including on the close path, where
history-entry timestamps are written.

### 3.6 Randomness — raw **50**, collapsed **9**, rule: `RN-N` = `choice`/`sample`/`random` as a word or an argparse `choices=` list (41 hits)

| Group | Distinct effect semantics | Raw hits | in-scope | ESCALATION | Declared port | Verdict |
|---|---|---|---|---|---|---|
| `RN-S` | REAL RANDOMNESS: nondeterministic value source | 9 | 6 | 3 | none | **`undeclared`** |
| `RN-N` | LEXICAL ONLY | 41 | 39 | 2 | n/a | collapsed |

All 9 real sites are seeded `random.Random(context.derived_seed)` in effect
providers (`examples/effect_providers/*/providers.py`, `tests/test_effect_provider_fuzzing.py:1202`)
plus `spec_double_compiler/effects.py:17`. Seeded is not unmodeled — but the seed
derivation is toolchain plumbing that no plan line classifies (ESC-7). `undeclared`
by default polarity; the modeled CLI performs no unseeded randomness.

### 3.7 Persistent store — raw **107**, collapsed **5**, rule: `PT-N` = `execute`/`commit`/`session`/`engine` as words — git commit, subprocess execute, a session id (102 hits)

| Group | Distinct effect semantics | Raw hits | in-scope | ESCALATION | Declared port | Verdict |
|---|---|---|---|---|---|---|
| `PT-S` | REAL PERSISTENT STORE | 5 | 3 | 2 | none | `undeclared` (fixture-only) |
| `PT-N` | LEXICAL ONLY | 102 | 73 | 29 | n/a | collapsed |

The 3 in-scope real sites are `sqlite3` in `examples/distributed_history/ecommerce_backend/domain.py:4,:28,:29`
— the example application's own store, not this CLI's. The 2 escalation hits are
the previous audit's own sweep scripts quoting the pattern. **The modeled CLI
uses no database.** This is the one category where the model's silence is right.

### 3.8 JVM / native — raw **417**, collapsed **57**, rule: `JV-N` = File/exec/Runtime as a word, an import, or a type name (360 hits)

| Group | Distinct effect semantics | Raw hits | in-scope | ESCALATION | Declared port | Verdict |
|---|---|---|---|---|---|---|
| `JV-S` | REAL JVM/NATIVE EFFECT: process, network, env, or file API on the JVM side | 57 | 18 | 39 | none | **`undeclared`** |
| `JV-N` | LEXICAL ONLY | 360 | 118 | 242 | n/a | collapsed |

`undeclared`, and Step 3's second non-negotiable rule applies verbatim: **these
sites are in a runtime the effect sandbox cannot observe.** `scripts/effect_conformance.py`
patches Python's `shutil`, `pathlib`, `subprocess` and `socket` in *this
interpreter* (`:1142`), so every Kotlin and Java site in `test_graph/`,
`examples/distributed_history/test_graph/` and the Test Graph SDK is invisible
to the shipped oracle. The oracle would report clean on all 57. `unobservable`
is not `clean`.

---

## 4. Sweep 3 — Behaviors

Same surface, same command shape, same accounting contract (`cac_ac_classify.py::BEHAVIOR_RULES`,
asserting group sizes sum to the raw count). Grouped by **distinct failure /
branch semantics**, never by file.

### 4.1 Error paths — raw **1,431**, groups **5**

Grouping rule: `raise` (refuse-and-propagate) → silent-capable handler
(`except …: pass|return None|continue`, or a bare block handler) → non-silent
handler → `try:` opener → lexical. First match wins.

| Group | Distinct behavior semantics | Raw | in-scope | ESC | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|
| `EP-RAISE` | RAISES: the site refuses and propagates | 876 | 554 | 322 | none | `unrepresented` |
| `EP-CATCH-SILENT` | CATCHES: handler that may swallow | 190 | 119 | 71 | none | `unrepresented` |
| `EP-CATCH` | CATCHES: handler with a non-silent body | 77 | 40 | 37 | none | `unrepresented` |
| `EP-TRY` | TRY BLOCK opener | 288 | 185 | 103 | n/a | structural |
| `EP-N` | LEXICAL ONLY | 0 | 0 | 0 | n/a | collapsed |

**The model represents exactly one refusal shape.** `CommandResult(ok, reason,
nextStep)` (`TlaSpecDevCli.tla:199`) carries a boolean and a reason, and the
guards that produce `accepted = FALSE` are the lifecycle preconditions
(`setup_phase`, `ticket_state`, gate verdicts). None of the 1,143 real
raise/catch sites is represented as a distinct outcome. The predecessor plan
recorded this as a limitation ("Per-command refusal branches beyond the modeled
gate verdicts … are out-of-model", `PS:101`); **the current plan carries no such
line**, so it is back as an uncovered behavior class (part of G-9).

### 4.2 Retries — raw **528**, collapsed **3**, rule: `RT-N` = retry/attempt as a word, an identifier, or a message (525 hits)

| Group | Raw | in-scope | ESC | Verdict |
|---|---|---|---|---|
| `RT-S` REAL RETRY LOOP | 3 | 1 | 2 | `unrepresented` |
| `RT-N` LEXICAL ONLY | 525 | 447 | 78 | collapsed |

Three real retry loops, one in scope. The model has no retry representation.
The 525-hit noise floor is the largest false-positive ratio in the audit (99.4%)
and is exactly the effect the prompt's unanchored-pattern warning describes.

### 4.3 Timeouts — raw **275**, collapsed **110**, rule: `TO-N` = the word timeout in prose or a help string (165 hits)

| Group | Raw | in-scope | ESC | Verdict |
|---|---|---|---|---|
| `TO-S` REAL TIMEOUT / DEADLINE | 110 | 82 | 28 | `unrepresented` |
| `TO-N` LEXICAL ONLY | 165 | 80 | 85 | collapsed |

110 real timeout/deadline sites, 0 represented. RP-07's whole subject —
`awaitWithTimeout` and the node launcher's descendant contract — lives in this
group and in `test_graph/`, which `semantic_model_rule` (`:26`) forbids modeling
(ESC-3).

### 4.4 Fallbacks — raw **314**, groups **4**

| Group | Distinct behavior semantics | Raw | in-scope | ESC | Verdict |
|---|---|---|---|---|---|
| `FB-IMPORT` | IMPORT FALLBACK: an optional dependency changes behaviour when absent | 33 | 15 | 18 | `unrepresented` |
| `FB-SILENT` | **SILENT DEFAULT: a missing input yields a default rather than a refusal** | 12 | 10 | 2 | **`unrepresented`** |
| `FB-DEFAULT` | DECLARED DEFAULT: argparse/config default | 232 | 111 | 121 | `unrepresented` |
| `FB-N` | LEXICAL ONLY | 37 | 18 | 19 | collapsed |

`FB-IMPORT` is consequential and is a live, recorded instance of the class this
doctrine keeps rediscovering — **a guard that silently passes when its input is
absent.** The plan itself warns "Run pytest with `--with pyyaml` or the
YAML-validity guard skips silently" (`ticket_plan.yaml:70-71`). That is a
config-driven branch that *disables a check*, it is documented as a hazard in
the plan, and **the model does not represent the disabled path.** `FB-SILENT`'s
12 sites are the `.get(key, None|[]|False)` shape that RP-01 spent an entire
ticket repairing in one field (`blind_spots: []` vs `null`); the repair was to
one consumer, and the model represents neither the present nor the absent path.

### 4.5 Concurrency / interleaving — raw **29**, collapsed **10**

| Group | Raw | in-scope | ESC | Verdict |
|---|---|---|---|---|
| `CC-S` REAL CONCURRENCY PRIMITIVE | 10 | 4 | 6 | `unrepresented` |
| `CC-N` LEXICAL ONLY | 19 | 12 | 7 | collapsed |

10 real primitives, 0 represented. The model is a single-threaded lifecycle:
`Next` (`TlaSpecDevCli.tla:667-696`) is a disjunction of whole commands with no
interleaving between components, and there is only one component to interleave
(§5). RP-07's diagnosis — a Kotlin compile daemon outliving the node launcher —
is precisely an interleaving defect, and it is unrepresentable in this model by
construction.

### 4.6 Config-driven branches — raw **1,160**, groups **4**

| Group | Distinct behavior semantics | Raw | in-scope | ESC | Verdict |
|---|---|---|---|---|---|
| `CB-ENV` | ENVIRONMENT-DRIVEN BRANCH | 124 | 101 | 23 | `unrepresented` |
| `CB-FLAG` | CLI-FLAG-DRIVEN BRANCH | 42 | 24 | 18 | `unrepresented` (G-9) |
| `CB-KEY` | CONFIG-KEY LOOKUP: behaviour depends on a manifest/JSON key | 825 | 423 | 402 | `unrepresented` |
| `CB-N` | LEXICAL ONLY | 169 | 96 | 73 | collapsed |

991 real config-driven branches, 0 represented. `CB-FLAG` contains the
guard-weakening flags that change the semantics of a *modeled* guard:
`--accept-new` (`tla_spec_dev.py:723`), `--allow-open` (`:719`),
`--no-promote-current` (`:721`), `--force` (`:428`, `:443`, `:471`), `--dry-run`
(`:429`, `:444`, `:472`), `--validate-only` (`:512`). `CloseTicket`'s guard
(`TlaSpecDevCli.tla:619-638`) encodes "current equals desired and spec-unit tests
passed"; `--accept-new` bypasses the first and `--allow-open` bypasses the
ticket-state precondition, and the model has no state in which either has
happened. The predecessor plan recorded per-flag variants as out-of-model
(`PS:101`, "guard-weakening flags are governed by doctrine, not modeled"); **the
current plan does not.**

---

## 5. Sweep 4 — Views, reported separately

**This project has exactly one view module.** `git ls-files 'specs/current/*.tla'`
returns `TlaSpecDevCli.tla` and nothing else; there is no `Internal.tla` and no
`External.tla`. Per Step 5, that is a Sweep-4 finding of the highest order and
is **not** reported as "N/A — single module": a single module is not a merged
view, it is a missing one.

`specs/desired_program_model/spec_manifest.yaml:56-61` records the history —
MF-023 measured `Q = 0.012`, found no clean cut, and deliberately did not
decompose — and cites "ticket_plan.yaml known_gaps, amended 2026-07-22" as the
authority. **That known_gaps entry does not exist in the architectural-coherence
plan** (G-6, ESC-1). AC-01 then re-measured the same model and found it worse:
"one component, Q = 0.000 (lastCommand and result are written by all 15
commands)" (`ticket_plan.yaml:335-337`), and RP-01 measured this repository's own
declared four-component partition at "Q = -0.025, 60% of actions crossing"
(`:919-921`).

### 5.1 Internal — verdict: `partial`

The single module *is* the internal view: it carries component-level state and
per-command transitions.

| Surface item | Verdict | Evidence (`file:line`) |
|---|---|---|
| Component state (10 variables) | `represented` | `TlaSpecDevCli.tla:162-172` |
| Internal actions (15 + `Stutter`) | `represented` | `TlaSpecDevCli.tla:228-666`, `Next` at `:667-696` |
| Lifecycle invariants (12) | `represented` | `TlaSpecDevCli.tla:698-843` |
| **Component decomposition** | `unrepresented` | The model's own tooling refuses to derive one: 1 emergent component, `Q = 0.000` (`ticket_plan.yaml:335-337`); the declared 4-component partition scores `Q = -0.025` (`:919-921`). There is no internal structure to interleave. |
| **Interleaving between components** | `unrepresented` | `Next` is a flat disjunction of whole commands (`:667-696`); no two components step concurrently because there are no components. 10 real concurrency primitives exist in the program (§4.5). |
| **Effect-provider / adapter runtime internals** | `unrepresented` | `spec_double_compiler/*`, `scripts/run_generated_case_adapters.py` — ESC-7 |

### 5.2 External — verdict: `unrepresented` (whole surface, by construction)

There is no External view module. Step 5: "report the whole External surface as
unrepresented rather than reporting the single module as complete."

**Enumeration (recorded):** `python3 specs/results/coverage-audit-arch-coherence-raw/cac_ac_external_surface.py`
walks the shipped `argparse` tree from `scripts/tla_spec_dev.py::build_parser`
and emits every caller-drivable item. **N = 93** (raw:
`sweep4-external-surface.txt`): 15 subcommands, 9 positionals, 69 options.

| # | Surface item | Verdict | Evidence (`file:line`) |
|---|---|---|---|
| 1-10 | The 10 **leaf** subcommands: `scaffold project`, `scaffold workflow`, `open ticket`, `run spec-unit-tests`, `run effect-conformance`, `run kill-test`, `analyze complexity`, `analyze architecture`, `analyze corpus`, `close ticket` | `represented` | `TlaSpecDevCli.tla:263/305/324/561/466/522/393/650/427/619` ↔ `tla_spec_dev.py:421/435/463/491/544/571/616/639/668/708` |
| 11-15 | The 5 **group** subcommands `scaffold`, `open`, `run`, `analyze`, `close` invoked bare | **`unrepresented`** | Each sets `func=incomplete_command` (`tla_spec_dev.py:416, :458, :486, :608, :703`), which prints `incomplete command: <path>` and **exits 2** (`:56-61`). That is an externally observable outcome with no action and no `result` value in the model (**G-8**). |
| 16-24 | The 9 positionals (`ticket_name`, `tla`, `cfg`, `cases_dir`, …) | **`unrepresented`** | `sweep4-external-surface.txt`. Only `root ∈ SpecRoots` and `ticket ∈ Tickets` are modeled as action parameters; no other positional exists in the model. |
| 25-93 | The 69 options | **`unrepresented`** | `sweep4-external-surface.txt`. Includes the six guard-weakening flags in §4.6 (**G-9**). |
| — | The **observable projection**: what a caller can *see* | **`partial`** | The model projects `lastCommand` and `result` (`TlaSpecDevCli.tla:166-167`) plus four gate verdicts. The CLI additionally emits the full descriptor text/JSON, the reflexion report, the delta, the coverage report, exit codes 0/1/2, and stderr `wrote evidence: <path>` lines (`analyze_architecture.py:1118`). None of those is projected. |

**External verdict `unrepresented`: 83 of 93 external surface items have no
representation, and there is no External module in which they could have one.**

---

## 6. Dispositions

Only three exist. **No "justified", "accept as-is", "acceptable risk", "known
limitation", "deferred" or "out of contract" disposition is available for an
in-scope gap.** None is used below.

### 6.1 In-scope gaps — HARD, block promotion (12)

| # | Gap | Sweep | Disposition | Proposed remediation (advisory) |
|---|---|---|---|---|
| **G-1** | **`AnalyzeArchitecture` has no row in `effects.actions`** in any of the three `spec_manifest.yaml` trees. It is the only one of the 15 non-stutter actions without one. The manifest's own rule (`spec_manifest.yaml:196-199`) states that an **absent** row claims "unmapped" while an **empty** row claims "performs no distinct effect" — and `TlaSpecDevCli.tla:214-222` states that "each action's `@port` lines mirror its row in `effects.actions`". There is no row to mirror. The epic's one new action shipped without its effect declaration. | 2 | **model it** | Add `AnalyzeArchitecture: [evidence_report]` to `effects.actions` in `specs/current`, `specs/desired_program_model` and (at promotion) `specs/program_model`; or `AnalyzeArchitecture: []` **only if** G-2 is closed by removing `--out`. Plan line: `:285` (AC-01), `:283` (AC-01). |
| **G-2** | **`analyze architecture --out` performs an undeclared `filesystem.write`.** `scripts/analyze_architecture.py:1114-1118`: `out_path.parent.mkdir(parents=True, exist_ok=True); out_path.write_text(rendered)`. The path is **unconstrained** — `--out` is a bare string (`:1162`), so a write can land anywhere, while the nearest candidate port `evidence_report` targets only `**/results/**`. AC-01's own acceptance evidence (`ticket_plan.yaml:315-320`) is six files produced by this path. | 2 | **model it** | Declare `evidence_report` on the new `AnalyzeArchitecture` row and constrain `--out` to resolve under `results/`; or drop `--out` and let callers redirect stdout (the descriptor is already written to stdout at `:1112`). Plan line: `:283`. |
| **G-3** | **`architecture_reflexion.py --out` performs the same undeclared write** at `:2288-2292`, plus the `--baseline` delta payload (`:2222`) rendered into it. Same unconstrained path. | 2 | **model it** | Same remediation as G-2. Plan line: `:378` (AC-02), `:871` (RP-01), `:607` (AC-04). |
| **G-4** | **The model's own annotation is factually false.** `TlaSpecDevCli.tla:649` reads `\* No @port: the scan reads the model and the source tree and prints.` The scan does not only print — G-2 and G-3 are its writes. This is the "honest-in-prose / misleading-in-artifact" class RP-02 was opened for, one level up: the *model* now carries the misleading record. | 2 | **model it** | Replace `:649` with the `@port` line G-1/G-2 create, in the shape `:227`/`:392` already use. Plan line: `:285`. |
| **G-5** | **A stale contradicted record in all three manifests.** `spec_manifest.yaml:73-74` (desired), `:75-76` (current), `:71-72` (program_model) state "the model's **9 variables and 15 actions** live in TlaSpecDevCli.tla". The model has **10 variables and 16 actions** — AC-01 added `architecture_scan` and `AnalyzeArchitecture` and did not update the comment. The plan itself records the correct figures at `:643-644`. Identical class to EV-01-DF-03, which RP-05 was opened to repair. | 2 | **model it** | Update the three comments to 10/16, and add the count to whatever check RP-05 used for `architecture_components.yaml`, so the next variable addition cannot leave it stale. Plan line: `:285`. |
| **G-6** | **Two manifest comments cite plan text that does not exist.** `spec_manifest.yaml:56-61` cites "ticket_plan.yaml known_gaps, amended 2026-07-22" as the authority for the view split being unscoped; `spec_manifest.yaml:124-130` cites "the 2026-07-22 scope amendment" as the authority for case generation being "EXPERIMENTAL surface, deliberately unmodeled". **Neither amendment is in the architectural-coherence plan.** Two shipped model artifacts are justified by a document the epic replaced. | 2 | **model it** | The owner restores the two rulings into `planning_rules.semantic_model_rule` / `service_catalog.known_gaps` (see ESC-1), and the manifest comments cite the new line numbers. Until then G-7 and G-10 have no covering plan line. Plan line: `:285`. |
| **G-7** | **Single view module — the whole External view is unrepresented by construction.** 83 of 93 caller-drivable surface items have no representation and no module in which to have one (§5.2). | 4 | **model it** | Either split `TlaSpecDevCli.tla` into `Internal`/`External` (AC-03 measured 2 of 115,975 partitions meeting all three shipped criteria — `ticket_plan.yaml:558-563`, AC-03-DF-02, with a checked-in reproduction), **or** the owner restores the recorded known-gap line and this becomes an inventory row instead of a gap. It cannot be closed by a per-finding justification. Plan line: `:285`. |
| **G-8** | **The five group subcommands' `incomplete_command` outcome is unrepresented.** `tla_spec_dev.py:56-61` prints `incomplete command: <path>` and **exits 2**; wired at `:416, :458, :486, :608, :703`. `CommandResult` has `accepted`/`reason`/`next` but no state in which a command was *not* dispatched. | 4 | **model it** | Add a single `IncompleteCommand` action setting `result' = CommandResult(FALSE, "incomplete", <next>)` and leaving all other variables unchanged — one action covers all five, and it is exactly the shape `Stutter` already uses. Plan line: `:284`. |
| **G-9** | **The 69 options and 9 positionals are unrepresented**, including six flags that weaken *modeled* guards: `--accept-new` (`:723`), `--allow-open` (`:719`), `--no-promote-current` (`:721`), `--force` (`:428/:443/:471`), `--dry-run` (`:429/:444/:472`), `--validate-only` (`:512`). `CloseTicket`'s guard (`TlaSpecDevCli.tla:619-638`) requires current==desired and spec-unit-tests-passed; `--accept-new` and `--allow-open` bypass those preconditions and the model has no state in which that happened. | 3, 4 | **model it** | Model the guard-weakening flags only — six of 78, not all 78 — as an explicit weakened-close transition, so a close taken under `--accept-new` is a *different state* from one taken under the guard. The remaining 72 are presentation. **Or** the owner restores `PS:101` and this becomes an inventory row. Plan line: `:284`. |
| **G-10** | **Case-module generation is entirely unrepresented, and it is this epic's headline feature.** `scripts/case_modules.py` ships a standalone `main()` unreachable from `tla_spec_dev.py`'s parser, writing a coverage record (`:479-480`) and a JSON report (`:822-823`); `scripts/generate_cases_from_tlc_dump.py` spawns java/TLC (`:115`), `rmtree`s a metadir (`:139`) and writes generated packages (`:881-882`). No action, no port, no CLI subcommand. **CM-01 and RP-03 both closed "ZERO model delta" against surface the model does not contain.** | 1, 2 | **model it** or **change the program** | Either add a `GenerateCases` action with `corpus_process` (spawn) + `spec_tree` (write) + `spec_tree_delete` (the metadir `rmtree`), or move case generation behind an existing modeled command. **Or** the owner restores the 2026-07-22 amendment G-6 names. Plan lines: `:1209` (RP-03), `:208` (CM-01), `:966` (RP-02), `:1210` (RP-03), `:150` (service_catalog). |
| **G-11** | **`scripts/infer_action_params.py:825-826` writes the parameter-recovery audit** (`mkdir` + `write_text`) with no action and no port. RP-02 spent the ticket making that artifact honest about its own corpus; nothing represents its production. | 2 | **model it** | Fold into G-10's `GenerateCases` (the audit is a generation-time artifact) with `evidence_report`. Plan line: `:965` (RP-02). |
| **G-12** | **AC-04's `architecture_delta` ledger member and its four attribution verdicts are unrepresented.** `architecture_scan ∈ {coherent, divergent, unmappable}` (`TlaSpecDevCli.tla:652`) covers the scan, but the delta's outcomes — `code_only`, `unattributable`, `unverified`, `improved`-with-RED-FLAG (`ticket_plan.yaml:655-670`) — are new externally observable results of `analyze architecture --baseline` with no modeled state. The refusals AC-04 shipped are exactly the ones a reader would want the model to guarantee. | 1, 2 | **model it** | Either widen `architecture_scan`'s domain or add a `architecture_delta` variable, and record the state-count cost the way `ticket_plan.yaml:95-110` recorded AC-01's 4.6×. Plan lines: `:606` (AC-04), `:1078` (RP-04), `:607`/`:871`. |

### 6.2 Out-of-scope inventory — does not gate (0)

| # | Surface | Quoted plan line placing it out of scope |
|---|---|---|
| — | **empty** | The architectural-coherence plan contains **no line that places any surface out of scope.** Every candidate — `specs/.history/`, `spec_double_compiler/`, `skill-scripts/`, the 24 unnamed `scripts/*.py` — is therefore an ESCALATION (§0.5), not an inventory row. Step 6 forbids reaching an out-of-scope classification by reasoning rather than by quoting a plan line, and there is nothing to quote. |

### 6.3 Scope escalations — owner amends the plan, once (7)

| # | Row | Plan line that should change | Argument |
|---|---|---|---|
| **ESC-1** | The whole modeled-surface boundary | `ticket_plan.yaml:26` (`semantic_model_rule`) and `:160-162` (`known_gaps`) | Restore, in this plan's own words, the four rulings the predecessor folded in at the previous audit's request (`PS:49-68`, `PS:98-103`): the `generate` limitation, the per-flag/refusal-branch limitation, the single-module view-split limitation, and the harness/toolchain out-of-model amendment. Without them G-7, G-9 and G-10 are hard gaps that the owner has already ruled on once. **The last audit raised this exact escalation (ESC-C2-1) and the fix was reverted by the next plan.** |
| **ESC-2** | The audit's scope basis | `service_catalog:147-162` | Add a representation-scope declaration distinct from `implementation_scope`. As written, 325 example-fixture rows are in scope for `TlaSpecDevCli.tla` and 24 of 34 `scripts/*.py` are unclassifiable. A gate whose scope is an edit-permission list measures the wrong thing in both directions. |
| **ESC-3** | `tests/` (`:210`), `specs/current/tests/` (`:287`), `test_graph/` (`:1272`) — 62 rows | `:26` vs `:210`/`:287`/`:1272` | These are in scope by `implementation_scope` and un-modelable by `semantic_model_rule`. **62 rows have no available disposition.** The owner must say which document wins. |
| **ESC-4** | `spec_manifest.yaml` (three trees) | any `implementation_scope`, or `service_catalog` | Every effect port lives there and no plan line names it. G-1, G-5 and G-6 are filed against `:285` because that is the closest in-scope anchor, which is a workaround, not a classification. |
| **ESC-5** | `specs/.history/**` — 5,402 files | `service_catalog:147-162` | Declare whether sealed history is program surface. It was excluded by stated filter F1 and **not walked**; that exclusion is this auditor's judgment, which Step 0 says it should not be. |
| **ESC-6** | `skill-scripts/install-tlc2.sh:37` | any `implementation_scope`, or `service_catalog` | A real `curl` download on the `BuildSkillCli`/`InstallLocalCli` path, with **no `network.*` port declared anywhere** although the sandbox observes `network.connect` (`effect_conformance.py:106, :775-788`). Unclassifiable as written; would be a hard gap if the plan named the file. |
| **ESC-7** | `spec_double_compiler/**`, `scripts/run_generated_case_adapters.py`, `templates/python/ports.py.j2` | `:496` vs `PS:102` | `PS:102` ruled this set out-of-model as shipped harness plumbing; the current plan's `:496` puts `templates/` **in** scope. The two documents contradict each other on the same files. |

---

## 7. Verdict

- In-scope gaps: **12**
- Out-of-scope inventoried: **0**
- Escalations: **7**
- **Verdict: `incomplete`**

`incomplete` rather than `fail` because the 12 gaps are not the limiting fact
about this report. The limiting facts are: (a) Step 0's HALT conditions are met,
so the scope this gate is supposed to measure against does not exist in usable
form; (b) 187 of 596 Sweep-1 rows — including 24 of the 34 files in `scripts/`,
the program the model represents — could not be classified at all; (c) 5,402
files were excluded by a filter this auditor chose; and (d) 512 of 596 rows were
dispositioned from a path rather than from reading the code (§8.3).

`incomplete` is **not** a `pass`. Per `references/coverage_audit.md`,
"Recording": at workflow-scope close, any verdict other than `pass` — including
`incomplete` — **refuses the close**, because a sweep that did not walk the
surface carries no information about it. **This epic should not promote on this
report.**

The 12 in-scope gaps are hard and independent of the HALT: each is anchored on a
file a plan line names, and each is closed by modeling it or changing the
program. Three of them (G-1, G-4, G-5) are model/manifest desyncs that no oracle
in this toolchain checks, which is the same class the first MF-026 run found.

**A proposed ledger block is written to
`specs/results/coverage-audit-arch-coherence-raw/coverage_audit_ledger_input_proposed.yaml`
as evidence.** It was deliberately **not** applied to
`specs/results/complexity_ledger.json` or `coverage_audit_ledger_input.yaml`:
the dispatching instruction restricts this agent to committing its report and
its evidence, and a gate that edits the ledger it reports into is the kind of
self-clearing this doctrine forbids. **The owner must record the verdict.**

---

## 8. Attestation

This section is more load-bearing than the tables. `prompts/coverage_audit.md`
says so, and after running the procedure I agree.

### 8.1 Row-count reconciliation per sweep

| Sweep | Enumeration command | Raw N | Table rows M | `N == M` |
|---|---|---|---|---|
| 1 — program surface | `git ls-files '*.py' '*.sh' '*.kt' '*.kts' '*.java' '*.j2' \| grep -v '^specs/\.history/' \| sort` | 596 | 596 | ✅ asserted by `cac_ac_classify.py` |
| 2.1 filesystem | `xargs -0 grep -nE '\b(open\|Path\|write_text\|read_text\|write_bytes\|mkdir\|makedirs\|remove\|unlink\|rename\|replace\|copy\|copytree\|rmtree\|tempfile\|mkdtemp\|NamedTemporaryFile)\b'` | 3,909 | 5 groups summing to 3,909 + 54 per-site destructive rows | ✅ asserted |
| 2.2 subprocess | same shape, `\b(subprocess\|Popen\|run\|call\|check_output\|check_call\|system\|execv\|execve\|spawn)\b` | 1,366 | 2 groups summing to 1,366 | ✅ asserted |
| 2.3 network | `\b(socket\|connect\|requests\|urlopen\|urlretrieve\|urllib\|httpx\|aiohttp\|HTTPConnection\|curl\|wget)\b` | 145 | 2 groups summing to 145 | ✅ asserted |
| 2.4 environment | `\b(environ\|getenv\|putenv\|setdefault\|argv\|load_dotenv\|expanduser\|PATH)\b` | 394 | 2 groups summing to 394 | ✅ asserted |
| 2.5 clock | `\b(datetime\|now\|utcnow\|today\|time\|monotonic\|perf_counter\|sleep\|timestamp)\b` | 384 | 2 groups summing to 384 | ✅ asserted |
| 2.6 randomness | `\b(random\|randint\|choice\|shuffle\|sample\|uuid\|uuid4\|secrets\|urandom\|token_hex)\b` | 50 | 2 groups summing to 50 | ✅ asserted |
| 2.7 persistent store | `\b(sqlite3\|psycopg\|pymysql\|redis\|boto3\|engine\|session\|cursor\|execute\|commit)\b` | 107 | 2 groups summing to 107 | ✅ asserted |
| 2.8 JVM/native | `\b(File\|ProcessBuilder\|HttpClient\|getenv\|exec\|Files\|Paths\|Runtime)\b` | 417 | 2 groups summing to 417 | ✅ asserted |
| 3.1 error paths | `\b(except\|raise)\b\|try:` | 1,431 | 5 groups summing to 1,431 | ✅ asserted |
| 3.2 retries | `\b(retry\|retries\|backoff\|attempt\|attempts\|max_tries)\b` | 528 | 2 groups summing to 528 | ✅ asserted |
| 3.3 timeouts | `\b(timeout\|timeouts\|deadline\|expires\|TimeoutError)\b` | 275 | 2 groups summing to 275 | ✅ asserted |
| 3.4 fallbacks | `\b(fallback\|default\|defaults\|ImportError)\b\|or None\|except.*pass` | 314 | 4 groups summing to 314 | ✅ asserted |
| 3.5 concurrency | `\b(thread\|threading\|async\|await\|lock\|Lock\|concurrent\|multiprocessing\|Semaphore\|daemon)\b` | 29 | 2 groups summing to 29 | ✅ asserted |
| 3.6 config branches | `\b(getenv\|environ\|flag\|flags\|enabled\|disabled)\b\|\.get\("\|--no-\|--allow\|--force\|--dry-run` | 1,160 | 4 groups summing to 1,160 | ✅ asserted |
| 4 — external view | `python3 .../cac_ac_external_surface.py` (walks the shipped argparse tree) | 93 | 93 (rows 1-93, banded) | ✅ |

"Asserted" means `cac_ac_classify.py` raises `AssertionError` if any category's
group sizes do not sum to its raw count. The script ran clean. **This is
stronger than a self-report but weaker than an independent inventory** — see 8.6.

Sweep 4's 93 rows are presented in five bands (1-10, 11-15, 16-24, 25-93, plus
the projection row) rather than 93 separate lines, because every row within a
band carries the identical verdict and evidence pointer. The banding is
mechanical and stated; the raw 93 lines are in `sweep4-external-surface.txt`.

### 8.2 What surface did I NOT walk?

**Not "none".** Named precisely:

1. **`specs/.history/**` — 5,402 files** in the language set (4,489 `.py`, plus
   Kotlin/Java under archived Test Graph reports), 9,781 files in total.
   Excluded by stated filter F1, escalated as ESC-5. This is sealed append-only
   history, but *I* decided that, not a plan line.
2. **Non-source tracked files — 6,566 of 12,564.** `.json` (1,236), `.txt`
   (1,170), `.md` (870), `.yaml` (660), `.jsonl` (555), `.toml` (544), `.cfg`
   (513), `.tla` (348), `.gz`, `.jar`, `.png` and others were **not** in any
   sweep. Several are program surface in the relevant sense: `spec_manifest.yaml`
   holds every effect port, `kill_mutants.toml` holds the mutant catalog,
   `case_adapters.toml` holds the adapter bindings, and `*.tla` under
   `examples/**` are the fixture models. G-1/G-5/G-6 were found in
   `spec_manifest.yaml` by targeted reading, **not** by a sweep — so the
   manifest class is under-swept and there may be more of it.
3. **Runtime behavior.** No sweep executed the CLI. Effects were found by
   pattern, not by observation; the effect sandbox has never run against this
   model (`generation_status: planned`).
4. **`references/`, `prompts/`, `templates/*.md`, `SKILL.md`, `NEXT-EPIC.md`** —
   named by plan lines `:211/:288/:495/:496/:497/:498/:608/:785/:1144/:1211/:1212/:1365`
   but carrying no executable surface, so they produced no Sweep-1 rows. Their
   *content* was not audited for coverage claims.

### 8.3 Rows dispositioned from path/name rather than from reading code

**Per-sweep read-vs-inferred, reported because concealing it is the failure:**

| Sweep | Rows | READ | INFERRED | Inferred % |
|---|---|---|---|---|
| 1 — program surface | 596 | **84** | **512** | **86%** |
| 2 — effects (per group) | 25 groups | 25 (each group's membership rule was applied mechanically; representative members read in 8 of 25) | 0 groups, but the *per-site* judgments inside 17 groups are inferred | — |
| 2 — destructive per-site | 54 | 12 | 42 | 78% |
| 3 — behaviors (per group) | 19 groups | 19 rules applied mechanically; representative members read in 6 of 19 | — | — |
| 4 — external view | 93 | 93 (the row set is the parser's own output; the 10 leaf mappings were traced to `tla_spec_dev.py` dispatch functions and to the model's actions) | 0 | 0% |

The 84 Sweep-1 rows I actually read: all 34 `scripts/*.py` (entry points, effect
sites and CLI wiring — `tla_spec_dev.py` in full), the 3 `spec_double_compiler/`
modules, 8 `skill-scripts/`+`scripts/*.sh`, and 39 files opened while tracing
G-1..G-12. **The 512 inferred rows are almost entirely `examples/**` (325),
`tests/` (32), `specs/{current,program_model,desired_program_model}/tests/`
(51), `test_graph/` (13) and `specs/tickets/MF-027/**` (110).** They carry the
default polarity `unrepresented`, which is the correct default but is *not* the
same as a read judgment. **A reader should treat any `unrepresented` verdict
outside `scripts/` as "not shown to be covered", not as "shown to be uncovered".**

This is the known side effect the prompt names: the row-count discipline
prevents silent sampling and creates pressure toward shallow rows. 86% shallow
is what that pressure produced at this surface size, and the number is the
honest artifact.

### 8.4 Rows whose scope I decided by reasoning rather than by a quoted plan line

**187 Sweep-1 rows**, plus the whole of `specs/.history/**`. All are marked
`ESCALATION` in the tables and enumerated in §0.5 / §6.3 — **none is presented
as a classification.** No row anywhere in this report carries `out-of-scope`.

One decision was mine and I am flagging it rather than burying it: **filter F1**
(excluding `specs/.history/`) is a scope decision wearing a shell flag, exactly
what Step 2 warns against. I applied it because a 5,998-row Sweep 1 was not
producible and because no plan line names the tree — but the honest status is
ESC-5, and the owner should rule on it.

### 8.5 Could a reader reproduce this row set from the recorded commands?

**Yes, for the row sets.** Every raw enumeration is committed under
`specs/results/coverage-audit-arch-coherence-raw/`, and
`cac_ac_classify.py` + `cac_ac_external_surface.py` regenerate every table's
rows from those raws with the classification rules as executable code rather
than prose. Re-running them at commit `3467051` reproduces this report's counts
exactly.

**No, for the verdicts.** The `represented`/`partial`/`unrepresented` cell and
the `declared`/`undeclared`/`partial` cell are judgments encoded in
`cac_ac_classify.py::REPRESENTED` and in §3's prose. A reader can check them
against the cited `file:line`; they cannot be derived mechanically. That split
is the intended one (tooling owns enumeration, the agent owns disposition), and
it is stated so nobody mistakes the script for an oracle.

### 8.6 Findings about the prompt itself (required)

Four, in descending order of how much they let me produce a plausible report
without earning it.

1. **Step 0's closure rule is correct and the plan schema it reads cannot
   satisfy it.** `implementation_scope` is defined by the epic workflow as an
   *edit-permission* list; the audit reads it as a *representation* scope. Those
   coincide only by accident. Here they diverged so far that 325 fixture files
   are "in scope" and 24 of 34 `scripts/*.py` are not. **The prompt should say
   which plan key declares representation scope, and HALT if that key is
   absent rather than falling back to `implementation_scope`.** As written it
   invites an auditor to produce a 409-row in-scope table that measures the
   wrong surface, and the row-count discipline makes that table look rigorous.

2. **Step 2's "one row per file" is unbounded and the prompt gives no relief
   valve, unlike Steps 3 and 4.** At 596 rows I could produce the table only by
   generating 86% of it from paths. At 5,998 (unfiltered) I could not have
   produced it at all, and the only escape the prompt offers is a filter —
   which it simultaneously warns is "a scope decision wearing a shell flag".
   **That is a trap: the prompt forces the auditor to make a scope decision it
   forbids the auditor from making.** Steps 3 and 4 grant grouping on stated
   terms; Step 2 should grant the same, with the read-vs-inferred count in §8.3
   as the price.

3. **Nothing in the prompt requires the auditor to sweep non-source files, and
   the highest-value findings here are in one.** G-1, G-5 and G-6 are all in
   `spec_manifest.yaml`. Step 2 says "adapt the glob to the project's
   languages"; a YAML manifest is not a language, so a compliant auditor sweeps
   `*.py` and misses the file where every effect port lives. Given that the
   first MF-026 run also found "three model/manifest desyncs no oracle checks",
   **the manifest is a recurring defect site and the prompt should enumerate it
   explicitly as its own sweep.**

4. **The self-reported `N == M` limit is real, and I narrowed it without
   closing it.** Writing the assertion into `cac_ac_classify.py` means the
   reconciliation fails loudly rather than being claimed — a reviewer can
   `python3 cac_ac_classify.py` and watch it assert. But **I wrote the script,
   I chose the group regexes, and I chose filter F1.** An agent willing to
   write a permissive regex and claim a clean sweep is not stopped by any of
   this. The mechanical inventory tracked as
   [issue #48](https://github.com/haydenrear/tla-spec-dev/issues/48) is still
   the only thing that closes it, and this run is further evidence for it: the
   single most consequential number in this report — 24 of 34 `scripts/*.py`
   unclassifiable — came out of the classifier, not out of my attention.

**One finding about the prompt's own validation status.** The prompt records
run 1 as `INCOMPLETE`, 19 in-scope gaps, 145/160 escalated, and lists the fixes
made in response. Run 2 (close 2, 2026-07-23) reached `PASS` with 0 gaps and
raised ESC-C2-1 — "the successor plan does not restate those rulings in its own
text." **This run found that the next successor plan did the same thing again,
and that the previous fix was reverted.** The escalation mechanism works
exactly as designed and nothing carries its output forward: a scope amendment
lives in one plan file and dies when the epic closes. That is a defect in the
*workflow*, not in this prompt, and it is the reason six of this report's twelve
gaps exist.
