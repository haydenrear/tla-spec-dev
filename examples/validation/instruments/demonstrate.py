#!/usr/bin/env python3
"""FI-02. Run every shipped instrument against a DEMONSTRATED FAILING INPUT.

    python3 examples/validation/instruments/demonstrate.py
    python3 examples/validation/instruments/demonstrate.py --tier fast
    python3 examples/validation/instruments/demonstrate.py --only corpus-runner
    python3 examples/validation/instruments/demonstrate.py --format json --out FILE

`references/architecture_advice.md` **S2**: *"Every criterion must have a
demonstrated failing input and a demonstrated passing input."* It was written
for a scanner that has since been deleted, and until FI-01 it had never been
turned on an instrument this repository kept. FI-01 turned it on one -- the
control-property probe -- and the result justified the epic: against the parent
probe exactly as it shipped, three of four deliberately broken controls reported
`HOLDS`. Every `HOLDS` that probe had ever printed was uninformative.

This file turns it on everything else.

WHAT A ROW MEANS. For each instrument the registry declares up to three
demonstrations, each of which is RE-RUNNABLE and each of which STAGES ITS OWN
TREE in a temporary directory, so nothing here edits the repository:

    failing      the thing the instrument watches is GENUINELY BROKEN, and the
                 instrument must report it. Not a test that the instrument
                 runs; a demonstration that it goes red.
    passing      the same instrument on an unbroken subject, which must stay
                 green. S2 asks for both, and an instrument that reported
                 everything broken would be as useless as one that reported
                 everything fine.
    blind_spot   a genuine break the instrument demonstrably does NOT report.
                 This slot exists because R2 says a control that cannot fail is
                 reported, never patched into looking fine -- and because the
                 count of things our instruments cannot see is the honest
                 product of this ticket.

WHERE A SLOT IS ABSENT the registry must say why in `no_failing_demonstration`
or `no_passing_demonstration`, and the reason is printed in the table. THE COUNT
OF INSTRUMENTS WITH NO DEMONSTRATED FAILING INPUT IS THIS COMMAND'S PRODUCT. A
high count is the honest outcome. There is no target on the ratio; setting one
before anything had ever been demonstrated would be inventing the answer.

THIS IS NOT A GATE. It refuses nothing about the repository's design and no
close path consults it. It exits non-zero for exactly one reason: a DECLARED
demonstration did not reproduce -- which means either the instrument changed or
the demonstration went stale, and both are things a reader must be told rather
than left to discover.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
REGISTRY = HERE / "instruments.toml"

SLOTS = ("failing", "passing", "blind_spot")

#: A demonstration is either run as a command line, or it is a pytest node that
#: performs the break-and-check in process. `declared` carries no executable
#: form and must carry a `reason`.
KINDS = ("cli", "pytest", "declared")


class DemonstrationError(RuntimeError):
    """The demonstration itself is malformed -- distinct from a red instrument."""


# ---------------------------------------------------------------------------
# staging
# ---------------------------------------------------------------------------


def stage(spec: dict[str, Any], tree: Path) -> None:
    """Copy the declared inputs into `tree`, then break them as declared.

    Everything an instrument reads is staged, so the demonstration never edits
    the repository and two demonstrations of the same instrument cannot
    interfere. `check_catalogue.py` and `make_blind_copies.py` both WRITE to the
    tree they measure; that is why this is not optional.
    """

    for entry in spec.get("stage", []):
        source = REPO_ROOT / entry["from"]
        destination = tree / entry["to"]
        if not source.exists():
            raise DemonstrationError(f"stage source does not exist: {entry['from']}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, destination, ignore=shutil.ignore_patterns("__pycache__"))
        else:
            shutil.copy2(source, destination)

    for entry in spec.get("mutate", []):
        target = tree / entry["file"]
        if not target.is_file():
            raise DemonstrationError(f"mutate target is not a file: {entry['file']}")
        text = target.read_text(encoding="utf-8")
        if "append" in entry:
            target.write_text(text + entry["append"], encoding="utf-8")
            continue
        find, replace = entry["find"], entry["replace"]
        occurrences = text.count(find)
        if occurrences != 1:
            # The same rule `check_catalogue.py` applies to a seeded fault:
            # zero seeds nothing and reports a false green, more than one seeds
            # several faults and reports them as one.
            raise DemonstrationError(
                f"{entry['file']}: `find` occurs {occurrences} time(s), must be exactly 1"
            )
        if find == replace:
            raise DemonstrationError(f"{entry['file']}: find and replace are identical")
        target.write_text(text.replace(find, replace), encoding="utf-8")


def expand(value: str, tree: Path) -> str:
    return (
        value.replace("{repo}", str(REPO_ROOT))
        .replace("{tree}", str(tree))
        .replace("{python}", sys.executable)
    )


# ---------------------------------------------------------------------------
# running
# ---------------------------------------------------------------------------


def run_cli(spec: dict[str, Any], tree: Path) -> dict[str, Any]:
    argv = [expand(part, tree) for part in spec["argv"]]
    cwd = expand(spec.get("cwd", "{tree}"), tree)
    completed = subprocess.run(
        argv, cwd=cwd, capture_output=True, text=True, timeout=spec.get("timeout", 900)
    )
    return {
        "exit": completed.returncode,
        "output": completed.stdout + completed.stderr,
        "argv": argv,
    }


def run_pytest(spec: dict[str, Any], tree: Path) -> dict[str, Any]:
    argv = [
        "uv", "run", "--with", "pytest", "--with", "pyyaml",
        "python", "-m", "pytest", "-q", *spec["nodes"],
    ]
    completed = subprocess.run(
        argv, cwd=REPO_ROOT, capture_output=True, text=True, timeout=spec.get("timeout", 900)
    )
    return {
        "exit": completed.returncode,
        "output": completed.stdout + completed.stderr,
        "argv": argv,
    }


def judge(spec: dict[str, Any], observed: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    expected_exit = spec.get("expect_exit")
    if expected_exit is not None and observed["exit"] != expected_exit:
        problems.append(f"exit {observed['exit']}, declared {expected_exit}")
    for needle in spec.get("expect_output", []):
        if needle not in observed["output"]:
            problems.append(f"output does not contain {needle!r}")
    for needle in spec.get("expect_absent", []):
        if needle in observed["output"]:
            problems.append(f"output contains {needle!r}, which it must not")
    return problems


def demonstrate(spec: dict[str, Any]) -> dict[str, Any]:
    kind = spec.get("kind", "cli")
    if kind not in KINDS:
        raise DemonstrationError(f"unknown demonstration kind {kind!r}")
    if kind == "declared":
        return {"kind": kind, "ran": False, "problems": [], "reason": spec.get("reason", "")}

    workspace = Path(tempfile.mkdtemp(prefix="fi02-demo-"))
    try:
        tree = workspace / "tree"
        tree.mkdir()
        if kind == "cli":
            stage(spec, tree)
            observed = run_cli(spec, tree)
        else:
            observed = run_pytest(spec, tree)
        return {
            "kind": kind,
            "ran": True,
            "exit": observed["exit"],
            "problems": judge(spec, observed),
            "argv": observed["argv"],
            "tail": "\n".join(observed["output"].splitlines()[-6:]),
        }
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


# ---------------------------------------------------------------------------
# the enumeration
# ---------------------------------------------------------------------------


def load_registry(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def selected(instrument: dict[str, Any], only: list[str], tier: str) -> bool:
    if only and instrument["id"] not in only:
        return False
    return True


def slot_runnable(spec: dict[str, Any] | None, tier: str) -> bool:
    if spec is None:
        return False
    if spec.get("kind", "cli") == "declared":
        return False
    if tier == "fast" and spec.get("tier", "fast") != "fast":
        return False
    return True


def run(args: argparse.Namespace) -> int:
    registry = load_registry(args.registry)
    instruments = registry["instrument"]

    if args.list:
        for entry in instruments:
            print(f"{entry['id']:<34} {entry['classification']}")
        return 0

    rows: list[dict[str, Any]] = []
    failures: list[str] = []

    for entry in instruments:
        if not selected(entry, args.only, args.tier):
            continue
        row: dict[str, Any] = {
            "id": entry["id"],
            "name": entry["name"],
            "paths": entry.get("paths", []),
            "family": entry["family"],
            "classification": entry["classification"],
            "watches": entry["watches"],
            "verdict_surface": entry["verdict_surface"],
            "has_failing_demonstration": "failing" in entry,
            "has_passing_demonstration": "passing" in entry,
            "no_failing_demonstration": entry.get("no_failing_demonstration"),
            "no_passing_demonstration": entry.get("no_passing_demonstration"),
            "slots": {},
        }
        for slot in SLOTS:
            spec = entry.get(slot)
            if spec is None:
                continue
            if not slot_runnable(spec, args.tier):
                row["slots"][slot] = {"ran": False, "skipped": True,
                                      "summary": spec.get("summary", ""),
                                      "reason": spec.get("reason", "")}
                continue
            try:
                result = demonstrate(spec)
            except DemonstrationError as exc:
                result = {"kind": spec.get("kind", "cli"), "ran": False,
                          "problems": [f"MALFORMED DEMONSTRATION: {exc}"]}
            except subprocess.TimeoutExpired:
                result = {"kind": spec.get("kind", "cli"), "ran": False,
                          "problems": ["TIMED OUT"]}
            result["summary"] = spec.get("summary", "")
            row["slots"][slot] = result
            for problem in result["problems"]:
                failures.append(f"{entry['id']} / {slot}: {problem}")
        rows.append(row)

    report = {
        "registry": registry["registry"],
        "tier": args.tier,
        "rows": rows,
        "counts": counts(rows),
        "reproduction_failures": failures,
    }

    if args.format == "json":
        payload = json.dumps(report, indent=2, sort_keys=True)
    else:
        payload = render(report)
    print(payload)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(f"\nwrote {args.out}")
    return 1 if failures else 0


def counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    instruments = [r for r in rows if r["family"] != "not-an-instrument"]
    return {
        "enumerated": len(rows),
        "instruments": len(instruments),
        "not_an_instrument": len(rows) - len(instruments),
        "with_failing_demonstration": sum(1 for r in instruments if r["has_failing_demonstration"]),
        "without_failing_demonstration": sum(
            1 for r in instruments if not r["has_failing_demonstration"]
        ),
        "with_passing_demonstration": sum(1 for r in instruments if r["has_passing_demonstration"]),
        "with_a_demonstrated_blind_spot": sum(1 for r in rows if "blind_spot" in r["slots"]),
    }


def render(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("FI-02 -- every shipped instrument, and whether it can be shown to fail")
    lines.append("=" * 78)
    lines.append("")
    lines.append(f"{'instrument':<34} {'fail':<6} {'pass':<6} {'blind':<6} classification")
    lines.append("-" * 78)

    def mark(row: dict[str, Any], slot: str) -> str:
        result = row["slots"].get(slot)
        if result is None:
            return "-"
        if result.get("skipped"):
            return "skip"
        if result["problems"]:
            return "MISS"
        if not result.get("ran"):
            return "decl"
        return "ok"

    for row in report["rows"]:
        lines.append(
            f"{row['id']:<34} {mark(row, 'failing'):<6} {mark(row, 'passing'):<6} "
            f"{mark(row, 'blind_spot'):<6} {row['classification']}"
        )

    lines.append("")
    lines.append("THE COUNT -- this command's product")
    lines.append("-" * 78)
    counted = report["counts"]
    lines.append(f"  enumerated                              {counted['enumerated']}")
    lines.append(f"  of which classified NOT an instrument   {counted['not_an_instrument']}")
    lines.append(f"  instruments                             {counted['instruments']}")
    lines.append(f"  WITH a demonstrated failing input       {counted['with_failing_demonstration']}")
    lines.append(f"  WITHOUT one, and why, below             {counted['without_failing_demonstration']}")
    lines.append(f"  with a demonstrated BLIND SPOT          {counted['with_a_demonstrated_blind_spot']}")
    lines.append("")
    lines.append("  No target is set on that ratio. A high count in the fifth row is the")
    lines.append("  honest outcome and the epic prefers it to a flattering one.")

    without = [r for r in report["rows"]
               if r["family"] != "not-an-instrument" and not r["has_failing_demonstration"]]
    if without:
        lines.append("")
        lines.append("INSTRUMENTS THAT CANNOT BE SHOWN TO FAIL, with the reason")
        lines.append("-" * 78)
        for row in without:
            lines.append(f"  {row['id']}")
            lines.append(f"      {row['no_failing_demonstration']}")

    blind = [r for r in report["rows"] if "blind_spot" in r["slots"]]
    if blind:
        lines.append("")
        lines.append("DEMONSTRATED BLIND SPOTS -- a genuine break each one does NOT report")
        lines.append("-" * 78)
        for row in blind:
            lines.append(f"  {row['id']}")
            lines.append(f"      {row['slots']['blind_spot'].get('summary', '')}")

    if report["reproduction_failures"]:
        lines.append("")
        lines.append("A DECLARED DEMONSTRATION DID NOT REPRODUCE")
        lines.append("-" * 78)
        for problem in report["reproduction_failures"]:
            lines.append(f"  {problem}")
        lines.append("")
        lines.append("  Either the instrument changed or the demonstration went stale.")
        lines.append("  Both are things a reader has to be told.")
    else:
        lines.append("")
        lines.append("Every declared demonstration reproduced.")
    return "\n".join(lines)


def add_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--only", action="append", default=[])
    parser.add_argument("--tier", choices=("fast", "all"), default="all")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--list", action="store_true")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(parser)
    return run(parser.parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
