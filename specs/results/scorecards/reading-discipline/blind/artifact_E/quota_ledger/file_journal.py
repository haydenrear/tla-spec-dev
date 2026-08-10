"""Driven adapter: the `Journal` port backed by a text file, one line per entry.

The only module that knows the durable side is a filesystem. It knows nothing
about tenants, quotas, or reservations -- it moves lines, and the line format
belongs to the domain that writes them.
"""

from __future__ import annotations

from pathlib import Path


class FileJournal:
    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._path.write_text("", encoding="utf-8")  # "the ledger file starts empty"

    def append(self, line: str) -> None:
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def lines(self) -> list[str]:
        # The empty trailing element after the final newline is an artifact of
        # storing lines in a file, so it is dropped here and not in the domain.
        return [line for line in self._path.read_text(encoding="utf-8").splitlines() if line]
