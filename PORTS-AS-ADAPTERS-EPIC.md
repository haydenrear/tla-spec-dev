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

**The static scanners were deleted on 2026-08-04** — 9,552 lines — and what they
taught is `references/architecture_advice.md`: nine rules to act on now, restated
as acceptance criteria a future scanner must satisfy before it earns any
authority. The state space **divided** for the first time in this ledger's
history as a result.

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

The defenses are structural rather than exhortation, and they live in exactly
one place: **`references/eval_scorecard.md`** — the scoring rules, the anchors,
the judging protocol. **This charter does not restate them.** It restated the
baseline table once (§7) and two of those rows were wrong for weeks, which is
the whole reason it now points instead.

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

## 6. The scorecard is scaffolded now, and history is part of judging

**PA-05 blocks the evaluation on purpose.** For two epics every scorecard was
hand-authored from the rubric by whichever agent was judging — which is how a
dimension key or the `refuses_to_claim` requirement drifts, and it put the burden
of remembering five sets of anchors on the judge. PA-05 scaffolds the card with
the anchors and rules inline, and **makes blinding the default** rather than
something each eval remembers. Both prior rounds blinded correctly by discipline.
Discipline is not a mechanism.

**And it teaches the scorer to read history, which matters more.** The metric is
the delta — but a row can go stale without anyone noticing. The predecessor's
instrument was repaired *after* its measurement, and two of its sealed numbers
stopped describing the instrument that produced them. A scorer comparing naively
across that boundary would have compared two different instruments and called the
difference progress.

The reading rules PA-05 put in the rubric are `R-H1`..`R-H5` of
`references/eval_scorecard.md`, and every one of them is executed by
`score_tools.py audit`. **They are not copied here** — a reading rule stated in
two places is a reading rule that can disagree with itself, and the audit only
knows about one of the two.

Three worked examples are already in the record and you should be able to tell
them apart: guard relaxation 0 → 3 of 3 is a **real mechanism gain**; D1 = 3
appearing on **both** arms is an **attribution correction**, not a gain; and
"controls green on both arms" is a **sealed number known-wrong** for one arm.

## 7. Self-improvement is the delta, not the total

`specs/results/scorecards/SELF-IMPROVEMENT.md` carries every epic's scores on the
same five dimensions. **One epic's card says how good an artifact is; that file
says whether we are getting better.**

**The baselines you are measured against are not restated here.** Read them
from that file and from the sealed cards under `specs/results/scorecards/`:

```bash
python3 examples/validation/scorecards/score_tools.py history --example <example>
python3 examples/validation/scorecards/score_tools.py index specs/results/scorecards/<epic>
```

**This section carried a copy of that table, and the copy is why the sentence
above exists.** Two of its four rows were wrong, and both were wrong the same
way: written against `HP-06`'s sealed run, then read forward across the
instrument change that superseded it.

- One credited the treatment with a bug-detection result **both arms got**, and
  in doing so **contradicted §5 of this same document**, which says plainly:
  *"the bug-catching gain was the generator, which both arms get — not the
  prompt."* The table and the thesis disagreed, and the table was wrong.
- The other inverted which arm the best-ever honesty score went to. The score
  itself was right in both runs; the attribution was backwards — in the one
  document every ticket agent is told to read first.

Both were corrected by hand, mid-epic, by the epic owner. `PA-05` found the
first while building the tool for finding exactly this, which is the strongest
argument its ticket could have made for itself. The findings keep the wrong rows
verbatim in `specs/desired_program_model/deferred_findings.yaml`, because a
finding that deletes its own subject is not a finding.

Three things follow, and the third is why this section is now a pointer:

- **The sealed runs are not edited.** Both stand as measured; `INSTRUMENT-LOG.toml`
  records which one describes the current instrument, and `history` prints the
  note beside the row.
- **Watch every dimension when one moves.** A rise on one bought by a fall on
  another is not improvement — it is the toolchain learning to overclaim. Read
  that off the ledger, per example, never off a summary.
- **A declaration that nothing executes will drift** — including this one. A
  charter that copies the ledger goes stale; a charter that points at it cannot.
  `tests/test_card_has_one_home.py` is what turned that from a resolution into a
  check, after four deliberately disagreeing copies were seeded at `6aac1ec` and
  **three of the four went unnoticed by every instrument this repository ships**.

---

## 8. Discipline that keeps this honest

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

## 9. The standing rule

**A low or unflattering result is the preferred outcome.** Every epic here
produced its best material by measuring something that did not work: the gate
that caught nothing, the repair that moved zero cells, the structure that arrived
and caught no bugs, the clean audit that was clean because of its own filter.

**An epic that closes with only good news about itself has not been measured.**
