# Scorecards — subtract-to-measure-sm05

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
| toolchain_removal | K | pass 1 | opus | 2 | 3 | 2 | 2 | 4 | D3 |
| toolchain_removal | K | pass 2 | opus | 3 | 3 | 2 | 2 | 4 | D3 |
| toolchain_removal | K | pass 3 | sonnet | 3 | 4 | 4 | 3 | 4 | D3 |
| toolchain_removal | K | pass 4 | sonnet | 2 | 3 | 3 | 2 | 4 | D3 |

### Declared `contested` against computed

- `toolchain_removal` / 20260807-sm05rm-K-p1: the card declares `contested = []`; the cards compute `['D3']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.
- `toolchain_removal` / 20260807-sm05rm-K-p2: the card declares `contested = []`; the cards compute `['D3']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.
- `toolchain_removal` / 20260807-sm05rm-K-p3: the card declares `contested = []`; the cards compute `['D3']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.
- `toolchain_removal` / 20260807-sm05rm-K-p4: the card declares `contested = []`; the cards compute `['D3']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.

### Contested — rule 5, computed

- **toolchain_removal / arm K, D3** — spread 2: claude-opus-5[1m]/pass 1 = 2, claude-opus-5[1m]/pass 2 = 2, claude-sonnet-5/pass 3 = 4, claude-sonnet-5/pass 4 = 3. Rule 5 asks for a third pass citing NEW evidence.

### Tier splits

A dimension where two judge tiers do not overlap at all on the same
artifact. Reported only where the ranges are DISJOINT — an overlap is two
tiers agreeing as far as this can tell.

- **toolchain_removal / arm K, D3** — `opus` [2, 2]; `sonnet` [3, 4]; `sonnet` higher by 1.5 point(s).

- **toolchain_removal** (20260807-sm05rm-K-p1): A removal that was measured instead of asserted -- the deleted port-swap machinery is shown to have bought zero unique kills and to have been blind to the one failure it existed to prevent -- but at the scored commit every cell that still decides anything is hand-written and the four model-derived columns are undecided because the cut left a live caller of a function it deleted; treat the subtraction as earned and the model-derived reach as unmeasured until those columns are re-run at f49a1c9.
- **toolchain_removal** (20260807-sm05rm-K-p2): The removal is honestly priced and the deleted mechanism is demonstrably redundant, but the cut also broke the only model-derived check pointed at it -- all four corpus columns report CONTROL_RED and the positive control failed on four of nine -- so before this change is read as behaviour-preserving, repair the apply_wiring import in the port-swap driver and re-run run_gap_mutants.py at f49a1c9.
- **toolchain_removal** (20260807-sm05rm-K-p3): The removal cuts real, measured complexity from exactly the file it claims to (D2=4) without losing the specific fault-catching it claims to preserve (D4=3, D1=3), its own stated justification ('zero unique kills across 28 tables') checks out against the raw mutant data and against a fault I seeded myself, and the artifact is honest about what it no longer carries (D5=4); D1/D4's ceiling is one the artifact cannot reach under the strict model-derived-not-hand-written reading of anchor 4 no matter how good its hand-written suite is.
- **toolchain_removal** (20260807-sm05rm-K-p4): The removal is honestly measured and mostly paid-for, but the evidence given does not show the toolchain's model-derived (as opposed to hand-written) detection still reaching the hard fault classes after the cut, and a non-trivial side effect -- a domain-fault detector column going from a decided kill to CONTROL_RED -- was disclosed but not closed.
