# Scorecards — score-drives-validation-sv01-v5

scorecard_version 5. See `references/eval_scorecard.md`.

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

| example | arm | judge | model | D1 bug detection | D2 complexity | D3 modularity | D4 behavior preservation | D5 honesty | contested |
|---|---|---|---|---|---|---|---|---|---|
| ab_quota_ledger | GL | pass 1 | claude-opus-5[1m] | — | 2 | 4 | — | — | — |
| ab_quota_ledger | GL | pass 2 | claude-opus-5[1m] | — | 2 | 4 | — | — | — |

### Contested — rule 5, computed

None. No dimension has a spread greater than 1 in any judge group here.

### Tier splits

A dimension where two judge tiers do not overlap at all on the same
artifact. Reported only where the ranges are DISJOINT — an overlap is two
tiers agreeing as far as this can tell.

None.

- **ab_quota_ledger** (20260812-sv01v5-GL-p1): A genuinely small ports-and-adapters implementation whose boundary I verified by running rather than by reading imports -- the domain touches only `append`/`records` on its port at runtime, every filesystem open in a full scenario comes from `file_journal.py`, and 50 of its 53 cases are one case list run against a real adapter and a working fake with literal expected transcripts on both -- so D3=4; D2=2 because the design is proportional to its behavior (max cc=5, in the one function that has four specified rejections) with `available` derived rather than stored, but no before/after complexity figure is recorded anywhere and anchor 3 asks for measurement, not argument. The finding worth more than either number is what seeded faults showed: I killed 17 of 20 mutants with the artifact's own suite and 13 of 20 with the shared suite, and the three that survived BOTH are the ones that matter -- reordering the rejection guards so `reserve("nobody", 0)` returns `amount_not_positive` instead of `unknown_tenant` (FEATURE.md:40-45 specifies that order and no case ever makes two guards true at once), and swapping the shipped composition root to hand the domain an `InMemoryJournal` or a file at the wrong path, which nothing observes because the artifact's own suite never constructs `QuotaLedger` and the shared suite never looks at the path it passed in. I did not learn which arm this is.
- **ab_quota_ledger** (20260812-sv01v5-GL-p2): A four-file quota ledger whose boundary is real under execution, not just under import inspection: the domain calls only `append`/`records`, the one-line adapter swap at quota_ledger/__init__.py:39 passes 28/28 of the shared suite with nothing on disk, and the same case list runs against a real file adapter and a working in-memory one with literal expected transcripts on both -- D3 4, with the honest limit that the disk is observed independently only by one test outside that paired list, so an adapter that never touches the filesystem survives 26 of 27 own cases and all 28 shared ones. Complexity is proportional and single-writer with `available` derived rather than stored (domain.py:118-120), but nothing measures it before or after, so D2 is 2 and not 3. Of eleven faults I seeded, nine died and two lived: an id burned on a rejected reserve dies only in the artifact's own suite, and swapping the `tenant_closed` / `amount_not_positive` precedence dies in neither -- the ordered rejection chain the feature specifies is untested wherever two guards fire at once. I did not identify which arm `GL` is, though NOTES.md:102-123 quotes a structural instruction ('Section 1: the domain holds no file handle, no path') that this artifact's author was evidently given and that FEATURE.md explicitly does not contain.
