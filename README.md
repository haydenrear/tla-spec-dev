# Spec Double Compiler

Development repository for the `spec-double-compiler` skill.

User-facing workflow guidance lives in:

- `SKILL.md`
- `references/typical_workflow.md`
- `references/generation_modes.md`
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
python3 -m py_compile scripts/*.py tests/*.py spec_double_compiler/*.py
uv run --with pytest -m pytest tests
uv run examples/distributed_history/tests/test_ecommerce_backend.py
uv run examples/distributed_history/specs/program_model/tests/test_ecommerce_adapters.py
```

The distributed ecommerce example tests include PEP 723 uv script headers, so
`uv run <test-file>` retrieves pytest even when the ambient interpreter does
not have it installed.

For production repositories that use the desired/current migration loop,
scaffold the workflow directories first:

```bash
python3 scripts/scaffold_spec_workflow.py --root .
```

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
python3 scripts/start_ticket.py TICKET-123
python3 scripts/close-ticket.py TICKET-123 --summary "Kept generated cases spec-local" --result specs/results/tlc.txt
```

`start_ticket.py` creates `specs/tickets/TICKET-123/current` and `desired` for
parallel ticket work. `close-ticket.py` moves that ticket directory into
history and promotes ticket `desired/` to project `specs/current`.

At the end of a desired/current workflow:

```bash
python3 scripts/close_tickets.py --repo-root . --summary "Promoted desired/current into program_model"
```

These commands write under `specs/.history/<workflow-name>/`, refuse to
overwrite an existing close entry, and print a recommended git commit command
for the history directory.

## Repository Shape

- `scripts/`: scaffold, generation, TLC-case, adapter-runner, history, and workflow-closeout CLIs.
- `spec_double_compiler/`: importable runtime used by generated case runners.
- `templates/`: Jinja templates for generated Python/TLA artifacts.
- `examples/`: checked-in examples and generated artifacts.
- `references/`: user-facing skill references.
- `tests/`: unit tests for parsers, generators, runners, and workflow scripts.
- `tickets/`: small roadmap/history notes for this skill implementation.
