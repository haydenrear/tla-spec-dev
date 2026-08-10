# What an external project would need — and what that says about what to cut

**RM-02 research output. No production code ships with it.** Its job is to scope
RM-03's removal, and the way it does that is by answering one question against
the record rather than against the anchors' wording: **does this card grade
architecture, or does it grade conformance to this project's architecture?**

The evidence is `specs/results/scorecards/portable-substrate/GOAL-portable/`.
Every figure below re-derives from the 73 sealed cards in about two seconds:

```
python3 specs/results/scorecards/portable-substrate/GOAL-portable/analysis/portability.py
```

**Scope, stated first (`R3`).** 59 of the 73 sealed cards are the example
`ab_quota_ledger`; 4 are `toolchain_removal`; the remaining 10 are two cards
each of five fixtures. **Every figure here is a figure about that population and
about no wider one**, and where a figure is true of one example it says which.
This page is the third consecutive artifact in this repository to be written
under that rule because the first two were not.

---

## 1. The answer

**The card grades four different things under one name, and only one of them is
architecture.**

| | what it actually grades | portable? |
|---|---|---|
| **D1** | whether the subject owns **this project's toolchain** | **no** |
| **D2** | design economy — is one fact stored twice | **yes** |
| **D3** | conformance to **one architectural style** | **conditionally** |
| **D4** | whether the subject owns **this project's toolchain** | **no** |
| **D5** | disclosure practice, orthogonal to architecture | as a note, not a score |

The first thing the record settles is what the question is *not*. Judges do not
score a repository checklist: **78–86% of all citations on every dimension point
at the artifact under judgement**, and citations at this project's formal models,
its spec-double compiler and its scripts together never exceed 5% on any
dimension. Whatever is local about this card is local in its *anchors*, not in
where judges were looking. So the question has to be answered from the
rationales.

### 1.1 D1 and D4 grade the toolchain, not the code

D1's anchor 4 requires cases "derived from the model"; D4's anchor 3 requires the
check to be "model-derived (a corpus, a TLC invariant)". Judges apply those
clauses literally and say so:

> *"Anchor 4 is refused: T's cases are hand-written."* — `ports-as-adapters/…/20260805-T-p2`

> *"Not 3: every check here is hand-written. The fixture ships no corpus and no
> TLC-derived instrument, so there is no model-derived check to raise the
> anchor."* — `architectural-coherence/ex5_pipeline_divergent/20260803-j2`

Measured over the corpus: **an anchor decision cites this project's machinery in
38% of D1 rationales and 18% of D4 rationales, against 4% on D2 and 0% on D3 and
D5.** The consequence is a ceiling, and this project already found it — RD-03
recorded that no model exists in any tree of `ab_quota_ledger`, so *"D1 is
structurally capped at 3 and D4 at 2 for every arm of this example, whatever the
code does"* (`RD-03-DF-11`). The cards agree: **D1 is 3 on 55 of 59
`ab_quota_ledger` cards.** The two cards that reach 4 do so on the *eval
harness's* shared model-derived corpus, byte-identical across the arms it was
scoring — so even there the anchor was awarded for a property of the round, not
of the artifact.

An external project inherits that ceiling on day one and cannot lift it without
adopting TLA+ and the case generator. **D1 and D4 do not export.**

**And the cap propagates — measured, not inferred from the wording.** D2's anchor
4 gates on D4 ≥ 3, so an adopter with no formal model is capped at D2 = 3 as
well. The cards show that clause reaching across and doing it, and they show
*which judges let it*:

| `reading-discipline` arm | judge | D2 | cites the D4 model cap as the reason |
|---|---|---|---|
| `D` | opus p1 / p2 | 3 / **4** | no / no |
| `D` | sonnet p3 / p4 | 3 / 3 | **yes / yes** |
| `M` | opus p1 / p2 | **4** / **4** | no / no |
| `M` | sonnet p3 / p4 | 3 / 3 | **yes / yes** |

> *"Anchor 4 is not reachable: it additionally requires D4 ≥ 3, and D4 is capped
> at 2 below (no model-derived check exists in this project) — so despite having
> the strongest evidence available … 3 is the ceiling."* — `reading-discipline/…/rd03M-M-p3`

**Four of four `sonnet` judges name the model clause as their ceiling; zero of
four `opus` judges do.** So the tier split on D2 — the dimension the card says
holds still — is not a disagreement about complexity at all. It is one
parenthetical about TLA+ being read as a definition by one tier and as an
illustration by the other, exactly as `RD-03-DF-14` proposed, and here confirmed
independently and unanimously within each tier.

**This is the single strongest evidence in this ticket that the local clause is
what makes the card local**, because it shows that clause reaching a dimension
that has nothing to do with formal models and capping it.

### 1.2 D3 grades one style, and it grades it as a verdict rather than a scale

D3's rationales are the cleanest in the corpus: 0% rest an anchor decision on
local machinery, and judges argue in ordinary terms — seams, runtime calls,
injection, a named swap. Nothing in D3's *reasoning* is this project's property.

Its *outcome* is another matter. Grouping every `ab_quota_ledger` card by the
`effect_boundary` its subject declares:

| declared boundary | cards | D3 values |
|---|---|---|
| `ports-and-adapters` | 18 | **4 on every one** |
| `effectful` | 40 | 0 (×6), 1 (×15), 2 (×19) — **never above 2** |

**Disjoint, with no overlap in 58 cards of `ab_quota_ledger`** — a wider
replication of RD-04's original 10-against-24 and in the same direction. D3 is
not a graded scale here. It is a two-valued verdict on a style choice, with a
little resolution inside each value.

This produces a contradiction between two shipped documents, and it is worth
naming plainly because it is the crux of the portability question.
`references/architecture_tags.md` §2.2 says the values are **"nominal, never
ranked"**, and gives the reason: *"the moment one is better the tag is a target,
and `MF-020` applies."* But the card's D3 anchors 3 and 4 *are* the definition of
`ports-and-adapters` — "the domain does not import its I/O", "a driven port
exercised by a real adapter *and* a fake". **The tag refuses to rank the values;
the dimension it exists to make comparable ranks them 4 against ≤ 2.** The tag
design says as much in §2.3 — *"the tag names the shape the anchors assume"* —
without drawing the conclusion: an adopter whose architecture is not that shape
is not being measured, they are being told their style is worth ≤ 2.

Two things keep this from being a flat "do not export".

- **The style must be held, not declared.** `ex5_pipeline_divergent` is declared
  `ports-and-adapters` and scored **D3 = 1 by both judges** — the fixture built
  to declare boundaries the code does not follow. D3 does real work *inside* the
  style, which is why it discriminated for `ports-as-adapters`.
- **`toolchain_removal` reached 3 and 4 on an `effectful` subject.** That is the
  single counterexample in the record, and RD-04 already dissolved it: the four
  judges scored three different subjects, and within each scope the spread is
  zero.

So D3 exports **to an adopter who has already chosen ports-and-adapters as their
target**, and to nobody else. For anyone else it is a constant ≤ 2 that reads
like a grade. That precondition has to travel with the dimension, written down.

### 1.3 D2 is the one that travels

D2 mentions the local complexity descriptor in 40% of rationales, but the
descriptor is not what decides it. Every D2 ≥ 3 in the `reading-discipline`
round — the round the epic's D2 result rests on — is decided by diffing two
plain Python trees:

> *"I diffed the two trees myself before reading either note. … `_held[t]` was at
> every instant equal to `sum(r.amount for r in _outstanding.values() …)` — one
> number stored twice, kept in agreement by hand across reserve, commit and
> release, and read in exactly one place."* — `reading-discipline/…/rd03D-D-p2`

Nothing in that requires a TLA+ model, a corpus, a port or a language. This
project's own prior finding points the same way from the other side:
`references/hexagonal_prompting.md` records that the complexity clauses had to be
restated in code terms because *"the prompt's audience may have no model at
all, so the reading rules travel and the numbers do not."* **The reading rules
are the portable part of D2 and the descriptor is not**, and the descriptor's
irrelevance here is measured, not argued: RD-03 found 19 of 21 axes
byte-identical across the only simplification this project ever measured, with
one moving the wrong way, while eight judges found it independently.

D2's honest limit is different and it is a limit on *use*, not on portability:
on the example `ab_quota_ledger`, **D2 = 2 on 51 of 59
cards.** It moves only where a before and
after exist, because anchor 3 requires them. See §3.

### 1.4 D5 is portable and nearly uninformative

D5 rationales cite no local machinery at all, and D5 is demonstrably
independent of architecture: `ex6_jenga`, the deliberately incoherent fixture,
scores **D5 = 4 from both judges** while its D3 is 0 and 1;
`ex5_pipeline_divergent` scores **D5 = 4 from both judges** at D3 = 1. D5 is
about the record kept around the artifact, not about the artifact.

That is fine, and it means D5 is not a fifth reading of the design — it is a
reading of the write-up. It is also near-saturated: **D5 is 3 or 4 on 53 of 59
`ab_quota_ledger` cards.** Export the discipline; do not export the number.

---

## 2. What is irreducibly local

Six items. None is "hard to port"; each is *meaningless or unreachable* outside
this repository.

1. **D1 anchor 4, D4 anchors 3 and 4, and D2 anchor 4's D4 gate.** Not
   expensive — **unreachable**. They ask for a formal model, and an adopter
   without one is capped before writing a line. This is the whole of the
   difference between grading architecture and grading conformance to a
   toolchain, and it is three clauses.
2. **`scripts/analyze_complexity.py` — the TLA+ descriptor** (2,401 lines at
   `2c0d94e`). Parses a constrained TLA+ profile. Its outputs — variables,
   actions, state-space bound, R/W density — are properties of a *model*, and D2's
   anchor preamble instructs the judge to read them first. A project with no
   TLA+ spec has nothing to read.
3. **The `effect_boundary` derivation** (`architecture_tags.py`, 688 lines,
   backed by `scripts/code_complexity.py`, 968 lines). Python `ast` only. An
   adopter in any other language derives `UNDERIVABLE:unparsed` on every subject.
   That fails open and is therefore harmless — and it is also *empty*: they ship
   1,656 lines that say nothing about their code. Clause (b)'s
   `state_colocation < 0.5` threshold has additionally never been measured near
   its boundary.
4. **The `[[demonstration]]` table's refusal authority.** It is re-derived from
   *this repository's cards* on every `audit`. An adopter starts at zero cards,
   so the table is empty and the tag has authority nowhere — which is correct
   behaviour and means the mechanism does no work until they have run enough
   rounds to populate it themselves. It cannot be handed over; only the rule can.
5. **`examples/validation/gap_mutants/gap_mutants.toml`** (576 lines) and the
   mutant catalogues. These are hand-authored faults **in `ab_quota_ledger`**.
   They are a fixture wearing a tool's clothes. Nothing in them transfers, and
   the runner that reads them (633 lines) has nothing to run without them.
6. **The hard-wired repository layout in `score_tools.py`** — `REPO_ROOT` from
   `HERE.parents[3]`, `specs/desired_program_model/deferred_findings.yaml` for
   `R-H3`'s `filed_as`, and `scope`'s sweep globs. Small and real. `--rubric` and
   `--root` already cover the rest, which is why this is item 6 and not item 1.

**One defect found while checking item 6, and it binds this repository before it
binds anyone else.** `scaffold`'s blinding draws opaque arm labels from
`LABEL_POOL = "DEFGHJKLMNRSTUVWZ"` — 17 characters — excluding every label any
prior round published. This repository has consumed 17 labels and **4 remain:
`G`, `J`, `L`, `V`.** A round needing five arms is refused, and no round can ever
be blinded here again after four more. The blinding mechanism has a bounded
lifetime baked into a constant. Filed as `RM-02-DF-01`.

---

## 3. The minimum an adopter must supply, costed

**This project can supply:** the anchors — `score_tools.py serve` emits **85
lines** out of the rubric file's **709** at `2c0d94e`, and the other 624 are
reading rules and prior results a judge must never see, which `serve` already
withholds. **That ratio is the single most encouraging number in this ticket:
88% of the card an adopter would think they have to read is not the card.** Also
`score_tools.py`'s
`scaffold`/`check`/`seal`/`index`/`contested`/`history`; the blinding mechanism;
`prompts/hexagonal_implementation.md`, which was built to travel; and the reading
rules `R-H2`, `R-H4`, `R-H6` and `R3`, none of which mention anything local.

**The adopter must supply four things, and the second is the expensive one.**

1. **A subject with a declared scope.** Cost: minutes. Not optional — the
   `toolchain_removal` round is the demonstration that four judges handed one
   undeclared subject will score three different ones, D3 = 2, 2, 3, 4, with a
   spread of zero once each card is read at the scope its own citations name.
   This is the cheapest high-value item in the whole substrate.

2. **A before and an after.** D2's anchor 3 requires a simplification *and* its
   measured effect; D4's anchor 2 requires the baseline's behaviours enumerated.
   **An adopter therefore cannot score a codebase. They can only score a change
   to one.** On the record this is not a marginal restriction: D2 is flat at 2 on
   51 of 59 `ab_quota_ledger` cards, and every card where it moved came from the
   one round that supplied a revision pair. **The card is an instrument for
   changes, not an instrument for code**, and nothing in the card says so.

3. **Two blind judges per artifact, and a third pass for anything contested.**
   From this project's own re-score rounds: four fresh judges per version
   boundary (SM-04), twelve for a three-artifact round (FI-03).

4. **A behavioural suite of their own.** Without one, D4 sits at 0 or 1 and D2's
   anchor 4 is unreachable regardless of the model clause.

**Neither side can supply**: `R-H1`'s architecture clause (needs a demonstration
table the adopter has no cards for) and `R-H5`'s `readable` flag (needs two ends
of a movement). Both correctly fail open and both do nothing on day one.

---

## 4. Does the change rule survive an adopter using it?

The rule — *bump `scorecard_version`, keep the old anchors, re-score at least one
prior example under both* — is the mechanism behind the loop the owner described:
a regression found by hand becomes a card iteration the adopter chose. It
survives in outline. Three things break in practice, and only one of them is a
gap in the rule itself.

- **It cannot be exercised on day one.** "Re-score a prior example" presumes a
  sealed prior example. An adopter's first version bump has nothing to re-score
  against, and the honest answer is that their v1 → v2 discontinuity is
  unmeasurable rather than zero.
- **Freezing the old rubric is operator sequencing, not a mechanism.** The card
  says so itself, and it is `FI-06-DF-11(c)`, open. `--card-version N` alone
  reproduces the old *schema* against the *new* bar. An adopter who misses the
  `--rubric <frozen>` half measures nothing and gets a clean-looking result.
- **The gap: the rule measures the discontinuity but never asks the new anchor
  to be able to refuse.** An adopter adding an anchor for a regression they just
  found already knows how their artifact scores on it. Re-scoring a prior example
  under both versions does not test that — it reports a number whose sign was
  known before the round began. This epic's own `no_axis_tuned_to_a_known_answer`
  rule requires an added axis to ship with **a seeded case where it moves the
  wrong way**; the change rule requires no such thing. That requirement belongs
  in "Changing this card" as a sentence. **It is not a gate and must not become
  one** — the epic forbids new gates, and a check here would be the fifth static
  check this project has shipped that catches nothing.

**And a first-contact failure worth documenting rather than discovering.**
`serve` and `scaffold` refuse the whole batch when the served text asserts how one
of the five dimensions has scored or moved. An adopter writing a new anchor out
of a regression they found will very naturally write that regression into the
anchor's caveat — and be refused, with nothing written. The refusal is correct
and it is the mechanism working. It is also the most likely way an adopter's
first iteration fails, and no page currently warns them.

---

## 5. What this says about what to cut

**Adoption requires less, not more. Every item below is a removal.**

That is the honest answer and it is the useful one, because "simplify" had no
stopping rule and this does. Nothing in this page proposes a new instrument, a
new field, a new check or a new document beyond itself.

Ordered by how much each one buys:

1. **Cut D1 and D4 from the card, or cut the model clause out of their anchors.**
   Pick one; do not do both and do not do neither. On this repository's own
   evidence D1 is a constant (3 on 55 of 59 `ab_quota_ledger` cards) and D4 is
   the worst-behaved dimension measured — see §6. If the clauses go, D1 and D4
   become ordinary questions about tests and both become exportable; if the
   dimensions go, the card is three dimensions and two notes and every remaining
   number means the same thing everywhere. **The status quo — carrying two
   dimensions that are structurally pinned on the only example the project
   scores — is the one option the record does not support.**
2. **Cut D2's anchor 4.** It gates the one portable dimension on the least
   portable clause in the card, and it is the mechanism behind the D2 tier split
   (`RD-03-DF-14`). Removing it costs the top of one scale and frees D2 entirely.
3. **Cut D5 to a recorded note.** It is orthogonal to architecture by
   measurement, saturated at 3–4 on 53 of 59 `ab_quota_ledger` cards, and it
   still tier-splits. Keep the discipline; stop scoring it.
4. **Cut the mutant catalogues and the gap-mutant runner** (`gap_mutants.toml`
   576 lines + runner 633 + `check_catalogue.py` 1,344, all at `2c0d94e`) **on
   adoption grounds as well as on the epic's existing grounds.** They are
   `ab_quota_ledger` fixtures. There is no version of them an adopter receives.
   RM-01 must price this cut; RM-02's contribution is that a zero price here
   would not make it a free cut, because the adoption argument is independent of
   the pricing one.
5. **Stop shipping the architecture tag as an adopter-facing surface.** Its
   derivation is Python-only and its refusal authority is re-derived from this
   repository's own cards, so an adopter receives 1,656 lines that say nothing
   about their code and a table with no rows. The *rule* — architecture is a
   comparability axis, name it before you compare — costs one sentence and
   carries the whole value. Keep `references/architecture_tags.md` as RD-04's
   sealed design record; it is not adopter documentation and should stop being
   read as any.

**And the distinction RM-03 must not lose.** §2's list is *irreducibly local*,
which is **not** the same as *should be cut*. `scripts/analyze_complexity.py` is
the largest item on that list and it is **not** a cut candidate: the TLA+
descriptor serves the spec workflow, which is a different job from grading a
card, and removing it to make the card portable would delete a working thing to
tidy a page. The same holds for `code_complexity.py`. What the adoption argument
says about them is narrower and it is enough: **their outputs must stop being a
precondition of a D2 score.** That is a change to D2's anchor preamble, not a
deletion of an instrument.

**Two more things RM-03 should NOT cut on adoption grounds:**

- **The behavioural suite.** Its defunding as a *finding channel* is settled on
  other evidence; as the thing an adopter must supply for D4 to have a referent
  at all, it is load-bearing.
- **`scope`, `seal`, `contested`, the blinding mechanism, and
  `R-H2`/`R-H4`/`R3`.** These cost nothing to hand over and are the reason any
  number here is readable at all. They are the substrate's best export and the
  epic should be careful not to cut them for being unglamorous.

---

## 6. Which dimensions survive the trip

A dimension that cannot be trusted in the project that built it should not be
exported. Measured over the **8 judge groups in the sealed record scored by both
`opus` and `sonnet`**, counting a tier split exactly as `R-H6` defines it —
disjoint ranges on the same artifact:

| | tier-split groups | directions | verdict |
|---|---|---|---|
| **D1** | 0 of 8 | — | stable **and near-constant**; do not export |
| **D2** | 1 of 8 | opus higher | **export** |
| **D3** | 3 of 8 | opus higher ×2, sonnet higher ×1 | export **with its style precondition** |
| **D4** | 4 of 8 | opus higher ×3, sonnet higher ×1 | **do not export** |
| **D5** | 2 of 8 | opus higher ×2 | export as a note |

**Two things in that table correct the epic's working assumptions and are
reported as corrections rather than results.**

- **D3 tier-splits three times as often as D2, and in both directions.**
  `references/eval_scorecard.md`'s own R-H5 calls D2 and D3 *"the dimensions that
  have held still on unchanged input"* and advises resting cross-epic claims on
  them; `ports-as-adapters` rested its headline there. That advice is about
  *unchanged input within a tier* and it is not wrong — but **across tiers, D3 is
  the second least stable dimension on the card**, and no page says so.
  **The magnitude, stated so this is not overread:** two of D3's three splits are
  one-point offsets at the floor (`[1,1]` against `[0,0]`), which is a different
  phenomenon from the third, `toolchain_removal` at `opus [2,2]` against
  `sonnet [3,4]`, which straddles the 2→3 seam RD-04 identified as the place
  where *"the domain silently changes referent"*. One of three is at the seam
  that matters. Filed as `RM-02-DF-02`.
- **D5's splits both run the same way here** — `opus` higher on both. The epic
  charter records D5's tiers as *"running in opposite directions"*. On disjoint
  ranges over these 8 groups they do not. The two statements are about different
  quantities (per-judge deltas versus group-level disjointness) and this is not a
  contradiction, but a reader comparing them will think it is. Filed as
  `RM-02-DF-03`.

**And the limit on this table, said before anyone quotes it.** Eight groups. Seven
of them are one example, `ab_quota_ledger`, and six of those seven come from a
single round. This is not a measured population and no claim here should be read
as a rate. It is enough to say *which dimensions have been caught splitting* and
not enough to say how often any of them does.

---

## 7. What this ticket could not settle

- **Whether D3 discriminates inside `effectful`.** The record has 40
  `effectful` `ab_quota_ledger` cards spanning 0–2 and 4 `toolchain_removal`
  cards spanning 2–4 whose spread RD-04 attributed to three different subjects.
  Whether a *well-built* non-hexagonal program can reach D3 = 3 is untested,
  and it is the single measurement that would decide whether D3 exports
  unconditionally. RM-04's blind round on `scripts/` is the first subject in the
  project's history that could answer it.
- **Whether D2 replicates off `ab_quota_ledger`.** Every D2 movement in the
  record is one example, one round. RM-04 owns this.
- **What an adopter's first round actually costs.** Everything in §3 is costed
  from *this* project's rounds, where the operators wrote the instrument. That is
  a floor and it is certainly not the number.
- **Whether the card is worth adopting at all.** Out of scope, deliberately. This
  page answers what would have to be true.

## 8. What was rejected

- **A portability layer, an adapter interface, a config file, a "profile"
  mechanism, or any `--external` mode.** The epic's stopping rule is not a
  feature request. Every one of these was a way to keep the unexportable parts by
  wrapping them.
- **Adding a non-TLA+ path to D1 and D4 so the anchors become reachable.** This
  is the shape of `MF-020`: an axis added because the current one gives an
  unwanted answer. Cutting the clause is honest; replacing it with an easier one
  is not.
- **Adding a sixth dimension for "adoptability".** Rejected on sight.
- **A check that the change rule was followed.** `no_new_gates_rule`, and five
  epics of evidence that it would catch nothing.
- **Rewriting `architecture_tags.md` §2.2 to admit the ranking.** A predecessor's
  statement at a predecessor's scope is not edited to match a successor's
  finding. It is filed (`RM-02-DF-04`) and left standing.
- **Reporting the 58-card D3 separation as a fact about the card.** It is a fact
  about `ab_quota_ledger`, and this page says so every time it appears.

---

## 9. `scope` run over this page, and the bound that applies

```
python3 examples/validation/scorecards/score_tools.py scope
```

| | counted | REFUTED | COUNT-MOVED | HOLDS | UNREACHABLE |
|---|---|---|---|---|---|
| before this page (tree `2c0d94e`) | 70 | 55 | 0 | 0 | 15 |
| with this page | 72 | 55 | 0 | 2 | 15 |
| with RM-02's findings as well | **76** | **55** | **0** | **4** | **17** |

**Every figure this ticket contributes to the counted column HOLDS**, re-derived
against the cards on disk: `D1 = 3 on 55 of 59` and `D2 = 2 on 51 of 59`, each
resolved to the example `ab_quota_ledger`, counted once in §1 and once where §9
quotes them back. This ticket refutes nothing and moves no existing figure. Those
are also the first entries in the HOLDS column of this repository's sweep, which
is a statement about how few figures here have ever carried their scope and not a
compliment to this page.

The two figures this ticket adds to UNREACHABLE are both inside `RM-02-DF-05`
below — **the finding is unreadable to the checker for exactly the reason it
documents**, and rephrasing it would delete the demonstration.

**The applicable bound is the second one — `RD-04-DF-01`, the ≤3-word qualifier
window** (`NEXT-EPIC.md` §6). Three of this page's figures are invisible to the
checker rather than checked by it, which is the *first* bound (`RD-02-DF-01`) and
is stated here rather than left for a reader to discover:

- the D3-by-boundary table in §1.2 (18 cards at 4, 40 cards at ≤ 2) — a table
  cell carries no bind-and-value form;
- `D5 is 3 or 4 on 53 of 59` in §1.4 and §5 — a figure naming two values is not
  matched;
- every figure in §6's tier-split table — those count judge groups, not cards.

**A sharper edge on bound 2 than the record carries, found by writing this page.**
`scope`'s counted-noun pattern is `[A-Za-z][A-Za-z-]*` and **does not admit an
underscore**, so `ab_quota_ledger` written immediately after a count is parsed as
the qualifier `['ab']` and the figure is refused as unreachable before the
window search for a named example ever runs. Every example id in this corpus
contains an underscore, so **a figure in this repository can never carry its
example name as its counted noun** — the scope must be established in the two
lines before it instead. That is how the second row of the table above was
obtained: the first draft of the D2 figure was UNREACHABLE for exactly this
reason and was rephrased, not re-scoped. Filed as `RM-02-DF-05`; it is a bound
on the checker, and an adopter naming their example `order_service` inherits it
on their first figure.
