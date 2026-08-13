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
| `price_removal.py` | 838 | `RM-05-DF-01`, `CL-02` — for every fault whose killing nodes all lie in a file the removal deletes, `ENTAILED-SURVIVES` follows from `git show` alone. The instrument had one reachable answer. |
| `altered_score_probe.py` | 177 | `RM-02` — a fixture probe over `ab_quota_ledger`, with no version an adopter receives. |
| `residual_faults.toml` | 193 | `RM-02` — the catalogue is hand-authored faults in `ab_quota_ledger`; the probe has nothing to read without it. |

`RM-03` had already retired this directory's other half — `run_gap_mutants.py`,
`gap_mutants.toml`, `tests/test_gap_mutants.py` — on the same adoption grounds,
and recorded then that `price_removal.py price` reads a measured after-table
**that nothing in this repository produces any more**. `CA-02` finishes that
removal rather than leaving the sound-but-unanswerable half standing.

## What the tree can no longer do

- It cannot compute `ENTAILED-SURVIVES` / `FREE` / `NO-KILL-TO-LOSE` for a
  removal. **`CL-02` re-priced the whole sealed history over kill sets and got
  `priced rows: []`, 0 of 10**, so what is lost is a verdict that was never
  once informative — not a measurement anyone will miss.
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
