# ARM B — the treatment prompt

**Dispatch this file verbatim, as the entire prompt, to one fresh agent.**

This is the **treatment arm** of the hexagonal-prompting A/B, and it is the
instrument the epic exists to test: architecture guidance delivered as a
**prompt** rather than as a schema, a check, or a gate.

This file is a complete, standalone prompt. It is **not arm A with a paragraph
switched on**. The two arms were written independently against the same feature
file, and they are declared as two files precisely so that a reader of the
record can see which instrument produced which number.

---

## Section 1 — the architecture ask

<!-- HP-02-SLOT:BEGIN -->

You are being asked for two things at once. They are in tension, and the tension
is deliberate.

1. **Ports and adapters, in fact.**
2. **The simplest design that keeps every behavior.**

### 1. Ports and adapters, in fact

*In fact* means the structure holds when the program runs, not in the file
names. A package called `adapters/` whose contents the domain constructs for
itself is not a port; it is a folder.

- **The domain is the rules.** It holds no file handle, no path, no clock, no
  environment, no network, no global. What it does is a function of what it was
  given and what it was told.

- **Every outside thing the domain needs is a driven port**: a small interface
  the *domain* declares, in the *domain's* vocabulary, named for the need rather
  than for the technology that satisfies it. Two or three methods; a port with
  ten is a module boundary that got mislabelled.

- **The domain module does not import the modules that implement its ports.**
  Not "does not use" — does not import. The concrete adapter is built somewhere
  else and handed in. That somewhere else is one small composition point (a
  factory, a constructor, the entry point). It is allowed to know about
  everything, and it is the only thing that is.

- **Write a fake for each driven port, and run the same cases against both.**
  Not a mock that records calls — a working in-memory implementation of the same
  interface. Then take the cases that exercise behavior through that port and
  run the *identical* case list against the real adapter and against the fake.
  If a case can only be written for one of them, the port is leaking. **Each
  case asserts an expected value, not merely that the two agree** — two wirings
  of the same domain agree with each other even when the domain is wrong, so a
  test that only compares them can never fail for a reason you care about.

- **State the swap in one sentence**, in your notes: "replace *this* adapter
  with *that* one and no domain file changes." If you cannot write that sentence
  about a concrete alternative, you have a layer, not a port.

- **Do not invent ports for things that are not outside.** A port in front of
  pure computation is indirection with nothing behind it to swap. One port per
  real outside dependency; nothing else indirected.

### 2. The simplest design that keeps every behavior

Simple here does not mean small, or clever, or few files. It means **the
complexity is proportional to the behavior the program actually has.**

The test is one question: **which distinctions does the behavior actually
make?** If nothing — no rule, no branch, no observable result, no test — can
tell two states apart, the difference between them is representation, not
behavior.

Things that are usually accidental, worth hunting for in your own design:

- **State nothing reads.** A field every operation writes and nothing ever
  branches on, asserts, or returns. Stated intent is not a reader: name a
  concrete one, or treat it as bookkeeping.
- **State written from everywhere.** If most operations write the same piece of
  state, it couples every operation to every other. Prefer one writer per piece
  of state where the behavior allows it.
- **An operation that touches most of the state.** Usually several jobs in one
  step.
- **A representation wider than the distinctions.** If the program behaves
  differently at "none", "some" and "all", it has three cases, however the value
  happens to be stored.

These are places to look, not rules to satisfy. A small program with an
irreducible core will look dense by every one of them and be right.

### The two asks pull against each other. How to resolve it

Ports and adapters **add parts**: an interface, a fake, a composition point, an
indirection at every call. "Minimize complexity", read mechanically, deletes all
of them.

Neither ask overrides the other. The rule that resolves them:

> **One port per real outside dependency. Nothing else indirected. No layer that
> exists because a layer seemed due.**

If the design still looks like more parts than the feature deserves after that,
record it as a decision you made and leave it standing. A decision you write
down is worth more than a boundary collapsed to make a count go down.

### Two things this is not asking for

**This is not asking you to make any check pass.** Nothing here is scored by a
tool, there is no threshold, and there is no report to turn green. If you find
yourself doing something because it would clear a check, stop. That instruction
has been *measured* to produce duplication across the very boundaries it was
supposed to protect — the cheapest way to make a structural report clean is to
copy the shared thing into both sides of the boundary, and the diff does not
look like a mistake.

**And a smaller number is never, on its own, a better design.** A count of
anything — variables, branches, lines, files — goes down when you delete
something, and the count cannot tell you whether what you deleted was carrying
behavior. So whenever you remove or collapse something, do one of two things
explicitly:

- point at the code or the test that still holds the behavior it carried; or
- say plainly that the behavior is gone, and why you think that is correct.

"The tests still pass" is the weakest possible form of the first one, because
the tests were written against the design you are changing.

<!-- HP-02-SLOT:END -->

---

## Section 2 — the feature

Implement the feature specified in `examples/validation/ab/FEATURE.md`, in
Python, in the working directory you have been given.

Read the feature file in full first. It is the whole requirement. Section 1
tells you how to build it; the feature file tells you what it must do. Where
they appear to conflict, the feature file wins on **behavior** and Section 1
wins on **structure** — and say in `NOTES.md` that they conflicted, because a
prompt whose two halves fight each other is a finding about the prompt.

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
- `examples/validation/ab/arm_a/`
- `examples/validation/PREDICTIONS-HP.md`
- anything under `specs/results/scorecards/` or
  `specs/.history/*/closed-snapshot/results/scorecards/`

If you open one by accident, say so in `NOTES.md`. That disclosure costs you
nothing and is the only thing that keeps the round interpretable; concealing it
voids the arm.

## Section 7 — what you will not be told

You are one arm of a two-arm comparison. You are not being told what the other
arm is, what is being compared, or on what dimensions, because knowing would
change what you write. Report what you built, not what you think is wanted.
