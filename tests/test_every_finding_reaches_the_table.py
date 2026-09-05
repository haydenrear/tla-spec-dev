"""A finding written up and not placed is a finding the matrix cannot see.

Eleven `H-` findings were written up in full in
`examples/validation/agent_rounds/SELF-IMPROVEMENT-MATRIX.md` and appeared in no
total in it. They were not hidden -- each had its own section, some of them long
ones -- and the file still reported conservation over a set that excluded them.
**Nobody noticed until the repository's owner asked whether the round's bugs had
been attributed.**

The cause is structural, not clerical. `SKILL.md` makes the epic agent the
matrix's single writer, so that naming stays stable without a taxonomy or a
merge step. That rule has no provision for the case where **the writer is also
the author of the thing being measured**: this round, every defect in the
harness was filed by the person who wrote the harness, and they landed in prose
while defects in the toolchain landed in rows. Not by decision -- by category
drift, one finding at a time.

`CA-01` dispatches judges blind to the operator's conclusions. Nothing
dispatches an auditor blind to the matrix-writer's classifications. This test is
the cheap half of that: it does not judge whether a placement is RIGHT, only
that a finding written up was placed at all.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MATRIX = REPO_ROOT / "examples" / "validation" / "agent_rounds" / "SELF-IMPROVEMENT-MATRIX.md"

#: A finding id as this record writes them: `E-09`, `G-04b`, `H-06a`, `SV-06`.
_ID = r"[A-Z]{1,3}-\d{2,3}[a-z]?"
#: A section heading that WRITES UP a finding, e.g. "### `H-05` — the classifier..."
_WRITEUP = re.compile(r"^#{2,4}\s+`(" + _ID + r")`", re.M)
#: The `findings` column of the attribution table. Rows begin with an anchor in
#: backticks and carry a pipe-separated list of ids.
_TABLE_ROW = re.compile(r"^\|\s*\*{0,2}`(?:TlaSpecDevCli\.|UNMODELED/)[^`]+`\*{0,2}\s*\|(.+)$", re.M)


def _written_up() -> set[str]:
    return set(_WRITEUP.findall(MATRIX.read_text(encoding="utf-8")))


def _placed() -> set[str]:
    placed: set[str] = set()
    for row in _TABLE_ROW.findall(MATRIX.read_text(encoding="utf-8")):
        placed.update(re.findall(_ID, row))
    return placed


def test_the_matrix_has_rows_and_writeups_to_compare() -> None:
    """Guard the guard: two empty sets are equal and prove nothing."""
    written, placed = _written_up(), _placed()
    assert len(written) >= 5, f"only {len(written)} write-ups found; the parser has drifted"
    assert len(placed) >= 10, f"only {len(placed)} placed ids found; the parser has drifted"


def test_every_finding_written_up_is_placed_in_the_table() -> None:
    """The failure this file exists for, stated as a predicate.

    A finding with its own section and no row is invisible to every number the
    matrix reports -- including `conservation`, which is the one property this
    table claims. Eleven of them accumulated before anyone asked.
    """
    unplaced = sorted(_written_up() - _placed())
    assert not unplaced, (
        "these findings are written up in the matrix and appear in no row of the "
        "attribution table, so no total in the file counts them:\n  "
        + "\n  ".join(unplaced)
        + "\n\nPlace each one against a `<Module>.<Action>` or an `UNMODELED/<bin>`. "
        "If it genuinely belongs to none, open the bin -- `bug_attribution.md` §7c: "
        "refusing to add is the escape conservation cannot see."
    )


def test_a_range_in_the_table_is_spelled_out_or_the_count_is_wrong() -> None:
    """`E-04`—`E-08` in a cell hides three ids from every id-level check.

    The `GenerateCases` row uses a range. That is readable, and it means this
    file's own placement check cannot see `E-05`, `E-06` or `E-07`. Rather than
    forbid ranges, this asserts the endpoints are placed and names what a range
    costs, so the next reader knows the id-level guarantee has a hole in exactly
    one row.
    """
    text = MATRIX.read_text(encoding="utf-8")
    ranges = re.findall(r"`(" + _ID + r")`[—-]+`(" + _ID + r")`", text)
    for low, high in ranges:
        assert low in _placed() and high in _placed(), (
            f"the range {low}-{high} names endpoints that are not themselves placed"
        )
