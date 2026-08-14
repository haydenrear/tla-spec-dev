# `CA-04` — before/after descriptor comparison

**The fourth `validated_refactor` member (CD-09).** Recorded from this run, on
the two models the close is actually about. The gate wants this to EXIST from
the run; the delta judgement is the ledger's, not this document's.

- **before** — `git show 4302082:specs/current/{TlaSpecDevCli.tla,MC.cfg}`,
  reconstructed into a scratch tree and **verified byte-faithful by sha256**:
  `9c0f394c28259fe67848d2b7d45323d759d29bfb8e69c916b010051c91c622ef`, identical
  to `git show`'s own output. 1,054 lines, 26 `kill_test` occurrences.
- **after** — `specs/current/` at `feature/CA-04` on the merged tip. 930 lines,
  2 `kill_test` occurrences (both inside the removal note).

---

## 1. Static descriptor

| | before | after | delta |
|---|---|---|---|
| variables (declared) | 9 | 8 | **−1** (`kill_test`) |
| variables (resolved) | 7 | 6 | −1 |
| variables (unresolved) | `lastCommand`, `result` | `lastCommand`, `result` | **unchanged** |
| Next disjuncts | 17 | 16 | **−1** (`RunKillTest`) |
| `@command` actions | 16 | 15 | −1 |
| invariants in `MC.cfg` | 14 | 13 | **−1** (`KillTestVerdictRequiresBudgets`) |
| declared bound | 1,111,320 | 277,830 | **÷4 exactly** |
| cap comparison | `False` (over) | **`None`** (refused) | see §4 |

**The bound moved by exactly the removed variable's cardinality.** `kill_test`
had 4 values (`unknown`, `pass`, `below_floor`, `incomplete_catalog`) and
`1,111,320 / 4 = 277,830`. **No other factor in the chain moved**: 174,960,
34,992, 663,552, 221,184, 1,179,648 and 393,216 all still hold and are all still
asserted in `tests/test_analyze_complexity.py`. A removal that had disturbed
anything else would have broken one of those six.

---

## 2. TLC, both sides

```
BEFORE   tlc2 -config MC.cfg TlaSpecDevCli.tla
         Model checking completed. No error has been found.
         13,008,254 states generated, 563,963 distinct states found, 0 left on queue.
         depth of the complete state graph search = 25
         EXIT=0                                        -> specs/results/.../CA-04/tlc-before.txt

AFTER    tlc2 -config MC.cfg TlaSpecDevCli.tla
         Model checking completed. No error has been found.
         2,505,440 states generated, 124,643 distinct states found, 0 left on queue.
         depth of the complete state graph search = 24
         EXIT=0                                        -> specs/results/.../CA-04/tlc-after.txt
```

**Both green. Every invariant that held before still holds after** — the after
config carries all 13 surviving invariants and TLC found no error over the whole
reachable state space.

### The before run independently confirms the reconstruction

`TlaSpecDevCli.tla`'s own comment, written long before this ticket, records:
*"CloseTicket guards on TicketSpecUnitTestsPassed and TLC proves
ClosedTicketsPassedSpecUnitTests over **563,963 states**"*. The reconstructed
before-model produced **563,963 distinct states**. **The reconstruction is not
merely sha-identical to the file; it reproduces the state count the repository
recorded for that model.** That is the check that would have caught an
unfaithful `before` tree, and it passed.

### Reachable states fell by more than the declared bound did

```
declared bound     1,111,320 -> 277,830    ÷ 4.00
distinct states      563,963 -> 124,643    ÷ 4.52
depth                     25 -> 24         -1
```

**The two ratios differ and the difference is real, not noise.** The declared
bound divides by exactly the variable's cardinality because it is a product.
The reachable state count falls further because `RunKillTest` was also a *step*:
removing it removes the transitions that reached the `kill_test`-bearing states,
and the search depth drops by one accordingly. **The extra 0.52 is the action,
not the variable.** Reporting only the ÷4 would have hidden that a transition
left the model as well as a state component.

---

## 3. Behavior

Repository unit suite on the merged tip, `uv run --with pytest --with pyyaml -m
pytest tests -q`. Recorded in §6a of `PRICE-TABLE.md` and in
`pytest-repo-unit-*.txt`. **No test that exercises retained behavior newly
fails.** The full attribution, including the two reds this ticket leaves
standing, is in `PRICE-TABLE.md` §6 and §6a — it is not summarised here, because
a validated-refactor record that paraphrases its own suite result is how a red
gets lost.

---

## 4. The one comparison that got WORSE, stated because it is the unflattering half

**`comparable_to_cap` went from `False` to `None`.**

- `False` = *"incomplete, but already over the cap"* — sound in the direction it
  is made, because unresolved variables can only make the complete bound larger.
- `None` = the comparison is **refused**: an incomplete bound at or under the cap
  supports no statement at all.

The scanner's advisory changed with it, from `state_space_bound` to
`state_space_bound_partial` (*"INCOMPLETE and CANNOT be compared … reports the
cap comparison as unknown rather than as within cap"*).

**The model did not become compliant. It became unmeasurable against the cap.**
This ticket's own price table said "now under the declared budget" in an earlier
draft; that was the flattering reading and it is corrected there and here.
`tests/test_analyze_complexity.py` now asserts `is None` with the reasoning
beside it, so the next reader cannot re-acquire the wrong version.

---

## 5. What this comparison does NOT license

**It does not show that the removed behavior was unnecessary.** It shows the
model is consistent without it. `kill_test` was the only oracle validating the
representation against the *program*; TLC green on both sides says the remaining
model is self-consistent, which is precisely the property the kill test existed
because TLC could not check. **A green `tlc_after` is therefore weaker evidence
here than it would be for an ordinary refactor**, and the ledger should not be
read as certifying the capability loss — only the model's internal soundness
across it. The capability price is priced in `PRICE-TABLE.md` §4.
