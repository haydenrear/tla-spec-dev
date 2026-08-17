# SS-02 — `R1` gets a third clause, and it is executed

**The slice was the RULE and the INSTRUMENT, not the repairs.** No instance of
the absent-input class was repaired here. That is `SS-05`'s, deliberately, so
`SS-08` measures a class nobody shrank while measuring it.

> **READ §10 FIRST.** An independent reviewer of PR #284, instructed to refute,
> returned **CHANGES** with eleven findings — and **both HIGH findings were
> instances of the class this check exists to close, inside the check.** An
> all-waived contract reported `SATISFIED` with zero demonstrations run; the
> "mandatory" exit-code declaration was evaded by deleting one line. §1–§9 were
> written before that round and are unedited except where a figure in them was
> wrong; **§10 is what moved and why.**

---

## 0. Every figure in this file names its tree, because a figure is a joint property of the artifact and the tree

| label | commit | what it is |
|---|---|---|
| **base** | `48f9c7e` | the OID `origin/epic/stabilize-substrate` resolved to when this worktree was created, measured **before `open ticket SS-02`** |
| **epic tip** | `eb2567b` | the epic branch after `SS-03` merged, which this branch reconciled with |
| **tip (pre-close)** | `9e6e015`+ | this branch, reconciled, **before `close ticket SS-02`** |
| checkout | `/Users/hayde/IdeaProjects/wt-epic-stabilize-substrate-SS-02` | `SS-01-DF-03`: `audit` and `scope` answer differently under different roots |

---

## 1. The rule, and why it is three states and not two

`R1` requires a demonstrated **failing** input on a real subject. It does not
require a demonstrated **absent** one. `CA-10` swept 43 verdict-producing
modules and found **48 instances across 30 of them** answering PASS — clean,
disposed, `0 violation(s)`, exit 0 — to an input that is absent, empty or
unparseable, and **every one of the 48 satisfied `R1` in full**.

**The extension, landed as an executed check rather than a doctrine line:**

> Every instrument in this repository's own instrument register ships a
> demonstrated absent-input case, and the correct answer is **UNDECIDED or a
> refusal — never PASS**.

**Three states, and wave 1 of this epic paid for the third.** `CA-10-DF-11`
repaired the **absent** ledger with the signature change `set[str]` →
`set[str] | None`. `SS-01` repaired the **wrong** one. An independent reviewer
then handed the result a ledger that **existed and named nothing** and got **14
confident fabrication accusations against real citations** (`SS-01-DF-04`).
**A fallback that merely moves the false PASS to a rarer input has not fixed the
class**, so a contract distinguishing only absent-from-present satisfies nothing
here:

| state | the input is |
|---|---|
| `absent` | not in the tree at all |
| `unreadable` | there, and unreadable as itself — empty, truncated, malformed |
| `empty` | read and parsed perfectly, and genuinely naming nothing |

**And distinguishability is found by EXECUTION, not by reading the contract.** A
register can declare three states while the instrument collapses two of them,
and reading the TOML cannot tell. Each state's real output is checked against
the other states' declared markers; a collapse must be **declared with a
reason** or the check refuses. That is `SS-01-DF-04` consumed into what the
substrate checks, rather than filed.

**Where it lives.** `python3 examples/validation/scorecards/score_tools.py
absent-input`, over `examples/validation/instruments/instruments.toml`. Written
up in `references/eval_scorecard.md` § *An instrument's absent input*, and in
the register's own preamble beside the three slots it joins.

---

## 2. `R1` applied to the check itself: a demonstrated refusal on a REAL instrument

**Subject: registry row `scorecard-audit` — `score_tools.py audit`**, the
instrument whose `_finding_ids` signature change is the worked shape of the
whole class. **Not a fixture:** both runs read the shipped register; the BEFORE
run removes exactly one block from it.

| run | command | result |
|---|---|---|
| **before** | `absent-input --contract-only --only scorecard-audit` over the register **minus** `[instrument.absent_input]` | **exit 1**, `NO CONTRACT` |
| **after** | `absent-input --only scorecard-audit`, all three states **staged and executed** | **exit 0**, `SATISFIED` |

Transcript: `R1-refusal-on-a-real-instrument.txt`.

**What the three states actually do.** Each stages a tree that **symlinks every
repository entry except the input under test** and substitutes it. That is not
convenience: `audit` verifies **133 sealed digests** against paths under
`REPO_ROOT`, so a demonstration that *copies* the repository to move one file
produces 133 seal violations that say nothing about the ledger. Measured — the
first attempt did exactly that.

| state | the ledger is | `audit` answers |
|---|---|---|
| `absent` | no live file, no close recording one | `UNVERIFIED no findings ledger this tool can READ ids from: no ... and no workflow close under specs/.history/ records one` |
| `unreadable` | `findings:\n  - id: [unclosed` | `UNVERIFIED ... exists but names no findings (empty, unreadable or malformed)` |
| `empty` | `findings: []` | **the same line** |

**All three are UNDECIDED, and all three exit 0.** Both of those facts are
declared in the register rather than smoothed over, and both became findings —
§5.

---

## 3. The check's own answer to an absent input

The self-referential trap, answered rather than asserted. **If any run below had
exited 0 it would be the 49th instance of the class, shipped inside the fix for
the class.** Transcript: `the-checks-own-absent-input.txt`.

| input | first line of output | exit |
|---|---|---|
| register path with no file at it | `UNVERIFIED: [absent] no instrument register at …` | **2** |
| zero-byte register | `UNVERIFIED: [unreadable] … is EMPTY (0 byte(s))` | **2** |
| register that does not parse | `UNVERIFIED: [unreadable] … DOES NOT PARSE` | **2** |
| register that parses and declares 0 instruments | `UNVERIFIED: [empty] … PARSES AND DECLARES 0 instruments` | **2** |
| register whose every row is `not-an-instrument` | `UNVERIFIED: [empty] … EVERY ONE is family = "not-an-instrument"` | **2** |
| `--only` matching nothing | `UNVERIFIED: [empty] --only [...] selected 0 of 56 instrument(s)` | **2** |

**Six distinct sentences, six exit 2s, no 0.** Two further places the same
question is asked of it: `--contract-only` reads the TOML and executes nothing,
so it **cannot** report 0 — it reports `DECLARED (not executed)` and exits 2;
and `--state`, which narrows execution to a subset, reports `PARTIAL` and exits
2, because "all three reproduce" and "no two states collapse" are properties of
the **set** and a subset answering with the whole set's word is an
empty-selection answer with extra steps.

**One collision, disclosed, not hidden.** `argparse` also exits 2 on a usage
error, so the **code alone** does not separate UNDECIDED from "you typed the
command wrong". Found the way it will be found in the field: a transcript loop
mis-quoted its arguments and produced six argparse errors that read as six
correct UNDECIDED verdicts until the output was read. The **first output line**
always separates them, and every contract asserts on it. `SS-02-DF-02`.

---

## 4. The count — this command's product, with numerator and denominator named

Executed run over the whole register
(`absent-input-whole-register-executed.txt`, exit 1):

```
instruments in the register                 56
selected                                    56
contract EXECUTED and holding                2      <- scorecard-audit, absent-input-check
contract declared, not executed              0
contract executed over a SUBSET of states    0
WITHOUT one                                 54
with a contract that did not hold            0
states declared unreachable, with a reason   0
DECLARED indistinguishable state pairs       1
```

**2 of 56. There is no target on that ratio** and a high `WITHOUT` count is the
honest outcome — a threshold on a repair count before the check existed would be
`MF-020`.

**`56`, not `55`, and the denominator moved for a stated reason:** the register
carried 65 rows / 55 instruments at the base; this ticket added **one row**, the
check itself, so it is inside the population it measures. **That is denominator
movement, +1, and it is this ticket's.**

**Note what this count is NOT.** It is a count over the **instrument register**
(56 rows). `GOAL-absent-input-consumed`'s other denominator is the **48
instances across 30 of 43 verdict-producing modules** from `CA-10`'s sweep.
They are different populations and neither is a rate over the other. **This
ticket moved the instance count by zero, deliberately** — §6.

---

## 5. Findings filed: nine, all reproducible

**Four before review, five after it.** This section describes the first four;
`SS-02-DF-05` … `-09` are in §10, and **two of those five are repaired here
rather than routed** — the review found them inside the check itself.

Ledger `specs/deferred_findings.yaml`, **appended only**: 308 rows at the base →
**317** after `SS-03` merged → **321** before review → **326** here. Row count
only rises, all ids unique; the tail conflict with `SS-03` was resolved by
keeping both sets **in promotion order** (`SS-03` at 20, then `SS-02` at 30).

| id | what | routed to |
|---|---|---|
| `SS-02-DF-01` | **`audit` cannot tell a malformed ledger from a deliberately empty one.** `_finding_ids` reads ids with a **regex** and never parses the file, so a truncated write, a bad merge, a zero-byte file and a correct `findings: []` are one state to it. The **verdict is right in all four** — this is not the false-PASS class — but a half-written ledger is reported in the exact words of an intentional one. Found by the check's own execution-based distinguishability test. | `SS-05` |
| `SS-02-DF-02` | **UNDECIDED exit 2 collides with argparse's usage-error 2.** The shape this command exists to report, recorded against the command that reports it. | `SS-08` |
| `SS-02-DF-03` | **`audit` answers UNDECIDED in its text and PASS on its exit code.** `0 violation(s)`, exit 0, over a tree it could not audit. The absent-input class **surviving its own repair one layer out**: `CA-10-DF-11` and `SS-01-DF-04` moved the answer from wrong to undecided and left the carrier unable to say so. The check makes `exit_code_cannot_carry_the_answer` **mandatory** for any state that answers `undecided` and exits 0. | `SS-05` |
| `SS-02-DF-04` | **The register's own guards cannot see the new slot.** `demonstrate.py`'s `SLOTS` literal is `("failing","passing","blind_spot")` and four tests iterate it, so an absent-input contract could cite a nonexistent pytest node or assert only an exit code and no sibling guard would notice. The check imposes the equivalent itself, so nothing is unpoliced **today** — but the obligation now lives in two places. `FI-04-DF-04`'s shape. | `SS-06` |

`disposition.py --ticket SS-02` → **`DISPOSED ticket SS-02: 4 findings, all three
clauses hold`** — and **`4` is not `9`**. The instrument selects a row only when
`found_by` starts with the ticket id *and* the row id does, so the five
review-round rows are invisible to it. Selected by id prefix instead, **all nine
pass all three clauses, `0 of 9` fail.** See §10.5: the under-count is exactly
the externally-found rows, which is the direction that flatters the ticket.

---

## 6. The suite — five numbers that sum, at both ends, every movement attributed

Command, exactly: `uv run --with pytest --with pyyaml -m pytest tests -q`.

| | failed | passed | skipped | **xfailed** | collection |
|---|---:|---:|---:|---:|---:|
| **base `48f9c7e`**, before `open ticket` | **8** | **1509** | **0** | **1** | **1518** |
| epic tip `eb2567b` (`SS-03`'s own post-close figure, **not re-derived here** — §6.3) | 7 | 1521 | 0 | 1 | 1529 |
| **tip, pre-close** | **7** | **1548** | **0** | **1** | **1556** |

`8 + 1509 + 0 + 1 = 1518`. `7 + 1548 + 0 + 1 = 1556`. Both exact.
`pytest-base-48f9c7e.txt`, `pytest-tip-preclose.txt`,
`collect-base-48f9c7e.txt`, `collect-tip-preclose.txt`.

**The base figure `8 / 1509 / 0 / 1 / 1518` is the owner's `50046b2` figure
re-derived at `48f9c7e` in a fresh worktree and it matches exactly**, so the
owner-corrections commit moved nothing in the tree.

### 6.1 Collection `1518 → 1556`, attributed node by node

Not by arithmetic: by diffing the sorted `--collect-only` node ids at both
trees. `collection-attribution.txt`.

| movement | nodes | cause | whose |
|---|---:|---|---|
| **+23** | `tests/test_absent_input_demonstrations.py`, all of it | the new demonstrations | **SS-02 — pure denominator movement** |
| **+4** | `test_spec_yaml_valid` re-parametrised over `specs/tickets/SS-02/`: `complexity_ledger.yaml` → `…0`/`…1`, `ticket.yaml` → `…0`/`…1`, `spec_manifest.yaml6`, `spec_manifest.yaml7` (−2 +6) | **`open ticket` inflates collection by +4**; `close ticket` removes it | **SS-02, and it does not survive the close** |
| **+10** | `tests/test_goal_baseline_is_a_card.py` | `SS-03`'s recogniser repair | SS-03 |
| **+1** | `test_spec_yaml_valid[baseline_resolution_index.yaml]` | `SS-03`'s new evidence file | SS-03 |

`23 + 4 + 10 + 1 = 38`, and `1518 + 38 = 1556`. **Nothing in the movement is
unattributed.**

**`expected_effect` for `GOAL-tree-stabilizes` said collection would RISE by the
new demonstrations and that this is denominator movement. It did, by 23, and it
is.** A pass rate that improved because 23 passing tests were added is not a
stabilised tree and is not claimed as one.

### 6.2 Reds and passes

**Reds: 8 at the base → 7 at the epic tip → 7 here. This ticket moved the red
count by ZERO.** The one that went green
(`test_goal_baseline_is_a_card::test_a_real_epic_plans_judged_baseline_cannot_be_re_opened`)
is **`SS-03`'s repaired numerator**, not mine. The 7 survivors carry the same
causes they carried at the epic tip:

| red | cause | status |
|---|---|---|
| `test_architecture_tags::test_the_same_tag_control_holds` | `RM-06-DF-01` | deliberate, untouched |
| `test_instrument_demonstrations::test_every_declared_path_exists` | `CA-04-DF-04` (`scripts/run_kill_test.py` does not exist) | declared, untouched |
| `test_instrument_demonstrations::test_every_fast_demonstration_reproduces` | `CA-04-DF-04`, same missing file | declared, untouched — **and see below** |
| `test_source_citations…[specs/current/spec_manifest.yaml]` | scaffolded manifests | inherited |
| `test_source_citations…[specs/desired_program_model/spec_manifest.yaml]` | same | inherited |
| `test_source_citations…[specs/program_model/spec_manifest.yaml]` | same | inherited |
| `test_ticket_retirement…matching_close_receipts` | `ticket SS-02 is not closed: status=planned` … and 6 more | expected, self-clearing per ticket |

**`test_every_fast_demonstration_reproduces` deserves a sentence, because this
ticket added rows to the file it reads.** It was red at the base for
`CA-04-DF-04` and it is red at the tip for `CA-04-DF-04`. The new row's own two
demonstrations were run in isolation and **both reproduce**:
`python3 examples/validation/instruments/demonstrate.py --only absent-input-check
--tier fast` → `fail ok / pass ok`, *"Every declared demonstration reproduced."*
**Nothing this ticket added contributes to that red.**

**Passes: 1509 → 1548, `+39`.** `+38` is the collection movement above; `+1` is
`SS-03`'s repaired red. **Skips 0 → 0. Xfailed 1 → 1** (`SS-01`'s
`xfail(strict=True)` pinning `SS-01-DF-01`, untouched).

### 6.3 What I could NOT do, stated rather than papered over

**I did not independently re-derive the epic tip `eb2567b`.** The row above is
`SS-03`'s own post-close figure from
`specs/results/scorecards/stabilize-substrate/SS-03/pytest-reconciled-POSTCLOSE.txt`,
quoted, not measured by me. It is arithmetically consistent with both figures I
*did* measure — `1518 + 11 = 1529` from the node diff, and the single red that
moved is `SS-03`'s own — but **a quoted figure is a quoted figure**, and this
epic's record says every party that quoted one eventually corrected it. A
20-minute run at `eb2567b` in a third worktree is what would settle it and I did
not spend it.

### 6.4 The cost this ticket adds to every later ticket's suite run

**`tests/test_absent_input_demonstrations.py` takes 5m16s on its own** (23
passed), and the whole suite went **23:25 at the base → 27:48 at the tip**. The
demonstrations are genuinely executed — six staged trees and six real
invocations of `audit` at roughly 27 seconds each — and `--state` exists so the
expensive ones can be run one state at a time. **That is a real cost and it is
disclosed rather than absorbed.**

---

## 7. `close ticket` — the two figures, and which is authoritative

`close ticket` **seals the history entry and deletes the workspace in one
operation**, so the sealed entry can never describe the tree it produces, and
`R-H4` forbids editing the entry afterwards. Both figures are therefore
published, and both were measured.

| | failed | passed | skipped | xfailed | collection |
|---|---:|---:|---:|---:|---:|
| **pre-close** — what the sealed summary carries | **7** | **1548** | **0** | **1** | **1556** |
| **post-close** at `711cd02` | **7** | **1544** | **0** | **1** | **1552** |
| **final**, after merging owner commit `0f31cc3` — **the tree this PR merges** | **7** | **1544** | **0** | **1** | **1552** |

`7 + 1544 + 0 + 1 = 1552`. **The final figure is the authoritative one for
`SS-08`**, because it describes the tree that is merged. The pre-close figure is
authoritative for nothing except what the close itself saw.

**A third full run, and it was not wasted even though it moved nothing.** The
epic branch advanced to `0f31cc3` — an owner commit correcting
`GOAL-four-results-still-stand/baseline.md` and amending `SS-07`'s and `SS-08`'s
plan entries — **after** this ticket had reconciled at `eb2567b` and closed.
Nothing in it touches `SS-02`'s entry, its goals, its conflict keys, or
`schedule_revision`, and the assignment equality check was re-run against the
merged plan and holds. It **does** touch a baseline and the plan, both of which
several tests read, so the matrix was rerun rather than argued about:
**`7 / 1544 / 0 / 1 / 1552`, byte-for-byte the same verdict set.**
`pytest-tip-final-0f31cc3.txt`, `collect-tip-final-0f31cc3.txt`,
`spec-unit-SS-02-final.txt` (exit 0, 56 passed). **If the epic tip moves again
before this PR merges, that is disclosed here rather than chased.**

**The whole of the `−4` is the `open ticket` inflation being removed, and it is
identified node by node**, not inferred from the arithmetic —
`collect-tip-postclose.txt` diffed against `collect-tip-preclose.txt`:

```
removed  test_spec_yaml_valid[complexity_ledger.yaml0]  [ticket.yaml0]
         test_spec_yaml_valid[complexity_ledger.yaml1]  [ticket.yaml1]
         test_spec_yaml_valid[spec_manifest.yaml6]      [spec_manifest.yaml7]
added    test_spec_yaml_valid[complexity_ledger.yaml]   [ticket.yaml]
```

Six out, two back in: the parametrisation de-duplicates its ids only while two
files share a basename, so removing `specs/tickets/SS-02/` collapses the pairs
back to the single ids the base tree carried. **Net `−4`, exactly the `+4` §6.1
attributed to `open ticket`. Passes fall by the same 4. No red moves.**

**`test_ticket_retirement` is still red and correctly so:** it now complains
about five planned tickets instead of six, `SS-02` having dropped off the list.

### 7.1 The sealed copy and this file have diverged, on purpose — and where

`specs/.history/stabilize-substrate-epic/ticket-002-SS-02/results/RESULT.md` is
the byte-frozen copy the close took. **`R-H4` leaves it there.** This file, at
`specs/results/scorecards/stabilize-substrate/SS-02/RESULT.md`, is the live one
and is the one to read.

**Where exactly they diverge, since a vague answer to that is what a reader
cannot check.** The sealed copy is **312 lines** and **carries §7, §8 and §9** —
it is not truncated. It first diverged **inside §7**, at its line 276: it
describes the post-close figures as living in files *"measured after the
close"*, because at seal time they had not been measured yet, where this file
carries the measured table. **Review round 2 then widened the gap deliberately**
— the banner at the top, the corrected counts in §5, this subsection, and all of
§10 postdate the seal. The sealed copy is the close's own record of what it saw;
**this file is the current one and is the one to read.**

> **CORRECTED.** The PR body first said the sealed copy *"stops at §6"*. It does
> not, and an independent reviewer of PR #284 checked. The claim was written
> from what I expected the close to capture rather than from reading the file it
> wrote — which is this epic's most repeated error shape, committed here about
> the artifact documenting that error shape.

`SS-01` hit the same divergence one ticket ago (`8/1508/0/1516` sealed against
`8/1504/0/1512` live). It is structural, not a mistake either of us made.

---

## 8. Goal contribution

| goal | contribution | expected | measured |
|---|---|---|---|
| `GOAL-absent-input-consumed` | direct | clauses (a), (b), (e) move from "no check exists" to "an executed check with a demonstrated refusal on a real instrument"; **no effect on the instance count** | **moved as expected.** (a) the check exists and is executed; (b) demonstrated refusal on `scorecard-audit`, exit 1 → exit 0; (e) it reads one file, is wired into no close path, and `test_the_check_gates_nothing` executes that. **Instance count moved by 0** — no instance repaired. |
| `GOAL-tree-stabilizes` | guard | collection RISES by the new demonstrations; report it as denominator movement | **moved as expected.** `+23` nodes, denominator, named; reds flat at 7; every unit of `1518 → 1556` attributed node by node. |
| `GOAL-four-results-still-stand` | guard | none expected | **no measurable movement.** `audit` → `0 violation(s)`, exit 0 (`audit-tip.txt`). `serve | wc -c` = **6,281**, digest `sha256:2d7d4a0506d9b259` — **byte-identical to the base** despite `references/eval_scorecard.md` growing, because `serve` renders only dimensions, anchors, caveats and scoring rules. `scope` exit 1 (its own demonstrated failing input), `contested` exit 0, `tags` exit 0 (`instruments-still-run.txt`). |

`GOAL-absent-input-consumed` clauses (c) and (d) are **not** this ticket's:
(c) is the re-sweep, `SS-08`'s; (d) binds every repair, and this ticket shipped
none.

---

## 9. The validation matrix

| entry | command | result |
|---|---|---|
| `tlc` | — | **N/A: no TLC target exists at this tree.** `run` accepts only `spec-unit-tests` and `effect-conformance`. `SS-00-DF-05`. |
| `spec_unit` | `python3 scripts/tla_spec_dev.py --spec-root specs run spec-unit-tests` | **exit 0, 56 passed** — `spec-unit-SS-02.txt` |
| `repository_unit` | `uv run --with pytest --with pyyaml -m pytest tests -q` | §6 |
| `graphs` | — | none declared |
| `spec_graph` | — | **N/A, and the no-op is stated rather than skipped:** this ticket changes a measurement instrument and the instrument register. Ticket-local `desired/` and `current/` are byte-identical to each other and to the whole-program state (`diff -rq` clean), and no `External.tla` surface, action, invariant or model config moved. |

---

## 10. Review round 2 — the check for the class contained the class, twice

PR #284 went to an independent reviewer instructed to **REFUTE**. Verdict:
**CHANGES**, eleven findings, two HIGH. **Both HIGH findings are instances of
the absent-input class, inside the check built to close it.** That is the most
on-thesis result this ticket produced and it is not buried.

### 10.1 What the reviewer verified that I had not

Recorded first, because a review that only lists defects is not a measurement:

- **My staging is a genuine control, and the reviewer ran the control I did
  not.** Symlink-everything *including* the ledger → 0 UNVERIFIED, 0 violations,
  exit 0, 18,900 chars. So the BEFORE/AFTER difference comes from the input
  under test and not from the staging. **I should have run that arm myself.**
- The BEFORE/AFTER pair survives being run **symmetrically**.
- **My declared collapse is stronger than I claimed:** `unreadable` and `empty`
  produce **byte-identical 19,222-character outputs**. `SS-02-DF-01` understates
  itself.
- `2 of 56` re-derives exactly; the `+1` self-inclusion is legitimate;
  `48 → 48` confirmed by **zero deletions** in the diff; `R-H4` absolute across
  144 files, all `A`, zero `M`/`D`; the suite exact at the head; node diff
  `34 added / 0 removed`; all four ledger reproductions run; and my 5m16s cost
  figure measured at 4:46 against it — inside run-to-run variance.

### 10.2 The two HIGH findings, both repaired, both filed

**`SS-02-DF-05` — an all-waived contract was reported SATISFIED and counted as
EXECUTED.** One row, three states, each `unreachable = "cannot be constructed"`:
`SATISFIED`, `contract EXECUTED and holding 1`, footer *"every state
reproduced"*, **exit 0**, with **zero demonstrations run**. That is **sub-shape 7
of this command's own taxonomy — an empty selection reported as a satisfied
population — inside the fix for the class.** Three places promised the opposite,
including `score_tools.py`'s own comment `# counted and printed separately,
NEVER as satisfied` **one line above the code that did the opposite**. It
shipped because `unreachable` **had no test**.

Repaired: its own verdict `WAIVED (n of 3)`, its own bucket `waived_rows`
**inside** the identity assertion that the buckets sum to `selected`, its own
printed section, and **exit 2** — nothing refused, nothing demonstrated. The
affirmative footer now prints only when **every** selected row is `SATISFIED`.
Four tests pin it. **A bucket that was not in the sum is how the fall-through
survived**, and the report printed an identity its own buckets did not satisfy.

**`SS-02-DF-06` — the "mandatory" `exit_code_cannot_carry_the_answer` was
opt-in.** The rule read the **declared** exit code, and `_absent_judge` compares
the exit code only when one is declared — so **deleting one line** disabled the
comparison *and* the rule that depends on it, and a contract answering
`undecided` while exiting 0 reported `SATISFIED`. Repaired in **both**
directions: `expect_exit` is now required on every state, and
`absent_observed_problems` applies the rule to the **observed** exit code, so a
contract that declares a nonzero exit and then observes 0 is refused too.

**And one more, the reviewer's own, found while reproducing the first:** a
register row with no `id` died with `KeyError: 'id'` and a traceback. **A
traceback is not one of the three answers**, and a register unreadable *as a
register* is an absent-input case for this check like any other. Rows are now
validated on the way in; a row missing `id` or `family` answers
`UNVERIFIED: [unreadable]`, exit 2.

### 10.3 The other nine, and what happened to each

| # | finding | disposition |
|---|---|---|
| F3 | `SS-02-DF-04` said **four** tests iterate the `SLOTS` literal. **There are two** (`:674`, `:751`), and the row's own grep returns 2. | **corrected in place** before merge, with the original wording quoted in the row |
| F4 | My own `R1` demonstration summary published **"53 of 55"** where the executed check says **54 of 56** — neither defensible reading. | **corrected** in `instruments.toml` |
| F8 | *"No file in `CA-10`'s 48-instance table was edited"* is **false** — `score_tools.py` carries five of the 48 and this ticket shifted all five citations **+9**. | **corrected**, with the full `+9` mapping in `GOAL-absent-input-consumed/SS-02-the-check-exists.md`; `48 → 48` stands on **zero deletions** |
| F9 | *"The sealed `RESULT.md` stops at §6"* is **false** — it carries §7–§9 and diverges mid-§7 at its line 276. | **corrected**, §7.1 |
| F10 | Out-of-key disclosure list incomplete. | **completed**, §10.4 |
| F5 | Collapse detection compares author-declared markers, never verdicts or exit codes — three identical verdicts differing only in an echoed path pass. | **`SS-02-DF-08`**, routed to `SS-05` on owner instruction |
| F6/F7 | The affirmative footer printed unconditionally; `--only known --only typo` drops the typo silently and exits 0. | **`SS-02-DF-07`**, routed to `SS-05`. **Say plainly:** the footer half was closed as an unavoidable consequence of `SS-02-DF-05`'s repair — leaving a sentence I knew to be false was not available. **The `--only` half is open** and is why the row exists. |
| F11 | `test_the_check_gates_nothing` greps one directory for one literal, so an `import` evades it; `test_the_register_is_the_only_thing_the_check_reads` inspects only `argv`, never `env`/`cwd`/`stage.from`/`link.from`/`write.file`/`nodes`. | **`SS-02-DF-09`**, routed to `SS-06`. **Clause (e) still holds at this tip — by inspection over two contracts, NOT because those two tests establish it**, and `SS-08` must not quote them as proof without this row beside them. |

**Findings: 4 → 9.** Ledger **321 → 326** rows, appended only, all ids unique.
**That is over the assignment's deferment budget of 5 for this ticket** — the
owner directed the routing of F5/F6/F7/F11 and directed F1 to be filed as well;
disclosed rather than trimmed to fit.

### 10.4 The complete out-of-key file list (F10)

Everything this branch touches outside the declared conflict keys:

| path | why |
|---|---|
| `examples/validation/instruments/instruments.toml` | **the check's subject.** No sibling ticket claims it |
| `specs/deferred_findings.yaml` | the shared cumulative ledger, **appended only** |
| `specs/desired_program_model/ticket_plan.yaml` | `status: planned → closed` on **this ticket's entry only** |
| `specs/tickets/SS-02/**`, `specs/.history/stabilize-substrate-epic/ticket-002-SS-02/**` | `open ticket` / `close ticket` byproducts |
| `specs/results/complexity_ledger.json` | close byproduct, **+343 lines to a shared append target that will conflict with every remaining sibling** |
| `specs/results/skill_feedback.md` | close byproduct |
| `specs/current/**` | the ticket-scoped promotion the close performs |

`tests/test_instrument_demonstrations.py` is `SS-06`'s key and was **not**
touched — that is why `SS-02-DF-04` exists instead of a fix.

### 10.5 Two things the owner corrected, and one figure of the owner's that this round moved

The owner withdrew two items as theirs, not mine: SS-08 obligation 9a's
`--ticket` claim, and issue #275's stale "297 rows" (my **308 at `48f9c7e`** is
right). **One of those two moved during this round and the owner should see the
new number.**

`disposition.py --ticket SS-02` selects a row only when **`found_by` starts with
the ticket id** *and* the row id does. At `cbb6761` that was **4 of 4** and the
owner's "for SS-02 it is exactly right" was true. **At this head it is 4 of 9** —
the five review-round rows are excluded because their `found_by` is
*"independent reviewer of PR #284 instructed to REFUTE"*.

**The under-count is not random: it is exactly the rows an independent reviewer
found.** So the instrument systematically under-reports a ticket's findings in
the direction of hiding externally-found ones, which is the direction that
flatters the ticket. All nine rows pass the three clauses when selected by id
prefix (`0 of 9` fail). **Recorded for the owner's softening of 9a; not filed,
because 9a is the owner's.**

### 10.6 What I think is wrong in the review

**Nothing.** Every finding I could check, I reproduced: the all-waived
`SATISFIED`, the one-line `expect_exit` evasion, the `KeyError`, two loops and
not four, `53 of 55` matching no reading, the five `+9` citation shifts read at
both line numbers in the tip file, and the sealed copy carrying §7–§9. **The
reviewer was right on all eleven, and right about the two HIGHs being the
ticket's own thesis turned on the ticket.**

One refinement rather than a disagreement, on F6/F7: the footer half could not
be left standing while `SS-02-DF-05` was repaired, because the fix makes the
sentence false rather than merely weak. It is closed here and the row says so.
