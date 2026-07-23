# Coverage Audit Report — run 5 (re-verdict at workflow close, post-CD-11 + third owner amendment)

- **Epic / workflow:** `complexity-descriptor-epic` (workflow close; CD-01, CD-02, CD-03, CD-09, CD-10, CD-11 all done and merged)
- **Scope source:** `specs/desired_program_model/ticket_plan.yaml` (schedule_revision 4, `:20`): `semantic_model_rule` lines `520-562` (unchanged since run 4); `service_catalog` + `known_gaps` lines `576-599` (`:585` AMENDED — ESC-R4-1 wording fix); ticket `implementation_scope` lines `2046-2049` (CD-01), `2123-2125` (CD-02), `2193-2197` (CD-03), `2287-2291` (CD-09), `2365-2368` (CD-10), **`2448-2452` (CD-11, NEW)**
- **Model audited:** `specs/current/TlaSpecDevCli.tla` @ `5f84937`
- **Date:** `2026-07-22`
- **Verdict:** `PASS` — 0 in-scope gaps; R4-1/R4-2/R4-3 verified FIXED in the tree, ESC-R4-1/2/3 dispositioned by owner amendment + CD-11 and verified

> This audit checks **completeness of what is modeled**, not fidelity
> (`prompts/coverage_audit.md`). Run 4 (FAIL, 3 gaps, 3 escalations):
> `specs/results/epic-close/coverage_audit_report_run4.md`. This run is a
> **verify-by-diff re-verdict**, licensed by a fresh enumeration diff against
> run 4's recorded surface (§2): the surface changed by exactly one added file
> and five content-modified files, all accounted for below. Every run-4
> gap/escalation site was re-read fresh at 5f84937; Sweep 2/3 were re-derived
> mechanically over the changed surface with fixed patterns (§3). Raw outputs:
> `specs/results/epic-close/sweep-raw-run5/`.

## 0. Declared scope (delta against run 4's verbatim quote)

Run 4 quoted `ticket_plan.yaml:520-562`, `:576-599`, and the five ticket
implementation_scope blocks verbatim (its §0). Fresh reads this run:

- `:520-562` (`semantic_model_rule`) — **byte-identical to run 4's quote**
  (re-read in full this run). All recorded owner rulings carried unchanged:
  the ESC-6 correction `:538-542`, granularity rulings `:544-551`, ESC-1
  `:551-554`, ESC-3 `:554-557`, ESC-5 `:557-558`, ESC-7 `:559-560`.
- `:576-599` (`service_catalog` + `known_gaps`) — identical to run 4's quote
  **except `:585`**, which now reads (quoted verbatim, fresh):

```yaml
# specs/desired_program_model/ticket_plan.yaml:585 (existing_boundaries, AMENDED — resolves ESC-R4-1)
    - "EXPERIMENTAL surface (the 2026-07-21 pivot): corpus gate, effect conformance, kill test — SHIPPED and MODELED as-is per the ESC-6 correction in semantic_model_rule; only scripts/generate_cases_from_tlc_dump.py (generate) is unmodeled, a recorded limitation (ESC-R4-1 wording fix, 2026-07-22)"
```

  The stale "deliberately unmodeled" wording is gone; the catalog and
  `:538-542` no longer contradict. **ESC-R4-1 resolved by the owner, verified.**
- CD-11's implementation_scope, quoted verbatim (NEW scope surface this run):

```yaml
# specs/desired_program_model/ticket_plan.yaml:2448-2452
    implementation_scope:
      - specs/current/spec_manifest.yaml (R4-1/2/3 port rows; ESC-R4-2 stanzas)
      - specs/current/TlaSpecDevCli.tla (@port annotation vocabulary only — no semantic delta)
      - specs/current/kill_mutants.toml (catalog for changed ports)
      - tests/test_kill_test.py (boundary counts if they change)
```

Closure rule: unchanged from runs 3-4 (file-only scoping; `:524-525` totality
reading for the lifecycle closure, attested §8.4). No new scope inference was
required: the one new surface row and five changed files all classify under
already-quoted lines (§2, §3).

## 1. Model representation index (re-derived fresh)

Corrected regex `grep -cE '^[A-Za-z_][A-Za-z0-9_]*(\(.*\))?[[:space:]]+==' specs/current/*.tla`
→ **N = 41** (prompt's single-space variant still yields 36 — prompt defect
STILL open, §8.6). Non-comment content of `TlaSpecDevCli.tla` verified
**byte-identical** to 400c51a (mechanical check: comment-stripped diff empty),
so the action/invariant index is line-for-line run 4's: 15 actions (14
@command + Stutter), 13 invariants. **CD-11's zero-semantic-delta claim is
verified mechanically, and TLC confirms it:** `cd11-post-promotion-tlc.txt` vs
`cd10-post-promotion-tlc.txt` — 6,209,780 states generated, 283,805 distinct,
depth 25, identical in both.

| Kind | Fresh state | Evidence |
|---|---|---|
| Ports (**9**, was 7) | `spec_tree` :167-169, `evidence_report` :170-172, `cli_artifact` :173-175, `test_process` :186-188, `runner_process` :197-199, `spec_tree_delete` :208-210, `git_metadata` :216-218, **`mutation_write` :233-235 (NEW, CD-11)**, **`corpus_process` :244-246 (NEW, CD-11)** | `specs/current/spec_manifest.yaml` |
| Action→port map | **14 of 14** @command actions mapped (`spec_manifest.yaml:247-294`); two deliberately EMPTY rows with rationale: `RecordBudgets: []` :259, **`AnalyzeCorpus: []` :273 (NEW, CD-11 R4-3)** | fresh read |
| Bindings | `case_adapters.toml` **unchanged since run 4** (git diff clean); 14 adapters = the @command action set | `grep -c 'adapter = '` → 14 |
| `actions.yml` / `testgraph_bindings.yml` outside examples/ | none (find exit 1) | Step-1 command |
| Kill catalog | **22 = 9 ports + 13 invariants**, one per boundary (`grep -c '\[\[mutants\]\]'` → 22; IDs listed: 9 `port-*` incl. `port-mutation_write` :125, `port-corpus_process` :139) | `specs/current/kill_mutants.toml` |

**Run-4 index desyncs — all closed:**

1. ESC-R4-2 (empty `state_fields`/`actions`/`ports` stanzas) — **recorded, not
   populated** (CD-11 choice; judged in §6.3).
2. ESC-R4-3 (@port vocabulary) — **fixed**; mechanical check this run:
   annotation vocabulary `grep -oE '@port TlaSpecDevCliPort\.[a-z_]+'` yields
   exactly {cli_artifact, corpus_process, evidence_report, git_metadata,
   mutation_write, runner_process, spec_tree, spec_tree_delete, test_process};
   declared port set is the same 9 names — **exact intersection, 9 = 9**.
   Per-action mirror verified for all 14 rows against `spec_manifest.yaml:247-294`
   (e.g. RunKillTest :505-507 = [evidence_report, mutation_write,
   corpus_process] = manifest :292; CloseTicket :600-602 = manifest :294); the
   two empty rows carry explicit "No @port" notes naming their rulings
   (`TlaSpecDevCli.tla:278-279` RecordBudgets, `:413` AnalyzeCorpus).
3. ESC-R4-1 (`:585` stale wording) — **fixed by the owner** (§0).

**Trees reconciled at 5f84937** (re-checked this run): `TlaSpecDevCli.tla`,
`spec_manifest.yaml`, `kill_mutants.toml`, `case_adapters.toml`,
`production_adapters.py` each diff-identical across `specs/current/`,
`specs/program_model/`, `specs/desired_program_model/`.

## 2. Sweep 1 — Program surface (fresh enumeration + diff against run 4)

**Enumeration commands and raw counts (fresh at 5f84937):**

```bash
git ls-files '*.py'   | sort   # 2378 raw
git ls-files '*.kt'   | sort   #  567 raw
git ls-files '*.kts'  | sort   #  135 raw
git ls-files '*.java' | sort   #  324 raw
git ls-files '*.sh'   | sort   #    5 raw
# single filter (same as runs 3-4): grep -v '^specs/\.history/'
# filtered union -> N = 359
```

Raw lists and filtered union: `sweep-raw-run5/ca5-raw-*.txt`,
`ca5-surface-all.txt`. The py raw count grew 2284→2378 from CD-11's sealed
history entry (filtered) plus one real surface file.

**Surface diff vs run 4** (`diff ca4-surface-all.txt ca5-surface-all.txt`,
archived at `sweep-raw-run5/ca5-surface-diff-vs-run4.txt`):

```
168a169
> specs/results/epic-close/sweep-raw-run4/ca4_classify.py
```

**Exactly one added row; zero removed.** Content changes on the shared 358
rows (`git diff --name-status 400c51a..HEAD` filtered to surface globs,
archived at `ca5-changed-surface-name-status.txt`): 5 files —
`scripts/new_ticket_workflow.py`, `tests/test_kill_test.py`, and the three
tree copies of `tests/test_tla_spec_dev_kill_test_adapter.py`. **The claim
"surface unchanged except CD-11's manifest/annotation/test edits" HOLDS**
(the one addition is run 4's own archived classifier, not program surface),
so verify-by-diff is licensed on the stated terms.

**Row set:** run 4's machine-emitted 358-row table
(`sweep-raw-run4/sweep1_table.md`) carries over row-identical — every
classification input (path, plan lines, closure rule) is unchanged for those
rows — plus one new row dispositioned fresh:

| # | Module | In/Out | Plan line | Spec action(s) | Verdict | Evidence |
|---|---|---|---|---|---|---|
| 359 | `specs/results/epic-close/sweep-raw-run4/ca4_classify.py` | out | :521-522 (validation scripts) + :524-525 (totality: outside the shipped CLI lifecycle closure) | - | unrepresented | READ this run: run-4 coverage-audit tooling; emits `sweep1_table.md`/`destructive_sites.txt` into the run-4 raw dir (`:137`, `:187`); imported/reached by nothing in the lifecycle closure |

`enumerated N = 359, table rows M = 358 (carried, row-identical by surface
diff) + 1 (fresh) = 359, N == M`. Dispositions: **in-scope 24 / out-of-scope
335 / ESCALATION 0**. Verdict totals: represented 8, partial 14,
unrepresented 337.

**In-scope verdict deltas vs run 4** (from the fix verifications in §6.1):
the three `partial`/gap-carrying rows' named uncovered behaviors are now
declared — no in-scope row retains a named unrepresented effect.

## 3. Sweep 2 — Effects (verify-by-diff, mechanically complete)

For a fixed pattern, grep hits depend only on file content; the surface
partitions into 353 content-identical files (hits carry over from run 4's
archived raws exactly), 5 modified files, and 1 added file. Both halves of the
delta were enumerated fresh
(`sweep-raw-run5/ca5_changed_enum.sh`, `ca5_delta_check.sh`; raw hits per
category in `sweep-raw-run5/changed_<category>.txt`), with the run-5 patterns
(prompt Step-3 table, word-boundary anchored, JVM-extended) applied to **both**
the 400c51a and 5f84937 content of the 5 modified files so pattern variance
cannot masquerade as content delta:

| Category | old5 | new5 | Δ modified | added file | Δ disposition |
|---|---|---|---|---|---|
| Filesystem | 159 | 159 | 0 | 20 | added-file only (below) |
| Subprocess | 23 | 26 | **+3** | 17 | 2 = CD-11 scaffolder comment lines (`new_ticket_workflow.py:634,:690`, word "run" in "audit run 4"); 1 = CD-11 comment `tests/test_kill_test.py:720` ("spawn" in prose). Zero new spawn primitives |
| Network | 0 | 0 | 0 | 0 | — |
| Environment | 1 | 1 | 0 | 1 | added-file only |
| Clock | 4 | 5 | **+1** | 5 | `tests/test_kill_test.py:720` ("now" in the same CD-11 comment). Zero new clock calls |
| Randomness | 0 | 0 | 0 | 0 | — |
| Persistent store | 0 | 0 | 0 | 1 | added-file only (`execute` identifier) |

**Added file** (`ca4_classify.py`, out-of-scope row 359): its real primitives
are two `write_text` calls emitting run-4 audit artifacts under
`specs/results/epic-close/sweep-raw-run4/` (`:137`, `:187`) — inventory per
its Sweep-1 row; no spawn, no network, no delete.

**Destructive deletes/overwrites (always per-site):** the delete-primitive
extract over the changed surface is empty (no `rmtree|\.unlink\(|os\.remove\(`
delta; run 4's 23 sites stand unchanged in content-identical files, re-verified
for the three in-scope sites at `spec_evolution.py:154/:385/:477`). The two
run-4 overwrite sites are re-read fresh in §6.1 (R4-1) — now **`declared`**.

**Conclusion:** zero new effect sites in scope; every run-4 group verdict
stands except the three gap rows, which flip to `declared` per §6.1.

## 4. Sweep 3 — Behaviors (verify-by-diff, same mechanics)

Same fixed-pattern old/new comparison (`ca5_delta_check.sh`):

| Class | old5 | new5 | Δ modified | added file | Disposition |
|---|---|---|---|---|---|
| Error paths | 11 | 11 | 0 | 0 | no delta |
| Retries | 0 | 0 | 0 | 0 | no delta |
| Timeouts | 0 | 0 | 0 | 0 | no delta |
| Fallbacks | 7 | 7 | 0 | 7 | added-file `default=` argparse-class matches — out-of-scope row 359 |
| Concurrency | 3 | 3 | 0 | 0 | no delta |
| Config-driven | 16 | 16 | 0 | 1 | added-file only |

Zero behavior deltas on modified files; run 4's behavior tables and their
quoted-ruling dispositions (granularity `:544-551`+`:599`, out-of-model
`:530-533`, ESC-1/ESC-3/ESC-7 rulings) carry over row-identical. Not
re-litigated, per instruction.

## 5. Sweep 4 — Views, separately

Enumeration: `ls specs/current/*.tla` → 1 module; `specs/program_model/*.tla`
→ 1 (fresh). Unchanged from run 4: **Internal — unrepresented by construction;
External — unrepresented by construction.** Both remain out-of-scope inventory
by the quoted known_gap `:597` (view split FUTURE WORK, MF-023 Q=0.012 basis,
text unchanged this run). The finding stays on the record; it is not a gap
this audit may count.

## 6. Dispositions and fix verification

### 6.1 Run-4 in-scope gaps — all three verified FIXED in the tree (fresh reads)

| Gap | Fix verified at 5f84937 | Evidence (all READ this run) |
|---|---|---|
| **R4-1** RunKillTest mutation overwrites + corpus spawn | **FIXED — declared, not relocated.** `mutation_write` port (filesystem.write, target `*scripts/*`) `spec_manifest.yaml:233-235` with rationale `:219-232`; `corpus_process` port (process.spawn, target `*`) `:244-246` with rationale `:236-243`; RunKillTest row = `[evidence_report, mutation_write, corpus_process]` `:292`, comment `:286-291` recording test_process's removal from the row (it stays declared and exercised via RunSpecUnitTests `:293`; `port-test_process` mutant still refines RunSpecUnitTests, `kill_mutants.toml:65-75`). Code sites re-read live: seed `target.write_text(patched)` / finally-restore `target.write_text(original)` (`kill_test.py:548/:551` region), spawn `subprocess.run(list(command)…)` (`:609` region) from user `--corpus-command` (`run_kill_test.py:196-198`). Glob coverage checked against the catalog's actual `path` keys: 10 `scripts/*.py` + `skill-scripts/install-tla-spec-dev.sh` — all match `*scripts/*` (fnmatch `*` crosses separators). **The honest `*` spawn-target rationale is recorded** (`:239-243`: "any glob narrower than `*` would assert a constraint the code does not enforce — the documented pytest-shaped corpus command is one possible value, not a contract") — this is the honest form run 4's remediation asked for, not a widened dishonest match. Kill catalog seeds both: `port-mutation_write` (`:125-133`, restore-instead-of-seed — the kill test measures nothing while claiming it measured) and `port-corpus_process` (`:139-147`, spawn drops the final argument); both `find` patterns match the live code verbatim. |
| **R4-2** RunEffectConformance undeclared sandbox writes | **FIXED — `spec_tree` declared on the action.** Row = `[evidence_report, spec_tree]` `spec_manifest.yaml:285`; **choice rationale recorded** `:274-284` (symmetry with RunSpecUnitTests' identical physical writes; work tree is spec-scoped working state, not evidence; "the dishonesty lived in the manifest, so the manifest is what changed"). Write sites re-read live: `work_dir` defaults to `spec_dir/.effect-conformance-work` + `mkdir` (`effect_conformance_report.py:148-149`), per-case dirs (`:163` region), sandbox roots (`effect_conformance.py:619`, `:656`) — all under `**/specs/**`, now matched by the declared spec_tree for this action. |
| **R4-3** AnalyzeCorpus dead `evidence_report` port | **FIXED — removed with a G4-style deliberate-empty row.** `AnalyzeCorpus: []` `spec_manifest.yaml:273`, rationale `:265-272` citing the G4 class, the exact add_arguments/run() evidence, and the RecordBudgets empty-vs-absent rule. Re-verified fresh: primitive grep over `corpus_diagnostics.py` for `write_text|write_bytes|open(..w/a|--out` returns zero hits (exit 1) — the command still reads and prints only. The @port annotation carries the matching "No @port" note (`TlaSpecDevCli.tla:413`). |

Supporting evidence, re-checked: repo unit tests 578 passed
(`ticket-005-CD-11/results/repo_unit_tests.txt`), with the boundary-count
battery updated 20→22 and the `--list-boundaries` assertion `22/22`
(`tests/test_kill_test.py:715-721`, `:797-800` — the only test deltas);
spec-unit adapters passed for both targets (`spec_unit_tests.txt`); both
test graphs PASS (`cd11-post-promotion-graph-*.txt`); TLC identical (§1);
`max_distinct_states: 500000` carried (verified in
`specs/current/spec_manifest.yaml` budgets block).

### 6.2 In-scope gaps this run

**None.** The port-honesty boundary `:589` is now met on every audited path:
all in-scope effect sites map to declared ports for their actions, no declared
port is dead (both empty rows are deliberate with recorded rationale), the
kill catalog covers 22/22 declared boundaries, and the four-run manifest
desyncs are closed.

### 6.3 Judgment on CD-11's ESC-R4-2 disposition (record-not-populate) — asked for explicitly

**Judged SOUND on its recorded rationale.** The escalation's own remediation
menu offered exactly this option ("Declare the blocks as generated-content
placeholders (and say so in the manifest), populate them, or remove them").
CD-11 took it fully: the manifest comment (`spec_manifest.yaml:123-132`)
states the semantics — empty means "no generated case index yet"
(`case_codegen.generation_status: planned`), NOT "the model has no
state/actions/ports", naming where the authoritative declarations live — and
the identical comment now ships in **both** scaffolder templates
(`scripts/new_ticket_workflow.py:630-634`, `:686-690`), so every future
scaffold documents itself. The empty-vs-inapplicable distinction the run-4
objective demanded is made explicitly. The core argument — populating from the
model would create a second, unconsumed-until-codegen declaration of
actions/ports that can desync from the authoritative ones, the exact desync
class this ticket closes (ESC-R4-3 was such a desync) — is coherent and
consistent with the DF-2/G4 precedents against declarations nothing exercises.

**One imprecision, on the record:** the reconciliation doc's aside that the
stanzas have "no consumer anywhere in scripts/ or tests/"
(`port_honesty_reconciliation.md:78-79`) is loose — `scripts/generate_python.py`
reads top-level `ports:` (`:74,:83,:128,:452,:490`) and `state:` as
codegen input. That consumer is the case-codegen owner the recorded meaning
itself names ("filled only when generation_status reaches `generated`"), so
the durable manifest record is accurate and the disposition stands; only the
history doc's side sentence overstates. Observation, not a gap and not an
escalation — no plan line is contradicted and no scope question is open.

### 6.4 Out-of-scope inventory — does not gate

335 rows (run 4's 334, classifications carried row-identical, + row 359).
Standing observations carried: wrapper deletes out-of-model per the `:554-557`
ruling; bash runtimes unobservable-not-clean; **corpus_process declares the
spawn, not what the child did** (MF-027 rule) — child effects of a
user-supplied non-default corpus command are unrepresented by construction,
the same standing as test_process/runner_process children in run 4's grp rows;
the documented default corpus is the adapter battery whose children ARE the
modeled commands.

### 6.5 Scope escalations

**None.** ESC-R4-1 resolved by owner amendment (`:585`, §0); ESC-R4-2/3
resolved by CD-11 (§1, §6.3), each verified in the tree.

## 7. Verdict

- In-scope gaps: **0** — R4-1/R4-2/R4-3 each verified closed by changing the
  program's manifest declarations (the disposition run 4 assigned), with
  recorded rationale at every choice point.
- Escalations: **0 open** — the three run-4 escalations carry owner/ticket
  dispositions verified this run.
- Out-of-scope inventory: non-empty (335 rows), recorded.

**Verdict: `PASS`.** Zero in-scope gaps against the amended scope
(schedule_revision 4). On the record alongside the pass: both views remain
unrepresented by construction (quoted known_gap `:597`); `generate` remains
unmodeled (quoted `:585`/`:598`); the granularity and out-of-model rulings
inventory real behavior the model does not represent — all owner-declared
boundaries, reviewable in one place, none waived per-finding.

## 8. Attestation

1. **Enumerations.** Sweep 1: 5 `git ls-files` commands (raw
   2378/567/135/324/5), one stated filter (`specs/.history/**`), N = 359;
   M = 358 carried (surface-diff-identical rows, run 4's machine-emitted
   table) + 1 fresh = 359; `N == M`. Sweep 2: 13 category patterns applied
   fresh to the 6-file changed surface AND (fixed-pattern) to the 400c51a
   content of the 5 modified files (`ca5_delta_check.sh` output quoted in §3);
   carried counts for the 353 content-identical files rest on run 4's archived
   raws plus the content-identity argument, which the surface diff and
   name-status listing make mechanical. Sweep 3: same mechanics, 6 classes.
   Sweep 4: `ls` of 2 model dirs. All stated reconciliations hold.
2. **Surface not walked:** `specs/.history/**` (stated filter — except the
   CD-11 entry's manifest.json/results, which were read as evidence); non-code
   surface except the named model/manifest/catalog/binding/plan files (read);
   the 335 out-of-scope rows' contents (row 359 excepted — read).
3. **READ vs INFERRED.** Fresh reads this run: the plan scope blocks
   (`:520-599`, `:2396-2479`), `spec_manifest.yaml` effects/actions/stanza
   regions in full, `TlaSpecDevCli.tla` diff + annotation set + both No-@port
   notes, `kill_mutants.toml` IDs + both new blocks + port-test_process block,
   `kill_test.py`/`run_kill_test.py`/`effect_conformance_report.py`/
   `effect_conformance.py`/`corpus_diagnostics.py` gap-site regions,
   `new_ticket_workflow.py` diff, both kill-test test diffs,
   `ca4_classify.py` (row 359), CD-11's reconciliation doc and evidence tails,
   TLC outputs, ledger block. Carried without re-reading: run 4's 358 row
   classifications and its Sweep 2/3 group dispositions for content-identical
   files (licensed by the surface diff; this is the run's stated method, not
   silent sampling). Per-sweep: Sweep 1 — 1 row read fresh, 358 carried;
   Sweeps 2/3 — every delta hit read, carried groups not re-read.
4. **Scope by reasoning?** The carried `:524-525` totality reading (attested
   in runs 3-4, corroborated by the owner's ESC-3 ruling) — applied to row
   359 alongside `:521-522`. No other reasoning-based scope decision; the
   `:585`-vs-`:538-542` conflict run 4 had to adjudicate no longer exists.
5. **Reproducibility:** yes — `sweep-raw-run5/` holds the raw lists, the
   surface diff, the changed-file name-status, both enumeration scripts, and
   the 13 per-category changed-surface raws; a reader re-running them at
   5f84937, plus run 4's archived `sweep-raw-run4/`, re-derives every table.
6. **Findings about this prompt.** (a) STILL OPEN: Step-1 single-space regex;
   Step-4 hardcoded subdirectories; the run-4 finding that the prompt lacks a
   re-audit procedure after boundary amendments. (b) NEW: the prompt has no
   verify-by-diff protocol — this run's method (surface-diff license,
   fixed-pattern old/new content comparison, carried-row attestation) was
   specified by the dispatching instruction, not the prompt; without such an
   instruction an agent would either redo full sweeps (safe, expensive) or
   silently carry stale tables (the failure mode). Worth codifying with the
   re-audit rule. (c) The self-reported `N == M` limitation stands; note that
   this run's carried rows make the reviewer's recount depend on run 4's
   archived raws remaining intact — the immutability of `sweep-raw-run4/` is
   now load-bearing for two reports.
