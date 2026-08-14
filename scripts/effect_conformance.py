#!/usr/bin/env python3
"""Effect conformance harness (MF-013).

Ticket 007 made resource boundaries first-class. This module makes the check
mechanical: components declare typed emissions on named ports, the runner
executes an adapter inside a sandbox that *passively* records what actually
crossed a boundary, and the two are diffed per case.

Three surfaces:

1. **Declaration.** ``effects:`` in the manifest (or ``actions.yml``) names
   each component's ports, gives every port a type and a target pattern, and
   says which ports each action may emit on. A port is the only way anything
   leaves a component.

2. **Observation.** :class:`EffectSandbox` patches the real boundaries --
   filesystem writes/deletes, process spawns, socket connects, HTTP -- and
   records every crossing. Observation is passive by construction: an adapter
   cannot decline to report an effect, because it is not the adapter doing the
   reporting. Temp dirs and fake transports are handed to the adapter so the
   effects are contained, not so they are hidden.

   **The sandbox observes the in-process CPython runtime and nothing else**
   (MF-027). Its patches are monkeypatches on ``builtins.open``, ``os``,
   ``shutil``, ``pathlib.Path``, ``subprocess`` and ``socket`` objects living
   in *this* interpreter. No patch crosses a process boundary. A Java or
   Kotlin adapter in a separate JVM, a JBang/uv Test Graph node, or any
   adapter that delegates its real work to a child process is therefore
   **invisible** to it.

   MF-027 makes that edge declared rather than silent. Observability is
   granted only on positive evidence -- the adapter was actually imported and
   called as a Python object in this interpreter -- and is refused otherwise.
   A refused target produces the :data:`VERDICT_UNOBSERVABLE` verdict, which
   is a **failure**, not a clean report. See :class:`UnobservableTarget` and
   :func:`assess_target_observability`.

   **MF-033 adds a SECOND observer that reaches across the boundary.** MF-028
   measured that every adapter in this repository shells out, so the in-process
   sandbox saw only the spawn and refused. :class:`WorkingTreeObserver` sees the
   child a different way -- it snapshots the working-tree roots before the child
   runs and diffs them after, so files the child created/changed/deleted become
   real ``filesystem.write``/``filesystem.delete`` observations regardless of the
   child's runtime. This is added observability, not a weakened refusal: the
   observer covers only the axes it can positively prove (the filesystem), and
   :func:`diff_effects` narrows a spawn's process-boundary finding to name only
   the axes still unwatched (network, nested spawns) -- which keeps the verdict
   ``unobservable`` until *every* axis has an observer. A spawn with no
   out-of-process evidence is unchanged: still fully unobservable. Nothing here
   downgrades a verdict; it only lets the run SEE more, and report what it still
   cannot.

3. **Diff.** Observed effects are matched against the ports declared for the
   case's action. Two findings, both hard failures:

   - An **undeclared observed effect** is a gap: the model is blind to real
     behavior, which is the one thing a representation may not be. The gap is
     recorded AND the run fails.
   - A **declared-but-never-observed port** across the whole corpus is dead
     model surface: remove the port, or produce a case that exercises it.

4. **Execution.** :func:`execute_corpus` drives a generated case corpus through
   the mapped adapters inside the sandbox. HP-04 moved it here from the CLI
   shim, because running it for the first time in the project's history found
   three defects that four rounds of *reading* the oracle had not:

   - **It could not import the adapters of a project the CLI itself
     scaffolds** (RC-02-DF-02). ``case_adapters.toml`` names adapters as bare
     module paths (``production_adapters:BuildSkillCliAdapter``) and nothing
     put the target spec directory on ``sys.path``, so the very first run died
     with ``ModuleNotFoundError`` before a single case executed.
     :func:`corpus_import_roots` now builds the same root set the enforcing
     runner gets on ``PYTHONPATH``.
   - **It aborted the whole run on the first adapter that could not take a
     case** (RC-02-DF-03). Nine of seventeen adapters in this repository's own
     model implement ``apply()`` and no ``run(case, work_dir)``. A skip is a
     **report** (:class:`SkippedCase`), never a refusal, and never silence: the
     summary line carries the executed/skipped/unbound action counts, and a
     declared port whose every action was skipped is annotated as UNEXERCISED
     rather than read as proven dead.
   - **Its findings were not reproducible** (MF026-R4-F-01): 20 / 15 / 14 gaps
     across three runs of an identical corpus on an identical tree, because the
     work directory persisted between runs and an adapter that materializes its
     own before-state writes a file on the first run that it finds already
     present on the second. A gap count that moves 43% is not a number anything
     can cite. :func:`reset_case_work_dir` gives every case an empty directory,
     so the run is a function of the corpus and the tree and of nothing else.

**NOTHING SUPPRESSES A GAP REPORT.** There is no justification field, no
annotation, no manifest entry, and no flag that turns a gap into a pass. The
2026-07-18 degeneracy audit found this ticket's original criteria
("fails *or* is recorded as a representation gap", plus an out-of-contract
justification table) to be the worst offender in the epic: they made the
failure optional provided someone wrote a sentence. Both escapes are withdrawn.

Because a withdrawn escape tends to grow back, this module does the opposite of
honoring one. :func:`load_effect_declarations` actively SCANS for
suppression-shaped keys and records them in ``ignored_suppression_keys``. They
are reported loudly and have no effect on any verdict. A silently ignored key
would be nearly as bad as an honored one -- an author could believe a gap was
waived. See ``references/architecture_tractability.md``, "No Degenerate
Escapes", rules 3 and 4, and ``references/modular_fuzzing.md`` oracle 3.

**NOTHING DOWNGRADES AN UNOBSERVABLE VERDICT EITHER.** MF-027 extends the same
rule to the observability edge, for the same reason: the tempting "helpful"
move is to let a user whose runtime the sandbox cannot support opt out of the
check, and that opt-out would reintroduce exactly the silence this ticket
removed. The observability-shaped keys in :data:`SUPPRESSION_KEYS` are scanned,
reported, and never honored, and :attr:`EffectConformanceReport.ok` consults no
configuration at all.
"""

from __future__ import annotations

import builtins
import fnmatch
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

#: Effect types the sandbox knows how to observe. A declaration naming a type
#: outside this set is rejected: an unobservable port is a declaration that can
#: never be checked, and an unchecked declaration is decoration.
EFFECT_TYPES = frozenset(
    {
        "filesystem.write",
        "filesystem.delete",
        "process.spawn",
        "network.connect",
        "network.http",
    }
)

#: Keys whose presence anywhere in an effects block indicates someone is trying
#: to reintroduce the withdrawn suppression escape. They are collected and
#: reported; they never change a verdict.
SUPPRESSION_KEYS = frozenset(
    {
        "justification",
        "justifications",
        "out_of_contract",
        "out_of_contract_justification",
        "suppress",
        "suppressed",
        "suppresses",
        "waiver",
        "waived",
        "accepted_gap",
        "accepted_gaps",
        "allow_undeclared",
        "ignore_undeclared",
        "expected_gap",
        # MF-027: the observability-shaped variants. A user whose runtime the
        # sandbox cannot observe will reach for one of these; they are scanned
        # and reported exactly like the gap-suppression keys, and honored
        # exactly as much -- not at all.
        "assume_observable",
        "assume_observed",
        "observable",
        "skip_observability",
        "skip_effect_conformance",
        "allow_unobservable",
        "ignore_unobservable",
        "unobservable_ok",
        "trusted_runtime",
        "external_runtime_ok",
    }
)

VERDICT_CLEAN = "clean"
VERDICT_GAPS = "gaps"
VERDICT_DEAD_SURFACE = "dead_surface"
#: MF-027: the sandbox could not observe the target at all. This DOMINATES the
#: other verdicts: a diff computed over a target that was never seen carries no
#: information, so reporting it as "clean" -- or even as "gaps" -- would assert
#: something the run has no evidence for.
VERDICT_UNOBSERVABLE = "unobservable"
#: HP-04: an adapter accepted a case and then raised. Ranked below
#: ``unobservable`` and above ``gaps`` for the same reason ``unobservable``
#: outranks both: a diff over a case that blew up mid-way is a statement about a
#: partial observation set.
VERDICT_ADAPTER_ERROR = "adapter_error"

#: Runtime identifiers the sandbox can actually observe. The sandbox patches
#: objects in this CPython interpreter, so this set has exactly one member in
#: spirit: code running in-process, here, now.
OBSERVABLE_RUNTIMES = frozenset({"python", "cpython", "in-process", "python:in-process"})

#: Substrings in an adapter reference, kind, or channel that prove the work
#: happens somewhere the sandbox's monkeypatches do not reach. Matching is
#: deliberately broad: a false "unobservable" costs a user an explicit
#: declaration, while a false "observable" costs them a green report on an
#: unchecked program, which is the failure mode this ticket exists to remove.
NON_PYTHON_RUNTIME_MARKERS = (
    "jvm",
    "java",
    "kotlin",
    "jbang",
    "gradle",
    "scala",
    "clojure",
    "node",
    "npx",
    "npm",
    "deno",
    "bun",
    "golang",
    "rust",
    "cargo",
    "dotnet",
    "ruby",
    "docker",
    "container",
    "podman",
    "kubectl",
    "ssh",
    "shell",
    "bash",
    "subprocess",
    "exec",
    "remote",
)


class EffectDeclarationError(ValueError):
    """The ``effects:`` block is malformed. A malformed gate is a failed gate."""


@dataclass(frozen=True)
class PortDeclaration:
    """One typed emission point owned by a component."""

    component: str
    port: str
    type: str
    target: str

    @property
    def qualified(self) -> str:
        return f"{self.component}.{self.port}"

    def matches(self, effect: "ObservedEffect") -> bool:
        if effect.type != self.type:
            return False
        return _target_matches(self.target, effect.target)


@dataclass(frozen=True)
class ObservedEffect:
    """One boundary crossing the sandbox actually saw."""

    type: str
    target: str
    action: str = ""
    case: str = ""
    detail: str = ""

    def describe(self) -> str:
        where = f" during {self.case}" if self.case else ""
        return f"{self.type} -> {self.target}{where}"


#: MF-027 finding kinds. ``runtime`` means the target itself runs outside this
#: interpreter; ``process-boundary`` means an observable target handed work to a
#: child process whose own effects were never seen.
UNOBSERVABLE_RUNTIME = "runtime"
UNOBSERVABLE_PROCESS_BOUNDARY = "process-boundary"

#: MF-033: every effect type a child process could emit across a spawn boundary.
#: The in-process sandbox observes NONE of them (its monkeypatches do not cross a
#: process boundary). An out-of-process observer discharges the subset it can
#: positively prove; whatever remains is the named unobservable residual. This is
#: exactly ``EFFECT_TYPES``: a child can write, delete, spawn again, and connect.
BOUNDARY_EFFECT_TYPES = frozenset(EFFECT_TYPES)


@dataclass(frozen=True)
class UnobservableTarget:
    """Something the sandbox could not see. Always a failure.

    This is the finding MF-013 was missing. Its absence is what let a JVM
    adapter and a subprocess-delegating adapter both return ``clean``: the
    sandbox observed nothing, nothing observed matched nothing declared, and
    an empty diff read as a passing one.
    """

    target: str
    reason: str
    kind: str = UNOBSERVABLE_RUNTIME
    detail: str = ""

    def describe(self) -> str:
        if self.kind == UNOBSERVABLE_PROCESS_BOUNDARY:
            head = f"UNOBSERVABLE BOUNDARY: process {self.target!r}"
        else:
            head = f"TARGET NOT OBSERVABLE: {self.target!r}"
        tail = f" [{self.detail}]" if self.detail else ""
        return f"{head} -- {self.reason}{tail}"


@dataclass(frozen=True)
class OutOfProcessObservation:
    """Positive evidence gathered by an observer that reaches ACROSS a boundary.

    MF-033. The in-process sandbox cannot see a child process's effects, so under
    MF-027/MF-028 a declared ``process.spawn`` produced :data:`VERDICT_UNOBSERVABLE`
    permanently: every adapter in this repository shells out, the sandbox saw the
    spawn but nothing the child did, and refused. This record carries what an
    *out-of-process* observer -- e.g. a working-tree snapshot diff -- actually
    measured for one bracketed execution window: which effect TYPES it positively
    covered, over which root, and how many effects it saw.

    It is evidence, never a downgrade. Two properties keep MF-027 polarity intact:

    * ``covered_types`` is a positive claim -- the observer watched those axes and
      can point at the files that changed. It is not a permission to assume; an
      observer that watched nothing carries an empty set and discharges nothing.
    * whatever a child could emit but this observer did not watch stays in the
      residual (see :func:`diff_effects`). Observing the filesystem does not
      certify the network. So an unobserved axis still refuses.
    """

    case: str
    action: str
    observer: str
    covered_types: frozenset[str]
    root: str = ""
    observed_count: int = 0


#: HP-04 skip reasons. ``not-runnable`` means the adapter has no case-driven
#: entry point at all (``apply()`` and no ``run(case, work_dir)``);
#: ``declined`` means the adapter has one and its own ``can_run``/``validate``
#: refused this particular case; ``unbound`` means the mapping binds no adapter
#: for the case's action.
SKIP_NOT_RUNNABLE = "not-runnable"
SKIP_DECLINED = "declined"
SKIP_UNBOUND = "unbound"
#: The adapter accepted the case and then RAISED. Unlike the three above this
#: one is a FAILURE and enters ``EffectConformanceReport.ok``. It is recorded
#: rather than allowed to propagate for the same reason as the others -- one bad
#: case used to hide every case after it -- but recording a failure is not the
#: same as forgiving one, and an adapter that blew up has told the run nothing
#: about the effects its action performs.
SKIP_ERROR = "error"


@dataclass(frozen=True)
class SkippedCase:
    """A case the runner did not execute, and why. A REPORT, never a refusal.

    RC-02-DF-03. Before HP-04 the oracle called ``call_adapter`` unconditionally
    and the first ``apply()``-only adapter raised ``TypeError``, killing the run
    with no report written -- so a corpus containing any analyze/run/close case
    produced nothing at all rather than a partial measurement.

    A skip is deliberately **not** a verdict input. The epic's
    ``no_new_gates_rule`` is explicit that skipping an adapter that cannot
    execute is a report, and adding it to :attr:`EffectConformanceReport.ok`
    would be shipping a new blocking check under the cover of a bug fix.

    It is equally deliberately **not silent**. MF-027's whole lesson is that an
    absence of observation must never read as a clean observation, so the skip
    count rides in :meth:`EffectConformanceReport.summary` beside the gap count,
    every skip is rendered with its reason, and a declared port whose every
    declaring action was skipped is annotated as unexercised rather than
    presented as proven dead surface.
    """

    case: str
    action: str
    adapter: str
    reason: str
    kind: str = SKIP_NOT_RUNNABLE

    def describe(self) -> str:
        adapter = self.adapter or "<unbound>"
        head = "ADAPTER ERROR" if self.kind == SKIP_ERROR else "SKIPPED"
        return (
            f"{head} [{self.kind}]: case {self.case} (action {self.action or '<unmapped>'}) "
            f"-- adapter {adapter}: {self.reason}"
        )


@dataclass(frozen=True)
class TargetObservability:
    """The verdict on whether one target can be observed in-process."""

    target: str
    observable: bool
    reason: str
    detail: str = ""

    def finding(self) -> UnobservableTarget | None:
        if self.observable:
            return None
        return UnobservableTarget(
            target=self.target,
            reason=self.reason,
            kind=UNOBSERVABLE_RUNTIME,
            detail=self.detail,
        )


def assess_target_observability(
    target: str,
    *,
    resolved: Any = None,
    runtime: str | None = None,
    kind: str | None = None,
    channel: str | None = None,
) -> TargetObservability:
    """Decide whether ``target`` is observable by the in-process sandbox.

    Observability is granted only on **positive evidence**, never assumed. The
    only evidence that counts is ``resolved``: a live Python object, imported
    into this interpreter, that the runner is about to call directly. If the
    runner cannot hand over such an object, the target's real work happens
    somewhere the monkeypatches do not reach, and the sandbox says so.

    This polarity is the whole point. Defaulting to "observable" and refusing
    only on recognised non-Python markers would mean every runtime nobody
    thought to enumerate silently reports clean -- the exact defect MF-027
    closes. Defaulting to "unobservable" means an unrecognised runtime costs
    its author an explicit refusal they can read and act on.
    """
    label = str(target)

    declared = (runtime or "").strip().lower()
    if declared and declared not in OBSERVABLE_RUNTIMES:
        return TargetObservability(
            target=label,
            observable=False,
            reason=(
                f"declared runtime {declared!r} is not the in-process CPython runtime; "
                "the sandbox patches only objects in this interpreter and no patch "
                "crosses a process boundary"
            ),
            detail=f"runtime={declared}",
        )

    for field_name, value in (("kind", kind), ("channel", channel), ("adapter", label)):
        marker = _non_python_marker(value)
        if marker is not None:
            return TargetObservability(
                target=label,
                observable=False,
                reason=(
                    f"{field_name} {value!r} names the out-of-process runtime {marker!r}; "
                    "the in-process sandbox cannot observe it"
                ),
                detail=f"{field_name}={value}",
            )

    if resolved is None:
        return TargetObservability(
            target=label,
            observable=False,
            reason=(
                "no in-process Python object was resolved for this target, so the "
                "sandbox has no evidence it can observe anything it does"
            ),
            detail="resolved=None",
        )

    if not _is_python_reference(label):
        return TargetObservability(
            target=label,
            observable=False,
            reason=(
                "target is not a Python 'module:object' reference, so it does not "
                "name code this interpreter runs"
            ),
            detail="reference-shape",
        )

    return TargetObservability(
        target=label,
        observable=True,
        reason="resolved to an in-process Python object in this interpreter",
        detail=f"module={getattr(resolved, '__module__', type(resolved).__module__)}",
    )


def _non_python_marker(value: Any) -> str | None:
    if not value:
        return None
    text = str(value).lower()
    for marker in NON_PYTHON_RUNTIME_MARKERS:
        if marker in text:
            return marker
    return None


def _is_python_reference(reference: str) -> bool:
    """True for a ``module.path:object`` reference and nothing else."""
    if ":" not in reference:
        return False
    module_part, _, object_part = reference.partition(":")
    if not module_part or not object_part:
        return False
    if any(char in reference for char in " \t/\\"):
        return False
    parts = module_part.split(".") + object_part.split(".")
    return all(part.isidentifier() for part in parts)


def _target_matches(pattern: str, target: str) -> bool:
    """Glob match with ``**`` spanning separators.

    ``fnmatch`` treats ``*`` as crossing ``/`` already, which is what we want
    for path patterns like ``**/specs/**``; the normalization here just makes
    ``**`` and ``*`` behave the same and keeps separators uniform.
    """
    normalized = target.replace(os.sep, "/")
    collapsed = pattern.replace(os.sep, "/").replace("**", "*")
    while "**" in collapsed:
        collapsed = collapsed.replace("**", "*")
    return fnmatch.fnmatch(normalized, collapsed)


@dataclass
class EffectDeclarations:
    """The declared effect surface: ports per component, ports per action."""

    ports: dict[str, PortDeclaration] = field(default_factory=dict)
    action_ports: dict[str, list[str]] = field(default_factory=dict)
    #: Suppression-shaped keys found while parsing. Recorded and reported;
    #: never consulted by any verdict. See the module docstring.
    ignored_suppression_keys: list[str] = field(default_factory=list)

    def declared_for_action(self, action: str) -> list[PortDeclaration]:
        return [self.ports[name] for name in self.action_ports.get(action, []) if name in self.ports]

    def all_qualified(self) -> list[str]:
        return sorted(decl.qualified for decl in self.ports.values())


def load_effect_declarations(data: Any) -> EffectDeclarations:
    """Parse an ``effects:`` block into declarations.

    Accepts either a whole manifest/actions mapping containing ``effects:`` or
    the effects block itself.
    """
    if data is None:
        return EffectDeclarations()
    if not isinstance(data, dict):
        raise EffectDeclarationError(f"effects block must be a mapping, got {type(data).__name__}")

    block = data.get("effects", data) if "effects" in data else data
    if block is None:
        return EffectDeclarations()
    if not isinstance(block, dict):
        raise EffectDeclarationError(f"effects block must be a mapping, got {type(block).__name__}")

    declarations = EffectDeclarations()
    declarations.ignored_suppression_keys = _scan_for_suppression(block, "effects")

    components = block.get("components") or {}
    if not isinstance(components, dict):
        raise EffectDeclarationError("effects.components must be a mapping of component -> ports")

    for component, spec in components.items():
        if not isinstance(spec, dict):
            raise EffectDeclarationError(f"effects.components.{component} must be a mapping")
        ports = spec.get("ports") or {}
        if not isinstance(ports, dict):
            raise EffectDeclarationError(f"effects.components.{component}.ports must be a mapping")
        for port, port_spec in ports.items():
            if not isinstance(port_spec, dict):
                raise EffectDeclarationError(f"port {component}.{port} must be a mapping")
            effect_type = port_spec.get("type")
            target = port_spec.get("target")
            # No "when present" conditionals: a port that does not say what it
            # emits, or where, cannot be checked against anything.
            if not effect_type:
                raise EffectDeclarationError(f"port {component}.{port} declares no type")
            if effect_type not in EFFECT_TYPES:
                raise EffectDeclarationError(
                    f"port {component}.{port} declares unobservable type {effect_type!r}; "
                    f"known types: {', '.join(sorted(EFFECT_TYPES))}"
                )
            if not target:
                raise EffectDeclarationError(f"port {component}.{port} declares no target pattern")
            if port in declarations.ports:
                raise EffectDeclarationError(f"duplicate port name {port!r}")
            declarations.ports[port] = PortDeclaration(
                component=str(component), port=str(port), type=str(effect_type), target=str(target)
            )

    actions = block.get("actions") or {}
    if not isinstance(actions, dict):
        raise EffectDeclarationError("effects.actions must be a mapping of action -> [port]")
    for action, port_names in actions.items():
        if port_names is None:
            port_names = []
        if isinstance(port_names, str):
            port_names = [port_names]
        if not isinstance(port_names, list):
            raise EffectDeclarationError(f"effects.actions.{action} must be a list of port names")
        for name in port_names:
            if name not in declarations.ports:
                raise EffectDeclarationError(
                    f"action {action} declares unknown port {name!r}; declare it under effects.components"
                )
        declarations.action_ports[str(action)] = [str(name) for name in port_names]

    return declarations


def _scan_for_suppression(node: Any, path: str) -> list[str]:
    """Find suppression-shaped keys so they can be reported, never honored."""
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            child = f"{path}.{key}"
            if isinstance(key, str) and key.lower() in SUPPRESSION_KEYS:
                found.append(child)
            found.extend(_scan_for_suppression(value, child))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            found.extend(_scan_for_suppression(value, f"{path}[{index}]"))
    return found


@dataclass
class RecordingTransport:
    """A fake transport that records every send instead of performing one."""

    name: str
    recorder: "EffectRecorder"

    def send(self, target: str, payload: Any = None) -> None:
        self.recorder.record(
            ObservedEffect(type="network.http", target=str(target), detail=f"transport {self.name}")
        )

    def connect(self, target: str) -> None:
        self.recorder.record(
            ObservedEffect(type="network.connect", target=str(target), detail=f"transport {self.name}")
        )


@dataclass
class EffectRecorder:
    """Collects observed effects. Passive: adapters do not call into this."""

    effects: list[ObservedEffect] = field(default_factory=list)
    current_action: str = ""
    current_case: str = ""
    #: MF-027: targets the sandbox was asked to observe and could not. Kept
    #: beside the effects because they are the same kind of fact -- what the
    #: run actually saw -- and because a diff that ignored them would be a
    #: diff over an unknown population.
    unobservable: list[UnobservableTarget] = field(default_factory=list)
    #: MF-033: positive evidence from out-of-process observers (working-tree
    #: snapshot diffs). Each entry names the axes an observer covered for a
    #: bracketed window. Like ``unobservable``, this is a fact the run gathered;
    #: there is deliberately no method to withdraw one, because it is evidence,
    #: not a flag.
    out_of_process: list["OutOfProcessObservation"] = field(default_factory=list)
    #: HP-04 (RC-02-DF-03): cases the runner could not execute, with the reason.
    #: Like ``unobservable`` this is a fact the run gathered and there is no
    #: method to withdraw one -- but unlike it, a skip changes no verdict.
    skipped: list["SkippedCase"] = field(default_factory=list)

    def record_unobservable(self, finding: UnobservableTarget) -> None:
        """Record a refusal. There is no matching ``clear``/``waive`` method."""
        if finding not in self.unobservable:
            self.unobservable.append(finding)

    def record_skip(self, skip: "SkippedCase") -> None:
        """Record a case the runner did not execute. No ``clear``/``waive``."""
        self.skipped.append(skip)

    def record_out_of_process(self, observation: "OutOfProcessObservation") -> None:
        """Record what an out-of-process observer proved. No ``clear``/``waive``."""
        self.out_of_process.append(observation)

    def record(self, effect: ObservedEffect) -> None:
        self.effects.append(
            ObservedEffect(
                type=effect.type,
                target=effect.target,
                action=effect.action or self.current_action,
                case=effect.case or self.current_case,
                detail=effect.detail,
            )
        )

    def for_case(self, case: str) -> list[ObservedEffect]:
        return [effect for effect in self.effects if effect.case == case]


_WRITE_MODES = frozenset("wax+")


class EffectSandbox:
    """Execute adapter code with real boundaries patched and recorded.

    Used as a context manager. Patches are installed process-wide for the
    duration and removed in ``__exit__`` even on error. The sandbox root is a
    caller-supplied temp dir; effects are recorded whether or not they land
    inside it, so escaping the sandbox is itself observable.
    """

    def __init__(self, root: Path, recorder: EffectRecorder | None = None) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.recorder = recorder if recorder is not None else EffectRecorder()
        self._originals: dict[str, Any] = {}

    # -- observability --------------------------------------------------
    def require_observable(
        self,
        target: str,
        *,
        resolved: Any = None,
        runtime: str | None = None,
        kind: str | None = None,
        channel: str | None = None,
    ) -> TargetObservability:
        """Assess ``target`` and record a refusal when it cannot be observed.

        Runners call this **before** executing an adapter. The return value is
        informational -- callers may skip work they know will not be seen --
        but the finding is already recorded either way, so declining to check
        the return value cannot produce a clean report. Refusal is recorded at
        the sandbox, not decided at the call site.
        """
        assessment = assess_target_observability(
            target, resolved=resolved, runtime=runtime, kind=kind, channel=channel
        )
        finding = assessment.finding()
        if finding is not None:
            self.recorder.record_unobservable(finding)
        return assessment

    # -- transports -----------------------------------------------------
    def transport(self, name: str) -> RecordingTransport:
        """A fake transport handed to adapters in place of a real one."""
        return RecordingTransport(name=name, recorder=self.recorder)

    def temp_dir(self, name: str) -> Path:
        path = self.root / name
        path.mkdir(parents=True, exist_ok=True)
        return path

    # -- lifecycle ------------------------------------------------------
    def __enter__(self) -> "EffectSandbox":
        self._install()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self._restore()

    def observe(self, action: str = "", case: str = "") -> "_ObservationScope":
        return _ObservationScope(self, action=action, case=case)

    # -- patching -------------------------------------------------------
    def _install(self) -> None:
        recorder = self.recorder

        def _record(effect_type: str, target: Any, detail: str = "") -> None:
            recorder.record(ObservedEffect(type=effect_type, target=str(target), detail=detail))

        self._originals["open"] = builtins.open
        real_open = builtins.open

        def patched_open(file: Any, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
            if any(char in _WRITE_MODES for char in mode):
                _record("filesystem.write", _abspath(file), "open")
            return real_open(file, mode, *args, **kwargs)

        builtins.open = patched_open

        self._patch_module(os, "remove", "filesystem.delete", 0)
        self._patch_module(os, "unlink", "filesystem.delete", 0)
        self._patch_module(os, "rmdir", "filesystem.delete", 0)
        self._patch_module(os, "mkdir", "filesystem.write", 0)
        self._patch_module(os, "makedirs", "filesystem.write", 0)
        self._patch_module(shutil, "rmtree", "filesystem.delete", 0)
        self._patch_module(shutil, "copyfile", "filesystem.write", 1)
        self._patch_module(shutil, "copy", "filesystem.write", 1)
        self._patch_module(shutil, "copy2", "filesystem.write", 1)
        self._patch_module(shutil, "move", "filesystem.write", 1)

        self._patch_path_method("write_text", "filesystem.write")
        self._patch_path_method("write_bytes", "filesystem.write")
        # HP-04: `Path.open` was NOT patched, so `path.open("a")` -- the
        # idiomatic way to append to a durable file -- crossed the boundary
        # unobserved while `builtins.open(path, "a")` was recorded. Found by
        # running the oracle over HP-01's A/B reference: the ordering mutant M09
        # replaces a `Path.open("a")` append with `Path.write_text`, and the
        # oracle "killed" it purely because the mutation swapped an INVISIBLE
        # write for a visible one. An oracle whose observation depends on which
        # of two equivalent APIs the program picked reports a fact about the
        # program's style, and the failure direction is the bad one: the more
        # common idiom was the silent one.
        self._patch_path_open()
        self._patch_path_method("mkdir", "filesystem.write")
        self._patch_path_method("unlink", "filesystem.delete")
        self._patch_path_method("rmdir", "filesystem.delete")

        self._patch_process("run")
        self._patch_process("call")
        self._patch_process("check_call")
        self._patch_process("check_output")
        self._patch_popen()
        self._patch_socket()

    def _patch_module(self, module: Any, name: str, effect_type: str, arg_index: int) -> None:
        original = getattr(module, name, None)
        if original is None:
            return
        key = f"{module.__name__}.{name}"
        self._originals[key] = (module, name, original)
        recorder = self.recorder

        def patched(*args: Any, **kwargs: Any) -> Any:
            if len(args) > arg_index:
                recorder.record(
                    ObservedEffect(type=effect_type, target=str(_abspath(args[arg_index])), detail=key)
                )
            return original(*args, **kwargs)

        setattr(module, name, patched)

    def _patch_path_method(self, name: str, effect_type: str) -> None:
        original = getattr(Path, name, None)
        if original is None:
            return
        key = f"Path.{name}"
        self._originals[key] = (Path, name, original)
        recorder = self.recorder

        def patched(self_path: Path, *args: Any, **kwargs: Any) -> Any:
            recorder.record(ObservedEffect(type=effect_type, target=str(_abspath(self_path)), detail=key))
            return original(self_path, *args, **kwargs)

        setattr(Path, name, patched)

    def _patch_path_open(self) -> None:
        """Record ``Path.open`` in a write mode, like ``builtins.open``.

        Same mode test as the ``builtins.open`` patch, so the two idioms are
        observed identically -- which is the whole point of adding it.
        """
        original = getattr(Path, "open", None)
        if original is None:  # pragma: no cover - defensive
            return
        self._originals["Path.open"] = (Path, "open", original)
        recorder = self.recorder

        def patched(self_path: Path, mode: str = "r", *args: Any, **kwargs: Any) -> Any:
            if any(char in _WRITE_MODES for char in mode):
                recorder.record(
                    ObservedEffect(
                        type="filesystem.write", target=str(_abspath(self_path)), detail="Path.open"
                    )
                )
            return original(self_path, mode, *args, **kwargs)

        setattr(Path, "open", patched)

    def _patch_process(self, name: str) -> None:
        original = getattr(subprocess, name, None)
        if original is None:
            return
        key = f"subprocess.{name}"
        self._originals[key] = (subprocess, name, original)
        recorder = self.recorder

        def patched(*args: Any, **kwargs: Any) -> Any:
            if args:
                recorder.record(
                    ObservedEffect(type="process.spawn", target=_command_target(args[0]), detail=key)
                )
            return original(*args, **kwargs)

        setattr(subprocess, name, patched)

    def _patch_popen(self) -> None:
        original = subprocess.Popen
        self._originals["subprocess.Popen"] = (subprocess, "Popen", original)
        recorder = self.recorder

        class PatchedPopen(original):  # type: ignore[misc,valid-type]
            def __init__(self, args: Any = None, *rest: Any, **kwargs: Any) -> None:
                recorder.record(
                    ObservedEffect(type="process.spawn", target=_command_target(args), detail="subprocess.Popen")
                )
                super().__init__(args, *rest, **kwargs)

        subprocess.Popen = PatchedPopen  # type: ignore[misc]

    def _patch_socket(self) -> None:
        try:
            import socket
        except ImportError:  # pragma: no cover
            return
        original = socket.socket.connect
        self._originals["socket.connect"] = (socket.socket, "connect", original)
        recorder = self.recorder

        def patched(self_sock: Any, address: Any) -> Any:
            recorder.record(
                ObservedEffect(type="network.connect", target=_address_target(address), detail="socket.connect")
            )
            return original(self_sock, address)

        socket.socket.connect = patched  # type: ignore[assignment]

    def _restore(self) -> None:
        if "open" in self._originals:
            builtins.open = self._originals.pop("open")
        for key, entry in list(self._originals.items()):
            if isinstance(entry, tuple) and len(entry) == 3:
                target, name, original = entry
                setattr(target, name, original)
            self._originals.pop(key, None)


class WorkingTreeObserver:
    """Out-of-process filesystem observation via a working-tree snapshot diff.

    MF-033. :class:`EffectSandbox` monkeypatches *this* interpreter, so a child
    process's filesystem effects are invisible to it (MF-028: every adapter in
    this repository shells out, so the sandbox saw the spawn and nothing else).
    This observer sees them a different way, and one that does not depend on the
    child's runtime at all: it snapshots one or more working-tree roots *before*
    an execution window and diffs them *after*. A file that appeared or changed
    is a ``filesystem.write``; a file that vanished is a ``filesystem.delete``.
    That is positive evidence of what the child actually did to the filesystem,
    gathered from OUTSIDE any process boundary -- it works the same whether the
    child was Python, java (TLC), or pytest.

    **It covers the filesystem axis, and says so.** A child's network
    connections and its own nested spawns leave no working-tree trace, so this
    observer does not claim them: :attr:`covered_types` is exactly
    ``{filesystem.write, filesystem.delete}``. Everything else a child could do
    stays the named unobservable residual (:func:`diff_effects`). Coverage is a
    positive property of what the observer measured, never an assertion of
    absence -- observing the filesystem does not certify the network, and this
    class offers no way to pretend otherwise. That is how MF-027 polarity
    survives the added observability: more is seen, but nothing unseen is waved
    through.

    Used as a context manager around the adapter call whose child you want to
    observe. The recorded effects and the :class:`OutOfProcessObservation`
    coverage record both land on the supplied recorder.
    """

    covered_types = frozenset({"filesystem.write", "filesystem.delete"})

    def __init__(
        self,
        roots: Iterable[Path] | Path,
        recorder: EffectRecorder,
        *,
        action: str = "",
        case: str = "",
        observer: str = "working-tree-diff",
    ) -> None:
        if isinstance(roots, (str, Path)):
            roots = [roots]
        self.roots = [Path(root) for root in roots]
        self.recorder = recorder
        self.action = action
        self.case = case
        self.observer = observer
        self._before: dict[str, tuple[int, int]] = {}

    def __enter__(self) -> "WorkingTreeObserver":
        self._before = self._snapshot()
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        # Record even on error: a child that wrote and then failed still wrote,
        # and hiding those effects would be exactly the blindness this removes.
        self._diff_and_record()

    def _snapshot(self) -> dict[str, tuple[int, int]]:
        """Map every existing file under the roots to (size, mtime_ns).

        Directories are not effects on their own -- a ``filesystem.write`` is a
        file crossing the boundary -- so only files are tracked. mtime is kept
        alongside size so that an in-place overwrite of identical length still
        reads as a write.
        """
        snapshot: dict[str, tuple[int, int]] = {}
        for root in self.roots:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                try:
                    if not path.is_file():
                        continue
                    stat = path.stat()
                except OSError:
                    continue
                snapshot[str(_abspath(path))] = (stat.st_size, stat.st_mtime_ns)
        return snapshot

    def _diff_and_record(self) -> None:
        after = self._snapshot()
        writes = 0
        deletes = 0
        for target, meta in sorted(after.items()):
            if target not in self._before or self._before[target] != meta:
                self._record(target, "filesystem.write")
                writes += 1
        for target in sorted(self._before):
            if target not in after:
                self._record(target, "filesystem.delete")
                deletes += 1
        self.recorder.record_out_of_process(
            OutOfProcessObservation(
                case=self.case,
                action=self.action,
                observer=self.observer,
                covered_types=self.covered_types,
                root=", ".join(str(root) for root in self.roots),
                observed_count=writes + deletes,
            )
        )

    def _record(self, target: str, effect_type: str) -> None:
        self.recorder.record(
            ObservedEffect(
                type=effect_type,
                target=target,
                action=self.action,
                case=self.case,
                detail=f"out-of-process:{self.observer}",
            )
        )


class _ObservationScope:
    """Tags every effect recorded inside the ``with`` body with a case/action."""

    def __init__(self, sandbox: EffectSandbox, action: str, case: str) -> None:
        self._recorder = sandbox.recorder
        self._action = action
        self._case = case
        self._saved: tuple[str, str] = ("", "")

    def __enter__(self) -> EffectRecorder:
        self._saved = (self._recorder.current_action, self._recorder.current_case)
        self._recorder.current_action = self._action
        self._recorder.current_case = self._case
        return self._recorder

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self._recorder.current_action, self._recorder.current_case = self._saved


def _abspath(value: Any) -> str:
    try:
        return str(Path(os.fspath(value)).resolve())
    except (TypeError, ValueError, OSError):
        return str(value)


def _command_target(command: Any) -> str:
    if command is None:
        return ""
    if isinstance(command, (list, tuple)):
        return " ".join(str(part) for part in command)
    return str(command)


def _address_target(address: Any) -> str:
    if isinstance(address, tuple) and len(address) >= 2:
        return f"{address[0]}:{address[1]}"
    return str(address)


@dataclass
class EffectGap:
    """An observed effect with no declared port. Always a failure."""

    effect: ObservedEffect

    def describe(self) -> str:
        return (
            f"UNDECLARED EFFECT: {self.effect.describe()} "
            f"(action {self.effect.action or '<unmapped>'}) -- no declared port accepts it"
        )


@dataclass
class DeadSurface:
    """A declared port no case ever exercised. Always a failure.

    HP-04 adds :attr:`blocked_by`: the actions that declare this port and whose
    cases the run SKIPPED (see :class:`SkippedCase`). The verdict is unchanged
    -- an unexercised port still fails -- but the message is, because "declared
    but never observed" and "declared, and every action that could have
    exercised it was skipped" are different claims and only the first is
    evidence that the surface is dead. Nine of this model's seventeen adapters
    are ``apply()``-only, so before this annotation the oracle's dead-port list
    silently mixed proven dead surface with ports nothing had ever been in a
    position to exercise.
    """

    port: PortDeclaration
    #: Actions declaring this port whose cases were all skipped, if any.
    blocked_by: tuple[str, ...] = ()

    def describe(self) -> str:
        if self.blocked_by:
            return (
                f"UNEXERCISED PORT (NOT proven dead): port {self.port.qualified} "
                f"({self.port.type} -> {self.port.target}) -- every action declaring it "
                f"was SKIPPED by this run: {', '.join(self.blocked_by)}. "
                "This is an absence of evidence, not evidence of absence."
            )
        return (
            f"DEAD MODEL SURFACE: port {self.port.qualified} "
            f"({self.port.type} -> {self.port.target}) declared but never observed"
        )


@dataclass
class EffectConformanceReport:
    """The diff. ``ok`` is the gate; there is no path to ok=True with findings."""

    gaps: list[EffectGap] = field(default_factory=list)
    dead_surface: list[DeadSurface] = field(default_factory=list)
    observed: list[ObservedEffect] = field(default_factory=list)
    declared: list[str] = field(default_factory=list)
    cases: list[str] = field(default_factory=list)
    ignored_suppression_keys: list[str] = field(default_factory=list)
    #: MF-027: targets the run could not observe. Non-empty => the run FAILS.
    unobservable: list[UnobservableTarget] = field(default_factory=list)
    #: MF-033: what out-of-process observers positively measured. This is
    #: evidence, reported so the reader can see WHICH child effects were
    #: recovered across a boundary and on which axes; it never enters ``ok``.
    out_of_process: list[OutOfProcessObservation] = field(default_factory=list)
    #: HP-04 (RC-02-DF-03): the cases this run did not execute, with reasons.
    #: Reported, never a verdict input -- see :class:`SkippedCase`.
    skipped: list[SkippedCase] = field(default_factory=list)
    #: HP-04: the modeled actions the corpus offered, whether or not their
    #: adapters could run. ``executed`` + ``skipped`` action names partition it,
    #: which is what makes "the oracle sees N of M actions" a statement anyone
    #: can check against the run instead of against the source.
    offered_actions: list[str] = field(default_factory=list)
    executed_actions: list[str] = field(default_factory=list)
    #: HP-04 (MF026-R4-F-01): the work directory this run used and whether each
    #: case started from an empty one. A run whose scratch persisted is a run
    #: whose numbers depend on what ran before it.
    work_dir: str = ""
    work_dir_reset: bool = False

    @property
    def skipped_actions(self) -> list[str]:
        executed = set(self.executed_actions)
        return sorted({skip.action for skip in self.skipped if skip.action and skip.action not in executed})

    @property
    def errored(self) -> list[SkippedCase]:
        """Cases whose adapter accepted them and then RAISED. A failure."""
        return [skip for skip in self.skipped if skip.kind == SKIP_ERROR]

    @property
    def ok(self) -> bool:
        # Note the shape: no flag, no manifest entry, and no justification is
        # consulted here. Findings exist => the run fails. This property is the
        # gate the 2026-07-18 audit required, and inverting it is the escape it
        # withdrew.
        #
        # MF-027 adds `unobservable` to the same conjunction rather than
        # beside it, so there is no second code path that could be relaxed
        # independently. An unobservable target is not a caveat attached to a
        # pass; it is a failure.
        #
        # HP-04 deliberately does NOT add `skipped` here. The epic's
        # no_new_gates_rule says skipping an adapter that cannot execute is a
        # report, never a refusal, and a bug-fix ticket that quietly turned the
        # 9 apply()-only adapters in this repository's own model into a hard
        # failure would have shipped a new blocking check under cover. The skip
        # is instead impossible to miss: it is in `summary()`, in `render()`,
        # and it annotates every dead-port finding it could have caused.
        #
        # An adapter that RAISED is the one exception, and it is not a new gate:
        # before HP-04 that exception propagated and killed the whole command,
        # so the run already failed. Collecting it lets the remaining cases run
        # and be reported; it does not forgive it.
        return not self.gaps and not self.dead_surface and not self.unobservable and not self.errored

    @property
    def verdict(self) -> str:
        """Maps onto the TLA ``effect_conformance`` variable.

        ``unobservable`` is tested FIRST and deliberately outranks the others.
        When the sandbox could not see a target, the gap and dead-surface
        counts are statements about an empty or partial observation set, and
        promoting either of them to the headline would dress an absence of
        evidence as a measurement.
        """
        if self.unobservable:
            return VERDICT_UNOBSERVABLE
        if self.errored:
            return VERDICT_ADAPTER_ERROR
        if self.gaps:
            return VERDICT_GAPS
        if self.dead_surface:
            return VERDICT_DEAD_SURFACE
        return VERDICT_CLEAN

    def summary(self) -> str:
        # HP-04: the skip count is APPENDED to the historical summary rather
        # than folded into it. A reader comparing this line with a pre-HP-04
        # report should see the same leading counts plus one new fact, not a
        # reshuffled sentence they have to re-parse.
        head = (
            f"effect conformance {self.verdict}: {len(self.observed)} observed effect(s) over "
            f"{len(self.cases)} case(s), {len(self.declared)} declared port(s), "
            f"{len(self.gaps)} gap(s), {len(self.dead_surface)} dead port(s), "
            f"{len(self.unobservable)} unobservable target(s)"
        )
        errored = self.errored
        if self.skipped or self.offered_actions:
            head += f", {len(self.skipped) - len(errored)} skipped case(s)"
        if errored:
            head += f", {len(errored)} ADAPTER ERROR(S)"
        return head

    def action_reach(self) -> str:
        """One line answering "how many actions can this oracle actually see?".

        The question RC-02-DF-03 left open, answered by the run instead of by
        counting ``hasattr(cls, "run")`` over the mapping by hand.
        """
        executed = sorted(set(self.executed_actions))
        skipped = self.skipped_actions
        offered = sorted(set(self.offered_actions) | set(executed) | set(skipped))
        errored = sorted({skip.action for skip in self.errored if skip.action})
        line = (
            f"ADAPTER REACH: {len(executed)} of {len(offered)} action(s) in this corpus DRIVEN; "
            f"{len(skipped)} SKIPPED. Driven: {', '.join(executed) or '(none)'}. "
            f"Skipped: {', '.join(skipped) or '(none)'}."
        )
        if errored:
            # "Driven" is not "measured": an adapter that raised was called and
            # told the run nothing, so naming these separately is the difference
            # between reach and evidence.
            line += (
                f" Of the driven, {len(errored)} RAISED on at least one case and are "
                f"measured by nothing: {', '.join(errored)}."
            )
        return line

    def render(self) -> str:
        lines = [self.summary()]
        if self.work_dir:
            lines.append(
                f"work dir: {self.work_dir} "
                + (
                    "(each case started from an EMPTY directory, so two runs over an "
                    "identical corpus report identical counts -- MF026-R4-F-01)"
                    if self.work_dir_reset
                    else "(NOT reset per case: results may depend on what ran before)"
                )
            )
        if self.skipped or self.offered_actions:
            lines.append(self.action_reach())
        errored = self.errored
        if errored:
            lines.append("")
            lines.append(
                "ADAPTER ERRORS -- these adapters accepted their case and then RAISED. "
                "This is a FAILURE, not a skip: the run reports every case instead of "
                "dying on the first, and reports nothing about what these actions do:"
            )
            lines.extend(f"  - {skip.describe()}" for skip in errored)
        reported = [skip for skip in self.skipped if skip.kind != SKIP_ERROR]
        if reported:
            lines.append("")
            lines.append(
                "SKIPPED CASES -- reported, never a refusal (no_new_gates_rule). The "
                "oracle certifies NOTHING about the actions below; their ports are "
                "unexercised by this run rather than proven dead:"
            )
            lines.extend(f"  - {skip.describe()}" for skip in reported)
        if self.out_of_process:
            observed = sum(obs.observed_count for obs in self.out_of_process)
            axes = sorted({t for obs in self.out_of_process for t in obs.covered_types})
            lines.append("")
            lines.append(
                f"OUT-OF-PROCESS OBSERVATION: {len(self.out_of_process)} window(s) reached "
                f"across a process boundary and recovered {observed} child effect(s) on axes "
                f"{', '.join(axes)}. These were diffed against the declared ports like any "
                "other observation; the axes NOT listed here stayed unobservable (MF-027)."
            )
        if self.ignored_suppression_keys:
            lines.append("")
            lines.append(
                "IGNORED SUPPRESSION ATTEMPT(S) -- these keys were found in the effects "
                "block and had NO effect on the verdict. Out-of-contract justifications "
                "were withdrawn 2026-07-18; nothing suppresses a gap report:"
            )
            lines.extend(f"  - {key}" for key in self.ignored_suppression_keys)
        if self.unobservable:
            lines.append("")
            lines.append(
                "REFUSED -- the sandbox could not observe the target(s) below. This "
                "report certifies NOTHING about them. The effect oracle observes the "
                "in-process CPython runtime only; it does not cross a process boundary."
            )
            for finding in self.unobservable:
                lines.append(f"  - {finding.describe()}")
        for gap in self.gaps:
            lines.append(f"  - {gap.describe()}")
        for dead in self.dead_surface:
            lines.append(f"  - {dead.describe()}")
        if self.unobservable:
            lines.append("")
            lines.append(
                "Run the target in-process as a Python adapter, or accept that this "
                "oracle does not cover it and check that boundary another way. There "
                "is no flag, annotation, or manifest entry that turns this into a "
                "pass -- see references/modular_fuzzing.md, oracle 3."
            )
        elif not self.ok:
            lines.append("")
            lines.append(
                "Model the effect (declare the port), or change the program so it no "
                "longer emits it. Remove the dead port, or add a case that exercises "
                "it. There is no third option."
            )
        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "ok": self.ok,
            "summary": self.summary(),
            "cases": list(self.cases),
            "declared_ports": list(self.declared),
            "observed_effects": [
                {
                    "type": effect.type,
                    "target": effect.target,
                    "action": effect.action,
                    "case": effect.case,
                    "detail": effect.detail,
                }
                for effect in self.observed
            ],
            "gaps": [
                {
                    "type": gap.effect.type,
                    "target": gap.effect.target,
                    "action": gap.effect.action,
                    "case": gap.effect.case,
                    "message": gap.describe(),
                }
                for gap in self.gaps
            ],
            "dead_surface": [
                {
                    "port": dead.port.qualified,
                    "type": dead.port.type,
                    "target": dead.port.target,
                    "blocked_by_skipped_actions": list(dead.blocked_by),
                    "proven_dead": not dead.blocked_by,
                }
                for dead in self.dead_surface
            ],
            "skipped_cases": [
                {
                    "case": skip.case,
                    "action": skip.action,
                    "adapter": skip.adapter,
                    "kind": skip.kind,
                    "reason": skip.reason,
                    "message": skip.describe(),
                }
                for skip in self.skipped
            ],
            "action_reach": {
                "offered": sorted(set(self.offered_actions) | set(self.executed_actions) | set(self.skipped_actions)),
                "executed": sorted(set(self.executed_actions)),
                "skipped": self.skipped_actions,
                "summary": self.action_reach(),
            },
            "determinism": {
                "work_dir": self.work_dir,
                "work_dir_reset_per_case": self.work_dir_reset,
                "note": (
                    "MF026-R4-F-01: the gap count was 20/15/14 across three runs of an "
                    "identical corpus because this directory persisted between runs. Each "
                    "case now starts from an empty one."
                ),
            },
            "adapter_errors": [
                {
                    "case": skip.case,
                    "action": skip.action,
                    "adapter": skip.adapter,
                    "reason": skip.reason,
                }
                for skip in self.errored
            ],
            "skip_policy": (
                "HP-04: a case whose adapter cannot execute it is SKIPPED AND REPORTED and "
                "never aborts the run, and the skip enters no verdict -- the epic's "
                "no_new_gates_rule. It is also never silent: it is in the summary line, in "
                "the rendered report, and it annotates every dead-port finding it caused"
            ),
            "unobservable_targets": [
                {
                    "target": finding.target,
                    "reason": finding.reason,
                    "kind": finding.kind,
                    "detail": finding.detail,
                    "message": finding.describe(),
                }
                for finding in self.unobservable
            ],
            "out_of_process_observations": [
                {
                    "case": obs.case,
                    "action": obs.action,
                    "observer": obs.observer,
                    "covered_types": sorted(obs.covered_types),
                    "root": obs.root,
                    "observed_count": obs.observed_count,
                }
                for obs in self.out_of_process
            ],
            "observable_scope": (
                "in-process CPython only: builtins.open, os/shutil/pathlib mutators, "
                "subprocess spawns and socket.connect patched in THIS interpreter. No "
                "patch crosses a process boundary; JVM, JBang/uv node, and child-process "
                "work is not observed (MF-027)"
            ),
            "ignored_suppression_keys": list(self.ignored_suppression_keys),
            "suppression_policy": (
                "withdrawn 2026-07-18: no justification, annotation, or manifest entry "
                "suppresses a gap report. MF-027: the same holds for an unobservable "
                "target -- no configuration downgrades that verdict to a pass"
            ),
        }

    def write(self, path: Path) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path


def diff_effects(
    declarations: EffectDeclarations,
    observed: Iterable[ObservedEffect],
    *,
    cases: Iterable[str] = (),
    case_actions: dict[str, str] | None = None,
    unobservable: Iterable[UnobservableTarget] = (),
    out_of_process: Iterable[OutOfProcessObservation] = (),
    skipped: Iterable[SkippedCase] = (),
    offered_actions: Iterable[str] = (),
    executed_actions: Iterable[str] = (),
    work_dir: str = "",
    work_dir_reset: bool = False,
) -> EffectConformanceReport:
    """Diff observed effects against declared ports.

    Per case: every observed effect must match a port declared for that case's
    action. Across the corpus: every declared port must have matched at least
    one observed effect.

    MF-027: ``unobservable`` carries the sandbox's refusals into the report,
    and every observed ``process.spawn`` additionally produces a
    process-boundary finding here. The second half is the important one: a
    spawn that MATCHES a declared port is still a boundary the sandbox cannot
    see through. Declaring ``tlc_process`` says "I spawn java"; it does not
    say what java then wrote. Treating a declared spawn as fully accounted for
    is precisely the silence MF-027 removes, so the finding is derived from the
    observation itself and no declaration suppresses it.

    MF-033: ``out_of_process`` carries positive evidence from observers that
    reach across the boundary the in-process sandbox cannot (e.g. a
    :class:`WorkingTreeObserver` snapshot diff). For a spawn whose case an
    out-of-process observer bracketed, the axes that observer PROVED it covered
    are discharged -- their effects are already in ``observed`` and diffed like
    any other -- and the process-boundary finding is narrowed to name only the
    axes that still have no observer. This is not a suppression path: coverage is
    a positive measurement, an unwatched axis (network, nested spawn) stays in
    the residual, and a spawn with no out-of-process evidence at all is
    unchanged -- still fully unobservable. Only a spawn every one of whose axes
    was positively observed is fully accounted for, which a filesystem-only
    observer never is. Polarity is preserved: more is seen, nothing unseen is
    waved through.
    """
    observed_list = list(observed)
    case_actions = case_actions or {}
    out_of_process_list = list(out_of_process)
    skipped_list = list(skipped)
    report = EffectConformanceReport(
        observed=observed_list,
        declared=declarations.all_qualified(),
        cases=list(cases),
        ignored_suppression_keys=list(declarations.ignored_suppression_keys),
        unobservable=list(unobservable),
        out_of_process=out_of_process_list,
        skipped=skipped_list,
        offered_actions=list(offered_actions),
        executed_actions=list(executed_actions),
        work_dir=work_dir,
        work_dir_reset=work_dir_reset,
    )

    # MF-033: per-case union of the axes an out-of-process observer positively
    # covered. Empty for every existing caller, so their spawns keep the full
    # (unnarrowed) finding below -- the MF-027 default.
    coverage_by_case: dict[str, set[str]] = {}
    for observation in out_of_process_list:
        coverage_by_case.setdefault(observation.case, set()).update(observation.covered_types)

    for effect in observed_list:
        if effect.type != "process.spawn":
            continue
        covered = coverage_by_case.get(effect.case, set())
        residual = sorted(BOUNDARY_EFFECT_TYPES - covered)
        if not residual:
            # Every axis a child could emit on was positively observed by some
            # out-of-process observer. There is nothing left the run cannot see,
            # so the boundary is fully accounted for and no finding is raised.
            continue
        if covered:
            reason = (
                "a child process was spawned; its "
                f"{', '.join(sorted(covered))} effects were observed out-of-process "
                f"(working-tree diff), but its {', '.join(residual)} effects have no "
                "observer and remain invisible to this run"
            )
        else:
            reason = (
                "a child process was spawned; the sandbox records the spawn but "
                "observes nothing the child does -- its writes, deletes and "
                "connections are invisible to this run"
            )
        finding = UnobservableTarget(
            target=effect.target,
            reason=reason,
            kind=UNOBSERVABLE_PROCESS_BOUNDARY,
            detail=f"case={effect.case or '<none>'} action={effect.action or '<unmapped>'}",
        )
        if finding not in report.unobservable:
            report.unobservable.append(finding)

    exercised: set[str] = set()
    seen_gaps: set[tuple[str, str, str, str]] = set()
    for effect in observed_list:
        action = effect.action or case_actions.get(effect.case, "")
        candidates = declarations.declared_for_action(action)
        matched = [decl for decl in candidates if decl.matches(effect)]
        if matched:
            exercised.update(decl.port for decl in matched)
            continue
        # One boundary crossing can trip several patches at once (Path.mkdir
        # calls os.mkdir; shutil.copy calls open). Collapsing identical
        # (type, target, action, case) gaps reports each CROSSING once instead
        # of once per interception layer.
        #
        # This is not evidence removal: every raw observation is retained in
        # `report.observed`, no distinct crossing is dropped, and the collapse
        # can only ever reduce duplicate copies of a gap that is already
        # reported -- it can never turn a gap into a pass.
        key = (effect.type, effect.target, action, effect.case)
        if key in seen_gaps:
            continue
        seen_gaps.add(key)
        report.gaps.append(EffectGap(effect=effect))

    # HP-04: which actions were skipped, so a port only those actions declare
    # can be reported as unexercised rather than as proven dead surface.
    executed_names = set(report.executed_actions)
    skipped_names = {skip.action for skip in skipped_list if skip.action and skip.action not in executed_names}
    for name, decl in sorted(declarations.ports.items()):
        if name in exercised:
            continue
        declaring = sorted(
            action for action, ports in declarations.action_ports.items() if name in ports
        )
        blocked = tuple(action for action in declaring if action in skipped_names)
        # Only an annotation when EVERY declaring action was skipped. If even
        # one ran and did not exercise the port, the run does carry evidence and
        # softening the message would be the absence-of-evidence mistake in the
        # other direction.
        if declaring and len(blocked) == len(declaring):
            report.dead_surface.append(DeadSurface(port=decl, blocked_by=blocked))
        else:
            report.dead_surface.append(DeadSurface(port=decl))

    return report


# ---------------------------------------------------------------------------
# Execution (HP-04). Moved here from `scripts/effect_conformance_report.py` so
# the oracle's own module owns the loop, and so the three defects below have one
# place to be fixed rather than one per caller.
# ---------------------------------------------------------------------------

#: The repository root, i.e. the directory holding ``scripts/`` and
#: ``spec_double_compiler/``. Scaffolded adapters import ``CaseRunResult`` from
#: the latter, so it belongs on every import path the oracle builds.
_TOOLCHAIN_ROOT = Path(__file__).resolve().parents[1]


def corpus_import_roots(spec_dir: Path, extra: Iterable[Path] = ()) -> list[Path]:
    """The import roots a scaffolded project's adapters need. RC-02-DF-02.

    ``case_adapters.toml`` -- the file ``tla-spec-dev scaffold`` writes -- names
    adapters as bare module paths such as
    ``production_adapters:BuildSkillCliAdapter``. Those resolve only with the
    target spec directory on ``sys.path``.

    The enforcing runner already gets exactly this set: ``run spec-unit-tests``
    spawns ``scripts/run_generated_case_adapters.py`` with
    ``PYTHONPATH=<target dir>:<repo root>:<toolchain root>``
    (``scripts/tla_spec_dev.py``, ``command_env``). The standalone oracle built
    none of it, which made it the only one of the pair that could not read a
    project the CLI itself created -- the exact inverse of the documented
    relationship between them. The order here mirrors ``command_env``: the spec
    dir first, so a project's own module wins over a same-named one in the
    toolchain.
    """
    roots: list[Path] = []
    for candidate in (Path(spec_dir), *[Path(item) for item in extra], Path.cwd(), _TOOLCHAIN_ROOT):
        try:
            resolved = candidate.resolve()
        except OSError:  # pragma: no cover - defensive
            continue
        if resolved not in roots:
            roots.append(resolved)
    return roots


def ensure_import_roots(roots: Iterable[Path]) -> list[str]:
    """Put ``roots`` at the front of ``sys.path``; return the ones added.

    Front, not back: a scaffolded project's ``production_adapters`` must win
    over anything already importable under that name, or the oracle silently
    measures the wrong program.
    """
    added: list[str] = []
    for root in reversed(list(roots)):
        text = str(root)
        if text in sys.path:
            continue
        sys.path.insert(0, text)
        added.append(text)
    return added


def reset_case_work_dir(work_dir: Path, case_name: str) -> Path:
    """Return an EMPTY directory for ``case_name`` under ``work_dir``.

    MF026-R4-F-01. The oracle's gap count was 20 / 15 / 14 across three runs of
    an identical corpus on an identical tree -- a 43% spread on the number that
    would gate anything -- and the cause was this directory surviving between
    runs. Adapters materialize their own before-state by replaying CLI commands
    into ``<case>/target-repo``; a scaffold command writes a file on a cold run
    and finds it already present on a warm one, so the cold run observes a
    ``filesystem.write`` the warm run does not. That is a gap that exists
    because of what ran yesterday.

    Only the per-case subdirectory is removed, and only under a directory the
    oracle owns. Recreating it is what makes the run a function of the corpus
    and the tree; leaving the parent alone is what keeps ``--work-dir`` a
    directory the caller can point anywhere without the oracle emptying it.
    """
    # MF-026 round 2. The per-case directory lives under a fixed `case-work`
    # component -- the same shape scripts/run_generated_case_adapters.py:1413 (case-work)
    # already uses -- so `case_work_dir_delete` can declare `**/case-work/*`
    # instead of `**`. The first repair declared `**`, which _target_matches
    # collapses to `*` and fnmatch crosses separators with, so it accepted every
    # string and no filesystem.delete on this action could ever be a gap again.
    # `--work-dir` stays pointable anywhere; only the component is fixed.
    case_dir = Path(work_dir) / "case-work" / case_name
    if case_dir.exists():
        shutil.rmtree(case_dir)
    case_dir.mkdir(parents=True, exist_ok=True)
    return case_dir


def _case_action_name(case: Any) -> str:
    """The action a generated case exercises, from the case's own input."""
    action = getattr(getattr(case, "input", None), "action", None)
    if isinstance(action, str) and action:
        return action
    for label in sorted(getattr(case, "labels", ()) or ()):
        if isinstance(label, str) and label and ":" not in label:
            return label
    return ""


@dataclass
class CorpusExecution:
    """What one corpus execution produced, beside the recorded effects."""

    cases: list[str] = field(default_factory=list)
    offered_actions: list[str] = field(default_factory=list)
    executed_actions: list[str] = field(default_factory=list)
    work_dir: Path | None = None
    import_roots: list[str] = field(default_factory=list)


def adapter_skip_reason(adapter: Any, case: Any) -> tuple[str, str] | None:
    """Why ``adapter`` cannot run ``case``, or ``None`` if it can. RC-02-DF-03.

    Two distinct facts, kept distinct because they mean different things about
    the model:

    * **no case-driven entry point at all** -- the adapter implements
      ``apply()`` and no ``run(case, work_dir)``. Nine of this repository's own
      seventeen bound adapters are in this state, so the oracle can execute at
      most 8 of 18 modeled actions, and that is a fact about the ADAPTERS.
    * **the adapter declined this case** -- it has a ``run`` and its own
      ``can_run``/``validate`` refused this particular input. That is a fact
      about the CASE, and it is the check ``run_generated_case_adapters``
      already applies before executing anything.
    """
    from spec_double_compiler.runtime import adapter_accepts_case

    if getattr(adapter, "run", None) is None:
        return (
            SKIP_NOT_RUNNABLE,
            "adapter defines apply() but no run(case, work_dir), so no case can drive it; "
            "the oracle observes nothing for this action",
        )
    accepted, reason = adapter_accepts_case(adapter, case)
    if not accepted:
        return (SKIP_DECLINED, reason or "adapter can_run() declined this case")
    return None


def execute_corpus(
    *,
    spec_dir: Path,
    cases_dirs: Iterable[Path],
    mapping_path: Path,
    work_dir: Path,
    recorder: EffectRecorder,
    import_roots: Iterable[Path] = (),
) -> CorpusExecution:
    """Run each mapped adapter for each case in the sandbox.

    The whole loop, with all three HP-04 repairs applied in one place:
    :func:`corpus_import_roots` before the first import, :func:`reset_case_work_dir`
    before each case, and :func:`adapter_skip_reason` instead of an unconditional
    ``call_adapter``.
    """
    from run_generated_case_adapters import adapter_for_case, load_cases, load_mappings
    from spec_double_compiler.runtime import call_adapter, instantiate, load_object

    execution = CorpusExecution(work_dir=Path(work_dir))
    execution.import_roots = ensure_import_roots(corpus_import_roots(Path(spec_dir), import_roots))

    mappings = load_mappings(Path(mapping_path))
    work_root = Path(work_dir)
    work_root.mkdir(parents=True, exist_ok=True)

    adapter_cache: dict[str, Any] = {}
    for cases_dir in cases_dirs:
        module = load_cases(Path(cases_dir))
        for case in module.CASES:
            mapping = adapter_for_case(case, mappings)
            # An UNBOUND case still has an action -- that is the whole point of
            # reporting it -- so the name comes from the case itself when the
            # mapping has nothing to offer.
            action = mapping.label if mapping is not None else _case_action_name(case)
            if action:
                execution.offered_actions.append(action)
            if mapping is None or mapping.adapter is None:
                # An unbound action is a fact about the mapping, and before
                # HP-04 it was passed over in silence -- indistinguishable in
                # the report from an action that ran clean.
                recorder.record_skip(
                    SkippedCase(
                        case=case.name,
                        action=action,
                        adapter="",
                        reason="no adapter is bound for this action in " + Path(mapping_path).name,
                        kind=SKIP_UNBOUND,
                    )
                )
                continue
            adapter = adapter_cache.get(mapping.adapter)
            if adapter is None:
                adapter = instantiate(load_object(mapping.adapter))
                adapter_cache[mapping.adapter] = adapter
            skip = adapter_skip_reason(adapter, case)
            if skip is not None:
                kind, reason = skip
                recorder.record_skip(
                    SkippedCase(
                        case=case.name,
                        action=mapping.label,
                        adapter=mapping.adapter,
                        reason=reason,
                        kind=kind,
                    )
                )
                continue
            case_dir = reset_case_work_dir(Path(work_dir), case.name)
            sandbox = EffectSandbox(root=case_dir / "sandbox", recorder=recorder)
            execution.cases.append(case.name)
            execution.executed_actions.append(mapping.label)
            # MF-027: same assessment as the enforcing copy in
            # run_generated_case_adapters. Both runners refuse; neither is the
            # lenient one.
            sandbox.require_observable(
                mapping.adapter or mapping.label,
                resolved=adapter,
                runtime=getattr(mapping, "runtime", None),
                kind=mapping.kind,
                channel=mapping.channel,
            )
            try:
                with sandbox, sandbox.observe(action=mapping.label, case=case.name):
                    call_adapter(adapter, case, case_dir)
            except Exception as exc:  # noqa: BLE001 -- reported, not swallowed
                # One bad case used to hide every case after it. Collect it,
                # keep going, and FAIL the run: see SKIP_ERROR.
                recorder.record_skip(
                    SkippedCase(
                        case=case.name,
                        action=mapping.label,
                        adapter=mapping.adapter,
                        reason=f"{type(exc).__name__}: {exc}",
                        kind=SKIP_ERROR,
                    )
                )
    return execution
