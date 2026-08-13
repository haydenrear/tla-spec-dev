# `RD-03-DF-08` — the descriptor as a precondition of a D2 score

**CA-03. Measured at `4302082`, the epic tip after CA-01 and CA-02 merged.**

**Verdict: the cut was already made, at card version 4, and CA-03 removes
nothing.** The enumeration below is the deliverable, and it is complete.

---

## 0. The finding, quoted before it is used

`specs/desired_program_model/deferred_findings.yaml`, `RD-03-DF-08`:

> THE COMPLEXITY DESCRIPTOR CANNOT SEE THE ONLY SIMPLIFICATION THIS ROUND
> MEASURED, AND EIGHT BLIND JUDGES SAID SO INDEPENDENTLY.
>
> On `Z` -> `M`, NINETEEN OF TWENTY-ONE measured axes are byte-identical […]
> On `N` -> `D`, a column moves the WRONG WAY: `branch_points` 26 -> 27 […]
> NO AXIS COUNTS STORED-VERSUS-DERIVED DUPLICATION, which is the only kind of
> simplification either revision made.

And its `blast_radius`, which is the sentence that decides this ticket:

> Every D2 judgement in this repository that leaned on the descriptor. **It does
> not invalidate any score — rule 7 forbids scoring the block** — but it is the
> reason a judge who followed the numbers would have reached the opposite
> verdict on two of three pairs.

And its `suggested_fix`, in full, because it asks for the opposite of a deletion:

> DO NOT add an axis in order to make this round's revisions score better — that
> is `MF-020` in its purest form […] The alternative, **which costs nothing, is
> to state the blind spot beside the instrument**: the descriptor measures SHAPE
> and does not measure whether two stored things must agree.

**`RD-03-DF-08` asks for a sentence to be added to an instrument. It does not
ask for a coupling to be removed, because it records that the coupling was
already forbidden.** The work order's framing — *"Cut the descriptor's role as a
precondition of a D2 score"* — is a reading of the finding, not the finding.

---

## 1. Where the coupling was, and when each piece went

| # | the coupling | where it was | status at `4302082` |
|---|---|---|---|
| 1 | **D2's preamble required the descriptor to be read first** | the card | **REMOVED at version 4.** `references/eval_scorecard.md:769`: *"D2's preamble stops requiring a measured descriptor to be read first."* |
| 2 | **D2's anchor 4 gated on `D4 ≥ 3`**, and `D4` was the dimension the descriptor fed | the card | **REMOVED at version 4.** Same row: *"D2's anchor 4 is deleted, so D2 is a 0–3 scale."* |
| 3 | the retired preamble text | `references/eval_scorecard.md:801-803` | **kept verbatim and UNREACHABLE.** `:775-778`: *"`serve` renders parsed structure only and the parser matches `### D<n> — <name>` headings, which these deliberately are not."* |
| 4 | the retired preamble, **served** | `examples/validation/scorecards/rubric_v3_frozen.md:119-121` | **LIVE, REACHABLE, AND KEPT.** The one true exception. Filed as `CA-03-DF-02` and deliberately not touched — see §3. |

**What replaced piece 1** is the live version-5 preamble, which is the negation
of a precondition (`references/eval_scorecard.md:160-163`, served line 32):

> Diff the two trees yourself and decide whether one fact is stored twice […]
> Where a measured complexity descriptor exists **you may read it, and on its own
> it decides nothing; where none exists that is not a gap in the evidence.**

---

## 2. What is live at the tip, measured rather than assumed

### Nothing gates. Nothing is required.

```
$ grep -c 'code_complexity\|analyze_complexity' examples/validation/scorecards/score_tools.py
0
```

- **`check()`** (`score_tools.py:840-1122`) never opens `mechanical.json`. A D2
  score of 0–3 validates with no figure of any kind present anywhere in the tree.
- **`prompts/`** puts no descriptor in front of a judge.
  `prompts/produced_code_reading.md` is addressed at `:3-4` to *"the agent that
  wrote the tree"*, and the string `D2` does not occur in the file.
  `prompts/hexagonal_implementation.md:56-57`: the descriptor *"is dispatched
  AFTER the tree exists, as a separate ask, and never as part of the block
  below."*
- **The repository already asserts this**, and has since `RD-05`:
  `tests/test_code_complexity.py:669::test_no_reader_of_this_instrument_gates_on_its_output`
  scans repository-wide, `specs/**` included, and asserts `sorted(refusals) == []`.

### What DECORATES, and why none of it is cuttable

| where | what | why it stays |
|---|---|---|
| `score_tools.py:2136-2140` | `_skeleton_md`'s pointer: *"`mechanical.json` beside this file holds kill counts, complexity figures, case counts, determinism and runtime."* | **SERVED card rule 7 mandates the block**, and the *filename* is the one thing the card does not carry — which is exactly why `SM-06` kept the pointer after deleting the restatement around it. Four of the five things it names have nothing to do with the descriptor, so `RD-03-DF-08` does not reach it. |
| `score_tools.py:2213` | `"complexity_of_produced_code": {}` in `_mechanical_json` | Same rule 7. The block's own note reads *"Measured figures. NEVER SCORED."* |
| `references/eval_scorecard.md:238-240` | rule 7 itself, **served** (line 13 of `serve`) | The card. `serve \| wc -c` must stay `6281`; this ticket may not touch it. |
| `architecture_tags.py:81,150-163` | `measure()`, the only shipped executable reader | **On the D3 axis, not D2** — `DRIFT_DIM = "D3"` at `:110-112` — and it computes standing result 2. |

**A thing the card says is "recorded, never scored" is not a precondition of a
score.** That is the whole answer.

---

## 3. The one exception, and why it is not cut

`serve --rubric examples/validation/scorecards/rubric_v3_frozen.md
--card-version 3` renders the retired preamble verbatim into the bytes a
version-3 judge is served. **That is a live descriptor-as-precondition and it is
kept**: the frozen rubric exists so the card's own change rule — re-score a prior
example under both versions — is followable, and `R-H4` (do-not-cut list) seals
the record it reproduces. Deleting the sentence makes the version-3 bar
unreproducible.

Filed as `CA-03-DF-02`, disposition `wontfix`, so the next sweep does not count
it as live coupling and so §2's *"nothing remains"* is exact rather than
approximately true.

---

## 4. What CA-03 rejected

- **Cutting `analyze_complexity.py` or `code_complexity.py`.** Forbidden by
  `RM-02`, by the charter §5 and by the ticket's own acceptance. Not attempted.
- **Cutting `_mechanical_json` or the skeleton's mechanical-block pointer.**
  Rejected: served card rule 7 mandates the block, the acceptance freezes the
  card at 6,281 bytes, and `RD-03-DF-08` says nothing about kill counts, case
  counts, determinism or runtime. **A deletion resting on this finding for those
  four would be `CA-02`'s error repeated** — citing a finding as authority for a
  removal it does not license.
- **Taking `RD-03-DF-08`'s own suggested fix** (state the blind spot beside the
  instrument). It is an ADDITION, to `scripts/code_complexity.py`, outside CA-03's
  `conflict_keys`. Deferred rather than done.
- **Adding an axis for stored-versus-derived duplication.** `MF-020` in its
  purest form, and `RD-03` already refused it by name.
- **Finding something else to delete so the ticket has a number.** The line
  count for `RD-03-DF-08` is **zero**, and clause (b) of `GOAL-apparatus-cut`
  says a cut with no finding behind it fails the goal even if the lines fell.

Filed as `CA-03-DF-01`, disposition `settled`.
