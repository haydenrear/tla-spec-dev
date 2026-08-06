#!/usr/bin/env python3
"""Declared case modules: the `case_modules:` manifest block and its coverage report.

A case module EXTENDS a view, declares no state, no constants and no actions,
and either restricts the next-state relation to one aspect's entry points (a
**slice**) or replaces ``Init`` with an asserted **Given**. The doctrine is
``references/case_modules.md``; this module mechanizes exactly two things from
it:

* the **declaration** -- which modules exist, which view each extends, which
  actions each enters, and (for a Given) the claim the Given asserts, because
  an unexplained Given is unreviewable;
* the **aggregation report** -- per-action coverage across every declared
  module against the view's action set, naming the actions no module enters and
  the view's own corpus does not cover.

Two rules bind this file, both from
``references/architecture_tractability.md``:

* **Advisory, not blocking.** The report never gates anything and always exits
  0 when it could be produced. A nonzero exit means "I could not measure this"
  -- an unreadable manifest, a malformed block -- never "your coverage is bad".
* **Evidence integrity.** Counts come from generated corpora, never from
  estimates, and nothing is dropped, sampled, or rounded away. A module that
  was declared but not generated is reported as UNMEASURED, which is a
  different fact from zero.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

try:  # package import
    from .extract_spec_manifest import load_manifest
except ImportError:  # pragma: no cover - direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from extract_spec_manifest import load_manifest  # type: ignore[no-redef]


CASE_MODULES_KEY = "case_modules"
COVERAGE_FILENAME = "case_coverage.json"
FORMS = ("slice", "given")

#: The system property SANY reads as its module search path. TLC has no
#: command-line equivalent (there is no ``-lib``), so it is set on the JVM.
TLA_LIBRARY_PROPERTY = "TLA-Library"


class CaseModuleError(Exception):
    """The declaration could not be read. Never raised for weak coverage."""


@dataclass(frozen=True)
class CaseModuleDeclaration:
    """One entry of the manifest's ``case_modules:`` block."""

    name: str
    extends: str
    actions: tuple[str, ...]
    form: str
    claim: str | None
    view: str | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "extends": self.extends,
            "actions": list(self.actions),
            "form": self.form,
            "claim": self.claim,
            "view": self.view,
        }


# --------------------------------------------------------------------------
# Module search path (EV-02-DF-02)
# --------------------------------------------------------------------------


class ModuleSearchError(CaseModuleError):
    """An ``EXTENDS`` could not be resolved to a file, or resolved ambiguously.

    Raised BEFORE TLC is started, because TLC's own failure for this is a
    ``tla2sany.semantic.AbortException`` stack thirty lines below the sentence
    that names the missing module, and it is preceded by the complexity
    scanner's fail-closed paragraph. Both are true and neither says "the view
    you EXTENDS is in another directory".
    """


@dataclass(frozen=True)
class ModuleSearchPath:
    """Where the modules of one ``EXTENDS`` hierarchy were found.

    ``directories`` is the search path in precedence order, starting with the
    module's own directory. It is what SANY is given as ``TLA-Library`` and what
    the static analyzer is given as its lookup path, so the two can never
    resolve the same ``EXTENDS`` to different files.
    """

    root: Path
    directories: tuple[Path, ...]
    resolved: tuple[tuple[str, Path], ...]
    searched: tuple[tuple[Path, str], ...]

    @property
    def is_self_contained(self) -> bool:
        """True when every EXTENDS resolved inside the module's own directory."""
        return len(self.directories) == 1

    @property
    def elsewhere(self) -> tuple[tuple[str, Path], ...]:
        """The modules that resolved OUTSIDE the module's own directory."""
        root = self.root.parent
        return tuple((name, path) for name, path in self.resolved if path.parent != root)

    @property
    def files_base_first(self) -> tuple[Path, ...]:
        """Every file of the hierarchy, base modules first, root module last.

        ``resolved`` is in discovery order (the root's own EXTENDS, then
        theirs), so reversing it puts the deepest base module first. That is the
        order a reader of the concatenated text needs: an extending module's
        definitions must come after the ones they extend.
        """
        return tuple(path for _, path in reversed(self.resolved)) + (self.root,)

    def tla_library(self) -> str:
        """The value for the ``TLA-Library`` system property."""
        return os.pathsep.join(str(directory) for directory in self.directories)

    def describe(self) -> str:
        parts = [
            f"{name} -> {path}" for name, path in self.elsewhere
        ]
        return "; ".join(parts)


def _analyzer() -> Any:
    """The static TLA+ reader, imported lazily to keep this module cycle-free."""
    try:  # package import
        from . import analyze_complexity  # type: ignore[attr-defined]
    except ImportError:  # pragma: no cover - direct script execution
        import analyze_complexity  # type: ignore[no-redef]
    return analyze_complexity


def candidate_module_directories(
    tla_path: Path, extra_roots: Sequence[Path] = ()
) -> list[tuple[Path, str]]:
    """Directories searched for the modules ``tla_path`` EXTENDS, in order.

    Three kinds, and the precedence between them is the whole rule:

    1. ``module`` -- the module's own directory. A view sitting beside the case
       module always wins, which is what TLC itself does.
    2. ``explicit`` -- every ``--module-path`` the operator passed, in order.
    3. ``sibling`` -- directories beside the module's own that contain at least
       one ``.tla``. This is what makes the documented layout
       (``specs/case_modules/`` extending ``specs/program_model/``) work without
       a flag. It is one level, never recursive, and a module found in two
       siblings is an ERROR rather than a coin flip.
    """
    root = Path(tla_path).resolve().parent
    directories: list[tuple[Path, str]] = [(root, "module")]
    seen = {root}
    for extra in extra_roots:
        resolved = Path(extra).resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        directories.append((resolved, "explicit"))
    parent = root.parent
    if parent != root and parent.is_dir():
        for sibling in sorted(parent.iterdir()):
            resolved = sibling.resolve()
            if resolved in seen or not sibling.is_dir():
                continue
            if not any(sibling.glob("*.tla")):
                continue
            seen.add(resolved)
            directories.append((resolved, "sibling"))
    return directories


def resolve_search_path(
    tla_path: Path, extra_roots: Sequence[Path] = ()
) -> ModuleSearchPath:
    """Resolve every non-standard ``EXTENDS`` of ``tla_path``, transitively.

    Raises :class:`ModuleSearchError` naming the module, the directories that
    were searched, and the flag that fixes it. Nothing here inspects the
    contents of a module beyond its ``EXTENDS`` clause: this answers "which
    files does TLC need to read", not "what do they declare".
    """
    analyzer = _analyzer()
    tla_path = Path(tla_path).resolve()
    candidates = candidate_module_directories(tla_path, extra_roots)
    root_dir = tla_path.parent

    resolved: dict[str, Path] = {}
    used: list[Path] = [root_dir]
    queue: list[Path] = [tla_path]
    visited: set[Path] = {tla_path}

    while queue:
        current = queue.pop(0)
        try:
            text = analyzer.strip_comments(current.read_text(encoding="utf-8"))
        except OSError as error:
            raise ModuleSearchError(f"could not read {current}: {error}") from error
        for name in analyzer.parse_extends(text):
            if name in analyzer.STANDARD_MODULES or name in resolved:
                continue
            hits = [
                (directory / f"{name}.tla", kind)
                for directory, kind in candidates
                if (directory / f"{name}.tla").is_file()
            ]
            if not hits:
                searched = "\n".join(
                    f"    {directory}  ({kind})" for directory, kind in candidates
                )
                raise ModuleSearchError(
                    f"module {current.stem} EXTENDS {name}, but {name}.tla is in none of "
                    f"the directories on the module search path:\n{searched}\n"
                    f"  TLC resolves EXTENDS against the directory of the .tla it is given "
                    f"and the TLA-Library search path -- never against the current "
                    f"directory. Put {name}.tla on the path with "
                    f"--module-path <dir containing {name}.tla>, or move the module beside "
                    f"it. (If {name} is a standard library module this toolchain does not "
                    "know, add it to analyze_complexity.STANDARD_MODULES once verified.)"
                )
            ambiguous = [path for path, kind in hits if kind == "sibling"]
            if hits[0][1] == "sibling" and len(ambiguous) > 1:
                raise ModuleSearchError(
                    f"module {current.stem} EXTENDS {name}, and {name}.tla exists in more "
                    "than one directory beside "
                    f"{root_dir}:\n"
                    + "\n".join(f"    {path}" for path in ambiguous)
                    + "\n  Refusing to guess which one the model means. Name it with "
                    "--module-path <dir>, which takes precedence over the siblings."
                )
            chosen = hits[0][0]
            resolved[name] = chosen
            if chosen.parent not in used:
                used.append(chosen.parent)
            if chosen not in visited:
                visited.add(chosen)
                queue.append(chosen)

    return ModuleSearchPath(
        root=tla_path,
        directories=tuple(used),
        resolved=tuple(resolved.items()),
        searched=tuple(candidates),
    )


MANIFEST_FILENAME = "spec_manifest.yaml"


def resolve_manifest_path(
    spec_dir: Path, search_path: ModuleSearchPath | None = None
) -> Path:
    """The manifest that governs a generation, following the module search path.

    A case module in ``specs/case_modules/`` has no manifest beside it -- the
    manifest belongs to the VIEW it extends, in ``specs/program_model/``. Before
    EV-02-DF-02 the module had to be copied beside the view to generate at all,
    so the two directories were the same one and this never came up. Looking
    along the same path TLC reads keeps the declaration, the budgets and the
    corpus talking about one project.

    Returns the path beside ``spec_dir`` when nothing is found, so the caller
    still reports a missing manifest against the directory it expected.
    """
    local = Path(spec_dir) / MANIFEST_FILENAME
    if local.is_file() or search_path is None:
        return local
    for directory in search_path.directories:
        candidate = Path(directory) / MANIFEST_FILENAME
        if candidate.is_file():
            return candidate
    return local


def tlc_environment(
    search_path: ModuleSearchPath | None, env: dict[str, str] | None = None
) -> dict[str, str]:
    """A process environment that gives SANY ``search_path`` as its module path.

    TLC exposes no ``-lib`` flag; SANY reads the ``TLA-Library`` **system
    property**, so the only way through a ``tlc2`` launcher script is the JVM's
    own ``JAVA_TOOL_OPTIONS``. The JVM prints one "Picked up JAVA_TOOL_OPTIONS"
    line to stderr when it does this; that line is the receipt for the search
    path and is expected. Nothing is set when every module resolved locally, so
    the common case is byte-identical to before.
    """
    base = dict(os.environ if env is None else env)
    if search_path is None or search_path.is_self_contained:
        return base
    option = f"-D{TLA_LIBRARY_PROPERTY}={search_path.tla_library()}"
    existing = base.get("JAVA_TOOL_OPTIONS", "").strip()
    base["JAVA_TOOL_OPTIONS"] = f"{existing} {option}".strip()
    return base


def _as_str_list(value: Any) -> list[str] | None:
    if isinstance(value, str):
        return None
    if not isinstance(value, (list, tuple)):
        return None
    if any(not isinstance(item, str) for item in value):
        return None
    return [item.strip() for item in value]


def validate_case_modules(manifest: dict[str, Any]) -> list[str]:
    """Schema problems in the ``case_modules:`` block, or [] when it is sound.

    Reports every problem it finds rather than the first, so a manifest is
    fixed in one pass.
    """
    block = manifest.get(CASE_MODULES_KEY)
    if block is None:
        return []
    if not isinstance(block, dict):
        return [
            f"{CASE_MODULES_KEY}: must be a mapping of module name -> declaration, "
            f"got {type(block).__name__}"
        ]

    errors: list[str] = []
    for name, raw in block.items():
        where = f"{CASE_MODULES_KEY}.{name}"
        if not isinstance(raw, dict):
            errors.append(f"{where}: must be a mapping with at least `extends:` and `actions:`")
            continue

        extends = raw.get("extends")
        if not isinstance(extends, str) or not extends.strip():
            errors.append(
                f"{where}: `extends:` is required and names the view module this case "
                "module EXTENDS (a case module that extends nothing is a program spec)"
            )

        actions = _as_str_list(raw.get("actions"))
        if actions is None or not actions:
            errors.append(
                f"{where}: `actions:` is required and lists the view actions this "
                "aspect enters. An empty scope is not a case module."
            )
        elif len(set(actions)) != len(actions):
            duplicates = sorted({a for a in actions if actions.count(a) > 1})
            errors.append(f"{where}: `actions:` repeats {', '.join(duplicates)}")

        form = raw.get("form", "slice")
        if not isinstance(form, str) or form.strip() not in FORMS:
            errors.append(f"{where}: `form:` must be one of {', '.join(FORMS)} (default slice)")
            form = ""

        claim = raw.get("claim")
        if form.strip() == "given":
            if not isinstance(claim, str) or not claim.strip():
                errors.append(
                    f"{where}: a `form: given` module must record `claim:` -- the modeling "
                    "claim the Given asserts, in prose. A Given asserts a pre-state instead "
                    "of enumerating a path to it; unexplained, it is unreviewable "
                    "(references/case_modules.md, Integrity)."
                )
        elif claim is not None and not isinstance(claim, str):
            errors.append(f"{where}: `claim:` must be free text")

        view = raw.get("view")
        if view is not None and (not isinstance(view, str) or not view.strip()):
            errors.append(f"{where}: `view:` must name a generation view when present")

    return errors


def load_declarations(manifest: dict[str, Any]) -> dict[str, CaseModuleDeclaration]:
    """Parse the ``case_modules:`` block. Raises CaseModuleError when malformed."""
    errors = validate_case_modules(manifest)
    if errors:
        raise CaseModuleError("\n".join(f"- {error}" for error in errors))

    block = manifest.get(CASE_MODULES_KEY) or {}
    declarations: dict[str, CaseModuleDeclaration] = {}
    for name, raw in dict(block).items():
        form = str(raw.get("form", "slice")).strip()
        claim = raw.get("claim")
        declarations[str(name)] = CaseModuleDeclaration(
            name=str(name),
            extends=str(raw["extends"]).strip(),
            actions=tuple(_as_str_list(raw.get("actions")) or ()),
            form=form,
            claim=claim.strip() if isinstance(claim, str) and claim.strip() else None,
            view=str(raw["view"]).strip() if isinstance(raw.get("view"), str) else None,
        )
    return declarations


def declarations_from_manifest(manifest_path: Path) -> dict[str, CaseModuleDeclaration]:
    if not Path(manifest_path).is_file():
        return {}
    return load_declarations(load_manifest(Path(manifest_path)))


def declaration_for(
    manifest_path: Path, module: str, *, warn_stream: Any = None
) -> CaseModuleDeclaration | None:
    """The declaration for ``module``, or None.

    A malformed block WARNS and returns None. Case generation is never refused
    because a manifest is wrong -- the caller keeps its previous behavior and
    the operator sees why.
    """
    try:
        return declarations_from_manifest(Path(manifest_path)).get(module)
    except (CaseModuleError, ValueError) as error:
        if warn_stream is not None:
            print(
                f"warning: {Path(manifest_path)} has an unusable `{CASE_MODULES_KEY}:` block, "
                f"so no per-module action scope is applied:\n{error}",
                file=warn_stream,
            )
        return None


# --------------------------------------------------------------------------
# Per-corpus coverage records
# --------------------------------------------------------------------------


def coverage_record(
    *,
    module: str,
    view: str,
    action_counts: dict[str, int],
    declared_view_actions: Iterable[str],
    declaration: CaseModuleDeclaration | None,
    source: str,
) -> dict[str, Any]:
    """The per-corpus record generation writes beside a generated case package."""
    counts = {name: int(count) for name, count in sorted(action_counts.items())}
    declared = sorted(declared_view_actions)
    scope = list(declaration.actions) if declaration is not None else None
    record: dict[str, Any] = {
        "module": module,
        "view": view,
        "source": source,
        "cases": sum(counts.values()),
        "actions": counts,
        "declared_view_actions": declared,
        "case_module": declaration.as_dict() if declaration is not None else None,
    }
    if scope is not None:
        record["zero_case_actions_in_scope"] = sorted(
            name for name in scope if counts.get(name, 0) == 0 and name in declared
        )
        record["scope_actions_not_declared_for_view"] = sorted(
            name for name in scope if name not in declared
        )
        record["generated_outside_declared_scope"] = sorted(
            name for name in counts if name not in scope
        )
    return record


def write_coverage_record(package_dir: Path, record: dict[str, Any]) -> Path:
    path = Path(package_dir) / COVERAGE_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def read_coverage_record(path: Path) -> dict[str, Any]:
    path = Path(path)
    if path.is_dir():
        path = path / COVERAGE_FILENAME
    if not path.is_file():
        raise CaseModuleError(
            f"no {COVERAGE_FILENAME} at {path}. It is written next to every generated "
            "case package; regenerate the corpus, or point --corpus at the package "
            "directory that holds one."
        )
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise CaseModuleError(f"{path} is not readable JSON: {error}") from error
    if not isinstance(record, dict) or "module" not in record:
        raise CaseModuleError(f"{path} is not a case-coverage record")
    record["path"] = str(path)
    return record


# --------------------------------------------------------------------------
# Aggregation report
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class CoverageReport:
    view: str
    manifest_path: Path
    declarations: dict[str, CaseModuleDeclaration]
    module_records: dict[str, dict[str, Any]]
    view_records: dict[str, dict[str, Any]]
    view_actions: tuple[str, ...]
    view_action_source: str

    @property
    def measured_modules(self) -> list[str]:
        return sorted(self.module_records)

    @property
    def unmeasured_modules(self) -> list[str]:
        return sorted(set(self.declarations) - set(self.module_records))

    def module_counts(self, action: str) -> dict[str, int]:
        return {
            name: int(record.get("actions", {}).get(action, 0))
            for name, record in sorted(self.module_records.items())
        }

    def view_count(self, action: str) -> int | None:
        if not self.view_records:
            return None
        return sum(
            int(record.get("actions", {}).get(action, 0))
            for record in self.view_records.values()
        )

    def entered_by(self, action: str) -> list[str]:
        return [name for name, count in self.module_counts(action).items() if count > 0]

    def declared_by(self, action: str) -> list[str]:
        return sorted(
            name
            for name, declaration in self.declarations.items()
            if action in declaration.actions
        )

    @property
    def uncovered_actions(self) -> list[str]:
        """View actions no module ENTERS and the view's own corpus does not cover.

        A declared-but-unmeasured module cannot cover anything: a declaration is
        an intention, and this report counts cases.
        """
        uncovered = []
        for action in self.view_actions:
            if self.entered_by(action):
                continue
            in_view = self.view_count(action)
            if in_view is not None and in_view > 0:
                continue
            uncovered.append(action)
        return uncovered


def _view_actions_from_records(records: Iterable[dict[str, Any]]) -> tuple[list[str], str]:
    declared: set[str] = set()
    for record in records:
        declared.update(record.get("declared_view_actions") or [])
    return sorted(declared), "the declared view actions recorded with the supplied corpora"


def build_report(
    *,
    manifest_path: Path,
    corpora: list[dict[str, Any]],
    view: str | None = None,
    view_actions: Iterable[str] | None = None,
) -> CoverageReport:
    declarations = declarations_from_manifest(Path(manifest_path))
    resolved_view = view or (corpora[0].get("view") if corpora else None) or "external"

    scoped = [record for record in corpora if record.get("view") == resolved_view]
    module_records: dict[str, dict[str, Any]] = {}
    view_records: dict[str, dict[str, Any]] = {}
    for record in scoped:
        name = str(record.get("module"))
        if name in declarations:
            module_records[name] = record
        else:
            view_records[name] = record

    if view_actions is not None:
        actions, source = sorted(set(view_actions)), "the supplied actions metadata"
    else:
        actions, source = _view_actions_from_records(scoped)

    return CoverageReport(
        view=resolved_view,
        manifest_path=Path(manifest_path),
        declarations=declarations,
        module_records=module_records,
        view_records=view_records,
        view_actions=tuple(actions),
        view_action_source=source,
    )


def _table(rows: list[list[str]], headers: list[str]) -> str:
    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))
    lines = ["  ".join(header.ljust(widths[i]) for i, header in enumerate(headers)).rstrip()]
    lines.append("  ".join("-" * widths[i] for i in range(len(headers))))
    for row in rows:
        lines.append("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)).rstrip())
    return "\n".join(lines)


def render_report(report: CoverageReport) -> str:
    modules = report.measured_modules
    headers = ["action", "view corpus", *modules, "modules total"]
    rows: list[list[str]] = []
    for action in report.view_actions:
        counts = report.module_counts(action)
        in_view = report.view_count(action)
        rows.append(
            [
                action,
                "UNMEASURED" if in_view is None else str(in_view),
                *[str(counts[name]) for name in modules],
                str(sum(counts.values())),
            ]
        )

    forms = [report.declarations[name].form for name in sorted(report.declarations)]
    summary = ", ".join(
        f"{forms.count(form)} {form}" for form in FORMS if forms.count(form)
    ) or "none"

    lines = [
        f"case-module coverage -- view: {report.view}",
        f"  manifest: {report.manifest_path}",
        f"  declared case modules: {len(report.declarations)} ({summary})",
        f"  view action set: {len(report.view_actions)} actions, from {report.view_action_source}",
        "",
        "This is a REPORT. It states per-action coverage and gates nothing "
        "(references/architecture_tractability.md, 'Advisory, Not Blocking').",
        "",
    ]
    if rows:
        lines.append(_table(rows, headers))
    else:
        lines.append("(no view actions resolved -- supply --actions-metadata or a corpus)")
    lines.append("")

    if not report.view_records:
        lines.append(
            "The view's own corpus was NOT supplied, so its column reads UNMEASURED. "
            "Unmeasured is not zero: pass --corpus <view package> to include it."
        )
    else:
        lines.append(
            "view corpus: "
            + ", ".join(
                f"{name} ({record.get('cases', 0)} cases)"
                for name, record in sorted(report.view_records.items())
            )
        )

    if report.unmeasured_modules:
        lines.append("")
        lines.append(
            "declared but NOT measured (no corpus supplied; a declaration is an "
            "intention, not coverage): " + ", ".join(report.unmeasured_modules)
        )

    stale: list[str] = []
    for name, record in sorted(report.module_records.items()):
        outside = record.get("generated_outside_declared_scope") or []
        if outside:
            stale.append(f"{name} generated cases for {', '.join(outside)} outside its `actions:` scope")
        unknown = record.get("scope_actions_not_declared_for_view") or []
        if unknown:
            stale.append(
                f"{name} declares {', '.join(unknown)} in scope, which the view's "
                "actions metadata does not declare"
            )
    if stale:
        lines.append("")
        lines.append("declaration drift (the declared scope no longer matches the corpus):")
        lines.extend(f"  - {item}" for item in stale)

    lines.append("")
    uncovered = report.uncovered_actions
    if uncovered:
        lines.append(
            f"UNCOVERED: {len(uncovered)} view action(s) entered by no measured module and "
            "not covered by the view's own corpus:"
        )
        for action in uncovered:
            declared_by = report.declared_by(action)
            note = (
                f"declared in the scope of {', '.join(declared_by)}, which was not measured"
                if declared_by
                else "declared in no module's scope"
            )
            lines.append(f"  - {action} ({note})")
    else:
        lines.append(
            "UNCOVERED: none -- every view action is entered by a measured module or "
            "covered by the view's own corpus."
        )

    lines.append("")
    lines.append(
        "Cross-aspect interleaving is not in this table. Slices do not enumerate the "
        "interleavings between aspects; only a whole-view run does. Do not report the "
        "union of modules as equivalent to the view's corpus "
        "(references/case_modules.md, Integrity rule 4)."
    )
    return "\n".join(lines)


def report_payload(report: CoverageReport) -> dict[str, Any]:
    return {
        "view": report.view,
        "manifest": str(report.manifest_path),
        "view_actions": list(report.view_actions),
        "view_action_source": report.view_action_source,
        "declarations": {
            name: declaration.as_dict()
            for name, declaration in sorted(report.declarations.items())
        },
        "measured_modules": report.measured_modules,
        "unmeasured_modules": report.unmeasured_modules,
        "per_action": {
            action: {
                "view_corpus": report.view_count(action),
                "modules": report.module_counts(action),
                "entered_by": report.entered_by(action),
            }
            for action in report.view_actions
        },
        "uncovered_actions": report.uncovered_actions,
        "gates": "none -- this report blocks nothing and always exits 0",
    }


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def _load_view_actions(path: Path | None, view: str) -> list[str] | None:
    if path is None:
        return None
    try:
        from .generate_cases_from_tlc_dump import load_action_metadata, should_emit_action
    except ImportError:  # pragma: no cover - direct script execution
        from generate_cases_from_tlc_dump import (  # type: ignore[no-redef]
            load_action_metadata,
            should_emit_action,
        )

    metadata = load_action_metadata(Path(path), Path(path).parent)
    return [name for name, meta in metadata.items() if should_emit_action(meta, view)]


def _cmd_validate(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    if not manifest_path.is_file():
        print(f"ERROR: no manifest at {manifest_path}", file=sys.stderr)
        return 2
    errors = validate_case_modules(load_manifest(manifest_path))
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    declarations = load_declarations(load_manifest(manifest_path))
    if not declarations:
        print(f"{manifest_path}: no `{CASE_MODULES_KEY}:` block (that is not a problem)")
        return 0
    for name, declaration in sorted(declarations.items()):
        print(
            f"{name}: {declaration.form} of {declaration.extends}, "
            f"{len(declaration.actions)} action(s)"
            + (f", claim recorded ({len(declaration.claim)} chars)" if declaration.claim else "")
        )
    return 0


def _cmd_coverage(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    if not manifest_path.is_file():
        print(f"ERROR: no manifest at {manifest_path}", file=sys.stderr)
        return 2
    try:
        corpora = [read_coverage_record(Path(path)) for path in args.corpus]
        view_actions = _load_view_actions(
            Path(args.actions_metadata) if args.actions_metadata else None,
            args.view or "external",
        )
        report = build_report(
            manifest_path=manifest_path,
            corpora=corpora,
            view=args.view,
            view_actions=view_actions,
        )
    except CaseModuleError as error:
        # "I could not measure this" -- never "your coverage is insufficient".
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    print(render_report(report))
    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report_payload(report), indent=2, sort_keys=True) + "\n")
        print(f"\nwrote {out}")
    # Always 0 when the report could be produced. Uncovered actions are a
    # finding to read, not a build failure.
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Declared case modules: validate the manifest block and aggregate coverage."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Check the `case_modules:` block of a manifest.")
    validate.add_argument("--manifest", required=True, help="spec_manifest.yaml to read.")
    validate.set_defaults(func=_cmd_validate)

    coverage = sub.add_parser(
        "coverage",
        help="Aggregate per-action coverage across declared modules. Never gates; always exits 0.",
    )
    coverage.add_argument("--manifest", required=True, help="spec_manifest.yaml carrying case_modules:.")
    coverage.add_argument(
        "--corpus",
        action="append",
        default=[],
        help=(
            f"A generated case package (or its {COVERAGE_FILENAME}). Repeatable. A corpus "
            "whose module is declared in case_modules: counts as that module; any other "
            "counts as the view's own corpus."
        ),
    )
    coverage.add_argument("--view", help="Generation view to report (default: the first corpus's).")
    coverage.add_argument(
        "--actions-metadata",
        help="actions.yml supplying the view's action set. Without it the set is taken from the corpora.",
    )
    coverage.add_argument("--json", help="Also write the machine-readable report here.")
    coverage.set_defaults(func=_cmd_coverage)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
