Your working directory is `/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/daf0ac7d-2e56-422e-b6df-6330f27b6709/scratchpad/repo/subjects/artifact_N/`. It is empty. Create your implementation there. The repository root is `/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/daf0ac7d-2e56-422e-b6df-6330f27b6709/scratchpad/repo`; paths below that begin `examples/` are relative to it.

Run the shared behavioral suite against your implementation like this, from the repository root:

    QUOTA_LEDGER_DIR=/private/tmp/claude-501/-Users-hayde-IdeaProjects-tla-spec-dev/daf0ac7d-2e56-422e-b6df-6330f27b6709/scratchpad/repo/subjects/artifact_N QUOTA_LEDGER_IMPL=<the module name you chose> uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q

Do not open any file outside `examples/validation/ab/` other than the ones this message names.

Everything from here to the end of this message is the prompt. Follow it exactly.

---

# ARM C — the length-matched control prompt

**Dispatch this file verbatim, as the entire prompt, to one fresh agent.**

This is a **control arm**, matched to the other long arm in length of unique
content, so that a difference between arms can be attributed to what a prompt
*says* rather than to how much of it there is.

This file is a complete, standalone prompt. It is **not another arm with a
section swapped**. The arms were written independently against the same feature
file, and they are declared as three files precisely so that a reader of the
record can see which instrument produced which number.

---

## Section 1 — the evidence ask

<!-- PA-01-SLOT:BEGIN -->

You are being asked for two things at once. They are in tension, and the tension
is deliberate.

1. **Evidence, for every behavior, that you checked it.**
2. **Nothing asserted that you did not check.**

### 1. Evidence, for every behavior, that you checked it

*Evidence* means a reader who never speaks to you can tell which behaviors you
verified and what you verified them with. A sentence saying the program works is
not evidence; it is the claim the evidence is supposed to support.

- **Walk the feature file clause by clause and account for every one.** Not "I
  read it" — an account. For each clause: where the behavior lives, and the one
  concrete input you ran that would have caught it being absent. A clause you
  cannot name an input for is a clause you have not checked, however confident
  you are.

- **Say how you checked it, not that you checked it.** "Verified", "handled"
  and "covered" are words that survive being wrong. "`reserve('acme', 0)`
  returns `rejected/amount_not_positive`" does not.

- **Every rejection is a behavior, not error handling.** The feature names six
  reasons and an order they are decided in. Each one is a result the program
  must produce, on a named input, and each is worth as much evidence as an
  acceptance. Treat a wrong reason exactly as seriously as a wrong number: both
  are the program telling a reader something false.

- **Try the edges of every number the feature mentions,** and write down which
  ones you tried and what came back — including the ones that behaved the way
  you expected, because "I tried it and it was fine" is evidence and "I assumed
  it was fine" is not.

- **Record every ambiguity the moment you hit it,** with the sentence that
  produced it and the reading you chose. Not at the end, from memory: you will
  forget the ones you resolved without noticing.

- **Comments say why, never what.** A comment restating the line under it is
  noise that ages into a lie. A comment naming the clause a line exists to
  satisfy, or why the obvious simpler thing is wrong here, earns its place.

- **Use the feature file's words for the things it names.** If it says
  `available`, do not write `remaining`. A synonym is where a misunderstanding
  hides without ever looking like one.

### 2. Nothing asserted that you did not check

Every line of evidence you write is a claim someone downstream will rely on
without re-deriving it, so the second ask constrains the first: **the notes must
not contain a statement you have not actually run.**

- **A prediction written in the past tense is the failure mode.** "Rejects a
  closed tenant", written while you were implementing it and never run, reads
  exactly like the same sentence written after a passing run. Nobody downstream
  can tell those apart. You can. Mark them.

- **Label anything you reasoned rather than executed.** "I believe", "I did not
  run this" — these cost you nothing and are the only thing that keeps the rest
  of the document worth reading.

- **A thing you could not check is a result.** Write it down. An unmeasured
  claim recorded as unmeasured can be checked later; recorded as fact it will
  never be questioned again.

- **Do not describe intent as outcome.** "Ids are never reused" is an
  intention. "Ids are never reused; I reserved, released, and reserved again and
  got `r1`, then `r3`" is an outcome. The first sentence is true of almost every
  program that gets this wrong.

### The two asks pull against each other. How to resolve it

Thorough evidence **adds claims**: every clause accounted for, every edge
recorded, every ambiguity written out. "Assert nothing you did not check", read
mechanically, deletes most of them, because checking every claim costs more time
than you have.

Neither ask overrides the other. The rule that resolves them:

> **Fewer claims, each one carrying the input that produced it. No claim that
> exists because a claim seemed due.**

A short account where every sentence names what was run beats a long one where
half the sentences are confident and unattributed. If, after that, your account
looks thinner than the feature deserves, record that as a decision you made and
leave it standing. A gap you write down is worth more than a gap papered over
with a sentence that reads well.

### Two things this is not asking for

**This is not asking you to make any check pass.** Nothing here is scored by a
tool, there is no threshold, and there is no report to turn green. If you find
yourself writing a sentence because it would look complete rather than because
it is true, stop. The cheapest way to make an account look thorough is to
describe what the program is supposed to do, and the result does not look like a
mistake to anyone reading it afterwards.

**And more words are never, on their own, better evidence.** A count of
anything — sentences, cases tried, paragraphs of notes — goes up when you add
something, and the count cannot tell you whether what you added carries
information. So whenever you add a sentence to the notes, do one of two things
explicitly:

- name the input you ran that makes it true; or
- say plainly that you did not run one, and why you are writing it anyway.

"It follows from the code" is the weakest form of the first one, because the
code is what you are producing evidence about.

<!-- PA-01-SLOT:END -->

---

## Section 2 — the feature

Implement the feature specified in `examples/validation/ab/FEATURE.md`, in
Python, in the working directory you have been given.

Read the feature file in full first. It is the whole requirement. Section 1
tells you what you must show; the feature file tells you what it must do. Where
they appear to conflict, the feature file wins on **behavior** and Section 1
wins on **what you must show** — and say in `NOTES.md` that they conflicted,
because a prompt whose two halves fight each other is a finding about the
prompt.

## Section 3 — what to deliver

1. Working Python code implementing every command and query in the feature.
2. `examples/validation/ab/tests/test_behavior.py` passing unchanged against
   your implementation. **Do not edit that file.** It is the shared behavioral
   contract; a change to it is a change to the requirement.
3. Whatever tests of your own you think the code needs.
4. A short `NOTES.md` in your working directory saying what you built, what you
   decided, and anything you were unsure about.

## Section 4 — how to run the shared suite

Your implementation must expose the class as `QuotaLedger` and be importable
from a module your `NOTES.md` names. Point the shared suite at it with:

```bash
QUOTA_LEDGER_IMPL=<your.module.path> \
  uv run --with pytest python -m pytest examples/validation/ab/tests/test_behavior.py -q
```

## Section 5 — ground rules

- Use the standard library. Do not add dependencies.
- Do not change `FEATURE.md` or the shared suite.
- If the feature specification is ambiguous or self-contradictory, say so in
  `NOTES.md` and pick an interpretation. Do not invent requirements to resolve
  it, and do not implement both.
- Finish. A partial implementation with an elegant fragment is worth less here
  than a complete one, because the thing after this reads the whole surface.

## Section 6 — files you must not open

These would tell you what is being measured, and an implementer who knows the
answer key is not producing evidence about anything:

- `examples/validation/ab/seeded_faults.toml`
- `examples/validation/ab/check_catalogue.py`
- `examples/validation/ab/reference/`
- `examples/validation/ab/reference_ports/`
- `examples/validation/ab/arm_a/`
- `examples/validation/ab/arm_b/`
- `examples/validation/PREDICTIONS-HP.md`
- `examples/validation/PREDICTIONS-PA.md`
- anything under `specs/results/scorecards/` or
  `specs/.history/*/closed-snapshot/results/scorecards/`

If you open one by accident, say so in `NOTES.md`. That disclosure costs you
nothing and is the only thing that keeps the round interpretable; concealing it
voids the arm.

## Section 7 — what you will not be told

You are one arm of a multi-arm comparison. You are not being told what the other
arms are, what is being compared, or on what dimensions, because knowing would
change what you write. Report what you built, not what you think is wanted.
