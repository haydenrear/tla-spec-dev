# NOTES — arm_c

## What was built

`quota_ledger.py` — one module, one class `QuotaLedger`, one frozen dataclass
`Result` for command return values. Import it as:

```
QUOTA_LEDGER_DIR=specs/results/scorecards/ports-as-adapters/arms/arm_c \
QUOTA_LEDGER_IMPL=quota_ledger \
uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q
```

`test_extra.py` — 11 tests of my own, plus the unedited shared suite. Both
pass:

- `examples/validation/ab/tests/test_behavior.py`: 28 passed (ran from the
  repo root with the env vars above).
- `test_extra.py`: 11 passed (`uv run --with pytest python -m pytest
  specs/results/scorecards/ports-as-adapters/arms/arm_c/test_extra.py -q`,
  run from this directory).

Standard library only: `dataclasses`, `pathlib`, `typing`.

## Clause-by-clause account

For each clause: where it lives, and the concrete input I ran that would
have caught it being absent. All of these were actually executed — either by
the shared suite, by `test_extra.py`, or by an ad hoc script I ran during
development (quoted inline where it isn't in either test file) — not
reasoned about.

- **Construction / empty ledger file.** `QuotaLedger.__init__` calls
  `self._ledger_path.write_text("")`. Checked with a path that already had
  `"leftover garbage\n"` on disk before construction:
  `test_construction_truncates_an_existing_file` — after construction,
  `path.read_text() == ""`.

- **`available`, `committed`, `is_closed`, `outstanding_ids`,
  `ledger_lines`.** Each is a one-line dict lookup or, for `ledger_lines`, a
  read of the actual file on disk (not an in-memory mirror — see "durable"
  below). Covered throughout the shared suite's `snapshot()` helper and
  directly in `test_ledger_file_on_disk_matches_ledger_lines`, which reads
  the ledger file with `path.read_text()` independent of the `QuotaLedger`
  object and compares it byte-for-byte to `"COMMIT acme 5 5\nCLOSE acme
  5\n"`.

- **`reserve` — rejection order and all four reasons.**
  `reserve.<locals>` in `quota_ledger.py` checks unknown_tenant, then
  tenant_closed, then amount_not_positive, then quota_exceeded, in that
  order — matching the feature's numbered list. Ran, ad hoc:
  `reserve("acme", 0)` against a *closed* acme → `tenant_closed`, not
  `amount_not_positive` (`test_reserve_order_tenant_closed_beats_amount_not_positive`).
  `reserve("nobody", 0)` → `unknown_tenant`, not `amount_not_positive`
  (`test_reserve_order_unknown_tenant_beats_amount_not_positive`). The shared
  suite's parametrized `test_reserve_rejects_and_changes_nothing` separately
  confirms each of the four reasons on its own (`nobody/1`→`unknown_tenant`,
  `acme/0`→`amount_not_positive`, `acme/-2`→`amount_not_positive`,
  `acme/11`→`quota_exceeded`, `globex/5`→`quota_exceeded`), and
  `test_reserve_rejects_a_closed_tenant` covers `tenant_closed`.

- **`reserve` — exact boundary.** "greater than `available`" means equal to
  available must accept. Ran `reserve("acme", 10)` against quota 10 →
  accepted, `available("acme")` becomes 0
  (`test_reserve_at_exact_available_boundary_accepts`). Ran
  `reserve("acme", 11)` → `quota_exceeded`
  (`test_reserve_one_over_boundary_rejects`, and the shared suite's own
  `test_reserve_exhausts_the_quota_exactly`).

- **`reserve` — id allocation, `r1, r2, r3, …`, never reused, only on
  accept.** Ran a sequence: rejected `reserve("nobody", 1)`, rejected
  `reserve("acme", 0)`, rejected `reserve("acme", 999)`, then accepted
  `reserve("acme", 1)` → got `r1`, not `r4`
  (`test_rejected_reserve_does_not_consume_an_id`). Ran: reserve, reserve
  (→r2), release r2, reserve again → got `r3`, not the freed `r2`
  (`test_release_then_reserve_does_not_reuse_the_released_id`). Ran eleven
  reserves in a row and checked `outstanding_ids()` is
  `["r1","r2",...,"r11"]` in that numeric order, not string order (a plain
  string sort would put `"r10"` before `"r2"`)
  (`test_outstanding_ids_sort_numerically_past_nine`).

- **`commit` — moves hold to committed, does not restore `available`, writes
  one `COMMIT` line, rejects `unknown_reservation`.** All four asserted by
  the shared suite's `test_commit_moves_the_hold_into_committed_and_writes_one_line`,
  which explicitly checks `available("acme") == 7` after committing a `3`
  reserved out of `10` — "committing does not give the hold back" is
  asserted, not assumed. `test_commit_rejects_an_unknown_reservation` and
  `test_commit_twice_rejects_the_second` cover the reject path and its R4
  no-op.

- **`commit` — running total is per-tenant and accumulates (R2).** Shared
  suite's `test_commit_running_total_accumulates` (two acme commits, 3 then
  2, lines `"COMMIT acme 3 3"` then `"COMMIT acme 2 5"`) and
  `test_commit_totals_are_per_tenant` (acme and globex interleaved, each
  keeps its own running total).

- **`release` — returns amount to available, writes nothing, rejects
  `unknown_reservation`.** Shared suite's
  `test_release_returns_the_hold_and_writes_nothing` and
  `test_release_rejects_an_unknown_reservation`.

- **`close_tenant` — rejection order and all three reasons.** Feature orders
  unknown_tenant, tenant_closed, outstanding_reservations. Ran
  `close_tenant("nobody")` → `unknown_tenant`
  (`test_close_order_unknown_tenant_beats_outstanding_reservations` — the
  ordering claim here is weaker than the reserve one: an unknown tenant can
  never hold a reservation, so this case can't actually collide with
  `outstanding_reservations`; I could not construct an input where both
  applied simultaneously, and say so rather than claim I tested the order).
  Shared suite covers `tenant_closed` via
  `test_close_rejects_an_already_closed_tenant` and
  `outstanding_reservations` via
  `test_close_rejects_while_a_reservation_is_outstanding`.

- **`close_tenant` — writes exactly one `CLOSE` line with the committed
  total, including zero.** Shared suite's `test_close_writes_the_final_total`
  (commit 3, close, line is `"CLOSE acme 3"`) and
  `test_close_with_nothing_committed_writes_zero` (`"CLOSE acme 0"`, nothing
  committed). My own `test_r3_close_is_singular_second_close_line_never_written`
  additionally closes, then tries to close again (rejected), and checks the
  ledger's `CLOSE` lines are still exactly `["CLOSE acme 0"]` — the second,
  rejected attempt did not add a second line.

- **R1 (conservation).** Shared suite's
  `test_r1_conservation_holds_through_a_mixed_sequence` and
  `test_r1_conservation_holds_while_reservations_are_live` run mixed
  reserve/commit/release sequences and check
  `available + held + committed == quota` holds at each checkpoint.

- **R2 (ledger agrees with memory).** Shared suite's
  `test_r2_the_durable_ledger_agrees_with_memory` sums the `COMMIT` amounts
  from `ledger_lines()` and checks it equals `committed()`, and checks the
  running total column matches a running sum. My
  `test_ledger_file_on_disk_matches_ledger_lines` additionally reads the raw
  file bytes, not `ledger_lines()`'s return value, so the check is against
  the actual durable artifact and not just the method that reports on it.

- **R3 (close is final and singular).** Covered above under `close_tenant`.

- **R4 (rejection changes nothing).** Every rejection test in both files
  captures a `snapshot()` (or, in mine, the specific fields the command could
  plausibly touch) before the call and asserts it is unchanged after. This is
  the one place I leaned entirely on the shared suite's `snapshot()` helper
  rather than writing my own for every rejection path — it already compares
  all five observable queries, so a second version would have been the same
  assertion under a different name.

- **R5 (append-only, ordered).** Shared suite's
  `test_r5_the_ledger_is_append_only_and_ordered` interleaves acme and
  globex commits and a close, and checks the resulting three-line ledger is
  in call order (`globex` commit before `acme` commit before `globex`
  close, because that's the order I called them) not tenant order or
  alphabetical order.

## Decisions

- **`Result.reservation_id` on `commit` and `release`.** The feature says an
  accepted result "carries the `reservation_id` where the command has one."
  `commit` and `release` are *given* a reservation id as their argument, but
  they don't *allocate* one the way `reserve` does. I read "has one" as
  "there is a reservation id associated with this accepted result" and set
  it to the id that was passed in on both `commit` and `release`, rather
  than leaving it `None`. Not run against by the shared suite either way
  (it only checks `.status`, `.reason`, and `.reservation_id` on `reserve`'s
  result) — so this is unverified by any assertion, only a reading I
  committed to. Marking it as such: I did not check this against any
  external requirement beyond my own reading of the sentence.

- **`ledger_lines()` reads the file, not a cache.** I could have kept an
  in-memory list and appended to it alongside the file write. I chose to
  make `ledger_lines()` re-read the file on every call instead, so that a
  bug in the file-write path (wrong path, wrong mode, a write that silently
  failed) would show up as a `ledger_lines()` failure too, rather than being
  masked by a cache that only reflects what the code *believes* it wrote.
  Checked in `test_ledger_file_on_disk_matches_ledger_lines`, which compares
  `path.read_text()` (opened independently) against `ledger_lines()` and
  finds them equal after a commit and a close.

- **Blank-line filtering in `ledger_lines()`.** The feature says "no blanks."
  My writer never emits a blank line (`_append_line` always writes a single
  non-empty line plus one newline), so the filter in `ledger_lines()`
  (`line != ""`) is currently unreachable in normal operation — it only
  matters if something else appended to the file, which nothing in this
  program does. I left it in because the query's contract says "no blanks"
  regardless of whether my writer happens to uphold it, not because I found
  a path that produces one. I did not run a case that exercises this filter;
  I am not claiming to have observed it doing anything, only that it is
  there.

## Ambiguity encountered

The one place the two halves of the prompt actually pulled in different
directions, as instructed: FEATURE.md's `close_tenant` rejection order names
`unknown_tenant` before `outstanding_reservations`, but by construction an
unknown tenant can never have an outstanding reservation (you can't `reserve`
against a tenant that isn't in the quota mapping), so there is no input that
exercises the *order* between those two checks — only the union of "each
reason is reachable on its own." I could not produce evidence for an
ordering claim that has no distinguishing input, so `NOTES.md` says exactly
that (see the `close_order_unknown_tenant_beats_outstanding_reservations`
paragraph above) instead of asserting the order was "verified." This is not
a conflict between the feature and Section 1's instructions in the sense the
prompt warned about (behavior vs. what-to-show) — it's a case where the
feature's own ordering, applied to `close_tenant`, has no input that
distinguishes two of its own steps for one pair of reasons. I did not treat
it as a contradiction requiring an interpretation choice, because both
readings (checked in order vs. checked in the other order) produce identical
observable behavior for every input that exists; I just could not write it
up as something I "checked" against a specific input the way I could for
`reserve`'s four-way order.

## Files opened

Only `examples/validation/ab/FEATURE.md` and
`examples/validation/ab/tests/test_behavior.py`, as instructed. Nothing under
Section 6's forbidden list was opened.
