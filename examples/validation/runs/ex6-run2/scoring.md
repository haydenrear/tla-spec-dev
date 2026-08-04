# ex6 run 2 — the refusals, re-measured against the repaired tree

Run date 2026-07-30, EV-03. **Mechanical run: no agent.** Scored against the
same predictions (AC-P4, AC-P5, AC-P6, DP-2, DP-2b). RP-01 rewrote the verdict
rule; this arm exists to check that it did not break the refusals it was built
on top of.

## AC-P4 — `ex6_jenga`, the synthetic control: **PASS**, and now it says more

```
architecture_scan = unmappable          exit 0
convergences 7   divergences 0   absences 0
```

Round 1 reported one reason. Round 2 reports two, both as **basis limits**:

- `unfalsifiable_coherence` — every one of the 3 component pairs has a port, so
  no code edge could have been a divergence (round 1's reason, verbatim);
- `partition_does_not_decompose` — the declared partition fails 2 of 3 criteria
  (`modularity_q = −0.1856`, `crossing_action_fraction = 0.8`). **Round 1's
  report did not contain this fact at all** — `../ex5-run2/scoring.md` measured
  that the word "decompose" appeared zero times in the reflexion output and that
  the JSON had no field for it.

The verdict block now states `partition decomposes: NO — fails modularity_q,
crossing_action_fraction` and `a clean result is NOT SUPPORTABLE on this basis`.
`unmappable`, never `coherent`, and the 0 divergences are still explicitly not a
clean result.

## AC-P5 — the real Jenga (this repository's own model): **PASS**, unchanged

```
architecture_scan = unmappable          exit 0
source: EMERGENT
[FAIL] component_count:  measured 1,   rule >= 2
[FAIL] modularity_q:     measured 0.0, rule > 0
[OK  ] crossing_action_fraction: 0.0,  rule <= 0.5
MEASURED RESULT: this model DOES NOT DECOMPOSE under this partition.

Single-writer ownership:
  NOT MEASURABLE: ... Reporting zero violations here would be a clean result
  for a model with no architecture.
```

Every element of AC-P5 holds, identical to round 1.

## The asymmetry round 1 found is GONE

Round 1's finding, in `../ex6-run1/scoring.md`:

| path | one component, emergent | one component, DECLARED |
|---|---|---|
| `analyze architecture` (no code) | `unmappable` ✓ | `unmappable` ✓ |
| `architecture_reflexion` (with code), **round 1** | `unmappable` ✓ | **`coherent`** ✗ |
| `architecture_reflexion` (with code), **round 2** | `unmappable` ✓ | **`unmappable`** ✓ |

Round 1's sharpest sentence was: *"Declaring the same partition it already has,
and mapping `scripts/` to it, converts the epic's own headline refusal into a
clean."* Measured on the repaired tree (`../ex5-run3/artifacts/ex5_one_component.txt`
for the fixture; the repository's own declared partition below), it does not.

**DP-2 is re-scored CAUGHT** (round 1: MISSED). **DP-2b is re-scored CLOSED on
the measured path** (round 1: CONFIRMED). The mechanism is NE-01(1) and NE-01(2)
landed in the program: the `len(names) >= 2` clause is gone, and the
decomposition criteria travel with the verdict in both text and JSON.

## What re-scoring DP-2b does NOT mean

DP-2b was, in words, "a partition that fails all three criteria AND leaves one
pair unported reports a real-looking `coherent`, and no shipped mechanism flags
it." The **flagging** half is closed: the mechanism exists, it is a program and
not a prompt, and it fires on 191 of the 203 partitions in the sweep. What is
NOT closed:

- the reflexion check still measures **static import topology** (NE-02);
- **anything outside `--code` is still free** — the composition-root problem has
  no answer and nothing in this epic gave it one;
- the map is still declared and still editable, and the sweep varies the
  partition rather than the map.

`coherent` is now a claim the report qualifies. It is not a claim the report can
defend against a codebase that hides its coupling from a static import scan.

## The finding RP-01 recorded, verified here independently

This repository's OWN declared four-component partition
(`specs/program_model/architecture_components.yaml`) **does not decompose its
own model**: `modularity_q = −0.025485` (rule `> 0`),
`crossing_action_fraction = 0.6` (rule `<= 0.5`). Verdict `unmappable`, with
`partition_does_not_decompose` plus three `dynamic_import` blind spots, one
`first_party_outside_code_root`, and one `non_python_file`. Exit 0.

**So `coherent` is not a verdict this repository could earn today even with a
perfect extractor.** That contradicts the AC-02 ticket note in
`ticket_plan.yaml`, which still says this repository is
"falsifiable-and-clean under a four-component one". Filed as **EV-03-DF-01** in
`../ex5-run3/scoring.md`.

**AC-P6 PASS** — every command in this arm exits 0. Nothing in this epic refuses
a close, a promotion, or a case generation.

## Artifacts

`artifacts/ex6_reflexion.txt` (the synthetic control),
`artifacts/realjenga.txt` (`analyze architecture`, emergent, one component),
`artifacts/realjenga_declared.txt` (the reflexion check against this
repository's own declared partition and `scripts/`).
