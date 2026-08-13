# `GOAL-four-results-stand` — baseline

**Measured at the epic base `08d1d6a90ad2638cdfceee7cc2e150732daa3438`.**

This is the goal that constrains every other one. **A silently broken result is
the worst outcome available and fails this goal even if the lines fell.**

---

## The four results, each with the evidence that makes it checkable

### 1. Asking for an architecture changes the architecture

D3 went **1 → 4** on the prompt alone, replicated across rounds.

**The confound was killed directly, not argued away:** `arm C` — a *longer*
prompt carrying **no architectural vocabulary** — scored **1/1**. Prompt length
is not the mechanism.

- evidence: `examples/validation/ab/arm_a`, `arm_b`, `arm_c`;
  `specs/results/scorecards/ports-as-adapters/`

### 2. D3 separates architectures on more than one example

`eval_toolchain` — **the first example that is neither the house fixture nor a
hand-built case**:

```
effectful             [0, 1]
ports-and-adapters    [2, 4]
```

**Disjoint, and both judge tiers on both sides** — which `ab_quota_ledger`
cannot say.

- evidence: `specs/results/scorecards/portable-substrate/`

### 3. D3's v5 caveat discriminates

`SV-01`. On an artifact **lacking** the single-observer property, D3 held
**4, 4** at v4 and **4, 4** at v5. On one that **has** it (`CL-03`), D3 fell
**4, 4 → 3, 3**.

**Prediction sealed at a timestamped commit before any judge ran.**

- evidence: `specs/results/scorecards/score-drives-validation-sv01-v4/` and
  `-sv01-v5/`
- **discount, disclosed by the ticket itself:** `SV-01-DF-01` — all four judge
  scratch paths were a prior round's, holding the previous artifact and a prior
  `D3 = 4` one `ls` away. **A contamination that cuts toward the predicted
  answer.** Discounted, not withdrawn.

### 4. A score can produce a test and the re-score sees it

`SV-04`. Control arm **3, 3** vs treatment **4, 4** — **same bytes plus one
file** — with **D2 flat at 2 across all four**. `0 for 7 epics` became
`1 for 8`.

- evidence: `specs/results/scorecards/score-drives-validation-sv04/`

---

## The four disproofs, which are equally load-bearing

| disproof | figure |
|---|---|
| Model-derived cases do not catch bugs hand-written tests miss | **0** unique kills across six trees, **4** the other way, replicated on new subjects |
| Static gates catch nothing | seven epics, **zero** bugs caught by a static check |
| The removal-pricing instrument could only ever return zero | **0 of 9** over the sealed table |
| Three of the card's five dimensions graded toolchain ownership | **38%** of D1 and **18%** of D4 anchor rationales cited local machinery, against **0%** on D3 and D5 |

**`CA-04` must state explicitly whether disproof 1 is still reproducible from
the sealed record once the instrument that produced it is gone.**

---

## Instruments that must still run at the tip

`RM-02`: *"the substrate's best export, and the epic should be careful not to cut
them for being unglamorous."*

`scope`, `seal`, `contested`, the blinding mechanism, `R-H1`/`R-H2`/`R-H4`/`R3`,
and the version/served double seal. **`CL-01`'s second seal caught a real class
one ticket later.**

## The card at the base

```
serve | wc -c        6281
serve --digest-only  sha256:2d7d4a0506d9b259  (card version 5,
                     rubric file sha256:b7fe75437bf68646)
```

9 rungs, 2 scored dimensions.

---

## The suite at the epic base

Command — **this one, not `README.md:35`, which omits `--with pyyaml` and yields
12 phantom reds**:

```bash
uv run --with pytest --with pyyaml -m pytest tests -q
```

<!-- SUITE-BASELINE-START -->
*(pending — filled in by the run started at epic kickoff on this branch)*
<!-- SUITE-BASELINE-END -->

**Compare against this figure, not against a recollection.** Two reds are
inherited and deliberate — `RM-06-DF-01` (the same-tag control cannot tell
treatment from architecture) and the pricer grep tripped by narrative documents
— and `SV-02` and `SV-01` independently found a **third undeclared** red last
epic. **Do not repair any of them silently**, and **declare** any red beyond
this baseline with its cause.
