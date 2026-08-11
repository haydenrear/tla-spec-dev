# CL-03 — predictions, SEALED BEFORE MEASURING

**Sealed at `2026-08-11T18:42:43Z`, at branch point `10cf11a`, in the commit that
adds this file.** Nothing had been dispatched to any judge when this was written:
the four cards existed only as unfilled skeletons
(`close-the-loop-cl03-v4/...p1,p2`, `close-the-loop-cl03-v5/...p1,p2`), no judge
agent had been launched, and no score of any kind existed for the subject.

RM-05's evaluation declared an ALARM against itself for sealing predictions after
it had already done most of its own measurement. **The same alarm condition is
declared here in advance: if every prediction below holds cleanly, this round
reports an ALARM against itself**, because a prediction set that cannot lose was
not a prediction set.

Each prediction names a MECHANISM, not only an outcome, so that it can be wrong
for a stated reason.

---

## What is being measured

One artifact — `examples/validation/ab/reference_ports`, the fixture whose
real/fake adapter pair 22 `D3 = 4` cards rest on — scored **twice under two card
versions and nothing else different**: same artifact bytes, same judge model,
same declared subject (`toolchain_fixture`, scope
`examples/validation/ab/reference_ports`, architecture tag `ports-and-adapters`),
same dispatch text, two independent judges per version.

The treatment is **the card**, not the artifact. Version 5 changes exactly one
served thing that can reach a judge's reasoning about D3: the D3 caveat now says
that anchor 4 is satisfied by a real adapter that does nothing real. `R-H1` and
`R-H2` are satisfied by construction — one example, one architecture tag, and the
instrument axis is the only thing that moves.

**The regression is not repaired by this ticket and must not be.** No file under
`examples/validation/ab/` is edited.

---

## P1 — under version 4, `reference_ports` scores D3 = 4

**Mechanism.** Anchor 4 reads *"3, **and** a driven port is exercised by a real
adapter *and* a fake, with the same cases passing against both."* The fixture
satisfies every clause of that sentence literally: `journal_file.FileJournal` and
`journal_memory.InMemoryJournal` both satisfy `domain.LedgerJournal`, two
composition points bind them, and `examples/validation/ab/tests/test_behavior.py`
passes 28/28 through both wirings. Nothing in the version 4 served bytes asks
whether the real adapter is real.

**Prediction.** At least one of the two version 4 judges awards **D3 = 4**.

**Falsified if** both version 4 judges score D3 ≤ 3.

---

## P2 — under version 5, at least one judge names the single-observer fact

**Mechanism.** The version 5 caveat names the exact configuration the fixture is
in: *"if the only observer of the effect the port exists for is the adapter that
wrote it, say so and take 3."* `ReservationBook.ledger_lines()` (`domain.py:124`)
is that single observer, and no case in the packet opens the ledger file.

**Prediction.** At least one version 5 card's D3 rationale states that the
durable record is only ever read back through the adapter that wrote it, or an
equivalent statement naming `ledger_lines`/`lines()` as the sole observer.

**Falsified if** neither version 5 card contains that observation.

---

## P3 — THE PREDICTION WITH SOMETHING TO LOSE: version 5 does NOT move both cards down

**Mechanism, and why it may be wrong.** The caveat's antecedent is *"if the only
observer … is the adapter that wrote it"*, and `journal_file.py:30,33-34` visibly
calls `write_text` and `open(...,"a")`. A judge who reads the ADAPTER rather than
the OBSERVERS will conclude the real adapter plainly does something real and
award 4 anyway. The hole is not visible from `journal_file.py`; it is visible
only from the absence of any other reader, which is a negative fact about the
whole packet.

**Prediction.** At least one of the two version 5 judges still awards **D3 = 4**,
so the D3 delta across the version boundary is **not** a clean 2-of-2 drop.

**Falsified if** both version 5 judges score D3 ≤ 3.

**This is the prediction the round exists to be wrong about.** If it is
falsified, a two-sentence caveat moved a dimension that six epics of static gates
never moved, and that is the more interesting result.

---

## P4 — the judging practice predicts the finding better than the card version does

**Mechanism.** The fact is a negative one about the packet's observers. A judge
that seeds its own fault — for instance replacing `FileJournal`'s writes with a
list — observes the hole directly; a judge that reads the evidence has to notice
an absence.

**Prediction.** Across all four cards, `judging_practice.executed_own_faults ==
true` is a better predictor of whether the card names the single-observer fact
than `scorecard_version == 5` is.

**Falsified if** a card with `executed_own_faults == false` names it while a card
with `true` does not, in a way that reverses the association — or if all four
cards agree on both variables, in which case the prediction is **undecidable**
and is reported as undecidable rather than as held.

---

## P5 — the served surface does not grow (NEAR-CERTAINTY, declared as one)

`serve | wc -c` is **6,319 → 6,281 bytes** and rungs are **9 → 9**, already
measured at the time of sealing. This is not a forecast and is recorded so the
number is on the record before the judges are, not because it is at risk.

---

## P6 — the sealed record is unchanged by the bump (NEAR-CERTAINTY, declared as one)

`score_tools.py check specs/results/scorecards` reports the same **330**
problems after the version 5 bump as before it, because no sealed card is edited
and version 5 adds no rule any card must satisfy. Already measured at sealing
time. Declared for the same reason as P5.

---

## P7 — keying tier on the full model id does not manufacture a split

**Mechanism.** `derived_tier` substring-matches, so `claude-opus-5[1m]` and
`claude-opus-4` share one label and `claude-sonnet-5` and `claude-sonnet-4-5`
share another. Splitting them can only ever make a group's tier partition FINER.
A finer partition can turn a reported disjoint split into no split (two members
of one label separate), and it can create a new pair where none existed.

**Prediction.** Re-keying on the full model id **removes** at least one
previously reported tier split from the record and **creates none that reverse
an existing claim's direction**.

**Falsified if** a new split appears whose direction contradicts a split the
record already publishes.
