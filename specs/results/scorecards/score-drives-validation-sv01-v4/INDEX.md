# Scorecards — score-drives-validation-sv01-v4

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

- **ab_quota_ledger** (20260812-sv01v4-GL-p1): A four-file quota ledger whose hexagonal boundary is real under execution, not just under import inspection: the domain imports only `__future__`/`dataclasses`/`typing`, the whole swap is one line at quota_ledger/__init__.py:39, and when I performed that swap the domain file stayed byte-identical while all 28 shared cases passed, and when I poisoned every filesystem entry point in Python the domain ran a full scenario unharmed, reaching its collaborator only through `append` and `records` -- so D3 sits at 4, with a real adapter and a working fake driven by one 53-case list that asserts literal transcripts rather than agreement between the two wirings. D2 sits at 2 and not 3 for a single reason: the artifact makes a genuine simplification (`available` is derived at domain.py:118-120 rather than stored, which is why R1 cannot drift) and argues it well at NOTES.md:69-84, but records no figure before or after and `mechanical.json` is empty, and anchor 3 asks for measurement, not for argument -- I confirmed by deletion that the derived behavior is still independently asserted, which is the half of the caveat I can answer, but a judge measuring it afterwards is not the artifact recording it. Of thirteen faults I seeded, the artifact's own suite killed twelve and the shared floor killed eight; the single fault that survived BOTH is rejection PRECEDENCE -- swapping the `tenant_closed` and `amount_not_positive` guards at domain.py:139-142 leaves 53/53 and 28/28 green, because no case anywhere constructs an input where two rejection conditions hold at once, even though FEATURE.md:40-45 fixes the order explicitly. DISCLOSURE: I did not learn the arm mapping, but the artifact's own NOTES.md:102-123 has a section headed 'Where the feature file and the architecture ask conflicted' that quotes a structural instruction ('the domain holds no file handle, no path') from a prompt the feature file explicitly does not contain, so the artifact self-identifies as having been produced under a structure/architecture treatment; the blind is defeated by the artifact I was told to read, not by anything I went looking for.
- **ab_quota_ledger** (20260812-sv01v4-GL-p2): A four-file quota ledger whose boundary is real under runtime inspection and not merely declared: I wrote a third journal adapter of my own and drove the domain with it unchanged, and an audit hook shows the rules emit zero I/O events behind the fake and exactly one `open` behind the file adapter, so D3 is a 4 on executed evidence rather than on the import graph (D2 is a 2: the design stores no fact twice and `available` is derived rather than maintained, but the simplification the author argues for is argued, not measured, and there is no second tree in the packet to diff or any figure before or after). The finding worth more than either number is that 27 seeded faults located a consistent blind spot rather than a weak suite: the artifact's 53 cases kill 20 of them and out-catch the shared floor on id reuse, lexicographic id ordering, file truncation, list aliasing and the domain's own imports -- but rewiring the public `QuotaLedger` factory to the in-memory journal, so the program never writes a durable file at all, passes both suites, as does closing a tenant while a DIFFERENT tenant holds a live reservation, as does inverting FEATURE.md's stated rejection precedence so a closed tenant asked for a zero amount answers `amount_not_positive` instead of `tenant_closed`. The code is right on all three; nothing tests any of them, and the one case that presents itself as reading bytes off disk compares through `Path.read_text()`, which silently normalises CRLF, so a line-ending fault survives it too. I remained blind to the arm and worked out nothing about provenance. DISCLOSURE: after both scores were fixed I ran `git status --short` to confirm the tree was clean, which the dispatch's ban on routes into repository history fairly covers; its output listed the PATHS of a sibling pass-1 card and of a v5 round I did not know existed. I opened neither and saw no contents, no scores and no arm mapping -- filenames only -- and it came after scoring, but it is recorded rather than omitted.
