#!/usr/bin/env python3
"""CLI for oracle 4, the mutation kill test.

    tla-spec-dev run kill-test --ticket MF-016 --out results/kill-test.json

Seeds every mutant in the catalog into real production source, runs the
distilled corpus against each, and gates the resulting kill rate against
``kill_rate_floor`` from the manifest budgets.

Exit codes -- no flag changes this mapping:
    0  kill rate met the floor
    1  kill rate below the floor, or a regression against ``--baseline``
    2  incomplete/malformed catalog, or absent declarations

There is deliberately no ``--allow-below-floor``, no ``--accept-survivors``,
and no way to mark a mutant as expected-to-survive. See the ``kill_test``
module docstring for why this particular gate has no waiver: it is the value
floor that keeps every cost cap in the toolchain honest.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.kill_test import (  # noqa: E402
    EXIT_USAGE,
    KillTestCatalogError,
    compare_reports,
    load_catalog,
    render_report,
    run_kill_test,
    subprocess_case_runner,
)

DEFAULT_CATALOG_NAME = "kill_mutants.toml"


def add_arguments(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("--spec-root", default="specs", help="Spec root directory.")
    parser.add_argument("--ticket", help="Use this ticket's current/ spec directory.")
    parser.add_argument("--target", type=Path, help="Explicit spec directory carrying the declarations.")
    parser.add_argument(
        "--catalog",
        type=Path,
        help=f"Mutant catalog TOML. Defaults to <spec-dir>/{DEFAULT_CATALOG_NAME}.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        help="Repository root the mutant paths are relative to. Defaults to the repo root.",
    )
    parser.add_argument(
        "--cfg",
        action="append",
        default=[],
        metavar="NAME",
        help=(
            "Model config(s) whose invariants this kill test must cover, e.g. Internal.cfg. "
            "A kill test measures ONE component's representation with that component's "
            "corpus, so a repository with Internal and External models has two kill tests. "
            "OMITTING THIS IS THE STRICT DEFAULT: every *.cfg in the spec directory is "
            "required. Narrowing reduces only the coverage obligation -- every mutant in the "
            "catalog is still executed and still reported, so this cannot hide a survivor."
        ),
    )
    parser.add_argument(
        "--corpus-command",
        help=(
            "Shell-free command (space separated) that runs the distilled corpus. A nonzero "
            "exit means the seeded mutant was KILLED. Required unless --list-boundaries."
        ),
    )
    parser.add_argument(
        "--baseline",
        type=Path,
        help=(
            "A previous kill-test JSON report. The abstraction validator: a kill rate that "
            "DROPS against this baseline fails, because a revision that kills fewer mutants "
            "deleted bug-relevant behavior rather than re-representing it."
        ),
    )
    parser.add_argument(
        "--compare",
        nargs=2,
        metavar=("BEFORE", "AFTER"),
        type=Path,
        help="Compare two existing reports as an abstraction validation, and run nothing.",
    )
    parser.add_argument(
        "--list-boundaries",
        action="store_true",
        help=(
            "Print the boundaries that require a seeded fault (every declared port and every "
            "invariant) and which ones the catalog covers, then exit."
        ),
    )
    parser.add_argument("--out", type=Path, help="Write the JSON kill matrix here (ticket evidence).")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--timeout", type=int, default=600, help="Per-mutant corpus timeout in seconds.")
    return parser


def resolve_spec_dir(args: argparse.Namespace) -> Path:
    if getattr(args, "target", None):
        return Path(args.target)
    spec_root = Path(getattr(args, "spec_root", "specs"))
    ticket = getattr(args, "ticket", None)
    if ticket:
        return spec_root / "tickets" / ticket / "current"
    return spec_root / "current"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tla-spec-dev run kill-test",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        allow_abbrev=False,
    )
    add_arguments(parser)
    args = parser.parse_args(argv)
    return run(args)


def run(args: argparse.Namespace) -> int:
    if getattr(args, "compare", None):
        before_path, after_path = args.compare
        try:
            before = json.loads(Path(before_path).read_text(encoding="utf-8"))
            after = json.loads(Path(after_path).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR: could not read comparison reports: {exc}", file=sys.stderr)
            return EXIT_USAGE
        legitimate, message = compare_reports(before, after)
        print(message)
        return 0 if legitimate else 1

    repo_root = Path(__file__).resolve().parents[1]
    root = Path(args.root) if getattr(args, "root", None) else repo_root
    spec_dir = resolve_spec_dir(args)
    if not spec_dir.is_dir():
        print(f"ERROR: no spec directory at {spec_dir}", file=sys.stderr)
        return EXIT_USAGE

    catalog_path = Path(args.catalog) if args.catalog else spec_dir / DEFAULT_CATALOG_NAME
    try:
        catalog, suppressions = load_catalog(catalog_path)
    except KillTestCatalogError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_USAGE

    if args.list_boundaries:
        from scripts.kill_test import missing_boundaries, required_boundaries

        required = required_boundaries(spec_dir, args.cfg)
        if not required:
            print(
                f"ERROR: {spec_dir} declares no ports and no invariants. There is no boundary "
                f"to seed a fault at, so the kill test has nothing to measure. Declare the "
                f"effect ports and the model invariants first.",
                file=sys.stderr,
            )
            return EXIT_USAGE
        missing = missing_boundaries(catalog, required)
        covered = {mutant.boundary for mutant in catalog}
        for kind, ref in required:
            mark = "seeded" if (kind, ref) in covered else "NO MUTANT"
            print(f"[{mark:>9}] {kind:<9} {ref}")
        print(
            f"\n{len(required) - len(missing)}/{len(required)} declared boundaries carry a "
            f"seeded fault."
        )
        return 0 if not missing else EXIT_USAGE

    if not args.corpus_command:
        print(
            "ERROR: --corpus-command is required. The kill test runs the distilled corpus "
            "against each seeded mutant; without it there is nothing to kill mutants with, "
            "and reporting a rate would be fabricating one.",
            file=sys.stderr,
        )
        return EXIT_USAGE

    baseline = None
    if getattr(args, "baseline", None):
        try:
            baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR: could not read baseline report: {exc}", file=sys.stderr)
            return EXIT_USAGE

    command = args.corpus_command.split()
    runner = subprocess_case_runner(command, root=root, timeout=args.timeout)

    try:
        report = run_kill_test(
            spec_dir=spec_dir,
            catalog=catalog,
            runner=runner,
            root=root,
            suppressions=suppressions,
            baseline=baseline,
            baseline_source=str(args.baseline) if getattr(args, "baseline", None) else None,
            corpus_command=args.corpus_command,
            cfg_names=args.cfg,
        )
    except KillTestCatalogError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_USAGE

    report.notes.append(
        "This runner spawns a child process per mutant. Under the MF-027 effect oracle a "
        "process.spawn is an unobservable boundary even when a port declares it, so the kill "
        "test must run OUTSIDE the effect sandbox in this repository."
    )

    # Evidence is written whatever the verdict. A report that only appears when
    # the news is good is not evidence.
    if args.out:
        report.write(args.out, catalog)

    if args.format == "json":
        print(json.dumps(report.to_dict(catalog), indent=2, sort_keys=True))
    else:
        print(render_report(report, catalog))
    return report.exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
