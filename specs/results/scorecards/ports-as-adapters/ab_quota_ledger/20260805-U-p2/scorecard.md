# Scorecard — ab_quota_ledger, artifact `U`, judge pass 2

`run_id`: `20260805-U-p2` · scorecard_version 1 · rubric `references/eval_scorecard.md` digest `sha256:e33638087c4191da`

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

**Score:** **3**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:74`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:111`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:196`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:260`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:85`
**Refuses to claim** (required and non-null for a score of 4): _(not required below 4)_

**Rationale:** Anchor 2 holds on content: M04 is invisible to every instrument except the content-asserting effect provider and the shared suite (EVIDENCE.md:74), and I confirmed U's own oracle sees it too -- seeding a stale running total into quota_ledger.py:168 broke `test_commit_lines_reach_the_file_itself`, which reads the bytes off disk (test_quota_ledger.py:85-88). Anchor 3 holds on the refusal class: guard_relaxation is 0 of 3 for corpus-whole and 3 of 3 for corpus-neg (EVIDENCE.md:111-120). Not 4: the positive control is `green: false` with `"deciding": []` (EVIDENCE.md:196-215, 260), and corpus-port let M07 survive while executing 294 accepting Reserve cases (EVIDENCE.md:280-290), so the zeros are floors. U's record names spec ambiguities it did not resolve, but no fault class its cases cannot reach.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:103`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:150`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:170`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:194`
**Refuses to claim** (required and non-null for a score of 4): _(not required below 4)_

**Rationale:** Anchor 2: six attributes initialized in one place (quota_ledger.py:103-110), and no god-state -- `_committed` is written only by commit (line 170), `_closed` only by close_tenant (line 194), `_available` only by reserve and release (lines 150, 180). `_available` is stored rather than derived, which means R1 is maintained by hand across two writers instead of holding by construction, and `_Reservation.seq` duplicates the numeric part of the id it already carries (quota_ledger.py:66-69) so that `outstanding_ids` can sort by it (line 129) when insertion order already gives the answer. That is mild accidental structure, not disproportion, so anchor 2 still holds. Anchor 3 is unreachable: no before/after figures for this artifact exist, and the mechanical block is a cross-artifact table I am forbidden to convert.

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

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:10`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:72`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:110`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:134`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:168`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/quota_ledger.py:193`
**Refuses to claim** (required and non-null for a score of 4): _(not required below 4)_

**Rationale:** Anchor 2 is met and I checked it rather than took it: the boundary U declares is "one small class that writes it" (NOTES.md:117), and the code follows -- `QuotaLedger` never touches a path or a file handle, and every durable access goes through `_LedgerFile.append`/`.lines` (quota_ledger.py:134, 168, 193). Anchor 3 fails on its first clause: the domain class and its I/O are the same module, and that module imports `pathlib.Path` at line 10; the domain constructs `_LedgerFile(ledger_path)` directly at line 110 with no injection point, so an adapter cannot be replaced without touching the domain. I ran the swap anyway to be fair to it: rebinding the private module global `quota_ledger._LedgerFile` to an in-memory stand-in from outside does pass all 28 shared cases. I am not counting that as anchor 3 -- reaching into a module to overwrite one of its private names is touching the domain, not passing it a collaborator, and there is no declared contract for the substitute to satisfy.

## D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

**Score:** **4**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:279`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/test_quota_ledger.py:315`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:180`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/EVIDENCE.md:75`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:48`
**Refuses to claim** (required and non-null for a score of 4): Crash safety. NOTES.md:56-63 orders the durable write before the in-memory update and then explicitly declines the credit -- "it is not a crash-safety feature and I did not build one (no fsync, no journaling, no recovery; that is out of scope)". It also refuses to claim integer amounts are enforced and names the consequence precisely: `1.5` would be held, committed, and printed into a COMMIT line (NOTES.md:96-103).

**Rationale:** Anchor 2: the behaviors are enumerated decision by decision (NOTES.md:48-86) and pinned by 32 cases. Anchor 3 is met twice over -- the shared generated corpus ran against this artifact with 0 failures on unmutated code (EVIDENCE.md:180-187), and the artifact ships its own model-derived check: `check_rules` (test_quota_ledger.py:279-312) recomputes R1, R2 and R3 from an independently maintained model against the bytes on disk after every one of 400 randomized commands (test_quota_ledger.py:315-362), which is not a hand-written assertion about a fixed transcript. Anchor 4: caught, and demonstrated by me rather than assumed -- relaxing the `amount < 1` guard at quota_ledger.py:144 made that sweep fail, and corpus-whole independently KILLED six seeded faults (EVIDENCE.md:75-80).

## D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

**Score:** **4**

**Citations** (`file:line`; required for any score ≥ 2, and a score ≥ 2 without one is capped at 1 by the schema check):

- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:56`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:89`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:96`
- `specs/results/scorecards/ports-as-adapters/blind/artifact_U/NOTES.md:125`
**Refuses to claim** (required and non-null for a score of 4): That ordering the durable write first is a durability guarantee (NOTES.md:56-63), and that a non-integer amount is rejected -- it states the rule as written and says "If integrality is meant to be enforced, the six-reason vocabulary is missing a reason for it" (NOTES.md:96-103), turning its own gap into a finding about the specification rather than a silent choice.

**Rationale:** Anchor 2: limits named unprompted -- the KeyError on an unknown-tenant query, described as "the one place I am aware of where a reasonable implementer could differ from me" (NOTES.md:89-94), the non-integer amount, and `bool` being an `int` (NOTES.md:105-106). Anchor 3: it declines the positive verdict that the code's shape invites. Writing the durable append before the memory update looks exactly like crash safety and it refuses to call it that. Anchor 4 needs an unflattering result and U volunteers the most costly one in the round: NOTES.md:125-129 discloses that it ran `ls` on the fixture directory and saw the *names* of four must-not-open files before it knew what they were. Nothing compelled that disclosure and it can only damage the artifact's own blindness claim, which is what anchor 4 is for. I verified the claims that were checkable -- 28 and 32 passing, the write ordering at lines 168 and 193, the quotas copy at line 104 -- and all held.

## Verdict

_One sentence a reader can act on._

## Disclosures

_Anything you saw that you were not meant to see, anything you ran that changed the tree, and anything you REJECTED. For three rounds running the best finding in this project came from the last one, and zero came from re-running the suite._

---

## Verdict

A correct single-module implementation with the strongest self-owned oracle of the three -- a 400-step randomized sweep that recomputes R1/R2/R3 from disk after every command -- but its durable side is constructed inside the domain, so swapping it means editing the domain or monkeypatching a private global, and that is a seam, not a port.

## Total

**15 of 20.** Contested dimensions (spread > 1 between the two blind passes): **none**.

## What this judge REJECTED

Returned once for all three artifacts and reproduced verbatim on each of this judge's cards.

**A D4 of 4 for all three, which is where the evidence first pointed.** Every artifact's packet shows a model-derived corpus running clean on unmutated code and killing six or more seeded faults, so all three mechanically clear anchors 3 and 4. That would have made D4 a dimension that says nothing. I went looking for artifact-level discrimination and found it by mutation: T's and U's own suites both fail under a stale running total (4 of 53, 1 of 32), and W's does not -- 11 of 11 stayed green.

**A D3 of 3 for U, which I nearly gave after my own probe passed.** I rebound `quota_ledger._LedgerFile` to an in-memory stand-in from a shim outside the repository and all 28 shared cases passed -- a working substitution with no edit to the file. I rejected it as anchor-3 evidence on two grounds: the anchor's first clause ("the domain does not import its I/O") fails outright at quota_ledger.py:10, and overwriting a module's private name from outside is reaching into the domain rather than handing it a collaborator. There is no declared contract the substitute must satisfy, so nothing would tell a second implementer they had got it wrong. I have recorded the probe because the next judge deserves to know the substitution works.

**A reading of D5 anchor 2 that I discarded.** The anchor says limits must be named "in the artifact itself and not only in a report." Read strictly, `NOTES.md` is a report, and under that reading all three artifacts cap at D5 = 1. I rejected the strict reading because NOTES.md ships inside each artifact tree. But the anchor is ambiguous and a second judge could reasonably land three points lower on every artifact. **This is the largest single source of possible divergence on this card.**

**Using the mechanical block to separate the artifacts on D2.** W is a third of T's code lines and it would have been easy to let that do the work. Rule 7 forbids it and I judged structure instead: all three landed at 2, pinned by anchor 3 needing a before *and* an after that a from-scratch implementation cannot have.

## Disclosures

Returned once for all three artifacts and reproduced verbatim on each of this judge's cards.

**Nothing on the must-not-open list was opened.** One partial exposure: my first command included `ls -la` of the repository root, which printed the *names* of several `*EPIC*.md` files and a `prompts/` directory. I opened none of them and saw no contents.

**I did compare artifacts, and it was partly unavoidable.** Every artifact's `EVIDENCE.md` carries all three artifacts' mechanical figures, so I could not read one packet without seeing all three columns; I did not convert any of it into a score. I used cross-artifact comparison deliberately in the D4 discrimination and in the verdicts.

**Blinding leaked, through the NOTES.** T's NOTES quotes its own prompt and calls it "the architecture ask"; W's refers to "Section 1's instructions" with entirely different content; U's refers to no sections at all. I formed that inference before finishing T's D3. I do not believe it changed a score -- T's D3 = 4 rests on a swap I executed and W's D3 = 1 on a probe that returned "no seam exists" -- but a judge who wanted to flatter the treatment arm would have known exactly which one it was. **The instruction to read NOTES.md in full is in tension with the instruction to be blind to arm.**

**Three ways this round may be fooling itself:** (1) the columns that would show a port paying off are the dead ones -- the positive control SURVIVED on every port-binding column of every artifact while executing 294 accepting Reserve cases; (2) U's and W's kill tables are byte-identical across 11 mutants x 11 columns, and T differs from them in three cells total, so an apparatus of ninety-nine cells separates three artifacts by three; (3) D2's top half is unreachable by construction, because anchor 3 needs a before/after and this eval asks for from-scratch implementations, so D2 contributed nothing and will contribute nothing under the same task design.
