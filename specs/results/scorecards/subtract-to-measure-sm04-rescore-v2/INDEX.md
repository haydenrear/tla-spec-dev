# Scorecards — subtract-to-measure-sm04-rescore-v2

scorecard_version 2. See `references/eval_scorecard.md`.

**Never average across examples.** `ex6_jenga` is a deliberately
incoherent fixture and is supposed to score low on D3; averaging it
with `ex4` produces a number about nothing. Nothing in this file is
computed across two examples.

**No total, from scorecard_version 3.** Four of its five terms cannot
carry a delta, so a sum over them moves most where the card reads
worst. Read a dimension.

| example | arm | D1 bug detection | D2 complexity | D3 modularity | D4 behavior preservation | D5 honesty | contested |
|---|---|---|---|---|---|---|---|
| ab_quota_ledger | H | 3 | 2 | 2 | 2 | 3 | — |
| ab_quota_ledger | H | 3 | 2 | 2 | 3 | 3 | — |

- **ab_quota_ledger** (20260806-sm04v2-H-p1): A disciplined, content-asserting single-module implementation whose hand-written cases reach refusal and ordering classes the shared corpus cannot, but whose one model-flavoured check is nearly vacuous — 400 commands, 395 rejections, zero accepted releases — and consequently misses an R1 conservation break that the shared suite catches.
- **ab_quota_ledger** (20260806-sm04v2-H-p2): A small, honest, well-partitioned implementation whose durable seam is real but unswappable and whose flagship model-based sweep is nearly inert -- it accepts 5 of 400 commands and never an accepting release, and a conservation-breaking double refund survives its entire own suite.
