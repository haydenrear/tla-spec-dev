#!/usr/bin/env python3
"""Preserve the prompt AS DISPATCHED, and measure THAT.

    python3 examples/validation/ab/dispatch_record.py record \\
        --dir examples/validation/ab/dispatch/<round> --round <round> \\
        --arm arm_c --source examples/validation/ab/arm_c/PROMPT.md \\
        --dispatched /path/to/exact-bytes-sent.md --provenance preserved
    python3 examples/validation/ab/dispatch_record.py verify \\
        --dir examples/validation/ab/dispatch/<round>
    python3 examples/validation/ab/dispatch_record.py show \\
        --dir examples/validation/ab/dispatch/<round>
    python3 examples/validation/ab/dispatch_record.py demonstrate   # R1

WHY THIS FILE EXISTS -- PA-06-DF-10
-----------------------------------

`check_catalogue.py --arms` measured `examples/validation/ab/arm_c/PROMPT.md`
and reported arm C / arm B = **1.038**, "+3.8%, inside the declared +/-10%
tolerance", with **0 of 109** unique lines carrying architectural vocabulary.

PA-06 did not dispatch that file. It dispatched it with four additions -- a
working-directory preamble, a run hint, three extra do-not-open entries, and a
whole section asking for a `REJECTED.md`. As dispatched the same measures read
**124 unique lines, ratio 1.181, OUTSIDE the tolerance, and 4 of 124 lines
carrying architectural vocabulary** -- two of which are paths PA-06 itself
introduced, which told the arm whose entire job was architectural silence what
the epic was called.

The headline was measured on a file that was not the prompt the arm received.
Nothing recorded the difference, so nothing could notice it until an adversarial
channel reconstructed the dispatch by hand. **A dispatch delta nobody records is
a declaration nothing executes**, which is the class the epic plan's
`declaration_executability_rule` exists for.

WHAT IT DOES, AND WHAT IT REFUSES TO DO
---------------------------------------

`record` writes the **exact bytes sent** into an evidence directory and appends
a row to `dispatch.toml` carrying the digest of those bytes, the digest of the
on-disk source at dispatch time, and the measured size of the delta between
them. `verify` recomputes all three.

A dispatch delta is **not** an error. Adding a working directory to a prompt is
ordinary. What was wrong at PA-06 was that the delta was *unrecorded* and the
number was taken from the wrong file. So a recorded delta is REPORTED, in full,
with line counts, and `--arms` measures the artifact rather than the source.

It goes RED on four things, each of which means a number measured today would
not be a number about what was sent:

  1. the preserved artifact no longer hashes to what was recorded -- somebody
     edited the evidence;
  2. the on-disk source no longer hashes to what it was at dispatch -- a number
     measured on the source today describes a file the arm never saw;
  3. the recorded delta does not match the delta recomputed from the two files
     -- the declaration drifted from the artifacts;
  4. either file is missing.

It gates nothing in the product. Like `check_catalogue.py` it is a
fixture-and-evidence harness: nothing in the toolchain invokes it, it runs when
a human or a measuring ticket runs it, and its exit code says whether the
evidence is self-consistent. Per the epic plan's `no_new_gates_rule` this is not
a new blocking check on anything anyone builds.

PROVENANCE IS A FIELD, AND IT IS NOT DECORATION
-----------------------------------------------

`provenance = "preserved"` means the bytes were captured at dispatch.
`provenance = "reconstruction"` means somebody rebuilt them afterwards from
whatever record survived -- which is strictly weaker evidence, is exactly what
PA-06 had to do, and is the reason this file exists. `verify` prints the
provenance of every row it checks, loudly, and a reconstruction never silently
reads as a preserved dispatch.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import difflib
import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent.parent

MANIFEST_NAME = "dispatch.toml"

#: `preserved` is the only provenance that supports the sentence "this is what
#: the arm received". `reconstruction` is what PA-06 was left with.
PROVENANCES = ("preserved", "reconstruction")

MANIFEST_HEADER = """\
# Dispatched prompts -- the exact bytes each arm received.
#
# APPEND-ONLY, and written by `dispatch_record.py record`. Verify with
# `dispatch_record.py verify --dir <this directory>`.
#
# PA-06-DF-10: the previous round's length-match headline was measured on a file
# that was NOT the prompt the arm received. The arm's prompt was dispatched with
# four unrecorded additions, making the measured ratio 1.181 rather than 1.038
# and leaking the epic's own name into the arm whose whole job was architectural
# silence. What is measured is what is recorded here, not what is on disk.

schema_version = 1
"""


def digest(data: bytes) -> str:
    """The one digest function. Import it; do not re-derive it."""
    return "sha256:" + hashlib.sha256(data).hexdigest()[:16]


def digest_file(path: Path) -> str:
    return digest(path.read_bytes())


def line_delta(source: str, dispatched: str) -> tuple[int, int]:
    """`(lines added, lines removed)` going from source to dispatched.

    Distinct non-blank stripped lines, the SAME measure `check_catalogue.py`
    uses for unique content, so a delta reported here and a length measured
    there are about the same thing.
    """
    src = {ln.strip() for ln in source.splitlines() if ln.strip()}
    dis = {ln.strip() for ln in dispatched.splitlines() if ln.strip()}
    return len(dis - src), len(src - dis)


@dataclass(frozen=True)
class DispatchRecord:
    arm: str
    round: str
    source: str
    source_sha256: str
    artifact: str
    artifact_sha256: str
    provenance: str
    added_lines: int
    removed_lines: int
    recorded_at: str
    note: str = ""

    @property
    def identical_to_source(self) -> bool:
        return self.added_lines == 0 and self.removed_lines == 0


def manifest_path(directory: Path) -> Path:
    return directory / MANIFEST_NAME


def load_records(directory: Path) -> list[DispatchRecord]:
    """Every recorded dispatch in `directory`, in file order."""
    path = manifest_path(directory)
    if not path.is_file():
        return []
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    out = []
    for row in data.get("dispatch", []):
        out.append(DispatchRecord(
            arm=str(row["arm"]),
            round=str(row.get("round", "")),
            source=str(row["source"]),
            source_sha256=str(row["source_sha256"]),
            artifact=str(row["artifact"]),
            artifact_sha256=str(row["artifact_sha256"]),
            provenance=str(row.get("provenance", "preserved")),
            added_lines=int(row.get("added_lines", 0)),
            removed_lines=int(row.get("removed_lines", 0)),
            recorded_at=str(row.get("recorded_at", "")),
            note=str(row.get("note", "")),
        ))
    return out


def record_for(directory: Path, arm: str) -> DispatchRecord | None:
    """The dispatch recorded for `arm`, or None. The LAST row wins."""
    found = [r for r in load_records(directory) if r.arm == arm]
    return found[-1] if found else None


def dispatched_path(directory: Path, rec: DispatchRecord) -> Path:
    return directory / rec.artifact


def _toml_str(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def cmd_record(args: argparse.Namespace) -> int:
    directory = Path(args.dir)
    source = Path(args.source)
    dispatched = Path(args.dispatched)
    if args.provenance not in PROVENANCES:
        print(f"provenance must be one of {PROVENANCES}", file=sys.stderr)
        return 2
    for path in (source, dispatched):
        if not path.is_file():
            print(f"missing {path}", file=sys.stderr)
            return 2

    directory.mkdir(parents=True, exist_ok=True)
    artifact = f"{args.arm}.dispatched.md"
    target = directory / artifact
    payload = dispatched.read_bytes()
    if target.exists() and target.read_bytes() != payload:
        print(
            f"REFUSED: {target} already holds different bytes. A recorded dispatch is "
            f"never overwritten -- record the next one in a new round directory.",
            file=sys.stderr,
        )
        return 3
    target.write_bytes(payload)

    added, removed = line_delta(
        source.read_text(encoding="utf-8"), payload.decode("utf-8")
    )
    path_manifest = manifest_path(directory)
    if not path_manifest.exists():
        path_manifest.write_text(MANIFEST_HEADER, encoding="utf-8")

    try:
        rel_source = str(source.resolve().relative_to(REPO_ROOT))
    except ValueError:
        rel_source = str(source)
    rows = [
        "",
        "[[dispatch]]",
        f"arm = {_toml_str(args.arm)}",
        f"round = {_toml_str(args.round)}",
        f"source = {_toml_str(rel_source)}",
        f"source_sha256 = {_toml_str(digest_file(source))}",
        f"artifact = {_toml_str(artifact)}",
        f"artifact_sha256 = {_toml_str(digest(payload))}",
        f"provenance = {_toml_str(args.provenance)}",
        f"added_lines = {added}",
        f"removed_lines = {removed}",
        f"recorded_at = {_toml_str(args.recorded_at or _dt.date.today().isoformat())}",
    ]
    if args.note:
        rows.append(f"note = {_toml_str(args.note)}")
    with path_manifest.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(rows) + "\n")

    print(f"recorded {args.arm} ({args.provenance}) -> {target}")
    print(f"  dispatch delta vs {rel_source}: +{added} / -{removed} distinct lines")
    if added or removed:
        print("  the ARTIFACT is what gets measured. The source is not what was sent.")
    return 0


def verify(directory: Path, verbose: bool = True) -> list[str]:
    """Recompute everything the manifest declares. Returns the RED reasons."""
    problems: list[str] = []
    records = load_records(directory)
    if verbose:
        print(f"\ndispatch records in {directory}: {len(records)}")
    if not records:
        if verbose:
            print(
                "  NO DISPATCH RECORD. Any prompt measurement for this round is a\n"
                "  measurement of the bytes ON DISK, which PA-06-DF-10 established are\n"
                "  not necessarily the bytes that were sent."
            )
        return problems

    for rec in records:
        artifact = dispatched_path(directory, rec)
        source = REPO_ROOT / rec.source
        label = f"{rec.arm} [{rec.provenance}]"
        if verbose:
            print(f"\n  {label}  round={rec.round or '(unnamed)'}  recorded {rec.recorded_at}")
            if rec.provenance == "reconstruction":
                print(
                    "    RECONSTRUCTION, not a preserved dispatch: these bytes were "
                    "rebuilt\n    afterwards from whatever record survived. Weaker "
                    "evidence, on purpose."
                )
            if rec.note:
                print(f"    note: {rec.note}")

        if not artifact.is_file():
            problems.append(f"{label}: preserved artifact {artifact} is missing")
            continue
        got = digest_file(artifact)
        if got != rec.artifact_sha256:
            problems.append(
                f"{label}: the preserved artifact HAS BEEN EDITED since dispatch "
                f"({rec.artifact_sha256} -> {got}). What was sent is no longer recoverable "
                f"from this directory."
            )
            continue
        if verbose:
            print(f"    artifact {rec.artifact}: unchanged ({got})")

        if not source.is_file():
            problems.append(f"{label}: source {rec.source} no longer exists")
            continue
        source_now = digest_file(source)
        if source_now != rec.source_sha256:
            problems.append(
                f"{label}: THE SOURCE HAS CHANGED SINCE DISPATCH "
                f"({rec.source_sha256} -> {source_now}). `{rec.source}` is not the file "
                f"the arm was dispatched from; a number measured on it today is not a "
                f"number about what was sent. Measure {rec.artifact}."
            )
            continue

        added, removed = line_delta(
            source.read_text(encoding="utf-8"),
            artifact.read_text(encoding="utf-8"),
        )
        if (added, removed) != (rec.added_lines, rec.removed_lines):
            problems.append(
                f"{label}: declared delta +{rec.added_lines}/-{rec.removed_lines} but the "
                f"artifacts differ by +{added}/-{removed}. The declaration drifted from "
                f"the files."
            )
            continue

        if verbose:
            if added or removed:
                print(
                    f"    DISPATCH DELTA vs {rec.source}: "
                    f"+{added} / -{removed} distinct lines."
                )
                print(
                    "    Recorded, not an error -- but the ARTIFACT is what any prompt\n"
                    "    measurement for this round must read."
                )
            else:
                print(f"    dispatched byte-for-byte as {rec.source}")
    return problems


def cmd_verify(args: argparse.Namespace) -> int:
    problems = verify(Path(args.dir))
    if problems:
        print("\nRED -- the dispatch record does not describe the files:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print("\nevidence is self-consistent")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    directory = Path(args.dir)
    for rec in load_records(directory):
        artifact = dispatched_path(directory, rec)
        source = REPO_ROOT / rec.source
        print(f"\n=== {rec.arm} [{rec.provenance}] {rec.round} ===")
        if not (artifact.is_file() and source.is_file()):
            print("  (files missing)")
            continue
        diff = difflib.unified_diff(
            source.read_text(encoding="utf-8").splitlines(),
            artifact.read_text(encoding="utf-8").splitlines(),
            fromfile=rec.source,
            tofile=str(artifact.relative_to(REPO_ROOT)),
            lineterm="",
        )
        for line in diff:
            print("  " + line)
    return 0


#: The demonstrated FAILING INPUTS this checker ships with (R1). Each is a
#: mutation of a self-consistent record, a phrase that must appear in the RED
#: reason, and the sentence saying what a green here would mean.
DEMONSTRATIONS = (
    (
        "artifact_edited",
        "HAS BEEN EDITED",
        "somebody edits the preserved bytes after the fact and the record still "
        "claims they are what was sent",
    ),
    (
        "source_changed",
        "THE SOURCE HAS CHANGED",
        "the file the prompt was built from is edited after dispatch and a number "
        "measured on it today is presented as a number about what was sent -- "
        "PA-06-DF-10 exactly",
    ),
    (
        "declaration_drifted",
        "declared delta",
        "the recorded delta stops describing the two files, which is a declaration "
        "nothing executes",
    ),
    (
        "artifact_missing",
        "is missing",
        "the evidence is gone and the record still reads green",
    ),
)


def demonstrate(verbose: bool = True) -> list[str]:
    """R1: drive this checker's own failing inputs and require it to go RED.

    Not a test that the checker runs -- a re-runnable demonstration that it
    produces the result that would refute it. A checker that cannot go red is
    the defect this epic exists for, and one that only goes red in pytest is a
    checker whose demonstration nobody outside pytest can re-run.
    """
    import shutil  # noqa: PLC0415
    import tempfile  # noqa: PLC0415

    failures: list[str] = []
    for name, phrase, why in DEMONSTRATIONS:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "PROMPT.md"
            src.write_text("# ask\nline one\nline two\n", encoding="utf-8")
            sent = root / "sent.md"
            sent.write_text("# ask\nline one\nline two\nadded at dispatch\n", encoding="utf-8")
            evidence = root / "evidence"
            rc = main([
                "record", "--dir", str(evidence), "--arm", "arm_x",
                "--round", "demonstration", "--source", str(src),
                "--dispatched", str(sent), "--recorded-at", "1970-01-01",
            ])
            if rc != 0:
                failures.append(f"{name}: could not even record a clean dispatch (rc={rc})")
                continue
            clean = verify(evidence, verbose=False)
            if clean:
                failures.append(f"{name}: a self-consistent record reported RED: {clean}")
                continue

            artifact = evidence / "arm_x.dispatched.md"
            if name == "artifact_edited":
                artifact.write_text("# ask\ntampered\n", encoding="utf-8")
            elif name == "source_changed":
                src.write_text("# ask\nline one\nline two\nedited after dispatch\n",
                               encoding="utf-8")
            elif name == "declaration_drifted":
                manifest = manifest_path(evidence)
                manifest.write_text(
                    manifest.read_text(encoding="utf-8").replace(
                        "added_lines = 1", "added_lines = 0"),
                    encoding="utf-8",
                )
            elif name == "artifact_missing":
                artifact.unlink()

            problems = verify(evidence, verbose=False)
            hit = [p for p in problems if phrase in p]
            if verbose:
                status = "RED" if hit else "*** STAYED GREEN ***"
                print(f"  {name:<22} {status}")
                for p in problems:
                    print(f"      {p}")
            if not hit:
                failures.append(
                    f"{name}: STAYED GREEN. Nothing here notices when {why}. "
                    f"Reported problems: {problems or 'none'}"
                )
            shutil.rmtree(evidence, ignore_errors=True)
    return failures


def cmd_demonstrate(args: argparse.Namespace) -> int:
    print("R1 -- the demonstrated failing inputs of the dispatch record:\n")
    failures = demonstrate()
    print()
    if failures:
        print("THIS CHECKER FAILED ITS OWN DEMONSTRATION. It does not go red when the",
              file=sys.stderr)
        print("record stops describing the files, so no green it prints is evidence:",
              file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print(f"All {len(DEMONSTRATIONS)} demonstrated failing inputs went RED, and a")
    print("self-consistent record went green in each. R1 holds for this instrument.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    rec = sub.add_parser("record", help="preserve the exact bytes dispatched to one arm")
    rec.add_argument("--dir", required=True)
    rec.add_argument("--arm", required=True)
    rec.add_argument("--round", default="")
    rec.add_argument("--source", required=True, help="the on-disk prompt it was built from")
    rec.add_argument("--dispatched", required=True, help="a file holding the EXACT bytes sent")
    rec.add_argument("--provenance", default="preserved", choices=list(PROVENANCES))
    rec.add_argument("--note", default="")
    rec.add_argument("--recorded-at", dest="recorded_at", default="")
    rec.set_defaults(func=cmd_record)

    ver = sub.add_parser("verify", help="recompute every digest and delta the manifest declares")
    ver.add_argument("--dir", required=True)
    ver.set_defaults(func=cmd_verify)

    show = sub.add_parser("show", help="diff each recorded dispatch against its source")
    show.add_argument("--dir", required=True)
    show.set_defaults(func=cmd_show)

    dem = sub.add_parser("demonstrate", help="R1: drive this checker's own failing inputs")
    dem.set_defaults(func=lambda a: cmd_demonstrate(a))

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
