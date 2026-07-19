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

3. **Diff.** Observed effects are matched against the ports declared for the
   case's action. Two findings, both hard failures:

   - An **undeclared observed effect** is a gap: the model is blind to real
     behavior, which is the one thing a representation may not be. The gap is
     recorded AND the run fails.
   - A **declared-but-never-observed port** across the whole corpus is dead
     model surface: remove the port, or produce a case that exercises it.

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
"""

from __future__ import annotations

import builtins
import fnmatch
import json
import os
import shutil
import subprocess
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
    }
)

VERDICT_CLEAN = "clean"
VERDICT_GAPS = "gaps"
VERDICT_DEAD_SURFACE = "dead_surface"


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
    """A declared port no case ever exercised. Always a failure."""

    port: PortDeclaration

    def describe(self) -> str:
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

    @property
    def ok(self) -> bool:
        # Note the shape: no flag, no manifest entry, and no justification is
        # consulted here. Findings exist => the run fails. This property is the
        # gate the 2026-07-18 audit required, and inverting it is the escape it
        # withdrew.
        return not self.gaps and not self.dead_surface

    @property
    def verdict(self) -> str:
        """Maps onto the TLA ``effect_conformance`` variable."""
        if self.gaps:
            return VERDICT_GAPS
        if self.dead_surface:
            return VERDICT_DEAD_SURFACE
        return VERDICT_CLEAN

    def summary(self) -> str:
        return (
            f"effect conformance {self.verdict}: {len(self.observed)} observed effect(s) over "
            f"{len(self.cases)} case(s), {len(self.declared)} declared port(s), "
            f"{len(self.gaps)} gap(s), {len(self.dead_surface)} dead port(s)"
        )

    def render(self) -> str:
        lines = [self.summary()]
        if self.ignored_suppression_keys:
            lines.append("")
            lines.append(
                "IGNORED SUPPRESSION ATTEMPT(S) -- these keys were found in the effects "
                "block and had NO effect on the verdict. Out-of-contract justifications "
                "were withdrawn 2026-07-18; nothing suppresses a gap report:"
            )
            lines.extend(f"  - {key}" for key in self.ignored_suppression_keys)
        for gap in self.gaps:
            lines.append(f"  - {gap.describe()}")
        for dead in self.dead_surface:
            lines.append(f"  - {dead.describe()}")
        if not self.ok:
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
                {"port": dead.port.qualified, "type": dead.port.type, "target": dead.port.target}
                for dead in self.dead_surface
            ],
            "ignored_suppression_keys": list(self.ignored_suppression_keys),
            "suppression_policy": (
                "withdrawn 2026-07-18: no justification, annotation, or manifest entry "
                "suppresses a gap report"
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
) -> EffectConformanceReport:
    """Diff observed effects against declared ports.

    Per case: every observed effect must match a port declared for that case's
    action. Across the corpus: every declared port must have matched at least
    one observed effect.
    """
    observed_list = list(observed)
    case_actions = case_actions or {}
    report = EffectConformanceReport(
        observed=observed_list,
        declared=declarations.all_qualified(),
        cases=list(cases),
        ignored_suppression_keys=list(declarations.ignored_suppression_keys),
    )

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

    for name, decl in sorted(declarations.ports.items()):
        if name not in exercised:
            report.dead_surface.append(DeadSurface(port=decl))

    return report
