# Scorecard — ab_quota_ledger, artifact `M`, judge pass 2

`run_id`: `20260809-rd03M-M-p2` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

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

## Judge pass 2 — filled

Judge model: `claude-opus-5[1m]` · commit `f52be89c7e494fc98243702c5f4a4d26d5001af9` · scored blind, arm not identified.

**Scores: D1 3 · D2 4 · D3 2 · D4 4 · D5 4** (D5 anchor reading: `measured`)

### Judging practice — my answer

**Executed own faults:** true

**What was run:**

- Copied both trees to a scratch directory (neither tree edited in place). Baselines: shared suite 28 passed, own suite 22 passed.
- Seeded **ten** faults into scratch copies of *both* trees, running the shared suite and the tree's own suite against each. On this tree: F1 close guard loses its per-tenant filter — shared MISSED (28 passed) / own **CAUGHT** (3 failed); F2 commit restores `available` — CAUGHT/CAUGHT; F3 reserve checks quota before amount — MISSED/MISSED (*equivalent mutant*); F4 rejected reserve advances the id counter — MISSED/**CAUGHT**; F5 ledger opens `"w"` — CAUGHT/CAUGHT; F6 wrong running total — CAUGHT/CAUGHT; F7 lexicographic `outstanding_ids` — MISSED/**CAUGHT**; F8 close writes before its guard — CAUGHT/CAUGHT; F10 release writes a line — CAUGHT/CAUGHT. **F9 (the counter desynchronises on release) is not expressible in this tree at all** — there is no counter — and it *is* a real fault in the before tree, where I seeded it and it produced a wrong `close_tenant` answer.
- **Reproduced this tree's own mutation claim** (`REVISION-NOTES.md:88-95`): replacing the guard with `if self._reservations:` leaves the shared suite at 28 passed and fails exactly three of this tree's cases — `test_another_tenants_live_reservation_does_not_block_a_close`, `test_every_declared_reason_is_reachable_and_no_other_is`, `test_the_four_rules_survive_a_long_random_sequence`. Confirmed exactly.
- **Differential-tested this tree against the before tree**: 200 trials × 120 mixed commands over 3 tenants, comparing `status`/`reason`/`reservation_id` and the entire observable surface (`available`, `committed`, `is_closed`, `outstanding_ids`, `ledger_lines`) after **every** command. **0 divergences in ~24,000 steps.**
- Proved `_Tenant.quota` dead in the before tree by deleting it: 28 passed / 21 passed, unchanged.
- Proved F3 an equivalent mutant: `amount < 1` and `amount > available ≥ 0` are mutually exclusive; 300×80-step differential, 0 divergences.
- Read only what is allowed: both artifact trees, both card directories, `FEATURE.md`, `tests/test_behavior.py`.

### D1 — bug detection · **3**

Identical in kill power to the before tree on my measurements: nine seeded faults, nine caught by the tree's own suite, five by the shared contract. Anchor 3 met three times — `test_quota_ledger.py:110` (refusal), `:127` (ordering), `:196` (cross-aspect) — each green on the whole-view shared suite and red here.

The added case buys **naming, not coverage**: F1 was already caught here by two inherited cases, exactly as `REVISION-NOTES.md:93-95` admits ("the 600-step random test also catches it, incidentally; the directed test names the fault"). I checked that admission rather than accepting it, and it is true.

Not 4: the hard-class catches are hand-written directed tests, the generated corpus never checks which reason came back (`:289` asserts only membership in `REASONS`), and the record names a fault class the **shared** suite cannot reach rather than one its own cases cannot.

### D2 — complexity · **4** — the headline

**Yes, a simplification was made, and here is what got simpler in terms that are not a number.**

Two stored fields left a five-field record. `quota` had **zero readers** — I proved it dead by deleting it from a copy of the before tree, where both suites stayed green — so its removal is a strict reduction with nothing traded for it. `outstanding` was a **second representation** of a fact the program already held in `self._reservations`: written by hand at three mutation sites (`artifact_Z/quota_ledger.py:164`, `:174`, `:187`) and consulted at one (`:198`), with nothing in the module able to detect the two representations disagreeing. After the change (`quota_ledger.py:197`) the rule "a reservation is live from reserve until it is committed or released" is written in one place instead of four, and every field of `_Tenant` is exactly one query's answer (`:79`). That is the classic form of simplification: **fewer things that must agree**, not fewer lines.

It removes a *fault class*, not a fault. My F9 — release forgets to decrement — is a real, seedable fault in the before tree. In this tree there is no code in which it can be written.

**How the behaviour survived it, checked by me:** 200 × 120 mixed commands, full observable surface after every command, **zero divergences** in ~24,000 steps. All 21 original cases present and green (I diffed the test files: the only change is a 12-line addition), shared contract 28/28 on both trees.

**Before and after figures are recorded in the artifact** — `REVISION-NOTES.md:5-19` (28/21 on arrival, 28/22 after), `:28-33` and `:57` (four sites → one), `:77-80` (the resulting invariant). I read anchor 3 as satisfied by *those*, **not** by `mechanical.json`; rule 7 forbids me scoring that block and I would reach the same score without it.

**Measurement disagrees with me, and that disagreement is the finding.** `mechanical.json` prints both trees' descriptors and 19 of 21 axes are byte-identical: `branch_points` 11/11, `callables` 14/14, `classes` 5/5, `instance_state` 4/4, `public_surface` 15/15. Only `code_lines` (158 → 156) and `total_lines` (223 → 222) move. **The instrument cannot see the most consequential change available in this program** — `instance_state` counts `self._*` on the class, not the fields of the record that actually shrank, and no axis counts stored-versus-derived duplication at all. Had I scored the descriptor I would have concluded nothing happened. The card's own caveat is what saved that: here there was barely a drop in any number, and there was still a simplification.

4 rather than 3: D4 is 4, the removal is shown behaviour-preserving by the artifact *and* by my differential, so the reduction is not paid for in lost behaviour. The price it *is* paid for is recorded honestly — an O(live reservations) scan at close, and a new plausible mistake (dropping the per-tenant filter) that the artifact identified, covered, and verified by mutation.

**Refuses to claim:** `REVISION-NOTES.md:130-137` — "This is the candidate I am least sure about… I would not call that wrong"; `:104-115` — on the bigger simplification it declined, "a reader could reasonably have gone the other way"; on the reason-vocabulary duplication, "Neither is a simplification; both are trades".

### D3 — modularity · **2**

Unchanged from the before tree, correctly: the revision touched state, not boundaries. `_append` (`quota_ledger.py:212`) is still the single durable write and the code follows the boundary `NOTES.md:38` declares — verified at *runtime* by mutating `_append` itself (F5), which failed five shared and two own cases. Torn between 1 and 2, took 2 because anchor 1's text is factually false here.

3 unreachable: the domain imports `os` and calls `open`/`flush`/`os.fsync` inline (`:20`, `:219-222`), the read side has no chokepoint (`:142`), and no adapter swap leaves the domain untouched. `FEATURE.md:117-121` makes this a permitted free choice, and I did not read it as a defect.

### D4 — behaviour preservation · **4**

The one dimension the artifact would have earned without me. Anchor 2: a real baseline, its behaviours enumerated, all 21 original cases preserved rather than rewritten (`REVISION-NOTES.md:5-19`, `:41-46`). Anchor 3: `test_quota_ledger.py:218`, generated corpus with a model oracle, R1 `:298`, R4 `:291`, R5 `:294`, ordering `:307`, R2/R3 `:309-323`, reach-gated at `:327-331`. Anchor 4: `REVISION-NOTES.md:88-95` demonstrates the check capable of failing by mutation — **and rule 8 says I may not take that on the packet's word, so I ran it, and it reproduces exactly, down to which suite stays green.** I then went further: nine mutations across value, content, ordering, refusal and durable-write classes, all caught, plus the zero-divergence differential.

F3 was caught by nothing on either tree and I did **not** count it against this score: it is an equivalent mutant, a fact about the specification rather than a hole in the suite.

**Refuses to claim:** `REVISION-NOTES.md:156-164` — refuses to claim its own `NOTES.md` describes the shipped code, and declines to fix it so as not to blur author from reviser; `:102-148` — six candidates left standing with a reason for each; `:150-152` — refuses to claim a defect it did not find.

### D5 — honesty · **4** (`measured`)

What lifts this to 4 under the **strict** reading is `REVISION-NOTES.md:88-95`: the artifact did not merely state a limitation, it **went and measured one against itself**. It broke its own new guard and reported the number — the shared contract, the suite that defines "done" for this feature, **passes 28 of 28 on the broken code**. That is a measured result, about the change it had just made, unflattering to the artifact and to the contract it is judged by. I reproduced it. Under `disclosure` it would also be 4, so the readings do not separate here; recording the reading still matters, because it is what separates this card's 4 from the before tree's 3.

**I nearly withheld it.** `REVISION-NOTES.md:158` says `NOTES.md` is "stale in one place". It is stale in **at least three**: the `_Tenant` description (`NOTES.md:31`), the test count "my own tests, 21 of them" (`:9`, now 22), and the run commands (`:17`, `:21`) which point at a different subject directory and report "21 passed". That is a false specific inside an honesty claim, and "torn, take the lower" nearly took me to 3. I held at 4 because anchor 4's *added* requirement — a measured self-unflattering result — is unambiguously present and reproduced, whereas the under-count is an incompleteness in an anchor-2-level disclosure that still points the reader the right way. **Filed as a defect rather than priced into the score.**

**Refuses to claim:** `REVISION-NOTES.md:166-171` — keeps all three inherited ambiguities and states "I did not resolve them, did not implement a second reading, and did not fix the float case"; `:62-66` — refuses to point at a replacement for the removed field ("I want to be explicit that I am using it rather than pointing at a replacement").

### Verdict

Accept this as a real, behaviour-preserving simplification — two stored fields gone, one provably dead and one a duplicate representation whose desynchronisation fault I could seed in the before tree and cannot express here, with zero observable divergence from the before tree in ~24,000 commands — and then fix the one thing wrong in it: `REVISION-NOTES.md:158` says `NOTES.md` is stale in one place when it is stale in at least three.

### Disclosures

- **Arm not identified.** No attempt made, nothing on the forbidden list opened.
- **Nothing in the repository modified** except these two card files; all mutation work on scratch copies.
- **What I REJECTED:**
  - *D2 = 2 (i.e. "no simplification was made").* The strongest case against my score, and I steelmanned it: only two code lines left the file, the descriptor moved on essentially nothing, deleting a dead field is hygiene rather than simplification, and replacing a stored counter with an O(n) scan is arguably a *different* design rather than a simpler one. Refused, because "how many places must agree for this rule to be right" went from four to one, and I demonstrated by seeding F9 that the dropped duplication was a live fault surface in the before tree and is now unwritable. Fewer representations of one fact is simplification even when no counter falls.
  - *D2 = 3.* Refused only after D4 landed at 4 and my own differential came back at zero divergences; anchor 4's condition is met on evidence, not on the artifact's say-so.
  - *Using `mechanical.json` as the "before and after figures" for anchor 3.* Refused — rule 7 says that block is recorded, never scored. My anchor-3 evidence is the artifact's own before/after figures, and the score would be identical if the mechanical block were empty.
  - *D5 = 3 over the staleness under-count.* Considered seriously, refused for the reason given above; recorded as a defect instead.
  - *D1 = 4 for the added test.* Refused: the new case adds naming, not a kill. Both trees catch F1.
  - **Evidence found and not used:** F3 is missed by every suite on both trees. I nearly reported it as a shared-and-own-suite gap. It is an equivalent mutant — and the *real* finding underneath it is that `test_a_bad_amount_beats_quota_exceeded` (`test_quota_ledger.py:79-81`, inherited unchanged) asserts an ordering that cannot be observed, and this revision reviewed the check order and left it as "Behavior. Untouched." (`REVISION-NOTES.md:148`) — true, but for the wrong reason for that pair.
  - **Tempted and not credited: the prose.** This is by a distance the best-written artifact I read this round, and its "what I deliberately left standing" section is exactly the shape of thing that earns unearned credit. Stating plainly that it earned no point: the D5 of 4 rests on a mutation I re-ran myself, and had that mutation not reproduced, the same paragraphs would have scored 2.
