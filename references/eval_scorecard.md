# The Eval Scorecard

**Scorecard version 3.** Every eval in this repository is scored on this card,
by an agent judge, against artifacts. The card is the unit of comparison across
epics: one epic's numbers mean something only next to another's, so the card is
versioned and changing it is a deliberate, recorded act.

**Version 2 changed one thing: what the judge DID is now a field on the card.**
**Version 3 changed three, and none of them is an anchor.** The anchors are
byte-unchanged from version 1 — see [Version history](#version-history), whose
digest is checked by `score_tools.py check`. Cards written under an older
version stay valid, stay comparable to each other, and are **not** comparable
across a version boundary without saying so.

What version 3 changed:

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

Five dimensions, each scored **0–4**, total **0–20**. Three are the owner's
stated goals; two exist because they are the failure modes this project has
actually hit.

| | Dimension | The question |
|---|---|---|
| **D1** | **Bug detection** | Do the model-derived cases and their adapters *catch* seeded faults — especially the hard classes? |
| **D2** | **Complexity** | Is the design as simple as its behavior requires, and no simpler? |
| **D3** | **Modularity** | Is it ports and adapters in fact — domain independent of I/O, adapters swappable? |
| **D4** | **Behavior preservation** | Does the simpler design still do everything the baseline did? |
| **D5** | **Honesty** | Does the artifact refuse rather than falsely certify, and name what it cannot see? |

D5 is not a virtue score. It is here because `unobservable` beating a false clean
(MF-027) is the single doctrine that has survived every round intact, and because
an artifact that overstates its own reach corrupts every number next to it.

## The anchors

Anchors are what make two judges agree. Score the **lowest** anchor the artifact
fully satisfies; when torn between two, take the lower and say why.

### D1 — Bug detection

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

### D2 — Complexity

Read the measured descriptor first (variables, actions, state-space bound, R/W
density, modularity, dense rows). Then judge whether the numbers reflect
essential behavior or accidental structure.

- **0** — Complexity is unmeasured, or measured and ignored.
- **1** — Measured and reported; no relationship between the figures and the
  design is argued.
- **2** — The design's complexity is proportional to its behavior; no god-state,
  no variable written from everywhere.
- **3** — 2, **and** a simplification was made and its effect measured — the
  before and after figures are both recorded.
- **4** — 3, **and** the simplification is shown to be behavior-preserving
  (D4 ≥ 3), so the reduction is not paid for in lost behavior.

**A drop in a complexity number is not evidence on its own.** MF-020: a metric
can improve because an edge was deleted. A D2 of 3 or more requires the judge to
say *what got simpler and how the behavior survived it*.

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

**Import topology is not modularity.** Round 2 proved a codebase can pass every
import check with its coupling entirely intact. A D3 of 3 or more requires
evidence about what *calls* what at runtime, not what imports what.

### D4 — Behavior preservation

- **0** — Behavior changed and nobody checked.
- **1** — A test suite passes, with no argument that the suite covers the
  behavior at issue.
- **2** — The behaviors the baseline exhibited are enumerated and each is shown
  still to hold.
- **3** — 2, **and** the check is model-derived (a corpus, a TLC invariant)
  rather than only hand-written assertions.
- **4** — 3, **and** a deliberate behavior-breaking change is shown to be
  *caught* — the check is demonstrated to be capable of failing.

### D5 — Honesty

- **0** — Claims a clean it cannot support.
- **1** — Reports results without stating what was not measured.
- **2** — Names its blind spots and limits, unprompted, in the artifact itself
  and not only in a report.
- **3** — 2, **and** refuses to emit a positive verdict when its basis does not
  support one (`unobservable` / `unmappable` rather than a false clean).
- **4** — 3, **and** the record contains at least one result that is
  unflattering to the thing being scored.

**Anchor 4's phrase "a result unflattering to the thing being scored" carries
two defensible readings, and the card records which one you used.** Reading
**`disclosure`**: an artifact stating a limitation of itself is such a result.
Reading **`measured`**: anchor 4 asks for a result the artifact *measured*
against itself, and a stated limitation is anchor 2 and anchor 3 material.
**Both readings are legal, neither is the right one, and this note does not
change the bar** — score exactly the anchor you would have scored, and name the
reading in `dimensions.D5.anchor_reading`. It is required whenever D5 is scored
3 or 4, which is where the two readings can differ. Recording it is what makes
two judges who disagree readable: without it you cannot tell whether they
disagree about the artifact or about the anchor.

## Scoring rules that make it hard to game

1. **Score artifacts, never claims.** A summary saying "the adapters assert
   content" is not evidence; the adapter code is.
2. **Every score ≥ 2 cites `file:line`.** A score with no citation is capped
   at 1, mechanically, by the schema check.
3. **Every score of 4 additionally names something the artifact refuses to
   claim.** The top of every scale requires a stated limit. This is deliberate:
   it makes a perfect score impossible to reach by asserting more.
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
   neither is the right one; leaving it unsaid is what is not legal. **D4's
   anchor 4 is only awardable when it says `true`**, because that anchor asks
   for a behavior-breaking change *shown to be caught*, and a judge reading a
   table is repeating the artifact's claim rather than checking it. This is the
   anchor's own text made checkable, not a new bar.
9. **A judge is served the card, never the rubric file.** *(New in version 3.)*
   The scaffolded `scorecard.md` carries the rubric a judge needs. This file
   carries reading rules and prior results about these five dimensions as well,
   and a judge who reads it is handed conclusions about the instrument they are
   the instrument for. Every card records the digest of **the bytes it was
   served**, so a rubric change that can reach a judge cannot be invisible to
   that digest.

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
  "scorecard_version": 3,
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
    "D1": {"score": 2, "citations": ["path:line"], "rationale": "...",
           "refuses_to_claim": null},
    "D2": {"score": 3, "citations": ["path:line"], "rationale": "...",
           "refuses_to_claim": null},
    "D5": {"score": 3, "citations": ["path:line"], "rationale": "...",
           "refuses_to_claim": null, "anchor_reading": "measured"}
  },
  "contested": [],
  "verdict": "<one sentence a reader can act on>"
}
```

**There is no `total` from version 3.** A version 1 or 2 card carries one and
`check` still verifies its arithmetic; a version 3 card that carries one is
rejected.

`rubric.served_digest` is the load-bearing one. `rubric.digest` covers the
parsed anchors and scoring rules and is what `check` uses to refuse a skeleton
scaffolded against a stale bar. `file_sha256` covers the whole rubric file
including the parts a judge is never served: two cards whose `served_digest`
agrees while their `file_sha256` differs are reported `PROSE-DRIFT`, which is a
prompt to go and look and never a violation.

`arm` is `null` for a single-artifact eval and the arm label where arms exist.
`refuses_to_claim` is required and non-null for any score of 4.

`judging_practice` is **required on every filled card from version 2**.
`executed_own_faults` is a boolean and `what_was_run` is a list. `false` is a
legal answer, it is recorded as `PACKET-ONLY` by `check`, and it is never
corrected — a card that is pushed toward one answer records the pressure and not
the practice. The one consequence a `false` carries is that **D4 cannot be
scored 4**, and `check` rejects the combination.

`dimensions.D5.anchor_reading` is **required whenever D5 is scored 3 or 4**,
from version 3. It is `"disclosure"` or `"measured"` — see D5's note above.
Both are legal, neither is corrected, and it is not required at 0, 1 or 2,
where the two readings cannot differ.

## Reading a card

**There is no total, from version 3.** Its five terms are not five independent
readings: `D2` has taken one value on every card ever written about
`ab_quota_ledger`, and `D1`, `D4` and `D5` are each demonstrated to take a
different value from a different judge on the same bytes. A sum over them
moves for reasons a reader cannot attribute to anything, and it moves *most*
where the card is *least* readable — so it is the one number in this file that
rewards the dimensions that measure worst. `index` and `history` print the five
dimensions and no sum. **Read a dimension. There is nothing to read in a
headline.**

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

A row is comparable to another **only** on the same example **and** across an
unchanged instrument. `history` prints the changes as bars between the rows and
says plainly that rows on opposite sides are not comparable.

*Executed as:* every declared change must name a commit that resolves **and**
that actually touched one of its declared instrument paths — a fictional era
boundary is a violation — and every card measured before a change affecting its
example, carrying no note, is reported `OPEN`.

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

## Changing this card

Bump `scorecard_version`, keep the old anchors in the file, and re-score at
least one prior example under both versions so the discontinuity is measured
rather than assumed. A card that changes silently makes every historical
comparison a guess.

`score_tools.py scaffold --card-version N` emits the schema of card version N so
that re-score is possible at all; a tool that can only write the current version
makes the rule above unfollowable.

**`--card-version` alone is not enough, and saying so is part of the rule.** It
stamps the requested version number while reading every anchor, rule and digest
out of the rubric file it is pointed at, so on its own it reproduces the old
*schema* against the *new* bar. Reproducing the old card means also pointing it
at the old rubric: **freeze the rubric file before you edit it**, and scaffold
the old arm with `--rubric <the frozen copy> --card-version N`. FI-03 did this
by sequencing (`rubric_v1_frozen.md`); SM-04 did it the same way
(`rubric_v2_frozen.md`). That it is operator sequencing rather than a mechanism
is `FI-06-DF-11(c)`, open.

### Version history

The `anchors digest` column is over the **anchors alone**, not the whole rubric,
and `score_tools.py check` recomputes it from this file. Two versions carrying
the same digest is the statement that **the bar for each score did not move** —
only what a card must record about itself did. Note what this does *not* do:
`check` recomputes only the CURRENT version's row against the anchors in the
file, so it detects a stale table rather than a moved bar. That is
`FI-06-DF-11(a)`, open.

| version | anchors digest | what changed |
|---|---|---|
| **1** | `sha256:eeccf4576bc6fd85` | the original card: five dimensions, seven scoring rules, R-H1..R-H4. |
| **2** | `sha256:eeccf4576bc6fd85` | `judging_practice` required on every filled card (rule 8); D4 = 4 gated on it; the instability caveat promoted to R-H5 with a check. **Anchors unchanged.** |
| **3** | `sha256:eeccf4576bc6fd85` | the judge is served a generated card and never this file (rule 9); `served_digest` and `file_sha256` recorded per card; D5 anchor 4's two readings recorded in `anchor_reading`; `total` removed from the card and from every rendering. **Anchors unchanged.** |

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
