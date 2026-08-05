# Scorecard — ab_quota_ledger, artifact `U`, judge pass 1

`run_id`: `20260805-U-p1` · scorecard_version 1 · rubric `references/eval_scorecard.md` digest `sha256:e33638087c4191da`

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

**Score:** **4**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:111-119`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:101-109`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:279-312`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:315-362`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:162-170`
**Refuses to claim** (required and non-null for a score of 4): That non-integer amounts are handled -- NOTES.md:96-103 states that `1.5` is neither rejected nor integral, would be committed as `1.5` and would print that way in a COMMIT line, and that if integrality is meant to be enforced then the six-reason vocabulary is missing a reason for it. It refuses to add a seventh reason rather than quietly widen the contract.

**Rationale:** Anchor 2 by measurement: map-checking 2 of 2 on durable_content against map-silent's 1 of 2 (EVIDENCE.md:101-109), and U's own assertions read the file from disk independently of the accessor (test_quota_ledger.py:37-39, 85-95). Anchor 3: corpus-neg kills the refusal class 3 of 3 where corpus-whole kills 0 of 3 (EVIDENCE.md:111-119). Anchor 4: those cases are model-derived, the record names an unreachable class, and U's own cases are the strongest own-oracle of the three -- a 400-command randomized sweep re-deriving R1, R2 and R3 from an independent model against the bytes on disk after every single command (test_quota_ledger.py:279-362). All seven faults I seeded died against U's own suite, including two the shared suite misses.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:103-110`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:144-152`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:174-182`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:62-69`
**Refuses to claim** (required and non-null for a score of 4): _(not required below 4)_

**Rationale:** Anchor 2: complexity is proportional and there is no god-state -- `_available` has exactly two writers (reserve at 150, release at 180), `_committed` one (170), `_closed` one (194). Anchor 3 is not satisfied: no simplification is recorded with before and after figures; NOTES.md:48-86 argues six design choices in prose and measures none of them. I noted one piece of accidental structure that kept me from reading the design as tighter than it is: `_Reservation` stores both `reservation_id` and `seq` (62-69) when the id is literally `f"r{seq}"` (204), so one field is derivable from the other. I did not convert the mechanical block into a score.

## D3 — modularity

*Is it ports and adapters in fact — domain independent of I/O, adapters swappable?*

- **0** — No boundary is discernible; state is written from everywhere.
- **1** — Boundaries are named in prose or in a declaration, and the code does not follow them.
- **2** — The code follows the declared boundaries. Cross-boundary calls go through something identifiable as a port.
- **3** — The domain does not import its I/O. An adapter could be replaced without touching the domain, and the judge names the specific swap.
- **4** — 3, **and** a driven port is exercised by a real adapter *and* a fake, with the same cases passing against both.

> **Import topology is not modularity.** Round 2 proved a codebase can pass every import check with its coupling entirely intact. A D3 of 3 or more requires evidence about what *calls* what at runtime, not what imports what.

**Score:** **2**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:72-92`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:110`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:168`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:193`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:134`
**Refuses to claim** (required and non-null for a score of 4): _(not required below 4)_

**Rationale:** Anchor 2 is fully met: every durable call goes through `_LedgerFile` (writes at 168 and 193, reads at 134->90), nothing else in the module touches the filesystem, and that class is identifiable as a seam with a two-method surface. Anchor 3 fails on a fact I tested rather than inferred: the implementation is chosen inside the domain's own constructor at line 110, there is no injection point, and the only substitution I could achieve was rebinding the module-private global `quota_ledger._LedgerFile` from outside -- which worked, but is reaching into the domain module's namespace, not replacing an adapter behind a port. NOTES.md:113-118 is straightforward that no abstraction over the file was intended, so this is a design choice honestly stated, not a claim the code betrays. Anchor 4 is unreachable: no second implementation ships, and the packet records that the `corpus-port-swap:fake` column therefore ran the real one (EVIDENCE.md:49-51).

## D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

**Score:** **4**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:180-187`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:71-81`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:279-312`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:355-362`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:164-171`
**Refuses to claim** (required and non-null for a score of 4): Crash safety. NOTES.md:58-63 orders the durable write before the in-memory change and then explicitly refuses to call it a crash-safety feature: "no fsync, no journaling, no recovery; that is out of scope." I verified the ordering claim is true of the code (168 before 170; 193 before 194).

**Rationale:** Anchor 2: behaviors are enumerated and each is checked, including rejection-order ties the shared suite never distinguishes (255-273). Anchor 3: the model-derived corpus decides against this code with 0 failures on unmutated code (EVIDENCE.md:180-187), and U additionally ships its own independent-model oracle. Anchor 4: behavior-breaking changes are demonstrated caught in the packet, and independently all seven of my faults were caught by U's own suite. The detail that decided 4 over 3 is test_quota_ledger.py:355-362 -- the sweep asserts that it actually exercised acceptances, closes and durable writes, because "a sequence that only ever rejected would prove nothing." That is a check on the check.

## D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

**Score:** **4**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:96-103`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:87-94`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:120-129`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:58`
**Refuses to claim** (required and non-null for a score of 4): That its own blinding was clean. NOTES.md:120-129 discloses, unforced, that it ran `ls` on the fixture directory before knowing what was there and so saw the *names* of four must-not-open files. Nothing compelled that disclosure and it can only cost the author.

**Rationale:** Anchor 2: blind spots named unprompted and precisely (unknown-tenant queries, non-integer amounts, `bool` being an `int`). Anchor 3 in code as well as prose -- quota_ledger.py:58 asserts the rejection reason is one of the declared six with the message "undeclared rejection reason", so an undeclared reason fails loudly rather than being returned; and NOTES.md:104-111 refuses to assert a conflict it could not construct. Anchor 4: the voluntary leak disclosure is the unflattering result, and the admitted `1.5` defect is a second. I read the writing as good and set that aside; the assert at line 58 and the disclosure at 120-129 are what I scored.

## Verdict

_One sentence a reader can act on._

## Disclosures

_Anything you saw that you were not meant to see, anything you ran that changed the tree, and anything you REJECTED. For three rounds running the best finding in this project came from the last one, and zero came from re-running the suite._

---

## Verdict

The best oracle of the three -- an independent model re-checked against the bytes on disk after every one of 400 commands -- wrapped around a design with no port at all, so its durable side can only be swapped by rebinding a private module global.

## Total

**16 of 20.** Contested dimensions (spread > 1 between the two blind passes): **none**.

## What this judge REJECTED

See the corresponding section on this judge's card for artifact `T` -- the REJECTED and DISCLOSURES sections were returned once, covering all three artifacts, and are reproduced verbatim on each of this judge's three cards so that no card is read without them.

**I rejected scoring D1 and D4 from the packet's kill tables alone, and it changed a score.** W's and U's evidence packets are **byte-identical apart from the artifact label** -- I diffed them and the diff returned nothing but the two header lines. Eleven mutants across eleven instruments, the per-class block, the port-binding columns, the executability counts: not one cell differs between an artifact with a seam and a 400-command model oracle, and an artifact with `open()` inline in the domain and eleven tests. T differs from them in only three measured cells. Had I scored from the tables, U and W would have been indistinguishable on D1 and D4. That is why I wrote my own seven faults and ran them against each author's own suite -- which separated them immediately (W survived F4 and F5).

**I nearly gave U a D3 of 3 and backed away after running the swap.** Rebinding `quota_ledger._LedgerFile` to a memory implementation *works* -- I ran it, the ledger produced its lines and no file was created. For about a minute that looked like "an adapter could be replaced without touching the domain." I rejected it: the name I rebound lives in the domain module, is private by convention, and the constructor at line 110 chooses the implementation itself. A swap that requires monkeypatching a module's private global is not a port, and counting it would have made D3 a test of Python's mutability rather than of the design.

**I rejected the reading that would have given all three artifacts a D4 of 4** by crediting the shared harness to every artifact; and **the D2 reading that would have capped all three at 1** because no artifact measured its own complexity. All three landed at D2 = 2 and none reached 3, because not one recorded a before/after figure for any simplification -- an anchor reachable for the cost of two tool runs that nobody took.

## Disclosures

Returned once for all three artifacts and reproduced verbatim on each of this judge's cards.

**Nothing on the must-not-open list was opened.** `ls` of the repository root returned several `*EPIC*.md` filenames in the listing; I read none of them. I read only `references/eval_scorecard.md`, `examples/validation/ab/FEATURE.md`, `examples/validation/ab/tests/test_behavior.py`, and the three `blind/artifact_*/` trees.

**I did compare the artifacts.** I scored each tree sequentially -- T, then U, then W -- and did not open a later artifact's source while an earlier one was open. Two cross-artifact facts entered my reasoning afterwards: the U/W evidence-packet diff (which drove me to write my own mutants and affected W's D1 and D4), and the observation that U's write-before-memory ordering eliminates the gap T admits (which affected nothing).

**What I inferred about arms.** T is unmistakably the product of a prompt that asked for ports and adapters; W's NOTES also refers to "Section 1's instructions" with different content; U refers to no sections at all. I could not tell which arm is which treatment, and T and W sit at opposite ends of D3 despite both citing "Section 1". I did not adjust any score for arm.

**Ways this round may be fooling itself:** (1) U's and W's measured packets are byte-identical, so no port-related instrument distinguished a real port from no port except one cell; (2) the positive control is RED in all three packets and the port columns are where it fails, on 294 executed accepting Reserve cases; (3) D1 and D4 risk becoming free points that report the harness's competence as the artifact's; (4) my own seven faults are one judge's work in one sitting and I would not defend the W-versus-U gap on a wider set without re-running it.
