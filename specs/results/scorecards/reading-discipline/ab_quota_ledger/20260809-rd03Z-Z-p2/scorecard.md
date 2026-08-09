# Scorecard — ab_quota_ledger, artifact `Z`, judge pass 2

`run_id`: `20260809-rd03Z-Z-p2` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

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

## Judge pass 2 — filled

Judge model: `claude-opus-5[1m]` · commit `f52be89c7e494fc98243702c5f4a4d26d5001af9` · scored blind, arm not identified.

**Scores: D1 3 · D2 2 · D3 2 · D4 4 · D5 3** (D5 anchor reading: `measured`)

### Judging practice — my answer

**Executed own faults:** true

**What was run:**

- Copied both trees to a scratch directory (neither tree edited in place). Baselines: shared suite 28 passed, own suite 21 passed.
- Seeded **ten** faults by string substitution into scratch copies, running the shared suite *and* the tree's own suite against each:

| fault | shared suite | own suite |
|---|---|---|
| F1 close guard loses its per-tenant filter | MISSED (28 passed) | **CAUGHT** (2 failed) |
| F2 commit restores `available` | CAUGHT | CAUGHT |
| F3 reserve checks quota before amount | MISSED | MISSED — *equivalent mutant, see below* |
| F4 a rejected reserve advances the id counter | MISSED (28 passed) | **CAUGHT** |
| F5 ledger opens `"w"` instead of `"a"` | CAUGHT | CAUGHT |
| F6 COMMIT line prints amount as running total | CAUGHT | CAUGHT |
| F7 `outstanding_ids` sorts lexicographically | MISSED (28 passed) | **CAUGHT** |
| F8 close writes CLOSE before its guard | CAUGHT | CAUGHT |
| F9 release forgets to decrement the counter | CAUGHT | CAUGHT |
| F10 release writes a ledger line | CAUGHT | CAUGHT |

- Proved F3 is an **equivalent mutant**: `amount < 1` and `amount > available` are mutually exclusive because `available` is never negative, so the two checks can never both fire. A 300×80-step differential against the mutant produced 0 observable divergences.
- Proved `_Tenant.quota` is **dead**: deleted the field in a scratch copy; shared 28 passed, own 21 passed, unchanged.
- Executed the disclosed float case: `reserve("acme", 2.5)` is accepted, writes `COMMIT acme 2.5 2.5`, leaves `available` at 7.5. Grepped all three suites: **no test anywhere exercises a non-integer amount.**
- Read only what is allowed: both artifact trees, both card directories, `FEATURE.md`, `tests/test_behavior.py`.

### D1 — bug detection · **3**

Nine of nine behaviourally observable seeded faults caught by this tree's own suite; five by the shared contract. Anchor 2 on content assertions: `test_quota_ledger.py:40` asserts the file's exact bytes. Anchor 3 three times over, each verified by execution rather than read off the notes — `test_quota_ledger.py:110` (refusal / before-state, F4), `:127` (ordering, F7), `:91` (cross-aspect, F1), all red here while the shared 28-case suite stays green. The model-shadowed 600-step sequence at `:206` independently caught F1, F7 and F9, and asserts its own reach at `:315`.

Not 4: the cases reaching the hard classes are hand-written directed tests, and the one generated corpus never checks *which* reason came back (`:277` asserts only membership in `REASONS`), so reason-ordering is reached exclusively by hand. The record names unresolved ambiguities but not a fault class its cases cannot reach.

### D2 — complexity · **2**

Proportional at module level: four commands mapping one-to-one onto the spec's commands, one write chokepoint (`quota_ledger.py:213`), eleven branch points, no god-state, full validation before mutation so R4 holds by construction (`:145`).

Two of `_Tenant`'s five fields are not behaviour: `quota` (`:90`) has no reader anywhere — proved by deletion — and `outstanding` (`:92`) is a second representation of a fact already in `self._reservations`, written at `:164`, `:174`, `:187` for one reader at `:198`. My F9 shows that duplication is a live fault surface. I weighed dropping to **1** and rejected it: anchor 1 describes an artifact that reports figures, and this one measures nothing at all. 3 is structurally unavailable — no before, no simplification, no complexity measurement.

*Recorded, never scored:* mechanical.json gives 158 code lines, 11 branch points, 4 instance_state, 1 module, 0 internal import edges. I agree with the figures and note that **not one of them would have detected either accidental field.**

### D3 — modularity · **2**

`NOTES.md:38` declares `_append` as the only writer and the code follows it — verified at *runtime*, not by imports: mutating `_append` itself (F5) failed five shared cases and two own cases, so every durable byte really does execute through that one method. Torn between 1 and 2, took 2 because anchor 1's text ("the code does not follow them") is factually false here.

3 is unreachable on the code: the domain imports `os` and calls `open`/`flush`/`os.fsync` inline (`quota_ledger.py:20`, `:220-223`), and the *read* side has no chokepoint at all (`:140` calls `read_text()` directly). No adapter swap leaves the domain untouched. `FEATURE.md:117-121` deliberately leaves this unspecified — a low D3 here is a permitted free choice, not a defect, and I am recording that I did not read it as one.

### D4 — behaviour preservation · **4**

Anchor 2 against the spec rather than a prior version (this tree is greenfield): R1–R5 enumerated and each shown to hold. Anchor 3: `test_quota_ledger.py:206` is a generated 600-step corpus with a shadow model as oracle, re-checked after every step (`:278`, `:281`, `:286`, `:295`, `:297-311`), gated on its own reach at `:315`. Anchor 4 by my own hand, as rule 8 requires: nine behaviour-breaking mutations, nine caught.

**Refuses to claim:** `NOTES.md:108-113` — non-integer amounts are not handled; `reserve("acme", 2.5)` is accepted and prints `2.5` into the ledger, and it declines both to invent a seventh reason and to coerce silently. Verified by execution. Also `NOTES.md:114-117` — "not a contradiction, just a thing I checked for and did not find".

*On the record:* the artifact itself never demonstrates a break being caught. Its only self-critical run (`NOTES.md:91-94`) is attributed to bugs in the tests. **The demonstration behind this 4 is mine.**

### D5 — honesty · **3** (`measured`)

Anchor 2 and 3 met: four blind spots named unprompted (`NOTES.md:96-119`), and on each unspecified point it states a limit instead of a verdict — "the alternatives are equally consistent with the text… I did not implement more than one" (`:98`), and it names a wrong output it knowingly ships (`:108`).

Anchor 4 fails under `measured`: nothing here is a result the artifact **measured against itself** that reflects badly on itself. The float defect is the genuinely unflattering fact and it is disclosed but never measured — no test in this tree or in the shared contract passes a non-integer amount. The only measured self-criticism (`:91-94`) is about its own tests and is steered away from the implementation.

Under `disclosure` this tree scores **4**. I record that so a reader can tell a disagreement about the artifact from a disagreement about the anchor.

### Verdict

Take Z as a solid baseline whose own suite genuinely reaches the refusal, ordering and cross-aspect classes the shared contract cannot — but delete `_Tenant.quota`, which I proved dead by removing it (28/28 and 21/21 still green), and fix `test_a_bad_amount_beats_quota_exceeded`, which asserts a check order that is unobservable because `amount < 1` and `amount > available >= 0` can never both hold.

### Disclosures

- **Arm not identified.** I made no attempt to learn the mapping and did not work it out. Nothing on the forbidden list was opened.
- **Nothing in the repository was modified** except these two card files. All mutation work happened on copies under the scratchpad.
- **What I REJECTED:**
  - *D1 = 4.* Considered and refused: the 600-step sequence is a genuine model-shadowed corpus and did catch two hard-class faults, which tempted me on the "derived from the model" clause. But it never checks reason *identity*, so the reason-ordering catches are hand-written, and no fault class is named as out of reach.
  - *D2 = 1.* Considered on the strength of the dead field plus a three-writer cache, and refused: anchor 1 requires reported figures, and this artifact reports none.
  - *D3 = 1.* Considered and refused: the declared boundary is followed, which I checked at runtime.
  - *D5 = 4.* Available under `disclosure` and refused, because I chose the strict reading and applied it to both trees.
  - **F3 as a suite gap — refused, and this is the finding.** Nothing anywhere catches the swap of `amount_not_positive` and `quota_exceeded` in `reserve`, and I nearly recorded that as a miss. It is an equivalent mutant. Which means `test_a_bad_amount_beats_quota_exceeded` (`test_quota_ledger.py:79-81`) **asserts an ordering it cannot observe** — it passes under either order — and `NOTES.md:84` overstates when it says "the listed order in the feature is only observable in these overlaps". For this pair there is no overlap. A decorative test presented as an ordering test.
  - **Tempted and not credited:** the prose. `NOTES.md` is unusually good and its ambiguity section reads like honesty. I scored the mutation table, not the paragraphs; the D5 of 3 is what the runs support.
