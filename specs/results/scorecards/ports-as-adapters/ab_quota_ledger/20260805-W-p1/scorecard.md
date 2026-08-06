# Scorecard — ab_quota_ledger, artifact `W`, judge pass 1

`run_id`: `20260805-W-p1` · scorecard_version 1 · rubric `references/eval_scorecard.md` digest `sha256:e33638087c4191da`

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

**Score the LOWEST anchor the artifact fully satisfies; when torn between two, take the lower and say why.**

## The mechanical block is recorded, never scored

`mechanical.json` beside this file holds kill counts, complexity figures, case counts, determinism and runtime. It sits beside the judgement so a reader can see when the two disagree — **and a disagreement is a finding, not a rounding error.**

## D1 — bug detection

*Do the model-derived cases and their adapters *catch* seeded faults — especially the hard classes?*

- **0** — Cases exist and pass; no seeded fault is caught. A suite that is green on broken code.
- **1** — Catches faults that change a value the projection already prints. Misses everything requiring a content assertion.
- **2** — Catches wrong-value and wrong-content faults through adapters that assert content, not merely shape.
- **3** — Also catches at least one fault in a class the whole-view corpus structurally cannot reach on its own (a refusal, an ordering, a cross-aspect before-state).
- **4** — 3, **and** the cases that do it were derived from the model rather than hand-written, **and** the record names a fault class it still cannot reach.

**Score:** **3**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:111-119`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:101-109`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:85-95`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:64-70`
**Refuses to claim** (required and non-null for a score of 4): _(not required below 4)_

**Rationale:** Anchor 2 is met -- the artifact's own case asserts durable content byte-for-byte against the file read independently of the object (test_extra.py:94), and map-checking kills durable_content 2 of 2 against map-silent's 1 of 2. Anchor 3 is met by measurement: corpus-neg kills the refusal class 3 of 3 where corpus-whole kills 0 of 3. I stopped at 3 and did not go to 4 because of something I measured rather than read: W's own suite SURVIVED both hard-class faults I seeded -- commit refunding the hold (cross-aspect) and the close-with-outstanding guard removed (refusal) -- while T's and U's own suites killed both. Every hard-class kill in W's record therefore comes from cases W did not author, and its own record delegates R4 to the shared suite by name (NOTES.md:140-146). Torn between 3 and 4, rule 5 sends me to 3.

## D2 — complexity

*Is the design as simple as its behavior requires, and no simpler?*

Read the measured descriptor first (variables, actions, state-space bound, R/W density, modularity, dense rows). Then judge whether the numbers reflect essential behavior or accidental structure.

- **0** — Complexity is unmeasured, or measured and ignored.
- **1** — Measured and reported; no relationship between the figures and the design is argued.
- **2** — The design's complexity is proportional to its behavior; no god-state, no variable written from everywhere.
- **3** — 2, **and** a simplification was made and its effect measured — the before and after figures are both recorded.
- **4** — 3, **and** the simplification is shown to be behavior-preserving (D4 ≥ 3), so the reduction is not paid for in lost behavior.

> **A drop in a complexity number is not evidence on its own.** MF-020: a metric can improve because an edge was deleted. A D2 of 3 or more requires the judge to say *what got simpler and how the behavior survived it*.

**Score:** **2**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:27-42`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:69-83`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:85-94`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:105-115`
**Refuses to claim** (required and non-null for a score of 4): _(not required below 4)_

**Rationale:** Anchor 2: no god-state, no variable written from everywhere -- each of the six dicts has a small, named set of writers, `max_depth` is flat, and every command validates then mutates in the feature's declared order. Anchor 3 fails for the same reason as the others: no simplification with before and after figures is recorded anywhere in the artifact. I want to be explicit that I did **not** score W higher here for being the smallest of the three; the mechanical block is recorded and I refused to convert it, and I note for the reader that the figure a naive reading would reward W for is bought by folding the I/O into the domain, which is precisely what costs it D3.

## D3 — modularity

*Is it ports and adapters in fact — domain independent of I/O, adapters swappable?*

- **0** — No boundary is discernible; state is written from everywhere.
- **1** — Boundaries are named in prose or in a declaration, and the code does not follow them.
- **2** — The code follows the declared boundaries. Cross-boundary calls go through something identifiable as a port.
- **3** — The domain does not import its I/O. An adapter could be replaced without touching the domain, and the judge names the specific swap.
- **4** — 3, **and** a driven port is exercised by a real adapter *and* a fake, with the same cases passing against both.

> **Import topology is not modularity.** Round 2 proved a codebase can pass every import check with its coupling entirely intact. A D3 of 3 or more requires evidence about what *calls* what at runtime, not what imports what.

**Score:** **1**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:39-42`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:60-65`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:119-121`
**Refuses to claim** (required and non-null for a score of 4): _(not required below 4)_

**Rationale:** There is no port and no boundary of any kind: the path is domain instance state (39), the domain truncates the file in its own constructor (42), reads it directly in a query (64), and calls bare `open()` in a private method (120). Anchor 2 is not reachable -- `_append_line` is a helper the domain calls on itself, not something an adapter could implement, and it is not even the single crossing point, since two of the three filesystem touches bypass it. I considered 0 and rejected it: "state is written from everywhere" is false of this code, whose writes are localized per command, so 0 overstates the disorder. 1 is the closest honest placement -- the one seam a reader can name is not followed as a boundary. No second implementation exists, so the packet's `corpus-port-swap:fake` column ran the real code (EVIDENCE.md:49-51).

## D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

**Score:** **3**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:25-153`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:180-187`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:71-81`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:117-124`
**Refuses to claim** (required and non-null for a score of 4): _(not required below 4)_

**Rationale:** Anchor 2 is met more explicitly than by either other artifact -- NOTES.md:25-153 is a clause-by-clause account mapping every requirement to a specific executed input, and it distinguishes what was run from what was reasoned about. Anchor 3 is met: the model-derived corpus decides against this code, 3734 cases executed, 0 failures on unmutated code. Anchor 4 asks that the check be demonstrated capable of failing, and here the two readings diverge: the union of checks W relies on does fail under seeded faults (EVIDENCE.md:71-81), but W's own contribution to that union did not fail on either of the two behaviors I broke by hand. Torn, I take the lower. I flag for the reader that this is the same measured fact as my D1 deduction, counted in two dimensions that ask different questions -- discount it accordingly if you disagree.

## D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

**Score:** **4**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:157-167`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:179-188`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:190-210`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:102-113`
**Refuses to claim** (required and non-null for a score of 4): That its `Result.reservation_id` reading on commit and release is verified by anything. NOTES.md:157-167: "Not run against by the shared suite either way ... so this is unverified by any assertion, only a reading I committed to. Marking it as such."

**Rationale:** This is the strongest dimension of this artifact and the clearest instance of the doctrine the card exists to protect. Anchor 3 appears three separate times: it refuses to call the close-order claim verified because no input distinguishes the two checks (190-210); it refuses to claim the blank-line filter does anything, saying "I did not run a case that exercises this filter; I am not claiming to have observed it doing anything" (179-188); and it downgrades its own ordering test in the test's own docstring rather than only in the notes (test_extra.py:108-114 calls the claim "trivially true"). Anchor 4: an author reporting that a shipped line of his own code is unreachable and unexercised is an unflattering result about the artifact. The writing here is the plainest of the three and it did not tempt me either way -- I scored the three specific refusals, each of which I checked against the code.

## Verdict

_One sentence a reader can act on._

## Disclosures

_Anything you saw that you were not meant to see, anything you ran that changed the tree, and anything you REJECTED. For three rounds running the best finding in this project came from the last one, and zero came from re-running the suite._

---

## Verdict

The most honest record of the three attached to the least structured code -- believe every caveat it makes, and do not let its brevity read as discipline, because its own tests miss the cross-aspect and refusal faults that the other two catch.

## Total

**13 of 20.** Contested dimensions (spread > 1 between the two blind passes): **none**.

## What this judge REJECTED

Returned once for all three artifacts and reproduced verbatim on each of this judge's cards.

**I rejected scoring D1 and D4 from the packet's kill tables alone, and it changed a score.** W's and U's evidence packets are **byte-identical apart from the artifact label** -- I diffed them and the diff returned nothing but the two header lines. Eleven mutants across eleven instruments, the per-class block, the port-binding columns, the executability counts: not one cell differs between an artifact with a seam and a 400-command model oracle, and an artifact with `open()` inline in the domain and eleven tests. T differs from them in only three measured cells. Had I scored from the tables, U and W would have been indistinguishable on D1 and D4. That is why I wrote my own seven faults and ran them against each author's own suite -- which separated them immediately (W survived F4 and F5). If I had not done that, this round would have produced identical D1/D4 numbers for two artifacts that are not equivalent.

**I nearly gave W a D3 of 0 and backed away.** Anchor 0's text is "no boundary is discernible; state is written from everywhere." The first clause fits W exactly; the second does not -- its writes are localized per command and each dict has a small writer set. I took 1 and said why, rather than letting half an anchor's text drive a floor score.

**I rejected the reading that would have given all three artifacts a D4 of 4** by crediting the shared harness to every artifact, and **the D2 reading that would have capped all three at 1** because no artifact measured its own complexity. All three landed at D2 = 2 and none reached 3, because not one recorded a before/after figure for any simplification -- an anchor reachable for the cost of two tool runs that nobody took.

**A check I started and abandoned.** I began re-running `scripts/code_complexity.py` myself to sanity-check the mechanical block, and stopped -- the block is recorded and never scored, so a second copy of an unscoreable figure could only tempt me to use it.

## Disclosures

Returned once for all three artifacts and reproduced verbatim on each of this judge's cards.

**Nothing on the must-not-open list was opened.** `ls` of the repository root returned several `*EPIC*.md` filenames in the listing; I read none of them. I read only `references/eval_scorecard.md`, `examples/validation/ab/FEATURE.md`, `examples/validation/ab/tests/test_behavior.py`, and the three `blind/artifact_*/` trees.

**I did compare the artifacts.** I scored each tree sequentially and did not open a later artifact's source while an earlier one was open, but the U/W evidence-packet diff entered my reasoning afterwards and affected W's D1 and D4 scores.

**What I inferred about arms.** T is unmistakably the product of a prompt that asked for ports and adapters. W's NOTES also refers to "Section 1's instructions" with entirely different content and to "Section 6's forbidden list"; U refers to no sections at all. I could not tell which arm is which treatment, and T and W sit at opposite ends of D3 (4 and 1) despite both citing "Section 1" -- whatever structural instruction they shared, only one produced a port. I did not adjust any score for arm.

**Ways this round may be fooling itself:** (1) U's and W's measured packets are byte-identical, and the only cell in the round that distinguished a real port from no port was T's M09 fake/real divergence -- one cell out of ninety-nine; (2) the positive control is RED in all three packets and the port columns are where it fails, on 294 executed accepting Reserve cases; (3) D1 and D4 risk becoming free points that report the harness's competence as the artifact's; (4) my own seven faults are one judge's work in one sitting and F4/F5 happening to be the two W missed could be luck.
