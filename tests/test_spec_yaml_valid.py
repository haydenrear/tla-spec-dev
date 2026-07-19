"""Every YAML file under specs/ must parse.

Guard against a recurring silent failure. Twice in the modular-fuzzing epic a
YAML file under specs/ was committed in a syntactically invalid state and the
breakage was invisible:

- ``ticket_plan.yaml`` was pushed unparseable, so the epic's canonical plan
  could not be read at all.
- ``spec_manifest.yaml`` was invalid across several tickets while
  ``budgets.load_budgets`` silently fell back to documented defaults on every
  ``analyze complexity`` run. No verdict happened to be wrong, because the
  declared values equalled the defaults -- but a negotiated budget would have
  been ignored without a word. Recorded as SF-004 and again as SF-007.

The failure mode is what makes it worth a test: the repository's own fallback
YAML parser is lenient, PyYAML is not installed by default, and the mismatch
means a file can be accepted by one reader, rejected by another, and produce a
silent default from a third. Nothing surfaces it.

Historical snapshots under ``specs/.history`` are excluded on purpose. That tree
is append-only, records what was actually committed at the time, and therefore
legitimately contains the broken files this test exists to prevent.
"""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip(
    "yaml",
    reason="PyYAML is not a runtime dependency; run with `uv run --with pyyaml` to enforce",
)

SPECS = Path(__file__).resolve().parents[1] / "specs"


def _spec_yaml_files() -> list[Path]:
    if not SPECS.is_dir():
        return []
    return sorted(
        path
        for path in SPECS.rglob("*.y*ml")
        if ".history" not in path.parts and path.is_file()
    )


@pytest.mark.parametrize("path", _spec_yaml_files(), ids=lambda p: str(p.name))
def test_spec_yaml_parses(path: Path) -> None:
    """A YAML file under specs/ that does not parse is a silent-failure source."""
    try:
        yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:  # pragma: no cover - failure path is the point
        pytest.fail(f"{path} is not valid YAML: {exc}")


def test_at_least_one_spec_yaml_is_checked() -> None:
    """Guard the guard: an empty parametrisation would pass vacuously."""
    assert _spec_yaml_files(), "no YAML found under specs/ -- this test would pass vacuously"
