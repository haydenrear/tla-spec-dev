#!/usr/bin/env python3
"""Self-configured, composable fitness functions over the complexity descriptor.

CD-03. The agent who knows a project writes project-specific conditions over
the project's complexity descriptor -- "bound < X", "component_actions <= N",
"modularity >= Q", "no god-state", "variable_domain(v) <= D" -- composed with
and/or/not. The rules persist with the project (in ``spec_manifest.yaml``
under ``fitness_functions:``, or in a sibling ``fitness_functions.yaml`` /
``fitness_functions.json`` next to the spec -- the ``.json`` form needs only
the standard library), and when ``analyze complexity`` runs, any rule whose
condition does NOT hold FIRES and is surfaced in the report so future agents
are notified.

Deliberately quick and dirty, experimental, lean:

* the rule representation is a small YAML tree, not a DSL -- leaves are
  ``{fact, op, value}`` comparisons over the descriptor's published facts, and
  the only combinators are ``all`` / ``any`` / ``not``;
* there are NO built-in rules -- nothing fires unless the project's agent
  configured it;
* firings are ADVISORY -- they report, never block. Nothing here changes the
  scanner's exit code or gates promotion. Even a misconfigured rule is
  surfaced as INVALID rather than raised.

Semantics: a fitness function states a condition the project WANTS TO HOLD.
Evaluation is three-valued (Kleene): ``holds`` / ``fired`` (condition is
false) / ``unknown`` (a compared fact could not be measured, e.g. the bound is
UNKNOWN). Unknown never silently converts to a pass or a fail -- it is
reported as its own status.
"""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

# --------------------------------------------------------------------------
# Facts: the flat view of a descriptor a rule can compare against
# --------------------------------------------------------------------------

# Every scalar fact a leaf may name, with the one-line meaning used in error
# messages and references/fitness_functions.md. All are derived from the
# descriptor's [MEASURED] JSON payload -- rules read published facts, nothing
# private. ``variable_domain`` is the one parameterized fact (needs ``var:``).
FACT_DOCS: dict[str, str] = {
    "bound": "static state-space upper bound (UNKNOWN when no domain resolves)",
    "bound_known": "True when the static bound could be resolved at all",
    "modularity": "graph-modularity Q over the variable interaction graph",
    "component_count": "number of near-decomposable variable clusters",
    "max_component_variables": "size of the largest component, in variables",
    "max_component_actions": "actions touching the most-touched component",
    "action_count": "number of actions (top-level next-state-relation disjuncts; helpers attributed to their callers)",
    "variable_count": "number of declared variables",
    "god_state_count": "dense rows: variables touched by more than half the actions",
    "dense_column_count": "actions touching more than half the variables",
    "port_crossing_action_count": "actions touching more than one component",
    "unread_by_invariant_count": "variables no configured invariant reads",
    "unjustified_count": "variables with no justification linkage (UNKNOWN without a justification: table)",
    "variable_domain": "domain cardinality of one variable; needs var: <name>",
}

_OPS: dict[str, Any] = {
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "==": operator.eq,
    "!=": operator.ne,
}


def extract_facts(descriptor: dict[str, Any]) -> dict[str, Any]:
    """Flatten a descriptor JSON payload (``render_json`` shape) into facts.

    A fact whose value cannot be measured is ``None`` (e.g. ``bound`` when the
    descriptor reported UNKNOWN, ``unjustified_count`` without a
    ``justification:`` table); leaves comparing against it evaluate to
    ``unknown``, never to a silent pass or fail.
    """
    measured = descriptor.get("measured", {}) if isinstance(descriptor, dict) else {}
    components: list[list[str]] = measured.get("components") or []
    actions: list[dict[str, Any]] = measured.get("actions") or []
    dimensions: list[dict[str, Any]] = measured.get("dimensions") or []

    component_actions: list[int] = []
    for component in components:
        members = set(component)
        touching = [
            a
            for a in actions
            if (set(a.get("reads") or []) | set(a.get("writes") or [])) & members
        ]
        component_actions.append(len(touching))

    unjustified = measured.get("unjustified_variables")
    return {
        "bound": measured.get("state_space_upper_bound"),
        "bound_known": bool(measured.get("state_space_bound_known")),
        "modularity": measured.get("modularity"),
        "component_count": len(components),
        "max_component_variables": max((len(c) for c in components), default=0),
        "max_component_actions": max(component_actions, default=0),
        "action_count": len(actions),
        "variable_count": len(dimensions),
        "god_state_count": len(measured.get("dense_rows") or {}),
        "dense_column_count": len(measured.get("dense_columns") or []),
        "port_crossing_action_count": len(measured.get("port_crossing_actions") or {}),
        "unread_by_invariant_count": len(measured.get("unread_by_invariant") or []),
        "unjustified_count": len(unjustified) if isinstance(unjustified, list) else None,
        "variable_domain": {
            d.get("variable"): d.get("cardinality") for d in dimensions
        },
    }


# --------------------------------------------------------------------------
# Rule tree evaluation (three-valued: True / False / None-unknown)
# --------------------------------------------------------------------------


class RuleError(ValueError):
    """A rule is malformed. Caught and surfaced as an INVALID status -- a
    misconfigured fitness function is itself only advisory."""


def _fmt(value: Any) -> str:
    if isinstance(value, int) and not isinstance(value, bool):
        return f"{value:,}"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _eval_leaf(node: dict[str, Any], facts: dict[str, Any]) -> tuple[bool | None, list[str]]:
    fact = node.get("fact")
    if fact not in FACT_DOCS:
        raise RuleError(
            f"unknown fact {fact!r}; known facts: {', '.join(sorted(FACT_DOCS))}"
        )
    op_name = node.get("op")
    if op_name not in _OPS:
        raise RuleError(f"unknown op {op_name!r}; one of: {', '.join(_OPS)}")
    if "value" not in node:
        raise RuleError(f"leaf on fact {fact!r} is missing 'value'")
    expected = node["value"]

    if fact == "variable_domain":
        var = node.get("var")
        if not isinstance(var, str) or not var:
            raise RuleError("fact 'variable_domain' needs var: <variable name>")
        domains: dict[str, Any] = facts.get("variable_domain") or {}
        if var not in domains:
            raise RuleError(
                f"variable_domain: no variable {var!r} in this model; "
                f"variables: {', '.join(sorted(domains)) or '(none)'}"
            )
        measured = domains[var]
        label = f"variable_domain({var})"
    else:
        measured = facts.get(fact)
        label = str(fact)

    if measured is None:
        return None, [f"{label} is UNKNOWN, cannot check {op_name} {_fmt(expected)}"]
    try:
        outcome = bool(_OPS[op_name](measured, expected))
    except TypeError as exc:
        raise RuleError(
            f"cannot compare {label}={measured!r} {op_name} {expected!r}: {exc}"
        ) from exc
    word = "true" if outcome else "FALSE"
    return outcome, [f"{label}={_fmt(measured)} {op_name} {_fmt(expected)} is {word}"]


def evaluate_node(node: Any, facts: dict[str, Any]) -> tuple[bool | None, list[str]]:
    """Evaluate one rule-tree node. Returns ``(value, notes)``.

    ``value`` is three-valued: True (holds), False (fails), None (unknown).
    ``notes`` is the flat trace of every leaf comparison encountered, so a
    fired rule's detail shows exactly which measured facts drove it.
    """
    if not isinstance(node, dict) or not node:
        raise RuleError(f"rule node must be a non-empty mapping, got {node!r}")
    keys = set(node)
    if "all" in keys or "any" in keys:
        combinator = "all" if "all" in keys else "any"
        if keys - {combinator}:
            raise RuleError(f"'{combinator}' node has extra keys: {sorted(keys - {combinator})}")
        children = node[combinator]
        if not isinstance(children, list) or not children:
            raise RuleError(f"'{combinator}' takes a non-empty list of rule nodes")
        values: list[bool | None] = []
        notes: list[str] = []
        for child in children:
            value, child_notes = evaluate_node(child, facts)
            values.append(value)
            notes.extend(child_notes)
        if combinator == "all":
            if any(v is False for v in values):
                return False, notes
            if any(v is None for v in values):
                return None, notes
            return True, notes
        if any(v is True for v in values):
            return True, notes
        if any(v is None for v in values):
            return None, notes
        return False, notes
    if "not" in keys:
        if keys != {"not"}:
            raise RuleError(f"'not' node has extra keys: {sorted(keys - {'not'})}")
        value, notes = evaluate_node(node["not"], facts)
        return (None if value is None else not value), notes
    if "fact" in keys:
        return _eval_leaf(node, facts)
    raise RuleError(
        f"rule node needs one of 'fact', 'all', 'any', 'not'; got keys {sorted(keys)}"
    )


# --------------------------------------------------------------------------
# Per-project persistence: manifest block and/or sibling rules file
# --------------------------------------------------------------------------

# Both are probed, in this order, next to the spec. The .json file parses with
# the standard library alone -- the dependency-free choice when the CLI runs
# under a bare python3 without PyYAML.
RULES_FILENAMES = ("fitness_functions.yaml", "fitness_functions.json")
RULES_KEY = "fitness_functions"


@dataclass
class FitnessRule:
    name: str
    rule: Any
    description: str = ""
    source: str = ""


def _parse_entries(raw: Any, source: str) -> tuple[list[FitnessRule], list[str]]:
    rules: list[FitnessRule] = []
    errors: list[str] = []
    if not isinstance(raw, list):
        errors.append(f"{source}: '{RULES_KEY}' must be a list of rules")
        return rules, errors
    for index, entry in enumerate(raw):
        where = f"{source} rule[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{where}: each rule must be a mapping with name: and rule:")
            continue
        name = entry.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{where}: missing or empty name:")
            continue
        if "rule" not in entry:
            errors.append(f"{where} ({name}): missing rule:")
            continue
        rules.append(
            FitnessRule(
                name=name.strip(),
                rule=entry["rule"],
                description=str(entry.get("description") or ""),
                source=source,
            )
        )
    return rules, errors


def _load_rules_document(path: Path) -> tuple[Any, str | None]:
    """Parse one rules file. Returns ``(document, error)``.

    ``.json`` parses with the standard library; ``.yaml`` needs PyYAML and
    reports its absence as an advisory error (the CLI may run under a bare
    ``python3`` -- use ``fitness_functions.json`` there).
    """
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        try:
            import json

            return json.loads(text), None
        except Exception as exc:
            return None, f"{path.name}: unparseable JSON: {exc}"
    if not _yaml_available():
        return None, (
            f"{path.name}: PyYAML is unavailable under this python; use "
            "fitness_functions.json (standard library) instead"
        )
    import yaml  # type: ignore

    try:
        return yaml.safe_load(text), None
    except Exception as exc:
        return None, f"{path.name}: unparseable YAML: {exc}"


def _yaml_available() -> bool:
    """True when PyYAML imports under this interpreter.

    VAL-01: when it does not, the spec manifest was parsed by the repository's
    minimal fallback parser, which mangles flow-style rule leaves
    (``{fact: bound, ...}`` arrives as garbage keys like ``'{fact'``). Rules
    embedded in the manifest must then be reported as a CONFIG ERROR naming
    the missing dependency, never fed into rule validation.
    """
    try:
        import yaml  # type: ignore  # noqa: F401
    except Exception:
        return False
    return True


def load_rules(
    manifest: dict[str, Any] | None, spec_dir: Path | None
) -> tuple[list[FitnessRule], list[str], list[str]]:
    """Load the project's configured fitness functions.

    Sources: the manifest's ``fitness_functions:`` block and any
    ``fitness_functions.yaml`` / ``fitness_functions.json`` in ``spec_dir``
    (the spec's directory -- where the default manifest also lives).

    Returns ``(rules, sources, errors)``. There are NO built-in rules: with no
    ``fitness_functions:`` block in the manifest and no rules file, this
    returns ``([], [], [])`` and the scanner prints no fitness section at all.
    Config problems land in ``errors`` (surfaced advisorily), never raise.
    """
    rules: list[FitnessRule] = []
    sources: list[str] = []
    errors: list[str] = []

    if isinstance(manifest, dict) and RULES_KEY in manifest:
        sources.append(f"spec_manifest.yaml ({RULES_KEY}:)")
        if not _yaml_available():
            # VAL-01: under a bare python3 the manifest went through the
            # fallback parser, which cannot read flow-style rule leaves --
            # validating the mangled tree would surface a misleading INVALID
            # ("got keys ['{fact']"). Name the real problem instead.
            errors.append(
                f"spec_manifest.yaml: the '{RULES_KEY}:' block needs PyYAML, "
                "which is unavailable under this python -- the fallback "
                "manifest parser cannot read rule leaves. Move the rules to "
                "fitness_functions.json (standard library) next to the spec."
            )
        else:
            parsed, errs = _parse_entries(manifest.get(RULES_KEY), "spec_manifest.yaml")
            rules.extend(parsed)
            errors.extend(errs)

    for filename in RULES_FILENAMES if spec_dir is not None else ():
        rules_path = spec_dir / filename
        if not rules_path.is_file():
            continue
        sources.append(str(rules_path))
        loaded, error = _load_rules_document(rules_path)
        if error is not None:
            errors.append(error)
            continue
        if isinstance(loaded, dict):
            raw = loaded.get(RULES_KEY)
            if raw is None:
                errors.append(f"{rules_path.name}: no '{RULES_KEY}:' key at the root")
            else:
                parsed, errs = _parse_entries(raw, rules_path.name)
                rules.extend(parsed)
                errors.extend(errs)
        elif isinstance(loaded, list):
            parsed, errs = _parse_entries(loaded, rules_path.name)
            rules.extend(parsed)
            errors.extend(errs)
        elif loaded is not None:
            errors.append(
                f"{rules_path.name}: root must be a mapping with "
                f"'{RULES_KEY}:' or a bare list of rules"
            )
    return rules, sources, errors


# --------------------------------------------------------------------------
# Evaluation report
# --------------------------------------------------------------------------

STATUS_HOLDS = "holds"
STATUS_FIRED = "fired"
STATUS_UNKNOWN = "unknown"
STATUS_INVALID = "invalid"


@dataclass
class RuleResult:
    name: str
    status: str
    detail: str
    description: str = ""


@dataclass
class FitnessReport:
    sources: list[str] = field(default_factory=list)
    results: list[RuleResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def fired(self) -> list[RuleResult]:
        return [r for r in self.results if r.status == STATUS_FIRED]

    @property
    def configured(self) -> int:
        return len(self.results)


def evaluate_rules(
    rules: Sequence[FitnessRule],
    facts: dict[str, Any],
    *,
    sources: Iterable[str] = (),
    errors: Iterable[str] = (),
) -> FitnessReport:
    results: list[RuleResult] = []
    for rule in rules:
        try:
            value, notes = evaluate_node(rule.rule, facts)
        except RuleError as exc:
            results.append(
                RuleResult(rule.name, STATUS_INVALID, str(exc), rule.description)
            )
            continue
        if value is True:
            status = STATUS_HOLDS
        elif value is False:
            status = STATUS_FIRED
        else:
            status = STATUS_UNKNOWN
        results.append(
            RuleResult(rule.name, status, "; ".join(notes), rule.description)
        )
    return FitnessReport(sources=list(sources), results=results, errors=list(errors))


def run_fitness(
    manifest: dict[str, Any] | None,
    spec_dir: Path | None,
    descriptor: dict[str, Any],
) -> FitnessReport | None:
    """One-call entry point for the scanner.

    Returns ``None`` when the project configured nothing (no rules, no config
    errors) -- the caller then prints no fitness section at all, because there
    are no built-in rules. Never raises; never influences any exit code.
    """
    rules, sources, errors = load_rules(manifest, spec_dir)
    if not rules and not errors:
        return None
    facts = extract_facts(descriptor)
    return evaluate_rules(rules, facts, sources=sources, errors=errors)
