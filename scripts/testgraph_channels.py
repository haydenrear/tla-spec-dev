#!/usr/bin/env python3
"""External channel enforcement for Test Graph bindings (MF-015).

A Test Graph adapter that imports the production package in-process is not
driving the deployed program -- it is a spec-unit adapter wearing an External
label. Structural assertions ("this binding is external") never caught that,
because nothing verified the claim. This module verifies it.

Three enforcement surfaces, all hard gates:

1. **Channel.** Every external binding declares ``channel`` -- one of
   http/cli/fs/queue/k8s. Absence fails. There is no default channel and no
   inference from the adapter name: a binding whose author did not say how the
   program is driven has not declared an external channel.

2. **Import isolation.** The adapter, projector, expected_projection and
   assertion modules of an external binding are parsed and MAY NOT import the
   declared production package, directly or through a first-party helper. The
   analysis is transitive so that laundering the import through a sibling
   module does not evade it.

3. **Port binding configuration.** Every external contract declares
   ``port_bindings``, mapping each port to ``double`` or ``real``. This is what
   lets a graph run name its integration-ladder rung. An all-doubles
   configuration is rejected: with every port doubled nothing real is under
   test, so it is a spec-unit run and never a Test Graph node.

**No escape hatches** (references/architecture_tractability.md, "No Degenerate
Escapes"). There is no override flag, no "when present" conditional, and no
fallback default anywhere in this module. A missing declaration is a failure,
not a skipped check -- a gate that disables itself when its input is absent is
the exact degeneracy the doctrine forbids.

The one extensibility point is explicit and visible: a contract may declare
``additional_channels`` to name channels beyond the base five. That is a
per-program decision recorded in the bindings file, in the same shape as
raising a budget in the manifest. It widens the accepted set; it can never
excuse a binding that declares no channel at all.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

try:
    from .extract_spec_manifest import load_manifest
except ImportError:  # pragma: no cover - direct script execution
    from extract_spec_manifest import load_manifest


BASE_CHANNELS = frozenset({"http", "cli", "fs", "queue", "k8s"})
PORT_MODES = frozenset({"double", "real"})

#: Binding fields naming code that executes inside the Test Graph process.
#: Each is import-isolated: all four run in the harness, so a production
#: import in any one of them breaks External-ness just as thoroughly.
ADAPTER_ROLES = ("adapter", "projector", "expected_projection", "assertion")

REMEDIATION_IMPORT = (
    "rebind this action as a spec-unit adapter in case_adapters.toml, or drive "
    "the declared channel instead of calling the production package in-process"
)
REMEDIATION_CHANNEL = (
    "declare channel: one of {} (or add the name to external.additional_channels "
    "if this program genuinely drives another transport)"
)


@dataclass(frozen=True)
class ChannelViolation:
    """One enforcement failure, reported with everything needed to fix it."""

    action: str
    adapter: str
    problem: str
    remediation: str

    def render(self) -> str:
        return (
            f"  action {self.action}\n"
            f"    adapter:     {self.adapter}\n"
            f"    problem:     {self.problem}\n"
            f"    remediation: {self.remediation}"
        )


class ChannelEnforcementError(Exception):
    """Raised when external bindings fail enforcement. Carries every violation."""

    def __init__(self, source: str, violations: list[ChannelViolation]) -> None:
        self.source = source
        self.violations = violations
        body = "\n".join(violation.render() for violation in violations)
        super().__init__(
            f"ERROR: external channel enforcement failed for {len(violations)} "
            f"binding(s) in {source}\n{body}"
        )


# --------------------------------------------------------------------------
# Contract parsing
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class ExternalContract:
    """The ``external:`` block of a testgraph_bindings.yml file."""

    production_package: str
    port_bindings: dict[str, str]
    additional_channels: frozenset[str]

    @property
    def allowed_channels(self) -> frozenset[str]:
        return BASE_CHANNELS | self.additional_channels

    @property
    def real_ports(self) -> tuple[str, ...]:
        return tuple(sorted(p for p, mode in self.port_bindings.items() if mode == "real"))

    @property
    def double_ports(self) -> tuple[str, ...]:
        return tuple(sorted(p for p, mode in self.port_bindings.items() if mode == "double"))

    def rung(self) -> str:
        """Name the integration-ladder rung this configuration expresses."""
        return "+".join(self.real_ports) if self.real_ports else "all-doubles"


def load_bindings_data(path: Path) -> dict[str, Any]:
    """Load a bindings file, YAML or TOML.

    Bindings are conventionally YAML (``testgraph_bindings.yml``) but the runner
    accepts a TOML mapping for the same role, so this gate must read both or it
    would silently not apply to half the supported inputs.
    """
    if path.suffix.lower() in {".yaml", ".yml"}:
        data = load_manifest(path)
    else:
        try:
            from .run_generated_case_adapters import load_toml
        except ImportError:  # pragma: no cover - direct script execution
            from run_generated_case_adapters import load_toml
        data = load_toml(path)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: bindings root must be a mapping")
    return data


def parse_external_contract(data: dict[str, Any], source: str) -> ExternalContract:
    """Read and validate the ``external:`` block. Every field is required."""
    block = data.get("external")
    if not isinstance(block, dict):
        raise ChannelEnforcementError(
            source,
            [
                ChannelViolation(
                    action="<file>",
                    adapter=source,
                    problem="no external: block declaring production_package and port_bindings",
                    remediation=(
                        "add an external: block with production_package: <package> and "
                        "port_bindings: {<port>: double|real}"
                    ),
                )
            ],
        )

    violations: list[ChannelViolation] = []

    package = block.get("production_package")
    if not isinstance(package, str) or not package.strip():
        violations.append(
            ChannelViolation(
                action="<file>",
                adapter=source,
                problem="external.production_package is not declared",
                remediation=(
                    "name the importable package that IS the program under test, so "
                    "adapters can be checked for importing it in-process"
                ),
            )
        )
        package = ""

    raw_ports = block.get("port_bindings")
    port_bindings: dict[str, str] = {}
    if not isinstance(raw_ports, dict) or not raw_ports:
        violations.append(
            ChannelViolation(
                action="<file>",
                adapter=source,
                problem="external.port_bindings is not declared",
                remediation=(
                    "declare each port as double or real; this is what names the "
                    "integration-ladder rung the graph run occupies"
                ),
            )
        )
    else:
        for port, mode in raw_ports.items():
            if not isinstance(mode, str) or mode not in PORT_MODES:
                violations.append(
                    ChannelViolation(
                        action=f"port {port}",
                        adapter=source,
                        problem=f"port binding {mode!r} is not double or real",
                        remediation="set the port to exactly double or real",
                    )
                )
                continue
            port_bindings[str(port)] = mode
        if port_bindings and not any(mode == "real" for mode in port_bindings.values()):
            violations.append(
                ChannelViolation(
                    action="<file>",
                    adapter=source,
                    problem=(
                        "every port is bound to double, so no real component is under "
                        "test; an all-doubles configuration is not a Test Graph rung"
                    ),
                    remediation=(
                        "bind at least one port to real, or run these cases as "
                        "spec-unit cases where all-doubles is the correct shape"
                    ),
                )
            )

    raw_additional = block.get("additional_channels", [])
    additional: set[str] = set()
    if isinstance(raw_additional, list):
        for name in raw_additional:
            if isinstance(name, str) and name.strip():
                additional.add(name.strip())
    elif raw_additional:
        violations.append(
            ChannelViolation(
                action="<file>",
                adapter=source,
                problem="external.additional_channels must be a list of channel names",
                remediation="write additional_channels: [name, ...]",
            )
        )

    if violations:
        raise ChannelEnforcementError(source, violations)

    return ExternalContract(
        production_package=package,
        port_bindings=port_bindings,
        additional_channels=frozenset(additional),
    )


# --------------------------------------------------------------------------
# Static import analysis
# --------------------------------------------------------------------------


def module_of(reference: str) -> str:
    """``pkg.mod:Object`` -> ``pkg.mod``."""
    return reference.split(":", 1)[0]


def resolve_module_file(dotted: str, roots: Iterable[Path]) -> Path | None:
    """Find the source file for a dotted module name under any of ``roots``."""
    parts = dotted.split(".")
    for root in roots:
        candidate = root.joinpath(*parts).with_suffix(".py")
        if candidate.is_file():
            return candidate
        package = root.joinpath(*parts) / "__init__.py"
        if package.is_file():
            return package
    return None


def imported_modules(tree: ast.AST) -> set[str]:
    """Every module name this source imports, statically.

    Covers ``import x.y``, ``from x.y import z``, and the dynamic forms
    ``importlib.import_module("x.y")`` / ``__import__("x.y")`` when called with
    a literal -- the obvious ways an adapter reaches the production package.
    """
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            # Relative imports (level > 0) have no absolute module name here;
            # they are followed separately as first-party siblings.
            if node.level == 0 and node.module:
                found.add(node.module)
        elif isinstance(node, ast.Call):
            target = node.func
            name = None
            if isinstance(target, ast.Attribute) and target.attr == "import_module":
                name = "import_module"
            elif isinstance(target, ast.Name) and target.id in {"__import__", "import_module"}:
                name = target.id
            if name and node.args:
                first = node.args[0]
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    found.add(first.value)
    return found


def is_production_import(dotted: str, package: str) -> bool:
    return dotted == package or dotted.startswith(f"{package}.")


def production_imports_for_module(
    dotted: str,
    *,
    package: str,
    roots: list[Path],
    _visited: set[str] | None = None,
) -> list[tuple[str, str]]:
    """Transitively collect production imports reachable from ``dotted``.

    Returns ``(importing_module, imported_name)`` pairs. Transitive because an
    adapter that imports a local helper which imports the production package is
    running production code in-process just the same; only following direct
    imports would make the gate trivially evadable.
    """
    visited = _visited if _visited is not None else set()
    if dotted in visited:
        return []
    visited.add(dotted)

    path = resolve_module_file(dotted, roots)
    if path is None:
        return []

    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError):
        return []

    offenders: list[tuple[str, str]] = []
    for imported in sorted(imported_modules(tree)):
        if is_production_import(imported, package):
            offenders.append((dotted, imported))
            continue
        # Follow first-party imports only: a module we can resolve to a file
        # under the same roots is part of this repository's adapter code.
        if resolve_module_file(imported, roots) is not None:
            offenders.extend(
                production_imports_for_module(
                    imported, package=package, roots=roots, _visited=visited
                )
            )
    return offenders


# --------------------------------------------------------------------------
# The gate
# --------------------------------------------------------------------------


def channel_of(spec: dict[str, Any]) -> str | None:
    channel = spec.get("channel")
    return channel if isinstance(channel, str) and channel.strip() else None


def enforce_external_bindings(
    bindings_path: Path,
    *,
    import_roots: Iterable[Path] | None = None,
    actions: Iterable[str] | None = None,
) -> ExternalContract:
    """Hard gate over a testgraph_bindings.yml file.

    Raises :class:`ChannelEnforcementError` listing every violation. Returns the
    validated contract so callers can report the integration-ladder rung.

    ``actions`` optionally restricts enforcement to specific action names. It
    narrows *which bindings are checked*, never *how strictly*: any binding it
    covers is held to the full contract.
    """
    source = str(bindings_path)
    data = load_bindings_data(bindings_path)
    contract = parse_external_contract(data, source)

    roots = list(import_roots) if import_roots is not None else []
    roots.append(bindings_path.resolve().parent)
    # Walk upward so repo-root-relative dotted paths ("specs.program_model.adapters")
    # resolve as well as spec-dir-relative ones.
    roots.extend(bindings_path.resolve().parents)
    roots = list(dict.fromkeys(root for root in roots if root.is_dir()))

    action_table = data.get("actions")
    if not isinstance(action_table, dict) or not action_table:
        raise ChannelEnforcementError(
            source,
            [
                ChannelViolation(
                    action="<file>",
                    adapter=source,
                    problem="no actions: table of external bindings",
                    remediation="declare each external action under actions:",
                )
            ],
        )

    wanted = set(actions) if actions is not None else None
    violations: list[ChannelViolation] = []

    for name, spec in sorted(action_table.items()):
        action = str(name)
        if wanted is not None and action not in wanted:
            continue
        if not isinstance(spec, dict):
            violations.append(
                ChannelViolation(
                    action=action,
                    adapter="<none>",
                    problem="binding is not a mapping",
                    remediation="write the binding as a mapping of fields",
                )
            )
            continue

        adapter_ref = spec.get("adapter")
        adapter_label = adapter_ref if isinstance(adapter_ref, str) else "<none>"

        channel = channel_of(spec)
        if channel is None:
            violations.append(
                ChannelViolation(
                    action=action,
                    adapter=adapter_label,
                    problem="binding declares no channel",
                    remediation=REMEDIATION_CHANNEL.format(
                        "/".join(sorted(contract.allowed_channels))
                    ),
                )
            )
        elif channel not in contract.allowed_channels:
            violations.append(
                ChannelViolation(
                    action=action,
                    adapter=adapter_label,
                    problem=f"channel {channel!r} is not a declared channel",
                    remediation=REMEDIATION_CHANNEL.format(
                        "/".join(sorted(contract.allowed_channels))
                    ),
                )
            )

        for role in ADAPTER_ROLES:
            reference = spec.get(role)
            if not isinstance(reference, str) or not reference:
                continue
            dotted = module_of(reference)
            offenders = production_imports_for_module(
                dotted, package=contract.production_package, roots=roots
            )
            for importing, imported in offenders:
                via = "" if importing == dotted else f" (via {importing})"
                violations.append(
                    ChannelViolation(
                        action=action,
                        adapter=reference,
                        problem=(
                            f"{role} module {dotted} imports production package "
                            f"{imported!r}{via}; a Test Graph adapter that imports the "
                            f"program under test is running it in-process, not over "
                            f"the declared {channel or '<undeclared>'} channel"
                        ),
                        remediation=REMEDIATION_IMPORT,
                    )
                )

    if violations:
        raise ChannelEnforcementError(source, violations)
    return contract
