# `GOAL-absent-input-consumed` — what `SS-02` moved, clause by clause

**Tree:** `feature/SS-02`, reconciled with epic tip `eb2567b`, in
`/Users/hayde/IdeaProjects/wt-epic-stabilize-substrate-SS-02`.
**Baseline this is measured against:** `baseline.md` in this directory, at
`436c78c`. **Decided by `SS-08`, not here.** This file records what was
produced and where the transcripts are; it does not award a verdict.

---

## The four clauses this ticket touches

### (a) The extension exists AS AN EXECUTED CHECK — **produced**

`python3 examples/validation/scorecards/score_tools.py absent-input`, over
`examples/validation/instruments/instruments.toml`. Not a doctrine line, not a
comment, not a paragraph in a reference: a subcommand with a verdict surface,
23 tests, and two registry rows carrying contracts it executes.

The baseline said **"NO CHECK EXISTS."** One does now.

**What it requires of an instrument, and why each clause is there:**

| requirement | the finding it consumes |
|---|---|
| three states — `absent`, `unreadable`, `empty` | `SS-01-DF-04`: `CA-10-DF-11` repaired the absent ledger, `SS-01` the wrong one, and the **empty** one still produced 14 fabrication accusations |
| `answer` is `refusal` or `undecided`; **`pass` is not available** | the rule itself |
| every state declares `expect_output` | an exit code cannot show UNDECIDED rather than clean |
| `exit_code_cannot_carry_the_answer` is mandatory when a state answers `undecided` and exits 0 | `SS-02-DF-03`, found writing the first contract |
| states the instrument cannot tell apart must be **declared** — and the collapse is found **by executing** both states, not by reading the contract | `SS-01-DF-04` again: a contract can declare three states while the instrument collapses two |
| a state that cannot be constructed declares `unreachable = "<reason>"` and is **counted and printed**, never folded into the satisfied population | `CA-10` §3.4's own discipline |

### (b) A DEMONSTRATED REFUSAL ON A REAL INSTRUMENT, failing before and passing after — **produced**

**Subject: `scorecard-audit` = `score_tools.py audit`** — the instrument whose
`_finding_ids` signature change (`set[str]` → `set[str] | None`) is the worked
shape of the whole class. Both runs read the **shipped** register; the BEFORE
run removes exactly one block from it. **Not a fixture.**

| | exit | verdict |
|---|---:|---|
| register **minus** `[instrument.absent_input]` | **1** | `NO CONTRACT` |
| register as shipped, three states **staged and executed** | **0** | `SATISFIED` |

`../SS-02/R1-refusal-on-a-real-instrument.txt`.

### (e) NO NEW GATE OVER SUBJECT-PROGRAM CONTENT — **held, and executed**

The check reads **one file**: this repository's own instrument register. It
decides nothing about any subject program, and no close or promotion path
consults it. That is not a promise in a docstring —
`tests/test_absent_input_demonstrations.py::test_the_check_gates_nothing`
asserts that nothing under `scripts/**` references it, and
`test_the_register_is_the_only_thing_the_check_reads` asserts every contract's
`argv` stays inside `{repo}` or the staged `{tree}`.

Under the adjudicated static-gates doctrine this is the **permitted**
population — static checks over this project's own record, metadata and method,
**3 catches : 1 false refusal** — and the refused population is a gate over
subject-program content. It must never become one.

### (c) and (d) — **not this ticket's**

(c) the re-sweep of the 43 modules is `SS-08`'s. (d) binds every repair this
epic ships, and **this ticket shipped none**.

---

## The instance count: moved by ZERO, deliberately

`expected_effect` says in as many words: **NO EFFECT ON THE INSTANCE COUNT —
that is `SS-05`'s, so the class is measured before it is shrunk.**

**48 instances at the baseline. 48 at this tip.** Nothing in `CA-10`'s table
was repaired here. Four *new* findings were filed (`SS-02-DF-01` … `-04`), three
of which are further faces of the same class found **by the check** — but a
finding filed is a finding routed, and none of them is counted as a repair.

**Two things that look like movement and are not:**

- **`scorecard-audit` now carries a contract.** Declaring what an instrument
  answers is not repairing it. `audit` answered UNDECIDED to all three states
  **before** this ticket, because `CA-10` and `SS-01` had already repaired it;
  the contract records that, and the two things it does *badly* became
  `SS-02-DF-01` and `SS-02-DF-03` rather than edits.
- **The register denominator moved 55 → 56 instruments.** This ticket added one
  row: the check itself, so it sits inside the population it measures. **+1
  denominator, this ticket's, stated.**

---

## The count, at this tip

`../SS-02/absent-input-whole-register-executed.txt`, exit 1:

```
instruments in the register                 56
contract EXECUTED and holding                2
WITHOUT one                                 54
DECLARED indistinguishable state pairs       1
```

**2 of 56.** There is **no target on that ratio**; a threshold on a repair count
before the check existed would be `MF-020`. The two are `scorecard-audit` and
`absent-input-check`.

**Do not read `2 of 56` against `1 of 48`.** They are different populations —
the register enumerates *instruments*, `CA-10`'s sweep enumerates *instances of
a defect in modules*. Neither is a rate over the other.

---

## The check's own absent input — the trap, answered

Six ways to hand this check nothing, six exit-2 UNDECIDED answers, six distinct
sentences, no zeros: `../SS-02/the-checks-own-absent-input.txt`. Plus
`--contract-only` (declared, never executed → exit 2) and `--state` (a subset
answering for the set → `PARTIAL`, exit 2).

**One collision disclosed:** `argparse` also exits 2 on a usage error, so the
code alone does not separate UNDECIDED from a mistyped command; the first output
line always does. `SS-02-DF-02`.
