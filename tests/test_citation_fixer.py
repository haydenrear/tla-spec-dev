"""`--fix` repairs what is certain and refuses what is not.

`G-11`'s class: a line-number citation into another file goes stale when that
file grows, and nothing about behaviour changes, so every behavioural check
stays green. The checker already knew the right answer -- it printed *"the
anchor is at ...:1430"* -- and then asked a human to copy it across. **The
copying is the defect source**, and it had produced a stale citation in three
consecutive tickets before the check existed at all.

Eliminating the class means the tool writes the number. The whole risk of that
is a repair that GUESSES, so the two halves are tested together: the
unambiguous case must be repaired, and the ambiguous case must be left alone
with a message saying why.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_citations import fix_file, problems_in  # type: ignore[import-not-found]  # noqa: E402


def _tree(tmp_path: Path, cited: str, citing: str) -> tuple[Path, Path]:
    (tmp_path / "scripts").mkdir()
    target = tmp_path / "scripts" / "target.py"
    target.write_text(cited, encoding="utf-8")
    source = tmp_path / "scripts" / "citer.py"
    source.write_text(citing, encoding="utf-8")
    return source, target


def test_it_repairs_a_citation_whose_anchor_moved(tmp_path) -> None:
    """The `G-11` shape: the anchor is unique, so the number is derivable."""
    source, _ = _tree(
        tmp_path,
        cited="# padding\n" * 5 + "case_root = work_dir / 'case-work'\n",
        citing="# see scripts/target.py:2 (case-work) for the shape\n",
    )
    repaired = fix_file(source, root=tmp_path)
    assert repaired == 1, "the unambiguous citation was not repaired"
    assert "scripts/target.py:6 (case-work)" in source.read_text(), source.read_text()
    assert problems_in(source, root=tmp_path) == []


def test_it_refuses_when_the_anchor_appears_on_several_lines(tmp_path) -> None:
    """A repair that guesses is worse than a red check.

    This is the half that makes the fixer safe to run unattended: it changes
    only what it can derive, and what it leaves is a real question about what
    the author meant.
    """
    source, _ = _tree(
        tmp_path,
        cited="shutil.rmtree(a)\n# pad\nshutil.rmtree(b)\n",
        citing="# see scripts/target.py:2 (shutil.rmtree) here\n",
    )
    before = source.read_text()
    assert fix_file(source, root=tmp_path) == 0, "an ambiguous citation was rewritten"
    assert source.read_text() == before, "the file was touched anyway"

    problems = problems_in(source, root=tmp_path)
    assert len(problems) == 1
    assert not problems[0].repairable
    assert "appears on 2 lines" in problems[0].message, problems[0].message


def test_it_refuses_when_the_anchor_is_gone_entirely(tmp_path) -> None:
    """Zero hits is a deletion, not a move, and the citation may be meaningless now."""
    source, _ = _tree(
        tmp_path,
        cited="nothing here\n",
        citing="# see scripts/target.py:1 (vanished_token) here\n",
    )
    assert fix_file(source, root=tmp_path) == 0
    problems = problems_in(source, root=tmp_path)
    assert len(problems) == 1 and not problems[0].repairable
    assert "appears on 0 lines" in problems[0].message


def test_fixing_is_idempotent(tmp_path) -> None:
    """A second run must find nothing, or the tool is fighting itself."""
    source, _ = _tree(
        tmp_path,
        cited="# padding\n" * 3 + "marker_token = 1\n",
        citing="# see scripts/target.py:1 (marker_token) here\n",
    )
    assert fix_file(source, root=tmp_path) == 1
    assert fix_file(source, root=tmp_path) == 0


def test_the_shipped_checker_runs_and_reports_its_own_repairability() -> None:
    """The CLI is the thing a person actually invokes; run it.

    A library that works and a command that does not is a tool nobody uses. This
    asserts the entry point executes over the real scope and reports, without
    asserting the repository is currently clean -- it is not, and the remaining
    citations are the ambiguous ones a human owes an answer to.
    """
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "check_citations.py")],
        cwd=REPO_ROOT, text=True, capture_output=True, timeout=300,
    )
    assert proc.returncode in (0, 1), proc.stdout + proc.stderr
    combined = proc.stdout + proc.stderr
    assert "citation" in combined.lower(), combined[:400]
