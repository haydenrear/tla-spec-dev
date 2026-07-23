# OrderHub complexity decision (2026-07-22)

## Descriptor before (validation_artifacts/descriptor_before.txt)

- bound = 8,388,608 over 6 dimensions; dominant: auditLog 0..63 (64),
  retries 0..31 (32), orders/shipped 0..15 (16 each).
- Dense rows (god-state signature): `mode` (4/4, write-only), `dirty` (4/4),
  `auditLog` (4/4). Dense columns: PlaceOrder, ShipOrder, RetrySweep.
- Q = 0.000, single component; every variable invariant-read (via TypeOK);
  no justification table.
- WARNING: bound 8,388,608 > max_state_space_bound 1,000,000.

## Judgment (references/complexity_intuition.md reading order)

1. **Unknowns**: none.
2. **Bound vs behavior**: every domain was representation-wide. Behavior caps
   are orders <= 3, shipped <= orders <= 3, retries <= 2, auditLog <= 12 (the
   guards enforce exactly these), yet TypeOK declared 0..15/0..15/0..31/0..63.
   ~13,400x of the bound carried zero behavioral distinctions.
3. **Dense rows — the write-only-state test** ("a write-only stamped variable
   is bookkeeping — regardless of stated design intent — unless you can name a
   concrete dependent"):
   - `mode`: pure `w` row — written by every action, read by nothing. No guard
     branches on it, no invariant beyond its `mode \in 0..7` type conjunct, no
     test asserts it, no code reader (the app stamped it and never looked).
     **Bookkeeping — removed.** The README's "stamping the shared mode" is a
     sentence about the writer; stated intent is not a reader.
   - `dirty`: toggled by every action, read only by its own toggle. Same test,
     same result. **Bookkeeping — removed.**
   - `auditLog`: **passes the test** — every action's guard branches on it
     (`auditLog < 12` / `MAX_AUDIT`), tests assert its value
     (`test_audit_grows_with_every_operation`, `test_audit_cap_stops_everything`),
     and it is the program's one observable effect (consumed by
     `AuditJournalPort` in stages 3–5). Its 4/4 density is essential: "an audit
     log counts every operation up to a cap that stops the world" is the
     behavior. **Kept, defended, and given a justification + effect linkage.**
4. **Clusters**: single component both before and after — after the refactor
   the only coupling is through `auditLog`, which is the defended core.
5. **Coverage**: complete before and after (TypeOK reads everything).

## Action taken

- Model: removed `mode` and `dirty`; tightened TypeOK to behavioral widths
  (orders/shipped 0..3, retries 0..2, auditLog 0..12). No guard, action, or
  safety property changed.
- App (`order_hub.py`): removed the `mode` stamp and `dirty` toggle from
  `_stamp` (now `_audit`) and from `new_hub()`. Authorized by this ticket's
  scope ("refactor complexity out of the app"); classification and
  authorization kept separate per the intuition doc.
- Manifest: added `justification:` linkage for all four variables and two
  fitness functions locking the shape in.

## Validation (behavior retention, same run)

| measure | before | after |
|---|---|---|
| state-space bound | 8,388,608 | 624 (13,443x drop; nothing excluded) |
| TLC | green, 1878 generated / 717 distinct, depth 13 | green, 717 generated / 270 distinct, depth 13 |
| project tests | 6/6 pass | 6/6 pass, **assertions byte-identical** (no test ever read mode/dirty) |
| dense rows | mode, dirty, auditLog | auditLog only (defended above) |
| invariant coverage | complete | complete |
| justification linkage | absent | complete |
| warnings | bound > 1,000,000 | none |

Transition-level diff check (red-flag pattern: generated-states drop at
constant distinct states = deleted self-loop): generated and distinct dropped
together (1878/717 = 2.62 -> 717/270 = 2.66, depth 13 both) — the state graph
was quotiented by the removed bookkeeping dimensions, no transition structure
was deleted. The bound fell because representation left, not behavior.

Residual descriptor facts, accepted: `auditLog` dense row (essential, see
above); `ShipOrder` dense column (reads `orders` as the ship guard — the real
shipped<=orders coupling in a 4-variable model); Q = 0.000 (a 4-variable model
with one shared essential counter has no block structure to find).

## Fitness functions (locked-in shape)

- `bound-stays-behavioral`: `bound_known == true` AND `bound <= 624`. Any
  growth must arrive with a named new essential behavior and a rule update.
- `audit-is-the-only-dense-row`: `god_state_count <= 1` AND
  `unread_by_invariant_count == 0` AND `unjustified_count == 0`. auditLog is
  the one permitted dense row; no unread or unjustified state may return.

Both hold on the post-refactor scan (validation_artifacts/scan_with_fitness.txt).
