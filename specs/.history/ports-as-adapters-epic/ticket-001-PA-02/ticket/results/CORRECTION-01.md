# CORRECTION-01 — PA-02's headline table mixed two denominators

Raised by the epic owner in post-merge review, 2026-08-05, against commit
`d0b11ad`. **Filed as an addition. `NARRATIVE.md` and the measured records
beside it are UNEDITED**, per the standing treatment of a superseded number:
the run stands on the record as it was reported, and the correction sits next
to it.

**No measured figure was wrong. Every number the instrument printed is
reproducible and correct.** What was wrong is which of two correct numbers went
into which column of one table.

---

## The defect

`scripts/code_complexity.py` prints two totals blocks, `totals` (all modules)
and `totals_code_only`. PA-02's headline table — the one in the commit message
and the PR body, and the first of the two tables in `NARRATIVE.md` §1 — used
**`totals` for all four trees**.

That is self-consistent and still misleading, because the four trees do not
carry comparable denominators:

* `reference/` and `reference_ports/` ship **no test modules**, so for them
  `totals == totals_code_only`. Those columns were effectively code-only.
* `arm_a` and `arm_b` **do** ship their own tests, so their columns included
  them.

Two different things sat in adjacent columns, and the coincidence in the anchor
columns made the mixture invisible by eye.

## What it changed

| figure | as tabled (`totals`) | like for like (`totals_code_only`) |
|---|---|---|
| `branch_points` | 37 → 19, apparently halved | **10 → 11, the ported tree is HIGHER** |
| `max_depth` | 5 → 3 | **1 → 1, identical** |
| `public_surface` | 52 → 48, apparently smaller | **20 → 25, the ported tree is HIGHER** |
| `effectful_calls` | 20 → 6 | 5 → 3 |
| `code_lines` | 422 → 407 | 151 → 202 |

As tabled, the hexagonal arm looked substantially simpler. Like for like it is
slightly **larger** on surface and branching and identical on depth.

**The apparent improvement was an artifact of `arm_a` shipping a bigger test
file.** `arm_a`'s single test module carries **27 of its 37** all-modules branch
points and **15 of its 20** effectful calls; `arm_b`'s carries 8 of 19 and 3 of
6. Nothing about either implementation moved.

## Why it matters more than an ordinary error

This is **MF-020 wearing a new hat**: a number that improves because of *what
got counted*, in the ticket written to honour MF-020. And it is worse than the
usual case, because these figures land in a scorecard's **mechanical block,
which is recorded and never scored**. No judge challenges them. **A wrong number
in the unscored block is a wrong number nothing else in the protocol catches.**

`NARRATIVE.md` §2a already carried the correct like-for-like figures and said
"branch count 10 vs 11, max depth 1 vs 1 … for both pairs". The table
contradicted the paragraph beneath it, and the table is what a reader in a hurry
takes.

## The correction

1. **`role=code` in every column** is now the like-for-like table, recorded in
   `references/complexity_intuition.md` under a heading that names the shipped
   block key. The all-modules figures are kept — they are a real fact about the
   arms — in a **separate, labelled block, never interleaved**.
2. **The denominator rule is written down** as caution 3 of "Reading it", with
   this mistake as its worked example.
3. **It is executed, not promised.** `tests/test_code_complexity.py`:
   * `test_recorded_figures_match_a_live_run` asserts every cell of both tables
     against a live run, each from the block its own heading names. Verified by
     mutation: reintroducing the exact mixture (arm columns from `totals` inside
     the like-for-like table) fails with
     `('totals_code_only', 'branch_points', [10, 11, 37, 19], [10, 11, 10, 11])`.
   * `test_the_two_denominators_differ_so_a_mixed_table_is_catchable` names
     which trees the check is sharp on (`arm_a`, `arm_b`) and which it is not
     (`reference`, `reference_ports`), so the guard's own blind spot is stated
     rather than assumed.
   * `test_the_test_modules_carry_the_difference_and_it_is_recorded` measures
     the 27-of-37 split rather than narrating it.

## What does not change

* **The instrument.** No output format change beyond nothing; it already
  printed both blocks correctly and correctly labelled. The error was in the
  report, not the tool.
* **`GOAL-complexity-measurable`.** The instrument still tells both pairs apart,
  and it does so on `declared_interfaces` (0 vs 1), `internal_import_edges`
  (0 vs 3) and the effectful-module partition (`branch_points_in_effectful_
  modules` 10 → 1, `instance_state_in_effectful_modules` 8 → 1) — **exactly the
  figures that survive the correction, and exactly the ones measuring the port
  rather than the size.** The 10 → 1 partition reproduces unchanged.
* **No comparison mode was added**, no target was touched, and the goal's
  expected effect is unchanged.

## `PA-02-DF-01` gets STRONGER

The finding was already written from the implementation-only figures, so its
numbers were right. Under the corrected table it sharpens: like for like the
ported tree is **larger on more figures than the mis-tabled version showed** —
`code_lines` 151 → 202 and `effectful_calls` 5 → 3 join `public_surface`,
`modules` and `classes`, while branching, depth and the worst callable are flat.
The claim "the produced-code figures support no simplification claim for either
arm" is better supported after the correction than before it. It is not
softened; see `PA-02-DF-01`'s appended `correction` block.
