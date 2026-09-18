# Scorecards — self-improvement-substrate-si03

scorecard_version 1. See `references/eval_scorecard.md`.

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

**The judge column is the FULL MODEL ID, not a tier word.** `RM-04`
measured four judge models wearing two labels and no two rounds of that
epic using the same pair, so a table keyed on `opus`/`sonnet` invites a
reader to add two rounds that measured different programs. The family
word is still derived and still policed against a declared `tier`; what
changed is that it is no longer what a printed comparison is keyed on.

| example | arm | judge | model | I1 reporting | I2 proposal | I3 disposition | I4 attribution | I5 honesty | contested |
|---|---|---|---|---|---|---|---|---|---|
| si-06-pr352 | full | pass 0 | claude-opus-5[1m] | 3 | 2 | 3 | 0 | 3 | — |
| si-06-pr352 | redacted | pass 0 | claude-opus-5[1m] | 0 | 0 | 0 | 0 | 2 | — |

### Contested — rule 5, computed

None. No dimension has a spread greater than 1 in any judge group here.

### Tier splits

A dimension where two judge tiers do not overlap at all on the same
artifact. Reported only where the ranges are DISJOINT — an overlap is two
tiers agreeing as far as this can tell.

None.

- **si-06-pr352** (20260918-si03probe-full-p1): The loop is reported and disposed of and never attributed: I1/I3 at 3 and I4 at 0 on the same subject.
- **si-06-pr352** (20260918-si03probe-redacted-p1): With the two sections removed the same subject scores 0 on reporting, proposal and disposition, while attribution stays where it was.
