# Complexity Decision — order_hub (2026-07-21)

Descriptor evidence: `descriptor_before.txt` (baseline), `descriptor_after.txt`
(post-change), `scan_with_fitness.txt` (with fitness functions configured).
Judged against `references/complexity_intuition.md` (tla-spec-dev toolchain).

## What the baseline descriptor said

- **Bound = 8,388,608**, tripping the 1,000,000 advisory threshold. Dominant
  dimensions: `auditLog` 0..63 (64), `retries` 0..31 (32), `orders`/`shipped`
  0..15 (16 each), `mode` 0..7 (8).
- **Dense rows**: `mode`, `auditLog`, `dirty` touched by 4/4 actions; dense
  columns `PlaceOrder`, `ShipOrder`, `RetrySweep`.
- **Q = 0.000**, single cluster of all 6 variables, no port-crossing actions.
- Invariant coverage clean (every variable read by TypeOK); no
  `justification:` table; no unknowns.
- TLC reachability: 717 distinct states (1878 generated, depth 13) — bound
  was ~11,700x reachability.

## Judgment (reading order from complexity_intuition.md)

1. **Unknowns**: none. Nothing to explain.
2. **Bound vs behavior**: the bound was *representation, not behavior* — the
   textbook example-3 shape. The behavior's actual distinctions, straight
   from the guards, invariants, and tests:
   - `orders` ∈ 0..3 (guard `orders < 3`, invariant `orders <= 3`,
     `test_order_cap`);
   - `shipped` ∈ 0..3 (invariant `shipped <= orders <= 3`);
   - `retries` ∈ 0..2 (guard `retries < 2`, `test_retry_cap`);
   - `auditLog` ∈ 0..12 (guard `auditLog < 12` on every action — the cap
     that stops the world; `test_audit_cap_stops_everything` asserts the cap
     value, `test_audit_grows_with_every_operation` asserts exact counts, so
     every value 0..12 is an essential distinction);
   - `mode` ∈ 0..4 (Init sets 0; the only writes stamp 1..4);
   - `dirty` ∈ BOOLEAN.
   Essential bound: 5 x 4 x 4 x 3 x 13 x 2 = **6,240**. The other ~1,344x of
   the declared 8.39M was counter width no guard, invariant, or test ever
   distinguishes.
3. **Dense rows**: `auditLog`/`mode`/`dirty` written by every action is the
   *design* — "every operation routes through the hub, stamping the shared
   mode, audit log, and dirty flag" (README). `auditLog` is essential
   behavior (its cap gates every action; tests assert its exact values).
   `mode` and `dirty` are cheap stamps (x5 and x2 in the bound) that the
   code deliberately maintains. This is example-5 territory (deliberate
   hub density), not example-3 accidental smearing — a fact to record, not
   a problem to fix.
4. **Clusters**: Q = 0.000 / single component follows directly from the hub
   trio touching everything. Discounting the trio mentally, the remainder is
   well-shaped: `orders`/`shipped` (order lifecycle), `retries` (sweep),
   each with single writers.
5. **Coverage**: clean before and after.

## Decision

**Do a representation-only model refactor; do not touch the production code
or the tests.**

- **Done — tighten `TypeOK` to the behavioral domains** listed above
  (`OrderHub.tla`). This removes only representation width; additionally it
  *strengthens* verification, because TLC now checks the real caps
  (`auditLog <= 12`, `retries <= 2`, `shipped <= 3`, `mode <= 4`) as
  invariants instead of admitting unreachable slack.
- **Not done — production refactor of the hub stamps** (`mode`, `dirty`,
  `auditLog`). Rejected because: (a) `auditLog` is essential behavior, not
  bookkeeping — the tests assert its exact values and its world-stopping
  cap; (b) `mode`/`dirty` cost only x10 of a 6,240 bound and are the app's
  stated design; (c) the intuition doc requires explicit user approval
  before any production refactor, and there is no complexity payoff here
  that would justify asking.
- **Done — added a `justification:` table** to `spec_manifest.yaml` so every
  variable's right to exist is auditable (the baseline scan flagged its
  absence).
- **Done — configured two fitness functions** (in
  `specs/program_model/fitness_functions.json`; see below) so future agents
  are notified if the representation re-widens or new bookkeeping smears
  across the hub.

## Validation

| check | before | after |
|---|---|---|
| TLC (120s timeout) | green, 1878 generated / 717 distinct / depth 13 | green, **1878 generated / 717 distinct / depth 13 — identical** |
| tests (`uv run --with pytest -m pytest tests -q`) | 6 passed | 6 passed (no test touched) |
| state-space bound | 8,388,608 (WARNING > 1M) | 6,240, no warnings |
| dominant dimensions | auditLog 64, retries 32, orders 16 | auditLog 13, mode 5, orders 4 |
| R/W matrix, clusters, dense rows | see before | byte-identical sections |
| invariant coverage | all read | all read |
| justification linkage | no table | every variable linked |

The identical generated *and* distinct state counts are the transition-level
evidence the intuition doc demands: no behavior left the model and no
self-loop was deleted; only unreachable declared representation was removed.

## Fitness functions (advisory notifications for future agents)

1. `bound-stays-behavioral` — bound known and < 10,000; `auditLog` domain
   <= 13, `retries` <= 3, `orders` <= 4. Guards against exactly the
   regression fixed here (counters re-widened to production width). Headroom
   above 6,240 allows small essential growth; growth past it should arrive
   with a nameable behavior and a rule update.
2. `hub-density-stays-deliberate` — `god_state_count <= 3` (only the
   deliberate hub trio may be dense), `unread_by_invariant_count == 0`,
   `unjustified_count == 0`.

Both **hold** on the current scan (`scan_with_fitness.txt`). A probe scan on
a scratch copy with `auditLog` re-widened to 0..63 confirmed
`bound-stays-behavioral` FIRES with a leaf-level trace.

Note: the rules live in `fitness_functions.json`, not a manifest
`fitness_functions:` block, because this environment runs the CLI under a
bare `python3` without PyYAML and the manifest fallback parser cannot read
flow-style rule leaves (recorded as a toolchain finding in the ticket
report).
