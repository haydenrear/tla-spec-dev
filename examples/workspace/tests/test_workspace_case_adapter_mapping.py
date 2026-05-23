from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import sys

ROOT = Path(__file__).resolve().parents[3]
WORKSPACE = ROOT / "examples" / "workspace"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(WORKSPACE))

from case_adapters import WorkspaceCaseAdapter
from scripts.run_generated_case_adapters import load_mappings


def test_workspace_case_adapter_mapping_covers_create_label() -> None:
    mappings = load_mappings(WORKSPACE / "case_adapters.toml")

    assert mappings["Create"].adapter == "case_adapters:WorkspaceCaseAdapter"


def test_workspace_case_adapter_returns_case_expectations() -> None:
    case = SimpleNamespace(
        labels=frozenset({"Create"}),
        output={"changed": {"owned": {"before": {}, "after": {"u1": frozenset({"w1"})}}}},
        after={"owned": {"u1": frozenset({"w1"})}},
    )

    with TemporaryDirectory() as tmp:
        result = WorkspaceCaseAdapter().run(case, work_dir=Path(tmp))

    assert result == {"output": case.output, "after": case.after}


if __name__ == "__main__":
    test_workspace_case_adapter_mapping_covers_create_label()
    test_workspace_case_adapter_returns_case_expectations()
