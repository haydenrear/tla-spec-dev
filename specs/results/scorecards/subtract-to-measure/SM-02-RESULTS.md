# SM-02 — the `[ports.*]` binding machinery, removed and priced

**This project has never removed a mechanism it shipped. This is the first, and
the point of the ticket is not the removal — it is that the removal was
*measured*.** `SM-01` seeded a mutant in the gap of everything cut here, before
anything was cut. This file re-runs exactly those mutants against exactly that
runner and reports, per mutant, whether the mechanism was **redundant** or
**load-bearing**.

Parent: `f0c215d` (SM-01 merged). Cut: `067c5ea`.
Artifacts: `after-state-SM-02/` (the gap-mutant table, the produced-code
records at both commits, the guard-relaxation kill table, and the `SM-GM-I1`
re-check). Runner:
`examples/validation/gap_mutants/run_gap_mutants.py`, unmodified. Catalogue:
`examples/validation/gap_mutants/gap_mutants.toml`, unmodified. Corpus: the
byte-identical `--port-cases only` package `SM-01` used
(`cases.py` sha1 `08265aff0d81f27f4dfc9694d2a69c3c5b6e695c`).

---

## 1. THE HEADLINE — the gap-mutant table, before against after

**Three mutants were seeded in this mechanism's gap. All three STILL DIE. Zero
flipped `DIES` → `SURVIVES` on any detector that outlives the cut. The measured
price of removing the `[ports.*]` binding machinery is ZERO.**

Read the two halves apart. **Left: the detectors the machinery IS** — they cannot
report a survival once the mechanism they are is gone, and the runner does not
let them. **Right: the detectors that outlive it** — these are the ones that
decide.

### The detectors the machinery owns — every cell UNDECIDED after, never SURVIVED

| mutant | `corpus-port-swap:real` | `corpus-port-swap:fake` | `corpus-action-bound:real` | `corpus-action-bound:fake` | `port-binding-report` |
|---|---|---|---|---|---|
| **`SM-GM-P1`** | SURVIVES 1543 → **`CONTROL_RED`** 0 | **DIES** 1543 → **`CONTROL_RED`** 0 | SURVIVES 1543 → **`CONTROL_RED`** 0 | SURVIVES 1543 → **`CONTROL_RED`** 0 | — |
| **`SM-GM-P2`** | — | — | — | — | **DIES** 1 → **`INERT`** 0 |
| **`SM-GM-P3`** | SURVIVES 1543 → **`CONTROL_RED`** 0 | SURVIVES 1543 → **`CONTROL_RED`** 0 | SURVIVES 1543 → **`CONTROL_RED`** 0 | SURVIVES 1543 → **`CONTROL_RED`** 0 | — |
| **`SM-GM-CTRL-A`** (control) | **DIES** 1543 → **`CONTROL_RED`** 0 | **DIES** 1543 → **`CONTROL_RED`** 0 | **DIES** 1543 → **`CONTROL_RED`** 0 | **DIES** 1543 → **`CONTROL_RED`** 0 | — |

`port_corpus_run.py` imports `apply_wiring` at module scope, so after the cut it
dies at import; `run_port_swap` sees `harness_error` on the **unmutated control
run** and marks the whole column `CONTROL_RED`; `run_gap_mutants` propagates that
verdict rather than reading a zero as a survival. The after-run's `control_red`
therefore has **four entries**, all of them `CTRL-A on <machinery column>:
control reported CONTROL_RED, want DIES`.

> **That is the instrument working, not failing.** `R2`: a control that cannot
> fail is worse than no control, so it is reported RED. **`MF-020` applied to
> ourselves would have been to read those four zeros as `SURVIVES` and conclude
> nothing broke.** The artifact refuses to let anyone do that.
> `port-binding-report` lands on `INERT` — *nothing executed, decides nothing* —
> for the same reason by a different route: its entry-point FILE still exists,
> only the machinery inside it is gone, so the runner's `REMOVED` path does not
> fire (§5.5).

### The detectors that outlive the cut — THESE decide

| mutant | `suite-real` | `suite-fake` | `portswap-suite-real` | `portswap-suite-fake` | `pytest-full` | **verdict** |
|---|---|---|---|---|---|---|
| **`SM-GM-P1`** the fake journal records newest-first | SURVIVES 28 → SURVIVES 28 | **DIES** 28 → **DIES** 28 | SURVIVES → SURVIVES | **DIES** → **DIES** | **DIES** 1370 → **DIES** 1363 | **STILL DIES — REDUNDANT, the cut was free** |
| **`SM-GM-P2`** the manifest renames the port out from under the binding | — | — | — | — | **DIES** 1370 → **DIES** 1363 | **STILL DIES — REDUNDANT, the cut was free** |
| **`SM-GM-P3`** the fake is silently a second real adapter | SURVIVES 28 → SURVIVES 28 | SURVIVES 28 → SURVIVES 28 | SURVIVES → SURVIVES | SURVIVES → SURVIVES | **DIES** 1370 → **DIES** 1363 | **STILL DIES — REDUNDANT, the cut was free** |
| **`SM-GM-CTRL-A`** (positive control) | **DIES** 28 → **DIES** 28 | **DIES** 28 → **DIES** 28 | **DIES** → **DIES** | **DIES** → **DIES** | **DIES** 1370 → **DIES** 1363 | control **GREEN** on every surviving detector |

`1370 → 1363` is the acceptance suite shrinking by exactly the 21 nodes deleted
minus the 14 added (§6). Every declared mutant applied exactly once, before and
after, in both runs.

### Per mutant, in words, with the kill sets

**`SM-GM-P1` — REDUNDANT.** Kill set on `pytest-full` is **identical before and
after**: `test_a_composition_point_wires_the_fake`,
`test_both_wirings_of_one_domain_agree_on_the_feature`,
`test_every_adapter_internal_mutant_occurs_exactly_once_and_reverts`, all in
`tests/test_ab_three_arms_and_port_faults.py`. It still dies on `suite-fake` at
**28 executed** — four lines of `quota_ledger_fake.py`, no binding table, no
wiring flag, no mapping. The machinery's `corpus-port-swap:fake` cell was its
only `DIES` anywhere in this table, and it was matched on two independent
detectors that outlive it.

**`SM-GM-P2` — REDUNDANT, and its kill set changed composition without changing
its verdict.** Before, three `pytest-full` nodes; one of them,
`test_port_adapter_binding.py::test_a_bound_port_the_manifest_declares_is_reported_as_declared`,
**was deleted by this ticket**. After, still three:

- `test_port_case_generation.py::test_a_port_declared_in_the_manifest_is_read_in_the_effect_port_shape` — kept, and `SM-01` predicted it would survive
- `test_port_case_generation.py::test_the_ab_fixtures_port_region_is_the_ledger_aspect_derived` — kept, same
- `test_ports_binding_removed.py::test_the_generator_still_declares_ports_and_still_builds_port_labels` — **new, and I did not design it for this.** It is one of the two "the cut did not widen" guards and it reads the manifest through the shipped `load_port_catalog`, so a renamed port fails it. Reported as a coincidence, not claimed as coverage.

**`render_port_binding_report` was the machinery's one genuinely unique catch,
and it is gone.** `port-binding-report` no longer executes. **On this seeded gap
that costs zero**, because manifest drift is caught by three pytest nodes, two of
which predate `SM-02`. It is not zero in general: nothing now prints
`BOUND BUT NOT DECLARED` / `DECLARED BUT NOT BOUND` in one place on one run. A
gap mutant prices the class that was seeded; it says nothing about a class nobody
seeded, and this table makes no claim about one.

**`SM-GM-P3` — REDUNDANT, and it is the sharpest row here.** Kill set on
`pytest-full` **identical before and after**, five nodes, four of them in
`tests/test_ab_three_arms_and_port_faults.py` including
`test_a_fault_seeded_in_the_fake_is_reachable_only_through_the_fake`.

> **THE SWAP COULD NOT DETECT THAT ITS OWN FAKE WAS NOT A FAKE.** Before the cut,
> with the machinery fully present and `CTRL-A` **green on all six of its columns
> at 1543 executed each**, `SM-GM-P3` **survived every one of them**. The
> mechanism was not load-bearing here; it was **blind** here. Removing a
> mechanism that is blind to the one failure it exists to make impossible costs
> nothing — and that is now measured rather than argued.

### The mechanism-2 rows, run as a scope check — and one contaminated cell, reported

`SM-03`'s six mutants were re-run in the same artifact, not because they are this
ticket's to decide but because **a cut that moved one of them would have widened
past its scope.** Five are unchanged: `I2` SURVIVES→SURVIVES, `I3`
SURVIVES→SURVIVES, `I4` DIES→DIES, `I5` DIES→DIES, `I6` DIES→DIES on
`instrument-registry` and SURVIVES→SURVIVES on `pytest-full`.

**`SM-GM-I1` read `SURVIVES` → `DIES` on `pytest-full` in the run of record, and
it is a false kill.** The single new failing node is
`tests/test_testgraph_channels.py::test_runner_refuses_a_binding_without_a_channel`
— unrelated to the mutant, which skips `tests/test_complexity_ledger.py`;
unrelated to anything this ticket removed; and **passing in the acceptance suite
at the same commit** (§6: 1363 passed, 0 failed). Re-run alone on a quiet machine
at the same commit:

```
SURVIVES  pytest-full  1290 executed  new_failing_nodes: []
```

**Both runs are reported, and the re-run was decided on before its result was
seen** — the node was identifiable as unrelated from the run of record's own
`new_failing_nodes`, which is why it was re-run at all. `SM-GM-I1` is therefore
**unchanged by `SM-02`**, which is what the scope check needed. The general
hazard — one flaky node under machine contention yields a `DIES`
indistinguishable from a real one unless a reader opens `new_failing_nodes` — is
filed as **`SM-02-DF-03`**.

### What this settles about `N01`, and what it does not

`N01`, sealed by `SM-01`, predicts that for the two *behavioural* ports mutants
**every column reporting `DIES` today is matched by a `DIES` on a detector that
outlives `SM-02`**, and that neither flips. Its stated falsifier: either ports
mutant reporting `DIES` on some `corpus-port-swap:*` column before and `SURVIVES`
on every one of `pytest-full`, `suite-real`, `suite-fake` after. **No such cell
exists in this artifact.** `SM-GM-P1`'s one machinery `DIES` is matched by
`suite-fake` (28 executed) and `pytest-full` (1363); `SM-GM-P3` had no machinery
`DIES` to match. **`N01` is `SM-05`'s to score, not this ticket's** — what is
reported here are the cells that were measured.

### 1.1 The interruption check — one run WAS killed, and it is not the run of record

`SM-03`, running concurrently in a sibling worktree, executed a bare
`pkill -f run_gap_mutants.py`. That pattern matches by process name across the
whole machine and is blind to worktree boundaries. **Checked rather than assumed
away**, because a reader who finds `SM-03`'s disclosure will ask:

| run | interpreter | outcome | is it the run of record? |
|---|---|---|---|
| 1 | `python3` (3.9) | died in 0 s, `ModuleNotFoundError: tomli` — **my error**, wrong interpreter | no |
| 2 | `python3.14` | ran ~40 min, log stops mid-`SM-GM-I5`, **process vanished with no traceback and no output file** | **no — discarded whole** |
| 3 | `python3.14` | complete, artifact written | **YES** |

Run 2 has the exact signature of an external `SIGTERM`: no exception, no partial
JSON, no `wrote <path>` line. **Nothing from it is reported here, and no partial
table was reconciled into a complete one** — `--out` is written once at the end,
so there was no truncated artifact to be tempted by. Run 3 is a clean re-run of
the whole catalogue from `067c5ea`, and every cell in §1 comes from it.

**An interrupted measurement is not a measurement.** The rule is *report the run
that happened*; the run that happened was killed by something outside this
ticket, so it was thrown away rather than argued around.

---

## 2. What was removed, in files and lines

### 2.1 The toolchain

| file | change | lines |
|---|---|---|
| `scripts/run_generated_case_adapters.py` | the machinery, in twelve pieces | **−225 `code_lines`**, −6 callables, −5 public surface |
| `tests/test_port_adapter_binding.py` | **deleted whole** | −462 file lines, **−21 collected nodes** |
| `tests/test_ports_binding_removed.py` | **added** | +14 collected nodes |
| `references/case_modules.md` | the `PA-04` section rewritten | −65 lines of mechanism doc, +46 of what it bought |

The twelve pieces, named so a reader can check the list against the diff:

1. `AdapterMapping.binds`, `.port`, `.fake`
2. `load_mappings`' `[ports.*]` branch
3. `parse_simple_mapping_toml`'s `[ports.` branch (the fallback reader — two
   parsers is how a mechanism half-survives a removal)
4. `_port_declaration_type`
5. `port_case_label`
6. `load_declared_ports`
7. `port_bindings`
8. `apply_wiring`
9. `render_port_binding_report`
10. the `port-fake-real-swap` half of `render_oracle_statement`, and its
    `wiring` / `wiring_notes` parameters
11. the port-first precedence in `adapter_for_case`
12. `--wiring` and `--port-manifest`, and the emitted per-case program's
    `binds=` / `port=` / `fake=` fields

### 2.2 Produced-code figures, three ways

`scripts/code_complexity.py scripts tests examples/validation
specs/results/scorecards/ports-as-adapters/GOAL-port-reach/measure --json`,
identical command and identical interpreter (`python3.14`) for all three columns.

| tree | scope | SM-01's sealed before | re-measured at `f0c215d` | after `067c5ea` | delta vs `f0c215d` |
|---|---|---|---|---|---|
| `scripts/` | all | 21252 | **21252** | **21027** | **−225** |
| `scripts/` | role=code | 20140 | 20140 | 19915 | −225 |
| `tests/` | all | 20376 | **20443** | **20256** | **−187** |
| `tests/` | role=code | 214 | 214 | 214 | 0 |
| `examples/validation/` | all | 9366 | **9404** | 9404 | **0** |
| `.../GOAL-port-reach/measure/` | all | 876 | 876 | 876 | 0 |

**The middle column is not decoration.** `produced-code-before.json` does **not**
describe the commit `SM-02` branched from: `tests/` is 67 lines and
`examples/validation/` 38 lines low, because `SM-01` kept editing its own runner
and its own tests after capturing the artifact. `scripts/` — the only tree
either removal ticket materially changes, and the tree `N03` is stated on — is
**exact**. Filed as `SM-02-DF-02`; **not** repaired, because overwriting a sealed
before-state during the measurement it seals is the one move `measurement_rule`
forbids. `SM-05` should diff against the `f0c215d` column and report the SM-01
drift as its own row.

**`N03` is `SM-05`'s to score and this is only half its input**, but for the
record: `N03` predicts `scripts/` `code_lines` stays above **20189** after
`SM-02` *and* `SM-03`. `SM-02` alone leaves it at **21027**, a fall of 225 —
about **1.06 %** of the before figure. `SM-03` would have to remove a further
838 lines from `scripts/` to refute it.

### 2.3 What was NOT removed, and it is most of the list

`before-state/README.md` §4 named five removal candidates. **Three of the five
were rejected** — see §5.

---

## 3. Guard relaxation: still 3 of 3

**`corpus-neg`: `guard_relaxation` = `3 of 3`. `controls_red: []`.** Measured
after the cut, on `hexagonal-prompting-rerun/arms/arm_a` (a flat tree — **not** a
ported subject, so `FI-01-DF-01`'s cached-module defect does not apply), through
the shipped `examples/validation/ab/eval/run_controls.py`, against the sealed
`catalogue_arm_a.toml` + `controls_arm_a.toml`, over a freshly generated
`--negative-cases only` corpus (118 cases).

| class | `corpus-neg` | `suite` |
|---|---|---|
| **`guard_relaxation`** | **3 of 3** | 3 of 3 |
| `ordering` | 0 of 2 | 1 of 2 |
| `durable_content` | 0 of 2 | 2 of 2 |
| `cross_aspect` | 0 of 1 | 1 of 1 |
| `output_oracle` | 0 of 1 | 1 of 1 |
| `wrong_value` | 0 of 1 (1 not decidable) | 2 of 2 |

`polarities_with_no_deciding_control: []`, `limitations_contradicted_by_evidence:
[]`, `controls_red: []`.

**The cut did not widen.** `run_controls.py` never referenced `--wiring`,
`apply_wiring` or a `[ports.*]` table at all — the only importer of `apply_wiring`
outside the runner was `port_corpus_run.py`, a sealed artifact under
`specs/results/`. The corpus family, the negative corpus and the mapping
instruments are structurally untouched by this ticket.

### The sting that keeps this honest

`BA-P11` — *the one kill that saves the generator* — is killed by
`corpus-whole`, `corpus-slice-res`, `map-silent` and `map-checking`, and by
**neither the negative corpus nor the port corpus** (`FI-06`, per-column kill
sets). **It survives this removal untouched**, because not one of its four
killers passes through the machinery cut here. That is an argument from reach,
not a re-measurement: re-running the blind-rerun tables is `SM-05`'s harness and
`SM-02` did not run them. What `SM-02` did verify is the structural claim — that
no instrument in those tables imports anything this ticket deleted.

---

## 4. WHAT CONFIDENCE THE `suite-fake` EVIDENCE CAN ACTUALLY CARRY

`SM-01-DF-01`, owner-verified: **the two suite columns this ticket's headline
sentence rests on are structurally exempt from control checking.**
`run_port_swap.run_suite` returns `{"total_failed", "failures"}` with no
`per_action`, so `witness_count` returns `None` — which its own docstring defines
as *"not evaluable … nothing is decided against it"*. The control machinery that
exists **because** `PA-04`'s first run printed `control_red: []` over a survived
control never reaches those two columns at all.

**The honest split, and it changes the sentence but not the decision.**

**What the defect actually undermines.** The word **"strictly"**. The
domination is strict because of exactly one cell — `PA-M13-fake-drifts-from-real-
on-write`, `KILLED` by `suite-fake` and `SURVIVED` by `corpus-port-swap:fake` in
`port-swap-existing-catalogue-before.json`. That cell is uncounted, its control
is never evaluated, and `SM-01` **did not re-measure it** — `PA-M13` is not one
of the nine gap mutants. So *"`suite-fake` reaches **strictly** further than the
port column"* rests on a single cell that is **undecidable from its own
artifact**. It should be quoted with that caveat or not quoted at all.

**What the defect does not touch.** Three things, and each is enough on its own:

1. **`SM-01`'s `suite-real` / `suite-fake` are a different reading of the same
   subject, and they are counted and controlled.** `run_gap_mutants.run_detector`
   parses pytest's summary line (**28 executed** on each suite column, so "did not
   run" is excluded), compares **failure sets** against a pristine baseline rather
   than exit codes (so a skipped run cannot masquerade as a pass), and
   `SM-GM-CTRL-A` **died on both** at 28 executed each in the same run. `SM-01`
   reports these agree with the driver's uncounted columns on every cell.
2. **The decisive cells are not suite cells at all.** `SM-GM-P3` **survived all
   six** machinery columns at **1543 executed** each — counted, with `CTRL-A`
   green on those same six — and that is a demonstration that the swap is blind
   to its own premise which involves no suite column whatsoever.
   `SM-GM-P1` dies on `corpus-port-swap:fake` **and** on `pytest-full` (1370
   executed, counted, controlled), so the machinery's one kill is matched by the
   acceptance suite even with both suite columns struck out.
3. **The after-table in §1 is measured on the counted columns.** Whatever the
   sealed tables can or cannot decide, the before/after delta this ticket is
   judged on comes from `pytest-full`, `suite-*` (28 executed) and the ports
   family's own control accounting.

**Recommendation unchanged, sentence changed.** The case for defunding never
needed *strict* domination; it needed the machinery's unique reach to be **zero**,
and zero is established on counted, control-checked columns without reference to
`PA-M13`. **What must stop being said** is *"`suite-fake` strictly dominates
`corpus-port-swap:fake`"* stated flat. The supportable form is: *"every column
the machinery owns is matched by one that outlives it, on counted columns with a
green positive control; and the machinery is blind to a fake that is not a
fake."*

---

## 5. WHAT I REJECTED

**Five candidate cuts declined, and three of them were the large ones.** Under
`MF-020` the temptation runs the other way: every line I refused here would have
made the `D2` number look better.

### 5.1 The sealed measurement artifacts — 1234 lines declined

`before-state/README.md` §4 lists
`specs/results/scorecards/ports-as-adapters/GOAL-port-reach/measure/*.py`
(**1115 lines**: `run_port_swap.py` 549, `port_journal_adapters.py` 226,
`port_corpus_run.py` 148, `ports_binding.py` 137, `arm_b_fake.py` 55) and the
four `case_adapters.*.toml` carrying `[ports.*]` tables (**119 lines**) among the
things `SM-02` is "about to remove", and says: *"These are sealed measurement
artifacts, not just code. Cutting them changes the record, not only the
toolchain. `SM-02` must say which it did."*

**Declined, on three grounds.** (a) `run_gap_mutants.run_ports_family` **imports
`run_port_swap.py` as the sealed verdict-table driver** — deleting it would make
the before instrument unre-runnable, so `SM-05` could not compare like with like,
which is the whole experiment. (b) Every JSON under `GOAL-port-reach/results/`
would lose its producer, and a record whose instrument is gone cannot be
reproduced or contested. (c) It is outside `SM-02`'s `implementation_scope`
(`scripts/`, `references/`, `tests/`).

**And the honest fourth ground: it is 1234 lines, it is the single largest
number available to this ticket, and taking it would have made the removal look
five times bigger than the toolchain change actually is.** That is `MF-020`
exactly — a number falling because an edge was deleted.

**What that costs, stated rather than hidden.** After the cut,
`port_corpus_run.py` imports `apply_wiring` at module scope and dies. The driver
converts that into `harness_error` on the unmutated control run, so
`unmutated_control_failed` names the four corpus columns and every cell in them
reports **`CONTROL_RED`** — *undecided*, never `SURVIVED`. That is the driver
behaving correctly, and it is why the after-table's machinery columns read
`CONTROL_RED` rather than a fake survival.

### 5.2 `tests/test_ab_three_arms_and_port_faults.py` — 579 lines declined

It has *"port_faults"* in its name and sixteen mentions of wiring, and it would
have been an easy line to add to the deletion list. **Declined, and it is the
most important refusal here:** it exercises **composition points**, not the
binding table, and it is what **kills `SM-GM-P1` and `SM-GM-P3` on
`pytest-full`** — 7 of the 8 kill nodes across the two. Deleting it would have
removed the detector that proves this cut was free. That is `§3` of the epic
charter in one file: *removing an instrument removes the ability to detect that
the removal was harmful.*

### 5.3 The corpus — declined, twice over

`--port-cases`, `PortDeclaration`, `load_port_catalog`, `port_cases_for_corpus`
and `--negative-cases` are all untouched, and `tests/test_port_case_generation.py`
(642 lines) is kept. *"Defund `[ports.*]`"*
is supported; *"defund the corpus"* is not. Two of `SM-GM-P2`'s three
`pytest-full` kill nodes live in `test_port_case_generation.py`, so cutting it
would have manufactured a `SURVIVES`.

### 5.4 A refusal, or even a notice, on a leftover `[ports.*]` table

A mapping that still declares `[ports.*]` is now **ignored, not rejected**.
Adding a refusal is forbidden by `no_new_gates_rule`; adding a printed notice
re-introduces a reader of `ports` into the file this ticket is measured on
removing code from. **Filed as `SM-02-DF-01`, not fixed** — including the
asymmetry it leaves, where `tomllib` accepts-and-ignores the same file
`parse_simple_mapping_toml` now rejects.

### 5.5 Editing the catalogue so a dead detector reads `REMOVED` instead of `INERT`

`gap_mutants.toml` declares `port-binding-report` with
`entry_point = "scripts/run_generated_case_adapters.py"`. That file still exists
after the cut — only the machinery inside it is gone — so the runner's
`present: False → REMOVED` path does not fire, and the cell lands on **`INERT`**
(*nothing executed, decides nothing*) instead. Pointing the `entry_point` at
something that disappears would have produced the semantically nicer verdict.
**Declined:** `measurement_rule` — never edit a target to match a result. The
cell is reported as `INERT` with the reason, which carries the same information
and does not touch the sealed instrument.

### 5.6 Repairing `SM-01-DF-01`

The suggested fix (have `run_suite` parse the summary line for `total_ran`) is
four lines and would have strengthened this ticket's own evidence. **Declined:**
*file findings, never fix inline during a measurement*, and repairing the driver
mid-epic would mean the before and after were no longer the same instrument.

---

## 6. Acceptance

```
uv run --with pytest --with pyyaml python -m pytest tests -q
1363 passed in 371.50s (0:06:11)
```

**Arithmetic, exact.** `f0c215d` was **1370 passed**. Deleted
`tests/test_port_adapter_binding.py` = **21 collected nodes** (verified with
`--collect-only` on a `git archive` of the parent); added
`tests/test_ports_binding_removed.py` = **14**. 1370 − 21 + 14 = **1363**. No
test was disabled, skipped or xfailed to reach it.

### Parent-commit evidence for the new tests

`tests/test_ports_binding_removed.py`, copied unchanged onto a `git archive` of
`f0c215d` and run there:

```
12 failed, 2 passed in 0.29s
```

The twelve that fail are the removal itself. **The two that pass are the two
that must pass on both** —
`test_the_generator_still_declares_ports_and_still_builds_port_labels` and
`test_the_port_corpus_generation_flag_survives_the_cut` — the guards that the cut
did not widen into the corpus. A guard that only passed after the change would
not be a guard.

On the tip: **14 passed**.

### Collateral repaired, and it is line citations only

`test_source_citations.py` went red on four files: three `spec_manifest.yaml`
copies and `scripts/effect_conformance.py` cite `run_generated_case_adapters.py`
by **line number**, and the cut moved four of them
(`2506→2276`, `2652→2392`, `1583→1353`, `1584→1354`). Every citation still
resolves to the same anchor text it named. No prose was changed.

---

## 7. Findings filed, none fixed

`SM-02-DF-01` (minor), `SM-02-DF-02` (major) and `SM-02-DF-03` (major) in
`specs/desired_program_model/deferred_findings.yaml`. Budget 5, batch mode, **3
spent**. None fixed.

- **`SM-02-DF-01`** — the residue of the cut: a leftover `[ports.*]` table is
  accepted-and-ignored by `tomllib` and rejected by `parse_simple_mapping_toml`.
  Not repaired, because both candidate repairs ADD something and one of them is
  a gate.
- **`SM-02-DF-02`** — the sealed `produced-code-before.json` is 105 lines low
  across two of its four trees.
- **`SM-02-DF-03`** — one flaky node yields a `DIES` indistinguishable from a
  real kill unless the reader opens `new_failing_nodes`. Observed, not
  hypothesised (§1).

> **`SM-02-DF-02` is the one `SM-05` needs before it scores anything.** The
> sealed `produced-code-before.json` is 105 lines low across two of its four
> trees, so a naive after-minus-before hands `SM-02` and `SM-03` credit for
> removing `SM-01`'s own instrument. `scripts/` is exact, so `N03` survives.
