"""The file adapter on its own: the things that are true of a file and not of
the port. These are deliberately NOT in the parity list -- a case that can only
be written for one journal belongs to that journal, not to the port."""

from __future__ import annotations

from quota_ledger import QuotaLedger
from quota_ledger.journal_file import FileJournal


def test_the_ledger_file_starts_empty(tmp_path):
    path = tmp_path / "ledger.txt"
    path.write_text("COMMIT stale 1 1\n", encoding="utf-8")
    ledger = QuotaLedger({"acme": 5}, path)
    assert ledger.ledger_lines() == []
    assert path.read_text(encoding="utf-8") == ""


def test_lines_land_on_disk_one_per_entry(tmp_path):
    path = tmp_path / "ledger.txt"
    ledger = QuotaLedger({"acme": 5}, path)
    ledger.commit(ledger.reserve("acme", 2).reservation_id)
    ledger.close_tenant("acme")
    assert path.read_text(encoding="utf-8") == "COMMIT acme 2 2\nCLOSE acme 2\n"


def test_a_second_reader_of_the_same_file_sees_the_same_lines(tmp_path):
    path = tmp_path / "ledger.txt"
    ledger = QuotaLedger({"acme": 5}, path)
    ledger.commit(ledger.reserve("acme", 3).reservation_id)
    # Reading the file back through a separate handle: the lines are durable,
    # not an in-process buffer.
    assert path.read_text(encoding="utf-8").splitlines() == ["COMMIT acme 3 3"]


def test_blank_lines_in_the_file_are_not_reported(tmp_path):
    path = tmp_path / "ledger.txt"
    journal = FileJournal(path)
    journal.append("COMMIT acme 1 1")
    with path.open("a", encoding="utf-8") as handle:
        handle.write("\n   \n")
    journal.append("CLOSE acme 1")
    assert journal.lines() == ["COMMIT acme 1 1", "CLOSE acme 1"]


def test_appending_never_rewrites_what_is_already_there(tmp_path):
    path = tmp_path / "ledger.txt"
    journal = FileJournal(path)
    journal.append("first")
    before = path.read_text(encoding="utf-8")
    journal.append("second")
    after = path.read_text(encoding="utf-8")
    assert after.startswith(before)
    assert after == "first\nsecond\n"
