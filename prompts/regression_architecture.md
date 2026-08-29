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
> **If a regression does not fit any declared action, anchor it
> `UNMODELED/<bin>`** — where `<bin>` is what it sits beneath, named. Do not
> stretch an action to cover it. The size of `UNMODELED` measures how much of the
> real bug surface the semantic model does not reach, and stretching destroys
> exactly that number.
>
> **Group by the bin; never pool.** Seven findings pooled reads as one gap. Seven
> in one bin is a gap with a shape; seven across five bins is a model that is
> thin everywhere. **The pooled count cannot tell those apart**, and they want
> different answers.
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
> **3b. Which actions can the test graph not drive?** For each action carrying
> escapes, say whether a **binding** exists for it — an entry naming an adapter,
> a projector and an assertion, so that TLC-derived cases can drive it and a node
> can go red. An action with escapes and **no binding** is the pair this step
> exists to find: **defects are arriving there and nothing is pointed at it.**
>
> This is REACH asked of the model instead of an invariant, so the same rule
> governs it — an empty unbound-list is a **claim** and must say how it
> enumerated, or it is `UNDECIDED`.
>
> **3c. Read the bins.** For each `UNMODELED/<bin>`, give its count, whether it
> grew this round, and its **disposition** — `MODELABLE`, `DEFERRED`,
> `RECORD-ONLY`, or `UNDECIDED` (`references/bug_attribution.md` §7c). A new bin
> is `UNDECIDED` until somebody classifies it; that is the correct entry, not a
> gap to fill with a guess.
>
> - **`DEFERRED` — name the blocker and re-read it.** A blocker is a **missing
>   capability**, stated concretely: *"no runner exists that can drive a
>   multi-skill plugin end to end."* *"Hard to test"* is not a blocker.
>   **If the capability now exists and the bin did not move, say so — that is a
>   finding about the record.**
> - **A growing `DEFERRED` bin is a PRICE on the missing capability.** Say what
>   deferring has cost so far, in findings. That is the evidence the capability
>   would be built on, and it is the whole reason deferral is written down rather
>   than waved at.
> - **Every bin keeps counting, whatever its disposition.** Nothing is moved into
>   a disposition in order to stop counting it.
>
> **4. Say what you could not see, before you suggest anything.** How many
> records carry no attribution? How many areas have no denominator — that is, you
> know the escapes but not how many times the area was exercised? **An area with
> one escape in two invocations and one with one escape in a hundred look
> identical in this matrix.** **And how many actions did you not check for a
> binding?** If the record is too thin to support a conclusion, say so and stop
> at step 4.
>
> **5. For the row with the most repeated escapes — the responses, and say
> which.** **The row may be a bin.** `UNMODELED/<bin>` competes with the actions
> on the same column, and if a bin is the worst row then the bin is what this
> step is about — a matrix whose worst row is the one row the loop cannot act on
> has a hole where its answer should be.
>
> **For an ACTION there are two responses. They point in opposite directions, and
> the value of this step is that you must pick one and say why the other is wrong
> here.**
>
> > **(a) REDUCE — the action is too complex.** What about the SHAPE of that
> > action makes bugs there hard to catch automatically? Shapes worth naming: a
> > rule enforced on one path and not the identical path beside it; a seam where
> > two mechanisms meet and neither owns the boundary; a green that passes
> > because it could not look; an action carrying bookkeeping that has nothing to
> > do with what it means. **This shrinks the model surface.**
> >
> > **(b) EXPAND — the model cannot see it.** The escapes arrive by hand because
> > **nothing at that location can go red**. Model the behaviour the defects are
> > landing in — as a new action, or as more of an existing one — and add the
> > binding that drives it. **This grows the model surface.**
>
> **Choose by what the record says, not by which is cheaper.** Repeated escapes
> at an action the graph *can* drive argue for **(a)**: the instrument is there
> and the shape is defeating it. Repeated escapes at an action with **no
> binding** argue for **(b)**: nothing has ever looked, and simplifying a place
> you cannot observe is guessing.
>
> **For a BIN there is a third response, and the two above do not apply** — there
> is no action to simplify and nothing to bind:
>
> > **(c) MODEL — no action exists at all.** Findings are accumulating at a place
> > the model does not describe. Say whether the bin is `MODELABLE` **now**, and
> > if so what action it would become and what it would mean. **This is the only
> > response that makes `UNMODELED` fall while the model's breadth rises**, which
> > is the healthy direction for both numbers at once.
> >
> > **If it is `DEFERRED`, (c) is still an answer: name the capability that is
> > missing and price it against what the bin has cost so far.** Deferral with a
> > named blocker and a running cost is a result. Deferral as a shrug is the
> > refusal-to-model degeneracy, and it is the one conservation cannot see —
> > §7b guards deleting from the model, §7c guards never adding to it.
> >
> > **If it is `RECORD-ONLY`, say so and say why it will not become an action —
> > then still answer (a) for it.** Inability to represent something in TLA+ does
> > not exempt it from *"is this area too complex?"*. `RECORD-ONLY` is a claim
> > about representation, never about relevance.
>
> **When a bin does become an action, conservation applies and does real work:**
> its findings re-anchor **out of** `UNMODELED/<bin>` and **into** the new action,
> and the totals match. That is what proves the extension absorbed the history
> instead of restarting the count.
>
> **If (b) is not cheap, say so — that is an answer, not a blocker.** Name what
> about the code makes it hard to drive. **That is a refactor proposed for
> OBSERVABILITY, and it is a different claim from a refactor for simplicity** —
> keep them distinct, because they compete.
>
> **Because the anchor is the model, either response is a MODEL change.** Say
> what the action would become in the TLA+, and therefore which rows of the
> matrix would be carried, dropped or split.
>
> **5a. If your proposal changes the model, show the arithmetic.** Findings are
> conserved — `references/bug_attribution.md` §7b. State `findings before` and
> `findings after` and where each affected finding re-anchors. **They must be
> equal.** A proposal that appears to reduce a count by removing the place the
> count lives has reduced nothing, and these two numbers make that visible
> without anyone having to suspect you of it.
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
>
> **Response (b) is not an exception to that, and the difference is not one of
> degree:**
>
> - **Duplication** is a second instrument where one already stands, or an
>   assertion written to catch **the specific defect that already happened**.
>   That is `MF-020` — a recogniser fitted to a known answer — and it is
>   forbidden here whatever it is called.
> - **A binding** drives an action against **the model's own expectations**, from
>   TLC-derived cases. It is derived from the specification, not from the
>   finding. At an action with no binding it duplicates nothing: it is the
>   **first** instrument at that location.
>
> **The test is whether you could have written it before the bug existed.** A
> binding, yes — the model already said what the action does. An assertion shaped
> around the failure you just read, no. **If you cannot tell which you are
> proposing, you are proposing the second one.**

---

## Reading the output

Score it against four things before acting on any of it:

1. **Did it stop at step 4 when it should have?** A confident suggestion off a
   thin record has certified an absence it never observed.
2. **Did it choose the boundary?** It may describe and price. `architecture_advice.md` §6.
3. **Is anything gating on it?** Nothing may refuse on this output. §5.
4. **Did it propose a checker?** If so it ignored the one instruction with a
   measured reason behind it, and that is a finding about the prompt.
5. **Did it pick a response and say why the other was wrong?** An output that
   describes both and commits to neither has not done step 5. An output that
   picked **(a)** for an action it never checked for a binding picked the
   shrinking response without establishing anything had ever looked — the one
   ordering this prompt exists to prevent.
6. **If the model moves, do the two totals match?** They are the only place a
   removed row could go missing, and checking them costs one addition.
7. **Did a bin get a disposition, or a dismissal?** `DEFERRED` without a named
   missing capability is a shrug wearing a token, and it is the refusal-to-model
   degeneracy. **A bin that stopped counting is the finding**, whatever the
   disposition says.

**Then record the suggestion in the matrix with its declared price**, `OPEN`
until the owner decides. A suggestion refused with a reason is consumption; a
suggestion nobody read is not.
