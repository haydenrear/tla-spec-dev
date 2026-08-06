# NOTES

## What I built

A `QuotaLedger` implementing the feature in `examples/validation/ab/FEATURE.md`,
laid out as:

```
quota_ledger/
  __init__.py            composition root: public QuotaLedger(quotas, path)
  domain.py               QuotaBook (the domain) + Result
  ports.py                DurableLedger protocol -- the one driven port
  adapters/
    file_adapter.py       FileLedgerAdapter -- the real adapter (a file on disk)
    memory_adapter.py     InMemoryLedgerAdapter -- the fake, used in tests
tests/
  test_port_conformance.py    same case list run against real and fake adapter
  test_domain_port_swap.py    same command scenarios run against QuotaBook
                               wired to real vs. fake, asserting identical
                               externally observable results
  test_acceptance_extra.py    rejection-order edge cases, id-allocation and
                               ordering details, a ledger-file-on-disk check
```

Import path for the shared suite: `quota_ledger` (a package, at the root of
this directory).

```
QUOTA_LEDGER_DIR=<this directory> QUOTA_LEDGER_IMPL=quota_ledger \
  uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q
```

28 passed. My own suite (`uv run --with pytest python -m pytest tests/ -q`
from this directory) is 11 more, all passing.

## The one real outside dependency, and the one port

The only thing outside the domain's control is the durable ledger file. I
declared exactly one port for it, `DurableLedger`, in the domain's own
vocabulary: `append_line(line)` and `lines()`. Two methods, named for what the
domain needs (remember this, forever, in order) rather than for "file" or
"disk".

`QuotaBook` (`domain.py`) depends only on that protocol. It holds no path, no
file handle, no clock. It does not import `adapters/file_adapter.py` or
`adapters/memory_adapter.py` -- neither module appears anywhere in
`domain.py` or `ports.py`.

The swap sentence: replace `FileLedgerAdapter` with `InMemoryLedgerAdapter`
(or a database-backed one, or anything else that can append a line and read
all of them back in order) and no file under `quota_ledger/domain.py`
changes. `tests/test_domain_port_swap.py` runs identical command scenarios
against `QuotaBook` wired to each adapter and asserts every query -- not just
`ledger_lines()` -- comes out identical. `tests/test_port_conformance.py` runs
the same case list against both adapters directly, at the port boundary.

I did not add a port for anything else. Reservation storage, the tenant map,
id allocation -- all pure computation, all inside `QuotaBook`, nothing to
swap underneath any of it. A port there would be indirection with nothing
behind it.

## Where the composition point sits, and why it isn't a layer

`FEATURE.md` fixes `QuotaLedger`'s constructor to `(quotas, ledger_path)` --
a path, not a port object. That signature *is* the real outside dependency,
baked into the public API by the spec itself. So the composition root
(`quota_ledger/__init__.py`) is the one place, other than the adapters
themselves, that imports both the domain and a concrete adapter: its
constructor builds a `FileLedgerAdapter(ledger_path)` and hands it to
`QuotaBook`. Every command and query on the public `QuotaLedger` is a
straight one-line delegation to `QuotaBook`.

I considered folding `QuotaBook` and `QuotaLedger` into one class and having
its constructor build the adapter directly. I didn't, because then the class
holding the domain rules would import the module that implements its own
port, which is exactly the thing Section 1 says not to do ("not 'does not
use' -- does not import"). Keeping them separate costs one file and one class
that is pure delegation; the alternative buys nothing back except a smaller
file count, and a smaller file count is not itself a better design.

## Simplicity choices -- what I did *not* add

- **No `available` field.** `available(tenant)` is computed as
  `quota - held - committed` on every call, not stored and kept in sync by
  every command. Storing it would be one more field every one of `reserve`,
  `commit`, and `release` has to update correctly, for a value nothing needs
  faster than an integer subtraction. It also makes conservation (R1) true by
  construction rather than an invariant three separate writers have to
  maintain by hand.
- **No separate "reservation" class/aspect module.** A reservation is a
  `(tenant, amount)` tuple keyed by id in one dict. `close_tenant`'s
  outstanding-reservations check is a one-line scan of that dict's values;
  splitting reservation-tracking into its own class would add a boundary with
  only one real caller on each side of it.
- **No result subclasses per command.** One `Result` dataclass
  (`status`, `reason`, `reservation_id`) covers all four commands. `reason`
  and `reservation_id` are `None` where the command in question never sets
  them; that's a smaller surface than four bespoke result types for the same
  three fields.
- **`outstanding_ids()` returns dict-insertion order**, not a sort. Ids are
  assigned strictly increasing and a dict key is never reinserted after
  being deleted (commit/release always remove it for good), so insertion
  order already is ascending numeric order. Sorting on top of that would be
  work that recomputes something already true.

## Ambiguities and decisions

- **FEATURE.md doesn't say whether `is_closed`, `available`, etc. on an
  unknown tenant should raise or what they should return.** The shared suite
  never calls a query with an unknown tenant, so I left it as a `KeyError`
  from the underlying dict rather than inventing a sentinel return value --
  adding a defined-but-unspecified behavior here would be answering a
  question the feature doesn't ask.
- **Whether the file adapter should hold the file open across calls or
  reopen it each time.** I reopen for every `append_line`/`lines()` call
  (open, write or read, close). The feature makes no durability claim beyond
  "append-only" and there's no concurrency in scope (explicitly out of scope
  per FEATURE.md), so a long-lived handle would only add a resource lifetime
  to manage for no behavior anyone can observe.
- Section 1 and the feature file did not conflict for this feature: the
  feature specifies behavior only, and nothing in it forced a structure that
  fights ports-and-adapters or the simplicity test. No note of a conflict is
  needed beyond this one.

## Disclosure

I did not open any file in Section 6's list (`seeded_faults.toml`,
`check_catalogue.py`, `reference/`, `arm_a/`, `PREDICTIONS-HP.md`, or
anything under `specs/results/scorecards/` /
`specs/.history/*/closed-snapshot/results/scorecards/`). I did read
`examples/validation/ab/tests/test_behavior.py` (not on that list, and
explicitly the file I'm required to pass unchanged) to get the exact
constructor/method signatures and result-attribute names right.
