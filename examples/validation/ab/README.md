# The A/B — hexagonal prompting, decided by a scorecard

Built by **HP-01**. This directory is the *experiment*, not any mechanism the
experiment measures. Nothing here refuses anything, gates anything, or blocks a
promotion — per the epic plan's `no_new_gates_rule`, this epic ships no new
blocking check and no new static analyzer.

## The question

The predecessor epic shipped four static architecture checks and measured them
twice. **Bug detection did not move by a single cell.** Every check was
defeated cheaply — six lines of YAML in round 1, a 41-line re-export file in
round 2, both with every declaration digest unchanged.

So this epic inverts the bet: architecture guidance becomes a **prompt**, and
the whole thing is decided by an **A/B judged on a scorecard**. If the prompt
arm catches more bugs and is simpler at equal behavior, we won by prompting. If
it is indistinguishable from the control, the prompt is decoration and we learn
that in one round instead of after another epic of analyzer work.

## The two arms

| Arm | Prompt | Instrument |
|---|---|---|
| **A** | `arm_a/PROMPT.md` | an ordinary implementation ask |
| **B** | `arm_b/PROMPT.md` | hexagonal + minimize-complexity (HP-02 fills its Section 1) |

**Two files, never one prompt with a paragraph switched off.** The predecessor's
DP-8 rule is that a number reported without naming its arm is uninterpretable,
and that discipline is why it has a 4/6 and a 6/6 on the record instead of one
misleading average. `check_catalogue.py --arms` asserts that neither prompt is
the other with a section removed, and reports the shared envelope as a number.

The arms **share** their delivery instructions, ground rules, and blind-reading
rules verbatim. That is not sloppiness — it is the control being held identical
so that the only difference is the treatment, which is arm B's Section 1.

## What is held constant

Same feature (`FEATURE.md`), same model (`model/QuotaLedger.tla`), same seeded
catalogue (`seeded_faults.toml`), same shared behavioral suite
(`tests/test_behavior.py`), same two blind judges, same LLM.

**One model for both arms.** If each arm generated its own, a D1 difference
between arms could be a difference between their models and nobody could tell
which produced it.

## The files

| Path | What it is |
|---|---|
| `FEATURE.md` | the one specification, given to both arms unchanged. Pure behavior; no structure guidance, because structure is the variable under test |
| `arm_a/PROMPT.md`, `arm_b/PROMPT.md` | the two arms |
| `model/QuotaLedger.tla`, `.cfg` | the state machine, **TLC green**: 2649 distinct states, depth 8, four invariants |
| `model/spec_manifest.yaml` | the two aspect slices and the one durable port |
| `reference/quota_ledger.py` | **NOT AN ARM.** the fixed-byte tree the catalogue anchors on |
| `reference_ports/` | **NOT AN ARM.** PA-01's second anchor tree: the same feature with the durable side behind a port, and two composition points over one domain. See its own `README.md` |
| `tests/test_behavior.py` | the shared behavioral contract both arms must pass |
| `seeded_faults.toml` | the catalogue: 10 sealed HP-01 mutants + 4 PA-01 rows, exact find/replace |
| `check_catalogue.py` | the integrity harness |
| `scorecard_shape/` | two zero-score cards proving the two-arm scorecard shape validates |

## The catalogue

Ten mutants, each seeded **in the gap a specific mechanism is supposed to
lose**. That rule has a measured origin: round 1 concluded "case modules kill
exactly what the whole view kills", that conclusion was an artifact of a
catalogue with no cross-aspect mutant in it, and when one was deliberately
placed the claim fell to 9 of 10.

| Mutant | Class | Seeded in the gap belonging to |
|---|---|---|
| M01 zero amount accepted | guard_relaxation | HP-03 — a corpus replays only ENABLED edges |
| M02 quota checked against total | guard_relaxation | HP-03 |
| M03 close with live reservations | guard_relaxation + cross_aspect | HP-03 **and** the aspect slice |
| M04 durable running total stale | durable_content | HP-05 — a silent mapping has no durable oracle |
| M05 CLOSE total always 0, errors swallowed | durable_content | HP-05 |
| M06 release reports rejected, applies anyway | output_oracle | a state-only oracle |
| M07 hold one too large | wrong_value | **POSITIVE CONTROL** — in nobody's gap, must die everywhere |
| M08 commit also refunds the hold | cross_aspect | the aspect slice (CM-F5) |
| M09 ledger written newest-first | ordering | **NEGATIVE CONTROL** — a documented limit, measured instead of assumed |
| M10 release credits back double | wrong_value | HP-04 — the apply()-only blind spot |

Two classes are **deliberately not seeded** and say so in the catalogue:
concurrency (the feature declares none) and cross-process effects (the oracle
cannot see across a process boundary at all, so a mutant there is dead on
arrival). Recorded so HP-06 reports *"not seeded"* rather than *"not caught"*.
PA-01 adds three more declared omissions, each designed and then rejected
rather than merely not thought of.

## PA-01: the third arm, and the class that had nowhere to live

**Arm C** (`arm_c/PROMPT.md`) settles the confound HP-06 recorded and could not
test. Its own words: arm B's prompt was **6.6x longer in unique content**, so
"hexagonal helped" was never separable from "a longer ask helped". Arm C is
matched to arm B in unique content — measured, not asserted — and asks for
nothing architectural.

| | vs A | vs B | vs C |
|---|---|---|---|
| **arm A** | — | 16 | 17 |
| **arm B** | **105** (6.56x A) | — | 89 |
| **arm C** | **109** (1.038x B, +3.8%) | 92 | — |

Unique content = distinct non-blank whitespace-stripped lines present in the
row's arm and absent from the column's. `check_catalogue.py --arms` computes it
and also probes arm C's unique content for architectural vocabulary: **arm B 44
of 105 lines, arm C 0 of 109.**

**If arm C matches arm B, the epic's thesis is wrong** — longer prompts produce
better structure and the architectural content was decoration. That is a
legitimate outcome and arm C was built to be able to produce it. Sealed as
prediction **N01**.

**Four more mutants**, anchored on `reference_ports/` because the flat
reference has no adapter in it and a catalogue that cannot express a class
produces a zero that says nothing:

| Mutant | Class | Seeded in |
|---|---|---|
| PA-M11 real adapter drops CLOSE lines on read-back | adapter_internal | `journal_file.py` — the CONTRAST row |
| PA-M12 fake adapter drops CLOSE lines on read-back | adapter_internal | `journal_memory.py` — **the same fault, other side of the port** |
| PA-M13 fake truncates every stored line | adapter_internal | `journal_memory.py` — the write path |
| PA-M14 hold one too large, ported domain | wrong_value | **POSITIVE CONTROL** for the second anchor tree |

Measured at PA-01, all three wirings control-green
(`[pa_measured_swap_baseline]`):

| mutant | suite-real | suite-fake |
|---|---|---|
| PA-M11 | **KILLED** | SURVIVED |
| PA-M12 | **SURVIVED** | KILLED |
| PA-M13 | SURVIVED | KILLED |
| PA-M14 | KILLED | KILLED |

PA-M11 and PA-M12 are **the same fault**. Under the only wiring the predecessor
had, one dies and the other is untouchable — not because it is subtle, but
because nothing runs the file. That is `BA-B14` reproduced in a fixture we
control, with a twin that rules out "the fault was subtle". **Read the
difference between the rows, never a total.**

The remedy is `reference_ports/quota_ledger_fake.py`, which is four lines. It
went unwritten for a whole epic. Cheap-and-undone is a different finding from
expensive.

## Running it

```bash
# fixture integrity -- exactly-once, apply/revert, parse, gap coverage, arms
python3 examples/validation/ab/check_catalogue.py --arms

# the shared suite against the reference
uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q

# the model
bash scripts/run_tlc.sh examples/validation/ab/model/QuotaLedger.tla \
                        examples/validation/ab/model/QuotaLedger.cfg

# what the hand-written suite catches, references only, all three wirings
python3 examples/validation/ab/check_catalogue.py --verify-suite

# the shared suite through each side of the port
QUOTA_LEDGER_DIR=examples/validation/ab/reference_ports QUOTA_LEDGER_IMPL=quota_ledger \
  uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q
QUOTA_LEDGER_DIR=examples/validation/ab/reference_ports QUOTA_LEDGER_IMPL=quota_ledger_fake \
  uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q
```

At HP-06, re-anchor onto each arm's tree and prove exactly-once again per arm:

```bash
python3 examples/validation/ab/check_catalogue.py \
    --root <arm-tree> --catalogue <arm-catalogue.toml>
```

## The result HP-01 already measured, and it is unflattering

`--verify-suite`, on the reference, with a green control:
**the hand-written suite kills 10 of 10 mutants — including the ordering
negative control.**

That is the bar the generated corpus must clear. If a model-derived corpus
scores below 10 of 10 here, **the generator is worse on this fixture than a
suite a competent engineer writes in an afternoon**, and HP-06 must report it
in those words rather than reporting the corpus's kills in isolation, where
they would read as a success.

It also fixes how every number must be read. The interesting quantity is not
"how many died" but **which instrument saw which class**. Merging the `suite`
row into the `corpus` rows destroys the only comparison this round exists to
make.

*Declared bias:* the 10 of 10 is an upper bound, not typical. The suite was
written before the catalogue but by the same author who chose the fault
classes. It is not evidence that hand-written suites catch everything.

*And one of HP-01's own ten predictions was wrong* — M02 was predicted to
survive the suite and did not, because of arithmetic the author got wrong. It
is corrected in place with the error recorded beside it, because nothing was
dispatched yet. That correction is the entire argument for running
`--verify-suite` at all: otherwise the catalogue would have shipped an
annotation asserting the suite is blind to a class it is not blind to, and
HP-06 would have inherited it as background fact — which is exactly how round
1's guard-relaxation explanation survived a whole epic while being false.

## Sealed before dispatch

`../PREDICTIONS-HP.md` — 7 positive and **6 negative** predictions, each with
an ID, the instrument that settles it, and an expected direction. HP-06 scores
them `PASS` / `FAIL` / `SUPERSEDED` / `UNMEASURED` and **may not amend them**.

`../PREDICTIONS-PA.md` — this epic's, sealed by PA-01 before any other PA
ticket was dispatched: 7 positive and **8 negative**, scored by PA-06 as
written. N01 is the one that can embarrass this epic. N07/N08 were sealed in
the commit before the one that repaired the positive control, so the ordering
is in the history rather than in a promise.

## The positive control was red, and it was red on arm B

`check_catalogue.py --controls` probes whether a declared positive control is
invisible until an accepted `reserve` runs — the property that makes it go red
when `Reserve` stops executing, which is the regression it is the control for.

| tree | M07 semantic | accept-path semantic |
|---|---|---|
| arm A (EVAL-RERUN sealed tree) | HOLDS | HOLDS |
| arm B (EVAL-RERUN sealed tree) | **BROKEN** | HOLDS |
| arm C | UNMEASURED — no tree yet | UNMEASURED |
| `reference/` | HOLDS | HOLDS |
| `reference_ports/` | HOLDS | HOLDS |

Arm B derives `available()`, so the nearest re-anchoring of M07's sealed
semantic is wrong from construction, on every tenant, after a refusal. It stays
green through exactly the regression it exists to catch. **M07 is not deleted,
not re-seeded and not excused** — it still runs and its kills still stand. What
it stops doing on arm B is deciding whether the instrument works.

## FI-04: the arms can diverge, and the arm that has two homes for a fault

The A/B was itself an instrument that could not produce the result which would
refute it. `PA-06-DF-08`: the arms are identical on 10 of 11 mutated rows, so
the experiment could only diverge where **re-anchoring failed**, and the
measured 64 of 64 was arithmetic. FI-04 decided that explicitly — see
`eval/DECISION-fixture-or-goal.md` — and changed the fixture.

One semantic, *"the ledger's read-back silently drops every line beginning
`CLOSE`"*, re-anchored **by the property** onto four sites with nothing in
common. The arms do not agree on how many places it can live:

| arm | homes | why |
|---|---|---|
| A | 1 | one flat module, `_LedgerFile` private and always wired |
| C | 1 | one flat module, and `arm_c/REJECTED.md` records its author declining arm B's seam **on merit** |
| B | **2** | `FileJournal` and `InMemoryJournal` behind arm B's own `Journal` Protocol; exactly one composed at a time |

| row | arm | action-bound | `:real` | `:fake` | suite-real | suite-fake |
|---|---|---|---|---|---|---|
| `FI-M18` | A | KILLED | KILLED | **KILLED** | KILLED | *no such column* |
| `FI-M19` | C | KILLED | KILLED | **KILLED** | KILLED | *no such column* |
| `FI-M16` | B, wired | KILLED | KILLED | **SURVIVED** | KILLED | SURVIVED |
| `FI-M17` | B, unwired | SURVIVED | SURVIVED | **KILLED** | SURVIVED | KILLED |

**The divergence is the `:fake` column on the comparable row — A `KILLED`, C
`KILLED`, B `SURVIVED`** — and swapping in arm B's own fake took a *real durable
fault off the executed path with no instrument reporting that it had.* Arm C is
a third independent re-anchoring and lands on arm A's side, which is the check
PA-04 asked for. **`FI-M17` is the row `PA-06-DF-04` says had never existed on an
arm**, and it has no counterpart on A or C: a second implementation that
disagrees with the first is not a fault a one-implementation tree can host.

Every cell from `run_port_swap.py`, fresh interpreter per cell, controls green
and **read out of the artifact** rather than from an exit code (`FI-02-DF-02`).
`run_controls.py` is never pointed at a ported tree: `FI-01-DF-01`.

```bash
python3 examples/validation/ab/eval/run_arm_swap.py --subject arm_b \
    --cases <port corpus package> --out results/swap-arm_b.json
python3 examples/validation/ab/eval/divergence.py \
    --run arm_a=... --run arm_b=... --run arm_c=... \
    --catalogue arm_a=... --catalogue arm_b=... --catalogue arm_c=... --out d.json
python3 examples/validation/ab/eval/generator_vs_suite.py --out gvs.json
```

PA-01's positive control for the ports tree is therefore seeded on the **accept
path**, which is the one semantic measured to hold the property on every tree
that exists — and `--controls --tree-root` is what PA-06 runs on arm C's tree
before citing a kill number from it. **UNMEASURED is not a pass.**

The defect is not in the ports tree — M07's semantic HOLDS there, because that
tree stores `available`. It is in what happens when the semantic is
**re-anchored onto an arm**. So `PA-M14` is seeded on the accept path, its
`re_anchoring_rule` says to re-anchor **by the property, not by the bytes**, and
`--controls` is what decides whether a given arm has a valid positive control at
all. Repairing it moved the kill table by **zero cells**.
