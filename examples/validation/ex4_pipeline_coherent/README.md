# ex4 — the decomposable fixture, with matching production code

**Purpose: the positive test the architecture half of this epic did not have.**
AC-01 measured both real models available to it and both refused: this
repository's own model has one component at Q = 0.000, and the
`distributed_history` External view has two components but 9 of 12 actions
crossing. A run in which every model refuses proves only that the refusal
works. This fixture is a model that genuinely decomposes, with production code
that matches it, so `coherent` can be observed at least once and so
`ex5_pipeline_divergent` has something to be a twin *of*.

It is derived from the epic owner's probe model (`specs/results/Pipeline.tla`,
Q = 0.219) with **one variable and one action added**, for a reason recorded
below under "Why three components and not two".

Everything in the ANSWER KEY sections was measured on this branch before any
eval agent ran, and is reproduced by the commands in "Rerun".

---

## ANSWER KEY 1 — the architecture (what EV-02 scores against)

Command:

```bash
cd examples/validation/ex4_pipeline_coherent
python3 ../../../scripts/architecture_reflexion.py \
  specs/program_model/Pipeline.tla specs/program_model/Pipeline.cfg \
  --components specs/program_model/architecture_components.yaml \
  --code pipeline --map specs/program_model/architecture_map.yaml
```

| fact | value |
|---|---|
| `verdict.architecture_scan` | **`coherent`** |
| exit code | 0 |
| modules scanned / mapped | 8 / 8 |
| components realized | 3 of 3 |
| edges extracted | 4 |
| internal edges | 2 |
| **convergences** | **2** |
| **divergences** | **0** |
| **absences** | **0** |
| ported pairs | `dispatch<->ingest`, `dispatch<->ledger` |
| **unported pair** | **`ingest<->ledger`** |
| `divergence_detectable` | `true` |
| `basis.map_digest` | `sha256:51fc63424…` |
| `basis.architecture_digest` | `sha256:96e32621b…` |

The two convergences, exactly:

```
dispatch -> ingest  (P1)  pipeline/dispatch/delivery.py:10  import pipeline.ingest.queue.WorkQueue
ledger   -> dispatch (P2) pipeline/ledger/journal.py:13     import pipeline.dispatch.delivery.Dispatcher
```

**Any divergence reported on this fixture is a FALSE POSITIVE and is counted as
one.** That is the entire reason this fixture exists next to the twin: a check
that finds divergence everywhere is as useless as one that finds it nowhere.

### The model-side facts the answer key also expects

`analyze architecture` on the declared partition:

```
graph modularity Q = 0.133
[OK] component_count: 3            (rule >= 2)
[OK] modularity_q:   0.132653      (rule > 0)
[OK] crossing_action_fraction: 0.4 (rule <= 0.5)
MEASURED RESULT: the partition is a cut -- every criterion above is met.

Single-writer violations:
  delivered: written from ingest, dispatch by Deliver, Fail
  queue:     written from ingest, dispatch by Deliver, Enqueue

Spanning action: Deliver (writes queue in ingest AND delivered in dispatch)
```

**These two single-writer violations are CORRECT OUTPUT, not findings against
the fixture.** The epic owner flagged this in advance: the handoff action
`Deliver` writes on both sides of the boundary, so it is simultaneously the
port P1 and a single-writer violation. A handoff that mutates both sides in one
step has no explicit commit point; that is the atomicity-fidelity signal and it
is the honest answer. **An EV-02 report that names them is scored CORRECT. An
EV-02 report that treats them as a defect to be "fixed" has misread the
descriptor, and a scorer who counts them as false positives has miscalibrated
the key.**

### Why three components and not two

The owner's probe model has two components. A two-component partition has
exactly **one** component pair, that pair is ported, and
`unfalsifiable_coherence` therefore fires on every reflexion run over it — "no
divergences" would be a property of the declared architecture, not a
measurement of the code. **A fixture that cannot produce a divergence cannot be
the positive test for a divergence check.** Adding `ledger` and `Record` leaves
`ingest<->ledger` unported, so the coherent result above is falsifiable and the
twin's divergences are detectable.

The partition is **declared** (`architecture_components.yaml`) rather than
emergent, for a measured reason: greedy modularity maximization on this model
returns two components (`queue` clusters with ingest), which is the
two-component problem again. The declared path is also the path AC-01 says a
real user takes, and the path the centrepiece experiment attacks.

### The twins are the same model

`ex5_pipeline_divergent` ships **byte-identical** copies of the four files that
are the whole input to the architecture experiment:

```
specs/program_model/Pipeline.tla
specs/program_model/Pipeline.cfg
specs/program_model/architecture_components.yaml
specs/program_model/architecture_map.yaml
```

`python3 examples/validation/check_twins.py` checks it and exits nonzero if any
of the four has drifted. If they ever differ, the twins are two different
experiments and any EV-02 number measured across them is void.

The twins also ship a **byte-identical** `tests/test_behavior.py` (8 tests, both
green). A behavioral suite cannot tell them apart. Whatever EV-02 measures here
is measuring structure, not behavior.

### What this fixture cannot answer, stated so a silence is not read as a result

**The composition root has nowhere to live.** `tests/driver.py` wires all three
components. Inside `--code pipeline` it would give its component an edge to all
three — including the unported `ingest<->ledger` pair — and the *coherent*
fixture would report a divergence for a file whose only job is wiring. The
fixture answers it the only way the shipped tool allows: keep the wiring
outside the code root. Real projects hit this. Treat "where does the
composition root go" as a question the reflexion check does not have an answer
for, not as a defect of the fixture.

---

## ANSWER KEY 2 — the seeded content faults (aim 1)

The catalog is `seeded_faults.toml`, fixed and committed **before any corpus
run**. Six faults, one per named class plus a second off-by-one. Each row
carries the exact observable and the arm predicted to catch it.

Two arms, and they are **two declared adapter mappings, not one mapping with
its assertions switched off**:

| arm | mapping | instrument |
|---|---|---|
| **A — corpus alone** | `specs/program_model/case_adapters_corpus_only.toml` | projected after-state + adapter output. Binds a real file-backed ledger store that asserts nothing. This is the MF-038 instrument. |
| **B — corpus + content provider** | `specs/program_model/case_adapters.toml` | the same, plus a provider assertion that the persisted bytes equal the modeled after-state. This is the ex1-run4 instrument. |

| id | class | site | observable | predicted detector |
|---|---|---|---|---|
| F1 | wrong value | `pipeline/ledger/journal.py` `_entries.append(item)` | `ledger` after-state records `I1` for `i1` | A (`tla_projected_state`) and B |
| F2 | wrong field | `pipeline/dispatch/failures.py` `_failed.add(item)` | `failed`/`delivered` after-state; output `delivered_size` | A (`tla_projected_state`, `tla_output`) and B |
| F3 | off-by-one count | `journal.py` `_store.persist(...)` | persisted file is one entry short; **nothing in the projected state or output reads the file** | **B only.** A is predicted to SURVIVE — the MF-038 shape exactly |
| F4 | wrong status | `pipeline/ingest/inbox.py` `return True` | output `status` == `rejected` where the model says `applied`; after-state is CORRECT | A (`tla_output`) and B |
| F5 | silently-swallowed error | `journal.py` `_store.persist(...)` | persisted file empty, no exception escapes, `record()` still returns True | **B only.** A is predicted to SURVIVE |
| F6 | off-by-one count | `pipeline/ingest/queue.py` `_queue.remove(item)` | `queue` after-state one short; output `queue_size` one lower | A (`tla_projected_state`, `tla_output`) and B |

**Why F3 and F6 are the same class on two surfaces.** If both die and F3 dies
only under arm B, detectability is a property of the **observation surface**,
not of the fault class — which is what MF-038's own survivor analysis concluded
("a shallow-oracle result, not a coverage-of-code result") and what an
aggregate kill rate hides. If F6 also survives arm A, the corpus is weaker than
this fixture assumes and **the fixture is the finding**.

**EV-01 ran the CONTROL only.** Both arms are green on the unmutated program —
330 cases, exit 0 (`evidence/control-armA-corpus-only.log`,
`evidence/control-armB-corpus-plus-provider.log`). Without a green control,
"killed" means nothing (MF-016). The mutants are deliberately **not** run here:
a fixture author who scores his own instrument has deleted the measurement.

**The class this instrument cannot measure.** A fault whose only symptom is
*acting on the wrong item*. `scripts/infer_action_params.py` recovers **0 of 5**
parameters on this model — every action is `\E i \in Items` guarded by set
membership — so every case carries `params={'i': UNCHECKED}` and the adapters
pick the argument by diffing before against after. The oracle tells them which
item. Filed as **EV-01-DF-01**. No fault of that class is seeded, because its
survival would say nothing about the corpus.

> **RP-02 AMENDMENT — the paragraph above is superseded, and it was WRONG on
> its second half.** RP-02 added a `set-membership` mechanism to the generator:
> for `v' = v \cup {i}` / `v' = v \ {i}` the argument is the element that
> entered or left the set, cross-checked across every such conjunct. All **5 of
> 5** parameters now recover; all 330 cases carry `params={'i': 'i1'}` or
> `{'i': 'i2'}`; the adapter reads the argument off the case and never touches
> `case.after`. New corpus fingerprint in `evidence/corpus_fingerprint.txt`.
>
> The claim that this instrument *cannot measure* the wrong-item class was
> never tested, and it is false. RP-02 seeded two wrong-item faults and both
> are **KILLED — before the fix as well as after it** (the old adapter was
> handed the correct argument by the diff and passed it in, so a program that
> then ignored it still diverged in the projected after-state). The leak's real
> cost was that the argument was not in the artifact, nothing audited it, and
> the MF-028 vacuity trap was live. Measurement:
> `specs/tickets/RP-02/results/mutant-catalog-rerun.md`.
>
> **What did NOT change: guard relaxation is still 0 of 3.** All 330 recovered
> arguments are arguments the guard ACCEPTS (counted: 330 enabled, 0 rejected),
> because a TLC state graph has no edge for a transition that did not fire.
> That is the structural half of the two causes EV-02 named, and it is
> untouched by parameter recovery.

---

## ANSWER KEY 3 — the manual-test starter (aim 2)

The measured question: *how many lines does a person write, and how many
distinct behaviors come back?* Both aspects below were written knowing only the
public surface of `Pipeline.tla` — the action names, their guards, and the six
variables. Neither adds state, constants, or actions.

| aspect | form | lines a human wrote (non-blank, `.tla` + `.cfg`) | TLC states | cases | actions entered |
|---|---|---|---|---|---|
| `Scenario_DeliveryPath` | slice | **14** (8 + 6) | 25 | **50** | Accept 10, Enqueue 20, Deliver 20 |
| `Scenario_RecordAfterDelivery` | Given | **22** (16 + 6) | 8 | **6** | Record 2, Fail 4 |
| whole view (`Pipeline`) | — | — | 121 | **330** | Accept 22, Deliver 66, Enqueue 110, Fail 88, Record 44 |

**Ratio: 14 authored lines → 50 cases over 3 actions (3.6 cases per line);
22 authored lines → 6 cases over 2 actions (0.27 cases per line).**

Read those two numbers together, because reporting only the first would sell
the mechanism. The slice multiplies; the **Given divides**, and dividing is
what it is for — it replaces enumeration with an asserted pre-state and a
written claim. `Scenario_RecordAfterDelivery`'s claim is in
`spec_manifest.yaml` and is the reviewable part of the reduction.

`case_modules.py coverage` (evidence: `evidence/case_module_coverage.txt`)
reports `UNCOVERED: none` and states, every time, that cross-aspect
interleaving is **not** in the table. The union of the two aspects is 56 cases;
the view is 330. They are not the same corpus and the report says so.

---

## ANSWER KEY 4 — determinism (aim 3)

The owner already measured the generation half as byte-identical, so the risk
lives in **execution**. Both halves are recorded here, because a control that
always passes is how you notice the day it stops.

| half | check | result |
|---|---|---|
| generation (control) | two full regenerations, sha256 over the package | **identical**: `cases.py` `33e07e0de5360fae105466c0ea7869a4face3c3dfa116de63452888c78be6f97`, and `types.py` / `validators.py` / `doubles.py` / `__init__.py` all identical |
| **execution** | arm B run twice, over two independently generated packages | **byte-identical stdout** after normalizing the output directory path; both exit 0, 330 cases |

Corpus fingerprint of record: `evidence/corpus_fingerprint.txt`.
Any difference at all, however small, is a finding regardless of first-run
quality.

---

## Rerun (every command EV-01 actually ran)

```bash
export PATH="$HOME/.skill-manager/bin/cli:$PATH"      # tlc2
cd examples/validation/ex4_pipeline_coherent
REPO=../../..

# 1. model
timeout 120 bash $REPO/scripts/run_tlc.sh \
  specs/program_model/Pipeline.tla specs/program_model/Pipeline.cfg
#    -> 295 generated / 114 distinct / depth 11, no invariant violation

# 2. architecture, model side
python3 $REPO/scripts/analyze_architecture.py \
  specs/program_model/Pipeline.tla specs/program_model/Pipeline.cfg \
  --components specs/program_model/architecture_components.yaml

# 3. architecture, reflexion (ANSWER KEY 1)
python3 $REPO/scripts/architecture_reflexion.py \
  specs/program_model/Pipeline.tla specs/program_model/Pipeline.cfg \
  --components specs/program_model/architecture_components.yaml \
  --code pipeline --map specs/program_model/architecture_map.yaml

# 4. typed port contracts (needed by the effect port)
python3 $REPO/scripts/generate_python.py \
  specs/program_model/spec_manifest.yaml --out generated

# 5. the corpus
PYTHONPATH=$PWD python3 $REPO/scripts/generate_cases_from_tlc_dump.py \
  specs/program_model/Pipeline.tla specs/program_model/Pipeline.cfg \
  --out /tmp/ev01gen --package pipeline_cases --view internal \
  --actions-metadata specs/program_model/actions.yml \
  --state-projector specs.program_model.tlc_projection:project_visible_state \
  --output-projector specs.program_model.tlc_projection:project_adapter_output \
  --dedupe projected
#    -> 330 cases from 121 states

# 6. the two arms (CONTROL -- both must be green before any mutant is applied)
PYTHONPATH=<repo-root>:$PWD/generated python3 $REPO/scripts/run_generated_case_adapters.py \
  /tmp/ev01gen/spec-unit/pipeline_cases \
  --mapping specs/program_model/case_adapters_corpus_only.toml \
  --spec-dir specs/program_model --view internal --batch --import-root .
PYTHONPATH=<repo-root>:$PWD/generated python3 $REPO/scripts/run_generated_case_adapters.py \
  /tmp/ev01gen/spec-unit/pipeline_cases \
  --mapping specs/program_model/case_adapters.toml \
  --spec-dir specs/program_model --view internal --batch --import-root .

# 7. the case modules -- generated FROM specs/case_modules/, in place.
#    EV-01 had to copy them beside Pipeline.tla to generate at all; RP-03 fixed
#    the module search path, so `cp`/`rm` are gone and the checked-in modules
#    are reproducible where they live. Sibling directories of the .tla that hold
#    .tla files are searched automatically, which is how Pipeline is found; use
#    --module-path <dir> if the view lives somewhere else.
PYTHONPATH=$PWD python3 $REPO/scripts/generate_cases_from_tlc_dump.py \
  specs/case_modules/Scenario_DeliveryPath.tla specs/case_modules/Scenario_DeliveryPath.cfg \
  --out /tmp/ev01cm --package Scenario_DeliveryPath_cases --view internal \
  --actions-metadata specs/program_model/actions.yml \
  --state-projector specs.program_model.tlc_projection:project_visible_state \
  --output-projector specs.program_model.tlc_projection:project_adapter_output \
  --dedupe projected
#    -> 50 cases from 25 states  (same corpus the copy-and-delete run produced)
#   ... and the same command for Scenario_RecordAfterDelivery -> 6 cases from 8 states

python3 $REPO/scripts/case_modules.py validate  --manifest specs/program_model/spec_manifest.yaml
python3 $REPO/scripts/case_modules.py coverage  --manifest specs/program_model/spec_manifest.yaml \
  --actions-metadata specs/program_model/actions.yml --view internal \
  --corpus /tmp/ev01cm/spec-unit/Scenario_DeliveryPath_cases \
  --corpus /tmp/ev01cm/spec-unit/Scenario_RecordAfterDelivery_cases \
  --corpus /tmp/ev01gen/spec-unit/pipeline_cases

# 8. behavior (byte-identical file in both twins)
python3 -m pytest tests -q
```

The case modules are kept in `specs/case_modules/` and generate from there, in
place — the accepted baseline keeps none beside the view. The `spec_manifest.yaml`
that declares them is the *view's*, found along the same module search path.
`references/case_modules.md`, "Worked example: an internal-only project", runs
this fixture end to end with commands that need no editing.

## Layout

```
pipeline/                  the production tree -- the reflexion --code root
  ingest/{inbox,queue}.py      inbox, accepted, queue
  dispatch/{delivery,failures}.py  delivered, failed
  ledger/journal.py            ledger, and the LedgerStorePort effect
specs/program_model/       model, manifest, partition, map, adapters, providers
specs/case_modules/        the two authored aspects
tests/                     composition root + the behavioral suite
generated/                 typed port contracts (committed: the providers need them)
evidence/                  every output EV-01 kept
seeded_faults.toml         the fault catalog
```
