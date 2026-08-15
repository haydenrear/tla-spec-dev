# `GOAL-four-results-still-stand` — baseline

**Tree: `436c78c55c60c3ee45901223176124df5e38b6ff`**, the epic base.

**Continues `GOAL-four-results-stand`** of `cut-the-apparatus-epic`, sealed at
`specs/.history/cut-the-apparatus-epic/closed-snapshot/snapshots/desired_program_model/ticket_plan.yaml`.
Same goal, re-based baseline, **new ID** — see `GOAL-judged-goals-compliant`'s
baseline §6 for why the ID could not be reused.

**Sealed evidence in this directory:** `audit-436c78c.txt`,
`serve-digest-436c78c.txt`.

---

## 1. The four results, standing at the base

| # | result | evidence |
|---|---|---|
| 1 | **Asking for an architecture changes the architecture** | D3 went **1 → 4** on the prompt alone, replicated across rounds. Confound killed directly: a *longer* prompt with no architectural vocabulary scored **1/1** (arm C). |
| 2 | **D3 separates architectures on more than one example** | `eval_toolchain`: `effectful [0,1]` vs `ports-and-adapters [2,4]`, **disjoint, both judge tiers on both sides**. |
| 3 | **D3's v5 caveat discriminates** | `SV-01`: D3 held **4, 4** at v4 and v5 on an artifact **lacking** the property, against `CL-03`'s **4, 4 → 3, 3** on one that has it. Prediction sealed at a timestamped commit before any judge ran. |
| 4 | **A score can produce a test and the re-score sees it** | `SV-04`: control **3, 3** vs treatment **4, 4**, same bytes plus one file, D2 flat at 2 across all four. **Verified by execution** last epic — `CA-06` re-ran it and got `14 passed`, matching the sealed figure exactly. |

## 2. Result 2 is damaged but standing, and the damage is priced

`CA-02`'s cut left `rm04_removal_pricer` with no effect surface, so `derive`
moves **17 of 21 decided → 16 of 21**. **Numerator fell; denominator held at
21.** **A replicate was lost, not the result**, and `CA-02` priced it.

## 3. Two of the four DISPROOFS did not stand, and both overstatements came from a charter

- *"The removal-pricing instrument could only ever return zero"* — **refuted in
  three places** (`CA-00-DF-05`). `RM-05-DF-01` forbids the quotation by name;
  `RM-02` §10.2 says *"the instrument **can fire**"*; and `RD-02` — whose own
  `0 of 9` is explicitly scoped as **not** a statement about every mutant —
  refused the very deletion the claim was used to justify.
- *"Zero unique kills"* — **overstated**, and scoped narrower than it was quoted.

**The defensible sentence, and the one to use:** *"a non-zero was the informative
outcome, the instrument would have printed one, and none appeared — the goal is
met and the instrument is not yet useful"* (`NEXT-EPIC.md` §5). **Do not restore
the stronger wording.**

## 4. What actually broke is a disproof's INSTRUMENT

`specs/results/scorecards/close-the-loop/GOAL-price-means-something/repriced_history.py`
loads two files `CA-02` deleted and dies with `FileNotFoundError`. **The sealed
transcripts read; the claim cannot be re-derived.**

**`CA-08` decided the general question and the decision stands: a sealed
transcript does NOT suffice.** A transcript proves what a run printed; only a
runnable instrument proves the claim can be checked **by someone who does not
trust the transcript**. **`R-H4` forbids repairing a stranded script, so the only
honest moves are DISCLOSE or DO-NOT-CUT.** `SS-07` takes one and says which.

**And note how disproof 1 escaped, because it was measurement and not caution.**
`CA-04` was told to delete `kill_test.py`, measured that `run_controls.py:165`
imports it at module scope, and retained 310 lines. **Review then found three
more consumers it had missed** — it verified the two it found and stopped
looking. **Do not stop looking.**

## 5. Instrument state at the base

**The card:**

```
serve | wc -c            6281
serve --digest-only      sha256:2d7d4a0506d9b259
card version             5
rubric file              sha256:b7fe75437bf68646
```

**`audit` reports 9 violations at this tree — and that is a defect in the
instrument, not in the record.** All nine are `filed_as = CL-03-DF-04 is not an
id in deferred_findings.yaml`, and `CL-03-DF-04` **is** filed. Cause:
`SS-00-DF-01`, filed at kickoff — the archived-ledger fallback orders candidates
by `(mtime, size, path)`, git does not preserve mtimes, **so on a fresh worktree
all 85 candidates share one mtime and the largest file wins**: a four-epic-old
mid-ticket snapshot with 88 ids.

**Consequence for every figure in this epic: `audit`'s violation count is a joint
property of the tree AND the checkout.** Quote both, or the figure does not
reproduce. `CA-10` measured **0** at a tree that audits **9** here.

**`SS-01` repairs it before `SS-08` runs**, per
`planning_rules.kickoff_defects_are_repaired_before_the_evaluation`, **and the
proof is two independent fresh worktrees of the same commit returning the same
count** — inspecting the sort key is not proof. Until then, this goal's `audit`
figure carries the caveat, and `SS-08` reports an unrepaired `SS-00-DF-01` as an
ALARM rather than repairing it.

**`scope` still runs** — 82 counted figures at this tree; see
`GOAL-counted-figures-reach-the-record`'s baseline for the attributed movement
from `CA-08`'s 102.

## 6. What this goal has that the others do not

**It is the only goal this programme has ever run that caught an epic guarding
something already false.** Keep the method. Do not re-litigate the results.
