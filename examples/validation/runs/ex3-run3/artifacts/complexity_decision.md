# OrderHub complexity decision (2026-07-22)

Descriptor evidence: `descriptor_before.txt` / `descriptor_after.txt` in this
directory. Judged with `references/complexity_intuition.md` (tla-spec-dev).

## What the before-descriptor said

- **Bound 8,388,608** over 6 dimensions, WARNING: exceeds the advisory
  `max_state_space_bound` of 1,000,000. Dominant dimensions: `auditLog` 64,
  `retries` 32, `orders`/`shipped` 16 each.
- **Three dense rows**: `mode` (w 4/4), `dirty` (rw 4/4), `auditLog`
  (rw 4/4). Dense columns: PlaceOrder, ShipOrder, RetrySweep.
- **Q = 0.000, single cluster**, no port-crossing cut exists: mode/dirty/
  auditLog couple every variable to every action.
- Invariant coverage nominally clean, but only via aliasing: `Inv` includes
  `TypeOK`, whose conjuncts for `mode` and `dirty` are type-only.
- No justification table (dead-weight audit skipped).

## The judgment, fact by fact

**1. `mode` and `dirty` fail the write-only-state test — bookkeeping.**
The intuition doc's test: a write-only stamped variable is bookkeeping unless
you can name a concrete dependent — a guard that branches on it, an invariant
beyond its type conjunct, a test that asserts it, or a reader that consumes
it. Exhaustive check of this project:

- No guard in OrderHub.tla or order_hub.py reads `mode` or `dirty`.
- No invariant beyond the `TypeOK` type conjuncts (`mode \in 0..7`,
  `dirty \in BOOLEAN`) reads them; `SafetyInv` reads only orders/shipped.
- No test in tests/test_order_hub.py asserts `hub["mode"]` or `hub["dirty"]`.
- No production or toolchain reader consumes them.

The README's "stamping the shared mode ... and dirty flag" is stated intent,
and the test is explicit that stated intent is not a reader. This exact model
family is the doc's recorded boundary case: the run-1 classification (remove;
bound 624) is named canonical there. Classified: bookkeeping — removed from
model AND code. Code-removal authorization: this ticket's instruction to
"consider how to refactor complexity out of the app ... decide what to do
about this project's complexity, and do it", with tests as the behavior
contract.

**2. `auditLog` passes the test — keep it.** Every action's guard reads it
(`auditLog < 12` — the cap that stops the world), and two tests assert its
value (`test_audit_grows_with_every_operation`,
`test_audit_cap_stops_everything`). Its density (rw 4/4) is essential
behavior: a global operation cap is by definition read/written everywhere.
It stays, as the one accepted dense row.

**3. Domains were representation-wide — tightened to behavior width.**
The essential-distinction question per dimension: guards/invariants
distinguish orders 0..3 (cap 3), shipped 0..3 (<= orders), retries 0..2
(cap 2), auditLog 0..12 (cap 12, +1 steps). Declared domains were 0..15,
0..15, 0..31, 0..63 — 16x/16x/32x/64x wider than any distinction the
behavior makes. Tightened `TypeOK` to the essential widths. TLC confirms the
tightened TypeOK is invariant (no reachable state leaves it), so this is a
representation change only.

## What was changed

- `specs/program_model/OrderHub.tla`: removed `mode`/`dirty` and their
  stamping conjuncts; tightened TypeOK domains to 0..3 / 0..3 / 0..2 /
  0..12. Guards, action set, Init, SafetyInv unchanged.
- `order_hub.py`: removed `mode`/`dirty` from `new_hub`; `_stamp(hub, mode)`
  became `_record(hub)` (audit increment only). All guards and return values
  unchanged.
- `README.md`: no longer claims the mode/dirty stamping; notes the removal.
- `specs/program_model/spec_manifest.yaml`: added the `justification:` table
  (every remaining variable linked to invariants + the tests that need it).
- `specs/program_model/fitness_functions.json`: three remembered-decision
  rules (see below). Placed in JSON because this python lacks PyYAML.

Not changed: tests (the behavior contract) — zero edits, all 6 pass before
and after.

## Validation (before -> after)

| measure | before | after |
|---|---|---|
| state-space bound | 8,388,608 (WARNING > 1,000,000) | 624, no warnings |
| TLC (120s timeout) | green, 1878 generated / 717 distinct, depth 13 | green, 717 generated / 270 distinct, depth 13 |
| tests | 6 passed | 6 passed (unmodified) |
| dense rows | mode, dirty, auditLog | auditLog only (defended above) |
| invariant coverage | clean only via type-conjunct aliasing | clean; every var also read by a guard or asserted by a test |
| justification linkage | no table (audit skipped) | every variable linked |

Self-loop red-flag check: generated and distinct fell together (2.62x /
2.66x) and graph depth stayed 13 with the same max outdegree 4 — state
dimensions were removed, not transitions. The bound fell 13,444x because
representation left, not behavior: every guard, cap, invariant, and test
outcome is identical.

Residual facts accepted as-is: Q remains 0.000 (a 4-variable model with one
shared cap has no block structure to find); ShipOrder is flagged as a dense
column (3/4 variables — the essential `shipped < orders` guard plus the
audit cap, a small-model artifact per intuition example 2).

## Fitness functions configured

In `specs/program_model/fitness_functions.json`, all holding on the current
scan (`scan_with_fitness.txt`):

1. `bound-stays-essential` — bound known and <= 624; growth must arrive with
   a nameable behavior and a raised value.
2. `domains-stay-behavior-width` — per-variable domain caps (4/4/3/13); no
   return of production-width counters.
3. `no-new-bookkeeping-state` — god_state_count <= 1 (auditLog is the one
   accepted dense row), unread_by_invariant_count == 0,
   unjustified_count == 0.
