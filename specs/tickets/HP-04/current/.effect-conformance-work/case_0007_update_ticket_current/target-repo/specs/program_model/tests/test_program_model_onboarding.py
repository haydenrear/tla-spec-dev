"""The accepted baseline must carry BOTH views and BOTH adapter mappings.

This test fails while the scaffold is incomplete. That is deliberate: a
single-module baseline cannot generate Test Graph cases, so the project would
have no validation of its public surface.
"""

from pathlib import Path

import pytest


SPEC_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_BASELINE_FILES = [
    "Core.tla",
    "Internal.tla",
    "Internal.cfg",
    "External.tla",
    "External.cfg",
    "actions.yml",
    "adapters.py",
    "providers.py",
    "effect_provider_usage.yaml",
    "case_adapters.toml",
    "testgraph_bindings.yml",
    "tlc_projection.py",
    "spec_manifest.yaml",
]


@pytest.mark.parametrize("name", REQUIRED_BASELINE_FILES)
def test_baseline_file_exists(name: str) -> None:
    assert (SPEC_ROOT / name).exists(), (
        f"{name} is missing from the accepted program model. "
        "See references/testgraph_adapters.md and "
        "examples/distributed_history/specs/program_model/."
    )


def test_external_view_is_modeled() -> None:
    external = (SPEC_ROOT / "External.tla").read_text(encoding="utf-8")
    assert "EXTENDS Internal" in external, (
        "External.tla must project the internal semantics, not redefine them."
    )


def test_testgraph_bindings_cover_external_actions() -> None:
    bindings = (SPEC_ROOT / "testgraph_bindings.yml").read_text(encoding="utf-8")
    for hook in ("adapter:", "projector:", "expected_projection:", "assertion:"):
        assert hook in bindings, f"testgraph_bindings.yml is missing {hook}"
