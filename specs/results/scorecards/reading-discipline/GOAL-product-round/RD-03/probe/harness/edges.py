"""Targeted edge cases the random generator cannot reach. Each is read against
FEATURE.md by hand afterwards; a divergence between trees is a candidate defect,
an agreement is not evidence of correctness."""
import sys, importlib, tempfile, json
from pathlib import Path
tree = sys.argv[1]
sys.path.insert(0, tree)
m = importlib.import_module("quota_ledger")
Q = {"acme": 20, "globex": 4}
out = {}

def attempt(label, fn):
    try:
        out[label] = fn()
    except Exception as e:
        out[label] = f"RAISED {type(e).__name__}: {e}"

with tempfile.TemporaryDirectory() as raw:
    root = Path(raw)

    def nested_parent():
        book = m.QuotaLedger(dict(Q), root / "does" / "not" / "exist" / "l.txt")
        return book.ledger_lines()
    attempt("ledger path with a missing parent directory", nested_parent)

    def past_r9():
        book = m.QuotaLedger(dict(Q), root / "a.txt")
        for _ in range(12):
            book.reserve("acme", 1)
        return book.outstanding_ids()
    attempt("outstanding_ids past r9", past_r9)

    def two_books_one_path():
        first = m.QuotaLedger(dict(Q), root / "shared.txt")
        first.commit(first.reserve("acme", 3).reservation_id)
        second = m.QuotaLedger(dict(Q), root / "shared.txt")
        return {"first.ledger_lines": first.ledger_lines(),
                "first.committed": first.committed("acme"),
                "second.ledger_lines": second.ledger_lines()}
    attempt("two ledgers constructed on one path", two_books_one_path)

    def bool_amount():
        book = m.QuotaLedger(dict(Q), root / "b.txt")
        r = book.reserve("acme", True)
        return [r.status, getattr(r, "reason", None), book.available("acme")]
    attempt("reserve(t, True)", bool_amount)

    def tenant_with_space():
        book = m.QuotaLedger({"two words": 5}, root / "c.txt")
        book.commit(book.reserve("two words", 2).reservation_id)
        book.close_tenant("two words")
        return book.ledger_lines()
    attempt("tenant name containing a space", tenant_with_space)

    def empty_quotas():
        book = m.QuotaLedger({}, root / "d.txt")
        return [book.reserve("acme", 1).reason, book.close_tenant("acme").reason,
                book.ledger_lines()]
    attempt("empty quota mapping", empty_quotas)

    def zero_quota_close():
        book = m.QuotaLedger({"z": 0}, root / "e.txt")
        return [book.reserve("z", 1).reason, book.close_tenant("z").status,
                book.ledger_lines()]
    attempt("tenant with quota 0", zero_quota_close)

    def reserve_after_close_then_query():
        book = m.QuotaLedger(dict(Q), root / "f.txt")
        book.close_tenant("globex")
        return [book.available("globex"), book.is_closed("globex"),
                book.reserve("globex", 0).reason]
    attempt("reserve(closed, 0) reason precedence", reserve_after_close_then_query)

    def negative_quota():
        book = m.QuotaLedger({"n": -3}, root / "g.txt")
        return [book.available("n"), book.reserve("n", 1).reason,
                book.close_tenant("n").status, book.ledger_lines()]
    attempt("tenant with a negative quota", negative_quota)

print(json.dumps(out, indent=1, default=str))
