# Epic: reading discipline

**Starter for the next epic agent. Read this before the plan.**

Branch `epic/reading-discipline`, cut from `main` at `946b1ee` after
`subtract-to-measure` merged. Canonical plan:
`specs/desired_program_model/ticket_plan.yaml`.

---

## 1. The one sentence

**Six epics have closed on the same finding — a claim read forward without being
checked — and every fix so far has been a rule someone has to remember. This
epic makes scope-loss catchable by machine.**

Not a new mechanism. The *reading* of the ones we have.

---

## 2. The three instances, in ascending cost

- **`contested` is a scoring rule with no implementation.** Rule 5 says a spread
  > 1 is contested and needs a third pass on new evidence. Every card ever
  written carries `contested = []`. On the toolchain removal D3 was **2, 2, 3,
  4 — spread 2** — and `index` printed `—` on all four rows.
- **D3 was called "the one dimension that discriminates and holds still"** on
  the strength of one example. On a second subject it spread 2 and **split by
  judge tier** — `opus` 2, 2 against `sonnet` 4, 3.
- **An entire epic was justified by `D2 = 2 on 27 of 27 cards`.** That was true
  of **`ab_quota_ledger` alone**. Across all 49 sealed cards D2 has taken **four
  values over seven examples**, and `ex3_over_complex` scored **3 from both
  blind judges three epics earlier**, under the same anchors digest. The epic
  owner wrote the claim into the charter, the plan and the issue, repeated it
  four times, and "verified" it with a script containing
  `if "ab_quota_ledger" not in f: continue`. **The check was scoped to one
  example and the result reported as a property of the card.**

`R-H2` forbids **averaging** across examples. **Nothing forbade generalising
from one.** That gap is the epic.

---

## 3. The same defect one granularity up: architecture

*"D2 = 2 on 27 of 27"* is a claim scoped to one **example**, generalised.
*"D3 = 4 means modular"* is a claim scoped to one **architecture**, generalised.

The card is not comparable across architectures and nothing records which
architecture a score describes:

- a **ports-and-adapters** program is validated through port-bound adapters and
  per-port cases; a flat **effectful** program is validated through the effect
  oracle, in-process CPython only, driving 8 of 18 actions. **Same D1 anchor,
  different instrument reach.**
- D3's contested spread came from judges disagreeing about **what the artifact
  is** — one refused a D3 = 4 its own execution supported *because the port
  lives in a fixture*.
- `R-H1` already carries two comparability axes: same example, unchanged
  instrument. Architecture is the third and has always been implicit —
  `ex6_jenga` is *supposed* to score low on D3, handled today by prose telling
  readers not to average.

**RD-04 researches it; RD-05 implements what RD-04 decides.**

---

## 4. The rule this epic adds

**R3 — a claim carries its scope, and something refuses it when it does not.**
A figure of the form *"D<n> = k on N of N"* is a statement about whichever
examples, instruments and architectures produced those N cards. If the
underlying set is wider than the claim admits, the claim is wrong even when
every number in it is right.

---

## 5. And the trap this epic must not fall into

**A tag can become a suppression key.** If any unflattering comparison can be
dismissed as "different architecture", the card stops being able to say
anything — and this project has already shipped a construct that erased a
demonstrated kill with `verified: true, green: true, exit 0`.

Three guards, and they are not negotiable:

1. **Declared before scoring, derived where derivation is possible.** A tag
   asserted after the numbers are seen is not a tag.
2. **`INCOMPARABLE` is reported, never dropped.** A missing row and an
   incomparable one are not the same claim.
3. **A tag value earns its place by demonstrating it changes a score.** If two
   artifacts differing only in it score identically on all five dimensions, it
   distinguishes nothing and is deleted. **The vocabulary is falsifiable or it
   is decoration.**

---

## 6. Doctrine that carries forward unchanged

- **No new gates.** Five epics, zero bugs caught by a static check.
- **Complexity is a thermometer.** `CD-01`: it may not choose the boundary.
- **`MF-020`**: a metric falling is not evidence the design improved.
- **R1**: an instrument ships with a demonstrated *failing* input.
- **R2**: a control that cannot fail is worse than no control — report it RED.
- **`removal_is_a_delta_rule`** and **`denominator_rule`** stand.
- **Commit predictions before dispatch, with negatives that name their own
  falsifier.** If every prediction passes, **report it as an alarm.**
- **File findings; fix nothing during a measurement.**
- **Ask every blind agent what it REJECTED.** Six of seven rounds, the suite
  produced **zero** findings; that question produced most of them.
- **Never edit a target to match a result. Report the run that happened.**
- **Three commands that look local and are not:** `git worktree add`,
  `pkill -f`, and `wt new` off a stale ref — which branched a ticket **21
  commits behind**. Verify your branch point against the SHA in your work order.

---

## 7. The standing rule

**A low or unflattering result is the preferred outcome.** The predecessor's
best material was the discovery that its own founding premise was false, found
by the evaluation it had scheduled to check itself.

**An epic that closes with only good news about itself has not been measured.**
