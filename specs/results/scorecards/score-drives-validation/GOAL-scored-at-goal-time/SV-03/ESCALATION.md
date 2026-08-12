# SV-03 — four skill diffs, PROPOSED and ESCALATED, not applied

**Nothing in this directory has been applied to `SKILL_MANAGER_HOME`, and
`skill-manager sync` was not run.** Skills are READ from this repository and
never edited from it; a change that must land in an installed unit is proposed
as a diff and escalated to the owner. The three installed files below are
byte-identical to what they were before this ticket started, and
`analysis/no_card_project_unaffected.py` re-hashes all three at the end of
every run to prove it.

| unit | file | sha256 (first 16) of the base these diffs apply to |
|---|---|---|
| `git-epic-workflow` | `references/goals-and-evaluation.md` | `c63462221bbb3118` |
| `git-issue-workflow` | `references/goal-signal.md` | `488ffa0f1350e1a5` |
| `git-issue` | `references/regression-close.md` | `235a38ebbdfa63ad` |

The installed copies are **ahead of** the checked-out source repos
(`IdeaProjects/git-epic-skill`, `git-issue-skill`, `git-issue-workflow-skill`)
— all three differ. The diffs are cut against the **installed** bytes, which is
what the ticket agents actually read. Applying them to a source repo will need
that repo reconciled first; that is the owner's call and part of why this is
escalated rather than applied.

**Apply, if the owner decides to** — from each unit root:

```
git apply proposed-skill-diffs/01-git-epic-workflow-goals-and-evaluation-third-branch.patch
git apply proposed-skill-diffs/02-git-epic-workflow-goals-and-evaluation-evidence-is-a-card.patch
git apply proposed-skill-diffs/03-git-issue-workflow-goal-signal-subtraction.patch
git apply proposed-skill-diffs/04-git-issue-regression-close-loop-outlet.patch
```

All four are verified to apply cleanly to the pristine installed files,
independently and in either order, by `git apply --check` and then by a real
apply into a temp copy whose result is byte-compared against the intended text.
**01 and 02 are in the same file and are deliberately separate patches**,
because SV-06 says 01 is the change to make if the budget is one change.

---

## What the four diffs are, and what each one buys

### 01 — `goals-and-evaluation.md` §Baselines: the third branch

The section has exactly two branches, *harness exists* and *harness does not*.
**A judged instrument that exists but has never been run on this subject is in
neither**, and the file's judged-baseline paragraph only says how to cite a
*prior* run. An epic in that position has no branch to follow.

```diff
 - **Harness is judged and this subject has never been scored under it** — the
 +  instrument existing is not a baseline. Run it at epic kickoff on the epic
 +  branch, before any ticket lands, exactly as for a command harness; seal that
 +  run and record its card as the baseline. A judged instrument that has been
 +  run on other subjects, or in other epics, has measured something else. If a
 +  kickoff round is not affordable, `unmeasured` with the reason is the honest
 +  answer and the goal stays legal — a goal that cannot be scored is not a goal
 +  that fails.
```

*(The patch file is authoritative; this is a reading copy.)*

**Buys:** the whole of `GOAL-scored-at-goal-time`'s target. It is the one change
that moves a judged goal from *described* to *measurable*, and everything else
here is downstream of it or is a subtraction.

**Deviations from SV-06's proposed wording, both deliberate:**

1. **Added the fail-open clause** — *"If a kickoff round is not affordable,
   `unmeasured` with the reason is the honest answer and the goal stays legal —
   a goal that cannot be scored is not a goal that fails."* SV-06 §9 lists
   affordability as the thing it could not settle: *"a project with one engineer
   may find the two-ended design costs two rounds it will not run."* A branch
   that says *run the instrument at kickoff* and stops is read as an
   obligation. The epic's rule is that **a goal that cannot be scored is not a
   goal that fails**, and this is the sentence that puts it in the artifact
   rather than in a ticket report. It also costs nothing: `unmeasured` is
   already this file's sanctioned answer two paragraphs down.
2. **Dropped SV-06's closing sentence** *("a baseline written as prose about
   prior rounds cannot be re-read by the evaluation ticket, and cannot be
   re-derived later")* — diff 02 now carries that reason where it belongs, and
   saying it twice in one section is the copy-with-nothing-behind-it failure all
   three skills already forbid.

### 02 — same file, same section: the evidence is a card, not a folder

```diff
+**For a judged goal, `baseline.evidence` is the card, not the folder it sits
+in.** Point it at the sealed card that produced the number, or — where the
+number is a figure over several cards — at the exact list of them. A directory
+is not a card and neither is a results summary: the evaluation ticket has to
+re-open the same cards, and it cannot pick them out of a folder.
```

**Buys:** *"the evaluation compares against the sealed number"* stops being an
aspiration. This is the change with the most measurement behind it.

**Evidence, re-derived at `5620c9a` by `analysis/baseline_is_a_card.py`:** of
**27** distinct epic goals across **109** plans on disk, **18 name a judged
instrument** and **0 of those 18 have a baseline the evaluation ticket can
open** — 8 cite a **directory**, 8 cite a **document**, 1 cites a path that
**does not resolve at all**, and 1 is **pure prose**. There are **87** sealed
`scorecard.json` files and not one is cited by any goal.

**Deviation from SV-06's proposed wording, and it is a correction:** SV-06 wrote
*"the path to the **single** sealed card that produced the number"*. **Two of
this repository's judged goals cannot comply with that sentence at all**,
because their baseline is a figure over a population of cards and no single card
produced it:

- `GOAL-D2-can-move` — *"D2 = 2 on 27 of 27 cards ever written about the A/B
  example"*;
- `GOAL-validation-is-scorable` — *"D1 read 3 on 55 of 59 cards"*.

`GOAL-D2-can-move` is the goal SV-06 itself holds up as the best dimension-keyed
goal this project has ever written. A rule its own exemplar is structurally
unable to satisfy will be ignored or will be complied with falsely, so the
requirement is **enumerability**, not singularity: name the cards, however many
there are, so the evaluation can re-open the same set. The worked example in
`example_goal.yaml` cites **two** cards for exactly this reason.

### 03 — `goal-signal.md` §"During validation": one paragraph, a SUBTRACTION

Verbatim from SV-06 §7.3. It forecloses the obvious wrong build — scoring every
ticket — and it is the implementer-side mirror of a sentence
`git-issue/SKILL.md` already carries. **Nothing is added to the ticket loop by
it; it removes a thing an implementer would otherwise try.**

### 04 — `regression-close.md` §1: one sentence, the loop's outlet

Verbatim from SV-06 §7.4. §5 of that file already routes a judged instrument
correctly; §1 is the consumption seam and **does not know findings exist**. This
is the sentence `SV-04` will exercise. It adds no checklist item — *"Named test
graphs pass"* is already there.

### 05 — `git-issue/SKILL.md`: **NO CHANGE**, confirmed

Its template already carries `Metric / harness` and `Baseline → target`, epic
mode already copies from the plan, and it already warns that a judged instrument
is rarely the right local signal. A third statement of a rule stated twice is
worse than nothing. Confirmed by reading, not inherited.

---

## The cost, stated in the units this epic measures in

| | |
|---|---|
| bytes added to `serve` | **0** — `serve \| wc -c` is **6,281** at **9 rungs** before and after |
| files this repository ships that are touched | **0** |
| new fields in the plan schema | **0** |
| new gates, checks or validator rules | **0** |
| words added across all four diffs | **331** |
| words a project with no card must read and obey | **0** |

The last row is structural, not a promise: every added block **opens with a
conditional** — *"Harness is judged and…"*, *"For a judged goal…"*, *"Where a
goal's harness is a judged instrument…"*, *"Where the deciding instrument
records notes…"*. A project with no rubric never enters one.
`analysis/no_card_project_unaffected.py` checks each block for its guard and
`tests/test_goal_baseline_is_a_card.py` shows the check **failing** on an
unguarded block, so it cannot pass vacuously.

---

## What was rejected

- **A `dimension:` field, a `scored_by:` block, and a `score_signal:` field.**
  SV-06 built the first two, validated them at exit 0 with zero Python, and
  rejected them; nothing here re-opens that. Re-checked rather than inherited:
  every field is already sayable in `harness`, `metric` and `baseline.evidence`,
  and `dimension:` exports one project's rubric index into a schema three skills
  share. **Cheap to add is not a reason to add.** The worked example uses only
  keys that exist today, and a test asserts it.
- **A checker that a judged goal has a card baseline.** The temptation is
  strong because the classifier already exists in this directory and returning
  1 is one line. Refused: `no_new_gates_rule`, seven epics of static checking
  with zero bugs caught, and — decisively — the thing it would gate is *the
  epic owner's prose about their own baseline*. `analysis/baseline_is_a_card.py`
  has **no failing exit path at all**, is imported by nothing in `scripts/`,
  and a test asserts both.
- **A test asserting that plans comply.** Same reason, one layer down. The
  suite reports the count and pins the demonstration; it does not fail until
  someone edits a plan.
- **A card version bump, and any change to `references/eval_scorecard.md`.** The
  blind adopter's blocker 2 is that a bump makes `[[movement]]` mandatory and
  undocumented. Nothing here needs a bump: the goal process learns to name a
  card, the card learns nothing about the goal process.
- **A `--goal` flag on `score_tools.py`, or any `tla-spec-dev` path that reads
  a plan.** It inverts the dependency and would make the card a participant in
  the goal process rather than an instrument it names.
- **A new `references/` page in this repository.** `references/goal_score_wiring.md`
  is the design and this is the proposal; a third page restating both is the
  surface SV-06 spent its §8 refusing.
- **Editing `specs/desired_program_model/ticket_plan.yaml` to give this epic's
  own goals card baselines.** Those baselines are sealed at `eab2883`.
  Retro-fitting them would be editing a measurement to match a result, and it
  would destroy the R1 failing input this ticket depends on.

---

## The R1 failing input, on a real epic plan

`GOAL-loop-reaches-the-program`, in this epic's own live plan, cites
`specs/results/scorecards/close-the-loop/`. **That directory contains zero
`scorecard.json` files** — the CL-03 cards are in two sibling directories. So
the evaluation ticket is not merely handed a folder to pick a card out of;
there is no card in it to pick. Sealed at `eab2883`, never edited, and pinned by
`tests/test_goal_baseline_is_a_card.py::test_a_real_epic_plans_judged_baseline_cannot_be_re_opened`.

A second, sharper failing input applies to **the proposal itself**: SV-06's
verbatim wording for diff 02 is unsatisfiable by `GOAL-D2-can-move`, which is
the goal SV-06 cites as the best of its kind here. That is what the deviation
above fixes, and it was found by running the rule against the record rather
than by reading it.
