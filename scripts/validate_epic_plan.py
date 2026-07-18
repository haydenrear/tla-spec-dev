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


@dataclass(frozen=True)
class Ticket:
    id: str
    depends_on: tuple[str, ...]
    blocks: tuple[str, ...]
    wave: int | None
    promotion_order: int | None
    promotion_predecessor: object
    conflict_keys: frozenset[tuple[str, str]]


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

        tickets[raw_id] = Ticket(
            id=raw_id,
            depends_on=_id_list(raw, "depends_on", label, errors),
            blocks=_id_list(raw, "blocks", label, errors),
            wave=parsed_wave,
            promotion_order=parsed_order,
            promotion_predecessor=predecessor,
            conflict_keys=_conflict_keys(raw, label, errors),
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


def validate_plan(plan: object) -> list[str]:
    """Return deterministic diagnostics; an empty list means the plan is valid."""
    errors: list[str] = []
    _validate_deferment_policy(plan, errors)
    tickets = _parse_tickets(plan, errors)
    if not tickets:
        return errors
    _validate_dependency_graph(tickets, errors)
    _validate_conflicts(tickets, errors)
    _validate_promotion_lane(tickets, errors)
    return errors


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

    errors = validate_plan(plan)
    if errors:
        print(f"INVALID: {args.plan}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    ticket_count = len(plan["tickets"])
    wave_count = len({ticket["wave"] for ticket in plan["tickets"]})
    print(
        f"OK: {args.plan} has a valid epic schedule "
        f"({ticket_count} tickets across {wave_count} waves)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
