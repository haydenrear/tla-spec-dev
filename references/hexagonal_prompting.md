# Hexagonal Prompting: The Ask, The Reasons, And The Omissions

`prompts/hexagonal_implementation.md` is a **prompt**. It asks a coding agent
for ports and adapters in fact, and for the simplest design that keeps every
behavior. Nothing in this repository reads it, nothing enforces it, and it
refuses nothing. This page says what it asks for, why each clause is there, and
— at more length, because that is the part a later reader cannot reconstruct —
what it deliberately does **not** say.

The same ask is inlined as Section 1 of
`examples/validation/ab/arm_b/PROMPT.md`, the treatment arm of the
`hexagonal-prompting` A/B. See "Two copies, on purpose" below.

## Why a prompt and not a check

The predecessor epic shipped four static architecture levers and measured them
twice. **Bug detection did not move by a single cell** — 4 of 6, 6 of 6, 0 of 3
guard relaxation, 0 of 3 ordering, identical before and after seven repair
tickets. Every check was defeated cheaply: six lines of YAML in round 1, a
41-line re-export file in round 2, both with every declaration digest unchanged.

The epic plan's `no_new_gates_rule` states the owner direction that followed:
the hoops already built are not smart enough to provide value, and agents spend
real time jumping through them. Architecture guidance moves into the ask.

So the hypothesis under test, stated so it can fail: **an agent working from the
diagram — far enough from the code that it is not defending existing structure —
will produce a modular, testable design if simply asked for one, and will
preserve behavior while reducing complexity if told that is the goal.**

If that is false, the prompt is decoration, and the epic is built to say so in
one round rather than after another epic of analyzer work.

## What the prompt asks for

Six clauses on the architecture side, four on the complexity side, one rule that
resolves the conflict between them, and two prohibitions.

### The architecture clauses, and what each one is aimed at

| Clause | Why it is worded that way |
|---|---|
| the domain holds no handle, path, clock, environment, network or global | This is the operational form of "the domain does not import its I/O". Stated as *what the domain holds*, not *what it imports*, because import topology is not modularity — round 2 proved a codebase can pass every import check with its coupling entirely intact. |
| a driven port is a small interface the **domain** declares, in the **domain's** vocabulary, named for the need not the technology | Ownership direction is the whole content of dependency inversion. A `FileWriter` interface declared next to the file writer is the same coupling with an extra file. |
| "two or three methods; a port with ten is a module boundary that got mislabelled" | The failure mode where a port becomes a second copy of the domain's whole surface. |
| **the domain module does not import the modules that implement its ports** — not "does not use", does not import | The negative form is what makes it checkable by a reader in ten seconds, and it is the one clause here that is literally verifiable by looking. |
| write a **fake** for each driven port, and run the *identical* case list against the real adapter and the fake | This is the clause that makes the boundary load-bearing rather than decorative. A port with one implementation has never been swapped and nobody knows whether it can be. "Identical case list" is the operative word: two test files that happen to be about the same port prove nothing. |
| **state the swap in one sentence** | A concrete named alternative is the cheapest available falsifier. "This could be swapped" is a claim; "replace `FileLedger` with `SqliteLedger` and no domain file changes" is a claim with a subject. |
| **do not invent ports for things that are not outside** | The counterweight. Without it, "make it hexagonal" reliably produces a port per noun. |

### The complexity clauses

These are `references/complexity_intuition.md` restated in code terms. That
document is written about a **TLA+ descriptor**; the prompt's audience may have
no model at all, so the *reading rules* travel and the numbers do not:

| Descriptor fact | The prompt's form |
|---|---|
| "which distinctions does the behavior actually make?" | kept verbatim as the single test |
| variables no configured invariant reads | **state nothing reads**, with the write-only-state test's insistence that stated intent is not a reader |
| dense rows / god-state signature | **state written from everywhere**, plus prefer one writer |
| dense columns | **an operation that touches most of the state** |
| domains wider than the distinctions the behavior makes | **a representation wider than the distinctions** |
| a bad descriptor is a finding, not a failure; an irreducible core looks dense | "places to look, not rules to satisfy" and the closing sentence about the irreducible core |

### The rule that resolves the two asks

> One port per real outside dependency. Nothing else indirected. No layer that
> exists because a layer seemed due.

The two asks genuinely conflict, and pretending otherwise would leave the agent
to resolve it silently. Ports **add parts**. HP-01 sealed a prediction (N01)
that this prompt will not separate complexity in its own favour and may separate
against it, for exactly that reason. The prompt says the conflict out loud and
gives one rule instead of a precedence order, because a precedence order would
be read as "when in doubt, add a port" or "when in doubt, collapse it", and both
are wrong.

## What the prompt must not do, both learned by measurement

### It does not tell the agent to make any check pass

Round 2 measured that "make the coherence check clean" is a standing instruction
to **duplicate across component boundaries**. The agent cleared two divergences
by copying a format string into the other component, because the tool's only
accepted remedies were: duplicate it, push the dependency into the caller, or
edit the map. Nothing in the resulting report told the reviewer that the diff had
added duplication.

So the prompt contains no threshold, no score, no budget, no count, and no
report to turn green — **not one number appears in the ask** — and it names the
failure explicitly so an agent that meets such an instruction elsewhere
recognizes it.

This is also why HP-02 ships no checker. A ticket that finds itself adding a rule
that refuses something has left this epic's scope (`no_new_gates_rule`), and a
"is arm B's Section 1 still in sync with the canonical prompt?" test would be
exactly that rule.

### It does not imply that a metric improving means the design improved

MF-020: **a metric can improve because an edge was deleted.** The predecessor's
best complexity result was withheld from a top score by both blind judges for
precisely this — a reduction that deleted two model variables and two keys from
a public dict, with no check that could catch an external reader, and a prior run
on the identical model declined the identical deletion.

The prompt's form of that lesson is a duty attached to every removal: point at
the code or test that still holds the behavior, **or** say plainly that the
behavior is gone. And it downgrades the usual answer in advance — "the tests
still pass" is the weakest form of the first branch, because the tests were
written against the design being changed.

## What the prompt deliberately does not say

### No honesty, blind-spot, refusal or limits ask

The scorecard's D5 (`references/eval_scorecard.md`) measures exactly that, and
HP-01 sealed **N03**: D5 will not separate between arms, on the stated ground
that *neither prompt says anything about refusing, about naming blind spots, or
about `unobservable` beating a false clean*. N03 is the round's **blindness
check** — if D5 separates, the first explanation HP-06 must consider is that the
judges worked out which arm they were reading.

Adding an honesty ask here would have falsified N03's premise and destroyed that
check. So the prompt has none, and this is the omission most likely to be
mistaken for an oversight.

**Residual risk, stated rather than hidden.** Two clauses in the ask still ask
the agent to write something down: "state the swap in one sentence" and "record
it as a decision you made". Both are behavior/design notes and both fall inside
the *shared* envelope's existing instruction to say "what you decided" — arm A
carries that instruction verbatim. But they are not zero, and if D5 does
separate, this prompt is a candidate cause that HP-06 should weigh alongside
judge unblinding. PREDICTIONS-HP.md is sealed and was not amended to say so;
this paragraph is where it is recorded instead.

### No scorecard, no dimension, no judge, no epic

The ask never mentions the card, the dimensions, the arms, or what is being
compared. Arm B's Section 6 forbids the implementer from opening the scorecards
for the same reason: an implementer who knows the answer key is not producing
evidence about anything.

The consequence is worth being explicit about, because it looks like an
oversight in the other direction: the ask **does** request a fake plus an
identical case list run against both implementations, and that is also what the
card's D3 anchor 4 requires. That is not teaching to the test. The card was
written to reward a real engineering artifact, and the epic's entire hypothesis
is that asking for the artifact produces it. What would be teaching to the test
is naming the anchor, and the prompt does not.

### No prescribed layout, framework, or pattern vocabulary

No directory structure, no CQRS / repository / service / hexagon diagram, no
naming convention. The ask constrains **coupling** and leaves shape free, so that
a judge reading the result is reading a design decision rather than a template
the agent filled in.

### No complexity descriptor numbers in the arm prompt

`prompts/hexagonal_implementation.md` carries an optional step for taking an
`analyze complexity` descriptor before and after — but only when a model exists,
and marked as input to a judgement rather than a target.

Arm B gets no such step, and could not use one:

- the shipped scanner measures a **TLA+ model**, and both arms produce **Python**
  with no model of their own;
- the A/B holds **one model for both arms** on purpose
  (`examples/validation/ab/README.md`, "What is held constant") — if each arm
  had its own, a difference between arms could be a difference between their
  models and nobody could tell which produced it;
- handing arm B the model and not arm A would be a far larger confound than the
  one this round already carries.

This has a consequence for HP-06 that is filed as **HP-02-DF-01**: the
`GOAL-simpler-same-behavior` harness says "`analyze complexity` before and after
on the same artifact", and there is no artifact in this A/B that the shipped
scanner can read. HP-06 needs a stated substitute or an explicit `unmeasured` on
the mechanical half of D2.

## Two copies, on purpose

The ask exists twice, near-identically:

| Copy | Why it is there |
|---|---|
| `prompts/hexagonal_implementation.md`, between `HEXAGONAL-ASK:BEGIN/END` | **canonical.** The shipped, reusable prompt, with the caller's framing and the model-optional descriptor step. |
| `examples/validation/ab/arm_b/PROMPT.md` Section 1 | the A/B treatment. HP-01 requires each arm to be a complete standalone prompt dispatched verbatim — an arm that says "go read `prompts/…`" is an arm whose treatment depends on what a fresh agent chooses to open. |

The two differ only in the canonical copy's caller framing and its
model-optional step; the ask itself is the same text.

**And yes, this is duplication across a boundary, in a document whose central
lesson is that a check which rewards duplication gets it.** The difference is
that this copy is declared, in a table, with the canonical side named — and that
no tool asked for it and no tool checks it. A drift between the two is a defect a
reader can find in one diff; a *checker* for it would be the gate this epic
exists not to ship. If the drift ever matters, the fix is to delete a copy, not
to add an enforcer.

## Declared confounds this prompt adds to the round

Recorded here because `examples/validation/PREDICTIONS-HP.md` is sealed and
HP-02 may not amend it. Confound 1 in that file already states the general
problem; these are its measured particulars.

1. **Length and specificity are not controlled, and the gap is large.**
   Measured by `check_catalogue.py --arms` at the commit that filled the slot:

   ```
   arm_a/PROMPT.md   73 lines
   arm_b/PROMPT.md  194 lines
   shared verbatim:  38 lines      unique to A: 16      unique to B: 105
   ```

   Arm B's unique content is **6.6x** arm A's. If arm B wins on any dimension,
   this round cannot distinguish "hexagonal guidance helped" from "a longer,
   more specific ask helped". A third arm — an ask of arm B's length about
   something other than architecture — would separate them, and this epic does
   not run one.

2. **The ask names an artifact the card rewards.** Discussed above. Stated as a
   limit on the strength of any D3 = 4, not as a reason to discount it.

3. **The complexity half of D2 has no mechanical instrument on this fixture.**
   HP-02-DF-01. Judged D2 is unaffected; the descriptor half is not measurable
   on a Python tree.

## Validation status

**One local pilot at HP-02.** n = 1, one feature, not blind, both arms run by the
same operator on the same day, scored by nobody. Full evidence:
`specs/tickets/HP-02/results/goal-signal.md`.

It is a smoke test with two questions: *is the ask followable at all*, and *does
it cost bug detection* (HP-02's declared `guard` on `GOAL-catch-bugs`: a prompt
that produces prettier code whose adapters catch less has failed). It is not
evidence that the prompt helps. **Two of its three signals came back negative.**

| | result |
|---|---|
| structure | The ask is followable and was followed. Arm B's domain imports `dataclasses`, `typing` and its own `ports` module and nothing else; arm A's domain imports `pathlib` and opens the file itself. Arm B produced a `Protocol` port, a real adapter, a working fake, one composition point, and a named swap. Arm A produced none of those. |
| complexity | **Wrong way.** The declared instrument could not run at all (HP-02-DF-01). On parts — the only reading available without one — arm B is larger: 5 production files / 274 lines against 1 / 120. It did make two real representation reductions (no stored `available`, no in-memory ledger mirror), so it has fewer pieces of state that can drift and more modules. This reproduces the sealed N01. |
| bug detection | **Wrong way by one cell.** Shared suite: 10/10 on both arms, flat. Each arm's *own* tests: A 4/10, B 3/10 — and arm B wrote 3.6× the test code. The one arm B lost is the zero-amount guard. |

### The pilot found a hole in this prompt, and it is fixed but unmeasured

Arm B's real-vs-fake test asserted `scenario(fake) == scenario(real)` — two
wirings of the **same domain**, so every domain-logic fault moves both sides
identically and the test cannot fail for any fault in the rules. The artifact
this prompt asks for, and that D3 anchor 4 is written about, was **by
construction blind** to the faults D1 is written about. The agent followed the
instruction exactly as written; the instruction was underspecified.

One sentence was added to both copies of the ask afterwards ("Each case asserts
an expected value, not merely that the two agree…"). **The pilot measured the
text before that sentence, and was deliberately not re-run** — re-running a
signal after changing the thing until a better number appears is the pattern the
workflow forbids. HP-06's A/B is the first measurement of the shipped text.

That sequence is also the honest answer to "does asking work": the first thing
running the ask produced was a demonstration that a prompt can request the shape
of a good test and get a test that asserts nothing.

**The measurement is HP-06** — the same feature, both arms, two judges blind to
arm and to each other, `file:line` for every score ≥ 2. Until it reports, this
prompt is a hypothesis with a stated design and a recorded pilot, and any
sentence claiming more than that about it is unsupported.
