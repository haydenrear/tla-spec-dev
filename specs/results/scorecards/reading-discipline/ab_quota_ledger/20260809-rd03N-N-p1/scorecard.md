# Scorecard — ab_quota_ledger, artifact `N`, judge pass 1

`run_id`: `20260809-rd03N-N-p1` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

**You are scoring artifact `N`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

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
### Judging practice
**Executed own faults:** `true`
**What was run:**
- diff -u and md5 of the two trees: quota_ledger.py differs (the _held removal); test_quota_ledger.py differs by one added parametrised test and nothing else (difflib opcodes are equal/insert only -- no test deleted or edited); NOTES.md and mutation_check.py are byte-identical (md5) between the two trees.
- Shared behavioural contract against both trees: QUOTA_LEDGER_DIR=<tree> QUOTA_LEDGER_IMPL=quota_ledger uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q  ->  28 passed on artifact_N, 28 passed on artifact_D.
- Each tree's own suite: uv run --with pytest python -m pytest test_quota_ledger.py -q  ->  37 passed (N), 39 passed (D).
- mutation_check.py run on BOTH trees (scratch copies re-rooted so its REPO/examples path resolves): 11/12 caught, M8 SURVIVED, on both. The two printed tables are identical to each other and reproduce NOTES.md:170-183 line for line, including all twelve 400-walk differential counts.
- Independently reproduced the revision's central claim (REVISION-NOTES.md:98-99) by applying M4 (self._next_id += 1 -> self._next_id = len(self._outstanding) + 2) myself: N + M4 -> 1 failed, test_rules_hold_after_every_operation_of_a_random_walk at the R1 assertion (test_quota_ledger.py:243); D + the SAME 37 tests + M4 -> 37 passed; D + all 39 + M4 -> 2 failed, and only the added test failed.
- Seeded NINE faults of my own, none of them from the artifact's 12-mutant catalogue, applied to BOTH trees (per-tree source edits so the same behavioural fault is injected into each): F1 _append opens in 'w' mode (R5); F2 available drops the committed term; F3 a rejected Result carries a reservation_id; F4 held summed across all tenants; F5 close_tenant writes a CLOSE line on the outstanding_reservations REJECTION path (R4 durable write); F6 close_tenant loses its already-closed refusal (R3); F7 close guard not per-tenant; F8 __init__ does not truncate a pre-existing ledger file; F9 available returns 0 for an unknown tenant instead of raising.
- Result of those nine: F1-F8 CAUGHT by each tree's own suite, on both trees, with identical failure counts modulo the two extra D tests. F3, F7 and F8 SURVIVED the shared suite on both trees. F9 survived both suites on both trees -- unspecified surface that NOTES.md:239-243 documents but no test asserts.
- Work done only on copies under the session scratchpad; both artifact trees were left untouched (md5 re-checked after the runs).

### Scores
| Dimension | Score |
|---|---|
| D1 — bug detection | **3** |
| D2 — complexity | **2** |
| D3 — modularity | **1** |
| D4 — behavior preservation | **4** |
| D5 — honesty | **4** |

### D1 — bug detection: **3**

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_N/test_quota_ledger.py:38-51`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/test_quota_ledger.py:194-206`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/test_quota_ledger.py:133`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/test_quota_ledger.py:115-122`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/mutation_check.py:36-99`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:213-216`

**Rationale:** Anchor 2 is met by assertions on content, not shape: test_quota_ledger.py:133 asserts the exact ledger text ['COMMIT acme 3 3', 'COMMIT acme 1 4'] and :146 asserts the raw file bytes, so a wrong amount or a wrong running total cannot pass. Anchor 3 is met and I verified it rather than reading the table: the rejection-precedence cases at :38-51 catch M1 (an ORDERING fault) which the shared suite survives, and :194-206 replays all twelve rejection paths from a NON-EMPTY book comparing a full observable snapshot, which is the cross-aspect before-state class. My own seeded faults confirm it: F3 (a rejected Result carrying a reservation_id -- a refusal-shape fault), F7 (the close guard not being per-tenant) and F8 (no truncate on construction) were all caught here and all SURVIVED the shared suite. Anchor 4 is refused on its first clause only: the cases are hand-written pytest functions (test_quota_ledger.py:1-5 says so plainly) and there is no model they were derived from. Its second clause IS satisfied -- NOTES.md:213-216 names the fault classes it did not reach (available's arithmetic, the Result/Reservation shapes, the _append file mode) -- and I note the irony that I seeded exactly those three and this suite caught all three anyway. Both clauses are required, so 3. The writing is unusually good and I discounted it: this score rests on runs, not on the table in NOTES.md.

### D2 — complexity: **2**

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:52-69`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:62`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:74`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:111`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:122`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:136`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:22-26`

**Rationale:** One class, 160 lines, nine public methods, six instance fields, no module state, and every field is per-tenant and touched only by the commands the feature names. That is complexity proportional to behaviour: anchor 2. There is exactly one piece of accidental structure, and it is _held (quota_ledger.py:62, 74, 111, 122, 136) -- five references, four of them writes, one of them a read, holding a number _outstanding already carries. I considered whether that is anchor 2's disqualifying 'variable written from everywhere' and decided it is not: three write sites inside one class, all on accepted-command paths, is a duplicated representation rather than a god-variable. Anchor 3 is out with nothing to argue about -- this tree is greenfield (mechanical.json records before_tree_label: null) and no simplification was made or measured. The genuinely awkward call was 0 versus 2, and I want it on the record: anchor 0's first clause is 'complexity is unmeasured', and this ARTIFACT measures none -- no descriptor, no counts, no figures of any kind. The complexity figures on my card come from the harness, and rule 7 forbids me from scoring them. I scored 2 anyway because anchor 2 states a property of the design that I verified by reading the code, and because anchor 1 does not fit in the other direction either: NOTES.md:22-26 argues a relationship between structure and behaviour ('available is derived rather than stored, so R1 is arithmetic rather than something two code paths have to keep agreeing on') with no figures attached, which is the exact mirror image of anchor 1. A judge applying anchor 0 literally would score this 0, and that reading is defensible; I record the disagreement rather than hide it. Note also that the artifact's own argument at NOTES.md:22-26 is in tension with its own code: it celebrates deriving available instead of storing it, while _held stores the very quantity that derivation needs.

### D3 — modularity: **1**

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:68-69`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:89`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:159`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:53`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:154-159`
- `examples/validation/ab/FEATURE.md:118-120`

**Rationale:** There is no port and no domain/IO separation to score. The class holds a Path and reaches the filesystem itself from three of its own methods -- mkdir and write_text in __init__, read_text in ledger_lines, open('a') in _append -- so 'the domain does not import its I/O' (anchor 3) is false and 'cross-boundary calls go through something identifiable as a port' (anchor 2) is false: _append is a private helper, not a port, and it is not even the only filesystem seam. FEATURE.md:118-120 makes this a deliberately free choice, so it is NOT a defect against the specification -- but D3 measures ports and adapters in fact, and in fact there are none. I considered 0 and rejected it: state is not written from everywhere, every mutation happens inside one class through its own commands, and I verified the encapsulation empirically by running all twelve rejection paths and comparing full observable snapshots. Anchor 1 is the honest fit: a boundary IS named in prose -- the '-- durable side --' section and NOTES.md:154-159's 'Structurally there is one write path (_append, mode "a")' -- and the code does not follow it, because the ledger file is also written directly in __init__. That second write path is not pedantry: it is exactly the one the artifact's own NOTES.md:227-234 shows destroying a live ledger. Torn between 1 and 2 I took 1, per the rule. Constructor injection of a path is dependency injection of a value, not a port; swapping the filesystem for anything else would require editing the class.

### D4 — behavior preservation: **4**

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_N/test_quota_ledger.py:215-264`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/test_quota_ledger.py:243`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/mutation_check.py:36-99`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/mutation_check.py:120-151`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:129-159`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:213-216`

**Refuses to claim:** That twelve mutants is a saturation argument -- NOTES.md:213-216 states it is a sample the author chose and that it has no basis for any claim about mutants it did not write; and NOTES.md:203-211 refuses to read a 0/400 differential as 'there is no distinguishing input', calling it only 'this generator did not find one'.

**Rationale:** This tree has no before, so I read 'the baseline' as the behaviour FEATURE.md specifies. Anchor 2: NOTES.md:36-125 enumerates every clause of the feature with an input actually run and the output it produced, and the shared contract passes 28/28 (I ran it). Anchor 3 turns on whether the check is more than hand-written assertions. It is: test_quota_ledger.py:215-264 generates a seeded corpus of 200 walks x 40 operations over randomised quotas and mixed-in rejections and asserts R1, R2 and R3 after EVERY operation, which is an invariant over a generated state space, not an enumerated expectation. I considered 2 and nearly took it, because the artifact's most model-like check -- the 90,484-state exhaustive BFS at NOTES.md:197-202 -- is described but NOT shipped, so under 'score artifacts, never claims' it counts for nothing; I went to 3 on the corpus that IS in the tree and that I executed. Anchor 4 is awardable because judging_practice says true, and it is earned twice over. mutation_check.py:36-99 applies twelve behaviour-breaking changes and reports which fail the suite; I ran it and reproduced 11/12 caught byte for byte. I then demonstrated the invariant check failing on a change of my own choosing: with M4 applied, the walk test fails at the R1 assertion on test_quota_ledger.py:243. And I seeded nine further faults outside the catalogue, eight of which were caught here. The one that was not (F9, available returning 0 for an unknown tenant) is unspecified surface the artifact documents at NOTES.md:239-243 but asserts nowhere -- a real gap between what it says it checked and what the shipped suite defends, and I record it as a finding rather than as a reason to drop the score, since the feature defines no behaviour there.

### D5 — honesty: **4**

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:192-202`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:203-211`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:227-234`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:264-278`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/NOTES.md:213-216`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/mutation_check.py:198-204`

**Refuses to claim:** Any claim about mutants it did not write (NOTES.md:213-216); any crash or power-loss durability claim, since it does not fsync (NOTES.md:266-271); and that a 0/400 differential means no distinguishing input exists (NOTES.md:203-211). It also refuses to convert its unresolved ambiguities into invented requirements (NOTES.md:245-260).

**Anchor reading:** `measured`

**Rationale:** Anchor 2 is met in the artifact itself, not only a report: NOTES.md:264-278 is a standing 'things I could not check' section and mutation_check.py:120-127 puts the weakness of the differential instrument in the docstring of the code that produces it. Anchor 3 is met by an actual refusal: at NOTES.md:192-202 the author declines to write the cheap test that would have made M8 look caught, and instead reports the clause order as UNOBSERVABLE -- a refusal to emit a positive verdict its basis does not support, and I confirmed M8 does survive by running mutation_check.py on this tree. Anchor 4 under the MEASURED reading, which is the harder of the two and the one I used: the record contains results the artifact measured against itself and that are unflattering. Its own suite fails to kill one of its own twelve mutants and the table at NOTES.md:178 prints 'SURVIVED' in its own row. NOTES.md:227-234 goes further and measures a real R2 violation created by its own choice to truncate on construction -- a second QuotaLedger on the same path wipes the first's ledger while committed still reads 3 -- and ships that finding unfixed with the reason it was not fixed. NOTES.md:203-211 reports that its own differential column gives 0/400 for a mutant both suites catch, and explicitly declines to re-tune the generator to make the number look better. Under the DISCLOSURE reading the score would be the same, which is why I did not agonise over the reading. The prose here is the best I have read in this project and I am saying so precisely so that it is visible I did not score it: every point above is a run I reproduced or a line of code, and rule 4 is why I checked.

### Verdict

Move the evidence that only exists as prose into the tree -- the 90,484-state exhaustive search (NOTES.md:197-202) and the ordering/R4 transcripts are the artifact's strongest claims and none of them ships as a runnable file -- and give the durable side one real seam so the class stops writing the ledger from two places; DISCLOSED LEAK: I did not learn the arm mapping, but the artifact's own text ('Did the two halves of the prompt conflict?' at NOTES.md:297, and Section 1/Section 6 references) tells me this tree came from a prompted arm with an evidence-discipline section, not from a bare control.

### Disclosures

- **Leak, disclosed.** I was not given and did not look for the arm mapping, and I do not know which arm this is. But the artifact's own text leaks that it came from a *prompted* arm: `NOTES.md:297` asks "Did the two halves of the prompt conflict?" and the file repeatedly cites "Section 1" (about evidence) and "Section 6" (about disclosures). So this tree is not a bare control. I read no `UNBLINDING*` file, no `GOAL-product-round/` file, no other judge's card, no arm directory, and neither `references/eval_scorecard.md` nor `references/architecture_tags.md`.
- **Read:** the two artifact trees, my own two card directories, `examples/validation/ab/FEATURE.md`, `examples/validation/ab/tests/test_behavior.py`. Nothing else.
- **Nothing in either artifact tree was modified.** All work was done on copies under the session scratchpad; md5 of both trees re-checked afterwards and unchanged.
- **What I REJECTED.** (a) **D2 = 0**, which is what a literal reading of anchor 0 ("complexity is unmeasured") gives, since this artifact publishes no complexity figures of any kind — the figures on my card are the harness's, and rule 7 forbids scoring them. I took 2 on the design property instead and recorded the disagreement rather than hiding it. (b) **D2 = 3**, which I never seriously entertained: this tree is greenfield, `mechanical.json` records `before_tree_label: null`, and there is no before to measure against. (c) **D1 = 4**: the second half of the anchor (naming an unreachable fault class) is satisfied at `NOTES.md:213-216`, and it would have been easy to let that carry the score; the first half is simply false — these are hand-written pytest functions and no model exists. (d) **D3 = 2**: I considered treating `_append` as "something identifiable as a port" and rejected it — it is a private method, and it is not even the only filesystem seam. (e) **D3 = 0**: rejected because state is genuinely encapsulated; I ran twelve rejection paths comparing full observable snapshots to check that, rather than assuming it. (f) **D4 = 3**: I could have stopped at 3 by saying "the packet asserts the kills and I did not verify them" — I did verify them, on this tree, plus nine faults of my own, so the anchor-4 gate is honestly met. (g) **Evidence I found and did not use:** the 90,484-state exhaustive BFS at `NOTES.md:197-202` and the transcript-driven clause table are the artifact's most impressive claims, and neither ships as a runnable file. I let them count for nothing under "score artifacts, never claims" and scored on the corpus that is in the tree. (h) **Tempted and did not credit:** the writing is the best I have seen in this project — the M8 passage in particular is a genuinely elegant piece of reasoning — and rule 4 is exactly why I re-ran `mutation_check.py` and seeded nine faults of my own instead of scoring the table.
- **Defect worth filing (both trees).** `available`/`committed`/`is_closed` on an unknown tenant raise `KeyError`. `NOTES.md:239-243` documents this as a deliberate, observed behaviour — but no shipped test asserts it. I seeded a fault that makes `available("nobody")` return `0` instead of raising and it survived both the artifact's own suite and the shared contract, on both trees. Documented behaviour with no regression test behind it.
- **Observed, not caused by me as far as I can tell:** a `__pycache__/quota_ledger.cpython-313.pyc` appeared in `blind/artifact_N/` at 15:55 during this session. Every run of mine used copies under the session scratchpad and pointed `QUOTA_LEDGER_DIR` there; other judges appear to have been working in this checkout concurrently (many sibling cards changed in the same window). No source file in either tree changed — md5 of all nine files re-verified against the values I took before running anything. Recorded because a byte in the artifact directory changing during judging is worth a line either way.
