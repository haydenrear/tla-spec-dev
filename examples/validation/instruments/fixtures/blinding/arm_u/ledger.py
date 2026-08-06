"""A three-line stand-in for a judged artifact's implementation module."""

from __future__ import annotations


class Ledger:
    def __init__(self) -> None:
        self._committed: dict[str, int] = {}

    def commit(self, tenant: str, amount: int) -> None:
        self._committed[tenant] = self._committed.get(tenant, 0) + amount

    def committed(self) -> dict[str, int]:
        return dict(self._committed)
