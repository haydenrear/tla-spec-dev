# Scorecard — ab_quota_ledger, artifact `W`, judge pass 1

`run_id`: `20260806-v2-W-p1` · scorecard_version 2 · rubric `references/eval_scorecard.md` digest `sha256:19c6712ed509a228`

**You are scoring artifact `W`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:36`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:94`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:104`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:111`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:263`

**Refuses to claim** (required and non-null for a score of 4): _n/a — this score is not a 4._

**Rationale:** Anchor 2 is met, but by the instruments rather than by W's own cases: map-checking takes the durable-content class 2 of 2 and the shared suite 2 of 2 against W (EVIDENCE.md:104-110). Anchor 3 is met: corpus-neg takes the refusal class 3 of 3 where corpus-whole takes 0 of 3 (:111-120), and W's own test_extra.py:36-43 pins the tenant_closed / amount_not_positive tie -- which I confirmed is load-bearing by swapping those two checks, at which point that case is the one that fails. Not 4, on the shared ground and on a first-hand one. Shared: the only positive control M07 is red with deciding: [], corpus-port SURVIVED it across 294 accepting Reserve cases, so no model-derived reach is demonstrated this round. First-hand: I transposed <amount> and <running total> on the COMMIT line; the shared suite killed it and W's own suite did not, because W's only raw-bytes durability assertion (test_extra.py:85-95, the literal at :94) commits 5 as a tenant's first and only commit, making amount and running total the same number and the transposition invisible. W's own additional cases therefore add no content discrimination on the durable side, which is the thing they were written to add. W does satisfy anchor 4's third clause -- NOTES.md:179-188 and :190-210 both name classes it cannot reach -- but the first two clauses do not hold.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:31`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:58`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:90`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:113`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:327`

**Refuses to claim** (required and non-null for a score of 4): _n/a — this score is not a 4._

**Rationale:** The smallest of the three at 78 code lines and 11 callables, and nothing in it is doing work the behavior does not require. Writers counted: _committed at :90, _closed at :113, _available at :81 and :101, _outstanding at :82, :89, :100. No god-state; no variable written from everywhere; max_depth 1 and max_branch_points_in_callable 4, the same as both others. Two blemishes, recorded and not enough to drop a point: outstanding_ids at :58 derives ordering by parsing the numeric suffix back out of its own id strings, coupling the ordering rule to the id format rather than to allocation order; and the blank-line filter at :65 is code W itself reports as unreachable in normal operation (NOTES.md:179-188). Not 3: no before-and-after figures for any simplification are recorded. Mechanical block recorded and not scored -- and I note that being the smallest code_lines figure (EVIDENCE.md:327) earned W nothing here, because MF-020 says a smaller number can be smaller for the wrong reason and the anchor asks about proportionality, not size.

## D3 — modularity

*Is it ports and adapters in fact — domain independent of I/O, adapters swappable?*

- **0** — No boundary is discernible; state is written from everywhere.
- **1** — Boundaries are named in prose or in a declaration, and the code does not follow them.
- **2** — The code follows the declared boundaries. Cross-boundary calls go through something identifiable as a port.
- **3** — The domain does not import its I/O. An adapter could be replaced without touching the domain, and the judge names the specific swap.
- **4** — 3, **and** a driven port is exercised by a real adapter *and* a fake, with the same cases passing against both.

> **Import topology is not modularity.** Round 2 proved a codebase can pass every import check with its coupling entirely intact. A D3 of 3 or more requires evidence about what *calls* what at runtime, not what imports what.

**Score:** 1

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:42`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:64`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:119`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:336`

**Refuses to claim** (required and non-null for a score of 4): _n/a — this score is not a 4._

**Rationale:** This is the score I moved on most, and rule 5 decided it. Anchor 2 asks that cross-boundary calls go through something identifiable as a port. W has three cross-boundary calls and they go through three different places: the write through _append_line (:119-121), the read straight to self._ledger_path.read_text() inside the public ledger_lines() query (:64), and construction straight to write_text('') (:42). Two of the three bypass the only seam, and one of those two is a query the feature lists as observable state -- so the rules and the filesystem are interleaved rather than separated, and there is no one thing I can point at and call the port. Anchor 2 is therefore not fully satisfied. Anchor 0's wording ('state is written from everywhere') is too harsh -- W's in-memory state has clean single writers, as D2 records -- and anchor 1's wording ('named ... and the code does not follow them') does not literally fit either, because W declares no boundary in prose at all. Torn between 1 and 2, rule 5 says take the lower and say why: I took the lower on the seam, and the deciding fact is the read path at :64. Recorded fairly: FEATURE.md:113-122 makes 'whether the durable side is reached through an interface, a callable, or directly' a free choice and asks a judge not to read a difference there as a defect. W chose directly, legitimately. D3 then measures what that choice yields, which is a domain whose durable side cannot be replaced at all -- declared_interfaces: 0, and every one of the module's 10 branch points and 7 pieces of instance state sitting in the effectful module (EVIDENCE.md:336-342).

## D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

**Score:** 3

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:25`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:94`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:180`

**Refuses to claim** (required and non-null for a score of 4): _n/a — this score is not a 4._

**Rationale:** Anchor 2 is met more explicitly here than by either of the others: NOTES.md:25-153 walks every clause of FEATURE.md and names, per clause, the concrete input that would have caught it being absent, distinguishing what the shared suite covers from what its own file covers. Anchor 3: the packet's model-derived corpora ran against W with 0 failures on 3,734 executed unmutated whole-view cases (EVIDENCE.md:180). Not 4, and the gate was open -- I did execute my own faults. Two of my four deliberate breaks were caught by W's suite (the swapped rejection order, the id-burning rejection) and two were not. The miss that decides it is the transposed COMMIT line: it walked past W's only raw-bytes durability assertion because that assertion's amount equals its running total (test_extra.py:94). The shared suite caught it; W's own check, the one NOTES.md:130-136 offers as checking 'the actual durable artifact and not just the method that reports on it', did not. Anchor 4 is about the check being demonstrated capable of failing, and on the durable-content class W's is demonstrated incapable.

## D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

**Score:** 4

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:108`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:157`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:179`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:190`

**Refuses to claim** (required and non-null for a score of 4): W refuses to claim it verified close_tenant's rejection ORDER between unknown_tenant and outstanding_reservations: NOTES.md:190-210 states it could not construct an input where both apply and so declines to write the order up as checked -- 'I could not produce evidence for an ordering claim that has no distinguishing input' -- and test_extra.py:108-115 repeats the refusal in the test's own docstring. It also refuses to claim it observed the blank-line filter in ledger_lines() do anything: NOTES.md:179-188 states the filter is unreachable in normal operation and that 'I did not run a case that exercises this filter; I am not claiming to have observed it doing anything, only that it is there.' And it refuses to claim its reading of reservation_id on accepted commit/release results is verified: NOTES.md:157-167 marks it 'unverified by any assertion, only a reading I committed to.'

**Rationale:** Anchor 2 in the artifact itself and not only in a report: test_extra.py:108-115 carries a docstring telling the reader the case below it is 'trivially true since an unknown tenant can hold no reservations' -- a test file arguing against the strength of its own case, in a file whose job is to look strong. Anchor 3 is the unobservable-over-false-clean doctrine executed three separate times: an ordering claim with no distinguishing input is written up as unprovable rather than as checked (NOTES.md:190-210), a reading with no assertion behind it is labelled unverified rather than reported as covered (NOTES.md:157-167), and a filter that was never exercised is reported as never exercised (NOTES.md:179-188). Each had a cheaper flattering alternative available and none was taken. Anchor 4: the record contains results unflattering to W -- shipped code it states is unreachable in normal operation, and a design decision it states nothing in either suite tests. Those are facts about W that make W look worse and that no reader would have found without being told. Rule 4, in the direction it is usually not needed: W's record is the least polished of the three and its extra suite is the smallest at 11 cases. Neither counted. The score rests on three refusals I can point at by line, and it sits beside a D3 of 1 and a D4 of 3 on the same card -- which is the shape of an artifact that reports its own weaknesses accurately.

## Verdict

The most honest record of the three -- it names its own unreachable code and refuses two claims it cannot support -- wrapped around the least separable design, whose single durable-content assertion I broke without it noticing because that assertion's amount and running total are the same number.

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
