"""RC-02 (MF-026 round-3 N-3): every internal line citation is checked against
the line it cites.

**The recurrence is the finding, not the three digits.** RC-01's docstring at
`scripts/generate_cases_from_tlc_dump.py` cited `:115`, `:139` and `:881-882`
for lines that were `:116`, `:140` and `:882-883` -- stale in the commit that
wrote them. That was the third consecutive ticket to ship a stale internal
citation (EV-01-DF-03 in `architecture_components.yaml`; G-5 and G-7 in the
three `spec_manifest.yaml` files), and the audit's own note was that a pattern
repeating three times "argues for a check rather than more care".

## The convention this test enforces

A citation is `path/to/file.ext:<line>[-<line>] (<anchor>)`. Both halves are
required and both are checked:

1. **File-qualified.** A bare `:<line>` is REFUSED. RC-01's stale citation was
   bare, and the file it meant was genuinely ambiguous: the sentence named
   `scripts/tla_spec_dev.py` immediately before it while the lines belonged to
   the file the docstring was in. A reader cannot resolve that, and neither can
   a checker.
2. **Content-anchored.** The parenthesised token must appear on one of the
   cited lines. This is what catches a one-line shift, which is the whole of
   the N-3 defect -- a "does the line exist" check passes on `:115` and on
   `:116` alike, and so would have caught nothing.

Applying the convention to the surface below found **eight further stale
citations that no one had reported**, including one in the same comment block
RC-01 wrote (`install-tla-spec-dev.sh:22` for a write on line 23). They are
fixed in the same commit as this test.

## Scope, stated rather than assumed

The scoped surface is the in-model source the MF-026 audit enumerates:
`scripts/*.py`, the three `spec_manifest.yaml` files and the three
`TlaSpecDevCli.tla` modules. `tests/`, `references/`, `specs/results/` and the
planning YAML are deliberately OUT of scope: results and history are
append-only records of what was true when written, and rewriting them to satisfy
a checker would be the opposite of the point. Widening the scope is a decision
for whoever wants the coverage, not a default.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

#: The surface whose citations are checked. Globs, resolved against the repo.
CITATION_SCOPE = (
    "scripts/*.py",
    "specs/current/spec_manifest.yaml",
    "specs/desired_program_model/spec_manifest.yaml",
    "specs/program_model/spec_manifest.yaml",
    "specs/current/TlaSpecDevCli.tla",
    "specs/desired_program_model/TlaSpecDevCli.tla",
    "specs/program_model/TlaSpecDevCli.tla",
)

CITED_SUFFIXES = "py|sh|tla|yaml|yml|toml|cfg|kts|md"

#: `path/to/file.ext:12` or `file.ext:12-34`, followed by ` (anchor)`.
CITATION = re.compile(
    rf"(?P<file>[A-Za-z_][\w./-]*\.(?:{CITED_SUFFIXES}))"
    r":(?P<start>\d+)(?:-(?P<end>\d+))?"
    r"(?:\s*\((?P<anchor>[^()\n]{1,80})\))?"
)

#: A `:<line>` with no file in front of it. Python slices (`errors[:20]`,
#: `digest[:32]`) are the dominant false positive and are excluded by the `[`
#: in the lookbehind; so are `::`, `http://host:8080` and `12:30`.
BARE_CITATION = re.compile(r"(?<![\w.:/\[\d])(?<!\.\.)\:(\d{2,4})\b")


def scoped_files() -> list[Path]:
    found: list[Path] = []
    for pattern in CITATION_SCOPE:
        found.extend(sorted(REPO_ROOT.glob(pattern)))
    assert found, "citation scope matched no files"
    return found


def resolve_cited(name: str) -> Path | None:
    """A cited path, resolved from the repo root or by unique basename."""
    direct = REPO_ROOT / name
    if direct.is_file():
        return direct
    matches = [
        path
        for path in REPO_ROOT.rglob(Path(name).name)
        if path.is_file() and ".git" not in path.parts and "generated" not in path.parts
    ]
    return matches[0] if len(matches) == 1 else None


@pytest.mark.parametrize("path", scoped_files(), ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_every_line_citation_resolves_to_the_line_it_cites(path: Path) -> None:
    """The check that would have caught N-3, and did catch eight more."""
    text = path.read_text(encoding="utf-8")
    problems: list[str] = []

    for match in CITATION.finditer(text):
        source_line = text[: match.start()].count("\n") + 1
        where = f"{path.relative_to(REPO_ROOT)}:{source_line}"
        cited_name = match.group("file")
        start = int(match.group("start"))
        end = int(match.group("end") or start)
        anchor = match.group("anchor")

        if anchor is None:
            problems.append(
                f"{where}: citation `{cited_name}:{match.group('start')}"
                f"{'-' + match.group('end') if match.group('end') else ''}` has no "
                "(anchor). Write `file.py:12 (some_token_on_that_line)` -- an "
                "unanchored line number cannot be checked and goes stale silently."
            )
            continue

        cited = resolve_cited(cited_name)
        if cited is None:
            problems.append(f"{where}: cited file {cited_name!r} does not resolve to one file")
            continue

        lines = cited.read_text(encoding="utf-8").splitlines()
        if not 1 <= start <= end <= len(lines):
            problems.append(
                f"{where}: {cited_name}:{start}-{end} is outside the file "
                f"({len(lines)} lines)"
            )
            continue

        if not any(anchor in line for line in lines[start - 1 : end]):
            hits = [
                index + 1 for index, line in enumerate(lines) if anchor in line
            ]
            hint = f" -- the anchor is at {cited_name}:{hits[0]}" if len(hits) == 1 else ""
            problems.append(
                f"{where}: {cited_name}:{start}"
                f"{'-' + str(end) if end != start else ''} does not contain the "
                f"anchor {anchor!r}{hint}"
            )

    assert problems == [], "stale or uncheckable citations:\n  " + "\n  ".join(problems)


@pytest.mark.parametrize("path", scoped_files(), ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_no_citation_leaves_its_file_to_the_reader(path: Path) -> None:
    """A bare `:115` is refused, because RC-01's was genuinely ambiguous.

    Its sentence named `scripts/tla_spec_dev.py` and then wrote ", never saw
    the java spawn at :115" about a line in the file the docstring was in. Both
    readings are defensible, which means neither is a citation.
    """
    text = path.read_text(encoding="utf-8")
    #  Blank out the anchored citations first: `file.py:12-34` legitimately
    #  contains a `-34` and must not be re-reported as a bare citation.
    masked = CITATION.sub(lambda m: " " * len(m.group(0)), text)

    offenders = [
        f"{path.relative_to(REPO_ROOT)}:{masked[: m.start()].count(chr(10)) + 1}: "
        f"bare `:{m.group(1)}` -- name the file it belongs to"
        for m in BARE_CITATION.finditer(masked)
    ]
    assert offenders == [], "unqualified line citations:\n  " + "\n  ".join(offenders)
