# PREDICTIONS-SM, scored by SM-05

**The sealed file is `examples/validation/PREDICTIONS-SM.md` and it is NOT
amended.** Verified unmodified: `check_prediction_seal.py` reports sealed at
`b2b8e9c`, 51 of 51 records pre-date the seal, 12 sections parsed; and the file
has exactly one commit in its entire history (`b2b8e9c`, *"SM-01: seal the
predictions, before any number exists"*).

| ID | claim | instrument | verdict | why |
|---|---|---|---|---|
| **P01** | fake-side fault dies to the suite, not the binding | gap mutants | **PASS** | scored at SM-01. **ENTAILED and labelled so** — it is the contrast row for `N01`, not news |
| **P02** | manifest drift is the machinery's unique catch | gap mutants | **FAIL** | predicted `SURVIVES` on `pytest-full`; it **DIES** on three nodes, two of which outlive SM-02 |
| **P03** | `complexity-ledger` is redundant with the suite | gap mutants | **FAIL** | predicted `DIES` on both; **SURVIVES** both. SM-01 recorded the cause as a defect in its own mutant, not a finding about the row |
| **P04** | the enumeration check cannot see an omission | gap mutants | **PASS** | **ENTAILED and labelled so.** It became SM-03's acceptance test and is now `DIES` on both detectors |
| **P05** | "not constructible" is about the runner | gap mutants | **FAIL** on its second half | the tripwire dies as predicted; `instrument-registry` **also** dies, so the runner's limitation is reachable after all |
| **P06** | hollow slots blind to VACUOUS, not to MISSING | gap mutants | **PASS** | the split is exact, and it is the sharpest non-entailed pass in the file |
| **N01** | the `[ports.*]` machinery prices at ZERO on behaviour | gap mutants, before vs after | **PASS** | **confirmed on the integrated tip.** Stated falsifier: either ports mutant `DIES` on a `corpus-port-swap:*` column at SM-01 and `SURVIVES` on every one of `pytest-full`, `suite-real`, `suite-fake` at SM-05. **No such cell exists.** `SM-GM-P1`'s one machinery `DIES` is matched by `suite-fake` (28 executed) and `pytest-full` (1386); `SM-GM-P3` had no machinery `DIES` to lose |
| **N02** | the suite yields zero findings again | channel accounting | **PASS** | zero, for the **sixth round in seven** |
| **N03** | `scripts/` `code_lines` stays above 20189 | `code_complexity.py` | **PASS** | **21027** — a fall of 225, **1.06 %**. One command, no interpretation, exactly as the row asked |
| **N04** | `D2` does not reach 4 | 2 blind judges | **FAIL** | stated falsifier: *"either judge returning D2 = 4."* Judge `K-p3` scored **D2 = 4**, tying it to D4 = 3 as anchor 4 requires, with a named refusal |
| **N05** | `D3` moves zero cells on the removal | 2 blind judges | **SUPERSEDED** | see below |
| **N06** | nothing watches the enumerator's exit code | gap mutants | **FAIL** | scored at SM-01; two nodes in `test_instrument_demonstrations.py` watch it |

## 6 PASS, 5 FAIL, 1 SUPERSEDED — **NO ALARM**

`FI-04` scored 8 of 8 with four structurally unfalsifiable negatives, and `FI-06`
correctly called that an alarm. **This file is not that.** Five rows were refuted
by a run, **two of them negatives** (`N04`, `N06`), and the two passes among the
positives that were not entailed reduce to `P06`. Both remaining entailed rows
(`P01`, `P04`) said so in their own text before any number existed.

## Why `N05` is SUPERSEDED and not PASS

`N05` reads: *"`D3` scores the same on the removal as its **last sealed value**,
from both judges. Zero movement."* Its stated falsifier is *"any `D3` cell
differing from the last sealed value."*

**The removal subject is a NEW example.** `toolchain_removal` had no card before
this round, so "its last sealed value" names a value that never existed and the
falsifier cannot be evaluated as written. **The instrument turned out not to
measure what the prediction assumed** — which is exactly what the sealed
vocabulary defines `SUPERSEDED` for, and the instrument named is the sealed card
history under `R-H2`, which has no row for an example that has never been scored.

**Scoring it PASS would have been the flattering error.** D3 did not "move" on
the removal because there was nothing for it to move from, and counting that as a
confirmed negative is how a round reaches 8-of-8 and measures nothing.

**What is reported in its place, because `N05` is the row whose failure was to
outrank the headline:**

- **On the removal, D3 spans 2 → 4 across four judges and is `contested` under
  scoring rule 5.** The two-point pair is `K-p2` = 2 against `K-p3` = 4, and both
  judges state no new evidence can settle it — the disagreement is about what the
  artifact *is*, not about the code.
- **On the greenfield control — the same example as ten prior cards — D3 moved
  one point at the lower judge tier** (`S-p3` = 1 against a sealed 2). Declared as
  `[[movement]] sm05-gf-D3-low-tier` in `INSTRUMENT-LOG.toml` and re-derived by
  `audit`.

**D3 did not hold, and it is reported first in `RESULT.md` for that reason.**
`SM-05-DF-06`.
