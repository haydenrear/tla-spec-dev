# RC-02 — the effect oracle, executed against this model for the first time

`run effect-conformance` has existed since MF-013 and had **never been run
against `specs/current`**. `case_codegen.generation_status` was `planned`, no
`specs/*/generated/` existed, and every `declared` verdict in every MF-026 audit
round was an unchecked declaration. RC-01 made the oracle *reachable* by shipping
`generate cases`; this ticket **ran it**.

Nothing here was tuned. The oracle exits 1 on every run below and that is the
result being reported, not a problem being managed.

## What was run

| # | Run | Evidence | Verdict | Exit |
|---|---|---|---|---|
| 1 | `run effect-conformance --target specs/current` (no corpus) | `run-no-corpus.txt`, `no-corpus-report.json` | `dead_surface` | 1 |
| 2 | the same, over an executed corpus of this model | `run-action-covering-corpus.txt`, `action-covering-report.json` | **`unobservable`** | 1 |
| 3 | run 2 with RC-01's unattached ports restored (the N-1 counterfactual) | `run-counterfactual-pre-n1.txt` | `unobservable` | 1 |
| 4 | the same against a shipped example (`examples/effect_providers/atomic_publisher`) | `run-example-corpus.txt` | n/a — refused | 2 |

## Run 2 — the headline, verbatim

```
effect declarations: 12 port(s) from specs/current/spec_manifest.yaml
effect conformance unobservable: 57 observed effect(s) over 8 case(s),
  12 declared port(s), 20 gap(s), 9 dead port(s), 15 unobservable target(s)
```

`unobservable` outranks the other findings by design: every adapter in this
model's executable segment spawns the CLI as a child process, the sandbox
observes the in-process CPython runtime only, and the report says in its own
words that it **"certifies NOTHING"** about those 15 boundaries.

**20 UNDECLARED EFFECTS.** Two shapes, both real:

* `filesystem.write -> <work>/case_*/target-repo` on `OpenTicket`,
  `RecordBudgets`, `ScaffoldProject`, `ScaffoldWorkflow`, `UpdateTicketCurrent`,
  `UpdateTicketDesired` — the adapter's own before-state materialization
  (`adapter_case_runtime.materialize_before` replays the CLI prefix). The oracle
  cannot tell an adapter's scaffolding from the program's behaviour and
  attributes both to the action under test.
* `process.spawn -> python3 scripts/tla_spec_dev.py … scaffold project` etc. on
  the same actions, from the same replay.
* One that is neither: `filesystem.write ->
  …/target-repo/specs/program_model/spec_manifest.yaml` **during
  `case_0004_record_budgets`, action `RecordBudgets`** — whose effects row is
  deliberately EMPTY, claiming "performs no distinct effect". The writer is the
  replay rather than the command, so the row is not thereby falsified; but the
  only execution ever performed reports a write against the row that says there
  is none, and no oracle had ever been in a position to say so.

**9 DEAD PORTS**, including `cli_download` and `cli_artifact_delete` — the two
ports this ticket attached to `InstallLocalCli`. Attaching them satisfies the
manifest rule and the `@port` mirror rule; it does **not** make them exercised,
because they live in `install-tlc2.sh` and no adapter runs it. Reported plainly
rather than counted as a close.

## Run 3 — the N-1 counterfactual, and what it settles

Same corpus, same adapters, one edit: `InstallLocalCli: [cli_artifact]`, as
RC-01 shipped it.

| | gaps | dead ports |
|---|---|---|
| RC-01's rows (run 3) | **22** | **10** |
| RC-02's rows (run 2) | **20** | **9** |

The exact difference, from `diff` over the two findings lists:

```
- UNDECLARED EFFECT: process.spawn -> bash …/skill-scripts/install-tla-spec-dev.sh
    during case_0002_install_local_cli (action InstallLocalCli)
- UNDECLARED EFFECT: process.spawn -> …/bin/tla-spec-dev --version
    during case_0002_install_local_cli (action InstallLocalCli)
- DEAD MODEL SURFACE: port TlaSpecDevCliPort.cli_selftest_process
```

So the audit's claim — *"one run of the now-reachable oracle would have caught
N-1"* — is **confirmed for `cli_selftest_process` and not for the other two**.
`cli_download` and `cli_artifact_delete` report dead in BOTH runs, so a run would
have told RC-01 nothing about them. The claim is right about the mechanism and
one third right about the instance.

It also shows why the always-on replacement matters: the oracle's dead-surface
finding needs an executed corpus, and run 1 (no corpus) reports **all 12** ports
dead, in which the specific signal is indistinguishable from noise.
`tests/test_spec_manifest_records.py::test_every_declared_port_is_attached_to_an_action`
needs no corpus, no TLC and no adapter, and fails on the declaration itself.

## Why the corpus is 8 cases, and why `generation_status` stays `planned`

`tla-spec-dev generate cases specs/current/TlaSpecDevCli.tla specs/current/MCsmall.cfg`
was run in full (`generate-cases-mcsmall.txt`). It produced:

* **3,678,217 cases** from 118,573 distinct states (average outdegree 31);
* a **7.4 GB `cases.py`**, which CPython cannot import;
* **18,391× the manifest's own `max_internal_cases_per_component: 200`**, so the
  shipped cap gate REFUSED the corpus and exited 2.

`MCsmall.cfg` is already the reduced config MF-028 added for exactly this
purpose (1 ticket, 1 spec root). Projection does not rescue it — measured, not
assumed:

| projection | distinct states | distinct transitions |
|---|---|---|
| none | 118,573 | 3,678,217 |
| drop `lastCommand`, `result` (the two `UNPROJECTABLE_FIELDS`) | 20,356 | 628,424 |
| also drop `architecture_delta` | 5,092 | 96,056 |

**This model has no `tlc_projection.py`.** Every worked example in
`references/case_modules.md` pairs generation with one; this repository's own
model does not have one, which is the direct cause of the 3.7M-case corpus and
therefore of the oracle never having run.

So the corpus that was executed is the **action-covering subset**:
`build_action_covering_corpus.py` takes the real TLC dump of `MCsmall.cfg` and,
for each action, the first edge whose case the action's own adapter accepts via
the shipped `adapter_accepts_case`, then renders it with the shipped
`render_python_package`. It is a **lower bound**: fewer cases can only exercise
fewer ports, so no finding above can be an artifact of the subsetting, and no
port it reports dead could have been reported dead by a smaller corpus only.

`generation_status` therefore **stays `planned`**. The run does not support
moving it: there is no corpus of this model that the shipped gate accepts, and
`specs/*/generated/` still does not exist. Claiming `generated` would assert the
thing this evidence disproves.

## Two defects that stopped the very first run

Both were hit before a single case executed, and both are filed rather than
fixed (they are outside RC-02's slice):

1. `ModuleNotFoundError: No module named 'production_adapters'` —
   `run effect-conformance` executes adapters in-process and never puts the
   target spec directory on `sys.path`, while `run spec-unit-tests` puts it on
   `PYTHONPATH` for the enforcing runner. The standalone oracle cannot load the
   scaffolded `case_adapters.toml` convention. Worked around here with
   `PYTHONPATH=$PWD/specs/current:$PWD`. → **RC-02-DF-02**
2. `TypeError: adapter <AnalyzeArchitectureAdapter> does not define run(case, …)`
   — the oracle never consults `can_run` / `adapter_accepts_case` and has no skip
   path, so it aborts the whole run on the first `apply()`-only adapter. **9 of
   this model's 17 adapters** (every `analyze`, `run` and `close` action, plus
   `GenerateCases`) are `apply()`-only. → **RC-02-DF-03**

## Reproducing

```bash
python3 - <<'PY'
import sys; from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from scripts import case_modules, generate_cases_from_tlc_dump as g
tla = Path("specs/current/TlaSpecDevCli.tla").resolve()
dot = Path("specs/results/rc02-effect-conformance/TlaSpecDevCli-mcsmall.dot").resolve()
g.run_tlc_dump(tla, Path("specs/current/MCsmall.cfg").resolve(), dot, "tlc2",
               case_modules.resolve_search_path(tla, []))
PY
python3 specs/results/rc02-effect-conformance/build_action_covering_corpus.py \
  specs/results/rc02-effect-conformance/TlaSpecDevCli-mcsmall.dot \
  specs/results/rc02-effect-conformance/corpus-executed

PYTHONPATH="$PWD/specs/current:$PWD" python3 scripts/tla_spec_dev.py --spec-root specs \
  run effect-conformance --target specs/current \
  --cases-dir specs/results/rc02-effect-conformance/corpus-executed
```

The 428 MB `.dot` is not committed; the 8-case corpus it produced is, under
`corpus-executed/`.
