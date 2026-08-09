"""Per-tree re-anchoring of examples/validation/ab/seeded_faults.toml.

The catalogue's literal find/replace pairs are anchored on `reference/` and
`reference_ports/` and match none of these six trees. Each entry below is
re-anchored BY HAND from the mutant's `semantic` field, and every one is
checked by the driver in two ways: each `find` must occur EXACTLY ONCE in its
file, and the mutant's semantic witness must be False on the pristine tree and
True on the mutated tree. A patch that fails either check is a REPORTED HOLE.

A mutant may need more than one edit on a tree whose representation differs
from the reference's; those are listed and all of them are exactly-once checked.

INEXPRESSIBLE means the tree has no surface the semantic can be applied to. It
is a hole in the row, never a survivor.
"""

from __future__ import annotations

INEXPRESSIBLE = "INEXPRESSIBLE"

# --------------------------------------------------------------------------
# artifact_Z  (effectful, single module, `available` STORED)
# --------------------------------------------------------------------------
Z = {
    "M01": [("quota_ledger.py",
             "        if amount < 1:\n",
             "        if amount < 0:  # MUTANT M01\n")],
    "M02": [("quota_ledger.py",
             "        if amount > record.available:\n",
             "        if amount > record.quota:  # MUTANT M02\n")],
    "M03": [("quota_ledger.py",
             "        if record.outstanding > 0:\n",
             "        if False:  # MUTANT M03\n")],
    "M04": [("quota_ledger.py",
             '        self._append(f"COMMIT {reservation.tenant} {reservation.amount} {record.committed}")\n',
             '        self._append(f"COMMIT {reservation.tenant} {reservation.amount} {record.committed - reservation.amount}")  # MUTANT M04\n')],
    "M05": [("quota_ledger.py",
             '        self._append(f"CLOSE {tenant} {record.committed}")\n',
             '        try:  # MUTANT M05\n'
             '            self._append(f"CLOSE {tenant} 0")\n'
             '        except Exception:\n'
             '            pass\n')],
    "M06": [("quota_ledger.py",
             "        record.available += reservation.amount\n"
             "        # Nothing durable: a release is not a ledger event.\n"
             "        return Result.accepted()\n",
             "        record.available += reservation.amount\n"
             "        return Result.rejected(Reason.UNKNOWN_RESERVATION)  # MUTANT M06\n")],
    "M07": [("quota_ledger.py",
             "        record.available -= amount\n",
             "        record.available -= amount + 1  # MUTANT M07\n")],
    "M08": [("quota_ledger.py",
             "        record.committed += reservation.amount\n",
             "        record.committed += reservation.amount\n"
             "        record.available += reservation.amount  # MUTANT M08\n")],
    "M09": [("quota_ledger.py",
             '        with open(self._path, "a", encoding="utf-8") as handle:\n'
             '            handle.write(line + "\\n")\n'
             '            handle.flush()\n'
             '            os.fsync(handle.fileno())\n',
             '        existing = self._path.read_text(encoding="utf-8")  # MUTANT M09\n'
             '        self._path.write_text(line + "\\n" + existing, encoding="utf-8")\n')],
    "M10": [("quota_ledger.py",
             "        record.available += reservation.amount\n"
             "        # Nothing durable: a release is not a ledger event.\n",
             "        record.available += reservation.amount * 2  # MUTANT M10\n"
             "        # Nothing durable: a release is not a ledger event.\n")],
    "PA-M11": [("quota_ledger.py",
                "        return [line for line in text.splitlines() if line.strip()]\n",
                '        return [line for line in text.splitlines() if line.strip() and not line.startswith("CLOSE")]  # MUTANT PA-M11\n')],
    "PA-M12": INEXPRESSIBLE,
    "PA-M13": INEXPRESSIBLE,
    "PA-M14": [("quota_ledger.py",
                "        self._reservations[reservation_id] = _Reservation(tenant=tenant, amount=amount)\n",
                "        self._reservations[reservation_id] = _Reservation(tenant=tenant, amount=amount + 1)  # MUTANT PA-M14\n")],
    "FI-M15": [("quota_ledger.py",
                "        record.committed += reservation.amount\n",
                "        record.committed += reservation.amount + 1  # MUTANT FI-M15\n")],
}

# --------------------------------------------------------------------------
# artifact_M  (effectful, revision of Z; `available` STORED, no `quota` field,
#              no `outstanding` counter)
# --------------------------------------------------------------------------
ARTIFACT_M = dict(Z)
ARTIFACT_M["M02"] = [
    # The revision deleted the `quota` field, so the tenant's TOTAL quota is no
    # longer recorded anywhere. Restoring it is part of the mutation; without
    # it the semantic has nothing to compare against.
    ("quota_ledger.py",
     "    available: int\n    committed: int = 0\n",
     "    available: int\n    quota: int = 0  # MUTANT M02\n    committed: int = 0\n"),
    ("quota_ledger.py",
     "            name: _Tenant(available=quota) for name, quota in quotas.items()\n",
     "            name: _Tenant(available=quota, quota=quota) for name, quota in quotas.items()  # MUTANT M02\n"),
    ("quota_ledger.py",
     "        if amount > record.available:\n",
     "        if amount > record.quota:  # MUTANT M02\n"),
]
ARTIFACT_M["M03"] = [
    ("quota_ledger.py",
     "        if any(held.tenant == tenant for held in self._reservations.values()):\n",
     "        if False:  # MUTANT M03\n"),
]

# --------------------------------------------------------------------------
# artifact_N  (effectful, single module, `available` DERIVED from a stored
#              per-tenant `_held` running total)
# --------------------------------------------------------------------------
N = {
    "M01": [("quota_ledger.py",
             "        if amount < 1:\n",
             "        if amount < 0:  # MUTANT M01\n")],
    "M02": [("quota_ledger.py",
             "        if amount > self.available(tenant):\n",
             "        if amount > self._quota[tenant]:  # MUTANT M02\n")],
    "M03": [("quota_ledger.py",
             "        if any(r.tenant == tenant for r in self._outstanding.values()):\n",
             "        if False:  # MUTANT M03\n")],
    "M04": [("quota_ledger.py",
             '            f"{self._committed[reservation.tenant]}"\n',
             '            f"{self._committed[reservation.tenant] - reservation.amount}"  # MUTANT M04\n')],
    "M05": [("quota_ledger.py",
             '        self._append(f"CLOSE {tenant} {self._committed[tenant]}")\n',
             '        try:  # MUTANT M05\n'
             '            self._append(f"CLOSE {tenant} 0")\n'
             '        except Exception:\n'
             '            pass\n')],
    "M06": [("quota_ledger.py",
             "        # No ledger write: a release is not a durable event.\n"
             "        return _accepted(reservation_id)\n",
             "        return _rejected(UNKNOWN_RESERVATION)  # MUTANT M06\n")],
    "M07": [("quota_ledger.py",
             "        self._held[tenant] += amount\n",
             "        self._held[tenant] += amount + 1  # MUTANT M07\n")],
    "M08": [("quota_ledger.py",
             "        self._held[reservation.tenant] -= reservation.amount\n"
             "        self._committed[reservation.tenant] += reservation.amount\n",
             "        self._held[reservation.tenant] -= reservation.amount * 2  # MUTANT M08\n"
             "        self._committed[reservation.tenant] += reservation.amount\n")],
    "M09": [("quota_ledger.py",
             '        with self._ledger_path.open("a", encoding="utf-8") as handle:\n'
             '            handle.write(line + "\\n")\n',
             '        existing = self._ledger_path.read_text(encoding="utf-8")  # MUTANT M09\n'
             '        self._ledger_path.write_text(line + "\\n" + existing, encoding="utf-8")\n')],
    "M10": [("quota_ledger.py",
             "        self._held[reservation.tenant] -= reservation.amount\n"
             "        # No ledger write: a release is not a durable event.\n",
             "        self._held[reservation.tenant] -= reservation.amount * 2  # MUTANT M10\n"
             "        # No ledger write: a release is not a durable event.\n")],
    "PA-M11": [("quota_ledger.py",
                "        return [line for line in text.splitlines() if line]\n",
                '        return [line for line in text.splitlines() if line and not line.startswith("CLOSE")]  # MUTANT PA-M11\n')],
    "PA-M12": INEXPRESSIBLE,
    "PA-M13": INEXPRESSIBLE,
    "PA-M14": [("quota_ledger.py",
                "        self._outstanding[reservation_id] = Reservation(tenant, amount)\n",
                "        self._outstanding[reservation_id] = Reservation(tenant, amount + 1)  # MUTANT PA-M14\n")],
    "FI-M15": [("quota_ledger.py",
                "        self._committed[reservation.tenant] += reservation.amount\n",
                "        self._committed[reservation.tenant] += reservation.amount + 1  # MUTANT FI-M15\n")],
}

# --------------------------------------------------------------------------
# artifact_D  (effectful, revision of N; `available` DERIVED by walking the
#              outstanding table -- there is no stored `available` and no
#              stored held total anywhere)
# --------------------------------------------------------------------------
D = dict(N)
D["M06"] = N["M06"]
# M07's semantic is "available(t) drops by n+1 AND NOTHING ELSE MOVES". On a
# tree that stores neither `available` nor a held total there is no line that
# moves `available` alone: every lever also moves `committed`, the reservation's
# own amount, or the quota. This is the catalogue's own
# [pa_measured_control_audit] finding about arm B, re-encountered.
#
# DEMONSTRATED, NOT DECLARED. The nearest candidate re-anchoring is seeded here
# and RUN, so the hole is a measured failure of the semantic witness rather than
# an assertion that nobody checked. `absent` and `checked, none found` are
# different claims.
D["M07"] = [("quota_ledger.py",
             "        self._outstanding[reservation_id] = Reservation(tenant, amount)\n",
             "        self._outstanding[reservation_id] = Reservation(tenant, amount + 1)  # M07 CANDIDATE\n")]
D["M07_candidate_note"] = (
    "nearest anchoring: the only line on the accept path that can move a derived "
    "`available` by n+1 is the amount recorded on the reservation, which also "
    "makes the later commit credit n+1 -- a different row (PA-M14), not M07."
)
D["M08"] = [("quota_ledger.py",
             "        self._committed[reservation.tenant] += reservation.amount\n",
             "        self._committed[reservation.tenant] += reservation.amount\n"
             "        self._quota[reservation.tenant] += reservation.amount  # MUTANT M08\n")]
D["M10"] = [("quota_ledger.py",
             "        del self._outstanding[reservation_id]\n"
             "        # No ledger write: a release is not a durable event.\n",
             "        del self._outstanding[reservation_id]\n"
             "        self._quota[reservation.tenant] += reservation.amount  # MUTANT M10\n"
             "        # No ledger write: a release is not a durable event.\n")]

# --------------------------------------------------------------------------
# artifact_E / artifact_F  (ports-and-adapters; domain + Journal port + two
#              adapters; `available` DERIVED from the live holds)
# --------------------------------------------------------------------------
E = {
    "M01": [("quota_ledger/domain.py",
             "        if amount < 1:\n",
             "        if amount < 0:  # MUTANT M01\n")],
    "M02": [("quota_ledger/domain.py",
             "        if amount > self.available(tenant):\n",
             "        if amount > account.quota:  # MUTANT M02\n")],
    "M03": [("quota_ledger/domain.py",
             "        if self._held_by(tenant):\n",
             "        if False:  # MUTANT M03\n")],
    "M04": [("quota_ledger/domain.py",
             '        self._journal.append(f"COMMIT {hold.tenant} {hold.amount} {account.committed}")\n',
             '        self._journal.append(f"COMMIT {hold.tenant} {hold.amount} {account.committed - hold.amount}")  # MUTANT M04\n')],
    "M05": [("quota_ledger/domain.py",
             '        self._journal.append(f"CLOSE {tenant} {account.committed}")\n',
             '        try:  # MUTANT M05\n'
             '            self._journal.append(f"CLOSE {tenant} 0")\n'
             '        except Exception:\n'
             '            pass\n')],
    "M06": [("quota_ledger/domain.py",
             '        if self._holds.pop(reservation_id, None) is None:\n'
             '            return Result.reject("unknown_reservation")\n'
             '        return Result.accept()\n',
             '        if self._holds.pop(reservation_id, None) is None:\n'
             '            return Result.reject("unknown_reservation")\n'
             '        return Result.reject("unknown_reservation")  # MUTANT M06\n')],
    # Same hole as artifact_D, same reason: `available` is derived here too.
    # Seeded and RUN as the nearest candidate so the hole is measured.
    "M07": [("quota_ledger/domain.py",
             "        self._holds[reservation_id] = _Hold(tenant, amount)\n",
             "        self._holds[reservation_id] = _Hold(tenant, amount + 1)  # M07 CANDIDATE\n")],
    "M08": [("quota_ledger/domain.py",
             "        account.committed += hold.amount\n",
             "        account.committed += hold.amount\n"
             "        account.quota += hold.amount  # MUTANT M08\n")],
    "M09": [("quota_ledger/file_journal.py",
             '        with self._path.open("a", encoding="utf-8") as handle:\n'
             '            handle.write(line + "\\n")\n',
             '        existing = self._path.read_text(encoding="utf-8")  # MUTANT M09\n'
             '        self._path.write_text(line + "\\n" + existing, encoding="utf-8")\n')],
    "M10": [("quota_ledger/domain.py",
             '        if self._holds.pop(reservation_id, None) is None:\n'
             '            return Result.reject("unknown_reservation")\n'
             '        return Result.accept()\n',
             '        _released = self._holds.pop(reservation_id, None)  # MUTANT M10\n'
             '        if _released is None:\n'
             '            return Result.reject("unknown_reservation")\n'
             '        self._accounts[_released.tenant].quota += _released.amount  # MUTANT M10\n'
             '        return Result.accept()\n')],
    "PA-M11": [("quota_ledger/file_journal.py",
                '        return [line for line in self._path.read_text(encoding="utf-8").splitlines() if line]\n',
                '        return [line for line in self._path.read_text(encoding="utf-8").splitlines() if line and not line.startswith("CLOSE")]  # MUTANT PA-M11\n')],
    "PA-M12": [("quota_ledger/memory_journal.py",
                "        return list(self._lines)\n",
                '        return [line for line in self._lines if not line.startswith("CLOSE")]  # MUTANT PA-M12\n')],
    "PA-M13": [("quota_ledger/memory_journal.py",
                "        self._lines.append(line)\n",
                '        self._lines.append(" ".join(line.split()[:3]))  # MUTANT PA-M13\n')],
    "PA-M14": [("quota_ledger/domain.py",
                "        self._holds[reservation_id] = _Hold(tenant, amount)\n",
                "        self._holds[reservation_id] = _Hold(tenant, amount + 1)  # MUTANT PA-M14\n")],
    "FI-M15": [("quota_ledger/domain.py",
                "        account.committed += hold.amount\n",
                "        account.committed += hold.amount + 1  # MUTANT FI-M15\n")],
}

TREES = {
    "artifact_Z": Z,
    "artifact_M": ARTIFACT_M,
    "artifact_N": N,
    "artifact_D": D,
    "artifact_E": E,
    "artifact_F": dict(E),
}

#: Which wiring the semantic witness must run through. Everything defaults to
#: the real one -- the composition point FEATURE.md's constructor picks.
WITNESS_WIRING = {
    ("artifact_E", "PA-M12"): "fake",
    ("artifact_E", "PA-M13"): "fake",
    ("artifact_F", "PA-M12"): "fake",
    ("artifact_F", "PA-M13"): "fake",
}

#: Architecture value, supplied by the ticket. Not re-derived here.
ARCHITECTURE = {
    "artifact_Z": "effectful",
    "artifact_M": "effectful",
    "artifact_N": "effectful",
    "artifact_D": "effectful",
    "artifact_E": "ports-and-adapters",
    "artifact_F": "ports-and-adapters",
}

OWN_TESTS = {
    "artifact_Z": ["test_quota_ledger.py"],
    "artifact_M": ["test_quota_ledger.py"],
    "artifact_N": ["test_quota_ledger.py"],
    "artifact_D": ["test_quota_ledger.py"],
    "artifact_E": ["tests"],
    "artifact_F": ["tests"],
}
