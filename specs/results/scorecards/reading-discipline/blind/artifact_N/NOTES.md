# NOTES — quota ledger

## What I built

| File | What it is |
|---|---|
| `quota_ledger.py` | the implementation. **Module name for the shared suite: `quota_ledger`.** |
| `test_quota_ledger.py` | my own tests (37). Not a copy of the shared suite — every test covers something the shared suite leaves open. |
| `mutation_check.py` | evidence about the *tests*: breaks the implementation 12 ways, reports which suites notice. |

Shared suite, run from the repository root:

```bash
QUOTA_LEDGER_DIR=<this directory> QUOTA_LEDGER_IMPL=quota_ledger \
  uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q
# 28 passed in 1.72s
```

Mine, run from this directory: `uv run --with pytest python -m pytest test_quota_ledger.py -q`
→ `37 passed in 0.36s`. Both figures are from runs, not estimates.

Structure: one class, one module, stdlib only. `available` is derived
(`quota - held - committed`) rather than stored, so R1 is arithmetic rather than
something two code paths have to keep agreeing on. `ledger_lines()` re-reads the
file instead of returning an in-memory mirror, because R2 is a claim *about the
durable side* and a mirror would make it true by construction.

---

## Clause-by-clause account

Every row is one clause of FEATURE.md, where it lives, and **one input I
actually ran** that would have failed had the clause been absent. Outputs are
copied from the run, not recalled.

### Construction and queries

| Clause | Where | Input I ran | What came back |
|---|---|---|---|
| ledger file starts empty | `__init__` | fresh `QuotaLedger({"acme":10,"globex":4}, p)`; `ledger_lines()` | `[]` |
| …even on a path that had content | `__init__` truncate | wrote `COMMIT ghost 9 9\n` to the path first, then constructed | `[]` |
| `available` = quota not held or committed | `available` | fresh; `available("acme")`, `available("globex")` | `10`, `4` |
| `committed` starts at 0 | `committed` | fresh; `committed("acme")` | `0` |
| `is_closed` | `is_closed` | fresh; `is_closed("acme")` | `False` |
| `outstanding_ids()` ascending | `outstanding_ids` | 12 × `reserve("acme",1)` on quota 100 | `['r1'…'r9','r10','r11','r12']` — **numeric**, not the string order that puts `r10` first |
| `ledger_lines()` no blanks | `ledger_lines` | one commit + one close; raw file | file is `"COMMIT acme 3 3\nCLOSE globex 0\n"`, `ledger_lines()` has no `""` |

### `reserve` — the four rejections, **in order**

The shared suite only ever supplies inputs that violate exactly one clause, so
it cannot tell the declared order from a shuffled one. Each input below violates
**two** clauses at once; the reason that comes back is the one decided first.

| Ordering claim | Input I ran | What came back |
|---|---|---|
| `unknown_tenant` beats `amount_not_positive` | `reserve("nobody", 0)` | `rejected/unknown_tenant` |
| `unknown_tenant` beats `quota_exceeded` | `reserve("nobody", 99)` | `rejected/unknown_tenant` |
| `tenant_closed` beats `amount_not_positive` | `reserve("globex", 0)` after closing globex | `rejected/tenant_closed` |
| `tenant_closed` beats `quota_exceeded` | `reserve("globex", 99)` after closing globex | `rejected/tenant_closed` |
| `amount_not_positive` beats `quota_exceeded` | `reserve("z", 0)` on a **quota-0** tenant | `rejected/amount_not_positive` |

### `reserve` — acceptance, and the number edges

| Clause | Input I ran | What came back |
|---|---|---|
| `amount < 1` is the boundary | `reserve("acme", 1)` / `("acme", 0)` / `("acme", -1)` / `("acme", -2)` | `accepted r1` / `rejected/amount_not_positive` ×3 |
| `quota_exceeded` is `>` not `>=` | `reserve("acme", 10)` on quota 10 | `accepted r1`, then `available("acme") == 0` |
| exactly-available accepted | `reserve("acme",6)` → `available == 4` → `reserve("acme",4)` | `accepted r2` |
| available+1 rejected | `reserve("acme",6)` then `reserve("acme",5)` | `rejected/quota_exceeded` |
| quota+1 rejected | `reserve("acme", 11)` on a fresh book | `rejected/quota_exceeded` |
| exhausted quota rejects | `reserve("acme",10)` then `reserve("acme",1)` | `rejected/quota_exceeded` |
| reduces `available` by `amount` | `reserve("acme",3)` | `available("acme")` 10 → 7 |
| **committed** amount also keeps eating `available` | commit 6, then `reserve("acme",5)` / `("acme",4)` | `rejected/quota_exceeded` / `accepted r2` |

### `reserve` — ids

| Clause | Input I ran | What came back |
|---|---|---|
| allocated `r1, r2, r3…` in order of acceptance | `reserve("acme",1)`, `reserve("globex",1)` | `r1`, `r2` |
| never reused after **release** | reserve `r1`, reserve `r2`, `release("r1")`, reserve again | `r3` — not `r1` |
| never reused after **commit** | reserve `r1`, `commit("r1")`, reserve again | `r2` |
| *acceptance* order, so a rejection allocates nothing | `reserve("acme",99)`, `reserve("nobody",1)`, then `reserve("acme",1)` | `r1` |

That last row is the "ids are never reused" claim done as an outcome rather than
an intention: I reserved, released, and reserved again and got `r1`, then `r3`.

### `commit`

| Clause | Input I ran | What came back |
|---|---|---|
| appends exactly one line, that format | reserve 3, `commit("r1")` | `['COMMIT acme 3 3']` |
| running total accumulates per tenant | then reserve 2, commit | `['COMMIT acme 3 3', 'COMMIT acme 2 5']`; raw file `"COMMIT acme 3 3\nCOMMIT acme 2 5\n"` |
| increases `committed` | same | `committed("acme") == 5` |
| `available` **not** changed | reserve 3, read `available`, commit, read again | `7` → `7` |
| removes from outstanding | same | `outstanding_ids() == []` |
| `unknown_reservation` — never existed | `commit("r99")` on a fresh book | `rejected/unknown_reservation` |
| — already committed | `commit("r1")` twice | second: `rejected/unknown_reservation` |
| — already released | reserve, `release`, then `commit` that id | `rejected/unknown_reservation` |
| — empty string | `commit("")` | `rejected/unknown_reservation` |

### `release`

| Clause | Input I ran | What came back |
|---|---|---|
| returns the amount to `available` | reserve 3 (available 7), `release("r1")` | `accepted`; `available("acme") == 10` |
| does not touch `committed` | same | `committed("acme") == 0` |
| removes from outstanding | same | `outstanding_ids() == []` |
| **writes nothing** | same | `ledger_lines() == []` |
| …not even between two commits | reserve 3/2/1, commit r1, release r2, commit r3 | `['COMMIT acme 3 3', 'COMMIT acme 1 4']` — no third line, and r2's 2 is absent from the running total |
| `unknown_reservation` — double release | `release("r1")` twice | second: `rejected/unknown_reservation` |
| — already committed | commit `r1`, then `release("r1")` | `rejected/unknown_reservation`, `ledger_lines()` still `['COMMIT acme 3 3']` |

### `close_tenant`

| Clause | Input I ran | What came back |
|---|---|---|
| `unknown_tenant` | `close_tenant("nobody")` | `rejected/unknown_tenant` |
| `tenant_closed` | `close_tenant("globex")` twice | second: `rejected/tenant_closed` |
| `outstanding_reservations` | `reserve("acme",1)` then `close_tenant("acme")` | `rejected/outstanding_reservations` |
| allowed once resolved | then `release`, then close | `accepted` |
| appends exactly one line, that format | commit 3 then 2, close | `['COMMIT acme 3 3','COMMIT acme 2 5','CLOSE acme 5']` |
| total is `committed`, and 0 is written as 0 | `close_tenant("acme")` on a fresh book | `['CLOSE acme 0']` |
| released amounts are **not** in the total | reserve 3, release, close | `['CLOSE acme 0']` — not `CLOSE acme 3` |
| marks the tenant closed | after close | `is_closed("acme"), is_closed("globex") == (True, False)` |
| closure is per-tenant | close globex, then reserve on each | globex `rejected/tenant_closed`, acme `accepted r1` |

### The five rules

**R1 (conservation)** — checked as an assertion after *every* operation of 200
random walks × 40 ops, over quotas drawn 0–12, with reserve amounts drawn −2–13
so rejections are mixed in (`test_rules_hold_after_every_operation_of_a_random_walk`).
Result: no violation. Checking after every operation rather than at the end
matters — a rule that breaks and is then repaired still fails this.

**R2 (durable agrees with memory)** — same walk: for each tenant, the `COMMIT`
amounts are re-summed from the **file's** lines and compared to
`committed(tenant)`, and each line's 4th field is compared to the running sum to
that point. No violation. Separately: `test_ledger_lines_comes_from_the_file_not_a_memory_mirror`
compares `ledger_lines()` against `path.read_text().splitlines()`, and I ran a
second object over the same path, which read back `['COMMIT acme 3 3']`.

**R3 (close is final and singular)** — same walk: whenever `is_closed(t)`, there
is exactly one `CLOSE t …` line, its total equals `committed(t)`, and no live
reservation belongs to `t`. Whenever not closed, there are zero such lines. No
violation.

**R4 (a rejection changes nothing)** — I ran all **twelve** distinct rejection
paths against a *non-empty* book (r1 committed, r2 outstanding, globex closed),
comparing the full observable snapshot before and after. The shared suite mostly
rejects from a fresh book, where "changed nothing" and several ways of being
wrong look identical. All twelve: snapshot `SAME`. The six declared reasons were
all observed and nothing outside them was.

**R5 (append-only and ordered)** — `test_the_ledger_prefix_never_changes`
asserts, after each of 7 durable writes, that the earlier lines are unchanged.
For order specifically I ran reserve acme 2, reserve globex 1, commit globex,
commit acme, close globex → `['COMMIT globex 1 1','COMMIT acme 2 2','CLOSE globex 1']`,
which is command order and not tenant order. Structurally there is one write path
(`_append`, mode `"a"`) and no seek or rewrite anywhere in the class.

---

## Evidence about the tests themselves

A passing suite says the tests agree with the code, not that they would notice
the code being wrong. `mutation_check.py` breaks the implementation 12 ways.
Run output:

```
mutant                                            mine    shared  differential
M1  reserve: amount checked before closed         caught  survived 171/400 walks differ
M2  quota_exceeded uses >= instead of >           caught  caught   41/400
M3  commit hands the amount back to available     caught  caught   45/400
M4  ids are reused once a slot frees up           caught  survived  6/400
M5  release writes a ledger line                  caught  caught   71/400
M6  close writes the quota, not committed         caught  caught  376/400
M7  outstanding_ids sorted as strings             caught  survived  0/400
M8  close: outstanding checked before unknown     SURVIVED survived  0/400
M9  COMMIT running total is the amount            caught  caught    0/400
M10 close does not mark the tenant closed         caught  caught  384/400
M11 a rejected reserve still burns an id          caught  survived 83/400
M12 ledger_lines keeps blank lines                caught  caught  400/400
```

Three things I take from that, and one I explicitly do not:

1. **My suite caught 11 of 12; the shared suite caught 7 of 12.** The four the
   shared suite misses are the rejection *order* (M1), id *non-reuse* (M4, M11),
   and ascending-past-`r9` (M7) — precisely the clauses whose distinguishing
   inputs it never supplies. Passing it is a floor, as FEATURE.md says.

2. **M8 survived my suite too, and I chased it down rather than writing a test
   to paper over it.** M8 reorders `close_tenant` so `outstanding_reservations`
   is decided before `unknown_tenant`/`tenant_closed`. To observe that, you need
   a tenant that is unknown-or-closed *and* has a live reservation. Unknown is
   impossible (an unknown tenant cannot hold a reservation). For closed: I ran an
   exhaustive search over a one-tenant ledger, quotas 0–3, all operation
   sequences to depth 4 — **90,484 states explored, 0 with `closed AND
   outstanding`**. Plus 2,000 randomised single-tenant walks: 0 divergences. So
   M8 is observationally equivalent, not a coverage gap: **the order of
   `close_tenant`'s clauses 2 and 3 is unobservable.** I implemented the declared
   order anyway, since the feature declares one and matching it costs nothing.

3. **The differential column is the weaker instrument and says so.** M9 is
   caught by both suites yet shows `0/400` — the random generator picks
   reservation ids blindly, so it rarely produces the two-commits-on-one-tenant
   sequence that exposes a wrong running total. A `0/400` therefore means "this
   generator did not find a distinguishing input", never "there is none". M7's
   `0/400` has the same cause (walk quotas cap ids below `r10`); when I re-ran it
   with quota 40 it diverged **300/300**, `['r4'…'r10']` vs `['r10','r4'…'r9']`.
   I did not re-tune the committed script's generator to fix M9's zero.

**What I did not do:** I did not mutate `available`'s arithmetic, the
`Result`/`Reservation` shapes, or the `_append` file mode. Twelve mutants is a
sample I chose, not a saturation argument, and I have no basis for a claim about
mutants I did not write.

---

## Ambiguities, recorded when I hit them

1. **`outstanding_ids()` "ascending"** — reading the query table. Ascending by
   *string* and by *allocation number* diverge at `r10` (`"r10" < "r2"`). I chose
   numeric, since ids are described as `r1, r2, r3, …` in allocation order.
   Recorded because a book that never exceeds 9 live reservations cannot tell.

2. **"The ledger file starts empty"** — reading the construction sentence.
   Ambiguous between *the caller guarantees it* and *construction makes it so*. I
   chose to truncate. **This has a cost I measured, not guessed:** constructing a
   second `QuotaLedger` on a path an existing one is using wipes the first's
   ledger while its in-memory `committed` still reads `3`, which is R2 violated.
   Two ledgers on one path is arguably out of scope ("no process boundaries"), so
   I did not add a guard rather than invent a requirement — but the failure is
   real and I would want it decided before this went anywhere.

3. **`close_tenant`'s clause order** — reading the numbered list against the
   reachable states. Unobservable; see M8 above. Written in the declared order.

4. **Queries on an unknown tenant** — hit while writing the R4 snapshot helper.
   The feature defines no behavior for `available("nobody")`. Mine raises
   `KeyError: 'nobody'` (also `committed`, `is_closed`) — I ran all three. I did
   not convert these to a rejection: queries return values, not results, and the
   six reasons belong to commands.

5. **Non-integer `amount`** — hit while probing edges. The feature says integer
   quotas and "less than 1" but names no type rule. I added no validation, and
   the consequence is real: `reserve("acme", 2.5)` returns `accepted`, and
   committing it writes `COMMIT acme 2.5 2.5` — a ledger line the format does not
   contemplate. `reserve("acme", True)` is accepted as 1. Recorded rather than
   fixed, because a type rule is a requirement I would be inventing.

6. **Tenant names containing spaces** — same probe. `QuotaLedger({"a b": 5}, …)`
   then commit 2 writes `COMMIT a b 2 2`, which `.split()` reads as 5 fields, so
   any reader parsing by position gets the wrong amount. No validation added, for
   the same reason as (5). If tenant names are ever caller-supplied this is the
   first thing to fix.

Items 5 and 6 are behaviors I *observed*, not defects against the feature — the
feature does not forbid them. I am recording them as unspecified surface, not as
bugs, and I did not implement a resolution for either.

---

## Things I could not check, or did not

- **Durability in the crash sense.** I write with `open(…, "a")` in a `with`
  block, so each line reaches the OS on close, but I do **not** `fsync`. I did
  not test any crash or power-loss scenario and make no claim about one. "No
  process boundaries" is out of scope, so I read "durable" as "in the file", and
  that reading is a choice.
- **Concurrency.** Out of scope per the feature; not implemented, not tested, and
  the class is not safe under it.
- **Large-scale behavior.** My biggest run is 200 walks × 40 ops and 12
  simultaneous reservations. I have not run this at a size where anything about
  performance or id exhaustion would show, and I claim nothing about either.
- **The exhaustive BFS is small.** Quotas 0–3, one tenant, depth 4. It supports
  the specific M8 claim about `closed AND outstanding`; it is not a proof about
  the two-tenant state space, which I did not enumerate.

---

## Disclosures

- **Files I opened:** `examples/validation/ab/FEATURE.md` and
  `examples/validation/ab/tests/test_behavior.py` (both named in the prompt).
  Nothing else under `examples/`.
- I ran `ls -la` on `examples/validation/ab/`, so I **saw the file names** listed
  in Section 6 (`seeded_faults.toml`, `check_catalogue.py`, `reference/`,
  `arm_a/`, `arm_b/`, and others) in the directory listing. I did not open, read,
  grep, or execute any of them, and I know nothing of their contents. Disclosing
  it because a directory listing is arguably "opening the directory", and the
  disclosure costs nothing.
- `test_behavior.py` is unmodified. `FEATURE.md` is unmodified.
- No dependencies added; `quota_ledger.py` imports only `dataclasses`, `pathlib`,
  `typing`. `pytest` is used only by the test files, via `uv run --with pytest`.

## Did the two halves of the prompt conflict?

Not on behavior — Section 1 asks about *evidence* and FEATURE.md specifies
*behavior*, and I hit no case where doing what one asked broke the other.

There is one real tension, and it is between Section 1 and itself: "account for
every clause, try every edge" pulls toward more claims, and "assert nothing you
did not check" pulls toward fewer. Where I resolved it: I ran a transcript that
printed the actual input and actual result for each clause **before** writing any
of this file, and every table row above is copied from that output. The rows I
could not produce that way are in "could not check, or did not" instead, unmerged
with the rest. The place this shows most is M8 — the cheap move was a test that
asserts the declared order and passes trivially; what I have instead is a
measurement showing the order is unobservable, which is a thinner claim and a
truer one.
