# Scorecards — falsifiable-instruments-rescore-v2

scorecard_version 1. See `references/eval_scorecard.md`.

**Never average across examples.** `ex6_jenga` is a deliberately
incoherent fixture and is supposed to score low on D3; averaging it
with `ex4` produces a number about nothing. Nothing in this file is
computed across two examples.

| example | arm | D1 bug detection | D2 complexity | D3 modularity | D4 behavior preservation | D5 honesty | total | contested |
|---|---|---|---|---|---|---|---|---|
| ab_quota_ledger | T | 3 | 2 | 4 | 3 | 3 | **15**/20 | — |
| ab_quota_ledger | T | 3 | 2 | 4 | 4 | 4 | **17**/20 | — |
| ab_quota_ledger | U | 3 | 2 | 2 | 4 | 3 | **14**/20 | — |
| ab_quota_ledger | U | 3 | 2 | 2 | 4 | 4 | **15**/20 | — |
| ab_quota_ledger | W | 3 | 2 | 1 | 3 | 4 | **13**/20 | — |
| ab_quota_ledger | W | 3 | 2 | 1 | 3 | 4 | **13**/20 | — |

- **ab_quota_ledger** (20260806-v2-T-p1): A real port with two working implementations — I changed one line, left the domain byte-identical, and the shared suite passed 28/28 against the fake — wrapped around a 53-case suite that let the feature's declared rejection ORDER walk straight past it, so trust this artifact's boundary further than its coverage.
- **ab_quota_ledger** (20260806-v2-T-p2): Ports and adapters in fact rather than in prose -- one declared port, a real and a fake implementation, and one case list I confirmed by execution runs against both -- so treat T as this round's reference for D3; its ceiling is D2, where the simplification is argued and never measured.
- **ab_quota_ledger** (20260806-v2-U-p1): The strongest checks of the three against faults I seeded myself -- 4 of 4 caught, each by a distinct named case -- but every one of those kills is hand-written and the randomized model sweep it advertises executes one accepting commit in four hundred commands, so read what its cases assert and not what its docstrings claim.
- **ab_quota_ledger** (20260806-v2-U-p2): The only artifact carrying its own model-derived check -- a 400-command randomized sweep that recomputes R1/R2/R3 from the bytes on disk, which I confirmed fails under a seeded fault -- but its durable seam is a private class it constructs itself, so there is no swap to name and D3 stops at 2.
- **ab_quota_ledger** (20260806-v2-W-p1): The most honest record of the three -- it names its own unreachable code and refuses two claims it cannot support -- wrapped around the least separable design, whose single durable-content assertion I broke without it noticing because that assertion's amount and running total are the same number.
- **ab_quota_ledger** (20260806-v2-W-p2): The most honest record of the three and the least modular code -- no port, file I/O in three places inside the rules class -- and its own eleven cases went green under a cross-aspect fault that both other artifacts' suites caught, so read its clause-by-clause account as an accurate map of what the SHARED suite checks rather than of what W checks.
