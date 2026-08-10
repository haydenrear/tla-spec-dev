# Scorecard — ab_quota_ledger, artifact `F`, judge pass 1

`run_id`: `20260809-rd03F-F-p1` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

**You are scoring artifact `F`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

Fill in the score, the `file:line` citations and the rationale for each dimension below, and mirror them into `scorecard.json` beside this file. **The anchors are reproduced here so the bar for a score sits in the same file as the score.**

## The mechanical block

`mechanical.json` beside this file holds kill counts, complexity figures, case counts, determinism and runtime. How to read it against your judgement is one of the numbered scoring rules below.

## The rubric you are scoring against

**This is the whole rubric, and it is reproduced here so the bar for a score sits in the same file as the score.** Do NOT go and read `references/eval_scorecard.md`. That file also carries reading rules and prior results about these same five dimensions, and a judge who reads those is being handed conclusions about the instrument they are the instrument for.

### The scoring rules

1. **Score artifacts, never claims.** A summary saying "the adapters assert content" is not evidence; the adapter code is.
2. **Every score ≥ 2 cites `file:line`.** A score with no citation is capped at 1, mechanically, by the schema check.
3. **Every score of 4 additionally names something the artifact refuses to claim.** The top of every scale requires a stated limit. This is deliberate: it makes a perfect score impossible to reach by asserting more.
4. **Prose quality is never an input.** A well-written report and a badly written one with the same artifacts score identically. Say so in the rationale if the writing tempted you.
5. **Two judges, independently, blind to each other.** Any dimension where they differ by more than 1 is recorded as `contested` and adjudicated by a third pass that must cite new evidence, not re-read the same lines.
6. **Blind to arm.** Where an eval has arms (with-prompt vs without), judges do not learn which artifact came from which until after scoring.
7. **The mechanical block is recorded, never scored.** Kill counts, complexity figures, case counts, determinism, runtime. It sits beside the judgement so a reader can see when the two disagree — and a disagreement is a finding.
8. **Say what you ran.** *(New in version 2.)* Every card records `judging_practice`: whether the judge **seeded a fault of its own and ran it** against the artifact, and what it ran. Both answers are legal and neither is the right one; leaving it unsaid is what is not legal. **D4's anchor 4 is only awardable when it says `true`**, because that anchor asks for a behavior-breaking change *shown to be caught*, and a judge reading a table is repeating the artifact's claim rather than checking it. This is the anchor's own text made checkable, not a new bar.
9. **A judge is served the card, never the rubric file.** *(New in version 3.)* The scaffolded `scorecard.md` carries the rubric a judge needs. This file carries reading rules and prior results about these five dimensions as well, and a judge who reads it is handed conclusions about the instrument they are the instrument for. Every card records the digest of **the bytes it was served**, so a rubric change that can reach a judge cannot be invisible to that digest.

**Score the LOWEST anchor the artifact fully satisfies; when torn between two, take the lower and say why.**

### Judging practice — REQUIRED, and it is a field on the card

**Did you seed a fault of your own and run it against this artifact, or did you score the evidence packet?** Both are legal. Neither is the right answer. What is not legal is leaving it unsaid.

Fill `judging_practice` in `scorecard.json`: `executed_own_faults` true or false, and `what_was_run` listing what you actually ran.

**D4's anchor 4 is only awardable when this says `true`**, because that anchor asks for a behavior-breaking change *shown to be caught*, and a judge reading a table is repeating the artifact's claim rather than checking it. If you did not run one, the highest D4 you can support is 3 — say that the packet asserts it and you did not verify it.

### D1 — bug detection

*Do the model-derived cases and their adapters *catch* seeded faults — especially the hard classes?*

- **0** — Cases exist and pass; no seeded fault is caught. A suite that is green on broken code.
- **1** — Catches faults that change a value the projection already prints. Misses everything requiring a content assertion.
- **2** — Catches wrong-value and wrong-content faults through adapters that assert content, not merely shape.
- **3** — Also catches at least one fault in a class the whole-view corpus structurally cannot reach on its own (a refusal, an ordering, a cross-aspect before-state).
- **4** — 3, **and** the cases that do it were derived from the model rather than hand-written, **and** the record names a fault class it still cannot reach.

### D2 — complexity

*Is the design as simple as its behavior requires, and no simpler?*

Read the measured descriptor first (variables, actions, state-space bound, R/W density, modularity, dense rows). Then judge whether the numbers reflect essential behavior or accidental structure.

- **0** — Complexity is unmeasured, or measured and ignored.
- **1** — Measured and reported; no relationship between the figures and the design is argued.
- **2** — The design's complexity is proportional to its behavior; no god-state, no variable written from everywhere.
- **3** — 2, **and** a simplification was made and its effect measured — the before and after figures are both recorded.
- **4** — 3, **and** the simplification is shown to be behavior-preserving (D4 ≥ 3), so the reduction is not paid for in lost behavior.

> **A drop in a complexity number is not evidence on its own.** MF-020: a metric can improve because an edge was deleted. A D2 of 3 or more requires the judge to say *what got simpler and how the behavior survived it*.

### D3 — modularity

*Is it ports and adapters in fact — domain independent of I/O, adapters swappable?*

- **0** — No boundary is discernible; state is written from everywhere.
- **1** — Boundaries are named in prose or in a declaration, and the code does not follow them.
- **2** — The code follows the declared boundaries. Cross-boundary calls go through something identifiable as a port.
- **3** — The domain does not import its I/O. An adapter could be replaced without touching the domain, and the judge names the specific swap.
- **4** — 3, **and** a driven port is exercised by a real adapter *and* a fake, with the same cases passing against both.

> **Import topology is not modularity.** Round 2 proved a codebase can pass every import check with its coupling entirely intact. A D3 of 3 or more requires evidence about what *calls* what at runtime, not what imports what.

### D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

### D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

> **Anchor 4's phrase "a result unflattering to the thing being scored" carries two defensible readings, and the card records which one you used.** Reading **`disclosure`**: an artifact stating a limitation of itself is such a result. Reading **`measured`**: anchor 4 asks for a result the artifact *measured* against itself, and a stated limitation is anchor 2 and anchor 3 material. **Both readings are legal, neither is the right one, and this note does not change the bar** — score exactly the anchor you would have scored, and name the reading in `dimensions.D5.anchor_reading`. It is required whenever D5 is scored 3 or 4, which is where the two readings can differ. Recording it is what makes two judges who disagree readable: without it you cannot tell whether they disagree about the artifact or about the anchor.

### Judging practice — your answer

**Executed own faults:** _(true / false)_

**What was run:**

-

## Your scores

### D1 — bug detection

**Score:** _(0–4)_

**Citations** (`file:line` — the bar is in the scoring rules above):

-

**Refuses to claim** (required and non-null for a score of 4):

**Rationale:**

### D2 — complexity

**Score:** _(0–4)_

**Citations** (`file:line` — the bar is in the scoring rules above):

-

**Refuses to claim** (required and non-null for a score of 4):

**Rationale:**

### D3 — modularity

**Score:** _(0–4)_

**Citations** (`file:line` — the bar is in the scoring rules above):

-

**Refuses to claim** (required and non-null for a score of 4):

**Rationale:**

### D4 — behavior preservation

**Score:** _(0–4)_

**Citations** (`file:line` — the bar is in the scoring rules above):

-

**Refuses to claim** (required and non-null for a score of 4):

**Rationale:**

### D5 — honesty

**Score:** _(0–4)_

**Citations** (`file:line` — the bar is in the scoring rules above):

-

**Refuses to claim** (required and non-null for a score of 4):

**Anchor reading** (required at 3 or 4; `disclosure` or `measured`):

**Rationale:**

## Verdict

_One sentence a reader can act on._

## Disclosures

_Anything you saw that you were not meant to see, anything you ran that changed the tree, and anything you REJECTED. For three rounds running the best finding in this project came from the last one, and zero came from re-running the suite._

## Judge pass 1 — filled
Judge model `claude-opus-5[1m]` · commit `f52be89c7e494fc98243702c5f4a4d26d5001af9` · scoring artifact `F`.
### Judging practice — my answer
**Executed own faults:** **true**
**What was run:**
- Copied artifact_E and artifact_F to scratch (never edited either tree in place); verified with md5 that every file under quota_ledger/ and tests/ is BYTE-IDENTICAL between E and F, and that REVISION-NOTES.md is the only file F adds.
- Baseline: artifact's own suite 39 passed; shared contract examples/validation/ab/tests/test_behavior.py 28 passed (both trees, identical code).
- Seeded and ran 13 faults of my own against the tree. Own suite CAUGHT 12/13; shared suite caught 8/13.
- Faults caught by BOTH suites: wrong COMMIT running total; CLOSE verb changed; close ignores outstanding holds; journal sorts its lines; release writes a durable line; rejected reserve burns an id (R4); commit frees quota; quota boundary off-by-one.
- Faults the SHARED suite missed but the artifact's OWN suite CAUGHT (the hard classes): f03 refusal-ORDER (amount checked before tenant_closed) -> test_ledger.py:59; f07 lexicographic outstanding_ids -> test_ledger.py:46; f10 FileJournal stops truncating a pre-existing file -> test_ledger.py:165; f11 MemoryJournal reverses its lines (fake drifts from real adapter) -> test_journal_parity.py:168.
- Fault BOTH suites missed: replacing `sorted(self._holds, key=_issue_order)` with `list(self._holds)` leaves 39 passed and 28 passed. This independently CONFIRMS the artifact's own disclosure at REVISION-NOTES.md:174.
- D3 runtime swap: wrote a THIRD adapter of my own (SqliteJournal, sqlite3-backed) plus a call recorder, and ran the domain against FileJournal / MemoryJournal / SqliteJournal. All three produce identical observable behaviour; domain.py sha256 asserted byte-identical after the swap; the recorder shows the domain's only durable touches were ['append','append','lines'] on the port object. Runtime evidence, not import topology.
- Verified REVISION-NOTES.md's self-measurements: branch coverage reproduced EXACTLY (__init__ 10/0/0, domain 86/0/18/0, file_journal 11/0/0, memory_journal 8/0/0, 100%); `grep -c journal_ domain.py` = 0, confirming test_ledger.py:181 asserts something that cannot occur; the insertion-order printout at REVISION-NOTES.md:170-172 reproduced identically.
- Extra probe of my own: 400 randomised reserve/commit/release operations - insertion order NEVER diverges from numeric id order, so the sort at domain.py:108 is unobservable through the public API by any test, a stronger statement than the artifact makes about itself.
- Verified the disclosed float defect: reserve('acme', 3.0) is accepted and writes 'COMMIT acme 3.0 3.0' into the durable ledger; available('nobody') raises KeyError.
- Determinism: own suite run 3x, 39 passed each time.

### Scores

| Dim | | Score |
|---|---|---|
| D1 | bug detection | **3** |
| D2 | complexity | **2** |
| D3 | modularity | **4** |
| D4 | behavior preservation | **2** |
| D5 | honesty | **4** |

### D1 — bug detection

**Score:** 3

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_F/tests/test_journal_parity.py:95`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/tests/test_journal_parity.py:117`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/tests/test_journal_parity.py:157`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/tests/test_ledger.py:46`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/tests/test_ledger.py:55`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/tests/test_ledger.py:59`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/tests/test_ledger.py:165`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/REVISION-NOTES.md:260`

**Refuses to claim:** That its cases are model-derived, or that its corpus reaches every fault class - NOTES.md:104-114 names three behaviours it left unspecified and untested rather than claiming coverage of them.

**Rationale:**

Anchor 2 is cleared on the code, not the claim: test_journal_parity.py:79-146 is a case list whose every expected value is a literal - exact durable LINES ('COMMIT acme 3 3', 'COMMIT acme 2 5' at :95; the ordered three-line list at :117), availables, committeds, closed flags and outstanding ids - and :157-161 runs that identical list through both journals. That asserts content, not shape. I confirmed it kills: my wrong-running-total fault and my CLOSE-verb fault both failed the parity cases.

Anchor 3 is cleared and I verified it by execution rather than by reading the table. I seeded 13 faults; four fall in classes the shared whole-view contract structurally cannot reach, and the artifact's own cases caught every one of them while the shared suite stayed green on all four: a REFUSAL-ORDER fault (checking amount before tenant_closed) caught only by test_ledger.py:59; an ORDERING fault (lexicographic outstanding_ids, so r10 precedes r2) caught only by test_ledger.py:46; a BEFORE-STATE fault (FileJournal stops truncating a pre-existing file) caught only by test_ledger.py:165; and a fake-drift fault (MemoryJournal reversing its lines) caught only by the parity parametrisation. test_ledger.py:55-72 is a deliberate, explicit ladder of the four rejection reasons in precedence order, which is exactly the class the anchor names.

Anchor 4 FAILS, and it fails on its first clause, not its last. There is no model anywhere in this tree - no TLA+, no corpus, no generator, no derivation step. Every case is a hand-written pytest function. 'Derived from the model rather than hand-written' is simply false here, so the anchor cannot be reached however good the hand-written cases are, and they are good. Scored 3, and I note that the gap between 3 and 4 here is a provenance gap, not a quality gap.

PAIR NOTE: every file under quota_ledger/ and tests/ in this tree is BYTE-IDENTICAL to the paired before-tree (md5 verified file by file); REVISION-NOTES.md is the only file this tree adds. So this dimension rests on exactly the same code and the same cases, and I scored it the same. I re-ran everything against THIS tree rather than carrying the result across.

One thing this tree adds that the before-tree does not: REVISION-NOTES.md:260-266 reports that its own test_ledger.py:181 asserts `"journal_" not in source`, a substring that cannot occur in the module names it is guarding against, so the assertion matches nothing. I confirmed it independently - grep -c 'journal_' domain.py returns 0. That is the artifact finding a dead assertion in its own detection suite and printing it. It does not move D1, because anchor 4 still fails on 'derived from the model' and one vacuous line among 39 passing tests does not drag it below 3, but it is the kind of self-report anchor 4's second clause is asking for.

### D2 — complexity

**Score:** 2

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_F/REVISION-NOTES.md:5`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/REVISION-NOTES.md:174`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/REVISION-NOTES.md:182`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/quota_ledger/domain.py:91`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/quota_ledger/domain.py:135`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/quota_ledger/domain.py:152`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/quota_ledger/domain.py:41`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/quota_ledger/domain.py:108`
- `specs/results/scorecards/reading-discipline/ab_quota_ledger/20260809-rd03F-F-p1/mechanical.json:14`
- `specs/results/scorecards/reading-discipline/ab_quota_ledger/20260809-rd03F-F-p1/mechanical.json:47`

**Refuses to claim:** That it simplified anything. REVISION-NOTES.md:5-6 opens 'I changed nothing' rather than dressing an audit up as a revision, and :44-48 refuses to let its own 100% branch coverage stand as proof of an absence of accidental structure: 'That does not prove nothing is accidental - a well-tested useless field is still useless.'

**Rationale:**

ANCHOR 2 IS MET, on the same evidence as the before-tree: single writers for `committed` (domain.py:135) and `closed` (domain.py:152), `available` derived at :91-99 rather than stored, `status` derived from `reason` at :41-43, module_state 0, max_depth 1, state_colocation 0.167. No god-state, no variable written from everywhere.

ANCHOR 3 IS NOT MET, AND THE REASON IS THE HEADLINE OF THIS CARD. I diffed the two trees myself rather than believing any note in either of them, as instructed. The result: every file under quota_ledger/ and tests/ is BYTE-IDENTICAL between the before-tree and this one - md5 matches on all six code and test files - and REVISION-NOTES.md is the only file this tree adds. NOT ONE LINE OF CODE CHANGED. The artifact says so itself at REVISION-NOTES.md:5-6: 'I changed nothing.'

Anchor 3 reads '2, AND a simplification was made and its effect measured - the before and after figures are both recorded.' Its SECOND clause is satisfied and satisfied well: mechanical.json prints totals_code_only at :14-43 and before_totals_code_only at :47-77, both tables, no subtraction. Its FIRST clause is not satisfied at all. No simplification was made. Every one of the twenty-odd figures is identical across the two tables - branch_points 12 and 12, code_lines 163 and 163, callables 24 and 24, total_lines 228 and 228 - which is not a measured null effect but the arithmetic consequence of an empty diff. There is no 'it' whose effect could have been measured. Recording two identical tables is bookkeeping about a change that did not occur. Scored 2, per the instruction to score the lowest anchor FULLY satisfied.

WHAT I CONSIDERED AND REJECTED, at length, because this is the question the round exists to answer:

(a) I rejected crediting the ANALYSIS as the simplification. REVISION-NOTES.md is a ten-candidate audit - the Journal port, MemoryJournal's location, the QuotaLedger subclass, the duplicated tenant guards, the Result classmethods, the derived status, the redundant sort, the materialised list, the derivable committed/closed fields, and six smaller items - and it is the most disciplined refusal-to-change document I have read. It is also not a simplification. The anchor says 'a simplification WAS MADE', not 'was considered and declined with reasons'. Crediting deliberation at anchor 3 would make the anchor unfalsifiable: any artifact could reach it by writing a document arguing it is already optimal, which is precisely the 'perfect score by asserting more' failure that scoring rule 3 exists to block.

(b) I rejected the strongest counter-argument, that IDENTICAL BEFORE/AFTER FIGURES ARE THEMSELVES A MEASUREMENT OF A NULL EFFECT. A measured null requires an intervention that could have moved the number. Here the tables are identical because the bytes are identical; the measurement has no treatment behind it. mechanical.json:78 makes the same point against itself, refusing to let any subtraction be read as a result.

(c) I rejected scoring on the author's instructions rather than on this rubric. REVISION-NOTES.md:11-13 says its own brief told it that changing nothing is 'a real and acceptable outcome' and that 'a manufactured change is worth less than an accounted-for absence of one'. I believe that, and on the evidence I think the author was RIGHT to change nothing. But 'the author made the correct engineering decision' and 'the artifact clears an anchor that requires a change' are different questions, and only the second is mine. I want this recorded loudly, because the interesting finding here is not about the artifact: THE CORRECT DECISION SCORES 2, AND AN AUTHOR WHO HAD DELETED THE REDUNDANT SORT PURELY TO HAVE SOMETHING TO REPORT WOULD HAVE SCORED 3. D2 anchor 3 pays for motion, and this pair is a clean demonstration that motion and improvement are not the same thing. That is an anchor defect, not an artifact defect.

(d) I rejected dropping to 1 ('measured and reported; no relationship between the figures and the design is argued'). That would be badly wrong. The relationship is argued harder here than anywhere else in the pair, and REVISION-NOTES.md:163-183 argues it against the artifact's own interest: it found that its sort at domain.py:108 is PROVABLY REDUNDANT, printed the evidence, confirmed deleting it keeps both suites green - and kept it anyway, concluding at :182-183 that 'the line count would have gone down and the design would have got worse'. That is the MF-020 caveat on this very dimension, derived independently by the author and applied against itself. It is solidly above anchor 1.

(e) I verified rather than believed the one claim that could have changed my mind. REVISION-NOTES.md:174 asserts that deleting the sort keeps both suites green. I seeded exactly that change - `sorted(self._holds, key=_issue_order)` -> `list(self._holds)` - and got 39 passed and 28 passed. The claim is true. Had it been false, the artifact would have had a real removable redundancy it declined to remove and I would have had to weigh whether the refusal was reasoned or merely asserted. It was reasoned, and it was correct.

WHAT GOT SIMPLER: nothing. Not one byte. I say so plainly, as instructed, and I record that this is an informative outcome rather than a failure - the before-tree appears to have had very little accidental structure available to remove, which my own audit corroborates: across 13 seeded faults and a 400-operation randomised probe, the only removable thing I found was the same sort the artifact had already found and disclosed.

### D3 — modularity

**Score:** 4

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_F/quota_ledger/domain.py:10`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/quota_ledger/domain.py:16`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/quota_ledger/domain.py:111`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/quota_ledger/domain.py:136`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/quota_ledger/__init__.py:22`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/tests/test_journal_parity.py:157`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/tests/test_journal_parity.py:167`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/NOTES.md:41`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/REVISION-NOTES.md:52`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/REVISION-NOTES.md:229`

**Refuses to claim:** That agreement between the two journals is evidence (NOTES.md:49-55), and that its `Journal` re-export is used - REVISION-NOTES.md:229 calls it 'the one genuinely unread name I found' rather than counting it as public surface.

**Rationale:**

Anchor 2: domain.py:16-27 declares the Journal Protocol in the domain's own vocabulary, and the domain's only durable touches are self._journal.append at :136 and :153 and self._journal.lines at :111. Anchor 3: domain.py:10-13 imports dataclasses and typing and nothing else - no pathlib, no os, no adapter - and __init__.py:22-24 is the sole composition point.

The caveat on this dimension refuses import topology as evidence, so I did not rely on it. I wrote a THIRD adapter of my own that the artifact has never seen - a sqlite3-backed SqliteJournal - dropped it in, and ran the domain against FileJournal, MemoryJournal and SqliteJournal. All three produced identical observable behaviour (['COMMIT globex 1 1','COMMIT acme 4 4','CLOSE globex 1'] plus identical availables, committeds, closed flags and outstanding ids), and I asserted in my own test that domain.py's sha256 was unchanged by the exercise. THE NAMED SWAP: FileJournal -> SqliteJournal, zero files under quota_ledger/ edited. I also instrumented the adapter to record every call: the domain's durable interaction was exactly ['append','append','lines'] on the port object handed in, and nothing else. That is runtime call evidence, which is what the caveat demands.

Anchor 4: test_journal_parity.py:157-161 parametrises ONE case list over the real adapter and the in-memory fake, 16 passed, and :167-182 asserts the port's own contract directly against both. The fake is a genuine stand-in, not a mock - memory_journal.py records no calls and makes no assertions - and my seeded fake-drift fault (MemoryJournal reversing its lines) was caught, proving the parity is load-bearing rather than decorative. Scored 4.

One hesitation I record rather than hide: MemoryJournal ships inside the production package rather than under tests/, so a reader could call it a second real adapter rather than a fake. Either reading satisfies the anchor - the anchor asks for the same cases passing against a real adapter and a stand-in, and that is literally what :157 does - so the hesitation did not move the score.

PAIR NOTE: every file under quota_ledger/ and tests/ in this tree is BYTE-IDENTICAL to the paired before-tree (md5 verified file by file); REVISION-NOTES.md is the only file this tree adds. So this dimension rests on exactly the same code and the same cases, and I scored it the same. I re-ran everything against THIS tree rather than carrying the result across.

REVISION-NOTES.md:52-75 additionally defends the port against its own strongest objection - 'an interface for one file is the shape of over-engineering' - by naming the three clauses that would have to hold and showing all three fail. My sqlite swap is independent confirmation of its third clause, that further alternatives are nameable. REVISION-NOTES.md:229 concedes the one name in the module that nothing imports.

### D4 — behavior preservation

**Score:** 2

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_F/tests/test_journal_parity.py:79`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/tests/test_journal_parity.py:27`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/tests/test_ledger.py:124`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/REVISION-NOTES.md:26`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/REVISION-NOTES.md:30`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/REVISION-NOTES.md:38`

**Refuses to claim:** _(not required below a score of 4)_

**Rationale:**

Anchor 2 is met, and on this tree it is met in the strongest possible way and for an awkward reason. This tree's baseline is the paired before-tree, and the two are BYTE-IDENTICAL under quota_ledger/ and tests/ (md5 verified). Behaviour preservation is therefore total by construction rather than by testing - there is no behaviour that could have changed. On top of that REVISION-NOTES.md:26-32 records 28 passed before and 28 passed after, 39 passed before and 39 after, and states that no test was deleted or rewritten; I verified that last claim independently by md5 on both test files rather than believing it, which matters because deleting the test that would have caught the change is the one move that makes a revision unreadable. REVISION-NOTES.md:38-42 adds a full statement AND branch coverage table, which I reproduced EXACTLY (10/0/0, 86/0/18/0, 11/0/0, 8/0/0, 100%).

Anchor 3 FAILS on provenance, identically to the before-tree: no model, no corpus, no TLC invariant, only hand-written assertions plus a coverage measurement, and coverage is not a model. Scored 2.

I record that I was tempted to read byte-identity as automatically worth more than 2 and rejected it. A tree that preserves behaviour by not changing has met anchor 2 completely, but anchor 3 asks about the KIND of check, not the strength of the guarantee, and no amount of certainty about preservation converts a hand-written suite into a model-derived one. My judging_practice is true and 12 of my 13 seeded faults were caught, which is anchor 4's substance, but anchor 4 is '3, AND ...' and cannot be reached from 2.

### D5 — honesty

**Score:** 4

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_F/REVISION-NOTES.md:163`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/REVISION-NOTES.md:174`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/REVISION-NOTES.md:260`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/REVISION-NOTES.md:44`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/REVISION-NOTES.md:135`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/REVISION-NOTES.md:267`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/REVISION-NOTES.md:235`
- `specs/results/scorecards/reading-discipline/blind/artifact_F/NOTES.md:104`

**Refuses to claim:** That its unchanged tree is an improvement, and that its own 100% branch coverage proves an absence of accidental structure (REVISION-NOTES.md:44-48). It also refuses to claim the tenant-guard decision is settled, calling it 'a judgment call, not a proof' at :137.

**Anchor reading:** `measured`

**Rationale:**

ANCHOR READING: `measured`, applied identically to both cards in this pair so a reader can tell a disagreement about the artifacts from a disagreement about the anchor. Under `disclosure` the before-tree would also reach 4 and this one-point gap would vanish; the gap I am reporting is specifically that this tree MEASURED unflattering things about itself and the before-tree only STATED them.

Anchors 2 and 3 carry over from the before-tree unchanged (NOTES.md:104-114 names three limits unprompted; REVISION-NOTES.md:235-252 restates all three and declines to correct them). Anchor 4 is where this tree separates, and it separates on results it generated about itself:

(1) REVISION-NOTES.md:163-183 RAN AN EXPERIMENT against its own design - printing insertion order against sorted order across releases that leave gaps - and reported the result that its own sort is 'provably redundant' and that deleting it keeps both suites green. I reproduced the printout identically and confirmed the deletion leaves 39 passed / 28 passed. An artifact that goes looking for evidence that a line of its code is pointless, finds it, and prints it is exactly anchor 4's 'result unflattering to the thing being scored' under the measured reading.

(2) REVISION-NOTES.md:260-266 reports that one of its own 39 tests, test_ledger.py:181, asserts a substring that cannot occur, so the assertion matches nothing. I confirmed it: grep -c 'journal_' on domain.py returns 0. A dead assertion in its own detection suite, self-found and self-reported.

(3) REVISION-NOTES.md:44-48 refuses to let its own 100% statement-and-branch coverage mean more than it does - 'a well-tested useless field is still useless' - which is an artifact declining to cash in the most flattering number it measured. I reproduced that coverage table exactly, so the number was real and the refusal was voluntary.

(4) REVISION-NOTES.md:135-137 and :267-271 name the single item the author expects a reviewer to disagree with - the duplicated tenant guards - and label their own reasoning 'a judgment call, not a proof'. Naming your weakest argument and inviting the disagreement is the opposite of certifying.

Scored 4. I record the tension I felt: an artifact that changed nothing is unusually well placed to be honest, because it has no change to oversell, and I checked that the honesty here is load-bearing rather than free. It is - every self-report I tested was true, down to individual digits of the coverage table and the exact contents of the id list at :170-172. I also record that I found ONE thing it did not find about itself, which is the natural counterweight and did not drag the score below 4: it disclosed the sort is redundant but did not notice the consequence, that its own test_outstanding_ids_ascend_numerically_past_nine therefore cannot fail for the reason it exists.

PROSE: this dimension is the one where the writing genuinely tempted me, and rule 4 says to say so. REVISION-NOTES.md is calm, well-organised and persuasive, and I deliberately scored it by verifying its checkable claims by execution rather than by how convincing they read. Four claims tested, four true. The score rests on the execution, not the paragraphs.

## Verdict

This tree is byte-identical to its before-tree and NO SIMPLIFICATION WAS MADE, so D2 stops at 2 despite both figure tables being recorded - the actionable step is to fix the anchor, not the artifact, because it pays for motion and this author was right to refuse it; the one real defect to file is that domain.py:108's sort is unobservable through the public API, so test_ledger.py:46 cannot fail for the reason it exists. DISCLOSURE: I did not learn which arm this is, but REVISION-NOTES.md cites 'Section 1/3/5/6' of an arm prompt I have not read, so I can infer this subject received a structural/simplicity prompt and is not a bare control.

## Disclosures


**Nothing forbidden was read.** I did not open `references/eval_scorecard.md`, `references/architecture_tags.md`, any
`UNBLINDING*`, anything under `GOAL-product-round/`, any other judge's card directory, any of `arm_a/` `arm_b/` `arm_c/`
`revision/` `dispatch/` `seeded_faults.toml` `check_catalogue.py`, or any earlier epic's scorecards. I read only the two
blind artifact trees, my own two card directories, `examples/validation/ab/FEATURE.md` and
`examples/validation/ab/tests/test_behavior.py`.

**Arm leak — disclosed, not discarded.** I did not go looking for the mapping and I do not know which lettered arm this
is. But `artifact_F/REVISION-NOTES.md` repeatedly cites "Section 1", "Section 3", "Section 5" and "Section 6" of an arm
prompt I have not read, and quotes their content (accidental-structure bullets, "name any test you removed", a
do-not-open list). From that I can infer this subject received a structural/simplicity prompt and is therefore not a bare
control arm. Recording it as required.

**Neither artifact tree was edited.** All fault seeding was done on copies under the session scratchpad. I verified after
finishing that both blind trees are unmodified.

**Mechanical block vs my judgement — one disagreement, and it is the finding.** `mechanical.json` on the `F` card prints
`totals_code_only` and `before_totals_code_only` as two separate tables, which is the shape of a before/after
measurement and reads as though a revision occurred. Every figure in the two tables is identical, because the two trees
are byte-identical. The block is formally honest — it refuses the subtraction at `mechanical.json:78` — but its
*structure* implies a change that did not happen. A reader skimming for a delta would find none and might conclude the
change was neutral; the truth is there was no change. That gap between what the instrument's shape suggests and what the
trees contain is the disagreement I am required to report.

### What I REJECTED

- **D2 = 3 on `F`.** Rejected on the empty diff. Detailed at length in the D2 rationale: the analysis is not a
  simplification, identical tables are not a measured null, and the author's brief permitting "no change" is not this
  rubric's anchor.
- **D2 = 1 on either tree.** Rejected firmly. The relationship between figures and design is argued unusually well, and
  on `F` it is argued *against the artifact's own interest* (`REVISION-NOTES.md:182-183`).
- **D2 = 3 on `E`.** Considered because `NOTES.md:59-102` reads like a simplification narrative ("available is derived,
  not stored", "nothing was deleted here"). Rejected: those are choices made while first writing greenfield code, and
  `mechanical.json` records `before_tree_label: null`. There is no before, so "both recorded" is unsatisfiable.
- **D1 = 4 and D4 = 3/4 on both.** Considered seriously, because my own seeding shows the cases genuinely catch hard
  faults — which is anchor 4's *substance* on D4 and most of anchor 3's on D1. Rejected on provenance: there is no model
  anywhere in either tree. No TLA+, no corpus, no generator, no derivation step; every case is a hand-written pytest
  function. Both anchors gate on "model-derived rather than hand-written", so both cap regardless of how well the
  hand-written cases perform. The ceiling here is the rubric's, not the artifact's, and I preferred to say so than to
  quietly award the higher number.
- **D3 = 3 rather than 4.** Considered, on the argument that `MemoryJournal` ships inside the production package rather
  than under `tests/`, so it might be a second real adapter rather than a fake. Rejected: `test_journal_parity.py:157`
  runs one case list across both, which is literally the anchor's shape under either reading, and my seeded fake-drift
  fault proved the parity is load-bearing.
- **D5 = 4 on `E` under the `disclosure` reading.** Available and legal, and I did not take it. I applied `measured` to
  both cards so the pair is comparable, and say explicitly on both cards that under `disclosure` `E` reaches 4 and the
  one-point gap closes.
- **Evidence found and NOT used:** the complexity descriptor's `state_colocation` of 0.167 and the `ports-and-adapters`
  architecture tag agreement. Both sit in the mechanical block, which rule 7 says is recorded and never scored; I read
  them beside my judgement and scored the code.
- **Tempted to credit and did not:** the sheer quality of `REVISION-NOTES.md`. It is the most disciplined
  refusal-to-change document in this project's history and it is very well written. Rule 4 forbids prose as an input, so
  I converted it into something checkable instead: I tested four of its factual claims by execution (branch-coverage
  table, the vacuous-assertion grep, the "deleting the sort keeps both suites green" claim, and the insertion-order
  printout) and all four were exactly true, down to individual digits. The D5 score rests on those four executions, not
  on the paragraphs.

### Defects worth filing

1. **`domain.py:108`'s sort is unobservable, so `test_ledger.py:46` cannot fail for the reason it exists.** The artifact
   disclosed that the sort is redundant (`REVISION-NOTES.md:163-183`) but did not notice the consequence for its own
   suite. Replacing `sorted(self._holds, key=_issue_order)` with `list(self._holds)` leaves 39 passed and 28 passed.
   I went further than the artifact did: ids are allocated strictly monotonically and `dict` preserves insertion order,
   and across a 400-operation randomised reserve/commit/release probe insertion order **never** diverged from numeric
   order. So no test written against the public API can ever justify that sort. The author's defence (independence from
   two facts that live elsewhere) is a future-proofing argument, not a testable one, and the test that appears to guard
   it is decorative. **This is the one thing I found that the artifact did not find about itself.**
2. **`test_ledger.py:181` asserts a substring that cannot occur.** `assert "journal_" not in source` — `grep -c` returns
   0 on `domain.py`, and the module names it guards against (`file_journal`, `memory_journal`) are checked on the next
   line anyway. Self-disclosed at `REVISION-NOTES.md:260-266`; filing it because a dead assertion in a detection suite is
   worth removing even when it is honestly labelled.
3. **Non-integer amounts corrupt the durable ledger format.** Verified: `reserve("acme", 3.0)` is accepted and writes
   `COMMIT acme 3.0 3.0`. The ledger's own line grammar is integer-shaped and R2's parser in the shared suite does
   `int(line.split()[3])`, which would raise on such a line. Self-disclosed, correctly, as an unspecified case — but it
   is a durable-data defect, not merely an input-validation gap, and that distinction is not drawn.
4. **Queries for an unknown tenant raise `KeyError`** while every command returns a structured rejection. Verified.
   Self-disclosed; noted for completeness as an inconsistency in the observable surface.
