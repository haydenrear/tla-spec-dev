# ex5 run 2 — EV-01-DF-02 verified independently, and its blast radius measured

Run date 2026-07-27, EV-02. **Mechanical run: no agent.** The epic owner
promoted EV-01-DF-02 into EV-02's scope with the instruction: *verify it
independently and measure its blast radius. Do NOT fix it.* Nothing was fixed.

DF-02 as EV-01 filed it: a DECLARED partition which the descriptor itself prints
as `DOES NOT DECOMPOSE` is still consumed, and the reflexion check reports
`coherent` against it **without mentioning that the partition failed the
criteria**.

## 1. Independent verification — confirmed, and worse than filed

Reproduced from EV-01's own inputs in this worktree
(`ex4_pipeline_coherent/evidence/df02_nondecomposing_partition/`):

```
analyze_architecture.py  --components components.yaml
  [FAIL] crossing_action_fraction: measured 0.6, rule <= 0.5
  MEASURED RESULT: this model DOES NOT DECOMPOSE under this partition.

architecture_reflexion.py --components components.yaml --code pipeline --map map.yaml
  architecture_scan = coherent          exit 0
```

**Confirmed.** And two measurements EV-01 did not make:

- **The word "decompose" appears ZERO times in the reflexion text output.** So
  do `crossing_action_fraction`, `modularity_q`, and `criteria`. A reader of the
  reflexion report cannot learn that the partition failed.
- **The reflexion JSON carries no decomposition signal at all.** Top-level keys
  are `absences, advisory, basis, blind_spots, code_root, convergences,
  divergences, ignored_suppression_keys, language, map, measured, schema,
  schema_version, unmapped_modules, unrealized_components, verdict`. There is no
  `criteria`, no `decomposes`, no `modularity_q`. `blind_spots` is `[]`. **A
  machine consumer has no field to check.**

The mechanism, at `scripts/analyze_architecture.py:500`:

```python
@property
def consumable_as_architecture(self) -> bool:
    return self.partition_source == "declared" or self.decomposes
```

and `scripts/architecture_reflexion.py:836` gates on that property and nothing
else. **Declaring a partition is sufficient. The criteria table stands between
nobody and nothing on this path.**

## 2. THE SHARPER FINDING — the fully degenerate case is NOT caught

**EV-02-DF-01, new, and higher severity than DF-02.**

`PREDICTIONS.md` DP-2 predicted: *"the shipped `unfalsifiable_coherence` refusal
catches the fully degenerate case (verified on `ex6_jenga`: all 3 pairs ported,
`divergence_detectable = false`, verdict `unmappable`, NOT `coherent`)."*

Measured on **ex5, the divergent twin**, with a declared **one-component**
partition (`theapp`, all six variables) and the whole tree mapped to it:

```
architecture_scan = coherent          exit 0
divergences 0   absences 0   convergences 0
divergence_detectable: false
blind_spots: []
component_pairs: 0        internal_edges: 7 of 7
```

Four real divergences and one real absence, all reported clean. The report even
prints, in the same output:

> A code edge can only diverge across a pair in the second list. When that list
> is empty the architecture permits every pair and a clean result is true by
> construction.

— and then prints `coherent` anyway. The guard, at
`scripts/architecture_reflexion.py:921`:

```python
if not report.unported_pairs and len(names) >= 2:
    report.blind_spots.append(BlindSpot(kind="unfalsifiable_coherence", ...))
```

**`len(names) >= 2` excludes the one case the guard exists for.** `ex6_jenga`
(3 components, all pairs ported) IS caught. One blob is not. `divergence_
detectable` is computed as `False` and **no consumer reads it** — it is reported
in JSON and does not participate in the verdict.

**DP-2 is scored MISSED.** The refusal catches the *near*-degenerate case and
misses the *fully* degenerate one. **DP-2b is scored CONFIRMED**, and DF-02's
severity revised upward.

## 3. Blast radius, measured — how easily can a project obtain a false clean?

Method: enumerate **every set partition of ex5's six model variables** (Bell(6)
= **203**), derive the natural module map from variable ownership, and record
the descriptor's decomposition verdict and the reflexion verdict for each. The
fixture was never modified; generated YAML lived in scratch and was passed with
`--components`/`--map`. Machine-readable: `artifacts/blast.json`.

| outcome on a codebase with 4 real divergences + 1 real absence | count | share |
|---|---|---|
| `divergent` (correct) | 71 | 35.0% |
| `unmappable` (refused — 76 `unfalsifiable_coherence`, 52 `unrealized_component`) | 120 | 59.1% |
| **`coherent` (FALSE CLEAN)** | **12** | **5.9%** |

And the decisive cross-tabulation:

| | decomposes | does NOT decompose |
|---|---|---|
| **`coherent`** | **0** | **12** |
| `divergent` | 4 | 67 |
| `unmappable` | 8 | 112 |

**Every one of the 12 false cleans is a partition the descriptor itself
rejects. Not one honest partition produces a clean on this codebase.** The
decomposition criteria are a *perfect* discriminator here — and the reflexion
check does not consult them.

Cheapest false cleans found, by authoring cost:

- **1 component, whole tree mapped to it.** Fails `component_count` and
  `modularity_q`. ~6 lines of YAML. `coherent`, `blind_spots: []`.
- **3 components failing only `crossing_action_fraction`** — e.g.
  `[accepted, inbox] / [delivered, failed] / [ledger, queue]`. This one looks
  entirely plausible to a reviewer: three named components, two of them the
  project's real ones, and it reports `coherent` on a codebase with four
  divergences. `blind_spots: []`.

Restated as risk: **a project that declares its partition without reading
`analyze architecture` has a ~6% chance of a false clean by accident on this
model, and a 100% chance if it tries.**

## 4. Does anything downstream inherit the false clean?

Traced every consumer of the reflexion verdict in the shipped surface.

| consumer | inherits the false clean? | why |
|---|---|---|
| **`architecture_reflexion` text + JSON (AC-02)** | **YES, completely** | `coherent`, `blocks_promotion: false`, `blind_spots: []`, no decomposition field to check |
| **`architecture_delta` (AC-04, `--baseline`)** | **NO** | verified against the maximal gaming move: honest ex5 scan as baseline vs the one-component scan. Reports `direction = unattributable`, names all 8 re-placed modules, classifies each lost edge `endpoint_reassigned` ("the edge did not go away; the boundary it crossed did"), and reports **stable basis 0 → 0 (+0)**. **DP-7 PASS, robustly.** |
| **complexity ledger (`architecture_delta` member)** | **NO — and it never sees the verdict either** | the ledger reads the *delta report*, not the reflexion verdict. `architecture_scan` appears nowhere in `scripts/complexity_ledger.py`. A false `coherent` never enters the ledger, and neither does a true one. |
| **implementation brief (AC-03)** | **NO** | `prompts/implementation_brief.md` documents *this exact defect by name* and adds Gate B: `V1` **refuses** on a 1-component declared partition, `V3` **degrades** on `crossing_action_fraction > 0.5`, and `FULL` confidence requires all three criteria met. |
| **promotion / close / case generation** | **NO** | `architecture_scan` is recorded by the model and guarded by nothing. **AC-P6 holds**; the false clean blocks nothing because nothing blocks. |

### The finding that falls out of that table

**The mitigation for DF-02 already exists, is precisely correct, and lives in
the wrong place.** `prompts/implementation_brief.md` says, verbatim:

> `consumable_as_architecture` is `true` for *any* declared partition, including
> one that fails every decomposition criterion … That is correct for AC-02,
> whose question is "did the project name a boundary to compare code against".
> It is **not** sufficient for you…

AC-03 is a **prompt** — a discipline an agent may or may not follow. AC-02 is a
**program**. The check that a human must remember is enforced; the check a
program could enforce is not. Gate B's `V1`/`V3` tests are computable from data
`architecture_reflexion.py` already holds. **EV-02-DF-01, filed not fixed.**

### The honest bound on the blast radius

The blast radius is **narrow in consequence and wide in record**. Nothing
blocks, so no work is refused on a lie and no gate is passed on a lie. But
`coherent` is what a project reports, records in evidence, and puts in a PR
body — and on this path it can be obtained on a codebase with four real
divergences, from a partition the toolchain itself rejects, with no blind spot,
no caveat, and exit 0.

## Artifacts

`artifacts/blast.json` (all 203 partitions, machine-readable),
`artifacts/ex5_one_component.txt` / `.json` (the DF-06 false clean),
`artifacts/ex5_one_component_delta.txt` (AC-04 refusing it),
`artifacts/one_components.yaml` / `one_map.yaml` (the ~6 lines it takes).
The enumerator is `../ex4-run1/artifacts/df02_blast.py`.
