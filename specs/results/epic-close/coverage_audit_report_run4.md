# Coverage Audit Report — run 4 (re-verdict at workflow close, post-amendment-2 + CD-10)

- **Epic / workflow:** `complexity-descriptor-epic` (workflow close; CD-01, CD-02, CD-03, CD-09, CD-10 all done and merged)
- **Scope source:** `specs/desired_program_model/ticket_plan.yaml` (AMENDED AGAIN 2026-07-22, schedule_revision 3): `semantic_model_rule` lines `520-562`; `service_catalog` + `known_gaps` lines `576-599`; ticket `implementation_scope` lines `2046-2049` (CD-01), `2123-2125` (CD-02), `2193-2197` (CD-03), `2287-2291` (CD-09), `2365-2368` (CD-10)
- **Model audited:** `specs/current/TlaSpecDevCli.tla` @ `400c51a`
- **Date:** `2026-07-22`
- **Verdict:** `FAIL` — 3 in-scope gaps (all NEW, all on surface the second amendment pulled back into the modeled boundary)

> This audit checks **completeness of what is modeled**, not fidelity. The four
> oracles are bounded to what is already represented and cannot see this class
> of defect. See `prompts/coverage_audit.md`. Run 3 (FAIL, 4 gaps R3-1..R3-4,
> 8 escalations): `specs/results/epic-close/coverage_audit_report_run3.md` —
> used for targeting only; every enumeration below was re-run fresh at 400c51a.
> Raw sweep outputs: `specs/results/epic-close/sweep-raw-run4/`.

## Standing of the run-3 findings (verified fresh in the tree, not taken on faith)

| Run-3 item | Standing at 400c51a | Fresh evidence |
|---|---|---|
| R3-1 (lifecycle refusal branches) | **reclassified by owner amendment** — recorded granularity limitation | quoted `:544-551` + known_gaps `:599`; refusal sites verified still present (`spec_evolution.py:611-627`; no scripts/ change since 195b07d per `git diff --name-only`) |
| R3-2 (CloseTicket destructive deletes, no filesystem.delete port) | **FIXED by CD-10 — verified in tree** | `spec_tree_delete` port (filesystem.delete `**/specs/**`) declared `spec_manifest.yaml:198-200`, three sites cited in its comment `:190-197`; attached to CloseTicket `:231`; delete sites re-verified live: `spec_evolution.py:154` (rmtree states/), `:385` (rmtree in replace_tree — the #22 mechanism), `:477` (unlink); kill catalog seeds it (`kill_mutants.toml:94-102`, `port-spec_tree_delete`) |
| R3-3 (undeclared spawns: case runner + git) | **FIXED by CD-10 — verified in tree** | `runner_process` (process.spawn `*run_generated_case_adapters*`) `spec_manifest.yaml:187-189`, on RunSpecUnitTests `:230`; `git_metadata` (process.spawn `git rev-parse*`) `:206-208`, on CloseTicket `:231`; spawn sites re-verified live: `tla_spec_dev.py:314/:358`, `spec_evolution.py:99`; kill catalog seeds both (`kill_mutants.toml:79-92`, `:109-122`) |
| R3-4 (flag-variant branches incl. --accept-new) | **reclassified by owner amendment** — recorded granularity limitation; guard-weakening flags governed by doctrine | quoted `:547-551` + known_gaps `:599`; flags verified still shipped (`tla_spec_dev.py:645-655`, `:471-506`, `:401-458` unchanged) |
| DF-2 (RecordBudgets absent from effects.actions) | **FIXED by CD-10 — verified in tree** | `RecordBudgets: []` at `spec_manifest.yaml:221` — a deliberately EMPTY row, absent-vs-empty distinction recorded in its comment `:213-220`; effects.actions covers **14 of 14** @command actions (`:209-231`) |
| DF-3 (dangling Core/Internal/External source_model refs) | **FIXED by CD-10 — verified in tree** | `spec_manifest.yaml:109-117` — references REMOVED with rationale; `ls specs/program_model/*.tla` → `TlaSpecDevCli.tla` only |
| ESC-1 (complexity_ledger placement) | ruled: refusal machinery out-of-model | quoted `:551-554` |
| ESC-2 (view split + dangling refs) | ruled: FUTURE WORK, unscoped; refs removed | quoted known_gaps `:597`; DF-3 verified above |
| ESC-3 (10 unplaced wrapper/plumbing rows) | ruled: toolchain plumbing, out-of-model; deletes declared only where a modeled action performs them | quoted `:554-557`; verified the CLI close dispatch (`tla_spec_dev.py:178-193`) imports `spec_evolution` directly, never the wrappers — no wrapper delete is performed by a modeled action |
| ESC-4 (DF-2 decision) | ruled + fixed (empty row) | `spec_manifest.yaml:213-221` |
| ESC-5 (effect_conformance.py dual classification) | ruled: experimental surface per the ESC-6 ruling — i.e. **modeled** shipped-experimental command surface | quoted `:557-558` with `:538-542` |
| ESC-6 (amendment text vs tree) | ruled: the earlier "deliberately NOT modeled" wording was WRONG; AnalyzeCorpus/RunEffectConformance/RunKillTest stay modeled; only `generate` stays unmodeled | quoted `:538-542` + known_gaps `:598`; **residue: `:585` still carries the withdrawn wording — ESC-R4-1** |
| ESC-7 (clock/provenance reads) | ruled: out-of-model transcription | quoted `:559-560` |
| ESC-8 (`action set` vs Stutter wording) | fixed in the amended catalog | `:590` now reads "the model's **@command** action set"; `case_adapters.toml:13-53` binds exactly the 14 @command actions (verified fresh) |

**Kill catalog:** 20/20 — 7 port mutants (incl. honest seeded faults for the
three new CD-10 ports) + 13 invariant mutants, one per declared boundary
(`specs/current/kill_mutants.toml`: 20 `[[mutants]]` blocks vs 7 ports
`spec_manifest.yaml:157-208` + 13 invariants `TlaSpecDevCli.tla:633-773`).

**Trees reconciled at 400c51a:** `specs/current/{TlaSpecDevCli.tla,spec_manifest.yaml,case_adapters.toml}` diff-identical to the `specs/program_model/` and `specs/desired_program_model/` copies (checked this run).

---

## 0. Declared scope (quoted verbatim from the amended plan)
```yaml
# specs/desired_program_model/ticket_plan.yaml:520-562 (planning_rules.semantic_model_rule, AMENDED x2)
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
    AMENDED AGAIN 2026-07-22 (owner, resolving audit run 3's escalations):
    (ESC-6 correction) the experimental fuzzing surface REMAINS MODELED where
    it already is — AnalyzeCorpus, RunEffectConformance, RunKillTest, their
    state and gates, stay in the model as faithful representation of shipped
    (experimental) commands; the earlier "deliberately NOT modeled" wording
    was wrong. What stays unmodeled is `generate` — a RECORDED LIMITATION,
    to be modeled if/when the experimental surface is promoted, not an
    amendment claim that it does not exist. (R3-1/R3-4 granularity ruling)
    the model represents command-level lifecycle transitions and exactly the
    refusal/gate verdicts it already names; per-command refusal branches
    beyond those (e.g. the ledger close refusal) and per-flag variants
    (--accept-new, --allow-open, --no-promote-current, --validate-only,
    --force, --dry-run) are OUT-OF-MODEL as a recorded granularity
    limitation — flags that weaken guards are governed by doctrine (agents
    are forbidden --accept-new) rather than modeled. (ESC-1) the complexity
    ledger close refusal falls under the same granularity ruling: its
    verdict machinery is validation harness, out-of-model per this rule's
    first sentence. (ESC-3) the close/start/scaffold wrapper scripts,
    run_tlc.sh, and the desired-tree adapter copies are toolchain plumbing,
    out-of-model; their destructive deletes must still be DECLARED as ports
    where a modeled action performs them (CD-10). (ESC-5)
    effect_conformance.py is experimental surface per the ESC-6 ruling.
    (ESC-7) clock/provenance reads on the close path are out-of-model
    transcription. R3-2/R3-3 (undeclared deletes and spawns of modeled
    actions) and DF-2/DF-3 are REAL manifest desyncs fixed by CD-10, not
    amended away.
```

```yaml
# specs/desired_program_model/ticket_plan.yaml:576-599 (service_catalog + known_gaps, AMENDED)
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
    - declared ports match the effects modeled actions actually perform — writes, DELETES, and spawns (CD-09 for spawns of analyze; CD-10 for the close path's deletes, the case-runner and git spawns)
    - case_adapters.toml binds exactly the model's @command action set (CD-09; ESC-8 wording)
    - complexity-ledger decreases licensed by the validated-refactor basis (CD-09, owner-approved 2026-07-22)
    - manifest hygiene — effects.actions covers every modeled action; source_model references resolve (CD-10, DF-2/DF-3)
  adapter_boundaries:
    - specs/program_model/production_adapters.py spec-unit adapters
    - test_graph specWorkflow / cliWorkflow graphs
  known_gaps:
    - "AMENDED 2026-07-22 (ESC-2): this repository's baseline remains a single TlaSpecDevCli.tla module without the Internal/External view split. The MF-023 dogfooding ticket (concluded epic) measured modularity Q=0.012 — no clean cut — and deliberately did NOT decompose; that decision stands. The view split is FUTURE WORK, unscoped to any current ticket; the dangling Core/Internal/External source_model references in spec_manifest.yaml are removed by CD-10 (DF-3) rather than left pointing at files that do not exist."
    - "`generate` is unmodeled — recorded granularity limitation per the amended semantic_model_rule; modeled if/when the experimental surface is promoted."
    - "Per-command refusal branches beyond the modeled gate verdicts, and per-flag CLI variants, are out-of-model — recorded granularity limitation per the amended semantic_model_rule."
```

```yaml
# specs/desired_program_model/ticket_plan.yaml:2046-2049 (CD-01), 2123-2125 (CD-02), 2193-2197 (CD-03), 2287-2291 (CD-09), 2365-2368 (CD-10)
    implementation_scope:
      - scripts/analyze_complexity.py (remove suggestion machinery; F1 alias resolution; F3 bound honesty)
      - tests/test_analyze_complexity.py (F1 regression test failing pre-fix; F3 coverage)
      - SKILL.md and references/architecture_tractability.md (descriptor is the surface)
    implementation_scope:
      - references/complexity_intuition.md (new doc)
      - SKILL.md (wire the refactor-input framing into the workflow)
    implementation_scope:
      - scripts/fitness_functions.py (primitives + composition + evaluation; lean)
      - scripts/analyze_complexity.py (load per-project rules; surface fired rules in the report)
      - tests/test_fitness_functions.py
      - SKILL.md and references/fitness_functions.md (how an agent adds rules; advisory semantics)
    implementation_scope:
      - specs/current/TlaSpecDevCli.tla + MC.cfg (override removal; advisory-faithful guards; invariants)
      - specs/current/spec_manifest.yaml (ports; justification table rows touched)
      - specs/current/case_adapters.toml + production_adapters.py (binding reconciliation)
      - scripts/complexity_ledger.py + tests/test_complexity_ledger.py (retention basis)
    implementation_scope:
      - specs/current/spec_manifest.yaml (delete/spawn ports; effects.actions; source_model)
      - specs/current/kill_mutants.toml (boundary seeding for new ports)
      - specs/current/production_adapters.py + case_adapters.toml (only if schema surface requires)
```

| Scope line | Covers |
|---|---|
| `:524-525` | positive definition of the modeled surface: the shipped CLI lifecycle. Operationalized by the same mechanical closure rule as run 3: a file is lifecycle surface iff reachable from the shipped subcommands' dispatch in `scripts/tla_spec_dev.py` (:62-203) via imports, the runner spawn (:313-339/:358), or the `case_adapters.toml` binding and its imports |
| `:521-523` (first sentence, unamended) | pytest jobs, test-graph nodes, CI steps, integration harnesses, validation scripts — out of the modeled surface |
| `:538-542` (ESC-6 correction) | **AnalyzeCorpus, RunEffectConformance, RunKillTest and their backing scripts are MODELED shipped-experimental surface** — this run therefore audits `corpus_diagnostics.py`, `effect_conformance.py`, `effect_conformance_report.py`, `kill_test.py`, `run_kill_test.py` as in-scope (run 3 could not: the since-corrected wording put them out) |
| `:542` + known_gaps `:598` | `generate` unmodeled — recorded limitation |
| `:544-551` + known_gaps `:599` | per-command refusal branches and per-flag variants — recorded granularity limitation (retires R3-1/R3-4 as gap classes) |
| `:551-554` | ledger close-refusal machinery out-of-model (ESC-1 ruling) |
| `:554-557` | wrapper scripts, run_tlc.sh, desired-tree adapter copies — toolchain plumbing, out-of-model; deletes declared only where a modeled action performs them (retires run-3 ESC-3) |
| `:557-558` | effect_conformance.py placed (ESC-5 ruling) |
| `:559-560` | clock/provenance reads out-of-model transcription (retires run-3 ESC-7) |
| `:530-533` | fitness evaluation inside analyze, silent-degrade guards, runner env re-exec — out-of-model as transcription |
| `:583` | the CLI lifecycle as existing boundary |
| `:584` | `scripts/analyze_complexity.py`, `scripts/fitness_functions.py` (exact paths) |
| `:585` | experimental line — **stale wording, contradicts `:538-542`; see ESC-R4-1** (classification follows `:538-542`, which explicitly declares the older wording wrong) |
| `:586` | `spec_manifest.yaml` / `case_adapters.toml` schemas |
| `:589` | **the port-honesty boundary this run tests the newly re-scoped surface against: "declared ports match the effects modeled actions actually perform — writes, DELETES, and spawns" — found unmet on three paths (gaps R4-1, R4-2, R4-3)** |
| `:590` | `case_adapters.toml` binds exactly the @command action set |
| `:591` | complexity-ledger validated-refactor basis (with `:2291`) |
| `:592` | manifest hygiene: effects.actions coverage + source_model resolution (both verified fixed) |
| `:594` | `specs/program_model/production_adapters.py` (exact path) |
| `:597-599` | known_gaps: view split future work; `generate`; granularity limitations |
| `:2046-2049`, `:2123-2125`, `:2193-2197`, `:2287-2291`, `:2365-2368` | exact-path change surface of the five tickets |

**Closure rule applied:** a scope entry naming a FILE scopes that file only; no
entry writes a directory or glob, so no directory closure was granted. The
`:524-525` totality reading (a row provably outside the lifecycle closure is
out-of-scope BY that line) is carried over from run 3 and now reinforced by the
owner's ESC-3 ruling, which placed every row that reading had left ambiguous.
**Zero rows this run required an unstated scope inference** — every 358-row
classification traces to a quoted line above (attestation §8.4).

---

## 1. Model representation index

**Definitions.** Mandated regex → N = 36 (prompt defect: single-space `==`,
still unfixed — run-2 §8.6); corrected
`grep -nE '^[A-Za-z_][A-Za-z0-9_]*(\(.*\))?[[:space:]]+==' specs/current/*.tla`
→ **N = 41**: vars + 6 stage constants + 2 set helpers + CommandResult + Init +
15 action defs + Next + 13 invariants + Spec. **Identical line-for-line to
run 3's index** — CD-10 was zero model delta, verified (`git diff --name-only
195b07d..400c51a` touches no `.tla`).

| Kind | Names | Evidence |
|---|---|---|
| Actions (15 = 14 @command + Stutter) | `BuildSkillCli` :215, `InstallLocalCli` :231, `ScaffoldProject` :248, `RecordBudgets` :269, `ScaffoldWorkflow` :287, `OpenTicket` :305, `UpdateTicketDesired` :328, `UpdateTicketCurrent` :345, `AnalyzeComplexity` :371, `AnalyzeCorpus` :403, `RunEffectConformance` :440, `RunKillTest` :493, `RunSpecUnitTests` :529, `CloseTicket` :584, `Stutter` :601 | `specs/current/TlaSpecDevCli.tla` |
| Invariants (13) | `TypeInvariant` :633 … `KillTestVerdictRequiresBudgets` :773 | same |
| Ports (7) | `spec_tree` :157-159, `evidence_report` :160-162, `cli_artifact` :163-165, `test_process` :176-178, `runner_process` :187-189 (NEW, CD-10), `spec_tree_delete` :198-200 (NEW, CD-10), `git_metadata` :206-208 (NEW, CD-10) | `specs/current/spec_manifest.yaml` |
| Action→port map | **14 of 14 @command actions mapped** (`RecordBudgets: []` deliberately empty — DF-2 fixed) | `spec_manifest.yaml:209-231` |
| Bindings | 14 = exactly the @command action set; `Stutter` deliberately unbound with rationale | `case_adapters.toml:3-53` (discovered via `spec_manifest.yaml:233`) |
| `actions.yml` / `testgraph_bindings.yml` outside examples/ | none exist (find returned empty, exit 1) | Step-1 command |

**Index desyncs (fresh reads):**

1. `state_fields: []`, `actions: []`, `ports: {}` at `spec_manifest.yaml:123-125`
   while the model has 9 variables and 15 actions — MF-026 desync 3, STILL open,
   covered by no plan line (`:592` names only effects.actions and source_model)
   → **ESC-R4-2**.
2. The `@port TlaSpecDevCliPort.*` annotations (`TlaSpecDevCli.tla:214-583`,
   per-command vocabulary `build_skill_cli` … `close_ticket`) and the declared
   port names (`spec_tree` … `git_metadata`) still have **empty intersection** —
   MF-026 desync 2, STILL open, covered by no plan line → **ESC-R4-3**.
3. Run-3 desyncs 1 (dangling source_model) and 3 (RecordBudgets row) are FIXED
   (DF-3/DF-2, verified in the standing table). Run-3 desync 5
   (amendment-vs-tree contradiction) is resolved inside the semantic_model_rule
   by the ESC-6 correction but survives as stale wording at `:585` → **ESC-R4-1**.

---

## 2. Sweep 1 — Program surface

**Enumeration commands and raw counts (fresh at 400c51a):**

```bash
git ls-files '*.py'   | sort   # 2284 raw
git ls-files '*.kt'   | sort   #  567 raw
git ls-files '*.kts'  | sort   #  135 raw
git ls-files '*.java' | sort   #  324 raw
git ls-files '*.sh'   | sort   #    5 raw
# single filter applied to each: grep -v '^specs/\.history/'
# py 201, kt 84, kts 20, java 48, sh 5  ->  N = 358
```

**Filter statement:** exactly one filter — `specs/.history/**` (the sealed
append-only history tree; the raw py count grew 2191→2284 since run 3 purely
from CD-10's history entry). No amended plan line names a `.history` path as
surface. `tests/` NOT filtered (named at `:2048/:2196/:2291`). Raw lists:
`sweep-raw-run4/ca4-raw-*.txt`, filtered union
`sweep-raw-run4/ca4-surface-all.txt` — **diff-identical to run 3's surface**
(verified; the only surface file whose content changed since 195b07d is
`tests/test_kill_test.py`).

**Row-set discipline:** enumerated **N = 358**; table rows **M = 358**; `N == M`: yes.
Classification is mechanical (recorded script; its emitted table is reproduced
verbatim below and archived at `sweep-raw-run4/sweep1_table.md`).
Dispositions: **in-scope 24 / out-of-scope 334 / ESCALATION 0** — run 3's 11
escalated rows are all placed by the second amendment's rulings; 5 rows moved
INTO scope by the ESC-6 correction (`corpus_diagnostics.py`,
`effect_conformance.py`, `effect_conformance_report.py`, `kill_test.py`,
`run_kill_test.py`).
Verdict totals: represented 8, partial 14, unrepresented 336 (334 out-of-scope
rows by default polarity + `fitness_functions.py` out-of-model per `:530-533` +
`testgraph_channels.py`).

Rules (priority order; each row's plan line is in its own row):
**R1** exact path quoted in §0 → in. **R2** wrapper/plumbing rows named by the
ESC-3 ruling `:554-557` → out. **R3** `generate`/export surface per
`:585`/`:598`/`:521-522` → out. **R4** test/harness/validation surface per
`:521-522` (path component `tests`/`test_graph`/`graph-reports`, basename
`test_*.py`/`conftest.py`, the two `examples/` validation entry scripts) → out.
**R5** lifecycle closure per `:524-525` + `:538-542` (reachable from the
shipped subcommands via dispatch imports `tla_spec_dev.py:62-203`, the runner
spawn `:313-339`, or the `case_adapters.toml` binding and its imports —
including the five experimental-command files the ESC-6 correction keeps
modeled) → in. **R6** everything else provably outside the lifecycle closure →
out per `:524-525` (totality reading, attested §8.4).

| # | Module | In/Out | Plan line | Spec action(s) | Verdict | Evidence |
|---|---|---|---|---|---|---|
| 1 | `examples/distributed_history/ecommerce_backend/__init__.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 2 | `examples/distributed_history/ecommerce_backend/domain.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 3 | `examples/distributed_history/ecommerce_backend/service.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 4 | `examples/distributed_history/scripts/k3d-up.sh` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 5 | `examples/distributed_history/scripts/k8s-deploy.sh` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 6 | `examples/distributed_history/scripts/regenerate_tlc_cases.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 7 | `examples/distributed_history/specs/__init__.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 8 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/__init__.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 9 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/cases.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 10 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/types.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 11 | `examples/distributed_history/specs/generated/spec_unit/ecommerce_internal_cases/validators.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 12 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/__init__.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 13 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/cases.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 14 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/types.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 15 | `examples/distributed_history/specs/generated/testgraph/ecommerce_external_cases/validators.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 16 | `examples/distributed_history/specs/program_model/__init__.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 17 | `examples/distributed_history/specs/program_model/adapters.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 18 | `examples/distributed_history/specs/program_model/tests/test_ecommerce_adapters.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 19 | `examples/distributed_history/specs/program_model/tlc_projection.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 20 | `examples/distributed_history/test_graph/build-logic/build.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 21 | `examples/distributed_history/test_graph/build-logic/settings.gradle.kts` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 22 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphAssembler.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 23 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphModel.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 24 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/MiniJson.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 25 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/NodeDescribeLoader.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 26 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/TestGraphSpec.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 27 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/Toolchain.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 28 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphExtension.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 29 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphPlugin.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 30 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationNodeSpec.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 31 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationRuntime.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 32 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Context.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 33 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Executors.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 34 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/JBangExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 35 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/PlanExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 36 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/TimeoutParser.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 37 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/UvExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 38 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/InspectionTasks.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 39 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunReportWriter.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 40 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunTestGraphTask.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 41 | `examples/distributed_history/test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/ValidationReportTask.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
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
| 58 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/context.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 59 | `examples/distributed_history/test_graph/sdk/python/src/testgraphsdk/context_item.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
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
| 72 | `examples/validation/ex1_scaffold_only/taskq/taskq.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 73 | `examples/validation/ex1_scaffold_only/taskq/tests/test_taskq.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 74 | `examples/validation/ex3_over_complex/order_hub/order_hub.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 75 | `examples/validation/ex3_over_complex/order_hub/tests/test_order_hub.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 76 | `examples/validation/runs/ex3-run1/artifacts/order_hub_after.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 77 | `scripts/analyze_complexity.py` | in | :584, :2047 (CD-01), :2195 (CD-03) | AnalyzeComplexity | represented | AnalyzeComplexity TlaSpecDevCli.tla:371-401; evidence_report manifest:226 (writer :1622-1623); toml:37-38; advisory internals out-of-model per :530-533 [READ regions] |
| 78 | `scripts/budgets.py` | in | :524-525 (dispatch :89,:115) | RecordBudgets | partial | RecordBudgets TlaSpecDevCli.tla:269; manifest:221 (deliberately-empty effects row, DF-2 FIXED). UNCOVERED: load/refusal semantics -- out-of-model per :544-551/:599 (recorded granularity limitation) [grep-level] |
| 79 | `scripts/close-spec-workflow.py` | out | :554-557 (ESC-3 ruling: wrapper scripts, run_tlc.sh, desired-tree adapter copies are toolchain plumbing, out-of-model) | - | unrepresented | compat shim; placed by the run-3 escalation ruling [not read] |
| 80 | `scripts/close-ticket.py` | out | :554-557 (ESC-3 ruling: wrapper scripts, run_tlc.sh, desired-tree adapter copies are toolchain plumbing, out-of-model) | - | unrepresented | compat shim; placed by the run-3 escalation ruling [not read] |
| 81 | `scripts/close_spec_workflow.py` | out | :554-557 (ESC-3 ruling: wrapper scripts, run_tlc.sh, desired-tree adapter copies are toolchain plumbing, out-of-model) | - | unrepresented | close wrapper; rmtree :49 not performed by a modeled action, no port owed per :556-557; placed by the run-3 escalation ruling [not read] |
| 82 | `scripts/close_ticket.py` | out | :554-557 (ESC-3 ruling: wrapper scripts, run_tlc.sh, desired-tree adapter copies are toolchain plumbing, out-of-model) | - | unrepresented | close wrapper; placed by the run-3 escalation ruling [not read] |
| 83 | `scripts/close_tickets.py` | out | :554-557 (ESC-3 ruling: wrapper scripts, run_tlc.sh, desired-tree adapter copies are toolchain plumbing, out-of-model) | - | unrepresented | batch close (promotion_rule :565 forbids ticket agents running it); unlink :127 / rmtree :232 not performed by a modeled action; placed by the run-3 escalation ruling [not read] |
| 84 | `scripts/complexity_ledger.py` | in | :591, :2291 (CD-09) | CloseTicket | partial | ledger write on close under CloseTicket spec_tree manifest:231. UNCOVERED: verdict/refusal machinery -- out-of-model per ESC-1 ruling :551-554 (validation harness; granularity limitation :599) [READ via spec_evolution] |
| 85 | `scripts/corpus_diagnostics.py` | in | :538-542 (stays modeled), :524-525 (dispatch :148-151) | AnalyzeCorpus | partial | AnalyzeCorpus TlaSpecDevCli.tla:403-437; toml:40-41. UNCOVERED: AnalyzeCorpus declares evidence_report (manifest:227) but the command has no writer and no --out (run():902-935 prints only) -- dead declared port = gap R4-3 [READ] |
| 86 | `scripts/effect_conformance.py` | in | :557-558 (ESC-5 ruling), :538-542 | RunEffectConformance; effect_conformance' in RunSpecUnitTests | partial | sandbox behind RunEffectConformance :440 and RunSpecUnitTests :559; manifest:228. Sandbox root mkdir :619/:656 joins gap R4-2 on the effect-conformance path (covered by RunSpecUnitTests spec_tree on the runner path) [READ regions] |
| 87 | `scripts/effect_conformance_report.py` | in | :538-542, :557-558 (ESC-5/6 rulings) | RunEffectConformance | partial | RunEffectConformance TlaSpecDevCli.tla:440-489; evidence_report exercised (report.write :107). UNCOVERED: work-dir writes :149,:163 land under **/specs/** with spec_tree NOT declared for the action (manifest:228 = [evidence_report] only) = gap R4-2 [READ] |
| 88 | `scripts/export_testgraph_cases.py` | out | :521-522 (test-graph integration); also the generate pipeline per :598 | - | unrepresented | generate/export surface; default polarity, not read |
| 89 | `scripts/extract_spec_manifest.py` | in | :524-525 (dispatch :203; analyze; runner :30) | none directly | partial | manifest parsing inside every modeled command; parse refusals out-of-model per :544-551/:599 [grep-level] |
| 90 | `scripts/fitness_functions.py` | in | :584 named; :530-533 out-of-model | none | unrepresented | the whole file is the fitness-function evaluation :530-533 declares out-of-model as transcription (run-2 G1 reclassified; unchanged) [READ header run 3] |
| 91 | `scripts/generate_cases_from_tlc_dump.py` | out | :585, :598 (`generate` unmodeled -- recorded limitation), :542 | - | unrepresented | generate/export surface; default polarity, not read |
| 92 | `scripts/generate_docs.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 93 | `scripts/generate_python.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 94 | `scripts/infer_action_params.py` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 95 | `scripts/kill_test.py` | in | :538-542 (stays modeled) | RunKillTest | partial | RunKillTest TlaSpecDevCli.tla:493-525; manifest:229. UNCOVERED: mutation seed/restore write_text :548/:551 overwrites production source (scripts/**) matching NO declared port = gap R4-1; corpus spawn :609 matches test_process only for pytest-shaped commands [READ] |
| 96 | `scripts/new_ticket_workflow.py` | in | :524-525 (scaffold workflow/open; dispatch :102,:124) | ScaffoldWorkflow, OpenTicket | represented | ScaffoldWorkflow :287, OpenTicket :305; spec_tree manifest:222-223; toml:25-30 [grep-level] |
| 97 | `scripts/onboard_program_model.py` | in | :524-525 (scaffold; dispatch :64) | ScaffoldProject | represented | ScaffoldProject TlaSpecDevCli.tla:248; spec_tree manifest:212 [grep-level + run-3 READ carried] |
| 98 | `scripts/run_generated_case_adapters.py` | in | :524-525 (run; spawned by tla_spec_dev.py:313-339) | RunSpecUnitTests, RunEffectConformance | represented | RunSpecUnitTests TlaSpecDevCli.tla:529-577; spawn now declared runner_process manifest:187-189/:230 (R3-3a FIXED); env re-exec :971,:990-998 out-of-model per :531 [grep-level + verified citations] |
| 99 | `scripts/run_kill_test.py` | in | :538-542, :524-525 (dispatch :171-176) | RunKillTest | partial | run() :130 drives kill_test.seeded per mutant; report.write :225 -> evidence_report. UNCOVERED: shares gap R4-1 (spawn :198 of user-supplied corpus command; mutation writes) [READ] |
| 100 | `scripts/run_tlc.sh` | out | :554-557 (ESC-3 ruling: wrapper scripts, run_tlc.sh, desired-tree adapter copies are toolchain plumbing, out-of-model) | - | unrepresented | TLC runner wrapper; placed by the run-3 escalation ruling [not read] |
| 101 | `scripts/scaffold_spec.py` | out | :554-557 (ESC-3 ruling: wrapper scripts, run_tlc.sh, desired-tree adapter copies are toolchain plumbing, out-of-model) | - | unrepresented | tutorial scaffold wrapper; placed by the run-3 escalation ruling [not read] |
| 102 | `scripts/scaffold_spec_workflow.py` | out | :554-557 (ESC-3 ruling: wrapper scripts, run_tlc.sh, desired-tree adapter copies are toolchain plumbing, out-of-model) | - | unrepresented | workflow scaffold wrapper; placed by the run-3 escalation ruling [not read] |
| 103 | `scripts/skill_feedback.py` | in | :524-525 (close; spec_evolution.py:19) | CloseTicket | partial | feedback file under spec-root results matches spec_tree. UNCOVERED: clock provenance :86 -- out-of-model per ESC-7 ruling :559-560 [READ head run 3] |
| 104 | `scripts/spec_evolution.py` | in | :524-525 (close; dispatch :178) | CloseTicket | represented | CloseTicket TlaSpecDevCli.tla:584-599. Deletes :154,:385,:477 now declared spec_tree_delete manifest:198-200/:231 (R3-2 FIXED); git spawn :99 declared git_metadata :206-208/:231 (R3-3b FIXED); ledger + validation refusals out-of-model :544-554/:599; timestamps out-of-model :559-560 [READ regions] |
| 105 | `scripts/spec_paths.py` | in | :524-525 (closure via runner :31) | none | partial | path resolution inside modeled commands; no distinct effect surface [INFERRED] |
| 106 | `scripts/start_ticket.py` | out | :554-557 (ESC-3 ruling: wrapper scripts, run_tlc.sh, desired-tree adapter copies are toolchain plumbing, out-of-model) | - | unrepresented | open wrapper; placed by the run-3 escalation ruling [not read] |
| 107 | `scripts/testgraph_channels.py` | in | :524-525 (closure via runner :32) | none | unrepresented | channel enforcement for external test-graph bindings; enforced behavior is test-graph integration surface per :521-522 [INFERRED] |
| 108 | `scripts/tla_spec_dev.py` | in | :583, :524-525 | all 14 @command actions | represented | dispatch :62-203 -> TlaSpecDevCli.tla:215-599; port map manifest:209-231. Runner spawn :313-339/:358 now declared runner_process (manifest:187-189/:230, R3-3a FIXED); flag variants out-of-model per :547-551/:599 (recorded granularity limitation) [READ] |
| 109 | `skill-scripts/install-tla-spec-dev.sh` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 110 | `skill-scripts/install-tlc2.sh` | out | :524-525 (totality: outside the shipped CLI lifecycle closure; rule stated in section 2) | - | unrepresented | outside the shipped CLI lifecycle; default polarity, not read |
| 111 | `spec_double_compiler/__init__.py` | in | :524-525 (case runtime) | RunSpecUnitTests | partial | runtime consumed by generated cases/adapters (manifest:130-132) [INFERRED] |
| 112 | `spec_double_compiler/runtime.py` | in | :524-525 (case runtime) | RunSpecUnitTests | partial | double-execution engine behind RunSpecUnitTests batches [INFERRED] |
| 113 | `specs/current/adapter_case_runtime.py` | in | :2290 (CD-09), :2368 (CD-10) | RunSpecUnitTests | partial | harness shim; :36 spawn drives the CLI under test [grep-level] |
| 114 | `specs/current/production_adapters.py` | in | :2290 (CD-09), :2368 (CD-10) | all 14 bound actions | represented | bindings case_adapters.toml:13-53 <-> 14 @command actions (:590 wording now says '@command action set', ESC-8 FIXED); proven both ways by test_tla_spec_dev_binding_reconciliation.py [grep-level] |
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
| 132 | `specs/desired_program_model/production_adapters.py` | out | :554-557 (ESC-3 ruling: wrapper scripts, run_tlc.sh, desired-tree adapter copies are toolchain plumbing, out-of-model) | - | unrepresented | desired-tree adapter copy; placed by the run-3 escalation ruling [not read] |
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
| 150 | `specs/program_model/adapter_case_runtime.py` | in | :594 sibling (imported by production_adapters.py:23) | RunSpecUnitTests | partial | identical role to the specs/current copy; diff-verified identical this run [INFERRED] |
| 151 | `specs/program_model/production_adapters.py` | in | :594 (adapter_boundaries) | all 14 bound actions | represented | reconciled binding set; diff-verified identical to specs/current copy this run [grep-level] |
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
| 171 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphAssembler.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 172 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphModel.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 173 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/MiniJson.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 174 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/NodeDescribeLoader.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 175 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/TestGraphSpec.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 176 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/Toolchain.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 177 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphExtension.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 178 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphPlugin.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 179 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationNodeSpec.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 180 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationRuntime.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 181 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Context.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 182 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Executors.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 183 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/JBangExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 184 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/PlanExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 185 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/TimeoutParser.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 186 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/UvExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 187 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/InspectionTasks.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 188 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunReportWriter.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 189 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunTestGraphTask.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 190 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/ValidationReportTask.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
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
| 207 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/context.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 208 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-194428-2cebfb33/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/context_item.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
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
| 226 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphAssembler.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 227 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphModel.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 228 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/MiniJson.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 229 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/NodeDescribeLoader.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 230 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/TestGraphSpec.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 231 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/Toolchain.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 232 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphExtension.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 233 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphPlugin.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 234 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationNodeSpec.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 235 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationRuntime.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 236 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Context.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 237 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Executors.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 238 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/JBangExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 239 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/PlanExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 240 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/TimeoutParser.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 241 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/UvExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 242 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/InspectionTasks.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 243 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunReportWriter.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 244 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunTestGraphTask.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 245 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/ValidationReportTask.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
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
| 262 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/context.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 263 | `specs/tickets/MF-027/results/graph-reports/specWorkflow-20260719-195414-d28e3b52/cleanup-failure-probe-test-graph/sdk/python/src/testgraphsdk/context_item.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
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
| 281 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphAssembler.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 282 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/GraphModel.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 283 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/MiniJson.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 284 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/NodeDescribeLoader.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 285 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/TestGraphSpec.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 286 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/Toolchain.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 287 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphExtension.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 288 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationGraphPlugin.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 289 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationNodeSpec.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 290 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/ValidationRuntime.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 291 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Context.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 292 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/Executors.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 293 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/JBangExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 294 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/PlanExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 295 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/TimeoutParser.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 296 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/exec/UvExecutor.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 297 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/InspectionTasks.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 298 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunReportWriter.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 299 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/RunTestGraphTask.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 300 | `test_graph/build-logic/src/main/kotlin/com/hayden/testgraphsdk/tasks/ValidationReportTask.kt` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
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
| 317 | `test_graph/sdk/python/src/testgraphsdk/context.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
| 318 | `test_graph/sdk/python/src/testgraphsdk/context_item.py` | out | :521-522 (test graph nodes / integration harnesses) | - | unrepresented | test-graph node/harness surface; default polarity, not read |
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
| 337 | `tests/test_analyze_complexity.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; in scope as change surface only (:2048/:2196/:2291); not read |
| 338 | `tests/test_budgets.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 339 | `tests/test_case_adapter_runtime.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 340 | `tests/test_complexity_ledger.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; in scope as change surface only (:2048/:2196/:2291); not read |
| 341 | `tests/test_corpus_diagnostics.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 342 | `tests/test_effect_conformance.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 343 | `tests/test_effect_conformance_cli.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 344 | `tests/test_effect_conformance_runner.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 345 | `tests/test_export_testgraph_cases.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 346 | `tests/test_extract_spec_manifest.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 347 | `tests/test_fitness_functions.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; in scope as change surface only (:2048/:2196/:2291); not read |
| 348 | `tests/test_generate_cases_from_tlc_dump.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 349 | `tests/test_infer_action_params.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; default polarity, not read |
| 350 | `tests/test_kill_test.py` | out | :521 (pytest jobs) | - | unrepresented | pytest job; modified by CD-10 under objective text :2361-2362 though not an implementation_scope path; not read |
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
(`xargs /usr/bin/grep -nE <pattern> /dev/null < sweep-raw-run4/ca4-surface-all.txt`),
never a hardcoded subdirectory. Raw outputs: `sweep-raw-run4/<category>.txt`.
Patterns are the prompt's word-boundary sets; subprocess extended with
`ProcessBuilder` for the JVM surface (matching run 3). Partition rule (every
raw hit in exactly one group, sums machine-verified by the recorded script):
by path area — `lifecycle` (the 18 R1/R5 scripts + spec closure files, now
INCLUDING the five ESC-6 files), `other-scripts`, `adapters`
(production_adapters/adapter_case_runtime copies anywhere), `prod-runtime`
(spec_double_compiler), `repo-tests` (tests/), `spec-tests` (specs/**/tests/),
`testgraph` (test_graph | graph-reports component), `examples`,
`skill-scripts`. Areas out per `:521-522`/`:524-525`/`:554-557`/`:598` are
dispositioned as groups (inventory); in-scope areas are collapsed to real
primitive sites with the stated rule and dispositioned per-site.

### 3.1 Filesystem — raw `2653`, groups `9` (sum 2653)

| # | Group (area) | Raw | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | lifecycle | 534 | in | :524-525, :538-542 | spec_tree / evidence_report / spec_tree_delete (manifest:157-162, :198-200) | `declared` for the scaffold/open/close/analyze/run write-and-delete surface — the close deletes are now covered (R3-2 FIXED); **exceptions per-site in 3.1a/3.1b: gaps R4-1, R4-2** |
| 2 | adapters | 465 | in | :594/:2290/:2368 | spec_tree via exercised actions | `declared` (harness writes under spec tree/work dirs during modeled-action cases) |
| 3 | prod-runtime | 6 | in | :524-525 | n/a | no write primitive among hits (dataclass/Path plumbing) — `declared`-n/a |
| 4 | other-scripts | 135 | out | :554-557 / :585/:598 | — | inventory; wrapper deletes listed per-site in 3.1a with the ruling that covers them |
| 5 | repo-tests | 688 | out | :521 | — | inventory |
| 6 | spec-tests | 330 | out | :521 | — | inventory |
| 7 | testgraph | 444 | out | :521-522 | — | inventory |
| 8 | examples | 49 | out | :524-525 | — | inventory |
| 9 | skill-scripts | 2 | out | :524-525 | — | inventory (bash runtime — unobservable ≠ clean, noted) |

### 3.1a Destructive deletes — per-site, never grouped (raw 24 primitive-pattern lines, 23 real sites, 1 discard)

Collapse rule: destructive delete primitive = `shutil\.rmtree|\.unlink\(|os\.remove\(`
over `filesystem.txt` (raw extract archived: `sweep-raw-run4/destructive_sites.txt`);
1 discard: docstring `tests/test_promotion_preserves_current.py:4`.

| # | Site | Effect | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `scripts/spec_evolution.py:154` (via :707 ticket close / :851 workflow close) | rmtree of TLC `states/` dirs | in | :524-525 (close) | CloseTicket → `spec_tree_delete` (manifest:198-200, :231) | **`declared` — R3-2 FIXED** |
| 2 | `scripts/spec_evolution.py:385` (replace_tree, via promote :528) | rmtree of `current/` before promotion (the #22 mechanism) | in | :524-525 (close) | same | **`declared` — R3-2 FIXED** |
| 3 | `scripts/spec_evolution.py:477` | unlink of seeded paths dropped by ticket | in | :524-525 (close) | same | **`declared` — R3-2 FIXED** |
| 4 | `scripts/close_spec_workflow.py:49` | rmtree (workflow snapshot cleanup) | out | :554-557 (plumbing ruling; not performed by a modeled action — CLI dispatch verified) | — | inventory per quoted ruling |
| 5 | `scripts/close_tickets.py:127` | unlink | out | :554-557 + :565 (promotion_rule forbids agents running it) | — | inventory per quoted ruling |
| 6 | `scripts/close_tickets.py:232` | rmtree | out | same | — | inventory per quoted ruling |
| 7 | `scripts/generate_cases_from_tlc_dump.py:97` | rmtree metadir | out | :585/:598 (`generate` unmodeled — recorded limitation) | — | inventory |
| 8-10 | `examples/…/regenerate_tlc_cases.py:51`, `examples/run_distributed_history_validation.py:400,:402` | rmtree | out | :524-525 / :521-522 | — | inventory |
| 11-16 | `specs/tickets/MF-027/…/graph-reports/…` ×6 (cleanup/create_repo/failure_probe ×2 archived trees) | rmtree | out | :521-522 | — | inventory (archived evidence copies) |
| 17-19 | `test_graph/sources/spec_workflow_{cleanup,create_repo,failure_cleanup_probe}.py` | rmtree | out | :521-522 | — | inventory |
| 20-23 | `tests/test_effect_conformance.py:129,:824`, `tests/test_kill_test.py:943`, `tests/test_new_ticket_workflow.py:201` | unlink/os.remove in tmp fixtures | out | :521 | — | inventory |

### 3.1b Destructive overwrites — per-site (rule extension this run: overwrite = `write_text` to a pre-existing file the writer did not create)

The prompt's destructive class is "delete, rename, overwrite, truncate"; run 3
had no in-scope overwrite site because the kill test was out of the boundary.
The ESC-6 correction changes that:

| # | Site | Effect | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `scripts/kill_test.py:548` (seeded(), via `run_kill_test.py:130→198` — the shipped `run kill-test` path) | **overwrites a production source file with mutated code** (catalog `path` targets: `scripts/onboard_program_model.py`, `scripts/spec_evolution.py`, `scripts/tla_spec_dev.py`, … per kill_mutants.toml) | in | :538-542 (RunKillTest stays modeled); tested against :589 | RunKillTest → [evidence_report, test_process] (manifest:229) — **no filesystem.write port matches `scripts/**`** | **`undeclared` — gap R4-1** |
| 2 | `scripts/kill_test.py:551` (finally-branch restore) | overwrites the same file back to the original | in | same | same | **`undeclared` — gap R4-1** (the restore is the defense against #22-class corruption — an interrupted run leaves a mutated tree, which is precisely why the schema wants it declared) |

### 3.2 Subprocess — raw `1113`, collapsed `6` real spawn dispositions in in-scope areas

Rule: keep `subprocess\.(run|Popen|check_output|check_call|call)\(|os\.system\(|os\.exec\w*\(`
in lifecycle/adapters/prod-runtime areas; area groups inventory the rest
(testgraph 487, repo-tests 135, spec-tests 82, other-scripts 19, examples 28,
skill-scripts 1, prod-runtime 7 — out or plumbing per
:521-522/:524-525/:554-557; prod-runtime hits are identifier/prose).

> A `process.spawn` port declares the spawn, not what the child did.

| # | Site | Effect | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `scripts/tla_spec_dev.py:358` executing the `-m pytest` command (:296-303) | spawns pytest for spec-unit dirs | in | :524-525 (run) | test_process `*pytest*` (manifest:176-178, :230) | `declared` |
| 2 | `scripts/tla_spec_dev.py:358` executing the runner command (:313-339) | spawns the case runner | in | :524-525 (run); tested against :589 | **runner_process `*run_generated_case_adapters*` (manifest:187-189, :230)** | **`declared` — R3-3a FIXED** |
| 3 | `scripts/spec_evolution.py:99` (via git_metadata :801/:903) | spawns `git rev-parse…` for history provenance | in | :524-525 (close); tested against :589 | **git_metadata `git rev-parse*` (manifest:206-208, :231)** | **`declared` — R3-3b FIXED** (fail-open branch out-of-model per :531/:559-560) |
| 4 | `scripts/kill_test.py:609` (subprocess_case_runner, via `run_kill_test.py:198`) | spawns the user-supplied `--corpus-command` once per mutant + control run | in | :538-542 (RunKillTest); tested against :589 | test_process `*pytest*` covers the documented pytest-shaped corpus command; **the argument is unconstrained user input, so a non-pytest corpus command would match no port** | `partial` — named under gap R4-1's remediation (declare the corpus-runner spawn honestly or constrain the command) |
| 5 | `scripts/run_generated_case_adapters.py:992,:998` | batch env re-exec of itself | in | :531 | — | inventory — quoted out-of-model line covers the re-exec |
| 6 | `scripts/onboard_program_model.py:1188` | none — template text inside the scaffolded-test heredoc (:1145-1191) | in | :524-525 | n/a | not an effect site (READ, carried from run 3) |
| grp | `specs/{current,program_model}/production_adapters.py` ×11 sites each, `adapter_case_runtime.py:36` ×2 | harness spawns of the CLI under test | in | :594/:2290/:2368 | children ARE the modeled commands | `partial` (harness mechanics; child effects covered by the actions' own rows) |
| grp | `specs/desired_program_model/production_adapters.py` ×11 | same, desired-tree copy | out | :554-557 (plumbing ruling) | — | inventory per quoted ruling (was run-3 ESC) |

### 3.3 Network — raw `60`, collapsed `0` real sites in in-scope areas

Rule: keep lines invoking a network primitive (`urlopen|socket\.socket|\.connect\(|curl|wget`);
lifecycle-area hits (14) are all `scripts/effect_conformance.py`'s own
patch/observation code (:556-788 — it observes connects, performs none; now
in-scope by :538-542 and verified an observer, not an emitter) or prose
(`onboard_program_model.py:215,:1062`); real connects live in examples (19),
testgraph (16), skill-scripts curl (3), repo-tests (6), spec-tests (2) — out
per :521-522/:524-525; bash sites noted unobservable.

### 3.4 Environment — raw `317`, collapsed `3` real accessor sites in in-scope areas

Rule: keep `os\.environ|getenv|expanduser` accessor calls; discard `argv`,
dict-`setdefault`, prose. The five ESC-6 files contribute zero accessor sites
(verified: their hits are `setdefault` dict calls and argparse prose).

| # | Site | Effect | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `scripts/tla_spec_dev.py:271` (`os.environ.copy()` → child env) | env pass-through to spec-unit children | in | :524-525 | no env port type exists | inventory: input surface of RunSpecUnitTests children; behavior branch out per :531 |
| 2 | `scripts/run_generated_case_adapters.py:971` (`SPEC_DOUBLE_BATCH_REEXEC` read) | re-exec guard | in | :531 | — | inventory (quoted out-of-model) |
| 3 | `scripts/run_generated_case_adapters.py:990` (`os.environ.copy()`) | re-exec env | in | :531 | — | inventory (quoted out-of-model) |

Area groups (out): testgraph 248, examples 24, adapters 12, repo-tests 10,
spec-tests 1 — per :521-522/:524-525.

### 3.5 Clock — raw `278`, collapsed `4` real sites in in-scope areas

Rule: keep `datetime.now|time\.time|monotonic|perf_counter|sleep|timestamp()`
calls; discard prose/identifier matches (incl. `kill_test.py:1028` prose and
the one new hit since run 3, a comment in `tests/test_kill_test.py:717`).

| # | Site | Effect | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| 1 | `scripts/spec_evolution.py:770` | history entry `created_at_utc` | in | **:559-560 (ESC-7 ruling: out-of-model transcription)** | no clock port type exists | inventory per quoted ruling (was run-3 ESC-7; now placed) |
| 2 | `scripts/spec_evolution.py:883` | workflow entry timestamp | in | same | same | inventory per quoted ruling |
| 3 | `scripts/complexity_ledger.py:775` | ledger `recorded_at_utc` | in | same (+ :591/:2291) | same | inventory per quoted ruling |
| 4 | `scripts/skill_feedback.py:86` | feedback entry timestamp | in | same | same | inventory per quoted ruling |

Area groups (out): testgraph 223, examples 14, repo-tests 11, adapters 8,
spec-tests 4, other-scripts 1 — per :521-522/:524-525.

### 3.6 Randomness — raw `5`, collapsed `0`

Rule: all hits are the words `random`/`sample`/`choice` in comments/docstrings
(`fitness_functions.py:228`, `kill_test.py:171` — "deliberately not a random
AST perturbation", repo-tests ×3); no randomness primitive is called anywhere
in the enumerated surface.

### 3.7 Persistent store — raw `87`, collapsed `0` real users in in-scope areas

Rule: a real store effect requires a DB-module import; the lifecycle hits (9)
are `execute`/`commit` as identifiers or git-commit prose
(`spec_evolution.py:241-274` renders commit RECOMMENDATIONS, spawns nothing new;
`:109-113` are the already-dispositioned git_metadata reads); real store usage
lives in testgraph (43) and examples (32) — out per :521-522/:524-525.

---

## 4. Sweep 3 — Behaviors

Commands ran over the full surface (raw files `sweep-raw-run4/behaviors_*.txt`);
the prompt's literal Step-4 commands hardcode `scripts/ spec_double_compiler/` —
followed Step 3's own warning instead (run-2/3 attestation finding, STILL
unfixed in the prompt). Run-4 patterns are word-boundary anchored and
JVM-extended (`catch|throw|throws`, `waitFor`, `synchronized`); they differ
from run 3's (which matched unanchored substrings in places — e.g. its
concurrency count of 331 included `lock` inside "block"; this run's anchored
count is 22 with the same real-site outcome). Partition rule: same area groups
as §3, sums machine-verified.

### 4.1 Error paths — raw `821`, groups `8` by area (lifecycle 276, testgraph 255, other-scripts 95, adapters 59, examples 58, repo-tests 49, spec-tests 16, prod-runtime 13); lifecycle sub-grouped by failure semantics (rule: what the failure DOES to the command outcome)

| # | Behavior | Trigger | In/Out | Plan line | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|
| 1 | Loud refusal: complexity-ledger standing objective refuses the close ("There is no override flag") | `spec_evolution.py:611-627`, reached from every shipped close (:689/:835) | in | **:544-554 + :599 (granularity ruling + ESC-1 ruling — recorded limitation)** | CloseTicket :584-599 models command-level success only | inventory per quoted ruling (was gap R3-1's sharpest member; reclassified by the owner, not by this audit) |
| 2 | Loud refusals: input/state validation across lifecycle commands (missing plan :180, unknown ticket :224, ticket not closed :658, open tickets :830, existing entry :704/:848, missing model :584, ledger input errors :593; kill-test usage/catalog refusals `run_kill_test.py:180-186`, stale-mutant refusal `kill_test.py:538-546`) | `spec_evolution.py`, `extract_spec_manifest.py`, scaffold/open guards, kill/corpus/effect commands | in | **:544-551 + :599** ("per-command refusal branches beyond those the model names") | model represents refusal verdicts for the RunSpecUnitTests gates (:564-573) and the recorded corpus/effect/kill verdicts only | inventory per quoted ruling |
| 3 | Silent-degrade guards (analyze manifest-degrade `analyze_complexity.py:1046-1052`; fitness rules-doc errors `fitness_functions.py:284-295`; git fail-open `spec_evolution.py:99-101`) | absent/broken input | in | **:530-533 (quoted out-of-model)** | — | inventory |
| 4 | Sandbox observation/error plumbing (refuse-on-unobservable) | `effect_conformance.py` (require_observable :625+) | in | :538-542/:557-558 | effect_conformance verdicts in RunSpecUnitTests :559 and RunEffectConformance :440 | represented at verdict granularity; internals per :546 |
| 5 | prod-runtime case-failure propagation (13 hits) | `spec_double_compiler/runtime.py` | in | :524-525 | case failure surfaces as RunSpecUnitTests verdict (:560-573) | represented (verdict-carrying) |
| 6 | Test/harness error paths (repo-tests, spec-tests, adapters raise-for-assert) | — | out/in-harness | :521 | — | inventory |
| 7 | Testgraph/examples error paths | — | out | :521-522/:524-525 | — | inventory |
| 8 | other-scripts error paths (wrappers, generate) | — | out | :554-557/:585/:598 | — | inventory |

### 4.2 Retries — raw `165`, real retry loops in in-scope areas: `0` (lifecycle hits are 2 docstring/comment matches in `kill_test.py:131,:282`; loop-shaped retry lives in testgraph wait-for-ready polls (156) and examples (6) — out per :521-522/:524-525)

### 4.3 Timeouts — raw `322`, real sites in in-scope areas: `1`

| # | Behavior | Trigger | In/Out | Plan line | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|
| 1 | Per-mutant corpus timeout on the kill test (`--timeout`, default 600s; a timed-out corpus run scores the mutant) | `run_kill_test.py:104,:198` → `kill_test.py:592,:614` | in | **:547-551 + :599 (per-flag variants — recorded granularity limitation)** | RunKillTest :493-525 models the verdict, not the timing path | inventory per quoted ruling — NEW surface this run (run 3 reported 0 because the kill test was outside the then-declared boundary) |

Remaining: `budgets.py:41` is the `tlc_seconds` docstring (discard); testgraph
284, examples 15, adapters 12, spec-tests 4, repo-tests 2 — out per :521-522.

### 4.4 Fallbacks — raw `225`, groups `7` by area (lifecycle 87, testgraph 63, other-scripts 38, repo-tests 17, adapters 14, spec-tests 3, examples 3)

> Lifecycle sub-analysis: the silent-degrade members are exactly the class
> `:530-533` places out-of-model (analyze manifest-degrade :1046-1052, fitness
> advisory-error path :284-295, git fail-open :99-101) — inventory per the
> quoted line. Loud fail-on-missing members (budgets block must fail per
> MF-024) are refusal semantics → inventory per :544-551/:599. Remaining hits
> are `default=` argparse plumbing and dict fallbacks (no outcome change;
> re-derivable from raw).

### 4.5 Concurrency / interleaving — raw `22`, real concurrency primitives in in-scope areas: `0` (lifecycle hits are 4 prose matches — "synchronized" in scaffold template text `new_ticket_workflow.py:545,:685,:693`, "await" in a scaffold docstring `onboard_program_model.py:660`; real parallelism lives in test_graph Kotlin executors (16) — out per :521-522)

### 4.6 Config-driven branches — raw `898`, groups `8` by area (lifecycle 292, testgraph 234, adapters 164, other-scripts 95, examples 64, repo-tests 31, spec-tests 15, prod-runtime 3); lifecycle sub-grouped by rule: flags that alter or skip modeled semantics vs plumbing

| # | Behavior | Trigger | In/Out | Plan line | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|
| 1 | `close --accept-new` (skips current==desired check), `--allow-open`, `--no-promote-current`, `--workflow-name`/`--entry-name` | `tla_spec_dev.py:645-655`, spec_evolution :658 | in | **:547-551 + :599 (named explicitly: "--accept-new, --allow-open, --no-promote-current…"; "flags that weaken guards are governed by doctrine (agents are forbidden --accept-new) rather than modeled")** | CloseTicket :584-599 models one close semantics | inventory per quoted ruling (was gap R3-4; reclassified by the owner) |
| 2 | `run spec-unit-tests --validate-only`, `--label/--case/--limit`, `--no-batch` | `tla_spec_dev.py:471-506` | in | same (":--validate-only" named at :548) | RunSpecUnitTests :529-577 models the full batch verdict | inventory per quoted ruling |
| 3 | `scaffold/open --force/--dry-run` | `tla_spec_dev.py:401-458` | in | same (named at :549) | Scaffold*/OpenTicket model the write unconditionally | inventory per quoted ruling |
| 4 | Kill/corpus/effect command flags (`--timeout`, `--baseline`, `--suppressions`, `--out`, `--view`, `--cases-dir`, `--work-dir`) | `run_kill_test.py:95-116`, `corpus_diagnostics.py:835-852`, effect-conformance parser | in | :547-551 + :599 | AnalyzeCorpus/RunEffectConformance/RunKillTest model verdicts only | inventory per quoted ruling — NEW surface this run; **note `--out` presence/absence is load-bearing for gap R4-3** |
| 5 | Runner env/batch config (`SPEC_DOUBLE_BATCH_REEXEC`, `--python`) | runner :971-998 | in | **:531 (quoted out-of-model)** | — | inventory |
| 6 | Fitness rules presence/absence branch | `analyze_complexity.py:1194-1203` | in | **:530-532 (quoted out-of-model)** | — | inventory |
| 7 | Harness/testgraph/examples config | — | out | :521-522/:524-525 | — | inventory |
| 8 | other-scripts config (wrappers, generate) | — | out | :554-557/:585/:598 | — | inventory |

---

## 5. Sweep 4 — Views, reported separately

Enumeration: `ls specs/current/*.tla` → 1 module (`TlaSpecDevCli.tla`);
`specs/program_model/*.tla` → 1. The manifest no longer references
Internal/External/Core (DF-3 fixed, `spec_manifest.yaml:109-117`).

### 5.1 Internal — verdict: `unrepresented by construction (no Internal view module)`

| Surface item | Verdict | Evidence |
|---|---|---|
| Component decomposition, internal interleaving of the CLI's scripts | unrepresented by construction | single flat module; one-component `TlaSpecDevCliPort` (manifest:155) |

### 5.2 External — verdict: `unrepresented by construction (no External view module)`

| Surface item | Verdict | Evidence |
|---|---|---|
| Public input surface + observable projection as a distinct view; channel-typed Test Graph bindings | unrepresented by construction | no External.tla; `testgraph_bindings.yml` absent outside examples/ (§1 find) |

Not reported as "N/A — single module". **Scope standing — resolved this run:**
the amended known_gaps `:597` now records the split as "FUTURE WORK, unscoped
to any current ticket", quoting MF-023's measured Q=0.012 no-clean-cut basis.
Both view verdicts are therefore **out-of-scope inventory by a quoted plan
line** (run-3 ESC-2 retired). The finding remains on the record: every behavior
belonging to the missing views is unrepresented by construction, and the owner
has chosen to carry that as a recorded gap rather than close it.

---

## 6. Dispositions

### 6.1 In-scope gaps — HARD, block promotion

All three are NEW this run and share one cause: the ESC-6 correction
(`:538-542`) put AnalyzeCorpus / RunEffectConformance / RunKillTest back inside
the modeled boundary, and their backing scripts had never been audited against
the port-honesty promise `:589` ("declared ports match the effects modeled
actions actually perform — writes, DELETES, and spawns"). CD-10 fixed exactly
the paths run 3 named (close deletes, runner/git spawns) — these three are the
paths run 3 could not name because the then-current wording excluded them.

| # | Gap | Sweep | Disposition | Proposed remediation (advisory) |
|---|---|---|---|---|
| R4-1 | **RunKillTest overwrites production source files with no matching port.** The shipped `run kill-test` path (`tla_spec_dev.py:534-558` → `run_kill_test.py:130` → `kill_test.py:544-551` `seeded()`) write_texts a mutated copy over each catalog target (`scripts/onboard_program_model.py`, `scripts/spec_evolution.py`, … per `kill_mutants.toml` `path` keys), runs the corpus, and write_texts the original back. RunKillTest declares `[evidence_report, test_process]` (manifest:229); no filesystem.write port targets `scripts/**` (spec_tree is `**/specs/**`, evidence_report `**/results/**`, cli_artifact `**/.venv/**`). An interrupted run leaves the working tree mutated — the schema distinguishes exactly this so it cannot hide. Secondary member: the per-mutant corpus spawn (`kill_test.py:609`) matches `test_process` only when the user-supplied `--corpus-command` is pytest-shaped. | 2 (destructive overwrite, per-site 3.1b; subprocess 3.2 #4) | change the program (declare the port) | Declare a `mutation_write` port (filesystem.write, target `scripts/**` or the catalog's path set) on RunKillTest — or seed mutants in a copied tree so the modeled action never touches production source. For the spawn: declare a corpus-runner port or document/constrain the corpus command shape. |
| R4-2 | **RunEffectConformance writes its sandbox work tree with no port declared for the action.** The shipped `run effect-conformance` path with `--cases-dir` (its real invocation) creates `spec_dir/.effect-conformance-work` + per-case dirs + sandbox roots (`effect_conformance_report.py:149,:163`; `effect_conformance.py:619,:656`) — writes landing under `**/specs/**`, i.e. matching the `spec_tree` pattern, but RunEffectConformance declares `[evidence_report]` only (manifest:228). By the manifest's own rule (:134-136) an observed effect matching no port declared **for its action** is a GAP. (The same sandbox writes on the `run spec-unit-tests` path are covered — RunSpecUnitTests declares spec_tree, manifest:230.) | 2 (filesystem) | change the program (declare the port or move the work dir) | Add `spec_tree` to RunEffectConformance's port row — or default the work dir under `results/` so `evidence_report` covers it honestly. |
| R4-3 | **AnalyzeCorpus declares `evidence_report` but the command has no writer — a dead declared port**, the exact class CD-09's G4 removed for AnalyzeComplexity ("a declared port no case exercises is DEAD MODEL SURFACE", manifest:134-136; CD-09 acceptance `:2307` "no dead port"). `corpus_diagnostics.py` run() (:902-935) prints the report and returns; it has no `--out` flag (`add_arguments` :835-852: cases_dir/--view/--manifest only) and no file write anywhere (verified by primitive grep over the file: zero write sites). | 2 (port honesty, category-level) | change the program | Either add a writer (`--out` under `results/`, matching the other three analyze/run commands) or remove `evidence_report` from AnalyzeCorpus's row with the G4-style rationale comment. |

### 6.2 Out-of-scope inventory — does not gate

Everything Sweep 1 marks `out`: 334 rows across examples (76), testgraph +
graph-reports (23 + archived copies), repo-tests (25), spec-tests, archived
`specs/tickets/**` trees (110), wrapper/plumbing scripts per `:554-557` (11),
`generate`/export surface per `:585`/`:598` (2), skill-scripts (2) — each row's
quoted line is in the Sweep-1 table. Notable carried observations: the wrapper
deletes (`close_spec_workflow.py:49`, `close_tickets.py:127,:232`) are now
explicitly out-of-model by the ruling that also requires (and received, via
CD-10) port declarations for the modeled-action deletes; bash runtimes remain
unobservable-not-clean.

### 6.3 Scope escalations — owner amends the plan, once

None of these blocks classification (all 358 rows classified); all three are
wording/desync residues the rulings did not reach. Surfaced, not resolved:

| # | Escalation | Plan line(s) | What the owner must decide |
|---|---|---|---|
| ESC-R4-1 | `service_catalog.existing_boundaries:585` still reads "EXPERIMENTAL, deliberately unmodeled: … corpus gate, effect conformance, kill test" — the exact wording the second amendment (`:538-542`) declares WRONG for everything but `generate`. The catalog and the rule it sits beside now contradict each other; this run classified by `:538-542` (the later, explicitly-correcting text). | :585 vs :538-542 | One line: restate :585 as "`generate` only" (mirroring known_gaps :598), or note that the catalog line is superseded. |
| ESC-R4-2 | `spec_manifest.yaml:123-125` — `state_fields: []`, `actions: []`, `ports: {}` while the model carries 9 variables / 15 actions / 7 ports. MF-026 desync 3, open through four audit runs; no plan line places these blocks (`:592` covers only effects.actions and source_model). | :592 (silent about these keys) | Declare the blocks as generated-content placeholders (and say so in the manifest), populate them, or remove them. |
| ESC-R4-3 | `@port TlaSpecDevCliPort.<command_name>` annotations (`TlaSpecDevCli.tla:214-583`) vs declared port names (`spec_tree` … `git_metadata`): empty intersection — two vocabularies for "port" with nothing checking they refer to each other. MF-026 desync 2, open through four audit runs; no plan line covers it. | none (that is the escalation) | Rename the annotations to the declared port vocabulary, or record that `@port` means "command channel" and rename the tag. |

---

## 7. Verdict

- In-scope gaps: **3** (R4-1 RunKillTest mutation overwrites + corpus spawn;
  R4-2 RunEffectConformance undeclared work-tree writes; R4-3 AnalyzeCorpus
  dead evidence_report port) — all against the amendment's own `:589`/`:2307`
  port-honesty boundary, all on the surface `:538-542` re-scoped.
- Escalations: **3** (ESC-R4-1 stale `:585` wording; ESC-R4-2 manifest empty
  index blocks; ESC-R4-3 @port vocabulary desync) — none blocked
  classification.
- Out-of-scope inventory: non-empty (334 rows), recorded.

**Verdict: `FAIL`.** Promotion is blocked until R4-1..R4-3 are each closed by
modeling or by changing the program. The run-3 verdict's drivers are fully
retired: R3-2/R3-3/DF-2/DF-3 verified FIXED in the tree; R3-1/R3-4 and all
8 escalations carry recorded owner rulings this audit honors without
re-litigation. The residual FAIL is narrow, mechanical, and CD-10-shaped:
three port rows on the two experimental-command actions nobody had yet audited
inside the boundary. Also on the record: both views remain unrepresented by
construction — now a quoted known_gap (`:597`), not a gap this audit may count.

---

## 8. Attestation

1. **Enumerations.** Sweep 1: 5 `git ls-files` commands, raw 2284+567+135+324+5;
   one stated filter; N = 358 = M, machine-emitted table. Sweep 2: 7 category
   greps over `$SURFACE` via xargs, raw 2653/1113/60/317/278/5/87, each raw
   file archived; groups partitioned by a recorded script whose per-area sums
   equal each raw count (printed at run time); destructive extract 24 → 23
   sites + 1 discard, rule stated; overwrite extension 2 sites, rule stated.
   Sweep 3: 6 greps, raw 821/165/322/225/22/898, same partition; every
   lifecycle sub-group's rule stated in its section. Sweep 4: `ls` of 2 model
   dirs. All `N == M` reconciliations hold; the only raw-count deltas vs run 3
   trace to (a) `tests/test_kill_test.py`, the sole changed surface file
   (+1 clock, content-moved filesystem/subprocess lines), and (b) this run's
   anchored/extended behavior patterns, stated in §4.
2. **Surface not walked:** `specs/.history/**` (stated filter); non-code
   surface (YAML/TOML/MD/Gradle config except the named manifest/bindings/
   catalog files, which were read); the 334 out-of-scope rows' file contents.
3. **READ vs INFERRED.** Sweep 1 in-scope rows (24): READ this run — 9
   (`tla_spec_dev.py`, `spec_evolution.py` regions, `corpus_diagnostics.py`,
   `effect_conformance_report.py`, `effect_conformance.py` regions,
   `kill_test.py` regions, `run_kill_test.py`, plus `spec_manifest.yaml`,
   `kill_mutants.toml`, `case_adapters.toml` in full); READ in run 3 and
   re-verified by fresh grep this run — 9 (`analyze_complexity`, `budgets`,
   `complexity_ledger` via spec_evolution, `extract_spec_manifest`,
   `new_ticket_workflow`, `onboard_program_model`,
   `run_generated_case_adapters`, `skill_feedback`, `fitness_functions`
   header); INFERRED from role/import position — 6 (`spec_paths`,
   `testgraph_channels`, `spec_double_compiler` ×2, `adapter_case_runtime`
   ×2). All 334 out rows dispositioned from path via the stated rules, not
   read. **Every gap (R4-1/2/3) and every fix verification rests on rows READ
   this run with line citations.**
4. **Scope by reasoning?** One carried interpretive step: the `:524-525`
   totality reading (stated in §0/§2, identical to run 3's attested step, now
   corroborated by the owner's ESC-3 ruling resolving that reading's ambiguous
   rows in the same direction). The `:585`-vs-`:538-542` contradiction was
   resolved by the later text's own explicit supersession clause ("the earlier
   wording was wrong") — recorded as ESC-R4-1 rather than silently applied.
   No other row's scope was decided by reasoning.
5. **Reproducibility:** yes — the surface files, category raws, destructive
   extract, and the classifier that emits the Sweep-1 table verbatim are all
   under `sweep-raw-run4/`; a reader re-running the recorded commands at
   400c51a lands on these row sets exactly.
6. **Findings about this prompt.** (a) STILL OPEN from runs 2-3: the Step-1
   single-space regex and the Step-4 hardcoded subdirectories — both worked
   around, both should be fixed in the prompt. (b) NEW: the prompt has no
   procedure for a RE-AUDIT after an owner ruling — nothing says "when a
   ruling moves surface INTO scope, sweep that surface's effects as if for the
   first time". This run did so (it is how all three gaps were found), but a
   less suspicious reading of "verify the fixes" would have checked only the
   four named fixes and passed. The prompt should state: a boundary amendment
   invalidates prior sweeps over the moved surface. (c) The self-reported
   `N == M` limitation stands (tracked as #48); the recorded classifier
   narrows it for Sweep 1 but the collapse rules in Sweeps 2-3 remain
   judgment applied to raw files a reviewer must recount.
