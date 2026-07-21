# MF-038 — Kill-rate probe: do the generated cases catch real bugs?

**Investigation ticket. The deliverable is this measured number, not a feature.**
No production code changed; the TLA+ model is byte-identical to baseline. The
probe seeds realistic bugs into the production CLI implementations the runnable
corpus exercises and measures how many the generated cases catch.

Toolchain pin honored throughout: `python3 scripts/tla_spec_dev.py`, never
`tla-spec-dev` from PATH; no `skill-manager sync`.

## 0. Headline

- **Control: GREEN.** The unmutated runnable corpus passes (14/14 cases,
  exit 0), so the kill rate is meaningful (MF-016's own safeguard).
- **KILL RATE: 4 / 13 = 0.308.**
- **Every one of the 9 subtle (content / value / field) bugs SURVIVED. Every
  bug that was killed was a structural bug that changed which directory or
  tree gets created.**

The one-line finding for the owner: **the generated cases catch "did the command
create the right directory / advance the right lifecycle stage", and nothing
finer.** They are existence-and-path oracles, not content oracles. A defect that
writes the wrong *value*, drops or corrupts a *field*, or sets a
plausible-but-wrong *enum* is invisible to every oracle in the corpus today.

## 1. What was measured, and against which denominator

- **Instrument:** the real MF-016 kill-test primitives —
  `kill_test.subprocess_case_runner` (applies each mutant with
  `kill_test.seeded()` and always restores it) and `kill_test.control_run` (the
  green-control gate). Harness: `results/measure_kill_rate.py`. No threshold was
  lowered; there is no floor in this measurement (advisory reframe, 2026-07-20).
- **Corpus (the instrument), denominator note:** the **reduced runnable subset**.
  The full `MC.cfg` corpus is intractable to load (~11 GB, MF-034's OOM). Per
  MF-031/MF-032 the reduced `MCsmall.cfg` corpus (1 spec root, 1 ticket; 61,081
  cases) is used, and within it only the **~10% runnable** filesystem-mutating
  commands execute end to end. The probe runs a **14-case representative
  selection** spanning every runnable action (BuildSkillCli, InstallLocalCli,
  ScaffoldProject, RecordBudgets, ScaffoldWorkflow ×3, OpenTicket ×3,
  UpdateTicketDesired ×2, UpdateTicketCurrent ×2). ScaffoldProject / RecordBudgets
  / InstallLocalCli / BuildSkillCli each have exactly **one** case in the whole
  reduced corpus, so the selection is representative of the runnable corpus's
  kill power, not a sample of it.
- **Denominator of the rate = the 13 mutants** (killed / total). The cases are
  the instrument, not the denominator.
- **Bugs seeded into** the production CLI implementations those adapters drive:
  `scripts/onboard_program_model.py` (`scaffold project`),
  `scripts/new_ticket_workflow.py` (`scaffold workflow`, `open ticket`),
  `scripts/budgets.py` (budget defaults emitted into the scaffolded manifest).
  Every mutant is a literal, reviewable behavioral change — not a syntax break.

## 2. The oracle surface (why the number is what it is)

Each runnable adapter (`specs/current/production_adapters.py` +
`adapter_case_runtime.py`) MATERIALIZEs `case.before` by replaying the CLI,
EXECUTEs the action, PROJECTs the real repository back into the 9 model
variables, and COMPAREs field by field. But the projection reads only:

- `setup_phase` — from **directory/file existence**: `program_model/*.tla`
  exists → 3; manifest contains the literal `source: negotiated` → 4;
  `current/` **and** `desired_program_model/` dirs exist → 5.
- `ticket_state` — from **directory/marker existence**: `tickets/<id>/` exists →
  Opened; readiness markers in the `desired`/`current` trees → DesiredReady /
  CurrentReady.
- `result.accepted` — the CLI **exit code**.
- `lastCommand` — the command the adapter itself ran (not read from the tree).
- `spec_root` is declared UNCHECKED (unparameterized corpus); `result.next` is
  UNCHECKED (unprojectable); the four gate variables are carried UNCHANGED.

Nothing reads the **contents** of any scaffolded file, any budget value, any
manifest field, any enum, or any count. That is the entire explanation for the
survivor set below.

## 3. Per-bug kill / survive table

| Mutant | File / command | Class | Result | Why |
|---|---|---|---|---|
| m01 scaffold-project-wrong-dir | onboard `program_model`→`program_modelX` | obvious/structural | **KILLED** | `program_model` never appears → `setup_phase` projects 2≠3; also breaks downstream before-state replay |
| m08 scaffold-workflow-wrong-desired-dir | ticket_wf `desired_program_model`→`…X` | obvious/structural | **KILLED** | `desired_program_model` never appears → `setup_phase` 4≠5; downstream `open ticket` finds no ticket plan |
| m11 open-ticket-wrong-dir | ticket_wf `tickets/<id>`→`tickets/<id>X` | obvious/structural | **KILLED** | `project_ticket_state` finds no `tickets/cli_entrypoint` → ticket_state {…:0}≠{…:1} (clean projected-state conformance kill) |
| m13 open-ticket-desired=current | ticket_wf desired tree ← current path | subtle/structural | **KILLED** | ticket `desired/` subtree never created → UpdateTicketDesired before-state replay: "no desired model to mark ready" |
| m02 scaffold-project-empty-Internal.tla | onboard writes empty `Internal.tla` | subtle/content | SURVIVED | file still exists → `any(*.tla)` true → phase 3; no oracle reads `.tla` contents |
| m03 scaffold-project-model_role-enum | manifest `accepted`→`rejected_program_model` | subtle/enum | SURVIVED | manifest content never projected |
| m04 scaffold-project-workflow-enum | manifest `project_onboarding`→`project_teardown` | subtle/enum | SURVIVED | manifest content never projected |
| m05 budgets-max_distinct_states | `50000`→`40000` | subtle/value | SURVIVED | budget values never projected |
| m06 budgets-internal_cases-offbyone | `200`→`199` | subtle/off-by-one | SURVIVED | budget values never projected |
| m07 budgets-external_cases | `50`→`40` | subtle/value | SURVIVED | budget values never projected |
| m09 scaffold-workflow-manifest-wrong-field | `relation_to_program_model` wrong value | subtle/field | SURVIVED | current manifest content never projected |
| m10 ticket-plan-phase-enum | ticket_plan `planning`→`execution` | subtle/enum | SURVIVED | ticket_plan content never projected (only its existence / lookup) |
| m12 open-ticket-misplace-gitkeep | `results/.gitkeep`→`.gitkeepX` | subtle/path | SURVIVED | that file is never inspected by any oracle |

**Killed: m01, m08, m11, m13 (4). Survived: m02–m07, m09, m10, m12 (9).**

## 4. Survivor analysis — for each, WHY the cases missed it

All nine survivors share one root cause with three faces:

- **UNCHECKED field / no oracle for the surface (m02, m03, m04, m05, m06, m07,
  m09, m10, m12).** The projection maps a real repository into 9 model variables
  and none of them is a function of file *content*, a budget *value*, a manifest
  *field*, an enum, or a specific placeholder path. The variables that could
  carry such information (`lastCommand`, `result`, `spec_root`) are either
  reconstructed from the adapter's own invocation or declared UNCHECKED. So these
  bugs change bytes on disk that no oracle ever reads — the exact "UNCHECKED
  field" failure mode the doctrine names. The complexity analyzer already flagged
  the sibling of this gap ("no configured invariant reads [lastCommand, result]").
- **Coverage/granularity gap (m02 specifically).** Even the one variable that
  *is* read from the `.tla` surface — `setup_phase` — reads only *presence of any
  `*.tla`*, never that a specific module is non-empty or well-formed. An empty
  `Internal.tla` is a real, serious bug (the internal view has no model) and the
  corpus cannot see it.
- **Path never exercises the difference (none).** No survivor is due to the
  selected cases failing to run the mutated code — every mutated command WAS
  executed (control green, and each survivor's file was written); the divergence
  simply lands in a place no oracle observes. This is a shallow-oracle result,
  not a coverage-of-code result.

## 5. Recommendation

**As it stands, model-derived conformance testing is NOT yet worth shipping as
"case advising" on the strength of its bug-catching — the honest kill rate is
0.31, and it is 0.31 only because a third of this catalog was deliberately
structural. Weight the catalog the way real defects are distributed (mostly
wrong values and fields, not wrong directories) and the rate trends toward the
~0/9 the subtle band actually scored.** The cases today are an
*existence-and-exit-code* smoke test dressed as conformance: they confirm a
command created the expected tree and returned 0, which is real but shallow
value.

What would deepen the cases (and is exactly what a survivor points at):

1. **Project file/field content into model variables.** The single highest-value
   change: give the model variables that read the *contents* the commands
   produce — the scaffolded budget block, the manifest `status`/`model_role`, the
   ticket_plan `phase`/`status` — and project them from the real tree. Every
   m03–m10 survivor dies the moment one such variable exists and is compared.
2. **Make `setup_phase` (or a sibling) sensitive to module well-formedness**, not
   just `*.tla` presence, so m02 (empty/again-corrupt Internal.tla) is caught.
3. **Widen the corpus of runnable actions** (the 90% blocked on oracle-verdict
   projection, MF-023/MF-034) so the instrument covers more than 6 setup
   commands — but note this probe shows the *depth* problem is independent of and
   more urgent than the *breadth* problem: even on fully runnable commands the
   oracles are shallow.

The kill test itself did its job: it produced a precise, un-tuned number and its
survivors each name the model variable / action to refine
(`results/kill-rate-report.json`, field `refine_variable`/`refine_action`). That
pointer machinery is the shippable part; the corpus's current oracle depth is
not.

## 6. Honesty statement

No threshold was lowered, no survivor deleted, no seeding restricted to
catchable bugs (9 of 13 are subtle, and all 9 survived — the catalog is if
anything generous to the corpus by including 4 structural bugs). The result is
reported exactly as measured. A low kill rate is a valid outcome and is the
finding here. `ignored_suppression_keys: none`.

## 7. Reproduce

```
# 1. generate the reduced runnable corpus (61,081 cases)
python3 scripts/generate_cases_from_tlc_dump.py \
  specs/current/TlaSpecDevCli.tla specs/current/MCsmall.cfg \
  --out <out> --package tlc_state_graph_cases --view internal --tlc2 tlc2

# 2. measure the kill rate (control-first, then 13 mutants)
python3 specs/tickets/MF-038/results/measure_kill_rate.py \
  <out>/spec-unit/tlc_state_graph_cases \
  --out specs/tickets/MF-038/results/kill-rate-report.json
```

Artifacts: `kill_mutants_mf038.toml` (catalog), `case_adapters_mf038.toml`
(results-local mapping, NOT the production `case_adapters.toml` — binding the
corpus into production is MF-023's surface), `measure_kill_rate.py` (harness),
`kill-rate-report.json` (machine-readable kill matrix + per-survivor pointers),
`tlc.txt` (baseline: 231,621 distinct / depth 25).
