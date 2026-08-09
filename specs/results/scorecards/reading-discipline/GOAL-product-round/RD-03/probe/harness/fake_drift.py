"""Does artifact_E/F's fake adapter agree with the real one THROUGH THE DOMAIN,
on input the public API accepts? This is PA-M13's fault class -- "the fake
drifts from the real on write" -- looked for in the shipped code rather than
seeded."""
import sys, importlib, tempfile, json
from pathlib import Path
tree = sys.argv[1]
sys.path.insert(0, tree)
m = importlib.import_module("quota_ledger")

def through(journal_factory, tenant):
    with tempfile.TemporaryDirectory() as raw:
        book = m.Ledger({tenant: 9}, journal_factory(Path(raw)))
        book.commit(book.reserve(tenant, 2).reservation_id)
        book.close_tenant(tenant)
        return book.ledger_lines()

real = lambda root: m.FileJournal(root / "l.txt")
fake = lambda root: m.MemoryJournal()

for label, tenant in [("plain", "acme"),
                      ("tenant name containing a newline", "ac\nme"),
                      ("tenant name containing a carriage return", "ac\rme"),
                      ("tenant name containing U+2028", "ac me")]:
    print(f"-- {label}")
    print(f"   real: {through(real, tenant)!r}")
    print(f"   fake: {through(fake, tenant)!r}")

print("-- direct on the port, a blank line appended")
with tempfile.TemporaryDirectory() as raw:
    r = m.FileJournal(Path(raw) / "l.txt"); f = m.MemoryJournal()
    for j in (r, f):
        j.append("COMMIT a 1 1"); j.append(""); j.append("CLOSE a 1")
    print(f"   real: {r.lines()!r}")
    print(f"   fake: {f.lines()!r}")
