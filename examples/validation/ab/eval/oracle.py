"""The stable-controls oracle. ONE copy, every tree it is pointed at.

Descended from HP-06's `measure/arm_adapter.py`, which is left exactly as it ran
because the measurement it produced is sealed. This copy exists to make the
CONTROLS readable, and it differs from its ancestor in four places, each of
which is a disclosure rather than a convenience:

1.  **`Reserve` executes.** Its ancestor skipped 100% of positive `Reserve`
    cases for an unrecovered `a`, which is why a fault seeded inside `reserve`
    -- the catalogue's positive control -- survived every generated instrument.
    The repair is generator-side (`scripts/infer_action_params.py`,
    `except-value`) and nothing here compensates for it.

2.  **The reservation id is checked for EXPRESSIBILITY, and cases that fail it
    are skipped with a counted reason.** The model gives `Reserve` a
    reservation id as an ARGUMENT and admits any free one; the feature's API
    ALLOCATES the id and admits none. On a before-state where the model's `r`
    is not the id the API would allocate, the case describes a call this API
    cannot make. Its ancestor never noticed because it never ran a `Reserve`
    case at all; run them, and the whole-view control goes red on UNMUTATED
    code (HP-06-DF-11, predicted before this run).

    Two repairs were available and only one of them is honest. Installing the
    arm's id counter FROM the case's own `r` would run every case -- and would
    configure the program to produce the very id the oracle then compares, which
    is the MF-028 tautology one level down. Skipping keeps "which id was
    allocated" a real check on every case that runs, at the price of a
    DECLARED, COUNTED limitation on the cases that do not. The price is
    reported per action; it is not netted out of anything.

3.  **Executability is counted, per action, per skip rule.** A `SURVIVED` cell
    over an action that never executed is not a measurement, and until this
    file counted them there was no shipped artifact from which a reader could
    tell the two apart (HP-06's F2).

4.  **Failure text is retained for mutated runs, not only for controls.** Its
    ancestor computed it and discarded it (HP-06-DF-12), so no `KILLED` cell it
    produced is attributable to a case or an assertion. These are.

Everything else -- the projections, the comparison, the two self-referential
comparisons its ancestor disclosed in its own docstring -- is carried over
unchanged, including the disclosures:

* The MODEL's commit line is ``<<"COMMIT", tenant, amount>>`` -- it has no
  running total -- while the trees write ``COMMIT <tenant> <amount> <total>``.
  Projecting back into the model DISCARDS the total, so a fault that corrupts
  only the total is invisible to every corpus instrument here. That is the gap
  the `map-checking` column exists to cover.
* On a NEGATIVE case the assertion is refusal plus inertness. The rejection
  REASON is not compared: the case's reason is the model's violated conjunct
  and the tree's reason is its own string.
* `holder` and `amt` are backfilled from the case's own `before` for any id the
  tree does not hold, so for every action but `Reserve` those two fields compare
  the model's before-state against itself (HP-06's F4a). `Reserve` is now the
  one action for which they are a real check, which is the second reason this
  file cares that `Reserve` runs.
"""

from __future__ import annotations

import importlib
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

_binding = importlib.import_module(os.environ["QUOTA_LEDGER_BINDING"])

QUOTA = int(os.environ.get("QUOTA_LEDGER_QUOTA", "2"))

#: Skip rules, named so a count can be attributed to one.
UNBOUND_ACTION = "action has no binding in this API"
UNRECOVERED_ARGUMENT = "unrecovered argument"
REFUSED_ONLY_BY_R = "refused only by a constraint on `r`, which this API allocates"
ID_NOT_EXPRESSIBLE = "model chose a reservation id this API would not allocate"


def _command_type() -> Any:
    module = importlib.import_module("quota_ledger_effects.types")
    return module.AppendLedgerLine


def _decode(line: str) -> dict[str, Any]:
    """`COMMIT <tenant> <amount> <total>` / `CLOSE <tenant> <total>`."""
    parts = line.split()
    kind, tenant = parts[0], parts[1]
    if kind == "COMMIT":
        return {"kind": kind, "tenant": tenant, "amount": int(parts[2]), "total": int(parts[3])}
    total = int(parts[2])
    return {"kind": kind, "tenant": tenant, "amount": total, "total": total}


def _install_port(book: Any, port: Any) -> None:
    command_type = _command_type()
    _binding.install_line_observer(book, lambda line: port.append(command_type(**_decode(line))))


@dataclass
class _Result:
    output: Any = None
    after: Any = None
    semantic_output: Any = None


@dataclass
class Ledger:
    """Per-action accounting for one corpus over one tree.

    Deliberately not a single integer. ``ran`` and ``skipped`` per action are
    what make a `SURVIVED` cell readable; the per-rule breakdown is what makes a
    skip attributable to a stated limitation rather than to silence.
    """

    ran: Counter = field(default_factory=Counter)
    ran_positive: Counter = field(default_factory=Counter)
    failed: Counter = field(default_factory=Counter)
    skipped: Counter = field(default_factory=Counter)
    skipped_by_rule: Counter = field(default_factory=Counter)

    def as_dict(self) -> dict[str, Any]:
        actions = sorted(set(self.ran) | set(self.skipped))
        return {
            "total_ran": sum(self.ran.values()),
            "total_failed": sum(self.failed.values()),
            "total_skipped": sum(self.skipped.values()),
            "per_action": {
                action: {
                    "ran": self.ran.get(action, 0),
                    # Split because "this instrument executed 64 Reserve cases"
                    # and "this instrument executed an ACCEPTED reserve" are
                    # different facts, and a fault on the accept path is decided
                    # only by the second. A declared limitation is checked
                    # against this number rather than believed.
                    "ran_accepting": self.ran_positive.get(action, 0),
                    "ran_refusing": self.ran.get(action, 0) - self.ran_positive.get(action, 0),
                    "failed": self.failed.get(action, 0),
                    "skipped": self.skipped.get(action, 0),
                }
                for action in actions
            },
            "skipped_by_rule": dict(sorted(self.skipped_by_rule.items())),
        }


def _tenants(before: dict[str, Any]) -> list[str]:
    for field_name in ("available", "committed"):
        if field_name in before:
            return sorted(before[field_name])
    return []


def _ids(before: dict[str, Any]) -> list[str]:
    return sorted(before.get("amt", {}))


def _reservations(before: dict[str, Any]) -> list[tuple[str, str, int]]:
    holder = before.get("holder", {})
    amt = before.get("amt", {})
    return [(rid, holder[rid], amt[rid]) for rid in sorted(before.get("live", ()))]


def _next_ordinal(before: dict[str, Any]) -> int:
    """The next id ordinal the tree will allocate. Ids are never reused."""
    highest = 0
    for rid, tenant in before.get("holder", {}).items():
        if tenant == "none":
            continue
        digits = "".join(character for character in rid if character.isdigit())
        if digits:
            highest = max(highest, int(digits))
    return highest + 1


def allocatable_id(before: dict[str, Any]) -> str:
    """The one id this API can be made to allocate from this before-state."""
    return f"r{_next_ordinal(before)}"


def _render_line(entry: Any) -> str:
    kind, tenant, amount = entry
    if kind == "COMMIT":
        return f"COMMIT {tenant} {amount} -"
    return f"CLOSE {tenant} {amount}"


def _build(before: dict[str, Any], work_dir: Path | None, port: Any = None) -> Any:
    root = Path(work_dir) if work_dir is not None else Path(".")
    root.mkdir(parents=True, exist_ok=True)
    ledger_path = root / "ledger.txt"
    book = _binding.make({tenant: QUOTA for tenant in _tenants(before)}, ledger_path)
    _binding.install(
        book,
        committed=dict(before.get("committed", {})),
        closed=set(before.get("closed", ())),
        reservations=_reservations(before),
        next_ordinal=_next_ordinal(before),
    )
    ledger_path.write_text(
        "".join(f"{_render_line(entry)}\n" for entry in before.get("ledger", ())),
        encoding="utf-8",
    )
    if port is not None:
        _install_port(book, port)
    return book


def _as_int(token: str) -> Any:
    try:
        return int(token)
    except ValueError:
        return token


def _project_ledger(book: Any) -> tuple[Any, ...]:
    projected = []
    for line in book.ledger_lines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] in ("COMMIT", "CLOSE") and len(parts) >= 3:
            projected.append((parts[0], parts[1], _as_int(parts[2])))
        else:  # pragma: no cover - a shape the model cannot represent
            projected.append(tuple(parts))
    return tuple(projected)


def _snapshot(book: Any, before: dict[str, Any], result: Any) -> dict[str, Any]:
    tenants = _tenants(before)
    ids = _ids(before)
    live = set(book.outstanding_ids())
    holder: dict[str, Any] = {}
    amt: dict[str, Any] = {}
    for rid in ids:
        found = _binding.reservation(book, rid)
        if found is None:
            holder[rid] = before.get("holder", {}).get(rid, "none")
            amt[rid] = before.get("amt", {}).get(rid, 0)
        else:
            holder[rid], amt[rid] = found
    return {
        "available": {tenant: book.available(tenant) for tenant in tenants},
        "committed": {tenant: book.committed(tenant) for tenant in tenants},
        "closed": frozenset(tenant for tenant in tenants if book.is_closed(tenant)),
        "live": frozenset(live),
        "holder": holder,
        "amt": amt,
        "ledger": _project_ledger(book),
        "status": result.status,
        "reason": result.reason if result.reason is not None else "none",
    }


def _call(book: Any, action: str, params: dict[str, Any]) -> Any:
    if action == "Reserve":
        return book.reserve(params["t"], params["a"])
    if action == "Commit":
        return book.commit(params["r"])
    if action == "Release":
        return book.release(params["r"])
    if action == "CloseTenant":
        return book.close_tenant(params["t"])
    raise AssertionError(f"no binding for action {action!r}")


BOUND_ACTIONS = ("Reserve", "Commit", "Release", "CloseTenant")


def _is_unchecked(value: Any) -> bool:
    return repr(value) == "UNCHECKED"


def _to_projection(snapshot: dict[str, Any], case: Any) -> dict[str, Any]:
    """Compare only the fields the case's own projection carries (HP-06-DF-01)."""
    return {name: value for name, value in snapshot.items() if name in case.after}


class NegativeAdapter:
    """A call the model does not enable: the tree must refuse it."""

    def __init__(self) -> None:
        self.port: Any = None

    def can_run(self, case: Any) -> Any:
        if case.input.action not in BOUND_ACTIONS:
            return False, UNBOUND_ACTION
        if any(_is_unchecked(value) for value in case.input.params.values()):
            # HP-06's F16: the ancestor had no such guard here and would have
            # handed the sentinel to the tree, raising a TypeError that scores
            # as a kill. It never fired; it is closed anyway.
            return False, UNRECOVERED_ARGUMENT
        if case.input.action == "Reserve" and re.search(
            r"(?<![A-Za-z_])r(?![A-Za-z0-9_])", case.output.reason
        ):
            return False, REFUSED_ONLY_BY_R
        return True

    def run(self, case: Any, work_dir: Path | None = None) -> _Result:
        expected = case.output
        book = _build(case.before, work_dir, self.port)
        result = _call(book, case.input.action, dict(case.input.params))
        after = _to_projection(_snapshot(book, case.before, result), case)
        if result.status == "rejected":
            output = type(expected)(
                action=expected.action,
                params=dict(expected.params),
                reason=expected.reason,
                outcome_fields=tuple(expected.outcome_fields),
            )
        else:
            output = ("ACCEPTED", result.status, result.reservation_id)
        return _Result(
            output=output,
            after=after,
            semantic_output={"unobservable": list(expected.outcome_fields)},
        )


class PositiveAdapter:
    """An enabled edge: the tree must take exactly that transition."""

    def __init__(self) -> None:
        self.port: Any = None

    def can_run(self, case: Any) -> Any:
        if case.input.action not in BOUND_ACTIONS:
            return False, UNBOUND_ACTION
        if any(_is_unchecked(value) for value in case.input.params.values()):
            unchecked = sorted(
                name for name, value in case.input.params.items() if _is_unchecked(value)
            )
            return False, f"{UNRECOVERED_ARGUMENT} ({', '.join(unchecked)})"
        if case.input.action == "Reserve":
            chosen = case.input.params.get("r")
            if chosen is not None and chosen != allocatable_id(case.before):
                # HP-03-DF-01 / HP-06-DF-11, and the whole reason this file
                # exists. The model admits ANY free id; this API allocates one
                # and accepts none, so a case naming a different one is not a
                # call this API can make. NOT a defect of the tree, NOT a fault
                # the corpus caught, and NOT netted out of anything: it is a
                # counted limitation of the fixture's own refinement.
                return False, ID_NOT_EXPRESSIBLE
        return True

    def run(self, case: Any, work_dir: Path | None = None) -> _Result:
        book = _build(case.before, work_dir, self.port)
        params = dict(case.input.params)
        for name, value in params.items():
            if _is_unchecked(value):
                raise AssertionError(f"unrecovered argument {name!r} for {case.name}")
        result = _call(book, case.input.action, params)
        after = _to_projection(_snapshot(book, case.before, result), case)
        return _Result(output=None, after=after, semantic_output={"unobservable": []})
