# Scorecard — ab_quota_ledger, artifact `T`, judge pass 2

`run_id`: `20260806-v2-T-p2` · scorecard_version 2 · rubric `references/eval_scorecard.md` digest `sha256:19c6712ed509a228`

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:111-119`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:101-109`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:71-73`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:263`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:139-140`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:155-158`

**Refuses to claim** (required and non-null for a score of 4):

_Not required below a score of 4, and none is claimed here._

**Rationale:**

Anchor 2 is met on content and not shape: map-checking takes both durable-content mutants where map-silent takes one (EVIDENCE.md:101-109), and the difference between those two columns IS the content assertion. Anchor 3 is met: guard_relaxation is 0 of 3 for corpus-whole and 3 of 3 for corpus-neg (EVIDENCE.md:111-119) -- a refusal class the whole-view corpus structurally cannot reach -- and I reproduced it rather than reading it, deleting the tenant_closed guard at domain.py:139-140 and watching two of T's own cases and one shared case fail. Anchor 4 is the closest call on this card and I withheld it. Its two extra clauses are arguably satisfied: corpus-neg is model-derived, and NOTES.md:136-141 names a class nothing here reaches (a durable append that raises, leaving memory ahead of the ledger). What stopped me is the control block -- the positive control M07 is red with deciding: [] on this tree (EVIDENCE.md:263), and corpus-port and corpus-slice-led both SURVIVED a mutant they were required to kill. The top anchor would then rest on an instrument this run could not validate, so per rule 5 I took the lower. Prose quality tempted me here: T's record is the most fluent of the three and I gave it zero weight; the 3 is carried by the class rows and by my own runs.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:118-120`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:106-114`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:70-84`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:78`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:80`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:324-342`

**Refuses to claim** (required and non-null for a score of 4):

_Not required below a score of 4, and none is claimed here._

**Rationale:**

available is not stored: it is quota - held - committed computed per call (domain.py:118-120), so R1 cannot drift, and the three written pieces of state each have one writer (domain.py:106-114). That is proportionality, and the packet corroborates it from an unexpected direction: M08 and M10 had to be seeded into T by ADDITION rather than perturbation (EVIDENCE.md:78, EVIDENCE.md:80) because those faults have no one-token form in this design. I hit the same wall myself -- to make commit() refund the hold I had to invent a statement, since there is no _available to perturb. I stopped at 2 because anchor 3 asks for before and after FIGURES and T records none; the simplification is argued (NOTES.md:70-84) and never measured. The mechanical block disagrees with the direction of this score and the disagreement is the finding, not something to split: T is the LARGEST artifact on every raw figure -- 202 code lines, 4 modules, 25 public surface (EVIDENCE.md:324-342) -- and I still judged its complexity proportional, because the extra structure buys the swap D3 records. Do not read this 2 as agreement with the block.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:22-43`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:106-114`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/file_journal.py:13-35`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/memory_journal.py:14-22`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/__init__.py:37-39`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:26-36`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:260-270`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:168`

**Refuses to claim** (required and non-null for a score of 4):

T does not claim the port hides the record format: the COMMIT/CLOSE rendering is deliberately kept in the domain and the Journal carries a finished string (domain.py:159, NOTES.md:57-66), so FileJournal is NOT format-independent and a second adapter inherits nothing about framing. It also refuses any further indirection -- no port in front of the arithmetic, no repository interface over the reservations dict (NOTES.md:53-55).

**Rationale:**

The port is declared inside the domain in the domain's own vocabulary (domain.py:22-43), the domain never constructs one (domain.py:106-114), and the composition module is the only file that names both sides (__init__.py:37-39). Two working implementations exist (file_journal.py:13-35, memory_journal.py:14-22) and ONE case list runs against both through a parametrized fixture (tests/test_ledger.py:26-36) -- 53 cases green on both wirings, which I re-ran. The caveat says import topology is not modularity, so I checked calls and not imports: I seeded a fault into FileJournal.records ONLY and re-ran T's own suite. Six failures, every one of them a [file] parameterization and none a [memory] one. The same cases really do execute against two different implementations behind the port; that is a runtime fact, not a declaration. The packet corroborates it independently: corpus-port-swap:fake and :real differ on exactly one mutant (EVIDENCE.md:168), which is only possible if the binding substituted code. The named swap: replace FileJournal(ledger_path) with InMemoryJournal() at __init__.py:39 -- one line, in the one module allowed to know both sides, no domain file touched. An AST test asserts the domain's import set is exactly {__future__, dataclasses, typing} (tests/test_ledger.py:260-270); I count that as corroboration only, since the caveat is explicit that imports are not the evidence.

## D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

**Score:** 4

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:117-131`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:202-225`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:161-199`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:180-186`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:61-62`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:151-160`

**Refuses to claim** (required and non-null for a score of 4):

T refuses to claim R2 survives a failed durable write: commit updates memory and then appends (domain.py:151-160), and NOTES.md:136-141 names this as the one place R2 is not enforced by construction -- no rollback, no write-ahead ordering, and no case covers it.

**Rationale:**

Anchor 2: the baseline behaviors are enumerated as literal expected transcripts rather than shape checks -- interleaved per-tenant running totals (tests/test_ledger.py:117-131), a nine-way rejection parametrization that re-reads the durable side too (tests/test_ledger.py:161-199), and one long mixed run read off a concrete expected ledger (tests/test_ledger.py:202-225) -- and the shared suite passes unedited, 28 of 28, which I re-ran (EVIDENCE.md:61-62). Anchor 3 is carried by the EVAL's corpus and not by anything T brought: 3734 model-graph cases execute against it with 0 failures on unmutated code (EVIDENCE.md:180-186), while T's own checks are hand-written assertions plus an AST check. I say that plainly so a third pass can disagree with the attribution rather than with the arithmetic. Anchor 4 I ran myself: four behavior-breaking edits, one at a time, each reverted and re-diffed byte-identical -- a removed refusal, a stale running total, a commit that refunds the hold, and a reversed durable read. T's own suite failed on all four (2, 26, 6 and 6 cases). The check is demonstrated capable of failing, not asserted to be.

## D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

**Score:** 4

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:1-11`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/file_journal.py:20-23`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:125-147`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:136-141`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:102-123`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:260-270`

**Refuses to claim** (required and non-null for a score of 4):

T refuses to reach any verdict on non-integer amounts: reserve('acme', 2.5) is accepted and would print as 2.5 in a COMMIT line, and it declines to add a seventh rejection reason rather than pretend the fixed six-word vocabulary covers the case (NOTES.md:142-145).

**Rationale:**

The blind spots are in the artifact and not only in a report: the domain module's own docstring states what it holds and what it refuses to hold (domain.py:1-11), and the file adapter's states which framing belongs to the file and not to the contract (file_journal.py:20-23). NOTES.md:125-147 is a list of interpretations picked under ambiguity, each named as a choice rather than as a fact. Anchor 3: item 3 declines to certify R2 -- 'the one place I can name where R2 is not enforced by construction' -- instead of reporting a clean (NOTES.md:136-141). Anchor 4: the record carries results unflattering to itself. It admits its public entry point is a factory function named like a class and that this reads oddly (NOTES.md:102-123), and that a non-integer amount would flow into a COMMIT line unchecked. I checked the checkable claims rather than crediting them: 53 own cases and 28 shared cases both pass, and the import assertion it says it makes exists and passes (tests/test_ledger.py:260-270).

## Verdict

Ports and adapters in fact rather than in prose -- one declared port, a real and a fake implementation, and one case list I confirmed by execution runs against both -- so treat T as this round's reference for D3; its ceiling is D2, where the simplification is argued and never measured.

## Disclosures

_Anything you saw that you were not meant to see, anything you ran that changed the tree, and anything you REJECTED. For three rounds running the best finding in this project came from the last one, and zero came from re-running the suite._

**Anything I saw that I was not meant to see.** I read the rubric (`references/eval_scorecard.md`), `examples/validation/ab/FEATURE.md`, `examples/validation/ab/tests/test_behavior.py`, and the three `blind/artifact_*/` directories. Nothing else. One leak to record: The artifacts' own NOTES.md files quote fragments of the prompts they were given -- 'the architecture ask' and 'Section 1: the domain holds no file handle, no path' in one, 'Section 6's forbidden list' and 'as instructed' in another, and a third that mentions no sections at all. That makes the arms partially inferable from inside the blind directories, and I did form an impression of which artifact came from which kind of prompt. I am recording it rather than acting on it: I did not open arm_a/, arm_b/, arm_c/, README.md, seeded_faults.toml, any PREDICTIONS file, any -p1 directory, UNBLINDING.md or anything else under specs/results/scorecards/ outside the three blind directories and my own three card directories, and I made no attempt to confirm the mapping. Separately, my scratch directory already contained a `fill.py` written before this session began; I did not open it, and I wrote my own script under a different name.

**A finding about the packets themselves.** artifact_U/EVIDENCE.md and artifact_W/EVIDENCE.md are BYTE-IDENTICAL apart from the two header lines naming the artifact (`diff` reports 1c1 and 3c3 and nothing else). Either those two trees really did measure identically across all 11 mutants x 11 instruments, or one packet was copied from the other. Nothing inside the packet distinguishes the two cases, so I scored no difference between U and W off that table; every U-vs-W difference on these cards comes from the code, the tests, or what I ran.

**Anything I ran, and whether it changed anything on disk.** Everything listed in `judging_practice`. All execution happened in a scratch tree outside the repository; twelve fault seedings were applied and reverted there and the scratch copies were then diffed back against the blind directories and found identical apart from __pycache__. NOTHING ON DISK IN THE REPOSITORY WAS CHANGED by me except the three card directories I was asked to fill. I ran no git command that changes state.

**Anything I REJECTED.**

- REJECTED D1 = 4. The anchor's own text is arguably satisfied -- the catching cases are model-derived and the record names an unreachable class. I withheld it because the positive control M07 is red with deciding: [] on this tree, so the top anchor would rest on an instrument this run could not validate. Rule 5: torn, took the lower, said why.
- REJECTED D2 = 3, and this was the nearest miss on the card. The simplification (available derived, not stored) is real, argued, and corroborated from outside the artifact by the packet's seeded_by column and by my own inability to perturb a commit-refund into T without inventing a statement. Anchor 3 asks for before and after FIGURES; none exist, so 2.
- REJECTED reading the mechanical block as evidence against D2. T is the largest artifact on every raw figure. Recorded as a disagreement between block and judgement rather than split down the middle.
- REJECTED counting T's dual-wiring suite as a model-derived check for D4 anchor 3. It is hand-written, however thorough. Anchor 3 there is carried by the eval's corpus and the card says so.
- REJECTED prose quality explicitly. T's record is the best-written of the three and that is worth zero; every score above 2 on this card cites code or a run.
