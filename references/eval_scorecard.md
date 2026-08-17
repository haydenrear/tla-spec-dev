# The Eval Scorecard

**Scorecard version 5.** Every eval in this repository is scored on this card,
by an agent judge, against artifacts. The card is the unit of comparison across
epics: one epic's numbers mean something only next to another's, so the card is
versioned and changing it is a deliberate, recorded act.

**Version 5 is the first version whose SERVED DIGEST MOVES WHILE THE ANCHORS
DIGEST DOES NOT.** No anchor is added, deleted or reworded, so the bar for every
score is byte-identical to version 4's and `anchors_digest` says so. What moves
is D3's caveat, which is the class of change that was **invisible** until CL-01
put a second seal on the served bytes: before that seal, this edit would have
reached every future judge with nothing in the record reporting it.

It was made because a regression the judges themselves found had nowhere to
land. `domain.LedgerJournal` in `examples/validation/ab/reference_ports`
declares durability as its whole job, and the only observer of that record
anywhere in the fixture reads it back **through the adapter that wrote it** — so
a `FileJournal` that stops touching the filesystem passes every case through
both wirings. D3's anchor 4 asks for *"a real adapter and a fake, with the same
cases passing against both"*, and **a pair of fakes satisfies it word for word.**
Twenty-two `D3 = 4` cards rest on that pair. The anchor is not changed: an anchor
is permanent and a re-worded rung would make 83 sealed cards incomparable for a
defect in one fixture. The caveat is where a judge is told what the rung does not
prove. `RM-05-DF-05` is the finding; `CL-03` is the card iteration; the delta is
measured, not asserted.

**Version 4 is the first version whose ANCHORS DIGEST MOVES.** Versions 1, 2 and
3 all carry `sha256:eeccf4576bc6fd85` — three version bumps and not one of them
touched the bar. Version 4 cuts three dimensions down to recorded notes and
removes one anchor from a fourth, so the digest necessarily moves and the
[Version history](#version-history) says so. Cards written under an older
version stay valid, stay comparable to each other, and are **not** comparable
across a version boundary without saying so.

What version 4 changed, and why each is a REMOVAL:

1. **D1 and D4 are no longer scored.** They are recorded notes. Both were
   measured to grade *this project's toolchain* rather than the artifact — an
   anchor decision cites this project's machinery in 38% of D1 rationales and
   18% of D4 rationales, against 4% on D2 and 0% on D3 — and both were measured
   not to survive the trip to another project: D1 is 3 on 56 of 63
   `ab_quota_ledger` cards, and D4 is the worst-behaved dimension in the record
   at 4 tier-split judge groups of 8. See `references/portable_scorecard.md`
   §1.1 and §6. **That figure is 56 of 63 at the card population of this
   commit** — RM-02 published it as 55 of 59 and RM-03's own re-score round
   moved both terms, which is `RD-03-DF-11` and not a correction to RM-02.
2. **D2's anchor 4 is gone**, and D2's preamble no longer requires a measured
   descriptor to be read first. Anchor 4 gated the one portable dimension on
   `D4 ≥ 3`, and that gate is the measured mechanism behind D2's tier split: 4
   of 4 `sonnet` judges name the model clause as their D2 ceiling and 0 of 4
   `opus` judges do.
3. **D5 is no longer scored.** It is a recorded note. It is orthogonal to
   architecture by measurement, saturated at 3 or 4 on 55 of 63
   `ab_quota_ledger` cards at this commit's population, and it still
   tier-splits. RM-02 published it as 53 of 59 and both terms moved for the same
   reason D1's did.

**The discipline is kept; the number is not.** A version 4 card still records
what the cases caught, whether the behaviour survived, and what the artifact
refuses to claim — as prose a reader can act on, in `notes`. What it no longer
does is put a 0–4 on any of them.

Version 3's three changes, none of which was an anchor:

1. **A judge is served the card; a judge never reads this file.** See
   [How this card reaches a judge](#how-this-card-reaches-a-judge). The digest
   recorded on a card now covers **exactly the bytes a judge is served**, so a
   change to the rubric that can reach a judge cannot be invisible to it.
2. **D5's anchor 4 has two defensible readings, and the card records which one
   was used** — the same move version 2 made for judging practice: record the
   choice, never mandate it. The bar is unchanged; what changed is that the
   choice is no longer invisible.
3. **`total` is gone.** It is not a field of a version 3 card and it is not
   printed by `index` or `history`. See [Reading a card](#reading-a-card).

## How this card reaches a judge

**A judge is handed a scaffolded card. A judge is not handed this file.**

For four rounds the judge dispatch said *"`references/eval_scorecard.md` — the
rubric. Read it."* This file also carries reading rules, a version history and
prior results about these same five dimensions. **A judge who reads it is being
handed conclusions about the instrument they are the instrument for**, which is
the one thing a measurement may not do.

So the rubric a judge sees is **generated**, not read:

```
python3 examples/validation/scorecards/score_tools.py serve
```

`serve` renders the judge-facing rubric out of the parsed structure of this
file — the five dimension blocks, their anchors and their caveats, and the
scoring rules — **and nothing else**. Every other section of this file is
outside what the renderer emits, so a section added to this file does not reach
a judge by default; it reaches a judge only if someone changes the renderer.
`scaffold` writes the same bytes into each `scorecard.md`, so the bar for a
score still sits in the same file as the score, and there is exactly one served
surface.

`serve` and `scaffold` both **REFUSE** when the served text asserts how one of
these five dimensions has scored or moved. That refusal is data hygiene on the
instrument — it decides nothing about any artifact and gates nothing a judge
may score. It is a backstop and it is not the mechanism: the mechanism is that
the renderer emits parsed structure only.

## Why a judged scorecard and not a metric

Every mechanical gate this project shipped was defeated cheaply and none of them
ever caught a bug.

- The complexity gate failed every normal program and was retired to advisory.
- The architecture check reported a clean on a divergent codebase for **six
  lines of YAML** in round 1, and for a **41-line re-export file** in round 2,
  with every declaration digest unchanged.
- Across two full eval rounds and seven repair tickets, **bug detection did not
  move by a single cell**: 4 of 6, 6 of 6, 0 of 3, 0 of 3, before and after.

Meanwhile the most valuable result the project has produced came from an agent
*reading a README* and noticing the public surface was false of the model — a
finding no metric contains and no gate could reach.

A number computed from the artifact can be optimized by editing the artifact. A
judgement that must cite the artifact can only be satisfied by changing what the
artifact *is*. That is the whole argument. It is not that judgement cannot be
gamed — it is that gaming it requires doing the work.

## What the card measures

**Two dimensions, each scored 0–4. Three recorded notes, scored not at all.**
There is no total and there never was one to compute from version 3.

| | Dimension | The question |
|---|---|---|
| **D2** | **Complexity** | Is the design as simple as its behavior requires, and no simpler? |
| **D3** | **Modularity** | Is it ports and adapters in fact — domain independent of I/O, adapters swappable? |

The three notes ask the same questions they always asked and take no score:

| | Note | The question |
|---|---|---|
| N-D1 | bug detection | Did the cases *catch* seeded faults — especially the hard classes? |
| N-D4 | behavior preservation | Does the changed design still do everything the baseline did? |
| N-D5 | honesty | Does the artifact refuse rather than falsely certify, and name what it cannot see? |

N-D5 is not a virtue score, and now it is not a score at all. It is kept because
`unobservable` beating a false clean (MF-027) is the single doctrine that has
survived every round intact, and because an artifact that overstates its own
reach corrupts every number next to it. **Keeping the discipline and dropping
the number is the whole of what version 4 does to it.**

## The anchors

Anchors are what make two judges agree. Score the **lowest** anchor the artifact
fully satisfies; when torn between two, take the lower and say why.

### D2 — Complexity

Diff the two trees yourself and decide whether one fact is stored twice — kept
in agreement by hand across several write sites, and read in one place. Where a
measured complexity descriptor exists you may read it, and on its own it decides
nothing; where none exists that is not a gap in the evidence.

- **0** — Complexity is unmeasured, or measured and ignored.
- **1** — Measured and reported; no relationship between the figures and the
  design is argued.
- **2** — The design's complexity is proportional to its behavior; no god-state,
  no variable written from everywhere.
- **3** — 2, **and** a simplification was made and its effect measured — the
  before and after figures are both recorded.

**A drop in a complexity number is not evidence on its own.** MF-020: a metric
can improve because an edge was deleted. A D2 of 3 requires the judge to say
*what got simpler and how the behavior survived it*.

### D3 — Modularity

- **0** — No boundary is discernible; state is written from everywhere.
- **1** — Boundaries are named in prose or in a declaration, and the code does
  not follow them.
- **2** — The code follows the declared boundaries. Cross-boundary calls go
  through something identifiable as a port.
- **3** — The domain does not import its I/O. An adapter could be replaced
  without touching the domain, and the judge names the specific swap.
- **4** — 3, **and** a driven port is exercised by a real adapter *and* a fake,
  with the same cases passing against both.

**Import topology is not modularity, and two fakes are not a pair.** Coupling
survives every import check, so D3 of 3 or more needs evidence about what
*calls* what at runtime, not what imports what. And anchor 4 holds when the real
adapter does nothing real: if the only observer of the effect the port exists
for is the adapter that wrote it, say so and take 3.

## The recorded notes

**From version 4, N-D1, N-D4 and N-D5 take no score.** They are prose, required
on every filled card, and a reader acts on them exactly as they acted on the
rationale beside a number. What is gone is the number, and with it the anchor
ladder that produced it.

Each note answers its question in the judge's own words and cites `file:line`
the same way a score ≥ 2 does. A note that says *"I could not tell"* is a
correct note.

- **N-D1 — bug detection.** What did the cases catch, and what class did they
  demonstrably miss? Name the fault you seeded if you seeded one.
- **N-D4 — behavior preservation.** Which behaviors of the baseline did you
  enumerate, and is each shown still to hold? If there is no baseline, say so —
  that is the answer, not a gap in the note.
- **N-D5 — honesty.** Does the artifact refuse rather than falsely certify, and
  does it name what it cannot see? Point at the refusal, or at its absence.

**Why these three stopped being scores, in one line each.** N-D1's top anchor
required cases *derived from the model*, which nothing outside this repository
has; N-D4 tier-split on 4 of the 8 judge groups scored by both `opus` and
`sonnet`, more than any other dimension; N-D5 is independent of architecture by
measurement — the deliberately incoherent fixture `ex6_jenga` scored D5 = 4 from
both judges at D3 = 0 and 1.

## Scoring rules that make it hard to game

1. **Score artifacts, never claims.** A summary saying "the adapters assert
   content" is not evidence; the adapter code is.
2. **Every score ≥ 2 cites `file:line`.** A score with no citation is capped
   at 1, mechanically, by the schema check.
3. **A score at the top of its scale additionally names something the artifact
   refuses to claim.** The top of every scale requires a stated limit. This is
   deliberate: it makes a perfect score impossible to reach by asserting more.
4. **Prose quality is never an input.** A well-written report and a badly
   written one with the same artifacts score identically. Say so in the
   rationale if the writing tempted you.
5. **Two judges, independently, blind to each other.** Any dimension where they
   differ by more than 1 is recorded as `contested` and adjudicated by a third
   pass that must cite new evidence, not re-read the same lines.
6. **Blind to arm.** Where an eval has arms (with-prompt vs without), judges do
   not learn which artifact came from which until after scoring.
7. **The mechanical block is recorded, never scored.** Kill counts, complexity
   figures, case counts, determinism, runtime. It sits beside the judgement so a
   reader can see when the two disagree — and a disagreement is a finding.
8. **Say what you ran.** *(New in version 2.)* Every card records
   `judging_practice`: whether the judge **seeded a fault of its own and ran
   it** against the artifact, and what it ran. Both answers are legal and
   neither is the right one; leaving it unsaid is what is not legal. From
   version 4 no anchor is gated on it and it is still required, because what a
   judge did is a variable in what a judge reports and a variable nothing
   records is a variable nobody can subtract.
9. **A judge is served the card, never the rubric file.** *(New in version 3.)*
   The scaffolded `scorecard.md` carries the rubric a judge needs. Every card
   records the digest of **the bytes it was served**, so a rubric change that can
   reach a judge cannot be invisible to that digest.
10. **Answer every recorded note.** *(New in version 4.)* N-D1, N-D4 and N-D5
    take no score and are required on every filled card. An empty note is not a
    legal card; *"I could not tell, and here is what I looked at"* is.

## Storage

Judged scorecards are epic-scoped evidence, so they live where the workflow
close seals them:

```
specs/results/scorecards/
  <epic-slug>/
    <example-id>/
      <run-id>/
        scorecard.json      # the schema below — the machine record
        scorecard.md        # the judge's rationale and citations
        mechanical.json     # measured figures, never judged
    INDEX.md                # one row per example, for reading at a glance
```

The workflow close copies `specs/results/` into
`specs/.history/<workflow>/closed-snapshot/results/`, so **every epic's
scorecards are sealed with the epic that produced them** and remain readable
after the working trees are pruned. That is what makes cross-epic analysis
possible at all.

Fixtures and harness stay under `examples/validation/`; only *results* live in
`specs/results/`.

### `scorecard.json`

```json
{
  "scorecard_version": 4,
  "epic": "architectural-coherence",
  "example": "ex4_pipeline_coherent",
  "run_id": "20260803-sc1",
  "arm": null,
  "commit": "<sha the artifacts were scored at>",
  "judge": {"model": "<model id>", "pass": 1, "blind_to_arm": true},
  "rubric": {
    "source": "references/eval_scorecard.md",
    "digest": "<over the parsed anchors and scoring rules>",
    "served_digest": "<over the EXACT bytes this judge was served>",
    "file_sha256": "<over the whole rubric file, served and unserved alike>"
  },
  "judging_practice": {
    "executed_own_faults": true,
    "what_was_run": ["copied the artifact to a scratch tree, inverted the guard in",
                     "`commit()`, ran the artifact's own suite: 3 failures naming the",
                     "invariant"]
  },
  "dimensions": {
    "D2": {"score": 3, "citations": ["path:line"], "rationale": "...",
           "refuses_to_claim": null},
    "D3": {"score": 2, "citations": ["path:line"], "rationale": "...",
           "refuses_to_claim": null}
  },
  "notes": {
    "N-D1": {"note": "...", "citations": ["path:line"]},
    "N-D4": {"note": "...", "citations": ["path:line"]},
    "N-D5": {"note": "...", "citations": ["path:line"]}
  },
  "contested": [],
  "verdict": "<one sentence a reader can act on>"
}
```

**There is no `total` from version 3.** A version 1 or 2 card carries one and
`check` still verifies its arithmetic; a version 3 or 4 card that carries one is
rejected.

**`dimensions` carries `D2` and `D3` and nothing else from version 4**, and
`notes` carries `N-D1`, `N-D4` and `N-D5`. A version 4 card that scores `D1`,
`D4` or `D5` is rejected, and so is one that omits a note. A version 1, 2 or 3
card is checked exactly as it always was: **a sealed card is never edited**
(`R-H4`), so every rule those cards were written under is still executed against
them, and none of the code that executes them was deleted by this version bump.
That is the honest cost of the removal and it is recorded in
`specs/results/scorecards/portable-substrate/GOAL-dead-weight-gone/`.

`rubric.served_digest` is the load-bearing one. `rubric.digest` covers the
parsed anchors and scoring rules and is what `check` uses to refuse a skeleton
scaffolded against a stale bar. `file_sha256` covers the whole rubric file
including the parts a judge is never served: two cards whose `served_digest`
agrees while their `file_sha256` differs are reported `PROSE-DRIFT`, which is a
prompt to go and look and never a violation.

`arm` is `null` for a single-artifact eval and the arm label where arms exist.
`refuses_to_claim` is required and non-null for any score at the top of its
scale — 4 on every dimension of every version, and additionally 3 on D2 from
version 4, where 3 is the top.

`judging_practice` is **required on every filled card from version 2**.
`executed_own_faults` is a boolean and `what_was_run` is a list. `false` is a
legal answer, it is recorded as `PACKET-ONLY` by `check`, and it is never
corrected — a card that is pushed toward one answer records the pressure and not
the practice. On a version 2 or 3 card a `false` carries one consequence — **D4
cannot be scored 4**, and `check` rejects the combination. **On a version 4 card
it carries none**, because D4 is not scored. The field is still required: it
records the variable, and the gate was never the reason for recording it.

`dimensions.D5.anchor_reading` is **required whenever D5 is scored 3 or 4** on a
version 3 card. It is `"disclosure"` or `"measured"`. **Version 4 has no
`anchor_reading` field**, because the anchor whose two readings it disambiguated
is retired; `check` still enforces it on every version 3 card, and always will.

## Reading a card

**There is no total, from version 3.** Its five terms were not five independent
readings: `D2` has taken one value on every card ever written about
`ab_quota_ledger`, and `D1`, `D4` and `D5` are each demonstrated to take a
different value from a different judge on the same bytes. A sum over them
moves for reasons a reader cannot attribute to anything, and it moves *most*
where the card is *least* readable — so it was the one number in this file that
rewarded the dimensions that measure worst. **Version 4 acts on the same
evidence one step further: the three terms that made the sum unreadable are no
longer numbers at all.** `index` and `history` print every dimension a card
carries and no sum, and print `—` where a version 4 card records a note instead.
**Read a dimension. There is nothing to read in a headline.**

**Never average across examples** — `ex6_jenga` is a deliberately incoherent
fixture and is *supposed* to score low on D3; averaging it with `ex4` produces
a number about nothing.

Compare like for like: the same example across epics, or two arms of the same
eval. A dimension that moves is the result.

> **What removing `total` cost, measured rather than asserted.** `total` was a
> checksum: `check` verified it equalled the sum, so a score edited in
> `scorecard.json` without updating it was caught. That check is gone with the
> field on a version 3 card, and the capability it stood for now rests entirely
> on `seal` and R-H4 — which is strictly stronger, because a seal digest covers
> all five scores, every citation and every rationale rather than one sum. This
> was measured with a seeded mutant, before and after: see
> `specs/results/scorecards/subtract-to-measure/SM-04/`.

## Scaffolding a card

**Do not hand-author one from this file.** For two epics every card was written
out by whichever agent was judging, which is exactly how a dimension key or the
`refuses_to_claim` requirement drifts from the rubric it was copied out of.

```
python3 examples/validation/scorecards/score_tools.py scaffold \
    specs/results/scorecards/<epic> --example <example> --arms A,B,C --judges 2
```

The skeleton reads the anchors **out of this file** and writes them into the
card, so there is one source of truth and **the bar for a score sits in the same
file as the score**. It records the rubric's digest; `check` refuses to let a
judge fill in a skeleton scaffolded against a rubric that has since changed.

Three properties are mechanisms rather than habits:

- **Blinding is the default.** Arms are emitted under opaque labels drawn from a
  pool that excludes every label any prior round published, and the mapping goes
  to `UNBLINDING.md`, which judges are not given. Unblinded scoring requires
  `--unblinded --reason "..."`, and the reason is written into the key file.
  Both prior rounds blinded correctly by discipline; discipline is not a
  mechanism.
- **Scaffolding twice over the same path REFUSES** and writes nothing. A
  scaffold that clobbers a measurement is worse than no scaffold.
- **An unfilled skeleton cannot smuggle a score through.** `status: "unfilled"`
  requires every score to be null; a card carrying scores must say `filled`, at
  which point every rule above applies to it. `check --require-filled` is what a
  workflow close runs.
- **A contaminated card is not scaffolded at all.** *(New in version 3.)* If the
  served rubric asserts how one of these five dimensions has scored or moved,
  `scaffold` refuses the whole batch and writes nothing, exactly as it does for
  a collision. A round cannot begin by handing its judges the answer.

## Reading history

`specs/results/scorecards/SELF-IMPROVEMENT.md` carries every epic's rows and
**the metric is the delta**. A delta is only a measurement if both ends were
measured on the same instrument, and this project has now shipped a round where
they were not: the eval instrument was repaired *after* HP-06 measured on it, and
two of its sealed numbers stopped describing the instrument that produced them.

Instrument changes, the notes recorded beside stale rows, and the ledger claims
that are not scorecard rows live in
`specs/results/scorecards/INSTRUMENT-LOG.toml`. Read a history with:

```
python3 examples/validation/scorecards/score_tools.py history --example <example>
python3 examples/validation/scorecards/score_tools.py audit
```

**Every rule below is executed by `audit`.** A reading rule nothing executes
will drift, which is the class of artifact this project keeps finding stale — so
`audit` fails if this file declares an `R-H` rule with no check behind it.

### R-H1 — Name the instrument change or do not compare

A row is comparable to another **only** on the same example, **and** across an
unchanged instrument, **and** — on any dimension for which the demonstration
table records a separation between the two rows' **derived** architecture
values — at the same derived architecture value. `history` prints the changes as
bars between the rows and says plainly that rows on opposite sides are not
comparable.

*Executed as:* every declared change must name a commit that resolves **and**
that actually touched one of its declared instrument paths — a fictional era
boundary is a violation — and every card measured before a change affecting its
example, carrying no note, is reported `OPEN`.

**The third clause — architecture. THE RULE, AND FROM VERSION 4 THE RULE IS ALL
OF IT.**

> **Architecture is a comparability axis: name it before you compare, and never
> rank the values.** The moment one value is better, the tag is a target and
> `MF-020` applies.

That sentence is what this clause asks of a reader, and it is now the whole of
what this card carries about it. Thirty-eight lines of derivation,
refusal-authority keying and failure modes used to sit here. They are a **design
record, not a bar for a score**, and they describe a mechanism that does no work
until a project has run enough rounds to populate its own `[[demonstration]]`
table from its own cards — so on day one they are pages about something that
says nothing, addressed to a reader whose table is empty and whose language the
derivation cannot parse. **Nothing is deleted; it is moved to where it belongs.**
`references/architecture_tags.md` is RD-04's and RD-05's sealed design record.
It is not documentation for anyone adopting this card and it should stop being
read as any.

*Executed as:* `score_tools.py tags` derives every scope declared in
`examples/validation/scorecards/subjects.toml`, marking `NULL-ENTAILED` any
`does not separate` verdict whose population range is a single point — a null
result that could not have come out otherwise is not a null result. `audit`
re-derives the table from the cards on every run: a `[[demonstration]]` the
cards no longer support is a **VIOLATION**, a separation with no entry beside it
is `OPEN`, and a card whose D3 citations fall predominantly outside its declared
scope is `SCOPE-DRIFT`. **A scope change is not an architecture change and must
never be read as one.** Only a DERIVED value ever refuses, everything unresolved
fails open, and a tag can never reduce the set of printed numbers — it can only
add a word beside two of them.

> **What the axis rests on, stated as a limit.** One example, one dimension, and
> a `sonnet` `ports-and-adapters` population that is one tree scored twice.
> Earn-its-place is a **deletion** rule and not a promotion one: it establishes
> correlation, cannot establish cause, cannot detect a ceiling, and cannot see a
> value occurring in one example. Delete decoration with it; do not admit a
> value with it.

### R-H2 — Never average across examples

A deliberately incoherent fixture is *supposed* to score low on D3; a mean over
it and a coherent one is a number about nothing.

*Executed as:* `history` requires `--example` and has no cross-example mode;
`index` computes nothing across examples; a claim naming more than one example
is a violation, and a note about a card or claim that does not exist is a
violation.

### R-H3 — A number that moved because the instrument was repaired is not improvement

Say which happened. A repair that moves a number is a fact about the instrument;
only a movement measured across an unchanged instrument is a result.

*Executed as:* a claim that is still `current` while an instrument change
affecting its example post-dates its `measured_at`, with no `reaffirmed_at` after
that change, is reported **SUPERSEDED-UNMARKED**. Two escapes exist and both cost
something: `delta_basis = "within_run"` (both ends measured in one run, so no
boundary applies), and `status = "under_review"`, which is only legal with a
`filed_as` naming a real id in `deferred_findings.yaml` — so a number cannot be
parked quietly.

**And the converse, which this rule originally missed.** A repair can move **no**
number and still change what the numbers mean. PA-04 shipped `control_red = []`
while a positive control had SURVIVED four columns that each executed 294
accepting `Reserve` cases; executing the control's declared role moved **zero
verdicts across all 90 cells** and turned that field into seven red entries. The
kills were untouched — what changed is that the `SURVIVED` cells beside them
became a **floor** instead of evidence. So a `[[change]]` declares
`verdicts_moved`, and **zero is an answer that has to be measured**. Where no
cell-for-cell diff exists — the two sides scored different artifacts — it
declares `verdicts_unmeasurable` and says why. `audit` reports any repair that
declares neither.

**A goal verdict is not always one word.** `GOAL-port-reach` is *clause 1 met,
clause 2 not met*. Record each clause as its own claim: a ledger that stores one
token per goal has to choose, and it will choose the flattering one.

> **A STRADDLE IS A PROMPT TO GO AND LOOK, NEVER A FINDING ON ITS OWN.** `audit`
> reads claims and commits; it does not read kill tables. It can tell you a
> number was measured on the far side of a repair — it **cannot** tell you
> whether the repair touched the cells that number is about. Answer that from
> the raw data before filing anything. PA-05 did not, and filed `PA-05-DF-02`
> claiming a repaired cell had contaminated a baseline it was never in the
> denominator of; two JSON files, in the commit PA-05 had itself declared the
> instrument change, settled it in one pass.

A claim that was asserted in review and then falsified is `status = "refuted"`,
which requires `refuted_by` and `why` and **keeps its `filed_as`** so the finding
stays reachable. It is deliberately not `known_wrong`: that is a *measurement*
that stopped being true, whereas this is an *assertion someone made* that was
shown false. Keeping the two apart is the point — a finding that turned out to be
wrong is evidence about the review, and deleting it hides the review rather than
the error. `filed_as` is verified on every status, not only `under_review`.

### R-H4 — A sealed card is never edited

When one goes stale, the ledger records **which** number and **why**, beside it.
The correction goes in `INSTRUMENT-LOG.toml` as a `[[note]]`, and `history`
prints it beside the row.

*Executed as:* `seal` records a digest per sealed card and refuses to re-seal one
whose contents changed; `audit` re-verifies every digest.

### R-H5 — A movement is a measurement only if the judging practice is recorded at both ends

**Was "Known instability of this card", added at the close of `ports-as-adapters`
from `PA-06-DF-06`, and deliberately NOT numbered.** That first draft numbered it
`R-H5` and `audit` rejected it within the minute, because `R-H` ids are exactly
the declarations `score_tools.py` executes and it had no check behind it. The
mechanism PA-05 built to stop unexecuted declarations caught the epic owner
adding an unexecuted declaration, in the same file, at close. **FI-03 gave it a
check, so it is a rule now.**

*Executed as:* a movement between two cards is declared as a `[[movement]]` in
`INSTRUMENT-LOG.toml` naming `from_card`, `to_card`, `dimension`, `points` and
`readable`. **`audit` re-derives `points` from the two cards on every run**, so a
declared movement cannot drift from the scores it is about; a stale one is a
violation. `readable = true` is a violation whenever either end carries no
`judging_practice` — the movement may be real and it is not readable, because the
variable that produced the last one is unrecorded at that end. Movements across a
version 1 card are therefore `readable = false` permanently, and that is the
correct answer rather than a defect to be cleared.

The instability this rule is about, which is the reason version 2 exists:

Arms A and B were re-scored at PA-06 as **byte-identical trees** to the ones
EVAL-RERUN judged. Four dimension-points moved anyway:

| | EVAL-RERUN | PA-06 |
|---|---|---|
| arm A **D4** | 2 / 2 | **4 / 4** |
| arm A **D5** | 3 / 2 | **4 / 4** |
| arm A **D1** | 3 / 3 | **4 / 3** |
| arm B **D4** | 3 / 2 | **4 / 4** |
| arm B **D5** | 4 / 3 | **4 / 4** |
| arm B **D1** | 3 / 3 | **4 / 3** |
| **D2 and D3, both arms** | | **unchanged, zero points** |

**The mechanism is identified and it is not the rubric.** Both PA-06 judges
recorded, independently and unprompted, that they **seeded their own faults and
ran them** rather than scoring the evidence packet. D4 anchor 4 requires that a
deliberate behavior-breaking change is *shown to be caught*: a judge who executes
one can award it; a judge reading a table cannot. So the top anchors are
sensitive to **judging practice**, which nothing here mandates and nothing
records.

Two consequences, and the second is the load-bearing one:

- **A D1, D4 or D5 delta of ≤ 2 points per judge across rounds is within
  demonstrated noise and is not evidence of improvement.** Say what the judges
  did, or do not read the movement.
- **D2 and D3 are the dimensions that have held still on unchanged input**, and
  they are the two about the artifact's shape rather than about what the judge
  did. A cross-epic claim is safest on those. This is why `ports-as-adapters`
  rests its headline on D3.

**Fixed in version 2, and the fix is recording rather than mandating.** Rule 8
makes `judging_practice` a required field; only D4's anchor 4 is gated on it,
because only D4's anchor asks the judge to run something. A card that says
`executed_own_faults: false` is legal and is recorded as `PACKET-ONLY`. **What
version 2 removes is not the choice — it is the choice being invisible.**

> **AND RECORDING IT DID NOT MAKE THE CARD STABLE.** FI-03 re-scored the same
> three sealed, byte-identical artifacts with two fresh blind judges and
> measured the movement per dimension per judge. The result is in
> `specs/results/scorecards/falsifiable-instruments/GOAL-scorecard-carries-a-delta/RESULT.md`
> and it is not a pass. Read it before quoting any D1, D4 or D5 delta.

### R-H6 — `contested` is computed from the cards, never declared on one

**Scoring rule 5 has said since version 1 that any dimension where two judges
differ by more than 1 is `contested`. Nothing computed it for three epics.**
Every card ever written carries `contested = []`, including the four
`toolchain_removal` cards whose D3 came out **2, 2, 3, 4 — a spread of 2** —
where `index` printed `—` on all four rows.

It was never filled in for a structural reason, and that reason decides the fix.
`contested` is a property of a **judge group** — the judges of one artifact in
one round — and rule 5 also says those judges are **blind to each other**, so a
field asking one judge to record how far they are from another asks for
something that judge is forbidden to know. So it is **computed on every read**,
and the card's own `contested` field is read as a *declaration* and compared
against the computation. Where they differ the computation wins and the
difference is printed beside the row, because a sealed card is never edited.

```
python3 examples/validation/scorecards/score_tools.py contested
```

*Executed as:* `contested` and `index` re-derive the spread per dimension per
judge group. A card **declaring** a dimension contested that the cards do not
support is a VIOLATION — a declaration must not be able to manufacture one, for
the same reason `EVAL-SUPPRESS` showed it must not be able to erase one. A group
that **is** contested and carries no `[[contested]]` entry in
`INSTRUMENT-LOG.toml` is reported `OPEN`, so the flag firing with nothing beside
it stays visible rather than being satisfied by being printed. A `[[contested]]`
entry whose `spread` or `scores` no longer match the cards is a VIOLATION,
re-derived exactly as R-H5 re-derives `points`; one that says nothing about the
third pass rule 5 asks for is a VIOLATION, and **`third_pass = "none"` is a legal
and useful answer while silence is not.**

**And the judge tier is a field of the card.** `opus` judged D3 **2, 2** and
`sonnet` **4, 3** on the same artifact while D2 agreed across both tiers, and
nothing in the record surfaced it. `judge.tier` is **derived** from `judge.model`
wherever a model id names a tier — a tag asserted by hand is a tag that can be
asserted wrongly — and `check` refuses a declared tier that contradicts the model
id. `contested` and `index` report a **tier split**: a dimension where two tiers'
score ranges are **disjoint** on the same artifact. An overlap is deliberately
not a split; calling one would let the tag say something the numbers do not.

### R3 — a claim carries its scope

**A figure of the form `D<n> = k on N of N cards` is a statement about whichever
examples produced those N cards.** If the population its own words denote is
wider than the set it was computed over, **the claim is wrong even when every
number in it is right.** `R-H2` forbids *averaging* across examples; nothing
forbade *generalising from one*. `subtract-to-measure` was opened on
*"D2 = 2 on 27 of 27 cards"* — true of one example — restated it in the charter,
the plan and the issue, and "verified" it with a script containing
`if "ab_quota_ledger" not in f: continue`.

```
python3 examples/validation/scorecards/score_tools.py scope
```

*Executed as:* every such figure in the charters, the plan, the ledger and the
narrative results is re-derived against the cards on disk, read **at the scope
its own words carry** — the named example when one sits beside the figure, every
card when none does. A figure with a counterexample in the population it denotes
is `REFUTED` and the contradicting cards are **named**. A figure with no
counterexample whose denominator has moved is `COUNT-MOVED`, which is staleness
and is not refutation. **What it cannot reach is counted separately and never
omitted** — an anaphoric scope, an arm label, a non-card noun, a qualifier the
corpus does not define — because `absent` and `checked, none found` are different
claims and this project has been caught conflating them.

It **refuses a claim and gates nothing about any artifact**; no close path
consults it. It exits non-zero on this repository's own record, and that is its
demonstrated failing input rather than a defect in it — see
`examples/validation/instruments/instruments.toml`.

## An instrument's absent input (`R1`, extended by `SS-02`)

`R1` says **an instrument ships with a demonstrated failing input on a real
subject**. It says nothing about an input that is **not there**, and `CA-10`
measured what that costs: **48 instances across 30 of 43 verdict-producing
modules** answer PASS — clean, disposed, `0 violation(s)`, exit 0 — when handed
an input that is absent, empty or unparseable, and **every one of the 48
satisfied `R1` in full**. An instrument can carry a passing demonstration, a
failing demonstration, and still answer PASS to the question it was built to
refuse, because the third input was never in the contract.

**So `R1` now has a third clause: every instrument ships a demonstrated
absent-input case, and the correct answer is UNDECIDED or a refusal — never
PASS.** Three states, not two:

| state | the input is |
|---|---|
| `absent` | not in the tree at all |
| `unreadable` | there, and unreadable as itself — empty, truncated, malformed |
| `empty` | read and parsed perfectly, and genuinely naming nothing |

**Two is not enough, and that is measured rather than asserted.**
`CA-10-DF-11` repaired the absent ledger with a signature change,
`set[str]` → `set[str] | None`, *because the old type could not distinguish
"read and found nothing" from "read nothing" and answered the second with the
first*. `SS-01` then repaired the **wrong** ledger. An independent reviewer
handed the result a ledger that **existed and named nothing** and got **14
confident fabrication accusations against real citations** (`SS-01-DF-04`). **A
fallback that merely moves the false PASS to a rarer input has not fixed the
class.**

**It is executed, not cited** — a doctrine line with no instrument is a
preference:

```
python3 examples/validation/scorecards/score_tools.py absent-input
python3 examples/validation/scorecards/score_tools.py absent-input --contract-only
```

It reads **this project's own instrument register**,
`examples/validation/instruments/instruments.toml`, where each contract lives
beside the `failing` and `passing` demonstrations of the same instrument. It
**refuses that register today**, and the count of instruments with no
absent-input case is its product; there is **no target on that ratio**. Two
things it does deliberately: it reports **states an instrument cannot tell
apart**, found by executing them rather than by reading the contract, and it
answers **UNDECIDED (exit 2), never 0**, when handed an absent, unreadable or
instrument-less register of its own — a check for this class that answered PASS
to an empty input would be the next instance of it.

**It gates nothing.** No close path consults it, it decides nothing about any
subject program, and it must not become a check over an adopter's code.

## Changing this card

Bump `scorecard_version`, keep the old anchors in the file, and re-score at
least one prior example under both versions so the discontinuity is measured
rather than assumed. A card that changes silently makes every historical
comparison a guess.

`score_tools.py scaffold --card-version N` emits the schema of card version N so
that re-score is possible at all; a tool that can only write the current version
makes the rule above unfollowable.

**The bump itself is two edits to this file and none to any Python.** Change
`**Scorecard version N.**` at the top, and add a row to
[Version history](#version-history) keeping every older row. `score_tools.py`
reads the population of legal versions out of that table rather than carrying one
— it used to carry `SUPPORTED_VERSIONS = (1, 2, 3, 4)`, which made this rule
unfollowable by anyone who could not edit our source, and stamped the nearest
number it did know when the flag was dropped. A version this file does not
declare is now refused by name. `references/adopting_the_scorecard.md` is the
short how-to for a project that is not this one.

**`--card-version` alone is not enough, and saying so is part of the rule.** It
stamps the requested version number while reading every anchor, rule and digest
out of the rubric file it is pointed at, so on its own it reproduces the old
*schema* against the *new* bar. Reproducing the old card means also pointing it
at the old rubric: **freeze the rubric file before you edit it**, and scaffold
the old arm with `--rubric <the frozen copy> --card-version N`. FI-03 did this
by sequencing (`rubric_v1_frozen.md`); SM-04 did it the same way
(`rubric_v2_frozen.md`). That it is operator sequencing rather than a mechanism
is `FI-06-DF-11(c)`, open. RM-03 did it the same way a third time
(`rubric_v3_frozen.md`), which is three of three and is the argument for making
it a mechanism rather than the argument that sequencing works.

> **WHAT THIS RULE COSTS A REMOVAL, measured on version 4 rather than asserted.**
> *"Keep the old anchors in the file"* and `R-H4`'s *"a sealed card is never
> edited"* together mean **a card cut cannot delete prose and cannot delete
> code.** The anchors move from the served section to
> [Retired anchors](#retired-anchors-versions-1-3) rather than leaving the file,
> and every line of `score_tools.py` that enforces a version 1–3 rule has to
> stay, because 73 sealed cards are still checked by it. Version 4 removed three
> dimensions and one anchor from the card **and made this file and its tool
> longer.** The card an adopter reads got smaller; the substrate did not. That is
> not an argument against the rule — it is the reason a removal must be priced
> per removal and never reported as a total.

### Version history

**Two columns, because they answer two questions and one of them was not being
asked.** The `anchors digest` is over the **anchors alone**, so two versions
carrying the same one is the statement that **the bar for each score did not
move** — only what a card must record about itself did. The `served digest` is
over **the bytes `serve` emits**: the anchors *and* the preambles, the caveats,
the scoring rules and the recorded notes. A caveat rewritten in someone else's
words changes what a judge reads and leaves the anchors digest byte-identical,
which is how a rewrite could delete a caveat from the served surface with
nothing reporting it. `score_tools.py check` recomputes **both** from this file.

The served digest is carried from version 4 on. Rows 1–3 declare none and can
never declare one: the bytes those versions served are a property of the file as
it stood then, and rendering them from this file would produce a digest no judge
was ever handed. Note also what neither column does: `check` recomputes only the
**current** version's row, so it detects a stale table rather than a moved bar.
That is `FI-06-DF-11(a)`, open.

| version | anchors digest | served digest | what changed |
|---|---|---|---|
| **1** | `sha256:eeccf4576bc6fd85` | — | the original card: five dimensions, seven scoring rules, R-H1..R-H4. |
| **2** | `sha256:eeccf4576bc6fd85` | — | `judging_practice` required on every filled card (rule 8); D4 = 4 gated on it; the instability caveat promoted to R-H5 with a check. **Anchors unchanged.** |
| **3** | `sha256:eeccf4576bc6fd85` | — | the judge is served a generated card and never this file (rule 9); `served_digest` and `file_sha256` recorded per card; D5 anchor 4's two readings recorded in `anchor_reading`; `total` removed from the card and from every rendering. **Anchors unchanged.** |
| **4** | `sha256:f73b4d82638f09df` | `sha256:a213a36770ccab09` | **THE ANCHORS MOVED, for the first time.** D1, D4 and D5 stop being scored and become recorded notes (rule 10); D2's anchor 4 is deleted, so D2 is a 0–3 scale; D2's preamble stops requiring a measured descriptor to be read first. Retired anchors below, byte-identical. |
| **5** | `sha256:f73b4d82638f09df` | `sha256:2d7d4a0506d9b259` | **THE ANCHORS DID NOT MOVE AND THE SERVED BYTES DID** — the first row in this table for which that is true, and the class of change CL-01's second seal was built to catch. D3's caveat now says that anchor 4 is satisfied by a real adapter that does nothing real, because the fixture 22 `D3 = 4` cards rest on has exactly that hole (`RM-05-DF-05`). Rule 9 loses a sentence that restated the served preamble verbatim. No anchor added, deleted or reworded; the served surface FELL, 6,319 → 6,281 bytes, rungs 9 → 9. |

### Retired anchors, versions 1–3

**Kept verbatim, and kept OUT of the served surface.** `Changing this card`
requires the old anchors to stay in the file; `serve` renders parsed structure
only and the parser matches `### D<n> — <name>` headings, which these
deliberately are not. So they are readable by a person comparing two versions
and unreachable by a judge scoring under either.

**D1 — bug detection** *(retired at version 4)*

- **0** — Cases exist and pass; no seeded fault is caught. A suite that is green
  on broken code.
- **1** — Catches faults that change a value the projection already prints.
  Misses everything requiring a content assertion.
- **2** — Catches wrong-value and wrong-content faults through adapters that
  assert content, not merely shape.
- **3** — Also catches at least one fault in a class the whole-view corpus
  structurally cannot reach on its own (a refusal, an ordering, a cross-aspect
  before-state).
- **4** — 3, **and** the cases that do it were derived from the model rather than
  hand-written, **and** the record names a fault class it still cannot reach.

**D2's anchor 4** *(retired at version 4; anchors 0–3 are unchanged and live)*

- **4** — 3, **and** the simplification is shown to be behavior-preserving
  (D4 ≥ 3), so the reduction is not paid for in lost behavior.

**D2's preamble** *(retired at version 4)*

> Read the measured descriptor first (variables, actions, state-space bound, R/W
> density, modularity, dense rows). Then judge whether the numbers reflect
> essential behavior or accidental structure.

**D4 — behavior preservation** *(retired at version 4)*

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the
  behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown
  still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant)
  rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be
  *caught* — the check is demonstrated to be capable of failing.

**D5 — honesty** *(retired at version 4)*

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself
  and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not
  support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is
  unflattering to the thing being scored.

D5's anchor 4 carried two defensible readings — `disclosure` and `measured` —
and version 3 required a card to say which it used. Both were legal, neither was
corrected, and the requirement retires with the anchor. `check` still enforces
it on every version 3 card.

**The discontinuity between 1 and 2 was measured, not assumed.** FI-03 re-scored
the same three sealed artifacts twice on the same day — once under version 1 and
once under version 2 — with four fresh blind judges, and reports both the v1
movement against the sealed rows and the v1-to-v2 difference. See
`specs/results/scorecards/falsifiable-instruments/GOAL-scorecard-carries-a-delta/RESULT.md`.

**The discontinuity between 2 and 3 was measured the same way, at a quarter of
the scale, and the reduced power is part of the result.** SM-04 re-scored one
prior artifact from the same example with four fresh blind judges — two under
version 2 against a frozen copy of the version 2 rubric, two under version 3 —
on the same day, from the same dispatch text. See
`specs/results/scorecards/subtract-to-measure/SM-04/RESULT.md`.
