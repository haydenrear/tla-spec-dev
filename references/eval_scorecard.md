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

## Changing this card

Bump `scorecard_version`, keep the old anchors in the file, and re-score at
least one prior example under both versions so the discontinuity is measured
rather than assumed. A card that changes silently makes every historical
comparison a guess.
