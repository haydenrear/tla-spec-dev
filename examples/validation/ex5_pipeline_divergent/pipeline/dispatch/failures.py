"""Model variable `failed`.

Component: dispatch. Reaches only its own component (an internal edge to
`delivery`).
"""

from __future__ import annotations

from pipeline.dispatch.delivery import Dispatcher


class FailureLog:
    """`failed`: delivered items that later failed."""

    def __init__(self, dispatcher: Dispatcher) -> None:
        self._dispatcher = dispatcher
        self._failed: set[str] = set()

    @property
    def failed(self) -> frozenset[str]:
        return frozenset(self._failed)

    def fail(self, item: str) -> bool:
        """`Fail(i)`: a delivered item, not already failed, becomes failed."""
        if item in self._failed:
            return False
        if not self._dispatcher.release(item):
            return False
        self._failed.add(item)
        return True
