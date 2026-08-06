# Scorecard — ab_quota_ledger, artifact `W`, judge pass 2

`run_id`: `20260805-W-p2` · scorecard_version 1 · rubric `references/eval_scorecard.md` digest `sha256:e33638087c4191da`

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:74`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:111`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:196`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:260`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:85`
**Refuses to claim** (required and non-null for a score of 4): _(not required below 4)_

**Rationale:** Anchor 2 is satisfied by the instruments, not by the artifact's own suite: M04 dies only under the content-asserting effect provider and the shared suite (EVIDENCE.md:74). I checked whether W's own cases reach that class and they do not -- seeding a stale running total into quota_ledger.py:93 left all 11 of W's tests green, because its single durable-content test commits exactly once (test_extra.py:85-95), so the running-total column is degenerate and `COMMIT acme 5 5` is unchanged by the fault. Anchor 3 holds on the refusal class: guard_relaxation 0 of 3 for corpus-whole, 3 of 3 for corpus-neg (EVIDENCE.md:111-120). Not 4: the positive control is `green: false` with `"deciding": []` (EVIDENCE.md:196-215, 260). W does name things it cannot observe (NOTES.md:190-210), but those are spec orderings with no distinguishing input, not fault classes the cases cannot reach.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:31`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:90`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:113`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:81`
**Refuses to claim** (required and non-null for a score of 4): _(not required below 4)_

**Rationale:** Anchor 2: six attributes set up in one block (quota_ledger.py:31-37) with disciplined writers -- `_committed` only by commit (line 90), `_closed` only by close_tenant (line 113), `_available` only by reserve and release (lines 81, 101). No state is written from everywhere and nothing is over-decomposed. Against it: `_available` duplicates what `_quota`, `_outstanding` and `_committed` already determine, and quota_ledger.py:65 carries a blank-line filter the artifact itself says is unreachable (NOTES.md:179-188) -- accidental, but one predicate. Anchor 3 is unreachable for the same reason as the others: no before/after figures exist for this artifact, and I will not convert the mechanical block into one. I deliberately did not let this artifact's smaller size move this score; that is exactly the arithmetic rule 7 forbids.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:39`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:64`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:102`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/quota_ledger.py:120`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:179`
**Refuses to claim** (required and non-null for a score of 4): _(not required below 4)_

**Rationale:** A boundary is named -- `_append_line` is called "my writer" at NOTES.md:180-181 and the code comment at quota_ledger.py:102 defines release by reference to it ("no `_append_line` call here") -- and the code does not follow it. `__init__` truncates the file itself with `write_text("")` (line 42) and `ledger_lines` reads it itself with `read_text()` (line 64), so two of the three durable operations bypass the one named writer, which itself calls `open()` inline (line 120). That is anchor 1's description almost word for word. I did not score 0 because "state is written from everywhere" is factually untrue here -- the writers are disciplined. I did not score 2 because I probed for a port and there is none: the module exposes no substitutable name for the durable side, and a subclass overriding both `_append_line` and `ledger_lines` still has a real file created on disk by the constructor before any override can take effect. Rule: import topology is not modularity, and here there is not even an import boundary to mistake for one.

## D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

**Score:** **3**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:25`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:130`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:180`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/EVIDENCE.md:75`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/test_extra.py:85`
**Refuses to claim** (required and non-null for a score of 4): _(not required below 4)_

**Rationale:** Anchor 2 is met better in form than by either other artifact: NOTES.md:25-153 is a clause-by-clause account naming, for every clause of the feature, the concrete input that would have caught it being absent, and it correctly credits the shared suite where its own cases do not reach (NOTES.md:130-133). Anchor 3 is met by the generated corpus running against this artifact with 0 failures on unmutated code (EVIDENCE.md:180-187). I am stopping at 3 rather than 4, and taking the lower of two I was torn between. Anchor 4 asks that the check be *demonstrated* capable of failing, and W's own contributed check is demonstrated incapable of failing on a clause its own account enumerates: the R2 running-total clause. `test_ledger_file_on_disk_matches_ledger_lines` (test_extra.py:85-95) commits once, so I mutated quota_ledger.py:93 to print the amount instead of the running total and all 11 of W's cases stayed green. The harness caught it; the artifact's own check could not, on the one clause where it claims to check the durable artifact directly.

## D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

**Score:** **4**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:157`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:179`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:190`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_W/NOTES.md:102`
**Refuses to claim** (required and non-null for a score of 4): That the `close_tenant` rejection *order* between `unknown_tenant` and `outstanding_reservations` was verified. NOTES.md:196-201 states that no input distinguishes the two checks, that it "could not produce evidence for an ordering claim that has no distinguishing input," and that it therefore writes exactly that "instead of asserting the order was 'verified'". It separately refuses to claim its blank-line filter has ever been exercised: "I am not claiming to have observed it doing anything, only that it is there" (NOTES.md:186-188).

**Rationale:** Anchor 2: limits named unprompted throughout, including inside the clause-by-clause account itself (NOTES.md:102-113 flags its own close-order test as weaker than the reserve-order one, mid-claim). Anchor 3 is the purest instance in this round: an `unobservable` where a false clean was available and would have gone unchallenged -- the ordering test at test_extra.py:108-114 passes, and the artifact still declines to call the ordering verified. Anchor 4 needs an unflattering result and there are two: NOTES.md:179-188 admits it shipped unreachable code and did not exercise it, and NOTES.md:157-167 marks its `reservation_id`-on-commit/release reading as "unverified by any assertion, only a reading I committed to." Both are self-inflicted. I checked the substantive claims -- 28 and 11 passing, the truncation at line 42, the numeric id sort at line 58, and the assertion that an unknown tenant can never hold a reservation -- and all held. The clause-by-clause prose is the most disciplined writing of the three; I scored the refusals and the two admissions, which are checkable, not the discipline.

## Verdict

_One sentence a reader can act on._

## Disclosures

_Anything you saw that you were not meant to see, anything you ran that changed the tree, and anything you REJECTED. For three rounds running the best finding in this project came from the last one, and zero came from re-running the suite._

---

## Verdict

The most honest record in the round and the smallest code, but there is no boundary at all between the rules and the file -- truncate, read and append all happen inside the domain class, no substitution is possible -- and its own eleven tests cannot see a stale R2 running total, which I confirmed by mutating it.

## Total

**13 of 20.** Contested dimensions (spread > 1 between the two blind passes): **none**.

## What this judge REJECTED

Returned once for all three artifacts and reproduced verbatim on each of this judge's cards.

**A D4 of 4 for all three, which is where the evidence first pointed.** Every artifact's packet shows a model-derived corpus running clean on unmutated code and killing six or more seeded faults, so all three mechanically clear anchors 3 and 4. That would have made D4 a dimension that says nothing. I went looking for artifact-level discrimination and found it by mutation: T's and U's own suites both fail under a stale running total (4 of 53, 1 of 32), and W's does not -- 11 of 11 stayed green, because its only durable-content test commits exactly once. That single check moved W from 4 to 3 and is the only thing separating them on this dimension. I record that the other 4s rest on harness evidence that is near-identical across artifacts.

**A D3 of 3 for U, which I nearly gave after my own probe passed** -- rebinding `quota_ledger._LedgerFile` from outside works and passes all 28 shared cases. Rejected: the anchor's first clause fails at quota_ledger.py:10, and overwriting a module's private name is reaching into the domain rather than handing it a collaborator.

**A D3 of 0 for W.** Anchor 0 says "state is written from everywhere," and that is simply false of W -- `_committed` has one writer, `_closed` has one writer. I refused to score an anchor whose description does not fit merely because the artifact deserves the low end of the dimension.

**Counting the `corpus-port-swap:fake` column as D3 evidence for T.** T is the only artifact whose fake column diverges from its real column, which is genuine proof that a second implementation was actually bound. It was tempting. I discarded it because the positive control on all three port-binding columns SURVIVED on every artifact while executing 294 accepting Reserve cases, so those columns are red and decide nothing. I used my own swap run instead, which I could see fail.

**A reading of D5 anchor 2 that I discarded.** Read strictly, `NOTES.md` is "a report" and all three artifacts would cap at D5 = 1. I rejected the strict reading because NOTES.md ships inside each artifact tree, but the anchor is ambiguous and a second judge could reasonably land three points lower on every artifact. **This is the largest single source of possible divergence on this card.**

**A D1 of 4 for W on its named-limits prose.** W names things it could not observe more explicitly than either other artifact, which looks like anchor 4's "the record names a fault class it still cannot reach." I rejected it: what W names is a specification ordering with no distinguishing input, which is a fact about the feature, not a class of fault its cases miss.

**A check I started and abandoned.** I began comparing how the three implementations filter blanks out of `ledger_lines` -- T `if line`, U `if line.strip()`, W `if line != ""` -- so a whitespace-only line would be dropped by U and kept by the others. I abandoned it: nothing in any of the three ever writes such a line and FEATURE.md does not specify it.

## Disclosures

Returned once for all three artifacts and reproduced verbatim on each of this judge's cards.

**Nothing on the must-not-open list was opened.** One partial exposure: my first command included `ls -la` of the repository root, which printed the *names* of several `*EPIC*.md` files and a `prompts/` directory. I opened none of them and saw no contents.

**I did compare artifacts, and it was partly unavoidable.** Every artifact's `EVIDENCE.md` carries all three artifacts' mechanical figures. I formed each score while on that artifact's tree but read all three in one session, and used cross-artifact comparison deliberately in the D4 discrimination and the verdicts.

**Blinding leaked, through the NOTES.** T's NOTES quotes its own prompt and calls it "the architecture ask"; W's refers to "Section 1's instructions" with entirely different content and to "Section 6's forbidden list"; U's refers to no sections at all. I formed that inference before finishing T's D3. I do not believe it changed a score, but a judge who wanted to flatter the treatment arm would have known exactly which one it was. **The instruction to read NOTES.md in full is in tension with the instruction to be blind to arm.**

**Three ways this round may be fooling itself:** (1) the port-related columns are precisely the dead ones -- the positive control SURVIVED on all of them on every artifact while executing 294 accepting Reserve cases; (2) U's and W's kill tables are byte-identical across 11 mutants x 11 columns while T differs in three cells, so ninety-nine cells separate three artifacts by three; (3) D2's top half is unreachable by construction, so D2 contributed nothing to this comparison and will contribute nothing to the next under the same task design.
