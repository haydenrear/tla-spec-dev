"""Synthetic adapters for the MF-013 runner-level effect conformance tests.

Three adapters, each a deliberate specimen:

* :class:`DeclaredEffectAdapter` writes only where its port says it writes.
* :class:`UndeclaredEffectAdapter` writes somewhere it never declared. It is
  the specimen that must FAIL the run.
* :class:`JustifiedUndeclaredEffectAdapter` does exactly the same thing while
  carrying a recorded justification on the adapter itself. It must fail
  identically -- that is the inverse test.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


class DeclaredEffectAdapter:
    """Emits only on its declared port."""

    def run(self, case: Any, work_dir: Path | None = None) -> dict[str, Any]:
        # The runner already created the sandbox root before patching, so the
        # adapter only writes into it -- creating it here would itself be an
        # effect on the directory rather than on its contents.
        sandbox_root = Path(work_dir) / "sandbox" if work_dir else Path(".")
        (sandbox_root / "declared.txt").write_text("declared write", encoding="utf-8")
        return {}


class UndeclaredEffectAdapter:
    """Writes outside every declared port. The run must fail because of this."""

    def run(self, case: Any, work_dir: Path | None = None) -> dict[str, Any]:
        # The runner already created the sandbox root before patching, so the
        # adapter only writes into it -- creating it here would itself be an
        # effect on the directory rather than on its contents.
        sandbox_root = Path(work_dir) / "sandbox" if work_dir else Path(".")
        (sandbox_root / "declared.txt").write_text("declared write", encoding="utf-8")
        # The undeclared effect: a sibling directory no port covers.
        stray = Path(work_dir).parent / "undeclared-store"
        stray.mkdir(parents=True, exist_ok=True)
        (stray / "leaked.txt").write_text("nobody modeled this", encoding="utf-8")
        return {}


class JustifiedUndeclaredEffectAdapter(UndeclaredEffectAdapter):
    """Identical behavior, plus every shape of recorded justification.

    None of these attributes are consulted by anything. They exist so the test
    can assert that their presence changes nothing -- the regression guard
    against reintroducing out-of-contract suppression, withdrawn 2026-07-18.
    """

    out_of_contract = True
    justification = "legacy cache directory; accepted by architecture review 2026-07-01"
    effect_waiver = ["**/undeclared-store/**"]
    allow_undeclared = True
