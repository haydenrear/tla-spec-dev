Your working directory is `/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/daf0ac7d-2e56-422e-b6df-6330f27b6709/scratchpad/repo/subjects/artifact_Z/`. It is empty. Create your implementation there. The repository root is `/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/daf0ac7d-2e56-422e-b6df-6330f27b6709/scratchpad/repo`; paths below that begin `examples/` are relative to it.

Run the shared behavioral suite against your implementation like this, from the repository root:

    QUOTA_LEDGER_DIR=/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/daf0ac7d-2e56-422e-b6df-6330f27b6709/scratchpad/repo/subjects/artifact_Z QUOTA_LEDGER_IMPL=<the module name you chose> uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q

Do not open any file outside `examples/validation/ab/` other than the ones this message names.

Everything from here to the end of this message is the prompt. Follow it exactly.

---

# ARM A — the control prompt

**Dispatch this file verbatim, as the entire prompt, to one fresh agent.**

This is the **control arm** of the hexagonal-prompting A/B. It is an ordinary
implementation ask: the kind of prompt this feature would get if nobody were
running an experiment. It is a complete, standalone prompt and it is **not arm
B with a section deleted** — nothing here was removed from anywhere, and the
two arms were written independently against the same feature file. That
distinction is the point of the whole design: the predecessor's DP-8 rule is
that a number reported without naming its arm is uninterpretable.

---

## Your task

Implement the feature specified in `examples/validation/ab/FEATURE.md`, in
Python, in the working directory you have been given.

Read the feature file in full first. It is the whole requirement.

## What to deliver

1. Working Python code implementing every command and query in the feature.
2. `examples/validation/ab/tests/test_behavior.py` passing unchanged against
   your implementation. **Do not edit that file.** It is the shared behavioral
   contract; a change to it is a change to the requirement.
3. Whatever tests of your own you think the code needs.
4. A short `NOTES.md` in your working directory saying what you built, what you
   decided, and anything you were unsure about.

## How to run the shared suite

Your implementation must expose the class as `QuotaLedger` and be importable
from a module your `NOTES.md` names. Point the shared suite at it with:

```bash
QUOTA_LEDGER_IMPL=<your.module.path> \
  uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q
```

## Ground rules

- Use the standard library. Do not add dependencies.
- Do not change `FEATURE.md` or the shared suite.
- If the feature specification is ambiguous or self-contradictory, say so in
  `NOTES.md` and pick an interpretation. Do not invent requirements to resolve
  it, and do not implement both.
- Finish. A partial implementation with an elegant fragment is worth less here
  than a complete one, because the thing after this reads the whole surface.

## Files you must not open

These would tell you what is being measured, and an implementer who knows the
answer key is not producing evidence about anything:

- `examples/validation/ab/seeded_faults.toml`
- `examples/validation/ab/check_catalogue.py`
- `examples/validation/ab/reference/`
- `examples/validation/ab/arm_b/`
- `examples/validation/PREDICTIONS-HP.md`
- anything under `specs/results/scorecards/` or
  `specs/.history/*/closed-snapshot/results/scorecards/`

If you open one by accident, say so in `NOTES.md`. That disclosure costs you
nothing and is the only thing that keeps the round interpretable; concealing it
voids the arm.

## What you will not be told

You are one arm of a two-arm comparison. You are not being told what the other
arm is, what is being compared, or on what dimensions, because knowing would
change what you write. Report what you built, not what you think is wanted.
