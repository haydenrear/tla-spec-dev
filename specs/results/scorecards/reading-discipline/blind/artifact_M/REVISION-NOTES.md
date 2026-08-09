# REVISION NOTES — quota ledger

## State on arrival

Green, before I touched anything:

```
QUOTA_LEDGER_DIR=<...>/subjects/artifact_M QUOTA_LEDGER_IMPL=quota_ledger \
  uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q
# 28 passed

cd <...>/subjects/artifact_M && uv run --with pytest python -m pytest test_quota_ledger.py -q
# 21 passed
```

After the revision: **28 passed** (shared suite, unedited) and **22 passed**
(the implementation's own tests — all 21 originals still present and passing,
plus one I added). No behavior changed: no result, reason, check order, ledger
byte, or query value is different.

---

## What I changed

One change, in one place: the tenant record carried two numbers that were not
state. Both are gone. Everything else in the file is as I found it.

### 1. Removed `_Tenant.outstanding`, the live-reservation count

It was incremented in `reserve`, decremented in `commit`, decremented in
`release`, and read in exactly one place — the `outstanding_reservations` guard
in `close_tenant`.

**Where the behavior it carried now lives:** in `close_tenant`, directly —

```python
if any(held.tenant == tenant for held in self._reservations.values()):
    return Result.rejected(Reason.OUTSTANDING_RESERVATIONS)
```

The rejection is unchanged in reason, in position (still third, after
`unknown_tenant` and `tenant_closed`), and in effect. It is covered by
`test_behavior.py::test_close_rejects_while_a_reservation_is_outstanding` and
`::test_close_is_allowed_once_the_reservation_is_resolved`, by
`test_quota_ledger.py::test_a_released_reservation_unblocks_close_but_a_committed_one_also_does`,
by the 600-step random sequence, and by the new test described below.

**Why it was accidental structure and not state:** "this tenant holds live
reservations" is already recorded in `self._reservations`, which is also what
`outstanding_ids()` returns. The count was a second representation of that same
fact, kept in step by hand at three mutation sites. It made one rule — a
reservation is live from `reserve` until it is committed or released — something
that had to be written correctly in four places instead of one, and nothing
could have told the two representations apart if they had drifted: the
divergence would surface only as a wrong `close_tenant` result. The original
notes give the reason for it plainly ("so `close_tenant` can answer 'does this
tenant hold anything' without scanning the reservation table"), and that is a
speed argument, not a behavior one. `close_tenant` now scans; the feature states
no performance requirement, closes are rare, and the scan is over the live
reservations only.

### 2. Removed `_Tenant.quota`

**The behavior is gone, and I believe that is correct, because there was none.**
This is the second of the two accountings the ask allows, and I want to be
explicit that I am using it rather than pointing at a replacement.

`quota` was written once at construction, from the same argument that seeded
`available`, and then never read: nothing branched on it, asserted it, returned
it, or wrote it again. No query exposes a tenant's quota, so no observable
distinction depended on it. R1 names quota, but R1 is checked by the tests
against the `quotas` mapping *they* passed to the constructor
(`test_behavior.py::test_r1_conservation_holds_through_a_mixed_sequence`, and
`test_quota_ledger.py` line ~287) — not against this field. So no test loses a
reader either. I could not name a concrete reader, so by the ask's own test it
was bookkeeping.

The result of both removals: every field of `_Tenant` is now exactly one query's
answer — `available` → `available()`, `committed` → `committed()`, `closed` →
`is_closed()` — and no stored value is a cache of any other.

### 3. Added one test (no test deleted or rewritten)

`test_quota_ledger.py::test_another_tenants_live_reservation_does_not_block_a_close`.

This is the test the revision needs rather than one it inherited. With a
per-tenant counter, the guard was per-tenant *by construction*: each record had
its own number, so "is anything outstanding anywhere" was not an expression you
could write by accident. With a predicate over a shared table, the per-tenant
filter is an explicit clause, and dropping it is a plausible mistake. So I
checked that the mistake is actually caught: replacing the guard with
`if self._reservations:` in a scratch copy leaves the **shared suite passing
28/28** and fails the new test. It is load-bearing, not decoration. (The
600-step random test also catches it, incidentally; the directed test names the
fault.)

Every one of the 21 original tests is still present and still passing. I deleted
nothing and rewrote nothing.

---

## What I looked at and deliberately left standing

- **`available` stored, rather than derived from `quota`.** This is the biggest
  candidate and the one real judgement call. R1 makes `available` a function of
  the other state (`quota - committed - sum of live amounts`), so it could be
  derived, and the subtle "commit does not restore `available`" rule would then
  fall out of the definition instead of needing a comment. I left it, for two
  reasons. First, it does not remove a representation, it swaps which of two
  linked numbers is stored — and it would store `quota`, which no query exposes,
  in order to derive `available`, which is the answer to a query. After change 2
  every stored field is directly observable; deriving would give that up.
  Second, counter-versus-derivation is a different design, not accidental
  machinery inside this one, and the ask is to simplify within the design I was
  given. Recorded here because a reader could reasonably have gone the other way.
- **`Reason` plus `REASONS` plus the assert in `Result.rejected`.** The six
  reason names are genuinely written twice, which is the "two places that must
  change together" smell. I still left it: `REASONS` has a real reader outside
  the module (`test_quota_ledger.py` imports it and asserts the set of reachable
  reasons *equals* it), and the assert is precisely what stops the duplication
  from drifting silently. The two collapses available are deriving `REASONS`
  from `vars(Reason)` — introspection, clever rather than simple — or inlining
  the literals and dropping the class, which removes a typo guard and reduces
  the module's exported surface. Neither is a simplification; both are trades.
- **The `_tenant()` helper's `try/except KeyError: raise KeyError(...)`.** It
  looks like indirection that re-raises the same exception type, but it changes
  the message (`KeyError: "unknown tenant: 'nobody'"` rather than
  `KeyError: 'nobody'`). That message is observable, so removing it would be a
  behavior change, which the ask forbids.
- **The shared prologue of `commit` and `release`** — look up the id, reject
  `unknown_reservation`, delete from the table. One rule spread over two places.
  I left it because extracting it means a helper with an optional-return
  protocol serving two callers whose next steps have nothing in common; it moves
  the decision behind a layer instead of removing it, and the layer would have
  exactly two things behind it and no third ever. **This is the candidate I am
  least sure about.** A reader who thinks the duplicated guard matters more than
  the added indirection would extract it, and I would not call that wrong.
- **`_append` as the single durable write, the `fsync`, `mkdir(parents=True)` on
  the ledger's parent, accepting `str` or `Path`, sorting `outstanding_ids()` by
  numeric suffix, and advancing the id counter only on acceptance.** Each is
  read, each does something no other code does. `fsync` and `mkdir` arguably go
  past what the feature demands, but removing them removes behavior
  (durability before return; construction into a missing directory), and I am
  not permitted to trim behavior any more than to add it.
- **`ledger_lines()` re-reading the file on every call**, rather than answering
  from memory. Deliberate in the original and load-bearing for R2: a query
  served from a memory copy could not report a disagreement with disk.
- **The order of checks in `reserve` and `close_tenant`.** Behavior. Untouched.

I found nothing in the implementation that I believe is behaviorally wrong, so
there is nothing I am leaving wrong-but-untouched under the ask's "say so and
leave it" rule.

---

## Unclear, and things I was unsure about

1. **`NOTES.md` is now stale in one place.** Its "Shape of it" section describes
   `_Tenant` as holding `quota`, `available`, `committed`, `closed` and a
   reservation count, and explains why the count exists. Both of those fields
   are gone. **I did not edit `NOTES.md`**: it is the original author's account
   of what they built, and rewriting it would blur the boundary between what
   they wrote and what I changed. Flagging it here is the alternative, and a
   reader should treat that paragraph as describing the pre-revision code.
2. **The ambiguities the original notes raise are real, and I kept its answers
   exactly** — a pre-existing ledger file is truncated; queries about an unknown
   tenant raise `KeyError`; non-integer amounts are neither coerced nor
   rejected, so `reserve("acme", 2.5)` is accepted and writes `2.5` into the
   ledger. I agree `FEATURE.md` does not settle any of the three. I did not
   resolve them, did not implement a second reading, and did not "fix" the
   float case.
3. **The `_Reservation` frozen dataclass** could be a plain tuple. That is
   taste, not structure — it removes no distinction — so I left it. Noting it
   only so it is clear I considered and rejected it rather than missed it.
4. I did not find anything self-contradictory in `FEATURE.md`.

---

## Disclosure

I opened no file on the must-not-open list. Files I read, all of them named in
my instructions or inside my working directory: `FEATURE.md`,
`examples/validation/ab/tests/test_behavior.py`, and this directory's
`NOTES.md`, `quota_ledger.py`, `test_quota_ledger.py`.

Two other things I did, disclosed for completeness because they touched paths
outside `examples/validation/ab/`:

- I listed this working directory (`ls`), and at the repository root I ran
  `git diff --stat` and `git diff -- subjects/artifact_M/quota_ledger.py` hoping
  to read my own diff. Both produced no output (this subtree appears untracked),
  so no file content was shown by either.
- For the mutation check described above I copied `quota_ledger.py` and
  `test_quota_ledger.py` into a scratch directory outside the repository,
  edited the copy, ran the suites against it, and deleted it. Nothing in the
  repository was modified by that check.
