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

> **UNFILLED — HP-02 owns this section.**
>
> HP-01 declares this arm and the envelope around it; it does **not** write the
> treatment. Writing both the instrument and the experiment that judges it is
> how an epic ends up measuring its own opinion.
>
> HP-02 replaces everything between the two slot markers with the hexagonal +
> minimize-complexity ask, per its plan entry. Per that entry, the content must:
>
> - ask for **ports and adapters explicitly** — a domain that does not import
>   its I/O, driven ports behind interfaces, adapters swappable for fakes;
> - ask for the **simplest design that retains the behaviors**, feeding the
>   shipped complexity descriptor in **as guidance**, never as a threshold;
> - **not** instruct the agent to make any check pass. "Make the coherence
>   check clean" was measured, in round 2, to be a standing instruction to
>   duplicate across component boundaries;
> - **not** promise that a metric improving means the design improved. MF-020:
>   a metric can improve because an edge was deleted.
>
> HP-02 should also record, in its own ticket, that a longer and more specific
> prompt is a **declared confound** of this round — see confound 1 in
> `examples/validation/PREDICTIONS-HP.md`. This round cannot separate "the
> hexagonal guidance helped" from "a longer, more specific ask helped." That is
> a limit to state, not a defect to hide.
>
> **This arm must not be dispatched while this slot is unfilled.**
> `check_catalogue.py --arms` reports the slot's state; it reports, it does not
> refuse, because nothing in this epic gates.

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
