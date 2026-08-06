# FI-06 — falsifiable-instruments, the evaluation

**A MEASUREMENT, NOT A VICTORY LAP.** Measured on the integrated epic tip
`30d033e` (FI-01..FI-05 all merged), from a worktree at `6c05d22`. Suite:
**1335 passed, 0 failed** (`uv run --with pytest --with pyyaml python -m pytest
tests -q`, 379s).

**Nothing was fixed. Twelve findings are filed, `FI-06-DF-01` .. `FI-06-DF-12`.**

---

## THE THREE GOALS

| goal | baseline | measured | target | verdict |
|---|---|---|---|---|
| `GOAL-instruments-can-fail` | *roughly 0 of ~9* | **26 of 35** as the harness reports it; **at most ~11 of ~43** once the enumeration is swept and the demonstrations are attacked | no target on the ratio; **"nothing is silently omitted"** | **MISSED** — on the only clause it targets |
| `GOAL-scorecard-carries-a-delta` | 4 dimension-points on byte-identical trees | max **1** per judge vs the adjacent sealed row; max **2** vs the row before it, on **D4** and **D5** | at most **1** per judge, on every dimension | **MISSED** |
| `GOAL-fixture-can-diverge` | NULL ENTAILED (64/64, 88/88) | metric retired with reasoning **and** one demonstrated divergence, re-derived byte-identical at the tip | a demonstrated divergence **or** an explicit retirement | **MET, narrowly** |

**No target was edited. No number was re-run until it passed.** Every figure
below is the run that happened.

**The one-sentence answer.** The epic asked *"do we actually know that any of
this works, and would we be able to tell if it did not?"* It built the first
apparatus in this project's history capable of answering that, and the first
thing that apparatus found, when turned on itself, is that **it is short by at
least eight instruments, twelve of its twenty-six demonstrations report `ok` for
a test that never ran, and the judges who produced its best number had been shown
the answer.** That is a better outcome than a clean report and it is the epic's
product.

---

# 1. Do the instruments fail when they should?

## The count, as the harness reports it on the integrated tip

`python3 examples/validation/instruments/demonstrate.py --format json`, exit 0,
artifact at `measure/instruments-at-the-tip.json`:

```
enumerated                              40
of which classified NOT an instrument    5
instruments                             35
WITH a demonstrated failing input       26
WITHOUT one                              9
with a demonstrated BLIND SPOT          12
reproduction failures                    0
```

The baseline the epic opened on was *"roughly 0 of ~9"*. The enumeration found
**35**. **The charter's own baseline undercounted the toolchain by nearly four
times** — before this epic, nobody in this project knew how many instruments it
shipped to within a factor of four. That is the first result and it is the
strongest argument for having run the epic at all.

**And `12 of 35` matters more than `26 of 35`.** Twelve instruments now ship a
*demonstrated inability* — a genuine break they provably do not report. Six of
those twelve fail toward **green**:

| instrument | the break it does not report |
|---|---|
| `control-decision-driver` | cannot measure a ported tree at all — `ARM_MODULE_PREFIXES = ("quota_ledger",)` leaves `domain` and `journal_file` cached. **15 of 15 false `SURVIVED`, no error.** `FI-01-DF-01` |
| `blinding-sanitiser` | `This is ARM B, the hexagonal treatment arm.` — the exact sentence `PA-06-DF-11` measured — **passes CLEAN.** The grep runs after the substitutions and looks for the set they just removed. |
| `dispatch-record` | an **empty evidence directory verifies GREEN**, which is the live state of arms A and B. `FI-05-DF-02` |
| `prediction-seal` | a no-kill row naming no mutant is `UNPARSED` and the exit code is **0**; it reaches **1 of 3** such rows. `FI-05-DF-03` |
| `divergence-reachability` | a mis-declared comparable row gives a **wrong count, not a refusal**. `FI-04-DF-04` |
| `scorecard-audit` | `OPEN` and `UNVERIFIED` are printed and not counted; only `VIOLATION` moves the exit code. |

## The 9 with no demonstrated failing input

Three are `demonstrated-cannot-fail`. One is correct by design —
`produced-code-instrument` is a thermometer, `EXIT_OK = 0` is its only exit
constant, and pointed at a path that does not exist it printed `path: not found
-- reported, not refused` and exited 0. Two are defects: `suite-verification`
prints `*** DISAGREES ***` and never appends it to `problems`
(`FI-02-DF-01`), and `port-swap-driver` has exactly one `Return` in `main()` —
verified at the tip, `run_port_swap.py:543`, `return 0` — while
`eval/results/fi01/swap-reference_ports.json` carries **4** `control_red` entries
from a run that exited 0 (`FI-02-DF-02`).

Five are `no-demonstration-constructible`: four repository tripwires whose
predicate is written inline in a pytest parametrised over a file list resolved
from the test module's own `__file__`, so there is no root a fixture tree can be
handed; and the Test Graph nodes, which need a toolchain this checkout does not
provision. **They are almost certainly correct, and nobody has ever seen one go
red for the reason it exists** — which is exactly the state the thermometer
tripwire was in for a whole epic before `PA-06-DF-05`.

One is `no-instrument-exists`, and **it re-demonstrated itself on this very
ticket.** After `open ticket FI-06`:

```
specs/tickets/FI-06/ticket.yaml:48                 "status": "active"
specs/desired_program_model/ticket_plan.yaml:27    active_ticket: null
specs/desired_program_model/ticket_plan.yaml:117   status: planned     (FI-06's own row)
```

Three files disagree about the state of the ticket being opened, the file an
agent reads first is one of the wrong ones, and nothing compares them.

## THE GOAL'S ONLY TARGET, AND IT IS MISSED

The goal sets **no target on the ratio** — deliberately and correctly. It targets
one thing:

> *"What is targeted is that **NOTHING IS SILENTLY OMITTED** from the
> enumeration."*

`tests/test_instrument_demonstrations.py::test_the_named_instruments_are_all_enumerated`
asserts `required <= enumerated` over a literal list. It catches a **rename**.
It cannot catch an instrument that was **never added** (`FI-04-DF-04`). Inside
this epic that failed three times with the suite fully green — FI-04's
`divergence.py`, and both of FI-05's.

**FI-06's adversarial channel found at least eight more, and one of them is the
enumerator itself.** Verified absent by `tomllib` lookup at this commit
(`FI-06-DF-01`):

```
examples/validation/ab/eval/run_arm_swap.py       SystemExit(status or report_control_state(out))
examples/validation/instruments/demonstrate.py    nonzero when a demonstration stops reproducing
tests/test_instrument_demonstrations.py           repo tripwire, thermometer-tripwire's own family
tests/test_produced_code_prompt.py                gating scan over examples/ and prompts/
scripts/extract_spec_manifest.py                  validate_manifest; main() returns 1
scripts/generate_python.py:967                    same predicate; generation REFUSES
examples/run_distributed_history_validation.py    incl. an explicit NEGATIVE control
examples/validate_split_desired_workflow.py       SystemExit on scaffold drift
examples/effect_providers/run_validations.py      + three validate.py under it
```

Two of these are the epic's own. **`run_arm_swap.py` was shipped by FI-04 in the
same directory, in the same reconcile, as the instrument FI-04 registered by hand
while writing the finding about exactly this failure.** And one of them is
**RED on the shipped tree right now**:

```
$ cd specs/program_model && python3 ../../scripts/extract_spec_manifest.py spec_manifest.yaml
ERROR: missing required manifest key: state
ERROR: missing required manifest key: commands
ERROR: missing required manifest key: results
EXIT=1
```

An unenumerated instrument, red on the repository's own model, watched by
nothing, sharing its predicate with the code generator.

## AND THE 26 DOES NOT SURVIVE EITHER

**All twelve `kind = "pytest"` failing slots declare `expect_exit = 0` and
nothing else — not one carries an `expect_output`.** `judge()` checks the exit
code and substrings; `run_pytest` never inspects output; **pytest exits 0 when
every collected test is SKIPPED.** A one-row probe registry whose failing slot is
a single `@pytest.mark.skip` test prints `ok`, `WITH a demonstrated failing input
1`, `Every declared demonstration reproduced`, exit 0 (`FI-06-DF-02`). This is
the `R-H5` failure generalised: a demonstration can stop running entirely and the
harness still calls it reproduced.

**Two rows have `failing.nodes` byte-identical to `passing.nodes`** —
`complexity-ledger` and `case-modules-validate` run the same command twice and
print `ok / ok`. Confirmed by excision, not by reading: deleting the two tests
the `failing` summary describes leaves the slot reporting `ok`
(`FI-06-DF-03`). **A third, `control-decision-driver`, goes red for a different
reason than the one it states** — `run_controls.py:613-618` short-circuits on
`separates_the_trees == false` before the suite ever runs, and `expect_output` is
the mutant id, which both causes satisfy.

### The honest figure

```
                                      reported      honest
instruments enumerated                      35      >= 43   (floor; nothing enforces completeness)
with a demonstrated failing input           26      <= 23   (26 - 3 unattributable)
   of which cannot go quietly green         --         11   (26 - 3 - 12 pytest-skip-blind)
without one                                  9      >= 20
```

**`GOAL-instruments-can-fail`: the classification clause is met and is real work.
Its only target — "nothing is silently omitted" — is MISSED, and the mechanism
that would meet it was never built.** `26 of 35` is not a ratio over a known set:
the denominator is a floor and the numerator is a ceiling.

## What the epic did buy here, stated plainly

- **The 12 declared blind spots are the most valuable artifact in the epic.**
  Nothing before this round could state what an instrument cannot see.
- **R2 was actually followed, once.** `port-scoped-control-check` ships a failing
  demonstration and **no passing one**, because `PA-M14` is inert on
  `reference_ports` and R2 says it is reported red, not re-anchored into looking
  fine. No green was manufactured.
- **The `R-H5` staleness lesson is now guarded rather than remembered.** FI-02's
  audit demonstration was pinned to `R-H5`; FI-03 implemented `R-H5`; the
  demonstration went green; and `test_every_fast_demonstration_reproduces` caught
  it **on the merge**, because that row asserts `expect_exit = 1` and
  `expect_output`. It was moved to the free id `R-H9`. The id is still pinned —
  but a staleness now goes red instead of quiet. **`FI-06-DF-02` is the same
  lesson not applied to the pytest slots.**

---

# 2. Is the scorecard stable enough to carry a delta?

## Verified on the tip

`score_tools.py audit` → **0 violations**, exit 0, every sealed digest
re-verified and all 38 declared `[[movement]]` entries re-derived from the cards
they name. `check --require-filled` over the three rounds → 18 cards, 18 filled,
**0 problems**.

FI-03's measurement, re-derived independently by FI-06's adversarial channel from
the 22 raw `scorecard.json` files without using `derive_movements.py` — **zero
disagreement, every cell and every summed |movement|**:

```
     PA-06 -> rescore v1   D1:1 D2:0 D3:0 D4:1 D5:1   MAX 1   MET      sum 9
     PA-06 -> rescore v2   D1:1 D2:0 D3:0 D4:1 D5:1   MAX 1   MET      sum 5
EVAL-RERUN -> rescore v1   D1:0 D2:0 D3:0 D4:2 D5:1   MAX 2   MISSED   sum 7
EVAL-RERUN -> rescore v2   D1:0 D2:0 D3:0 D4:2 D5:2   MAX 2   MISSED   sum 10
EVAL-RERUN -> PA-06        D1:1 D2:0 D3:0 D4:2 D5:2   MAX 2   baseline sum 13
        v1 -> v2 (bump)    D1:0 D2:0 D3:0 D4:1 D5:1   MAX 1   MET      sum 4
```

The label mapping `T=Q, U=P` was checked against two `UNBLINDING.md` files that
predate the scores rather than assumed — and it is a hand-typed CLI flag with no
default and nothing validating it.

> **`GOAL-scorecard-carries-a-delta` is MISSED. On D4, and on D5.** Reporting the
> adjacent-row comparison alone would be the flattering half of one measurement
> over the same bytes. FI-03 did not do that; it led with the miss.

## THE TARGET CANNOT DETECT DRIFT, ONLY A JUMP

The measured movement is **directional, not noise**:

```
PA-06 -> v1     signed sum   -7 over 30 cells     8 of 9 movements NEGATIVE
PA-06 -> v2     signed sum   -5 over 30 cells     5 of 5 NEGATIVE
RERUN -> PA-06  signed sum  +13 over 20 cells     9 of 9 POSITIVE
```

`≤1 per judge` is a **max** statistic and is structurally blind to a consistent
one-directional walk. `EVAL-RERUN → PA-06 → FI-03` is an up-then-down excursion
in which every round passes a per-round `≤1` test while the `total` column moves
**4 of 20 points — 20% of the scale — on byte-identical code** (`U`-p2: 11 → 15).
Four more rounds of "MET at −1" walks D5 from 4 to 0 with every step certified
within target.

**And the sharpest point neither FI-03 nor the ledger makes: the card's verdict
on identical bytes depends on which sealed round you compare against.** That
falsifies *"the metric is the delta"* more directly than either verdict does,
because it means the delta is not a property of the pair of artifacts — it is a
property of the pair of reading sessions.

## THE CONSOLATION IS HALF WRONG — D2 IS A CONSTANT

FI-03's `RESULT.md` and `SELF-IMPROVEMENT.md:1121-1122` both carry:

> *"D2 AND D3 MOVED ZERO POINTS ... the strongest stability evidence this project
> has ever produced about anything."*

**D3, yes. D2, no.** Over every `scorecard.json` in the repository including
every sealed `specs/.history` snapshot:

```
D2 on example ab_quota_ledger:   2 on 27 of 27 cards.  No other value, ever.
D3 on example ab_quota_ledger:   1 (x7)   2 (x10)   4 (x10)
```

Twenty-seven cards, five rounds, two card versions, three arms, an owner tracking
pass, every judge. **D2 has taken exactly one value.**

**And it is forced by the anchor, not by the artifacts.** D2 anchor 3 requires
*"a simplification was made and its effect measured — the before and after
figures are both recorded."* These artifacts are built once from a `FEATURE.md`;
there is no before. The judges say so unprompted in their own rationales — *"no
before figure for this artifact exists anywhere"* (PA-06 T-p2), *"Anchor 3 is
unreachable"* (PA-06 W-p2), *"Nothing was transformed from P into Q"*
(EVAL-RERUN Q-p1).

**A dimension that has never taken a second value cannot be shown stable by
failing to move.** D4 and D5 cannot carry a delta because they are noisy. **D2
cannot carry one because it has no signal.** Opposite defects, reported as one
good-news line.

**The ledger already contains its own refutation, fifty lines above.**
`SELF-IMPROVEMENT.md:1069`, written at PA-06 close: *"**D2 reaching 4.** No. All
six cards are 2, and **anchor 3 is now known to be unreachable by construction
under this task design.**"* Then `:1122` calls its zero movement the strongest
stability evidence in the project and `:1144` records *"D2 … can it carry a
delta? **yes**"*. `FI-06-DF-05`.

## AND THE JUDGES WERE SHOWN THE ANSWER

All four FI-03 judges were told, in `JUDGE-DISPATCH-v1.md:39` and `-v2.md:39`,
*"`references/eval_scorecard.md` — the rubric. **Read it.**"* At `51fe73d`, the
commit they scored, that file contains:

```
:334  "## Known instability of this card -- D1, D4 and D5 move on unchanged input"
:361  "| **D2 and D3, both arms** | | **unchanged, zero points** |"
:376  "**D2 and D3 are the dimensions that have held still on unchanged input**"
```

plus a table printing arms A and B's prior sealed D1/D4/D5 values.

```
$ git show 930fa57:references/eval_scorecard.md | grep -c "held still on unchanged input"
0
```

**PA-06's judges did not have it. EVAL-RERUN's did not have it.** So *"D2 and D3
moved zero across four independent pairs"* rests on **two uncontaminated pairs
and two that were shown the conclusion, by name, with the numbers.**

`FI-03-DF-02` and `BYTE-IDENTITY.md` §4 both identify this exact paragraph and
both scope its effect to **D4** — "both v1 judges cited it as their reason for
not executing". Neither notices that the same paragraph asserts the D2/D3
stability finding directly. **The defect FI-03 filed is a subset of the defect it
has.** `FI-06-DF-04`.

**A fifth item belongs on the ledger's "evidence we are fooling ourselves" list
and is currently true: a judge being handed the result before scoring.**

## D3 survives, and it is the only one that does

D3 = 4 for `T`/`Q`/`X` (10 of 10), 2 for `U`/`P`/`Y` (10 of 10), 1 for `W` (7 of
7). Perfectly discriminating, perfectly reproducible across rounds, card
versions and judging practices, and not pinned to floor or ceiling. **Attacked on
floor/ceiling pinning, coarse anchors, judge-family collapse and artifact size —
none held.** `ports-as-adapters` resting its headline on D3 survives this audit.

Three qualifications, none fatal: D3's anchors are near-mechanical (PA-06's T-p1
rationale is literally *"I edited `__init__.py:39` in a scratch copy"*), so its
reproducibility is a check's rather than a judgement's; D3 has never taken 0 or
3; and **`D3 = 4/2/1` was produced by THREE blind pairs, not four** — `W` was
built at PA-06 and did not exist at EVAL-RERUN, which `RESULT.md` §2 itself says
two sections before asserting four pairs for it.

## Which columns of `SELF-IMPROVEMENT.md` are trustworthy

| column | verdict |
|---|---|
| **D1** | **cite with the caveat.** 23 of 27 cards are `3`. Moved 0 of 40 against EVAL-RERUN. The two `4`s are one PA-06 pass-1 judge and have not replicated in two rounds. Cite as "has never left 3", never as a delta. |
| **D2** | **MUST STOP BEING CITED — as anything.** Constant at 2 on 27 of 27. Anchor 3 unreachable by construction. It carries zero bits about the artifact and zero about the card. |
| **D3** | **TRUSTWORTHY — the only column that is.** With: near-mechanical anchors, one model family, **three** pairs not four, and two of those pairs primed by the rubric. |
| **D4** | **MUST STOP BEING CITED.** `2/2 → 4/4 → 3/4 → 4/4` on byte-identical code. Every movement from a version 1 row is permanently `readable = false`, and **exactly one version 2 round exists**, so there is no readable D4 delta in this repository at all. |
| **D5** | **MUST STOP BEING CITED**, for a different reason: both v2 judges executed their own faults and still split 3 against 4 on the same bytes. D4's instability has a mechanism; D5's is an ambiguous anchor and has none. |
| **`total`** | **MUST STOP BEING CITED — the worst column in the file.** It sums a constant (D2) with two dimensions that cannot carry a delta. Observed movement on byte-identical code: **+4 of 20**. It is bolded in every table, in a file whose first line is *"The metric is the delta, not the total."* |
| **`architectural-coherence` baseline table** | **MUST STOP BEING CITED ACROSS EPICS.** Those ten cards were scored at `ab0dfee`, where `references/eval_scorecard.md` **is not in the tree**; they carry no `anchors` block and no `rubric` key. Nothing in the file says this — and they are the only evidence anywhere that D2 is capable of moving. |
| **goal tables** | trustworthy where the goal is mechanical; **not** where the target is a D-number. `GOAL-simpler-same-behavior`'s target is *"D2 = 4 from both judges"* — a target on a dimension that cannot exceed 2 under this task design. It is recorded `missed`; it is **unmeasurable**. |
| **findings-by-channel tables** | **trustworthy.** Counts of provenance, not judge output. Nothing in this audit touches them. |

## The live caveats, verified rather than inherited

- **`FI-03-DF-02` is understated.** The parsed digest `sha256:e33638087c4191da`
  is identical at `f65bb9b` (HP-06 judged, 9,705 bytes), `24ed3fa` (EVAL-RERUN,
  9,705), `930fa57` (PA-06, 16,514), `8878cd5` (16,626), `d3f483d` (19,627) and
  `51fe73d` (FI-03, 19,503) — **one hash over a 2× growth of the file, including
  the entire `R-H1..R-H4` block and the entire instability section.** DF-02
  scopes it to PA-06 vs FI-03-v1; it is every round from HP-06 forward.
  Independently confirmed at the tip: `check --require-filled` now prints
  `RUBRIC-DRIFT` on all twelve v1-and-PA-06 cards and **exits 0 with `0
  problem(s)`**.
- **The anchors digest is not machine-checked.** The rubric claims two versions
  carrying one digest is *"the machine-checked statement that the bar for each
  score did not move"*. `version_history_problems` compares only the **current**
  version's row against the **current** file; version 1's anchors are archived
  nowhere. Editing an anchor and updating both rows passes. The anchors genuinely
  never moved — the claim is true and the sentence describing how it is known is
  false. `FI-06-DF-11`.
- **`--card-version 1` does not reproduce a prior card.** Every anchor, rule and
  digest comes from the current file, so a v1/v2 re-score reads the same anchors
  twice and the change rule is structurally incapable of measuring an **anchor**
  discontinuity. Harmless here only because FI-03 scaffolded the v1 arm before
  editing the rubric — operator sequencing, not a mechanism.
- **`FI-03-DF-01`** — no round before FI-03 preserved its dispatch. Since the
  dispatch tells the judge what to read and how long to spend, and since D4's
  whole instability is *"did the judge run something"*, an unrecorded dispatch
  difference is a plausible **complete** explanation for the D4 movement. **That
  makes every number in FI-03 an upper bound on card instability rather than a
  measurement of it.**
- **`FI-03-DF-04`'s premise is wrong as written** (the log applies a change with
  no `affects` to *every* card, which is the opposite mechanism) **and its
  consequence is right**: every scorecard row in the repository sits on the far
  side of at least one unrecorded card change, `audit` is green, and that green
  is produced by the rubric being invisible to the log.
- **The EVAL-RERUN baseline's judged inputs do not exist.** `BYTE-IDENTITY.md`
  verifies the PA-06-era blind trees and the pre-sanitisation sources.
  EVAL-RERUN's blind copies lived in a scratch dir and were never committed —
  `hexagonal-prompting-rerun/` has `arms/` and no `blind/` — and the two rounds'
  sanitisers demonstrably differ. **The MISS is measured against a baseline whose
  judged artifacts are gone.**
- **One model family.** 37 of 37 cards are `claude-opus-5[1m]`. Four
  "independent pairs" are four samples from one posterior. The exact reproduction
  of PA-06's pass-2 row is simultaneously the strongest result and the strongest
  illustration of this. Fourth round running.

## Mechanical block — recorded, never scored

`scripts/code_complexity.py`, `role=code`, the three judged arms
(`thermometer_rule`; `MF-020`: a figure moving is not evidence about the design):

| figure | arm A (`U`) | arm B (`T`) | arm C (`W`) |
|---|---|---|---|
| modules | 1 | **4** | 1 |
| code_lines | 151 | 202 | 78 |
| callables | 17 | 23 | 11 |
| classes | 4 | 6 | 2 |
| public_surface | 20 | 25 | 11 |
| instance_state | 8 | 8 | 7 |
| declared_interfaces | 0 | **1** | 0 |
| internal_import_edges | 0 | **3** | 0 |
| branch_points | 10 | 11 | 10 |
| max_branch_points_in_callable | 4 | 4 | 4 |
| max_depth | 1 | 1 | 1 |
| **branch_points_in_effectful_modules** | **10** | **1** | **10** |
| **instance_state_in_effectful_modules** | **8** | **1** | **7** |
| effectful_calls | 5 | 3 | 3 |
| effect groups | filesystem | filesystem | filesystem |

**AGREEMENT WITH D2: NONE, AND BY RULE 7 THAT IS A FINDING.** All three arms make
the same kind of outside-world call. The figures separate them by an order of
magnitude on where the branching *lives* — 10 against 1 — and on whether a
boundary is declared at all. **D2 scores all three identically, at 2, from every
judge in every round.** Measurement and judgement disagree, and the card's own
scoring rule 7 says that is a finding rather than a rounding error.

---

# 3. Can the fixture's arms diverge at all?

## The retirement was reasoned, and the reasoning is right

The metric — *the count of comparable cells where the arms AGREE* — was retired
because the catalogue holds the **semantic** equal across arms, so any fault that
could move it is by construction not comparable. **The metric forbids its own
answer.** That diagnosis is correct, and the same-semantic rule it indicts is the
*right* rule for comparing detection. It is the wrong one for comparing
validation shape, and one catalogue cannot do both jobs.

## The replacement, re-derived at the tip

`divergence.py` over FI-04's three sealed run artifacts reproduces
**byte-identically** (JSON equality with the sealed
`results/fi04/divergence.json`: `True`). `git diff 31123dc 30d033e` over every
measurement input — all three arm trees, `reference_ports/`, the model, the
manifest, the shared suite, the catalogues, the swap driver, the case generator —
is **empty**. And FI-06's adversarial channel regenerated the 1,855-case corpus
from scratch and re-ran all three arms independently: **zero cells moved across
all 13 column-slots**, `control_red == []` and `unmutated_control_failed == []`
on every run, read out of the JSON and never from an exit code
(`FI-02-DF-02` respected; `run_controls.py` never invoked on a ported subject,
`FI-01-DF-01` respected).

```
VERDICT: FIXTURE CAN DIVERGE

ledger-readback-drops-close-lines / corpus-port-swap:fake
    arm_a: KILLED    via FI-M18   (compositions=1)
    arm_b: SURVIVED  via FI-M16   (compositions=2)
    arm_c: KILLED    via FI-M19   (compositions=1)
```

**FI-04's measurement discipline is genuinely good and the cells are real.** The
question is what they mean.

## Is the replacement sound, or does it entail its own answer too?

**It is met on the target's own terms, and the apparatus contributes almost
nothing to the conclusion it is presented as supporting.** Six results, in order
of force:

**(a) `arm B SURVIVED` was the only possible outcome — for *any* fault at that
site.** `arm_b_fake.py` composes `Ledger(quotas, InMemoryJournal())`;
`FileJournal` is never constructed under `:fake`; `FI-M16` is seeded in
`file_journal.py`. Dead code cannot fail a test. Four maximally destructive
probes at the same site — read-back returns nothing, read-back raises, append
writes nothing, and **the constructor raising unconditionally** — all give
`KILLED KILLED SURVIVED KILLED SURVIVED`. **The fault's semantics contribute zero
bits.**

**(b) `arm A KILLED` on `:fake` was entailed given `:real` KILLED, and the
artifact says so in English.** Arm A's and arm C's mappings declare no `fake =`
key, and every arm-A and arm-C run writes:

> `"wiring_notes": ["PORT ledger.LedgerAppendPort: NO FAKE DECLARED, so --wiring
> fake ran its REAL adapter. This column decides nothing about a fake for this
> port because there is not one."]`

**`divergence.py`, `run_arm_swap.py` and `FI-04.md` read `wiring_notes`
nowhere.** The single reported divergence is *arm A's real run against arm B's
fake run*, and the instrument's own artifact says the arm-A cell decides nothing.
`FI-06-DF-12`'s neighbour finding.

**(c) Re-anchor one call frame up and the divergence vanishes.** FI-M18's
`re_anchoring_rule` says *"seed at whatever expression returns the durable
ledger's records to a reader"*; FI-M16's adds a qualifier arm A's does not have,
*"in the implementation the default composition wires"*. Applying **arm A's own
rule** to arm B names a second candidate — `Ledger.ledger_lines()` in
`domain.py`, the method every arm exposes and the exact site arm C's FI-M19 is
already at. Seeding there:

```
arm A  KILLED KILLED KILLED KILLED
arm B  KILLED KILLED KILLED KILLED KILLED
arm C  KILLED KILLED KILLED KILLED
divergence.py: NO DIVERGENCE MEASURED. The null is still entailed.
               corpus-port-swap:fake  NOT_REACHABLE  compositions={a:1, b:1, c:1}
```

**Same sentence, same arms, same corpus, same driver. The divergence exists or
does not exist depending on which of two expressions in arm B you choose to
mutate** — and arm B's measured composition count drops to 1, so
"compositions measured from the runs, not read from a mapping" is a function of
the **catalogue**, not of the arm.

**(d) The selector was added after the seal.** `wired_by_default` does not exist
at `4697687`, the commit the predictions were sealed at; both values were added
at `e074ae5`, the commit that first ships the results. Flipping it between FI-M16
and FI-M17, over the same unmodified runs, gives **3 divergences on different
columns** and turns `corpus-port-swap:fake` **RED**. `FI-04-DF-04` calls this "a
wrong count rather than a refusal"; it is worse. `FI-06-DF-09`.

*The declaration is currently TRUE and FI-06 verified it rather than inheriting
it:* `hexagonal-prompting-rerun/arms/arm_b/quota_ledger/__init__.py` —
`QuotaLedger()` returns `Ledger(quotas, FileJournal(ledger_path))`. What does not
exist is anything that would keep it true.

**(e) The sealed analysis goes RED on the same data; the shipped one does not.**
`divergence.py` at `4697687`, run over the same three artifacts, reports 4
divergences and exits **1** with `reachability CLAIMED and NOT DEMONSTRATED on:
suite-fake`. The shipped version splits that branch into a new verdict class
`REACHABLE_BY_ABSENCE` which requires no demonstration and **cannot be red**.
`FI-04.md` says *"The assertion was not weakened."* On that branch it was, in the
commit that shipped the results, and the absence branch has no failing
demonstration. `FI-06-DF-09`.

**(f) Three of the five columns cannot be contradicted by any run.**
`divergence.py:114-124` hardcodes `distinct_compositions: 1` for any column whose
name does not end `:fake`, so `corpus-action-bound`, `corpus-port-swap:real` and
`suite-real` always report `NOT_REACHABLE (E1+E2 entailed)`. The file's own
docstring warns that *"a reachability analysis that cannot come out red is the
fifth unfalsifiable instrument in this repository."* **Three fifths of its output
is exactly that**, and the test named *"measured from the run not read from a
mapping"* asserts those two constants. `FI-06-DF-10`.

**And `corpus-action-bound` is a reprint of `corpus-port-swap:real`.** Applying
`AD-F6`'s own evidence-identity test to that pair returns **True on every row of
every arm**. FI-04's three-arm table has **13 column-slots and 8 distinct
programs**. `FI-06-DF-10`.

## The verdict, and it is not one word

**`GOAL-fixture-can-diverge` is MET.** Both permitted branches were delivered —
the metric was explicitly retired with reasoning, and a divergence was
demonstrated, reproduced from scratch, with green controls read out of the
artifacts. That is more than "missed a second time", which the target names as
the one impermissible outcome.

**What it bought is one bit, and the bit is real:** `:real` KILLED on all three
arms was *not* entailed — the fault could have been invisible to the port corpus,
in which case the run goes `CLAIMED_REACHABLE_BUT_UNDEMONSTRATED` and red. And
arm B genuinely has a swappable seam that arms A and C do not, which is a
measured outcome of the prompts.

**What it did not buy: a measurement.** Given that one bit, every remaining cell
in the headline table is derivable by reading three mapping files and one import
graph with nothing executed. The retired metric entailed the **null**; the
replacement entails the **positive**. That is an improvement — a fixture that can
only say "no" is worse than one that can say "yes" — and it is not the same thing
as a fixture whose arms could have surprised us.

**And the one divergence points AGAINST the port**, which the catalogue wrote
down before it was run: *"swapping in the arm's own fake made a real durable
fault invisible, and no instrument reported that it had … it is a COST of the
port, not a benefit."*

## The 8 sealed predictions, scored as written — never amended

`git diff 4697687 e074ae5` shows **not one `predicted_*` string was touched.**

| # | prediction | score |
|---|---|---|
| 1 | `FI-M18` KILLED on all four of arm A's columns | **PASS**, inflated — 2 independent cells, not 4 (`FI-06-DF-10`) |
| 2 | `FI-M19` KILLED on all four of arm C's columns | **PASS**, inflated — same |
| 3 | `FI-M16` KILLED on action-bound/`:real`/`suite-real`, SURVIVED on `:fake`/`suite-fake` | **PASS**; the `:fake` halves entailed |
| 4 | `FI-M17` SURVIVED on action-bound/`:real`/`suite-real`, KILLED on `:fake`/`suite-fake` | **PASS**; largely entailed |
| 5 | **neg:** arm A's and arm C's `:real` and `:fake` cells are IDENTICAL | **PASS — VACUOUS.** Both columns resolve to the same adapter over the same cases in the same driver. A determinism check wearing an architecture check's label. |
| 6 | **neg:** `FI-M17` SURVIVES `corpus-action-bound` | **PASS — entailed by four lines of arm B's own source** |
| 7 | **neg:** `FI-M17` gets no arm-A or arm-C counterpart | **PASS — SELF-FULFILLING.** Its truth-maker is that FI-04 wrote one `[[mutants]]` block per file. |
| 8 | **neg:** arms A and C get no `suite-fake` column at all | **PASS — SELF-FULFILLING.** Its truth-maker is `run_arm_swap.py:109-125`, a hand-written `suites` dict. (The architectural claim underneath is true.) |

**8 of 8, 0 FAIL, 0 SUPERSEDED — and the ledger lists "every prediction passing"
as evidence we are fooling ourselves. It is triggered and it is reported as
triggered.** FI-04 self-declared the shared-author bias (`FI-04-DF-03`). This is
stronger than that concession: **four of the four negatives are structurally
unfalsifiable**, not merely biased. What 8-of-8 buys is that no cell was
reinterpreted after it was seen. It is not surprise, and this round had none from
this channel.

---

# 4. Does anything we generate beat a hand-written suite yet?

## The tip reproduces the correction exactly

`generator_vs_suite.py`, artifact at `measure/generator-vs-suite-at-the-tip.json`:

| catalogue | rows | generated union | suite | generated-only | suite-only | verdict |
|---|---|---|---|---|---|---|
| seeded / arm A (author-written) | 11 | 10 | 10 | — | — | IDENTICAL SETS |
| seeded / arm B (author-written) | 11 | 10 | 10 | — | — | IDENTICAL SETS |
| blind-rerun / arm A | 15 | 11 | 11 | `BA-P11` | `BA-P05` | COMPLEMENTARY |
| blind-rerun / arm B | 15 | 10 | 10 | `BA-Q11` | `BA-Q05` | COMPLEMENTARY |
| ports / `reference_ports` | 5 | **3** | **5** | — | `PA-M13`, `PA-M14` | **SUITE STRICTLY DOMINATES** |

## THE HEADLINE: THERE IS A SECOND BLIND CATALOGUE AND ON IT THE SUITE DOMINATES

`FALSIFIABLE-INSTRUMENTS-EPIC.md` §2 and `FI-04-DF-01` both say *"the only
catalogues in this repository authored **blind**"*. **That is false.**
`specs/results/scorecards/hexagonal-prompting/GOAL-catch-bugs/kill-table-blind-author-arm-{a,b}.json`
is a second blind-authored pair, same channel, same protocol, sealed in the same
tree since `1a2b65f`. Re-derived at the tip:

```
blind-HP06 / arm A   13 rows   generated union 8   suite 9
                     generated-only []   suite-only ['BA-A02']   SUITE STRICTLY DOMINATES
blind-HP06 / arm B   14 rows   generated union 8   suite 9
                     generated-only []   suite-only ['BA-B02']   SUITE STRICTLY DOMINATES
```

It is not an inference — the sealed run record says it in prose at
`.../GOAL-catch-bugs/README.md:146,168`.

**And it is the same fault class.** `BA-A10` / `BA-B10`, `fault_class =
"id_allocation"` — *"ids are REUSED once earlier reservations have been
resolved"* — is `SURVIVED` by `corpus-whole`, `corpus-neg`, `map-checking` **and
`suite`** on both arms. `README.md:147` lists it under *"Invisible to EVERY
instrument including the suite."* `BA-P11`, the one kill that saves the
generator, is the same semantic drawn by a different blind author.

> **The repository holds TWO blind draws of one fault class and they disagree
> completely. n is 2, not 1. The correction cites one and does not know the other
> exists.** `FI-06-DF-07`.

## AND THE MECHANISM IS A CONSTANT IN THE `.cfg`

`QuotaLedger.cfg:8` declares `ResIds = {r1, r2}`. `QuotaLedger.tla:107` requires
`holder[r] = NoTenant` for `Reserve`, and `holder'` is assigned at exactly one
place, `:112`, with `Commit`, `Release` and `CloseTenant` all listing `holder`
UNCHANGED. **No behaviour of this model contains more than two `Reserve`
actions.** No corpus derived from it — whole, slice, negative, port, under any
mapping — can express a third allocation.

```
BA-P11 (rerun blind author)   first reuses an id at allocation #2   INSIDE the ceiling   -> 4 generated columns kill it
BA-A10 (HP-06 blind author)   first reuses an id at allocation #4   OUTSIDE it           -> nothing kills it, suite included
```

**The wall is already instrumented, counted, and printed on every run.**
`eval/oracle.py:86-101` defines `STATE_NOT_EXPRESSIBLE` — *"past `|ResIds|`
reservations the API has left the model's domain behind"* — and records it as
true of **266 of 294** skips. Every rerun kill table reports exactly **294**
skipped cases per corpus column against it, under the older label *"model chose a
reservation id this API would not allocate"*, which attributes a **structural
depth ceiling** to an **argument-choice nuisance**. Three epics of that number in
every artifact and nobody connected it to the id-family survivals.

> **`BA-P11` is not evidence that the generator sees id reuse. It is the
> coincidence that this instance manifests one allocation inside a wall the
> `.cfg` puts at two.** `FI-06-DF-08`.

## The "blind" catalogue was sighted on both instruments

The rerun blind-author prompt grants, by name, `FEATURE.md`, `QuotaLedger.tla`,
`QuotaLedger.cfg`, `spec_manifest.yaml` — **and
`examples/validation/ab/tests/test_behavior.py`, the hand-written suite itself.**
Every mutant carries a `gap_targeted` field naming which instrument it is aimed
at. `BA-P05`'s reads *"a model-derived corpus cannot construct the input"*;
`BA-P11`'s reads *"Corpora that never resolve a reservation before allocating the
next one."* The author says so outright in its `FINDINGS.md` §5: *"`BA-P05` /
`BA-Q05` are seeded there deliberately."*

**The one-kill-each-way is constructed, not sampled.** It shows that an author
with sight of both instruments can build a fault in either one's blind spot. It
is not evidence about the distribution of faults a real engineer writes, and the
correction reads it as the latter. The prompt is a good prompt for *finding*
blind spots and the wrong instrument for *comparing* hit rates.

**And `BA-P11` is a missing assertion on a trace the suite already runs.**
`tests/test_behavior.py:177`,
`test_release_then_reserve_again_uses_the_returned_quota`, does
`reserve → release → reserve` and asserts only `.status == "accepted"`. Adding
`.reservation_id == "r2"` to that existing line kills it. The fault is real — a
live hold silently overwritten is a production-class defect — but the *approach*
is not blind to it; this suite happened not to assert it.

## Per-column kill sets, derived from the raw tables

Both blind-rerun arms, with `suite` inside the uniqueness denominator:

```
                 kills   UNIQUE            subsumed by
corpus-neg           3   none              NOTHING  (but suite ⊇ its whole set)
corpus-slice-led     2   none              corpus-whole, map-checking, map-silent
corpus-slice-res     3   none              corpus-whole, map-checking, map-silent
corpus-whole         7   none              map-checking, map-silent
map-silent           7   none              corpus-whole, map-checking
map-checking         8   none              NOTHING
suite               11   BA-P05            --
```

1. **"No generated instrument has a unique kill" is STILL TRUE on the blind
   catalogues.** `BA-P11` is killed by four generated columns, so no single one
   holds it uniquely. **The suite is the only column in any blind table with a
   unique kill.** What the correction establishes is complementarity between the
   suite and the *union of six columns* — weaker than complementarity between the
   suite and the generator.
2. **No single generated column has ever matched the suite on any catalogue
   here.** Best generated column: `map-checking` at 8, against the suite's 11 and
   10. The tie is six-against-one.
3. **`map-checking ∪ corpus-neg` exactly equals the entire generated union** on
   every full table. Four of six columns have never earned a cell.
4. And `generator_vs_suite.py`'s headline **doubles n** by summing arm A and arm
   B, whose catalogue header states the same fifteen classes are instantiated in
   both. The honest figure is **1 and 1, replicated**.

## The funding answer, committed to

Swept across every kill table in the repository:

- **`corpus-neg`, the negative corpus — the `modular-fuzzing` epic's purchase.**
  **Zero unique kills, anywhere.** Its marginal over the rest of the generated
  family is +3/+3/+3/+2, and **every one of those is also killed by the suite**.
  It is not among the four columns that kill `BA-P11`. Marginal value over a
  hand-written suite, across every catalogue ever run here: **zero mutants**.
- **`corpus-port*`, the port machinery — the `ports-as-adapters` epic's
  purchase.** **Zero unique kills, anywhere.** Its only marginal over the rest of
  the generated family, on any table, is `PA-M12` and `FI-M17`, and both are
  duplicated by `suite-fake`. On its own home fixture the generated union is 3 of
  5 against the suite's 5 of 5. **And it appears in no blind table at all.** It is
  also the only family that returns a *wrong* verdict on a declared positive
  control — `PA-M14`, `must_be: KILLED`, `SURVIVED` on all four port columns,
  each having measurably executed 294 accepting `Reserve` cases.

> **The two mechanisms the last two epics bought contribute ZERO to the one
> comparison that controls for authorship. One is absent from it; the other is
> redundant with the suite inside it.**

**DEFUND the `[ports.*]` binding machinery.** Unconditionally. Two epics, zero
unique kills across every table, strictly dominated on its own home fixture,
never measured blind, and wrong on its own positive control.

**DEFUND `corpus-neg` as a separately funded mechanism**, and `corpus-whole`,
`corpus-slice-res`, `corpus-slice-led` and `map-silent` with it. Zero marginal
cells on every table. If the corpus family survives at all it is one column,
`map-checking`.

**On generation as a whole: WE CANNOT TELL, and the honest reading of the
evidence is now negative.** The complementarity result rests on one fault class,
on a catalogue authored by someone who could see both instruments and aimed at
each one's blind spot, at a depth one allocation inside the model's constant
ceiling — and **the same class drawn independently by a different blind author
scored the generated family zero.** Two epics of instrument defects mean the
measurement is not trustworthy in either direction, so "defund generation
entirely" is not supportable either.

**Fund exactly one thing next: the experiment below. Nothing else.**

## What would change the answer, and why it has never been run

*k* ≥ 4 catalogue authors, each given **only** `FEATURE.md` and the
implementation trees. Withhold the `.tla`, the `.cfg`, the manifest **and the
suite**. Forbid the `gap_targeted` field. Require faults drawn from *how the
requirement could be misimplemented*, not from *what an instrument would miss*.
**Enlarge `ResIds`, `Tenants` and `Amounts` so the constant ceiling is not the
deciding variable.** Run every catalogue through the full column set **including
the port columns**. Report generated-only and suite-only as **sets** per
catalogue, and the **variance across authors**.

Why it has not been run:

1. **No catalogue here was authored without sight of at least one instrument.**
   The seeded catalogue's author wrote the suite. Both blind authors were handed
   the model, the manifest and the suite, and were asked for a `gap_targeted`,
   which *instructs* them to aim.
2. **k = 1 per epoch, and the two epochs were never compared.** Their answers on
   the shared fault class disagree completely, and because nobody put the tables
   side by side the disagreement has been invisible for two epics. **That
   disagreement is the missing error bar, and it is already large enough to
   swallow the result.**
3. **The constants make the ceiling the dominant variable and nobody has varied
   them.** `ResIds = {r1, r2}` has been fixed since the fixture was built.
4. **The port columns have never been run against a blind catalogue.**
   `FI-04-DF-01`'s own `suggested_fix` says exactly this and it is still open.

**Concrete falsifiers, each one mutant wide.** On ports: one mutant, any
catalogue, killed by a `corpus-port*` column and survived by both suite columns.
Currently zero. On the negative corpus: the same. On generation: ≥3
generated-only kills on a catalogue whose author was not shown the suite, on a
model whose constants do not decide the answer. **Against generation: re-run
`BA-P11` with `ResIds = {r1,r2,r3,r4}`. If it survives the generated family
there too, the last kill is gone.**

---

# 5. The claim this epic carried forward and did not check

**`FALSIFIABLE-INSTRUMENTS-EPIC.md:94-98`, under "Established, and worth building
on", restates a RETRACTED number as fact** — one section after the section the
owner had to correct for doing exactly that.

> *"arm C 1/1 — a length-matched control, longer than arm B, **with no
> architectural vocabulary**, scored the lowest of the three. … **The
> predecessor's 6.6× confound is retired.**"*

Measured at the tip against the bytes this epic itself now preserves as
dispatched:

```
$ python3 examples/validation/ab/check_catalogue.py --arms \
      --dispatch-dir examples/validation/ab/dispatch/ports-as-adapters

  arm C / arm B:  1.181  (+18.1%),  tolerance +/-10%
  ARCHITECTURAL VOCABULARY: arm C: 4 of 124 unique lines
      [PORTS]  - `PORTS-AS-ADAPTERS-EPIC.md`, ...
      [ports]  Your working directory is `.../scorecards/ports-as-adapters/arms/arm_c/`

CATALOGUE INTEGRITY FAILED
  arm C's unique content is +18.1% of arm B's, outside the declared +/-10% tolerance.
  ... if it asks for structure it is a second treatment and the confound is not settled.
```

**The control was neither length-matched nor architecturally silent, as
dispatched.** PA-06 measured this honestly and filed `PA-06-DF-10`; the
retraction is at `ports-as-adapters/RESULTS.md:121-125`. **It is in the sealed
record and in neither document that hands the result forward** — `NEXT-EPIC.md`
§0-AAA calls it "the one clean win" without it, and this charter restates it.

This does **not** overturn the D3 result: 1/1 against 4/4 is far outside anything
either defect accounts for, and PA-06 said so. What is false is the stated
tolerance and the "no architectural vocabulary", in the two documents a next epic
reads first. `FI-06-DF-06`.

---

# 6. FINDINGS BY CHANNEL — and the ratio IS the result

## Across the whole epic, FI-01 through FI-06

| channel | findings | what it cost |
|---|---|---|
| **suite re-run** | **0** | one command, in every acceptance list, **green throughout** |
| **the building ticket auditing its own instrument** | **16** | the epic's dominant channel and a new one |
| **blind judge asked what it REJECTED** | **1** | free — a section of the card |
| **blind judges' unprompted disclosure** | **1** | free |
| **fresh adversarial attack (FI-06)** | **12** | four agents, ~280 tool calls, ~18 minutes wall clock in parallel |
| **total** | **30** | |

> **Stated as a result: 0 : 16 : 1 : 1 : 12. The suite produced ZERO. Every one
> of the thirty came from asking an agent what its own instrument cannot report,
> or from telling one to attack.**

**The predecessor ran 1 : 12 : 4 : 2 — 18 of 19 from the REJECTED question or an
attack brief, with the suite's first finding in four rounds. This round the suite
went back to zero, and it did so while three instruments were missing from the
enumeration, twelve demonstrations could report `ok` for a test that never ran,
two had no seeded break, and one shipped validator was red on the repository's
own model.** The ledger's alarm was *"findings arriving only from the suite"*.
The opposite is what keeps happening, and this round is the sharpest instance:
**a suite that is green while the thing it watches is broken is this epic's own
subject, and it arrived in the epic's own findings process.**

**The new channel is the epic's real methodological product.** Sixteen findings
came from a question no previous round asked: *build the instrument, then ask
what it cannot report.* Every FI-01 and FI-02 finding, all four of FI-04's and all
three of FI-05's came from it. It is cheaper than an adversarial agent and it
found the structural defects; the adversarial channel found the ones the builder
could not see because they were about the builder's own frame.

## The four FI-06 channels, and what each was told

Full record in `channels/ADVERSARIAL.md`. Four agents, blind to each other, each
told that a finding making the headline worse is worth more than one confirming
it, each forbidden to write to the repository so the measurement had no moving
floor (`FI-03`'s recorded defect, not repeated).

---

# 7. AGAINST THE "EVIDENCE WE ARE FOOLING OURSELVES" LIST, ITEM BY ITEM

**"Every prediction passing."** — **TRUE ON ONE CHANNEL AND IT IS REPORTED AS
TRUE.** FI-04's eight sealed predictions are **8 of 8**, and four of the four
negatives are structurally unfalsifiable (§3). *"A round where nothing surprises
measured nothing"* — that channel measured nothing. It is not true of the epic:
`GOAL-scorecard-carries-a-delta` is missed, `GOAL-instruments-can-fail`'s only
target is missed, and the generator answer moved twice in opposite directions.

**"Findings arriving only from the suite."** — **FALSE, and the inverse is now
the standing alarm.** Zero of thirty. Fifth round in six with the suite at zero.

**"A score moving without an artifact moving."** — **TRUE, and worse than the
ledger records.** It is true at EVAL-RERUN→PA-06 (+13 over 20 cells, `total` +4),
PA-06→v1 (−7 over 30), PA-06→v2 (−5 over 30), EVAL-RERUN→v2 (+8 over 20), and
across the version bump (4 over 30). **Five separate demonstrations on trees
verified byte-identical at the tree-object level.** The ledger marks it as having
happened once.

**"A withheld case passing that its siblings failed."** — **DID NOT ARISE.**
Nothing was repaired in FI-06 and no fix was measured on the instrument that
found it. FI-06 fixed nothing, by rule.

**A fifth item belongs on the list and is currently TRUE: a judge being handed
the result before scoring** (§2, `FI-06-DF-04`). It is proposed for the list
rather than silently added, because the list is the ledger's.

---

# 8. WHAT FI-06 REJECTED

- **Adding the eight omitted instruments to the registry, or fixing any of the
  twelve findings.** The `measurement_rule` is the whole reason the count means
  anything, and eight of the twelve findings would have moved the numbers this
  ticket exists to report, during the report. The temptation was real on
  `FI-06-DF-01`: registering `run_arm_swap.py` is four lines and would have made
  `26 of 35` into `27 of 36`. **That is the number-fitting the rule forbids.**
- **Reporting `26 of 35` as the answer to question 1**, or `at most 11 of 43` as
  the answer without also reporting the 26. The first is the harness's own
  output and the second is what it survives; a reader needs both and the gap
  between them is the finding.
- **Re-running any measurement after seeing a result.** Every number here is the
  first run of that command at this tip. `demonstrate.py` was run once for the
  count; the per-instrument runs were spot checks that changed nothing.
- **Editing `FALSIFIABLE-INSTRUMENTS-EPIC.md` §3.** `FI-04-DF-01` established
  that a charter claim is corrected by the epic owner, not by the ticket that
  finds it. Filed as `FI-06-DF-06` instead.
- **Amending any sealed prediction, or re-reading a `SUPERSEDED` where a `PASS`
  would have been kinder.** All eight are `PASS`, and the honest report is that
  four of them could not have failed.
- **Softening the "8 of 8" by calling it a partial pass.** The predictions say
  what they say and they came out as written. What is filed is that the negatives
  were unfalsifiable, not that the scores are wrong.
- **Declaring `GOAL-fixture-can-diverge` MISSED on the strength of §3's
  entailment argument.** The target names two acceptable outcomes and FI-04
  delivered both. Moving the verdict to match a better argument found later is
  editing a target to match a result, in the direction that looks more rigorous.
  **The verdict is MET and the entailment is reported beside it at full
  strength.**
- **Declaring `GOAL-instruments-can-fail` MET on the classification clause
  alone.** The goal's text names one target and it is the one that failed.
- **Letting any agent's finding into this document unverified.** Every
  adversarial claim quoted above was independently reproduced by FI-06 before
  being written down — the second blind catalogue, the `ResIds` ceiling, the
  `wired_by_default` diff, the `action-bound ≡ :real` identity, the twelve
  `expect_output`-less pytest slots, the two identical failing/passing slots, the
  rubric leak at `51fe73d:361,376`, and the red `extract_spec_manifest.py`.
  **Two agent claims were dropped for failing that check** (see
  `channels/ADVERSARIAL.md`).
- **Filing `FI-04-DF-01` again.** It is settled and the owner settled it
  independently. `FI-06-DF-07` is filed because it makes the *correction* wrong
  about the record, not because it restores the original sentence.

---

# 9. WHAT THE ADVERSARIAL AGENTS REJECTED

Recorded because the REJECTED question is this project's highest-yield channel
and a rejected attack is evidence about the artifact.

**Channel A (enumeration).** Rejected: the `R-H5` lead — already fixed, moved to
`R-H9`, verified free. `scorecard-audit` reporting 7 violations — an artifact of
its own git-less scratch copy; withdrawn after re-running against the real tree.
`corpus-diagnostics` having no `expect_output` — reproduced and the red names the
stated cause. `tla-complexity-descriptor` firing on a missing file — disproved,
it refuses on the `INSTANCE` construct. `dispatch-record`'s expectation being
incidental — disproved by removing the mutation and watching both strings vanish.
`run_tlc.sh` and the install scripts — usage and prerequisite errors, correctly
excluded. Five `scripts/*.py` parked rather than filed, on the boundary between a
verdict and a precondition, "so the epic owner gets twelve unarguable omissions
rather than seventeen with five to litigate."

**Channel B (divergence).** Rejected: that the mutant fails to apply to arm B —
`applied_exactly_once: true` on every row. That it is a mapping-anchoring miss —
every `find` occurs exactly once. That the cells were fudged — **zero cells moved
across an independent corpus regeneration and three independent runs**; FI-04's
measurement discipline is genuinely good. That `arm_b_fake.py` is an
epic-authored artefact making `:fake` a harness difference — it calls only arm
B's own `__all__` exports and follows arm B's own docstring, and an arm-A
equivalent is genuinely not constructible from arm A's public surface. That arm
B's `:fake` column is dead — `FI-M15` and `FI-M17` both die on it. That the
predictions were amended — they were not.

**Channel C (generator vs suite).** Rejected: that the shipped script's
arithmetic is wrong — recomputed all five tables per column and per mutant id,
**zero disagreements**. That the correction's arithmetic is wrong at the
mutant-id level — **all correct**. That `suite-fake` does not strictly dominate
`corpus-port-swap:fake` — verified from three independent raw tables, it does,
plus exactly two. That the epoch-1 blind catalogue's mis-keyed `refine_variable`
suppressed its kills — disproved, those fields never enter the verdict. That
`BA-P11` is a toy — rejected, it is a genuine production-class defect. That the
blind catalogue is a fraud — rejected as overreach; it self-reports its own leaks
and the problem is the brief's design, not dishonesty.

**Channel D (scorecard).** Rejected: that the reported table is wrong — every
cell reproduced. That the label mapping was fitted to the scores — documented
independently in two `UNBLINDING.md` files that predate them. **That FI-03 buried
the miss — it did not; both documents open with `MISSED` and the REJECTED section
names reporting the flattering half as a move it declined.** That D3 is
degenerate too — attacked on floor/ceiling, coarse anchors, judge-family collapse
and artifact size; none held. That the anchors moved and the digest hid it — they
did not, `eeccf4576bc6fd85` at all seven sampled commits. That the `D4 = 4` gate
is retroactive rubber-stamping — a v1 judge really did award D4 = 4 on all three
artifacts while writing that it had seeded nothing.

---

# 10. DID THIS EPIC MAKE THE PROJECT'S NUMBERS MEAN MORE?

**Yes, and less than it reports.**

**More, in three ways that are real and were not available before:**

1. **Thirty-five instruments are named, and twelve of them now carry a written,
   re-runnable statement of what they cannot see.** No previous round could say
   what any instrument was blind to. Six of those twelve fail toward green, which
   is a class of defect that was previously invisible by construction.
2. **The scorecard's delta question is answered rather than assumed.** D4 and D5
   cannot carry one. D3 can. D2's zero is a constant. Three of the five
   dimensions and the `total` column must stop being cited, and that is a real
   subtraction from what the ledger claimed.
3. **The generator question has an error bar for the first time**, and the error
   bar is bigger than the effect: two blind draws of one fault class, one each
   way, with the favourable one sitting one allocation inside a ceiling the
   `.cfg` sets at two.

**Less, in one way that dominates:**

**Every count this epic produced is a count over a set nothing enforces.** The
goal's only target is *"nothing is silently omitted"*, and the mechanism that
would meet it was never built — `FI-04-DF-04` was filed and not closed, and it
failed three more times inside the epic, once in the ticket that filed it. **A
number whose denominator has no lower bound and whose numerator has no upper
bound is not more meaningful than no number; it is a number with a false
precision the previous rounds did not have.**

**And the epic did to itself, twice, what it was written to stop.** Its charter
restated as settled fact two claims that the sealed record had already retracted
— the generator sentence (§2, corrected by the owner mid-epic) and the arm C
length-match (§3, still uncorrected). **The document that exists to warn against
reading a row forward without checking it contains two rows read forward without
checking.** That is the honest summary of what four epics of mechanism work have
bought: the mechanisms are better and the reading discipline is not, and the
reading discipline is what every one of these failures has been.

**The one recommendation.** Do not open a fifth mechanism epic. Close
`FI-04-DF-04` — the `close ticket` predicate over the diff, one predicate, no
taxonomy — and run the blind-author experiment in §4 with the constants enlarged
and the port columns included. **That is the only outstanding question in this
repository whose answer would change a decision.**
