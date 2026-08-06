#!/usr/bin/env python3
"""R1: R-H5's demonstrated failing input, on the real ledger, re-runnably.

R1 asks for more than a test that the instrument runs. It asks for a
demonstration that the instrument goes RED when the thing it watches is
genuinely broken, on real data, that anyone can re-run.

This copies the whole live scorecard tree to a temporary directory, confirms
`audit` is green on the copy, then breaks it in the two ways R-H5 exists to
catch and confirms it goes red each time:

  1. a movement row that stopped matching the cards it names -- the stale row;
  2. a movement declared `readable` across a card that says nothing about what
     its judge did -- the thing that moved four dimension-points on
     byte-identical trees.

**Nothing under specs/ is modified.** The live tree is copied, never edited, and
the copy is discarded. Exits non-zero if either break fails to produce a
violation, because a check that cannot go red is worse than no check.

  python3 demonstrate_rh5.py [--keep]
"""
from __future__ import annotations

import argparse
import importlib.util
import io
import contextlib
import pathlib
import re
import shutil
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve()
REPO_ROOT = HERE.parents[6]
SCORECARDS = REPO_ROOT / "specs/results/scorecards"
TOOL = REPO_ROOT / "examples/validation/scorecards/score_tools.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("score_tools_fi03", TOOL)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def audit(st, root: pathlib.Path) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = st.main(["audit", "--root", str(root), "--quiet-ok"])
    return rc, buf.getvalue()


def rh5_violations(text: str) -> list[str]:
    out, inside = [], False
    for line in text.splitlines():
        if line.startswith("## R-H5"):
            inside = True
            continue
        if line.startswith("## "):
            inside = False
        if inside and line.strip().startswith("VIOLATION"):
            out.append(line.strip())
    return out


def first_movement_block(text: str) -> tuple[int, int]:
    """(start, end) character offsets of the first [[movement]] block."""
    m = re.search(r"^\[\[movement\]\]\n(?:.+\n)+?(?=\n|\Z)", text, re.M)
    if not m:
        sys.exit("no [[movement]] in the ledger -- run derive_movements.py and record some")
    return m.start(), m.end()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true", help="keep the temporary copy")
    args = ap.parse_args(argv)

    st = load_tool()
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="fi03-rh5-"))
    root = tmp / "scorecards"
    shutil.copytree(SCORECARDS, root)
    log = root / "INSTRUMENT-LOG.toml"
    original = log.read_text()
    failures = []

    print("=" * 74)
    print("R-H5 DEMONSTRATED FAILING INPUT -- run against a copy of the live ledger")
    print(f"source: {SCORECARDS}")
    print("=" * 74)

    rc, out = audit(st, root)
    print(f"\n[0] UNMODIFIED COPY -> exit {rc}, R-H5 violations: {len(rh5_violations(out))}")
    if rc != 0 or rh5_violations(out):
        failures.append("the unmodified copy is not green, so nothing below means anything")
        print(out)

    # --- break 1: a row that stopped matching the cards it names -------------
    start, end = first_movement_block(original)
    block = original[start:end]
    mid = re.search(r'^id = "(.+)"', block, re.M).group(1)
    points = int(re.search(r"^points = (-?\d+)", block, re.M).group(1))
    broken = re.sub(r"^points = -?\d+", f"points = {points + 7}", block, flags=re.M)
    log.write_text(original[:start] + broken + original[end:])
    rc, out = audit(st, root)
    found = rh5_violations(out)
    print(f"\n[1] STALE ROW -- `{mid}` says points = {points + 7}, the cards say {points}")
    print(f"    exit {rc}, R-H5 violations: {len(found)}")
    for line in found:
        print("   ", line)
    if rc == 0 or not any("re-derived from the cards" in f for f in found):
        failures.append("a stale movement row did not produce a violation")

    # --- break 2: read across a card that says nothing about its judge -------
    log.write_text(original)
    unreadable = re.search(r"^\[\[movement\]\]\n(?:.+\n)*?readable = false\n(?:.+\n)*?"
                           r"(?=\n|\Z)", original, re.M)
    if not unreadable:
        failures.append("no `readable = false` movement in the ledger to flip")
    else:
        blk = unreadable.group(0)
        mid = re.search(r'^id = "(.+)"', blk, re.M).group(1)
        flipped = blk.replace("readable = false", "readable = true")
        log.write_text(original[:unreadable.start()] + flipped + original[unreadable.end():])
        rc, out = audit(st, root)
        found = rh5_violations(out)
        print(f"\n[2] READ ACROSS AN UNRECORDED PRACTICE -- `{mid}` declared readable = true")
        print(f"    exit {rc}, R-H5 violations: {len(found)}")
        for line in found:
            print("   ", line)
        if rc == 0 or not any("DO NOT READ THE MOVEMENT" in f for f in found):
            failures.append("reading a movement across an unrecorded practice did not "
                            "produce a violation")

    log.write_text(original)
    rc, out = audit(st, root)
    print(f"\n[3] RESTORED -> exit {rc}, R-H5 violations: {len(rh5_violations(out))}")
    if rc != 0:
        failures.append("the restored copy is not green again")

    if args.keep:
        print(f"\ncopy kept at {tmp}")
    else:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if failures:
        for f in failures:
            print(f"FAILED: {f}")
        print("\nR-H5 CANNOT FAIL. Report it red; do not ship it.")
        return 1
    print("R-H5 goes RED on both of the inputs it exists to catch, and GREEN otherwise.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
