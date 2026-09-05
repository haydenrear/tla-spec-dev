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

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

# ONE IMPLEMENTATION, imported rather than repeated.
#
# The checker used to live here in full, which meant the only way to act on what
# it found was to retype the number it had just computed. `G-11` is what that
# costs: it reported *"the anchor is at ...:1430"* and a human copied it across,
# and the copying is the defect source -- three consecutive tickets shipped a
# stale citation before this check existed at all.
#
# `scripts/check_citations.py` now owns the convention and adds `--fix`, which
# rewrites the number when the anchor resolves to exactly ONE line and refuses
# when it resolves to none or several. This file is the gate; that file is the
# tool; neither restates the other. A second copy of a rule is a second thing to
# forget (E-14).
from check_citations import (  # type: ignore[import-not-found]  # noqa: E402
    bare_citations_in,
    problems_in,
    scoped_files,
)


@pytest.mark.parametrize("path", scoped_files(), ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_every_line_citation_resolves_to_the_line_it_cites(path: Path) -> None:
    """The check that would have caught N-3, and did catch eight more.

    When this fails, `python3 scripts/check_citations.py --fix` repairs every
    citation whose anchor is unambiguous. What it leaves is the real question:
    an anchor that appears on several lines, or none, where a repair would have
    to guess which line was meant.
    """
    problems = problems_in(path)
    assert problems == [], (
        "stale or uncheckable citations (try `python3 scripts/check_citations.py --fix`):\n  "
        + "\n  ".join(f"{p.where}: {p.message}" for p in problems)
    )


@pytest.mark.parametrize("path", scoped_files(), ids=lambda p: str(p.relative_to(REPO_ROOT)))
def test_no_citation_leaves_its_file_to_the_reader(path: Path) -> None:
    """A bare line number is refused, because RC-01's was genuinely ambiguous.

    The sentence named one file and the lines belonged to another. A reader
    cannot resolve that, and neither can a checker -- so the convention requires
    the file, and this is the half of it a `--fix` can never repair.
    """
    problems = bare_citations_in(path)
    assert problems == [], "citations with no file:\n  " + "\n  ".join(
        f"{p.where}: {p.message}" for p in problems
    )
