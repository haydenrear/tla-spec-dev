# Scorecard — ab_quota_ledger, artifact `U`, judge pass 1

`run_id`: `20260806-v2-U-p1` · scorecard_version 2 · rubric `references/eval_scorecard.md` digest `sha256:19c6712ed509a228`

**You are scoring artifact `U`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

Fill in the score, the `file:line` citations and the rationale for each dimension below, and mirror them into `scorecard.json` beside this file. **The anchors are reproduced here so the bar for a score sits in the same file as the score.**

## The rules, in the file where the score is written

1. **Score artifacts, never claims.** A summary saying "the adapters assert content" is not evidence; the adapter code is.
2. **Every score ≥ 2 cites `file:line`.** A score with no citation is capped at 1, mechanically, by the schema check.
3. **Every score of 4 additionally names something the artifact refuses to claim.** The top of every scale requires a stated limit. This is deliberate: it makes a perfect score impossible to reach by asserting more.
4. **Prose quality is never an input.** A well-written report and a badly written one with the same artifacts score identically. Say so in the rationale if the writing tempted you.
5. **Two judges, independently, blind to each other.** Any dimension where they differ by more than 1 is recorded as `contested` and adjudicated by a third pass that must cite new evidence, not re-read the same lines.
6. **Blind to arm.** Where an eval has arms (with-prompt vs without), judges do not learn which artifact came from which until after scoring.
7. **The mechanical block is recorded, never scored.** Kill counts, complexity figures, case counts, determinism, runtime. It sits beside the judgement so a reader can see when the two disagree — and a disagreement is a finding.
8. **Say what you ran.** *(New in version 2.)* Every card records `judging_practice`: whether the judge **seeded a fault of its own and ran it** against the artifact, and what it ran. Both answers are legal and neither is the right one; leaving it unsaid is what is not legal. **D4's anchor 4 is only awardable when it says `true`**, because that anchor asks for a behavior-breaking change *shown to be caught*, and a judge reading a table is repeating the artifact's claim rather than checking it. This is the anchor's own text made checkable, not a new bar. See [R-H5](#r-h5--a-movement-is-a-measurement-only-if-the-judging-practice-is-recorded-at-both-ends) for what it is for.

**Score the LOWEST anchor the artifact fully satisfies; when torn between two, take the lower and say why.**

## Judging practice — REQUIRED, and it is a field on the card

**Did you seed a fault of your own and run it against this artifact, or did you score the evidence packet?** Both are legal. Neither is the right answer. What is not legal is leaving it unsaid.

Fill `judging_practice` in `scorecard.json`: `executed_own_faults` true or false, and `what_was_run` listing what you actually ran.

> This field exists because two judges re-scored **byte-identical trees** and four dimension-points moved. Both had privately chosen to seed and run their own faults; the round before them had not; and nothing on either card said so. **The card was measuring the judge and reporting it as the artifact.**

**D4's anchor 4 is only awardable when this says `true`.** That anchor asks for a behavior-breaking change *shown to be caught*. If you did not run one, the highest D4 you can support is 3 — say that the packet asserts it and you did not verify it. **D1, D4 and D5 all moved on unchanged input; only D4's anchor is gated, because only D4's anchor asks you to run something.**

**Executed own faults:** **true**

**What was run:**

- Copied all three blind artifact directories and examples/validation/ab/tests/test_behavior.py to a scratch tree OUTSIDE the repository. Nothing in the repository was modified or executed in place.
- Seeded FOUR faults of my own, one at a time, into each artifact's implementation module, asserting a unique anchor and that reverting was byte-identical: FJ1 (content) the COMMIT line transposes <amount> and <running total>; FJ2 (refusal ordering) reserve checks amount_not_positive BEFORE tenant_closed, contradicting FEATURE.md's numbered order; FJ3 (inertness on hidden state) a quota_exceeded rejection increments the reservation-id counter; FJ4 (output oracle) an ACCEPTED commit Result carries reason='unknown_reservation'.
- Ran the unedited shared suite AND the artifact's own tests against each of the 12 mutants plus 3 baselines. Baselines: T 28 shared / 53 own, U 28 / 32, W 28 / 11, all green.
- Own-suite results. T: FJ1 KILLED, FJ2 SURVIVED, FJ3 KILLED, FJ4 SURVIVED. U: FJ1 KILLED, FJ2 KILLED, FJ3 KILLED, FJ4 KILLED. W: FJ1 SURVIVED, FJ2 KILLED, FJ3 KILLED, FJ4 SURVIVED. Shared suite, identical for all three: FJ1 KILLED, FJ2/FJ3/FJ4 SURVIVED.
- Executed T's declared adapter swap: changed the single line quota_ledger/__init__.py:39 to Ledger(quotas, InMemoryJournal()), confirmed domain.py and tests/test_ledger.py byte-identical to the originals, ran the shared suite: 28 passed.
- Re-ran U's randomized model sweep (test_quota_ledger.py:315) on its own seed 20260804 and counted outcomes: 1 accepted reserve, 1 accepted commit, 0 accepted releases, 3 accepted closes in 400 commands; final ledger ['COMMIT acme 7 7', 'CLOSE initech 0', 'CLOSE globex 0', 'CLOSE acme 7'].
- I did NOT re-run any model-derived corpus. Every corpus figure I cite is read from the artifact's EVIDENCE.md, not measured by me.

## The mechanical block is recorded, never scored

`mechanical.json` beside this file holds kill counts, complexity figures, case counts, determinism and runtime. It sits beside the judgement so a reader can see when the two disagree — **and a disagreement is a finding, not a rounding error.**

## D1 — bug detection

*Do the model-derived cases and their adapters *catch* seeded faults — especially the hard classes?*

- **0** — Cases exist and pass; no seeded fault is caught. A suite that is green on broken code.
- **1** — Catches faults that change a value the projection already prints. Misses everything requiring a content assertion.
- **2** — Catches wrong-value and wrong-content faults through adapters that assert content, not merely shape.
- **3** — Also catches at least one fault in a class the whole-view corpus structurally cannot reach on its own (a refusal, an ordering, a cross-aspect before-state).
- **4** — 3, **and** the cases that do it were derived from the model rather than hand-written, **and** the record names a fault class it still cannot reach.

**Score:** 3

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:85`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:182`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:255`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:315`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:111`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:263`

**Refuses to claim** (required and non-null for a score of 4): _n/a — this score is not a 4._

**Rationale:** The best measured result of the three, and it still stops at 3. I seeded four faults and U's suite caught all four, each naming the broken behavior: the transposed COMMIT line by test_commit_lines_reach_the_file_itself (:85-88, which asserts the file's bytes rather than the accessor's return), the swapped rejection order by test_reserve_rejection_order_is_the_declared_one (:255-262), the id-burning rejection by test_a_rejected_reserve_does_not_consume_an_id, and the accepted result carrying a rejection reason by test_accepted_results_carry_no_reason (:182-186). Anchors 2 and 3 are comfortably met, the latter also by corpus-neg taking the refusal class 3 of 3 where corpus-whole takes 0 of 3 (EVIDENCE.md:111-120). Not 4, for the reason the anchor names: it pays for cases 'derived from the model rather than hand-written', and all four kills came from small hand-written cases. U's own model-derived check -- the 400-command sweep at :315-362 recomputing R1/R2/R3 against an independent model at :279-312 -- caught none of the four. I re-ran it on its own seed 20260804 and counted 1 accepting reserve, 1 accepting commit, 0 accepting releases and 3 accepting closes in 400 commands; the ledger it produces is ['COMMIT acme 7 7', 'CLOSE initech 0', 'CLOSE globex 0', 'CLOSE acme 7'], so amount and running total are the same number on the only COMMIT line it ever writes and the transposition is structurally invisible to it. Independently, the packet's model-derived columns have no demonstrated reach on any artifact this round: M07 is red with deciding: [] and corpus-port SURVIVED it across 294 accepting Reserve cases.

## D2 — complexity

*Is the design as simple as its behavior requires, and no simpler?*

Read the measured descriptor first (variables, actions, state-space bound, R/W density, modularity, dense rows). Then judge whether the numbers reflect essential behavior or accidental structure.

- **0** — Complexity is unmeasured, or measured and ignored.
- **1** — Measured and reported; no relationship between the figures and the design is argued.
- **2** — The design's complexity is proportional to its behavior; no god-state, no variable written from everywhere.
- **3** — 2, **and** a simplification was made and its effect measured — the before and after figures are both recorded.
- **4** — 3, **and** the simplification is shown to be behavior-preserving (D4 ≥ 3), so the reduction is not paid for in lost behavior.

> **A drop in a complexity number is not evidence on its own.** MF-020: a metric can improve because an edge was deleted. A D2 of 3 or more requires the judge to say *what got simpler and how the behavior survived it*.

**Score:** 2

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:58`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:127`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:150`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:170`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:341`

**Refuses to claim** (required and non-null for a score of 4): _n/a — this score is not a 4._

**Rationale:** Proportional to the behavior, no god-state, counted by writers: _committed assigned at :170, _closed at :194, _available at :150 and :180 -- the two commands whose whole meaning is taking and returning a hold -- and _reservations at :151, :171, :181. R4's 'a rejection reason is always one of the six' is turned into a machine check at :58 rather than left as a rule every call site must remember, which is structure buying a behavior rather than structure for its own sake. Two pieces of accidental structure, recorded and not enough to cost a point: _Reservation carries both reservation_id and seq and outstanding_ids sorts by seq at :127-130 although the dict is already in allocation order, and _quotas and _available begin as two copies of one mapping. Not 3: no simplification with before-and-after figures is recorded anywhere in the artifact. Mechanical block recorded, not scored; its branch_points_in_effectful_modules: 10 for U is a D3 fact and I use it there, not here.

## D3 — modularity

*Is it ports and adapters in fact — domain independent of I/O, adapters swappable?*

- **0** — No boundary is discernible; state is written from everywhere.
- **1** — Boundaries are named in prose or in a declaration, and the code does not follow them.
- **2** — The code follows the declared boundaries. Cross-boundary calls go through something identifiable as a port.
- **3** — The domain does not import its I/O. An adapter could be replaced without touching the domain, and the judge names the specific swap.
- **4** — 3, **and** a driven port is exercised by a real adapter *and* a fake, with the same cases passing against both.

> **Import topology is not modularity.** Round 2 proved a codebase can pass every import check with its coupling entirely intact. A D3 of 3 or more requires evidence about what *calls* what at runtime, not what imports what.

**Score:** 2

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:72`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:110`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:134`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:168`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:193`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:115`

**Refuses to claim** (required and non-null for a score of 4): _n/a — this score is not a 4._

**Rationale:** Anchor 2 exactly, and cleanly. There is an identifiable seam and the code follows it without a single exception: open, read_text and write_text appear nowhere in the module outside _LedgerFile (:72-92), and QuotaLedger reaches the durable side only through self._ledger.append(...) at :168 and :193 and self._ledger.lines() at :134. That is a cross-boundary call going through something identifiable as a port, at runtime, on every path. Not 3, because the domain owns its I/O. QuotaLedger.__init__ constructs _LedgerFile(ledger_path) itself at :110 from a path it was handed, pathlib.Path is imported at module scope (:10), and there is no seam to inject a different implementation through -- replacing the durable side means editing the constructor of the class that holds the rules. I could not name a swap that leaves the rules untouched, and naming the swap is what anchor 3 requires of me. This is a stated choice, not a broken declaration: NOTES.md:115-118 says an abstraction over the file beyond the one small writer class was deliberately not added, and FEATURE.md:113-122 makes that a free choice. Anchor 1 therefore does not fit; anchor 2 does, fully.

## D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

**Score:** 4

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:85`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:182`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:255`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:279`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:180`

**Refuses to claim** (required and non-null for a score of 4): U refuses to claim crash safety or recovery. NOTES.md:62-63 states that ordering the durable write before the in-memory update 'is not a crash-safety feature and I did not build one (no fsync, no journaling, no recovery; that is out of scope)'. It also refuses to claim integrality is enforced: NOTES.md:96-103 states that reserve(t, 1.5) 'would be held and committed as 1.5, and would print that way in a COMMIT line', and concludes 'If integrality is meant to be enforced, the six-reason vocabulary is missing a reason for it' rather than adding a seventh reason it was not given. It further declines to invent a return value for available() on an unknown tenant (NOTES.md:89-94).

**Rationale:** Anchor 2: behaviors enumerated per named case across construction, durability, id allocation, accepted-result shape and every rejection path, 32 passing, re-run rather than read. Anchor 3: model-derived checks on both sides -- the packet's corpora ran against U with 0 failures on 3,734 executed unmutated whole-view cases (EVIDENCE.md:180), and U itself ships an independent-model recomputation of R1, R2 and R3 against the file on disk after every command (:279-312). Anchor 4, and this is the one I ran rather than read: I made four deliberate behavior-breaking changes and U's checks caught all four, each failing a case that names the broken behavior. The check is demonstrated capable of failing. The disagreement I am required to record rather than split: the half of U's checking that caught them is the hand-written half. Its model-derived half -- the sweep whose docstring at :11-12 advertises 'R1/R2/R3 under a long randomized command sequence checked against an independent model' -- caught nothing, because on its own seed it executes five accepting commands in four hundred. I award the anchor on what actually failed under a deliberate break, and flag that the sweep's own guard against exactly this degeneracy (:358-362, 'a sequence that only ever rejected would prove nothing') is satisfied by a single accepted commit and so cannot detect it.

## D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

**Score:** 3

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:58`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:62`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:89`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:96`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:358`

**Refuses to claim** (required and non-null for a score of 4): _n/a — this score is not a 4._

**Rationale:** Anchor 2 and anchor 3 both hold. Blind spots are named unprompted and a positive verdict is refused where the basis is missing: U declines to invent unknown-tenant query semantics (NOTES.md:89-94), declines an integrality check and names the resulting hole in the six-reason vocabulary instead of papering over it (NOTES.md:96-103), and declines to call its write ordering crash safety (NOTES.md:62-63). In the artifact itself, quota_ledger.py:58 makes R4's vocabulary rule an executable assertion rather than a claim. Not 4: nothing in U's record is unflattering to U. Both reported results are green (28 passed, 32 passed), and the single place its record leans past its evidence leans the flattering way -- the comment at test_quota_ledger.py:358-359 says the sweep 'should have exercised both outcomes of every command, not just rejections', and I measured that run to contain one accepted commit and zero accepted releases. I considered 2 for that and rejected it: an over-claim about coverage in a comment is not a false clean about behavior, and every statement U makes about what its code does is true. Between 3 and 4 rule 5 sends me down, so 3.

## Verdict

The strongest checks of the three against faults I seeded myself -- 4 of 4 caught, each by a distinct named case -- but every one of those kills is hand-written and the randomized model sweep it advertises executes one accepting commit in four hundred commands, so read what its cases assert and not what its docstrings claim.

## Disclosures

**Anything I saw that I was not meant to see.**

- Nothing on the must-not-read list was opened. I read `references/eval_scorecard.md`, `examples/validation/ab/FEATURE.md`, `examples/validation/ab/tests/test_behavior.py`, the three `blind/artifact_*/` directories, and my own three card directories.
- Two directory listings showed me file *names* I did not open. `ls` on the repository root showed the `*EPIC*.md` filenames; `ls` on `.../falsifiable-instruments-rescore-v2/ab_quota_ledger/` showed that three `-p2` card directories exist beside mine. I opened neither, and I know nothing of the other judge's scores.
- **One accidental read, disclosed in full.** The scratchpad path I chose for my card-filling script was already occupied by a leftover script from an earlier judging session. I read its first 15 lines before realising, and stopped there. What I saw was a docstring, imports, and two constants: it targets `specs/results/scorecards/falsifiable-instruments-rescore-v1/ab_quota_ledger`, a different epic directory from mine, with the same commit sha and the same model id. I saw no scores, no rationale, no artifact labels and nothing about my three cards. I did not open it again and I wrote my own script to a different filename.
- **A partial arm leak, disclosed rather than suppressed.** `artifact_T/NOTES.md:102-116` and `artifact_W/NOTES.md:201-216` both quote a numbered prompt section ("Section 1", "Section 6") that `artifact_U/NOTES.md` never mentions, and T's NOTES describes resolving a conflict between the feature and an explicit "architecture ask" / "structure ask". So I formed a belief that T and W were given a structured prompt that U's record shows no trace of. I did not go looking for this, I do not know the label-to-arm mapping, and I did not use it: the D3 spread (T 4, U 2, W 1) cuts straight across the pair I would have grouped together, which is the check I applied to myself.

**Anything I ran, and whether it changed anything on disk.**

- Everything listed under Judging practice, in a scratch tree outside the repository. Twelve mutants across three artifacts, thirty pytest invocations, one adapter swap, one instrumented replay of U's sweep.
- **Inside the repository I wrote only my own three card directories** (`scorecard.json`, `scorecard.md`, and `mechanical.json`, into which I recorded the fault matrix I measured because the field asks for measurements). I ran no git command that changes state and I committed nothing.

**What I REJECTED.**

- **Rejected D1 = 4 on all three artifacts, including U, which caught 4 of 4 of my faults.** Anchor 4 pays for cases "derived from the model rather than hand-written". Every kill that distinguishes these three artifacts came from a small hand-written case; the model-derived columns are byte-identical across all three (`cases.py` sha1 recorded at `EVIDENCE.md:190`) and their only positive control, M07, is RED with `deciding: []` — `corpus-port` SURVIVED the wrong-hold control while executing 294 accepting `Reserve` cases, measured, on all three artifacts. I was two sentences from giving U a 4 on the strength of 4-of-4.
- **Rejected D4 = 4 for T and for W.** I had executed my own faults, so the gate was open. Two of my four breaks walked past each of their suites, and in both cases the survivor is behavior FEATURE.md states outright.
- **Rejected D5 = 2 for U.** `test_quota_ledger.py:358-359` says the sweep "should have exercised both outcomes of every command, not just rejections; a sequence that only ever rejected would prove nothing", and I measured that sweep to contain one accepted commit and zero accepted releases in 400 commands. I decided that is an over-claim about coverage in a comment, not a false clean about behavior, and that everything U states about its behavior is true. It stayed at 3.
- **Rejected D3 = 2 for W**, having first written it. The deciding fact was that I could not point at one thing and call it the port: two of W's three cross-boundary calls bypass its only seam, and one of those two is a public query.
- **Rejected the mechanical block as a D2 signal.** T is 202 code lines to W's 78 and the temptation to read that as a complexity gap is strong. Rule 7 forbids converting the figure into a score and MF-020 says the smaller number can be smaller because something was deleted. I scored D2 from the writer counts in the code instead, and all three came out at 2.
- **Rejected the `corpus-port-swap:fake` KILLED cells for U and W as evidence of a fake.** `EVIDENCE.md:49-51` says that on an artifact shipping no second implementation, that column runs the REAL one. Those cells describe the real adapter twice and say nothing about swappability. T's is the only one of the three where that column measures a second implementation — and it is also the only one that disagrees with `:real` (M09, `EVIDENCE.md:168`).
- **Rejected reading T's two `seeded_by: addition` rows (M08, M10) as a point for or against T.** The packet says it is a fact about the diff. It is tempting to read "the fault has no one-token form in this design" as evidence of robustness; I counted it neither way.
- **Rejected the conclusion that the near-identical kill tables mean the three artifacts are near-identical on bug detection.** They are near-identical because the corpora are byte-identical and the positive control is red, which is a fact about the instrument. The four faults I seeded myself separated the three artifacts 2 / 4 / 2 in the same afternoon.
- **Rejected prose quality, explicitly and in both directions.** T's NOTES is the most persuasive document of the three and tempted me toward a 4 on D5 and a 3 on D2; W's is the least polished and its extra suite is the smallest at 11 cases, and it took the only D5 of 4. Neither was an input.
