"""Two adapters for ONE port, differing only in which implementation they wire.

PA-04. These are what a `[ports."ledger.LedgerAppendPort"]` binding names:

    adapter = "port_journal_adapters:RealJournalAdapter"   # FileJournal
    fake    = "port_journal_adapters:FakeJournalAdapter"   # InMemoryJournal

`--wiring real` loads the first, `--wiring fake` the second, over the IDENTICAL
generated case list. Everything else about the two classes is the same code:
the same `can_run` skip rules, the same state installation, the same
projection, the same comparison. If a number moves between the two columns, the
only thing that differed is which implementation of `LedgerJournal` the domain
was composed over -- which is the claim the whole ticket rests on.

WHY THESE ARE NOT `oracle.PositiveAdapter` / `oracle.NegativeAdapter`

They mostly are: `can_run`, `_snapshot`, `_call`, `_to_projection` and every
skip rule are IMPORTED from `examples/validation/ab/eval/oracle.py` and not
reimplemented, so the executability accounting here is the same accounting the
sealed runs used and the counts are comparable to theirs. Only `_build` is
local, for two reasons that are both about the port:

1.  The composition point is chosen PER ADAPTER rather than once per process
    from an environment variable. An env var would make the wiring a property
    of how the run was invoked; the acceptance criterion is that it is a
    property of the mapping, readable there.
2.  The before-state ledger is seeded THROUGH THE PORT rather than by writing
    the file. See `ports_binding.seed_journal` for why writing the file is not
    merely inconvenient but wrong here.

WHAT THESE ADAPTERS DO NOT DO

They do not assert that the two wirings AGREE. A parity test between a real
adapter and its fake passes when the domain is wrong, because both wirings are
wrong together. Both columns are compared against the MODEL's expected
after-state, which is the same standard the hand-written suite holds them to.
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[5]
_AB_EVAL = _REPO_ROOT / "examples/validation/ab/eval"
_RERUN_MEASURE = _REPO_ROOT / "specs/results/scorecards/hexagonal-prompting-rerun/measure"

for _entry in (str(_HERE), str(_AB_EVAL), str(_RERUN_MEASURE)):
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

# `oracle` resolves its binding at import time. Point it at this tree's binding
# before importing it, and never overwrite a binding a caller already chose.
os.environ.setdefault("QUOTA_LEDGER_BINDING", "ports_binding")

import oracle  # noqa: E402


class _JournalPortAdapter:
    """One declared port, one implementation of it, every case in the corpus.

    A single class handles both polarities because a mapping binds one adapter
    per label and a port corpus generated with `--negative-cases with-positive`
    carries both. The polarity is read off the case's own label, which is what
    `run_controls.py` does with the same corpus.
    """

    #: The composition point this adapter wires -- a module exposing
    #: `QuotaLedger(quotas, path)`. THE ONLY THING that differs between a real
    #: wiring and its fake.
    impl_module = "quota_ledger"

    def __init__(self) -> None:
        self.port: Any = None
        self._positive = oracle.PositiveAdapter()
        self._negative = oracle.NegativeAdapter()

    @property
    def _binding(self) -> Any:
        """The SAME binding module the shared oracle resolved.

        Read from the environment rather than declared on the class so the two
        cannot disagree: `oracle._snapshot` reaches the tree's internals through
        `oracle._binding`, and an adapter installing a before-state through a
        different module than the one that reads it back would compare a tree
        against itself in one place and against another tree in the next.
        """
        return importlib.import_module(os.environ.get("QUOTA_LEDGER_BINDING", "ports_binding"))

    # -- polarity -----------------------------------------------------------
    @staticmethod
    def _accepting(case: Any) -> bool:
        return "negative" not in set(case.labels)

    def _delegate(self, case: Any) -> Any:
        return self._positive if self._accepting(case) else self._negative

    def can_run(self, case: Any) -> Any:
        """Every skip rule, unchanged, from the shared oracle."""
        return self._delegate(case).can_run(case)

    # -- composition --------------------------------------------------------
    def _compose(self, quotas: dict[str, int], path: Path) -> Any:
        """Build the book over THIS adapter's implementation of the port.

        A binding that can select its composition point does so; one that cannot
        is a tree with a single wiring, and `impl_module` names the only one it
        has. Arm A is that case and it is the measured fact rather than a
        limitation of this harness: a flat module has no second implementation
        for a swap to swap.
        """
        return importlib.import_module(self.impl_module).QuotaLedger(dict(quotas), path)

    def _seed_journal(self, book: Any, root: Path, lines: list[str]) -> None:
        """Install the before-state's durable record.

        THROUGH THE PORT where there is one, and by writing the file where there
        is not. Writing the file is what every previous run did and it is
        correct only for a tree whose single wiring reads that file back: a fake
        journal ignores the path, so a before-state installed by writing a file
        arrives at the real wiring and vanishes at the fake one, and every case
        with a non-empty before-ledger would go red on unmutated code for a
        reason that has nothing to do with any mutant.
        """
        journal = getattr(book, "_journal", None)
        if journal is not None:
            for line in lines:
                journal.append(line)
            return
        (root / "ledger.txt").write_text(
            "".join(f"{line}\n" for line in lines), encoding="utf-8"
        )

    def _build(self, before: dict[str, Any], work_dir: Path | None) -> Any:
        root = Path(work_dir) if work_dir is not None else Path(".")
        root.mkdir(parents=True, exist_ok=True)
        book = self._compose(
            {tenant: oracle.QUOTA for tenant in oracle._tenants(before)}, root / "ledger.txt"
        )
        self._binding.install(
            book,
            committed=dict(before.get("committed", {})),
            closed=set(before.get("closed", ())),
            reservations=oracle._reservations(before),
            next_ordinal=oracle._next_ordinal(before),
        )
        self._seed_journal(
            book, root, [oracle._render_line(entry) for entry in before.get("ledger", ())]
        )
        return book

    # -- execution ----------------------------------------------------------
    def run(self, case: Any, work_dir: Path | None = None) -> Any:
        book = self._build(case.before, work_dir)
        params = dict(case.input.params)
        if self._accepting(case):
            for name, value in params.items():
                if oracle._is_unchecked(value):
                    raise AssertionError(f"unrecovered argument {name!r} for {case.name}")
            result = oracle._call(book, case.input.action, params)
            after = oracle._to_projection(oracle._snapshot(book, case.before, result), case)
            return oracle._Result(output=None, after=after, semantic_output={"unobservable": []})

        expected = case.output
        result = oracle._call(book, case.input.action, params)
        after = oracle._to_projection(oracle._snapshot(book, case.before, result), case)
        if result.status == "rejected":
            output = type(expected)(
                action=expected.action,
                params=dict(expected.params),
                reason=expected.reason,
                outcome_fields=tuple(expected.outcome_fields),
            )
        else:
            output = ("ACCEPTED", result.status, result.reservation_id)
        return oracle._Result(
            output=output,
            after=after,
            semantic_output={"unobservable": list(expected.outcome_fields)},
        )


class RealJournalAdapter(_JournalPortAdapter):
    """`LedgerJournal` = `journal_file.FileJournal`. A file on disk."""

    impl_module = "quota_ledger"


class FakeJournalAdapter(_JournalPortAdapter):
    """`LedgerJournal` = `journal_memory.InMemoryJournal`. The record in memory.

    Before `quota_ledger_fake.py` existed there was no composition point
    pointing at this adapter, so no case, no corpus and no suite ran a single
    line of it. That is `BA-B14` -- a fault in the treatment arm's in-memory
    adapter surviving five corpus instruments, the effect oracle and the
    hand-written suite -- and this class is the half of the swap that runs it.
    """

    impl_module = "quota_ledger_fake"


class ArmRealAdapter(_JournalPortAdapter):
    """Whatever composition point the ARM itself ships, on both arms.

    Arm A's `QuotaLedger` is a flat class over a file; arm B's is a factory
    returning `Ledger(quotas, FileJournal(path))`. Both answer to
    `QuotaLedger(quotas, path)`, which is the only thing this adapter needs and
    the only thing the feature ever specified.
    """

    impl_module = "quota_ledger"


class ArmBFakeAdapter(_JournalPortAdapter):
    """Arm B's `Journal` port, composed over arm B's own `InMemoryJournal`.

    There is no arm-A counterpart to this class and that absence is the
    measurement, not an omission: arm A declares no port, ships one
    implementation of nothing, and has no second wiring for a swap to reach.
    """

    impl_module = "arm_b_fake"
