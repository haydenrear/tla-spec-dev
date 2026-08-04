"""The real `DurableLedger`: an append-only file on disk."""

from __future__ import annotations

from pathlib import Path
from typing import List, Union


class FileLedgerAdapter:
    """Durable ledger backed by a file. Appends open, write, and close the
    file each time rather than holding a long-lived handle, so the domain's
    view (via `lines()`) always reflects exactly what is on disk -- there is
    no in-memory copy to fall out of step with the file."""

    def __init__(self, path: Union[str, Path]):
        self._path = Path(path)
        if not self._path.exists():
            self._path.write_text("", encoding="utf-8")

    def append_line(self, line: str) -> None:
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def lines(self) -> List[str]:
        text = self._path.read_text(encoding="utf-8")
        return [line for line in text.splitlines() if line]
