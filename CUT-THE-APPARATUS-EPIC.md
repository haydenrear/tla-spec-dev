# Epic: cut the apparatus

**Starter for every ticket agent on this epic. Read this before you touch git.**

Branch `epic/cut-the-apparatus`, cut from `main` at
`08d1d6a90ad2638cdfceee7cc2e150732daa3438` after `score-drives-validation`
merged. Canonical plan: `specs/desired_program_model/ticket_plan.yaml`. Prior
record: `NEXT-EPIC.md` §0-AAAAAAAAA, then §0-AAAAAAAA. Owner's starter:
issue #254.

---

## 1. The ratio is the subject

Seven epics produced **95 sealed scorecards and 210 findings**, of which **four
results survive adversarial checking**. The machinery built to produce them is
**43,553 lines of Python** across `scripts/` and `examples/validation/`, against
a served card of **6,281 bytes and two scored dimensions** — roughly **half of
one percent**.

**This epic changes that ratio without destroying the four results.**

---

## 2. The four results you must not break

**Everything you cut must leave these standing.** If your cut breaks one, say
which, say what broke it, and say whether the trade was worth it. **A silently
broken result is the worst outcome available and fails `GOAL-four-results-stand`
even if the lines fell.**

| result | evidence |
|---|---|
| **Asking for an architecture changes the architecture** | D3 went **1 → 4** on the prompt alone, replicated across rounds. Confound killed directly: a *longer* prompt with no architectural vocabulary scored **1/1** (`arm C`). |
| **D3 separates architectures on more than one example** | `eval_toolchain`: `effectful [0,1]` vs `ports-and-adapters [2,4]`, disjoint, **both judge tiers on both sides**. |
| **D3's v5 caveat discriminates** | `SV-01`: D3 held **4, 4** at v4 and v5 on an artifact **lacking** the property, against `CL-03`'s **4, 4 → 3, 3** on one that has it. Prediction sealed at a timestamped commit before any judge ran. |
| **A score can produce a test and the re-score sees it** | `SV-04`: control **3, 3** vs treatment **4, 4**, same bytes plus one file, D2 flat at 2 across all four. |

### And four things disproven, which are equally load-bearing

- **Model-derived cases do not catch bugs hand-written tests miss** — zero unique
  kills for the generated corpus across six trees, **four the other way**,
  replicated on new subjects.
- **Static gates catch nothing** — seven epics, zero bugs caught by a static
  check.
- **The removal-pricing instrument has not yet been useful** — *"A non-zero was
  the informative outcome, the instrument would have printed one, and none
  appeared… The goal is met and the instrument is not yet useful"*
  (`NEXT-EPIC.md` §5).

  > **CORRECTED 2026-08-13 — `CA-00-DF-05`. This bullet previously read "could
  > only ever return zero… 0 of 9 over the sealed table", copied from issue #254
  > into this charter, the plan, the goal baseline and CA-02's work order
  > WITHOUT BEING CHECKED. The sealed record refutes it in three places.**
  > `RM-05-DF-01` forbids the quotation by name: *"WHAT SURVIVES, STATED SO THIS
  > FINDING CANNOT BE QUOTED AS 'THE EPIC PRICED NOTHING'… The epic HAS a priced
  > removal."* `RM-02` §10.2: *"the instrument **can fire**, history remains
  > free."* And `RD-02` — which scopes its own `0 of 9` as explicitly **not** a
  > statement about every mutant — **refused this very deletion**, titling itself
  > *"the apparatus is load-bearing"* and filing `RD-02-DF-02` against exactly
  > this restatement.
  >
  > **The cut still stands**, on `RM-02`'s adoption argument and `NEXT-EPIC` §5's
  > "do not fund a third epic on it". It is right for a weaker and true reason
  > rather than a strong and false one. **`R3`/`scope` would have caught this and
  > nobody ran it against this charter.**
- **Three of the card's five dimensions graded toolchain ownership** — an anchor
  decision cited this project's own machinery in **38% of D1** and **18% of D4**
  rationales, against **0%** on D3 and D5.

---

## 3. The four goals

Read your ticket's `goals` block **before implementing**. The
`expected_effect` is the result your change is aiming at.

| goal | baseline | target |
|---|---|---|
| `GOAL-apparatus-cut` | 43,553 py lines (`scripts/` 27,652 + `examples/validation/` 15,901); card 6,281 b | ≤30,487 lines (**≥30%**), every deletion names its finding, card does not grow, surfaces reported separately |
| `GOAL-consumption-obligatory` | **1 of 38** consumed; register untouched since 2026-08-11; no `channel`, no `cost` | disposition requirement with a **demonstrated refusal**; register repaired with the true denominator; both fields populated. **No target on the rate itself** |
| `GOAL-blind-dispatch` | **4 of 4** blind agents leaked the operator's memory; **no round was ever blind** | what an agent receives is **measured**; a memory-free path **proven by fresh agents**; or the impossibility stated as a finding |
| `GOAL-four-results-stand` | four results standing at the base | each still reproduces, or the epic names which one it broke |

**`GOAL-blind-dispatch` lands first (CA-01) and before any judged round.**

---

## 4. Cut on the record, never on aesthetics

**Every deletion names the finding ID that justifies it, and every cut is
priced** — what it removed, what it cost, and what the tree can no longer do.
A cut with no finding behind it does not ship, and **clause (b) of
`GOAL-apparatus-cut` fails even if the lines fell.**

`RM-03` declined `kill_test.py` because it is a **model delta**. That refusal was
right for that ticket. **A model delta is now a cost to price rather than a
reason to stop.**

### The structural fact that makes cutting hard

**`RM-03-DF-03`: the change rule keeps old anchors and `R-H4` seals the record,
so a CARD removal cannot delete prose or code.** Three epics called themselves
simplifications and came out net-additive **because that outcome is required by
construction**. So:

- **`serve | wc -c` is the metric for the CARD** — 6,281 bytes, 9 rungs,
  `sha256:2d7d4a0506d9b259`. **Do not grow it.**
- **Repository lines are the metric for the APPARATUS** — and they are what this
  epic is about.
- **Never report the card and the apparatus as one number**, and never report a
  cut in repository lines without saying **which surface**.

---

## 5. Do not cut these

`scope`, `seal`, `contested`, the blinding mechanism, `R-H1`/`R-H2`/`R-H4`/`R3`,
and the version/served double seal. `RM-02`: *"the substrate's best export, and
the epic should be careful not to cut them for being unglamorous."* `CL-01`'s
second seal caught a real class one ticket later.

**`analyze_complexity.py` and `code_complexity.py` serve the spec workflow and
STAY.** Only their role as a **precondition of a D2 score** is cut.

**The suite keeps its regression-guard job.** It is defunded only as a *finding
channel*. Do not delete it.

---

## 6. The TLA+ / case-generation / adapter path — owner decision

> *"I do want to keep parts of the TLA+ diagram, I still think generating cases,
> using adapters is valid, I want to make it dead simple, the regressions should
> tried to be included in TLA+ and adapters in the most simple validated way."*

**Take that as a decision, and note the tension honestly rather than quietly
resolving it either way:**

- **The measurement says the current implementation does not beat hand-written
  tests** — 0 unique kills against 4 the other way, replicated.
- **The owner's direction is to keep it and make it dead simple.**

**Those are compatible only if it gets dramatically smaller.** `CA-06` owns it.
**Simplify aggressively; do not delete.** If the simplified version still yields
zero unique kills, **say so** — that is a result, and the direction was to
simplify it, not to prove it works.

---

## 7. What not to do

- **Do not cut the card.** 6,281 bytes, two scored dimensions, not the problem.
- **Do not add a gate.** Seven epics, zero bugs caught.
- **Do not add a diagram rung.** `diagram`, `mermaid`, `UML`, `C4`, `.svg`:
  **0 sentences across 0 of 95 cards.**
- **Do not restore D1, D4 or D5 as scored dimensions** without the both-wordings
  re-score `SV-02` says is owed first.
- **Do not run a judged round before `CA-01` lands** — or if you must, say
  exactly what your judges received.
- **Do not solve blindness by editing the operator's memory silently.** Propose a
  diff and escalate.

---

## 8. Doctrine, all measured

- **`MF-020`** — never add an axis, test, rung or case fitted to a known answer.
  Refused three times; most recently when a judge named it unprompted after a
  310-line removal made Python lines *rise*.
- **`R1`** — an instrument ships with a demonstrated **failing** input on a
  **real subject**, not a fixture. This project has shipped three instruments
  later found blind.
- **`R-H1`/`R-H2`** — same example, unchanged instrument, same architecture tag.
  **Never average across examples or versions.** 63 of 95 cards are one example;
  5 card versions are 5 incomparable eras.
- **`R3`** — a claim carries its scope. `scope` has four known bounds; read them
  before quoting it.
- **`denominator_rule`** — if a count moves, say whether the numerator rose or
  the denominator fell. **Including suite counts.**
- **Seal predictions BEFORE measuring, in a commit, with a timestamp.**
- **If every prediction passes, report it as an ALARM.**
- **File findings; fix nothing during a measurement.**
- **Ask every blind agent what it REJECTED** — it has produced more than any
  check.
- **NEW THIS EPIC — every research ticket runs its own proposed rule against the
  sealed record before it ships**, and reports what the rule refuses. Four
  tickets corrected their predecessor last epic and **four of five corrections
  were available to the party corrected from data it already had.** That is `R1`
  pointed at prose. It is not a gate.

---

## 9. Operational rules this project has paid for

- **`wt new` branches from the LOCAL ref.** It has put tickets **4, 14 and 21
  commits behind**. **Verify your branch point** — including against a SHA the
  owner hands you, which has been wrong once.
- **The test command is `uv run --with pytest --with pyyaml -m pytest tests -q`.**
  `README.md:35` omits `--with pyyaml` and yields **12 phantom reds** against a
  real baseline of two.
- **Two reds are inherited and deliberate**: `RM-06-DF-01` (the same-tag control
  cannot tell treatment from architecture) and the pricer grep tripped by
  narrative documents. **Do not repair them silently.** The epic-base suite
  figure is in `specs/results/scorecards/cut-the-apparatus/GOAL-four-results-stand/baseline.md`
  — compare against **that**, not against a recollection.
- **Do NOT report `git archive` figures as tree properties.** Those tests read
  git history; an archive has no `.git`.
- **Write scratch output to a TICKET-SPECIFIC path.** Two concurrent tickets
  corrupted a shared `baseline.txt`.
- **Do NOT hand-roll a wait loop** for a run you started.
- **Never kill a process by name alone**, and check whether a process is yours
  first.
- **Read the validator's OUTPUT, not its exit code.**
- **Never invoke `tla-spec-dev` from PATH.**
- **Skills are READ, never edited.** Propose any `SKILL_MANAGER_HOME` change as a
  diff and escalate. **Never run `skill-manager sync`.**

### The two homes, declared

`SV-05-DF-03` measured two Skill Manager homes disagreeing. Verified again at
this epic's kickoff: the operator's `validate_epic_plan.py` is **47,433 bytes**
and the per-worktree copy is **27,926 bytes**. **This epic's plan was validated
against both and passes both**, with no warnings.

**11 change-managed units are stale against their sources at the epic base.**
They are **deliberately not synced** for the duration — syncing mid-epic moves
text under tickets already running. **The authoritative home for every ticket is
its own per-worktree home**, created by `skt ticket new`.

---

## 10. The standing rule

**A low or unflattering result is the preferred outcome.** The last three epics'
best material was, in order: their own premise falsified, their own headline
withdrawn, and the discovery that **no round this programme has run was blind**.

**An epic that closes with only good news about itself has not been measured.**
