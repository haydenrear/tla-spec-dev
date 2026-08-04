"""Reality witnesses: proof that a mutant is a FAULT and not an equivalent one.

A negative control's whole job is to survive. That makes it the one row in a
catalogue where "nothing happened" is the expected result -- and therefore the
one row where an EQUIVALENT MUTANT is indistinguishable from a working control.
A mutant that changes no observable behaviour survives every instrument for a
reason that has nothing to do with what any instrument can see, and reporting it
as "the corpus structurally cannot see this" would be a false claim about the
corpus.

So a mutant may declare a `reality_witness`. The driver runs it against the
PRISTINE tree (it must report False: the fault is absent) and against the
MUTATED tree (it must report True: the fault is present). Only then is the row
allowed to serve as a control. If a witness does not separate the two trees, the
mutant is reported as EQUIVALENT_OR_UNWITNESSED and decides nothing.

A witness is deliberately NOT one of the instruments. It reaches the fault by
the shortest path available -- the feature's own public API, read against
FEATURE.md -- because its question is "is this a real defect", not "can the
instruments find it".
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def outstanding_ids_not_ascending(module: Any, work_dir: Path) -> bool:
    """FEATURE.md: `outstanding_ids()` returns live ids ASCENDING.

    Needs two live reservations; with one, ascending and descending coincide,
    which is exactly why the hand-written suite does not catch this (it never
    asserts the order of more than one id, and its `snapshot()` comparisons
    compare a book against itself).
    """
    book = module.QuotaLedger({"acme": 10}, work_dir / "witness.txt")
    book.reserve("acme", 1)
    book.reserve("acme", 1)
    ids = list(book.outstanding_ids())
    return ids != sorted(ids)
