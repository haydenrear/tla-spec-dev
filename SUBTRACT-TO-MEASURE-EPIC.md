# Epic: subtract to measure

**Starter for the next epic agent. Read this before the plan.**

Branch `epic/subtract-to-measure`, cut from `main` at `3f58aca` after
`falsifiable-instruments` merged. Canonical plan:
`specs/desired_program_model/ticket_plan.yaml`.

---

## 1. The one sentence

**We have never given the scorecard a subject it could measure, so we do not yet
know whether it works — and the toolchain we built to measure with is the first
subject that could tell us.**

`D2 = 2` on **27 of 27 cards ever written**. Two explanations have never been
separated:

- **(a)** the card cannot measure complexity, or
- **(b)** there has never been anything to measure.

D2 anchor 3 requires *"a simplification was made and its effect measured — the
before and after figures are both recorded."* **Every subject this project has
ever scored was greenfield**: written once, from a prompt, with no before. **No
greenfield artifact can reach D2 anchor 3, ever.** So D2's constancy may not be a
defect in the card at all.

This epic produces the first real before/after: **a substantial, evidence-driven
removal from the toolchain itself**, which carries five epics of accumulated
complexity and — measured — mostly cannot be shown to work.

---

## 2. Why subtraction, on evidence

Five epics of adding. What the record says about what we added:

- **The `[ports.*]` binding machinery**: zero unique kills across 28 tables,
  absent from every blind-authored table, strictly dominated by the hand-written
  suite. It was the centerpiece of an epic.
- **The falsifiability registry**: reported 26 of 35 instruments with a
  demonstrated failing input. Swept, it is **at most ~11 of ≥43** — twelve
  demonstrations assert only `expect_exit = 0`, which a *fully skipped* run
  satisfies.
- **The suite as a finding channel**: **zero findings in five of six rounds.**
- **Gates**: three epics, zero bugs caught, each defeated cheaply.

What has earned its keep, and is not on the table:

- **The prompt.** D3 went 1 → 4, and arm C — length-matched, longer, no
  architectural vocabulary — scored **1/1**. Its author considered the exact seam
  and declined it on merit. Replicated, confounder-controlled.
- **D3.** The one dimension shown to discriminate (4/2/1) *and* hold still (zero
  movement across four rounds and 60 judge-scores).
- **The negative corpus**, narrowly: guard relaxation 0 → 3 of 3, a class nothing
  else reached.
- **The blind-author and adversarial channels**, which produced almost every
  finding worth having.

---

## 3. The trap, named before we start

`MF-020`: *a metric improving is not evidence the design improved — a number can
fall because an edge was deleted.* **Applied to ourselves: removing an instrument
removes the ability to detect that the removal was harmful.**

So `SM-01` goes first and alone: **seed a mutant in the gap each mechanism claims
to cover, before anything is removed.** After removal each mutant either still
dies (redundant, the cut was free) or survives (load-bearing, and we have just
priced it). **Both are results. A removal with no mutant in its gap is not a
measurement.**

Second form of the same trap: **deleting a hollow demonstration must not quietly
improve the ratio.** Report deletions separately from repairs. A ratio that rises
because the denominator shrank is `MF-020` wearing this epic's clothes.

---

## 4. What is deliberately NOT retired

**D2, D4 and D5 stay on the card.** It would be easy to drop them now — D2 is a
constant, D4 and D5 move two points on byte-identical code. **Do not.** The whole
experiment is to find out whether they were ever given a chance. Retiring them
before `SM-05` runs destroys the only measurement that could settle it.

**The corpus is not the ports machinery.** "Defund `[ports.*]`" is supported.
"Defund the corpus" is **not** — and the two must not be allowed to merge into
one cut.

---

## 5. Doctrine that carries forward unchanged

- **No new gates.** Four epics, zero bugs.
- **Complexity is a thermometer, never a thermostat.** `CD-01`: it proposes no
  cut. It may not choose the boundary — including in this epic, where the subject
  is our own boundary.
- **R1**: an instrument ships with a demonstrated *failing* input.
- **R2**: a control that cannot fail is worse than no control — report it RED.
- **Commit predictions before dispatch, with at least three negatives.** And if
  every prediction passes, **report that as an alarm**: a round where nothing was
  refuted measured nothing.
- **File findings; fix nothing during a measurement.**
- **Ask every blind agent what it REJECTED.**
- **Never edit a target to match a result. Report the run that happened.**
- **NEVER KILL A PROCESS BY NAME ALONE.** Ticket agents run concurrently in
  sibling worktrees on one machine, and `pkill -f run_gap_mutants.py` matches
  every worktree, not yours. Scope it to your own tree:

  ```bash
  pkill -f "<your-worktree-path>.*run_gap_mutants"
  ```

  This is the same class of mistake as a bare `git worktree add` — a command
  that looks local and is not — and it was found the same way: **SM-03 ran the
  unscoped form, disclosed it unprompted, and could not tell retroactively
  whether it had killed a concurrent ticket's measurement.** SM-02 was running
  a gap-mutant pass at the time.

  **If a run of yours aborts without an explanation you can account for, treat
  it as interrupted and re-run it.** Do not reason around a truncated artifact
  and do not reconcile a partial table into a complete one. An interrupted
  measurement is not a measurement.

  The rule is the epic owner's omission, not the agent's: the standing rules
  said this emphatically about worktrees and nothing about processes.

---

## 6. The standing rule

**A low or unflattering result is the preferred outcome.** The predecessor's best
material was the discovery that its own headline number was hollow, found by an
instrument it had built four tickets earlier.

**An epic that closes with only good news about itself has not been measured.**
