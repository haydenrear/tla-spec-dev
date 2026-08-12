# NOTES — quota ledger

## What I built

A `quota_ledger` package in this directory. Four files:

| File | What it is |
|---|---|
| `quota_ledger/domain.py` | The rules. Declares the `Journal` port, the `Result` and `Reservation` values, and the `Ledger` class that holds all the behavior. |
| `quota_ledger/file_journal.py` | `FileJournal` — the real driven adapter. The only place that knows about paths, encodings and newlines. |
| `quota_ledger/memory_journal.py` | `InMemoryJournal` — a working in-memory implementation of the same port. |
| `quota_ledger/__init__.py` | The composition point, and the `QuotaLedger` entry point the feature names. |

Tests of my own are in `tests/test_ledger.py` (53 cases).

### Running the shared suite

Module path is `quota_ledger`; it needs this directory on `sys.path`, which the
shared suite reads from `QUOTA_LEDGER_DIR`:

```bash
cd <path><worktree>
QUOTA_LEDGER_DIR=<this directory> QUOTA_LEDGER_IMPL=quota_ledger \
  uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q
```

28 passed, file unedited. My own suite: `uv run --with pytest python -m pytest
tests/test_ledger.py -q` from this directory — 53 passed.

## The port

One real outside dependency: the durable, append-only ledger file. One port,
`Journal`, two methods:

```python
def append(self, record: str) -> None: ...
def records(self) -> list[str]: ...
```

Named for the need — a permanent record that only grows — not for the file that
happens to satisfy it. Its full contract is written on the Protocol in
`domain.py`: append puts one record at the end, `records()` gives back exactly
what was appended in that order and nothing else, a fresh journal is empty, and
the returned list belongs to the caller.

**The swap, in one sentence:** replace `FileJournal(ledger_path)` with
`InMemoryJournal()` in `quota_ledger/__init__.py` and no domain file changes.
That is one line in the one module allowed to know about both sides; `domain.py`
imports only `__future__`, `dataclasses` and `typing`, and there is a test that
parses its import statements and asserts exactly that, because "does not
import" is a claim about the file rather than about intent.

Nothing else is indirected. There is no port in front of the arithmetic, no
repository interface over the reservations dict, no service layer. The
reservations live in a dict inside the domain because they are not outside it.

### The line format is in the domain, on purpose

`COMMIT <tenant> <amount> <total>` is behavior — the shared suite asserts those
exact strings, and R2 is a statement about what those lines say. So the two
f-strings live in `Ledger.commit` and `Ledger.close_tenant`, and the port
carries the finished record. The alternative (a port that takes a
`CommitRecord` and lets each adapter render it) would force the same format
into `FileJournal` and `InMemoryJournal` both, which is duplication across the
boundary the port exists to protect. The file adapter owns only what is truly
the file's: the trailing newline it has to add on write and strip on read.

## Decisions

**`available` is derived, not stored.** It is
`quota - held - committed`, computed on each call. Three commands would
otherwise have to write it and remember to keep R1 true; as it stands R1 is
true by construction and cannot drift. It also makes the feature's trickiest
sentence — "committing does not give the hold back" — fall out rather than be
maintained: commit moves an amount from `_outstanding` to `_committed`, and a
subtraction of both does not notice. This is a *derivation*, not a deletion:
the behavior is still asserted, by name and value, in
`test_commit_writes_one_line_and_keeps_the_amount_deducted` and in the shared
suite's `test_commit_moves_the_hold_into_committed_and_writes_one_line`.

That leaves three pieces of written state: `_outstanding`, `_committed`
(written by `commit` only), `_closed` (written by `close_tenant` only), plus
the `_issued` id counter (written by `reserve` only, and only on acceptance, so
a rejection does not burn an id — tested).

**`outstanding_ids()` is `list(self._outstanding)`.** Ids are allocated
ascending, never reused, and a dict preserves insertion order, so insertion
order *is* ascending order and no sort is needed. This is the one place I
relied on a language guarantee instead of restating the requirement, so there
is a test (`test_outstanding_ids_stay_ascending_past_ten`) that goes past `r10`,
where a naive lexicographic sort would put `r10` before `r2`.

**Both journals are exercised by one case list.** Every behavioral test in
`tests/test_ledger.py` runs twice through a parametrized fixture — once wired
to `FileJournal`, once to `InMemoryJournal` — and each asserts a literal
expected value (`["COMMIT globex 1 1", "COMMIT acme 4 4", ...]`), never that
the two wirings agree with each other. No case had to be written for only one
of them. Two file-specific tests sit outside that list, because they are about
the file rather than about the rules: that the bytes on disk are one record per
line, and that constructing a journal starts it empty.

## Where the feature file and the architecture ask conflicted

They conflict in exactly one place, and it is worth recording.

FEATURE.md: "Construction takes a mapping of tenant name to integer quota, and
a **path** for the ledger file", and the shared suite constructs
`QuotaLedger(dict(QUOTAS), tmp_path / "ledger.txt")`. Section 1: the domain
holds "no file handle, no path".

Resolved as instructed — the feature wins on behavior, the structure ask wins
on structure. The public `QuotaLedger` takes the path and is therefore *not*
the domain object: it is a factory function in the composition module that
turns the path into a `FileJournal` and hands that to `Ledger(quotas,
journal)`. The rules never see a path; the name and signature the feature
requires are preserved exactly.

The alternative would have been a `QuotaLedger` class that takes a path and
delegates all nine methods to an inner `Ledger`, which is nine methods of
duplication at the boundary for no behavior. A factory function named like a
class is slightly unusual to read; I took that over the duplication, and it is
the only place where the shape of the code is driven by a name the feature
fixed.

## Unsure / unspecified — interpretations I picked

1. **Queries on an unknown tenant.** `available("nobody")`, `committed`,
   `is_closed` are unspecified for tenants that do not exist. `available` and
   `committed` raise `KeyError`; `is_closed` returns `False`. I did not add an
   unknown-tenant result to the query side, because the feature gives the
   query column no status/reason vocabulary and only commands reject.
2. **An existing file at the path.** "The ledger file starts empty", so
   constructing a `FileJournal` truncates. There is no reopen-and-resume
   behavior in the feature (nothing is persisted except the ledger, and nothing
   reads it back at construction), so I did not invent one.
3. **A failed durable write.** `commit` and `close_tenant` update memory and
   then append. If the append raised, memory would have moved without a
   durable record. The feature specifies no failure or atomicity semantics
   (R4 is about *rejections*, which never reach the journal at all), so I did
   not build a rollback or a write-ahead ordering. This is the one place I can
   name where R2 is not enforced by construction.
4. **Non-integer amounts.** `reserve("acme", 2.5)` is not addressed by the
   feature. `amount < 1` and the arithmetic accept it and it would flow into
   the ledger line. I did not add a type check, which would be a seventh
   rejection reason and the vocabulary is fixed at six.

I found no self-contradiction inside FEATURE.md itself.

## Files I did not open

None of the listed files were opened: `seeded_faults.toml`,
`check_catalogue.py`, `reference/`, `this artifact/`, `<predictions-file>`, and anything
under `<results-path>` or the history snapshots. I also did not open
`examples/validation/ab/README.md`, which is not on the list but sits in the
same directory and looked likely to describe the comparison. I read exactly two
files in the repository: `FEATURE.md` and `tests/test_behavior.py`. I wrote
nothing to the repository; `git status` there is clean.
