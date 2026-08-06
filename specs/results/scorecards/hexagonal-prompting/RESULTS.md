# HP-06 — the A/B, judged blind, and the three goals decided

**A measurement, not a victory lap.** Read the four sentences below, then read
`PREDICTIONS-SCORED.md` before believing any of the good news.

1. **The instrument's positive control is RED on the control arm.** M07 exists
   so a table of zeros can be told apart from a broken instrument, and it
   survives all six generated instruments on arm A. HP-05 measured the same red
   control one ticket earlier. Every whole-view corpus number on this page is a
   floor reported under a broken control.
2. **The hand-written suite still beats the generator, and a catalogue nobody
   tuned beats them both down.** On the seeded catalogue: suite 10 of 10, the
   union of all six generated instruments 9 of 10, and the one survivor is the
   positive control. **On this fixture the generated corpus is still worse than a
   suite a competent engineer writes in an afternoon.** On a fresh catalogue
   authored by an agent that had never seen the seeded one: **corpora 8 of 13,
   suite 9 of 13, and four whole classes invisible to every instrument including
   the suite.** A catalogue written by the author of the mechanisms flatters both
   instruments by roughly a quarter.
3. **The prompt produced the structure it asked for, and the structure caught
   nothing extra.** D3 went 2/2 → 4/4. The per-mutant kill verdicts are
   **identical on 49 of 49 comparable cells**. A port did not detect one
   additional fault.
4. **Four of thirteen sealed predictions were wrong, three of them negatives.**
   That is the half of the prediction file that exists to catch this project
   repeating something it has recorded as fact.

## The scorecard, both arms

Two judges per artifact, blind to arm and to each other, `references/eval_scorecard.md`
in full. Unblinding key and an honest account of how good the blinding was:
`UNBLINDING.md`. Schema check: `5 scorecard(s) checked, 0 problem(s)`.

| artifact | D1 bugs | D2 complexity | D3 modularity | D4 behavior | D5 honesty | total |
|---|---|---|---|---|---|---|
| **arm B** — hexagonal + minimize-complexity ask | 3 / 3 | 2 / 2 | **4 / 4** | 3 / 3 | 3 / 3 | **15 / 15** of 20 |
| **arm A** — ordinary ask | 3 / 2 | 2 / 2 | 2 / 2 | 2 / 2 | 4 / 3 | **13 / 11** of 20 |
| *pre-treatment control (owner pass 0, decides nothing)* | 0 | 2 | 1 | 2 | 3 | 8 of 20 |

**Contested dimensions: none.** Maximum spread across all ten independent scores
is 1 (arm A's D1 and D5). Rule 5's third pass fired zero times. Artifact X's two
judges agreed on every dimension exactly — which is worth reading as a limit as
much as a virtue: two judges of the same model family reading the same anchors
are not independent the way two people are (sealed confound 4).

### Why arm A's D1 differs by one, and it is HP-06's own fault

Judge `Y-p2` capped D1 at 2 partly because HP-06's evidence packet said "no case
that calls `reserve` ever executes" while the same table credits `corpus-neg`
with killing M03 and `corpus-whole` with killing M06 — both of which need a live
reservation. The judge called it a contradiction and refused the anchor.

**It is not a contradiction, and the packet should have said so.** Live
reservations are *installed* into the before-state by the adapter, not built by
calling `reserve`. Negative `Reserve` cases do run and do call `reserve`, but
every one of them is a rejected call that returns before the mutated line. Both
statements are true together.

One missing sentence in a measurement's own prose moved a judged score by one
anchor. Filed as **HP-06-DF-04**, not fixed — re-writing the packet and
re-judging is exactly the selective re-run this ticket may not do.

## Goal verdicts

### GOAL-catch-bugs — `met`, and read the caveat in the same breath

| | |
|---|---|
| **baseline** | D1 = 2 / 2 / 2 / 1 / 0 on five fixtures; **nothing reached 3 on either judge on any example**. Guard relaxation 0 of 3 on both arms and 0 of 4 on a blind catalogue. |
| **measured** | **D1 = 3 from both judges on arm B** (and 3 / 2 on arm A). Guard relaxation **3 of 3 under `corpus-neg` on both arms** on the seeded catalogue, 0 of 3 under every other generated instrument. On a fresh, independently authored catalogue: **1 of 1 under `corpus-neg`, 0 of 1 under every other generated instrument, on both arms**. |
| **target** | at least one example scores D1 ≥ 3 from BOTH judges, and guard-relaxation kills > 0 on both the seeded catalogue and a fresh blind one |
| **verdict** | **`met`** |

**The caveat that travels with it and must never be separated from it:** the
catalogue's positive control is red on arm A, so the whole-view corpus rows are a
floor under a broken instrument. The D1 = 3 anchor is *not* carried by those
rows — it is carried by `corpus-neg`, whose own controls are green on both arms
(94 of 118 cases executed, zero failures on unmutated code) and which does not
depend on a positive `Reserve` case existing. Both judges reached 3 by that
route and both refused 4 for control reasons.

Run record: `GOAL-catch-bugs/README.md`, `kill-table-arm-{a,b}-merged.json`,
`determinism.txt` (two full runs byte-identical, failure text and case order
included).

### GOAL-simpler-same-behavior — `missed`

| | |
|---|---|
| **baseline** | highest D2 in the set is 3 (ex3), and **both judges withheld 4 for the same reason** — the reduction was not shown behavior-preserving |
| **measured** | **D2 = 2 from all four judges, on both arms.** Mechanically: arm B 123 significant production lines / 11 branches / 4 modules / 21 public names; arm A 147 / 13 / 1 / 17. |
| **target** | an arm-B artifact scores D2 = 4 from both judges, which by the rubric requires D4 ≥ 3 |
| **verdict** | **`missed`** |

The target was not moved and is not up for amendment; the owner's
`schedule_revision: 2` amendment said so in advance and said this goal was on
track to be missed. It was, though **not for the predicted reason**.

Every judge gave the same account: **neither artifact made a simplification and
measured it.** D2 anchor 3 requires a before and an after of *something*, and
both arms implemented the same spec from scratch. Arm B's own notes state it
collapsed nothing and has no deletion to point at. The owner amendment's
proposal — read the arm pair as the before/after — was supplied to every judge
in the evidence packet, and no judge accepted it as satisfying anchor 3: two
independent artifacts are a comparison, not a refactoring.

**That is a finding about the metric, not about the arms.** D2 as written cannot
be scored above 2 by an A/B at all. Filed as **HP-06-DF-05**.

The unpredicted part: **arm B came out smaller.** Sealed N01 predicted the
treatment's descriptor would not be lower; it is lower on lines and on branches
and higher on modules and public names. HP-02's pilot on an *earlier draft* of
the prompt measured 274 lines against 120 and recorded N01 as reproduced; the
shipped text goes the other way. A prediction confirmed against a draft is not
confirmed against what shipped.

Run record: `GOAL-simpler-same-behavior/README.md`, `mechanical.json`.

### GOAL-hexagonal-in-fact — `met`

| | |
|---|---|
| **baseline** | D3 = 1 / 1–2 / 3 / 1 / 0–1. **Only one fixture ever reached 3 and nothing ever reached 4.** |
| **measured** | **arm B: D3 = 4 from both judges.** Arm A: 2 from both. |
| **target** | the prompt arm scores D3 ≥ 3 from both judges on the majority of produced artifacts, with at least one 4 |
| **verdict** | **`met`** |

The first 4 on any dimension other than D5 in the project's history. Both judges
earned it by **running the artifact's real-adapter/fake parity suite themselves**
rather than believing its notes, and both checked specifically for the hole
HP-02's pilot found in an earlier draft of this prompt (`scenario(fake) ==
scenario(real)`, which cannot fail for any fault in the rules). The sentence
added to close that hole was never re-measured by HP-02; this is its first
measurement and it held.

**And it cannot be attributed to hexagonality.** 105 unique prompt lines to 16 —
6.6x. This round cannot distinguish "hexagonal guidance helped" from "a longer,
more specific ask helped", and a third arm this epic does not run is what would.

Run record: `GOAL-hexagonal-in-fact/README.md`.

## The structural result nobody predicted

**Three of the ten catalogue mutants cannot be written against arm B at all.**
M08, M10 and (faithfully) M07 are all faults in *maintaining a redundant stored
count*. Arm A keeps `held` as a stored counter three commands mutate; arm B
computes the held total from the live reservations on every read. Arm B has no
place for those three faults to live.

The shipped integrity harness reports it rather than this file asserting it:

```
python3 examples/validation/ab/check_catalogue.py --root <arm-b> --catalogue <arm-b-catalogue>
  8 mutant(s) ... CATALOGUE INTEGRITY FAILED
  no mutant in required class 'cross_aspect'
  no mutant declares a fault in the 'apply()-only' gap
```

This is the only thing in the round that looks like the treatment producing a
*detection* benefit, and it is worth being careful about what it is: not "the
port caught a bug" but "a design with less redundant state has fewer places for a
class of bug to exist." It also means **the two arms' raw kill counts are not
comparable and were not compared** — arm B's evidence rests on eight mutants,
arm A's on ten, and M07 is not the same experiment on the two arms.

## The fresh, independently authored catalogue — and it is the least flattering thing here

A second agent, forbidden the sealed catalogue and every HP-06 result, authored
**13 mutants for arm A and 14 for arm B** from the implementations, the
specification and the model. Same instruments, same run.

| | arm A | arm B |
|---|---|---|
| generated corpora, union | **8 of 13** | **8 of 14** |
| hand-written suite | **9 of 13** | **9 of 14** |
| invisible to EVERY instrument, suite included | **4** | **5** |

Against the seeded catalogue's 9 of 10 and 10 of 10. **A catalogue written by the
author of the mechanisms flatters both instruments by roughly a quarter.** That
is the single most useful number this round produced and no prediction contains
it.

Four classes nothing in this fixture can see: `guard_order`, `id_allocation`,
`query_projection`, `durable_encoding`. On arm B a fifth: `unwired_adapter`.

**A second class only the negative corpus sees, which nobody claimed.**
`rejection_side_effect` — a rejected call that performs a durable write — is 1 of
1 under `corpus-neg` and 0 of 1 under every other generated instrument on both
arms. HP-03 built the negative corpus for guard relaxation; it also catches the
class R4 is actually about.

**And the port's cost, which nobody predicted.** `BA-B14` is a fault in arm B's
in-memory journal adapter. It survives every instrument **including the
hand-written suite**, and arm A has no counterpart, because arm A has one durable
implementation whose composition point is its constructor. The port removes
places for some faults to live *and creates a region no shared oracle reaches* —
the fake that earned arm B its D3 = 4 is verified by nothing outside arm B's own
tests.

**A correction to HP-06's own conclusion, from the same channel.** HP-06's
catalogue records that M08 and M10 "cannot be written" against arm B. The blind
author seeded the cross-aspect leak into arm B anyway, by **adding** a
quota-inflating statement rather than perturbing one, reproducing M08's exact
observable — and it died. The corrected claim is that **the asymmetry is in
seedability, not killability**: a one-token operand slip in arm A, an invented
statement in arm B. HP-06's catalogue was **not** re-seeded after the fact.

## Which instrument saw which class — the only quantity worth reporting

| class | corpus-whole | corpus-neg | slice-res | slice-led | map-silent | map-checking | suite |
|---|---|---|---|---|---|---|---|
| guard_relaxation (3) | **0 of 3** | **3 of 3** | 0 of 3 | 0 of 3 | 0 of 3 | 0 of 3 | 3 of 3 |
| durable_content (2) | 1 of 2 | 0 of 2 | 0 of 2 | 0 of 2 | 1 of 2 | **2 of 2** | 2 of 2 |
| ordering (1, negative control) | 1 of 1 | 0 of 1 | 0 of 1 | 1 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| output_oracle (1) | 1 of 1 | 0 of 1 | 1 of 1 | 0 of 1 | 1 of 1 | 1 of 1 | 1 of 1 |
| cross_aspect (1, arm A only) | 1 of 1 | 0 of 1 | **0 of 1** | **0 of 1** | 1 of 1 | 1 of 1 | 1 of 1 |
| wrong_value — arm A (2) | 1 of 2 | 0 of 2 | 1 of 2 | 0 of 2 | 1 of 2 | 1 of 2 | 2 of 2 |

Identical on both arms except the `wrong_value` row, which contains M07.

* **Guard relaxation moves only under the negative corpus**, and it moves fully.
  0 of 3 / 0 of 3 / 0 of 4 across three catalogues, five instruments and two
  rounds of the predecessor; **3 of 3** here, on two real implementations rather
  than a fixture reference. HP-03's headline reproduces.
* **The mapping is worth exactly one mutant** — M04 — and the arm is worth
  nothing. The direction replicates for the fifth time; the magnitude does not
  reproduce as a proportion, for the fourth time. **The "30% of the instrument's
  yield" figure is a fixture property and must not be quoted as a mechanism
  property.**
* **Ordering is not invisible to corpora.** M09 dies under `corpus-whole`,
  `corpus-slice-led` and both mappings. HP-03 already retracted the claim; this
  reproduces the retraction on two arms. Ordering is invisible when the modelled
  thing is a **set**; this model uses a **sequence**.
* **The aspect slices lost what they were declared to be lost by.** M08 dies
  under the whole view and survives both slices, exactly as P04 predicted.

## Findings by channel — the ratio, stated as a result

| channel | findings |
|---|---|
| **suite re-run** (1130 + 143 + 2×28 assertions, all green) | **0** |
| **fresh adversarial attack** on HP-06's own instruments | **17**, six of which falsified a claim HP-06 had already written down |
| **blind author** asked what it rejected | **13** |

**0 : 17 : 13. Sealed N06 passes for the third round running, and the alarm it
exists to fire should be read as firing: the suite has stopped being
informative.** Not one of 1,329 green assertions produced a fact about the
toolchain that anybody did not already know.

For the third round running, the single most valuable section of the whole
record is the one headed **REJECTED**.

**Six of HP-06's own written claims were false and are corrected in place**, each
marked and attributed: the guard-relaxation zero's stated mechanism, the
`branches` comparison, the `state_writers` workaround, the determinism coverage,
the arm-B M07 catalogue entry, and the forbidden cross-class aggregate. The most
consequential is the first — **this model spells refusals out as first-class
actions, so the whole-view corpus *does* contain refusal cases and HP-06's own
oracle skips all 39,688 of them.** The 3-of-3 under `corpus-neg` survives
adversarial tracing; the framing of the zeros beside it does not.

Everything is in `FINDINGS.md`; twelve `HP-06-DF-*` are filed and **none is
fixed**.

## Not seeded, therefore not measured

* **Concurrency** — the specification declares none.
* **Cross-process effects** — the effect oracle is in-process CPython only, so a
  mutant there is dead on arrival.

Both are recorded as *not seeded*, never as *not caught*.

## Where everything is

| | |
|---|---|
| the two arms' code, as produced | `arms/arm_a/`, `arms/arm_b/` |
| the instruments | `measure/` |
| kill tables, determinism, run record | `GOAL-catch-bugs/` |
| the mechanical block | `GOAL-simpler-same-behavior/` |
| the modularity record | `GOAL-hexagonal-in-fact/` |
| four judged scorecards + index | `ab_quota_ledger/`, `INDEX.md` |
| unblinding key and its limits | `UNBLINDING.md` |
| the sealed predictions, scored | `PREDICTIONS-SCORED.md` |
| findings by channel, and everything filed | `FINDINGS.md` |
