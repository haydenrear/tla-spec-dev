# attribute-the-catch

**Epic branch:** `epic/attribute-the-catch`, from `main` at `902cfd7`.
**Tickets:** `AT-01`..`AT-03`, evaluation `AT-04`.
**This epic ships markdown and prompts. It ships no code.**

---

## 0. THE THESIS, IN THE OWNER'S WORDS

> **Their charter records what caught a bug; nothing records what a passing case
> could never have caught.**

**A finding only exists where something was found.** Every record this project
keeps is indexed by a failure: the ledger has 364 findings and not one row for a
place nobody looked. So the record is dense exactly where the instruments work
and **empty exactly where they are blind** — and it reads the same either way.

**This epic records the negative space.** Four record kinds, three of which run
in the opposite direction from a finding:

| kind | direction | question |
|---|---|---|
| **CATCH** | backward, from a failure | A regression happened. What caught it, what area was it in, what pins it now? |
| **REACH** | forward, from a rule | An invariant exists. Which surfaces enforce it — and **which do not**? |
| **BLIND** | forward, from a green | A case passes. What could it **never** have caught? |
| **PRICE** | forward, from a proposal | A change was proposed. What was it priced at **before** — and what did it cost? |

**Each of the last three is on this list because it already cost something
measured:**

- **REACH.** An invariant enforced on `bin/cli` and `bin/mcp` and unenforced on
  `skills/`, `plugins/` and the agent dirs. Nothing recorded the second half.
  **Three live homes, eight days after the fix.** (`DEF-124`)
- **BLIND.** A node green for weeks, because every fixture planted a wrapper and
  repair cannot read a symlink. **Green meant *could not look*.** (`DEF-115`)
- **PRICE.** `gate_passed: False` on **16 of 16 runs with nothing stopping.**
  Measured afterwards, never priced beforehand, so the signal had nowhere to
  land.

**CATCH alone would not have caught any of the three**, and that is the argument
for the other three kinds.

---

## 1. WHAT THIS EPIC SHIPS, AND WHAT IT REFUSES TO SHIP

**Ships:** one reference page, edits to where the epic and ticket surfaces are
written, one sub-agent prompt.

**Does not ship:** a script, a subcommand, a validator, a gate, a test, an index,
a query tool. **Not one line of Python.**

**There is no new test, and this is a fact rather than a preference.**
`tests/test_spec_yaml_valid.py` already parses every `specs/**/*.y*ml` outside
`.history`, and the ledger is directly under `specs/`. The only mechanical
property this epic needs — *the file parses* — is already guarded, by a test that
already guards itself against passing vacuously.

**The data is collected. It is read by a model, by reading it.** No index,
nothing precomputed, no tool between the record and whoever is asking. **If
answering requires a tool, the schema is wrong.**

---

## 2. WHY MARKDOWN AND PROMPTS, AND THE PRECEDENT THAT CUTS BOTH WAYS

`references/architecture_advice.md` opens with the reason:

> Every mechanical gate this project shipped was defeated cheaply and none of
> them ever caught a bug. The complexity gate failed every normal program and was
> retired to advisory. The architecture check reported a clean on a divergent
> codebase for **six lines of YAML** in round 1, and for a **41-line re-export
> file** in round 2, with every declaration digest unchanged. Across two full eval
> rounds and seven repair tickets, **bug detection did not move by a single
> cell**: 4 of 6, 6 of 6, 0 of 3, 0 of 3, before and after.

`prompts/hexagonal_implementation.md` states the contract this epic inherits:

> It is **a prompt, not a check.** It refuses nothing, gates nothing, blocks no
> promotion, and no tool in this repository reads it.

**And the counterweight, which this epic bets against and must report either
way.** The epic that produced that prompt measured its own result as:

> **THE PROMPT PRODUCED THE STRUCTURE AND THE STRUCTURE CAUGHT NOTHING — again**

**Asking has a track record of producing shape without producing catches.** A
null result is a result, published as one.

---

## 3. THE STARTING STATE, MEASURED

`channel` shipped in `CA-02`, **six epics ago**, with a closed seven-token
vocabulary. Measured on the cumulative ledger at the `epic/stabilize-substrate`
tip — 364 findings:

| channel | rows | in the declared vocabulary? |
|---|---|---|
| `operator-doing-the-work` | 30 | yes |
| `independent-review` | 29 | yes |
| `execution` | 23 | **NO** |
| `operator-running-a-shipped-instrument` | 20 | yes |
| `census` | 16 | yes |
| `the-suite` | 14 | yes |
| `operator-running-own-instrument` | 8 | yes |
| `review` | 3 | **NO** |
| `reading` | 1 | **NO** |
| `blind-judges` | **0** | declared, never used |

**144 of 364 populated — 39.6%. 27 of the 144 outside the vocabulary
`references/consumption.md` calls "closed now." `blind-judges` declared and never
selected.**

**No token names the test graph.** `the-suite` is pytest. `surface.test_graph` is
a *file list*, not a catcher, non-empty on **7 of 364**.

**REACH, BLIND and PRICE have no record at all — the baseline for each is zero
rows of a kind that does not exist.**

**And BLIND has a live population here already:** `CA-10-DF-14` records **3
vacuous passes** in this repository's own suite, and `SS-06` measured the
vacuous population at **six**, not three. **Those are BLIND records waiting for a
place to be written down.**

---

## 4. THE ARCHITECTURAL AREA, AND THE SURFACE LIST — prose, named by whoever knows

**No path map. No derived region. No taxonomy.**

A CATCH names its area in prose, written by whoever found the bug. A REACH names
its enforced and unenforced surfaces in prose, written by whoever wrote the
invariant. **They are the only parties who know**, and a model reading twenty
records can group prose; it cannot recover an area from a token chosen to make a
count look better.

**`surface` is not touched.** It exists for parallel-ticket conflict detection —
`git-epic-workflow/references/deferment.md`, *"which conflict key or semantic
boundary it crosses"* — feeding `blast_radius` and the deferment policy. Bending
it into an architecture axis breaks what it does do and makes 364 rows
incomparable. And it would not help: `workflow` is non-empty on **309** of 364,
`production` on **77**.

---

## 5. THE ONE RULE THAT MAKES REACH AND BLIND WORTH ANYTHING

**An empty unenforced-list, and an empty blind-spot, are CLAIMS. They are never
defaults.**

This is the whole of `DEF-124` and `DEF-115` in one sentence. A REACH that says
*"enforced everywhere"* and a BLIND that says *"this case could have caught
anything"* are the two most dangerous rows either kind can carry, because they
read as maximum coverage and cost nothing to write.

So both are governed by the rule `SS-02` already landed for absent inputs:

> **The correct answer to an absent input is UNDECIDED or a refusal — never
> PASS.**

**"I did not enumerate the surfaces" is UNDECIDED. "I enumerated them and found
none uncovered" is a claim and names how it was enumerated.** The two must never
be written the same way, and a record that cannot tell them apart has shipped
`SS-02`'s class in a new field.

---

## 6. THE JUDGED CARD IS NOT TOUCHED

`references/eval_scorecard.md` is **out of scope, deliberately.** It already
carries the right question as an unscored recorded note:

> **N-D1 — bug detection.** What did the cases catch, and what class did they
> demonstrably miss? Name the fault you seeded if you seeded one.

Editing that text moves the **served digest**, forcing a card version bump and a
comparability statement about **95 sealed cards**, for prose saying what N-D1
already says. **The epic-level attribution belongs in the epic's own evaluation
RESULT, not in the five-dimension card a blind judge scores.**

**Byte cost to `serve`: 0. Anchors digest: unchanged. Card version: unchanged.**

---

## 7. THE GOALS

Six. **None is decided by a script**, because there is no script. Each is decided
by `AT-04` reading the record and reporting a count with its denominator.

### `GOAL-the-record-says-what-caught-it` — CATCH
**Baseline.** 144 of 364 carry any channel; 27 out of vocabulary; no token names
the test graph.
**Target.** (a) 100% of this epic's own findings say what caught it, N of M by
reading. (b) Graph, suite and hand distinguishable **without reading
`channel_note`**. (c) The 27 out-of-vocabulary rows decided — mapped, absorbed,
or UNDECIDED where the original intent is unrecoverable — each count stated.
**UNDECIDED is a correct answer and its count is a result.** (d) `blind-judges`
retired or demonstrated.

### `GOAL-hand-catches-name-their-pin` — CATCH
**Baseline.** **0.** Disposition measures routing, never consumption.
**Target.** (a) Every hand-caught finding names an assertion — test node id or
`path::test_name`. (b) Required for hand-caught findings **only**: a regression
the graph caught is already pinned by the thing that caught it, and a second
assertion is duplication (`architecture_advice.md` §5). (c) Where no assertion
was added, the record **says so and says why**.

### `GOAL-invariants-name-their-unenforced-surfaces` — REACH
**Baseline.** **0 rows. The kind does not exist.** `DEF-124`: an invariant
enforced on `bin/cli` and `bin/mcp`, unenforced on `skills/`, `plugins/` and the
agent dirs, **three live homes lost eight days after the fix**, and nothing in
any record named the second list.
**Target.** (a) A REACH record names the surfaces the invariant **is** enforced
on and the surfaces it **is not**, both enumerated. (b) **An empty unenforced
list is a claim and names how the surfaces were enumerated** — §5. (c) *"I did
not enumerate"* is UNDECIDED and is written differently from *"I enumerated and
found none"*. (d) At least one REACH is written for a real invariant in this
repository, with a real uncovered surface named. (e) **Nothing enforces this.**

### `GOAL-green-declares-its-blind-spot` — BLIND
**Baseline.** **0 rows. The kind does not exist.** `DEF-115`: a node green for
weeks because every fixture planted a wrapper and repair cannot read a symlink —
**green meant *could not look***. This repository has its own live population:
`CA-10-DF-14`'s 3 vacuous passes, measured by `SS-06` at **six**.
**Target.** (a) A BLIND record names, for a passing case, a class it could
**never** have caught, and why — the fixture, the wrapper, the unreadable input.
(b) **An empty blind spot is a claim**, not a default — §5. (c) At least one
BLIND is written against a real green in this repository, and the vacuous-pass
population is the obvious place to start. (d) A BLIND is written **by whoever
wrote the case**, not reconstructed later by a reader. (e) **Nothing enforces
this** — it does not gate, it does not fail a green.

### `GOAL-proposals-are-priced-before-not-after` — PRICE
**Baseline.** **0 rows.** `gate_passed: False` on **16 of 16 runs with nothing
stopping** — measured afterwards, never priced beforehand.
**Target.** (a) A PRICE record carries the price **declared before the change**
and the cost **measured after**, as two separate fields written at two different
times. (b) **A price written after the measurement is not a price** and the
record must make backfilling visible rather than convenient. (c) The refactor
prompt emits a PRICE, not a retrospective. (d) Where a proposal was refused, the
declared price stands as the record of what it would have cost. (e) **Nothing
enforces this.**

### `GOAL-the-surfaces-ask-for-all-four`
**Baseline.** No surface mentions any of the four.
**Target.** (a) The ticket close-out asks for CATCH and BLIND. (b) The epic
goal/scorecard/evaluation asks for all four. (c) **Asked for, never enforced** —
no gate, no refusal, no exit code, nothing reads it. (d) **The ask fits on a
screen at each site.** A page of instructions at a close-out is a page nobody
reads, and would reproduce the 39.6% with better documentation.

---

## 8. THE TICKETS

| ticket | what it does |
|---|---|
| **`AT-01`** | `references/bug_attribution.md` — the four record kinds, the vocabulary, and §5's claim-versus-UNDECIDED rule. |
| **`AT-02`** | Where they are asked for: the ticket close-out and the epic goal/scorecard/evaluation surface. |
| **`AT-03`** | `prompts/regression_architecture.md` — the refactor prompt, reading all four kinds, emitting a PRICE. |
| **`AT-04`** | **EVALUATION** — decide the six goals by reading, run the prompt once, publish what it produced including nothing. |

---

## 9. THE REFACTOR PROMPT — `AT-03`, and its four constraints

The ask, dispatched verbatim with the records pasted underneath:

> Here are this project's CATCH, REACH, BLIND and PRICE records. Which areas
> produced regressions that every automated instrument missed? Which invariants
> are enforced on some surfaces and not others? Which greens are blind? For the
> worst one: is there a **refactor that removes the class** — not one that catches
> it — and **what do you price it at, before anyone tries it?**

**Four constraints, all from prior results rather than taste:**

- **It may not choose the boundary.** `references/architecture_advice.md` §6:
  *"Advice may describe a good boundary; it must not choose one."* It describes
  and prices; the owner decides.
- **It is not a gate.** §5: *"'Make the check clean' is a standing instruction to
  duplicate."*
- **It must say what it could not see.** §9: *"Refuse rather than certify what
  you could not see."* The ledger is 39.6% attributed and REACH/BLIND start
  empty. **A clean verdict off that record has certified an absence it never
  observed.**
- **It prices forward.** The output is a PRICE record — a number declared before
  anyone tries the refactor — **not a measurement that the refactor already paid
  off.** A retrospective is the failure mode this constraint exists to prevent.
