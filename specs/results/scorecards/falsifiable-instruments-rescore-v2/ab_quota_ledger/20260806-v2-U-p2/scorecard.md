# Scorecard — ab_quota_ledger, artifact `U`, judge pass 2

`run_id`: `20260806-v2-U-p2` · scorecard_version 2 · rubric `references/eval_scorecard.md` digest `sha256:19c6712ed509a228`

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:111-119`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:101-109`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:260`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:142-143`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:315-362`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:255-273`

**Refuses to claim** (required and non-null for a score of 4):

_Not required below a score of 4, and none is claimed here._

**Rationale:**

Anchor 2 is met on content and not shape: map-checking takes both durable-content mutants where map-silent takes one (EVIDENCE.md:101-109). Anchor 3 is met: guard_relaxation is 0 of 3 for corpus-whole and 3 of 3 for corpus-neg (EVIDENCE.md:111-119), a refusal class the whole-view corpus cannot reach on its own, and I reproduced it by deleting the tenant_closed guard at quota_ledger.py:142-143 -- two of U's own cases and one shared case failed. U's own cases reach the hard classes independently: the declared rejection ORDER is pinned by cases the shared suite does not contain (test_quota_ledger.py:255-273), and when I seeded a cross-aspect fault -- commit giving the hold back to available -- three of U's own cases failed, one of them the randomized model sweep (test_quota_ledger.py:315-362). Anchor 4 withheld for the reason that applies to every card in this round: the positive control M07 is red with deciding: [] (EVIDENCE.md:260) and corpus-port SURVIVED a mutant it was required to kill, so the top anchor would rest on an unvalidated instrument. Rule 5, took the lower.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:103-110`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:72-92`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:125-130`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:199-205`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:310-328`

**Refuses to claim** (required and non-null for a score of 4):

_Not required below a score of 4, and none is claimed here._

**Rationale:**

available is stored and maintained by reserve and release (quota_ledger.py:103-110), so R1 is kept by two sites agreeing rather than by construction -- but nothing is written from everywhere, each dict has a small named set of writers, and the durable side is off in its own class (quota_ledger.py:72-92). That is anchor 2. Two pieces of accidental structure keep it from being tighter, and neither is a god-state: _Reservation.seq stores the integer that is already inside the id it sits beside (quota_ledger.py:199-205), and outstanding_ids() sorts on every call although insertion order already IS allocation order (quota_ledger.py:125-130). Anchor 3 is unreachable: no before and after figures are recorded anywhere in the artifact. The mechanical block puts U in the middle on every figure (EVIDENCE.md:310-328) and I did not convert that into anything -- a middle number is not a middle judgement.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:72-92`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:110`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:132-134`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:168`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:193`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:113-118`

**Refuses to claim** (required and non-null for a score of 4):

_Not required below a score of 4, and none is claimed here._

**Rationale:**

Every durable operation in the rules goes through one seam: QuotaLedger never touches the filesystem itself -- self._ledger.append(...) at :168 and :193 and self._ledger.lines() at :134 are the only durable calls, and path, encoding, truncation, parent-directory creation and the trailing newline all live inside _LedgerFile (quota_ledger.py:72-92). The declared boundary is exactly that and no more (NOTES.md:113-118), and the code follows it, which is anchor 2. Anchor 3 fails on one line: QuotaLedger.__init__ builds its own adapter out of a path (quota_ledger.py:110), so the rules do hold a path and replacing the durable side means editing the module that holds the rules. There is no injection point and no second implementation, so I can name no swap -- and the anchor requires me to name one. The packet agrees from the other side: corpus-port-swap:fake and :real are identical on all eleven mutants, because for U the 'fake' run is the real implementation again.

## D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

**Score:** 4

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:279-312`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:315-362`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:37-39`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:114-130`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:180-186`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:61-62`

**Refuses to claim** (required and non-null for a score of 4):

U refuses to claim crash safety from its write-before-mutate ordering: NOTES.md:59-63 states that nothing in the feature requires it, that it is NOT a crash-safety feature, and that no fsync, journaling or recovery was built -- the ordering 'just costs nothing and orders the two sides sensibly'.

**Rationale:**

Anchor 2: the enumerated behaviors are checked against the bytes on disk rather than against the accessor that reports on them (test_quota_ledger.py:37-39), including R4's 'a rejection writes nothing durable' across six commands (test_quota_ledger.py:114-130), and the shared suite passes unedited, 28 of 28, which I re-ran (EVIDENCE.md:61-62). Anchor 3 is met by something U BROUGHT rather than by the eval's instrument: check_rules recomputes R1, R2 and R3 from scratch against an independent model and against the file on disk after every one of 400 randomized commands, accepted and rejected alike (test_quota_ledger.py:279-312, :315-362), and it asserts at the end that the sweep actually exercised acceptances rather than only rejections. The eval's corpus (EVIDENCE.md:180-186) is a second, independent instance of the same anchor. Anchor 4 I ran: I added one line to commit() giving the hold back to available, and test_rules_hold_through_a_long_random_sequence was one of the three cases that failed -- the model check is demonstrated capable of failing, not asserted to be. All four of my faults were caught (2, 4, 3 and 2 cases). This is the only artifact of the three whose model-derived check is its own.

## D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

**Score:** 4

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:74-77`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:163-166`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:88-111`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:96-103`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:59-63`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:120-129`

**Refuses to claim** (required and non-null for a score of 4):

U refuses to claim integrality is enforced: it implements 'amount is less than 1' literally, states that 1.5 would be held, committed and printed into a COMMIT line unchecked, and observes that the fixed six-reason vocabulary contains no reason it could have rejected with (NOTES.md:96-103). It also refuses to invent a return value for available('nobody') rather than ship a sentinel (NOTES.md:89-94).

**Rationale:**

Limits sit in the code as well as in the record: _LedgerFile's docstring states why reads come from the file and not from a mirror (quota_ledger.py:74-77) and commit() states what the write ordering does and does not buy (quota_ledger.py:163-166). NOTES.md:88-111 names blind spots unprompted. Anchor 3: it declines to invent a return value for a query on an unknown tenant and says so, rather than shipping a 0 or a None that would read as an answer (NOTES.md:89-94). Anchor 4: the unflattering results are about itself -- a non-integer amount 'would be held and committed as 1.5, and would print that way in a COMMIT line' (NOTES.md:96-103), and it discloses that it ran ls and saw the NAMES of files it had been told not to open (NOTES.md:120-129). A disclosure that costs the author something is exactly what this anchor asks for. I verified the checkable claims: 32 own cases and 28 shared cases pass, and the write-before-mutate ordering it describes is where it says it is.

## Verdict

The only artifact carrying its own model-derived check -- a 400-command randomized sweep that recomputes R1/R2/R3 from the bytes on disk, which I confirmed fails under a seeded fault -- but its durable seam is a private class it constructs itself, so there is no swap to name and D3 stops at 2.

## Disclosures

_Anything you saw that you were not meant to see, anything you ran that changed the tree, and anything you REJECTED. For three rounds running the best finding in this project came from the last one, and zero came from re-running the suite._

**Anything I saw that I was not meant to see.** I read the rubric (`references/eval_scorecard.md`), `examples/validation/ab/FEATURE.md`, `examples/validation/ab/tests/test_behavior.py`, and the three `blind/artifact_*/` directories. Nothing else. One leak to record: The artifacts' own NOTES.md files quote fragments of the prompts they were given -- 'the architecture ask' and 'Section 1: the domain holds no file handle, no path' in one, 'Section 6's forbidden list' and 'as instructed' in another, and a third that mentions no sections at all. That makes the arms partially inferable from inside the blind directories, and I did form an impression of which artifact came from which kind of prompt. I am recording it rather than acting on it: I did not open arm_a/, arm_b/, arm_c/, README.md, seeded_faults.toml, any PREDICTIONS file, any -p1 directory, UNBLINDING.md or anything else under specs/results/scorecards/ outside the three blind directories and my own three card directories, and I made no attempt to confirm the mapping. Separately, my scratch directory already contained a `fill.py` written before this session began; I did not open it, and I wrote my own script under a different name.

**A finding about the packets themselves.** artifact_U/EVIDENCE.md and artifact_W/EVIDENCE.md are BYTE-IDENTICAL apart from the two header lines naming the artifact (`diff` reports 1c1 and 3c3 and nothing else). Either those two trees really did measure identically across all 11 mutants x 11 instruments, or one packet was copied from the other. Nothing inside the packet distinguishes the two cases, so I scored no difference between U and W off that table; every U-vs-W difference on these cards comes from the code, the tests, or what I ran.

**Anything I ran, and whether it changed anything on disk.** Everything listed in `judging_practice`. All execution happened in a scratch tree outside the repository; twelve fault seedings were applied and reverted there and the scratch copies were then diffed back against the blind directories and found identical apart from __pycache__. NOTHING ON DISK IN THE REPOSITORY WAS CHANGED by me except the three card directories I was asked to fill. I ran no git command that changes state.

**Anything I REJECTED.**

- REJECTED D3 = 3, and it was the nearest miss on this card. _LedgerFile is a clean two-method seam and the rules genuinely never touch the filesystem, which is most of what anchor 3 describes. The constructor building its own adapter out of a path (quota_ledger.py:110) is what stopped it: I could not name a swap that does not edit the module holding the rules, and the anchor requires the judge to name one.
- REJECTED D1 = 4, on the red positive control, exactly as on the other two cards.
- REJECTED the argument that U's randomized sweep is 'just another hand-written test'. I ran a fault under it and it failed, and it recomputes the rules from an independent model rather than comparing against literals. That decided D4 anchor 3, and it is the one place on these three cards where anchor 3 is met by the artifact instead of by the harness.
- REJECTED holding U's own disclosure against it. It records having seen the names (not the contents) of files on its forbidden list. Penalising a volunteered disclosure would train the next artifact to stay quiet, and D5's top anchor asks for precisely this.
- REJECTED counting the U/W packet twinning as evidence about U. See the note above on the byte-identical evidence packets.
