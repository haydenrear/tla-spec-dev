# CA-05 — the harvest register, recounted and repaired

Working for the denominator in `GOAL-consumption-obligatory`. The register is
`specs/results/scorecards/close-the-loop/GOAL-loop-closes-once/CL-03/HARVEST-CL-03.md`;
the repair is an **addendum** to it and edits none of `CL-03`'s text.

## 1. The old count verified before it was changed

`grep -cE '^\*\*[A-F][0-9]+\.'` → **38**, ids contiguous, no gaps, no duplicates:

| section | ids | n |
|---|---|---|
| A — the durable record | A1–A7 | 7 |
| B — checks that cannot fail | B1–B6 | 6 |
| C — gates that report clean on broken input | C1–C7 | 7 |
| D — numbers that do not mean what they appear to mean | D1–D7 | 7 |
| E — documentation asserting what the code does not do | E1–E5 | 5 |
| F — the instrument, about itself | F1–F6 | 6 |

**38 was correct.** Independently corroborated inside the ledger by
`CL-04-DF-04`, which enumerates the same ids and the same grep.

## 2. What was missing

**`SV-01-DF-05`** filed three defect classes into `deferred_findings.yaml` on
2026-08-12 and **not** into the register. All three were found by blind judges
scoring `artifact_under_score`; all four judges declined to move a score on any
of them and said why. They are appended as **G1, G2, G3**:

| id | class | judges |
|---|---|---|
| G1 | rejection precedence is pinned by no case — the one requirement `FEATURE.md` numbers | **4 of 4, independently** |
| G2 | the shipped composition root is exercised by no case | 2 |
| G3 | the single byte-reading case normalises CRLF and cannot see a line-ending fault | 1 |

*(A fourth item in the same row — closing tenant A while tenant B holds a live
reservation — is a single missing case, not a class, and was not promoted.)*

## 3. The true denominator, with the movement named

<!-- CA-05-DENOMINATOR-START -->
```
CL-03's sweep, 2026-08-11                    38
appended by CA-05 from SV-01-DF-05          + 3   (G1, G2, G3)
                                            ----
register total                                41
```

**Per `denominator_rule` — which half moved:**

> **THE DENOMINATOR ROSE, 38 → 41. THE NUMERATOR DID NOT MOVE.**
>
> - consumed into program validation: **1 of 38 (2.6%) → 1 of 41 (2.4%)**
> - named by a ledger row: **4 of 38 → 4 of 41**
>
> **No consumption was lost and nothing regressed.** The rate fell purely
> because the register was repaired. A rate that falls on a bookkeeping repair
> was overstated before the repair, not damaged by it.
<!-- CA-05-DENOMINATOR-END -->

## 4. 41 is a FLOOR, and that is the more important sentence

`CL-03` swept **83 cards**. `find specs/results/scorecards -name scorecard.json | wc -l`
at `a6bdf42` → **95**. **Twelve cards have been sealed since the sweep and
nobody has swept them.**

So 41 is what one bounded, reproducible repair yields — **not** what re-running
`CL-03`'s method over 95 cards would yield. Re-running it is CL-03's whole
ticket (four agents, four slices, 800,181 characters of judge prose), and a
cheap imitation would produce a number that *looks* like CL-03's and was not
made the same way — the comparability error `R-H1`/`R-H2` exist to prevent.

**Quoting 41 as "the number of known classes" is the same error quoting 38 was.**
Filed as `CA-05-DF-04`.

## 5. Read the numerator honestly — three of the four are self-inflicted

| class | ledger row | consumed, or committed? |
|---|---|---|
| `A1` | `SV-04` | **CONSUMED** — into program validation; control 3,3 vs treatment 4,4 |
| `E1` | `SV-04-DF-01` | **COMMITTED** — by the very file written to consume `A1`, caught by a judge in the same round |
| `F3` | `SV-04-DF-02`, `CL-04-DF-05`, `SV-04-DF-05` | **COMMITTED** — a blinding leak, this time inside the instrument |
| `F6` | `SV-04-DF-04` | **COMMITTED** — a round's own two judges made contradictory factual claims |

**One class in 41 has been consumed. Three more were re-committed by the
programme that named them.** *"4 of 38 named"* quoted without that sentence
overstates the loop by a factor of four.

**Disclosed, and deliberately not counted:** `SV-04-DF-05` also names the whole
`C` **section** — *"gates that report clean on broken input"* — inside the
scoring toolchain. That is a reference at section granularity, not to any of
`C1`–`C7`, so the count of 4 stands. Recorded so the next census does not have
to decide it twice.

## 6. Four classes checked for a missed citation, and none was found

`C5` (the pricer returning `PRICED` over an inert column), `D2` (the −225/+1677
lines), `F1` (the duplicated `DIMS` derivation) and `B5` (`mutation_check.py`
green with pytest missing) all have ledger rows on the *same defect* —
`RM-05-DF-02`/`CL-02-DF-02`, `RD-02-DF-05`, `CL-03-DF-05`, `RD-03-DF-01`
respectively. **None of them cites the harvest or the class id.** In every case
the citation runs the other way: the harvest cites the ledger row. So they are
**not** consumption and **not** "named by a ledger row"; they are the harvest
recording work that already existed. The count stays 4.

## 7. Method, and its bound

The three additions came from one named ledger row that the prior epic's own
close-out identified as the gap. **This is a bookkeeping repair, not a sweep.**
It cannot find a class nobody filed, and it did not look. Section 4 is the
statement of that bound.
