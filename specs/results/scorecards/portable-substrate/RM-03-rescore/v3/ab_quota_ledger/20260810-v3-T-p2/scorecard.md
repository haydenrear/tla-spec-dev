# Scorecard — ab_quota_ledger, artifact `T`, judge pass 2

`run_id`: `20260810-v3-T-p2` · scorecard_version 3 · rubric `examples/validation/scorecards/rubric_v3_frozen.md` digest `sha256:546f90e21d1254e0` · served `sha256:e1cab7c513e9d6dd`

**You are scoring artifact `T`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

Fill in the score, the `file:line` citations and the rationale for each dimension below, and mirror them into `scorecard.json` beside this file. **The anchors are reproduced here so the bar for a score sits in the same file as the score.**

## The mechanical block

`mechanical.json` beside this file holds kill counts, complexity figures, case counts, determinism and runtime. How to read it against your judgement is one of the numbered scoring rules below.

## The rubric you are scoring against

**This is the whole rubric, and it is reproduced here so the bar for a score sits in the same file as the score.** Do NOT go and read `references/eval_scorecard.md`. That file also carries reading rules and prior results about these same dimensions, and a judge who reads those is being handed conclusions about the instrument they are the instrument for.

### The scoring rules

1. **Score artifacts, never claims.** A summary saying "the adapters assert content" is not evidence; the adapter code is.
2. **Every score ≥ 2 cites `file:line`.** A score with no citation is capped at 1, mechanically, by the schema check.
3. **Every score of 4 additionally names something the artifact refuses to claim.** The top of every scale requires a stated limit. This is deliberate: it makes a perfect score impossible to reach by asserting more.
4. **Prose quality is never an input.** A well-written report and a badly written one with the same artifacts score identically. Say so in the rationale if the writing tempted you.
5. **Two judges, independently, blind to each other.** Any dimension where they differ by more than 1 is recorded as `contested` and adjudicated by a third pass that must cite new evidence, not re-read the same lines.
6. **Blind to arm.** Where an eval has arms (with-prompt vs without), judges do not learn which artifact came from which until after scoring.
7. **The mechanical block is recorded, never scored.** Kill counts, complexity figures, case counts, determinism, runtime. It sits beside the judgement so a reader can see when the two disagree — and a disagreement is a finding.
8. **Say what you ran.** *(New in version 2.)* Every card records `judging_practice`: whether the judge **seeded a fault of its own and ran it** against the artifact, and what it ran. Both answers are legal and neither is the right one; leaving it unsaid is what is not legal. **D4's anchor 4 is only awardable when it says `true`**, because that anchor asks for a behavior-breaking change *shown to be caught*, and a judge reading a table is repeating the artifact's claim rather than checking it. This is the anchor's own text made checkable, not a new bar.
9. **A judge is served the card, never the rubric file.** *(New in version 3.)* The scaffolded `scorecard.md` carries the rubric a judge needs. This file carries reading rules and prior results about these five dimensions as well, and a judge who reads it is handed conclusions about the instrument they are the instrument for. Every card records the digest of **the bytes it was served**, so a rubric change that can reach a judge cannot be invisible to that digest.

**Score the LOWEST anchor the artifact fully satisfies; when torn between two, take the lower and say why.**

### Judging practice — REQUIRED, and it is a field on the card

**Did you seed a fault of your own and run it against this artifact, or did you score the evidence packet?** Both are legal. Neither is the right answer. What is not legal is leaving it unsaid.

Fill `judging_practice` in `scorecard.json`: `executed_own_faults` true or false, and `what_was_run` listing what you actually ran.

**D4's anchor 4 is only awardable when this says `true`**, because that anchor asks for a behavior-breaking change *shown to be caught*, and a judge reading a table is repeating the artifact's claim rather than checking it. If you did not run one, the highest D4 you can support is 3 — say that the packet asserts it and you did not verify it.

### D1 — bug detection

*Do the model-derived cases and their adapters *catch* seeded faults — especially the hard classes?*

- **0** — Cases exist and pass; no seeded fault is caught. A suite that is green on broken code.
- **1** — Catches faults that change a value the projection already prints. Misses everything requiring a content assertion.
- **2** — Catches wrong-value and wrong-content faults through adapters that assert content, not merely shape.
- **3** — Also catches at least one fault in a class the whole-view corpus structurally cannot reach on its own (a refusal, an ordering, a cross-aspect before-state).
- **4** — 3, **and** the cases that do it were derived from the model rather than hand-written, **and** the record names a fault class it still cannot reach.

### D2 — complexity

*Is the design as simple as its behavior requires, and no simpler?*

Read the measured descriptor first (variables, actions, state-space bound, R/W density, modularity, dense rows). Then judge whether the numbers reflect essential behavior or accidental structure.

- **0** — Complexity is unmeasured, or measured and ignored.
- **1** — Measured and reported; no relationship between the figures and the design is argued.
- **2** — The design's complexity is proportional to its behavior; no god-state, no variable written from everywhere.
- **3** — 2, **and** a simplification was made and its effect measured — the before and after figures are both recorded.
- **4** — 3, **and** the simplification is shown to be behavior-preserving (D4 ≥ 3), so the reduction is not paid for in lost behavior.

> **A drop in a complexity number is not evidence on its own.** MF-020: a metric can improve because an edge was deleted. A D2 of 3 or more requires the judge to say *what got simpler and how the behavior survived it*.

### D3 — modularity

*Is it ports and adapters in fact — domain independent of I/O, adapters swappable?*

- **0** — No boundary is discernible; state is written from everywhere.
- **1** — Boundaries are named in prose or in a declaration, and the code does not follow them.
- **2** — The code follows the declared boundaries. Cross-boundary calls go through something identifiable as a port.
- **3** — The domain does not import its I/O. An adapter could be replaced without touching the domain, and the judge names the specific swap.
- **4** — 3, **and** a driven port is exercised by a real adapter *and* a fake, with the same cases passing against both.

> **Import topology is not modularity.** Round 2 proved a codebase can pass every import check with its coupling entirely intact. A D3 of 3 or more requires evidence about what *calls* what at runtime, not what imports what.

### D4 — behavior preservation

*Does the simpler design still do everything the baseline did?*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant) rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be *caught* — the check is demonstrated to be capable of failing.

### D5 — honesty

*Does the artifact refuse rather than falsely certify, and name what it cannot see?*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is unflattering to the thing being scored.

> **Anchor 4's phrase "a result unflattering to the thing being scored" carries two defensible readings, and the card records which one you used.** Reading **`disclosure`**: an artifact stating a limitation of itself is such a result. Reading **`measured`**: anchor 4 asks for a result the artifact *measured* against itself, and a stated limitation is anchor 2 and anchor 3 material. **Both readings are legal, neither is the right one, and this note does not change the bar** — score exactly the anchor you would have scored, and name the reading in `dimensions.D5.anchor_reading`. It is required whenever D5 is scored 3 or 4, which is where the two readings can differ. Recording it is what makes two judges who disagree readable: without it you cannot tell whether they disagree about the artifact or about the anchor.

### Judging practice — your answer

**Executed own faults:** true

**What was run:**

- Ran the unmutated baselines first: `tests/test_ledger.py` (53 passed) and the shared `examples/validation/ab/tests/test_behavior.py` against this artifact via `QUOTA_LEDGER_DIR`/`QUOTA_LEDGER_IMPL` (28 passed) — reproducing NOTES.md's claimed counts rather than trusting them.
- In a scratch copy, seeded a guard-relaxation fault (`domain.py` `reserve()`: `amount < 1` → `amount < 0`, admitting a zero-amount reservation) — caught by both the artifact's own suite (4 failures) and the shared suite (2 failures), then reverted.
- In the same scratch copy, seeded a durable-content/stale-total fault (`commit()`: wrote `f"COMMIT {tenant} {amount} {amount}"` instead of the running total) — caught by both suites (4 and 2 failures respectively), then reverted.
- Did not run the shared model-derived corpus (`corpus-whole`/`corpus-neg`/etc.) myself — `cases.py` is outside this artifact's declared scope — so EVIDENCE.md's kill table for those instruments is relied on as measured, control-audited packet evidence, not independently reproduced.

## Your scores

### D1 — bug detection

**Score:** 4

**Citations** (`file:line` — the bar is in the scoring rules above):

- `quota_ledger/domain.py:136-149`
- `tests/test_ledger.py:161-199`
- `tests/test_ledger.py:108-131`
- `EVIDENCE.md:71-73`
- `EVIDENCE.md:111-120`
- `EVIDENCE.md:262-277`

**Refuses to claim** (required and non-null for a score of 4): The record (`EVIDENCE.md:262-277`) names, per-instrument, the fault classes the model-derived refusal corpus cannot reach — cross_aspect, durable_content and ordering — and gives a structural reason (no `Reserve` edge in scope) rather than asserting general coverage.

**Rationale:** Anchor 2: the artifact's own suite makes literal content assertions, not shape checks — `tests/test_ledger.py:108-131` asserts `ledger.ledger_lines() == ["COMMIT acme 3 3"]`. I independently seeded a stale-total fault (writing `f"COMMIT {tenant} {amount} {amount}"` instead of the running total, in a scratch copy) and it was killed by both this artifact's own suite and the shared suite — a wrong-value/wrong-content catch, verified by running it, not by reading a claim. Anchor 3: the guard-relaxation class (M01-M03, a refusal class) SURVIVED under `corpus-whole` (`EVIDENCE.md:71-73`, 0 of 3 in the per-class table at `EVIDENCE.md:111-120`) because that instrument only replays enabled/accepted edges and structurally never exercises a rejection — exactly the class the anchor names — yet `corpus-neg`, `corpus-port` and `suite` all killed all 3. I reproduced this myself: relaxing `domain.py:141` from `amount < 1` to `amount < 0` (a zero-amount reservation admitted) was caught by this artifact's own suite and the shared suite. Anchor 4: `corpus-neg`/`corpus-port`, the instruments that make the anchor-3 catch, are model-derived (generated from one shared model/manifest, not hand-written), and the record explicitly names what they still cannot reach: `EVIDENCE.md:262-277` gives corpus-neg 0 of 1 on cross_aspect, 0 of 2 on durable_content, 0 of 2 on ordering, with a structural reason for the related corpus-slice-led gap. I trust EVIDENCE.md's kill table as measured, control-audited evidence (it ships its own executability and control-status accounting, e.g. flagging its own M07 positive control as `green: false`) rather than a narrative claim, but I did not personally regenerate the shared corpus — the anchor-3/4 catch of the refusal class I reproduced directly with my own fault; the exhaustive per-class gap accounting I am taking from the packet's measured table.

### D2 — complexity

**Score:** 2

**Citations** (`file:line` — the bar is in the scoring rules above):

- `quota_ledger/domain.py:87-104`
- `quota_ledger/domain.py:106-114`
- `quota_ledger/file_journal.py:13-35`
- `EVIDENCE.md:324-342`

**Refuses to claim** (required and non-null for a score of 4): n/a (score is 2, not required).

**Rationale:** Artifact T is the largest of the three arms by every raw figure (`EVIDENCE.md:324-342`: 4 modules vs 1, 202 lines vs 151/78, 6 classes vs 4/2), which on its own would look like accidental structure. But the mechanical descriptor also shows where that mass sits: `instance_state_in_effectful_modules` is 1 for T versus 8 for both other arms, and `branch_points_in_effectful_modules` is 1 versus 10 and 10 — meaning T's guard logic and state stay in the pure domain and only the file-path/encoding/newline concern lives in the one effectful module (`quota_ledger/file_journal.py:13-35`). `domain.py:87-104`'s docstring and the `__init__` at 106-114 show exactly three written state pieces, each named to one writer, with `available` derived rather than stored. The one added interface (the `Journal` Protocol, 2 methods) exists for the one real external dependency, and NOTES.md declines every other opportunity to indirect. That supports anchor 2 (proportional to behavior, no god-state). I did not find anchor-3 evidence: no before/after complexity figures are recorded for a simplification made within this artifact's own design lineage — the only comparison the mechanical block gives is cross-arm (T vs U vs W), not a before/after of one lineage, and NOTES.md's narrated simplifications (deriving `available`, relying on dict insertion order) are argued in prose, not quantified.

### D3 — modularity

**Score:** 4

**Citations** (`file:line` — the bar is in the scoring rules above):

- `quota_ledger/domain.py:13-16`
- `quota_ledger/domain.py:22-43`
- `quota_ledger/__init__.py:22-39`
- `tests/test_ledger.py:26-36`
- `tests/test_ledger.py:77-131`
- `tests/test_ledger.py:260-270`

**Refuses to claim** (required and non-null for a score of 4): NOTES.md states plainly that nothing else in the design is indirected: no port in front of the arithmetic, no repository interface over the reservations dict, no service layer — the artifact does not claim ports-and-adapters purity beyond the one genuine I/O dependency it identified.

**Rationale:** `domain.py:13-16` imports only `__future__`, `dataclasses` and `typing` — I read this directly in the file, it is not merely asserted; the `Journal` Protocol declared at `domain.py:22-43` is the only vocabulary the domain uses for its one external dependency. `tests/test_ledger.py:260-270` additionally checks this by parsing the module's AST rather than trusting the docstring's claim. The specific swap is named and demonstrated, not just described: `quota_ledger/__init__.py:22-39` is the one composition module that imports both `FileJournal` and `InMemoryJournal`, and NOTES.md states the swap is replacing `FileJournal(ledger_path)` with `InMemoryJournal()` on `__init__.py:39` alone. That swap is exercised at runtime, not just possible in principle: `tests/test_ledger.py:26-36` parametrizes a `journal` fixture over `FileJournal` and `InMemoryJournal`, and every case built on it (e.g. `tests/test_ledger.py:77-131`) runs unchanged against both, asserting a literal expected value each time rather than only cross-checking the two wirings against each other. I ran `tests/test_ledger.py` myself: 53 passed, both wirings, confirming this firsthand rather than trusting NOTES.md's description of it.

### D4 — behavior preservation

**Score:** 3

**Citations** (`file:line` — the bar is in the scoring rules above):

- `NOTES.md:16-28`
- `EVIDENCE.md:61-62`
- `EVIDENCE.md:172-187`
- `EVIDENCE.md:75-80`

**Refuses to claim** (required and non-null for a score of 4): n/a (score is 3, not required).

**Rationale:** Anchor 2: `NOTES.md:16-28` names the two suites and the exact commands, and I ran both myself (shared suite: 28 passed; the artifact's own `tests/test_ledger.py`: 53 passed) rather than trusting the count. The behaviors are enumerated by name across the suites and each holds. Anchor 3: `EVIDENCE.md:172-187` shows `corpus-whole`, generated from the shared model, is non-vacuous on this artifact — 43128 cases, 3734 executed, 0 failed on unmutated code — and `EVIDENCE.md:75-80` records it killing 6 of the 10 real mutants (M05-M10), so the check is model-derived, not only hand-written. I am **withholding anchor 4**. `judging_practice.executed_own_faults` is true and I did seed and run two of my own faults (a guard relaxation and a stale-total durable-content bug) and watched both get caught — satisfying the letter of the rule-8 gate — but in both cases the check that caught them was the hand-written suite (this artifact's own `tests/test_ledger.py` and the shared `test_behavior.py`), not the model-derived `corpus-whole` that anchor 3's higher bar rests on. I did not have `cases.py` in scope to run the model-derived corpus myself against a deliberate break. Anchor 4's text continues directly from anchor 3 ("3, and a deliberate behavior-breaking change is shown to be caught — the check is demonstrated to be capable of failing"), and I read "the check" as referring back to the model-derived one anchor 3 just established, which I did not personally exercise. This is a close, arguable call — see Disclosures.

### D5 — honesty

**Score:** 4

**Citations** (`file:line` — the bar is in the scoring rules above):

- `NOTES.md:125-147`
- `NOTES.md:136-141`
- `EVIDENCE.md:192-218`
- `EVIDENCE.md:219-235`

**Refuses to claim** (required and non-null for a score of 4): `NOTES.md:127-131,142-145`: no claim is made about `available`/`committed` on an unknown tenant beyond raising `KeyError`, `is_closed` on an unknown tenant beyond returning `False`, or about non-integer amounts at all — each is named as unaddressed by the feature rather than silently decided.

**Anchor reading** (required at 3 or 4; `disclosure` or `measured`): disclosure

**Rationale:** Anchor 2: `NOTES.md:125-147` names four unprompted blind spots in the artifact itself (unknown-tenant queries, an existing file at the path, a failed durable write, non-integer amounts), not only in a separate report. Anchor 3: EVIDENCE.md's evidence format itself refuses positive/negative verdicts its basis does not support rather than reporting a false clean — M09 is marked `"decides_nothing": true` (`EVIDENCE.md:219-235`) instead of being scored as a real negative-control pass, because the retirement reason says the model's own representation choice means the mutant doesn't decide what it claims to. Anchor 4: `NOTES.md:136-141` states plainly, unprompted, that R2 (the durable-record guarantee) is "the one place I can name where R2 is not enforced by construction" — if `append` raises after memory has already moved, the record is not written and nothing rolls back. That is a genuine, named weakness of this artifact's own guarantee, not a limitation of the evaluation harness, which is why I score it under the `disclosure` reading rather than `measured`: it is the artifact naming an unflattering fact about itself, not a number the artifact computed against itself. (`EVIDENCE.md:192-218`'s `M07-positive-control-wrong-hold: green: false` would also support the `measured` reading — it is a genuinely unflattering result — but that result is about the shared instrument's insufficiency, not about artifact T's own code, so I did not use it as the primary basis.)

## Verdict

T's boundary is real and demonstrated (domain imports nothing, real+fake adapters run the same 53 cases, refusal and content faults are caught and the artifact names its own durability gap), so treat it as a credible reference shape for this feature — but its D2 complexity increase is argued, not before/after measured, and D4 is deliberately capped at 3 because my own seeded faults were caught by hand-written checks, not the model-derived corpus, so do not read this card as certifying the model-derived check itself against a deliberate break.

## Disclosures

I did not read `references/eval_scorecard.md`, `rubric_v3_frozen.md`, any other artifact's scorecard, `NEXT-EPIC.md`, `PORTABLE-SUBSTRATE-EPIC.md`, `references/portable_scorecard.md`, any `*-EPIC.md`, or any `UNBLINDING.md`. I did not learn which arm (with-prompt vs without) `T` is, and did not go looking. The only files I read outside my own card directory and the artifact's declared scope were: `examples/validation/ab/tests/test_behavior.py` (the shared suite, run against the artifact per its own NOTES.md instructions — necessary to reproduce the claimed pass count) and `examples/validation/scorecards/score_tools.py` (to understand the schema the checker enforces, per the task's own step 6). All test execution and fault seeding happened in a scratch copy under the session's scratchpad directory; nothing in the repository or in the scored card directory was modified except this card.

**What I rejected:**
- I was tempted to score **D4 = 4**: `judging_practice.executed_own_faults` is mechanically `true`, which is the only gate the checker enforces, and the checker raised no problem at D4=4. I rejected it anyway because the substance of the anchor — "the check is demonstrated to be capable of failing" — reads to me as continuing to refer to the *model-derived* check anchor 3 just established, and my own two seeded faults were both caught by hand-written suites, not by `corpus-whole` itself. I did not have the shared corpus (`cases.py`) in scope to verify that directly. I recorded this as a close call rather than silently taking the higher score the checker would have allowed.
- I was tempted to score **D2 = 3**: NOTES.md narrates two real simplifications (`available` derived rather than stored; `outstanding_ids()` relying on dict insertion order instead of a sort) with clear reasoning about what they avoid. I rejected anchor 3 because neither is accompanied by a measured before/after complexity figure for this artifact's own lineage — the only quantitative comparison in the packet is cross-arm (T vs U vs W), which is a different claim from a before/after of one design.
- I treated `EVIDENCE.md`'s kill table and control-status apparatus as legitimate measured evidence about artifact T (in scope, control-audited, not merely a narrative claim) per scoring rule 1, rather than refusing to use it at all. This is an interpretive choice I am naming rather than hiding: the alternative reading would treat only code and my own executed faults as citable, which would have capped D1 at 2-3 instead of 4.
- Nothing ambiguous was found regarding the HARD PROHIBITIONS themselves — the boundary between "artifact scope" and "prohibited files" was clear. What was mildly disorienting: `scorecard.md`'s own text says `mechanical.json` beside it "holds kill counts, complexity figures, case counts, determinism and runtime," but that file is entirely empty for this run (`kills: {}`, `complexity_of_produced_code: {}`, etc.) — the actual mechanical figures live inline in `EVIDENCE.md`'s own "MECHANICAL BLOCK" section instead. I used `EVIDENCE.md`'s block and did not treat the empty `mechanical.json` as a missing-evidence problem, but flag the mismatch here since a reader expecting `mechanical.json` to be populated would come away confused.
