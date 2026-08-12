# SV-01 — predictions, sealed BEFORE any judge is dispatched

**Sealed at `2026-08-12T16:39Z`.** At the moment of the commit that adds this
file: the four cards exist as **unfilled skeletons**, no judge agent has been
launched, and **the operator has not yet run the mutation probe in P6.** The
only thing read about this artifact beforehand is its source, and the only
numbers known about it are the ten sealed cards named in §3 below.

`GOAL-caveat-discriminates`. Harnessed here, decided by `SV-05`.

---

## 1. What is being measured, in one sentence

**`close-the-loop` moved `D3` from `4, 4` to `3, 3` by adding a caveat that
tells a judge to take 3 when the only observer of the effect the port exists for
is the adapter that wrote it — and it applied that caveat to an artifact WITH
EXACTLY THAT PROPERTY.** That is the minimum possible evidence that a caveat is
wired up. It demonstrates plumbing. **It does not measure discrimination.**

This round scores **one artifact that plainly LACKS the property** under card
version 4 and card version 5, two passes a side, same judge model, same
architecture tag, same packet, same dispatch text.

- **If `D3` falls here too**, the caveat is **general downward pressure** and
  `close-the-loop`'s headline is a **recalibration**, not a detection.
- **If it holds**, the caveat **discriminates** and the headline is earned.

**A null is the informative outcome and will be reported as loudly as CL-03
reported the move.**

---

## 2. The artifact, and why it qualifies — declared, checkable by reading

Subject `sv01_negative_control`, declared in
`examples/validation/scorecards/subjects.toml` before the scaffold ran. Scope:

```
specs/results/scorecards/score-drives-validation/GOAL-caveat-discriminates/SV-01/blind/artifact_under_score
```

It is a **byte-identical copy** of `arm_b`'s `quota_ledger/`,
`tests/test_ledger.py` and `NOTES.md`. `EVIDENCE.md` is not copied: it is the
producing round's instrument output, its first line names the published label,
and it is not part of the artifact.

**The caveat's condition is FALSE here, and it is false in a way a reader can
check without running anything:**

| # | the observer | where | is it the adapter that wrote it? |
|---|---|---|---|
| 1 | `FileJournal.records()` | `quota_ledger/file_journal.py:33-35` | **yes** — this is the CL-03 case |
| 2 | `path.read_text()`, asserting the exact bytes on disk | `tests/test_ledger.py:244, 247` | **NO** |
| 3 | a **second** `FileJournal` instance reading the first one's path | `tests/test_ledger.py:251-254` | a different instance |

Observer 2 is the one that matters. A `FileJournal` gutted to an in-memory list
— the exact mutation CL-03's operator and both its v5 judges ran — **cannot**
pass `assert path.read_text() == "COMMIT acme 1 1\nCLOSE acme 1\n"`.

**The architecture tag is the same as CL-03's subject**, derived and not
asserted: `toolchain_fixture` derives `ports-and-adapters`,
`sv01_negative_control` derives `ports-and-adapters` (`iface=1`, `eff_mods=1/4`,
`state_coloc=0.125` — identical to `arm_b`, which is what a byte-identical copy
should give).

---

## 3. What the record already says about these bytes — the prior, stated up front

The same tree has been scored **ten times** and read **`D3 = 4` on every one**,
across card versions **1, 2, 3 and 4** and across **two** judge models
(`claude-opus-5[1m]`, `claude-sonnet-4-5`). `D2` read **2** on all ten.

**It has never been scored under version 5.**

Those ten cards are **not** this round's evidence and are not averaged with it:
they are a different round, a different packet and a different dispatch, and
`R-H1`/`R-H2` forbid the splice. They are stated here so that this file cannot
later be read as if the outcome were unexpected in either direction, and so the
prediction below is on the record as a prediction rather than as a memory.

---

## 4. THE PREDICTIONS

| | prediction | how it is decided |
|---|---|---|
| **P1** | **both version 4 judges award `D3 = 4`** | the two v4 cards |
| **P2** | **at least one version 5 judge quotes the caveat AND states its condition is not met here, citing an observer that is not the adapter** | the two v5 cards' `D3.rationale` |
| **P3** | **THE HEADLINE — `D3` holds at `4` on BOTH version 5 passes** | the two v5 cards |
| **P4** | **`D2` is unmoved across the version boundary** (the two rubrics differ on D3's caveat and on scoring rule 9 and on nothing else) | all four cards |
| **P5** | **`serve \| wc -c` is 6,281 bytes and 9 rungs at the end of this ticket, unchanged** | measured at sealing |
| **P6** | **gutting `FileJournal` to an in-memory list FAILS at least one case in `tests/test_ledger.py`** — the artifact's lack of the property is mechanical, not rhetorical | the operator's probe, run after this file is committed |
| **P7** | **the suite reports the same two inherited failures at this ticket's tree as at `a527305`** (`RM-06-DF-01`, and the pricer grep tripped by narrative documents) | a full run at both trees |

**P3 is the prediction this round exists to be wrong about.** CL-03 wrote the
same sentence about its own `P3` and was wrong. If `D3` comes back `3, 3` here,
**the caveat does not discriminate**, `close-the-loop`'s headline is a
recalibration, and this file's author predicted the opposite in advance.

---

## 5. How each outcome will be read — fixed NOW, so it cannot be fitted later

| v5 result | verdict | what it does to the record |
|---|---|---|
| `4, 4` | **DISCRIMINATES** | CL-03's headline is earned. The caveat's condition was checked and found false, and the score did not move. |
| `3, 3` | **DOWNWARD PRESSURE — the null** | CL-03's headline becomes a **recalibration**. Every claim that reads the `4,4 → 3,3` move as a *detection* inherits the correction, and each one is named. |
| `4, 3` or `3, 4` | **CONTESTED, spread 1 — NOT decisive either way** | Recorded as contested. **A split is not a discrimination**; the round reports that the caveat's effect on an artifact lacking the property is within judge-to-judge variance, and says the cell is still open. No third pass is run to break the tie — a third pass produces a third number, and CL-03 declined the same move for the same reason. |
| any `D3 < 3` under v5 | **DOWNWARD PRESSURE, worse than the null** | the caveat would be moving a dimension below the floor its own text names. |

**Alarm condition, declared in advance.** If `D2` also moves across the version
boundary (P4 false), then something other than the D3 caveat is moving scores in
this round — packet, dispatch or judge variance — and **P3 cannot be read as a
statement about the caveat at all**, in either direction. That would make the
round INCONCLUSIVE, and it would be reported as inconclusive rather than as a
verdict.

---

## 6. What this round will NOT claim

- **It will not average across the version boundary**, and it will not average
  with the ten prior cards of §3.
- **It will not claim anything about `ab_quota_ledger` as an example** from one
  artifact, nor about any artifact other than this scope. `R3`: a claim carries
  its scope. This is one artifact, one judge model, two passes a side.
- **It will not claim the caveat is correct or incorrect.** It measures one
  thing: whether the caveat's effect is conditional on the property it names.
- **It will not repair anything** — not the two inherited reds, not the artifact,
  not the caveat. Findings are filed.
