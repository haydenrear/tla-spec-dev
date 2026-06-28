from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.export_testgraph_cases import case_to_trace, export_cases
from scripts.generate_cases_from_tlc_dump import ActionMetadata, Edge, render_python_package
from scripts.run_generated_case_adapters import load_cases


def test_export_external_case_as_testgraph_trace(tmp_path: Path) -> None:
    package_dir = tmp_path / "external_cases"
    render_python_package(
        module="Program",
        states={
            "0": {"status": "none"},
            "1": {"status": "accepted", "seen": frozenset({"r1"})},
        },
        edges=[Edge("0", "1", "Submit")],
        package_dir=package_dir,
        view="external",
        action_metadata={"Submit": ActionMetadata("Submit", "external", "e2e_direct", ("testgraph",))},
    )

    cases = list(load_cases(package_dir).CASES)
    written = export_cases(cases, tmp_path / "traces", module="Program")

    trace_path = tmp_path / "traces" / f"{cases[0].name}.json"
    assert trace_path in written
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    assert trace["schema_version"] == "tla-testgraph.trace.v1"
    assert trace["view"] == "external"
    assert trace["source"]["module"] == "Program"
    assert trace["steps"][0]["action"] == "Submit"
    assert trace["steps"][0]["controllability"] == "e2e_direct"
    assert trace["steps"][0]["post"]["seen"] == ["r1"]
    assert trace["steps"][0]["expected_response"]["changed"]["seen"]["after"] == ["r1"]


def test_export_rejects_internal_cases(tmp_path: Path) -> None:
    package_dir = tmp_path / "internal_cases"
    render_python_package(
        module="Program",
        states={"0": {"status": "none"}, "1": {"status": "pending"}},
        edges=[Edge("0", "1", "AcceptRequest")],
        package_dir=package_dir,
    )

    case = load_cases(package_dir).CASES[0]

    try:
        case_to_trace(case, module="Program")
    except ValueError as exc:
        assert "not external" in str(exc)
    else:
        raise AssertionError("expected internal case export to fail")


def test_load_cases_reloads_same_basename_from_new_directory(tmp_path: Path) -> None:
    first_dir = tmp_path / "first" / "external_cases"
    second_dir = tmp_path / "second" / "external_cases"
    render_python_package(
        module="Program",
        states={"0": {"status": "none"}, "1": {"status": "first"}},
        edges=[Edge("0", "1", "Submit")],
        package_dir=first_dir,
        view="external",
        action_metadata={"Submit": ActionMetadata("Submit", "external", "e2e_direct", ("testgraph",))},
    )
    render_python_package(
        module="Program",
        states={"0": {"status": "none"}, "1": {"status": "second"}},
        edges=[Edge("0", "1", "Submit")],
        package_dir=second_dir,
        view="external",
        action_metadata={"Submit": ActionMetadata("Submit", "external", "e2e_direct", ("testgraph",))},
    )

    first_cases = list(load_cases(first_dir).CASES)
    second_cases = list(load_cases(second_dir).CASES)

    assert first_cases[0].after["status"] == "first"
    assert second_cases[0].after["status"] == "second"
