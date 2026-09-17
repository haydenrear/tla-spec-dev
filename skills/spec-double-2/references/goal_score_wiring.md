# Wiring the score into the goal process

**SV-06 research output. No production code, no skill edit, and no byte added to
`serve`.** Its job is to scope SV-03 and rewrite SV-07, and the way it does that
is by reading the files the epic charter named before proposing anything. There
turned out to be six of them rather than four, and they turned out to be almost
entirely right already.

**Scope, stated first (`R3`).** Every count below is over **this repository's own
plans and the installed Skill Manager home, at tree `a527305`**. Re-derive all of
them in about a second:

```
uv run --with pyyaml python3 \
  specs/results/scorecards/score-drives-validation/GOAL-scored-at-goal-time/SV-06/analysis/goal_score_survey.py
```

Nothing here is a figure about skills in general, about other projects, or about
adopters. Where a figure is about this repository it says so.

---

## 1. The answer

**The wiring already exists. It is populated in prose twelve times over and has
never once been populated with a score, and the hole is one branch of one
section of one file.**

The epic's baseline for `GOAL-scored-at-goal-time` says *"NO GOAL HAS EVER BEEN
KEYED TO A DIMENSION."* Measured against the plans on disk at `a527305`, that is
false and not marginally so. Of **27 distinct epic goals** in this repository's
live and sealed plans, **12 name a scorecard dimension** in their statement,
metric, harness or target. `GOAL-D2-can-move` is the clearest: its metric is
*"D2 scored by two blind judges on the toolchain's removal, before against
after, per judge"*, its baseline is a card figure, and its target is *"D2 reaches
3 or more"*. That is a goal keyed to a dimension, declared before the work,
decided by an evaluation ticket, in a plan this project shipped one epic ago.

What has never happened is different, sharper, and it is the thing worth
building:

> **Of 27 goals, ZERO have a `baseline.evidence` that points at a sealed card.**
> There are **87 sealed `scorecard.json` files** in this repository. Not one of
> them is cited as the baseline of any goal. All 25 distinct `baseline.evidence`
> values are a directory, a `RESULT.md`, a `SELF-IMPROVEMENT.md` line range, or
> a reference page.

`git-epic-workflow/references/goals-and-evaluation.md` already asks for exactly
this, in as many words: *"A judged baseline is a prior scored run, not a
recollection. `baseline.value` cites the sealed card that produced the number and
`baseline.evidence` points at it."* **The hook is there, it is correctly worded,
and its compliance rate in the project that wrote it is 0 of 27.**

So the gap is not *"nothing reaches the scorecard"*. The gap is that a goal
**describes** a score and never **is** one. The evaluation ticket runs the card
and compares its number against a paragraph.

**The whole of the fix is a third branch in one section**, and §7 spends the rest
of this page saying so in the fewest edits that can carry it.

---

## 2. What already exists, reported before anything is proposed

### 2.1 `git-issue-workflow/references/goal-signal.md` — the implementer's half

290 lines, and it is complete. It defines the goal signal today as:

- a per-ticket contract of five things — the goal, the contribution kind, the
  expected effect, a cheap local signal, and who decides it for real;
- an order of operations that puts **reading the expected effect before the first
  edit**, with a stated reason (*"a ticket agent who implements the slice and
  reads the goal afterwards has already made every design choice without it"*);
- a precedence table that is the load-bearing part: **the validation matrix
  decides the ticket, the local signal decides nothing, the evaluation ticket
  decides the goal**;
- four reportable classifications, of which *"no measurable movement"* is
  explicitly one;
- a `role: evaluation` section with a subsection titled **"When the instrument is
  judged rather than executed"** that names `tla-spec-dev` by name, quotes this
  project's own reason for judging (*"A number computed from the artifact can be
  optimized by editing the artifact"*), and states three rules it says are the
  instrument's and not the skill's: the card is **scaffolded from the rubric,
  never hand-written**; blinding, sealing and comparability are the instrument's
  rules; and **a judged number can move on unchanged input**, so a movement
  inside a documented noise band is not a result.

**Nothing in it needs to change to make a goal scorable, and one paragraph should
be added to stop the wrong thing being built.** See §4, seam 5.

### 2.2 `git-issue/references/regression-close.md` — the loop's consumption path

231 lines. §1–§4 name the graphs, attach reports to the spec ticket, close it
through `tla-spec-dev`, and require both test layers green. §5 is the
`## Goal contribution` half — the author-side mirror of `goal-signal.md`, and the
two files say so about each other in their closing paragraphs. §6 commits, §7 is
the Skill Manager home gate.

Two things matter for this ticket:

- **§5 already routes a judged instrument correctly**: *"Where the deciding
  instrument is a judged one, its own documentation governs how the result is
  produced, sealed, and compared… Cite it and follow it; this skill restates none
  of it. For `tla-spec-dev` that is `references/eval_scorecard.md`."*
- **§1 is where the loop's consumption step belongs, and it is empty of it.** §1
  asks the implementer to name the graphs that cover the changed surface. A
  validation artifact that exists *because a judge's recorded note named a gap*
  is a graph named at §1 — there is no other place in any of the six files where
  a concrete test, graph or adapter is named as an outcome. The epic's measured
  bottleneck is that **nothing consumed a filed finding**; §1 is the consumption
  step and it does not know findings exist.

### 2.3 Verdict on both

**The hooks exist and nothing populates them**, and the two hooks fail in
opposite ways:

| hook | state |
|---|---|
| `goals-and-evaluation.md`'s judged baseline | correctly specified, **0 of 27 goals comply** |
| `goal-signal.md`'s judged-instrument section | correctly specified, **and correctly used** — this project's evaluation tickets do run it |
| `regression-close.md` §5 goal contribution | correctly specified and used |
| `regression-close.md` §1 as the loop's outlet | **not specified at all** |

---

## 3. The confirmed surface

The charter says *three skills and four files*. **Three skills is right. Four
files is two short.**

| skill | file | what it carries |
|---|---|---|
| `git-epic-workflow` | `references/goals-and-evaluation.md` | goal schema, baselines, the judged-instrument section, finalization |
| `git-issue-workflow` | `SKILL.md` | one line naming a judged rubric in the evaluation role |
| `git-issue-workflow` | `references/goal-signal.md` | the implementer's half (§2.1) |
| `git-issue` | `SKILL.md` | the `## Goals & evaluation` template; **"an issue names a rubric; it never copies one"** |
| `git-issue` | `references/discovery.md` | the **measurement inventory** — asks whether a judged instrument exists before a goal is written |
| `git-issue` | `references/regression-close.md` | the close-out and consumption path (§2.2) |

`git-issue/references/discovery.md` is the one the survey missed that matters. It
is the seam where an author asks *"what instrument decides this?"* **before** the
goal is written, and it already answers correctly: *"an artifact scored against a
versioned rubric by judges who cite it is an instrument, and in some repositories
it is the better one."* It needs nothing. It is reported because the baseline
figure of "four files" is sealed at `eab2883` and is wrong.

### `spec-double-compiler` is this repository, installed

Confirmed rather than assumed. The installed unit at
`$SKILL_MANAGER_HOME/skills/spec-double-compiler/` carries `.git`, its top-level
listing is this repository's listing, its `SKILL.md` head is byte-identical to
this repository's, and **its `references/eval_scorecard.md` is byte-identical to
this repository's copy at `a527305`**. Its matches are 979 files carrying about
20,000 occurrences of `scorecard`, and they are `specs/results` (468 files) and
`specs/.history` (433 files) — the sealed record — plus `examples/validation`
(52).

It is **not an integration point** and correctly out of scope. One correction to
the charter's wording: it is not a *bundled copy of the record*, it is **the
whole repository shipped as a skill unit**, live card and tooling included. That
distinction is not pedantry — it means the card already reaches an adopter
through a skill install today, with no wiring at all, which is why §6 can promise
so much and change so little.

---

## 4. Where the score belongs in the lifecycle

Eight seams. Two are right, one is right for a different payload, and the rest
are wrong — one of them dangerously.

**Seam 1 — the epic goal is agreed with the user. RIGHT, and this is what
"during the goal process" means.** `goals-and-evaluation.md` already tells the
epic owner to ask for *"the instrument that decides it — a command, or a judged
procedure with its rubric"*. A goal whose harness is the card is already legal
here and has been written twelve times.

**Seam 2 — the epic baseline is measured at kickoff. RIGHT, AND IT IS THE HOLE.**
The Baselines section has exactly two branches: *harness exists* → measure at
kickoff before any ticket lands; *harness does not exist* → schedule a wave-1
ticket to build it and measure. **A judged instrument that exists but has never
been run on this subject is in neither**, and the file's judged-baseline
paragraph only tells you how to cite a *prior* run. So an epic whose subject has
never been scored has no branch to follow, and the 0-of-27 figure is what
following no branch looks like. **This is the seam. Everything else in this
design is downstream of it or is a subtraction.**

**Seam 3 — issue authoring (`git-issue/SKILL.md`, `references/discovery.md`).
RIGHT and already correct.** The measurement inventory asks for the instrument;
the template has `Metric / harness` and `Baseline → target`; and in epic mode the
file already says these *"are not asked for at all — they are copied from the
epic's canonical plan"*. An issue is a **copy** of a goal, not a place a score is
produced. Nothing to add. Adding anything here would put a second statement of
the goal beside the plan's, which is the copy-with-nothing-behind-it failure all
three skills already forbid.

**Seam 4 — ticket start. RIGHT for reading, WRONG for scoring.** `goal-signal.md`
already requires the expected effect to be read before the first edit, and a
sealed baseline card is exactly the sort of thing that belongs in that read. But
scoring at ticket start scores a tree that is mid-epic and therefore not the tree
the baseline was measured on.

**Seam 5 — ticket close, as a local signal. WRONG, and it is the seam a reader of
"score during the goal process" will reach for first.** Three reasons, each
measured in this repository:

1. **Cost.** This project's own rounds are four fresh judges per version
   boundary (`SM-04`) and twelve for a three-artifact round (`FI-03`). Per
   ticket, that is the epic's judging budget spent on advisory numbers.
2. **Noise exceeds the signal.** The instrument's own documentation warns that
   *"a judged number can move on unchanged input"*, and this repository has
   measured the band. One ticket's movement sits inside it.
3. **Comparability.** `R-H1` and `R-H2` make a number comparable only on the same
   example across an unchanged instrument. A per-ticket card is a different
   subject state each time; a column of them is a column of incomparable numbers
   that will nonetheless be read as a trend.

`git-issue/SKILL.md` already carries the author-side half of this: *"A judged
instrument is rarely the right local signal: judging is expensive, and a rubric's
own noise can swamp one ticket's movement."* **The implementer-side mirror is
missing, and those two files are required to mirror each other.** The correct
`local_signal` for a judged goal is `N/A: <reason>`, which is already a
first-class answer everywhere.

**Seam 6 — ticket close, as the loop's outlet (`regression-close.md` §1). RIGHT,
for a different payload.** Not a score — a **finding**. A judge's recorded note
(`N-D1` asks *"what class did the cases demonstrably miss"*) names a gap; the
answer to that gap is a named regression graph or test at §1. This is the only
place in the six files where a concrete validation artifact is named as an
output, and it is the seam `SV-04` will exercise.

**Seam 7 — the evaluation ticket. RIGHT and complete.** `goal-signal.md`'s judged
section is the most finished thing in the surface. Nothing to add. Once seam 2
puts a card path in the baseline, the sentence *"reports baseline → measured →
target"* becomes card-against-card instead of card-against-paragraph, with no
edit at all.

**Seam 8 — finalization. RIGHT and complete.** One row per clause, verdicts
`met` / `missed` / `unmeasured`, and an explicit provision for a goal whose
target is deliberately not a number.

### The shape of the answer

**The card runs at the two ends of an epic and nowhere in between.** That is not
a convenience. It follows from `RM-02`'s own strongest conclusion, which it
stated inside a costing list rather than as a constraint: **the card is an
instrument for changes, not an instrument for code.** An instrument for changes
is run at the two ends of a change. An epic *is* the change; a ticket is not, and
that is why seam 5 is wrong on principle and not only on budget.

---

## 5. What crosses a skill boundary, and what cannot

The question is not "what would an adopter have to copy" — that is `RM-02`'s
question. It is narrower: **what can a skill that does not own a rubric write
down about a score?**

### Crosses

| carried thing | why it crosses |
|---|---|
| **A path to a sealed card** | An opaque string to the skill, resolvable by whoever owns the rubric. This is the whole of the proposal. |
| **A rubric identity and version** | Already required by all three skills — *"write which rubric, which version, how many judges, and where the evidence lands, then link the rubric."* |
| **A judge count and a blinding statement** | Facts about a procedure, not about a rubric. |
| **The verdict vocabulary** — `met` / `missed` / `unmeasured`, one row per clause | Already shared across all four reporting sites. |
| **The refusal to compare across an instrument change**, as a *rule* | Already stated in `goals-and-evaluation.md`: *"say so and treat the movement as a fact about the instrument until proven otherwise."* |

### Cannot cross

| carried thing | why not |
|---|---|
| **A dimension id (`D2`, `D3`)** | It is an index into **one project's rubric file**. This card's D2 is complexity at version 5 and was something else at version 3; an adopter's D2 is whatever their §"The anchors" says. A skill schema with a `dimension:` field has exported a local key into a vocabulary three skills share, and the first adopter whose card has four dimensions named A–D breaks it. **Dimension keying belongs in the goal's free-text `metric`, where 12 goals already put it.** |
| **A served digest** | A hash over bytes only that project's `serve` produces. It is *within-project* comparability machinery; a skill storing it stores a string it can never check and invites a cross-project comparison the digest cannot support. |
| **An era boundary** | `R-H1` executes as *"every declared change must name a commit that resolves and that actually touched one of its declared instrument paths."* Commits and instrument paths are one repository's. **The rule crosses; the boundary does not.** |
| **A `[[demonstration]]` refusal authority** | Re-derived from that project's own cards on every `audit`, and therefore empty for every adopter on day one. |
| **A subject declaration** | **Split.** The *requirement* to declare a subject crosses and should — `RM-02` measured it as the cheapest high-value item in the substrate, on the round where four judges handed one undeclared subject scored three different ones. The *syntax* (`subjects.toml` scopes) does not. |

### Where `RM-02`'s irreducibly-local list was wrong

`references/portable_scorecard.md` §2 lists six items. It is prior art and it is
good, and four corrections apply once the reader is a skill rather than an
adopter.

1. **Its axis is not this axis, and on this axis it is nearly inverted.**
   `RM-02` asked *what can an adopter copying `score_tools.py` not use*. Its
   largest item — `scripts/analyze_complexity.py`, 2,401 lines — is completely
   irrelevant to the goal process; no skill would ever name it. Meanwhile the two
   things that most clearly cannot cross a skill boundary, **the served digest
   and the era boundary**, appear nowhere on its list. A tool-portability
   inventory is not a vocabulary inventory, and the goal-process question needed
   the second.

2. **Item 4 is right, and `RM-02` did not generalise it.** Of the
   `[[demonstration]]` table it says *"It cannot be handed over; only the rule
   can."* That rule/table split is the correct answer for **every** comparability
   mechanism in the card — `R-H1`'s era boundary and `R-H5`'s `readable` flag
   have the identical structure and neither is listed. `RM-02` found the general
   principle once and filed it as one item.

3. **Item 1 is obsolete and the page still ships it as current.** It names D1
   anchor 4, D4 anchors 3 and 4, and D2 anchor 4's D4 gate as *"not expensive —
   unreachable"*. At version 5 **D1 and D4 take no score at all**, D2's top
   anchor is 3, and D2's preamble now reads *"where none exists that is not a gap
   in the evidence"* — which is precisely the change §5 of that same page asked
   for. The top item of the irreducibly-local list was fixed by the epic that
   followed it, and a reader arriving today (including this ticket's own work
   order) inherits it as live. Filed rather than edited: a predecessor's
   statement at a predecessor's scope is not rewritten to match a successor's
   finding, which is the rule `RM-02` itself applied to `architecture_tags.md`
   §2.2.

4. **It is a list of things where a boundary needs a list of statements.** What
   crosses is a path, a version, a judge count and a verdict word. `RM-02`'s
   inventory has no row for any of those, because it never asked who the reader
   is. That omission is the correction that decides SV-07's shape: because the
   carried things are all statements a skill can already make, **SV-07 adds no
   field.**

---

## 6. A project with no card, designed for first

This is the constraint the epic states most loudly — *"any proposal that makes
the card mandatory anywhere fails this goal"* — and it is satisfied structurally
rather than by care.

1. **Every proposed sentence lives inside a conditional that already exists and
   is already opt-in.** Seam 2's new branch is inside *"where the instrument is a
   judged one"*; seam 5's paragraph begins *"for a goal whose harness is
   judged"*; seam 6's sentence begins *"when the deciding instrument records
   notes"*. A project with no rubric never enters any of them and reads them as
   three sentences about somebody else's instrument, next to the sentences about
   somebody else's instrument that are already there.

2. **No field is added anywhere, so no field can be missing.** §5 item 4 is the
   reason. The proposal reuses `harness`, `metric`, `baseline.value` and
   `baseline.evidence`, all four of which already exist, are already free text,
   and already have a sanctioned empty answer.

3. **No validator change, measured.** The epic plan validator was run on this
   epic's plan at `a527305` and again on a scratch copy carrying an invented
   `scored_by:` block on a goal and a `score_signal:` on a ticket-goal link. Both
   exit 0 with the same message: the schema reads named fields and ignores
   unknown ones. **That experiment is reported because it is the argument for
   NOT adding the field** (§8) — but it also proves the converse, which is what
   matters here: a plan with no scoring block validates today, unchanged, and
   will validate identically after SV-07.

4. **No new gate, no new check, no new warning.** `epic_goals: []` with
   `goals_waived:` remains a warning that does not block. Seven epics of static
   checking caught zero bugs, and this design ships no eighth.

5. **The strongest guarantee is that no skill file gains a scorecard
   vocabulary.** After SV-07, the only artifact in the world that names `D3` is
   the project's own plan file. There is nothing for an adopter to ignore, no
   term to look up, and no dead field to leave blank.

**The test SV-05 should run**, in the shape `CL-04` used: hand a blind agent the
six files after SV-07 lands, plus the plan of an epic that declares no judged
harness, and ask it to run the goal process end to end. **If it asks what rubric
to use, the design failed.** A pass is that it never notices the sentences.

---

## 7. The hand-off to SV-07

Five entries, in dependency order. **Byte cost to `serve`: 0 on every one** —
none touches `references/eval_scorecard.md`, so the served text stays **6,281
bytes and 9 rungs** at `a527305` (D2's four rungs 0–3 plus D3's five rungs 0–4).
**No anchor is added, so nothing permanent is created.**

### 1. `git-epic-workflow/references/goals-and-evaluation.md`, §Baselines — the third branch

The section has two branches and a judged instrument on a never-scored subject
falls between them. Add the third, roughly four sentences:

> **Harness is judged and the subject has never been scored under it** — run the
> instrument at epic kickoff on the epic branch, before any ticket lands, exactly
> as for a command harness. Seal that run and record its card as the baseline.
> This is the only way the evaluation's number has anything to compare against;
> a baseline written as prose about prior rounds cannot be re-read by the
> evaluation ticket, and cannot be re-derived later.

**Buys:** the entire `GOAL-scored-at-goal-time` target. This is the one change
that moves the goal from `unmeasured` to measurable, and everything below is
either downstream of it or a subtraction. **Do this one first and alone if the
budget is one change.**

### 2. Same file, same section — `baseline.evidence` is a card, not a directory

One sentence, tightening a rule the file already states:

> For a judged goal, `baseline.evidence` is the path to the single sealed card
> that produced the number. **A directory is not a card**, and neither is a
> results summary: the evaluation ticket has to re-read the exact card, and it
> cannot pick one out of a folder.

**Buys:** *"the evaluation compares against the sealed number"* stops being an
aspiration. **Evidence:** 0 of 27 goals in this repository comply with the
existing wording; all 25 distinct values are directories, summaries or reference
pages, while 87 sealed cards sit unreferenced. This is the change with the most
measurement behind it and it is one sentence.

### 3. `git-issue-workflow/references/goal-signal.md`, §"During validation" — one paragraph, and it is a subtraction

> Where a goal's harness is a **judged** instrument, a score is normally **not**
> the local signal. Judging costs several blind judges per round, a judged number
> can move on unchanged input by more than one ticket moves it, and a card scored
> on a mid-epic tree is not comparable to the baseline under the instrument's own
> comparability rules. `N/A: judging is too expensive and its noise exceeds one
> ticket's movement` is the expected answer, and it is a complete one. Read the
> baseline card before implementing; do not produce a new one.

**Buys:** it forecloses the obvious wrong build — scoring every ticket — before
SV-03 or an adopter reaches for it. It is the implementer-side mirror of a
sentence `git-issue/SKILL.md` already carries, and those two files are required
to mirror each other by `regression-close.md`'s own closing paragraph.

### 4. `git-issue/references/regression-close.md`, §1 — one sentence, the loop's outlet

> Where the deciding instrument records **notes** as well as scores, a note that
> names a gap in the changed surface is answered here: name the graph or test
> that now covers it, and say which note it answers. The score movement that
> follows is an **observation**, never the objective — validation tuned to raise
> a number is the failure the instrument's own rules exist to prevent.

**Buys:** `GOAL-loop-reaches-the-program`'s consumption step gets a home in the
skill rather than only in this repository's epic prose. It adds no checklist item
— *"Named test graphs pass"* is already there. This is the sentence `SV-04` will
exercise.

### 5. `git-issue/SKILL.md` — **recommend no change**

Its template already carries `Metric / harness` and `Baseline → target`; epic
mode already copies from the plan; and it already warns that a judged instrument
is rarely the right local signal. A clause on `Baseline → target` saying the
judged half is a card path would be a **third** statement of a rule stated twice.
If SV-05's blind agent misses it, add it then, with the miss as the evidence.

### Not changed, deliberately

- **`validate_epic_plan.py`** — measured to accept an optional block unchanged,
  and no block is being added. Zero lines of Python in the whole hand-off.
- **`git-issue/references/discovery.md`** — its measurement-inventory question
  already covers a judged instrument, verbatim and correctly.
- **`git-issue-workflow/SKILL.md`** — its one mention is a summary of the
  evaluation role.
- **`references/eval_scorecard.md`** — 0 bytes. The card does not learn about
  the goal process; the goal process learns to name a card.

### The one convention that is not a skill change

Dimension keying goes in the goal's existing free-text `metric`, in this shape:

```yaml
metric: "D3 on <subject>, two blind judges, rubric version 5"
```

Twelve goals already do this. **No `dimension:` field**, for the reason in §5.

---

## 8. What was rejected

- **A `scored_by:` block on `epic_goals[]`** carrying `rubric`,
  `rubric_version`, `dimension`, `subject` and `baseline_card`. **This was built
  and validated, not waved away**: the plan validator accepts it today, exit 0,
  byte-identical message, zero Python changed. Rejected anyway. Every one of its
  five fields is already sayable in `harness`, `metric` and `baseline.evidence`;
  four of the five are project-local; and `dimension:` in particular exports a
  local key into a schema three skills share. **Cheap to add is not a reason to
  add.**
- **A `score_signal:` field on a ticket's goal link.** Same experiment, same
  pass. Rejected: `local_signal` exists and the correct value is `N/A`. A field
  whose sanctioned value is *"don't"* is a sentence.
- **Scoring at ticket start or ticket close.** §4 seam 5 — cost, noise,
  comparability. This is the framework the epic's phrasing most invites.
- **Any new check, gate or validator rule** — including a check that a judged
  goal has a card baseline. `no_new_gates_rule`, and seven epics of evidence it
  would catch nothing. The 0-of-27 figure is an argument for a sentence, not for
  a checker.
- **A `--goal` or `--epic-goal` flag on `score_tools.py`**, and any
  `tla-spec-dev` CLI path that reads a plan. It inverts the dependency: skills
  would then need the card installed to run the goal process, which is exactly
  the failure §6 exists to prevent. The card is an instrument the goal process
  *names*, never a participant in it.
- **A shared "judged instrument" reference page** in any of the three skills.
  The framework answer, and it would be the seventh file in a surface this
  ticket has just finished counting.
- **Restating any of the card's rules in any skill file.** Forbidden three times
  over already, each citation naming the same measured failure — a charter here
  restated a table of judged results and two rows were wrong.
- **Editing `references/portable_scorecard.md` §2 item 1** to remove the
  obsolete clauses. `RM-02` refused exactly this move for `architecture_tags.md`
  §2.2. Filed instead.
- **Reporting "12 of 27 goals are dimension-keyed" as a fact about goal
  processes.** It is a fact about **this repository's plans at `a527305`**, and
  this page says so wherever it appears.

---

## 9. What this ticket could not settle

- **Whether an adopter ever reaches seam 2.** Everything above is designed
  against this repository's own record, where the operators wrote both the card
  and the epics. `SV-05`'s blind test is the only thing that decides it, and §6
  states the pass condition in advance so it cannot be adjusted afterwards.
- **Whether a baseline card at kickoff is affordable for an ordinary project.**
  This project's kickoff scoring cost is several blind judges; a project with one
  engineer may find the two-ended design costs two rounds it will not run. The
  honest answer is that the design makes scoring *possible* at goal time and says
  nothing about whether it is *worth it*, which is `SV-05`'s and the owner's
  call.
- **Whether the loop's outlet at seam 6 produces anything.** `SV-04` owns that,
  on a harvested defect. This page places the seam; it does not demonstrate that
  anything comes out of it, and 0 for 7 epics is the standing prior.

---

## 10. `scope` run over this page, and the bound that applies

```
uv run --python 3.12 python3 examples/validation/scorecards/score_tools.py scope
```

**Every row names its tree.** Run at `a527305` + SV-06, and again with this page
moved aside:

| tree | counted | REFUTED | COUNT-MOVED | HOLDS | UNREACHABLE |
|---|---|---|---|---|---|
| `a527305` + SV-06 | 93 | 68 | 0 | 5 | 20 |
| `a527305`, this page moved aside | 93 | 68 | 0 | 5 | 20 |

**SV-06's delta is zero on every column**, and `scope --path
references/goal_score_wiring.md` reports 0 counted figures. That is not a clean
bill of health and it must not be read as one: it is **bound 1**
(`RD-02-DF-01`) — every figure on this page is **invisible to the checker rather
than checked by it**, because `scope` re-derives figures of the form
`D<n> = k on N of M cards` and nothing here is one. This page counts **goals,
files and evidence values**, not cards.

So the discipline `scope` executes is owed by hand, and it is: the 27, the 12,
the 0, the 25 and the 87 are figures about **this repository's plans and record
at `a527305`** and about no wider population. They are not figures about goal
processes, about skills, or about what an adopter would find. The survey script
prints the tree it computed them over for exactly this reason.

`scope`'s exit 1 is the record's inherited state and is its demonstrated failing
input, not a defect introduced here.
