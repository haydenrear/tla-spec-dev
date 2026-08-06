# Scorecards — ports-as-adapters

scorecard_version 1. See `references/eval_scorecard.md`.

**Never average across examples.** `ex6_jenga` is a deliberately
incoherent fixture and is supposed to score low on D3; averaging it
with `ex4` produces a number about nothing. Nothing in this file is
computed across two examples.

| example | arm | D1 bug detection | D2 complexity | D3 modularity | D4 behavior preservation | D5 honesty | total | contested |
|---|---|---|---|---|---|---|---|---|
| ab_quota_ledger | T | 4 | 2 | 4 | 4 | 4 | **18**/20 | — |
| ab_quota_ledger | T | 3 | 2 | 4 | 4 | 4 | **17**/20 | — |
| ab_quota_ledger | U | 4 | 2 | 2 | 4 | 4 | **16**/20 | — |
| ab_quota_ledger | U | 3 | 2 | 2 | 4 | 4 | **15**/20 | — |
| ab_quota_ledger | W | 3 | 2 | 1 | 3 | 4 | **13**/20 | — |
| ab_quota_ledger | W | 3 | 2 | 1 | 3 | 4 | **13**/20 | — |

- **ab_quota_ledger** (20260805-T-p1): The only artifact of the three with a real port -- I replaced the entire durable side by editing one line outside the domain and all 28 baseline behaviors held with no file touched; treat its four-module shape as bought, not spent.
- **ab_quota_ledger** (20260805-T-p2): Ship it -- the port is real and I proved it by running the whole unmodified shared suite against the in-memory adapter with the domain untouched -- but treat every SURVIVED cell in its packet as a floor, because the run's positive control decided nothing on this artifact.
- **ab_quota_ledger** (20260805-U-p1): The best oracle of the three -- an independent model re-checked against the bytes on disk after every one of 400 commands -- wrapped around a design with no port at all, so its durable side can only be swapped by rebinding a private module global.
- **ab_quota_ledger** (20260805-U-p2): A correct single-module implementation with the strongest self-owned oracle of the three -- a 400-step randomized sweep that recomputes R1/R2/R3 from disk after every command -- but its durable side is constructed inside the domain, so swapping it means editing the domain or monkeypatching a private global, and that is a seam, not a port.
- **ab_quota_ledger** (20260805-W-p1): The most honest record of the three attached to the least structured code -- believe every caveat it makes, and do not let its brevity read as discipline, because its own tests miss the cross-aspect and refusal faults that the other two catch.
- **ab_quota_ledger** (20260805-W-p2): The most honest record in the round and the smallest code, but there is no boundary at all between the rules and the file -- truncate, read and append all happen inside the domain class, no substitution is possible -- and its own eleven tests cannot see a stale R2 running total, which I confirmed by mutating it.
