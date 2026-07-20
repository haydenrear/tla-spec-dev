"""MF-023: a dangling `source_model:` reference must FAIL, not pass silently.

From the epic's first commit until this ticket, `specs/current/spec_manifest.yaml`
declared

    source_model:
      program_model_core: ../program_model/Core.tla
      program_model_internal: ../program_model/Internal.tla
      program_model_external: ../program_model/External.tla

while **all three files were absent**, and nothing failed. `analyze complexity`
ran clean straight past it, every gate stayed green, and the desync survived
nine merged tickets. MF-026's coverage audit found it by reading, which is
exactly the kind of check that should not depend on an agent noticing.

These tests make the dangling case fail. They are deliberately generic -- they
resolve *every* path-valued entry under `source_model:` rather than the three
that happened to be broken, so a future manifest that adds a fourth reference
is covered without anyone remembering to extend this file.
"""

from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

REPO_ROOT = Path(__file__).resolve().parents[1]

MANIFESTS = [
    REPO_ROOT / "specs" / "current" / "spec_manifest.yaml",
    REPO_ROOT / "specs" / "program_model" / "spec_manifest.yaml",
]


def _manifests_with_source_model() -> list[tuple[Path, dict]]:
    found = []
    for path in MANIFESTS:
        if not path.is_file():
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if isinstance(data.get("source_model"), dict):
            found.append((path, data["source_model"]))
    return found


def test_at_least_one_manifest_declares_source_model() -> None:
    """Guard the guard: if `source_model:` disappears, this suite must not
    silently become vacuous. A test that passes because it checked nothing is
    the same defect it exists to catch."""
    assert _manifests_with_source_model(), (
        "no spec manifest declares a source_model block -- either the schema "
        "changed or this test has gone stale; do not leave it passing vacuously"
    )


def test_every_source_model_reference_resolves() -> None:
    """Every path-valued `source_model:` entry must name a file that exists."""
    dangling: list[str] = []

    for manifest_path, source_model in _manifests_with_source_model():
        for key, value in source_model.items():
            if not isinstance(value, str) or not value.strip():
                continue
            # Paths are declared relative to the manifest's own directory.
            target = (manifest_path.parent / value).resolve()
            if not target.exists():
                dangling.append(
                    f"{manifest_path.relative_to(REPO_ROOT)}: "
                    f"source_model.{key} -> {value} (resolved {target}) DOES NOT EXIST"
                )

    assert not dangling, (
        "dangling source_model reference(s) -- a manifest naming a model file "
        "that is not there must fail rather than pass:\n  " + "\n  ".join(dangling)
    )


def test_the_decomposed_views_are_the_referenced_ones() -> None:
    """MF-023's acceptance criterion: Core/Internal/External replace the single
    module. Assert the current manifest actually points at the decomposed views
    rather than at a single-module baseline."""
    current = REPO_ROOT / "specs" / "current" / "spec_manifest.yaml"
    if not current.is_file():
        pytest.skip("specs/current/spec_manifest.yaml not present")

    data = yaml.safe_load(current.read_text(encoding="utf-8")) or {}
    source_model = data.get("source_model") or {}

    for key in ("program_model_core", "program_model_internal", "program_model_external"):
        assert key in source_model, f"current manifest lost source_model.{key}"
        target = (current.parent / source_model[key]).resolve()
        assert target.is_file(), f"source_model.{key} -> {source_model[key]} is missing"
