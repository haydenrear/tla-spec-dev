#!/usr/bin/env python3
"""Scaffold the first whole-program TLA+ model for an existing repository.

This is the project-onboarding path. It creates ``specs/program_model`` as the
accepted baseline and intentionally does not create ``specs/current`` or
``specs/desired_program_model``. Those directories are for later ticket work
after a program model already exists.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower()).strip("_")
    return normalized or "program_model"


def _module_name(value: str) -> str:
    direct = re.sub(r"[^a-zA-Z0-9]+", "", value)
    if direct and direct[0].isalpha() and any(ch.isupper() for ch in direct[1:]):
        return direct
    candidate = "".join(part.capitalize() for part in re.split(r"[^a-zA-Z0-9]+", value) if part)
    if not candidate:
        return "ProgramModel"
    if candidate[0].isdigit():
        return f"Program{candidate}"
    return candidate


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


def _resolve_spec_root(repo_root: Path, spec_root: Path) -> Path:
    return spec_root if spec_root.is_absolute() else repo_root / spec_root


def _display_spec_root(repo_root: Path, spec_root: Path) -> str:
    if spec_root.is_absolute():
        try:
            return spec_root.relative_to(repo_root).as_posix()
        except ValueError:
            return spec_root.as_posix()
    return spec_root.as_posix()


def program_model_tla(module: str) -> str:
    return f"""----------------------------- MODULE {module} -----------------------------
EXTENDS Naturals, FiniteSets, Sequences, TLC

CONSTANTS
  Units,
  SkillUnits,
  PluginUnits,
  CliDeps,
  McpDeps,
  NoReason

VARIABLES
  installed_units,
  projected_units,
  registered_mcp_deps,
  units_lock,
  result

vars == << installed_units, projected_units, registered_mcp_deps, units_lock, result >>

KnownUnits == SkillUnits \\cup PluginUnits

Init ==
  /\\ installed_units = {{}}
  /\\ projected_units = {{}}
  /\\ registered_mcp_deps = {{}}
  /\\ units_lock = {{}}
  /\\ result = [accepted |-> TRUE, reason |-> NoReason]

\\* @command InstallUnit
\\* @result InstallUnitResult
\\* @port ProgramModelPort.install_unit
InstallUnit(u) ==
  IF u \\in installed_units
  THEN
    /\\ result' = [accepted |-> FALSE, reason |-> "ALREADY_INSTALLED"]
    /\\ UNCHANGED << installed_units, projected_units, registered_mcp_deps, units_lock >>
  ELSE
    /\\ installed_units' = installed_units \\cup {{u}}
    /\\ projected_units' = projected_units \\cup {{u}}
    /\\ registered_mcp_deps' = registered_mcp_deps \\cup (McpDeps[u])
    /\\ units_lock' = units_lock \\cup {{u}}
    /\\ result' = [accepted |-> TRUE, reason |-> NoReason]

\\* @command RemoveUnit
\\* @result RemoveUnitResult
\\* @port ProgramModelPort.remove_unit
RemoveUnit(u) ==
  IF u \\notin installed_units
  THEN
    /\\ result' = [accepted |-> FALSE, reason |-> "NOT_INSTALLED"]
    /\\ UNCHANGED << installed_units, projected_units, registered_mcp_deps, units_lock >>
  ELSE
    /\\ installed_units' = installed_units \\ {{u}}
    /\\ projected_units' = projected_units \\ {{u}}
    /\\ registered_mcp_deps' =
        UNION {{McpDeps[v] : v \\in installed_units' }}
    /\\ units_lock' = units_lock \\ {{u}}
    /\\ result' = [accepted |-> TRUE, reason |-> NoReason]

\\* @command SyncLock
\\* @result SyncLockResult
\\* @port ProgramModelPort.sync_lock
SyncLock(target) ==
  /\\ target \\subseteq KnownUnits
  /\\ installed_units' = target
  /\\ projected_units' = target
  /\\ registered_mcp_deps' = UNION {{McpDeps[u] : u \\in target}}
  /\\ units_lock' = target
  /\\ result' = [accepted |-> TRUE, reason |-> NoReason]

Next ==
  \\/ \\E u \\in KnownUnits:
      InstallUnit(u)
  \\/ \\E u \\in KnownUnits:
      RemoveUnit(u)
  \\/ \\E target \\in SUBSET KnownUnits:
      SyncLock(target)

\\* @invariant InstalledUnitsAreKnown
InstalledUnitsAreKnown ==
  installed_units \\subseteq KnownUnits

\\* @invariant SkillAndPluginKindsAreDisjoint
SkillAndPluginKindsAreDisjoint ==
  SkillUnits \\cap PluginUnits = {{}}

\\* @invariant ProjectedUnitsAreInstalled
ProjectedUnitsAreInstalled ==
  projected_units \\subseteq installed_units

\\* @invariant LockTracksInstalledUnits
LockTracksInstalledUnits ==
  units_lock = installed_units

\\* @invariant RegisteredMcpDepsComeFromInstalledUnits
RegisteredMcpDepsComeFromInstalledUnits ==
  registered_mcp_deps = UNION {{McpDeps[u] : u \\in installed_units}}

Spec ==
  Init /\\ [][Next]_vars

=============================================================================
"""


def model_cfg() -> str:
    return """SPECIFICATION Spec

CONSTANTS
  Units = {hello_skill, hello_plugin}
  SkillUnits = {hello_skill}
  PluginUnits = {hello_plugin}
  CliDeps = (hello_skill :> {} @@ hello_plugin :> {})
  McpDeps = (hello_skill :> {} @@ hello_plugin :> {echo_mcp})
  NoReason = NoReason

INVARIANTS
  InstalledUnitsAreKnown
  SkillAndPluginKindsAreDisjoint
  ProjectedUnitsAreInstalled
  LockTracksInstalledUnits
  RegisteredMcpDepsComeFromInstalledUnits
"""


def manifest(module: str, package: str, spec_root_text: str = "specs") -> str:
    return f"""module: {module}
package: {package}

status:
  workflow: project_onboarding
  model_role: accepted_program_model
  relation_to_current: none_until_ticket_workflow_starts
  relation_to_desired_program_model: none_until_ticket_workflow_starts
  updated: null
  onboarding:
    status: scaffolded
    next:
      - Replace the scaffolded state fields and actions with repository-specific whole-program semantics.
      - Add adapter mappings for real production boundaries.
      - Run TLC for {spec_root_text}/program_model/MC.cfg.
      - Generate transition cases and validate adapter coverage.

state:
  {module}State:
    fields:
      installed_units:
        type: frozenset[UnitId]
        tla: installed_units
      projected_units:
        type: frozenset[UnitId]
        tla: projected_units
      registered_mcp_deps:
        type: frozenset[McpDependencyId]
        tla: registered_mcp_deps
      units_lock:
        type: frozenset[UnitId]
        tla: units_lock

types:
  UnitId:
    python: str
    source: Units
  McpDependencyId:
    python: str
    source: McpDeps

commands:
  InstallUnit:
    action: InstallUnit
    fields:
      unit_id:
        type: UnitId
        tla: u
  RemoveUnit:
    action: RemoveUnit
    fields:
      unit_id:
        type: UnitId
        tla: u
  SyncLock:
    action: SyncLock
    fields:
      target_units:
        type: frozenset[UnitId]
        tla: target

results:
  InstallUnitResult:
    fields:
      accepted:
        type: bool
      reason:
        type: str | None
        default: None
  RemoveUnitResult:
    fields:
      accepted:
        type: bool
      reason:
        type: str | None
        default: None
  SyncLockResult:
    fields:
      accepted:
        type: bool
      reason:
        type: str | None
        default: None

ports:
  ProgramModelPort:
    methods:
      install_unit:
        command: InstallUnit
        result: InstallUnitResult
      remove_unit:
        command: RemoveUnit
        result: RemoveUnitResult
      sync_lock:
        command: SyncLock
        result: SyncLockResult
      snapshot:
        result: {module}State

invariants:
  - InstalledUnitsAreKnown
  - SkillAndPluginKindsAreDisjoint
  - ProjectedUnitsAreInstalled
  - LockTracksInstalledUnits
  - RegisteredMcpDepsComeFromInstalledUnits

finite_model:
  Units:
    values:
      - hello_skill
      - hello_plugin
  SkillUnits:
    values:
      - hello_skill
  PluginUnits:
    values:
      - hello_plugin
  McpDeps:
    values:
      hello_skill: []
      hello_plugin:
        - echo_mcp

case_codegen:
  style: explicit_transition_cases
  generation_status: planned
"""


def readme(module: str, spec_root_text: str = "specs") -> str:
    return f"""# Program Model

This directory is the accepted whole-program TLA+ model for this repository.
It is the semantic baseline for future ticket workflows.

Files:

- `{module}.tla`: canonical whole-program state machine.
- `MC.cfg`: bounded TLC model for the accepted baseline.
- `spec_manifest.yaml`: manifest for generated cases, ports, invariants,
  adapter expectations, and onboarding status.
- `case_adapters.toml`: production adapter mapping for generated cases.
- `production_adapters.py`: repository-local adapter extension points.

Use `{spec_root_text}/current` and `{spec_root_text}/desired_program_model` only after this baseline
exists and a later ticket needs a planned destination. First onboarding should
not create those directories.
"""


def case_adapters_toml() -> str:
    return """# Map generated program-model action labels to production adapters.
# Example:
# [adapters.InstallUnit]
# adapter = "specs.program_model.production_adapters:InstallUnitAdapter"
"""


def production_adapters_py() -> str:
    return '''"""Production adapters for whole-program model cases.

Each adapter materializes a generated case pre-state, calls the production
boundary, observes production state, and refines the observation back to the
generated case shape.
"""

from __future__ import annotations


class ScaffoldedProgramModelAdapter:
    """Placeholder documenting the expected adapter shape."""

    def can_run(self, case):
        return False, "replace with a repository-specific program-model adapter"
'''


def onboarding_test(module: str, spec_root_text: str = "specs") -> str:
    return f'''from pathlib import Path


SPEC_ROOT = Path(__file__).resolve().parents[1]


def test_program_model_onboarding_scaffold_has_program_model_files() -> None:
    assert (SPEC_ROOT / "{module}.tla").exists()
    assert (SPEC_ROOT / "spec_manifest.yaml").exists()
'''


def scaffold(
    repo_root: Path,
    name: str | None,
    force: bool,
    dry_run: bool,
    spec_root: Path = Path("specs"),
) -> list[Path]:
    module = _module_name(name or repo_root.name)
    package = f"{_slug(module)}_program_cases"
    resolved_spec_root = _resolve_spec_root(repo_root, spec_root)
    spec_root_text = _display_spec_root(repo_root, spec_root)
    program_dir = resolved_spec_root / "program_model"

    files = [
        (program_dir / "README.md", readme(module, spec_root_text)),
        (program_dir / f"{module}.tla", program_model_tla(module)),
        (program_dir / "MC.cfg", model_cfg()),
        (program_dir / "spec_manifest.yaml", manifest(module, package, spec_root_text)),
        (program_dir / "case_adapters.toml", case_adapters_toml()),
        (program_dir / "production_adapters.py", production_adapters_py()),
        (program_dir / "tests" / "test_program_model_onboarding.py", onboarding_test(module, spec_root_text)),
    ]

    written: list[Path] = []
    for path, content in files:
        if write_file(path, content, force=force, dry_run=dry_run):
            written.append(path)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root to scaffold into.")
    parser.add_argument("--spec-root", type=Path, default=Path("specs"), help="Spec root under the repository.")
    parser.add_argument("--name", help="Program/module name. Defaults to the repository directory name.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing program-model files.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned writes without changing files.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    written = scaffold(repo_root, args.name, args.force, args.dry_run, args.spec_root)
    print(f"scaffolded program model files: {len(written)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
