# Epic kickoff — `stabilize-substrate`

**Branch `epic/stabilize-substrate`, cut from `main` at
`436c78c55c60c3ee45901223176124df5e38b6ff`**, the merge of
`epic/cut-the-apparatus`. Owner's starter: issue #271.

**Everything below was measured on this branch before any ticket landed.** No
figure in this file is carried from the work order; where the work order
disagreed, the work order is corrected and the movement attributed.

---

## 1. The work order handed this epic five figures. Five moved.

| issue #271 says | re-derived at `436c78c` | attribution |
|---|---|---|
| apparatus **41,691** py lines | **41,971** | #271's figure is at `ea624b9`, the pre-merge epic tip. **+280** from the four post-close commits — `disposition.py`, `spec_evolution.py`, `complexity_ledger.py`, `close_tickets.py`. Verified by re-running the same command at `ea624b9`: **41,691** exactly. |
| **0 of 18** judged goals openable | **0 of 20** | **Numerator held at zero; denominator rose by two.** `18` is `SV-05`'s figure at `3e16b96`, before `cut-the-apparatus` added four goals. `denominator_rule`, applied to the figure the epic was handed. |
| the ledger lives at a per-epic path | **the live path does not exist** | `disposition.LEDGER` and `score_tools.LEDGER_LIVE` both name `specs/desired_program_model/deferred_findings.yaml`, **which the workflow close deletes**. Every consumer is on the archive fallback. |
| `scope` sweep **102 / 80 REFUTED / 2 HOLDS / 20 UNREACHABLE**, byte-identical base to tip | **82 / 63 / 2 / 17** | **−20 REFUTED, every one from the deleted ledger file**; +3/−3 in `NEXT-EPIC.md`, re-anchored by the `0-AAAAAAAAAA` amendment and now REFUTED where they were UNREACHABLE. `102 − 23 + 3 = 82`. **Denominator movement caused by a file disappearing. Nothing was checked, refuted or repaired.** |
| suite **7 / 1462 / 22** at collection **1491** | **17 / 1483 / 4** at collection **1504** | **#271's figure is the CLOSED-WORKFLOW state, which no ticket agent will ever stand in.** Scaffolding the successor workflow restores 13 collected nodes and unskips 18 of the 22. Fully attributed in `../GOAL-tree-stabilizes/baseline.md` §2. |

**Also held, re-derived:** card **6,281 bytes**, `sha256:2d7d4a0506d9b259`, card
version 5, rubric file `sha256:b7fe75437bf68646`; `scope --path` returns **0**
counted figures on `CUT-THE-APPARATUS-EPIC.md` and **3, all REFUTED**, on
`NEXT-EPIC.md`.

**Method note.** The `scope` movement was attributed by diffing this tree's
`scope --format json` against the sealed `CA-08/goal/scope-tip.json` on
`(file, line, span)` — 23 gone, 3 added — not by comparing summary lines. The
summary lines alone would have said "the sweep shrank" and stopped there.

## 2. A live defect, found at kickoff and filed rather than fixed

**`SS-00-DF-01`, assigned to `SS-01`.**

`score_tools.py audit` reports **9 violations** on this worktree — all nine
`filed_as = CL-03-DF-04 is not an id in deferred_findings.yaml`, and
`CL-03-DF-04` **is** filed. `CA-10` measured **0** at the same commit.

**Cause.** `CA-10-DF-11`'s repair falls back to `LEDGER_ARCHIVE_GLOBS` ordered by
`(mtime, size, path)`. **Git does not preserve mtimes.** On a fresh worktree all
**85** candidates carry one mtime — the checkout time — so the ordering
degenerates to **size, then path**, and the largest file wins:
`specs/.history/subtract-to-measure-epic/ticket-005-SM-05/…/deferred_findings.yaml`,
**88 ids, four epics old, a mid-ticket snapshot** — not the 296-row closed
snapshot the entry manifest records under `findings_ledger`.

**The repair moved the wrong answer from "no ledger" to "wrong ledger"**, which
`CA-10-absent-input/RESULT.md` warns against in its own words: *"a fallback that
merely moves the false PASS to a rarer input has not fixed the class."*

**Two consequences.** Every `audit` figure in this epic is a joint property of
**the tree and the checkout** — quote both or it does not reproduce. And this is
**the absent-input class one step on**: the input is not absent, it is *wrong*,
and the instrument is equally confident either way.

**Filed, not fixed.** The owner does not repair code inside a ticket's slice, and
the nine violations are part of the measured base state.

## 3. A defect this kickoff committed, and its own instrument caught — `SS-00-DF-02`

The first draft of the plan **reused the predecessor's `GOAL-four-results-stand`
ID** for the carried goal. `baseline_is_a_card.py` then reported **35** distinct
goals where **36** exist: it **collapsed the two same-ID goals into one row**, and
the collapse presented as a *smaller denominator* rather than as an error. **It
did not warn, did not refuse, and did not report an ambiguity**, and which of the
two baselines the collapsed row reports is undefined by the code.

**The direction is why it matters.** This instrument exists to compute an `N of M`
compliance rate, and an undetected collision **shrinks M**, which **inflates the
rate**. An instrument that mis-reports in the flattering direction, on the exact
quantity it exists to compute, is worse than one that refuses.

**`GOAL-four-results-still-stand`'s `continues:` field is the workaround this
finding forced, not the fix.** `SS-03` repairs it and checks the record for other
cross-epic ID reuse.

## 3a. And a third: the owner edited files a running measurement reads

The first baseline run began at **14:00** and collected **1491**. `specs/current`
appeared at **14:03**; `specs/desired_program_model` was still being written at
**14:23**. **The run collected the closed tree and executed against the
scaffolded one**, returning `14 failed / 1471 passed / 6 skipped`.

**That is §8's rule, committed by the person who wrote it into the charter, at
kickoff.** The run is preserved as
`pytest-CONTAMINATED-scaffold-landed-mid-run.txt` — **kept rather than deleted,
because deleting it removes the record of what was measured** — and the suite was
re-run clean on the settled tree with nothing edited for 26 minutes.

## 4. And a fourth, which changed a target's wording — `SS-00-DF-03`

**All five of this epic's harnesses are commands.** The census classified **three
of the five** as naming a *judged* instrument, because its judged-instrument
recogniser is a **keyword matcher over the harness prose** — words like `card`,
`sealed` and `scored` appearing in a description of what the command *reads*.

That is `CA-08-DF-01`'s class **from the other side**: there the sentence form was
too narrow and reached nothing; here it is too loose and reaches too much. **So
`0 of 20` is not established as the number of judged goals — only as the number of
harness strings containing certain words**, and that denominator has been quoted
across four epics. **This one errs in the UNFLATTERING direction, which is
probably why nobody caught it.**

`GOAL-judged-goals-compliant` clause (a) now says so, `SS-03` repairs it, and it
**forbids fixing it by rewording the plan until the classification flips**
(`MF-020`).

## 4a. Owner decision: all three are repaired before the evaluation

**Taken 2026-08-15, recorded as
`planning_rules.kickoff_defects_are_repaired_before_the_evaluation`.**

`SS-00-DF-01` is `SS-01`'s; `SS-00-DF-02` and `SS-00-DF-03` are `SS-03`'s. Both
tickets are **wave 1** and both promote **long before** `SS-08`, so the rule costs
the schedule nothing.

**The reason is not tidiness.** All three are defects in the instruments `SS-08`
must use to decide the goals, and **two mis-report in a direction** — `DF-02`
inflates a compliance rate, `DF-01` accuses true citations of being fabricated.
**An evaluation run on instruments known to mis-report is not a measurement.**

**`SS-08` verifies by execution, not by reading a PR** — for `DF-01` that means
`audit` on two independent fresh worktrees of the same commit returning the same
count. **An unrepaired defect is an ALARM with its affected figures named, not a
repair job**, and any baseline a repair moved is reported as **a fact about the
instrument**, never absorbed into a goal verdict.

## 5. Decisions taken at kickoff

| decision | choice | note |
|---|---|---|
| goals | four new + one carried | `GOAL-absent-input-consumed`, `GOAL-tree-stabilizes`, `GOAL-judged-goals-compliant`, `GOAL-counted-figures-reach-the-record`, `GOAL-four-results-still-stand` |
| size target | **none** | §3.1 of #271: net-additive is required by construction. Four epics have called themselves simplifications and come out net-additive. **Nothing is cut for being long.** |
| deferment | `batch`, blocking escalates, budget 5 | backlog `specs/deferred_findings.yaml` |
| ledger path | **moved to `specs/deferred_findings.yaml`** | owner moved the data; **296 rows verified byte-identical** to the closed snapshot before and after. `SS-01` owns the consumer migration and must **verify** the inherited "10 live files" figure. The **25 archival scorecards must not be rewritten.** |
| the three kickoff defects | **repaired before the evaluation** | Owner decision 2026-08-15, §4a. `SS-00-DF-01` -> `SS-01`; `SS-00-DF-02`, `SS-00-DF-03` -> `SS-03`. Both are wave 1, so it costs the schedule nothing. |
| local `main` | **fast-forwarded `08d1d6a` -> `436c78c`** | Owner-approved 2026-08-15, **after** the epic branch was cut and **after** every baseline here was measured. No figure in this record depends on it, and the assignments still pin OIDs. |
| stale units | `deploy-helm` + `debugging` synced in **both** tiers | **`spec-double-compiler` deliberately NOT synced** — it ships the whole 402 MB repository including every charter and a stale `NEXT-EPIC.md` (#271 §7.5, an unmeasured contamination channel), and syncing mid-epic moves text under running tickets |

## 6. The schedule

8 tickets, 5 waves, 5 goals. Validated by
`git-epic-workflow/scripts/validate_epic_plan.py`: **OK, no warnings.**

| ticket | wave | depends on | promotes after | goal |
|---|---|---|---|---|
| `SS-01` ledger relocation + 4 inherited decisions + `SS-00-DF-01` | 1 | — | — | enabling |
| `SS-03` judged-goal compliance | 1 | — | `SS-01` | `GOAL-judged-goals-compliant` |
| `SS-02` `R1` absent-input extension as an **executed check** | 2 | `SS-01` | `SS-03` | `GOAL-absent-input-consumed` |
| `SS-07` four results + the stranded disproof instrument | 2 | `SS-01` | `SS-02` | `GOAL-four-results-still-stand` |
| `SS-04` counted-figure recogniser | 3 | `SS-02` | `SS-07` | `GOAL-counted-figures-reach-the-record` |
| `SS-06` the 22 skips, 13 uncollected, 3 vacuous passes | 3 | `SS-02` | `SS-04` | `GOAL-tree-stabilizes` |
| `SS-05` repair the class | 4 | `SS-02`,`SS-04`,`SS-06` | `SS-06` | `GOAL-absent-input-consumed` |
| `SS-08` **EVALUATION** | 5 | all | `SS-05` | owns all five |

**`score_tools.py` is the bottleneck** — `SS-01`, `SS-02`, `SS-04` and `SS-05`
all touch it, so they are in four different waves by construction. That is the
cost of the conflict-key rule and it is deliberate.

## 7. Hazards declared rather than repaired

- **Local `main` was stale at `08d1d6a`** while `origin/main` was `436c78c`.
  `wt new` branches from the **local** ref, so every assignment names a resolved
  OID. **Resolved 2026-08-15: fast-forwarded to `436c78c` with the owner's
  explicit approval**, after the epic branch was cut and after every baseline in
  this record was measured — **no figure here depends on it**. The assignments
  still pin OIDs, because the hazard is the habit, not that one ref.
- **`skt check` in the root tier reports `deploy-helm modified locally (ahead)`
  immediately after a successful sync to the remote tip.** Not chased; noted so
  a ticket agent does not read it as its own doing.
- **`spec-double-compiler` is stale in both tiers, deliberately.**
- **`audit` is 9 at this checkout and 0 at another.** `SS-00-DF-01`.

## 8. Evidence index

| path | what |
|---|---|
| `pytest-baseline-436c78c.txt` | **the baseline** — 17 / 1483 / 4, collection 1504, clean run on the settled tree |
| `pytest-CONTAMINATED-scaffold-landed-mid-run.txt` | the contaminated first run, preserved and labelled — §3a |
| `render_assignments.py` | renders every issue body **from** the canonical plan, so the assignment cannot drift from it; `--check` re-renders and diffs |
| `../GOAL-absent-input-consumed/` | `baseline.md`, `class-rows-436c78c.txt` |
| `../GOAL-tree-stabilizes/` | `baseline.md`, `collection-436c78c.txt` |
| `../GOAL-judged-goals-compliant/` | `baseline.md`, `baseline_is_a_card-436c78c.txt` |
| `../GOAL-counted-figures-reach-the-record/` | `baseline.md`, `scope-work-directing-docs-436c78c.txt`, `scope-whole-record-436c78c.txt`, `.json` |
| `../GOAL-four-results-still-stand/` | `baseline.md`, `audit-436c78c.txt`, `serve-digest-436c78c.txt` |
