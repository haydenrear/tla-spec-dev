# Regression → architecture — sub-agent prompt

**Dispatch the "The ask" block below verbatim**, with the project's attribution
records and the current self-improvement matrix pasted underneath. Everything
outside that block is for the caller.

It is **a prompt, not a check.** It refuses nothing, gates nothing, blocks no
promotion, and no tool reads it or its output. Doctrine:
`references/bug_attribution.md`; the accumulating output is
`examples/validation/agent_rounds/SELF-IMPROVEMENT-MATRIX.md`.

## Why this is a prompt and will stay one

A tool that computed the influence graph would parse findings, infer areas, and
join them across epics — three inference steps, each a place to put a bug into
the instrument used to find bugs. **The cost of a wrong row is higher than the
cost of writing it by hand.** If a tool is built later it goes in a separate
library and this prompt is its specification.

**And the measured precedent:** every mechanical gate this repository shipped was
defeated cheaply and none caught a bug in a subject program. The prompt that
replaced them produced structure and *"the structure caught nothing — again."*
**Asking is on trial here too.** A run of this prompt that produces nothing is a
result and is published as one.

## What to paste

Every CATCH, REACH, BLIND and PRICE record the project holds, **including the
`UNDECIDED` rows** — they are the input to step 4 and stripping them is the
easiest way to make this prompt lie. Then the current matrix.

---

## The ask

> Below are this project's records of where its defects came from, and the
> self-improvement matrix built from earlier rounds. Your job is to extend the
> matrix and then say what its shape implies about the architecture.
>
> **1. Anchor each new regression to a TLA+ action.** For each one: what caught
> it (`automated` / `hand` / `reading`), **which action in the model it happened
> inside** — `<Module>.<Action>` from `specs/program_model/` — and whether an
> assertion now pins it. A regression found by hand and pinned by an assertion is
> the full arc; say which arcs are incomplete and where they stopped.
>
> **If a regression does not fit any declared action, anchor it `UNMODELED` and
> say what it sits beneath.** Do not stretch an action to cover it. The size of
> `UNMODELED` is a measurement of how much of the real bug surface the semantic
> model does not reach, and stretching destroys exactly that number.
>
> **2. Update the matrix, per anchor:** escaped to hand, pinned, still unpinned,
> and the finding IDs. **Append and amend; never silently rewrite a row.** An
> action with no new regressions gets no row — absence of evidence is absence,
> not zero.
>
> **3. Read the `escaped to hand` column.** It is the only column that says an
> automated instrument was blind. Which actions keep appearing in it across
> rounds, not just this one? **An action that escapes once is noise. An action
> that escapes in three rounds is telling you something about its shape.**
>
> **3a. Say what is WORKING.** Which actions have closed arcs? Which fixes were
> later measured as working? **A matrix that only records problems will
> recommend churn**, and an action that has stopped producing escapes is the
> result the whole programme is for.
>
> **4. Say what you could not see, before you suggest anything.** How many
> records carry no attribution? How many areas have no denominator — that is, you
> know the escapes but not how many times the area was exercised? **An area with
> one escape in two invocations and one with one escape in a hundred look
> identical in this matrix.** If the record is too thin to support a conclusion,
> say so and stop at step 4.
>
> **5. For the action with the most repeated escapes — is it too complex, and
> is it time to refactor it?** Not a check, not a lint, not more tests. **What
> about the SHAPE of that action makes bugs there hard to catch automatically?**
> Shapes worth naming: a rule enforced on one path and not the identical path
> beside it; a seam where two mechanisms meet and neither owns the boundary; a
> green that passes because it could not look; an action carrying bookkeeping
> that has nothing to do with what it means.
>
> **Because the anchor is the model, the refactor is a MODEL refactor.** Say
> what the action would become in the TLA+, and therefore which rows of the
> matrix would be carried and which dropped.
>
> **6. Price it forward and do not choose it.** State what the change would
> cost — surfaces touched, roughly how much moves, what behaviour changes, and
> what would have to be true for it to be a bad trade. **This is a prediction
> made before anyone tries it, not a measurement that a past change paid off.**
> Describe the option; the owner decides. An answer phrased as an instruction is
> the wrong answer.
>
> **What not to do.** Do not propose adding a check, gate, lint or static
> analyzer — that route is measured and closed here. Do not answer "write more
> tests" for an area that escapes; if the instruments were blind, more of them
> are blind too. Do not fill an empty field with an inference: an absent record
> is an absent record, and saying so is the useful answer.

---

## Reading the output

Score it against four things before acting on any of it:

1. **Did it stop at step 4 when it should have?** A confident suggestion off a
   thin record has certified an absence it never observed.
2. **Did it choose the boundary?** It may describe and price. `architecture_advice.md` §6.
3. **Is anything gating on it?** Nothing may refuse on this output. §5.
4. **Did it propose a checker?** If so it ignored the one instruction with a
   measured reason behind it, and that is a finding about the prompt.

**Then record the suggestion in the matrix with its declared price**, `OPEN`
until the owner decides. A suggestion refused with a reason is consumption; a
suggestion nobody read is not.
