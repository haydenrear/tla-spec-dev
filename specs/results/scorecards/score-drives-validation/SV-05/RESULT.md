# SV-05 — the evaluation: three goals reached, one half of the owner's goal untouched, and every blind agent was contaminated before it read a word

**The `score-drives-validation` evaluation. It MEASURES and FIXES NOTHING.**

**Branch point `71ce81a`**, verified with `git rev-parse --short HEAD` against
`epic/score-drives-validation` and against the SHA the work order gave. They
agreed — the first time in this epic that a handed-out SHA and the local ref
both resolved to the same commit.

**Predictions sealed at `2026-08-12T18:41:42-04:00`** (`2026-08-12T22:41:42Z`),
commit **`3e16b96`**, before a single subcommand of `score_tools.py` was
executed, before the suite ran, before any predecessor's script was re-run at
this tree, and before any of the four blind agents existed. Twenty-seven
predictions, `PREDICTIONS-SV-05.md` beside this file, §0 of which lists exactly
what had already been read.

**Four of the twenty-seven are falsified. The declared alarm did not fire —
but read §2.1 before treating that as a well-designed round.**

---

## 1. The four goals, decided

| goal | verdict | the number it turns on |
|---|---|---|
| **`GOAL-caveat-discriminates`** | **DISCRIMINATES — not a null, and discounted rather than withdrawn** | `D3 = 4, 4` at v4 and `4, 4` at v5 on an artifact lacking the property, against CL-03's `4, 4 → 3, 3` on one that has it |
| **`GOAL-validation-is-scorable`** | **YES — and the answer was already in the card, and the carrier that was recommended is mis-priced** | the property is D4's retired anchor 4 verbatim; 3 clauses, not 2 dimensions, carried the toolchain grading; **both carriers cost a version bump** |
| **`GOAL-scored-at-goal-time`** | **NOT ACHIEVED — and the reason is not the one the epic was opened on** | 0 of 18 judged goals have a baseline the evaluation can open, unchanged; four skill diffs escalated, never applied; **and a blind stranger reading the UNPATCHED text already produces a card-backed baseline** |
| **`GOAL-loop-reaches-the-program`** | **ACHIEVED, once, n = 1** | control `3, 3` against treatment `4, 4`, one file's difference; **0 for 7 epics becomes 1 for 8** |

**Three of four reached. The fourth did not, and the half of the owner's goal it
belongs to is the half that was never attempted.**

---

## 2. The predictions, scored

Twenty-seven sealed. **23 held, 4 falsified.** Full table in §14; the four that
broke are here because they are the result.

| | prediction | outcome |
|---|---|---|
| **P2** | `--digest-only` is not a flag `serve` accepts | **FALSIFIED.** It is, it works, and using it uncovered `SV-05-DF-01` |
| **P3** | five distinct served digests across versions 1–5; at least one earlier version serves more than 9 rungs | **FALSIFIED ON BOTH HALVES — and this is the finding of the section.** Four distinct digests, not five: **`--card-version 4` and `--card-version 5` are byte-identical.** And every version renders **9 rungs**, including versions that scored five dimensions |
| **P18** | the counterfactual: the patched blind agent names a specific sealed card as its baseline and the pristine one does not | **FALSIFIED. Both did.** The diffs do not buy the card. §5 |
| **P23** | this epic files zero findings touching the shipped toolchain under `CL-04`'s narrow definition | **FALSIFIED.** One — `SV-06-DF-04`, and it is **the first finding in 205 ledger rows ever to name root `SKILL.md`**, a surface `CL-04` measured at zero across six epics |

### 2.1 The alarm did not fire, and that is not the same as a good round

`CL-04` got 3 of 11 wrong and warned: *"six of the eleven merely predicted that
the predecessors' reports would reproduce."* **This round is worse on that axis,
not better.** Of the 23 that held, **13 predicted that a predecessor's report
would reproduce when I re-derived it at my tree** — and reports in this project
have reproduced reliably for six epics. The informative predictions were the
ones with a mechanism, and **three of the four mechanism-carrying ones broke**
(`P3`, `P18`, `P23`). `P27`'s bar — at least 3 falsified — was cleared by
exactly one.

**Every prediction I made about the four goals' verdicts held.** That is the
weakest part of this round: I read six RESULT pages before sealing, and §0 of
the predictions says so. The verdicts are re-derived from cards and scripts
rather than believed, which is worth something, but **agreement between a reader
and what they read is not evidence.** The material that is worth anything here
came from the two things I could not read in advance: the blind 2×2 (§5) and
running the instrument myself (§3).

---

## 3. `GOAL-caveat-discriminates` — DISCRIMINATES, and here is the discount

**Re-derived from `scorecard.json`, not from SV-01's prose.** All four cards
read directly:

| card | rubric | served digest recorded | D2 | **D3** |
|---|---|---|---|---|
| `20260812-sv01v4-GL-p1` | `rubric_v4_frozen.md` | `sha256:a213a36770ccab09` | 2 | **4** |
| `20260812-sv01v4-GL-p2` | `rubric_v4_frozen.md` | `sha256:a213a36770ccab09` | 2 | **4** |
| `20260812-sv01v5-GL-p1` | `references/eval_scorecard.md` | `sha256:2d7d4a0506d9b259` | 2 | **4** |
| `20260812-sv01v5-GL-p2` | `references/eval_scorecard.md` | `sha256:2d7d4a0506d9b259` | 2 | **4** |

All four judges `claude-opus-5[1m]`. **`D3` delta across the version boundary:
0.** Against `CL-03`'s `4, 4 → 3, 3` on an artifact that HAS the property. The
missing cell is filled, `close-the-loop`'s headline is a **detection**, and
`CL-04-DF-05` is discharged.

### What it costs, and it is more than SV-01 charged itself

1. **`SV-01-DF-01` — every one of the four judges was handed a scratch directory
   holding a prior round's artifact and a prior `D3 = 4`.** The leak cuts
   *toward* the predicted answer. SV-01 disclosed it, refused to discard a card
   after seeing its score (the right call), and reported it as cutting toward
   the answer. **I do not withdraw the verdict on this. I discount it**, because
   two of the four judges reported the directory unprompted, said they opened
   nothing, and moved to a fresh subdirectory — and because the mechanism the
   judges gave for keeping 4 is *specific and checkable*: both v5 judges cite
   `tests/test_ledger.py:244/247` reading the file out of band, and that is a
   fact about the artifact, not about what they saw in an `ls`.
2. **And there is a second contamination SV-01 could not have seen, because it
   arrives before any tool call.** §5.4: **the operator's auto-memory is in every
   subagent's context before it reads anything**, and at the time SV-01's judges
   ran it contained the line *"Scorecard D1/D4/D5 unstable — measured 2026-08-05:
   up to 2 points per judge move on byte-identical artifacts; its D2/D3 claim is
   CORRECTED by the next two entries"* and *"Subtract-to-measure epic — D2 proven
   able to measure, D3 shown contested"*. **Four judges scoring D2 and D3 blind
   had, in context, a sentence telling them which dimensions this project
   believes are stable.** `SV-05-DF-02`. This does not point in an obvious
   direction for `D3 = 4` and I do not claim it produced the answer; it does mean
   **no round in this programme has ever been blind in the sense its dispatches
   assert.**
3. **`SV-01-DF-04`, unchanged and load-bearing.** The shared 28-case suite is
   blind to the property on *both* artifacts. The discrimination is conditional
   on a judge reading or running **the artifact's own tests**.
4. **Two cells, on two different examples.** `R-H1`/`R-H2`: these are not two
   rows of one table and nothing here is averaged.

**Verdict: the caveat discriminates, on one artifact, one judge model, four
cards, with two disclosed contaminations one of which was invisible to the
ticket that ran it.** It is a real negative control and it is not a calibration
curve.

---

## 4. `GOAL-validation-is-scorable` — YES, with the recommendation refuted

**Re-run at MY tree — 95 cards, not the 87 SV-02 was written against:**

```
D1 anchor decisions citing local machinery   28 of 75   (37%)
D4 anchor decisions citing local machinery   13 of 75   (17%)
D3 anchor decisions citing local machinery    0 of 95
demonstration sentences, machinery-citing    44 of 343  (12.8%)
  ... inside the ladder-free N-D1 notes       1 of 39   (3%)
```

**The decomposition holds and is the answer**: 13 of 13 of D4's machinery-citing
decisions name anchor 3; 26 of 28 of D1's name anchor 3 or 4. **Three clauses
carried the toolchain grading, not two dimensions.** The property — *the
artifact's own checking has a demonstrated red, and the region where it stays
green is named* — is provenance-blind and is **already in the card** as D4's
retired anchor 4 and D3's live v5 caveat.

**One SV-02 figure moved and is restated rather than quoted.** Its headline
autopsy fraction was **14.0% (44 of 315)**; at 95 cards it is **12.8% (44 of
343)**. Same numerator, denominator grew by the epic's own eight cards.
`denominator_rule`.

### The refutation, and it is the ticket's best product

`SV-07-DF-01`. `references/scoring_validation.md` §7 concluded *"Carrier R
requires a version bump… **The free carriers do not.**"* **The second sentence is
false**, demonstrated by SV-07 executing the card's own change rule against a
card carrying the candidate prompt: a recorded note's prompt is inside **both**
of the card's seals. **Both carriers cost a version bump.** What still separates
them is 4 permanent rungs and 682 bytes — a real difference, and **not the
difference the recommendation rested on**.

**`serve | wc -c` does not distinguish the two carriers on the axis that binds.**
The epic's single surface metric is silent about the cost that actually decides
this choice. That is the sharpest thing this epic learned about its own
instrument, and it was learned by a ticket **trying to ship the recommendation**
rather than by reading it.

**Verdict: validation IS scorable without grading a toolchain. The card can
already say so. Nothing was restored, and nothing should be until SV-02 §7.1's
round runs — which this ticket REJECTED running, with a reason (§10).**

---

## 5. `GOAL-scored-at-goal-time` — NOT ACHIEVED, and the blind test relocated the gap

### 5.1 The numbers did not move, because nothing was installed

Re-running the predecessors' own scripts at my tree:

| | SV-06 at `a527305` | SV-03 at `5620c9a` | **SV-05 at `3e16b96`** |
|---|---|---|---|
| distinct epic goals | 27 | 27 | **27** |
| … naming a dimension in prose | 12 | 12 | **12** |
| … naming a judged instrument | — | 18 | **18** |
| … whose baseline the evaluation can **open** | — | **0 of 18** | **0 of 18** |
| `baseline.evidence` pointing at a `scorecard.json` | 0 of 27 | 0 of 27 | **0 of 27** |
| sealed cards on disk | 87 | 95 | **95** |

**Zero movement on every row.** The four skill diffs were **escalated, not
applied** — correctly, under the epic's own rule that skills are read and never
written from here. **All four still apply cleanly** (`git apply --check`,
`SV-05` re-ran it) to **both** installed homes. `P15` held.

`GOAL-loop-reaches-the-program`'s own baseline still cites
`specs/results/scorecards/close-the-loop/`, **a directory containing zero
`scorecard.json` files**, which is SV-03's `R1` subject and is untouched.

### 5.2 The blind 2×2 — the test SV-06 §9 and SV-03 §10 both handed to this ticket

Four agents, none given this repository, its `specs/`, its cards or its history.
Each got a scratch copy of the six surveyed skill files and one epic plan for a
**fictional** project, and an identical prompt that never used the words
*rubric*, *score* or *card*. **Design sealed in `PREDICTIONS-SV-05.md` §4 before
any agent existed.** Nothing was written to any `SKILL_MANAGER_HOME`;
`skill-manager sync` was never run.

| arm | skill text | plan | outcome |
|---|---|---|---|
| **A** | pristine | judged instrument, never run on this subject | named **four specific evidence files**, refused the other service's scores, refused to average — **but routed through the `"Harness does not exist"` branch and deferred the baseline to a wave-1 ticket** |
| **B** | + SV-03's four diffs | the same | cited the new sentence **verbatim** — *"The instrument existing is not a baseline"* — and ran the kickoff **on the epic branch before any ticket lands** |
| **C** | pristine | no card anywhere | **never asked what rubric to use.** Rejected the judged route explicitly, on the project's own README |
| **D** | + the four diffs | the same | **the same.** Never mentioned the added sentences as an obstacle |

### 5.3 What the diffs actually buy — `P18` falsified, and SV-06's stated buy is corrected

**`P18` predicted that only the patched agent would name a specific sealed card.
Both did.** Arm A, on the *unpatched* text, wrote a baseline naming
`reviewer-1.md`, `reviewer-2.md`, `scope.txt` and `setup.md`, pinned the
instrument by blob SHA, fixed the scored artifact as a file list, refused to
average the two reviewers, and refused to reuse the other service's numbers.

**So the openable card was already reachable from the text as it ships.** SV-06
says edit 01 *"buys the whole of `GOAL-scored-at-goal-time`'s target"*. **It buys
half of it, and the half it buys is the half the goal is named after.** What
separates A from B is **when**:

- **A had no branch to stand in and said so in the file**: it wrote
  *"per goals-and-evaluation.md (`Harness does not exist`) this goal takes the
  wave-1 route"* — routing a judged instrument that plainly **does** exist into
  the branch for one that does not, and thereby producing a baseline scored at
  **ticket** time, after RS-04 merges.
- **B took the third branch** and produced a baseline scored at **goal** time,
  before any ticket lands.

**That is a cold, independent confirmation of `SV-06-DF-02` and of SV-03's
premise**: an owner whose judged instrument exists but has never been run on this
subject is in neither branch, and a competent stranger mis-routes into the wrong
one. It was found by a reader who had never seen this repository.

**And it relocates the gap.** The epic was opened on *"no goal has ever been
keyed to a dimension"*. SV-06 corrected that to 12 of 27. This round adds the
rest: **the documentation as it ships today already leads a stranger to a
card-backed, sealed, per-judge, non-averaged baseline. The compliance rate of 0
of 18 is not a documentation gap. It is ours.** `SV-06-DF-02` called it *"a skill
rule with a compliance rate of zero in the project that it names"*; this round
shows the rule is **followable cold**, which makes the zero worse rather than
better.

### 5.4 The absence guarantee holds — and every arm was contaminated before it started

**`P17` held.** Neither no-card arm asked what rubric to use. Both **rejected the
judged route in terms**, C at length: *"the README says outright that there is no
review rubric… importing a rubric here would be importing another repository's
machinery into a 6k-line Go tar tool."* **The patched arm did not notice the
added sentences** — which is the pass condition SV-06 sealed in advance.

**`P19` and `P20` held, and produced the most valuable output of the round.**

**`SV-05-DF-02` — the leak that no dispatch in this programme has ever named.
Four of four blind agents, unprompted, reported that the operator's persistent
auto-memory and environment block were in their context BEFORE they opened
anything.** One quoted `MEMORY.md` verbatim — *"up to 2 points per judge move on
byte-identical artifacts"* — and named `single-example generalisation`,
`ports-as-adapters`, `subtract-to-measure` and `architectural-coherence`. The
environment block additionally handed each of them this repository's path,
branch, clean status and **the subject lines of its five most recent commits,
several of which state epic outcomes**. Two agents said plainly they could not
claim it had no influence.

**This requires no tool call.** `SV-01-DF-03` filed `git status` as a blinding
leak the dispatches never named; this is strictly worse, because a forbidden-list
cannot reach it. **It applies retroactively to every blind round this programme
has run** — CL-04's adopter probe, SV-01's four judges, SV-04's four judges,
SV-06's census, and these four.

**`P20` held four ways over.** All four agents independently found the same two
defects in the **installed** skill text, which no ticket in this epic named:
(i) `harness:` holds a ticket id where the schema asks for the instrument, and
(ii) `tickets: []` leaves the plan failing conditions the validator calls
**errors**, not warnings — *"the plan cannot validate as it stands, whatever I
write in `baseline:`"*. **Four independent rediscoveries inside one round**, on
the surface this whole goal rests on. That is `HARVEST-CL-03`'s
rediscovery-multiplicity signature reproduced a third time in this epic.

**Verdict: NOT ACHIEVED.** The design exists, it is demonstrated to work on a
stranger, it demonstrably costs a no-card project nothing — **and none of it is
installed, so not one number in this repository moved.**

---

## 6. `GOAL-loop-reaches-the-program` — ACHIEVED once, and I reproduced both halves

Read from the cards, not the prose:

| card | arm | D2 | **D3** |
|---|---|---|---|
| `20260812-sv04conf-GL-p1` / `-p2` | **CTL** (byte-identical to CL-03's packet) | 2, 2 | **3, 3** |
| `20260812-sv04conf-LG-p1` / `-p2` | **SV** (+ one file) | 2, 2 | **4, 4** |

**`D3` +1, unanimous, control unanimous at the predecessor's value, one added
file the only mover.** Harvested class `A1`, filed once as `RM-05-DF-05` and
consumed by nothing for seven epics. **0 for 7 becomes 1 for 8.**

### Both halves reproduced independently, in a scratch copy

| mutant | shared 28, real | shared 28, fake | conformance 14 |
|---|---|---|---|
| control | 28 pass | 28 pass | 14 pass |
| **M1** — `FileJournal` gutted, zero filesystem contact | **28 pass**, **0 `ledger.txt` created** | **28 pass** | **6 fail** |
| **JF-5** — the domain keeps a shadow list and never calls the port | **28 pass** | **28 pass** | **14 pass — 70 of 70 GREEN** |

**`P16` held on both halves.** M1 — the harvested class — survives the shared
suite under both wirings and dies under the new file. **My M1 kills 6 where
SV-04 reported 5**; my mutant is not byte-identical to SV-04's (mine drops the
truncating `write_text` in `__init__`), and I report the difference rather than
round it to agreement.

**And `JF-5` reproduces exactly: 70 of 70 green.** The unflattering half of
SV-04's own result stands under independent reproduction — **a domain that stops
calling the port entirely is invisible to all three suites, including the one
built to consume the harvested class**, whose docstring claims the opposite
(`SV-04-DF-01`, filed, not repaired).

**Verdict: ACHIEVED, n = 1, one artifact, one feature, one class, with the
built artifact's own claims falsified inside the round that built it.**

---

## 7. The owner's two-half goal — how much is now true

> **1. Any project being onboarded can, during any and all epics and as part of
> the goal process, score its validation and its architecture.**

**Architecture: yes, and it travels.** D3 separates on two examples, across judge
tiers, its caveat fired on a stranger's artifact it was never written for, **and
it now has a negative control.** A blind adopter ran the whole loop on a program
it wrote itself.

**Validation: scorable, and not scored.** The property is provenance-blind, is
already in the card as a retired anchor and a live caveat, and is elicited today
only through an **unscored note**. Restoring it to a score costs 4 permanent
rungs; sharpening the note costs a version bump. **Nothing was changed. The card
serves two scored dimensions and it did before this epic.**

**"During the goal process": NO, and this is the load-bearing failure.** 0 of 18
judged goals have a baseline the evaluation can open; the wiring is designed,
demonstrated, escalated, and **not installed**. A project onboarding today gets
whatever its owner improvises — which, measured cold on a stranger, is **most of
the way there and routed through the wrong branch**.

> **2. From that goal and scorecard, new validation processes are introduced
> into the project — improved architecture and diagrams, and integration and
> unit tests derived from them.**

**Tests: once. Diagrams: never, and there is no evidence base at all.**
**Architecture improvements: no** — SV-04 deliberately did not touch
`reference_ports/`, because moving the scored bytes would have destroyed the
counterfactual. **Model actions and adapters: no.**

**Scored honestly: half one is roughly two-thirds true and one-third installed.
Half two is 1 for 8 on tests and 0 for 8 on everything else it names.**

---

## 8. The diagram zero — and what it means for the next epic

Re-derived at 95 cards:

```
DIAGRAMS: 0 sentences across 0 of 95 cards.
```

`diagram`, `mermaid`, `UML`, `C4` and `.svg` appear in **no rationale, no note,
no verdict, on any card this project has ever sealed** — eight epics, five card
versions, five examples. It was 0 of 87 when SV-02 measured it; **this epic added
eight cards and did not move it off zero.**

**Half the owner's stated second half has no evidence base whatsoever**, and
three separate tickets refused to build one — SV-02 rejected a rung for diagrams
under `MF-020`, SV-04 rejected building a diagram *"to be scored against a rung
that does not exist"*, and SV-07 added nothing. **All three refusals were
correct.** A rung fitted to a known answer is the one move this project has
refused for eight epics.

**What it means for the next epic, plainly:** the honest options are two, and
they are not symmetric.

1. **Drop diagrams from the owner's goal statement** and say the goal was
   written wider than anything this programme has ever measured. Zero cost, and
   it makes the goal decidable.
2. **Run one round that scores an artifact WITH a diagram against the same
   artifact WITHOUT one**, under the card as it stands, and see whether any judge
   mentions it unprompted. **If no judge mentions it, there is nothing to score
   and option 1 is forced.** That is a cheap negative control of exactly the
   shape `SV-01` just ran, and it is the only route to a diagram rung that is not
   `MF-020`.

**Do NOT add a diagram rung first.** Eight epics, zero sentences, and this
project's own doctrine forbids fitting an axis to an answer nobody has.

---

## 9. Four tickets corrected their predecessor — health, or underpowered research?

**On the evidence: mostly underpowered, in one specific and repeatable way.**

| correction | what it took to find | available to the predecessor? |
|---|---|---|
| SV-06 corrects the epic's *"no goal has ever been keyed to a dimension"* → **12 of 27** | one survey script over plans already on disk | **yes — the owner wrote the baseline without running it** |
| SV-03 corrects SV-06's **0 of 27 → 0 of 18** and finds its wording unsatisfiable by its own exemplar | resolving `baseline.evidence` against the filesystem, over data SV-06 had already enumerated | **yes.** SV-03 says it: *"found by running the rule against the record, not by reading it"* |
| SV-07 refutes SV-02's *"the free carriers do not"* | executing the card's change rule against a card carrying the prompt | **yes — SV-02 already imported the real renderer** to price the bytes and stopped one command short |
| SV-04's `SV-04-DF-04` corrects `CL-03-DF-02` | **a new round, a new file, four fresh judges** | **NO. Genuinely unavailable to CL-03** |
| SV-01 and SV-06, independently, correct the work order's *"2 reds"* → **3** | running the suite at the branch point | **yes — the owner did not run it** |

**Four of five corrections were available to the party they corrected, from data
that party already had, and were found by a successor EXECUTING a rule its
predecessor had only STATED.** One required new measurement.

**That is not a healthy pipeline; it is a research design with a hole in it, and
the hole has a name.** Every research ticket in this epic produced a *rule* or a
*figure* and did not run it against the record it was derived from. The project
already has the doctrine — `R1`, *an instrument ships with a demonstrated
failing input on a real subject* — and it is applied to instruments and not to
**prose recommendations**. `SV-07` is the counter-example that proves it works:
it was the only ticket asked to *ship* its predecessor's recommendation, and it
refuted it in one command.

**The recommendation for the next epic is one sentence: every research ticket
must run its own proposed rule against the sealed record before it ships, and
report what the rule refuses.** That is not a gate; it is what `R1` already says,
pointed at prose.

**The healthy reading, stated so it is not lost:** every one of these
corrections was *found and filed*, none was buried, and two were found
independently by tickets that could not see each other. A programme where the
successor reliably corrects the predecessor **in public** is working. It is
working expensively.

---

## 10. The consumption rate — where it stands

`HARVEST-CL-03.md` carries **38 numbered classes** (`grep -cE '^\*\*[A-F][0-9]+\.'`
→ 38, re-run at my tree). Of those, ~1 had ever been filed, and **0 had ever been
consumed** in seven epics.

| | before this epic | **now** |
|---|---|---|
| harvest classes **consumed into program validation** | **0 of 38** | **1 of 38 (2.6%)** — `A1`, by `test_journal_conformance.py` |
| harvest classes **named by a ledger row** | ~1 | **4 of 38** — `A1`, `E1`, `F3`, `F6` |
| new judge-found defect classes **filed but unconsumed** | — | **3** (`SV-01-DF-05`) + 2 (`SV-04-DF-03`, `SV-04-DF-05`) |
| `HARVEST-CL-03.md` itself | 38 classes | **38 classes — untouched this epic** |

**The rate moved, once, and it is the first time.** But read the second row
before quoting the first: **three of the four newly-named classes are this
project catching itself committing the class**, not consuming it —
`E1` (the file written to consume `A1` shipped a false docstring), `F3` (our own
`score_tools.py` narrates prior scores at every judge it serves), `F6`
(reproduced in SV-04's own two judges).

**And the denominator is now stale in the wrong direction.** `SV-01-DF-05` filed
**three defect classes** four blind judges found in a scored artifact that both
suites miss. They went into the ledger; **nobody appended them to the harvest.**
The harvest is a snapshot of one sweep on one day and nothing maintains it, so
`38` understates the backlog and every future *"1 in 38"* will be measured against
a denominator that stopped growing on 2026-08-11.

**Where it stands: 1 consumed, 38 known, 5 more filed outside the register, and
the register is not being kept.** The bottleneck is unchanged — the programme
detects abundantly (8 of this epic's 26 findings came from blind judges; four
independent judges reproduced `A1` in one round; four independent blind agents
reproduced two skill defects in another) and consumes once per epic when a
ticket is explicitly funded to.

---

## 11. The served surface — before and after, with `--digest-only` per version

**`P1` held. The card was not touched by this epic and is not touched by this
ticket.**

```
git diff eab2883 71ce81a -- references/eval_scorecard.md    (empty)
serve | wc -c    6,281  ->  6,281      rungs   9 -> 9
```

| tree | `serve \| wc -c` | rungs | cards | `check` problems |
|---|---|---|---|---|
| `eab2883` — epic base | **6,281** | 9 | 87 | 330 |
| `71ce81a` — epic tip | **6,281** | 9 | 95 | 330 |
| `71ce81a` + SV-05 | **6,281** | 9 | 95 | 330 |

`audit`: **0 violations**. `contested`: **9 contested dimensions over 39 judge
groups, 0 unrecorded** — this epic's eight cards introduced **no** new contested
dimension. `SV-02-DF-02` reproduces: `serve 2>/dev/null` is 6,281 and
`serve 2>&1` is 6,373, and the metric still names no stream.

### `--digest-only`, per version — and it is a defect, not a table

`P2` said the flag does not exist. **It exists.** `P3` said five versions would
give five digests and that an earlier version would serve more rungs. **Both
halves false:**

| `--card-version` | bytes | rungs | `--digest-only` |
|---|---|---|---|
| 1 | 4,450 | **9** | `sha256:a753de37842e4953` |
| 2 | 5,191 | **9** | `sha256:d6bc48a44641aead` |
| 3 | 5,548 | **9** | `sha256:116146e48ecec13b` |
| **4** | **6,281** | **9** | **`sha256:2d7d4a0506d9b259`** |
| **5** | **6,281** | **9** | **`sha256:2d7d4a0506d9b259`** |
| 6 | — | — | `REFUSED: … the card declares version 5` |
| *the real v4*, `--rubric rubric_v4_frozen.md` | *6,319* | *9* | *`sha256:a213a36770ccab09`* |

**`--card-version 4` and `--card-version 5` are byte-identical, and neither is
the version 4 card.** The diff against the frozen v4 is exactly two lines, and
one of them is **the version 5 caveat** — *"and two fakes are not a pair… if the
only observer of the effect the port exists for is the adapter that wrote it,
say so and take 3"* — the single sentence that is the treatment in this epic's
headline experiment.

A round that reproduces the v4 arm through the flag alone gets **the v5 text
under a `scorecard_version: 4` label, recording the v5 served digest**, and
`check` accepts it. Versions 1–3 are worse in a quieter way: they render at
**9 rungs** when those versions scored five dimensions, so they are cards that
never existed. **Only version 6 refuses.**

**`SV-01` got this right only because it used `--rubric rubric_v4_frozen.md`.**
This is the mechanism behind the still-open `FI-06-DF-11(c)` — *five consecutive
rounds reproduced an old card by operator sequencing rather than by tooling* —
and it is worse than that finding says: **the tooling route exists, and it
silently returns the wrong card.** Filed as `SV-05-DF-01`.

### And the surface metric is blind to a real degradation

`scope`, every row naming its tree:

| tree | counted | REFUTED | COUNT-MOVED | **HOLDS** | UNREACHABLE |
|---|---|---|---|---|---|
| `eab2883` — epic base | 92 | 67 | 0 | **5** | 20 |
| `86a8767` — SV-04's branch point | 97 | 71 | 0 | **6** | 20 |
| **`71ce81a` — epic tip** | 97 | 75 | 0 | **2** | 20 |
| `71ce81a` + SV-05 | 97 | 75 | 0 | **2** | 20 |

**Four claims that held at `86a8767` are refuted at `71ce81a`, and this epic's
own eight cards did it** by moving `ab_quota_ledger`'s population 63 → 67 and the
corpus 87 → 95. One of the four is **the shipped card file itself** —
`references/eval_scorecard.md:42`, *"D1 is 3 on 56 of 63"*, now re-deriving as
**56 of 67**. Another is `references/scoring_validation.md:247`, **written this
epic and refuted by this epic**.

**The whole record now carries 2 claims that hold out of 97 counted, and both
are on one page about a six-card example.** `serve | wc -c` did not move by one
byte through any of it. `SV-05-DF-04`.

---

## 12. Suite numbers, each with its tree

`uv run --with pytest --with pyyaml python -m pytest tests -q`. **No figure below
is a `git archive` figure.**

| # | tree | working state | collected | result |
|---|---|---|---|---|
| 1 | `71ce81a`, detached `git worktree` at `…/scratchpad/SV-05/baseline-71ce81a` | **clean, `git status --porcelain` = 0** | **1,530** | collect-only |
| 2 | `feature/SV-05` at `3e16b96`, the sealed-predictions commit | this ticket's predictions only | **1,530** | **2 failed, 1528 passed** (1357.72s, 22:37) |
| 3 | `feature/SV-05`, final tree — the three files named above | the RESULT, the five findings, `NEXT-EPIC.md` | — | **the same 2 failed**, re-run targeted (`2 failed, 60 passed`) |

**`P7` held: 1,530 collected at the epic tip.** **`P8` held: SV-05's delta on
the collected count is 0, measured with `--collect-only` at both trees, not
assumed.** This ticket writes no test, deletes none, skips none and weakens none.

**The two inherited reds are the two the charter declares, and NEITHER IS
REPAIRED:**

- `tests/test_architecture_tags.py::test_the_same_tag_control_holds` —
  `RM-06-DF-01`, whose own docstring says *"THIS TEST IS DELIBERATELY RED"*;
- `tests/test_price_removal.py::test_nothing_in_the_repository_invokes_the_pricer`
  — the pricer grep tripped by narrative documents, whose offender list already
  names `NEXT-EPIC.md`, **the file this ticket must edit**. It was red before and
  it is red after, and **the offender list is byte-identical at both ends** —
  `['CLOSE-THE-LOOP-EPIC.md', 'NEXT-EPIC.md']`, measured rather than asserted.
  `test_card_has_one_home` is **green at the final tree** even though this
  ticket's finding quotes the D3 caveat verbatim; that was checked, not assumed.

### 12.1 `scope` over SV-05's own documents — and the bound fires again

| tree | counted | REFUTED | COUNT-MOVED | HOLDS | UNREACHABLE |
|---|---|---|---|---|---|
| `71ce81a` + SV-05's predictions only | 97 | 75 | 0 | 2 | 20 |
| **final tree** — RESULT, findings, `NEXT-EPIC.md` | **102** | **80** | 0 | **2** | 20 |

**SV-05's documents add 5 counted figures and all 5 are REFUTED**, including one
in this page at `RESULT.md:542`. **Every one of them is a figure this ticket
quotes IN ORDER TO DOCUMENT ITS REFUTATION** — the same `56 of 63` that §11
reports as newly refuted.

**That is a second instance of the bound `SV-02` escalated**, on the same figure,
one ticket later: `scope` cannot distinguish a figure a page *asserts* from one
it *quotes in order to correct*. **SV-02 worked around it by spelling the
denominator in words and named the workaround. I did not work around it**, and
left the quotation intact, because a page about `SV-05-DF-04` that hides its own
REFUTED row is arguing the opposite of its own finding.

**The third red the epic opened with is gone** because the owner repaired it at
`2059500` with a pointer, not because any ticket touched it. **The work order
this ticket was dispatched under says "2 failed"; at `a527305` it was 3, and two
tickets found that independently.** The number is right *now*, for a reason that
happened during the epic.

### The plan schema — and the epic ran on the wrong validator

The work order says `git-epic-workflow` was updated mid-epic (`4e6fcd7`) to
require a plan-level `schedule_revision`, that the epic plan was fixed, and that
**`close-the-loop`'s plan on `main` is INVALID against the new validator**.

**`P26` held — and the fact is bigger than stated:**

| validator | bytes | `main`'s `close-the-loop` plan | this epic's plan |
|---|---|---|---|
| **per-checkout home** (`.skill-manager/`, what every ticket agent ran) | 27,926 | **OK** | OK (4 goals, 7 tickets) |
| **operator's global home** (`~/.claude`) | **47,433** | **INVALID — `schedule_revision must be a positive integer`** | OK (**7 tickets, 0 retired**, 4 goals) |

**Two homes, two validators, 19,507 bytes apart, disagreeing about whether
`main`'s plan is valid.** `wt new` snapshots a Skill Manager home at
worktree-creation time; the operator's home moved during the epic and the
snapshots did not. **3 of the 6 surveyed skill files differ between the two
homes**, including `goals-and-evaluation.md` — the file SV-06 surveyed, SV-03 cut
its diffs against, and this ticket's blind 2×2 was built from.

**So `main`'s plan is invalid, the epic's own plan was repaired for a rule its
own tickets' validator never enforced, and the surface this goal was designed
against is a snapshot rather than the installed text.** It is not any ticket's
regression. `SV-05-DF-03`.

---

## 13. Cost and channel — with the basis named, and the third consecutive lapse

### 13.1 Did the tickets record theirs? One of six.

**`P21` held exactly.** The string `token` appears in **one** RESULT page in this
epic — `SV-01` §12, which recorded `subagent_tokens` with the basis named
*because it had read `CL-04-DF-02` and chose to*. **SV-02, SV-03, SV-04, SV-06
and SV-07 recorded none** — including **SV-04, which dispatched four blind
judges** and reported no token figure at all.

**That is a third consecutive epic of near-total lapse, and the cause is exactly
what `CL-04-DF-02` diagnosed: nothing asks.** `ticket_plan.yaml`'s
`acceptance.assertions` do not require it, the close-out path does not require
it, and the only artifact that demands it is the evaluation ticket's dispatch —
**which arrives after the other tickets' spend is gone.** CL-04's proposed
repair — a required `cost` block with `basis` and `value` at ticket close-out —
**was never implemented.** Not re-filed; it is `CL-04-DF-02` unchanged, and it is
escalated in §16.

### 13.2 This round's own, with its basis

**Basis:** `subagent_tokens` as reported by the four blind-agent dispatches,
summed. **Composition of that field is undocumented.** The operator's own spend
is **not** captured by it and is missing — the same bound `RM-05`, `CL-04` and
`SV-01` reported.

| channel | findings | `subagent_tokens` | per 100k |
|---|---|---|---|
| **the four blind agents** | **2** (`DF-02`, and the skill-surface escalation) | **353,816** | **0.57** |
| operator running the shipped instrument | 2 (`DF-01`, `DF-04`) | not captured | — |
| operator re-reading a predecessor's output | 1 (`DF-05`) | not captured | — |
| the suite | 0 | not captured | — |

**Comparable to `SV-01`'s 0.98 — same basis, same epic, same field.** It is the
first time in this programme that two rounds have used the same named basis, and
it is the whole point of naming one.

**Not comparable** to `CL-04`'s 0.98, `RD-03`'s 1.14 or `SM-05`'s 0.60.

### 13.3 The epic's 26 findings by channel

`CL-04` filed the structural defect that makes this expensive: **the ledger has
no `channel` field**, so the signal exists only as free text inside `found_by`.
**Still true, six epics after it was first asked for.** The classification below
is mine, from `found_by` plus each ticket's own attribution, and is a judgement
call on 26 rows.

| channel | findings | ids |
|---|---|---|
| **blind judges** | **8** | `SV-01-DF-01/02/03/05`, `SV-04-DF-01/02/03/04` |
| census over the sealed record or the plans | 8 | `SV-02-DF-01/03`, `SV-03-DF-01/02/03/04`, `SV-06-DF-01/03` |
| operator doing the work / reading | 5 | `SV-01-DF-04`, `SV-03-DF-05`, `SV-06-DF-02/04/05` |
| operator running a shipped instrument they did not build | 3 | `SV-02-DF-02/04`, `SV-07-DF-01` |
| **the suite** | **2** | `SV-02-DF-05`, `SV-04-DF-05` |
| **total** | **26** | five tickets at their budget of 5, `SV-07` at 1 |

**The suite went from 0 last epic to 2, and the mechanism is the one `RM-05`
named and `CL-04` predicted forward: it produces findings exactly when somebody
is funded to read it.** `SV-02` was told to baseline the suite at the branch
point and found the undeclared third red; `SV-04` shipped a defect and the suite
caught it 21 minutes later while **four gates in the round's own toolchain
reported clean**. **Two epics running, that causal claim has made a forward
prediction that came true.**

**Blind channels produced 8 of 26 — the largest single channel, and the first
epic where they lead.** `CL-04`'s epic had 7 of 11 from an operator doing
ordinary work.

**Three tickets hit the budget of five and escalated rather than file a sixth**
(`SV-02`, `SV-06`, `SV-04`). `P22` held on both halves — 26 findings, in the
predicted 25–32, and three spent budgets.

### 13.4 The shipped toolchain, counted separately — and `P23` falsified

**Rule, stated so it is reproducible:** a finding touches the shipped toolchain
if its `surface:` block names a path under `scripts/`, `spec_double_compiler/`,
`templates/`, `skill-scripts/`, or root `SKILL.md`. That is `CL-04`'s definition.

| | this epic | whole ledger at `71ce81a` |
|---|---|---|
| **narrow rule (CL-04's)** | **1 of 26** | **10 of 205** |
| … of which under `scripts/` | 0 | 9 |
| … of which root `SKILL.md` | **1** | **1** |
| **CL-04's own caveat applied** — `examples/validation/*`, the instruments this programme actually runs | **4 of 26** | **86 of 205** |

**`P23` is falsified by one row, and the row matters.** `SV-06-DF-04` names root
`SKILL.md` — *"`SKILL.md:1337` ships a description of a five-dimension card that
the checker refuses"*, verified at my tree: line 1337 still reads
*"THE EVALUATION RUBRIC. Five judged dimensions"*, at a tree serving two.
**`CL-04` measured `spec_double_compiler/`, `templates/`, `skill-scripts/` and
root `SKILL.md` at zero finding surfaces across six epics. This is the first.**

**And the two-epic zero on shipped BYTES is broken.** `P24` held:

```
git diff --stat eab2883 71ce81a -- scripts/ spec_double_compiler/ templates/ skill-scripts/ SKILL.md
 scripts/candidate_note_bar.py | 281 ++++++++++++++++++++++++++++++++++++++++++
```

**281 lines, one file, and nothing adopts it** — SV-07 shipped a generator that
derives the candidate bar from the card at run time, and the shortest test in its
file asserts that nothing imports it. **Three epics of zero bytes ends with a
tool that is deliberately inert.**

---

## 14. The full prediction table

| | prediction | outcome |
|---|---|---|
| P1 | `serve` 6,281 / 9 rungs, card untouched | **HELD** |
| **P2** | `--digest-only` is not a flag | **FALSIFIED** |
| **P3** | 5 distinct digests v1–v5; an earlier version serves >9 rungs | **FALSIFIED, both halves** |
| P4 | 95 cards, 95 filled, 330 problems | **HELD**, exactly |
| P5 | `audit` 0 violations, no new contested dimension | **HELD** |
| P6 | suite 2 failed, and the two named | **HELD** — 2 failed, 1528 passed |
| P7 | 1,530 collected at `71ce81a` | **HELD** |
| P8 | SV-05 adds 0 collected and no red | **HELD on both** — 1,530 at both trees, offender list byte-identical |
| P9 | all four SV-01 cards `D3 = 4` read from JSON; v5 rationales test the caveat | **HELD** |
| P10 | caveat discriminates, discounted not withdrawn | **HELD** |
| P11 | validation scorable; carrier claim refuted | **HELD** |
| P12 | diagram zero holds at 95 cards | **HELD** — 0 sentences, 0 cards |
| P13 | D1 ≈ 37%, D4 ≈ 17% within a point at 95 cards | **HELD** — 37%, 17% |
| P14 | 0 of 18 openable, 12 of 27 dimension-keyed, unchanged | **HELD** |
| P15 | all four patches still apply cleanly | **HELD** — and to both homes |
| P16 | M1 reproduces; `JF-5` reproduces 70/70 green | **HELD**, both halves |
| P17 | absence guarantee holds in both no-card arms | **HELD** |
| **P18** | only the patched judged arm names a specific card | **FALSIFIED — both did** |
| P19 | ≥1 agent reports a rejection; ≥1 discloses contamination | **HELD — 4 of 4 on both** |
| P20 | ≥1 agent finds a blocker in the installed text no ticket named | **HELD — 4 of 4, same two** |
| P21 | exactly one ticket recorded a token basis | **HELD** |
| P22 | 25–32 findings; ≥3 spent budgets | **HELD** — 26 and 3 |
| **P23** | 0 shipped-toolchain findings this epic | **FALSIFIED — 1, and it is a first** |
| P24 | the shipped-bytes zero is broken | **HELD** — 281 lines |
| P25 | 1 harvest class consumed; ≤6 filed | **HELD** — 1 consumed, 4 named |
| P26 | the current validator rejects `main`'s plan | **HELD**, and the skew is worse |
| P27 | ≥3 falsified | **HELD — 4.** The alarm did not fire, by one |

---

## 15. What this result does NOT establish — read before quoting it

1. **`n = 1` everywhere that matters.** One artifact for the negative control,
   one artifact for the loop closure, one judge model (`claude-opus-5[1m]`) on
   all eight of this epic's cards, one fictional project per arm in the blind 2×2.
2. **The blind 2×2 is one agent per cell.** Four cells, four agents, no
   replication. A second agent in arm A might not have mis-routed, and the whole
   of §5.3 turns on one agent's choice of branch. **It is a signal, not a rate.**
3. **Every blind agent in this round was contaminated before it started** (§5.4),
   including the ones whose output §5.3 rests on. They disclosed it; I did not
   discard them, because discarding an agent after reading its answer is the one
   move a round may not make.
4. **My blind arms were labelled `arm-A` … `arm-D` and one agent noticed**, and
   said so: *"my own assigned path discloses that this task is one blind arm of a
   comparison."* SV-04 drew labels from a pool excluding published labels; **I
   did not, and that is this round's own blinding defect** (§16).
5. **The consumption figure of 1 counts one class.** It does not show that a
   conformance suite is the right carrier for any other class, and the file that
   consumed it shipped a false claim about itself.
6. **The `scope` movement in §11 is a fact about a text-matching checker**, whose
   bounds `RD-02-DF-01` and `RM-02-DF-05` already record. It refutes claims by
   re-deriving denominators; it cannot tell an assertion from a quotation.
7. **I read all six RESULT pages before sealing predictions.** §2.1.

---

## 16. What SV-05 REJECTED

- **Running SV-07's both-wordings judging round.** SV-07 §6 leaves it here.
  **Refused, and the refusal was sealed before measuring**: cards scaffolded
  against the candidate bar record a served digest for a **card version 6 that
  does not exist in the card** — and `serve --card-version 6` refuses outright
  (§11), so the round would have to be run through `--rubric`, permanently adding
  drift rows to the record whose comparability is the thing the change rule
  exists to protect. It decides **none of the four goals**. Handed to
  `NEXT-EPIC.md` with the hazard named.
- **Repairing anything.** Both inherited reds; `RESULT-SV-04.md`'s two unfilled
  placeholders; `main`'s invalid plan; `SKILL.md:1337`; the card file's now-refuted
  figure; every blocker four blind agents returned.
- **Applying SV-03's four diffs to any `SKILL_MANAGER_HOME`.** They were applied
  to a **copy** so the counterfactual could be measured. Both homes were hashed
  and are unchanged. `skill-manager sync` was never run.
- **Discarding a blind agent after reading its answer**, including the one that
  falsified `P18` and the one that told me my own labels leaked.
- **Widening the shipped-toolchain definition to make the number bigger.** The
  narrow rule is `CL-04`'s and is kept; the wider figure is reported beside it,
  labelled, exactly as `CL-04`'s census did.
- **Averaging anything.** `R-H1`/`R-H2`. SV-01's v4 and v5 arms are two cells;
  SV-04's `GL` and `LG` are two cells; the four blind agents are four cells.
- **Editing `ticket_plan.yaml` to mark SV-05 `done`.** The plan is **outside this
  ticket's `implementation_scope`** (`specs/results/scorecards/`, `NEXT-EPIC.md`).
  The row stays `planned` and the owner is told so here rather than the scope
  being widened quietly.
- **Reporting a `git archive` figure as a tree property.** None appears.
- **Filing a sixth finding.** The budget is five and it is spent; three
  escalations are below, on `RM-02`'s precedent.

### Escalated rather than filed — the budget of five is spent

1. **`CL-04-DF-02` is unrepaired and this is its third epic.** One ticket of six
   recorded a token basis. The proposed repair — a required `cost` block at
   ticket close-out — was never built. **Not re-filed**; it is the same finding.
2. **Four of four blind agents independently found two defects in the installed
   skill text that no ticket in this epic named**: `harness:` holds a ticket id
   where the schema asks for the instrument, and `tickets: []` leaves a plan
   failing conditions the validator calls errors. Skill surface; this repository
   may not edit it.
3. **`RESULT-SV-04.md` §9 ships two unfilled placeholders** — a suite row reading
   `SUITE_AFTER_REPAIR` at tree `REPAIR_SHA`, in a sealed evaluation record, past
   a close-out that did not catch it.
4. **This round's own blinding defect**: arm labels `arm-A`…`arm-D` disclosed to
   at least one agent that it was one arm of a comparison.

---

## 17. Findings filed — five, none repaired

| id | severity | what |
|---|---|---|
| `SV-05-DF-01` | **major** | **`serve --card-version N` silently serves the wrong card.** v4 and v5 are byte-identical; v1–v3 render at 9 rungs when those versions scored five dimensions; only v6 refuses. A round using the flag records the current served digest under an old version label and `check` accepts it. This is the mechanism behind `FI-06-DF-11(c)`. |
| `SV-05-DF-02` | **major** | **The operator's auto-memory and environment block are in every subagent's context before it reads anything**, naming epics, outcomes and *"up to 2 points per judge move on byte-identical artifacts"*. 4 of 4 blind agents disclosed it unprompted. It requires no tool call, so no forbidden list reaches it, and it applies to every blind round this programme has run. |
| `SV-05-DF-03` | **major** | **Two Skill Manager homes, and the epic ran on the older one.** `wt new` snapshots a home; the operator's moved during the epic. 3 of 6 surveyed files differ; the two `validate_epic_plan.py` differ by 19,507 bytes and **disagree about whether `main`'s plan is valid.** |
| `SV-05-DF-04` | moderate | **This epic's own eight cards refuted four claims that previously held**, one of them in the shipped card file (`references/eval_scorecard.md:42`) and one in a page written this epic. The record is down to **2 HOLDS of 97 counted**, and `serve \| wc -c` did not move by a byte. |
| `SV-05-DF-05` | moderate | **`GOAL-scored-at-goal-time`'s gap is not where the epic said it was.** A blind stranger reading the **unpatched** text produced a card-backed, sealed, per-judge baseline; the diffs buy the **timing**, not the card. SV-06's *"buys the whole of the target"* is corrected, and the 0-of-18 compliance rate is this project's, not the documentation's. |
