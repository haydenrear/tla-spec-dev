# Epic: stabilize the executable substrate

**Starter for every ticket agent on this epic. Read this before you touch git.**

Branch `epic/stabilize-substrate`, cut from `main` at
`436c78c55c60c3ee45901223176124df5e38b6ff`, the merge of
`epic/cut-the-apparatus`. Canonical plan:
`specs/desired_program_model/ticket_plan.yaml`. Prior record: `NEXT-EPIC.md`
§0-AAAAAAAAAA, then §0-AAAAAAAAA. Owner's starter: issue #271.

---

## 0. READ THIS BEFORE ANYTHING — three figures in your work order already moved

Issue #271 opens by telling the successor that its predecessor's cut list was
fiction: three of four ordered targets did not exist as described and the fourth
was load-bearing in the opposite direction. **That instruction was followed
against issue #271 itself, and three of its own figures did not survive.**

| #271 says | re-derived at `436c78c` | why it moved |
|---|---|---|
| apparatus is **41,691** py lines | **41,971** | #271's figure is measured at `ea624b9`, the pre-merge epic tip. The four post-close commits added **+280** to `scripts/` (`disposition.py`, `spec_evolution.py`, `complexity_ledger.py`, `close_tickets.py`). |
| **0 of 18** judged goals have an openable baseline | **0 of 20** | The numerator held at zero; **the denominator rose** when `cut-the-apparatus` added four goals. 31 distinct goals, 20 judged, 0 card-backed. `denominator_rule` applies to the figure you were handed. |
| the ledger is at a per-epic path | it is, and **the live path does not exist** | `disposition.LEDGER` and `score_tools.LEDGER_LIVE` both name `specs/desired_program_model/deferred_findings.yaml`, which the close **deletes**. Every consumer is running on the archive fallback right now. |
| the `scope` sweep is **102 figures**, byte-identical at base and tip | **82** | **−20 REFUTED, every one of them from the ledger file the close deleted**, plus 3 `NEXT-EPIC.md` rows re-anchored by the amendment. Denominator movement caused by a file disappearing — **nothing was checked, refuted or repaired to produce it.** |

**What survived unchanged, each re-derived on this branch:** collection **1491**;
card **6,281 bytes**, `sha256:2d7d4a0506d9b259`, card version 5; `scope` reads
**0** counted figures on `CUT-THE-APPARATUS-EPIC.md` — **and 0 on this charter,
which is full of `<n> of <m>` sentences** — and **3, all REFUTED**, on
`NEXT-EPIC.md`.

**And the kickoff found a live one, filed as `SS-00-DF-01` and assigned to
`SS-01`.** `score_tools.py audit` reports **9 violations** on this worktree and
**0** on the worktree `CA-10` measured, **at the same commit**. Cause: the
archived-ledger fallback orders candidates by `(mtime, size, path)`, **git does
not preserve mtimes**, so on a fresh checkout all 85 candidates share one mtime,
the ordering degenerates to size, and **the largest file wins** — a four-epic-old
mid-ticket snapshot with 88 ids. **`CA-10-DF-11`'s repair moved the wrong answer
from "no ledger" to "wrong ledger"**, which that repair's own write-up warns
against in its own words.

**Two consequences you inherit.** Every `audit` figure in this epic is a joint
property of **the tree and the checkout** — quote both. And **this is the
absent-input class one step on**: the input is not absent, it is *wrong*, and the
instrument is equally confident either way.

**So: for every claim in this charter, in your issue, and in any finding either
cites, open the source, read the sentence, and check the tree before acting on
it.** The instrument that is supposed to do this for you cannot: `CA-08-DF-01`,
`scope` returns zero counted figures on charters, plans, baselines and price
tables. `SS-04` is the ticket that changes that; until it lands, you are the
recogniser.

---

## 1. The thesis: the tree is the finish condition, not the count

The predecessor closed its workflow for the first time in this repository's
history and the tree entered a state it had never been in. Reds moved 8 → 11 → 7.
Every movement was attributed, and the answer was neither "we regressed" nor "we
fixed it":

```
pre-close    7 failed / 1497 passed /  0 skipped   collection 1504
post-close  11 failed / 1458 passed / 22 skipped   collection 1491
after fix    7 failed / 1462 passed / 22 skipped   collection 1491
```

**The count converged by repaired numerator, not fallen denominator. The tree did
not converge.**

**Your finish condition is the tree.** Reds, passes, skips **and collection**
reported together, every movement attributed with numerator and denominator
named — or a movement that cannot be attributed, **which is the finding.**

### And the kickoff measurement already moved two of the three populations

**The epic base is `17 failed / 1483 passed / 4 skipped / collection 1504`**, on
the tree with this epic's workflow scaffolded — **the tree you will actually
stand in.** They sum. Compare against **that**, in
`GOAL-tree-stabilizes`'s baseline evidence, never against #271's figure.

| | #271 (closed state) | **epic base** | |
|---|---:|---:|---|
| collected | 1491 | **1504** | **+13 denominator** |
| skipped | 22 | **4** | −18 |
| passed | 1462 | **1483** | +21 |
| failed | 7 | **17** | +10 numerator |

- **The "13 uncollected nodes" were not a defect. They were the closed state.**
  Scaffolding restored all 13 and collection returned to its pre-close value.
- **Eighteen of the 22 skips were one shape** — *"`specs/current` is absent"* —
  and now run. **The four survivors are all one line**,
  `test_workflow_close_keeps_the_ledger.py:92` (`CA-10-DF-12`), and **they unskip
  when `SS-01` repoints the ledger.**
- **The 3 vacuous passes are untouched by any of it, and they are the real
  work** — unlike a skip, they are invisible.
- **Ten new reds, each attributed** in the baseline. Five are `SS-00-DF-01`; one
  is #271 §7.1's own prediction firing (`test_card_has_one_home.py:126` hard-codes
  the dead ledger path and now demands the third carved exception); one is a test
  whose `R1` subject moved out from under it; one clears itself as tickets close.

**This is the charter's own rule in action: a red that appears after a metric is
fixed is not automatically a regression.**

---

## 2. The five goals

Read your ticket's `goals` block **before implementing**. The `expected_effect`
is the result your change is aiming at, not decoration.

| goal | baseline at `436c78c` | decided by |
|---|---|---|
| `GOAL-absent-input-consumed` | 48 instances across **30 of 43** verdict-producing modules; 1 fixed, 47 open. `R1` requires a demonstrated FAILING input; it does not require an ABSENT one | `SS-08` |
| `GOAL-tree-stabilizes` | recorded in this goal's baseline evidence, measured on this branch — reds, passes, skips, collection, plus 13 uncollected nodes and 3 vacuous passes | `SS-08` |
| `GOAL-judged-goals-compliant` | **0 of 20** judged goals have a baseline the evaluation can open: 8 directory, 10 summary, 1 unresolvable, 1 prose | `SS-08` |
| `GOAL-counted-figures-reach-the-record` | `scope` reads **0** counted figures on charters, plans, baselines and price tables; **3** on `NEXT-EPIC.md`. It recognises one sentence form | `SS-08` |
| `GOAL-four-results-stand` | four results standing at the base; two of the predecessor's four DISPROOFS did not | `SS-08` |

**There is no size goal, and that is a decision, not an oversight.** `#271` §3.1:
the change rule keeps old anchors, `R-H4` seals the record, and the close-out
writes a full `specs/.history` snapshot — so **net-additive is required by
construction**, and four epics running have called themselves simplifications and
come out net-additive. Setting a fifth line-count target would measure the
close-out, not the work. **Nothing in this epic is cut for being long.**

**`GOAL-four-results-stand` is carried forward unchanged** because it is the only
goal this programme has ever run that caught an epic guarding something already
false.

---

## 3. The first ticket, and the consumption this epic exists to land

**`GOAL-absent-input-consumed` is the reason for the epic.**

**The class: an instrument that returns a confident PASSING answer when handed an
absent or empty input.** 43 verdict-producing modules were swept, 30 carry the
defect, 48 instances filed with file, line, behaviour, reachability, reproduction
and correct answer — ledger rows `CA-10-DF-17`…`CA-10-DF-25`, all `carried` into
this epic. Full table:
`specs/results/scorecards/cut-the-apparatus/CA-10-absent-input/RESULT.md`.

| instance | behaviour |
|---|---|
| `generate_python.py:238` | absent/empty `invariants:` → `def validate_state(state): return None` — **a state oracle that passes every state. Two shipped examples carry it today**, with `validate_manifest` reporting zero errors |
| `corpus_diagnostics.py` | `passed = not over_cap` → **an empty corpus always passes** |
| `disposition.py` | duplicate keys → certified clean (repaired; **still blind at any indent other than four spaces**) |
| `blind_dispatch` | empty subject → PASS (repaired; its `UNDECIDED` branch is **dead code**) |
| `score_tools._finding_ids()` | ledger absent → empty set → **every `filed_as` reported fabricated** — the one that is fixed |

**The doctrine this earns — land it, do not just cite it.** Extend `R1`: every
instrument ships a demonstrated **absent-input** case, and the correct answer is
**UNDECIDED or a refusal — never PASS.** The fixed instance shows the shape, and
the repair was a **signature change**, `set[str]` → `set[str] | None`, *because
the old type could not distinguish "read and found nothing" from "read nothing",
and answered the second with the first.* That is the class in one line.

**Filing a finding routes it; it does not change what the substrate checks.**
`GOAL-consumption-obligatory` measured 1-of-41 and the epic then produced 57
findings while consuming almost none into its own checks. `SS-02` lands the rule
as an **executed check**, not prose. **A doctrine line with no instrument is a
preference.**

**Two corrections to the framing, and they matter for how you scope your work.**
Three of the five originally-named exemplars **were already repaired and nothing
in the record said so** — and each left a **named half** behind. **Do not assume a
filed finding is open. Check.** And: **measure before repairing; do not quietly
shrink the class.**

---

## 4. The integration point — what this repository is for

**No epic before the predecessor stated this. It is stated here.**

**Object level — every other repository.** A repo runs `git-epic-workflow`,
declares `epic_goals`, each naming a `harness`. `goals-and-evaluation.md`
**already permits that harness to be a judged procedure rather than a command** —
*"scored against `<rubric>` version N by two blind judges, evidence under
`<evidence_root>`"*. A `role: evaluation` ticket runs it on the integrated tip and
reports baseline → measured → target per clause. **That loop needs no new
mechanism.**

**Meta level — this repository.** `tla-spec-dev` builds and validates the card
those harnesses name, **and uses itself as the subject**. Every result is doubly
loaded: about the instrument *and* about the toolchain that produced it. **That is
why the predecessor's best findings are about its own charter rather than anyone's
code — the subject and the instrument are the same object.**

**The join is one file: `git-epic-workflow/references/goals-and-evaluation.md`.**
The only artifact that both every epic in every repo reads *and* can name a judged
instrument. **It is the integration point across observed self-improvement**, and
the path by which the card reaches projects that will never read this repository.

**Its measured state, the oldest open wound: `0 of 20` judged goals have a
baseline the evaluation can open** — 0 of 18 when #271 was written; the numerator
held and the denominator rose. `SV-05` established the cause: an agent on the
*unpatched* text already produces a card-backed, sealed, never-averaged baseline;
what it cannot do is find a branch to stand in, so it routes a judged instrument
that exists into *"harness does not exist"*. **The four escalated diffs are now
merged upstream and the installed text carries them** — verified on this
branch's home. **The compliance rate of zero is ours**, and `SS-03` is the ticket
that pays it down.

---

## 5. Do not cut these

An epic told to stabilize will be tempted by all of them because they are long.
Each earns its keep, several measurably.

- **`goals-and-evaluation.md` §"The instrument does not have to be a command"** —
  §4 above. **Its length is the mechanism.**
- **`deferment.md`:** *"An entry with no reproduction is not a finding, it is a
  hunch — do not file it."* One sentence; it is why 262 of 267 rows carried a
  reproduction.
- **`git-issue-workflow` §"The one command: `wt`"**, including the exit-code
  table. **Its redundancy is the fix for a measured failure.**
- **The `&&`-chaining comments citing the W2 eval** — a measured agent failure
  fixed by a shell operator and a comment. Cheapest fix-to-harm ratio in the set.
- **`git-issue`:** *"An issue names a rubric; it never copies one."*
- **Rule 11 of `git-epic-workflow`.** It is right.
- **`scope`, `seal`, `contested`, the blinding mechanism, `R-H1`/`R-H2`/`R-H4`/
  `R3`, and the version/served double seal** — `RM-02`: *"the substrate's best
  export, and the epic should be careful not to cut them for being unglamorous."*
- **`candidate_note_bar.py`** — its test is **the only one in the repository
  pinning the card at 6,281 bytes.**

---

## 6. The static-gates doctrine, as adjudicated — and what it permits this epic

**Wording that survives, and you may not quote a shorter version of it:**

> **No static check in this project has ever been shown to catch a semantic
> defect in shipped program code.**
>
> **Static checks over this project's own record, metadata and method have caught
> real defects repeatedly and changed outcomes.** **3 catches : 1 false refusal**
> last epic.
>
> **Those are two different claims.** And the first **is not evidence about
> gates** — *"zero observations of X is not evidence about X when the instrument
> was never aimed at X… That is a fact about what the project chose to build, not
> a fact about gates"* (the blind judge, Arm J).
>
> **The real defect is that it was unfalsifiable as stated**, which is exactly
> what made it usable to refuse things for eight cycles. *"'Seven cycles, zero
> bugs' has never been audited."* **Nobody may invoke the headline until it has
> been.**

**So, operative for this epic:** the doctrine **may** refuse a gate over subject-
program content, on a burden-shifting basis. It **may not** refuse a check over
**this project's own record or metadata** — that population has three catches and
a measured record of changing outcomes.

**`SS-02`'s absent-input check is in the permitted population**, and it is
scoped to it: it checks this project's own instrument register. **It is not a gate
on an adopter's code.** `SS-04`'s recogniser is **explicitly not a gate** and
**reports UNREACHABLE by default.**

---

## 7. Doctrine — all measured

- **`MF-020`** — never add an axis, test, rung or case fitted to a known answer.
  **Refused correctly at least five times**, including a party declining to
  soften its own rule after seeing its own data.
- **`R1`** — a demonstrated **failing** input on a **real subject** — **and now a
  demonstrated ABSENT input** (§3). `SS-02` lands the extension; every ticket
  after it complies.
- **`R-H1`/`R-H2`** — same example, unchanged instrument, same architecture tag.
  Never average across examples or versions.
- **`denominator_rule`** — if a count moves, say whether the numerator rose or the
  denominator fell. **It applies to the figures in your own work order**: §0 above
  is this rule applied to issue #271.
- **Seal predictions BEFORE measuring**, in a commit, with a timestamp. **If every
  prediction passes, report it as an ALARM.**
- **File findings; fix nothing during a measurement — then change what the
  substrate CHECKS.** A finding that is only filed has been routed, not consumed.
- **Ask every blind agent what it REJECTED** — it produced more than any check,
  again. **And ask what was LOADED in its packet**: *"stripping conclusions off a
  selected set of facts does not make the selection neutral"* (`CA-08-DF-07`).
- **Re-probe blindness every round.** `--safe-mode`'s memory behaviour is
  **observed four times and specified zero times**, and `check` reads the agent's
  report rather than the harness's configuration. **Verify each round; do not
  trust the flag.** A neutral cell is required as well — safe-mode does not strip
  `gitStatus`. **And the cell path check refuses only `tla-spec`/`spec-dev`, so a
  path naming the *ticket* passes.** Do not name your cell after your ticket.
- **Do not read `blind` as `unbiased`, and do not call a dictated answer
  unprompted.** The verdict is the agent's; the sentence may be the probe's. Say
  which.
- **Every research ticket runs its own proposed rule against the sealed record
  before it ships**, and reports what the rule refuses.

---

## 8. Operational rules this project has paid for

- **Test command:** `uv run --with pytest --with pyyaml -m pytest tests -q`.
  Without `--with pyyaml`, 12 tests go phantom red. **The epic-base figure is
  `17 / 1483 / 4 / 1504`, in `GOAL-tree-stabilizes`'s baseline evidence, and every
  ticket compares against THAT** — not against a recollection and not against
  #271's `7 / 1462 / 22 / 1491`, which describes the closed-workflow state.
- **Do not edit files a running measurement reads.** Six parties did this in one
  epic, starting with the owner — **and this epic's owner did it at kickoff**,
  scaffolding `specs/current` three minutes into a 26-minute suite run that had
  already collected. That run is preserved, labelled, and is not the baseline:
  `kickoff/pytest-CONTAMINATED-scaffold-landed-mid-run.txt`. **It was kept rather
  than deleted, because deleting it removes the record of what was measured.**
- **`close ticket` refuses while the plan says `planned`.** Flip your entry first.
- **The ledger is cumulative — append; never rewrite.** This epic's live path is
  **`specs/deferred_findings.yaml`**, carrying all **296** inherited rows. Until
  `SS-01` merges, the instruments still name the dead per-epic path, so invoke
  `python3 scripts/disposition.py --ledger specs/deferred_findings.yaml`.
- **`wt new` branches from the LOCAL ref, and `main` in the primary checkout is
  stale at `08d1d6a` right now.** Your assignment names a resolved commit OID.
  **Use it. Verify your branch point.**
- **Never invoke `tla-spec-dev` from PATH** — use
  `python3 scripts/tla_spec_dev.py --spec-root specs …`.
- **Skills are READ from this repository and NEVER edited.** Anything that must
  change in a `SKILL_MANAGER_HOME` is **proposed as a diff and escalated**.
  **`spec-double-compiler` is deliberately NOT synced for the duration** —
  owner's decision, recorded: it ships the whole 402 MB repository including every
  charter and a stale `NEXT-EPIC.md`, and syncing it mid-epic would move text
  under tickets already running and load the predecessor's conclusions onto disk.
  `deploy-helm` and `debugging` **were** synced in both tiers at kickoff.
- **Scratch to a ticket-specific path.** Two concurrent tickets corrupted a shared
  `baseline.txt`.
- **Never hand-roll a wait loop. Never kill a process by name alone**, and check
  whether a process is yours first.
- **Read the validator's output, not its exit code.**

---

## 9. What the final evaluation ticket must do

`SS-08`, `role: evaluation`, promoting last, owning every goal.

1. **Decide every goal clause by clause.** Never collapse a multi-clause target to
   one word — a ledger storing one verdict per goal **will pick the flattering
   clause**. The predecessor's evaluation split a clause to gain a MET *and* split
   another to invent a MISSED, and withdrew both. **Splitting a clause to add a
   MET and splitting one to add a MISSED are the same error.**
2. **Report the tree, not just the count** — reds, passes, skips, collection, and
   every movement attributed with numerator and denominator named.
3. **Run its judged work through `--safe-mode` plus a neutral cell, and state
   exactly what its judges received either way** — including that **the agent
   selecting the packet is not blind**, and that the evaluating session itself
   carries `MEMORY.md` unless it is run from a neutral cell.
4. **Seal predictions before measuring, in a commit, with a timestamp. If every
   prediction passes, report it as an ALARM.**
5. **Re-derive every figure it quotes.** The predecessor's evaluation published
   three refuted figures and its headline finding was refuted on review — off by
   1,000 on its own enumeration.
6. **Report findings by channel with the token basis named**, and say which
   tickets recorded their own. "Not instrumented" is the honest answer, not a gap.
7. **File findings; fix nothing.** And **name what should change in the substrate
   as a result.**
8. **Do not route its own findings to itself.** `CA-05-DF-03` face (a):
   self-routing satisfies `D3` with full marks and means nothing.

---

## 10. Open decisions this epic inherited, and how they were decided

| # | inherited from #271 | decision |
|---|---|---|
| 1 | the cumulative ledger lives in a per-epic directory | **Moved to `specs/deferred_findings.yaml`.** Owner moved the data at kickoff, all 296 rows preserved and counted before and after; `SS-01` owns the consumer migration and must **verify** the "10 live files / 25 archival scorecards" figure rather than inherit it. The 25 archival scorecards **must not be rewritten.** |
| 2 | appending to an archived ledger falsifies `resolve_ledger`'s "frozen at that close" claim (`CA-10-DF-10`) | **`SS-01` decides it on the record.** Already true twice. |
| 3 | `score_tools.py:3448` globs the dead directory; `DEFAULT_SWEEP`'s docstring declares `specs/.history/**` out of scope | **`SS-01` decides.** Cost of leaving it: 17 REFUTED figures currently unswept. Changing it overrides a written decision — say so if you change it. |
| 4 | 29 `SF-*` skill findings are unfiled | **Filed into `specs/deferred_findings.yaml` by whichever ticket touches the surface**, under the epic's batch policy. Not a ticket of its own. |
| 5 | `spec-double-compiler` ships the whole repository — an unmeasured contamination channel | **Not synced for the duration** (§8). Measuring what the installed unit puts in a dispatched agent's context is **carried, not scheduled** — it is the successor's. |
| 6 | should the epic set a size target | **No.** §2. |

---

## 11. The standing rule

**A low or unflattering result is the preferred outcome.**

The predecessor's best material: three of its four cut targets were fiction; its
charter asserted a claim the record refutes; its evaluation's excuse for its own
failure was an instance of that failure; and the instrument its owner proposed as
the durable fix **cannot read the documents that direct the work**.

**An epic that closes with only good news about itself has not been measured.**
