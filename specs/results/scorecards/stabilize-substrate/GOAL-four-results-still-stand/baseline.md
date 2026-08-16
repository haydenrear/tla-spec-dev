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

**`audit` reported 9 violations at the epic base — and that was a defect in the
instrument, not in the record.** All nine were `filed_as = CL-03-DF-04 is not an
id in deferred_findings.yaml`, and `CL-03-DF-04` **is** filed. `SS-00-DF-01`.

> **CORRECTED AND SUPERSEDED 2026-08-16. This block previously stated the cause
> as "all 85 candidates share one mtime and the largest file wins". THAT
> MECHANISM IS WITHDRAWN — it was an artifact of the owner's own diagnostic,
> which printed mtimes with `:.0f` and collapsed four distinct seconds into one.**
> There are **85 distinct mtimes**; size is never consulted because no tie
> exists; and **the largest file is the *correct* one**, so had the filed account
> been right the instrument would have been right. The real cause is worse:
> **mtimes reflect git checkout order, which carries no historical information
> at all.** `SS-01-DF-02`. The withdrawn wording is quoted here rather than
> deleted, per `R-H4`'s spirit.
>
> **Also withdrawn: "`CA-10` measured 0 at a tree that audits 9 here."** Both
> fresh clones give **9** at the base and **0** at the tip; the instability is
> **fresh-vs-touched**, not checkout-vs-checkout.
>
> **REPAIRED AT `50046b2`.** `audit` is **0** on a fresh checkout, proven on four
> independent fresh clones rather than by inspecting the sort key. **The current
> figure for this goal is 0, not 9.**

**The consequence that survives, and it is the durable one:** `audit`'s violation
count is a joint property of **the tree AND the checkout** — quote both, or the
figure does not reproduce.

**`scope` runs and reads 103** at `50046b2` (81 REFUTED, 2 HOLDS, 20 UNREACHABLE)
— **not the 82 this baseline originally recorded.** `SS-01` added the relocated
ledger to `DEFAULT_SWEEP`; the 82 is superseded and the cause is a ticket, not a
claim being resolved. And `SS-01-DF-03`: **a `scope` verdict is a joint property
of the file and the tree it is swept in**, and the output records nothing about
which root it used. See `GOAL-counted-figures-reach-the-record`'s baseline for
the full attribution, including the owner's corrected cross-tab.

## 6. What this goal has that the others do not

**It is the only goal this programme has ever run that caught an epic guarding
something already false.** Keep the method. Do not re-litigate the results.
