# `GOAL-consumption-obligatory` — baseline

**Measured at the epic base `08d1d6a90ad2638cdfceee7cc2e150732daa3438`.**

---

## The figures, and the second row is the one to read first

| | value |
|---|---|
| harvest classes **consumed into program validation** | **1 of 38 (2.6%)** — class `A1`, by `SV-04` |
| harvest classes named by a ledger row | **4 of 38** — `A1`, `E1`, `F3`, `F6` |
| new judge-found classes filed but unconsumed | 5 |
| `HARVEST-CL-03.md` | **38 classes — untouched through the whole of the last epic** |

**Read the second row before quoting the first: three of the four newly-named
classes are this project catching itself committing the class**, not consuming
it.

## The denominator is wrong and everybody is quoting it anyway

`SV-01-DF-05` filed **three new defect classes** into the ledger and **not** into
the harvest. **So 38 stopped growing on 2026-08-11 and now understates the
backlog.** Every future *"1 in 38"* is measured against a register nobody
maintains.

`denominator_rule` applies with force to this goal: **if the count moves, say
whether the numerator rose or the denominator fell.**

## Two fields, asked for and never built

| field | asked for | status at the epic base |
|---|---|---|
| `channel` on the ledger | **six epics ago** | **absent.** Every findings-by-channel table in the record is a hand classification of free text |
| `cost` block (`basis` + `value`) at ticket close-out | `CL-04`, **three epics ago** | **absent.** One ticket of six recorded a token basis last epic |

`SV-05`'s own, basis named: `subagent_tokens` over four blind dispatches,
**353,816 tokens, 2 findings from that channel, 0.57 per 100k** — comparable to
`SV-01`'s **0.98** on the same basis. **That is the first time two rounds in this
programme have been comparable at all, and it is the whole argument for naming a
basis.**

## The diagnosis, in the owner's words

> *Detection, filing, scoring and re-scoring all work. Consumption is 1 of 38
> because nothing requires it. Either a filed finding must receive a disposition
> before an epic can close, or the honest description is a measurement programme
> rather than a self-improvement loop. Both are respectable; the current state is
> neither.*

## The target

**NO TARGET ON THE RATE ITSELF.** A threshold on a consumption number before the
mechanism exists would be `MF-020` — fitting a measure to a known answer — and
the mechanism is what is being built. Four clauses:

1. A disposition requirement exists, is exercised on this epic's own findings,
   and has a **demonstrated refusal on a real input** (`R1`), not a fixture.
2. The register is repaired, the **true denominator** stated, numerator/
   denominator movement named.
3. `channel` and `cost` exist and are populated **by this epic's own tickets**.
4. If a clause cannot be met, **the honest alternative is stated**: a measurement
   programme rather than a self-improvement loop. **Silence is not an option.**

## Evidence sources

- `specs/results/scorecards/close-the-loop/GOAL-loop-closes-once/CL-03/HARVEST-CL-03.md`
- `specs/results/scorecards/SELF-IMPROVEMENT.md` (1,602 lines)
- `specs/results/scorecards/score-drives-validation/SV-05/RESULT.md` §7 and §9
