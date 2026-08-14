#!/usr/bin/env python3
"""Refuse an epic close-out while any finding it filed is undisposed.

THIS IS NOT A GATE ON ANYONE'S CODE. It is a close-out requirement on THIS
project's own epics, run by hand at epic close and by `CA-08`. It reads one file
-- `specs/desired_program_model/deferred_findings.yaml` -- and reports whether
the findings an epic filed were routed anywhere. Once a workflow close has
removed `desired_program_model/`, it reads the copy that close archived under
`specs/.history/` instead, and says on stderr which one (`resolve_ledger`).

The slogan this file used to carry unqualified, now qualified because it was
FALSE in this ticket's own PR: seven epics of static checking caught zero bugs
IN A SUBJECT PROGRAM. That measured claim stands. It is NOT the claim that no
check ever catches anything -- `registry-enumeration-coverage` caught this very
ticket shipping an unregistered instrument, and a set-completeness check over
machine-derived metadata is a different class from a static gate on content.

The rule, three clauses, in `references/consumption.md`:

  D1  every finding filed by the epic carries a `disposition` that is not `open`
  D2  a TERMINAL disposition carries a `disposition_note` -- what was done
  D3  a DEFERRAL (`carried`) names a successor in `disposition_ticket`

WHAT D3 DOES NOT ASK, and it is a wide hole -- `CA-05-DF-03`. It does not ask
that the successor be outside the filing epic (SELF-ROUTING PASSES, and all
three of this ticket's own deferrals do it), nor that it resolve to anything
(a bare ticket id passes, as does any non-empty string), nor that a deferral
carry a note. Two field rewrites turn the whole backlog green. It measures
ROUTING, never CONSUMPTION.

Exit 0 = disposed, 1 = REFUSED, 2 = usage/parse error. A STRUCTURAL fault
(duplicate keys) refuses before any clause is evaluated.

    python3 scripts/disposition.py --epic cut-the-apparatus     # refuses
    python3 scripts/disposition.py --ticket CA-05               # accepts
    python3 scripts/disposition.py --all                        # every epic
"""
from __future__ import annotations

import argparse
import re
import pathlib
import sys

LEDGER = "specs/desired_program_model/deferred_findings.yaml"

# WHERE THE LEDGER GOES WHEN THE WORKFLOW CLOSES. `LEDGER` is a path inside
# `desired_program_model/`, and `scripts/close_tickets.py` REMOVES that directory
# at workflow close -- by design; the close is supposed to take the workflow
# directories with it. So the live path is not a stable address: it exists
# during an epic and is gone the moment the epic is closed, which is exactly
# when someone wants to read what the epic filed. Before CA-09 this script
# answered that with a bare `FileNotFoundError` traceback.
#
# The close archives the ledger into the history entry (`spec_evolution.
# snapshot_findings_ledger`, recorded in the entry manifest as
# `findings_ledger`). These globs find those archives, newest first. The first
# form is the named artifact the close writes; the second is the same file
# carried along inside the desired-model snapshot, which is where closes BEFORE
# CA-09 left it and the only copy those entries have.
ARCHIVE_GLOBS = (
    "specs/.history/*/*/deferred_findings.yaml",
    "specs/.history/*/*/snapshots/desired_program_model/deferred_findings.yaml",
)

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

# `channel` is ADVISORY here and is NOT one of the three clauses. Reported so the
# vocabulary is not merely "described as closed" -- the asymmetry the PR #265
# reviewer named, where `disposition`'s vocabulary was enforced and `channel`'s
# was documented and enforced by nothing at all (harvest class `C2`).
CHANNELS = {
    "blind-judges", "census", "operator-doing-the-work",
    "operator-running-a-shipped-instrument", "operator-running-own-instrument",
    "the-suite", "independent-review",
}


def off_vocabulary_channels(rows: list[dict]) -> list[tuple[str, str]]:
    """Rows whose `channel` is set but outside `CHANNELS`. Advisory, never a clause."""
    return [(str(r.get("id", "?")), str(r["channel"])) for r in rows
            if r.get("channel") and r["channel"] not in CHANNELS]


def duplicate_keys(text: str) -> list[tuple[str, str, list[int]]]:
    """Rows carrying the same key twice, which YAML resolves SILENTLY to the last.

    `CA-05-DF-06`. Seven rows (`SM-05-DF-01`..`DF-07`) carried two
    `disposition_ticket` keys: `#188` above the note and `#169` below it. Every
    parser kept `#169`, so this checker read a value the author never intended,
    disagreed with the `disposition_note` on the same row and with the close-out
    commit message, and printed `DISPOSED subtract-to-measure`. **A false PASS on
    real data, and one of the two acceptances the discrimination argument rested
    on.** Found by an independent reviewer of PR #265, not by this instrument.

    A structural fault is reported SEPARATELY from a clause violation and always
    refuses: a clause verdict computed over silently-discarded input is not a
    verdict at all.
    """
    out: list[tuple[str, str, list[int]]] = []
    rid = "?"
    seen: dict[str, list[int]] = {}

    def flush() -> None:
        for k, ns in seen.items():
            if len(ns) > 1:
                out.append((rid, k, ns))

    for n, line in enumerate(text.split("\n"), 1):
        if re.match(r"^  - id: ", line):
            flush()
            rid, seen = line.split("id: ", 1)[1].strip(), {}
        elif m := re.match(r"^    ([A-Za-z_][A-Za-z0-9_]*):", line):
            seen.setdefault(m.group(1), []).append(n)
    flush()
    return out


def archived_ledgers(root: pathlib.Path = pathlib.Path(".")) -> list[pathlib.Path]:
    """Every archived copy of the ledger under `specs/.history`, best last.

    Ordered by (mtime, size). Size breaks mtime ties -- and it is not arbitrary:
    the ledger is APPEND-ONLY by rule, so of two copies the larger one carries
    the later state. A `git checkout` flattens mtimes, which is exactly when the
    tie-break is needed.
    """
    seen: dict[pathlib.Path, None] = {}
    for pattern in ARCHIVE_GLOBS:
        for path in root.glob(pattern):
            seen.setdefault(path.resolve(), None)
    return sorted(seen, key=lambda p: (p.stat().st_mtime, p.stat().st_size, str(p)))


def resolve_ledger(path: pathlib.Path, *, explicit: bool) -> pathlib.Path:
    """The live ledger if it is there; otherwise the newest archived copy.

    THIS IS A READ FALLBACK, NOT AN EXEMPTION. The close still removes
    `desired_program_model/` and the live ledger with it. What changed is that
    this script can still answer afterwards, and says out loud which copy it
    read -- an archived ledger is frozen at the close, so a verdict from one is
    a verdict about a closed epic, never about work done since.
    """
    if path.exists():
        return path
    if explicit:
        raise SystemExit(f"{path}: no such ledger (--ledger was given explicitly, so no archive is searched)")
    archives = archived_ledgers()
    if not archives:
        raise SystemExit(
            f"{path}: no ledger there and no archived copy under specs/.history. "
            f"If a workflow close removed it, the archive is "
            f"specs/.history/<workflow>/closed-snapshot/deferred_findings.yaml "
            f"(entry manifest key `findings_ledger`)."
        )
    newest = archives[-1]
    print(
        f"NOTE: {path} is absent -- a workflow close removes desired_program_model/. "
        f"Reading the archived ledger {newest}, which is FROZEN at that close.",
        file=sys.stderr,
    )
    return newest


def load(path: pathlib.Path) -> list[dict]:
    import yaml  # deferred: the ledger is the only reason this script needs it

    text = path.read_text()
    if dups := duplicate_keys(text):
        for rid, key, ns in dups:
            print(f"STRUCTURAL {rid}: `{key}` appears {len(ns)}x at lines "
                  f"{', '.join(map(str, ns))} -- YAML keeps the LAST and discards "
                  f"the rest without a word", file=sys.stderr)
        raise SystemExit(
            f"{path}: {len(dups)} duplicate key(s) -- REFUSING to report a clause "
            f"verdict over input a parser has silently discarded (CA-05-DF-06)"
        )
    doc = yaml.safe_load(text) or {}
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
    p.add_argument(
        "--ledger",
        default=None,
        type=pathlib.Path,
        help=f"ledger to read (default {LEDGER}, falling back to the newest archived copy "
             f"under specs/.history once a workflow close has removed the live one)",
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--epic", help="epic name or ticket-id prefix, e.g. cut-the-apparatus or CA")
    g.add_argument("--ticket", help="one ticket id, e.g. CA-05")
    g.add_argument("--all", action="store_true", help="every epic in the ledger, oldest id first")
    p.add_argument("-v", "--verbose", action="store_true")
    a = p.parse_args(argv)

    ledger_path = resolve_ledger(a.ledger or pathlib.Path(LEDGER), explicit=a.ledger is not None)
    rows = load(ledger_path)
    if a.all:
        worst = 0
        for e in sorted({epic_of(r) for r in rows}):
            worst |= report([r for r in rows if epic_of(r) == e], e, a.verbose)
        print(f"\n{sum(1 for r in rows if violations(r))} of {len(rows)} findings "
              f"in {ledger_path} are undisposed")
        if off := off_vocabulary_channels(rows):
            print(f"\nADVISORY (not a clause): {len(off)} row(s) carry a `channel` "
                  f"outside the vocabulary in references/consumption.md:")
            for rid, ch in off:
                print(f"           {rid}: {ch!r}")
        return worst
    if a.ticket:
        sel = [r for r in rows if str(r.get("found_by") or r.get("id", "")).startswith(a.ticket)
               and str(r.get("id", "")).startswith(a.ticket + "-")]
        return report(sel, f"ticket {a.ticket}", a.verbose)
    want = EPICS.get(a.epic.upper(), a.epic)
    return report([r for r in rows if epic_of(r) == want], f"epic {want}", a.verbose)


if __name__ == "__main__":
    sys.exit(main())
