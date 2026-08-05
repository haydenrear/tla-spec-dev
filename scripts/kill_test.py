#!/usr/bin/env python3
"""Oracle 4 -- the mutation kill test.

The first three oracles ask whether the representation is self-consistent
(TLC), whether its corpus is tractable (`analyze corpus`), and whether its
declared boundaries match observed behavior (`run effect-conformance`). None
of them asks the only question that makes a representation's quality
*falsifiable*:

    Hypothesis:  representation R captures the bug-relevant behavior of
                 component C at its port surface.
    Experiment:  seed k faults into C, run the distilled corpus, and require
                 the kill rate to meet ``kill_rate_floor``.

A mutant that SURVIVES is a refuted hypothesis at one specific place. It is
not a score; it is a pointer. The corpus executed a deliberately broken
program and could not tell it from the correct one, so the representation is
too abstract exactly at the boundary that mutant perturbs -- and the mutant
declares which model variable and which model action own that boundary. That
is why :class:`Mutant` requires ``refine_variable`` and ``refine_action``: a
mutant that cannot say what to refine when it survives is not worth seeding,
so the catalog loader rejects it rather than defaulting the fields.

Why the floor is a hard gate, and why it is the load-bearing one
----------------------------------------------------------------
Every other budget in this toolchain is a COST CAP: fewer states, fewer
cases, smaller components. Cost caps alone invite the obvious degeneracy --
shrink the model toward nothing and every cap passes. The kill rate is the
matching VALUE FLOOR, and it is what makes the cost caps safe, because a
trivial model stops killing mutants. Cost cap plus value floor is a real
optimization target; either one alone is a gameable number.

So there is deliberately NO waiver here. No ``--allow-below-floor``, no
``--accept-survivors``, no manifest key that records a sub-floor rate as
acceptable, no "unless overridden" branch. Below the floor FAILS. Suppression-
shaped keys found anywhere in the catalog are reported in
``ignored_suppression_keys`` and honored never. Weakening this gate would
weaken every cost cap in the toolchain at once, which is the whole reason it
exists.

Coverage is COMPUTED, not promised
-----------------------------------
"At minimum one fault per port and one per invariant" is not a rule the
catalog author is asked to remember. :func:`required_boundaries` derives the
obligation every run from the two declaration sites themselves -- the ports in
``spec_manifest.yaml`` under ``effects.components.*.ports``, and the
invariants in ``MC.cfg`` under ``INVARIANTS``. A boundary with no mutant is an
INCOMPLETE CATALOG and exits 2. Declaring a new port or adding a new invariant
therefore breaks the kill test until somebody seeds a fault for it. That is
the intended direction of pressure: the declarations drive the experiment, so
the experiment cannot silently fall behind the model.

Note what an incomplete catalog is NOT: it is not a low kill rate. Refusing to
compute a rate over an admittedly partial experiment is the same discipline
MF-027 applied to ``unobservable`` -- a number derived from a surface you
never covered carries no information, and reporting it as a passing 1.0 would
assert something the run has no evidence for.

Abstraction validation
----------------------
``references/architecture_tractability.md`` licenses an abstraction iff the
kill rate holds after it. :func:`compare_reports` implements exactly that:
given a baseline report from before a model revision, a kill rate that DROPS
means the abstraction deleted bug-relevant distinctions and is refused. A
re-representation that retains behavior keeps killing the same mutants; one
that deletes behavior stops. This is the mechanism that tells a legitimate
simplification from a disguised deletion, and it is why the standing
complexity objective can be pursued without quietly discarding coverage.

The control run
---------------
"Killed" is operationalized as "the corpus run failed", which means a corpus
that ALREADY FAILS on correct code kills every mutant trivially and reports a
perfect 1.0. :func:`control_run` therefore runs the corpus unmutated FIRST and
refuses when it is red. This is not a theoretical precaution: the first
end-to-end run of the worked distributed_history kill test scored 7/7 for
exactly this reason -- the corpus was failing an unrelated effect-oracle
finding before any fault was seeded. Without the control, that would have
shipped as a perfect score.

Exit codes (the toolchain-wide convention; no flag changes this mapping):
    0  kill rate met the floor
    1  kill rate below the floor, or a regression against a baseline
    2  incomplete catalog, malformed catalog, absent declarations, or a corpus
       that does not pass on the unmutated program
"""

from __future__ import annotations

import fnmatch
import json
import re
import shutil
import subprocess
import sys
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.budgets import load_budgets  # noqa: E402

EXIT_PASS = 0
EXIT_BELOW_FLOOR = 1
EXIT_USAGE = 2

#: The kill test met the floor over a complete catalog.
VERDICT_PASS = "pass"
#: A complete catalog was run and the kill rate fell below ``kill_rate_floor``.
VERDICT_BELOW_FLOOR = "below_floor"
#: A declared port or invariant has no seeded mutant. No rate is computed --
#: see the module docstring on why a partial experiment yields no number.
VERDICT_INCOMPLETE_CATALOG = "incomplete_catalog"
#: The kill rate dropped against a baseline: the abstraction under test
#: deleted bug-relevant behavior and is refused.
VERDICT_REGRESSED = "regressed"
#: The corpus does not pass on the UNMUTATED program, so no kill can be
#: attributed to any mutation. This dominates every other verdict -- see
#: :func:`control_run`.
VERDICT_NO_CONTROL = "control_failed"

BOUNDARY_PORT = "port"
BOUNDARY_INVARIANT = "invariant"
BOUNDARY_KINDS = (BOUNDARY_PORT, BOUNDARY_INVARIANT)

#: Keys that would, if honored, let a survivor or a sub-floor rate pass. They
#: are scanned for, reported loudly, and honored never -- the same treatment
#: MF-013/MF-027 gave gap suppression. Listing them here is not a feature; it
#: is a tripwire, so an attempt to add degeneracy shows up in the evidence.
SUPPRESSION_KEYS = frozenset(
    {
        "accept_survivor",
        "accept_survivors",
        "accepted_survivor",
        "allow_below_floor",
        "allow_survivor",
        "allow_survivors",
        "expected_to_survive",
        "ignore_survivor",
        "justification",
        "known_survivor",
        # EVAL-SUPPRESS. The A/B eval's control record
        # (`examples/validation/ab/eval/controls.toml`) introduced a second
        # family of suppression: `[[limitation]]` declares that an instrument
        # cannot decide a mutant, and `[[retired_control]]` declares that a
        # control's own declaration was falsified. Both are CHECKED constructs
        # -- a limitation must name a witness the run verifies against its own
        # executability counts, and since EVAL-SUPPRESS neither may convert a
        # demonstrated KILL -- but until then neither appeared on any
        # suppression list, so a reader auditing this file for "what can make a
        # survivor or a kill disappear" would not have found the one mechanism
        # that could (EVAL-RERUN-DF-02). Listing them changes nothing about how
        # they are honored, which is: on evidence, never on the say-so of the
        # key. It makes them visible in `ignored_suppression_keys` and, via
        # `scan_for_suppression`, in every artifact `run_controls.py` writes.
        "limitation",
        "limitation_on",
        "not_decidable",
        "override",
        "retired_control",
        "skip",
        # Listed so the scan enumerates each declared limitation INSTANCE
        # (`limitation[0].witness_ran_must_be`) and not merely the fact that
        # the file uses the construct. It is also literally a key that, if
        # honored on its say-so instead of checked against the run's own
        # counts, lets a cell pass -- which is this list's own definition.
        "witness_ran_must_be",
        "skip_kill_test",
        "survivor_ok",
        "suppress",
        "tolerate",
        "waiver",
        "waived",
        "xfail",
    }
)


class KillTestCatalogError(Exception):
    """The mutant catalog is malformed. Always an exit-2 refusal."""


# --------------------------------------------------------------------------
# Mutants
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class Mutant:
    """One seeded fault at one modeled boundary.

    ``find``/``replace`` is a literal, reviewable text substitution in a real
    production source file. It is deliberately not a random AST perturbation:
    a kill test whose mutants nobody can read produces survivors nobody can
    act on, and the survivor's whole value here is that it points somewhere.

    ``refine_variable`` and ``refine_action`` are the pointer. They name the
    model element that OWNS this boundary, so a survivor reads as "refine
    this variable / this action", not as a decimal that dropped.
    """

    id: str
    boundary_kind: str
    boundary_ref: str
    path: str
    find: str
    replace: str
    description: str
    refine_variable: str
    refine_action: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "boundary_kind": self.boundary_kind,
            "boundary_ref": self.boundary_ref,
            "path": self.path,
            "find": self.find,
            "replace": self.replace,
            "description": self.description,
            "refine_variable": self.refine_variable,
            "refine_action": self.refine_action,
        }

    @property
    def boundary(self) -> tuple[str, str]:
        return (self.boundary_kind, self.boundary_ref)


REQUIRED_MUTANT_FIELDS = (
    "id",
    "boundary_kind",
    "boundary_ref",
    "path",
    "find",
    "replace",
    "description",
    "refine_variable",
    "refine_action",
)


def parse_mutants(raw: Any, *, source: str = "<catalog>") -> tuple[list[Mutant], list[str]]:
    """Build mutants from parsed catalog data.

    Returns ``(mutants, ignored_suppression_keys)``. Every field in
    :data:`REQUIRED_MUTANT_FIELDS` is required. Nothing is defaulted -- a
    mutant that omits ``refine_variable`` cannot point at anything when it
    survives, and a mutant that omits ``boundary_ref`` cannot be counted
    toward coverage, so both are refusals rather than shrugs.
    """

    if not isinstance(raw, dict):
        raise KillTestCatalogError(f"{source}: catalog root must be a mapping")
    entries = raw.get("mutants")
    if not isinstance(entries, list) or not entries:
        raise KillTestCatalogError(
            f"{source}: catalog declares no mutants. An empty catalog is not a passing kill "
            f"test -- seed one fault per declared port and one per invariant."
        )

    suppressions = sorted(_scan_for_suppression(raw))
    mutants: list[Mutant] = []
    seen: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise KillTestCatalogError(f"{source}: mutant #{index} is not a mapping")
        missing = [key for key in REQUIRED_MUTANT_FIELDS if not entry.get(key)]
        if missing:
            raise KillTestCatalogError(
                f"{source}: mutant #{index} ({entry.get('id', '<no id>')}) is missing required "
                f"field(s) {', '.join(missing)}. Every field is required: a mutant that cannot "
                f"name the variable and action to refine is useless when it survives."
            )
        kind = str(entry["boundary_kind"])
        if kind not in BOUNDARY_KINDS:
            raise KillTestCatalogError(
                f"{source}: mutant {entry['id']} has boundary_kind {kind!r}; "
                f"expected one of {', '.join(BOUNDARY_KINDS)}"
            )
        mutant_id = str(entry["id"])
        if mutant_id in seen:
            raise KillTestCatalogError(f"{source}: duplicate mutant id {mutant_id!r}")
        seen.add(mutant_id)
        mutants.append(
            Mutant(
                id=mutant_id,
                boundary_kind=kind,
                boundary_ref=str(entry["boundary_ref"]),
                path=str(entry["path"]),
                find=str(entry["find"]),
                replace=str(entry["replace"]),
                description=str(entry["description"]),
                refine_variable=str(entry["refine_variable"]),
                refine_action=str(entry["refine_action"]),
            )
        )
    return mutants, suppressions


def scan_for_suppression(node: Any, prefix: str = "") -> set[str]:
    """Public entry point for anything else that loads a catalog-shaped file.

    `examples/validation/ab/eval/run_controls.py` calls this on every catalogue
    it is given, so the eval's own `[[limitation]]` and `[[retired_control]]`
    constructs are enumerated in the run artifact by the same scanner and
    against the same list as the kill test's own (EVAL-SUPPRESS). One list, one
    scanner, one place to look.
    """

    return _scan_for_suppression(node, prefix)


def _scan_for_suppression(node: Any, prefix: str = "") -> set[str]:
    """Collect suppression-shaped keys anywhere in the catalog.

    They are never honored. Reporting them is the point: an attempt to add a
    waiver becomes visible in the evidence rather than becoming behavior.
    """

    found: set[str] = set()
    if isinstance(node, dict):
        for key, value in node.items():
            dotted = f"{prefix}.{key}" if prefix else str(key)
            if str(key).lower() in SUPPRESSION_KEYS:
                found.add(dotted)
            found |= _scan_for_suppression(value, dotted)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found |= _scan_for_suppression(value, f"{prefix}[{index}]")
    return found


def load_catalog(path: Path) -> tuple[list[Mutant], list[str]]:
    """Load a TOML mutant catalog."""

    path = Path(path)
    if not path.is_file():
        raise KillTestCatalogError(
            f"no mutant catalog at {path}. The kill test has no fault to seed, which is not "
            f"the same as a program with no faults -- declare the catalog."
        )
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
        try:
            import tomli as tomllib  # type: ignore[no-redef]
        except ModuleNotFoundError as exc:
            # Deliberately NOT the simple-parser fallback that
            # run_generated_case_adapters uses for adapter mappings. Mutant
            # catalogs contain multi-line literals, and a parser that silently
            # dropped the entries it could not read would hand back a smaller
            # catalog that still looked complete -- the exact coverage drift
            # this module exists to prevent. Refuse instead.
            raise KillTestCatalogError(
                f"no TOML parser available on {sys.executable} (Python "
                f"{sys.version_info.major}.{sys.version_info.minor}). The mutant catalog is "
                f"not parsed with the simple fallback parser used for adapter mappings, "
                f"because a partially-read catalog would under-report the required boundary "
                f"set and report a complete kill test over a surface it never covered. "
                f"Run this command on Python 3.11+ or install `tomli`."
            ) from exc
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - surfaced as a refusal
        raise KillTestCatalogError(f"{path}: could not parse catalog: {exc}") from exc
    return parse_mutants(raw, source=str(path))


# --------------------------------------------------------------------------
# Required coverage, derived from the declarations themselves
# --------------------------------------------------------------------------


def declared_ports(manifest_path: Path) -> list[str]:
    """Port ids declared under ``effects.components.*.ports``.

    Read straight from the manifest so the obligation tracks the model. A
    manifest that declares no ports is an exit-2 refusal at the call site: a
    component with no port surface has no boundary to test, and silently
    computing a kill rate over zero ports would be the "check that disables
    itself when its input is absent" the doctrine forbids.
    """

    data = _read_yaml(manifest_path)
    if not isinstance(data, dict):
        return []
    effects = data.get("effects")
    if not isinstance(effects, dict):
        return []
    components = effects.get("components")
    if not isinstance(components, dict):
        return []
    ports: list[str] = []
    for component in components.values():
        if not isinstance(component, dict):
            continue
        declared = component.get("ports")
        if isinstance(declared, dict):
            ports.extend(str(name) for name in declared)
        elif isinstance(declared, list):
            for item in declared:
                if isinstance(item, dict) and item.get("id"):
                    ports.append(str(item["id"]))
                elif isinstance(item, str):
                    ports.append(item)
    return sorted(set(ports))


#: TLC section keywords that terminate an INVARIANTS block.
_CFG_SECTIONS = frozenset(
    {
        "SPECIFICATION",
        "INIT",
        "NEXT",
        "CONSTANT",
        "CONSTANTS",
        "INVARIANT",
        "INVARIANTS",
        "PROPERTY",
        "PROPERTIES",
        "SYMMETRY",
        "CONSTRAINT",
        "CONSTRAINTS",
        "ACTION_CONSTRAINT",
        "ACTION_CONSTRAINTS",
        "VIEW",
        "ALIAS",
        "CHECK_DEADLOCK",
        "POSTCONDITION",
    }
)

_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def declared_invariants(cfg_path: Path) -> list[str]:
    """Invariant names declared in a TLC config.

    Both TLC spellings are handled, because getting this wrong would silently
    shrink the required-boundary set and hand back a kill test that looks
    complete while covering nothing:

        INVARIANT  Foo                (inline, one or more names)
        INVARIANTS                    (block, one name per following line)
          Foo
          Bar
    """

    if not Path(cfg_path).is_file():
        return []
    names: list[str] = []
    in_block = False
    for raw_line in Path(cfg_path).read_text(encoding="utf-8").splitlines():
        line = raw_line.split("\\*", 1)[0].strip()
        if not line:
            continue
        head, _, rest = line.partition(" ")
        if head in _CFG_SECTIONS:
            if head in ("INVARIANT", "INVARIANTS"):
                in_block = True
                # Inline form: any names on the same line are invariants.
                names.extend(_IDENT.findall(rest))
            else:
                in_block = False
            continue
        if in_block:
            if _IDENT.fullmatch(line):
                names.append(line)
            else:
                in_block = False
    # Preserve declaration order while dropping duplicates.
    seen: set[str] = set()
    return [name for name in names if not (name in seen or seen.add(name))]


def required_boundaries(spec_dir: Path, cfg_names: Sequence[str] | None = None) -> list[tuple[str, str]]:
    """Every boundary that MUST carry at least one seeded fault.

    This is the mechanism behind "one per port and one per invariant". It is
    recomputed from ``spec_manifest.yaml`` and ``MC.cfg`` on every run, so the
    obligation cannot drift behind the model: add a port, and the kill test
    refuses until a mutant exists for it.
    """

    spec_dir = Path(spec_dir)
    boundaries = [(BOUNDARY_PORT, name) for name in declared_ports(spec_dir / "spec_manifest.yaml")]

    # EVERY TLC config in the spec directory contributes its invariants by
    # default. A repository split into Internal.cfg/External.cfg would
    # otherwise silently drop half its invariants from the required set and
    # report a complete catalog -- the failure mode this whole function exists
    # to prevent. Ordering is by filename so the required set is stable.
    #
    # `cfg_names` narrows this to named configs, because a kill test measures
    # ONE component's representation with THAT component's corpus, and a
    # repository with two models has two kill tests rather than one blended
    # one. Three things keep this from being an escape hatch: the strict
    # behavior is the DEFAULT (omitting it requires every invariant in the
    # directory), the narrowing is explicit and names a real config file, and
    # it reduces only the COVERAGE OBLIGATION -- never the set of mutants that
    # actually run. Every mutant in the catalog is executed either way, so a
    # mutant outside the scoped model still reports if it survives.
    if cfg_names:
        cfg_paths = []
        for name in cfg_names:
            cfg_path = spec_dir / name
            if not cfg_path.is_file():
                raise KillTestCatalogError(
                    f"no such model config: {cfg_path}. Scoping must name a real config; "
                    f"it cannot silently select nothing."
                )
            cfg_paths.append(cfg_path)
    else:
        cfg_paths = sorted(spec_dir.glob("*.cfg"))

    seen: set[str] = set()
    for cfg_path in cfg_paths:
        for name in declared_invariants(cfg_path):
            if name not in seen:
                seen.add(name)
                boundaries.append((BOUNDARY_INVARIANT, name))
    return boundaries


def missing_boundaries(
    mutants: Sequence[Mutant], required: Sequence[tuple[str, str]]
) -> list[tuple[str, str]]:
    covered = {mutant.boundary for mutant in mutants}
    return [boundary for boundary in required if boundary not in covered]


# --------------------------------------------------------------------------
# Running mutants
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class MutantOutcome:
    """One row of the kill matrix."""

    mutant_id: str
    boundary_kind: str
    boundary_ref: str
    killed: bool
    killed_by: list[str]
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "mutant_id": self.mutant_id,
            "boundary_kind": self.boundary_kind,
            "boundary_ref": self.boundary_ref,
            "killed": self.killed,
            "killed_by": sorted(self.killed_by),
            "detail": self.detail,
        }


@contextmanager
def seeded(mutant: Mutant, root: Path) -> Iterator[Path]:
    """Apply ``mutant`` to a real source file, then always restore it.

    The restore is in a ``finally`` so an exception mid-run cannot leave a
    fault seeded in the tree. A kill test that can corrupt the working copy
    would be a worse defect than the one it is looking for.
    """

    target = Path(root) / mutant.path
    if not target.is_file():
        raise KillTestCatalogError(f"mutant {mutant.id}: no such file {target}")
    original = target.read_text(encoding="utf-8")
    if mutant.find not in original:
        raise KillTestCatalogError(
            f"mutant {mutant.id}: pattern not found in {mutant.path}. The mutant has gone stale "
            f"against the code it was written for -- a stale mutant that no longer applies is "
            f"not a killed mutant, so this refuses rather than scoring it."
        )
    patched = original.replace(mutant.find, mutant.replace, 1)
    if patched == original:
        raise KillTestCatalogError(f"mutant {mutant.id}: substitution changed nothing")
    try:
        target.write_text(patched, encoding="utf-8")
        yield target
    finally:
        target.write_text(original, encoding="utf-8")


#: A case runner takes a seeded mutant and returns ``(killed, killed_by, detail)``.
#: Passing ``None`` instead of a mutant means "run the corpus unmutated" -- the
#: control run. Every runner must support it; see :func:`control_run`.
CaseRunner = Callable[["Mutant | None"], "tuple[bool, list[str], str]"]


def control_run(runner: CaseRunner) -> tuple[bool, str]:
    """Run the corpus against the UNMUTATED program. Returns ``(green, detail)``.

    This is the experiment's control, and omitting it is the single most
    dangerous degeneracy a kill test can have. "Killed" is operationalized as
    "the corpus run failed", so a corpus that ALREADY FAILS on correct code
    kills every mutant trivially and reports a perfect 1.0 -- a maximally
    flattering number carrying exactly zero information about the
    representation.

    This is not hypothetical. The first end-to-end run of the worked
    distributed_history kill test scored 7/7 for precisely this reason: the
    corpus command was failing on the effect oracle's dead-surface finding
    before any mutant was seeded, and every "kill" was that same unrelated
    failure. The kill rate looked perfect and meant nothing.

    So a red control REFUSES rather than scoring. It is reported as its own
    verdict, not folded into ``below_floor``, because the remedy is completely
    different: fix the corpus, then measure. Nothing about the representation
    has been learned either way.
    """

    failed, _, detail = runner(None)
    # The runner's contract is inverted here on purpose: it reports "killed",
    # which for the unmutated program means "the corpus failed".
    return (not failed), detail


def subprocess_case_runner(
    command: Sequence[str],
    *,
    root: Path,
    timeout: int = 600,
) -> CaseRunner:
    """Run the distilled corpus in a child process; nonzero exit == killed.

    IMPORTANT, and recorded here rather than in a note nobody reads: this
    runner SHELLS OUT. Under the MF-027 effect oracle a ``process.spawn`` is
    an ``unobservable`` boundary even when a matching port is declared, and
    this repository declares two such ports (``tlc_process`` -> ``*java*``,
    ``test_process`` -> ``*pytest*``). A kill-test run driven this way must
    therefore execute OUTSIDE the effect sandbox; run it inside and the two
    oracles deadlock, with the effect oracle correctly refusing the very
    spawns the kill test needs. That is not a reason to relax either oracle --
    it is a real constraint on how the kill test can be run in this
    repository, and MF-023 must resolve it when it runs the corpus for real.
    """

    def _invoke() -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            list(command),
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

    def run(mutant: Mutant | None) -> tuple[bool, list[str], str]:
        if mutant is None:
            # Control run: no fault seeded.
            completed = _invoke()
        else:
            with seeded(mutant, root):
                completed = _invoke()
        killed = completed.returncode != 0
        detail = (completed.stdout + completed.stderr).strip()
        return killed, _failing_case_names(detail), detail[-4000:]

    return run


_CASE_NAME = re.compile(r"^(?P<name>[\w./\[\]-]+)(?: via [\w.]+)?: ", re.MULTILINE)


def _failing_case_names(output: str) -> list[str]:
    return sorted({match.group("name") for match in _CASE_NAME.finditer(output)})


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------


@dataclass
class KillTestReport:
    """The kill matrix, the gate verdict, and the refinement pointers."""

    spec_dir: str
    manifest_path: str
    kill_rate_floor: float
    outcomes: list[MutantOutcome] = field(default_factory=list)
    missing: list[tuple[str, str]] = field(default_factory=list)
    required: list[tuple[str, str]] = field(default_factory=list)
    ignored_suppression_keys: list[str] = field(default_factory=list)
    baseline_kill_rate: float | None = None
    baseline_source: str | None = None
    corpus_command: str = ""
    control_green: bool | None = None
    control_detail: str = ""
    notes: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.outcomes)

    @property
    def killed(self) -> int:
        return sum(1 for outcome in self.outcomes if outcome.killed)

    @property
    def survivors(self) -> list[MutantOutcome]:
        return [outcome for outcome in self.outcomes if not outcome.killed]

    @property
    def kill_rate(self) -> float | None:
        """``None`` when the catalog is incomplete.

        Deliberately not 0.0 and deliberately not 1.0. A rate computed over a
        surface that was never fully covered is not a measurement, and giving
        it a number invites treating it as one.
        """

        if self.control_green is False or self.missing or not self.outcomes:
            return None
        return self.killed / self.total

    @property
    def verdict(self) -> str:
        # Control dominates everything: without a green control run, no kill
        # can be attributed to any mutation, so no other verdict is meaningful.
        if self.control_green is False:
            return VERDICT_NO_CONTROL
        if self.missing:
            return VERDICT_INCOMPLETE_CATALOG
        rate = self.kill_rate
        if rate is None:
            return VERDICT_INCOMPLETE_CATALOG
        if self.baseline_kill_rate is not None and rate < self.baseline_kill_rate:
            return VERDICT_REGRESSED
        if rate < self.kill_rate_floor:
            return VERDICT_BELOW_FLOOR
        return VERDICT_PASS

    @property
    def ok(self) -> bool:
        """One conjunction, consulting no configuration.

        There is no second code path here that a later change could relax
        independently, and no argument, environment variable, or manifest key
        participates. Below the floor is False. Incomplete is False. A
        regression against the baseline is False.
        """

        return self.verdict == VERDICT_PASS

    @property
    def exit_code(self) -> int:
        if self.verdict in (VERDICT_INCOMPLETE_CATALOG, VERDICT_NO_CONTROL):
            return EXIT_USAGE
        if self.verdict in (VERDICT_BELOW_FLOOR, VERDICT_REGRESSED):
            return EXIT_BELOW_FLOOR
        return EXIT_PASS

    def refinement_pointers(self, catalog: Sequence[Mutant]) -> list[dict[str, Any]]:
        """Turn each survivor into an instruction, not a statistic.

        This is the whole reason the kill test is worth running. "Kill rate
        0.71" tells nobody what to do. "Mutant port-tlc-process survived: the
        corpus never distinguished it, so the representation is too abstract
        at variable ``complexity_gate`` / action ``AnalyzeComplexity``" names
        the exact place the model is lying and the exact edit that would fix
        it.
        """

        by_id = {mutant.id: mutant for mutant in catalog}
        pointers: list[dict[str, Any]] = []
        for outcome in self.survivors:
            mutant = by_id.get(outcome.mutant_id)
            if mutant is None:
                continue
            pointers.append(
                {
                    "mutant_id": mutant.id,
                    "boundary_kind": mutant.boundary_kind,
                    "boundary_ref": mutant.boundary_ref,
                    "seeded_fault": mutant.description,
                    "source_path": mutant.path,
                    "refine_variable": mutant.refine_variable,
                    "refine_action": mutant.refine_action,
                    "message": (
                        f"SURVIVED: {mutant.id} seeded a fault at {mutant.boundary_kind} "
                        f"'{mutant.boundary_ref}' ({mutant.description}) and the distilled "
                        f"corpus could not tell the broken program from the correct one. The "
                        f"representation is too abstract at this boundary. Refine variable "
                        f"'{mutant.refine_variable}' (widen its domain so the faulted and "
                        f"correct behaviors land in different states) or action "
                        f"'{mutant.refine_action}' (tighten its guard or postcondition so a "
                        f"generated case exercises the difference). Then re-run; the mutant "
                        f"must die."
                    ),
                }
            )
        return pointers

    def to_dict(self, catalog: Sequence[Mutant] = ()) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "ok": self.ok,
            "exit_code": self.exit_code,
            "kill_rate": self.kill_rate,
            "kill_rate_floor": self.kill_rate_floor,
            "baseline_kill_rate": self.baseline_kill_rate,
            "baseline_source": self.baseline_source,
            "mutants_total": self.total,
            "mutants_killed": self.killed,
            "mutants_survived": len(self.survivors),
            "spec_dir": self.spec_dir,
            "manifest_path": self.manifest_path,
            "corpus_command": self.corpus_command,
            "control_green": self.control_green,
            "control_detail": self.control_detail,
            "required_boundaries": [
                {"kind": kind, "ref": ref} for kind, ref in self.required
            ],
            "uncovered_boundaries": [
                {"kind": kind, "ref": ref} for kind, ref in self.missing
            ],
            "kill_matrix": [outcome.to_dict() for outcome in self.outcomes],
            "surviving_mutants": self.refinement_pointers(catalog),
            "ignored_suppression_keys": self.ignored_suppression_keys,
            "suppression_policy": (
                "Suppression-shaped keys are reported and never honored. There is no waiver "
                "for a surviving mutant and no flag that accepts a sub-floor kill rate."
            ),
            "notes": self.notes,
            "summary": self.summary(),
        }

    def summary(self) -> str:
        if self.control_green is False:
            return (
                "CONTROL FAILED: the corpus does not pass on the UNMUTATED program, so every "
                "mutant would be recorded as killed by that same pre-existing failure and the "
                "kill rate would be a meaningless 1.0. Fix the corpus, then measure. Nothing "
                "has been learned about the representation."
            )
        if self.missing:
            listed = ", ".join(f"{kind} {ref}" for kind, ref in self.missing)
            return (
                f"INCOMPLETE CATALOG: {len(self.missing)} declared boundary/boundaries carry no "
                f"seeded fault ({listed}). No kill rate is computed over a partial experiment."
            )
        rate = self.kill_rate
        assert rate is not None
        base = (
            f"kill rate {rate:.3f} ({self.killed}/{self.total} mutants killed) "
            f"against floor {self.kill_rate_floor:.3f}"
        )
        if self.verdict == VERDICT_REGRESSED:
            return (
                f"REGRESSED: {base}; baseline was {self.baseline_kill_rate:.3f}. The model "
                f"revision under test kills fewer mutants than the one it replaces, so it "
                f"deleted bug-relevant behavior. That is not a legitimate abstraction."
            )
        if self.verdict == VERDICT_BELOW_FLOOR:
            return (
                f"BELOW FLOOR: {base}. {len(self.survivors)} mutant(s) survived; each names the "
                f"variable and action to refine. There is no waiver."
            )
        return f"PASS: {base}."

    def write(self, path: Path, catalog: Sequence[Mutant] = ()) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(self.to_dict(catalog), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return path


def render_report(report: KillTestReport, catalog: Sequence[Mutant] = ()) -> str:
    """Human-readable kill matrix and refinement pointers."""

    lines: list[str] = []
    lines.append("Mutation kill test (oracle 4)")
    lines.append("=" * 60)
    lines.append(f"spec dir : {report.spec_dir}")
    lines.append(f"manifest : {report.manifest_path}")
    if report.corpus_command:
        lines.append(f"corpus   : {report.corpus_command}")
    lines.append("")

    lines.append(f"Required boundaries ({len(report.required)}):")
    covered = {(o.boundary_kind, o.boundary_ref) for o in report.outcomes}
    for kind, ref in report.required:
        mark = "seeded" if (kind, ref) in covered else "NO MUTANT"
        lines.append(f"  [{mark:>9}] {kind:<9} {ref}")
    lines.append("")

    if report.outcomes:
        lines.append("Kill matrix:")
        width = max(len(o.mutant_id) for o in report.outcomes)
        for outcome in report.outcomes:
            mark = "KILLED" if outcome.killed else "SURVIVED"
            lines.append(
                f"  {outcome.mutant_id:<{width}}  {mark:<8}  "
                f"{outcome.boundary_kind}:{outcome.boundary_ref}"
            )
        lines.append("")

    pointers = report.refinement_pointers(catalog)
    if pointers:
        lines.append("Surviving-mutant analysis -- what to refine:")
        for pointer in pointers:
            lines.append(f"  * {pointer['message']}")
        lines.append("")

    if report.ignored_suppression_keys:
        lines.append("Suppression-shaped keys found and IGNORED (never honored):")
        for key in report.ignored_suppression_keys:
            lines.append(f"  ! {key}")
        lines.append("")

    for note in report.notes:
        lines.append(f"note: {note}")
    if report.notes:
        lines.append("")

    if report.control_green is False:
        lines.append("Control run (unmutated program) FAILED. Corpus output:")
        for line in report.control_detail.splitlines()[-25:]:
            lines.append(f"  | {line}")
        lines.append("")

    lines.append(report.summary())
    if not report.ok:
        lines.append("")
        if report.verdict == VERDICT_NO_CONTROL:
            lines.append(
                "REFUSING to seed any mutant. The corpus must pass on the correct program "
                "before it can be asked to detect a broken one -- otherwise every mutant is "
                "recorded as killed by the pre-existing failure and the kill rate is 1.0 by "
                "construction. There is no flag that skips the control."
            )
        elif report.verdict == VERDICT_INCOMPLETE_CATALOG:
            lines.append(
                "REFUSING to score a partial experiment. Seed one fault per uncovered "
                "boundary above. There is no flag that skips a boundary."
            )
        else:
            lines.append(
                "REFUSING. Raise the kill rate by refining the representation at the "
                "boundaries named above. The floor is not waivable: it is the value floor "
                "that makes every cost cap in this toolchain safe, because a trivial model "
                "passes every cap and kills no mutants."
            )
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# Orchestration
# --------------------------------------------------------------------------


def run_kill_test(
    *,
    spec_dir: Path,
    catalog: Sequence[Mutant],
    runner: CaseRunner,
    root: Path,
    suppressions: Sequence[str] = (),
    baseline: dict[str, Any] | None = None,
    baseline_source: str | None = None,
    corpus_command: str = "",
    cfg_names: Sequence[str] | None = None,
    warn: bool = True,
    stream: Any = None,
) -> KillTestReport:
    """Seed every mutant, run the corpus against each, and gate the rate."""

    spec_dir = Path(spec_dir)
    manifest_path = spec_dir / "spec_manifest.yaml"
    budgets = load_budgets(manifest_path, warn=warn, stream=stream)
    floor = float(budgets["kill_rate_floor"])

    required = required_boundaries(spec_dir, cfg_names)
    report = KillTestReport(
        spec_dir=str(spec_dir),
        manifest_path=str(manifest_path),
        kill_rate_floor=floor,
        required=required,
        ignored_suppression_keys=list(suppressions),
        corpus_command=corpus_command,
    )
    report.missing = missing_boundaries(catalog, required)

    if report.missing:
        # Do not run a partial experiment. See the module docstring.
        return report

    # THE CONTROL. Before seeding anything, prove the corpus passes on the
    # unmutated program. A red corpus kills every mutant trivially and reports
    # a perfect, meaningless 1.0. See control_run().
    green, control_detail = control_run(runner)
    report.control_green = green
    report.control_detail = control_detail[-4000:]
    if not green:
        return report

    for mutant in catalog:
        killed, killed_by, detail = runner(mutant)
        report.outcomes.append(
            MutantOutcome(
                mutant_id=mutant.id,
                boundary_kind=mutant.boundary_kind,
                boundary_ref=mutant.boundary_ref,
                killed=killed,
                killed_by=list(killed_by),
                detail=detail,
            )
        )

    if baseline is not None:
        rate = baseline.get("kill_rate")
        if isinstance(rate, (int, float)):
            report.baseline_kill_rate = float(rate)
            report.baseline_source = baseline_source

    return report


def compare_reports(before: dict[str, Any], after: dict[str, Any]) -> tuple[bool, str]:
    """Abstraction validator: an abstraction is legitimate iff the rate holds.

    Returns ``(legitimate, message)``. A drop is refused. Note the asymmetry
    is intentional: a RISE is fine (the revision made the model sharper), a
    HOLD is fine (the revision was a true re-representation), a DROP is a
    deletion of bug-relevant behavior wearing the costume of a simplification.
    This is the check that lets the standing complexity objective be pursued
    honestly -- without it, "47% fewer states" and "deleted half the coverage"
    look identical from the outside.
    """

    before_rate = before.get("kill_rate")
    after_rate = after.get("kill_rate")
    if not isinstance(before_rate, (int, float)):
        return False, "baseline report has no kill_rate; cannot validate the abstraction"
    if not isinstance(after_rate, (int, float)):
        return False, "revised report has no kill_rate; cannot validate the abstraction"
    before_killed = {
        row["mutant_id"] for row in before.get("kill_matrix", []) if row.get("killed")
    }
    after_killed = {
        row["mutant_id"] for row in after.get("kill_matrix", []) if row.get("killed")
    }
    lost = sorted(before_killed - after_killed)
    if after_rate < before_rate:
        return False, (
            f"ABSTRACTION REFUSED: kill rate fell {before_rate:.3f} -> {after_rate:.3f}. "
            f"Mutants that the previous representation killed and this one does not: "
            f"{', '.join(lost) or '(none by id; the catalog changed)'}. A revision that kills "
            f"fewer mutants deleted externally-visible behavior; it is not a re-representation."
        )
    if lost:
        return False, (
            f"ABSTRACTION REFUSED: the kill rate held ({before_rate:.3f} -> {after_rate:.3f}) "
            f"but these previously-killed mutants now survive: {', '.join(lost)}. The rate is "
            f"an aggregate; a swap that loses one boundary and gains another is still a lost "
            f"boundary."
        )
    return True, (
        f"abstraction legitimate: kill rate {before_rate:.3f} -> {after_rate:.3f} and every "
        f"previously-killed mutant is still killed"
    )


def gate_report(
    spec_dir: Path,
    catalog_path: Path,
    runner: CaseRunner,
    *,
    root: Path,
    baseline: dict[str, Any] | None = None,
) -> tuple[bool, str]:
    """Run the kill-test gate. Returns ``(passed, message)``.

    Deliberately the same shape as ``analyze_complexity.gate_report`` and
    ``corpus_diagnostics.gate_report`` so all four oracles read identically at
    every call site.
    """

    catalog, suppressions = load_catalog(catalog_path)
    report = run_kill_test(
        spec_dir=spec_dir,
        catalog=catalog,
        runner=runner,
        root=root,
        suppressions=suppressions,
        baseline=baseline,
    )
    return report.ok, report.summary()


def _read_yaml(path: Path) -> Any:
    """Parse a manifest, preferring PyYAML and falling back to the repo parser."""

    path = Path(path)
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore[import-untyped]

        return yaml.safe_load(text)
    except ModuleNotFoundError:
        pass
    try:
        from scripts.budgets import _read_manifest  # noqa: PLC0415

        return _read_manifest(path)
    except Exception:  # noqa: BLE001
        return None


__all__ = [
    "EXIT_BELOW_FLOOR",
    "EXIT_PASS",
    "EXIT_USAGE",
    "KillTestCatalogError",
    "KillTestReport",
    "Mutant",
    "MutantOutcome",
    "VERDICT_BELOW_FLOOR",
    "VERDICT_INCOMPLETE_CATALOG",
    "VERDICT_PASS",
    "VERDICT_NO_CONTROL",
    "VERDICT_REGRESSED",
    "compare_reports",
    "control_run",
    "declared_invariants",
    "declared_ports",
    "gate_report",
    "load_catalog",
    "missing_boundaries",
    "parse_mutants",
    "render_report",
    "required_boundaries",
    "run_kill_test",
    "seeded",
    "subprocess_case_runner",
]
