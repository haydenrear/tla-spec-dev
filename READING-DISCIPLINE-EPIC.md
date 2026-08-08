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

## 6a. What RD-01 measured, and what every later ticket must carry

**19 of 44 counted figures in this repository do not survive a check.** 19
REFUTED · 11 COUNT-MOVED · 6 HOLDS · 8 UNREACHABLE, against a baseline of zero.
Four are live assertions, including the figure `subtract-to-measure` was opened
on; nine more are quotations that carried them forward; **one sits inside the
section of `references/eval_scorecard.md` that declares R3 itself.**

Three things follow that bind the rest of this epic:

**"The suite is green" has never been true in a ticket worktree** (`RD-01-DF-02`,
owner-verified by direct comparison). `test_card_has_one_home.py` and
`test_code_complexity.py` walk the gitignored `.claude/` and `.skill-manager/`
homes **that `wt new` itself creates**, and those homes hold copies of the card
and of the instrument. Same two files: **44 passed** in a tree with no homes,
**2 failed** in a ticket worktree. Zero tracked-file violations either side — a
false-positive class in the tripwires, not a defect in the tree.

> **Say which tree a suite number came from.** A green from a ticket worktree
> was never green, and a red from one may be this and not you. The epic owner
> reported ticket-worktree greens as evidence for several rounds.

**Rule 5's third pass has never been applied to anything, ever** (`RD-01-DF-03`).
`contested` now computes and fires on exactly one group in 49 sealed cards. The
rule says that group needs a third pass citing **new** evidence. Either run it or
record that it will not be run and why — a rule that fires and is then ignored is
worse than one that never fired.

**A tier split is a real effect and there are three of them**, two of which
nobody had looked for: D3 `opus`[2,2] vs `sonnet`[3,4]; greenfield D4
`opus`[2,2] vs `sonnet`[3,3]; and greenfield D5 `opus`[3,3] vs `sonnet`[2,2] —
**running the other way.** D2 overlaps. Record the tier on every card you
produce, and do not compare across tiers without saying so.

---

## 6b. OWNER RULING: deriving a tag is not a thermostat, and the invariant must say so

**RD-04 escalated this as blocking and was right to.**
`test_no_reader_of_this_instrument_gates_on_its_output` states a repository-wide
invariant: a file *"is allowed to refer to the instrument and to transcribe its
figures. It is not allowed to branch on them, compare them, assert on them or
exit on them — that is a thermostat, whatever it is called."* **The tag's
derivation predicate branches on exactly those figures.**

**The ruling: the invariant means a figure deciding something about the CODE.
Deriving a comparability label is not that, and the invariant's wording is
wrong rather than the design.**

The distinction that decides it, and it is `CD-01`:

- **Choosing the boundary** — "your port should go here" — is forbidden, because
  a tool that picks the cut makes every edge legal by construction.
- **Observing where the boundary already is** — "these effectful calls sit in one
  module" — is the thermometer's entire job. The tag reads where the boundary
  *is*. It proposes none, refuses none, scores none.

`no_new_gates_rule` already draws this line: **a tag constrains what may be
COMPARED and refuses nothing about the code.**

**Three conditions on the ruling, and they are not optional:**

1. **RD-05 does not add itself to `GATING_SCAN_EXEMPT`.** RD-04 is right that a
   unilateral exemption would be the wrong repair. **Fix the invariant's
   statement** so it says *gating on the code*, and make the distinction
   explicit in the docstring. An exemption hides a correct rule; a corrected
   rule survives the next reader.
2. **The new risk is a wrong predicate, not a wrong principle.** A derivation
   that misfires suppresses a *legitimate* comparison — the suppression key
   arriving through a bad predicate rather than through malice. So the
   derivation must be checkable against the artifact, and a
   derivation/declaration disagreement must **fail open**, which RD-04's design
   already does. Keep it.
3. **State the ruling's own limit.** The separation the tag rests on is
   **`opus`-only, n = 0 in `sonnet`** (RD-04 §9.1). A ruling that a mechanism is
   sound does not make the evidence under it wider than it is.

---

## 7. The standing rule

**A low or unflattering result is the preferred outcome.** The predecessor's
best material was the discovery that its own founding premise was false, found
by the evaluation it had scheduled to check itself.

**An epic that closes with only good news about itself has not been measured.**
