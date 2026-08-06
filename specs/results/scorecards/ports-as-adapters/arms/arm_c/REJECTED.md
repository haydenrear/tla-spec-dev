# REJECTED — what I considered and did not do

## Design: an in-memory ledger-lines cache alongside the file

First draft kept a `self._lines: list[str]` that both the writer and
`ledger_lines()` used, appending to it whenever the file was appended to.
Rejected it once I noticed `ledger_lines()` would then never actually prove
the file write happened — a bug that appended to the list but wrote to the
wrong path, or wrote with a bad mode, would pass every test that only calls
`ledger_lines()`. Switched to reading the file itself on every call. Slower
(a full file read per query) but the feature calls it a *durable* ledger, and
"durable" is exactly the property a cache can silently stop reflecting. The
program is small enough that the read cost is not a real concern.

## Design: a `Reservation` class instead of a `(tenant, amount)` tuple

Considered giving each outstanding reservation its own small class or
dataclass rather than storing `(tenant, amount)` tuples in a dict keyed by
id. Rejected it — there is nothing else a reservation needs to carry (no
timestamp, no status field beyond "is it in the outstanding dict at all"),
so a named class would be a wrapper around two fields with no behavior of
its own. `outstanding_reservations` in `close_tenant` would have needed
`r.tenant == tenant` instead of `held_tenant == tenant` from an unpacked
tuple — a wash either way, so I kept the smaller thing.

## Design: raising exceptions for programmer errors (e.g., a `tenant` that's
not a string, negative quotas at construction)

Feature doesn't call out constructor validation, and "Not part of the
feature" explicitly rules out scope inflation. Considered adding a guard
against negative quotas passed into the constructor, since a negative quota
would make `available` start negative and every subsequent `reserve` reject
with `quota_exceeded` in a confusing way. Rejected adding it: nothing in the
feature says construction can fail, there's no rejection vocabulary for a
constructor, and "do not invent requirements to resolve it" cuts against
inventing a new failure mode the feature never names. If someone constructs
a `QuotaLedger` with a negative quota, the program will behave in a way
that's *consistent* (conservation still holds: available starts negative,
reservations against it still reduce available further, nothing crashes) even
though it's presumably not what a caller wants. Left it alone.

## Check: asserting the exact exception type for malformed input

Considered writing tests that pass a non-string `tenant` or non-int `amount`
and asserting *something* sensible happens (a clean `TypeError`, or a
rejection). Rejected writing these — the feature specifies a closed
vocabulary of six rejection reasons for command failures, all of which are
about domain state (unknown tenant, closed tenant, bad amount, unknown
reservation, outstanding reservations), not about malformed argument types.
A `TypeError` from `amount < 1` on a non-comparable type is Python doing its
normal job, not a feature behavior, and inventing a rejection reason for it
would be exactly the kind of requirement-invention Section 5's ground rules
rule out. I did not write a test for this and did not add guard code for it.

## Check: fuzzing amount and tenant combinations beyond the named boundaries

Considered a property-style test that tries many random amounts against many
random quotas and checks conservation (R1) holds. Rejected it in favor of
the specific boundary values the feature actually names (0, negative,
exactly `available`, one over `available`) plus the two multi-step sequences
the shared suite and my own tests already exercise. A random sweep would
add a large count of executions without adding distinct claims — the
arithmetic in `reserve`/`commit`/`release` is the same three lines regardless
of which numbers go through it, so the boundary values are where a
off-by-one would actually show up, and I already have those.

## Reading: does "amount" ever need to be validated as an integer?

The feature says "`amount` is less than 1" for `amount_not_positive`, which
presumes `amount` is already a number you can compare to 1. Considered
whether to coerce or validate. Rejected doing either — the shared suite only
ever calls `reserve` with plain ints, and the feature gives no rejection
reason for "not an integer." I left `amount` untyped at the boundary (Python
will happily compare floats to `1` too) and did not test or guard for
non-numeric input, for the same reason as the malformed-input point above.

## Structural: splitting reservations and the ledger writer into separate
objects/modules behind an interface

The feature's "Deliberately unspecified" section explicitly says this is a
free choice ("whether the durable side is reached through an interface, a
callable, or directly"). Considered it, in particular a small `LedgerWriter`
class the `QuotaLedger` would hold a reference to, so the append-only file
write is one clearly-named seam. Rejected it for this program: there is
exactly one place that writes to the ledger (`_append_line`), it is called
from exactly two commands, and introducing a second class to wrap one method
would be a layer with no second implementation behind it and no test that
needs to swap one in. Kept it as a private method on `QuotaLedger`.

## Nothing else

I did not find a reading of the feature I discarded for producing wrong
behavior — the four rejection reasons on `reserve`, the three on
`close_tenant`, and the "committing does not restore available" rule all
read the same way on every pass through the text, so there was no second
interpretation to reject there. Everything above is either a structural
choice or a scope boundary, not a behavioral one.
