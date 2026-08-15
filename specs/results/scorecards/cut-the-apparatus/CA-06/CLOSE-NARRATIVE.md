# `CA-06` close narrative

**Ticket**: make the TLA+ / case-generation / adapter path dead simple, and
report what the simplified version costs and catches on a real subject.

**The one-line summary, which is not the one the ticket was commissioned to
produce**: the path is simpler, it is **not** dramatically smaller, and the
measurement taken instead of the cut is the ticket's real output.

---

## 1. Why there is no complexity decrease to license

**The model delta is `direction=zero`.** No `.tla`, no `.cfg` and no
`spec_manifest.yaml` changed:

```bash
git diff e379d6b -- specs/program_model specs/current \
    specs/desired_program_model/TlaSpecDevCli.tla \
    specs/desired_program_model/spec_manifest.yaml     # -> empty
```

No variable, action or bound moved, so **TLC was legitimately skipped** and the
`validated_refactor` basis — which exists to license a *decrease* — has nothing
to license. `specs/tickets/CA-06/current` equals `desired`.

**That is recorded as a defect rather than a virtue.** "No model delta" was the
wrong phrase and this ticket used it in its first PR. The accurate statement is
**no model work was done, and the model is now stale**: all three trees still
declare `case_program_process` and `case_program_write`, ports that exist only
for the execution mode this ticket deleted, and all three of their declaration
comments cite line numbers inside deleted code. Enumerated in `CA-06-DF-03`'s
`blast_radius`; not repaired here because
`tests/test_port_declarations.py:136` asserts one of them by name, making it a
model change with a test to update, discovered at review time on an open PR.

---

## 2. What was measured, and the number that matters

The work order asked what the path **costs and catches on a real subject**, and
said to report a zero yield as a result rather than work around it.

**Subject**: `examples/distributed_history` — this repository's own worked
example, not the house fixture every prior kill measurement in this project
used. **128 mutants enumerated exhaustively** from a fixed grammar over every
eligible AST site of `ecommerce_backend/domain.py`.

| discount | corpus-only | semantic | suite-only | semantic |
|---|---:|---:|---:|---:|
| raw | 39 | 3 | 9 | 1 |
| minus `load_state`/`reset` | 22 | 3 | 9 | 1 |
| **minus `project_order`** | **12** | **0** | **9** | **1** |

**ON JOINTLY-EXERCISED CODE THE GENERATED CORPUS HAS ZERO SEMANTIC UNIQUE KILLS
AND THE HAND-WRITTEN SUITE HAS ONE.** The raw 39 measures **coverage breadth,
not fault-detection power**: the corpus wins where it is the only thing
executing the code, and wins nothing where both instruments run.

**The third row is not mine.** An independent reviewer reproduced the probe
exactly — 44/9/39/36, zero per-mutant disagreements — and then found that all
three semantic corpus-only kills sit in `project_order`, a near-duplicate of
`process_outbox` the 42-line hand-written test never calls. I reported 39 and
conceded 22. The honest figure for fault-detection power is **0 against 1**, and
it is the reviewer's, adopted whole.

**So the disproof survives.** What `CA-06-DF-04` refutes is the **unqualified
generalisation** carried by the charter, the plan and the goal baseline. It does
**not** touch the `ab_quota_ledger` result. The defensible sentence, which
should replace the bare one wherever it appears:

> *"on `ab_quota_ledger`, against that subject's developed hand-written suite,
> the generated corpus had zero unique kills."*

**`MF-020` ordering, stated because it cannot be checked**: the claim that the
mutant population was fixed before `CA-06-DF-01` was found rests on the ticket
agent's word. The probe, its transcript and the finding all landed in one commit,
so the reviewer could confirm only that the structure is *consistent* with the
account. The cheap fix nobody has been doing: **commit the population before
running it.**

---

## 3. What the measurement found — the two `R1` failures

**`CA-06-DF-01`.** `extract_action_signatures` defaulted to the literal name
`Next` and **neither caller ever overrode it**, so the negative corpus and the
port corpus emitted **zero cases** on any model that spells its next-state
relation differently — while the run still printed `corpus gate PASS`.
`examples/distributed_history` names its relations `InternalNext` and
`ExternalNext` and got nothing from either mode. **Every measurement defending
those two mechanisms is taken on `QuotaLedger`, the one model here literally
named `Next`.** Fixed by calling `find_next_relation`, which the sibling module
has shipped for three epics and this module never called. `0 -> 11` cases.

**`CA-06-DF-02`.** The 11 still cannot execute: the negative pass keys `params`
by TLA formal names while the positive pass keys them by the recovered names
every shipped adapter uses. All 11 die on `KeyError`. **So the measured yield of
`--negative-cases` on a real subject is zero cases *executed*.** Filed, not
fixed — re-keying changes what a corpus contains, which `HP-03` forbids doing
silently.

**`CA-06-DF-05`.** The gate that hid `CA-06-DF-01` is **not** repaired.
`corpus_diagnostics.py` computes `passed` as `not over_cap` — a one-sided cap —
so an empty corpus exceeds nothing and prints PASS. Filed rather than folded, at
the epic owner's instruction, with a **subtractive** suggested fix (stop
printing a verdict the measurement cannot support) because `no_new_gates_rule`
forbids the obvious one. `CA-04`'s removal of `kill_rate_floor` quoted the model
predicting exactly this: *"shrink the model toward nothing and every cap
passes."*

---

## 4. Three findings about method, which are the ticket's durable output

### 4.1 A grep cannot find an absent argument

This ticket cut an execution mode on the claim that it had **zero live callers**.
**That claim was false when it was filed.** Two live call sites reached the mode
— `tests/test_case_adapter_runtime.py`'s subprocess test, *literally named for
the mode*, and `tests/test_testgraph_channels.py::_run_adapters` — and
`scripts/tla_spec_dev.py` still shipped `--no-batch`, now a silent no-op.

**The loader check searched for the string `--batch`, and every one of those call
sites is characterised by the ABSENCE of a flag.**

**That is `CA-04-DF-06`'s class arriving from a third direction in three
tickets:**

| ticket | what the check missed |
|---|---|
| `CA-02` | a deleted **path** — `repriced_history.py` broke silently |
| `CA-04` | established the check is blind to deleted **interfaces** — subcommands, exports, manifest keys, TOML sections |
| `CA-06` | a **live caller identifiable only by what it does not say** |

**The generalisation, stated so the next ticket can use it: a grep finds tokens,
and the absence of a token is not a token.** A check built on `git grep` can
never see a caller that relies on a default, and defaults are exactly what a
simplification removes. Neither the path grep nor the interface grep `CA-04`
added would have caught this; a third grep will not either.

### 4.2 The same citation defect bit three times in one ticket

`scripts/effect_conformance.py:1684` cites
`run_generated_case_adapters.py:<line> (case-work)`.

```
1354 -> 1405     deleting 108 lines moved the anchor
1405 -> 1413     adding the review's import-root docstring moved it again
```

**Every edit to a file that something cites by line number re-breaks the
citation.** It went red on the first suite run, was repointed, and went red again
on the review round for exactly the same reason. The test caught it every time —
which is `RC-02`'s instrument doing precisely what its docstring promises,
*"a line shift now breaks a test instead of a reader"*.

**This is the strongest argument this project has produced for content anchors
over line numbers**, and `RC-02`, which built the anchor mechanism, already made
it. The anchor is what made each failure diagnosable in one line; the line
number is what made it fail three times.

### 4.3 `scripts/` moved approximately nothing once the review fixes are counted

```
surface               (a) e379d6b   (b) 88165bd   (c) head    (c)-(b)   (c)-(a)
                        baseline     epic tip     this PR     CA-06     actual
scripts/                   26,547       26,760      26,756       -4       +209
examples/validation/       14,854       14,854      14,854        0          0
tests/                     30,422       30,635      30,738     +103       +316
```

CA-06's own `scripts/` figure was **−32** when the PR opened and is **−4** now.
The `--no-batch` tombstone, the renamed test's docstring and the docstring
explaining the import-root bug cost **28 lines** between them.

**That is `RD-02`'s finding for the third time inside one ticket** —
*"every removal shipped instruments, tests and demonstrations to prove the
removal safe and nobody counted that as a cost"* — **and responding to a review
is itself one of those costs.** This ticket was commissioned as *"the largest
single reduction in the epic"*. **In `scripts/` it is approximately nothing.**

Both columns are printed because printing only the counterfactual was a
presentation failure a reviewer caught: `(c)-(b)` is this ticket's contribution,
`(c)-(a)` is what actually happened to the branch, and the difference is
`CA-05`, which merged mid-ticket.

---

## 5. What was refused, and why the refusal is the right call

**The mass this ticket was sent to cut is `--negative-cases` (290 lines on a
1,043-line shared TLA+ expression parser and guard evaluator) and `--port-cases`
(397 on the same parser) — 1,730 lines together. It was not cut.**

`SM-02` measured both one epic ago and **kept** them, in a shipped test that is
still green, written expressly so that *"a later reader cannot quietly widen"*
"defund `[ports.*]`" into "defund the corpus". **A ticket does not overturn a
predecessor's measurement by asserting the opposite. It measures again.** Section
3 is what measuring again produced, and it is a stronger case for the owner to
decide on than the sentence the work order offered.

**The reviewer's verdict on that refusal, recorded because it is the disposition
of this ticket's central choice**: *"a correct refusal on the record, not
work-avoidance; the ticket produced a better result than the cut it declined."*

**And `SM-02`'s guard is weak, which is worth knowing before anyone relies on
it**: it asserts only that two flags appear in `--help`, so it would have stayed
green through the entire `CA-06-DF-01` blindness.

Also refused, each with its reason in the PR body: fixing `CA-06-DF-02`'s
keying; deleting the hand-rolled TOML fallback; deleting the three advisory
reporters (**no finding on the record condemns them**, and clause (b) of
`GOAL-apparatus-cut` fails a cut with no finding behind it even if the lines
fall); adding a convention-driven entry point (needs a model delta and *adds*
lines); and re-running the kill table with the demonstration file included, which
would be `MF-020`.

---

## 6. Refinement search

**Searched, and one refinement was found and applied**: the next-state relation
resolver. It is a **deletion of a hardcoded constant** in favour of
`find_next_relation`, a function the repository already ships and tests in
`scripts/analyze_complexity.py`, and it removes a special case rather than adding
one. It is a **no-op on both models that already worked** — the resolver returns
`Next` for each — so no sealed corpus moves and no TLC figure changes.

**No refinement of the TLA+ representation itself was found**, because this
ticket changed no TLA+ at all: `direction=zero`. The representation was searched
for reducible surface in the course of `CA-06-DF-03`'s removal — the deleted
execution mode's two declared ports, `case_program_process` and
`case_program_write`, **are** now-dead model surface and **are** a genuine
available reduction — and it was **deliberately not taken** here, because it
needs `tests/test_port_declarations.py` updated with it and it arrived at review
time. It is enumerated in `CA-06-DF-03` so the next ticket can take it without
rediscovering it, and it needs no TLC: removing a port declaration whose effect
can no longer occur changes no variable, action or bound.

---

## 7. Evidence

All under `specs/results/scorecards/cut-the-apparatus/CA-06/`:

| file | what it carries |
|---|---|
| `RESULTS.md` | cost and catch on the real subject, the three-tier table, the ordering caveat |
| `PRICE-TABLE.md` | removal and addition tables, three-column figures, model-delta restatement, suite movement |
| `kill-table.json`, `mutation_probe.py`, `mutation-probe-transcript.txt` | the 128-mutant population and its per-mutant verdicts |
| `next-relation-resolution.txt` | which definition each model's next-state relation actually is |
| `negative-corpus-before.txt` / `-after.txt` / `-execution.txt` | `0 -> 11` cases, and all 11 failing on `KeyError` |
| `regression-as-adapter-case.py`, `regression-demonstration.txt` | one regression expressed as an adapter conformance case, red on the mutant, green on pristine |
| `loader-check.txt` | the required path **and** interface greps — and the check that still missed section 4.1 |
| `sv04-still-reproduces.txt` | `SV-04`'s instrument, `14 passed`, matching the sealed figure |
| `pytest-baseline.txt`, `pytest-after.txt`, `pytest-after-review.txt`, `pytest-promotion.txt` | every suite run, including the two that went red and why |
| `spec-unit-tests.txt` | `55 passed, 1 failed`, the failure verified inherited |

**Findings**: `CA-06-DF-01` (repaired), `CA-06-DF-02` (carried, CA-07),
`CA-06-DF-03` (repaired), `CA-06-DF-04` (carried, CA-08), `CA-06-DF-05`
(carried, CA-08). Five of a budget of five, every one disposed, all passing
`CA-05`'s disposition instrument with no violations and no channel advisories.
