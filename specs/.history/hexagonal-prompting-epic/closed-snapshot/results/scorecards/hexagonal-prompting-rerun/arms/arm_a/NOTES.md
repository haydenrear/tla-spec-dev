# NOTES — arm A, quota ledger

## What I built

Two files, both in this working directory:

- `quota_ledger.py` — the implementation. Exposes `QuotaLedger`, plus the
  `Result` type its commands return.
- `test_quota_ledger.py` — my own tests (32), on top of the shared suite.

Standard library only; no dependencies added.

### How to run the shared suite against it

The module is `quota_ledger`, in this directory. The shared suite needs the
directory on `sys.path`, which it takes from `QUOTA_LEDGER_DIR`:

```bash
QUOTA_LEDGER_DIR=/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/b726dabf-a199-4b0c-8c2d-dda863fb43b7/scratchpad/armwork/arm_a \
QUOTA_LEDGER_IMPL=quota_ledger \
  uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q
```

Result: **28 passed**, suite unedited.

My own tests:

```bash
cd <this directory> && uv run --with pytest python -m pytest test_quota_ledger.py -q
```

Result: **32 passed**.

### Shape of the code

One module. A frozen `Result` dataclass with `status` / `reason` /
`reservation_id`; a `_Reservation` record (id, tenant, amount, allocation
sequence); a small `_LedgerFile` for the durable side; and `QuotaLedger`
holding `available`, `committed`, the closed set, the live reservations, and
the id counter.

Each command validates in the order the feature lists the rejections, and only
then mutates. The six rejection reasons are module-level constants collected in
one frozenset, and `Result.rejected` asserts membership — that keeps R4's "a
rejection reason is always one of the six named above" from being something
each call site has to remember on its own.

## What I decided

Things the feature leaves open, or does not mention, where I had to pick:

1. **`ledger_lines()` reads the file on every call.** I kept no in-memory
   mirror of the ledger. The feature calls it "the durable ledger's lines", so
   a reader observing something the file does not contain seemed wrong, and it
   makes R2 and R5 checkable against reality rather than against a copy.
   Blank lines are filtered out on read, per the query's description.

2. **The durable write happens before the in-memory update** in `commit` and
   `close_tenant`. The line's contents are computable without mutating, so if
   the append raises, memory has not moved ahead of the ledger. Nothing in the
   feature requires this — it is not a crash-safety feature and I did not build
   one (no fsync, no journaling, no recovery; that is out of scope) — it just
   costs nothing and orders the two sides sensibly.

3. **The constructor truncates an existing file at the path.** "The ledger file
   starts empty" is stated as a fact about construction, so I made it true:
   create the file (and any missing parent directory) empty. The alternative
   reading — append to whatever is there, or refuse — would mean a fresh
   `QuotaLedger` could report committed totals it does not have in memory,
   breaking R2 on line one. I went with truncate.

4. **"Ascending" in `outstanding_ids()` means allocation order, not string
   order.** These differ once there are ten reservations: sorted as strings,
   `"r10"` comes before `"r2"`. I sort by the numeric sequence the id was
   allocated from, so `r2` precedes `r10`. The shared suite never gets past
   `r3`, so it does not distinguish the two; `test_outstanding_ids_are_ascending_past_ten`
   pins my reading.

5. **Accepted results from `commit` and `release` carry the reservation id**
   they acted on; `close_tenant` carries `None`, since it has no reservation.
   That is my reading of "an accepted one carries the `reservation_id` where
   the command has one".

6. **The quotas mapping is copied** at construction, so a caller mutating their
   dict afterwards cannot change a quota or introduce a tenant.

## What I was unsure about

- **Queries with an unknown tenant.** `available("nobody")` raises `KeyError`.
  The feature gives commands a rejection channel and queries none, and invents
  no return value for this case, so I left the dict lookup to speak for itself
  rather than inventing a sentinel like `0` or `None`. This is the one place I
  am aware of where a reasonable implementer could differ from me without
  either of us contradicting the text.

- **Non-integer `amount`.** The rule is literally "`amount` is less than 1", so
  `0.5` is rejected as `amount_not_positive` and `1.5` is not rejected at all —
  it would be held and committed as `1.5`, and would print that way in a
  `COMMIT` line. The feature says the quotas are integers but never says the
  amounts must be, and it gives me no reason to reject a non-integer amount, so
  I implemented the rule as written rather than adding a type check the
  vocabulary has no reason for. If integrality is meant to be enforced, the
  six-reason vocabulary is missing a reason for it.

- **`bool` is an `int` in Python**, so `reserve(t, True)` reserves 1. Falls out
  of the above; not worth a special case.

I did not find anything in the feature that is self-contradictory. The one
interaction I checked for a conflict — committing a reservation belonging to a
closed tenant — cannot arise, because closing requires no outstanding
reservations and a closed tenant can never acquire one.

## Scope

I did not add: concurrency or locking, a CLI, configuration, a ledger reader or
recovery path, persistence of anything but the ledger file, or an abstraction
over the file beyond the one small class that writes it. The feature calls
those out as scope inflation and I agree.

## Files opened

I read `examples/validation/ab/FEATURE.md` and
`examples/validation/ab/tests/test_behavior.py`, and nothing else in the repo.

One disclosure, for completeness: I ran `ls` on `examples/validation/ab/`
before I knew what was in it, so I saw the *names* of some files on the
must-not-open list (`seeded_faults.toml`, `check_catalogue.py`, `reference/`,
`arm_b/`). I opened none of them and saw no contents. I have no idea what is
being measured or what is in the other arm.
