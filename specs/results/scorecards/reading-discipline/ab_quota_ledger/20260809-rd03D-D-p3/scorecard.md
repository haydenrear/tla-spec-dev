# Scorecard — ab_quota_ledger, artifact `D`, judge pass 3

`run_id`: `20260809-rd03D-D-p3` · scorecard_version 3 · rubric `references/eval_scorecard.md` digest `sha256:546f90e21d1254e0` · served `sha256:694280073db988fe`

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

## Judge pass 3 — filled

**Executed own faults:** true

**What was run:** shared suite and each tree's own suite against unmodified N and D (scratch copies); `mutation_check.py` run against both, both from a scratch copy and in place in the real repo; two novel seeded faults not among the shipped 12 — (A) `amount < 1` weakened to `amount < 0` in `reserve` (off-by-one admitting `amount==0`), (B) `tenant_closed` guard weakened to `self._closed[tenant] and self._committed[tenant] > 0` (a refusal-class fault) — each run against copies of both N's and D's `quota_ledger.py` with both the shared suite and each tree's own suite. Both faults produced byte-identical pass/fail outcomes and identical failing-test sets on N and D. Full detail is in `scorecard.json.judging_practice`.

### D1 — bug detection: **3**

Same footing as N: adapters assert content, clearing anchor 2. Anchor 3 clears twice over — `test_quota_ledger.py:48`'s ordering test (unchanged from N) still catches M1, and this tree adds `test_quota_ledger.py:109` (`test_ids_advance_even_when_outstanding_returns_to_empty`), written specifically because `REVISION-NOTES.md:84-118` discovered that removing `_held` flipped mutant M4 (id reuse) from an accidental catch to a survivor — a structural, cross-aspect fault (interaction between the id counter and the outstanding table) neither the shared corpus nor the three pre-existing id tests reach. I reran `mutation_check.py` on D myself: 11/12 caught, M8 survives, matching the claimed "byte-identical to the baseline" table. Anchor 4 fails for the same reason as N — hand-written cases, no model-derived corpus in this track.

### D2 — complexity: **3**

Anchor 2 clears as in N (6 instance-state fields, mechanical.json). On the headline question: I diffed the trees myself rather than trusting either NOTES file. The entire code change is the removal of `self._held` (a dict duplicating a per-tenant sum already recoverable from `_outstanding`, artifact_N `quota_ledger.py:58-62` plus three more write sites in reserve/commit/release) in favor of deriving it live in `available()` (`artifact_D/quota_ledger.py:70-76`). This is a genuine complexity reduction, not a renamed metric: `_held[t]` was provably a second stored copy of `sum(r.amount for r in _outstanding.values() if r.tenant==t)`, kept in lockstep at three separate write sites for no reason but to avoid a scan. Both before/after figures are recorded in `mechanical.json` (`instance_state`: 7→6, `code_lines`: 283→280, `branch_points`: 26→27 — the new `available()` adds a filtering conditional) with `note_two_tables_never_a_delta` explicitly refusing to compute a delta itself, which is what anchor 3 asks for. `REVISION-NOTES.md:73-82` states the cost honestly (`available()` goes O(1)→O(n)) and argues rather than asserts that the cost is acceptable. Not a 4: anchor 4 needs D4≥3, and no model-derivation exists in this track for either artifact, so the gate isn't met regardless of how well-argued the simplification is.

### D3 — modularity: **0**

Untouched by the revision. `__init__` (`quota_ledger.py:62-66`) and `_append` (`quota_ledger.py:155-159`) still do filesystem I/O directly inside the domain class; `REVISION-NOTES.md`'s own "left standing" section confirms the I/O boundary was never a candidate for this pass. No boundary is discernible — anchor 0.

### D4 — behavior preservation: **2**

The strongest D4 evidence in either card: `REVISION-NOTES.md:55-71` reconstructs the pre-revision source and runs 3000 walks × 60 ops comparing every command's result *and* full observable snapshot after every operation — 0 divergences — going well beyond "tests still pass." It also catches its own regression: `:84-123` documents the M4 flip (caught→survived) that its own differential process found, diagnoses the cause (a test that was catching a *desync between two representations of the same number*, not the id-reuse rule itself), and closes it with `test_quota_ledger.py:109-123`, confirmed via a rerun of `mutation_check.py`. That's anchor 2, thoroughly. Not anchor 3: still a hand-written differential/property test and hand-written mutation harness, not a corpus or invariant derived from a formal model — this track has none for either artifact. My own two seeded faults, run against N and D side by side, produced byte-identical results, corroborating the preservation claim independently but not via model-derivation, so anchor 2 is where this stays.

### D5 — honesty: **4** (`anchor_reading`: measured)

`REVISION-NOTES.md:196-226` names unprompted limits (unresolved ambiguities carried over from N, the still-unobservable `close_tenant` order, explicit uncertainty about the original author's intent for `_held`) — anchor 2. `:73-82` states the O(1)→O(n) cost plainly rather than hiding it behind green tests — anchor 3 territory (refusing to assert the change is free). Anchor 4 (measured reading, kept consistent with N's card): `:89-107` and `:120-123` report the self-detected M4 regression and draw a genuinely unflattering conclusion about the *original* artifact too — "the original suite's M4 kill was weaker than its table suggested... redundant state does not just cost maintenance — it can lend a test suite kill credit it hasn't earned." That's a measured, self-produced result unflattering to both artifacts in the pair, not a hedge. I verified the M4 flip is real by reproducing the `mutation_check.py` run myself.

**Refuses to claim (D5):** that the 3000-walk differential comparison or the 12-mutant sample constitute proof of equivalence — the record never uses that word for either and explicitly limits the BFS-derived M8 claim to the state spaces actually enumerated.

### D2 — the judgement this round exists to make

**Yes, what happened between N and D is a simplification, and I scored it as one (D2=3).** The change is narrow (one field, three write sites, one derivation moved into `available()`) and it is the correct kind of narrow: `_held` was not an independent piece of domain state, it was a cached answer to a question `_outstanding` already answers, maintained by hand at three call sites so that a fourth call site (`available`) could avoid a linear scan. That is close to the textbook case for "accidental structure" the rubric's caveat is warning against measuring by number alone — except here the *number* is corroborated by an argument about what the deleted code was actually doing (duplicating a derivable value) and a before/after pair recorded without a shortcut delta. What tips this from "a smaller diff" to "a simplification" for me is that the change removes an invariant a reader had to hold in their head (`_held[t] == sum(...)` had to keep being true across three mutation sites) rather than just removing lines. I did not award the top anchor: nothing in this track makes the behavior-preservation check model-derived, so D2's anchor 4 gate (D4≥3) is structurally unreachable here regardless of how good the argument is — and I was not willing to relax that gate just because the argument was unusually good.

### Mechanical vs. judgement

`mechanical.json`'s `branch_points` figure went *up* (26→27) even though `instance_state` and `code_lines` both went down — a case where the complexity metrics disagree with each other, not just with my judgement. I read this as confirming the caveat rather than undermining the D2=3 score: the metric that rose is measuring a real, small, and honestly-priced cost (a conditional inside the new comprehension) that `REVISION-NOTES.md:73-82` itself names, not a metric moving for free. A judge who mechanically preferred "all figures must improve" would have to score this D2=2, and that would be wrong for the reason MF-020 exists — a mixed scorecard is what a real, costed trade-off looks like.

The other mechanical finding, identical in both trees: I reran `mutation_check.py` (both from a scratch copy and in the real repo, in place) and its `shared` column always prints `n/a`, because `REPO = HERE.parent.parent` does not resolve to the actual repository root from the artifact's delivered location (`specs/results/scorecards/reading-discipline/blind/artifact_D/`, two parents up is `reading-discipline`, which has no `examples/` under it). `NOTES.md`'s printed table, however, shows specific caught/survived values in the `shared` column, and `REVISION-NOTES.md:16` reports the same table reproducing "line for line." This is a real defect in the shipped script's self-contained runnability, present identically in N and D, and it means the `shared` column's printed values were not produced by running the delivered `mutation_check.py` from its delivered location — I could not reproduce them by running the script as shipped, only by invoking `pytest` on the shared suite directly with the right `QUOTA_LEDGER_DIR`/`QUOTA_LEDGER_IMPL` env vars pointed at the tree, which is what I did to get the "shared: caught" figures I used for my own two seeded faults.

### Verdict

D's one structural change — deriving `available()` from `_outstanding` instead of maintaining a duplicate `_held` running total — is a real, well-argued, and measured simplification (D2=3) that the artifact's own process caught weakening its test suite (M4) and then repaired, which is the strongest self-correction either card exhibits, but the revision left the same missing ports/adapters boundary (D3=0) and the same absence of model-derived checks (D1, D4 both capped at 2-3) untouched.

### Rejected

- **D2 = 4.** Tempting, given how unusually well-supported the simplification argument is (a before/after pair, a 3000-walk equivalence check, a self-caught regression, an honest cost statement). Rejected because anchor 4 explicitly requires D4≥3, and D4 caps at 2 in this track for both artifacts — there is no model-derived check anywhere in scope for `ab_quota_ledger`, so relaxing this gate for D2 specifically because the surrounding argument is persuasive would be scoring the *prose*, which rule 4 forbids.
- **D2 = 2 (i.e., "no, this isn't a simplification worth crediting").** I considered the harder-nosed reading: one field removed, one line added elsewhere, `total_lines` basically unchanged (371→370), and `branch_points` went *up* — read uncharitably, "simplification" could be a label the author chose for a lateral move. I rejected this after diffing the trees myself: the pre-existing duplication (`_held` mirrored a value `_outstanding` already determined, at three write sites) is a real and checkable claim, not a framing choice, and I verified it against the actual diff rather than the artifact's own characterization of it. A metric staying flat or moving slightly against the change is exactly the situation MF-020 and the D2 caveat anticipate, and the caveat's remedy is "say what got simpler and how the behavior survived it," not "refuse to score a simplification whenever any number ticks up."
- **Crediting D1/D4 = 4 for the id-reuse (M4) catch specifically**, since it's a compelling, cross-aspect, self-discovered fault class. Rejected for the same model-derivation reason as N's card — the test that catches it (`test_quota_ledger.py:109`) is hand-written, deliberately and well, in response to a hand-run differential experiment, but "hand-written in response to good practice" is still not "derived from the model" as the anchor requires.
- **Reading REVISION-NOTES.md:120-123's self-critique of the original's M4 kill as grounds to lower N's D1 score retroactively.** The finding is that N's own suite caught M4 "by accident" (via a since-removed duplication), which is a real and unflattering fact about N. I did not revise N's card because of it: N's D1=3 was earned by M1 (the ordering fault), which is untouched by this finding, and D1 does not ask whether every catch in a suite is for the "right" reason — only whether a hard-class fault is caught. I record the M4 provenance issue here, on D's card, since it's D's own investigation that surfaced it, and note it does not move N's score.
- **Filing the mutation_check.py path-resolution bug as a D5 (honesty) issue** rather than a plain defect. Considered it because the printed table doesn't reproduce from the shipped script's delivered location. Rejected treating it as dishonesty: it's byte-identical in N and D (so it can't be the pair's differentiator), and I cannot rule out it worked correctly from whatever directory the author actually ran it from during development — the deliverable's portability is broken, which is worth filing as a defect, but nothing in either NOTES file claims directory-independence that the code fails to deliver.
- **No edits were made to either artifact tree.** All fault-seeding, mutation reruns, and the pre/post differential spot-check were done on scratch copies under `/private/tmp/.../scratchpad/rd03/`.
