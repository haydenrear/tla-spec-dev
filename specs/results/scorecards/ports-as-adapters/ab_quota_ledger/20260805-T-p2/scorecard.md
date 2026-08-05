# Scorecard — ab_quota_ledger, artifact `T`, judge pass 2

`run_id`: `20260805-T-p2` · scorecard_version 1 · rubric `references/eval_scorecard.md` digest `sha256:e33638087c4191da`

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:71`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:74`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:111`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:196`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:263`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:124`
**Refuses to claim** (required and non-null for a score of 4): _(not required below 4)_

**Rationale:** Anchor 2 is met on content, not shape: M04-durable-stale-total SURVIVES the silent effect provider and is KILLED by the checking one (EVIDENCE.md:74), and I reproduced a content kill myself by rewriting the running-total f-string in domain.py:159 -- four of T's own cases failed, on both wirings. Anchor 3 is met by the refusal class: corpus-whole scores 0 of 3 on guard_relaxation while corpus-neg scores 3 of 3 (EVIDENCE.md:111-120), so a class the whole-view corpus structurally cannot reach is caught. I am not scoring 4. The declared positive control M07 is `green: false` with `"deciding": []` (EVIDENCE.md:196-218, 263), so every SURVIVED cell on this artifact is a floor rather than a measurement; and the one unreachable-class statement in T's own packet -- the LEDGER slice cannot see M07 -- was rejected by the run's own evidence (EVIDENCE.md:265-276), so anchor 4's "the record names a fault class it still cannot reach" has no surviving instance.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:106`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:118`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:151`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:172`
**Refuses to claim** (required and non-null for a score of 4): _(not required below 4)_

**Rationale:** Anchor 2: the state is six attributes set up in one place (domain.py:106-114) and each has a single meaning-bearing writer -- `_committed` only by commit (domain.py:158), `_closed` only by close_tenant (domain.py:180), `_issued` only by an accepted reserve (domain.py:146). `available` is not stored at all but derived (domain.py:118-120), so R1 has no maintenance burden and nothing is written from everywhere. Anchor 3 requires "a simplification was made and its effect measured -- the before and after figures are both recorded," and no before figure for this artifact exists anywhere: NOTES.md:70-84 argues the derivation but records no measurement of it. The mechanical block is a cross-artifact table, not a before/after, and rule 7 forbids me converting it, so 3 is unreachable here.

## D3 — modularity

*Is it ports and adapters in fact — domain independent of I/O, adapters swappable?*

- **0** — No boundary is discernible; state is written from everywhere.
- **1** — Boundaries are named in prose or in a declaration, and the code does not follow them.
- **2** — The code follows the declared boundaries. Cross-boundary calls go through something identifiable as a port.
- **3** — The domain does not import its I/O. An adapter could be replaced without touching the domain, and the judge names the specific swap.
- **4** — 3, **and** a driven port is exercised by a real adapter *and* a fake, with the same cases passing against both.

> **Import topology is not modularity.** Round 2 proved a codebase can pass every import check with its coupling entirely intact. A D3 of 3 or more requires evidence about what *calls* what at runtime, not what imports what.

**Score:** **4**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:13`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:22`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/domain.py:132`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/__init__.py:39`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/quota_ledger/memory_journal.py:14`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:26`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:260`
**Refuses to claim** (required and non-null for a score of 4): T refuses to claim the port buys it durability. NOTES.md:136-141 states that commit and close_tenant update memory and then append, so a failed append leaves memory ahead of the journal, and names this as "the one place I can name where R2 is not enforced by construction" -- it declines to build or claim a rollback. It also refuses to indirect anything else: NOTES.md:52-56 states there is no port in front of the arithmetic, no repository interface over the reservations dict, and no service layer.

**Rationale:** Anchor 3's specific swap is `FileJournal(ledger_path)` -> `InMemoryJournal()` at __init__.py:39, and the domain genuinely does not import its I/O -- domain.py:13-16 imports only `__future__`, `dataclasses`, `typing`, which test_ledger.py:260-270 asserts by parsing the AST rather than by assertion in prose. Anchor 4 needs runtime evidence, not import topology, so I ran it: the parametrized fixture at test_ledger.py:26-36 runs 16 [file] and 16 [memory] variants of one case list and all 53 pass, and separately I wrote a shim outside the repository that constructs `Ledger(quotas, InMemoryJournal())` and ran the entire unmodified shared suite through it -- 28 passed, with not one byte of the domain edited. That is a driven port exercised by a real adapter and a fake with the same cases passing against both. I withheld the `corpus-port-swap:fake` column as supporting evidence; see WHAT I REJECTED.

## D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

**Score:** **4**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:62`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:180`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/EVIDENCE.md:75`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:202`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:68`
**Refuses to claim** (required and non-null for a score of 4): That behavior is preserved under a durable-write failure. NOTES.md:136-141 declines to claim any atomicity or ordering guarantee between the memory update and the append, and NOTES.md:142-145 declines to claim a non-integer amount is rejected -- it says such an amount "would flow into the ledger line" and that adding a check would need a seventh rejection reason the vocabulary does not have.

**Rationale:** Anchor 2: the behaviors are enumerated -- NOTES.md:68-100 walks the derived `available`, the id counter, and the ordering guarantee, and tests/test_ledger.py:202-226 reads R1, R2, R3 and R5 off one concrete expected transcript with literal values rather than self-consistency. Anchor 3: a model-derived check, not only hand-written assertions -- the generated corpus ran against this artifact with 0 failures on unmutated code across every instrument (EVIDENCE.md:180-187), on a corpus whose sha1 is shared with the other artifacts (EVIDENCE.md:190). Anchor 4: the check is demonstrated capable of failing -- corpus-whole KILLED six of the eleven seeded faults (EVIDENCE.md:75-80), and I confirmed the artifact's own suite is capable of failing too by seeding a stale running total into domain.py:159, which broke 4 of 53 cases across both wirings. I nearly took 3 here; see WHAT I REJECTED.

## D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

**Score:** **4**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:136`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:142`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:118`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/NOTES.md:149`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_T/tests/test_ledger.py:260`
**Refuses to claim** (required and non-null for a score of 4): That "the domain does not import its I/O" is true on the strength of the author's word. NOTES.md:49-51 says the claim is "about the file rather than about intent" and converts it into an executed AST check (tests/test_ledger.py:260-270) instead of asserting it. It also refuses to claim R2 holds through a failed append (NOTES.md:136-141) and refuses to claim integer amounts are enforced (NOTES.md:142-145).

**Rationale:** Anchor 2: the limits are named unprompted in the shipped record -- four interpretations it picked and could not verify (NOTES.md:125-147), plus the disclosure at NOTES.md:149-157 that it declined to open a file (`examples/validation/ab/README.md`) that was not even on its forbidden list. Anchor 3: rather than certify the boundary, it converts the claim into a check that could fail. Anchor 4 needs an unflattering result and there are two: NOTES.md:136-141 concedes a hole in R2 under write failure, and NOTES.md:118-123 concedes that its `QuotaLedger` factory-named-like-a-class "is slightly unusual to read." Both are volunteered and neither is required by the feature. The writing here is polished and did tempt me; I scored the four interpretations and the disclosure, which are checkable, and not the prose.

## Verdict

_One sentence a reader can act on._

## Disclosures

_Anything you saw that you were not meant to see, anything you ran that changed the tree, and anything you REJECTED. For three rounds running the best finding in this project came from the last one, and zero came from re-running the suite._

---

## Verdict

Ship it -- the port is real and I proved it by running the whole unmodified shared suite against the in-memory adapter with the domain untouched -- but treat every SURVIVED cell in its packet as a floor, because the run's positive control decided nothing on this artifact.

## Total

**17 of 20.** Contested dimensions (spread > 1 between the two blind passes): **none**.

## What this judge REJECTED

Returned once for all three artifacts and reproduced verbatim on each of this judge's cards.

**A D4 of 4 for all three, which is where the evidence first pointed.** Every artifact's packet shows a model-derived corpus running clean on unmutated code and killing six or more seeded faults, so all three mechanically clear anchors 3 and 4. That would have made D4 a dimension that says nothing. I went looking for artifact-level discrimination and found it by mutation: T's and U's own suites both fail under a stale running total (4 of 53, 1 of 32), and W's does not -- 11 of 11 stayed green, because its only durable-content test commits exactly once. That single check moved W from 4 to 3 and is the only thing separating them on this dimension. I record that the other 4s rest on harness evidence that is near-identical across artifacts.

**A D3 of 3 for U, which I nearly gave after my own probe passed.** I rebound `quota_ledger._LedgerFile` to an in-memory stand-in from a shim outside the repository and all 28 shared cases passed -- a working substitution with no edit to the file. I rejected it as anchor-3 evidence on two grounds: the anchor's first clause ("the domain does not import its I/O") fails outright at quota_ledger.py:10, and overwriting a module's private name from outside is reaching into the domain rather than handing it a collaborator. There is no declared contract the substitute must satisfy, so nothing would tell a second implementer they had got it wrong. I have recorded the probe because the next judge deserves to know the substitution works.

**A D3 of 0 for W.** Anchor 0 says "state is written from everywhere," and that is simply false of W -- `_committed` has one writer, `_closed` has one writer. I refused to score an anchor whose description does not fit merely because the artifact deserves the low end of the dimension.

**Counting the `corpus-port-swap:fake` column as D3 evidence for T.** T is the only artifact whose fake column diverges from its real column (M09 KILLED real, SURVIVED fake -- artifact_T/EVIDENCE.md:168), which is genuine proof that a second implementation was actually bound. It was tempting. I discarded it because the positive control on all three port-binding columns SURVIVED on every artifact while executing 294 accepting Reserve cases (artifact_T/EVIDENCE.md:282-316), so those columns are red and decide nothing. I used my own swap run instead, which I could see fail.

**A reading of D5 anchor 2 that I discarded.** The anchor says limits must be named "in the artifact itself and not only in a report." Read strictly, `NOTES.md` is a report, and under that reading all three artifacts cap at D5 = 1, because none of them annotates a blind spot in the source -- W's unreachable filter at quota_ledger.py:65 carries no comment saying so, and U's and T's code comments state rationale, not limits. I rejected the strict reading because NOTES.md ships inside each artifact tree and is the deliverable's own documentation, not correspondence with a judge. But the anchor is ambiguous and a second judge could reasonably land three points lower on every artifact. This is the largest single source of possible divergence on this card.

**Using the mechanical block to separate the artifacts on D2.** W is a third of T's code lines and it would have been easy to let that do the work. Rule 7 forbids it and I judged structure instead: all three landed at 2, and all three are pinned there by the same thing -- anchor 3 needs a before *and* an after, and a from-scratch implementation has no before.

**A D1 of 4 for W on its named-limits prose.** W names things it could not observe more explicitly than either other artifact (NOTES.md:190-210), which looks like anchor 4's "the record names a fault class it still cannot reach." I rejected it: what W names is a specification ordering with no distinguishing input, which is a fact about the feature, not a class of fault its cases miss. And the positive control is red on all three artifacts, which is reason enough to keep every D1 off the top of the scale.

**A check I started and abandoned.** I began comparing how the three implementations filter blanks out of `ledger_lines` -- T uses `if line` (file_journal.py:35), U uses `if line.strip()` (quota_ledger.py:92), W uses `if line != ""` (quota_ledger.py:65) -- so a whitespace-only line would be dropped by U and kept by T and W. I abandoned it: nothing in any of the three ever writes such a line, W says so explicitly, and FEATURE.md does not specify it. Scoring it would have been scoring a difference the specification calls free.

## Disclosures

Returned once for all three artifacts and reproduced verbatim on each of this judge's cards.

**Nothing on the must-not-open list was opened.** I read `references/eval_scorecard.md`, `examples/validation/ab/FEATURE.md`, `examples/validation/ab/tests/test_behavior.py`, and the three `blind/artifact_*/` trees. One partial exposure to disclose: my first command included `ls -la` of the repository root, which printed the *names* of `PORTS-AS-ADAPTERS-EPIC.md`, `NEXT-EPIC.md`, `ARCHITECTURAL-COHERENCE-EPIC.md`, `COMPLEXITY-DESCRIPTOR-EPIC.md`, `EFFECT-PROVIDER-EPIC.md`, `EPIC-HANDOFF.md`, `PORTS-AS-ADAPTERS-STARTER-PROMPT.md` and a `prompts/` directory. I opened none of them and saw no contents.

**I did compare artifacts, and it was partly unavoidable.** Every artifact's `EVIDENCE.md` contains a MECHANICAL BLOCK carrying all three artifacts' figures, so I could not read one packet without seeing all three columns; I did not convert any of it into a score. I formed each score while on that artifact's tree, but I read all three trees in one session and I used cross-artifact comparison deliberately in two places: the D4 discrimination (W's own suite versus T's and U's under the same mutation) and the verdicts. Judges who read this card should treat T's D3 = 4 and W's D3 = 1 as independently grounded -- each rests on a probe I ran against that artifact alone.

**Blinding leaked, through the NOTES.** T's `NOTES.md:102-116` quotes its own prompt -- "Section 1: the domain holds 'no file handle, no path'" -- and calls it "the architecture ask." W's `NOTES.md:202` refers to "Section 1's instructions" with entirely different content ("behavior vs. what-to-show") and to "Section 6's forbidden list." U's NOTES refers to no sections at all. So I could infer that T received an explicit ports-and-adapters instruction and that at least two artifacts came from sectioned prompts of different content. I formed that inference before finishing T's D3. I do not believe it changed a score -- T's D3 = 4 rests on a swap I executed and W's D3 = 1 on a probe that returned "no seam exists" -- but a judge who wanted to flatter the treatment arm would have known exactly which one it was. **The instruction to read NOTES.md in full is in tension with the instruction to be blind to arm.**

**Three ways I think this round may be fooling itself.**

1. *The columns that would show the effect are the dead ones.* `corpus-port` and all three port-binding columns are precisely the instruments that would demonstrate a declared port paying off, and the positive control SURVIVED on every one of them, on all three artifacts, while executing 294 accepting Reserve cases. T has a real, swappable port and `corpus-port` still let M07 through. Whatever those columns measure, it is not port reach.

2. *U's and W's kill tables are byte-identical.* I diffed them: across 11 mutants x 11 columns, every verdict, every per-class count and every control field matches; the only textual difference in the two files is the label on the mechanical block's column header. Two materially different implementations -- one with a file-owning class, one with `open()` inline in the domain -- produced not one differing cell. T differs from them in three cells total (M07/corpus-neg, M07/corpus-slice-led, M09/`corpus-port-swap:fake`). An 11x11 apparatus that separates three artifacts by three cells is either measuring something the artifacts do not vary in, or it is not measuring.

3. *D2's top half is unreachable by construction.* Anchor 3 requires a simplification whose before and after were both measured, and this eval asks for from-scratch implementations of one spec. No artifact can have a before. Every artifact in this round is pinned at D2 = 2 regardless of what it did, so D2 contributed nothing to the comparison and will contribute nothing to the next one under the same task design.
