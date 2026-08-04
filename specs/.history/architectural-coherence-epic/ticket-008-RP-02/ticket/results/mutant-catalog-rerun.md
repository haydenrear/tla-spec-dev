# RP-02 -- the 12-mutant catalog, re-run before and after

## What was re-run, and the one honesty caveat about it

`examples/validation/runs/ex4-run3/` records a **12-mutant catalog** the blind
agent built and scored, but keeps only the **class table**, not the diffs. That
omission is EV-02's own protocol finding (`EV-02-PROTO-02`: "a blind run's
mutant catalog must be an artifact"). So the catalog re-run here is a
**RECONSTRUCTION** from the published class assignment, kept at
`harness/mutants.toml`, and it is scored only against the published *per-class*
counts. Any per-mutant number below is this reconstruction's.

The reconstruction reproduces the published class table on every class that
matters to this ticket:

| class | published (ex4-run3, view corpus) | reconstruction, ARM A | reconstruction, ARM B |
|---|---|---|---|
| guard relaxation (M1-M3) | **0 killed** | **0 killed** | **0 killed** |
| wrong write (M5-M8, M10) | 5 killed | 4 killed (M10 needs the port) | **5 killed** |
| ordering (M9, M11, M12) | 0 killed | 0 killed | 0 killed |
| equivalent (M4) | n/a | survives, correctly | survives, correctly |

## The measurement this ticket exists for

Both configurations were run in full. Nothing is inferred.

* **BEFORE** = corpus generated at epic tip `506e0e0` (`params={'i': UNCHECKED}`
  on all 330 cases) + the adapter that diffed `case.after` for its argument.
* **AFTER** = corpus generated with RP-02's `set-membership` recovery
  (`params={'i': 'i1'}` / `'i2'`, 330 of 330) + the adapter that reads the
  argument off the case and never touches `case.after`.

Control green in every configuration before any mutant (`arm_a`, `arm_b`,
`pytest`), all 330 cases, exit 0.

| id | class | ARM A before | ARM A after | ARM B before | ARM B after | pytest after |
|---|---|---|---|---|---|---|
| M1 | guard relaxation | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED |
| M2 | guard relaxation | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED |
| M3 | guard relaxation | SURVIVED | SURVIVED | SURVIVED | SURVIVED | KILLED |
| M4 | equivalent | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED |
| M5 | wrong write | KILLED | KILLED | KILLED | KILLED | KILLED |
| M6 | wrong write | KILLED | KILLED | KILLED | KILLED | KILLED |
| M7 | wrong write | KILLED | KILLED | KILLED | KILLED | SURVIVED |
| M8 | wrong write | KILLED | KILLED | KILLED | KILLED | KILLED |
| M9 | ordering | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED |
| M10 | wrong write, durable | SURVIVED | SURVIVED | KILLED | KILLED | SURVIVED |
| M11 | ordering | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED |
| M12 | ordering | SURVIVED | SURVIVED | SURVIVED | SURVIVED | SURVIVED |

**Not one cell changed.** Recovering every parameter killed nothing that was
not already killed, and lost nothing that was.

## THE HONEST NEGATIVE: guard relaxation is still 0 of 3, and here is why

Not an opinion -- a count over the corpus (`harness/corpus_shape.py`):

```
cases: 330
expected output statuses: {'applied': 330}

action      cases  arg ENABLED  arg REJECTED
Accept         22           22             0
Deliver        66           66             0
Enqueue       110          110             0
Fail           88           88             0
Record         44           44             0
TOTAL         330          330             0

argument/before-state pairs the model would REFUSE that a corpus COULD have
emitted: 220 (over 330 cases x 2 items)
emitted by the generator: 0 -- a state graph has no edge for a refused argument.
```

**Every one of the 330 recovered arguments is an argument the guard ACCEPTS.**
A relaxed guard is a guard that says yes where the model says no; the corpus
never asks it that question, so it can never hear the wrong answer. 220 such
questions exist in this state space and the generator emits none of them,
because a TLC state graph has no edge for a transition that did not fire.

EV-02 named two compounding causes of the unkillable guard class:

1. **structural** -- a generated corpus replays only ENABLED edges, so it
   contains no rejected inputs;
2. **oracle leakage** -- the adapter took the argument from `case.after`, so it
   only ever called with the argument that was going to succeed.

RP-02 removes cause 2 and the class stays at 0 of 3. **The whole of the
remaining failure is attributable to cause 1**, which is what the split above
was for. Cause 2 was real and is fixed; it was never what made guard relaxation
unkillable.

## A second honest negative: the "wrong item" limitation was overstated

`seeded_faults.toml` states that a fault whose only symptom is *acting on the
wrong item* is a class this instrument cannot measure, and declines to seed one
"because seeding one would produce a survivor that says nothing about the
corpus". So RP-02 seeded two (`harness/wrong_item_probe.py`): an `accept()` and
a `record()` that ignore the item they were handed and pick one out of ambient
state instead.

| mutant | BEFORE (UNCHECKED corpus + oracle-diffing adapter) | AFTER (recovered corpus + case-argument adapter) |
|---|---|---|
| W1 accept acts on the wrong item | **KILLED** | **KILLED** |
| W2 record acts on the wrong item | **KILLED** | **KILLED** |

It was killable all along. The old adapter was handed the *correct* argument by
the diff and passed it in, so a program that then ignored it diverged in the
projected after-state and died. The leak's real cost was never kill power on
this fixture -- it was that the argument was not in the artifact, nothing
audited it, the claim "the corpus tests arguments" was unfalsifiable, and the
MF-028 vacuity trap (derive from `case.after`, then check against `case.after`)
was live in a file nobody re-read. Those are the things RP-02 fixes.

**This contradicts a written claim in `seeded_faults.toml` and
`README.md`.** Both are amended in place with the measurement, and neither
answer-key row is altered.

## Reproduce

```bash
export PATH="$HOME/.skill-manager/bin/cli:$PATH"
cd examples/validation/ex4_pipeline_coherent
PYTHONPATH=$PWD python3 ../../../scripts/generate_cases_from_tlc_dump.py \
  specs/program_model/Pipeline.tla specs/program_model/Pipeline.cfg \
  --out <OUT> --package pipeline_cases --view internal \
  --actions-metadata specs/program_model/actions.yml \
  --state-projector specs.program_model.tlc_projection:project_visible_state \
  --output-projector specs.program_model.tlc_projection:project_adapter_output \
  --dedupe projected
# then, with <OUT>/spec-unit/pipeline_cases as the corpus:
python3 specs/tickets/RP-02/results/harness/run_mutants.py         # AFTER  matrix
python3 specs/tickets/RP-02/results/harness/run_mutants_before.py  # BEFORE matrix
python3 specs/tickets/RP-02/results/harness/wrong_item_probe.py    # W1/W2
python3 specs/tickets/RP-02/results/harness/corpus_shape.py        # rejected-input count
```

The harness scripts carry absolute paths from the worktree they ran in; retarget
`REPO`/`SCRATCH` at the top of each before rerunning elsewhere. Every mutant is
applied by verbatim find/replace with a `finally` restore, and `run_mutants.py`
ends by printing `git status` on `pipeline/` -- clean on this run.

Machine-readable: `mutant-matrix-before.json`, `mutant-matrix-after.json`,
`wrong-item-probe.json`.
