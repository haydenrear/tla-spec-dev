# Scorecards — falsifiable-instruments-rescore-v1

scorecard_version 1. See `references/eval_scorecard.md`.

**Never average across examples.** `ex6_jenga` is a deliberately
incoherent fixture and is supposed to score low on D3; averaging it
with `ex4` produces a number about nothing. Nothing in this file is
computed across two examples.

| example | arm | D1 bug detection | D2 complexity | D3 modularity | D4 behavior preservation | D5 honesty | total | contested |
|---|---|---|---|---|---|---|---|---|
| ab_quota_ledger | T | 3 | 2 | 4 | 3 | 3 | **15**/20 | — |
| ab_quota_ledger | T | 3 | 2 | 4 | 4 | 3 | **16**/20 | — |
| ab_quota_ledger | U | 3 | 2 | 2 | 3 | 3 | **13**/20 | — |
| ab_quota_ledger | U | 3 | 2 | 2 | 4 | 3 | **14**/20 | — |
| ab_quota_ledger | W | 3 | 2 | 1 | 3 | 4 | **13**/20 | — |
| ab_quota_ledger | W | 3 | 2 | 1 | 4 | 4 | **14**/20 | — |

- **ab_quota_ledger** (20260806-v1-T-p1): The only artifact of the three where a driven port exists in fact -- the domain imports nothing that does I/O, the swap is one expression at quota_ledger/__init__.py:39, and one case list passes against a real and a fake adapter with a run-time cell to prove the fake was really bound -- but every bug-detection number it carries belongs to the shared harness under a red positive control, so read its D3 and ignore its D1 as a ranking.
- **ab_quota_ledger** (20260806-v1-T-p2): The only artifact of the three that is ports-and-adapters in fact -- a declared port, two working implementations, and a swap demonstrated at runtime rather than by import topology -- so take T when the boundary is what you need; do not read its D2 as a simplification result, because no before/after figure exists anywhere for it.
- **ab_quota_ledger** (20260806-v1-U-p1): A clean single-module implementation with a real filesystem boundary that is hard-wired rather than swappable -- `_LedgerFile` is constructed by the class that uses it at quota_ledger.py:110, so no adapter can be replaced without editing the domain -- carried by the strongest self-written check of the three, a 400-step randomized sweep rechecking R1/R2/R3 against an independent model after every command.
- **ab_quota_ledger** (20260806-v1-U-p2): Take U for detection, not for the boundary: it has the strongest oracle of the three -- a 400-step randomised sweep that recomputes R1, R2 and R3 against the file on disk after every single command -- but the rules construct their own file adapter from a path, so nothing about the durable side can be replaced or faked without editing the class that holds the rules.
- **ab_quota_ledger** (20260806-v1-W-p1): The most honest record of the three -- it discloses one of its own tests as vacuous and one of its own branches as never executed, at the sites of both -- attached to the least modular code, where the class holding the rules opens the ledger file in three separate places and there is no port to swap.
- **ab_quota_ledger** (20260806-v1-W-p2): W is the smallest artifact and keeps the most honest record of the three -- its notes withhold precisely the claims its inputs cannot support -- but it has no boundary at all: three of its own methods touch the ledger path directly, so nothing about the durable side can be swapped, faked or tested apart from the rules.
