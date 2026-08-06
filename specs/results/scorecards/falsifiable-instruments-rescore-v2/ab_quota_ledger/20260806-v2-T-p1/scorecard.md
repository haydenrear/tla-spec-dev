# Scorecard — ab_quota_ledger, artifact `T`, judge pass 1

`run_id`: `20260806-v2-T-p1` · scorecard_version 2 · rubric `references/eval_scorecard.md` digest `sha256:19c6712ed509a228`

**You are scoring artifact `T`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:124`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:175`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:202`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:111`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:263`

**Refuses to claim** (required and non-null for a score of 4): _n/a — this score is not a 4._

**Rationale:** Anchor 2 is content, not shape, and I checked it by breaking it: tests/test_ledger.py:124-129 asserts the exact four-line interleaved transcript, and when I transposed <amount> and <running total> on the COMMIT line, T's own suite failed four cases -- two cases across two wirings. Anchor 3 holds: the refusal class is taken 3 of 3 by corpus-neg and corpus-port where corpus-whole takes 0 of 3 (EVIDENCE.md:111-120), and T's own suite carries a nine-case refusal table comparing full before/after state including the durable side (tests/test_ledger.py:161-199) and a concrete ordering transcript (:202-220). Not 4, on two grounds, and rule 5 says take the lower. First, the anchor pays for reach that is model-derived, and this run has not demonstrated any: the only positive control M07 is red with deciding: [], and corpus-port SURVIVED it while executing 294 accepting Reserve cases. Second, my own refusal-ordering fault -- amount_not_positive checked before tenant_closed, contradicting the numbered order at FEATURE.md:40-45 -- survived T's 53 cases and the shared suite both, so the refusal class T reaches is narrower than its record reads. T does satisfy anchor 4's third clause (NOTES.md:136-141 names R2-under-a-failed-durable-write as a class it cannot reach); the first two clauses are what fail.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:120`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:146`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:158`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:180`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:341`

**Refuses to claim** (required and non-null for a score of 4): _n/a — this score is not a 4._

**Rationale:** No god-state and no variable written from everywhere, checked by counting writers rather than by reading the claim: _committed is assigned at exactly one line (domain.py:158), _closed at one (:180), _issued at one (:146), and available is not stored at all -- it is quota - held - committed, computed at :120, so conservation has no writer that could fall out of step. Mechanical block, recorded and not scored: T is the largest of the three at 4 modules and 202 code lines against 151 and 78, and is simultaneously the only one whose effectful module carries 1 branch point and 1 piece of instance state rather than 10 and 8 or 7 (EVIDENCE.md:341-342). Where the block and I could disagree, the disagreement is that a line count reads T as the most complex and a writer count reads it as the most separated; I scored the writer count, because that is what the anchor names. Not 3: anchor 3 wants a simplification whose before and after figures are both recorded, and T argues its derivation of available in prose with no before figure anywhere. A described simplification is not a measured one. Rule 4: T's NOTES is the most persuasive of the three documents and it pushed me toward 3 here. It was not an input.

## D3 — modularity

*Is it ports and adapters in fact — domain independent of I/O, adapters swappable?*

- **0** — No boundary is discernible; state is written from everywhere.
- **1** — Boundaries are named in prose or in a declaration, and the code does not follow them.
- **2** — The code follows the declared boundaries. Cross-boundary calls go through something identifiable as a port.
- **3** — The domain does not import its I/O. An adapter could be replaced without touching the domain, and the judge names the specific swap.
- **4** — 3, **and** a driven port is exercised by a real adapter *and* a fake, with the same cases passing against both.

> **Import topology is not modularity.** Round 2 proved a codebase can pass every import check with its coupling entirely intact. A D3 of 3 or more requires evidence about what *calls* what at runtime, not what imports what.

**Score:** 4

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:22`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:132`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:159`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/__init__.py:39`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/memory_journal.py:14`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:26`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:168`

**Refuses to claim** (required and non-null for a score of 4): T refuses to claim R2 survives a failed durable write. NOTES.md:136-141 states that commit and close_tenant update memory and then append, that a raising append would leave memory ahead of the ledger, and -- verbatim -- 'This is the one place I can name where R2 is not enforced by construction'. It correspondingly declines to give the Journal port any failure, atomicity or rollback semantics rather than inventing them, and declines to invent a reopen-and-resume path for an existing ledger file.

**Rationale:** Runtime, not import topology, which is what the caveat demands. The Journal port is declared inside the domain in the domain's own vocabulary (domain.py:22-43), and the domain's only three cross-boundary calls all go through the injected object: self._journal.records() at :132, self._journal.append(...) at :159 and :181. The named swap, executed by me rather than read: I changed the single line quota_ledger/__init__.py:39 from FileJournal(ledger_path) to InMemoryJournal(), verified domain.py and tests/test_ledger.py were byte-identical to the originals, and ran the unedited shared behavioral suite -- 28 passed against the fake. That is an adapter replaced with the domain untouched. Anchor 4 additionally: tests/test_ledger.py:26-36 parametrizes every behavioral case over both implementations from one case list, 53 pass on both, and under my transposed-COMMIT-line fault exactly the same two cases failed on each wiring (4 failures = 2 cases x 2 wirings) -- evidence both are really being driven rather than one being short-circuited. memory_journal.py:14-22 is a working implementation of the contract, not a mock. Recorded disagreement with the packet: EVIDENCE.md:168 shows corpus-port-swap:fake SURVIVED M09 where :real KILLED it, so the two implementations are not equivalent under every fault. The anchor asks for the same cases passing against both, which holds on unmutated code; the divergence under mutation is a real limit on how far the fake substitutes for the file, and I record it rather than average it away.

## D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

**Score:** 3

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:108`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:202`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:62`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:180`

**Refuses to claim** (required and non-null for a score of 4): _n/a — this score is not a 4._

**Rationale:** Anchor 2: the behaviors are enumerated one per named case and each is shown to hold, on both wirings -- 53 passed, which I re-ran rather than read. Anchor 3: the check is not only hand-written; the model-derived corpora were run against T with 0 failures on unmutated code across 3,734 executed whole-view cases and 1,543 port cases (EVIDENCE.md:178-187), beside the shared suite's 28 (:62). Not 4, and the gate was open -- I executed my own faults, so I could have awarded it. Two of my four deliberate behavior-breaking changes were caught by T's suite (the transposed COMMIT line, the id-burning rejection) and two were not: the swapped rejection order and an accepted commit result carrying reason='unknown_reservation'. Both survivors are behavior FEATURE.md states outright -- the numbered order at FEATURE.md:40-45, and 'a rejected result carries a reason; an accepted one carries the reservation_id' at FEATURE.md:34-36. A check that a deliberate break walks past is not demonstrated capable of failing on that behavior, which is exactly what anchor 4 asks. Torn between 3 and 4, took 3.

## D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

**Score:** 3

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:110`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:260`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:104`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:136`

**Refuses to claim** (required and non-null for a score of 4): _n/a — this score is not a 4._

**Rationale:** Anchor 2 is satisfied in the artifact and not only in a report: domain.py:110-111 flags in a code comment that outstanding_ids() leans on dict insertion order, and the reliance is then discharged by a case that runs past r10; tests/test_ledger.py:260-270 converts 'the domain imports no I/O' from a claim into an AST parse of the file, because -- as NOTES.md:49-51 puts it -- that is a claim about the file rather than about intent. Anchor 3 is satisfied: NOTES.md:136-141 declines to certify R2 under a failed durable write rather than reporting a clean, and NOTES.md:125-135 declines to invent unknown-tenant query semantics or a seventh rejection reason. NOTES.md:104-123 records the one place the feature and the structure ask conflicted and states the cost of the resolution instead of hiding it. Not 4: every result in T's record is a pass -- 28 and 53 -- and I can find no measured result in it that is unflattering to T. Its limitations are design reasoning, which anchor 3 already pays for; anchor 4 asks for a result. Rule 4 bites hardest here: this is the best-written record of the three and it tempted me to a 4. It was not an input.

## Verdict

A real port with two working implementations — I changed one line, left the domain byte-identical, and the shared suite passed 28/28 against the fake — wrapped around a 53-case suite that let the feature's declared rejection ORDER walk straight past it, so trust this artifact's boundary further than its coverage.

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
