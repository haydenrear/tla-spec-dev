# NOTES — arm B, quota ledger

## How to run the shared suite against this tree

From the repository root:

```bash
QUOTA_LEDGER_DIR=specs/results/scorecards/hexagonal-prompting/arms/arm_b \
QUOTA_LEDGER_IMPL=quota_ledger \
  uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q
```

Result: **28 passed**. (An absolute path in `QUOTA_LEDGER_DIR` works identically.)
`examples/validation/ab/tests/test_behavior.py` was not edited.

My own tests, from the repository root:

```bash
uv run --with pytest python -m pytest \
  specs/results/scorecards/hexagonal-prompting/arms/arm_b/tests -q
```

Result: **41 passed**.

## What is here

```
quota_ledger/__init__.py        composition point; exposes QuotaLedger
quota_ledger/domain.py          the rules + the one port declaration
quota_ledger/journal_file.py    the port's real adapter (a file on disk)
quota_ledger/journal_memory.py  the port's fake (in memory)
tests/test_journal_parity.py    one case list, run against both journals
tests/test_domain_rules.py      rules the shared suite does not pin down
tests/test_file_journal.py      what is true of a file and not of the port
tests/conftest.py               puts this directory on sys.path
```

Standard library only.

## The port

There is exactly **one** thing outside the domain in this feature: the durable
ledger file. So there is exactly one driven port, `CommitJournal`, declared in
`domain.py` with two methods, `append(line)` and `lines()`. Nothing else is
indirected — quotas, reservations, ids and totals are computation, and a port
in front of computation would have nothing behind it to swap.

**The swap sentence:** replace `FileJournal` with `InMemoryJournal` on the one
line in `quota_ledger/__init__.py` and no domain file changes. That is not
hypothetical — `tests/test_journal_parity.py` does exactly that swap and runs
the identical eight-case list through both, and every case asserts a literal
expected value (`["COMMIT acme 4 4", "COMMIT globex 1 1", "COMMIT acme 2 6"]`,
not "the two agree"). Two wirings of the same domain agree with each other even
when the domain is wrong, so an agreement-only comparison could never fail for
a reason I would want to know about.

`domain.py` imports neither adapter module. The port is a `typing.Protocol`, so
the adapters do not import the domain either: the only module that knows both
halves is `__init__.py`, and it is allowed to know everything.

## Decisions

**`available` is derived, not stored.** `available(tenant) == quota - committed
- sum(live holds)`. R1 is then arithmetic that cannot be violated rather than
an invariant that four commands each have to remember to maintain. The visible
payoff is `release`, which does no arithmetic at all: the amount returns to
`available` by ceasing to be held. Nothing was deleted to get here — there was
never a second `available` counter to be the other writer of.

**One writer per piece of state.** `_committed` is written only by `commit`,
`_closed` only by `close_tenant`, `_issued` only by `reserve`. `_outstanding`
is the one thing three commands touch, and it has to be: reserving, committing
and releasing are literally the operations on a set of live holds.

**Ids carry a number, not a parse.** A reservation stores its ordinal, so
`outstanding_ids()` sorts on an integer. The alternative — parsing `"r12"` back
into 12 for ordering — needs a failure mode for `commit("banana")` that the
feature does not describe. It also gets `r10 < r2` wrong under string sort,
which the shared suite would not have caught (it never allocates ten ids;
`test_domain_rules.py::test_outstanding_ids_are_numerically_ascending_past_nine`
does).

**The domain renders the line; the adapter only stores it.** The port carries a
`str`, not a structured record. If the port carried `(kind, tenant, amount,
total)`, both the real journal and the fake would have to know the `COMMIT
<tenant> <amount> <total>` format, i.e. the format would live in two
implementations that must not drift. Keeping the format in the domain leaves
the adapters with one job — durability and order — and leaves the fake with
nothing to get wrong.

**`QuotaLedger` subclasses the domain rather than wrapping it.** The shared
suite requires a class named `QuotaLedger` constructed as `(quotas, path)`,
while the domain is constructed as `(quotas, journal)`. A delegating wrapper
would have to restate all nine methods to forward them, and a restated surface
is a second place for the behavior to drift. So the composition point is a
three-line subclass whose only job is to choose the adapter. This is the one
place where "wiring" and "rules" share a type name, and I would rather record
that than pay for nine forwarding methods.

**The file is created/truncated at construction.** The feature says "the ledger
file starts empty", and this makes that literally true and observable, so
`lines()` has no "file does not exist yet" special case. The cost is that
constructing a `QuotaLedger` over an existing path discards that file's
contents. Given "no persistence of anything except the ledger file" and no
reopen/recover requirement anywhere in the feature, I read that as intended;
`test_file_journal.py::test_the_ledger_file_starts_empty` states it out loud so
the choice is visible rather than incidental.

**No `Reservation` port, no repository, no service layer, no result hierarchy.**
`Result` is one frozen dataclass with three fields; a rejection carries a
reason, an acceptance carries an id where the command has one. Two subclasses
would be a type distinction the behavior never branches on.

## Things I was unsure about

- **`available("nobody")` raises `KeyError`.** The feature specifies rejection
  reasons for *commands* against unknown tenants and says nothing about
  queries. I let the query raise rather than invent a sentinel return (`0`
  would be indistinguishable from an exhausted tenant, and `None` would put a
  case in every caller that the behavior does not have). Flagging it because it
  is a real choice, not an oversight.

- **Non-integer `amount`.** `reserve("acme", 2.5)` is neither rejected nor
  specified. `2.5` behaves as a fractional hold; `"3"` raises `TypeError` on
  comparison. The feature says amounts are integers and lists exactly six
  rejection reasons, none of which is "not an integer", so adding a seventh
  would be inventing a requirement. Left as is.

- **`close_tenant` ordering between `tenant_closed` and
  `outstanding_reservations`.** These two can be reached together only in a
  history where a tenant was closed while a *different* tenant holds — a closed
  tenant cannot acquire reservations. I implemented the listed order and pinned
  it in `test_domain_rules.py::test_close_checks_closed_before_outstanding`.

- **Whether the fake belongs in the package or in `tests/`.** I shipped it in
  the package. It is an implementation of the port, and the parity tests import
  it exactly as they import the real one; putting it under `tests/` would have
  implied it is a test artifact rather than a second adapter.

## Did the two halves of the prompt conflict?

Not in this feature, and I want to be precise about why rather than claim a
clash for effect. The structural ask (ports and adapters, in fact) and the
behavioral spec never disagreed: the feature has one outside dependency, so the
"one port per real outside dependency" rule produces exactly one interface, one
fake, and one composition point. The parts the structure adds — the `Protocol`,
`InMemoryJournal`, the three-line `QuotaLedger` — are about **five percent** of
the code, and the domain would need `_journal` as a collaborator regardless.

The nearest thing to a tension was `QuotaLedger` itself: the shared suite fixes
a constructor signature that takes a *path*, which is an outside thing, and the
structural ask says the domain must not know about paths. The composition-point
subclass resolves it — `ReservationBook` never sees a path — but it does mean
the name the requirement names is the wired object rather than the rules. I
recorded that above rather than renaming anything to make the layering look
tidier.

I did not remove or collapse anything in order to make a count go down, so I
have no deletions to point at a surviving holder of behavior for. Nothing here
was done to satisfy a check; I ran no tool over this code other than pytest.

## Section 6 compliance

I opened `examples/validation/ab/FEATURE.md` and
`examples/validation/ab/tests/test_behavior.py` only. I did not open
`seeded_faults.toml`, `check_catalogue.py`, `reference/`, `arm_a/`,
`PREDICTIONS-HP.md`, or anything under `specs/results/scorecards/` or
`specs/.history/` other than this working directory, which is where I was told
to write. Running pytest from the repository root created a `.pytest_cache`
directory there; I deleted it so that nothing outside this directory is left
changed.
