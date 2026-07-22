from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.scaffold_spec import DEFAULT_VIEWS, parse_views, scaffold


# The one accepted baseline shape, shared with `tla-spec-dev scaffold project`.
BASELINE_FILES = [
    "Core.tla",
    "Internal.tla",
    "Internal.cfg",
    "External.tla",
    "External.cfg",
    "actions.yml",
    "adapters.py",
    "case_adapters.toml",
    "testgraph_bindings.yml",
    "tlc_projection.py",
    "spec_manifest.yaml",
]

DESIRED_OVERLAYS = ["DesiredCore.tla", "DesiredInternal.tla", "DesiredExternal.tla"]


def test_scaffold_spec_emits_both_views_by_default() -> None:
    """A view-less scaffold is not a supported output.

    Without an External view there are no Test Graph cases, so the spec can
    never be validated against its public surface.
    """
    assert parse_views(None) == set(DEFAULT_VIEWS) == {"internal", "external"}
    assert parse_views("internal") == {"internal", "external"}


@pytest.mark.parametrize("name", BASELINE_FILES + DESIRED_OVERLAYS)
def test_scaffold_spec_creates_accepted_baseline_shape(tmp_path: Path, name: str) -> None:
    target = scaffold("request-flow", tmp_path, parse_views("internal,external"))

    assert target == tmp_path / "request_flow"
    assert (target / name).exists()


def test_scaffold_spec_uses_flat_layout(tmp_path: Path) -> None:
    """The baseline is flat, matching examples/distributed_history/specs/program_model/.

    The old model/ + testgraph/ subdirectory layout diverged from the accepted
    shape and taught the wrong structure.
    """
    target = scaffold("request-flow", tmp_path, parse_views("internal,external"))

    assert not (target / "model").exists()
    assert not (target / "testgraph").exists()
    # No single-module stand-in for the two views.
    assert not (target / "RequestFlow.tla").exists()
    assert not (target / "MC.cfg").exists()


def test_scaffold_spec_wires_both_adapter_mappings(tmp_path: Path) -> None:
    target = scaffold("request-flow", tmp_path, parse_views("internal,external"))

    assert "Submit" in (target / "actions.yml").read_text(encoding="utf-8")

    bindings = (target / "testgraph_bindings.yml").read_text(encoding="utf-8")
    for hook in ("adapter:", "projector:", "expected_projection:", "assertion:"):
        assert hook in bindings

    adapters = (target / "adapters.py").read_text(encoding="utf-8")
    for symbol in (
        "class CreateInternalAdapter",
        "class SubmitExternalAdapter",
        "class ProgramStateProjector",
        "class ProjectedStateAssertion",
    ):
        assert symbol in adapters


def test_scaffold_spec_exposes_semantic_effect_schema_without_declaring_fake_effects(tmp_path: Path) -> None:
    target = scaffold("request-flow", tmp_path, parse_views("internal,external"))

    actions = (target / "actions.yml").read_text(encoding="utf-8")
    assert "effect_ports: typed semantic ports" in actions
    assert actions.count("effect_ports: []") == 6

    mapping = (target / "case_adapters.toml").read_text(encoding="utf-8")
    assert "[effect_providers.FilesystemPort]" in mapping
    assert 'provider = "providers:filesystem_provider"' in mapping

    manifest = (target / "spec_manifest.yaml").read_text(encoding="utf-8")
    assert "role: application" in manifest
    assert "role: effect" not in manifest


def test_scaffold_spec_view_modules_record_last_actions(tmp_path: Path) -> None:
    target = scaffold("request-flow", tmp_path, parse_views("internal,external"))

    internal = (target / "Internal.tla").read_text(encoding="utf-8")
    external = (target / "External.tla").read_text(encoding="utf-8")

    assert "EXTENDS Core" in internal
    assert "EXTENDS Internal" in external
    assert 'lastInternalAction = [name |-> "Init", params |-> <<>>]' in internal
    assert 'lastExternalAction = [name |-> "Init", params |-> <<>>]' in external
    assert "params |-> [ ]" not in internal
    assert "params |-> [ ]" not in external
