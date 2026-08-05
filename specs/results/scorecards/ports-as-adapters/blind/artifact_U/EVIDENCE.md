# Evidence packet — artifact U

This packet is measured evidence about **artifact U only**, except the
mechanical block, which covers all three artifacts because the scorecard's D2
anchor 3 reads a before/after and one column cannot reach it.

## How to use this packet

**The mechanical block is recorded and NEVER scored** (`references/
eval_scorecard.md`, rule 7). It sits beside your judgement so that a reader can
see when the two disagree, and a disagreement is a finding rather than something
to resolve by arithmetic. Do not convert a figure into a score.

**Score artifacts, never claims.** The artifact's own `NOTES.md` is evidence
about what its author says, not about what the code does. If a claim in it
matters to a score, check it against the code or run it.

**A number under a RED control is a FLOOR.** Read the control section before
reading any kill number. A positive control that should have died on an
instrument and did not means that instrument's zeros cannot be told apart from a
broken instrument.

**A drop in a complexity number is not evidence on its own** (MF-020): a count
can fall because behaviour was deleted.


## What each instrument is

Every one of these is a set of executable cases run against this artifact with
exactly one seeded fault applied, then reverted. `KILLED` means at least one
case failed under the fault; `SURVIVED` means none did; `NOT_DECIDABLE` means a
declared limitation for that pair was verified against this run's own
executability counts and held, so the cell decides nothing.

| instrument | what it is |
|---|---|
| `corpus-whole` | every enabled edge of the model's state graph, replayed |
| `corpus-neg` | the DISABLED edges at each reachable state, each asserting a refusal plus inertness |
| `corpus-slice-res` | the same, projected onto the reservation aspect only |
| `corpus-slice-led` | the same, projected onto the ledger aspect only |
| `corpus-port` | cases generated PER DECLARED PORT rather than per action |
| `map-silent` | `corpus-whole` with an effect provider that records and asserts nothing about content |
| `map-checking` | `corpus-whole` with an effect provider that asserts durable content |
| `suite` | the shared hand-written behavioral suite, unchanged, the same for every artifact |
| `corpus-action-bound` | the port corpus bound to ACTIONS -- the pre-port-binding world |
| `corpus-port-swap:real` | the port corpus bound to the declared PORT, real implementation |
| `corpus-port-swap:fake` | the same cases, same binding, the port's FAKE implementation if one exists |

`corpus-port-swap:fake` on an artifact that ships no second implementation runs
its REAL one, and the runner says so on every such run. That is a fact about the
artifact, not a limitation of the instrument.

Every corpus here is generated from ONE model and ONE manifest shared by all
three artifacts. No artifact's corpus differs from another's by a byte, and the
`cases.py` sha1 is recorded below. So a difference between artifacts in this
table is a difference in the CODE, never in the cases.


## Shared behavioral suite

`examples/validation/ab/tests/test_behavior.py`, unchanged, the same file for
every artifact: **28 passed**, on unmutated code.

## Per-mutant, per-instrument kill table

Eleven seeded faults, each applied exactly once to a copy of this artifact,
proved to revert byte-identically, and reverted. Every cell is a measured run.

| mutant | class | seeded_by | corpus-whole | corpus-neg | corpus-slice-res | corpus-slice-led | corpus-port | map-silent | map-checking | suite |
|---|---|---|---|---|---|---|---|---|---|---|
| `M01-guard-zero-amount` |  | perturbation | SURVIVED | KILLED | SURVIVED | SURVIVED | KILLED | SURVIVED | SURVIVED | KILLED |
| `M02-guard-over-quota` |  | perturbation | SURVIVED | KILLED | SURVIVED | SURVIVED | KILLED | SURVIVED | SURVIVED | KILLED |
| `M03-guard-close-with-outstanding` |  | perturbation | SURVIVED | KILLED | SURVIVED | SURVIVED | KILLED | SURVIVED | SURVIVED | KILLED |
| `M04-durable-stale-total` |  | perturbation | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED | KILLED |
| `M05-durable-close-line-zero-and-swallowed` |  | perturbation | KILLED | SURVIVED | SURVIVED | SURVIVED | KILLED | KILLED | KILLED | KILLED |
| `M06-wrong-status-on-release` |  | perturbation | KILLED | SURVIVED | KILLED | SURVIVED | SURVIVED | KILLED | KILLED | KILLED |
| `M07-positive-control-wrong-hold` |  | perturbation | KILLED | NOT_DECIDABLE | KILLED | NOT_DECIDABLE | SURVIVED | KILLED | KILLED | KILLED |
| `M08-cross-aspect-commit-refunds-the-hold` |  | perturbation | KILLED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED | KILLED | KILLED |
| `M09-negative-control-ledger-order` |  | perturbation | KILLED | SURVIVED | SURVIVED | KILLED | KILLED | KILLED | KILLED | KILLED |
| `M10-apply-only-double-refund` |  | perturbation | KILLED | SURVIVED | KILLED | SURVIVED | SURVIVED | KILLED | KILLED | KILLED |
| `N01-negative-control-outstanding-id-order` |  | ? | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED |

`seeded_by` is a fact about the DIFF, not about the artifact's quality:
`perturbation` = an existing statement changed; `addition` = a statement
invented and inserted, because the fault has no one-token form in this design.

### Per class

```
{
  "cross_aspect": {
    "corpus-neg": "0 of 1",
    "corpus-port": "0 of 1",
    "corpus-slice-led": "0 of 1",
    "corpus-slice-res": "0 of 1",
    "corpus-whole": "1 of 1",
    "map-checking": "1 of 1",
    "map-silent": "1 of 1",
    "suite": "1 of 1"
  },
  "durable_content": {
    "corpus-neg": "0 of 2",
    "corpus-port": "1 of 2",
    "corpus-slice-led": "0 of 2",
    "corpus-slice-res": "0 of 2",
    "corpus-whole": "1 of 2",
    "map-checking": "2 of 2",
    "map-silent": "1 of 2",
    "suite": "2 of 2"
  },
  "guard_relaxation": {
    "corpus-neg": "3 of 3",
    "corpus-port": "3 of 3",
    "corpus-slice-led": "0 of 3",
    "corpus-slice-res": "0 of 3",
    "corpus-whole": "0 of 3",
    "map-checking": "0 of 3",
    "map-silent": "0 of 3",
    "suite": "3 of 3"
  },
  "ordering": {
    "corpus-neg": "0 of 2",
    "corpus-port": "1 of 2",
    "corpus-slice-led": "1 of 2",
    "corpus-slice-res": "0 of 2",
    "corpus-whole": "1 of 2",
    "map-checking": "1 of 2",
    "map-silent": "1 of 2",
    "suite": "1 of 2"
  },
  "output_oracle": {
    "corpus-neg": "0 of 1",
    "corpus-port": "0 of 1",
    "corpus-slice-led": "0 of 1",
    "corpus-slice-res": "1 of 1",
    "corpus-whole": "1 of 1",
    "map-checking": "1 of 1",
    "map-silent": "1 of 1",
    "suite": "1 of 1"
  },
  "wrong_value": {
    "corpus-neg": "0 of 1 (1 not decidable)",
    "corpus-port": "0 of 2",
    "corpus-slice-led": "0 of 1 (1 not decidable)",
    "corpus-slice-res": "2 of 2",
    "corpus-whole": "2 of 2",
    "map-checking": "2 of 2",
    "map-silent": "2 of 2",
    "suite": "2 of 2"
  }
}
```

## The port-binding columns

The same generated port corpus, bound three ways.

| mutant | corpus-action-bound | corpus-port-swap:fake | corpus-port-swap:real |
|---|---|---|---|
| `M01-guard-zero-amount` | KILLED | KILLED | KILLED |
| `M02-guard-over-quota` | KILLED | KILLED | KILLED |
| `M03-guard-close-with-outstanding` | KILLED | KILLED | KILLED |
| `M04-durable-stale-total` | SURVIVED | SURVIVED | SURVIVED |
| `M05-durable-close-line-zero-and-swallowed` | KILLED | KILLED | KILLED |
| `M06-wrong-status-on-release` | SURVIVED | SURVIVED | SURVIVED |
| `M07-positive-control-wrong-hold` | SURVIVED | SURVIVED | SURVIVED |
| `M08-cross-aspect-commit-refunds-the-hold` | SURVIVED | SURVIVED | SURVIVED |
| `M09-negative-control-ledger-order` | KILLED | KILLED | KILLED |
| `M10-apply-only-double-refund` | SURVIVED | SURVIVED | SURVIVED |
| `N01-negative-control-outstanding-id-order` | SURVIVED | SURVIVED | SURVIVED |

## Executability, beside every kill number

From this run's own control pass on **unmutated** code. A zero from an
instrument that executed nothing is not the same claim as a zero from one that
executed 294 accepting `Reserve` cases.

| instrument | cases | executed | skipped | failed on unmutated code | accepting `Reserve` executed |
|---|---|---|---|---|---|
| `corpus-whole` | 43128 | 3734 | 39394 | 0 | 294 |
| `corpus-neg` | 118 | 94 | 24 | 0 | 0 |
| `corpus-slice-res` | 2438 | 320 | 2118 | 0 | 100 |
| `corpus-slice-led` | 56 | 10 | 46 | 0 | - |
| `corpus-port` | 1855 | 1543 | 312 | 0 | 294 |
| `map-silent` | 43128 | 3734 | 39394 | 0 | 294 |
| `map-checking` | 43128 | 3734 | 39394 | 0 | 294 |
| `suite` | - | - | - | 0 | - |

Generated corpus `cases.py` sha1 (the port corpus, identical for all three
artifacts): `08265aff0d81f27f4dfc9694d2a69c3c5b6e695c`.

## CONTROL STATUS — read this before any kill number

```
{
  "M07-positive-control-wrong-hold": {
    "green": false,
    "instruments_decided": [
      "corpus-port",
      "corpus-slice-res",
      "corpus-whole",
      "map-checking",
      "map-silent",
      "suite"
    ],
    "instruments_not_decidable": [
      "corpus-neg",
      "corpus-slice-led"
    ],
    "instruments_wrong": [
      "corpus-port"
    ],
    "must_be": "KILLED",
    "role": "positive"
  },
  "M09-negative-control-ledger-order": {
    "decides_nothing": true,
    "green": true,
    "measured_cells": {
      "corpus-neg": "SURVIVED",
      "corpus-port": "KILLED",
      "corpus-slice-led": "KILLED",
      "corpus-slice-res": "SURVIVED",
      "corpus-whole": "KILLED",
      "map-checking": "KILLED",
      "map-silent": "KILLED",
      "suite": "KILLED"
    },
    "replaced_by": "N01-negative-control-outstanding-id-order",
    "retirement_reason": "Retired for the reason given in full in examples/validation/ab/eval/controls.toml:\nM09 reverses a SEQUENCE and this model represents its ledger as one\n(`ledger' = Append(ledger, ...)`, projected as a tuple and compared\npositionally), so ordering is expressible and the corpus sees it. The retirement\nis a property of the MODEL, so it holds on every tree measured against that\nmodel. M09 is not deleted, not re-seeded and not excused: it still runs and is\nstill scored in the `ordering` class row. What it stops doing is deciding\nwhether the instrument works.",
    "role": "negative (RETIRED)"
  },
  "N01-negative-control-outstanding-id-order": {
    "green": true,
    "instruments_decided": [
      "corpus-neg",
      "corpus-port",
      "corpus-slice-led",
      "corpus-slice-res",
      "corpus-whole",
      "map-checking",
      "map-silent",
      "suite"
    ],
    "instruments_not_decidable": [],
    "instruments_wrong": [],
    "must_be": "SURVIVED",
    "reality_witness": {
      "on_mutated_tree": true,
      "on_pristine_tree": false,
      "separates_the_trees": true,
      "spec": "witnesses:outstanding_ids_not_ascending"
    },
    "role": "negative"
  }
}
```

```
control coverage: {"negative": {"deciding": ["N01-negative-control-outstanding-id-order"], "declared": ["M09-negative-control-ledger-order", "N01-negative-control-outstanding-id-order"], "green": true}, "positive": {"deciding": [], "declared": ["M07-positive-control-wrong-hold"], "green": false}}
polarities with no deciding control: []
limitations rejected by this run's own evidence: []
```

Port-binding columns, control roles executed against this run's measured counts:

```
[
  {
    "instrument": "corpus-action-bound",
    "must_be": "KILLED",
    "mutant": "M07-positive-control-wrong-hold",
    "observed_cell": "SURVIVED",
    "role": "positive",
    "why": "declared positive control; this instrument executed 294 accepting Reserve case(s) and the cell is SURVIVED, not KILLED",
    "witness_action": "Reserve",
    "witness_basis": "measured",
    "witness_ran_accepting": 294
  },
  {
    "instrument": "corpus-port-swap:fake",
    "must_be": "KILLED",
    "mutant": "M07-positive-control-wrong-hold",
    "observed_cell": "SURVIVED",
    "role": "positive",
    "why": "declared positive control; this instrument executed 294 accepting Reserve case(s) and the cell is SURVIVED, not KILLED",
    "witness_action": "Reserve",
    "witness_basis": "measured",
    "witness_ran_accepting": 294
  },
  {
    "instrument": "corpus-port-swap:real",
    "must_be": "KILLED",
    "mutant": "M07-positive-control-wrong-hold",
    "observed_cell": "SURVIVED",
    "role": "positive",
    "why": "declared positive control; this instrument executed 294 accepting Reserve case(s) and the cell is SURVIVED, not KILLED",
    "witness_action": "Reserve",
    "witness_basis": "measured",
    "witness_ran_accepting": 294
  }
]
```

## MECHANICAL BLOCK — recorded, never scored

Complexity of produced code, `role=code` only (implementation modules; test
modules excluded), over all three artifacts.

| figure | artifact T | artifact U | artifact W |
|---|---|---|---|
| `modules` | 4 | 1 | 1 |
| `code_lines` | 202 | 151 | 78 |
| `callables` | 23 | 17 | 11 |
| `classes` | 6 | 4 | 2 |
| `public_surface` | 25 | 20 | 11 |
| `instance_state` | 8 | 8 | 7 |
| `module_state` | 0 | 0 | 0 |
| `branch_points` | 11 | 10 | 10 |
| `max_branch_points_in_callable` | 4 | 4 | 4 |
| `max_depth` | 1 | 1 | 1 |
| `declared_interfaces` | 1 | 0 | 0 |
| `declared_interface_methods` | 2 | 0 | 0 |
| `internal_import_edges` | 3 | 0 | 0 |
| `effectful_calls` | 3 | 5 | 3 |
| `modules_with_effectful_calls` | 1 | 1 | 1 |
| `branch_points_in_effectful_modules` | 1 | 10 | 10 |
| `instance_state_in_effectful_modules` | 1 | 8 | 7 |

Definitions are the instrument's own and are printed by
`python3 scripts/code_complexity.py <target>`. `effectful_calls` UNDERCOUNTS by
construction: 18 sink names are left out of the vocabulary for colliding with
in-memory operations, and the instrument says so on every run.

**This block is not a score and must not be converted into one.**
