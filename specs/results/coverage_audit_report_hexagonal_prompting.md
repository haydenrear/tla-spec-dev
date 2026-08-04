# Coverage Audit Report — hexagonal-prompting epic (MF-026 gate)

- **Epic / workflow:** `hexagonal-prompting-epic`
- **Scope source:** `specs/desired_program_model/ticket_plan.yaml:102-119` (`representation_scope`), governed by `:38-68` (`semantic_model_rule`, `representation_scope_rule`, `surface_cost_rule`, `no_new_gates_rule`)
- **Model audited:** `specs/program_model/TlaSpecDevCli.tla` @ `f431c62` — 11 variables, 18 `Next` disjuncts, 17 `@command` actions, 12 ports (`specs/current/` and `specs/desired_program_model/` copies are byte-identical to it)
- **Date:** 2026-08-04
- **Verdict:** **`FAIL`**

> **ROUND 2 IS AT THE END OF THIS FILE.** Re-verified at `0a05eed` after the
> owner's closure: **G-1 closed** (by a declaration I argue is the wrong width),
> **G-2 still open** (the new port's glob cannot match the spawn it declares),
> **G-3 retired** (verified against the standing proviso), **escalations 0**.
> Round-2 verdict `FAIL`, 1 in-scope gap. Everything below this line is round 1
> at `f431c62` and is preserved unedited.

> This audit checks **completeness of what is modeled**, not fidelity. The four
> oracles are bounded to what is already represented and cannot see this class
> of defect. See `prompts/coverage_audit.md`.

## VERDICT AT A GLANCE

- **In-scope gaps: 3** (2 created by this epic's own diff, 1 pre-existing and never previously filed)
- **Out-of-model inventoried: 14,504**
- **Escalations: 3**
- **Suite:** 1122 passed, 0 failed — re-run, not read (`uv run --with pytest --with pyyaml python -m pytest tests -q`)
- **Effect oracle:** re-run ×3, `unobservable`, exit 1, **84 / 15 / 9 identical on every run**
- **Raw:** `specs/results/coverage-audit-hexagonal-prompting-raw/`
- **Reproducers:** `classify_scope.py`, `cli_closure.py`, `module_to_action.py`, `collapse_effects.py`, `group_behaviors.py`, `external_surface.py`

| | predecessor R4 (`ab0dfee`) | **this run (`f431c62`)** |
|---|---|---|
| Verdict | `pass` | **`fail`** |
| In-scope gaps | 0 | **3** |
| — created by the epic's own diff | 0 | **2** |
| Escalations | 0 | **3** |
| In-model surface | 52 files | **52 files** (identical set) |
| Row set enumerated | 6,210 (source extensions only) | **14,575 (every tracked file)** |

**The two checks you asked for, up front.**

| Check | Result |
|---|---|
| **HP-04's new `spec_tree_delete` against what the action actually deletes** | **GAP (G-1).** The port targets `**/specs/**`; the delete runs at `<--work-dir>/<case>` and `--work-dir` is unconstrained. `reset_case_work_dir`'s own docstring advertises that the caller "can point [it] anywhere". Same class RC-02 closed as N-2 one epic ago, on a new command path. |
| **HP-03's generator mode for undeclared writes or spawns** | **CLEAN.** `scripts/generate_cases_from_tlc_dump.py` has exactly the same six effect sites before (`b68cbd5`) and after (`f431c62`) — lines 96/116/140/669/882/883 → 106/126/150/716/1006/1007, renumbered, not added. Zero new spawns, zero new writes, zero new deletes. The negative report is `print`ed, never written. External surface grew by exactly 3 options (`--negative-cases`, `--negative-dedupe`, `--negative-action`), 0 subcommands, 0 positionals. |

---

## 0. Declared scope (quoted verbatim from the plan)

```yaml
# specs/desired_program_model/ticket_plan.yaml:102-119
representation_scope:
  note: >-
    What the MF-026 coverage audit measures the model against. Carried forward
    from the predecessor's final amendment, which took four audit rounds to get
    right. Written with explicit directory globs, because the audit's closure
    rule treats a bare file path as scoping that file alone.
  in_model:
    - "scripts/**/*.py -- the shipped CLI toolchain"
    - "specs/*/spec_manifest.yaml -- where every effect port is declared"
    - "specs/*/TlaSpecDevCli.tla and specs/*/MC*.cfg"
    - "specs/*/production_adapters.py and specs/*/adapter_case_runtime.py"
  out_of_model:
    - "tests/**, specs/*/tests/**, test_graph/** -- harnesses; semantic_model_rule forbids modeling them"
    - "examples/** -- fixtures and eval subjects; what the toolchain is pointed AT"
    - "specs/.history/**, specs/tickets/**, specs/results/** -- sealed history, ticket workspaces, recorded evidence"
    - "spec_double_compiler/**, templates/** -- generator templates and harness plumbing"
    - "skill-scripts/**, *.sh wrappers -- installer shell. SUBJECT TO THE STANDING PROVISO: out-of-model files still owe ports for effects they perform on modeled action paths."
    - "prompts/**, references/**, *.md -- documentation and sub-agent prompts"
```

```yaml
# specs/desired_program_model/ticket_plan.yaml:42-55
  semantic_model_rule: >-
    Do not add test graph nodes, pytest jobs, CI workflow steps, integration
    harnesses, or validation scripts as TLA+ program state/actions. The modeled
    program surface is the shipped CLI lifecycle. The predecessor's four
    rulings carry forward verbatim in substance -- the experimental fuzzing
    surface stays modeled; case generation is MODELED (superseding the dead
    `generate` ruling); refusal branches and per-flag variants are out-of-model
    EXCEPT the six guard-weakening flags, which are modeled; advisory internals
    and wrapper scripts are harness plumbing. THE STANDING PROVISO: an
    out-of-model FILE does not make an out-of-model EFFECT.
  representation_scope_rule: >-
    `implementation_scope` is EDIT PERMISSION, never representation scope. The
    MF-026 audit of the predecessor halted partly on that conflation. The
    coverage audit reads `representation_scope` and nothing else.
```

| Scope line | Covers | Rows |
|---|---|---|
| `:109` `scripts/**/*.py` | the shipped CLI toolchain | 34 IN |
| `:110` `specs/*/spec_manifest.yaml` | port declarations, 3 trees | 3 IN |
| `:111` `specs/*/TlaSpecDevCli.tla`, `specs/*/MC*.cfg` | the model and its finite instances | 9 IN |
| `:112` `specs/*/production_adapters.py`, `specs/*/adapter_case_runtime.py` | the spec-unit adapter layer | 6 IN |
| `:114` `tests/**`, `specs/*/tests/**`, `test_graph/**` | harnesses | 117 OUT |
| `:115` `examples/**` | fixtures and eval subjects | 2,085 OUT |
| `:116` `specs/.history/**`, `specs/tickets/**`, `specs/results/**` | sealed history, workspaces, evidence | 12,212 OUT |
| `:117` `spec_double_compiler/**`, `templates/**` | generator templates and plumbing | 18 OUT |
| `:118` `skill-scripts/**`, `*.sh` | installer shell (standing proviso applies) | 3 OUT |
| `:119` `prompts/**`, `references/**`, `*.md` | documentation and sub-agent prompts | 69 OUT |
| — | **no line covers these** | **19 ESCALATION** |

Counts are **first-match-wins in the order the plan writes the lines**, so a
`.md` under `examples/` is counted once, at `:115`. `:116` dominates because
`specs/.history/**` holds sealed snapshots of every previous tree.

Per-row citations: `coverage-audit-hexagonal-prompting-raw/sweep1-table.md` (14,575 rows),
derived by `classify_scope.py`, which encodes the globs above verbatim with
POSIX globstar semantics (`**` crosses `/`, `*` does not).

### Escalations (ambiguous or absent boundary)

| # | Row(s) | Why the plan text does not classify it |
|---|---|---|
| **ESC-1** | 19 tracked files, listed in §6.3 — most consequentially `specs/current/tlc_projection.py`, `specs/*/case_adapters.toml`, `specs/*/kill_mutants.toml`, `specs/*/architecture_components.yaml`, `specs/*/architecture_map.yaml` | `in_model` names the model, the manifest, the cfgs and two adapter modules. It does **not** name the action→adapter **binding table**, the **mutant catalog**, the **declared component partition**, or **any other `.py` inside a spec tree**. `scripts/**/*.py` does not reach `specs/current/tlc_projection.py`. No `out_of_model` line covers them either. |
| **ESC-2** | The whole **External view** (Sweep 4) | The predecessor's plan carried an explicit ruling that the single-module baseline made the External view *"an INVENTORY ROW under this line, not a gap"*. **That ruling was not carried forward.** The strings `External`, `Internal` and `view split` do not appear anywhere in this plan. Sweep 4 therefore has no plan line to classify against, and `prompts/coverage_audit.md` §5 defaults to reporting the whole External surface as unrepresented. |
| **ESC-3** | `scripts/run_generated_case_adapters.py` provider machinery; `scripts/generate_python.py` (and, via it, gap **G-3**) | The predecessor's ESC-7 ruling put "the effect-provider runtime — `scripts/run_generated_case_adapters.py` provider machinery, `spec_double_compiler/*`, `templates/python/ports.py.j2`" out-of-model. **Only two of the three survived the carry-forward** (`:117`). The `scripts/` half is claimed IN by `:109`, and `service_catalog.existing_boundaries:124` independently names `run_generated_case_adapters.py` as a boundary of this epic. Deciding whether the spec-double codegen is "advisory internals … harness plumbing" (`:50`) requires *interpreting* the boundary, which §0's HALT condition forbids. |

**None of these was resolved by inference.** ESC-1 and ESC-2 in particular are
the class the coordinator flagged: the block was carried forward from a
predecessor that took four rounds to converge, and it was carried forward
**incompletely**.

---

## 1. Model representation index

Enumerated, not asserted. Commands and raw files:

| Index | Command | Raw | Count |
|---|---|---|---|
| Actions | `grep -nE '^[A-Za-z_][A-Za-z0-9_]*(\(.*\))? ==' specs/current/*.tla` | `index-actions.txt` | 42 definitions, of which **17 `@command` actions** + `Stutter` |
| Ports | `grep -n 'ports\|effects\|channel' specs/current/spec_manifest.yaml` | `index-ports.txt` | **12 ports**, 17 action rows |
| Bindings | `find . -name 'actions.yml' -o -name 'testgraph_bindings.yml' -o -name 'case_adapters.toml' \| grep -v '^./examples/'` | — | `specs/{current,program_model,desired_program_model}/case_adapters.toml` — **all three are ESC-1 rows** |
| CLI leaves | `external_surface.py` | `sweep4-external-surface.txt` | 11 leaf subcommands, 17 subcommand nodes, 11 positionals, 85 options |

| Kind | Name | `file:line` |
|---|---|---|
| Action | `BuildSkillCli` `InstallLocalCli` `ScaffoldProject` `RecordBudgets` `ScaffoldWorkflow` `OpenTicket` `UpdateTicketDesired` `UpdateTicketCurrent` `AnalyzeComplexity` `AnalyzeCorpus` `RunEffectConformance` `RunKillTest` `RunSpecUnitTests` `CloseTicket` `CloseTicketWeakened` `AnalyzeArchitecture` `GenerateCases` | `specs/current/TlaSpecDevCli.tla:266,294,313,337,357,377,402,421,449,484,528,585,625,684,751,805,856` |
| Port | `spec_tree` `evidence_report` `cli_artifact` `cli_download` `cli_artifact_delete` `cli_selftest_process` `test_process` `runner_process` `spec_tree_delete` `git_metadata` `mutation_write` `corpus_process` | `specs/current/spec_manifest.yaml:134,137,175,187,195,202,228,242,257,268,286,298` |
| Binding | `adapters: case_adapters.toml` | `specs/current/spec_manifest.yaml:454` |

Sanity check passed: 17 actions for 11 CLI leaves + 6 non-CLI lifecycle actions
(`BuildSkillCli`, `InstallLocalCli`, `RecordBudgets`, `UpdateTicketDesired`,
`UpdateTicketCurrent`, `CloseTicketWeakened`) — not a suspiciously small index.

---

## 2. Sweep 1 — Program surface

**Enumeration:** `git ls-files` → raw count **N = 14,575**; table rows **M = 14,575**; `N == M`: ☑
(`sweep1-table.md`, produced by `classify_scope.py`; no filter of any kind was applied)

> **On filters — none were applied, deliberately.** The predecessor's Sweep 1
> enumerated only source extensions (`py kt java kts j2 sh`, 6,210 rows) and
> derived its in-model set separately from `git ls-files`. That is why it
> reported **ESCALATION 0**: the 19 rows that match no plan line are `.toml`,
> `.yaml` and a `.py` inside a spec tree, and **not one of them was ever in its
> row set**. Enumerating every tracked file is the only change of method in this
> run, and it is what surfaces ESC-1.

**Partition:** IN-MODEL **52** · OUT-OF-MODEL **14,504** · ESCALATION **19**.

### 2.1 In-model surface — all 52 rows

Module→action attribution is derived by `module_to_action.py`: each CLI leaf's
handler is read out of `build_parser`'s `set_defaults(func=…)` and its
transitive `scripts.*` import closure walked. A module in no closure is
`unrepresented` **by construction**, which is RC-01's own G-6 test applied
mechanically.

| # | Module | In/Out | Plan line | Spec action(s) | Verdict | Evidence |
|---|---|---|---|---|---|---|
| 1 | `scripts/analyze_architecture.py` | IN | `:109` | AnalyzeArchitecture | `represented` | `TlaSpecDevCli.tla:805`; `tla_spec_dev.py:155` |
| 2 | `scripts/analyze_complexity.py` | IN | `:109` | AnalyzeComplexity (+5) | `represented` | `TlaSpecDevCli.tla:449`; `tla_spec_dev.py:143` |
| 3 | `scripts/architecture_reflexion.py` | IN | `:109` | AnalyzeArchitecture | `represented` | closure of `run_analyze_architecture` |
| 4 | `scripts/budgets.py` | IN | `:109` | 9 actions | `represented` | `spec_manifest.yaml:337-346` (RecordBudgets `[]` row) |
| 5 | `scripts/case_modules.py` | IN | `:109` | GenerateCases | `represented` | `spec_manifest.yaml:379-395` |
| 6 | `scripts/close-spec-workflow.py` | IN | `:109` | — | **`unrepresented`** | shim for `close_spec_workflow`; `cli-closure-unreachable.txt` |
| 7 | `scripts/close-ticket.py` | IN | `:109` | — | **`unrepresented`** | shim for `close_ticket`; idem |
| 8 | `scripts/close_spec_workflow.py` | IN | `:109` | — | **`unrepresented`** | no `close workflow` subcommand exists; `shutil.rmtree` at `:49` |
| 9 | `scripts/close_ticket.py` | IN | `:109` | — | **`unrepresented`** | direct-invocation duplicate of `close ticket` |
| 10 | `scripts/close_tickets.py` | IN | `:109` | — | **`unrepresented`** | documented in `SKILL.md:624,919`; `unlink` `:127`, `rmtree` `:232` |
| 11 | `scripts/complexity_ledger.py` | IN | `:109` | CloseTicket / OpenTicket / ScaffoldWorkflow | `represented` | closure |
| 12 | `scripts/corpus_diagnostics.py` | IN | `:109` | AnalyzeCorpus | `represented` | `spec_manifest.yaml:353-363` |
| 13 | `scripts/effect_conformance.py` | IN | `:109` | RunEffectConformance (+2) | **`partial`** | **G-1** — the `--work-dir` delete is outside the declared glob |
| 14 | `scripts/effect_conformance_report.py` | IN | `:109` | RunEffectConformance | **`partial`** | **G-1** — `:152`/`:169` accept an unconstrained `--work-dir` |
| 15 | `scripts/export_testgraph_cases.py` | IN | `:109` | — | **`unrepresented`** | `references/testgraph_adapters.md:93` |
| 16 | `scripts/extract_spec_manifest.py` | IN | `:109` | 10 actions | `represented` | closure |
| 17 | `scripts/fitness_functions.py` | IN | `:109` | AnalyzeComplexity (+5) | `represented` | closure |
| 18 | `scripts/generate_cases_from_tlc_dump.py` | IN | `:109` | GenerateCases | `represented` | `spec_manifest.yaml:395`; `TlaSpecDevCli.tla:856` |
| 19 | `scripts/generate_docs.py` | IN | `:109` | — | **`unrepresented`** | `cli-closure-unreachable.txt` |
| 20 | `scripts/generate_python.py` | IN | `:109` | — | **`unrepresented`** | **G-3** — `references/generation_modes.md:11`; new write at `:891` |
| 21 | `scripts/infer_action_params.py` | IN | `:109` | GenerateCases | `represented` | `spec_manifest.yaml:383-386` |
| 22 | `scripts/kill_test.py` | IN | `:109` | RunKillTest | `represented` | `spec_manifest.yaml:271-300` |
| 23 | `scripts/new_ticket_workflow.py` | IN | `:109` | OpenTicket / ScaffoldWorkflow | `represented` | `tla_spec_dev.py:104,126` |
| 24 | `scripts/onboard_program_model.py` | IN | `:109` | ScaffoldProject (+2) | `represented` | `tla_spec_dev.py:63` |
| 25 | `scripts/run_generated_case_adapters.py` | IN | `:109` | RunSpecUnitTests (spawned, `tla_spec_dev.py:346`), RunEffectConformance (imported, `effect_conformance.py:1757`) | **`partial`** | **G-2** — `execute_programs` `:2178` spawn and `mkdtemp` `:2294` are outside every declared port |
| 26 | `scripts/run_kill_test.py` | IN | `:109` | RunKillTest | `represented` | `tla_spec_dev.py:196` |
| 27 | `scripts/scaffold_spec.py` | IN | `:109` | — | **`unrepresented`** | tutorial path; `references/workflows.md:36-39` |
| 28 | `scripts/scaffold_spec_workflow.py` | IN | `:109` | — | **`unrepresented`** | `cli-closure-unreachable.txt` |
| 29 | `scripts/skill_feedback.py` | IN | `:109` | CloseTicket | `represented` | closure |
| 30 | `scripts/spec_evolution.py` | IN | `:109` | CloseTicket / CloseTicketWeakened | `represented` | `spec_manifest.yaml:245-270` |
| 31 | `scripts/spec_paths.py` | IN | `:109` | 8 actions | `represented` | `spec_paths.py:76,131` guards cited by the manifest |
| 32 | `scripts/start_ticket.py` | IN | `:109` | — | **`unrepresented`** | `references/architecture_coherence.md:313` |
| 33 | `scripts/testgraph_channels.py` | IN | `:109` | AnalyzeCorpus / GenerateCases / RunEffectConformance | `represented` | closure |
| 34 | `scripts/tla_spec_dev.py` | IN | `:109` | ALL (entrypoint) | `represented` | `tla_spec_dev.py:408-799` |
| 35-37 | `specs/{current,program_model,desired_program_model}/spec_manifest.yaml` | IN | `:110` | the declaration table itself | `represented` | 12 ports / 17 action rows, checked by `tests/test_spec_manifest_records.py` |
| 38-40 | `specs/{…}/TlaSpecDevCli.tla` | IN | `:111` | the model itself | `represented` | byte-identical across all three trees |
| 41-46 | `specs/{…}/MC.cfg`, `specs/{…}/MCsmall.cfg` | IN | `:111` | finite instances | `represented` | unchanged by this epic |
| 47-49 | `specs/{…}/production_adapters.py` | IN | `:112` | 17 bound adapters | `represented` (surface) / inventory (behavior, `:46-47`) | 39 write sites each; adapter fixture trees |
| 50-52 | `specs/{…}/adapter_case_runtime.py` | IN | `:112` | adapter runtime | `represented` (surface) / inventory (behavior, `:46-47`) | 4 write sites each |

**11 of 34 in-model scripts are reachable from no modeled action.**
`cli-closure-unreachable.txt`, produced by `cli_closure.py`, which walks
top-level *and* function-local imports from `scripts/tla_spec_dev.py` (the CLI
imports lazily inside each handler; a top-level-only walk finds almost nothing).

Nine of the eleven are documented, shipped, direct-invocation entrypoints
(`SKILL.md:612,618,624,821,919`; `references/{maintenance,spec_evolution,typical_workflow,workflows,examples,generation_modes,testgraph_adapters}.md`).
Two are compatibility shims. The predecessor inventoried this whole class under
`semantic_model_rule`'s *"advisory internals and wrapper scripts are harness
plumbing"* (`:50`). **That reading is quotable for the close/start/scaffold
wrappers and is retained here** — they are inventory, not gaps. It is *not*
quotable for `generate_python.py`, which is the spec-double compiler itself:
see **G-3** and **ESC-3**.

### 2.2 Out-of-model — 14,504 rows

Every row carries its plan line in `sweep1-table.md`. Grouped by line in the
§0 table. Nothing was excluded by an auditor's filter; the partition is the
plan's own globs applied by `classify_scope.py`.

**Sweep 1 close:** `enumerated N = 14,575, table rows M = 14,575, N == M` ☑

---

## 3. Sweep 2 — Effects, by category

`SURFACE` = the 52 in-model paths from Sweep 1 (`surface-in-model-paths.txt`).
Every command below was run against exactly that list — never a hardcoded
subdirectory.

**The collapsing rule, applied by machine** (`collapse_effects.py`, so a reader
can re-derive every table from the raw file):

> A raw hit is RETAINED iff, after Python tokenisation blanks every comment and
> every string token, the matched pattern still matches that physical line.
> Nothing is dropped for being uninteresting. Non-Python in-model files
> (`.tla`, `.cfg`, `.yaml`) cannot be tokenised as Python and every hit in them
> is a comment or a declaration by construction, so they collapse to zero and
> are counted separately as `nonpython_dropped`.

| Category | Raw | Collapsed | non-Python dropped | comment/string dropped |
|---|---|---|---|---|
| Filesystem | 1,552 | 1,271 | 96 | 185 |
| Subprocess | 779 | 191 | 225 | 363 |
| Network | 26 | 6 | 12 | 8 |
| Environment | 63 | 45 | 0 | 18 |
| Clock | 115 | 13 | 57 | 45 |
| Randomness | 4 | 0 | 0 | 4 |
| Persistent store | 25 | 6 | 0 | 19 |
| **Destructive** (per-site, never grouped) | 56 | **9** | 33 | 14 |

`effects-collapse-summary.txt`. Non-Python languages: this repository's in-model
surface is Python + TLA+ + cfg/yaml only (`git ls-files scripts/` = 34 `.py` +
1 `.sh`; the `.sh` is out-of-model by `:118`). The 567 `.kt` / 324 `.java` /
137 `.kts` files are all under `examples/**` and `test_graph/**`, out-of-model
by `:114`/`:115`.

### 3.1 Filesystem — raw 1,552, collapsed 1,271, grouped

**Grouping rule:** by *destination semantics of the path written*, decided from
the declared port glob that would have to cover it. Every collapsed hit falls in
exactly one group. Write/create sites are separately enumerated per-site
(`effects-write-sites.txt`, **208 sites in 26 modules**).

| # | Group | Sites | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| FS-1 | Adapter fixture trees under a per-case work dir (`production_adapters.py` ×39×3, `adapter_case_runtime.py` ×4×3) | 129 | IN (surface) / out (behavior) | `:112` surface; `:46-47` behavior | — | inventory (`semantic_model_rule` first sentence: integration harnesses) |
| FS-2 | Writes under the spec tree on a modeled action path (`new_ticket_workflow`, `onboard_program_model`, `spec_evolution`, `case_modules`, `generate_cases_from_tlc_dump`, `infer_action_params`) | 31 | IN | `:109` | `spec_tree` `**/specs/**` | `declared` |
| FS-3 | Evidence writes under `results/` (`analyze_complexity:2301`, `analyze_architecture:1126`, `architecture_reflexion:2304`, `kill_test`, `complexity_ledger`, `skill_feedback`) | 18 | IN | `:109` | `evidence_report` `**/results/**`, constrained by `spec_paths.resolve_evidence_out:76` | `declared` |
| FS-4 | Mutation seed/restore into production source (`kill_test.py:548,551`) | 2 | IN | `:109` | `mutation_write` `*scripts/*` | `declared` |
| FS-5 | Effect-oracle work tree (`effect_conformance.py:714,751,1686,1765`) | 4 | IN | `:109` | `spec_tree` **on the default path only** | **`partial` — G-1** |
| FS-6 | Corpus-runner work tree, default `tempfile.mkdtemp` (`run_generated_case_adapters.py:2294` + per-case/program dirs) | 8 | IN | `:109` | none | **`undeclared` — G-2** |
| FS-7 | Codegen writes, incl. the new mutation of `case_adapters.toml` (`generate_python.py:852,853,891`, `generate_docs`, `scaffold_spec*`, `export_testgraph_cases`, `close_tickets`) | 16 | IN | `:109` | none | **`undeclared` — G-3** (the `:891` site); the rest inventory under `:50` |
| FS-8 | Reads only (`read_text`, `Path(...)`, `open(..., "r")`, type annotations, imports) | 1,063 | IN | `:109`/`:110`/`:111`/`:112` | n/a | not an effect |

Group sum 129+31+18+2+4+8+16+1,063 = **1,271** ☑

### 3.2 Subprocess — raw 779, collapsed 191, real spawns 51

**Grouping rule:** a collapsed hit is a REAL SPAWN iff the line contains
`subprocess.{run,Popen,call,check_output,check_call}`, `os.system` or `os.execv`
(`effects-subprocess-realspawn.txt`); everything else is LEXICAL (a bare `run`,
`call` or `spawn` identifier with no spawn primitive on the line).

> **A `process.spawn` port declares the spawn, not what the child did.** Every
> row below whose child performs its own effects is `partial` at best. This is
> MF-027's process-boundary finding and it is not re-collapsed here.

| # | Site | Effect | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| SP-1 | `effect_conformance.py:889,900` | patches `subprocess.Popen` to *observe* | IN | `:109` | n/a — instrumentation | not an effect |
| SP-2 | `generate_cases_from_tlc_dump.py:126` | java/TLC | IN | `:109` | `corpus_process` `*` on GenerateCases | **`partial`** — the child's own writes (TLC `states/`, the dump) are unrepresented |
| SP-3 | `kill_test.py:609` | user-supplied `--corpus-command`, once per mutant | IN | `:109` | `corpus_process` `*` on RunKillTest | **`partial`** — same reason |
| SP-4 | `spec_evolution.py:99` | `git rev-parse` | IN | `:109` | `git_metadata` `git rev-parse*` | **`partial`** — read-only child, effects nil; declared spawn is complete |
| SP-5 | `tla_spec_dev.py:401` | `uv run … pytest` **or** `python scripts/run_generated_case_adapters.py …` | IN | `:109` | `test_process` `*pytest*` / `runner_process` `*run_generated_case_adapters*` | **`partial`** — both children perform their own effects |
| SP-6 | `run_generated_case_adapters.py:2124` | batch re-exec of itself | IN | `:109` | `runner_process` | **`partial`** |
| SP-7 | `run_generated_case_adapters.py:2178` | `<python> <work_dir>/programs/case_*.py`, one child per case (`--no-batch`) | IN | `:109` | **none** — matches neither `*pytest*` nor `*run_generated_case_adapters*` | **`undeclared` — G-2** |
| SP-8 | `production_adapters.py` ×13 ×3, `adapter_case_runtime.py:36` ×3 | adapters replaying the CLI to materialise a before-state | IN (surface) / out (behavior) | `:112` / `:46-47` | — | inventory |
| SP-9 | `onboard_program_model.py:1298` | inside a scaffolded-test **template string** | IN | `:109` | n/a | false positive that survived the rule — see §8.6 |
| SP-10 | remaining 140 collapsed hits | LEXICAL — bare `run`/`call`/`spawn` identifiers | IN | as classified | n/a | not an effect |

Group sum 2+1+1+1+1+1+1+42+1+140 = **191** ☑

### 3.3 Network — raw 26, collapsed 6, real calls **0**

| # | Site | Effect | Verdict |
|---|---|---|---|
| 1-5 | `effect_conformance.py:643,904,907,908,917` | patches `socket.socket.connect` to *observe* | not an effect |
| 6 | `onboard_program_model.py:1149` | f-string prose residue | false positive |

**Zero real network calls in the in-model Python surface.** The repository's one
real network fetch is `skill-scripts/install-tlc2.sh:37 (curl -fL)` — an
out-of-model **file** (`:118`) whose **effect** is declared as
`cli_download` (`network.http` → `*`) on `InstallLocalCli`, exactly as the
standing proviso requires. `declared`.

### 3.4 Environment — raw 63, collapsed 45, real reads 5

| # | Site | Effect | Verdict |
|---|---|---|---|
| 1 | `generate_cases_from_tlc_dump.py:1025` | reads `JAVA_OPTS`-shaped env for the TLA library property | **`undeclared` — no observable type exists** (§7, F-2) |
| 2 | `run_generated_case_adapters.py:2096` | reads `SPEC_DOUBLE_BATCH_REEXEC` | idem |
| 3 | `run_generated_case_adapters.py:2164` | reads `PYTHONPATH` | idem |
| 4-5 | `architecture_reflexion.py:1998,2157` | prose residue | false positive |
| 6-45 | `argv` / `expanduser` / `setdefault` on dicts | lexical | not an effect |

The manifest restricts port `type` to `filesystem.write`, `filesystem.delete`,
`process.spawn`, `network.connect`, `network.http` (`spec_manifest.yaml:125-127`).
**There is no environment type**, so these cannot be declared and can never be
observed. Recorded as F-2, not counted as a gap — see §7.

### 3.5 Clock — raw 115, collapsed 13, real reads 4

`complexity_ledger.py:1193`, `skill_feedback.py:86`, `spec_evolution.py:1057`,
`spec_evolution.py:1175` — all `datetime.now(timezone.utc).isoformat()`, all
written into files already covered by `spec_tree` / `evidence_report`. Same
schema limitation as §3.4: **no clock type exists**. `undeclared`, recorded as
F-2. The remaining 9 are imports and prose.

### 3.6 Randomness — raw 4, collapsed **0**

All four are the word `random`/`sample` in comments. **No nondeterminism source
in the in-model surface.** (`--seed` is a caller-supplied integer threaded to
Hypothesis inside the out-of-model runtime.)

### 3.7 Persistent store — raw 25, collapsed 6, real **0**

`generate_cases_from_tlc_dump.py:308,309,311` is a local variable named
`cursor`; `onboard_program_model.py:1314` and `spec_evolution.py:241,244` are
prose/f-string residue. No database, no ORM, no object store.

### 3.8 Destructive effects — 9 sites, enumerated per-site

Never grouped, per §3 of the procedure.

| # | Site | Effect | In/Out | Plan line | Declared port | Verdict |
|---|---|---|---|---|---|---|
| D-1 | `scripts/spec_evolution.py:154` `shutil.rmtree(state_dir)` | TLC `states/` at ticket and workflow close | IN | `:109` | `spec_tree_delete` `**/specs/**` on CloseTicket/CloseTicketWeakened | `declared` |
| D-2 | `scripts/spec_evolution.py:385` `shutil.rmtree(dst)` | project `current/` before promotion — the GitHub #22 data-loss mechanism | IN | `:109` | `spec_tree_delete` | `declared` |
| D-3 | `scripts/spec_evolution.py:477` `target.unlink()` | seeded paths the ticket dropped | IN | `:109` | `spec_tree_delete` | `declared` |
| D-4 | `scripts/spec_evolution.py:1005` `shutil.move(active_dir → ticket_history_dir)` | **unlinks the source path**; both ends under `specs/` | IN | `:109` | `spec_tree_delete` (source), `spec_tree` (destination) | `declared` — but see F-4: the manifest's CloseTicket comment enumerates D-1/D-2/D-3 and **not** this move |
| D-5 | `scripts/generate_cases_from_tlc_dump.py:150` `shutil.rmtree(metadir, ignore_errors=True)` | TLC metadir in `run_tlc_dump`'s finally branch | IN | `:109` | `spec_tree_delete` on GenerateCases, **constrained by construction** via `spec_paths.resolve_spec_tree_out:131` | `declared` |
| D-6 | `scripts/effect_conformance.py:1685` `shutil.rmtree(case_dir)` | **HP-04's new per-case reset** | IN | `:109` | `spec_tree_delete` `**/specs/**` on RunEffectConformance — **true of the default path only** | **`partial` — G-1** |
| D-7 | `scripts/close_spec_workflow.py:49` `shutil.rmtree(path)` | workflow-close cleanup | IN | `:109` | none — no modeled action reaches this module | inventory under `:50` (wrapper/close script) |
| D-8 | `scripts/close_tickets.py:127` `dst_files[relative].unlink()` | promotion cleanup | IN | `:109` | none — idem | inventory under `:50` |
| D-9 | `scripts/close_tickets.py:232` `shutil.rmtree(directory)` | workflow directory removal | IN | `:109` | none — idem | inventory under `:50` |

Three raw hits were dropped by the collapsing rule and are *not* deletes:
`effect_conformance.py:783,787,807` pass `"unlink"` / `"rmtree"` as **string
arguments** to `_patch_module` — the sandbox registering what to observe.

---

## 4. Sweep 3 — Behaviors

Enumerations run against the same 52-path `SURFACE`. Grouping is mechanical
(`group_behaviors.py`); comment-vs-code is decided on the tokenised line, the
group on the raw line (flag names and manifest keys are string literals that
blanking erases).

### 4.1 Error paths — raw 830, groups 8, grouping rule: by the line's own raise/catch syntax

| # | Group | Count | In/Out | Plan line | Spec action / invariant | Verdict |
|---|---|---|---|---|---|---|
| 1 | `EP-RAISE-DOMAIN` — a named toolchain refusal class (`SpecTreePathError`, `EvidencePathError`, `EffectDeclarationError`, …) | 211 | IN | `:109` | refusal branches out-of-model per `:48-49` | inventory |
| 2 | `EP-CATCH` | 169 | IN | `:109` | idem | inventory |
| 3 | `EP-TRY` — the `try:` line itself | 141 | IN | `:109` | no semantics of its own | not a behavior |
| 4 | `EP-COMMENT` | 90 | IN | as classified | n/a | not a behavior |
| 5 | `EP-RAISE-SYSEXIT` — refuse the command, exit nonzero | 86 | IN | `:109` | `:48-49` | inventory |
| 6 | `EP-RAISE-BUILTIN` — precondition / programmer error | 86 | IN | `:109` | `:48-49` | inventory |
| 7 | `EP-OTHER` | 38 | IN | `:109` | n/a | not a behavior |
| 8 | `EP-RAISE-BARE` — re-raise | 9 | IN | `:109` | no new semantics | not a behavior |

Sum = **830** ☑. Every group is dispositioned by the same quoted line:
`semantic_model_rule` `:48-49`, *"refusal branches and per-flag variants are
out-of-model EXCEPT the six guard-weakening flags"*. This is what makes
`GenerateCases`' unconditional `result' = CommandResult(TRUE, …)`
(`TlaSpecDevCli.tla:859`) an inventory row rather than a gap, despite the
command having two shipped nonzero exits (the case-cap refusal at
`tla_spec_dev.py:745-749`, and `SpecTreePathError`).

### 4.2 Retries — raw 2, real **0**

Both hits (`kill_test.py:131,282`) are the word "attempt" in comments about
degeneracy tripwires. **No retry or backoff anywhere in the in-model surface.**

### 4.3 Timeouts — raw 20, real 4 + 1 finding

| # | Behavior | Trigger | In/Out | Plan line | Spec action | Verdict |
|---|---|---|---|---|---|---|
| 1 | Per-mutant corpus timeout, default 600 s; `TimeoutExpired` propagates uncaught | `kill_test.py:592,614`; `run_kill_test.py:104,198` | IN | `:109` | RunKillTest's verdict range is `{"pass","below_floor","incomplete_catalog"}` (`TlaSpecDevCli.tla:588`) and excludes a timeout | inventory under `:48-49` (refusal branch) |
| 2 | Adapter subprocess timeout, 180 s ×4 ×3 trees | `production_adapters.py:1407,1761,1891,2025` | IN (surface) / out (behavior) | `:112` / `:46-47` | — | inventory |
| 3 | **`tlc_seconds: 120` — "hard external timeout per TLC run"** | `budgets.py:35,49`; every `spec_manifest.yaml:34` | IN | `:109`, `:110` | none | **F-1 — declared everywhere, read by nothing.** `grep -rn tlc_seconds scripts/` returns only `budgets.py`'s default table and its own prose; the java/TLC spawn at `generate_cases_from_tlc_dump.py:126` passes **no `timeout=`**, and `scripts/run_tlc.sh` has none either. Not a coverage gap — the model does not claim a timeout outcome, so it is faithful — but a budget documented as hard and enforced nowhere. |

### 4.4 Fallbacks — raw 421, groups 5

| # | Group | Count | Verdict |
|---|---|---|---|
| 1 | `FB-DEFAULT` — argparse/manifest defaults | 247 | inventory under `:48-49` |
| 2 | `FB-COMMENT` | 123 | not a behavior |
| 3 | `FB-IMPORT` — `except ImportError` dual-import shim (script vs package) | 30 | inventory under `:50` |
| 4 | `FB-FALLBACK` — named fallback parameters (`new_ticket_workflow.discover_baseline`, `run_generated_case_adapters.invoke_with_fallbacks`) | 19 | inventory under `:48-49` |
| 5 | `FB-SILENT` — `analyze_complexity.py:2112` `… or None`, `spec_evolution.py:103` `rendered or None` | 2 | inventory |

Sum = **421** ☑.

> **The recurring class — a guard that silently passes when its input is absent
> — was searched for specifically and the in-model surface is clean of it.**
> Only two `or None` sites exist and neither disables a check; there is no
> `except: pass`. The one instance of the class in this repository is **F-1**
> above, and it is a *budget* that is never read rather than a *guard* that is
> skipped.

### 4.5 Concurrency / interleaving — raw 2, real **0**

Both hits are the word "await" in a docstring
(`onboard_program_model.py:732`, `scaffold_spec.py:476`). No threads, no
`asyncio`, no locks, no `multiprocessing` in the in-model surface. The
model's single-writer interleaving is faithful.

### 4.6 Config-driven branches — raw 905, groups 6

| # | Group | Count | In/Out | Plan line | Spec action | Verdict |
|---|---|---|---|---|---|---|
| 1 | `CB-MANIFEST` — `.get(...)` against a parsed manifest/plan/TOML | 603 | IN | `:109` | the manifest is itself modeled (`:110`) | inventory |
| 2 | `CB-COMMENT` | 189 | IN | — | n/a | not a behavior |
| 3 | `CB-OTHER` | 88 | IN | `:109` | — | inventory |
| 4 | **`CB-CLI-GUARDFLAG`** — `--allow-open`, `--accept-new`, `--force`, `--dry-run`, `--no-batch`, `--no-promote-current` | 16 | IN | `:47-49` (**explicitly modeled**) | `CloseTicketWeakened` (`TlaSpecDevCli.tla:751`), `guard_weakening` recorded at `spec_evolution.py:529-530,558-560`, asserted by `production_adapters.py:2537,2549` | `represented` |
| 5 | `CB-ENV` | 5 | IN | `:109` | — | **`undeclared`, F-2** (no observable type) |
| 6 | `CB-CLI-OTHER` | 4 | IN | `:109` | `:48-49` | inventory |

Sum = **905** ☑.

**One guard flag is modeled as a per-flag variant but reaches an undeclared
effect:** `--no-batch` (`tla_spec_dev.py:537,369-370`) selects the
`execute_programs` path — **G-2**.

---

## 5. Sweep 4 — Views, reported separately

**A merged verdict is not acceptable, and this project has one module.**
`specs/*/TlaSpecDevCli.tla` is a single module with no `Internal.tla` /
`External.tla` split (`spec_manifest.yaml:58-62` records the decision;
`MF-023` measured modularity `Q = 0.012` and deliberately did not decompose).

### 5.1 Internal — verdict: `represented, with 3 partials`

| Surface item | Verdict | Evidence |
|---|---|---|
| 11 state variables, each with a justification row | `represented` | `spec_manifest.yaml:464-529` |
| 17 `@command` actions, 18 `Next` disjuncts | `represented` | `TlaSpecDevCli.tla:874-907` |
| 13 invariants | `represented` | `TlaSpecDevCli.tla:909-1101` |
| 12 ports ↔ 17 action rows ↔ `@port` annotations | `represented` | enforced by `tests/test_spec_manifest_records.py`, green in the 1122 |
| Component interleaving | n/a — one component | `architecture_components.yaml` (an **ESC-1** row) |
| Effect declaration completeness | **`partial`** | G-1, G-2, G-3 |

### 5.2 External — verdict: **`unrepresented by construction`** — see ESC-2

| Surface item | Verdict | Evidence |
|---|---|---|
| 17 subcommand nodes, 11 leaf | `represented` — the 11 leaves map 1:1 onto modeled actions | `sweep4-external-surface.txt` |
| 11 positionals | `represented` (as action parameters) | idem |
| 6 guard-weakening options | `represented` | `:47-49`, §4.6 |
| 79 other options | inventory | `:48-49` per-flag variants |
| **The External *view module* itself** | **`unrepresented`** | no `External.tla`, no `testgraph_bindings.yml` outside `examples/**`; `git ls-files \| grep testgraph_bindings.yml \| grep -v "^examples/"` is empty |
| **Test Graph case generation from an External view** | **`unrepresented`** | `max_external_cases_per_action: 50` is declared (`spec_manifest.yaml:48`) and unreachable |

`prompts/coverage_audit.md` §5 requires: *"If the project has only one view
module … report the whole External surface as unrepresented rather than
reporting the single module as complete. Do not report 'N/A — single module'."*
**The predecessor did not have to, because its plan carried an explicit ruling
making this an inventory row. This plan does not.** I am not resolving that by
inference in either direction — it is **ESC-2**, and it is the single largest
row-count consequence in this report.

**External surface delta this epic:** 110 → 113 rows. +3 options
(`--negative-cases`, `--negative-dedupe`, `--negative-action`), +0 subcommands,
+0 positionals. HP-03's "per-flag variant of an existing action" claim is
mechanically confirmed.

---

## 6. Dispositions

### 6.1 In-scope gaps — HARD, block promotion

| # | Gap | Sweep | Disposition | Proposed remediation (advisory) |
|---|---|---|---|---|
| **G-1** | **`RunEffectConformance`'s `spec_tree_delete` (and `spec_tree`) declare `**/specs/**`, but the effects they cover run at a caller-chosen path.** `--work-dir` is `type=Path` with no resolver (`effect_conformance_report.py:169`), defaulted at `:152` to `spec_dir/.effect-conformance-work` and otherwise used raw. `reset_case_work_dir` then `shutil.rmtree`s `<work_dir>/<case_name>` (`effect_conformance.py:1685`) and `mkdir`s the work root (`:1765`). The function's **own docstring** (`:1678-1681`) states the design intent: *"leaving the parent alone is what keeps `--work-dir` a directory the caller can point anywhere without the oracle emptying it."* Anywhere includes outside `specs/`. **Created by this epic (HP-04).** | 2 (§3.1 FS-5, §3.8 D-6) | **change the program** | Apply the guard that already exists: `spec_paths.resolve_spec_tree_out(args.work_dir, spec_dir)` at `effect_conformance_report.py:152`, exactly as RC-02 applied it to `generate cases --out`/`--dot` for gap N-2. `SpecTreePathError`'s docstring (`spec_paths.py:105-128`) already names *"the destructive `shutil.rmtree` … ran wherever the caller pointed, while the only ports that could cover them target `**/specs/**`"* — the same sentence describes this site. The alternative (widening `spec_tree_delete` to `*`) would weaken a port `CloseTicket` depends on in order to legalise a destructive delete at a caller-chosen path, which RC-02 explicitly rejected. |
| **G-2** | **`RunSpecUnitTests --no-batch` spawns children and writes trees that no declared port covers.** `run_generated_case_adapters.execute_programs` (`:2178`) runs `<python> <work_dir>/programs/case_*.py`, one child per case — matching neither `test_process` (`*pytest*`) nor `runner_process` (`*run_generated_case_adapters*`). With no `--work-dir`, `work_dir = tempfile.mkdtemp(prefix="spec-double-cases-")` (`:2294`), so the case programs (`:1255`) and per-case work trees (`:1256`) land outside both `spec_tree` (`**/specs/**`) and `evidence_report` (`**/results/**`). `--no-batch` is a shipped flag on a modeled action (`tla_spec_dev.py:537,369-370`). **Pre-existing at `b68cbd5`; never previously filed** — it was outside the predecessor's Sweep-2 disposition and its Sweep-1 verdictless table. | 2 (§3.1 FS-6, §3.2 SP-7), 4.6 | **model it** | Declare two ports on `RunSpecUnitTests`: `case_program_process` (`process.spawn` → `*/programs/case_*`) and a write port for the runner work tree. Surface cost per `surface_cost_rule`: **zero state space** — `effects.actions` is a declaration table, not state, and TLC enumerates identically (the same argument HP-04 made for `spec_tree_delete`). Alternative: **change the program** so `--work-dir` defaults under the spec tree and is resolved through `resolve_spec_tree_out`, which folds this into `spec_tree` and simultaneously removes a temp-dir dependency the oracle can never see. |
| **G-3** | **HP-05 added a write that mutates the adapter binding table, from a module no modeled action reaches.** `generate_python.py:891` `mapping_path.write_text(…)` appends `[effect_providers.<Port>]` tables to `specs/*/case_adapters.toml` — the file `spec_manifest.yaml:454` names as the model's binding table and that `effect_conformance.load_mappings` reads. `scripts/generate_python.py` is in-model by `:109` and is reachable from **no** CLI subcommand (`cli-closure-unreachable.txt`); it is a documented shipped command (`references/generation_modes.md:11`). No action, no port. **Created by this epic (HP-05).** Compounding: the file it writes is itself an **ESC-1** row. | 1 (row 20), 2 (§3.1 FS-7) | **model it** | Either (a) give the codegen a modeled action and a `spec_tree` port — the disposition RC-01 chose for the structurally identical G-6 (`generate cases` was shipped, documented and unrepresented for the same reason); or (b) **resolve ESC-3 in the owner's favour**, restoring the predecessor's ESC-7 ruling into `representation_scope.out_of_model`, which converts this row to inventory **in one visible plan line** rather than by a per-finding waiver. I am not choosing between these — (b) is a boundary decision, and boundary decisions are the owner's. |

**No forbidden disposition appears anywhere in this report.**
`grep -niE 'justified\|accept as-is\|acceptable risk\|out of contract\|low priority\|not worth modeling\|unlikely in practice'` over this file returns exactly one line: this sentence.

### 6.2 Out-of-scope inventory — does not gate

**14,504 rows**, every one carrying its plan line in `sweep1-table.md`.

| # | Surface | Quoted plan line | Rows |
|---|---|---|---|
| 1 | `specs/.history/**`, `specs/tickets/**`, `specs/results/**` | `:116` | 12,212 |
| 2 | `examples/**` — fixtures, worked examples, this epic's own A/B arms | `:115` | 2,085 |
| 3 | `tests/**`, `specs/*/tests/**`, `test_graph/**` | `:114` | 117 |
| 4 | `prompts/**`, `references/**`, `*.md` not already caught by a directory line | `:119` | 69 |
| 5 | `spec_double_compiler/**`, `templates/**` | `:117` | 18 |
| 6 | `skill-scripts/**`, `*.sh` (incl. `scripts/run_tlc.sh`) — standing proviso applied: the one effect they perform on a modeled path, the tlc2 jar download, **is** declared as `cli_download` | `:118` | 3 |
| 7 | Behavior-level: refusal branches, 79 non-guard options, the 6 group-subcommand `exit 2` paths | `:48-49` | — |
| 8 | Behavior-level: adapter fixture writes and CLI-replay spawns in `production_adapters.py` / `adapter_case_runtime.py` (in-model as *surface* by `:112`) | `:46-47` | — |
| 9 | Behavior-level: the 9 documented non-CLI wrapper/close/start/scaffold scripts | `:50` | — |

### 6.3 Scope escalations — owner amends the plan, once

| # | Row(s) | Plan line that should change | Argument |
|---|---|---|---|
| **ESC-1** | 19 files: `specs/{current,program_model,desired_program_model}/case_adapters.toml`, `…/kill_mutants.toml`, `…/architecture_components.yaml`, `…/architecture_map.yaml`, `specs/current/tlc_projection.py`, `specs/desired_program_model/{ticket_plan,desired_state,deferred_findings}.yaml`, `.gitignore`, `skill-manager.toml`, `.DS_Store` | `representation_scope.in_model` `:108-112` (add) or `out_of_model` `:113-119` (add) | The block names the model, the manifest, the cfgs and two adapter modules, and stops. It does not name **the action→adapter binding table** (which `prompts/coverage_audit.md` §1 requires in the representation index and which `effect_conformance.load_mappings` reads), **the mutant catalog** (oracle 4's entire input), **the declared component partition** (what `analyze complexity`/`architecture` measure), or **any other `.py` in a spec tree**. The last of those is not hypothetical: **`specs/current/tlc_projection.py` is new in this epic (HP-03) and is the reason a corpus of this model is importable at all** — 3,678,217 cases → 541, a 6,800× reduction (`references/generation_modes.md:155-165`). It is `desired_boundaries:130`'s *"A tractable corpus: a projection this model does not have"*, delivered — and the audit's scope block cannot classify it. It exists only in `specs/current/`; neither `program_model` nor `desired_program_model` has one. Also: `.DS_Store` is tracked. |
| **ESC-2** | The External view; by extension every Sweep-4 row in §5.2 | `service_catalog.known_gaps` `:135-137` (restore) | The predecessor's plan carried: *"this repository's baseline remains a SINGLE `TlaSpecDevCli.tla` module without the Internal/External view split — future work, unscoped … the External view being unrepresented is an INVENTORY ROW under this line, not a gap."* This plan's `known_gaps` has two entries and neither is it; `External`, `Internal` and `view split` appear **nowhere** in the file. `prompts/coverage_audit.md` §5 mandates reporting the whole External surface as unrepresented absent a counter-quote, and §0 forbids me supplying one. Restoring one sentence retires this. |
| **ESC-3** | `scripts/run_generated_case_adapters.py` provider machinery; `scripts/generate_python.py` (governs **G-3**) | `service_catalog.known_gaps` `:135-137` (restore) or `representation_scope.out_of_model` `:113-119` (add) | The predecessor's ESC-7 ruling put "the effect-provider runtime — `scripts/run_generated_case_adapters.py` provider machinery, `spec_double_compiler/*`, `templates/python/ports.py.j2`" out-of-model. **Two of the three survived the carry-forward** (`:117`); the `scripts/` half did not, and `:109` claims it IN. Meanwhile `service_catalog.existing_boundaries:124` names `run_generated_case_adapters.py` as a boundary of *this* epic and the manifest declares `runner_process` for it — so the plan currently says three different things about one file. Deciding whether the spec-double codegen is "advisory internals … harness plumbing" (`:50`) requires interpreting the boundary, which §0 forbids. |

---

## 7. Findings recorded, NOT counted as gaps

Each is a fidelity, determinism or record defect. Counting them would inflate
the verdict; omitting them would repeat the failure §8.6 describes.

| # | Finding | Severity | Owner |
|---|---|---|---|
| **F-1** | **`tlc_seconds: 120` is documented as a "hard external timeout per TLC run" in `budgets.py:49` and in all three `spec_manifest.yaml:34`, and is read by no code path.** `grep -rn tlc_seconds scripts/` returns only `budgets.py`'s own default table and prose. The java/TLC spawn (`generate_cases_from_tlc_dump.py:126`) passes no `timeout=`; `scripts/run_tlc.sh` has none. It is the only budget in the block presented as an operational hard limit (`budgets.py:110`), and it is the one that does nothing. | minor | `scripts/budgets.py`, `scripts/generate_cases_from_tlc_dump.py` |
| **F-2** | **The effect schema has no observable type for clock or environment reads**, so 4 `datetime.now()` sites and 3 env reads on in-model modules can never be declared and can never be observed. `spec_manifest.yaml:125-127` restricts `type` to filesystem/process/network, correctly — an unobservable type could never be checked — but the consequence is that a whole class of nondeterminism input is outside the model *and* outside the oracle, silently. | minor | the schema |
| **F-3** | **`spec_tree_delete` — the one unit of model surface this epic added — reports DEAD MODEL SURFACE in the shipped oracle.** All three of my runs: `DEAD MODEL SURFACE: port TlaSpecDevCliPort.spec_tree_delete (filesystem.delete -> **/specs/**) declared but never observed`. By the manifest's own rule 30 lines above the declaration, that is a HARD FAILURE. Mitigating: the port was already dead before HP-04 (declared for `CloseTicket`, `CloseTicketWeakened`, `GenerateCases`), the dead-port count is **9 before and 9 after**, and HP-04's own delete is executed *outside* the sandbox window by construction (`effect_conformance.py:1809` resets, `:1824` enters the sandbox), so the oracle could not observe it even in principle. **Not a coverage gap** — dead surface is the inverse of unmodelled surface — but the epic's single surface addition is, by the shipped instrument's own report, not exercised. | major | `spec_manifest.yaml`, oracle design |
| **F-4** | `spec_evolution.py:1005` `shutil.move(active_dir → ticket_history_dir)` unlinks its source and is covered by `spec_tree_delete`'s glob, but the manifest's `spec_tree_delete` comment (`:245-256`) enumerates the *other three* CloseTicket deletes by `file:line` and not this one. The port is correct; the citation block is incomplete. Same class as the citations `tests/test_source_citations.py` was built to catch, which checks the anchors that exist rather than the ones that are missing. | minor | `spec_manifest.yaml` |
| **F-6** | **The plan's own `known_gaps:137` citation went stale inside this epic.** It cites `effect_conformance.py:1141-1145` for *"in-process CPython only"*. At `b68cbd5` that was exact; HP-04 inserted ~300 lines above it and the text now lives at `:1441` (the header statement is at `:26`). `ticket_plan.yaml:137` now points at an `OutOfProcessObservation` field declaration. This is the **fifth consecutive ticket** to ship a stale internal figure, in the one document this gate reads its scope from, and it is exactly the class `tests/test_source_citations.py` was built for — which still does not cover `ticket_plan.yaml`. The predecessor recommended extending it; the recommendation was not taken and the defect recurred within one epic. | minor | `ticket_plan.yaml`, `tests/test_source_citations.py` |
| **F-5** | **HP-04's determinism repair is REAL and I verified it independently.** Three runs of the identical corpus against the identical tree: **84 observed / 15 gaps / 9 dead / 15 unobservable / exit 1 — byte-identical every time.** **Run 1 was a COLD run** -- `git status` was clean at `f431c62` and `specs/current/.effect-conformance-work/` did not exist, so runs 1/2/3 span exactly the cold-vs-warm axis that produced the predecessor's spread. It measured 20 / 15 / 14 gaps across four runs (a 43% spread) and filed it as its own major finding F-1. That finding is closed by measurement, not by assertion. Credit where due. | — (positive) | `scripts/effect_conformance.py` |

---

## 8. Attestation

### 8.1 Row-count reconciliation per sweep

| Sweep | Enumeration command | N (raw) | M (rows) | `N == M` |
|---|---|---|---|---|
| 1 — surface | `git ls-files` → `classify_scope.py` | 14,575 | 14,575 (`sweep1-table.md`) | ☑ |
| 1 — in-model detail | `surface-in-model.txt` | 52 | 52 (§2.1) | ☑ |
| 2 — filesystem | `grep -nE <pattern> $(cat surface-in-model-paths.txt)` | 1,552 → 1,271 collapsed | 8 groups summing 1,271 | ☑ |
| 2 — subprocess | idem | 779 → 191 | 10 groups summing 191 | ☑ |
| 2 — network | idem | 26 → 6 | 6 rows | ☑ |
| 2 — environment | idem | 63 → 45 | 45 accounted (5 real + 40 lexical) | ☑ |
| 2 — clock | idem | 115 → 13 | 13 accounted (4 real + 9 lexical) | ☑ |
| 2 — randomness | idem | 4 → 0 | 0 | ☑ |
| 2 — store | idem | 25 → 6 | 6 rows | ☑ |
| 2 — destructive | idem | 56 → 9 | 9 rows, per-site (§3.8) | ☑ |
| 2 — write sites | `effects-write-sites.txt` | 213 → 208 | 208, per-file counts in §3.1 | ☑ |
| 3 — error paths | `group_behaviors.py` | 830 | 8 groups summing 830 | ☑ |
| 3 — retries | grep | 2 | 2 | ☑ |
| 3 — timeouts | grep | 20 | 20 (4 real + 4 adapter ×3 + 4 budget lines) | ☑ |
| 3 — fallbacks | `group_behaviors.py` | 421 | 5 groups summing 421 | ☑ |
| 3 — concurrency | grep | 2 | 2 | ☑ |
| 3 — config branches | `group_behaviors.py` | 905 | 6 groups summing 905 | ☑ |
| 4 — external surface | `external_surface.py` | 113 | 113 (17 subcommand + 11 positional + 85 option) | ☑ |
| CLI closure | `cli_closure.py` | 34 scripts | 23 reachable + 11 unreachable | ☑ |

No inequality anywhere. Every collapsed count has its rule stated and applied by
a committed script, so a reviewer can recount from the raw file.

### 8.2 Surface NOT walked

- **TLC was not re-run.** The claim "118,573 distinct before and after" is
  instead established **by construction**: stripping `\*` comments from
  `specs/program_model/TlaSpecDevCli.tla` at `b68cbd5` and at `f431c62` yields
  **byte-identical files** (`tla-comment-stripped-diff.txt`), and
  `MC.cfg`/`MCsmall.cfg` are unchanged. The epic's model-semantics delta is
  provably zero, so the state space cannot have moved. This is stronger than a
  re-run, not weaker.
- **The kill test was not run.** Out of scope for a completeness gate, and it
  cannot run inside the effect sandbox (`kill_test.py:598-606`).
- **`generate cases` was not re-run.** The predecessor measured 3,678,217 cases
  at `ab0dfee`; HP-03's `tlc_projection.py` claims 541 (`generation_modes.md:160`).
  **I did not verify that number.** It is the single most decision-relevant
  unverified claim in this epic and I am flagging it rather than repeating it.
- **The 14,504 out-of-model rows were classified from path, not read.** That is
  classification against explicit globs, not coverage.
- Non-source tracked files inside in-model globs: none exist beyond the 12
  already in §2.1.

### 8.3 Rows dispositioned from path/name rather than from reading code

| Sweep | Rows | READ | INFERRED (derived mechanically, not read) |
|---|---|---|---|
| 1 in-model | 52 | **12** | **40** |
| 1 out-of-model | 14,504 | 0 | 14,504 (glob classification) |
| 2 (all categories) | 1,536 collapsed | 24 sites read in context | remainder from the tokenised line + its file's role |
| 3 | 2,180 | 12 | remainder grouped mechanically |
| 4 | 113 | 113 (walked from the live `argparse` tree) | 0 |

**READ in full or in the load-bearing regions — 12 of the 52 in-model rows, plus 2 rows that are not in-model:**
In-model (12): `scripts/tla_spec_dev.py`, `scripts/effect_conformance.py`,
`scripts/effect_conformance_report.py`, `scripts/generate_cases_from_tlc_dump.py`,
`scripts/generate_python.py`, `scripts/run_generated_case_adapters.py`,
`scripts/spec_paths.py`, `scripts/kill_test.py`, `scripts/spec_evolution.py`,
`scripts/onboard_program_model.py`, `specs/current/spec_manifest.yaml` (in full),
`specs/current/TlaSpecDevCli.tla` (index + the 4 actions this epic touches).
Not in-model but read because the report turns on them:
`specs/current/tlc_projection.py` (an ESC-1 row) and
`specs/desired_program_model/ticket_plan.yaml` (scope and rules blocks, in full).

**INFERRED (40)** — dispositioned from the transitive import closure, the
tokenised effect-site enumeration, and the module docstring, *not* from a full
read: the other 24 `scripts/*.py`, `production_adapters.py` ×3,
`adapter_case_runtime.py` ×3, `spec_manifest.yaml` ×2, `TlaSpecDevCli.tla` ×2,
`MC*.cfg` ×6. These are my least reliable rows. Two mitigations: the three spec
trees are md5-identical for every file except `spec_manifest.yaml`, so 8 of the
40 are duplicates of files I read; and every effect site in all 38 is
enumerated mechanically and appears in §3 whether or not I read its
surroundings. **The predecessor reported 52/52 read, 0 inferred. I cannot
claim that, and I am not claiming it.**

### 8.4 Rows whose scope was decided by reasoning rather than a quoted plan line

**19 — and all 19 are reported as ESC-1, not classified.** No row was moved
in-scope or out-of-scope by reasoning. The three escalations exist precisely
because I refused to resolve them.

One methodological choice must be declared: `classify_scope.py` treats the
separator-free globs `*.md` and `*.sh` as applying at **any depth**, because the
plan writes them as file kinds (*"`*.sh` wrappers"*, *"`*.md` — documentation"*).
A strict repo-root-only reading would move **34 rows** (33 `.md` + `scripts/run_tlc.sh`)
out of `out_of_model` and into ESC-1 — chiefly `specs/{current,program_model,desired_program_model}/README.md`
and `tickets/*.md`. That reading is available and I judged it against the plan's
evident intent; if the owner disagrees, ESC-1 grows from 19 to 53 rows and
nothing else in this report changes. The measurement is one command:
`python3 specs/results/coverage-audit-hexagonal-prompting-raw/classify_scope.py .`
with `matches()` restricted to repo-root for separator-free globs.

### 8.5 Could a reader reproduce this row set from the recorded commands?

**☑ Yes.** Six committed scripts under
`specs/results/coverage-audit-hexagonal-prompting-raw/` produce every row set
and every count in this report from a clean checkout of `f431c62`:
`classify_scope.py`, `cli_closure.py`, `module_to_action.py`,
`collapse_effects.py`, `group_behaviors.py`, `external_surface.py`. Every grep
is recorded with its pattern and its output file. The three oracle runs are a
one-line recipe:
`python3 scripts/tla_spec_dev.py --spec-root specs run effect-conformance --target specs/current --cases-dir specs/results/rc02-effect-conformance/corpus-executed`.

### 8.6 Findings about the prompt itself

**Three, and the first is the one that matters.**

1. **`prompts/coverage_audit.md` does not require the row set to be
   language-independent, and the predecessor's convergence to `escalations: 0`
   was an artifact of that gap.** Step 2 says *"Adapt the glob to the project's
   languages (`*.java`, `*.kt`, `*.kts`, `*.sh`, `*.ts`, …)"* — a **source-code**
   enumeration. `cac_ac_classify_v4.py` did exactly that: 6,210 rows over
   `py kt java kts j2 sh`. Its own `in_model` list contains `*.yaml`, `*.tla` and
   `*.cfg` files, which it handled through a *separate* derivation. The
   consequence is precise: **the 19 rows that match no plan line are `.toml`,
   `.yaml` and a `.py` inside a spec tree, and not one of them could ever have
   entered its row set.** A zero-escalation result was structurally guaranteed
   for exactly the artifacts the four oracles consume — the binding table, the
   mutant catalog, the component partition. **Recommend Step 2 mandate
   `git ls-files` with no extension filter**, and classify by plan glob rather
   than pre-filtering by language. This is what the doctrine's own
   "tooling owns enumeration; the agent owns disposition" split implies, and it
   is the sharpest available answer to the known-open self-report problem.

2. **The prompt has no step that checks a carried-forward scope block against
   its predecessor.** `representation_scope:103-107` says it was *"Carried
   forward from the predecessor's final amendment, which took four audit rounds
   to get right."* Two of that amendment's governing rulings — the External-view
   inventory row and the effect-provider-runtime carve-out — **did not survive
   the copy**, and both are load-bearing here (ESC-2, ESC-3, and G-3 hangs off
   ESC-3). A four-round convergence is an asset that a copy-paste can silently
   spend. **Recommend Step 0 add: when the plan says the scope was carried
   forward, diff it against the source and report every dropped line as an
   escalation before classifying a single row.**

3. **The collapsing rule I wrote is honest but not perfect, and the prompt gives
   no way to say so inside a table.** `collapse_effects.py` blanks
   `token.COMMENT` and `token.STRING`, but Python 3.12+ tokenises f-strings into
   `FSTRING_START`/`FSTRING_MIDDLE`, so f-string prose survives as if it were
   code. That is exactly how `onboard_program_model.py:1298` — a
   `subprocess.run` inside a scaffolded-test **template literal** — reached
   §3.2 as row SP-9, and how `spec_evolution.py:241,244` reached §3.7. Three
   false positives in 1,536 collapsed hits (0.2%), all disclosed, none affecting
   a verdict. I am reporting it because a reader recounting from the raw file
   will hit them and is entitled to know they are known.

**On the finding the predecessor filed against this prompt** — *"no notion of a
verdict that is clean but uninformative"* — see §9. That recommendation has not
been implemented in `prompts/coverage_audit.md`; I have implemented it here by
hand, and I would have needed it even at `fail`, which suggests the section
should be unconditional rather than attached to `pass`.

---

## 9. What this verdict does not tell you

> The predecessor asked for this section to be mandatory on a `pass`. This is a
> `fail`, and it is **still** needed — a reader who sees "3 gaps, all narrow,
> all closable in a few lines" would draw exactly the wrong conclusion about the
> state of the toolchain. Sourced from the effect oracle's actual last verdict
> (run 3 of 3, `verify-effect-conformance-run3.txt`).

**The instrument behind this gate reported `unobservable`, three times out of three.**

```
effect declarations: 12 port(s) from specs/current/spec_manifest.yaml
effect conformance unobservable: 84 observed effect(s) over 8 case(s),
  12 declared port(s), 15 gap(s), 9 dead port(s),
  15 unobservable target(s), 0 skipped case(s)          [exit 1]
```

1. **9 of 12 ports are DEAD.** `cli_artifact_delete`, `cli_download`,
   `corpus_process`, `evidence_report`, `git_metadata`, `mutation_write`,
   `runner_process`, `spec_tree_delete`, `test_process` — declared, never
   observed. Only `cli_artifact`, `cli_selftest_process` and `spec_tree` are
   exercised. **The program demonstrably performs most of the dead ones**
   (§3.2, §3.8 enumerate them at `file:line`). So when this report says a site
   is `declared`, that means *a declaration exists and matches by glob* — it does
   **not** mean any oracle has ever confirmed it. For 9 of 12 ports, none has.

2. **0 of the 15 gaps the oracle finds are effects of the action under test.**
   13 are the adapter spawning `tla_spec_dev.py` to replay a case's
   precondition; 2 are writes into the sandbox's own work directory. The oracle
   is measuring its own harness.

3. **The cause is the process boundary, and it is stated by the tool itself**
   (`effect_conformance.py:26` and `:1441`, *"in-process CPython only … No patch
   crosses a process boundary"* — **note the plan cites `:1141-1145`, which was
   correct at `b68cbd5` and is stale at `f431c62`; see F-6**). Every adapter spawns the CLI as a child, so the
   program's real writes happen where the sandbox cannot see them. `known_gaps:137`
   already says this: *"A port for an action whose effects happen in a child is
   dead on arrival and NO added coverage moves it."*

4. **G-1, G-2 and G-3 are therefore gaps no oracle in this toolchain could have
   found, and closing them will not make any oracle greener.** They are gaps in
   what the model *claims*, found by reading the program. That is what this gate
   is for, and it is also the honest limit of what closing them buys.

5. **The second observer produced nothing.** `effect_conformance.py` ships an
   MF-033 out-of-process observer that is meant to reach across the spawn
   boundary (`:38`, `:307`, `:1022`). It emitted **no `OUT-OF-PROCESS
   OBSERVATION` line on any of my three runs**, while all 15 boundaries
   reported `UNOBSERVABLE`. The mechanism exists; on this corpus it recovers
   nothing.

6. **`case_codegen.generation_status` is still `planned`** in all three trees.
   The 8 executed cases come from a corpus RC-02 committed under
   `specs/results/`, not from a generated package this model ships.

7. **What did move:** HP-04's determinism repair is real and independently
   verified (F-5). The gap count is now stable at 15 across runs where the
   predecessor measured a 43% spread. That is a genuine improvement to the
   instrument, and it is the epic's clearest technical win in the modeled
   surface.

---

## 10. The judgement you asked for, separately from the verdict

> *Is any remaining unmodelled surface load-bearing for GENERATING CASES or for
> the ORACLE seeing effects — as opposed to bookkeeping fidelity about our own
> CLI?*

**Almost all of it is bookkeeping. There is exactly one exception, and it is an
escalation rather than a gap.**

| Remaining unmodelled surface | Load-bearing for generation? | For effect observation? |
|---|---|---|
| **G-1** — `--work-dir` outside `**/specs/**` | No | **Marginally yes** — an unconstrained work dir is where the oracle's own writes land, and the sandbox already reports 2 of its 15 gaps against that directory |
| **G-2** — `--no-batch` child spawns, temp work tree | No | **No, and worse: it is a new process boundary.** Declaring it would make the model honest and would not let the sandbox see one additional byte |
| **G-3** — codegen writes the binding table | No | No |
| The 9 wrapper/close/start/scaffold scripts | No | No |
| External view (ESC-2) | **Structurally yes, and structurally unavailable** — `max_external_cases_per_action: 50` is declared and unreachable, because there is no External view to generate from. But `MF-023` measured `Q = 0.012` with no clean cut; this needs a decomposition, not a coverage fix |
| **`specs/current/tlc_projection.py` (ESC-1)** | **YES — decisively.** This is the one row where the answer is not bookkeeping | No |
| Clock / environment reads (F-2) | No | No — the schema cannot express them |
| `tlc_seconds` never read (F-1) | No | No |

**The one exception, stated plainly.** `specs/current/tlc_projection.py` is not
peripheral surface that happens to be unclassified — **it is the mechanism that
makes case generation possible on this model at all.** Without it, `MCsmall.cfg`
(the config that exists *so that* a corpus is tractable) yields 3,678,217 cases
and a 7.4 GB `cases.py` CPython cannot import, 18,391× the manifest's own cap.
With it, the epic claims 541 cases and 667 KB. It is `desired_boundaries:130`
delivered. And the scope block this gate reads **cannot classify it**: it is not
`scripts/**/*.py`, not `spec_manifest.yaml`, not `TlaSpecDevCli.tla`, not a
`MC*.cfg`, not `production_adapters.py`, not `adapter_case_runtime.py`. It also
exists in only one of the three spec trees.

That is not a call to model it. It is a call to *classify* it, in one plan line,
so the next audit can see the thing this epic actually built.

**Everything else confirms the predecessor's read, and confirms your redirect.**
Coverage and generation remain opposed on this model — the epic's answer to that
was a **projection**, not more coverage, and that was the right instinct. The
oracle remains blind across the process boundary, and G-2 shows the toolchain
*adding* process boundaries rather than removing them. Two of the three gaps I
found are declaration bookkeeping about our own CLI, worth a short fix and
nothing more.

**My read: close on a small honest number.** Three gaps, two of them a few lines
each; three escalations, two of them a restored sentence each. The expensive
thing in this report is not the gap list — it is §9, and no amount of coverage
work moves it.

---

## 11. Verdict

- In-scope gaps: **3**
- Out-of-scope inventoried: **14,504**
- Escalations: **3**
- Gaps created by this epic's own diff: **2** (G-1 HP-04, G-3 HP-05)
- **Verdict: `FAIL`**

`FAIL` blocks promotion until every in-scope gap is closed by modeling it or
changing the program. Resolving ESC-3 in the owner's favour retires G-3 by a
visible boundary amendment rather than a per-finding waiver; G-1 and G-2 stand
regardless of how any escalation is resolved.

The proposed ledger block is at
`specs/results/coverage-audit-hexagonal-prompting-raw/coverage_audit_ledger_input_proposed.yaml`
and is **NOT applied**. A gate that edits the ledger it reports into is the
self-clearing this doctrine forbids.

---
---

# ROUND 2 — targeted re-verification at `0a05eed`

- **Scope source:** `specs/desired_program_model/ticket_plan.yaml:102-146` (`representation_scope` @ schedule_revision 3, commit `475bc9a`)
- **Model audited:** `specs/program_model/TlaSpecDevCli.tla` @ `0a05eed` — 11 variables, 18 `Next` disjuncts, 17 `@command` actions, **14 ports**
- **Date:** 2026-08-04
- **Verdict:** **`FAIL`** — 1 of 3 gaps remains open

Targeted, not a fresh sweep: round 1's enumerations stand, and the model
semantics have not moved. What was re-run is listed in §R8.

| | round 1 (`f431c62`) | **round 2 (`0a05eed`)** |
|---|---|---|
| Verdict | `fail` | **`fail`** |
| In-scope gaps | 3 | **1** |
| Escalations | 3 | **0** |
| Row set | 14,575 | **14,658** |
| In-model surface | 52 | **57** |
| Declared ports | 12 | **14** |
| **Dead ports (oracle)** | **9** | **11** |
| Suite (clean tree) | 1,122 | **1,123** — and the `+1` is my own round-1 evidence file, not a new test (§R6) |

---

## R1. G-1 — **CLOSED**, by a declaration I think is the wrong width

**Status: closed as a coverage gap. Not closed as a good declaration.**

The gap I filed was *"the declaration is narrower than the behaviour"*. It no
longer is: `case_work_dir_delete` (`filesystem.delete` → `**`) is declared on
`RunEffectConformance` (`spec_manifest.yaml:260-271`, `TlaSpecDevCli.tla:526-533`),
and `**` accepts the delete at `effect_conformance.py:1685` wherever `--work-dir`
points. **No undeclared effect remains on that path. G-1 is closed and I am not
re-counting it.**

### You asked whether `**` is too permissive to be a real declaration. **Yes.**

Verified mechanically (`reverify_port_globs.py`, `reverify-port-glob-check.txt`).
`_target_matches` (`effect_conformance.py:513-524`) collapses `**` → `*`, and
`fnmatch`'s `*` crosses separators, so **`target: "**"` accepts every string** —
`/`, `""`, `/Users/me/important-project`, everything.

Two consequences, both concrete:

1. **It switches off the check for that action.** The manifest's rule is *"an
   observed effect matching no port declared for its action is a GAP"*. With a
   `filesystem.delete` port at `**`, **no delete `RunEffectConformance` ever
   performs can be a gap** — including the exact regression
   `reset_case_work_dir`'s docstring exists to prevent. The docstring
   (`:1678-1681`) says: *"Only the per-case subdirectory is removed … leaving
   the parent alone is what keeps `--work-dir` a directory the caller can point
   anywhere without the oracle emptying it."* If a future edit deletes the
   parent instead, `**` declares it and the oracle reports clean.
2. **It subsumes `spec_tree_delete` on the same row.** Both are
   `filesystem.delete`; `**` accepts every target `**/specs/**` accepts. That row
   entry can no longer be the unique explanation of anything.

**The manifest's own precedent does not cover this.** `cli_artifact`,
`cli_download` and `corpus_process` use `*` with a stated test — *"any glob
narrower than `*` would assert a constraint the code does not enforce"*. Here the
code **does** enforce a constraint, and documents it as a designed invariant:
the deleted path is always exactly one level below a caller-supplied root, and
never the root. `**` fails that test. HP-04's declaration was narrower than the
behaviour; this one is wider. **Same defect class, opposite sign.**

### Did I close this the wrong way? Partly — my disposition was wrong, and so is the replacement

**Your revert was right in direction and I was wrong to propose the constraint.**
`--work-dir` is documented as pointable, the per-case dir is scratch, and forcing
scratch into `specs/` would have made the model's own directory a dumping ground.
I should have seen that from the docstring, which predates my report.

**One correction to the evidence, though:** the three callers that broke are all
**tests** — `tests/test_effect_conformance.py:1263` (`work_dir="/tmp/w"`), `:1331`,
`:1532` (`tmp_path / "work"`). The only non-test caller of `execute_corpus` is
`effect_conformance_report._execute_corpus:153`. Tests are out-of-model by
`ticket_plan.yaml:130`, so *"it broke three legitimate callers"* is not itself
evidence about shipped behaviour. The flag's documented contract is, and that
argument stands on its own.

### The third option neither of us took, which I think is the right one

Neither "constrain the flag" nor "widen to `**`". **Give the delete a path shape
the glob can express, which the sibling runner already does.**
`run_generated_case_adapters.py:1256` puts per-case trees under a fixed
`case-work/` component; `effect_conformance.reset_case_work_dir:1683` does not.
Change `case_dir = Path(work_dir) / case_name` to
`Path(work_dir) / "case-work" / case_name` and declare:

```yaml
case_work_dir_delete:
  type: filesystem.delete
  target: "**/case-work/*"          # not "**"
```

`--work-dir` stays pointable anywhere, the three tests keep passing, and the
declaration becomes **falsifiable again**: a delete of the parent, or of anything
outside a `case-work/` directory, is a gap. That is a small program change plus a
narrower glob, and it makes the two runners consistent with each other.

---

## R2. G-2 — **NOT CLOSED.** The new port cannot match the spawn, and the write half was never addressed

### R2.1 The glob is off by one character

`case_program_process` declares `target: "*programs/case_*"` — **underscore**.
The shipped path component is built by
`run_generated_case_adapters._opaque_path_component:1358`:

```python
return f"{role}-{hashlib.sha256(payload).hexdigest()[:32]}"     # role='case'  ->  "case-<hex>"
```

— **hyphen**. So the program is `<work_dir>/programs/case-<32 hex>.py`, the
recorded spawn target (`_command_target:1071-1076` joins argv with spaces) is
`<python> <work_dir>/programs/case-<hex>.py`, and:

```
case.name = 'case_0002_install_local_cli'
  recorded target = /opt/homebrew/.../python3.14 /var/.../programs/case-182e6983c2ecf596e977c78e1c118b7a.py
  matches '*programs/case_*' -> False
```

**False for every case name tested, and false for all of them by construction** —
the component never contains `case_`. Reproduced with the oracle's own matcher in
`reverify_port_globs.py`; raw output in `reverify-port-glob-check.txt`.

| glob | accepts the real target? |
|---|---|
| `*programs/case_*` (shipped) | **False** |
| `*programs/case-*` | True |
| `*/programs/*` | True |

**The effect at `run_generated_case_adapters.py:2178` therefore still matches no
declared port. G-2's spawn half is open, and the port is dead by construction —
not because no case exercises it, but because no case *can*.**

One-character fix: `target: "*programs/case-*"`. What is actually missing is the
test — see R6.

### R2.2 The write half was not addressed at all

G-2 as filed had two halves. The closure added a `process.spawn` port and nothing
else. `RunSpecUnitTests` is now
`[test_process, runner_process, spec_tree, case_program_process]`, and with no
`--work-dir` the runner still does `work_dir = tempfile.mkdtemp(...)`
(`:2294`) and writes:

- `<work_dir>/programs/case-<hex>.py`, one per case (`:1255`)
- `<work_dir>/case-work/case-<hex>/` (`:1256`)

both outside `spec_tree` (`**/specs/**`) and `evidence_report` (`**/results/**`).
**No declared write port accepts them.** Undeclared, unchanged from round 1.

### R2.3 Was `--no-batch` even in scope? The closure answers a question the plan does not

`semantic_model_rule:48-49` puts *"per-flag variants"* out-of-model except six
guard-weakening flags it never enumerates. `--no-batch` (`tla_spec_dev.py:537`)
appears **nowhere else in the repository** — no doc, no adapter, no corpus
command. A reading exists on which G-2 was always inventory.

**You resolved it by declaring a port, which rules that an out-of-model flag
branch still owes a port for its effects.** I think that is the right ruling and
it is consistent with the standing proviso's spirit. But **the plan does not say
it**, and the standing proviso is written about FILES, not flags. One sentence in
`semantic_model_rule` would make the ruling quotable by the next audit instead of
inferable from a commit.

---

## R3. G-3 — **RETIRED**, verified rather than accepted

You asked me to test the retirement against the standing proviso rather than take
it. Three checks, all mechanical:

1. **The carve-out exists and covers the file.** `ticket_plan.yaml:145` restores
   *"`scripts/run_generated_case_adapters.py` provider machinery,
   `scripts/generate_python.py` codegen … out-of-model"*.
2. **No modelled action reaches the codegen path.** `cli_closure.py` re-run at
   `0a05eed`: `generate_python` is still unreachable from `tla_spec_dev.py`. Its
   only in-repo importer is `generate_docs.py:14`, itself unreachable; the only
   other mention is a docstring at `scaffold_spec.py:5`. **No modelled action
   spawns or imports it** — `grep -rn generate_python scripts/ specs/*/production_adapters.py`
   returns exactly those two lines.
3. **So the proviso does not fire.** The write at `generate_python.py:891` is not
   performed on a modelled action path, and no port is owed. **G-3 genuinely
   retires.**

**Tripwire, recorded because the retirement is conditional and nothing enforces
the condition:** the moment `generate python` becomes a CLI subcommand — or any
modelled action imports the codegen — G-3 reopens automatically, and it will
reopen silently, because no test asserts that `generate_python` stays outside
`build_parser`'s import closure. `cli_closure.py` is committed and is that test
if you want it.

Note the shape the plan now holds, which is coherent but load-bearing:
`specs/*/case_adapters.toml` is **in-model** (`:126`) while the only module that
mutates it is **out-of-model** (`:145`). That is fine exactly as long as check (2)
holds, and no longer.

---

## R4. Escalations — **genuinely answered**, with one precedence gap

Re-run of the partition against schedule_revision 3
(`classify_scope_v2.py`, `reverify-scope-partition.txt`):

```
[specific-wins] N=14658 M=14658  IN=57  OUT=14599  CONFLICT=2  ESCALATION=0
[in-wins]       N=14658 M=14658  IN=59  OUT=14599  CONFLICT=0  ESCALATION=0
```

**ESC-1 — answered, all 19 rows.** Every round-1 escalation now classifies, and
the classifier prints each one against its new line. `specs/*/tlc_projection.py`
IN (`:128`), `case_adapters.toml` IN (`:126`), `kill_mutants.toml` IN (`:127`),
`architecture_*.yaml` OUT (`:142`), plan artifacts OUT (`:143`), root config OUT
(`:144`). **Still unclassified: 0.** Swept the 5 newly-in-scope files for effect
surface: **zero hits** — `tlc_projection.py` imports only `typing.Any` and
defines two pure functions; the two `.toml`s are declarations. The scope
expansion creates no new gap.

**ESC-2 — answered.** `representation_scope.view_split:146` restores the ruling,
nested under the block the procedure reads, so Sweep 4 now has a line to classify
against. §5.2's External rows become inventory under it rather than an
escalation. This is the row-count consequence I flagged, closed by one sentence.

**ESC-3 — answered, but the plan does not state precedence.** The carve-out at
`:145` overlaps `in_model: scripts/**/*.py` at `:122`, so a mechanical classifier
must guess which wins. **It does not change any verdict** — both readings give
`ESCALATION=0`, and the amendment's own words ("that asymmetry was an accident of
copying") make the intent unambiguous. But `classify_scope_v2.py` reports 2
CONFLICT rows under specific-wins, and the next auditor will hit the same fork.
One clause — *"a named file in `out_of_model` overrides a directory glob in
`in_model`"* — removes it. **Minor, and not an escalation.**

**On the correction you recorded.** You wrote the structural-guarantee finding
into the plan and attributed it. For the record, the amendment's own framing is
the right one and I would not soften it: a carried-forward scope block must be
diffed against its source, not copied and trusted.

---

## R5. What the closure cost, swept as surface

**No code changed.** `git diff --name-only f58d2a2..0a05eed -- 'scripts/*.py' 'specs/*/production_adapters.py' 'specs/*/adapter_case_runtime.py' 'specs/*/tlc_projection.py'` is **empty**. The closure is declarations, catalogue, two test constants, plan and docs.

**Model semantics unmoved, proved not asserted.** `specs/program_model/TlaSpecDevCli.tla` is **byte-identical at `b68cbd5` and `0a05eed` after comment stripping**; `MC.cfg`/`MCsmall.cfg` unchanged. The `@port` lines are `\*` comments. TLC cannot have moved.

**The two new mutants apply and revert** (`reverify_mutants.py`, `reverify-mutants.txt`) — checked in all three trees:

| mutant | file | `find` occurrences | applies | reverts byte-for-byte | refine |
|---|---|---|---|---|---|
| `port-case_work_dir_delete` | `effect_conformance.py:1685` | **1** | yes | **yes** | `effect_conformance` / `RunEffectConformance` |
| `port-case_program_process` | `run_generated_case_adapters.py:2178` | **1** | yes | **yes** | `ticket_state` / `RunSpecUnitTests` |

`refine_variable` corrections land correctly (`effect_conformance` for the oracle
mutant matches the variable that carries its verdict; `ticket_state` for the
runner mutant matches the existing `port-test_process` precedent).
`run kill-test --list-boundaries` → **`28/28 declared boundaries carry a seeded
fault.`**, exit 0, zero `NO MUTANT`, and **the production tree is unmutated
afterwards** (`git status` clean). 14 declared ports, 14 port mutants, none
missing.

**But both new mutants are structurally un-killable by the shipped corpus:**

- `port-case_program_process` seeds a fault at `:2178`, on the `--no-batch`
  branch. `tla_spec_dev.py:369-370` appends `--batch` unless `--no-batch` is
  passed, and `--no-batch` appears nowhere in the repository outside its own
  argparse line. The mutated line **never executes**, so the mutant is a
  guaranteed survivor against any documented corpus command.
- `port-case_work_dir_delete` seeds "the work dir is not emptied between cases".
  Its symptom is *cross-run* nondeterminism (the MF026-R4-F-01 defect). A corpus
  executed once cannot observe it.

Neither is a coverage gap. Both mean the kill rate will move down, not up, if
oracle 4 is ever run against this catalogue — worth knowing before, not after.

**Citations: clean.** All **84** content-anchored citations across the three
manifests and three model files resolve, checked independently of
`tests/test_source_citations.py` (`reverify_citations.py`). The three new ones
are exact: `effect_conformance.py:1685 (shutil.rmtree)`,
`:1809 (reset_case_work_dir)`, `run_generated_case_adapters.py:2178 (subprocess.run)`.

---

## R6. Findings from round 2

| # | Finding | Severity |
|---|---|---|
| **F-7** | **`case_work_dir_delete` target `**` is too permissive to be a declaration.** It accepts every string, switches off gap detection for every `filesystem.delete` on `RunEffectConformance`, and subsumes `spec_tree_delete` on the same row. The manifest's `*`-glob precedent does not apply, because here the code *does* constrain the target and documents the constraint as a designed invariant. Fix in R1. | **major** |
| **F-8** | **Both new ports report DEAD MODEL SURFACE.** Dead ports **9 → 11** of 14, two oracle runs, identical. Distinguish the causes: `case_work_dir_delete` is dead because the reset runs *outside* the sandbox window (`:1809` resets, `:1824` enters), so no corpus could ever exercise it; `case_program_process` is dead because its glob cannot match. Both are HARD FAILURES by the manifest's own rule, and both are attributable to this closure. | **major** |
| **F-9** | **The closure added zero tests that could detect a wrong glob.** The only test changes are two literal counts (`26 → 28`, `test_kill_test.py:734,813`) — precisely the assertions that pass whether or not a port is correct. `grep -rn '_target_matches\|target_matches' tests/` returns **nothing**: no test anywhere asserts that a declared glob accepts a target the shipped code actually produces. One such test, parametrised over the 14 ports, would have caught F-8's second half before commit. **This is the single highest-value follow-up in this report.** | **major** |
| **F-10** | **`ticket_plan.yaml:165` still cites `effect_conformance.py:1141-1145`** for "in-process CPython only". Round 1 filed this as F-6; the plan was amended at schedule_revision 3 and the citation was not fixed. Line 1141 is now an `OutOfProcessObservation` field; the text is at `:1441`. `tests/test_source_citations.py` still does not cover `ticket_plan.yaml`. | minor |
| **F-11** | `semantic_model_rule` does not say whether an out-of-model **flag branch** owes a port for its effects. The standing proviso is written about files. The G-2 closure rules "yes" by action; one sentence would make it quotable. Related: the plan names *"the six guard-weakening flags"* and never enumerates them. | minor |
| **F-12** | **The `+1` in the suite count is my own evidence.** 1,122 at `f431c62`, 1,123 at `0a05eed`, both measured in a **fresh worktree**. `tests/test_spec_yaml_valid.py::test_spec_yaml_parses` is parametrised over discovered YAML, and round 1's `coverage_audit_ledger_input_proposed.yaml` is one more file to parse. **The closure added no test.** (Also: running the oracle leaves `specs/current/.effect-conformance-work/` behind, which inflates that parametrisation by ~94 — removed after each run here.) | informational |

Round-1 findings F-1, F-2, F-4, F-5 stand unchanged. F-3 is superseded by F-8.

---

## R7. Did I close these the wrong way? — plainly

- **G-1: your call was better than mine, and the width is still wrong.** Reverting
  my disposition was correct and I would not argue it back. `**` is not a
  declaration, it is the absence of one written in the declaration's slot. R1
  gives a third option that keeps your direction and restores falsifiability.
- **G-2: declaring rather than constraining was right; the declaration is wrong.**
  Your reasoning — *"forcing it into the spec tree would move real execution
  output into the model's own directory"* — is correct and I accept it over my
  proposal. But the port does not match, and half the gap was not addressed.
- **G-3: right, and verified.**
- **The escalations: genuinely answered, not answered-looking.** I re-ran the
  partition rather than reading the amendment: 19 of 19 classified, 0 remaining,
  under both readings of the one overlap.
- **The pattern worth naming.** Round 1 found a declaration narrower than the
  behaviour. Round 2 found one wider than the behaviour and one that misses it by
  a character. Three declaration/behaviour mismatches in three consecutive
  attempts, none catchable by any shipped test. **F-9 is the fix for the class,
  and it is cheaper than any of the individual repairs.**

---

## R8. What was re-run, and what was not

**Re-run:** the scope partition against the amended block (both readings); the
CLI import closure; the effect oracle ×2; `run kill-test --list-boundaries`; the
mutant apply/revert check ×3 trees; the citation check (84); the TLA
comment-stripped equality proof; the full suite in a **fresh worktree** at
`f431c62`, `f58d2a2` and `0a05eed`; an effect sweep over the 5 newly-in-scope
files; the port-glob match check against the oracle's own matcher.

**Not re-run, deliberately:** Sweeps 2 and 3 in full — no code changed, so round
1's 1,536 collapsed effect sites and 2,180 behaviour rows are unchanged by
construction. TLC — proved unnecessary by byte equality. `generate cases` — the
541-case figure remains **unverified**, as in round 1, and remains the most
decision-relevant unverified claim in this epic. Oracle 4 end-to-end — it cannot
run inside the effect sandbox (`kill_test.py:598-606`), and running it seeds
faults into production source.

**Read vs inferred:** 8 files read in the load-bearing regions this round
(`effect_conformance.py`, `run_generated_case_adapters.py`, all three
`spec_manifest.yaml` diffs, `TlaSpecDevCli.tla` diff, `kill_mutants.toml`,
`ticket_plan.yaml` amendment, `tlc_projection.py`). Every claim above is backed
by a committed reproducer.

---

## R9. What this verdict does not tell you (kept, per your instruction)

Unchanged in substance from round 1, and **worse on one axis**:

```
effect conformance unobservable: 84 observed effect(s) over 8 case(s),
  14 declared port(s), 15 gap(s), 11 dead port(s),
  15 unobservable target(s), 0 skipped case(s)          [exit 1, both runs]
```

- **11 of 14 ports are now DEAD**, up from 9 of 12. Only `cli_artifact`,
  `cli_selftest_process` and `spec_tree` are ever exercised. **Declaring more
  made the dead-surface number worse, not better** — which is the honest price of
  closing a coverage gap on a model whose oracle cannot reach the actions the
  new ports belong to.
- **0 of the 15 gaps are effects of the action under test.** Unchanged: 13 are
  the adapter replaying preconditions, 2 are the sandbox's own work dir.
- **The verdict is still `unobservable`, exit 1.** Neither closure moved it, and
  neither could: `RunEffectConformance` and `RunSpecUnitTests` are not among the
  8 executed cases, and the MF-033 out-of-process observer emitted nothing.
- **So "declared" still means "a declaration exists and matches by glob"** — and
  F-8 shows that for one of the two new ports it does not even mean that. Nothing
  in this toolchain would have told you. I found it by reproducing the oracle's
  matcher against the shipped path builder, not by running a gate.
- **Determinism holds.** 84/15/11 identical across both runs — HP-04's repair
  survives the closure.

**Read this as: the model is now more honest about two effects it performs, one
of those two declarations is wrong, and the instrument that would tell you still
cannot see either action.**

---

## R10. Round-2 verdict

- In-scope gaps: **1** — G-2 (spawn glob does not match; write half never declared)
- Escalations: **0**
- Gaps created by the closure: **0** (F-7 and F-8 are declaration-quality
  findings, not unmodelled surface — counting them would inflate)
- Out-of-scope inventoried: **14,599**
- **Verdict: `FAIL`**

G-2 is a one-character glob fix plus one write port. What I would not ship
without is **F-9** — the test that asserts every declared glob accepts a target
the shipped code actually produces. Three declaration/behaviour mismatches in
three attempts is a class, and it is the only finding here that closes the class
rather than an instance.

The updated ledger block is at
`specs/results/coverage-audit-hexagonal-prompting-raw/coverage_audit_ledger_input_proposed.yaml`
and remains **NOT applied**.
