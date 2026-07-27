# ex4 run 1 — the mechanical arms, scored against PREDICTIONS.md (A1-*, A2-*, A3-P1)

Run date 2026-07-27, EV-02. **Mechanical run: no agent.** Aim 1 (seeded content
faults, both declared arms), aim 2 (the authored aspects), and the generation
half of aim 3. Corpus `gen1`, generated fresh from `Pipeline.tla` in this
worktree.

Every number below is `killed/seeded` per fault class per arm, or a case count.
Nothing was fixed: the mutants are applied by a context manager that restores
the file and clears `__pycache__` on exit, and `git status` on `examples/` is
empty after every step.

## The control (MF-016 — without it "killed" means nothing)

| arm | mapping | cases | exit | verdict |
|---|---|---|---|---|
| **A — corpus alone** | `case_adapters_corpus_only.toml` (`silent_ledger_store_provider`) | 330 | **0** | GREEN |
| **B — corpus + content provider** | `case_adapters.toml` (`ledger_store_provider`) | 330 | **0** | GREEN |

Both controls green on the unmutated program before any mutant was applied.
**A1-P1 PASS.** Every kill below is therefore admissible.

## Aim 1 — the kill table, per fault class, per arm

`killed` = the arm's run exited nonzero with the mutant in place. `points` =
`ERROR: N batched case executions failed`, the runner's own count.

| id | fault class | ARM A killed | A points | A detector | ARM B killed | B points | B detector | predicted arm | scored |
|---|---|---|---|---|---|---|---|---|---|
| F1 | wrong value | **YES** | 44 | `tla_projected_state` | **YES** | 88 | `tla_projected_state` + `provider_content_assertion` | A and B | **as predicted** |
| F2 | wrong field | **YES** | 88 | `tla_output` | **YES** | 88 | `tla_output` | A and B | **as predicted** |
| F3 | off-by-one count (durable) | **NO** | 0 | — | **YES** | 44 | `provider_content_assertion` | B only | **as predicted** |
| F4 | wrong status | **YES** | 22 | `tla_output` | **YES** | 22 | `tla_output` | A and B | **as predicted** |
| F5 | silently-swallowed error | **NO** | 0 | — | **YES** | 44 | `provider_content_assertion` | B only | **as predicted** |
| F6 | off-by-one count (in-memory) | **YES** | 15 | `tla_output` | **YES** | 15 | `tla_output` | A and B | **as predicted** |

**ARM A: 4 of 6. ARM B: 6 of 6.** Every per-fault prediction in
`seeded_faults.toml` held, including both predicted survivors.

- **A1-P2 PASS** — ARM A kills F1/F2/F4/F6 and survives F3/F5, exactly.
- **A1-P3 PASS** — ARM B kills all six; F3 and F5 by `provider_content_assertion`
  and by nothing else.
- **A1-P4 PASS** — the headline is **4/6 corpus, 6/6 with the provider**, and it
  is reported per arm here and nowhere as an aggregate.
- **A1-P5 PASS** — F4 (wrong status, correct after-state) died under ARM A on
  `tla_output` alone. The class MF-038 could not see at all is closed by the
  **content-bearing output projection**, which was MF-038's own first
  recommendation. That is a corpus-side win and it is not a fuzzing win.
- **A1-P6 PASS, and it resolves the way the fixture hoped it would not have to
  hedge.** F3 and F6 are one fault class on two surfaces. F6 (in-memory) dies
  under ARM A; F3 (durable) does not. **Detectability here is a property of the
  observation surface, not of the fault class** — MF-038's survivor analysis,
  reproduced deliberately and confirmed.

### What ARM A's 4/6 is and is not, against the MF-038 baseline

MF-038: **0 of 9** content bugs, kill rate 0.31, green control. ARM A here:
**4 of 6**, green control. The comparison is real but it is bounded, and the
bound must travel with the number:

1. **EV-01-DF-01 (upper bound).** `scripts/infer_action_params.py` recovers
   **0 of 5** parameters on this model, so every case carries
   `params={'i': UNCHECKED}` and the adapter selects the action argument by
   diffing `case.before` against `case.after` — **the oracle hands the adapter
   the argument.** ARM A's 4/6 is therefore an **upper bound** on what a corpus
   with honestly recovered parameters would achieve. Blind run B confirmed this
   from the outside without ever seeing DF-01. Reporting "4/6 beats 0/9" without
   this caveat is overclaiming, and this run does not.
2. **No fault of the class "acted on the wrong item" is seeded** (A1-P7), for
   the reason in 1. The silence is not a result.
3. **F4's kill belongs to the output projection, not to the effect runtime.**
   MF-038's only output oracle was a process exit code; ex4 projects
   `status`/`ledger_size`/`queue_size`/`delivered_size`. Attribute the win to
   the projection.
4. **F3 and F5's kills belong to the provider, not to the corpus** (DP-8). ARM A
   is the MF-038 instrument and it reproduces MF-038's result on exactly the
   faults MF-038 was made of: durable side-effects nothing reads.

### Two measurement notes about the instrument itself

- **Detector attribution is first-oracle-to-fire, not a complete set.** The
  runner compares adapter output before after-state, so F2 reports `tla_output`
  only although the after-state also differs. Co-detection cannot be read off
  the logs.
- **F6 is a partial kill: 15 of 66 `Deliver` cases.** The mutant deletes a
  second queue element, which is only observable when the queue holds a second
  element at that index. A binary killed/survived table hides that; the point
  column is in the table for this reason.

## Aim 2 — the manual-test starter, re-measured

`case_modules.py validate` exit 0, `coverage` exit 0, on corpora regenerated in
this worktree:

| aspect | form | authored lines | states | cases | actions entered |
|---|---|---|---|---|---|
| `Scenario_DeliveryPath` | slice | 14 | 25 | **50** (Accept 10, Enqueue 20, Deliver 20) | 3 |
| `Scenario_RecordAfterDelivery` | Given | 22 | 8 | **6** (Fail 4, Record 2) | 2 |
| whole view `Pipeline` | — | — | 121 | **330** | 5 |

**A2-P1 PASS** (EV-01's numbers reproduce exactly). **A2-P3 PASS** — both
aspects run against the same `actions.yml`, adapters and providers, unchanged.
**A2-P2 honoured**: the ratios are **3.6 cases/line for the slice and 0.27
cases/line for the Given**, and both are stated. The slice multiplies; the Given
divides, and dividing is what it is for.

**DP-3 PASS (tool side).** `coverage` prints, unprompted:

> Cross-aspect interleaving is not in this table. Slices do not enumerate the
> interleavings between aspects; only a whole-view run does.

Union of the two aspects = 56 cases; the view = 330. The risk lives in the
writing, not the tool, and this record does not report 56 as coverage of 330.

### Finding EV-02-DF-02 — a checked-in case module is not reproducible in place

Independently reproduced (blind run B found it first). Generating from
`specs/case_modules/`, where the convention keeps them:

```
tlc2 ... specs/case_modules/Scenario_DeliveryPath.tla   ->  exit 150
```

TLC runs with `cwd` = the `.tla`'s directory and no module search path, so a
module in `specs/case_modules/` cannot `EXTENDS` a view in
`specs/program_model/`. The fixture README's "Rerun" section documents the
copy-in/copy-out dance; nothing in the tool or the error says why it is needed.
Artifact: `artifacts/inplace.log`. **Filed, not fixed.**

## Aim 3 — the generation control (A3-P1)

`cases.py` sha256 =
`33e07e0de5360fae105466c0ea7869a4face3c3dfa116de63452888c78be6f97` — **the
value EV-01 recorded**, reproduced in a different worktree, a different output
directory, and (see run 2) a different Python interpreter. `types.py`,
`validators.py`, `doubles.py`, `__init__.py` identical too. **A3-P1 PASS.**

## Fixture integrity (X-P4)

`check_twins.py` exit 0 before and after; all five hashes match.
`git status --porcelain examples/` empty after every mutant. No answer key,
`PREDICTIONS.md`, or `seeded_faults.toml` was edited. **X-P4 PASS.**

## Artifacts

`artifacts/` — 14 mutant/control logs (both arms), `kill_matrix.json`,
`validate.txt`, `coverage.txt`, `inplace.log`, `ex4_reflexion.txt`, the DF-02
reproduction (`ex4_descriptor.txt`, `ex4_reflexion.txt`, `ex4_reflexion.json`),
and the three harness scripts (`kill_matrix.py`, `replay.py`, `df02_blast.py`)
so every number here is re-derivable.
