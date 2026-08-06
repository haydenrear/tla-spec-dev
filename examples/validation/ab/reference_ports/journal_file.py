"""The REAL adapter for `domain.LedgerJournal`: a file on disk.

Imports nothing from the domain -- the port is structural, so the dependency
runs one way only: a composition point knows about this module, and this module
knows about a filesystem.

This file is one of the two regions the PA catalogue seeds INSIDE. A fault here
is reachable by anything that runs the shared suite through the real wiring,
which is every instrument the predecessor had. It is seeded as the CONTRAST for
the fault seeded in `journal_memory.py`, which nothing the predecessor had could
reach. Two faults with one semantic, one on each side of the port, is the whole
measurement: the difference between the two rows is the size of the blind
region the port creates.
"""

from __future__ import annotations

from pathlib import Path


class FileJournal:
    """Durable, append-only, one line per entry.

    The file starts empty, as FEATURE.md says, so construction creates or
    truncates it.
    """

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._path.write_text("", encoding="utf-8")

    def append(self, line: str) -> None:
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def lines(self) -> list[str]:
        text = self._path.read_text(encoding="utf-8")
        return [entry for entry in text.splitlines() if entry]
