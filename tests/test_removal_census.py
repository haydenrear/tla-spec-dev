"""RD-02 -- the removal census, and the three ways it refuses.

`subtract-to-measure` published one figure about its own size (`-225 lines from
scripts/`). It was true. It hid that the same epic added 1677 net `code_lines`
across the trees it touched, because every removal shipped instruments, tests
and demonstrations to prove the removal safe and **nobody counted that as a
cost**.

The census counts it, per removal. What is tested here is not that its
arithmetic is pretty -- it is that the census **cannot be made to lie in the
three ways this project has already been lied to**:

  1. by a total, which is the shape of the claim that hid the cost;
  2. by a manifest that drifts away from the tree it claims to measure;
  3. by a removal with no mutant in its gap and no reason it has none, which
     `removal_is_a_delta_rule` calls not a measurement at all.

EVERY FAILING INPUT HERE IS THE REAL SHIPPED MANIFEST, mutated the way a real
manifest goes wrong. There is no synthetic fixture in this file, because R1
asks for a demonstrated failure against a real subject and a fixture that fails
proves only that a fixture can be written.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CENSUS = REPO_ROOT / "examples/validation/removal_census/removal_census.py"
MANIFEST = REPO_ROOT / "examples/validation/removal_census/removals.toml"

tomllib = pytest.importorskip("tomllib")


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CENSUS), *args],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )


@pytest.fixture(scope="module")
def manifest() -> dict:
    return tomllib.loads(MANIFEST.read_text(encoding="utf-8"))


def mutated_manifest(tmp_path: Path, find: str, replace: str) -> Path:
    """The SHIPPED manifest with one thing changed, written where it can be run."""
    text = MANIFEST.read_text(encoding="utf-8")
    assert text.count(find) == 1, f"{find!r} occurs {text.count(find)} times, need exactly 1"
    path = tmp_path / "removals.toml"
    path.write_text(text.replace(find, replace), encoding="utf-8")
    return path


# -- 1. the three refusals, each on the real manifest -----------------------


def test_it_refuses_to_emit_a_total_over_removals() -> None:
    """THE REFUSAL IS THE INSTRUMENT. A total is what the predecessor reported."""
    ok = run("census")
    assert ok.returncode == 0, ok.stderr
    refused = run("census", "--total")
    assert refused.returncode == 2
    assert "REFUSED" in refused.stderr
    assert "1677" in refused.stderr, "the refusal has to say WHY, with the figure"


def test_a_total_declared_in_the_manifest_is_refused_the_same_way(tmp_path: Path) -> None:
    """A flag anyone can pass is a flag anyone can also set in the file."""
    path = mutated_manifest(tmp_path, "report_total = false", "report_total = true")
    refused = run("--manifest", str(path), "census")
    assert refused.returncode == 2 and "REFUSED" in refused.stderr


def test_a_manifest_that_has_drifted_from_the_tree_is_refused(tmp_path: Path) -> None:
    """DEMONSTRATED FAILING INPUT, on the real manifest.

    `290` is the count of lines SM-02 deleted from the case-adapter runner. Move
    it by one and `check` has to say so, because a census whose numbers are typed
    in rather than measured reports whatever its author last believed.
    """
    assert run("check").returncode == 0, "control: the shipped manifest measures true"
    path = mutated_manifest(tmp_path, "expect_lines = 290", "expect_lines = 291")
    drifted = run("--manifest", str(path), "check")
    assert drifted.returncode == 2
    assert "CENSUS-DRIFT" in drifted.stderr
    assert "measures 290, manifest says 291" in drifted.stderr


def test_a_removal_with_no_mutant_and_no_reason_is_refused(tmp_path: Path) -> None:
    """`removal_is_a_delta_rule`, enforced against the manifest rather than
    remembered. `card-duplication` legitimately has no catalogue mutant and says
    why; delete the reason and the row stops being a measurement."""
    text = MANIFEST.read_text(encoding="utf-8")
    start = text.index("no_gap_reason = \"\"\"", text.index('id = "card-duplication"'))
    end = text.index('"""', start + 20) + 3
    path = tmp_path / "removals.toml"
    path.write_text(text[:start] + text[end:], encoding="utf-8")
    refused = run("--manifest", str(path), "census")
    assert refused.returncode == 2
    assert "declares no gap mutant and no reason" in refused.stderr


# -- 2. what the census is FOR ---------------------------------------------


def test_no_row_of_the_output_is_a_total() -> None:
    """Not a promise in a docstring: the rendered table is inspected."""
    out = run("census").stdout
    body = [line for line in out.split("\n") if line.startswith("|")]
    assert body, out
    for line in body:
        assert not line.lower().startswith(("| total", "| **total", "| sum", "| net")), line
    assert "No total row" in out


def test_every_figure_carries_the_scope_it_was_measured_over(tmp_path: Path) -> None:
    """R3. A count with no scope is the defect this epic was opened on."""
    out = tmp_path / "census.json"
    assert run("census", "--json", str(out)).returncode == 0
    payload = json.loads(out.read_text())
    for removal in payload["removals"]:
        assert removal["scope"], removal["id"]
        for region in removal["regions"]:
            assert region["scope"] and region["reason"], (removal["id"], region)


def test_each_removal_reports_two_denominators_and_never_their_average(manifest) -> None:
    """`denominator_rule`. `cut_tests` is real deletion and is not the mechanism;
    folding it into one denominator makes every ratio look cheaper than it is.
    SM-02 is the case in point: 462 of its 828 deleted lines were the deleted
    mechanism's own test file."""
    out = run("census").stdout
    header = next(line for line in out.split("\n") if line.startswith("| removal"))
    assert "cut (production)" in header and "cut (its own tests)" in header
    assert "proof / production" in header and "proof / all cut" in header


# -- 3. the discriminating-power reading, against the sealed before-table ---


def test_the_discriminate_table_is_read_from_the_sealed_before_state(manifest) -> None:
    """The verdicts are derived from `gap-mutants-before.json` as SM-01 sealed
    it, not from anything this ticket produced."""
    table = REPO_ROOT / manifest["gap_mutant_before_table"]
    assert table.exists(), table
    out = run("discriminate")
    assert out.returncode == 0, out.stderr
    assert str(table.relative_to(REPO_ROOT)) in out.stdout


def test_no_catalogue_mutant_could_have_priced_a_removal_and_it_says_so(tmp_path: Path) -> None:
    """THE FINDING, ASSERTED SO IT CANNOT ROT.

    A gap mutant can only report that a removal cost something if EVERY detector
    that killed it is one the removal deletes. Not one of the nine mutants in
    `gap_mutants.toml` meets that: each was already dying on a detector that
    outlived its cut, or was not dying at all. The `DIES` verdicts SM-02 and
    SM-05 re-ran and reported were entailed by SM-01's before-table before
    either cut was made.

    If a future removal seeds a mutant that IS discriminating, this test fails,
    and that is the right time to re-read the epic's conclusion.
    """
    out = tmp_path / "disc.json"
    assert run("discriminate", "--json", str(out)).returncode == 0
    rows = json.loads(out.read_text())
    discriminating = [r for r in rows if r["verdict"] == "DISCRIMINATING"]
    assert discriminating == [], (
        f"a mutant can now price a removal: {[r['mutant'] for r in discriminating]}. "
        f"RD-02 concluded the opposite on nine mutants; re-read that conclusion."
    )
    assert {r["verdict"] for r in rows} <= {"NON-DISCRIMINATING", "NO-KILL-TO-LOSE"}


def test_the_one_mutant_that_did_price_a_removal_is_recorded_outside_the_table(
    manifest,
) -> None:
    """R3, applied to this ticket's own headline.

    "Two epics of gap mutants produced zero `DIES` -> `SURVIVES`" is a claim
    about `gap_mutants.toml`. `SM-04-GM-T1` was seeded under the same rule, by
    the same epic, as an executing test rather than a catalogue row -- and it
    went `DIES` -> `SURVIVES`. The manifest counts it separately rather than
    letting the catalogue's scope be read as the rule's.
    """
    outside = {row["id"]: row for row in manifest["mutant_outside_this_table"]}
    assert "SM-04-GM-T1" in outside
    assert "DIES -> SURVIVES" in outside["SM-04-GM-T1"]["verdict"]
    node = outside["SM-04-GM-T1"]["lives_in"].split("::")[0]
    assert (REPO_ROOT / node).exists(), f"{node} is cited and does not exist"


def test_rd02s_own_removal_is_priced_by_the_same_manifest(manifest) -> None:
    """A ticket that prices four removals and exempts its own has not measured."""
    ids = {row["id"] for row in manifest["removal"]}
    assert "dead-port-binding-report-detector" in ids
    mine = next(r for r in manifest["removal"] if r["id"] == "dead-port-binding-report-detector")
    assert mine["gap_mutants"], "RD-02's own cut declares no mutant in its gap"
    assert any(region["role"] == "proof" for region in mine["region"])
