# A DELIBERATE FAILING INPUT. NEITHER FILE HERE IS A CLAIM.

`same_line.md` and `wrapped.md` contain **the same sentence**, differing only in
where the line breaks. The sentence is true: on the example `ab_quota_ledger`,
all 10 cards of the subject `arm_b` — the only `ports-and-adapters` subject that
example has — carry D3 = 4.

```
python3 examples/validation/scorecards/score_tools.py scope --path <this dir>/same_line.md
python3 examples/validation/scorecards/score_tools.py scope --path <this dir>/wrapped.md
```

| file | verdict |
|---|---|
| `same_line.md` | `UNREACHABLE` — unresolved qualifier |
| `wrapped.md` | **`REFUTED`** — population 35, 25 counterexamples named, every one of them a card about a **different subject** |

**`wrapped.md` is the one `REFUTED` figure this ticket adds to the record.** It is
a probe, not an assertion, and it is the demonstrated failing input for
`RD-04-DF-01` — the same way `score_tools.py scope` itself ships exiting non-zero
on this repository's own record.

**Denominator rule.** The repository-wide `scope` sweep moved from 19 `REFUTED`
(RD-01's baseline) to 20. **The numerator rose by exactly one and this file is
it.** No newly discovered false claim in the record is behind that move, and the
other seven figures RD-04 adds are 3 `HOLDS` and 4 `UNREACHABLE`.

Do not delete these files to make a count go down. That is the move the workflow
forbids.
