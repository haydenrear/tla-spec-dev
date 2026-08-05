# FINDINGS — things that are not mutants

Numbered. Each says what I checked and how. Where a claim is measured, the
harness that measured it is named; where it is read off a file, the file and
line are named.

---

## A. Answer keys leaking into files I was allowed to read

### 1. `model/QuotaLedger.tla`'s header comment names the existing catalogue's mutants and their locations

The module comment (lines 2-25) says, in the file I was explicitly given:

> "Commit and CloseTenant are the CROSS-ASPECT actions: their guards read
> RESERVATIONS and their effects write LEDGER. **M03 and M08 in
> ../seeded_faults.toml are seeded exactly there**"

and

> "The predecessor measured that a state-only oracle cannot see a fault where
> the transition is correct and the REPORTED OUTCOME is wrong (**M06**), and
> that a corpus containing no rejected input cannot see guard relaxation at
> all."

Inline comments then name **M02, M07, M08, M10** as the mutants that break
`Conservation` (line 72) and **M03** as the one that breaks
`ClosedHasNoOutstanding` (line 76).

### 2. `model/spec_manifest.yaml` goes further and states the mechanism, the placement, and prior scores

Lines 20-24 and 53-57 describe M08 exactly: *"its cause is a LEDGER-aspect
action and its symptom lands on a RESERVATIONS-aspect variable"*, *"a Commit
that also refunds the hold"*, plus the prior result *"the claim fell to 9 of
10"*. Lines 60-66 state *"3 of 3 durable-write mutants died under a
content-asserting mapping and 0 of 3 under a silent one"* and name HP-03,
HP-05 and HP-06.

### 3. Consequence: two of my thirty mutants are not independent evidence

`BA-P07` / `BA-Q07` (`cross_aspect_write`) is, by the manifest's own words, the
same fault as M08 — *"a Commit that also refunds the hold"* is a verbatim
description of the edit I made to ONE. `BA-P08` / `BA-Q08`
(`durable_content_running_total`) is the class the manifest says has already
been measured at 3-of-3 vs 0-of-3.

I did not open `seeded_faults.toml`. I did read files that describe its
contents. **A "blind" author who reads the model and the manifest is not blind
to the two fault classes this fixture cares most about.** If the point of this
round is that a catalogue written by the mechanism's author flatters the
mechanism by ~25%, then the leak channel is not only `seeded_faults.toml`: it
is the TLA+ header comments and the manifest prose, and both are on the
*allowed* list. Any future round should strip narrative from the model and the
manifest, or move it to a file on the forbidden list.

The other thirteen classes I arrived at from FEATURE.md, the two programs, and
the shared suite alone. I have no way to know how many of them collide.

---

## B. Disagreements between the specification and the model

### 4. The model's `COMMIT` line has no running total; FEATURE.md's R2 is entirely about the running total

`QuotaLedger.tla` line 122:

```tla
ledger' = Append(ledger, << "COMMIT", holder[r], amt[r] >>)
```

Three fields: tag, tenant, amount. FEATURE.md requires
`COMMIT <tenant> <amount> <committed-total-after-this-commit>` and R2 is the
rule that the fourth field is the running sum. The model's `CloseTenant` (line
139) *does* carry its total: `<< "CLOSE", t, committed[t] >>`.

So the model is asymmetric where the requirement is not, and the asymmetry runs
exactly against R2. A refinement check against this model cannot see
`BA-x08` — there is no model field for the mutated field to disagree with —
while it can see `BA-x09`. Meanwhile `spec_manifest.yaml` declares
`asserts_content: true` on `LedgerAppendPort` and its description says COMMIT
lines *"carry tenant, amount and the running total after the commit"*, which is
true of the requirement and false of the model the manifest points at.

If a run scores `BA-x08` as killed, check whether it was killed by the model or
by the shared suite, because the model as written does not contain the field.

### 5. `unknown_tenant` is in the model's reason vocabulary and no action can ever produce it

`Reasons` (lines 49-51) lists `"unknown_tenant"`. No `Refuse` call in the
module passes it — the seven refusal actions produce `tenant_closed`,
`amount_not_positive`, `quota_exceeded`, `unknown_reservation` (twice),
`tenant_closed` again, and `outstanding_reservations`. `Tenants` is a CONSTANT,
so an unknown tenant is not a constructible input.

One sixth of the declared rejection vocabulary is unreachable in the model.
`BA-P05` / `BA-Q05` are seeded there deliberately. A model-derived corpus
cannot generate the input; a model-derived oracle has no proposition about it;
only the requirement text and a hand-written case know it exists. (The shared
suite does catch it — one test — which is itself part of the answer to "what
does a normal suite catch that a generated corpus does not".)

### 6. `RejectionIsInert` does not check that a rejection is inert

```tla
RejectionIsInert ==
    status = "rejected" => reason \in Reasons \ {"none"}
```

The comment above it says it expresses *"R4 — a rejection changes nothing …
Expressed as: a rejected step leaves every variable but status/reason alone."*
The body says only that a rejected step names a non-`none` reason. It is a
one-state predicate; inertness is a two-state property and cannot be written as
an `INVARIANT` at all. The actual inertness lives in the `Refuse` operator's
`UNCHANGED` clause, i.e. in the *model's* behavior, not in anything checked
against the implementation.

`QuotaLedger.cfg` lists exactly four invariants, and this is one of them.
`BA-P12` and `BA-Q12` satisfy it while violating R4 outright. **This is an
assertion whose name promises a rule it does not hold.**

### 7. The model has one `Quota` for all tenants; the requirement and the suite have per-tenant quotas

`CONSTANTS … Quota` (line 32, commented *"every tenant's quota (one number
keeps the space small)"*), used by `Conservation` as
`available[t] + Held(t) + committed[t] = Quota`. The cfg sets `Quota = 2`.
The shared suite runs `{"acme": 10, "globex": 4}`.

Conservation as written is only meaningful in a world where all tenants share a
quota. Nothing in the model can express the per-tenant quota mapping that
`QuotaLedger.__init__` takes as its first argument, so no model-derived corpus
can construct the state space either program actually operates in. `BA-x04`
(`guard_basis_confusion`) is only a *fault* because quota != available; in the
model's state space, with `Quota = 2` and `Amounts = {0,1,2}`, the difference
between "check against quota" and "check against available" is much narrower
than it is in the program.

### 8. The model cannot express a negative amount, and half of the requirement's rule is about negatives

`RefuseReserveNotPositive` requires `a = 0`, not `a < 1`; `Amounts` is a subset
of Nat and the cfg sets `{0, 1, 2}`. FEATURE.md says *"amount is less than 1"*
and the shared suite tests `reserve("acme", -2)`.

`BA-x03` relaxes `amount < 1` to `amount < 0`, which is visible in the model
(0 becomes acceptable, and `Reserve` requires `a >= 1`). The *other* half of
the same guard — anything about negatives — is unmodelable.

### 9. Reservation ids are a guard in the model, so "never reused" is not a checked property

`Reserve` requires `holder[r] = NoTenant`, and neither `Commit` nor `Release`
resets `holder` or `amt`. With `ResIds = {r1, r2}` in the cfg, **at most two
reserves can occur in any behavior**, and a reused id is simply not a modeled
step rather than a violated invariant.

Consequence: `BA-x11` (`identity_reuse`) and `BA-x14`
(`observation_order_violation`, which needs ten live ids) are both structurally
outside the model's reach. `BA-x14`'s blind spot is doubled — lexicographic and
numeric order agree on `r1..r9`, and the model can allocate two.

### 10. The manifest's own empty-vs-absent policy is violated by the manifest

`spec_manifest.yaml` lines 80-86 insist:

> "Deliberately EMPTY, not absent. Empty claims 'performs no distinct effect';
> absent claims 'unmapped'. Collapsing the two turns 'we checked, there are
> none' into 'nobody looked'."

`effects.actions` then maps four actions: `Commit`, `CloseTenant`, `Reserve:
[]`, `Release: []`. **All seven `Refuse*` actions are absent, not empty** — and
they are exactly the actions R4 is about, i.e. the ones where "performs no
durable write" is a claim someone should want checked. By the manifest's own
definition, nobody looked at the refusal edges' effects.

### 11. The two declared case-module slices are close to empty, if `form: slice` means what the manifest's prose says

The `Aspect_Reservations` claim says *"it does NOT project committed or the
ledger, and **it does not contain Commit**"*, which reads as: `Next` is
restricted to the listed actions. Taking that reading:

- **`Aspect_Reservations`** lists `Reserve, Release, RefuseReserveClosed,
  RefuseReserveNotPositive, RefuseReserveOverQuota, RefuseReleaseUnknown`. It
  does not contain `CloseTenant`, which is the **only** writer of `closed`.
  `Init` sets `closed = {}`, so in this slice `closed` is forever empty and
  `RefuseReserveClosed` (`t \in closed`) is **never enabled**. The slice cannot
  reach the closed-tenant rejection at all, so `BA-x01`
  (`guard_order_inversion`, whose separating input requires a closed tenant) is
  invisible to it for a reason that has nothing to do with aspects.

- **`Aspect_Ledger`** lists `Commit, CloseTenant, RefuseCommitUnknown,
  RefuseCloseAlreadyClosed, RefuseCloseOutstanding`. It does not contain
  `Reserve`, the only action that adds to `live`. `Init` sets `live = {}`, so
  `Commit(r)` (`r \in live`) is **never enabled** and `RefuseCloseOutstanding`
  (`\E r \in live : …`) is never enabled either. `committed` stays 0 forever
  and the only reachable ledger line in the entire slice is `CLOSE t 0`.

If that reading is right, the manifest's claim that `Aspect_Ledger` cannot see
M08 is true, but not because of aspect projection — **the slice cannot execute
`Commit` at all**, so it cannot see any Commit fault whatsoever, cross-aspect
or not. A round that reports "the ledger slice killed k of n" is reporting on a
slice in which committing is unreachable. This should be checked before any
conclusion is drawn from slice kill rates.

---

## C. Disagreements between the two implementations, in unmutated code

I ran a 600-step randomized command sequence (`C94_sweep` in
`observations.py`) against both clean trees, recording after **every** step:
the result triple, `available`, `committed`, `is_closed` for three tenants,
`outstanding_ids()` and `ledger_lines()`. That is 3600 observation slots.

### 12. The two programs differ in exactly one observable, in 17 of 3600 slots

**Every state observation is identical.** All 17 differences are the same
thing: the `reservation_id` carried by an *accepted* `commit` or `release`
result.

- ONE: `commit("r1")` -> `accepted, reason=None, reservation_id="r1"`
- TWO: `commit("r1")` -> `accepted, reason=None, reservation_id=None`

FEATURE.md says *"an accepted one carries the `reservation_id` where the
command has one"*. Both readings are defensible; the shared suite never asks.
This is the only behavioral disagreement I could find between the two arms, and
it is a requirement ambiguity, not a defect in either. It is also why RJ-10 is
in REJECTED rather than in a catalogue.

### 13. A ledger path in a non-existent directory: ONE creates it, TWO raises

ONE's `_LedgerFile.__init__` calls `self._path.parent.mkdir(parents=True,
exist_ok=True)`. TWO's `FileJournal.__init__` calls `write_text` directly and
raises `FileNotFoundError`. Measured by `C93_missing_parent`. Unspecified in
FEATURE.md; neither is wrong.

### 14. Everything else converged

Despite different implementation prompts, the two arms independently arrived at:
the same frozen `Result` dataclass with `status`/`reason`/`reservation_id` and
the same two static constructors; the same six-element `REJECTION_REASONS`
frozenset; the same `assert reason in REJECTION_REASONS` inside
`Result.rejected`; the same four-guard order in `reserve` and three-guard order
in `close_tenant`; the same decision to truncate an existing ledger file; the
same `KeyError` on `available("nobody")`; the same `False` from
`is_closed("nobody")`; and the same non-decision about non-integer amounts.

Both NOTES independently flag the same three unspecified areas (unknown-tenant
queries, an existing file at the path, non-integer amounts) and both include a
test named for the `r10`-before-`r2` trap.

**For the A/B this is the finding.** The variable under test moved the code's
*shape* a long way — one module versus a package with a declared port and two
adapters — and moved its *behavior* by one ambiguous field. Any instrument that
scores the two arms differently is scoring shape, or scoring noise, unless it
can point at one of the two differences above.

---

## D. The shared suite

### 15. `test_rejection_reasons_come_from_the_declared_vocabulary` cannot fail on a substitution

```python
observed = { …six reasons… }
assert observed <= declared
```

`observed` is a **set**, and the assertion is a subset test. Any program that
returns any of the six declared reasons for all six commands passes it — the
set could collapse to a single element and still be a subset. `BA-x05`
substitutes one declared reason for another and this test passes; the mutant is
caught only by the parametrized `test_reserve_rejects_and_changes_nothing`
elsewhere in the file. The test's name promises the vocabulary is checked; what
it checks is that no *undeclared* string appears.

### 16. R1 is asserted with the held term hard-coded

`test_r1_conservation_holds_through_a_mixed_sequence` asserts
`outstanding_ids() == []` and then uses `held = {"acme": 0, "globex": 0}` — so
R1 is only checked with nothing held. The companion test hard-codes `7`. R1 is
never checked against a recomputed held total across a mixed sequence. Both
arms' *own* suites do better than the shared one here (ONE runs a 400-step
model-based sweep; TWO asserts literal expected values through both journals).

### 17. Measured: the shared suite misses 4 of 15 classes in ONE and 5 of 15 in TWO

From `report.json`. Survivors: `guard_order_inversion`, `identity_reuse`,
`observation_order_violation`, `construction_not_empty` in both arms, plus
`rejection_not_inert` in TWO (where the damage is to the id counter rather than
to a stored `available`, and TWO's counter damage is not observable through any
query the shared suite makes).

That is the floor an instrument has to beat to have earned anything.

---

## E. Claims in the artifacts that the exercise cannot price

### 18. TWO's "R1 is true by construction and cannot drift"

TWO derives `available` as `quota - held - committed` and its NOTES argue R1
therefore cannot break. `BA-Q07` breaks R1 by deleting one term of that very
derivation — the derivation is not a proof, it is a single point of failure
with a smaller surface. And `BA-Q06` is worse for the claim: it keeps R1 *true*
and breaks R2, in both arms identically. Derivation moves where a conservation
fault can live; it does not remove it, and it does nothing about the
memory-versus-durable rule.

### 19. ONE's "the durable write happens before the in-memory change, so a write that fails leaves the two sides agreeing"

Measured (RJ-04, RJ-05 in `rejects_report.json`): swapping either arm to the
other's ordering is separated by **nothing** — no driver, no 600-step sweep, no
shared suite. FEATURE.md specifies no failure mode for the durable write, so
there is no execution in which the two orders differ.

The claim is not wrong; it is unpriceable under this requirement. It is worth
recording that TWO *could* be made to price it — the `Journal` port admits a
raising adapter — and ONE could not, because ONE has no injection seam at all.
That is a real, testable consequence of the architectural difference the A/B is
varying, and no instrument in this fixture currently exercises it. If the A/B
wants to measure what the port buys, a failing-`append` adapter is the
experiment, and it is one the requirement would have to be extended to permit.
