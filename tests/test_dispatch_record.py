"""The dispatched prompt is preserved, and the preservation can go RED.

PA-06-DF-10: `check_catalogue.py --arms` measured
`examples/validation/ab/arm_c/PROMPT.md` and reported arm C / arm B = **1.038**,
"inside the declared +/-10% tolerance", with **0 of 109** unique lines carrying
architectural vocabulary. PA-06 dispatched that file with four unrecorded
additions. Measured on the bytes that were actually sent, the same three numbers
are **1.181, OUTSIDE the tolerance, and 4 of 124** -- two of the four being paths
PA-06 itself introduced, which told the arm whose entire job was architectural
silence what the epic was called.

R1 says an instrument ships with a demonstrated failing input. This one gets two
kinds:

* **synthetic** -- `dispatch_record.demonstrate()` drives four mutations of a
  self-consistent record and requires a distinct RED for each;
* **historical** -- the same harness, over the real record, reports one set of
  numbers from the file on disk and a different set from the bytes that were
  sent, and only the second set trips the tolerance. Green and red from one
  checker on two real inputs.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
AB = REPO_ROOT / "examples" / "validation" / "ab"
for _p in (str(REPO_ROOT), str(AB)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import check_catalogue  # noqa: E402
import dispatch_record  # noqa: E402

PA_DISPATCH = AB / "dispatch" / "ports-as-adapters"
RECONSTRUCTION = (
    REPO_ROOT / "specs" / "results" / "scorecards" / "ports-as-adapters"
    / "measure" / "arm_c_dispatched_prompt.md"
)


# ---------------------------------------------------------------------------
# the record itself
# ---------------------------------------------------------------------------


def test_a_clean_record_round_trips(tmp_path: Path) -> None:
    source = tmp_path / "PROMPT.md"
    source.write_text("# ask\nalpha\nbeta\n", encoding="utf-8")
    sent = tmp_path / "sent.md"
    sent.write_text("# ask\nalpha\nbeta\ngamma\n", encoding="utf-8")
    evidence = tmp_path / "evidence"

    assert dispatch_record.main([
        "record", "--dir", str(evidence), "--arm", "arm_z", "--round", "t",
        "--source", str(source), "--dispatched", str(sent),
    ]) == 0
    rec = dispatch_record.record_for(evidence, "arm_z")
    assert rec is not None
    assert (rec.added_lines, rec.removed_lines) == (1, 0)
    assert rec.provenance == "preserved"
    assert not rec.identical_to_source
    assert dispatch_record.dispatched_path(evidence, rec).read_bytes() == sent.read_bytes()
    assert dispatch_record.verify(evidence, verbose=False) == []


def test_a_byte_identical_dispatch_records_a_zero_delta(tmp_path: Path) -> None:
    source = tmp_path / "PROMPT.md"
    source.write_text("# ask\nalpha\n", encoding="utf-8")
    evidence = tmp_path / "evidence"
    dispatch_record.main([
        "record", "--dir", str(evidence), "--arm", "arm_z",
        "--source", str(source), "--dispatched", str(source),
    ])
    rec = dispatch_record.record_for(evidence, "arm_z")
    assert rec is not None and rec.identical_to_source
    assert dispatch_record.verify(evidence, verbose=False) == []


def test_recording_over_different_bytes_is_refused(tmp_path: Path) -> None:
    """A recorded dispatch is evidence. Overwriting it destroys the only copy."""

    source = tmp_path / "PROMPT.md"
    source.write_text("# ask\nalpha\n", encoding="utf-8")
    other = tmp_path / "other.md"
    other.write_text("# ask\nbeta\n", encoding="utf-8")
    evidence = tmp_path / "evidence"
    assert dispatch_record.main([
        "record", "--dir", str(evidence), "--arm", "arm_z",
        "--source", str(source), "--dispatched", str(source),
    ]) == 0
    assert dispatch_record.main([
        "record", "--dir", str(evidence), "--arm", "arm_z",
        "--source", str(source), "--dispatched", str(other),
    ]) == 3


# ---------------------------------------------------------------------------
# R1 -- the demonstrated failing inputs
# ---------------------------------------------------------------------------


def test_every_demonstrated_failing_input_goes_red() -> None:
    failures = dispatch_record.demonstrate(verbose=False)
    assert failures == [], (
        "the dispatch record does not go red when it stops describing the files, so "
        f"no green it prints is evidence: {failures}"
    )


def test_the_demonstration_covers_the_four_ways_a_record_stops_being_true() -> None:
    names = {name for name, _phrase, _why in dispatch_record.DEMONSTRATIONS}
    assert names == {
        "artifact_edited", "source_changed", "declaration_drifted", "artifact_missing",
    }


def test_the_demonstration_is_runnable_from_the_command_line() -> None:
    """R1 asks for a re-runnable demonstration, not one only pytest can run."""

    proc = subprocess.run(
        [sys.executable, str(AB / "dispatch_record.py"), "demonstrate"],
        capture_output=True, text=True, check=False, cwd=str(REPO_ROOT),
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "R1 holds for this instrument" in proc.stdout


@pytest.mark.parametrize(
    "mutation,phrase",
    [
        ("artifact", "HAS BEEN EDITED"),
        ("source", "THE SOURCE HAS CHANGED"),
        ("manifest", "declared delta"),
    ],
)
def test_each_mutation_names_what_broke(tmp_path: Path, mutation: str, phrase: str) -> None:
    """The RED must say WHICH claim stopped being true, not merely that one did."""

    source = tmp_path / "PROMPT.md"
    source.write_text("# ask\nalpha\nbeta\n", encoding="utf-8")
    sent = tmp_path / "sent.md"
    sent.write_text("# ask\nalpha\nbeta\ngamma\n", encoding="utf-8")
    evidence = tmp_path / "evidence"
    dispatch_record.main([
        "record", "--dir", str(evidence), "--arm", "arm_z",
        "--source", str(source), "--dispatched", str(sent),
    ])
    assert dispatch_record.verify(evidence, verbose=False) == []

    if mutation == "artifact":
        (evidence / "arm_z.dispatched.md").write_text("tampered\n", encoding="utf-8")
    elif mutation == "source":
        source.write_text("# ask\nalpha\nbeta\nedited later\n", encoding="utf-8")
    else:
        manifest = dispatch_record.manifest_path(evidence)
        manifest.write_text(
            manifest.read_text(encoding="utf-8").replace("added_lines = 1", "added_lines = 9"),
            encoding="utf-8",
        )

    problems = dispatch_record.verify(evidence, verbose=False)
    assert problems, f"{mutation} stayed green"
    assert any(phrase in p for p in problems), problems


# ---------------------------------------------------------------------------
# the historical demonstration -- the real PA-06-DF-10 record
# ---------------------------------------------------------------------------


def test_the_shipped_ports_as_adapters_record_is_self_consistent() -> None:
    assert dispatch_record.verify(PA_DISPATCH, verbose=False) == []
    rec = dispatch_record.record_for(PA_DISPATCH, "arm_c")
    assert rec is not None
    assert rec.provenance == "reconstruction", (
        "these bytes were rebuilt afterwards, not preserved at dispatch. Labelling them "
        "'preserved' would make weaker evidence read as stronger, which is the whole "
        "defect PA-06-DF-10 records."
    )
    assert (rec.added_lines, rec.removed_lines) == (17, 3), (
        "PA-06-DF-10's reproduction: 17 lines present only in the dispatched form, 3 "
        "present only on disk."
    )
    assert dispatch_record.dispatched_path(PA_DISPATCH, rec).read_bytes() == \
        RECONSTRUCTION.read_bytes()


def test_on_disk_and_as_dispatched_give_different_answers() -> None:
    """The demonstration, measured with the SHIPPED builders.

    Same harness, same two comparisons, two real inputs -- one inside the
    declared tolerance with no architectural vocabulary, one outside it with
    four hits. The second is the one that describes what arm C received.
    """

    a = check_catalogue.distinct_lines(check_catalogue.arm_prompt("arm_a"))
    b = check_catalogue.distinct_lines(check_catalogue.arm_prompt("arm_b"))
    on_disk = check_catalogue.distinct_lines(check_catalogue.arm_prompt("arm_c"))
    rec = dispatch_record.record_for(PA_DISPATCH, "arm_c")
    assert rec is not None
    sent = check_catalogue.distinct_lines(dispatch_record.dispatched_path(PA_DISPATCH, rec))

    b_unique = len(b - a)
    assert b_unique == 105

    disk_unique = len(on_disk - a)
    sent_unique = len(sent - a)
    assert (disk_unique, sent_unique) == (109, 124)

    disk_ratio = disk_unique / b_unique
    sent_ratio = sent_unique / b_unique
    assert round(disk_ratio, 3) == 1.038
    assert round(sent_ratio, 3) == 1.181

    tolerance = check_catalogue.LENGTH_MATCH_TOLERANCE
    assert abs(disk_ratio - 1) <= tolerance, "the on-disk number is the one that read green"
    assert abs(sent_ratio - 1) > tolerance, (
        "the dispatched number must trip the tolerance -- that is the retraction"
    )

    assert check_catalogue.architectural_hits(on_disk - a) == []
    sent_hits = check_catalogue.architectural_hits(sent - a)
    assert len(sent_hits) == 4
    joined = " ".join(line for _word, line in sent_hits)
    assert "PORTS-AS-ADAPTERS-EPIC.md" in joined and "ports-as-adapters" in joined, (
        "two of the four hits are paths PA-06 introduced: the epic's own name, handed "
        "to the arm whose entire job was architectural silence."
    )


def test_check_arms_is_green_on_disk_and_red_as_dispatched(capsys) -> None:
    """One entry point, two inputs, two verdicts. This IS the failing input."""

    green = check_catalogue.check_arms()
    assert green == [], f"--arms on disk should still reproduce the sealed report: {green}"

    red = check_catalogue.check_arms(PA_DISPATCH)
    assert red, "--arms measured AS DISPATCHED must report the retraction"
    assert any("+18.1%" in problem for problem in red), red
    assert any("architectural vocabulary on 4 line(s)" in problem for problem in red), red

    printed = capsys.readouterr().out
    assert "AS DISPATCHED [reconstruction]" in printed
    assert "DISPATCH DELTA" in printed


def test_without_a_record_the_report_says_which_bytes_it_measured(capsys) -> None:
    check_catalogue.check_arms()
    printed = capsys.readouterr().out
    assert "NO DISPATCH RECORD REQUESTED" in printed
    assert "<- on disk" in printed


def test_the_slot_markers_are_read_from_the_template_not_the_dispatch(capsys) -> None:
    """A dispatched copy may legitimately have resolved its slot away."""

    problems = check_catalogue.check_arms(PA_DISPATCH)
    assert not any("slot markers" in p for p in problems), problems
    assert "ARM C SLOT: filled." in capsys.readouterr().out


def test_a_missing_dispatch_directory_is_reported_not_raised(tmp_path: Path) -> None:
    empty = tmp_path / "nothing"
    assert dispatch_record.load_records(empty) == []
    assert dispatch_record.verify(empty, verbose=False) == []


def test_the_manifest_survives_a_copy(tmp_path: Path) -> None:
    """Digests are over bytes, so the record verifies wherever the tree sits."""

    copied = tmp_path / "copy"
    shutil.copytree(PA_DISPATCH, copied)
    assert dispatch_record.verify(copied, verbose=False) == []
