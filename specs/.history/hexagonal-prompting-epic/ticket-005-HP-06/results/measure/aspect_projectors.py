"""State projections that make each aspect slice project ONLY its aspect.

HP-06 measurement instrument. A TLA+ slice inherits every VARIABLE of the
module it extends, so restricting `Next` restricts what the slice *enters*, not
what it *observes*. The manifest's two `claim` sentences say more than that:

    Aspect_Reservations   "projects available, live, holder, amt and closed;
                           it does NOT project committed or the ledger"
    Aspect_Ledger         "projects committed and the ledger; it does NOT
                           project available"

Without these projections both slices would compare all nine variables, and a
LEDGER slice that compares `available` is not the slice M08 was seeded against
-- it would kill M08 and the result would read as "case modules see cross-aspect
faults" when what actually happened is that the instrument was built wider than
its own declaration. That is the round-1 mistake the fixture exists to avoid,
run in the opposite direction.

`status` and `reason` are kept by BOTH slices. They are the reported outcome of
the call rather than an aspect's state, the model carries them precisely so a
refusal has something to assert (QuotaLedger.tla's own comment says so), and
dropping them from a slice would silently delete the negative corpus's only
oracle.
"""

from __future__ import annotations

from typing import Any

RESERVATIONS_FIELDS = ("available", "live", "holder", "amt", "closed", "status", "reason")
LEDGER_FIELDS = ("committed", "ledger", "closed", "status", "reason")


def _keep(state: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
    return {name: value for name, value in state.items() if name in fields}


def project_reservations(state: dict[str, Any]) -> dict[str, Any]:
    return _keep(state, RESERVATIONS_FIELDS)


def project_ledger(state: dict[str, Any]) -> dict[str, Any]:
    return _keep(state, LEDGER_FIELDS)
