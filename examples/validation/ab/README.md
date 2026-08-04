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
| `tests/test_behavior.py` | the shared behavioral contract both arms must pass |
| `seeded_faults.toml` | the catalogue: 10 mutants, exact find/replace |
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

## Running it

```bash
# fixture integrity -- exactly-once, apply/revert, parse, gap coverage, arms
python3 examples/validation/ab/check_catalogue.py --arms

# the shared suite against the reference
uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q

# the model
bash scripts/run_tlc.sh examples/validation/ab/model/QuotaLedger.tla \
                        examples/validation/ab/model/QuotaLedger.cfg

# what the hand-written suite catches, reference only
python3 examples/validation/ab/check_catalogue.py --verify-suite
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
