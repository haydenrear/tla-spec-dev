# Scorecard — ab_quota_ledger, artifact `N`, judge pass 3

`run_id`: `20260809-rd03N-N-p3` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

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

## Judge pass 3 — filled

**Executed own faults:** true

**What was run:** shared suite and each tree's own suite against unmodified N and D (scratch copies); `mutation_check.py` run against both, both from a scratch copy and in place in the real repo; two novel seeded faults not among the shipped 12 — (A) `amount < 1` weakened to `amount < 0` in `reserve` (off-by-one admitting `amount==0`), (B) `tenant_closed` guard weakened to `self._closed[tenant] and self._committed[tenant] > 0` (a refusal-class fault) — each run against copies of both N's and D's `quota_ledger.py` with both the shared suite and each tree's own suite. Full detail is in `scorecard.json.judging_practice`.

### D1 — bug detection: **3**

Adapters assert content (`.reason`, `ledger_lines()`), clearing anchor 2 (`quota_ledger.py:94-104`, `test_quota_ledger.py:48`). Anchor 3 clears via M1 — an ordering fault (`mutation_check.py:37-46` swaps the `tenant_closed`/`amount_not_positive` check order) that `NOTES.md:170-178` records as caught by the artifact's own suite and survived by the shared corpus, because the shared corpus only ever varies one violated clause at a time. I reproduced this by rerunning `mutation_check.py` myself. Anchor 4 fails: the cases are hand-written pytest and a hand-written mutation harness, not derived from any formal model — no TLA+ spec or spec-double-compiler model exists for `ab_quota_ledger` among what I was permitted to read.

### D2 — complexity: **2**

7 instance-state fields (`quota_ledger.py:52-63`), each with a small traceable set of writers, proportional to the 5 rules / 4 commands / 5 queries the spec declares — anchor 2. Anchor 3 does not apply: `mechanical.json` records `before_tree_label: null` / `"This tree is a greenfield subject. It has no before."` — N is the baseline, not a simplification of anything, so there is no before/after pair to score here.

### D3 — modularity: **0**

No I/O boundary of any kind exists. `__init__` (`quota_ledger.py:65-69`) and `_append` (`quota_ledger.py:156-160`) call `Path.write_text`/`Path.open` directly inside the domain class; `NOTES.md:26-28` states the design choice as "one class, one module, stdlib only" with no port named even in prose. This is anchor 0, not anchor 1 — no boundary is declared anywhere to fail to follow.

### D4 — behavior preservation: **2**

`NOTES.md:30-161`'s clause-by-clause table plus `test_quota_ledger.py:215`'s 200-walk-x-40-op property test enumerate FEATURE.md's behaviors and show each holds — anchor 2. Not anchor 3: hand-written property test and hand-written mutation harness, no model-derived corpus or invariant exists in this track. My own two seeded faults were both caught by both suites, corroborating anchor 2 empirically but not substituting for model-derivation.

### D5 — honesty: **4** (`anchor_reading`: measured)

`NOTES.md:264-280` and `:220-261` name blind spots unprompted (no fsync/crash testing, no concurrency, BFS limited to one tenant quota 0-3) — anchor 2. `NOTES.md:192-215` refuses to certify the declared `close_tenant` clause order as more than "unobservable," backed by a 90,484-state exhaustive search rather than asserting the stronger claim its test table would have let it get away with — anchor 3. Anchor 4 (measured reading): `NOTES.md:170-178`'s own mutation table records `M8 ... SURVIVED` against its own 37-test suite, and `:215` states outright "I have no basis for a claim about mutants I did not write" — a self-measured, unflattering coverage gap the artifact reports rather than suppresses. I verified this figure is real by rerunning `mutation_check.py` myself.

**Refuses to claim (D5):** that its 12-mutant sample or single-tenant BFS constitute a saturation argument.

### Mechanical vs. judgement

No disagreement worth flagging for N specifically; see D's section for the mutation_check.py path-resolution defect that affects both trees identically (its `SHARED_SUITE` lookup never resolves in the real repo layout, so the "shared" column in both `NOTES.md`'s printed table and any live rerun of the script diverge — the script prints `n/a` when actually run, while `NOTES.md`'s table shows specific caught/survived values, meaning that table was not produced by running the script as shipped, at least not from its delivered location).

### Verdict

N is a competently-scoped single-class implementation with real, verified bug-catching evidence and unusually candid self-reporting, but it has no ports/adapters boundary at all (D3=0) and its behavior checks, while thorough, are hand-written rather than model-derived, which caps D1 and D4 below the top of their scales.

### Rejected

- **D1/D4 = 4 for either artifact.** Both artifacts' evidence is genuinely strong (mutation testing, property-based random walks, an exhaustive BFS for one clause), and it was tempting to read "the record names a fault class it still cannot reach" (D1 anchor 4) as satisfied by `NOTES.md`'s own "What I did not do" section. I rejected this because anchor 4 is conjunctive — model-derivation is required *and* stated separately from "names what it cannot reach" — and nothing in this track is model-derived. Crediting rigor-that-isn't-model-derived as if it were would erase the distinction the rubric is drawing.
- **D3 = 1 for N**, on the theory that `NOTES.md`'s prose about "the durable side" and `ledger_lines()` re-reading the file rather than mirroring state amounts to a *declared* boundary that the code then follows loosely. I rejected this: that prose is about R2 (durability semantics), not about a domain/adapter split, and there is no sentence anywhere naming an intended port. Anchor 1 requires a declared boundary to exist and be violated; here none is declared at all, which is the anchor-0 condition.
- **Docking D2 for the missing before/after.** N genuinely cannot clear anchor 3 (no before), and I considered treating that structural impossibility as a reason to look for *some* other simplification-in-place (e.g., the six reason constants, or the frozen dataclasses) to credit. I rejected manufacturing a "before" that doesn't exist — the anchor asks about a specific act (a simplification made and measured), not a general simplicity argument, and N is honestly the baseline, not a revision.
- **Treating the `_append`/single-write-path comment as evidence of a port.** `quota_ledger.py:156-160`'s comment ("there is no seek and no rewrite path in this class") is about R5 (append-only-ness), not about swappability. I did not credit it toward D3.
- **Using the mutation_check.py path bug to lower D5.** The script's `SHARED_SUITE` resolution never finding the real repo root is a real defect, and I considered treating the mismatch between the printed "shared" column and a live rerun as a D5-relevant honesty problem (numbers in the record that don't reproduce). I did not, for two reasons: (1) it's identical in both N and D, so it can't differentiate the pair, which is what D5's comparison here is doing work for; and (2) I have no way to rule out that the author ran the script from a different working directory during development where the path did resolve — the *deliverable's* self-contained runnability is broken, but that's better filed as a build/packaging defect than scored as a dishonesty finding, since nothing in `NOTES.md`'s prose claims the script is directory-independent.
- **Nothing in this pass changed my reading of the artifact tree** — no edits were made to `specs/results/scorecards/reading-discipline/blind/artifact_N/` or `artifact_D/`; all fault-seeding was done on scratch copies under `/private/tmp/.../scratchpad/rd03/`.
