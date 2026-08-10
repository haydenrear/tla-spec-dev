"""Does each adapter behind artifact_E/F's declared `Journal` port satisfy the
contract the port declares? Read from quota_ledger/domain.py:

    def lines(self) -> list[str]:
        \"\"\"Every line appended, in the order appended, none of them blank.\"\"\"
"""
import sys, tempfile
from pathlib import Path
tree = sys.argv[1]
sys.path.insert(0, tree)
from quota_ledger import FileJournal, MemoryJournal

with tempfile.TemporaryDirectory() as raw:
    real = FileJournal(Path(raw) / "l.txt")
    fake = MemoryJournal()
    for journal, name in ((real, "FileJournal (real)"), (fake, "MemoryJournal (fake)")):
        journal.append("COMMIT a 1 1")
        journal.append("")
        journal.append("CLOSE a 1")
        print(f"{name:<24} lines()={journal.lines()!r}")
