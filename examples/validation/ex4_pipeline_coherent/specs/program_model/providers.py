"""Effect providers for `LedgerStorePort`.

TWO providers are shipped, and shipping two is the whole point of this file.
The MF-038 baseline (0 of 9 content bugs caught) and the ex1-run4 result (45
points killed, every one by a provider CONTENT assertion) are measurements of
two different instruments, and an eval that runs only one of them credits the
wrong component. So this fixture makes the two arms two declared mappings:

  ARM A -- corpus alone
      --mapping specs/program_model/case_adapters_corpus_only.toml
      binds `silent_ledger_store_provider`: a real file-backed store that
      writes what the program tells it to write and asserts NOTHING. The only
      oracles in play are the corpus's own: the projected after-state and the
      adapter output. This is the MF-038 instrument.

  ARM B -- corpus + content-asserting provider
      --mapping specs/program_model/case_adapters.toml
      binds `ledger_store_provider`: the same store, plus an assertion on
      scope exit that the PERSISTED BYTES equal the modeled after-state's
      `ledger`. This is the ex1-run4 instrument.

Neither arm suppresses anything. Arm A is not arm B with its assertions turned
off by a flag -- it is a different declared provider, so a reader of the
mapping can see which instrument produced a number. A suppression key would
have been the shorter route and the wrong one.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from pipeline_contract.types import PersistLedger


class FileLedgerStore:
    """The durable side of the ledger: one line of comma-joined entries."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.writes: list[str] = []

    def persist(self, command: PersistLedger) -> str:
        entries = command.entries
        self.writes.append(entries)
        self.path.write_text(entries, encoding="utf-8")
        return str(self.path)

    def persisted(self) -> str:
        if not self.path.exists():
            return ""
        return self.path.read_text(encoding="utf-8")


class SilentLedgerStoreProvider:
    """ARM A. Binds the real boundary; makes no claim about what crossed it."""

    @contextmanager
    def bind(self, context: Any) -> Iterator[Any]:
        work_dir = Path(context.work_dir)
        work_dir.mkdir(parents=True, exist_ok=True)
        store = FileLedgerStore(work_dir / "ledger.txt")
        try:
            yield store
        finally:
            pass


class ContentAssertingLedgerStoreProvider:
    """ARM B. Asserts the persisted bytes against the modeled after-state.

    The assertion is the exact shape ex1-run4 measured: persisted content ==
    modeled after-state, which also doubles as a no-write-on-no-transition
    check. It never rewrites the case; if a concrete value cannot represent the
    modeled outcome the model is wrong, not the oracle.
    """

    @contextmanager
    def bind(self, context: Any) -> Iterator[Any]:
        work_dir = Path(context.work_dir)
        work_dir.mkdir(parents=True, exist_ok=True)
        store = FileLedgerStore(work_dir / "ledger.txt")
        try:
            yield store
        finally:
            expected = sorted(context.case.after["ledger"])
            persisted = store.persisted()
            actual = [item for item in persisted.split(",") if item]
            if sorted(actual) != expected:
                raise AssertionError(
                    "DETECTOR[provider_content_assertion] "
                    f"persisted ledger {actual!r} != modeled after-state {expected!r} "
                    f"(action={context.action}, case={context.case.name})"
                )
            before = sorted(context.case.before["ledger"])
            if expected == before and store.writes:
                raise AssertionError(
                    "DETECTOR[provider_content_assertion] "
                    f"the ledger did not change in the model but the program wrote "
                    f"{store.writes!r} (action={context.action}, case={context.case.name})"
                )


ledger_store_provider = ContentAssertingLedgerStoreProvider()
silent_ledger_store_provider = SilentLedgerStoreProvider()
