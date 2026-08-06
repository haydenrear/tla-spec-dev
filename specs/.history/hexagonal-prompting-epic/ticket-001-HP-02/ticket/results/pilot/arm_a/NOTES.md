# NOTES — QuotaLedger (arm A)

## What I built

A single class, `QuotaLedger`, in `quota_ledger.py`, importable as module
`quota_ledger`. It holds three per-tenant dicts (`available`, `committed`,
`closed`) and one dict of live reservations (`id -> (tenant, amount)`), plus a
monotonic counter for reservation ids. `commit` and `close_tenant` append a
line to the ledger file and to an in-memory mirror list; `ledger_lines()`
returns the mirror. A small frozen `Result` dataclass (`status`, `reason`,
`reservation_id`) is the return type for every command.

Everything lives in one file because the feature explicitly leaves file/module
layout as a free choice, and nothing about this feature (single class, no
external collaborators, no swappable durability backend) asked for more
structure than that. The durable side is reached directly (`Path.open("a")`),
not through an injected interface, since there's exactly one durability
mechanism in scope and no configuration axis to abstract over.

## Decisions

- **Construction truncates the ledger file.** The spec says "the ledger file
  starts empty" but doesn't say what to do if a file already exists at the
  given path. I chose to truncate on construction (`write_text("")`) rather
  than assume the path is always fresh, so the invariant ("starts empty")
  holds unconditionally rather than only when the caller happens to hand in a
  path nothing has touched. Covered by
  `test_construction_truncates_a_preexisting_file`.
- **Accepted results other than `reserve`'s carry `reservation_id=None`.** The
  spec says an accepted result "carries the `reservation_id` where the
  command has one" — only `reserve` allocates one, so `commit`, `release`, and
  `close_tenant` return `Result(status="accepted")` with `reservation_id`
  defaulting to `None`. The shared suite never inspects this field on those
  three, so this is inference, not something the tests pin down.
- **Reservation id counter never rewinds.** A rejected `reserve` never touches
  the counter (nothing was allocated); a released or committed reservation's
  id is freed from `_outstanding` but the counter keeps climbing, per "ids are
  ... never reused." Covered by
  `test_reservation_ids_keep_climbing_past_release_and_commit`.
- **`outstanding_ids()` sorts numerically, not lexicographically.** "Ascending"
  for ids like `r1, r2, ..., r10` is ambiguous under plain string sort (`r10`
  would sort before `r2`). I read "ascending" as ascending allocation order,
  i.e. numeric, and sort on `int(id[1:])`. Covered by
  `test_outstanding_ids_sort_numerically_not_lexicographically`.
- **Rejection order in `reserve`.** Implemented exactly in the order the
  feature lists: `unknown_tenant`, `tenant_closed`, `amount_not_positive`,
  `quota_exceeded`. Same for `close_tenant`'s three reasons. No ambiguity here,
  noted only because it's easy to get the order wrong and have it not show up
  until a case where two conditions overlap.

## Nothing ambiguous or self-contradictory found otherwise

The rest of the spec (R1-R5, the six rejection reasons, the two ledger line
formats) read as unambiguous to me and I implemented them literally.

## Files I did not open

None of the forbidden files were opened: `seeded_faults.toml`,
`check_catalogue.py`, `reference/`, `arm_b/`, `PREDICTIONS-HP.md`, or anything
under `specs/results/scorecards/` / `specs/.history/*/closed-snapshot/results/scorecards/`.

## How to run

From the repository root:

```bash
QUOTA_LEDGER_DIR=specs/tickets/HP-02/results/pilot/arm_a \
QUOTA_LEDGER_IMPL=quota_ledger \
  uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q
```

28 passed. My own extra tests are in `test_quota_ledger.py` in this directory
(run with `uv run --with pytest python -m pytest test_quota_ledger.py -q` from
this directory) — 6 passed.
