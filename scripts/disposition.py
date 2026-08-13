#!/usr/bin/env python3
"""Refuse an epic close-out while any finding it filed is undisposed.

THIS IS NOT A GATE ON ANYONE'S CODE. Seven epics of static checking caught zero
bugs and this epic adds no gate. It is a close-out requirement on THIS project's
own epics, run by hand at epic close and by `CA-08`. It reads one file --
`specs/desired_program_model/deferred_findings.yaml` -- and reports whether the
findings an epic filed were routed anywhere.

The rule, three clauses, in `references/consumption.md`:

  D1  every finding filed by the epic carries a `disposition` that is not `open`
  D2  a TERMINAL disposition carries a `disposition_note` -- what was done
  D3  a DEFERRAL (`carried`) names a successor in `disposition_ticket`

Exit 0 = disposed, 1 = REFUSED, 2 = usage/parse error.

    python3 scripts/disposition.py --epic cut-the-apparatus     # refuses
    python3 scripts/disposition.py --ticket CA-05               # accepts
    python3 scripts/disposition.py --all                        # every epic
"""
from __future__ import annotations

import argparse
import pathlib
import sys

LEDGER = "specs/desired_program_model/deferred_findings.yaml"

# Ticket-id prefix -> epic, a fact of the record rather than a configuration.
EPICS = {
    "PA": "ports-as-adapters",
    "FI": "falsifiable-instruments",
    "SM": "subtract-to-measure",
    "RD": "reading-discipline",
    "RM": "portable-substrate",
    "CL": "close-the-loop",
    "SV": "score-drives-validation",
    "CA": "cut-the-apparatus",
}

TERMINAL = {"repaired", "settled", "refuted", "consumed", "wontfix"}
DEFERRAL = {"carried"}


def load(path: pathlib.Path) -> list[dict]:
    import yaml  # deferred: the ledger is the only reason this script needs it

    doc = yaml.safe_load(path.read_text()) or {}
    rows = doc.get("findings") or []
    if not rows:
        raise SystemExit(f"{path}: no `findings` -- refusing to report 0 of 0")
    return rows


def epic_of(row: dict) -> str:
    prefix = str(row.get("id", "")).split("-")[0]
    return EPICS.get(prefix, prefix or "?")


def violations(row: dict) -> list[str]:
    """Every clause this row fails, named. A row can fail more than one."""
    out: list[str] = []
    d = row.get("disposition")
    if d is None:
        out.append("D1 no `disposition` field at all")
    elif d == "open":
        out.append("D1 `disposition: open` -- filed and routed nowhere")
    elif d in TERMINAL:
        if not str(row.get("disposition_note") or "").strip():
            out.append(f"D2 `{d}` with no `disposition_note` -- no record of what was done")
    elif d in DEFERRAL:
        if not str(row.get("disposition_ticket") or "").strip():
            out.append(f"D3 `{d}` with no `disposition_ticket` -- deferred to nobody")
    else:
        out.append(f"D1 `disposition: {d}` is outside the vocabulary")
    return out


def report(rows: list[dict], label: str, verbose: bool) -> int:
    bad = [(r, v) for r in rows if (v := violations(r))]
    n, b = len(rows), len(bad)
    if not rows:
        print(f"REFUSED  {label}: no findings match -- an epic that filed nothing "
              f"has not been shown to be clean, only unexamined")
        return 1
    if not bad:
        print(f"DISPOSED {label}: {n} findings, all three clauses hold")
        return 0
    print(f"REFUSED  {label}: {b} of {n} findings undisposed")
    clauses: dict[str, int] = {}
    for _, vs in bad:
        for v in vs:
            clauses[v.split(" ", 1)[0]] = clauses.get(v.split(" ", 1)[0], 0) + 1
    for c in sorted(clauses):
        print(f"           {c}: {clauses[c]}")
    shown = bad if verbose else bad[:5]
    for r, vs in shown:
        for v in vs:
            print(f"           {r.get('id', '?')}: {v}")
    if len(shown) < b:
        print(f"           ... and {b - len(shown)} more (use -v)")
    return 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ledger", default=LEDGER, type=pathlib.Path)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--epic", help="epic name or ticket-id prefix, e.g. cut-the-apparatus or CA")
    g.add_argument("--ticket", help="one ticket id, e.g. CA-05")
    g.add_argument("--all", action="store_true", help="every epic in the ledger, oldest id first")
    p.add_argument("-v", "--verbose", action="store_true")
    a = p.parse_args(argv)

    rows = load(a.ledger)
    if a.all:
        worst = 0
        for e in sorted({epic_of(r) for r in rows}):
            worst |= report([r for r in rows if epic_of(r) == e], e, a.verbose)
        print(f"\n{sum(1 for r in rows if violations(r))} of {len(rows)} findings "
              f"in {a.ledger} are undisposed")
        return worst
    if a.ticket:
        sel = [r for r in rows if str(r.get("found_by") or r.get("id", "")).startswith(a.ticket)
               and str(r.get("id", "")).startswith(a.ticket + "-")]
        return report(sel, f"ticket {a.ticket}", a.verbose)
    want = EPICS.get(a.epic.upper(), a.epic)
    return report([r for r in rows if epic_of(r) == want], f"epic {want}", a.verbose)


if __name__ == "__main__":
    sys.exit(main())
