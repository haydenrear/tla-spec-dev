# Coverage Audit Report — close 2 (workflow close, complexity-descriptor-main-readiness; promotion gate for the main merge)

- **Epic / workflow:** `epic/complexity-descriptor`, workflow
  `complexity-descriptor-main-readiness` (CD-04..CD-08 all done and merged,
  PRs #94-#98; effect-provider epic merged at 86865d2; integration
  497ab99/37c6c65; owner spot-fixes e7fcd09; finalization prep db78854)
- **Scope source:**
  - `specs/desired_program_model/ticket_plan.yaml` (schedule_revision 2, at
    HEAD e2fdfa7) — cited below as **CP:NN**: `semantic_model_rule` `CP:49`;
    `case_execution_rule` `CP:53`; `service_catalog` `CP:63-82` (`CP:80` =
    the AMENDED 2026-07-23 known_gaps entry); ticket `implementation_scope`
    blocks `CP:128-132` (CD-04), `CP:199-202` (CD-05), `CP:270-273` (CD-08),
    `CP:338-340` (CD-06), `CP:419-425` (CD-07).
  - `specs/.history/complexity-descriptor-epic/closed-snapshot/snapshots/desired_program_model/ticket_plan.yaml`
    — cited below as **PS:NN**: the predecessor workflow's sealed plan
    carrying the recorded owner rulings this batch inherits
    (`PS:520-562` amended `semantic_model_rule`; `PS:576-599`
    `service_catalog` + known_gaps). Incorporation basis: the current plan's
    header declares itself "Successor to the closed complexity-descriptor-epic
    workflow (snapshot in specs/.history/)" (`CP:7-8`), `CP:80` cites "this
    plan's semantic_model_rule" for the same out-of-model doctrine, and the
    dispatching instruction records that the predecessor audits (runs 2-5)
    "settled the scope boundary through recorded owner rulings" which are not
    to be re-litigated. **See ESC-C2-1 (§6.5): the successor plan does not
    restate those rulings in its own text.**
- **Model audited:** `specs/current/TlaSpecDevCli.tla` @ HEAD `e2fdfa7`
  (byte-identical to 5f84937, the run-5 PASS SHA — §1)
- **Date:** 2026-07-23
- **Verdict:** **`PASS`** — 0 in-scope gaps; 1 advisory escalation surfaced
  (ESC-C2-1, scope-text hygiene, not a coverage hole), unresolved by this
  audit as required.

> This audit checks **completeness of what is modeled**, not fidelity
> (`prompts/coverage_audit.md`). Predecessor audits: runs 2-5 under
> `specs/results/epic-close/` (run 5 PASS, 0 gaps, at 5f84937). This run is a
> **FRESH full enumeration** — the surface changed by ~213 net files since
> run 5 (effect-provider merge + batch), so verify-by-diff was explicitly not
> licensed. Raw outputs: `specs/results/finalization/sweep-raw-close2/`.
> Row rules are applied by `sweep-raw-close2/cac2_classify.py`; a reader
> running it against the archived raws reproduces every table.

## 0. Declared scope (quoted verbatim; I did not choose it)

### 0.1 Current plan — `specs/desired_program_model/ticket_plan.yaml`

```yaml
# CP:49
  semantic_model_rule: Do not add test graph nodes, pytest jobs, CI workflow steps, integration harnesses, or validation scripts as TLA+ program state/actions. The CLI's own workflow commands ARE program behavior for this repository.
# CP:53
  case_execution_rule: The fuzzing machinery is EXPERIMENTAL and not product validation — do not run case generation, the corpus, effect conformance, or the kill test as ticket validation (CD-08 exercises the example's documented generation path as its ACCEPTANCE surface, which is different from product validation).
```

```yaml
# CP:63-82
service_catalog:
  existing_boundaries:
    - tla-spec-dev CLI (scaffold/open/run/analyze/close)
    - scripts/analyze_complexity.py complexity descriptor
    - scripts/fitness_functions.py advisory fitness rules
    - scripts/corpus_diagnostics.py corpus gate (EXPERIMENTAL fuzzing surface)
    - examples/distributed_history ticket-workflow example
  desired_boundaries:
    - corpus gate speaks findings + a redesign question, never a prescriptive move
    - descriptor domain resolution covers operator-defined sets, wrapped conjuncts, and multi-view invariant naming
    - R/W matrix attributed to top-level actions through called operators
    - scaffold/UX language consistent with the advisory doctrine
    - the shipped example passes its own documented workflow out of the box
  adapter_boundaries:
    - specs/program_model/production_adapters.py spec-unit adapters
    - test_graph specWorkflow / cliWorkflow graphs
  known_gaps:
    - "AMENDED 2026-07-23 (owner, pre-finalization; schedule_revision 2): the effect-provider epic merged at 86865d2 with zero host-model delta. Its runtime (scripts/run_generated_case_adapters.py provider machinery, spec_double_compiler/*, templates/python/ports.py.j2, scripts/fitness-era extensions) is SHIPPED validation harness and toolchain plumbing — out-of-model per this plan's semantic_model_rule first sentence, exactly as the spec-unit runner always was. examples/effect_providers/* are EXPERIMENTAL validation fixtures carrying 12 recorded, unwaived model-completeness gaps (specs/.history/effect-provider-epic/open-state-at-merge/README.md); their models are promotion-blocked and never enter specs/program_model. Owner-direct commits after CD-07 (merge 86865d2 + integration 497ab99/37c6c65/e7fcd09 spot fixes, validation evidence) are recorded finalization amendments: zero TLA model delta, full-suite + provider-validation green at each."
    - "Suggestions removed by CD-01 may return in a later epic, earned from real-app descriptor observations, possibly as an agent. Not in this batch."
```

Ticket `implementation_scope` blocks (verbatim):

```yaml
# CP:128-132 (CD-04)
    implementation_scope:
      - scripts/corpus_diagnostics.py (finding + redesign question output)
      - scripts/tla_spec_dev.py (analyze corpus help text)
      - tests/test_corpus_diagnostics.py (assert question form, no prescriptive move)
      - references/modular_fuzzing.md (corpus gate description)
# CP:199-202 (CD-05)
    implementation_scope:
      - scripts/analyze_complexity.py (_set_size, infer_dimensions, domain-source precedence)
      - tests/test_analyze_complexity.py (three regression tests, failing pre-fix)
      - references/architecture_tractability.md (document the resolver's coverage)
# CP:270-273 (CD-08)
    implementation_scope:
      - examples/distributed_history/ (manifest caps + scripts + READMEs)
      - examples/run_distributed_history_validation.py (target-path parameter)
      - scripts/export_testgraph_cases.py (manifest resolution / loud failure)
# CP:338-340 (CD-06)
    implementation_scope:
      - scripts/analyze_complexity.py (action attribution / matrix construction)
      - tests/test_analyze_complexity.py (both-direction regression tests)
# CP:419-425 (CD-07)
    implementation_scope:
      - scripts/new_ticket_workflow.py (scaffold wording)
      - scripts/fitness_functions.py + scripts/tla_spec_dev.py (manifest-rules CONFIG ERROR path)
      - scripts/budgets.py (retired keys)
      - scripts/analyze_complexity.py (sentinel warning wording)
      - scripts/run_tlc.sh (states/ scratch dir)
      - references/fitness_functions.md, references/complexity_intuition.md, references/architecture_tractability.md, SKILL.md (schema docs + boundary sharpening)
```

### 0.2 Predecessor rulings — sealed snapshot (recorded owner text, quoted fresh this run)

`PS:520-562` (`semantic_model_rule`, amended twice by the owner) — re-read in
full this run; the operative rulings, with their sub-ranges as cited in every
row below:

- `PS:521-522` — "Do not add test graph nodes, pytest jobs, CI workflow
  steps, integration harnesses, or validation scripts as TLA+ program
  state/actions."
- `PS:524-525` — "the modeled program surface is the SHIPPED CLI lifecycle —
  scaffold, open, run spec-unit-tests, analyze (descriptor scan), close."
  (The totality reading of this line — everything outside the lifecycle
  closure is out-of-model — was attested in runs 3-5 and is carried; §8.4.)
- `PS:530-533` — "Advisory tooling internals — fitness-function evaluation
  inside analyze, silent-degrade guard branches, the runner's env re-exec —
  are declared out-of-model as transcription".
- `PS:538-542` — ESC-6 correction: "the experimental fuzzing surface REMAINS
  MODELED where it already is — AnalyzeCorpus, RunEffectConformance,
  RunKillTest, their state and gates ... What stays unmodeled is `generate` —
  a RECORDED LIMITATION".
- `PS:544-551` — granularity ruling: "per-command refusal branches beyond
  those ... and per-flag variants (--accept-new, --allow-open,
  --no-promote-current, --validate-only, --force, --dry-run) are
  OUT-OF-MODEL as a recorded granularity limitation".
- `PS:551-554` (ESC-1, ledger close refusal = validation harness),
  `PS:554-557` (ESC-3, "the close/start/scaffold wrapper scripts, run_tlc.sh,
  and the desired-tree adapter copies are toolchain plumbing, out-of-model;
  their destructive deletes must still be DECLARED as ports where a modeled
  action performs them"), `PS:557-558` (ESC-5), `PS:559-560` (ESC-7,
  clock/provenance reads on the close path out-of-model).

`PS:596-599` (`known_gaps`):

```yaml
    - "AMENDED 2026-07-22 (ESC-2): this repository's baseline remains a single TlaSpecDevCli.tla module without the Internal/External view split. The MF-023 dogfooding ticket (concluded epic) measured modularity Q=0.012 — no clean cut — and deliberately did NOT decompose; that decision stands. The view split is FUTURE WORK, unscoped to any current ticket; the dangling Core/Internal/External source_model references in spec_manifest.yaml are removed by CD-10 (DF-3) rather than left pointing at files that do not exist."
    - "`generate` is unmodeled — recorded granularity limitation per the amended semantic_model_rule; modeled if/when the experimental surface is promoted."
    - "Per-command refusal branches beyond the modeled gate verdicts, and per-flag CLI variants, are out-of-model — recorded granularity limitation per the amended semantic_model_rule."
```

**Closure rule applied:** file-only scoping; a directory counts only when the
plan writes one (CD-08's `examples/distributed_history/` carries a trailing
slash — the one directory grant in this plan). No filter dropped any
plan-named path (§2).

## 1. Model representation index (re-derived fresh)

Corrected regex `grep -cE '^[A-Za-z_][A-Za-z0-9_]*(\(.*\))?[[:space:]]+==' specs/current/*.tla`
→ **N = 41** (the prompt's single-space variant still yields 36 — prompt
defect STILL open, §8.6). `git diff 5f84937..HEAD` over
`specs/current/{TlaSpecDevCli.tla,MC.cfg,kill_mutants.toml,case_adapters.toml}`
is **empty** — the module is byte-identical to the run-5 PASS state, so the
index is line-for-line run 5's: **15 actions** (14 `@command` + Stutter),
**13 invariants**.

| Kind | Fresh state | Evidence |
|---|---|---|
| Ports (**9**) | `spec_tree` :110-112, `evidence_report` :113-115, `cli_artifact` :116-118, `test_process` :129-131, `runner_process` :140-142, `spec_tree_delete` :151-153, `git_metadata` :159-161, `mutation_write` :176-178, `corpus_process` :187-189 | `specs/current/spec_manifest.yaml` (read fresh; line numbers shifted from run 5 by the status-header rewrite only) |
| Action→port map | **14 of 14** @command actions mapped (`spec_manifest.yaml:190-237`); two deliberately EMPTY rows with recorded rationale: `RecordBudgets: []` :202, `AnalyzeCorpus: []` :216 | fresh read |
| Bindings | `case_adapters.toml` unchanged since 5f84937 (git diff clean); `grep -c 'adapter = '` → **14** = the @command action set | fresh |
| `actions.yml`/`testgraph_bindings.yml` outside examples/ | none (find exit 1) | Step-1 command |
| Kill catalog | **22** = 9 ports + 13 invariants (`grep -c '\[\[mutants\]\]'` → 22); file unchanged since 5f84937 | `specs/current/kill_mutants.toml` |

**Trees reconciled at HEAD** (checked fresh): `TlaSpecDevCli.tla`,
`spec_manifest.yaml`, `kill_mutants.toml`, `case_adapters.toml`,
`production_adapters.py` each diff-identical across `specs/current/`,
`specs/program_model/`, `specs/desired_program_model/`;
`specs/desired_program_model/adapter_case_runtime.py` (new in the desired
tree this workflow) diff-identical to the current-tree copy.

**Manifest delta since run 5** (read in full): the only changes to
`specs/current/spec_manifest.yaml` are the status-header rewrite
(workflow/ticket/slice bookkeeping) and the MR-DF-01 comment noting semantic
blocks are carried verbatim; ports/actions/budgets blocks byte-unchanged.

## 2. Sweep 1 — Program surface (fresh enumeration)

**Enumeration commands and raw counts (fresh at e2fdfa7):**

```bash
git ls-files '*.py'   | sort   # 3511 raw
git ls-files '*.kt'   | sort   #  588 raw
git ls-files '*.kts'  | sort   #  140 raw
git ls-files '*.java' | sort   #  336 raw
git ls-files '*.sh'   | sort   #    7 raw
git ls-files '*.j2'   | sort   #   12 raw   (NEW language glob this run — see §8.6)
# single filter: grep -v '^specs/\.history/'  (immutable sealed history;
# checked against the scope: no plan line names a code path under it)
# filtered union -> N = 572  (py 401, kt 84, kts 20, java 48, sh 7, j2 12)
```

Raw lists: `sweep-raw-close2/cac2-raw-*.txt`; union
`cac2-surface-all.txt`; changed-file listing vs run 5 (for read
prioritization only, NOT verify-by-diff):
`cac2-changed-surface-name-status.txt` (239 changed/added surface files).

**Row set:** all 572 rows emitted by `cac2_classify.py` →
`sweep-raw-close2/sweep1_table.md` (one row per file; the rule set is the
script's recorded content, summarized: 25 named lifecycle/adapter rows in-scope;
wrapper/plumbing per `PS:554-557`; generate/export per `PS:542/PS:598`;
`examples/effect_providers/**` per `CP:80`; test_graph per `CP:49`;
tests per `CP:49`; validation scripts/evidence per `CP:49`/`PS:521-522`;
`examples/distributed_history/**` per `PS:524-525` totality with the
behavioral boundary noted (`CP:69`, `CP:75`, `CP:271-272`); archived ticket
trees and audit tooling per `PS:524-525`/`CP:49`; templates per
`CP:80`/`PS:598`; fallback = `PS:524-525` totality).

`enumerated N = 572, table rows M = 572, N == M` (script prints
`rows=572 in=25 out=547`). Dispositions: **in-scope 25 / out-of-scope 547 /
ESCALATION rows 0**. Verdict totals: represented 13, partial 10,
unrepresented 549 (of which in-scope unrepresented = 2:
`scripts/fitness_functions.py` per `PS:530-533`, `scripts/testgraph_channels.py`
per `PS:521-522` — both placed out-of-model by quoted rulings → inventory).

The 25 in-scope rows (full row text in `sweep1_table.md`):

| Module | Verdict | Placed by | Note (this run) |
|---|---|---|---|
| scripts/tla_spec_dev.py | represented | CP:64, PS:524-525 | READ diff: runner spawn gains `--fuzz-runs/--seed/--fuzz-iteration` (defaults 1/0; flags out-of-model PS:547-551; spawn still matches runner_process :140-142); CD-04 help rewording; provider epilog text. Zero new effect primitives |
| scripts/onboard_program_model.py | represented | PS:524-525 | READ diff: e7fcd09 scaffold-template content (the `subprocess.run` at :1298 is INSIDE the emitted f-string template — scaffold content under spec_tree, not a spawn ScaffoldProject performs) |
| scripts/new_ticket_workflow.py | represented | PS:524-525, CP:420 | READ diff: CD-07 VAL-04 wording + MR-DF-01/e7fcd09 semantic-tail carry; same spec_tree writes |
| scripts/budgets.py | partial | PS:524-525, CP:422 | uncovered load/refusal → PS:544-551/PS:599 |
| scripts/analyze_complexity.py | represented | CP:66, CP:200, CP:339, CP:423 | READ diff scan: CD-05/06/07 all inside advisory internals (PS:530-533); verdict envelope `complexity_gate' ∈ {pass,fail}` unchanged; zero new primitives |
| scripts/fitness_functions.py | unrepresented | CP:67; PS:530-533 | inventory; READ diff: CD-07 CONFIG ERROR added then 497ab99 removed it (CP:80 amendment) |
| scripts/complexity_ledger.py | partial | PS:524-525 | unchanged since 5f84937; ESC-1 PS:551-554 |
| scripts/extract_spec_manifest.py | partial | PS:524-525 | READ diff: 37c6c65/497ab99 parser extensions (floats, single-line inline mappings); pure parsing |
| scripts/spec_evolution.py | represented | PS:524-525 | unchanged; deletes/spawn declared (:151-153, :159-161) |
| scripts/skill_feedback.py | partial | PS:524-525 | unchanged; ESC-7 PS:559-560 |
| scripts/spec_paths.py | partial | PS:524-525 | unchanged |
| scripts/testgraph_channels.py | unrepresented | PS:521-522 | inventory (test-graph enforcement surface) |
| scripts/run_generated_case_adapters.py | represented | PS:524-525, CP:80 | READ diff (+1245 lines): provider machinery = child-side surface behind declared runner_process; only new primitives: work-dir mkdir :1381 (under existing work tree), PYTHONPATH read :1138 (replay text) |
| scripts/corpus_diagnostics.py | represented | CP:65, CP:129, PS:538-542 | READ diff: CD-04 REDESIGN QUESTION output; print-only + exit codes unchanged; `enforce_case_cap`:826 retains "Fix the diagram" on the generate/export path — matches the model's own strings :420/:588 |
| scripts/effect_conformance_report.py | represented | PS:538-542, PS:557-558 | unchanged; R4-2 closure carried |
| scripts/effect_conformance.py | represented | PS:557-558, PS:538-542 | unchanged; :692 hit is the sandbox PATCHING rmtree for observation |
| scripts/kill_test.py | represented | PS:538-542 | unchanged; mutation_write/corpus_process declared; MF-027 child standing |
| scripts/run_kill_test.py | represented | PS:538-542 | unchanged |
| spec_double_compiler/__init__.py | partial | PS:524-525, CP:80 | unchanged |
| spec_double_compiler/runtime.py | partial | PS:524-525, CP:80 | READ diff: EP-01 provider context/protocol — pure datatypes, no I/O |
| spec_double_compiler/effects.py | partial | CP:80 | NEW; READ in full (25 lines): sha256 seed derivation, no I/O/clock/OS-randomness |
| specs/current/adapter_case_runtime.py | partial | CP:77 | reconciled copy |
| specs/current/production_adapters.py | represented | CP:77 | READ diff: CD-04 adapter assertion tracks the reworded output |
| specs/program_model/adapter_case_runtime.py | partial | CP:77 | diff-identical to current |
| specs/program_model/production_adapters.py | represented | CP:77 | diff-identical to current |

## 3. Sweep 2 — Effects, by category (fresh, full surface, JVM-extended patterns)

Commands: word-boundary `grep -nE` per category over every file in
`cac2-surface-all.txt`, JVM equivalents folded in (patterns recorded in the
shell history note inside `cac2_classify.py` header and reproducible from the
raw files). Raw outputs: `sweep-raw-close2/<category>.txt`. Area partition
(the grouping rule: partition raw hits by the path-prefix area function in
`cac2_classify.py`, which a reader can re-apply mechanically; every raw hit
lands in exactly one area group):

| Category | Raw N | lifecycle | adapters | prod-runtime | testgraph | repo-tests | spec-tests | effect-providers | examples-other | validation-evidence | templates | audit-tooling | other-scripts | skill-scripts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Filesystem | 3774 | 559 | 498 | 7 | 884 | 921 | 340 | 325 | 51 | 18 | 0 | 31 | 138 | 2 |
| Subprocess | 1437 | 202 | 177 | 7 | 574 | 190 | 88 | 115 | 27 | 4 | 0 | 30 | 20 | 3 |
| Network | 147 | 14 | 0 | 0 | 16 | 8 | 8 | 77 | 19 | 0 | 0 | 2 | 0 | 3 |
| Environment | 397 | 25 | 12 | 0 | 258 | 15 | 7 | 50 | 20 | 5 | 0 | 5 | 0 | 0 |
| Clock | 463 | 20 | 9 | 0 | 281 | 13 | 4 | 114 | 14 | 0 | 0 | 7 | 1 | 0 |
| Randomness | 62 | 2 | 0 | 1 | 8 | 11 | 0 | 22 | 0 | 16 | 0 | 2 | 0 | 0 |
| Persistent store | 111 | 9 | 0 | 0 | 43 | 1 | 0 | 20 | 32 | 0 | 0 | 3 | 3 | 0 |

**Out-of-scope area groups (inventory; do not gate).** Each group verdict is
placed by the quoted line already governing its Sweep-1 rows: testgraph
(`CP:49`), repo-tests/spec-tests (`CP:49`), effect-providers (`CP:80` — the
77 network hits are the `legacy_payment_http` HTTP fixture, exactly the
experimental surface the amendment records with 12 unwaived gaps),
examples-other incl. distributed_history (`PS:524-525`/`CP:69` behavioral
boundary), validation-evidence (`CP:49`), templates (`CP:80`/`PS:598` — no
`scripts/` consumer of `*.j2` exists, checked mechanically, so no modeled
action can reach them), audit-tooling (`CP:49`/run-5 row-359 precedent),
other-scripts = wrappers/generate (`PS:554-557`/`PS:598`), skill-scripts
(`PS:524-525` totality; also the install script is a kill-test
mutation_write target, declared :176-178). Standing rule carried: non-Python
runtimes (kt/kts/java, sh) are **unobservable by the effect sandbox —
`unobservable` is not `clean`** — inventory, as in runs 1-5.

**In-scope areas (lifecycle + adapters + prod-runtime), per category:**

- **Filesystem (559 lifecycle raw)** — groups (rule: match the I/O verb in
  the hit line; counts re-derivable from `filesystem.txt`): write-class 48
  (writes under spec tree / results / scaffold emissions → declared
  `spec_tree`/`evidence_report`/`mutation_write` per the action rows
  :190-237); read-class 31 (manifest/model reads — no port type exists for
  reads in the schema :101-105; out-of-model as non-observable-port surface,
  standing since run 2); delete-class 4 → **per-site below**; temp 2 (runner
  mkdtemp work dir — child-side behind runner_process); remainder 474 =
  handle/prose false-positive class (bare `Path`/`open` word matches with no
  I/O verb; collapsing rule stated, re-derivable). Adapters 498 + prod-runtime
  7: harness shim writes inside the conformance work tree, declared via
  RunSpecUnitTests/RunEffectConformance rows (:236/:228). **Verdict:
  declared** (no undeclared write class).
- **Subprocess (202 lifecycle raw)** — real spawn primitives extracted
  mechanically (`subprocess.(run|Popen|check_*)|os.system|execv`): exactly 6
  sites. `kill_test.py:609` → `corpus_process` :187-189 (declared; child
  effects out-of-model per MF-027 standing). `spec_evolution.py:99` →
  `git_metadata` :159-161. `tla_spec_dev.py:372` → the single dispatch spawn,
  command lines built at :296-303 (pytest → `test_process` :129-131) and
  :313-358 (runner → `runner_process` :140-142; the new fuzz flags do not
  break the target glob). `run_generated_case_adapters.py:2050/:2104` →
  child-side re-exec behind the declared runner spawn (`PS:531` names the env
  re-exec out-of-model). `onboard_program_model.py:1298` → NOT a spawn: text
  inside the emitted scaffold template (READ). Remaining raw hits are `\brun\b`
  word matches in prose/identifiers (collapsing rule; re-derivable).
  **Verdict: declared; zero undeclared spawns.**
- **Network (14 lifecycle raw)** — all in `effect_conformance.py`: the
  sandbox's socket.connect PATCH (observer, :775-788) plus docstrings; the
  observer performs no outbound connect. **Zero real network calls in the
  modeled lifecycle** (fresh full-surface check, not a narrowed one).
- **Environment (25 lifecycle raw)** — dispatcher env copy
  (`tla_spec_dev.py:274`) feeding declared child spawns; runner re-exec reads
  (:2022/:2048/:2090) child-side per `PS:531`; rest are PATH-word prose.
  Out-of-model transcription per `PS:530-533`. |
- **Clock (20 lifecycle raw)** — real clock reads only on the close path
  (`complexity_ledger.py:775`, `spec_evolution.py:770/:883`,
  `skill_feedback.py:86`) → ESC-7 ruling `PS:559-560`; rest prose.
- **Randomness (2 lifecycle + 1 prod-runtime raw)** — all
  prose/docstring; `spec_double_compiler/effects.py` is deterministic sha256.
  **Zero OS-randomness sites in scope.**
- **Persistent store (9 lifecycle raw)** — all false positives
  (`execute`/`cursor`/`commit` as words in prose and git-command strings;
  collapsing rule stated). **Zero database/store clients in the repository's
  in-scope surface.**

**Destructive sites — always per-site** (`destructive_sites.txt`, 56 raw
sites full-surface, pattern incl. `rm -rf`/`mktemp`/`deleteRecursively`):
in-scope code sites are exactly `spec_evolution.py:154/:385/:477` (declared
`spec_tree_delete` :151-153, action row :237 — carried from run-5
verification; file unchanged) and `effect_conformance.py:692` (observer patch
of rmtree; performs no delete). Out-of-scope sites: `run_tlc.sh:31-32`
(NEW this batch, CD-07 VAL-03: mktemp scratch dir + `trap rm -rf` of its own
temp dir — plumbing per `PS:554-557`, performed by no modeled action, targets
only its mktemp dir); `close_spec_workflow.py:49`, `close_tickets.py:127/:232`
(wrappers, `PS:554-557`); `generate_cases_from_tlc_dump.py:97` (generate,
`PS:598`); 25 testgraph + 8 repo-tests + 3 spec-tests + 7 effect-providers +
3 examples + 1 validation-evidence + 3 mktemp-in-tests sites — each visible
per-site in the raw file, each governed by its area's quoted line.

## 4. Sweep 3 — Behaviors (fresh, full surface)

Same mechanics (anchored patterns, raw files `behaviors_*.txt`, area
partition by the recorded rule):

| Class | Raw N | lifecycle | in-scope real sites after collapse | Disposition |
|---|---|---|---|---|
| Error paths | 1451 | 379 | grouped by failure semantics (parse refusals, gate refusals, subprocess failure propagation, fail-open guards) | refusal/gate verdicts the model names are represented (result reasons, gate variables); branches beyond them → `PS:544-551`/`PS:599` recorded granularity limitation; fail-open git branch → `PS:557-560` |
| Retries | 565 | 2 | 0 (both prose: kill_test.py:131/:282 tripwire docs) | none in scope; 402 effect-providers + 148 testgraph hits are fixture/JVM surface (`CP:80`/`CP:49`) |
| Timeouts | 287 | 5 | 2 real (run_kill_test `--timeout` 600 default :104/:198; kill_test :592/:614) | experimental surface modeled at verdict level per `PS:538-542`; per-flag timeout value out-of-model `PS:547-551` |
| Fallbacks | 241 | 86 | argparse `default=` class + guarded imports | silent-degrade guards out-of-model as transcription `PS:530-533`; the VAL-01 CONFIG ERROR fallback was REMOVED by 497ab99 (parser now evaluates identically without PyYAML — stronger than the guard; `CP:80`) |
| Concurrency | 27 | 1 | 0 (onboard docstring) | no concurrency primitives in the modeled lifecycle (carried finding, re-verified fresh) |
| Config-driven | 866 | 265 | flag/env-driven branches (--view, --batch, --fuzz-*, TLA_SPEC_DEV_ROOT etc.) | per-flag variants out-of-model `PS:544-551`/`PS:599`; TLA_SPEC_DEV_ROOT (CD-08) lives in example scripts (out per `PS:524-525`) |

The rediscovered class — "a guard that silently passes when its input is
absent" — was checked against the fresh surface: the manifest-missing warning
path (CD-07 item 4) now names what happened instead of a sentinel path (READ
diff), and remains advisory-internals surface per `PS:530-533`. No new
silent-pass guard entered the modeled lifecycle this batch.

## 5. Sweep 4 — Both views, separately

Enumeration: `ls specs/current/*.tla` → **1 module**; `specs/program_model`,
`specs/desired_program_model` → 1 each (same module, diff-identical).

- **Internal view: unrepresented by construction.**
- **External view: unrepresented by construction.**

Both remain out-of-scope inventory **only** by the quoted known_gap `PS:597`
(view split FUTURE WORK; MF-023 Q=0.012 basis). The finding stays on the
record at full strength; it is not a gap this audit may count, and it is
NOT restated in the successor plan's own text (ESC-C2-1). The four example
fixtures each carry their own Core/Internal/External views — fixture surface
per `CP:80`/`CP:69`, and the effect-provider fixtures' own audit returned
**FAIL, 12 in-scope gaps** (`specs/results/coverage_audit_report.md`,
`coverage_audit_ledger_input.yaml: in_scope_gaps: 12`) — recorded, unwaived,
promotion-blocked exactly as `CP:80` states.

## 6. Dispositions and the modeled-surface spot-verification

### 6.1 In-scope gaps this run

**None.** Fresh sweeps found zero undeclared effect sites and zero
unrepresented behavior on the modeled surface that is not placed by a quoted
recorded ruling. The run-5 closures (R4-1/2/3) are carried in byte-identical
files (`kill_test.py`, `effect_conformance*.py`, manifest port/action blocks
— all unchanged since 5f84937, verified by git diff).

### 6.2 Modeled-surface spot-verification (dispatch-required; all fresh reads)

The batch + merge claimed **zero model delta** eleven times. Verified:

1. **Mechanical:** `specs/current/TlaSpecDevCli.tla`, `MC.cfg`,
   `kill_mutants.toml`, `case_adapters.toml` byte-identical
   5f84937→HEAD (git diff empty). `spec_manifest.yaml` differs only in the
   status header + a carry-comment (read in full). TLC identity therefore
   holds by construction; recorded evidence agrees (ledger input: 6,209,780
   generated / 283,805 distinct / depth 25, = `cd11-post-promotion-tlc.txt`).
2. **Corpus gate (CD-04):** output wording change only — verdict logic,
   exit codes, print-only behavior unchanged (READ diff);
   `AnalyzeCorpus` models the verdict (`corpus_gate' ∈ {"pass","fail"}`,
   TLA :415-426) and its manifest row is deliberately empty (:216), so no
   modeled observable changed. The adapter assertion was updated WITH the
   model trees (production_adapters.py, all three copies) — the observable
   the oracle checks moved in lockstep, and spec-unit conformance passes
   fresh (below). The retained "Fix the diagram…" refusal text
   (`corpus_diagnostics.py:826`, generate/export path) still matches the
   model's own result strings (TLA :420/:588) — no desync in either
   direction.
3. **Analyzer accuracy (CD-05/CD-06) + polish (CD-07):** all changes live
   inside the advisory scan; the modeled surface is the nondeterministic
   verdict envelope `complexity_gate' ∈ {"pass","fail"}` (TLA :379-393),
   which accuracy fixes cannot leave. Zero new effect primitives in the
   diffs (mechanical grep, §2). `run_tlc.sh`'s new scratch-dir behavior is
   plumbing (`PS:554-557`) and touches only its own mktemp dir.
4. **Provider runtime merge + e7fcd09/497ab99:** the runner's +1245 lines
   and `spec_double_compiler/*` sit behind the declared `runner_process`
   spawn; the dispatcher's new fuzz flags default to 1/0 (single
   deterministic iteration = prior behavior) and the spawned command still
   matches the declared target glob; flags are out-of-model per `PS:547-551`.
   The removed VAL-01 CONFIG ERROR path is advisory-internals surface
   (`PS:530-533`) recorded as a finalization amendment (`CP:80`).
5. **Live oracles, this run:** repository unit suite **688 passed** fresh at
   HEAD; spec-unit adapter conformance **67 passed, "spec-unit validation
   passed for 1 target(s)"** fresh at HEAD — the model and program agree on
   every bound case of the reconciled tree.

**Conclusion: nothing in the modeled CLI lifecycle's observable behavior
changed without a corresponding model-tree change; the zero-model-delta
claims are verified on the modeled surface.**

### 6.3 Out-of-scope inventory — does not gate

547 rows recorded (`sweep1_table.md`), plus the per-category area groups
(§3-4). Standing observations carried at full strength: both views missing
(`PS:597`); `generate` + templates unmodeled (`PS:598`; no repo consumer of
`*.j2` found); wrapper/plumbing deletes performed by no modeled action
(`PS:554-557`, now including `run_tlc.sh`'s temp-dir cleanup); JVM/bash
runtimes unobservable-not-clean; `corpus_process`/`runner_process` declare
the spawn, never the child (MF-027) — provider machinery and user corpus
commands are child-side by construction; `examples/effect_providers/*` carry
**12 recorded unwaived gaps** in their own audit and are promotion-blocked
(`CP:80`).

### 6.4 Dispositions summary

Every `partial`/`unrepresented`/`undeclared` row above is dispositioned
**Inventory it** with its quoted plan line (the only rows lacking a named
action are placed by `PS:521-533/538-562` rulings or `CP:49/80`); there are
**zero Model-it / Change-the-program rows** this run. No forbidden
disposition was used; no per-finding waiver exists anywhere in this report.

### 6.5 Scope escalations — surfaced, not resolved

**ESC-C2-1 (advisory; owner action requested).** The successor plan's own
text does not carry the predecessor's recorded rulings: `CP:49` is the
pre-amendment one-sentence rule, and `CP:79-82` known_gaps omit the view-split
(`PS:597`), `generate` (`PS:598`), and refusal/flag-granularity (`PS:599`)
limitations plus the `PS:522-562` amendment text. Every out-of-model
classification that cites a PS line in this report is therefore quotable only
from the sealed snapshot, incorporated via `CP:7-8` and the dispatching
instruction's recorded-rulings direction. This audit proceeded on that basis
(dispatch: the rulings are settled and not to be re-litigated) rather than
HALTing, and flags it: **fold `PS:597-599` and the operative
`semantic_model_rule` amendment text into the successor plan (or its next
revision) so the promotion-gate scope is self-contained.** One sentence of
owner text closes it. No row's disposition changes under any answer that
keeps the recorded rulings in force; if the owner instead repudiated the
predecessor rulings, this report's verdict would need re-derivation — which
is exactly why the escalation is surfaced rather than silently absorbed.

No other escalation: the amended `CP:80` covers the entire merged surface
this run swept (runner machinery, `spec_double_compiler/*`, templates,
fixtures, owner-direct commits) — no post-merge surface was found that the
amendment fails to name or that a quoted line fails to place.

## 7. Verdict

- In-scope gaps: **0**.
- Escalations: **1 surfaced (ESC-C2-1, advisory scope-text hygiene), 0
  resolved by this audit**.
- Out-of-scope inventory: non-empty (547 rows + area groups), recorded.

**Verdict: `PASS`.** Zero in-scope gaps against the amended scope
(`CP` schedule_revision 2 + the incorporated recorded rulings). On the record
alongside the pass: both views remain unrepresented by construction
(`PS:597`); `generate` and the codegen templates remain unmodeled
(`PS:598`/`CP:80`); granularity and out-of-model rulings inventory real
behavior the model does not represent; the effect-provider fixtures carry 12
recorded unwaived gaps and are promotion-blocked (`CP:80`) — all
owner-declared boundaries, reviewable in one place, none waived per-finding.

## 8. Attestation

1. **Enumerations.** Sweep 1: six `git ls-files` globs (raw
   3511/588/140/336/7/12), one stated filter (`specs/.history/**`), union
   N = 572; table M = 572 (machine-emitted, `cac2_classify.py` prints
   `rows=572`); `N == M`. Sweep 2: seven full-surface category greps (raw
   3774/1437/147/397/463/62/111), each raw file archived; area partitions
   machine-derived; collapse rules stated per category (§3) and re-derivable
   from the raws. Destructive: dedicated full-surface grep, 56 raw = 56
   listed; `N == M`. Sweep 3: six class greps (1451/565/287/241/27/866),
   same mechanics. Sweep 4: `ls` of the three model dirs (1 module each).
2. **Surface NOT walked:** `specs/.history/**` code (stated filter), except
   the quoted snapshot plan and named evidence files, which were read;
   the contents of the 547 out-of-scope rows except where a category hit was
   examined (all lifecycle-area hits, the destructive site list, and the
   network per-site check were examined; out-of-scope area hits were
   dispositioned by group, per-site only for destructive); non-code files
   except the named model/manifest/catalog/plan/evidence files.
3. **READ vs INFERRED (per sweep).** Sweep 1 in-scope 25: **17 rows read
   this run** (full file: `spec_double_compiler/effects.py`,
   manifest ports/actions region, TLA action regions, `run_tlc.sh` diff;
   full diff or diff+region: tla_spec_dev, onboard_program_model,
   new_ticket_workflow, budgets, analyze_complexity, fitness_functions,
   extract_spec_manifest, corpus_diagnostics, run_generated_case_adapters,
   spec_double_compiler/runtime, production_adapters ×2, plus scaffold/
   generate/export diffs among the out rows); **8 rows carried** on the
   mechanical license that git shows the file byte-unchanged since 5f84937
   where runs 4-5 read them (complexity_ledger, spec_evolution,
   skill_feedback, spec_paths, testgraph_channels, effect_conformance,
   effect_conformance_report, kill_test/run_kill_test,
   adapter_case_runtime ×2 — diff-verified copies). Sweep 1 out-of-scope 547:
   dispositioned from path by the recorded rules, **not read** (stated
   per-row in the table). Sweeps 2-3: every lifecycle-area hit examined
   (real-primitive extraction quoted in §3); out-of-scope hits dispositioned
   by area group. The inferred rows are the least reliable; they are exactly
   the rows the quoted boundary lines govern wholesale.
4. **Scope by reasoning?** Two carried interpretive steps, both surfaced:
   (a) the `PS:524-525` totality reading (attested runs 3-5, corroborated by
   the owner's ESC-3 ruling); (b) the incorporation of the sealed-snapshot
   rulings into the successor plan's scope — **ESC-C2-1**, licensed by the
   dispatching instruction and `CP:7-8`, surfaced for owner text rather than
   resolved here. No other row's scope was decided by reasoning.
5. **Reproducibility:** yes — `sweep-raw-close2/` holds the six raw
   enumeration lists, the union, the changed-file listing, all 13 category
   raws, the destructive list, and `cac2_classify.py` whose output IS the
   table; re-running the recorded commands at e2fdfa7 re-derives every row
   and every count in this report.
6. **Findings about this prompt.** (a) STILL OPEN: the Step-1 single-space
   regex (36 vs 41 — silently drops parameterized actions); Step-4's
   hardcoded `scripts/ spec_double_compiler/` row-set commands (run fresh
   over the full surface here); no re-audit procedure after boundary
   amendments; no verify-by-diff protocol (moot this run — dispatch ordered
   fresh enumeration, which is the safe default the prompt should name).
   (b) NEW: the prompt's language-glob list let five prior runs skip `*.j2`
   entirely — 12 codegen templates were never enumerated until the owner
   amendment happened to name one (`CP:80`); the prompt should require an
   extension-inventory pass (`git ls-files | sed 's/.*\.//' | sort -u`)
   before fixing the glob set. (c) NEW: the prompt assumes the scope lives in
   ONE plan file; a successor workflow whose plan supersedes a rulings-bearing
   predecessor plan has no prompt-sanctioned way to quote the still-operative
   rulings — this run had to surface ESC-C2-1 and lean on the dispatch. Codify
   the rule: recorded rulings survive only if restated or explicitly
   incorporated by the successor plan, else they are escalations.
   (d) The self-reported `N == M` limitation stands; the machine-emitted
   table narrows it (a reviewer recounts from the archived raws) but the
   LIFECYCLE verdict texts inside `cac2_classify.py` are still my claims —
   the per-file citations in §2/§6.2 are the checkable part.
