# The Eval Scorecard

**Scorecard version 1.** Every eval in this repository is scored on this card,
by an agent judge, against artifacts. The card is the unit of comparison across
epics: one epic's numbers mean something only next to another's, so the card is
versioned and changing it is a deliberate, recorded act.

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
  "scorecard_version": 1,
  "epic": "architectural-coherence",
  "example": "ex4_pipeline_coherent",
  "run_id": "20260803-sc1",
  "arm": null,
  "commit": "<sha the artifacts were scored at>",
  "judge": {"model": "<model id>", "pass": 1, "blind_to_arm": true},
  "dimensions": {
    "D1": {"score": 2, "citations": ["path:line"], "rationale": "...",
           "refuses_to_claim": null},
    "D2": {"score": 3, "citations": ["path:line"], "rationale": "...",
           "refuses_to_claim": null}
  },
  "total": 0,
  "contested": [],
  "verdict": "<one sentence a reader can act on>"
}
```

`arm` is `null` for a single-artifact eval and the arm label where arms exist.
`refuses_to_claim` is required and non-null for any score of 4.

## Reading a card

A total is for tracking one example over time. **Never average across
examples** — `ex6_jenga` is a deliberately incoherent fixture and is *supposed*
to score low on D3; averaging it with `ex4` produces a number about nothing.

Compare like for like: the same example across epics, or two arms of the same
eval. A dimension that moves is the result; a total that moves is a headline.

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

## Changing this card

Bump `scorecard_version`, keep the old anchors in the file, and re-score at
least one prior example under both versions so the discontinuity is measured
rather than assumed. A card that changes silently makes every historical
comparison a guess.
