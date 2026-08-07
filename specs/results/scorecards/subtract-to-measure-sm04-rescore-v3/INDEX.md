# Scorecards — subtract-to-measure-sm04-rescore-v3

scorecard_version 3. See `references/eval_scorecard.md`.

**Never average across examples.** `ex6_jenga` is a deliberately
incoherent fixture and is supposed to score low on D3; averaging it
with `ex4` produces a number about nothing. Nothing in this file is
computed across two examples.

**No total, from scorecard_version 3.** Four of its five terms cannot
carry a delta, so a sum over them moves most where the card reads
worst. Read a dimension.

| example | arm | D1 bug detection | D2 complexity | D3 modularity | D4 behavior preservation | D5 honesty | contested |
|---|---|---|---|---|---|---|---|
| ab_quota_ledger | R | 3 | 2 | 2 | 3 | 3 | — |
| ab_quota_ledger | R | 3 | 2 | 2 | 4 | 2 | — |

- **ab_quota_ledger** (20260806-sm04v3-R-p1): A small, honest, correctly-seamed single module whose own cases reach an ordering class the shared suite structurally cannot, but which is not ports-and-adapters and does not claim to be, measures no complexity, and leaves two behaviors it states in prose — the accepted-release reservation_id and the unknown-tenant refusal — pinned by no case at all, as my own seeded faults demonstrated.
- **ab_quota_ledger** (20260806-sm04v3-R-p2): A single-module implementation whose behavior checking is genuinely strong -- an invariant sweep I demonstrated capable of failing on five of six faults I seeded myself -- sitting on a design with a real I/O seam but no injectable port, and whose stated honesty policy is contradicted three lines from where it is declared by `is_closed('nobody') == False`.
