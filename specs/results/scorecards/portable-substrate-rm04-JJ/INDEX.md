# Scorecards — portable-substrate-rm04-JJ

scorecard_version 4. See `references/eval_scorecard.md`.

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
| eval_toolchain | JJ | pass 1 | opus | — | 1 | 1 | — | — | — |
| eval_toolchain | JJ | pass 2 | sonnet | — | 2 | 0 | — | — | — |

### Contested — rule 5, computed

None. No dimension has a spread greater than 1 in any judge group here.

### Tier splits

A dimension where two judge tiers do not overlap at all on the same
artifact. Reported only where the ranges are DISJOINT — an overlap is two
tiers agreeing as far as this can tell.

- **eval_toolchain / arm JJ, D2** — `opus` [1]; `sonnet` [2]; `sonnet` higher by 1.0 point(s).
- **eval_toolchain / arm JJ, D3** — `opus` [1]; `sonnet` [0]; `opus` higher by 1.0 point(s).

- **eval_toolchain** (20260810-rm04-JJ-p1): Gate every verdict on an executable count before quoting any number from this scope -- price() returns PRICED and altered_score_probe returns UNCAUGHT over columns that provably did not run, both limits the files themselves state and do not enforce -- and delete price_removal.py's hand-typed RECORD, which already disagrees with removals.toml about where one of its three removals landed.
- **eval_toolchain** (20260810-rm04-JJ-p2): Score examples/validation/gap_mutants/ as a stateless, honestly-bounded analysis toolkit with no ports-and-adapters architecture at all (D3=0) whose apparent complexity improvement is not a preserved-behavior simplification (D2=2, not 3) -- the repository's own removal census records that this exact cut, from a live mutant-execution catalogue to a pair of passive pricing/probe tools, has a non-zero price, so read the mechanical figures as a scope reduction, not a free simplification.
