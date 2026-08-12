# Can validation be scored without grading toolchain ownership?

**SV-02 research output. No production code ships with it.** Its job is to scope
`SV-03`, `SV-04` and `SV-07` by answering one question against the sealed record
rather than against the anchors' wording: **is there a property that separates
well-validated code from badly-validated code independently of which tools
produced the tests — and if there is, what is the cheapest thing that can carry
it?**

The method is `RM-02`'s and it is used deliberately, because `RM-02` is the
ticket that retired the validation dimensions and a successor arguing with it
should be checkable by its own instrument. Every figure below re-derives in
about two seconds from the 87 sealed cards:

```
python3 specs/results/scorecards/score-drives-validation/\
GOAL-validation-is-scorable/SV-02/analysis/scorability.py
python3 specs/results/scorecards/score-drives-validation/\
GOAL-validation-is-scorable/SV-02/analysis/carrier_cost.py
```

**Scope, stated first (`R3`).** The corpus at `a527305` is **87 sealed cards,
399 scored rationales and 36 recorded notes**. Of the 87 cards, **63 are the
example `ab_quota_ledger`**, 8 `toolchain_removal`, 6 `eval_toolchain`, and 10
are two cards each of five fixtures. Card versions: 31 at v1, 8 at v2, 36 at v3,
10 at v4, 2 at v5. Every figure here is a figure about that population and about
no wider one, and where a figure is true of one example it says which. Nothing is
averaged across examples or across card versions (`R-H1`, `R-H2`).

---

## 1. The answer

**YES — validation is scorable without grading a toolchain, and the property
that does it was already written into this card and was never the thing that
failed.**

The property is one sentence:

> **The artifact's own checking has a demonstrated red, and the region where it
> stays green is named.**

Call it **demonstrated refutability**. It says nothing about where a case came
from. Hand-written, generated, property-based, fuzzed and model-derived all
satisfy it or fail it identically. It is `R1` — *an instrument ships with a
demonstrated failing input on a real subject* — turned around and pointed at the
subject instead of at our own instruments.

**And the second answer, which matters as much: it should NOT be carried by a
scored rung.** Measured in §6, a rung costs **+682 bytes and four permanent
anchors** on a 6,281-byte surface that must not grow, plus a production change,
a version bump and a mandatory re-score. Sharpening the note prompt that already
elicits the property costs **−15 bytes, or exactly 0**. The cheap carrier is not
a compromise here; on this record it is the better instrument, for a reason §5
gives.

**What was actually wrong with D1 and D4 was three clauses, not two dimensions.**

| | the clause | what it asks |
|---|---|---|
| D1 anchor 3 | *"a class the whole-view corpus structurally cannot reach"* | own our corpus |
| D1 anchor 4 | *"derived from the model rather than hand-written"* | own TLA+ and the generator |
| D4 anchor 3 | *"the check is model-derived (a corpus, a TLC invariant)"* | own TLA+ and the generator |

Every other rung on both ladders names no tool at all. **D4's top rung is the
property this page proposes, written by a predecessor and shipped for three
versions** — *"a deliberate behavior-breaking change is shown to be caught — the
check is demonstrated to be capable of failing"* — and **D1's floor is its
negation**, *"cases exist and
pass; no seeded fault is caught. A suite that is green on broken code."* Both are
in `references/eval_scorecard.md` under `Retired anchors, versions 1–3`, which is
where they live and where this page deliberately does not restate them, for the
reason `tests/test_card_has_one_home.py` executes.

**The property was not unreachable. It was buried under a rung that was.**

---

## 2. The autopsy, run RM-02's way

`RM-02` measured how often an **anchor decision** cites this project's own
machinery in the same sentence. Re-derived at `a527305` over all 87 cards, its
figures hold and the corpus has grown by 14 cards since:

| | RM-02, 73 cards | this tree, 87 cards |
|---|---|---|
| **D1** | 38% | **37%** (28 of 75) |
| **D4** | 18% | **17%** (13 of 75) |
| D2 | 4% | 3% (3 of 87) |
| D3 | 0% | 0% (0 of 87) |
| D5 | 0% | 0% (0 of 75) |

**That is the number to beat, and the candidate is measured against it with the
same patterns.** `scorability.py` copies `LOCAL_TERMS` and `ANCHOR_DECISION` out
of `portability.py` unchanged, and says so in a comment, so the two figures are
comparable rather than merely adjacent.

A **demonstration sentence** is one where a named break meets a red-or-green
outcome of the subject's own checking. The patterns contain no word about
provenance — that is what makes this a test of the candidate rather than of D1.

**THE AUTOPSY FRACTION: 44 of 315 demonstration sentences in the whole record —
14.0% — cite this project's machinery.** Against D1's 37%, that is better; on its
own it is not good enough, and the decomposition is where the answer is:

| where the sentences live | n | citing local machinery |
|---|---|---|
| D1 rationales | 125 | 25 (20%) |
| D4 rationales | 75 | 12 (16%) |
| D2 rationales | 29 | 3 (10%) |
| D3 rationales | 28 | 1 (4%) |
| D5 rationales | 22 | 1 (5%) |
| **N-D1 notes — the same question with the ladder REMOVED** | **30** | **1 (3%)** |
| N-D4 notes | 4 | 1 (25%) |
| N-D5 notes | 2 | 0 (0%) |

**The last two rows are 6 sentences and carry no rate**, and are printed only so
the table sums to 315.

**The machinery is attached to the ladder, not to the property.** The same
question, asked of the same judges on the same subjects with no rungs beneath it,
falls from 20% to **3%** — one sentence in thirty. That is not a rounding
difference from D3's 0%, and it is the single strongest number in this ticket.

**And the concentration is total.** Of D4's 13 machinery-citing anchor decisions,
**13 name anchor 3**. Of D1's 28, **26 name anchor 3 or anchor 4**. Nothing is
diffusely local about either dimension; three clauses are.

### 2.1 The candidate is not D1 wearing a hat

If the property only ever appeared under D1, it would be D1. It does not:
**160 of 315 demonstration sentences — 51% — are written under D2, D3, D4, D5 or
the notes**, by judges who were not being asked about bug detection at all. D3's
28 are the interesting ones, because D3 is the dimension the card kept and its
anchor decisions are 0% local. Judges reach for a demonstrated red whatever rung
they are standing on.

---

## 3. Why D4 was retired, and why the stated reason does not survive checking

`references/eval_scorecard.md` gives three one-line reasons for the version 4
retirements. D4's is: *"N-D4 tier-split on 4 of the 8 judge groups scored by both
`opus` and `sonnet`, more than any other dimension."*

The instability is real and at this tree it is **5 of 9 groups**. What the card
presents as an independent reason is not independent:

| group | opus | sonnet | lower tier names the model clause |
|---|---|---|---|
| `portable-substrate` / `ab_quota_ledger` / T | [2] | [3] | 1 of 1 |
| `reading-discipline` / `ab_quota_ledger` / D | [4, 4] | [2, 2] | 2 of 2 |
| `reading-discipline` / `ab_quota_ledger` / M | [4, 4] | [2, 2] | 2 of 2 |
| `reading-discipline` / `ab_quota_ledger` / N | [4, 4] | [2, 2] | 2 of 2 |
| `subtract-to-measure-sm05-greenfield` / `ab_quota_ledger` | [2, 2] | [3, 3] | 2 of 2 |

**In 5 of 5 D4 tier-split groups, every card on the lower side names the model
clause as its ceiling.** The `reading-discipline` rows are the sharpest: three
arms, a two-point gap each, and all six `sonnet` cards refuse anchor 3 in almost
the same words — *"a mutation check is not a model-derived check"*, *"there is no
TLA+ spec or generator anywhere in this tree"*, *"everything here is
hand-written"* — while all six `opus` cards read the same clause as an
illustration, clear it, and go to 4.

**This is the mechanism `RM-02` proved for D2's anchor 4, now shown for D4's
anchor 3, in the same direction and by the same tier.** `RM-02` called the D2
case *"the single strongest evidence that the local clause is what makes the card
local."* D4 is the second instance and it was not looked for.

The consequence for this ticket is narrow and it is the whole argument:
**D4's instability is a symptom of the clause, so it cannot also be an
independent reason to distrust the rest of the ladder.** Filed as `SV-02-DF-01`;
the card's own sentence is a predecessor's statement at a predecessor's scope and
is not edited.

**What the counterfactual would be, stated as a counterfactual.** Four of the six
lower-tier `reading-discipline` cards report a caught break in their own prose
before refusing the rung — `rd03M-M-p3` says the fault it reproduced *was*
caught and by hand-written pytest; `rd03N-N-p4` re-ran the artifact's mutation
check and reproduced 11 of 12 caught. Under a provenance-free ladder those cards
have their evidence for the top rung already written down. **That is a reading of
sealed prose and not a measurement**, and it is exactly the claim a re-score
would have to settle. It is `SV-07`'s, not this page's.

### 3.1 The other thing wrong with D4's top rung, and it is not the clause

At versions 2 and 3 the served card carried this, verbatim, in the judging
practice block:

> **D4's anchor 4 is only awardable when this says `true`** …

**The top rung of the validation dimension was gated on a fact about the judge's
session.** The cards agree: of the 19 cards at D4 = 4, **11 of the 11 that carry
the `executed_own_faults` field say `true` and none says `false`** (the other 8
are version 1 cards, which predate the field). Version 4 de-gated every anchor
from judging practice and the served text now says so.

**So a restored rung must ask for the ARTIFACT's demonstration, not the judge's.**
A judge who seeds a fault and watches it die has learned something about the
artifact's checking; an artifact whose own record contains that demonstration has
*shipped* something. Only the second is a property of the subject, and only the
second is comparable between two artifacts scored by different judges. The record
prices the difference: **`executed_own_faults` is `true` on 52 of 87 cards
(60%)**, and the four cards where it is `false` produced the only note in the
corpus that demonstrates nothing at all.

---

## 4. What the property looks like when nobody is holding a ladder

The 12 cards at versions 4 and 5 answer D1's question as prose with no rungs.
They are the closest thing the record has to an experiment on this question, and
they are worth reading rather than summarising — `20260811-cl03v5-CL-p1` and
`-p2`, `20260810-v4-T-p1`, `20260810-rm04-GG-p1`.

What the judges converged on, unprompted and without agreeing with each other:

1. **A named break.** *"M1 gutted every filesystem call out of
   `journal_file.py:32-38`"*; *"`_Tenant.quota` deleted in a scratch copy"*;
   *"`sorted(..., reverse=True)` at the same line"*.
2. **The subject's own checking run against it, with a denominator.** *"all 28
   cases passed"*; *"died 5 of 28 under the real wiring and 0 under the fake"*;
   *"SURVIVED all 53 cases"*; *"0/56"*.
3. **The green region named, with the reason it is structural.** *"Append-only-ness,
   on-disk line format, and the file existing at all are unobservable to this
   suite by construction, not by oversight."*

Not one of those three needs a tool anyone else has to own. The denominators are
the artifact's own case count. **The one machinery-citing sentence in all 30 is
`rm04-LL-p1`'s** — *"no generated case has ever executed against `scripts/`"* —
and it is machinery-citing because in that round **our toolchain was the
subject**, which is a different thing from an anchor requiring it.

**The grades vary**, which is what D1's number never did. `demonstration_grade`
in the analysis is a crude regex read of the prose and is **not** a proposed rung;
its only job is to answer whether the property moves. Over the 12 notes it
returns four distinct values, and it separates the two honest nulls —
`rm04-JJ-p2`'s *"I did not execute anything in this scope"* and `rm04-LL-p2`'s
*"I could not tell, and here is what I looked at"* — from the four that carry a
break, a denominator and a named region. Against that, on the example
`ab_quota_ledger`, **D1 = 3 on 56 of 63 cards** — 61 of the 63 carry a D1 score
at all and 56 of them read 3 — while the prose inside those very cards spans the
grade's whole range. **D1's number was discarding signal that was already written
in D1's own rationale.**

---

## 5. Models, adapter surfaces, and diagrams

The owner's goal names *improved architecture and diagrams* and validation
derived from them. The three parts have three different answers and only one of
them is good news.

**An adapter conformance surface: YES, already, with zero toolchain
dependence.** D3's anchor 4 — *a driven port exercised by a real adapter and a
fake, with the same cases passing against both* — names no tool, and **0 of 87
D3 anchor decisions cite local machinery**. It has been reached on **22
`ab_quota_ledger` cards**, 3 `toolchain_removal` cards and 1 `eval_toolchain`
card. And D3's version 5 caveat *is* demonstrated refutability applied to the
port: *if the only observer of the effect the port exists for is the adapter that
wrote it, take 3.* **That caveat fired correctly on a stranger's artifact it was
never written for** (`CL-04` §8), authored by an agent forbidden our source.
**The property has already travelled, blind, to somebody who is not us.** Nothing
needs building for this; it needs noticing.

**A TLA+ model: yes in principle, and NOT ON THIS RECORD.** Judges do cite models
— 36 citations at a `.tla`, `.cfg` or `program_model` path, spread over five
examples, all of them fixtures the project wrote — and two statements in the
corpus are demonstrated refutability applied to a model rather than to code:

> *"the invariant `LedgerIsDownstream` is written weakly enough … to pass
> vacuously on the half that matters"* — `ex4_pipeline_coherent`, D4

> *"the invariant-coverage section counts a `TypeOK` type conjunct as a semantic
> read, so write-only variables show clean coverage"* — `ex3_over_complex`, D5

The first needs TLA+ literacy and nothing of ours. The second is about **our**
coverage checker and would not transfer. **No anchor in the record has ever been
awarded or refused on a model's discriminating power**, so a claim that a model
can be scored this way is unfalsified rather than supported, and it is `SV-07`'s
open question. What is settled is the negative: **the moment "has a model"
becomes a rung, D1 anchor 4 is back.** A model is one possible source of checks
and the property must read it the way D2's preamble already reads the complexity
descriptor — *where none exists that is not a gap in the evidence.*

**A diagram: NO. There is nothing to build on.** The string `diagram` and every
variant of it — `mermaid`, `UML`, `C4`, `.svg` — appears in **0 sentences across
0 of 87 cards, 399 rationales and 36 notes.** Seven epics of judging have never
once looked at a picture. The property applies in principle (a diagram is a
claim, and the question is whether anything goes red when the code stops matching
it), but **inventing a rung for a surface with no evidence is `MF-020` in the
form the project has already refused twice.** If the owner wants diagrams scored,
the first act is a round in which one is scored, not an anchor.

---

## 6. The carrier, costed in bytes

The surface metric is `serve | wc -c`: **6,281 bytes, 9 rungs**. Every figure
below comes out of `carrier_cost.py`, which calls the **real** renderer, so these
are the bytes a judge would be handed and not an estimate of them.

| carrier | bytes | rungs | delta |
|---|---|---|---|
| v5 as shipped | 6,281 | 9 | — |
| **P1** — note prompt asks for the denominator and the structural reason | 6,266 | 9 | **−15** |
| **P2** — note prompt adds *"who wrote the cases is not an input"* | 6,281 | 9 | **0** |
| **P3** — both | 6,303 | 9 | +22 |
| P4 — both, verbose | 6,419 | 9 | +138 |
| **R** — restore D4 as a scored dimension, drop the N-D4 note | 6,962 | **13** | **+682** |
| N — a new sixth dimension, notes kept | 7,162 | 13 | +882 |

**P1 and P2 are free and P1 is negative**, and the reason is a deduplication
rather than a trick: N-D1's current prompt ends *"Name the fault you seeded if
you seeded one"*, which the served surface **already asks twice** — scoring rule
8 and the whole `Judging practice — REQUIRED` block. Spending those bytes on the
denominator and on the provenance clause is a strictly better use of text a judge
is already reading.

**R costs more than its bytes.** `serve` refuses a version 5 rubric that carries
D4 anchors, and the refusal was run rather than predicted:

```
REFUSED: …: declares scorecard version 5 and still serves anchors for D4.
A retired dimension is kept in the file under `Retired anchors` …
```

So R additionally requires: a change to `scored_dims` and `note_dims`; an entry
in `TOP_SCORE_V4` if the scale is not 0–4, because `top_score` returns 4 for any
dimension not in that dict; a bump to version 6; and the change rule's re-score
of at least one prior example under both versions. **And four permanent anchors
on a card whose change rule forbids deleting a shipped one.** Against a note
prompt, which costs nothing and can be rewritten next epic.

**The recommendation is P1 or P2, and the decision between them belongs to
whoever writes it, because they differ by which half of §1's sentence is
explicit.** The proposal this page defends:

> *What went red when you broke it, with the denominator, and what class stays
> green by construction?* — **−15 bytes, 9 rungs, no anchor.**

**This is not "the property is too weak for a rung."** It is that the property is
already being elicited at full strength by a note, the notes are richer than the
scores they replaced, and the one thing a rung buys — a number to key a goal to —
can be had from **the denominator the note already carries**, which is a number
without a ladder. `5 of 28` is comparable across a before and an after of the
same artifact, which is what `SV-04` needs and all `R-H2` permits. It is not
comparable between two artifacts, and it should not be.

---

## 7. What the blind adopter's blockers say

`CL-04`'s probe is the only evidence in the record from someone who was not us,
and three of its fifteen blockers bear on this ticket.

- **Its blocker 1 is demonstrated refutability, fired at us.** *"The architecture
  axis is a check that cannot fail when under-installed … the probe then pointed a
  subject's `scope` at a directory that does not exist and got byte-identical
  output."* An outsider, with no vocabulary from this page, reached for exactly
  the property this page proposes and applied it to our instrument. That is the
  strongest available evidence that the property is not ours: **it is what
  somebody who was not us used to judge us.**
- **It rejected a score on the same grounds.** It refused D3 = 4 on its own
  artifact because *"nothing but `JsonFileStore` ever reads the JSON file"* —
  a green region named, with the structural reason. It did that from the served
  caveat alone, under a card it had bumped itself.
- **And the warning for `SV-03`.** Its blocker 2 is that a card bump made
  `INSTRUMENT-LOG.toml` and `[[movement]]` mandatory at the next `audit` and the
  format is documented nowhere; it brute-forced four wrong shapes. **Carrier R
  requires a version bump and would hand every adopter that experience.** The
  free carriers do not.

**What it does not establish**: one adopter, one artifact, self-judged. n = 1.

---

## 8. What this scopes for the successors

- **`SV-03`** — validation IS scorable, so the ticket does not shrink to
  architecture. But **the keyable quantity is a denominator inside a note, not a
  dimension score**, and a goal that keys to it keys to *this artifact, before and
  after*, never to a cross-artifact comparison. If the wiring needs a scored
  dimension it has D2 and D3 today and should use them; validation arrives as a
  note with a number in it.
- **`SV-04`** — the harvest classes it must consume are overwhelmingly this
  property already: `B1`–`B6` are checks that cannot fail, `C1`–`C7` are gates
  reporting clean on broken input, `D1`–`D7` are numbers with nothing behind them.
  **A closure that turns one of those into a case whose denominator moves is the
  loop reaching the program**, and the before-number is already sealed in a card.
- **`SV-07`** — carries §5's model question and §3's counterfactual, both listed
  in §9.

---

## 9. What this ticket could NOT settle

- **Whether a provenance-free ladder would actually close D4's tier split.** §3's
  counterfactual reads six sealed rationales and finds the top-rung evidence
  already written in four of them. That is a reading, not a re-score, and only a
  round with fresh judges under both wordings decides it. It is also the one
  experiment that would make Carrier R defensible, and nobody should adopt R
  before it runs.
- **Whether a TLA+ model can be scored on its discriminating power.** Two
  statements in the record do it; no anchor has ever turned on it; and the
  fixtures involved are ours. §5.
- **Whether the notes are richer than the scores because the ladder went, or
  because the rounds got better.** The 12 note-bearing cards come from two rounds
  three epics later than most of the corpus, with different judge models and a
  different subject mix. **This confound is not controlled and it is the main
  bound on §4.** What is *not* confounded is §2's decomposition and §3's 5 of 5,
  because both compare cards within the same round.
- **What the property costs an adopter.** Everything here is priced from rounds
  where we wrote both the artifact and the instrument. `RM-02` §7 said the same
  and it is still true.
- **Whether `demonstration_grade` measures anything.** It is a regex over prose,
  it has never been validated against a human read, and it is used here for one
  purpose only — showing that the property varies where D1's number did not.

---

## 10. What was REJECTED

- **A sixth dimension for validation.** +882 bytes, four permanent anchors, and
  `RM-02` rejected the same shape on sight for adoptability. Priced in §6 and
  left there so the price is visible rather than asserted.
- **Restoring D1.** Its ladder is 20% local in its own rationales and its number
  read 3 on 56 of 63 cards of `ab_quota_ledger`, the only example the project
  scores at scale. Nothing in this
  page argues for it, and repairing anchors 3 and 4 does not save it: **anchor 1
  turns on "a value the projection already prints", and `projection` is our word
  for our thing** — so the locality reaches a rung the clause repair does not
  touch. Its floor and its top are the property; the three rungs in between are
  not.
- **Restoring D4 with anchor 3 deleted — rejected FOR NOW, not on principle.**
  This is the closest call in the ticket and the honest position is that the
  evidence supports the anchor and not yet the rung: 13 of 13 of D4's machinery
  citations sit on that one clause, its distribution on `ab_quota_ledger` is
  {1:1, 2:26, 3:16, 4:18} against D1's {0:1, 2:1, 3:56, 4:3}, and its top rung is
  already the property. What is missing is §9's first bullet. **Adopting R before
  that round is fitting a rung to an answer we like, which is `MF-020`.**
- **A dimension asking "do you have model-derived cases", in any wording.** The
  trap named in the work order. It is D1 anchor 4 and it fails for the reason
  measured in §2.
- **A rung for diagrams.** Zero evidence in 87 cards. §5.
- **Scoring the judge's demonstration rather than the artifact's.** §3.1. It is
  what the version 2 gate did, and 11 of 11 D4 = 4 cards carrying the field say
  the judge ran something.
- **A check that a note carries a denominator.** `no_new_gates_rule`, and seven
  epics of static checking that caught nothing. If a judge writes a note with no
  number, that is a fact about the round and the round should say so.
- **Rewriting `eval_scorecard.md`'s retirement sentence for D4.** A predecessor's
  statement at a predecessor's scope is filed (`SV-02-DF-01`) and left standing,
  the way `RM-02` left `architecture_tags.md` §2.2.

---

## 11. `scope` run over this page

```
python3 examples/validation/scorecards/score_tools.py scope
```

**Every row names its tree.** The sweep is a joint property of the record and the
card population and moves when either does, so it is run at the ticket's branch
point and again with this page present.

| tree | counted | REFUTED | COUNT-MOVED | HOLDS | UNREACHABLE |
|---|---|---|---|---|---|
| `a527305` — branch point, without this page | 92 | 67 | 0 | 5 | 20 |
| `a527305` + this page — **the reconciled tree** | **93** | **67** | **0** | **6** | **20** |

**SV-02's delta: +1 counted, +1 HOLDS, REFUTED and UNREACHABLE unchanged.**

**And the checker refuted this page's first draft, which is the part worth
recording.** The figure in §4 was written as *"D1 scored 3 on 56 of 61
`ab_quota_ledger` cards"* and `scope` returned *"re-derives as 56 of 63, not 56
of 61 — the denominator moved"*. It was right: 63 cards of that example exist and
two of them carry an `N-D1` note instead of a D1 score, so a denominator of 61
silently drops the two cards where the number stopped existing — which is the
exact fact this page is about. **The figure was RE-SCOPED and not rephrased**,
which is the opposite of what `RM-02` §9 had to do with its own D2 figure, and
the `denominator_rule` earned its keep on the first page that tried to argue
against the ticket that wrote it.

**The bound that applies is `RM-02-DF-05`:**
`scope`'s counted-noun pattern admits no underscore, so `ab_quota_ledger` written
immediately after a count is refused before the search for a named example runs.
Every figure in this page that names that example therefore establishes the scope
in the two lines before the count, and the ones that do not — the D4 tier-split
table in §3, the byte table in §6 — carry no bind-and-value form at all and are
invisible to the checker rather than checked by it. That is `RD-02-DF-01`, stated
here rather than left for a reader to find.
