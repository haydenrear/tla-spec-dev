# DISCLOSURE — this result's instrument does not run at the repository tip

**Written by `SS-07` (`stabilize-substrate`, issue #276) on 2026-08-16.
Nothing in this directory was edited to write it: `R-H4` says a sealed
measurement is annotated beside itself, never rewritten.** Read this before you
read `RESULT-CL-02.md`, `repriced-history-sweep.txt` or
`parent-10cf11a-same-commands.txt`.

**Every figure below names the tree it was measured on. `SS-01-DF-03`: a verdict
is a joint property of the artifact AND the tree it is computed in.**

---

## 1. What is disclosed

`repriced_history.py` in this directory **does not run at the repository tip.**
Re-confirmed by execution at tree `48f9c7e` (`epic/stabilize-substrate`, wave-1
tip) on 2026-08-16:

```
$ python3 specs/results/scorecards/close-the-loop/GOAL-price-means-something/repriced_history.py
FileNotFoundError: [Errno 2] No such file or directory:
  '<repo>/examples/validation/gap_mutants/price_removal.py'
```

Line 21 loads `examples/validation/gap_mutants/price_removal.py` and line 22
loads `examples/validation/removal_census/removals.toml`. **`CA-02` deleted
both**, at `37ab155`, and priced the deletion in its own price table. Filed as
`CA-02-DF-04` by the ticket that caused it, against itself.

**What survives and what does not, checked file by file at `48f9c7e`:**

| input | state at `48f9c7e` |
|---|---|
| `examples/validation/gap_mutants/price_removal.py` | **ABSENT** — the instrument |
| `examples/validation/removal_census/removals.toml` | **ABSENT** — the manifest |
| `.../subtract-to-measure/before-state/gap-mutants-before.json` | present |
| `.../portable-substrate/GOAL-dead-weight-gone/rm03-gap-mutants-before.json` | present |
| `.../reading-discipline/GOAL-apparatus-priced/rd02-gap-mutant-before.json` | present |
| `.../portable-substrate/GOAL-removal-can-be-priced/RM-01/residual-{before,after}-bf0fb29*.json` | present |

**The data survives; the instrument does not.** That asymmetry is the whole
disclosure: the sealed transcripts still *read*, and at the tip they cannot be
*re-computed*.

## 2. The decision this directory is now covered by

`CA-08` decided the general question, and `SS-07` did not reopen it:

> **A sealed transcript does NOT suffice.** A transcript proves what a run
> printed; only a runnable instrument proves the claim can be checked **by
> someone who does not trust the transcript**.

`R-H4` forbids repairing a stranded script — restoring `price_removal.py` would
undo `CA-02`'s assigned cut, and rewriting `repriced_history.py` to not need it
would edit a sealed measurement script and make this transcript no longer the
one that produced the published figure. **So the only honest moves are DISCLOSE
or DO-NOT-CUT.**

**`SS-07` takes DISCLOSE.** DO-NOT-CUT was not available to it: the cut landed
four commits before this epic branched, and taking it now would mean reverting
another ticket's priced, closed work under cover of a verification ticket.

## 3. And DISCLOSE is worth more than it was, because the re-derivation was RUN

**`CA-02-DF-04`'s `reproduction` field names a restore command. Nobody had ever
executed it. `SS-07` did, at `48f9c7e`, and it reproduces exactly.**

In a **throwaway detached checkout** — never this branch, never the record:

```bash
git worktree add --detach <cell> 48f9c7e
cd <cell>
git archive 37ab155 examples/validation/gap_mutants examples/validation/removal_census | tar -x -C .
python3 specs/results/scorecards/close-the-loop/GOAL-price-means-something/repriced_history.py
```

Result at `48f9c7e` + the two paths restored from `37ab155`:

```
TOTAL PRICED RESULTS ACROSS RE-PRICED HISTORY: 0
0 of 10 disagree with the measurement.
priced rows: []
this_instrument verdicts: ['NO-KILL-TO-LOSE', 'UNDECIDED']
RM-01-RF-1 ...  PRICED
RM-01-RF-CTRL ... CONTROL-EXCLUDED
```

**`diff` against `repriced-history-sweep.txt` in this directory: byte-identical,
zero lines of difference.**

**What that does and does not buy.**

- It **does** give a doubter a runnable route: three commands, no edit to any
  sealed file, no trust in the transcript required. That is the property
  `CA-08` said a transcript alone cannot provide, and it now exists.
- It **does not** make the result re-derivable *at the tip*, and `SS-07` does
  not claim it does. The route depends on `37ab155` remaining reachable in this
  repository's history. **If that history is ever rewritten or shallow-cloned,
  this result becomes unre-derivable with nothing going red to say so.**
- It **does not** license restoring the files. The cut stands; the price table
  stands; this page is the price being paid out loud.

## 4. The wording of the result itself — the two stronger sentences are WITHDRAWN

Two claims that were used to justify or summarise this work **did not survive
review and must not be restored:**

- ~~*"the removal-pricing instrument could only ever return zero"*~~ —
  **refuted in three places** (`CA-00-DF-05`). `RM-02` §10.2 says *"the
  instrument **can fire**"*; `RD-02`'s own `0 of 9` is explicitly scoped as
  **not** a statement about every mutant; and `CL-02` records that `RM-01-RF-1`
  is still `PRICED` and is still the only price this project has — which the
  re-run in §3 re-derives.
- ~~*"zero unique kills"*~~ — **overstated**, and quoted wider than the scope it
  was measured in.

**The defensible sentence, `NEXT-EPIC.md` §5, and the one to use:**

> *"A non-zero was the informative outcome, the instrument would have printed
> one, and none appeared. **The goal is met and the instrument is not yet
> useful.** Meeting the goal is not evidence that it will become useful."*

## 5. What should change in the substrate, and what did not

`CA-02-DF-04`'s `suggested_fix` names the mechanical check that would have
caught this: *"a cut must GREP THE SEALED RECORD for loaders of every file it
deletes."* **Filing that routed it; nothing computed it.** `SS-07` computed it
in the only direction a sealed record allows — from the loaders outward —
and the sweep is
`specs/results/scorecards/stabilize-substrate/SS-07/stranded_loaders.py`.

**`repriced_history.py` is not the only one.** The sweep and its triage are in
`specs/results/scorecards/stabilize-substrate/SS-07/RESULT.md` §5. `SS-07` files
the findings and repairs nothing.
