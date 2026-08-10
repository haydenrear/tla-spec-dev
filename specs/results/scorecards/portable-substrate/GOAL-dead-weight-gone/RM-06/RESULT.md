# RM-06 — the sixteen, sorted

**BLOCKING.** RM-03 cannot price a removal against a red baseline.

**The split is the deliverable, not the green.** This ticket ends with **six
tests still red**, deliberately, each carrying its own account in its own
docstring and a finding beside it.

**Branch point** `95b2c79`, as the work order required, verified before any
edit. **Reconciled onto `356ffe8`** mid-ticket when RM-02 landed.

---

## 1. The measurement, with its tree

Both runs are **REAL CHECKOUTS** with their own gitignored `.claude/` and
`.skill-manager/` homes. Neither is a `git archive` staging, and no figure below
is a property of a tree without a `.git`.

Interpreter: CPython 3.12.13 with `pytest`, `hypothesis`, `pyyaml`, `jinja2`.
Command: `python -m pytest tests -q`.

| tree | commit | result |
|---|---|---|
| **BEFORE** — epic worktree, `git status` empty | **`356ffe8`** | **16 failed, 1481 passed** in 784.87s |
| **AFTER** — ticket worktree, `git status` empty | **`e0dae3d`** | **6 failed, 1495 passed** in 865.33s |

### The BEFORE set is the fourth independent measurement of the same sixteen

RM-01 measured it at `2c0d94e` and `1af158b`. RM-02 measured it at `29c1adc`.
This ticket measured it at `356ffe8`. **All four failing sets are identical name
for name.** None of the sixteen belongs to any ticket, and the epic base
inherited every one of them from `main` at `19c5c7b`.

`denominator_rule`, BEFORE to AFTER. **Ten of the sixteen went green and six
remain by design.** The passing column moves 1481 → 1495, and that is +14 rather
than +10 because the denominator ALSO rose: collection goes 1497 → 1501. Four of
the fourteen are the ticket-workspace tests `scripts/start_ticket.py` scaffolds
into `specs/tickets/RM-06/tests/`, **and they go away at close** — so the tree
this PR leaves behind reads **6 failed, 1491 passed**. Ten of the fourteen are
failures repaired. Nothing left either column.

Both runs are recorded verbatim beside this file as `suite-before-356ffe8.txt`
and `suite-after-e0dae3d.txt`.

---

## 2. THE SIXTEEN, SORTED — with the reason for each

### Group 1 — pinned to a count the record legitimately grew

RD-03 added 24 cards. The verdict each of these asserts is still correct; only
the number moved. **Every expectation is re-derived from the record, and none is
re-derived by asking the same function that produced the number.** No exact
count was replaced by a `>= 1` floor anywhere in this ticket.

| # | test | pinned to | the record now says | how the expectation is re-derived |
|---|---|---|---|---|
| 1 | `test_score_tools.py::test_the_claim_that_justified_an_epic_is_refused` | 8 counterexamples | **16** | the counterexample set must equal, **card for card**, every filled card in the record whose `D2` is not 2 — computed from the cards on disk, not read back out of the sweep |
| 2 | `test_score_tools.py::test_the_same_figure_with_its_scope_beside_it_is_not_refuted` | the literal `35 of 35 … ab_quota_ledger` HOLDS | **REFUTED at every denominator** | the figure is computed from the cards, then evaluated **twice** — with and without the example named beside it — and the two verdicts must differ |
| 3 | `test_score_tools.py::test_the_committed_history_rendering_is_current` | the committed rendering | 24 rows short | the **rendering** is regenerated; the test is untouched |
| 4 | `test_score_tools.py::…records_its_one_contested_dimension` → `…records_every_contested_dimension_it_computes` | `len(entries) == 1` | **7** | the ledger must record **exactly** the groups the cards compute, in both directions |
| 5 | `test_architecture_tags.py::test_a_card_with_no_subject_is_legal_and_is_every_sealed_card` | `declared == []`, `48 mapped / 1 unmapped` | 24 cards declare a subject | split into the half that was load-bearing — **no card predating RD-05 grew a subject field**, which is what R-H4 actually says — plus a new one: every declared subject is declared in `subjects.toml`. The mapping is re-derived rather than pinned. |

**#5 is the one worth reading twice.** `declared == []` was not a stale count.
It asserted that RD-05's own feature had not shipped: a card scaffolded from
RD-05 onward is *designed* to carry `subject.name`, and RD-03 was the first
round to scaffold 24 of them. Restoring the empty list would have asserted a
falsehood about the product.

### Group 2 — controls that are genuinely failing. **THESE STAY RED.**

| # | test | why red is the correct outcome |
|---|---|---|
| 6 | `test_architecture_tags.py::test_the_same_tag_control_holds` | **`RM-06-DF-01`.** Nine same-tag pairs separate — eight on `D2`, one on `D5` — and every one is an RD-06 before-tree scoring disjointly from its own after-tree at the same derived value. The control is reporting a real result: **it cannot tell TREATMENT from ARCHITECTURE.** |
| 7 | `test_architecture_tags.py::test_the_committed_demonstration_re_derives_from_the_cards` | **`RM-06-DF-02`.** The one declared refusal authority in the record disagrees with the cards. |
| 8 | `test_score_tools.py::test_the_repo_ledger_passes_its_own_audit` | the same single violation |
| 9 | `test_score_tools.py::test_the_repo_ledger_passes_its_own_audit_with_rh6` | the same single violation |
| 10 | `test_score_tools.py::test_the_shipped_rh5_demonstration_still_goes_red` | the same single violation, one layer out |
| 11 | `test_instrument_demonstrations.py::test_every_fast_demonstration_reproduces` | the same single violation, plus `RM-06-DF-04`. **Two of its four broken slots WERE repaired** — `scorecard-scope/passing` and `scorecard-contested/passing` — and the `scorecard-contested-drift/failing` mutation anchor, which had gone `MALFORMED` and was therefore executing nothing at all. What is left is `scorecard-audit` and `scorecard-contested-drift` asserting record-wide violation TOTALS that the standing defect moves. |

#### #6 — the same-tag control

The two repairs that would have cleared it were both **rejected**:

- **scoping the control to the dimension the separation is claimed on**, where
  it still holds — that makes it a check about the shipped row rather than about
  the axis;
- **excluding revision pairs from the population** — that removes exactly the
  evidence the control exists to see.

Either one converts a measurement into a tautology. The test now names the nine
pairs in its assertion message and says in its own docstring that it is
deliberately red.

#### #7–#11 — one stale declaration, five red nodes and four red registry slots

`audit` reports **exactly one violation** over this repository, at `2c0d94e`, at
`95b2c79` and at `356ffe8` alike: the ledger's `[[demonstration]]` row declares
a range and a tier list that the 73-card record no longer supports.

**This ticket repaired that row and then reverted the repair on the epic owner's
instruction, and the instruction is right.** Editing a declared refusal authority
into agreement with the cards makes it certify whatever the record happens to
say — it stops being a control — and it silently widens what the axis may refuse
a comparison on, from one judge tier to two and from a lower bound of 1 to 0.
Settling it belongs beside RM-04's threshold work.

**And the row is not wrong; it is scoped — which is now asserted rather than
argued.** `test_the_committed_demonstration_re_derives_from_the_cards`
re-derives the demonstration table over the 49 cards sealed before
`reading-discipline` — RD-04's own population — and the declaration reproduces
**exactly**, ranges and tier list both, *before* it goes red on the live record.
That is the difference between a stale declaration and a wrong one, executed.

### Group 3 — claims that were true and are now false. The claim is rewritten.

| # | test | the claim that died | what replaced it |
|---|---|---|---|
| 12 | `test_architecture_tags.py::test_the_one_row_carries_its_tier_limit` | *"no `sonnet` judge has ever scored a `ports-and-adapters` subject on `ab_quota_ledger`: n = 0"* | `tiers_measured` is asserted at its true value **and the bound is re-derived**: the `sonnet` `ports-and-adapters` population is four cards over **two** declared subjects, and those two are the `E`→`F` revision pair. `n = 0` became `n = 1 tree`. |
| 13 | `test_architecture_tags.py::test_a_null_verdict_that_could_not_have_come_out_otherwise_is_marked` | *"`D2` took ONE value across the whole comparison population"* | exact correspondence over the live record, re-derived from raw card scores; **plus the marking demonstrated still firing on the 49 sealed cards**, where that population is single-valued |
| 14 | `test_architecture_tags.py::test_the_population_range_is_printed_beside_every_non_separating_verdict` | `assert "NULL-ENTAILED" in out.stdout` | the set of printed marks must **equal** the set of entries the table derives as null-entailed — currently empty, so what is asserted is that the marker appears nowhere |
| 15 | `test_score_tools.py::test_contested_fires_on_exactly_one_group_in_the_whole_sealed_record` → `test_contested_is_re_derived_and_still_fires_on_a_minority_of_groups` | *"exactly one group in the whole sealed record"* | the flagged set is compared against an **independent** re-implementation of rule 5 over the raw cards, and the check must still fire on a strict **minority** of judge groups |
| 16 | `test_score_tools.py::test_a_scoped_claim_whose_denominator_moved_is_stale_and_not_refuted` | the shipped `SM-04` line is COUNT-MOVED | that line is now **REFUTED** and the test says so; the staleness/refutation distinction is kept executed on a **real card population** (`ex4_pipeline_coherent`), and the test asserts the finding directly: **no line in the shipped record reaches COUNT-MOVED any more** |

#### #13 and #14 — the honest cost of the rewrite, stated

The live record now contains **no null-entailed cell at all**, so an existence
assertion about the marker cannot be kept. Replacing it with exact
set-correspondence is stronger in shape and empty in content today, and that
would have been a hollow trade on its own. It is not left on its own: #13
demonstrates the marking **firing** over the 49 sealed cards, which are real and
are not a fixture. The mechanism is still shown to work; what changed is the
corpus.

#### #16 — the finding hiding inside a repair

`SM-04`'s line did not move because the sweep changed. It moved because RD-06's
revision pairs supplied counterexamples on the very example it was correctly
scoped to. Chasing that one line surfaced `RM-06-DF-03`: **the sweep has four
verdicts and two of them now have no live instance anywhere in the record.**

---

## 3. WHAT I REJECTED

Every one of these would have reached green faster by asserting less.

1. **Repairing the `[[demonstration]]` row.** Done, then reverted on the epic
   owner's instruction. It would have turned five red nodes and four red
   registry slots green in one edit — the single largest green available in this
   ticket — by making a declared authority agree with itself.
2. **Scoping the same-tag control to the dimension where it still holds.** One
   line, nine failures gone, and the control would thereafter have been unable
   to report the thing it just reported.
3. **Excluding RD-06's revision pairs from the same-tag population.** Same
   green, and it deletes the only within-value treatment difference the record
   has ever contained.
4. **`assert len(named) >= 1`** on the counterexample set, and its siblings.
   Explicitly forbidden by the work order and correctly so: it passes on a sweep
   that finds one counterexample and loses fifteen.
5. **Restoring `35 of 35 … ab_quota_ledger` as the scope control.** It is false
   at every denominator now. Also rejected: re-pinning the currently true
   `51 of 59`, which is true today and goes stale on the next round that scores
   that example.
6. **Re-pinning `1 violation(s)` to `2 violation(s)`** in the two registry
   demonstration slots. That bakes a standing defect into a demonstration, so
   the demonstration would go red when the defect is *fixed*.
7. **Dropping `1 violation(s)` from those slots instead.** Considered, written,
   and reverted within the same edit: the enclosing test is red either way, so
   dropping an exact assertion bought no green at all — only a weaker registry.
8. **Widening the null-entailed assertion to "the marker appears or the
   population is multi-valued".** A disjunction that cannot fail.

---

## 4. Findings filed — four, none fixed inline beyond this ticket's scope

| id | severity | one line |
|---|---|---|
| `RM-06-DF-01` | major | the same-tag control fires nine times and cannot distinguish treatment from architecture |
| `RM-06-DF-02` | **blocking** | the one declared refusal authority no longer matches the cards; five suite nodes and four registry slots are red downstream of it and of nothing else |
| `RM-06-DF-03` | major | the sweep returns 0 COUNT-MOVED and 0 HOLDS over the whole record — two of its four verdicts have no live instance |
| `RM-06-DF-04` | minor | a demonstration pinned to a record-wide property measures the record, not the break: one mutation anchor went MALFORMED on corpus growth (repaired), two violation totals are red on an unrelated standing defect (not repaired) |

`RM-06-DF-02` is `blocking`, and the deferment policy says blocking escalates to
the owner. **It was escalated and the owner ruled on it before this ticket
closed**, which is the ruling recorded in §2 and in the test's own docstring.

---

## 5. `scope` over this document, and the bound that applies

Run: `score_tools.py scope --path <this file>`.

**Result: 0 counted figures — 0 REFUTED, 0 COUNT-MOVED, 0 HOLDS, 0
UNREACHABLE.** That is not a clean bill of health and it is not reported as one.

**THE APPLICABLE BOUND IS THE FIRST ONE, `RD-02-DF-01`.** The sweep is keyed on
a figure of the form `D<n> = k on N of M cards`. This document is full of counts
about dimensions — nine same-tag pairs of which eight are on `D2`, sixteen
counterexamples against a population of seventy-three cards, a `sonnet`
population of four cards over two subjects — and **not one of them is written in
that form**, so every one is INVISIBLE to the sweep: not refused, not
`UNREACHABLE`, not counted. `RD-02-DF-01` says exactly this and says it moves
the count DOWN by an unmeasured amount. A reader who takes `0 REFUTED` here as
evidence that this document's figures were checked has read it backwards.
**Nothing in this document was checked by the sweep.**

Two further bounds apply to what this document says rather than to what it
counts:

- **`RD-05` §7.1** — this document **mentions** the claims it is calling dead
  (`35 of 35`, *"exactly one group"*, *"n = 0"*) in order to say they are dead.
  The checker cannot tell a claim from a mention of one, so had any of those
  been written in countable form they would have been refuted for being quoted.
- **`RM-02-DF-05`** — the counted-noun pattern excludes the underscore and every
  example id in this corpus contains one, so a figure here could not have
  carried `ab_quota_ledger` as its counted noun even if it had wanted to. The
  scope would have had to sit in the preceding two lines instead.

`RD-04-DF-01`, the ≤3-word qualifier window, does not bite: with no counted
figure there is no qualifier to land outside it.
