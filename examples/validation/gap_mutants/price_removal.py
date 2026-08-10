#!/usr/bin/env python3
"""Price a removal from the KILL SET instead of from the detector list.

    python3 examples/validation/gap_mutants/price_removal.py price \\
        --before before.json --after after.json --head <sha>

    python3 examples/validation/gap_mutants/price_removal.py entail \\
        --before before.json --removal hardcoded-enumeration-literal

    python3 examples/validation/gap_mutants/price_removal.py audit

WHY THIS FILE EXISTS
====================

`RD-02` measured that **0 of 9** gap mutants over the sealed before-table could
have priced their removal, and named the reason: a gap mutant prices a removal
only if every detector that killed it is one the removal deletes. It then
shipped `removal_census.py discriminate`, which computes that condition up
front so an entailed `DIES` can be *reported* as entailed rather than published
as a measurement.

**The condition is computed over DETECTOR NAMES, and that makes it unsound in
the one direction it is used in.**

    surviving = [d for d in kills if d not in deleted_detectors]
    if surviving:  ->  "NON-DISCRIMINATING ... DIES after the cut was entailed"

Two things are wrong with reading a surviving detector *name* as a surviving
kill.

1. **`pytest-full` is the whole suite and no removal has ever deleted it.**
   Any fault it kills is classified `NON-DISCRIMINATING` before anything is
   run. Over the sealed table that is 5 of the 9 rows, and a sixth goes the
   same way through `instrument-registry`. The arithmetic, not the removals,
   is what produced the zero.

2. **A detector can survive by name and lose the kill.** A removal may delete
   the *node* inside a surviving suite, or leave the node id in place and
   replace its **body** with something weaker. `SM-03` did exactly the second:
   `test_the_named_instruments_are_all_enumerated` has the same file, the same
   function name and the same node id at `bf0fb29~1` and `bf0fb29`, and a
   different check inside it. Every survivorship test at detector granularity
   AND at node granularity says that detector outlived the cut. Both are right
   and neither is the question.

THE ASYMMETRY, WHICH IS THE WHOLE POINT
=======================================

Survivorship over a before-table is **sound towards `SURVIVES` and unsound
towards `DIES`**.

* If **no** killing (detector, node) survives the cut, every kill the fault had
  is gone. That is a proof, from the before-run alone, that the removal took
  the detection away. It is the direction that carries the **price**.
* If **some** killing (detector, node) survives the cut, nothing follows. The
  survivor may have been weakened. The honest verdict is `UNDECIDED`, and this
  file never emits `ENTAILED-DIES`.

**So a fault that cannot be re-run after a cut can still be evaluated after the
cut** -- because proving `SURVIVES` needs only the before-run and the diff, and
`SURVIVES` is the direction a price lives in. The re-runnability requirement in
`gap_mutants.toml` bought nothing on the priceable side, and cost the entire
class of faults whose surface dies with the mechanism.

BOUND ON `ENTAILED-SURVIVES`, stated rather than left to be found
-----------------------------------------------------------------

It proves the removal removed every kill the fault **had**. It cannot see a
kill the after tree **added** -- a removal that deletes a detector and ships a
stronger replacement reads `ENTAILED-SURVIVES` here and `DIES` on a real
after-run. So `ENTAILED-SURVIVES` is an upper bound on the price, and `price`
(which reads a measured after-table) is what settles it. Both are printed; the
instrument has no mode that emits only one.

WHAT IT IS NOT
==============

**Not a gate.** Nothing in this repository invokes it, no close path consults
it, and its exit code refuses nothing about the design. It exits 1 when a
declared removal names a mutant that is not in the before-table it was given,
because a price computed over a mutant that was never measured is the failure
this whole family keeps finding.

**Not a verdict about the removal.** `PRICED` means a fault the repository used
to catch is no longer caught. Whether that is an acceptable cost is a human's
call.

**Not a second implementation of `discriminate`.** `audit` imports the shipped
`removal_census.discriminating` and swaps DATA only, so what is compared
against measurement is the classifier that actually ships, not a re-typed copy
of it (`PA-04-DF-02`).
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
CENSUS = REPO_ROOT / "examples/validation/removal_census"
DEFAULT_MANIFEST = CENSUS / "removals.toml"

#: A verdict that decides nothing. Read as a survival, each of these is the
#: `FI-06` failure -- a green that nothing executed behind.
UNDECIDABLE = ("INERT", "CONTROL_RED", "NOT_RUN")

#: The three ways a kill can be lost. The third is the one no survivorship
#: test can see, and it is the one `SM-03` produced.
DETECTOR_REMOVED = "DETECTOR-REMOVED"
NODE_REMOVED = "NODE-REMOVED"
DETECTOR_WEAKENED = "DETECTOR-WEAKENED"

#: A kill with no node named -- a cli detector, or a suite that went red
#: without pytest printing a FAILED line.
RED_EXIT = "<red-exit>"

_PARAM = re.compile(r"\[[^\]]*\]$")


# --------------------------------------------------------------------------
# reading a gap-mutant artifact
# --------------------------------------------------------------------------


def kill_set(record: dict[str, Any]) -> tuple[set[tuple[str, str]], list[str]]:
    """Every (detector, node) that newly failed, and the cells that decide nothing.

    A `DIES` with no node named still counts as a kill -- it is a real red --
    but it is carried as `<red-exit>` so a reader can tell a named kill from an
    exit code. `INERT`, `CONTROL_RED` and `NOT_RUN` are neither kills nor
    survivals and are returned separately; a price computed over them would be
    a price computed over a column that did not run.
    """
    kills: set[tuple[str, str]] = set()
    undecided: list[str] = []
    for detector_id, cell in (record.get("detectors") or {}).items():
        verdict = cell.get("verdict")
        if verdict in UNDECIDABLE:
            undecided.append(detector_id)
            continue
        if verdict != "DIES":
            continue
        nodes = cell.get("new_failing_nodes") or []
        if nodes:
            kills.update((detector_id, node) for node in nodes)
        else:
            kills.add((detector_id, RED_EXIT))
    return kills, sorted(undecided)


# --------------------------------------------------------------------------
# does a killing node still exist?
# --------------------------------------------------------------------------


def _show(ref: str, path: str) -> str | None:
    done = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    return done.stdout if done.returncode == 0 else None


def node_present(ref: str, node: str) -> bool:
    """Is this pytest node id still in the tree at `ref`?

    Deliberately shallow: the file must exist and the last `::` component's
    function name must still be defined in it. It answers "was this node
    deleted", which is all survivorship is entitled to ask. **It says nothing
    about whether the node still asserts what it asserted** -- that is
    `DETECTOR-WEAKENED`, and the only thing that sees it is running the fault.
    """
    if node == RED_EXIT:
        return True
    path, _, rest = node.partition("::")
    blob = _show(ref, path)
    if blob is None:
        return False
    if not rest:
        return True
    name = _PARAM.sub("", rest.split("::")[-1])
    return f"def {name}(" in blob


# --------------------------------------------------------------------------
# the measured price: before-table against after-table
# --------------------------------------------------------------------------


def price(
    before: dict[str, Any],
    after: dict[str, Any],
    mutant_id: str,
    head: str | None,
    deleted_detectors: list[str],
) -> dict[str, Any]:
    """The price of a removal for one fault, read from both measured tables."""
    b_record = before["per_mutant"].get(mutant_id)
    a_record = after["per_mutant"].get(mutant_id)
    if b_record is None or a_record is None:
        missing = "before" if b_record is None else "after"
        return {"mutant": mutant_id, "verdict": "NOT-IN-TABLE", "why": f"absent from the {missing} table"}

    b_kills, b_undecided = kill_set(b_record)
    a_kills, a_undecided = kill_set(a_record)

    row: dict[str, Any] = {
        "mutant": mutant_id,
        "kills_before": sorted(f"{d}::{n}" for d, n in b_kills),
        "kills_after": sorted(f"{d}::{n}" for d, n in a_kills),
        "undecidable_columns_before": b_undecided,
        "undecidable_columns_after": a_undecided,
    }

    if not b_kills:
        row["verdict"] = "NO-KILL-TO-LOSE"
        row["why"] = "nothing caught it before the cut, so the cut cannot have taken a kill away"
        return row

    lost = sorted(b_kills - a_kills)
    row["lost_kills"] = [
        {
            "detector": detector,
            "node": node,
            "reason": _loss_reason(detector, node, head, deleted_detectors, a_record),
        }
        for detector, node in lost
    ]

    if a_kills:
        row["verdict"] = "FREE"
        row["why"] = "something still catches it after the cut; the detection was redundant"
        return row

    row["verdict"] = "PRICED"
    row["why"] = "every kill it had is gone; the removal took the detection away"
    return row


def _loss_reason(
    detector: str,
    node: str,
    head: str | None,
    deleted_detectors: list[str],
    a_record: dict[str, Any],
) -> str:
    cell = (a_record.get("detectors") or {}).get(detector)
    if detector in deleted_detectors or (cell or {}).get("verdict") == "REMOVED" or cell is None:
        return DETECTOR_REMOVED
    if head and not node_present(head, node):
        return NODE_REMOVED
    return DETECTOR_WEAKENED


# --------------------------------------------------------------------------
# the before-only reading, and the direction it is sound in
# --------------------------------------------------------------------------


def entail(
    before: dict[str, Any],
    mutant_id: str,
    deleted_detectors: list[str],
    head: str | None,
) -> dict[str, Any]:
    """What survivorship over the before-table alone is entitled to conclude.

    THREE VERDICTS, AND ONLY ONE OF THEM IS A CONCLUSION:

      NO-KILL-TO-LOSE     nothing caught it before; the cut cannot cost anything
      ENTAILED-SURVIVES   no killing (detector, node) survives the cut. The
                          removal took every kill this fault had. SOUND -- and
                          bounded: it cannot see a kill the after tree ADDED.
      UNDECIDED           some killing (detector, node) survives by name. That
                          is NOT `entailed DIES`: the survivor may have been
                          weakened, and only running the fault can tell.

    The shipped `removal_census.discriminating` returns `NON-DISCRIMINATING`
    for the third case with the reason *"DIES after the cut was entailed before
    the cut was made"*. That is the unsound step this function refuses to take.
    """
    record = before["per_mutant"].get(mutant_id)
    if record is None:
        return {"mutant": mutant_id, "verdict": "NOT-IN-TABLE"}

    kills, undecided = kill_set(record)
    row: dict[str, Any] = {
        "mutant": mutant_id,
        "kills_before": sorted(f"{d}::{n}" for d, n in kills),
        "undecidable_columns_before": undecided,
    }
    if not kills:
        row["verdict"] = "NO-KILL-TO-LOSE"
        return row

    survivors = []
    for detector, node in sorted(kills):
        if detector in deleted_detectors:
            continue
        if head and not node_present(head, node):
            continue
        survivors.append(f"{detector}::{node}")
    row["kills_that_survive_by_name"] = survivors
    if survivors:
        row["verdict"] = "UNDECIDED"
        row["why"] = (
            "a killing node still exists at the head of the removal. It may or may not "
            "still catch this fault -- a node can keep its id and lose its body. Running "
            "the fault is the only thing that decides it."
        )
    else:
        row["verdict"] = "ENTAILED-SURVIVES"
        row["why"] = (
            "every killing node the fault had is deleted by this removal, so the removal "
            "took the detection away. Bound: this cannot see a kill the after tree ADDED."
        )
    return row


# --------------------------------------------------------------------------
# audit -- the shipped classifier against the measured record
# --------------------------------------------------------------------------


def _shipped_discriminating():
    """The classifier that actually ships. Imported, never re-typed."""
    sys.path.insert(0, str(CENSUS))
    import removal_census  # noqa: E402  (path must be set first)

    return removal_census.discriminating


#: The sealed record: one before-table, and the after-tables published against
#: it. Each pair names the removal whose `deletes_detectors` applies.
RECORD = [
    {
        "removal": "ports-binding-machinery",
        "head": "0342a3a",
        "before": "specs/results/scorecards/subtract-to-measure/before-state/gap-mutants-before.json",
        "after": "specs/results/scorecards/subtract-to-measure/after-state-SM-02/gap-mutants-after-SM-02.json",
    },
    {
        "removal": "hardcoded-enumeration-literal",
        "head": "bf0fb29",
        "before": "specs/results/scorecards/subtract-to-measure/before-state/gap-mutants-before.json",
        "after": "specs/results/scorecards/subtract-to-measure/after-state/gap-mutants-after.json",
    },
    {
        "removal": "dead-port-binding-report-detector",
        "head": "HEAD",
        "before": "specs/results/scorecards/reading-discipline/GOAL-apparatus-priced/rd02-gap-mutant-before.json",
        "after": "specs/results/scorecards/reading-discipline/GOAL-apparatus-priced/rd02-gap-mutant-after.json",
    },
]


def audit(manifest: dict[str, Any]) -> dict[str, Any]:
    """Every published before/after pair, classifier prediction against measurement."""
    discriminating = _shipped_discriminating()
    removals = {row["id"]: row for row in manifest.get("removal", [])}
    rows: list[dict[str, Any]] = []
    for pair in RECORD:
        removal = removals.get(pair["removal"])
        if removal is None:
            continue
        before = json.loads((REPO_ROOT / pair["before"]).read_text(encoding="utf-8"))
        after = json.loads((REPO_ROOT / pair["after"]).read_text(encoding="utf-8"))
        deleted = removal.get("deletes_detectors", [])
        for mutant_id in removal.get("gap_mutants", []):
            shipped = discriminating(before, mutant_id, deleted)
            measured = price(before, after, mutant_id, pair["head"], deleted)
            rows.append({
                "removal": pair["removal"],
                "mutant": mutant_id,
                "shipped_classifier": shipped["verdict"],
                "this_instrument": entail(before, mutant_id, deleted, pair["head"])["verdict"],
                "measured": measured["verdict"],
                "lost_kills": measured.get("lost_kills", []),
                "agrees": _agrees(shipped["verdict"], measured["verdict"]),
            })
    return {"rows": rows, "record": RECORD}


def _agrees(shipped: str, measured: str) -> bool:
    """Did the shipped classifier's prediction match what the re-run measured?"""
    if shipped == "NO-KILL-TO-LOSE":
        return measured == "NO-KILL-TO-LOSE"
    if shipped == "NON-DISCRIMINATING":  # it predicts DIES after the cut
        return measured == "FREE"
    if shipped == "DISCRIMINATING":      # it predicts the re-run could say something
        return measured in ("PRICED", "FREE")
    return measured == "NOT-IN-TABLE"


# --------------------------------------------------------------------------
# rendering and main
# --------------------------------------------------------------------------


def render_price(rows: list[dict[str, Any]]) -> str:
    out = ["THE PRICE, READ FROM THE KILL SET", ""]
    for row in rows:
        out.append(f"{row['verdict']:<16} {row['mutant']}")
        if row.get("why"):
            out.append(f"                 {row['why']}")
        for lost in row.get("lost_kills", []):
            out.append(f"    lost kill   [{lost['reason']}] {lost['detector']} :: {lost['node']}")
        for column in row.get("undecidable_columns_after", []):
            out.append(f"    UNDECIDABLE column after the cut, read as neither: {column}")
    priced = [r for r in rows if r["verdict"] == "PRICED"]
    out += ["", f"{len(priced)} of {len(rows)} fault(s) PRICED -- a fault the repository "
                f"used to catch and no longer catches."]
    return "\n".join(out)


def render_audit(report: dict[str, Any]) -> str:
    out = [
        "THE SHIPPED CLASSIFIER AGAINST THE MEASURED RECORD",
        "",
        "| removal | mutant | discriminate | price_removal | measured | agrees |",
        "|---|---|---|---|---|---|",
    ]
    for row in report["rows"]:
        out.append(
            f"| {row['removal']} | {row['mutant'][:34]} | {row['shipped_classifier']} "
            f"| {row['this_instrument']} | {row['measured']} | "
            f"{'yes' if row['agrees'] else '**NO**'} |"
        )
    bad = [r for r in report["rows"] if not r["agrees"]]
    out += ["", f"{len(bad)} of {len(report['rows'])} disagree with the measurement."]
    weakened = [
        lost for row in report["rows"] for lost in row["lost_kills"]
        if lost["reason"] == DETECTOR_WEAKENED
    ]
    out.append(
        f"{len(weakened)} lost kill(s) in the sealed record are DETECTOR-WEAKENED -- "
        "the class no survivorship test can see."
    )
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("price", help="measured price from a before-table and an after-table")
    p.add_argument("--before", type=Path, required=True)
    p.add_argument("--after", type=Path, required=True)
    p.add_argument("--head", default=None, help="the removal's head sha, for node survivorship")
    p.add_argument("--removal", default=None, help="a removal id in the manifest")
    p.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    p.add_argument("--fault", action="append", default=[],
                   help="fault id to price; repeatable. Defaults to the removal's declared list.")
    p.add_argument("--out", type=Path, default=None)

    e = sub.add_parser("entail", help="what the before-table alone entails, and in which direction")
    e.add_argument("--before", type=Path, required=True)
    e.add_argument("--removal", default=None)
    e.add_argument("--head", default=None)
    e.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    e.add_argument("--fault", action="append", default=[],
                   help="fault id to read; repeatable. Defaults to the removal's declared list.")
    e.add_argument("--out", type=Path, default=None)

    a = sub.add_parser("audit", help="the shipped classifier against every published re-run")
    a.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    a.add_argument("--out", type=Path, default=None)

    args = parser.parse_args(argv)
    manifest = tomllib.loads(args.manifest.read_text(encoding="utf-8"))
    removals = {row["id"]: row for row in manifest.get("removal", [])}

    if args.command == "audit":
        report = audit(manifest)
        print(render_audit(report))
        _write(args.out, report)
        return 0

    before = json.loads(args.before.read_text(encoding="utf-8"))
    removal = removals.get(args.removal) if args.removal else None
    deleted = list(removal.get("deletes_detectors", [])) if removal else []
    # `--removal` supplies the removal's DETECTOR LIST. It does not have to
    # supply the faults: a fault seeded after the removal landed is priced
    # against the same cut and is not in that removal's `gap_mutants`. `--fault`
    # names the subjects; without it they default to the manifest's list, and
    # without that to every fault in the before-table.
    declared = list(args.fault) or list(removal.get("gap_mutants", [])) if removal else list(args.fault)
    subjects = declared or sorted(before["per_mutant"])

    missing = [m for m in declared if m not in before["per_mutant"]]

    if args.command == "entail":
        rows = [entail(before, m, deleted, args.head) for m in subjects]
        for row in rows:
            print(f"{row['verdict']:<19} {row['mutant']}")
            if row.get("why"):
                print(f"                    {row['why']}")
        _write(args.out, {"removal": args.removal, "head": args.head, "rows": rows})
        return 1 if missing else 0

    after = json.loads(args.after.read_text(encoding="utf-8"))
    rows = [price(before, after, m, args.head, deleted) for m in subjects]
    print(render_price(rows))
    _write(args.out, {"removal": args.removal, "head": args.head,
                      "before": str(args.before), "after": str(args.after), "rows": rows})
    return 1 if missing else 0


def _write(out: Path | None, payload: dict[str, Any]) -> None:
    if out is None:
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    raise SystemExit(main())
