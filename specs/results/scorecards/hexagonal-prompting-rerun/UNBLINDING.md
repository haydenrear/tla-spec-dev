# Unblinding key, and an honest account of how good the blinding was

## The key

| scorecard `arm` | is | prompt |
|---|---|---|
| `P` | **arm A** | `examples/validation/ab/arm_a/PROMPT.md` — the ordinary implementation ask (the CONTROL) |
| `Q` | **arm B** | `examples/validation/ab/arm_b/PROMPT.md` — the hexagonal + minimize-complexity ask (the TREATMENT) |

**The labels are deliberately NOT HP-06's.** That round used `X` for arm B and
`Y` for arm A and published the key. New letters were chosen so that a judge who
stumbled into the sealed run — which all four were forbidden — could not read
this round's arms off it.

Sources: `arms/arm_a` → `<scratch>/blind/artifact_P`, `arms/arm_b` →
`<scratch>/blind/artifact_Q`.

## What each judge could and could not see

Each judge received: one artifact's complete tree (implementation, its own
tests, its `NOTES.md`, sanitised), that artifact's evidence packet (shared-suite
result, full per-mutant per-instrument kill table with the `seeded_by` column,
the executability table, the control status, and the mechanical block for
**both** artifacts, neutrally labelled `P` / `Q`), plus
`references/eval_scorecard.md`, the shared `FEATURE.md` and the shared
behavioral suite.

Each judge was forbidden the other artifact's source, the other artifact's
evidence packet, either arm prompt, `PREDICTIONS-HP.md`, `seeded_faults.toml`,
`examples/validation/ab/README.md`, `NEXT-EPIC.md`, everything under
`specs/results/scorecards/` and `specs/.history/`, and any other judge's output.
The four judges were dispatched independently and none could see another's work.

The mechanical block for both artifacts was supplied deliberately, exactly as
HP-06 did it: the owner's `schedule_revision: 2` amendment makes the arm PAIR
the before/after that D2 anchor 3 reads against, so a judge with one column
could not reach anchor 3 at all. Source code was still one artifact per judge.

## The sanitising pass, and the leak HP-06 had is closed

HP-06's blinding leaked because its pass grepped for `arm A` and the file said
`Arm A`. **This round's arm-A agent produced the identical marker** —
`test_quota_ledger.py:1` opened `"""Arm A's own tests...`, and its `NOTES.md`
header read `# NOTES — arm A`. The sanitiser used case-insensitive regexes over
every `.py` and `.md` in both blind copies, covering `arm a`, `arm-a`, `arm_a`,
`arms`, and both working-directory paths, and the result was verified with a
case-insensitive grep for `arm[ _-]?[ab]`, `arms?`, `hexagonal`, `treatment`,
`control arm` and `EVAL-RERUN`: **clean.**

The blind copies were then proved **AST-identical** to the arms they came from,
file by file, so nothing but comments and docstrings changed.

## What still leaks, and no pass can fix it

Artifact Q's `NOTES.md` describes, in its own words, the structural ask its
author was given: a declared port, a fake, a composition point, a stated swap
sentence, and a section headed "a prompt-level conflict, reported as asked". A
judge reading it learns that *this* artifact was asked for a structure.

This is a property of judging artifacts whose authors were told to explain their
designs. It is unchanged from HP-06 and any future round claiming a blind
judgement of an architecture prompt has to state it.

**Both artifact-Q judges anticipated it unprompted.** One recorded that "the
prose is the best I've scored on this card and I treated the polish as grounds
for suspicion rather than credit"; the other rebuilt the whole catalogue itself
rather than read the packet. Both explicitly declined to infer which arm they
held.

## Three disclosures the judges made, none of which was concealed

1. **Judge `Q-p2` read a file another agent wrote into the shared scratchpad.**
   A concurrently running channel wrote a mutation script into the directory
   seconds after the judge emptied it; the judge read it before realising it was
   not its own, disclosed it, noted it contained no scores or conclusions, and
   moved to an isolated directory.
2. **Judge `Q-p1` saw one untracked path under `specs/results/scorecards/`** in
   `git status --porcelain` output while verifying a `NOTES.md` claim. Path seen,
   nothing opened.
3. **The blind-catalogue author saw six directory NAMES** under
   `specs/results/scorecards/hexagonal-prompting-rerun/` for the same reason, and
   the *names* of forbidden files from an `ls` of `examples/validation/ab/`.
   Nothing opened.

All three are the harness leaking through `ls` and `git status`, not the
sanitising pass failing, and all three were volunteered. **None was re-run**:
discarding a card after seeing its score is the one thing this round may not do.

## The most serious blinding finding is not about the judges

**The answer key leaks into files the blind roles are explicitly ALLOWED to
read.** The blind-catalogue author found that
`examples/validation/ab/model/QuotaLedger.tla`'s header comment **names M02,
M03, M06, M07, M08 and M10 and says where they are seeded**, and that
`model/spec_manifest.yaml` goes further — describing M08 verbatim ("a Commit
that also refunds the hold"), quoting its prior score ("fell to 9 of 10"), and
stating the durable-write result ("3 of 3 … vs 0 of 3").

**Two of that channel's thirty mutants are therefore not independent evidence.**
If the premise of the blind channel is that an author-written catalogue flatters
the mechanisms by roughly a quarter, then the model's prose and the manifest are
a second contamination channel and belong behind the forbidden list. Filed;
not fixed, because fixing a fixture during its own measurement destroys it.

## The third-pass rule fired zero times, again

| artifact | D1 | D2 | D3 | D4 | D5 |
|---|---|---|---|---|---|
| P (arm A) | 3 / 3 | 2 / 2 | 2 / 2 | 2 / 2 | 3 / 2 |
| Q (arm B) | 3 / 3 | 2 / 2 | 4 / 4 | 3 / 2 | 4 / 3 |

Maximum spread across all ten independent scores is **1**. **Zero dimensions are
contested and no third pass was run.** Both judges agreed exactly on D1, D2 and
D3 for both artifacts.

Agreement this tight is not on its own a virtue, and the sealed confound (4)
says why: two judges of the same model family reading the same anchors are not
independent the way two people would be. All four ran here on
`claude-opus-5[1m]`.

**What is new and does argue for the protocol:** all four judges built their own
mutants and ran them, rather than scoring the packet. Two independently
discovered the same false self-certification in artifact P's own test suite, by
instrumenting it, having started from different seeds. That is convergence on
executed evidence rather than on a shared prior.
