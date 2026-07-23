# Decompose This Repository By Dogfooding The Finished Toolchain

Status: Open

Scheduled **last** in the epic (promotion_order 85), after every mechanism
ticket has landed.

This repository has carried the same known gap since the epic began: its own
baseline is a single `TlaSpecDevCli.tla` module, without the Internal/External
view split that `SKILL.md` mandates for every project it onboards. The tool
does not yet meet its own standard.

## The point of this ticket

Do the decomposition **by running the finished toolchain on this repository**,
not by hand.

Every mechanism the epic built gets exercised end-to-end against a real target
for the first time:

| Mechanism | Ticket | Role here |
|---|---|---|
| `analyze complexity` | MF-011 | proposes the cut from the R/W matrix and modularity score |
| budgets block | MF-012 | supplies the gates the cut is measured against |
| corpus distillation | MF-014 | produces the case corpus for the decomposed views |
| effect conformance | MF-013 | validates side-effect contracts at the new ports |
| External channel enforcement | MF-015 | checks channel-authentic bindings |
| mutation kill test | MF-016 | proves the decomposed models are not shrunk past usefulness |
| complexity ledger + refinement loop | MF-019 | records the delta and searches for further reduction |

The decomposition is the deliverable. **The dogfooding is the acceptance test
of the entire epic.**

## The finding outranks the migration

Where a tool proves inadequate, awkward, or wrong when pointed at its own
repository, **that finding is worth more than a completed migration**. Record
it with evidence. Do not work around it by hand and report success — a hand
migration that hides a broken tool is the worst possible outcome here, because
it produces a clean result that conceals exactly what this ticket exists to
discover.

If `analyze complexity` proposes a cut that is obviously wrong, say so. If the
kill test cannot run against a decomposed view, say so. If corpus distillation
produces a useless corpus at the ports, say so. Those are the highest-value
outputs available from this work.

## Motivating trigger

MF-011's component-size heuristics fail on the undecomposed model — `C1 is
touched by 11 actions, exceeding max_component_actions 8`. That is a **true
finding**, not a miscalibration: the component budgets presuppose a decomposed
model with contract environments at the ports, which this repository does not
yet have. This ticket resolves it at the root rather than by renegotiating the
budget.

## Acceptance criteria

- The cut is **proposed by `analyze complexity`** from the R/W matrix and
  modularity score, not chosen by hand. Record the command output that
  produced it. If you override the proposal, justify the override explicitly.
- `Core.tla` / `Internal.tla` / `External.tla` replace the single module, with
  every action and invariant mapped to a view and the mapping enumerated.
- The component-size heuristics **pass on the decomposed views without
  renegotiating `max_component_actions`**. If they do not, that is a finding
  about either the budget or the cut — report it rather than tuning it away.
- Reachable behavior is retained across the split, **proven** against the
  pre-split baseline rather than asserted. Establish that baseline first.
- Every mechanism in the table above is run against this repository and its
  output recorded as evidence.
- Every mechanism that proves inadequate on a real target is recorded as a
  first-class finding with evidence.
- The MF-019 refinement loop runs on the finished decomposition, with
  recommendations recorded for owner approval.
- The `specs/program_model/spec_manifest.yaml` desync recorded in the epic
  notes (it still names the booleans collapsed by MF-020 and MF-022) is
  reconciled as part of this work.

## Note

This is the largest ticket in the epic and the only one whose value is
primarily diagnostic. Budget time for writing findings up properly, not only
for making the migration land.
