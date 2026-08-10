# NOTES — quota ledger

## What to import

```
QUOTA_LEDGER_DIR=<this directory> QUOTA_LEDGER_IMPL=quota_ledger
```

`quota_ledger` is a package; `QuotaLedger` is exported from its `__init__.py`.

Both suites pass:

- shared contract: `examples/validation/ab/tests/test_behavior.py` — 28 passed, file unchanged.
- mine: `tests/` in this directory — 39 passed.

## What I built

```
quota_ledger/
  domain.py          the rules; declares the Journal port
  file_journal.py    Journal backed by a text file
  memory_journal.py  Journal kept in memory
  __init__.py        composition point: QuotaLedger = Ledger wired to a file
tests/
  test_journal_parity.py   one case list, run against both journals
  test_ledger.py           behavior the shared suite leaves open, plus the wiring
```

## The port

There is exactly one thing outside the rules: the durable, append-only ledger.
So there is exactly one port, `Journal`, with two methods — `append(line)` and
`lines()` — declared in `domain.py` in the domain's vocabulary, named for the
need rather than for files.

Nothing else is indirected. Id allocation, quota arithmetic and the rejection
ordering are pure computation, and a port in front of them would be an
interface with nothing behind it to swap. There is no clock, no environment, no
network in this feature, so there is no port for one.

**The swap sentence:** replace `FileJournal` with `MemoryJournal` — or with a
journal that appends to SQLite, to a socket, to an S3 object — and no file
under `quota_ledger/` other than `__init__.py` changes. `domain.py` imports
neither adapter; `tests/test_ledger.py::test_the_domain_module_does_not_import_its_adapters`
asserts that rather than asking you to believe it.

`MemoryJournal` is a working implementation, not a mock: it records no calls
and makes no assertions. `tests/test_journal_parity.py` runs the *identical*
case list against both journals, and every case asserts a literal expected
value — lines, availables, committeds, closed flags, outstanding ids. Two
wirings of the same domain agree with each other even when the domain is wrong,
so agreement alone would be a test that can never fail for an interesting
reason. Agreement still falls out of the same expected dict passing under both
parametrisations; it just isn't what the test rests on. No case in that list
can be written for only one of the journals.

## Decisions

**`available` is derived, not stored.** It is
`quota - committed - sum(live holds)`. R1 (conservation) is then arithmetic
instead of an invariant that `reserve`, `commit`, `release` and `close` each
have to remember to maintain, and `release` collapses to a single dict removal.
Nothing was deleted here: the behavior "release returns the hold" is carried by
the hold leaving `_holds`, and "commit does not give the hold back" is carried
by `committed` rising by exactly the amount the hold stopped contributing.
`stored available` would have been a fourth writer of the same number.

**`Result.status` is derived from `reason`.** An accepted result is exactly one
with no reason, so a stored `status` could only ever contradict the `reason`
beside it. `status` is still on the public surface, unchanged, and both suites
read it.

**A live reservation stores no id of its own.** It is stored under its id in a
dict; a copy inside the value would be a field nothing reads.

**`committed` is stored, not recomputed from the ledger file.** Recomputing it
would make R2 true by construction, but it would put a parser for the ledger's
own line format in the domain and make every query a read of the durable side.
Instead `commit` is the single writer of `committed` and appends the matching
line in the same step, which is where R2 actually lives.

**Ids sort numerically, not lexicographically.** "Ascending" is ambiguous once
there are ten reservations — `"r10" < "r2"` as strings. I read it as issue
order and sort by the integer, tested at
`test_outstanding_ids_ascend_numerically_past_nine`. The dict's insertion order
would give the same answer today; sorting explicitly means the query does not
depend on an allocation invariant holding forever.

**Ids advance only on acceptance.** A rejected `reserve` does not consume one,
which is the only way R4 ("a rejection changes nothing") is observable for the
counter.

**"The ledger file starts empty" is implemented as truncation.** `FileJournal`
writes an empty file at construction, so constructing over a pre-existing file
discards it. The alternative reading — append to whatever is there — would
require reading prior state back into memory, which the feature explicitly puts
out of scope ("no persistence of anything except the ledger file"). Tested at
`test_the_ledger_file_starts_empty`.

**Blank-line filtering lives in `FileJournal`, not in the domain.** The empty
string after the final newline is an artifact of storing lines in a file;
`MemoryJournal` has no such artifact and so needs no filter.

## Unsure / unspecified, left alone

- **Queries for an unknown tenant.** `available("nobody")` raises `KeyError`.
  The feature specifies rejection reasons for *commands* only and says nothing
  about queries, so I did not invent a return value for this.
- **Non-integer amounts.** `amount < 1` rejects `0.5` as `amount_not_positive`
  and accepts `3.0`. The feature says "integer quota" and "less than 1"; I did
  not add a type check it does not ask for.
- **Duplicate tenant names / non-positive quotas at construction.** Not
  specified, not validated. A tenant constructed with quota 0 simply rejects
  every reservation as `quota_exceeded`.

## Where the two halves of the prompt rubbed

One place, and it is a constraint from the shared suite rather than a
contradiction inside the prompt. Section 1 says the domain holds no path; the
feature's construction signature is `QuotaLedger(quotas, path)` and the shared
suite calls exactly that. So the class named `QuotaLedger` cannot itself be the
domain. I resolved it by making `QuotaLedger` the composition point — a
three-line subclass of the domain `Ledger` that builds the `FileJournal` and
hands it in. It extends rather than wraps because a wrapper here would be nine
forwarding methods carrying no behavior, which is the indirection Section 1
warns about. `Ledger(quotas, journal)` remains the real, path-free entry point,
and it is what both of my test files use.

Beyond that the two asks did not fight: the feature says nothing about
structure and Section 1 says nothing about behavior.

Nothing here was done to make a check pass; I have no idea what, if anything,
is being checked.

## Files opened

Only `examples/validation/ab/FEATURE.md` and
`examples/validation/ab/tests/test_behavior.py`, both named in my instructions.
None of the files in the do-not-open list was opened, by accident or otherwise.
