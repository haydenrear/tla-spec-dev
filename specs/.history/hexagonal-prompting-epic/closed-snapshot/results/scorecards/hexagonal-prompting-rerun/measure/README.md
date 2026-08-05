# The instruments — EVAL-RERUN

Everything here is a re-anchoring or a binding for THIS round. The oracle, the
driver, the aspect slices, the effect-provider mappings and the generated effect
package are the SHIPPED ones and are not copied:

| what | where | changed this round? |
|---|---|---|
| the driver | `examples/validation/ab/eval/run_controls.py` | no |
| the oracle | `examples/validation/ab/eval/oracle.py` | no |
| reality witnesses | `examples/validation/ab/eval/witnesses.py` | no |
| the sealed catalogue | `examples/validation/ab/seeded_faults.toml` | no — **sealed, not amended** |
| the stable control record | `examples/validation/ab/eval/controls.toml` | no |
| aspect slices, mappings, effect codegen | `specs/results/scorecards/hexagonal-prompting/measure/` | no |
| the two arm bindings | here | **new — one per arm** |
| the two re-anchored catalogues | here | **new — one per arm** |
| the two arm control records | here | **new — one per arm** |

## Files

| file | what it is |
|---|---|
| `rerun_arm_a_binding.py`, `rerun_arm_b_binding.py` | how the shared oracle installs a model before-state into each tree. **A binding is not blind**: whoever writes one has read the code. The judges are blind; this is not. |
| `catalogue_arm_a.toml`, `catalogue_arm_b.toml` | the ten sealed mutants re-anchored, each carrying `seeded_by` |
| `controls_arm_a.toml`, `controls_arm_b.toml` | M07's scope, M09's retirement, and N01 with its reality witness |
| `catalogue-integrity-arm-{a,b}.txt` | the shipped harness's output, both **EXIT 0** |

## The one deliberate difference from `reference_binding.py`

Both arm bindings look the tree up on **every call** rather than holding a
module reference from import time. `run_controls.py` purges `quota_ledger*` and
a **fixed list** of binding module names between mutants; these bindings are not
on that list and that list lives in a file this measurement may not edit.

Holding the reference produced **EVAL-RERUN-DF-01**: every mutant executed
against the pristine tree and reported SURVIVED, with green controls. The broken
run is published as
`../GOAL-catch-bugs/kill-table-arm-a-STALE-BINDING-DF-01.json`. It was caught by
the hand-written `suite` column of the same table disagreeing with all six
generated columns.

## The two `seeded_by = "addition"` rows, and why they exist

Arm B derives `available` and stores no reservations-side quantity, so M08 and
M10 — both faults in maintaining a redundant stored count — have no one-token
form in it. HP-06 dropped them from arm B's catalogue and reported a denominator
of 8, then had to disown the number in its own run record. Its blind-author
channel proved the faults are seedable by *adding* a statement and that both
die.

This round seeds all ten on both arms and records **how** the diff had to be
written. The asymmetry is in seedability, not killability, and a kill-count
table cannot show it — which is the entire argument for the column.

## The M07 substitution on arm B, declared

Arm A's M07 inflates a stored deduction inside `reserve` (faithful to the sealed
catalogue). Arm B has nothing stored to deduct, so its M07 inflates the
*computation* of the held total: same class, same blatancy, **wider reach** — it
is observable after any command, including a refusal, and is present from
construction. HP-06 made the identical substitution and the identical
disclosure.

Consequence, and it is the single cell on which the two arms' tables differ:
arm A declares a verified limitation for M07 under `corpus-neg` (the negative
corpus executes 64 `Reserve` cases, **0 of them accepting**) and arm B does not,
because on arm B the limitation would be false. **M07's arm-A and arm-B cells
are not the same experiment and must not be differenced.**
