# RM-02 — the portability question, answered from the 73 sealed cards

**The decision is `references/portable_scorecard.md`. This is the evidence
under it.** RM-02 is a research ticket; no production code ships.

**Tree.** All figures computed at the epic base `2c0d94e`, working tree clean
for `references/`, `examples/`, `scripts/` and `prompts/`. Baseline `main` is
`19c5c7b`. No `git archive` was used and no figure here is an archive property.

**Re-run** — about two seconds from the repository root:

```
python3 specs/results/scorecards/portable-substrate/GOAL-portable/analysis/portability.py
```

`analysis/OUTPUT.txt` is that command's sealed output. `analysis/extract.py` is
the flat per-(card, dimension) dump the exploratory passes ran against.

**Neither script is an instrument.** They read sealed cards, print, and exit 0
unconditionally; there is no refusal path in either, nothing imports them, and no
close path consults them. That is deliberate under `no_new_gates_rule` — this
ticket ends with one fewer thing that can say no, not one more.

---

## What this cannot measure, said first

- **59 of the 73 cards are one example.** Every per-dimension figure is a figure
  about a corpus dominated by `ab_quota_ledger`, and `R-H2` forbids averaging
  across the rest. Where a claim is true of one example the decision page says
  which; where it is true of the whole corpus it says that instead.
- **The tier table is 8 judge groups, 7 of them one example, 6 of those 7 from
  one round.** It is enough to say *which* dimensions have been caught splitting.
  It is not a rate and must not be quoted as one.
- **Locality is measured by what judges wrote, not by what they thought.** §2
  below counts sentences in which an anchor decision and a local-machinery term
  co-occur. A judge who silently applied a local clause without naming it is
  invisible to it, so §2's figures are a **floor** on locality, never a ceiling.
- **No adopter was observed.** Every cost in §3 of the decision page is taken
  from rounds this project ran on itself, with the instrument's own authors
  operating it. That is a floor too.
- **The `effect_boundary` grouping in §4 uses the DECLARED value**, transcribed
  from `examples/validation/scorecards/subjects.toml`, because four of the
  grouped subjects are fixtures with no tree to derive from. A declaration never
  refuses a comparison (`architecture_tags.md` §3.3) and here it only groups.

---

## 1. Where judges look

Citation targets, all 73 cards, per dimension. `SUBJECT` is the artifact under
judgement; the rest are this repository's own surfaces.

| dim | citations | SUBJECT | EVAL-HARNESS | FORMAL-MODEL | REPO-SCRIPTS | SDC | DOCS |
|---|---|---|---|---|---|---|---|
| D1 | 377 | 84% | 11% | 1% | 1% | 0% | 0% |
| D2 | 358 | 86% | 7% | 3% | 2% | 0% | 0% |
| D3 | 373 | 86% | 9% | 2% | 2% | 1% | 0% |
| D4 | 331 | 80% | 15% | 1% | 0% | 0% | 0% |
| D5 | 382 | 78% | 17% | 0% | 2% | 0% | 1% |

**The card is not a repository checklist.** Whatever is local about it is local
in the anchors, not in where judges were looking — which is why the question has
to be settled from rationales.

## 2. Where the anchors bind

Share of rationales in which an **anchor decision** and a **local-machinery term**
(TLC, TLA+, model-derived, the whole-view corpus, generated corpora, spec double,
projection, catalogue) occur in the same sentence.

| dim | rationales | anchor decision resting on local machinery |
|---|---|---|
| **D1** | 73 | **28 (38%)** |
| D2 | 73 | 3 (4%) |
| **D3** | 73 | **0 (0%)** |
| **D4** | 73 | **13 (18%)** |
| **D5** | 73 | **0 (0%)** |

Verbatim, from the cards:

- *"Anchor 4 is refused: T's cases are hand-written."* — `ports-as-adapters/ab_quota_ledger/20260805-T-p2`
- *"Anchor 4 refused: hand-written, and the model-derived corpus is the shared instrument, identical across artifacts."* — `ports-as-adapters/ab_quota_ledger/20260805-U-p2`
- *"Anchor 3 requires the check to be model-derived — a corpus or a TLC invariant — … and this fixture ships neither."* — `architectural-coherence/ex5_pipeline_divergent/20260803-j1`
- *"Not 3: every check here is hand-written. The fixture ships no corpus and no TLC-derived instrument, so there is no model-derived check to raise the anchor."* — `architectural-coherence/ex5_pipeline_divergent/20260803-j2`

Both D1 = 4 cards in the corpus award anchor 4 on `corpus-neg`, the **eval
harness's** shared model-derived corpus, byte-identical across the arms being
scored — the same artifact other judges cited as their reason to refuse it.

### 2.1 The clause reaching D2, and splitting it by tier

D2's anchor 4 gates on D4 ≥ 3, and D4's anchor 3 is the model clause. On the
`reading-discipline` round's two cleared revision pairs, every card:

| arm | judge | tier | D2 | names the D4 model cap as its ceiling |
|---|---|---|---|---|
| `D` | p1 | opus | 3 | no |
| `D` | p2 | opus | **4** | no |
| `D` | p3 | sonnet | 3 | **yes** |
| `D` | p4 | sonnet | 3 | **yes** |
| `M` | p1 | opus | **4** | no |
| `M` | p2 | opus | **4** | no |
| `M` | p3 | sonnet | 3 | **yes** |
| `M` | p4 | sonnet | 3 | **yes** |

**4 of 4 `sonnet`, 0 of 4 `opus`.** The D2 tier split is the model-derivation
parenthetical read as a definition by one tier and an illustration by the other
— `RD-03-DF-14`'s proposed mechanism, confirmed here from the rationales,
unanimous within each tier. It is also the clause reaching a dimension that has
nothing to do with formal models and capping it, which is the sharpest evidence
in this ticket that what is local about the card is local in three clauses.

Re-derive:

```
python3 -c "
import json,glob,re
for p in sorted(glob.glob('specs/results/scorecards/reading-discipline/**/scorecard.json',recursive=True)):
    d=json.load(open(p)); v=d['dimensions'].get('D2')
    if d.get('arm') in ('M','D') and v:
        print(d['arm'], d['judge']['model'], v['score'],
              bool(re.search(r'ceiling|not reachable|anchor 4 (requires|needs|is not)',
                             v['rationale'], re.I)))"
```

## 3. Tier splits, as `R-H6` defines them (disjoint ranges, same artifact)

8 judge groups scored by both `opus` and `sonnet`.

| dim | split groups | directions |
|---|---|---|
| D1 | 0 of 8 | — |
| D2 | 1 of 8 | opus higher |
| **D3** | **3 of 8** | opus higher ×2, sonnet higher ×1 |
| **D4** | **4 of 8** | opus higher ×3, sonnet higher ×1 |
| D5 | 2 of 8 | opus higher ×2 |

Two of D3's three splits are one-point offsets at the floor (`[1,1]` against
`[0,0]`). The third is `toolchain_removal` at `opus [2,2]` against
`sonnet [3,4]`, which straddles the 2→3 seam. Full per-group rows are in
`analysis/OUTPUT.txt` §3.

## 4. D3 by declared `effect_boundary`, per example — never averaged

| example | `ports-and-adapters` | `effectful` | |
|---|---|---|---|
| `ab_quota_ledger` | 4 on all 18 cards | 0–2 on all 40 cards | **disjoint** |
| `toolchain_removal` | — | 2, 2, 3, 4 | |
| `ex4_pipeline_coherent` | 3, 3 | — | |
| `ex5_pipeline_divergent` | 1, 1 | — | |
| `ex1_scaffold_only` | — | 1, 1 | |
| `ex3_over_complex` | — | 1, 2 | |
| `ex6_jenga` | — | 0, 1 | |

One `ab_quota_ledger` card is unmapped — `20260804-owner-pre`, the
`A-control-reference` — leaving 58 of 59 grouped.

`ex5_pipeline_divergent` is the control that stops this being read as "declare
the tag, collect the 4": it declares `ports-and-adapters` and both judges scored
**D3 = 1**. `toolchain_removal` is the single counterexample and RD-04 already
dissolved it — the four judges scored three different subjects and the spread
inside each scope is zero.

## 5. Per-example ranges — what each dimension actually does here

`ab_quota_ledger`, 59 cards, eight rounds, three card versions, six arms:

| dim | distribution | span |
|---|---|---|
| D1 | 0:1, 2:1, **3:55**, 4:2 | 4 |
| D2 | **2:51**, 3:5, 4:3 | 2 |
| D3 | 0:6, 1:16, 2:19, **4:18** — nothing at 3 | 4 |
| D4 | 1:1, 2:25, 3:15, 4:18 | 3 |
| D5 | 2:6, 3:22, 4:31 | 2 |

**D3 has no mass at 3 on this example at all.** It is bimodal, which is what a
verdict on a style looks like rather than what a scale looks like.

## 6. The blinding label pool, checked mechanically

```python
import score_tools as st
taken = st.used_labels(pathlib.Path('specs/results/scorecards'))
[c for c in st.LABEL_POOL if c not in taken]   # -> ['G', 'J', 'L', 'V']
```

`LABEL_POOL` is 17 characters and excludes every label any prior round
published. **Four remain in this repository.** `scaffold` refuses a batch it
cannot label. RM-04 plans a blind round; this binds it. `RM-02-DF-01`.

## 7. `scope` over everything this ticket wrote

| | counted | REFUTED | COUNT-MOVED | HOLDS | UNREACHABLE |
|---|---|---|---|---|---|
| tree `2c0d94e`, before RM-02 | 70 | 55 | 0 | 0 | 15 |
| decision page added | 72 | 55 | 0 | 2 | 15 |
| findings filed as well | **76** | **55** | **0** | **4** | **17** |

**RM-02 refutes nothing and moves nothing.** It adds four counted figures and
all four HOLD — two in `references/portable_scorecard.md` §1 and the same two
quoted back in §9. They are the first entries in this repository's HOLDS column,
which is a statement about how rarely a figure here has carried its scope and
not a compliment to this ticket.

The two figures RM-02 adds to the UNREACHABLE column are both inside
`RM-02-DF-05`, the finding whose entire subject is that `scope`'s noun pattern
excludes the underscore. **The finding is unreadable to the checker for exactly
the reason it documents**, and it is left that way deliberately: rephrasing it
would delete the demonstration. The applicable bound is the second one,
`RD-04-DF-01`; see `references/portable_scorecard.md` §9 for the three figures
of this ticket's that are invisible to the checker rather than checked by it.

## 8. `audit`, and a pre-existing violation that corroborates §4

`score_tools.py audit` reports **1 violation at `2c0d94e` and 1 violation with
RM-02's changes — the same one.** RM-02 breaks nothing:

```
VIOLATION  [[demonstration]] effect_boundary-ab_quota_ledger-D3-effectful-vs-ports-and-adapters:
           declares ranges {'effectful': [1, 2], 'ports-and-adapters': [4, 4]};
           the cards give {'effectful': [0, 2], 'ports-and-adapters': [4, 4]}.
```

It is worth pointing at because `audit` re-derives that table from the cards
independently of anything here and lands on **the same `effectful` range §4
reports, 0–2** — the declared `[1, 2]` is the stale figure, not the measurement.
It is left standing: the epic files findings and fixes nothing during a
measurement, and this one the tooling already reports on every run.

## 9. Findings filed

`RM-02-DF-01` … `RM-02-DF-05`, in
`specs/desired_program_model/deferred_findings.yaml`. Five is the epic's budget
and none is blocking. **Nothing was fixed inline.**
