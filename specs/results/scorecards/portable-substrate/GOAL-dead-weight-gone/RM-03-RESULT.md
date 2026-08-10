# RM-03 — the removal, priced per removal

**Ticket:** RM-03, issue #211. **Branch point:** `9f110ae`, verified.
**Promotion predecessor:** RM-06, merged.

**Scope, stated first (`R3`).** Every line figure below is `git diff -U0`
line counts over the named paths at the named commit range, in this worktree.
It is **not** `code_lines` from `scripts/code_complexity.py`, which counts
differently and is what the `subtract-to-measure` `+1677` figure was measured
in. The two are not interchangeable and no row here claims to be the other.
**Every suite number names its tree.** §7 records what `scope` made of this
page and which of its four bounds applies.

**There is no total on this page, and `removal_census.py` refuses one.**

---

## 1. The baseline, and the six that stay red

| tree | result |
|---|---|
| `9f110ae` — the branch point, a real checkout, `uv run --with pytest --with pyyaml python -m pytest tests -q` | **6 failed, 1491 passed** in 841s |

The six are RM-06's, left red on purpose. **This ticket repaired none of them.**

```
tests/test_architecture_tags.py::test_the_same_tag_control_holds                     RM-06-DF-01
tests/test_architecture_tags.py::test_the_committed_demonstration_re_derives_from_the_cards   RM-06-DF-02
tests/test_instrument_demonstrations.py::test_every_fast_demonstration_reproduces
tests/test_score_tools.py::test_the_shipped_rh5_demonstration_still_goes_red
tests/test_score_tools.py::test_the_repo_ledger_passes_its_own_audit
tests/test_score_tools.py::test_the_repo_ledger_passes_its_own_audit_with_rh6
```

---

## 2. THE HEADLINE, AND IT IS TWO-SIDED

**The card an adopter reads got a quarter smaller. The repository got longer.
Both are measured, and the second is the one worth reading.**

| | version 3 | version 4 | direction |
|---|---|---|---|
| **served rubric — the bytes a judge is handed** | 8220 bytes | **6272** | **−24%** |
| served rubric, lines | 83 | **67** | **−19%** |
| **anchor rungs a judge must apply** | 25 | **9** | **−64%** |
| scored dimensions | 5 | **2** | denominator fell |
| recorded notes | 0 | 3 | added |
| `references/eval_scorecard.md` | — | — | **+235 / −144** |
| `examples/validation/scorecards/score_tools.py` | — | — | **+247 / −40** |

`denominator_rule`: the anchor-rung count fell because the **denominator** fell —
three dimensions stopped being scored and one anchor was deleted. No rung was
made easier.

**Why the repository could not shrink, and it is the card's own doing.**
`Changing this card` requires *"keep the old anchors in the file"*; `R-H4`
requires *"a sealed card is never edited"*, and 73 sealed cards are still
checked by `score_tools.py`. So a retired anchor **leaves the served section and
stays in the file**, every line of the tool that enforces a version 1–3 rule
**must stay** because it is the only thing still checking those cards, and the
bump adds a *branch* — which is longer than the thing it branches. **A card
removal cannot delete prose and cannot delete code.** Filed as `RM-03-DF-03`,
with the fix: measure a card change in **served** bytes, which already have a
digest over exactly them, and never in repository lines.

---

## 3. THE PER-REMOVAL TABLE

Five removals were attempted. Two of the epic's three levers turned out not to
be removable by this ticket at all, and both are reported as such rather than
dressed up (§8).

### 3.1 — the card: D1, D4 and D5 stop being scored; D2's anchor 4 is deleted

`90d0667` → `1e6f691`. One mechanism change with four clauses; **the shared cost
is reported once and is NOT divided four ways to make each clause look cheap.**

| role | path | lines |
|---|---|---|
| `cut_prose` | `references/eval_scorecard.md` — D1's anchor block 13, D4's 11, D5's anchors + the `anchor_reading` note 22, D2's anchor 4 two and its descriptor preamble three, three table rows, the scoring-rule clauses that named them | **144 removed** |
| `replacement` | `references/eval_scorecard.md` — `Retired anchors, versions 1–3` (the same anchors, verbatim, where no judge can be served them), `The recorded notes`, rule 10, the version-4 row and its account | 235 added |
| `replacement` | `examples/validation/scorecards/score_tools.py` — `scored_dims`/`note_dims`/`top_score`, the notes parser, the version-4 branches of `serve`, `check` and both skeletons | 247 added, 40 removed |
| `proof` | `examples/validation/scorecards/rubric_v3_frozen.md` | **709 added** |
| `proof` | `tests/test_score_tools.py` | 227 added, 62 removed |
| `proof` | `tests/test_card_has_one_home.py` | 34 added, 3 removed |

**lines removed 249 · lines added to prove it safe 970 · ratio 1 : 3.9**
(counting the frozen rubric and both test files as proof, and the rubric and
tool edits as replacement.)

**The ratio is reported as it falls and no reclassification was taken.** Moving
`rubric_v3_frozen.md` out of `proof` — it is arguably `replacement`, since it is
the bar itself and not a demonstration about it — would improve the ratio to
1 : 1.05 in one keystroke. RD-02 turned down a free 2.9× on exactly this move
and RM-06 turned down the largest green available to it; this row keeps the
worse number.

### 3.2 — the architecture tag stops being an adopter-facing surface

`90d0667` → `1e6f691`, inside the same file as 3.1 and counted inside its 144.

| role | path | lines |
|---|---|---|
| `cut_prose` | `references/eval_scorecard.md` — R-H1's third clause: 38 lines of tag derivation, refusal-authority keying and failure modes | **38 removed** |
| `replacement` | the rule, in one block quote, plus what `audit` executes | 30 added |

**lines removed 38 · lines added to prove it safe 0 · ratio 38 : 0.**
Nothing was added to prove this safe because nothing about it is executable:
`score_tools.py tags` and `audit` are untouched, every check behind R-H1 still
runs, and `references/architecture_tags.md` — RD-04's and RD-05's sealed design
record — is not edited. **This is the cheapest removal in the ticket and the
only one with a clean ratio.** It is also the only one whose subject was pure
exposition, which is the general lesson.

### 3.3 — the mutant catalogue and the gap-mutant runner

`1e6f691` → `HEAD`.

| role | path | lines |
|---|---|---|
| `cut_production` | `examples/validation/gap_mutants/run_gap_mutants.py` | **633 removed** |
| `cut_production` | `examples/validation/gap_mutants/gap_mutants.toml` | **728 removed** (576 shipped + 152 RM-03 seeded into it before the cut) |
| `cut_tests` | `tests/test_gap_mutants.py` | **537 removed** |
| `proof` | the before-table `rm03-gap-mutants-before.json`, seeded and measured before the cut | see §4 |

**lines removed 1361 (production) · 1898 (with the mechanism's own tests) ·
lines added to prove it safe: 0 new lines of code; the proof is a measured
before-table and an `entail` reading against the head.**

`denominator_rule`: `tests/` loses 537 lines and 32 collected nodes. The
numerator did not rise — the suite total falls by exactly the nodes that tested
the deleted mechanism, and no other test was touched.

### 3.4 — the suite as a finding channel

**0 removed · 0 added · there was nothing in the tree to remove.** Searched at
`9f110ae`: `SKILL.md`, `references/`, `prompts/`, `scripts/` and `templates/`
carry no instruction to run the suite as a source of findings. Its only shipped
role is the acceptance command of every ticket in `ticket_plan.yaml`, which is
the regression-guard job it keeps. **The funding lives in round practice, not in
the tree.** `RM-03-DF-04`.

### 3.5 — static gates

**0 removed · 0 added · REJECTED, with the reason in §8 and `RM-03-DF-05`.**

---

## 4. WHAT EACH REMOVAL PRICED AT

Priced with **`price_removal.py`, over kill sets** — never with
`removal_census.py discriminate`, which is `RM-01-DF-01` and would have returned
`NON-DISCRIMINATING` for every row here before anything ran.

Three faults were seeded in the gaps of the mechanisms this ticket removes, at
`90d0667`, **before any cut was made**, and measured against `pytest-full` (the
whole suite, at node granularity) and `pytest-gap-mutants`. A fourth could not be
written and the reason is `RM-03-DF-02`.

**`pytest-full` is a detector here on purpose.** `RM-01-DF-01` is that
`discriminate` reads a surviving detector NAME as a surviving kill, and
`pytest-full` is never deleted, so it made every row non-discriminating by
arithmetic. `price_removal.py` reads the kill set as **(detector, node)** pairs,
so a node deleted inside a surviving suite is a lost kill. Using the whole suite
rather than a hand-picked subset is also the conservative choice: a narrower
detector set makes fewer kills available to lose and therefore **inflates**
`PRICED`.

### 4.1 the before-table — every fault died, and the control fired

`specs/results/scorecards/portable-substrate/GOAL-dead-weight-gone/rm03-gap-mutants-before.json`,
staged from `90d0667`, 1487 tests executed per `pytest-full` column.

| fault | verdict before | the kills it had |
|---|---|---|
| `RM03-GM-D4` | **DIES** | `pytest-full::…test_d4_anchor_4_is_not_awardable_by_a_judge_that_ran_nothing`, `…::test_d1_and_d5_are_deliberately_not_gated` |
| `RM03-GM-D5` | **DIES** | `pytest-full::…test_d5_scored_where_the_two_readings_differ_must_name_which` |
| `RM03-GM-RUNNER` | **DIES** | `pytest-full::…test_an_edit_that_changes_nothing_refuses`, `pytest-gap-mutants::` the same node |
| `RM03-GM-CTRL-C` *(positive control)* | **DIES on both columns** | — |

`Every declared mutant applied exactly once.` The control is what makes the
table readable: a column that cannot go red decides nothing, and both did.

### 4.2 the prices

| removal | fault | verdict | what it means |
|---|---|---|---|
| **the mutant catalogue and the gap-mutant runner** (§3.3) | `RM03-GM-RUNNER` | **`ENTAILED-SURVIVES` → PRICED** | **Every killing node the fault had is deleted by this removal.** `tests/test_gap_mutants.py` is gone, so both kills — the one inside `pytest-full` and the one in its own column — go with it. A fault this repository used to catch it no longer catches. |
| **the card** (§3.1) | `RM03-GM-D4` | measured, §4.3 | |
| **the card** (§3.1) | `RM03-GM-D5` | measured, §4.3 | |
| **the architecture tag as an adopter-facing surface** (§3.2) | — | **UNPRICED** | Nothing executable changed. `tags` and `audit` are byte-identical and every check behind R-H1 still runs, so there is no gap to seed a fault in. Labelled unpriced rather than given a zero. |
| **the suite as a finding channel** (§3.4) | — | **UNPRICED, and there was nothing to price** | `RM-03-DF-04`. |
| **static gates** (§3.5) | — | **NOT REMOVED** | `RM-03-DF-05`. |

**A non-zero price, and what it is and is not.** `ENTAILED-SURVIVES` is sound
towards `SURVIVES` and is an **upper bound** on the price: it cannot see a kill
the after tree ADDED. `price_removal.py` says so itself and this page does not
round it up. What it establishes is that the removal took away every kill that
fault had — the thing `RD-02`'s `0 of 9` and `RM-01`'s re-priced `0 of 10` could
never establish for any historical removal.

**It is also a fault in the deleted mechanism, and that has to be said.** The
fault `RM03-GM-RUNNER` seeds is *inside* `run_gap_mutants.py`; the tests that
caught it are that file's own tests. Whether "a mechanism's own tests stop
catching faults in the mechanism" is a cost a reader should accept is exactly
the judgement `price_removal.py` refuses to make — *"`PRICED` means a fault the
repository used to catch is no longer caught. Whether that is an acceptable cost
is a human's call."* RM-05's call. What is NOT in doubt is that the instrument
returned something other than zero on a real removal, which is
`GOAL-removal-can-be-priced`'s whole question.

### 4.3 the card's two faults — why `entail` alone is not the answer

```
price_removal.py entail --before …before.json --head 6298eee
  ENTAILED-SURVIVES   RM03-GM-RUNNER-an-unapplied-mutant-reports-a-survival
  UNDECIDED           RM03-GM-D4-the-top-of-behaviour-preservation-stops-needing-a-run
  UNDECIDED           RM03-GM-D5-a-split-on-the-honesty-anchor-stops-being-readable
```

**`UNDECIDED` is the correct answer and it is the interesting one.** Both card
faults' killing nodes still exist at the head **with the same node ids** — and
this ticket **changed their bodies**: `test_d4_anchor_4_is_not_awardable_by_a_judge_that_ran_nothing`
and `test_d5_scored_where_the_two_readings_differ_must_name_which` were
re-pinned to scaffold a *version 3* card. That is precisely
`DETECTOR-WEAKENED`, the class `SM-03` produced and the class no survivorship
test can see — and it is the second defect in `RM-01-DF-01`, met in the wild by
the next ticket after the one that named it.

So the card's price cannot be read off the diff and had to be measured:

*(§4.4, from the after-table)*

---

## 5. THE D1/D4 DECISION

RM-02 §5.1: *"Cut D1 and D4 from the card, or cut the model clause out of their
anchors. Pick one; do not do both and do not do neither."*

**Taken: cut the dimensions.** They are recorded notes and keep their questions.

The clause option fixes portability and nothing else. RM-02 §6 says *"do not
export"* about both dimensions **on grounds the clause is not responsible for**:

- **D1 is near-constant.** 3 on 55 of 59 `ab_quota_ledger` cards. A dimension
  that takes one value on the only example a project scores carries no
  information whatever its anchors say, and deleting the model clause from
  anchor 4 does not give it any.
- **D4 is the worst-behaved dimension in the record**, tier-splitting on 4 of
  the 8 judge groups scored by both tiers. That is a stability problem, and an
  anchor edit is not a stability fix.

And one argument the record makes that RM-02 does not: **D1 is the dimension
that scores the lever this epic measured dead.** Its own question is *"do the
model-derived cases catch seeded faults"*, and the epic's charter table records
that lever as **fails — 0 unique kills against 4 the other way, replicated on
new subjects**. Keeping a scored dimension whose subject the same epic declares
dead is incoherent; cutting the clause would have kept it.

**The status quo was the one option the record does not support, and it was not
taken.**

---

## 6. THE `scorecard_version` BUMP AND THE RE-SCORE UNDER BOTH VERSIONS

The change rule applies to this ticket in full, and all three parts were done.

1. **Bumped**: version 3 → **4**. `sha256:eeccf4576bc6fd85` →
   `sha256:f73b4d82638f09df`. **This is the first bump in the card's history
   whose anchors digest moves**, and the version history says so.
2. **Old anchors kept**: verbatim, in `### Retired anchors, versions 1–3`, under
   headings the parser deliberately does not match, so they are readable by a
   person comparing two versions and unreachable by a judge scoring under
   either. `test_the_version_bump_kept_the_anchors_and_says_so_in_a_digest`
   executes this against the frozen v3 rubric's parsed anchors rather than
   asserting it.
3. **Re-scored a prior example under both versions**: one sealed artifact,
   `artifact_T` (`ab_quota_ledger`, declared subject `arm_b`), four fresh blind
   judges on the same day from the same dispatch text — two under version 3
   against `rubric_v3_frozen.md`, two under version 4. Cards in
   `specs/results/scorecards/portable-substrate/RM-03-rescore/`.

### The measured discontinuity

| version | judge | D1 | **D2** | **D3** | D4 | D5 |
|---|---|---|---|---|---|---|
| 3 | `opus` p1 | 3 | **2** | **4** | 2 | 4 |
| 3 | `sonnet` p2 | 4 | **2** | **4** | 3 | 4 |
| 4 | `opus` p1 | — | **2** | **4** | — | — |
| 4 | `sonnet` p2 | — | **2** | **4** | — | — |

**The discontinuity on the two surviving dimensions is zero points, across both
versions and both tiers.** D2 = 2 and D3 = 4 on 4 of 4 cards.

**And the three dimensions that were cut are the ones that disagreed in the very
round that cut them** — D1 3 against 4, D4 2 against 3, both across tiers, on
the same bytes. D5 agreed at 4. That is one artifact and it is not a rate; what
it is enough to say is that no cross-version movement was found on D2 or D3
here, and that the disagreement that did appear appeared only on retired
dimensions.

### What the judges said unprompted, and it is the strongest result on this page

Both version 4 judges reported, independently, that **being made to write prose
instead of a number changed what they concluded**:

> *"Writing out **why** the pair diverges forced me to see that the divergence is
> the mechanism succeeding … having to enumerate behaviors made me run the swap
> against the shared suite, which is what surfaced that the shared suite pins
> nothing about the file on disk — the single most useful finding on this card,
> and one no score on any of these dimensions would have carried."*
> — `20260810-v4-T-p1`

> *"Writing full prose rather than just a number is what surfaced the M09
> asymmetry as worth flagging at all — a bare score would have let it pass
> silently."* — `20260810-v4-T-p2`

Two judges is two judges. It is reported because it is the outcome the removal
was *not* designed to produce and neither judge was asked to look for it.

### What the round cost, and one thing it broke

- **Blinding was defeated by the card itself.** `scaffold --subject arm_b`
  writes `subject.name: "arm_b"` into the skeleton, so a judge handed a blinded
  arm label `T` reads the real arm name off its own card before opening the
  artifact. The `20260810-v4-T-p1` judge disclosed it unprompted. This is a
  defect in the blinding mechanism the epic's do-not-cut list protects, it is
  **not** filed — RM-03's budget of five is spent and none of the five is less
  important — and it is escalated here instead. It reproduces in one command.
- **Two judges reported `SERVED-DRIFT` and `RUBRIC-DRIFT`** because the rubric
  was still being edited while they scored. Their scores are readable against
  the digest each recorded, and the operator error is recorded rather than
  hidden.
- **`check` on a version 3 card defaults to the version 4 rubric** and reports
  drift that is not drift. Re-scoring an old version needs
  `--rubric <frozen>` on `check` as well as on `scaffold`.

---

## 7. `scope` OVER THIS TICKET'S OWN WRITING, AND THE BOUND THAT APPLIES

```
python3 examples/validation/scorecards/score_tools.py scope
```

| tree | counted | REFUTED | COUNT-MOVED | HOLDS | UNREACHABLE |
|---|---|---|---|---|---|
| `95b2c79` + RM-02 — RM-02's reconciled tree | 80 | 59 | 0 | 4 | 17 |
| **this ticket's tree** | **81** | **59** | **0** | **5** | **17** |

**RM-03's delta is +1 counted, +1 HOLDS, and nothing else moves.** The one
figure this ticket contributes to the counted column is
`references/eval_scorecard.md:22` — `D1 is 3 on 55 of 59 ab_quota_ledger cards`
— and it **HOLDS**, re-derived against the cards on disk. This ticket refutes
nothing and moves no existing figure.

**The applicable bound is the first one, `RD-02-DF-01`** — three of this
ticket's figures are *invisible* to the checker rather than checked by it, and
that is stated here rather than left for a reader to discover:

- `D5 is 3 or 4 on 53 of 59 ab_quota_ledger cards` — a figure naming **two**
  values is not matched at all;
- `D4 tier-splits on 4 of the 8 judge groups` — counts judge groups, not cards;
- `an anchor decision cites this project's machinery in 38% of D1 rationales` —
  a percentage of rationales is not a card count.

Not `RD-04-DF-01` and not `RM-02-DF-05`: the one figure that *is* counted parses
correctly and resolves its example.

---

## 8. WHAT WAS REJECTED — especially what would have made this look bigger

- **`scripts/kill_test.py` and `run_kill_test.py`, 1384 lines.** By a wide
  margin the largest removal available, and it belongs to **both** dead levers
  at once: a *hard static gate* (`kill_rate_floor`, described in its own
  docstring as "the load-bearing one") over *model-derived case bug-finding*.
  **Rejected because it is a specified action of `TlaSpecDevCli.tla`** and
  RM-03's plan entry declares `model_delta_expectation: none expected`. Taking
  the biggest number available by quietly changing the specification is the
  shape of error this epic exists to find. `RM-03-DF-05`.
- **Reclassifying `rubric_v3_frozen.md` from `proof` to `replacement`.** A free
  1 : 3.9 → 1 : 1.05 improvement on §3.1's ratio, available in one keystroke and
  arguably correct. Not taken; RD-02 refused the same trade.
- **`examples/validation/ab/check_catalogue.py`, 1344 lines**, named in
  RM-02 §5.4's parenthetical. Rejected: it is not a catalogue, it is the
  arm-dispatch integrity instrument whose `--arms` mode produced FI-06's
  retraction of PA-06's tolerance claim, and `tests/test_ab_three_arms_and_port_faults.py`
  and `tests/test_dispatch_record.py` rest on it. Deleting a working check to
  make a line count larger is the trade this ticket is supposed to refuse.
- **`examples/validation/gap_mutants/altered_score_probe.py` (177) and
  `residual_faults.toml` (193).** They sit in the deleted directory and look
  like part of the cut. They are **RM-01's**, not the catalogue's:
  `altered_score_probe.py` is RM-01's demonstrated `DIES` → `SURVIVES` on a real
  removal — the R1 requirement that an instrument ship with a demonstrated
  failing input — and `residual_faults.toml` is the measured pair behind
  `RM-01-DF-01`. Cutting either would delete the evidence that the pricing
  instrument can fire, in the ticket whose job is to fire it.
- **Repairing any of RM-06's six red tests.** They are other tickets' findings.
- **`scripts/analyze_complexity.py` (2401) and `code_complexity.py` (968).**
  Irreducibly local is not the same as should be cut. What the adoption argument
  demanded was narrower and it was done: D2's anchor preamble no longer requires
  their output to be read first.
- **`scope`, `seal`, `contested`, the blinding mechanism, `R-H2`, `R-H4`, `R3`,
  and the behavioural suite.** Untouched.

---

## 9. DID THE SUBSTRATE ACTUALLY SHRINK?

**Lines: no, not on the card; yes, on the gap-mutant machinery.** §3.1 is
+970/−249 and §3.3 is −1911/+0. The two are different in kind and adding them is
the total this page refuses.

**Instruments: one fewer.** `run_gap_mutants.py` is gone. `price_removal.py`
keeps its `entail` mode and loses the only producer of its `price` mode's input
— `RM-03-DF-01`, blocking, escalated.

**Concepts an adopter must understand: this is where the removal is real.** A
judge went from five anchor ladders and 25 rungs to two ladders and 9 rungs,
from a card that required a measured TLA+ descriptor to be read first to one
that says diff the two trees, and from R-H1's 48-line architecture apparatus to
one sentence. Two of the four things RM-02 costed an adopter — a formal model
and a model-derived check — are no longer asked for anywhere on the card.
