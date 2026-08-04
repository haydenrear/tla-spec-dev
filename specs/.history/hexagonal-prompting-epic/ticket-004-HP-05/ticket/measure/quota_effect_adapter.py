"""HP-05's instrument: the same corpus, run under three mappings.

TICKET-LOCAL (``specs/tickets/**`` is out of the modeled representation scope).
This is the measurement, not shipped surface. The thing under measurement IS
shipped: the provider it binds is the one ``scripts/generate_python.py`` emits
from ``spec_manifest.yaml``, imported unmodified. Nothing here reimplements a
content assertion.

It is HP-03's adapter with ONE change, and the change is the whole ticket:

    HP-03's adapter projected the implementation's ledger back into the model's
    vocabulary, which DISCARDS the running total, because the model's COMMIT
    element is << "COMMIT", tenant, amount >> and carries no total. Its own
    docstring says so: "any fault that corrupts only the total is invisible
    here." M04 survived both of HP-03's corpora for exactly that reason.

    Here, the durable write goes THROUGH THE PORT. `_append_line` is replaced,
    for the lifetime of one case, by a call to the bound LedgerAppendPort with
    the full line -- total included -- and the file write still happens, so the
    projected-state comparison HP-03 made is unchanged and still runs. The
    projection loses nothing it had; the port sees what the projection cannot.

THE SEAM IS INSTALLED BY THE INSTRUMENT, and that is disclosed rather than
hidden. `reference/quota_ledger.py` has no port: it opens the file itself. That
is the `binding_style: self_installed` case references/effect_providers.md
already names -- "None, when the scope installs and restores a bounded
repository integration itself" -- and it is what any adapter for a legacy
service does. What it does NOT do is change the implementation under test: the
mutants are applied to the same bytes either way, and the seam is identical
under all three mappings, so the only thing that varies between the arms is the
provider named in the mapping.

THE CODEC IS THE INSTRUMENT'S, NOT THE MODEL'S. Turning `COMMIT t1 1 1` into a
payload is knowledge about the implementation's line format, and no model
derives it. That is a real cost of a content oracle and it is stated here so
that nobody reads the kill numbers as though the framework inferred the format.
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

#: The actions that declare LedgerAppendPort, mirroring the fixture manifest's
#: `effects.actions` block. Reserve and Release declare `[]` -- empty, not
#: absent -- so no provider is bound for them and no crossing is expected.
PORT_ACTIONS = ("Commit", "CloseTenant")


@dataclass
class _Result:
    output: Any = None
    after: Any = None
    semantic_output: Any = None


def _tenants(before: dict[str, Any]) -> list[str]:
    return sorted(before.get("available", {}))


def _build(before: dict[str, Any], work_dir: Path | None, port: Any) -> Any:
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
    if port is not None:
        _install_port(book, port)
    return book


def _install_port(book: Any, port: Any) -> None:
    """Route this book's durable append through the bound port, and to the file.

    Bounded and per-instance: the class is untouched, so the seam disappears
    with the book. The file write still happens because the projected-state
    comparison reads it back -- the port is an ADDITIONAL oracle, never a
    replacement for the one HP-03 already had.
    """
    original = book._append_line
    command_type = _command_type()

    def _append_line(line: str) -> None:
        port.append(command_type(**_decode(line)))
        original(line)

    book._append_line = _append_line


def _command_type() -> Any:
    module = importlib.import_module("quota_ledger_effects.types")
    return module.AppendLedgerLine


def _decode(line: str) -> dict[str, Any]:
    """`COMMIT <tenant> <amount> <total>` / `CLOSE <tenant> <total>`.

    The model's CLOSE element is << "CLOSE", t, committed[t] >>: its third slot
    IS the total, so a CLOSE line's amount and total are the same number. That
    is why one content rule -- `append.total == committed[tenant]` -- covers
    both line kinds instead of needing a rule per kind.
    """
    parts = line.split()
    kind, tenant = parts[0], parts[1]
    if kind == "COMMIT":
        return {"kind": kind, "tenant": tenant, "amount": int(parts[2]), "total": int(parts[3])}
    total = int(parts[2])
    return {"kind": kind, "tenant": tenant, "amount": total, "total": total}


def _render_line(entry: Any) -> str:
    kind, tenant, amount = entry
    if kind == "COMMIT":
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


class PositiveAdapter:
    """An enabled edge: the implementation must take exactly that transition."""

    def __init__(self) -> None:
        self.port: Any = None

    def can_run(self, case: Any) -> Any:
        if case.input.action not in ("Reserve", "Commit", "Release", "CloseTenant"):
            return False, f"{case.input.action} is a modeled refusal with no recoverable argument"
        if any(_is_unchecked(value) for value in case.input.params.values()):
            unchecked = sorted(name for name, value in case.input.params.items() if _is_unchecked(value))
            return False, f"unrecovered argument(s) {', '.join(unchecked)}"
        return True

    def run(self, case: Any, work_dir: Path | None = None) -> _Result:
        book = _build(case.before, work_dir, self.port)
        params = dict(case.input.params)
        unobservable: list[str] = []
        result = _call(book, case.input.action, _fill(params, case))
        after = _snapshot(book, case.before, result)
        if case.input.action == "Reserve" and _is_unchecked(params.get("r")):
            unobservable.extend(["holder", "amt", "live"])
        return _Result(output=None, after=after, semantic_output={"unobservable": unobservable})


class NegativeAdapter:
    """A call the model does not enable: the implementation must refuse it."""

    def __init__(self) -> None:
        self.port: Any = None

    def can_run(self, case: Any) -> Any:
        if case.input.action not in ("Reserve", "Commit", "Release", "CloseTenant"):
            return False, f"no binding for {case.input.action}"
        if case.input.action == "Reserve" and re.search(
            r"(?<![A-Za-z_])r(?![A-Za-z0-9_])", case.output.reason
        ):
            # HP-03-DF-01, carried forward unchanged: the model gives Reserve a
            # reservation id as an ARGUMENT while the API allocates it, so a
            # case refused solely by a constraint on `r` asserts the rejection
            # of a call this API cannot express. Skipped and reported, never
            # counted.
            return False, "refused only by a constraint on `r`, which this API allocates rather than accepts"
        return True

    def run(self, case: Any, work_dir: Path | None = None) -> _Result:
        expected = case.output
        book = _build(case.before, work_dir, self.port)
        result = _call(book, case.input.action, dict(case.input.params))
        after = _snapshot(book, case.before, result)
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


def _is_unchecked(value: Any) -> bool:
    return repr(value) == "UNCHECKED"


def _fill(params: dict[str, Any], case: Any) -> dict[str, Any]:
    filled = {}
    for name, value in params.items():
        if _is_unchecked(value):
            raise AssertionError(f"unrecovered argument {name!r} for {case.name}")
        filled[name] = value
    return filled
