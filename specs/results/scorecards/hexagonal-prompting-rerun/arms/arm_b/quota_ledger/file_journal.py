"""A Journal kept as lines in a file. The real driven adapter.

This module knows about paths, encodings and newlines. The domain does not,
and does not import this module.
"""

from __future__ import annotations

import os
from pathlib import Path


class FileJournal:
    """One record per line, in a text file, appended and never rewritten.

    Constructing one establishes an empty journal: the feature says the ledger
    file starts empty, so an existing file at this path is truncated.

    The file is the durable form, so it carries framing the journal contract
    does not: a trailing newline after the last record. Stripping that framing
    back off on read is this adapter's job, not the domain's -- the contract
    promises the records that were appended and nothing else.
    """

    def __init__(self, path: str | os.PathLike[str]) -> None:
        self._path = Path(path)
        self._path.write_text("", encoding="utf-8")

    def append(self, record: str) -> None:
        with self._path.open("a", encoding="utf-8") as handle:
            handle.write(record + "\n")

    def records(self) -> list[str]:
        text = self._path.read_text(encoding="utf-8")
        return [line for line in text.splitlines() if line]
