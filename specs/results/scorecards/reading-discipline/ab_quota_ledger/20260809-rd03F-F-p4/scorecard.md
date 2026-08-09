# Scorecard — ab_quota_ledger, artifact `F`, judge pass 4

`run_id`: `20260809-rd03F-F-p4` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

**You are scoring artifact `F`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

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

**Judging practice.** Executed own faults: true. Same fault-seeding campaign as the E card (three seeded faults: a content fault, a rejection-order swap, a lexicographic-sort fault), run in a scratch copy, plus a direct `diff -ru` between `blind/artifact_E` and `blind/artifact_F` and an independent string check of the `"journal_"` substring claim in `REVISION-NOTES.md`. Neither artifact tree was edited in place.

**The headline: is this a simplification?** `diff -ru artifact_E artifact_F` shows zero differences anywhere under `quota_ledger/` or `tests/`. The only new file in F is `REVISION-NOTES.md`, whose own stated Outcome is "I changed nothing." `mechanical.json` on this card carries both trees' measured figures and they are identical in every field — not lower, not higher, identical — which is consistent with, and independently confirms, the zero code diff. **My judgement: this does not constitute "a simplification was made."** D2 anchor 3 requires both that the before/after figures be recorded (true — they're right here) and that a simplification actually happened (false — nothing changed). `REVISION-NOTES.md` documents real investigative work: ten candidate over-engineering patterns examined against the actual code, each left standing with a specific, checkable reason (I independently verified the `Journal` port, both adapters, the `QuotaLedger` subclass, and the duplicated tenant guards it discusses all exist exactly as described). That is a legitimate, evidenced *negative result* — but a negative result is not a simplification, and I am scoring the anchor's text, not the effort behind the conclusion. D2 = 2 for F, same as E, and for the same underlying reason: this pair never actually diverges.

**D1 = 3, D3 = 4, D4 = 2** — identical reasoning and identical evidence to the E card, since the code is byte-identical. See that card's writeup for the fault-seeding detail.

**D5 = 4, anchor_reading = measured.** This is where F earns something E does not. Told to simplify, F refuses to claim the positive verdict it was sent to produce and says plainly it did not simplify — that clears anchor 3 (a refused verdict against an unsupported basis). It clears anchor 4 under the `measured` reading: `REVISION-NOTES.md` reports that `test_the_domain_module_does_not_import_its_adapters`'s assertion `"journal_" not in source` can never fail, because that substring cannot occur in either adapter module name it is meant to guard against. I checked this myself — `file_journal` and `memory_journal` both contain `_journal`, neither contains `journal_` — confirmed vacuous. F found a genuine defect in its own shipped test suite and reported it rather than quietly fixing it or leaving it unremarked. That is an actively investigated, unflattering-to-itself result, not a general disclaimer, which is why I used the `measured` reading rather than `disclosure`.

**Rejected.** I strongly considered D2 = 0 or 1 for F on the theory that recording identical before/after tables and calling it done is close to "measured and ignored" — I rejected 0 because the figures are not ignored, they're read and the absence of change is explicitly reasoned about; I rejected making this a punitive score generally, because the rubric's caveat is about not crediting a *dropped* number, not about penalizing a *stable* one, and F's own complexity was already at anchor-2 quality before the revision pass. I considered giving D2 = 3 anyway on the argument that "a simplification was made" could be read loosely as "a simplification pass was made" (i.e., the *activity* happened, even if its output was null) — I rejected this because the anchor's plain-language subject is the artifact, not the process: "a simplification was made" describes a change to the design, and none occurred. I considered scoring D5 under the `disclosure` reading instead of `measured` — I rejected `disclosure` alone because the vacuous-assertion finding is not a stated limitation in the abstract, it's a specific claim F went and checked; I recorded `measured` for that reason but note a `disclosure`-reading judge would likely still land at 4 via the "I changed nothing when asked to" refusal alone. I did not find, and did not credit, any complexity-number decrease anywhere in the artifact or `mechanical.json` — there isn't one to find. I did not read `references/eval_scorecard.md`, `UNBLINDING*`, the GOAL-product-round tree, any other judge's card, or `arm_a/arm_b/arm_c/revision/dispatch/seeded_faults.toml/check_catalogue.py`; I did look at directory listings under `examples/validation/ab/` while orienting (I saw a `model/QuotaLedger.tla` file exists) but did not open its contents, matching the same restraint `REVISION-NOTES.md` itself describes.
