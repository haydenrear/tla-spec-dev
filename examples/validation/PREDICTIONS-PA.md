# PREDICTIONS — ports-as-adapters epic

**Sealed at dispatch. PA-06 scores these and may not amend them.**

Committed by PA-01 *before* PA-02, PA-03, PA-04 or PA-05 is dispatched. Every
row has an **ID**, the **instrument** that settles it, and an **expected
direction**. A prediction with no instrument is an opinion, and an opinion
cannot be wrong in a way anyone notices.

## Why this file exists, and why half of it predicts nothing moving

The predecessor's two most informative results were both negatives.

One was **predicted**: HP-04 repaired the effect oracle from 8 of 18 actions to
18 of 18 — a real, correct, well-evidenced repair — and moved the seeded-mutant
matrix by **zero cells**, exactly as N05 said it would. Because it was
predicted, the round could say what the repair was worth instead of arguing
about it.

One was **not**: arm B produced a `Protocol` port, a real adapter, a working
fake, one composition point and a domain importing no I/O — the first D3 = 4 in
this project's history — and its per-mutant verdicts were **identical to arm
A's on 49 of 49 comparable cells**. The structure arrived and caught nothing.
Nobody had written that down as a possible outcome, so it read as a surprise
rather than as a measurement.

**A round where every prediction passes has measured nothing.** The bar this
file sets: at least three predictions must be about something NOT moving, and
they must be things a reader would plausibly expect to move. Six are recorded
(N01–N08). Predicting that an unrelated number stays flat is padding.

## Ground rules

- Agents implementing the arms are **never shown this file**, before or during
  their run. It is in every arm's do-not-open list.
- Findings during measurement are **FILED, never fixed** — a fix during a
  measurement destroys the measurement.
- Every number is reported **per arm, per class, and per instrument**. A kill
  rate with no arm named is uninterpretable.
- **Never average across examples or across arms.** Never merge the `suite` row
  into the `corpus` rows.
- **Read the difference between PA-M11 and PA-M12, never their total.** They
  are one fault seeded on both sides of one port; a count that adds them
  together destroys the only comparison they exist to make.
- Scoring vocabulary at PA-06: `PASS`, `FAIL`, `SUPERSEDED` (the instrument
  turned out not to measure what the prediction assumed — must cite which
  instrument and why), or `UNMEASURED` (the instrument did not run — must say
  why). **`UNMEASURED` is not a pass.**

## The arms

| Arm | Prompt file | Instrument under test |
|---|---|---|
| **A** | `examples/validation/ab/arm_a/PROMPT.md` | an ordinary implementation ask |
| **B** | `examples/validation/ab/arm_b/PROMPT.md` | the hexagonal + minimize-complexity ask |
| **C** | `examples/validation/ab/arm_c/PROMPT.md` | **PA-01's addition**: a length-matched control that asks for nothing architectural |

Same feature (`examples/validation/ab/FEATURE.md`), same model, same seeded
catalogue, same shared behavioural suite, same blind judges.

**Arms A and B are byte-identical to the prompts that produced the sealed HP
numbers.** They were deliberately not edited, so PA-06 can compare across the
epic boundary without declaring an instrument change on those two arms. The
cost is on the record rather than fixed: both still say "two-arm comparison"
and neither lists `arm_c/` in its do-not-open section (**PA-01-DF-02**).

### The length match, measured

`python3 examples/validation/ab/check_catalogue.py --arms`, unique content =
distinct non-blank whitespace-stripped lines present in the row's arm and
absent from the column's arm — the same measure that produced the
predecessor's sealed "6.6×".

| | vs A | vs B | vs C | distinct lines |
|---|---|---|---|---|
| **arm A** | — | 16 | 17 | 54 |
| **arm B** | **105** | — | 89 | 143 |
| **arm C** | **109** | 92 | — | 146 |

- arm B unique vs arm A: **105 lines**, = **6.56×** arm A's 16. *That is the
  predecessor's 6.6× confound, re-derived here.*
- arm C unique vs arm A: **109 lines**, = **1.038×** arm B, **+3.8%**, inside
  the declared ±10% tolerance.
- Architectural vocabulary in unique content: **arm B 44 of 105 lines, arm C 0
  of 109.** (A word-boundary vocabulary probe over the content each arm does
  not share with arm A. It cannot detect structural guidance phrased without
  any of those words, and it says so where it is defined.)

**Arm C is 3.8% longer than arm B, not shorter.** That residual is reported
rather than tuned away, and it cuts differently depending on the outcome: if
arm C matches arm B it is a slightly *stronger* case for length, and if arm C
fails to match it is a slightly *weaker* case against it. Nobody may pick the
reading after seeing the result.

## The measured baselines these are predictions against

From the sealed predecessor scorecards, two blind judges, zero contested
dimensions across 25 + 10 independent scores:

| | best ever recorded | where |
|---|---|---|
| **D1** bug detection | **3** — and on **both** arms | the generator, which both arms get; not the prompt |
| **D2** complexity | **3**, never 4 | withheld by both judges twice, same reason |
| **D3** modularity | **4** (arm B, both judges) | the first 4 in the project |
| **D5** honesty | **4** | and it went to the *control* |

Per-mutant verdicts **identical on 49 of 49** comparable cells between arms.
Guard relaxation 0 of 3, 0 of 3, 0 of 4 before the negative corpus; 3 of 3 and
5 of 5 after it.

### And two baselines measured at PA-01, both unflattering to this epic

**(1) The hand-written suite kills 10 of 10** on the flat reference, control
green (`seeded_faults.toml [measured_suite_baseline]`, re-confirmed by this
ticket's run). That is the bar a generated corpus has to clear, and it is high.

**(2) The port's blind region, measured** (`[pa_measured_swap_baseline]`), all
three wirings control-green before any mutant:

| mutant | suite-real | suite-fake |
|---|---|---|
| PA-M11 real adapter drops CLOSE lines | **KILLED** | SURVIVED |
| PA-M12 fake adapter drops CLOSE lines | **SURVIVED** | KILLED |
| PA-M13 fake drifts from real on write | SURVIVED | KILLED |
| PA-M14 positive control (ports domain) | KILLED | KILLED |

PA-M11 and PA-M12 are the same fault. Under the only wiring the predecessor
had, one dies and the other is untouchable — not because it is subtle, but
because nothing runs the file. **The remedy is four lines**
(`reference_ports/quota_ledger_fake.py`) and nobody wrote it for a whole epic.
Cheap-and-undone is a different finding from expensive.

**(3) The positive control is red on arm B, run rather than read**
(`[pa_measured_control_audit]`). The epic owner reported it from the closing
ledger's prose; PA-01 was asked to verify it against the artifact by running it,
and did. `check_catalogue.py --controls` probes whether a declared positive
control is invisible until an accepted `reserve` executes — the property that
makes it go red when `Reserve` stops executing, which is the regression it is
the control for.

| tree | M07 semantic | accept-path semantic |
|---|---|---|
| arm A (EVAL-RERUN sealed tree) | **HOLDS** | HOLDS |
| arm B (EVAL-RERUN sealed tree) | **BROKEN** | HOLDS |
| arm C | **UNMEASURED — no tree exists yet** | UNMEASURED |
| `reference/` | HOLDS | HOLDS |
| `reference_ports/` | HOLDS | HOLDS |

The owner is right. On arm B, M07 is observable at construction, after a
refusal, and after an accepted `close_tenant` on a tenant with no live
reservation — because arm B derives `available()`, so the nearest re-anchoring
of M07's sealed semantic is wrong everywhere rather than only on the accept
path. It therefore stays GREEN through the exact regression it exists to catch,
which EVAL-RERUN's adversarial channel demonstrated the expensive way with a
corpus with every `Reserve` case deleted.

**Arm C's cell is UNMEASURED, and UNMEASURED is not a pass.** Arm C is a
prompt; its tree is built at PA-06. What PA-01 supplies is the thing that
decides it: a semantic measured to hold on every tree that exists, and a probe
that runs on any tree in seconds. PA-06 runs `--controls --tree-root` on arm C's
tree before citing one kill number from arm C.

---

## Positive predictions

### P01 — the port's blind region closes when, and only when, something wires the fake
**Instrument:** PA-M12 and PA-M13 under `suite-real` and `suite-fake`, per arm,
per wiring, from the per-mutant table.
**Direction:** UP from a measured zero, on the fake column only.
At least one adapter-internal fault seeded in a fake **dies on at least one
generated instrument** once cases are driven through both wirings. Baseline: a
fault of this class survived every instrument the predecessor had, including
the hand-written suite (`BA-B14`).
**This is `GOAL-port-reach`'s stated target.** If it stays at zero, the epic's
central mechanism does not work and PA-06 says so in those words.

### P02 — the arms' verdicts diverge on at least one cell
**Instrument:** the per-mutant verdict table, arm A vs arm B, comparable cells
only, count of cells where the arms AGREE.
**Direction:** DOWN from 49 of 49.
At least one comparable cell differs between arms, **and the divergence is
attributable to a port** rather than to prompt length — which is what arm C is
for. `GOAL-cases-drive-ports`'s target.
**A divergence arm C also shows is not a port result.** Say so.

### P03 — the complexity instrument tells the arms apart
**Instrument:** PA-02's produced-code measurement, run over all three arms.
**Direction:** figures DIFFER between arms.
Baseline: no such instrument exists, which is why D2 measured 2 for both arms
from all four judges. **No target on the number** — a threshold set before
anything can produce a figure would be inventing the answer.

### P04 — both positive controls die everywhere
**Instrument:** M07 (flat tree) and PA-M14 (ports tree), every arm, every
wiring, every mapping.
**Direction:** killed, 100%.
If either survives, **every number in its tree is void** and PA-06 reports the
instrument as unciteable rather than reporting kills. PA-M14 exists because a
column of survivors on `reference_ports/` cannot otherwise be told apart from
an instrument that never ran that tree.

### P05 — all three arms finish
**Instrument:** the shared behavioural suite, and D4.
**Direction:** all three arms ≥ 2 on D4.
If any arm fails the shared suite, **the round is not an A/B/C** and PA-06 says
so rather than reporting the differences.

### P06 — arm B reproduces its D3
**Instrument:** two blind judges, D3.
**Direction:** arm B ≥ 3 from both judges, arm A 1–2.
The predecessor's headline replicated on the same fixture with the same rubric.
If arm B does **not** reproduce D3 ≥ 3, the sealed 4 was a single sample and
PA-06 must say that before interpreting anything else in the round.

### P07 — the repaired positive control holds its property on every arm
**Instrument:** `check_catalogue.py --controls --tree-root --root <arm tree>`,
run per arm at PA-06, including arm C.
**Direction:** HOLDS on all three arms.
**Sealed BEFORE the repair, and this is the whole point of the row.** PA-01
measured the accept-path semantic HOLDS on arm A, arm B, `reference/` and
`reference_ports/`, and it has never been run on arm C because arm C does not
exist yet. P07 predicts it holds there too.
**If it does not hold on some arm, PA-06 must say so and leave that arm's
control RED.** It may not make the cell green by weakening what the control
asserts. A control that cannot fail is worse than one that is honestly broken,
and re-creating that defect here — in the round whose predecessor's worst
finding was exactly it — would be this epic's worst possible own goal.

---

## Negative predictions — what will NOT move

**These are the rows this file exists for.** N07 and N08 were sealed in the
commit *before* the one that repairs the positive control, so the git history
carries the ordering rather than this sentence.

### N01 — arm C will NOT match arm B on D3
**Instrument:** two blind judges, D3, arm C vs arm B, with the measured
unique-content counts (109 vs 105) beside them.
**Direction:** FLAT for arm C — arm C scores at arm A's level (1–2), not arm
B's.
This is the confound the predecessor could not test, recorded as a prediction
so that the answer counts either way.
**If arm C matches arm B, this prediction FAILS and the finding is that longer
prompts produce better structure and the architectural content was
decoration.** That is a legitimate and valuable outcome; arm C was built to be
able to produce it. Nobody may then argue that arm C's subject "also implies
structure" — that argument had to be made *before* the run, and it is not made
here.

### N02 — the port will NOT, by itself, move D1
**Instrument:** D1 per arm from both judges, plus the per-class per-arm kill
table.
**Direction:** FLAT — arms within ±1 on D1, and the per-class counts differing
by at most one cell **for every class except `adapter_internal`**.
The predecessor's cleanest result is that D1 = 3 landed on **both** arms: the
bug-catching gain was the generator, which every arm gets, not the prompt.
Architecture and detection are separate levers. Whatever moves D1 this epic
comes from driving cases through both wirings, not from asking for ports.
**Arm B must also not REDUCE D1.** A prompt producing prettier code whose
adapters catch less has failed.

### N03 — the fake/real swap will move nothing OUTSIDE the adapter-internal class
**Instrument:** the per-mutant table, all classes except `adapter_internal`,
before and after cases are driven through both wirings.
**Direction:** FLAT — **zero cells.**
This is N05's shape recorded again on purpose, because N05 was right and its
being right is the most useful thing the predecessor produced. A fault in the
domain is equally visible through either wiring; running the suite twice cannot
find it twice. **Predicted: coverage-style metrics improve substantially and
every non-adapter row of the kill table is unchanged.**
If a non-adapter cell does move, **that cell is the finding** and it must be
named, because it means the swap is reaching something nobody designed it to
reach.

### N04 — D5 will not separate between arms
**Instrument:** D5 from both judges, three arms.
**Direction:** FLAT.
No prompt says anything about refusing, naming blind spots, or `unobservable`
beating a false clean. D5 measures the toolchain's reports, which are identical
across arms.
**This is also the round's blindness check:** if D5 separates, the most likely
explanation is not that one prompt produced a more honest program — it is that
the judges worked out which arm they were reading. PA-06 must consider that
explanation before any other. Note that the sealed D5 = 4 went to the *control*,
so "the treatment is more honest" has already failed once.

### N05 — ordering stays at zero on every generated corpus, on every arm
**Instrument:** M09 under `corpus-whole`, `corpus-slice`, `corpus-neg`, both
mappings, three arms.
**Direction:** FLAT at zero for every corpus instrument.
Sets in the model, ordered lists in the code, `sorted()` at every oracle layer.
**Measured and stated up front so this is not read as wider than it is: the
hand-written suite DOES kill M09.** So N05 predicts a *split*, not a universal
zero, and the split is the point. A kill by a corpus retracts a documented
limit and is a finding; a survivor confirms one. Both are results.

### N07 — repairing the positive control will move ZERO cells in the kill table
**Instrument:** the per-mutant per-arm per-instrument table, every row, before
and after the control repair, on the trees that exist.
**Direction:** FLAT — **zero cells**, on every row including the control's own,
on arm A and on both references.
**Sealed BEFORE the repair.** This is the RP-02 / N05 shape recorded as a
prediction for the third time, because it was right the first two. Both M07 and
the accept-path control are blatant faults that die to any instrument executing
an accepted `reserve`; the repair changes WHICH LINE is perturbed, not whether
the fault is reachable. The one cell predicted to change is **arm B's control
row, and it changes provenance rather than value**: from green-for-the-wrong-
reason (killed by `CloseTenant` cases on states with no live reservation) to
green-for-the-right-reason. That is not a detection gain and PA-06 must not
report it as one.
**If any non-control cell moves, that cell is the finding** and it must be
named, because it would mean the two semantics are not the same experiment.

### N08 — the control repair will not move any judged dimension
**Instrument:** D1–D5, both blind judges, all three arms.
**Direction:** FLAT.
The judges score artifacts against the rubric. A control is an instrument for
deciding whether the kill table is readable at all; it is not an artifact any
arm produced, and no arm's code changes because of it.
**If a judged dimension moves, the most likely explanation is not the control.**
PA-06 must look for the other change first.

### N06 — the suite channel will produce none of this epic's findings
**Instrument:** PA-06's findings-by-channel table (suite re-run / fresh
adversarial attack / blind author), with counts.
**Direction:** ZERO from the suite channel.
Three rounds running, the best finding came from asking an agent what it
**rejected**, and **zero** came from re-running the suite.
**If it repeats, PA-06 must say plainly that the suite has stopped being
informative.** That alarm exists to fire before the tool silently gets worse.

---

## Stated confounds — read before attributing any win

Not predictions. Limits on what this round can conclude, written now so nobody
argues them away later.

1. **Arm C controls for LENGTH, not for every difference.** It is matched to
   ±3.8% in unique content and asks for nothing architectural by a word-boundary
   probe. It does not control for *subject*: its ask is about evidence and
   documentation, and if writing down every decision happens to produce more
   structure, this round cannot separate that from length either. What it does
   settle is the specific confound the predecessor recorded — "6.6× longer" —
   and no more.
2. **The vocabulary probe is not a semantic judgement.** Zero hits means arm C
   uses none of 34 word patterns. It does not mean arm C is architecturally
   silent in a way a reader would agree with.
3. **`reference_ports/` is not an arm.** Like `reference/`, it exists so the
   catalogue's `find`/`replace` has fixed bytes, and it exists at all because
   the flat reference contains no adapter to seed inside. Its numbers are never
   placed beside an arm's.
4. **The fixture and the mutants seeded into it have the same author.** That is
   the declared bias `[measured_suite_baseline]` already carries; two anchor
   trees do not reduce it.
5. **`n = 1` feature.** One specification, three arms. A dimension that moves is
   a signal about this feature, not a property of prompting.
6. **The judges are agents.** Blind to each other and to arm, citing
   `file:line` — but agents. "Prose quality is never an input" is the one rule
   nothing mechanical enforces, and both long prompts ask for things that tend
   to read well.
7. **The control was repaired BEFORE any measurement, not after one.** The
   standing rule forbids repairing an instrument *after* an unflattering signal
   and forbids moving a *target*. This is neither: no PA measurement exists yet,
   and `GOAL-port-reach`'s target clause ("no positive control is red") is
   untouched by PA-01. The git history is the evidence for the ordering — this
   file, with P07/N07/N08 and the measured audit, is committed in the commit
   BEFORE the one that changes the control.
8. **Arms A and B carry stale text** (PA-01-DF-02): "two-arm comparison", and no
   `arm_c/` in their do-not-open lists. They were left byte-identical on purpose
   so the cross-epic comparison holds. PA-06 must add `arm_c/` to the forbidden
   list out of band and record that it did.

## Scoring template for PA-06

| ID | Prediction | Instrument | Expected | Observed | Verdict |
|---|---|---|---|---|---|
| P01 | an adapter-internal fault dies on a generated instrument | PA-M12/PA-M13 × wiring | UP from 0 | | |
| P02 | arms' per-mutant verdicts diverge ≥ 1 cell | per-mutant table | DOWN from 49/49 | | |
| P03 | complexity instrument separates the arms | PA-02 over 3 arms | figures differ | | |
| P04 | M07 and PA-M14 die everywhere | all arms/wirings | 100% killed | | |
| P05 | all three arms pass the shared suite | shared suite + D4 | all ≥ 2 | | |
| P06 | arm B reproduces D3 ≥ 3 both judges | 2 blind judges | reproduces | | |
| P07 | repaired control HOLDS the accept-path property on every arm | `--controls --tree-root` per arm | HOLDS ×3 | | |
| **N01** | **arm C does NOT match arm B on D3** | 2 blind judges + line counts | FLAT at arm A's level | | |
| **N02** | **the port does not move D1** | D1 + per-class table | within ±1, ≤1 cell | | |
| **N03** | **the swap moves zero non-adapter cells** | per-mutant table by class | FLAT, zero cells | | |
| **N04** | **D5 does not separate** | D5, both judges | FLAT | | |
| **N05** | **ordering stays zero on every corpus** | M09 × corpora (suite kills it, measured) | FLAT at 0 for corpus | | |
| **N06** | **the suite produces no findings** | findings-by-channel | ZERO from suite | | |
| **N07** | **the control repair moves zero cells** | per-mutant table before/after | FLAT, zero cells | | |
| **N08** | **the control repair moves no judged dimension** | D1–D5, both judges | FLAT | | |
