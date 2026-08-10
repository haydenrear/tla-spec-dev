# Epic: portable substrate

**Starter for the next epic agent. Read this before the plan.**

Branch `epic/portable-substrate`, cut from `main` at `19c5c7b` after
`reading-discipline` merged. Canonical plan:
`specs/desired_program_model/ticket_plan.yaml`. Prior record: `NEXT-EPIC.md`
§0-AAAAAA.

---

## 1. The one sentence

**Remove what has been measured dead, then prove the two dimensions that
survive — and use "could someone else adopt this?" as the stopping rule for how
much to cut.**

Remove first, then iterate. You cannot demonstrate a dimension works while
carrying instruments already known not to.

---

## 2. What is being removed, and why it is safe to say so

Four interventions have now been measured against a control. **Two survived.**

| lever | verdict | evidence |
|---|---|---|
| the prompt → D3 | **works** | 1 → 4, replicated; length-matched arm C scored 1/1 |
| a revision pass → D2 | **works** | 2 pairs cleared; byte-identical pair refused 4/4 |
| model-derived cases find bugs | **fails** | 0 unique kills vs 4 the other way, on new subjects |
| static gates catch defects | **fails** | five epics, no caught bug |

Plus the suite as a **finding channel**: one finding in seven rounds. It is a
fine regression guard. That is a different job and it keeps that job.

---

## 3. The thing that makes this epic hard

**The instrument that prices removals can only return zero.**

A gap mutant can price a removal only if *every* detector that killed it is one
that removal deletes. Over the sealed before-table that is **0 of 9**. And the
re-runnability rule **systematically excludes exactly the faults that could go
`DIES`→`SURVIVES`** — the one fault the `[ports.*]` machinery uniquely caught was
declared `not_seedable` *because it cannot be re-run after the cut*.

So two epics of "free" removals were **free by construction**, and the epic that
called itself the great simplification came out **net +1677 lines**.

**RM-01 exists to fix that before anything is cut.** If RM-03's removals all
price at zero again, that is a finding about RM-01 — not three free cuts.

---

## 4. Why portability is in a removal epic

The scorecard has only ever graded this repository's own methodology. The owner
intends to expose it so external projects grade their own architecture, and so
that regressions they find by hand become card and architecture iterations they
choose for themselves.

That is strategic. It is also **the only non-arbitrary stopping rule available**:
*"simplify"* has no natural end; *"could a project that did not build this adopt
it?"* does.

**RM-02 must not let this become a reason to add.** If the honest answer is that
adoption requires *less*, that is the more useful finding.

---

## 5. Doctrine that carries forward unchanged

- **No new gates.** Five epics, zero bugs caught by a static check.
- **Complexity is a thermometer** and may not choose the boundary (`CD-01`).
  **And it could not see the only simplification ever measured** — 19 of 21 axes
  byte-identical, one moving the wrong way, while eight judges found it
  independently. **Do not add an axis tuned to the known answer** (`MF-020`).
- **`R3`: a claim carries its scope.** `scope` has **three** bounds now; name the
  one that applies.
- **`R-H1`/`R-H2`**: same example, unchanged instrument, same architecture tag.
  Never average across examples.
- **Record judge tier.** Four splits are on the record, three unlooked-for, one
  running in opposite directions — **and D2 split too**, on magnitude.
- **R1**: an instrument ships with a demonstrated *failing* input on a real
  subject.
- **`denominator_rule`**: say whether the numerator rose or the denominator fell.
- **Commit predictions before dispatch. If every prediction passes, that is an
  ALARM.**
- **File findings; fix nothing during a measurement.**
- **Ask every blind agent what it REJECTED.**

---

## 6. Operational rules this project has paid for

- **`wt new` branches from the LOCAL ref.** It has put tickets 4, 14 and 21
  commits behind. **Verify your branch point against the SHA in your work order.**
- **Do NOT report `git archive` figures as tree properties.** Those tests read
  git history; the archive has no `.git`. Nine of ten "archive failures" were
  that, in an instruction the owner gave three tickets and retracted.
- **Do NOT hand-roll a wait loop for a run you started.** Two agents stalled that
  way last epic, one for over an hour after its work was already pushed.
- **Never kill a process by name alone** — scope `pkill` to your worktree.

---

## 7. The standing rule

**A low or unflattering result is the preferred outcome.**

The predecessor's best material was that its own founding premise was false, and
that its owner's instructions had put a phantom figure into three ticket records.

**An epic that closes with only good news about itself has not been measured.**
