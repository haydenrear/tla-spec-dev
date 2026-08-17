"""SS-06. THE DELETION METHOD, RUN AS A BATTERY.

    python3 specs/results/scorecards/stabilize-substrate/SS-06/vacuity_probe.py \
        --root /path/to/a/THROWAWAY/checkout [--case NAME] [--list] [--selftest]

WHY THIS EXISTS. `CA-07-DF-05` -- one of the three genuine shipped-code bugs the
predecessor epic caught -- was found by DELETING THE CODE A TEST COVERS AND
SEEING WHETHER ANYTHING WENT RED. Nothing in this repository computes that.
`CA-10-DF-14` names three tests that "pass" while asserting nothing; the only
way to tell a pass from a vacuous pass is to take the thing away and look at the
report. This runs that experiment as a named, repeatable battery instead of a
one-off grep, so the answer is a table rather than a claim.

NOT A GATE. It asserts nothing about this repository, refuses no close, changes
no exit code anywhere else, and nothing invokes it. It prints a census. A case
whose observed summary differs from its recorded expectation is printed as
`DIFFERS` and the process still exits 0; the finding is the row, not the code.

IT MUTATES THE TREE IT IS POINTED AT, ON PURPOSE. That is the whole method, and
it is why `--root` is REQUIRED and why this file refuses to run against its own
repository. Point it at a throwaway clone. Every mutation is reverted in a
`finally`, and the tree is checked with `git status --porcelain` afterwards; a
dirty tree at the end is reported as `NOT-REVERTED` rather than swallowed.

ABSENT INPUT (`R1`, as extended by `SS-02`). The correct answer to an absent or
empty input is a REFUSAL or an explicit UNDECIDED, never a PASS. Three cases,
all exercised by `--selftest` through `main()` and its exit code:
  * `--root` omitted                    -> REFUSED, exit 2
  * `--root` does not exist             -> REFUSED, exit 2
  * `--root` exists but is not a
    checkout of this repository
    (no `tests/`, no `scripts/`)        -> REFUSED, exit 2
A refusal is exit 2 and names the root. Exit 0 means the battery RAN; it never
means "the tree is fine".

WHY THE SELF-TEST INVOKES `main()`. `SS-07-DF-06` found the predicate-restating
self-test -- a check that re-implements the assertion instead of running the
command -- inside the instrument built to police exactly this class, and the
vacuity was concealing a crash on a line the restating version could never
reach. This self-test calls `main()` with real argv and asserts on the EXIT CODE
and the printed text. Seed a mutant to see it fail: delete the `root.exists()`
refusal in `main()` and `--selftest` reports FAIL.

KNOWN LIMIT, STATED RATHER THAN DISCOVERED LATER: a case proves something about
THE NODES IT RUNS, not about the suite. `PASSES-UNCHANGED` means those nodes did
not notice; it does not mean nothing anywhere did. The battery runs a named node
list per case for that reason, and the node list is part of the record.
"""
from __future__ import annotations

import argparse
import dataclasses
import re
import shutil
import subprocess
import sys
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[5]

PYTEST = ["uv", "run", "--with", "pytest", "--with", "pyyaml", "-m", "pytest"]

SPECS_CURRENT_NODES = [
    "tests/test_analyze_complexity.py::test_repository_own_model_reproduces_the_recorded_state_space_bound",
    "tests/test_analyze_complexity.py::test_cm01df02_the_repository_own_cfg_is_unchanged_by_the_fix",
    "tests/test_analyze_complexity.py::test_repository_own_model_has_landed_the_setup_phase_collapse",
]
EXAMPLE_NODES = [
    "tests/test_analyze_complexity.py::test_rp04_shipped_example_no_longer_reports_a_partial_bound_within_cap",
    "tests/test_analyze_complexity.py::test_cm01df02_shipped_example_cfg_yields_only_its_invariant",
    "tests/test_analyze_complexity.py::test_cd06_real_distributed_history_external_matrix_lists_the_next_disjuncts",
]

ANALYZER = "scripts/analyze_complexity.py"
EXAMPLE_TLA = "examples/distributed_history/specs/program_model/External.tla"
EXAMPLE_CFG = "examples/distributed_history/specs/program_model/External.cfg"


@dataclasses.dataclass
class Case:
    name: str
    what_is_taken_away: str
    nodes: list[str]
    # (root) -> None. Mutates the tree. Reverted by git checkout afterwards.
    mutate: object
    expectation: str


def _rm(root: pathlib.Path, rel: str) -> None:
    target = root / rel
    if target.is_dir():
        shutil.rmtree(target)
    elif target.exists():
        target.unlink()
    else:
        # A case whose subject is not there cannot say anything about the tree,
        # and "nothing to take away" is not "taking it away changed nothing".
        # Exit 2, the same refusal code as every other absent input here.
        print(
            f"vacuity_probe: REFUSED: case target absent before mutation: {rel}. "
            f"Nothing was taken away, so nothing is known about this case.",
            file=sys.stderr,
        )
        raise SystemExit(2)


def _sub(root: pathlib.Path, rel: str, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    if old not in text:
        print(
            f"vacuity_probe: REFUSED: mutation site not found in {rel}: {old!r}. "
            f"The code this case is about has moved; nothing was mutated, so "
            f"nothing is known about this case.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


CASES: list[Case] = [
    Case(
        name="input-absent-specs-current",
        what_is_taken_away="the whole of specs/current/ -- the model the three nodes are ABOUT",
        nodes=SPECS_CURRENT_NODES,
        mutate=lambda root: _rm(root, "specs/current"),
        expectation="3 skipped -- UNDECIDED and visible in the summary line. Before "
        "this ticket: 3 passed, indistinguishable from a real pass.",
    ),
    Case(
        name="input-absent-example-model",
        what_is_taken_away="examples/distributed_history/.../External.tla and .cfg -- "
        "committed files with no legitimate absent state",
        nodes=EXAMPLE_NODES,
        mutate=lambda root: (_rm(root, EXAMPLE_TLA), _rm(root, EXAMPLE_CFG)),
        expectation="3 failed -- a REFUSAL, because a committed fixture that has "
        "vanished is a defect, not a configuration. Before this ticket: 3 passed.",
    ),
    Case(
        name="code-deleted-state-space-bound",
        what_is_taken_away="the multiplication in state_space_bound() -- the product "
        "becomes 1 for every model",
        nodes=SPECS_CURRENT_NODES + EXAMPLE_NODES,
        mutate=lambda root: _sub(
            root, ANALYZER,
            "        bound *= int(dimension.cardinality or 1)",
            "        bound *= 1  # vacuity_probe mutant",
        ),
        expectation="red -- these nodes assert exact bounds, so deleting the "
        "product must be visible to them.",
    ),
    Case(
        name="code-deleted-parse-cfg-invariants",
        what_is_taken_away="the body of parse_cfg_invariants() -- it answers 'no "
        "invariants' for every .cfg",
        nodes=SPECS_CURRENT_NODES + EXAMPLE_NODES,
        mutate=lambda root: _sub(
            root, ANALYZER,
            "    text = strip_comments(cfg_text)\n    names: list[str] = []\n    in_block = False",
            "    return []  # vacuity_probe mutant\n    text = strip_comments(cfg_text)\n"
            "    names: list[str] = []\n    in_block = False",
        ),
        expectation="red -- the two cfg nodes read real invariant names out of a "
        "real .cfg.",
    ),
    Case(
        name="subject-changed-setup-phase",
        what_is_taken_away="the setup_phase variable declaration in the repository's "
        "own live model",
        nodes=SPECS_CURRENT_NODES,
        mutate=lambda root: _sub(
            root, "specs/current/TlaSpecDevCli.tla",
            "setup_phase", "setup_phase_RENAMED_BY_PROBE",
        ),
        expectation="red -- the node exists to say the MF-022 collapse is still "
        "landed in the live model.",
    ),
    Case(
        name="subject-changed-mc-cfg",
        what_is_taken_away="the INVARIANT name in the repository's own MC.cfg",
        nodes=SPECS_CURRENT_NODES,
        mutate=lambda root: _sub(
            root, "specs/current/MC.cfg", "TypeInvariant", "NOTTYPEINVARIANT",
        ),
        expectation="red -- the node asserts the first configured invariant IS "
        "TypeInvariant.",
    ),
    # THE SEVENTH CASE, added after the independent reviewer of PR #286 showed the
    # first six DID NOT SUPPORT THE SENTENCE THEY WERE CITED FOR. The claim was
    # "these six notice every change to the code and the model they cover";
    # measured node by node,
    # `test_cd06_real_distributed_history_external_matrix_lists_the_next_disjuncts`
    # PASSES under BOTH code mutations -- it asserts an action list, not a bound
    # and not a cfg invariant -- and it is not in either subject-change node list
    # at all. So five of six were established by execution and the sixth was
    # asserted. This case reaches it, and it is the only one that does.
    Case(
        name="subject-changed-example-next-relation",
        what_is_taken_away="one disjunct -- RunFulfillmentWorkerNoop -- from the "
        "shipped example's ExternalNext",
        nodes=EXAMPLE_NODES,
        mutate=lambda root: _sub(
            root, EXAMPLE_TLA,
            "  \\/ \\E c \\in Clients : RunFulfillmentWorkerNoop(c)\n",
            "",
        ),
        expectation="red on test_cd06 -- it asserts the exact twelve-disjunct "
        "action list, so removing a disjunct must be visible to it.",
    ),
]

# `pytest -q`'s LAST line, and only that line: `3 failed, 2 passed in 0.07s`.
#
# SS-06-DF-02, found by running this battery rather than by reading it. The
# first version of `summarise` grepped the WHOLE report for `(\d+) passed` and
# took the last match. `pytest` echoes the source of a failing assertion, the
# repaired helper's docstring contains the string "`3 passed` either way", and
# the census duly reported `3 failed, 3 passed` for a THREE-node run. A
# recogniser that reads its subject's prose as its subject's result is
# `CA-08-DF-01` seen from the other side, and it shipped inside the instrument
# this ticket wrote to police vacuous checks. Anchor on the summary line.
SUMMARY_LINE_RE = re.compile(
    r"^(?P<counts>\d+ [a-z]+(?:, \d+ [a-z]+)*)"
    r"(?: in \d+(?:\.\d+)?s.*)?$"
)


def summarise(stdout: str) -> str:
    """The pytest summary counts, as a stable string, or UNPARSED.

    Absent input, again: an empty or unrecognisable pytest report is UNPARSED,
    never "0 failed". "I could not read the report" and "the report says zero"
    are different answers.
    """
    if not stdout.strip():
        return "UNPARSED (no output)"
    for raw in reversed(stdout.splitlines()):
        line = raw.strip().strip("=").strip()
        if not line or " in " not in line:
            continue
        match = SUMMARY_LINE_RE.match(line)
        if match:
            return match.group("counts")
    return "UNPARSED (no pytest summary line in report)"


def run_case(root: pathlib.Path, case: Case, verbose: bool) -> dict:
    before = subprocess.run(
        PYTEST + ["-q", *case.nodes], cwd=root, capture_output=True, text=True
    )
    try:
        case.mutate(root)
        after = subprocess.run(
            PYTEST + ["-q", *case.nodes], cwd=root, capture_output=True, text=True
        )
    finally:
        subprocess.run(["git", "checkout", "--", "."], cwd=root, capture_output=True)
        subprocess.run(["git", "clean", "-qfd"], cwd=root, capture_output=True)
    dirty = subprocess.run(
        ["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True
    ).stdout.strip()
    row = {
        "case": case.name,
        "taken_away": case.what_is_taken_away,
        "nodes": len(case.nodes),
        "unmutated": summarise(before.stdout),
        "unmutated_exit": before.returncode,
        "mutated": summarise(after.stdout),
        "mutated_exit": after.returncode,
        "reverted": "clean" if not dirty else f"NOT-REVERTED: {dirty}",
        "expectation": case.expectation,
    }
    if verbose:
        row["mutated_stdout"] = after.stdout
    return row


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--root", default=None)
    parser.add_argument("--case", default=None)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()

    if args.list:
        for case in CASES:
            print(f"{case.name}\n    takes away: {case.what_is_taken_away}")
        return 0

    if args.root is None:
        print(
            "vacuity_probe: REFUSED: --root is required and must name a THROWAWAY "
            "checkout. This battery mutates the tree it is pointed at.",
            file=sys.stderr,
        )
        return 2
    root = pathlib.Path(args.root).resolve()
    if not root.exists():
        print(f"vacuity_probe: REFUSED: root does not exist: {root}", file=sys.stderr)
        return 2
    if not root.is_dir():
        print(
            f"vacuity_probe: REFUSED: root is not a directory: {root}",
            file=sys.stderr,
        )
        return 2
    # SS-06-DF-05, found by MEASURING this instrument against SS-02's own rule
    # rather than reasoning about it. Before this branch existed, a directory
    # this process is not allowed to READ answered "no tests/ or scripts/" --
    # `Path.is_dir()` returns False on a PermissionError, so "I was not allowed
    # to look" was reported in the exact words of "there is nothing there". The
    # VERDICT was already correct (a refusal, exit 2) and the CAUSE was a
    # fabrication, which is the same defect `SS-07-DF-08` found in the sweep it
    # shipped and the same one `SS-01-DF-04` found when an unreadable ledger
    # produced 14 fabrication accusations. Distinguishing them costs one branch.
    try:
        next(root.iterdir(), None)
    except PermissionError:
        print(
            f"vacuity_probe: REFUSED: root cannot be READ (permission denied): "
            f"{root}. This is NOT the same answer as 'not a checkout' -- nothing "
            f"was looked at, so nothing is known about what is there.",
            file=sys.stderr,
        )
        return 2
    if not (root / "tests").is_dir() or not (root / "scripts").is_dir():
        print(
            f"vacuity_probe: REFUSED: root is not a checkout of this repository "
            f"(no tests/ or scripts/): {root}",
            file=sys.stderr,
        )
        return 2
    if root == REPO_ROOT:
        print(
            f"vacuity_probe: REFUSED: root is this instrument's own repository: "
            f"{root}. Clone it first.",
            file=sys.stderr,
        )
        return 2

    selected = [c for c in CASES if args.case in (None, c.name)]
    if not selected:
        print(f"vacuity_probe: REFUSED: no such case: {args.case}", file=sys.stderr)
        return 2

    print(f"vacuity_probe: root {root}")
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True
    ).stdout.strip()
    print(f"vacuity_probe: tree {head or 'UNKNOWN (not a git checkout)'}")
    print()
    for case in selected:
        row = run_case(root, case, args.verbose)
        print(f"case        {row['case']}")
        print(f"  takes away  {row['taken_away']}")
        print(f"  nodes       {row['nodes']}")
        print(f"  unmutated   {row['unmutated']}  (exit {row['unmutated_exit']})")
        print(f"  mutated     {row['mutated']}  (exit {row['mutated_exit']})")
        print(f"  revert      {row['reverted']}")
        print(f"  expectation {row['expectation']}")
        verdict = (
            "NOTICED" if row["unmutated"] != row["mutated"] else "PASSES-UNCHANGED"
        )
        print(f"  verdict     {verdict}")
        if args.verbose:
            print("  --- mutated report ---")
            for line in row["mutated_stdout"].splitlines():
                print(f"  | {line}")
        print()
    return 0


def selftest() -> int:
    """Run main() for real and assert on its exit code and its output.

    NOT a restatement of the predicates above: every case below goes through
    `main()` with an argv, and asserts the exit code AND the text. Seed a mutant
    -- delete the `root.exists()` refusal -- and this reports FAIL.
    """
    import contextlib
    import io
    import tempfile

    failures: list[str] = []

    def check(label: str, argv: list[str], want_code: int, want_text: str) -> None:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = main(argv)
            except SystemExit as exc:  # argparse
                code = int(exc.code or 0)
        text = out.getvalue() + err.getvalue()
        if code != want_code:
            failures.append(f"{label}: exit {code}, wanted {want_code}")
        if want_text not in text:
            failures.append(f"{label}: output did not contain {want_text!r}: {text!r}")

    check("no --root", [], 2, "--root is required")
    with tempfile.TemporaryDirectory() as tmp:
        missing = pathlib.Path(tmp) / "nope"
        check("absent root", ["--root", str(missing)], 2, "root does not exist")
        check("empty root", ["--root", tmp], 2, "not a checkout of this repository")
        a_file = pathlib.Path(tmp) / "afile"
        a_file.write_text("not a directory\n", encoding="utf-8")
        check("root is a file", ["--root", str(a_file)], 2, "root is not a directory")
        # SS-06-DF-05, pinned. "I was not allowed to look" must not be reported
        # in the words of "there is nothing there". Skipped, with a printed
        # reason, when the process can read anything regardless of mode.
        locked = pathlib.Path(tmp) / "locked"
        locked.mkdir()
        locked.chmod(0o000)
        try:
            try:
                next(locked.iterdir(), None)
            except PermissionError:
                check("unreadable root", ["--root", str(locked)], 2,
                      "cannot be READ (permission denied)")
            else:
                print("selftest: SKIPPED unreadable-root case -- this process can "
                      "read a 0o000 directory (running as root?), so the state "
                      "cannot be staged here. NOT counted as a pass.")
        finally:
            locked.chmod(0o755)
    check("own repository", ["--root", str(REPO_ROOT)], 2, "REFUSED")
    check("--list", ["--list"], 0, "input-absent-specs-current")

    # SS-06-DF-02, pinned in both directions. The trap is a REAL `pytest -q`
    # report whose traceback echoes the string "`3 passed` either way" out of
    # the source it is printing; the answer must come from the summary LINE.
    trap = (
        "FFF\n"
        "=================================== FAILURES ===================================\n"
        '        `SS-06` it turned it green (`vacuity_probe.py --case\n'
        '        input-absent-example-model`, tree `8dd0442`: `3 passed` either way).\n'
        "E           AssertionError: ... is a COMMITTED fixture and is not on disk.\n"
        "=========================== short test summary info ============================\n"
        "FAILED tests/test_analyze_complexity.py::test_one\n"
        "3 failed in 0.07s\n"
    )
    for label, text, want in (
        ("summary line wins over echoed prose", trap, "3 failed"),
        ("mixed counts", "..s\n1 failed, 4 passed, 2 skipped in 1.20s\n", "1 failed, 4 passed, 2 skipped"),
        ("clean run", "......\n86 passed in 5.48s\n", "86 passed"),
        ("absent report", "", "UNPARSED (no output)"),
        ("unreadable report", "totally unrelated\n", "UNPARSED (no pytest summary line in report)"),
    ):
        got = summarise(text)
        if got != want:
            failures.append(f"summarise/{label}: got {got!r}, wanted {want!r}")

    if failures:
        for line in failures:
            print(f"selftest: {line}")
        print("selftest: FAIL")
        return 1
    print("selftest: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
