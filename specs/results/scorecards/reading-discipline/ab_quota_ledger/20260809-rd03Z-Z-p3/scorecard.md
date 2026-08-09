# Scorecard — ab_quota_ledger, artifact `Z`, judge pass 3

`run_id`: `20260809-rd03Z-Z-p3` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

**You are scoring artifact `Z`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

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

**Model:** `claude-sonnet-5`. **Commit:** `f52be89c7e494fc98243702c5f4a4d26d5001af9`.

**Scores:** D1=3, D2=2, D3=1, D4=2, D5=4 (anchor_reading: disclosure).

**Judging practice:** `executed_own_faults: true`. I copied both artifact_Z's and artifact_M's `quota_ledger.py` + `test_quota_ledger.py` into scratch and ran five seeded-fault experiments against both trees (full list in `judging_practice.what_was_run` in `scorecard.json`): a wrong-running-total content fault (caught by the shared suite on both, identically — D1 anchor 2 evidence); an order-swap fault between the `tenant_closed` and `amount_not_positive` checks in `reserve()` (invisible to the shared suite on both, caught only by each artifact's own `test_closed_beats_a_bad_amount_and_beats_quota` — D1 anchor 3 evidence); and, specific to the pair, the exact cross-tenant close-guard mutation `REVISION-NOTES.md` on M's tree claims to have run (`if self._reservations:` in place of the tenant-scoped guard) — I reproduced it myself rather than trusting the note, and it held: shared suite 28/28 green, M's own new test fails. I also tried two analogues of that same fault against Z's counter-based design and found the closest one is caught by the *shared* suite alone (a materially easier bug to trip than M's), which became direct evidence for the D2 rationale below rather than a side note.

**D1 (bug detection), both 3:** Content faults are caught by adapters asserting values, not shape (anchor 2, both). An ordering fault between overlapping rejection checks is caught only by each artifact's own hand-written tests, never the shared corpus, which has no test case combining a closed tenant with a bad amount (anchor 3, both). Anchor 4 needs the catching cases to be model-derived; nothing in this tree is — no TLA+ spec, no generated corpus, `mechanical.json` records zero declared interfaces and no generator. Hand-written pytest, however thorough (and it is: a 600-step property test naming R1–R5 explicitly), cannot clear anchor 4's first clause.

**D2 (complexity) — the headline, Z=2, M=3:** I read `_Tenant`'s field list against what M's revision proved. Z's `_Tenant` carried `quota` (written once at construction, read by no code path — only by tests, against their own copy of the input) and `outstanding` (a hand-maintained duplicate of a fact already recoverable from `self._reservations`, kept in sync at three call sites: `reserve` +1, `commit` -1, `release` -1). M removes both; every remaining field is now exactly one query's answer. I verified this is not just a line-count illusion: I seeded the fault M's own notes describe catching — replacing the new tenant-scoped guard with a non-scoped `if self._reservations:` — and independently confirmed it breaks only M's own tests (never the shared suite), so the guard's tenant-scoping is load-bearing and covered, not decorative. **What got simpler:** two representations of "this tenant holds a live reservation" collapsed to one, removing a hand-synchronization obligation at three call sites and a wholly-dead field. **How the behavior survived it:** the removed counter's sole reader (`close_tenant`'s guard) now reads the canonical table directly; I confirmed by mutation that a plausible way to get that migration wrong (dropping the per-tenant filter) is caught, and is caught by exactly the new test M's revision notes claim it is. This clears D2 anchor 3's literal bar (a simplification was made, and `mechanical.json` on M's card carries both before and after `totals_code_only` tables) and is a genuine finding, not a restated claim, because I reran the check myself rather than reading the note and moving on. It is **capped at 3, not 4**: anchor 4 needs D4 ≥ 3, and D4 is 2 for both (see below) because nothing here is model-derived. Z gets 2, not 3: there is no simplification event in Z's own history to measure a before/after on — Z is the origin point — so anchor 3 cannot apply to Z regardless of the pair's outcome; and I do not read Z as a clean anchor-2 pass either, given the later-proven redundancy, though I score it there because the anchor's literal text (no god-state, no variable written from everywhere) is met and I try not to score anchors more strictly than they are written. **Measurement vs. judgement disagreement, worth flagging per the rubric's own rule 7:** `mechanical.json`'s structural counts (`branch_points`, `callables`, `classes`, `instance_state`, `effectful_calls`) are *identical* between Z and M; only `code_lines` (158→156) and `total_lines` (223→222) move, by one and two lines respectively, against a longer docstring that partially offsets the two deleted field lines. The descriptor is nearly blind to a change I judge as real and behavior-relevant (state-redundancy removal), because it counts structure at the module/class level, not per-field duplication. A reader trusting only the mechanical block would see almost nothing happened; a reader trusting only the D2 caveat's warning ("a drop in a complexity number is not evidence on its own") might wrongly discount M's change as noise. Both readings would be wrong here; the number and the finding point in different directions in magnitude even though they agree in sign.

**D3 (modularity), both 1, unaffected by the diff:** Neither tree separates domain from I/O in a ports-and-adapters sense — `QuotaLedger` imports `os`/`Path` directly and its `_append` method calls `open()`/`os.fsync()` inline. There is a real internal write-chokepoint, named in prose in `NOTES.md`, which stops this from being anchor 0. But nothing is swappable: no interface, no injected dependency (`mechanical.json`: `declared_interfaces: 0` on both). FEATURE.md explicitly leaves this unspecified, so it is not a defect against the spec, only a low score against this dimension. Identical for Z and M — the diff never touches the I/O boundary.

**D4 (behavior preservation), both 2:** For M this is well-supported: `REVISION-NOTES.md` enumerates, per removed field, which existing tests already covered the behavior it carried, states a before/after pass count, and — I confirmed independently — the guard's mutation-sensitivity claim holds. For Z, which has no "before," I read the dimension as asking whether Z's own required behaviors are enumerated and shown to hold against the spec, which its 600-step property test does explicitly (R1–R5 named and asserted every step). Neither clears anchor 3: every check in this tree is hand-written pytest, nothing model-derived.

**D5 (honesty), both 4, disclosure reading:** Both `NOTES.md` (identical in both trees) and, for M, `REVISION-NOTES.md` name blind spots unprompted and decline to silently resolve genuine ambiguities — most concretely, non-integer reservation amounts are neither coerced nor rejected, and both notes say so plainly rather than picking a silent behavior. M adds its own unflattering admission: "This is the candidate I am least sure about" regarding whether the commit/release shared prologue should have been extracted. I scored under the **disclosure** reading, not measured: neither tree reports a self-run check whose *result* was unflattering to itself (M's one described mutation test is reported as passing, i.e. is flattering); what both report is a stated limitation, which is anchor-2/3 material read generously up to anchor 4 under the disclosure reading the rubric explicitly permits.

### What I rejected

- **D2=4 for M.** The rubric's anchor 4 requires D4≥3 textually, and I take that literally rather than treating "the check held under my own mutation" as morally equivalent to a model-derived check. It is not — it is still hand-written pytest; I just ran it myself instead of trusting the note. Tempting, because I did more verification work on this claim than on almost anything else in the pair, but doing the verification myself does not upgrade the *kind* of check it is.
- **D2=1 for Z.** I seriously considered this, on the theory that a design later proven to carry two removable fields cannot be called "proportional to its behavior." I rejected it because anchor 2's actual text is narrower than that (no god-state, no variable written from everywhere) and Z meets it as written; scoring below what the literal anchor text supports, just because I know something a first reader of Z alone would not, seemed like importing information from M into a card that is supposed to judge Z as an artifact. I flagged the tension in the rationale instead of resolving it by fiat downward.
- **D3=2 for either.** The single-write-method discipline (`_append`) is real and I almost credited it as "something identifiable as a port." I rejected this because nothing is actually swappable — no interface exists to swap through, and the round-2 caveat ("import topology is not modularity") reads to me as a general warning against crediting structure that looks port-shaped without being swap-tested. I did not attempt to write a fake durable adapter and swap it in — that would have been the honest way to earn a 2 or 3, and I did not do it, so I did not award it.
- **A same-file citation for D1 anchor 4's "names a fault class it still cannot reach."** I looked for this in both `NOTES.md` and `REVISION-NOTES.md` and did not find either tree naming a fault class its *own* suite cannot catch (both discuss *ambiguities*, not *coverage gaps*). I did not manufacture one on the artifacts' behalf.
- **Treating the identical `mechanical.json` structural counts as evidence M's change is not real.** The rubric's own caveat cuts one way (a metric drop is not proof of improvement); I nearly let the *lack* of a drop argue the reverse (no improvement happened at all). I rejected that inference too, because I have direct, independently-reproduced behavioral evidence (the mutation test) that the removed state was genuinely redundant — the metric's silence here is a limitation of the instrument's granularity, not counter-evidence.
- **Reading `Z`/`M` as `arm A`/`arm B` or similar.** I did not attempt to infer or go looking for which experimental arm produced either tree; I have no basis to report a leak.
