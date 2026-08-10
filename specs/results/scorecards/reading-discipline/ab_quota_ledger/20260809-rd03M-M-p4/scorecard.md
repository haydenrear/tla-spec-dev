# Scorecard — ab_quota_ledger, artifact `M`, judge pass 4

`run_id`: `20260809-rd03M-M-p4` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

**You are scoring artifact `M`.** That label is opaque on purpose: it is not the arm name, and the mapping is not in this directory. Do not go looking for it. If you learn which arm you hold, say so in the verdict — a disclosed leak is recorded, never grounds to discard a card.

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

**Model:** `claude-sonnet-5`. **Commit:** `f52be89c7e494fc98243702c5f4a4d26d5001af9`.

**Judging practice:** `executed_own_faults: true`. Same scratch-copy protocol as on Z, run separately against M: baseline confirmed (22 own / 28 shared), then two seeded faults, both in scratch copies only. (1) The same `reserve()` ordering swap I ran on Z, unaffected by the revision — same result: shared suite 28/28, M's own ordering test failed. (2) A cross-tenant guard fault: I replaced `close_tenant`'s `if any(held.tenant == tenant for held in self._reservations.values()):` (`quota_ledger.py:197`) with `if self._reservations:`, independently reproducing the exact mutation `REVISION-NOTES.md:92-95` describes the *author* running. Shared suite stayed 28/28 green; 3 of M's 22 own tests failed, including `test_another_tenants_live_reservation_does_not_block_a_close` (`test_quota_ledger.py:196-205`), the test the revision added specifically for this scenario. This independently confirms the revision's central claim rather than repeating it.

**Scores:** D1=3, D2=3, D3=0, D4=2, D5=3.

- **D1 (3):** same content-assertion anchor-2 evidence as Z, plus two independently-run anchor-3 faults (ordering, and the cross-tenant guard above) — a stronger anchor-3 case than Z's single fault, but anchor 4 still unreachable (nothing model-derived).
- **D2 (3) — the headline dimension this round.** A real, small simplification was made, and I verified it rather than reading the claim. What got simpler: Z's `_Tenant` (`quota_ledger.py:79-92`, Z tree) carries 5 fields; I confirmed by reading the code (not the notes) that `quota` is written once and never read anywhere in the module, and `outstanding` is written from 3 sites (`reserve`/`commit`/`release`, Z lines 164/174/187) to serve exactly 1 reader, a fact already fully recoverable from `self._reservations`. M's `_Tenant` (`quota_ledger.py:79-94`) drops both — 3 fields left, each one query's answer, no field a cache of another. How behavior survived: I did not trust `REVISION-NOTES.md:23-60`'s equivalence argument — I mutated the collapsed guard myself (see judging practice) and confirmed the shared suite cannot tell the difference but M's own directed test can. Both before/after complexity tables are recorded in `mechanical.json` per the anchor's literal requirement. **A finding for the record:** the mechanical complexity instrument is nearly blind to this change — `branch_points` (11→11), `callables` (14→14), `classes` (5→5), even `instance_state` (4→4) are unchanged; only `code_lines` (158→156) and `total_lines` (223→222) move by 1-2 lines. The instrument does not appear to count dataclass field count or write-site fan-in, so a real reduction in duplicated state is nearly invisible to it — the measurement/judgement disagreement the mechanical block exists to surface. **A second, unscored finding:** the removed counter was not free. With a per-tenant counter, a cross-tenant close bug was structurally impossible to write; with the counter gone, that bug is one plausible line away and is caught only because a human wrote a directed test for it. A structural guarantee was traded for a test-coverage guarantee — real, and currently covered by evidence I ran myself, but a trade, not a pure win. Anchor 4 unreachable: it requires D4≥3, and D4 is capped at 2 (below) for lack of model-derivation, so even my strongest possible evidence (a judge-run, caught, deliberate behavior-break) cannot lift this past 3 under the rubric's own gate.
- **D3 (0):** unchanged from Z — the revision touched only `_Tenant`'s fields and the `close_tenant` guard, not the I/O boundary. Same direct filesystem calls, same zero declared interfaces.
- **D4 (2):** `REVISION-NOTES.md:16-19`'s claim (28 shared / 22 own, all 21 original Z tests retained) independently confirmed by my own baseline run. Solid anchor 2. Not anchor 3: the mutation check the author describes (`REVISION-NOTES.md:82-99`), which I independently reran, is real evidence of a caught behavior-break, but a mutation check is not a model-derived check, and rerunning it myself does not manufacture model-derivation that isn't there. I have the single strongest piece of D4 evidence available this round and still capped the score at 2, because anchor 3's gate (model-derivation) is a different bar than "was a break shown to be caught," and this project has no path to the former with hand-written Python alone.
- **D5 (3), anchor_reading=disclosure:** M's `NOTES.md` is unedited (confirmed byte-identical to Z's), carrying forward the same anchor-2/3 disclosures, plus `REVISION-NOTES.md:102-152` naming five specific candidate simplifications considered and rejected with reasons, including "This is the candidate I am least sure about" (lines 130-137). Considered anchor 4 via `REVISION-NOTES.md:116-124`'s admission that the `Reason`/`REASONS` duplication ("the 'two places that must change together' smell") was knowingly left in — genuinely tempting — but rejected it because the admission is framed as a justified trade-off with a named reason (an external reader depends on `REASONS`), not a result the artifact discovered was wrong; under the "measured" reading that is anchor-2/3 material, not anchor 4. Took the lower.

**What I rejected:** D2=2 (I found this too conservative once I'd independently verified the simplification's safety myself rather than just reading the claim — real state-representation collapse with recorded before/after figures clears anchor 3's literal bar). D2=4 (blocked cleanly by D4<3; did not round up despite unusually strong D4-adjacent evidence). D1=4 and D4≥3 (no model-derivation anywhere in this project — the strength of my own executed mutation evidence does not substitute for the anchor's specific requirement). D5=4 (the one clearly self-critical admission left in the code is framed as a considered trade, not a discovered flaw).
