# The BEFORE state — captured by SM-01, before anything was removed

**This is the input `D2` anchor 3 has never had.** The anchor reads *"a
simplification was made and its effect measured — **the before and after figures
are both recorded**"*, and in five epics there has never been a before, because
every subject this project has scored was greenfield. `SM-05` diffs the after
against exactly these numbers.

Captured at the `SM-01` parent commit, on the branch `epic/subtract-to-measure`.
Nothing here is a verdict and nothing here proposes a cut — `CD-01`, the
thermometer rule: the instrument may not choose the boundary, including in this
epic, where the boundary is our own.

---

## 1. Produced-code descriptor — `scripts/code_complexity.py` over the shipped tree

Four trees, measured separately and never averaged. `--json` record in
`produced-code-before.json`; the rendered tables, including the per-module rows
and the import edges, in `produced-code-before.txt`.

Command, verbatim:

```
python3 scripts/code_complexity.py \
  scripts tests examples/validation \
  specs/results/scorecards/ports-as-adapters/GOAL-port-reach/measure --json
```

| tree | scope | modules | code_lines | callables | classes | public_surface | branch_points (effectful) | instance_state (effectful) |
|---|---|---|---|---|---|---|---|---|
| `scripts/` | all modules | 33 | 21252 | 803 | 90 | 882 | 3268 | 31 |
| `scripts/` | role=code | 31 | 20140 | 766 | 86 | 831 | 3145 | 31 |
| `tests/` | all modules | 49 | 20376 | 1291 | 75 | 1450 | 741 | 12 |
| `tests/` | role=code | 2 | 214 | 9 | 5 | 13 | 2 | 0 |
| `examples/validation/` | all modules | 89 | 9366 | 481 | 67 | 618 | 1204 | 33 |
| `examples/validation/` | role=code | 82 | 8802 | 413 | 65 | 546 | 1199 | 33 |
| `.../GOAL-port-reach/measure/` | all modules | 5 | 876 | 31 | 5 | 39 | 84 | 3 |
| `.../GOAL-port-reach/measure/` | role=code | 5 | 876 | 31 | 5 | 39 | 84 | 3 |

Whole-tree aggregate across those four trees: **176 modules, 51 870 code_lines,
2 606 callables, 237 classes, 2 989 public_surface.**

**Read this beside `MF-020`, which is printed inside the instrument itself: a
figure falling is not evidence the design improved. There is deliberately no
`--compare` mode and no delta output.** `SM-05` is expected to run the same
command and print two tables, not a subtraction.

## 2. The acceptance suite

```
uv run --with pytest --with pyyaml python -m pytest tests -q
1335 passed in 329.53s (0:05:29)
```

In a `git archive` tree — no `.git` — the same command is **9 failed, 1326
passed in 158.81s**. The nine are git-history readers and fail for that reason
alone. They are named in `gap-mutants-before.json` under `baselines`, and the
gap-mutant verdict rule compares *failure sets*, never exit codes, because of
them.

## 3. Instrument registry

Full sweep in `instrument-sweep-before.md`, derived by parsing
`instruments.toml` rather than by quoting a previous round's prose. The
registry's own run is `instruments-before.json` / `instruments-before.txt`.

| figure | before |
|---|---|
| enumerated rows | **40** |
| classified `not-an-instrument` | **5** |
| instruments | **35** |
| with a demonstrated failing input | **26** |
| without one | **9** |
| with a demonstrated blind spot | **12** |
| distinct declared paths | **38** |
| pytest failing slots asserting only `expect_exit = 0` | **12 — every pytest failing slot in the file** |
| rows where `failing.nodes == passing.nodes` | **2** (`complexity-ledger`, `case-modules-validate`) |

**`denominator_rule`.** `26 of 35` is the number on the card. After `SM-03`,
deletions are reported separately from repairs and both counts are given, so a
ratio that rose because the denominator shrank is visible as such.

## 4. What `SM-02` is about to remove, in lines

| file | lines | note |
|---|---|---|
| `scripts/run_generated_case_adapters.py` | 2717 total | ~250 of them are `[ports.*]`: the `AdapterMapping` port fields, `load_mappings`' `ports` branch, `port_case_label`, `load_declared_ports`, `port_bindings`, `apply_wiring`, `render_port_binding_report`, the port half of `render_oracle_statement`, the fallback parser branch, the port-first sort key in `adapter_for_case`, the emitted-program fields, and the `--wiring` / `--port-manifest` argparse blocks |
| `tests/test_port_adapter_binding.py` | 462 | the only pytest file that exercises `[ports.*]`; **16 test functions, 46 collected nodes together with `test_port_case_generation.py`** |
| `references/case_modules.md` | 782 total | `:436-497` documents the mechanism |
| `.../GOAL-port-reach/measure/*.py` | 1115 | `run_port_swap.py` 549, `port_journal_adapters.py` 226, `port_corpus_run.py` 148, `ports_binding.py` 137, `arm_b_fake.py` 55 |
| `.../GOAL-port-reach/measure/case_adapters.*.toml` | 119 | four of the six carry a `[ports.*]` table |

**These are sealed measurement artifacts, not just code.** Cutting them changes
the record, not only the toolchain. `SM-02` must say which it did.

## 5. The ports evidence at the tip, re-derived rather than quoted

`port-swap-existing-catalogue-before.json` — `run_port_swap.py --subject
reference_ports` at this commit, against the **pre-existing** `seeded_faults.toml`
catalogue, over a freshly generated `--port-cases only` corpus (1855 cases).

| mutant | `corpus-port-swap:real` | `corpus-port-swap:fake` | `corpus-action-bound:real` | `corpus-action-bound:fake` | `suite-real` | `suite-fake` |
|---|---|---|---|---|---|---|
| `FI-M15-positive-control-commit-total-too-large` | KILLED | KILLED | KILLED | KILLED | KILLED | KILLED |
| `PA-M11-real-adapter-drops-close-lines` | KILLED | SURVIVED | KILLED | KILLED | KILLED | SURVIVED |
| `PA-M12-fake-adapter-drops-close-lines` | SURVIVED | KILLED | SURVIVED | SURVIVED | SURVIVED | KILLED |
| `PA-M13-fake-drifts-from-real-on-write` | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED | **KILLED** |
| `PA-M14-positive-control-accepted-hold-too-large` | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED | KILLED |

`suite-fake` — four lines of `quota_ledger_fake.py`, no binding table, no wiring
flag — kills everything `corpus-port-swap:fake` kills **plus `PA-M13`**. That is
the strict domination `SM-02` rests on, re-derived here rather than quoted.

**And the driver returned 0 while printing four RED control/instrument pairs**
(`PA-M14` survived all four corpus columns having executed 294 accepting
`Reserve` cases on each). `FI-02-DF-02`. Every number in the corpus columns above
is therefore a **floor**, and nothing downstream may read this driver's exit
code.

## 6. The gap mutants

`gap-mutants-before.json`, produced by
`examples/validation/gap_mutants/run_gap_mutants.py` from
`examples/validation/gap_mutants/gap_mutants.toml`. **Seeded and committed
before `SM-02` or `SM-03` was dispatched.** The full table and its reading are in
`../SM-01-RESULTS.md`.

`SM-05` re-runs the same command on the integrated tip:

```
python3 examples/validation/gap_mutants/run_gap_mutants.py \
  --cases <scratch>/specs/corpus-port/spec-unit/quota_port \
  --out specs/results/scorecards/subtract-to-measure/gap-mutants-after.json
```

with the corpus regenerated by the recipe in
`../../ports-as-adapters/GOAL-port-reach/RESULTS.md`. Each mutant then reports
`DIES` (redundant, the cut was free) or `SURVIVES` (load-bearing, and now
priced). A detector whose entry point no longer exists reports `REMOVED`, never
`SURVIVES`.

**Run of record: 26 min 43 s, zero mutants failed to apply, both positive
controls died on every detector they declare, `control_red` empty.**

| what | before |
|---|---|
| gap mutants seeded | **9** |
| positive controls | **2**, both green |
| detectors | **7** (3 of which do not survive `SM-02`) |
| mechanisms with no seedable gap, named | **4** |
| `pytest-full` baseline on the staged tree | exit 1, **1370 executed, 9 failing** (all nine read git history) |
| cells with no executable count | **2** — the shipped driver's own suite columns, `SM-01-DF-01` |

Four mechanisms have **no seedable gap** and are named in the artifact's
`not_seedable` block with their reasons rather than dropped from the table.
