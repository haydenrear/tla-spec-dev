#!/usr/bin/env python3
"""Assert the EV-01 twin fixtures still share one architecture experiment.

`ex4_pipeline_coherent` and `ex5_pipeline_divergent` must differ ONLY in
production code. The four files below are the whole input to the architecture
half of the eval; if any of them drifts, the twins are two different
experiments and every number measured across them is void.

    python3 examples/validation/check_twins.py

Exit 0 when the four are byte-identical and both behavioral suites are the same
file; exit 1 with a diff otherwise. It gates nothing in the toolchain -- it is
a fixture-integrity check EV-02 should run before it starts.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
A = ROOT / "ex4_pipeline_coherent"
B = ROOT / "ex5_pipeline_divergent"

SHARED = (
    "specs/program_model/Pipeline.tla",
    "specs/program_model/Pipeline.cfg",
    "specs/program_model/architecture_components.yaml",
    "specs/program_model/architecture_map.yaml",
    "tests/test_behavior.py",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    for rel in SHARED:
        left, right = A / rel, B / rel
        for path in (left, right):
            if not path.is_file():
                failures.append(f"MISSING {path.relative_to(ROOT)}")
        if not (left.is_file() and right.is_file()):
            continue
        dl, dr = digest(left), digest(right)
        status = "ok " if dl == dr else "DIFF"
        print(f"{status} {rel}  {dl[:16]}  {dr[:16]}")
        if dl != dr:
            failures.append(f"DIVERGED {rel}: {dl} != {dr}")

    if failures:
        print("\nTWIN INTEGRITY FAILED -- the twins are not the same experiment:")
        for line in failures:
            print(f"  {line}")
        return 1
    print("\nTwin integrity holds: the twins differ only in production code.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
