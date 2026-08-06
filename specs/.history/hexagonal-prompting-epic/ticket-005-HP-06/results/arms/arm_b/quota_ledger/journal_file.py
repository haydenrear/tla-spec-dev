"""A CommitJournal that is a file on disk.

Imports nothing from the domain -- the port is structural, so the dependency
runs one way only: the composition point knows about this module, and this
module knows about a filesystem.
"""

from __future__ import annotations

from pathlib import Path


class FileJournal:
    """Durable, append-only, one line per entry.

    The file starts empty, as the feature says, so construction creates or
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
        return [line for line in text.splitlines() if line.strip()]
