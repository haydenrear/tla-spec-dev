#!/usr/bin/env python3
"""Static complexity analysis for a constrained-profile TLA+ spec + cfg.

Mechanizes the decomposition method in ``references/modular_fuzzing.md`` and
the diagnostics in ``references/architecture_tractability.md`` so an agent has
a number to engineer against **before** TLC ever runs.

What it emits:

* the per-variable domain cardinality table (parsed from ``TypeInvariant`` and
  the ``.cfg`` constants);
* the state-space upper bound (the product of those cardinalities) and the
  dominant dimensions;
* the variables x actions read/write matrix;
* a graph-modularity score over that matrix, the near-decomposable variable
  clusters, and the candidate port-crossing actions;
* variables with no justification linkage, flagged as dead weight, when the
  manifest carries a ``justification:`` table;
* a **suggested move** -- abstract, decompose, or refactor -- which is a
  RECOMMENDATION REQUIRING USER APPROVAL and is never auto-applied; and
* a budget verdict read through :mod:`scripts.budgets` (the MF-012 helper),
  which drives a nonzero exit.

Two standing cautions are wired into the output rather than left to prose,
because both have already cost this repository real work (see MF-020):

1. **The distinct-state count is blind to deleted self-loops.** Removing an
   idempotent re-fire transition returns to an already-known state, so
   distinct states and depth do not move and a distinct-state gate sees
   nothing. ``--tlc-report``/``--baseline-tlc`` compare TLC runs and raise a
   RED FLAG when generated states drop at constant distinct states and depth.
2. **Projected reductions are unverified until the transition diff is read.**
   Every number in the output is tagged MEASURED or PROJECTED, and no
   projected figure is ever presented as a finding.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Modularity at or above this is treated as "a cut plausibly exists".
MODULARITY_CUT_THRESHOLD = 0.30

# Exit codes.
EXIT_PASS = 0
EXIT_BUDGET_EXCEEDED = 1
EXIT_USAGE = 2


# --------------------------------------------------------------------------
# TLA+ / cfg parsing (the constrained profile in references/tla_profile.md)
# --------------------------------------------------------------------------

_DEF_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(?:\(([^)]*)\))?\s*==\s*(.*)$")
_TERMINATOR_RE = re.compile(r"^====+\s*$")


def strip_comments(text: str) -> str:
    """Remove TLA+ line comments and block comments."""
    text = re.sub(r"\(\*.*?\*\)", " ", text, flags=re.DOTALL)
    out = []
    for line in text.splitlines():
        idx = line.find("\\*")
        out.append(line if idx < 0 else line[:idx])
    return "\n".join(out)


def parse_declaration_block(text: str, keyword: str) -> list[str]:
    """Parse a ``VARIABLES``/``CONSTANTS`` declaration into a name list."""
    # NOTE: horizontal whitespace only. `\s*` under re.MULTILINE would let `^`
    # anchor on an earlier blank line and swallow the newlines in between,
    # putting match.start() before the declaration.
    pattern = re.compile(rf"^[ \t]*{keyword}S?\b(.*)$", re.MULTILINE)
    match = pattern.search(text)
    if match is None:
        return []
    lines = text[match.start() :].splitlines()
    collected: list[str] = []
    first = re.sub(rf"^[ \t]*{keyword}S?\b", "", lines[0])
    buffer = [first]
    for line in lines[1:]:
        stripped = line.strip()
        if not stripped:
            if collected or any(part.strip() for part in buffer):
                break
            continue
        # A new definition or declaration ends the block.
        if _DEF_RE.match(stripped) or _TERMINATOR_RE.match(stripped):
            break
        if re.match(r"^(VARIABLE|CONSTANT|ASSUME|EXTENDS|LOCAL)", stripped):
            break
        buffer.append(stripped)
    joined = " ".join(buffer)
    for chunk in joined.split(","):
        name = chunk.strip()
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
            collected.append(name)
    return collected


@dataclass
class Definition:
    name: str
    params: list[str]
    body: str


def parse_definitions(text: str) -> list[Definition]:
    """Split a module body into top-level ``Name == body`` definitions."""
    lines = text.splitlines()
    defs: list[Definition] = []
    current: Definition | None = None
    body_lines: list[str] = []

    def flush() -> None:
        nonlocal current, body_lines
        if current is not None:
            current.body = "\n".join(body_lines)
            defs.append(current)
        current = None
        body_lines = []

    for line in lines:
        if _TERMINATOR_RE.match(line.strip()):
            flush()
            continue
        match = _DEF_RE.match(line)
        # Only a definition when it starts at column 0 (top level).
        if match and not line[:1].isspace():
            flush()
            params = [p.strip() for p in (match.group(2) or "").split(",") if p.strip()]
            current = Definition(name=match.group(1), params=params, body="")
            body_lines = [match.group(3)]
        elif current is not None:
            body_lines.append(line)
    flush()
    return defs


# --------------------------------------------------------------------------
# EXTENDS resolution (MF-030)
# --------------------------------------------------------------------------
#
# The analyzer used to read one .tla file and stop. On a decomposed model --
# the architecture SKILL.md mandates -- that scores only the declarations
# literally present in that file and silently drops everything reached through
# EXTENDS. The error is NEVER conservative: missing variables always shrink the
# product bound, so the gate fails toward PASS. MF-023 measured `External`
# reporting bound = 1 over 2 of its 9 variables for exactly this reason.
#
# The resolver below follows EXTENDS through the module hierarchy and unions
# the declarations the analyzer reads (VARIABLES, CONSTANTS, and the top-level
# definitions that carry TypeInvariant, Init, and the actions) into a single
# resolved view. What it does and does NOT handle is declared explicitly, and
# every construct it cannot model FAILS CLOSED with a named error rather than
# under-reporting -- see references/architecture_tractability.md, "No
# Degenerate Escapes": when you cannot resolve something, write the failure,
# not a smaller number.
#
# HANDLED:
#   * EXTENDS of one or more sibling modules, transitively, deduped, with the
#     extending module's own declarations overriding inherited names.
#   * EXTENDS of the standard TLA+ library modules below, which declare no
#     VARIABLES/CONSTANTS the bound reads and are skipped rather than resolved.
#
# NOT HANDLED -- each fails closed with a named error:
#   * INSTANCE / named instantiation (`Foo == INSTANCE M`) and unnamed
#     instantiation (`INSTANCE M`);
#   * substitution (`... WITH x <- y`) -- only ever appears with INSTANCE;
#   * parameterized instantiation (`I(x) == INSTANCE M WITH ...`);
#   * LOCAL definitions and LOCAL INSTANCE -- the analyzer cannot tell which
#     LOCAL names an extending module sees;
#   * an EXTENDS naming a non-standard module whose .tla file is not found.

# Standard TLA+ library modules. Extending these contributes operators (`+`,
# `Cardinality`, `Append`, ...) but declares no VARIABLES and no CONSTANTS the
# static bound reads, so they are skipped rather than resolved to a file.
# Anything NOT on this list must resolve to a real file or the analyzer fails
# closed -- silently skipping an unknown module would under-report the bound.
STANDARD_MODULES = frozenset(
    {
        "Naturals",
        "Integers",
        "Reals",
        "Sequences",
        "FiniteSets",
        "Bags",
        "TLC",
        "Json",
    }
)

_EXTENDS_RE = re.compile(r"(?m)^[ \t]*EXTENDS\b(.*)$")
_INSTANCE_RE = re.compile(r"(?<![A-Za-z0-9_])INSTANCE(?![A-Za-z0-9_])")
_LOCAL_RE = re.compile(r"(?m)^[ \t]*LOCAL(?![A-Za-z0-9_])")


class ModuleResolutionError(Exception):
    """The analyzer cannot faithfully resolve the EXTENDS hierarchy.

    Raised instead of returning a bound so the complexity gate FAILS CLOSED. An
    unresolved or unsupported hierarchy that returned a number would return a
    smaller one -- missing declarations only ever shrink the product -- which is
    the original MF-030 defect wearing a new hat. See
    references/architecture_tractability.md, "No Degenerate Escapes".
    """


class UnresolvedExtendsError(ModuleResolutionError):
    """An EXTENDS names a non-standard module whose ``.tla`` file was not found."""


class UnsupportedModuleConstructError(ModuleResolutionError):
    """A construct this static resolver does not model appears in the hierarchy.

    INSTANCE, substitution (``WITH``), parameterized instantiation, or LOCAL.
    Each changes which declarations are in scope in ways the resolver does not
    compute, so it refuses rather than under-report.
    """


def parse_extends(text: str) -> list[str]:
    """Names in every ``EXTENDS`` clause of a (comment-stripped) module."""
    names: list[str] = []
    for match in _EXTENDS_RE.finditer(text):
        for chunk in match.group(1).split(","):
            name = chunk.strip()
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
                names.append(name)
    return names


@dataclass
class ResolvedModule:
    """The union of declarations across an EXTENDS hierarchy.

    ``variables``/``constants``/``defs`` are base-first: an extended module's
    declarations precede the extending module's, and a name the extending
    module redefines overrides the inherited one.
    """

    root: str
    variables: list[str]
    constants: list[str]
    defs: list["Definition"]
    modules: list[str]
    extended_files: list[Path]


def resolve_module(
    tla_path: Path, *, _seen: set[Path] | None = None
) -> ResolvedModule:
    """Follow ``EXTENDS`` and union the declarations the analyzer reads.

    Raises :class:`ModuleResolutionError` (fails closed) on any construct it
    cannot model, rather than returning an under-reported view.
    """
    seen = _seen if _seen is not None else set()
    resolved_path = tla_path.resolve()
    if resolved_path in seen:
        raise ModuleResolutionError(
            f"cyclic EXTENDS detected at {resolved_path.name}; the module "
            "hierarchy is not a tree"
        )
    seen.add(resolved_path)

    text = strip_comments(resolved_path.read_text(encoding="utf-8"))
    module_match = re.search(r"MODULE\s+([A-Za-z0-9_]+)", text)
    module_name = module_match.group(1) if module_match else resolved_path.stem

    # Fail closed on constructs whose scoping this static resolver does not model.
    if _INSTANCE_RE.search(text):
        raise UnsupportedModuleConstructError(
            f"module {module_name} ({resolved_path.name}) uses INSTANCE "
            "(module instantiation / substitution WITH / parameterized "
            "instantiation). The complexity analyzer does not model which "
            "declarations this brings into scope and FAILS CLOSED rather than "
            "under-report the bound."
        )
    if _LOCAL_RE.search(text):
        raise UnsupportedModuleConstructError(
            f"module {module_name} ({resolved_path.name}) uses LOCAL. The "
            "analyzer cannot tell which LOCAL declarations an extending module "
            "sees and FAILS CLOSED rather than under-report the bound."
        )

    variables: list[str] = []
    constants: list[str] = []
    defs_by_name: dict[str, Definition] = {}
    modules: list[str] = []
    extended_files: list[Path] = []

    def merge(dst: list[str], names: Iterable[str]) -> None:
        for name in names:
            if name not in dst:
                dst.append(name)

    for extended in parse_extends(text):
        if extended in STANDARD_MODULES:
            continue
        candidate = resolved_path.parent / f"{extended}.tla"
        if not candidate.is_file():
            raise UnresolvedExtendsError(
                f"module {module_name} ({resolved_path.name}) EXTENDS "
                f"{extended}, but {candidate.name} was not found in "
                f"{resolved_path.parent}. The analyzer cannot union "
                "declarations from a module it cannot read and FAILS CLOSED "
                "rather than under-report the bound. If it is a library module "
                "with no VARIABLES, add it to STANDARD_MODULES once verified."
            )
        sub = resolve_module(candidate, _seen=seen)
        merge(variables, sub.variables)
        merge(constants, sub.constants)
        for definition in sub.defs:
            defs_by_name[definition.name] = definition
        merge(modules, sub.modules)
        extended_files.append(candidate)
        extended_files.extend(sub.extended_files)

    # The extending module's own declarations extend and override the inherited
    # set (TLA+ forbids redefinition, so override is only reached on collision).
    merge(variables, parse_declaration_block(text, "VARIABLE"))
    merge(constants, parse_declaration_block(text, "CONSTANT"))
    for definition in parse_definitions(text):
        defs_by_name[definition.name] = definition
    merge(modules, [module_name])

    return ResolvedModule(
        root=module_name,
        variables=variables,
        constants=constants,
        defs=list(defs_by_name.values()),
        modules=modules,
        extended_files=extended_files,
    )


def parse_cfg_constants(cfg_text: str) -> dict[str, Any]:
    """Parse ``CONSTANTS`` assignments from a TLC ``.cfg``.

    Returns a mapping of constant name to either a ``list`` (set value) or a
    string (model value).
    """
    text = strip_comments(cfg_text)
    constants: dict[str, Any] = {}
    in_block = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        upper = line.upper()
        if upper.startswith("CONSTANT"):
            in_block = True
            line = re.sub(r"^CONSTANTS?\s*", "", line, flags=re.IGNORECASE).strip()
            if not line:
                continue
        elif re.match(r"^[A-Z_]+$", line) or upper.startswith(
            ("SPECIFICATION", "INVARIANT", "PROPERT", "INIT", "NEXT", "SYMMETRY", "VIEW", "CONSTRAINT")
        ):
            in_block = False
            continue
        if not in_block:
            continue
        match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(?:<-|=)\s*(.+)$", line)
        if not match:
            continue
        name, value = match.group(1), match.group(2).strip()
        set_match = re.fullmatch(r"\{(.*)\}", value)
        if set_match:
            inner = set_match.group(1).strip()
            members = [m.strip() for m in inner.split(",") if m.strip()] if inner else []
            constants[name] = members
        else:
            constants[name] = value
    return constants


# --------------------------------------------------------------------------
# Read/write extraction
# --------------------------------------------------------------------------

_UNCHANGED_TUPLE_RE = re.compile(r"UNCHANGED\s*<<(.*?)>>", re.DOTALL)
_UNCHANGED_NAME_RE = re.compile(r"UNCHANGED\s+([A-Za-z_][A-Za-z0-9_]*)")


def strip_unchanged(body: str) -> str:
    """Remove ``UNCHANGED`` clauses -- they are neither reads nor writes."""
    body = _UNCHANGED_TUPLE_RE.sub(" ", body)
    body = _UNCHANGED_NAME_RE.sub(" ", body)
    return body


def references(body: str, name: str) -> bool:
    return re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}(?![A-Za-z0-9_'])", body) is not None


def primed_references(body: str, name: str) -> bool:
    return re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}'", body) is not None


@dataclass
class Action:
    name: str
    reads: set[str] = field(default_factory=set)
    writes: set[str] = field(default_factory=set)
    body: str = ""

    @property
    def touched(self) -> set[str]:
        return self.reads | self.writes


def extract_actions(defs: Sequence[Definition], variables: Sequence[str]) -> list[Action]:
    """An action is a top-level definition that primes at least one variable."""
    actions: list[Action] = []
    for definition in defs:
        body = strip_unchanged(definition.body)
        writes = {v for v in variables if primed_references(body, v)}
        if not writes:
            continue
        reads = {v for v in variables if references(body, v)}
        actions.append(Action(name=definition.name, reads=reads, writes=writes, body=body))
    return actions


# --------------------------------------------------------------------------
# Domain cardinality inference
# --------------------------------------------------------------------------


@dataclass
class Dimension:
    variable: str
    expression: str | None
    cardinality: int | None
    note: str = ""

    @property
    def bounded(self) -> bool:
        return self.cardinality is not None and self.cardinality > 0


def _set_size(expr: str, constants: dict[str, Any]) -> int | None:
    """Resolve the cardinality of a set-valued expression."""
    expr = expr.strip()
    if expr == "BOOLEAN":
        return 2
    literal = re.fullmatch(r"\{(.*)\}", expr, flags=re.DOTALL)
    if literal:
        inner = literal.group(1).strip()
        if not inner:
            return 0
        return len([m for m in inner.split(",") if m.strip()])
    rng = re.fullmatch(r"(-?\d+)\s*\.\.\s*(-?\d+)", expr)
    if rng:
        low, high = int(rng.group(1)), int(rng.group(2))
        return max(0, high - low + 1)
    # Union of resolvable parts.
    if "\\cup" in expr:
        total = 0
        for part in expr.split("\\cup"):
            size = _set_size(part, constants)
            if size is None:
                return None
            total += size
        return total
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", expr):
        value = constants.get(expr)
        if isinstance(value, list):
            return len(value)
        if isinstance(value, str):
            return 1
        return None
    return None


def infer_dimensions(
    type_invariant: str | None,
    variables: Sequence[str],
    constants: dict[str, Any],
) -> list[Dimension]:
    """Derive a per-variable domain cardinality from ``TypeInvariant``.

    Variables the type invariant does not constrain are reported with an
    unknown cardinality and excluded from the product, rather than silently
    assigned a convenient number.
    """
    dimensions: list[Dimension] = []
    body = type_invariant or ""
    for variable in variables:
        expression: str | None = None
        cardinality: int | None = None
        note = ""

        subset = re.search(
            rf"(?<![A-Za-z0-9_]){re.escape(variable)}\s*\\subseteq\s*([^\n]+)", body
        )
        member = re.search(
            rf"(?<![A-Za-z0-9_]){re.escape(variable)}\s*\\in\s*([^\n]+)", body
        )
        if subset:
            expression = f"SUBSET {subset.group(1).strip()}"
            base = _set_size(subset.group(1), constants)
            if base is not None:
                cardinality = 2**base
                note = f"powerset of {base} elements"
        elif member:
            raw = member.group(1).strip()
            expression = raw
            function = re.fullmatch(r"\[(.+?)\s*->\s*(.+)\]", raw, flags=re.DOTALL)
            if function:
                domain_size = _set_size(function.group(1), constants)
                range_size = _set_size(function.group(2), constants)
                if domain_size is not None and range_size is not None:
                    cardinality = range_size**domain_size
                    note = f"{range_size}^{domain_size} total functions"
            else:
                cardinality = _set_size(raw, constants)
        if cardinality is None and not note:
            note = "unconstrained by TypeInvariant -- excluded from the bound"
        dimensions.append(
            Dimension(
                variable=variable,
                expression=expression,
                cardinality=cardinality,
                note=note,
            )
        )
    return dimensions


def state_space_bound(dimensions: Iterable[Dimension]) -> int:
    bound = 1
    for dimension in dimensions:
        if dimension.bounded:
            bound *= int(dimension.cardinality or 1)
    return bound


# --------------------------------------------------------------------------
# Modularity over the R/W matrix
# --------------------------------------------------------------------------


def interaction_graph(actions: Sequence[Action], variables: Sequence[str]) -> dict[tuple[str, str], int]:
    """Weight each variable pair by the number of actions touching both."""
    weights: dict[tuple[str, str], int] = {}
    for action in actions:
        touched = sorted(action.touched & set(variables))
        for i, left in enumerate(touched):
            for right in touched[i + 1 :]:
                key = (left, right)
                weights[key] = weights.get(key, 0) + 1
    return weights


def modularity(partition: Sequence[set[str]], weights: dict[tuple[str, str], int]) -> float:
    """Newman-Girvan modularity Q of a partition of the weighted graph."""
    total = sum(weights.values())
    if total == 0:
        return 0.0
    degree: dict[str, int] = {}
    for (left, right), weight in weights.items():
        degree[left] = degree.get(left, 0) + weight
        degree[right] = degree.get(right, 0) + weight
    score = 0.0
    for community in partition:
        internal = sum(
            weight
            for (left, right), weight in weights.items()
            if left in community and right in community
        )
        attached = sum(degree.get(node, 0) for node in community)
        score += internal / total - (attached / (2 * total)) ** 2
    return score


def greedy_communities(
    variables: Sequence[str], weights: dict[tuple[str, str], int]
) -> tuple[list[set[str]], float]:
    """Greedy agglomerative modularity maximization (CNM-style).

    Deterministic: ties break on sorted community keys, so the same model
    always yields the same recommendation.
    """
    partition: list[set[str]] = [{v} for v in variables]
    best_q = modularity(partition, weights)
    if not weights:
        return partition, best_q
    improved = True
    while improved and len(partition) > 1:
        improved = False
        best_pair: tuple[int, int] | None = None
        best_gain = 0.0
        for i in range(len(partition)):
            for j in range(i + 1, len(partition)):
                connected = any(
                    (left in partition[i] and right in partition[j])
                    or (left in partition[j] and right in partition[i])
                    for (left, right) in weights
                )
                if not connected:
                    continue
                candidate = [c for k, c in enumerate(partition) if k not in (i, j)]
                candidate.append(partition[i] | partition[j])
                gain = modularity(candidate, weights) - best_q
                if gain > best_gain + 1e-12:
                    best_gain = gain
                    best_pair = (i, j)
        if best_pair is not None:
            i, j = best_pair
            merged = partition[i] | partition[j]
            partition = [c for k, c in enumerate(partition) if k not in (i, j)]
            partition.append(merged)
            best_q += best_gain
            improved = True
    partition.sort(key=lambda c: (-len(c), sorted(c)))
    return partition, best_q


def crossing_actions(
    partition: Sequence[set[str]], actions: Sequence[Action]
) -> dict[str, list[str]]:
    """Actions that touch more than one community are candidate ports."""
    crossings: dict[str, list[str]] = {}
    for action in actions:
        hit = [
            index
            for index, community in enumerate(partition)
            if action.touched & community
        ]
        if len(hit) > 1:
            crossings[action.name] = [f"C{index + 1}" for index in hit]
    return crossings


# --------------------------------------------------------------------------
# Abstraction candidates
# --------------------------------------------------------------------------


@dataclass
class OrdinalChain:
    """A set of latching booleans pinned into a total order.

    ``k`` such booleans admit only ``k + 1`` reachable combinations out of
    ``2**k``, so they represent one ordinal phase variable. This is exactly the
    shape MF-020 collapsed for the ticket lifecycle.
    """

    members: list[str]

    @property
    def combinations_declared(self) -> int:
        return 2 ** len(self.members)

    @property
    def combinations_reachable(self) -> int:
        return len(self.members) + 1


def latching_booleans(
    dimensions: Sequence[Dimension], actions: Sequence[Action], init_body: str
) -> list[str]:
    """Booleans initialized FALSE and only ever assigned TRUE."""
    booleans = {
        d.variable
        for d in dimensions
        if d.cardinality == 2 and (d.expression or "").strip() == "BOOLEAN"
    }
    latching: list[str] = []
    for name in sorted(booleans):
        if not re.search(rf"(?<![A-Za-z0-9_]){re.escape(name)}\s*=\s*FALSE", init_body):
            continue
        assignments = []
        for action in actions:
            if name not in action.writes:
                continue
            assignments.extend(
                re.findall(rf"(?<![A-Za-z0-9_]){re.escape(name)}'\s*=\s*(TRUE|FALSE)", action.body)
            )
        if assignments and all(value == "TRUE" for value in assignments):
            latching.append(name)
    return latching


def implication_chains(
    latching: Sequence[str], action_bodies: dict[str, str], actions: Sequence[Action]
) -> list[OrdinalChain]:
    """Derive ``X => Y`` from guards, then extract maximal total orders.

    If every action that sets ``X`` to TRUE requires ``Y`` positively in its
    guard, and ``Y`` latches, then ``X => Y`` holds in every reachable state.
    A set of latching booleans whose implication order is total collapses to
    one ordinal.
    """
    latching_set = set(latching)
    implies: dict[str, set[str]] = {name: set() for name in latching}
    for name in latching:
        writers = [a for a in actions if name in a.writes]
        if not writers:
            continue
        per_writer: list[set[str]] = []
        for action in writers:
            body = action_bodies.get(action.name, "")
            guard = body.split(f"{name}'")[0]
            positives = {
                other
                for other in latching_set
                if other != name
                and re.search(rf"/\\\s*{re.escape(other)}(?![A-Za-z0-9_'])", guard)
                and not re.search(rf"~\s*{re.escape(other)}(?![A-Za-z0-9_'])", guard)
            }
            per_writer.append(positives)
        common = set.intersection(*per_writer) if per_writer else set()
        implies[name] = common

    # Transitive closure.
    for _ in range(len(latching)):
        for name in latching:
            for other in list(implies[name]):
                implies[name] |= implies.get(other, set())

    remaining = set(latching)
    chains: list[OrdinalChain] = []
    while remaining:
        ordered = sorted(remaining, key=lambda n: (len(implies[n] & remaining), n))
        chain = [ordered[0]]
        for candidate in ordered[1:]:
            if all(member in implies[candidate] for member in chain):
                chain.append(candidate)
        if len(chain) >= 2:
            chains.append(OrdinalChain(members=chain))
        remaining -= set(chain)
        if len(chain) == 1:
            continue
    return chains


def projectable_variables(
    variables: Sequence[str], invariant_bodies: dict[str, str], dimensions: Sequence[Dimension]
) -> list[str]:
    """Variables no invariant reads -- Move 1 projection candidates."""
    read_by_invariant: set[str] = set()
    for body in invariant_bodies.values():
        for variable in variables:
            if references(body, variable):
                read_by_invariant.add(variable)
    return [v for v in variables if v not in read_by_invariant]


# --------------------------------------------------------------------------
# TLC report comparison (the self-loop blindness check)
# --------------------------------------------------------------------------


@dataclass
class TlcReport:
    generated: int | None = None
    distinct: int | None = None
    depth: int | None = None

    @property
    def complete(self) -> bool:
        return None not in (self.generated, self.distinct, self.depth)


def parse_tlc_report(text: str) -> TlcReport:
    report = TlcReport()
    counts = re.search(r"([\d,]+)\s+states generated,\s*([\d,]+)\s+distinct states found", text)
    if counts:
        report.generated = int(counts.group(1).replace(",", ""))
        report.distinct = int(counts.group(2).replace(",", ""))
    depth = re.search(r"depth of the complete state graph search is\s+(\d+)", text)
    if depth:
        report.depth = int(depth.group(1))
    return report


def compare_tlc_reports(baseline: TlcReport, current: TlcReport) -> list[dict[str, str]]:
    """Detect the failure mode a distinct-state gate cannot see.

    A generated-states drop at constant distinct states and constant depth
    means transitions were removed without removing any state -- typically a
    deleted self-loop, i.e. a real behavior change wearing the costume of a
    re-representation. That is a RED FLAG, never a win.
    """
    findings: list[dict[str, str]] = []
    if not (baseline.complete and current.complete):
        findings.append(
            {
                "level": "NOTE",
                "message": "TLC reports incomplete; comparison skipped.",
            }
        )
        return findings
    same_states = baseline.distinct == current.distinct and baseline.depth == current.depth
    if current.generated < baseline.generated and same_states:
        findings.append(
            {
                "level": "RED FLAG",
                "message": (
                    f"generated states dropped {baseline.generated} -> {current.generated} "
                    f"while distinct states ({current.distinct}) and depth ({current.depth}) "
                    "are unchanged. A distinct-state gate is STRUCTURALLY BLIND to this: "
                    "removing a self-loop returns to an already-known state. Inspect the "
                    "transition-level diff before recording any reduction -- an idempotent "
                    "re-fire transition may have been deleted (behavior change), not "
                    "re-represented. See MF-020."
                ),
            }
        )
    elif current.generated < baseline.generated:
        findings.append(
            {
                "level": "INFO",
                "message": (
                    f"generated states {baseline.generated} -> {current.generated} with "
                    f"distinct {baseline.distinct} -> {current.distinct} and depth "
                    f"{baseline.depth} -> {current.depth}. State-level change accompanies the "
                    "transition-level change; still confirm against the transition diff."
                ),
            }
        )
    else:
        findings.append(
            {
                "level": "OK",
                "message": (
                    f"generated {baseline.generated} -> {current.generated}, distinct "
                    f"{baseline.distinct} -> {current.distinct}, depth {baseline.depth} -> "
                    f"{current.depth}. No self-loop-deletion signature."
                ),
            }
        )
    return findings


# --------------------------------------------------------------------------
# Analysis assembly
# --------------------------------------------------------------------------


@dataclass
class Analysis:
    module: str
    tla_path: Path
    cfg_path: Path
    manifest_path: Path | None
    constants: dict[str, Any]
    variables: list[str]
    dimensions: list[Dimension]
    actions: list[Action]
    bound: int
    unbounded: list[str]
    communities: list[set[str]]
    modularity_score: float
    crossings: dict[str, list[str]]
    chains: list[OrdinalChain]
    projectable: list[str]
    unjustified: list[str] | None
    budgets: dict[str, Any]
    violations: list[str]
    tlc_findings: list[dict[str, str]]

    @property
    def projected_bound(self) -> int:
        """Bound after the projected abstractions -- PROJECTED, not measured."""
        bound = self.bound
        for chain in self.chains:
            bound = bound // chain.combinations_declared * chain.combinations_reachable
        return bound

    @property
    def gate_passed(self) -> bool:
        return not self.violations


def load_justification(manifest: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(manifest, dict):
        return None
    table = manifest.get("justification")
    return table if isinstance(table, dict) else None


def unjustified_variables(
    variables: Sequence[str], table: dict[str, Any] | None
) -> list[str] | None:
    """Variables with no invariant, effect, or kill-test linkage."""
    if table is None:
        return None
    flagged: list[str] = []
    for variable in variables:
        entry = table.get(variable)
        if not isinstance(entry, dict):
            flagged.append(variable)
            continue
        linked = False
        for key in ("invariants", "effects", "kill_tests"):
            value = entry.get(key)
            if isinstance(value, (list, tuple)) and any(str(v).strip() for v in value):
                linked = True
        if not linked:
            flagged.append(variable)
    return flagged


def analyze(
    tla_path: Path,
    cfg_path: Path,
    manifest_path: Path | None,
    *,
    baseline_tlc: Path | None = None,
    current_tlc: Path | None = None,
    warn_stream: Any = None,
) -> Analysis:
    from scripts.budgets import load_budgets

    cfg_text = cfg_path.read_text(encoding="utf-8")

    # MF-030: follow EXTENDS and union declarations across the module hierarchy.
    # On a single-file spec that extends only standard library modules this is
    # identical to reading the one file; on a decomposed model it recovers the
    # variables, TypeInvariant, and actions the extended modules contribute.
    # resolve_module raises ModuleResolutionError (fails closed) on any
    # construct it cannot model -- callers must not swallow it into a bound.
    resolved = resolve_module(tla_path)
    module = resolved.root
    variables = resolved.variables
    constants = parse_cfg_constants(cfg_text)
    defs = resolved.defs
    by_name = {d.name: d for d in defs}

    actions = extract_actions(defs, variables)
    action_bodies = {a.name: a.body for a in actions}

    type_invariant = by_name["TypeInvariant"].body if "TypeInvariant" in by_name else None
    dimensions = infer_dimensions(type_invariant, variables, constants)
    bound = state_space_bound(dimensions)
    unbounded = [d.variable for d in dimensions if not d.bounded]

    weights = interaction_graph(actions, variables)
    communities, score = greedy_communities(variables, weights)
    crossings = crossing_actions(communities, actions)

    init_body = by_name["Init"].body if "Init" in by_name else ""
    latching = latching_booleans(dimensions, actions, init_body)
    chains = implication_chains(latching, action_bodies, actions)

    invariant_names = parse_cfg_invariants(cfg_text)
    invariant_bodies = {
        name: by_name[name].body for name in invariant_names if name in by_name
    }
    projectable = projectable_variables(variables, invariant_bodies, dimensions)

    manifest: dict[str, Any] | None = None
    if manifest_path and manifest_path.is_file():
        try:
            from scripts.extract_spec_manifest import load_manifest

            manifest = load_manifest(manifest_path)
        except Exception:
            manifest = None
    unjustified = unjustified_variables(variables, load_justification(manifest))

    budgets = load_budgets(
        manifest_path if manifest_path else Path("does-not-exist"),
        warn=True,
        stream=warn_stream if warn_stream is not None else sys.stderr,
    )

    violations: list[str] = []
    # MF-022: the static bound is a Cartesian over-approximation of the
    # DECLARED representation -- it ignores every action guard, so it counts
    # combinations the program can never occupy. It is therefore gated against
    # max_state_space_bound (a TLC-capacity ceiling), NOT against
    # max_distinct_states, which caps ACTUAL reachable states measured by TLC
    # after the fact. Comparing the two is a category error: on this
    # repository the bound over-approximated reachable states by ~400x, failing
    # a model that was 17x under its own reachable-state budget.
    if bound > budgets["max_state_space_bound"]:
        violations.append(
            f"state-space upper bound {bound:,} exceeds max_state_space_bound "
            f"{budgets['max_state_space_bound']:,}"
        )
    for index, community in enumerate(communities, start=1):
        if len(community) > budgets["max_component_variables"]:
            violations.append(
                f"component C{index} has {len(community)} variables, exceeding "
                f"max_component_variables {budgets['max_component_variables']}"
            )
    for index, community in enumerate(communities, start=1):
        touching = [a.name for a in actions if a.touched & community]
        if len(touching) > budgets["max_component_actions"]:
            violations.append(
                f"component C{index} is touched by {len(touching)} actions, exceeding "
                f"max_component_actions {budgets['max_component_actions']}"
            )

    tlc_findings: list[dict[str, str]] = []
    if current_tlc is not None and current_tlc.is_file():
        current_report = parse_tlc_report(current_tlc.read_text(encoding="utf-8"))
        if baseline_tlc is not None and baseline_tlc.is_file():
            baseline_report = parse_tlc_report(baseline_tlc.read_text(encoding="utf-8"))
            tlc_findings = compare_tlc_reports(baseline_report, current_report)
        elif current_report.complete:
            tlc_findings = [
                {
                    "level": "INFO",
                    "message": (
                        f"TLC measured {current_report.generated} generated / "
                        f"{current_report.distinct} distinct / depth {current_report.depth}. "
                        "Pass --baseline-tlc to check for the self-loop-deletion signature."
                    ),
                }
            ]
        # MF-022: max_distinct_states caps ACTUAL reachable states, so it can
        # only be checked once TLC has measured them (--tlc-report). This is the
        # comparison the budget was always for; before MF-022 it was applied
        # to the static over-approximation instead.
        if current_report.complete and current_report.distinct is not None:
            if current_report.distinct > budgets["max_distinct_states"]:
                violations.append(
                    f"TLC-measured {current_report.distinct:,} distinct reachable states "
                    f"exceeds max_distinct_states {budgets['max_distinct_states']:,}"
                )
            else:
                tlc_findings.append(
                    {
                        "level": "INFO",
                        "message": (
                            f"TLC-measured {current_report.distinct:,} distinct reachable "
                            f"states is within max_distinct_states "
                            f"{budgets['max_distinct_states']:,}."
                        ),
                    }
                )

    return Analysis(
        module=module,
        tla_path=tla_path,
        cfg_path=cfg_path,
        manifest_path=manifest_path,
        constants=constants,
        variables=variables,
        dimensions=dimensions,
        actions=actions,
        bound=bound,
        unbounded=unbounded,
        communities=communities,
        modularity_score=score,
        crossings=crossings,
        chains=chains,
        projectable=projectable,
        unjustified=unjustified,
        budgets=budgets,
        violations=violations,
        tlc_findings=tlc_findings,
    )


def parse_cfg_invariants(cfg_text: str) -> list[str]:
    text = strip_comments(cfg_text)
    names: list[str] = []
    in_block = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if re.match(r"^INVARIANTS?\b", line, flags=re.IGNORECASE):
            in_block = True
            rest = re.sub(r"^INVARIANTS?\s*", "", line, flags=re.IGNORECASE).strip()
            if rest:
                names.append(rest)
            continue
        if re.match(r"^[A-Z]+\b", line) and not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", line):
            in_block = False
            continue
        if in_block:
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", line):
                names.append(line)
            else:
                in_block = False
    return names


# --------------------------------------------------------------------------
# Suggested move (RECOMMENDATION -- requires user approval)
# --------------------------------------------------------------------------


def suggest_move(analysis: Analysis) -> dict[str, Any]:
    """Choose among the three moves and return evidence, never a verdict.

    Order follows ``references/architecture_tractability.md``: try to change
    the representation (abstract) before cutting (decompose) before asking for
    a production change (refactor).
    """
    evidence: list[str] = []
    projected: list[str] = []

    if analysis.chains or analysis.projectable:
        move = "ABSTRACT"
        rationale = (
            "The representation carries dimensions the reachable state space does not use."
        )
        for chain in analysis.chains:
            members = ", ".join(chain.members)
            evidence.append(
                f"latching booleans [{members}] are pinned into a total order by their own "
                f"action guards, so only {chain.combinations_reachable} of "
                f"{chain.combinations_declared} combinations are reachable"
            )
            projected.append(
                f"collapsing [{members}] into one ordinal 0..{len(chain.members)} would take "
                f"the model from {len(analysis.variables)} to "
                f"{len(analysis.variables) - len(chain.members) + 1} variables and the declared "
                f"bound from {analysis.bound:,} to "
                f"{analysis.bound // chain.combinations_declared * chain.combinations_reachable:,}; "
                "reachable states should be UNCHANGED -- verify with TLC, and treat a "
                "generated-states drop at constant distinct states as a red flag"
            )
        if analysis.projectable:
            names = ", ".join(analysis.projectable)
            evidence.append(
                f"no configured invariant reads [{names}]; Move 1 permits projecting "
                "variables no invariant reads"
            )
            projected.append(
                f"projecting [{names}] removes them from the model; legitimate IFF the "
                "mutation kill rate holds afterwards (tickets/016)"
            )
    elif analysis.modularity_score >= MODULARITY_CUT_THRESHOLD and len(analysis.communities) > 1:
        move = "DECOMPOSE"
        rationale = (
            f"The R/W matrix has modular structure (Q={analysis.modularity_score:.3f} >= "
            f"{MODULARITY_CUT_THRESHOLD}); a narrow cut exists and can be named."
        )
        for index, community in enumerate(analysis.communities, start=1):
            evidence.append(f"candidate component C{index}: {', '.join(sorted(community))}")
        if analysis.crossings:
            evidence.append(
                "candidate port-crossing actions: "
                + ", ".join(f"{name} ({'/'.join(where)})" for name, where in sorted(analysis.crossings.items()))
            )
        projected.append(
            "replacing each port's far side with a contract environment makes component "
            "state spaces add instead of multiply"
        )
    else:
        move = "REFACTOR"
        rationale = (
            f"No projectable dimension and no narrow cut (Q={analysis.modularity_score:.3f} < "
            f"{MODULARITY_CUT_THRESHOLD}). The failed search is itself the architecture finding."
        )
        action_count = {v: 0 for v in analysis.variables}
        for action in analysis.actions:
            for variable in action.touched:
                action_count[variable] += 1
        dense_rows = sorted(
            (v for v in analysis.variables if action_count[v] > len(analysis.actions) / 2),
            key=lambda v: (-action_count[v], v),
        )
        dense_cols = sorted(
            (a.name for a in analysis.actions if len(a.touched) > len(analysis.variables) / 2),
        )
        if dense_rows:
            evidence.append(
                "dense rows (god-state): "
                + ", ".join(f"{v} touched by {action_count[v]}/{len(analysis.actions)} actions" for v in dense_rows)
            )
        if dense_cols:
            evidence.append("dense columns (actions touching almost everything): " + ", ".join(dense_cols))
        projected.append(
            "target shapes: functional core / imperative shell, single-writer state, "
            "explicit commit points, explicit protocol state"
        )

    return {
        "move": move,
        "status": "RECOMMENDATION -- REQUIRES USER APPROVAL, NOT AUTO-APPLIED",
        "rationale": rationale,
        "evidence_measured": evidence,
        "gain_projected": projected,
    }


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------


def _table(rows: Sequence[Sequence[str]], headers: Sequence[str]) -> str:
    widths = [len(h) for h in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))
    lines = ["  ".join(h.ljust(widths[i]) for i, h in enumerate(headers)).rstrip()]
    lines.append("  ".join("-" * widths[i] for i in range(len(headers))))
    for row in rows:
        lines.append("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)).rstrip())
    return "\n".join(lines)


def render_text(analysis: Analysis) -> str:
    out: list[str] = []
    add = out.append

    add(f"analyze complexity -- {analysis.module}")
    add(f"  spec:     {analysis.tla_path}")
    add(f"  config:   {analysis.cfg_path}")
    add(f"  manifest: {analysis.manifest_path or '(none)'}")
    add("")
    add("LEGEND: [MEASURED] parsed from this spec + cfg. [PROJECTED] an estimate that is")
    add("        UNVERIFIED until the transition-level diff is read and TLC is rerun.")
    add("")

    add("[MEASURED] Dimension table")
    rows = [
        (
            d.variable,
            d.expression or "(unconstrained)",
            f"{d.cardinality:,}" if d.bounded else "unknown",
            d.note,
        )
        for d in analysis.dimensions
    ]
    add(_table(rows, ("variable", "domain", "cardinality", "note")))
    add("")

    add("[MEASURED] State-space upper bound")
    add(f"  bound = {analysis.bound:,}  (product of {len(analysis.variables) - len(analysis.unbounded)} bounded dimensions)")
    if analysis.unbounded:
        add(f"  excluded (unconstrained by TypeInvariant): {', '.join(analysis.unbounded)}")
    dominant = sorted(
        (d for d in analysis.dimensions if d.bounded),
        key=lambda d: -(d.cardinality or 0),
    )[:3]
    if dominant and analysis.bound > 1:
        add("  dominant dimensions:")
        for d in dominant:
            share = math.log(d.cardinality or 1) / math.log(analysis.bound) * 100
            add(f"    {d.variable}: {d.cardinality:,} ({share:.1f}% of the bound in log space)")
    add("")

    add("[MEASURED] Variables x actions read/write matrix")
    header = ["variable"] + [a.name for a in analysis.actions]
    matrix_rows = []
    for variable in analysis.variables:
        row = [variable]
        for action in analysis.actions:
            read = variable in action.reads
            write = variable in action.writes
            row.append("rw" if read and write else "w" if write else "r" if read else ".")
        matrix_rows.append(row)
    add(_table(matrix_rows, header))
    add("")

    add("[MEASURED] Near-decomposability")
    add(f"  graph modularity Q = {analysis.modularity_score:.3f} over the variable interaction graph")
    add(f"  (weight of an edge = number of actions touching both variables)")
    for index, community in enumerate(analysis.communities, start=1):
        touching = [a.name for a in analysis.actions if a.touched & community]
        add(f"  C{index}: {', '.join(sorted(community))}  ({len(community)} variables, {len(touching)} actions)")
    if analysis.crossings:
        add("  candidate port-crossing actions:")
        for name, where in sorted(analysis.crossings.items()):
            add(f"    {name} crosses {', '.join(where)}")
    else:
        add("  no port-crossing actions (single component, or fully independent components)")
    add("")

    add("[MEASURED] Justification linkage")
    if analysis.unjustified is None:
        add("  no justification: table in the manifest -- dead-weight analysis skipped.")
        add("  Add one to make every variable's right to exist auditable")
        add("  (references/architecture_tractability.md, 'Grow The Model By Evidence').")
    elif analysis.unjustified:
        add("  DEAD WEIGHT -- variables with no invariant, effect, or kill-test linkage:")
        for variable in analysis.unjustified:
            add(f"    {variable}")
    else:
        add("  every variable has a recorded justification linkage.")
    add("")

    if analysis.tlc_findings:
        add("[MEASURED] TLC transition-level diagnostics")
        for finding in analysis.tlc_findings:
            add(f"  {finding['level']}: {finding['message']}")
        add("")

    suggestion = suggest_move(analysis)
    add("=" * 78)
    add(f"SUGGESTED MOVE: {suggestion['move']}")
    add(suggestion["status"])
    add("=" * 78)
    add(f"  {suggestion['rationale']}")
    if suggestion["evidence_measured"]:
        add("  [MEASURED] evidence:")
        for item in suggestion["evidence_measured"]:
            add(f"    - {item}")
    if suggestion["gain_projected"]:
        add("  [PROJECTED] gain -- UNVERIFIED, requires the transition diff and a TLC rerun:")
        for item in suggestion["gain_projected"]:
            add(f"    - {item}")
    add("")
    add("  A poor score is not a verdict. Some components score badly and still need to")
    add("  exist in that form -- performance paths, protocol-mandated shapes, irreducible")
    add("  domain complexity. This output is evidence for the owner, not a decision.")
    add("  Before recording ANY projected reduction as a result: read the transition-level")
    add("  diff. A generated-states drop at constant distinct states is a RED FLAG (a")
    add("  deleted self-loop), not a win -- the distinct-state gate cannot see it.")
    add("")

    add("[MEASURED] Budget gate")
    add(f"  source: {analysis.manifest_path or 'documented defaults'}")
    for key in (
        "max_state_space_bound",
        "max_distinct_states",
        "max_component_variables",
        "max_component_actions",
    ):
        add(f"    {key}: {analysis.budgets[key]:,}")
    add("  max_state_space_bound gates the STATIC declared-representation bound above.")
    add("  max_distinct_states caps ACTUAL reachable states and is checked only once")
    add("  TLC has measured them (--tlc-report); the two are not interchangeable.")
    if analysis.gate_passed:
        add("  VERDICT: PASS -- the model is within budget.")
    else:
        add("  VERDICT: FAIL -- budget exceeded:")
        for violation in analysis.violations:
            add(f"    - {violation}")
        add("  Case generation will refuse to run against this model.")
        add("  Override explicitly with --allow-over-budget once the cost is understood.")
    return "\n".join(out) + "\n"


def render_json(analysis: Analysis) -> str:
    payload = {
        "module": analysis.module,
        "spec": str(analysis.tla_path),
        "cfg": str(analysis.cfg_path),
        "manifest": str(analysis.manifest_path) if analysis.manifest_path else None,
        "measured": {
            "dimensions": [
                {
                    "variable": d.variable,
                    "domain": d.expression,
                    "cardinality": d.cardinality,
                    "note": d.note,
                }
                for d in analysis.dimensions
            ],
            "state_space_upper_bound": analysis.bound,
            "unbounded_variables": analysis.unbounded,
            "actions": [
                {"name": a.name, "reads": sorted(a.reads), "writes": sorted(a.writes)}
                for a in analysis.actions
            ],
            "modularity": analysis.modularity_score,
            "components": [sorted(c) for c in analysis.communities],
            "port_crossing_actions": analysis.crossings,
            "unjustified_variables": analysis.unjustified,
            "tlc_findings": analysis.tlc_findings,
        },
        "projected": {
            "bound_after_suggested_abstractions": analysis.projected_bound,
            "verified": False,
            "caveat": (
                "PROJECTED figures are unverified until the transition-level diff is read "
                "and TLC is rerun. A generated-states drop at constant distinct states is a "
                "RED FLAG (deleted self-loop), not a reduction."
            ),
        },
        "suggested_move": suggest_move(analysis),
        "budgets": {
            key: analysis.budgets[key]
            for key in (
                "max_state_space_bound",
                "max_distinct_states",
                "max_component_variables",
                "max_component_actions",
            )
        },
        "gate": {
            "passed": analysis.gate_passed,
            "violations": analysis.violations,
        },
    }
    return json.dumps(payload, indent=2, sort_keys=False) + "\n"


# --------------------------------------------------------------------------
# Gate helper used by case generation
# --------------------------------------------------------------------------


def gate_report(tla_path: Path, cfg_path: Path, manifest_path: Path | None) -> tuple[bool, str]:
    """Run the gate for case generation. Returns ``(passed, message)``."""
    try:
        analysis = analyze(tla_path, cfg_path, manifest_path)
    except ModuleResolutionError as exc:
        # MF-030: a hierarchy the analyzer cannot resolve fails the gate. It is
        # NOT scored on the declarations that happen to be present, because that
        # number would only ever be smaller than the truth (missing variables
        # shrink the product) -- the gate would fail toward PASS.
        return False, (
            "complexity gate FAIL -- the module hierarchy could not be "
            "resolved, so the model cannot be measured:\n"
            f"  {exc}\n"
            "Failing closed: an unresolved hierarchy would under-report the "
            "bound and pass a model that was never measured."
        )
    if analysis.gate_passed:
        return True, (
            f"complexity gate PASS: state-space upper bound {analysis.bound:,} within "
            f"max_state_space_bound {analysis.budgets['max_state_space_bound']:,}"
        )
    lines = [
        "complexity gate FAIL -- this model exceeds its manifest budgets and would",
        "likely exhaust TLC rather than finish.",
        "",
    ]
    for violation in analysis.violations:
        lines.append(f"  - {violation}")
    lines.append("")
    lines.append("Dominant dimensions:")
    dominant = sorted(
        (d for d in analysis.dimensions if d.bounded), key=lambda d: -(d.cardinality or 0)
    )[:5]
    for d in dominant:
        lines.append(f"  {d.variable}: {d.cardinality:,}  ({d.expression})")
    suggestion = suggest_move(analysis)
    lines.append("")
    lines.append(f"Suggested move: {suggestion['move']} ({suggestion['status']})")
    for item in suggestion["evidence_measured"]:
        lines.append(f"  - {item}")
    lines.append("")
    lines.append("Run `tla-spec-dev analyze complexity <spec> <cfg>` for the full report.")
    return False, "\n".join(lines)


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
    manifest_path = Path(args.manifest).resolve() if args.manifest else default_manifest_for(tla_path)

    try:
        analysis = analyze(
            tla_path,
            cfg_path,
            manifest_path,
            baseline_tlc=Path(args.baseline_tlc).resolve() if args.baseline_tlc else None,
            current_tlc=Path(args.tlc_report).resolve() if args.tlc_report else None,
        )
    except ModuleResolutionError as exc:
        # MF-030: fail closed (nonzero) with the named reason rather than crash
        # or emit an under-reported number.
        print(
            "ERROR: complexity analysis FAILED CLOSED -- the module hierarchy "
            f"could not be resolved:\n  {exc}",
            file=sys.stderr,
        )
        return EXIT_BUDGET_EXCEEDED

    rendered = render_json(analysis) if args.format == "json" else render_text(analysis)
    sys.stdout.write(rendered)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered, encoding="utf-8")
        print(f"wrote evidence: {out_path}", file=sys.stderr)
    return EXIT_PASS if analysis.gate_passed else EXIT_BUDGET_EXCEEDED


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("tla", help="TLA+ module to analyze.")
    parser.add_argument("cfg", nargs="?", help="TLC config. Defaults to <module>.cfg or MC.cfg.")
    parser.add_argument("--manifest", help="spec_manifest.yaml carrying budgets: and justification:.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format.")
    parser.add_argument("--out", help="Also write the report here (ticket results/ evidence).")
    parser.add_argument("--tlc-report", help="TLC output for this model, for transition-level diagnostics.")
    parser.add_argument("--baseline-tlc", help="Baseline TLC output to compare against (self-loop check).")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="analyze_complexity",
        description="Static complexity analysis and budget gate for a constrained-profile TLA+ spec.",
    )
    add_arguments(parser)
    return run(parser.parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
