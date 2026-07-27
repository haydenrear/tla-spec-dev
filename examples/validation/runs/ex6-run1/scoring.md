# ex6 run 1 — the refusals, scored against PREDICTIONS.md (AC-P4, AC-P5, DP-2, DP-2b)

Run date 2026-07-27, EV-02. **Mechanical run: no agent.** Both incoherent
targets measured: the synthetic control (`ex6_jenga`) and the primary one — this
repository's own model.

## AC-P4 — `ex6_jenga`, the synthetic control: **PASS**

```
architecture_scan = unmappable          exit 0
convergences 6   divergences 0   absences 0
blind spot: [unfalsifiable_coherence] every one of the 3 component pair(s) in
this architecture has a port, so no code edge could have been a divergence.
```

`unmappable`, never `coherent`, and its 0 divergences are explicitly **not** a
clean result. The output volunteers the reason and adds: *"there is no flag,
key, annotation, or environment variable that turns it into `coherent`."*

## AC-P5 — the real Jenga (`specs/program_model/TlaSpecDevCli.tla`): **PASS**

```
architecture_scan = unmappable          exit 0
[FAIL] component_count:  measured 1,   rule >= 2
[FAIL] modularity_q:     measured 0.0, rule > 0
[OK  ] crossing_action_fraction: 0.0,  rule <= 0.5
MEASURED RESULT: this model DOES NOT DECOMPOSE under this partition.

Single-writer ownership:
  NOT MEASURABLE: ... Reporting zero violations here would be a clean result
  for a model with no architecture.
```

One component, Q = 0.000, ownership **NOT MEASURABLE** rather than "zero
violations". Every element of AC-P5 holds. The toolchain's own model is a real,
unarguable instance of the shape this epic is about, and it refuses.

**AC-P6 PASS** — both exit 0. Nothing refuses a close, a promotion, or a case
generation.

## DP-2 — scored **MISSED**, and this is the finding of the run

DP-2 predicted the `unfalsifiable_coherence` refusal *"catches the fully
degenerate case"*, citing this fixture as the verification. The citation is
sound and the conclusion drawn from it is not.

`ex6_jenga` is **3 components with every pair ported** — degenerate by
saturation. The **fully** degenerate case is **1 component**, and the guard
excludes it by construction (`len(names) >= 2`, `architecture_reflexion.py:921`).
Measured on ex5 in `../ex5-run2/scoring.md`: a declared one-component partition
on a codebase with four real divergences reports **`coherent`, `blind_spots:
[]`**. Filed as **EV-02-DF-01**.

Note the asymmetry the two commands produce on the *same* one-blob shape:

| path | one component, emergent | one component, DECLARED |
|---|---|---|
| `analyze architecture` (no code) | `unmappable` ✓ | `unmappable` (always, by design) ✓ |
| `architecture_reflexion` (with code) | `unmappable` ✓ | **`coherent`** ✗ |

The real Jenga refuses only because its one component is **emergent**. Declaring
the same partition it already has, and mapping `scripts/` to it, converts the
epic's own headline refusal into a clean. That is the blast radius of DF-02
aimed at the repository that ships it.

## DP-2b — scored **CONFIRMED**

`consumable_as_architecture` is `true` for any declared partition including one
that fails all three criteria; ex6 measures `decomposes = false`,
`consumable = true`, comparison ran anyway. PREDICTIONS invited a better
outcome — *"if EV-02 finds a mechanism that does flag it, that is a better
outcome than the prediction"*. **One was found and it is not on this path:**
AC-03's Gate B (`prompts/implementation_brief.md`) refuses `V1` and degrades
`V3` on exactly these grounds. It is a prompt, not a program. See
`../ex5-run2/scoring.md` §4 and EV-02-DF-01.

## Artifacts

`artifacts/ex6_reflexion.txt`, `artifacts/realjenga.txt`.
