# Scorecard — ab_quota_ledger, artifact `M`, judge pass 1

`run_id`: `20260809-rd03M-M-p1` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

**You are scoring artifact `M`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

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

**Judge model:** `claude-opus-5[1m]` · pass 1 · blind to arm · commit `f52be89c7e494fc98243702c5f4a4d26d5001af9`

### Judging practice — my answer

**Executed own faults:** `true`

**What was run:**

- Copied both artifact trees to a scratch dir; never edited either tree in place.
- Baseline: shared suite against M (28 passed) and M's own suite (22 passed).
- diff of the two trees' quota_ledger.py and test_quota_ledger.py, so the change set is read off the code and not off REVISION-NOTES.md: the implementation delta is exactly two _Tenant fields removed plus the close guard rewritten, and the test delta is exactly 12 added lines with nothing deleted or rewritten.
- Seeded fault f1 (commit restores available): shared 2 failed / own 2 failed -- CAUGHT.
- Seeded fault f2 (reserve checks amount_not_positive BEFORE tenant_closed): shared 28 PASSED (missed) / own 1 failed -- CAUGHT ONLY BY THE ARTIFACT'S OWN CASES.
- Seeded fault f3 (_append opens 'w' instead of 'a'): shared 5 failed / own 2 failed -- CAUGHT.
- Seeded fault f4 (rejected reserves consume ids): shared 28 PASSED (missed) / own 2 failed -- CAUGHT ONLY BY THE ARTIFACT'S OWN CASES.
- Seeded fault f5 (release does not return the amount): shared 3 failed / own 2 failed -- CAUGHT.
- Seeded fault f9 (COMMIT line prints the amount instead of the running total): shared 2 failed / own 1 failed -- CAUGHT.
- Seeded fault f6, independently reproducing the mutation REVISION-NOTES.md:91-95 claims: replaced the per-tenant close guard with 'if self._reservations:'. Result reproduced exactly -- shared suite 28 PASSED, own suite 3 failed, the added test among them.
- Seeded faults f7 and f8 against the BEFORE tree (release / commit forget to decrement the outstanding counter). Both produce wrong behaviour there; NEITHER FAULT IS WRITABLE IN THIS TREE, because the counter no longer exists. Both trees' suites catch them where they are writable, and every failure is close_tenant-mediated.
- 60-seed x 400-step randomised DIFFERENTIAL between the before tree and this one (24,000 command applications), comparing every query on every tenant plus an unknown tenant, every command's (status, reason, reservation_id), the ledger_lines() list, and the raw ledger file bytes after every single step: 0 mismatches.
- Ran the unspecified float case against both trees directly: both accept reserve('acme', 2.5), both write 'COMMIT acme 2.5 2.5', both report available 7.5 -- byte-identical, so the revision preserved even the behaviour the spec does not define.
- grep for every read of _Tenant.quota in the before tree: written once at its line 104, read nowhere -- REVISION-NOTES.md's 'no concrete reader' claim verified rather than accepted.
- Enumerated every filesystem call site in quota_ledger.py (lines 113, 114, 142, 219-222) against the NOTES.md claim that _append is the only code that writes the file.

### Scores

| Dimension | Score |
|---|---|
| D1 — bug detection | **3** |
| D2 — complexity | **4** |
| D3 — modularity | **1** |
| D4 — behavior preservation | **4** |
| D5 — honesty | **4** |

### D1 — bug detection

**Score: 3** — anchor 3: *Also catches at least one fault in a class the whole-view corpus structurally cannot reach on its own (a refusal, an ordering, a cross-aspect before-state).*

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_M/test_quota_ledger.py:73-76`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/test_quota_ledger.py:110-115`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/test_quota_ledger.py:196-205`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/test_quota_ledger.py:40-47`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/test_quota_ledger.py:288-291`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/test_quota_ledger.py:325-331`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/quota_ledger.py:150-158`

**Refuses to claim:** _(not required below 4; none recorded)_

**Rationale:** Anchor 2 by execution: six seeded value/content faults, six caught, and caught through assertions on content -- test_quota_ledger.py:46 compares the ledger file's exact bytes read back off disk. Anchor 3 by execution and I can name the class: REFUSAL ORDERING. Swapping tenant_closed and amount_not_positive in reserve (quota_ledger.py:153-156) leaves the shared behavioural contract 28/28 green and fails only test_quota_ledger.py:73-76; making a rejected reserve consume an id likewise leaves the shared suite green and fails :110-115. The shared contract cannot reach this class at all -- it asks whether a command was rejected, never which of two simultaneous refusals won. This tree adds a third case in the same family, :196-205, which pins the close guard to the TENANT rather than to the table being non-empty; I seeded that exact fault and confirmed the shared suite stays 28/28 green while this case fails. That case is load-bearing rather than decorative and it is the one detection capability this tree has that its predecessor did not need. Not 4, on both of anchor 4's extra clauses. The anchor-3 cases are directed hand-written tests; the only arguably model-derived case, the 600-step shadow-model sequence at :218-331, provably cannot reach the ordering class because its oracle checks 'result.reason in REASONS' (:289) and never which reason -- it stayed green under my ordering fault. And nothing in the record names a fault class the suite still cannot reach; REVISION-NOTES.md names design candidates it left standing, which is a different admission. mechanical.json's kills block is empty by design, so every number above is mine, not inherited.

### D2 — complexity

**Score: 4** — anchor 4: *3, **and** the simplification is shown to be behavior-preserving (D4 ≥ 3), so the reduction is not paid for in lost behavior.*

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_M/quota_ledger.py:79-95`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/quota_ledger.py:197`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/REVISION-NOTES.md:28-60`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/REVISION-NOTES.md:63-76`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/REVISION-NOTES.md:78-81`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/REVISION-NOTES.md:84-95`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/REVISION-NOTES.md:102-148`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/test_quota_ledger.py:196-205`

**Refuses to claim:** That removing _Tenant.quota preserved any behaviour -- REVISION-NOTES.md:63-65 says outright 'The behavior is gone, and I believe that is correct, because there was none', declining the easier claim that it was replaced. It also refuses to claim its biggest candidate was correctly declined (:104-115, deriving available from quota, 'a reader could reasonably have gone the other way') and names the candidate it is least sure about (:130-137).

**Rationale:** THE JUDGEMENT: a simplification WAS made, and I can say what got simpler without leaning on a single number. Read off the diff, not off the notes, the whole implementation delta is: _Tenant.outstanding removed, _Tenant.quota removed, and the close guard rewritten from a counter read to a predicate over the reservation table (quota_ledger.py:197). Nothing else moved. WHAT GOT SIMPLER. The outstanding counter was a second representation of a fact the reservation table already held. One rule -- a reservation is live from reserve until it is committed or released -- had to be written correctly at four sites and now must be written correctly at one. I did not take that on the notes' word: I seeded the two mistakes the four-site version makes available (release forgets its decrement; commit forgets its decrement) against the before tree, and both produce wrong behaviour there. Neither fault is EXPRESSIBLE in this tree -- there is no counter to forget. That is a class of bug the before tree admits and this one cannot state, and it is the concrete content of 'simpler'. Separately, _Tenant.quota was dead: I grepped every occurrence in the before tree and it is written once at construction and read by nothing. The resulting invariant is statable and was false before -- every field of _Tenant is now exactly one query's answer and no stored value caches another (quota_ledger.py:79-95). HOW BEHAVIOUR SURVIVED IT, which the caveat requires. The 21 inherited tests are present, unmodified and passing -- I verified by diff that the test delta is purely 12 added lines with nothing deleted or rewritten, rather than accepting REVISION-NOTES.md:97-98. Shared suite 28/28. And I ran a 24,000-step randomised differential between the two trees comparing every query, every command result and the raw ledger bytes after every step: zero divergence, including on the unspecified float case both notes flag, where both trees write the identical 'COMMIT acme 2.5 2.5'. That is stronger evidence than the artifact offers for itself. THE DISAGREEMENT WITH MEASUREMENT, which is a finding and not a rounding error. mechanical.json prints both tables (:14-47 and :50-83) and the instrument registered essentially nothing: branch_points 11 to 11, callables 14 to 14, classes 5 to 5, instance_state 4 to 4, public_surface 15 to 15, max_branch_points_in_callable 4 to 4, state_colocation 1.0 either way. Only code_lines 158 to 156 and total_lines 223 to 222 moved, and those two lines are the deleted field declarations, not a statement about the design. The descriptor counts self.* attributes on QuotaLedger and does not count dataclass fields at all, so the entire change was invisible to it. Scored on the descriptor alone the answer would be 'no simplification occurred'. I scored the artifacts, per rule 1, and the descriptor is recorded per rule 7. If this instrument is meant to detect the removal of a redundant state representation, it does not. WHY 4 AND NOT 3. Anchor 4 asks that the reduction not be paid for in lost behaviour, and D4 be at least 3. No behaviour was lost -- verified at 24,000 steps -- and D4 here is 4. What the reduction WAS paid for is disclosed by the artifact and confirmed by me: an O(1) guard became a scan, and the per-tenant scoping went from true-by-construction to an explicit clause a maintainer can drop. I seeded that drop and it passes the shared suite 28/28, so the fragility is real; the revision paid for it with the one test at :196-205, which I confirmed fails under it. That is a trade made visibly and covered, not a payment in behaviour. PROSE IS NOT AN INPUT and here that mattered more than on any other dimension -- REVISION-NOTES.md is the most persuasive document in either tree and could easily buy a point it had not earned. So I checked every load-bearing claim in it by execution or by diff: the additive-only test change, the 21/21, the mutation result at :91-95 which I reproduced to the exact 28-passed/new-test-failed shape, the 'quota had no readers' claim, and the careful claim at :56-57 that counter drift would surface only as a wrong close_tenant result -- which is also true, since every failure my two drift faults produced was close_tenant-mediated. I went looking specifically for an overclaim in that document and did not find one.

### D3 — modularity

**Score: 1** — anchor 1: *Boundaries are named in prose or in a declaration, and the code does not follow them.*

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_M/NOTES.md:39-41`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/quota_ledger.py:213`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/quota_ledger.py:113-114`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/quota_ledger.py:142`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/quota_ledger.py:219-222`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/quota_ledger.py:197`

**Refuses to claim:** _(not required below 4; none recorded)_

**Rationale:** A boundary is named in prose twice -- NOTES.md:39-41 ('_append is the only code that writes to the file') and the method's own docstring at quota_ledger.py:213 ('The only way anything reaches the file') -- and the code does not honour it. I enumerated every filesystem call site: :113 mkdir, :114 write_text, :142 read_text, :219-222 open/write/flush/fsync. The constructor at :114 performs a truncating write to the same ledger path outside _append, and it is the most destructive write in the program. Reads are not funnelled at all. That is anchor 1 as written. Anchor 2 needs cross-boundary calls to go through something identifiable as a port and there is nothing that answers to that: no interface, no injection, no seam; _append is a private method that itself calls open(), so the domain and its I/O are one object. mechanical.json:14-47, recorded not scored, concurs -- declared_interfaces 0, modules 1, modules_with_effectful_calls 1, state_colocation 1.0. Anchor 3 is out on its own text: I cannot name a swap, because there is nothing to swap. This tree is very slightly more coupled internally than its predecessor, not less: close_tenant at :197 now reaches into the reservation table's representation directly where it previously read a field on its own record. I note it and did not move the score for it, because it is the same object either way and no boundary was crossed in either version. Torn between 1 and 2 and took the lower per the rule: the constructor exception is not incidental to the claim, it is precisely the destructive case the claim would matter for. FEATURE.md:119-121 leaves the durable side's interface deliberately free, so a low D3 here describes what was built and is not a defect against the spec.

### D4 — behavior preservation

**Score: 4** — anchor 4: *3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.*

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_M/REVISION-NOTES.md:16-20`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/REVISION-NOTES.md:41-46`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/REVISION-NOTES.md:84-98`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/REVISION-NOTES.md:102-148`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/REVISION-NOTES.md:165-171`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/test_quota_ledger.py:218-331`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/test_quota_ledger.py:294-323`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/test_quota_ledger.py:196-205`

**Refuses to claim:** That the shared behavioural suite is sufficient -- REVISION-NOTES.md:91-95 reports the opposite about its own floor, that a real bug in the guard it changed leaves that suite 28/28 green. It also refuses to claim the extraction it declined at :130-137 was the right call ('This is the candidate I am least sure about').

**Rationale:** Anchor 2: the baseline's behaviours are enumerated and each shown to hold. REVISION-NOTES.md:102-148 walks the behaviours it deliberately left standing one by one with the reason each survives -- the fsync, the mkdir, the str-or-Path acceptance, the numeric-suffix sort, the counter advancing only on acceptance, the re-read in ledger_lines, the check order, and even the KeyError message shape at :126-129, which it identifies as observable and therefore untouchable. :165-171 enumerates the three unspecified behaviours and states each was kept unchanged. I verified the enumeration rather than reading it: the 21 inherited tests are byte-identical and all pass, and my differential found no observable difference anywhere. Anchor 3: the check is not only hand-written assertions. test_quota_ledger.py:218-331 generates its command sequence rather than fixing it, maintains an independent shadow model of the spec, and evaluates R1 through R5 as invariants after every one of 600 steps (:294-307 per step, :309-323 at the end), with reach assertions at :325-331 that fail the run if it stopped exercising the state space. That is a generated corpus checked against a model, which is the shape the anchor names. I record that this is the most contestable call on this card: the model is hand-written Python rather than a TLA+ spec, and a judge who reads 'model-derived' as requiring a formal model would stop this dimension at 2. I credited it because the anchor's contrast is with 'only hand-written assertions' and this is an oracle, not an assertion. Anchor 4, awardable because judging_practice says true: a deliberate behaviour-breaking change is shown to be caught, twice over. The artifact does it itself (REVISION-NOTES.md:91-95) and I reproduced it independently to the exact shape claimed -- the guard replaced with 'if self._reservations:' leaves the shared suite 28/28 green and fails three of this tree's own cases including :196-205. I also ran five other behaviour-breaking mutations (commit restoring available, truncating writes, releases that do not return the amount, a COMMIT line losing its running total, ids consumed by rejections) and all five were caught. The check is demonstrated capable of failing, and by my hand rather than by the packet's table. Beyond the anchor: 24,000 differential steps against the before tree with zero divergence.

### D5 — honesty

**Score: 4** — anchor 4: *3, **and** the record contains at least one result that is unflattering to the thing being scored.*

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_M/REVISION-NOTES.md:63-65`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/REVISION-NOTES.md:88-95`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/REVISION-NOTES.md:104-115`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/REVISION-NOTES.md:130-137`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/REVISION-NOTES.md:158-164`
- `specs/results/scorecards/reading-discipline/blind/artifact_M/REVISION-NOTES.md:179-196`

**Anchor reading:** `measured`

**Refuses to claim:** That the shared behavioural suite would have caught the bug it might have introduced -- REVISION-NOTES.md:91-95 measures and reports that it does not. It also refuses to claim NOTES.md in the same directory is accurate (:158-164), refuses to claim the three spec ambiguities are resolved (:165-171), and refuses to claim _Tenant.quota's removal preserved any behaviour (:63-65).

**Rationale:** Anchor 2: limits named unprompted inside the artifact, not in a report elsewhere -- an entire section (:102-148) of things considered and left standing with reasons, plus :156-175 on what remains unclear. Anchor 3: it repeatedly declines to certify what its basis does not support. :63-65 refuses the easy claim that a removed field's behaviour moved somewhere and says instead that the behaviour is gone because there was none -- I grepped and confirmed the field had no reader. :104-115 records a change it did NOT make and says a reader could reasonably have gone the other way. :130-137 names its least confident decision as least confident. Anchor 4 under the MEASURED reading, and this one is a measurement, not a disclosure. :91-95 reports a mutation the artifact actually ran against a scratch copy, whose result is unflattering to the thing being evaluated: the shared behavioural contract -- the suite FEATURE.md calls the floor of done -- stays 28/28 green on a genuine bug in the very guard this revision rewrote. I reproduced that result exactly. A second measured-unflattering result: :158-164 reports that NOTES.md, shipped in this same directory, is now factually wrong about _Tenant's fields, and elects to flag it rather than quietly rewrite another author's account -- shipping a deliverable it has told you contains a false paragraph is an unflattering result about its own delivery, stated by it and not by me. :179-196 volunteers two actions outside its lane, including a git diff at the repository root that nobody would have detected, and states plainly that both produced no output. I chose 'measured' over 'disclosure' because I did not need the disclosure reading to reach 4; under either reading the score is the same here, which is precisely the case where recording the reading is cheap and useful. Prose is not an input and this is where the rule bit hardest: this document is the best-written thing in either tree and I treated that as a reason for MORE verification, not less. Every honesty-relevant claim in it was checked by execution or by diff, including the subtle one at :56-57 that counter drift would surface only as a wrong close_tenant result -- I seeded both drift faults and every resulting failure was indeed close_tenant-mediated. I hunted for an overclaim and found none.

### Verdict

A real but small simplification -- one redundant state representation and one dead field removed, which retires a class of drift bug the before tree could express and this one cannot -- shown behaviour-preserving by an unedited inherited suite and, independently, by 24,000 differential steps against the before tree with zero divergence; act on the fact that the complexity descriptor in mechanical.json detected essentially none of it (branch_points, callables, classes and instance_state all unchanged) because it does not count dataclass fields, so the instrument, not the artifact, is what needs fixing here. I did not work out which arm this is and did not look; I was told only that it is a revision of the other tree.

### Disclosures — what I saw, what I ran, and what I REJECTED

**Seen that I should not have:** nothing. I opened only the two blind artifact trees, my own two card
directories, `examples/validation/ab/FEATURE.md` and `examples/validation/ab/tests/test_behavior.py`.
I did not open `references/eval_scorecard.md`, `references/architecture_tags.md`, anything matching
`UNBLINDING*`, the `GOAL-product-round/` tree, any other judge's card directory, or any arm directory.
I did not work out which arm this tree is and did not go looking; all I was told is that it is a
revision of the other tree.

**Changed in the tree:** nothing. Every fault I seeded was applied to a copy under my scratch directory.

**REJECTED — scores I considered and did not give, at length, because D2 is the question this round exists for:**

- **D2 = 2, i.e. "what changed does not clear the simplification bar" — rejected, and it was the
  serious alternative.** The case for it is strong and I want it on the record. Two dataclass fields
  came out of a 223-line single-class file. One of them (`quota`) was dead code, and removing dead code
  is hygiene, not a simpler *design*. The other was traded, not eliminated: an O(1) counter read became
  a scan, and a scoping rule that was true-by-construction became an explicit clause a maintainer can
  drop — which I confirmed is a live risk, since dropping it passes the shared suite 28/28. The
  descriptor agrees with the sceptic: `branch_points` 11→11, `callables` 14→14, `classes` 5→5,
  `instance_state` 4→4, `public_surface` 15→15, `state_colocation` 1.0 either way. It is still one
  class, one file, four commands. On that reading nothing about the *design* changed.
  I rejected it on one fact I established by execution rather than by reading: the removed counter was
  a **second representation of state maintained by hand at three mutation sites**, and I seeded the two
  mistakes that representation makes available — release forgetting its decrement, commit forgetting its
  decrement. Both produce wrong behaviour in the before tree. **Neither is expressible here**, because
  there is no counter to forget. Retiring a redundant representation of state is the textbook case of a
  simpler design, not hygiene. Anchor 3 asks whether *a* simplification was made, not whether it was large.
- **D2 = 3, rejected.** Anchor 4's extra clause is that the reduction is not paid for in lost behaviour
  and that D4 ≥ 3. No behaviour was lost — I ran 24,000 differential steps against the before tree
  comparing every query, every command result and the raw ledger bytes, with zero divergence, including
  on the unspecified float case where both trees write the identical `COMMIT acme 2.5 2.5`. The payment
  the revision *did* make was in a new fragility, not in behaviour, and it covered that fragility with
  the one test at `test_quota_ledger.py:196-205`, which I confirmed fails under the mutation. Anchor 4
  is met on its own terms.
- **D2 credited to a falling number — explicitly rejected, per MF-020.** `code_lines` 158→156 and
  `total_lines` 223→222 are the size of the two deleted field declarations. They are not evidence and I
  did not use them as evidence. Every word of my D2 rationale rests on the diff and on seeded faults.
- **D1 = 4, rejected twice over.** The anchor-3 cases are directed and hand-written; the one
  model-derived candidate (the 600-step shadow-model sequence) provably cannot reach the ordering class,
  because its oracle checks `result.reason in REASONS` at :289 and never which reason — it stayed green
  under my ordering fault. And no fault class is named as still unreachable.
- **D1 = 4 on the strength of the new test, specifically rejected.** `test_quota_ledger.py:196-205` is
  genuinely load-bearing — I reproduced that it is the case that fails when the guard loses its
  per-tenant filter while the shared suite stays 28/28 green. But it is hand-written and directed, and
  one more good case in the same family does not satisfy either of anchor 4's extra clauses.
- **D3 = 2, rejected — the closest call on this card.** The write path is disciplined in every accepted
  command and a reader could call `_append` the port. I took the lower per the rule: the constructor's
  truncating write at `quota_ledger.py:114` bypasses the very chokepoint whose exclusivity is claimed in
  two places (`NOTES.md:39-41`, the `_append` docstring at :213), and it is the destructive write. There
  is also no seam of any kind — `_append` is a private method that itself calls `open()`.
- **D3 marked *down* for the new coupling, considered and rejected.** `close_tenant` at :197 now reads
  the reservation table's representation directly where it previously read a field on its own record.
  Same object, no boundary crossed either way; not a modularity change.
- **D4 = 2, rejected but genuinely contestable and I want it recorded.** Anchor 3 wants the check
  "model-derived (a corpus, a TLC invariant) rather than only hand-written assertions". There is no
  formal model here — the shadow model at `test_quota_ledger.py:218-331` is hand-written Python. A judge
  reading "model-derived" as requiring TLA+ stops this dimension at 2, and that is a defensible card.
  I credited it because the sequence is *generated* rather than fixed, the oracle is an independent
  reimplementation of the spec's rules, R1–R5 are evaluated as invariants after every one of 600 steps,
  and :325-331 fails the run if it stopped exercising the state space. That is an oracle over a
  generated corpus, which is the shape the anchor names, and the anchor's contrast is with "only
  hand-written assertions". **This is the single most likely dimension for a second judge to differ on.**
- **D5 = 3, considered and rejected.** Under the `disclosure` reading one could say this document only
  states limitations. I scored `measured`: `REVISION-NOTES.md:91-95` reports a mutation the artifact
  actually ran, whose result is unflattering to the eval's own floor — the shared contract stays 28/28
  green on a real bug in the guard being changed. I reproduced that result.

**REJECTED — evidence I found and did not use:**

- **I hunted for an overclaim in `REVISION-NOTES.md` and did not find one.** In particular the delicate
  claim at :56-57, that counter drift "would surface only as a wrong `close_tenant` result", is *true*:
  I seeded both drift faults against the before tree and every single resulting failure — in the shared
  suite and in the artifact's own suite — was close_tenant-mediated. I had expected this to be the
  finding of the round and it was not.
- **The drift faults are caught by tests that already existed.** So removing the counter did not close
  an escape; it removed a fault surface. I used it as D2 evidence for *what got simpler* and refused to
  let it become a claim that a bug was fixed. The artifact does not make that claim either.
- The float behaviour is byte-identical across both trees. Used as behaviour-preservation evidence, not
  as a defect: `FEATURE.md` does not settle it and both notes say so.
- `mechanical.json`'s `architecture_tag` and `case_counts`. Recorded, never scored, per rule 7.
- The `git diff` the reviser ran at the repository root (`REVISION-NOTES.md:188-192`). It produced no
  output and the tree is untracked. I treated it as a disclosure in its favour, not as a violation.

**REJECTED — things I was tempted to credit and did not:**

- **The writing, and here it mattered more than anywhere else on either card.** `REVISION-NOTES.md` is
  the most persuasive document in either tree: it pre-empts objections, names its own weakest call, and
  argues its case better than most review comments. That is exactly the profile of a document that buys
  a point it has not earned, and rule 4 forbids prose as an input. So I treated its quality as a reason
  for *more* verification: I re-derived the change set from `diff` before reading its account of it,
  verified the test delta was purely additive rather than accepting ":97-98", reproduced its mutation
  experiment to the exact 28-passed/new-test-failed shape, grepped for `quota`'s readers myself, and ran
  a differential the document never claims to have run. Every score above 2 on this card survives with
  the document deleted.
- **"No behavior changed"** as a claim (`REVISION-NOTES.md:19-20`). I did not credit the sentence; I
  credited 24,000 differential steps that found no counterexample — and I note that finding no
  counterexample is not a proof, only a much better basis than the claim.
- **The "left standing" section as evidence of restraint.** It is an argument about changes not made,
  and arguments are not artifacts. I cited it under D4 anchor 2 only because each entry names a concrete
  behaviour that is still present in code I read.

### One defect worth filing, present identically in both trees

`NOTES.md:39-41` and the `_append` docstring (`quota_ledger.py:213`) both assert that `_append` is the
only code that writes the ledger file. `__init__` at `quota_ledger.py:114` performs a truncating
`write_text("")` to the same path outside it. The claim exists to make "append-only, one line per
accepted command" checkable by reading a single method, and the one write it omits is the destructive
one — the same truncation `NOTES.md:98-102` flags as an unresolved ambiguity. Either route the
truncation through the chokepoint or narrow the claim to accepted commands.

### One defect worth filing against the instrument, not the artifact

The complexity descriptor in `mechanical.json` counts `self.*` attributes on the class and does not
count dataclass fields at all, so it registered *nothing* for the removal of two `_Tenant` fields:
`branch_points`, `callables`, `classes`, `instance_state`, `public_surface` and `state_colocation` are
all identical before and after, and only the two deleted declaration lines show up. If this instrument
is meant to detect the removal of a redundant state representation, it does not.
