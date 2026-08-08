# Scorecards — subtract-to-measure-sm05-greenfield

scorecard_version 3. See `references/eval_scorecard.md`.

**Never average across examples.** `ex6_jenga` is a deliberately
incoherent fixture and is supposed to score low on D3; averaging it
with `ex4` produces a number about nothing. Nothing in this file is
computed across two examples.

**No total, from scorecard_version 3.** Four of its five terms cannot
carry a delta, so a sum over them moves most where the card reads
worst. Read a dimension.

**`contested` is computed, never declared.** Scoring rule 5 — a spread
greater than 1 across the judges of one artifact — is re-derived from the
cards on every run. A card's own `contested` field is a declaration and
cannot manufacture one or erase one; where the two differ, the difference
is printed below the table.

| example | arm | judge | tier | D1 bug detection | D2 complexity | D3 modularity | D4 behavior preservation | D5 honesty | contested |
|---|---|---|---|---|---|---|---|---|---|
| ab_quota_ledger | S | pass 1 | opus | 3 | 2 | 2 | 2 | 3 | — |
| ab_quota_ledger | S | pass 2 | opus | 3 | 2 | 2 | 2 | 3 | — |
| ab_quota_ledger | S | pass 3 | sonnet | 3 | 2 | 1 | 3 | 2 | — |
| ab_quota_ledger | S | pass 4 | sonnet | 3 | 2 | 2 | 3 | 2 | — |

### Contested — rule 5, computed

None. No dimension has a spread greater than 1 in any judge group here.

### Tier splits

A dimension where two judge tiers do not overlap at all on the same
artifact. Reported only where the ranges are DISJOINT — an overlap is two
tiers agreeing as far as this can tell.

- **ab_quota_ledger / arm S, D4** — `opus` [2, 2]; `sonnet` [3, 3]; `sonnet` higher by 1.0 point(s).
- **ab_quota_ledger / arm S, D5** — `opus` [3, 3]; `sonnet` [2, 2]; `opus` higher by 1.0 point(s).

- **ab_quota_ledger** (20260807-sm05gf-S-p1): An honest, proportionate, well-tested single-module implementation whose own test suite reaches one fault class the shared model provably cannot express -- but whose sole model-derived check is measured here to accept 5 of 400 commands at its pinned seed and never a single release, which is why a release that reports 'rejected' while still releasing passes all 32 of its own tests.
- **ab_quota_ledger** (20260807-sm05gf-S-p2): A disciplined single-module implementation with one real durable-side chokepoint but no swappable port and no model, whose 32 green tests conceal a measured hole -- its flagship 400-step randomized sweep reaches a terminal state at step 30, issues five accepting transitions in total and never once an accepting release, and its own anti-degeneracy guard passes anyway.
- **ab_quota_ledger** (20260807-sm05gf-S-p3): A correct, well-tested, honestly-annotated single-module implementation that catches real faults including a refusal-class one a whole-view corpus alone cannot reach (D1=3, D4=3), but it is not ports-and-adapters in any functional sense -- the domain hardcodes its own concrete durable-I/O class with zero abstraction or injection and ships no fake to swap in (D3=1) -- so read it as a solid direct implementation, not a hexagonal one.
- **ab_quota_ledger** (20260807-sm05gf-S-p4): A competent, honest, single-module implementation that satisfies the spec and is caught out by real content- and refusal-sensitive checks (including one I built myself), but it never attempts a ports-and-adapters split, and my own independently-seeded ordering fault exposed a real detection gap between the shared suite and the artifact's own tests that the evidence packet's tables alone would not have surfaced.
