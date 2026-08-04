# ex3_over_complex — judge pass 2 (run 20260803-j2)

Scorecard version 1. Commit `ab0dfee`. Arm: none (single-artifact eval).
`ex3_over_complex` is a deliberately over-complex fixture; it is judged on
whether the complexity work done to it is measured, not on the shipped design.

| dim | score | one line |
|---|---|---|
| D1 bug detection | 2 | two content faults killed by content assertions; ordering asserted, never probed |
| D2 complexity | 3 | the best-evidenced simplification in the set; behavior-preservation contested by the record |
| D3 modularity | 2 | one real effect port, proven by a probe; god-state core unchanged |
| D4 behavior preservation | 3 | six behaviors + TLC + a 716-case corpus; the failing-capable demo is post-hoc |
| D5 honesty | 3 | limits named in the artifacts; run verdicts generalize past two probes |
| **total** | **13**/20 | |

## What I measured myself

I ran `analyze complexity` on the shipped fixture at scoring time:
bound **8,388,608**, Q = 0.000, one component, dense rows `auditLog` 4/4,
`dirty` 4/4, `mode` 4/4, dense columns PlaceOrder/ShipOrder/RetrySweep, and
"no justification: table in the manifest -- dead-weight analysis skipped".
That reproduces the run records' "before" figures exactly.

I also verified the load-bearing structural fact by reading the source rather
than the report: **no guard in `OrderHub.tla` reads `mode` or `dirty`**
(`:33-34`, `:42-43`, `:51-52`, `:60` read only `orders`, `shipped`, `retries`,
`auditLog`), and **no test reads them** (`tests/test_order_hub.py:9-53` touches
`orders`, `shipped`, `audit_log` only).

## D1 — bug detection: 2

Two seeded faults, both killed:

- dropped effect (`_audit` increments the counter but skips `on_audit`) → the
  provider's count assertion, message quoted verbatim and matching the
  provider's own f-string at `providers.py:91-95`;
- wrong content (`ship_order` audited as `"place_order"`) → the per-entry
  content assertion at `providers.py:78-83`.

Matching the quoted failure text against the assertion source is what lifts
`assertion_probes.txt` above a claim: those strings cannot be produced by
anything else.

It stops at 2. The provider asserts consecutive-`seq` ordering
(`providers.py:72-77`, `:96-99`) and **no ordering fault was ever seeded**, so
the class is asserted and unmeasured. That matters because the epic-wide result
is 0-of-N on ordering everywhere it *was* probed; an unprobed ordering assertion
is not evidence that this one would fire.

## D2 — complexity: 3

What got simpler, and it is verifiable rather than argued:

- `mode` and `dirty` deleted from model and program — written by every action,
  read by no guard, no invariant beyond a type conjunct, no test, no reader;
- domains right-sized from `0..15/0..15/0..31/0..63` to `0..3/0..3/0..2/0..12`,
  which are the caps the guards already enforce.

Before and after are both in the record: 8,388,608 / three dense rows /
warning, becomes 624 / one dense row / no warning.

How behavior survived, on artifacts:

- deleted variables are unread by every guard (I checked the model source);
- the fixture's own suite is unchanged, assertions byte-identical, and none of
  its tests reads the deleted keys;
- the MF-020 trap is addressed head-on: generated **and** distinct fell together
  at constant depth (1878/717 → 717/270, depth 13 both), so the state graph was
  quotiented, not truncated (`complexity_decision.md:65-69`).

Why not 4. The deletion also removes two keys from `new_hub()`'s returned dict —
a public-surface change with no check capable of catching an external reader —
and **run 2 of this same fixture judged the identical deletion a design decision
and declined it** (VAL-15). The record therefore contains two defensible,
opposite answers to "was this behavior-preserving". I take the lower anchor and
say so.

## D3 — modularity: 2

The one runtime fact I trust here is probe 1: removing the `on_audit` call while
leaving the counter increment produced a provider count-assertion failure
(`assertion_probes.txt:6-10`). That is evidence about what *calls* what, not
what imports what, and it is what the card asks for.

It goes no higher. There is no swap to name — the usage record says in-memory
journal only, no cross-process observation — and the instrumented `order_hub.py`
is absent from the run record, so the seam is visible only through a provider
and a probe. The rest of the design is one shared mutable dict stamped by every
operation (`order_hub.py:26-29` from `:36`, `:44`, `:52`, `:59`); Q = 0.000 and a
single component before *and* after the refactor. A reader should take D3 = 2
here as "one real effect port bolted onto a god-state core".

## D4 — behavior preservation: 3

Six behaviors enumerated by the fixture's suite and each shown to hold with
assertions byte-identical; the model-derived leg is real (TLC re-run on the same
invariant, plus 716 exhaustive transition cases executed against unchanged
adapters, `campaign_tail.txt:1-3`).

Not 4, by the take-the-lower rule: the deliberate behavior-breaking changes that
*were* caught exercise the effect provider built after the refactor, not the
instrument that validated the refactor, and they are recorded as an agent-written
summary rather than raw output. The corroborating message match is why this is
still a 3 and not a 2.

## D5 — honesty: 3

Anchors 2 and 3 are met inside the artifacts: the provider's usage file names the
bypass it cannot observe and the in-memory limit (`:10-12`); the decision doc
lists residual complexity it accepts rather than arguing away (`:71-74`); the
probe file opens by refusing to count a green campaign until the assertions are
shown to bite (`:1-4`). The record carries a real unflattering result — two runs
of the same fixture classified the same variables oppositely (VAL-15).

Held at 3 because the run verdicts reach past the evidence: "provably kill
content bugs" and "the compounding the two epics were built for" from two probes
on one port, and the one class the provider asserts but never probes (ordering)
is never named as unmeasured. Naming it would have cost a sentence.
