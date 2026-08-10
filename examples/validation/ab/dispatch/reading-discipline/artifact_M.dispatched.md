Your working directory is `/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/daf0ac7d-2e56-422e-b6df-6330f27b6709/scratchpad/repo/subjects/artifact_M/`. It already contains a working implementation of the feature, and its own notes name the module. That directory is the code you were given. The repository root is `/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/daf0ac7d-2e56-422e-b6df-6330f27b6709/scratchpad/repo`; paths below that begin `examples/` are relative to it.

Run the shared behavioural suite like this, from the repository root:

    QUOTA_LEDGER_DIR=/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/daf0ac7d-2e56-422e-b6df-6330f27b6709/scratchpad/repo/subjects/artifact_M QUOTA_LEDGER_IMPL=<the module the notes name> uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q

Do not open any file outside `examples/validation/ab/` other than the ones this message names.

Everything from here to the end of this message is the prompt. Follow it exactly.

---

# REVISION — a second pass over code that already exists

**Dispatch this file verbatim, as the entire prompt, to one fresh agent.**

This is **not an arm of the A/B.** The three arm prompts (`arm_a/`, `arm_b/`,
`arm_c/`) each ask a fresh agent to build the feature from nothing, and they are
compared against each other. This prompt asks something a greenfield prompt
structurally cannot ask: **take an implementation that exists and revise it.**

It was written independently against the same feature file. It is not an arm
prompt with a section added or removed, and no number measured on an arm is
measured on this.

---

## Section 1 — the ask

You have been given a working implementation of a feature. It passes its
behavioral contract today. **Your job is to make the design simpler without
changing what the program does.**

### What "simpler" means here

Simple does not mean small, or clever, or fewer files. It means **the structure
carries no more machinery than the behavior needs.** The test is one question:
**which distinctions does the behavior actually make?** If nothing — no rule, no
branch, no observable result, no test — can tell two states apart, the
difference between them is representation, not behavior.

Places where accidental structure usually hides. These are places to look, not
rules to satisfy:

- **State nothing reads.** A field every operation writes and nothing ever
  branches on, asserts, or returns. Stated intent is not a reader: name a
  concrete one, or treat it as bookkeeping.
- **The same decision made twice.** Two places that must be changed together
  because they encode one rule between them.
- **A representation wider than the distinctions.** If the program behaves
  differently at "none", "some" and "all", it has three cases, however the value
  happens to be stored.
- **An operation that touches most of the state.** Usually several jobs in one
  step.
- **Indirection with nothing behind it.** A layer, wrapper, or interface with
  exactly one thing on the other side of it that nothing ever replaces, and no
  concrete alternative you can name.
- **A parameter, flag, or branch no caller ever varies.**

### What you must not do

- **Do not change behavior.** Not the results, not the rejection reasons, not
  the order of checks, not what is written to the durable side, not the values
  any query returns. If you believe the existing behavior is wrong, **say so in
  your notes and leave it exactly as it is.** Correcting it here would make the
  revision impossible to read.
- **Do not add behavior.** No new commands, queries, options, configuration, or
  error handling that the feature file does not require.
- **Do not rename things for taste.** A rename is not a simplification and it
  buries the ones you did make in noise.
- **Do not restructure the code into a different architecture because you would
  have built it differently.** You are revising this design, not replacing it.
  Where the existing design makes a structural choice the feature file leaves
  free, that choice stands; simplify *within* it.

### And a smaller number is never, on its own, a better design

Any count — of lines, files, classes, branches, fields — goes down when you
delete something, and the count cannot tell you whether what you deleted was
carrying behavior. So for **every** removal or collapse, do one of two things
explicitly in your notes:

- point at the code or the test that still holds the behavior it carried; or
- say plainly that the behavior is gone, and why you think that is correct.

"The tests still pass" is the weakest possible form of the first one, because
the tests were written against the design you are changing.

### If there is nothing worth simplifying, say so and change nothing

That is a real and acceptable outcome, and it is worth more than a revision
invented to have something to report. A pass that changes nothing and explains
what it looked at and why each candidate was left standing is a complete answer
to this prompt. **Do not manufacture a change.**

---

## Section 2 — the feature it must keep implementing

`examples/validation/ab/FEATURE.md` is the whole requirement, and it has not
changed. Read it in full before you touch anything: a simplification that
deletes a behavior the feature requires is not a simplification, and the
existing code is not the specification.

## Section 3 — what to deliver

1. The revised implementation, in the working directory you have been given.
2. `examples/validation/ab/tests/test_behavior.py` passing unchanged.
   **Do not edit that file.** It is the behavioral contract; a change to it is a
   change to the requirement.
3. Every test that came with the implementation still present and still passing,
   **unless** a test tested a structure you removed. If you delete or rewrite a
   test, name it in your notes and say what still covers the behavior it
   covered. Deleting the test that would have caught your change is the one
   move that makes a revision unreadable.
4. Whatever additional tests the revision needs.
5. A `REVISION-NOTES.md` in your working directory, saying:
   - **what you changed**, one entry per change, each with the two-part
     accounting Section 1 asks for;
   - **what you looked at and deliberately left standing**, and why;
   - anything in the original you found unclear, and anything you were unsure
     about.

## Section 4 — how to run the shared suite

The implementation exposes the class as `QuotaLedger`. Its notes name the
module. Run the contract against it with:

```bash
QUOTA_LEDGER_DIR=<your working directory> QUOTA_LEDGER_IMPL=<the module> \
  uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q
```

**Run it before you change anything.** A revision that starts from a red suite
is measuring the wrong thing, and if it is red on arrival, stop and say so in
`REVISION-NOTES.md` rather than fixing it.

## Section 5 — ground rules

- Use the standard library. Do not add dependencies.
- Do not change `FEATURE.md` or the shared suite.
- If the feature specification is ambiguous or self-contradictory, say so in
  `REVISION-NOTES.md` and keep whatever the existing code already does. Do not
  resolve it, and do not implement both readings.
- Finish. Leave the working directory in a state where the suite runs green.

## Section 6 — files you must not open

These would tell you what is being measured, and a reviser who knows the answer
key is not producing evidence about anything:

- `examples/validation/ab/seeded_faults.toml`
- `examples/validation/ab/check_catalogue.py`
- `examples/validation/ab/reference/`
- `examples/validation/ab/reference_ports/`
- `examples/validation/ab/arm_a/`, `arm_b/`, `arm_c/`
- `examples/validation/PREDICTIONS-HP.md`, `examples/validation/PREDICTIONS-PA.md`
- anything under `specs/results/scorecards/` or
  `specs/.history/*/closed-snapshot/results/scorecards/`

If you open one by accident, say so in `REVISION-NOTES.md`. That disclosure
costs you nothing and is the only thing that keeps the round interpretable;
concealing it voids the pass.

## Section 7 — what you will not be told

You are not being told who wrote the implementation you were given, what it was
asked for, what it is being compared against, or on what dimensions, because
knowing would change what you write. **Report what you did, not what you think
is wanted.** A revision that changed one thing and says so plainly is worth more
here than one that changed ten and cannot account for them.
