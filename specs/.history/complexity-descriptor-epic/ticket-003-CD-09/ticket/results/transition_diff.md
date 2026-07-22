# CD-09 -- transition-level diff of the advisory-faithful model delta (G2)

The red-flag doctrine (MF-020) demands that any generated-states drop at
constant distinct states be explained transition-by-transition. This delta is
NOT that pattern -- generated states rose 5,619,356 -> 6,209,780 and distinct
states rose 231,621 -> 283,805 at constant depth 25 -- but the plan requires
the transition-level diff for any real model delta, so here is every edge
class that changed and why each change is a re-representation of the shipped
program rather than a behavior addition or deletion.

## What changed in the model text

1. `RunSpecUnitTests(root, ticket, override)` -> `RunSpecUnitTests(root, ticket)`
   and the `\E override \in BOOLEAN` quantifier in `Next` removed.
2. The guard disjunction
   `complexity_gate = "pass" \/ (complexity_gate = "fail" /\ override)`
   removed outright -- no complexity read remains in the action.
3. Invariant `SpecUnitTestsRequireAnalyzedGate` removed (model + MC.cfg +
   MCsmall.cfg) with a tombstone comment.

## Edge classes removed

- **Duplicate parameter bindings, not edges.** For every state `s` with
  `complexity_gate = "pass"` where RunSpecUnitTests was enabled, TLC
  previously computed each successor TWICE -- once per `override` binding
  (both satisfied the guard; `override` was read nowhere else, so both
  bindings produced the identical successor state). For `complexity_gate =
  "fail"` states only the `override = TRUE` binding fired (one computation).
  Removing the parameter removes the duplicate COMPUTATION only: every
  state-graph edge `s -> s'` present before is present after. No transition
  is deleted. (This alone would have shown as a generated-states drop at
  constant distinct states -- the red-flag costume -- had the guard removal
  below not dominated it.)

## Edge classes added

- **RunSpecUnitTests from gate-unknown states.** In every reachable state
  with `complexity_gate = "unknown"`, an active ticket at
  TicketCurrentReady..TicketSpecUnitTestsPassed, and setup_phase >= 2,
  RunSpecUnitTests edges now exist where before there were none. This is the
  shipped behavior: `tla-spec-dev run spec-unit-tests` performs no complexity
  check (scripts/tla_spec_dev.py run_spec_unit_tests builds pytest and
  case-adapter commands unconditionally), and the generation-time scan is
  advisory, proceeding on fail with a warning and no flag
  (scripts/generate_cases_from_tlc_dump.py:866-882 in the audited numbering,
  `ensure_complexity_scan`).
- **Downstream states of those edges.** Tickets can now reach
  TicketSpecUnitTestsPassed and TicketClosed while `complexity_gate` remains
  "unknown", and every action reachable from such states contributes its
  normal edges there. These state combinations are exactly the ones the
  removed invariant declared unreachable -- their reachability (+52,184
  distinct states) is the TLC-checked proof that the removal was real, not
  cosmetic.

## Edge classes unchanged

- All 13 other actions' guards and updates are textually untouched; their
  edges over the previously-reachable state set are identical.
- Where `complexity_gate` is "pass" or "fail", RunSpecUnitTests's
  state-level enabledness is UNCHANGED (before: pass, or fail with the
  existential override available; after: no read at all -- same states
  enabled), so no previously-possible spec-unit behavior was lost.

## Accounting for the counts

- distinct: 231,621 -> 283,805 (+52,184) -- entirely the newly-honest
  gate-unknown states described above; no other domain or guard changed.
- generated: 5,619,356 -> 6,209,780. Net +590,424 = (new edges from and
  through gate-unknown states) minus (the removed duplicate override-binding
  computations at gate-pass states). Both components move the count in
  opposite directions; the addition dominates.
- depth: 25 -> 25 -- the longest command sequence is unchanged; the new
  states hang off existing prefixes.

## Verdict

Every removed computation is a duplicate binding of a retained edge; every
added edge represents shipped advisory behavior the old model wrongly
forbade. No deleted self-loop, no behavior deletion wearing a
re-representation costume. TLC green before (tlc_before.txt) and after
(tlc_current.txt) on the surviving invariant set.
