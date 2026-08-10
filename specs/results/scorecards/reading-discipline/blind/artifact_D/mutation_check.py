"""Evidence about the TESTS, not about the code.

`test_quota_ledger.py` passing tells you the tests agree with the code. It does
not tell you the tests would have noticed the code being wrong. This script
breaks the implementation in twelve specific ways and reports, for each, whether
the shared suite and my suite fail -- and, for any survivor, whether the mutant
is observationally different from the original at all.

    python3 mutation_check.py

Stdlib only. Writes to a temporary directory; touches nothing in this one.
"""

from __future__ import annotations

import importlib.util
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = (HERE / "quota_ledger.py").read_text()

REPO = HERE.parent.parent
SHARED_SUITE = REPO / "examples/validation/ab/tests/test_behavior.py"


def _mutate(old: str, new: str) -> str:
    assert old in SOURCE, f"mutation anchor not found: {old[:60]!r}"
    return SOURCE.replace(old, new, 1)


MUTANTS: dict[str, str] = {
    "M1  reserve: amount checked before closed": _mutate(
        "        if self._closed[tenant]:\n"
        "            return _rejected(TENANT_CLOSED)\n"
        "        if amount < 1:\n"
        "            return _rejected(AMOUNT_NOT_POSITIVE)",
        "        if amount < 1:\n"
        "            return _rejected(AMOUNT_NOT_POSITIVE)\n"
        "        if self._closed[tenant]:\n"
        "            return _rejected(TENANT_CLOSED)",
    ),
    "M2  quota_exceeded uses >= instead of >": _mutate(
        "if amount > self.available(tenant):", "if amount >= self.available(tenant):"
    ),
    "M3  commit hands the amount back to available": _mutate(
        "        self._committed[reservation.tenant] += reservation.amount",
        "        self._committed[reservation.tenant] += reservation.amount\n"
        "        self._quota[reservation.tenant] += reservation.amount",
    ),
    "M4  ids are reused once a slot frees up": _mutate(
        "        self._next_id += 1", "        self._next_id = len(self._outstanding) + 2"
    ),
    "M5  release writes a ledger line": _mutate(
        "        # No ledger write: a release is not a durable event.",
        "        self._append(f'RELEASE {reservation.tenant} {reservation.amount}')",
    ),
    "M6  close writes the quota, not the committed total": _mutate(
        'self._append(f"CLOSE {tenant} {self._committed[tenant]}")',
        'self._append(f"CLOSE {tenant} {self._quota[tenant]}")',
    ),
    "M7  outstanding_ids sorted as strings": _mutate(
        "return sorted(self._outstanding, key=lambda rid: int(rid[1:]))",
        "return sorted(self._outstanding)",
    ),
    "M8  close: outstanding checked before unknown_tenant": _mutate(
        "        if tenant not in self._quota:\n"
        "            return _rejected(UNKNOWN_TENANT)\n"
        "        if self._closed[tenant]:\n"
        "            return _rejected(TENANT_CLOSED)\n"
        "        if any(r.tenant == tenant for r in self._outstanding.values()):",
        "        if any(r.tenant == tenant for r in self._outstanding.values()):\n"
        "            return _rejected(OUTSTANDING_RESERVATIONS)\n"
        "        if tenant not in self._quota:\n"
        "            return _rejected(UNKNOWN_TENANT)\n"
        "        if self._closed[tenant]:\n"
        "            return _rejected(TENANT_CLOSED)\n"
        "        if False:",
    ),
    "M9  COMMIT running total is the amount, not the total": _mutate(
        'f"{self._committed[reservation.tenant]}"', 'f"{reservation.amount}"'
    ),
    "M10 close does not mark the tenant closed": _mutate(
        "        self._closed[tenant] = True\n", ""
    ),
    "M11 a rejected reserve still burns an id": _mutate(
        "        if amount > self.available(tenant):\n            return _rejected(QUOTA_EXCEEDED)",
        "        if amount > self.available(tenant):\n"
        "            self._next_id += 1\n"
        "            return _rejected(QUOTA_EXCEEDED)",
    ),
    "M12 ledger_lines keeps blank lines": _mutate(
        "return [line for line in text.splitlines() if line]", "return text.split(chr(10))"
    ),
}


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses resolves annotations through sys.modules
    spec.loader.exec_module(module)
    return module


def _observable(book, tenants):
    return (
        [book.available(t) for t in tenants],
        [book.committed(t) for t in tenants],
        [book.is_closed(t) for t in tenants],
        book.outstanding_ids(),
        book.ledger_lines(),
    )


def differential(original, mutant, workdir: Path, walks: int = 400, quota_max: int = 14) -> int:
    """How many random walks the mutant is observably different on.

    Zero does not prove equivalence -- it says this generator did not reach a
    distinguishing input, which is a different and weaker statement.
    """
    rng = random.Random(20260809)
    diverged = 0
    for _ in range(walks):
        quotas = {"acme": rng.randint(0, quota_max), "globex": rng.randint(0, quota_max)}
        a = original.QuotaLedger(dict(quotas), workdir / "a.txt")
        b = mutant.QuotaLedger(dict(quotas), workdir / "b.txt")
        tenants = list(quotas)
        for _ in range(40):
            operation = rng.choice(["reserve", "commit", "release", "close_tenant"])
            if operation == "reserve":
                args = (rng.choice(["acme", "globex", "nobody"]), rng.randint(-2, quota_max + 2))
            elif operation == "close_tenant":
                args = (rng.choice(["acme", "globex", "nobody"]),)
            else:
                args = (f"r{rng.randint(1, 20)}",)

            first = getattr(a, operation)(*args)
            second = getattr(b, operation)(*args)
            if (first.status, first.reason, first.reservation_id) != (
                second.status,
                second.reason,
                second.reservation_id,
            ) or _observable(a, tenants) != _observable(b, tenants):
                diverged += 1
                break
    return diverged


def _run_pytest(target: Path, impl_dir: Path, cwd: Path) -> bool:
    """True when the suite FAILS -- i.e. the mutant was caught."""
    env = dict(os.environ, QUOTA_LEDGER_DIR=str(impl_dir), QUOTA_LEDGER_IMPL="quota_ledger")
    done = subprocess.run(
        [sys.executable, "-m", "pytest", str(target), "-q", "-p", "no:cacheprovider"],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
    )
    return done.returncode != 0


def main() -> int:
    with tempfile.TemporaryDirectory() as raw:
        workdir = Path(raw)
        (workdir / "test_quota_ledger.py").write_text((HERE / "test_quota_ledger.py").read_text())
        original = _load(HERE / "quota_ledger.py", "quota_ledger_original")

        shared_available = SHARED_SUITE.exists()
        header = f"{'mutant':<48} {'mine':<7} {'shared':<7} differential"
        print(header)
        print("-" * len(header))

        survivors = []
        for label, code in MUTANTS.items():
            (workdir / "quota_ledger.py").write_text(code)
            mine = _run_pytest(workdir / "test_quota_ledger.py", workdir, workdir)
            shared = (
                _run_pytest(SHARED_SUITE, workdir, REPO) if shared_available else None
            )
            mutant = _load(workdir / "quota_ledger.py", f"mutant_{label.split()[0]}")
            diverged = differential(original, mutant, workdir)

            if not mine:
                survivors.append((label, diverged))
            print(
                f"{label:<48} {'caught' if mine else 'SURVIVED':<7} "
                f"{('caught' if shared else 'survived') if shared_available else 'n/a':<7} "
                f"{diverged}/400 walks differ"
            )

        print()
        for label, diverged in survivors:
            if diverged == 0:
                print(
                    f"{label.split()[0]} survives my suite AND showed no observable difference in "
                    f"400 walks -- read it as observationally equivalent, not as a coverage gap."
                )
            else:
                print(f"{label.split()[0]} survives my suite but IS observable: a real gap.")
        if not survivors:
            print("No survivors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
