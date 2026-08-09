# REVISION NOTES — quota ledger

## Outcome

**I changed nothing.** No file under `quota_ledger/` or `tests/` was edited,
deleted, added, or renamed. The only new file in this directory is this one.

Section 1 says that is a real and acceptable outcome and that a manufactured
change is worth less than an accounted-for absence of one. I went looking for
the six kinds of accidental structure it names, found candidates for four of
them, and concluded that each candidate is either carrying a distinction the
behavior makes, or sits inside a structural choice `FEATURE.md` explicitly
leaves free — which Section 1 says stands. The rest of this file is that
accounting, candidate by candidate, so the conclusion can be checked rather
than believed.

## Suite state

Run before touching anything, from the repository root:

```
QUOTA_LEDGER_DIR=<this directory> QUOTA_LEDGER_IMPL=quota_ledger \
  uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q
```

- **Before:** 28 passed. Green on arrival, so the pass is measuring the right
  thing.
- **After:** 28 passed. Same file, unedited, and the implementation it ran
  against is byte-identical.
- The implementation's own suite: 39 passed before, 39 passed after. No test
  was deleted or rewritten, so Section 3's "name any test you removed" has
  nothing to report.

I also ran the artifact's own 39 tests under branch coverage as an objective
check for structure nothing reaches:

```
quota_ledger/__init__.py         10 stmts   0 miss   0 branch   0 partial  100%
quota_ledger/domain.py           86 stmts   0 miss  18 branch   0 partial  100%
quota_ledger/file_journal.py     11 stmts   0 miss   0 branch   0 partial  100%
quota_ledger/memory_journal.py    8 stmts   0 miss   0 branch   0 partial  100%
```

Full statement *and* branch coverage means there is no unreached line and no
untaken branch anywhere in the package. That does not prove nothing is
accidental — a well-tested useless field is still useless — but it rules out
the cheapest kind of finding, which is why I went looking at the level of
distinctions instead.

## What I looked at, and why each was left standing

### 1. The `Journal` port — the loudest target, and the one I am most confident about

`domain.py` declares a `Journal` Protocol with `append(line)` / `lines()`, and
there are two adapters behind it. This is the first thing a reviser is tempted
to collapse: the feature writes lines to one file, so "an interface for one
file" is the shape of over-engineering.

It is not that shape here, on the prompt's own test. Section 1's bullet is *an
interface with exactly one thing on the other side of it that nothing ever
replaces, and no concrete alternative you can name*. All three clauses fail:
there are two implementations, `tests/test_journal_parity.py` actually
substitutes one for the other across twelve parametrised cases, and further
alternatives are nameable (SQLite, a socket, an in-process buffer).

And independently: `FEATURE.md` lists "whether the durable side is reached
through an interface, a callable, or directly" under **Deliberately
unspecified**. Section 1 says that where the existing design makes a structural
choice the feature leaves free, that choice stands and I simplify within it.
Collapsing the port would also require deleting `memory_journal.py` and
rewriting the parity suite and the `test_ledger.py` fixture — deleting the
tests that would have caught the change, which Section 3 calls the one move
that makes a revision unreadable.

**Left standing.** No behavior at risk; nothing removed.

### 2. `MemoryJournal` living in the package rather than in `tests/`

Related but distinct: the second adapter is only ever constructed by tests, so
one could argue it is test scaffolding shipped in the production package.

Moving it to `tests/` would not remove any machinery — the same class, the same
two methods, the same call sites — it would only change which directory the
file sits in and break two import lines. That is a file move, not a
simplification, and it is close enough to "renaming for taste" that it would
bury a real finding if I had one. It is also the concrete thing that makes
candidate 1 a real port rather than a decorative one.

**Left standing.**

### 3. `QuotaLedger` as a two-line subclass of `Ledger`

`__init__.py` defines `QuotaLedger(Ledger)` whose entire body is
`super().__init__(quotas, FileJournal(ledger_path))`. A wrapper with exactly one
thing behind it.

The distinction it carries is real and is forced by two things at once: the
shared suite constructs `QuotaLedger(quotas, path)`, and the domain holds no
path. Something has to turn a path into a journal, and this is the smallest
thing that can. The alternatives are all the same size or larger: a factory
function is the same mechanism under a different keyword; letting
`Ledger.__init__` take a path would move the filesystem into the domain, which
is undoing the design's free structural choice rather than simplifying within
it; a forwarding wrapper would be nine methods carrying no behavior, which is
the indirection the bullet actually warns about.

**Left standing.**

### 4. The duplicated tenant guards in `reserve` and `close_tenant`

Both commands open with the same two lines:

```python
account = self._accounts.get(tenant)
if account is None:  return Result.reject("unknown_tenant")
if account.closed:   return Result.reject("tenant_closed")
```

This is the best candidate in the file for "the same decision made twice", and
I spent the most time on it. I wrote out the extraction — a
`_tenant_rejection(tenant) -> str | None` helper — and did not keep it, for
three reasons:

- It is not one rule split across two places. `FEATURE.md` states the rejection
  order **twice, separately**, once under `reserve` and once under
  `close_tenant`. They coincide today; nothing says they must move together. A
  helper would assert a coupling the requirement does not make.
- It removes four lines and adds six, and the six introduce a second way to
  carry a rejection reason (a bare `str | None` alongside `Result`) — a
  representation the program otherwise does not have.
- The order of checks is behavior here (Section 1 names "the order of checks"
  explicitly as a thing not to change), and the order is easier to verify
  against the feature when each command states its own sequence top to bottom.

**Left standing.** If a reviewer disagrees with one item in this file, I expect
it to be this one; the argument above is the whole of my reasoning and it is a
judgment call, not a proof.

### 5. `Result.accept` / `Result.reject` classmethods

Two classmethods that look like aliases of the constructor — `Result.accept()`
is `Result()`, `Result.reject(r)` is `Result(r)`.

They are not pure aliases: between them they are the only two ways the code ever
builds a `Result`, and neither one offers the "reason **and** reservation_id"
combination. So they encode "a rejection carries no id, an acceptance carries no
reason" in the construction surface, which is a distinction the behavior makes
and which `tests/test_ledger.py::test_a_rejected_result_carries_no_reservation_id`
reads. Removing them would push that invariant onto every call site.

**Left standing.**

### 6. `Result.status` as a derived property

Already derived from `reason` rather than stored. There is nothing to collapse
here — a stored `status` would be the second writer of one fact, and it isn't
present. Noted only because it is the kind of thing this pass is looking for and
it was already handled.

**Nothing to do.**

### 7. `outstanding_ids()` sorting by `_issue_order`

`outstanding_ids` returns `sorted(self._holds, key=_issue_order)`, supported by
a five-line helper. Ids are allocated strictly increasing and dicts preserve
insertion order, so the keys are *already* ascending. I confirmed this
empirically, including across releases that leave gaps:

```
insertion order: ['r1','r2','r4','r5','r6','r8','r9','r10','r11','r12']
sorted         : ['r1','r2','r4','r5','r6','r8','r9','r10','r11','r12']
```

So the sort is provably redundant, and deleting it keeps both suites green.
I did not delete it, and this is exactly the case Section 1's warning about
counts is about. The sort is not redundant *machinery*; it is the query's
independence from two facts that live elsewhere — that ids are numerically
monotonic in issue order, and that `dict` preserves insertion order. Removing it
would make `outstanding_ids` silently wrong the day either of those changes,
and the two-part accounting would have to read "the behavior is now carried by
an invariant in a different method", which is a worse place for it to live than
where it is. The line count would have gone down and the design would have got
worse.

**Left standing.**

### 8. `_held_by` materialising a list

`_held_by` builds a list that `available` immediately sums and `close_tenant`
immediately tests for emptiness. Both callers want less than a list.

That is a performance observation, not a structural one — the distinctions the
program makes are unchanged either way — and Section 1 is explicit that smaller
is not the goal. Changing it would be noise.

**Left standing.**

### 9. `committed` and `closed` stored in memory while also derivable from the journal

`is_closed(t)` could be `any(line.startswith(f"CLOSE {t} ") for line in
journal.lines())`, and `committed(t)` could be a sum over that tenant's `COMMIT`
lines. That would make R2 and R3 true by construction and delete two fields.

It would also put a parser for the ledger's own line format inside the rules,
turn three of the five queries into reads of the durable side, and make the
domain depend on the journal's text encoding in both directions instead of one.
That is a different architecture, not a simplification of this one. The existing
design's answer — `commit` is the single writer of `committed` and appends the
matching line in the same step — keeps R2 in one place already.

**Left standing.** (This was already reasoned about in `NOTES.md`; I checked the
reasoning rather than taking it, and agree with it.)

### 10. Smaller items checked and dismissed

- **`_Account` / `_Hold` dataclasses.** Every field is read: `quota` and
  `committed` by `available`, `closed` by `is_closed` and two guards, `tenant`
  and `amount` by `available`, `commit` and `_held_by`. No field is written-only.
  `_Hold` already carries no copy of its own id.
- **`_issued`.** Cannot be derived from `len(_holds)` — ids are never reused, so
  the counter has to survive removals. Genuinely needed state.
- **Blank-line filtering in `FileJournal` only.** It is an artifact of the
  trailing newline in a file; `MemoryJournal` has no such artifact and so needs
  no filter. Hoisting it into the domain would be one rule made to serve one
  adapter's storage detail.
- **`Journal` re-exported from `__init__.py` but imported by nothing.** The one
  genuinely unread name I found. It is a type, exported so a third-party journal
  can annotate against it; removing it narrows the public surface, which is a
  behavior-adjacent change for no structural gain. Too small to be a finding.
- **`reserve` fetching `account` and then calling `self.available(tenant)`,
  which fetches it again.** A local, not a duplicated decision.
- **Docstrings restating `NOTES.md` rationale.** Prose duplication, not
  structural duplication. Trimming it is taste.

## Behavior I think is questionable, and left exactly as it is

Section 1 says to report these and not correct them. All three are already
recorded in `NOTES.md`; I agree with leaving them, and changed none of them.

- **Queries for an unknown tenant raise `KeyError`.** `available("nobody")`,
  `committed("nobody")` and `is_closed("nobody")` all raise. `FEATURE.md`
  specifies rejection reasons for commands only and is silent on queries, so
  there is no specified answer to converge on.
- **Non-integer amounts.** `reserve("acme", 3.0)` is accepted and writes
  `COMMIT acme 3.0 3.0` to the durable ledger. The feature says "integer quota"
  and "amount is less than 1", and never says amounts are integers, so a type
  check would be added behavior.
- **`FileJournal` truncates a pre-existing file at construction.** "The ledger
  file starts empty" is read as truncation. The other reading — append to what
  is there — would require reading prior state back into memory, which the
  feature puts out of scope. This is the closest thing to an ambiguity in the
  feature and I kept what the code does, per Section 5.

## Unclear, and things I was unsure about

- **"Ascending" in `outstanding_ids()`.** Ambiguous past nine reservations,
  since `"r10" < "r2"` as strings. The code reads it as issue order. I agree,
  but it is genuinely underspecified and both readings pass the shared suite
  only because it never allocates ten ids.
- **`tests/test_ledger.py::test_the_domain_module_does_not_import_its_adapters`
  asserts `"journal_" not in source`.** That substring cannot occur in any of
  the module names it is guarding against (`file_journal`, `memory_journal`),
  which are checked on the next line anyway, so the assertion appears to match
  nothing. I left it: it is a test, it passes, and it guards a structure I did
  not remove — editing a passing test to make a stylistic point is not a
  simplification and would only obscure the fact that I changed no code.
- **The one thing I would want a second opinion on** is candidate 4, the
  duplicated tenant guards. I can construct a reading where extracting them is
  the right call. I did not take it because the feature states the ordering
  twice and the extraction trades four lines of duplication for a second,
  parallel way of representing a rejection.

## Files opened

Only:

- `examples/validation/ab/FEATURE.md`
- `examples/validation/ab/tests/test_behavior.py` (run, not read or edited)
- everything inside this working directory (`NOTES.md`, `quota_ledger/`,
  `tests/`)

Nothing on the Section 6 do-not-open list was opened, by accident or otherwise.
I did not open `arm_a/`, `arm_b/`, `arm_c/`, `seeded_faults.toml`,
`check_catalogue.py`, `reference/`, `reference_ports/`, either `PREDICTIONS-*`
file, or anything under a `scorecards/` directory. I listed the contents of
`examples/validation/ab/` (directory names only, no file contents) while
orienting, which showed those paths exist; I read none of them.
