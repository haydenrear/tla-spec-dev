# RM-05 — predictions, sealed before any blind agent was dispatched

**Sealed at tree `58411dc` + this file, before the first `Agent` call of this
ticket.** Nothing below is edited after a channel reports. §A records what I had
already measured myself at sealing time, so that no measurement of mine is
smuggled in later as a prediction.

---

## A. WHAT I HAD ALREADY MEASURED WHEN THIS WAS SEALED

These are **not predictions**. They are stated here so a reader can tell my
priors from my guesses.

1. `serve` output: **8,396 bytes / 84 lines / 25 anchor rungs** at `19c5c7b`,
   **6,409 / 68 / 9** at `58411dc`. Byte-identical at every v3 commit checked
   (`2098d55`, `f85f07a`, `4ec3028`, `19c5c7b`).
2. `references/eval_scorecard.md` as a **file**: 9,791 bytes at its first commit
   (`40bde2c`, version 1) rising monotonically to **44,266** at `58411dc`
   (version 4). `^- **n** —` rung lines in the file: **25 at every commit
   checked, including version 4.**
3. `19c5c7b:scripts` and `58411dc:scripts` are the same git tree
   (`e9d5544a…`). So are `SKILL.md`, `prompts/`, `templates/`,
   `spec_double_compiler/` and `test_graph/`. **`references/` is the only
   shipped surface this epic moved.**
4. Instrument registry: **65 rows at `19c5c7b`, 65 rows at `58411dc`.**
   Two out (`SM-01's gap-mutant runner`, `a cli detector's argv against its
   entry point`), two in (`RM-01's removal pricer`, `SM-04-GM-T1, driven
   through the shipped CLI`).
5. Findings ledger: **157 rows, 23 of them this epic.** Findings whose `surface`
   names a path under `scripts/`: PA 4, SM 3, FI 0, RD 1 — **8 of 134** across
   the four prior epics, which reproduces the owner's figure exactly.
6. No ticket in this epic recorded a token count anywhere in the tree, and no
   per-worktree agent transcript survives.

## B. PREDICTIONS ABOUT THE BLIND CHANNELS

Three channels are dispatched blind: **A** re-derives the epic's pricing
headline from the sealed artifacts; **B** attacks portability and whether the
self-improvement loop transfers; **C** builds the removal/addition typology and
tests the owner's candidate pattern against the record.

| | prediction |
|---|---|
| **P1** | Channel A confirms `RM03-GM-RUNNER` reads `ENTAILED-SURVIVES` at the head, **and** files at least one material qualification to "the first PRICED removal" that RM-03's own page does not already state. |
| **P2** | Channel B concludes the **loop does not transfer as-is**, and names the card's own change rule (`keep the old anchors`, `R-H4`) as a reason an adopter's card grows monotonically from its first iteration. |
| **P3** | Channel C **falsifies the owner's candidate pattern on at least one row** — at least one thing this epic removed *did* gate something, or at least one surviving field records a measurement without gating on it. |
| **P4** | **No blind channel finds a defect in `scripts/`.** No commit in this epic touches it. If a channel does find one, it is the best finding of the round. |
| **P5** | At least one channel reports that the epic's re-scores and blind rounds are **not independent of the epic's own operators**, i.e. names a leak, a confound or a self-reference that is not already on the record. |
| **P6** | The full suite at `58411dc` in this real checkout comes back **1 failed, 1470 passed**, the failure being `tests/test_architecture_tags.py::test_the_same_tag_control_holds`. |
| **P7** | I will be tempted to publish a per-token ratio on a basis I invent for the occasion, and the honest report is that **this epic recorded no token basis at all**, so `RD-03-DF-13`'s repair lasted exactly one round. |

## C. PROVISIONAL GOAL CALLS, MADE BEFORE ANY CHANNEL REPORTED

Sealed so that a channel's report cannot quietly move them without that move
being visible.

| goal | provisional call at sealing |
|---|---|
| `GOAL-removal-can-be-priced` | **MET, narrowly** — one `PRICED` on one removal, and the fault priced is inside the deleted mechanism. |
| `GOAL-dead-weight-gone` | **PARTIALLY MET** — one of the three levers was never in the tree, one was rejected on specification grounds, one was removed. |
| `GOAL-dimensions-replicate` | **SPLIT** — D3 replicated, D2 did not, D4/D5 dropped. |
| `GOAL-portable` | **MET as a decision** — and the decision is that adoption requires less, not more. |

**If every one of P1–P7 passes, that is an ALARM and this document says so in
advance.**
