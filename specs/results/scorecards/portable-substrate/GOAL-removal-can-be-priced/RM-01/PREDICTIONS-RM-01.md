# RM-01 — predictions, sealed before any number existed

**Sealed at `2c0d94e`** (the epic base), before the residual fault was applied to
any tree and before `price_removal.py` was written. Nothing below is edited
after a measurement; every one is answered in `RESULT.md` §"how the predictions
came out", including the ones that were wrong.

The standing rule: **if every prediction passes, that is an ALARM.**

---

## P1 — the shortcut is unsound in the DIES direction

`removal_census.py discriminate` classifies a mutant `NON-DISCRIMINATING` when
some detector that killed it survives the cut. I predict this is **unsound**: a
detector can survive by name and lose the kill, because a removal can replace a
detector's *body* while keeping its node id.

**Prediction: at least one real fault exists on a real removal that
`discriminate` calls `NON-DISCRIMINATING` and that measurably goes
`DIES` → `SURVIVES`.**

## P2 — `RM-01-RF-1` prices non-zero on SM-03's removal

The fault: `tests/test_code_complexity.py` loses its registration in
`instruments.toml` (`paths = []` on the `thermometer-tripwire` row) while the
file stays on disk.

| tree | prediction |
|---|---|
| `bf0fb29~1` (before SM-03's cut) | `registry-enumeration` **DIES** — `required <= enumerated` names the path |
| `bf0fb29` (after) | `registry-enumeration` **SURVIVES** — the derived walk's roots are `scripts` + `examples/validation` and its predicate cannot see a pytest tripwire |

**And `pytest-full` catches it at neither tree.** This is the prediction most
likely to be wrong: a 1300-node suite has many chances to notice.

## P3 — node granularity does NOT rescue the nine catalogue mutants

RD-02 computed `0 of 9` at **detector** granularity. I predict that recomputing
it at **kill-node** granularity — a killing node counts as surviving only if the
node still exists at the removal's head — **still gives 0 of 9**, and that at
most one node in the whole table is lost to a removal.

If this is wrong, RD-02's headline is wrong and that is the louder result.

## P4 — `SM-04-GM-T1` reproduces from an independent implementation

A probe that scaffolds a card with the tree's own `score_tools.py`, alters one
dimension score, and re-runs `check` will report **CAUGHT at `6aac1ec~1`** and
**UNCAUGHT at `6aac1ec`**, on an unsealed card, without importing any of the
test's helpers.

## P5 — the restriction rule is sound only towards SURVIVES

I predict that over the sealed before-table and the three published after-tables
there is **at least one cell** where survivorship predicts `DIES` and the
measurement says `SURVIVES`, and **no cell** where survivorship predicts
`SURVIVES` and the measurement says `DIES`.

The second half is the load-bearing one: it is what makes a before-only reading
of a residual fault admissible.

## P6 — the `[ports.*]` `fake =` fault stays unpriceable, for a different reason

SM-01 declared it `not_seedable` because it cannot be re-run. I predict that
once re-runnability is dropped it is *still* not a price — because the surface
and the capability were removed together, so the fault class is **extinct**
rather than **unwatched**, and an extinct fault class costs nothing in the
currency a gap mutant measures.

If this holds, the famous excluded fault was excluded for the wrong reason and
would have priced at zero anyway.

## P7 — my own ticket will be net-additive

Every epic in this family that called itself a simplification came out
net-additive. I predict RM-01 adds more lines than any removal it prices, and I
predict I will be tempted to classify my own instrument as "product" rather than
"proof" to improve the ratio. Recorded here so the temptation is on the record
before it arrives.
