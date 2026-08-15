# `GOAL-tree-stabilizes` — baseline

**Tree: `436c78c55c60c3ee45901223176124df5e38b6ff`, on `epic/stabilize-substrate`
with the epic workflow scaffolded and the ledger relocated** — that is, the tree
every ticket agent will actually stand in.

**Every ticket compares against the four numbers in §1, not against issue #271's
figure and not against a recollection.**

**Sealed evidence in this directory and in `../kickoff/`:**

- `collection-436c78c.txt` — `--collect-only`
- `../kickoff/pytest-baseline-436c78c.txt` — the clean run
- `../kickoff/pytest-CONTAMINATED-scaffold-landed-mid-run.txt` — see §4

---

## 1. The four numbers, and they sum

```
$ uv run --with pytest --with pyyaml -m pytest tests -q
17 failed, 1483 passed, 4 skipped in 1527.65s (0:25:27)

$ uv run --with pytest --with pyyaml -m pytest tests -q --collect-only
1504 tests collected
```

| | failed | passed | skipped | collected |
|---|---:|---:|---:|---:|
| **epic base, this branch** | **17** | **1483** | **4** | **1504** |

`17 + 1483 + 4 = 1504` ✓

## 2. Issue #271's baseline is a different tree, and the difference is the whole point

#271 states `7 failed / 1462 passed / 22 skipped at collection 1491`. **That is
the CLOSED-workflow state, which no ticket agent will ever be standing in.**
Scaffolding the successor workflow — `specs/current` and
`specs/desired_program_model` — changes it before any ticket starts.

| | #271 (closed state) | epic base (scaffolded) | movement |
|---|---:|---:|---|
| collected | 1491 | **1504** | **+13 DENOMINATOR** |
| skipped | 22 | **4** | **−18** |
| passed | 1462 | **1483** | **+21** |
| failed | 7 | **17** | **+10 NUMERATOR** |

**Every unit of it is attributed below. None of it is a repair and none of it is
a regression.**

### 2.1 The "13 uncollected nodes" were not a defect. They were the closed state.

**+13 collected, exactly.** The nodes were uncollected because the workflow close
deleted `specs/current` and `specs/desired_program_model`. **Scaffolding this
epic's workflow restored all 13 and collection returned to 1504 — the pre-close
figure.**

**So `SS-06` does not have 13 uncollected nodes to chase.** Clause (d) is
satisfied at the base by explanation, and the explanation is *the workflow was
closed*. **`SS-06` verifies this and does not re-derive a problem that is
already gone.**

### 2.2 Eighteen of the 22 skips were the same thing. Four survive, and they are one finding.

The predecessor's 22, from `CA-10-post-close/skip-reasons.txt`, are all one
shape — *"`specs/current` is absent"*, *"`specs/desired_program_model` is
absent"*, *"no promoted `spec_manifest.yaml`"*:

| file | skips | at the epic base |
|---|---:|---|
| `test_spec_manifest_records.py:52` | 12 | **run** |
| `test_port_declarations.py:79` | 4 | **run** |
| `test_effect_conformance*.py` | 2 | **run** |
| **`test_workflow_close_keeps_the_ledger.py:92`** | **4** | **STILL SKIPPED** |

**The four survivors are `CA-10-DF-12`** — *"`CA-09`'s own proof that the close
preserves the ledger skips itself out on a closed repository."* Their guard reads
`specs/desired_program_model/deferred_findings.yaml … is absent`, and this epic's
ledger is at `specs/deferred_findings.yaml`. **They unskip when `SS-01`
repoints.** Verified by targeted run: `145 passed, 4 skipped`, all four from that
one line.

**So clause (c) has a population of four, not 22, and all four belong to
`SS-01`.**

### 2.3 The ten new reds, each attributed

| red | cause | owner |
|---|---|---|
| `test_disposition_requirement` × **5** (`…ledger_loads_and_is_not_empty`, `…every_row_carries_a_disposition_field`, `…the_ticket_that_shipped_the_rule_obeys_it`, `…self_routing_passes_d3…`, `…no_duplicate_keys`) | **`SS-00-DF-01`.** `assert 88 > 200` — the ledger resolved to the **88-id `SM-05` mid-ticket snapshot** instead of the 297-row live one, because the archive fallback sorts by filesystem mtime and a fresh worktree has none | `SS-01` |
| `test_card_has_one_home::test_only_the_card_states_a_dimension_an_anchor_or_a_scoring_rule` | **the third carved exception, demanded live.** `tests/test_card_has_one_home.py:126` hard-codes `"specs/desired_program_model/deferred_findings.yaml"` in `GUARDED`; the ledger moved and its rows quote card anchors, so ten lines are now unguarded. **This is #271 §7.1's prediction firing** — *"the next path will need a third"* | `SS-01`, and the answer is **not** a third exception |
| `test_source_citations[specs/current/spec_manifest.yaml]` | the scaffold created a manifest whose citations do not all resolve | `SS-06` |
| `test_source_citations[specs/desired_program_model/spec_manifest.yaml]` | same | `SS-06` |
| `test_goal_baseline_is_a_card::…cannot_be_re_opened` | **its `R1` subject moved out from under it.** `KeyError: 'GOAL-loop-reaches-the-program'` — the demonstration reads the **live** plan, and the live plan is now this epic's. Its own docstring gives the remedy: *"Move the demonstration to another failing goal and say which; do not delete it"* | `SS-03` |
| `test_ticket_retirement::…matching_close_receipts` | **expected and self-clearing.** *"ticket `SS-01` is not closed: status=planned"* — eight planned tickets. Goes green as they close. **Not a defect** | none |

**And this is the charter's own rule in action: a red that appears after fixing a
metric is not automatically a regression.** Five of these ten are the substrate
reporting truthfully about a real defect (`SS-00-DF-01`) for the first time in
this checkout; one is a prediction from the work order firing on schedule; one is
a test whose subject legitimately moved; one is bookkeeping that clears itself.

### 2.4 The seven inherited reds

`test_architecture_tags::test_the_same_tag_control_holds` (**deliberate**,
`RM-06-DF-01`), `test_instrument_demonstrations` × 2 (**declared**,
`CA-04-DF-04`), `test_score_tools` × 3 (**`SS-00-DF-01`** — `CA-10` repaired
these and they are red again here, which is the finding), and
`test_source_citations[specs/program_model/spec_manifest.yaml]`.

**Do not repair the deliberate reds silently.**

## 3. The three vacuous passes are still there, and they are the real work

`CA-10-DF-14`. **Unlike a skip they are invisible**, and a test that cannot fail
is not a pass. They are untouched by anything above.

**The method that finds them is on the record and nobody has institutionalized
it:** `CA-07-DF-05` was found by **deleting code to see whether anything went
red**, and established that *nothing in the suite would ever have gone red, in
either direction*. It was one of the three genuine shipped-code bugs the last
epic caught. **`SS-06` uses it.**

## 4. A contaminated run is preserved beside the clean one, deliberately

`../kickoff/pytest-CONTAMINATED-scaffold-landed-mid-run.txt` records
`14 failed / 1471 passed / 6 skipped`, collection 1491.

**It is contaminated and it is kept.** The run began at 14:00 and collected 1491;
`specs/current` appeared at **14:03** and `specs/desired_program_model` was still
being written at **14:23**, so the run collected the closed tree and executed
against the scaffolded one. **The owner edited files a running measurement reads
— the exact rule the charter states in §8, committed by the person who wrote
it.**

**It is not deleted, because deleting it would remove the record of what was
actually measured.** No figure in this baseline comes from it.

## 5. What this goal is not

**There is no target on the red count.** A threshold on reds is precisely the
incentive that produced a converged count over an unconverged tree last epic.
**Reds may rise** — when a vacuous pass becomes a real failing test, that is
`SS-06` succeeding.

**Report four numbers that sum, every time, and attribute every movement.**
