#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "PyYAML>=6.0.2,<7",
# ]
# ///
"""Validate scheduling metadata in an epic ticket plan."""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Any, Sequence

import yaml


DEFAULT_PLAN = Path("specs/desired_program_model/ticket_plan.yaml")
STABLE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
MISSING = object()
DEFERMENT_MODES = ("batch", "ask", "inline")
DEFERMENT_BLOCKING = ("escalate", "ask")
GOAL_KINDS = ("perf", "eval", "integration", "quality")
GOAL_TEXT_FIELDS = ("statement", "metric", "harness", "target", "evidence_root")
CONTRIBUTIONS = ("direct", "enabling", "guard")
TICKET_ROLES = ("implementation", "evaluation")
EVALUATION = "evaluation"
UNMEASURED = "unmeasured"


@dataclass(frozen=True)
class PlanReport:
    errors: list[str]
    warnings: list[str]


@dataclass(frozen=True)
class GoalLink:
    goal: str
    contribution: str | None
    local_signal: str | None


@dataclass(frozen=True)
class Goal:
    id: str
    evaluation_ticket: object
    baseline_value: str | None


@dataclass(frozen=True)
class Ticket:
    id: str
    depends_on: tuple[str, ...]
    blocks: tuple[str, ...]
    wave: int | None
    promotion_order: int | None
    promotion_predecessor: object
    conflict_keys: frozenset[tuple[str, str]]
    role: str
    goals: tuple[GoalLink, ...]
    owns_goals: object


def _ticket_label(index: int, raw_id: object) -> str:
    if isinstance(raw_id, str) and raw_id:
        return f"ticket {raw_id!r}"
    return f"ticket at index {index}"


def _id_list(
    raw: dict[str, Any], field: str, label: str, errors: list[str]
) -> tuple[str, ...]:
    value = raw.get(field, MISSING)
    if not isinstance(value, list):
        errors.append(f"{label}: {field} must be a list")
        return ()

    result: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not STABLE_ID.fullmatch(item):
            errors.append(
                f"{label}: {field}[{index}] must be a stable ticket ID "
                "using only letters, digits, '.', '_' or '-'"
            )
            continue
        result.append(item)

    duplicates = sorted({item for item in result if result.count(item) > 1})
    if duplicates:
        errors.append(f"{label}: {field} contains duplicate IDs: {duplicates}")
    return tuple(result)


def _conflict_keys(
    raw: dict[str, Any], label: str, errors: list[str]
) -> frozenset[tuple[str, str]]:
    value = raw.get("conflict_keys", MISSING)
    if not isinstance(value, dict):
        errors.append(f"{label}: conflict_keys must be a mapping of lists")
        return frozenset()

    result: set[tuple[str, str]] = set()
    for category, keys in value.items():
        if not isinstance(category, str) or not category.strip():
            errors.append(f"{label}: conflict_keys categories must be non-empty strings")
            continue
        if not isinstance(keys, list):
            errors.append(f"{label}: conflict_keys.{category} must be a list")
            continue
        seen: set[str] = set()
        for index, key in enumerate(keys):
            if not isinstance(key, str) or not key.strip():
                errors.append(
                    f"{label}: conflict_keys.{category}[{index}] must be a "
                    "non-empty string"
                )
                continue
            if key in seen:
                errors.append(
                    f"{label}: conflict_keys.{category} contains duplicate key {key!r}"
                )
            seen.add(key)
            result.add((category, key))
    return frozenset(result)


def _goal_links(
    raw: dict[str, Any], label: str, errors: list[str]
) -> tuple[GoalLink, ...]:
    value = raw.get("goals", MISSING)
    if value is MISSING:
        return ()
    if not isinstance(value, list):
        errors.append(f"{label}: goals must be a list of goal relations")
        return ()

    links: list[GoalLink] = []
    seen: set[str] = set()
    for index, entry in enumerate(value):
        entry_label = f"{label}: goals[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{entry_label} must be a mapping")
            continue

        goal_id = entry.get("goal", MISSING)
        if not isinstance(goal_id, str) or not STABLE_ID.fullmatch(goal_id):
            errors.append(f"{entry_label}: goal must be a stable goal ID")
            continue
        if goal_id in seen:
            errors.append(f"{entry_label}: duplicate relation to goal {goal_id!r}")
            continue
        seen.add(goal_id)

        contribution = entry.get("contribution", MISSING)
        if contribution not in CONTRIBUTIONS:
            errors.append(
                f"{entry_label}: contribution must be one of {list(CONTRIBUTIONS)}"
            )
            contribution = None

        effect = entry.get("expected_effect", MISSING)
        if not isinstance(effect, str) or not effect.strip():
            errors.append(
                f"{entry_label}: expected_effect must state the result this ticket "
                "should produce, or 'none — enabling only'"
            )

        signal = entry.get("local_signal", MISSING)
        if not isinstance(signal, str) or not signal.strip():
            errors.append(
                f"{entry_label}: local_signal must be a command or 'N/A: <reason>'"
            )
            signal = None

        links.append(
            GoalLink(
                goal=goal_id,
                contribution=contribution if isinstance(contribution, str) else None,
                local_signal=signal if isinstance(signal, str) else None,
            )
        )
    return tuple(links)


def _parse_tickets(plan: object, errors: list[str]) -> dict[str, Ticket]:
    if not isinstance(plan, dict):
        errors.append("plan root must be a mapping")
        return {}
    raw_tickets = plan.get("tickets")
    if not isinstance(raw_tickets, list) or not raw_tickets:
        errors.append("plan must contain a non-empty tickets list")
        return {}

    tickets: dict[str, Ticket] = {}
    for index, raw in enumerate(raw_tickets):
        if not isinstance(raw, dict):
            errors.append(f"ticket at index {index} must be a mapping")
            continue

        raw_id = raw.get("id", MISSING)
        label = _ticket_label(index, raw_id)
        if not isinstance(raw_id, str) or not STABLE_ID.fullmatch(raw_id):
            errors.append(
                f"{label}: id must be a stable string using only letters, digits, "
                "'.', '_' or '-' and must start with a letter or digit"
            )
            continue
        if raw_id in tickets:
            errors.append(f"duplicate ticket ID {raw_id!r}")
            continue

        wave = raw.get("wave", MISSING)
        if type(wave) is not int or wave < 1:
            errors.append(f"{label}: wave must be a positive integer")
            parsed_wave = None
        else:
            parsed_wave = wave

        promotion_order = raw.get("promotion_order", MISSING)
        if type(promotion_order) is not int:
            errors.append(f"{label}: promotion_order must be an integer")
            parsed_order = None
        else:
            parsed_order = promotion_order

        predecessor = raw.get("promotion_predecessor", MISSING)
        if predecessor is not MISSING and predecessor is not None:
            if not isinstance(predecessor, str) or not STABLE_ID.fullmatch(predecessor):
                errors.append(
                    f"{label}: promotion_predecessor must be null or a stable ticket ID"
                )

        role = raw.get("role", "implementation")
        if role not in TICKET_ROLES:
            errors.append(f"{label}: role must be one of {list(TICKET_ROLES)}")
            role = "implementation"

        tickets[raw_id] = Ticket(
            id=raw_id,
            depends_on=_id_list(raw, "depends_on", label, errors),
            blocks=_id_list(raw, "blocks", label, errors),
            wave=parsed_wave,
            promotion_order=parsed_order,
            promotion_predecessor=predecessor,
            conflict_keys=_conflict_keys(raw, label, errors),
            role=role,
            goals=_goal_links(raw, label, errors),
            owns_goals=raw.get("owns_goals", MISSING),
        )
    return tickets


def _find_dependency_cycle(tickets: dict[str, Ticket]) -> list[str] | None:
    state = {ticket_id: 0 for ticket_id in tickets}
    stack: list[str] = []

    def visit(ticket_id: str) -> list[str] | None:
        state[ticket_id] = 1
        stack.append(ticket_id)
        for dependency in sorted(tickets[ticket_id].depends_on):
            if dependency not in tickets:
                continue
            if state[dependency] == 0:
                cycle = visit(dependency)
                if cycle:
                    return cycle
            elif state[dependency] == 1:
                start = stack.index(dependency)
                return stack[start:] + [dependency]
        stack.pop()
        state[ticket_id] = 2
        return None

    for ticket_id in sorted(tickets):
        if state[ticket_id] == 0:
            cycle = visit(ticket_id)
            if cycle:
                return cycle
    return None


def _validate_dependency_graph(tickets: dict[str, Ticket], errors: list[str]) -> None:
    expected_blocks: dict[str, set[str]] = {ticket_id: set() for ticket_id in tickets}

    for ticket in tickets.values():
        for dependency in ticket.depends_on:
            if dependency == ticket.id:
                errors.append(f"ticket {ticket.id!r}: cannot depend on itself")
            elif dependency not in tickets:
                errors.append(
                    f"ticket {ticket.id!r}: depends_on references unknown ticket "
                    f"{dependency!r}"
                )
            else:
                expected_blocks[dependency].add(ticket.id)
                dependency_ticket = tickets[dependency]
                if (
                    ticket.wave is not None
                    and dependency_ticket.wave is not None
                    and dependency_ticket.wave >= ticket.wave
                ):
                    errors.append(
                        f"ticket {ticket.id!r}: dependency {dependency!r} is in wave "
                        f"{dependency_ticket.wave}, which is not earlier than wave "
                        f"{ticket.wave}"
                    )

        for blocked in ticket.blocks:
            if blocked == ticket.id:
                errors.append(f"ticket {ticket.id!r}: cannot block itself")
            elif blocked not in tickets:
                errors.append(
                    f"ticket {ticket.id!r}: blocks references unknown ticket {blocked!r}"
                )

    for ticket in tickets.values():
        actual = set(ticket.blocks)
        expected = expected_blocks[ticket.id]
        if actual != expected:
            errors.append(
                f"ticket {ticket.id!r}: blocks must be the exact reverse of "
                f"depends_on; expected {sorted(expected)}, got {sorted(actual)}"
            )

    cycle = _find_dependency_cycle(tickets)
    if cycle:
        errors.append(f"dependency cycle detected: {' -> '.join(cycle)}")


def _validate_conflicts(tickets: dict[str, Ticket], errors: list[str]) -> None:
    by_wave: dict[int, list[Ticket]] = defaultdict(list)
    for ticket in tickets.values():
        if ticket.wave is not None:
            by_wave[ticket.wave].append(ticket)

    for wave, wave_tickets in sorted(by_wave.items()):
        ordered = sorted(wave_tickets, key=lambda ticket: ticket.id)
        for left_index, left in enumerate(ordered):
            for right in ordered[left_index + 1 :]:
                overlap = sorted(left.conflict_keys & right.conflict_keys)
                if overlap:
                    rendered = [f"{category}:{key}" for category, key in overlap]
                    errors.append(
                        f"wave {wave}: tickets {left.id!r} and {right.id!r} share "
                        f"conflict keys {rendered}"
                    )


def _render_predecessor(value: object) -> str:
    if value is MISSING:
        return "<missing>"
    return repr(value)


def _validate_promotion_lane(tickets: dict[str, Ticket], errors: list[str]) -> None:
    orders: dict[int, list[str]] = defaultdict(list)
    for ticket in tickets.values():
        if ticket.promotion_order is not None:
            orders[ticket.promotion_order].append(ticket.id)
        predecessor = ticket.promotion_predecessor
        if isinstance(predecessor, str):
            if predecessor == ticket.id:
                errors.append(
                    f"ticket {ticket.id!r}: promotion_predecessor cannot name itself"
                )
            elif predecessor not in tickets:
                errors.append(
                    f"ticket {ticket.id!r}: promotion_predecessor references unknown "
                    f"ticket {predecessor!r}"
                )

    duplicate_orders = {
        order: sorted(ticket_ids)
        for order, ticket_ids in orders.items()
        if len(ticket_ids) > 1
    }
    for order, ticket_ids in sorted(duplicate_orders.items()):
        errors.append(
            f"promotion_order {order} is not unique; used by tickets {ticket_ids}"
        )

    for ticket in tickets.values():
        if ticket.promotion_order is None:
            continue
        for dependency in ticket.depends_on:
            dependency_ticket = tickets.get(dependency)
            if dependency_ticket is None or dependency_ticket.promotion_order is None:
                continue
            if dependency_ticket.promotion_order >= ticket.promotion_order:
                errors.append(
                    "promotion_order is not a topological extension: dependency "
                    f"{dependency!r} ({dependency_ticket.promotion_order}) must precede "
                    f"ticket {ticket.id!r} ({ticket.promotion_order})"
                )

    if len(orders) != len(tickets) or duplicate_orders:
        return

    lane = sorted(tickets.values(), key=lambda ticket: ticket.promotion_order)  # type: ignore[arg-type]
    for index, ticket in enumerate(lane):
        expected = None if index == 0 else lane[index - 1].id
        actual = ticket.promotion_predecessor
        if actual is MISSING:
            errors.append(
                f"ticket {ticket.id!r}: promotion_predecessor is required; "
                f"expected {_render_predecessor(expected)}"
            )
        elif actual != expected:
            errors.append(
                f"ticket {ticket.id!r}: promotion_predecessor must be "
                f"{_render_predecessor(expected)}; got {_render_predecessor(actual)}"
            )


def _baseline_value(
    raw: object, label: str, errors: list[str]
) -> str | None:
    """Accept either a `{value: ...}` mapping or a bare measured string."""
    if raw is MISSING or raw is None:
        return None
    if isinstance(raw, str):
        return raw.strip() or None
    if not isinstance(raw, dict):
        errors.append(f"{label}: baseline must be a mapping with a value, or a string")
        return None
    value = raw.get("value")
    if not isinstance(value, str) or not value.strip():
        return None
    return value.strip()


def _parse_goals(
    plan: object, errors: list[str], warnings: list[str]
) -> dict[str, Goal]:
    """Goals are agreed with the user, so their absence warns rather than fails."""
    if not isinstance(plan, dict):
        return {}

    raw_goals = plan.get("epic_goals", MISSING)
    if raw_goals is MISSING or raw_goals == []:
        waiver = plan.get("goals_waived", MISSING)
        if isinstance(waiver, str) and waiver.strip():
            warnings.append(
                f"epic_goals is waived: {waiver.strip()}; no evaluation ticket will "
                "decide this epic's outcome"
            )
        else:
            warnings.append(
                "plan declares no epic_goals; ask the user what should be measurably "
                "better, add the evaluation/perf ticket that decides it, and relate "
                "every ticket to it (see references/goals-and-evaluation.md)"
            )
        return {}

    if not isinstance(raw_goals, list):
        errors.append("epic_goals must be a list of goals")
        return {}

    goals: dict[str, Goal] = {}
    for index, raw in enumerate(raw_goals):
        label = f"epic_goals[{index}]"
        if not isinstance(raw, dict):
            errors.append(f"{label} must be a mapping")
            continue

        goal_id = raw.get("id", MISSING)
        if not isinstance(goal_id, str) or not STABLE_ID.fullmatch(goal_id):
            errors.append(f"{label}: id must be a stable goal ID")
            continue
        if goal_id in goals:
            errors.append(f"duplicate goal ID {goal_id!r}")
            continue
        label = f"goal {goal_id!r}"

        if raw.get("kind", MISSING) not in GOAL_KINDS:
            errors.append(f"{label}: kind must be one of {list(GOAL_KINDS)}")
        for field in GOAL_TEXT_FIELDS:
            value = raw.get(field, MISSING)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label}: {field} must be a non-empty string")

        baseline = _baseline_value(raw.get("baseline", MISSING), label, errors)
        if baseline is None or baseline.lower() == UNMEASURED:
            warnings.append(
                f"{label}: baseline is unmeasured; measure it on the epic branch "
                "before behavioral tickets land, or schedule a wave-1 harness ticket"
            )
            baseline = None

        evaluation_ticket = raw.get("evaluation_ticket", MISSING)
        if evaluation_ticket is MISSING or not isinstance(evaluation_ticket, str):
            errors.append(
                f"{label}: evaluation_ticket must name the ticket that decides this goal"
            )

        goals[goal_id] = Goal(
            id=goal_id,
            evaluation_ticket=evaluation_ticket,
            baseline_value=baseline,
        )
    return goals


def _ancestors(tickets: dict[str, Ticket], start: str) -> set[str]:
    """Tickets `start` transitively depends on; cycle-safe."""
    seen: set[str] = set()
    stack = [start]
    while stack:
        current = stack.pop()
        ticket = tickets.get(current)
        if ticket is None:
            continue
        for dependency in ticket.depends_on:
            if dependency in seen or dependency not in tickets:
                continue
            seen.add(dependency)
            stack.append(dependency)
    return seen


def _validate_owns_goals(
    ticket: Ticket, goals: dict[str, Goal], errors: list[str]
) -> None:
    if ticket.owns_goals is MISSING:
        return
    if not isinstance(ticket.owns_goals, list):
        errors.append(f"ticket {ticket.id!r}: owns_goals must be a list of goal IDs")
        return
    for goal_id in ticket.owns_goals:
        if not isinstance(goal_id, str) or goal_id not in goals:
            errors.append(
                f"ticket {ticket.id!r}: owns_goals references unknown goal {goal_id!r}"
            )
            continue
        if goals[goal_id].evaluation_ticket != ticket.id:
            errors.append(
                f"ticket {ticket.id!r}: owns_goals lists {goal_id!r}, but that goal's "
                f"evaluation_ticket is {goals[goal_id].evaluation_ticket!r}"
            )
    owned = {
        goal.id for goal in goals.values() if goal.evaluation_ticket == ticket.id
    }
    declared = {goal for goal in ticket.owns_goals if isinstance(goal, str)}
    missing = sorted(owned - declared)
    if missing:
        errors.append(
            f"ticket {ticket.id!r}: owns_goals must list every goal it decides; "
            f"missing {missing}"
        )


def _validate_goal_alignment(
    goals: dict[str, Goal],
    tickets: dict[str, Ticket],
    errors: list[str],
    warnings: list[str],
) -> None:
    if not goals:
        return

    has_evaluation_ticket = any(
        ticket.role == EVALUATION for ticket in tickets.values()
    )
    if not has_evaluation_ticket:
        warnings.append(
            "no ticket declares role: evaluation; schedule a terminal "
            "evaluation/perf/integration ticket that runs each goal harness on the "
            "integrated epic and decides it"
        )

    contributors: dict[str, list[Ticket]] = defaultdict(list)
    for ticket in sorted(tickets.values(), key=lambda item: item.id):
        _validate_owns_goals(ticket, goals, errors)

        if not ticket.goals:
            errors.append(
                f"ticket {ticket.id!r}: must relate to at least one epic goal so its "
                "agent knows which measured outcome the work serves"
            )
            continue

        for link in ticket.goals:
            if link.goal not in goals:
                errors.append(
                    f"ticket {ticket.id!r}: goals references unknown goal {link.goal!r}"
                )
                continue
            if link.contribution == "direct":
                if ticket.role != EVALUATION and (
                    link.local_signal is None
                    or link.local_signal.strip().upper().startswith("N/A")
                ):
                    warnings.append(
                        f"ticket {ticket.id!r}: direct contribution to {link.goal!r} "
                        "has no local signal; the agent cannot tell whether its change "
                        "moved the metric until finalization"
                    )
            # A goal's own decider never counts as a contributor to it, even when
            # the plan has not marked its role yet.
            if (
                ticket.role != EVALUATION
                and goals[link.goal].evaluation_ticket != ticket.id
            ):
                contributors[link.goal].append(ticket)

    for goal_id, goal in sorted(goals.items()):
        goal_contributors = contributors.get(goal_id, [])
        if not goal_contributors:
            errors.append(
                f"goal {goal_id!r}: no implementation ticket contributes to it; "
                "schedule the work or drop the goal"
            )

        evaluator_id = goal.evaluation_ticket
        if not isinstance(evaluator_id, str):
            continue
        evaluator = tickets.get(evaluator_id)
        if evaluator is None:
            errors.append(
                f"goal {goal_id!r}: evaluation_ticket references unknown ticket "
                f"{evaluator_id!r}"
            )
            continue
        if evaluator.role != EVALUATION and has_evaluation_ticket:
            errors.append(
                f"goal {goal_id!r}: evaluation_ticket {evaluator_id!r} must declare "
                "role: evaluation"
            )

        evaluator_ancestors = _ancestors(tickets, evaluator_id)
        for contributor in goal_contributors:
            if contributor.id not in evaluator_ancestors:
                errors.append(
                    f"goal {goal_id!r}: evaluation ticket {evaluator_id!r} must depend "
                    f"on contributor {contributor.id!r}, directly or transitively, so "
                    "the measurement runs on the integrated result"
                )
            if (
                evaluator.promotion_order is not None
                and contributor.promotion_order is not None
                and evaluator.promotion_order <= contributor.promotion_order
            ):
                errors.append(
                    f"goal {goal_id!r}: evaluation ticket {evaluator_id!r} "
                    f"({evaluator.promotion_order}) must promote after contributor "
                    f"{contributor.id!r} ({contributor.promotion_order})"
                )


def _validate_deferment_policy(plan: object, errors: list[str]) -> None:
    """The policy is agreed with the user at epic creation, so require it here."""
    if not isinstance(plan, dict):
        return

    policy = plan.get("deferment_policy", MISSING)
    if policy is MISSING:
        errors.append(
            "plan must declare deferment_policy; agree the failure-case policy "
            "with the user before dispatch (see references/deferment.md)"
        )
        return
    if not isinstance(policy, dict):
        errors.append("deferment_policy must be a mapping")
        return

    mode = policy.get("mode", MISSING)
    if mode not in DEFERMENT_MODES:
        errors.append(
            f"deferment_policy.mode must be one of {list(DEFERMENT_MODES)}"
        )

    blocking = policy.get("blocking", MISSING)
    if blocking not in DEFERMENT_BLOCKING:
        errors.append(
            f"deferment_policy.blocking must be one of {list(DEFERMENT_BLOCKING)}"
        )

    budget = policy.get("budget", MISSING)
    if type(budget) is not int or budget < 1:
        errors.append("deferment_policy.budget must be a positive integer")

    backlog = policy.get("backlog", MISSING)
    if not isinstance(backlog, str) or not backlog.strip():
        errors.append("deferment_policy.backlog must be a non-empty path string")


def validate_plan(plan: object) -> PlanReport:
    """Return deterministic diagnostics; no errors means the plan is valid.

    Warnings never fail the plan: a missing goal set or evaluation ticket is a
    conversation to have with the epic owner, not a schema violation.
    """
    errors: list[str] = []
    warnings: list[str] = []
    _validate_deferment_policy(plan, errors)
    goals = _parse_goals(plan, errors, warnings)
    tickets = _parse_tickets(plan, errors)
    if not tickets:
        return PlanReport(errors=errors, warnings=warnings)
    _validate_dependency_graph(tickets, errors)
    _validate_conflicts(tickets, errors)
    _validate_promotion_lane(tickets, errors)
    _validate_goal_alignment(goals, tickets, errors, warnings)
    return PlanReport(errors=errors, warnings=warnings)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate dependency, wave, conflict, and promotion metadata in an epic ticket plan."
    )
    parser.add_argument(
        "plan",
        nargs="?",
        type=Path,
        default=DEFAULT_PLAN,
        help=f"ticket plan YAML (default: {DEFAULT_PLAN})",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        with args.plan.open("r", encoding="utf-8") as plan_file:
            plan = yaml.safe_load(plan_file)
    except OSError as error:
        print(f"ERROR: cannot read {args.plan}: {error}", file=sys.stderr)
        return 2
    except yaml.YAMLError as error:
        print(f"ERROR: invalid YAML in {args.plan}: {error}", file=sys.stderr)
        return 2

    report = validate_plan(plan)
    for warning in report.warnings:
        print(f"WARNING: {warning}", file=sys.stderr)

    if report.errors:
        print(f"INVALID: {args.plan}", file=sys.stderr)
        for error in report.errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    ticket_count = len(plan["tickets"])
    wave_count = len({ticket["wave"] for ticket in plan["tickets"]})
    goal_count = len(plan.get("epic_goals") or [])
    goal_label = "goal" if goal_count == 1 else "goals"
    print(
        f"OK: {args.plan} has a valid epic schedule "
        f"({ticket_count} tickets across {wave_count} waves, "
        f"{goal_count} {goal_label})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
