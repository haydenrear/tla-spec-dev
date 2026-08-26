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
