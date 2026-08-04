"""HP-04: a FAKE for ex4's `LedgerStorePort`, to run the same cases twice.

Scorecard D3 anchor 4 asks for a driven port exercised by a REAL adapter AND a
FAKE, with the same cases passing against both. `examples/validation/ex4_*`
ships the real one -- `FileLedgerStore`, a file on disk -- and no fake, and
before HP-04 the question could not be asked at all: a slice's corpus refused to
execute under every mapping the fixture shipped (CM-F5 / EV-03-DF-02).

This file is the fake, and it lives under `specs/tickets/HP-04/results/` rather
than inside the fixture so nothing HP-06 scores is touched. It implements the
same one-method port and carries the SAME content assertion as ex4's arm-B
provider, which is the property that makes the comparison mean anything: if the
fake asserted less, "the same cases pass against both" would be true by being
weaker.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

# The runner checks the FAKE against the generated port Protocol by exact
# annotation, so the fake has to name the same command type the real adapter
# does. That check is the reason "the same cases pass against both" means
# something: a fake that widened `command` to `Any` was refused outright.
from pipeline_contract.types import PersistLedger


class InMemoryLedgerStore:
    """The same port, with no filesystem behind it at all."""

    def __init__(self) -> None:
        self.writes: list[str] = []
        self._entries = ""

    def persist(self, command: PersistLedger) -> str:
        self.writes.append(command.entries)
        self._entries = command.entries
        return "memory://ledger"

    def persisted(self) -> str:
        return self._entries


class ContentAssertingFakeLedgerStoreProvider:
    """Byte-for-byte the arm-B assertion, over the fake instead of the file."""

    @contextmanager
    def bind(self, context: Any) -> Iterator[Any]:
        store = InMemoryLedgerStore()
        try:
            yield store
        finally:
            expected = sorted(context.case.after["ledger"])
            actual = [item for item in store.persisted().split(",") if item]
            if sorted(actual) != expected:
                raise AssertionError(
                    "DETECTOR[fake_provider_content_assertion] "
                    f"persisted ledger {actual!r} != modeled after-state {expected!r} "
                    f"(action={context.action}, case={context.case.name})"
                )
            before = sorted(context.case.before["ledger"])
            if expected == before and store.writes:
                raise AssertionError(
                    "DETECTOR[fake_provider_content_assertion] "
                    f"the ledger did not change in the model but the program wrote "
                    f"{store.writes!r} (action={context.action}, case={context.case.name})"
                )


fake_ledger_store_provider = ContentAssertingFakeLedgerStoreProvider()
