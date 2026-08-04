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
import hashlib
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

if __package__ in (None, ""):  # direct `python3 scripts/architecture_reflexion.py`
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.spec_paths import EvidencePathError, resolve_evidence_out  # noqa: E402
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
#: Bumped to 2 by AC-04, additively: every v1 field is present and unchanged,
#: and a ``basis`` block was added. The bump is not cosmetic -- ``basis`` is what
#: makes a v2 payload usable as a ``--baseline``, and a consumer must be able to
#: tell a payload that records the map it measured from one that does not.
SCHEMA_VERSION = 2

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
class BasisLimit:
    """A reason the BASIS cannot support a ``coherent`` verdict (RP-01).

    Deliberately NOT a :class:`BlindSpot`, and the distinction is the whole
    design. A blind spot is something the extractor could not SEE: nothing it
    might have found can be trusted, so every verdict collapses to
    ``unmappable``. A basis limit is the opposite situation -- the target was
    seen in full, every finding is real and is reported with its ``file:line``,
    and what cannot be supported is only the CERTIFICATE. ``coherent`` is a
    claim about the CODE, and a partition the model's own criteria reject
    cannot establish one.

    So a basis limit withholds a clean and never touches a finding. The
    alternative was measured rather than argued: making these force
    ``unmappable`` like a blind spot costs 67 of EV-02's 71 real divergence
    verdicts on the 203-partition sweep and removes exactly zero additional
    false cleans. Withholding the clean alone removes all twelve.
    """

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
    def comparison_ran(self) -> bool:
        """Whether the code side was observed at all.

        When this is false the finding lists are not empty, they are
        UNDEFINED -- there are no convergences, divergences or absences here,
        not zero of them. Every renderer branches on it.
        """
        return self.graph is not None and self.mapping is not None

    @property
    def divergence_detectable(self) -> bool:
        """Whether ANY code edge could have been a divergence.

        False when every component pair has a port -- and equally false when
        there are no component pairs at all, which is what a ONE-component
        partition produces: every code edge is internal by construction and
        nothing the code does could be seen. In both cases "no divergences" is
        a property of the declared architecture, not a measurement of the code.
        A ``coherent`` verdict on an architecture that permits everything is the
        structural twin of a clean effect report from a sandbox that observed
        nothing, and MF-027 governs both.

        RP-01: this used to be computed, published in the JSON, and read by no
        consumer, while the guard that should have read it was written
        ``len(names) >= 2`` and excluded the one blob it existed for. It is now
        the first thing :meth:`unsupported_clean` consults.
        """
        return bool(self.unported_pairs)

    def unsupported_clean(self) -> list[BasisLimit]:
        """Reasons a ``coherent`` verdict is not supportable under THIS basis.

        Computed on every call from the descriptor and the pair sets ALONE. It
        stores nothing and it never reads ``blind_spots`` or any other mutable
        field, which is what makes the refusal undowngradable: there is no list
        a caller, a later edit, or a test can empty to resurrect the clean.

        This is deliberately NOT a refusal of the partition and NOT a blind
        spot. The comparison still runs, every divergence and absence is still
        named with its ``file:line``, a ``divergent`` verdict is unaffected,
        and the command still exits 0. What is withheld is the CERTIFICATE --
        see :class:`BasisLimit`.
        """
        out: list[BasisLimit] = []
        if not self.comparison_ran:
            return out
        descriptor = self.descriptor
        names = sorted(c.name for c in descriptor.components)
        if not self.divergence_detectable:
            if len(names) < 2:
                detail = (
                    f"this architecture has {len(names)} component(s), so it has NO "
                    "component pair at all: every code edge is internal by "
                    "construction and no code edge could have been a divergence. A "
                    "clean result here is a property of the declared partition and "
                    "says nothing whatever about the code -- six lines of YAML "
                    "declaring one component would otherwise certify any codebase, "
                    "however many boundaries it violates."
                )
            else:
                total = len(self.port_pairs) + len(self.unported_pairs)
                detail = (
                    f"every one of the {total} component pair(s) in this "
                    "architecture has a port, so no code edge could have been a "
                    "divergence. 'No divergences' here is a property of the declared "
                    "architecture, not a measurement of the code, and a coherent "
                    "verdict would be true by construction. (This is what a model whose "
                    "actions all touch the same variables produces under any partition.)"
                )
            out.append(
                BasisLimit(
                    kind="unfalsifiable_coherence",
                    detail=detail,
                    where=str(descriptor.tla_path),
                )
            )
        if not descriptor.decomposes:
            failed = [c for c in descriptor.criteria if not c["met"]]
            measured = "; ".join(
                f"{c['name']} measured {c['measured']}, rule {c['rule']}" for c in failed
            )
            out.append(
                BasisLimit(
                    kind="partition_does_not_decompose",
                    detail=(
                        f"the {descriptor.partition_source.upper()} partition fails "
                        f"{len(failed)} of {len(descriptor.criteria)} decomposition "
                        f"criteria ({measured}), so this program's own published rule "
                        "says it is not a cut of this model. The findings below are "
                        "real and are reported in full -- what is withheld is the "
                        "clean: `coherent` measured against a partition the model does "
                        "not support is a different claim from `coherent` measured "
                        "against one it does, and the verdict may not spend the same "
                        "word on both. Declaring a coarser partition is the cheapest "
                        "way to make every divergence vanish with no code change."
                    ),
                    where=descriptor.partition_origin,
                )
            )
        return out

    @property
    def verdict(self) -> str:
        """The value recorded in the model's ``architecture_scan``.

        Reads ``self`` only. No flag, key, annotation, or environment variable
        participates: there is nothing to pass in that could change the answer.

        The order is the meaning. A blind spot or an unobserved code side beats
        everything, because nothing measured under one can be trusted. A
        FINDING beats a basis limit, because a divergence the extractor saw at
        a `file:line` is a fact about the code whatever the standing of the
        partition it crossed -- withholding it would trade twelve false cleans
        for sixty-seven suppressed real findings. A basis limit beats only the
        clean, which is the one verdict that claims the code was vindicated.
        """
        if self.blind_spots:
            return VERDICT_UNMAPPABLE
        if not self.comparison_ran:
            # No code side was observed. `divergences == []` is undefined here,
            # not zero, so neither `coherent` nor `divergent` is sayable.
            return VERDICT_UNMAPPABLE
        if self.divergences or self.absences:
            return VERDICT_DIVERGENT
        if self.unsupported_clean():
            return VERDICT_UNMAPPABLE
        return VERDICT_COHERENT

    @property
    def reasons(self) -> list[str]:
        out: list[str] = []
        for spot in self.blind_spots:
            where = f" ({spot.where})" if spot.where else ""
            out.append(f"[{spot.kind}] {spot.detail}{where}")
        # Always listed, and listed under a DIVERGENT verdict too: a reader who
        # is about to act on these findings must know what they were measured
        # against, and a reader who sees none must know why that is not a clean.
        for limit in self.unsupported_clean():
            where = f" ({limit.where})" if limit.where else ""
            out.append(f"[{limit.kind}] {limit.detail}{where}")
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

    # RP-01. A guard used to sit here reading `if not report.unported_pairs and
    # len(names) >= 2`, appending a blind spot. It excluded the strongest case
    # of the very thing it was written to catch -- a ONE-component partition has
    # no pairs at all, so it passed vacuously and six lines of YAML certified a
    # codebase with four real divergences. There is now no guard here at all:
    # the condition is DERIVED by `ReflexionReport.unsupported_clean()` from the
    # descriptor and the pair sets, and read by the verdict itself. Nothing is
    # appended to a list, so nothing can be forgotten, emptied, or ignored --
    # which is exactly how `divergence_detectable` came to be computed,
    # published in the JSON, and consulted by no consumer.

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
# AC-04 -- the BASIS: what a delta is computed against
# --------------------------------------------------------------------------
#
# The divergence delta is a number that makes people look good, and it is
# trivially forgeable: AC-02 recorded that any divergence disappears if the map
# moves the offending module into the component it reaches -- no code change,
# verdict flips. If the map may differ between the before scan and the after
# scan, the delta measures the MAP, not the refactor.
#
# So a scan records the identity of everything the comparison was made against,
# and the delta refuses to attribute a change to the code unless that identity
# held:
#
#   map_digest           the DECLARED placements (module -> component) and the
#                        language. Not the file's bytes and not its path: a
#                        reformatted or relocated map with identical placements
#                        is the same map, and a comment change must not read as
#                        a boundary change.
#   architecture_digest  the MODEL side -- the component names, the port pairs,
#                        and the actions that cross each port. A port added to
#                        the model turns a divergence into a convergence with no
#                        code change at all, which is the same forgery from the
#                        other end.
#   scanned_modules      the files the extractor actually read. Needed to tell
#                        "this module was deleted" from "this module stopped
#                        being mapped" when an edge disappears -- see
#                        ``_classify_lost``.


DELTA_SCHEMA = "tla-spec-dev/architecture-delta"
DELTA_SCHEMA_VERSION = 1

#: The delta's headline verdict. ``improved``/``worsened``/``unchanged`` are
#: measurements of the code; the other two are refusals to call the number a
#: refactor result.
DIRECTION_IMPROVED = "improved"
DIRECTION_WORSENED = "worsened"
DIRECTION_UNCHANGED = "unchanged"
DIRECTION_UNVERIFIED = "unverified"
DIRECTION_UNATTRIBUTABLE = "unattributable"

#: How a before/after pair is related. ``code_only`` is the only one under which
#: the headline delta is a fact about the code alone.
ATTRIBUTION_CODE_ONLY = "code_only"
ATTRIBUTION_PARTIAL = "partial"
ATTRIBUTION_UNATTRIBUTABLE = "unattributable"


class BaselineError(Exception):
    """A baseline that cannot serve as one.

    Unusable INPUT, like :class:`ReflexionMapError` -- exits nonzero. Computing
    a delta against a scan whose map is unknown, or against a scan whose
    comparison never ran, would print an improvement derived from nothing.
    """


def _digest(payload: Any) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(blob).hexdigest()


def scan_basis(report: ReflexionReport) -> dict[str, Any]:
    """Everything this scan was measured AGAINST, recorded with the scan.

    Emitted into every report payload so that a later run can prove the two
    scans were measured against the same declared boundary -- or say plainly
    that they were not.
    """
    mapping = report.mapping
    graph = report.graph
    descriptor = report.descriptor

    id_to_name = {c.cid: c.name for c in descriptor.components}
    port_actions: dict[str, list[str]] = {}
    for port in descriptor.ports:
        left, right = port.between
        if left in id_to_name and right in id_to_name:
            key = "|".join(sorted((id_to_name[left], id_to_name[right])))
            port_actions[key] = sorted(port.actions)
    architecture = {
        "components": sorted(id_to_name.values()),
        "ports": {key: port_actions[key] for key in sorted(port_actions)},
    }

    placements: dict[str, str] = {}
    map_digest: str | None = None
    if mapping is not None:
        placements = {key: mapping.modules[key] for key in sorted(mapping.modules)}
        map_digest = _digest({"language": mapping.language, "placements": placements})

    unsupported = report.unsupported_clean()
    return {
        "map_origin": mapping.origin if mapping else None,
        "map_language": mapping.language if mapping else None,
        "map_digest": map_digest,
        "placements": placements,
        "code_root": str(graph.root) if graph else None,
        "scanned_modules": sorted(graph.modules) if graph else [],
        "architecture_digest": _digest(architecture),
        "architecture_components": architecture["components"],
        "architecture_ports": [key.split("|") for key in sorted(port_actions)],
        "architecture_port_actions": architecture["ports"],
        "comparison_ran": mapping is not None and graph is not None,
        # RP-01: the PARTITION half of the basis. A scan is measured against a
        # cut somebody chose, and whether the model's own criteria call that
        # choice a cut is the difference between a clean that means something
        # and one that was bought with six lines of YAML. It travels with the
        # scan, in this block and again under `verdict`, so no consumer can
        # reach the verdict without passing the basis it rests on.
        "partition_source": descriptor.partition_source,
        "partition_origin": descriptor.partition_origin,
        "partition_decomposes": descriptor.decomposes,
        "partition_criteria": descriptor.criteria,
        "partition_failed_criteria": [
            c["name"] for c in descriptor.criteria if not c["met"]
        ],
        "component_count": len(descriptor.components),
        "divergence_detectable": report.divergence_detectable
        if report.comparison_ran
        else None,
        "clean_result_supportable": not unsupported if report.comparison_ran else None,
        "unsupported_clean_reasons": [spot.payload() for spot in unsupported],
    }


# --------------------------------------------------------------------------
# AC-04 -- the before/after delta
# --------------------------------------------------------------------------
#
# MF-020, applied to structure. A projected complexity reduction once turned out
# to be a DELETED TRANSITION rather than a re-representation, and the
# distinct-state count was structurally blind to it. The same blindness has an
# exact structural twin: a divergence count can fall because the offending edge
# was removed, because the file was deleted, or because the module stopped being
# mapped and its edges stopped being looked at. The count cannot tell those
# apart. So this delta reports the SPECIFIC EDGES that disappeared, classifies
# each one, and a drop it cannot enumerate is ``unverified`` -- never an
# improvement.
#
# The unit of the delta is a DISTINCT DEPENDENCY: (from, to, kind, symbol). The
# line number is deliberately not part of the identity -- a refactor that moves
# code within a file shifts every line, and an edge set keyed by line would
# report the entire graph as lost and regained. Every site of a dependency is
# still listed on its row, so a reader can navigate to all of them.


def _edge_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        str(row.get("from", "")),
        str(row.get("to", "")),
        str(row.get("kind", "")),
        str(row.get("symbol", "")),
    )


def _group_edges(rows: Sequence[dict[str, Any]]) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    """Collapse per-site rows into one row per distinct dependency."""
    grouped: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        key = _edge_key(row)
        entry = grouped.get(key)
        if entry is None:
            entry = {
                "from": row.get("from"),
                "to": row.get("to"),
                "kind": row.get("kind"),
                "symbol": row.get("symbol"),
                "from_component": row.get("from_component"),
                "to_component": row.get("to_component"),
                "pair": row.get("pair"),
                "port": row.get("port"),
                "sites": [],
            }
            grouped[key] = entry
        site = row.get("site") or f"{row.get('file')}:{row.get('line')}"
        if site not in entry["sites"]:
            entry["sites"].append(site)
    return grouped


def _absence_key(row: dict[str, Any]) -> tuple[str, str]:
    between = row.get("between") or []
    pair = sorted(str(x) for x in between)
    while len(pair) < 2:
        pair.append("")
    return (pair[0], pair[1])


def _basis_of(payload: dict[str, Any]) -> dict[str, Any]:
    """The reflexion block of a scan payload, whichever way it was written.

    ``analyze architecture --format json`` nests the reflexion report under
    ``reflexion``; the standalone script emits it as the document root.
    """
    if isinstance(payload.get("reflexion"), dict):
        return payload["reflexion"]
    return payload


def load_baseline(path: Path) -> dict[str, Any]:
    """Read a previous scan as the baseline. Refuses anything that cannot be one.

    Each refusal below exists because the alternative is a printed improvement
    that no measurement supports:

    * a text report -- readable, but it does not enumerate the edges, so a drop
      measured against it is unverified by construction (the MF-020 rule);
    * a payload from a scan whose comparison NEVER RAN -- "0 divergences" was
      never measured there, so a later 0 is not a delta of anything;
    * a payload with no ``basis`` -- the map it was measured against is
      unrecoverable, and a delta across two unknown maps measures the maps.
    """
    path = Path(path)
    if not path.is_file():
        raise BaselineError(f"baseline scan not found: {path}")
    text = path.read_text(encoding="utf-8")
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise BaselineError(
            f"{path}: not a JSON scan payload ({exc}). The baseline must be the output of "
            "`analyze architecture --format json`. A text report does not enumerate the "
            "edges, and a divergence drop measured against counts alone is unverified by "
            "construction -- the exact blindness MF-020 found in the distinct-state count."
        ) from exc
    if not isinstance(payload, dict):
        raise BaselineError(f"{path}: not a JSON object")
    block = _basis_of(payload)
    if block.get("schema") not in (SCHEMA, None):
        raise BaselineError(
            f"{path}: schema `{block.get('schema')}` is not `{SCHEMA}`; this is not an "
            "architecture scan"
        )
    basis = block.get("basis")
    if isinstance(basis, dict) and not basis.get("comparison_ran"):
        # Checked before the digest, because this scan has a legitimate reason to
        # carry no map: the diff never happened. "Zero divergences" was never
        # measured there, so a later zero is not a delta of anything.
        raise BaselineError(
            f"{path}: the baseline scan's comparison never ran (verdict "
            f"`{(block.get('verdict') or {}).get('architecture_scan')}`), so it holds no "
            "convergences, divergences, or absences -- not zero of them. There is nothing "
            "to compare against."
        )
    if not isinstance(basis, dict) or not basis.get("map_digest"):
        raise BaselineError(
            f"{path}: carries no `basis.map_digest`, so the map it was measured against "
            "cannot be identified. A delta across two maps that cannot be shown to be the "
            "same map measures the MAP, not the refactor. Re-run the baseline scan with a "
            f"build that emits schema_version {SCHEMA_VERSION}."
        )
    for key in ("convergences", "divergences", "absences"):
        if not isinstance(block.get(key), list):
            raise BaselineError(
                f"{path}: `{key}` is not an enumerated list. A drop reported without the "
                "edges that disappeared is unverified by construction (MF-020)."
            )
    return block


def _compare_basis(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """How the two scans' declared basis differ, and what that costs the delta."""
    before_placements = before.get("placements") or {}
    after_placements = after.get("placements") or {}
    shared = sorted(set(before_placements) & set(after_placements))

    reassigned = [
        {
            "module": module,
            "from_component": before_placements[module],
            "to_component": after_placements[module],
        }
        for module in shared
        if before_placements[module] != after_placements[module]
    ]
    added = sorted(set(after_placements) - set(before_placements))
    removed = sorted(set(before_placements) - set(after_placements))

    before_components = sorted(set(before_placements.values()))
    after_components = sorted(set(after_placements.values()))

    architecture_changed = before.get("architecture_digest") != after.get("architecture_digest")
    before_ports = {tuple(p) for p in (before.get("architecture_ports") or [])}
    after_ports = {tuple(p) for p in (after.get("architecture_ports") or [])}

    reasons: list[str] = []
    if architecture_changed:
        reasons.append(
            "the MODEL side changed between the two scans (components or ports differ), so "
            "the two runs do not share a definition of what a divergence IS. Adding a port "
            "converts a divergence into a convergence with no code change."
        )
    if reassigned:
        listed = ", ".join(
            f"{row['module']} ({row['from_component']} -> {row['to_component']})"
            for row in reassigned[:8]
        )
        if len(reassigned) > 8:
            listed += f", ... (+{len(reassigned) - 8} more)"
        reasons.append(
            f"{len(reassigned)} module(s) present in both scans were RE-PLACED by the map: "
            f"{listed}. Re-placing a module moves the boundary, not the code -- it is the "
            "one edit that makes any divergence disappear for free."
        )
    if set(before_components) != set(after_components):
        reasons.append(
            "the map's component set changed "
            f"({', '.join(before_components)} -> {', '.join(after_components)})"
        )

    if reasons:
        attribution = ATTRIBUTION_UNATTRIBUTABLE
    elif added or removed:
        attribution = ATTRIBUTION_PARTIAL
    else:
        attribution = ATTRIBUTION_CODE_ONLY

    if attribution == ATTRIBUTION_PARTIAL:
        reasons.append(
            f"the map gained {len(added)} module placement(s) and lost {len(removed)}. No "
            "surviving module was re-placed, so the boundary held -- but where a NEW module "
            "was placed was declared by this change, and edges touching one are not a "
            "measurement of the code alone. The `stable_basis` figures below exclude them."
        )

    return {
        "attribution": attribution,
        "reasons": reasons,
        "map_digest_before": before.get("map_digest"),
        "map_digest_after": after.get("map_digest"),
        "map_unchanged": before.get("map_digest") == after.get("map_digest"),
        "architecture_digest_before": before.get("architecture_digest"),
        "architecture_digest_after": after.get("architecture_digest"),
        "architecture_unchanged": not architecture_changed,
        "map_changes": {
            "reassigned": reassigned,
            "added": added,
            "removed": removed,
            "components_before": before_components,
            "components_after": after_components,
        },
        "architecture_changes": {
            "ports_added": [list(p) for p in sorted(after_ports - before_ports)],
            "ports_removed": [list(p) for p in sorted(before_ports - after_ports)],
            "components_before": before.get("architecture_components") or [],
            "components_after": after.get("architecture_components") or [],
        },
        "stable_modules": [
            module for module in shared if before_placements[module] == after_placements[module]
        ],
    }


def _classify_lost(
    row: dict[str, Any], before: dict[str, Any], after: dict[str, Any]
) -> dict[str, Any]:
    """Why one edge is no longer reported. The MF-020 question, per edge.

    A count cannot distinguish these four. Whether the delta is evidence of
    anything depends entirely on which one each disappearance was.
    """
    after_placements = after.get("placements") or {}
    after_scanned = set(after.get("scanned_modules") or [])
    before_placements = before.get("placements") or {}

    for endpoint in ("from", "to"):
        module = str(row.get(endpoint) or "")
        if module in after_placements:
            if before_placements.get(module) != after_placements.get(module):
                return {
                    "reason": "endpoint_reassigned",
                    "module": module,
                    "detail": (
                        f"`{module}` was re-placed by the map "
                        f"({before_placements.get(module)} -> {after_placements[module]}). The "
                        "edge did not go away; the boundary it crossed did."
                    ),
                    "verifies_drop": False,
                }
            continue
        if module in after_scanned:
            return {
                "reason": "endpoint_unmapped",
                "module": module,
                "detail": (
                    f"`{module}` is still in the scanned tree but the map no longer places "
                    "it, so its edges are no longer judged at all. The edge left the "
                    "MEASUREMENT, not the code -- the structural twin of MF-020's deleted "
                    "self-loop, and it is why this drop is not an improvement."
                ),
                "verifies_drop": False,
            }
        return {
            "reason": "endpoint_left_tree",
            "module": module,
            "detail": (
                f"`{module}` is no longer in the scanned tree (deleted, renamed, or moved "
                "out of --code). The coupling is gone because the file is gone -- a "
                "deletion, which is a different fact from a re-representation."
            ),
            "verifies_drop": True,
        }
    return {
        "reason": "dependency_removed",
        "module": None,
        "detail": (
            "both endpoints are still scanned and still placed in the same components, and "
            "the dependency between them is gone. This is the disappearance a refactor "
            "produces."
        ),
        "verifies_drop": True,
    }


def _delta_block(
    before_rows: Sequence[dict[str, Any]],
    after_rows: Sequence[dict[str, Any]],
    before_basis: dict[str, Any],
    after_basis: dict[str, Any],
    stable: set[str] | None = None,
) -> dict[str, Any]:
    before_edges = _group_edges(before_rows)
    after_edges = _group_edges(after_rows)
    lost_keys = sorted(set(before_edges) - set(after_edges))
    gained_keys = sorted(set(after_edges) - set(before_edges))

    lost = []
    for key in lost_keys:
        row = dict(before_edges[key])
        row["classification"] = _classify_lost(row, before_basis, after_basis)
        lost.append(row)
    gained = [dict(after_edges[key]) for key in gained_keys]

    block: dict[str, Any] = {
        "before": len(before_edges),
        "after": len(after_edges),
        "delta": len(after_edges) - len(before_edges),
        "before_sites": len(before_rows),
        "after_sites": len(after_rows),
        "unchanged": len(set(before_edges) & set(after_edges)),
        "lost": lost,
        "gained": gained,
        # A self-check on the arithmetic. It can only fail on a hand-edited
        # payload -- the counts are DERIVED from the enumeration here, which is
        # precisely why "a drop with no edges" is not expressible.
        "accounted": (len(after_edges) - len(before_edges)) == (len(gained) - len(lost)),
    }
    if stable is not None:
        def _stable(rows: dict[tuple[str, str, str, str], dict[str, Any]]) -> set[Any]:
            return {
                key
                for key, row in rows.items()
                if str(row.get("from")) in stable and str(row.get("to")) in stable
            }

        stable_before = _stable(before_edges)
        stable_after = _stable(after_edges)
        block["stable_basis"] = {
            "before": len(stable_before),
            "after": len(stable_after),
            "delta": len(stable_after) - len(stable_before),
            "lost": [dict(before_edges[k]) for k in sorted(stable_before - stable_after)],
            "gained": [dict(after_edges[k]) for k in sorted(stable_after - stable_before)],
            "note": (
                "restricted to modules present in BOTH scans with the same declared "
                "component. This subset is the part of the delta the map did not touch."
            ),
        }
    return block


def _absence_delta(
    before_rows: Sequence[dict[str, Any]], after_rows: Sequence[dict[str, Any]]
) -> dict[str, Any]:
    before_map = {_absence_key(r): r for r in before_rows if isinstance(r, dict)}
    after_map = {_absence_key(r): r for r in after_rows if isinstance(r, dict)}
    return {
        "before": len(before_map),
        "after": len(after_map),
        "delta": len(after_map) - len(before_map),
        "lost": [before_map[k] for k in sorted(set(before_map) - set(after_map))],
        "gained": [after_map[k] for k in sorted(set(after_map) - set(before_map))],
    }


def structural_delta(baseline: dict[str, Any], report: ReflexionReport) -> dict[str, Any]:
    """The before/after comparison. Advisory: it gates nothing and suggests nothing.

    The headline is the DIVERGENCE delta, because a divergence is the only one of
    the three categories that names a coupling the architecture does not admit.
    Absences and convergences are reported beside it, never folded into it: a
    port that stopped being realized is a different finding from a boundary that
    started being crossed, and averaging them would hide both.
    """
    after_basis = scan_basis(report)
    before_basis = baseline.get("basis") or {}
    basis = _compare_basis(before_basis, after_basis)
    stable = set(basis["stable_modules"])

    current = report_payload(report)
    # `or []` on BOTH sides: a scan whose comparison never ran now carries
    # `null` rather than `[]` for its finding lists (RP-01), and the delta must
    # not read that as a measured zero. It does not -- `comparison_ran` is
    # checked below and forces `unattributable` -- but the arithmetic that runs
    # first needs a list, and the counts it produces are discarded there.
    divergences = _delta_block(
        baseline.get("divergences") or [],
        current["divergences"] or [],
        before_basis,
        after_basis,
        stable,
    )
    convergences = _delta_block(
        baseline.get("convergences") or [],
        current["convergences"] or [],
        before_basis,
        after_basis,
        stable,
    )
    absences = _absence_delta(baseline.get("absences") or [], current["absences"] or [])

    unverifying = [
        row
        for row in divergences["lost"]
        if not row["classification"]["verifies_drop"]
    ]
    removal_only = bool(divergences["lost"]) and all(
        row["classification"]["reason"] == "endpoint_left_tree" for row in divergences["lost"]
    )

    why: list[str] = []
    red_flags: list[str] = []

    if not after_basis.get("comparison_ran"):
        # THIS scan's diff never ran (the model has no architecture to measure
        # against). Its zeroes were never measured, so every baseline finding
        # would read as "disappeared" and the delta would report a clean sweep
        # for a comparison that did not happen -- the false clean the whole
        # check exists to refuse, one level up.
        direction = DIRECTION_UNATTRIBUTABLE
        basis["attribution"] = ATTRIBUTION_UNATTRIBUTABLE
        why.append(
            "this scan's comparison DID NOT RUN, so it holds no convergences, divergences, "
            "or absences -- not zero of them. Nothing here disappeared; it was never "
            "measured. See the reflexion verdict above for why."
        )
    elif basis["attribution"] == ATTRIBUTION_UNATTRIBUTABLE:
        direction = DIRECTION_UNATTRIBUTABLE
        why.append(
            "the two scans were not measured against the same declared basis, so this is "
            "not a refactor result. The numbers below are real; what they are a fact ABOUT "
            "is undetermined."
        )
        why.extend(basis["reasons"])
    elif divergences["delta"] < 0 and unverifying:
        direction = DIRECTION_UNVERIFIED
        why.append(
            f"{len(unverifying)} of the {len(divergences['lost'])} disappeared divergence(s) "
            "left the MEASUREMENT rather than the code. A drop that is not accounted for by "
            "edges that actually went away is unverified by construction -- the structural "
            "form of MF-020, where a projected reduction turned out to be a deleted "
            "transition the distinct-state count could not see."
        )
        why.extend(row["classification"]["detail"] for row in unverifying[:5])
    elif not divergences["accounted"]:
        direction = DIRECTION_UNVERIFIED
        why.append(
            "the enumerated edges do not account for the change in the count. The payload "
            "was edited by hand; the delta is not usable."
        )
    elif divergences["delta"] < 0:
        direction = DIRECTION_IMPROVED
        why.append(
            f"{-divergences['delta']} fewer distinct divergent dependenc(ies), each one "
            "enumerated below with the site it used to sit at."
        )
    elif divergences["delta"] > 0:
        direction = DIRECTION_WORSENED
        why.append(
            f"{divergences['delta']} more distinct divergent dependenc(ies). Recorded, not "
            "refused: this delta gates nothing."
        )
    else:
        direction = DIRECTION_UNCHANGED
        why.append(
            f"the divergence count did not change ({divergences['before']} -> "
            f"{divergences['after']})."
            + (
                f" {len(divergences['lost'])} disappeared and {len(divergences['gained'])} "
                "appeared, so 'unchanged' is a count, not a claim that nothing moved."
                if divergences["lost"] or divergences["gained"]
                else ""
            )
        )

    if removal_only and direction == DIRECTION_IMPROVED:
        red_flags.append(
            "every disappeared divergence is accounted for by a module that LEFT THE "
            "SCANNED TREE. Deleting the file removes the coupling; it does not show the "
            "responsibility was re-represented somewhere legal. MF-020 is the precedent: "
            "record where the behavior went, or say it was deleted."
        )
    if absences["delta"] > 0:
        red_flags.append(
            f"{absences['delta']} more declared port(s) are now realized by no code edge. A "
            "refactor that lowers divergences by severing a declared interaction has moved "
            "the finding, not removed it."
        )
    if basis["attribution"] == ATTRIBUTION_PARTIAL:
        red_flags.append(
            "the module set changed between the scans; read `stable_basis` for the part of "
            "the delta the map did not touch."
        )

    return {
        "schema": DELTA_SCHEMA,
        "schema_version": DELTA_SCHEMA_VERSION,
        "baseline": {
            "map_origin": before_basis.get("map_origin"),
            "map_digest": before_basis.get("map_digest"),
            "architecture_digest": before_basis.get("architecture_digest"),
            "code_root": before_basis.get("code_root"),
            "verdict": (baseline.get("verdict") or {}).get("architecture_scan"),
            "modules_scanned": len(before_basis.get("scanned_modules") or []),
        },
        "current": {
            "map_origin": after_basis.get("map_origin"),
            "map_digest": after_basis.get("map_digest"),
            "architecture_digest": after_basis.get("architecture_digest"),
            "code_root": after_basis.get("code_root"),
            "verdict": report.verdict,
            "modules_scanned": len(after_basis.get("scanned_modules") or []),
        },
        "basis": {
            key: value for key, value in basis.items() if key != "stable_modules"
        },
        "divergences": divergences,
        "convergences": convergences,
        "absences": absences,
        "verdict": {
            "direction": direction,
            "why": why,
            "red_flags": red_flags,
            "blocks_promotion": False,
        },
        "advisory": {
            "blocks_promotion": False,
            "suggests_moves": False,
            "note": (
                "The delta is EVIDENCE FOR A PERSON. A rise is recorded, never refused; a "
                "drop is recorded with the edges that disappeared, or it is not called an "
                "improvement. Nothing here names a module that should move (CD-01)."
            ),
        },
    }


def render_delta_text(delta: dict[str, Any]) -> str:
    out: list[str] = []
    add = out.append
    verdict = delta["verdict"]
    basis = delta["basis"]

    add("[MEASURED] Architecture delta -- this scan against a recorded baseline")
    add(f"  baseline map:  {_relative(delta['baseline']['map_origin'])}")
    add(f"    digest:      {delta['baseline']['map_digest']}")
    add(f"  current map:   {_relative(delta['current']['map_origin'])}")
    add(f"    digest:      {delta['current']['map_digest']}")
    add(
        f"  model side:    architecture digest "
        f"{'UNCHANGED' if basis['architecture_unchanged'] else 'CHANGED'} "
        f"({delta['baseline']['architecture_digest']} -> "
        f"{delta['current']['architecture_digest']})"
    )
    add(f"  attribution:   {basis['attribution']}")
    for reason in basis["reasons"]:
        add(f"    - {reason}")
    add("")

    for name in ("divergences", "convergences"):
        block = delta[name]
        add(
            f"  {name.upper()}: {block['before']} -> {block['after']} "
            f"({block['delta']:+d} distinct dependenc(ies); "
            f"{block['before_sites']} -> {block['after_sites']} sites)"
        )
        if block["lost"]:
            add(f"    LOST ({len(block['lost'])}):")
            for row in block["lost"]:
                add(
                    f"      - {row['from']} -{row['kind']}-> {row['to']}  "
                    f"[{row['symbol']}]  was at {', '.join(row['sites'])}"
                )
                if name == "divergences":
                    add(f"        {row['classification']['reason']}: {row['classification']['detail']}")
        if block["gained"]:
            add(f"    GAINED ({len(block['gained'])}):")
            for row in block["gained"]:
                add(
                    f"      + {row['from']} -{row['kind']}-> {row['to']}  "
                    f"[{row['symbol']}]  at {', '.join(row['sites'])}"
                )
        if not block["lost"] and not block["gained"]:
            add("    no dependency appeared or disappeared.")
        if "stable_basis" in block and basis["attribution"] != ATTRIBUTION_CODE_ONLY:
            stable = block["stable_basis"]
            add(
                f"    stable-basis only (modules in both scans, same component): "
                f"{stable['before']} -> {stable['after']} ({stable['delta']:+d})"
            )
        add("")

    absences = delta["absences"]
    add(f"  ABSENCES: {absences['before']} -> {absences['after']} ({absences['delta']:+d})")
    for row in absences["gained"]:
        add(f"      + {row.get('port')}  {' <-> '.join(row.get('between') or [])}")
    for row in absences["lost"]:
        add(f"      - {row.get('port')}  {' <-> '.join(row.get('between') or [])}")
    add("")

    add("[MEASURED] Delta verdict")
    add(f"  direction = {verdict['direction']}")
    for reason in verdict["why"]:
        add(f"    - {reason}")
    for flag in verdict["red_flags"]:
        add(f"    RED FLAG: {flag}")
    add("")
    if verdict["direction"] == DIRECTION_UNATTRIBUTABLE:
        add("  UNATTRIBUTABLE is not a bad result and not a good one. The two scans do not")
        add("  share a basis, so no number here is a fact about the refactor. Re-run the")
        add("  baseline against the current map to get a comparison, and say in the record")
        add("  that the map changed.")
    elif verdict["direction"] == DIRECTION_UNVERIFIED:
        add("  UNVERIFIED: the count fell and the edges do not explain why. This is the")
        add("  structural MF-020. It is reported as unverified rather than as an")
        add("  improvement, and nothing downgrades that.")
    add("  Advisory: nothing here blocks a close, a promotion, or a case generation.")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------


def report_payload(report: ReflexionReport) -> dict[str, Any]:
    graph = report.graph
    mapping = report.mapping
    ran = report.comparison_ran
    # RP-01, the AC-03-DF-01 rule applied one field over. When the comparison
    # never ran there are no convergences, divergences or absences here -- NOT
    # zero of them, which is what `[]` says to a consumer and what the text
    # renderer has always refused to print. Undefined is `null` and carries its
    # reason in `not_measured`.
    not_measured = (
        None
        if ran
        else (
            "NOT MEASURED: the comparison never ran, so the finding lists and the "
            "counts they summarize are undefined rather than empty. See "
            "`verdict.reasons` for why. A consumer that reads a `0` or an `[]` here "
            "as a measured result is reading a clean report on a target that was "
            "never observed."
        )
    )
    basis = scan_basis(report)
    unsupported = report.unsupported_clean()
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "map": mapping.origin if mapping else None,
        "code_root": str(graph.root) if graph else None,
        "language": mapping.language if mapping else None,
        "measured": {
            "not_measured": not_measured,
            "modules_scanned": len(graph.modules) if ran else None,
            "modules_mapped": len(mapping.modules) if ran else None,
            "edges_extracted": len(graph.edges) if ran else None,
            "component_pairs": (len(report.port_pairs) + len(report.unported_pairs))
            if ran
            else None,
            "ported_pairs": [list(p) for p in report.port_pairs] if ran else None,
            "unported_pairs": [list(p) for p in report.unported_pairs] if ran else None,
            "divergence_detectable": report.divergence_detectable if ran else None,
            "internal_edges": len(report.internal_edges) if ran else None,
            "external_imports": (
                {name: sorted(set(sites)) for name, sites in sorted(graph.external_imports.items())}
                if ran
                else None
            ),
        },
        # AC-04: what this scan was measured AGAINST, recorded WITH the scan so
        # that a later delta can prove -- or deny -- that the two runs shared a
        # boundary. Without this a delta measures the map. RP-01 added the
        # partition half: the model side of the basis, with every decomposition
        # criterion and its measurement.
        "basis": basis,
        "convergences": report.convergences if ran else None,
        "divergences": report.divergences if ran else None,
        "absences": report.absences if ran else None,
        "unmapped_modules": [graph.display(m) for m in sorted(report.unmapped_modules)]
        if ran
        else None,
        "unrealized_components": report.unrealized_components if ran else None,
        "blind_spots": [spot.payload() for spot in report.blind_spots],
        # RP-01. Beside `blind_spots`, never inside it: a blind spot is
        # something the extractor could not see and forces `unmappable`; a
        # basis limit is something it saw perfectly well against a boundary
        # that cannot support a clean, and withholds only `coherent`.
        "basis_limits": [limit.payload() for limit in unsupported],
        "ignored_suppression_keys": report.ignored_suppression_keys,
        "verdict": {
            "architecture_scan": report.verdict,
            "reasons": report.reasons,
            "blocks_promotion": False,
            # RP-01: the basis travels WITH the verdict, not only in a sibling
            # block a consumer may never open. Everything here is needed to
            # decide whether this verdict's word can be taken at face value.
            "measured_against": {
                "partition_source": basis["partition_source"],
                "partition_origin": basis["partition_origin"],
                "component_count": basis["component_count"],
                "partition_decomposes": basis["partition_decomposes"],
                "partition_criteria": basis["partition_criteria"],
                "partition_failed_criteria": basis["partition_failed_criteria"],
                "divergence_detectable": basis["divergence_detectable"],
                "comparison_ran": basis["comparison_ran"],
            },
            "clean_result_supportable": basis["clean_result_supportable"],
            "unsupported_clean_reasons": [spot.payload() for spot in unsupported],
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

    # RP-01: the BASIS, printed before the findings and again beside the
    # verdict. A reader who sees only the counts cannot tell a clean that was
    # measured from a clean that was declared.
    descriptor = report.descriptor
    add("  Measured against this partition -- the basis of every figure below:")
    add(f"    source:  {descriptor.partition_source.upper()}")
    add(f"    origin:  {descriptor.partition_origin}")
    add(
        "    components: "
        + (", ".join(sorted(c.name for c in descriptor.components)) or "(none)")
    )
    add("    does this partition decompose the model?")
    for criterion in descriptor.criteria:
        mark = "OK  " if criterion["met"] else "FAIL"
        add(
            f"      [{mark}] {criterion['name']}: measured {criterion['measured']}, "
            f"rule {criterion['rule']}"
        )
    if descriptor.decomposes:
        add("      -> every criterion is met: this partition IS a cut of the model.")
    else:
        failed = ", ".join(c["name"] for c in descriptor.criteria if not c["met"])
        add(
            f"      -> DOES NOT DECOMPOSE ({failed}). The comparison still runs and "
            "every finding"
        )
        add(
            "         below is real, but this program's own rule says this is not a "
            "cut, so a"
        )
        add("         clean result measured against it is not a clean result about the code.")
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
        add(
            f"    divergence_detectable = "
            f"{'true' if report.divergence_detectable else 'false'}"
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
    # RP-01: the basis, restated where the verdict is read. A consumer that
    # stops at the verdict line must still be told what it was measured against.
    add("  measured against:")
    add(
        f"    partition:              {descriptor.partition_source.upper()}, "
        f"{len(descriptor.components)} component(s)"
    )
    add(
        f"    partition decomposes:   "
        f"{'yes' if descriptor.decomposes else 'NO -- fails ' + ', '.join(c['name'] for c in descriptor.criteria if not c['met'])}"
    )
    add(
        f"    divergence_detectable:  "
        f"{'true' if report.divergence_detectable else 'FALSE -- no code edge could have been a divergence'}"
    )
    add(
        f"    a clean result is       "
        f"{'SUPPORTABLE on this basis' if not report.unsupported_clean() else 'NOT SUPPORTABLE on this basis'}"
    )
    add("")
    if report.verdict == VERDICT_UNMAPPABLE:
        add("  UNMAPPABLE is not 'clean with caveats' and not 'nothing found'. Any finding")
        add("  listed above is real; the verdict says the check could not see the whole")
        add("  target, so it will not certify what it did not observe. Nothing downgrades")
        add("  this: there is no flag, key, annotation, or environment variable that turns")
        add("  it into `coherent`.")
        if report.unsupported_clean() and not report.blind_spots:
            add("")
            add("  Here it is the BASIS, not the extractor, that withholds the clean. The")
            add("  partition is not refused and the comparison was not skipped: everything")
            add("  above was measured, this command exits 0, and nothing is blocked. What")
            add("  is withheld is the word `coherent`, which is a claim about the CODE --")
            add("  and it cannot be bought by declaring a coarser boundary.")
    elif report.verdict == VERDICT_DIVERGENT:
        add("  DIVERGENT is a FINDING, not a failure. This command exits 0. It names the")
        add("  edges and the ports; it does not say which module should move (CD-01).")
        if report.unsupported_clean():
            add("")
            add("  The findings stand on their own -- an edge the extractor resolved to a")
            add("  file:line is a fact about the code. But the boundary they were measured")
            add("  ACROSS is one this program's own criteria reject, so their number is not")
            add("  a score: a coarser partition would report fewer of them with no code")
            add("  change, and this basis could not have produced a `coherent` either way.")
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
    parser.add_argument(
        "--baseline",
        help=(
            "AC-04 refactor delta: a previous `--format json` scan to compare this one "
            "against. Reports the divergence delta with the specific edges gained and "
            "lost, and refuses to call a drop an improvement when the two scans were not "
            "measured against the same declared map and model."
        ),
    )
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument(
        "--out",
        help=(
            "Also write the report here. RC-01: the path MUST resolve under a "
            "`results/` directory -- that is the surface the `evidence_report` "
            "effect port declares, and a write anywhere else is undeclared."
        ),
    )


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

    delta = None
    if getattr(args, "baseline", None):
        try:
            delta = structural_delta(load_baseline(Path(args.baseline)), report)
        except BaselineError as exc:
            print(f"ERROR: the baseline scan is not usable as one:\n  {exc}", file=sys.stderr)
            return EXIT_USAGE

    if args.format == "json":
        payload = report_payload(report)
        if delta is not None:
            payload["delta"] = delta
        rendered = json.dumps(payload, indent=2, sort_keys=False) + "\n"
    else:
        rendered = render_report_text(report)
        if delta is not None:
            rendered += "\n" + render_delta_text(delta)
    sys.stdout.write(rendered)
    if args.out:
        # RC-01 (MF-026 G-2): same constraint as `analyze architecture --out`;
        # this module is the same scan reached by its own entrypoint.
        try:
            out_path = resolve_evidence_out(args.out)
        except EvidencePathError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return EXIT_USAGE
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
