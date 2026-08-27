"""What a history entry refuses to archive.

Build scaffolding and binaries carried no reviewable decision and were copied
into every receipt anyway: 24 checked-in `gradle-wrapper.jar` files across the
history at the time of this change. Both tests here fail on the pre-change
behavior, where `copy_ignore` returned an empty set for all of them.

Deliberately NOT tested here: deduplicating the archived ticket workdir against
the snapshot beside it. That was measured and rejected -- git already stores one
blob per unique content, so eliding a byte-identical copy saves nothing in
version control, and deleting it breaks every reader that expects the archived
workdir to be a complete tree.
"""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.spec_evolution import copy_ignore, copy_snapshot


def test_build_scaffolding_and_binaries_are_never_archived(tmp_path: Path) -> None:
    source = tmp_path / "results"
    (source / "gradle" / "wrapper").mkdir(parents=True)
    (source / "gradle" / "wrapper" / "gradle-wrapper.jar").write_bytes(b"PK\x03\x04")
    (source / ".venv").mkdir()
    (source / ".venv" / "pyvenv.cfg").write_text("home = /usr")
    (source / "report.json").write_text("{}")

    destination = tmp_path / "entry" / "results"
    copy_snapshot(source, destination)

    archived = {path.name for path in destination.rglob("*") if path.is_file()}
    assert archived == {"report.json"}


def test_a_stray_jar_beside_real_evidence_is_dropped_and_the_evidence_kept(tmp_path: Path) -> None:
    names = ["report.json", "app.jar", "Internal.tla", "cache.pyc"]

    ignored = copy_ignore(str(tmp_path), names)

    assert ignored == {"app.jar", "cache.pyc"}


def test_the_ticket_workdir_is_pruned_too_and_not_only_the_snapshots(tmp_path: Path) -> None:
    """The exclusions must reach the tree that is MOVED, not only the copied one.

    THIS IS THE TEST THE TWO ABOVE COULD NOT BE. Both call `copy_snapshot` /
    `copy_ignore` directly, so they exercise the model SNAPSHOTS -- the half of
    a history entry that rarely contains a jar. The ticket workdir, which is
    where a gradle wrapper or a vendored venv actually lives, reaches the entry
    by `shutil.move`, which consults no ignore function.

    Measured on a real close before `prune_ignored` existed: a planted
    `gradle-wrapper.jar` and `.venv/` landed under `<entry>/ticket/current/`
    while `<entry>/snapshots/` was clean. Both tests above were GREEN for that
    close. Green meant they were asking the copied tree a question about the
    moved one.
    """
    from scripts.spec_evolution import prune_ignored

    workdir = tmp_path / "ticket"
    (workdir / "current" / "test_graph" / "gradle" / "wrapper").mkdir(parents=True)
    (workdir / "current" / "test_graph" / "gradle" / "wrapper" / "gradle-wrapper.jar").write_bytes(b"PK\x03\x04")
    (workdir / "current" / ".venv" / "lib").mkdir(parents=True)
    (workdir / "current" / ".venv" / "lib" / "vendored.txt").write_text("vendored")
    (workdir / "current" / "stray.pyc").write_bytes(b"\x00")
    # Everything a reader is entitled to find must survive.
    (workdir / "desired").mkdir()
    (workdir / "desired" / "External.tla").write_text("---- MODULE External ----\n====\n")
    (workdir / "current" / "Internal.tla").write_text("---- MODULE Internal ----\n====\n")
    (workdir / "results").mkdir()
    (workdir / "results" / "report.json").write_text("{}")

    removed = prune_ignored(workdir)

    survivors = {
        path.relative_to(workdir).as_posix()
        for path in workdir.rglob("*")
        if path.is_file()
    }
    assert survivors == {
        "desired/External.tla",
        "current/Internal.tla",
        "results/report.json",
    }, "pruning removed evidence, or failed to remove scaffolding"
    assert removed, "nothing was pruned, so the exclusions did not reach the moved tree"
    assert not (workdir / "current" / ".venv").exists()
    assert not (workdir / "current" / "test_graph" / "gradle").exists()


def test_pruning_never_removes_the_archived_workdir_a_reader_expects(tmp_path: Path) -> None:
    """The rejected optimisation, kept as a guard.

    The commit that added these exclusions RECORDED A REJECTION: an intra-entry
    deduplication that elided archived files byte-identical to the snapshot
    beside them looked like it recovered 50.5 MB, recovered nothing in version
    control because git already dedups, and broke three tests by deleting
    `ticket/desired/External.tla`. Pruning must not drift into that.
    """
    from scripts.spec_evolution import prune_ignored

    workdir = tmp_path / "ticket"
    (workdir / "desired").mkdir(parents=True)
    (workdir / "desired" / "External.tla").write_text("---- MODULE External ----\n====\n")

    prune_ignored(workdir)

    assert (workdir / "desired" / "External.tla").exists(), (
        "deleting a file readers expect, to save bytes git was not spending, "
        "is a bad trade twice over"
    )
