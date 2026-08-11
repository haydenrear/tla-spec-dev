# CL-03 — the loop closed once, end to end, and the point moved

**`GOAL-loop-closes-once`, harnessed. Decided by `CL-04`.**

---

## 1. The one sentence

**A regression two blind judges found by hand became a card iteration, and the
card iteration moved the score on a byte-identical artifact: `D3` went `4, 4` to
`3, 3` across the version boundary, with the same judge model and the same
architecture tag on both sides — and both version 5 judges quote the new caveat
as their reason.**

The programme is named for that loop. This is the first time it has been run end
to end.

---

## 2. Is the `FileJournal` hole real? YES, and it was reproduced four ways

The ticket says plainly: **if it is not real, say so.** It is real, and it is
demonstrable in one command.

`examples/validation/ab/reference_ports/domain.py:39-52` declares the port's
whole job as durability — *"a record that outlives the run"*. The only observer
of that record anywhere in the fixture is `ReservationBook.ledger_lines()`
(`domain.py:125`), which reads it back **through the adapter that wrote it**.
`examples/validation/ab/tests/test_behavior.py` never opens the ledger path.

So a `FileJournal` that keeps the lines on the instance and never touches the
filesystem passes **28/28 through the real wiring and 28/28 through the fake**.

| who | what they did | result |
|---|---|---|
| **CL-03 (operator)** | replaced `FileJournal`'s writes with a list in a scratch copy | 28 passed real, 28 passed fake, 28 passed unmutated control |
| **v5 judge, pass 1** | *"M1 — `FileJournal` gutted to an in-memory list, zero filesystem contact"* | 28/28 real; `--basetemp` shows **28 `ledger.txt` files at baseline against 0 under M1** |
| **v5 judge, pass 2** | rewrote the class to keep lines in a list, same three methods | 28/28 both wirings; *"a direct probe confirmed the ledger path does not exist on disk after a successful commit"* |
| **v4 judge, pass 1** | did not mutate it, and named it anyway | *"the only behavior separating the real adapter from the fake is durability past the object's lifetime, and no case asserts it"* |

**It was already filed** — `RM-05-DF-05`, by the round that was measuring the
record rather than producing it. What had never happened is the next step. **The
loop's missing link was not detection and was not filing. It was that nothing
consumed a filed finding.**

### The stronger thing the round found, and it is about the anchor

The version 4 judge that saw the hole and did **not** deduct explains why, and
this is the most valuable sentence the round produced:

> **"A D3 of 3, nearly given. … I rejected the deduction because the finding is
> worse than a deduction: rung 4 is unsatisfiable by any suite that does assert
> durability, since such a case must fail the fake. The anchor structurally
> rewards blindness to the property that makes the real adapter real."**

`D3` anchor 4 asks for *"the same cases passing against both."* A case that
asserts the real adapter wrote a file **must fail against the fake**. So the
anchor's own text excludes exactly the property that distinguishes a real adapter
from a fake — and a fixture is rewarded for not testing it. Filed as
`CL-03-DF-02`. **It is an anchor defect, and CL-03 does not touch the anchor.**

---

## 3. The loop, closed once — the four steps and their evidence

### Step 1 — REGRESSION (already found, already filed, never consumed)

`RM-05-DF-05`, found independently by `portable-substrate-rm04-GG/…-p1`
(`claude-opus-4`, seeded `JF-4`) and by `portable-substrate/RM-03-rescore/v4/…-T-p1`
(`claude-opus-5[1m]`), one ticket apart, neither of them looking for it.

### Step 2 — CARD ITERATION (version 4 → version 5)

**Two edits to `references/eval_scorecard.md` and none to any Python**, which is
what the change rule says a bump is. `score_tools.py` read version 5 out of the
`### Version history` table. **This is CL-01's change rule used as a stranger
would use it, and it worked** — see §6.

The change is **a caveat, not an anchor**, because an anchor is permanent under
the change rule and rewording rung 4 would make 83 sealed cards incomparable over
a defect in one fixture.

```
  **Import topology is not modularity, and two fakes are not a pair.** Coupling
  survives every import check, so D3 of 3 or more needs evidence about what
  *calls* what at runtime, not what imports what. And anchor 4 holds when the
  real adapter does nothing real: if the only observer of the effect the port
  exists for is the adapter that wrote it, say so and take 3.
```

**Version 5 is the first row in the card's history whose SERVED digest moves
while its ANCHORS digest does not** — `sha256:f73b4d82638f09df` both sides,
`sha256:a213a36770ccab09 → sha256:2d7d4a0506d9b259`. That is precisely the class
of change that was **invisible** before CL-01 shipped the second seal. **The
seal moved. CL-01's mechanism is exercised, not asserted.**

### Step 3 — ARCHITECTURAL DELTA (measured, on a byte-identical artifact)

One artifact — `examples/validation/ab/reference_ports`, the subject declared as
`toolchain_fixture` in `subjects.toml` with architecture tag
`ports-and-adapters` — scored **four times** with fresh judges: twice under
version 4 from the frozen `rubric_v4_frozen.md`, twice under version 5. Same
artifact bytes, same judge model on all four cards, same architecture tag, same
dispatch text. `R-H1` and `R-H2` hold by construction: **the instrument axis is
the only thing that moves.**

| card | version | served digest | D2 | **D3** | ran own faults |
|---|---|---|---|---|---|
| `20260811-cl03v4-CL-p1` | 4 | `a213a36770ccab09` | 2 | **4** | yes |
| `20260811-cl03v4-CL-p2` | 4 | `a213a36770ccab09` | 2 | **4** | yes |
| `20260811-cl03v5-CL-p1` | 5 | `2d7d4a0506d9b259` | 2 | **3** | yes |
| `20260811-cl03v5-CL-p2` | 5 | `2d7d4a0506d9b259` | 0 | **3** | yes |

**`D3` delta: −1, on both judges, unanimous either side.** Both version 5
judges cite the caveat by its own words:

> **v5 p1:** *"WHY NOT 4. The caveat: 'if the only observer of the effect the
> port exists for is the adapter that wrote it, say so and take 3.' The port
> exists for durability. The only reader of the file is `journal_file.py:36`,
> the same class that wrote it at `:32`."*

> **v5 p2:** *"D3 = 4, which I had already written down. … Everything anchor 4
> asks for is visibly present and the caveat's condition is undetectable by
> reading — the file genuinely calls `write_text` and `open`. Only deleting the
> durability and re-running answered it."*

### Step 4 — RE-SCORE, sealed

All four cards pass `check` with **0 problems** and are sealed into
`INSTRUMENT-LOG.toml`. `check` reports **SERVED-DRIFT** on the two version 4
cards — *"the bar this judge read is not the bar in the tree"* — which is the
seal doing its job across the boundary, not a defect.

`D2` in the version 5 group is **CONTESTED, spread 2** (`2` against `0`), and it
is recorded rather than adjudicated: both judges wrote the same defect and differ
only on where D2's ladder puts it. `[[contested]] cl03-v5-d2-spread-2`,
`third_pass = "none"`, with the reason. See `CL-03-DF-02(b)`.

---

## 4. The predictions, scored — and P3 is FALSIFIED

Sealed at `2026-08-11T18:42:43Z` in commit `a73186d`, **before any judge agent
was launched** and while all four cards were unfilled skeletons.

| | prediction | outcome |
|---|---|---|
| **P1** | at least one v4 judge awards D3 = 4 | **HELD** — both did |
| **P2** | at least one v5 card names the single-observer fact | **HELD** — both did, quoting the caveat |
| **P3** | **at least one v5 judge still awards 4** | **FALSIFIED** — `3, 3` |
| **P4** | `executed_own_faults` predicts the finding better than the card version | **FALSIFIED, and it is the result** — see below |
| **P5** | served surface does not grow | held (measured at sealing) |
| **P6** | `check` over the record reports the same 330 problems | held — still 330 at tree 3, over 87 cards |
| **P7** | re-keying tier on the model id removes ≥1 split and creates no contradicting one | **FALSIFIED as written** — it removes none and creates none |

**Two of the four real predictions are wrong, and the alarm condition declared in
advance is NOT triggered.**

**P3 was the prediction the round existed to be wrong about, and it was wrong.**
Its mechanism was correct and its conclusion was not: v5 p2 confirms the caveat's
condition *is* undetectable by reading — and then ran the mutation anyway. **A
two-sentence caveat, costing 138 bytes and no anchor, moved a dimension by a full
point on both judges. Six epics of static gates moved bug detection by zero
cells.**

**P4 is the sharper falsification.** All four judges ran their own faults, so the
practice variable is constant and cannot explain anything — and **both version 4
judges saw the durability hole and declined to deduct.** v4 p1 named it in as
many words in its rejection notes. So the observation was *already present under
version 4*, in a judge's prose, deciding nothing. **The card version, not the
judging practice, is what converted an observation into a score.** That is
`RM-05-DF-05`'s complaint — *"a finding written into a card note is a finding
nobody carries forward"* — reproduced under controlled conditions and then
closed.

---

## 5. The served surface — the metric, before and after

```
serve | wc -c    6,319  ->  6,281       (-38 bytes, -0.6%)
rungs                9  ->      9       (no anchor added, deleted or reworded)
anchors_digest   sha256:f73b4d82638f09df  ->  unchanged
served_digest    sha256:a213a36770ccab09  ->  sha256:2d7d4a0506d9b259
```

**The surface fell.** The D3 caveat costs 138 bytes. They are paid for out of
scoring rule 9, which restated the served preamble's second sentence
**verbatim** — the identical statement is served two paragraphs above it, so
nothing left the served surface that was not already on it. Both edits are in
`references/eval_scorecard.md`; the renderer is untouched, which is the test of
whether a stranger could have made this change.

The 6,319 figure is `CL-01-DF-01`'s corrected one. The number four documents
called 6,409 is 90 bytes of the command's own stderr.

---

## 6. Did CL-01's change rule work, used as a stranger would use it?

**Yes, on all four clauses, and one of them bit.**

1. **A bump needs no source edit.** Changed `**Scorecard version 4.**` to `5`
   and added a row. `score_tools.py serve` immediately reported *"card version
   5"*. `SUPPORTED_VERSIONS = (1, 2, 3, 4)` is still a literal in the tool and
   was not touched.
2. **`--card-version` alone is not enough, and the rule says so.** The version 4
   arm was scaffolded with `--rubric examples/validation/scorecards/rubric_v4_frozen.md
   --card-version 4` after freezing the file, exactly as the rule instructs, and
   it reproduces `served_digest sha256:a213a36770ccab09` **byte for byte**. That
   is the fourth round to do it by operator sequencing, which is
   `FI-06-DF-11(c)` still open and now four of four.
3. **The seal moved.** A caveat-only change moved `served_digest` and left
   `anchors_digest` byte-identical — the exact case CL-01 built the second seal
   for, now demonstrated on a real bump rather than a constructed one.
4. **AND IT BIT.** Four of CL-01's own tests went **red on a correct bump**,
   because they use the literal `5` as the version *"our card declares no version
   5"* and pin `row[4]` and the D3 caveat's exact prose. **A demonstrated failing
   input that names a version by number expires the moment the card legitimately
   reaches that number.** Repaired by making every one of them relative to what
   the file declares — `declared_version`, `bumped_to_next`, `caveat_in_file` —
   which is strictly stronger than the literals they replace. Filed as
   `CL-03-DF-04`. **Nothing was weakened: every assertion is kept and three are
   now version-independent.**

---

## 7. The version-4 era boundary, declared three epics late

`R-H1`'s instrument axis is computed from `[[change]]` rows and from nothing
else. **The version 4 bump — the first in the card's history whose anchors digest
moved — was never declared.** `RM-05-DF-03`.

Two rows are added: `RM-03-scorecard-v4` (commit `1e6f691`) and
`CL-03-scorecard-v5` (commit `a73186d`).

**Measured consequence, and it is the point of the row:**

```
audit, WITHOUT the era boundaries:   0 violation(s)
audit, WITH them:                   10 violation(s)
audit, after the ten are PARKED:     0 violation(s)
```

**All ten are `SUPERSEDED-UNMARKED`** — claims still marked `current`, measured
before a bar that existed and was undeclared, that nothing re-affirmed. `R-H1`
reported a clean for three epics **because the boundary it polices had never been
declared**. Four rounds' claims, two of them goal decisions.

**How they are disposed of, and why that is not a repair.** The rule offers
three dispositions: re-affirm, mark superseded, or move to `under_review` with a
filed finding. **Only the third is available to a ticket that is not the claim's
own round** — re-affirming somebody else's number during a measurement is what
`measurement_rule` forbids, and `superseded` asserts a replacement nobody
measured. So all ten are `under_review` against `CL-03-DF-04`, and **the
statement, the figure and the `why` of every one of them are byte-identical to
what their round wrote.** What changed is that the record now says they sit
across a declared bar. That is strictly more information than `current` was.

**This was not free.** Declaring the boundary turned `score_tools`'s own
`test_the_repo_ledger_passes_its_own_audit` red until the ten were parked, which
is the rule finally reaching the thing it was written for.

What is now readable and was not: **D3's served block is byte-identical across
the version 3 / version 4 boundary and D2's is not.** *"D3 replicated and D2 did
not"* compares a dimension whose bar held still against one whose bar moved in
the ticket before.

---

## 8. Tier keyed on the full model id — and the confound is not where it looked

`RM-04` found four judge models under two labels. `derived_tier` substring-matches,
so `claude-opus-5[1m]`/`claude-opus-4` are both `opus` and
`claude-sonnet-5`/`claude-sonnet-4-5` are both `sonnet`.

`tier_split_of` and the `index` comparison column are now keyed on
`judge_model_key` — **the full model id** — with the family word carried beside
it and still policed against a declared `tier`. The demonstrated failing input is
in `tests/test_score_tools.py`: four cards, one artifact, `claude-opus-5[1m]` at
`1, 1` against `claude-opus-4` at `3, 3`. Under the family key that group has
**one** tier, `len(by_tier) < 2`, and the splitter returns **nothing** — a
two-point disjoint separation the record could not report.

**And the measured result on the real record is that it changes no split at all.**

```
judge groups                     35
family collisions                 0    (no group carries two models of one family)
split dimensions, family key     18
split dimensions, model-id key   18    (identical)
```

**So the confound is ACROSS rounds, not within a group.** Every group is exactly
one `opus` model and one `sonnet` model; what was wrong was that a reader could
add `reading-discipline`'s `opus` (= `claude-opus-5[1m]`) to `RM-04`'s `opus`
(= `claude-opus-4`) and call it one program. The record shows why that matters:
on D3, `claude-opus-4` is **lower** than `claude-sonnet-4-5` on subject `GG`
(2 vs 4) and **higher** on `JJ` and `LL` (1 vs 0). **The direction of the "tier"
effect is not constant across the models wearing the label.**

`P7` predicted a removal and got none. **The fix is to print the id, not to
re-partition**, and saying so is worth more than the repair.

**Still broken, not touched:** `architecture_tags.py:274` derives a *second*
tier inline — two tiers and `?`, with `tiers_measured` hardcoded to
`(opus, sonnet)` — in a module `score_tools.py` already imports. The two
derivations had already diverged before this ticket; keying one of them on the
model id makes the divergence **wider**. `CL-03-DF-05`.

---

## 9. Suite numbers, with their trees — and a retraction

**A NUMBER IS RETRACTED BEFORE IT IS QUOTED.** CL-03 and CL-02 were handed the
**identical scratchpad path** and both redirected a full suite run into
`baseline.txt` (`CL-02-DF-03`), so that file may be two runs spliced into one
plausible transcript. **CL-03 never reported a figure from it and does not now.**
Everything below was re-measured after the collision was known, into paths
carrying this ticket's id, and **every number names the tree it came from.**

**No `git archive` figure appears here.** These tests read git history and an
archive has no `.git`.

| tree | commit | working state | result |
|---|---|---|---|
| `wt-epic-close-the-loop` | `0368e6f` | clean checkout, **epic tip after CL-02 merged** | **2 failed, 1488 passed** |
| `wt-epic-close-the-loop-CL-03` | `e3750d1` | this ticket, reconciled onto that tip | **2 failed, 1496 passed** |

**The two failures are the same two at both ends, and they are the inherited
deliberate ones:** `tests/test_architecture_tags.py::test_the_same_tag_control_holds`
(`RM-06-DF-01`) and `tests/test_price_removal.py::test_nothing_in_the_repository_invokes_the_pricer`,
which at this tip names **two** narrative documents because
`CLOSE-THE-LOOP-EPIC.md` trips it as well. **Neither was repaired.**

**`denominator_rule`, measured rather than asserted.** Collected went 1,490 →
1,498, and the arithmetic is stated: **+9 tests written, −1 parametrise case**
(D2 left `test_the_tag_cannot_refuse_a_comparison_on_a_dimension_it_did_not_move`
and moved to a test of its own that asserts more). The numerator rose by 8 and
**nothing was deleted, skipped or weakened.** Every assertion CL-01 shipped is
still asserted, and four of them are now derived from what the card declares
rather than from a literal — strictly stronger (§6, `CL-03-DF-04`).

**The first tip run came back 12 failed and ten of those were mine.** None was
noise; each is worked through in §9.1. Reporting the clean figure without that
sentence would be the thing this project keeps filing findings about.

### 9.1 The ten, and what each one was

| # | red | what it actually was |
|---|---|---|
| 2 | `test_the_repo_ledger_passes_its_own_audit` (+ its R-H6 twin) | **the era boundary firing.** `audit` 0 → 10 violations. Ten claims **parked** `under_review` against `CL-03-DF-04`, figures byte-identical; back to 0 |
| 1 | `test_the_committed_history_rendering_is_current` | the committed `HISTORY-*.md` renderings went stale against the new ledger; regenerated with `history --write` |
| 1 | `test_only_the_card_states_a_dimension_an_anchor_or_a_scoring_rule` | `rubric_v4_frozen.md` is a second copy of the card. It earns its `GUARDED` entry the way v3 does — with a **running** comparison of **both** digests |
| 1 | `test_a_scaffolded_scope_is_declared_before_scoring_and_a_moved_one_is_refused` | **a real defect: `check(card, where)` with no rubric fell back to the literal tuple**, so the first legitimate bump made it refuse a card at the version the card file declares. `check` now reads the card file. `CL-03-DF-04(b)` one level down |
| 1 | `test_every_fast_demonstration_reproduces` | `scorecard-contested` pinned `8 contested dimension(s)`; this round makes nine. Updated with the arithmetic stated |
| 1 | `test_the_claim_that_justified_an_epic_is_refused` | the counterexample floor moved 19 → 20 for the **fourth consecutive round** — `RM-06-DF-02`'s open-population shape on schedule. Verdict unchanged and unchangeable |
| **2** | `test_authority_is_keyed_on_dimension_and_value_pair`, `…did_not_move[D2]` | **`CL-03-DF-06`, escalated.** Four honest cards gave the architecture tag refusal authority on **D2** — a confound, not an architecture effect. Handled as `RM-06` handled RD-03 retiring its `["opus"]` bound: **rewrite the claim, do not restore the number** |
| 1 | `test_the_index_judge_column_is_the_model_id` | **mine, and it edited the sealed record.** `index` WRITES `INDEX.md` into the directory it is pointed at; the test now runs against a `tmp_path` copy and the stray file is removed |

### The instrument's own counts, at tree 3

```
score_tools.py check specs/results/scorecards   87 cards, 87 filled, 330 problems
score_tools.py audit                            10 violations  (0 before the era rows)
score_tools.py contested --root ...             9 contested dimensions over 35 groups,
                                                0 unrecorded, 18 tier-split dimensions
serve | wc -c                                   6,281   (9 rungs)
```

**330 is the same figure CL-01 reported over 83 cards; the card count rose to 87
because CL-03 added four and no sealed card was edited.** `0 unrecorded` is new:
CL-03's own contested spread is the first one recorded in the same round that
produced it.

## 10. What CL-03 REJECTED

- **Manufacturing a regression.** Not needed: the candidate was real and
  reproduced four independent ways. Had it not been, §2 would say so and that
  would have been the result.
- **Repairing the `FileJournal` hole.** The one-line repair is obvious — give the
  fixture one observer that does not go through the adapter. Filing it, carrying
  it into a card iteration and measuring the delta are different acts from
  repairing the code, and **repairing it would have destroyed the subject the
  delta is measured on.** Not done, deliberately.
- **Rewording D3's anchor 4.** It carries the regression better than any caveat
  would. It is also permanent under the change rule, and 83 sealed cards are read
  against it. **An anchor is a thing you cannot take back; a caveat costs
  nothing.** Rejected in favour of the cheapest carrier that works.
- **Adding a tenth rung.** Considered for exactly as long as it took to notice
  that a new anchor can never be removed.
- **Growing the served surface and reporting it honestly.** Available and
  refused. The budget is the constraint the epic set, and paying for the caveat
  out of a verbatim duplication is a real payment rather than an accounting one.
- **Repairing the ten `SUPERSEDED-UNMARKED` claims.** They belong to four other
  rounds and re-affirming somebody else's number during a measurement is the
  move the rule forbids. Filed.
- **Repairing `test_nothing_in_the_repository_invokes_the_pricer`.** This
  document mentions `price_removal`. Inherited red, left red.
- **Adjudicating D2's contested spread with a third pass.** A third pass produces
  a third number and does not decide the ladder both judges independently named.
- **Blinding the judges to the artifact's own prose.** Both v4 judges disclosed
  that `reference_ports/README.md:20-24` and `journal_memory.py:7-27` quote
  `BA-B14` **including the phrase "the fake that earned arm B its `D3 = 4`"** —
  so the packet hands a judge a prior D3 number before it forms its own.
  Redacting it would have changed the artifact. Recorded as a leak instead:
  `HARVEST-CL-03.md` §F3. **It cuts against the result** (it primes toward 4,
  and the v5 judges went to 3), which is why it is reported and not corrected.

---

## 11. The sweep: what the judges' notes actually contained

**`HARVEST-CL-03.md`** is the register. 83 cards, 391 rationales, 389
`refuses_to_claim`, 52 `what_was_run`, 800,181 characters, read in full by four
independent agents given no hypothesis.

The headline is not any single defect. It is that **the same defects were
rediscovered independently up to six times each, across different epics, judge
models and card versions, and approximately one of them ever became a finding.**
A red positive control read as a measurement: 6 passes. A `:fake` column that
re-runs the real implementation: 5. A D3 ladder with no rung for the subject: 5.
A 400-step "independent model" sweep that accepts 5 of 400 with its own
anti-vacuity guard passing: 4. The shared 28-case contract green on real bugs:
**every card of an entire epic.**

**That is what a detection channel looks like when nothing downstream consumes
it — and it is the same shape as the finding this ticket carried through the
loop.**

---

## 12. Reconciliation with CL-02, the promotion predecessor

CL-02 merged while this ticket was running. **The epic tip is `0368e6f`,
verified with `git rev-parse` and not taken on trust** — the owner first passed
`f4c8bde`, which does not resolve in this repository, and CL-03 checked before
acting rather than after. That is the failure mode that has put tickets 4, 14 and
21 commits adrift here, and the rule is the same whoever hands you the number.

`0368e6f` is merged into `feature/CL-03` at `b1068fb`. **One conflict, in
`specs/desired_program_model/deferred_findings.yaml`, and it was a pure
append/append**: both tickets added findings at the end of the same list.
Resolved by keeping **both** appends in full — `CL-03-DF-01…05` then
`CL-02-DF-01…03` — verified by re-parsing the file (172 findings) rather than by
reading the diff. **No finding of either ticket was dropped or reworded.**
Nothing else conflicted: CL-02's surface was `examples/validation/gap_mutants/`
and CL-03's was `examples/validation/scorecards/`, `references/` and
`specs/results/`.

**The served surface is unchanged by the merge: 6,281 bytes, 9 rungs.**

**CL-03 makes no cost claim anywhere, and could not.** CL-02's sweep returned
`priced rows: []` with `0 of 10` historical removals disagreeing and `RM-01-RF-1`
still the only price this project has. **The card iteration in §3 is priced by
nothing and is not presented as priced** — its evidence is a re-score under two
card versions on one artifact, which is a different instrument from the pricer
and makes no claim the pricer would have to support.

CL-02's second result cuts the same way as this one from another direction:
`gap-mutant-catalogue-and-runner` now reads **`EXTINCT`** rather than
`ENTAILED-SURVIVES`, which is RM-05's withdrawal of that headline confirmed
independently.
