#!/usr/bin/env python3
"""Complexity of PRODUCED CODE. A thermometer, never a thermostat.

The shipped model descriptor (:mod:`scripts.analyze_complexity`) reads TLA+.
Every arm of every A/B this project has run produces **Python**, so when the
predecessor epic asked whether the hexagonal prompt made the produced code
simpler, D2 measured 2 for both arms from all four judges -- not because the
prompt failed to simplify, but because **nothing in the toolchain could tell.**
This module is the instrument that was missing. It reports the same *kind* of
figures the model descriptor reports (units, surface, pieces of mutable state,
branching, depth, who depends on whom, where the outside world is touched) over
the thing the agent actually wrote.

WHAT IT IS NOT, and this is the entire design constraint
--------------------------------------------------------

It **reports**. It refuses nothing, it proposes nothing, and nothing in this
toolchain gates on its output. Its figures land in the eval scorecard's
MECHANICAL BLOCK, which is recorded and never scored, precisely so that a
disagreement between measurement and judgement is visible as a finding rather
than resolved by arithmetic (``references/eval_scorecard.md``).

Three rules are wired into the code rather than left to prose, because each was
bought by a measured failure in this repository:

* **MF-020 -- a number falling is not evidence the design improved.** A metric
  can improve because an edge was *deleted*. The best complexity result on this
  project's record was withheld from a top score by both blind judges for
  exactly that. So this module emits **no verdict, no comparison, and no
  direction**: there is no ``--compare`` mode and no delta output, because a
  printed ``-12`` is the shape that invites a reader to treat a fall as a
  finding. Run it twice and read two tables.
* **CD-01 -- it proposes no cut, no refactor, no move.** A tool that picks the
  boundary makes every edge legal by construction. The model descriptor's
  suggested-move machinery was removed for being confidently wrong; none of it
  is reintroduced here.
* **No new gates** (the epic's ``no_new_gates_rule``). There is no threshold in
  this file. There is no constant a measured figure is compared against, there
  is no nonzero exit path for any input, and ``tests/test_code_complexity.py``
  asserts both of those against the shipped source and the shipped output.

**It exits 0 on every input.** A file it cannot parse costs *completeness*,
which is reported as a fact with the path and the reason, and never causes a
refusal. A path that does not exist is likewise reported, not raised. The only
nonzero exit is argparse's own usage error, which is a statement about the
command line, not about any program under measurement.

WHAT IT MEASURES
----------------

Per module (one row per ``.py`` file found under the tree) and as a tree total:

``code_lines`` / ``total_lines``
    Physical size. Non-blank, non-comment lines, and all lines.
``callables``
    ``def`` and ``async def`` at any nesting, including methods.
``public_top_level`` / ``public_methods`` / ``public_surface``
    Names not beginning with ``_``: module-level functions, classes and
    assigned names; then public methods of public classes. ``public_surface``
    is their sum. ``__init__`` and every other dunder is excluded by the
    leading-underscore rule; that is deliberate and is why it is stated here.
``declared_exports``
    ``len(__all__)`` when ``__all__`` is a module-level literal list/tuple of
    strings; ``null`` when the module declares none.
``instance_state``
    Distinct ``self.<name>`` assignment targets, summed over classes. The
    pieces of mutable state an object carries.
``module_state``
    Distinct module-level names that are *rebound*: assigned more than once at
    module level, targeted by an augmented assignment, or named in a ``global``
    statement inside a function. A module-level name assigned exactly once and
    never rebound is counted in ``public_top_level``, not here.
``branch_points``
    Decision points. Counted constructs are exactly: ``if`` statements
    (including each ``elif``, which the AST nests), conditional expressions,
    ``for``/``async for``, ``while``, each ``except`` handler, each ``if``
    clause of a comprehension, each ``match`` case, and each additional operand
    of a boolean operator (``a and b and c`` counts 2). ``assert``, ``with``
    and a bare ``try`` are NOT counted; that choice is stated rather than
    hidden, because it changes the figure for test modules most of all.
``max_branch_points_in_callable`` / ``busiest_callable``
    The single most-branching callable, and its name, so a total spread thinly
    and a total concentrated in one function are distinguishable.
``max_depth`` / ``deepest_callable``
    Deepest nesting of block statements (``if``/``for``/``while``/``with``/
    ``try``/``match``) inside any callable, and the callable it occurs in. A
    callable with no block statement has depth 0.
``declared_interfaces``
    Classes whose bases name ``Protocol`` or ``ABC``, or which carry an
    ``@abstractmethod``, with the count of their methods. The code analogue of
    a declared port. Reported as a count, not as a good thing.
``effectful_calls``
    Syntactic calls to a fixed, printed list of outside-world sinks
    (``EFFECT_SINKS``) -- filesystem, process, network, clock, randomness,
    stdio. Reported per module with the distinct sinks seen, so the report
    shows *where the outside world is touched*, which is the code analogue of
    the model descriptor's read/write matrix. Its limits are stated in the
    completeness block: a sink reached through an alias, a local variable, or
    ``getattr`` is not seen, and every ``import *`` and ``setattr`` in the tree
    is counted as an unresolved construct for that reason.
``internal_import_edges``
    Import edges whose target is another module inside the same tree, listed.
    Imports of anything outside the tree are counted separately and not listed.

Every module row also carries a ``role`` of ``test`` or ``code``, assigned by
NAME ALONE (``test_*.py``, ``*_test.py``, ``conftest.py``, or any path
component named ``test``/``tests``). Totals are reported twice, once over all
modules and once over ``code`` modules only, and the rule is printed with the
report. This project has already been burned once by an audit that was clean
because of its own filter, so the filter is output, not policy.

USAGE
-----

::

    python3 scripts/code_complexity.py <tree-or-file> [<tree-or-file> ...]
    python3 scripts/code_complexity.py <tree> --json

``--json`` emits the machine record, which is what belongs in a scorecard's
``mechanical.json``.
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

#: Report format version. Bumped when a figure is added, removed or redefined,
#: so a sealed mechanical.json can always be read against the definitions that
#: produced it.
REPORT_VERSION = 1

#: The one exit code this module ever produces for a measurement. There is no
#: other. "This tree is complex" is a figure; it is not an error, and it is not
#: a refusal.
EXIT_OK = 0

#: Directory names never walked into. Printed with every report.
SKIPPED_DIR_NAMES = frozenset(
    {"__pycache__", ".git", ".hg", ".svn", ".tox", ".venv", "venv", ".mypy_cache",
     ".pytest_cache", ".ruff_cache", "node_modules", ".eggs"}
)

#: Path components and filename shapes that make a module's ``role`` ``test``.
#: Name alone -- nothing is inferred from a module's contents.
TEST_DIR_NAMES = frozenset({"test", "tests", "testing"})

#: Outside-world sinks recognised syntactically, grouped for the report. The
#: grouping is descriptive; no group is weighted, ranked or preferred.
#:
#: The vocabulary is deliberately biased to UNDERCOUNT. Names that collide with
#: ordinary in-memory operations are listed in :data:`AMBIGUOUS_SINKS_EXCLUDED`
#: and left out, because a `dict.get` counted as a network call is a figure
#: that says something false, while a missed `requests.get` is a figure that
#: says less than the truth and says so in the completeness block. One-sided
#: the same way the negative corpus is one-sided.
EFFECT_SINKS: dict[str, tuple[str, ...]] = {
    "filesystem": (
        "open", "read_text", "write_text", "read_bytes", "write_bytes",
        "mkdir", "makedirs", "rmdir", "unlink", "rename", "touch",
        "copyfile", "copytree", "rmtree", "listdir", "glob", "rglob",
        "iterdir", "chmod", "stat", "exists", "is_file", "is_dir",
        "mkstemp", "mkdtemp", "NamedTemporaryFile", "TemporaryDirectory",
        "writelines", "flush", "fsync",
    ),
    "process": (
        "check_call", "check_output", "Popen", "system", "execv", "fork",
        "kill", "getenv", "putenv", "environ", "argv",
    ),
    "network": ("socket", "connect", "urlopen", "urlretrieve", "recv", "sendall"),
    "clock": ("sleep", "now", "utcnow", "today", "monotonic", "perf_counter"),
    "randomness": ("random", "randint", "randrange", "choice", "shuffle", "uuid4", "uuid1"),
    "stdio": ("print", "input", "stdout", "stderr", "stdin"),
}

#: Sink names deliberately NOT recognised, with the in-memory operation each
#: one collides with. Printed with every report so the undercount is visible
#: rather than inferred.
AMBIGUOUS_SINKS_EXCLUDED: dict[str, str] = {
    "get": "dict.get",
    "post": "too generic to attribute",
    "put": "queue.put",
    "delete": "too generic to attribute",
    "head": "too generic to attribute",
    "send": "generator.send",
    "request": "too generic to attribute",
    "run": "any runner method",
    "call": "any callable-invoking method",
    "remove": "list.remove / set.remove",
    "replace": "str.replace / dataclasses.replace",
    "copy": "dict.copy / list.copy",
    "move": "too generic to attribute",
    "walk": "ast.walk",
    "time": "any attribute named time",
    "sample": "random.sample / statistical sampling",
    "exit": "any exit method",
    "spawn": "too generic to attribute",
}

#: Flat name -> group, built once. A name in two groups takes the first.
_SINK_GROUP: dict[str, str] = {}
for _group, _names in EFFECT_SINKS.items():
    for _name in _names:
        _SINK_GROUP.setdefault(_name, _group)

#: Base names that make a class a declared interface.
INTERFACE_BASES = frozenset({"Protocol", "ABC", "ABCMeta"})

#: Decorator names that make a method abstract.
ABSTRACT_DECORATORS = frozenset(
    {"abstractmethod", "abstractproperty", "abstractclassmethod", "abstractstaticmethod"}
)

#: Printed with every report. It carries no banned-in-tests judgement word on
#: purpose: the disclaimer must not itself smuggle in a vocabulary of verdict.
STANDING_NOTE = (
    "Figures only. Nothing here is a judgement of them and nothing is prescribed. "
    "A figure moving in either direction is not, by itself, evidence about the "
    "design (MF-020): a count can fall because behaviour was deleted."
)


# ---------------------------------------------------------------------------
# per-module measurement
# ---------------------------------------------------------------------------


@dataclass
class ModuleFigures:
    """One row of the report. Every field is a measured fact about one file."""

    path: str
    role: str
    parsed: bool
    unparsed_reason: str | None = None
    total_lines: int = 0
    code_lines: int = 0
    callables: int = 0
    classes: int = 0
    public_top_level: int = 0
    public_methods: int = 0
    public_surface: int = 0
    declared_exports: int | None = None
    instance_state: int = 0
    module_state: int = 0
    branch_points: int = 0
    max_branch_points_in_callable: int = 0
    busiest_callable: str | None = None
    max_depth: int = 0
    deepest_callable: str | None = None
    declared_interfaces: int = 0
    declared_interface_methods: int = 0
    effectful_calls: int = 0
    effect_sinks: list[str] = field(default_factory=list)
    imports_internal: list[str] = field(default_factory=list)
    imports_external: int = 0
    unresolved_constructs: list[str] = field(default_factory=list)


#: Fields summed to produce a totals block. Anything not listed is per-module
#: only (a maximum, a name, a list) and is handled explicitly.
SUMMED_FIELDS = (
    "total_lines",
    "code_lines",
    "callables",
    "classes",
    "public_top_level",
    "public_methods",
    "public_surface",
    "instance_state",
    "module_state",
    "branch_points",
    "declared_interfaces",
    "declared_interface_methods",
    "effectful_calls",
    "imports_external",
)

#: Fields reported as the maximum over modules rather than a sum.
MAX_FIELDS = ("max_branch_points_in_callable", "max_depth")

BLOCK_STATEMENTS = (
    ast.If,
    ast.For,
    ast.AsyncFor,
    ast.While,
    ast.With,
    ast.AsyncWith,
    ast.Try,
)
if hasattr(ast, "Match"):  # 3.10+
    BLOCK_STATEMENTS = BLOCK_STATEMENTS + (ast.Match,)  # type: ignore[assignment]
if hasattr(ast, "TryStar"):  # 3.11+
    BLOCK_STATEMENTS = BLOCK_STATEMENTS + (ast.TryStar,)  # type: ignore[assignment]

FUNCTION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef)


def classify_role(path: Path, root: Path) -> str:
    """``test`` or ``code``, from the NAME only. Contents are never consulted."""

    try:
        rel = path.relative_to(root)
    except ValueError:
        rel = Path(path.name)
    parts = [part.lower() for part in rel.parts]
    if any(part in TEST_DIR_NAMES for part in parts[:-1]):
        return "test"
    name = rel.name.lower()
    if name == "conftest.py" or name.startswith("test_") or name.endswith("_test.py"):
        return "test"
    return "code"


def count_branch_points(node: ast.AST) -> int:
    """Decision points inside ``node``, per the list in the module docstring.

    Nested function and class bodies ARE included, because they execute inside
    the enclosing module; a caller that wants a single callable's own figure
    passes that callable's node.
    """

    total = 0
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While)):
            total += 1
        elif isinstance(child, ast.ExceptHandler):
            total += 1
        elif isinstance(child, ast.BoolOp):
            total += max(0, len(child.values) - 1)
        elif isinstance(child, ast.comprehension):
            total += len(child.ifs)
        elif hasattr(ast, "match_case") and isinstance(child, ast.match_case):
            total += 1
    return total


def max_block_depth(node: ast.AST) -> int:
    """Deepest nesting of block statements within ``node``'s own body."""

    def walk(body: Iterable[ast.stmt], depth: int) -> int:
        deepest = depth
        for stmt in body:
            if isinstance(stmt, BLOCK_STATEMENTS):
                inner = depth + 1
                deepest = max(deepest, inner)
                for attr in ("body", "orelse", "finalbody"):
                    deepest = max(deepest, walk(getattr(stmt, attr, []) or [], inner))
                for handler in getattr(stmt, "handlers", []) or []:
                    deepest = max(deepest, walk(handler.body, inner))
                for case in getattr(stmt, "cases", []) or []:
                    deepest = max(deepest, walk(case.body, inner))
            elif isinstance(stmt, FUNCTION_NODES + (ast.ClassDef,)):
                # A nested definition's depth belongs to that definition.
                continue
            else:
                for attr in ("body", "orelse", "finalbody"):
                    nested = getattr(stmt, attr, None)
                    if isinstance(nested, list):
                        deepest = max(deepest, walk(nested, depth))
        return deepest

    body = getattr(node, "body", [])
    return walk(body, 0)


def _self_attribute_targets(func: ast.AST, self_name: str) -> set[str]:
    names: set[str] = set()
    for child in ast.walk(func):
        targets: list[ast.expr] = []
        if isinstance(child, ast.Assign):
            targets = list(child.targets)
        elif isinstance(child, (ast.AugAssign, ast.AnnAssign)):
            targets = [child.target]
        for target in targets:
            for leaf in _flatten_target(target):
                if (
                    isinstance(leaf, ast.Attribute)
                    and isinstance(leaf.value, ast.Name)
                    and leaf.value.id == self_name
                ):
                    names.add(leaf.attr)
    return names


def _flatten_target(target: ast.expr) -> Iterable[ast.expr]:
    if isinstance(target, (ast.Tuple, ast.List)):
        for element in target.elts:
            yield from _flatten_target(element)
    else:
        yield target


def _sink_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Attribute):
        return node.attr
    if isinstance(node, ast.Name):
        return node.id
    return None


def _decorator_names(node: ast.AST) -> set[str]:
    names: set[str] = set()
    for decorator in getattr(node, "decorator_list", []) or []:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        name = _sink_name(target)
        if name:
            names.add(name)
    return names


def _is_interface(node: ast.ClassDef) -> bool:
    for base in node.bases:
        name = _sink_name(base)
        if name in INTERFACE_BASES:
            return True
    for keyword in node.keywords:
        if keyword.arg == "metaclass" and _sink_name(keyword.value) in INTERFACE_BASES:
            return True
    for stmt in node.body:
        if isinstance(stmt, FUNCTION_NODES) and (
            _decorator_names(stmt) & ABSTRACT_DECORATORS
        ):
            return True
    return False


def _qualified(stack: Sequence[str], name: str) -> str:
    return ".".join(list(stack) + [name])


def measure_module(path: Path, root: Path, source: str | None = None) -> ModuleFigures:
    """Figures for one file. Never raises for a file it cannot read or parse."""

    role = classify_role(path, root)
    try:
        rel = str(path.relative_to(root))
    except ValueError:
        rel = path.name
    figures = ModuleFigures(path=rel, role=role, parsed=False)

    if source is None:
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            figures.unparsed_reason = f"{type(exc).__name__}: {exc}"
            return figures

    lines = source.splitlines()
    figures.total_lines = len(lines)
    figures.code_lines = sum(
        1 for line in lines if line.strip() and not line.strip().startswith("#")
    )

    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, RecursionError, MemoryError) as exc:
        figures.unparsed_reason = f"{type(exc).__name__}: {exc}"
        return figures

    figures.parsed = True

    public_top: set[str] = set()
    module_assign_counts: dict[str, int] = {}
    rebound: set[str] = set()
    sinks: set[str] = set()
    unresolved: list[str] = []
    imports: list[tuple[str, int]] = []  # (dotted module, relative level)

    for stmt in tree.body:
        if isinstance(stmt, FUNCTION_NODES + (ast.ClassDef,)):
            if not stmt.name.startswith("_"):
                public_top.add(stmt.name)
        elif isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                for leaf in _flatten_target(target):
                    if isinstance(leaf, ast.Name):
                        module_assign_counts[leaf.id] = (
                            module_assign_counts.get(leaf.id, 0) + 1
                        )
                        if not leaf.id.startswith("_"):
                            public_top.add(leaf.id)
        elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            if stmt.value is not None:
                module_assign_counts[stmt.target.id] = (
                    module_assign_counts.get(stmt.target.id, 0) + 1
                )
            if not stmt.target.id.startswith("_"):
                public_top.add(stmt.target.id)
        elif isinstance(stmt, ast.AugAssign) and isinstance(stmt.target, ast.Name):
            rebound.add(stmt.target.id)
        elif isinstance(stmt, (ast.For, ast.AsyncFor)) and isinstance(
            stmt.target, ast.Name
        ):
            rebound.add(stmt.target.id)

    # __all__, when it is a literal.
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    if isinstance(stmt.value, (ast.List, ast.Tuple)):
                        figures.declared_exports = len(stmt.value.elts)

    class_stack: list[str] = []
    func_stack: list[str] = []
    busiest = ("", -1)
    deepest = ("", -1)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            figures.classes += 1
            if _is_interface(node):
                figures.declared_interfaces += 1
                figures.declared_interface_methods += sum(
                    1 for stmt in node.body if isinstance(stmt, FUNCTION_NODES)
                )
            if not node.name.startswith("_"):
                for stmt in node.body:
                    if isinstance(stmt, FUNCTION_NODES) and not stmt.name.startswith("_"):
                        figures.public_methods += 1
            # instance state: distinct self.<attr> targets in this class
            self_names: set[str] = set()
            for stmt in node.body:
                if isinstance(stmt, FUNCTION_NODES):
                    args = stmt.args.posonlyargs + stmt.args.args
                    if args:
                        self_names |= _self_attribute_targets(stmt, args[0].arg)
            figures.instance_state += len(self_names)
        elif isinstance(node, FUNCTION_NODES):
            figures.callables += 1
            own = count_branch_points(node)
            if own > busiest[1]:
                busiest = (node.name, own)
            depth = max_block_depth(node)
            if depth > deepest[1]:
                deepest = (node.name, depth)
            for child in ast.walk(node):
                if isinstance(child, ast.Global):
                    rebound.update(child.names)
        elif isinstance(node, ast.Call):
            name = _sink_name(node.func)
            if name in _SINK_GROUP:
                figures.effectful_calls += 1
                sinks.add(name)
            if name == "setattr":
                unresolved.append("setattr(): a state write this instrument cannot name")
            if name in {"globals", "locals", "eval", "exec", "getattr"}:
                unresolved.append(f"{name}(): a reference this instrument cannot resolve")
        elif isinstance(node, ast.Attribute):
            # sys.argv / sys.stdout style sinks are attribute reads, not calls
            if node.attr in _SINK_GROUP and _SINK_GROUP[node.attr] in {"stdio", "process"}:
                if isinstance(node.value, ast.Name) and node.value.id in {"sys", "os"}:
                    figures.effectful_calls += 1
                    sinks.add(node.attr)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.name, 0))
        elif isinstance(node, ast.ImportFrom):
            if node.names and node.names[0].name == "*":
                unresolved.append(
                    f"from {'.' * node.level}{node.module or ''} import *: "
                    "names this instrument cannot attribute"
                )
            imports.append((node.module or "", node.level))

    figures.branch_points = count_branch_points(tree)
    figures.max_branch_points_in_callable = max(0, busiest[1])
    figures.busiest_callable = busiest[0] or None
    figures.max_depth = max(0, deepest[1])
    figures.deepest_callable = deepest[0] or None

    for name, count in module_assign_counts.items():
        if count > 1:
            rebound.add(name)
    figures.module_state = len(rebound)

    figures.public_top_level = len(public_top)
    figures.public_surface = figures.public_top_level + figures.public_methods
    figures.effect_sinks = sorted(sinks)
    figures.unresolved_constructs = sorted(set(unresolved))
    figures._raw_imports = imports  # type: ignore[attr-defined]
    return figures


# ---------------------------------------------------------------------------
# tree assembly
# ---------------------------------------------------------------------------


def discover_python_files(target: Path) -> list[Path]:
    """Every ``.py`` under ``target``, or ``target`` itself when it is a file."""

    if target.is_file():
        return [target] if target.suffix == ".py" else []
    found: list[Path] = []
    for path in sorted(target.rglob("*.py")):
        if any(part in SKIPPED_DIR_NAMES for part in path.parts):
            continue
        found.append(path)
    return found


def _import_index(paths: Sequence[str]) -> dict[str, str]:
    """Map dotted suffixes of in-tree module names back to their file path."""

    index: dict[str, str] = {}
    for rel in paths:
        parts = Path(rel).with_suffix("").parts
        if parts and parts[-1] == "__init__":
            parts = parts[:-1]
        if not parts:
            continue
        for start in range(len(parts)):
            key = ".".join(parts[start:])
            index.setdefault(key, rel)
    return index


def _resolve_imports(modules: list[ModuleFigures]) -> None:
    index = _import_index([m.path for m in modules])
    by_path = {m.path: m for m in modules}
    for module in modules:
        raw = getattr(module, "_raw_imports", [])
        internal: set[str] = set()
        external = 0
        own_parts = Path(module.path).with_suffix("").parts
        for dotted, level in raw:
            target: str | None = None
            if level:
                base = list(own_parts[:-1])
                for _ in range(level - 1):
                    if base:
                        base.pop()
                key = ".".join(base + (dotted.split(".") if dotted else []))
                target = index.get(key) or index.get(dotted)
            else:
                target = index.get(dotted)
                if target is None and dotted:
                    target = index.get(dotted.split(".")[-1])
            if target is not None and target != module.path and target in by_path:
                internal.add(target)
            else:
                external += 1
        module.imports_internal = sorted(internal)
        module.imports_external = external
        if hasattr(module, "_raw_imports"):
            delattr(module, "_raw_imports")


def _totals(modules: Sequence[ModuleFigures]) -> dict[str, Any]:
    parsed = [m for m in modules if m.parsed]
    totals: dict[str, Any] = {"modules": len(modules)}
    for name in SUMMED_FIELDS:
        totals[name] = sum(getattr(m, name) for m in parsed)
    for name in MAX_FIELDS:
        totals[name] = max((getattr(m, name) for m in parsed), default=0)
    edges = sorted(
        {(m.path, target) for m in parsed for target in m.imports_internal}
    )
    totals["internal_import_edges"] = len(edges)
    totals["modules_with_effectful_calls"] = sum(
        1 for m in parsed if m.effectful_calls
    )
    # A partition of two figures already reported, by a predicate already
    # reported. Without it the tree totals are blind to WHERE the outside world
    # sits relative to the decisions -- the code analogue of the model
    # descriptor's dense rows. It is a location, not a score.
    totals["branch_points_in_effectful_modules"] = sum(
        m.branch_points for m in parsed if m.effectful_calls
    )
    totals["instance_state_in_effectful_modules"] = sum(
        m.instance_state for m in parsed if m.effectful_calls
    )
    totals["effect_sinks"] = sorted({s for m in parsed for s in m.effect_sinks})
    totals["effect_sink_groups"] = sorted(
        {_SINK_GROUP[s] for m in parsed for s in m.effect_sinks if s in _SINK_GROUP}
    )
    return totals


def analyze_tree(target: str | Path) -> dict[str, Any]:
    """The full record for one tree. Never raises for a bad or missing path."""

    target = Path(target)
    record: dict[str, Any] = {
        "report_version": REPORT_VERSION,
        "target": str(target),
        "note": STANDING_NOTE,
        "definitions": {
            "role_rule": (
                "role is assigned by NAME alone: a path component in "
                f"{sorted(TEST_DIR_NAMES)}, or a filename matching test_*.py, "
                "*_test.py or conftest.py, is role=test. Contents are never read."
            ),
            "branch_points": (
                "if / elif / conditional-expression / for / async-for / while / "
                "each except handler / each comprehension if / each match case / "
                "each extra operand of a boolean operator. assert, with and a "
                "bare try are NOT counted."
            ),
            "max_depth": (
                "deepest nesting of if/for/while/with/try/match inside a single "
                "callable; a callable with no block statement has depth 0"
            ),
            "instance_state": "distinct self.<name> assignment targets per class, summed",
            "module_state": (
                "distinct module-level names rebound: assigned more than once, "
                "augmented-assigned, or declared global inside a function"
            ),
            "public_surface": (
                "module-level names not starting with _ , plus public methods of "
                "public classes. Dunders, including __init__, are excluded."
            ),
            "declared_interfaces": (
                "classes based on Protocol/ABC or carrying an @abstractmethod"
            ),
            "effectful_calls": (
                "syntactic calls to the printed EFFECT_SINKS list. A sink reached "
                "through an alias, a local variable or getattr is NOT seen, and "
                "the names in effect_sinks_excluded are not seen either. This "
                "figure UNDERCOUNTS by construction."
            ),
            "skipped_directories": sorted(SKIPPED_DIR_NAMES),
        },
        "effect_sink_vocabulary": {k: list(v) for k, v in EFFECT_SINKS.items()},
        "effect_sinks_excluded": dict(AMBIGUOUS_SINKS_EXCLUDED),
    }

    if not target.exists():
        record["modules"] = []
        record["totals"] = _totals([])
        record["totals_code_only"] = _totals([])
        record["completeness"] = {
            "files_seen": 0,
            "files_parsed": 0,
            "files_unparsed": 0,
            "parsed_fraction": None,
            "unparsed": [],
            "unresolved_constructs": [],
            "path_state": "not found -- reported, not refused",
        }
        return record

    root = target if target.is_dir() else target.parent
    files = discover_python_files(target)
    modules = [measure_module(path, root) for path in files]
    _resolve_imports(modules)

    parsed = [m for m in modules if m.parsed]
    unparsed = [m for m in modules if not m.parsed]
    code_only = [m for m in modules if m.role == "code"]

    record["modules"] = [asdict(m) for m in modules]
    record["totals"] = _totals(modules)
    record["totals_code_only"] = _totals(code_only)
    record["internal_import_edges"] = sorted(
        [m.path, target_path]
        for m in parsed
        for target_path in m.imports_internal
    )
    record["completeness"] = {
        "files_seen": len(modules),
        "files_parsed": len(parsed),
        "files_unparsed": len(unparsed),
        "parsed_fraction": (len(parsed) / len(modules)) if modules else None,
        "unparsed": [
            {"path": m.path, "reason": m.unparsed_reason} for m in unparsed
        ],
        "unresolved_constructs": sorted(
            {f"{m.path}: {item}" for m in parsed for item in m.unresolved_constructs}
        ),
        "path_state": "present",
    }
    return record


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------

#: Column key -> heading, in print order.
TABLE_COLUMNS: tuple[tuple[str, str], ...] = (
    ("role", "role"),
    ("code_lines", "code"),
    ("callables", "defs"),
    ("public_surface", "public"),
    ("instance_state", "inst"),
    ("module_state", "mod"),
    ("branch_points", "branch"),
    ("max_branch_points_in_callable", "worst"),
    ("max_depth", "depth"),
    ("declared_interfaces", "iface"),
    ("effectful_calls", "effect"),
)


def render(record: dict[str, Any]) -> str:
    out: list[str] = []
    out.append(f"code complexity report v{record['report_version']}")
    out.append(f"target: {record['target']}")
    out.append("")
    out.append(record["note"])
    out.append("")

    completeness = record["completeness"]
    if completeness["path_state"] != "present":
        out.append(f"path: {completeness['path_state']}")
        out.append("figures: none measured")
        out.append("")
        _render_completeness(out, completeness)
        return "\n".join(out) + "\n"

    modules = record["modules"]
    if not modules:
        out.append("no .py files found under this target")
        out.append("")
        _render_completeness(out, completeness)
        return "\n".join(out) + "\n"

    name_width = max([len(m["path"]) for m in modules] + [len("module")])
    headings = ["module".ljust(name_width)] + [
        heading.rjust(6) for _, heading in TABLE_COLUMNS
    ]
    out.append("  ".join(headings))
    out.append("-" * len("  ".join(headings)))
    for module in modules:
        if not module["parsed"]:
            out.append(
                f"{module['path'].ljust(name_width)}  "
                f"{module['role'].rjust(6)}  [not parsed: {module['unparsed_reason']}]"
            )
            continue
        row = [module["path"].ljust(name_width)]
        for key, _ in TABLE_COLUMNS:
            row.append(str(module[key]).rjust(6))
        out.append("  ".join(row))
    out.append("")

    for label, key in (("TOTAL (all modules)", "totals"), ("TOTAL (role=code)", "totals_code_only")):
        totals = record[key]
        out.append(f"{label}: modules={totals['modules']}")
        out.append(
            "  code_lines={code_lines}  callables={callables}  classes={classes}"
            "  public_surface={public_surface}".format(**totals)
        )
        out.append(
            "  instance_state={instance_state}  module_state={module_state}"
            "  branch_points={branch_points}".format(**totals)
        )
        out.append(
            "  max_branch_points_in_callable={max_branch_points_in_callable}"
            "  max_depth={max_depth}".format(**totals)
        )
        out.append(
            "  declared_interfaces={declared_interfaces}"
            "  declared_interface_methods={declared_interface_methods}".format(**totals)
        )
        out.append(
            "  internal_import_edges={internal_import_edges}"
            "  effectful_calls={effectful_calls}"
            "  modules_with_effectful_calls={modules_with_effectful_calls}".format(**totals)
        )
        out.append(
            "  branch_points_in_effectful_modules="
            "{branch_points_in_effectful_modules}"
            "  instance_state_in_effectful_modules="
            "{instance_state_in_effectful_modules}".format(**totals)
        )
        if totals["effect_sinks"]:
            out.append(
                "  effect_sinks: "
                + ", ".join(totals["effect_sinks"])
                + f"  (groups: {', '.join(totals['effect_sink_groups'])})"
            )
        out.append("")

    edges = record.get("internal_import_edges") or []
    out.append(f"internal import edges ({len(edges)}):")
    if edges:
        for source, dest in edges:
            out.append(f"  {source} -> {dest}")
    else:
        out.append("  (none: no module in this tree imports another)")
    out.append("")

    _render_completeness(out, completeness)
    out.append(
        "  effectful_calls undercounts by construction: "
        + str(len(AMBIGUOUS_SINKS_EXCLUDED))
        + " sink names are left out of the vocabulary for colliding with "
        "in-memory operations ("
        + ", ".join(f"{k} ~ {v}" for k, v in sorted(AMBIGUOUS_SINKS_EXCLUDED.items()))
        + ")"
    )
    out.append("")
    out.append("column key: " + "; ".join(f"{h}={k}" for k, h in TABLE_COLUMNS))
    out.append("role rule: " + record["definitions"]["role_rule"])
    return "\n".join(out) + "\n"


def _render_completeness(out: list[str], completeness: dict[str, Any]) -> None:
    fraction = completeness["parsed_fraction"]
    rendered = "n/a" if fraction is None else f"{fraction:.3f}"
    out.append(
        "completeness: {files_parsed}/{files_seen} files parsed "
        "(fraction {fraction})".format(fraction=rendered, **completeness)
    )
    for item in completeness["unparsed"]:
        out.append(f"  not parsed: {item['path']} -- {item['reason']}")
    for item in completeness["unresolved_constructs"]:
        out.append(f"  not resolved: {item}")
    if not completeness["unparsed"] and not completeness["unresolved_constructs"]:
        out.append("  nothing was left unmeasured by this instrument's own limits")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="code_complexity",
        description=(
            "Report complexity figures for produced Python. A thermometer: it "
            "measures and prints, it refuses nothing, and no part of this "
            "toolchain reads its output as a condition."
        ),
        epilog=(
            "Always exits 0 for any target, including one that does not exist "
            "or cannot be parsed. There is no comparison mode: MF-020 -- a "
            "figure falling is not evidence the design improved -- and a "
            "printed delta invites exactly that reading."
        ),
    )
    parser.add_argument("targets", nargs="+", help="tree(s) or .py file(s) to measure")
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="emit the machine record (what belongs in a scorecard mechanical.json)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    records = [analyze_tree(target) for target in args.targets]
    if args.as_json:
        payload = records[0] if len(records) == 1 else {"reports": records}
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for index, record in enumerate(records):
            if index:
                print()
            print(render(record), end="")
    return EXIT_OK


if __name__ == "__main__":  # pragma: no cover - exercised via subprocess in tests
    sys.exit(main())
