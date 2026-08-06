#!/usr/bin/env python3
"""Gap mutants: price a removal BEFORE it happens, and again after.

    python3 examples/validation/gap_mutants/run_gap_mutants.py \\
        --cases <scratch>/specs/corpus-port/spec-unit/quota_port \\
        --out specs/results/scorecards/subtract-to-measure/before-state/gap-mutants.json

WHY THIS FILE EXISTS -- `removal_is_a_delta_rule`
--------------------------------------------------

`MF-020` says a number can fall because an edge was **deleted**. Applied to
ourselves: **removing an instrument removes the ability to detect that the
removal was harmful.** If `SM-02` cuts the `[ports.*]` binding machinery and
`SM-03` cuts the hollow instrument rows and every number afterwards looks fine,
we cannot tell whether the cut things were noise or whether we cut exactly the
things that would have objected.

So each mechanism slated for removal gets a **fault seeded in the gap it claims
to cover**, measured against every detector that exists *now*. After the cut,
`SM-05` re-runs this same file. Each mutant then either

  * still **DIES** -- the mechanism was **redundant** and the cut was free, or
  * now **SURVIVES** -- the mechanism was **load-bearing**, and we have just
    priced it in the only currency that means anything.

**Both outcomes are results.** A removal with no mutant in its gap is not a
measurement, and a mechanism with no seedable gap is **reported** (see
`[[not_seedable]]` in the catalogue) rather than dropped from the table.

WHAT IT IS NOT
--------------

**Not a gate.** Nothing in this repository invokes it, no close path consults
it, and its exit code refuses nothing about the design. It exits non-zero for
exactly one reason: a declared mutant could not be **applied** (its anchor was
missing, ambiguous, or a no-op), because an unapplied mutant reported as
`SURVIVES` is the `FI-01-DF-01` failure -- fifteen false survivals with no
error -- wearing this epic's clothes.

**Not a verdict about the removal.** It reports what each detector did. Whether
a `SURVIVES` is an acceptable price is `SM-05`'s call and a human's, not this
file's.

THREE INHERITED DEFECTS ARE WIRED INTO THE VERDICT RULE
--------------------------------------------------------

* **`FI-01-DF-01`** -- a purge that leaves modules cached reports SURVIVED with
  no error. Every detector here runs in a **subprocess** against a **freshly
  staged tree**, and `__pycache__` is swept between applications.

* **`FI-02-DF-02`** -- `run_port_swap.py` prints a red control and **exits 0**.
  Nothing here reads an exit code from it; `control_red` and
  `unmutated_control_failed` are read out of its JSON, and a column whose
  control is red is reported `CONTROL_RED`, never `SURVIVES`.

* **A `SURVIVES` with nothing executed is not a survival.** Every detector
  reports how many tests/cases it actually ran. Zero executed is `INERT`, which
  decides nothing, because `expect_exit = 0` is satisfied by a *fully skipped*
  run -- which is the `FI-06` finding this epic was opened on, and it applies to
  this file as much as to the registry.

THE BASELINE IS A SET OF FAILURES, NOT AN EXIT CODE
----------------------------------------------------

The staged tree is produced with `git archive`, which has no `.git`, so the
handful of tests that read git history fail there **for that reason alone**.
Rather than hide them, every detector is run once on the **pristine** staged
tree and its failing node ids are recorded. A mutant `DIES` only when it
produces failures the pristine tree did not have. The pre-existing failures are
written into the artifact, named, so a reader can see exactly what was excused
and why.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
DEFAULT_CATALOGUE = HERE / "gap_mutants.toml"

#: Verdict vocabulary. Kept as constants so a typo is an AttributeError rather
#: than a cell that silently means nothing.
DIES = "DIES"
SURVIVES = "SURVIVES"
INERT = "INERT"
CONTROL_RED = "CONTROL_RED"
REMOVED = "REMOVED"
NOT_RUN = "NOT_RUN"

#: pytest's own summary line. `passed`, `failed`, `errors`, `skipped`,
#: `deselected`, `xfailed`, `xpassed` are all counted so that "nothing ran" is
#: distinguishable from "everything passed".
_SUMMARY = re.compile(r"(\d+) (passed|failed|error|errors|skipped|deselected|xfailed|xpassed)")
_FAILED_NODE = re.compile(r"^(?:FAILED|ERROR) (\S+)", re.MULTILINE)


# --------------------------------------------------------------------------
# staging
# --------------------------------------------------------------------------


def stage_tree(ref: str, dest: Path) -> None:
    """Materialise `ref`'s tree at `dest`. No `.git`; see the module docstring."""
    dest.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(
        ["git", "archive", ref], cwd=str(REPO_ROOT), stdout=subprocess.PIPE, check=True
    )
    subprocess.run(["tar", "-x", "-C", str(dest)], input=archive.stdout, check=True)


def sweep_pycache(tree: Path) -> None:
    for cache in tree.rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)


class MutantNotApplied(RuntimeError):
    """A declared mutant's anchor was missing, ambiguous, or a no-op."""


def apply_mutant(tree: Path, mutant: dict[str, Any]) -> dict[str, Any]:
    """Apply every edit in `mutant`, returning what to restore afterwards.

    Refuses -- loudly -- on anything that would make the mutant a no-op. An
    unapplied mutant that reports SURVIVES is worse than no mutant at all,
    because it reads as evidence that nothing was lost.
    """
    undo: list[tuple[Path, str | None]] = []
    applied: list[dict[str, Any]] = []
    for edit in mutant.get("edit", []):
        target = tree / edit["path"]
        if "add_file" in edit:
            if target.exists():
                raise MutantNotApplied(
                    f"{mutant['id']}: add_file target {edit['path']} already exists"
                )
            undo.append((target, None))
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(edit["add_file"], encoding="utf-8")
            applied.append({"path": edit["path"], "op": "add_file"})
            continue
        if not target.is_file():
            raise MutantNotApplied(f"{mutant['id']}: {edit['path']} is not a file in the tree")
        original = target.read_text(encoding="utf-8")
        undo.append((target, original))
        if "append" in edit:
            target.write_text(original + edit["append"], encoding="utf-8")
            applied.append({"path": edit["path"], "op": "append"})
            continue
        occurrences = original.count(edit["find"])
        if occurrences != 1:
            raise MutantNotApplied(
                f"{mutant['id']}: anchor occurs {occurrences} times in {edit['path']}, want 1"
            )
        mutated = original.replace(edit["find"], edit["replace"], 1)
        if mutated == original:
            raise MutantNotApplied(f"{mutant['id']}: edit to {edit['path']} changed nothing")
        target.write_text(mutated, encoding="utf-8")
        applied.append({"path": edit["path"], "op": "replace", "occurrences_of_find": occurrences})
    sweep_pycache(tree)
    return {"undo": undo, "applied": applied}


def restore(state: dict[str, Any], tree: Path) -> None:
    for target, original in reversed(state["undo"]):
        if original is None:
            target.unlink(missing_ok=True)
        else:
            target.write_text(original, encoding="utf-8")
    sweep_pycache(tree)


# --------------------------------------------------------------------------
# detectors
# --------------------------------------------------------------------------


def expand(token: str, tree: Path, cases: Path | None = None) -> str:
    token = token.replace("{tree}", str(tree)).replace("{python}", sys.executable)
    return token.replace("{cases}", str(cases) if cases else "{cases}")


def run_detector(
    detector: dict[str, Any],
    tree: Path,
    extra_args: list[str],
    cases: Path | None = None,
) -> dict[str, Any]:
    """Run one detector against `tree` and report what it did, not what it meant."""
    entry = detector.get("entry_point")
    if entry and not (tree / entry).exists():
        # The mechanism this detector IS was removed. That is a fact about the
        # tree, never a survival: a detector that no longer exists cannot be
        # said to have failed to catch anything.
        return {"present": False, "executed": 0, "red": None, "failing_nodes": [], "tail": []}

    environment = dict(os.environ)
    for key, value in (detector.get("env") or {}).items():
        environment[key] = expand(str(value), tree, cases)
    environment.pop("PYTHONDONTWRITEBYTECODE", None)

    if detector["kind"] == "pytest":
        argv = ["uv", "run", "--with", "pytest", "--with", "pyyaml", "python", "-m", "pytest", "-q"]
        argv += [expand(node, tree, cases) for node in detector["nodes"]] + extra_args
    elif detector["kind"] == "cli":
        argv = [expand(token, tree, cases) for token in detector["argv"]] + extra_args
    else:
        raise ValueError(f"unknown detector kind {detector['kind']!r}")

    completed = subprocess.run(
        argv,
        cwd=str(tree / detector.get("cwd", ".")),
        env=environment,
        capture_output=True,
        text=True,
        timeout=detector.get("timeout", 3600),
    )
    blob = completed.stdout + completed.stderr
    counts: dict[str, int] = {}
    for number, word in _SUMMARY.findall(blob):
        counts[word] = counts.get(word, 0) + int(number)
    executed = counts.get("passed", 0) + counts.get("failed", 0) + counts.get("error", 0)
    executed += counts.get("errors", 0) + counts.get("xfailed", 0) + counts.get("xpassed", 0)

    if detector["kind"] == "cli":
        # A CLI detector executed if it produced output at all; where a real
        # count is available the detector declares how to read it.
        executed = 1 if blob.strip() else 0
        marker = detector.get("executed_if_stdout_contains")
        if marker:
            executed = 1 if any(m in blob for m in marker) else 0

    markers = detector.get("red_if_stdout_contains")
    if markers:
        red = any(marker in blob for marker in markers)
    else:
        red = completed.returncode != 0

    return {
        "present": True,
        "argv": argv,
        "exit": completed.returncode,
        "executed": executed,
        "counts": counts,
        "red": red,
        "failing_nodes": sorted(
            {node.split("/tree/")[-1] for node in _FAILED_NODE.findall(blob)}
        ),
        "tail": [line for line in blob.splitlines() if line.strip()][-4:],
    }


#: Nodes that go red because THIS RUNNER mutated the tree, not because the
#: repository detected the fault. `tests/test_gap_mutants.py::
#: test_every_mutant_anchor_occurs_exactly_once_in_the_shipped_tree` reads the
#: catalogue's anchors out of the tree it is running in, and during a
#: measurement that tree is the mutated one -- so it fires on every mutant, for
#: every mutant, and would credit the repository with a kill it did not make.
#:
#: THE INSTRUMENT WAS DETECTING ITSELF. Found by reading the first run's raw
#: `new_failing_nodes` rather than its verdicts: five of the nine mutants had
#: this node and nothing else in their pytest-full kill set. It is excluded from
#: the verdict and REPORTED in `self_detected_nodes` on every cell, never
#: silently dropped -- an exclusion nobody can see is indistinguishable from a
#: number that was tuned.
SELF_DETECTION = ("tests/test_gap_mutants.py::"
                  "test_every_mutant_anchor_occurs_exactly_once_in_the_shipped_tree",)


def new_failures(baseline: dict[str, Any], observed: dict[str, Any]) -> tuple[list[str], list[str]]:
    """(failures the repository found, failures this runner caused itself)."""
    fresh = set(observed["failing_nodes"]) - set(baseline.get("failing_nodes", []))
    mine = sorted(node for node in fresh if node in SELF_DETECTION)
    return sorted(fresh - set(mine)), mine


def verdict(baseline: dict[str, Any], observed: dict[str, Any]) -> str:
    if not observed["present"]:
        return REMOVED
    if observed["executed"] == 0:
        return INERT
    real, _ = new_failures(baseline, observed)
    if real:
        return DIES
    if observed["red"] and not baseline.get("red"):
        # A red exit with no NEW node named is only a kill if the baseline was
        # green; a suite already red for git-history reasons decides nothing.
        return DIES
    return SURVIVES


# --------------------------------------------------------------------------
# the ports family: driven through the SHIPPED port-swap instrument
# --------------------------------------------------------------------------


def run_ports_family(
    mutants: list[dict[str, Any]], cases: Path, workdir: Path
) -> dict[str, dict[str, Any]]:
    """Measure the ports gap mutants with `run_port_swap.py`, DATA SWAP ONLY.

    The same move `examples/validation/ab/eval/run_arm_swap.py` makes: import
    the shipped driver and replace one DATA field -- the catalogue -- so the
    verdict rule, the control accounting and the executable counts are the ones
    that were sealed, not a second implementation of them. Two verdict-table
    drivers is how a number gets quoted against the wrong instrument
    (`PA-04-DF-02`); there is still only one.

    Every reading here comes out of the driver's JSON. Its exit code is
    deliberately not consulted: `FI-02-DF-02` -- it prints a red control and
    returns 0.
    """
    measure = REPO_ROOT / (
        "specs/results/scorecards/ports-as-adapters/GOAL-port-reach/measure"
    )
    driver = measure / "run_port_swap.py"
    rows = [m for m in mutants if m.get("port_swap_path")]
    if not rows:
        return {}
    if not driver.exists():
        return {m["id"]: {"driver_present": False} for m in rows}

    # The shipped driver reports its catalogues as `path.relative_to(REPO_ROOT)`,
    # so the derived file has to live inside the repository. It is written into
    # a throwaway directory beside this runner and removed in `finally`; nothing
    # reads it afterwards and it is never committed.
    scratch = Path(tempfile.mkdtemp(prefix=".sm01-ports-", dir=HERE))
    catalogue = scratch / "gap_mutants_ports.toml"
    blocks = ["# DERIVED at run time from gap_mutants.toml. Do not edit.\n"]
    for mutant in rows:
        edit = mutant["edit"][0]
        blocks.append(
            "[[mutants]]\n"
            f"id = {json.dumps(mutant['id'])}\n"
            'fault_class = "gap_mutant"\n'
            f"gap_targeted = {json.dumps(mutant['gap'])}\n"
            f"path = {json.dumps(mutant['port_swap_path'])}\n"
            f"find = {json.dumps(edit['find'])}\n"
            f"replace = {json.dumps(edit['replace'])}\n"
            f"description = {json.dumps(mutant['claims_to_catch'])}\n"
        )
    catalogue.write_text("\n".join(blocks), encoding="utf-8")

    out = workdir / "ports-swap.json"
    sys.path.insert(0, str(measure))
    import run_port_swap  # noqa: E402  (path must be set first)

    run_port_swap.SUBJECTS["reference_ports"]["catalogues"] = [catalogue]
    argv = sys.argv
    sys.argv = [
        str(driver), "--subject", "reference_ports",
        "--cases", str(cases), "--out", str(out),
    ]
    try:
        run_port_swap.main()
    finally:
        sys.argv = argv
        shutil.rmtree(scratch, ignore_errors=True)
    report = json.loads(out.read_text(encoding="utf-8"))

    # `control_red` and `unmutated_control_failed` are read out of the JSON.
    # Never the exit code -- FI-02-DF-02.
    broken = set(report["unmutated_control_failed"])
    results: dict[str, dict[str, Any]] = {}
    for mutant_id, record in report["per_mutant"].items():
        if not record["applied_exactly_once"]:
            raise MutantNotApplied(
                f"{mutant_id}: port-swap driver applied it "
                f"{record['occurrences_of_find']} time(s)"
            )
        detectors: dict[str, Any] = {}
        for column, cell in record["cells"].items():
            evidence = record["evidence"].get(column, {})
            # The shipped driver's two suite columns carry NO executable count.
            # They are kept under distinct names so the counted `suite-real` /
            # `suite-fake` this runner produces do not silently overwrite them:
            # two readings of the same subject that disagree is a finding, and a
            # collision would hide it.
            column = {"suite-real": "portswap-suite-real",
                      "suite-fake": "portswap-suite-fake"}.get(column, column)
            ran = evidence.get("total_ran")
            if column in broken:
                cell_verdict = CONTROL_RED
            elif cell == "KILLED":
                cell_verdict = DIES
            elif ran == 0:
                cell_verdict = INERT
            else:
                cell_verdict = SURVIVES
            detectors[column] = {
                "verdict": cell_verdict,
                "raw_cell": cell,
                "executed": ran,
                # The two SUITE columns of the shipped driver return only
                # `total_failed`. There is no executable count behind them, so a
                # SURVIVED there cannot be told apart from a suite that did not
                # run. Reported, not silently filled in.
                "executable_count_available": ran is not None,
                "evidence": evidence,
                "uses_ports_binding": column.startswith("corpus-port-swap"),
            }
        results[mutant_id] = {
            "driver_present": True,
            "detectors": detectors,
            "control_red": report["control_red"],
            "unmutated_control_failed": report["unmutated_control_failed"],
        }
    return results


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalogue", type=Path, default=DEFAULT_CATALOGUE)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--only", action="append", default=[])
    parser.add_argument("--ref", default="HEAD", help="git ref to stage the tree from")
    parser.add_argument(
        "--cases", type=Path, default=None,
        help="generated port corpus package; without it the ports family is NOT_RUN",
    )
    parser.add_argument(
        "--family", choices=("staged", "ports", "all"), default="all",
    )
    parser.add_argument("--keep-tree", action="store_true")
    args = parser.parse_args(argv)

    document = tomllib.loads(args.catalogue.read_text(encoding="utf-8"))
    detectors = {entry["id"]: entry for entry in document.get("detector", [])}
    # Controls run through EXACTLY the same path as the gap mutants. A control
    # measured by a second code path is not a control for the first one.
    declared = [{**entry, "is_control": False} for entry in document.get("mutant", [])]
    declared += [{**entry, "is_control": True} for entry in document.get("control", [])]
    mutants = [
        entry for entry in declared
        if not args.only or entry["id"] in args.only
    ]

    workdir = Path(tempfile.mkdtemp(prefix="sm01-gap-mutants-"))
    tree = workdir / "tree"
    results: dict[str, Any] = {}
    unapplied: list[str] = []

    try:
        ports: dict[str, dict[str, Any]] = {}
        if args.family in ("ports", "all"):
            if args.cases is None:
                ports = {m["id"]: {"driver_present": None} for m in mutants
                         if m.get("port_swap_path")}
            else:
                ports = run_ports_family(mutants, args.cases.resolve(), workdir)

        baselines: dict[str, dict[str, Any]] = {}
        wanted = {
            (row["id"], tuple(row.get("args", [])))
            for mutant in mutants
            for row in mutant.get("detector", [])
        }
        # Staging costs a `git archive` of the whole tree. A run that selects no
        # staged detector -- `--family ports`, or an `--only` that matches
        # nothing -- must not need a working `.git` to report its
        # `[[not_seedable]]` rows.
        if args.family in ("staged", "all") and wanted:
            print(f"staging {args.ref} ...", file=sys.stderr)
            stage_tree(args.ref, tree)
            for detector_id, extra in sorted(wanted):
                print(f"baseline: {detector_id} {' '.join(extra)}", file=sys.stderr)
                baselines[f"{detector_id} {' '.join(extra)}".strip()] = run_detector(
                    detectors[detector_id], tree, list(extra), args.cases
                )

        for mutant in mutants:
            record: dict[str, Any] = {
                "is_control": mutant["is_control"],
                "control_role": mutant.get("control_role"),
                "must_die_on": mutant.get("must_die_on", []),
                "mechanism": mutant["mechanism"],
                "removed_by": mutant["removed_by"],
                "claims_to_catch": mutant["claims_to_catch"],
                "gap": mutant["gap"],
                "seeded_in": [edit["path"] for edit in mutant.get("edit", [])],
                "detectors": {},
            }
            if mutant["id"] in ports:
                port_record = ports[mutant["id"]]
                if port_record.get("driver_present") is None:
                    record["detectors"]["corpus-port-swap"] = {"verdict": NOT_RUN,
                                                               "reason": "no --cases given"}
                elif port_record["driver_present"] is False:
                    record["detectors"]["corpus-port-swap"] = {"verdict": REMOVED}
                else:
                    record["detectors"].update(port_record["detectors"])
                    record["control_red"] = port_record["control_red"]
                    record["unmutated_control_failed"] = port_record[
                        "unmutated_control_failed"
                    ]

            if args.family in ("staged", "all") and mutant.get("detector"):
                print(f"mutant {mutant['id']} ...", file=sys.stderr)
                try:
                    state = apply_mutant(tree, mutant)
                except MutantNotApplied as exc:
                    unapplied.append(str(exc))
                    record["applied"] = False
                    record["problem"] = str(exc)
                    results[mutant["id"]] = record
                    continue
                record["applied"] = True
                record["edits"] = state["applied"]
                try:
                    for row in mutant["detector"]:
                        extra = list(row.get("args", []))
                        key = f"{row['id']} {' '.join(extra)}".strip()
                        observed = run_detector(detectors[row["id"]], tree, extra, args.cases)
                        baseline = baselines.get(key, {})
                        record["detectors"][row["id"]] = {
                            "verdict": verdict(baseline, observed),
                            "executed": observed["executed"],
                            "executable_count_available": True,
                            "exit": observed.get("exit"),
                            "new_failing_nodes": new_failures(baseline, observed)[0],
                            "self_detected_nodes": new_failures(baseline, observed)[1],
                            "baseline_failing_nodes": baseline.get("failing_nodes", []),
                            "tail": observed["tail"],
                            "uses_ports_binding": bool(
                                detectors[row["id"]].get("uses_ports_binding")
                            ),
                        }
                finally:
                    restore(state, tree)
            results[mutant["id"]] = record

        # R2 -- a control that cannot fail is worse than no control, so it is
        # reported RED rather than quietly passed over. A gap mutant's SURVIVES
        # on a detector whose positive control did not die there is not a
        # survival; it is an undecided cell, and the artifact says so.
        control_red: list[dict[str, Any]] = []
        for mutant_id, record in results.items():
            if not record.get("is_control"):
                continue
            for detector_id in record.get("must_die_on", []):
                cell = record["detectors"].get(detector_id)
                if cell is None:
                    control_red.append({"control": mutant_id, "detector": detector_id,
                                        "why": "the control was never run on this detector"})
                elif cell["verdict"] != DIES:
                    control_red.append({"control": mutant_id, "detector": detector_id,
                                        "why": f"control reported {cell['verdict']}, want DIES",
                                        "executed": cell.get("executed")})
        undecided = sorted({row["detector"] for row in control_red})

        report = {
            "registry": document["registry"],
            "control_red": control_red,
            "detectors_with_a_red_control": undecided,
            "ref": args.ref,
            "catalogue": str(args.catalogue.relative_to(REPO_ROOT)),
            "cases": str(args.cases) if args.cases else None,
            "baselines": baselines,
            "per_mutant": dict(sorted(results.items())),
            # R2: a mechanism with no seedable gap is REPORTED, never dropped
            # from the table. Silence and "we checked and there is none" are
            # different claims.
            "not_seedable": document.get("not_seedable", []),
            "mutants_not_applied": unapplied,
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(render(report))
        print(f"\nwrote {args.out}")
        return 1 if unapplied else 0
    finally:
        if args.keep_tree:
            print(f"tree kept at {workdir}", file=sys.stderr)
        else:
            shutil.rmtree(workdir, ignore_errors=True)


def render(report: dict[str, Any]) -> str:
    lines = [
        "GAP MUTANTS -- what currently catches the fault each removal claims to cover",
        "",
    ]
    for mutant_id, record in report["per_mutant"].items():
        lines.append(f"{mutant_id}  [{record['mechanism']} -- removed by {record['removed_by']}]")
        if record.get("applied") is False:
            lines.append(f"    NOT APPLIED: {record['problem']}")
            continue
        for detector_id, cell in sorted(record["detectors"].items()):
            executed = cell.get("executed")
            count = "no executable count" if not cell.get(
                "executable_count_available", True
            ) else f"{executed} executed"
            lines.append(f"    {cell['verdict']:<12} {detector_id:<28} {count}")
    if report.get("control_red"):
        lines += ["", "RED CONTROLS (R2) -- every SURVIVES on these detectors is UNDECIDED, not a survival:"]
        for row in report["control_red"]:
            lines.append(f"  {row['control']} on {row['detector']}: {row['why']}")
    elif report.get("detectors_with_a_red_control") == []:
        lines += ["", "Every positive control died on every detector it declares."]
    if report["not_seedable"]:
        lines += ["", "NO SEEDABLE GAP -- reported, not skipped:"]
        for row in report["not_seedable"]:
            lines.append(f"  {row['mechanism']}")
            lines.append(f"      {row['reason']}")
    if report["mutants_not_applied"]:
        lines += ["", "MUTANTS THAT DID NOT APPLY (every one voids its own row):"]
        lines += [f"  {problem}" for problem in report["mutants_not_applied"]]
    else:
        lines += ["", "Every declared mutant applied exactly once."]
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
