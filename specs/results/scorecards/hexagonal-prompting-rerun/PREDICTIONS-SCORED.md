# The sealed predictions, scored on the REPAIRED instrument

`examples/validation/PREDICTIONS-HP.md` was sealed by HP-01 before any ticket was
dispatched. **It has not been amended.** This file scores it against EVAL-RERUN,
and **prints HP-06's verdict beside every row where the two differ** — the point
of a re-run on a repaired instrument is that the disagreements are the result.

Vocabulary, as the sealed file defines it: `PASS`, `FAIL`, `SUPERSEDED` (the
instrument turned out not to measure what the prediction assumed — must cite
which instrument and why), `UNMEASURED` (the instrument did not run — must say
why; **not a pass**).

## The scoring

| ID | Prediction | EVAL-RERUN observed | verdict | HP-06 said |
|---|---|---|---|---|
| P01 | D3 separates, arm B ≥ 3 from both judges where arm A is 1–2 | arm B **4 / 4**; arm A **2 / 2** | **PASS** | PASS |
| P02 | guard relaxation moves off zero under `corpus-neg`, never `suite` | **3 of 3 under `corpus-neg` on both arms**, 0 of 3 under every other generated instrument. On a fresh blind catalogue, **three** classes are corpus-neg-only | **PASS** | PASS |
| P03 | the mapping reproduces its measured 30% of the yield | mapping gap is **one mutant** (M04), arm gap **zero**, on both arms — the seventh fixture on which the direction replicates and the magnitude does not | **FAIL** | FAIL |
| P04 | M08 survives the slice, dies under the whole view | **KILLED** by `corpus-whole`, **SURVIVED** on both aspect slices, **on BOTH arms** | **PASS** | PASS (arm A only — arm B was not seeded) |
| P05 | the positive control M07 dies everywhere | **arm A: KILLED on all five instruments that execute an accepted `Reserve`**, `NOT_DECIDABLE` on two, **no SURVIVED cell**. Arm B: killed on six — but see the two qualifications below | **PASS** | **FAIL** |
| P06 | some artifact reaches D1 ≥ 3 from both judges | **both arms 3 / 3** | **PASS** | PASS |
| P07 | both arms finish; both ≥ 2 on D4 | shared suite **28 passed** on both; D4 arm A 2 / 2, arm B 3 / 2 | **PASS** | PASS |
| **N01** | D2 does not separate, and **"arm B's measured descriptor is not lower than arm A's"** | D2 **2 / 2 / 2 / 2**, flat. Descriptor: arm B is **larger on every figure that differs** — 129 lines to 122, 11 branches to 10, 4 modules to 1, 25 public names to 20 | **PASS** | **FAIL** |
| **N02** | ordering stays at zero on every generated corpus, both arms | M09 **KILLED** by `corpus-whole`, `corpus-slice-led`, `map-silent` and `map-checking` on both arms | **FAIL** | FAIL |
| **N03** | D5 does not separate between arms | arm A **3 / 2**, arm B **4 / 3** — the treatment is one anchor higher on both judges | **FAIL** | **PASS** |
| **N04** | the prompt does not move D1; per-class kill counts differ by at most one cell | D1 **3 / 3 on both arms**. One differing cell in 77 on the sealed catalogue, and it is the cell the catalogue declares incomparable; **56 of 56 strictly comparable cells identical**. Two differing cells on the blind catalogue, both on rows its author declared non-parallel | **PASS** | PASS |
| **N05** | HP-04's oracle repair moves the mutant matrix by zero cells | the pre-HP-04 oracle was **not run** this round | **UNMEASURED** | PASS |
| **N06** | the suite produces none of this epic's findings | **0 from re-running the suites** — 986 repo tests, 28 + 28 shared, 32 + 53 the arms' own, all green, no fact about the toolchain. But see the counter-example below | **PASS**, with a first-in-three-rounds caveat | PASS |

**8 PASS, 3 FAIL, 0 SUPERSEDED, 1 UNMEASURED.**

**Three rows moved against HP-06, and all three are the interesting kind.**

## P05 — the row this whole re-run exists for, and it flips

HP-06 scored P05 **FAIL** in the strongest terms the sealed file allows: M07
survived all six generated instruments on arm A, because parameter recovery
reported `Reserve(a) -- 0 of 588 cases carry an argument` and no case that called
`reserve` ever executed.

On the repaired generator, recovery is **4,028 of 4,028**, **294 accepted
`Reserve` cases execute**, and **arm A's M07 has no SURVIVED cell anywhere.** The
faithful seeding — byte-for-byte the sealed catalogue's `-= amount + 1` — dies on
`corpus-whole`, `corpus-slice-res`, `map-silent`, `map-checking` and `suite`.

**Two qualifications travel with the PASS and must never be separated from it.**

1. **It is not literally "100% killed".** Two cells are `NOT_DECIDABLE`, and
   the adversarial channel showed (F3) that one of the two limitations is
   "verified" against a **missing dictionary key** rather than a measured zero,
   and (F2) that the limitation mechanism can convert a demonstrated kill into
   `NOT_DECIDABLE` with `verified: true` and exit 0. The suppression is
   *plausible* on arm A and *unaudited*.
2. **Arm B's M07 is not a valid positive control at all.** Delete every `Reserve`
   case from the corpus — HP-06's exact regression — and arm A's M07 correctly
   goes SURVIVED while **arm B's stays KILLED**, because the broader-reach
   substitute is detectable through `CloseTenant` on a state with no live
   reservation. Arm B's whole-view rows are not backed by a working control.

So the honest sentence is: **the failure P05 recorded is fixed on the arm where
P05 could be tested faithfully, and the arm-B column of the same row is not
evidence about anything.**

## N01 — the same prediction, opposite verdicts, from the same prompt text

HP-06 measured its treatment arm at **123 production lines against 147** and
scored N01 FAIL. This round measures **129 against 122** — the other way — and
scores it PASS. Same two prompt files, same feature, same rubric, four different
agents.

**This is the strongest single piece of evidence in either round that a
descriptor delta between one pair of artifacts is noise at this scale.** The
judged half of N01 has now held twice (D2 flat at 2 across eight independent
judges); the descriptor half has gone both ways. Nobody should quote either
direction as a property of the prompt.

## N03 — D5 separated, and the sealed file says to suspect the judges first

N03 predicted D5 would be flat, and instructed that if it separated, *"the most
likely explanation is not that one prompt produced a more honest program — it is
that the judges worked out which arm they were reading."* That explanation was
considered first, and it does not fit:

- Both artifact-Q judges **declined to infer the arm** and recorded that they
  treated the artifact's polish as grounds for suspicion rather than credit.
- The separation is driven by the **control** arm being marked DOWN on executed
  evidence, not by the treatment being marked up on prose. Two judges
  independently instrumented artifact P's flagship
  `test_rules_hold_through_a_long_random_sequence` — which advertises 400
  randomized commands against an independent model — and found that on
  **unmutated** code it accepts about 1 reserve, 1 commit, 0–1 releases and 3
  closes before every tenant closes and the remaining ~390 steps bounce off a
  closed ledger. Its own anti-degeneracy guard passes on the degenerate run it
  was written to prevent.
- Artifact Q's D5 = 4 was earned by a judge **reproducing all four of its
  self-declared limits**, including injecting a raising `Journal.append` and
  confirming that `committed('acme') == 3` against an empty journal — R2
  genuinely broken, exactly as the artifact says.
- And the judge that gave Q a 3 rather than a 4 did so because it **falsified**
  one of Q's own claims: the fake and the real adapter are not contract-
  equivalent (`'A\nB'` and `''` diverge).

**D5 separated because one artifact certified something false about itself and
the other did not, and both were checked by running them.** That is the
dimension working, and N03 is still FAIL.

## N06 — passes, and for the first time in three rounds it has a counter-example

Re-running the suites produced **zero** findings, for the third round running.

But the hand-written suite **as a kill-table instrument** produced this round's
first defect. EVAL-RERUN-DF-01 — a stale module reference that made all eleven
mutants execute against pristine code and report SURVIVED — was caught because
the `suite` column killed 10 of 11 while all six generated columns killed 0. **A
green positive control did not catch it. Six generated instruments did not catch
it. The disagreement between a hand-written instrument and a generated one
did.**

That is not what N06 measures, and N06 stands as PASS on its own terms. It is
recorded here because "the suite has stopped being informative" is a sentence
this project has now written twice, and this round is the first evidence against
it.

## What the sealed confounds still forbid

Unchanged and not argued away:

1. **Prompt length is not controlled.** Recomputed on the shipped files: **16
   lines unique to arm A, 105 unique to arm B — 6.6x**, on 38 shared. P01's win
   **cannot** be attributed to "hexagonal" over "a longer, more specific ask".
   Two rounds have now produced D3 = 4 without ever testing that distinction.
2. **The reference implementation is not an arm** and appears in no table beside
   one.
3. **n = 1 feature.** Every result here is about this feature.
4. **The judges are agents** — four of them, all `claude-opus-5[1m]`, reading the
   same anchors. Their agreement is not the independence four people would give.
   Rule 4 (prose quality is never an input) is the one rule nothing mechanical
   can enforce; all four judges addressed it explicitly and two said the writing
   tempted them.
