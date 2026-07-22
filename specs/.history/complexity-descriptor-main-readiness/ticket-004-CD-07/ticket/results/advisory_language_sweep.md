# CD-07 advisory-language sweep (VAL-04 evidence)

Date: 2026-07-22. Branch: `feature/92-cd07-advisory-polish`.
Claim: **no gate-era budget language remains in scaffold output or in any
generated file**, and every remaining `hard gate` occurrence in the live tree
is either (a) a real non-budget hard gate that exists by design, (b) an
explicitly superseded historical narrative, or (c) an immutable record.

## 1. Scaffold output and generated files: zero hits

Fresh scaffold in a clean directory, run under bare `python3` (no PyYAML):

```
$ python3 scripts/tla_spec_dev.py --spec-root specs scaffold project --name OrderDemo   # exit 0
$ python3 scripts/tla_spec_dev.py --spec-root specs scaffold workflow T-1 "Demo workflow"  # exit 0
$ grep -ri "hard gate" scaffold_project.out scaffold_workflow.out specs/
(no matches; grep exit 1)
```

What the scaffold now says instead (epilog, from `scripts/budgets.py
budget_prompt`, printed verbatim by both scaffold commands):

```
Budgets are advisory thresholds, not gates: analyze complexity reads them from
this manifest and warns -- naming the component/variable/action and the measured
fact -- when a threshold is exceeded. It never blocks promotion or changes its
exit code. The one hard operational limit is tlc_seconds (wall time, not
complexity). The EXPERIMENTAL fuzzing surface (case generation, the adapter
runner, the mutation kill test) also reads its caps and floors from this block.
See SKILL.md 'Complexity Budgets Are Advisory' and references/modular_fuzzing.md 'Budgets'.
```

All three generated manifests (`specs/program_model/spec_manifest.yaml`,
`specs/current/spec_manifest.yaml`,
`specs/desired_program_model/spec_manifest.yaml`) carry the advisory budgets
comment ("advisory thresholds ... warns with facts and never blocks") and the
VAL-05 `justification:` schema comment. Regression-locked by
`tests/test_budgets.py::test_scaffold_project_emits_budgets_and_prompt`,
`::test_scaffold_workflow_emits_budgets_and_prompt`, and
`::test_budget_prompt_and_scaffold_comments_use_advisory_language`.

Sources reworded this ticket:
- `scripts/budgets.py` — `budget_prompt` epilog (was "Budgets are hard gates,
  not aspirations") and module docstring.
- `scripts/new_ticket_workflow.py` — both generated-manifest budget comments
  (the VAL-04 sites, previously "hard gates read by analyze complexity ...").
- `scripts/onboard_program_model.py` — the scaffold-project manifest budget
  comment (same gate-era sentence, found by this sweep).

## 2. Repo-wide inventory of remaining `hard gate` occurrences (case-insensitive)

Command: `grep -rni "hard gate" --include='*.py' --include='*.sh'
--include='*.md' --include='*.yaml' --include='*.yml' --include='*.tla' .`
(excluding `specs/.history/`, which is append-only and exempt by the plan).

Disposition of every live-tree hit:

| file | occurrences | disposition |
|---|---|---|
| `scripts/corpus_diagnostics.py` | 3 | EXEMPT (by-design, non-budget): the EXPERIMENTAL corpus case-cap gate really does report-and-exit-2 rather than trim; describing it as a hard gate is accurate (ex2 validation scoring: "a hard gate by design"). |
| `scripts/generate_cases_from_tlc_dump.py`, `scripts/export_testgraph_cases.py` | 1 each | EXEMPT (by-design, non-budget): same case-cap gate, MF-014 shape. |
| `scripts/testgraph_channels.py` | 2 | EXEMPT (by-design, non-budget): MF-015 external channel enforcement is a real hard gate with no override. |
| `scripts/scaffold_spec.py` | 1 | EXEMPT (by-design, non-budget): the generated `testgraph_bindings.yml` comment describes MF-015 channel enforcement, which does hard-fail; not budget language. |
| `scripts/kill_test.py` | 1 | EXEMPT (EXPERIMENTAL surface): docstring explains why the kill-rate floor exits nonzero as built; SKILL.md documents that this does not gate promotion. |
| `specs/program_model/spec_manifest.yaml` | 1 | EXEMPT (by-design, non-budget): MF-015 channel-enforcement note ("all three are hard gates with no override"), promoted model text. |
| `references/architecture_tractability.md` | 3 | EXEMPT (superseded historical narrative): each occurrence sits inside "Advisory, Not Blocking" / "No Degenerate Escapes" text that explicitly states the hard-gate framing is reversed and outranked. |
| `references/modular_fuzzing.md` | 1 | EXEMPT (history note): "*History.* The complexity check was originally a hard gate ..." |
| `references/testgraph_adapters.md` | 1 | EXEMPT (by-design, non-budget): channel-enforcement gates. |
| `tests/test_budgets.py` | 6 | SELF-REFERENTIAL: this ticket's negative assertions (`"hard gates" not in ...`). |
| `tests/test_corpus_diagnostics.py`, `tests/test_analyze_complexity.py` | 1 each | EXEMPT: comments describing the by-design case-cap gate and its history. |
| `specs/desired_program_model/ticket_plan.yaml`, `specs/tickets/CD-07/ticket.yaml`, `specs/results/skill_feedback.md`, `specs/results/epic-close/deferred_findings_final.yaml` | 2 each | EXEMPT (immutable records): dispatched plan/ticket text and triaged findings quote the VAL-04 defect verbatim. |
| `examples/validation/runs/*/scoring.md` | 4 total | EXEMPT (immutable validation records). |
| `tickets/014-*.md`, `tickets/027-*.md`, `EPIC-HANDOFF.md`, `COMPLEXITY-DESCRIPTOR-EPIC.md` | 1 each | EXEMPT (historical epic/ticket records of the pre-reframe era). |
| `specs/.history/**` | many | EXEMPT by plan rule: append-only history is never edited. |

No occurrence outside these categories remains: **zero reachable scaffold
output, generated file, epilog, or doctrine doc calls budgets hard gates.**

## 3. Related UX evidence captured in the same sweep

- VAL-02: a per-docs budgets block (no `kill_rate_floor`, no
  `max_symmetric_instances`) scans with an empty stderr — see
  `fitness_manifest_config_error.txt` (stderr section) and
  `tests/test_budgets.py::test_per_docs_block_without_experimental_keys_scans_clean`.
- CD-02-DF-01: the no-manifest warning is now
  `warning: no manifest supplied (no --manifest and no spec_manifest.yaml next
  to the spec); using documented default budgets
  (references/modular_fuzzing.md)` — no sentinel path; see
  `fitness_manifest_config_error.txt` and
  `tests/test_analyze_complexity.py::test_no_manifest_warning_names_no_sentinel_path`.
- VAL-03: `bash scripts/run_tlc.sh specs/tickets/CD-07/current/TlaSpecDevCli.tla
  specs/tickets/CD-07/current/MC.cfg` exits 0 (TLC green, 283,805 distinct
  states) and leaves **no `states/` directory** in the spec dir — TLC's
  `-metadir` now points at a `mktemp -d` location removed by an EXIT trap.
