# Spec Double Compiler

Development repository for the `spec-double-compiler` skill.

User-facing workflow guidance lives in:

- `SKILL.md`
- `references/typical_workflow.md`
- `references/generation_modes.md`
- `references/streaming_case_protocol.md`
- `references/runtime_requirements.md`
- `references/codegen_contract.md`
- `references/conformance_testing.md`
- `references/testgraph_adapters.md`
- `references/edge-cases.md`
- `references/tla_profile.md`
- `references/spec_evolution.md`
- `references/workflows.md`

## Install Locally

```bash
skill-manager install file://$(pwd) --dry-run
skill-manager install file://$(pwd)
```

The skill declares CLI dependencies for `jinja2`, `pytest`, and a
`skill-script` installed `tlc2` wrapper. The `tlc2` wrapper requires Java.

## Develop

Run focused checks while editing:

```bash
PYTHONPYCACHEPREFIX=/tmp/spec-double-pyc python3 -m py_compile scripts/*.py tests/*.py spec_double_compiler/*.py
uv run --with pytest --with jsonschema -m pytest tests
uv run examples/distributed_history/tests/test_ecommerce_backend.py
uv run examples/distributed_history/specs/program_model/tests/test_ecommerce_adapters.py
```

The distributed ecommerce example tests include PEP 723 uv script headers, so
`uv run <test-file>` retrieves pytest even when the ambient interpreter does
not have it installed.

For production repositories that use the desired/current migration loop,
scaffold the workflow directories first:

```bash
python3 scripts/tla_spec_dev.py --spec-root specs scaffold project --name ProjectName
python3 scripts/tla_spec_dev.py --spec-root specs scaffold workflow TICKET-123 "Ticket title"
python3 scripts/tla_spec_dev.py --spec-root specs open ticket TICKET-123
python3 scripts/tla_spec_dev.py --spec-root specs run spec-unit-tests --ticket TICKET-123
```

The installed wrapper exposes the same workflow as `tla-spec-dev`; the
repository path uses `python3 scripts/tla_spec_dev.py` so local development does
not depend on a prior skill install. Use the same `--spec-root` for every
project, workflow, ticket, run, and close command.

## Regenerate Examples

The active checked-in example is `examples/distributed_history`. Regenerate
its TLC-derived internal and external case packages into an ignored build
directory:

```bash
uv run examples/distributed_history/scripts/regenerate_tlc_cases.py \
  --out test_graph/build/generated/manual
```

Run the generated internal/spec-unit cases:

```bash
python3 scripts/run_generated_case_adapters.py \
  examples/distributed_history/test_graph/build/generated/manual/spec-unit/ecommerce_internal_cases \
  --mapping examples/distributed_history/specs/program_model/case_adapters.toml \
  --view internal \
  --batch \
  --import-root examples/distributed_history
```

View-aware case generation writes explicit internal and external outputs:

```bash
python3 scripts/generate_cases_from_tlc_dump.py path/to/Internal.tla path/to/Internal.cfg --out generated --package internal_cases --view internal --actions-metadata model/actions.yml
python3 scripts/generate_cases_from_tlc_dump.py path/to/External.tla path/to/External.cfg --out generated --package external_cases --view external --actions-metadata model/actions.yml
python3 scripts/export_testgraph_cases.py generated/testgraph/external_cases --out generated/testgraph/traces
```

For large graphs and cross-language adapters, emit the bounded JSONL protocol
instead of a runtime `cases.py`:

```bash
python3 scripts/generate_cases_from_tlc_dump.py \
  path/to/Internal.tla path/to/Internal.cfg \
  --out generated \
  --package internal_cases \
  --format streaming-jsonl \
  --max-cases 10000 \
  --max-output-bytes 134217728 \
  --max-rss-mib 512 \
  --max-seconds 120 \
  --per-case-timeout-ms 30000 \
  --seed model-seed
```

The output is `case-manifest.json` plus `cases.jsonl`. A hard resource breach
removes the partial case stream, writes a typed incomplete manifest, and exits
nonzero. See `references/streaming_case_protocol.md`.

External adapter bindings may include `kind` to batch cases that need the same
external harness setup and cleanup. Batch adapters can define optional
`setup_all(ctx)`, `teardown_all(ctx)`, `setup(ctx)`, and `teardown(ctx)` hooks.
Use these hooks for integration-state preparation such as clearing database
rows, committing Kafka offsets, preparing a CLI workspace, or removing
per-trace test fixtures.

For external assertions, configure `projector = "module:Object"` to retrieve
the actual deployed state. By default, the runner compares that actual state to
the generated TLA case's `after` state. Use `expected_projection` when only a
projection of the TLA state is externally observable, and use `assertion` only
for custom comparison logic.

Relative case outputs such as `--out cases` are resolved under the spec
directory. A command run from the repository root and the same command run from
the spec directory should produce the same spec-local artifact layout.

Adapter mapping validation:

```bash
python3 scripts/run_generated_case_adapters.py \
  examples/distributed_history/test_graph/build/generated/manual/testgraph/ecommerce_external_cases \
  --mapping examples/distributed_history/specs/program_model/testgraph_bindings.yml \
  --view external \
  --batch \
  --validate-only \
  --import-root examples/distributed_history
```

For larger case sets, use batch mode:

```bash
python3 scripts/run_generated_case_adapters.py path/to/generated_cases --mapping path/to/case_adapters.toml --batch --validate-capabilities
```

## Spec Evolution History

Use append-only close records to keep active context small without losing
history.
After each ticket is marked closed in
`specs/desired_program_model/ticket_plan.yaml`:

```bash
python3 scripts/tla_spec_dev.py --spec-root specs open ticket TICKET-123
python3 scripts/tla_spec_dev.py --spec-root specs close ticket TICKET-123 \
  --summary "Kept generated cases spec-local" \
  --result specs/results/tlc.txt
```

`open ticket` creates `specs/tickets/TICKET-123/current` and `desired` for
parallel ticket work. `close ticket` moves that ticket directory into
history, validates ticket `current/ == desired/`, replaces project
`specs/current` with ticket `desired/`, and merges ticket-local Test Graph
artifacts back into project specs.

The parent repository also has a Test Graph that exercises this workflow in a
disposable git repository under the graph build directory:

```bash
/Users/hayde/.skill-manager/skills/test-graph/scripts/discover.py specWorkflow
/Users/hayde/.skill-manager/skills/test-graph/scripts/run.py specWorkflow
```

At the end of a desired/current workflow:

```bash
python3 scripts/close_tickets.py --repo-root . --summary "Promoted desired/current into program_model"
```

These commands write under `specs/.history/<workflow-name>/`, refuse to
overwrite an existing close entry, and print a recommended git commit command
for the history directory.

The lower-level `start_ticket.py`, `close-ticket.py`, and `close_tickets.py`
scripts remain implementation details for the CLI and for workflow closeout.
New onboarding documentation should lead with `tla-spec-dev`.

## Repository Shape

- `scripts/`: scaffold, generation, TLC-case, adapter-runner, history, and workflow-closeout CLIs.
- `spec_double_compiler/`: importable runtime used by generated case runners.
- `templates/`: Jinja templates for generated Python/TLA artifacts.
- `examples/`: checked-in examples and generated artifacts.
- `references/`: user-facing skill references.
- `test_graph/`: parent repository Test Graph, including `specWorkflow` for the ticket workflow CLI.
- `tests/`: unit tests for parsers, generators, runners, and workflow scripts.
- `tickets/`: small roadmap/history notes for this skill implementation.
