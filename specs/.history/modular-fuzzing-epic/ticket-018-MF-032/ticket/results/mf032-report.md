# MF-032 — Case execution across the remaining adapters

Builds on MF-028 (the banding spike) and MF-031 (the two missing UpdateTicket
adapters + ticket-segment machinery). This ticket gives `run()` to the adapters
MF-028 banded runnable, promotes the shared before-state builder/projector into
a module, and fixes the runner's all-or-nothing comparison.

Toolchain pin honored throughout: `python3 scripts/tla_spec_dev.py`, never
`tla-spec-dev` from PATH; no `skill-manager sync`.

## 0. Headline

Four adapters now execute generated cases end to end. The remaining eleven stay
`apply()`-only, and that is the correct, structural outcome MF-028 predicted —
not a shortfall. The honest executability number is **7.8% → 9.8%**, and the
reason it is small is itself the finding: the corpus is dominated by gate/oracle
actions whose after-state cannot be projected from the filesystem.

## 1. Per-adapter status (the fifteen MF-028 banded, plus MF-031's two)

| # | Adapter | Action | MF-028 band | MF-032 status | Structural reason (if blocked) |
|---|---|---|---|---|---|
| — | BuildSkillCliAdapter | BuildSkillCli | (MF-028 floor) | **executes** | done in MF-028 |
| — | ScaffoldProjectAdapter | ScaffoldProject | (MF-028 measured) | **executes** | done in MF-028 |
| 1 | InstallLocalCliAdapter | InstallLocalCli | trivial | **executes (NEW)** | — |
| 2 | TestGraphCliAdapter | ValidateTestGraphCli | trivial | apply()-only | **dead binding**: not a model action; no corpus case carries this label, so a `run()` can never be exercised. Kept as the spec-unit surface. |
| 3 | ScaffoldWorkflowAdapter | ScaffoldWorkflow | moderate | **executes (NEW)** | — |
| 4 | RecordBudgetsAdapter | RecordBudgets | moderate | **executes (NEW)** | — (no CLI command corresponds; run() performs the in-place manifest edit `_negotiate_budgets`) |
| 5 | OpenTicketAdapter | OpenTicket | moderate | **executes (NEW)** | — (first setup adapter advancing `ticket_state`; reuses MF-031's projection) |
| 6 | RunSpecUnitTestsAdapter | RunSpecUnitTests | moderate | apply()-only | **blocked**: after-state changes `corpus_gate` and `effect_conformance` to *nondeterministic* verdicts and advances the ticket to `SpecUnitTestsPassed(4)`, which `project_ticket_state` cannot observe. Projecting these needs oracle-verdict projection (MF-023/MF-034 surface), not filesystem evidence. |
| 7 | AnalyzeComplexityAdapter | AnalyzeComplexity | hard | apply()-only | **blocked**: `apply()` asserts both sides of the gate plus generation-advisory in one call (≥3 transitions); the after-state sets `complexity_gate ∈ {pass,fail}`, a nondeterministic verdict not recoverable from the tree. |
| 8 | AnalyzeCorpusAdapter | AnalyzeCorpus | hard | apply()-only | **blocked**: same shape; sets `corpus_gate ∈ {pass,fail}`. Also implicated in the `analyze corpus` OOM (MF-034). |
| 9 | RunEffectConformanceAdapter | RunEffectConformance | hard | apply()-only | **blocked**: sets `effect_conformance ∈ {clean,gaps,dead_surface,unobservable}` — an oracle verdict, not filesystem state; and the effect sandbox sees only in-process CPython while every adapter shells out (MF-028 §3.2b). |
| 10 | RunKillTestAdapter | RunKillTest | hard | apply()-only | **blocked**: 200+ lines building 4 fixture spec trees and asserting three independent properties; a single case cannot express it. Sets `kill_test ∈ {pass,below_floor,incomplete_catalog}`, a verdict. |
| 11 | CloseTicketAdapter | CloseTicket | hard | apply()-only | **blocked**: before-state needs a ticket at `SpecUnitTestsPassed(4)`, which MF-031 refuses as out-of-segment (needs the spec-unit/close gate machinery). |
| 12 | ClosePromotionPreservesCurrentAdapter | CloseTicket | blocked | apply()-only | **blocked**: duplicate `action_name="CloseTicket"`; unreachable under one-label-to-one-adapter binding (MF-031 finding). |
| 13 | SkillFeedbackCloseOutAdapter | CloseTicket | blocked | apply()-only | **blocked**: duplicate label **and** closes a workflow twice to assert accumulation across closes — not a single-transition property. |
| 14 | ComplexityLedgerCloseOutAdapter | CloseTicket | blocked | apply()-only | **blocked**: duplicate label; multi-close ledger-gating battery. |
| 15 | UpdateTicketDesired / UpdateTicketCurrent | UpdateTicket* | (new work) | **executes** | done in MF-031 |

**Summary:** 4 newly executing this ticket (InstallLocalCli, ScaffoldWorkflow,
RecordBudgets, OpenTicket); 4 already executing (2 MF-028 + 2 MF-031); 1 dead
binding (TestGraphCli); 10 remain structurally `apply()`-only.

## 2. Real end-to-end runs (the real runner, real generated cases)

`results/case-execution-run.txt` — each case run through
`scripts/run_generated_case_adapters.py … --batch` against the reduced corpus,
mapped by `results/case_adapters_mf032.toml` (a **results-local** mapping;
binding the corpus into the production `case_adapters.toml` is MF-023's surface):

```
InstallLocalCli / case_0003_install_local_cli   -> executed 1 cases in batch, exit=0
ScaffoldWorkflow / case_0009_scaffold_workflow  -> executed 1 cases in batch, exit=0
RecordBudgets   / case_0007_record_budgets      -> executed 1 cases in batch, exit=0
OpenTicket      / case_0022_open_ticket         -> executed 1 cases in batch, exit=0
```

`results/case-execution-projection.txt` — field-by-field detail: each POSITIVE
run reports **10 checked / 1 unchecked (`result.next`) / 0 mismatch**.

## 3. Negative controls (a check that cannot fail is not a check — MF-029)

Every newly-executing adapter has a negative control proven to fail, derived
from the before-state and the transition, never from the field checked. On the
**real** corpus cases (`results/case-execution-projection.txt`):

```
InstallLocalCli  corrupt setup_phase 2->3   -> REJECTED (projected 2 != model 3)
ScaffoldWorkflow corrupt lastCommand        -> REJECTED (projected real != model 'WRONG')
RecordBudgets    corrupt setup_phase 4->5   -> REJECTED (projected 4 != model 5)
OpenTicket       corrupt ticket_state value -> REJECTED (projected {..:1} != model {..:2})
```

Also encoded as spec-unit tests in
`tests/test_tla_spec_dev_case_execution_run.py` (12 tests: 4 positive + 6
negative + 2 guard/can_run).

## 4. The shared module — a module, not a base class

`adapter_case_runtime.py` (new, beside `production_adapters.py`) holds the
before-state builder (`materialize_before` + the setup/ticket-segment replay),
the projector (`project_state`, `project_ticket_state`), and the field
comparator (`compare_projection`, `enforce_projection`), plus the constants,
markers and `recover_ticket_except_index`. Every case-executing adapter imports
these free functions and composes them in its own `run()`.

Why a module and not a base class: the adapters' `apply()` signatures are
incompatible — `apply()`, `apply(bin_dir, cache_dir)`,
`apply(target_repo, *, ...)` — so a shared base class would fight them
(MF-028 §5.3). Free functions compose without constraining the surface.
`production_adapters.py` adds its own directory to `sys.path` so the sibling
module resolves in all three load contexts: runner `--import-root`, the promoted
`specs/current` tree, and `importlib.util.spec_from_file_location` in spec-unit
tests.

## 5. Runner per-field comparison (MF-031 deferred this here)

`scripts/run_generated_case_adapters.py`: the whole-dict `==` (runtime's
`assert_case_result`, and the runner's `assert_projected_state`) is replaced by
per-field comparison honoring UNCHECKED:

- `compare_fields_honoring_unchecked(expected, actual, unobservable)` — reports
  agreements / disagreements / **unchecked** separately, so an unobservable
  field is reported UNCHECKED, never faked as agreement.
- `assert_case_result_per_field(...)` — the per-field after-state check; an
  adapter can return a real `after` plus the fields it could not observe
  (via `semantic_output["unobservable"]`) and get an honest per-field verdict
  from the runner instead of the old all-or-nothing boolean. Wired into both the
  batch executor and the generated-program template.
- `assert_projected_state` now compares dict projections field by field
  (keeping the `projected state mismatch` message).

`runtime.py::assert_case_result` was **not** edited — it is out of this ticket's
conflict keys and the fix lives entirely in the runner, which is in scope.

Tests updated/added in `tests/test_case_adapter_runtime.py`:
`test_compare_fields_honoring_unchecked_reports_three_buckets`,
`test_assert_case_result_per_field_honors_declared_unobservable`,
`test_assert_case_result_per_field_fails_on_checked_field`,
`test_batched_runner_after_comparison_is_per_field`. No existing test needed its
contract changed — the projected-state tests pass unchanged because per-field
comparison of equal dicts agrees and a real mismatch still fails.

## 6. Corpus executability, re-measured (not assumed)

Reduced single-ticket corpus (`MCsmall.cfg`: 1 spec root, 1 ticket) — the full
`MC.cfg` corpus is 5,619,356 transitions / ~11 GB `cases.py` and intractable to
load (MF-034's OOM surface). 61,081 cases. Full output:
`results/corpus-executability.txt`.

**Two axes, and MF-032 moves only the second.**

- **Axis 1 — before-state materializable** (MF-031's axis): **81.6%**,
  unchanged. MF-032 does not touch before-state construction.
- **Axis 2 — action has a `run()` adapter AND before-state materializable**
  (true end-to-end executability): **7.8% → 9.8%** (+1221 cases:
  OpenTicket 699 + ScaffoldWorkflow 520 + RecordBudgets 1 + InstallLocalCli 1).

MF-031's headline 81.6% measured before-state materializability alone; it
over-counts true executability because it credits cases whose action still has
no single-transition `run()`. The dominant blocker is now unambiguously the
**action axis**: 89.2% of the corpus is RunEffectConformance (15,920),
RunKillTest (11,940), RunSpecUnitTests (10,392), AnalyzeCorpus (7,960),
AnalyzeComplexity (7,960) and CloseTicket (304) — the HARD/BLOCKED bands whose
after-state changes nondeterministic gate verdicts not recoverable from the
filesystem. Making those execute needs oracle-verdict projection and in-process
CLI invocation, an axis MF-028 flagged and the current plan assigns to
MF-023/MF-034 — a finding, not a failure.

## 7. Did I need anything outside my conflict_keys?

No. All production changes are in `specs/program_model/production_adapters.py`
(promoted from ticket-local `current`/`desired`) — plus the new sibling module
`adapter_case_runtime.py` beside it — and `scripts/run_generated_case_adapters.py`.
The results-local mapping and measurement scripts live under the evidence root.
`case_adapters.toml`, `runtime.py`, and the TLA+ model were **not** touched.

## 8. Validation matrix (actual)

| Check | Command | Result |
|---|---|---|
| TLC | `run_tlc.sh … MC.cfg` (120s ext. timeout) | 231,621 distinct / depth 25 — identical to baseline (zero model delta) |
| spec-unit | `run spec-unit-tests --ticket MF-032` | 60 passed |
| repo units | `pytest tests -q` | 512 passed (508 baseline + 4 new runner tests; no regression) |
| specWorkflow | `test-graph run.py specWorkflow` | PASSED 8/8 |
| cliWorkflow | `test-graph run.py cliWorkflow` | PASSED 2/2 |

`max_distinct_states: 500000` carried through `desired/` and verified in
`specs/current/spec_manifest.yaml` after promotion (SF-003, #32).
