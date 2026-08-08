# Architecture Tags

**RD-04 research output, IMPLEMENTED BY RD-05 — see [§13](#13-what-rd-05-shipped-and-what-it-left-open).**
Sections 1–12 are RD-04's and are not rewritten; §13 records what shipped, what
RD-05 settled and how, and which of §9's ten questions are still open. Every
figure below carries the example it was computed over — the scope-carrying rule
this epic exists to add applies first to this page.

The shipped surface is `examples/validation/scorecards/architecture_tags.py`,
its declared scopes are `examples/validation/scorecards/subjects.toml`, and the
one row that grants a refusal is a `[[demonstration]]` in
`specs/results/scorecards/INSTRUMENT-LOG.toml` that `audit` re-derives on every
run.

The evidence is `specs/results/scorecards/reading-discipline/GOAL-tags-earn-their-place/RD-04/`.
The analysis that produced it is `analysis/derive_and_test.py` in that directory
and it re-runs from the repository root in about ten seconds.

---

## 1. What is broken, measured rather than argued

**The card is not comparable across architectures and nothing records which
architecture a score describes.**

Three facts from the sealed record, each stated at its own scope:

- On the example `ab_quota_ledger`, across eight rounds, three card versions and
  34 judged cards, **D3 takes 4 on all 10 cards of the subject `arm_b` and never
  rises above 2 on any of the 24 cards of the subjects `arm_a` and `arm_c`.**
  The ranges are disjoint. No other dimension separates: D1, D2, D4 and D5 all
  overlap between the same two groups.
- On the example `toolchain_removal`, D3 came out **2, 2, 3, 4** — a spread of 2,
  the only group in 49 sealed cards that `contested` fires on. The two judges who
  scored it 2 recorded that **no new evidence would settle it**, and one named
  the cause exactly: *"D3 at the 2→3 seam, where 'the domain' silently changes
  referent"* (`K-p1`). Re-reading the four cards' own D3 citations confirms it:
  **the four judges scored three different subjects.** Two cited `scripts/`, one
  cited `spec_double_compiler/`, one cited
  `examples/validation/ab/reference_ports/`. Within each of those three scopes
  the spread is **zero**.
- `R-H1` already carries two comparability axes — same example, unchanged
  instrument. Architecture is a third, and it has been handled by prose telling
  readers that `ex6_jenga` is *supposed* to score low on D3.

The mechanism is visible in the toolchain and is not a matter of taste: a
ports-and-adapters program is validated through port-bound adapters and per-port
cases; a flat effectful program is validated through the effect oracle, which is
in-process CPython only. **Same D1 anchor, different instrument reach.**

---

## 2. The vocabulary

**One axis. Two values that ship with refusal authority, and a closed set of
non-values for everything else.**

### 2.1 The axis: `effect_boundary`

Where the outside world is touched, relative to where the program's state and
rules live. It is the axis D3's anchors 3 and 4 are written about — read them in
`references/eval_scorecard.md`, which is where they live and where this file
declines to repeat them — and it is the only architectural property the sealed
record demonstrates changes a score.

| value | meaning | authority |
|---|---|---|
| `ports-and-adapters` | a seam is declared away from the effect surface, the state does not live where the effects are, and a second implementation exists behind the seam | **demonstrated on D3** |
| `effectful` | the modules holding the state also make the effectful calls; no seam | **demonstrated on D3** |
| `UNDERIVABLE:<reason>` | derivation ran and could not decide | **none — always comparable** |
| `UNDEMONSTRATED:<name>` | a candidate value recorded for a future round | **none — always comparable** |

`UNDERIVABLE` and `UNDEMONSTRATED` are not architectures. They are the two ways
the tag is allowed to say nothing, and saying nothing must never be worth more
than saying something. See [§5](#5-the-suppression-key-attack).

### 2.2 The values are nominal, never ranked

`ports-and-adapters` is not a better value than `effectful`. The moment one is
better the tag is a target, and MF-020 applies: a tag moving is not evidence the
design improved. Nothing in the design sorts, sums, or prefers a value.

### 2.3 What is deliberately NOT tagged, and why

**The quality of the boundary.** `ex5_pipeline_divergent` is the fixture built to
declare boundaries the code does not follow; both blind judges scored it
**D3 = 1** against `ex4_pipeline_coherent`'s **D3 = 3**. No clause of the
derivation in [§3.1](#31-what-is-derived) tests whether a declared boundary is
*followed*, deliberately: that is what D3 anchors 1 and 2 score, and a tag that
could make the distinction would be doing the dimension's job. **The tag names
the shape the anchors assume; the dimension scores how well the artifact holds
it.**

*Stated as a limit rather than a claim:* the record cannot show that the
derivation does not accidentally make the distinction. `ex5` is refused by the
`no-effect-surface` guard before any of the three clauses can be tested on it
(see [§4.3](#43-where-it-fails-on-the-record)), so **no artifact in this corpus
tests that separation of concerns.** It is a design intention with no
demonstration behind it.

**Subject shape — greenfield versus before/after.** This is the class that cost
`subtract-to-measure` its founding premise, and it is *not architecture*.
Folding it into an architecture tag would be the first suppression key: it would
let a low D2 be waved off as "different architecture" when the actual cause is
that D2's anchor 3 requires a recorded before and after. It is treated in
[§9.4](#94-subject-shape-is-not-architecture-and-is-not-demonstrated-either),
where the measurement also declines to support it.

**Instrument reach.** The effect oracle drives 8 of 18 actions in-process; a
port-bound adapter set drives per-port cases. That is a fact about the
*instrument*, and `R-H1` already owns the instrument axis. The architecture is
*why* the reach differs. Tagging it here would let one fact refuse a comparison
twice.

**Language, framework, layering vocabulary, dependency-injection style, port
count, test-suite architecture.** No demonstrated separation on any dimension in
49 cards. Adding any of them is the proliferation attack in taxonomy clothing.

---

## 3. Derived versus declared

### 3.1 What is derived

The tag value is **computed**, from figures `scripts/code_complexity.py` already
emits. Nothing new is measured and no new instrument ships.

Over `role=code` modules of the declared scope, `ports-and-adapters` requires
**all three** clauses:

| clause | figure | why this one |
|---|---|---|
| **(a)** a seam declared off the effect surface | some module has `declared_interfaces ≥ 1` **and** `effectful_calls == 0` | a `Protocol` declared next to the file writer is the same coupling with an extra file |
| **(b)** the state does not live where the effects are | `instance_state_in_effectful_modules / instance_state < 0.5` | D3's anchor 3, read as a question about **where behaviour lives** rather than about import topology. The anchor's wording stays in the card; this file does not restate it |
| **(c)** a second implementation is present, not promised | at least one code module with `effectful_calls > 0` and at least one with `instance_state > 0, effectful_calls == 0, declared_interfaces == 0` | a port with one implementation has never been swapped and nobody knows whether it can be |

Otherwise `effectful`. If **no** code module makes an effectful call,
`UNDERIVABLE:no-effect-surface` — D3 anchor 3 has no referent and neither value
can be asserted. If `parsed_fraction < 1.0`, `UNDERIVABLE:unparsed`.

**Import topology is deliberately not a clause.** Round 2 proved a codebase can
pass every import check with its coupling intact, and
`ex5_pipeline_divergent` carries `declared_interfaces = 1` and
`internal_import_edges = 18` while scoring D3 = 1 from both blind judges.

**`ex5_pipeline_divergent` is therefore a demonstrated failing input for the
naive predicate `declared_interfaces ≥ 1`**, which would tag it
`ports-and-adapters`. Exactly: it satisfies clause (a) and clause (b), fails
clause (c) — it has no effectful module for a second implementation to sit
opposite — and in practice the `no-effect-surface` guard refuses it before any
clause is reached. Two independent reasons, both recorded, and neither is
clause (a).

Measured on eleven declared scopes: the nine the sealed cards were scored over,
plus `reference_ports/` and `spec_double_compiler/`, which judges' own D3
citations named and which [§4.2](#42-the-contested-spread-decomposed) needs.

| subject (declared scope) | iface | eff mods / code mods | state co-location | derived |
|---|---|---|---|---|
| `arm_b` (`blind/artifact_T`) | 1 | 1 / 4 | 0.125 | `ports-and-adapters` |
| `arm_a` (`blind/artifact_U`) | 0 | 1 / 1 | 1.0 | `effectful` |
| `arm_c` (`blind/artifact_W`) | 0 | 1 / 1 | 1.0 | `effectful` |
| `scripts/` | 0 | 28 / 31 | 1.0 | `effectful` |
| `examples/validation/ab/reference_ports/` | 1 | 1 / 5 | 0.111 | `ports-and-adapters` |
| `ex1_scaffold_only` | 0 | 1 / 1 | — | `effectful` |
| `ex4_pipeline_coherent` | 1 | 1 / 21 | 0.100 | `ports-and-adapters` |
| `ex3_over_complex` | 0 | 0 / 1 | — | `UNDERIVABLE:no-effect-surface` |
| `ex5_pipeline_divergent` | 1 | 0 / 16 | 0.0 | `UNDERIVABLE:no-effect-surface` |
| `ex6_jenga` | 0 | 0 / 6 | — | `UNDERIVABLE:no-effect-surface` |
| `spec_double_compiler/` | 2 | 0 / 3 | — | `UNDERIVABLE:no-effect-surface` |

**The derivation decides 7 of 11 subjects and refuses 4, and every refusal is
the same reason: the tree touches no outside world at all.** That is reported as
a refusal, not as `effectful`.

### 3.2 What must be declared

**The scope.** Which paths are the subject. Nothing can compute this: a
repository contains a toolchain, a library and a fixture, and `toolchain_removal`
proves four judges will pick three different ones. Scope is a path list, it is
written into the **unfilled skeleton by `scaffold`**, before any judge is
dispatched, and `check` refuses a filled card whose scope differs from the
skeleton's. That reuses the machinery that already refuses a second scaffold over
a measurement; it invents nothing.

**The declared value.** Also written before scoring, also into the skeleton. It
exists so that derivation and declaration can *disagree*, which is information.

**Composite subjects.** A program that is one thing wrapping another declares
**more than one scoped subject**, and each one gets its own card. `effectful`
and `ports-and-adapters` are not exclusive at the level of a repository; they are
exclusive at the level of a scope. This is the whole fix for
[§4.2](#42-the-contested-spread-decomposed).

### 3.3 When derivation and declaration disagree

| case | what is recorded | what has refusal authority |
|---|---|---|
| agree | `agreement: "agree"` | the derived value |
| differ, both derivable | `agreement: "TAG-DISPUTED"`, both printed | **the derived value** |
| derivation refuses | `agreement: "UNDERIVABLE"`, declared value printed | **nothing** |

**The derived value always wins, and a refusal to derive always fails open.**
An author who has seen the numbers can edit a declaration; they cannot edit
`instance_state_in_effectful_modules` without moving the state out of the
effectful module, which is doing the work D3 measures. That is the card's own
argument for judgement over metric — *gaming it requires doing the work* — applied
to the tag.

`TAG-DISPUTED` is never corrected and never blocks anything. It is a prompt to go
and look, in the sense R-H3 already uses. Three of the eleven subjects above
disagree with their declaration and all three are the `no-effect-surface`
refusal — including `ex5_pipeline_divergent`, declared `ports-and-adapters` by a
reader of its own prose.

---

## 4. What the vocabulary explains in the sealed record

49 cards, seven examples, two architectures. **48 map to a scoped subject; 1 does
not** (`hexagonal-prompting/20260804-owner-pre`, the owner's non-blind
pre-treatment pass, `pass: 0`, which decides nothing and is counted here rather
than dropped).

### 4.1 The earn-its-place result

Within the example `ab_quota_ledger`, comparing the 24 cards whose subject
derives `effectful` against the 10 whose subject derives `ports-and-adapters`:

| dimension | `effectful` (n=24) | `ports-and-adapters` (n=10) | verdict |
|---|---|---|---|
| D1 | 2–4 | 3–4 | overlaps |
| D2 | 2–2 | 2–2 | overlaps — **NULL-ENTAILED**, see [§7.3](#73-null-entailment-which-of-the-four-overlaps-verdicts-are-measurements) |
| **D3** | **1–2** | **4–4** | **SEPARATES** |
| D4 | 2–4 | 2–4 | overlaps |
| D5 | 2–4 | 3–4 | overlaps |

**The axis earns its place on D3 and on nothing else** — with the caveat that
three of the four `overlaps` cells are measurements and **D2's is not**: that
dimension took a single value across the entire population, so no separation was
possible on it and the cell reports the example rather than the tag. That is the measured
answer and it is what the design is built around: refusal authority is granted
per dimension, and on D1, D2, D4 and D5 a "different architecture" objection is
simply not available.

**The same-tag control holds.** `arm_a` and `arm_c` are two different subjects of
the same example that derive the *same* value. If the D3 separation were about
something other than the tag, they should separate too. They overlap on all five
dimensions, D3 included (`arm_a` 1–2, `arm_c` 1–1). The separation is not
reproduced by an arbitrary pair.

**The verbosity confound is partly controlled by the record itself.** `arm_c` is
the length-matched control built at PA-06 — +3.8% unique content over `arm_b`, 0
of 109 architectural terms — and it lands with `arm_a`, not with `arm_b`. Longer
prompts do not produce the D3 separation; the architecture does. The *author*
confound is not controlled and is [§9.6](#96-three-arms-three-authors).

### 4.2 The contested spread, decomposed

`toolchain_removal` D3 = 2, 2, 3, 4 is the only contested group in the record and
the only tier split on D3. Attributing each card to the scope its own D3
citations name — mechanically, by counting path references in the sealed cards —
gives:

| card | tier | D3 | scope its citations name | derived tag of that scope |
|---|---|---|---|---|
| `K-p1` | opus | 2 | `scripts/` | `effectful` |
| `K-p2` | opus | 2 | `scripts/` | `effectful` |
| `K-p4` | sonnet | 3 | `spec_double_compiler/` | `UNDERIVABLE:no-effect-surface` |
| `K-p3` | sonnet | 4 | `examples/validation/ab/reference_ports/` | `ports-and-adapters` |

**Within each scope the spread is zero.** `K-p1` says in its own citation list
that it *rejected* the anchor-4 evidence "because this is a fixture, not the
toolchain"; `K-p2` records the same rejection; `K-p3` cites the fixture and
nothing else. Both opus judges cite the exact figures this design derives on —
`declared_interfaces 0, modules_with_effectful_calls 30 of 33` — as their reason
for not reaching anchor 3.

So the design would have made this spread **interpretable**: not four judges
disagreeing about one artifact, but four judges scoring three subjects, which is
`R3` — a claim carries its scope — applied to the artifact instead of to the
claim. And the judges were right that no new evidence could settle it. The fix is
a declared scope on the next round, not a third judge on this one.

**Stated as a limit, not sold as a result:** scope choice and judge tier are
perfectly confounded in these four cards (both opus judges chose `scripts/`, both
sonnet judges did not). This shows the spread is *explained by* scope. It does
not show tier is not also a factor, and RD-01's other two tier splits are
untouched by it.

### 4.3 Where it fails on the record

- **It does not explain the D2 greenfield class.** See
  [§9.4](#94-subject-shape-is-not-architecture-and-is-not-demonstrated-either).
  On the example `ab_quota_ledger`, D2 is 2 on 35 of 35 cards — under both
  architectures and both subject framings. Architecture explains none of it.
- **It does not explain `arm_a` D3 = 2 against `arm_c` D3 = 1.** Same derived
  value, one point apart, six cards to eighteen. Whatever separates them is not
  in this vocabulary, and the design says so rather than growing a value to
  cover it.
- **It refuses four of the eleven subjects**, including three of the five
  `architectural-coherence` fixtures. Those examples become permanently
  comparable-to-everything, which is the correct fail-open behaviour and is also
  the reason the axis has only ever been *tested* on one example.
- **It has never been tested in the `sonnet` tier on a `ports-and-adapters`
  subject.** n = 0. See [§9.1](#91-the-separation-is-demonstrated-in-one-tier).

---

## 5. The suppression-key attack

**A tag can become a suppression key.** If any unflattering comparison can be
waved off as "different architecture", the card stops being able to say anything.
This project has already shipped a construct that erased a demonstrated kill with
`verified: true, green: true, exit 0`, and another where a `[[limitation]]`
converted a cell before the mutated run was consulted.

Six attacks, each with the mechanism that defeats it. A design that only asserts
it is safe fails this ticket, so each defence names the thing that has to be true.

### A1 — Declare the tag that makes the loss go away

*After seeing D3 = 2, write `effectful` on the loser and `ports-and-adapters` on
the winner. The comparison becomes INCOMPARABLE and the delta disappears.*

**Defeated by §3.3: a declaration has no refusal authority, ever.** Only the
derived value can make anything incomparable. To move the derived value the
author must move the state out of the effectful module and put a second
implementation behind a seam — which is the work D3 is measuring. The declared
value is still recorded, and a disagreement is surfaced as `TAG-DISPUTED` rather
than silently resolved.

### A2 — Make the subject underivable so the declaration is all there is

*Add an unparsed module. Score a non-Python tree. Remove the effect surface. Now
nothing computes, so the declaration decides.*

**Defeated by fail-open: `UNDERIVABLE` has zero refusal authority.** An
underivable subject is comparable to everything. The tag can only ever *subtract*
comparability when derivation succeeds **on both sides** and the values differ on
a dimension in the demonstration table. This is `unobservable` beating a false
clean, pointed at the tag: an unmeasurable tag says nothing, and saying nothing
may not buy more than saying something.

### A3 — Add values until nothing is comparable to anything

*Every artifact is its own architecture. Every comparison is refused.*

**Defeated by the earn-its-place test.** A value with no demonstrated separation
is `UNDEMONSTRATED` and fails open exactly like `UNDERIVABLE`. The vocabulary may
grow without limit; the *refusing* vocabulary grows only by a blind round with a
within-example pair, at the cost in [§7.5](#75-what-it-costs). Under this
design the refusing vocabulary today has exactly **two** values.

### A4 — Spread the earned refusal across the other four dimensions

*Grant it on D3, where it is demonstrated, then let it refuse D1, D2, D4 and D5
too, since they are about the same artifact.*

**Defeated by per-dimension authority.** Refusal is keyed on `(dimension,
value-pair)` and read from a demonstration table that `audit` **re-derives from
the cards on every run**, exactly as R-H5 re-derives `points` and R-H6 re-derives
`contested`. A stale table entry is a violation, not a rounding error. Measured
today the table has one row — D3 — and the other four dimensions overlap over 34
cards, so the objection is not available on them at all.

### A5 — Choose the scope that carries the flattering tag

*Not hypothetical. It is what produced `toolchain_removal` D3 = 4, on a card
whose every citation is to a fixture.*

**Defeated by declaring scope before scoring, and by checking citations against
it.** Scope goes into the unfilled skeleton; `check` refuses a filled card whose
scope moved. A card whose D3 citations fall predominantly outside its declared
scope is reported **`SCOPE-DRIFT`** — and §4.2 is the demonstration that this is
computable from sealed cards, because it is how that table was built. A scope
change is not an architecture change and must never be read as one.

### A6 — Emit INCOMPARABLE and drop the row

*The `EVAL-SUPPRESS` shape: the verdict is printed, the number stops existing.*

**Defeated by §6.2: an INCOMPARABLE pair prints both scores.** The verdict
annotates the *pair*; it never touches a row. `ABSENT`, `UNDERIVABLE` and
`INCOMPARABLE` are three distinct states with three distinct counters, because a
missing row and an incomparable one are not the same claim and this project has
been caught conflating `absent` with `checked, none found`. **A tag can never
reduce the set of printed numbers. It can only add a word beside two of them.**

### The invariant all six reduce to

> **The tag has exactly one power: to annotate a comparison between two scores
> that are both still printed. It cannot hide a number, cannot change a score,
> cannot refuse a build, and cannot refuse a comparison on any dimension where it
> has not demonstrated it moves one.**

---

## 6. Comparability

### 6.1 What `R-H1` becomes

R-H1 today: *a row is comparable to another only on the same example and across
an unchanged instrument.*

**Proposed R-H1, with a third clause that is conditional rather than blanket:**

> A row is comparable to another **only** on the same example, **and** across an
> unchanged instrument, **and** — on any dimension for which the demonstration
> table records a separation between the two rows' **derived** architecture
> values — at the same derived architecture value.
>
> *Executed as:* everything R-H1 already executes, plus: the demonstration table
> is re-derived from the cards on every `audit`, and a table entry the cards no
> longer support is a VIOLATION. A row whose subject scope is absent is reported
> `OPEN`. A row whose derived value is `UNDERIVABLE` or whose value pair is
> `UNDEMONSTRATED` is **comparable**, and the reason is printed.

It extends R-H1 rather than adding an `R-H7` deliberately. R-H5's own history is
that an unnumbered rule with no check was added at close and `audit` rejected it
within the minute; a new `R-H` id is a promise to ship a check, and folding into
R-H1 inherits a check that already runs. **If RD-05 prefers a new id it must ship
the check in the same commit.**

### 6.2 What `INCOMPARABLE` looks like

Four states, four counters, one printing rule.

```
example: ab_quota_ledger
dim  arm_b [ports-and-adapters]   arm_a [effectful]     verdict
---  -------------------------    ------------------    ---------------------------------
D1   3 3 3 3 3 3 3 3 3 4          2 3 3 3 ... 4         comparable
D2   2 2 2 2 2 2 2 2 2 2          2 2 2 2 ... 2         comparable
D3   4 4 4 4 4 4 4 4 4 4          1 2 2 2 ... 2         INCOMPARABLE (architecture:
                                                        effectful/ports-and-adapters,
                                                        demonstrated on D3, table row
                                                        rd04-d3-effect-boundary)
D4   2 3 3 3 3 3 4 4 4 4          2 2 2 3 ... 4         comparable
D5   3 3 3 3 3 3 4 4 4 4          2 2 2 3 ... 4         comparable

incomparable pairs reported: 1     absent: 0     underivable: 0
```

| state | means | printed |
|---|---|---|
| `comparable` | checked, values equal or pair not in the table | both score sets |
| `INCOMPARABLE(axis, values, table row)` | checked, decided, differ on a demonstrated dimension | **both score sets, unchanged** |
| `UNDERIVABLE(reason)` | checked, could not decide → comparable | both score sets + the reason |
| `ABSENT` | no card exists | `—`, counted separately |

**Silence is how a denominator shrinks.** `incomparable_pairs_reported` is one of
`GOAL-tags-earn-their-place`'s own metrics, so an implementation that quietly
drops incomparable pairs scores itself down.

---

## 7. How a value earns its place

### 7.1 The test

> A tag value survives only if **two artifacts of the same example, differing in
> that value, score in disjoint ranges on some dimension.** Identical ranges on
> all five means it distinguishes nothing and it is deleted.

It must be within one example, because `R-H2` forbids comparing across examples
and a taxonomy is not exempt from the reading rules it is meant to serve. It is
`R1` applied to a taxonomy: the vocabulary ships with a demonstrated failing
input, which is any value that cannot produce a separation.

Two additions the bare rule does not state and needs:

- **A same-tag control.** Two subjects of the same example carrying the *same*
  value must **not** separate on the dimension claimed. §4.1 runs it and it
  holds. Without it, a separation between any two artifacts counts, and any two
  artifacts differ in something.
- **A tier check.** RD-01 measured three real tier splits. A separation present
  in one tier and absent in the other is a fact about the tier. §4.1's separation
  is demonstrated in `opus` and **not measured** in `sonnet`, and that is
  recorded as absent rather than as agreement.

### 7.2 Is it sound?

**Sound as a deletion rule. Not sound as a promotion rule.** State it that way or
it will be over-read.

- As a *deletion* rule it is correct and cheap. A value with no separation
  anywhere in the record cannot be doing comparability work, whatever the
  argument for it. It deletes decoration and that is exactly what it is for.
- As a *promotion* rule it establishes correlation and calls it authority.
  Nothing in the test forces the separation to be **caused** by the value.
  `arm_b` differs from `arm_a` in architecture *and* prompt *and* author *and*
  size. The record's own `arm_c` removes the verbosity confound; nothing removes
  the author confound. So a value that passes is **admitted, not proven**, and it
  must carry its confound list forward on the demonstration table row.

Three failure modes the test cannot see, all three real in this record:

- **It cannot detect a ceiling.** A value that changes a *reachable maximum*
  without changing the *observed* score is invisible to it. That is exactly the
  greenfield case: four judges wrote that D2's anchor 3 is unreachable by
  construction for a greenfield artifact, and D2 came out **2** — the same value
  it takes everywhere on that example, where `D2 = 2` on 35 of 35 cards of
  `ab_quota_ledger`. The rationales moved; the scores did not. Under the test as
  written, `greenfield` is deleted, and the thing that
  cost an epic goes unrecorded.
- **It cannot see a value that occurs in only one example.** No sibling, no test,
  ever. `no-effect-surface` is stuck there today.
- **A `no separation` verdict can be entailed rather than measured.** See
  [§7.3](#73-null-entailment-which-of-the-four-overlaps-verdicts-are-measurements).

The first two are arguments for a *second*, weaker admission route — a demonstrated
**unreachable anchor**, cited from the rubric text rather than from a score
delta. RD-04 does **not** recommend building it, because a rationale-based route
is exactly the door A1 walks through. It is named in §9 so RD-05 decides it
deliberately.

### 7.3 Null-entailment: which of the four `overlaps` verdicts are measurements

**RD-02 measured that a gap mutant can price a removal only if every detector
that killed it is one the removal deletes — 0 of 9 over the sealed table — so its
zero-price results were *entailed by the setup* rather than measured.** The
earn-its-place test has the same failure mode. RD-04 did not state it in the
first draft; it is stated here rather than left for RD-05 to inherit.

**A dimension that took one value across the whole population cannot separate.**
An `overlaps` verdict on such a dimension reports the example, not the tag.
Re-run over §4.1's four `overlaps` results, printing the population's observed
range beside each:

| dimension | values the population took | the `overlaps` verdict is |
|---|---|---|
| D1 | 2, 3, 4 | **a measurement** — a separation was possible and did not occur |
| **D2** | **2** | **NULL-ENTAILED — no separation was possible** |
| D4 | 2, 3, 4 | a measurement |
| D5 | 2, 3, 4 | a measurement |

**Three of the four are measurements and one is not.** The claim that
architecture separates D3 *and nothing else* is therefore supported on D1, D4 and
D5, and **carries no evidence at all on D2** — that cell says only that
`ab_quota_ledger` has never produced a D2 other than 2, which was already known
and is a fact about the example rather than about the tag.

It does not change the design: D2 gets no refusal authority either way, and it
gets none for a *weaker* reason than the other three. **What changes is what may
be said about it.**

**The rule RD-05 must carry:** a `does not separate` verdict is reported with the
population's observed range beside it, and marked `NULL-ENTAILED` when that range
is a single point. A null result that could not have come out otherwise is not a
null result.

### 7.4 And the converse — does the derivation borrow the anchor?

The mirror risk, on the *positive* side. Derivation clause (c) asks for a second
implementation behind the seam; D3's anchor 4 asks for a driven port exercised by
a real adapter *and* a fake. Those are close enough that the D3 separation could
be the predicate quietly encoding the anchor — in which case `ports-and-adapters`
would *entail* a high D3 and the separation would measure nothing.

**Refuted by the record.** `ex4_pipeline_coherent` derives `ports-and-adapters`
under all three clauses and was scored **D3 = 3 by both blind judges**. The
predicate does not force a 4.

*Why this is not an R-H2 violation:* it is a claim about the **predicate**, not a
comparison of scores across examples. One counterexample anywhere refutes *"the
predicate entails D3 = 4"*, and none of `ex4`'s numbers is compared with any of
`ab_quota_ledger`'s.

The clauses remain **correlated** with the anchor, and that correlation is a
confound the demonstration table row must carry forward. It is not an entailment.

### 7.5 What it costs

- **At least one blind round per candidate value**: two judges minimum, on an
  example that already has a sibling artifact differing in that value, plus the
  sibling itself if it does not exist. On this project's measured rates that is
  the dominant cost of adding a value, and it is the intended cost — it is what
  stops the vocabulary growing.
- **Values that are true and useful will be refused**, at least at first, because
  no sibling exists. `no-effect-surface` is a real property of four of eleven
  subjects and it ships with no authority.
- **A demonstration table that must be re-derived on every read**, which is
  another executed rule to maintain, and another thing that can go stale.

---

## 8. Scoring an architecture change

Moving a subject from one value to another is a before/after — the subject shape
D2 was just measured to be able to read. It is declared as an
`[[architecture_change]]` in `INSTRUMENT-LOG.toml` naming `from_card`, `to_card`,
`scope`, `from_value`, `to_value` and per-dimension `points`, with `points`
**re-derived from the two cards on every `audit`** exactly as R-H5 re-derives a
`[[movement]]`. A stale entry is a violation.

Two reading rules, and the second is the load-bearing one:

**On a dimension in the demonstration table for that value pair** — today, D3 —
the delta is reported `EXPECTED-BY-TAG` and compared against the band the record
demonstrates. On `ab_quota_ledger` that band is `effectful` ∈ [1,2] against
`ports-and-adapters` ∈ [4,4], so an `effectful → ports-and-adapters` change is
expected to move D3 by **+2 to +3**.

> **The interesting result is a delta OUTSIDE the band, and a delta inside it is
> not news.** A refactor declared as ports-and-adapters that moves D3 by +1 did
> not buy what the tag buys — that is a finding about the refactor. A refactor
> that moves it by +3 when the band says +2 is a finding too. **A delta of
> exactly what the tag predicts is the tag showing up in the numbers and is
> evidence of nothing.** This is MF-020 one granularity up: a metric moving in
> the direction it was pushed is not evidence the design improved.

**On the other four dimensions** the delta is an ordinary movement under R-H5 —
readable only if `judging_practice` is recorded at both ends — and **that is
where the real result of an architecture change lives.** Whether making a program
ports-and-adapters catches more bugs is a D1 question, and D1 is precisely the
dimension the tag has no authority over.

A change whose `from` or `to` value is `UNDERIVABLE` is recorded and is **not** an
architecture change; it is a scope or a measurement gap and is reported as one.

---

## 9. What RD-04 could not settle

These are RD-05's open questions. They are not assumptions to bake into code.

### 9.1 The separation is demonstrated in one tier

No `sonnet` judge has ever scored a `ports-and-adapters` subject on
`ab_quota_ledger`: n = 0. The D3 separation is `opus`-only, over 22 `effectful`
and 10 `ports-and-adapters` cards. Two `sonnet` judges on `blind/artifact_T`
would settle it and cost one round. **Until then the demonstration table row must
carry `tiers_measured = ["opus"]`,** and a cross-tier comparison on D3 is not
covered by anything measured here.

### 9.2 The `state_colocation` threshold is unvalidated

`< 0.5` is a number RD-04 chose. The observed values are 0.100–0.125 against
1.000 — a chasm — so *any* threshold in that interval gives the same answer on
every subject in the record. **No artifact anywhere near the boundary has ever
been measured.** Do not read 0.5 as measured. The first artifact that lands near
it is the one that decides the clause, and RD-05 should make the threshold a
printed constant rather than a buried one.

### 9.3 `no-effect-surface` has one data point

`spec_double_compiler/` derives `UNDERIVABLE:no-effect-surface` and was scored
D3 = 3 by one judge, within the same example as `scripts/` (`effectful`, D3 = 2,
2) and `reference_ports/` (`ports-and-adapters`, D3 = 4). That is a within-example
signal for a third value and it is **n = 1 in two of three cells** — a single
card cannot establish a range, so it is not a demonstration.

*Named experiment:* score `spec_double_compiler/` as its own declared scope with
two blind judges, same round, same tier as an `effectful` sibling. If D3's range
is disjoint from `effectful`'s, `pure` earns its place. If not, delete it.

### 9.4 Subject shape is not architecture, and is not demonstrated either

The D2 evidence in the epic charter — *2 on greenfield, 3/4 on a real before and
after* — compares `ab_quota_ledger` against `toolchain_removal`, which is a
**cross-example comparison R-H2 forbids**. Within `ab_quota_ledger`, the framing
changed between the arm-pair rounds and the greenfield round and **D2 did not
move**: `D2 = 2` on 35 of 35 cards of `ab_quota_ledger`, 31 under the arm-pair
framing and 4 under greenfield. So `greenfield` fails the earn-its-place test on the
record as it stands, for the ceiling reason in §7.2.

RD-04's position: it is a real class, it is **not** architecture, and putting it
on the architecture axis would be the first suppression key. Whether it deserves
its own axis is undecided.

*Named experiment:* re-score `toolchain_removal`'s after-tree alone, no before
supplied, two blind judges at the tier that produced D2 = 3, 3. If D2 falls to 2,
`subject_shape` earns its own axis on that example. If it does not, delete it.

### 9.5 Non-Python subjects

The derivation is a Python AST walk. Every other language is
`UNDERIVABLE:unparsed` and therefore comparable to everything. That is the right
default for a corpus that is entirely Python and it is untested against anything
else.

### 9.6 Three arms, three authors

`arm_a`, `arm_b` and `arm_c` differ in architecture, prompt, author and size.
`arm_c` controls length; nothing controls author. A within-author pair — the same
agent asked for both shapes of the same feature — would settle it and does not
exist.

### 9.7 Composite subjects and `contested`

`toolchain_removal` needs three scoped cards where it has four unscoped ones.
Whether one round may emit several scoped cards for one artifact, how `contested`
groups them (a judge group is per-artifact today, and would have to become
per-scope), and whether the four sealed cards can be *re-attributed* rather than
re-run, are all undecided. **The sealed cards are never edited** — R-H4 — so any
re-attribution is a `[[note]]` beside them, not a correction to them.

### 9.8 `scope` refutes a true subject-scoped claim, and the reason is placement

RD-01's `score_tools.py scope` resolves a figure's population from a **named
example** in the window, and reports an **arm-scoped** figure `UNREACHABLE` on
the stated ground that arm labels are round-local and opaque by design. Every
figure this design makes worth writing is scoped by a **subject**, which is
neither an example nor an arm.

Take the figure this design most wants to write. It is **true**: all 10 cards of
the subject `arm_b` carry D3 = 4, and no card of any other `ports-and-adapters`
subject of `ab_quota_ledger` exists.

> D3 = 4 on 10 of 10 `ports-and-adapters` cards of `ab_quota_ledger`.

**`scope` returns `REFUTED` for it — a true figure — and whether it does depends
on where the narrowing word sits.** Four probes, preserved under
`analysis/wrap_probe/`:

| probe | verdict |
|---|---|
| `…10 of 10 \`ports-and-adapters\` cards of \`ab_quota_ledger\`` | `UNREACHABLE` — *"the counted noun narrows the population with ['ports-and-adapters']"* |
| the same, wrapped after `10 of 10` | **`REFUTED`**, population 35, *"25 card(s) … do not carry D3 = 4"*, twelve named |
| `…10 of 10 cards of the \`ports-and-adapters\` subject of \`ab_quota_ledger\`` | **`REFUTED`**, on one line |
| `…10 of 10 cards, on the example \`ab_quota_ledger\`, of arm_b's subject` | **`REFUTED`**, on one line |

**The mechanism is placement, not wrapping.** `scope` inspects a window of at
most three words immediately after the count. A narrowing word inside that
window is seen, and the figure is `UNREACHABLE`. **The same narrowing word
anywhere else — after the card noun, in an aside, or on the next line — is
invisible, and the figure is refuted at example scope.** Line-wrapping is one
instance of the general case. *(This section was first written on the wrapping
instance alone; the epic owner could not reproduce that instance with different
probe text and identified the broader class, which the four probes above
confirm. The narrower statement is corrected here rather than left standing.)*

**Every one of those 25 counterexamples is a card about a different subject.**
The claim is true and the refutation is manufactured, by a checker that cannot
see the axis the claim is scoped on.

**And a second blind spot compounds it, measured by RD-02:** `scope` is keyed on
a `D[1-5]` token, so a counted figure that names its dimension in words is
invisible. A four-line probe carrying four counted figures — *"Bug detection came
out 4 on 10 of 10 cards…"*, *"Modularity was 4 on 10 of 10 cards…"*, *"D3 = 4 on
10 of 10 cards…"*, *"The complexity dimension scored 2 on 35 of 35 cards…"* —
reports **"1 counted figure(s)"**.

Together these make **RD-01's own headline a scoped claim whose scope nobody
stated.** Its denominator is *figures carrying a dimension token*, not *counted
figures*; and its numerator can include refutations that are artifacts of
qualifier placement rather than false claims. `REFUTED` is the verdict
`GOAL-scope-loss-catchable` counts as its headline, with no target on it and a
high count declared the honest outcome — **so a checker that can both miss
figures and manufacture refutations can move that headline in either direction.**
RD-01's own doctrine, that `absent` and `checked, none found` are different
claims, applies with more force to `refuted` and `could not read`.

**RD-05 must either teach `scope` to resolve a subject scope from the cards'
`subject.scope` field, or make an unresolvable subject scope report
`UNREACHABLE` rather than falling back to the example.** Both are legal; leaving
it is not.

The other three counted figures on this page report `HOLDS` only because each was
deliberately phrased at example scope. Filed as `RD-04-DF-01`.

### 9.9 The derivation branches on complexity figures, and a standing invariant forbids that

**Found only in a tree with no per-checkout homes, and it is the most consequential
open question here.**

`tests/test_code_complexity.py::test_no_reader_of_this_instrument_gates_on_its_output`
states a repository-wide invariant in its own docstring: a file *"is allowed to
refer to the instrument and to transcribe its figures. It is not allowed to
branch on them, compare them, assert on them or exit on them — that is a
thermostat, whatever it is called."*

**RD-04's derivation predicate does exactly that.** Clause (b) compares
`instance_state_in_effectful_modules / instance_state` against a threshold;
clauses (a) and (c) compare `declared_interfaces` and `effectful_calls` against
zero. The analysis script trips the tripwire, and **RD-05's implementation will
trip it harder**, because it will do the same branching on a shipped path rather
than in an evidence directory.

Two readings, and RD-04 does not have the authority to choose:

- **It is a thermostat.** Then the tag cannot be derived at all — and derivation
  is the *entire* anti-suppression mechanism ([§5, A1](#5-the-suppression-key-attack)).
  A declared-only tag is the suppression key this ticket exists to prevent.
- **It is not.** The invariant is aimed at a figure *deciding something about the
  code* — the thermostat that fails a build, refuses a design, or chooses a
  boundary (`CD-01`). A derived tag **refuses nothing about any artifact**; the
  plan's own `no_new_gates_rule` says a tag *"constrains what may be COMPARED and
  refuses nothing about the code."* On this reading the tag is a classifier over
  the *record*, not a thermostat over the *program*.

RD-04's view is the second, and it is a **view, not a demonstration**. The
invariant as written carries no such exception, and the existing
`GATING_SCAN_EXEMPT` list is bounded by a property another test checks — so an
exemption for a derivation would have to earn one the same way, or the invariant
would have to say what it means.

**RD-05 cannot resolve this by itself and must not add itself to the exemption
list without the invariant's scope being stated.** Escalated to the epic owner
rather than filed quietly.

### 9.10 `arm_a` D3 = 2 against `arm_c` D3 = 1

Same derived value, ranges 1–2 and 1–1, eighteen cards against six. The design
explains none of it and does not grow a value to cover it.

---

## 10. Future-proofing, and its limits

The owner intends to add options an agent is *required* to choose among, with the
formalization evolving from those choices. What this design does and does not
accommodate:

**Accommodated.** A second axis, with its own values, its own demonstration table
and its own per-dimension authority — the design is keyed on `(axis, dimension,
value-pair)` throughout, not on a single `architecture` field. A new value on an
existing axis, at the cost of one blind round. A scope-per-subject model, so a
program that is several things at once is describable without the values having
to be exclusive. A derivation that improves — the facts are read from a versioned
instrument report, and a card records which version derived it.

**Not accommodated, on purpose.** An agent choosing its own tag at scoring time:
a declaration never refuses a comparison, and that is the property A1 rests on.
Free-text values: the axis is closed and an unknown value is `UNDEMONSTRATED`
with no authority. Ranked or ordinal values: see §2.2. A tag that gates anything
about the code: `no_new_gates_rule`, five epics, zero bugs caught by a static
check.

**Not built.** The choice menu itself. RD-04 was asked to say what the design
accommodates and to stop there.

---

## 11. What RD-04 rejected

1. **A single unscoped `architecture` scalar per card.** The `toolchain_removal`
   decomposition shows one artifact carrying three values at three scopes; an
   unscoped scalar forces that disagreement into one field and loses it.
2. **`hexagonal` as a value name.** The record's own vocabulary is
   `ports-and-adapters`, which is D3's anchor text. `hexagonal` is the name of the
   *prompt* that produced `arm_b`; naming the tag after the treatment makes the
   tag read the answer key.
3. **A `layered` / `mvc` / `pipeline` / `monolith` style vocabulary.** Zero
   demonstrated separations. Attack A3 in taxonomy clothing.
4. **Deriving from import topology.** Rejected on the card's own measured ground.
   `ex5_pipeline_divergent` has `declared_interfaces = 1`,
   `internal_import_edges = 18` and D3 = 1 from both blind judges.
5. **`declared_interfaces ≥ 1` as the whole predicate.** Same demonstrated
   failing input. It is why clauses (b) and (c) exist.
6. **Letting the tag distinguish a followed boundary from a diverged one.** That
   is D3 anchors 1 and 2. A tag that could make the distinction would be scoring
   the dimension.
7. **Making the tag a gate, a threshold, or an input to any close path.**
8. **`INCOMPARABLE` dropping the row.** `EVAL-SUPPRESS`.
9. **Ranking the values.**
10. **Tagging instrument reach as architecture.** `R-H1` already owns it;
    double-counting lets one fact refuse a comparison twice.
11. **Running a third pass to settle `toolchain_removal`'s D3 contest.** The
    judges were right that no new *evidence* could settle it — the disagreement
    was not about evidence. Rule 5 permits `third_pass = "none"` when it is
    recorded with a reason, and this is the reason. The fix is a declared scope
    on the next round.
12. **A rationale-based admission route for tag values** (§7.2). It would let a
    value earn authority from prose, which is the door A1 walks through. Named in
    §9 for RD-05 rather than built.

---

## 12. Status

**A design with a measured basis and no implementation.** One axis, two
authoritative values, one demonstrated dimension, one example, one judge tier.
Everything above that is an open question in §9. Any sentence claiming more than
that about this page is unsupported.

*RD-05 note:* the second clause of the first sentence is the only one that
changed. The evidence under it did not — see §13.

---

## 13. What RD-05 shipped, and what it left open

**The design is now executed. The evidence under it is exactly as wide as it was
when RD-04 wrote §12,** and every limit that section states still holds: one
axis, two authoritative values, one demonstrated dimension, one example, one
judge tier.

### 13.1 What shipped

| surface | what it does |
|---|---|
| `examples/validation/scorecards/subjects.toml` | the **declared** scopes — eleven of them, each a path list, a declared value and the cards that scored it. Nothing here is computed and nothing here may be |
| `scaffold --subject NAME` | copies that scope into the **unfilled** skeleton, before any judge is dispatched; `check` refuses a filled card whose `subject.scope` moved — attack A5, executed |
| `examples/validation/scorecards/architecture_tags.py` | derivation, the demonstration table, comparability verdicts and `SCOPE-DRIFT`. Exit code always 0 |
| `score_tools.py tags [--compare A B]` | the same, and the pair view that prints both score sets |
| `audit`, R-H1's third clause | re-derives the table from the cards every run; a `[[demonstration]]` the cards no longer support is a VIOLATION, an undeclared separation is `OPEN`, a drifted card is `OPEN` |
| `[[demonstration]]` in `INSTRUMENT-LOG.toml` | **one row**, D3, `effectful`/`ports-and-adapters`, `tiers_measured = ["opus"]` |
| `tests/test_architecture_tags.py` | 30 tests; the failing input is `toolchain_removal`'s sealed cards |

**The vocabulary did not grow.** Two values with refusal authority, both
demonstrated in the one cell that separates; `UNDERIVABLE:<reason>` and
`UNDEMONSTRATED:<name>` with none. `pure` and `greenfield` were *not* admitted —
§9.3 and §9.4 name the experiments that would decide them, and earn-its-place is
a deletion rule, so it cannot admit either.

### 13.2 What RD-05 settled, and how

- **§9.9 — the thermostat question.** Settled **by the epic owner's ruling**
  (`READING-DISCIPLINE-EPIC.md` §6b), not by RD-05: the invariant means a figure
  deciding something about the CODE. RD-05 did **not** add itself to
  `GATING_SCAN_EXEMPT`. It fixed the invariant's **statement**:
  `test_no_reader_of_this_instrument_gates_on_its_output` now forbids
  `refusing_uses` — a figure reaching a `raise`, an `assert`, an `exit`, or a
  branch whose arm does one of those — and reports the rest as `observing_uses`.
  `architecture_tags.py` is scanned like any other file and stays green because
  of a property it has, pinned by
  `test_the_derivation_observes_and_never_refuses`.
  **The ruling's own limit stands and is [§13.3](#133-what-is-still-open):** the
  separation is `opus`-only.
- **§9.8 — `scope` refuting a true subject-scoped claim.** Settled the second
  way §9.8 permits: **an unresolvable subject scope is not resolved to the
  example.** `subjects.toml` gives `scope` nothing to fall back on because the
  fix is upstream of it — every figure this design makes worth writing is now
  written at *subject* scope and RD-05's own claims are phrased so the checker
  can reach them or are reported `UNREACHABLE`. `RD-04-DF-01` stays open: the
  checker itself is unchanged, and RD-05 files `RD-05-DF-01` for the narrower
  half it measured.
- **§7.3 — null-entailment.** Settled as a shipped column rather than a note.
  Every non-separating cell prints the population's observed range, and a range
  that is a single point is printed `NULL-ENTAILED`. Three of the four
  `overlaps` cells are measurements; D2's is not.
- **§9.7 — composite subjects.** Settled only in the half RD-04 said could be:
  `toolchain_removal`'s four cards are **re-attributed by a `[[note]]`-shaped
  report, never edited** (R-H4). `SCOPE-DRIFT` names two of the four. Whether one
  round may emit several scoped cards, and how `contested` groups them, is
  **untouched** and stays open.

### 13.3 What is still open

**§9.1 stays a question and is the axis's binding limit.** No `sonnet` judge has
ever scored a `ports-and-adapters` subject on `ab_quota_ledger`: n = 0. The
demonstration row carries `tiers_measured = ["opus"]`, `audit` re-derives that
field, and a declared `["opus", "sonnet"]` is a VIOLATION until two `sonnet`
judges score `blind/artifact_T`. **Nothing RD-05 built makes that evidence
wider.**

**§9.2** — the `0.5` threshold is a printed constant now and is still
unmeasured near its boundary. **§9.3** — `pure` still has one data point.
**§9.4** — `greenfield` is still not architecture and still fails earn-its-place
on the record as it stands. **§9.5** — non-Python subjects are still
`UNDERIVABLE:unparsed` and still untested. **§9.6** — the author confound is
still uncontrolled. **§9.10** — `arm_a` D3 = 2 against `arm_c` D3 = 1 is still
unexplained, and the vocabulary still does not grow a value to cover it.

### 13.4 One correction to this page

§3.1's table prints `—` for `ex6_jenga`'s state co-location. RD-04's own machine
record — `analysis/result.json` — gives **0.0**, on `instance_state = 7`, which
is what the shipped derivation reproduces. `—` is what that column prints where
there is no instance state at all, which is right for `ex1_scaffold_only`,
`ex3_over_complex` and `spec_double_compiler/` and wrong for `ex6_jenga`. One
cell, a transcription slip in the table rather than a difference in the
predicate — the machine record is right. Recorded here rather than edited there,
and pinned by
`test_the_derivation_reproduces_rd04s_sealed_machine_record`, which compares
against `result.json` and deliberately not against this page.
