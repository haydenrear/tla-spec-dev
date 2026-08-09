"""FEATURE.md, commit: "appends EXACTLY ONE line to the durable ledger".
A tenant name containing a line break makes one accepted command produce two
lines in ledger_lines(), and R2's per-line accounting stops parsing."""
import sys, importlib, tempfile
from pathlib import Path
tree = sys.argv[1]
sys.path.insert(0, tree)
m = importlib.import_module("quota_ledger")
with tempfile.TemporaryDirectory() as raw:
    book = m.QuotaLedger({"ac\nme": 9}, Path(raw) / "l.txt")
    r = book.reserve("ac\nme", 2)
    before = list(book.ledger_lines())
    book.commit(r.reservation_id)
    after = list(book.ledger_lines())
    print(f"  lines added by ONE accepted commit: {len(after) - len(before)}  -> {after!r}")
    print(f"  committed()={book.committed('ac\nme')!r}  available()={book.available('ac\nme')!r}")
