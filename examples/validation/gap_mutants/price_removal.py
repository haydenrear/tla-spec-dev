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

EXTINCT: A FAULT WHOSE HABITAT WAS DELETED IS NOT A FAULT THAT SURVIVED A CUT
=============================================================================

`CL-02`. `RM-05` withdrew the previous epic's headline and the reason is in this
file. **For every fault all of whose killing nodes lie inside a file the removal
deletes, `ENTAILED-SURVIVES` follows from `git show` alone, with nothing run and
no other verdict reachable.** The round's own control -- `is_control` true,
`removed_by` `"nothing"`, `gap` `"NONE, on purpose"` -- returned the headline
verdict from the same arithmetic, and that row was missing from the four-row
output the report printed as three. **So the verdict carried no information
about the removal.**

The distinction the verdict was missing is one this repository had already
written down and never computed. `residual_faults.toml`'s `[[not_seedable]]`
row says it in words:

    The fault class is EXTINCT, not UNWATCHED, and an extinct fault class costs
    nothing in the currency a gap mutant measures. What that removal DID cost is
    a CAPABILITY, NOT A DETECTION, and no gap mutant of any posture measures
    capability.

`EXTINCT` computes that. A fault is extinct at a removal's head when **the
removal deleted the fault's own habitat** -- every file the mutant must edit in
order to exist is gone -- so there is no post-removal artifact the fault could
be seeded into. `ENTAILED-SURVIVES` says *a detection was taken away*.
`EXTINCT` says *there is nothing left to detect*, and it is **not** a price.

**HABITAT IS READ FROM THE EDIT OPS, NOT FROM THE PATH LIST, AND THAT IS THE
WHOLE CARE IN IT.** `SM-GM-I3-an-instrument-that-was-never-added-to-the-registry`
edits `scripts/gap_probe_instrument.py` with `op = "add_file"`, and that path is
absent at `bf0fb29` **because the mutant creates it**. Absence there is the
fault's PRECONDITION, not its extinction. A rule that read "any declared path
missing at head" would have called `SM-GM-I3` extinct and made `SM-03`'s removal
look cheaper than it is. Only an edit that requires the file to already exist
(`replace`, `append`, ...) declares habitat; a mutant whose every edit is
`add_file` carries its own habitat and can never be `EXTINCT`.

BOUND ON `EXTINCT`, stated rather than left to be found
-------------------------------------------------------

It is file-granular, exactly as shallow as `node_present`. **A mechanism that was
RENAMED rather than deleted reads `EXTINCT` here and is not extinct** -- the
fault class may be perfectly expressible in the file that replaced it. `EXTINCT`
is therefore an upper bound on extinction, in the same way `ENTAILED-SURVIVES`
is an upper bound on the price, and it is reported as **a refusal to price, not
as a zero**: an extinct fault is one this instrument declines to measure, and
the capability the removal may have cost is measured by nothing here.

DECLARED CONTROLS ARE NOT PRICEABLE ROWS
========================================

A row that declares `is_control` -- or `removed_by = "nothing"`, which says the
removal is not on its causal path at all -- **cannot appear as a priced result**.
`CONTROL-EXCLUDED` is its verdict in every mode, and `is_priced_result` is false
for it by construction.

**The row is still PRINTED.** RM-05's finding was not that a control was scored;
it was that the control's row went *missing from the output*, so nobody saw the
verdict repeat. Dropping control rows to keep the table tidy would reproduce that
failure exactly. They are shown, in their own block, outside every denominator.

`--head` IS VALIDATED, BECAUSE AN UNRESOLVABLE ONE PRICED EVERYTHING
====================================================================

`node_present` answers `False` when `git show <head>:<path>` fails, and it failed
identically for *a path this removal deleted* and for *a head that does not name
a commit*. So a typo'd, truncated or unfetched `--head` made every killing node
look deleted and returned `ENTAILED-SURVIVES` for every fault in the table, **at
exit 0** (`RM-05`, §2). `resolve_head` now resolves the ref before any verdict is
computed and raises `HeadNotResolvable`; the CLI exits 2 and prints no table. The
demonstrated failing input is `--head deadbeefdeadbeef` over the sealed RM-03
before-table, which used to print four `ENTAILED-SURVIVES` rows.

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
# the vocabulary, named so a renderer and a test cannot drift from it
# --------------------------------------------------------------------------

NOT_IN_TABLE = "NOT-IN-TABLE"
CONTROL_EXCLUDED = "CONTROL-EXCLUDED"
EXTINCT = "EXTINCT"
NO_KILL_TO_LOSE = "NO-KILL-TO-LOSE"
ENTAILED_SURVIVES = "ENTAILED-SURVIVES"
UNDECIDED = "UNDECIDED"
PRICED = "PRICED"
FREE = "FREE"

#: The two verdicts that assert a removal took a detection away. Everything a
#: reader would quote as "this removal cost something" is in here, and nothing
#: else is. `CL-02`: a declared control must never reach this set, and neither
#: must a fault whose habitat the removal deleted.
PRICED_VERDICTS = frozenset({PRICED, ENTAILED_SURVIVES})

#: Edit ops that CREATE the file they name. A mutant made only of these carries
#: its own habitat, so a missing path is its precondition and never its
#: extinction -- `SM-GM-I3`, which is why this set exists.
OPS_THAT_CREATE_THEIR_HABITAT = frozenset({"add_file", "create", "new_file"})


def is_priced_result(row: dict[str, Any]) -> bool:
    """Would a reader quote this row as a removal having cost a detection?"""
    return row.get("verdict") in PRICED_VERDICTS


class HeadNotResolvable(RuntimeError):
    """`--head` did not name a commit in this repository.

    Raised BEFORE any verdict is computed. Left unraised, this condition made
    `git show <head>:<path>` fail for every path, which reads as "every killing
    node was deleted", which returns `ENTAILED-SURVIVES` for the whole table at
    exit 0 (`RM-05` §2).
    """


_RESOLVED: dict[str, str] = {}


def resolve_head(head: str) -> str:
    """The full sha `head` names, or `HeadNotResolvable`. Never a silent False."""
    if head in _RESOLVED:
        return _RESOLVED[head]
    done = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{head}^{{commit}}"],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    sha = done.stdout.strip()
    if done.returncode != 0 or not sha:
        raise HeadNotResolvable(
            f"--head {head!r} does not name a commit in {REPO_ROOT}. Refusing to "
            "compute a verdict: an unresolvable head makes every killing node "
            "look deleted and prices the whole table."
        )
    _RESOLVED[head] = sha
    return sha


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


def declared_control(record: dict[str, Any]) -> str | None:
    """Why this row is a control, or `None` if it is a subject.

    Read from the row's OWN DECLARATIONS in the sealed table -- never inferred
    from its verdicts, which is what would let a result decide the exclusion.

      `is_control`    the seeding author said so
      `removed_by`    `"nothing"` -- the removal is not on this row's causal
                      path, so it cannot be priced against it whatever it does
      `control_role`  a written role; a row with one is a control that lost its
                      flag, and `RM-05` is about a control nobody noticed

    All four controls in the sealed record (`SM-GM-CTRL-A`, `SM-GM-CTRL-B`,
    `RM-01-RF-CTRL`, `RM03-GM-CTRL-C`) declare the first two together.
    """
    if record.get("is_control"):
        return "declared is_control"
    if (record.get("removed_by") or "").strip().lower() == "nothing":
        return "removed_by is 'nothing' -- the removal is not on its causal path"
    role = record.get("control_role")
    if isinstance(role, str) and role.strip():
        return "carries a control_role"
    return None


def habitat(record: dict[str, Any]) -> list[str]:
    """The paths this fault needs to ALREADY EXIST in order to be seeded.

    An `add_file` edit creates what it names, so it declares no habitat: its
    path being absent is the fault's precondition. `SM-GM-I3` is exactly that
    row and a path-list reading would have called it extinct.
    """
    return sorted({
        edit["path"]
        for edit in (record.get("edits") or [])
        if edit.get("path")
        and (edit.get("op") or "replace") not in OPS_THAT_CREATE_THEIR_HABITAT
    })


def extinct_at(record: dict[str, Any], head: str | None) -> tuple[bool, list[str]]:
    """Did the removal delete every file this fault needed in order to exist?

    Returns `(extinct, the habitat that was read)`. `False` with no head, and
    `False` for a mutant that declares no habitat at all -- both mean the
    question was not answerable, never that the answer was no.
    """
    sites = habitat(record)
    if head is None or not sites:
        return False, sites
    return all(_show(head, path) is None for path in sites), sites


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
    """The price of a removal for one fault, read from both measured tables.

    `CL-02`: a declared control is `CONTROL-EXCLUDED` here too. The exclusion is
    a property of the ROW, not of the mode it is read in -- a control that could
    be priced by `price` while `entail` refused it would be the same defect with
    one more step in front of it.
    """
    if head is not None:
        resolve_head(head)
    b_record = before["per_mutant"].get(mutant_id)
    a_record = after["per_mutant"].get(mutant_id)
    if b_record is None or a_record is None:
        missing = "before" if b_record is None else "after"
        return {"mutant": mutant_id, "verdict": NOT_IN_TABLE, "why": f"absent from the {missing} table"}

    control = declared_control(b_record)
    if control is not None:
        return {
            "mutant": mutant_id,
            "verdict": CONTROL_EXCLUDED,
            "control_reason": control,
            "why": "a declared control is not a priced result in any mode",
        }

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
        row["verdict"] = NO_KILL_TO_LOSE
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
        row["verdict"] = FREE
        row["why"] = "something still catches it after the cut; the detection was redundant"
        return row

    row["verdict"] = PRICED
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

    FIVE VERDICTS, AND ONLY ONE OF THEM IS A PRICE:

      CONTROL-EXCLUDED    a declared control. Never priced, always printed.
      EXTINCT             the removal deleted this fault's habitat. There is no
                          post-removal artifact it could be seeded into, so
                          there is nothing left to detect and nothing to price.
                          NOT a zero -- a refusal to measure. Bounded: a
                          mechanism RENAMED rather than deleted reads EXTINCT.
      NO-KILL-TO-LOSE     nothing caught it before; the cut cannot cost anything
      ENTAILED-SURVIVES   no killing (detector, node) survives the cut. The
                          removal took every kill this fault had. SOUND -- and
                          bounded: it cannot see a kill the after tree ADDED.
      UNDECIDED           some killing (detector, node) survives by name. That
                          is NOT `entailed DIES`: the survivor may have been
                          weakened, and only running the fault can tell.

    THE ORDER IS THE ARGUMENT. `EXTINCT` is a fact about the SUBJECT and it
    strictly dominates every fact about DETECTION: if the fault cannot exist
    after the cut, then "everything that caught it is gone" is true and vacuous.
    That vacuous truth is what `RM-03` published as the first priced removal.

    The shipped `removal_census.discriminating` returns `NON-DISCRIMINATING`
    for `UNDECIDED` with the reason *"DIES after the cut was entailed before
    the cut was made"*. That is the unsound step this function refuses to take.
    """
    if head is not None:
        resolve_head(head)
    record = before["per_mutant"].get(mutant_id)
    if record is None:
        return {"mutant": mutant_id, "verdict": NOT_IN_TABLE}

    control = declared_control(record)
    if control is not None:
        return {
            "mutant": mutant_id,
            "verdict": CONTROL_EXCLUDED,
            "control_reason": control,
            "why": (
                "a declared control is not a priced result in any mode. It is shown "
                "and not scored: RM-05's finding was that a control's row went MISSING "
                "from the output, so nobody saw it return the headline verdict."
            ),
        }

    kills, undecided = kill_set(record)
    row: dict[str, Any] = {
        "mutant": mutant_id,
        "kills_before": sorted(f"{d}::{n}" for d, n in kills),
        "undecidable_columns_before": undecided,
    }

    gone, sites = extinct_at(record, head)
    row["habitat"] = sites
    if not sites:
        row["habitat_note"] = (
            "this row declares no habitat, so extinction was not asked"
            if head else "no --head, so extinction was not asked"
        )
    elif head is None:
        row["habitat_note"] = "no --head, so extinction was not asked"
    if gone:
        row["verdict"] = EXTINCT
        row["why"] = (
            "the removal deleted every file this fault needed in order to exist, so "
            "there is no post-removal artifact it could be seeded into. NOT A PRICE "
            "and not a zero: an extinct fault class costs nothing in the currency a "
            "gap mutant measures, and what a removal like this DOES cost is a "
            "CAPABILITY, which nothing here measures. Bound: file-granular -- a "
            "mechanism RENAMED rather than deleted reads EXTINCT and is not extinct."
        )
        return row

    if not kills:
        row["verdict"] = NO_KILL_TO_LOSE
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
        row["verdict"] = UNDECIDED
        row["why"] = (
            "a killing node still exists at the head of the removal. It may or may not "
            "still catch this fault -- a node can keep its id and lose its body. Running "
            "the fault is the only thing that decides it."
        )
    else:
        row["verdict"] = ENTAILED_SURVIVES
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
    if measured == CONTROL_EXCLUDED:
        # A control is not a prediction the classifier is answerable for.
        return True
    if shipped == NO_KILL_TO_LOSE:
        return measured == NO_KILL_TO_LOSE
    if shipped == "NON-DISCRIMINATING":  # it predicts DIES after the cut
        return measured == FREE
    if shipped == "DISCRIMINATING":      # it predicts the re-run could say something
        return measured in (PRICED, FREE)
    return measured == NOT_IN_TABLE


# --------------------------------------------------------------------------
# rendering and main
# --------------------------------------------------------------------------


def _render_control_block(rows: list[dict[str, Any]]) -> list[str]:
    """Controls, PRINTED and outside every denominator.

    `RM-05`'s finding was a control row missing from the output, not a control
    row being scored. A tidier table that dropped these would repeat it.
    """
    controls = [r for r in rows if r["verdict"] == CONTROL_EXCLUDED]
    if not controls:
        return []
    out = ["", "DECLARED CONTROLS -- shown, never priced, in no denominator:"]
    for row in controls:
        out.append(f"    {CONTROL_EXCLUDED}  {row['mutant']}")
        out.append(f"        {row.get('control_reason', '')}")
    return out


def render_price(rows: list[dict[str, Any]]) -> str:
    out = ["THE PRICE, READ FROM THE KILL SET", ""]
    subjects = [r for r in rows if r["verdict"] != CONTROL_EXCLUDED]
    for row in subjects:
        out.append(f"{row['verdict']:<16} {row['mutant']}")
        if row.get("why"):
            out.append(f"                 {row['why']}")
        for lost in row.get("lost_kills", []):
            out.append(f"    lost kill   [{lost['reason']}] {lost['detector']} :: {lost['node']}")
        for column in row.get("undecidable_columns_after", []):
            out.append(f"    UNDECIDABLE column after the cut, read as neither: {column}")
    out += _render_control_block(rows)
    priced = [r for r in subjects if r["verdict"] == PRICED]
    # `denominator_rule`: the denominator is SUBJECTS, and it says so. A control
    # leaving it lowers the denominator without lowering any numerator, which is
    # the direction that makes a price look LARGER -- so the excluded count is
    # printed beside it rather than absorbed.
    out += ["", f"{len(priced)} of {len(subjects)} fault(s) PRICED -- a fault the repository "
                f"used to catch and no longer catches.",
            f"denominator: {len(subjects)} subject(s); "
            f"{len(rows) - len(subjects)} declared control(s) excluded from it."]
    return "\n".join(out)


def render_entail(rows: list[dict[str, Any]], head: str | None) -> str:
    """The before-only reading, with the two things `RM-03`'s output lacked:
    every row present, and a statement of what the denominator is."""
    out = ["WHAT THE BEFORE-TABLE ALONE ENTAILS", ""]
    subjects = [r for r in rows if r["verdict"] != CONTROL_EXCLUDED]
    for row in subjects:
        out.append(f"{row['verdict']:<19} {row['mutant']}")
        if row.get("why"):
            out.append(f"                    {row['why']}")
        if row["verdict"] == EXTINCT:
            for path in row.get("habitat", []):
                out.append(f"    habitat deleted by this removal: {path}")
    out += _render_control_block(rows)
    entailed = [r for r in subjects if r["verdict"] == ENTAILED_SURVIVES]
    extinct = [r for r in subjects if r["verdict"] == EXTINCT]
    if head is None:
        out += ["", "NOTE: no --head. Node survivorship and EXTINCT were BOTH unasked; "
                    "this table is the weakest reading the instrument has."]
    out += ["", f"{len(entailed)} of {len(subjects)} subject(s) ENTAILED-SURVIVES; "
                f"{len(extinct)} EXTINCT (not a price); "
                f"{len(rows) - len(subjects)} declared control(s) excluded."]
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

    # `--head` FIRST, AND BEFORE A SINGLE VERDICT. An unresolvable head used to
    # make every killing node look deleted and price the whole table at exit 0.
    if args.head is not None:
        try:
            resolve_head(args.head)
        except HeadNotResolvable as bad:
            print(f"error: {bad}", file=sys.stderr)
            return 2

    if args.command == "entail":
        rows = [entail(before, m, deleted, args.head) for m in subjects]
        print(render_entail(rows, args.head))
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
