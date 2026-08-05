# PREDICTIONS-PA, scored at PA-06

**`examples/validation/PREDICTIONS-PA.md` is SEALED and is NOT AMENDED.** Nothing
in it was edited, reworded or reinterpreted after a result was known. This file
records the verdicts and nothing else.

Vocabulary, from the sealed file: `PASS`, `FAIL`, `SUPERSEDED` (the instrument
turned out not to measure what the prediction assumed — must cite which
instrument and why), `UNMEASURED` (the instrument did not run — must say why).
**`UNMEASURED` is not a pass.**

## The table

| ID | Prediction | Expected | Observed | Verdict |
|---|---|---|---|---|
| **P01** | an adapter-internal fault dies on a generated instrument | UP from 0 | `PA-M12` **KILLED** on `corpus-port-swap:fake`, SURVIVED on the other three corpus columns and on `suite-real` | **PASS** |
| **P02** | arms' per-mutant verdicts diverge ≥ 1 comparable cell | DOWN from 49 of 49 | the 49 → 56 → **64** lineage did **not** move: 64 of 64 identical, every pairing | **FAIL** |
| **P03** | the complexity instrument separates the arms | figures differ | differ on 11 figures across three arms | **PASS** |
| **P04** | `M07` and `PA-M14` die everywhere | 100% killed | `M07` SURVIVED on 3 columns × 3 arms; `PA-M14` SURVIVED on 4 columns | **FAIL** |
| **P05** | all three arms pass the shared suite, D4 ≥ 2 | all ≥ 2 | suite **28 passed** on all three; D4 = 4/4, 4/4, 3/3 | **PASS** |
| **P06** | arm B reproduces D3 ≥ 3 from both judges | reproduces; arm A 1–2 | **arm B D3 = 4 / 4**; arm A 2 / 2 | **PASS** |
| **P07** | the repaired control HOLDS its property on every arm | HOLDS ×3 | **HOLDS on arm A, arm B and arm C** — and the probe is measured to be **unable to fail** | **PASS, and the instrument is shown VACUOUS. Read the row below before citing it.** |
| **N01** | arm C does NOT match arm B on D3 | FLAT, at arm A's level (1–2) | **arm C D3 = 1 / 1** against arm B's 4 / 4 and arm A's 2 / 2 | **PASS**, decisively |
| **N02** | the port does not move D1 | within ±1, ≤1 cell per class | D1: arm B 4/3, arm A 4/3, arm C 3/3 — **all within ±1**; per-class counts **identical on all three arms on all eight instruments (0 cells)**. Arm B did not REDUCE D1 | **PASS** |
| **N03** | the swap moves zero non-adapter cells | FLAT, zero cells | **one non-adapter cell moved**: arm B's `M09` (class `ordering`), `corpus-action-bound` KILLED → `corpus-port-swap:fake` SURVIVED | **FAIL** |
| **N04** | D5 does not separate between arms | FLAT | **D5 = 4 / 4 on all three arms.** Perfectly flat | **PASS** |
| **N05** | ordering stays at zero on every generated corpus | FLAT at 0 for corpus | `M09` **KILLED** by `corpus-whole`, `corpus-slice-led`, `corpus-port`, `map-silent`, `map-checking` on **all three arms** | **FAIL** |
| **N06** | the suite channel produces none of this round's findings | ZERO from suite | **1** — `test_nothing_executable_reads_this_instrument` went red | **FAIL** |
| **N07** | the control repair moves zero cells | FLAT, zero cells | **zero cells moved**, measured on the control's own row and proved from the diff for the other ten | **PASS** |
| **N08** | the control repair moves no judged dimension | FLAT | four dimension-points moved on unchanged artifacts — **but there is no before/after on one instrument to read them across** | **SUPERSEDED** |

---

## The rows that need their reasoning written out

### P02 — FAIL, and the passing half is recorded rather than substituted

There are two candidate instruments and it matters which one the prediction
named. P02's **Direction** field says *"DOWN from 49 of 49"*, and 49 → 56 → 64 is
the lineage of the **eight-instrument `run_controls.py` table**. On that table:

```
arm A vs arm B   64 of 64 identical
arm A vs arm C   64 of 64 identical   (and 88 of 88 over ALL rows)
arm B vs arm C   64 of 64 identical
```

**The number the prediction named did not move.** P02 is FAIL.

On the **port-binding columns**, which did not exist when 49 of 49 was measured,
one comparable cell does diverge — arm B's `M09` under `corpus-port-swap:fake` —
and arm C does **not** show it, so it is attributable to a port rather than to
prompt length, which is the second half P02 asks for.

**That half is recorded here, not used to convert the verdict.** Reading P02 as
PASS would mean switching denominators to the one that moved, after seeing which
one moved. The epic's rule is *"never re-run selectively until a number passes"*,
and swapping instruments after the fact is the same act with fewer keystrokes.

### P04 — FAIL, and the sealed prediction is STRICTER than what this ticket did

Measured, driver `run_port_swap.py`, controls' roles executed against each run's
own counts:

| control | red on | witness |
|---|---|---|
| `M07` | `corpus-action-bound`, `corpus-port-swap:real`, `corpus-port-swap:fake` — **on all three arms** | 294 accepting `Reserve` executed per column |
| `M07` | `corpus-port` (8-instrument table) — **on all three arms** | 294 accepting `Reserve` |
| `PA-M14` | all four corpus columns of `reference_ports` | 294 accepting `Reserve` per column |
| `N01` | **GREEN everywhere** — a working negative control | — |

**P04's own consequence clause is harsher than the treatment this round applied.**
It says: *"If either survives, **every number in its tree is void** and PA-06
reports the instrument as unciteable rather than reporting kills."* This ticket
did **not** report the port-scoped columns as unciteable. It reported them as a
**FLOOR**, which is PA-04's framing and the epic owner's instruction in this
ticket's dispatch (*"Every port-scoped kill number is a floor"*).

That divergence is recorded rather than resolved silently, because a sealed
prediction being quietly softened is the exact move this file exists to prevent.
Both readings are on the page; a reader who takes the sealed one should treat
every `SURVIVED` in a port-scoped column as saying nothing at all, and `PA-M12`'s
`KILLED` as the only citable cell there.

### P07 — PASS on its stated instrument, and the instrument cannot fail

P07's instrument is named in the row: `check_catalogue.py --controls --tree-root
--root <arm tree>`. It was run per arm, on `PA-M14` re-anchored **by the property
rather than by the bytes** as `seeded_faults.toml`'s `re_anchoring_rule` demands,
and it reports **HOLDS on arm A, arm B and arm C** — including arm C, whose cell
was sealed `UNMEASURED`. On its own terms P07 PASSES and the verdict is not
softened.

**And the adversarial channel then measured the instrument and it cannot fail.**

- **`AD-F5`.** A control whose mutation replaces `self._next_id: int = 1` with
  *the identical line plus a comment*, declared `control_role = "positive"`,
  reports **`HOLDS — invisible until an accepted reserve executes`**. The probe
  tests only "invisible BEFORE"; nothing tests "visible WITH".
- **`AD-F4`.** `PA-M14`'s declared observable — *"available(t) is one too low
  immediately after an ACCEPTED reserve"* — is **false on three of the four trees
  it is declared on**. Measured after one accepted `reserve("t1", 2)`:
  `reference_ports` 1 → 1, arm A 1 → 1, arm C 1 → 1, **arm B 1 → 0**. The trees
  that STORE `available` deduct the parameter; only the one that DERIVES it shows
  the fault in one step. **Every corpus case is single-action, so `PA-M14` cannot
  be killed by any corpus on three of the four trees, whatever the projection
  does.**

**P07's own row wrote the warning this round walked into:** *"A control that
cannot fail is worse than one that is honestly broken, and re-creating that
defect here — in the round whose predecessor's worst finding was exactly it —
would be this epic's worst possible own goal."* `PA-01-DF-05`'s whole subject is
that nothing ever checked a positive control against the property that makes it
one. PA-01 built the check; the check is one-sided. Filed as `PA-06-DF-07`,
severity blocking, and **not repaired** — the probe is an instrument under
measurement.

**What P07's PASS is still worth:** it is a true statement that the re-anchoring
preserved the declared property on every tree, which is more than `M07`'s
semantic managed (BROKEN on arm B, re-measured here). What it is not worth is
evidence that any arm now has a working positive control. It does not.

### N03 — FAIL, and the cell is NAMED, which is what N03 asked for

> *"If a non-adapter cell does move, **that cell is the finding** and it must be
> named, because it means the swap is reaching something nobody designed it to
> reach."*

**The cell: arm B, `M09-negative-control-ledger-order`, class `ordering`, between
`corpus-action-bound` (KILLED) and `corpus-port-swap:fake` (SURVIVED).**

It moves in the direction N03 did not consider. N03 reasoned that *"a fault in the
domain is equally visible through either wiring; running the suite twice cannot
find it twice"* — true, and irrelevant here, because `M09` on arm B is **not in
the domain**. It is in `quota_ledger/file_journal.py`, arm B's real driven
adapter, `boundary_kind = "port"`. Under the fake wiring that file is not on the
executed path at all, so the swap did not *find* something extra: it **lost**
something the other wiring holds.

Arms A and C move zero cells, on every row, between the same two columns.

### N05 — FAIL, and the more interesting fact is WHEN it became false

`M09` is killed by five of the eight generated instruments on every arm.

N05's stated basis — *"Sets in the model, ordered lists in the code, `sorted()` at
every oracle layer"* — is **true of `N01` and false of `M09`**, and the record
already said so when N05 was sealed. `examples/validation/ab/eval/controls.toml`
retired `M09` as a control at `EVAL-STABLE` for exactly this reason: this model
represents its ledger as a *sequence* (`ledger' = Append(ledger, ...)`, projected
as a tuple and compared positionally), so ordering **is** expressible and the
corpus sees it. PA-03's sealed `kill-table-arm-a.json` records
`M09 / corpus-whole = KILLED`.

So N05 was sealed against data that already falsified it, in a file the sealing
ticket had read. **Not scored `SUPERSEDED`:** nothing about the instrument
changed, and the escape clause requires that it did. It is a wrong prediction,
and a wrong prediction is what this file is for. Filed as `PA-06-DF-03`.

**The ordering class is not uniformly zero and never was.** `N01` — reversing the
order of `outstanding_ids()` while keeping the set identical — **SURVIVED all
eight instruments on all three arms, including the hand-written suite.** That is
the row N05's reasoning actually describes, it is a working negative control, and
it is a documented limit that nothing retracted this round.

### N07 — PASS, measured rather than assumed, and it is the R-H3 converse

`N07` needed a **before**, and none existed: the pre-repair `PA-M14` was authored
at `e6d1351` and replaced at `46c29c9` without any instrument ever executing it.
`UNMEASURED is not a pass`, so it was measured — the pre-repair row extracted
verbatim from `46c29c9^` and run through the identical six columns on the
identical tree.

| instrument | before the repair | after the repair |
|---|---|---|
| `corpus-action-bound:real` | SURVIVED | SURVIVED |
| `corpus-action-bound:fake` | SURVIVED | SURVIVED |
| `corpus-port-swap:real` | SURVIVED | SURVIVED |
| `corpus-port-swap:fake` | SURVIVED | SURVIVED |
| `suite-real` | **KILLED** | **KILLED** |
| `suite-fake` | **KILLED** | **KILLED** |

**Zero cells moved.** And the other ten rows need no run: `git diff 46c29c9^
46c29c9 -- examples/validation/ab/seeded_faults.toml` changes exactly one
mutant's `id`, `find` and `replace`, so no cell of theirs *can* have moved — a
fact about the input, which is stronger evidence than a run.

**This is the third time the same shape has been right** (RP-02, N05-of-the-
predecessor, now N07), and it is the case `references/eval_scorecard.md` R-H3 was
extended to cover: *a repair can move **no** number and still change what the
numbers mean.* The repair moved nothing and changed everything about what the
control is worth — before it, the control's semantic broke on re-anchoring onto
arm B; after it, the property holds on all three arms. **`verdicts_moved = 0` is
an answer that had to be measured, and it was.**

---

### N08 — SUPERSEDED, and the movement it was watching for is reported anyway

N08's instrument is *"D1–D5, both blind judges, all three arms"*, before and
after the control repair. **There is no before.** The only "before" that exists is
EVAL-RERUN's sealed cards, and R-H1 forbids reading across the gap: two named
instrument changes sit between them (`PA-03-corpus-port`,
`PA-04-port-swap-columns`), PA-05 added R-H1..R-H4 to the rubric, the judges are
different agents, and this round gave each judge all three artifacts where
EVAL-RERUN gave each one. The instrument turned out not to measure what the
prediction assumed, which is what `SUPERSEDED` is for, and it must cite which —
it is the whole judged instrument, on both counts.

**The movement is reported regardless, because N08's second sentence tells PA-06
to look for the other change first, and there is one.** Arms A and B are
byte-identical to the sealed trees:

```
arm A  D4  2/2 -> 4/4     arm B  D4  3/2 -> 4/4
arm A  D5  3/2 -> 4/4     arm B  D5  4/3 -> 4/4
arm A  D1  3/3 -> 4/3     arm B  D1  3/3 -> 4/3
arm A  D2, D3  unchanged  arm B  D2, D3  unchanged
```

**The other change is judging practice.** Both PA-06 judges wrote, unprompted and
independently, that they seeded their own faults and ran them against each
author's own suite instead of scoring the packet, and both said that is what
moved a score. D4 anchor 4 requires a demonstrated catch; a judge who executes
one can award it and a judge reading a table cannot. **It is not the control.**
Filed as `PA-06-DF-06`, and it is item three on the ledger's own "evidence we are
fooling ourselves" list — *a score moving without an artifact moving* — which
has now happened.

---

## Five of fifteen FAILED, one SUPERSEDED, and that is the point

`P02`, `P04`, `N03`, `N05`, `N06` failed; `N08` is superseded; nine passed.
**Three of the five failures are NEGATIVE predictions**, which is where a
predictions file earns its keep: `N03` failed and named the cell it existed to
name, `N06` failed in the direction nobody expected, and `N05` failed against
data that already falsified it when it was sealed.

**A round where every prediction passes has measured nothing.** This one did not.

---

## What the sealed confounds got right, and one they missed

The sealed file lists eight confounds. Seven stand exactly as written. Two are
worth marking:

- **Confound 1 — "arm C controls for LENGTH, not for every difference"** — is the
  most load-bearing sentence in the file and it held. Arm C did not match arm B,
  so the confound cuts in the direction the file declared *in advance*: a residual
  in arm C's favour makes the case against length *weaker*, and this round takes
  that reading because nobody may pick it after seeing the result. **And the
  residual is larger than the sealed file records.** PA-06 dispatched
  `arm_c/PROMPT.md` with four additions and did not preserve what it sent; the
  as-dispatched prompt is **124 unique lines vs arm A, +18.1% over arm B, outside
  the declared ±10% tolerance**, with 4 of 124 architectural hits rather than 0 of
  109 — two of them paths PA-06 itself introduced, which told the arm what the
  epic is called. Both defects point *against* this round's conclusion, which is
  why it survives them. Filed as `PA-06-DF-10`; the tolerance claim is retracted.
- **Confound 3 — "`reference_ports/` is not an arm"** — is the one that costs this
  round the most, and the sealed file understated it. Every `adapter_internal`
  mutant in this project lives on `reference_ports/`. **No arm has an
  adapter-internal fault seeded in it at all**, so `GOAL-port-reach` clause 1 is
  demonstrated on a fixture whose mutants and whose code have the same author,
  and never on an artifact any prompt produced. Filed as `PA-06-DF-04`.

**A ninth confound this round adds:** arms A and B were authored in the
predecessor epic and arm C today, by this ticket, from a prompt carrying three
additions arms A and B never had. The arm-C leg is a cross-round comparison and
no blinding removes that.
