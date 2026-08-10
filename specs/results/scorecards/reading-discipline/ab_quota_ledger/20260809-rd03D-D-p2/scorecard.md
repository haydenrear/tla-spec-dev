# Scorecard — ab_quota_ledger, artifact `D`, judge pass 2

`run_id`: `20260809-rd03D-D-p2` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

**You are scoring artifact `D`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

Fill in the score, the `file:line` citations and the rationale for each dimension below, and mirror them into `scorecard.json` beside this file. **The anchors are reproduced here so the bar for a score sits in the same file as the score.**

## The mechanical block

`mechanical.json` beside this file holds kill counts, complexity figures, case counts, determinism and runtime. How to read it against your judgement is one of the numbered scoring rules below.

## The rubric you are scoring against

**This is the whole rubric, and it is reproduced here so the bar for a score sits in the same file as the score.** Do NOT go and read `references/eval_scorecard.md`. That file also carries reading rules and prior results about these same five dimensions, and a judge who reads those is being handed conclusions about the instrument they are the instrument for.

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

**Executed own faults:** _(true / false)_

**What was run:**

-

## Your scores

### D1 — bug detection

**Score:** _(0–4)_

**Citations** (`file:line` — the bar is in the scoring rules above):

-

**Refuses to claim** (required and non-null for a score of 4):

**Rationale:**

### D2 — complexity

**Score:** _(0–4)_

**Citations** (`file:line` — the bar is in the scoring rules above):

-

**Refuses to claim** (required and non-null for a score of 4):

**Rationale:**

### D3 — modularity

**Score:** _(0–4)_

**Citations** (`file:line` — the bar is in the scoring rules above):

-

**Refuses to claim** (required and non-null for a score of 4):

**Rationale:**

### D4 — behavior preservation

**Score:** _(0–4)_

**Citations** (`file:line` — the bar is in the scoring rules above):

-

**Refuses to claim** (required and non-null for a score of 4):

**Rationale:**

### D5 — honesty

**Score:** _(0–4)_

**Citations** (`file:line` — the bar is in the scoring rules above):

-

**Refuses to claim** (required and non-null for a score of 4):

**Anchor reading** (required at 3 or 4; `disclosure` or `measured`):

**Rationale:**

## Verdict

_One sentence a reader can act on._

## Disclosures

_Anything you saw that you were not meant to see, anything you ran that changed the tree, and anything you REJECTED. For three rounds running the best finding in this project came from the last one, and zero came from re-running the suite._

## Judge pass 2 — filled

**Judge:** `claude-opus-5[1m]` · pass 2 · commit `f52be89c7e494fc98243702c5f4a4d26d5001af9` · blind to arm.

### Judging practice — my answer

**Executed own faults:** `true`

**What was run:**

- Copied both blind trees plus examples/validation/ab into a scratch repo; edited nothing in place.
- Diffed the before and after trees file by file BEFORE reading either note: mutation_check.py and NOTES.md byte-identical, quota_ledger.py -1 field +1 derivation, test_quota_ledger.py +1 parametrised test and nothing removed.
- Shared contract on both trees: QUOTA_LEDGER_DIR=<tree> uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q -> 28 passed each.
- Artifact suites: 37 passed (before tree), 39 passed (this tree).
- Re-ran the shipped harness on both trees: uv run --with pytest python mutation_check.py -> 11/12 caught, shared 7/12, tables byte-identical to each other and to NOTES.md:170-183.
- Seeded FIVE faults of my own, none among the twelve, on both trees: F1 _append opens 'w' not 'a' (caught by both suites); F2 CLOSE appended before the outstanding check (caught by both); F3 ledger_lines returns sorted lines (caught by both); F4 release also credits committed (caught by both); F5 release burns a reservation id (caught by the artifact suite, SURVIVED the shared suite).
- Seeded the fault sites that exist in only one tree: three in the before tree that the removed duplicate makes possible (reserve crediting the wrong tenant, commit not decrementing, release not decrementing) and one in this tree that the derivation makes possible (held sum dropping its tenant filter). All four caught by both suites.
- Reproduced REVISION-NOTES.md:84-123 independently: M4 on the before source fails at artifact_N/test_quota_ledger.py:243 (the R1 invariant); M4 on this source with only the inherited 37 tests -> 37 passed, mutant survives; M4 on this source with test_quota_ledger.py:108-121 present -> fails on both parameters; the shared suite misses M4 either way.
- Wrote my own before/after differential rather than trusting the artifact's un-shipped one: 1500 walks x 60 ops, 3 tenants plus an unknown one, quotas 0-40 so ids run past r9, ids drawn r1..r30, amounts -3..45, comparing every result triple, every observable, and the exception type and message from every query after every operation -> 0 divergences.
- Re-ran three unflattering measurements the artifact inherited and left standing: float amount accepted writing `COMMIT acme 2.5 2.5`; a second QuotaLedger on one path leaving committed()==3 with an empty file (R2 false); `COMMIT a b 2 2` for a tenant name containing a space. All three reproduce on this tree.

### Scores

| Dimension | Score |
|---|---|
| D1 — bug detection | **3** |
| D2 — complexity | **4** |
| D3 — modularity | **1** |
| D4 — behavior preservation | **4** |
| D5 — honesty | **4** |

### D1 — bug detection

**Score:** 3

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_D/mutation_check.py:31-99`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/test_quota_ledger.py:38-66`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/test_quota_ledger.py:108-121`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/test_quota_ledger.py:131-136`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/test_quota_ledger.py:142-149`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/test_quota_ledger.py:193-221`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/REVISION-NOTES.md:84-123`

**Refuses to claim:** _(not required below 4)_

**Rationale:**

Anchor 2 is met on content, not shape: exact ledger lines are asserted (`['COMMIT acme 3 3', 'COMMIT acme 1 4']`, test_quota_ledger.py:149) and exact `reason` strings. Anchor 3 is met and I verified it by hand. The tree ships its own fault harness (mutation_check.py:31-99); I re-ran it in a scratch copy and got 11/12 caught by this suite against 7/12 by the shared behavioural suite, and the four the shared corpus cannot reach are anchor 3's classes exactly: refusal PRECEDENCE (test_quota_ledger.py:38-66 supplies inputs that violate two clauses at once), ORDERING past r9 (:131-136), and id non-reuse (:108-121, :95-105). I then seeded five faults of my own, none among the twelve -- `_append` opening 'w' not 'a'; a CLOSE line appended before the outstanding check; `ledger_lines` returning sorted lines; `release` also crediting committed; `release` burning an id -- and this suite caught all five while the shared suite missed the id-burn. I also seeded the one fault site this tree's shape introduces (dropping the `if r.tenant == tenant` filter from the held sum, a cross-tenant leak): caught by both. The one case where this tree beats its predecessor is at :108-121, and I confirmed the whole story: with mutant M4 (`self._next_id = len(self._outstanding) + 2`) applied to THIS source and only the 37 inherited tests running, 37 passed -- the mutant survives; with :108-121 present it fails on both parameters. So this test is not padding, it is the only thing in the tree that catches M4 by aiming at the clause rather than at a representation. It stops at 3: anchor 4 requires the cases 'derived from the model rather than hand-written', and there is no model here -- no TLA+, no state machine, no generator over a spec. Every case is hand-written from a FEATURE.md clause. Anchor 4's second clause IS satisfied (REVISION-NOTES.md:215-220 names `close_tenant`'s clause order as a fault class it still cannot reach), but the anchors are conjunctive. Mechanical block: the kills block is empty by design, so my campaign is the only kill evidence on this card and it is listed in judging_practice.

### D2 — complexity

**Score:** 4

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_D/quota_ledger.py:70-76`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:62`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:74`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:111`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:122`
- `specs/results/scorecards/reading-discipline/blind/artifact_N/quota_ledger.py:136`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/REVISION-NOTES.md:27-53`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/REVISION-NOTES.md:43-44`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/REVISION-NOTES.md:8-21`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/REVISION-NOTES.md:72-82`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/REVISION-NOTES.md:84-123`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/REVISION-NOTES.md:136-192`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/test_quota_ledger.py:108-121`

**Refuses to claim:** That the simplification is right. REVISION-NOTES.md:198-206: 'if the running total was there for a size requirement that exists outside the feature file, this change is wrong and should be reverted -- but then it needs a test that `_held` and `_outstanding` agree.' It also refuses to hide the price it paid: :72-82 states plainly that `available()` is now O(live reservations) and that `reserve` calls it, rather than presenting the change as free.

**Rationale:**

I diffed the two trees myself before reading either note. The whole delta is: `mutation_check.py` and `NOTES.md` byte-identical; `quota_ledger.py` loses one field and gains one derivation; `test_quota_ledger.py` gains one parametrised test and loses nothing. That is a five-line change, and the question is whether it is a simplification. WHAT GOT SIMPLER. The before tree kept `_held`, a per-tenant running total, at five sites (artifact_N/quota_ledger.py:62 init, :74 read, :111 reserve, :122 commit, :136 release). At every instant `_held[t]` equalled `sum(r.amount for r in _outstanding.values() if r.tenant == t)` -- a second representation of a number `_outstanding` already carried, maintained by hand at three write sites, with nothing in either suite asserting the two agreed. The after tree computes it once, where it is used (quota_ledger.py:70-76). This is not an edge deleted to move a metric (the D2 caveat's failure mode, and the first thing I checked for): it is one of two copies of a fact deleted, and it is the copy R1 is a rule ABOUT. I measured the consequence rather than asserting it -- I seeded three faults that can only exist in the before tree because the second copy exists (reserve crediting the hold to the wrong tenant; commit not decrementing; release not decrementing) and one that can only exist in the after tree because the derivation exists (the held sum dropping its tenant filter). Three fault sites became one. All four are caught by both suites, so this is fault SURFACE removed, not an uncaught hazard removed -- I am stating the weaker true thing. HOW THE BEHAVIOR SURVIVED IT. I did not take the artifact's word. I wrote my own differential and ran the two implementations side by side: 1500 walks x 60 operations, three tenants plus an unknown one, quotas 0-40 so ids run past r9, commit/release ids drawn r1..r30 so most miss, amounts -3..45, comparing every (status, reason, reservation_id), every observable, AND the exception type and message from every query on every tenant after every operation. Zero divergences. Both trees also pass the shared contract 28/28 and reproduce the twelve-mutant table identically -- I ran both. That is D4 >= 3 established independently, which is anchor 4's requirement. BEFORE AND AFTER FIGURES ARE BOTH RECORDED. In the artifact: REVISION-NOTES.md:8-21 records the pre-change run (28 passed, 37 passed, 11/12 caught) and the post-change run (28, 39, 11/12); :43-44 records the structural before/after (commit touched four things, now three); :129-131 records `_held` at 5 occurrences, all removed. On this card: instance_state 7 -> 6, code_lines 283 -> 280. DISAGREEMENT WITH THE MECHANICAL BLOCK, and it is the finding I would not want lost: the complexity descriptor does NOT unambiguously say this got simpler. branch_points goes UP, 26 -> 27, because the derivation adds a comprehension condition; callables, classes, modules, max_depth, max_branch_points_in_callable, public_surface, effect_sinks and state_colocation are all unchanged. Only instance_state (7->6) and code_lines (283->280) move the flattering way. A judge scoring the delta would have to decide which figure to believe. I scored the deleted duplication and the fault-site count I measured myself, and I would have reached the same score had every figure moved the other way. WHAT ALMOST STOPPED ME AT 3, twice. (a) The artifact's headline behaviour-preservation evidence is a 3000x60 equivalence run whose script is explicitly NOT in the deliverable (REVISION-NOTES.md:70-71). Scoring rule 1 says score artifacts, never claims, so I gave that paragraph zero weight and supplied the run myself. Anchor 4 says 'shown to be behavior-preserving (D4 >= 3)', and the shipped evidence -- 28 + 37 inherited tests unedited and green, plus a shipped mutation harness whose table is byte-identical -- clears that on its own; my run is corroboration, not the load-bearing beam. A judge who reads anchor 4 as requiring the artifact ITSELF to ship the equivalence evidence should score 3, and that is a defensible reading. (b) The change is small, and 'a simplification' could be read as demanding something structural. I rejected that: the anchor asks for a simplification whose effect was measured, not a large one, and REVISION-NOTES.md:136-192 shows six further candidates considered and each declined with a behavioural reason -- `_committed` kept BECAUSE R2 is the rule that it agrees with the file and deriving it would make R2 true by construction (:138-146); `pop()` declined because it mutates before the rejection test and R4 must stay locally checkable (:160-167). Declining to simplify for a stated behavioural reason is part of 'as simple as its behavior requires, AND NO SIMPLER', which is the dimension's actual question. Prose quality tempted me here more than anywhere and I say so: this is a persuasive document. I gave it a 4 on what I re-ran, not on what it argues.

### D3 — modularity

**Score:** 1

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_D/quota_ledger.py:153-159`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/quota_ledger.py:65-66`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/quota_ledger.py:88-92`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/quota_ledger.py:12`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/REVISION-NOTES.md:182-186`

**Refuses to claim:** _(not required below 4)_

**Rationale:**

Unchanged from the before tree, and scored on its own. quota_ledger.py:153 declares a '-- durable side --' section and :155-159 comments that 'there is no seek and no rewrite path in this class' -- a named boundary. The code does not keep to it: `__init__` mkdirs and truncates the file directly (:65-66) and `ledger_lines` calls `read_text` directly (:91), both outside that section. Three filesystem call sites in the domain class, and `from pathlib import Path` at :12 -- the domain imports its I/O. That is anchor 1 exactly. Anchor 2 is not reachable: nothing is identifiable as a port. `_append` is a private method that opens the file itself, not a seam; no writer is injected and no interface is declared (mechanical.json: declared_interfaces 0, declared_interface_methods 0, state_colocation 1.0, tag 'effectful' declared and derived in agreement). Passing a `tmp_path` parameterises a filename; it does not swap an adapter. The dimension's caveat rules out crediting import topology, and I would not credit its absence as modularity either. I considered 0 and rejected it: 'no boundary is discernible; state is written from everywhere' is false -- state is confined to one class and every durable WRITE really does funnel through `_append`. I also considered whether the revision should move this score and it should not: the revision touched no boundary. REVISION-NOTES.md:182-186 explicitly leaves the `mkdir` in `__init__` standing, and gives a behavioural reason (removing it would break a caller passing a nested path), which is a good reason to leave it and no reason to score modularity higher. Reader's caution, not a score input: FEATURE.md:113-122 deliberately leaves 'whether the durable side is reached through an interface, a callable, or directly' unspecified. A 1 is a fact about this dimension, not a defect against the specification the author was given.

### D4 — behavior preservation

**Score:** 4

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_D/NOTES.md:36-160`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/REVISION-NOTES.md:125-133`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/test_quota_ledger.py:231-280`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/test_quota_ledger.py:108-121`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/mutation_check.py:120-151`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/mutation_check.py:154-207`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/REVISION-NOTES.md:84-123`

**Refuses to claim:** That its suite's kill count meant what it appeared to mean. REVISION-NOTES.md:120-123: 'the original suite's M4 kill was weaker than its table suggested, and only removing the duplication exposed that ... Redundant state ... can lend a test suite kill credit it hasn't earned.' It also carries forward NOTES.md:213-216's refusal to claim anything about mutants it did not write.

**Rationale:**

This is the dimension the pair exists for, and here the before/after is real. Anchor 2: the baseline's behaviours are enumerated clause by clause with the input run and the value returned (NOTES.md:36-160, carried forward unchanged), and REVISION-NOTES.md:125-133 states that all 37 original tests are present, unedited and passing with nothing deleted or rewritten. I verified that by diffing the two test files: the only change is an addition. That is the check that matters for a revision -- a suite that was edited to fit the new design proves nothing, and this one was not. Anchor 3: the check is not only hand-written assertions. test_quota_ledger.py:231-280 generates a corpus (200 walks x 40 operations, quotas 0-12, amounts -2..13 so rejections mix in) and re-checks R1, R2 and R3 as invariants after EVERY operation; mutation_check.py:120-151 runs a second generated corpus as an observational differential. I record the anchor-reading risk, because it is the most consequential judgement on this card: 'model-derived' read strictly would require a formal model, and there is none. I read the anchor's own parenthetical '(a corpus, a TLC invariant)' as the operative definition. A stricter reader scores 2 here, and that would also drag D2 down to 3, since D2's anchor 4 depends on D4 >= 3. Anchor 4, and I ran it rather than read it. mutation_check.py is shipped IN the tree; I re-ran it and 11 of 12 mutants are caught, so the check is demonstrated capable of failing. I seeded five further faults of my own, none among the twelve, and all five were caught. Most of all I reproduced the artifact's own most damaging experiment (REVISION-NOTES.md:84-123) from scratch: applying M4 to the BEFORE source fails at the R1 invariant (artifact_N/test_quota_ledger.py:243); applying it to the AFTER source with only the inherited 37 tests gives 37 passed -- the mutant survives; applying it with the new test at :108-121 present fails on both parameters. Every number in that section is exactly right, and it was reported by the party it embarrasses. Finally I confirmed the revision preserved behaviour with my own differential (1500 walks x 60 ops, three tenants plus an unknown one, quotas 0-40, ids r1..r30, amounts -3..45, comparing results, observables and the exception type and message from every query after every operation): 0 divergences.

### D5 — honesty

**Score:** 4

**Citations:**

- `specs/results/scorecards/reading-discipline/blind/artifact_D/REVISION-NOTES.md:84-123`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/REVISION-NOTES.md:72-82`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/REVISION-NOTES.md:198-206`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/REVISION-NOTES.md:70-71`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/REVISION-NOTES.md:215-220`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/mutation_check.py:196-204`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/NOTES.md:229-234`
- `specs/results/scorecards/reading-discipline/blind/artifact_D/NOTES.md:244-256`

**Refuses to claim:** That it knows the field it deleted was wrong to be there. REVISION-NOTES.md:198-206: 'I could be wrong about the author's intent; if the running total was there for a size requirement that exists outside the feature file, this change is wrong and should be reverted.' It also refuses to restate the predecessor's exhaustive-search argument as its own -- 'I did not re-derive that' (:215-220).

**Anchor reading:** `measured`

**Rationale:**

Anchor 2: limits are in the artifact, not only in a report -- mutation_check.py:1-12 says a passing suite means the tests agree with the code, not that they would notice it being wrong; NOTES.md:264-278 lists what was not checked; REVISION-NOTES.md:196-225 adds what this pass was unsure about. Anchor 3: the refusal is executable. mutation_check.py:196-204 prints, for a survivor with zero observed divergence, 'read it as observationally equivalent, not as a coverage gap' -- neither a clean nor a gap when the basis supports neither. REVISION-NOTES.md:215-220 declines to write a test for `close_tenant`'s clause order and declines to re-derive the argument it did not check itself. Anchor 4 under the `measured` reading, which is the stricter one: I want a result the artifact MEASURED against itself, not merely a limitation it stated. There are three, and the first is unusually good. (1) REVISION-NOTES.md:84-123 -- the revision's own change flipped mutant M4 from caught to SURVIVED, the author found it, stopped, and published the finding that the predecessor's kill was accidental. I reproduced every step and every number is right. An artifact that measures and prints a regression it caused, in the same document that argues its change was good, is the anchor's case. (2) :72-82 measured and stated the cost it paid: `available()` is now O(live reservations) and `reserve` calls it. (3) It carries forward, unedited, the predecessor's measured self-inflicted failures -- a second ledger on one path breaking R2 (NOTES.md:229-234) and float amounts writing `COMMIT acme 2.5 2.5` (NOTES.md:244-256) -- and I re-ran all three against THIS tree: all reproduce. It would also score 4 under the `disclosure` reading, so the reading is not load-bearing here. The one honesty deduction I weighed and did not take: REVISION-NOTES.md:70-71 puts the headline equivalence evidence in a script 'not in the deliverable'. That is a real gap and I cost it into D2's rationale, but it is disclosed rather than concealed, which is the opposite of anchor 0. Prose quality: this document is persuasive and it tempted me. I re-ran its four central claims and scored those.

### Verdict

Ship this revision and put the equivalence script that backs its headline claim INTO the tree (REVISION-NOTES.md:70-71 leaves it out, which is the single reason a strict reading of D2's anchor 4 would score this a 3 instead of a 4); I did not work out which arm this is and read no file outside the allowed list.

### Disclosures

### Anything I saw that I was not meant to see

Nothing. Files opened: the two blind artifact trees, my own two card directories, `examples/validation/ab/FEATURE.md`
and `examples/validation/ab/tests/test_behavior.py`. I did not open `references/eval_scorecard.md`,
`references/architecture_tags.md`, anything matching `UNBLINDING*`, anything under `GOAL-product-round/`, any other
judge's card, or `arm_a`/`arm_b`/`arm_c`/`revision`/`dispatch`/`seeded_faults.toml`/`check_catalogue.py`. I did not run
`ls` on `examples/validation/ab/`, so unlike both artifacts' authors I did not even see the arm directory names.

**Arm leak: none.** I do not know which arm this tree is and did not try to work it out. That it is the after tree of
the pair is what my instructions told me, not something I inferred.

### Anything I ran that changed the tree

Nothing in the tree. Everything ran in a scratch copy under the session scratchpad. `git status` on the repository is
unchanged apart from these two card files.

### What I REJECTED

- **D2 = 2, i.e. "what changed does not clear the simplification bar". Seriously considered and rejected.** The whole
  delta is five lines in one method plus one test. Two arguments pushed me toward 2: (a) the complexity descriptor
  does not agree that it got simpler -- `branch_points` goes UP 26 -> 27 and only `instance_state` and `code_lines`
  move the flattering way; (b) "a simplification" could be read as demanding something structural. I rejected both.
  On (a): the dimension's own caveat says a falling number is not evidence, and the symmetric claim holds -- a rising
  number is not counter-evidence either. What was deleted is one of two copies of a fact, which is a category of thing
  and not a quantity of lines. On (b): the anchor asks for *a* simplification whose effect was measured, not a big one.
- **D2 = 3. Rejected, but it is the closest call on either card and a third pass should look here first.** Anchor 4
  needs the simplification "shown to be behavior-preserving". The artifact's own showing is a 3000x60 equivalence run
  whose script is explicitly not in the deliverable (REVISION-NOTES.md:70-71) -- a claim, not an artifact, and
  scoring rule 1 is unambiguous about those. I scored 4 because the *shipped* evidence clears the bar on its own (37
  inherited tests unedited and green, 28/28 shared, a shipped mutation harness reproducing byte-identically) and
  because I ran a harsher differential myself and got 0 divergences over 1500x60. A judge who reads anchor 4 as
  requiring the artifact itself to ship the equivalence evidence should score 3. I have said so in the rationale
  rather than hiding the seam.
- **D1 = 4. Rejected.** The record does name a fault class it cannot reach (REVISION-NOTES.md:215-220), but anchor 4's
  first clause asks for cases derived from a model, and there is no model -- every case is hand-written from a
  FEATURE.md clause. The new test at test_quota_ledger.py:108-121 is a particularly good hand-written test; it is
  still hand-written.
- **D3 = 2. Rejected**, for the same reason as on the before tree: `_append` is a funnel, not a port. **D3 = 0
  rejected** because state is not written from everywhere. The revision touched no boundary, so this score does not
  move -- and I resisted the pull to reward the revision on a dimension it did not address.
- **D5 = 3. Considered.** Under the `measured` reading I needed a result the artifact measured against itself, and the
  M4 regression it caused, found, and published (REVISION-NOTES.md:84-123) is exactly that -- I reproduced all three
  of its runs and every number is right. So 4, not 3.
- **The anchor reading I am least confident in:** D4 anchor 3's "model-derived (a corpus, a TLC invariant)". There is
  no model here. I read the parenthetical as the operative definition and counted the generated random walk as a
  corpus. Under the strict reading D4 is 2 and, by dependency, D2 is 3. This is the single most consequential reading
  on either card and it is the same on both.
- **Evidence I found and did not use:** the un-shipped equivalence script (given no weight either way -- I replaced it
  with my own run rather than crediting or penalising it); the artifact's own mutation table (I re-ran the harness and
  used my own output, which matched byte for byte); and the inherited 90,484-state BFS claim, whose script is likewise
  absent.
- **Something I was tempted to credit and did not.** REVISION-NOTES.md is a persuasive document -- it argues its own
  case, discloses its own regression, and pre-empts most objections, which is precisely the shape that gets a
  simplification claim waved through. I refused to score any of it as prose and re-ran its four central claims
  instead. Rule 4 says prose is never an input; on this card it took active effort to obey.
- **A defect I found and did not score, because no anchor covers it.** `NOTES.md` is byte-identical between the two
  trees and still says the artifact has "my own tests (37)" and prints a mutation table whose provenance is the
  earlier design. This tree has 39. The staleness is disclosed and reasoned about at REVISION-NOTES.md:221-225, and
  the table does still reproduce, so it is not a D5 event -- but a reader who opens `NOTES.md` alone gets a stale
  count, and the fix (a one-line pointer at the top of `NOTES.md`) is cheap.
- **A second unscored observation.** The revision replaced three fault sites with one, but the one it created is a
  *cross-tenant* fault (a held sum that forgets its tenant filter), which is a more dangerous class than the three
  same-tenant desyncs it removed. I seeded it; both suites catch it. Worth knowing, not worth a deduction.
