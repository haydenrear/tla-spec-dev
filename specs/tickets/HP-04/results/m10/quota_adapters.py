"""HP-04: spec-unit adapters over HP-01's A/B reference, for the M10 run.

WHAT THIS IS FOR, stated first so it cannot be mistaken for an arm. HP-01's
catalogue seeds **M10 (release credits back double)** into HP-04's declared blind
spot: the effect oracle "never consults `can_run` and aborts the whole run on the
first `apply()`-only adapter", so an action whose adapter is `apply()`-only is
invisible to it. Measuring that needed a corpus of `examples/validation/ab/model`
executing against `examples/validation/ab/reference` -- and the A/B fixture ships
no adapters, because building them is HP-06's job when it runs the experiment.

So this file exists to RUN THE INSTRUMENT, not to be judged as an arm:

* it lives under `specs/tickets/HP-04/results/`, not under
  `examples/validation/ab/`, so nothing HP-06 scores is touched;
* the reference tree is read and never written (the mutants are applied and
  reverted by `run_m10.py` using HP-01's own catalogue and byte-identical
  revert);
* **`Release` is deliberately `apply()`-only.** That is not laziness, it is the
  seeded condition. M10's catalogue entry says so in as many words: "`Release`
  is the action here most likely to get an `apply()`-only adapter: it has no
  durable effect and no interesting output, so there is nothing obvious for a
  provider to assert."

Every other action gets a `run(case, work_dir)`, so the corpus reaches them.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[4]
REFERENCE = REPO_ROOT / "examples" / "validation" / "ab" / "reference" / "quota_ledger.py"

_spec = importlib.util.spec_from_file_location("hp04_quota_ledger_reference", REFERENCE)
assert _spec is not None and _spec.loader is not None
reference = importlib.util.module_from_spec(_spec)
sys.modules["hp04_quota_ledger_reference"] = reference
_spec.loader.exec_module(reference)

NO_TENANT = "none"


def _materialize(case, work_dir: Path):
    """Build a reference QuotaLedger standing in the case's BEFORE state.

    The model's `available` already holds the post-hold figure, so the ledger is
    constructed at quota and then written into directly. Poking the private
    fields is the same move `specs/*/adapter_case_runtime.py` makes with CLI
    replay: a spec-unit adapter's job is to put the program in the modeled state,
    by whatever route the program allows.
    """
    before = case.before
    work_dir = Path(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = work_dir / "ledger.txt"
    quotas = {tenant: 2 for tenant in before["available"]}
    program = reference.QuotaLedger(quotas, ledger_path)
    program._available = dict(before["available"])
    program._committed = dict(before["committed"])
    program._closed = set(before["closed"])
    program._outstanding = {
        res: reference.Reservation(res, tenant, before["amt"][res])
        for res, tenant in before["holder"].items()
        if tenant != NO_TENANT
    }
    if before["ledger"]:
        # The model's ledger entries are 3-tuples; the reference's COMMIT line
        # additionally carries the running total, which is reconstructed from
        # `committed` so the before-state file is what the program would have
        # written on the way here.
        lines = []
        running = {tenant: 0 for tenant in before["available"]}
        for entry in before["ledger"]:
            kind, tenant, amount = entry[0], entry[1], int(entry[2])
            if kind == "COMMIT":
                running[tenant] += amount
                lines.append(f"COMMIT {tenant} {amount} {running[tenant]}")
            else:
                lines.append(f"CLOSE {tenant} {amount}")
        ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return program, ledger_path


def _parse_ledger(lines: list[str]) -> tuple:
    """The durable lines, in the MODEL's vocabulary.

    The model appends `<<"COMMIT", holder[r], amt[r]>>` and
    `<<"CLOSE", t, committed[t]>>`; the reference additionally writes a running
    total on the COMMIT line, which the model does not carry. That extra field
    is DROPPED here, and dropping it is faithful rather than convenient: a
    projection cannot assert a value the model does not have. It is also
    exactly why M04 (`durable running total stale`) is seeded as
    `durable_content` against HP-05's content-asserting provider and not
    against the corpus -- the corpus structurally cannot see it, and this
    adapter's survival on M04 is that limit showing up as a measurement.
    """
    parsed = []
    for line in lines:
        parts = line.split()
        if parts and parts[0] == "COMMIT" and len(parts) >= 3:
            parsed.append(("COMMIT", parts[1], int(parts[2])))
        elif parts and parts[0] == "CLOSE" and len(parts) >= 3:
            parsed.append(("CLOSE", parts[1], int(parts[2])))
        else:  # a shape the model has no term for; kept verbatim so it cannot
            parsed.append(tuple(parts))  # be mistaken for a matching line
    return tuple(parsed)


def _project(case, program, ledger_path: Path, result) -> dict:
    """Read the reference back out in the model's own vocabulary.

    `holder` and `amt` start from the BEFORE state because the model never
    clears them -- "ids are never reused" (QuotaLedger.tla, Reserve) -- while
    the reference drops the reservation from `_outstanding` on commit and
    release. `live` is the set that actually moves.
    """
    holder = dict(case.before["holder"])
    amt = dict(case.before["amt"])
    for res, reservation in program._outstanding.items():
        holder[res] = reservation.tenant
        amt[res] = reservation.amount
    return {
        "amt": amt,
        "available": dict(program._available),
        "closed": frozenset(program._closed),
        "committed": dict(program._committed),
        "holder": holder,
        "ledger": _parse_ledger(program.ledger_lines()),
        "live": frozenset(program._outstanding),
        "reason": NO_TENANT if result is None or result.reason is None else result.reason,
        "status": "init" if result is None else result.status,
    }


class _Base:
    """Materialize, drive, project. `can_run` guards what the case must carry."""

    required_params: tuple[str, ...] = ()

    def can_run(self, case) -> tuple[bool, str | None]:
        params = getattr(case.input, "params", {}) or {}
        for name in self.required_params:
            if name not in params:
                return False, f"case does not carry the {name!r} argument"
        return True, None

    def _amount(self, case, params) -> int:
        """The reserve amount, recovered from the modeled outcome when UNCHECKED.

        The generated corpus reports `a` as UNCHECKED for `Reserve` -- the
        parameter-recovery limit RC-02 measured -- so the amount comes from the
        transition the model already describes rather than from a guess.
        """
        reservation = params.get("r")
        after_amt = case.after.get("amt", {})
        before_amt = case.before.get("amt", {})
        if reservation in after_amt:
            return int(after_amt[reservation]) - int(before_amt.get(reservation, 0))
        return 0

    def _drive(self, case, program, params):  # pragma: no cover - overridden
        raise NotImplementedError

    def run(self, case, work_dir: Path | None = None):
        program, ledger_path = _materialize(case, Path(work_dir or HERE / "_work"))
        params = getattr(case.input, "params", {}) or {}
        result = self._drive(case, program, params)
        return {"after": _project(case, program, ledger_path, result)}


class ReserveAdapter(_Base):
    required_params = ("t", "r")

    def _drive(self, case, program, params):
        # The model names the reservation id the transition allocates; the
        # reference allocates from its own counter. Aligning the counter is
        # materialization, not a fix to the program: the case says WHICH id this
        # transition produces, and an adapter that ignored it would report a
        # mismatch on every Reserve and drown every real one.
        program._next_id = int(str(params["r"]).lstrip("r"))
        return program.reserve(params["t"], self._amount(case, params))


class RefuseReserveClosedAdapter(ReserveAdapter):
    pass


class RefuseReserveNotPositiveAdapter(ReserveAdapter):
    def _drive(self, case, program, params):
        return program.reserve(params["t"], 0)


class RefuseReserveOverQuotaAdapter(ReserveAdapter):
    def _drive(self, case, program, params):
        return program.reserve(params["t"], program.available(params["t"]) + 1)


class CommitAdapter(_Base):
    required_params = ("r",)

    def _drive(self, case, program, params):
        return program.commit(params["r"])


class RefuseCommitUnknownAdapter(CommitAdapter):
    pass


class CloseTenantAdapter(_Base):
    required_params = ("t",)

    def _drive(self, case, program, params):
        return program.close_tenant(params["t"])


class RefuseCloseAlreadyClosedAdapter(CloseTenantAdapter):
    pass


class RefuseCloseOutstandingAdapter(CloseTenantAdapter):
    pass


class RefuseReleaseUnknownAdapter(_Base):
    required_params = ("r",)

    def _drive(self, case, program, params):
        return program.release(params["r"])


class ReleaseAdapter:
    """THE SEEDED BLIND SPOT. `apply()` and no `run(case, work_dir)`.

    Nine of seventeen adapters in this repository's own model are exactly this
    shape, which is why the effect oracle could see at most 8 of 18 modeled
    actions. Before HP-04 meeting one of these aborted the entire run with
    ``TypeError: adapter ... does not define run(case, ...)`` and no report was
    written at all. After HP-04 the case is SKIPPED and named -- which makes the
    action visible in the report and, exactly as prediction N05 says, does NOT
    make M10 killable, because a skipped case executes nothing.
    """

    def apply(self) -> dict[str, object]:
        program = reference.QuotaLedger({"t1": 2}, HERE / "_apply" / "ledger.txt")
        return {"available": program.available("t1")}


class ReleaseRunnableAdapter(_Base):
    """THE COUNTERFACTUAL. The same action with a `run(case, work_dir)`.

    Prediction N05 says HP-04 makes the apply()-only action VISIBLE without
    making it KILLABLE. `ReleaseAdapter` above settles the first half. This one
    settles the second: bound in `case_adapters_release_runnable.toml` and run
    over the same corpus and the same catalogue, it is the smallest change that
    could make M10 die -- and if M10 dies here, the remaining work is nine
    `run()` implementations in `production_adapters.py`, not anything in the
    oracle. That is a much more useful thing to know than a survivor.
    """

    required_params = ("r",)

    def _drive(self, case, program, params):
        return program.release(params["r"])
