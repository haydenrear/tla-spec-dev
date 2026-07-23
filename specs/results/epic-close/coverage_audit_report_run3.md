# Coverage Audit Report — run 3 (re-verdict at workflow close, post-amendment + CD-09)

- **Epic / workflow:** `complexity-descriptor-epic` (workflow close; CD-01, CD-02, CD-03, CD-09 all done and merged)
- **Scope source:** `specs/desired_program_model/ticket_plan.yaml` (AMENDED 2026-07-22, schedule_revision 2): `semantic_model_rule` lines `520-536`; `service_catalog` lines `550-570`; ticket `implementation_scope` lines `2017-2020` (CD-01), `2094-2096` (CD-02), `2164-2168` (CD-03), `2258-2262` (CD-09)
- **Model audited:** `specs/current/TlaSpecDevCli.tla` @ `195b07d`
- **Date:** `2026-07-22`
- **Verdict:** `FAIL` — 4 in-scope gaps

> This audit checks **completeness of what is modeled**, not fidelity. The four
> oracles are bounded to what is already represented and cannot see this class
> of defect. See `prompts/coverage_audit.md`. Run 2 (FAIL, 7 gaps):
> `specs/results/epic-close/coverage_audit_report.md` — used for targeting only;
> every enumeration below was re-run fresh at 195b07d. Raw sweep outputs:
> `specs/results/epic-close/sweep-raw-run3/`.

**Standing of the run-2 findings under the amendment (verified fresh, not taken
on faith):**

| Run-2 item | Amended-boundary standing | Fresh evidence |
|---|---|---|
| G1 (fitness subsystem unmodeled) | out-of-model by quoted `:530-533` | quoted in §0; `scripts/fitness_functions.py` row inventoried |
| G2 (blocking gate + override in model) | **FIXED by CD-09 — verified in tree** | `RunSpecUnitTests(root, ticket)` TlaSpecDevCli.tla:529 has no override parameter; the guard :529-559 carries no `complexity_gate` condition; every `override` occurrence in the file is commentary documenting its absence (:513-525, :550); `complexity_gate` survives only as recorded advisory fact (:374, :643) with `kill_tests: []` (manifest:222-225) |
| G3 (no case-generation action) | out-of-model by quoted `:525-530` + `:559` | quoted in §0 |
| G4 (dead tlc_process port) | **FIXED by CD-09 — verified in tree** | `tlc_process` absent from declared ports (manifest:153-175); removal rationale recorded at manifest:163-172; `AnalyzeComplexity: [evidence_report]` manifest:184; `scripts/analyze_complexity.py` contains no subprocess import (verified) |
| G5 (11/14 bindings + ValidateTestGraphCli) | **FIXED by CD-09 — verified in tree** | `case_adapters.toml:13-53` binds exactly the 14 @command actions; `ValidateTestGraphCli` gone; `Stutter` deliberately unbound with rationale (toml:3-11); proven both ways by `specs/current/tests/test_tla_spec_dev_binding_reconciliation.py` |
| G6 (silent-degrade guards) | out-of-model by quoted `:530-533` ("silent-degrade guard branches") | quoted in §0 |
| G7 (runner internals) | out-of-model by quoted `:530-533` ("the runner's env re-exec") | quoted in §0 |
| E1–E6 | amendment claims all resolved; **residue found** — see §6.3 | this run's escalations |

---

## 0. Declared scope (quoted verbatim from the amended plan)

```yaml
# specs/desired_program_model/ticket_plan.yaml:520-536 (planning_rules.semantic_model_rule, AMENDED)
  semantic_model_rule: >-
    Do not add test graph nodes, pytest jobs, CI workflow steps, integration
    harnesses, or validation scripts as TLA+ program state/actions. AMENDED
    2026-07-22 (owner, coverage-audit run 2, resolving its scope escalations):
    the modeled program surface is the SHIPPED CLI lifecycle — scaffold, open,
    run spec-unit-tests, analyze (descriptor scan), close. Post-pivot, case
    generation, the corpus gate, effect conformance, and the mutation kill
    test are the EXPERIMENTAL fuzzing surface and are deliberately NOT
    modeled (the 2026-07-21 ship-scanner/drop-fuzzing decision demoted them
    from the product; modeling them would represent surface the product does
    not ship). Advisory tooling internals — fitness-function evaluation
    inside analyze, silent-degrade guard branches, the runner's env re-exec —
    are declared out-of-model as transcription (MF-015 precedent: no
    invariant needs them, no modeled command observes them; adding state for
    them is transcription rather than evidence). Audit gaps G1/G6/G7 are
    reclassified by this amendment; G3 is resolved by the experimental
    demotion; G2/G4/G5 are REAL desyncs fixed by CD-09, not amended away.
```

```yaml
# specs/desired_program_model/ticket_plan.yaml:550-570 (service_catalog, AMENDED)
service_catalog:
  # AMENDED 2026-07-22 (owner, coverage-audit run 2): boundaries restated to
  # the post-pivot product. The audit's escalations E1-E6 are resolved by this
  # amendment plus the amended semantic_model_rule above; its in-scope gaps
  # G2/G4/G5 are fixed by CD-09 (never amended away), G3 by the experimental
  # demotion, G1/G6/G7 by the out-of-model declarations.
  existing_boundaries:
    - tla-spec-dev CLI shipped lifecycle (scaffold/open/run spec-unit-tests/analyze/close) — THE MODELED SURFACE
    - scripts/analyze_complexity.py complexity descriptor + scripts/fitness_functions.py advisory rules (advisory internals out-of-model as transcription)
    - "EXPERIMENTAL, deliberately unmodeled: scripts/generate_cases_from_tlc_dump.py, corpus gate, effect conformance, kill test (the 2026-07-21 pivot)"
    - spec_manifest.yaml / case_adapters.toml schemas
  desired_boundaries:
    - model faithful to the advisory program (no blocking-gate or override representation — CD-09)
    - declared ports match what modeled actions actually spawn (CD-09)
    - case_adapters.toml binds exactly the model's action set (CD-09)
    - complexity-ledger decreases licensed by the validated-refactor basis (CD-09, owner-approved 2026-07-22)
  adapter_boundaries:
    - specs/program_model/production_adapters.py spec-unit adapters
    - test_graph specWorkflow / cliWorkflow graphs
  known_gaps:
    - "This repository's baseline is a single TlaSpecDevCli.tla module without the Internal/External view split that SKILL.md mandates for onboarded projects. Originally recorded as out of scope for this epic. Owner direction 2026-07-18: it is now IN scope but scheduled LAST, as MF-023 at promotion_order 85, after every mechanism ticket has landed. [...] See references/migration.md and tickets/023-decompose-via-dogfooding.md."
```

```yaml
# specs/desired_program_model/ticket_plan.yaml:2017-2020 (CD-01), 2094-2096 (CD-02), 2164-2168 (CD-03), 2258-2262 (CD-09)
    implementation_scope:                                     # CD-01
      - scripts/analyze_complexity.py (remove suggestion machinery; F1 alias resolution; F3 bound honesty)
      - tests/test_analyze_complexity.py (F1 regression test failing pre-fix; F3 coverage)
      - SKILL.md and references/architecture_tractability.md (descriptor is the surface)
    implementation_scope:                                     # CD-02
      - references/complexity_intuition.md (new doc)
      - SKILL.md (wire the refactor-input framing into the workflow)
    implementation_scope:                                     # CD-03
      - scripts/fitness_functions.py (primitives + composition + evaluation; lean)
      - scripts/analyze_complexity.py (load per-project rules; surface fired rules in the report)
      - tests/test_fitness_functions.py
      - SKILL.md and references/fitness_functions.md (how an agent adds rules; advisory semantics)
    implementation_scope:                                     # CD-09
      - specs/current/TlaSpecDevCli.tla + MC.cfg (override removal; advisory-faithful guards; invariants)
      - specs/current/spec_manifest.yaml (ports; justification table rows touched)
      - specs/current/case_adapters.toml + production_adapters.py (binding reconciliation)
      - scripts/complexity_ledger.py + tests/test_complexity_ledger.py (retention basis)
```

| Scope line | Covers |
|---|---|
| `:524-525` ("the modeled program surface is the SHIPPED CLI lifecycle — scaffold, open, run spec-unit-tests, analyze (descriptor scan), close") | the positive, exclusive definition of the modeled surface. Operationalized this run by a stated mechanical rule (§2): a file is lifecycle surface iff reachable from the five shipped subcommands' dispatch in `scripts/tla_spec_dev.py` via imports (:62-203), the runner spawn (:313-339), or the `case_adapters.toml` adapter binding and its imports |
| `:521-522` (first sentence, unamended) | pytest jobs, test-graph nodes, CI steps, integration harnesses, validation scripts — out of the modeled surface |
| `:525-530` + `:559` | case generation, corpus gate, effect conformance, kill test — experimental, deliberately unmodeled |
| `:530-533` | fitness evaluation inside analyze, silent-degrade guard branches, runner env re-exec — out-of-model as transcription |
| `:557` | the CLI lifecycle as existing boundary (still a program description, not a path — run-2 E2's complaint stands textually; the closure rule above is this run's stated operationalization) |
| `:558` | `scripts/analyze_complexity.py`, `scripts/fitness_functions.py` (exact paths) |
| `:560` | `spec_manifest.yaml` / `case_adapters.toml` schemas (bare filenames — run-2 E3 residue; the operative instances are taken as the specs/current pair named by :2260-2261) |
| `:563` | port honesty promise: "declared ports match what modeled actions actually spawn" — **tested fresh in §3.2; found unmet on two paths (gap R3-3)** |
| `:565` | `scripts/complexity_ledger.py` validated-refactor basis (with :2262) |
| `:567` | `specs/program_model/production_adapters.py` (exact path) |
| `:569-570` (known_gaps, retained verbatim from the previous epic) | the Internal/External split — **the quoted text still scopes it to concluded-epic MF-023; see ESC-2** |
| `:2018-2019`, `:2165-2167`, `:2262` | exact-path change surface (scripts + named test files) |
| `:2259-2261` | `specs/current/` model/manifest/bindings/adapters (exact paths) |

**Closure rule applied:** a scope entry naming a FILE scopes that file only; no
entry writes a directory or glob, so no directory closure was granted. The one
adopted reading beyond exact paths: `:524-525` is a **totality** ("the modeled
program surface IS the shipped CLI lifecycle"), so a row provably outside the
lifecycle closure is out-of-scope BY that line. This reading is recorded as the
run's single interpretive step (attestation §8.4); rows where lifecycle
membership is itself ambiguous were ESCALATED, not resolved (11 rows, §6.3).

---

## 1. Model representation index

**Definitions.** Mandated regex → N = 36 (defect: single-space `==` — run-2
finding §8.6 still unfixed in the prompt; it drops the 5 alignment-padded stage
constants at :186-189,:191); corrected
`grep -nE '^[A-Za-z_][A-Za-z0-9_]*(\(.*\))?[[:space:]]+==' specs/current/*.tla`
→ **N = 41** (1 vars + 6 stage constants + 2 set helpers + CommandResult + Init
+ 15 action defs + Next + 13 invariants + Spec; run 2 had 42 with 14
invariants — `SpecUnitTestsRequireAnalyzedGate` was removed by CD-09 and
`RunSpecUnitTests` lost its third parameter).

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
| Action | `AnalyzeComplexity(root)` | `specs/current/TlaSpecDevCli.tla:371` |
| Action | `AnalyzeCorpus(root)` | `specs/current/TlaSpecDevCli.tla:403` |
| Action | `RunEffectConformance(root)` | `specs/current/TlaSpecDevCli.tla:440` |
| Action | `RunKillTest(root)` | `specs/current/TlaSpecDevCli.tla:493` |
| Action | `RunSpecUnitTests(root, ticket)` | `specs/current/TlaSpecDevCli.tla:529` (no override — G2 fixed) |
| Action | `CloseTicket(root, ticket)` | `specs/current/TlaSpecDevCli.tla:584` |
| Action | `Stutter` | `specs/current/TlaSpecDevCli.tla:601` (frame condition, deliberately unbound — toml:8-11) |
| Non-action defs | 13 invariants (`TypeInvariant` :633 … `KillTestVerdictRequiresBudgets` :773), `Init` :200, `Next` :604, `Spec` :776, helpers :173-197 | `specs/current/TlaSpecDevCli.tla` |
| Port | `spec_tree` (filesystem.write `**/specs/**`) | `specs/current/spec_manifest.yaml:154-156` |
| Port | `evidence_report` (filesystem.write `**/results/**`) | `specs/current/spec_manifest.yaml:157-159` |
| Port | `cli_artifact` (filesystem.write `**/.venv/**`) | `specs/current/spec_manifest.yaml:160-162` |
| Port | `test_process` (process.spawn `*pytest*`) | `specs/current/spec_manifest.yaml:173-175` (`tlc_process` REMOVED — G4 fixed, rationale :163-172) |
| Action→port map | **13 of 14 @command actions mapped; `RecordBudgets` absent** (CD09-DF-2, still open) | `specs/current/spec_manifest.yaml:176-189` |
| Binding | 14 bindings = exactly the 14 @command actions (G5 fixed) | `specs/current/case_adapters.toml:13-53` (discovered via `spec_manifest.yaml:191`) |
| Binding | `actions.yml` / `testgraph_bindings.yml` outside examples/ | **none exist** (find returned empty, exit 1) |

**Index desyncs (fresh reads):**

1. `spec_manifest.yaml:110-113` still references `../program_model/Core.tla`,
   `Internal.tla`, `External.tla` — none exist (`ls specs/program_model/*.tla`
   → `TlaSpecDevCli.tla` only). CD09-DF-3, still open → ESC-2.
2. `state_fields: []`, `actions: []`, `ports: {}` at manifest:120-122 while the
   model has 9 variables and 15 actions (MF-026 desync 3, still open).
3. `effects.actions` maps 13 of 14 — `RecordBudgets` has no row (CD09-DF-2,
   still open → ESC-4; not a coverage gap, see §6.3).
4. The `@port TlaSpecDevCliPort.*` annotations and the declared port names
   still have empty intersection (MF-026 desync 2, still open).
5. **New this run:** the amendment text `:526-530` declares case generation,
   corpus gate, effect conformance, and kill test "deliberately NOT modeled",
   but the model retains `AnalyzeCorpus` :403, `RunEffectConformance` :440,
   `RunKillTest` :493, state `corpus_gate`/`effect_conformance`/`kill_test`,
   their bindings (toml:40-47), and the corpus/effect guards inside
   `RunSpecUnitTests` :544-573 — the tree models surface the amendment says is
   unmodeled → ESC-6.

Trees reconciled at 195b07d (verified: `specs/current/TlaSpecDevCli.tla` ==
`specs/program_model/…` == `specs/desired_program_model/…`; case_adapters.toml
likewise) — CD09-DF-4 resolved.

---

## 2. Sweep 1 — Program surface

**Enumeration commands and raw counts:**

```bash
git ls-files '*.py'   | wc -l   # 2191 raw
git ls-files '*.kt'   | wc -l   #  567 raw
git ls-files '*.kts'  | wc -l   #  135 raw
git ls-files '*.java' | wc -l   #  324 raw
git ls-files '*.sh'   | wc -l   #    5 raw
# single filter applied to each: grep -v '^specs/\.history/'
# py 201, kt 84, kts 20, java 48, sh 5  ->  N = 358
```

**Filter statement:** exactly one filter — `specs/.history/**` (the sealed
append-only history tree; 1990 py + 483 kt + 115 kts + 276 java files dropped).
No amended plan line names a `.history` path as surface. `tests/` NOT filtered
(named at :2019/:2167/:2262). Raw lists: `sweep-raw-run3/ca3-raw-*.txt`,
filtered union `sweep-raw-run3/ca3-surface-all.txt`.

**Row-set discipline:** enumerated **N = 358**; table rows **M = 358**; `N == M`: yes.
Classification is mechanical (rules below applied by a recorded script);
dispositions: **in-scope 19 / out-of-scope 328 / ESCALATION 11**.
Verdict totals: represented 5, partial 12, unrepresented 341 (default polarity).

Rules (priority order; each row's plan line is in its own row):
**R1** exact path quoted in §0 → in. **R-ESC** the 11 rows of §6.3 →
escalation. **R3** experimental fuzzing surface per :525-530/:559 (exact path
`generate_cases_from_tlc_dump.py`; name-mapped `corpus_diagnostics`,
`effect_conformance_report`, `kill_test`, `run_kill_test`,
`export_testgraph_cases` — mapping recorded in attestation §8.4) → out.
**R2** per :521-522: a `tests`/`test_graph`/`graph-reports` path component,
basename `test_*.py`/`conftest.py`, or the two `examples/*validation*` entry
scripts → out. **R4** lifecycle closure per :524-525/:557 (membership =
reachable from the five shipped subcommands via dispatch imports
tla_spec_dev.py:62-203, the runner spawn :313-339, or the case_adapters.toml
binding and its imports) → in. **R5** everything else provably outside the
lifecycle closure → out per :524-525 (totality reading, attested §8.4).

| # | Module | In/Out | Plan line | Spec action(s) | Verdict | Evidence |
|---|---|---|---|---|---|---|
| 1 | `examples/distributed_history/ecommerce_backend/__init__.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 2 | `examples/distributed_history/ecommerce_backend/domain.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 3 | `examples/distributed_history/ecommerce_backend/service.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 4 | `examples/distributed_history/scripts/k3d-up.sh` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 5 | `examples/distributed_history/scripts/k8s-deploy.sh` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 6 | `examples/distributed_history/scripts/regenerate_tlc_cases.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 7 | `examples/distributed_history/specs/__init__.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 8 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/__init__.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 9 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/cases.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 10 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/types.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 11 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/validators.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 12 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/__init__.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 13 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/cases.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 14 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/types.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 15 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/validators.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 16 | `examples/distributed_history/specs/program_model/__init__.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 17 | `examples/distributed_history/specs/program_model/adapters.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 18 | `examples/distributed_history/specs/program_model/tests/test_ecommerce_adapters.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 19 | `examples/distributed_history/specs/program_model/tlc_projection.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 20 | `examples/distributed_history/test_graph/build-logic/build.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 21 | `examples/distributed_history/test_graph/build-logic/settings.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 22 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Context.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 23 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Executors.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 24 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/JBangExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 25 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/PlanExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 26 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/TimeoutParser.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 27 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/UvExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 28 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphAssembler.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 29 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphModel.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 30 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/MiniJson.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 31 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/NodeDescribeLoader.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 32 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/InspectionTasks.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 33 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunReportWriter.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 34 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunTestGraphTask.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 35 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/ValidationReportTask.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 36 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/TestGraphSpec.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 37 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/Toolchain.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 38 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphExtension.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 39 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphPlugin.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 40 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationNodeSpec.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 41 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationRuntime.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 42 | `examples/distributed_history/test_graph/build-logic/src/test/kotlin/com/hayden/testgraphsdk/exec/PlanExecutorResumeHarnessTest.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 43 | `examples/distributed_history/test_graph/build.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 44 | `examples/distributed_history/test_graph/sdk/java/build.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 45 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextItem.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 46 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextSerde.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 47 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Json.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 48 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/JsonMapper.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 49 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Node.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 50 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeBody.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 51 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeContext.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 52 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeResult.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 53 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeSpec.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 54 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeStatus.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 55 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ProcessRecord.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 56 | `examples/distributed_history/test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Procs.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 57 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/__init__.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 58 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/context_item.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 59 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/context.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 60 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/node_spec.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 61 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/procs.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 62 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/result.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 63 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/runner.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 64 | `examples/distributed_history/test_graph/settings.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 65 | `examples/distributed_history/test_graph/sources/cleanup_ecommerce.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 66 | `examples/distributed_history/test_graph/sources/collect_evidence.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 67 | `examples/distributed_history/test_graph/sources/deploy_ecommerce.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 68 | `examples/distributed_history/test_graph/sources/run_external_cases.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 69 | `examples/distributed_history/tests/test_ecommerce_backend.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 70 | `examples/run_distributed_history_validation.py` | out | :521-522 (validation scripts) | - | unrepresented | validation entry script; default polarity, not read |
| 71 | `examples/validate_split_desired_workflow.py` | out | :521-522 (validation scripts) | - | unrepresented | validation entry script; default polarity, not read |
| 72 | `examples/validation/ex1_scaffold_only/taskq/taskq.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 73 | `examples/validation/ex1_scaffold_only/taskq/tests/test_taskq.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 74 | `examples/validation/ex3_over_complex/order_hub/order_hub.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 75 | `examples/validation/ex3_over_complex/order_hub/tests/test_order_hub.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 76 | `examples/validation/runs/ex3-run1/artifacts/order_hub_after.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 77 | `scripts/analyze_complexity.py` | in | :558 (existing_boundaries), :2018 (CD-01), :2166 (CD-03) | AnalyzeComplexity | represented | AnalyzeComplexity TlaSpecDevCli.tla:371-401; port map manifest:184; binding case_adapters.toml:37-38. Advisory internals (fitness eval :1194-1203; manifest-degrade :1046-1052) out-of-model per :530-533 [READ] |
| 78 | `scripts/budgets.py` | in | :524-525 (scaffold lifecycle; dispatch tla_spec_dev.py:89,:115; analyze consumer :984) | RecordBudgets | partial | RecordBudgets TlaSpecDevCli.tla:269; budgets block manifest:96-107. UNCOVERED: load/refusal semantics beyond budgets_recorded (refusals grouped under gap R3-1) [grep-level] |
| 79 | `scripts/close_spec_workflow.py` | ESCALATION | no plan line places this row (see 6.3) | - | unrepresented | workflow-close wrapper (imports spec_evolution) not reachable from the shipped CLI dispatch; whether 'the SHIPPED CLI lifecycle' (:524-525) covers standalone wrappers is undeclared. Contains destructive rmtree :49 |
| 80 | `scripts/close_ticket.py` | ESCALATION | no plan line places this row (see 6.3) | - | unrepresented | close wrapper importing the same spec_evolution.create_ticket_history_entry the CLI uses; membership in the shipped lifecycle undeclared |
| 81 | `scripts/close_tickets.py` | ESCALATION | no plan line places this row (see 6.3) | - | unrepresented | batch close (plan :539 forbids ticket agents running it); destructive unlink/rmtree :127,:232; membership undeclared |
| 82 | `scripts/close-spec-workflow.py` | ESCALATION | no plan line places this row (see 6.3) | - | unrepresented | compat shim for close_spec_workflow.py; membership undeclared |
| 83 | `scripts/close-ticket.py` | ESCALATION | no plan line places this row (see 6.3) | - | unrepresented | compat shim for close_ticket.py; membership undeclared |
| 84 | `scripts/complexity_ledger.py` | in | :565 (desired_boundaries), :2262 (CD-09), :524-525 (close lifecycle) | CloseTicket (none for the ledger gate) | partial | ledger write on close falls under CloseTicket spec_tree manifest:189. UNCOVERED: blocking refusal branch, spec_evolution.py:611-627 verdict.rejected -> SystemExit 'no override flag' = gap R3-1 [READ via spec_evolution] |
| 85 | `scripts/corpus_diagnostics.py` | out | :526 ('the corpus gate' - experimental fuzzing surface) | - | unrepresented | experimental fuzzing surface, deliberately unmodeled by the amendment; default polarity, not read |
| 86 | `scripts/effect_conformance_report.py` | out | :527 ('effect conformance' - experimental fuzzing surface) | - | unrepresented | experimental fuzzing surface, deliberately unmodeled by the amendment; default polarity, not read |
| 87 | `scripts/effect_conformance.py` | ESCALATION | no plan line places this row (see 6.3) | - | unrepresented | DUAL: named experimental per :527 ('effect conformance') AND in the shipped run spec-unit-tests closure (runner import :24; manifest:127-129; model represents effect_conformance' at TlaSpecDevCli.tla:559) - conflicting quoted lines, owner must place it (ESC-5) |
| 88 | `scripts/export_testgraph_cases.py` | out | :525-526 (case-generation export; also :521-522 test-graph integration) | - | unrepresented | experimental fuzzing surface, deliberately unmodeled by the amendment; default polarity, not read |
| 89 | `scripts/extract_spec_manifest.py` | in | :524-525 (closure: dispatch :203; analyze :1048; runner :30) | none directly | partial | manifest parsing inside every modeled command; loud parse refusals grouped under gap R3-1; no distinct effect surface [grep-level] |
| 90 | `scripts/fitness_functions.py` | in | named :558/:2165 but declared out-of-model :530-533 | none | unrepresented | the whole file is the fitness-function evaluation :530-532 declares out-of-model as transcription (run-2 G1, reclassified by the amendment) [READ header] |
| 91 | `scripts/generate_cases_from_tlc_dump.py` | out | :559 ('EXPERIMENTAL, deliberately unmodeled: scripts/generate_cases_from_tlc_dump.py...') | - | unrepresented | experimental fuzzing surface, deliberately unmodeled by the amendment; default polarity, not read |
| 92 | `scripts/generate_docs.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 93 | `scripts/generate_python.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 94 | `scripts/infer_action_params.py` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 95 | `scripts/kill_test.py` | out | :527-528 ('the mutation kill test' - experimental fuzzing surface) | - | unrepresented | experimental fuzzing surface, deliberately unmodeled by the amendment; default polarity, not read |
| 96 | `scripts/new_ticket_workflow.py` | in | :524-525 (scaffold workflow/open; dispatch :102,:124) | ScaffoldWorkflow, OpenTicket | represented | ScaffoldWorkflow TlaSpecDevCli.tla:287; OpenTicket :305; spec_tree manifest:180-181; bindings toml:25-29 [grep-level] |
| 97 | `scripts/onboard_program_model.py` | in | :524-525 (scaffold project; dispatch :64) | ScaffoldProject | represented | ScaffoldProject TlaSpecDevCli.tla:248; spec_tree manifest:179. NOTE: the :1188 subprocess.run is template text inside the scaffolded-test heredoc (:1145-1191), not a program effect - corrects run 2's uncovered-spawn note [READ region] |
| 98 | `scripts/run_generated_case_adapters.py` | in | :524-525 (run spec-unit-tests; spawned by tla_spec_dev.py:313-339) | RunSpecUnitTests, RunEffectConformance | partial | RunSpecUnitTests TlaSpecDevCli.tla:529-577; ports manifest:188. Env re-exec :971,:990-998 out-of-model per :531. Parent spawn coverage is gap R3-3 [grep-level + re-verified run-2 citations] |
| 99 | `scripts/run_kill_test.py` | out | :527-528 ('the mutation kill test' - experimental fuzzing surface) | - | unrepresented | experimental fuzzing surface, deliberately unmodeled by the amendment; default polarity, not read |
| 100 | `scripts/run_tlc.sh` | ESCALATION | no plan line places this row (see 6.3) | - | unrepresented | TLC runner invoked by acceptance commands; ':521-522 validation scripts' reading available but unstated; run-2 escalation E1 member the amendment did not place |
| 101 | `scripts/scaffold_spec_workflow.py` | ESCALATION | no plan line places this row (see 6.3) | - | unrepresented | workflow scaffold wrapper; membership undeclared |
| 102 | `scripts/scaffold_spec.py` | ESCALATION | no plan line places this row (see 6.3) | - | unrepresented | tutorial scaffold path (self-described alternative to 'tla-spec-dev scaffold project'); membership undeclared |
| 103 | `scripts/skill_feedback.py` | in | :524-525 (close; spec_evolution.py:19) | CloseTicket | partial | feedback file under spec-root results (skill_feedback.py:94) matches spec_tree '**/specs/**'. UNCOVERED: clock provenance :86 (escalation ESC-7) [READ head] |
| 104 | `scripts/spec_evolution.py` | in | :524-525 (close; dispatch :178) | CloseTicket | partial | CloseTicket TlaSpecDevCli.tla:584-599. UNCOVERED: ledger refusal :611-627 (gap R3-1); destructive deletes :154,:385,:477 (gap R3-2); git spawn :99 via :801 (gap R3-3); history timestamps :770,:883 (ESC-7) [READ regions] |
| 105 | `scripts/spec_paths.py` | in | :524-525 (closure via runner :31) | none | partial | path resolution used inside modeled commands; no distinct behavior/effect surface of its own [INFERRED] |
| 106 | `scripts/start_ticket.py` | ESCALATION | no plan line places this row (see 6.3) | - | unrepresented | open wrapper importing the same scaffold_ticket_directory the CLI uses; membership undeclared |
| 107 | `scripts/testgraph_channels.py` | in | :524-525 (closure via runner :32) | none | unrepresented | channel enforcement for external test-graph bindings; the enforced behavior is test-graph integration surface per :521-522 [INFERRED] |
| 108 | `scripts/tla_spec_dev.py` | in | :557 (existing_boundaries), :524-525 | all 14 @command actions | partial | dispatch :62-203 -> actions TlaSpecDevCli.tla:215-599; port map manifest:176-189. UNCOVERED: runner spawn :313-339,:358 matches no declared port (gap R3-3); flag-variant branches (gap R3-4) [READ] |
| 109 | `skill-scripts/install-tla-spec-dev.sh` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 110 | `skill-scripts/install-tlc2.sh` | out | :524-525 (modeled surface IS the shipped CLI lifecycle; this row is not part of it - closure rule stated in 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 111 | `spec_double_compiler/__init__.py` | in | :524-525 (case runtime of run spec-unit-tests) | RunSpecUnitTests | partial | runtime consumed by generated cases/adapters (manifest:127-129) [INFERRED] |
| 112 | `spec_double_compiler/runtime.py` | in | :524-525 (case runtime of run spec-unit-tests) | RunSpecUnitTests | partial | double-execution engine behind RunSpecUnitTests batches (manifest:127-129) [INFERRED] |
| 113 | `specs/current/adapter_case_runtime.py` | in | :2261 (CD-09 adapters), :524-525 | RunSpecUnitTests | partial | harness shim; :36 spawn drives the CLI under test - harness mechanics under the experimental conformance oracle :526-527 [grep-level] |
| 114 | `specs/current/production_adapters.py` | in | :2261 (CD-09 implementation_scope) | all 14 bound actions | represented | bindings case_adapters.toml:13-53 <-> 14 actions; proven by specs/current/tests/test_tla_spec_dev_binding_reconciliation.py; adapter spawns drive the modeled commands (harness) [grep-level] |
| 115 | `specs/current/tests/test_current_ticket_workflow.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 116 | `specs/current/tests/test_tla_spec_dev_analyze_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 117 | `specs/current/tests/test_tla_spec_dev_binding_reconciliation.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 118 | `specs/current/tests/test_tla_spec_dev_budgets_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 119 | `specs/current/tests/test_tla_spec_dev_case_execution_run.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 120 | `specs/current/tests/test_tla_spec_dev_cli_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 121 | `specs/current/tests/test_tla_spec_dev_close_promotion_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 122 | `specs/current/tests/test_tla_spec_dev_complexity_ledger_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 123 | `specs/current/tests/test_tla_spec_dev_corpus_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 124 | `specs/current/tests/test_tla_spec_dev_effect_conformance_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 125 | `specs/current/tests/test_tla_spec_dev_kill_test_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 126 | `specs/current/tests/test_tla_spec_dev_run_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 127 | `specs/current/tests/test_tla_spec_dev_scaffold_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 128 | `specs/current/tests/test_tla_spec_dev_skill_feedback_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 129 | `specs/current/tests/test_tla_spec_dev_test_graph_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 130 | `specs/current/tests/test_tla_spec_dev_ticket_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 131 | `specs/current/tests/test_tla_spec_dev_update_ticket_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 132 | `specs/desired_program_model/production_adapters.py` | ESCALATION | no plan line places this row (see 6.3) | - | unrepresented | desired-tree adapter copy; :567 names the program_model copy and :2261 the current copy; this copy is placed by no line (run-2 E1 member the amendment did not place) |
| 133 | `specs/desired_program_model/tests/test_current_ticket_workflow.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 134 | `specs/desired_program_model/tests/test_tla_spec_dev_analyze_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 135 | `specs/desired_program_model/tests/test_tla_spec_dev_binding_reconciliation.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 136 | `specs/desired_program_model/tests/test_tla_spec_dev_budgets_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 137 | `specs/desired_program_model/tests/test_tla_spec_dev_case_execution_run.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 138 | `specs/desired_program_model/tests/test_tla_spec_dev_cli_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 139 | `specs/desired_program_model/tests/test_tla_spec_dev_close_promotion_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 140 | `specs/desired_program_model/tests/test_tla_spec_dev_complexity_ledger_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 141 | `specs/desired_program_model/tests/test_tla_spec_dev_corpus_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 142 | `specs/desired_program_model/tests/test_tla_spec_dev_effect_conformance_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 143 | `specs/desired_program_model/tests/test_tla_spec_dev_kill_test_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 144 | `specs/desired_program_model/tests/test_tla_spec_dev_run_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 145 | `specs/desired_program_model/tests/test_tla_spec_dev_scaffold_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 146 | `specs/desired_program_model/tests/test_tla_spec_dev_skill_feedback_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 147 | `specs/desired_program_model/tests/test_tla_spec_dev_test_graph_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 148 | `specs/desired_program_model/tests/test_tla_spec_dev_ticket_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 149 | `specs/desired_program_model/tests/test_tla_spec_dev_update_ticket_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 150 | `specs/program_model/adapter_case_runtime.py` | in | :567 sibling (imported by production_adapters.py:23) | RunSpecUnitTests | partial | identical role to the specs/current copy [INFERRED] |
| 151 | `specs/program_model/production_adapters.py` | in | :567 (adapter_boundaries) | all 14 bound actions | represented | reconciled binding set; diff-verified identical to specs/current copy this run [grep-level] |
| 152 | `specs/program_model/tests/test_current_ticket_workflow.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 153 | `specs/program_model/tests/test_tla_spec_dev_analyze_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 154 | `specs/program_model/tests/test_tla_spec_dev_binding_reconciliation.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 155 | `specs/program_model/tests/test_tla_spec_dev_budgets_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 156 | `specs/program_model/tests/test_tla_spec_dev_case_execution_run.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 157 | `specs/program_model/tests/test_tla_spec_dev_cli_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 158 | `specs/program_model/tests/test_tla_spec_dev_close_promotion_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 159 | `specs/program_model/tests/test_tla_spec_dev_complexity_ledger_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 160 | `specs/program_model/tests/test_tla_spec_dev_corpus_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 161 | `specs/program_model/tests/test_tla_spec_dev_effect_conformance_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 162 | `specs/program_model/tests/test_tla_spec_dev_kill_test_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 163 | `specs/program_model/tests/test_tla_spec_dev_run_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 164 | `specs/program_model/tests/test_tla_spec_dev_scaffold_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 165 | `specs/program_model/tests/test_tla_spec_dev_skill_feedback_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 166 | `specs/program_model/tests/test_tla_spec_dev_test_graph_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 167 | `specs/program_model/tests/test_tla_spec_dev_ticket_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 168 | `specs/program_model/tests/test_tla_spec_dev_update_ticket_adapter.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 169 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/build.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 170 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/settings.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 171 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Context.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 172 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Executors.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 173 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/JBangExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 174 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/PlanExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 175 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/TimeoutParser.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 176 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/UvExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 177 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphAssembler.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 178 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphModel.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 179 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/MiniJson.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 180 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/NodeDescribeLoader.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 181 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/InspectionTasks.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 182 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunReportWriter.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 183 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunTestGraphTask.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 184 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/ValidationReportTask.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 185 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/TestGraphSpec.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 186 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/Toolchain.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 187 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphExtension.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 188 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphPlugin.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 189 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationNodeSpec.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 190 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationRuntime.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 191 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/test/kotlin/com/hayden/testgraphsdk/exec/PlanExecutorResumeHarnessTest.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 192 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 193 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/build.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 194 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextItem.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 195 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextSerde.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 196 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Json.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 197 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/JsonMapper.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 198 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Node.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 199 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeBody.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 200 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeContext.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 201 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeResult.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 202 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeSpec.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 203 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeStatus.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 204 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ProcessRecord.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 205 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Procs.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 206 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/__init__.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 207 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/context_item.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 208 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/context.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 209 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/node_spec.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 210 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/procs.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 211 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/result.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 212 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/runner.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 213 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/settings.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 214 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_cleanup.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 215 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_close_ticket.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 216 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_complete_ticket.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 217 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_create_repo.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 218 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_failure_cleanup_probe.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 219 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_force_failure.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 220 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_spec_units.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 221 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/spec_workflow_start_ticket.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 222 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/tla_spec_dev_cli_help.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 223 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sources/tla_spec_dev_cli_install.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 224 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/build.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 225 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/settings.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 226 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Context.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 227 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Executors.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 228 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/JBangExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 229 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/PlanExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 230 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/TimeoutParser.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 231 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/UvExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 232 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphAssembler.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 233 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphModel.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 234 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/MiniJson.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 235 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/NodeDescribeLoader.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 236 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/InspectionTasks.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 237 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunReportWriter.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 238 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunTestGraphTask.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 239 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/ValidationReportTask.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 240 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/TestGraphSpec.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 241 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/Toolchain.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 242 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphExtension.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 243 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphPlugin.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 244 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationNodeSpec.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 245 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationRuntime.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 246 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/test/kotlin/com/hayden/testgraphsdk/exec/PlanExecutorResumeHarnessTest.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 247 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 248 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/build.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 249 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextItem.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 250 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextSerde.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 251 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Json.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 252 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/JsonMapper.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 253 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Node.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 254 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeBody.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 255 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeContext.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 256 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeResult.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 257 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeSpec.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 258 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeStatus.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 259 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ProcessRecord.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 260 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Procs.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 261 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/__init__.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 262 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/context_item.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 263 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/context.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 264 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/node_spec.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 265 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/procs.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 266 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/result.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 267 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/runner.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 268 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/settings.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 269 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_cleanup.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 270 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_close_ticket.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 271 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_complete_ticket.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 272 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_create_repo.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 273 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_failure_cleanup_probe.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 274 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_force_failure.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 275 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_spec_units.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 276 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/spec_workflow_start_ticket.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 277 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/tla_spec_dev_cli_help.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 278 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sources/tla_spec_dev_cli_install.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 279 | `test_graph/build-logic/build.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 280 | `test_graph/build-logic/settings.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 281 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Context.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 282 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Executors.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 283 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/JBangExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 284 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/PlanExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 285 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/TimeoutParser.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 286 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/UvExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 287 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphAssembler.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 288 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphModel.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 289 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/MiniJson.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 290 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/NodeDescribeLoader.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 291 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/InspectionTasks.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 292 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunReportWriter.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 293 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunTestGraphTask.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 294 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/ValidationReportTask.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 295 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/TestGraphSpec.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 296 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/Toolchain.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 297 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphExtension.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 298 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphPlugin.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 299 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationNodeSpec.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 300 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationRuntime.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 301 | `test_graph/build-logic/src/test/kotlin/com/hayden/testgraphsdk/exec/PlanExecutorResumeHarnessTest.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 302 | `test_graph/build.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 303 | `test_graph/sdk/java/build.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 304 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextItem.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 305 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ContextSerde.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 306 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Json.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 307 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/JsonMapper.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 308 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Node.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 309 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeBody.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 310 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeContext.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 311 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeResult.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 312 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeSpec.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 313 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/NodeStatus.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 314 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/ProcessRecord.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 315 | `test_graph/sdk/java/src/main/java/com/hayden/testgraphsdk/sdk/Procs.java` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 316 | `test_graph/sdk/python/src/testgraphsdk/__init__.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 317 | `test_graph/sdk/python/src/testgraphsdk/context_item.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 318 | `test_graph/sdk/python/src/testgraphsdk/context.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 319 | `test_graph/sdk/python/src/testgraphsdk/node_spec.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 320 | `test_graph/sdk/python/src/testgraphsdk/procs.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 321 | `test_graph/sdk/python/src/testgraphsdk/result.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 322 | `test_graph/sdk/python/src/testgraphsdk/runner.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 323 | `test_graph/settings.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 324 | `test_graph/sources/spec_workflow_cleanup.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 325 | `test_graph/sources/spec_workflow_close_ticket.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 326 | `test_graph/sources/spec_workflow_complete_ticket.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 327 | `test_graph/sources/spec_workflow_create_repo.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 328 | `test_graph/sources/spec_workflow_failure_cleanup_probe.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 329 | `test_graph/sources/spec_workflow_force_failure.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 330 | `test_graph/sources/spec_workflow_spec_units.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 331 | `test_graph/sources/spec_workflow_start_ticket.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 332 | `test_graph/sources/tla_spec_dev_cli_help.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 333 | `test_graph/sources/tla_spec_dev_cli_install.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 334 | `tests/conftest.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 335 | `tests/corpus_fixtures.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 336 | `tests/effect_adapter_fixtures.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 337 | `tests/test_analyze_complexity.py` | out | :521 (pytest jobs); named change surface at :2019 | - | unrepresented | pytest job; in scope as change surface only; default polarity, not read |
| 338 | `tests/test_budgets.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 339 | `tests/test_case_adapter_runtime.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 340 | `tests/test_complexity_ledger.py` | out | :521 (pytest jobs); named change surface at :2262 | - | unrepresented | pytest job; in scope as change surface only; default polarity, not read |
| 341 | `tests/test_corpus_diagnostics.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 342 | `tests/test_effect_conformance_cli.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 343 | `tests/test_effect_conformance_runner.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 344 | `tests/test_effect_conformance.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 345 | `tests/test_export_testgraph_cases.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 346 | `tests/test_extract_spec_manifest.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 347 | `tests/test_fitness_functions.py` | out | :521 (pytest jobs); named change surface at :2167 | - | unrepresented | pytest job; in scope as change surface only; default polarity, not read |
| 348 | `tests/test_generate_cases_from_tlc_dump.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 349 | `tests/test_infer_action_params.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 350 | `tests/test_kill_test.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 351 | `tests/test_new_ticket_workflow.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 352 | `tests/test_onboard_program_model.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 353 | `tests/test_promotion_preserves_current.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 354 | `tests/test_scaffold_spec_views.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 355 | `tests/test_skill_feedback.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 356 | `tests/test_spec_yaml_valid.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 357 | `tests/test_testgraph_channels.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 358 | `tests/test_tla_spec_dev_cli.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |

Close: `enumerated N = 358, table rows M = 358, N == M`.

---

## 3. Sweep 2 — Effects, by category

All commands ran over the full Sweep-1 surface
(`xargs /usr/bin/grep -nE <pattern> /dev/null < sweep-raw-run3/ca3-surface-all.txt`),
never a hardcoded subdirectory. Raw outputs: `sweep-raw-run3/<category>.txt`.
Partition rule (every raw hit in exactly one group, sums machine-verified):
by path area — `lifecycle-scripts` (the 14 R4 files), `other-scripts`,
`adapters` (production_adapters/adapter_case_runtime copies), `prod-runtime`
(spec_double_compiler), `repo-tests` (tests/), `spec-tests` (specs/**/tests/),
`testgraph` (test_graph|graph-reports component), `examples`, `skill-scripts`.
Areas out per :521-522 / :524-525 / :525-530 are dispositioned as groups
(inventory); in-scope areas are collapsed to real primitive sites with the
stated rule and dispositioned per-site.

### 3.1 Filesystem — raw `2653`, groups `9` (sum 2653)

| # | Group (area) | Raw | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | lifecycle-scripts | 442 | in | :524-525 | spec_tree / evidence_report (manifest:154-159) | `declared` for the scaffold/open/analyze/close/run write surface (writes land under `**/specs/**` and `**/results/**`); destructive subset is NOT declared — see 3.1a |
| 2 | adapters | 465 | in | :567/:2261 | spec_tree via exercised actions | `declared` (harness writes under spec tree/work dirs during modeled-action cases) |
| 3 | prod-runtime | 6 | in | :524-525 | n/a | no write primitive among hits (dataclass/Path plumbing) — `declared`-n/a |
| 4 | other-scripts | 227 | out/ESC | :524-525 / §6.3 | — | inventory; wrapper deletes listed per-site in 3.1a |
| 5 | repo-tests | 688 | out | :521 | — | inventory |
| 6 | spec-tests | 321 | out | :521 | — | inventory |
| 7 | testgraph | 444 | out | :521-522 | — | inventory |
| 8 | examples | 58 | out | :524-525 | — | inventory |
| 9 | skill-scripts | 2 | out | :524-525 | — | inventory (bash runtime — unobservable ≠ clean, noted) |

### 3.1a Destructive filesystem effects — per-site, never grouped (raw 26 primitive-pattern lines, 23 real sites, 3 discards)

Collapse rule: destructive primitive = `shutil.rmtree|\.unlink\(|os\.remove\(`;
discards (re-derivable from `sweep-raw-run3/filesystem.txt`): 2 docstring/prose
(`tests/test_promotion_preserves_current.py:4`, `tests/test_skill_feedback.py:229`)
and 1 sandbox patch-definition, not a delete (`scripts/effect_conformance.py:692`).

| # | Site | Effect | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `scripts/spec_evolution.py:154` (via :707, ticket close; :851 workflow close) | rmtree of TLC `states/` dirs | in | :524-525 (close) | CloseTicket → [spec_tree] (filesystem.write only) | **`undeclared` — gap R3-2** |
| 2 | `scripts/spec_evolution.py:385` (replace_tree, via promote :528) | rmtree of `current/` before promotion | in | :524-525 (close) | same | **`undeclared` — gap R3-2** |
| 3 | `scripts/spec_evolution.py:477` | unlink of seeded paths dropped by ticket | in | :524-525 (close) | same | **`undeclared` — gap R3-2** |
| 4 | `scripts/close_spec_workflow.py:49` | rmtree (workflow snapshot cleanup) | ESC | §6.3 ESC-3 | — | escalated with its row |
| 5 | `scripts/close_tickets.py:127` | unlink | ESC | §6.3 ESC-3 | — | escalated with its row |
| 6 | `scripts/close_tickets.py:232` | rmtree | ESC | §6.3 ESC-3 | — | escalated with its row |
| 7 | `scripts/generate_cases_from_tlc_dump.py:97` | rmtree metadir | out | :559 | — | inventory (experimental) |
| 8-10 | `examples/…/regenerate_tlc_cases.py:51`, `examples/run_distributed_history_validation.py:400,:402` | rmtree | out | :524-525 / :521-522 | — | inventory |
| 11-16 | `specs/tickets/MF-027/…/graph-reports/…` ×6 (cleanup/create_repo/failure_cleanup_probe ×2 trees) | rmtree | out | :521-522 | — | inventory (archived evidence copies) |
| 17-19 | `test_graph/sources/spec_workflow_{cleanup,create_repo,failure_cleanup_probe}.py` | rmtree | out | :521-522 | — | inventory |
| 20-23 | `tests/test_effect_conformance.py:129,:824`, `tests/test_kill_test.py:940`, `tests/test_new_ticket_workflow.py:201` | unlink/os.remove in tmp fixtures | out | :521 | — | inventory |

### 3.2 Subprocess — raw `1113`, collapsed `5` real spawn sites in in-scope areas, rule: keep `subprocess\.(run|Popen|check_output|check_call|call)\(|os\.system\(|os\.exec\w*\(` in lifecycle/adapters/prod-runtime areas; area groups inventory the rest (testgraph 487, repo-tests 135, spec-tests 75, other-scripts 67, examples 35, skill-scripts 1 — out per :521-522/:524-525/§6.3; adapter-copy sites ×11 per copy are the harness driving the modeled CLI, see below)

> A `process.spawn` port declares the spawn, not what the child did.

| # | Site | Effect | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `scripts/tla_spec_dev.py:358` executing the `-m pytest` command (:296-303) | spawns pytest for spec-unit dirs | in | :524-525 (run) | test_process `*pytest*` (manifest:173-175, :188) | `declared` |
| 2 | `scripts/tla_spec_dev.py:358` executing the runner command (:313-339, `python scripts/run_generated_case_adapters.py …`) | spawns the case runner | in | :524-525 (run); tested against :563 | **no port matches** (`*pytest*` does not match the command line) | **`undeclared` — gap R3-3** |
| 3 | `scripts/spec_evolution.py:99` (via git_metadata :801 ticket close, :903 workflow close) | spawns `git rev-parse…` for history provenance | in | :524-525 (close); tested against :563 | **none declared for CloseTicket** | **`undeclared` — gap R3-3** (the fail-open branch on git error is out-of-model per :531; the spawn is not) |
| 4 | `scripts/run_generated_case_adapters.py:992,:998` | batch env re-exec of itself | in | :531 | — | inventory — quoted out-of-model line covers the re-exec |
| 5 | `scripts/onboard_program_model.py:1188` | none — template text inside the scaffolded-test heredoc (:1145-1191) | in | :524-525 | n/a | not an effect site (READ; corrects run-2 row 57) |
| grp | `specs/{current,program_model}/production_adapters.py` ×11 sites each (:258-:1770), `adapter_case_runtime.py:36` ×2 | harness spawns of the CLI under test | in | :567/:2261 | children ARE the modeled commands; observed-vs-declared checking is the experimental oracle per :526-527 | `partial` (harness mechanics; child effects covered by the actions' own rows) |
| grp | `specs/desired_program_model/production_adapters.py` ×11 | same, unplaced copy | ESC | §6.3 ESC-3 | — | escalated with its row |

### 3.3 Network — raw `60`, collapsed `0` real sites in in-scope areas, rule: keep lines invoking a network primitive (`urlopen|socket\.socket|\.connect\(|curl|wget`); in-scope-area hits are all the sandbox's own patch/observation code (`scripts/effect_conformance.py:556-788` — it observes connects, performs none) or prose (`onboard_program_model.py:215,:1062`); real connects live in examples (21), testgraph (16), skill-scripts curl (3), repo-tests (6) — out per :521-522/:524-525, bash sites noted unobservable

### 3.4 Environment — raw `317`, collapsed `3` real accessor sites in in-scope areas, rule: keep `os\.environ|getenv|expanduser` accessor calls; discard `argv`, dict-`setdefault`, prose

| # | Site | Effect | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `scripts/tla_spec_dev.py:271` (`os.environ.copy()` → child env) | env pass-through to spec-unit children | in | :524-525 | no env port type exists | inventory: input surface of RunSpecUnitTests children; behavior branch is the runner's env contract, out per :531 |
| 2 | `scripts/run_generated_case_adapters.py:971` (`SPEC_DOUBLE_BATCH_REEXEC` read) | re-exec guard | in | :531 | — | inventory (quoted out-of-model) |
| 3 | `scripts/run_generated_case_adapters.py:990` (`os.environ.copy()`) | re-exec env | in | :531 | — | inventory (quoted out-of-model) |

Area groups (out): testgraph 248, examples 25, adapters 12 (env plumbing in harness), repo-tests 10, other-scripts 5 — per :521-522/:524-525/§6.3.

### 3.5 Clock — raw `277`, collapsed `4` real sites in in-scope areas, rule: keep `datetime.now|time\.time|monotonic|perf_counter|sleep|timestamp()` calls; discard prose/identifier matches

| # | Site | Effect | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `scripts/spec_evolution.py:770` | history entry `created_at_utc` | in | :524-525 (close) | no clock port type exists | `undeclared`-unobservable; provenance transcription → ESC-7 (owner: extend :530-533 or model time) |
| 2 | `scripts/spec_evolution.py:883` | workflow entry timestamp | in | same | same | same → ESC-7 |
| 3 | `scripts/complexity_ledger.py:775` | ledger `recorded_at_utc` | in | :565/:2262 | same | same → ESC-7 |
| 4 | `scripts/skill_feedback.py:86` | feedback entry timestamp | in | :524-525 (close) | same | same → ESC-7 |

Area groups (out): testgraph 223 (timers/sleeps), examples 18, repo-tests 10, adapters 8, other-scripts 2 — per :521-522/:524-525.

### 3.6 Randomness — raw `5`, collapsed `0`, rule: all hits are the words `random`/`sample`/`choice` in comments/docstrings (`fitness_functions.py:228`, `repo-tests ×3`, `other-scripts ×1`); no randomness primitive is called anywhere in the enumerated surface

### 3.7 Persistent store — raw `87`, collapsed `0` real users in in-scope areas, rule: a real store effect requires a DB-module import; the in-scope-area hits are `execute`/`commit` as identifiers or git-commit prose (`spec_evolution.py:241-274` renders commit RECOMMENDATIONS, spawns nothing new); real store usage lives in testgraph (43) and examples (32) — out per :521-522/:524-525

---

## 4. Sweep 3 — Behaviors

Commands ran over the full surface (raw files `sweep-raw-run3/behaviors_*.txt`);
the prompt's literal Step-4 commands hardcode `scripts/ spec_double_compiler/`
— followed Step 3's own warning instead (run-2 attestation finding, still
unfixed in the prompt). Partition rule: same area groups as §3.

### 4.1 Error paths — raw `872`, groups `8` by area (lifecycle 238, testgraph 187, other-scripts 147, repo-tests 102, adapters 84, examples 65, spec-tests 36, prod-runtime 13); lifecycle hits sub-grouped by failure semantics (rule: what the failure DOES to the command outcome)

| # | Behavior | Trigger | In/Out | Plan line | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|
| 1 | **Loud refusal: complexity-ledger standing objective refuses the close** ("There is no override flag") | `spec_evolution.py:611-627` (`verdict.rejected` → SystemExit), reached from every shipped `close ticket`/`close workflow` (:689/:835) | in | :524-525 (close), :565 | CloseTicket :584-599 — result is unconditionally `CommandResult(TRUE,…)`; **no refusal branch exists in the model** | **unrepresented — gap R3-1** |
| 2 | Loud refusals: input/state validation across lifecycle commands (missing plan :180, non-mapping plan :183-185, unknown ticket :224, ticket not closed :658, open tickets :830, existing history entry :704/:848, missing model :584, ledger input errors :593) | `spec_evolution.py`, `extract_spec_manifest.py`, scaffold/open guards | in | :524-525 | model represents refusal verdicts ONLY for RunSpecUnitTests gates (:564-573); other commands model success only | **unrepresented — gap R3-1** (grouped: same semantics — command refuses, tree untouched) |
| 3 | Silent-degrade guards (analyze manifest-degrade `analyze_complexity.py:1046-1052`; fitness rules-doc errors `fitness_functions.py:284-295`; git fail-open `spec_evolution.py:99-101`) | absent/broken input | in | **:530-533 (quoted out-of-model)** | — | inventory (run-2 G6, reclassified) |
| 4 | Sandbox observation/error plumbing | `effect_conformance.py` | ESC | §6.3 ESC-5 | — | escalated with its file |
| 5 | Experimental-surface error paths | corpus/kill/effect/generation scripts | out | :525-530/:559 | — | inventory |
| 6 | Test/harness error paths (repo-tests, spec-tests, adapters raise-for-assert) | — | out/in-harness | :521 | — | inventory |
| 7 | Testgraph/examples error paths | — | out | :521-522/:524-525 | — | inventory |
| 8 | prod-runtime case-failure propagation (13 hits) | `spec_double_compiler/runtime.py` | in | :524-525 | case failure surfaces as RunSpecUnitTests verdict (TlaSpecDevCli.tla:560-573) | represented (verdict-carrying) |

### 4.2 Retries — raw `128`, real retry loops in in-scope areas: `0` (lifecycle hits: none; all loop-shaped retry lives in testgraph wait-for-ready polls (104) and examples (8) — out per :521-522/:524-525)

### 4.3 Timeouts — raw `273`, real sites in in-scope areas: `0` (single lifecycle hit `budgets.py:41` is the `tlc_seconds` doc string — the budget value itself gates TLC runs on the experimental generation path, out per :525-526; testgraph 236 out per :521-522)

### 4.4 Fallbacks — raw `456`, groups `7` by area (lifecycle 139, testgraph 131, other-scripts 68, repo-tests 52, adapters 32, spec-tests 30, examples 4)

> Lifecycle sub-analysis: the silent-degrade members (the recurring "guard that
> silently passes when its input is absent") are exactly the class the
> amendment's `:530-533` places out-of-model — analyze manifest-degrade
> :1046-1052, fitness advisory-error path :284-295, git fail-open :99-101 —
> inventory per the quoted line. Loud fail-on-missing members (budgets block
> must fail per MF-024) are refusal semantics → grouped under gap R3-1.
> Remaining hits are `default=` argparse plumbing and dict fallbacks
> (transcription-level, no outcome change; re-derivable from raw).

### 4.5 Concurrency / interleaving — raw `331`, real concurrency primitives in in-scope areas: `0` (lifecycle hits are prose — "await" in scaffold docstrings `onboard_program_model.py:660`, "synchronized" template text; real parallelism lives in test_graph Kotlin executors and repo-test fixtures — out per :521-522/:521)

### 4.6 Config-driven branches — raw `763`, groups `8` by area (lifecycle 220, adapters 156, testgraph 142, other-scripts 116, examples 61, repo-tests 50, spec-tests 15, prod-runtime 3); lifecycle sub-grouped by rule: flags that alter or skip modeled semantics vs plumbing

| # | Behavior | Trigger | In/Out | Plan line | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|
| 1 | **`close --accept-new`: skips the current==desired check and overwrites current/ from desired/** (a guard-disabling flag — the doctrine's highest-risk class; promotion_rule :539 forbids ticket agents using it, but it ships) | `tla_spec_dev.py:651-655` → `spec_evolution` | in | :524-525 (close) | CloseTicket :584-599 models one close semantics, no variant | **unrepresented — gap R3-4** |
| 2 | `close --allow-open` (close a non-done ticket), `--no-promote-current` (skip promotion), `--workflow-name`/`--entry-name` overrides | `tla_spec_dev.py:645-650`, spec_evolution :658 guard bypass | in | :524-525 | same | **unrepresented — gap R3-4** |
| 3 | `run spec-unit-tests --validate-only` (skip execution), `--label/--case/--limit` (subset selection), `--no-batch` | `tla_spec_dev.py:471-506` | in | :524-525 (run) | RunSpecUnitTests :529-577 models the full batch verdict only | **unrepresented — gap R3-4** (grouped) |
| 4 | `scaffold/open --force/--dry-run` (overwrite vs no-write variants of the scaffold effect) | `tla_spec_dev.py:401-458` | in | :524-525 | Scaffold*/OpenTicket model the write unconditionally | **unrepresented — gap R3-4** (grouped) |
| 5 | Runner env/batch config (`SPEC_DOUBLE_BATCH_REEXEC`, `--python`) | runner :971-998 | in | **:531 (quoted out-of-model)** | — | inventory |
| 6 | Fitness rules presence/absence branch | `analyze_complexity.py:1194-1203` | in | **:530-532 (quoted out-of-model)** | — | inventory |
| 7 | Experimental-surface flags (corpus/kill/effect/generation) | — | out | :525-530/:559 | — | inventory |
| 8 | Harness/testgraph/examples/other-scripts config | — | out/ESC | :521-522/:524-525/§6.3 | — | inventory |

---

## 5. Sweep 4 — Views, reported separately

Enumeration: `ls specs/current/*.tla` → 1 module (`TlaSpecDevCli.tla`);
`specs/program_model/*.tla` → 1; `Internal.tla`/`External.tla`/`Core.tla`
referenced at manifest:110-113 — none exist.

### 5.1 Internal — verdict: `unrepresented by construction (no Internal view module)`

| Surface item | Verdict | Evidence |
|---|---|---|
| Component decomposition, internal interleaving of the CLI's scripts | unrepresented by construction | single flat module; no component boundaries beyond the one-module `TlaSpecDevCliPort` component (manifest:152) |

### 5.2 External — verdict: `unrepresented by construction (no External view module)`

| Surface item | Verdict | Evidence |
|---|---|---|
| Public input surface + observable projection as a distinct view; channel-typed Test Graph bindings | unrepresented by construction | no External.tla; `testgraph_bindings.yml` absent outside examples/ (§1 find) |

Not reported as "N/A — single module": the whole of both views' surface is
unrepresented by construction. **Scope standing:** the only plan line touching
this is the retained known_gaps text `:569-570`, which scopes the split to
MF-023 of the CONCLUDED epic (closed 2026-07-21 as dogfooding/docs without
producing the views). The amendment claims E1-E6 resolved (E4 was exactly this
question) but did not update the text → ESC-2, not a classifiable in-scope gap
and not a classifiable out-of-scope inventory row. The owner must place it.

---

## 6. Dispositions

### 6.1 In-scope gaps — HARD, block promotion

| # | Gap | Sweep | Disposition | Proposed remediation (advisory) |
|---|---|---|---|---|
| R3-1 | **Refusal branches of shipped lifecycle commands are unrepresented.** The model's own style models gate refusals for RunSpecUnitTests (result FALSE on gaps/fail :564-573), but every other lifecycle action — including CloseTicket, whose shipped path contains the complexity-ledger standing-objective refusal with "no override flag" (spec_evolution.py:611-627) and eight loud validation refusals — carries an unconditionally-TRUE result (CloseTicket :593). The ledger refusal is a shipped, owner-designed gate (:565, exercised by CD-09's own close) invisible to all four oracles. | 3 (error paths) | model it | Add a refusal result branch to CloseTicket (ledger verdict as the guard's observable outcome, mirroring corpus_gate/effect_conformance style), or declare command-refusal semantics out-of-model in :530-533 — one reviewable owner line, not per-finding waivers. |
| R3-2 | **CloseTicket performs destructive deletes with no `filesystem.delete` port.** Three sites on the shipped close path: states-dir rmtree (spec_evolution.py:154 via :707/:851), current/ rmtree before promotion (:385 via :528), seeded-path unlink (:477). The schema distinguishes filesystem.delete (manifest:145-147); CloseTicket declares [spec_tree] filesystem.write only (manifest:189). The promotion rmtree is the exact mechanism of the GitHub #22 data-loss defect this repo already shipped once. | 2 (destructive, per-site) | change the program (declare the port) | Declare a `spec_tree_delete` (filesystem.delete `**/specs/**`) port on CloseTicket — or narrow the deletes and declare what remains. Destructive sites are never grouped; all three are named. |
| R3-3 | **Declared ports do not match what modeled actions actually spawn — the amended `:563` boundary is unmet on two paths.** (a) RunSpecUnitTests' shipped dispatch spawns the case runner (`python scripts/run_generated_case_adapters.py …`, tla_spec_dev.py:313-339,:358) — matches no port (`test_process` is `*pytest*`; only the `-m pytest` child :296-303 matches). (b) CloseTicket spawns `git rev-parse…` (spec_evolution.py:99 via :801/:903) — CloseTicket declares no process.spawn at all. | 2 (subprocess) | change the program (declare/retarget the ports) | Widen test_process's target to cover the runner spawn (or add a `runner_process` port), and declare a `git_metadata` process.spawn for CloseTicket — or drop the git call. |
| R3-4 | **Flag-variant branches of modeled commands are unrepresented**, including guard-disabling members: `close --accept-new` skips the current==desired check (the class :539 forbids agents to use — shipped anyway), `--allow-open`, `--no-promote-current`; `run --validate-only` skips execution; `scaffold/open --force/--dry-run` suppress or force the modeled write. Grouped by the stated rule (flags that alter or skip modeled semantics; plumbing flags excluded). | 3 (config branches) | model it or change the program | Either model the variant semantics (e.g. a close mode input with invariant-checked reachability), remove the flags the doctrine already forbids (--accept-new for ticket agents), or amend :530-533 once to declare CLI flag variants out-of-model — an owner boundary line, which this audit may not write. |

### 6.2 Out-of-scope inventory — does not gate

| # | Surface | Quoted plan line placing it out of scope |
|---|---|---|
| 1 | 80 pytest-job files (R2: `tests` component / `test_*.py` / `conftest.py`), incl. the named change-surface tests :2019/:2167/:2262 | :521 ("pytest jobs") |
| 2 | 214 test-graph/harness files (R2: `test_graph`/`graph-reports` component) | :521-522 ("test graph nodes", "integration harnesses") |
| 3 | 2 validation entry scripts | :521-522 ("validation scripts") |
| 4 | 6 experimental fuzzing scripts (generate_cases_from_tlc_dump, corpus_diagnostics, effect_conformance_report, kill_test, run_kill_test, export_testgraph_cases) | :559 / :525-530 |
| 5 | 26 rows outside the lifecycle closure (examples app/generated/artifact sources, generate_docs/generate_python/infer_action_params, skill-scripts, example sh) | :524-525 (totality) |
| 6 | scripts/fitness_functions.py — carried as an in-scope named-boundary row (one of the 19) whose entire behavior is declared out-of-model, so it contributes no gap | :530-533 |
| 7 | effect/behavior area groups of the above (§3-§4) | :521-522 / :524-525 / :525-530 |

(Counts: 328 out-of-scope rows = 80 + 214 + 2 + 6 + 26.)

### 6.3 Scope escalations — owner amends the plan, once

| # | Row | Plan line that should change | Argument |
|---|---|---|---|
| ESC-1 | `scripts/complexity_ledger.py` classification tension | :521 vs :565/:2262 | Three lines name the ledger in-scope (:565, :2262, :524-525 close path); a stretch reading of :521 "validation scripts" could exclude it. This run classified it IN (the three explicit lines win); gap R3-1 depends partly on that call — the owner should confirm in one line. |
| ESC-2 | Internal/External view split + dangling `source_model` refs (CD09-DF-3) | :569-570 (known_gaps, retained verbatim) | The quoted text scopes the split to concluded-epic MF-023, which closed without producing the views; manifest:110-113 still references three nonexistent files. The amendment claims E4 resolved but did not update this text. Whether the split is in this epic's scope is undeclared — the owner must restate the known_gap for the current epic (and either delete the dangling references or schedule the split). |
| ESC-3 | 10 unplaced rows: `close_ticket.py`, `close_tickets.py`, `close_spec_workflow.py`, `close-ticket.py`, `close-spec-workflow.py`, `start_ticket.py`, `scaffold_spec.py`, `scaffold_spec_workflow.py`, `run_tlc.sh`, `specs/desired_program_model/production_adapters.py` | :557 / :524-525 | These implement or wrap lifecycle behavior but are not reachable from the shipped CLI dispatch; whether "the SHIPPED CLI lifecycle" includes standalone wrappers is undeclared (run-2 E1/E2 residue — the amendment re-declared the catalog but still names the CLI by description, not paths). Note: close_spec_workflow.py:49 and close_tickets.py:127,:232 contain destructive deletes that would join gap R3-2 if the owner rules them in. |
| ESC-4 | CD09-DF-2: `RecordBudgets` absent from `effects.actions` (manifest:176-189) | :560 / manifest effect contract | Not a coverage gap: the CLI performs no distinct budgets write (scaffold's template emission is declared under Scaffold* spec_tree; recording user-negotiated values is an agent edit, not a program effect — verified: `budget_prompt` only prints, tla_spec_dev.py:89-120). But the index row is still missing and DF-2's requested owner decision ("declare spec_tree for it, or record why budget-recording is out of the effect contract") remains unmade. One line either way. |
| ESC-5 | `scripts/effect_conformance.py` dual classification | :527 vs :524-525 | Named experimental by :527, yet imported by the shipped runner (:24) and modeled — RunSpecUnitTests carries `effect_conformance'` :559 and manifest:127-129 says every spec-unit batch measures it. Conflicting quoted lines; the owner must place the sandbox (shipped measurement infrastructure vs experimental oracle). |
| ESC-6 | Amendment text vs tree: ":526-530 deliberately NOT modeled" while `AnalyzeCorpus` :403, `RunEffectConformance` :440, `RunKillTest` :493, their state, bindings (toml:40-47), and the corpus/effect guards in RunSpecUnitTests :544-573 remain in the model | :525-530 | The model still represents the demoted fuzzing surface the amendment says is unmodeled. Over-modeling, not a coverage gap — but it is dead model surface by the manifest's own rule (:131-133) the moment the experimental commands stop shipping, and the amendment's own words contradict the tree it licenses. Strike the actions or soften the sentence. |
| ESC-7 | 4 clock/provenance sites on the close path (spec_evolution:770,:883; complexity_ledger:775; skill_feedback:86) | :530-533 | No port type can declare a clock read and no invariant needs time; this audit judges them transcription — which is an argument that :530-533 should say so (add "provenance timestamps"), not a disposition this audit may grant. Until the line exists they are recorded here, not silently dropped. |
| ESC-8 | CD09-DF-1 wording: :564 "binds exactly the model's action set" vs Stutter | :564 | The tree operationalizes "action set" as the 14 @command actions (toml:3-11 rationale; binding test both ways); `Stutter` is a 15th TLA action, deliberately unbound. The corpus-gate refusal scenario DF-1 records is out per :526-527 (experimental). One word ("@command action set") makes :564 unambiguous. |

---

## 7. Verdict

- In-scope gaps: **4** (R3-1 refusal branches incl. the ledger gate; R3-2
  CloseTicket undeclared destructive deletes ×3 sites; R3-3 undeclared spawns
  on RunSpecUnitTests/CloseTicket — amended boundary :563 unmet; R3-4
  flag-variant branches incl. guard-disabling `--accept-new`)
- Out-of-scope inventoried: **328 files** + their effect/behavior groups
- Escalations: **8 issues covering 11 escalated rows + 7 boundary questions**
- **Verdict: `FAIL`**

**Why FAIL despite the amendment landing as designed:** all seven run-2 gaps
are properly closed — G2/G4/G5 verified fixed in the tree (§0 table), G1/G3/
G6/G7 out by quoted lines. But the amendment did the thing amendments do: by
declaring the shipped CLI lifecycle THE modeled surface (:524-525), it pulled
the ~15 lifecycle files run 2 could only ESCALATE (E1) into scope, and their
read-verified contents contain behavior and effects the model does not
represent and no quoted line excludes. Three of the four gaps sit exactly on
the amendment's own desired_boundaries (:563 port honesty — R3-2/R3-3; :565
ledger basis — R3-1's sharpest member). These are new classifications of
surface run 2 already recorded inside escalated rows, not re-litigations of
the owner's boundary.

CD09-DF dispositions under the amended scope: **DF-1** out-of-scope per
:526-527 (+ ESC-8 wording); **DF-2** not a coverage gap (ESC-4, owner decision
still owed); **DF-3** index desync feeding ESC-2 (no line makes the split
in-scope for this epic); DF-4 resolved at 195b07d (verified §1).

---

## 8. Attestation

1. **Row-count reconciliation per sweep:**
   - Step 1 index: mandated regex N=36 (defective, single-space `==` — run-2
     finding, prompt still unfixed); corrected N=41; ports 4; action→port rows
     13; bindings 14. Table reflects the corrected enumeration.
   - Sweep 1: N=358 (2191+567+135+324+5 raw minus the one stated `.history`
     filter), M=358. **N == M** (table generated by the recorded classifier;
     counts printed by it: in 19 / out 328 / ESC 11).
   - Sweep 2: raw N per category 2653/1113/60/317/277/5/87; every raw hit
     partitioned into area groups by the stated path rule (sums machine-checked
     equal to N); in-scope-area collapses per stated primitive rules with
     collapsed counts 3.1a 26→23 (3 discards named), 3.2 →5 real sites +2
     harness groups, 3.3 →0, 3.4 →3, 3.5 →4, 3.6 →0, 3.7 →0; destructive sites
     enumerated per-site 23/23.
   - Sweep 3: raw N 872/128/273/456/331/763; same partition accounting;
     lifecycle sub-groups stated as rules (refusal semantics; flag semantics);
     retry 128→0, timeout 273→0, concurrency 331→0 real in-scope sites.
   - Sweep 4: view modules N=1 per tree (ls), both views reported separately.
2. **Surface NOT walked:** `specs/.history/**` (stated filter; sealed);
   non-code config/template surface (`*.yaml/json/toml/cfg/md/j2` — including
   `templates/` j2 files, which shape scaffold output and were checked only
   via the manifest/model they emit); `*.tla` files as program surface (they
   are the audited model); jars; `.dot` state graphs; `states/` TLC dumps.
   Kotlin/Java/kts files were enumerated in Sweep 1 and partitioned in Sweeps
   2-3, but per-line effect patterns beyond the shared regex extensions
   (`ProcessBuilder|Runtime.getRuntime|HttpClient|System.getenv`) were not run
   as a separate Kotlin-specific pass (all such files are out per :521-522;
   per the prompt, a category searched only shallowly for those files is
   recorded, not hidden).
3. **Rows-READ vs rows-INFERRED (Sweep 1):** READ this session (targeted
   regions, cited by line): 12 — TlaSpecDevCli.tla (index + G2 regions + Close/
   RunSpecUnitTests bodies), spec_manifest.yaml (full ports/effects/
   justification), case_adapters.toml (full), tla_spec_dev.py (dispatch,
   parsers, spawn path), spec_evolution.py (ledger/refusal/delete/git regions),
   onboard_program_model.py (:1145-1195 template region), skill_feedback.py
   (head + write sites), close-wrapper heads ×5, scaffold_spec.py head,
   complexity_ledger.py (rejected-property region), fitness_functions.py
   (header). Grep-level (patterns read, bodies not): budgets.py,
   new_ticket_workflow.py, run_generated_case_adapters.py,
   production_adapters copies, adapter_case_runtime, extract_spec_manifest,
   effect_conformance (patch-site greps). INFERRED from path + index:
   **~330 of 358**, including every out-per-:521-522 row, every archived
   graph-reports row, and 4 in-scope rows marked [INFERRED] (spec_paths,
   testgraph_channels, spec_double_compiler ×2, program_model
   adapter_case_runtime) — these are the least reliable rows. All four gaps
   rest exclusively on READ rows.
4. **Rows whose scope was decided by reasoning rather than a quoted line:**
   (a) the totality reading of :524-525 (out-classifies the 26-row closure
   complement; the amendment's stated purpose — resolving run-2's E1 — makes
   the exclusive reading clearly intended, but it is a reading; rejecting it
   moves those 41 rows to escalations and changes no gap); (b) the name→phrase
   mapping of the 5 unnamed experimental scripts to :525-530's categories
   (corpus_diagnostics→"corpus gate" etc.); (c) classifying
   complexity_ledger.py IN over a stretch reading of :521 (declared as ESC-1
   because gap R3-1 partly depends on it); (d) treating graph-reports archived
   copies as :521-522 surface (run-2 judgment call, repeated). All four are
   surfaced here; (a)-(b) change inventory only, (c) is escalated.
5. **Can a reader reproduce this row set from the recorded commands?** yes —
   enumeration commands, the single filter, the classifier rules (priority
   order in §2), partition rule, and every collapse rule are stated; raw
   outputs committed at `specs/results/epic-close/sweep-raw-run3/`.
6. **Findings about this prompt** (required):
   - The Step-1 regex single-space defect and the Step-4 hardcoded-directory
     contradiction found by run 2 are BOTH still in the prompt verbatim; this
     run re-hit both and reapplied run 2's corrections. A third run should not
     have to.
   - **The prompt has no vocabulary for an amendment→tree contradiction** (ESC-6:
     the plan declares surface unmodeled that the model still models). Sweeps
     detect unrepresented program surface, not over-represented model surface;
     only the §1 index-building step surfaces it, and nothing requires
     reporting it. It is reported here anyway.
   - **Scope amendments move gaps between categories rather than only closing
     them:** resolving run-2's E1 escalations by re-declaring the boundary
     converted escalated rows into in-scope rows whose recorded-but-unclassified
     findings became gaps. The prompt's model (gaps close by modeling/changing;
     escalations close by amendment) is right, but a reader should expect a
     post-amendment re-audit to surface NEW gaps from the widened scope — that
     is the gate working, not churn.
   - The group-disposition allowance again did the heavy lifting (328
     out-of-scope rows dispositioned by area groups); the per-site destructive
     rule again proved its worth — R3-2 was found only because destructive
     sites may never be grouped.
