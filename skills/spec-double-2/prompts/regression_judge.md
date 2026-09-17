# Regression-attribution judge — sub-agent prompt

**Dispatch the "The ask" block verbatim to a judge that has NOT done the work.**
This is the leg round 1 was missing: its agents graded their own transcripts, and
a self-graded *"nothing could have told me that"* is precisely the verdict an
agent has an incentive to give.

## What the judge is and is not given

**Given:** the transcript, the task as the working agent received it, and the
tool output it saw.

**NOT given:** the friction ledger, the self-improvement matrix, prior rounds'
verdicts, or the working agent's own grading. **A judge handed conclusions about
the instrument it is the instrument for is not a measurement** —
`references/eval_scorecard.md` states the rule and this obeys it.

**Two judges, blind to each other.** Where they differ by more than one class, a
third pass adjudicates and must cite **new** evidence rather than re-read the
same lines.

---

## The ask

> Below is a transcript of an agent using a command-line toolchain to complete
> one task, and the task exactly as that agent received it. Judge the transcript.
> You are not judging whether the agent was clever; you are judging what the
> toolchain cost it.
>
> **1. Count the round trips.** A round trip is: the agent invoked a command,
> got a refusal or an error, and had to change something before trying again. A
> first invocation that succeeds is zero. Count from the transcript, not from any
> number the agent reported about itself.
>
> **2. Classify each round trip** into exactly one of:
>
> - **`TOOL-COULD-HAVE-SAID`** — the information the agent lacked was already
>   known to the tool at the moment it refused. Quote the message it gave and say
>   what it could have said instead.
> - **`DOC-COULD-HAVE-SAID`** — it was written down, in a file the agent had no
>   particular reason to open. Name the file.
> - **`IRREDUCIBLE`** — the agent had to supply a judgement, a value, or a piece
>   of context that nothing could have known for it.
>
> **Be hard on `IRREDUCIBLE`.** It is the verdict that lets a toolchain off, so
> it needs the strongest evidence: to use it, name what the agent had to decide
> and say why no message could have carried it. **"The agent worked it out from
> the file's comments" is `DOC-COULD-HAVE-SAID`, not `IRREDUCIBLE`** — the
> information existed.
>
> **3. Was any round trip the AGENT's fault rather than the tool's?** A
> malformed edit, a truncated read of the output, a command the tool never
> offered. **Say so explicitly and exclude it from the tool's cost.** A count
> that blames the toolchain for the agent's mistakes is worthless.
>
> **4. Was the agent misled by a SUCCESS?** Did any command exit 0 while
> producing a result that did not do what the agent thought? This is the failure
> mode a round-trip count cannot see, and it is worth more than the count.
>
> **5. One sentence: the single most expensive moment, and what the toolchain
> could have done differently at exactly that point.**
>
> Report the counts even when they are unflattering to the toolchain, and
> especially when they are unflattering to the agent. An inflated count makes
> the measurement worthless in the direction that feels generous.

---

## Reading the verdicts

**`TOOL-COULD-HAVE-SAID` is the only class that becomes a change.** It goes to
the change ledger with a price declared before the fix.

**`IRREDUCIBLE` is the floor and it is a real result.** A task whose trips are
all irreducible has nothing to fix, and reporting that honestly is why the class
exists. **But two judges independently reaching `IRREDUCIBLE` is evidence; one
agent saying it about itself is not.**

**A step-4 finding outranks the whole count.** An agent misled by a green has hit
a `BLIND` record, and those are the ones this project has repeatedly paid for.
