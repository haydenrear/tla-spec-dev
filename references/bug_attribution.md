# Bug Attribution

*What the record keeps about where defects come from, what caught them, and —
the part nothing has ever kept — **where nobody looked**.*

**AT-01 output. This page is read, not executed.** No script reads it, nothing
gates on it, and no exit code anywhere depends on a field described here. The
only mechanical property any of it has is that the file it lives in parses,
which `tests/test_spec_yaml_valid.py` already guards for every
`specs/**/*.y*ml` outside `.history`.

---

## 1. The problem, stated as the shape of the record

**A finding only exists where something was found.**

The cumulative ledger has **364 findings** and not one row for a place nobody
looked. The record is dense exactly where the instruments work and empty exactly
where they are blind — **and it reads the same either way.** A reader cannot
distinguish "we looked here and it was clean" from "nothing has ever looked
here", because only the first kind of place produces rows.

Three failures paid for this page, and **none of them would have been prevented
by a better finding**:

| | what happened | what no record held |
|---|---|---|
| `DEF-124` | an invariant enforced on `bin/cli` and `bin/mcp`, unenforced on `skills/`, `plugins/` and the agent dirs | **the second list.** Three live homes, eight days after the fix |
| `DEF-115` | a node green for weeks; every fixture planted a wrapper and repair cannot read a symlink | **that green meant *could not look*** |
| budgets | `gate_passed: False` on **16 of 16 runs**, nothing stopping | **a price declared before**, so the measurement had nowhere to land |

---

## 2. Four record kinds

| kind | direction | the question it answers |
|---|---|---|
| **CATCH** | backward, from a failure | A regression happened. What caught it, what area was it in, what pins it now? |
| **REACH** | forward, from a rule | An invariant exists. Which surfaces enforce it — **and which do not**? |
| **BLIND** | forward, from a green | A case passes. What could it **never** have caught? |
| **PRICE** | forward, from a proposal | A change was proposed. What was it priced at **before** — and what did it cost? |

**CATCH is the only one indexed by a failure.** The other three are the negative
space, and they are the reason this page exists.

---

## 3. THE RULE THAT MAKES REACH AND BLIND WORTH ANYTHING

**An empty unenforced-list and an empty blind-spot are CLAIMS. They are never
defaults.**

This is `DEF-124` and `DEF-115` in one sentence. A REACH saying *"enforced
everywhere"* and a BLIND saying *"this case could have caught anything"* are the
two most dangerous rows either kind can carry: they read as maximum coverage and
cost nothing to write.

Both are therefore governed by the rule `SS-02` already landed for absent inputs:

> **The correct answer to an absent input is UNDECIDED or a refusal — never
> PASS.**

Applied here:

- *"I did not enumerate the surfaces"* → **`unenforced: UNDECIDED`**, with the
  reason.
- *"I enumerated them and found none uncovered"* → **a claim**, and it names
  **how** it enumerated.

**These must never be written the same way.** A record that cannot tell them
apart has shipped `SS-02`'s class in a new field, and it will read as coverage
for however long it takes the next `DEF-124` to arrive.

---

## 4. CATCH — the channel, the area, the pin

A CATCH is an ordinary finding in `specs/deferred_findings.yaml` carrying three
things beyond the existing schema.

```yaml
- id: AT-01-DF-01
  # ... the existing finding fields ...
  channel: test-graph                    # the vocabulary in §4.1
  channel_note: "specWorkflow node ..."  # existing free text, optional
  area: "the workflow-close path"        # PROSE, written by whoever found it
  pinned_by: "tests/test_x.py::test_y"   # or omitted, with pin_note saying why
```

### 4.1 The channel vocabulary, and its class

**Nine tokens.** Seven are `CA-02`'s, unchanged and not relabelled. Two —
`test-graph` and `tlc` — are added because the record could not name them.

**The class is a lookup, not a judgement.** *"Was this caught by an automated
instrument or by a hand?"* is answered by finding the token in this table. **No
`channel_note` is read.**

| channel | class | what it means |
|---|---|---|
| `test-graph` | **automated** | a Test Graph node went red — **new** |
| `the-suite` | **automated** | pytest |
| `tlc` | **automated** | the model checker — **new** |
| `operator-running-a-shipped-instrument` | **automated** | a standing instrument reported it; a person invoked it |
| `operator-doing-the-work` | **hand** | found while doing something else |
| `operator-running-own-instrument` | **hand** | a probe written for the occasion and thrown away |
| `cross-implementation` | **automated** | two implementations of the same contract disagreed — **new**, and see below |
| `census` | **reading** | a systematic sweep of the record |
| `independent-review` | **reading** | a reviewer reading the change |
| `blind-judges` | **reading** | a scored card's judge |

**The line between `automated` and `hand` is one question:** *would it catch this
again tomorrow, with nobody watching?*

**`cross-implementation` is `automated` by that question and is worth its own
token because nothing else finds what it finds.** It was added after two
independently-written fixes to the same YAML parser were run against each
other's corpora and each turned out to be wrong in ways its own tests reported
clean on — then two further defects surfaced that had survived both. A single
implementation cannot produce this signal at any budget, and the only
prerequisite is that a second implementation of the same contract exists.
`PyYAML` is that second implementation here; `#298` and `#307` are the record. That is why
`operator-running-a-shipped-instrument` is automated — the instrument stands —
and `operator-running-own-instrument` is **hand** — the probe does not. **A
throwaway probe that found a real bug is a hand catch wearing a script.**

### 4.2 The pin

**Any CATCH whose class is not `automated` names the assertion that will catch it
next time**, as a test node id or `path::test_name`.

```yaml
  pinned_by: "tests/test_absent_invariants_refuse.py::test_empty_invariants_refuse"
```

**Where no assertion was added, the record says so and says why:**

```yaml
  pin_note: "not pinned: the failure is in the installer, which has no fixture
             here. Filed as skill-manager#261."
```

**A blank is not an answer.** `pin_note` present with `pinned_by` absent is a
complete record; both absent is not.

**Automated catches need no pin** — the thing that caught it is the pin, and
adding a second assertion is duplication, which
`references/architecture_advice.md` §5 names as a standing instruction to
duplicate.

> **This is wider than `GOAL-hand-catches-name-their-pin`'s text, which says
> hand.** It is widened to `reading` deliberately: a bug found by a reviewer has
> nothing standing that would find it again, which is the entire reason the pin
> exists. The widening is recorded here rather than applied silently, and
> `AT-04` scores the goal on its own text.

---

## 5. REACH — an invariant, and the surfaces it does not cover

**Written by whoever wrote the invariant**, because they are the only party who
knows what they were aiming at.

```yaml
reach:
  - invariant: "every executable entrypoint resolves its home before writing"
    enforced_on:
      - "bin/cli"
      - "bin/mcp"
    unenforced_on:
      - "skills/"
      - "plugins/"
      - "the agent directories"
    enumerated_by: "read every directory containing an executable; 5 found, 2 covered"
    note: "DEF-124. The unenforced list is why three live homes were lost eight
           days after the fix was called done."
```

**`unenforced_on` is the field this kind exists for.** `enforced_on` is what
anybody would write anyway.

**`enumerated_by` is mandatory whenever `unenforced_on` is empty**, and it says
how the surfaces were enumerated — §3. An empty list with no `enumerated_by` is
malformed, not clean.

**Where the surfaces were not enumerated:**

```yaml
    unenforced_on: UNDECIDED
    enumerated_by: "not enumerated — I checked the two entrypoints I changed"
```

**That row is honest and it is more useful than a confident empty list.**

---

## 6. BLIND — a green, and what it could never have caught

**Written by whoever wrote the case**, at the time they write it. A BLIND
reconstructed later by a reader is a different and weaker artifact, because the
author is the only one who knows what the fixture was standing in for.

```yaml
blind:
  - case: "test_repair_restores_wrapper"
    passes: true
    could_not_have_caught: "any defect reachable only through a symlinked home —
      every fixture plants a real wrapper, and repair cannot read a symlink, so
      the symlink path is never executed"
    why: "fixture construction, not assertion strength"
    note: "DEF-115. Green for weeks. Green meant COULD NOT LOOK."
```

**An empty `could_not_have_caught` is a claim** — §3 — and needs the same
treatment as an empty `unenforced_on`. *"I did not work out what this case is
blind to"* is `UNDECIDED`, and it is the correct entry when it is true.

**This repository has a starting population and it is not zero.**
`CA-10-DF-14` records **3 vacuous passes**; `SS-06` re-measured the vacuous
population at **six**. Those are BLIND records that already exist as findings and
have never had a place to be written as reach.

**A BLIND does not fail a green and does not gate a close.** It annotates one.

---

## 7. PRICE — declared before, measured after

```yaml
price:
  - proposal: "collapse the three manifest parsers into one"
    declared_before:
      value: "≈400 lines removed, 2 days, one behaviour change to the fallback path"
      declared_at_commit: "902cfd7"
    measured_after:
      value: "612 lines removed, 3 days, two behaviour changes"
      measured_at_commit: null      # null until it is actually measured
    verdict: null                   # null until both halves exist
```

**Two fields, written at two different times, and the record makes backfilling
visible rather than convenient.** `declared_at_commit` is the point of the whole
kind: a price whose declaration commit is *after* the measurement commit is not a
price, it is a retrospective, and anyone reading the two shas can see it.

**Why this kind exists:** `gate_passed: False` on **16 of 16 runs with nothing
stopping.** The cost was measured every single time. It was never priced, so
sixteen measurements had nothing to be measured *against* and sixteen times
nothing happened.

**A refused proposal keeps its `declared_before`.** That is the record of what it
would have cost, and it is the only reason a refusal is reviewable later.

---

## 7a. The influence graph, and the matrix it accumulates into

**The four kinds are per-finding. The influence graph is what they add up to.**

The arc for one regression is **found → area → pinned**:

```
a regression happened
  -> what CAUGHT it            (CATCH.channel, class automated | hand | reading)
  -> what AREA it lived in     (CATCH.area, prose, from whoever found it)
  -> what PINS it now          (CATCH.pinned_by, or pin_note saying why not)
```

**The area is recorded as prose by the finder, and ANCHORED TO A TLA+ ACTION by
the epic agent.** The model is the semantic representation of the program and it
outlives the code — files are renamed, split and moved; `CloseTicket` is not. A
regression that fits no declared action is anchored `UNMODELED`, and **the size
of that bucket measures how much of the real bug surface the model does not
reach.** Do not stretch an action to cover something it does not mean; stretching
destroys that number.

Accumulated per anchor across tickets and epics, that is
`examples/validation/agent_rounds/SELF-IMPROVEMENT-MATRIX.md`. **The column that
matters is `escaped to hand`** — the only one that says an automated instrument
was blind.

**An area that escapes once is noise. An area that escapes in three rounds is
telling you something about its shape.** That is the whole reason to keep the
graph over time rather than per epic.

**It is maintained by prompting, not by a tool, and that is a decision rather
than a gap.** Computing it would mean parsing findings, inferring areas and
joining across epics — three inference steps, each a place to put a bug into the
instrument used to find bugs. `prompts/regression_architecture.md` is the ask;
`prompts/regression_judge.md` judges the transcripts blind. **No checker, gate,
lint or static analyzer is the answer here** — that route is measured and closed
(`references/architecture_advice.md`), and if a tool is built later it belongs in
a separate library with this page as its specification.

**What the graph cannot currently say, stated so nobody reads it as more than it
is: there are no denominators.** An area with one escape in two invocations and
one with one escape in a hundred look identical in the matrix. Until a round
carries per-area invocation counts, a concentration in that table may be a
concentration of attention rather than of defects.

## 7b. CONSERVATION — what happens to findings when the model changes

**The model may shrink. The record may not.**

This is the whole rule, and it exists because the matrix anchors findings to
TLA+ actions, which makes the model a place where counts live — and anything
that holds a count can be improved by editing the container instead of the
contents.

**There is no prohibition here and there should not be one.** Reducing
complexity where defects aggregate is one of the two responses this programme
wants, and it legitimately removes model surface. A ban on removal would put
that response in direct conflict with the record that motivates it. So removal
stays available and is made *pointless* instead:

> **Total findings is invariant under any model change. Only their distribution
> moves.**

Drop an action and its findings re-anchor — to whatever absorbed the behaviour,
or to `UNMODELED`. Merge two and the rows add. Split one and the parts sum to
the whole. **Nothing evaporates**, and a reader checks it by summing a column.

### Why arithmetic and not a rule against deleting

**Spreading findings across more of the model and hiding a concentration are the
same edit.** Both split a heavy row into light ones; both are a diff that adds
actions. No prohibition can separate them, because there is nothing in the
change itself to separate. The sum can: after a legitimate split the parts still
add to the original, and the concentration is visibly redistributed rather than
reduced.

That also disposes of the four quieter versions of the same move — **merge**,
**widen an action's meaning until the bug is not in it**, **re-anchor to
`UNMODELED`**, and **drop**. Under conservation all four are relabelling, and
relabelling does not change a total.

### What a model change must therefore record

Every model change is recorded in the matrix's carry-through log, and each
affected row says **carried**, **dropped** or **split/merged** — that part is
unchanged. Conservation adds one line to the entry:

```
findings before: N    findings after: N    (re-anchored: <id> -> <new anchor>, ...)
```

**If the two numbers differ, the entry is wrong**, and it is wrong in a way that
is visible without reading any of the prose around it.

### The corollary, which is the point of the whole loop

A proposal that reduces an action's escape count **by removing the action** has
reduced nothing, and under conservation it cannot even appear to. So the only
way the count at an action falls is the honest one: **something started catching
the defects before they escaped.**

That is what makes "fewer escapes" mean anything, and it is why this rule sits
next to PRICE rather than in a governance section. It is not a control. It is
the thing that makes the measurement mean what it says.

## 8. What this page deliberately does not do

- **It does not gate.** Nothing refuses, nothing blocks a close, no exit code
  moves. `references/architecture_advice.md` opens with why: *"Every mechanical
  gate this project shipped was defeated cheaply and none of them ever caught a
  bug."*
- **It does not derive the area or the surfaces.** No path map, no taxonomy. Both
  are prose from the person who knows. A model reading twenty records can group
  prose; it cannot recover an area from a token chosen to make a count look
  better — `references/architecture_tags.md` §5 enumerates that attack as `A1`.
- **It does not touch `surface`.** That field is for parallel-ticket conflict
  detection — `git-epic-workflow/references/deferment.md` — and bending it into
  an architecture axis breaks what it does do. Measured, it would not help
  anyway: `workflow` is non-empty on **309** of 364 rows and `production` on
  **77**.
- **It does not touch `references/eval_scorecard.md`.** The judged card's `N-D1`
  already asks what the cases caught and missed, unscored. Editing it moves the
  served digest and forces a version bump across 95 sealed cards for no new
  question. **Byte cost to `serve`: 0.**
- **It builds no index.** The record is read by reading it. If answering one of
  §2's four questions requires a tool, the schema is wrong.

---

## 9. The drift this page inherits, measured

**`CA-02` closed the channel vocabulary. The very next epic put four tokens
outside it on 27 rows, and `disposition.py`'s `ADVISORY (not a clause)` line
printed on every one of them.**

At the `epic/stabilize-substrate` tip — 364 findings, **144 with a channel
(39.6%)**:

| token | rows | disposition |
|---|---|---|
| `execution` | 23 | see below |
| `review` | 3 | → `independent-review` |
| `reading` | 1 | see below |

**All 27 are `SS-*`. Not one is from any other epic.** The advisory worked
exactly as designed — it advised, and was ignored, twenty-seven times, by the
epic standing closest to it.

**And the disposition is mostly UNDECIDED, because the evidence is not there.**
`channel_note` exists on **45 of 364** rows overall and on **9 of the 27**
drifted ones. **Eighteen of the 27 carry no prose at all.**

- **`review` → `independent-review`.** A mechanical rename of a synonym, not a
  classification. 3 rows.
- **`execution` (23) and `reading` (1) → UNDECIDED where no `channel_note`
  exists.** `execution` plausibly means `the-suite`, `tlc` or
  `operator-running-a-shipped-instrument`, and **those are three different
  classes in §4.1's table** — the guess would decide the automated/hand split for
  23 rows on nothing. `references/consumption.md` already names this move as the
  thing to avoid: *assigning a channel from somebody else's prose is the hand
  classification this programme exists to remove.*

**UNDECIDED is the correct answer here and its count is a result, not a failure.**

### `blind-judges`

**Declared by `CA-02`, selected zero times in 364 findings.** It is **retained**,
not retired: it is the one token naming a channel that produced findings this
project has published at length — the four judges of the `hexagonal-prompting`
rerun produced 4 findings the round's own ratio omitted. **The token is not dead;
the filing is.** A token retired because nobody typed it would delete the
evidence that a channel exists and is not being recorded, which is this page's
entire subject.
