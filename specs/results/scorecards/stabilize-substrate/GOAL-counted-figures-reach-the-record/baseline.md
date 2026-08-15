# `GOAL-counted-figures-reach-the-record` — baseline

**Tree: `436c78c55c60c3ee45901223176124df5e38b6ff`**, the epic base, measured on
`epic/stabilize-substrate` before any ticket landed.

**Raw output, sealed, in this directory:**

- `scope-work-directing-docs-436c78c.txt` — five `scope --path` runs
- `scope-whole-record-436c78c.txt` — the default sweep

---

## 1. `scope` is blind to the documents that direct the work

```
scope --path STABILIZE-SUBSTRATE-EPIC.md                    0 counted figures
scope --path CUT-THE-APPARATUS-EPIC.md                      0 counted figures
scope --path specs/desired_program_model/ticket_plan.yaml   0 counted figures
scope --path .../cut-the-apparatus/GOAL-apparatus-cut/baseline.md   0 counted figures
scope --path NEXT-EPIC.md                                   3 counted figures, 3 REFUTED
```

**Including this epic's own charter, which is full of `<n> of <m>` sentences.**

**The bound is the sentence form, not the corpus, and this is
reviewer-confirmed:** those files **are** swept. `scope` recognises one form —
`D<n> = <v> on <n> of <m>` — and *"0 of 9 over the sealed table"* is not in it.

**Do not overstate it.** `CA-08`'s own starter printed **four** of these five
rows and carried a heading — *"`scope` CANNOT READ ANY DOCUMENT THIS PROJECT USES
TO DIRECT WORK"* — that the dropped fifth row refutes. `scope` **does** read
`NEXT-EPIC.md`. The successor's starter must never be more absolute than the
epic's own measurement.

## 2. The whole-record sweep, and a fourth figure from the work order that moved

`CA-08` recorded the sweep as **byte-for-byte identical** at the predecessor's
base and tip: **102 figures / 80 REFUTED / 0 COUNT-MOVED / 2 HOLDS / 20
UNREACHABLE over 37 files**.

**At this tree it is 82 / 63 / 0 / 2 / 17 over 36 files.** Diffed against the
sealed `CA-08/goal/scope-tip.json` by `(file, line, span)`:

| movement | count | attribution |
|---|---:|---|
| **gone** | **23** | **20 REFUTED, all from `specs/desired_program_model/deferred_findings.yaml`** — the live ledger the workflow close **deleted**; plus 3 UNREACHABLE from `NEXT-EPIC.md` |
| **added** | **3** | `NEXT-EPIC.md`, re-anchored by the `0-AAAAAAAAAA` amendment, and now **REFUTED** where the three they replace were UNREACHABLE |
| net | **−20** | `102 − 23 + 3 = 82` ✓ |

**This is denominator movement caused by a file disappearing, not by any claim
being resolved.** No figure was checked, refuted or repaired to produce it.

**It also prices open decision #3 concretely.** Issue #271 §7.3 says the cost of
leaving `DEFAULT_SWEEP` globbing the dead directory is *"17 REFUTED figures
currently unswept"*. Re-derived: `scope --path specs/deferred_findings.yaml`
reaches **21 counted figures — 18 REFUTED, 3 UNREACHABLE**. **17 is the current
whole-record UNREACHABLE count, not the unswept-REFUTED count**, and the two look
alike. `SS-01` owns the exact reconciliation.

## 3. Why this matters more than its size suggests

**Every counted figure that has ever hurt this project is invisible to the
instrument named to catch it** — *"0 of 9"*, *"1 of 38"*, *"four rounds'
claims"*, *"8 failed, 1490 passed"*, *"seven epics, zero bugs"*.

The predecessor's charter carried a correction block reading *"`R3`/`scope` would
have caught this and nobody ran it against this charter."* **It was run. It
returned zero.** `CA-08-DF-01`, and the evaluation called it the most useful
thing it found.

## 4. The constraint on the fix, restated because it is the whole risk

**`MF-020` applies directly.** Five figures are named in §3 above **and their
answers are known**. A recogniser tuned until those five parse is **fitted to a
known answer** and fails clause (d) even if it works.

**And `UNREACHABLE` is the default.** A claim the instrument cannot reach is
**not** a claim that holds; the two counts stay separate on purpose, and the tool
prints that sentence itself on every run. **A false REFUTED is worse than an
UNREACHABLE.**

**Not a gate.** Nothing refuses, nothing blocks a close, no exit code changes.
