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
    python3 examples/validation/ab/check_catalogue.py --demonstrate \\
        --catalogue examples/validation/ab/probe_demonstrations.toml

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
control, and **since FI-01 it runs BOTH HALVES of the property**: the mutant
must be invisible until the path it is the control for executes, AND observable
once one does, in the number of steps the instruments actually run, moving at
least one observable inside the region its property declares.

Before FI-01 only the first half existed. `PA-06-DF-07` demonstrated what that
was worth: a mutant whose `replace` was **the identical line plus a comment**,
declared `control_role = "positive"`, was reported `HOLDS`. A probe that returns
HOLDS for a no-op is not a probe. The same one-sidedness hid that `PA-M14` is
unobservable in ONE STEP on three of the four trees it is declared on, while
every generated corpus case is single-action -- so its RED on those trees was a
property of the control and not of the instrument.

`--demonstrate` is the other half of `architecture_advice.md` **S2**, and it is
the reason to believe anything `--controls` prints: it runs the probe against
`probe_demonstrations.toml`, a catalogue of controls that are BROKEN ON PURPOSE,
each declaring the verdict the probe must return for it. The command passes only
if the probe reports every one of them broken. It is re-runnable, it takes
seconds, and if a future change makes the probe soft it fails there.

It reports; a BROKEN / INERT / OUT_OF_REGION verdict is recorded and never
converted into anything. **R2: a control that cannot be made to work is reported
RED, never made green by weakening what it asserts.**

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

#: THE PORT'S DERIVED REGION, taken from the generator rather than restated.
#:
#: `tla_spec_dev.py generate cases ... --port-cases only` prints, for this
#: fixture's one declared port::
#:
#:     ledger.LedgerAppendPort: 1855 case(s); region {closed, committed, ledger}
#:
#: A port case narrows its expected `after` to that region. So a fault whose
#: symptom lands ANYWHERE ELSE cannot be decided by a port-scoped instrument, no
#: matter how blatant it is -- which is `PA-03-DF-03` and `PA-04-DF-01` in one
#: sentence, and why `M07` and `PA-M14` both SURVIVE `corpus-port` while it is
#: executing hundreds of cases.
#:
#: `ledger` is spelled `ledger_lines` here because that is what the driver below
#: calls; the other two names are the generator's own.
PORT_REGION = ("closed", "committed", "ledger_lines")

#: The observables the probe compares. Everything the feature exposes; nothing
#: derived, nothing sampled.
OBSERVABLES = ("available", "committed", "closed", "outstanding", "ledger_lines")

#: ONE driver, four scripted plans, so that "invisible before" and "observable
#: after" are measured by the same instrument on the same projection.
#:
#: The plans are named for what they DO, not for what they prove:
#:
#:   refusals-and-accepted-close       construction, every refusal, and one
#:                                     ACCEPTED `close_tenant`. No accepted
#:                                     `reserve`. (This is PA-01's original
#:                                     driver, unchanged in what it executes.)
#:   one-accepted-reserve              construction and exactly one accepted
#:                                     `reserve`. The step count matters: EVERY
#:                                     GENERATED CORPUS CASE IS SINGLE-ACTION,
#:                                     so a control that needs two steps cannot
#:                                     be killed by any corpus (PA-06-DF-07 a).
#:   everything-but-an-accepted-commit construction, every refusal, an accepted
#:                                     reserve, an accepted release, a second
#:                                     accepted reserve and an accepted
#:                                     `close_tenant`. No accepted `commit`.
#:   one-accepted-commit               construction, one accepted reserve and
#:                                     the `commit` that follows it.
PROBE_DRIVER = r'''
import importlib, json, sys
from pathlib import Path

sys.path.insert(0, sys.argv[1])
QuotaLedger = importlib.import_module(sys.argv[2]).QuotaLedger
plan = sys.argv[4]
ledger = QuotaLedger({"acme": 10, "globex": 4}, Path(sys.argv[3]))
TENANTS = ("acme", "globex")
trace = []


def snapshot(tag):
    trace.append({
        "tag": tag,
        "available": [ledger.available(t) for t in TENANTS],
        "committed": [ledger.committed(t) for t in TENANTS],
        "closed": [ledger.is_closed(t) for t in TENANTS],
        "outstanding": [str(entry) for entry in ledger.outstanding_ids()],
        "ledger_lines": [str(entry) for entry in ledger.ledger_lines()],
    })


def call(name, *args):
    outcome = getattr(ledger, name)(*args)
    trace.append({
        "tag": "call " + name + repr(args),
        "status": [outcome.status, outcome.reason],
    })
    snapshot("after " + name + repr(args))
    return outcome


REFUSALS = (
    ("reserve", ("nobody", 1)), ("reserve", ("acme", 0)), ("reserve", ("acme", -2)),
    ("reserve", ("acme", 999)), ("commit", ("r99",)), ("release", ("r99",)),
    ("close_tenant", ("nobody",)),
)

snapshot("construction")
if plan == "refusals-and-accepted-close":
    for name, args in REFUSALS:
        call(name, *args)
    # An ACCEPTED command that is not an accepted reserve. This is the one that
    # caught arm B: its M07 was killed by CloseTenant cases on states with no
    # live reservation at all.
    call("close_tenant", "globex")
elif plan == "one-accepted-reserve":
    call("reserve", "acme", 3)
elif plan == "everything-but-an-accepted-commit":
    for name, args in REFUSALS:
        call(name, *args)
    first = call("reserve", "acme", 3)
    call("release", first.reservation_id)
    call("reserve", "acme", 2)
    call("close_tenant", "globex")
elif plan == "one-accepted-commit":
    first = call("reserve", "acme", 3)
    call("commit", first.reservation_id)
else:
    raise SystemExit("unknown plan " + plan)
print(json.dumps(trace, sort_keys=True))
'''


class ControlProperty:
    """A control property with BOTH halves, because one half passes a no-op.

    `PA-06-DF-07 (b)`: `--controls` tested only "invisible BEFORE an accepted
    reserve" and nothing tested "visible WITH one", so a mutant whose `replace`
    was THE IDENTICAL LINE PLUS A COMMENT was reported `HOLDS`. A probe that
    returns `HOLDS` for a no-op is not a probe, and every `HOLDS` it ever
    printed was worth nothing as evidence that a control works.

    So a property carries three things and all three are executed:

      `absent`   the plan that must show NO difference. Failing it means the
                 control is observable without the path it is the control for,
                 and therefore stays green through exactly the regression it
                 exists to catch.
      `present`  the plan that MUST show a difference, in the number of steps
                 the instruments actually execute. Failing it means the control
                 is INERT here -- the no-op case, and also `PA-M14` on every
                 tree that stores `available` rather than deriving it.
      `region`   observables at least one of which must move, or `()` for no
                 region requirement. This is what "seeded inside a port's
                 region" means executably.

    REGION IS AN INCLUSION TEST, NEVER A CONFINEMENT TEST, and that is a
    deliberate reading of `PA-06-DF-07`. Confinement is representation-
    dependent: arm B derives `available()` from `committed`, so a fault on
    `committed` moves `available` there and moves nothing else on a tree that
    stores it. A property that demanded confinement would report the same
    control HOLDS on one arm and BROKEN on another for a reason that is about
    the arm's data structures rather than about the control. What the probe DOES
    do with the extra observables is report them: the full moved set is printed
    beside every verdict, so a reader sees confinement or its absence as a
    measurement.
    """

    def __init__(self, name: str, absent: str, present: str,
                 region: tuple[str, ...], prose: str) -> None:
        self.name = name
        self.absent = absent
        self.present = present
        self.region = region
        self.prose = prose


#: Every property a catalogue may declare in `[pa_control_properties]`. A
#: property named there and absent here is reported, not guessed at.
CONTROL_PROPERTIES: dict[str, ControlProperty] = {
    "accept-path-only": ControlProperty(
        name="accept-path-only",
        absent="refusals-and-accepted-close",
        present="one-accepted-reserve",
        region=(),
        prose=(
            "invisible until an accepted `reserve` executes, and observable "
            "immediately after ONE. No region requirement: this property is "
            "about the ACCEPT PATH, and `available` is outside every declared "
            "port region on this fixture -- which is why a control holding it "
            "can still be undecidable by a port-scoped instrument."
        ),
    ),
    "port-region-commit-path": ControlProperty(
        name="port-region-commit-path",
        absent="everything-but-an-accepted-commit",
        present="one-accepted-commit",
        region=PORT_REGION,
        prose=(
            "invisible until an accepted `commit` executes, observable "
            "immediately after ONE, and moving at least one observable INSIDE "
            "the declared port region {closed, committed, ledger}. This is the "
            "property `PA-03-DF-03` and `PA-04-DF-01` asked for and no control "
            "had: a fault a PORT-SCOPED instrument can decide."
        ),
    ),
}


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
    #
    # FI-01 CHANGED "exactly 1" TO "at least 1", AND THE CHANGE IS A
    # STRENGTHENING RATHER THAN A RELAXATION -- read it with the rule
    # `--controls` now enforces, which is that at least one positive control per
    # tree must HOLD ITS PROPERTY when probed. "Exactly one" served nothing on
    # its own: one BROKEN control satisfied it, which is precisely the state
    # `PA-06-DF-07` found and R2 calls worse than having none. What a tree needs
    # is a control that can go red, and it needs the broken one kept beside it,
    # still declared, still probed, still reported -- not deleted to keep a
    # count at one. `reference_ports` now carries two: `PA-M14`, which is
    # measured INERT here and stays in the record saying so, and `FI-M15`, which
    # holds.
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
        if len(positives) < 1:
            problems.append(
                f"anchor tree {tree!r} has {len(positives)} positive control(s), expected "
                f"at least 1. Without one, a column of survivors on that tree cannot be "
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


def moved_observables(clean: str, dirty: str) -> list[str]:
    """Which observables differ between two traces. Reported, never inferred."""
    import json  # noqa: PLC0415 -- local, so the module stays import-light

    left, right = json.loads(clean), json.loads(dirty)
    if len(left) != len(right):
        return ["<trace length>"] + sorted(OBSERVABLES)
    moved: set[str] = set()
    for one, other in zip(left, right):
        if one.get("tag") != other.get("tag"):
            moved.add("<trace shape>")
        if one.get("status") != other.get("status"):
            moved.add("status")
        for name in OBSERVABLES:
            if one.get(name) != other.get(name):
                moved.add(name)
    return sorted(moved)


def probe_control_property(
    tree: Path, module: str, relative: str, find: str, replace: str,
    property_name: str = CONTROL_PROPERTY,
) -> tuple[str, str]:
    """Does this mutant hold BOTH halves of its declared control property?

    Returns ``(verdict, detail)`` where verdict is one of:

      ``HOLDS``          invisible under the property's `absent` plan AND
                         observable under its `present` plan, moving at least
                         one observable inside the declared region.
      ``BROKEN``         observable under the `absent` plan. The control stays
                         green through the regression it exists to catch.
      ``INERT``          invisible under the `present` plan too. NOTHING CAN
                         EVER SEE IT, so it can never go red and it is not a
                         control at all. A no-op lands here, and so does a
                         control that needs two steps on a tree where every
                         generated case is single-action.
      ``OUT_OF_REGION``  observable, but nothing it moves is inside the region
                         the property declares. A port-scoped instrument
                         projects only its region, so it cannot decide this.
      ``ERROR``          the probe could not run.

    Before FI-01 only the first half existed, and a mutant whose `replace` was
    the identical line plus a comment was reported ``HOLDS`` (`PA-06-DF-07 b`).
    """
    prop = CONTROL_PROPERTIES.get(property_name)
    if prop is None:
        return "ERROR", (
            f"undeclared control property {property_name!r}; known: "
            f"{', '.join(sorted(CONTROL_PROPERTIES))}"
        )

    def drive(work: Path, ledger_path: Path, plan: str) -> str:
        done = subprocess.run(
            [sys.executable, "-c", PROBE_DRIVER,
             str(work), module, str(ledger_path), plan],
            capture_output=True, text=True,
        )
        if done.returncode:
            tail = done.stderr.strip().splitlines()
            return "ERROR:" + (tail[-1] if tail else "no output")
        return done.stdout.strip()

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "tree"
        shutil.copytree(tree, work)
        target = work / relative
        if not target.is_file():
            return "ERROR", f"no {relative} under {tree}"
        source = target.read_text(encoding="utf-8")
        occurrences = source.count(find)
        if occurrences != 1:
            return "ERROR", f"`find` occurs {occurrences} time(s) in {relative}"

        traces: dict[str, str] = {}
        for state in ("clean", "dirty"):
            if state == "dirty":
                target.write_text(source.replace(find, replace, 1), encoding="utf-8")
            for plan in (prop.absent, prop.present):
                # A fresh ledger file per run: the file adapter TRUNCATES at
                # construction, so sharing one would make the second plan read
                # the first plan's leftovers on some trees and not on others.
                traces[f"{state}/{plan}"] = drive(
                    work, Path(tmp) / f"ledger-{state}-{plan}.txt", plan
                )

    broken = {key: value for key, value in traces.items() if value.startswith("ERROR")}
    if broken:
        first = sorted(broken)[0]
        return "ERROR", f"{first}: {broken[first][:120]}"

    if traces[f"clean/{prop.absent}"] != traces[f"dirty/{prop.absent}"]:
        moved = moved_observables(
            traces[f"clean/{prop.absent}"], traces[f"dirty/{prop.absent}"]
        )
        return "BROKEN", (
            f"observable under {prop.absent!r}, which executes none of the path "
            f"this control is the control FOR; it stays green through exactly "
            f"the regression it exists to catch. moved: {', '.join(moved)}"
        )

    if traces[f"clean/{prop.present}"] == traces[f"dirty/{prop.present}"]:
        return "INERT", (
            f"NOTHING MOVES under {prop.present!r} either. A control nothing can "
            f"observe can never go red; this is the verdict a no-op earns, and "
            f"the verdict a control earns when it needs more steps than the "
            f"instruments execute"
        )

    moved = moved_observables(
        traces[f"clean/{prop.present}"], traces[f"dirty/{prop.present}"]
    )
    inside = [name for name in moved if name in prop.region]
    if prop.region and not inside:
        return "OUT_OF_REGION", (
            f"observable under {prop.present!r} but only outside the declared "
            f"region {{{', '.join(prop.region)}}}. moved: {', '.join(moved)}. A "
            f"port-scoped instrument projects only its region, so it cannot "
            f"decide this control"
        )

    return "HOLDS", (
        f"invisible under {prop.absent!r}; observable under {prop.present!r}; "
        f"moved: {', '.join(moved)}"
        + (f"; inside the region: {', '.join(inside)}" if prop.region else "")
    )


def _toml():
    try:
        import tomllib  # noqa: PLC0415
    except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
        import tomli as tomllib  # type: ignore[no-redef]  # noqa: PLC0415
    return tomllib


def resolve_control_properties(catalogue: Path) -> tuple[dict[str, str], list[str]]:
    """`[pa_control_properties]`, THROUGH `extends`. Returns `(table, problems)`.

    `PA-06-DF-02`: `extends` was documentation. Every per-arm catalogue carries
    `extends = "examples/validation/ab/seeded_faults.toml"`, and this function's
    predecessor read the property table only out of the file it was handed -- so
    a re-anchored control whose parent DOES declare it was reported undeclared,
    and PA-06 worked around it by copying the table into each of its three
    re-anchoring files. Five copies of one property and nothing checking them
    against each other is the `declaration_executability_rule`'s own failure
    shape, produced by the fix for a declaration nothing executed.

    One level is followed, which covers every catalogue that exists. A child's
    entry wins over its parent's, so a re-anchoring may state a DIFFERENT
    property for a tree it has measured -- what it may no longer do is have to
    restate the same one.

    `extends` may carry a `<path> @ <rev>` form (`pa_m14_prerepair.toml` does),
    which names a parent AS OF a commit. The path half is resolved; the revision
    is not checked out and is reported as unfollowed rather than as a defect.
    """
    tomllib = _toml()
    problems: list[str] = []
    document = tomllib.loads(catalogue.read_text(encoding="utf-8"))
    child = {
        str(key): str(value)
        for key, value in document.get("pa_control_properties", {}).items()
    }

    declared = str(document.get("catalogue", {}).get("extends", "")).strip()
    if not declared:
        return child, problems

    path_part, _, revision = declared.partition("@")
    parent_path = REPO_ROOT / path_part.strip()
    if not parent_path.is_file():
        problems.append(
            f"`extends` names {path_part.strip()!r}, which does not exist. An "
            f"inherited declaration that resolves to nothing is the drift the "
            f"`declaration_executability_rule` is about."
        )
        return child, problems

    inherited = {
        str(key): str(value)
        for key, value in tomllib.loads(
            parent_path.read_text(encoding="utf-8")
        ).get("pa_control_properties", {}).items()
    }
    merged = dict(inherited)
    merged.update(child)
    note = f"  extends: {path_part.strip()} -- {len(inherited)} inherited property/ies"
    if revision.strip():
        note += f" (revision {revision.strip()!r} is NOT checked out; the path is)"
    print(note)
    return merged, problems


def check_controls(
    catalogue: Path, root: Path, module: str, tree_root: bool = False
) -> list[str]:
    """Run the control-property probe over every declared positive control.

    Reports. It does not refuse a promotion, it does not gate the product, and
    a BROKEN / INERT / OUT_OF_REGION verdict is recorded rather than converted
    into anything. A control that could excuse itself would be the defect
    EVAL-SUPPRESS found; a control that CANNOT go red is the defect R2 names,
    and this is where it is caught.
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
    # which mutant it is about. Since FI-01 the table is read THROUGH `extends`.
    declared_properties, inherit_problems = resolve_control_properties(catalogue)
    problems += inherit_problems

    print("\ncontrol-property probe -- BOTH halves, since FI-01")
    print("  A positive control must be INVISIBLE until the path it is the")
    print("  control for executes, AND OBSERVABLE once one does, in the number")
    print("  of steps the instruments actually run. Before FI-01 only the first")
    print("  half was tested and a NO-OP reported HOLDS (PA-06-DF-07).\n")
    for name, prop in sorted(CONTROL_PROPERTIES.items()):
        print(f"    {name:<26} {prop.prose}")
    print(f"\n  {'control':<46} {'tree':<18} verdict")
    print("  " + "-" * 84)

    verdicts: dict[str, tuple[str, str]] = {}
    trees_seen: dict[str, list[str]] = {}
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

        declared = str(declared_properties.get(str(row["id"]), ""))
        if declared not in CONTROL_PROPERTIES:
            problems.append(
                f"{row['id']}: `[pa_control_properties]` declares {declared!r}, "
                f"which is not one of {sorted(CONTROL_PROPERTIES)}. The property "
                f"is the whole job; a control that does not state one cannot be "
                f"checked against it, and an undeclared control is how a role "
                f"string gets copied."
            )
            verdicts[str(row["id"])] = ("ERROR", "no declared property")
            trees_seen.setdefault(tree_name, []).append(str(row["id"]))
            print(f"  {str(row['id']):<46} {tree_name:<18} NO DECLARED PROPERTY")
            continue

        verdict, detail = probe_control_property(
            tree, module, inner, str(row["find"]), str(row["replace"]), declared
        )
        verdicts[str(row["id"])] = (verdict, detail)
        trees_seen.setdefault(tree_name, []).append(str(row["id"]))
        print(f"  {str(row['id']):<46} {tree_name:<18} {verdict}   [{declared}]")
        print(f"  {'':<46} {'':<18} {detail}")
        if verdict == "ERROR":
            problems.append(f"{row['id']}: probe could not run on {tree_name} -- {detail}")
        elif verdict != "HOLDS":
            problems.append(
                f"{row['id']}: declared a positive control but is {verdict} on "
                f"{tree_name} under the {declared!r} property -- {detail}. R2: it is "
                f"reported RED, not made green by weakening what it asserts."
            )

    # R2, per tree. A tree whose every positive control is broken has NO working
    # control, and a column of survivors on it cannot be told apart from an
    # instrument that never ran it. That is worse than having none, because the
    # broken one reads like one.
    for tree_name, ids in sorted(trees_seen.items()):
        holding = [name for name in ids if verdicts.get(name, ("", ""))[0] == "HOLDS"]
        if not holding:
            problems.append(
                f"tree {tree_name!r} has {len(ids)} declared positive control(s) and "
                f"NOT ONE holds its property: {', '.join(ids)}. Every kill number "
                f"measured on this tree is a FLOOR under a red control."
            )
        else:
            print(f"\n  {tree_name}: {len(holding)} of {len(ids)} positive control(s) HOLD "
                  f"({', '.join(holding)})")

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


def demonstrate_probe_failure(
    catalogue: Path, root: Path, module: str, tree_root: bool = False
) -> list[str]:
    """R1: THE PROBE'S OWN DEMONSTRATED FAILING INPUT, re-runnable.

    `architecture_advice.md` S2 -- "every criterion must have a demonstrated
    failing input and a demonstrated passing input" -- applied to the criterion
    itself. Each row of the demonstration catalogue is a DELIBERATELY BROKEN
    control that declares, in `probe_must_report`, the verdict the probe has to
    return for it. If the probe returns anything else -- above all if it returns
    `HOLDS` -- this exits nonzero and says which row it went soft on.

    The rows are broken in the ways that have actually happened, not in invented
    ways: a no-op (`PA-06-DF-07 b`, measured), a control observable from
    construction (arm B's `M07`, measured), and a control whose symptom lands
    outside the port's region (`PA-03-DF-03`, measured on `M07` and `PA-M14`).
    """
    problems: list[str] = []
    _, rows, _ = load_catalogue(catalogue)
    declared_properties, inherit_problems = resolve_control_properties(catalogue)
    problems += inherit_problems

    print("\nDEMONSTRATED FAILING INPUTS for the control-property probe (R1).")
    print("  Every row below is a control that is BROKEN ON PURPOSE. The probe")
    print("  passes this demonstration only by REPORTING each one broken.\n")
    print(f"  {'demonstration':<40} {'declared':<28} {'must report':<15} observed")
    print("  " + "-" * 104)

    for row in rows:
        expected = str(row.get("probe_must_report", "")).strip()
        if not expected:
            problems.append(
                f"{row.get('id')}: a demonstration row with no `probe_must_report`. "
                f"A demonstration that does not say what it demonstrates cannot fail."
            )
            continue
        relative = str(row.get("path", ""))
        if tree_root:
            tree, inner = root, relative
        else:
            head = relative.split("/")[0]
            tree, inner = root / head, relative[len(head) + 1:]
        declared = str(declared_properties.get(str(row["id"]), ""))
        verdict, detail = probe_control_property(
            tree, module, inner, str(row["find"]), str(row["replace"]), declared
        )
        agrees = verdict == expected
        print(f"  {str(row['id']):<40} {declared:<28} {expected:<15} "
              f"{verdict}{'' if agrees else '   *** THE PROBE WENT SOFT ***'}")
        print(f"  {'':<40} {detail}")
        if not agrees:
            problems.append(
                f"{row['id']}: the probe reported {verdict!r} where the "
                f"demonstration requires {expected!r}. "
                + (
                    "A probe that returns HOLDS for a control that cannot fail is "
                    "not a probe, and every HOLDS it has ever printed is void."
                    if verdict == "HOLDS"
                    else f"detail: {detail}"
                )
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
    parser.add_argument("--demonstrate", action="store_true",
                        help="R1: run the probe's own demonstrated FAILING inputs")
    args = parser.parse_args()

    if args.demonstrate:
        # The demonstration catalogue is not a measurement catalogue: it holds
        # broken controls only, so the class/gap/adapter assertions would report
        # a dozen absences that are the point rather than defects.
        problems = demonstrate_probe_failure(
            args.catalogue.resolve(), args.root.resolve(), args.impl, args.tree_root
        )
        print()
        if problems:
            print("THE PROBE FAILED ITS OWN DEMONSTRATION -- it does not go red on a")
            print("control that is broken, so no HOLDS it prints is evidence:")
            for line in problems:
                print(f"  {line}")
            return 1
        print("The probe reported every deliberately broken control broken. R1 holds:")
        print("this instrument ships with a demonstrated failing input.")
        return 0

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
