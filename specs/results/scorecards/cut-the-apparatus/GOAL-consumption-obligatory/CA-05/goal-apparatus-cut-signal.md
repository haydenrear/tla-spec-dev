# CA-05 — GOAL-apparatus-cut local signal (REVISED at the merged epic tip)

Guard goal. `expected_effect: none expected, AND THE HAZARD IS REAL -- this
ticket could add apparatus in the name of measuring apparatus. PRICE anything it
ships.`

Measured on `feature/CA-05` with `origin/epic/cut-the-apparatus` (`4302082`,
CA-02 merged) merged in. **The tree is named in every figure.**

## The declared command

```
$ find scripts examples/validation -name '*.py' -not -path '*/__pycache__/*' | xargs wc -l | tail -1
   42550 total
```

## Per surface, at the RECONCILED tip `e379d6b` (CA-01..CA-04 all merged)

```
                          epic tip e379d6b    HEAD     MY DELTA
scripts/*.py                        26,547  26,760       +213   scripts/disposition.py
examples/validation/*.py            14,854  14,854         +0   NO Python changed
                                    ------  ------
combined                            41,401  41,614       +213

tests/*.py                          30,422  30,635       +213   NOT in the goal metric
instruments.toml                         -       -        +75   TOML, not in the metric
```

**All deltas are `git diff --numstat` against `e379d6b`, not a subtraction of
totals.** The absolute figures fell sharply between review rounds because
**CA-02, CA-03 and CA-04 cut; CA-05 only added.**

## The card, reported separately

```
$ score_tools.py serve | wc -c        -> 6281
$ score_tools.py serve --digest-only  -> sha256:2d7d4a0506d9b259
```

**UNCHANGED at 6,281 bytes. Clause (c) holds.**

## Classification: MOVED THE WRONG WAY, by 213 lines

**Worse than the 133 first reported.** Review added 80 lines to
`scripts/disposition.py`: the `CA-05-DF-06` duplicate-key guard (~32) and the
advisory `channel`-vocabulary check (~18), plus docstring.

Clause (a) asks these surfaces to FALL and this ticket raised `scripts/` by 213.
**Stated plainly rather than buried: the guard goal moved the wrong way and this
ticket is the cause.**

What was bought: a demonstrated refusal on real input (`R1`), and a structural
guard whose failing input is a REAL six-day-old corruption that had defeated
every reader of this file. The alternatives were measured and rejected -- a
`grep` cannot scope to an epic or check the D2/D3 grammar, and putting the file
in `tests/` where the metric does not count it would have been metric-dodging.

## Clauses (b), (c), (d)

- **(b) every deletion names its finding** -- 13 line deletions in the ledger:
  **7** are the `CA-05-DF-06` repair, **6** are `channel` reshapes whose prose is
  preserved verbatim in `channel_note`. **No finding row deleted, no prose lost**
  (226 -> 232 rows, verified row-by-row).
- **(c)** card unchanged at 6,281 / `sha256:2d7d4a0506d9b259`.
- **(d)** surfaces reported separately, tree named, never combined with the card.
