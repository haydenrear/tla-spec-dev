# Scorecard — ab_quota_ledger, artifact `D`, judge pass 4

`run_id`: `20260809-rd03D-D-p4` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

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

## Judge pass 4 — filled

Judge model: `claude-sonnet-5`. Commit scored: `f52be89c7e494fc98243702c5f4a4d26d5001af9`. Full detail (citations, rationale, refuses_to_claim, anchor_reading) is mirrored in `scorecard.json`; this section is the same content in prose. I diffed artifact N and artifact D myself before scoring either — the only substantive change anywhere in `quota_ledger.py` is the removal of the `_held` field and its three synchronized update sites, plus one added test in `test_quota_ledger.py`; `mutation_check.py` is byte-identical.

**Judging practice.** `executed_own_faults: true`. What I ran (full list in `judging_practice.what_was_run`): shared suite and own suite against a scratch copy of this tree (28 and 39 passed, matching REVISION-NOTES.md); `mutation_check.py`, reproducing NOTES.md/REVISION-NOTES.md's table exactly (M8 SURVIVED, 11/12 caught, byte-identical to N's table); all 12 shipped mutants regenerated and run against the real shared suite directly (same 7-of-12 split as N); one fault of my own, not among the 12 (deleted `release()`'s `del self._outstanding[reservation_id]` line), applied identically to both trees and reproduced interactively — on D it is visible immediately on `available()` itself, on N it is masked by the still-correct `_held` field; an independent 60,000-operation N-vs-D differential I wrote myself (0 divergences), distinct from and not trusting the equivalence script REVISION-NOTES.md describes but does not ship; and a targeted reconstruction — post-revision code plus N's pre-revision 37-test suite, mutant M4 applied — that independently confirmed REVISION-NOTES.md's central claim: the id-reuse mutant M4 survives (37 passed) against the code with `_held` removed but the new test not yet added, exactly as REVISION-NOTES.md reports happened before the fix was written.

**D1 — bug detection: 3.** Citations: `quota_ledger.py:96-106`, `test_quota_ledger.py:38-50`, `:209-222`, `:108-121`, `mutation_check.py:37-46`. Same ordering/cross-aspect evidence as N (unchanged by the revision, confirmed by diff), plus a second, D-specific instance: `test_ids_advance_even_when_outstanding_returns_to_empty` (:108-121) exists because removing `_held` turned mutant M4 from an accidental catch into a survivor, and this new test is what catches it directly instead. Verified myself (see judging practice). Not a 4, same reason as N: no formal model anywhere in this exercise.

**D2 — complexity: 3 — the headline dimension.** Citations: `quota_ledger.py:70-76` (D's derivation), `artifact_N/quota_ledger.py:60-63,111,122,136` (the removed field and its three sites), `REVISION-NOTES.md:27-53` and `:84-123`, this card's `mechanical.json`. mechanical.json records both before/after tables: instance_state 7→6, code_lines 283→280, but branch_points 26→27 (the static instrument counts the generator's inline filter as a branch, even though it replaces three imperative branches with one declarative one) — instrument and judgement disagree on that one figure's direction, and I say so rather than picking the number that supports my read. What got simpler: four call sites that had to agree about one number collapse into one authoritative table read once. I did not accept this on the artifact's word — I seeded a fault of my own (deleting `release()`'s outstanding-clear) into both trees identically. In N the bug is partly masked (`available()` reads a separate field the deletion doesn't touch, so it keeps reporting correctly until the zombie reservation is later committed a second time, at which point N genuinely manufactures capacity: available=10, committed=3, sum=13 > quota=10). In D the same one-line deletion is immediately visible on `available()` itself, because there is only one representation left to corrupt. That reproduces, from an angle the artifact never tried, REVISION-NOTES.md's own claim about M4: the old duplication let a test "catch" a bug by accident (via desync), not by actually checking for it. Not a 4: anchor 4 needs D4 ≥ 3, and D4 tops out at 2 for both artifacts (no model-derived check exists in this exercise), so 4 is unreachable regardless of how strong the behavior-preservation evidence is.

**D3 — modularity: 0.** Unchanged from N by the revision (confirmed by diff): `__init__`, `ledger_lines`, and `_append` still touch the filesystem directly on `QuotaLedger` itself, no port/adapter boundary discernible or named. Citations: `quota_ledger.py:62-66,88-92,155-159`, mechanical.json.

**D4 — behavior preservation: 2.** Citations: `REVISION-NOTES.md:55-71` (enumerated invariant + differential claim), `:19-21` (test counts), `:84-123`. REVISION-NOTES.md's own equivalence script is explicitly "not in the deliverable," so I did not accept its claim as-is — I wrote and ran my own independent N-vs-D differential (60,000 operations, 0 divergences), which corroborates anchor 2 on evidence I generated, not evidence I read. Anchor 3 needs a model-derived check; nothing here is (mine included) — capped at 2, same ceiling as N.

**D5 — honesty: 4**, anchor_reading `measured`. Citations: `REVISION-NOTES.md:73-82` ("What it costs" — O(1)→O(n) `available()`, stated plainly), `:89-107` (the M4 regression-then-fix story), `:207-214` (N's measured R2 violation carried forward, not dropped). D earns its own, second, independent anchor-4 result beyond what it inherits from N: the revision's own first pass caused a *measured* regression — removing `_held` silently dropped the shipped mutation suite's M4 kill from caught to SURVIVED — which the author found, diagnosed as an accidental catch, and only then fixed. I independently reproduced a version of the same phenomenon with a fault of my own (see D2). Refuses to claim: performance-neutrality for `available()`; durability under crash/power-loss (inherited); safety of two ledger instances on one path (inherited, still unresolved); exhaustiveness of its own equivalence check.

**Verdict.** The `_held` removal is a genuine, measured simplification (D2=3): it collapses a duplicated per-tenant total into a single derivation, verified behavior-preserving by both the artifact's own equivalence claim and my independent 60,000-operation differential (0 divergences) — but it is not free, since the same change caused a real, disclosed regression in the shipped mutation suite and a stated O(1)→O(n) cost, and it inherits N's D3=0 and the missing "commit after release" test unchanged.

**What I rejected, and why:**

- **Reading the branch_points increase (26→27) as evidence this is NOT a simplification.** I considered scoring D2 at 2, treating the mixed metric signal as reason to doubt the "simplification" framing entirely. I rejected this because the rubric explicitly asks the judge to look past a metric moving in either direction and say what got simpler in the code — I did that (three synchronized writes collapsed to one derivation) and backed it with a fault I seeded myself, not with the metric. The metric disagreement is recorded as a finding in the D2 rationale, not resolved by picking whichever number was convenient.
- **Scoring D2 at 4.** The behavior-preservation evidence here (my own 60,000-op differential, REVISION-NOTES.md's 3000-walk claim, the M4 reconstruction) is about as strong as this kind of artifact gets, and I was tempted to let that strength carry D2 to the top. I did not, because anchor 4 has a specific, mechanical gate (D4 ≥ 3) and D4 cannot clear it here — no model-derived check exists anywhere in this exercise. Strength of hand-written evidence is not a substitute for the anchor's stated requirement.
- **Treating my MY1 fault finding as proof D is "more correct" than N.** Same rejection as on the N card: it is evidence about where an identical defect becomes visible, not about which artifact ships fewer defects. Both trees have the bug equally, because I put it there.
- **Crediting D1 with a 4** for having *two* instances of the anchor-3 pattern (M1-style ordering and the new M4 test) instead of N's one. Two instances of a hand-written, non-model-derived case are still hand-written and non-model-derived; anchor 4's bar is about provenance, not count.
- **The M4 regression as a story I only half-verified.** REVISION-NOTES.md's account of "post-revision + M4 → 37 passed, nothing caught it" describes a state that no longer exists in the shipped tree (the fix is already included, so simply re-running D's `mutation_check.py` shows M4 caught). I did not let that stop me at "plausible" — I reconstructed the actual intermediate state (D's code, N's pre-fix test file) and ran it, and it does behave exactly as claimed.
- **A defect worth filing, inherited unchanged from N**: no test, in either the shared suite or either artifact's own suite, titled for "commit a reservation that was already released." The revision did not introduce or fix this; it is exactly as absent in D as in N.
- **Files I opened:** only the allowed set (this artifact tree, my two card directories, FEATURE.md, test_behavior.py, both `mechanical.json` files). Nothing forbidden. I did not go looking for the arm mapping and did not work it out. All test/fault runs were against scratch copies; nothing under `specs/results/...` was edited.
