#!/usr/bin/env python3
"""HP-04: the kill table, per class, per arm, over HP-01's seeded catalogue.

    python3 run_m10.py <repo-before> <repo-after>

`repo-before` is a checkout of the epic tip (the oracle as HP-04 found it);
`repo-after` is this ticket's tree. Both are pointed at the SAME corpus, the
SAME adapters and the SAME reference, so the only variable is the oracle.

WHAT COUNTS AS A KILL, stated before any number. The effect oracle exits nonzero
on gaps, dead surface and unobservable targets whether or not a mutant is
present, so exit status cannot distinguish a caught fault from the oracle's
standing findings. A mutant is KILLED by an arm when that arm's REPORT DIFFERS
from its report on the unmutated reference. That definition is only available at
all because of this ticket's third fix: before HP-04 the same corpus on the same
tree produced 20 / 15 / 14 gaps across three runs, so "the report differed"
carried no information.

An arm that produces NO report -- a traceback -- kills nothing and is recorded as
`no-report`, which is worse than zero kills and is reported as its own outcome
rather than folded into one.

Mutants are applied and reverted with HP-01's own catalogue, and the revert is
verified byte-identical after every mutant. Nothing under
`examples/validation/ab/` is left changed.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import tomllib
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
CATALOGUE = REPO / "examples" / "validation" / "ab" / "seeded_faults.toml"
CATALOGUE_ROOT = REPO / "examples" / "validation" / "ab"


def load_mutants() -> list[dict]:
    return tomllib.loads(CATALOGUE.read_text(encoding="utf-8"))["mutants"]


def run_oracle(repo: Path, work: Path, out: Path) -> tuple[int, dict | None, str]:
    """One `run effect-conformance` against the m10 spec dir."""
    env = dict(os.environ)
    # The BEFORE arm cannot import the adapters at all without this
    # (RC-02-DF-02). It is supplied to BOTH arms deliberately: otherwise the
    # comparison would be about the import fix and the skip fix at once, and
    # neither would be measured.
    env["PYTHONPATH"] = os.pathsep.join([str(HERE), str(REPO)])
    proc = subprocess.run(
        [
            sys.executable,
            str(repo / "scripts" / "tla_spec_dev.py"),
            "--spec-root",
            "specs",
            "run",
            "effect-conformance",
            "--target",
            str(HERE),
            "--cases-dir",
            str(HERE / "cases"),
            "--work-dir",
            str(work),
            "--out",
            str(out),
        ],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
    )
    payload = None
    if out.exists():
        payload = json.loads(out.read_text(encoding="utf-8"))
        out.unlink()
    return proc.returncode, payload, proc.stdout + proc.stderr


#: The corpus column runs only the actions whose adapter can execute a case.
#: With the whole corpus its control is RED -- every `Release` case raises the
#: apply()-only TypeError and every `Refuse*` case raises KeyError because the
#: generated corpus recovers NO arguments for a refusal -- and HP-01's own rule
#: is that without a green control every kill could be an unrelated pre-existing
#: failure. Restricting the column is therefore what makes it citeable, and the
#: two reasons it has to be restricted are themselves results: one is HP-04's
#: blind spot and the other is HP-03's.
CORPUS_LABELS = ("Reserve", "Commit", "CloseTenant")

#: `case_0005_reserve via Reserve: AssertionError: ...`
CASE_FAILURE = re.compile(r"^(case_\S+) via (\S+): (\w+)", re.MULTILINE)


def run_corpus(repo: Path, work: Path) -> tuple[int, str]:
    """The corpus runner, which DOES assert the projected after-state.

    Included as a reference column. HP-04 changes nothing about how it asserts,
    so a difference between it and the oracle columns is a fact about the two
    instruments rather than about this ticket.

    The comparison is the SET OF FAILING CASES, not the exit code: the runner
    also reports effect-conformance gaps for its own case-work directories, so
    it exits nonzero on a clean tree and the exit code cannot separate a kill
    from that standing noise.
    """
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(HERE), str(REPO)])
    proc = subprocess.run(
        [
            sys.executable,
            str(repo / "scripts" / "run_generated_case_adapters.py"),
            str(HERE / "cases"),
            "--mapping",
            str(HERE / "case_adapters.toml"),
            "--spec-dir",
            str(HERE),
            "--view",
            "internal",
            "--batch",
            "--work-dir",
            str(work),
            "--import-root",
            str(HERE),
            *[arg for label in CORPUS_LABELS for arg in ("--label", label)],
        ],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
    )
    log = proc.stdout + proc.stderr
    failures = sorted({f"{case}|{label}|{kind}" for case, label, kind in CASE_FAILURE.findall(log)})
    return proc.returncode, "\n".join(failures)


def run_corpus_labels(repo: Path, work: Path, mapping: str, label: str) -> str:
    """The corpus runner over one label under an alternative mapping."""
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(HERE), str(REPO)])
    proc = subprocess.run(
        [
            sys.executable,
            str(repo / "scripts" / "run_generated_case_adapters.py"),
            str(HERE / "cases"),
            "--mapping", str(HERE / mapping),
            "--spec-dir", str(HERE),
            "--view", "internal",
            "--batch",
            "--work-dir", str(work),
            "--import-root", str(HERE),
            "--label", label,
        ],
        cwd=repo, env=env, capture_output=True, text=True,
    )
    log = proc.stdout + proc.stderr
    return "\n".join(sorted({f"{c}|{k}" for c, _, k in CASE_FAILURE.findall(log)}))


def comparable(payload: dict | None, work: Path) -> str:
    """The part of a report a mutant could move, with absolute paths dropped.

    `work` is normalized out as well as the repo root. THIS IS NOT COSMETIC: the
    first version of this script reported 10 of 10 KILLED on every class,
    including the ordering NEGATIVE CONTROL, purely because control and mutant
    ran in differently-named temp directories and every gap message carries its
    target path. That is a false-kill instrument, and it is recorded here rather
    than quietly corrected because the number it produced was flattering.
    """
    if payload is None:
        return "<no-report>"
    def scrub(text: str) -> str:
        return text.replace(str(work), "<work>").replace(str(REPO), "<repo>")
    return json.dumps(
        {
            "verdict": payload["verdict"],
            "gaps": sorted(scrub(g["message"]) for g in payload["gaps"]),
            "dead_surface": sorted(d["port"] for d in payload["dead_surface"]),
            "skipped": sorted(scrub(s["message"]) for s in payload["skipped_cases"]),
            # DEDUPED BY CROSSING, not counted per interception layer. One
            # boundary crossing trips several patches at once (`Path.write_text`
            # calls `Path.open`; `Path.mkdir` calls `os.mkdir`), which
            # `diff_effects` already collapses for gaps. Counting the raw
            # multiset instead reported the ORDERING NEGATIVE CONTROL as killed,
            # because M09 swaps an append for a read-and-rewrite and that trips
            # one more layer -- a difference in how the write was spelled, not
            # in what crossed the boundary.
            "observed": sorted(
                {f"{e['type']}|{e['action']}|{scrub(e['target'])}" for e in payload["observed_effects"]}
            ),
        },
        sort_keys=True,
    )


def main() -> int:
    before = Path(sys.argv[1]).resolve()
    after = Path(sys.argv[2]).resolve()
    mutants = load_mutants()
    tmp = Path(tempfile.mkdtemp(prefix="hp04-m10-"))

    arms = {"oracle-before": before, "oracle-after": after}
    # ONE work dir per arm, reused by the control and by every mutant. That is
    # only safe because of this ticket's own determinism fix: before HP-04 a
    # reused work dir was exactly what made the gap count 20 / 15 / 14.
    work = {arm: tmp / arm for arm in arms}
    corpus_work = tmp / "corpus"
    control_report: dict[str, str] = {}
    control_corpus: dict[str, int] = {}
    for arm, repo in arms.items():
        code, payload, log = run_oracle(repo, work[arm], tmp / f"{arm}-control.json")
        control_report[arm] = comparable(payload, work[arm])
        print(f"CONTROL {arm}: exit={code} report={'yes' if payload else 'NO REPORT'}")
        if payload is None:
            print("  " + (log.strip().splitlines()[-1] if log.strip() else ""))
    control_corpus["corpus-after"] = run_corpus(after, corpus_work)[1]
    print(
        "CONTROL corpus-after: "
        + (f"{len(control_corpus['corpus-after'].splitlines())} failing case(s) -- CONTROL IS RED"
           if control_corpus["corpus-after"] else "GREEN (no case failed)")
        + f", labels {', '.join(CORPUS_LABELS)}"
    )
    print()

    rows: list[dict] = []
    for mutant in mutants:
        target = CATALOGUE_ROOT / mutant["path"]
        original = target.read_text(encoding="utf-8")
        assert original.count(mutant["find"]) == 1, f"{mutant['id']}: find is not exactly-once"
        target.write_text(original.replace(mutant["find"], mutant["replace"]), encoding="utf-8")
        row = {"id": mutant["id"], "class": mutant["fault_class"]}
        try:
            for arm, repo in arms.items():
                _, payload, _ = run_oracle(repo, work[arm], tmp / "m.json")
                if payload is None:
                    row[arm] = "no-report"
                else:
                    row[arm] = (
                        "KILLED" if comparable(payload, work[arm]) != control_report[arm] else "survived"
                    )
            _, corpus_failures = run_corpus(after, corpus_work)
            row["corpus-after"] = (
                "KILLED" if corpus_failures != control_corpus["corpus-after"] else "survived"
            )
        finally:
            target.write_text(original, encoding="utf-8")
            assert target.read_text(encoding="utf-8") == original, "revert was not byte-identical"
        rows.append(row)
        print(f"  {row['id']:34s} {row['class']:18s} "
              f"{row['oracle-before']:11s} {row['oracle-after']:11s} {row['corpus-after']}")

    print()
    print("KILL TABLE -- per class, per arm. No aggregate rate: an average over")
    print("classes whose whole point is that they behave differently is a number")
    print("about nothing (HP-01's catalogue header).")
    print()
    print(f"{'class':20s} {'n':>3s}  {'oracle-before':>14s}  {'oracle-after':>13s}  {'corpus-after':>13s}")
    by_class: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_class[row["class"]].append(row)
    for fault_class in sorted(by_class):
        group = by_class[fault_class]
        def tally(arm: str) -> str:
            killed = sum(1 for row in group if row[arm] == "KILLED")
            if all(row[arm] == "no-report" for row in group):
                return "no-report"
            return f"{killed} of {len(group)}"
        print(
            f"{fault_class:20s} {len(group):3d}  {tally('oracle-before'):>14s}  "
            f"{tally('oracle-after'):>13s}  {tally('corpus-after'):>13s}"
        )
    print()
    m10 = next(row for row in rows if row["id"].startswith("M10"))
    print(f"M10 (HP-04's own seeded blind spot): oracle-before={m10['oracle-before']}, "
          f"oracle-after={m10['oracle-after']}, corpus-after={m10['corpus-after']}")
    print()
    print("M10 COUNTERFACTUAL -- the same action with a run(case, work_dir).")
    print("Prediction N05: HP-04 makes the apply()-only action VISIBLE without")
    print("making it KILLABLE. The counterfactual says what WOULD kill it.")
    mutant = next(m for m in mutants if m["id"].startswith("M10"))
    target = CATALOGUE_ROOT / mutant["path"]
    original = target.read_text(encoding="utf-8")
    control = run_corpus_labels(after, tmp / "cf", "case_adapters_release_runnable.toml", "Release")
    target.write_text(original.replace(mutant["find"], mutant["replace"]), encoding="utf-8")
    try:
        seeded = run_corpus_labels(after, tmp / "cf", "case_adapters_release_runnable.toml", "Release")
    finally:
        target.write_text(original, encoding="utf-8")
    verdict = "KILLED" if seeded != control else "survived"
    print(f"  control failing cases: {len(control.splitlines() if control else [])}; "
          f"seeded: {len(seeded.splitlines() if seeded else [])}; M10 = {verdict}")
    print("  => the limit is NOT the oracle's reach. It is the nine apply()-only")
    print("     adapters in production_adapters.py, which HP-04 may not edit.")
    print()
    print("fixture clean after revert:")
    print(subprocess.run(["git", "status", "--porcelain", "examples/validation/ab"],
                         cwd=REPO, capture_output=True, text=True).stdout or "  (clean)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
