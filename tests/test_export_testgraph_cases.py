from pathlib import Path
import json
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.export_testgraph_cases import case_to_trace, export_cases, main as export_main
from scripts.generate_cases_from_tlc_dump import ActionMetadata, Edge, render_python_package
from scripts.run_generated_case_adapters import load_cases
from scripts.testgraph_channels import ExternalContract


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
    # MF-015: the exported manifest names the integration-ladder rung, so the
    # validated external contract is a required input rather than an optional one.
    contract = ExternalContract(
        production_package="program_under_test",
        port_bindings={"RequestPort": "real", "ClockPort": "double"},
        additional_channels=frozenset(),
    )
    written = export_cases(cases, tmp_path / "traces", module="Program", contract=contract)

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

    manifest = json.loads((tmp_path / "traces" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["integration_rung"]["rung"] == "RequestPort"
    assert manifest["integration_rung"]["real_ports"] == ["RequestPort"]
    assert manifest["integration_rung"]["double_ports"] == ["ClockPort"]


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


# ---------------------------------------------------------------------------
# VAL-10 (CD-08): manifest resolution for a corpus in a build directory.
#
# The recorded symptom: a generator PASSes a corpus against the manifest cap,
# then the exporter REFUSES the same corpus at the built-in default cap 50,
# because the corpus lives in a build dir with no spec_manifest.yaml above it
# and no --manifest was given. The exporter must resolve the manifest from the
# spec root (the directory holding --bindings) when discoverable, and
# otherwise fail loudly naming --manifest -- never silently default.
# ---------------------------------------------------------------------------


def _spec_root(tmp_path: Path, *, manifest_budgets: str | None) -> Path:
    """A spec root holding a legal bindings file and (optionally) a manifest."""
    spec = tmp_path / "specs" / "program_model"
    spec.mkdir(parents=True)
    (spec / "adapters.py").write_text(
        "import urllib.request\n"
        "\n"
        "class SubmitHttpAdapter:\n"
        "    def run(self, case, work_dir=None):\n"
        "        urllib.request.urlopen('http://localhost:8080/submit')\n"
        "        return {'ok': True}\n",
        encoding="utf-8",
    )
    (spec / "testgraph_bindings.yml").write_text(
        "external:\n"
        "  production_package: program_under_test\n"
        "  port_bindings:\n"
        "    RequestPort: real\n"
        "    ClockPort: double\n"
        "actions:\n"
        "  Submit:\n"
        "    view: external\n"
        "    channel: http\n"
        "    layer: external\n"
        "    controllability: e2e_direct\n"
        "    adapter: adapters:SubmitHttpAdapter\n",
        encoding="utf-8",
    )
    if manifest_budgets is not None:
        (spec / "spec_manifest.yaml").write_text(
            "module: Program\n" + manifest_budgets,
            encoding="utf-8",
        )
    return spec


def _build_dir_corpus(tmp_path: Path, package_basename: str, case_count: int = 2) -> Path:
    """An external case package in a build dir with no manifest above it."""
    package_dir = tmp_path / "build" / "generated" / "testgraph" / package_basename
    render_python_package(
        module="Program",
        states={"0": {"status": "none"}, **{str(i): {"status": f"s{i}"} for i in range(1, case_count + 1)}},
        edges=[Edge("0", str(i), "Submit") for i in range(1, case_count + 1)],
        package_dir=package_dir,
        view="external",
        action_metadata={"Submit": ActionMetadata("Submit", "external", "e2e_direct", ("testgraph",))},
    )
    return package_dir


def _run_export(monkeypatch, cases_dir: Path, out_dir: Path, bindings: Path, *extra: str) -> int:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "export_testgraph_cases.py",
            str(cases_dir),
            "--out",
            str(out_dir),
            "--bindings",
            str(bindings),
            *extra,
        ],
    )
    return export_main()


def test_build_dir_corpus_gated_by_spec_root_manifest_not_builtin_cap(tmp_path, monkeypatch, capsys) -> None:
    """The manifest beside --bindings governs the gate, not the built-in cap.

    The spec-root manifest caps external cases per action at 1 while the
    corpus holds 2 -- under the built-in default of 50. Refusal proves the
    exporter resolved the spec root's manifest instead of silently defaulting.
    """
    spec = _spec_root(
        tmp_path,
        manifest_budgets="budgets:\n  max_external_cases_per_action: 1\n",
    )
    cases_dir = _build_dir_corpus(tmp_path, "val10_tight_cases", case_count=2)

    with pytest.raises(SystemExit) as excinfo:
        _run_export(monkeypatch, cases_dir, tmp_path / "traces", spec / "testgraph_bindings.yml")

    assert excinfo.value.code == 2  # the cap gate's over-cap refusal
    out = capsys.readouterr()
    assert "case caps read from" in out.out
    assert str(spec / "spec_manifest.yaml") in out.out


def test_build_dir_corpus_exports_under_spec_root_manifest_cap(tmp_path, monkeypatch, capsys) -> None:
    spec = _spec_root(
        tmp_path,
        manifest_budgets="budgets:\n  max_external_cases_per_action: 10\n",
    )
    cases_dir = _build_dir_corpus(tmp_path, "val10_roomy_cases", case_count=2)

    assert _run_export(monkeypatch, cases_dir, tmp_path / "traces", spec / "testgraph_bindings.yml") == 0
    out = capsys.readouterr()
    assert str(spec / "spec_manifest.yaml") in out.out
    assert (tmp_path / "traces" / "manifest.json").is_file()


def test_build_dir_corpus_without_any_manifest_fails_naming_the_flag(tmp_path, monkeypatch) -> None:
    """No manifest above the corpus, none beside --bindings: fail loudly."""
    spec = _spec_root(tmp_path, manifest_budgets=None)
    cases_dir = _build_dir_corpus(tmp_path, "val10_orphan_cases", case_count=1)

    with pytest.raises(SystemExit) as excinfo:
        _run_export(monkeypatch, cases_dir, tmp_path / "traces", spec / "testgraph_bindings.yml")

    message = str(excinfo.value.code)
    assert "--manifest" in message
    assert "spec_manifest.yaml" in message


def test_explicit_missing_manifest_fails_rather_than_defaulting(tmp_path, monkeypatch) -> None:
    spec = _spec_root(
        tmp_path,
        manifest_budgets="budgets:\n  max_external_cases_per_action: 10\n",
    )
    cases_dir = _build_dir_corpus(tmp_path, "val10_typo_cases", case_count=1)

    with pytest.raises(SystemExit) as excinfo:
        _run_export(
            monkeypatch,
            cases_dir,
            tmp_path / "traces",
            spec / "testgraph_bindings.yml",
            "--manifest",
            str(tmp_path / "no_such_manifest.yaml"),
        )

    assert "--manifest" in str(excinfo.value.code)


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
