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

> **CORRECTED 2026-08-16, after SS-01's review. THE ROW BELOW PREVIOUSLY READ
> "20 REFUTED, all from the ledger; plus 3 UNREACHABLE from `NEXT-EPIC.md`".
> THAT WAS AN INFERENCE, NOT A MEASUREMENT.** I had two marginal totals — by
> file `20/3` and by verdict `20 REFUTED / 3 UNREACHABLE` — and **assumed they
> cross-tabulated. They do not.** The cross-tab was never run until the SS-01
> review forced it. Corrected figures below; the totals, the file attribution
> and `102 − 23 + 3 = 82` were all correct and are unchanged.
>
> **The consequence is that I corrected a figure that was right.** Issue #271's
> *"17 REFUTED figures currently unswept"* is **exactly right** — the ledger
> carried precisely 17 REFUTED rows and they were unswept — and `CA-10-DF-18`
> instance 5 had already measured and written both numbers. My wrong version
> reached the charter, the plan, issue #273 and, via SS-01, a comment inside
> `score_tools.py`. `SS-01` then over-corrected on top of it and its reviewer
> refuted that in turn. **Three parties, one un-run cross-tab.**

| movement | count | attribution |
|---|---:|---|
| **gone** | **23** | **17 REFUTED + 3 UNREACHABLE from `specs/desired_program_model/deferred_findings.yaml`** — the live ledger the workflow close **deleted** — plus **3 REFUTED** from `NEXT-EPIC.md` |
| **added** | **3** | `NEXT-EPIC.md`, re-anchored by the `0-AAAAAAAAAA` amendment, **REFUTED**, a net wash against the 3 REFUTED it lost |
| net | **−20** | `102 − 23 + 3 = 82` ✓ — **and all 20 net-lost rows are ledger rows, so the ledger accounts for the movement exactly** |

> **SUPERSEDED 2026-08-16 by `SS-01` at `50046b2`.** `SS-01` added the relocated
> ledger to `DEFAULT_SWEEP`, and `scope` now reads **103** (81 REFUTED, 2 HOLDS,
> 20 UNREACHABLE). **The baseline of 82 is superseded and the cause is a ticket,
> not a claim being resolved** — `SS-04` measures against 103 at `50046b2`, and
> `SS-08` reports the movement as denominator, named.

**This is denominator movement caused by a file disappearing, not by any claim
being resolved.** No figure was checked, refuted or repaired to produce it.

**It also prices open decision #3 — and my pricing of it was wrong too.** Issue
#271 §7.3 says the cost of leaving `DEFAULT_SWEEP` globbing the dead directory is
*"17 REFUTED figures currently unswept"*.

> **CORRECTED 2026-08-16. I wrote that "17 is the current whole-record
> UNREACHABLE count, not the unswept-REFUTED count". #271 WAS RIGHT: the ledger
> carried exactly 17 REFUTED rows and they were unswept.** The whole-record
> UNREACHABLE count is *also* 17, and that coincidence is what made the
> misreading plausible — it misled me and then misled `SS-01`, which repeated a
> sharper version of it into `score_tools.py`.
>
> **And `SS-01` found why the counts looked inconsistent, which is the useful
> part:** `scope --path` on the ledger reaches **21 (18 REFUTED, 3 UNREACHABLE)**
> when run against a bare root, and **20 (17 REFUTED, 3 UNREACHABLE)** when the
> same bytes are swept inside the repository. **A `scope` verdict is a joint
> property of the file and the tree it is swept in, and the output records
> nothing about which root was used** — `SS-01-DF-03`, carried to `SS-04`.

The residual point stands and is unaffected: **21, 20 and 17 are three different
readings that look alike**, and `SS-01` reconciled them on the record — 21 under
a bare root, 20 in the repository, 17 of those REFUTED. **`SS-01` also acted on
it**, adding the relocated ledger to `DEFAULT_SWEEP` and taking `scope` to 103.

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
