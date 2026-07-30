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

Four mechanisms recover a parameter, in this preference order:

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

``set-membership``  (RP-02)
    The action body contains ``v' = v \\cup {param}`` or ``v' = v \\ {param}``.
    The parameter is the element that ENTERED or LEFT that set between before
    and after. This is the shape of every ``\\E i \\in Items`` action on a
    set-valued model, and MF-029 recovered NONE of them: the audit said
    UNRECOVERABLE and the adapters were left to re-derive the argument from the
    after-state themselves, which is oracle leakage in a place nobody audits.

    Recovery is CROSS-CHECKED. An action typically moves the same element
    through several sets at once (``Accept(i)`` takes ``i`` out of ``inbox``
    and puts it into ``accepted``), and every such conjunct is an independent
    witness. All witnesses that produce exactly one moved element must agree;
    a disagreement, or two elements moving in every witness at once, yields
    ``UNCHECKED`` rather than a guess. That is the soundness bound: the
    mechanism is sound exactly when the state pair determines the element, and
    it says so when it does not.

    Like ``except-index``, the recovery CONSUMES an observation: "which element
    moved in ``v``" is no longer an independent check for the source variables
    (``consumed_observations``). Everything else -- the other variables, the
    action's output, and the *effects* it performed -- still is.

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
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


GUARD_PINNED = "guard-pinned"
EXCEPT_INDEX = "except-index"
SET_MEMBERSHIP = "set-membership"
WRITTEN_THROUGH = "written-through"
UNRECOVERABLE = "unrecoverable"

#: Directions a set-membership conjunct can move its parameter.
ENTERED = "entered"
LEFT = "left"


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
    #: Every witness a ``set-membership`` recovery cross-checks, as
    #: ``(variable, ENTERED | LEFT)`` pairs in declaration order. Empty for
    #: every other mechanism.
    sources: tuple[tuple[str, str], ...] = ()

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

    @property
    def consumed_observations(self) -> tuple[str, ...]:
        """Observations the recovery has spent, phrased as what they were.

        Weaker than ``unavailable_checks``, and deliberately separate from it.
        ``except-index`` spends "which index of ``v`` changed" and
        ``set-membership`` spends "which element moved in ``v``"; the value
        each changed *to* stays checkable, and so does every other variable.
        Reported so a reader of the audit can see the price of the recovery
        rather than infer it.
        """
        spent: list[str] = []
        for param in self.params:
            if param.mechanism == EXCEPT_INDEX and param.variable:
                spent.append(f"which index of `{param.variable}` changed")
            elif param.mechanism == SET_MEMBERSHIP:
                for variable, direction in param.sources:
                    verb = "entered" if direction == ENTERED else "left"
                    spent.append(f"which element {verb} `{variable}`")
        return tuple(sorted(dict.fromkeys(spent)))


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


def set_membership_sources(
    param: str,
    body: str,
    variables: tuple[str, ...],
) -> tuple[tuple[str, str], ...]:
    """Every ``v' = v \\cup {param}`` / ``v' = v \\ {param}`` conjunct in a body.

    Returned in VARIABLES declaration order so the recipe -- and therefore the
    corpus -- is deterministic regardless of dict iteration or source layout.
    """
    escaped = re.escape(param)
    found: list[tuple[str, str]] = []
    for variable in variables:
        name = re.escape(variable)
        entered = re.compile(
            rf"{name}'\s*=\s*(?:"
            rf"{name}\s*\\(?:cup|union)\s*\{{\s*{escaped}\s*\}}"
            rf"|\{{\s*{escaped}\s*\}}\s*\\(?:cup|union)\s*{name}"
            rf")",
            re.DOTALL,
        )
        # Set difference: a lone backslash followed by the singleton. `\cup`
        # cannot match here -- a letter follows its backslash, not a brace.
        left = re.compile(
            rf"{name}'\s*=\s*{name}\s*\\\s*\{{\s*{escaped}\s*\}}",
            re.DOTALL,
        )
        if entered.search(body):
            found.append((variable, ENTERED))
        if left.search(body):
            found.append((variable, LEFT))
    return tuple(found)


def classify_param(param: str, body: str, variables: tuple[str, ...]) -> ParamRecovery:
    """Decide which mechanism recovers ``param`` inside ``body``.

    Preference order is guard-pinned, then except-index, then set-membership,
    then written-through: strictly increasing reliance on the after-state, so
    the mechanism that consults the least of it wins.
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

    # 3. set-membership: `v' = v \cup {param}` or `v' = v \ {param}`. Every
    #    matching conjunct is kept as a cross-checking witness.
    sources = set_membership_sources(param, body, variables)
    if sources:
        return ParamRecovery(
            name=param,
            mechanism=SET_MEMBERSHIP,
            variable=sources[0][0],
            sources=sources,
        )

    # 4. written-through: a conjunct `v' = param`.
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
            "function with it, adds it to or removes it from a set, or writes it "
            "into the after-state; the state pair does not determine it"
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

    if recovery.mechanism == SET_MEMBERSHIP:
        return recover_set_member(recovery, before, after)

    if recovery.mechanism == WRITTEN_THROUGH:
        variable = recovery.variable or ""
        if variable not in after:
            return UNCHECKED
        return after[variable]

    return UNCHECKED


def moved_members(before: Any, after: Any, direction: str) -> list[Any] | None:
    """Elements that entered or left a set, or ``None`` if either side is not one.

    ``None`` (not-a-set) is kept distinct from ``[]`` (a set that did not move)
    so the caller can tell "this witness does not apply" from "this witness saw
    nothing move".
    """
    if not isinstance(before, (set, frozenset)) or not isinstance(after, (set, frozenset)):
        return None
    moved = set(after) - set(before) if direction == ENTERED else set(before) - set(after)
    return sorted(moved, key=repr)


def recover_set_member(
    recovery: ParamRecovery,
    before: dict[str, Any],
    after: dict[str, Any],
) -> Any:
    """The element the transition moved, agreed by every applicable witness.

    Sound exactly when the state pair determines the element. It does not when
    a witness sees two or more elements move at once (which one was the
    argument?) or when two witnesses disagree (a conditional body took a branch
    the recipe cannot see). Both are ``UNCHECKED``, never a guess: a case with
    an unrecovered argument is a finding to report, not a case to drop.
    """
    witnesses: list[Any] = []
    for variable, direction in recovery.sources:
        moved = moved_members(before.get(variable), after.get(variable), direction)
        if moved is None or len(moved) != 1:
            # Not a set, nothing moved (the conjunct was vacuous on this edge),
            # or an ambiguous multi-element move. Not evidence either way.
            continue
        witnesses.append(moved[0])
    if not witnesses:
        return UNCHECKED
    first = witnesses[0]
    if any(candidate != first for candidate in witnesses[1:]):
        return UNCHECKED
    return first


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
# Measuring what a run actually recovered
# ---------------------------------------------------------------------------
#
# RP-02. The audit used to be written from the RECIPES alone: a static reading
# of the module's syntax. On `reminder_worker` it printed "Every parameter of
# every action is recoverable from its state pair" over a run that had just
# reported `0/38 cases carry arguments`, because a mechanism NAMED is not an
# argument RECOVERED. The audit contradicted the corpus it audits (EV-02-DF-03).
#
# The fix is not softer wording. It is that the audit now takes the corpus's
# own measurement and reports THAT, per parameter. A class the run failed to
# recover is UNRECOVERABLE for that class no matter what the syntax promised,
# and the sentence claiming universal recoverability cannot be reached without
# a non-empty corpus in which every exercised parameter was in fact recovered.


@dataclass(frozen=True)
class RecoveryMeasurement:
    """Measured recovery for one parameter of one action, over one corpus."""

    action: str
    param: str
    cases: int = 0
    recovered: int = 0

    @property
    def unchecked(self) -> int:
        return self.cases - self.recovered

    @property
    def verdict(self) -> str:
        if self.cases == 0:
            return "not exercised"
        if self.recovered == 0:
            return "UNRECOVERABLE"
        if self.recovered == self.cases:
            return "recovered"
        return "partial"


@dataclass(frozen=True)
class CorpusMeasurement:
    """What one generation run recovered, counted case by case."""

    total_cases: int = 0
    action_cases: dict[str, int] = field(default_factory=dict)
    params: dict[tuple[str, str], RecoveryMeasurement] = field(default_factory=dict)

    def for_param(self, action: str, param: str) -> RecoveryMeasurement:
        return self.params.get((action, param), RecoveryMeasurement(action, param))

    @property
    def unrecovered(self) -> tuple[RecoveryMeasurement, ...]:
        return tuple(
            measurement
            for _, measurement in sorted(self.params.items())
            if measurement.verdict == "UNRECOVERABLE"
        )

    @property
    def partial(self) -> tuple[RecoveryMeasurement, ...]:
        return tuple(
            measurement
            for _, measurement in sorted(self.params.items())
            if measurement.verdict == "partial"
        )

    @property
    def fully_recovered(self) -> bool:
        """True only when a NON-EMPTY corpus recovered every exercised parameter."""
        exercised = [m for m in self.params.values() if m.cases]
        return bool(self.total_cases) and bool(exercised) and all(
            measurement.verdict == "recovered" for measurement in exercised
        )


def measure_recovery(
    observations: Iterable[tuple[str, dict[str, Any]]],
) -> CorpusMeasurement:
    """Count, per action parameter, how many cases carry a real argument.

    ``observations`` is ``(action, params)`` per emitted case -- the corpus as
    it was written to disk, with nothing dropped, filtered or sampled.
    """
    total = 0
    action_cases: dict[str, int] = {}
    tally: dict[tuple[str, str], list[int]] = {}
    for action, params in observations:
        total += 1
        action_cases[action] = action_cases.get(action, 0) + 1
        for name, value in (params or {}).items():
            counts = tally.setdefault((action, name), [0, 0])
            counts[0] += 1
            if value is not UNCHECKED:
                counts[1] += 1
    return CorpusMeasurement(
        total_cases=total,
        action_cases=action_cases,
        params={
            key: RecoveryMeasurement(key[0], key[1], cases=counts[0], recovered=counts[1])
            for key, counts in tally.items()
        },
    )


# ---------------------------------------------------------------------------
# Audit reporting
# ---------------------------------------------------------------------------


def _measured_cell(measurement: RecoveryMeasurement) -> str:
    verdict = measurement.verdict
    if verdict == "not exercised":
        return "*not exercised by this corpus (0 cases)*"
    if verdict == "UNRECOVERABLE":
        return f"**UNRECOVERABLE ON THIS CORPUS -- 0 of {measurement.cases} cases carry it**"
    if verdict == "partial":
        return f"**PARTIAL -- {measurement.recovered} of {measurement.cases} cases carry it**"
    return f"recovered in {measurement.recovered} of {measurement.cases} cases"


def render_audit(
    recipes: dict[str, ActionRecipe],
    measurement: CorpusMeasurement | None = None,
) -> str:
    """A per-action recoverability audit, mechanism by mechanism AND measured.

    ``measurement`` is the corpus this audit is about. Without one the audit
    declares itself STATIC and makes no claim about any corpus -- it may not,
    because a named mechanism is a property of the module's syntax and an
    argument on a case is a property of a run.
    """
    measured = measurement is not None
    lines = [
        "# Action parameter recoverability audit",
        "",
        "Generated by `scripts/infer_action_params.py` (MF-029, RP-02) from the",
        "TLA+ module source. Every action label is listed, including the ones with",
        "no parameters, so the audit is complete rather than selective.",
        "",
    ]
    if measured:
        assert measurement is not None
        lines.extend(
            [
                f"**Measured over the corpus this run generated: {measurement.total_cases} cases.**",
                "The `Measured` column is the count from those cases, not a reading of",
                "the syntax. Where the two disagree, the measurement is the finding.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "**STATIC AUDIT -- NO CORPUS WAS MEASURED.** Every mechanism named below",
                "is a claim about the module's syntax only. It is NOT evidence that any",
                "generated case carries an argument; nothing here may be read as one.",
                "",
            ]
        )
    header = "| Action | Parameter | Mechanism | Source variable |"
    rule = "|---|---|---|---|"
    if measured:
        header += " Measured on this corpus |"
        rule += "---|"
    header += " Fields no longer independently checkable | Observations the recovery consumed |"
    rule += "---|---|"
    lines.extend([header, rule])

    for action in sorted(recipes):
        recipe = recipes[action]
        blocked = ", ".join(f"`{name}`" for name in recipe.unavailable_checks) or "-"
        spent = "; ".join(recipe.consumed_observations) or "-"
        if not recipe.params:
            row = f"| `{action}` | *(none)* | n/a -- nullary action | - |"
            if measured:
                assert measurement is not None
                cases = measurement.action_cases.get(action, 0)
                carried = sorted(
                    param for (act, param) in measurement.params if act == action
                )
                note = f"{cases} cases, no parameters in the module"
                if carried:
                    # The model declared its own arguments through an action
                    # marker. They are NOT recovered; they were stated.
                    note += f"; the corpus carries {', '.join(f'`{n}`' for n in carried)} (model-declared)"
                row += f" {note} |"
            row += f" {blocked} | {spent} |"
            lines.append(row)
            continue
        for recovery in recipe.params:
            variable = f"`{recovery.variable}`" if recovery.variable else "-"
            if recovery.mechanism == SET_MEMBERSHIP and recovery.sources:
                variable = ", ".join(
                    f"`{name}` ({direction})" for name, direction in recovery.sources
                )
            note = recovery.mechanism
            if recovery.mechanism == UNRECOVERABLE:
                note = f"**UNRECOVERABLE -> UNCHECKED** ({recovery.reason})"
            row = f"| `{action}` | `{recovery.name}` | {note} | {variable} |"
            if measured:
                assert measurement is not None
                row += f" {_measured_cell(measurement.for_param(action, recovery.name))} |"
            row += f" {blocked} | {spent} |"
            lines.append(row)

    lines.extend(["", "## Findings", ""])
    static_unrecoverable = sorted(
        (recipe.action, recovery.name)
        for recipe in recipes.values()
        for recovery in recipe.params
        if not recovery.recoverable
    )
    if static_unrecoverable:
        lines.append(
            "No mechanism reaches these parameters at all; every case carries "
            "`UNCHECKED` for them (never fabricated, never a reason to drop a case):"
        )
        lines.append("")
        for action, param in static_unrecoverable:
            lines.append(f"- `{action}({param})` -- UNRECOVERABLE by construction")
        lines.append("")

    if not measured:
        lines.append(
            "No corpus was measured, so this audit states NOTHING about how many "
            "cases carry an argument. Run the generator to obtain that number; a "
            "mechanism named above is not a recovered argument."
        )
        lines.append("")
        return "\n".join(lines)

    assert measurement is not None
    if measurement.total_cases == 0:
        lines.append(
            "The corpus is EMPTY (0 cases). Nothing was recovered because nothing "
            "was generated; no recoverability claim is made."
        )
        lines.append("")
        return "\n".join(lines)

    unrecovered = measurement.unrecovered
    partial = measurement.partial
    if unrecovered:
        lines.append(
            "**UNRECOVERABLE on this corpus.** These parameters were reached by a "
            "mechanism, and the mechanism recovered NOTHING on a single case. The "
            "class is UNRECOVERABLE for this run whatever the syntax promised:"
        )
        lines.append("")
        for item in unrecovered:
            lines.append(
                f"- `{item.action}({item.param})` -- 0 of {item.cases} cases carry an argument"
            )
        lines.append("")
    if partial:
        lines.append("**PARTIALLY recovered.** Some cases carry an argument and some do not:")
        lines.append("")
        for item in partial:
            lines.append(
                f"- `{item.action}({item.param})` -- {item.recovered} of {item.cases} "
                f"cases carry an argument, {item.unchecked} carry `UNCHECKED`"
            )
        lines.append("")

    # Arguments the corpus carries for an action the module declares NULLARY
    # come from the model's own action marker: they were STATED by the model,
    # not recovered from a state pair. Counting them towards a recovery claim
    # would be crediting this module for work it did not do.
    described = {
        (recipe.action, recovery.name)
        for recipe in recipes.values()
        for recovery in recipe.params
    }
    declared = sorted(key for key in measurement.params if key not in described)
    if declared:
        lines.append(
            "**Model-declared, not recovered.** The corpus carries these arguments "
            "because the model states them in its own action marker. No mechanism "
            "in this module produced them and none is credited for them:"
        )
        lines.append("")
        for action, param in declared:
            item = measurement.for_param(action, param)
            lines.append(
                f"- `{action}({param})` -- stated by the model on "
                f"{item.recovered} of {item.cases} cases"
            )
        lines.append("")

    recovered_all = [
        measurement.for_param(action, param)
        for action, param in sorted(described)
        if measurement.for_param(action, param).cases
    ]
    if recovered_all and all(item.verdict == "recovered" for item in recovered_all):
        lines.append(
            "Every parameter of every action THIS CORPUS EXERCISES was recovered on "
            f"every one of its cases ({measurement.total_cases} cases). The claim is "
            "scoped to this run and to the actions it entered; it is not a claim "
            "about actions no case reached."
        )
        lines.append("")
    elif not recovered_all and not static_unrecoverable:
        lines.append(
            "This corpus exercises no parameterised action, so this module recovered "
            "nothing and makes no recoverability claim."
        )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tla", type=Path)
    parser.add_argument("--out", type=Path, help="Write the audit here instead of stdout.")
    args = parser.parse_args()
    # No corpus here: this entry point reads a module and nothing else, so the
    # audit it prints declares itself static rather than borrowing a claim it
    # has not measured.
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
