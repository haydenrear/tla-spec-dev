#!/usr/bin/env python3
"""Seal-time check: a prediction whose subject the record ALREADY measured.

    python3 examples/validation/check_prediction_seal.py \\
        examples/validation/PREDICTIONS-PA.md
    python3 examples/validation/check_prediction_seal.py --demonstrate
    python3 examples/validation/check_prediction_seal.py <file> --record <json> ...

WHY THIS FILE EXISTS -- PA-06-DF-03
-----------------------------------

`PREDICTIONS-PA.md` sealed **N05**: "ordering stays at zero on every generated
corpus, on every arm ... M09 under `corpus-whole`, `corpus-slice`, `corpus-neg`,
both mappings, three arms. Direction: FLAT at zero for every corpus instrument."

**It was already false when it was sealed, and the record said so.** A kill
table sealed at HP-03 -- committed before the prediction file existed and an
ancestor of the commit that sealed it -- records
`M09-negative-control-ledger-order / corpus-whole = KILLED`. So does the rerun's
sealed table. And `examples/validation/ab/eval/controls.toml` had already
RETIRED M09 as a negative control, in a `[[retired_control]]` block whose stated
reason is that "ordering is therefore fully expressible here, the corpus sees
it, and M09 dies under corpus-whole, corpus-slice-led, map-silent and
map-checking".

N05 was scored FAIL at PA-06, which is what a predictions file is for. What is
not fine is that **nobody had to run anything to know it would fail.** A
prediction is only a prediction if the sealer has not already measured its
subject; otherwise it is a transcription error wearing a prediction's clothes,
and it makes the file's honest failures ("five of fifteen failed") harder to
read as information.

THE PROCEDURE THIS SHIPS, AND WHERE IT APPLIES
----------------------------------------------

Run it **before sealing**, over the predictions file, with the records that
exist at that moment. For every prediction that names a mutant and an
instrument and predicts NO KILL, it looks the cell up and reports:

  ALREADY MEASURED   the record contains a KILL for that exact cell, and the
                     record PRE-DATES the seal (its commit is an ancestor of
                     the sealing commit). This is the PA-06-DF-03 class. Either
                     fix the prediction before sealing, or mark it as a
                     deliberate re-test.
  LATER              the record contains a KILL but was measured AFTER the seal.
                     That is an ordinary falsification and is exactly what a
                     predictions file is for. Reported, never a problem.
  RE-TEST            the prediction says so itself. A row carrying
                     `**Already measured:**` is declaring that it knows, which
                     is the escape PA-06-DF-03's `suggested_fix` asks for, and
                     it is reported with the text of that declaration so a
                     reader can judge it.

**It never edits a sealed file, and it must not be used to.** `PREDICTIONS-PA.md`
is sealed; the correct response to what this prints about it is a finding beside
it, not an amendment. The check is for the NEXT file, at the moment before it is
sealed.

WHAT IT IS NOT
--------------

Not a gate. Nothing in the toolchain invokes it, it blocks no promotion, and no
scorecard reads it. Its exit code is for the human sealing the file.

Not a semantic judgement. It matches mutant IDs and instrument column names
syntactically, so a prediction phrased without either is invisible to it, and a
prediction whose direction is stated in prose it does not recognise is reported
as UNPARSED rather than as clean -- silence and a pass are different claims and
it prints them differently.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11
    import tomli as tomllib  # type: ignore[no-redef]

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent

DEFAULT_CONTROLS = HERE / "ab" / "eval" / "controls.toml"

#: A verdict that says the instrument REACHED the fault. Anything else (a
#: survivor, a red control, an unmeasured cell) is not a contradiction.
KILL_VERDICTS = {"KILLED"}

#: Prose that means "this will not be killed". Deliberately short: a direction
#: this does not recognise is reported UNPARSED, never assumed clean.
NO_KILL_DIRECTION = re.compile(
    r"\b(?:flat at zero|at zero|stays? at zero|zero cells?|zero for every|"
    r"survives?|survived|no kill|nothing (?:is )?killed)\b",
    re.IGNORECASE,
)

#: `M09`, `PA-M14`, `FI-M15`, `N01`. Matched against the mutant ids in a record,
#: which are longer (`M09-negative-control-ledger-order`), by prefix.
MUTANT_ID = re.compile(r"\b((?:PA-|FI-|HP-)?[MN]\d{1,2})\b")

#: A row that declares it already knows. PA-06-DF-03's `suggested_fix`: "or, if
#: it is sealed deliberately as a re-test, say so in the row."
RETEST_MARKER = re.compile(r"\*\*Already measured:?\*\*(.*)", re.IGNORECASE)

SECTION = re.compile(r"^###\s+(?:\*\*)?([A-Z]{1,3}\d{1,3})(?:\*\*)?\s*(?:[-—–]\s*)?(.*)$")

#: The two fields a prediction file's own ground rules require of every row:
#: "Every row has an ID, the INSTRUMENT that settles it, and an expected
#: DIRECTION." Subjects are read from the instrument field and the direction
#: from the direction field -- NOT from the whole section. Reading the whole
#: section is what made the first draft of this checker report N05 against
#: `suite`, which N05's prose names precisely in order to EXCLUDE it.
FIELD = re.compile(
    r"^\*\*(Instrument|Direction|Already measured):?\*\*(.*)", re.IGNORECASE
)


@dataclass
class Prediction:
    id: str
    title: str
    body: str = ""
    mutants: set[str] = field(default_factory=set)
    instruments: set[str] = field(default_factory=set)

    def field_text(self, name: str) -> str:
        """The named `**Field:**` value, WRAPPED continuation lines included.

        A field ends at the first line that finishes a sentence. These files
        hard-wrap, so `**Direction:** FLAT for arm C -- arm C scores at arm A's
        level (1-2), not arm` needs its next line; but P04's
        `**Direction:** killed, 100%.` is finished, and the sentence after it
        ("If either survives...") is commentary. Swallowing the commentary is
        not cosmetic: it is what made the first draft of this checker read P04
        -- a prediction that both controls DIE -- as a prediction that
        something survives.
        """
        out: list[str] = []
        collecting = False
        for line in self.body.splitlines():
            found = FIELD.match(line)
            if found:
                collecting = found.group(1).lower() == name.lower()
                if not collecting:
                    continue
                out.append(found.group(2))
            elif collecting:
                if not line.strip():
                    break
                out.append(line)
            else:
                continue
            if out[-1].rstrip().endswith((".", "!")):
                break
        return " ".join(out).strip()

    @property
    def predicts_no_kill(self) -> bool:
        return bool(NO_KILL_DIRECTION.search(self.field_text("Direction")))

    @property
    def retest_note(self) -> str:
        return self.field_text("Already measured")


@dataclass
class Record:
    path: Path
    per_mutant: dict[str, dict[str, str]]
    commit: str | None
    predates_seal: bool | None

    @property
    def columns(self) -> set[str]:
        return {c for cells in self.per_mutant.values() for c in cells}


def _git(*argv: str) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", "-C", str(REPO_ROOT), *argv], capture_output=True, text=True, check=False
    )
    return proc.returncode, proc.stdout.strip()


_GIT_MEMO: dict[tuple[str, str], object] = {}


def introducing_commit(path: Path) -> str | None:
    """The commit that ADDED `path` -- when the record came into existence."""
    key = ("introduced", str(path))
    if key not in _GIT_MEMO:
        rc, out = _git("log", "--diff-filter=A", "--format=%H", "--", str(path))
        if rc != 0 or not out:
            rc, out = _git("log", "--format=%H", "--", str(path))
        _GIT_MEMO[key] = out.splitlines()[-1] if out else None
    return _GIT_MEMO[key]  # type: ignore[return-value]


def sealing_commit(path: Path) -> str | None:
    """The commit that last touched the predictions file -- when it was sealed."""
    rc, out = _git("log", "-1", "--format=%H", "--", str(path))
    return out or None


def is_ancestor(older: str, newer: str) -> bool | None:
    key = ("ancestor", f"{older}..{newer}")
    if key not in _GIT_MEMO:
        rc, _ = _git("merge-base", "--is-ancestor", older, newer)
        _GIT_MEMO[key] = None if rc > 1 else rc == 0
    return _GIT_MEMO[key]  # type: ignore[return-value]


def parse_predictions(text: str) -> list[Prediction]:
    """Split on `### <ID> — <title>` headings. One section, one prediction."""
    out: list[Prediction] = []
    current: Prediction | None = None
    lines: list[str] = []
    for line in text.splitlines():
        found = SECTION.match(line)
        if found:
            if current is not None:
                current.body = "\n".join(lines)
                out.append(current)
            current = Prediction(id=found.group(1), title=found.group(2).strip())
            lines = []
        elif current is not None:
            lines.append(line)
    if current is not None:
        current.body = "\n".join(lines)
        out.append(current)
    return out


def attach_subjects(preds: list[Prediction], columns: set[str]) -> None:
    """Fill in the mutants and instrument columns each prediction's INSTRUMENT
    field names.

    Instrument columns are matched against the names actually present in the
    records, plus a family rule so `corpus-slice` reaches `corpus-slice-led`
    and `corpus-slice-res` -- N05 names the family, and a checker that only
    matched exact strings would miss the row it exists for.

    Read from the instrument field and the title alone. A mutant mentioned in
    the surrounding prose is not a subject: N05's prose names `suite` in order
    to say the suite DOES kill M09, and a checker that counted that as a
    prediction about `suite` would report the row for the one thing it got
    right.
    """
    ordered = sorted(columns, key=len, reverse=True)
    section_ids = {p.id for p in preds}
    for pred in preds:
        haystack = f"{pred.title}\n{pred.field_text('Instrument')}"
        # A token that is ALSO a section id in this file is ambiguous: this
        # project's prediction ids (`N05`) and its mutant ids
        # (`N01-negative-control-...`) share a namespace. Dropped from the
        # subjects and reported, never silently resolved either way.
        pred.mutants = {
            m.group(1) for m in MUTANT_ID.finditer(haystack)
            if m.group(1) not in section_ids
        }
        named: set[str] = set()
        for column in ordered:
            if re.search(rf"\b{re.escape(column)}\b", haystack):
                named.add(column)
        for token in re.findall(r"\b[a-z]+(?:-[a-z]+)+\b", haystack):
            for column in ordered:
                if column.startswith(token + "-"):
                    named.add(column)
        pred.instruments = named


def load_record(path: Path, seal: str | None) -> Record | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    per_mutant = data.get("per_mutant")
    if not isinstance(per_mutant, dict):
        return None
    commit = introducing_commit(path)
    predates = None
    if commit and seal:
        predates = is_ancestor(commit, seal)
    return Record(path=path, per_mutant=per_mutant, commit=commit, predates_seal=predates)


def retired_controls(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return list(data.get("retired_control", []))


def matches(mutant_key: str, named: str) -> bool:
    return mutant_key == named or mutant_key.startswith(named + "-")


@dataclass
class Row:
    kind: str            # ALREADY MEASURED | LATER | RE-TEST | UNPARSED
    prediction: str
    detail: str


def check(
    predictions_path: Path,
    records: list[Path],
    controls_path: Path = DEFAULT_CONTROLS,
    verbose: bool = True,
) -> list[Row]:
    seal = sealing_commit(predictions_path)
    loaded = [r for r in (load_record(p, seal) for p in records) if r is not None]
    columns: set[str] = set()
    for rec in loaded:
        columns |= rec.columns
    preds = parse_predictions(predictions_path.read_text(encoding="utf-8"))
    attach_subjects(preds, columns)

    if verbose:
        print(f"predictions: {predictions_path}")
        print(f"  sealed at: {seal or '(not committed)'}")
        print(f"  records read: {len(loaded)} of {len(records)} "
              f"({sum(1 for r in loaded if r.predates_seal)} pre-date the seal)")
        print(f"  sections parsed: {len(preds)}")

    rows: list[Row] = []
    for pred in preds:
        if not pred.predicts_no_kill:
            continue
        subject = f"{pred.id} ({', '.join(sorted(pred.mutants)) or 'no mutant named'}"
        subject += f" x {', '.join(sorted(pred.instruments))})" if pred.instruments else ")"
        if not (pred.mutants and pred.instruments):
            missing = " nor ".join(
                part for part, ok in (("a mutant", pred.mutants),
                                      ("an instrument column", pred.instruments)) if not ok
            )
            rows.append(Row(
                "UNPARSED", pred.id,
                f"{subject}: predicts no kill, but its **Instrument:** field names neither "
                f"{missing} that appears in any record. NOT CHECKED -- and silence here is "
                f"not a pass. A prediction whose subject cannot be looked up is one nothing "
                f"can contradict at seal time.",
            ))
            continue

        note = pred.retest_note
        # Cell -> the records carrying it. Deduplicated by CELL, because the
        # same table is archived in several places and a report that lists one
        # cell thirty times buries the one it exists to show.
        before: dict[str, list[Path]] = {}
        after: dict[str, list[Path]] = {}
        for rec in loaded:
            for key, cells in rec.per_mutant.items():
                if not any(matches(key, m) for m in pred.mutants):
                    continue
                for column, verdict in cells.items():
                    if column not in pred.instruments or verdict not in KILL_VERDICTS:
                        continue
                    cell = f"{key} / {column} = {verdict}"
                    (before if rec.predates_seal else after).setdefault(cell, []).append(rec.path)

        hits = [
            f"{cell}  ({len(paths)} record(s), e.g. {paths[0].relative_to(REPO_ROOT)})"
            for cell, paths in sorted(before.items())
        ]
        for retired in retired_controls(controls_path):
            key = str(retired.get("mutant", ""))
            if any(matches(key, m) for m in pred.mutants):
                hits.append(
                    f"{key} was RETIRED as a {retired.get('was')} control in "
                    f"{controls_path.relative_to(REPO_ROOT)} -- "
                    f"{' '.join(str(retired.get('reason', '')).split())[:200]}"
                )

        if hits and note:
            rows.append(Row("RE-TEST", pred.id, f"{subject}: declared -- {note}"))
        elif hits:
            rows.append(Row(
                "ALREADY MEASURED", pred.id,
                f"{subject}: the record ALREADY contained a kill for this cell when the "
                f"file was sealed:\n" + "\n".join(f"        {h}" for h in hits),
            ))
        for cell, paths in sorted(after.items()):
            rows.append(Row(
                "LATER", pred.id,
                f"{subject}: {cell}  ({len(paths)} record(s), e.g. "
                f"{paths[0].relative_to(REPO_ROOT)})",
            ))
    return rows


def report(rows: list[Row]) -> int:
    already = [r for r in rows if r.kind == "ALREADY MEASURED"]
    for kind in ("ALREADY MEASURED", "RE-TEST", "LATER", "UNPARSED"):
        chosen = [r for r in rows if r.kind == kind]
        if not chosen:
            continue
        print(f"\n{kind}:")
        for row in chosen:
            print(f"  {row.detail}")
    print()
    if already:
        print("NOT SEALABLE AS WRITTEN. The prediction(s) above are contradicted by")
        print("measurements that existed BEFORE the seal. A prediction is only a")
        print("prediction if the sealer has not already measured its subject: correct")
        print("the row, or declare it a deliberate re-test with `**Already measured:**`.")
        return 1
    print("No prediction is contradicted by a measurement that pre-dates the seal.")
    print("(That is not a claim that any of them is right -- only that none of them")
    print("was already known wrong.)")
    return 0


def default_records() -> list[Path]:
    return sorted(
        p for p in (REPO_ROOT / "specs").rglob("kill-table*.json") if p.is_file()
    )


# ---------------------------------------------------------------------------
# R1 -- the demonstrated failing input, taken from the real record
# ---------------------------------------------------------------------------

#: N05 in the sealed `PREDICTIONS-PA.md`. This is not a fixture: it is the
#: prediction PA-06-DF-03 was filed about, checked against the kill tables that
#: were already in the tree when PA-01 sealed it.
DEMONSTRATION_FILE = HERE / "PREDICTIONS-PA.md"
DEMONSTRATION_ID = "N05"


def demonstrate(verbose: bool = True) -> list[str]:
    """R1: the checker must go RED on the row this project already got wrong.

    Two inputs, one green and one red, both from the shipped record:

      * `PREDICTIONS-PA.md` -- N05 must be reported ALREADY MEASURED;
      * the same file with N05's subject removed -- must be clean, so the red
        is attributable to N05 rather than to the checker disliking the file.
    """
    import tempfile  # noqa: PLC0415

    failures: list[str] = []
    records = default_records()
    rows = check(DEMONSTRATION_FILE, records, verbose=False)
    red = [r for r in rows if r.kind == "ALREADY MEASURED" and r.prediction == DEMONSTRATION_ID]
    if verbose:
        print(f"  {'PREDICTIONS-PA.md as sealed':<44} "
              f"{'RED on ' + DEMONSTRATION_ID if red else '*** STAYED GREEN ***'}")
        for row in red:
            print(f"      {row.detail}")
    if not red:
        failures.append(
            f"{DEMONSTRATION_ID} was NOT reported. This checker cannot produce the result "
            f"that would refute it, so no clean report it prints is evidence. Rows: "
            f"{[(r.kind, r.prediction) for r in rows]}"
        )

    text = DEMONSTRATION_FILE.read_text(encoding="utf-8")
    without = re.sub(
        r"^### N05 .*?(?=^### )", "### N05 — removed for the demonstration\n\n",
        text, count=1, flags=re.MULTILINE | re.DOTALL,
    )
    with tempfile.TemporaryDirectory() as tmp:
        scrubbed = Path(tmp) / "PREDICTIONS-SCRUBBED.md"
        scrubbed.write_text(without, encoding="utf-8")
        rows2 = check(scrubbed, records, verbose=False)
        still = [r for r in rows2 if r.kind == "ALREADY MEASURED"
                 and r.prediction == DEMONSTRATION_ID]
    if verbose:
        print(f"  {'the same file with N05 removed':<44} "
              f"{'*** STILL RED ***' if still else 'green'}")
    if still:
        failures.append(
            f"{DEMONSTRATION_ID} was still reported after its section was removed, so the "
            f"red is not attributable to that row."
        )
    return failures


def cmd_demonstrate() -> int:
    print("R1 -- the demonstrated failing input, on the real record:\n")
    failures = demonstrate()
    print()
    if failures:
        print("THIS CHECKER FAILED ITS OWN DEMONSTRATION:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print("The checker reports the one prediction this project is already known to")
    print("have sealed against data that falsified it, and reports nothing once that")
    print("row is removed. R1 holds for this instrument.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("predictions", nargs="?", type=Path)
    parser.add_argument("--record", type=Path, action="append", default=[],
                        help="a kill table to read (default: every kill-table*.json "
                             "under specs/)")
    parser.add_argument("--controls", type=Path, default=DEFAULT_CONTROLS)
    parser.add_argument("--demonstrate", action="store_true",
                        help="R1: run this checker's own demonstrated failing input")
    args = parser.parse_args(argv)

    if args.demonstrate:
        return cmd_demonstrate()
    if args.predictions is None:
        parser.error("a predictions file is required unless --demonstrate is given")
    records = args.record or default_records()
    return report(check(args.predictions, records, args.controls))


if __name__ == "__main__":
    raise SystemExit(main())
