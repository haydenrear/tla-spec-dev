# The Improvement Card

**Scorecard version 1.**
**Card kind: improvement.**

`references/eval_scorecard.md` scores an **artifact**. This card scores the
**loop**: what an agent did when the substrate got in its way. Its subject is a
piece of work — a ticket, a wave, or an epic — and the question it asks is
whether the blocker that work hit ended as a change to the substrate or as a
workaround nobody can find again.

**This card does not restate the eval card. It extends it**, and the extension
is by reference rather than by copy:

| what governs | where it lives |
|---|---|
| anchors are ladders; score the lowest rung fully satisfied | the eval card, and it is served to a judge from there |
| how many judges score, and what each may know of the other | the eval card's scoring rules |
| cite the artifact; a score with no citation is capped | the eval card's scoring rules |
| sealing, `R-H1`..`R-H6`, and how a history is read | the eval card's `Reading history` |
| bumping a card version, and what a bump costs | the eval card's `Changing this card` |
| what a judge is served, and what it is never served | the eval card's `How this card reaches a judge` |

Those rules are not reproduced here and must not be. A copy in this file would
be a second statement of a bar that nothing compares to the bar, which is the
defect `tests/test_card_has_one_home.py` exists to catch. **What this file
carries is only what is new: its own dimensions, its own anchors, its own
scoring rules, its own judge packet, and its own reading rules.**

## Why the loop needs its own card

Seven epics of this project improved the *product* and left the *substrate*
where it was. The record says why: a finding that names a skill was written up
in full and filed nowhere — thirteen of them at once, all carrying
`recorded-local` — because describing a blocker costs less than proposing a fix
for it and nothing ever read the difference.

`SI-04` gave that difference a field (`skill_change`, one grammar, four record
files, one reader). A field records; it does not judge. **This card is the
judgement, and it is deliberately judged rather than counted**, for the reason
the eval card already gives about numbers computed from artifacts: a count of
`skill_change:` tokens is satisfied by writing tokens.

## What this card measures

**Five dimensions, each scored 0–4.** There is no total and there never will be
one; the eval card's reasoning about sums applies here unchanged and is not
repeated.

| | Dimension | The question |
|---|---|---|
| **I1** | **reporting** | Did the blockers this work actually met get reported at all? |
| **I2** | **proposal** | Did each report carry a proposed change, or only a description? |
| **I3** | **disposition** | Was each proposal applied, or declined with a reason, on the record? |
| **I4** | **attribution** | Was the anchor placed, and the model updated where it implied a change? |
| **I5** | **honesty** | Does the work refuse to claim what its own artifacts do not show? |

**The order is the loop's order and it is not arbitrary.** A proposal cannot be
disposed of if it was never made, and a proposal cannot be made about a blocker
that was never reported. So I2 is bounded by I1 and I3 by I2 in practice, and a
card whose I3 exceeds its I1 by more than one rung is a card to re-read.

## The anchors

Score the **lowest** anchor the subject fully satisfies; when torn between two,
take the lower and say why. Every rung from 2 upward names a **committed path** —
see scoring rule 2 below, which is this card's own and is stricter than the eval
card's citation rule for a reason stated there.

### I1 — reporting

A blocker is anything in the substrate that cost this work time: a command that
refused, a document that was wrong, a script that resolved a path that no longer
exists, an instruction that could not be followed as written. **The denominator
is the blockers the work MET, not the blockers that exist** — so a subject that
met none and says so is not thereby a 0.

- **0** — Blockers were met and none is reported. The work routed around them
  and the record is silent.
- **1** — A blocker is mentioned in passing — in a commit message, a code
  comment, an aside in a summary — with nothing a reader could act on.
- **2** — Blockers are reported in the place the work order names for them, each
  one identifying the unit it is about.
- **3** — 2, **and** each report carries what was run and what happened, so a
  reader can reproduce the blocker without asking the author.
- **4** — 3, **and** the report distinguishes blockers the work routed around
  from blockers it absorbed, and says which measurement each substitution cost.

**`none met` IS A LEGITIMATE AND COMMON ANSWER, and it is scored on the
evidence for it, not on the phrase.** A subject that declares `none met` and
whose record shows an unreported refusal is a 0, not a 2. A subject that
declares `none met` on work that genuinely met none is scored on I1 exactly as
one that reported three: what is scored is whether the record matches what
happened. Say in the rationale which of the two you found, because a reader
cannot tell them apart from the number.

### I2 — proposal

- **0** — Reports describe a problem and propose nothing.
- **1** — A direction is gestured at — "this should be fixed", "someone should
  look at the resolver" — naming no change.
- **2** — Each report names a specific change to a named unit, in prose a
  maintainer of that unit could act on.
- **3** — 2, **and** the proposal is a diff, a commit, or an issue carrying one.
  **Prose alone is not a proposal at this rung**; the record already contains
  prose proposals that nobody could apply.
- **4** — 3, **and** where the file was in the subject's own worktree the change
  was applied there rather than proposed, and the record says which of the two
  happened for every blocker and why.

**The asymmetry at rung 4 is deliberate and it is the whole point of the
rung.** Proposing a change to a file you are holding is cheaper than applying
it and looks identical in a summary. What separates them is the commit, so
rung 4 is the only rung that cannot be reached by writing.

### I3 — disposition

- **0** — Proposals were made and the record does not say what became of any of
  them.
- **1** — An outcome is implied — a proposal is absent from a later document, a
  ticket is closed — and never stated.
- **2** — Each proposal carries a stated outcome: applied, declined, or routed,
  with the unit named.
- **3** — 2, **and** every decline carries a reason a reader can disagree with,
  and every application carries the commit that made it.
- **4** — 3, **and** at least one disposition is unflattering to the subject —
  a proposal it declined for a reason it records as weak, or one it applied that
  it also records as insufficient — **and** no proposal is left in a state that
  reads as terminal without being one.

**A ROUTE IS NOT A DISPOSITION, and this is the rung the record keeps
failing.** Filing a finding against a skill and closing the ticket that filed
it changes nothing about the skill. Where a proposal is routed to a successor,
rung 2 is the ceiling until the successor exists and is named; the routing is
the *record* of a disposition being owed, not the disposition.

### I4 — attribution

The anchor is where the defect **happened**, in the model's own vocabulary —
a `<Module>.<Action>`, or `UNMODELED/<bin>` where no action covers it.

- **0** — Defects are recorded with no anchor at all.
- **1** — An anchor is present and is a restatement of the surface — the file
  the defect was found in, wearing an action's name.
- **2** — Each defect names the action it happened inside, or `UNMODELED/<bin>`
  with the bin chosen from the declared vocabulary rather than invented.
- **3** — 2, **and** where an anchor is `UNMODELED`, the record says what the
  model would have to gain to cover it — so the bin is a question rather than a
  shrug.
- **4** — 3, **and** an anchor that implied a model change produced one, or the
  record names who owns the change and why this subject could not make it.

**AN ANCHOR IS NOT A BLAME ASSIGNMENT AND MUST NEVER BE SCORED AS ONE.**
`UNMODELED/<bin>` is frequently the correct answer and a subject whose defects
are honestly unmodelled is not thereby worse than one that forced every defect
into an action. What rung 3 asks for is that the gap be *named*; what it
refuses is a bin used as a place to put things.

### I5 — honesty

- **0** — The record claims an outcome its own artifacts contradict.
- **1** — Claims are made that the artifacts neither support nor contradict, and
  nothing says which is which.
- **2** — Every load-bearing claim in the record is traceable to a committed
  artifact, and the claims that are not are marked.
- **3** — 2, **and** the record states what it did not measure, unprompted, in
  the artifact rather than only in a summary.
- **4** — 3, **and** the record contains at least one claim the subject withdrew
  or corrected against itself, with the original left where it was.

**A WITHDRAWAL IS EVIDENCE ABOUT THE REVIEW, NOT AN ADMISSION OF WEAKNESS, and
rung 4 exists to stop it being read as one.** The costliest recurring error in
this project's record is a claim restated forward until nobody could find its
scope. A subject that caught one of its own and said so is, on this dimension,
better than one with nothing to withdraw — and a subject that quietly deleted
a wrong claim instead of withdrawing it scores below both.

## Scoring rules that make it hard to game

These are **this card's own** rules. The eval card's rules govern judging in
general and are served to a judge alongside these; they are not restated here.

1. **The subject is the record, never the retelling.** A summary saying a
   blocker was proposed is not evidence that it was; the PR body, the commit,
   the backlog row and the close summary are.
2. **Every rung from 2 upward names a path that a reader can open.** A
   `file:line`, a commit sha, a backlog id that resolves, or a PR section that
   exists. A score of 2 or more whose citations name nothing openable is capped
   at 1, mechanically. This is stricter than the eval card's citation rule
   because this card's subject is a record rather than a program: a record
   nobody can re-open is indistinguishable from one that was never written.
3. **A number that cannot be re-derived from an artifact that still exists is
   not a measurement.** Where the subject cites a count, the judge re-derives it
   or records that it could not, and a figure that cannot be re-derived is
   evidence of nothing regardless of whether it is right.
4. **The denominator is what the subject met, and the judge estimates it
   independently.** Read the subject's own artifacts for blockers it did not
   report before scoring I1; a card that takes the subject's blocker count on
   trust is scoring the retelling, which rule 1 forbids.
5. **Absence of a report is not evidence of absence of a blocker, and it is not
   evidence of one either.** Where the judge cannot tell whether a blocker was
   met, that is recorded as undecided on the record and the rung is scored on
   what is visible. Both directions of this error have been made here.
6. **Work volume is never an input.** A subject that met three blockers and
   disposed of three scores exactly as one that met one and disposed of one.
   Say so in the rationale if the size tempted you.
7. **The judge packet is fixed before scoring and recorded on the card.** What
   the judge received is a field, not a recollection — see `The judge packet`
   below.
8. **A subject may not be scored by an agent that produced it.** The loop's
   subject is somebody's own work, and self-scoring here is not a bias to
   discount but a different measurement entirely.

## The judge packet

**The eval card's judge opens a tree. This card's judge opens a record**, and a
record has no natural boundary — so the packet is enumerated rather than
described, and what the judge received is written onto the card.

A packet for one **ticket** subject is exactly these, and nothing else:

| item | where it comes from |
|---|---|
| the PR body | `gh pr view <n> --json body`, verbatim |
| the `## Skill changes proposed` section | inside that body; **its absence is data and is passed as absent**, never as an empty table |
| the `## Review input` section | inside that body |
| the `## Deferred findings` section | inside that body |
| the close summary | the spec close-history entry, where the subject closed one |
| the backlog rows the subject filed | by id, from the backlog the work order names |
| the subject's own commits | `git log --stat` over the ticket branch |

A **wave** subject is the wave review artifact plus every ticket packet the wave
merged. An **epic** subject is every wave packet plus the epic's own close
record. `subject_shape` is a required field on the card and takes exactly
`ticket`, `wave`, or `epic`.

**What the packet deliberately excludes:** this file, the eval card, any prior
improvement card, the self-improvement ledger, and every document stating how a
dimension of this card has scored or moved. A judge handed a conclusion about
the instrument they are the instrument for is the defect the eval card's
`serve` was built against, and the same mechanism covers this card — the bytes a
judge is served are rendered from parsed structure, never read out of this file.

**A packet that could not be assembled is recorded, never substituted.** Where
an item above does not exist for a subject, the card says so in
`packet.absent`; where it exists and was not passed, the card says that in
`packet.withheld` with the reason. The two are different and a card that
collapses them is not a legal card.

### The contamination note

`references/blind_dispatch.md` is the authority on what a dispatched agent
receives, and it is the authority for this card too. **Every improvement card
carries the contamination note that page prescribes for the path actually used**
— not the one that was intended — and carries it beside the score rather than in
a methods appendix.

Two facts about blindness on this card in particular, both of which make its
packet harder to blind than the eval card's:

- **The subject names the project in every line.** A ticket PR body cites this
  repository's paths, its skills and its ticket ids. There is no cell neutral
  enough to hide that, and no improvement card may describe itself as blind to
  the project's identity.
- **A judge who has read this project's memory has read its conclusions about
  its own loop.** That is exactly the leak class `blind_dispatch.md` measured,
  and it is the reason rule 8 exists: the cheapest available judge is the one
  that already knows the answer.

So the honest claim an improvement card may make is *blind to the arm and to the
other judge*, plus whatever the dispatch path earns, stated in that page's
words. **`NOT BLIND` is a legal card. A card claiming a blindness its dispatch
did not buy is not.**

## Controls

**Every check this card makes ships with a pair, and the pair is verified not to
be vacuous.** A control that would pass whatever the instrument did is not a
control, and this project has shipped one before.

For each dimension the record carries:

- a **positive control** — a real subject that should score at or near the top,
  and does;
- a **negative control** — a real subject that should score 0 or 1, and does;
- a **non-vacuity check** — evidence that the negative control's low score comes
  from the dimension and not from an unrelated defect in the packet. The cheapest
  form, and the one this card's own round uses, is a **redaction pair**: the same
  subject with and without the section the dimension reads, differing in nothing
  else. If both halves score the same, the check is measuring something other
  than what it claims.

A dimension whose negative control is constructed rather than real is marked
`synthetic` on the card, and a round in which every negative control is synthetic
is reported as such — the eval card's fixtures earned their keep by being real,
and a loop-scoring card built entirely on invented subjects would be scoring its
own imagination.

## Storage

Improvement cards live beside eval cards and are sealed by the same close:

```
specs/results/scorecards/
  <round>/
    <subject-id>/
      <run-id>/
        scorecard.json      # carries `card_kind: "improvement"`
        scorecard.md        # the judge's rationale and citations
        mechanical.json     # measured figures, never judged
```

`card_kind` is what separates the two populations. **An improvement card carries
`subject: null`** and is attributed by its own `subject_shape` and `subject_ref`
rather than through `subjects.toml`, whose scopes are the eval card's
architecture axis and have no meaning here.

### `scorecard.json`, the fields this card adds

Everything the eval card's schema requires is required here too and is not
restated. What is new:

```json
{
  "card_kind": "improvement",
  "scorecard_version": 1,
  "subject_shape": "ticket",
  "subject_ref": "PR #352 / SI-06",
  "packet": {
    "items": ["pr_body", "skill_changes_proposed", "review_input",
              "deferred_findings", "commits"],
    "absent": ["close_summary"],
    "withheld": [],
    "contamination": "NOT BLIND. ..."
  },
  "controls": {"I1": {"kind": "real", "negative": "<run-id>"}},
  "dimensions": {
    "I1": {"score": 3, "citations": ["path:line"], "rationale": "...",
           "refuses_to_claim": null}
  }
}
```

`packet.items` is what the judge received, `packet.absent` is what did not exist,
and `packet.withheld` is what existed and was not passed, each with a reason.
`packet.contamination` is required and non-empty on every filled card: the
blindness claim is a field, not a sentence somewhere in the prose.

`refuses_to_claim` is required and non-null for a score of 4 on any dimension,
exactly as the eval card requires at the top of each of its scales.

## Reading history

The eval card's `R-H1`..`R-H6` govern this card's history unchanged — the same
comparability, averaging, repair-versus-improvement, sealing, movement and
contested rules, executed by the same audit over the same ledger. They are not
restated here.

**Every rule below is executed**, by the same discipline the eval card states:
a reading rule nothing executes will drift, so `audit` fails if this file
declares an `R-I` rule with no check behind it.

### R-I1 — A subject is named by a reference that still resolves

A card's `subject_ref` must name something a reader can still open — a PR
number, a ticket id, a wave, an epic — and the card's citations must be
openable. A subject identified only by a description is a subject nobody can
re-score, and a card nobody can re-score cannot take part in a delta.

*Executed as:* every filled improvement card must carry a non-empty
`subject_ref` and a `subject_shape` from the declared vocabulary; a card whose
`subject_shape` is not one of `ticket`, `wave`, `epic` is a **VIOLATION**, and a
card carrying citations that name no path at all is reported `OPEN`.

### R-I2 — The packet is recorded, and absent is not withheld

What a judge received is part of what its score means. Two cards of the same
subject whose packets differ are not two measurements of one thing.

*Executed as:* a filled card with no `packet.items` is a **VIOLATION**; a card
whose `packet.withheld` is non-empty and carries no reason is a **VIOLATION**;
and two cards of the same subject in one round whose `packet.items` differ are
reported `OPEN`, because a spread between them is not readable as disagreement.

### R-I3 — A blindness claim is the dispatch's, not the author's

*Executed as:* `packet.contamination` is required and non-empty on every filled
card. A card whose contamination note claims blindness in words the dispatch
record does not support is not machine-detectable and is deliberately not
claimed to be — what is executed is that the field exists and is not empty, and
the rest is the judge's disclosure obligation under rule 7.

## Changing this card

The eval card's `Changing this card` governs this file too, mechanically and
without exception: bump `**Scorecard version N.**`, keep every old anchor in the
file, add a row to `Version history` keeping the old rows, freeze a copy before
editing, and re-score at least one prior subject under both versions. Nothing
about that rule is different here and none of it is restated.

**One thing is different, and it is a restriction rather than an exemption.**
This card has no sealed population yet. That makes a bump cheap *today* and it
will not stay cheap, so the first version is deliberately the smallest card that
can discriminate — five dimensions, no notes, no derived axis, no total — rather
than the most complete one. Rungs are easier to add than to retire; the eval
card's version 4 is the measured price of retiring three dimensions, and it made
that file and its tool longer.

### Version history

| version | anchors digest | served digest | what changed |
|---|---|---|---|
| **1** | `sha256:54155436f9ba69c2` | `sha256:8f66d32e9e9e7d12` | the original improvement card: five scored dimensions, eight scoring rules, an enumerated judge packet, `R-I1`..`R-I3`. |
