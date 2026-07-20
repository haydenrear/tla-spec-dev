#!/usr/bin/env python3
"""Recover TLA+ action parameters from a case's own before/after state pair.

MF-029. Every generated case used to carry ``params={}``: the generator
recorded *that* an action fired, never *with what*. For a CLI that is most of
the point -- an adapter checked without arguments buys reachability testing,
not argument testing.

This is deliberately a GENERATOR-side recovery and NOT a model change. Adding a
``lastInternalAction`` marker to the TLA+ module was considered and rejected:
unnecessary, because the parameters are already implied by the state pair the
generator holds; and unaffordable, because ``max_state_space_bound`` sits at
70% and MF-019 proved a single boolean variable breaches it. Being
generator-side is also what makes this cheaply revertible -- nothing in the
spec changes, and reverting is deleting this module.

Three mechanisms recover a parameter, in this preference order:

``guard-pinned``
    The action body contains a conjunct ``param = someVariable`` with
    ``someVariable`` unprimed. The parameter therefore equals the BEFORE-state
    value of that variable. This is the safest mechanism: nothing in the
    after-state is consulted, so every after-state field stays independently
    checkable.

``except-index``
    The action body contains ``v' = [v EXCEPT ![param] = ...]``. The parameter
    is the index whose entry differs between before and after. The identity of
    the changed index is consumed by the recovery, so "which index changed" is
    no longer an independent check for ``v``; the value it changed *to*, and
    every other variable, still are.

``written-through``
    The action body contains a conjunct ``v' = param``. The parameter is read
    straight out of the after-state.

    THIS IS THE MECHANISM CLOSEST TO THE TRAP. MF-028's spike defaulted
    ``spec_root`` from ``case.after`` and then "checked" the result against
    ``case.after``; it passed vacuously, and was caught only because a negative
    control that should have failed, passed. Recovering the parameter this way
    is legitimate. Checking the field it was recovered FROM is not -- that
    field is a tautology for this action and is reported as such in
    ``unavailable_checks``.

Anything the three mechanisms do not reach is marked ``UNCHECKED``. It is never
fabricated, and the case is never dropped: an unrecoverable parameter is a
finding to report, not a case to filter away.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


GUARD_PINNED = "guard-pinned"
EXCEPT_INDEX = "except-index"
WRITTEN_THROUGH = "written-through"
UNRECOVERABLE = "unrecoverable"


class Unchecked:
    """Sentinel for a parameter that could not be recovered.

    It is deliberately NOT ``None``, ``""`` or ``0``: those are values a model
    could legitimately produce, and an adapter comparing against one of them
    could pass by coincidence. ``UNCHECKED`` compares equal only to itself, so
    any check that expects a concrete argument fails loudly against it.
    """

    _instance: "Unchecked | None" = None

    def __new__(cls) -> "Unchecked":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "UNCHECKED"

    def __bool__(self) -> bool:
        return False

    def __eq__(self, other: Any) -> bool:
        return other is self

    def __ne__(self, other: Any) -> bool:
        return other is not self

    def __hash__(self) -> int:
        return hash("tla-spec-dev.UNCHECKED")


UNCHECKED = Unchecked()


@dataclass(frozen=True)
class ParamRecovery:
    """How one formal parameter of one action is recovered."""

    name: str
    mechanism: str
    variable: str | None = None
    reason: str | None = None

    @property
    def recoverable(self) -> bool:
        return self.mechanism != UNRECOVERABLE


@dataclass(frozen=True)
class ActionRecipe:
    """The complete recovery plan for one action label."""

    action: str
    params: tuple[ParamRecovery, ...]

    @property
    def fully_recoverable(self) -> bool:
        return all(param.recoverable for param in self.params)

    @property
    def unavailable_checks(self) -> tuple[str, ...]:
        """After-state fields that this action's recovery has made tautological.

        A ``written-through`` parameter is read out of the after-state, so
        comparing that same after-state field against the recovered parameter
        proves nothing. Callers must treat these fields as NOT independently
        checkable for this action.
        """
        return tuple(
            sorted(
                {
                    param.variable
                    for param in self.params
                    if param.mechanism == WRITTEN_THROUGH and param.variable
                }
            )
        )


# ---------------------------------------------------------------------------
# TLA+ source analysis
# ---------------------------------------------------------------------------

DEFINITION_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(?:\(([^)]*)\))?\s*==\s*$")
VARIABLES_RE = re.compile(r"^\s*VARIABLES?\b(.*)$")
COMMENT_RE = re.compile(r"\\\*.*$")


def strip_comments(text: str) -> str:
    return "\n".join(COMMENT_RE.sub("", line) for line in text.splitlines())


def parse_variables(source: str) -> tuple[str, ...]:
    """Collect the declared VARIABLES of a module."""
    lines = strip_comments(source).splitlines()
    names: list[str] = []
    collecting = False
    for line in lines:
        match = VARIABLES_RE.match(line)
        if match:
            collecting = True
            line = match.group(1)
        elif not collecting:
            continue
        stripped = line.strip()
        if collecting and not stripped:
            # A blank line ends the (contiguous) declaration block.
            if names:
                break
            continue
        if collecting and DEFINITION_RE.match(line):
            break
        for token in re.split(r"[,\s]+", stripped):
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", token or ""):
                names.append(token)
        if collecting and not stripped.endswith(","):
            # Declarations here are one-per-line and comma-separated; the first
            # line without a trailing comma closes the block.
            if names:
                break
    return tuple(dict.fromkeys(names))


def parse_action_bodies(source: str) -> dict[str, tuple[tuple[str, ...], str]]:
    """Map every top-level definition to its formal parameters and body text."""
    lines = strip_comments(source).splitlines()
    bodies: dict[str, tuple[tuple[str, ...], str]] = {}
    current: str | None = None
    params: tuple[str, ...] = ()
    buffer: list[str] = []
    for line in lines:
        match = DEFINITION_RE.match(line)
        if match:
            if current is not None:
                bodies[current] = (params, "\n".join(buffer))
            current = match.group(1)
            raw_params = match.group(2) or ""
            params = tuple(
                token.strip()
                for token in raw_params.split(",")
                if token.strip()
            )
            buffer = []
            continue
        if current is not None:
            buffer.append(line)
    if current is not None:
        bodies[current] = (params, "\n".join(buffer))
    return bodies


def classify_param(param: str, body: str, variables: tuple[str, ...]) -> ParamRecovery:
    """Decide which mechanism recovers ``param`` inside ``body``.

    Preference order is guard-pinned, then except-index, then written-through:
    strictly increasing reliance on the after-state, so the mechanism that
    consults the least of it wins.
    """
    escaped = re.escape(param)

    # 1. guard-pinned: a conjunct `param = v` (or `v = param`) with v unprimed.
    for variable in variables:
        pinned = re.compile(
            rf"/\\\s*(?:{escaped}\s*=\s*{re.escape(variable)}"
            rf"|{re.escape(variable)}\s*=\s*{escaped})\s*(?:$|\n)",
            re.MULTILINE,
        )
        if pinned.search(body):
            return ParamRecovery(name=param, mechanism=GUARD_PINNED, variable=variable)

    # 2. except-index: `v' = [v EXCEPT ![param] = ...]`, possibly inside an IF.
    for variable in variables:
        except_index = re.compile(
            rf"{re.escape(variable)}'\s*=\s*(?:.*?\s)?\[\s*{re.escape(variable)}\s+EXCEPT\s+!\[\s*{escaped}\s*\]",
            re.DOTALL,
        )
        if except_index.search(body):
            return ParamRecovery(name=param, mechanism=EXCEPT_INDEX, variable=variable)

    # 3. written-through: a conjunct `v' = param`.
    for variable in variables:
        written = re.compile(
            rf"/\\\s*{re.escape(variable)}'\s*=\s*{escaped}\s*(?:$|\n)",
            re.MULTILINE,
        )
        if written.search(body):
            return ParamRecovery(name=param, mechanism=WRITTEN_THROUGH, variable=variable)

    return ParamRecovery(
        name=param,
        mechanism=UNRECOVERABLE,
        reason=(
            "no conjunct pins the parameter to a before-state variable, indexes a "
            "function with it, or writes it into the after-state; the state pair "
            "does not determine it"
        ),
    )


def build_recipes(tla_source: str) -> dict[str, ActionRecipe]:
    """Derive one recovery recipe per parameterised definition in a module."""
    variables = parse_variables(tla_source)
    bodies = parse_action_bodies(tla_source)
    recipes: dict[str, ActionRecipe] = {}
    for name, (params, body) in bodies.items():
        # Only definitions that assign primed variables are actions.
        if not re.search(r"[A-Za-z_][A-Za-z0-9_]*'\s*=", body) and "UNCHANGED" not in body:
            continue
        recipes[name] = ActionRecipe(
            action=name,
            params=tuple(classify_param(param, body, variables) for param in params),
        )
    return recipes


def build_recipes_from_path(tla_path: Path) -> dict[str, ActionRecipe]:
    return build_recipes(Path(tla_path).read_text())


# ---------------------------------------------------------------------------
# Applying a recipe to a state pair
# ---------------------------------------------------------------------------


def changed_indices(before: Any, after: Any) -> list[str]:
    """Indices whose entry differs between two TLC function values."""
    if not isinstance(before, dict) or not isinstance(after, dict):
        return []
    keys = sorted(set(before) | set(after))
    return [key for key in keys if before.get(key) != after.get(key)]


def recover_param(
    recovery: ParamRecovery,
    before: dict[str, Any],
    after: dict[str, Any],
) -> Any:
    """Recover one parameter, or return ``UNCHECKED``.

    Never invents a value. Every branch that cannot establish the argument
    returns the sentinel rather than something that would make a downstream
    comparison succeed.
    """
    if recovery.mechanism == GUARD_PINNED:
        variable = recovery.variable or ""
        if variable not in before:
            return UNCHECKED
        # Derived from the BEFORE state only. The after-state is never read.
        return before[variable]

    if recovery.mechanism == EXCEPT_INDEX:
        variable = recovery.variable or ""
        indices = changed_indices(before.get(variable), after.get(variable))
        if len(indices) != 1:
            # Zero changed indices means the EXCEPT branch was not taken on this
            # edge (for example RunSpecUnitTests on a failing gate, whose
            # ticket_state' is the unchanged function). More than one means the
            # diff is ambiguous. Neither justifies guessing.
            return UNCHECKED
        return indices[0]

    if recovery.mechanism == WRITTEN_THROUGH:
        variable = recovery.variable or ""
        if variable not in after:
            return UNCHECKED
        return after[variable]

    return UNCHECKED


def infer_params(
    action: str,
    before: dict[str, Any],
    after: dict[str, Any],
    recipes: dict[str, ActionRecipe] | None,
) -> dict[str, Any]:
    """Recover every formal parameter of ``action`` from its own state pair."""
    if not recipes:
        return {}
    recipe = recipes.get(action)
    if recipe is None:
        return {}
    return {
        recovery.name: recover_param(recovery, before, after)
        for recovery in recipe.params
    }


def unchecked_param_names(params: dict[str, Any]) -> tuple[str, ...]:
    return tuple(sorted(name for name, value in params.items() if value is UNCHECKED))


# ---------------------------------------------------------------------------
# Audit reporting
# ---------------------------------------------------------------------------


def render_audit(recipes: dict[str, ActionRecipe]) -> str:
    """A per-action recoverability audit, named mechanism by named mechanism."""
    lines = [
        "# Action parameter recoverability audit",
        "",
        "Generated by `scripts/infer_action_params.py` (MF-029) from the TLA+",
        "module source. Every action label is listed, including the ones with no",
        "parameters, so the audit is complete rather than selective.",
        "",
        "| Action | Parameter | Mechanism | Source variable | Fields no longer independently checkable |",
        "|---|---|---|---|---|",
    ]
    for action in sorted(recipes):
        recipe = recipes[action]
        blocked = ", ".join(recipe.unavailable_checks) or "-"
        if not recipe.params:
            lines.append(f"| `{action}` | *(none)* | n/a -- nullary action | - | - |")
            continue
        for recovery in recipe.params:
            variable = f"`{recovery.variable}`" if recovery.variable else "-"
            note = recovery.mechanism
            if recovery.mechanism == UNRECOVERABLE:
                note = f"**UNRECOVERABLE -> UNCHECKED** ({recovery.reason})"
            lines.append(
                f"| `{action}` | `{recovery.name}` | {note} | {variable} | {blocked} |"
            )
    unrecoverable = [
        (recipe.action, recovery.name)
        for recipe in recipes.values()
        for recovery in recipe.params
        if not recovery.recoverable
    ]
    lines.extend(["", "## Findings", ""])
    if unrecoverable:
        lines.append("Parameters marked UNCHECKED (never fabricated, never a reason to drop a case):")
        lines.append("")
        for action, param in sorted(unrecoverable):
            lines.append(f"- `{action}({param})`")
    else:
        lines.append("Every parameter of every action is recoverable from its state pair.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tla", type=Path)
    parser.add_argument("--out", type=Path, help="Write the audit here instead of stdout.")
    args = parser.parse_args()
    audit = render_audit(build_recipes_from_path(args.tla))
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(audit)
        print(f"wrote {args.out}")
    else:
        print(audit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
