"""Arm B's own fake, composed at arm B's own port. NOT AN EDIT TO ARM B.

Arm B is a sealed, judged artifact. Nothing here changes a byte of it. This
module calls only names arm B itself exports from `quota_ledger/__init__.py`:

    __all__ = ["QuotaLedger", "Ledger", "Journal", "Result", "Reservation",
               "FileJournal", "InMemoryJournal"]

and composes two of them the way arm B's own docstring says they compose:

    "The swap, in one sentence: replace `FileJournal(ledger_path)` on the line
     below with `InMemoryJournal()` and no domain file changes."
                        -- arms/arm_b/quota_ledger/__init__.py

That sentence is the claim arm B earned `D3 = 4` for on both blind judges, and
until this file nothing outside arm B's own tests had ever taken it up. The
whole of PA-04 is the observation that the sentence was true and unexercised:
the port removes places for some faults to live and creates a region no shared
oracle reaches, and the fake that earned the score was verified by nothing
outside the arm.

WHY THIS IS NOT SEEDING, AND WHY IT IS NOT EDITING THE ARM

It adds no behaviour and changes no verdict on any existing column. It is a
COMPOSITION POINT, the same artifact `examples/validation/ab/reference_ports/
quota_ledger_fake.py` is for the reference tree, written in the measurement
tree rather than in the arm precisely so that the arm stays byte-identical to
what was judged. If arm B had shipped this file itself, its `--wiring fake`
column would be identical.

WHAT IT PROVES AND WHAT IT DOES NOT

It proves the swap is constructible from arm B's public surface. It does NOT
prove an arm would produce this shape -- arm B did produce it, which is the
measured fact, and arm A did not, which is the other one.
"""

from __future__ import annotations

import importlib
import os
from typing import Any, Mapping


def QuotaLedger(quotas: Mapping[str, int], ledger_path: str | os.PathLike[str]) -> Any:
    """Arm B's `Ledger`, composed over arm B's `InMemoryJournal`.

    `ledger_path` is accepted and unused, exactly as it is in the reference
    tree's fake composition point: the fake has nothing to put at a path. The
    parameter stays so that this module is substitutable for the real
    composition point without any caller knowing which it got -- which is what
    makes the case list identical across the two wirings.
    """
    arm = importlib.import_module("quota_ledger")
    return arm.Ledger(dict(quotas), arm.InMemoryJournal())
