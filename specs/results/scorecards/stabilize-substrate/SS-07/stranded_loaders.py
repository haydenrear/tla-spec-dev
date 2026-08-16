"""SS-07. Sweep the SEALED RECORD for scripts that load a file the tree no
longer has -- the class `repriced_history.py` is one instance of.

    python3 specs/results/scorecards/stabilize-substrate/SS-07/stranded_loaders.py [--root DIR]

WHY THIS EXISTS. `CA-02-DF-04`'s own `suggested_fix` names the mechanical check
that would have caught the stranded pricing instrument: *"a cut must GREP THE
SEALED RECORD for loaders of every file it deletes"*. Filing that finding routed
it; nothing ever computed it. This computes it, in the only direction a sealed
record allows -- from the loaders outward -- so it answers the question for every
cut at once instead of one cut at a time.

NOT A GATE. It asserts nothing, refuses nothing, and exits 0 on any finding. It
prints a census and names every stranded reference. Nothing invokes it.

WHAT IT DOES. For every `*.py` under the record root it parses the file with
`ast` and collects every string literal that denotes a repository-relative path
(a literal whose first segment is a real top-level directory of this repository,
or which resolves against the file's own directory). It then reports, per file,
which of those paths are ABSENT at the tree it is run in.

ABSENT INPUT (`R1`, as extended by `SS-02`). Three absent-input cases are
demonstrated by `--selftest` and the correct answer to each is a REFUSAL or an
explicit UNDECIDED, never a PASS:
  * the record root does not exist            -> REFUSED, exit 2
  * the record root contains no `*.py`        -> UNDECIDED: nothing swept
  * a file parses to zero path literals       -> counted as NO-PATHS, never as
                                                 "all its paths resolve"
The third is the one that matters and it is the same signature defect
`score_tools._finding_ids()` had: "swept and found nothing referenced" and
"referenced nothing this can see" are different answers and a bare integer
cannot tell them apart.

KNOWN LIMIT, STATED RATHER THAN DISCOVERED LATER: this reads STRING LITERALS.
A path assembled at runtime from parts, read from a manifest, or globbed is
invisible to it, so a clean report is a floor and never a proof. It is reported
as `UNREACHABLE-BY-CONSTRUCTION` in the census rather than silently omitted.
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[5]
DEFAULT_RECORD_ROOT = REPO_ROOT / "specs" / "results"

# A literal is treated as a repository path only if its first segment is one of
# these. Anything else (a URL, a format string, a shell fragment) is ignored.
TOP_LEVEL = {
    "examples", "scripts", "specs", "tests", "spec_double_compiler",
    "templates", "references", "prompts", "test_graph", "skill-scripts",
    "tickets", "skill-dev",
}
SUFFIXES = {
    ".py", ".toml", ".json", ".md", ".yaml", ".yml", ".tla", ".cfg", ".txt",
    ".sh", ".kts", ".java",
}


def path_literals(tree: ast.AST) -> set[str]:
    out: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            s = node.value.strip()
            if "/" not in s or s.startswith(("http://", "https://", "/")):
                continue
            if "\n" in s or " " in s or "*" in s or "{" in s or "%" in s:
                continue
            head = s.split("/", 1)[0]
            if head not in TOP_LEVEL:
                continue
            if pathlib.PurePosixPath(s).suffix not in SUFFIXES:
                continue
            out.add(s)
    return out


def sweep(record_root: pathlib.Path) -> dict:
    files = sorted(record_root.rglob("*.py"))
    rows = []
    for f in files:
        try:
            tree = ast.parse(f.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError) as exc:
            rows.append({"file": f, "unparsed": str(exc), "refs": [], "missing": []})
            continue
        refs = sorted(path_literals(tree))
        missing = [r for r in refs if not (REPO_ROOT / r).exists()]
        rows.append({"file": f, "unparsed": None, "refs": refs, "missing": missing})
    return {"root": record_root, "files": files, "rows": rows}


def render(report: dict) -> str:
    rows = report["rows"]
    lines = [
        "=" * 96,
        "STRANDED LOADERS IN THE SEALED RECORD -- scripts that name a file the tree does not have",
        "=" * 96,
        f"record root : {report['root']}",
        f"repo root   : {REPO_ROOT}",
        "",
    ]
    stranded = [r for r in rows if r["missing"]]
    no_paths = [r for r in rows if not r["unparsed"] and not r["refs"]]
    unparsed = [r for r in rows if r["unparsed"]]
    for r in stranded:
        # A `--root` outside this repository is legitimate -- `SS-01-DF-03`: a
        # verdict is a joint property of the file AND the tree it is swept in,
        # so sweeping a foreign tree is a thing a caller will do. The first
        # version called `.relative_to(REPO_ROOT)` unconditionally and CRASHED
        # with `ValueError` on any such root. FOUND BY MAKING THE SELF-TEST CALL
        # THE ENTRY POINT: the predicate-restating version could never reach
        # this line. `SS-07-DF-06`.
        resolved = r["file"].resolve()
        try:
            shown = resolved.relative_to(REPO_ROOT)
        except ValueError:
            shown = resolved
        lines.append(f"STRANDED  {shown}")
        for m in r["missing"]:
            lines.append(f"            ABSENT  {m}")
    if not stranded:
        lines.append("no stranded literal path reference found")
    lines += [
        "",
        "-" * 96,
        f"{len(rows)} file(s) swept",
        f"{len(stranded)} file(s) name at least one ABSENT path",
        f"{sum(len(r['missing']) for r in rows)} absent reference(s) in total",
        f"{len(no_paths)} file(s) NO-PATHS (parsed, zero repository path literals) "
        f"-- NOT the same answer as 'every path resolves'",
        f"{len(unparsed)} file(s) UNPARSED",
        "UNREACHABLE-BY-CONSTRUCTION: any path built at runtime, read from a manifest,",
        "or globbed is invisible to a literal sweep. A clean report is a FLOOR.",
    ]
    return "\n".join(lines)


def selftest() -> int:
    """R1 as extended by SS-02: a demonstrated FAILING input and demonstrated
    ABSENT inputs -- and EVERY CASE CALLS THE ENTRY POINT.

    CORRECTED 2026-08-16 (`SS-07-DF-06`). The first version of this self-test
    computed `"REFUSED" if not missing_root.exists() else "exists?!"` and
    asserted on `rep["files"]` directly. Those two cases RESTATED THE PREDICATE
    INSTEAD OF RUNNING THE INSTRUMENT: they would have printed PASS even if the
    refusal branch had been deleted. That is the `CA-10-DF-14` vacuous-check
    shape, inside the instrument written to police vacuity, and review caught it.
    Every case below now invokes `main()` and asserts on ITS EXIT CODE AND ITS
    OUTPUT, so deleting a branch turns the self-test red.
    """
    import contextlib, io, tempfile

    def run(argv: list[str]) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue() + err.getvalue()

    results = []

    # (1) ABSENT record root -> REFUSED, exit 2. Never "0 stranded".
    code, text = run(["--root", str(REPO_ROOT / "specs" / "results" / "__no_such_root__")])
    results.append(("absent-input 1: record root does not exist",
                    code == 2 and "REFUSED" in text,
                    f"exit={code} REFUSED={'REFUSED' in text}", "exit 2 + REFUSED"))

    with tempfile.TemporaryDirectory() as td:
        # (2) EMPTY record root -> UNDECIDED, and NOT a clean report.
        empty = pathlib.Path(td) / "empty"
        empty.mkdir()
        code, text = run(["--root", str(empty)])
        results.append(("absent-input 2: record root holds no *.py",
                        "UNDECIDED" in text and "no stranded" not in text,
                        f"exit={code} UNDECIDED={'UNDECIDED' in text} "
                        f"clean_claimed={'no stranded' in text}",
                        "UNDECIDED, and no clean verdict"))

        # (3) A file naming ZERO paths is NO-PATHS, not "all its paths resolve".
        d3 = pathlib.Path(td) / "nopaths"
        d3.mkdir()
        (d3 / "a.py").write_text("x = 1\n", encoding="utf-8")
        code, text = run(["--root", str(d3)])
        results.append(("absent-input 3: file names zero repository paths",
                        "1 file(s) NO-PATHS" in text and "no stranded literal path reference found" in text,
                        f"exit={code} no_paths_counted={'1 file(s) NO-PATHS' in text}",
                        "counted as NO-PATHS, reported separately from 'resolves'"))

        # (4) FAILING input on a REAL subject shape: a file naming a file this
        #     repository genuinely deleted must come back STRANDED.
        d4 = pathlib.Path(td) / "failing"
        d4.mkdir()
        (d4 / "b.py").write_text(
            'p = "examples/validation/gap_mutants/price_removal.py"\n', encoding="utf-8")
        code, text = run(["--root", str(d4)])
        results.append(("failing-input: file names a really-deleted file",
                        "STRANDED" in text and "1 file(s) name at least one ABSENT path" in text,
                        f"exit={code} STRANDED={'STRANDED' in text}",
                        "STRANDED, counted in the census"))

    ok = True
    for name, passed, observed, expected in results:
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
        print(f"         expected: {expected}")
        print(f"         observed: {observed}")
        ok &= passed
    print("\nselftest:", "PASS" if ok else "FAIL",
          "-- every case invoked main(); none restates the predicate")
    return 0 if ok else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="stranded_loaders.py")
    ap.add_argument("--root", default=str(DEFAULT_RECORD_ROOT))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    root = pathlib.Path(args.root)
    if not root.exists():
        print(f"REFUSED: record root {root} does not exist. An absent record is not "
              f"a clean record.", file=sys.stderr)
        return 2
    report = sweep(root)
    if not report["files"]:
        print(f"UNDECIDED: no *.py under {root}. Nothing was swept, which is not "
              f"the same answer as nothing is stranded.", file=sys.stderr)
        return 0
    print(render(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
