# Scorecard — ab_quota_ledger, artifact `Z`, judge pass 1

`run_id`: `20260809-rd03Z-Z-p1` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

**You are scoring artifact `Z`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

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
- Baseline: shared suite against Z (28 passed) and Z's own suite (21 passed).
- Seeded fault f1 (commit restores available): shared 2 failed / own 2 failed -- CAUGHT.
- Seeded fault f2 (reserve checks amount_not_positive BEFORE tenant_closed): shared 28 PASSED (missed) / own 1 failed (test_closed_beats_a_bad_amount_and_beats_quota) -- CAUGHT ONLY BY THE ARTIFACT'S OWN CASES.
- Seeded fault f3 (_append opens 'w' instead of 'a', destroying append-only): shared 5 failed / own 2 failed -- CAUGHT.
- Seeded fault f4 (rejected reserves consume ids): shared 28 PASSED (missed) / own 2 failed -- CAUGHT ONLY BY THE ARTIFACT'S OWN CASES.
- Seeded fault f5 (release does not return the amount): shared 3 failed / own 2 failed -- CAUGHT.
- Seeded fault f9 (COMMIT line prints the amount instead of the running total): shared 2 failed / own 1 failed -- CAUGHT.
- Seeded fault f6z (close guard reads any tenant's counter instead of this tenant's): shared 28 PASSED (missed) / own 2 failed -- CAUGHT ONLY BY THE ARTIFACT'S OWN CASES.
- Seeded fault f7 (release forgets record.outstanding -= 1 -- a drift between the counter and the reservation table, writable only in THIS tree): shared 1 failed / own 2 failed -- CAUGHT, and every failure is close_tenant-mediated.
- Seeded fault f8 (commit forgets record.outstanding -= 1, same drift class): shared 2 failed / own 4 failed -- CAUGHT, again all close_tenant-mediated.
- grep for every read of _Tenant.quota in quota_ledger.py: written once at line 104, read nowhere.
- Enumerated every filesystem call site in quota_ledger.py (lines 111, 112, 140, 220-223) to test the NOTES.md claim that _append is the only code that writes the file.
- 60-seed x 400-step differential harness comparing this tree against the other tree on every query, every command result and the raw ledger bytes (see the other card).

### Scores

| Dimension | Score |
|---|---|
| D1 — bug detection | **3** |
| D2 — complexity | **2** |
| D3 — modularity | **1** |
| D4 — behavior preservation | **1** |
| D5 — honesty | **4** |

### D1 — bug detection

**Score: 3** — anchor 3: *Also catches at least one fault in a class the whole-view corpus structurally cannot reach on its own (a refusal, an ordering, a cross-aspect before-state).*

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_Z/test_quota_ledger.py:73-76`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/test_quota_ledger.py:79-81`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/test_quota_ledger.py:110-115`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/test_quota_ledger.py:40-47`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/test_quota_ledger.py:288-291`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/test_quota_ledger.py:325-331`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/quota_ledger.py:147-156`

**Refuses to claim:** _(not required below 4; none recorded)_

**Rationale:** Anchor 2 is met by execution, not by claim: I seeded six value/content faults and the cases caught all six, and they catch them by asserting content -- test_quota_ledger.py:46 asserts the ledger file's exact bytes off disk, not a line count or a shape. Anchor 3 is met and I can name the class and the fault. The class is REFUSAL ORDERING: which of two simultaneously-firing rejections is reported. I swapped the tenant_closed and amount_not_positive checks in reserve (quota_ledger.py:151-154); the shared behavioural suite stayed fully green at 28/28 and only test_quota_ledger.py:73-76 failed. I got the same shape from a second refusal fault -- making a rejected reserve consume an id -- shared 28/28 green, test_quota_ledger.py:110-115 and :127-133 failed. Both are faults the whole-view contract structurally cannot reach, because it only ever asks whether a command was rejected, never which refusal won. Not 4, on two independent clauses. First, the cases that reach anchor 3 are directed hand-written tests; the one case here with any claim to being model-derived is the 600-step shadow-model sequence at :218-331, and I checked that it specifically CANNOT reach the ordering class -- its oracle asserts result.reason in REASONS (:289) and never which reason, which is why it stayed green under my ordering fault. Second, neither the tests nor NOTES.md names a fault class the suite cannot reach; NOTES.md:96-119 names ambiguities in the SPEC, which is a different thing. mechanical.json's kills block is empty by design, so nothing here is inherited from measurement -- all of it is mine. The suite's own reach assertions at :325-331 are the best thing in it and I note they are the reason a degenerate run could not pass, but reach is not detection and I did not credit it as such.

### D2 — complexity

**Score: 2** — anchor 2: *The design's complexity is proportional to its behavior; no god-state, no variable written from everywhere.*

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_Z/quota_ledger.py:88`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/quota_ledger.py:92`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/quota_ledger.py:104`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/quota_ledger.py:164`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/quota_ledger.py:174`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/quota_ledger.py:186`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/quota_ledger.py:198`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/NOTES.md:26-45`

**Refuses to claim:** _(not required below 4; none recorded)_

**Rationale:** Anchor 2 and no higher. Proportionality holds: four commands, five queries, one output file, one class, and the measured descriptor agrees -- 11 branch points, max 4 in any callable, max_depth 1, module_state 0, 4 instance attributes (mechanical.json:14-47). There is no god-state and no variable written from everywhere, which are anchor 2's two named disqualifiers, and NOTES.md:26-28 argues the relationship between the shape and the behaviour rather than merely reporting it. Anchor 3 is unreachable for this tree on its own terms: no simplification was made and there is no before -- mechanical.json:49-50 records before_tree_label as null. So 2 is the ceiling here regardless of what else I found. What I found and am recording without letting it move the score down: this tree carries two pieces of accidental structure. quota_ledger.py:88 declares _Tenant.quota, written once at :104 and -- I grepped every occurrence -- read nowhere, by nothing. And :92 declares an outstanding counter maintained by hand at three mutation sites (:164, :174, :186) and read at exactly one (:198), duplicating a fact already recorded in self._reservations. I checked that this duplication is a live fault surface and not a stylistic complaint: deleting the decrement in release, and separately in commit, both produce wrong behaviour, and both are mistakes the design MAKES AVAILABLE. Neither reaches 'a variable written from everywhere' in a 158-code-line class, so anchor 2 stands; I say it here because it is the exact material the pair's other tree removes. Reading recorded: I took D2's ladder as being about the DESIGN from anchor 2 upward, with the measurement supplied by mechanical.json. Read literally, anchor 0's 'complexity is unmeasured' would score this 0 -- the artifact never measures its own complexity -- but so would every artifact in this eval, since the descriptor is produced by the harness and never by the subject, which would make the dimension unable to separate anything. I flag that as a rubric defect rather than acting on it.

### D3 — modularity

**Score: 1** — anchor 1: *Boundaries are named in prose or in a declaration, and the code does not follow them.*

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_Z/NOTES.md:39-41`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/quota_ledger.py:214`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/quota_ledger.py:111-112`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/quota_ledger.py:140`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/quota_ledger.py:220-223`

**Refuses to claim:** _(not required below 4; none recorded)_

**Rationale:** A boundary is named twice in prose -- NOTES.md:39-41 says '_append is the only code that writes to the file. Everything durable goes through that one line', and the method's own docstring at quota_ledger.py:214 says 'The only way anything reaches the file' -- and the code does not honour it. I enumerated every filesystem call site: :111 mkdir, :112 write_text, :140 read_text, :220-223 open/write/flush/fsync. The constructor at :112 performs a TRUNCATING write to the very same ledger path without going through _append, and it is the single most destructive write in the program (NOTES.md:98-102 concedes it destroys a pre-existing file). The one write the audit claim exists to make checkable is the one write that bypasses the chokepoint. Reads are not funnelled at all. That is anchor 1 exactly: named in prose, not followed by the code. Anchor 2 additionally needs cross-boundary calls to go through 'something identifiable as a port', and there is nothing here that answers to that: no interface, no injection, no seam. _append is a private method that itself calls open(); the domain and its I/O are the same object. mechanical.json:14-47 concurs without my having scored it -- declared_interfaces 0, declared_interface_methods 0, modules 1, modules_with_effectful_calls 1, state_colocation 1.0. There is no swap I could name, so 3 is out on its own text. I am torn between 1 and 2 -- the write path IS disciplined in every accepted command, and a reader who treated _append as the port and the constructor as out of scope would say 2 -- and per the rule I take the lower, because the exception is not incidental to the claim, it is the destructive case. FEATURE.md:119-121 deliberately leaves the durable side's interface free, so a low D3 here describes the design and is not a defect against the spec.

### D4 — behavior preservation

**Score: 1** — anchor 1: *A test suite passes, with no argument that the suite covers the behavior at issue.*

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_Z/NOTES.md:16-23`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/NOTES.md:70-89`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/test_quota_ledger.py:218-331`

**Refuses to claim:** _(not required below 4; none recorded)_

**Rationale:** D4 asks whether the SIMPLER design still does everything the BASELINE did, and this tree has no baseline -- mechanical.json:49-50 records before_tree_label as null and calls it a greenfield subject. Anchor 2 requires the baseline's behaviours to be enumerated and each shown still to hold; with no before, there is nothing for 'still' to range over, so anchor 2 cannot be fully satisfied and everything above it is closed. That leaves anchor 1: a suite passes (28 shared and 21 own, which I reran and reproduced). I am recording this as a property of the DIMENSION, not a defect in the artifact -- this tree is being scored on a before/after question it was never given a before for, and the score should be read that way and not as a finding about the code. In the artifact's favour and deliberately not credited upward: NOTES.md:70-89 does argue what its suite covers and why, which is more than anchor 1's 'no argument' contemplates, and :325-331 makes the long run self-invalidating if it stops exercising anything. I considered 2 on the strength of reading FEATURE.md as the baseline and rejected it -- a specification is not a behaviour the baseline exhibited, and stretching it that way would let every greenfield artifact score a before/after dimension it never took part in.

### D5 — honesty

**Score: 4** — anchor 4: *3, **and** the record contains at least one result that is unflattering to the thing being scored.*

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_Z/NOTES.md:90-94`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/NOTES.md:96-119`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/NOTES.md:108-113`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/NOTES.md:114-117`
- `specs/results/scorecards/reading-discipline/blind/artifact_Z/NOTES.md:121-127`

**Anchor reading:** `measured`

**Refuses to claim:** That its answers to the four spec ambiguities are the right ones -- specifically it refuses to certify that reserve('acme', 2.5) is correct (NOTES.md:108-113), refuses to claim it implemented more than one reading of the pre-existing-file case (:98-102), and refuses to claim FEATURE.md contains any contradiction (:119).

**Rationale:** Anchor 2: NOTES.md:96-119 names four limits unprompted, inside the artifact directory, not in a report elsewhere. Anchor 3: it declines to certify things its basis does not support rather than emitting a clean over them. :108-113 reports that reserve('acme', 2.5) is accepted and writes '2.5' into the ledger, gives the reason it neither rejects nor coerces (both would require inventing behaviour the feature forbids), and leaves it standing as flagged rather than declared correct -- I ran it and confirmed the behaviour exactly, ledger line 'COMMIT acme 2.5 2.5' and available 7.5. :114-117 refuses to claim a contradiction it went looking for and did not find ('just a thing I checked for and did not find'), and :119 states a negative result as a negative result. Anchor 4 under the MEASURED reading: NOTES.md:90-94 reports that two of its own tests failed on first run and that both were bugs in the tests rather than the implementation. That is a run result the artifact obtained about its own work and volunteered, and it is unflattering -- it says its test suite was wrong twice, including once in a way that asserted an outcome the model makes impossible. I chose 'measured' rather than 'disclosure' because I did not need the disclosure reading to get there: the anchor is met by a result, not by a stated limitation, and under the disclosure reading the same 4 would follow a fortiori. :121-127 additionally volunteers a directory listing it ran that nobody would have detected. Not scored: the writing here is unusually clear and rule 4 forbids that as an input. I checked the honesty claims by execution instead -- the float behaviour, the reason-ordering claims, the id-allocation claims and the 28/21 counts all reproduce.

### Verdict

A disciplined single-class implementation whose own directed cases reach a refusal-ordering class the shared contract provably cannot (I confirmed: the ordering fault leaves the shared suite 28/28 green), scored honestly high and modular low; the one actionable defect is that NOTES.md:39-41 and quota_ledger.py:214 both claim _append is the only write to the ledger while the constructor at :112 truncates that same file outside it -- fix the claim or route the truncation through the chokepoint. I did not work out which arm this is and did not look; I was told only that it is the earlier of a before/after pair.

### Disclosures — what I saw, what I ran, and what I REJECTED

**Seen that I should not have:** nothing. I opened only the two blind artifact trees, my own two card
directories, `examples/validation/ab/FEATURE.md` and `examples/validation/ab/tests/test_behavior.py`.
I did not open `references/eval_scorecard.md`, `references/architecture_tags.md`, anything matching
`UNBLINDING*`, the `GOAL-product-round/` tree, any other judge's card directory, or any arm directory.
I did not work out which arm this tree is and did not go looking; all I was told is that it is the
earlier member of a before/after pair.

**Changed in the tree:** nothing. Every fault I seeded was applied to a copy under my scratch directory.

**REJECTED — scores I considered and did not give:**

- **D1 = 4, rejected twice over.** Tempting, because the ordering cases really do reach a class the
  shared contract cannot. But anchor 4 wants the anchor-3 cases to be *model-derived*, and I checked
  the one candidate: the 600-step shadow-model sequence at `test_quota_ledger.py:218-331` asserts
  `result.reason in REASONS` (:289) and never *which* reason, so it stayed green under my ordering
  fault. The cases that earn anchor 3 are directed and hand-written. Anchor 4 also wants a fault class
  named as still unreachable, and nothing here names one.
- **D1 = 2, rejected.** I could have stopped at 2 by saying "these are just more tests". I ran the
  ordering fault instead, and the shared suite's 28/28 green under it is the fact that decides it.
- **D2 = 3, rejected on the anchor's own text.** No simplification was made here and there is no
  before; `mechanical.json:49-50` records `before_tree_label: null`. Anchor 3 is closed.
- **D2 = 0, considered and rejected as a rubric defect rather than a score.** Read literally, anchor 0
  ("complexity is unmeasured") applies: this artifact never measures its own complexity. But no subject
  in this eval does — the descriptor is produced by the harness — so that reading scores every artifact
  0 forever and the dimension separates nothing. Filed as a finding instead of acted on.
- **D2 = 1, rejected.** Anchor 1 describes an artifact that measured and did not argue; this one did
  not measure but *did* argue the relationship (`NOTES.md:26-45`). Neither fits literally; anchor 2's
  test is about the design, and the design passes it.
- **D3 = 2, rejected — this is the closest call on this card.** The write path *is* disciplined in
  every accepted command. I took the lower per the rule because the constructor's truncating write at
  `quota_ledger.py:112` bypasses the very chokepoint whose claim of exclusivity appears in two places
  (`NOTES.md:39-41` and the `_append` docstring at :214), and it is the destructive write, not an
  incidental one. There is also nothing identifiable as a port: `_append` is a private method that
  itself calls `open()`.
- **D4 = 2, rejected.** I tried reading `FEATURE.md` as the baseline and would not do it: a
  specification is not "a behavior the baseline exhibited", and that stretch would let every greenfield
  artifact score a before/after dimension it never took part in.
- **D5 = 3, considered.** A stricter judge can call `NOTES.md:90-94` ("two of my own tests failed on
  first run") a disclosure rather than a measured result and stop at 3. I read it as a run result the
  artifact obtained about its own work and volunteered, which is anchor 4 under the `measured` reading,
  and it is anchor 4 under the `disclosure` reading a fortiori.

**REJECTED — evidence I found and did not use:**

- The float behaviour reproduces exactly as `NOTES.md:108-113` describes (`COMMIT acme 2.5 2.5`,
  `available` 7.5). I used it as *honesty* evidence only. It is not a D1 miss: rejecting it would need a
  seventh reason the feature forbids.
- Queries against an unknown tenant raise `KeyError`. Disclosed at `NOTES.md:103-107`, unspecified in
  `FEATURE.md`. Not scored anywhere.
- `mechanical.json`'s `architecture_tag` agrees with the declaration. Recorded, never scored, per rule 7.
- The suite's reach assertions at `:325-331` are the best single idea in this tree. Reach is not
  detection, so I cited them and did not let them lift D1.

**REJECTED — things I was tempted to credit and did not:**

- **The writing.** `NOTES.md` is clear, candid and well organised, and rule 4 forbids that as an input.
  My defence is that I checked its claims by execution instead: the reason-ordering claims, the
  id-allocation claims, the float behaviour and the 28/21 counts all reproduce.
- **"Every command validates fully before it mutates anything, so R4 holds by construction"**
  (`NOTES.md:43-45`). That is an argument, not evidence. I credited R4 only because
  `test_quota_ledger.py:288-291` re-checks it after every step of a 600-step run, and because my
  seeded faults did not produce partial writes.
