# CD-11: experimental-surface port honesty — reconciliation record

Resolves audit run 4's R4-1, R4-2, R4-3 and the two four-run manifest desyncs
ESC-R4-2, ESC-R4-3 (`specs/results/epic-close/coverage_audit_report_run4.md`).
Zero TLA+ semantic delta: TLC on the ticket model reproduces the CD-10
baseline byte-for-byte in counts — 6,209,780 states generated, 283,805
distinct, depth 25 (`tlc_current.txt` here vs
`specs/results/cd10-post-promotion-tlc.txt`).

## R4-1 — RunKillTest's undeclared production-source writes and spawn

Code sites verified before the fix: `scripts/kill_test.py:548` writes the
mutated copy over the catalog target and `:551` writes the original back in
the `finally` branch, driven per mutant by `scripts/run_kill_test.py:130`;
the catalog's `path` keys target `scripts/*.py` and
`skill-scripts/install-tla-spec-dev.sh`. The per-mutant corpus spawn is
`scripts/kill_test.py:609` (subprocess_case_runner) reached via
`run_kill_test.py:198`, and its argument is the unconstrained user-supplied
`--corpus-command`.

**Choice: declare, do not relocate.**

- New port `mutation_write` (`filesystem.write`, target `*scripts/*`) on
  RunKillTest. The glob covers both catalog trees (fnmatch `*` crosses
  separators, so `scripts/` and `skill-scripts/` both match); no other
  declared write port covers them (spec_tree `**/specs/**`, evidence_report
  `**/results/**`, cli_artifact `**/.venv/**`). Declaring was chosen over
  seeding a copied tree because the finally-branch restore is the shipped
  defense against #22-class corruption, and the schema distinguishes exactly
  this write so an interrupted run's mutated tree cannot hide — the honest
  move is to make the danger visible, not to relocate it.
- New port `corpus_process` (`process.spawn`, target `*`) on RunKillTest,
  replacing `test_process` on that row (test_process stays declared and
  exercised via RunSpecUnitTests). Any glob narrower than `*` would assert a
  constraint the code does not enforce: the documented pytest-shaped corpus
  command is one possible value, not a contract.

## R4-2 — RunEffectConformance's undeclared sandbox writes

Code sites verified: `scripts/effect_conformance_report.py:149` defaults the
work dir to `spec_dir/.effect-conformance-work` and mkdirs it, `:163` mkdirs
per-case dirs; `scripts/effect_conformance.py:619`/`:656` mkdir the sandbox
roots beneath them. All land under `**/specs/**` while the action declared
`[evidence_report]` only.

**Choice: declare `spec_tree` on the action, not relocate the work dir.**
Rationale, in order of weight:

1. The same physical sandbox writes on the `run spec-unit-tests` path are
   already declared as spec_tree on RunSpecUnitTests — declaring makes the
   two paths symmetric instead of describing one honestly and hiding the
   other.
2. The work tree is spec-scoped working state, not evidence; moving it under
   `results/` to let evidence_report cover it would blur the evidence
   surface, and `--work-dir` remains available for callers who want it
   elsewhere.
3. The dishonesty lived in the manifest, not in the program — so the
   manifest is what changed. Relocating would alter a shipped default purely
   to fit a declaration.

## R4-3 — AnalyzeCorpus's dead declared port

Code verified: `scripts/corpus_diagnostics.py` `add_arguments` (:835-852)
registers `cases_dir`/`--view`/`--manifest` only — no `--out`; `run()`
(:902-935) prints the rendered report and returns; the file contains no
write site.

**Choice: remove the row's `evidence_report`, G4-style.** `AnalyzeCorpus: []`
is deliberately an EMPTY row, not an absent one (the CD-10 RecordBudgets
rule): the command reads and prints, performing no distinct declared effect.
Removal matches shipped print-only behavior; adding a writer would be new
behavior invented to justify a stale declaration — the exact inversion CD-09's
G4 ruling forbids.

## ESC-R4-2 — empty `state_fields` / `actions` / `ports` stanzas

The stanzas are scaffold-emitted placeholders (`scripts/new_ticket_workflow.py`
emits them empty in both the current and desired manifest templates) with no
consumer anywhere in scripts/ or tests/. **Choice: record the placeholder
meaning rather than populate.** Populating from the model would create a
second, unconsumed declaration of actions/ports that can desync from the
authoritative ones — the exact desync class this ticket closes. The manifest
comment (above the stanzas) now states: empty means "no generated case index
yet" (case_codegen.generation_status is `planned`), NOT "the model has no
state/actions/ports" — those live in TlaSpecDevCli.tla (9 variables, 15
actions) and effects.components (9 ports). The same meaning is recorded at
the schema source, `scripts/new_ticket_workflow.py`, so every future
scaffold documents itself.

## ESC-R4-3 — @port annotation vocabulary

**Choice: rename the annotations to the declared port vocabulary** (the
first remediation offered by the escalation). All 14 `@port
TlaSpecDevCliPort.<command_name>` annotation comments in TlaSpecDevCli.tla
now carry one line per declared port of the action's effects row; the two
empty rows (RecordBudgets, AnalyzeCorpus) carry an explicit "No @port" note
naming the ruling. The annotation vocabulary and the declared port names now
intersect exactly: {cli_artifact, spec_tree, evidence_report, test_process,
runner_process, spec_tree_delete, git_metadata, mutation_write,
corpus_process} on both sides. Comments only — nothing parses `@port` (the
only `@command/@result` emitters are scaffold templates), and TLC counts are
unchanged.

## Kill catalog and boundary counts

`kill_mutants.toml` gains `port-mutation_write` (seeded() writes the original
back instead of the patched copy — the kill test measures nothing while
claiming it measured) and `port-corpus_process` (the spawn drops the
command's final argument). Both patterns verified verbatim-unique, parse
clean, and restore byte-identical (tests/test_kill_test.py real-catalog
battery). Required boundaries: 22 = 9 declared ports + 13 invariants;
`tests/test_kill_test.py` updated 20 → 22 with a CD-11 note, and the
`--list-boundaries` CLI assertion updated to `22/22`.

## Budget carry

`max_distinct_states: 500000` and its negotiated 2026-07-19 rationale are
untouched in the ticket desired/current manifests and verified again
post-promotion in `specs/current/spec_manifest.yaml`.
