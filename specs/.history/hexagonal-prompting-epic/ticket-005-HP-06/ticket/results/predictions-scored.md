# The sealed predictions, scored

`examples/validation/PREDICTIONS-HP.md` was committed by HP-01 before HP-02,
HP-03, HP-04 or HP-05 was dispatched. **It has not been amended.** This file is
the scoring, kept separate so the sealed file stays sealed.

Vocabulary, as the sealed file defines it: `PASS`, `FAIL`, `SUPERSEDED` (the
instrument turned out not to measure what the prediction assumed — must cite
which instrument and why), `UNMEASURED` (the instrument did not run — must say
why; **not a pass**).

## The scoring

| ID | Prediction | Expected | Observed | Verdict |
|---|---|---|---|---|
| P01 | D3 separates, arm B ≥ 3 from both judges where arm A is 1–2 | UP | arm B **4 / 4**; arm A **2 / 2** | **PASS** |
| P02 | guard relaxation moves off zero under `corpus-neg`, never `suite` | UP from 0 | **3 of 3 under `corpus-neg` on both arms**; 0 of 3 under every other generated instrument | **PASS** |
| P03 | the mapping choice reproduces its measured 30% of the yield: durable-content mutants die under the checking mapping and survive under the silent one, "reproducing the predecessor's 3 of 3 vs 0 of 3" | large mapping gap, near-zero arm gap | mapping gap is **one mutant** (M04): `map-checking` 2 of 2, `map-silent` 1 of 2, on both arms. Arm gap **zero**. | **FAIL** |
| P04 | M08 survives the slice, dies under the whole view | separates | arm A: **KILLED** by `corpus-whole`, **SURVIVED** on both aspect slices. Arm B: not seedable. | **PASS** |
| P05 | the positive control M07 dies everywhere, every arm, every mapping | 100% killed | **arm A: SURVIVES all six generated instruments**, dies only to the suite. Arm B: dies, but only via a broader-reach substitute. | **FAIL** |
| P06 | some artifact reaches D1 ≥ 3 from both judges | UP from a ceiling of 2 | arm B **3 / 3**; arm A **3 / 2** | **PASS** |
| P07 | both arms finish; both ≥ 2 on D4 | both ≥ 2 | shared suite **28 passed** on both; D4 arm B 3/3, arm A 2/2 | **PASS** |
| **N01** | D2 does not separate for arm B, and **"arm B's measured descriptor is not lower than arm A's"** | FLAT or reversed | D2 **2 / 2 on both arms** — flat, as predicted. But the descriptor **is lower**: 123 significant production lines against 147, 11 branches against 13. | **FAIL** |
| **N02** | ordering stays at zero on every *generated corpus*, on both arms | FLAT at 0 for every corpus | M09 **KILLED** by `corpus-whole`, `corpus-slice-led`, `map-silent` and `map-checking` on both arms; survives `corpus-neg` and `corpus-slice-res` | **FAIL** |
| **N03** | D5 does not separate between arms | FLAT | arm B 3 / 3; arm A **4 / 3**. No separation in the treatment's favour; if anything the control is higher. | **PASS** |
| **N04** | the prompt does not move D1; arms within ±1; per-class kill counts differ by at most one cell | within ±1 | D1 arm B 3/3, arm A 3/2 — within ±1. Per-mutant verdicts are **identical on all seven mutants seeded identically into both arms, across all seven instruments — 49 of 49 cells**. The only differing row is M07, whose arm-B seeding is a substitute. | **PASS** |
| **N05** | HP-04's oracle repair moves the mutant matrix by zero cells | FLAT — zero cells | Confirmed at HP-04 from its own committed before/after table: 0 cells. HP-06 verified the record; it did **not** re-run the pre-HP-04 oracle. | **PASS**, with the re-run caveat stated |
| **N06** | the suite produces none of this epic's findings | ZERO from the suite | see the findings-by-channel table in `RESULTS.md` | **PASS** |

**7 PASS, 4 FAIL, 0 SUPERSEDED, 0 UNMEASURED.** Four of the thirteen sealed
predictions were wrong, and **three of the four wrong ones are negative
predictions** — which is the half of the file that exists to catch this project
telling itself something it has already recorded as fact.

## The four that failed, at the length they deserve

### P05 — the positive control is red, and it is the round's most consequential result

P05 is written in the strongest terms in the file: *"If M07 survives, **every
other number in the round is void** and HP-06 reports the instrument as
unciteable rather than reporting kills."*

On arm A it survives every generated instrument. The mechanism is measured, not
guessed: the generator's own parameter-recovery audit reports `UNRECOVERABLE on
this corpus: Reserve(a) -- 0 of 588 cases carry an argument`, so every positive
`Reserve` case is skipped for an unrecovered argument and the fault seeded inside
`reserve()` is never executed. Negative `Reserve` cases *do* run and *do* call
`reserve`, but every one of them is a rejected call that returns before the
mutated line — so they cannot reach it either.

HP-05 measured the same red control on the fixture's reference implementation
and said the `wrong_value` row was not citeable. **One epic later it is still
red, now on a real arm.** Whatever else this round found, this is the thing that
should be fixed before the next one runs.

Reported rather than obeyed to the letter: this file does **not** declare every
number void. `corpus-neg`'s controls are green on both arms and the
guard-relaxation result is carried entirely by that instrument, which never
depends on a positive `Reserve` case. The rows that depend on the whole-view
corpus are reported as a floor under a broken control, and both artifact-Y judges
independently reached the same conclusion and capped D1 for exactly that reason.

### P03 — the direction replicates for the third time; the magnitude does not, again

The mapping is worth **one mutant** on this fixture, on both arms: M04 dies under
`map-checking` and survives under `map-silent` and under the plain whole-view
corpus. M05, the other `durable_content` mutant, dies under every mapping
including none — HP-05 already corrected the owner's claim that M05 was
suite-only, and this reproduces that correction on two more implementations.

So the sealed text — "reproducing the predecessor's 3 of 3 vs 0 of 3" — is false
here, and the "30% of the instrument's yield" figure fails to reproduce as a
proportion for the **fourth and fifth** fixture. The *direction* is now five for
five. **The magnitude is a property of the fixture and must never be quoted as a
property of the mechanism.**

### N02 — ordering was already retracted, and this reproduces the retraction

HP-03 retracted "ordering is structurally invisible to every layer" on
measurement: it is invisible when the modelled thing is a **set**, and this model
represents its ledger as a **sequence**, so a corpus that compares the projected
`ledger` sees the reversal. N02 was sealed before that retraction and is
therefore scored FAIL rather than SUPERSEDED — the instrument measured exactly
what the prediction assumed, and the prediction was wrong.

The split N02 predicted does exist, just not where it said: `corpus-neg` and the
reservations slice cannot see M09, because neither projects the ledger.

### N01 — the treatment arm came out *smaller*, which nobody predicted

N01's reasoning was that ports and adapters are more parts. On the shipped prompt
text the treatment arm is **1 module → 4 modules and 21 public names → but 123
significant production lines against 147, and 11 branches against 13.**

The pilot HP-02 ran on an *earlier draft* of the same prompt measured 274 lines
against 120 and recorded N01 as reproduced. HP-02 deliberately did not re-run
after amending the prompt, and said HP-06 would be the shipped text's first
measurement. It was, and it went the other way. **A prediction confirmed against
a draft is not confirmed against the thing that shipped.**

The judged half of N01 held exactly: D2 is 2 from all four judges, on both arms,
and no judge found a measured simplification in either artifact.

## What the sealed confounds still forbid

Unchanged and not argued away:

1. **Prompt length is not controlled.** 16 lines unique to arm A, 105 unique to
   arm B — 6.6x. **P01's win cannot be attributed to "hexagonal" over "a longer,
   more specific ask."** That needs a third arm this epic does not run.
2. **The reference is not an arm** and appears in no table beside one.
3. **n = 1 feature.** Every result here is about this feature.
4. **The judges are agents**, two of them, of the same model family, reading the
   same anchors. Their agreement is not the independence two people would give.
