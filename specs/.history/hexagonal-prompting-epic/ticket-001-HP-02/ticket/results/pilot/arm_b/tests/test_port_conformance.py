"""The `DurableLedger` port has exactly one real outside dependency behind
it: durable, ordered, append-only storage. This file is the identical case
list run against both implementations that satisfy it -- the real
(file-backed) adapter and the fake (in-memory) one used elsewhere in this
test suite to exercise the domain without touching a filesystem.

Every case here runs, unchanged, against both. If a case could only be
written for one of them, that would mean the port was leaking something
adapter-specific -- it isn't.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quota_ledger.adapters.file_adapter import FileLedgerAdapter
from quota_ledger.adapters.memory_adapter import InMemoryLedgerAdapter


def case_starts_empty(port):
    assert port.lines() == []


def case_append_then_read_back(port):
    port.append_line("COMMIT acme 3 3")
    assert port.lines() == ["COMMIT acme 3 3"]


def case_preserves_append_order_across_tenants(port):
    port.append_line("COMMIT acme 3 3")
    port.append_line("COMMIT globex 1 1")
    port.append_line("CLOSE globex 1")
    assert port.lines() == [
        "COMMIT acme 3 3",
        "COMMIT globex 1 1",
        "CLOSE globex 1",
    ]


def case_lines_returns_a_fresh_list_each_time(port):
    port.append_line("COMMIT acme 3 3")
    first = port.lines()
    first.append("not really appended")
    assert port.lines() == ["COMMIT acme 3 3"]


CASES = [
    case_starts_empty,
    case_append_then_read_back,
    case_preserves_append_order_across_tenants,
    case_lines_returns_a_fresh_list_each_time,
]


def test_fake_satisfies_the_port_contract():
    for case in CASES:
        case(InMemoryLedgerAdapter())


def test_real_satisfies_the_port_contract(tmp_path):
    for case in CASES:
        case(FileLedgerAdapter(tmp_path / f"{case.__name__}.txt"))
