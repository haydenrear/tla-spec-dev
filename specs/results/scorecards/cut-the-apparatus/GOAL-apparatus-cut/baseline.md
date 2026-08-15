# `GOAL-apparatus-cut` — baseline

**Measured at the epic base `08d1d6a90ad2638cdfceee7cc2e150732daa3438`**
(`main`, the merge of `epic/score-drives-validation`), on the freshly created
`epic/cut-the-apparatus` worktree, **before any ticket landed**.

---

## The command, verbatim

```bash
find scripts examples/validation -name '*.py' -not -path '*/__pycache__/*' | xargs wc -l | tail -1
```

## The figures

| surface | lines | note |
|---|---:|---|
| `scripts/` | **27,652** | `find scripts -name '*.py' -not -path '*/__pycache__/*'` |
| `examples/validation/` | **15,901** | `find examples/validation -name '*.py' -not -path '*/__pycache__/*'` |
| **apparatus total** | **43,553** | the goal's metric |
| `tests/` | 32,162 | reported for context; **not** in the metric |

**The card, reported separately and never combined with the above:**

```
python3 examples/validation/scorecards/score_tools.py serve | wc -c   ->  6281
python3 examples/validation/scorecards/score_tools.py serve --digest-only
    -> sha256:2d7d4a0506d9b259  (card version 5, rubric file sha256:b7fe75437bf68646)
```

9 rungs, 2 scored dimensions.

**Ratio: the card is 6,281 bytes against 43,553 lines of apparatus. That ratio
is the epic's subject.**

## The target

**≤ 30,487 apparatus lines** — a cut of **at least 30%** from 43,553 — with
every deletion naming the finding ID that justifies it, and the card at
**≤ 6,281 bytes**.

---

## `denominator_rule`: this figure is not issue #254's figure

Issue #254 states **42,446 lines of Python** under `examples/validation/` +
`scripts/` at `d038afd`, **and does not state the glob that produced it.** This
file's 43,553 is *this* command at *this* tree. The two are **not
interchangeable**, and the 1,107-line gap is not evidence of anything: it is
two unstated denominators.

**Every figure in this epic names its tree and its command.** `SV-05-DF-04`
measured four previously-holding claims refuted by one epic's own eight cards,
one of them in the shipped card file, for exactly this reason: *write the tree
and the population into the sentence, or stop writing counted figures in the
present tense.*

## Largest files at the base, for orientation only

These are **not** a cut list. The cut list is the findings, and it lives in
`ticket_plan.yaml`.

```
3571  examples/validation/scorecards/score_tools.py
3471  scripts/generate_cases_from_tlc_dump.py
2455  scripts/run_generated_case_adapters.py
2401  scripts/analyze_complexity.py          <- STAYS (serves the spec workflow)
1845  scripts/effect_conformance.py
1408  scripts/onboard_program_model.py
1344  examples/validation/ab/check_catalogue.py
1251  scripts/spec_evolution.py
1245  scripts/complexity_ledger.py
1149  scripts/kill_test.py
 968  scripts/code_complexity.py             <- STAYS (serves the spec workflow)
 838  examples/validation/gap_mutants/price_removal.py
 429  examples/validation/removal_census/removal_census.py
 281  scripts/candidate_note_bar.py          <- nothing imports it (SV-06)
 177  examples/validation/gap_mutants/altered_score_probe.py
```
