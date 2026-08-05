# REJECTED — faults considered and not seeded

Fourteen candidates were built, applied to throwaway copies, and attacked with
all 15 catalogue drivers, five extra probe drivers, a 600-step randomized
command sweep observing every query after every step, and the shared
hand-written suite. `./rejects.py` is the prober; `./rejects_report.json` is
its raw output. Every claim below is that harness's result, not my opinion.

The reasons are sorted into three kinds, because they are not interchangeable:

- **NOT A DEFECT** — the program is still correct against FEATURE.md. Seeding
  it would manufacture a false negative for whatever instrument is being
  measured, and would flatter any instrument that happens not to look there.
- **COULD NOT OBSERVE** — I believe it is wrong but I could not build an input
  that separates it. This is the category the brief says has been wrong before,
  so each one below says exactly *what would be needed* to observe it. If a
  later round finds that input, the entry is a fault the catalogue is missing.
- **REAL, BUT DELIBERATELY NOT SEEDED** — a genuine defect I verified I can
  separate, excluded for a stated structural reason. These are the entries most
  likely to be worth promoting into a future catalogue.

---

## NOT A DEFECT

### RJ-01 (ONE) — dropping `handle.flush()` from the durable append
`_LedgerFile.append` writes inside a `with`, which closes the handle and
flushes it. The `flush()` is dead. **Nothing separated it**: all 20 drivers, the
sweep, and the shared suite are byte-identical.
This is a true equivalent mutant. A catalogue that seeded it would be
rewarding an instrument for noticing something that is not there. ONE's NOTES
call the flush deliberate; it is inert.

### RJ-02 (ONE) — `if line.strip()` → no filter in `_LedgerFile.lines`
### RJ-03 (TWO) — `if line` → no filter in `FileJournal.records`
Both filters are unreachable. `splitlines()` on text that always ends in
exactly one `\n` per record never yields an empty element, and no record is
ever written blank or whitespace-only. **Nothing separated either.** They are
defensive code against an input the writer cannot produce. Seeding here would
score an instrument on a branch the program cannot reach.

### RJ-06 (ONE) / RJ-07 (TWO) — deleting `assert reason in REJECTION_REASONS`
Both implementations assert the reason vocabulary inside `Result.rejected`.
Every call site passes a literal drawn from that same frozenset, so the assert
can never fire. **Nothing separated either.** It is a comment with a runtime
cost. Worth noting for a different reason: R4's "a rejection reason is always
one of the six named above" is *enforced* in both programs by an assertion that
is structurally incapable of failing.

### RJ-14 (ONE) — `@dataclass(frozen=True)` → `@dataclass` on `Result`
Nothing in either program or in any observation mutates a `Result`.
**Nothing separated it.** Immutability here is a design preference, not
behavior. (Note this is *not* symmetric with RJ-11 below: nothing hands a
`Result` back to a caller who then mutates it, whereas `records()` explicitly
promises the list is the caller's.)

### RJ-04 (ONE) / RJ-05 (TWO) — swapping durable-write order against memory update
ONE writes the ledger line *before* updating `_committed`; TWO updates
`_committed` *before* appending. Each artifact's NOTES argues for its own
order, and ONE explicitly claims its order means "a write that fails leaves the
two sides agreeing".

I made each arm adopt the other's order. **Nothing separated either one** —
not one driver, not the sweep, not the shared suite.

This is *not* filed as "could not observe". It is genuinely not a defect under
this requirement: FEATURE.md specifies no failure mode for the durable write,
so there is no execution in which the orders differ. But it is the sharpest
example in the whole exercise of an architectural claim that no available
instrument can price. See FINDINGS #12.

---

## COULD NOT OBSERVE — but I do not think I am done

### RJ-09 (ONE) — the constructor aliasing the caller's quota mapping
`dict(quotas)` → `quotas`. Both artifacts copy; both NOTES mention it.
**Separated by exactly one driver** (`C91_caller_dict`, which mutates the
caller's dict after construction) and by **nothing else** — not the sweep, not
the shared suite.

Filed here rather than as a defect because I cannot show it *is* one:
FEATURE.md never says the mapping is copied, never says what happens if the
caller mutates it, and quotas are not in the observable-state table. What I can
say is that the two arms agree on the copy and both wrote a test for it, which
is evidence that competent engineers read the requirement as demanding it. If a
later round decides that reading is right, this is a real fault the catalogue
is missing, and the input that finds it is "construct, then mutate the dict you
passed" — an input no model-derived corpus will generate, because the quota
mapping is a CONSTANT in the model rather than an argument.

### RJ-13 (ONE) — dropping `self._path.parent.mkdir(parents=True, exist_ok=True)`
**Separated by one driver only** (`C93_missing_parent`: a ledger path in a
directory that does not exist). Not by the sweep, not by the shared suite.

Not seeded because it is not a defect *and the two arms disagree about it in
unmutated code*: ONE creates missing parents, TWO raises `FileNotFoundError`.
See FINDINGS #10. A catalogue cannot seed a fault whose corrected behavior one
of the two arms does not implement — the mutant would be "make ONE behave like
TWO", which scores an instrument on a free choice.

### RJ-10 (ONE) — `commit`/`release` dropping the `reservation_id` from their result
**Separated by two drivers** (`C92_result_ids` and the 600-step sweep, which
records every returned id). Not by the shared suite.

Not seeded, and this is the most important entry in this file: **the mutated
ONE is byte-for-byte the behavior TWO ships.** Clean ONE returns
`accepted / r1` from `commit("r1")`; clean TWO returns `accepted / None`. Both
pass the shared suite. FEATURE.md's "an accepted one carries the
`reservation_id` where the command has one" does not settle whether `commit`
"has one".

Seeding this would score one arm for a fault that is the other arm's shipped,
defensible reading of an ambiguous sentence. Any catalogue that contains a
mutant like this is measuring the requirement's ambiguity and reporting it as
an arm difference.

---

## REAL, BUT DELIBERATELY NOT SEEDED

### RJ-11 (TWO) — `InMemoryJournal.records` returning its internal list
`return list(self._records)` → `return self._records`. This violates a
contract TWO *writes down itself*, on the `Journal` Protocol: "the list
`records` returns belongs to the caller; mutating it does not disturb the
journal". A caller who appends to or clears the returned list corrupts the
durable record — which is R5 ("nothing is ever rewritten, reordered, or
removed") reached through the port instead of through the file.

**Separated by `C90_port_contract` alone**, through TWO's own public surface
(`from quota_ledger import Ledger, InMemoryJournal`, both in `__all__`).
Separated by nothing else, including the sweep and the shared suite, because
the `QuotaLedger` factory the requirement names always wires `FileJournal`,
whose `records()` builds a fresh list regardless.

Not seeded for one reason: **ONE has no counterpart.** ONE declares no port
and ships no second adapter, so there is no edit to ONE with the same
`semantic`, and a mutant that exists in only one arm's catalogue turns a
per-arm kill rate into a comparison of two different denominators. This is a
measurement artifact of the A/B design, not a judgement about the fault.

It is worth promoting deliberately in a later round *as an asymmetric probe*,
because it is the only fault I found that lives entirely in the second
implementation of a port — exactly the surface TWO's architecture creates and
ONE's does not. An instrument that scores the two arms equal on a catalogue
that structurally cannot contain such a fault has not measured the difference
the A/B exists to measure.

### RJ-12 (TWO) — `_holdings` dropping its tenant filter
`[held for held in self._outstanding.values() if held.tenant == tenant]` →
no filter. Every tenant is then charged for every tenant's live reservations,
and `close_tenant` refuses while *any* tenant holds anything.

**Separated by the 600-step sweep and by the shared suite** (which fails).
Notably **not separated by any of my 15 catalogue drivers**, because every one
of them holds a reservation on only one tenant at a time — a blind spot in my
own drivers that the sweep caught, and the reason the sweep is in the prober.

Not seeded only because it would be a 16th class with no counterpart in ONE
(ONE has no per-tenant fold: it decrements a stored `available` directly). Same
denominator argument as RJ-11.

---

## Considered and not built

These I rejected before writing an edit, so there is no harness evidence; the
reason is on its face.

- **`status` string typos** (`"accepted"` → `"ok"`). Real, but caught by the
  first assertion of any suite in existence. Seeding it inflates every
  instrument's score equally and discriminates nothing.
- **Type checks on non-integer `amount`.** Both NOTES flag that `reserve(t,
  1.5)` is held and committed as `1.5`. This is *unspecified*, identically, in
  both arms — the six-reason vocabulary has no reason for it and FEATURE.md
  never requires integrality. Seeding a "fix" or a "break" here would be
  seeding my own reading of a gap. It belongs in FINDINGS (#7), not in a
  catalogue.
- **Queries on an unknown tenant.** `available("nobody")` raises `KeyError` in
  both. Both NOTES independently flag it as unspecified. Same reasoning.
- **Concurrency, crash-during-write, partial lines, fsync.** FEATURE.md's "Not
  part of the feature" rules these out explicitly, and neither implementation
  has a seam to inject them (ONE has no port at all). Seeding here measures
  scope inflation, not defect detection.
- **`is_closed("nobody")`.** Returns `False` in both, rather than raising like
  the other two queries do. Inconsistent, identical across arms, unspecified.
  FINDINGS (#8).
- **Mutants inside each artifact's own test file.** Both ship substantial
  suites of their own (32 and 53 cases). Breaking a test is not a defect in the
  program, and scoring an instrument on it would reward instruments that read
  the arm's tests — which is precisely the contamination this exercise exists
  to avoid.
