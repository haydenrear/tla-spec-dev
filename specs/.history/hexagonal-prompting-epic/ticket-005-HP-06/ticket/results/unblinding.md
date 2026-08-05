# Unblinding key, and an honest account of how good the blinding was

## The key

| scorecard `arm` | is | prompt |
|---|---|---|
| `X` | **arm B** | `examples/validation/ab/arm_b/PROMPT.md` — the hexagonal + minimize-complexity ask (the TREATMENT) |
| `Y` | **arm A** | `examples/validation/ab/arm_a/PROMPT.md` — the ordinary implementation ask (the CONTROL) |
| `A-control-reference` | neither | the owner's pre-treatment tracking pass on the fixture reference, `pass: 0`, non-blind, decides nothing |

Sources: `arms/arm_b` → `<scratch>/blind/artifact_X`, `arms/arm_a` →
`<scratch>/blind/artifact_Y`.

## What each judge could and could not see

Each judge received: one artifact's complete tree (implementation, its own
tests, its `NOTES.md`), that artifact's evidence packet (shared-suite result,
full per-mutant per-instrument kill table, what the catalogue could and could not
seed into it, and the mechanical block for **both** artifacts, neutrally
labelled), plus `references/eval_scorecard.md` and the shared `FEATURE.md` and
shared behavioral suite.

Each judge was forbidden the other artifact's source, the other artifact's
evidence packet, either arm prompt, `PREDICTIONS-HP.md`, `seeded_faults.toml`,
`SELF-IMPROVEMENT.md`, and any other judge's output. The four judges were
dispatched independently and none of them could see another's work.

The mechanical block for both artifacts was supplied deliberately: the owner's
`schedule_revision: 2` amendment makes the **arm pair** the before/after that D2
anchor 3 reads against, so a judge with only one column could not reach anchor 3
at all. Source code was still one artifact per judge.

## THE BLINDING LEAKED ON ONE ARM, and the judge who found it reported it

**`arms/arm_a/test_quota_ledger.py:1` opens `"""Arm A's own tests for
quota_ledger.`** — the arm-A agent labelled its own file, and HP-06's sanitising
pass missed it because the pass grepped for `arm A` and the file says `Arm A`.

So both artifact-Y judges could see the label `A`. Judge `Y-p1` found it,
reported it unprompted as "a blinding leak in the experiment", and recorded that
it deducted nothing for it. Artifact X carried no equivalent marker (its
`NOTES.md` header was neutralised and nothing else in its tree names an arm).

**What this does and does not compromise.** The judges were never told what "arm
A" or "arm B" means, were not shown either prompt, and were not told which was
the treatment. What leaked is a *label*, from which a reader could guess that "A"
is the control by alphabet alone. The direction that guess would push is toward
scoring artifact Y lower — and artifact Y is the arm that scored **higher** on
D5 (4 and 3, against artifact X's 3 and 3), which is the opposite of what a judge
rewarding a guessed treatment would produce.

**It was not re-run.** Re-judging artifact Y after seeing its scores would mean
discarding cards and re-running an instrument until a number changed, which is
the thing this ticket is forbidden to do and the thing that would make every
other number here unreadable. The leak is filed as **HP-06-DF-03**, the cards
stand as scored, and the limit is recorded here rather than repaired.

## A second, deeper limit on blinding, which no sanitising pass can fix

Artifact X's `NOTES.md` describes, in its own words, the structural ask its
author was given: a declared port, a fake, a composition point, a stated swap
sentence. A judge reading it learns that *this* artifact was asked for a
structure, even without being told what the other arm was asked for.

This is not a defect in the procedure. It is a property of judging artifacts
whose author was told to explain their design: the treatment is partly legible in
the product. Any future round claiming a blind judgement of an architecture
prompt has to state the same limit.

## The third-pass rule fired zero times

`references/eval_scorecard.md` rule 5: a dimension where the two judges differ by
more than 1 is `contested` and is adjudicated by a third pass citing new
evidence.

| artifact | D1 | D2 | D3 | D4 | D5 |
|---|---|---|---|---|---|
| X (arm B) | 3 / 3 | 2 / 2 | 4 / 4 | 3 / 3 | 3 / 3 |
| Y (arm A) | 3 / 2 | 2 / 2 | 2 / 2 | 2 / 2 | 4 / 3 |

Maximum spread across all ten independent scores is **1** (artifact Y, D1 and
D5). **Zero dimensions are contested and no third pass was run.** Artifact X's
two judges agreed on every dimension exactly.

Agreement this tight is not on its own a virtue — two judges of the same model
family reading the same anchors are not independent in the way two people would
be — and the sealed confounds say so (`PREDICTIONS-HP.md`, confound 4).
