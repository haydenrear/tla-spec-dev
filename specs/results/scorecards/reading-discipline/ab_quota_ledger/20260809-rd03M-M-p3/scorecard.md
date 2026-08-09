# Scorecard — ab_quota_ledger, artifact `M`, judge pass 3

`run_id`: `20260809-rd03M-M-p3` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

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

## Judge pass 3 — filled

**Model:** `claude-sonnet-5`. **Commit:** `f52be89c7e494fc98243702c5f4a4d26d5001af9`.

**Scores:** D1=3, D2=3, D3=1, D4=2, D5=4 (anchor_reading: disclosure).

**Judging practice:** `executed_own_faults: true`. Same five-experiment campaign described on the `Z` card, run against both trees together (full list in `judging_practice.what_was_run` in `scorecard.json`). The one specific to this card: `REVISION-NOTES.md:90-95` claims that mutating the close guard from the new tenant-scoped `any(held.tenant == tenant for held in self._reservations.values())` to a bare `if self._reservations:` passes the shared suite 28/28 and fails `test_another_tenants_live_reservation_does_not_block_a_close`. I made that exact edit myself in a scratch copy rather than trusting the prose, and reran both suites: the claim held exactly as stated, and also broke `test_every_declared_reason_is_reachable_and_no_other_is` and the 600-step property test, which the note does not mention but which are additional independent confirmation.

**D1 (bug detection), 3:** Same structure as Z — content faults caught by the shared suite (anchor 2); an order-swap fault in `reserve()` caught only by this artifact's own tests (anchor 3). Specific to M: the cross-tenant close-guard fault is a second, independently-confirmed anchor-3 case — a fault class (leakage across tenants at `close_tenant`) the shared corpus structurally cannot reach because it never has two tenants holding live reservations simultaneously against a close call on one of them. Anchor 4 fails on the model-derivation clause: everything here is hand-written pytest.

**D2 (complexity) — the headline, 3:** This is the card the round's central question lands on. **What got simpler:** `_Tenant` lost two fields — `quota` (write-once, read-never, `quota_ledger.py` diff at `_Tenant`'s definition) and `outstanding` (a hand-synchronized duplicate of `len({r for r in reservations if r.tenant == this})`, maintained at three call sites: increment in `reserve`, decrement in `commit`, decrement in `release`). Every remaining field of `_Tenant` — `available`, `committed`, `closed` — is now exactly one query's answer; no stored value is a cache of any other. `close_tenant`'s guard changed from reading the counter to scanning `self._reservations` directly (`quota_ledger.py:197`), which is the *only* place the removed field's behavior needed to move to, and it moved there completely — I checked there is no other reader of the old counter left dangling. **How the behavior survived it:** I did not accept `REVISION-NOTES.md`'s mutation-test claim as read; I reproduced it. The claim is exactly right — replacing the tenant-scoped guard with a non-scoped one passes the *shared* suite unchanged (28/28) and fails only tests inside this artifact's own suite, meaning the tenant-scoping the revision introduced is both correct and covered, not merely present. `mechanical.json` on this card carries both the before (`before_totals_code_only`, labeled `Z`) and after (`totals_code_only`) tables side by side per the rubric's instruction, satisfying anchor 3's literal requirement that both figures be recorded. **Capped at 3, not 4:** anchor 4 needs D4≥3; D4 is 2 here because the covering check, however well-targeted, is hand-written pytest, not a model-derived corpus or invariant. **Disagreement between measurement and judgement, which the rubric asks me to flag when it happens:** almost none of `mechanical.json`'s structural counts moved — `branch_points`, `callables`, `classes`, `instance_state` (4 in both), `effectful_calls` are byte-identical between the before and after tables; only `code_lines` (158→156, a net drop of 2 despite deleting more than 2 lines of field declarations, because the `_Tenant` docstring grew) and `total_lines` (223→222) moved at all, and barely. If I had scored from the mechanical block alone I would have called this noise and stayed at D2=2. I did not, because I have direct behavioral evidence (the reproduced mutation test) that a real piece of redundant, hand-synchronized state was removed and that removal is covered. The instrument's near-silence here is a statement about what it measures (module/class-level structure counts), not about whether a simplification happened.

**D3 (modularity), 1, unaffected by the revision:** The diff between Z and M never touches the I/O boundary — `_append` still calls `open()`/`os.fsync()` inline inside the domain class, same as Z, no interface introduced. Full reasoning on the Z card; identical here.

**D4 (behavior preservation), 2:** This is the strongest-documented dimension in this tree. `REVISION-NOTES.md:16-19` states the before/after pass counts (28/28 shared, 21→22 own, all originals retained) and `:33-46` enumerates, field by field, which existing tests already covered the behavior each removed field carried — a genuine per-behavior enumeration, not just a pass/fail count (anchor 2, cleanly met, better-documented than Z's card). It does not reach anchor 3: the check that caught my reproduced fault is hand-written pytest, and `REVISION-NOTES.md` does not claim otherwise — it never asserts the check is model-derived.

**D5 (honesty), 4, disclosure reading:** `REVISION-NOTES.md` keeps and restates all three of `NOTES.md`'s original unresolved ambiguities rather than quietly fixing or dropping them (`:165-171`), explicitly declining to "fix" the non-integer-amount case it inherited. It adds a genuinely new, self-critical admission: "`This is the candidate I am least sure about`" (`:134-137`) about whether the commit/release shared prologue should have been extracted — a live, stated uncertainty about its own judgement call, not a hedge on someone else's ambiguity. It also flags that `NOTES.md` is now stale in one section and states plainly why it was deliberately left that way rather than silently patched (`:158-164`) — disclosing a known inconsistency in its own delivered artifact instead of cleaning it up invisibly. Scored under **disclosure**, not measured, for the same reason as Z: the one self-run check this tree reports (the mutation test) is reported as *passing* — a flattering result — so there is no measured-unflattering-result to point to; what earns the 4 is the stated limitation.

### What I rejected

- **D2=4.** Same reasoning as noted on the Z card: I take "D4≥3" in anchor 4's text literally. Running the mutation test myself instead of reading about it makes the *evidence* better, not the *kind* of check different — it is still hand-written pytest, not model-derived. I was genuinely tempted here, more than on Z's card, because the verification I did is exactly the kind of independent confirmation the rubric rewards elsewhere; I held the line anyway.
- **Crediting the near-zero `mechanical.json` delta as evidence against a simplification having occurred.** Considered seriously — the rubric's own caveat about drops in complexity numbers cuts toward suspicion of *any* complexity claim, and here there is barely a drop at all to be suspicious of. I rejected using this as a reason to lower D2, because I am not relying on the metric drop as my evidence — I am relying on the reproduced mutation test and the direct code-level argument (one representation of "live reservation" instead of two). The metric's silence is a finding about the metric (recorded above), not a veto over my own evidence.
- **D3=2 or 3, on the strength of `_append` being the sole write site.** Same rejection as on Z's card, for the same reason: nothing is swappable, and I did not build and swap a fake adapter myself, which is the only way I would have trusted a higher score here.
- **Reading the new test `test_another_tenants_live_reservation_does_not_block_a_close` as itself evidence of D1 anchor 4.** It is model-... no — it is hand-written, purpose-built after the fact to target exactly the fault the revision's own change could introduce. That is good test design, but it is not derivation from a model, and I did not let the fact that it is unusually well-targeted substitute for that clause.
- **Reading `Z`/`M` as arm labels or inferring which arm produced which tree.** Did not attempt it; no leak to disclose.
