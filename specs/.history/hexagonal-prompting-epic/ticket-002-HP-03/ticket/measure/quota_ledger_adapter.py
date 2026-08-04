"""Adapters binding the QuotaLedger corpus to a real implementation.

Ticket-local (``specs/tickets/**`` is out of the modeled representation scope):
this is the INSTRUMENT HP-03 measures with, not shipped toolchain surface.

It maps the model's nine variables onto the reference implementation's private
state, dispatches one call, and projects the result back into the model's
vocabulary so the shipped runner's per-field comparison can do the judging.

TWO ORACLES ARE DELIBERATELY NOT CLAIMED, and a run that forgets to say so
over-reads its own numbers:

* The MODEL's ledger line for a commit is ``<<"COMMIT", tenant, amount>>`` --
  it carries no running total -- while the implementation writes
  ``COMMIT <tenant> <amount> <total>``. Projecting the implementation back into
  the model therefore DISCARDS the total, so any fault that corrupts only the
  total is invisible here. That is a limit of the model, not of the corpus.
* The model's ``ledger`` is a sequence and the projection preserves order, so
  ordering IS compared -- but only over the fields the model carries.

For a NEGATIVE case the assertion is refusal plus inertness. ``status`` and
``reason`` are declared unobservable, because a real refusal legitimately
writes them and the case's ``outcome_fields`` says which those are. The refusal
itself is judged by the output comparison; the rejection REASON is not compared
at all -- the case's reason is the model's violated conjunct, in TLA+, and the
implementation's reason is its own string. Copying the model's reason through
on a refusal is what makes the outputs comparable; it is recorded here rather
than hidden, because a check that compares a value against itself proves
nothing and MF-028 lost a whole spike to exactly that.
"""

from __future__ import annotations

import importlib
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_IMPL_DIR = os.environ.get("QUOTA_LEDGER_DIR")
if _IMPL_DIR and _IMPL_DIR not in sys.path:
    sys.path.insert(0, _IMPL_DIR)
_impl = importlib.import_module(os.environ.get("QUOTA_LEDGER_IMPL", "quota_ledger"))

QUOTA = int(os.environ.get("QUOTA_LEDGER_QUOTA", "2"))


@dataclass
class _Result:
    output: Any = None
    after: Any = None
    semantic_output: Any = None


def _tenants(before: dict[str, Any]) -> list[str]:
    return sorted(before.get("available", {}))


def _build(before: dict[str, Any], work_dir: Path | None) -> Any:
    root = Path(work_dir) if work_dir is not None else Path(".")
    root.mkdir(parents=True, exist_ok=True)
    ledger_path = root / "ledger.txt"
    book = _impl.QuotaLedger({tenant: QUOTA for tenant in _tenants(before)}, ledger_path)
    book._available = dict(before["available"])
    book._committed = dict(before["committed"])
    book._closed = set(before["closed"])
    book._outstanding = {
        rid: _impl.Reservation(id=rid, tenant=before["holder"][rid], amount=before["amt"][rid])
        for rid in sorted(before["live"])
    }
    # Ids are never reused in the model, so the next one must not collide with
    # a holder the before-state already records.
    used = [rid for rid in before.get("holder", {}) if before["holder"][rid] != "none"]
    highest = 0
    for rid in used:
        digits = "".join(character for character in rid if character.isdigit())
        if digits:
            highest = max(highest, int(digits))
    book._next_id = highest + 1
    ledger_path.write_text(
        "".join(f"{_render_line(entry)}\n" for entry in before.get("ledger", ())),
        encoding="utf-8",
    )
    return book


def _render_line(entry: Any) -> str:
    kind, tenant, amount = entry
    if kind == "COMMIT":
        # The model's COMMIT line has no running total; the implementation's
        # does. A placeholder keeps the projection round-trippable without
        # inventing a total the model never stated.
        return f"COMMIT {tenant} {amount} -"
    return f"CLOSE {tenant} {amount}"


def _project_ledger(book: Any) -> tuple[Any, ...]:
    projected = []
    for line in book.ledger_lines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "COMMIT" and len(parts) >= 3:
            projected.append(("COMMIT", parts[1], _as_int(parts[2])))
        elif parts[0] == "CLOSE" and len(parts) >= 3:
            projected.append(("CLOSE", parts[1], _as_int(parts[2])))
        else:  # pragma: no cover - a shape the model cannot represent
            projected.append(tuple(parts))
    return tuple(projected)


def _as_int(token: str) -> Any:
    try:
        return int(token)
    except ValueError:
        return token


def _snapshot(book: Any, before: dict[str, Any], result: Any) -> dict[str, Any]:
    tenants = _tenants(before)
    ids = sorted(before.get("amt", {}))
    outstanding = book._outstanding
    return {
        "available": {tenant: book.available(tenant) for tenant in tenants},
        "committed": {tenant: book.committed(tenant) for tenant in tenants},
        "closed": frozenset(tenant for tenant in tenants if book.is_closed(tenant)),
        "live": frozenset(outstanding),
        "holder": {
            rid: (outstanding[rid].tenant if rid in outstanding else before["holder"].get(rid, "none"))
            for rid in ids
        },
        "amt": {
            rid: (outstanding[rid].amount if rid in outstanding else before["amt"].get(rid, 0))
            for rid in ids
        },
        "ledger": _project_ledger(book),
        "status": result.status,
        "reason": result.reason if result.reason is not None else "none",
    }


def _call(book: Any, action: str, params: dict[str, Any], before: dict[str, Any]) -> Any:
    if action == "Reserve":
        return book.reserve(params["t"], params["a"])
    if action == "Commit":
        return book.commit(params["r"])
    if action == "Release":
        return book.release(params["r"])
    if action == "CloseTenant":
        return book.close_tenant(params["t"])
    raise AssertionError(f"no binding for action {action!r}")


class NegativeAdapter:
    """A call the model does not enable: the implementation must refuse it."""

    def can_run(self, case: Any) -> Any:
        if case.input.action not in ("Reserve", "Commit", "Release", "CloseTenant"):
            return False, f"no binding for {case.input.action}"
        if case.input.action == "Reserve" and re.search(r"(?<![A-Za-z_])r(?![A-Za-z0-9_])", case.output.reason):
            # HP-03-DF-01, and the negative corpus is what found it. The model
            # gives Reserve a reservation id as an ARGUMENT
            # (`Reserve(t, a, r)`, guarded by `r \notin live` and
            # `holder[r] = NoTenant`), while FEATURE.md's API is
            # `reserve(tenant, amount)` and the implementation ALLOCATES the id.
            # So a case refused solely by a constraint on `r` asserts the
            # rejection of a call this API cannot express: there is no argument
            # to make stale. Four of these are accepted by the UNMUTATED
            # reference, which is a red control, not a kill -- they are skipped
            # here and reported, never counted.
            return False, "refused only by a constraint on `r`, which this API allocates rather than accepts"
        return True

    def run(self, case: Any, work_dir: Path | None = None) -> _Result:
        expected = case.output
        book = _build(case.before, work_dir)
        result = _call(book, case.input.action, dict(case.input.params), case.before)
        after = _snapshot(book, case.before, result)
        if result.status == "rejected":
            # Comparable-by-construction: the refusal is the oracle, the reason
            # string is not. See the module docstring.
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
    """An enabled edge: the implementation must take exactly that transition."""

    def can_run(self, case: Any) -> Any:
        if case.input.action not in ("Reserve", "Commit", "Release", "CloseTenant"):
            # The fixture's Refuse* actions take (t, a, r) and use none of them,
            # so nothing recovers their arguments and every one of their cases
            # carries `params={}`. There is no call to make. This is the cost of
            # spelling refusals out as their own actions, measured rather than
            # asserted -- see specs/tickets/HP-03/results/.
            return False, f"{case.input.action} is a modeled refusal with no recoverable argument"
        if any(_is_unchecked(value) for value in case.input.params.values()):
            unchecked = sorted(name for name, value in case.input.params.items() if _is_unchecked(value))
            return False, f"unrecovered argument(s) {', '.join(unchecked)}"
        return True

    def run(self, case: Any, work_dir: Path | None = None) -> _Result:
        book = _build(case.before, work_dir)
        params = dict(case.input.params)
        unobservable: list[str] = []
        result = _call(book, case.input.action, _fill(params, case), case.before)
        after = _snapshot(book, case.before, result)
        # The implementation allocates reservation ids itself. When the model's
        # `r` argument did not recover, the id it would have used is unknown, so
        # the two id-indexed variables cannot be compared for a Reserve.
        if case.input.action == "Reserve" and _is_unchecked(params.get("r")):
            unobservable.extend(["holder", "amt", "live"])
        return _Result(output=None, after=after, semantic_output={"unobservable": unobservable})


def _is_unchecked(value: Any) -> bool:
    return repr(value) == "UNCHECKED"


def _fill(params: dict[str, Any], case: Any) -> dict[str, Any]:
    """Arguments the implementation needs, refusing to invent one it lacks.

    An UNCHECKED argument is not defaulted from ``case.after`` -- that is the
    oracle leak RP-02 removed, and re-introducing it here would make this
    instrument agree with itself.
    """
    filled = {}
    for name, value in params.items():
        if _is_unchecked(value):
            raise AssertionError(f"unrecovered argument {name!r} for {case.name}")
        filled[name] = value
    return filled
