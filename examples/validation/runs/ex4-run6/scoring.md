# ex4 run 6 — the aspect-authoring path, re-run blind on a fresh scratch copy

Run date 2026-07-30, EV-03. **Blind agent run**, dispatched by the EV-03 ticket
agent. QA-engineer persona; never saw `PREDICTIONS.md`, the answer key, the
seeded-fault table, the two shipped aspects (removed from the copy), or any epic
context. Owner-scored; the numbers below were re-derived here from the agent's
preserved tree and its shipped artifacts.

## Protocol

**EV-02-PROTO-01 in force.** `artifacts/sanitize_runB.py` plus a targeted second
pass replaced every module docstring, comment block, manifest header and README
that carried epic context with purpose-written text that reads as the project's
own. The `case_modules:` block and `specs/case_modules/` were removed so the
agent authored from nothing. Final leak scan over the whole tree for `EV-0*`,
"answer key", "predictions", "fixture", "twin", "seeded", "epic", `MF-0*`,
`RP-0*`, `CM-0*`, `DF-0*`, "ARM A", "ARM B", "oracle leakage": **zero hits.**

**EV-02-PROTO-02 in force.** Round 1's blind aspect run measured 12 mutants and
shipped no catalogue, so its numbers could not be re-scored. This run was
instructed to ship the catalogue as a file, and it did:
`artifacts/mutant_catalogue.toml` (16 mutants, exact `find`/`replace`),
`artifacts/mutant_run.py` (green control + apply/run/restore), and
`artifacts/mutant_results.json`. **Every number below is re-derivable.**

The blind is mechanical: the trimmed toolchain copy carries `scripts/`,
`references/`, `prompts/` and `SKILL.md`, with `examples/` and `specs/` removed.

## Aim 2 — authoring cost vs. yield

| artifact | total lines | non-comment |
|---|---|---|
| `Scenario_IntakeToDelivery.{tla,cfg}` — a **slice** | 25 | 14 |
| `Scenario_DurableOutcome.{tla,cfg}` — a **Given** | 44 | 20 |
| `case_modules:` block | 20 | 16 |
| **authored total** | **89** | **50** |
| `case_adapters_slice.toml` — **forced by CM-F5** | 35 | 16 |

| corpus | states | cases |
|---|---|---|
| whole view (0 new lines) | 121 | **330** |
| slice | 25 | **50** |
| Given | 16 | **24** |
| **modules, union** | 41 | **74** |

**89 authored lines → 74 cases**, 0.83 cases per authored line. 404 of 404 cases
across all three corpora carry fully recovered arguments; **0 `UNCHECKED`.**

**A2-P1 PASS by reproduction on new material** — a second author, working from
the public surface, produced a slice at 50 cases and a Given at 24, in the same
ranges as the shipped 50 and 6.

**A2-P2 honoured, and the agent volunteered the honest framing without being
asked**: it reported cases-per-authored-line and cases-per-non-comment-line, and
then said the cost argument does not apply here at all — the whole view generates
in 0.95 s and executes 330 cases in 0.23 s, so there is nothing to save. Its own
conclusion: on this project a case module is worth writing for what it
*documents*, and the `references/case_modules.md` headline (1m 23s → 2.2s) is
selling the wrong benefit at this scale. **That is a docs finding, and it is
sharper than A2-P2.**

**A2-P3 — PASS for the Given, FAIL for the slice.** See CM-F5 below.

## A2-P4 and Step 0 — the measurable behaviour change from RP-03

Round 1: the agent produced a schema-valid, coverage-clean decomposition with no
author in the loop, noticed on its own, and flagged it. Round 1 scored Step 0
"unenforceable, and nothing said so".

Round 2, with RP-03's labelled-unenforceable contract in the prompt: the agent
opened its report with a section titled *"Provenance of the aspect list — read
this before the numbers"*, stated **"No author was in the loop"**, and wrote
**"This decomposition is UNREVIEWED"** in bold before quoting a single number. It
also separated the two halves the RP-03 asymmetry table names: the *claim* came
from the README, the *predicate* came from having the model open.

**That is exactly the contract RP-03 shipped, honoured by an agent that had never
seen RP-03.** It is still not a control — `case_modules.py validate` exited 0 on
an authorless decomposition without a murmur, and the agent said so (its F7). The
change is that the artifact now carries the caveat, which is what the contract
asked for and all it claimed.

## CM-F5 — independently confirmed, with the same sharpening

The agent hit it without knowing it existed, lost 3 of its 15 actions to it, and
reached the identical conclusion this ticket's mechanical arm reached
(`../ex4-run4/scoring.md`, step 6b):

> `case_adapters.toml` and `case_adapters_corpus_only.toml` differ only in
> **which** `LedgerStorePort` provider they bind — both bind one — so every
> mapping the project ships is refused by every slice that excludes `Record`. A
> project with one effect port and a slice that does not enter it has zero
> working mappings, not one.

It worked around it by authoring a third mapping with the provider block deleted,
and then made the point this ticket's own record did not: **the workaround is a
strictly weaker instrument.** Its slice's 3 kills all come from state comparison,
and the three `durable_write` mutants are invisible to it *by construction*,
because the thing that would have seen them is the provider CM-F5 forced it to
delete. **Anyone reading a slice's green run without reading its mapping will
over-read it.**

This is the third independent confirmation of CM-F5 in this ticket and the
sharpest statement of its cost. **EV-03-DF-02** is amended with it.

## Aim 1 — the agent's 16-mutant catalogue, per class per instrument

Green control first, on all six instruments, before any mutant. It was green.

| class | seeded | view + checking mapping | view + silent mapping | Given corpus + checking | Given + silent | slice + provider-free | pytest |
|---|---|---|---|---|---|---|---|
| **guard_accepts** | 4 | **0** | **0** | **0** | **0** | **0** | **4** |
| guard_rejects | 2 | 2 | 2 | 1 | 1 | 1 | 2 |
| missing_write | 3 | 3 | 3 | 1 | 1 | 2 | 3 |
| wrong_value | 1 | 1 | 1 | 1 | 1 | 0 | 1 |
| **durable_write** | 3 | **3** | **0** | **3** | **0** | 0 | **0** |
| **ordering** | 2 | **0** | **0** | **0** | **0** | **0** | **0** |
| **total / 16** | | **10** | 7 | 6 | 3 | 3 | **10** |

| combination | killed / 16 |
|---|---|
| case modules, union | **9** |
| view + pytest | **14** |
| case modules + pytest | 13 |
| **killed by nothing** | **2** (both ordering) |

### What this independently replicates, from outside, post-repair

1. **Guard relaxation is 0 of 4 on EVERY corpus instrument** and 4 of 4 on the
   hand-written suite. **This is the third independent confirmation** — round 1's
   blind agent (0 of 3), RP-02's reconstruction (0 of 3 before AND after the
   parameter-recovery fix), and now a second blind agent on a fresh catalogue,
   **on the repaired tree, with 100% parameter recovery in place.** The agent
   verified the mechanism itself without prompting:
   ```
   grep -o "'status': '[a-z]*'" cases.py | sort | uniq -c
   #  330 'status': 'applied'
   ```
   *"The corpus is built from enabled transitions only; it never once asks the
   program to reject a call."* That is RP-02's structural half, found from
   scratch by someone who had never read RP-02.
2. **The two mappings are two instruments, and the gap is exactly the durable
   class** — 3 kills, 30% of that instrument's yield. DP-8's discipline
   reproduced by an agent that had to be told only "name which mapping produced
   the number".
3. **Ordering is invisible to everything**, including the hand-written suite.
   The agent traced all four layers (model uses sets; `adapters.py` projects
   `frozenset`; the provider compares `sorted()`; the behavioural tests only
   assert single-element lists) and concluded it needs a **model** change, not a
   test change. Identical to round 1's conclusion, arrived at independently.

### The result that qualifies round 1's headline

Round 1's blind run reported a Given that **killed exactly what the 330-case view
killed** — "8.7× reduction at zero measured loss". Round 2 measures the same
shape with a mutant deliberately placed in the gap:

**74 case-module cases reached 9 of the view's 10 kills.** The one lost (M16) is
a `Fail` that misbehaves *only when the work queue is still non-empty* — a
before-state the Given asserts away (`queue = {}`) and the slice never reaches.

> *"If M16 were not in the catalogue the case modules would score identically to
> the view and the report would be quietly misleading. Do not read a 'case
> modules == view' result off a catalogue that has no cross-aspect mutant in
> it."*

**That is the correct reading of round 1's zero-loss result, and it retires it as
a headline.** Round 1's catalogue had no such mutant; its "zero measured loss"
was a property of the catalogue, not of the Given. The agent also sharpened the
vocabulary: every generated case is one action against a materialized
before-state, so on this profile "cross-aspect interleaving" is not about call
orderings at all — it is about **before-state diversity**, and that is where the
loss lives. `NEXT-EPIC.md` NE-04's first bullet is corrected accordingly.

## The finding round 1 called "worth more than any mechanism", reproduced

Working from the README alone, a **second** agent found that the public surface
is false of the model: `Fail(i)` removes the item from `delivered` and `Record(i)`
requires it, so a failed item can never reach the ledger, while the README
promises *"a failed item is recorded as failed"* and *"the ledger records each
outcome"*.

Round 2 adds three things round 1 did not have:

1. **`LedgerIsDownstream` is written as if the promise held.**
   `ledger \subseteq (delivered \cup failed)` permits a state no action can
   reach, so the real invariant (`ledger ⊆ delivered`) is strictly stronger and
   the written one passes vacuously on the half that matters.
2. **The behavioural suite asserts the same weak thing** and therefore cannot
   fail.
3. **`test_two_item_interleaving` asserts the negation of the README sentence.**
   Whoever fixes the promise must change a passing test.

Same conclusion as round 1, reached by a different agent on a differently
sanitized copy: **the value came from the act of authoring, not from the cases.**
It replicates.

## Two NEW toolchain findings, both verified by the scorer

**`--effect-report PATH` silently writes nothing.** Verified independently on the
shipped ex4 fixture: `--effect-report /tmp/eff_probe.json` on a 330-case ARM B
run produced **no file, no warning, no message, exit 0**. The flag is gated on
`declarations is not None and bool(declarations.ports)`, and
`load_effect_declarations_for_spec` looks for an `effects:` block in `actions.yml`
or the manifest — this project has neither; it has `ports:` in the manifest and
`effect_ports:` per action. The code comment two lines above the gate says *"The
report is written unconditionally — it is ticket evidence whether the verdict is
clean or not"*, which is not what the code does. **Filed as EV-03-DF-04**, and it
is the same honest-in-prose / silent-in-artifact class this epic keeps finding.

**`analyze architecture` without `--components` silently substitutes an emergent
partition for the declared one.** Verified independently on ex4:

| | without `--components` (the prompt's Step 1) | with `--components` |
|---|---|---|
| `partition.source` | `emergent` | `declared` |
| components | `C1`, `C2` | `ingest`, `dispatch`, `ledger` |
| ports | `P1 C1<->C2` crossed by **`Enqueue`** | `P1` by **`Deliver`**, `P2` by **`Record`** |
| spanning actions | none | `Deliver` |

The declared answer is the one the model's own comments assert. The default run
erases the deliberate `Deliver` spanning action and attributes the boundary
crossing to a different action. `partition.source` does say `emergent` in the
JSON — the tool is not lying — but `prompts/aspect_decomposition.md` Step 1 pipes
straight past it, and `spec_manifest.yaml` points at the partition file **in
prose the tool cannot read**. **Filed as EV-03-DF-05.**

## X-P3 — re-scored

Round 1: 8 friction items, 6 of them documentation insufficiency, **FAIL**.
Round 2: **8 items again, FAIL again — but they are different items.**

| round 1 item | round 2 status |
|---|---|
| a case module cannot generate where the docs put it | **GONE** (RP-03) |
| every documented path assumes an external view | **GONE** (RP-03's worked example) |
| `--out` resolves against the `.tla` dir, undocumented | **PARTLY** — now printed at runtime; the agent still calls it "a default that is wrong for every invocation I would naturally type" |
| the `--import-root` error names one root when two are needed | **GONE** (RP-03) |
| Step 1's command does not run as written | **PARTLY** — `--spec-root` is documented now; the agent's point is that the more useful missing warning is `--components` |
| interpreter roulette | **STILL OPEN** (EV-02-DF-05), hit again |
| the audit contradicts its own corpus | **GONE** (RP-02) |
| nothing in the repo was modified | **PASS**, verified |

New in round 2: CM-F5's zero-working-mappings, `--effect-report`'s silence,
`analyze architecture`'s silent substitution, ERROR-on-stdout reading as a pass
through a pipe, and no `.cfg` scaffold. **The docs got materially better and
X-P3 still fails**, which is the honest way to report it.

The agent also volunteered what worked as documented: `case_modules.py validate`;
per-module action scoping (CM-F2 — **zero** spurious zero-case warnings for the
two out-of-scope actions, with one clear sentence saying so); **the `EXTENDS`
resolution from a sibling directory with no flag, which printed its search path
unprompted** (that is RP-03's fix, praised by someone who did not know it had
ever been broken); the recorded-Given-claim echo; 404/404 parameter recovery; and
the replay command in the failure output.

## Determinism (independent third measurement)

Generation byte-identical across two full runs, **18 of 18 files** over three
packages; `case_coverage.json` differs only in `source`. Execution identical,
including **under a mutant**, where the two runs produced identical
`EFFECT_FUZZ_FAILURE` blocks down to the derived provider seed and a
copy-pasteable replay command. **A3-P1, A3-P2 PASS**, third instrument.

## Fixture integrity

Scorer-verified (`artifacts/runB_restoration_check.txt`): `pipeline/`,
`test_behavior.py`, `Pipeline.tla`, `adapters.py`, `providers.py` and both
shipped mappings are **byte-identical to the pristine snapshot**. The agent's own
harness took a sha256 of every `pipeline/**/*.py` before the control run and
asserted it after every mutant and at exit. One pre-existing file was edited by
design (`spec_manifest.yaml`, `case_modules:` block appended — the diff is in
`artifacts/authored_case_modules/spec_manifest.diff`), and one file was added
under protest (`case_adapters_slice.toml`). **X-P4 PASS**; nothing in the
repository tree was touched.

## Artifacts

`artifacts/BLIND-RUN-B-REPORT.md` (the agent's report, verbatim),
`artifacts/mutant_catalogue.toml` + `mutant_run.py` + `mutant_results.json` (the
re-derivable catalogue EV-02-PROTO-02 asked for),
`artifacts/authored_case_modules/` (both modules, the forced third mapping, and
the manifest diff), `artifacts/runB_restoration_check.txt`,
`artifacts/sanitize_runB.py`.
The agent's tree and its pristine snapshot are in this ticket's scratch at
`blind/runB` and `blind/runB-pristine`.
