# Generation Modes

Spec Double Compiler has two related generation paths. Keep them distinct.

## Manifest-Driven Spec Doubles

Use `scripts/generate_python.py` when a reviewed `spec_manifest.yaml` defines
the Python API shape:

```bash
python scripts/generate_python.py path/to/spec_manifest.yaml --out path/to/generated
```

This mode generates:

- Python dataclasses for states, commands, results, and events.
- Protocols for ports.
- A deterministic fake/spec double from explicit manifest templates.
- Validators, strategies, traces, contract tests, and generated docs.

This is best when the boundary API is known and the manifest is the reviewed
bridge from TLA+ names to Python names.

## TLC State-Graph Cases

Use `scripts/generate_cases_from_tlc_dump.py` when TLC's reachable state graph
is the case source of truth:

```bash
python scripts/generate_cases_from_tlc_dump.py path/to/Model.tla path/to/MC.cfg --out path/to/generated --package model_cases
```

This mode generates:

- One `StateGraphCase` per action-labeled TLC edge.
- Generic before/input/output/after case descriptors.
- A scripted transition double that accepts exactly the generated case input.
- Validators for structural replay.

Repository-local adapters then map real production boundaries to these generic
case descriptors through `case_adapters.toml` and
`scripts/run_generated_case_adapters.py`.

For large graphs or cross-language adapters, use the resource-bounded
streaming interchange instead of a generated `cases.py`:

```bash
python scripts/generate_cases_from_tlc_dump.py \
  path/to/Model.tla path/to/MC.cfg \
  --out path/to/generated \
  --package model_cases \
  --format streaming-jsonl \
  --max-cases 10000 \
  --max-output-bytes 134217728 \
  --max-rss-mib 512 \
  --max-seconds 120 \
  --seed model-seed
```

This emits `case-manifest.json` plus `cases.jsonl`, performs deterministic
stable-hash selection stratified by action/outcome, and writes a typed
incomplete manifest with a nonzero exit when a hard resource budget is
exceeded. It never emits runtime `cases.py`. Read
`references/streaming_case_protocol.md` for the versioned record fields,
canonical JSON rules, digest accounting, and failure semantics.

Every TLC run used to produce this state graph has a hard two-minute budget.
Wrap the model-check command in an external 120-second timeout and stop it when
the budget expires. A timeout means the diagram is not a viable case-generation
abstraction. First inspect domain cardinalities, variable combinations, action
branching, interleavings, symmetry, and TLC progress output to identify what
multiplies the state count. Distinguish compressible modeling detail from
essential program complexity. Then introduce another diagram/refinement with
smaller bounded domains, less irrelevant state, or separated independent
lifecycles. Do not increase the timeout or wait for the same state space. When
essential complexity remains, give the user concrete options for lowering
program complexity, with the semantic and coverage tradeoff of each option,
before choosing what to omit.

## Relationship To Program Workflow

`program_model`, `current`, and `desired_program_model` are workflow roles, not
generation modes.

- `program_model` is the accepted baseline.
- `current` is the whole-program model implemented right now during active
  ticket work.
- `desired_program_model` is the target model plus ticket plan.

Either generation mode can be used from the appropriate workflow directory, but
for whole-program behavior changes the TLC state-graph case path is usually the
better fit because it keeps cases tied directly to the reachable model.
