from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.scaffold_spec import parse_views, scaffold


def test_scaffold_spec_can_create_internal_external_view_files(tmp_path: Path) -> None:
    target = scaffold("request-flow", tmp_path, parse_views("internal,external"))

    assert target == tmp_path / "request_flow"
    assert (target / "RequestFlow.tla").exists()
    assert (target / "model/Core.tla").exists()
    assert (target / "model/Internal.tla").exists()
    assert (target / "model/External.tla").exists()
    assert (target / "model/DesiredCore.tla").exists()
    assert (target / "model/DesiredInternal.tla").exists()
    assert (target / "model/DesiredExternal.tla").exists()
    assert "Submit" in (target / "model/actions.yml").read_text(encoding="utf-8")
    internal = (target / "model/Internal.tla").read_text(encoding="utf-8")
    external = (target / "model/External.tla").read_text(encoding="utf-8")
    assert 'lastInternalAction = [name |-> "Init", params |-> <<>>]' in internal
    assert 'lastExternalAction = [name |-> "Init", params |-> <<>>]' in external
    assert "params |-> [ ]" not in internal
    assert "params |-> [ ]" not in external
    assert (target / "testgraph/bindings.yml").exists()
    assert (target / "testgraph/selectors.yml").exists()
    assert (target / "testgraph/assertions.yml").exists()
