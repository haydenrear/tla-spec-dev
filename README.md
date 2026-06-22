# Spec Double Compiler

Development repository for the `spec-double-compiler` skill.

User-facing workflow guidance lives in:

- `SKILL.md`
- `references/typical_workflow.md`
- `references/generation_modes.md`
- `references/runtime_requirements.md`
- `references/codegen_contract.md`
- `references/conformance_testing.md`
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
python3 -m pytest tests
```

If `pytest` is not installed in the active environment, use the
`skill-manager.toml` dependency declaration or run the scripts directly for
smoke checks.

For production repositories that use the desired/current migration loop,
scaffold the workflow directories first:

```bash
python3 scripts/scaffold_spec_workflow.py --root .
```

## Regenerate Examples

Manifest-driven fake/spec-double artifacts:

```bash
python3 scripts/generate_python.py examples/workspace/spec_manifest.yaml --out examples/workspace/generated
```

TLC-derived whole-program transition cases:

```bash
python3 scripts/generate_cases_from_tlc_dump.py examples/workspace/Workspace.tla examples/workspace/MC.cfg --out examples/workspace/generated --package workspace_cases
```

View-aware case generation writes explicit internal and external outputs:

```bash
python3 scripts/generate_cases_from_tlc_dump.py path/to/Internal.tla path/to/Internal.cfg --out generated --package internal_cases --view internal --actions-metadata model/actions.yml
python3 scripts/generate_cases_from_tlc_dump.py path/to/External.tla path/to/External.cfg --out generated --package external_cases --view external --actions-metadata model/actions.yml
python3 scripts/export_testgraph_cases.py generated/testgraph/external_cases --out generated/testgraph/traces
```

External adapter bindings may include `kind` to batch cases that need the same
cluster setup and cleanup. Batch adapters can define optional
`setup_all(ctx)`, `teardown_all(ctx)`, `setup(ctx)`, and `teardown(ctx)` hooks.
Use these hooks for deployed-state preparation such as clearing database rows,
committing Kafka offsets, or removing per-trace test fixtures.

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
python3 scripts/run_generated_case_adapters.py examples/workspace/generated/workspace_cases --mapping examples/workspace/case_adapters.toml --import-root examples/workspace --label Create --validate-only
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
python3 scripts/close-ticket.py TICKET-123 --summary "Kept generated cases spec-local" --result specs/results/tlc.txt
```

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
