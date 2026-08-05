# Epic: ports as adapters

**Starter for the next epic agent. Read this before the plan.**

Branch `epic/ports-as-adapters`, cut from `main` after `hexagonal-prompting`
closed. Canonical plan: `specs/desired_program_model/ticket_plan.yaml`.

---

## Where this is going, in one paragraph

We are building a way to produce **simpler, better-validated software** by
combining three things that are each weak alone: **architecture guidance given as
a prompt**, **test cases generated from a formal model**, and **judgement from
intelligent agents, scored on a fixed card**. Complexity analysis sits underneath
all three as a **thermometer, never a thermostat** — it reports numbers, it
refuses nothing, and its output is input to a judgement rather than a gate. The
loop is meant to improve itself: the same card, on the same examples, across
epics, so that the *delta* is the measurement.

Everything below is why each of those clauses is worded that way, and every one
of them was bought with a measured failure.

---

## 1. The settled question: gates do not work here

Three epics were spent building static checks. The result is not ambiguous.

- **Bug detection did not move by a single cell** across two full eval rounds and
  seven repair tickets. 4 of 6, 6 of 6, 0 of 3, 0 of 3 — before and after.
- **Every check shipped was defeated cheaply.** Six lines of YAML in one round.
  A 41-line re-export file in the next, with every declaration digest unchanged.
- **The complexity gate failed every normal program** and was retired to advisory.
- **A static architecture check flipped its verdict on this repository because
  one variable was added, with nothing tuned**, clearing a criterion
  (`modularity_q > 0`) that cannot fail.

**Do not propose a new gate.** The current plan carries a `no_new_gates_rule` and
it is load-bearing: a ticket that finds itself adding a rule that refuses
something has left scope. Guidance goes into prompts. Verdicts come from judged
scorecards.

There was one gate still in the toolchain — the MF-026 coverage audit, which
refused a workflow close with **no override flag**. **Retired 2026-08-04**
(owner direction), with the static architecture scanners and for a related
reason: its verdict is a word the audited party types about a sweep the audited
party performed. The AUDIT is kept and is still the only thing here that looks
at unmodeled surface; the refusal is gone. Its own final judgement, twice, was
that the surface it guarded is bookkeeping about our own CLI. See
`references/coverage_audit.md`, "Status", and
`references/architecture_advice.md`.

---

## 2. Why an agent judges, and why that is not soft

A number computed from an artifact can be optimized by editing the artifact. **A
judgement that must cite the artifact can only be satisfied by changing what the
artifact is.** That is the whole argument, and it is not a claim that judgement
cannot be gamed — it is a claim that gaming it requires doing the work.

The defenses are structural rather than exhortation (`references/eval_scorecard.md`):

- score **artifacts, never claims** — a report sentence is not evidence;
- **any score ≥ 2 without a `file:line` citation is mechanically capped at 1**;
- **a score of 4 must name something the artifact refuses to claim**, so the top
  of every scale is unreachable by asserting more;
- **prose quality is never an input**;
- **two judges, blind to each other and to arm**, with a spread > 1 recorded as
  `contested` and adjudicated only on *new* evidence;
- **the mechanical block sits beside the judgement and is never scored**, so a
  disagreement between measurement and judgement is visible as a finding.

It works. Across 25 independent scores in one epic and 10 in the next, blind
judges produced **zero contested dimensions** — maximum spread 1. A rubric where
independent judges diverge is a rubric that measures the judge.

---

## 3. Complexity analysis: a thermometer, not a thermostat

The descriptor reports dimensions, a state-space bound, an R/W matrix,
modularity, dense rows. **It proposes nothing and refuses nothing** (CD-01), and
that is deliberate: a tool that picks the boundary makes every edge legal by
construction.

Two facts to carry:

- **A metric improving is not evidence the design improved.** MF-020: a number
  can fall because an edge was *deleted*. The best complexity result in the
  record was withheld from a top score by both judges for exactly this — a
  reduction that removed two variables with no check that could catch an
  external reader.
- **It measures TLA+, not produced code.** This is why the "simpler at equal
  behavior" goal missed last epic with D2 = 2 on both arms: not because the
  prompt failed to simplify, but because **nothing in the toolchain could tell.**
  Building that instrument is a goal of this epic.

---

## 4. What actually worked, and is worth reusing

Two mechanisms earned their place by measurement. Start from them.

- **The prompt produces real architecture.** Asking an agent for ports and
  adapters took modularity from **D3 = 1 to D3 = 4** on both blind judges — the
  first 4 on any dimension in the project's history. Arm B produced a `Protocol`
  port, a real adapter, a working fake, one composition point, and a domain that
  imports no I/O. `prompts/hexagonal_implementation.md`.
- **The negative corpus reaches a class nothing else could.** Guard relaxation —
  "the program accepts what the model forbids" — measured **0 of 3, 0 of 3, 0 of
  4** across three catalogues, five instruments and two rounds. Emitting the
  *disabled* edges at each reachable state as cases asserting rejection took it
  to **3 of 3 and 5 of 5**. Soundness is one-sided by construction: evaluation is
  three-valued and UNKNOWN never emits, so an unimplemented construct costs
  completeness and never soundness.

**Caveat that travels with the D3 win:** the treatment prompt was **6.6× longer**
in unique content than the control. "Hexagonal helped" is not yet separable from
"a longer prompt helped." A third arm settles it and has not been run.

---

## 5. The thesis of THIS epic

The two halves above were built and **never connected**, and the evidence is
exact:

> A fault in arm B's in-memory adapter **survives every instrument**. The port
> creates a region no shared oracle reaches.

and

> Per-mutant verdicts **identical on 49 of 49** comparable cells between the arms.

So the prompt created ports, and the validation machinery does not know ports
exist. Our adapters still bind to whole actions, exactly as they did before
hexagonal was mentioned. **The structure arrived and caught nothing.**

That is the gap, and closing it is the epic:

**Make the model's ports and the toolchain's adapters the same object.**

- the prompt already makes the agent declare ports in the domain's vocabulary —
  have it declare them in the **manifest** too;
- generate cases **per port**, not only per action;
- bind spec-unit and Test Graph adapters **to ports**, so a generated case drives
  a real port;
- make the **fake/real swap the instrument**: identical cases against both, and a
  fault in either dies.

The owner named this at the outset — hexagonal fits *because we already call them
adapters*. We built both senses of the word and never made them one object.

---

## 6. Self-improvement is the delta, not the total

`specs/results/scorecards/SELF-IMPROVEMENT.md` carries every epic's scores on the
same five dimensions. **One epic's card says how good an artifact is; that file
says whether we are getting better.**

Baselines you are measured against, all sealed in closed snapshots:

| | best ever recorded | where |
|---|---|---|
| **D1** bug detection | **3** (arm B, both judges) | first 3; was 2 or lower everywhere before |
| **D2** complexity | **3**, never 4 | withheld by both judges, twice, for the same reason |
| **D3** modularity | **4** (arm B, both judges) | first 4 in the project |
| **D5** honesty | **4** | and it went to the *control*, not the treatment |

**Watch D5 when the others move.** A rise in D1 bought by a fall in D5 is not
improvement — it is the toolchain learning to overclaim.

---

## 7. Discipline that keeps this honest

Written down because each one was learned by breaking it.

- **Commit predictions before dispatch, including negatives.** Six of one epic's
  predictions were wrong and knowing which six was the whole value. A round where
  every prediction passes measured nothing. **Predict what will NOT move** — the
  most informative result in two epics was a repair that worked and changed
  nothing.
- **Never edit a target to match a result.** Repairing an unrunnable *instrument*
  after an unflattering signal is legitimate; moving the *target* is not. Both
  happened last epic, in the same commit, deliberately labelled.
- **Never re-run selectively until a number passes.** Report the run that
  happened.
- **File findings; fix nothing during a measurement.** A fix during measurement
  destroys the measurement.
- **Seed a mutant in the gap each mechanism is supposed to lose.** A reduction
  result with no mutant in the gap is not a measurement.
- **Report per class, per arm — never a single kill rate.** A number without its
  arm is uninterpretable.
- **A positive control that survives invalidates its row.** One is currently red.
- **Ask every blind agent what it REJECTED.** For three rounds running the best
  finding came from that question, and **zero** came from re-running the suite.
- **Diff a carried-forward scope block against its source.** Copying one silently
  dropped two governing rulings, twice, in consecutive epics.

---

## 8. The standing rule

**A low or unflattering result is the preferred outcome.** Every epic here
produced its best material by measuring something that did not work: the gate
that caught nothing, the repair that moved zero cells, the structure that arrived
and caught no bugs, the clean audit that was clean because of its own filter.

**An epic that closes with only good news about itself has not been measured.**
