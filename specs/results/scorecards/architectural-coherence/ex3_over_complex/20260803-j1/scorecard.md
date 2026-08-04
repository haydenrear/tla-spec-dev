# ex3_over_complex — judge pass 1 (`20260803-j1`)

scorecard_version 1 · commit `ab0dfee` · arm `null` (single-artifact eval)
Judge: `claude-opus-5[1m]`, pass 1, blind to arm.

| D1 | D2 | D3 | D4 | D5 | total |
|---|---|---|---|---|---|
| 2 | **3** | 1 | 3 | 3 | **12**/20 |

**This fixture is deliberately over-complex.** Its low D3 is what it was built to
have. Its D2 of 3 is the only 3-or-better complexity score in the set, and it is
earned by committed before/after descriptors, four times over.

## What I re-ran myself

`analyze complexity` on the pristine baseline, read-only at this commit:
bound **8,388,608** COMPLETE over 6 of 6 variables, Q = 0.000, **one** component,
**three dense rows** (`auditLog`, `dirty`, `mode`, all 4/4) and **three dense
columns**. The baseline in `PREDICTIONS.md` reproduces exactly.

## D1 — bug detection: 2

The fixture alone is anchor-0 territory: six pytest tests over a dict
(`test_order_hub.py:9-53`), no seeded faults, no content oracle, no I/O to observe.

Run 4's agent-authored provider is real content-asserting code —
`ex3-run4/artifacts/providers.py:71-99` raises on a per-entry operation-name
mismatch, on a count mismatch between the stored journal and the modeled
`auditLog`, and on out-of-order sequence numbers. Two deliberate faults were seeded
and both killed (`assertion_probes.txt:6-16`): a dropped effect caught by the count
assertion, a wrong operation name caught by the per-entry content assertion — file
restored byte-identically, tests green afterward. Wrong-value and wrong-content
through adapters that assert content: anchor 2.

Anchor 3 is not attempted. No refusal, no ordering, no cross-aspect before-state.
The provider *has* a `consecutive_seq_ordering` assertion (`providers.py:99`) but no
ordering fault was ever seeded against it. Two faults, both predicted to die, both
dying, is anchor 2 and nothing more.

## D2 — complexity: 3

The card requires the judge to say **what got simpler and how the behavior survived
it** before awarding 3. Here it is.

**What got simpler, part (a):** `OrderHub.tla:10-16` declares domains far wider than
any guard enforces — `orders 0..15` against a guard of `< 3`, `retries 0..31`
against `< 2`, `auditLog 0..63` against `< 12`. Honest resizing alone reaches
**6,240**, and run 2 measured it with generated *and* distinct state counts
**byte-identical** before and after (1,878 / 717). That is the cleanest possible
evidence: nothing reachable moved, only the declared representation shrank.

**What got simpler, part (b):** the remaining 6,240 → 624 is the **deletion** of
`mode` and `dirty` from the model *and* the production code
(`descriptor_before.txt:24` → `descriptor_after.txt:22`; dense rows
`descriptor_before.txt:48-51` → `descriptor_after.txt:44-45`, 3 → 1).

**How behavior survived:** TLC green under the same `Inv`, the six behavior tests
byte-identical and passing, depth and outdegree constant, and generated and distinct
falling *together* — which is not the deleted-self-loop pattern the tool warns
about. Run 1's agent applied that check unprompted (`ex3-run1/scoring.md:12`).

**Not 4, and MF-020 is exactly why.** Anchor 4 requires the simplification be
*shown* behavior-preserving. Part (b) is a deleted edge whose preservation rests on
six hand-written tests that never referenced the deleted variables — a check that
could not have failed on that change. Torn between 3 and 4, lower per rule 5.

## D3 — modularity: 1

`order_hub.py:15-60` is one module in which four functions mutate one shared dict,
and every one routes through `_stamp` (`order_hub.py:26-29`), which writes `mode`,
`audit_log` and `dirty` on every call. My descriptor run confirms the model side:
Q = 0.000, one component, three variables touched by 4 of 4 actions, three dense
columns. That is anchor 0's wording — state written from everywhere, no boundary
discernible.

What lifts it to 1: run 4 **declared** a boundary — an `AuditJournalPort` with an
`on_audit` seam and a generated runtime-checkable Protocol
(`ex3-run4/artifacts/effect_provider_usage.yaml:1-10`) — and the shipped code does
not carry it. No artifact in this repository contains the ported `order_hub.py`,
only the provider that would bind to it. A boundary named in a declaration that the
shipped code does not follow is anchor 1.

Recorded: there is no I/O in this fixture at all, so "domain independent of I/O" has
nothing to be independent of, and no swap could be named.

## D4 — behavior preservation: 3

Anchor 3 is met. Behaviors enumerated one test per rule
(`test_order_hub.py:9-53`) and each shown to hold after every refactor with zero
assertion changes across four runs. The check is model-derived: `OrderHub.cfg:3`
checks `Inv` under TLC, the transition-level red-flag test was applied unprompted,
and run 4 generated 716 exhaustive transition cases and ran a 3,580-point campaign.

Anchor 4's condition is literally met (`assertion_probes.txt:6-19`). I take the
lower anchor because **the change whose preservation matters most is the one the
check could not have failed on**: three of the four runs deleted `mode` and `dirty`
from the model *and* the production code, and the six tests never referenced either
variable — so "tests pass unmodified" cannot distinguish removing dead state from
removing behavior. The epic knows this: `ex3-run2/scoring.md:11` records that a
second agent read the same descriptor and the same doc and **kept** them as the
program's stated design. Two runs disagree about whether that deletion loses
behavior, and nothing in the check can settle it.

## D5 — honesty: 3

Anchor 3 is clear, and the record refuses to round up:

- `ex3-run2/scoring.md:11` scores E3-P2 **PARTIAL** against the committed
  prediction because the dense-row clause was not met — a prediction scored against
  itself rather than reinterpreted.
- VAL-15 (`ex3-run2/scoring.md:27-39`) files the honest negative that two reasonable
  agents put the same write-only stamped state on opposite sides of the intuition
  doc's line — the doc under test is ambiguous.
- `ex3-run3/scoring.md:22-27` records a blind spot in the tool itself: the
  invariant-coverage section counts a `TypeOK` type conjunct as a semantic read, so
  write-only variables show clean coverage.
- `ex3-run1/scoring.md:22-33` files three toolchain defects including VAL-04, the
  scaffold contradicting its own advisory doctrine.
- The tool's own output refuses to convert a number into a verdict — I saw "A poor
  score is not a verdict" and the deleted-self-loop red-flag paragraph in the
  descriptor I ran.

**The strongest argument for 4**, recorded so a second judge can see where the line
fell: `ex3-run4/artifacts/effect_provider_usage.yaml:10-12` declares a
`bypass_limits` block *in the artifact*, naming what the provider cannot observe (a
bypass that edits `order_hub._audit` directly; in-memory only, no cross-process
observation). That meets anchor 2 in the artifact rather than in a report, and the
items above meet anchor 4's bar.

**What stops 4:** the run verdicts generalize past their evidence — run 1 closes
"the sharpest test passed", run 4 closes "This is the compounding the two epics were
built for" — and no ex3 record states the limit that this is one 60-line program
with six hand-written tests, no I/O, and a deliberately inflated representation.
Genuinely a 3-versus-4 call; lower per rule 5.

## Verdict

The only fixture in the set that measures a simplification with committed before and
after descriptors, four times over, and the one place the toolchain demonstrably
changed behavior — but half its headline reduction is a variable deletion validated
by six tests that never read the deleted variables, and its shipped code has no
boundary at all.
