"""Semantic witnesses. One per catalogue mutant, written from the `semantic`
field in examples/validation/ab/seeded_faults.toml and from FEATURE.md only.

Each returns True iff the declared semantic is OBSERVED through the feature's
own public API. The driver runs every witness on the pristine tree (must be
False) and on the mutated tree (must be True). A witness that does not separate
the two trees means the re-anchoring did not reproduce the semantic, and that
cell is a REPORTED HOLE -- never a survivor.

`make` builds a ledger: make(quotas: dict, path: Path) -> QuotaLedger-like.
"""

from __future__ import annotations

QUOTAS = {"acme": 10, "globex": 4}


def _lines(book):
    return list(book.ledger_lines())


# -- guard relaxation ------------------------------------------------------

def M01(make, path):
    """reserve(t, 0) is ACCEPTED with a fresh id instead of rejected."""
    book = make(dict(QUOTAS), path)
    result = book.reserve("acme", 0)
    return result.status == "accepted" and result.reservation_id is not None


def M02(make, path):
    """quota_exceeded compares against TOTAL quota, so two reserves that each
    fit the quota but not the remainder are both accepted and available goes
    negative."""
    book = make(dict(QUOTAS), path)
    first = book.reserve("acme", 6)
    second = book.reserve("acme", 6)
    return (
        first.status == "accepted"
        and second.status == "accepted"
        and book.available("acme") < 0
    )


def M03(make, path):
    """close_tenant is accepted while the tenant has a live reservation, and a
    CLOSE line is written."""
    book = make(dict(QUOTAS), path)
    book.reserve("acme", 3)
    result = book.close_tenant("acme")
    return (
        result.status == "accepted"
        and book.is_closed("acme")
        and any(line.startswith("CLOSE acme") for line in _lines(book))
    )


# -- durable content -------------------------------------------------------

def M04(make, path):
    """Each COMMIT line's running total is the total BEFORE this commit;
    in-memory committed() is correct."""
    book = make(dict(QUOTAS), path)
    book.commit(book.reserve("acme", 3).reservation_id)
    lines = _lines(book)
    if book.committed("acme") != 3 or len(lines) != 1:
        return False
    parts = lines[0].split()
    return parts[:3] == ["COMMIT", "acme", "3"] and parts[3] == "0"


def M05(make, path):
    """close_tenant writes a CLOSE line whose total is literally 0 regardless
    of what was committed; committed() and the status stay correct."""
    book = make(dict(QUOTAS), path)
    book.commit(book.reserve("acme", 3).reservation_id)
    result = book.close_tenant("acme")
    lines = _lines(book)
    return (
        result.status == "accepted"
        and book.committed("acme") == 3
        and lines[-1] == "CLOSE acme 0"
    )


# -- output oracle ---------------------------------------------------------

def M06(make, path):
    """release applies its correct effect and then returns
    rejected/unknown_reservation."""
    book = make(dict(QUOTAS), path)
    rid = book.reserve("acme", 3).reservation_id
    result = book.release(rid)
    return (
        result.status == "rejected"
        and result.reason == "unknown_reservation"
        and book.available("acme") == 10
        and list(book.outstanding_ids()) == []
        and _lines(book) == []
    )


# -- wrong value -----------------------------------------------------------

def M07(make, path):
    """reserve(t, n) reduces available(t) by n+1 -- AND NOTHING ELSE.

    The second clause is what makes this M07 rather than PA-M14. A mutation
    that records amount+1 ON THE RESERVATION also moves `available` by n+1 on
    a tree that derives it, and would pass a witness that only read
    `available`; it is a different row of the catalogue, and its later commit
    credits n+1. So the witness also requires the reservation's own amount to
    be untouched, read through what a commit credits.
    """
    book = make(dict(QUOTAS), path)
    result = book.reserve("acme", 3)
    if not (result.status == "accepted" and book.available("acme") == 6):
        return False
    book.commit(result.reservation_id)
    return book.committed("acme") == 3 and _lines(book) == ["COMMIT acme 3 3"]


def M10(make, path):
    """release(r) credits available(t) with 2x the reservation amount."""
    book = make(dict(QUOTAS), path)
    rid = book.reserve("acme", 3).reservation_id
    result = book.release(rid)
    return result.status == "accepted" and book.available("acme") == 13


# -- cross aspect ----------------------------------------------------------

def M08(make, path):
    """commit performs the correct LEDGER effect AND returns the amount to
    available(t). committed() and every ledger line stay correct."""
    book = make(dict(QUOTAS), path)
    book.commit(book.reserve("acme", 3).reservation_id)
    return (
        book.available("acme") == 10
        and book.committed("acme") == 3
        and _lines(book) == ["COMMIT acme 3 3"]
    )


# -- ordering (negative control) -------------------------------------------

def M09(make, path):
    """Ledger lines are prepended. The SET of lines is identical to correct
    behaviour; only R5's order is violated."""
    book = make(dict(QUOTAS), path)
    acme = book.reserve("acme", 2).reservation_id
    globex = book.reserve("globex", 1).reservation_id
    book.commit(globex)
    book.commit(acme)
    correct = ["COMMIT globex 1 1", "COMMIT acme 2 2"]
    lines = _lines(book)
    return lines == list(reversed(correct)) and sorted(lines) == sorted(correct)


# -- adapter internal ------------------------------------------------------

def PA_M11(make, path):
    """The durable read-back filters out every line beginning CLOSE. The bytes
    written are correct; committed(), is_closed() and available() are correct."""
    book = make(dict(QUOTAS), path)
    book.commit(book.reserve("acme", 3).reservation_id)
    book.close_tenant("acme")
    return (
        book.is_closed("acme")
        and book.committed("acme") == 3
        and _lines(book) == ["COMMIT acme 3 3"]
    )


def PA_M13(make, path):
    """Every stored line is truncated to its first three whitespace fields, so
    COMMIT lines lose their running total and CLOSE lines are unaffected."""
    book = make(dict(QUOTAS), path)
    book.commit(book.reserve("acme", 3).reservation_id)
    book.close_tenant("acme")
    return _lines(book) == ["COMMIT acme 3", "CLOSE acme 3"]


# -- the two later positive controls ---------------------------------------

def PA_M14(make, path):
    """The reservation created by an ACCEPTED reserve records amount+1. The
    representation-independent observable is what a later commit credits.

    CORRECTED DURING THE RUN, disclosed rather than quietly fixed. The first
    form also asserted the COMMIT line read `COMMIT acme 3 4`. That was wrong
    about the semantic, not about any tree: a tree whose COMMIT line takes its
    amount field from the STORED reservation writes `COMMIT acme 4 4`, and a
    tree that uses the call parameter writes `COMMIT acme 3 4`. Both carry the
    declared semantic. The over-specified clause reported artifact_Z as a hole
    it is not.
    """
    book = make(dict(QUOTAS), path)
    rid = book.reserve("acme", 3).reservation_id
    book.commit(rid)
    return book.committed("acme") == 4


def PA_M14_inert_after_one_reserve(make, path):
    """The other half of PA-M14's declared control property: nothing observable
    moves after ONE accepted reserve. Reported, not used as the witness."""
    book = make(dict(QUOTAS), path)
    book.reserve("acme", 3)
    return book.available("acme") == 7


def FI_M15(make, path):
    """commit(r) adds amount+1 to committed(t) and the COMMIT line's running
    total is one too large.

    CORRECTED DURING THE RUN, disclosed rather than quietly fixed. The first
    form also required `available(t) == 7`, i.e. CONFINEMENT to the port's
    region. The catalogue's own `re_anchoring_rule` for this row forbids that
    test in as many words -- "NOTE WHAT THE PROPERTY DOES NOT REQUIRE:
    confinement ... The probe therefore tests INCLUSION -- at least one moved
    observable inside the region -- and REPORTS the full moved set". A tree
    that derives `available` from `committed` moves `available` too, and the
    confinement clause reported artifact_N, artifact_D, artifact_E and
    artifact_F as holes they are not. The full moved set is reported per
    (tree, mutant) by the driver instead.
    """
    book = make(dict(QUOTAS), path)
    rid = book.reserve("acme", 3).reservation_id
    book.commit(rid)
    return book.committed("acme") == 4 and _lines(book) == ["COMMIT acme 3 4"]


# -- fake-side rows, only meaningful where a fake adapter exists ------------

def PA_M12(make, path):
    """The read-back filters out every line beginning CLOSE -- same observable
    as PA-M11, through the fake wiring."""
    return PA_M11(make, path)


def moved_observables(make, path):
    """Every observable FEATURE.md names, after each step of one fixed
    sequence. The driver diffs pristine against mutated and reports which
    observables a mutant actually moves -- the INCLUSION report the FI-M15
    re-anchoring rule asks for, and the evidence that an INEXPRESSIBLE or a
    HOLE verdict is about the tree rather than about a witness."""
    book = make(dict(QUOTAS), path)
    trace = []

    def step(label, result=None):
        trace.append({
            "step": label,
            "status": None if result is None else result.status,
            "reason": None if result is None else getattr(result, "reason", None),
            "reservation_id": None if result is None else getattr(result, "reservation_id", None),
            "available": {t: book.available(t) for t in QUOTAS},
            "committed": {t: book.committed(t) for t in QUOTAS},
            "closed": {t: book.is_closed(t) for t in QUOTAS},
            "outstanding": list(book.outstanding_ids()),
            "ledger": _lines(book),
        })

    step("construct")
    first = book.reserve("acme", 3)
    step("reserve acme 3", first)
    step("reserve acme 0", book.reserve("acme", 0))
    second = book.reserve("globex", 2)
    step("reserve globex 2", second)
    step("commit r1", book.commit(first.reservation_id))
    step("release r3", book.release(second.reservation_id))
    step("close acme", book.close_tenant("acme"))
    step("close acme again", book.close_tenant("acme"))
    return trace


WITNESSES = {
    "M01": M01, "M02": M02, "M03": M03, "M04": M04, "M05": M05,
    "M06": M06, "M07": M07, "M08": M08, "M09": M09, "M10": M10,
    "PA-M11": PA_M11, "PA-M12": PA_M12, "PA-M13": PA_M13,
    "PA-M14": PA_M14, "FI-M15": FI_M15,
}
