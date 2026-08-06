# Scorecard — ab_quota_ledger, artifact `W`, judge pass 2

`run_id`: `20260806-v2-W-p2` · scorecard_version 2 · rubric `references/eval_scorecard.md` digest `sha256:19c6712ed509a228`

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

**Executed own faults:** true

**What was run:**

- Copied artifact_T, artifact_U and artifact_W and the shared suite (examples/validation/ab/tests/test_behavior.py) into a scratch tree OUTSIDE the repository. Nothing in the repository was written to.
- Baseline, unmutated: each artifact's own suite and the unedited shared suite. T 53 own / 28 shared, U 32 own / 28 shared, W 11 own / 28 shared -- all green, which is the NOTES.md counts checked rather than credited.
- Seeded FOUR behavior-breaking faults of my own, one at a time, into each of the three artifacts (12 seedings), reverting after each and re-diffing the scratch tree byte-identical against the blind directories: F1 removed reserve()'s tenant_closed guard; F2 wrote the PRE-commit running total into the COMMIT line; F3 made commit() give the hold back to available (a cross-aspect before-state fault); F4 reversed the durable read path.
- Ran each artifact's OWN suite and the shared suite under every fault. Own-suite failures -- T: 2 / 26 / 6 / 6. U: 2 / 4 / 3 / 2. W: 1 / 1 / ZERO / 1. The shared suite failed 1 / 6 / 2 / 5 cases on all three identically.
- For T, F4 was seeded in quota_ledger/file_journal.py ONLY: all six failures carried the [file] fixture parameter and none the [memory] one, which is runtime evidence that the same cases execute against two implementations behind the port.
- For U, the three failures under F3 included test_rules_hold_through_a_long_random_sequence -- its own model-based check demonstrated capable of failing.
- For W under F3, its own eleven cases reported 11 passed; only the shared suite caught it.
- Verified afterwards with `diff -r` that all three scratch copies are identical to the blind directories apart from __pycache__, and that nothing in the repository changed.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:111-119`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:101-109`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:260`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:36-50`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:64-70`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:90-93`

**Refuses to claim** (required and non-null for a score of 4):

_Not required below a score of 4, and none is claimed here._

**Rationale:**

Anchors 2 and 3 are met by the same shared instrument as on the other two cards: map-checking takes both durable-content mutants where map-silent takes one (EVIDENCE.md:101-109), and corpus-neg takes all three guard relaxations where corpus-whole takes none (EVIDENCE.md:111-119) -- a refusal class the whole-view corpus cannot reach on its own. I reproduced the refusal case by hand and W's own suite and the shared suite each failed one case. W's own cases add genuine ties the shared suite does not pin: closed-beats-not-positive on reserve (test_extra.py:36-50) and the double-digit id sort (test_extra.py:64-70). Anchor 4 withheld: the positive control M07 is red with deciding: [] (EVIDENCE.md:260). A second finding I record here WITHOUT converting it into a point: I seeded a cross-aspect fault -- commit giving the hold back to available at quota_ledger.py:90-93 -- and W's own eleven cases reported 11 passed, where T's and U's own suites both failed. Only the shared hand-written suite caught it. Anchor 3 asks only that the hard class be caught by something, and it was, so this costs W nothing on D1. It costs it on D4.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:31-42`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:46-65`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:85-94`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:119-121`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:310-328`

**Refuses to claim** (required and non-null for a score of 4):

_Not required below a score of 4, and none is claimed here._

**Rationale:**

78 code lines, the smallest of the three, and the structure is honest about what it holds: each dict is written by the command that owns it (quota_ledger.py:31-42), the queries are one-line lookups plus one file read (quota_ledger.py:46-65), and there is exactly one durable writer (quota_ledger.py:119-121). No god-state and no variable written from everywhere, so anchor 2 holds. The cost of storing _available rather than deriving it is real and lands in the same place my D1 note does: R1 is maintained by reserve, release and commit agreeing with one another (quota_ledger.py:81, :101, :90-93) rather than by construction, which is what makes a commit-refund fault expressible as a one-statement perturbation here. Anchor 3 is unreachable: no before and after figures exist. The mechanical block makes W the smallest artifact on nearly every figure (EVIDENCE.md:310-328) and I did not convert that into a higher score -- small is not the same as proportional, and part of the smallness is bought by having no seam, which is D3's business and not D2's.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:39-42`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:60-65`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:119-121`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:26-27`

**Refuses to claim** (required and non-null for a score of 4):

_Not required below a score of 4, and none is claimed here._

**Rationale:**

There is no port. File I/O sits in three places inside the class that holds the rules: the constructor takes a path and truncates it (quota_ledger.py:39-42), ledger_lines() does a raw read_text() in the query itself (quota_ledger.py:60-65), and _append_line opens the file for append (quota_ledger.py:119-121). _append_line funnels every WRITE, which is why this is not a 0 -- state is not written from everywhere and each aspect has one writer. It is not a 2 either: no boundary is declared anywhere in the artifact, and the read half of the durable side bypasses the only helper that could have been the seam, so cross-boundary calls do not all go through something identifiable as a port. Anchor 1's own wording does not fit W cleanly -- it describes an artifact that NAMES boundaries and then does not follow them, and W names none -- so I am scoring the ladder position rather than the sentence, and saying so. Torn between 1 and 2, I took the lower per rule 5: a seam has to cover the boundary to be a boundary. Note this is not dishonesty -- W claims no modularity it does not have, which is why D5 is where it is.

## D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

**Score:** 3

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:25-31`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:124-146`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:85-95`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:117-124`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:180-186`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:61-62`

**Refuses to claim** (required and non-null for a score of 4):

_Not required below a score of 4, and none is claimed here._

**Rationale:**

Anchor 2 is met better here than anywhere else in this round: NOTES.md:25-31 opens a clause-by-clause account that, for every clause of the feature, names where it lives and the concrete input that would catch its absence -- and every test it names exists and passes, which I checked by running all eleven rather than by reading the list. The durable side is verified against the raw bytes independently of the accessor (test_extra.py:85-95) and R3's singularity is checked after a rejected second close (test_extra.py:117-124). Anchor 3 is carried by the EVAL's corpus -- 3734 model-graph cases, 0 failures on unmutated code (EVIDENCE.md:180-186) -- and by nothing W brought; its own checks are hand-written. Anchor 4 is where I stopped, and I stopped because I ran it rather than read it. The account explicitly delegates R1 and R4 to the shared suite (NOTES.md:124-146), and when I made commit() refund the hold, W's own suite reported 11 passed while the shared suite failed 2. The behavior IS checked -- but the check W itself carries was demonstrated NOT to be capable of failing on one of the behaviors its own record enumerates. Torn between 3 and 4, I took the lower and named the case.

## D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

**Score:** 4

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:17-19`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:56-58`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:61-65`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:190-210`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:179-188`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:155-167`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:102-113`

**Refuses to claim** (required and non-null for a score of 4):

W refuses to claim it verified close_tenant's unknown_tenant-before-outstanding_reservations ordering, because no input exists that distinguishes the two checks, and says so rather than listing it as tested (NOTES.md:102-113, NOTES.md:190-210). It also refuses to claim its blank-line filter was ever observed doing anything -- 'I did not run a case that exercises this filter; I am not claiming to have observed it doing anything, only that it is there' (NOTES.md:179-188).

**Rationale:**

This is W's strongest dimension and it is strong on the anchor's own terms. Anchor 2: limits sit in the code, not only in the report -- which commands set reservation_id and why (quota_ledger.py:17-19), why the id sort is numeric (quota_ledger.py:56-58), and why the query re-reads the file instead of trusting a mirror (quota_ledger.py:61-65). Anchor 3 is textbook: the artifact refuses to certify what it could not observe -- 'I could not produce evidence for an ordering claim that has no distinguishing input' (NOTES.md:190-210) and 'I am not claiming to have observed it doing anything' (NOTES.md:179-188). Anchor 4: the unflattering results are about itself. It ships a line it admits is unreachable, and flags a design decision as 'unverified by any assertion, only a reading I committed to' (NOTES.md:155-167). I checked rather than credited: every test the account names exists and the whole file passes. Prose quality is never an input and the temptation ran the OTHER way here -- W's record is the longest and most repetitive of the three, and I did not let that reduce the score.

## Verdict

The most honest record of the three and the least modular code -- no port, file I/O in three places inside the rules class -- and its own eleven cases went green under a cross-aspect fault that both other artifacts' suites caught, so read its clause-by-clause account as an accurate map of what the SHARED suite checks rather than of what W checks.

## Disclosures

_Anything you saw that you were not meant to see, anything you ran that changed the tree, and anything you REJECTED. For three rounds running the best finding in this project came from the last one, and zero came from re-running the suite._

**Anything I saw that I was not meant to see.** I read the rubric (`references/eval_scorecard.md`), `examples/validation/ab/FEATURE.md`, `examples/validation/ab/tests/test_behavior.py`, and the three `blind/artifact_*/` directories. Nothing else. One leak to record: The artifacts' own NOTES.md files quote fragments of the prompts they were given -- 'the architecture ask' and 'Section 1: the domain holds no file handle, no path' in one, 'Section 6's forbidden list' and 'as instructed' in another, and a third that mentions no sections at all. That makes the arms partially inferable from inside the blind directories, and I did form an impression of which artifact came from which kind of prompt. I am recording it rather than acting on it: I did not open arm_a/, arm_b/, arm_c/, README.md, seeded_faults.toml, any PREDICTIONS file, any -p1 directory, UNBLINDING.md or anything else under specs/results/scorecards/ outside the three blind directories and my own three card directories, and I made no attempt to confirm the mapping. Separately, my scratch directory already contained a `fill.py` written before this session began; I did not open it, and I wrote my own script under a different name.

**A finding about the packets themselves.** artifact_U/EVIDENCE.md and artifact_W/EVIDENCE.md are BYTE-IDENTICAL apart from the two header lines naming the artifact (`diff` reports 1c1 and 3c3 and nothing else). Either those two trees really did measure identically across all 11 mutants x 11 instruments, or one packet was copied from the other. Nothing inside the packet distinguishes the two cases, so I scored no difference between U and W off that table; every U-vs-W difference on these cards comes from the code, the tests, or what I ran.

**Anything I ran, and whether it changed anything on disk.** Everything listed in `judging_practice`. All execution happened in a scratch tree outside the repository; twelve fault seedings were applied and reverted there and the scratch copies were then diffed back against the blind directories and found identical apart from __pycache__. NOTHING ON DISK IN THE REPOSITORY WAS CHANGED by me except the three card directories I was asked to fill. I ran no git command that changes state.

**Anything I REJECTED.**

- REJECTED D3 = 2. _append_line is a single write funnel and it tempted me; what took it to 1 is that ledger_lines() reads the file inline in the query, bypassing that funnel, and that no boundary is declared anywhere for the code to be following.
- REJECTED D4 = 4, after running it rather than reading it. W's own suite was green under a fault that both other artifacts' own suites caught. Had I scored the packet alone I would have given the 4, because the packet's kill table shows corpus-whole taking M08 1 of 1 and says nothing about whose cases those are.
- REJECTED D1 = 2. The hard class is caught for W by the same model-derived corpus as everywhere else and anchor 3 asks no more than that. I did not let the hole in W's own suite double-count into D1 as well as D4.
- REJECTED treating the length and repetition of W's record as a negative, and REJECTED treating its clause-by-clause thoroughness as a positive on any dimension other than the two where I could check it (D4 anchor 2, D5).
- REJECTED the argument that NOTES.md is 'only a report' and so cannot satisfy D5 anchor 2's 'in the artifact itself'. It ships with the artifact, and the code carries limits of its own at quota_ledger.py:17-19 and :61-65 independently.
