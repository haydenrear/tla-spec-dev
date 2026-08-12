# SV-02 — validation is scorable, the property was already in the card, and the rung is the wrong carrier

**A RESEARCH ticket. No production code ships.** The design and the argument live
in **`references/scoring_validation.md`**; this page is the ticket record — what
was run, on which tree, what it cost, and what it could not settle.

**Branch point: `a527305`**, verified with `git rev-parse --short HEAD` against
the SHA the work order gave and against `epic/score-drives-validation`. They
agreed. The epic charter warns that `wt new` branches from the LOCAL ref and has
put tickets 4, 14 and 21 commits behind; it did not here.

**RECONCILED ONTO `b999d71`** after the epic tip moved under this ticket —
`f2cfe2e` merged SV-06, and `2059500` repaired the third suite red this ticket
filed as `SV-02-DF-05`. **Every figure below was re-measured at the reconciled
tree**, and the two trees are named separately wherever they differ. The corpus
itself did not move: 87 sealed cards, 399 scored rationales, 36 recorded notes,
identical example and version distributions at `a527305` and at `b999d71`, so
**every figure in the design page holds unchanged.** The reconcile changed the
suite baseline and the sweep counts, and nothing else.

---

## 1. The four questions, answered

**1. Is validation scorable without grading a toolchain? YES.** The property is
*the artifact's own checking has a demonstrated red, and the region where it
stays green is named.* It is provenance-blind by construction — hand-written,
generated, property-based, fuzzed and model-derived satisfy or fail it
identically — and it is not new: **it is already written into this card** as D4's
retired anchor 4 (*"a deliberate behavior-breaking change is shown to be caught —
the check is demonstrated to be capable of failing"*), as D1's retired anchor 0
(*"a suite that is green on broken code"*), and as D3's live version 5 caveat.

**2. The autopsy fraction, computed RM-02's way: 14.0% over the whole record
(44 of 315 demonstration sentences), and 3% — one sentence in thirty — in the
ladder-free `N-D1` notes**, against D1's 37% and D4's 17% at this tree. The
decomposition is the answer: **13 of 13 of D4's machinery-citing anchor decisions
name anchor 3, and 26 of 28 of D1's name anchor 3 or 4.** The locality is three
clauses, not two dimensions.

**3. A TLA+ model or an adapter surface without our compiler?**
**Adapter surface: yes, already** — D3 anchor 4 names no tool, **0 of 87 D3
anchor decisions cite local machinery**, it is reached on 22 `ab_quota_ledger`
cards, and its v5 caveat fired correctly on a stranger's artifact (`CL-04` §8).
**TLA+ model: in principle yes, on this record no** — 36 model citations exist and
two judge statements apply the property to an invariant, but **no anchor has ever
turned on a model's discriminating power**, and making possession of a model a
rung rebuilds D1 anchor 4. **Diagram: no.** `diagram`, `mermaid`, `UML`, `C4`,
`.svg` appear in **0 sentences across 0 of 87 cards**.

**4. Byte cost, and the carrier.** Measured with the real renderer, not
estimated. Sharpening the `N-D1` note prompt to ask for the denominator and the
structural reason costs **−15 bytes** and keeps 9 rungs; adding *"who wrote the
cases is not an input"* instead costs **exactly 0**. Restoring D4 as a scored
dimension costs **+682 bytes and 4 permanent anchors** (9 → 13 rungs), plus a
change to `scored_dims`/`note_dims`, a row in `TOP_SCORE_V4`, a version bump and
the change rule's re-score. A new sixth dimension costs **+882**.
**A note carries it; a rung does not pay for itself.**

---

## 2. What was run, and on which tree

**All re-run at the reconciled tree.** And the design page's figures are not
merely unchanged, they are **unmovable by this reconcile**, which is checkable
rather than asserted:

```
git diff --stat a527305 b999d71 -- 'specs/results/scorecards/**/scorecard.json'
git diff --stat a527305 b999d71 -- references/eval_scorecard.md examples/validation/scorecards/
```

**Both are empty.** The 87-card corpus, the rubric and the card tooling are
byte-identical across the tip move, so every figure derived from them — the
autopsy fractions, the 13-of-13, the 5-of-5, the byte table, the diagram zero —
has the same inputs it had before. What the reconcile moved is the suite baseline
and the sweep counts, and both are re-measured below.

| | command | result |
|---|---|---|
| the corpus analysis | `analysis/scorability.py` | 9 sections; same inputs at both trees, same output |
| the carrier pricing | `analysis/carrier_cost.py` | the byte table, and a RUN refusal; unchanged by the reconcile |
| RM-02's own script, re-derived | `…/portable-substrate/…/analysis/portability.py` | 37% / 17% / 3% / 0% / 0% — its 38/18/4/0/0 holds at 87 cards, at both trees |
| the surface metric | `score_tools.py serve 2>/dev/null \| wc -c` | **6,281 bytes, 9 rungs at both trees** — unchanged |
| the sweep | `score_tools.py scope` | §4 — **moved on reconcile**, re-measured |
| the suite | `uv run --with pytest --with pyyaml python -m pytest tests -q` | §5 — **moved on reconcile**, re-measured |

Both analysis scripts read only sealed cards, write nothing, and are imported by
nothing. `carrier_cost.py` imports `score_tools` to call the **real** renderer;
it monkeypatches `scored_dims`/`note_dims` inside a `try/finally` in its own
process to render a hypothetical, and restores them immediately. No production
file is touched.

**Scratch output went to an SV-02-specific path** throughout
(`…/scratchpad/SV-02-*`), per the charter's rule about the two concurrent tickets
that corrupted a shared `baseline.txt`.

---

## 3. The result that decided it

The record contains a natural experiment nobody ran deliberately. **Version 4
turned D1's question into a note with no rungs beneath it, and left the question
itself unchanged.** Twelve cards have been judged that way.

| | machinery-citing | population |
|---|---|---|
| D1 anchor decisions | **37%** (28 of 75) | scored rationales, versions 1–3 |
| demonstration sentences inside D1's rationales | 20% (25 of 125) | the same cards |
| **demonstration sentences inside `N-D1` notes** | **3% (1 of 30)** | 12 cards, versions 4–5 |

**The machinery was attached to the ladder, not to the property.** And the one
machinery-citing sentence in the notes is machinery-citing because in that round
**our own toolchain was the subject** — a different thing from an anchor
requiring it.

**The confound, stated because it bounds the result:** the 12 note-bearing cards
come from two rounds three epics later than most of the corpus, with a different
judge-model mix and a different subject mix. The 3% is not controlled against the
37%. What *is* controlled is the anchor decomposition (13 of 13, 26 of 28) and
the tier-split cause (5 of 5), because both compare cards inside the same round.

---

## 4. `scope`, with both trees named

| tree | counted | REFUTED | COUNT-MOVED | HOLDS | UNREACHABLE |
|---|---|---|---|---|---|
| `b999d71`, epic tip, without SV-02's page or evidence | 93 | 68 | 0 | 5 | 20 |
| `b999d71` + SV-02 — **the reconciled tree** | **94** | **68** | **0** | **6** | **20** |

**Delta: +1 counted, +1 HOLDS, nothing refuted, nothing moved, nothing added to
UNREACHABLE.** Both rows re-measured at `b999d71` after the reconcile; the
pre-reconcile rows (92 → 93 at `a527305`) are superseded and not carried
forward.

**The first draft's figure was refuted and re-scoped.** §4's denominator was
sixty-one where the corpus says sixty-three, because two `ab_quota_ledger` cards
carry an `N-D1` note instead of a D1 score — the exact fact the page is about.
**Re-scoped, not rephrased.**

**AND A CORRECTION TO THIS TICKET'S OWN EARLIER REPORT, found on reconcile.**
The pre-reconcile PR reported *"92 → 93 counted, +1 HOLDS, nothing refuted"*.
**That number was measured before §11's closing paragraph was written and was
therefore wrong for the tree that shipped.** That paragraph quoted the corrected
figure verbatim so a reader could see what had changed, and **`scope` counted the
quotation as a claim and refuted it** — nothing in its parse distinguishes a
figure a page *asserts* from one it *quotes in order to correct*. So the page
acquired a REFUTED row for the very error it was documenting. Fixed by spelling
the denominator in words, which is a workaround and is named as one.

**This is a new bound on the checker**, alongside `RD-02-DF-01` and
`RM-02-DF-05`. **Not filed** — the budget of five is spent and none of the five
is blocking — and **escalated in the ticket report** on `RM-02`'s precedent. It
is also a small demonstration of the ticket's own thesis: a re-run caught it, and
nothing about the page's argument changed.

---

## 5. The suite, with its tree and its inherited reds

`uv run --with pytest --with pyyaml python -m pytest tests -q`.

| tree | result |
|---|---|
| `a527305` **with** SV-02's files | 3 failed, 1499 passed in 1177s |
| `a527305` **without** them (`git stash -u`), the three tests alone | 3 failed, 59 passed |
| **`b999d71` merged into `feature/SV-02`** — the reconciled tree | **2 failed, 1497 passed** in 1101s |
| `b999d71` + SV-02, the three tests alone | **2 failed**, 60 passed |

**SV-02 adds no red, at either tree** — RUN, not assumed, at both.

| test | at `a527305` | at `b999d71` |
|---|---|---|
| `test_architecture_tags.py::test_the_same_tag_control_holds` | red | **red** — inherited, `RM-06-DF-01` |
| `test_price_removal.py::test_nothing_in_the_repository_invokes_the_pricer` | red | **red** — inherited, the pricer grep tripped by narrative documents; it names `CLOSE-THE-LOOP-EPIC.md` and `NEXT-EPIC.md`, never SV-02's |
| `test_card_has_one_home.py::test_only_the_card_states_a_dimension_an_anchor_or_a_scoring_rule` | red — **the undeclared third** | **GREEN, 8 passed** — repaired by the owner at `2059500` |

**The third red is gone, and the epic now carries the two its charter declares.**
SV-02 filed it as `SV-02-DF-05` when there were three; the owner repaired it with
a **pointer** rather than a corrected copy — which is the fix
`test_card_has_one_home`'s own docstring asks for and the option the finding
recommended. `SV-02-DF-05` is marked `repaired` in the ledger with that
verification recorded on it. **This ticket does not carry the three-red figure
forward.**

**And the denominator moved, so it is named rather than quietly restated.**
Collected tests fell **1502 → 1499** across the tip move. **SV-02's own
contribution is zero in both directions**, measured by collecting with and
without its page and evidence directory at the reconciled tree:

```
pytest tests --collect-only -q   ->  1499 with SV-02, 1499 without
```

— **0 added, 0 removed**, the id sets identical. The three belong to the tip
move, not to this ticket, and they are flagged here rather than chased: whatever
`b999d71` dropped is the owner's tree to read, and a research ticket reporting
`1497 passed` against a silently smaller denominator would be committing the
error this repository files findings about.

**This ticket's own hazard was checked rather than assumed.** SV-02 adds two
narrative documents, which is exactly the input that trips the pricer grep and
exactly what `test_card_has_one_home` exists to catch. Neither is named by either
failure: `references/scoring_validation.md` cites no pricer, and it quotes the
retired D1 and D4 anchors as prose while deliberately **not** restating D2's or
D3's live anchors — for the reason that test executes, which the page says where
it declines to restate them.

---

## 6. What this scopes

- **`SV-03`** — validation IS scorable, so the ticket does **not** shrink to
  architecture. But the keyable quantity is **a denominator inside a note**, not
  a dimension score, and a goal keyed to it is keyed to *this artifact, before
  and after* — never across artifacts. `5 of 28` is exactly what `R-H2` permits
  and nothing more. If the wiring needs a scored dimension today it has D2 and
  D3.
- **`SV-04`** — `HARVEST-CL-03`'s classes **B1–B6** (checks that cannot fail),
  **C1–C7** (gates clean on broken input) and **D1–D7** (numbers with nothing
  behind them) are this property already. A closure that turns one of them into a
  case whose denominator moves is the loop reaching the program, and the
  before-number is already sealed in a card.
- **`SV-07`** — carries the model question and the D4 counterfactual, both in §7.

---

## 7. What could NOT be settled

1. **Whether a provenance-free ladder would close D4's tier split.** Four of the
   six lower-tier `reading-discipline` cards already have the top-rung evidence
   written in their own prose. **That is a reading of sealed text, not a
   re-score**, and it is the one experiment that would make a restored rung
   defensible. Nobody should restore D4 before it runs.
2. **Whether a TLA+ model can be scored on its discriminating power.** Two
   statements in the record do it; no anchor has ever turned on it; both fixtures
   are ours.
3. **Whether the notes are richer because the ladder went or because the rounds
   got better.** §3's confound. Uncontrolled.
4. **What the property costs an adopter.** Everything here is priced from rounds
   where we wrote both the artifact and the instrument — a floor, not the number.
   `RM-02` §7 said the same and it is still true.
5. **Whether `demonstration_grade` measures anything.** A regex over prose, never
   validated against a human read, used for one purpose only: showing the
   property varies where D1's number did not.

---

## 8. What was REJECTED

- **A sixth dimension.** +882 bytes and four permanent anchors. Priced rather
  than dismissed, so the price is visible.
- **Restoring D1**, clause-repaired or otherwise. 20% local in its own
  rationales, 3 on 56 of 63 cards of `ab_quota_ledger`, and its anchors 1 and 2
  grade what a projection prints — our word for our thing.
- **Restoring D4 with anchor 3 deleted — rejected FOR NOW and not on principle.**
  The closest call in the ticket. The evidence supports the *anchor* and not yet
  the *rung*, and adopting it before §7.1's round is fitting a rung to an answer
  we like.
- **Any dimension asking "do you have model-derived cases".** The trap in the
  work order; it is D1 anchor 4.
- **A rung for diagrams.** Zero evidence in 87 cards. `MF-020`.
- **Scoring the judge's demonstration rather than the artifact's.** It is what
  the version 2 gate did — the served card said *"D4's anchor 4 is only awardable
  when this says `true`"* — and **11 of the 11 D4 = 4 cards carrying the field say
  the judge ran something, none says false.**
- **A check that a note carries a denominator.** `no_new_gates_rule`.
- **Editing `eval_scorecard.md`'s D4 retirement sentence.** Filed as
  `SV-02-DF-01` and left standing, the way `RM-02` left `architecture_tags.md`
  §2.2.
- **Reporting the 3% as a fact about the card.** It is a fact about 12 cards from
  two rounds, and §3 says so where it appears.

---

## 9. Findings filed

Five, against a budget of five. **None blocking**, so nothing escalates — and
one is already `repaired`.

**Escalated rather than filed, because the budget is spent** (`RM-02`'s
precedent): `scope` cannot distinguish a counted figure a page **asserts** from
one it **quotes in order to correct**, so a page documenting its own corrected
denominator acquires a REFUTED row for the error it is documenting. §4.

| id | severity | what |
|---|---|---|
| `SV-02-DF-01` | major | D4's retirement sentence gives tier instability as an independent reason; **5 of 5 split groups have every lower-tier card naming the model clause**. The figure has also moved, 4-of-8 → 5-of-9. |
| `SV-02-DF-02` | minor | The epic's surface metric names no stream: `serve \| wc -c` is 6,281 and `serve 2>&1 \| wc -c` is 6,373. |
| `SV-02-DF-03` | minor | The served card asks three separate times whether the judge seeded a fault — 43 of N-D1's 113 bytes, on a surface that must not grow. |
| `SV-02-DF-04` | minor | `top_score`'s default hides the version map behind an anchor-count error message; fires the moment anyone un-retires a dimension. |
| `SV-02-DF-05` | minor | The epic opened with **three** red tests and told every ticket there were two — the third tripped by the epic's own opening commit restating D2 and D3. **`repaired`** by the owner at `2059500` with a pointer, verified here at `b999d71`: `test_card_has_one_home` is 8 passed and the epic now carries the two reds it declares. |
