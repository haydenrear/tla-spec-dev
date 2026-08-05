# NOTES — arm A, quota ledger

## What I built

Two files, both in this directory:

- `quota_ledger.py` — the implementation. Public surface is `QuotaLedger`,
  plus the `Result` type its commands return and a `REASONS` frozenset naming
  the six rejection reasons.
- `test_quota_ledger.py` — my own tests (38), aimed at what the shared suite
  leaves open rather than at re-covering it.

Inside `quota_ledger.py`:

- `Result` — a frozen dataclass carrying `status`, and `reason` /
  `reservation_id` where the outcome has one. `accepted` / `rejected`
  properties for readability at call sites.
- `_Tenant` — one tenant's position: `quota`, `held`, `committed`, `closed`.
  `available` is a **derived property** (`quota - held - committed`), not a
  fourth stored counter. That makes R1 (conservation) true by construction
  rather than something three separate mutations have to keep true; there is
  no way to write a code path that drifts it.
- `_Reservation` — id, tenant, amount, and the allocation sequence number.
- `_LedgerFile` — the durable side. Its only write operation is an append; its
  read goes back to disk every time. R5 (append-only, ordered) is a property
  of this class having no other method.
- `QuotaLedger` — the commands and queries, holding the tenants, the live
  reservations, an id counter, and one `_LedgerFile`.

## Running it

Shared behavioral suite, from the repository root
(`/Users/hayde/IdeaProjects/wt-epic-hexagonal-prompting-HP-06`):

```bash
QUOTA_LEDGER_DIR=specs/results/scorecards/hexagonal-prompting/arms/arm_a \
QUOTA_LEDGER_IMPL=quota_ledger \
  uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q
```

Result: **28 passed**. `test_behavior.py` was not modified.

The module name the suite imports is `quota_ledger`. `QUOTA_LEDGER_DIR` is
inserted at `sys.path[0]`, so this directory wins over the reference directory
of the same module name; an absolute path for `QUOTA_LEDGER_DIR` works
identically and I verified both.

My own tests, from this directory:

```bash
uv run --with pytest python -m pytest test_quota_ledger.py -q
```

Result: **38 passed**. Standard library only, pytest as the runner; no
dependencies added.

## Decisions

**Checks run in the order the feature lists them, as a straight-line sequence
of early returns.** `reserve` reports `unknown_tenant` before `tenant_closed`
before `amount_not_positive` before `quota_exceeded`, so a request that fails
several checks reports the first. A negative amount against an exhausted quota
is `amount_not_positive`, never `quota_exceeded`. Tested explicitly, because
the shared suite only ever exercises requests that fail exactly one check.

**Rejections return before touching anything.** Every rejection path is an
early `return` above the first mutation and above the ledger write, so R4
holds structurally rather than by remembering to undo. In particular a
rejected `reserve` does not burn an id — the counter advances only past the
last check.

**The durable write happens before the in-memory mutation.** In `commit` and
`close_tenant` the line is appended first, then memory is updated to match the
line that was actually written. If the append raised, memory would be
untouched and R2 would still hold; the reverse order could leave memory
claiming a commit that never reached disk. Nothing in the feature requires
crash safety and I did not build any (no fsync, no journal) — this is just the
cheaper of two orderings.

**`available` is not stored.** See above. The practical consequence is that
`commit` moves an amount from `held` to `committed` and `available` does not
move, which is exactly what the feature says, and it is one subtraction and
one addition rather than a rule someone has to remember not to break.

**`ledger_lines()` re-reads the file.** It is not a memory mirror of what was
written. If it were, R2 would be tautological and the test that the durable
side agrees with memory would prove nothing. Blank lines are filtered on read,
per the query's description.

**`outstanding_ids()` sorts by allocation sequence, not by string.** Ids are
`r1, r2, … r10`, and `"r10" < "r2"` lexically. "Ascending" has to mean
allocation order for the sequence to be `r1…r10`, so each reservation carries
its sequence number and the sort uses it. The shared suite never reaches r10;
my suite does.

**The quota mapping is copied at construction.** `dict(quotas)` — a caller
mutating the mapping afterwards does not silently change quotas or introduce
tenants. Tested.

**The ledger file is truncated at construction.** "The ledger file starts
empty" is stated as a fact about construction, so an existing file at that
path is emptied rather than appended to. A missing parent directory is
created. Both tested.

## Things the feature does not settle, and what I chose

1. **Queries on an unknown tenant.** `available("nobody")`,
   `committed(...)`, `is_closed(...)` — the feature gives the six rejection
   reasons to *commands*, and queries do not return a `Result` at all, so
   there is no in-band way to say "no such tenant". I raise `KeyError`.
   Returning `0` would be worse: it would make a nonexistent tenant look like
   a real one with an empty position. This is a genuine free choice and a
   different arm could reasonably raise a custom exception instead.

2. **Non-integer `amount`.** The feature says quotas are integers and that
   `amount` is rejected when "less than 1", so I test `amount < 1` and do no
   type checking. A float `2.5` would therefore be accepted and would land in
   the ledger line as `2.5`. I did not add validation because the feature does
   not ask for it and "do not invent requirements" cuts against it — but it is
   the loosest edge of the implementation and I am flagging it rather than
   quietly deciding it does not matter.

3. **Whether `close_tenant` should be rejected for a tenant that is closed
   *and* holds reservations.** Unreachable: close cannot succeed while a hold
   is live, so no closed tenant ever has one. The check order is written as
   the feature lists it anyway. My test for close-precedence says so instead
   of asserting an unreachable case.

4. **`commit`/`release` on a reservation whose tenant was later closed.** Also
   unreachable for the same reason. No special handling.

I did not find a self-contradiction in the feature. The one place I had to
read carefully is that `commit` leaves `available` alone — the feature states
it twice, in the command description and in R1, and they agree.

## Scope

No concurrency, no locking, no CLI, no config, no network, no persistence of
anything but the ledger file, no reload-from-ledger constructor. The feature
puts all of those out of scope and I added none of them.

## Files I opened

`examples/validation/ab/FEATURE.md` and
`examples/validation/ab/tests/test_behavior.py`, both of which the prompt
directs me to read.

**Disclosure:** I ran `ls -la` on `examples/validation/ab/` and
`examples/validation/ab/tests/` before reading either file. That listed the
*names* of entries in the directory, including `seeded_faults.toml`,
`check_catalogue.py`, `reference/`, `arm_b/`, `model/`, `scorecard_shape/`,
and `README.md`. I opened none of them and read no contents beyond the two
files named above. All the do-not-open names were already given to me in the
prompt itself; `model/`, `scorecard_shape/` and `README.md` are names I
learned only from that listing and did not open. Reporting it because the
disclosure costs nothing and a listing is arguably a partial open.
