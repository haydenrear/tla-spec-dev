# `gap_mutants/` — retired by `CA-02`

**Nothing executable lives here any more.** This directory is kept, and kept
non-empty, for one reason that is not sentiment: it is the declared `scope` of a
**sealed scorecard subject**.

```toml
[subject.rm04_removal_pricer]
example = "eval_toolchain"
scope = ["examples/validation/gap_mutants"]
declared_effect_boundary = "effectful"
labels = [["portable-substrate-rm04-JJ", "JJ"]]
```

A sealed subject whose scope path stops resolving is a sealed card nobody can
re-read against the tree it was scored on. `R-H4` seals the record; this file is
what keeps that seal legible after the code under it was cut.

---

## What was here, and the finding that removed each file

| file | lines | removed because |
|---|---|---|
| `price_removal.py` | 838 | **`RM-02`** — a sound instrument with **no measured after-table in this repository to run against**, over a fixture no adopter receives. |
| `altered_score_probe.py` | 177 | `RM-02` — a fixture probe over `ab_quota_ledger`, with no version an adopter receives. |
| `residual_faults.toml` | 193 | `RM-02` — the catalogue is hand-authored faults in `ab_quota_ledger`; the probe has nothing to read without it. |

> **CORRECTED after independent review of PR #264.** The first version of this
> row said `price_removal.py` was removed because *"the instrument had one
> reachable answer"*, citing `RM-05-DF-01` and `CL-02`. **The sealed record
> refutes that.** `NEXT-EPIC.md` §5: *"a non-zero was the informative outcome,
> **the instrument would have printed one**, and none appeared… the instrument
> is **not yet useful**."* `RM-02` §10.2: *"**the instrument can fire**, history
> remains free."* And `CL-02`'s headline keeps the exception: ***"`RM-01-RF-1` is
> still `PRICED` and is still the only price this project has."*** `RM-05-DF-01`
> additionally forbids the quotation in its own words — *"STATED SO THIS FINDING
> CANNOT BE QUOTED AS 'THE EPIC PRICED NOTHING'"* — and describes the file
> **before** `CL-02` repaired it. Full correction table:
> `specs/results/scorecards/cut-the-apparatus/CA-02/PRICE-TABLE.md` §0. The
> propagation is filed as **`CA-00-DF-05`** (major, open), which names the origin
> as the epic owner's and records that `CA-02` was the ticket told to check the
> dependency explicitly and propagated it instead.

`RM-03` had already retired this directory's other half — `run_gap_mutants.py`,
`gap_mutants.toml`, `tests/test_gap_mutants.py` — on the same adoption grounds,
and recorded then that `price_removal.py price` reads a measured after-table
**that nothing in this repository produces any more**. `CA-02` finishes that
removal on `RM-02`'s adoption grounds, not on a pricing count.

## What the tree can no longer do

- It cannot compute `ENTAILED-SURVIVES` / `FREE` / `NO-KILL-TO-LOSE` for a
  removal. `CL-02`'s re-pricing sweep returned **`priced rows: []`** over the
  published before-tables — **an instrument that was not yet useful, not one
  that could never fire**, and one price (`RM-01-RF-1`) stands outside that
  sweep.
- **`specs/.../GOAL-price-means-something/repriced_history.py` NO LONGER RUNS.**
  It loads this directory's `price_removal.py` at line 21 and now dies with
  `FileNotFoundError`. The sealed transcripts still read, so the RESULT survives;
  **what is lost is the ability to re-derive it.** `CA-02-DF-04`.
- It cannot re-run `SM-04-GM-T1` from an independent implementation. The
  finding itself stays readable in the sealed record.

## Recovering it

Every deleted file is in git history and the sealed before-tree is materialised
in the repository, so neither depends on this directory:

```bash
git show 37ab155:examples/validation/gap_mutants/price_removal.py
git show 37ab155:examples/validation/gap_mutants/altered_score_probe.py
git show 37ab155:examples/validation/gap_mutants/residual_faults.toml
```

The `rm04_removal_pricer` before/after that `portable-substrate-rm04-JJ` scored
D2 on is **not** recovered from here — its before tree is checked in at
`specs/results/scorecards/portable-substrate/GOAL-dimensions-replicate/RM-04/blind/artifact_JJ_before`
and is untouched by this cut.

Registry rows for all three files moved to `[[retired]]` in
`examples/validation/instruments/instruments.toml` rather than being deleted,
because a capability that leaves a registry without a row is exactly what
`FI-04-DF-04` is about.
