#!/usr/bin/env python3
"""Refuse an epic close-out while any finding it filed is undisposed.

THIS IS NOT A GATE ON ANYONE'S CODE. It is a close-out requirement on THIS
project's own epics, run by hand at epic close and by `CA-08`. It reads one file
-- `specs/deferred_findings.yaml` -- and reports whether the findings an epic
filed were routed anywhere.

`SS-01` MOVED THAT ADDRESS, and the move is the point rather than a detail. The
ledger used to live at `specs/desired_program_model/deferred_findings.yaml`,
inside the directory `scripts/close_tickets.py` REMOVES at workflow close -- so
the cumulative, cross-epic record of every finding this project has filed
vanished at exactly the moment someone wanted to read what the closed epic had
filed. It lived there by accident of scaffolding, not because it belongs to one
workflow (`CA-10-DF-10`). It now lives beside the workflow directories instead
of inside one, and survives their removal.

The read fallback stays, because a tree with no live ledger is still a tree an
adopter can hand this script -- but `resolve_ledger` no longer GUESSES which
archived copy is the ledger. See `archived_ledgers`.

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
import json
import re
import pathlib
import sys

LEDGER = "specs/deferred_findings.yaml"

# WHERE AN ARCHIVED LEDGER IS FOUND, AND WHY IT IS FOUND BY READING RATHER THAN
# BY GLOBBING. A workflow close writes the ledger at the top of its history entry
# (`spec_evolution.snapshot_findings_ledger`) and RECORDS THE ADDRESS in that
# entry's `manifest.json`, under `findings_ledger`, beside `created_at_utc`.
# Those are facts stored IN THE TREE, so they read the same in every checkout.
HISTORY_MANIFESTS = "specs/.history/*/*/manifest.json"

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
    """Every archived ledger a workflow close RECORDED, oldest close last-but-one.

    RESOLVED FROM THE TREE, NEVER FROM THE FILESYSTEM. `SS-00-DF-01`: this used
    to glob for the FILENAME and order the hits by `(st_mtime, st_size, path)`.
    Git does not carry mtimes, so that order was a property of the CHECKOUT. On
    a fresh clone of this repository it selected a four-epic-old MID-TICKET
    snapshot with 88 ids over the 296-id copy the close recorded, and `audit`
    then reported nine TRUE `filed_as` citations as fabrications. One `touch` on
    the correct file moved the same tree from nine violations to zero.

    (Two details of that finding are corrected by `SS-01-DF-02`, because they
    change what a fix would have to be: the 85 candidates do NOT share one
    mtime -- they carry 85 distinct ones -- so the order never fell through to
    size, and the LARGEST candidate is the CORRECT one. "Sort by size" reads
    like a repair and is not one.)

    So the filename is not the question. A close writes the ledger at the top of
    its history entry and NAMES it in that entry's `manifest.json` under
    `findings_ledger`; ordering is by the manifest's own `created_at_utc`. A
    copy no manifest points at is not a candidate at all -- it cannot be
    identified as the ledger any close kept, and identifying one anyway is what
    produced the wrong answer. That leaves `resolve_ledger` with nothing to
    return in some trees, which is the correct answer and not a gap.
    """
    found: list[tuple[str, str, pathlib.Path]] = []
    for manifest_path in root.glob(HISTORY_MANIFESTS):
        try:
            manifest = json.loads(manifest_path.read_text())
        except (OSError, ValueError):
            continue
        record = manifest.get("findings_ledger")
        if not isinstance(record, dict) or not record.get("exists") or not record.get("snapshot"):
            continue
        snapshot = pathlib.Path(str(record["snapshot"]))
        for candidate in (root / snapshot, manifest_path.parent / snapshot.name):
            if candidate.is_file():
                found.append((str(manifest.get("created_at_utc") or ""),
                              str(manifest_path), candidate.resolve()))
                break
    return [path for _, _, path in sorted(found)]


def resolve_ledger(path: pathlib.Path, *, explicit: bool,
                   root: pathlib.Path | None = None) -> pathlib.Path:
    """The live ledger if it is there; otherwise the one the latest close RECORDED.

    THIS IS A READ FALLBACK, NOT AN EXEMPTION, and after `SS-01` it is the RARE
    case rather than the normal one: the live ledger now sits beside the
    workflow directories instead of inside one, so a close no longer removes it.
    The fallback remains because it is the path an adopter's tree takes, and
    `SS-00-DF-01` was a defect in the fallback, not in the address.

    NOTHING HERE PROMISES A FREEZE. It used to -- "an archived ledger is FROZEN
    at that close" -- and this repository's own record falsifies it: the copy
    `cut-the-apparatus-epic` archived carries 296 rows against the 278 its own
    close snapshot took, because the close had left nowhere else to write
    (`CA-10-DF-10`). What is promised is what can be checked: this is the copy
    that close RECORDED, chosen from the tree.

    `root` is WHICH tree, and it used to be missing: the archive search ran
    against the process's working directory whatever ledger it was asked about,
    so a caller pointing at another checkout was answered from this one. It
    defaults to the working directory, which is what the CLI means.
    """
    if path.exists():
        return path
    if explicit:
        raise SystemExit(f"{path}: no such ledger (--ledger was given explicitly, so no archive is searched)")
    archives = archived_ledgers(root if root is not None else pathlib.Path("."))
    if not archives:
        raise SystemExit(
            f"{path}: no ledger there, and no workflow close under specs/.history "
            f"RECORDS one in its manifest under `findings_ledger`. UNVERIFIED -- "
            f"refusing to report a verdict against whichever archived copy happens "
            f"to be biggest, or newest on this checkout (`SS-00-DF-01`). Name one "
            f"with --ledger if you know which it is."
        )
    newest = archives[-1]
    print(
        f"NOTE: {path} is absent. Reading the archived ledger {newest} -- the copy "
        f"the LATEST workflow close recorded under `findings_ledger`, chosen from "
        f"the tree and not from file timestamps. A verdict from it is a verdict "
        f"about that closed epic.",
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
        help=f"ledger to read (default {LEDGER}, falling back to the archived copy the "
             f"latest workflow close recorded under specs/.history when there is no live one)",
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
