"""SS-05. `blind_dispatch check`'s UNDECIDED branch was DEAD CODE. Now it fires.

`CA-10-DF-24`, first entry. The guard read

    if not any(groups.values()):
        print("UNDECIDED: no needles could be derived. Not a pass.")
        return 2

and `groups["harness block label"]` is `list(HARNESS_MARKERS)` -- four hard-coded
strings in the module -- so `any(...)` was ALWAYS true and the branch could never
be reached. Both classes that are actually derived from the tree fail silently to
`[]`: `memory_needles` returns `[]` when the memory file is absent and
`commit_needles` returns `[]` on `SubprocessError`/`OSError`. Measured on the
shipped code:

    check <400-byte report> --repo /tmp/notarepo --memory /nonexistent/MEMORY.md
    -> needles 4 harness block label
       needles 0 operator memory entry
       needles 0 repository commit subject
       WEAK PASS, exit 0

Both live needle classes derived nothing and the round was passed. This is the
half of `CA-00-DF-04` that survived its own repair: the empty-subject half was
fixed by `MIN_REPORT_BYTES`/`DISPATCH_FAILURE_SIGNATURES`, and this one was not.

WHY A CONSTANT MAY NOT KEEP A GUARD ALIVE. The question the guard asks is "did
anything get looked up?". A tuple of literals in the same file answers "yes"
without looking anything up, so it cannot be evidence for the proposition. The
fix is the one `CA-10`'s own table prescribes: test the DERIVED classes only.

NON-VACUITY IS THE WHOLE RISK HERE, and it is asserted below: a guard that
refused whenever ANY class was empty would refuse every honest run whose operator
had no memory index, which would be a new false REFUSAL traded for the old false
PASS. One derivable class is enough to decide the round.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INSTRUMENT = ROOT / "examples" / "validation" / "instruments" / "blind_dispatch.py"

sys.path.insert(0, str(INSTRUMENT.parent))
import blind_dispatch as BD  # noqa: E402


def check(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(INSTRUMENT), "check", *args],
        capture_output=True, text=True, cwd=str(ROOT), timeout=300,
    )


def honest_report(tmp_path: Path) -> Path:
    """A subject well above `MIN_REPORT_BYTES` that names none of the needles."""
    path = tmp_path / "report.md"
    path.write_text("q" * 400, encoding="utf-8")
    return path


def test_the_guard_no_longer_consults_a_class_that_is_a_constant() -> None:
    """The mechanism, asserted directly rather than inferred from output.

    `HARNESS_MARKERS` is non-empty by construction and is not in the derived set,
    so no run can be decided by it alone.
    """
    assert BD.HARNESS_MARKERS, "the literal class is empty; this test is stale"
    assert "harness block label" not in BD.DERIVED_NEEDLE_CLASSES
    assert set(BD.DERIVED_NEEDLE_CLASSES) == {
        "operator memory entry", "repository commit subject"
    }


def test_both_derived_classes_empty_is_UNDECIDED_and_exit_2(tmp_path) -> None:
    """THE DEMONSTRATED ABSENT-INPUT CASE. Failing before, passing after.

    Before: `WEAK PASS`, exit 0. After: `UNDECIDED`, exit 2. The subject is a
    real 400-byte report, the memory path is absent and `--repo` is not a git
    repository, which is the exact reproduction `CA-10-DF-24` records.
    """
    done = check(str(honest_report(tmp_path)),
                 "--repo", str(tmp_path / "notarepo"),
                 "--memory", str(tmp_path / "nonexistent" / "MEMORY.md"))
    combined = done.stdout + done.stderr

    assert done.returncode == 2, combined
    assert "UNDECIDED: no needles could be derived from this tree" in combined
    assert "Not a pass" in combined
    assert "WEAK PASS" not in combined
    # It names WHICH classes came back empty, so the answer is readable without
    # re-deriving it. An UNDECIDED that does not say what was undecidable is the
    # shape SS-06-DF-05 was filed about.
    assert "operator memory entry" in combined
    assert "repository commit subject" in combined
    assert "hard-coded literals" in combined


def test_ONE_derivable_class_still_decides_the_round(tmp_path) -> None:
    """NON-VACUITY, and the false-refusal this repair could have introduced.

    `--repo` is this repository, so commit subjects derive; the memory file is
    still absent. That is the ordinary case for a ticket worktree and it must
    still produce a verdict, marked WEAK. A guard that refused here would have
    traded a false PASS for a false REFUSAL, which is not a repair.
    """
    done = check(str(honest_report(tmp_path)),
                 "--repo", str(ROOT),
                 "--memory", str(tmp_path / "nonexistent" / "MEMORY.md"))
    combined = done.stdout + done.stderr

    assert done.returncode == 0, combined
    assert "WEAK PASS" in combined
    assert "UNDECIDED" not in combined
    assert "0 memory needles" in combined, (
        "the weakness must still be announced -- it is the reason WEAK exists"
    )


def test_the_empty_subject_half_of_CA_00_DF_04_still_refuses(tmp_path) -> None:
    """The half that was already repaired is not traded for the half that was not.

    An empty subject and a failed dispatch must still exit 2 through the
    precondition, BEFORE any needle is counted -- a different branch from the one
    this ticket repaired, and both must hold.
    """
    empty = tmp_path / "empty.md"
    empty.write_text("", encoding="utf-8")
    done = check(str(empty), "--repo", str(ROOT))
    assert done.returncode == 2
    assert "the subject is empty" in done.stdout + done.stderr

    failed = tmp_path / "failed.md"
    failed.write_text("Error: Invalid API key\n" + "z" * 400, encoding="utf-8")
    done = check(str(failed), "--repo", str(ROOT))
    assert done.returncode == 2
    assert "failed dispatch" in done.stdout + done.stderr
