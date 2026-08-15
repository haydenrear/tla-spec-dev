# CA-08 — sealed predictions

**Sealed 2026-08-14T04:55:58Z (2026-08-14 00:55:58 EDT), in this commit, BEFORE
any measurement was run.**

Written from: issue #262, `CUT-THE-APPARATUS-EPIC.md`, `ticket_plan.yaml`
(schedule_revision 2), and the four `baseline.md` files under
`specs/results/scorecards/cut-the-apparatus/`. **Nothing under any contributor's
`RESULT.md`, `PRICE-TABLE.md`, `FINDINGS`, or the ledger has been opened at the
time of sealing. No line count, no card serve, no suite run, no `scope`, no
`disposition.py` run has happened.**

Tree at sealing: `feature/CA-08` at the epic tip
`ea624b9723cb10d1864da67400e52dd032c6ed49`.

The last evaluation in this project (`SV-05`) declared an **ALARM against
itself** for sealing after measuring. This file exists so that cannot be said
of `CA-08`. **If every prediction below passes, that is itself an ALARM and
must be reported as one** — a prediction set that never fails was fitted to a
known answer (`MF-020`).

---

## P1 — `GOAL-apparatus-cut` (a): the 30% cut is MISSED

`scripts/` + `examples/validation/` Python lines at the tip will be **above
30,487**. Point estimate **38,000–43,000**, i.e. a cut of **less than 15%**.

Reasoning sealed with it: the charter's own do-not-cut list protects
`analyze_complexity.py` (2,401), `code_complexity.py` (968), `scope`, `seal`,
`contested` and the double seal; `CA-06` was told to **simplify, not delete**
the 3,471 + 2,455 line TLA+/adapter path; and `score_tools.py` (3,571) is the
card's own server. That is most of the mass, ring-fenced before the epic
started.

## P2 — the epic is net-additive on the whole tree

Counting **all** tracked lines (`.py` + `.md` + `.yaml`) across the diff
`08d1d6a…ea624b9`, the epic **added more than it removed**. `RM-03-DF-03` says
this outcome is required by construction for card removals and three previous
"simplifications" produced it. **I predict this one did too**, and that the
apparatus-only figure is the flattering slice.

## P3 — `GOAL-apparatus-cut` (b) is MISSED

At least one of the following will hold when the price tables are audited
against `git diff --stat 08d1d6a..ea624b9`:

- a deleted path with no finding ID in any price table; **or**
- a price-table figure that does not match the actual diff; **or**
- a deletion in the diff that appears in **no** price table at all.

I expect the third. `CA-02` established the format at ticket 2 of 7, so
whatever CA-00/CA-01 removed predates the format.

## P4 — `GOAL-apparatus-cut` (c) is MET

`score_tools.py serve | wc -c` is **exactly 6,281** at the tip and
`serve --digest-only` is **unchanged at `sha256:2d7d4a0506d9b259`**, card
version 5. The charter forbade touching the card and nobody had a reason to.

## P5 — `GOAL-apparatus-cut` (d) is MET

Every ticket reported `scripts/` and `examples/validation/` separately. The
format file mandates it and `CA-02` wrote the format.

## P6 — `GOAL-consumption-obligatory` (a) is MET

`scripts/disposition.py` exists, runs, and **refuses `cut-the-apparatus`** at
this tip on a real input. Commit `88165bd` is titled "the requirement still
refuses the epic", so the refusal is real and not a fixture.

## P7 — `GOAL-consumption-obligatory` (b) is MET but the movement is BOTH ways

The true denominator is stated as **41** (38 + `SV-01-DF-05`'s 3) and the
numerator as **2**. Under `denominator_rule` this is **numerator +1 AND
denominator +3** — the rate 1/38 (2.6%) → 2/41 (4.9%) is not a clean
improvement and I predict at least one document in the epic quotes the
percentage without the denominator move.

## P8 — `GOAL-consumption-obligatory` (c) is MISSED

`channel` exists on the ledger. **`cost` is populated by fewer than half of
this epic's eight tickets** — I predict **3 or fewer of 8** recorded a token
basis, and that at least one ticket honestly recorded "not instrumented".
`CL-04` proposed `cost` three epics ago and one ticket of six recorded one last
epic; nothing in the seven contributors' work orders made it mechanical.

## P9 — `GOAL-blind-dispatch` (a), (c), (d) are MET; (b) is MET

`--safe-mode` from a neutral cell carries neither the auto-memory nor the
commit subject lines, and CA-01 + its reviewer measured the inventory. I
predict my own fresh dispatch through that path **confirms** it.

## P10 — my own blind agents will still report SOMETHING they were not meant to have

Not the memory and not the commit subjects — but I predict at least one fresh
agent reports receiving **the working directory path** (which contains the
string `tla-spec-dev` and, if run from the ticket worktree,
`cut-the-apparatus-CA-08`) and treats it as informative. **Blindness by this
path is blindness to the operator's conclusions, not blindness to the
project's identity**, and I predict the round shows that.

## P11 — `GOAL-four-results-stand` (a) is MET, (b) is MET, (c) is MET

All four results still reproduce from the sealed record; the suite lands at
**8 reds** (the epic-tip baseline named in my work order), with no red
attributable to CA-08.

## P12 — but at least one of the four is now READABLE and not RE-DERIVABLE

I predict at least one of the four results, or one of the four disproofs, has
lost its **running instrument** while keeping its sealed transcript — most
likely **disproof 1** (`0 unique kills`), because `CA-04` was assigned
`kill_test.py` (1,149 lines) and the baseline explicitly orders CA-04 to state
whether disproof 1 is still reproducible once the instrument is gone. The
price-table format's own §5 demands READABLE and RE-DERIVABLE be answered
separately **because `CA-02` got exactly this wrong**.

## P13 — the static-gates doctrine as worded is FALSIFIED

"Static gates catch nothing — seven epics, zero bugs" does **not** survive this
epic. I predict the catch/false-refusal ratio comes out **3 catches : 1 false
refusal**, and that the wording that survives is narrower — about **gates on an
adopter's code**, not about close-out obligations on this project's own record.
I further predict that **no** cell in that ratio is a *bug in shipped code*:
every catch is a catch about the **record**, which is why the original wording
was ever defensible.

## P14 — findings-by-channel: fewer than half the tickets recorded their own basis

Consistent with P8. I predict the epic's aggregate findings-per-100k-tokens
figure is **not computable across all seven contributors** from what they
recorded, and that the honest report is a partial table with named gaps rather
than a single ratio.

## P15 — `scope` reaches more rows at the tip than at the base

Because the epic added prose. I predict `scope`'s coverage of the epic's **own**
prose is **under 50%** and that CA-03's finding — `scope` reached **none** of
its prose — replicates in spirit at CA-08: `scope` is bounded to the sealed
scorecard record and does not read charter/`NEXT-EPIC.md`/epic markdown.

## P16 — the five recurring classes are NOT five distinct things

I predict **`CA-00-DF-05`'s class (a scoped result restated unqualified) and
the line-number-citation class are the same failure** — citing a locator
without re-reading the thing it locates — and that `SF-307` (a grep cannot find
an absent argument) and "instruments that certify what they cannot see" are
**also the same failure** at two altitudes. So: **five names, three things.**

## P17 — NOT every prediction passes

The meta-prediction. I expect **P1, P3, P8, P13(partly), P14** to pass and at
least one of **P7, P11, P12, P15, P16** to fail. If all sixteen above pass,
**that is the ALARM** and it will be reported as one in `RESULT.md`.

---

## What I have deliberately NOT predicted

- The exact line-count figure. A point estimate wide enough to always be right
  is not a prediction; P1's claim is the **verdict** (missed) plus a band.
- Whether any specific finding ID exists. I have not read the ledger.
- The card digest changing. P4 predicts it does not; if it did, that is a
  charter violation and a finding, not a prediction miss.
