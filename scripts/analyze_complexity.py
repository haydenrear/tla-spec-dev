#!/usr/bin/env python3
"""The complexity DESCRIPTOR for a constrained-profile TLA+ spec + cfg.

A factual pass-through for TLA+ complexity: it measures the model and reports
what is there, so an agent has numbers to reason from **before** TLC ever
runs. Facts, not judgment -- it never suggests an architectural move (CD-01;
the earlier suggested-move machinery was confidently wrong on standard TLA+
and was removed; suggestions may return later, earned from real-app
observations).

What it emits:

* the per-variable domain cardinality table (parsed from
  ``TypeInvariant``/``TypeOK`` or, when neither exists, the transitively
  resolved bodies of the cfg-configured invariants) plus the ``.cfg``
  constants;
* the state-space upper bound (the product of those cardinalities) and the
  dominant dimensions -- or an EXPLICIT "unknown" when no variable domain
  could be resolved, never a silent 1;
* the variables x actions read/write matrix;
* a graph-modularity score over that matrix, the near-decomposable variable
  clusters, and the candidate port-crossing actions;
* dense rows (god-state variables touched by most actions) and dense columns
  (actions touching most variables);
* variables no configured invariant reads -- with invariant aliasing and
  composition (``INVARIANT Inv`` with ``Inv == RealInv``) resolved
  transitively;
* variables with no justification linkage, flagged as dead weight, when the
  manifest carries a ``justification:`` table; and
* **advisory complexity warnings** read against the thresholds in
  :mod:`scripts.budgets` (the MF-012 helper). Each threshold breach becomes a
  WARNING that names the component/variable/action and states the measured
  fact. It NEVER drives a nonzero exit and NEVER blocks promotion (MF-036;
  references/architecture_tractability.md, "Advisory, Not Blocking"). The scan
  exits nonzero only when it *cannot analyze* the model at all -- an unresolved
  module hierarchy (MF-030 fail-closed) or a usage error -- which is a
  different thing from "this model is complex".
* **self-configured fitness functions** (CD-03): when the project's agent has
  written rules over the descriptor's facts (``fitness_functions:`` in the
  manifest or a sibling ``fitness_functions.yaml``), each rule whose condition
  does not hold FIRES and is surfaced here so future agents are notified.
  There are NO built-in rules and firings are advisory -- they report, never
  block, and never change the exit code. See
  :mod:`scripts.fitness_functions` and ``references/fitness_functions.md``.

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

# Exit codes.
EXIT_PASS = 0
# MF-036: this is the "I could not analyze this model" exit, NOT "this model is
# complex". A complex model now exits EXIT_PASS with advisory warnings; only an
# unresolvable module hierarchy (MF-030 fail-closed) reaches here. The old name
# is retained for import compatibility.
EXIT_ANALYSIS_ERROR = 1
EXIT_BUDGET_EXCEEDED = EXIT_ANALYSIS_ERROR
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


def strip_frame_conditions(body: str, variables: Iterable[str]) -> str:
    """Remove explicit ``v' = v`` frame-condition conjuncts (MF-036).

    ``v' = v`` says the action leaves ``v`` UNCHANGED -- it is the written-out
    form of ``UNCHANGED v`` and is neither a read nor a write of ``v``. Counting
    it as a touch inflates the R/W matrix: every variable an action leaves alone
    then shows as coupled to it, over-reporting the god-state. A probe's
    5-variable / 10-command CLI (each command touching only two variables, the
    rest pinned with ``v' = v``) reported a fully-coupled 10/10 component that
    was almost entirely frame conditions.

    Only an EXACT frame condition is removed: the right-hand side must be the
    bare variable, ending at a conjunction/disjunction boundary or the end of
    the body. ``v' = v + 1`` and ``v' = v \\cup {x}`` genuinely read the old
    value of ``v`` and are left intact, so a real write-that-reads is never
    silenced.
    """
    for name in variables:
        escaped = re.escape(name)
        body = re.sub(
            rf"(?<![A-Za-z0-9_]){escaped}'\s*=\s*{escaped}(?=\s*(?:/\\|\\/|$))",
            " ",
            body,
        )
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
        # MF-036: strip BOTH forms of "leaves it alone" -- the UNCHANGED clause
        # and the explicit ``v' = v`` frame condition -- before reads/writes are
        # extracted, so a variable an action does not touch is not counted as
        # coupled to it.
        body = strip_frame_conditions(strip_unchanged(definition.body), variables)
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
    source_label: str = "TypeInvariant",
) -> list[Dimension]:
    """Derive a per-variable domain cardinality from the domain source text.

    The source is ``TypeInvariant``/``TypeOK`` when the module defines one, or
    the transitively resolved cfg-invariant bodies otherwise (CD-01, F3).
    Variables the source does not constrain are reported with an unknown
    cardinality and excluded from the product, rather than silently assigned a
    convenient number.
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
            note = f"unconstrained by {source_label} -- excluded from the bound"
        dimensions.append(
            Dimension(
                variable=variable,
                expression=expression,
                cardinality=cardinality,
                note=note,
            )
        )
    return dimensions


def state_space_bound(dimensions: Iterable[Dimension]) -> int | None:
    """Product of the bounded dimensions, or ``None`` when there are none.

    CD-01 (F3): with no resolvable domain the old code returned a silent 1 --
    a meaningless headline number. ``None`` means UNKNOWN and is rendered as
    such, never as 1.
    """
    bounded = [d for d in dimensions if d.bounded]
    if not bounded:
        return None
    bound = 1
    for dimension in bounded:
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
# Invariant resolution and invariant-read analysis
# --------------------------------------------------------------------------


def resolve_definition_body(
    name: str, defs_by_name: dict[str, "Definition"], _seen: set[str] | None = None
) -> str:
    """The body of ``name`` with every referenced definition expanded, transitively.

    CD-01 (F1): ``INVARIANT Inv`` with ``Inv == RealInv`` is standard TLA+ --
    invariant aliasing and composition. Reading only the immediate body of the
    cfg-named invariant sees a one-token alias with no variable names in it, so
    every variable was judged "read by no invariant". This helper follows every
    definition reference in the body (and onward, with a cycle guard) so the
    resolved text contains the variables the invariant actually reads.
    """
    seen = _seen if _seen is not None else set()
    if name in seen or name not in defs_by_name:
        return ""
    seen.add(name)
    body = defs_by_name[name].body
    parts = [body]
    for token in sorted(set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", body))):
        if token not in seen and token in defs_by_name:
            parts.append(resolve_definition_body(token, defs_by_name, seen))
    return "\n".join(parts)


def invariant_unread_variables(
    variables: Sequence[str], invariant_bodies: dict[str, str]
) -> list[str]:
    """Variables no configured invariant reads -- a fact, not a recommendation.

    ``invariant_bodies`` must be TRANSITIVELY RESOLVED bodies (see
    :func:`resolve_definition_body`) or aliased/composed invariants will make
    every variable appear unread (the F1 defect).
    """
    read_by_invariant: set[str] = set()
    for body in invariant_bodies.values():
        for variable in variables:
            if references(body, variable):
                read_by_invariant.add(variable)
    return [v for v in variables if v not in read_by_invariant]


def dense_rows_and_columns(
    variables: Sequence[str], actions: Sequence[Action]
) -> tuple[dict[str, int], list[str]]:
    """Dense rows (god-state variables) and dense columns of the R/W matrix.

    A dense row is a variable touched by more than half the actions -- the
    god-state signature. A dense column is an action touching more than half
    the variables. Both are measured facts of the matrix, reported as part of
    the descriptor.
    """
    action_count = {v: 0 for v in variables}
    for action in actions:
        for variable in action.touched:
            if variable in action_count:
                action_count[variable] += 1
    dense_rows = {
        v: action_count[v]
        for v in sorted(variables, key=lambda v: (-action_count[v], v))
        if actions and action_count[v] > len(actions) / 2
    }
    dense_cols = sorted(
        a.name for a in actions if variables and len(a.touched) > len(variables) / 2
    )
    return dense_rows, dense_cols


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
class Advisory:
    """One advisory complexity finding: what and where it is.

    MF-036: complexity is a scanner, not a gate
    (references/architecture_tractability.md, "Advisory, Not Blocking"). Each
    Advisory is a WARNING that NEVER blocks promotion. ``finding`` names the
    component / variable / action and the measured threshold breach -- a fact.
    CD-01 removed the ``recommendation`` field with the rest of the
    suggested-move machinery: the descriptor states facts and the owner
    decides what, if anything, to do about them.
    """

    kind: str
    finding: str


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
    bound: int | None
    bound_source: str | None
    unbounded: list[str]
    communities: list[set[str]]
    modularity_score: float
    crossings: dict[str, list[str]]
    dense_rows: dict[str, int]
    dense_columns: list[str]
    unread_by_invariant: list[str]
    unjustified: list[str] | None
    budgets: dict[str, Any]
    warnings: list[Advisory]
    tlc_findings: list[dict[str, str]]
    # CD-03: the project's self-configured fitness functions, evaluated over
    # this descriptor. None when the project configured nothing -- there are NO
    # built-in rules. Firings are advisory: they are surfaced in the report and
    # NEVER change the exit code or block promotion.
    fitness: Any = None

    @property
    def violations(self) -> list[str]:
        """The advisory finding strings.

        Retained under this name so the complexity ledger (out of MF-036's
        scope) keeps recording the findings. Since MF-036 these are WARNINGS,
        not gate violations -- they are recorded as evidence, never enforced.
        """
        return [w.finding for w in self.warnings]

    @property
    def gate_passed(self) -> bool:
        """True when the scan raised no complexity warnings.

        MF-036: complexity is advisory -- this value NEVER gates promotion. A
        False result means "the scan raised warnings the owner should read", not
        "the build fails". The name and the ledger field are kept for
        continuity with the pre-reframe ledger schema.
        """
        return not self.warnings


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

    # CD-01 (F1): resolve invariant aliasing/composition transitively. The cfg
    # may configure `INVARIANT Inv` with `Inv == RealInv` -- reading only the
    # immediate alias body sees no variable names at all.
    invariant_names = parse_cfg_invariants(cfg_text)
    invariant_bodies = {
        name: resolve_definition_body(name, by_name)
        for name in invariant_names
        if name in by_name
    }

    # CD-01 (F3): the per-variable domain source. Prefer a TypeInvariant/TypeOK
    # definition (resolved transitively -- it may itself compose); with neither,
    # fall back to the resolved cfg-invariant bodies, whose membership conjuncts
    # may still bound variables. When nothing resolves a domain, the bound is
    # reported UNKNOWN -- never a silent 1.
    if "TypeInvariant" in by_name:
        domain_source_label = "TypeInvariant"
        domain_source: str | None = resolve_definition_body("TypeInvariant", by_name)
    elif "TypeOK" in by_name:
        domain_source_label = "TypeOK"
        domain_source = resolve_definition_body("TypeOK", by_name)
    elif invariant_bodies:
        domain_source_label = "the configured invariants (resolved transitively)"
        domain_source = "\n".join(invariant_bodies.values())
    else:
        domain_source_label = "any type invariant or configured invariant"
        domain_source = None

    dimensions = infer_dimensions(
        domain_source, variables, constants, source_label=domain_source_label
    )
    bound = state_space_bound(dimensions)
    bound_source = domain_source_label if bound is not None else None
    unbounded = [d.variable for d in dimensions if not d.bounded]

    weights = interaction_graph(actions, variables)
    communities, score = greedy_communities(variables, weights)
    crossings = crossing_actions(communities, actions)
    dense_rows, dense_columns = dense_rows_and_columns(variables, actions)

    unread = invariant_unread_variables(variables, invariant_bodies)

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

    # MF-036: each threshold breach is an ADVISORY warning that names the
    # component/variable/action and states the measured fact. None of these
    # block promotion, refuse case generation, or drive a nonzero exit -- they
    # are findings for the owner, per references/architecture_tractability.md,
    # "Advisory, Not Blocking". The only nonzero exit is for a model the scan
    # CANNOT analyze (ModuleResolutionError / usage), handled in the CLI.
    warnings: list[Advisory] = []
    # MF-022: the static bound is a Cartesian over-approximation of the
    # DECLARED representation -- it ignores every action guard, so it counts
    # combinations the program can never occupy. It is therefore compared
    # against max_state_space_bound (a TLC-capacity ceiling), NOT against
    # max_distinct_states, which caps ACTUAL reachable states measured by TLC
    # after the fact. Comparing the two is a category error: on this
    # repository the bound over-approximated reachable states by ~400x, on a
    # model that was 17x under its own reachable-state budget.
    if bound is not None and bound > budgets["max_state_space_bound"]:
        warnings.append(
            Advisory(
                kind="state_space_bound",
                finding=(
                    f"state-space upper bound {bound:,} exceeds max_state_space_bound "
                    f"{budgets['max_state_space_bound']:,}"
                ),
            )
        )
    if bound is None:
        warnings.append(
            Advisory(
                kind="state_space_bound_unknown",
                finding=(
                    "state-space upper bound UNKNOWN: no variable domain could be "
                    "resolved from a TypeInvariant/TypeOK or from the configured "
                    "invariants, so the bound cannot be compared against "
                    "max_state_space_bound"
                ),
            )
        )
    for index, community in enumerate(communities, start=1):
        if len(community) > budgets["max_component_variables"]:
            members = ", ".join(sorted(community))
            warnings.append(
                Advisory(
                    kind="component_variables",
                    finding=(
                        f"component C{index} has {len(community)} variables "
                        f"({members}), exceeding max_component_variables "
                        f"{budgets['max_component_variables']}"
                    ),
                )
            )
    for index, community in enumerate(communities, start=1):
        touching = [a.name for a in actions if a.touched & community]
        if len(touching) > budgets["max_component_actions"]:
            warnings.append(
                Advisory(
                    kind="component_actions",
                    finding=(
                        f"component C{index} is touched by {len(touching)} actions "
                        f"({', '.join(touching)}), exceeding max_component_actions "
                        f"{budgets['max_component_actions']}"
                    ),
                )
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
                warnings.append(
                    Advisory(
                        kind="distinct_states",
                        finding=(
                            f"TLC-measured {current_report.distinct:,} distinct reachable "
                            f"states exceeds max_distinct_states "
                            f"{budgets['max_distinct_states']:,}"
                        ),
                    )
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

    analysis = Analysis(
        module=module,
        tla_path=tla_path,
        cfg_path=cfg_path,
        manifest_path=manifest_path,
        constants=constants,
        variables=variables,
        dimensions=dimensions,
        actions=actions,
        bound=bound,
        bound_source=bound_source,
        unbounded=unbounded,
        communities=communities,
        modularity_score=score,
        crossings=crossings,
        dense_rows=dense_rows,
        dense_columns=dense_columns,
        unread_by_invariant=unread,
        unjustified=unjustified,
        budgets=budgets,
        warnings=warnings,
        tlc_findings=tlc_findings,
    )

    # CD-03: evaluate the project's self-configured fitness functions over the
    # published descriptor facts. Rules persist with the project -- in the
    # manifest under `fitness_functions:` and/or in a sibling
    # fitness_functions.yaml next to the spec. No rules configured -> None ->
    # no fitness section in either renderer (there are NO built-in rules).
    # Advisory: firings are surfaced for future agents, never affect the exit
    # code, and even a broken rules file only yields advisory config errors.
    from scripts.fitness_functions import run_fitness

    analysis.fitness = run_fitness(manifest, tla_path.parent, descriptor_payload(analysis))
    return analysis


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

    add(f"analyze complexity -- {analysis.module} (complexity descriptor)")
    add(f"  spec:     {analysis.tla_path}")
    add(f"  config:   {analysis.cfg_path}")
    add(f"  manifest: {analysis.manifest_path or '(none)'}")
    add("")
    add("This is a DESCRIPTOR: every figure below is [MEASURED] -- parsed from this")
    add("spec + cfg. It states facts about the model and makes no suggestions.")
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
    if analysis.bound is None:
        add("  bound = UNKNOWN -- no variable domain could be resolved from a")
        add("  TypeInvariant/TypeOK or from the configured invariants. This is an")
        add("  explicit unknown, not a small model.")
    else:
        add(
            f"  bound = {analysis.bound:,}  (product of "
            f"{len(analysis.variables) - len(analysis.unbounded)} bounded dimensions; "
            f"domains from {analysis.bound_source})"
        )
    if analysis.unbounded:
        add(f"  excluded (no resolvable domain): {', '.join(analysis.unbounded)}")
    dominant = sorted(
        (d for d in analysis.dimensions if d.bounded),
        key=lambda d: -(d.cardinality or 0),
    )[:3]
    if dominant and analysis.bound is not None and analysis.bound > 1:
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

    add("[MEASURED] Dense rows and columns of the R/W matrix")
    if analysis.dense_rows:
        add("  dense rows (god-state signature -- variable touched by more than half the actions):")
        for variable, count in analysis.dense_rows.items():
            add(f"    {variable} touched by {count}/{len(analysis.actions)} actions")
    else:
        add("  no dense rows (no variable is touched by more than half the actions)")
    if analysis.dense_columns:
        add("  dense columns (action touching more than half the variables):")
        for name in analysis.dense_columns:
            add(f"    {name}")
    else:
        add("  no dense columns (no action touches more than half the variables)")
    add("")

    add("[MEASURED] Invariant coverage (aliased/composed invariants resolved transitively)")
    if analysis.unread_by_invariant:
        add("  variables no configured invariant reads:")
        for variable in analysis.unread_by_invariant:
            add(f"    {variable}")
    else:
        add("  every variable is read by at least one configured invariant.")
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

    add("  A poor score is not a verdict. Some components score badly and still need to")
    add("  exist in that form -- performance paths, protocol-mandated shapes, irreducible")
    add("  domain complexity. This output is evidence for the owner, not a decision.")
    add("  Before recording ANY complexity reduction as a result: read the transition-level")
    add("  diff. A generated-states drop at constant distinct states is a RED FLAG (a")
    add("  deleted self-loop), not a win -- the distinct-state gate cannot see it.")
    add("")

    add("[MEASURED] Complexity thresholds (advisory -- warnings only)")
    add(f"  source: {analysis.manifest_path or 'documented defaults'}")
    for key in (
        "max_state_space_bound",
        "max_distinct_states",
        "max_component_variables",
        "max_component_actions",
    ):
        add(f"    {key}: {analysis.budgets[key]:,}")
    add("  max_state_space_bound compares against the STATIC declared-representation bound above.")
    add("  max_distinct_states compares against ACTUAL reachable states and is checked only once")
    add("  TLC has measured them (--tlc-report); the two are not interchangeable.")
    add("")
    if not analysis.warnings:
        add("  No complexity warnings -- every metric is within its advisory threshold.")
    else:
        add("  COMPLEXITY WARNINGS -- these are FINDINGS. They do NOT block promotion,")
        add("  do NOT refuse case generation, and do NOT change the exit code. Complexity is a")
        add("  scanner, not a gate (references/architecture_tractability.md, 'Advisory, Not")
        add("  Blocking'). The owner decides, with the user, whether to act on each one.")
        for warning in analysis.warnings:
            add("")
            add(f"  WARNING: {warning.finding}")
    add("")

    # CD-03: the project's self-configured fitness functions. The section only
    # exists when the project configured rules (or a rules source is broken) --
    # there are NO built-in rules. Firings are notifications for future agents,
    # never blocks: the exit code is unchanged by any number of firings.
    if analysis.fitness is not None:
        fitness = analysis.fitness
        add("[CONFIGURED] Fitness functions (self-configured; advisory -- report, never block)")
        add(f"  sources: {', '.join(fitness.sources) or '(none)'}")
        for error in fitness.errors:
            add(f"  CONFIG ERROR: {error}")
        for result in fitness.results:
            if result.status == "holds":
                add(f"  holds: {result.name}")
            else:
                add(f"  {result.status.upper()}: {result.name} -- {result.detail}")
                if result.description:
                    add(f"    ({result.description})")
        if fitness.fired:
            add("")
            add("  A FIRED fitness function is a NOTIFICATION to this project's future")
            add("  agents: a condition the project's agent declared it wants to hold does")
            add("  not hold on this scan. It does NOT block promotion and does NOT change")
            add("  the exit code -- read it, judge it, and decide with the owner.")
        add("")

    add("  `analyze complexity` exits 0 whenever it can analyze the model -- a complex model")
    add("  is a finding, not a failure. It exits nonzero ONLY when the model cannot be")
    add("  analyzed at all (e.g. an unresolved module hierarchy); that is 'I could not")
    add("  measure this', which is distinct from 'this is complex'.")
    return "\n".join(out) + "\n"


def descriptor_payload(analysis: Analysis) -> dict[str, Any]:
    """The descriptor as a plain dict -- the JSON payload shape.

    Also the fact source for CD-03 fitness functions: rules are evaluated over
    exactly the facts this payload publishes, nothing private.
    """
    payload: dict[str, Any] = {
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
            "state_space_bound_known": analysis.bound is not None,
            "state_space_bound_source": analysis.bound_source,
            "unbounded_variables": analysis.unbounded,
            "actions": [
                {"name": a.name, "reads": sorted(a.reads), "writes": sorted(a.writes)}
                for a in analysis.actions
            ],
            "modularity": analysis.modularity_score,
            "components": [sorted(c) for c in analysis.communities],
            "port_crossing_actions": analysis.crossings,
            "dense_rows": analysis.dense_rows,
            "dense_columns": analysis.dense_columns,
            "unread_by_invariant": analysis.unread_by_invariant,
            "unjustified_variables": analysis.unjustified,
            "tlc_findings": analysis.tlc_findings,
        },
        "budgets": {
            key: analysis.budgets[key]
            for key in (
                "max_state_space_bound",
                "max_distinct_states",
                "max_component_variables",
                "max_component_actions",
            )
        },
        "advisory": {
            "blocks_promotion": False,
            "clean": analysis.gate_passed,
            "warnings": [
                {
                    "kind": warning.kind,
                    "finding": warning.finding,
                }
                for warning in analysis.warnings
            ],
        },
    }
    # CD-03: self-configured fitness functions. None when the project has no
    # rules configured (there are no built-in rules). Advisory only.
    if analysis.fitness is None:
        payload["fitness"] = None
    else:
        payload["fitness"] = {
            "blocks_promotion": False,
            "sources": analysis.fitness.sources,
            "config_errors": analysis.fitness.errors,
            "fired": [r.name for r in analysis.fitness.fired],
            "results": [
                {
                    "name": r.name,
                    "status": r.status,
                    "detail": r.detail,
                    "description": r.description,
                }
                for r in analysis.fitness.results
            ],
        }
    return payload


def render_json(analysis: Analysis) -> str:
    return json.dumps(descriptor_payload(analysis), indent=2, sort_keys=False) + "\n"


# --------------------------------------------------------------------------
# Advisory report helper used by case generation
# --------------------------------------------------------------------------


def gate_report(tla_path: Path, cfg_path: Path, manifest_path: Path | None) -> tuple[bool, str]:
    """Advisory complexity report for case generation. Returns ``(clean, message)``.

    MF-036: this is a scanner, not a gate. ``clean`` is True when the scan
    raised no complexity warnings; a False value means the caller should print
    the warnings, NOT that it should refuse. Case generation is expected to
    proceed either way (references/architecture_tractability.md, "Advisory, Not
    Blocking"). The one thing that is not a mere finding is a model the scan
    cannot analyze at all (MF-030 fail-closed): that is reported as ``clean =
    False`` with a "could not be resolved" message so the caller can surface it,
    but even then the caller proceeds -- TLC may handle a model the static
    scanner cannot.
    """
    try:
        analysis = analyze(tla_path, cfg_path, manifest_path)
    except ModuleResolutionError as exc:
        return False, (
            "complexity scan could not analyze this model -- the module "
            "hierarchy could not be resolved:\n"
            f"  {exc}\n"
            "This is an 'I could not measure this' note, not a promotion block; "
            "case generation still proceeds."
        )
    if analysis.gate_passed:
        return True, (
            f"complexity scan clean: state-space upper bound {analysis.bound:,} within "
            f"max_state_space_bound {analysis.budgets['max_state_space_bound']:,}, and "
            "every component within its advisory thresholds"
        )
    lines = [
        "complexity scan -- ADVISORY WARNINGS (these do NOT block case generation):",
        "",
    ]
    for warning in analysis.warnings:
        lines.append(f"  WARNING: {warning.finding}")
    lines.append("")
    lines.append("Dominant dimensions:")
    dominant = sorted(
        (d for d in analysis.dimensions if d.bounded), key=lambda d: -(d.cardinality or 0)
    )[:5]
    for d in dominant:
        lines.append(f"  {d.variable}: {d.cardinality:,}  ({d.expression})")
    lines.append("")
    lines.append("Run `tla-spec-dev analyze complexity <spec> <cfg>` for the full descriptor.")
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
        # MF-030 / MF-036: a hierarchy the analyzer CANNOT resolve is the one
        # genuine error -- "I could not measure this model" -- so it fails closed
        # nonzero rather than emit an under-reported number. This is distinct
        # from "this model is complex", which is now advisory and exits 0.
        print(
            "ERROR: complexity analysis could not analyze this model -- the module "
            f"hierarchy could not be resolved:\n  {exc}",
            file=sys.stderr,
        )
        return EXIT_ANALYSIS_ERROR

    rendered = render_json(analysis) if args.format == "json" else render_text(analysis)
    sys.stdout.write(rendered)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered, encoding="utf-8")
        print(f"wrote evidence: {out_path}", file=sys.stderr)
    # MF-036: a complex model is a finding, not a failure. Once the model could
    # be analyzed, the command exits 0 regardless of how many advisory warnings
    # the scan raised -- complexity never blocks promotion.
    return EXIT_PASS


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
