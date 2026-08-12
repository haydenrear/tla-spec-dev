# FEATURE — quota ledger

**One specification, written once, given to both arms unchanged.**

This file is the shared half of the A/B. It says only **what** the program must
do. It contains no guidance about structure, decomposition, layering, testing
style, simplicity, or file organization — all of that is the variable under
test and lives in the arm prompts, never here. If you are editing this file to
add a "should be modular" or a "keep it simple", stop: you are destroying the
experiment by putting the treatment into the control.

---

## The program

A `QuotaLedger` manages **reservations** held against a **per-tenant quota**,
and commits them to a **durable, append-only ledger file**.

Construction takes a mapping of tenant name to integer quota, and a path for
the ledger file. The ledger file starts empty.

## State a reader can observe

| Query | Returns |
|---|---|
| `available(tenant)` | the quota not currently held or committed |
| `committed(tenant)` | the total committed so far |
| `is_closed(tenant)` | whether the tenant is closed |
| `outstanding_ids()` | the ids of all live reservations, ascending |
| `ledger_lines()` | the durable ledger's lines, in the order written, no blanks |

## Commands

Every command returns a result carrying a `status` of `"accepted"` or
`"rejected"`. A rejected result carries a `reason`; an accepted one carries the
`reservation_id` where the command has one.

### `reserve(tenant, amount)`

Rejects, in this order, with these reasons:

1. `unknown_tenant` — no such tenant
2. `tenant_closed` — the tenant is closed
3. `amount_not_positive` — `amount` is less than 1
4. `quota_exceeded` — `amount` is greater than `available(tenant)`

Otherwise accepts: allocates a fresh reservation id, reduces
`available(tenant)` by `amount`, and records the reservation as outstanding.
Ids are allocated `r1`, `r2`, `r3`, … in order of acceptance and are never
reused.

### `commit(reservation_id)`

Rejects with `unknown_reservation` when the id is not outstanding.

Otherwise accepts: removes the reservation from outstanding, increases
`committed(tenant)` by the reservation's amount, and **appends exactly one
line** to the durable ledger:

```
COMMIT <tenant> <amount> <committed-total-after-this-commit>
```

`available(tenant)` is **not** changed — the amount was already deducted at
`reserve` and committing it does not give it back.

### `release(reservation_id)`

Rejects with `unknown_reservation` when the id is not outstanding.

Otherwise accepts: removes the reservation from outstanding and returns its
amount to `available(tenant)`. **Writes nothing to the ledger.**

### `close_tenant(tenant)`

Rejects, in this order:

1. `unknown_tenant` — no such tenant
2. `tenant_closed` — already closed
3. `outstanding_reservations` — the tenant has at least one live reservation

Otherwise accepts: marks the tenant closed and **appends exactly one line** to
the durable ledger:

```
CLOSE <tenant> <committed-total>
```

## Rules that must hold at all times

- **R1 — conservation.** For every tenant,
  `available + (sum of that tenant's outstanding amounts) + committed == quota`.
- **R2 — the durable ledger agrees with memory.** For every tenant, the
  amounts on that tenant's `COMMIT` lines sum to `committed(tenant)`, and the
  running total on each `COMMIT` line equals the sum of that tenant's `COMMIT`
  amounts up to and including that line.
- **R3 — a close is final and singular.** A closed tenant has no outstanding
  reservations and exactly one `CLOSE` line, whose total equals
  `committed(tenant)`.
- **R4 — a rejection changes nothing.** A command that returns
  `status == "rejected"` performs **no** state change and **no** durable write.
  A rejection reason is always one of the six named above.
- **R5 — the ledger is append-only and ordered.** Lines appear in the order the
  accepting commands ran. Nothing is ever rewritten, reordered, or removed.

## What "done" means

`examples/validation/ab/tests/test_behavior.py` runs unchanged against your
implementation and passes. That suite is the shared behavioral contract for
both arms; it is not a definition of quality and passing it is a floor, not a
result.

## Deliberately unspecified

These are free choices, and both arms are free to make them differently. They
are listed so that a judge does not read a difference here as a defect:

- how the code is split across files, modules, classes, or functions;
- whether the durable side is reached through an interface, a callable, or
  directly;
- how reservations are stored;
- what additional tests you write beyond the shared suite.

## Not part of the feature

No concurrency. No process boundaries. No persistence of anything except the
ledger file. No configuration, no CLI, no network. Adding any of these is out
of scope and will be read as scope inflation, not as thoroughness.
