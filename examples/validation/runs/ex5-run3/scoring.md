# ex5 run 3 — the 203-partition sweep, re-run against the repaired tree (RP-01)

Run date 2026-07-30, EV-03. **Mechanical run: no agent.** Round 2 of the eval,
scored against the SAME committed predictions in `../../PREDICTIONS.md`. The
enumeration and the module-map derivation are byte-for-byte the ones
`../ex4-run1/artifacts/df02_blast.py` used in round 1, so the 203 rows are
like-for-like; the round-2 harness
(`artifacts/df02_blast_round2.py`) only *adds* the fields RP-01 introduced.

Interpreter pinned for the whole ticket: `python3.13.14` in a uv venv carrying
`pytest` + `pyyaml` + `tomllib` (see run 4's note on EV-02-DF-05). The YAML
fallback parser and PyYAML were checked to produce byte-identical JSON on this
fixture before any number below was taken.

## Half 1 — the answer key, re-measured (AC-P1, AC-P2, AC-P3, AC-P6)

`artifacts/ex5_reflexion.txt`, and ex4's control at
`../ex4-run4/artifacts/ex4_reflexion.txt`.

| fact | key | round 1 | round 2 |
|---|---|---|---|
| `architecture_scan` (ex5) | `divergent` | `divergent` | **`divergent`** |
| divergences | 4 | 4 | **4**, same four `file:line` |
| absences | 1 | 1 | **1** (`P2 dispatch <-> ledger`) |
| exit code | 0 | 0 | **0** |
| `architecture_scan` (ex4, the coherent twin) | `coherent` | `coherent` | **`coherent`** |
| false positives on ex4 | 0 | 0 | **0** |
| precision / recall | 1.000 / 1.000 | 1.000 / 1.000 | **1.000 / 1.000** |

The four sites, unchanged: `pipeline/ingest/inbox.py:11` (import),
`pipeline/ingest/inbox.py:39` (call), `pipeline/ingest/queue.py:12` (import),
`pipeline/ledger/journal.py:55` (function-local import).

**AC-P1, AC-P2, AC-P3, AC-P6 PASS**, exactly as in round 1. RP-01 changed the
verdict rule and **cost nothing on the honest path**: the coherent twin still
earns its `coherent`, and it now says on what basis
(`partition decomposes: yes`, `divergence_detectable: true`, `a clean result is
SUPPORTABLE on this basis`).

`check_twins.py` exit 0 before and after. **X-P4 PASS.**

## Half 2 — the sweep. RP-01's headline, measured rather than assumed

All 203 set partitions of ex5's six model variables, each with the natural
module map, on a codebase carrying 4 real divergences and 1 real absence.

| outcome | round 1 | round 2 | delta |
|---|---|---|---|
| **`coherent` (FALSE CLEAN)** | **12** (5.9%) | **0** | **−12** |
| `coherent` (honest) | 0 | 0 | 0 |
| `divergent` | 71 (35.0%) | **91** (44.8%) | **+20** |
| `unmappable` | 120 (59.1%) | 112 (55.2%) | −8 |
| exit 0 | 203/203 | **203/203** | 0 |

**Zero partitions produce a clean the criteria do not support.** RP-01's
acceptance assertion is MET, measured on the same instrument that found the
defect.

### The transition matrix — nothing regressed

| round 1 → round 2 | count |
|---|---|
| `unmappable` → `unmappable` | 100 |
| `divergent` → `divergent` | **71** |
| `unmappable` → `divergent` | **20** |
| `coherent` → `unmappable` | **12** |

**Not one divergence verdict was lost.** All 71 of round 1's `divergent`
verdicts are still `divergent`, and 20 partitions that round 1 refused now
report their findings instead.

All 12 of round 1's false cleans are now `unmappable`, each carrying
`partition_does_not_decompose` in `basis_limits`, and the one-component case
carries `unfalsifiable_coherence` as well.

### The 20 gained verdicts are the measured case for `basis_limits` ≠ `blind_spots`

Every one of the 20 newly-reported `divergent` partitions carries
`unfalsifiable_coherence` as a **basis limit**. Each had **1 absence** that
round 1 suppressed to `unmappable`. Filing the limit as a *withheld clean*
rather than as a *blind spot* is what let a real finding through.

The counterfactual RP-01 measured, **verified here independently**: of round 1's
71 `divergent` verdicts, **67 carry `partition_does_not_decompose` in round 2's
basis limits** — so had that limit been filed as a blind spot, 67 of 71 real
divergence verdicts would have been suppressed to `unmappable` to remove the
same 12 false cleans. RP-01's number reproduces exactly.

Of round 2's 91 `divergent` verdicts, **87 carry at least one basis limit and 4
carry none** — the 4 honest partitions.

### The sharpest single case: the one-component false clean

`artifacts/ex5_one_component.txt`, the ~6 lines of YAML that were round 1's
headline (`artifacts/one_components.yaml`, `one_map.yaml` — the round-1 files,
unmodified):

| | round 1 | round 2 |
|---|---|---|
| verdict | **`coherent`** | **`unmappable`** |
| `blind_spots` | `[]` | `[]` |
| `basis_limits` | *(field did not exist)* | `unfalsifiable_coherence`, `partition_does_not_decompose` |
| exit | 0 | **0** |
| divergences reported | 0 | 0 |

Both limits are printed in the text and carried in the JSON, and the verdict
block now states `a clean result is NOT SUPPORTABLE on this basis`. The report
also states in full sentences that the partition is *not refused*, the
comparison *ran*, and what is withheld is the word `coherent`.

**DP-2 was scored MISSED in round 1. It is scored CAUGHT in round 2**, and by
the mechanism NE-01(1) named: the `len(names) >= 2` clause is gone, so the
one-blob partition is the *strongest* case of `unfalsifiable_coherence` rather
than an exception to it.

**DP-2b was scored CONFIRMED in round 1 and is scored CLOSED in round 2** on
this measurement: a declared partition that fails all three criteria no longer
yields a real-looking `coherent`. NE-01(3) was honoured — the partition is not
refused, findings keep their `file:line`, exit stays 0.

## What this arm did NOT measure, stated so a silence is not a result

- The sweep is one fixture, one model, six variables, one map-derivation rule.
  "Zero false cleans on 203 partitions of ex5" is not "zero false cleans."
- The sweep varies the **partition**. It does not vary the **map** independently
  of the partition, and the map is the other editable declaration. A map that
  places a module in a component it does not belong to is still a way to move a
  boundary, and this arm does not enumerate that space.
- Everything here is still **static import topology** (NE-02, untouched by any
  repair in this epic).

## Filed this run

**EV-03-DF-01** — the AC-02 dogfood conclusion is now false and is still on
record. AC-02's ticket note says this repository is "falsifiable-and-clean
under a four-component one". Measured on the repaired tree with this
repository's own declared partition (`artifacts/../../ex6-run2/artifacts/realjenga_declared.txt`):
`modularity_q = −0.025485` (rule `> 0`), `crossing_action_fraction = 0.6` (rule
`<= 0.5`), verdict `unmappable`, `partition_does_not_decompose`. RP-01 recorded
this; nothing has corrected the AC-02 note in `ticket_plan.yaml`, and a reader
of the plan still finds the retracted claim. Documentation defect, filed not
fixed.

## Artifacts

`artifacts/blast.json` (all 203 rows with the round-2 fields),
`artifacts/blast-summary.txt` (the harness's own summary),
`artifacts/df02_blast_round2.py` (the harness),
`artifacts/ex5_reflexion.txt` (the re-measured answer key),
`artifacts/ex5_one_component.txt` / `.json` (round 1's headline false clean, now
refused), `artifacts/one_components.yaml` / `one_map.yaml` (the six lines, as
round 1 wrote them).
