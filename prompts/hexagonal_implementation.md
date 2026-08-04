# Hexagonal Implementation — sub-agent prompt (HP-02)

**Dispatch the "The ask" block below verbatim as the prompt for a sub-agent**,
alongside whatever specifies the feature. Everything outside that block is for
the caller: what this prompt is, what it deliberately does not say, and how it
is meant to be used.

It is **a prompt, not a check.** It refuses nothing, gates nothing, blocks no
promotion, and no tool in this repository reads it. The epic that produced it
(`hexagonal-prompting`) exists to test whether asking is enough — the
predecessor shipped four static architecture checks, measured them twice, and
bug detection did not move by a single cell while every check was defeated by a
few lines of re-export. See `references/hexagonal_prompting.md` for what this
prompt asks for, why, and what it deliberately omits.

Companions that already ship: `prompts/implementation_brief.md` renders a
*measured* constrained ask from an architecture descriptor (use it when you have
a model and want the constraints to be derivable); `prompts/aspect_decomposition.md`
decomposes a model into aspects. This prompt is the one for the case where you
have a feature to build and want the design asked for rather than derived.

## Optional, and only when a model exists

If the work has a TLA+ model, take a descriptor before and after and read it per
`references/complexity_intuition.md`:

```bash
python3 scripts/tla_spec_dev.py --spec-root specs analyze complexity <tla> <cfg>
```

**This is input to a judgement, never a verdict, and never a target.** The
scanner is advisory: it exits 0 on a bad descriptor and nothing it prints blocks
anything. Do not hand the numbers to the implementing agent as thresholds to
beat — §2 of the ask below is the descriptor's *reading rules* restated in code
terms precisely so that an agent with no model can apply them, and so that
nobody is asked to optimize a number.

The descriptor measures a **model**, not a Python tree. If the artifact under
construction has no model, there is no before-and-after to take, and saying so
is better than substituting a proxy metric.

---

## The ask

<!-- HEXAGONAL-ASK:BEGIN -->

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

<!-- HEXAGONAL-ASK:END -->

---

## What this prompt deliberately does not say

Recorded here so a later reader can tell an omission from an oversight. The
reasoning is in `references/hexagonal_prompting.md`.

- **No threshold, score, count or budget.** Not one number appears in the ask.
- **No instruction to satisfy any tool.** No "make the coherence check clean",
  no "keep the descriptor under", no report to turn green.
- **No named architecture beyond the two asks.** No prescribed directory layout,
  no framework, no CQRS/repository/service vocabulary. The ask constrains the
  *coupling* and leaves the shape free.
- **No ask for honesty, blind spots, refusals, or limits.** That is a separate
  dimension of this repository's scorecard, it is deliberately *not* varied by
  this prompt, and adding it here would quietly change what a comparison against
  an ordinary ask is measuring.
- **No claim that this works.** Whether asking produces modularity in fact is
  the open question the `hexagonal-prompting` epic exists to answer, and HP-06
  decides it. Until then this prompt is a hypothesis with a stated design, not a
  result.

## Validation status of this prompt — read before trusting it

**One local pilot at HP-02**, n = 1, not blind, not the experiment: evidence
under `specs/tickets/HP-02/results/`. It is a smoke test that the ask is
followable and that it does not cost bug detection, not a measurement of whether
the ask helps. The measurement is HP-06's A/B with two blind judges, and this
line should be replaced with its result when it exists.
