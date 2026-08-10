# NOTES — quota ledger

## What I built

Two files, both in this directory:

- `quota_ledger.py` — the implementation. Exposes `QuotaLedger`, plus `Result`
  and the reason vocabulary (`Reason`, `REASONS`).
- `test_quota_ledger.py` — my own tests, 21 of them, alongside the shared suite.

Standard library only, no dependencies added. `FEATURE.md` and
`examples/validation/ab/tests/test_behavior.py` were not modified.

**Module name for the shared suite: `quota_ledger`.**

```bash
QUOTA_LEDGER_DIR=<...>/subjects/artifact_Z QUOTA_LEDGER_IMPL=quota_ledger \
  uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q
# 28 passed

cd <...>/subjects/artifact_Z && uv run --with pytest python -m pytest test_quota_ledger.py -q
# 21 passed
```

## Shape of it

One class, one file. The feature is small — four commands, five queries, one
output file — and splitting it further would have added indirection without
removing anything.

- `_Tenant` holds a tenant's whole position: `quota`, `available`, `committed`,
  `closed`, and a count of live reservations. The count is there so
  `close_tenant` can answer "does this tenant hold anything" without scanning
  the reservation table.
- `_Reservation` is a frozen `(tenant, amount)` pair in a dict keyed by id.
- `Result` is a frozen dataclass with `status` / `reason` / `reservation_id`.
  Its `rejected()` constructor asserts the reason is one of the declared six,
  so an undeclared reason cannot leave this module even by typo.
- `_append` is the only code that writes to the file. Everything durable goes
  through that one line, which is what makes "append-only, one line per
  accepted command" checkable by reading a single method.

Every command validates fully before it mutates anything, so R4 (a rejection
changes nothing) holds by construction rather than by rollback — there is no
partial state to undo.

## Decisions

- **`ledger_lines()` reads the file, every call.** It does not answer from an
  in-memory copy. R2 says the durable side agrees with memory; a query served
  from memory could never report that it doesn't. Blank lines are dropped as
  the feature asks. This costs a read per call and is not a hot path.
- **The constructor truncates.** "The ledger file starts empty," so
  construction writes an empty file, creating parent directories if needed. A
  pre-existing file at that path is emptied rather than appended to or treated
  as an error. See the ambiguity note below.
- **Writes are flushed and `fsync`ed** before the accepting command returns,
  since the ledger is described as durable.
- **`outstanding_ids()` sorts by the numeric part of the id**, not
  lexicographically, so `r9` precedes `r10`. Insertion order would happen to be
  correct here, but it would be correct by accident.
- **The id counter advances only on acceptance**, so rejected reserves consume
  no ids and the sequence is "order of acceptance" as specified.
- **`commit` does not restore `available`.** Called out explicitly in the
  feature and easy to get backwards, so it carries a comment at the site.
- **Accepted results carry a `reservation_id` only from `reserve`**, which is
  the only command that has one; the other three return `reservation_id=None`.
- The ledger path accepts a `str` or a `Path`.

## Tests I wrote

The shared suite is thorough on the happy paths, so mine go where it doesn't:

- **Reason ordering when two checks would both fire** — `reserve("nobody", 0)`
  must say `unknown_tenant`, a closed tenant beats a bad amount, a negative
  amount beats `quota_exceeded`. The listed order in the feature is only
  observable in these overlaps.
- **The file on disk**, byte for byte, rather than only `ledger_lines()`; that
  the file starts empty; that release never touches it.
- **Id allocation** past `r9`, and that rejections consume no ids.
- **Double resolution** in all four orders (commit/commit, commit/release,
  release/commit, release/release).
- **A 600-step deterministic random sequence** driving all four commands
  against a shadow model, checking R1–R5 after *every* step, and asserting at
  the end that the run actually reached both outcomes of every command and all
  six reasons — otherwise a run that quietly stopped doing anything would still
  pass. Quotas there are deliberately lopsided: two large tenants keep
  reservations live for 600 steps (a commit drains quota permanently), one tiny
  tenant is what generates `quota_exceeded`.

Two of my own tests failed on first run. Both were bugs in the tests, not the
implementation: one asserted six distinct reasons from a setup that could only
produce five, and one asserted a ledger line count the model makes impossible
(committed quota never returns, so total lines are bounded by total quota).

## Ambiguities and unsureties

1. **A pre-existing ledger file.** The feature says the file starts empty but
   not what to do if something is already at the path. I truncate. The
   alternatives — appending to it, or refusing — are equally consistent with
   the text; I picked the one that makes the stated postcondition true for
   every construction. I did not implement more than one.
2. **Queries against an unknown tenant** (`available("nobody")`) are
   unspecified: the query table has no rejection channel and the six reasons
   belong to commands. Those queries raise `KeyError`. Returning a sentinel like
   `0` or `None` would have made an unknown tenant indistinguishable from an
   exhausted one, which seemed worse than raising.
3. **Non-integer amounts.** The feature says integer quotas and "amount is less
   than 1". I compare numerically and neither coerce nor type-check, so
   `reserve("acme", 2.5)` would be accepted and would print as `2.5` in the
   ledger. Rejecting it would mean inventing a seventh reason, which the feature
   forbids, and silently coercing would break conservation. Left as is, and
   flagged here.
4. **Whether `is_closed`/`close_tenant` interact with commits of reservations
   made before a close** — they can't. Close requires no outstanding
   reservations, so no reservation can outlive its tenant's close. Not a
   contradiction, just a thing I checked for and did not find.

I found nothing self-contradictory in the feature.

## Disclosure

I opened no file from the "must not open" list. Files I read: `FEATURE.md` and
`tests/test_behavior.py`, both named in my instructions. I also ran a
directory listing (`ls`) of the repository root and of my own working directory
to orient myself, which showed top-level filenames but opened no file; noting it
here since it is the only thing I did outside `examples/validation/ab/`.
