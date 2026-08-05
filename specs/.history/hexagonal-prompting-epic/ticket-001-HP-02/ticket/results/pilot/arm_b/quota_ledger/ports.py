"""The one driven port the domain needs: durable, append-only storage.

Named for the need (durably remembering lines, in order, forever) rather than
for any technology that could satisfy it. Two operations; nothing else outside
the domain's control is indirected through here.
"""

from __future__ import annotations

from typing import List, Protocol


class DurableLedger(Protocol):
    """A place that remembers lines forever, in the order they were given it.

    Concrete alternative: a file, a database table, an in-memory list. Any of
    them satisfies this port with no change to the domain that depends on it.
    """

    def append_line(self, line: str) -> None:
        """Durably record one more line, after every line already recorded."""
        ...

    def lines(self) -> List[str]:
        """Every line recorded so far, in the order it was appended, none blank."""
        ...
