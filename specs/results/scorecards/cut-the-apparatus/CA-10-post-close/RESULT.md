# The post-close suite figure, and what the close cost

**Tree:** `epic/cut-the-apparatus` at `7d99969` (the performed close) plus one
repair to `tests/test_disposition_requirement.py`. **Nothing else changed**, and
nothing was edited while the run was in flight.

**Command** (the one the epic doc pins; `--with pyyaml` is required):

```bash
uv run --with pytest --with pyyaml -m pytest tests -q
```

## The figure

| | failed | passed | skipped | collected |
|---|---:|---:|---:|---:|
| **pre-close** (`7d99969^` = `0ed12a5`) | **7** | **1497** | **0** | **1504** |
| **post-close** (this tree) | **11** | **1458** | **22** | **1491** |

`11 failed, 1458 passed, 22 skipped in 1176.74s (0:19:36)`, exit 1.

**The post-close figure is worse than the pre-close one, and every unit of the
difference is attributed below.** Nothing here is unexplained.

## Per-red accounting against 7 / 1497, per `denominator_rule`

### Reds: 7 → 11 is **−2 denominator, +6 numerator**

| pre-close red | post-close | movement |
|---|---|---|
| `test_architecture_tags::test_the_same_tag_control_holds` | still red, same cause | unchanged (deliberate, `RM-06-DF-01`) |
| `test_goal_baseline_is_a_card::…cannot_be_re_opened` | still red, **DIFFERENT CAUSE** | see below |
| `test_source_citations::…[specs/current/spec_manifest.yaml]` | **gone** | **denominator −1** |
| `test_source_citations::…[specs/desired_program_model/spec_manifest.yaml]` | **gone** | **denominator −1** |
| `test_source_citations::…[specs/program_model/spec_manifest.yaml]` | still red, same cause | unchanged |
| `test_instrument_demonstrations::test_every_declared_path_exists` | still red | unchanged (declared, `CA-04-DF-04`) |
| `test_instrument_demonstrations::test_every_fast_demonstration_reproduces` | still red | unchanged (declared, `CA-04-DF-04`) |

**`test_source_citations` drops from 3 reds to 1 because two of its subjects no
longer exist. That is a DENOMINATOR FALL, NOT A REPAIR.** Nothing about the
citations improved; the files holding them were deleted by the close. The
predicted movement is **confirmed**.

Six reds are new, and all six are the close:

| new red | cause | class |
|---|---|---|
| `test_ticket_retirement::…delivered_plan_has_matching_close_receipts` | `missing ticket plan: …/specs/desired_program_model/ticket_plan.yaml` | **predicted; confirmed** |
| `test_port_case_generation::test_this_repositorys_own_manifest_declares_no_orphan_port_name` | `load_port_catalog(specs/current/spec_manifest.yaml)` returns an empty catalogue, so `assert declared` fails on `set()` | **not predicted** |
| `test_score_tools::test_a_refuted_finding_stays_on_the_record_with_its_filing` | `score_tools._finding_ids()` | **not predicted** |
| `test_score_tools::test_the_shipped_rh5_demonstration_still_goes_red` | `score_tools._finding_ids()` | **not predicted** |
| `test_score_tools::test_the_repo_ledger_passes_its_own_audit` | `score_tools._finding_ids()` | **not predicted** |
| `test_score_tools::test_the_repo_ledger_passes_its_own_audit_with_rh6` | `score_tools._finding_ids()` | **not predicted** |

`7 − 2 + 6 = 11`.

### A different failure with the same name is not the same red — and it happened TWICE

**`test_ticket_retirement::test_repository_canonical_delivered_plan_has_matching_close_receipts`**
returns to red, and **the cause is different**. It was resolved by `CA-10` as a
receipt contradiction. It is now `missing ticket plan`, because the plan it
validates lived inside the directory the close deletes. **This is not the old red
coming back.** Nothing about receipts regressed; the subject was removed from
under a test that hard-codes its live address.

**`test_goal_baseline_is_a_card::test_a_real_epic_plans_judged_baseline_cannot_be_re_opened`
is the second instance, and it was not predicted at all.** Its red is counted in
PR #272 as the standing epic-kickoff red `CA-00-DF-02` — a demonstration that a
judged baseline cites a directory holding zero cards. Post-close it never reaches
that assertion: it dies at `LIVE_PLAN.read_text()` with `FileNotFoundError` on
`specs/desired_program_model/ticket_plan.yaml`. **The declared demonstration is no
longer being demonstrated.** The name is red, the count is unchanged, and the
thing the red was evidence for is no longer under test.

### Passes: 1497 → 1458 is **−39**, and it is three movements

| movement | n | numerator or denominator |
|---|---:|---|
| green nodes deleted with their subjects | **−11** | **denominator** |
| green tests that now skip | **−22** | **denominator** (still collected, no longer executed) |
| green tests that went red | **−6** | **numerator** |

`−11 − 22 − 6 = −39`. **Exact.**

### Collection: 1504 → 1491 is **−13**, all denominator

Eight `test_source_citations` nodes (four subjects × two tests) and five
`test_spec_yaml_valid::test_spec_yaml_parses` nodes. Two of the thirteen were red
pre-close and eleven were green; both are denominator falls, and the two red ones
are the `test_source_citations` drop above.

### Skips: 0 → 22, all denominator

| file | n | reason |
|---|---:|---|
| `test_spec_manifest_records` | 12 | `specs/{current,desired_program_model}` absent |
| `test_port_declarations` | 4 | `specs/{current,desired_program_model}` absent |
| **`test_workflow_close_keeps_the_ledger`** | **4** | **"the epic these tests use as their subject has itself been closed"** |
| `test_effect_conformance` | 1 | no promoted `spec_manifest.yaml` |
| `test_effect_conformance_cli` | 1 | no promoted `spec_manifest.yaml` |

**The four in the middle row are `CA-09`'s own tests that the close preserves the
ledger.** They skip themselves out of the run at exactly the moment their subject
becomes real. `CA-10-DF-12`.

### And three passes that are not passes

`tests/test_analyze_complexity.py` guards three repository-model tests with a
bare `if not tla.is_file(): return`. Post-close all three return immediately and
are **counted among the 1458 passes while asserting nothing**:
`test_repository_own_model_reproduces_the_recorded_state_space_bound`,
`test_cm01df02_the_repository_own_cfg_is_unchanged_by_the_fix`,
`test_repository_own_model_has_landed_the_setup_phase_collapse`. A skip is
visible in the summary line; a bare `return` is not. `CA-10-DF-14`.

## The largest unpredicted movement, attributed by measurement

Four of the six new reds are one line:
`examples/validation/scorecards/score_tools.py:2788`.

```python
def _finding_ids() -> set[str]:
    path = REPO_ROOT / "specs/desired_program_model/deferred_findings.yaml"
    if not path.exists():
        return set()
```

**It fails into confident wrongness rather than refusing.** With the ledger gone
it returns an empty set, and `audit`'s R-H3 rule then reports every `filed_as`
citation in the whole scorecard record as fabricated. The probe in
`probe_score_tools.py` (output in `score-tools-attribution-probe.txt`) imports the
module against this tree and swaps only that function:

| `_finding_ids()` | violations | exit |
|---|---:|---:|
| as the suite runs it (live ledger absent) | **14** | 1 |
| resolved to the archived ledger (278 ids) | **0** | 0 |

**The close is the entire cause, and the audit was clean before it.** `CA-09` gave
`scripts/disposition.py` a read fallback; `score_tools.py` reads the same ledger
at the same hard-coded address and has none. `CA-10-DF-11`.

The same probe refutes a declaration in the record: two of those tests carry
`**DELIBERATELY RED (RM-06, group 2)**` docstrings describing one standing R-H1
violation. With the ledger visible the audit reports **zero** violations and exits
0 — the tests were green, and the "deliberately red" declaration is stale.
`CA-10-DF-15`.

## What was repaired, and what was deliberately not

**Repaired — one class, in one file.** `tests/test_disposition_requirement.py`
now resolves through `D.resolve_ledger` exactly as `scripts/disposition.py` does.
`CA-10-DF-06`'s stated one-line fix was **incomplete**: the module reads the live
path **twice**, and applying only the fixture line left
`test_the_real_ledger_has_no_duplicate_keys` failing instead of erroring. Both
reads now go through one `ledger_path()` helper. `15 passed`. `CA-10-DF-08`.

**Not repaired, deliberately.** `test_ticket_retirement`, `test_port_case_generation`
and the four `test_score_tools` reds are reds this pass did not cause, and
`CA-10-DF-06` records that whether a closed repository's tests should validate the
ARCHIVED artifacts is the owner's question. Repairing them would also have voided
the figure above. They are filed, not fixed.

## What could not be attributed

**Nothing.** Every red is named with its cause, every collected node lost is
listed, every skip is listed with its reason, and the three arithmetic identities
close exactly: `7 − 2 + 6 = 11`, `−11 − 22 − 6 = −39`, `1504 − 13 = 1491`.
