"""Adapter conformance for the `LedgerJournal` port declared in
`../reference_ports/domain.py:38-58`.

WHY THIS FILE EXISTS
--------------------
The port's docstring names its whole job: *"a record that outlives the run and
reads back in the order it was written."* Until this file, **nothing anywhere
observed that record except the adapter that wrote it.**
`../tests/test_behavior.py` reaches the ledger only through
`ReservationBook.ledger_lines()` -> `LedgerJournal.lines()`, so the real
adapter's one distinguishing property was asserted by nothing.

That is not a suspicion. Replace `FileJournal`'s body with a plain list, remove
every filesystem call, and **28 of 28 shared cases still pass through the real
wiring while zero `ledger.txt` files are created.** The hole is filed as
`RM-05-DF-05`, the way `journal_memory.py:11` cites `BA-B14` for the hole on the
other side of the same port. This file is the case that kills it.

WHAT IT IS AND IS NOT
---------------------
It is a **conformance suite for the two adapters**, exercised directly rather
than through the domain, in two parts:

  * `TestPortContract` -- the clauses the port declares, run against **both**
    implementations from one parametrised source. `FileJournal` and
    `InMemoryJournal` must answer these identically.
  * `TestDurableRecord` -- the clauses only a durable adapter can satisfy, and
    **every observation in them is made out of band**: `Path.read_text()` on the
    declared path, never `journal.lines()`. A reader that goes back through the
    adapter re-asks the writer and learns nothing.

**The second part cannot run against the fake, and that is the point, not a
gap.** `InMemoryJournal` is durable for the lifetime of the object; a case that
asserts a byte on disk *must* fail against it. So the pair is held together by
`test_the_fake_leaves_no_durable_record`, which asserts the difference instead
of assuming it -- if the fake ever started writing a file, the pair would stop
being a real one and a fake one and nothing else here would notice.

WHAT THIS SUITE STILL CANNOT SEE
--------------------------------
  * **Anything about `ReservationBook`.** These cases never construct a
    `QuotaLedger`. A domain that stopped calling the port entirely is invisible
    here and visible to `test_behavior.py`; the two suites are complements.
  * **Concurrency and crash-atomicity.** Every case is single-process and
    sequential. A partial write torn by a crash between `open` and `write` is
    outside what any of this observes.
  * **Any record older than one object.** The adapter truncates on construction
    (`journal_file.py:30`), so a record cannot be read back by a second
    `FileJournal` over the same path. That is pinned rather than papered over by
    `test_construction_truncates_so_no_second_wiring_can_read_the_record`, and
    it means the port's "outlives the run" is satisfied only in the sense that
    the *file* outlives the object -- not that the adapter can ever reopen it.

Run it:

    uv run --with pytest python -m pytest \\
      examples/validation/ab/tests/test_journal_conformance.py -q

`QUOTA_LEDGER_PORTS_DIR` points it at another tree that declares the same port.
It does not default to skipping: a tree with no adapters fails at collection,
loudly, because a conformance suite that quietly runs zero cases is the defect
class this file was written to answer.
"""

from __future__ import annotations

import gc
import importlib
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pytest

_HERE = Path(__file__).resolve().parent
_DEFAULT_PORTS_DIR = _HERE.parent / "reference_ports"

sys.path.insert(0, os.environ.get("QUOTA_LEDGER_PORTS_DIR", str(_DEFAULT_PORTS_DIR)))
FileJournal = importlib.import_module("journal_file").FileJournal
InMemoryJournal = importlib.import_module("journal_memory").InMemoryJournal

LEDGER_NAME = "ledger.txt"


@dataclass(frozen=True)
class Adapter:
    """One implementation of `LedgerJournal`, plus how to observe it OUT OF BAND.

    `durable` is the whole difference between the two rows and it is a declared
    property, not an inferred one: it says whether this adapter claims the
    record survives as bytes somewhere a reader that has never heard of the
    adapter can find them.
    """

    name: str
    make: Callable[[Path], object]
    durable: bool


def _real(directory: Path) -> object:
    return FileJournal(directory / LEDGER_NAME)


def _fake(directory: Path) -> object:
    return InMemoryJournal()


REAL = Adapter(name="FileJournal", make=_real, durable=True)
FAKE = Adapter(name="InMemoryJournal", make=_fake, durable=False)

ADAPTERS = [REAL, FAKE]
DURABLE_ADAPTERS = [adapter for adapter in ADAPTERS if adapter.durable]


def record_on_disk(directory: Path) -> list[str]:
    """The record as a reader who has never heard of the adapter would find it.

    This function is the whole contribution of this file. It opens the declared
    path itself. It never calls `lines()`, and it must never be changed to.
    """
    path = directory / LEDGER_NAME
    if not path.exists():
        raise AssertionError(
            f"no record at {path}: the durable adapter wrote nothing a reader outside it can find"
        )
    return [entry for entry in path.read_text(encoding="utf-8").splitlines() if entry]


# -- the port contract, identical against both implementations --------------


class TestPortContract:
    """One source of cases, run against both implementations of the port.

    These go through `lines()` deliberately: they are about the interface the
    domain was written against, and both implementations owe the same answers.
    `journal_memory.py` is reached here without a composition point wiring it,
    so a fault on the fake side has somewhere to be seen in the same run as a
    fault on the real side rather than only under a second wiring.
    """

    @pytest.mark.parametrize("adapter", ADAPTERS, ids=lambda a: a.name)
    def test_a_new_journal_reports_no_lines(self, adapter, tmp_path):
        assert adapter.make(tmp_path).lines() == []

    @pytest.mark.parametrize("adapter", ADAPTERS, ids=lambda a: a.name)
    def test_appends_read_back_in_the_order_written(self, adapter, tmp_path):
        journal = adapter.make(tmp_path)
        for line in ("COMMIT acme 3 3", "COMMIT globex 2 2", "CLOSE acme 3"):
            journal.append(line)
        assert journal.lines() == ["COMMIT acme 3 3", "COMMIT globex 2 2", "CLOSE acme 3"]

    @pytest.mark.parametrize("adapter", ADAPTERS, ids=lambda a: a.name)
    def test_reading_the_record_does_not_consume_it(self, adapter, tmp_path):
        journal = adapter.make(tmp_path)
        journal.append("COMMIT acme 1 1")
        assert journal.lines() == journal.lines() == ["COMMIT acme 1 1"]

    @pytest.mark.parametrize("adapter", ADAPTERS, ids=lambda a: a.name)
    def test_a_blank_append_is_not_reported_as_a_line(self, adapter, tmp_path):
        journal = adapter.make(tmp_path)
        journal.append("")
        journal.append("CLOSE acme 0")
        assert journal.lines() == ["CLOSE acme 0"]


# -- the durable record, observed by something that is not the writer -------


class TestDurableRecord:
    """Only a `durable` adapter can satisfy these, and every read is out of band.

    Not one assertion in this class calls `lines()`. That is the entire remedy:
    a suite that reads the record back through the adapter that wrote it is
    asking the writer whether it wrote, and gets the same answer from an adapter
    that touched no filesystem at all.
    """

    @pytest.mark.parametrize("adapter", DURABLE_ADAPTERS, ids=lambda a: a.name)
    def test_every_appended_line_reaches_the_declared_path(self, adapter, tmp_path):
        journal = adapter.make(tmp_path)
        for line in ("COMMIT acme 3 3", "COMMIT acme 2 5", "CLOSE acme 5"):
            journal.append(line)
        assert record_on_disk(tmp_path) == ["COMMIT acme 3 3", "COMMIT acme 2 5", "CLOSE acme 5"]

    @pytest.mark.parametrize("adapter", DURABLE_ADAPTERS, ids=lambda a: a.name)
    def test_an_append_is_on_disk_before_the_next_call_is_made(self, adapter, tmp_path):
        """A record buffered until something asks for it is not a durable record."""
        journal = adapter.make(tmp_path)
        journal.append("COMMIT acme 3 3")
        assert record_on_disk(tmp_path) == ["COMMIT acme 3 3"]
        journal.append("COMMIT acme 2 5")
        assert record_on_disk(tmp_path) == ["COMMIT acme 3 3", "COMMIT acme 2 5"]

    @pytest.mark.parametrize("adapter", DURABLE_ADAPTERS, ids=lambda a: a.name)
    def test_the_record_outlives_the_object_that_wrote_it(self, adapter, tmp_path):
        """"A record that outlives the run" -- `domain.py:42`, taken literally."""
        journal = adapter.make(tmp_path)
        journal.append("COMMIT acme 3 3")
        del journal
        gc.collect()
        assert record_on_disk(tmp_path) == ["COMMIT acme 3 3"]

    @pytest.mark.parametrize("adapter", DURABLE_ADAPTERS, ids=lambda a: a.name)
    def test_the_record_starts_empty_and_the_file_exists(self, adapter, tmp_path):
        """`../FEATURE.md`: "the ledger file starts empty" -- an empty FILE."""
        adapter.make(tmp_path)
        assert (tmp_path / LEDGER_NAME).read_text(encoding="utf-8") == ""


# -- the pair is a real one and a fake one, asserted rather than assumed ----


def test_the_fake_leaves_no_durable_record(tmp_path, monkeypatch):
    """The fake's defining property, stated as a case.

    `journal_memory.py:34` calls itself "durable for the lifetime of the
    object". If it ever grew a file, the two wirings would stop being a real
    adapter and a fake and every conclusion drawn from running one suite through
    both would quietly change meaning.

    The fake is handed no path, so a fake that started writing would write
    somewhere it invented -- almost certainly relative to the working directory.
    `chdir` is what makes that observable rather than assumed away.
    """
    monkeypatch.chdir(tmp_path)
    journal = FAKE.make(tmp_path)
    journal.append("COMMIT acme 3 3")
    assert journal.lines() == ["COMMIT acme 3 3"]
    assert sorted(path.name for path in tmp_path.iterdir()) == []


def test_construction_truncates_so_no_second_wiring_can_read_the_record(tmp_path):
    """The limit this suite pins instead of papering over.

    `journal_file.py:30` truncates the path in the constructor, so "outlives the
    run" holds for the FILE and not for the ADAPTER: point a second `FileJournal`
    at a written record and the record is gone. This case exists so that the
    property is written down somewhere executable, and so that a tree which
    later makes the adapter reopen an existing record has to come here and say
    so.
    """
    first = REAL.make(tmp_path)
    first.append("COMMIT acme 3 3")
    assert record_on_disk(tmp_path) == ["COMMIT acme 3 3"]

    REAL.make(tmp_path)
    assert (tmp_path / LEDGER_NAME).read_text(encoding="utf-8") == ""
