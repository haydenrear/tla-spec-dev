# OrderHub complexity decision (2026-07-21)

Input: `validation_artifacts/descriptor_before.txt` (`analyze complexity` on
`specs/program_model/OrderHub.tla` + `OrderHub.cfg` + `spec_manifest.yaml`),
read with `references/complexity_intuition.md`.

## What the before-descriptor said

- **Bound 8,388,608**, exceeding the 1,000,000 advisory budget. Dominant
  dimensions: `auditLog` 0..63 (64), `retries` 0..31 (32), `orders`/`shipped`
  0..15 (16 each), `mode` 0..7 (8), `dirty` (2).
- **Dense rows**: `mode`, `dirty`, `auditLog` each touched by 4/4 actions.
  Dense columns: `PlaceOrder`, `ShipOrder`, `RetrySweep`.
- **Q = 0.000**, one cluster of all 6 variables, no port-crossing actions —
  no cut exists because the stamps couple everything to everything.
- Coverage nominally clean ("every variable is read by at least one
  configured invariant") — but only via the aliased `Inv == TypeOK /\ SafetyInv`:
  `mode` and `dirty` are read by **no property beyond their type conjunct**.
- No justification table (dead-weight audit skipped).
- TLC baseline: green, 1,878 generated / 717 distinct states, depth 13.

## Judgment (per the intuition doc's reading order)

1. **Unknowns**: none. Good.
2. **Bound vs behavior**: almost entirely representation, not behavior. The
   only distinctions the behavior makes are: `orders` 0..3 (guard
   `orders < 3`, invariant `orders <= 3`), `shipped` 0..3 (`shipped <= orders`),
   `retries` 0..2 (guard `retries < 2`), `auditLog` 0..12 (guard
   `auditLog < 12`; the cap stops the world). Declared widths were 4x-11x
   the essential widths — an essential-width remodel of the same behavior
   yields 4*4*3*13 = 624.
3. **Dense rows**: `mode` (written by every action, read by nothing — no
   guard, no invariant beyond type, no test, no code reader) and `dirty`
   (toggled by every action, distinguishes nothing) are the textbook
   example-3 signature: bookkeeping smeared across every transition,
   carrying zero behavioral distinctions while multiplying the bound by 16x
   and densifying every column. `auditLog` is the exception: its cap is real
   behavior, asserted by `test_audit_cap_stops_everything` — it stays, as
   the one accepted dense row.

## Decision

Two moves, both executed:

1. **Production refactor** (authorized by the ticket: "consider how to
   refactor complexity out of the app ... decide ... and do it"): remove the
   `mode` and `dirty` fields from `order_hub.py`. No test reads them, no
   function's return value depends on them, no guard consults them — the
   behavior contract (the tests) is untouched, byte for byte.
2. **Representation remodel**: drop `mode`/`dirty` from `OrderHub.tla` and
   tighten every remaining domain to its essential width
   (`orders`/`shipped` 0..3, `retries` 0..2, `auditLog` 0..12). Guards,
   actions, `SafetyInv`, and `Init` are otherwise unchanged. Added a
   per-variable `justification:` table to the manifest.

Explicitly **not** done: no change to the audit-cap coupling. `auditLog` is
still written by 4/4 actions — that is the program's real shape (a shared
cap that stops the world), not accidental complexity. Q stays 0.000 and one
dense row remains; both are defended, not fixed.

## Validation (behavior retained, same run)

| measure | before | after |
|---|---|---|
| state-space bound | 8,388,608 (WARNING > 1M budget) | 624, no warnings |
| TLC (120s timeout) | green: 1,878 generated / 717 distinct, depth 13, max outdegree 4 | green: 717 generated / 270 distinct, depth 13, max outdegree 4 |
| tests | 6/6 pass | same 6/6 pass, zero assertion changes |
| dense rows | mode, dirty, auditLog (4/4 each) | auditLog only (accepted) |
| invariant coverage | all covered, but mode/dirty type-only | all covered; every variable also guard- or SafetyInv-relevant |
| justification linkage | no table | every variable linked (invariants/effects/kill tests) |

Transition-diff sanity (the deleted-self-loop red flag): generated and
distinct counts fell **together** (717/270 vs 1,878/717), and depth (13) and
max outdegree (4) are unchanged — the reachable transition structure is the
same program minus unread distinctions, not a deleted behavior.

## Remembered as fitness functions

`specs/program_model/fitness_functions.json` (JSON because this environment
has no PyYAML): `bound-stays-proportional` (bound <= 2000, auditLog domain
<= 13), `audit-cap-is-the-only-hub` (god_state_count <= 1,
dense_column_count <= 1), `all-state-load-bearing`
(unread_by_invariant_count == 0, unjustified_count == 0). All three hold on
the current scan (`validation_artifacts/scan_with_fitness.txt`); a
widened-domain scratch copy confirmed `bound-stays-proportional` FIREs on
regression.
