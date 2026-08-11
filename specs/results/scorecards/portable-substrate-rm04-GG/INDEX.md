# Scorecards — portable-substrate-rm04-GG

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
| eval_toolchain | GG | pass 1 | opus | — | 2 | 2 | — | — | D3 |
| eval_toolchain | GG | pass 2 | sonnet | — | 1 | 4 | — | — | D3 |

### Declared `contested` against computed

- `eval_toolchain` / 20260810-rm04-GG-p1: the card declares `contested = []`; the cards compute `['D3']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.
- `eval_toolchain` / 20260810-rm04-GG-p2: the card declares `contested = []`; the cards compute `['D3']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.

### Contested — rule 5, computed

- **eval_toolchain / arm GG, D3** — spread 2: claude-opus-4/pass 1 = 2, claude-sonnet-4-5/pass 2 = 4. Rule 5 asks for a third pass citing NEW evidence.

### Tier splits

A dimension where two judge tiers do not overlap at all on the same
artifact. Reported only where the ranges are DISJOINT — an overlap is two
tiers agreeing as far as this can tell.

- **eval_toolchain / arm GG, D2** — `opus` [2]; `sonnet` [1]; `opus` higher by 1.0 point(s).
- **eval_toolchain / arm GG, D3** — `opus` [2]; `sonnet` [4]; `sonnet` higher by 2.0 point(s).

- **eval_toolchain** (20260810-rm04-GG-p1): D2 = 2 and D3 = 2 at the declared scope: the harness's own logic is duplicated by hand across modules and performs its I/O in the modules that compute, while the anchor-4-shaped port evidence -- which I executed and which holds -- lives in a 5-module fixture inside the scope, so read this card as 'the fixture is ports-and-adapters and the harness around it is not', and note the disclosed leak (examples/validation/scorecards/subjects.toml:263-267 declares this exact scope's effect boundary, and :233-236 predicts D2 bounded at 2 for it) before comparing this card with any other.
- **eval_toolchain** (20260810-rm04-GG-p2): The demonstrated real-adapter-and-fake port swap in ab/reference_ports (D3 = 4) is genuine and runtime-verified, but a reader should not extend it to the rest of this 85-module, 14,207-line scope, which also contains declared god-state fixtures (ex3_over_complex, ex6_jenga) that keep D2 at 1 and an unfinished fake on ex4's own LedgerStorePort that the toolchain never exercises.
