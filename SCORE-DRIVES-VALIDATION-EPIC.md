# Epic: score drives validation

**Starter for the next epic agent. Read this before the plan.**

Branch `epic/score-drives-validation`, cut from `main` at `eab2883` after
`close-the-loop` merged. Canonical plan:
`specs/desired_program_model/ticket_plan.yaml`. Prior record: `NEXT-EPIC.md`
§0-AAAAAAAA.

---

## 1. The owner's goal, in two halves

1. **Any project being onboarded can, during any and all epics and as part of
   the goal process, score its VALIDATION and its ARCHITECTURE.**
2. **From that goal and scorecard, new validation is introduced into the
   project** — improved architecture and diagrams, and integration and unit tests
   derived from them.

**Half one is half true. Half two has never been attempted.**

---

## 2. What is already true, measured

- **The card is portable.** A blind adopter — forbidden our `.py` source, all of
  `specs/`, our tests and our git history — ran serve → scaffold → fill → check →
  seal → audit → **bump to version 6** → re-score, on a program it wrote itself.
- **Architecture scoring works and travels.** D3 separated on a second example
  across both judge tiers, and its caveat **fired correctly on a stranger's
  artifact it was never written for.**
- **The loop closes.** Regression → card iteration → re-score, twice, in
  opposite directions.

---

## 3. The three gaps this epic exists for

**THE CARD CANNOT SCORE VALIDATION, AND WE REMOVED THAT ABILITY ON PURPOSE.**
At version 5 it serves **exactly two scored dimensions**; three more are
**recorded notes that take no score**. Run
`score_tools.py serve` and read them there — this page does not restate them,
because only the card may say what a dimension is. **The two retired to notes
were the validation dimensions.** They were cut because **38% of D1 and 18% of D4 anchor decisions
cited this project's own machinery**, against **0%** on D3 and D5 — they graded
*toolchain ownership*, not validation. Right call for portability; wrong outcome
for this goal. **SV-02 must not rebuild them under new names.**

**THE SCORE IS NOT IN THE GOAL PROCESS.** Across every skill, the entire surface
is **three skills and four files** — one cross-reference in
`git-epic-workflow/references/goals-and-evaluation.md`, `git-issue-workflow`'s
`goal-signal.md`, and `git-issue`'s `SKILL.md` and `regression-close.md`.
**No goal has ever been keyed to a dimension.** `spec-double-compiler`'s ~990
matches are its bundled copy of this repository's own record.

**THE LOOP IMPROVES THE INSTRUMENT, NEVER THE PROGRAM.** Every closure has
terminated in a card change and a score change. **No score has ever produced a
test, a diagram, a model action or an adapter. That path is 0 for 7 epics.**

---

## 4. And one debt carried forward

**The D3 caveat has no negative control.** It was applied to an artifact with
exactly the property it names, and the score went to 3. That demonstrates
plumbing, not discrimination. Both firings ran the same direction.

> **A null is the informative outcome and must be reported as loudly as
> `close-the-loop` reported the move.**

`SV-01` settles it, first, cheaply, with a design that already exists.

---

## 5. The constraints that bind every ticket

- **`serve | wc -c` is the surface metric: 6,281 bytes, 9 rungs. It must not
  grow.** Repository lines are net-additive *by construction* — the change rule
  keeps old anchors and `R-H4` seals the record — so they measure nothing.
- **An anchor is permanent. A prompt or a recorded note is free.** Prefer the
  cheapest carrier that does the job, and justify any new rung.
- **The card is never mandatory anywhere.** A project that declines to score runs
  epics exactly as it does today. **Design for absence first.**
- **No new gates.** Seven epics of static checking, zero bugs caught.
- **Skills are READ, never edited from here.** Anything that must change in
  `SKILL_MANAGER_HOME` is proposed as a diff and escalated. **Never run
  `skill-manager sync`.**
- **Use a harvested defect, not a fresh one.** `HARVEST-CL-03.md` carries **38
  classes** found by judges across seven epics, of which roughly **one** was ever
  filed. The measured bottleneck of this whole programme is that **nothing
  consumed a filed finding** — `SV-04` is the consumption step, and inventing a
  new defect dodges the thing being tested.

---

## 6. Doctrine that carries forward unchanged

- **`MF-020`**: never add an axis, a test or a rung fitted to a known answer.
  The clearest invitation this project ever produced was refused twice.
- **R1**: an instrument ships with a demonstrated *failing* input on a real
  subject.
- **`R-H1`/`R-H2`**: same example, unchanged instrument, same architecture tag.
  Never average across examples or versions.
- **`denominator_rule`**, including suite counts.
- **Seal predictions BEFORE measuring and say when**, in a commit with a
  timestamp.
- **File findings; fix nothing during a measurement.**
- **Ask every blind agent what it REJECTED.**

---

## 7. Operational rules this project has paid for

- **`wt new` branches from the LOCAL ref.** It has put tickets 4, 14 and 21
  commits behind. **Verify your branch point** — and verify it even when the
  owner hands you the SHA, which has been wrong once.
- **Do NOT report `git archive` figures as tree properties.**
- **Write scratch output to a TICKET-SPECIFIC path.** Two concurrent tickets
  corrupted a shared `baseline.txt` last epic.
- **Do NOT hand-roll a wait loop. Never kill a process by name alone**, and check
  whether a process is yours before touching it.

**Two reds are inherited deliberately**: `RM-06-DF-01`, and the pricer grep
tripped by narrative documents. Do not repair them silently.

---

## 8. The standing rule

**A low or unflattering result is the preferred outcome.** The predecessor's best
result was its own premise being falsified, and its evaluation corrected the
owner's headline figure by a factor of six in the flattering direction.

**An epic that closes with only good news about itself has not been measured.**
