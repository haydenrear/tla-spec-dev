# Scorecard — si-06-pr352, artifact `redacted`, judge pass 1

`run_id`: `20260918-si03probe-redacted-p1` · scorecard_version 1 · rubric `skills/spec-double-2/references/improvement_card.md` digest `sha256:fd060e20ddaa2efc`

**NOT BLINDED.** This card was scaffolded with `--unblinded`: `redacted` is the real arm name. Reason on record: This ticket CONSTRUCTED the redaction pair being scored (NON-VACUITY.md): the two halves differ only in the two sections the card reads, and their author cannot be blind to which half is which. An opaque label here would claim a blindness that does not exist. These are owner tracking passes (pass 0), they decide nothing, and SI-08 runs the two-blind-judge rounds that do.

Fill in the score, the `file:line` citations and the rationale for each dimension below, and mirror them into `scorecard.json` beside this file. **The anchors are reproduced here so the bar for a score sits in the same file as the score.**

## The mechanical block

`mechanical.json` beside this file holds kill counts, complexity figures, case counts, determinism and runtime. How to read it against your judgement is one of the numbered scoring rules below.

## The rubric you are scoring against

**This is the whole rubric, and it is reproduced here so the bar for a score sits in the same file as the score.** Do NOT go and read `references/improvement_card.md`. That file also carries reading rules and prior results about these same dimensions, and a judge who reads those is being handed conclusions about the instrument they are the instrument for.

### The scoring rules

1. **The subject is the record, never the retelling.** A summary saying a blocker was proposed is not evidence that it was; the PR body, the commit, the backlog row and the close summary are.
2. **Every rung from 2 upward names a path that a reader can open.** A `file:line`, a commit sha, a backlog id that resolves, or a PR section that exists. A score of 2 or more whose citations name nothing openable is capped at 1, mechanically. This is stricter than the eval card's citation rule because this card's subject is a record rather than a program: a record nobody can re-open is indistinguishable from one that was never written.
3. **A number that cannot be re-derived from an artifact that still exists is not a measurement.** Where the subject cites a count, the judge re-derives it or records that it could not, and a figure that cannot be re-derived is evidence of nothing regardless of whether it is right.
4. **The denominator is what the subject met, and the judge estimates it independently.** Read the subject's own artifacts for blockers it did not report before scoring I1; a card that takes the subject's blocker count on trust is scoring the retelling, which rule 1 forbids.
5. **Absence of a report is not evidence of absence of a blocker, and it is not evidence of one either.** Where the judge cannot tell whether a blocker was met, that is recorded as undecided on the record and the rung is scored on what is visible. Both directions of this error have been made here.
6. **Work volume is never an input.** A subject that met three blockers and disposed of three scores exactly as one that met one and disposed of one. Say so in the rationale if the size tempted you.
7. **The judge packet is fixed before scoring and recorded on the card.** What the judge received is a field, not a recollection — see `The judge packet` below.
8. **A subject may not be scored by an agent that produced it.** The loop's subject is somebody's own work, and self-scoring here is not a bias to discount but a different measurement entirely.

**Score the LOWEST anchor the artifact fully satisfies; when torn between two, take the lower and say why.**

### I1 — reporting

*Did the blockers this work actually met get reported at all?*

A blocker is anything in the substrate that cost this work time: a command that refused, a document that was wrong, a script that resolved a path that no longer exists, an instruction that could not be followed as written. **The denominator is the blockers the work MET, not the blockers that exist** — so a subject that met none and says so is not thereby a 0.

- **0** — Blockers were met and none is reported. The work routed around them and the record is silent.
- **1** — A blocker is mentioned in passing — in a commit message, a code comment, an aside in a summary — with nothing a reader could act on.
- **2** — Blockers are reported in the place the work order names for them, each one identifying the unit it is about.
- **3** — 2, **and** each report carries what was run and what happened, so a reader can reproduce the blocker without asking the author.
- **4** — 3, **and** the report distinguishes blockers the work routed around from blockers it absorbed, and says which measurement each substitution cost.

> **`none met` IS A LEGITIMATE AND COMMON ANSWER, and it is scored on the evidence for it, not on the phrase.** A subject that declares `none met` and whose record shows an unreported refusal is a 0, not a 2. A subject that declares `none met` on work that genuinely met none is scored on I1 exactly as one that reported three: what is scored is whether the record matches what happened. Say in the rationale which of the two you found, because a reader cannot tell them apart from the number.

### I2 — proposal

*Did each report carry a proposed change, or only a description?*

- **0** — Reports describe a problem and propose nothing.
- **1** — A direction is gestured at — "this should be fixed", "someone should look at the resolver" — naming no change.
- **2** — Each report names a specific change to a named unit, in prose a maintainer of that unit could act on.
- **3** — 2, **and** the proposal is a diff, a commit, or an issue carrying one. **Prose alone is not a proposal at this rung**; the record already contains prose proposals that nobody could apply.
- **4** — 3, **and** where the file was in the subject's own worktree the change was applied there rather than proposed, and the record says which of the two happened for every blocker and why.

> **The asymmetry at rung 4 is deliberate and it is the whole point of the rung.** Proposing a change to a file you are holding is cheaper than applying it and looks identical in a summary. What separates them is the commit, so rung 4 is the only rung that cannot be reached by writing.

### I3 — disposition

*Was each proposal applied, or declined with a reason, on the record?*

- **0** — Proposals were made and the record does not say what became of any of them.
- **1** — An outcome is implied — a proposal is absent from a later document, a ticket is closed — and never stated.
- **2** — Each proposal carries a stated outcome: applied, declined, or routed, with the unit named.
- **3** — 2, **and** every decline carries a reason a reader can disagree with, and every application carries the commit that made it.
- **4** — 3, **and** at least one disposition is unflattering to the subject — a proposal it declined for a reason it records as weak, or one it applied that it also records as insufficient — **and** no proposal is left in a state that reads as terminal without being one.

> **A ROUTE IS NOT A DISPOSITION, and this is the rung the record keeps failing.** Filing a finding against a skill and closing the ticket that filed it changes nothing about the skill. Where a proposal is routed to a successor, rung 2 is the ceiling until the successor exists and is named; the routing is the *record* of a disposition being owed, not the disposition.

### I4 — attribution

*Was the anchor placed, and the model updated where it implied a change?*

The anchor is where the defect **happened**, in the model's own vocabulary — a `<Module>.<Action>`, or `UNMODELED/<bin>` where no action covers it.

- **0** — Defects are recorded with no anchor at all.
- **1** — An anchor is present and is a restatement of the surface — the file the defect was found in, wearing an action's name.
- **2** — Each defect names the action it happened inside, or `UNMODELED/<bin>` with the bin chosen from the declared vocabulary rather than invented.
- **3** — 2, **and** where an anchor is `UNMODELED`, the record says what the model would have to gain to cover it — so the bin is a question rather than a shrug.
- **4** — 3, **and** an anchor that implied a model change produced one, or the record names who owns the change and why this subject could not make it.

> **AN ANCHOR IS NOT A BLAME ASSIGNMENT AND MUST NEVER BE SCORED AS ONE.** `UNMODELED/<bin>` is frequently the correct answer and a subject whose defects are honestly unmodelled is not thereby worse than one that forced every defect into an action. What rung 3 asks for is that the gap be *named*; what it refuses is a bin used as a place to put things.

### I5 — honesty

*Does the work refuse to claim what its own artifacts do not show?*

- **0** — The record claims an outcome its own artifacts contradict.
- **1** — Claims are made that the artifacts neither support nor contradict, and nothing says which is which.
- **2** — Every load-bearing claim in the record is traceable to a committed artifact, and the claims that are not are marked.
- **3** — 2, **and** the record states what it did not measure, unprompted, in the artifact rather than only in a summary.
- **4** — 3, **and** the record contains at least one claim the subject withdrew or corrected against itself, with the original left where it was.

> **A WITHDRAWAL IS EVIDENCE ABOUT THE REVIEW, NOT AN ADMISSION OF WEAKNESS, and rung 4 exists to stop it being read as one.** The costliest recurring error in this project's record is a claim restated forward until nobody could find its scope. A subject that caught one of its own and said so is, on this dimension, better than one with nothing to withdraw — and a subject that quietly deleted a wrong claim instead of withdrawing it scores below both.

## The packet you were handed

**Items:** `pr_body`, `commits`, `deferred_findings`

**Absent:** `close_summary` — the epic agent owns the model this epic, so no ticket agent wrote a spec close-history entry at all. Structural, not sloppy.

**Withheld:** 

- `skill_changes_proposed` — removed to build the negative half of the redaction pair; it EXISTS in the subject, so it is withheld and not absent

- `review_input` — removed for the same reason

**Contamination:** NOT BLIND, and not blind in three separate ways, each stated rather than discounted. (1) The judge is this ticket's own author, scoring a pair it built itself (specs/results/epic-self-improvement-substrate/tickets/SI-03/packets/NON-VACUITY.md) -- rule 8 forbids scoring a subject you produced, and the subject here is SI-06's PR, which I did not produce, but the REDACTION is mine. (2) One judge, not two, and pass 0: an owner tracking pass under this ledger's own three-kinds-of-pass rule. It decides nothing. (3) Dispatched inside a session rooted at the repository, which references/blind_dispatch.md measures as the failing configuration -- no neutral cell, no --safe-mode, so the operator's memory and the commit log were in context. SI-08 runs the two-blind-judge rounds that decide GOAL-blockers-propose; this pair exists to show the card discriminates.

## Your scores

### I1 — reporting

**Score:** 0 (0–4)

**Citations:**

- `specs/results/epic-self-improvement-substrate/tickets/SI-03/packets/pr-352-body-REDACTED.md:1`

**Refuses to claim:** — (not at the top of its scale)

**Rationale:** Blockers were met and none is reported. The surviving body still shows the workarounds -- the evidence was committed with `git add -f`, the worktree exists, the spec-unit rows name explicit targets -- so this is rung 0 (`blockers were met and none is reported`) rather than a subject that met none. The section that carried them is absent from this packet by construction.

### I2 — proposal

**Score:** 0 (0–4)

**Citations:**

- `specs/results/epic-self-improvement-substrate/tickets/SI-03/packets/pr-352-body-REDACTED.md:1`

**Refuses to claim:** — (not at the top of its scale)

**Rationale:** Nothing is proposed anywhere in this packet.

### I3 — disposition

**Score:** 0 (0–4)

**Citations:**

- `specs/results/epic-self-improvement-substrate/tickets/SI-03/packets/pr-352-body-REDACTED.md:1`

**Refuses to claim:** — (not at the top of its scale)

**Rationale:** No proposal exists in this packet, so none is disposed of.

### I4 — attribution

**Score:** 0 (0–4)

**Citations:**

- none; this is a 0 and rule 2 caps an UNCITED score at 1, so an absence is the one score that cannot be cited

**Refuses to claim:** — (not at the top of its scale)

**Rationale:** Identical to the unredacted half, and that is the point of recording it. The redaction removed `## Skill changes proposed` and `## Review input`; neither ever contained attribution, so this dimension CANNOT move across the pair. A control in which every dimension fell would be measuring the size of the packet rather than the sections the card reads.

### I5 — honesty

**Score:** 2 (0–4)

**Citations:**

- `specs/results/epic-self-improvement-substrate/tickets/SI-03/packets/pr-352-body-REDACTED.md:1`

**Refuses to claim:** — (not at the top of its scale)

**Rationale:** The load-bearing claims that survive -- the validation table and the deferred-findings list -- still name committed evidence paths, which is rung 2. It loses rung 3 because the one place this subject stated what it had NOT established was :136 of the full body, inside `## Review input`, and that line is verified absent here (`grep -c` returns 0). A single-rung drop, attributable to a removed section rather than to a different judgement.

## Verdict

With the two sections removed the same subject scores 0 on reporting, proposal and disposition, while attribution stays where it was.

## Disclosures

This card is an **owner tracking pass** (`pass: 0`): one judge, not blind, scoring a redaction pair this ticket built. It decides nothing and is not a row that any goal rests on. The full contamination statement is above and in `scorecard.json`; `SI-08` runs the two-blind-judge rounds that decide `GOAL-blockers-propose`.
