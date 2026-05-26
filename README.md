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

## Regenerate Examples

Manifest-driven fake/spec-double artifacts:

```bash
python3 scripts/generate_python.py examples/workspace/spec_manifest.yaml --out examples/workspace/generated
```

TLC-derived whole-program transition cases:

```bash
python3 scripts/generate_cases_from_tlc_dump.py examples/workspace/Workspace.tla examples/workspace/MC.cfg --out examples/workspace/generated --package workspace_cases
```

Adapter mapping validation:

```bash
python3 scripts/run_generated_case_adapters.py examples/workspace/generated/workspace_cases --mapping examples/workspace/case_adapters.toml --import-root examples/workspace --label Create --validate-only
```

## Repository Shape

- `scripts/`: scaffold, generation, TLC-case, adapter-runner, and workflow-closeout CLIs.
- `spec_double_compiler/`: importable runtime used by generated case runners.
- `templates/`: Jinja templates for generated Python/TLA artifacts.
- `examples/`: checked-in examples and generated artifacts.
- `references/`: user-facing skill references.
- `tests/`: unit tests for parsers, generators, runners, and workflow scripts.
- `tickets/`: small roadmap/history notes for this skill implementation.
