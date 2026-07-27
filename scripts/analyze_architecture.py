#!/usr/bin/env python3
"""AC-01: the ARCHITECTURE DESCRIPTOR -- the structure the diagram implies.

`analyze complexity` already computes the variables x actions R/W matrix, the
graph modularity of that matrix, and the near-decomposable clusters it admits.
It PRINTS them. Nothing can consume them, and nothing names the thing they
describe. This module names it and makes it addressable:

  * **components** -- the variable clusters, with the actions that touch them;
  * **ownership** -- for each variable, the actions that write it, and every
    single-writer violation (a variable written from more than one component);
  * **ports**      -- the crossing actions between components: what would have
    to become an interface if the cut were taken;
  * **span**       -- the actions whose WRITE set spans components (the
    god-actions), with their model-side (file-free) evidence.

Three rules govern every line below.

**Advisory, not blocking (MF-036, and the epic's standing doctrine).** This
command records facts. It never refuses a close, a promotion, or a case
generation. The only nonzero exit is the MF-030 fail-closed: a module
hierarchy the parser cannot resolve, which is "I could not measure this", not
"this model is incoherent". A model that is a single undifferentiated blob
exits 0 and says so.

**No suggested moves (CD-01).** The abstract/decompose/refactor chooser was
removed after validation showed it confidently wrong on standard TLA+ (an
aliased invariant made it recommend projecting away every variable). This
module does not propose a partition, a refactor, a target shape, or a next
step. Every figure it prints is labeled ``[MEASURED]``. The one judgment it
makes -- "this partition is not a cut" -- is a REFUSAL, published with the
explicit criteria table that produced it, so the reader can check the rule.

**A refusal beats a false clean (MF-027).** A model whose interaction graph
does not decompose says so. It does not get a one-component partition in which
every variable is trivially "owned by its component" and no action is a port:
that would report a clean architecture for a model that has none. Where the
measurement is not defined, the field is ``null`` and carries a reason.

Consumers
---------
The JSON payload (``--format json``) is the contract AC-02 (reflexion check)
and AC-03 (implementation-brief prompt) read. See
``references/architecture_coherence.md`` for the field-by-field contract, and
in particular ``partition.consumable_as_architecture``: when it is false, a
consumer must report ``unmappable`` rather than treat the blob as a clean
architecture.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

if __package__ in (None, ""):  # direct `python3 scripts/analyze_architecture.py`
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.analyze_complexity import (  # noqa: E402
    Action,
    ModuleResolutionError,
    extract_actions,
    extract_next_actions,
    find_next_relation,
    greedy_communities,
    interaction_graph,
    modularity,
    resolve_module,
)

EXIT_PASS = 0
EXIT_ANALYSIS_ERROR = 1
EXIT_USAGE = 2

SCHEMA = "tla-spec-dev/architecture-descriptor"
SCHEMA_VERSION = 1

# The R/W matrix's own >half convention, reused rather than invented: the
# complexity descriptor already calls a variable a dense row when more than half
# the actions touch it, and an action a dense column when it touches more than
# half the variables. A partition more than half of whose actions cross it is
# the same shape of fact -- the boundary is crossed by most of the program, so
# it is not a boundary.
MAX_CROSSING_FRACTION = 0.5

# Newman's conventional reading of the modularity score: Q above ~0.3 indicates
# significant community structure. REPORTED, never applied as a criterion --
# picking a Q threshold to pass or fail models is exactly the kind of tuned
# judgment CD-01 removed. The criteria below use only Q > 0 ("the partition
# explains more than chance").
NEWMAN_SIGNIFICANT_Q = 0.3


# --------------------------------------------------------------------------
# Components
# --------------------------------------------------------------------------


@dataclass
class Component:
    """One component: a named set of variables and the actions that reach it."""

    cid: str
    name: str
    variables: list[str] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    internal_actions: list[str] = field(default_factory=list)
    crossing_actions: list[str] = field(default_factory=list)
    writers: list[str] = field(default_factory=list)
    owns: list[str] = field(default_factory=list)
    reaches: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Port:
    """A port: the pair of components a set of actions crosses.

    The unit of the reflexion check (AC-02). A code edge whose endpoints map to
    two different components is CONVERGENT iff a port exists between them, and
    DIVERGENT otherwise.
    """

    pid: str
    between: tuple[str, str]
    actions: list[str] = field(default_factory=list)


class DeclaredPartitionError(Exception):
    """A declared component partition that cannot be read as one.

    Unusable INPUT, not an unusable model -- this exits nonzero like a usage
    error, because the project asked for a partition to be measured and the
    file it named could not be understood. Silently falling back to the
    emergent clustering would measure something the project did not ask for.
    """


def load_declared_components(
    source: Any, variables: Sequence[str], origin: str
) -> list[Component]:
    """Read a DECLARED component partition. Never inferred, never proposed.

    Shape (in ``spec_manifest.yaml`` under ``architecture:`` or in the file
    passed to ``--components``)::

        architecture:
          components:
            - name: lifecycle
              variables: [setup_phase, spec_root, ticket_state]
            - name: scanners
              variables: [complexity_gate, corpus_gate]

    Symmetric with AC-02's declared module map, for the same reason stated
    there: an auditing tool that picks its own boundary can define every
    finding out of existence. The tool measures the partition the project
    declares; it never writes one.
    """
    if isinstance(source, dict) and "architecture" in source:
        source = source.get("architecture")
    if isinstance(source, dict) and "components" in source:
        source = source.get("components")
    if not isinstance(source, (list, tuple)) or not source:
        raise DeclaredPartitionError(
            f"{origin}: expected a non-empty `components:` list under `architecture:`"
        )
    known = set(variables)
    components: list[Component] = []
    seen_names: set[str] = set()
    for index, entry in enumerate(source, start=1):
        if not isinstance(entry, dict):
            raise DeclaredPartitionError(
                f"{origin}: component #{index} is not a mapping with `name:` and `variables:`"
            )
        name = str(entry.get("name") or "").strip()
        if not name:
            raise DeclaredPartitionError(f"{origin}: component #{index} has no `name:`")
        if name in seen_names:
            raise DeclaredPartitionError(f"{origin}: component `{name}` is declared twice")
        seen_names.add(name)
        members = entry.get("variables")
        if not isinstance(members, (list, tuple)) or not members:
            raise DeclaredPartitionError(
                f"{origin}: component `{name}` declares no `variables:`"
            )
        unknown = [str(v) for v in members if str(v) not in known]
        if unknown:
            raise DeclaredPartitionError(
                f"{origin}: component `{name}` declares variables the model does not "
                f"have: {', '.join(sorted(unknown))}"
            )
        components.append(
            Component(cid=f"C{index}", name=name, variables=sorted(str(v) for v in members))
        )
    assigned: dict[str, str] = {}
    for component in components:
        for variable in component.variables:
            if variable in assigned:
                raise DeclaredPartitionError(
                    f"{origin}: `{variable}` is declared in both `{assigned[variable]}` and "
                    f"`{component.name}` -- a component partition must not overlap"
                )
            assigned[variable] = component.name
    return components


def emergent_components(
    variables: Sequence[str], actions: Sequence[Action]
) -> tuple[list[Component], float]:
    """The clusters the R/W matrix admits, via the complexity scanner's own method.

    Deliberately the SAME greedy modularity maximization `analyze complexity`
    already runs, not a second opinion: this ticket makes that structure
    addressable, it does not introduce a rival algorithm whose disagreements
    nobody could adjudicate.
    """
    weights = interaction_graph(actions, variables)
    partition, score = greedy_communities(variables, weights)
    components = [
        Component(cid=f"C{index}", name=f"C{index}", variables=sorted(cluster))
        for index, cluster in enumerate(partition, start=1)
    ]
    return components, score


def attribute_actions(components: Sequence[Component], actions: Sequence[Action]) -> None:
    """Fill each component's action lists, owned variables, and reachable set."""
    for component in components:
        member = set(component.variables)
        touching = [a.name for a in actions if a.touched & member]
        crossing = [
            a.name
            for a in actions
            if a.touched & member
            and any(a.touched & set(other.variables) for other in components if other is not component)
        ]
        component.actions = sorted(touching)
        component.crossing_actions = sorted(crossing)
        component.internal_actions = sorted(set(touching) - set(crossing))
        component.writers = sorted({a.name for a in actions if a.writes & member})
    # A variable is OWNED by a component when that component is the only one
    # its writes are confined to. Ownership is a property of the write set, not
    # of cluster membership. With a single component the question is not
    # defined -- everything would be trivially "owned", which is a clean answer
    # for a model with no components at all -- so it is left empty and the
    # renderer says why.
    if len(components) >= 2:
        writer_components = component_writers(components, actions)
        for component in components:
            component.owns = sorted(
                variable
                for variable in component.variables
                if writer_components.get(variable) == [component.cid]
            )
    by_id = {c.cid: c for c in components}
    for component in components:
        reaches: dict[str, list[str]] = {}
        member = set(component.variables)
        for action in actions:
            if not action.touched & member:
                continue
            for other in components:
                if other is component:
                    continue
                if action.touched & set(other.variables):
                    reaches.setdefault(other.cid, []).append(action.name)
        component.reaches = [
            {
                "component": cid,
                "name": by_id[cid].name,
                "via_actions": sorted(set(names)),
            }
            for cid, names in sorted(reaches.items())
        ]


def component_of(components: Sequence[Component]) -> dict[str, str]:
    return {v: c.cid for c in components for v in c.variables}


def component_writers(
    components: Sequence[Component], actions: Sequence[Action]
) -> dict[str, list[str]]:
    """For each variable, the components its writes are committed alongside.

    Attribution is over each action's WRITE set only, deliberately. An action
    that reads ``a`` in C1 and writes ``b`` in C2 writes into one component;
    calling ``b`` multi-component because the action glanced across the
    boundary would make every variable touched by any crossing action a
    violation, and the finding would carry no information. An action that
    WRITES in C1 and C2 does commit state in both, and every variable it writes
    is then, measurably, not confined to one component.
    """
    owner = component_of(components)
    result: dict[str, list[str]] = {variable: [] for variable in owner}
    for action in actions:
        written_in = sorted({owner[v] for v in action.writes if v in owner})
        for variable in action.writes:
            if variable not in owner:
                continue
            for cid in written_in:
                if cid not in result[variable]:
                    result[variable].append(cid)
    return {variable: sorted(cids) for variable, cids in result.items()}


# --------------------------------------------------------------------------
# Ports and span
# --------------------------------------------------------------------------


def ports_of(components: Sequence[Component], actions: Sequence[Action]) -> list[Port]:
    """The component pairs actions cross -- the interfaces the cut would need."""
    owner = component_of(components)
    pairs: dict[tuple[str, str], list[str]] = {}
    for action in actions:
        hit = sorted({owner[v] for v in action.touched if v in owner})
        for i, left in enumerate(hit):
            for right in hit[i + 1 :]:
                pairs.setdefault((left, right), []).append(action.name)
    return [
        Port(pid=f"P{index}", between=pair, actions=sorted(set(names)))
        for index, (pair, names) in enumerate(sorted(pairs.items()), start=1)
    ]


def crossing_actions_of(
    components: Sequence[Component], actions: Sequence[Action], ports: Sequence[Port]
) -> list[dict[str, Any]]:
    owner = component_of(components)
    port_of_pair = {port.between: port.pid for port in ports}
    rows: list[dict[str, Any]] = []
    for action in sorted(actions, key=lambda a: a.name):
        hit = sorted({owner[v] for v in action.touched if v in owner})
        if len(hit) < 2:
            continue
        pids = sorted(
            port_of_pair[(left, right)]
            for i, left in enumerate(hit)
            for right in hit[i + 1 :]
            if (left, right) in port_of_pair
        )
        rows.append(
            {
                "action": action.name,
                "components": hit,
                "ports": pids,
                "reads": {
                    cid: sorted(v for v in action.reads if owner.get(v) == cid) for cid in hit
                },
                "writes": {
                    cid: sorted(v for v in action.writes if owner.get(v) == cid) for cid in hit
                },
            }
        )
    return rows


def spanning_actions_of(
    components: Sequence[Component], actions: Sequence[Action]
) -> list[dict[str, Any]]:
    """Actions whose WRITE set spans components -- the god-actions.

    Distinct from a crossing action, which merely READS across the boundary. A
    spanning action commits state in two components in one step, so the cut
    cannot be taken without splitting the action's atomicity. The evidence is
    file-free by construction: it names variables and actions of the model.
    """
    owner = component_of(components)
    rows: list[dict[str, Any]] = []
    for action in sorted(actions, key=lambda a: a.name):
        written = sorted({owner[v] for v in action.writes if v in owner})
        if len(written) < 2:
            continue
        rows.append(
            {
                "action": action.name,
                "write_components": written,
                "writes": {
                    cid: sorted(v for v in action.writes if owner.get(v) == cid)
                    for cid in written
                },
                "evidence": (
                    f"{action.name} writes "
                    + "; ".join(
                        f"{cid}: {', '.join(sorted(v for v in action.writes if owner.get(v) == cid))}"
                        for cid in written
                    )
                    + " in one step"
                ),
            }
        )
    return rows


def single_writer_violations(
    components: Sequence[Component], actions: Sequence[Action]
) -> list[dict[str, Any]]:
    """Variables written from more than one component (Move 3, single-writer state)."""
    writer_components = component_writers(components, actions)
    by_id = {c.cid: c.name for c in components}
    rows: list[dict[str, Any]] = []
    for variable in sorted(writer_components):
        cids = writer_components[variable]
        if len(cids) < 2:
            continue
        rows.append(
            {
                "variable": variable,
                "components": cids,
                "component_names": [by_id[cid] for cid in cids],
                "writers": sorted(a.name for a in actions if variable in a.writes),
            }
        )
    return rows


# --------------------------------------------------------------------------
# Does the partition decompose the model at all?
# --------------------------------------------------------------------------


def decomposition_criteria(
    components: Sequence[Component], actions: Sequence[Action], q: float
) -> list[dict[str, Any]]:
    """The published rule that decides whether a partition is a CUT.

    Three checks, each a measured number against a stated rule. They are
    printed with their measurements so a reader can disagree with the rule
    rather than with a verdict handed down without one.
    """
    crossing = {row["action"] for row in crossing_actions_of(components, actions, ports_of(components, actions))}
    fraction = (len(crossing) / len(actions)) if actions else 0.0
    return [
        {
            "name": "component_count",
            "measured": len(components),
            "rule": ">= 2",
            "met": len(components) >= 2,
            "why": "a partition with one component separated nothing",
        },
        {
            "name": "modularity_q",
            "measured": round(q, 6),
            "rule": "> 0",
            "met": q > 0.0,
            "why": (
                "Q <= 0 means the partition groups no more interaction than chance "
                f"(Newman's conventional threshold for significant community structure "
                f"is {NEWMAN_SIGNIFICANT_Q}; reported, not applied)"
            ),
        },
        {
            "name": "crossing_action_fraction",
            "measured": round(fraction, 6),
            "rule": f"<= {MAX_CROSSING_FRACTION}",
            "met": fraction <= MAX_CROSSING_FRACTION,
            "why": (
                "a boundary crossed by more than half the actions is not a boundary "
                "(the R/W matrix's own dense-row/dense-column convention)"
            ),
        },
    ]


# --------------------------------------------------------------------------
# Descriptor
# --------------------------------------------------------------------------


@dataclass
class ArchitectureDescriptor:
    module: str
    tla_path: Path
    cfg_path: Path
    manifest_path: Path | None
    variables: list[str]
    actions: list[Action]
    action_attribution: str
    partition_source: str
    partition_origin: str
    components: list[Component]
    modularity_q: float
    criteria: list[dict[str, Any]]
    ports: list[Port]
    crossings: list[dict[str, Any]]
    spans: list[dict[str, Any]]
    writers: dict[str, list[str]]
    violations: list[dict[str, Any]] | None
    violations_basis: str
    unassigned_variables: list[str]

    @property
    def decomposes(self) -> bool:
        return all(c["met"] for c in self.criteria)

    @property
    def consumable_as_architecture(self) -> bool:
        """Whether a consumer (AC-02/AC-03) may treat these components as THE architecture.

        A declared partition is consumable because the project named it; an
        emergent partition is consumable only if it is actually a cut. When
        this is false a consumer MUST report ``unmappable`` -- treating a
        single undifferentiated blob as an architecture makes every code edge
        internal and reports a clean result for a model with no structure.
        """
        return self.partition_source == "declared" or self.decomposes

    @property
    def architecture_scan(self) -> str:
        """The value the model's ``architecture_scan`` variable records.

        Always ``unmappable`` from this command. AC-01 measures the MODEL; with
        no production code there is nothing for the code to be coherent WITH,
        and a clean report on a target that was never observed is
        indistinguishable from a clean report on one that was (MF-027). AC-02
        supplies the code side and the other two values.
        """
        return "unmappable"

    @property
    def scan_reasons(self) -> list[str]:
        reasons: list[str] = []
        if not self.consumable_as_architecture:
            failed = [c["name"] for c in self.criteria if not c["met"]]
            reasons.append(
                "the model's variable interaction graph does not decompose (the "
                f"emergent partition fails: {', '.join(failed)}) and the project "
                "declares no component partition, so there is no architecture here to "
                "measure code against"
            )
        reasons.append(
            "no production code was supplied: `analyze architecture` on its own "
            "measures only the model side. The code comparison (--code/--map, the "
            "reflexion check) is AC-02; until it runs, coherence is unobserved"
        )
        return reasons


def analyze(
    tla_path: Path,
    cfg_path: Path,
    manifest_path: Path | None = None,
    *,
    components_path: Path | None = None,
) -> ArchitectureDescriptor:
    cfg_text = cfg_path.read_text(encoding="utf-8")

    # MF-030 fail-closed: resolve_module raises on any hierarchy construct the
    # parser cannot model. Never swallowed -- an unmeasurable model is the one
    # genuine error this command has.
    resolved = resolve_module(tla_path)
    variables = resolved.variables
    by_name = {d.name: d for d in resolved.defs}

    # CD-06: the action set is the top-level disjuncts of the next-state
    # relation, with helper bodies expanded. Same attribution as the complexity
    # descriptor, including its honest fallback note.
    next_name = find_next_relation(cfg_text, by_name)
    if next_name is not None:
        actions = extract_next_actions(next_name, by_name, variables)
        attribution = (
            f"top-level disjuncts of the next-state relation {next_name}, "
            "called-operator bodies expanded transitively; helpers are not actions"
        )
    else:
        actions = extract_actions(resolved.defs, variables)
        attribution = (
            "FALLBACK primes heuristic (every definition priming a variable) -- no "
            "next-state relation found via cfg NEXT or SPECIFICATION; helper operators "
            "may be listed as actions and composed actions may be missing"
        )

    declared_source: Any = None
    origin = ""
    if components_path is not None:
        declared_source = _load_yaml(components_path)
        origin = str(components_path)
    elif manifest_path is not None and manifest_path.is_file():
        # An unreadable MANIFEST is not an unusable declaration: the project did
        # not ask for a partition here, so fall through to the emergent
        # clustering rather than refuse. `--components` is the explicit request,
        # and that one does fail loudly.
        try:
            manifest = _load_yaml(manifest_path)
        except DeclaredPartitionError:
            manifest = None
        if isinstance(manifest, dict) and isinstance(manifest.get("architecture"), dict):
            declared_source = manifest["architecture"]
            origin = str(manifest_path)

    unassigned: list[str] = []
    if declared_source is not None:
        components = load_declared_components(declared_source, variables, origin)
        partition_source = "declared"
        partition_origin = f"declared by the project in {origin}"
        assigned = {v for c in components for v in c.variables}
        unassigned = [v for v in variables if v not in assigned]
        weights = interaction_graph(actions, variables)
        q = modularity([set(c.variables) for c in components], weights)
    else:
        components, q = emergent_components(variables, actions)
        partition_source = "emergent"
        partition_origin = (
            "computed by greedy modularity maximization over the variable "
            "interaction graph (the same method `analyze complexity` reports) -- "
            "a MEASUREMENT of what the matrix admits, not a declaration and not a "
            "proposal"
        )

    attribute_actions(components, actions)
    criteria = decomposition_criteria(components, actions, q)
    ports = ports_of(components, actions)
    crossings = crossing_actions_of(components, actions, ports)
    spans = spanning_actions_of(components, actions)
    writers = {
        variable: sorted(a.name for a in actions if variable in a.writes)
        for variable in variables
    }

    if len(components) < 2:
        # MF-027 refusal: with one component every variable is trivially
        # written "within its component" and the answer would be a clean zero
        # for a model that has no components at all.
        violations: list[dict[str, Any]] | None = None
        basis = (
            "NOT MEASURABLE: single-writer ownership is defined against a component "
            "partition, and this model has only one component. Reporting zero "
            "violations here would be a clean result for a model with no architecture."
        )
    else:
        violations = single_writer_violations(components, actions)
        if partition_source == "declared":
            basis = f"the DECLARED partition ({origin})"
        elif all(c["met"] for c in criteria):
            basis = "the EMERGENT partition, which meets every decomposition criterion"
        else:
            basis = (
                "the EMERGENT partition, which DOES NOT decompose the model (see the "
                "criteria table) -- these violations are relative to a cut the model "
                "does not actually have"
            )

    return ArchitectureDescriptor(
        module=resolved.root,
        tla_path=tla_path,
        cfg_path=cfg_path,
        manifest_path=manifest_path,
        variables=list(variables),
        actions=actions,
        action_attribution=attribution,
        partition_source=partition_source,
        partition_origin=partition_origin,
        components=components,
        modularity_q=q,
        criteria=criteria,
        ports=ports,
        crossings=crossings,
        spans=spans,
        writers=writers,
        violations=violations,
        violations_basis=basis,
        unassigned_variables=unassigned,
    )


def _load_yaml(path: Path) -> Any:
    """Read a YAML document, preferring PyYAML and falling back to the repo parser.

    The CLI runs under whatever interpreter the user has, and PyYAML is not a
    hard dependency of this repository -- ``scripts/extract_spec_manifest.py``
    ships a dependency-free parser for exactly the manifest subset this block
    lives in. Try the real parser first so a fuller YAML file still reads, then
    fall back rather than refusing to measure a manifest the rest of the
    toolchain reads fine.
    """
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)
    except ImportError:
        pass
    except Exception as exc:
        errors.append(f"PyYAML: {exc}")
    try:
        from scripts.extract_spec_manifest import parse_simple_yaml

        return parse_simple_yaml(text)
    except Exception as exc:
        errors.append(f"built-in parser: {exc}")
    raise DeclaredPartitionError(
        f"{path}: could not be parsed as YAML ({'; '.join(errors)})"
    )


# --------------------------------------------------------------------------
# JSON payload -- the AC-02 / AC-03 contract
# --------------------------------------------------------------------------


def descriptor_payload(
    descriptor: ArchitectureDescriptor, reflexion_report: Any = None
) -> dict[str, Any]:
    """The machine-readable descriptor. Field contract: references/architecture_coherence.md.

    ``reflexion_report`` is AC-02's :class:`~scripts.architecture_reflexion.ReflexionReport`
    when ``--code``/``--map`` were supplied. It is ADDITIVE: the descriptor
    fields are identical with and without it, and ``verdict.architecture_scan``
    moves off ``unmappable`` only because a code side was actually observed.
    """
    payload = {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "module": descriptor.module,
        "spec": str(descriptor.tla_path),
        "cfg": str(descriptor.cfg_path),
        "manifest": str(descriptor.manifest_path) if descriptor.manifest_path else None,
        "measured": {
            "variables": descriptor.variables,
            "actions": [
                {"name": a.name, "reads": sorted(a.reads), "writes": sorted(a.writes)}
                for a in sorted(descriptor.actions, key=lambda a: a.name)
            ],
            "action_attribution": descriptor.action_attribution,
            "partition": {
                "source": descriptor.partition_source,
                "origin": descriptor.partition_origin,
                "modularity_q": round(descriptor.modularity_q, 6),
                "newman_significant_q": NEWMAN_SIGNIFICANT_Q,
                "decomposes": descriptor.decomposes,
                "consumable_as_architecture": descriptor.consumable_as_architecture,
                "criteria": descriptor.criteria,
                "unassigned_variables": descriptor.unassigned_variables,
                "components": [
                    {
                        "id": c.cid,
                        "name": c.name,
                        "variables": c.variables,
                        "owns": c.owns,
                        "actions": c.actions,
                        "internal_actions": c.internal_actions,
                        "crossing_actions": c.crossing_actions,
                        "writer_actions": c.writers,
                        "reaches": c.reaches,
                    }
                    for c in descriptor.components
                ],
            },
            "ownership": {
                "writers": descriptor.writers,
                "single_writer_violations": descriptor.violations,
                "single_writer_basis": descriptor.violations_basis,
            },
            "ports": [
                {"id": p.pid, "between": list(p.between), "actions": p.actions}
                for p in descriptor.ports
            ],
            "crossing_actions": descriptor.crossings,
            "spanning_actions": descriptor.spans,
        },
        "verdict": {
            # The value the TLA+ model's `architecture_scan` variable records.
            "architecture_scan": descriptor.architecture_scan,
            "reasons": descriptor.scan_reasons,
            "blocks_promotion": False,
        },
        "advisory": {
            "blocks_promotion": False,
            "suggests_moves": False,
            "note": (
                "This descriptor states measured facts about the model's structure. It "
                "makes no recommendation, proposes no cut, and never refuses a close, a "
                "promotion, or a case generation."
            ),
        },
    }
    if reflexion_report is not None:
        from scripts.architecture_reflexion import report_payload

        payload["reflexion"] = report_payload(reflexion_report)
        payload["verdict"]["architecture_scan"] = reflexion_report.verdict
        payload["verdict"]["reasons"] = reflexion_report.reasons
    return payload


def render_json(descriptor: ArchitectureDescriptor, reflexion_report: Any = None) -> str:
    return (
        json.dumps(descriptor_payload(descriptor, reflexion_report), indent=2, sort_keys=False)
        + "\n"
    )


# --------------------------------------------------------------------------
# Text descriptor
# --------------------------------------------------------------------------


def _wrap(prefix: str, items: Iterable[str]) -> str:
    values = list(items)
    return f"{prefix}{', '.join(values) if values else '(none)'}"


def render_text(descriptor: ArchitectureDescriptor, reflexion_report: Any = None) -> str:
    out: list[str] = []
    add = out.append
    add(f"analyze architecture -- {descriptor.module} (architecture descriptor)")
    add(f"  spec:     {descriptor.tla_path}")
    add(f"  config:   {descriptor.cfg_path}")
    add(f"  manifest: {descriptor.manifest_path if descriptor.manifest_path else '(none)'}")
    add("")
    add("This is a DESCRIPTOR: every figure below is [MEASURED] -- parsed from this")
    add("spec + cfg. It names the structure the model implies and makes no")
    add("suggestions: no proposed cut, no refactor, no verdict on the code.")
    add("")

    add("[MEASURED] Component partition")
    add(f"  source: {descriptor.partition_source.upper()}")
    add(f"  {descriptor.partition_origin}")
    add(f"  actions: {descriptor.action_attribution}")
    if descriptor.unassigned_variables:
        add(_wrap("  variables in NO declared component: ", descriptor.unassigned_variables))
    add("")
    single_component = len(descriptor.components) < 2
    for component in descriptor.components:
        label = component.cid if component.cid == component.name else f"{component.cid} ({component.name})"
        add(f"  {label}")
        add(_wrap("    variables:         ", component.variables))
        if single_component:
            add(
                "    owns:              NOT MEASURABLE with one component -- every "
                "variable would be trivially owned."
            )
        else:
            add(_wrap("    owns (writes confined here): ", component.owns))
        add(_wrap("    internal actions:  ", component.internal_actions))
        add(_wrap("    crossing actions:  ", component.crossing_actions))
        if component.reaches:
            for reach in component.reaches:
                add(
                    f"    reaches {reach['component']} via: "
                    + ", ".join(reach["via_actions"])
                )
        else:
            add("    reaches: (nothing -- no action of this component touches another)")
        add("")

    add("[MEASURED] Does this partition decompose the model?")
    add(f"  graph modularity Q = {descriptor.modularity_q:.3f}")
    for criterion in descriptor.criteria:
        mark = "OK  " if criterion["met"] else "FAIL"
        add(
            f"  [{mark}] {criterion['name']}: measured {criterion['measured']}, "
            f"rule {criterion['rule']}"
        )
        add(f"         {criterion['why']}")
    add("")
    if descriptor.decomposes:
        add("  MEASURED RESULT: the partition is a cut -- every criterion above is met.")
    else:
        add("  MEASURED RESULT: this model DOES NOT DECOMPOSE under this partition.")
        add("  The descriptor states that rather than presenting a cut the model does")
        add("  not have. It does not propose a different one: naming a boundary the")
        add("  matrix does not show is the CD-01 failure mode, and a clean-looking")
        add("  architecture derived from an invented cut is worse than none.")
    if not descriptor.consumable_as_architecture:
        add("")
        add("  Consumers (the reflexion check, the implementation brief) must treat")
        add("  this as UNMAPPABLE. To have an architecture measured here, DECLARE one")
        add("  (`architecture:` in spec_manifest.yaml, or --components) -- the tool")
        add("  measures a declared partition; it never writes one for you.")
    add("")

    add("[MEASURED] State ownership -- which actions write each variable")
    width = max((len(v) for v in descriptor.variables), default=8)
    for variable in descriptor.variables:
        writers = descriptor.writers.get(variable, [])
        add(f"  {variable.ljust(width)}  {', '.join(writers) if writers else '(written by no action)'}")
    add("")
    add("[MEASURED] Single-writer violations (a variable written from >1 component)")
    if descriptor.violations is None:
        add(f"  {descriptor.violations_basis}")
    else:
        add(f"  basis: {descriptor.violations_basis}")
        if not descriptor.violations:
            add("  none: every variable is written from exactly one component.")
        for row in descriptor.violations:
            add(
                f"  {row['variable']}: written from {', '.join(row['components'])} "
                f"by {', '.join(row['writers'])}"
            )
    add("")

    add("[MEASURED] Ports -- the crossings that would become interfaces")
    if not descriptor.ports:
        add("  none: no action touches more than one component.")
    for port in descriptor.ports:
        add(f"  {port.pid}  {port.between[0]} <-> {port.between[1]}")
        add(_wrap("      crossed by: ", port.actions))
    add("")
    if descriptor.crossings:
        add("  per crossing action:")
        for row in descriptor.crossings:
            add(f"    {row['action']} crosses {', '.join(row['components'])} ({', '.join(row['ports'])})")
            for cid in row["components"]:
                reads = row["reads"].get(cid) or []
                writes = row["writes"].get(cid) or []
                add(
                    f"      {cid}: reads {', '.join(reads) if reads else '-'}"
                    f" | writes {', '.join(writes) if writes else '-'}"
                )
        add("")

    add("[MEASURED] Spanning actions -- write sets that span components")
    if not descriptor.spans:
        add("  none: no action commits state in more than one component in one step.")
    for row in descriptor.spans:
        add(f"  {row['evidence']}")
    add("")

    if reflexion_report is not None:
        from scripts.architecture_reflexion import render_report_text

        out.append(render_report_text(reflexion_report).rstrip("\n"))
        return "\n".join(out) + "\n"

    add("[MEASURED] Architecture scan verdict")
    add(f"  architecture_scan = {descriptor.architecture_scan}")
    for reason in descriptor.scan_reasons:
        add(f"    - {reason}")
    add("")
    add("  `analyze architecture` exits 0 whenever it can analyze the model. A model")
    add("  with no architecture is a FINDING, not a failure. It exits nonzero ONLY")
    add("  when the model cannot be analyzed at all (an unresolved module hierarchy),")
    add("  which is 'I could not measure this'. Nothing here blocks a close, a")
    add("  promotion, or a case generation.")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def default_cfg_for(tla_path: Path) -> Path:
    candidate = tla_path.with_suffix(".cfg")
    if candidate.is_file():
        return candidate
    return tla_path.parent / "MC.cfg"


def default_manifest_for(tla_path: Path) -> Path | None:
    candidate = tla_path.parent / "spec_manifest.yaml"
    return candidate if candidate.is_file() else None


def run(args: argparse.Namespace) -> int:
    tla_path = Path(args.tla).resolve()
    if not tla_path.is_file():
        print(f"ERROR: spec not found: {tla_path}", file=sys.stderr)
        return EXIT_USAGE
    cfg_path = Path(args.cfg).resolve() if args.cfg else default_cfg_for(tla_path)
    if not cfg_path.is_file():
        print(f"ERROR: config not found: {cfg_path}", file=sys.stderr)
        return EXIT_USAGE
    manifest_path = (
        Path(args.manifest).resolve() if args.manifest else default_manifest_for(tla_path)
    )
    components_path = (
        Path(getattr(args, "components", None)).resolve()
        if getattr(args, "components", None)
        else None
    )
    if components_path is not None and not components_path.is_file():
        print(f"ERROR: declared components file not found: {components_path}", file=sys.stderr)
        return EXIT_USAGE

    code = getattr(args, "code", None)
    map_path = getattr(args, "map_path", None)
    if bool(code) != bool(map_path):
        # Half a reflexion check is not a reflexion check. Scanning code with no
        # map would make the tool choose the boundary; a map with no code would
        # report every port absent. Both are measurements of nothing that look
        # like measurements.
        missing = "--map" if code else "--code"
        print(
            f"ERROR: the reflexion check needs both --code and --map; {missing} is missing.",
            file=sys.stderr,
        )
        return EXIT_USAGE

    try:
        descriptor = analyze(tla_path, cfg_path, manifest_path, components_path=components_path)
    except ModuleResolutionError as exc:
        # MF-030 fail-closed. The one genuine error: "I could not measure this
        # model", distinct from "this model has no architecture" (which is a
        # finding and exits 0).
        print(
            "ERROR: architecture analysis could not analyze this model -- the module "
            f"hierarchy could not be resolved:\n  {exc}",
            file=sys.stderr,
        )
        return EXIT_ANALYSIS_ERROR
    except DeclaredPartitionError as exc:
        # Unusable INPUT: the project asked for a declared partition to be
        # measured and it could not be read. Falling back to the emergent
        # clustering would silently measure something else.
        print(f"ERROR: declared component partition is unusable:\n  {exc}", file=sys.stderr)
        return EXIT_USAGE

    report = None
    if code and map_path:
        # Imported here, not at module scope: AC-02's module reads this one, and
        # the descriptor must stay usable (and importable) with no code side.
        from scripts.architecture_reflexion import (
            CodeExtractionError,
            ReflexionMapError,
            run_reflexion,
        )

        try:
            report = run_reflexion(descriptor, code, map_path)
        except (ReflexionMapError, CodeExtractionError) as exc:
            # "I could not measure this": unusable INPUT, the one nonzero exit
            # the reflexion check has. A divergent codebase exits 0.
            print(f"ERROR: the reflexion check could not be run:\n  {exc}", file=sys.stderr)
            return EXIT_USAGE

    rendered = (
        render_json(descriptor, report)
        if args.format == "json"
        else render_text(descriptor, report)
    )
    sys.stdout.write(rendered)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered, encoding="utf-8")
        print(f"wrote evidence: {out_path}", file=sys.stderr)
    return EXIT_PASS


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("tla", help="TLA+ module to analyze.")
    parser.add_argument("cfg", nargs="?", help="TLC config. Defaults to <module>.cfg or MC.cfg.")
    parser.add_argument(
        "--manifest",
        help="spec_manifest.yaml; its `architecture:` block declares the component partition.",
    )
    parser.add_argument(
        "--components",
        help=(
            "YAML file declaring the component partition (architecture: components:). "
            "DECLARED by the project, never inferred -- the tool measures the partition "
            "you name and never proposes one."
        ),
    )
    parser.add_argument(
        "--code",
        help=(
            "AC-02 reflexion check: root of the production tree to measure against this "
            "model's architecture. Requires --map."
        ),
    )
    parser.add_argument(
        "--map",
        dest="map_path",
        help=(
            "AC-02 reflexion check: YAML file declaring the production module -> model "
            "component map. DECLARED by the project, never inferred. Requires --code."
        ),
    )
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    parser.add_argument("--out", help="Also write the descriptor here (ticket results/ evidence).")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="analyze_architecture",
        description="Architecture descriptor for a constrained-profile TLA+ spec.",
    )
    add_arguments(parser)
    return run(parser.parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
