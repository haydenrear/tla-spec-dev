# SS-07 — the four standing results at the tip, and the stranded disproof instrument

Ticket `SS-07`, issue #276, branch `feature/SS-07`, base **`48f9c7e`** (the
resolved OID of `origin/epic/stabilize-substrate`, wave-1 tip).
Goal `GOAL-four-results-still-stand`, contribution **direct** (clauses a, b, d).
Goal `GOAL-tree-stabilizes`, contribution **guard**.

**Every figure in this file names the tree it was measured on and the root it
was swept in.** `SS-01-DF-03`: a verdict is a joint property of the artifact AND
the tree. Where a figure was corroborated in a second checkout, both are named.

**Measurement cells.** Three checkouts of the same commit were used and they are
distinguished throughout: **`WT`** = the ticket worktree
(`wt-epic-stabilize-substrate-SS-07`, tracked changes present), **`A`** and
**`B`** = two detached, otherwise-untouched worktrees of `48f9c7e` created for
this ticket. Neither cell was named after the ticket.

---

## 0. Headline

**All four results stand at `48f9c7e`. Three were re-verified BY EXECUTION and
the fourth by execution of the instrument that computes its numbers. Result 2 is
damaged exactly as recorded and no worse. The stranded disproof instrument is
DECIDED: DISCLOSE.**

**And the disclosure came out stronger than the record said it could.**
`CA-02-DF-04` names a restore command that nobody had ever run. `SS-07` ran it
in a throwaway checkout and `repriced_history.py` reproduces
**byte-identical to its sealed transcript**. The claim is not re-derivable *at
the tip*; it is re-derivable *from this repository's history in three commands*,
and that is a materially better answer than "cannot be re-derived".

**Four defects were found by not stopping**, and the worst is that **running the
verification instruments MUTATES the record they verify** — `score_tools.py
index` rewrote six committed `INDEX.md` files and created three more, silently,
as a side effect of being used to check that the sealed cards render. Every one
was reverted; `git status` is quoted in §5.

**No sealed file was repaired, edited or re-sealed.** `R-H4` held.

---

## 1. The four results, each verified individually

| # | result | verified by | verdict at `48f9c7e` |
|---|---|---|---|
| 1 | Asking for an architecture changes the architecture | **execution** — `check_catalogue.py --arms` re-derives the confound control; `index` re-derives every score | **STANDS** |
| 2 | D3 separates architectures on more than one example | **execution** — `architecture_tags.py derive`; `index`; `contested` | **STANDS, DAMAGED** exactly as priced |
| 3 | D3's v5 caveat discriminates | **execution** — `index` and `history` over four sealed trees | **STANDS** |
| 4 | A score can produce a test and the re-score sees it | **execution** — the conformance suite re-run, `14 passed` | **STANDS, VERIFIED BY EXECUTION** |

### Result 1 — asking for an architecture changes the architecture

Two halves, both re-derived at `48f9c7e` in `WT`.

**The effect.** `score_tools.py index specs/results/scorecards/hexagonal-prompting`:

```
| ab_quota_ledger | A-control-reference | pass 0 | claude-opus-5[1m] | 0 | 2 | 1 | 2 | 3 | — |
| ab_quota_ledger | X                   | pass 1 | claude-opus-5[1m] | 3 | 2 | 4 | 3 | 3 | — |
| ab_quota_ledger | X                   | pass 2 | claude-opus-5[1m] | 3 | 2 | 4 | 3 | 3 | — |
```

**D3 = 1 on the pre-treatment control, 4 and 4 on the treatment arm.** Replicated
in `hexagonal-prompting-rerun` (`Q` = 4, 4) and again in `ports-as-adapters`
(`T` = arm B = 4, 4 against `U` = arm A = 2, 2).

**The confound kill, which is the load-bearing half.**
`python3 examples/validation/ab/check_catalogue.py --arms` **still runs** and
re-derives the length match from the prompts on disk, not from a recorded number:

```
arm B unique vs arm A: 105 lines   (6.56x arm A's 16 -- the predecessor's 6.6x)
arm C unique vs arm A: 109 lines
arm C / arm B:         1.038  (+3.8%), tolerance +/-10%
ARCHITECTURAL VOCABULARY in content not shared with arm A:
  arm B: 44 of 105 unique lines
  arm C:  0 of 109 unique lines
Catalogue integrity holds: every pattern occurs exactly once, every
mutant applies and reverts cleanly, and every declared gap is seeded.
```

`UNBLINDING.md` maps `W` → arm C, and `index` gives **`W` D3 = 1, 1**. So a
**longer** prompt carrying **zero** architectural terms scores **1/1** while the
treatment scores 4/4. **The confound is dead at this tree, re-derived rather
than quoted.** The instrument prints its own limit unprompted — *"a vocabulary
probe, not a semantic judgement"* — and that sentence is not softened here.

### Result 2 — D3 separates architectures on more than one example, DAMAGED

**Confirmed at `48f9c7e`, in both `WT` and cell `B`:**

```
$ python3 examples/validation/scorecards/architecture_tags.py derive
rm04_removal_pricer      derived=UNDERIVABLE:no-effect-surface   declared=effectful   UNDERIVABLE
                           iface=0 eff_mods=0/0 state_coloc=None
...
16 of 21 subject(s) decided; 5 refused.
```

**`denominator_rule`: the NUMERATOR fell, 17 → 16. The DENOMINATOR held at 21.**
`rm04_removal_pricer`'s declared scope is `examples/validation/gap_mutants`,
which `CA-02` emptied of Python; `eff_mods=0/0` is the tree reporting truthfully
that there is nothing left to derive over. **A replicate was lost, not the
result.**

**The result itself is untouched, and it is re-derived here rather than read.**
`index` over the three sealed `portable-substrate-rm04-*` trees:

| arm | subject | tag | D3, judge 1 (`claude-opus-4`) | D3, judge 2 (`claude-sonnet-4-5`) |
|---|---|---|---|---|
| `GG` | `rm04_eval_harness` | ports-and-adapters | **2** | **4** |
| `JJ` | `rm04_removal_pricer` | effectful | **1** | **0** |
| `LL` | `rm04_scripts` | effectful | **1** | **0** |

**`[0,1]` against `[2,4]` — disjoint, both judge tiers on both sides**, exactly
as the baseline states. `contested` re-computes the `GG` D3 spread of 2 and the
tier split, and `audit` re-verifies both as third-pass-clean.

**What is damaged and what is not, said apart.** The *scores* are intact and
re-derivable; the *architecture-tag derivation* that annotates the effectful side
now runs on **one** subject (`rm04_scripts`) where it ran on two. The
ports-and-adapters side always had one. **`SS-07` does not restore the replicate
and does not price it again — `CA-02` priced it.**

### Result 3 — D3's v5 caveat discriminates

Re-derived at `48f9c7e` in `WT` by `index` over all four sealed trees:

| tree | artifact | D3 pass 1 | D3 pass 2 |
|---|---|---|---|
| `score-drives-validation-sv01-v4` | `sv01_negative_control` — **lacks** the property | 4 | 4 |
| `score-drives-validation-sv01-v5` | same artifact, v5 card | **4** | **4** |
| `close-the-loop-cl03-v4` | `CL-03` — **has** the property | 4 | 4 |
| `close-the-loop-cl03-v5` | same artifact, v5 card | **3** | **3** |

**The caveat moved the artifact that has the property and left the one that does
not alone.** `history --example toolchain_removal` reproduces the same rows with
their card-version era boundary and prints `ROWS ABOVE ARE NOT COMPARABLE TO
ROWS BELOW` — `R-H1`/`R-H2` executed, not promised.

One thing the record does not say and this ticket does: **`close-the-loop-cl03-v5`
carries a contested D2** (pass 1 = 2, pass 2 = 0, spread 2), computed by
`contested` and re-verified by `audit` as `cl03-v5-d2-spread-2`. It is on D2, not
on D3, so it does not touch this result — but a reader comparing the v4 and v5
cards meets a 2-point D2 spread in the same directory and should not read it as
part of the D3 finding.

### Result 4 — a score can produce a test and the re-score sees it

**Re-verified BY EXECUTION at `48f9c7e` in `WT`**, the same way `CA-06` did it:

```
$ QUOTA_LEDGER_PORTS_DIR=examples/validation/ab/reference_ports \
  uv run --with pytest --with pyyaml -m pytest examples/validation/ab/tests/test_journal_conformance.py -q
14 passed in 0.10s

$ QUOTA_LEDGER_DIR=examples/validation/ab/reference_ports QUOTA_LEDGER_IMPL=quota_ledger      ... test_behavior.py -q
28 passed

$ QUOTA_LEDGER_DIR=examples/validation/ab/reference_ports QUOTA_LEDGER_IMPL=quota_ledger_fake ... test_behavior.py -q
28 passed
```

**`14 passed`, matching the sealed figure exactly, and 70 of 70 across the three
wirings.** The conformance suite **is** the test the score produced; it exists
because a judge scored D3 and named what the score could not see.

And the re-score sees it — `index specs/results/scorecards/score-drives-validation-sv04`:

| arm | D2 p1 | D2 p2 | D3 p1 | D3 p2 |
|---|---|---|---|---|
| `GL` (control) | 2 | 2 | **3** | **3** |
| `LG` (treatment) | 2 | 2 | **4** | **4** |

**Control 3,3 against treatment 4,4, D2 flat at 2 across all four.** Exactly the
sealed figures.

---

## 2. Clause (b) — the do-not-cut instruments still run

All at `48f9c7e`; `audit`, `scope`, `serve` and `derive` corroborated in cell `B`.

| instrument | command | result at `48f9c7e` |
|---|---|---|
| **served/version double seal** | `serve \| wc -c`; `serve --digest-only`; stderr header | **6281 bytes**; `sha256:2d7d4a0506d9b259`; `served digest sha256:2d7d4a0506d9b259 (card version 5, rubric file sha256:b7fe75437bf68646)` — identical in `WT` and `B` |
| **`R-H4`** | `score_tools.py audit` | **0 violation(s)**, exit 0, in `WT` **and** in fresh cell `B`. `SS-01`'s repair of `SS-00-DF-01` holds on a second checkout |
| **`seal`** | `seal` over all 11 sealed card trees of the four results | `nothing new to seal`, tree unchanged — idempotent, and its drift branch is the refusal that protects the seal |
| **`contested`** | `contested` | **9 contested dimension(s) over 39 judge group(s), 0 unrecorded** |
| **`R3` / `scope`** | `scope` (default sweep, swept **inside the repository**) | **103 counted figures: 81 REFUTED, 0 COUNT-MOVED, 2 HOLDS, 20 UNREACHABLE**, exit 1 — its demonstrated failing input is this repository's own record. Identical in cell `B` |
| **`scope --path NEXT-EPIC.md`** | | **3 counted, 3 REFUTED** — matches the charter |
| **`R-H1`/`R-H2`** | `history --example {ab_quota_ledger,eval_toolchain,toolchain_removal}` | all three render, era boundaries printed, no cross-era average |
| **the blinding mechanism** | `blind_dispatch.py cell` / `check` | see below |
| **`check`** | `check <every card tree of the four results> --require-filled` | **0 problems** on all 11 trees, 33 cards |

**`scope` is 103 at `48f9c7e`, not the 82 in this goal's own baseline.** That is
`SS-01` adding the relocated ledger to `DEFAULT_SWEEP`, and it supersedes the
sealed baseline figure. **Named, not inherited.**

**The blinding mechanism, probed rather than trusted**, per
`planning_rules.blindness_is_re_probed_every_round`:

- `cell` on a path containing `-Users-hayde-IdeaProjects-tla-spec-dev` prints
  `PROBLEM path component ... names the project under test` — **and exits 0**.
  Read the output, not the exit code.
- `check` on an **empty** report: `UNDECIDED: the subject is empty. … This is
  NOT a pass.` The absent-input case is repaired and the `UNDECIDED` branch is
  live, not dead code.
- `check` on a 129-byte report: `UNDECIDED … below the 200-byte floor`.
- `check` on a **586-byte report containing one real memory-entry title and one
  real commit subject**: `REFUSED: 2 leak indicator(s) …  This round is not
  blind.` **The demonstrated failing input fires at this tree.**
- **A hazard every ticket on this epic inherits, stated because it is not
  obvious:** `check --repo .` from a ticket worktree derives **0 memory
  needles**, because a worktree has no memory slug of its own, and returns
  **WEAK PASS**. The strongest needle class is silently unavailable. The source
  documents this at `blind_dispatch.py:99-105`; pass `--memory` with the
  **dispatching session's** file. With it, 20 memory needles were derived and
  the refusal above fired.

## 3. Clause (c) — the card does not grow

`serve | wc -c` = **6281** at `48f9c7e`, equal to the 6,281 clause ceiling, in
both `WT` and cell `B`. Digest **`sha256:2d7d4a0506d9b259`**, card version **5**,
rubric file **`sha256:b7fe75437bf68646`** — byte-identical to the sealed base
figures in `serve-digest-436c78c.txt`. **This ticket added no note and no rung.**

## 4. Clause (d) — the stranded disproof instrument is DECIDED: **DISCLOSE**

The decision and the full disclosure are written where a reader of the claim
meets it:
**`specs/results/scorecards/close-the-loop/GOAL-price-means-something/00-DISCLOSURE-NOT-RE-DERIVABLE-AT-THE-TIP.md`**,
sorting first in that directory, beside the sealed transcripts and above
`RESULT-CL-02.md`. **No file in that directory was edited.**

Summary of what it records:

- **Re-confirmed at `48f9c7e`:** `repriced_history.py` dies with
  `FileNotFoundError` on `examples/validation/gap_mutants/price_removal.py`;
  `examples/validation/removal_census/removals.toml` is absent too. **The four
  sealed before-tables it reads all survive** — the data lives, the instrument
  does not.
- **DO-NOT-CUT was not available**: the cut landed four commits before this
  epic branched. **`R-H4` forbids repairing.** So: **DISCLOSE.**
- **New, and it is the useful part:** `CA-02-DF-04`'s `reproduction` names a
  restore command that had never been run. Run at `48f9c7e` in cell `B` with
  `examples/validation/{gap_mutants,removal_census}` restored from `37ab155`:

  ```
  TOTAL PRICED RESULTS ACROSS RE-PRICED HISTORY: 0
  priced rows: []
  RM-01-RF-1 ... PRICED      RM-01-RF-CTRL ... CONTROL-EXCLUDED
  ```

  **`diff` against the sealed `repriced-history-sweep.txt`: byte-identical.**
  A doubter now has a runnable route that requires trusting no transcript —
  the property `CA-08` said a transcript alone cannot supply.
- **What it does not buy**: the route depends on `37ab155` staying reachable.
  Checked: reachable in this repository and in the installed
  `spec-double-compiler` unit (not a shallow clone). A shallow or rewritten
  history breaks it with nothing going red.

**The two withdrawn overstatements are NOT restored.** The disclosure strikes
them by name and uses `NEXT-EPIC.md` §5's wording: *"a non-zero was the
informative outcome, the instrument would have printed one, and none appeared —
the goal is met and the instrument is not yet useful."*

## 5. Not stopping — what the sweep found

`CA-04` verified the two consumers it found and stopped; review found three
more. So this ticket looked past its four subjects.

**Consumers of `scripts/kill_test.py` at `48f9c7e` — five, matching the review's
correction, not `CA-04`'s two:**

| # | site | found by |
|---|---|---|
| 1 | `examples/validation/ab/eval/run_controls.py:165` (module scope) | `CA-04` |
| 2 | `examples/validation/ab/check_catalogue.py:457` | `CA-04` |
| 3 | `tests/test_falsifiable_controls.py:470` | review |
| 4 | `tests/test_ab_three_arms_and_port_faults.py:573` | review |
| 5 | `tests/test_eval_controls.py:503` | review |

`scripts/kill_test.py` is **310 lines** at this tree, exactly the retained count,
and `check_catalogue.py --arms` — the instrument that re-derives result 1's
confound kill — runs. **Disproof 1 is still re-derivable.**

### The general check `CA-02-DF-04` asked for, computed

`CA-02-DF-04`'s `suggested_fix`: *"a cut must GREP THE SEALED RECORD for loaders
of every file it deletes."* Nothing ever computed it. This ticket wrote
`stranded_loaders.py` (in this directory) and ran it. It is **not a gate**: it
asserts nothing, exits 0 on any finding, and ships `--selftest` with three
absent-input cases and one failing input, whose correct answers are `REFUSED`,
`UNDECIDED`, `NO-PATHS` and `STRANDED` — never `PASS`.

Swept at `48f9c7e` over `specs/results` (160 files): **8 files name 15 absent
paths.** Each was then **executed**, because a literal that is never loaded is
not a stranding:

| script | runs at `48f9c7e`? | verdict |
|---|---|---|
| `.../close-the-loop/GOAL-price-means-something/repriced_history.py` | **NO — `FileNotFoundError`** | **STRANDED**, the known one (§4) |
| `.../score-drives-validation/.../SV-03/analysis/no_card_project_unaffected.py` | **runs, exits 1, all four patches fail to apply** | **STRANDED BY SUCCESS** — new, `SS-07-DF-03` |
| `.../coverage-audit-hexagonal-prompting-raw/classify_scope_v2.py` | runs, **overwrites 4 committed evidence files with different content** | **`SS-07-DF-02`** |
| `.../finalization/sweep-raw-close2/cac2_classify.py` | runs, **overwrites 1 committed evidence file with different content** | **`SS-07-DF-02`** |
| `.../cut-the-apparatus/CA-06/mutation_probe.py` | refuses: `KeyError: 'CA06_WORKTREE'` | parameterised, not stranded; its literal is subject-relative |
| `.../coverage-audit-arch-coherence-raw/cac_ac_classify.py` | runs, exit 0 | literals are rule-table prose, never loaded |
| `.../epic-close/sweep-raw-run4/ca4_classify.py` | runs, exit 0 | same |
| `.../ports-as-adapters/GOAL-port-reach/measure/run_port_swap.py` | runs, exit 0 | literal is subject-relative |

**Stated limit, not discovered later:** the sweep reads string literals. A path
assembled at runtime, read from a manifest or globbed is invisible to it, and
the report says so in its own output. **A clean report is a floor.**

### The worst one: verifying the record MUTATES the record

**`score_tools.py index` writes `INDEX.md` into the card tree it is pointed at
(`score_tools.py:1657`) and has no read-only mode.** Running it to check that
the sealed cards render — which is what this goal's own harness asks for —
**modified six committed `INDEX.md` files and created three that had never
existed**:

```
 M specs/results/scorecards/hexagonal-prompting/INDEX.md
 M specs/results/scorecards/hexagonal-prompting-rerun/INDEX.md
 M specs/results/scorecards/portable-substrate-rm04-{GG,JJ,LL}/INDEX.md
 M specs/results/scorecards/ports-as-adapters/INDEX.md
?? specs/results/scorecards/close-the-loop-cl03-{v4,v5}/INDEX.md
?? specs/results/scorecards/score-drives-validation-sv04/INDEX.md
```

**Every score value in every diff was identical** — the committed files are
stale only in *presentation*: they carry the `total` column that
`scorecard_version 3` abolished, or the word `opus`/`sonnet` where `RM-04`
requires the full model ID. **That is the reassuring half and it is why the four
results verify.** The alarming half is that a reader running the documented
check silently rewrites the record, and `R-H4` says a sealed measurement is
annotated, never rewritten. **All nine were reverted; the diff for
`close-the-loop-cl03-v4` was kept in this ticket's scratch as evidence of what
was generated, and no generated `INDEX.md` is in this PR.** `SS-07-DF-01`.

**`git status --short` in `WT` after every probe, revert included:**

```
?? specs/results/scorecards/stabilize-substrate/SS-07/
?? specs/tickets/SS-07/
```

## 6. Checking the baseline I was measured against

`GOAL-four-results-still-stand`'s `baseline.md` is the owner's, and the owner's
`GOAL-counted-figures-reach-the-record` baseline was corrected on 2026-08-16
after publishing a cross-tab it never ran. So this baseline was read rather than
trusted. **Two of its figures are stale at `48f9c7e` and one of its mechanisms
is refuted:**

| baseline says (`436c78c`) | at `48f9c7e` | why |
|---|---|---|
| *"`scope` still runs — **82** counted figures"* | **103** | `SS-01` added the relocated ledger to `DEFAULT_SWEEP`. Superseded, not wrong. |
| *"`audit` reports **9** violations at this tree"* | **0**, in `WT` and in fresh cell `B` | `SS-01` repaired `SS-00-DF-01`. The baseline's own caveat predicted this. |
| *"on a fresh worktree **all 85 candidates share one mtime and the largest file wins**"* | **refuted** | The charter withdrew this on 2026-08-16: there are **85 distinct mtimes**, size is never consulted, and the largest file was the *correct* one. The stated cause was an artifact of the owner's `:.0f` probe. **`baseline.md` still carries the withdrawn mechanism**, and `R-H4` means it is corrected here rather than edited there. |

Everything else in the baseline reproduces. **The result claims themselves — all
four, plus result 2's damage and both withdrawn overstatements — are exactly as
recorded, and this ticket re-derived rather than quoted every number it repeats.**

## 7. A rule this ticket did NOT follow, reported rather than hidden

`planning_rules.measurement_rule`: *"SEAL PREDICTIONS BEFORE MEASURING AND SAY
WHEN, in a commit with a timestamp."* **`SS-07` did not.** It began executing the
four results within minutes of provisioning the worktree and no
`PREDICTIONS-SS-07.md` was written first, so **there is no sealed prediction set
for this ticket and none was back-written afterwards** — a prediction file
committed after the numbers are known is worse than none, and `MF-020` forbids
it directly.

**What that costs, stated so `SS-08` can price it:** every verdict in §1–§4 is a
re-derivation of a figure that was already published, so there was no free
parameter for a prediction to have constrained — but §5's sweep *was* open-ended,
and a sealed prediction there would have been worth having. **The four findings
in §8 are therefore reported as findings and not as confirmed predictions.**

## 8. Findings filed — four, fixing nothing

| id | what | disposition |
|---|---|---|
| `SS-07-DF-01` | `index` writes `INDEX.md` into the card tree with no read-only mode; six committed `INDEX.md` are stale and three sealed trees have none | carried -> SS-08 |
| `SS-07-DF-02` | two sealed-record classifiers overwrite their own committed evidence when re-run, with different content at this tree | carried -> SS-08 |
| `SS-07-DF-03` | `SV-03`'s no-card instrument is stranded by success and prints `IDENTICAL: True` in its body while the treatment never applied | carried -> SS-08 |
| `SS-07-DF-04` | the mechanical check `CA-02-DF-04` asked for now exists and is demonstrated, and **nothing executes it** | carried -> SS-08 |

**`SS-07` repaired nothing.** It reverted every mutation its own probes caused
and left the sealed record byte-identical to `48f9c7e`.

---

## 9. The reconciled tip, and the suite

This branch was reconciled onto `origin/epic/stabilize-substrate` at **`eb2567b`**
(after `SS-03` merged) at commit **`06cbcce`**. The ledger tail conflicted with
`SS-03`'s rows and was resolved by **keeping both sets in promotion order** —
`SS-03` (`promotion_order` 20) before `SS-07` (40). **No row was rewritten,
reordered or removed, and the count only rose: 308 at `48f9c7e` → 317 at
`eb2567b` → 321 here.** `disposition.py --ticket SS-07` → `DISPOSED … all three
clauses hold`.

**Every instrument figure in §1–§3 was re-run at `06cbcce` and NOTHING MOVED:**
`serve | wc -c` 6281, digest `sha256:2d7d4a0506d9b259`, card version 5, rubric
`sha256:b7fe75437bf68646`; `audit` 0 violations; `scope` 103 (81/0/2/20);
`scope --path NEXT-EPIC.md` 3, all REFUTED; `contested` 9 over 39 groups;
`derive` 16 of 21; the conformance suite `14 passed`; `check_catalogue.py --arms`
integrity holds; `repriced_history.py` still `FileNotFoundError`;
`stranded_loaders.py` still 8 files / 15 absent references.
Transcript: `evidence/tip-instruments-06cbcce.txt`.

### The suite — FIVE numbers that sum, and every movement attributed

`failed + passed + skipped + xfailed = collection`, every time. **A four-number
report silently stops summing** the moment an `xfail(strict=True)` exists, and
`SS-01` added one.

| tree | cell | `SS-07` workspace | failed | passed | skipped | xfailed | collection |
|---|---|---|---:|---:|---:|---:|---:|
| **`48f9c7e`** (base) | **A**, fresh detached, untouched | **closed** | **8** | **1509** | **0** | **1** | **1518** |
| `48f9c7e` (base) | `WT`, before `open ticket` — **contaminated, see below** | closed | 8 | 1509 | 0 | 1 | 1518 |
| `eb2567b` (epic tip, post-`SS-03`) | **A** | closed | — | — | — | — | **1529** (`--collect-only`) |
| **`06cbcce`** (tip) | `WT` | **OPEN** | **7** | **1525** | **0** | **1** | **1533** |

`8 + 1509 + 0 + 1 = 1518`. `7 + 1525 + 0 + 1 = 1533`. **Both sum.** Collection at
base was also taken directly: `--collect-only` → `1518 tests collected`.

**Every movement, with its numerator/denominator direction:**

| movement | Δ | cause | mine? |
|---|---:|---|---|
| **collection** `1518 → 1529` | **+11** | **`SS-03`'s merge.** Measured directly by `--collect-only` at `eb2567b` in cell `A` with no ticket workspace open: `1529 tests collected`. `SS-03` added 339 lines to `tests/test_goal_baseline_is_a_card.py`. **Denominator rose.** | **no** |
| **collection** `1529 → 1533` | **+4** | **`open ticket SS-07`**, widening parametrized `test_spec_yaml_valid` over the scaffolded `specs/tickets/SS-07/` tree — the +4 the assignment documents, on the OPEN side of the close. **Denominator rose.** | yes, and it reverses on close |
| **failed** `8 → 7` | **−1** | `tests/test_goal_baseline_is_a_card.py::test_a_real_epic_plans_judged_baseline_cannot_be_re_opened` was red at base and is green at the tip. **`SS-03` rewrote that test and its subject baseline between the two trees.** **Numerator fell; NOT this ticket's repair and not claimed as one.** | **no** |
| **passed** `1509 → 1525` | **+16** | `+15` newly collected nodes (11 `SS-03`, 4 workspace) `+1` the red `SS-03` cleared. | mixed, attributed above |
| **skipped** `0 → 0` | 0 | the four `CA-10-DF-12` skips were already gone at the base | — |
| **xfailed** `1 → 1` | 0 | `SS-01`'s `xfail(strict=True)` pinning `SS-01-DF-01`, unchanged | — |

**Nothing is unattributed, and the remaining seven reds are BYTE-IDENTICAL sets
at base and tip** — `test_architecture_tags::test_the_same_tag_control_holds`,
two `test_instrument_demonstrations` rows, three `test_source_citations`
manifest rows, and `test_ticket_retirement`, which is the expected self-clearing
one (*"ticket … is not closed: status=planned"*). **This ticket added no red and
repaired none.** `GOAL-tree-stabilizes` contribution: **guard, no measurable
movement attributable to `SS-07`.**

### Contamination disclosed rather than assumed

**The first base run was contaminated and is published anyway.** The `WT` run at
`48f9c7e` started before this ticket's first file was written, and
`stranded_loaders.py` landed under `specs/results/scorecards/` about nine minutes
into it — **the exact mistake `operational_rules_this_project_has_paid_for` names
and that six parties made in one epic, starting with an owner.** It was caught,
and cell `A` exists to answer it: a fresh detached worktree of the same commit,
untouched for its whole run. **Both give `8 / 1509 / 0 / 1 / 1518` and the same
eight failing test IDs, so the contamination moved nothing — but that is a
measured answer, not a defence, and the contaminated run is NOT the figure
quoted.** Cell `A` is. The contaminated transcript is kept as
`evidence/pytest-base-48f9c7e-WT-CONTAMINATED.txt` rather than deleted, because
deleting it removes the record of what was measured.

## 10. Two things the sweep sharpened after the findings were written

**`SS-07-DF-01` is worse than first measured, and the correction is here rather
than by editing the filed row.** Running `index` over **all 18 sealed card
trees** in throwaway cell `B` (reverted; cell `B` `git status` clean afterwards):

- **18** sealed trees, **15** carry a committed `INDEX.md`, **3 carry none**.
- **13 of the 15 are STALE** — only two match what the current `index` emits.
- **The 3 with no `INDEX.md` at all are `close-the-loop-cl03-v4`,
  `close-the-loop-cl03-v5` and `score-drives-validation-sv04` — the card trees of
  results 3 and 4.**
- Spot-checked `architectural-coherence` and `subtract-to-measure-sm05`: same
  shape as the six in §5 — **every score identical**, only the `total` column and
  the tier-word-vs-full-model-ID presentation differ.

**`R-H4` was demonstrated with a FAILING input, not just observed at 0.** In cell
`B`, one sealed card was drifted by a single byte and restored:

```
audit                      0 violation(s)      # before
seal <that card>           REFUSED: these are already sealed and their contents changed.
                             sha256:6c1d81a783050c52 -> sha256:e67426bc7d969422
audit                      1 violation(s)      # drifted
audit (after restore)      0 violation(s)
```

**`seal` refuses drift and names both digests; `audit` moves 0 → 1 → 0 on a
one-byte change.** `R-H4` is executed, not asserted. `evidence/rh4-demonstrated-with-a-failing-input.txt`.

**One observation deliberately NOT filed as a finding.** `check` over the whole
`specs/results/scorecards/` root at `48f9c7e` reports **330 problems over 95
cards**, located entirely in three trees — `reading-discipline` 180,
`subtract-to-measure-sm05` 86, `subtract-to-measure-sm05-greenfield` 64 — and
**none in the eleven trees of the four standing results, which report 0.** The
classes are `RUBRIC-DRIFT`/`SERVED-DRIFT` (older cards scored against an older
rubric, which is `R-H1`/`R-H2` reporting correctly and which `check` itself
annotates *"a filled card is evidence and is not edited"*) and `INVALID`
(citations not in `file:line` form). **That is not obviously a defect and it is
outside this ticket's slice, so it is reported and not filed** — an entry with no
established defect is a hunch.

## 11. The rest of the validation matrix

| entry | command | result at `06cbcce` |
|---|---|---|
| **spec unit** | `python3 scripts/tla_spec_dev.py --spec-root specs run spec-unit-tests` | **`56 passed`**, `spec-unit validation passed for 1 target(s)` |
| **spec unit, ticket-scoped** | `… run spec-unit-tests --ticket SS-07` | **`spec-unit validation passed for 2 target(s)`** — project `current` and `specs/tickets/SS-07/current` |
| **model delta** | `diff -rq specs/tickets/SS-07/{current,desired}` | **byte-identical**, so `model_delta_expectation: none expected` holds and the close-time equality gate would pass |
| **tlc** | — | **`N/A`: no TLC target exists at this tree**, verified by invocation: `run` accepts only `spec-unit-tests` and `effect-conformance`. Owner error in the dispatch template, already filed as `SS-00-DF-05`; nothing was substituted for it |
| **spec graph / graphs** | — | none declared; this ticket changes no `External.tla` surface |

**One extra, run although not required, because it is this epic's own subject
matter.** `run effect-conformance` with no `--cases-dir` exits 1 reporting two
DEAD MODEL SURFACEs — **and then names its own absent input unprompted**:

> *"NOTE: no `--cases-dir` supplied, so no adapter was executed and nothing was
> observed. The dead-surface finding above reflects an empty observation set."*

**That is the absent-input class answered correctly**: the instrument prints a
verdict and, in the same breath, tells the reader the verdict is about an empty
observation set. It is recorded here as a POSITIVE instance beside the negative
ones in §5, not as a red — it is not in this ticket's REQUIRED matrix and no
corpus was supplied to it.

## 12. The decomposition, MEASURED — no step of it is inferred

§9 attributed the movement using a `--collect-only` at the epic tip and closed
the arithmetic exactly. **That left the pass/fail split of `SS-03`'s +11
inferred from the totals, and inferred is not measured**, so the full suite was
then run at `eb2567b` too, in cell `A`, from a fresh start. **It changes no
conclusion and it removes the inference.**

| tree | cell | `SS-07` workspace | failed | passed | skipped | xfailed | collection |
|---|---|---|---:|---:|---:|---:|---:|
| **`48f9c7e`** epic base | **A** | closed | **8** | **1509** | **0** | **1** | **1518** |
| **`eb2567b`** epic tip, post-`SS-03` | **A** | closed | **7** | **1521** | **0** | **1** | **1529** |
| **`06cbcce`** this branch | `WT` | **OPEN** | **7** | **1525** | **0** | **1** | **1533** |

All three sum: `8+1509+0+1 = 1518`; `7+1521+0+1 = 1529`; `7+1525+0+1 = 1533`.

**Split at the boundary that matters — what `SS-03` did, and what `SS-07` did:**

| segment | failed | passed | skipped | xfailed | collection |
|---|---:|---:|---:|---:|---:|
| `48f9c7e → eb2567b` — **`SS-03`'s merge, not this ticket** | **−1** | **+12** | 0 | 0 | **+11** |
| `eb2567b → 06cbcce` — **`SS-07`, everything this ticket did** | **0** | **+4** | **0** | **0** | **+4** |

**`SS-07`'s entire footprint on the tree is `+4` collected and `+4` passed, and
both are `open ticket SS-07` widening parametrized `test_spec_yaml_valid` over
`specs/tickets/SS-07/`. It reverses on close.** Zero reds added, zero reds
repaired, zero skips, zero xfails.

**`SS-03`'s segment, for the record and not for this ticket's credit:**
numerator fell 8 → 7 (`test_goal_baseline_is_a_card::test_a_real_epic_plans_judged_baseline_cannot_be_re_opened`,
which `SS-03` rewrote), denominator rose 1518 → 1529, and passed rose by 12 =
11 newly collected nodes plus the one cleared red.

**The seven reds are a byte-identical set at `eb2567b` and at `06cbcce`.**

`GOAL-tree-stabilizes`, contribution **guard**: **no measurable movement
attributable to `SS-07` beyond the workspace scaffold, and that is the expected
effect stated in the plan.** Evidence: `evidence/pytest-base-48f9c7e-cellA.txt`,
`evidence/pytest-epictip-eb2567b-cellA.txt`, `evidence/pytest-tip-06cbcce.txt`.
