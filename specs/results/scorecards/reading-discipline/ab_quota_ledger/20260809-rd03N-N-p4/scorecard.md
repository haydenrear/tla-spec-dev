# Scorecard — ab_quota_ledger, artifact `N`, judge pass 4

`run_id`: `20260809-rd03N-N-p4` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

**You are scoring artifact `N`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

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

## Judge pass 4 — filled

Judge model: `claude-sonnet-5`. Commit scored: `f52be89c7e494fc98243702c5f4a4d26d5001af9`. Full detail (citations, rationale, refuses_to_claim, anchor_reading) is mirrored in `scorecard.json`; this section is the same content in prose.

**Judging practice.** `executed_own_faults: true`. What I ran: the shared suite and the artifact's own suite against a scratch copy of this tree (28 and 37 passed, matching NOTES.md); `mutation_check.py` (first, by accident, with no `pytest` on the bare `python3`, which made every mutant read as "caught" because the harness treats any nonzero subprocess exit as a catch — caught the discrepancy against the printed table and re-ran correctly via `uv run --with pytest`, reproducing NOTES.md's table exactly, M8 SURVIVED); all 12 shipped mutants regenerated and run directly against the real shared suite from the repo root (reproduced the 7-of-12 split exactly); one fault of my own not among the 12 (deleted `release()`'s `del self._outstanding[reservation_id]` line) run against both suites and reproduced interactively; and an independent 1000-walk x 60-op x 3-tenant differential between this tree and artifact D that I wrote myself (60,000 operations, 0 divergences).

**D1 — bug detection: 3.** Citations: `quota_ledger.py:94-104` (reserve's fixed rejection order), `test_quota_ledger.py:38-50` (`test_reserve_rejection_order`, two-clause-violating inputs), `test_quota_ledger.py:193-206` (`test_r4_every_rejection_path_changes_nothing`, R4 from a non-empty book), `mutation_check.py:37-46` (M1). The own suite catches an ordering fault (M1, verified: survives the real shared suite, caught by the own suite) and a cross-aspect before-state (R4 checked from a non-empty book, not just a fresh one) — both classes the whole-view shared suite structurally cannot reach alone. Not a 4: every case is hand-written; there is no formal model anywhere in this exercise for cases to be derived from.

**D2 — complexity: 2.** Citations: `quota_ledger.py:60-63` (the `_held` field and its comment), `:111` (reserve), `:122` (commit), `:136` (release) — three synchronized update sites — and this card's `mechanical.json`. Complexity is broadly proportional to FEATURE.md's four commands/five queries/five rules; NOTES.md:22-26 does argue a relationship between figures and design, ruling out anchor 1. The one exception is `_held`: a stored per-tenant total duplicating what `_outstanding` already implies, kept in sync at three call sites — accidental rather than essential structure (this is exactly what artifact D removes), but narrow enough (3 sites, one class) that I did not drop this below 2. N has no before (mechanical.json: "This tree is a greenfield subject"), so anchor 3 cannot apply regardless.

**D3 — modularity: 0.** Citations: `quota_ledger.py:65-69` (`__init__` mkdir/write_text), `:86-90` (`ledger_lines` read_text), `:156-160` (`_append` open/write) — all directly on `QuotaLedger`, no Protocol/ABC/injected writer; mechanical.json confirms declared_interfaces=0 and tags the tree "effectful" (agreement: agree). FEATURE.md leaves this a free choice, so it is not a defect against spec, but no port/adapter boundary is discernible and none is named in prose to fail to follow, ruling out anchor 1. Floor score.

**D4 — behavior preservation: 2.** Citations: `NOTES.md:36-125` (clause-by-clause account), `:127-159` (R1-R5 checked after every op of 200 walks x 40 ops), `mutation_check.py:36-99`. Behaviors are enumerated and shown, by an actual run, to hold — verified myself rather than trusted (see judging practice). Anchor 3 needs a model-derived check; nothing here is, so capped at 2.

**D5 — honesty: 4**, anchor_reading `measured`. Citations: `NOTES.md:227-234` (measured R2 violation: two `QuotaLedger` instances on one path), `:204-211` (differential-column hedging, agreeing with the "zero does not prove equivalence" caveat), `mutation_check.py:120-125` (that caveat's source), `NOTES.md:264-278` ("Things I could not check, or did not"). Anchor 2/3 clearly met (unprompted limits, explicit refusal to over-read a 0/400 divergence count as proof). Anchor 4: the two-ledgers-one-path item is a *measured*, demonstrated R2 violation the author produced and reported, not merely a disclosed gap — unflattering under either reading, scored under `measured`. Refuses to claim: durability under crash/power-loss; safety of two ledger instances on one path; a saturation claim about its own 12 mutants.

**Verdict.** Ship-quality single-file implementation with unusually rigorous self-testing, but not ports-and-adapters (D3=0) and nothing model-derived (D1/D4 capped); the two concrete next steps are the redundant `_held` cache (which artifact D removes) and a missing dedicated test for "commit a reservation that was already released."

**What I rejected, and why:**

- **Docking D2 to 1 for the redundant `_held` field.** NOTES.md never surfaces the duplication as a concern, and it is accidental structure by the argument made on the D card. I kept N at 2 rather than 1 because anchor 1's bar ("no relationship between the figures and the design is argued") is not met — NOTES.md:22-26 does argue one — and the duplication itself is narrow (3 sites, 1 class), not a god-object. Named the tension in the rationale instead of silently rounding down.
- **Crediting D1 or D4 with a 4 because the artifact's own account is genuinely thorough.** Rigor is not model-derivation. Nothing in this exercise is generated from a formal model (no TLA+ layer anywhere under `examples/validation/ab/`); anchor 4 on both dimensions requires exactly that, and no amount of hand-written care substitutes for it.
- **Scoring D3 at 1 instead of 0**, on the theory that `_append`/`ledger_lines` being the only two file-touching methods is an informal boundary. Rejected: anchor 1 needs a boundary *named* (in prose or a declaration) that the code then fails to follow, and nothing here is named — FEATURE.md explicitly declines to require one. Scoring 1 would have meant inventing a declaration to then mark not-quite-followed.
- **Treating my own seeded fault (the `release()` deletion) as proof D is "more correct."** It is not — it is evidence D's simplification changes *where* an identical-sized defect shows up, not whether one exists. Both trees ship the bug equally (I put it there); the finding is about detectability and duplication, kept in the D2 rationale rather than read as a correctness win for D.
- **A defect worth filing, for whoever owns this exercise next**: neither the shared suite nor either artifact's own suite has a test titled for "commit a reservation that was already released" (the reverse order — release after commit — is tested; this direction is not). Both catch my seeded version only as collateral damage on other assertions (R1, `outstanding_ids`), not via a dedicated check, and on N specifically that collateral path needs a second operation (a follow-up commit) before anything looks wrong, since `available()` alone does not notice.
- **Files I opened:** only the allowed set — this artifact tree, my two card directories, FEATURE.md, test_behavior.py, and both `mechanical.json` files (which the scaffold itself points a judge at). I did not read `references/eval_scorecard.md`, `UNBLINDING*`, `GOAL-product-round/`, any other judge's card, or `arm_a/arm_b/arm_c/revision/dispatch/seeded_faults.toml/check_catalogue.py`. I did not go looking for the arm mapping and did not work it out. All test/fault runs were against scratch copies in `/private/tmp/.../scratchpad/`; nothing under `specs/results/...` was edited.
