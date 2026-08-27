# Regression Architecture — sub-agent prompt (AT-03)

**Dispatch the "The ask" block below verbatim as the prompt for a sub-agent**,
with the project's CATCH, REACH, BLIND and PRICE records pasted underneath it.
Everything outside that block is for the caller.

It is **a prompt, not a check.** It refuses nothing, gates nothing, blocks no
promotion, and no tool in this repository reads it or its output. Doctrine:
`references/bug_attribution.md` for the four record kinds;
`references/architecture_advice.md` §5, §6 and §9 for the three constraints the
ask carries and why each one is there.

---

## Why this prompt exists

Six epics of static checking in this repository caught zero bugs in a subject
program, and the page that records why opens with the reason:

> Every mechanical gate this project shipped was defeated cheaply and none of
> them ever caught a bug.
> — `references/architecture_advice.md`

So the remaining question is whether **asking** works where checking did not.
This prompt is that question, pointed at one thing a check could never see: the
shape of the record's own blind spots.

## What this prompt does not say, and the precedent against it

**It does not say the architecture is wrong.** It has no opinion about the
program. It reads what the record says about where defects came from and where
nobody looked, and asks whether those two shapes suggest a change.

**And the honest precedent, which the caller should hold while reading any
output:** the epic that produced `prompts/hexagonal_implementation.md` measured
its own result as

> **THE PROMPT PRODUCED THE STRUCTURE AND THE STRUCTURE CAUGHT NOTHING — again**

**Asking has a track record here of producing shape without producing catches.**
A run of this prompt that produces nothing is a result and is published as one,
at the same prominence as a run that produces something.

## Do not fit it to a known answer

`MF-020`: a recogniser written while looking at the answer will find the answer.
If you edit this prompt after reading which area currently leads the CATCH
counts, you have fitted it. **State which you did.** This file was written
before any REACH or BLIND record existed in this repository, so the first run is
against a corpus whose answer was unknown when the ask was written.

## What to paste underneath

Every record described in `references/bug_attribution.md` §2, in whatever form
the record actually holds them. **Paste the UNDECIDED rows too** — they are the
input to the third constraint, and stripping them is the single easiest way to
make this prompt lie.

---

## The ask

> Below are this project's records of where its defects came from and where
> nobody looked. There are four kinds and they run in different directions.
>
> - **CATCH** — a regression happened. What caught it (`channel`, whose class is
>   `automated`, `hand` or `reading`), what area it was in, and what assertion
>   pins it now.
> - **REACH** — an invariant, the surfaces it **is** enforced on, and the
>   surfaces it **is not**.
> - **BLIND** — a case that passes, and the class of defect it could **never**
>   have caught.
> - **PRICE** — a change that was proposed, what it was priced at before anyone
>   tried it, and what it actually cost.
>
> Answer in this order.
>
> **1. Where do the escapes concentrate?** Group the CATCH records by area. For
> each area report how many were caught by something `automated` and how many
> escaped to a `hand` or to `reading`. Name the areas where the escapes
> concentrate. Do not compute a rate you cannot defend: if an area has three
> records, say three, not 67%.
>
> **2. Which invariants are enforced unevenly?** From the REACH records, name
> every invariant with a non-empty `unenforced_on`. Then, separately, name every
> invariant whose `unenforced_on` is **empty** and check its `enumerated_by`: an
> empty list with a weak enumeration is a claim of full coverage that nobody
> established, and it belongs in your answer next to the genuinely uneven ones.
>
> **3. Which greens are blind?** From the BLIND records, name the passing cases
> whose `could_not_have_caught` overlaps an area from step 1. **A green sitting
> on top of an area that keeps escaping to hand is the strongest single signal in
> this record**, because it means the instrument is present, reporting success,
> and not looking.
>
> **4. Say what you could not see — before you propose anything.** State what
> fraction of the records carry an attribution at all, how many REACH rows say
> `UNDECIDED`, and how many BLIND rows are absent for cases you can see passing.
> **If the record is too thin to support a conclusion, say that and stop.**
> Reporting a clean architecture from a partial record certifies an absence you
> never observed, and that is a worse outcome than returning nothing.
>
> **5. For the worst area only — one refactor.** Is there a change that **removes
> the class** rather than catching it? Describe the change and the boundary it
> would move. **Do not choose it.** You are describing an option and its
> consequences for someone else to decide; an answer phrased as an instruction
> is the wrong answer.
>
> **6. Price it, forward.** Before anyone tries it, state what you expect it to
> cost: the surfaces it touches, roughly how much moves, what behaviour changes,
> and what would have to be true for it to be a bad trade. **This is a
> prediction, not a measurement.** Do not describe what a past refactor already
> bought. If you cannot price it, say so — an unpriced proposal is a preference.
>
> **What you must not do.** Do not propose adding a check, a gate or a lint. Do
> not recommend more tests as the primary answer to an area that escapes — that
> is the standing instruction to duplicate. Do not rank areas you did not read
> records for. Do not fill an empty field with an inference; an absent record is
> an absent record and saying so is the useful answer.

---

## Reading the output

**Score it against the three constraints before acting on any of it:**

1. **§6 — did it choose the boundary?** It may describe a good boundary and price
   it. An output that says *"do this"* has taken a decision that is not the
   prompt's to take, and the finding is about the prompt, not the architecture.
2. **§5 — is anything gating on it?** Nothing may refuse on this output. If a
   proposal arrives as *"make the check clean"*, it is the duplication
   instruction and should be refused with that reason recorded.
3. **§9 — did it say what it could not see?** Step 4 exists to make this
   unavoidable. An output that skips step 4 and proceeds to step 5 has certified
   an absence, and its step 5 should be discarded regardless of how good it
   sounds.

**Then record the outcome as a PRICE** — §7 of `references/bug_attribution.md` —
with `declared_before` filled and `measured_after` left null. **A proposal that is
refused keeps its declared price**; that is what makes the refusal reviewable
later.

**A proposal nobody read counts as neither acted on nor refused.**
