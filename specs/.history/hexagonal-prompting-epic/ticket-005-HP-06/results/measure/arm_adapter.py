"""The shared oracle. ONE copy, both arms.

HP-06 measurement instrument, descended from HP-03's `quota_ledger_adapter.py`
and carrying its two disclosures unchanged:

* The MODEL's commit line is ``<<"COMMIT", tenant, amount>>`` -- it has no
  running total -- while both arms write ``COMMIT <tenant> <amount> <total>``.
  Projecting an arm back into the model therefore DISCARDS the total, so a fault
  that corrupts only the total is invisible to every corpus instrument here.
  That is a limit of the model, not of the corpus, and it is exactly the gap the
  `map-checking` column exists to cover.
* On a NEGATIVE case the assertion is refusal plus inertness. The rejection
  REASON is not compared: the case's reason is the model's violated conjunct in
  TLA+ and the arm's reason is its own string. Copying the model's reason
  through on a refusal is what makes the outputs comparable; recorded here
  rather than hidden, because a check that compares a value against itself
  proves nothing.

Everything arm-specific lives in `arm_a_binding.py` / `arm_b_binding.py`,
selected by ``QUOTA_LEDGER_BINDING``. This file never branches on the arm, and a
reader can confirm that by grepping it for the letters A and B.
"""

from __future__ import annotations

import importlib
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

_binding = importlib.import_module(os.environ["QUOTA_LEDGER_BINDING"])

QUOTA = int(os.environ.get("QUOTA_LEDGER_QUOTA", "2"))


def _command_type() -> Any:
    module = importlib.import_module("quota_ledger_effects.types")
    return module.AppendLedgerLine


def _decode(line: str) -> dict[str, Any]:
    """`COMMIT <tenant> <amount> <total>` / `CLOSE <tenant> <total>`.

    HP-05's codec, unchanged. The model's CLOSE element is
    ``<< "CLOSE", t, committed[t] >>`` -- its third slot IS the total -- so a
    CLOSE line's amount and total are the same number, which is why one content
    rule (`append.total == committed[tenant]`) covers both line kinds.
    """
    parts = line.split()
    kind, tenant = parts[0], parts[1]
    if kind == "COMMIT":
        return {"kind": kind, "tenant": tenant, "amount": int(parts[2]), "total": int(parts[3])}
    total = int(parts[2])
    return {"kind": kind, "tenant": tenant, "amount": total, "total": total}


def _install_port(book: Any, port: Any) -> None:
    """Route the durable append through the bound port AND to the file.

    An ADDITIONAL oracle, never a replacement: the projected-state comparison
    still reads the file back, so nothing HP-03 had is lost. Per instance, so
    the seam disappears with the book.
    """
    command_type = _command_type()
    _binding.install_line_observer(book, lambda line: port.append(command_type(**_decode(line))))


@dataclass
class _Result:
    output: Any = None
    after: Any = None
    semantic_output: Any = None


def _tenants(before: dict[str, Any]) -> list[str]:
    for field in ("available", "committed"):
        if field in before:
            return sorted(before[field])
    return []


def _ids(before: dict[str, Any]) -> list[str]:
    return sorted(before.get("amt", {}))


def _reservations(before: dict[str, Any]) -> list[tuple[str, str, int]]:
    holder = before.get("holder", {})
    amt = before.get("amt", {})
    return [
        (rid, holder[rid], amt[rid])
        for rid in sorted(before.get("live", ()))
    ]


def _next_ordinal(before: dict[str, Any]) -> int:
    """The next id the arm may allocate. Ids are never reused in the model."""
    highest = 0
    for rid, tenant in before.get("holder", {}).items():
        if tenant == "none":
            continue
        digits = "".join(character for character in rid if character.isdigit())
        if digits:
            highest = max(highest, int(digits))
    return highest + 1


def _render_line(entry: Any) -> str:
    kind, tenant, amount = entry
    if kind == "COMMIT":
        # The model's COMMIT line has no running total; both arms' lines do. A
        # placeholder keeps the projection round-trippable without inventing a
        # total the model never stated.
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
    holder = {}
    amt = {}
    for rid in ids:
        found = _binding.reservation(book, rid)
        if found is None:
            holder[rid] = before.get("holder", {}).get(rid, "none")
            amt[rid] = before.get("amt", {}).get(rid, 0)
        else:
            holder[rid], amt[rid] = found
    snapshot = {
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
    return snapshot


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
    """Compare only the fields the case's own projection carries.

    A SLICE projects a subset of the model's variables, so its cases' `after`
    dicts hold only that aspect's fields. The shipped comparator merges expected
    and actual key sets, so an adapter returning the WHOLE state against a
    projected case reports every unprojected field as `expected None, actual
    <value>` -- which is what made both slice columns come back with a red
    control on the first run, on both arms, on the unmutated code.

    Filtering here is the honest reading of the manifest's own claim sentences:
    the RESERVATIONS slice does not project `committed` or the ledger, so it
    must not judge them. Nothing is hidden -- the whole-view columns are
    unaffected because their cases carry all nine fields.
    """
    return {name: value for name, value in snapshot.items() if name in case.after}


class NegativeAdapter:
    """A call the model does not enable: the arm must refuse it."""

    def __init__(self) -> None:
        self.port: Any = None

    def can_run(self, case: Any) -> Any:
        if case.input.action not in BOUND_ACTIONS:
            return False, f"no binding for {case.input.action}"
        if case.input.action == "Reserve" and re.search(
            r"(?<![A-Za-z_])r(?![A-Za-z0-9_])", case.output.reason
        ):
            # HP-03-DF-01, reproduced verbatim rather than re-derived. The model
            # gives Reserve a reservation id as an ARGUMENT while FEATURE.md's
            # API allocates it, so a case refused solely by a constraint on `r`
            # asserts the rejection of a call this API cannot express. Skipped
            # and reported, never counted -- on BOTH arms identically.
            return False, "refused only by a constraint on `r`, which this API allocates rather than accepts"
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
    """An enabled edge: the arm must take exactly that transition."""

    def __init__(self) -> None:
        self.port: Any = None

    def can_run(self, case: Any) -> Any:
        if case.input.action not in BOUND_ACTIONS:
            return False, f"{case.input.action} is a modeled refusal with no recoverable argument"
        if any(_is_unchecked(value) for value in case.input.params.values()):
            unchecked = sorted(
                name for name, value in case.input.params.items() if _is_unchecked(value)
            )
            return False, f"unrecovered argument(s) {', '.join(unchecked)}"
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
