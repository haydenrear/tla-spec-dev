#!/usr/bin/env python3
"""Integrity harness for the HP-01 seeded fault catalogue.

    python3 examples/validation/ab/check_catalogue.py
    python3 examples/validation/ab/check_catalogue.py --arms
    python3 examples/validation/ab/check_catalogue.py --controls
    python3 examples/validation/ab/check_catalogue.py --verify-suite
    python3 examples/validation/ab/check_catalogue.py --root <arm-tree> \\
        --catalogue <arm-catalogue.toml>
    python3 examples/validation/ab/check_catalogue.py --controls --tree-root \\
        --root <arm-tree> --catalogue <arm-catalogue.toml> --impl <module>

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
  7. Exactly one positive control PER ANCHOR TREE, and at least one negative
     control. Per-tree since PA-01: with two anchor trees, one global control
     leaves the second tree with no witness, and a column of survivors there
     cannot be told apart from an instrument that never ran it.
  8. Since PA-01: every mutant seeded inside a declared adapter implementation
     declares `fault_class = "adapter_internal"`, and every row declaring that
     class is seeded inside a declared adapter -- checked in BOTH directions, so
     a rename fails here instead of orphaning the declaration.

`--arms` reports the THREE arms and the length match. Arm C is the
length-matched control PA-01 added: as long as arm B in unique content, asking
for nothing architectural, so a difference between B and C is attributable to
what the prompt SAYS rather than to how much of it there is. It reports the
match as a measured number and probes arm C's unique content for architectural
vocabulary.

`--controls` runs the CONTROL-PROPERTY PROBE over every declared positive
control: is the mutant invisible until an accepted `reserve` executes? A
control that is observable after a refusal, or from construction, stays green
through exactly the regression it exists to catch. Measured at PA-01: arm A
HOLDS, **arm B BROKEN**, both references HOLD. It reports; a BROKEN verdict is
recorded and never converted into anything.

`--verify-suite` additionally runs the shared behavioral suite under every
mutant, **against the references only**, and compares the result with each
mutant's `predicted_suite` / `predicted_suite_real` / `predicted_suite_fake`
field. Since PA-01 that is three wirings of one suite: the flat reference, and
the ported reference through each side of its port. The last two differ only in
which adapter the composition point hands the domain, and that difference is
the only instrument here that reaches the fake at all.

All of it is fixture verification, not the eval: it measures this file's own
suite against this file's own references, and it touches no arm. It exists
because a catalogue whose annotations are wrong is worse than one with no
annotations.
"""

from __future__ import annotations

import argparse
import ast
import os
import re
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
    "adapter_internal": (
        "PA-01 -- a fault INSIDE an adapter implementation. BA-B14 measured this "
        "class surviving every instrument including the hand-written suite, and no "
        "catalogue before PA-01 could express it, because the only anchor tree had "
        "no adapter in it."
    ),
}

#: The minimum number of mutants seeded inside an adapter implementation. The
#: canonical plan's PA-01 acceptance says "at least two", and the two are not
#: interchangeable: PA-M11/PA-M12 are one semantic on both sides of one port,
#: so a single row could not measure the difference the pair exists to measure.
MIN_ADAPTER_INTERNAL = 2

#: Files that ARE adapter implementations, relative to the catalogue root. A
#: mutant claiming `fault_class = "adapter_internal"` must live in one, and a
#: mutant living in one must claim the class. Checked in BOTH directions, so
#: renaming an adapter fails here instead of silently orphaning the
#: declaration -- the plan's `declaration_executability_rule`.
ADAPTER_IMPLEMENTATIONS = (
    "reference_ports/journal_file.py",
    "reference_ports/journal_memory.py",
)

#: The mechanism gaps the plan names. Each must carry at least one mutant, and
#: the mutant's `gap_targeted` prose must mention the keyword.
REQUIRED_GAPS = {
    "enabled": "HP-03 -- a corpus replays only ENABLED edges, so it holds no refusal",
    "slice": "case modules -- a slice narrower than its view orphans the other aspect",
    "silent": "HP-05 -- a silent mapping has no durable-write oracle",
    "apply()-only": "HP-04 -- the oracle aborts on the first apply()-only adapter",
    "behind a port": (
        "PA-01 -- the region a port creates that no shared oracle reaches. BA-B14: "
        "'the port removes places for some faults to live and creates a region no "
        "shared oracle reaches.'"
    ),
}

#: The three arms. Arm C is PA-01's addition: the LENGTH-MATCHED control.
ARMS = ("arm_a", "arm_b", "arm_c")

#: `(directory, module, prediction key, label)` the shared behavioural suite is
#: pointed at. The point of the last two is that they are the SAME suite over
#: the SAME domain, differing only in which adapter the composition point hands
#: in. That difference is the only instrument in this file that reaches
#: `journal_memory.py` at all.
SUITE_WIRINGS = (
    ("reference", "quota_ledger", "predicted_suite", "flat reference -- no port"),
    ("reference_ports", "quota_ledger", "predicted_suite_real",
     "ported reference, REAL adapter"),
    ("reference_ports", "quota_ledger_fake", "predicted_suite_fake",
     "ported reference, FAKE adapter"),
)

#: Vocabulary arm C must not use. Arm C is the length-matched control: as long
#: as arm B in unique content, asking for NOTHING architectural. If it asks for
#: structure it is a second treatment, and the confound it exists to settle is
#: not settled.
#:
#: This is a VOCABULARY PROBE, not a semantic judgement, and its limits are
#: exactly what they look like: it cannot detect structural guidance phrased
#: without any of these words, and it does not fire on a path that merely
#: contains one (`reference_ports/` does not match ``\bports?\b``). It is run
#: over arm C's content that is NOT shared with arm A, because arm A is the
#: ordinary control and anything C shares with it is architecturally neutral by
#: construction. It reports; it refuses nothing in the product.
ARCHITECTURAL_VOCABULARY = (
    r"hexagonal", r"ports?", r"adapters?", r"layers?", r"boundar(?:y|ies)",
    r"modules?", r"interfaces?", r"coupl\w*", r"cohes\w*", r"decoupl\w*",
    r"dependenc\w*", r"inject\w*", r"abstract\w*", r"indirect\w*",
    r"encapsulat\w*", r"composition", r"architect\w*", r"refactor\w*",
    r"structur\w*", r"decompos\w*", r"separation of concerns",
    r"single responsibility", r"domains?", r"fakes?", r"mocks?", r"stubs?",
    r"seams?", r"protocols?", r"packages?", r"modular\w*", r"design\w*",
    r"class(?:es)?", r"file organi[sz]ation",
)

#: How far arm C's unique content may sit from arm B's before "matched" stops
#: being a true word. The measured number is reported either way; the tolerance
#: only decides whether it is ALSO reported as a problem.
LENGTH_MATCH_TOLERANCE = 0.10

#: THE CONTROL PROPERTY, stated as a testable sentence rather than as a hope.
#:
#: A positive control exists to go RED when the instrument stops reaching the
#: fault. The failure mode it is written against here is HP-06's: `Reserve`
#: stopping executing. So the control must be observable ONLY after an accepted
#: `reserve` -- if any observable differs before one runs, the control stays
#: green through exactly the regression it exists to catch.
#:
#: This was not a hypothetical. EVAL-RERUN's adversarial channel built a corpus
#: with every `Reserve` case deleted and ran it:
#:
#:     ARM A: corpus-noreserve  M07 = SURVIVED   <- control correctly goes RED
#:     ARM B: corpus-noreserve  M07 = KILLED     <- control stays green through it
#:
#: because arm B derives `available()`, so the nearest re-anchoring of M07's
#: semantic is wrong from construction, on every tenant, after a refusal. PA-01
#: turns that one-off adversarial finding into a probe anyone can re-run on any
#: tree in seconds (`--controls`), because the finding cost an adversarial
#: channel to produce and a rerun to confirm, and the next arm gets one for free.
CONTROL_PROPERTY = "accept-path-only"

#: A driver that exercises everything a case can do EXCEPT accept a reserve:
#: construction, every refusal, and one ACCEPTED `close_tenant`. If a mutated
#: tree's output differs from the clean tree's here, the mutant is observable
#: without the accept path.
NO_ACCEPTED_RESERVE_DRIVER = r'''
import importlib, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
ledger = importlib.import_module(sys.argv[2]).QuotaLedger(
    {"acme": 10, "globex": 4}, Path(sys.argv[3])
)
tenants = ("acme", "globex")
seen = []


def snapshot(tag):
    seen.append((
        tag,
        tuple(ledger.available(t) for t in tenants),
        tuple(ledger.committed(t) for t in tenants),
        tuple(ledger.is_closed(t) for t in tenants),
        tuple(ledger.outstanding_ids()),
        tuple(ledger.ledger_lines()),
    ))


snapshot("construction")
for call, args in (
    ("reserve", ("nobody", 1)), ("reserve", ("acme", 0)), ("reserve", ("acme", -2)),
    ("reserve", ("acme", 999)), ("commit", ("r99",)), ("release", ("r99",)),
    ("close_tenant", ("nobody",)),
):
    outcome = getattr(ledger, call)(*args)
    seen.append((f"{call}{args}", outcome.status, outcome.reason))
    snapshot(f"after {call}{args}")
# An ACCEPTED command that is not an accepted reserve. This is the one that
# caught arm B: its M07 was killed by CloseTenant cases on states with no live
# reservation at all.
outcome = ledger.close_tenant("globex")
seen.append(("close_tenant('globex')", outcome.status, outcome.reason))
snapshot("after accepted close_tenant")
print(repr(seen))
'''


_ARCHITECTURAL_RE = re.compile(
    r"\b(?:" + "|".join(ARCHITECTURAL_VOCABULARY) + r")\b", re.IGNORECASE
)


def arm_prompt(arm: str) -> Path:
    """The one place an arm's prompt path is built. Import this, do not join."""
    return HERE / arm / "PROMPT.md"


def distinct_lines(path: Path) -> set[str]:
    """THE unique-content measure, defined once and executable.

    Non-blank lines, whitespace-stripped, de-duplicated. Nothing cleverer, on
    purpose: this is exactly the measure that produced the predecessor's sealed
    "6.6x longer in unique content", so a number computed here is comparable
    with the number in that record rather than merely similar to it.
    """
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def unique_content(subject: Path, against: Path) -> set[str]:
    """Lines in `subject` that do not appear anywhere in `against`."""
    return distinct_lines(subject) - distinct_lines(against)


def architectural_hits(lines) -> list[tuple[str, str]]:
    """`(matched word, line)` for every line asking for something structural."""
    hits = []
    for line in sorted(lines):
        found = _ARCHITECTURAL_RE.search(line)
        if found:
            hits.append((found.group(0), line))
    return hits


def adapter_internal_rows(rows: list[dict]) -> list[dict]:
    """Rows seeded INSIDE an adapter implementation, by declared class."""
    return [row for row in rows if str(row.get("fault_class")) == "adapter_internal"]


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

    # (7) controls, counted PER ANCHOR TREE.
    #
    # PA-01 changed this from a single global count. The reason is the same one
    # that put a positive control in the catalogue at all: a column of
    # survivors on one anchor tree cannot be told apart from an instrument that
    # never ran that tree. With two anchor trees, one global control leaves the
    # second tree with no such witness. Negative controls stay global -- there
    # is one, it is about the model's use of sets, and it is not a per-tree
    # property.
    negatives = [row for row in rows if str(row.get("control_role", "")).startswith("negative")]
    if not negatives:
        problems.append("expected at least 1 negative control")

    trees: dict[str, list[dict]] = {}
    for row in rows:
        trees.setdefault(str(row.get("path", "")).split("/")[0] or "<none>", []).append(row)
    positives_total = 0
    for tree in sorted(trees):
        positives = [
            row for row in trees[tree]
            if str(row.get("control_role", "")).startswith("positive")
        ]
        positives_total += len(positives)
        if len(positives) != 1:
            problems.append(
                f"anchor tree {tree!r} has {len(positives)} positive control(s), expected "
                f"exactly 1. Without one, a column of survivors on that tree cannot be "
                f"told apart from an instrument that never ran it."
            )

    # (8) PA-01: faults seeded INSIDE an adapter implementation.
    #
    # Checked in BOTH directions. A row that claims the class must live in a
    # declared adapter, and a row living in a declared adapter must claim the
    # class -- so renaming or moving an adapter fails here instead of leaving
    # the declaration pointing at nothing. Five declaration/behaviour
    # mismatches in five consecutive attempts by three authors is why.
    declared = set(ADAPTER_IMPLEMENTATIONS)
    claimed = adapter_internal_rows(rows)
    for row in claimed:
        if str(row.get("path")) not in declared:
            problems.append(
                f"{row.get('id')}: declares fault_class 'adapter_internal' but its path "
                f"{row.get('path')!r} is not one of ADAPTER_IMPLEMENTATIONS. A fault in "
                f"the domain relabelled as adapter-internal would report the class as "
                f"covered while measuring the class that was already covered."
            )
    for row in rows:
        if str(row.get("path")) in declared and row not in claimed:
            problems.append(
                f"{row.get('id')}: is seeded in the adapter implementation "
                f"{row.get('path')!r} but does not declare fault_class "
                f"'adapter_internal'. The class row would under-count."
            )
    for adapter in ADAPTER_IMPLEMENTATIONS:
        if not (root / adapter).is_file():
            problems.append(
                f"declared adapter implementation {adapter!r} does not exist under {root}. "
                f"The declaration has been orphaned by a rename."
            )
    if len(claimed) < MIN_ADAPTER_INTERNAL:
        problems.append(
            f"{len(claimed)} adapter-internal mutant(s); the plan's PA-01 acceptance "
            f"requires at least {MIN_ADAPTER_INTERNAL}."
        )
    sides = {str(row.get("path")) for row in claimed}
    if len(sides) < 2:
        problems.append(
            "every adapter-internal mutant is in the same file. The pair exists to seed "
            "ONE semantic on BOTH sides of one port; rows all on one side measure the "
            "difficulty of a fault rather than the size of the region."
        )

    print("class coverage:")
    for name in sorted(by_class):
        marker = "" if name in REQUIRED_CLASSES else "   (not a required class)"
        print(f"  {name:<20} {len(by_class[name])}  {', '.join(by_class[name])}{marker}")
    print(f"\ncontrols: {positives_total} positive ({len(trees)} anchor tree(s)), "
          f"{len(negatives)} negative")
    print(f"adapter-internal mutants: {len(claimed)} across {len(sides)} adapter file(s)")
    for row in claimed:
        print(f"  {str(row.get('id')):<42} {row.get('path')}")
    return problems


def check_arms() -> list[str]:
    """Report the THREE arms and the length match. Reports; does not refuse.

    PA-01 added arm C, and with it the measurement the predecessor could not
    make. Its own record: arm B's prompt was 6.6x longer in unique content than
    arm A's, so "hexagonal helped" was never separable from "a longer ask
    helped". Arm C is as long as arm B in unique content and asks for nothing
    architectural, so a difference between B and C is attributable to what the
    prompt SAYS. If arm C matches arm B, the finding is that longer prompts
    produce better structure -- a legitimate outcome this arm exists to be able
    to produce.
    """
    problems: list[str] = []
    paths = {arm: arm_prompt(arm) for arm in ARMS}

    print("\narms:")
    for arm, path in paths.items():
        if not path.is_file():
            problems.append(f"missing arm prompt {path}")
            return problems
        raw = path.read_text(encoding="utf-8")
        print(
            f"  {path.relative_to(REPO_ROOT)}  "
            f"({len(raw.splitlines())} lines, {len(distinct_lines(path))} distinct)"
        )

    lines = {arm: distinct_lines(path) for arm, path in paths.items()}

    # "No arm is another with a section removed" -- i.e. no subsets.
    for one in ARMS:
        for other in ARMS:
            if one != other and lines[one] <= lines[other]:
                problems.append(
                    f"{one}'s content is a strict subset of {other}'s: {one} IS {other} "
                    f"with a section removed. Declare the arms as independent prompts."
                )

    print(f"\n  shared by all three: {len(lines['arm_a'] & lines['arm_b'] & lines['arm_c'])} "
          f"lines (the controlled envelope)")
    print("\n  UNIQUE CONTENT -- distinct non-blank stripped lines in the row's arm")
    print("  that appear nowhere in the column's arm:\n")
    print(f"  {'':<10}" + "".join(f"{'vs ' + a:>12}" for a in ARMS))
    for one in ARMS:
        row = "".join(
            f"{'--':>12}" if one == other else f"{len(lines[one] - lines[other]):>12}"
            for other in ARMS
        )
        print(f"  {one:<10}{row}")

    # The measurement PA-01 exists to report, against the SAME control arm.
    b_unique = len(lines["arm_b"] - lines["arm_a"])
    c_unique = len(lines["arm_c"] - lines["arm_a"])
    a_unique = len(lines["arm_a"] - lines["arm_b"])
    ratio = c_unique / b_unique if b_unique else float("inf")
    print(
        f"\n  LENGTH MATCH, measured against arm A as the common control:\n"
        f"    arm B unique vs arm A: {b_unique} lines"
        f"   ({b_unique / a_unique:.2f}x arm A's {a_unique} -- the predecessor's 6.6x)\n"
        f"    arm C unique vs arm A: {c_unique} lines\n"
        f"    arm C / arm B:         {ratio:.3f}  ({(ratio - 1) * 100:+.1f}%), "
        f"tolerance +/-{LENGTH_MATCH_TOLERANCE * 100:.0f}%"
    )
    if abs(ratio - 1) > LENGTH_MATCH_TOLERANCE:
        problems.append(
            f"arm C's unique content is {(ratio - 1) * 100:+.1f}% of arm B's, outside the "
            f"declared +/-{LENGTH_MATCH_TOLERANCE * 100:.0f}% tolerance. A control that is "
            f"not length-matched does not separate 'hexagonal helped' from 'longer helped'."
        )

    # Arm C asks for nothing architectural. Probed over the content arm C does
    # NOT share with arm A, because arm A is the ordinary control.
    c_only = lines["arm_c"] - lines["arm_a"]
    hits = architectural_hits(c_only)
    b_only = lines["arm_b"] - lines["arm_a"]
    b_hits = architectural_hits(b_only)
    print(
        f"\n  ARCHITECTURAL VOCABULARY in content not shared with arm A:\n"
        f"    arm B: {len(b_hits)} of {len(b_only)} unique lines\n"
        f"    arm C: {len(hits)} of {len(c_only)} unique lines"
    )
    for word, line in hits:
        print(f"      [{word}] {line}")
    if hits:
        problems.append(
            f"arm C's unique content uses architectural vocabulary on {len(hits)} line(s). "
            f"Arm C is the length-matched control; if it asks for structure it is a second "
            f"treatment and the confound is not settled."
        )
    print(
        "    (A vocabulary probe, not a semantic judgement. It cannot detect\n"
        "     structural guidance phrased without any of these words.)"
    )

    body = paths["arm_b"].read_text(encoding="utf-8")
    if "HP-02-SLOT:BEGIN" not in body or "HP-02-SLOT:END" not in body:
        problems.append("arm B has no HP-02 slot markers")
    elif "UNFILLED" in body:
        print(
            "\n  ARM B SLOT: **UNFILLED** -- HP-02 owns it. Arm B must not be\n"
            "  dispatched in this state. Reported, not refused: nothing here gates."
        )
    else:
        print("\n  ARM B SLOT: filled.")

    body_c = paths["arm_c"].read_text(encoding="utf-8")
    if "PA-01-SLOT:BEGIN" not in body_c or "PA-01-SLOT:END" not in body_c:
        problems.append("arm C has no PA-01 slot markers")
    else:
        print("  ARM C SLOT: filled.")
    return problems


def verify_suite(catalogue: Path, root: Path) -> list[str]:
    """Run the shared suite under every mutant, on the REFERENCES ONLY.

    Three wirings, one suite file, one set of assertions. The flat reference is
    HP-01's, unchanged. The two ported wirings differ only in which adapter the
    composition point hands the domain -- and that difference is the whole of
    PA-01's instrument: it is the only thing here that executes a line of
    `journal_memory.py`.

    Still fixture verification, not the eval. It measures this file's own suite
    against this file's own references and touches no arm.
    """
    mutants, rows, _ = load_catalogue(catalogue)
    suite = HERE / "tests" / "test_behavior.py"
    problems: list[str] = []
    table: dict[str, dict[str, str]] = {}

    def run(impl_dir: Path, module: str) -> bool:
        env = dict(os.environ, QUOTA_LEDGER_DIR=str(impl_dir), QUOTA_LEDGER_IMPL=module)
        done = subprocess.run(
            ["uv", "run", "--with", "pytest", "python", "-m", "pytest", str(suite), "-q"],
            cwd=REPO_ROOT, env=env, capture_output=True, text=True,
        )
        return done.returncode == 0

    print("\nsuite verification (references only -- NOT an arm measurement):")
    for tree, module, key, label in SUITE_WIRINGS:
        source = root / tree
        if not source.is_dir():
            problems.append(f"no anchor tree at {source}")
            continue
        print(f"\n  === {label}   [{tree}, QUOTA_LEDGER_IMPL={module}] ===")
        with tempfile.TemporaryDirectory() as tmp:
            workdir = Path(tmp) / tree
            shutil.copytree(source, workdir)
            pristine = {
                path.relative_to(workdir).as_posix(): path.read_text(encoding="utf-8")
                for path in workdir.rglob("*.py")
            }

            # The control run. Without it, a "kill" may predate every mutant.
            if not run(workdir, module):
                problems.append(
                    f"CONTROL RUN FAILED for {label}: the suite is red on the unmutated "
                    f"tree. Every kill in this column would be that same unrelated failure."
                )
                print("  control (no mutant): suite RED -- column void")
                continue
            print("  control (no mutant): suite GREEN\n")

            for mutant, row in zip(mutants, rows):
                if not mutant.path.startswith(f"{tree}/"):
                    continue
                relative = mutant.path[len(tree) + 1:]
                target = workdir / relative
                original = pristine[relative]
                try:
                    target.write_text(
                        original.replace(mutant.find, mutant.replace, 1), encoding="utf-8"
                    )
                    killed = not run(workdir, module)
                finally:
                    target.write_text(original, encoding="utf-8")
                observed = "KILLED" if killed else "SURVIVED"
                table.setdefault(mutant.id, {})[key] = observed
                predicted = str(row.get(key, ""))
                if not predicted:
                    print(f"  {mutant.id:<42} {observed:<9} (no {key} annotation)")
                    continue
                agrees = predicted.upper().startswith(observed[:6].upper())
                print(
                    f"  {mutant.id:<42} {observed:<9} "
                    f"{'agrees' if agrees else '*** DISAGREES ***'}"
                )
                if not agrees:
                    print(f"      {key}: {predicted}")

    # The one comparison PA-01 exists to make, printed as a table rather than
    # as prose, because the difference between two cells is the finding and a
    # count that merged them would hide it (HP-06-DF-06).
    pair = [row for row in table if row.startswith(("PA-M11", "PA-M12", "PA-M13"))]
    if pair:
        print("\n  THE PORT'S BLIND REGION, one semantic on both sides of one port:\n")
        print(f"  {'mutant':<42} {'suite-real':<12} {'suite-fake':<12}")
        for name in sorted(pair):
            cells = table[name]
            print(
                f"  {name:<42} {cells.get('predicted_suite_real', '-'):<12} "
                f"{cells.get('predicted_suite_fake', '-'):<12}"
            )
        print(
            "\n  Read the DIFFERENCE between the rows, never a total. PA-M11 and PA-M12\n"
            "  are the same fault; if one dies and the other lives, the gap is the size\n"
            "  of the region the port creates, measured in one cell."
        )

    print(
        "\n  A disagreement is not a failure of this harness -- it is the catalogue's\n"
        "  annotation being wrong, and it must be corrected BEFORE dispatch or\n"
        "  recorded as a finding after it."
    )
    return problems


def probe_control_property(
    tree: Path, module: str, relative: str, find: str, replace: str
) -> tuple[str, str]:
    """Is this mutant invisible until an accepted `reserve` runs?

    Returns ``("HOLDS" | "BROKEN" | "ERROR", detail)``. HOLDS means the tree
    behaves identically with and without the mutant across construction, every
    refusal, and one accepted `close_tenant` -- so the only way to observe it is
    to execute an accepted `reserve`, which is exactly what a positive control
    for this instrument has to require.
    """

    def drive(work: Path, ledger_path: Path) -> str:
        done = subprocess.run(
            [sys.executable, "-c", NO_ACCEPTED_RESERVE_DRIVER,
             str(work), module, str(ledger_path)],
            capture_output=True, text=True,
        )
        if done.returncode:
            tail = done.stderr.strip().splitlines()
            return "ERROR:" + (tail[-1] if tail else "no output")
        return done.stdout.strip()

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "tree"
        shutil.copytree(tree, work)
        ledger_path = Path(tmp) / "ledger.txt"
        clean = drive(work, ledger_path)
        target = work / relative
        if not target.is_file():
            return "ERROR", f"no {relative} under {tree}"
        source = target.read_text(encoding="utf-8")
        occurrences = source.count(find)
        if occurrences != 1:
            return "ERROR", f"`find` occurs {occurrences} time(s) in {relative}"
        target.write_text(source.replace(find, replace, 1), encoding="utf-8")
        dirty = drive(work, ledger_path)

    if clean.startswith("ERROR") or dirty.startswith("ERROR"):
        return "ERROR", f"clean={clean[:90]} dirty={dirty[:90]}"
    if clean != dirty:
        return "BROKEN", (
            "an observable differs with ZERO accepted reserves, so this control "
            "stays green through the very regression it exists to catch"
        )
    return "HOLDS", "invisible until an accepted reserve executes"


def check_controls(
    catalogue: Path, root: Path, module: str, tree_root: bool = False
) -> list[str]:
    """Run the control-property probe over every declared positive control.

    Reports. It does not refuse a promotion, it does not gate the product, and
    a BROKEN verdict is recorded rather than converted into anything. A control
    that could excuse itself would be the defect EVAL-SUPPRESS found.
    """
    problems: list[str] = []
    _, rows, _ = load_catalogue(catalogue)
    positives = [
        row for row in rows
        if str(row.get("control_role", "")).startswith("positive")
    ]

    # The property is declared in a SIDE TABLE, not on the mutant rows. M07 is
    # a sealed HP-01 row and PA-01 does not amend sealed rows -- not even to add
    # a field. The declaration is PA-01's, so it lives in PA-01's table and says
    # which mutant it is about.
    try:
        import tomllib
    except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
        import tomli as tomllib  # type: ignore[no-redef]
    declared_properties = tomllib.loads(
        catalogue.read_text(encoding="utf-8")
    ).get("pa_control_properties", {})

    print(f"\ncontrol-property probe -- property: {CONTROL_PROPERTY!r}")
    print("  A positive control must be INVISIBLE until an accepted `reserve`")
    print("  runs. Otherwise it stays green through 'Reserve stopped executing',")
    print("  which is the regression it is the control for.\n")
    print(f"  {'control':<46} {'tree':<18} verdict")
    print("  " + "-" * 84)

    for row in positives:
        relative = str(row.get("path", ""))
        # Two shapes of catalogue reach here, and they are NOT distinguishable
        # by looking at the filesystem -- arm B's `quota_ledger/domain.py` has a
        # first segment that is a real directory, and so does this file's
        # `reference/quota_ledger.py`. Guessing would put the wrong directory on
        # `sys.path` and report ERROR for a control that is fine. So the caller
        # says which, with `--tree-root`, and PA-06 uses it for every arm.
        if tree_root:
            tree_name, tree, inner = root.name, root, relative
        else:
            head = relative.split("/")[0]
            tree_name, tree, inner = head, root / head, relative[len(head) + 1:]
        verdict, detail = probe_control_property(
            tree, module, inner, str(row["find"]), str(row["replace"])
        )
        print(f"  {str(row['id']):<46} {tree_name:<18} {verdict}")
        print(f"  {'':<46} {'':<18} {detail}")
        if verdict == "BROKEN":
            problems.append(
                f"{row['id']}: declared a positive control but does NOT hold the "
                f"{CONTROL_PROPERTY!r} property on {tree_name} -- {detail}"
            )
        elif verdict == "ERROR":
            problems.append(f"{row['id']}: probe could not run on {tree_name} -- {detail}")

        declared = str(declared_properties.get(str(row["id"]), ""))
        if declared != CONTROL_PROPERTY:
            problems.append(
                f"{row['id']}: `[pa_control_properties]` does not declare it as "
                f"{CONTROL_PROPERTY!r}. The property is the whole job; a control "
                f"that does not state it cannot be checked against it, and an "
                f"undeclared control is how a role string gets copied."
            )

    # Copied role strings are how a control stops being about the thing it
    # guards. EVAL-RERUN-DF-03: arm B's catalogue carried arm A's role string
    # over a mutant arm B's own data contradicted.
    roles: dict[str, list[str]] = {}
    for row in positives:
        roles.setdefault(str(row.get("control_role", "")), []).append(str(row["id"]))
    for role, ids in roles.items():
        if len(ids) > 1:
            problems.append(
                f"positive controls {', '.join(ids)} share a `control_role` string "
                f"verbatim. A role string copied from another control is how a "
                f"control stops being about the thing it guards (EVAL-RERUN-DF-03); "
                f"write each one for the tree it is on. Shared text: {role[:70]!r}"
            )
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalogue", type=Path, default=HERE / "seeded_faults.toml")
    parser.add_argument("--root", type=Path, default=HERE,
                        help="tree the mutant paths are relative to (an arm tree at HP-06)")
    parser.add_argument("--arms", action="store_true", help="report the three arm prompts")
    parser.add_argument("--verify-suite", action="store_true",
                        help="run the shared suite under every mutant, references only")
    parser.add_argument("--controls", action="store_true",
                        help="probe every positive control for the accept-path property")
    parser.add_argument("--impl", default="quota_ledger",
                        help="module the probe imports QuotaLedger from (an arm may differ)")
    parser.add_argument("--tree-root", action="store_true",
                        help="--root IS the tree; catalogue paths are relative to it (per-arm)")
    args = parser.parse_args()

    problems = check_integrity(args.catalogue.resolve(), args.root.resolve())
    if args.arms:
        problems += check_arms()
    if args.controls:
        problems += check_controls(
            args.catalogue.resolve(), args.root.resolve(), args.impl, args.tree_root
        )
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
