# Scorecards — hexagonal-prompting, EVAL-RERUN (repaired instrument)

scorecard_version 1. See `references/eval_scorecard.md`.

**This run supersedes `../hexagonal-prompting/` on the rows the instrument
repair invalidated. That run is sealed and is not edited.** Unblinding key:
`UNBLINDING.md` — `P` is arm A (the ordinary ask), `Q` is arm B (the hexagonal +
minimize-complexity ask). The letters are deliberately not HP-06's.

**Never average across examples.**

| example | arm | D1 bug detection | D2 complexity | D3 modularity | D4 behavior preservation | D5 honesty | total | contested |
|---|---|---|---|---|---|---|---|---|
| ab_quota_ledger | P | 3 | 2 | 2 | 2 | 3 | **12**/20 | — |
| ab_quota_ledger | P | 3 | 2 | 2 | 2 | 2 | **11**/20 | — |
| ab_quota_ledger | Q | 3 | 2 | 4 | 3 | 4 | **16**/20 | — |
| ab_quota_ledger | Q | 3 | 2 | 4 | 2 | 3 | **14**/20 | — |

Schema check: `4 scorecard(s) checked, 0 problem(s)`. Maximum spread across the
ten independent scores is 1; **zero dimensions contested**; no third pass run.

- **ab_quota_ledger** (20260804-rerun-P-p1): A clean, genuinely content-asserting single-module implementation whose own tests reach ordering and refusal faults every generated instrument misses, but whose headline "long randomized model-based sweep" is degenerate — 400 steps accept 1 reserve, 1 commit and 0 releases, so it cannot fail on release at all.
- **ab_quota_ledger** (20260804-rerun-P-p2): A disciplined, correct single-module implementation whose hand-written tests genuinely reach refusals and ordering that the generated corpus cannot — but its headline 400-step randomized sweep accepts only 5 commands and zero releases, so fix that degeneration before trusting any coverage claim this artifact makes about itself.
- **ab_quota_ledger** (20260804-rerun-Q-p1): Ship it as the modularity reference for this example: a one-line adapter swap that I ran keeps the full 28-case contract green with the domain byte-identical and zero filesystem calls, and all four of its self-reported defects reproduce exactly as written — but do not read its D2 as a simplification result.
- **ab_quota_ledger** (20260804-rerun-Q-p2): Accept this implementation but do not treat its port contract as demonstrated: its own 53 cases kill 11 of 11 seeded faults including the ordering control that survives every generated instrument, yet a tenant name containing a newline silently splits one COMMIT into two ledger lines (R2/R5 broken, undisclosed, caught by nothing), and the two Journal implementations disagree on newline and empty records.
