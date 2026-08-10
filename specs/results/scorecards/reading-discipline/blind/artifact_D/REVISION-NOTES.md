# REVISION-NOTES — quota ledger

A second pass over an implementation that already worked. **One structural
change, plus one test the change made necessary.** Everything else I looked at
is listed below with the reason it is still standing.

## The suite before I touched anything

Run first, as Section 4 asks:

```
QUOTA_LEDGER_DIR=<this dir> QUOTA_LEDGER_IMPL=quota_ledger \
  uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q
→ 28 passed in 0.04s
uv run --with pytest python -m pytest test_quota_ledger.py -q   → 37 passed in 0.30s
uv run --with pytest python mutation_check.py                   → 11/12 caught (M8 survives)
```

Green on arrival, and `mutation_check.py` reproduced the table in `NOTES.md`
line for line. After the revision: **28 passed, 39 passed** (37 + the 2 new
parametrisations), and the mutation table is byte-identical to the baseline.

---

## What I changed

### 1. Removed `self._held` — a stored per-tenant total that duplicated `_outstanding`

The original kept `_held: dict[tenant, int]` as a running sum, incremented in
`reserve` and decremented in both `commit` and `release`, read in exactly one
place: `available()`. Its comment gave the reason — "so `available` never has to
walk the outstanding table."

Why it is accidental structure: `_outstanding` already records every live
reservation with its tenant and amount, so `_held[t]` was, at every instant, a
second copy of `sum(r.amount for r in _outstanding.values() if r.tenant == t)`.
That is **the same decision made twice** — four write sites that had to be kept
in lockstep with a table that already held the answer. It is also the exact
duplication R1 is a rule *about*: R1 says available + held + committed == quota,
and the original expressed "held" twice, in two places that could disagree.

`available()` now derives the held sum. `reserve`, `commit` and `release` each
lose a line, and `commit` — which previously touched outstanding, held,
committed and the file — now touches three things instead of four.

**Where the behavior it carried now lives** (Section 1's first option):
`available()` at `quota_ledger.py:70-76` computes the identical quantity. The
equality is not a hope: `_held` was initialised to 0 for every tenant, increased
by `amount` on exactly the accepted-`reserve` path, and decreased by
`reservation.amount` on exactly the accepted-`commit` and accepted-`release`
paths — which are precisely the three places `_outstanding` gains or loses that
reservation. So `_held[t] == sum(...)` was an invariant of the original, and the
new code evaluates the right-hand side of that invariant directly.

**Evidence beyond "the tests still pass"** — because as Section 1 says, the tests
were written against the design I changed. I reconstructed the pre-revision
source and ran the two implementations side by side over random walks,
comparing every command's `(status, reason, reservation_id)` **and** the full
observable snapshot (`available`, `committed`, `is_closed`, `outstanding_ids`,
`ledger_lines`) after every single operation:

```
3000 walks x 60 ops, 3 tenants, quotas 0-40, amounts -2..12,
commit/release ids drawn from r1..r30 (so most are misses) -> divergences: 0
```

The same run also compares the exception raised by `available`/`committed`/
`is_closed` on an unknown tenant, since that is unspecified surface the original
happened to have: both raise `KeyError: 'nobody'`, and the derivation preserves
it because `self._quota[tenant]` is still the lookup that fails. (Script:
`../../m4probe/equiv.py` in my scratch area, not in the deliverable.)

**What it costs.** `available()` is now O(live reservations) rather than O(1),
and `reserve` calls it. I am stating that plainly rather than dismissing it. I
did not treat it as decisive because: the feature specifies no performance
requirement; `NOTES.md` records that the original's largest run was 12
simultaneous reservations and makes no performance claim either, so the stored
total was optimising a cost nobody had measured; and a duplicated
representation is paid for continuously in the reader's head, whereas this cost
is paid only at a size the feature explicitly puts out of scope. If a size
requirement ever appears, restoring the running total is a local change to one
function's inputs — and it should come back with a test that the two agree.

### 2. Added `test_ids_advance_even_when_outstanding_returns_to_empty`

Not a change I wanted; a change the revision **forced**, and the most important
thing in this document.

Removing `_held` flipped mutant **M4** ("ids are reused once a slot frees up",
which replaces `self._next_id += 1` with `self._next_id = len(self._outstanding)
+ 2`) from `caught` to `SURVIVED`. I stopped and chased it rather than shipping
the drop, because a revision that quietly lowers the suite's kill rate is
exactly the unreadable move Section 3 warns about.

What I found, by building both sources with M4 applied and running the suite
against each:

- **pre-revision + M4** → 1 failed: `test_rules_hold_after_every_operation_of_a_random_walk`, at the **R1** assertion.
- **post-revision + M4** → 37 passed. Nothing else in 37 tests noticed.

So the only test catching M4 was catching it **by accident**. Under id reuse,
`_outstanding[dup_id] = ...` silently overwrites the earlier reservation while
`_held += amount` still counted it, and R1 tripped on the resulting desync
between two representations of the same number. It was never testing "ids are
never reused"; it was testing that the duplicate stayed in sync — a property
that only existed because of the duplication. Once held is derived, the
implementation is self-consistently wrong under M4 and R1 holds.

The three id tests that were already there don't reach it either: none of them
lets `outstanding` drain to empty and refill, and while it is non-empty
`len(outstanding) + 2` happens to agree with the true counter.

The new test does it directly, against the feature clause rather than against a
representation: reserve/resolve three times in a row, parametrised over both
`release` and `commit`, and assert the ids are `r1, r2, r3`. Under M4 the third
is a second `r2`. Verified: it fails on post-revision + M4 (both parameters),
passes on the real implementation. `mutation_check.py` is back to 11/12 caught,
identical to the baseline table.

I take a second lesson from this and will not pretend otherwise: **the original
suite's M4 kill was weaker than its table suggested**, and only removing the
duplication exposed that. Redundant state does not just cost maintenance — it
can lend a test suite kill credit it hasn't earned.

### Tests deleted or rewritten

**None.** All 37 original tests are present and passing, unedited. Nothing in
`test_quota_ledger.py` referenced `_held` (I grepped: it appeared in
`quota_ledger.py` only, 5 times, all removed or replaced), and neither the shared
suite nor `mutation_check.py` touches implementation internals. All twelve
mutation anchors in `mutation_check.py` still resolve — I kept the `# No ledger
write` comment in `release`, which is M5's anchor, for that reason.

---

## What I looked at and left standing

**`_committed` alongside the ledger file.** The obvious next "duplication":
`committed(t)` is memory, and the same number is recoverable from the file's
COMMIT lines. Left, deliberately, and it is the interesting contrast with
`_held`. R2 is the requirement *that these two agree*; a rule of the form "X
agrees with Y" needs an X and a Y. `NOTES.md` makes the same point about
`ledger_lines()` re-reading the file. Deriving `committed` from the file would
make R2 true by construction and delete the only check with teeth. `_held` had
no such counterpart — nothing asserted that `_held` and `_outstanding` agreed,
which is what let M4 hide inside the gap between them.

**The six reason constants.** `UNKNOWN_TENANT = "unknown_tenant"` and friends
technically match "indirection with exactly one thing behind it" — each name has
one literal behind it and nothing ever replaces it. Left standing: inlining them
removes no decision (the choice of reason is still made once per branch), it is
a rename in the direction Section 1 forbids, and there is a real if modest
argument for them — R4 names a closed vocabulary of six, and the module lists
those six in one place.

**`_accepted` / `_rejected`.** Two-line constructors over `Result`. Six and ten
call sites. Not indirection with nothing behind it; inlining them would add
`status="rejected"` sixteen times. Taste, either way. Left.

**`get` + `del` in `commit`/`release`, which `pop(id, None)` would collapse.**
One line shorter and one dict lookup cheaper, and I decided against it: `pop`
mutates before the rejection test. It is a no-op on the rejection path, so R4
still holds — but R4 ("a rejection changes nothing") is precisely the property a
reader needs to be able to check locally, and buying one line by making the
state change happen before the check reads worse than the duplication costs. The
duplicated three-line preamble is also what makes the identical rejection rule
read identically in both commands.

**The unused `reservation` binding in `release`.** After the change, `release`
binds `reservation` only to test it against `None`; `if reservation_id not in
self._outstanding` would be tighter. Left for the symmetry above — the two
commands should decide `unknown_reservation` the same way, visibly.

**Three parallel dicts keyed by tenant** (`_quota`, `_committed`, `_closed`;
`_held` was the fourth). Folding them into one record per tenant is a lateral
representation change: same distinctions, same number of updates, just moved.
Section 1's test is which distinctions the behavior makes, and this changes
none of them. Also `_closed[t]` raising `KeyError` for an unknown tenant is
current behavior; a `set` of closed tenants would silently return `False`
instead, which is a behavior change on unspecified surface.

**`_ledger_path.parent.mkdir(parents=True, exist_ok=True)` in `__init__`.** A
candidate for machinery the feature doesn't ask for — the suite always passes an
existing `tmp_path`. Left, because removing it *is* a behavior change: a caller
passing a nested path succeeds today and would raise afterwards. Section 1 is
unambiguous that behavior stands even where I might not have written it.

**`Reservation` as a frozen dataclass, `Result` as a frozen dataclass,
`_append`, the `outstanding_ids` numeric sort key, the truncate-on-construct in
`__init__`, the rejection orders in `reserve` and `close_tenant`.** Each carries
a distinction the feature makes, or a documented ambiguity resolution I have no
standing to revisit. Left, untouched.

---

## Unclear in the original, and things I was unsure about

- **The `_held` comment stated a rationale the notes elsewhere disclaim.** The
  field said it existed "so `available` never has to walk the outstanding
  table", while `NOTES.md` says under "Things I could not check" that no run was
  large enough for performance to show. That contradiction is what made the
  field a candidate rather than a design choice I should leave alone. I could be
  wrong about the author's intent; if the running total was there for a size
  requirement that exists outside the feature file, this change is wrong and
  should be reverted — but then it needs a test that `_held` and `_outstanding`
  agree, which is the check whose absence let M4 through.
- **I did not resolve, and did not touch, the six items in `NOTES.md`'s
  "Ambiguities" section** — non-integer amounts accepted (`COMMIT acme 2.5 2.5`),
  tenant names with spaces producing unparseable lines, two ledgers on one path
  wiping each other, `KeyError` on unknown-tenant queries, and the unobservable
  clause order in `close_tenant`. Per Section 5 I kept exactly what the code
  does. I read the first three as real defects waiting for a requirement, not as
  violations of the feature as written; I am recording that opinion here and
  changing nothing, as Section 1 instructs.
- **`close_tenant`'s clause-2/clause-3 order remains unobservable** (M8 still
  survives both suites, 0/400 differential). I did not try to write a test for
  it. `NOTES.md` already argues from an exhaustive search that no reachable
  state distinguishes the two orders; I did not re-derive that, and I did not
  restructure the check to look tidier at the cost of matching the feature's
  declared order.
- **`NOTES.md` I left as the original author wrote it.** Its structural claim —
  "`available` is derived rather than stored" — is still true and now more so.
  Its mutation table still reproduces exactly. Editing someone's record of what
  they did to make my pass look tidier seemed like the wrong move; this file is
  the record of the second pass.

## Disclosures

- **Files I opened under `examples/`:** `examples/validation/ab/FEATURE.md` and
  `examples/validation/ab/tests/test_behavior.py`. Both are named in my work
  order. Nothing else under `examples/` was opened, read, grepped, or executed.
- I ran `ls -la` on `examples/validation/ab/`, so I **saw the file names** listed
  in Section 6 — `seeded_faults.toml`, `check_catalogue.py`, `reference/`,
  `reference_ports/`, `arm_a/`, `arm_b/`, `arm_c/`, and others — in the
  directory listing. I opened none of them and know nothing of their contents.
  Disclosed because a listing is arguably "opening the directory", and Section 6
  says the disclosure costs nothing. (`NOTES.md` records the original author
  making the same disclosure.)
- `test_behavior.py` and `FEATURE.md` are unmodified; `git status` on
  `examples/` is empty.
- No dependencies added. `quota_ledger.py` still imports only `dataclasses`,
  `pathlib`, `typing`.
- Files changed in this directory: `quota_ledger.py` (the revision),
  `test_quota_ledger.py` (one test added, nothing removed or edited), and this
  file. `NOTES.md` and `mutation_check.py` are untouched.
