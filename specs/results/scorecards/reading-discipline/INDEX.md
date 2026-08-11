# Scorecards — reading-discipline

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

**The judge column is the FULL MODEL ID, not a tier word.** `RM-04`
measured four judge models wearing two labels and no two rounds of that
epic using the same pair, so a table keyed on `opus`/`sonnet` invites a
reader to add two rounds that measured different programs. The family
word is still derived and still policed against a declared `tier`; what
changed is that it is no longer what a printed comparison is keyed on.

| example | arm | judge | model | D1 bug detection | D2 complexity | D3 modularity | D4 behavior preservation | D5 honesty | contested |
|---|---|---|---|---|---|---|---|---|---|
| ab_quota_ledger | D | pass 1 | claude-opus-5[1m] | 3 | 3 | 1 | 4 | 4 | D4 |
| ab_quota_ledger | D | pass 2 | claude-opus-5[1m] | 3 | 4 | 1 | 4 | 4 | D4 |
| ab_quota_ledger | D | pass 3 | claude-sonnet-5 | 3 | 3 | 0 | 2 | 4 | D4 |
| ab_quota_ledger | D | pass 4 | claude-sonnet-5 | 3 | 3 | 0 | 2 | 4 | D4 |
| ab_quota_ledger | E | pass 1 | claude-opus-5[1m] | 3 | 2 | 4 | 2 | 3 | — |
| ab_quota_ledger | E | pass 2 | claude-opus-5[1m] | 3 | 2 | 4 | 2 | 3 | — |
| ab_quota_ledger | E | pass 3 | claude-sonnet-5 | 3 | 2 | 4 | 2 | 2 | — |
| ab_quota_ledger | E | pass 4 | claude-sonnet-5 | 3 | 2 | 4 | 2 | 2 | — |
| ab_quota_ledger | F | pass 1 | claude-opus-5[1m] | 3 | 2 | 4 | 2 | 4 | — |
| ab_quota_ledger | F | pass 2 | claude-opus-5[1m] | 3 | 2 | 4 | 2 | 4 | — |
| ab_quota_ledger | F | pass 3 | claude-sonnet-5 | 3 | 2 | 4 | 2 | 4 | — |
| ab_quota_ledger | F | pass 4 | claude-sonnet-5 | 3 | 2 | 4 | 2 | 4 | — |
| ab_quota_ledger | M | pass 1 | claude-opus-5[1m] | 3 | 4 | 1 | 4 | 4 | D3, D4 |
| ab_quota_ledger | M | pass 2 | claude-opus-5[1m] | 3 | 4 | 2 | 4 | 4 | D3, D4 |
| ab_quota_ledger | M | pass 3 | claude-sonnet-5 | 3 | 3 | 1 | 2 | 4 | D3, D4 |
| ab_quota_ledger | M | pass 4 | claude-sonnet-5 | 3 | 3 | 0 | 2 | 3 | D3, D4 |
| ab_quota_ledger | N | pass 1 | claude-opus-5[1m] | 3 | 2 | 1 | 4 | 4 | D4 |
| ab_quota_ledger | N | pass 2 | claude-opus-5[1m] | 3 | 2 | 1 | 4 | 4 | D4 |
| ab_quota_ledger | N | pass 3 | claude-sonnet-5 | 3 | 2 | 0 | 2 | 4 | D4 |
| ab_quota_ledger | N | pass 4 | claude-sonnet-5 | 3 | 2 | 0 | 2 | 4 | D4 |
| ab_quota_ledger | Z | pass 1 | claude-opus-5[1m] | 3 | 2 | 1 | 1 | 4 | D3, D4 |
| ab_quota_ledger | Z | pass 2 | claude-opus-5[1m] | 3 | 2 | 2 | 4 | 3 | D3, D4 |
| ab_quota_ledger | Z | pass 3 | claude-sonnet-5 | 3 | 2 | 1 | 2 | 4 | D3, D4 |
| ab_quota_ledger | Z | pass 4 | claude-sonnet-5 | 3 | 2 | 0 | 2 | 3 | D3, D4 |

### Declared `contested` against computed

- `ab_quota_ledger` / 20260809-rd03D-D-p1: the card declares `contested = []`; the cards compute `['D4']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.
- `ab_quota_ledger` / 20260809-rd03D-D-p2: the card declares `contested = []`; the cards compute `['D4']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.
- `ab_quota_ledger` / 20260809-rd03D-D-p3: the card declares `contested = []`; the cards compute `['D4']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.
- `ab_quota_ledger` / 20260809-rd03D-D-p4: the card declares `contested = []`; the cards compute `['D4']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.
- `ab_quota_ledger` / 20260809-rd03M-M-p1: the card declares `contested = []`; the cards compute `['D3', 'D4']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.
- `ab_quota_ledger` / 20260809-rd03M-M-p2: the card declares `contested = []`; the cards compute `['D3', 'D4']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.
- `ab_quota_ledger` / 20260809-rd03M-M-p3: the card declares `contested = []`; the cards compute `['D3', 'D4']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.
- `ab_quota_ledger` / 20260809-rd03M-M-p4: the card declares `contested = []`; the cards compute `['D3', 'D4']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.
- `ab_quota_ledger` / 20260809-rd03N-N-p1: the card declares `contested = []`; the cards compute `['D4']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.
- `ab_quota_ledger` / 20260809-rd03N-N-p2: the card declares `contested = []`; the cards compute `['D4']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.
- `ab_quota_ledger` / 20260809-rd03N-N-p3: the card declares `contested = []`; the cards compute `['D4']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.
- `ab_quota_ledger` / 20260809-rd03N-N-p4: the card declares `contested = []`; the cards compute `['D4']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.
- `ab_quota_ledger` / 20260809-rd03Z-Z-p1: the card declares `contested = []`; the cards compute `['D3', 'D4']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.
- `ab_quota_ledger` / 20260809-rd03Z-Z-p2: the card declares `contested = []`; the cards compute `['D3', 'D4']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.
- `ab_quota_ledger` / 20260809-rd03Z-Z-p3: the card declares `contested = []`; the cards compute `['D3', 'D4']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.
- `ab_quota_ledger` / 20260809-rd03Z-Z-p4: the card declares `contested = []`; the cards compute `['D3', 'D4']`. **The computation is the answer.** A sealed card is never edited (R-H4), so the declaration stays where it is and this line is the correction beside it.

### Contested — rule 5, computed

- **ab_quota_ledger / arm D, D4** — spread 2: claude-opus-5[1m]/pass 1 = 4, claude-opus-5[1m]/pass 2 = 4, claude-sonnet-5/pass 3 = 2, claude-sonnet-5/pass 4 = 2. Rule 5 asks for a third pass citing NEW evidence.
- **ab_quota_ledger / arm M, D3** — spread 2: claude-opus-5[1m]/pass 1 = 1, claude-opus-5[1m]/pass 2 = 2, claude-sonnet-5/pass 3 = 1, claude-sonnet-5/pass 4 = 0. Rule 5 asks for a third pass citing NEW evidence.
- **ab_quota_ledger / arm M, D4** — spread 2: claude-opus-5[1m]/pass 1 = 4, claude-opus-5[1m]/pass 2 = 4, claude-sonnet-5/pass 3 = 2, claude-sonnet-5/pass 4 = 2. Rule 5 asks for a third pass citing NEW evidence.
- **ab_quota_ledger / arm N, D4** — spread 2: claude-opus-5[1m]/pass 1 = 4, claude-opus-5[1m]/pass 2 = 4, claude-sonnet-5/pass 3 = 2, claude-sonnet-5/pass 4 = 2. Rule 5 asks for a third pass citing NEW evidence.
- **ab_quota_ledger / arm Z, D3** — spread 2: claude-opus-5[1m]/pass 1 = 1, claude-opus-5[1m]/pass 2 = 2, claude-sonnet-5/pass 3 = 1, claude-sonnet-5/pass 4 = 0. Rule 5 asks for a third pass citing NEW evidence.
- **ab_quota_ledger / arm Z, D4** — spread 3: claude-opus-5[1m]/pass 1 = 1, claude-opus-5[1m]/pass 2 = 4, claude-sonnet-5/pass 3 = 2, claude-sonnet-5/pass 4 = 2. Rule 5 asks for a third pass citing NEW evidence.

### Tier splits

A dimension where two judge tiers do not overlap at all on the same
artifact. Reported only where the ranges are DISJOINT — an overlap is two
tiers agreeing as far as this can tell.

- **ab_quota_ledger / arm D, D3** — `claude-opus-5[1m]` [1, 1]; `claude-sonnet-5` [0, 0]; `claude-opus-5[1m]` higher by 1.0 point(s).
- **ab_quota_ledger / arm D, D4** — `claude-opus-5[1m]` [4, 4]; `claude-sonnet-5` [2, 2]; `claude-opus-5[1m]` higher by 2.0 point(s).
- **ab_quota_ledger / arm E, D5** — `claude-opus-5[1m]` [3, 3]; `claude-sonnet-5` [2, 2]; `claude-opus-5[1m]` higher by 1.0 point(s).
- **ab_quota_ledger / arm M, D2** — `claude-opus-5[1m]` [4, 4]; `claude-sonnet-5` [3, 3]; `claude-opus-5[1m]` higher by 1.0 point(s).
- **ab_quota_ledger / arm M, D4** — `claude-opus-5[1m]` [4, 4]; `claude-sonnet-5` [2, 2]; `claude-opus-5[1m]` higher by 2.0 point(s).
- **ab_quota_ledger / arm N, D3** — `claude-opus-5[1m]` [1, 1]; `claude-sonnet-5` [0, 0]; `claude-opus-5[1m]` higher by 1.0 point(s).
- **ab_quota_ledger / arm N, D4** — `claude-opus-5[1m]` [4, 4]; `claude-sonnet-5` [2, 2]; `claude-opus-5[1m]` higher by 2.0 point(s).

- **ab_quota_ledger** (20260809-rd03D-D-p1): Ship the pre/post equivalence probe instead of describing it -- REVISION-NOTES.md:71 says the 3000x60 differential script lives in a scratch directory outside the deliverable, and that single omission is the only thing standing between this revision and the top of D2, since its strongest behaviour-preservation evidence is currently a claim rather than an artifact; also refresh or footnote NOTES.md:8,20, which still says 37 tests in a tree that has 39. DISCLOSED LEAK: I did not learn the arm mapping, but the numbered 'Section 1/3/4/5/6' references throughout REVISION-NOTES.md tell me this came from a prompted revision arm working to a structured work order, not a bare one.
- **ab_quota_ledger** (20260809-rd03D-D-p2): Ship this revision and put the equivalence script that backs its headline claim INTO the tree (REVISION-NOTES.md:70-71 leaves it out, which is the single reason a strict reading of D2's anchor 4 would score this a 3 instead of a 4); I did not work out which arm this is and read no file outside the allowed list.
- **ab_quota_ledger** (20260809-rd03D-D-p3): D's one structural change -- deriving `available()` from `_outstanding` instead of maintaining a duplicate `_held` running total -- is a real, well-argued, and measured simplification (D2=3) that the artifact's own process caught weakening its test suite (M4) and then repaired, which is the strongest self-correction either card exhibits, but the revision left the same missing ports/adapters boundary (D3=0) and the same absence of model-derived checks (D1, D4 both capped at 2-3) untouched.
- **ab_quota_ledger** (20260809-rd03D-D-p4): The `_held` removal is a genuine, measured simplification (D2=3): it collapses a duplicated per-tenant total kept in sync at three call sites into a single derivation from `_outstanding`, verified behavior-preserving by both the artifact's own 3000-walk equivalence claim and my independent 60,000-operation N-vs-D differential (0 divergences) -- but it is not free, since the same change caused a real, disclosed regression in the shipped mutation suite (M4's kill going from caught to accidental-then-fixed) and a stated O(1)->O(n) cost in `available()`, and it inherits N's D3=0 (no ports/adapters boundary) and the missing 'commit after release' test unchanged.
- **ab_quota_ledger** (20260809-rd03E-E-p1): A genuinely well-separated ports-and-adapters tree whose own cases caught 12 of the 13 faults I seeded including four the shared contract cannot reach - so the actionable step is to give it a model-derived corpus, since the ONLY thing holding D1 and D4 below their top anchors is that every case here is hand-written; DISCLOSURE: I did not learn which arm this is, but REVISION-NOTES.md on the paired tree cites 'Section 1/3/5/6' of an arm prompt I have not read, so I can infer this subject received a structural/simplicity prompt and is not a bare control.
- **ab_quota_ledger** (20260809-rd03E-E-p2): A greenfield tree whose hand-written cases killed all twelve faults I seeded, four of them invisible to the shared contract, and whose port is substituted in fact and not just declared; to move it up, derive the cases from a model rather than by hand (that single change unlocks D1 4 and D4 3-4), and note that the blank-line filter at quota_ledger/file_journal.py:25 is dead code defended by a factually wrong justification at NOTES.md:100-102, since str.splitlines() emits no trailing empty element and deleting the filter leaves both suites green.
- **ab_quota_ledger** (20260809-rd03E-E-p3): Ship the design as built -- a proportional, genuinely swappable ports-and-adapters domain (D3=4) with a hand-written suite that catches value, ordering, and cross-aspect faults I seeded myself (D1=3) -- but don't credit it for a complexity reduction or a model-derived check it never attempted (D2=2, D4=2), since it has no before to compare against and its tests are hand-written pytest, not a corpus or invariant.
- **ab_quota_ledger** (20260809-rd03E-E-p4): Ship E's ports-and-adapters split as-is -- domain/adapters are cleanly separated with single-writer state and a real+fake adapter proven interchangeable against one identical case list -- but its bug-catching and behavior-preservation evidence is entirely hand-written, so a reviewer who needs D1/D4 at anchor 4 should generate a model-derived corpus before relying on this suite alone.
- **ab_quota_ledger** (20260809-rd03F-F-p1): This tree is byte-identical to its before-tree and NO SIMPLIFICATION WAS MADE, so D2 stops at 2 despite both figure tables being recorded - the actionable step is to fix the anchor, not the artifact, because it pays for motion and this author was right to refuse it; the one real defect to file is that domain.py:108's sort is unobservable through the public API, so test_ledger.py:46 cannot fail for the reason it exists. DISCLOSURE: I did not learn which arm this is, but REVISION-NOTES.md cites 'Section 1/3/5/6' of an arm prompt I have not read, so I can infer this subject received a structural/simplicity prompt and is not a bare control.
- **ab_quota_ledger** (20260809-rd03F-F-p2): Byte-identical to the tree it revises -- I diffed and checksummed it, and mechanical.json's two complexity tables agree in every field -- so no simplification was made and D2 anchor 3 fails on its first clause however good the accounting is; the actionable next step is that the one candidate it proved redundant (the `_issue_order` sort, which I confirmed can be deleted with both suites green) has a twin it missed and mis-justified, the dead `if line` filter at quota_ledger/file_journal.py:25, and either both should go or the accounting should explain both.
- **ab_quota_ledger** (20260809-rd03F-F-p3): F is byte-for-byte identical to E in every scored file -- diffed and md5'd myself, not taken on the notes' word -- so this revision made no simplification and D2 stays at 2, not 3; what F actually earns over E is a higher D5 (4) for stating that outcome plainly instead of dressing up a null diff as progress.
- **ab_quota_ledger** (20260809-rd03F-F-p4): Do not read F's identical-to-E complexity figures as evidence a simplification pass reduced complexity -- the tree is byte-for-byte unchanged from E, and F's honest 'I changed nothing, here is why' should be credited for D5 but must not be mistaken for a D2-anchor-3 result; the pair is better cited as an example of an eval separating 'did the model report try' from 'did complexity actually drop.'
- **ab_quota_ledger** (20260809-rd03M-M-p1): A real but small simplification -- one redundant state representation and one dead field removed, which retires a class of drift bug the before tree could express and this one cannot -- shown behaviour-preserving by an unedited inherited suite and, independently, by 24,000 differential steps against the before tree with zero divergence; act on the fact that the complexity descriptor in mechanical.json detected essentially none of it (branch_points, callables, classes and instance_state all unchanged) because it does not count dataclass fields, so the instrument, not the artifact, is what needs fixing here. I did not work out which arm this is and did not look; I was told only that it is a revision of the other tree.
- **ab_quota_ledger** (20260809-rd03M-M-p2): Accept this as a real, behaviour-preserving simplification -- two stored fields gone, one of them provably dead and one a duplicate representation whose desynchronisation fault I could seed in the before tree and cannot express here, with zero observable divergence from the before tree in ~24,000 commands -- and then fix the one thing that is wrong in it: REVISION-NOTES.md:158 says NOTES.md is stale in one place when it is stale in at least three, including a test count and a run command pointing at another tree; I did not work out which arm this is and made no attempt to.
- **ab_quota_ledger** (20260809-rd03M-M-p3): M is a real but small simplification of Z -- two accidental fields removed, replaced by one canonical representation, verified behavior-preserving by hand-written tests I independently reproduced -- and the mechanical complexity descriptor barely registers it (2 of 158 code lines), which is itself the finding: measure state redundancy, not line count, to see what this revision actually did.
- **ab_quota_ledger** (20260809-rd03M-M-p4): M genuinely simplified Z's tenant record by removing one dead field and one derived-and-duplicated counter (verified behavior-preserving by a judge-run mutation, not just the author's claim), but that gain is real and small (2 lines) and traded away a structural guarantee against a cross-tenant close bug for a test-coverage guarantee, so read the D2 gain as a real but modest one, not a headline result.
- **ab_quota_ledger** (20260809-rd03N-N-p1): Move the evidence that only exists as prose into the tree -- the 90,484-state exhaustive search (NOTES.md:197-202) and the ordering/R4 transcripts are the artifact's strongest claims and none of them ships as a runnable file -- and give the durable side one real seam so the class stops writing the ledger from two places; DISCLOSED LEAK: I did not learn the arm mapping, but the artifact's own text ('Did the two halves of the prompt conflict?' at NOTES.md:297, and Section 1/Section 6 references) tells me this tree came from a prompted arm with an evidence-discipline section, not from a bare control.
- **ab_quota_ledger** (20260809-rd03N-N-p2): Ship the mutation harness and the clause table as they are, and fix the one thing the artifact measured and left standing -- give `_append`/`ledger_lines`/`__init__` a single durable-side seam so the boundary the code declares at quota_ledger.py:154 is the boundary it keeps, which is the only reason D3 is a 1; I did not work out which arm this is and read no file outside the allowed list.
- **ab_quota_ledger** (20260809-rd03N-N-p3): N is a competently-scoped single-class implementation with real, verified bug-catching evidence and unusually candid self-reporting, but it has no ports/adapters boundary at all (D3=0) and its behavior checks, while thorough, are hand-written rather than model-derived, which caps D1 and D4 below the top of their scales.
- **ab_quota_ledger** (20260809-rd03N-N-p4): Ship-quality single-file implementation with unusually rigorous self-testing (mutation analysis, an exhaustive BFS for one unobservable ordering, a measured R2 violation disclosed rather than hidden), but it is not ports-and-adapters (D3=0) and none of its checks are model-derived (D1/D4 capped at 3/2); the two concrete gaps a reader should ask the author to close next are the redundant `_held` cache (see artifact D, which removes it) and a missing dedicated test for 'commit a reservation that was already released'.
- **ab_quota_ledger** (20260809-rd03Z-Z-p1): A disciplined single-class implementation whose own directed cases reach a refusal-ordering class the shared contract provably cannot (I confirmed: the ordering fault leaves the shared suite 28/28 green), scored honestly high and modular low; the one actionable defect is that NOTES.md:39-41 and quota_ledger.py:214 both claim _append is the only write to the ledger while the constructor at :112 truncates that same file outside it -- fix the claim or route the truncation through the chokepoint. I did not work out which arm this is and did not look; I was told only that it is the earlier of a before/after pair.
- **ab_quota_ledger** (20260809-rd03Z-Z-p2): Take Z as a solid baseline whose own suite genuinely reaches the refusal, ordering and cross-aspect classes the shared contract cannot -- but delete _Tenant.quota, which I proved dead by removing it (28/28 and 21/21 still green), and fix test_a_bad_amount_beats_quota_exceeded, which asserts a check order that is unobservable because amount < 1 and amount > available >= 0 can never both hold; I did not work out which arm this is and made no attempt to.
- **ab_quota_ledger** (20260809-rd03Z-Z-p3): Z is a competent, honestly-disclosed baseline that is not fully minimal -- M's revision found and proved (by an independently-reproduced mutation test) two removable fields in Z's own tenant record; a reader wanting Z's design should apply M's two-field removal rather than treat Z as already minimal.
- **ab_quota_ledger** (20260809-rd03Z-Z-p4): Z is a competent, honestly-documented, unhardened single-class implementation (D3=0, no port exists) whose bug-catching and behavior-preservation ceiling is set by its hand-written (not model-derived) test suite (D1=D4 capped at 3/2 respectively) -- a reader who wants D1/D4 to move needs a generated corpus or a formal invariant check, not more hand-written tests.
