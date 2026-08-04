#!/usr/bin/env python3
"""Integrity harness for the HP-01 seeded fault catalogue.

    python3 examples/validation/ab/check_catalogue.py
    python3 examples/validation/ab/check_catalogue.py --arms
    python3 examples/validation/ab/check_catalogue.py --verify-suite
    python3 examples/validation/ab/check_catalogue.py --root <arm-tree> \\
        --catalogue <arm-catalogue.toml>

**It gates nothing in the toolchain.** Per the epic plan's `no_new_gates_rule`
this epic ships no new blocking check and no new static analyzer. This is a
fixture-integrity harness in the shape of the shipped
`examples/validation/check_twins.py`: it refuses nothing in the product, it
runs when a human or HP-06 runs it, and its exit code says whether the
catalogue is self-consistent. A catalogue that is not self-consistent produces
numbers nobody can re-derive, which is the only thing this file is here to
prevent.

What it asserts:

  1. Every `find` pattern occurs **EXACTLY ONCE** in its target file. This is
     the load-bearing one. A pattern occurring twice seeds two faults and
     reports the result as one; a pattern occurring zero times seeds nothing
     and reports a survivor.
  2. `find` and `replace` differ, and applying the mutant actually changes the
     file.
  3. Apply-then-revert is **byte-identical**. A harness that can corrupt the
     fixture it measures is not a harness.
  4. The mutated file still parses. A mutant that breaks the syntax kills every
     instrument trivially and measures nothing.
  5. The catalogue loads under the shipped `scripts/kill_test.py` parser, so
     the shipped primitive can run it and so suppression-shaped keys are
     reported by the shipped tripwire rather than by a private copy of it.
  6. Every required fault class is present, and every declared mechanism gap
     carries at least one mutant. "Seed a fault in the gap each mechanism is
     supposed to lose" is a rule with a measured origin: round 1 concluded that
     case modules kill exactly what the whole view kills, and that conclusion
     was an artifact of a catalogue with no cross-aspect mutant in it.
  7. Exactly one positive control and at least one negative control exist.

`--verify-suite` additionally runs the shared behavioral suite under every
mutant, **against the reference only**, and compares the result with each
mutant's `predicted_suite` field. That is fixture verification, not the eval:
it measures this file's own hand-written suite against this file's own
reference, and it touches neither arm nor any mechanism the epic ships. It
exists because a catalogue whose annotations are wrong is worse than one with
no annotations.
"""

from __future__ import annotations

import argparse
import ast
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent.parent

#: Every class the eval needs evidence for. A missing class is a refusal: the
#: catalogue would report a silence that reads like a measurement.
REQUIRED_CLASSES = {
    "guard_relaxation": "0 on every instrument in every round; HP-03's whole target",
    "durable_content": "the one mechanism with a measured, replicated edge (HP-05)",
    "cross_aspect": "the gap the aspect slice loses; round 1's false conclusion",
    "output_oracle": "the class a state-only oracle cannot see at all",
    "wrong_value": "the positive control, plus HP-04's apply-only blind spot",
    "ordering": "the negative control; a documented limit, measured instead of assumed",
}

#: The mechanism gaps the plan names. Each must carry at least one mutant, and
#: the mutant's `gap_targeted` prose must mention the keyword.
REQUIRED_GAPS = {
    "enabled": "HP-03 -- a corpus replays only ENABLED edges, so it holds no refusal",
    "slice": "case modules -- a slice narrower than its view orphans the other aspect",
    "silent": "HP-05 -- a silent mapping has no durable-write oracle",
    "apply()-only": "HP-04 -- the oracle aborts on the first apply()-only adapter",
}


def load_catalogue(path: Path) -> tuple[list, list[dict], list[str]]:
    """Load via the SHIPPED parser, plus the raw rows for our extra fields."""
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import kill_test  # noqa: PLC0415

    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
        import tomli as tomllib  # type: ignore[no-redef]

    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    mutants, suppressions = kill_test.load_catalog(path)
    return mutants, raw.get("mutants", []), suppressions


def check_integrity(catalogue: Path, root: Path) -> list[str]:
    problems: list[str] = []
    mutants, rows, suppressions = load_catalogue(catalogue)

    if suppressions:
        problems.append(
            "catalogue carries suppression-shaped keys "
            f"({', '.join(suppressions)}). They are never honored; remove them."
        )

    print(f"catalogue: {catalogue}")
    print(f"root:      {root}")
    print(f"{len(mutants)} mutant(s)\n")
    print(f"{'id':<42} {'class':<18} occurs  revert  parses")
    print("-" * 86)

    by_class: dict[str, list[str]] = {}
    for mutant, row in zip(mutants, rows):
        by_class.setdefault(str(row.get("fault_class", "<none>")), []).append(mutant.id)
        target = root / mutant.path
        if not target.is_file():
            problems.append(f"{mutant.id}: no such file {target}")
            print(f"{mutant.id:<42} {'?':<18} MISSING")
            continue

        original = target.read_text(encoding="utf-8")
        occurrences = original.count(mutant.find)

        # (1) EXACTLY ONCE. The load-bearing assertion.
        if occurrences != 1:
            problems.append(
                f"{mutant.id}: `find` occurs {occurrences} time(s) in {mutant.path}, "
                f"must be exactly 1. "
                + (
                    "Zero seeds nothing and reports a survivor."
                    if occurrences == 0
                    else "More than one seeds several faults and reports them as one."
                )
            )

        # (2) the mutant must actually mutate
        if mutant.find == mutant.replace:
            problems.append(f"{mutant.id}: find and replace are identical")

        patched = original.replace(mutant.find, mutant.replace, 1)
        if patched == original:
            problems.append(f"{mutant.id}: applying the mutant changed nothing")

        # (3) apply/revert is byte-identical
        reverted_ok = False
        try:
            target.write_text(patched, encoding="utf-8")
            reverted_ok = True
        finally:
            target.write_text(original, encoding="utf-8")
        if target.read_text(encoding="utf-8") != original:
            problems.append(f"{mutant.id}: apply/revert was NOT byte-identical")
            reverted_ok = False

        # (4) the mutant still parses
        parses = True
        if mutant.path.endswith(".py"):
            try:
                ast.parse(patched)
            except SyntaxError as exc:
                parses = False
                problems.append(
                    f"{mutant.id}: the mutated file does not parse ({exc}). A syntax "
                    f"error kills every instrument trivially and measures nothing."
                )

        print(
            f"{mutant.id:<42} {str(row.get('fault_class','')):<18} "
            f"{occurrences:^6} {'ok' if reverted_ok else 'FAIL':^7} {'ok' if parses else 'FAIL':^6}"
        )

    # (6) required classes
    print()
    missing_classes = sorted(set(REQUIRED_CLASSES) - set(by_class))
    for name in missing_classes:
        problems.append(f"no mutant in required class {name!r} ({REQUIRED_CLASSES[name]})")

    # (6) required gaps
    gap_text = " ".join(str(row.get("gap_targeted", "")) for row in rows).lower()
    for keyword, why in REQUIRED_GAPS.items():
        if keyword.lower() not in gap_text:
            problems.append(
                f"no mutant declares a fault in the {keyword!r} gap ({why}). "
                f"A reduction result with no mutant in the gap is not a measurement."
            )

    # (7) controls
    roles = [str(row.get("control_role", "")) for row in rows]
    positives = [r for r in roles if r.startswith("positive")]
    negatives = [r for r in roles if r.startswith("negative")]
    if len(positives) != 1:
        problems.append(
            f"expected exactly 1 positive control, found {len(positives)}. Without one, "
            f"a table of zeros cannot be told apart from a broken instrument."
        )
    if not negatives:
        problems.append("expected at least 1 negative control")

    print("class coverage:")
    for name in sorted(by_class):
        marker = "" if name in REQUIRED_CLASSES else "   (not a required class)"
        print(f"  {name:<20} {len(by_class[name])}  {', '.join(by_class[name])}{marker}")
    print(f"\ncontrols: {len(positives)} positive, {len(negatives)} negative")
    return problems


def check_arms() -> list[str]:
    """Report the two arms. Reports; does not refuse."""
    problems: list[str] = []
    arm_a = HERE / "arm_a" / "PROMPT.md"
    arm_b = HERE / "arm_b" / "PROMPT.md"

    print("\narms:")
    for path in (arm_a, arm_b):
        if not path.is_file():
            problems.append(f"missing arm prompt {path}")
            return problems
        print(f"  {path.relative_to(REPO_ROOT)}  ({len(path.read_text().splitlines())} lines)")

    a_lines = {ln.strip() for ln in arm_a.read_text().splitlines() if ln.strip()}
    b_lines = {ln.strip() for ln in arm_b.read_text().splitlines() if ln.strip()}

    # "Neither is the other with a section removed" -- i.e. neither is a subset.
    if a_lines <= b_lines:
        problems.append(
            "arm A's content is a strict subset of arm B's: arm A IS arm B with a "
            "section removed. Declare the arms as two independent prompts."
        )
    if b_lines <= a_lines:
        problems.append("arm B's content is a strict subset of arm A's")

    shared = a_lines & b_lines
    print(
        f"  shared verbatim: {len(shared)} lines (the controlled envelope)\n"
        f"  unique to A:     {len(a_lines - b_lines)} lines\n"
        f"  unique to B:     {len(b_lines - a_lines)} lines"
    )
    print(
        "  The shared envelope is deliberate: the arms differ in the TREATMENT\n"
        "  (arm B section 1), not in the delivery, the feature, or the ground rules."
    )

    body = arm_b.read_text()
    if "HP-02-SLOT:BEGIN" not in body or "HP-02-SLOT:END" not in body:
        problems.append("arm B has no HP-02 slot markers")
    elif "UNFILLED" in body:
        print(
            "\n  ARM B SLOT: **UNFILLED** -- HP-02 owns it. Arm B must not be\n"
            "  dispatched in this state. Reported, not refused: nothing here gates."
        )
    else:
        print("\n  ARM B SLOT: filled.")
    return problems


def verify_suite(catalogue: Path, root: Path) -> list[str]:
    """Run the shared suite under every mutant, on the REFERENCE ONLY."""
    mutants, rows, _ = load_catalogue(catalogue)
    suite = HERE / "tests" / "test_behavior.py"
    results: list[tuple[str, str, str]] = []

    def run(impl_dir: Path) -> bool:
        env = dict(os.environ, QUOTA_LEDGER_DIR=str(impl_dir), QUOTA_LEDGER_IMPL="quota_ledger")
        done = subprocess.run(
            ["uv", "run", "--with", "pytest", "python", "-m", "pytest", str(suite), "-q"],
            cwd=REPO_ROOT, env=env, capture_output=True, text=True,
        )
        return done.returncode == 0

    print("\nsuite verification (reference only -- NOT an arm measurement):")
    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp) / "reference"
        shutil.copytree(root / "reference", workdir)
        pristine = (workdir / "quota_ledger.py").read_text(encoding="utf-8")

        # The control run. Without it, a "kill" may predate every mutant.
        if not run(workdir):
            return ["CONTROL RUN FAILED: the suite is red on the unmutated reference. "
                    "Every kill below would be that same unrelated failure."]
        print("  control (no mutant): suite GREEN\n")

        for mutant, row in zip(mutants, rows):
            target = workdir / Path(mutant.path).name
            try:
                target.write_text(pristine.replace(mutant.find, mutant.replace, 1), encoding="utf-8")
                killed = not run(workdir)
            finally:
                target.write_text(pristine, encoding="utf-8")
            observed = "KILLED" if killed else "SURVIVED"
            predicted = str(row.get("predicted_suite", ""))
            agrees = predicted.upper().startswith(observed[:6].upper())
            results.append((mutant.id, observed, predicted))
            print(f"  {mutant.id:<42} {observed:<9} {'agrees' if agrees else '*** DISAGREES ***'}")
            if not agrees:
                print(f"      predicted_suite: {predicted}")

    print(
        "\n  A disagreement is not a failure of this harness -- it is the catalogue's\n"
        "  annotation being wrong, and it must be corrected BEFORE dispatch or\n"
        "  recorded as a finding after it."
    )
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalogue", type=Path, default=HERE / "seeded_faults.toml")
    parser.add_argument("--root", type=Path, default=HERE,
                        help="tree the mutant paths are relative to (an arm tree at HP-06)")
    parser.add_argument("--arms", action="store_true", help="also report the two arm prompts")
    parser.add_argument("--verify-suite", action="store_true",
                        help="run the shared suite under every mutant, reference only")
    args = parser.parse_args()

    problems = check_integrity(args.catalogue.resolve(), args.root.resolve())
    if args.arms:
        problems += check_arms()
    if args.verify_suite:
        problems += verify_suite(args.catalogue.resolve(), args.root.resolve())

    print()
    if problems:
        print("CATALOGUE INTEGRITY FAILED -- numbers derived from it are not re-derivable:")
        for line in problems:
            print(f"  {line}")
        return 1
    print("Catalogue integrity holds: every pattern occurs exactly once, every")
    print("mutant applies and reverts cleanly, and every declared gap is seeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
