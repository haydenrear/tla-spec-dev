# RP-01 — False `coherent`: the declared-partition bypass

EV-01-DF-02 / EV-02-DF-01 / AC-03-DF-01. Advisory throughout: every command
below exits 0, nothing new blocks a close, a promotion, or a case generation,
and no move is suggested (CD-01).

## The reproduction

Six lines of YAML declaring a ONE-component partition, against the divergent
fixture (four seeded divergences and one absence):

```
$ cd examples/validation/ex5_pipeline_divergent
$ python3 ../../../scripts/architecture_reflexion.py \
    specs/program_model/Pipeline.tla specs/program_model/Pipeline.cfg \
    --components <one component> --code pipeline --map <one component>
```

| | verdict | blind spots | exit |
|---|---|---|---|
| before | **`coherent`** | `[]` | 0 |
| after | `unmappable` | `[]` — it is a **basis limit**, not a blind spot | 0 |

Full transcripts: `repro-one-component-before.txt`,
`repro-one-component-after.txt`, with the inputs at `repro-onecomp.yaml` /
`repro-onemap.yaml`.

## What changed, and why

### 1. `divergence_detectable` is now read by the verdict

The guard read `if not report.unported_pairs and len(names) >= 2`, which
excluded the strongest case of the thing it was written to catch: a
one-component partition has **no component pair at all**, so it passed
vacuously. The condition no longer lives in a guard that appends to a list.
`ReflexionReport.unsupported_clean()` derives it on every call from the
descriptor and the pair sets, and `verdict` consults it directly — so it cannot
be computed, published in the JSON, and read by nobody a second time. The
regression test empties `blind_spots`, `divergences` and `absences` and the
verdict still holds.

### 2. A declared partition that fails the criteria cannot buy a clean

`consumable_as_architecture` is `true` for any declared partition, which is
correct for AC-02's question ("did the project name a boundary to compare code
against") and was being used to answer a different one ("can this boundary
support a certificate"). The failed criteria are now published with their
measurements in the text and in the JSON, and the verdict withholds `coherent`.

**The partition is not refused** (NEXT-EPIC NE-01 point 3: carry the fact, not
the judgment). The comparison runs, every divergence keeps its `file:line`, the
command exits 0.

### 3. `basis_limits` is not `blind_spots` — and the split was measured

A blind spot is something the extractor **could not see**: nothing measured
under one can be trusted, so it collapses every verdict to `unmappable`. A
basis limit is the opposite — the target was seen in full, and what cannot be
supported is only the **certificate**. So a basis limit withholds a clean and
never touches a finding.

The first implementation of this ticket filed both as blind spots. Measured on
the sweep, that costs **67 of the 71 real divergence verdicts** and removes no
false clean that withholding `coherent` does not already remove. Recorded in
`df02-blast-radius-comparison.txt` so the choice is not re-litigated from taste.

### 4. Undefined is `null` with a reason, never `[]` (AC-03-DF-01)

- `components[].owns` is `null` + `components[].owns_basis` when the partition
  has one component. It was `[]`, which reads as *owns nothing* — a plausible
  architectural fact — where the text said `NOT MEASURABLE`.
- The same defect one field over: when the comparison never ran, the reflexion
  JSON said `convergences: []`, `divergences: []`, `absences: []`,
  `modules_scanned: 0`. The text renderer has always said "not zero of them";
  the JSON is what a consumer reads. All are now `null`, with
  `measured.not_measured` carrying the reason.
- `[]` and `0` now mean only what they say: measured, and empty.

### 5. The basis travels with the verdict

`verdict.measured_against` carries partition source, origin, component count,
every criterion with its measurement, the failed criteria, and
`divergence_detectable`; `verdict.clean_result_supportable` summarizes them;
`verdict.unsupported_clean_reasons` says why when false. The text report prints
the same basis twice — once above the findings, once beside the verdict.

## Validation

| check | result | evidence |
|---|---|---|
| zero TLA+ model delta | `current` == `desired`, byte for byte (`__pycache__` cleaned first) | `zero-model-delta.txt` |
| TLC on ticket current | green — 32,122,220 generated / 1,292,951 distinct / depth 26 / 0 left on queue, 58s. Identical to the epic baseline. | `tlc-current.txt` |
| spec-unit tests | 2 targets, 71 + 68, exit 0 | `spec-unit-tests.txt` |
| repository unit tests | **878 passed, 1 failed** — `test_skill_requires_two_minute_case_generation_budget`, the pre-existing red being fixed by RP-05 concurrently; untouched here. Baseline was 860 + the same 1. | `repository-unit-tests.txt` |
| 203-partition sweep | **12 `coherent` → 0.** Zero partitions produce a clean the criteria do not support. | `df02-blast-radius-after.json`, `df02-blast-radius-comparison.txt` |
| ex4 false-positive control | still **`coherent`**, honestly: partition decomposes, `divergence_detectable = true`, clean supportable | `ex4-coherent-control-after.txt` |
| ex5 honest partition | still **`divergent`**: 4 divergences + 1 absence, all with `file:line` | `ex5-divergent-after.txt` |

### The sweep, in one table

| verdict | EV-02 (before) | RP-01 (after) |
|---|---|---|
| `coherent` | 12 — **all 12 fail the criteria** | **0** |
| `divergent` | 71 | 91 |
| `unmappable` | 120 | 112 |

Two transitions, both intended: `coherent → unmappable` ×12 (exactly EV-02's
false cleans) and `unmappable → divergent` ×20. The second is not a relaxation
— every one of those 20 had `unfalsifiable_coherence` as its only blind spot
and carries exactly one real **absence**, which the old classification masked.

## Regression tests

`tests/test_architecture_reflexion.py::TestNoDeclaredPartitionBuysACleanTheBasisCannotSupport`
— 12 tests, **every one of which fails on the pre-RP-01 production code**
(verified by restoring both scripts from `HEAD` and re-running). Plus
`tests/test_analyze_architecture.py::...::test_blob_does_not_report_zero_single_writer_violations`,
extended to hole 3 and also failing pre-fix.

## The fixture repair, which is itself a finding

The unit suite's ONLY positive `coherent` case declared three singleton
components over three variables. A singleton partition has no intra-community
weight, so its modularity Q is negative **by construction** — it measured
−0.375. The suite's positive case was therefore itself an instance of the
defect this ticket closes: a clean certified against a partition the model's
own criteria reject. The fixture now gives each component a second variable and
an interacting action, measures Q = +0.260 with 2 of 7 actions crossing, and
meets every criterion. A structureless `BLOB_TLA` was added for the tests that
need a model with no architecture.
