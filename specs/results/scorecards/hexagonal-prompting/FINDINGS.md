# Findings by channel, and everything HP-06 filed

**FILE FINDINGS, FIX NOTHING.** No instrument was repaired and no measurement
re-run to improve a number. Where a channel showed that one of HP-06's own
*written claims* was false, the claim is **corrected in place with the
correction marked and attributed** — that is reporting hygiene, not a fix to the
thing measured, and the underlying instrument is left exactly as it ran.

## The channel ratio, stated as a result

| channel | what it is | findings |
|---|---|---|
| **suite re-run** | `pytest tests -q` (1130 passed), `run spec-unit-tests --ticket HP-06` (143 passed), the shared behavioral suite against both arms (28 passed each) | **0** |
| **fresh adversarial attack** | one agent asked to attack HP-06's own instruments and results and find the ways the numbers are wrong | **17**, of which **6 falsified a claim HP-06 had already written down** |
| **blind author** | one agent given the two implementations, forbidden the sealed catalogue and every HP-06 result, asked to author a fresh catalogue and above all to report what it **rejected** | **13** |

**Ratio: 0 : 17 : 13. Sealed prediction N06 — "the suite will produce none of
this epic's findings" — PASSES, for the third round running.**

Say it as HP-01 asked it be said: **the suite has stopped being informative.**
Two full green runs of 1130 and 143 tests, plus 56 shared-suite assertions across
two arms, produced not one fact about the toolchain that anybody did not already
know. Every finding this round came from an agent asked to attack, or from an
agent asked what it had decided *not* to do.

And for the third round running the single most valuable section in this file is
the one headed **REJECTED**.

## Adversarial channel — 17 findings

Full text in the ticket record. The six that falsified something HP-06 had
written are marked ★; each is corrected in place at the cited location.

### ★ F1 (SEVERE) — the guard-relaxation zero is not what the sealed catalogue says it is
`QuotaLedger.tla:144-158` models refusals as **first-class actions in `Next`**, so
the whole-view corpus *does* contain refusal cases — 39,688 of its 43,128. The
shared oracle skips every one (`measure/arm_adapter.py:276-278`). So the sealed
explanation — *"a generated corpus replays only ENABLED edges, so it never once
asks the program to refuse"* — **does not apply to this model**, and the 0-of-3
under `corpus-whole` is at least partly the oracle's skip rule.

Reconciled with the record: HP-03 measured *why* those cases are unrunnable — the
`Refuse*` actions take `(t, a, r)` and use none of them, so 39,100 cases carry
`params={}` and there is no call to make. **The corpus contains refusal edges and
no refusal calls.** The 3-of-3 under `corpus-neg` stands (the same channel traced
all three kills and confirmed them); the framing of the zeros beside it does not.
Corrected in `GOAL-catch-bugs/README.md`. **HP-06-DF-10.**

### F2 (SEVERE) — 92% of the whole-view corpus is skipped and nothing records why
`run_arm_kill_table.py:104-107` drops `verdict[1]`, the skip reason both adapters
take care to construct. The output records one integer (`"skipped": 39688`).
There is no breakdown by action, by rule or by case in any shipped artifact, and
the corpora are not committed. **No `SURVIVED` cell in five of the six columns
can be distinguished by any reader, from any shipped file, from "the relevant
action was never executed."**

### ★ F3 (HIGH) — `map-silent` is a re-print of `corpus-whole`
A silent provider asserts nothing, so it cannot change a verdict except by
raising. It changes none: the two columns agree on **18 of 18 cells** across both
arms. Presenting it as a sixth instrument inflates the apparent breadth of the
measurement. Corrected where the union is computed.

### F4 (MEDIUM / MEDIUM–HIGH) — two undisclosed self-referential comparisons
(a) `arm_adapter.py:171-177` backfills `holder` and `amt` out of the case's own
`before` for any id the arm does not hold — and every action but `Reserve` leaves
them UNCHANGED, so the oracle compares the model's before-state against the
model's after-state. **Neither field is citable as something the corpus
compared.** (b) `arm_adapter.py:266` hands the comparator the case's
`outcome_fields` as fields *not* to compare, which for this module is exactly
`("status", "reason")` — so **a mutant that rejects with the wrong reason is
invisible to `corpus-neg`**, and nothing said so. The module's own docstring
declares two such comparisons and says "a check that compares a value against
itself proves nothing"; these are a third and a fourth.

### F5 (HIGH) — `KILLED` means "any exception", and the evidence is discarded
A `TypeError`, a `KeyError` from a binding, an `IndexError` from `_decode` — all
score `KILLED`. `run_all()` collects failure text for every mutated run and
`main()` reads only the count (`run_arm_kill_table.py:190-219`). **Not one
`KILLED` cell in either merged table is attributable to a case, an assertion or a
reason.**

### F6 (HIGH) — `per_class` renders `CONTROL_RED` and `UNAPPLIED` as clean zeros
`run_arm_kill_table.py:239-241` counts anything that is not the literal `KILLED`
toward the denominator. This shipped: `kill-table-arm-a.json` (run 1) has all
twenty slice cells `CONTROL_RED` and prints a complete, plausible, **entirely
fabricated** class table beside them. The merged files are unaffected; run 1 is
still a shipped artifact and carries no marker.

### F7 (MEDIUM–HIGH) — the merged JSONs invite the comparison the README forbids
Arm A reports `wrong_value: corpus-neg "0 of 2"`, arm B `"1 of 1"`;
`cross_aspect` is simply absent from arm B. Nothing in either JSON marks a hole,
flags the red control, or forbids the comparison. Read side by side they say
"arm B's negative corpus catches 100% of wrong-value faults where arm A's catches
0%", and both halves are artifacts.

### ★ F8 (MEDIUM) — HP-06 shipped two contradictory claims about the same row
`catalogue_arm_b.toml` claimed its M07 re-anchoring produces *"the same
observable the sealed mutant declares"*; `GOAL-catch-bugs/README.md` called it a
*"broader-reach substitute"*. The README is right and the catalogue — the file
the driver actually reads — was wrong. Corrected in place.

### ★ F9 (MEDIUM) — the `branches` figure decomposes entirely into non-complexity
Node by node: three of arm A's "extra" branches buy behavior arm B does not
implement (parent-directory creation; a named `KeyError`), and the one branch
arm B has that arm A lacks is the same predicate written on the other side of a
`for`. **On matched behavior the two trees have identical decision counts.** The
neighbouring claim — that neither arm bought its figures by deleting behavior —
is unsupported *for exactly this delta*, because the shared suite uses `tmp_path`
and never exercises either. Corrected. **HP-06-DF-08.**

### ★ F10 (MEDIUM) — the prescribed workaround for HP-06-DF-02 is broken the same way
`state_writers` misses subscript writes, method mutation, `del`, every write
through a name other than `self`, and dataclass fields. Result:
`max_writers_of_one_attribute` is **2 for arm A, 2 for arm B and 2 for the
reference**, and in all three the one attribute with two writers is the id
counter. The figure marketed as the number behind "state written from everywhere"
**is a constant across all three trees and discriminates nothing.** Corrected.

### F11 (LOW) — `io_imports` reports arm A touching the outside world through a type annotation
`os` appears in arm A only as `path: os.PathLike | str`. No call, no attribute
access at runtime.

### ★ F12 (MEDIUM) — the determinism claim covered 2 of 6 instruments on 1 of 2 arms
Not covered: `corpus-whole`, `map-silent`, `map-checking`, `corpus-slice-led`,
the `suite` column, and arm B entirely. "Recorded failure text included"
over-claims even for the two it ran, because failure text is retained only for
controls. Corrected. **HP-06-DF-09.**

### ★ F13 (MEDIUM) — HP-06 computed the cross-class aggregate the catalogue forbids
Kept with the objection attached, because the brief and three predecessor close
notes all require the generator-versus-suite sentence and it cannot be said
without one. Three unanswered objections recorded beside it, including that
arm B's flawless 8 of 8 is arithmetically produced by removing from the
denominator the two mutants arm B could not be made to fail.

### F14 (MEDIUM, latent) — the whole-view control goes RED the moment `Reserve` recovery is fixed
The oracle discards the model's chosen reservation id and re-derives one from
`max(ordinal) + 1`. The model admits **any** free `r`, so `Reserve(t1,1,r2)` then
`Reserve(t1,1,r1)` is legal and the arms would allocate `"r3"`. It has never
fired because 100% of positive `Reserve` cases are skipped — **so the exact
remediation this round recommends would turn the control red.** Worth knowing
before the next round cites it as green.

### F15 (MEDIUM, latent) — the aspect projectors also decide what the oracle INSTALLS
The projector is applied to `before` as well as `after`, so every ledger-slice
case is installed with no outstanding reservations and every reservations-slice
case with `committed = 0` and an empty ledger. Here that is faithful — a
coincidence of these two slices — **it is asserted nowhere and nothing would
notice if it stopped holding.**

### F16 (LOW–MEDIUM, latent) — two adapters, two incompatible skip policies over one corpus
`PositiveAdapter` refuses an `UNCHECKED` parameter; `NegativeAdapter` has no such
guard and would pass the sentinel to the arm, raising a `TypeError` counted as a
**kill** (F5). Does not fire today only because negative-case arguments are
enumerated rather than recovered.

### F17 — the skip gate is reimplemented, not imported
`run_arm_kill_table.py`'s docstring claims the shipped assertions are imported and
never reimplemented. The shipped `adapter_accepts_case` is **not** imported; the
hand-rolled equivalent is precisely where the skip reason is discarded (F2).

### And what the adversarial channel could NOT break — this half is required
It re-derived `production_lines` independently (147 / 123 / 93, matching to the
line); confirmed the before-state installation of `available` is faithful on both
arms and could not construct a reachable state where it is not; confirmed
`_next_ordinal`'s "ids are never reused" reasoning; **traced all three
`corpus-neg` guard-relaxation kills and confirmed them as real measurements
unaffected by F4b**; confirmed the content assertion resolves against the model's
after-state rather than against itself; confirmed M05's `except Exception: pass`
cannot swallow it, because the assertion runs at `ExitStack` teardown; confirmed
the M01–M04, M06, M08–M10 re-anchorings are arithmetically faithful; confirmed
`merge_tables.py` cannot cherry-pick; and confirmed `arm_adapter.py` contains no
branch on the arm.

### What it REJECTED
Eight attacks considered and dismissed with reasons, of which two are worth
carrying forward: **R2** — every mutant happens to change its file's size, so
CPython's `(mtime, size)` bytecode invalidation cannot serve a stale `.pyc`; the
harness is *one whitespace-neutral mutant* away from a silent survivor and
nothing deletes `__pycache__` between mutants. **R8** — arm B's `InMemoryJournal`
is counted as production code, so part of the only figure on which arm B looks
worse (21 public names to 17) is the cost of a fake that arm A gets for free from
`tmp_path`; dismissed as a finding because a working adapter for a declared port
is defensibly production, but recorded because it moves that figure.

## Blind-author channel — 13 findings

Its catalogue and per-instrument results are in `GOAL-catch-bugs/README.md` and
`measure/blind_author/`.

**BA-F1. The model's COMMIT record has three fields; the feature's has four.**
`Append(ledger, <<"COMMIT", holder[r], amt[r]>>)` against `COMMIT <tenant>
<amount> <running-total>`. **R2's running-total clause is absent from the state
machine entirely**, and `spec_manifest.yaml`'s own port description describes a
line the model never constructs. No oracle derived from this model can catch a
stale running total — which is exactly why M04 needs the content mapping and its
`content: append: total: "committed[tenant]"` sentence. **The one measured edge
the epic has is a patch over a model that does not refine its own specification.**

**BA-F2. `RejectionIsInert` does not assert inertness.** The formula is a
well-formedness check on the reason; inertness is carried by each `Refuse`
action's `UNCHANGED`, so the invariant is unfalsifiable by construction and as an
oracle over an implementation trace would not catch a durable write on a rejected
path. The negative corpus's whole justification is R4, and the invariant carrying
R4's name is not the one doing the work.

**BA-F3. `unknown_tenant` is unreachable in the model.** It is in `Reasons`, but
every action quantifies over `t \in Tenants` and no refusal action exists for it.
One of the six reasons — one the shared suite exercises three times — has no
modeled edge.

**BA-F4. No behavior of the model contains a third `reserve`.** `holder` is never
reset and `ResIds = {r1, r2}`, so the clause the feature spends two sentences on
("`r1`, `r2`, `r3`, … never reused") is unreachable. Both of the author's
id-allocation and ordering mutants are invisible to the model *and* the suite.

**BA-F5. Negative amounts are unmodeled.** `Amounts = {0,1,2}` and the refusal
guards on `a = 0` exactly, while the feature says "less than 1" and the shared
suite sends `-2`.

**BA-F6.** "ascending" in `outstanding_ids()` is ambiguous and the readings
diverge at the tenth id; both arms happened to choose allocation order.

**BA-F7.** Query behavior on an unknown tenant is undefined, and **arm B is
internally inconsistent**: `is_closed("nobody")` returns `False` — reporting a
nonexistent tenant as open — while `available`/`committed` raise `KeyError`.

**BA-F8.** Whether an accepted `commit`/`release` carries a `reservation_id` is
undefined; the arms diverge and arm B is internally inconsistent.

**BA-F9. THE ARMS DIFFER IN UNMUTATED CODE ON CRASH CONSISTENCY, and nothing in
this fixture can see it.** Arm A appends then updates memory; arm B updates then
appends. With a durable write that raises mid-commit:

```
arm A: committed('acme')=0  outstanding=['r1']  R2 holds: True
arm B: committed('acme')=3  outstanding=[]      R2 holds: False
```

Invisible to the shared suite (it never makes the port fail) and to the model
(which has no failing-write action). **The sharpest irony in the round: arm B's
entire architecture is an injected port, which makes it the *easier* arm to test
for exactly this, and neither its own 41 tests nor anything else does.**

**BA-F10. The fixture leaks its own answer key.** `spec_manifest.yaml` names
`M08 (cross_aspect)` and describes it exactly; `QuotaLedger.tla`'s comments name
M03, M02/M07/M08/M10 and M06. Both are on the *permitted* list for anyone the
fixture asks to work blind. The author disclosed this unprompted and **withdrew
its own credit** for two classes it said were "handed to me by the fixture".

**BA-F11.** Two whole classes are each held by exactly one test, in both arms:
`durable_extra_write` and `rejection_side_effect`. Delete one assertion from
either and a class goes dark with no other signal.

**BA-F12.** Arm B's `close_tenant` guard is a truthiness test on an integer,
correct only because `reserve` rejects `amount < 1` — a guard in one command
silently underwriting a guard in another. First-order mutation cannot expose it.

**BA-F13. The rejection it is least confident about, recorded as it asked.** It
declined to seed durability across a failing write, in exactly the shape of the
predecessor's wrong rejection: *"I am declining a class because the harness
cannot currently reach it, not because the fault is unreal."* It then proved the
arms already diverge on it (BA-F9). **Seed it next round.**

### And the finding that corrected HP-06's own conclusion
HP-06's catalogue recorded that M08 and M10 "cannot be written" against arm B.
The blind author, from scratch, reached the same structural observation, printed
the four perturbations it tried and what each broke — and then **seeded the
cross-aspect leak into arm B anyway, by ADDING a quota-inflating statement rather
than perturbing one**, reproducing M08's exact observable. It died. The corrected
claim is that the asymmetry is in **seedability, not killability**. Its own
sentence: *"a kill-count table would hide it entirely."* **HP-06-DF-06**;
HP-06's catalogue was not re-seeded, because adding a mutant after seeing the
results is fitting the catalogue to the run.

### And the cost side of the port, which nobody predicted
`BA-B14`, a fault in arm B's in-memory journal adapter, **survives every
instrument including the hand-written suite.** Arm A has no counterpart, because
arm A has one durable implementation whose composition point is its constructor.
**The port removes places for some faults to live and creates a region no shared
oracle reaches** — the fake that earned arm B its D3 = 4 is verified by nothing
outside arm B's own tests.

## HP-06's own defects, filed and not fixed

| id | what |
|---|---|
| **HP-06-DF-01** | the slice adapter compared fields the slice does not project; both slice columns came back `CONTROL_RED` on unmutated code on both arms in run 1. Corrected in the instrument and re-run; provenance recorded per column. |
| **HP-06-DF-02** | the mechanical block cannot count mutable state or its writers in **either** arm (F10), and the count is an undercount for arm A specifically. `max_writers_of_one_attribute` is a constant 2 across all three trees. |
| **HP-06-DF-03** | the blinding leaked on arm A — `arms/arm_a/test_quota_ledger.py:1` says `Arm A`; the sanitising pass grepped for `arm A`. Found and disclosed by judge `Y-p1`. Not re-judged. |
| **HP-06-DF-04** | a missing sentence in HP-06's evidence packet moved a judged score by one anchor: judge `Y-p2` read "no case that calls `reserve` ever executes" as contradicting the corpus-neg kills. Both statements are true together — live reservations are *installed*, not built by calling `reserve`. Not fixed. |
| **HP-06-DF-05** | **D2 as written cannot be scored above 2 by an A/B at all.** Anchor 3 needs a before and an after of the same artifact. The owner's amendment proposed reading the arm pair as the before/after; it was supplied to every judge and **no judge accepted it**. Either the anchor needs an A/B variant or the card should say D2 ≥ 3 is unreachable for them. |
| **HP-06-DF-06** | HP-06's catalogue over-claimed "not seedable"; corrected to "not seedable by perturbing an existing statement". |
| **HP-06-DF-07** | the fixture leaks its own answer key (BA-F10) — HP-01's fixture, not HP-06's instrument, and it compromises any future blind work on it. |
| **HP-06-DF-08** | the `branches` figure is not comparable between the trees and its whole delta is behavior arm B does not implement plus one predicate written on the other side of a `for`. |
| **HP-06-DF-09** | the determinism claim covered 2 of 6 instruments on 1 of 2 arms. |
| **HP-06-DF-10** | the guard-relaxation zeros under `corpus-whole` are the oracle's skip rule, not the sealed catalogue's stated mechanism, because this model spells refusals out as actions. |
| **HP-06-DF-11** | the whole-view control is latently red (F14): fixing `Reserve` argument recovery — the remediation this round recommends — makes the oracle's re-derived reservation id wrong for a reachable class of before-states. |
| **HP-06-DF-12** | `KILLED` means "any exception" and the failure text for every mutant run is computed and discarded (F5), so no kill in either merged table is auditable. |

## Inherited, still open, re-confirmed by this run

* **HP-03-DF-02** — the corpus cap. Every corpus this round used was produced by a
  command that refused its own output: 43,128 cases against a cap of 200.
* **HP-04-DF-01** — nine of eighteen adapters have no `run()`. Untouched.
* **HP-05-DF-01 / DF-02** — `scaffold project` still ships a `NotImplementedError`
  provider stub; the shipped runner still does not print the mapping it loaded.
* **The red positive control.** M07 survives every generated instrument on arm A
  because the corpus recovers no `Reserve` argument. HP-05 reported it on the
  fixture reference; HP-06 reports it on a real arm. **This is the thing to fix
  before the next round runs** — and HP-06-DF-11 says fixing it will turn a
  second control red, which is the honest order of work rather than an objection.
