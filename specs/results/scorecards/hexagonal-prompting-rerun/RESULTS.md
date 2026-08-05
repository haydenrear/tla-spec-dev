# EVAL-RERUN — the A/B re-measured on the repaired instrument, and the three goals decided

**This supersedes `../hexagonal-prompting/` on the rows the instrument repair
invalidated. That run is not edited and is not restated.**

## Why this is a re-measurement and not a re-run until a number passed

Re-running selectively until a number passes is forbidden, and the difference
has to stay visible. **The instrument was repaired after HP-06 measured, and
HP-06 is known-invalid on two specific rows** (`SELF-IMPROVEMENT.md`,
"POST-EVALUATION CORRECTION"):

- **Parameter recovery gained a fifth mechanism.** `Reserve`'s amount was
  unrecoverable because nothing looked at the value written into a function
  entry. **0 of 588** positive `Reserve` cases carried an argument; every one was
  skipped. Recovery is now **4,028 of 4,028**, confirmed by this round's own
  generation run.
- **The negative control was invalid and is replaced.** M09 reverses a sequence
  and this model's ledger *is* a sequence, so it was never negative here. **The
  eval had no valid negative control for two rounds.** N01 replaces it, seeded
  against a set-typed collection, with a reality witness.

Both arms were re-dispatched **verbatim** to fresh agents from
`examples/validation/ab/`; the only text added was one paragraph naming a working
directory, identical on both arms. Same feature, same model, same catalogue, same
rubric, four fresh blind judges.

Also changed underneath the round and not by it: the static architecture scanners
were deleted (9,552 lines), the coverage audit's blocking refusal was retired,
and the state-space bound fell 26,671,680 → 1,111,320. `analyze_complexity.py`
and `fitness_functions.py` are byte-identical and untouched.

## Read these four sentences before any of the good news

1. **The positive control is now GREEN — on the arm where it could be seeded
   faithfully.** Arm A's M07 has no `SURVIVED` cell. **Arm B's M07 is not a
   working control**: an adversarial pass deleted every `Reserve` case from the
   corpus, reproducing HP-06's regression exactly, and arm A's control correctly
   went red while arm B's stayed green.
2. **The generated corpora now TIE the hand-written suite, and the tie is an
   artifact of unioning six instruments.** 10 of 11 against 10 of 11 on the
   seeded catalogue; 11 of 15 against 11 of 15 on a fresh blind one. The best
   *single* generated instrument reaches 7. And **the one mutant nothing kills
   also survives the hand-written suite** — which is why the two-epic-old bar
   sentence needs re-deriving rather than inheriting.
3. **The prompt produced the structure and the structure caught nothing, again.**
   D3 went 2/2 → 4/4. **All 56 strictly comparable per-mutant cells are
   identical between the arms.** A port did not detect one additional fault, and
   it created one region — the fake — that no shared oracle reaches.
4. **Three of thirteen sealed predictions moved against HP-06, and all three are
   informative.** P05 flipped FAIL → PASS (the repair worked). N01 flipped FAIL →
   PASS *from the same prompt text* (the descriptor delta is noise). N03 flipped
   PASS → FAIL (D5 separated, and the judges traced it to executed evidence).

## The scorecard, both arms

Two judges per artifact, blind to arm and to each other,
`references/eval_scorecard.md` in full. Key and an honest account of the
blinding: `UNBLINDING.md`. Schema check: **`4 scorecard(s) checked, 0
problem(s)`**.

| artifact | D1 bugs | D2 complexity | D3 modularity | D4 behavior | D5 honesty | total |
|---|---|---|---|---|---|---|
| **arm B** — hexagonal + minimize-complexity ask | 3 / 3 | 2 / 2 | **4 / 4** | 3 / 2 | 4 / 3 | **16 / 14** of 20 |
| **arm A** — ordinary ask | 3 / 3 | 2 / 2 | 2 / 2 | 2 / 2 | 3 / 2 | **12 / 11** of 20 |

**Contested dimensions: none.** Maximum spread across all ten independent scores
is 1 (arm A's D5, arm B's D4 and D5). Rule 5's third pass fired zero times.

Read that agreement as a limit as much as a virtue — four judges of one model
family reading one set of anchors are not four people (sealed confound 4). What
*does* argue for the protocol is that **all four built their own mutants and ran
them rather than scoring the packet**, and two independently converged on the
same false self-certification in arm A's tests from different seeds.

## Goal verdicts

### GOAL-catch-bugs — `met`

| | |
|---|---|
| **baseline** | D1 = 2 / 2 / 2 / 1 / 0 on five fixtures; **nothing reached 3 on either judge on any example.** Guard relaxation 0 of 3 on both arms and 0 of 4 on a blind catalogue |
| **measured** | **D1 = 3 from both judges on BOTH arms.** Guard relaxation **3 of 3 under `corpus-neg`** on the seeded catalogue on both arms, 0 of 3 under every other generated instrument. On a fresh, independently authored catalogue: **`guard_relaxation` 1 of 1 under `corpus-neg` and 0 of 1 under every other generated instrument, on both arms**, plus two further classes (`guard_basis_confusion`, `rejection_not_inert`) that only `corpus-neg` sees |
| **target** | at least one example scores D1 ≥ 3 from BOTH judges, and guard-relaxation kills > 0 on both the seeded catalogue and a fresh blind one |
| **verdict** | **`met`** — both clauses, on both arms |

**What earned the 3, in the judges' own accounting**: the artifacts' own tests
kill `N01`, which survives **every generated instrument and the shared suite**,
and all three guard relaxations, which `corpus-whole` structurally cannot reach.
Both routes are anchor 3's "a class the whole-view corpus cannot reach on its
own". **No judge gave a 4**, and all four gave the same reason: nothing in either
tree is model-derived.

**The caveat that travels with the verdict.** The whole-view rows on arm A rest
on a positive control demonstrated to fail when its failure mode returns; the
whole-view rows on **arm B do not** (adversarial F1). And the `NOT_DECIDABLE`
mechanism that scopes that control is an unaudited suppression key
(adversarial F2, F3). Neither touches the guard-relaxation result, which is
carried entirely by `corpus-neg`, whose controls are green and whose 94 executed
cases of 118 were independently reproduced.

Run record: `GOAL-catch-bugs/README.md`.

### GOAL-simpler-same-behavior — `missed`

| | |
|---|---|
| **baseline** | highest D2 anywhere is 3 (ex3), both judges withholding 4 for the same reason |
| **measured** | **D2 = 2 from all four judges on both arms.** Mechanically: arm A 122 production lines / 10 branches / 1 module / 20 public names; arm B 129 / 11 / 4 / 25 |
| **target** | an arm-B artifact scores D2 = 4 from both judges, which by the rubric requires D4 ≥ 3 |
| **verdict** | **`missed`** |

**The target was not moved.** Four of four judges rejected the owner's
`schedule_revision: 2` amendment, which was supplied to all of them with the
two-column mechanical block. Their reasons are in
`GOAL-simpler-same-behavior/README.md`; the new one is the sharpest:
**the block reports `mutable_state_count` 8 vs 8 and `max_writers` 2 vs 2 —
exactly the figures arm B's one real simplification would move — and the block
itself says they discriminate nothing.**

**HP-06-DF-05 is now replicated: D2 as written cannot be scored above 2 by an
A/B, across two rounds and eight independent judges.** That is a finding about
the card with enough evidence to act on.

### GOAL-hexagonal-in-fact — `met`

| | |
|---|---|
| **baseline** | D3 = 1 / 1–2 / 3 / 1 / 0–1. Only one fixture ever reached 3 and nothing ever reached 4 |
| **measured** | **arm B: D3 = 4 from both judges.** Arm A: 2 from both |
| **target** | the prompt arm scores D3 ≥ 3 from both judges on the majority of produced artifacts, with at least one 4 |
| **verdict** | **`met`** |

Both judges earned it by executing the swap — one line at `__init__.py:39`, 28 of
28 shared tests still green with `domain.py` byte-identical under `diff -r`, the
ledger file provably never created — and by proving the call topology at runtime
with an audit hook and an instrumented `builtins.open`. Both checked for the hole
HP-02's pilot found (`scenario(fake) == scenario(real)`); it is absent.

**And it still cannot be attributed to hexagonality: 105 unique prompt lines to
16, 6.6x, recomputed on the shipped files.** Two rounds have now produced D3 = 4
without testing "hexagonal" against "longer and more specific". A third arm is
the only thing that would.

Run record: `GOAL-hexagonal-in-fact/README.md`.

## FINDINGS BY CHANNEL — 0 : 15 : 19

| channel | findings |
|---|---|
| **suite re-run** (986 repo tests, 28 + 28 shared, 32 + 53 the arms' own — all green) | **0** |
| **fresh adversarial attack** on this round's own instruments | **15** — three SEVERE, and it falsified five claims this round had already written down |
| **blind catalogue author** asked what it rejected | **19** |
| *(new, not in HP-06's ratio)* **the four judges**, all of whom built their own mutants | **4** — a false self-certifying test, a reachable undisclosed R2/R5 break on a newline in a tenant name, a fake/real contract divergence, and a documented equivalent mutant |

**0 : 15 : 19. Sealed N06 passes for the fourth round running.** Not one of the
green assertions produced a fact about the toolchain that anybody did not
already know.

**But for the first time there is a counter-example, and it should be recorded
as loudly as the zero.** The hand-written suite **as a kill-table instrument**
caught this round's first defect: EVAL-RERUN-DF-01, a stale module reference
that made all eleven mutants execute against pristine code and report SURVIVED.
Six generated instruments did not catch it. A green positive control did not
catch it. **The disagreement between the hand-written column and the generated
columns did** — the exact use `references/eval_scorecard.md` rule 7 puts the
mechanical block beside the judgement for.

For the fourth round running, the single most valuable section of the record is
the one headed **REJECTED**.

## Six of this round's own written claims were false and are corrected in place

Each marked, attributed to the channel that broke it, in
`GOAL-catch-bugs/README.md`:

1. "Both controls are GREEN on both arms … the only reason anything else is
   citeable" — true, and it means two different things on the two arms (F1).
2. "each with a witness the driver verified against this run's own executability
   counts" — false for the `corpus-slice-led` cell, which verifies against a
   **missing key** (F3).
3. "A case naming a different id describes a call this API cannot make" — right
   for 28 of 294 `Reserve` skips, wrong for 266 (F4).
4. "76 comparable cells" — 56 by this round's own rule (F6).
5. "the reason is the negative control" — delete N01 and the tie is unchanged
   (F7).
6. "the only difference between the stored pairs is the `--label` string" — the
   shipped pair is same-label byte-identical, hence indistinguishable from a
   `cp`, and `reference-run.json` is not byte-identical to `final-run-1.json`
   either (F9, F10).

**Four `EVAL-RERUN-DF-*` are filed and none is fixed.** DF-01 is the one
exception in a narrow and stated sense: it was a defect in this round's own
binding, caught mid-run, and the broken run is published beside the good one
rather than deleted.

## The unflattering half

- **The suppression mechanism is real and unaudited.** A declared
  `[[limitation]]` converts a cell to `NOT_DECIDABLE` **before** the mutated run
  is consulted, so it can erase a demonstrated kill with `verified: true`,
  `green: true` and exit 0 — proved twice on this round's own data — and
  `scripts/kill_test.py`'s 19 suppression keys do not include it. **This is a
  defect in the shipped driver and it applies to the sealed reference run too.**
- **Arm B's positive control does not do a control's job**, and the catalogue
  carries arm A's role string verbatim over it.
- **The port's cost replicated and grew a second instance.** A judge found the
  real adapter and the fake are not contract-equivalent, falsifying a claim the
  artifact makes about itself; the blind author found a genuine defect living
  entirely inside the fake and declined to seed it because arm A has no
  counterpart.
- **The one measurable consequence of the architectural difference is not
  measured.** The two arms order the durable write against the memory update
  oppositely — in opposite directions from HP-06's pair — each argues for its
  choice, and nothing in this fixture can price it. Arm B *could* be made to
  price it with a raising `Journal`; arm A has no injection seam at all.
- **The answer key leaks into files the blind roles are allowed to read.**
  `QuotaLedger.tla`'s header names six of the ten seeded mutants and where they
  are seeded; `spec_manifest.yaml` describes one verbatim and quotes prior
  scores. Two of the blind author's thirty mutants are therefore not independent
  evidence.
- **The model does not refine its own specification**, replicated independently:
  the COMMIT record has three fields where the feature's has four, `unknown_tenant`
  is in the reason vocabulary and no action can produce it, `RejectionIsInert`
  does not check inertness, and the model cannot express a negative amount.
- **The two implementations differ in exactly one observable across 3,600
  measured slots** (a 600-step randomized sweep by the blind author): whether
  `commit`/`release` return the reservation id. **The prompt moved the shape
  enormously and the behavior by one ambiguous field.**

## Not seeded, therefore not measured

* **Concurrency** — the specification declares none.
* **Cross-process effects** — the effect oracle is in-process CPython only.

Recorded as *not seeded*, never as *not caught*.

## Where everything is

| | |
|---|---|
| the two arms' code, as produced | `arms/arm_a/`, `arms/arm_b/` |
| the instruments built for this round | `measure/` |
| kill tables, executability, determinism, run record | `GOAL-catch-bugs/` |
| the mechanical block | `GOAL-simpler-same-behavior/` |
| the modularity record | `GOAL-hexagonal-in-fact/` |
| four judged scorecards + index | `ab_quota_ledger/`, `INDEX.md` |
| unblinding key and its limits | `UNBLINDING.md` |
| the sealed predictions, scored, with HP-06 beside them | `PREDICTIONS-SCORED.md` |
| the adversarial and blind-author channels | `channels/` |
