#!/usr/bin/env python3
"""AC-02: the REFLEXION CHECK -- the production code, measured against the model.

Murphy, Notkin & Sullivan's software reflexion model, with the model side
supplied by AC-01's architecture descriptor:

  * a **declared map** from production modules to model components -- written
    by the project, never inferred;
  * an **extracted dependency graph** of the real code (Python: imports plus
    resolvable call edges), each edge carrying ``file:line``;
  * a **diff**, reported in the reflexion model's own three categories:

      ``convergence``  a code edge between two components that a port declares;
      ``divergence``   a code edge between two components no port declares --
                       the block pulled out from under three others;
      ``absence``      a declared port no code edge realizes -- dead
                       architecture.

    A fourth category, ``internal``, counts the edges that stay inside one
    component. Internal edges are not convergences: they never crossed a
    boundary, so no port was needed and none was checked.

Four rules govern every line below.

**Declared, never inferred.** The map is read, not computed. An auditing tool
that picks its own boundary can define every finding out of existence -- and
the boundary it would pick is the one the code already has, which makes every
edge legal by construction. The same rule AC-01 applies to the component
partition (``load_declared_components``), applied to the module map.

**A refusal beats a false clean (MF-027).** Everything this check cannot see
makes the verdict ``unmappable``: a model side with no architecture, a module
in the scanned tree the map does not place, a component no module realizes, a
dynamic edge the extractor cannot resolve, a file it cannot parse, and an
architecture whose ports permit every pair (under which "no divergences" is
true by construction rather than measured). ``unmappable`` is not "clean with
caveats": a clean report on a target you could not see is indistinguishable
from a clean report on one you could. **Findings are still reported under an
unmappable verdict** -- "I could not see all of it" and "I saw nothing" are
different facts too.

**Nothing downgrades an unmappable verdict.** There is no flag, key,
annotation, or environment variable that turns ``unmappable`` into
``coherent``. Suppression-shaped keys in the map are SCANNED, reported in
``ignored_suppression_keys``, and never honored -- the shape
``scripts/effect_conformance.py`` uses, for the reason stated there: a silently
ignored key is nearly as bad as an honored one, because the author believes the
finding was waived. :func:`reflexion_verdict` consults no configuration at all.

**Advisory, not blocking (the epic's standing doctrine).** A divergent codebase
is a FINDING. Exit 0. The only nonzero exit is "I could not measure this": an
unusable map or an unreadable code tree. No suggested moves (CD-01): this
module reports edges and facts. It never says where a module should live.

Coverage limits, stated once and reported in every run
------------------------------------------------------
* **Python only.** ``--code`` is scanned for ``*.py``. A non-Python file in the
  tree is counted and named, never silently skipped.
* **Static resolution only.** ``import``/``from``-``import`` (including
  relative imports and literal-argument ``importlib.import_module``), plus call
  sites whose callee resolves through one of those bindings. Anything reached
  through a computed name is a blind spot, not an absence.
* **In-tree edges only.** An import that resolves outside the scanned tree
  (the standard library, a third-party package) is recorded as an external
  dependency and is not an edge: the model declares components of *this*
  program, so it has nothing to say about the pair. This is a real limit --
  a component that talks to a database directly is invisible here -- and it is
  reported next to the counts rather than left to be discovered.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

if __package__ in (None, ""):  # direct `python3 scripts/architecture_reflexion.py`
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.analyze_architecture import (  # noqa: E402
    EXIT_ANALYSIS_ERROR,
    EXIT_PASS,
    EXIT_USAGE,
    ArchitectureDescriptor,
    DeclaredPartitionError,
    _load_yaml,
    analyze,
    default_cfg_for,
    default_manifest_for,
)
from scripts.analyze_complexity import ModuleResolutionError  # noqa: E402

SCHEMA = "tla-spec-dev/architecture-reflexion"
SCHEMA_VERSION = 1

#: The four verdict values ``architecture_scan`` ranges over. ``unknown`` is
#: the CLI's "not run" and is never produced here.
VERDICT_COHERENT = "coherent"
VERDICT_DIVERGENT = "divergent"
VERDICT_UNMAPPABLE = "unmappable"

#: Keys whose presence anywhere in the map is a request to be let off. They are
#: recorded and reported; none of them is read by any verdict. Copied in spirit
#: from ``scripts/effect_conformance.py``'s SUPPRESSION_KEYS: a withdrawn
#: escape tends to grow back, so the code does the opposite of honoring one.
SUPPRESSION_KEYS = frozenset(
    {
        "accept",
        "accepted",
        "accepted_divergence",
        "accepted_divergences",
        "allow_divergence",
        "allow_divergences",
        "allow_unmapped",
        "assume_coherent",
        "assume_mapped",
        "exclude",
        "excluded",
        "expected_divergences",
        "ignore",
        "ignored",
        "justification",
        "justifications",
        "known_divergences",
        "override",
        "skip",
        "skipped",
        "suppress",
        "suppressed",
        "trusted",
        "waive",
        "waived",
        "waiver",
    }
)


class ReflexionMapError(Exception):
    """A declared map that cannot be read as one.

    Unusable INPUT -- exits nonzero, like AC-01's :class:`DeclaredPartitionError`
    and for the same reason: the project asked for a specific map to be
    measured, and quietly measuring a different one (or none) would report
    facts about a boundary nobody declared.
    """


class CodeExtractionError(Exception):
    """The code tree could not be read at all. Also unusable input."""


# --------------------------------------------------------------------------
# The declared map
# --------------------------------------------------------------------------


@dataclass
class ReflexionMap:
    """A DECLARED production-module -> model-component map."""

    origin: str
    language: str
    #: module path (relative to the code root) -> declared component name
    modules: dict[str, str] = field(default_factory=dict)
    #: component name -> declared module paths, in declaration order
    components: dict[str, list[str]] = field(default_factory=dict)
    ignored_suppression_keys: list[str] = field(default_factory=list)


def _scan_for_suppression(node: Any, path: str) -> list[str]:
    """Find suppression-shaped keys so they can be reported, never honored."""
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            child = f"{path}.{key}"
            if isinstance(key, str) and key.lower() in SUPPRESSION_KEYS:
                found.append(child)
            found.extend(_scan_for_suppression(value, child))
    elif isinstance(node, (list, tuple)):
        for index, value in enumerate(node):
            found.extend(_scan_for_suppression(value, f"{path}[{index}]"))
    return found


def _expand_module_entry(entry: str, code_root: Path, origin: str) -> list[Path]:
    """Resolve one ``modules:`` entry to the files it names.

    Two spellings resolve, both required to land inside the scanned tree:
    relative to the code root (``analyze_architecture.py``) and relative to the
    working directory (``scripts/analyze_architecture.py``), because the second
    is how a map reads when the code root is a subdirectory of the project. A
    directory entry expands to every ``*.py`` beneath it.
    """
    text = str(entry).strip()
    if not text:
        raise ReflexionMapError(f"{origin}: an empty module entry")
    candidates = [code_root / text, Path(text).resolve()]
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:  # pragma: no cover - defensive
            continue
        if not resolved.exists():
            continue
        if resolved != code_root and code_root not in resolved.parents:
            raise ReflexionMapError(
                f"{origin}: module entry `{text}` resolves to {resolved}, which is "
                f"outside the scanned code root {code_root}. The map places modules of "
                "the tree being measured; a path outside it maps nothing."
            )
        if resolved.is_dir():
            return sorted(p for p in resolved.rglob("*.py") if _is_scannable(p))
        return [resolved]
    raise ReflexionMapError(
        f"{origin}: module entry `{text}` does not exist under the code root "
        f"{code_root} or the working directory. A map entry that names no file "
        "places no module -- it is a declaration about nothing."
    )


def load_reflexion_map(source: Any, code_root: Path, origin: str) -> ReflexionMap:
    """Read a DECLARED module map. Never inferred, never proposed.

    Shape::

        architecture_map:
          language: python
          components:
            - component: lifecycle     # a component name the descriptor has
              modules:
                - scripts/start_ticket.py
                - scripts/close_ticket.py
            - component: scanners
              modules: [scripts/analyze_complexity.py]

    Every rejection below is a refusal to measure a map that does not say what
    it appears to say. None of them is a judgment about the code.
    """
    if isinstance(source, dict) and "architecture_map" in source:
        outside = {k: v for k, v in source.items() if k != "architecture_map"}
        source = source.get("architecture_map")
        suppression = _scan_for_suppression(outside, "map") + _scan_for_suppression(
            source, "architecture_map"
        )
    else:
        suppression = _scan_for_suppression(source, "architecture_map")
    if not isinstance(source, dict):
        raise ReflexionMapError(
            f"{origin}: expected a mapping under `architecture_map:` with a "
            "`components:` list"
        )
    language = str(source.get("language") or "python").strip().lower()
    if language != "python":
        # The extractor ships for Python (AC-02 scope). Declaring another
        # language is not a silent pass: the map asked for a measurement this
        # build cannot make.
        raise ReflexionMapError(
            f"{origin}: language `{language}` has no extractor in this build. Only "
            "`python` is extractable; a map naming another language would be checked "
            "against an empty graph, which reports every port absent and every module "
            "unmapped while looking like a measurement."
        )
    entries = source.get("components")
    if not isinstance(entries, (list, tuple)) or not entries:
        raise ReflexionMapError(
            f"{origin}: expected a non-empty `components:` list under `architecture_map:`"
        )

    mapping = ReflexionMap(origin=origin, language=language)
    mapping.ignored_suppression_keys = suppression
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            raise ReflexionMapError(
                f"{origin}: map entry #{index} is not a mapping with `component:` and "
                "`modules:`"
            )
        name = str(entry.get("component") or entry.get("name") or "").strip()
        if not name:
            raise ReflexionMapError(f"{origin}: map entry #{index} names no `component:`")
        if name in mapping.components:
            raise ReflexionMapError(f"{origin}: component `{name}` is mapped twice")
        modules = entry.get("modules")
        if isinstance(modules, str):
            modules = [modules]
        if not isinstance(modules, (list, tuple)) or not modules:
            raise ReflexionMapError(
                f"{origin}: component `{name}` declares no `modules:`. A component "
                "with no modules is not a mapping of zero files -- it is a component "
                "the code does not realize, which is reported as such only when the "
                "map does not claim otherwise."
            )
        placed: list[str] = []
        for raw in modules:
            for path in _expand_module_entry(str(raw), code_root, origin):
                rel = path.relative_to(code_root).as_posix()
                if rel in mapping.modules and mapping.modules[rel] != name:
                    raise ReflexionMapError(
                        f"{origin}: `{rel}` is mapped to both `{mapping.modules[rel]}` "
                        f"and `{name}` -- a module map must not overlap. A module in "
                        "two components has no boundary to cross."
                    )
                mapping.modules[rel] = name
                if rel not in placed:
                    placed.append(rel)
        mapping.components[name] = placed
    return mapping


# --------------------------------------------------------------------------
# The extracted code graph
# --------------------------------------------------------------------------


@dataclass
class CodeEdge:
    """One dependency edge between two files of the scanned tree.

    ``file``/``line`` is the SITE: the import statement or the call, not the
    file the edge points at. A divergence a reader cannot navigate to is an
    opinion.
    """

    src: str
    dst: str
    kind: str
    symbol: str
    file: str
    line: int

    @property
    def site(self) -> str:
        return f"{self.file}:{self.line}"

    def payload(self) -> dict[str, Any]:
        return {
            "from": self.src,
            "to": self.dst,
            "kind": self.kind,
            "symbol": self.symbol,
            "file": self.file,
            "line": self.line,
            "site": self.site,
        }


@dataclass
class BlindSpot:
    """Something the extractor could not see. Each one forces ``unmappable``."""

    kind: str
    detail: str
    where: str | None = None

    def payload(self) -> dict[str, Any]:
        return {"kind": self.kind, "detail": self.detail, "where": self.where}


@dataclass
class CodeGraph:
    root: Path
    modules: list[str] = field(default_factory=list)
    edges: list[CodeEdge] = field(default_factory=list)
    blind_spots: list[BlindSpot] = field(default_factory=list)
    external_imports: dict[str, list[str]] = field(default_factory=dict)
    non_python_files: list[str] = field(default_factory=list)

    def display(self, rel: str) -> str:
        """A navigable path: relative to the working directory when it is under it.

        ``file:line`` is only evidence a reader can follow if the reader can
        paste it. Absolute paths from a temp checkout are not that.
        """
        absolute = (self.root / rel).resolve()
        try:
            return absolute.relative_to(Path.cwd()).as_posix()
        except ValueError:
            return absolute.as_posix()


def _is_scannable(path: Path) -> bool:
    parts = set(path.parts)
    return "__pycache__" not in parts and not path.name.startswith(".")


def _dotted_names(rel: str, root_name: str) -> list[str]:
    """The dotted module names a file answers to.

    Both the name relative to the code root (``analyze_complexity``) and the
    name relative to its parent (``scripts.analyze_complexity``), because a
    project imports its own package by either spelling depending on which
    directory is on ``sys.path``. Resolution that guessed only one of the two
    would report half the real edges as external and the tree as coherent.
    """
    parts = rel[: -len(".py")].split("/")
    if parts[-1] == "__init__":
        parts = parts[:-1]
    if not parts:
        return []
    names = [".".join(parts)]
    names.append(".".join([root_name, *parts]))
    return names


def _dotted_of_call(node: ast.AST) -> str | None:
    """The dotted name of a call target, or None when it is computed."""
    parts: list[str] = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if not isinstance(current, ast.Name):
        return None
    parts.append(current.id)
    return ".".join(reversed(parts))


class _ModuleVisitor(ast.NodeVisitor):
    """Collects import edges, call edges, and blind spots for one file."""

    def __init__(self, graph: CodeGraph, rel: str, index: dict[str, str]) -> None:
        self.graph = graph
        self.rel = rel
        self.index = index
        self.display = graph.display(rel)
        self.bindings: dict[str, str] = {}
        self.module_locals: set[str] = set()
        self.pending_calls: list[tuple[str, int]] = []

    # -- helpers ---------------------------------------------------------

    def _resolve(self, dotted: str) -> str | None:
        return self.index.get(dotted)

    def _is_in_tree_name(self, dotted: str) -> bool:
        """Whether a dotted name belongs to the scanned tree's namespace.

        Used to tell an EXTERNAL import (``json``, ``pytest``) from an in-tree
        import the extractor failed to resolve. The first is out of scope; the
        second is a blind spot.
        """
        head = dotted.split(".")[0]
        return head == self.graph.root.name or any(
            name == head or name.startswith(head + ".") for name in self.index
        )

    def _record_import(self, dotted: str, symbol: str, line: int, kind: str) -> str | None:
        target = self._resolve(dotted)
        if target is None:
            return None
        if target != self.rel:
            self.graph.edges.append(
                CodeEdge(
                    src=self.rel,
                    dst=target,
                    kind=kind,
                    symbol=symbol,
                    file=self.display,
                    line=line,
                )
            )
        return target

    def _record_external_or_blind(self, dotted: str, line: int) -> None:
        if self._is_in_tree_name(dotted):
            self.graph.blind_spots.append(
                BlindSpot(
                    kind="unresolved_import",
                    detail=(
                        f"`{dotted}` looks like a module of the scanned tree but does "
                        "not resolve to a file in it"
                    ),
                    where=f"{self.display}:{line}",
                )
            )
            return
        self.graph.external_imports.setdefault(dotted.split(".")[0], []).append(
            f"{self.display}:{line}"
        )

    def _relative_module(self, node: ast.ImportFrom) -> str | None:
        """Resolve ``from . import x`` / ``from ..pkg import y`` to a dotted name."""
        parts = self.rel[: -len(".py")].split("/")
        if parts[-1] == "__init__":
            parts = parts[:-1]
        package = parts[:-1] if parts and parts[-1] != "" else parts
        level = node.level
        if level > 1:
            package = package[: -(level - 1)] if level - 1 <= len(package) else []
        base = list(package)
        if node.module:
            base.extend(node.module.split("."))
        return ".".join(base) if base else None

    # -- visits ----------------------------------------------------------

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            target = self._record_import(alias.name, alias.name, node.lineno, "import")
            if target is None:
                self._record_external_or_blind(alias.name, node.lineno)
                continue
            local = alias.asname or alias.name
            self.bindings[local] = target
            if alias.asname is None and "." in alias.name:
                self.bindings[alias.name] = target
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = self._relative_module(node) if node.level else node.module
        if module is None:
            self.generic_visit(node)
            return
        base_target = self._resolve(module)
        for alias in node.names:
            if alias.name == "*":
                if base_target is not None:
                    self._record_import(module, "*", node.lineno, "import")
                    self.graph.blind_spots.append(
                        BlindSpot(
                            kind="star_import",
                            detail=(
                                f"`from {module} import *` -- the names it binds cannot "
                                "be attributed to a source module, so call edges "
                                "through them are invisible"
                            ),
                            where=f"{self.display}:{node.lineno}",
                        )
                    )
                else:
                    self._record_external_or_blind(module, node.lineno)
                continue
            # `from pkg import mod` where pkg.mod is itself a module.
            submodule = f"{module}.{alias.name}"
            target = self._record_import(
                submodule, f"{module}.{alias.name}", node.lineno, "import"
            )
            if target is not None:
                self.bindings[alias.asname or alias.name] = target
                continue
            if base_target is not None:
                self._record_import(module, f"{module}.{alias.name}", node.lineno, "import")
                self.bindings[alias.asname or alias.name] = base_target
                continue
            self._record_external_or_blind(module, node.lineno)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        dotted = _dotted_of_call(node.func)
        if dotted is not None:
            tail = dotted.rsplit(".", 1)[-1]
            if tail in {"import_module", "__import__"}:
                self._dynamic_import(node, dotted)
            elif tail == "getattr":
                self._dynamic_attribute(node)
            else:
                self.pending_calls.append((dotted, node.lineno))
        self.generic_visit(node)

    def _dynamic_import(self, node: ast.Call, dotted: str) -> None:
        argument = node.args[0] if node.args else None
        if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
            target = self._record_import(
                argument.value, f"{dotted}({argument.value!r})", node.lineno, "dynamic-import"
            )
            if target is None:
                self._record_external_or_blind(argument.value, node.lineno)
            return
        self.graph.blind_spots.append(
            BlindSpot(
                kind="dynamic_import",
                detail=(
                    f"`{dotted}(...)` is called with a computed module name; the edge it "
                    "creates cannot be resolved statically"
                ),
                where=f"{self.display}:{node.lineno}",
            )
        )

    def _dynamic_attribute(self, node: ast.Call) -> None:
        argument = node.args[0] if node.args else None
        base = _dotted_of_call(argument) if isinstance(argument, (ast.Name, ast.Attribute)) else None
        if base is None:
            return
        if self._binding_for(base) is None:
            return
        self.graph.blind_spots.append(
            BlindSpot(
                kind="dynamic_attribute",
                detail=(
                    f"`getattr({base}, ...)` reaches into a module of the scanned tree by "
                    "computed name; what it reaches cannot be resolved statically"
                ),
                where=f"{self.display}:{node.lineno}",
            )
        )

    def _binding_for(self, dotted: str) -> str | None:
        parts = dotted.split(".")
        for size in range(len(parts), 0, -1):
            prefix = ".".join(parts[:size])
            if prefix in self.bindings:
                return self.bindings[prefix]
        return None

    def finish(self) -> None:
        """Resolve call sites once every binding in the file is known."""
        for dotted, line in self.pending_calls:
            target = self._binding_for(dotted)
            if target is None or target == self.rel:
                continue
            self.graph.edges.append(
                CodeEdge(
                    src=self.rel,
                    dst=target,
                    kind="call",
                    symbol=dotted,
                    file=self.display,
                    line=line,
                )
            )


def extract_python_graph(code_root: Path) -> CodeGraph:
    """Extract the dependency graph of a Python tree.

    The extractor's contract, which another language's extractor would have to
    satisfy to take its place: given a root, produce (a) the module list, (b)
    edges with ``file:line`` at the SITE of the dependency, and (c) an explicit
    list of what it could not resolve. (c) is the part that matters -- an
    extractor that returns only (a) and (b) cannot be told apart from one that
    saw everything.
    """
    if not code_root.is_dir():
        raise CodeExtractionError(f"code root is not a directory: {code_root}")

    graph = CodeGraph(root=code_root)
    files: list[tuple[str, Path]] = []
    for path in sorted(code_root.rglob("*")):
        if not path.is_file() or not _is_scannable(path):
            continue
        rel = path.relative_to(code_root).as_posix()
        if path.suffix == ".py":
            files.append((rel, path))
            graph.modules.append(rel)
        else:
            graph.non_python_files.append(rel)

    if not files:
        raise CodeExtractionError(
            f"no Python files under {code_root}: there is no graph to extract, and an "
            "empty graph would report every declared port absent while looking like a "
            "measurement of the code"
        )

    index: dict[str, str] = {}
    for rel, _ in files:
        for name in _dotted_names(rel, code_root.name):
            index.setdefault(name, rel)

    for rel, path in files:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError, OSError) as exc:
            graph.blind_spots.append(
                BlindSpot(
                    kind="unparsed_file",
                    detail=f"could not be parsed as Python ({exc.__class__.__name__}: {exc})",
                    where=graph.display(rel),
                )
            )
            continue
        visitor = _ModuleVisitor(graph, rel, index)
        visitor.visit(tree)
        visitor.finish()

    # An import that resolves outside the code root is normally out of scope --
    # the model describes components of this program, not of the standard
    # library. But when the target sits NEXT TO the code root in the same
    # project, "outside the scan" is a property of where --code was pointed,
    # not of the program: narrowing the code root would then delete real edges
    # from the graph with nothing recorded. Those are named.
    for name in sorted(graph.external_imports):
        sibling = code_root.parent / name
        if (sibling / "__init__.py").is_file() or sibling.with_suffix(".py").is_file():
            graph.blind_spots.append(
                BlindSpot(
                    kind="first_party_outside_code_root",
                    detail=(
                        f"`{name}` is imported by the scanned tree and lives beside it "
                        f"in {code_root.parent}, but outside --code. Its edges are not "
                        "in this graph, and no component of the map can be held to "
                        "them. Widen --code, or accept that this dependency is "
                        "unmeasured"
                    ),
                    where=", ".join(sorted(set(graph.external_imports[name]))[:4]),
                )
            )

    for rel in graph.non_python_files:
        graph.blind_spots.append(
            BlindSpot(
                kind="non_python_file",
                detail=(
                    "is in the scanned tree and has no extractor in this build; whatever "
                    "dependencies it declares are invisible to this check"
                ),
                where=graph.display(rel),
            )
        )

    graph.edges = _dedupe(graph.edges)
    return graph


def _dedupe(edges: Iterable[CodeEdge]) -> list[CodeEdge]:
    seen: set[tuple[str, str, str, str, int]] = set()
    result: list[CodeEdge] = []
    for edge in edges:
        key = (edge.src, edge.dst, edge.kind, edge.file, edge.line)
        if key in seen:
            continue
        seen.add(key)
        result.append(edge)
    return sorted(result, key=lambda e: (e.src, e.dst, e.line, e.kind))


# --------------------------------------------------------------------------
# The reflexion diff
# --------------------------------------------------------------------------


@dataclass
class ReflexionReport:
    descriptor: ArchitectureDescriptor
    mapping: ReflexionMap | None
    graph: CodeGraph | None
    convergences: list[dict[str, Any]] = field(default_factory=list)
    divergences: list[dict[str, Any]] = field(default_factory=list)
    absences: list[dict[str, Any]] = field(default_factory=list)
    internal_edges: list[CodeEdge] = field(default_factory=list)
    blind_spots: list[BlindSpot] = field(default_factory=list)
    unmapped_modules: list[str] = field(default_factory=list)
    unrealized_components: list[str] = field(default_factory=list)
    port_pairs: list[tuple[str, str]] = field(default_factory=list)
    unported_pairs: list[tuple[str, str]] = field(default_factory=list)
    ignored_suppression_keys: list[str] = field(default_factory=list)

    @property
    def divergence_detectable(self) -> bool:
        """Whether ANY code edge could have been a divergence.

        False when every component pair has a port: then "no divergences" is a
        property of the declared architecture, not a measurement of the code.
        A ``coherent`` verdict on an architecture that permits everything is the
        structural twin of a clean effect report from a sandbox that observed
        nothing, and MF-027 governs both.
        """
        return bool(self.unported_pairs)

    @property
    def verdict(self) -> str:
        """The value recorded in the model's ``architecture_scan``.

        Reads ``self`` only. No flag, key, annotation, or environment variable
        participates: there is nothing to pass in that could change the answer.
        """
        if self.blind_spots:
            return VERDICT_UNMAPPABLE
        if self.divergences or self.absences:
            return VERDICT_DIVERGENT
        return VERDICT_COHERENT

    @property
    def reasons(self) -> list[str]:
        out: list[str] = []
        for spot in self.blind_spots:
            where = f" ({spot.where})" if spot.where else ""
            out.append(f"[{spot.kind}] {spot.detail}{where}")
        if self.divergences:
            out.append(
                f"{len(self.divergences)} code edge(s) cross a component boundary the "
                "model declares no port for"
            )
        if self.absences:
            out.append(
                f"{len(self.absences)} declared port(s) are realized by no code edge"
            )
        if not out:
            out.append(
                "every code edge that crosses a component boundary has a declared port, "
                "every declared port is realized, every module in the scanned tree is "
                "mapped, and every declared component is realized by code"
            )
        return out


def _grouped_blind_spot(kind: str, detail: str, items: Sequence[str]) -> BlindSpot:
    listed = ", ".join(items[:8])
    if len(items) > 8:
        listed += f", ... (+{len(items) - 8} more)"
    return BlindSpot(kind=kind, detail=f"{detail}: {listed}", where=None)


def reflexion(
    descriptor: ArchitectureDescriptor,
    map_source: Any,
    code_root: Path,
    map_origin: str,
) -> ReflexionReport:
    """Diff the extracted code graph against the model's declared architecture.

    Order matters and is deliberate:

    1. **The model side first.** If AC-01 says the partition is not consumable
       as an architecture, stop. The reason is about the MODEL, and validating
       a map against a partition the model does not have would report the
       map's spelling as the finding.
    2. **Then the target**, which must yield a graph or the run is refused: an
       empty extraction reports every port absent and looks like a measurement.
    3. **Then the map**, which must be usable or the run is refused (nonzero).
    4. **Then the diff**, whose findings are advisory and never refuse anything.
    """
    mapping = None
    graph = None
    report = ReflexionReport(descriptor=descriptor, mapping=mapping, graph=graph)

    if not descriptor.consumable_as_architecture:
        failed = [c["name"] for c in descriptor.criteria if not c["met"]]
        report.blind_spots.append(
            BlindSpot(
                kind="model_has_no_architecture",
                detail=(
                    "the MODEL side has no architecture to measure code against: the "
                    f"emergent partition fails ({', '.join(failed)}) and the project "
                    "declares none. This is a fact about "
                    f"{descriptor.tla_path.name}, not about the code -- with one "
                    "component every code edge is internal, and this check would "
                    "otherwise report a flawless codebase for a model with no boundary "
                    "in it. Declare a partition (`architecture:` in spec_manifest.yaml, "
                    "or --components) to make the comparison possible"
                ),
                where=str(descriptor.tla_path),
            )
        )
        return report

    graph = extract_python_graph(code_root)
    report.graph = graph

    mapping = load_reflexion_map(map_source, code_root, map_origin)
    report.mapping = mapping
    report.ignored_suppression_keys = list(mapping.ignored_suppression_keys)

    known = {c.name: c.cid for c in descriptor.components}
    unknown = [name for name in mapping.components if name not in known]
    if unknown:
        raise ReflexionMapError(
            f"{map_origin}: maps modules onto component(s) the model does not have: "
            f"{', '.join(sorted(unknown))}. The model's components are: "
            f"{', '.join(sorted(known))}. A map that names its own components measures "
            "the code against an architecture nobody declared."
        )

    report.blind_spots.extend(graph.blind_spots)

    # Every module in the scanned tree must be placed. A map that covers only
    # the tidy half of a tree and reports it clean is the whole failure mode
    # this check exists to prevent; leaving a module out makes the tree
    # unmappable, never cleaner.
    report.unmapped_modules = [m for m in graph.modules if m not in mapping.modules]
    if report.unmapped_modules:
        report.blind_spots.append(
            _grouped_blind_spot(
                "unmapped_module",
                f"{len(report.unmapped_modules)} module(s) in the scanned tree are placed "
                "in no component by the map, so their edges cannot be judged",
                [graph.display(m) for m in sorted(report.unmapped_modules)],
            )
        )

    report.unrealized_components = sorted(
        name for name in known if not mapping.components.get(name)
    )
    if report.unrealized_components:
        report.blind_spots.append(
            _grouped_blind_spot(
                "unrealized_component",
                "the map places no production module in these declared component(s), so "
                "whether the code respects their boundaries cannot be observed",
                report.unrealized_components,
            )
        )

    id_to_name = {c.cid: c.name for c in descriptor.components}
    port_pairs = {
        tuple(sorted((id_to_name[p.between[0]], id_to_name[p.between[1]])))
        for p in descriptor.ports
        if p.between[0] in id_to_name and p.between[1] in id_to_name
    }
    port_actions = {
        tuple(sorted((id_to_name[p.between[0]], id_to_name[p.between[1]]))): p
        for p in descriptor.ports
        if p.between[0] in id_to_name and p.between[1] in id_to_name
    }
    names = sorted(known)
    all_pairs = {
        (left, right) for i, left in enumerate(names) for right in names[i + 1 :]
    }
    report.port_pairs = sorted(port_pairs)
    report.unported_pairs = sorted(all_pairs - port_pairs)

    if not report.unported_pairs and len(names) >= 2:
        report.blind_spots.append(
            BlindSpot(
                kind="unfalsifiable_coherence",
                detail=(
                    f"every one of the {len(all_pairs)} component pair(s) in this "
                    "architecture has a port, so no code edge could have been a "
                    "divergence. 'No divergences' here is a property of the declared "
                    "architecture, not a measurement of the code, and a coherent "
                    "verdict would be true by construction. (This is what a model whose "
                    "actions all touch the same variables produces under any partition.)"
                ),
                where=str(descriptor.tla_path),
            )
        )

    realized: set[tuple[str, str]] = set()
    for edge in graph.edges:
        source = mapping.modules.get(edge.src)
        target = mapping.modules.get(edge.dst)
        if source is None or target is None:
            continue  # already a blind spot; judging it would invent a boundary
        if source == target:
            report.internal_edges.append(edge)
            continue
        pair = tuple(sorted((source, target)))
        row = {
            **edge.payload(),
            "from_component": source,
            "to_component": target,
            "pair": list(pair),
        }
        if pair in port_pairs:
            realized.add(pair)
            port = port_actions[pair]
            row["port"] = port.pid
            row["port_actions"] = port.actions
            report.convergences.append(row)
        else:
            row["port"] = None
            row["why"] = (
                f"no port between `{pair[0]}` and `{pair[1]}`: no action of the model "
                "touches both components, so the model does not declare that these two "
                "parts of the program interact"
            )
            report.divergences.append(row)

    for pair in sorted(port_pairs - realized):
        port = port_actions[pair]
        report.absences.append(
            {
                "port": port.pid,
                "between": list(pair),
                "actions": port.actions,
                "why": (
                    f"the model declares a port between `{pair[0]}` and `{pair[1]}` "
                    f"(crossed by {', '.join(port.actions)}), and no extracted code edge "
                    "connects the modules mapped to them -- dead architecture, or an "
                    "interaction the extractor cannot see"
                ),
            }
        )

    return report


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------


def report_payload(report: ReflexionReport) -> dict[str, Any]:
    graph = report.graph
    mapping = report.mapping
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "map": mapping.origin if mapping else None,
        "code_root": str(graph.root) if graph else None,
        "language": mapping.language if mapping else None,
        "measured": {
            "modules_scanned": len(graph.modules) if graph else 0,
            "modules_mapped": len(mapping.modules) if mapping else 0,
            "edges_extracted": len(graph.edges) if graph else 0,
            "component_pairs": len(report.port_pairs) + len(report.unported_pairs),
            "ported_pairs": [list(p) for p in report.port_pairs],
            "unported_pairs": [list(p) for p in report.unported_pairs],
            "divergence_detectable": report.divergence_detectable,
            "internal_edges": len(report.internal_edges),
            "external_imports": (
                {name: sorted(set(sites)) for name, sites in sorted(graph.external_imports.items())}
                if graph
                else {}
            ),
        },
        "convergences": report.convergences,
        "divergences": report.divergences,
        "absences": report.absences,
        "unmapped_modules": [graph.display(m) for m in sorted(report.unmapped_modules)]
        if graph
        else [],
        "unrealized_components": report.unrealized_components,
        "blind_spots": [spot.payload() for spot in report.blind_spots],
        "ignored_suppression_keys": report.ignored_suppression_keys,
        "verdict": {
            "architecture_scan": report.verdict,
            "reasons": report.reasons,
            "blocks_promotion": False,
        },
        "advisory": {
            "blocks_promotion": False,
            "suggests_moves": False,
            "note": (
                "This report states measured facts about the code's dependency graph "
                "relative to a declared map. It names no module that should move and "
                "proposes no boundary. A divergent verdict never refuses a close, a "
                "promotion, or a case generation."
            ),
        },
    }


def _relative(path: Any) -> str:
    """Shorten a path against the working directory, for a readable report."""
    try:
        return Path(str(path)).resolve().relative_to(Path.cwd()).as_posix()
    except ValueError:
        return str(path)


def render_report_text(report: ReflexionReport) -> str:
    out: list[str] = []
    add = out.append
    graph = report.graph
    mapping = report.mapping

    add("[MEASURED] Reflexion check -- production code against the model's architecture")
    if graph is None or mapping is None:
        # The diff never ran. Printing "DIVERGENCES (0) none." here would read
        # as a clean result for a comparison that was not performed -- the same
        # false clean the whole check exists to refuse.
        add("  NOT RUN. The comparison was not performed, so there are no convergences,")
        add("  divergences, or absences to report -- not zero of them. The reason is")
        add("  below.")
        add("")
        add("[MEASURED] Reflexion verdict")
        add(f"  architecture_scan = {report.verdict}")
        for reason in report.reasons:
            add(f"    - {reason}")
        add("")
        add("  UNMAPPABLE is the answer, not `coherent`. Nothing downgrades it: there is")
        add("  no flag, key, annotation, or environment variable that turns it into a")
        add("  clean result.")
        add("")
        add("  Advisory: nothing here blocks a close, a promotion, or a case generation.")
        return "\n".join(out) + "\n"

    add(f"  map:       {_relative(mapping.origin)}")
    add(f"  code root: {_relative(graph.root)}")
    if graph and mapping:
        add(
            f"  scanned {len(graph.modules)} Python module(s); the map places "
            f"{len(mapping.modules)} of them in {len(mapping.components)} component(s)"
        )
        add(f"  extracted {len(graph.edges)} dependency edge(s) (imports + resolvable calls)")
        add(
            f"  {len(report.internal_edges)} edge(s) stay inside one component and were "
            "not checked against a port"
        )
    add("")

    if report.ignored_suppression_keys:
        add("  IGNORED suppression-shaped keys in the map (recorded, never honored):")
        for key in report.ignored_suppression_keys:
            add(f"    - {key}")
        add("    None of these changed any figure or the verdict below.")
        add("")

    if mapping:
        add("  Is a divergence even detectable here?")
        add(
            f"    component pairs with a port:    "
            f"{', '.join(f'{a}<->{b}' for a, b in report.port_pairs) or '(none)'}"
        )
        add(
            f"    component pairs with NO port:   "
            f"{', '.join(f'{a}<->{b}' for a, b in report.unported_pairs) or '(none)'}"
        )
        add(
            "    A code edge can only diverge across a pair in the second list. When "
            "that list is"
        )
        add(
            "    empty the architecture permits every pair and a clean result is true "
            "by construction."
        )
        add("")

    add(f"  CONVERGENCES ({len(report.convergences)}) -- a crossing edge the model declares a port for")
    for row in report.convergences[:40]:
        add(
            f"    {row['from_component']} -> {row['to_component']}  ({row['port']}) "
            f"{row['from']} -> {row['to']}  [{row['kind']} {row['symbol']}]  {row['site']}"
        )
    if len(report.convergences) > 40:
        add(f"    ... (+{len(report.convergences) - 40} more)")
    add("")

    add(f"  DIVERGENCES ({len(report.divergences)}) -- a crossing edge NO port declares")
    if not report.divergences:
        add("    none.")
    for row in report.divergences:
        add(
            f"    {row['site']}  {row['from_component']} -> {row['to_component']}: "
            f"{row['from']} {row['kind']}s {row['symbol']} from {row['to']}"
        )
        add(f"      {row['why']}")
    add("")

    add(f"  ABSENCES ({len(report.absences)}) -- a declared port no code edge realizes")
    if not report.absences:
        add("    none.")
    for row in report.absences:
        add(f"    {row['port']}  {row['between'][0]} <-> {row['between'][1]}")
        add(f"      {row['why']}")
    add("")

    if graph and graph.external_imports:
        add(
            f"  Out of scope: {len(graph.external_imports)} import target(s) resolve "
            "outside the scanned tree"
        )
        add(
            "  (standard library and third-party packages). They are not edges: the "
            "model declares"
        )
        add(
            "  components of THIS program. A component that reaches an external system "
            "directly is"
        )
        add("  therefore invisible to this check.")
        add(f"    {', '.join(sorted(graph.external_imports))}")
        add("")

    add("[MEASURED] Reflexion verdict")
    add(f"  architecture_scan = {report.verdict}")
    for reason in report.reasons:
        add(f"    - {reason}")
    add("")
    if report.verdict == VERDICT_UNMAPPABLE:
        add("  UNMAPPABLE is not 'clean with caveats' and not 'nothing found'. Any finding")
        add("  listed above is real; the verdict says the check could not see the whole")
        add("  target, so it will not certify what it did not observe. Nothing downgrades")
        add("  this: there is no flag, key, annotation, or environment variable that turns")
        add("  it into `coherent`.")
    elif report.verdict == VERDICT_DIVERGENT:
        add("  DIVERGENT is a FINDING, not a failure. This command exits 0. It names the")
        add("  edges and the ports; it does not say which module should move (CD-01).")
    else:
        add("  COHERENT: over the edges this extractor can resolve, every boundary")
        add("  crossing in the code has a port in the model and every port is realized.")
    add("")
    add("  Advisory: nothing here blocks a close, a promotion, or a case generation.")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def run_reflexion(
    descriptor: ArchitectureDescriptor, code: str, map_path: str
) -> ReflexionReport:
    """Load the map, extract the graph, and diff. Raises on unusable input."""
    code_root = Path(code).resolve()
    if not code_root.is_dir():
        raise CodeExtractionError(f"code root not found or not a directory: {code_root}")
    map_file = Path(map_path).resolve()
    if not map_file.is_file():
        raise ReflexionMapError(f"map file not found: {map_file}")
    try:
        source = _load_yaml(map_file)
    except DeclaredPartitionError as exc:
        raise ReflexionMapError(str(exc)) from exc
    return reflexion(descriptor, source, code_root, str(map_file))


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("tla", help="TLA+ module whose architecture the code is measured against.")
    parser.add_argument("cfg", nargs="?", help="TLC config. Defaults to <module>.cfg or MC.cfg.")
    parser.add_argument("--manifest", help="spec_manifest.yaml carrying the `architecture:` block.")
    parser.add_argument("--components", help="YAML file declaring the component partition.")
    parser.add_argument("--code", required=True, help="Root of the production tree to scan.")
    parser.add_argument(
        "--map",
        required=True,
        dest="map_path",
        help=(
            "YAML file declaring the production module -> model component map. DECLARED "
            "by the project, never inferred -- a tool that picks its own boundary makes "
            "every edge legal by construction."
        ),
    )
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--out", help="Also write the report here (ticket results/ evidence).")


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
    components_path = Path(args.components).resolve() if args.components else None

    try:
        descriptor = analyze(
            tla_path, cfg_path, manifest_path, components_path=components_path
        )
    except ModuleResolutionError as exc:
        print(
            "ERROR: the model could not be analyzed -- the module hierarchy could not be "
            f"resolved:\n  {exc}",
            file=sys.stderr,
        )
        return EXIT_ANALYSIS_ERROR
    except DeclaredPartitionError as exc:
        print(f"ERROR: declared component partition is unusable:\n  {exc}", file=sys.stderr)
        return EXIT_USAGE

    try:
        report = run_reflexion(descriptor, args.code, args.map_path)
    except (ReflexionMapError, CodeExtractionError) as exc:
        # "I could not measure this" -- the only nonzero exit this check has.
        print(f"ERROR: the reflexion check could not be run:\n  {exc}", file=sys.stderr)
        return EXIT_USAGE

    rendered = (
        json.dumps(report_payload(report), indent=2, sort_keys=False) + "\n"
        if args.format == "json"
        else render_report_text(report)
    )
    sys.stdout.write(rendered)
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered, encoding="utf-8")
        print(f"wrote evidence: {out_path}", file=sys.stderr)
    # Advisory: a divergent or unmappable codebase is a finding, not a failure.
    return EXIT_PASS


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="architecture_reflexion",
        description=(
            "Reflexion check: measure a production tree against the architecture the "
            "model declares. Advisory -- reports convergences, divergences, and "
            "absences, and blocks nothing."
        ),
    )
    add_arguments(parser)
    return run(parser.parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
