# Spec Double Compiler

**The spec should generate the mock.**

Spec Double Compiler is a skill-manager skill for creating and maintaining
Python spec doubles from a constrained, annotated TLA+ program specification.
For production repositories, the intended pattern is one evolving program spec
whose generated cases can be sliced by label for local adapter tests.

TLA+ defines the program truth. Python makes selected slices of that truth
executable in tests. Production adapters conform to the generated Python
boundary.

## What This Provides

- A constrained TLA+ profile for practical state-machine specs.
- Guidance for maintaining one evolving whole-program spec instead of many
  disconnected feature specs.
- A ticket workflow scaffold for ordinary development tickets that need
  desired/current/program-model discipline.
- Templates for TLA+ modules, TLC configs, manifests, and Python package
  artifacts.
- Scripts for scaffolding specs, checking manifest references, generating
  Python files, generating generated package docs, and running TLC.
- A fully worked `Workspace` example with generated Python artifacts and
  tests.
- A partial `Subscription` example showing lifecycle-state modeling.
- Guidance for conformance tests, refinement mappings, maintenance, and
  AI retrieval.

## Skill-Manager Install

From the repository root:

```bash
skill-manager install file://$(pwd) --dry-run
skill-manager install file://$(pwd)
```

The skill declares CLI dependencies for `jinja2`, `pytest`, and a
`skill-script` installed `tlc2` wrapper. The `tlc2` wrapper downloads
the TLA+ tools jar from the TLA+ GitHub releases at install time and
requires a local Java runtime.

## Quick Start

```bash
python scripts/scaffold_spec.py workspace
python scripts/new_ticket_workflow.py TICKET-123 "Ticket title" --repo-root path/to/repo
python scripts/run_tlc.sh examples/workspace/Workspace.tla examples/workspace/MC.cfg
python scripts/generate_python.py examples/workspace/spec_manifest.yaml --out examples/workspace/generated
python -m pytest examples/workspace/tests
```

`new_ticket_workflow.py` scaffolds:

- `specs/current`: executable model of what has landed for the active ticket.
- `specs/desired_program_model`: target model plus ticket plan.
- `specs/desired_program_model/ticket_plan.yaml`: opinionated ticket breakdown
  with current-model increments, adapter expectations, tests, graph gates, and
  evidence slots.
- `status` sections in `spec_manifest.yaml` files so agents and humans can see
  which ticket is active, what is done, and what remains.

This is not a migration-only workflow. Use it for any behavior ticket where
formal state, adapters, and validation evidence should guide implementation.

To derive whole-program transition cases from TLC and validate that every
action label is mapped to an adapter:

```bash
python scripts/generate_cases_from_tlc_dump.py examples/workspace/Workspace.tla examples/workspace/MC.cfg --out examples/workspace/generated --package workspace_cases
python scripts/run_generated_case_adapters.py examples/workspace/generated/workspace_cases --mapping examples/workspace/case_adapters.toml --import-root examples/workspace --label Create --validate-only
```

For larger case sets, use batch mode:

```bash
python scripts/run_generated_case_adapters.py path/to/generated_cases --mapping path/to/case_adapters.toml --batch --validate-capabilities
```

Mapping entries may include `output_projection = "module:function"` for
semantic output checks. `generate_cases_from_tlc_dump.py --labeler
module:function` can add repository-specific labels while keeping the skill
generator domain-neutral.

If `pytest` is not installed, the example tests can also be run directly:

```bash
python examples/workspace/tests/test_workspace_spec_double.py
python examples/workspace/tests/test_workspace_adapter_conformance.py
python examples/workspace/tests/test_workspace_case_adapter_mapping.py
```

## File Tree

```text
SKILL.md
README.md
skill-manager.toml
templates/
  tla/
    MODULE.tla.j2
    MC.cfg.j2
    annotations.md
  python/
    pyproject.toml.j2
    package_init.py.j2
    types.py.j2
    ports.py.j2
    fake.py.j2
    validators.py.j2
    strategies.py.j2
    traces.py.j2
    contract_tests.py.j2
    docs.md.j2
scripts/
  scaffold_spec.py
  new_ticket_workflow.py
  extract_spec_manifest.py
  generate_python.py
  generate_docs.py
  run_tlc.sh
examples/
  workspace/
    Workspace.tla
    MC.cfg
    spec_manifest.yaml
    generated/
      workspace_cases/
        __init__.py
        cases.py
        doubles.py
        types.py
        validators.py
        docs.md
      workspace_spec/
        __init__.py
        types.py
        ports.py
        fake.py
        validators.py
        strategies.py
        traces.py
        contract_tests.py
        docs.md
    case_adapters.py
    case_adapters.toml
    tests/
      test_workspace_spec_double.py
      test_workspace_adapter_conformance.py
  subscription/
    Subscription.tla
    MC.cfg
    spec_manifest.yaml
references/
  tla_profile.md
  codegen_contract.md
  conformance_testing.md
  ai_retrieval.md
  maintenance.md
```

## Generation Boundary

The generator is manifest-driven in v0. It checks that referenced TLA+
module and action names exist, then emits deterministic Python artifacts
from `spec_manifest.yaml`. It intentionally does not parse all TLA+.

Use extension modules for production-specific code:

```text
workspace_spec_ext/
  adapter_mapping.py
  custom_strategies.py
  production_factories.py
```

Generated spec doubles are test dependencies, not production
dependencies.
