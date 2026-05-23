#!/usr/bin/env python3
"""Scaffold a model-backed ticket workflow in a repository.

The workflow is intentionally general. It is for any ticket or behavior change
where the repository should keep a formal desired state, executable current
state, adapters, and validation evidence in sync.
"""

from __future__ import annotations

import argparse
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]


def _load_manifest(path: Path) -> dict[str, Any]:
    import sys

    skill_root = str(SKILL_ROOT)
    if skill_root not in sys.path:
        sys.path.insert(0, skill_root)
    from scripts.extract_spec_manifest import load_manifest

    if not path.exists():
        return {}
    return load_manifest(path)


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return normalized or "ticket"


def _title(value: str) -> str:
    return " ".join(part.capitalize() for part in re.split(r"[-_\s]+", value) if part)


def _module_name(value: str) -> str:
    candidate = "".join(part.capitalize() for part in re.split(r"[^a-zA-Z0-9]+", value) if part)
    if not candidate:
        return "ProgramModel"
    if candidate[0].isdigit():
        return f"Program{candidate}"
    return candidate


@dataclass(frozen=True)
class Baseline:
    module: str
    package: str
    tla_path: Path | None
    cfg_path: Path | None
    manifest_path: Path | None


def discover_baseline(repo_root: Path, fallback_module: str) -> Baseline:
    program_dir = repo_root / "specs" / "program_model"
    manifest_path = program_dir / "spec_manifest.yaml"
    manifest = _load_manifest(manifest_path)
    module = str(manifest.get("module") or fallback_module)
    package = str(manifest.get("package") or f"{_slug(module).replace('-', '_')}_cases")
    tla_path = program_dir / f"{module}.tla"
    if not tla_path.exists():
        candidates = sorted(program_dir.glob("*.tla"))
        tla_path = candidates[0] if candidates else None
        if tla_path is not None:
            match = re.search(r"(?m)^\s*-+\s*MODULE\s+([A-Za-z][A-Za-z0-9_]*)\s*-+", tla_path.read_text())
            if match:
                module = match.group(1)
    cfg_path = program_dir / "MC.cfg"
    return Baseline(
        module=module,
        package=package,
        tla_path=tla_path if tla_path and tla_path.exists() else None,
        cfg_path=cfg_path if cfg_path.exists() else None,
        manifest_path=manifest_path if manifest_path.exists() else None,
    )


def write_file(path: Path, content: str, *, force: bool, dry_run: bool) -> bool:
    if path.exists() and not force:
        return False
    if dry_run:
        print(f"would write {path}")
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"wrote {path}")
    return True


def copy_file(src: Path | None, dst: Path, fallback: str, *, force: bool, dry_run: bool) -> bool:
    if dst.exists() and not force:
        return False
    if dry_run:
        action = f"copy {src}" if src else "write fallback"
        print(f"would {action} -> {dst}")
        return True
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src is not None:
        shutil.copyfile(src, dst)
        print(f"copied {src} -> {dst}")
    else:
        dst.write_text(fallback, encoding="utf-8")
        print(f"wrote {dst}")
    return True


def minimal_tla(module: str) -> str:
    return f"""----------------------------- MODULE {module} -----------------------------
EXTENDS Naturals, FiniteSets, Sequences, TLC

CONSTANTS
  Tickets,
  NoReason

VARIABLES
  accepted_tickets,
  result

vars == << accepted_tickets, result >>

Init ==
  /\\ accepted_tickets = {{}}
  /\\ result = [accepted |-> TRUE, reason |-> NoReason]

\\* @command AcceptTicket
\\* @result AcceptTicketResult
AcceptTicket(t) ==
  /\\ accepted_tickets' = accepted_tickets \\cup {{t}}
  /\\ result' = [accepted |-> TRUE, reason |-> NoReason]

Next ==
  \\E t \\in Tickets:
    AcceptTicket(t)

\\* @invariant AcceptedTicketsAreKnown
AcceptedTicketsAreKnown ==
  accepted_tickets \\subseteq Tickets

Spec ==
  Init /\\ [][Next]_vars

=============================================================================
"""


def minimal_cfg() -> str:
    return """SPECIFICATION Spec

CONSTANTS
  Tickets = {t1}
  NoReason = NoReason

INVARIANTS
  AcceptedTicketsAreKnown
"""


def current_readme(ticket_id: str, title: str, baseline: Baseline) -> str:
    return f"""# Current Program Model

This directory is the executable model of what the repository implements right
now for the active ticket workflow.

Active ticket: `{ticket_id}` - {title}

Baseline:

- Program model manifest: `../program_model/spec_manifest.yaml`
- Program model TLA module: `../program_model/{baseline.module}.tla`

Workflow:

1. Keep this model equivalent to `specs/program_model` before implementation.
2. After each ticket slice lands in production code, update this directory with
   the implemented state, actions, invariants, adapter mappings, and tests.
3. Run TLC and current-model adapter/unit tests before adding broader
   integration or graph coverage.
4. Record validation evidence in `spec_manifest.yaml` and keep
   `../desired_program_model/ticket_plan.yaml` synchronized.
"""


def desired_readme(ticket_id: str, title: str, baseline: Baseline) -> str:
    return f"""# Desired Program Model

This directory describes the planned destination for the active ticket
workflow. It is both a formal model target and a structured implementation
plan.

Initial ticket: `{ticket_id}` - {title}

Baseline:

- Program model manifest: `../program_model/spec_manifest.yaml`
- Program model TLA module: `../program_model/{baseline.module}.tla`

Files:

- `{baseline.module}.tla`: desired whole-program model target. Start from the
  accepted program model, then add the desired semantic state.
- `MC.cfg`: bounded TLC model for the desired target.
- `spec_manifest.yaml`: desired generated-case manifest plus workflow status.
- `ticket_plan.yaml`: ticket breakdown with dependencies, current-model
  increments, adapter expectations, validation commands, and evidence slots.
- `desired_state.yaml`: human-readable index of modeled boundaries and
  implementation status.
"""


def current_manifest(module: str, package: str, ticket_id: str, title: str) -> str:
    return f"""module: {module}
package: current_program_cases

status:
  workflow: ticket
  active_ticket: {ticket_id}
  active_ticket_title: "{title}"
  relation_to_program_model: starts_equivalent_then_advances_as_slices_land
  relation_to_desired_program_model: implemented_prefix_of_desired_ticket_plan
  updated: null
  current_slice:
    name: baseline
    status: scaffolded
    refines: []
    implemented_actions: []
    validation:
      unit: []
      tlc: []
      graph: []
      evidence: []
  next:
    - Fill in current state fields, actions, invariants, and adapters after the first production slice lands.
    - Run TLC and adapter/unit tests before adding graph execution coverage.

source_model:
  program_model_manifest: ../program_model/spec_manifest.yaml
  program_model_module: ../program_model/{module}.tla
  desired_ticket_plan: ../desired_program_model/ticket_plan.yaml

case_codegen:
  style: explicit_transition_cases
  generation_status: planned

state_fields: []
actions: []
ports: {{}}
adapters: case_adapters.toml
notes:
  package_from_program_model: {package}
"""


def desired_manifest(module: str, package: str, ticket_id: str, title: str) -> str:
    return f"""module: {module}
package: desired_program_cases

status:
  workflow: ticket
  initial_ticket: {ticket_id}
  initial_ticket_title: "{title}"
  ticket_plan: ticket_plan.yaml
  relation_to_program_model: desired_successor_of_accepted_program_model
  relation_to_current: target_state_for_specs_current_to_converge_to
  updated: null
  summary:
    desired_model_scaffolded: true
    ticket_plan_scaffolded: true
    current_model_scaffolded: true
    generated_cases: pending
    adapters: pending
  done: []
  pending:
    - Fill in desired state/actions/invariants for the ticket.
    - Break the work into tickets in ticket_plan.yaml.
    - Update specs/current as each ticket lands.
    - Promote converged desired/current model back into specs/program_model.

source_model:
  program_model_manifest: ../program_model/spec_manifest.yaml
  program_model_module: ../program_model/{module}.tla
  baseline_package: {package}

case_codegen:
  style: explicit_transition_cases
  generation_status: planned

state_fields: []
actions: []
ports: {{}}
notes:
  direction: >
    This manifest records the target whole-program model and the ticket workflow
    status. Keep ticket_plan.yaml synchronized whenever scope, order, validation,
    or acceptance criteria change.
"""


def ticket_plan(ticket_id: str, title: str, module: str) -> str:
    return f"""# This file is part of the desired program model.
# It is intentionally general: use it for any model-backed ticket workflow,
# not only migrations. Keep it synchronized with spec_manifest.yaml status.
version: 1
name: desired-ticket-workflow
updated: null
purpose: >
  Break the desired whole-program change into tickets that can be implemented,
  modeled in specs/current, unit-tested, and then validated with broader graph
  or integration checks.

planning_rules:
  current_model_rule: Update specs/current after each production slice lands.
  unit_validation_rule: Run current-model TLC and adapter/unit tests before adding graph execution.
  graph_rule: Add graph or integration nodes only after current-model validation passes.
  desired_sync_rule: Update this file and spec_manifest.yaml whenever scope, order, acceptance checks, or status changes.
  promotion_rule: When specs/current equals specs/desired_program_model, promote the converged model to specs/program_model.

status:
  workflow: ticket
  active_ticket: {ticket_id}
  active_ticket_title: "{title}"
  desired_module: {module}
  phase: planning

# Replace or extend these sections with project-specific domains. Service,
# process, queue, database, file, API, model, permission, or UI boundaries can
# all be listed here when they matter to correctness.
service_catalog:
  existing_boundaries: []
  desired_boundaries: []
  adapter_boundaries: []
  known_gaps: []

tickets:
  - id: {ticket_id}
    title: "{title}"
    status: next
    depends_on: []
    objective: >
      Describe the behavior change in program terms. Name the resource or
      state boundary that must become true, not only the implementation file.
    desired_actions:
      # Add TLA+ action names that will exist in specs/desired_program_model.
      - ReplaceWithDesiredAction
    implementation_scope:
      # Add production files, scripts, descriptors, infrastructure, or adapters
      # this ticket is allowed to touch.
      - Replace with implementation surfaces
    current_increment:
      model_state:
        # Add state fields that specs/current will gain after implementation.
        - replace_with_state_field
      model_actions:
        # Add actions that specs/current will gain after implementation.
        - ReplaceWithDesiredAction
      adapters:
        # Add adapter classes or commands that prove production conforms.
        - ReplaceWithAdapter
      unit_tests:
        # Add current-model tests that must pass before graph coverage.
        - pytest specs/current/tests
      graph_after_unit_pass:
        # Add graph/test nodes only after current-model tests pass.
        - replace.with.graph.node
    acceptance:
      commands:
        - python scripts/run_tlc_or_project_specific_check.py
      assertions:
        - The production slice refines to the current model.
        - The current model advances toward the desired model.
      evidence: []
"""


def desired_state(ticket_id: str, title: str, module: str) -> str:
    return f"""version: 1
name: desired-program-model
canonical_tla_module: {module}
canonical_tla_file: {module}.tla
bounded_model_config: MC.cfg
manifest: spec_manifest.yaml
ticket_plan: ticket_plan.yaml

relationship:
  extends_current_program_model: ../program_model/{module}.tla
  purpose: desired whole-program model for ticket workflow
  generation_status: planned

implementation_status:
  updated: null
  policy: specs/current is the executable state of landed work; this file summarizes the desired destination.
  active_ticket: {ticket_id}
  active_ticket_title: "{title}"
  summary:
    desired_model_scaffolded: true
    ticket_breakdown: scaffolded
    current_model: scaffolded
    generated_desired_cases: pending
    adapters: pending

modeled_boundary_status:
  ticket_plan:
    status: scaffolded
    artifact: ticket_plan.yaml
    next_ticket: {ticket_id}

program_domains: []
implementation_sources: {{}}
adapter_plan:
  desired_new_ports: []
guardrails: {{}}
"""


def case_adapters_toml() -> str:
    return """# Map generated current-model case labels to production adapters.
# Example:
# [adapters.ReplaceWithDesiredAction]
# adapter = "my_project.spec_adapters:ReplaceWithDesiredActionAdapter"
"""


def production_adapters_py() -> str:
    return '''"""Production adapters for current-model ticket workflow cases.

Add one small adapter per modeled boundary. Each adapter should materialize the
case pre-state, call the production boundary, observe production state, and
refine that observation back to the generated case shape.
"""

from __future__ import annotations


class ScaffoldedTicketAdapter:
    """Placeholder adapter documenting the expected shape."""

    def can_run(self, case):
        return False, "replace ScaffoldedTicketAdapter with a ticket-specific adapter"
'''


def current_test(ticket_id: str) -> str:
    return f'''from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_current_ticket_workflow_scaffold_points_to_desired_plan() -> None:
    manifest = ROOT / "specs/current/spec_manifest.yaml"
    plan = ROOT / "specs/desired_program_model/ticket_plan.yaml"

    assert manifest.exists()
    assert plan.exists()
    assert "{ticket_id}" in manifest.read_text(encoding="utf-8")
    assert "{ticket_id}" in plan.read_text(encoding="utf-8")
'''


def scaffold(repo_root: Path, ticket_id: str, title: str, force: bool, dry_run: bool) -> list[Path]:
    fallback_module = _module_name(repo_root.name)
    baseline = discover_baseline(repo_root, fallback_module)
    module = baseline.module
    package = baseline.package
    current_dir = repo_root / "specs" / "current"
    desired_dir = repo_root / "specs" / "desired_program_model"

    written: list[Path] = []

    files = [
        (current_dir / "README.md", current_readme(ticket_id, title, baseline)),
        (current_dir / "spec_manifest.yaml", current_manifest(module, package, ticket_id, title)),
        (current_dir / "case_adapters.toml", case_adapters_toml()),
        (current_dir / "production_adapters.py", production_adapters_py()),
        (current_dir / "tests" / "test_current_ticket_workflow.py", current_test(ticket_id)),
        (desired_dir / "README.md", desired_readme(ticket_id, title, baseline)),
        (desired_dir / "spec_manifest.yaml", desired_manifest(module, package, ticket_id, title)),
        (desired_dir / "ticket_plan.yaml", ticket_plan(ticket_id, title, module)),
        (desired_dir / "desired_state.yaml", desired_state(ticket_id, title, module)),
    ]
    for path, content in files:
        if write_file(path, content, force=force, dry_run=dry_run):
            written.append(path)

    tla_fallback = minimal_tla(module)
    cfg_fallback = minimal_cfg()
    for target_dir in [current_dir, desired_dir]:
        tla_target = target_dir / f"{module}.tla"
        cfg_target = target_dir / "MC.cfg"
        if copy_file(baseline.tla_path, tla_target, tla_fallback, force=force, dry_run=dry_run):
            written.append(tla_target)
        if copy_file(baseline.cfg_path, cfg_target, cfg_fallback, force=force, dry_run=dry_run):
            written.append(cfg_target)

    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ticket_id", help="Ticket id, for example AUTH-123 or K8S-010.")
    parser.add_argument("title", help="Human-readable ticket title.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root to scaffold into.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing scaffold files.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned writes without changing files.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    written = scaffold(repo_root, args.ticket_id, args.title, args.force, args.dry_run)
    print(f"scaffolded ticket workflow files: {len(written)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
