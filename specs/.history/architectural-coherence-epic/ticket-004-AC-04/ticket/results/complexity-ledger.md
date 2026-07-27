# AC-04 — complexity ledger narrative

## What this ticket did to the model: nothing

Zero TLA+ delta, as the plan expects. `specs/tickets/AC-04/current` and
`.../desired` are byte-identical and both are identical to `specs/current` for
`TlaSpecDevCli.tla`, `MC.cfg` and `spec_manifest.yaml`
(`results/zero-model-delta.txt`, `results/model-delta.txt`). Measured:
variables 10, actions 16, bound 2,799,360, modularity 0.0 — the same figures
AC-03 recorded. TLC green at 32,122,220 generated / 1,292,951 distinct / depth 26
in 59s (`results/tlc-current.txt`), matching AC-01's and AC-03's runs exactly.

The delta direction is therefore `zero`. `distinct_states`, `generated_states`
and `depth` move from `null` to measured because AC-03 recorded no TLC report and
this ticket does; that is a first measurement, not a reduction, and the ledger
treats a null-to-int transition as no direction at all.

## What this ticket added: the structure half of the ledger

The complexity delta answers *is the representation smaller*. It cannot see a
change that lowers the state-space bound by scattering a responsibility across
three more modules — every CD-09 member stays green through that. The new
`architecture_delta` member answers *did the code move toward or away from the
boundaries the model draws*, and is recorded beside the complexity delta at every
close.

It **gates nothing**. A ticket that raised structural divergence records it and
closes. The reasoning is the same one that made complexity advisory in the first
place: a structural finding that could refuse a close would be answered by not
running the scan, and then nothing is recorded at all.

Three things are mechanical rather than declared, and each is there because the
alternative is a number that flatters whoever produced it:

1. **The direction is derived, not typed.** The ledger opens the report file
   produced by `analyze architecture … --baseline` and reads the direction out of
   it. The only field an author writes is `claim:`, and the only refusal in this
   member is a claim the measurement contradicts.
2. **A drop the edges do not explain is `unverified`.** MF-020 applied to
   structure. Each disappeared dependency is classified — `dependency_removed`,
   `endpoint_left_tree`, `endpoint_unmapped`, `endpoint_reassigned` — and a count
   that fell because a module stopped being *looked at* is never reported as an
   improvement. The rule is enforced twice, in the delta and again in
   `parse_architecture_delta`, so a report produced elsewhere or edited afterwards
   cannot smuggle one in.
3. **The map's identity is part of the result.** Both scans record a digest of
   the declared placements and of the component/port structure, both digests land
   in the ledger entry, and a comparison whose basis moved reports
   `unattributable`. Measured on this repository: re-placing `scripts/budgets.py`
   from `surface` to `kill` moves the divergence count 0 → 6 with no code change
   (`results/gaming-probe.txt`).

## This ticket's own delta

`code_only` attribution, identical map and model digests, divergences 0 → 0,
convergences 93 → 95 with both gained dependencies enumerated at `file:line`
(`complexity_ledger.py` → `spec_paths.py`, import and call). The change added
coupling and the coupling it added has a declared port. Recorded, not claimed:
`claim:` is left empty, because the honest direction is `unchanged` and there is
nothing to assert. Full reading in `results/refactor-loop.md`, including what the
demonstration does **not** show.

## Refinement search: searched, found none

Looked for a representation of this ticket's capability that costs the model
less. There is nothing to cost: the delta is computed by a scanner over the
source tree and the ledger, and the model already carries `architecture_scan`
from AC-01. Adding an action for "compare two scans" would grow the state space
to represent a step no user of the CLI can observe as a state change — the
transcription failure mode the standing objective exists to avoid. Considered and
rejected: representing the delta direction as a fifth value of `architecture_scan`
(it is a fact about a *pair* of scans, not about the program's state, and folding
it in would make `architecture_scan` mean two different things).

## CM-01-DF-03, deliberately not fixed here

`_budget_utilization` in this file compares a possibly-partial state-space bound
against the cap as if it were complete (CM-01 recorded `bound = 4`,
`within_cap: true`, for a model TLC measures at 49,386 states). It sits in a file
that is this ticket's key, and it is still **left alone**, for three reasons:

- It is not implied by this ticket's desired model. AC-04's delta is a structure
  measurement; the bound's completeness is a property of the domain resolver in
  `scripts/analyze_complexity.py`, which is not this ticket's slice.
- The fix is not local. Making `within_cap` honest requires the bound to publish
  whether every variable domain resolved — a change to the complexity descriptor's
  contract, with its own tests and its own ledger consequences.
- It does not manifest on this ticket's model, so fixing it here would be
  unverifiable from this close: bound 2,799,360 is fully resolved, and
  `within_cap` is correctly `false` at 279.9% of the cap.

It stays as filed. This ticket adds no new deferred finding.

## Fuzzing-era retention members

`not_run`, honestly. No kill test, no effect-conformance run, no external
coverage sweep was performed for this ticket. Per the 2026-07-21 pivot they are
experimental and non-gating, and MF-038 (0 of 9 content bugs, kill rate 0.31)
is why a `not_run` here costs nothing: an oracle not validated to catch bugs
could not have licensed anything anyway. The oracles that **are** load-bearing
for this ticket's behavior-preservation claim — TLC before/after, the repository
behavior tests, and content-asserting effect providers where a corpus is replayed
(`ex1-run4`: 45 points killed on the exact MF-038 class) — are recorded in
`validated_refactor` with their evidence paths.

## Coverage audit

`not_run`. It is an end-of-epic step; this is a ticket close.
