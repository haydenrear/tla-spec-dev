from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys
from typing import Optional
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.generate_cases_from_tlc_dump import ActionMetadata, Edge, render_python_package
from scripts.run_generated_case_adapters import (
    AdapterMapping,
    adapter_for_case,
    execute_cases_in_batch,
    load_mappings,
    validate_adapter_capabilities,
    validate_mapping_coverage,
)
from spec_double_compiler.runtime import CaseRunResult, adapter_accepts_case, assert_case_result


@dataclass(frozen=True)
class Output:
    changed: dict


@dataclass(frozen=True)
class Case:
    name: str
    before: dict
    input: object
    output: Output
    after: dict
    labels: frozenset[str]


class RejectingAdapter:
    def can_run(self, case):
        return False, "unsupported fixture"


class AcceptingAdapter:
    def can_run(self, case):
        return True


def test_adapter_mapping_prefers_toml_order_for_fine_labels() -> None:
    case = Case("case_1", {}, object(), Output({}), {}, frozenset({"Action", "fine_edge"}))
    mappings = {
        "fine_edge": AdapterMapping("fine_edge", "module:Fine", order=0),
        "Action": AdapterMapping("Action", "module:Action", order=1),
    }

    assert adapter_for_case(case, mappings).label == "fine_edge"


def test_adapter_accepts_case_uses_can_run() -> None:
    accepted, reason = adapter_accepts_case(RejectingAdapter(), object())

    assert accepted is False
    assert reason == "unsupported fixture"
    assert adapter_accepts_case(AcceptingAdapter(), object()) == (True, None)


def test_assert_case_result_compares_semantic_projection() -> None:
    case = Case("case_1", {"items": set()}, object(), Output({}), {"items": {"a"}}, frozenset({"Action"}))

    assert_case_result(
        case=case,
        result=CaseRunResult(after=case.after, semantic_output={"added": ["a"]}),
        projector=lambda case: {"added": sorted(case.after["items"] - case.before["items"])},
    )


def make_view_case(
    name: str,
    label: str,
    *,
    view: str = "external",
    controllability: str = "e2e_direct",
    before: Optional[dict] = None,
    after: Optional[dict] = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        name=name,
        before=before or {},
        input=SimpleNamespace(action=label),
        output=Output({}),
        after=after or {},
        labels=frozenset({label}),
        view=view,
        controllability=controllability,
        generates=frozenset({"testgraph"} if view == "external" else {"spec_unit"}),
    )


def test_external_direct_action_requires_e2e_adapter_binding() -> None:
    case = make_view_case("submit_case", "Submit")

    validate_mapping_coverage(
        [case],
        {"Submit": AdapterMapping("Submit", "app.adapters:SubmitHttpAdapter", view="external", layer="external")},
    )

    try:
        validate_mapping_coverage([case], {"Submit": AdapterMapping("Submit", None, view="external", layer="external")})
    except SystemExit as exc:
        assert "does not define adapter" in str(exc)
    else:
        raise AssertionError("expected missing external action adapter to fail")


def test_hidden_action_does_not_require_adapter_binding() -> None:
    case = make_view_case("hidden_case", "HiddenWorkerProgress", view="internal", controllability="hidden")

    validate_mapping_coverage([case], {})


def test_observable_external_action_requires_projector_not_assertion_adapter() -> None:
    case = make_view_case("observe_case", "ObserveStatus", controllability="observable")

    validate_mapping_coverage(
        [case],
        {
            "ObserveStatus": AdapterMapping(
                "ObserveStatus",
                None,
                view="external",
                layer="external",
                controllability="observable",
                projector="app.projectors:RequestStateProjector",
            )
        },
    )

    try:
        validate_mapping_coverage(
            [case],
            {
                "ObserveStatus": AdapterMapping(
                    "ObserveStatus",
                    None,
                    view="external",
                    layer="external",
                    controllability="observable",
                    expected_projection="app.projectors:ExpectedRequestState",
                )
            },
        )
    except SystemExit as exc:
        assert "missing projector" in str(exc)
    else:
        raise AssertionError("expected observable action without projector to fail")


def test_load_mappings_supports_external_action_bindings(tmp_path: Path) -> None:
    path = tmp_path / "bindings.toml"
    path.write_text(
        """[actions.Submit]
view = "external"
layer = "external"
controllability = "e2e_direct"
adapter = "app.adapters:SubmitHttpAdapter"
projector = "app.projectors:RequestStateProjector"
assertion = "app.assertions:DefaultHttpAssertion"
kind = "request-http"
""",
        encoding="utf-8",
    )

    mappings = load_mappings(path)

    assert mappings["Submit"] == AdapterMapping(
        label="Submit",
        adapter="app.adapters:SubmitHttpAdapter",
        view="external",
        layer="external",
        controllability="e2e_direct",
        projector="app.projectors:RequestStateProjector",
        assertion="app.assertions:DefaultHttpAssertion",
        kind="request-http",
        order=0,
    )


def test_load_mappings_supports_yaml_action_bindings(tmp_path: Path) -> None:
    path = tmp_path / "bindings.yml"
    path.write_text(
        """actions:
  Submit:
    view: external
    layer: external
    controllability: e2e_direct
    adapter: app.adapters:SubmitHttpAdapter
    projector: app.projectors:RequestStateProjector
    kind: request-http
""",
        encoding="utf-8",
    )

    mappings = load_mappings(path)

    assert mappings["Submit"].adapter == "app.adapters:SubmitHttpAdapter"
    assert mappings["Submit"].projector == "app.projectors:RequestStateProjector"
    assert mappings["Submit"].kind == "request-http"


def test_batched_execution_runs_lifecycle_hooks_by_kind(tmp_path: Path) -> None:
    module_path = tmp_path / "lifecycle_adapters.py"
    module_path.write_text(
        """EVENTS = []


class SubmitAdapter:
    def setup_all(self, ctx):
        EVENTS.append(("setup_all", ctx.kind, tuple(case.name for case in ctx.cases)))
        ctx.shared["ready"] = True

    def setup(self, ctx):
        EVENTS.append(("setup", ctx.kind, ctx.case.name, ctx.shared["ready"]))

    def run(self, case, work_dir=None):
        EVENTS.append(("run", case.name, work_dir.name))

    def teardown(self, ctx):
        EVENTS.append(("teardown", ctx.kind, ctx.case.name, ctx.result is not None, ctx.error is None))

    def teardown_all(self, ctx):
        EVENTS.append(("teardown_all", ctx.kind, tuple(case.name for case in ctx.cases), ctx.shared["ready"]))
""",
        encoding="utf-8",
    )
    sys.path.insert(0, str(tmp_path))
    import lifecycle_adapters

    case1 = make_view_case("case_1", "Submit")
    case2 = make_view_case("case_2", "Retry")
    mappings = {
        "Submit": AdapterMapping("Submit", "lifecycle_adapters:SubmitAdapter", kind="request-http"),
        "Retry": AdapterMapping("Retry", "lifecycle_adapters:SubmitAdapter", kind="request-http"),
    }

    execute_cases_in_batch(cases=[case1, case2], mappings=mappings, work_dir=tmp_path / "work", import_roots=[tmp_path])

    assert lifecycle_adapters.EVENTS == [
        ("setup_all", "request-http", ("case_1", "case_2")),
        ("setup", "request-http", "case_1", True),
        ("run", "case_1", "case_1"),
        ("teardown", "request-http", "case_1", True, True),
        ("setup", "request-http", "case_2", True),
        ("run", "case_2", "case_2"),
        ("teardown", "request-http", "case_2", True, True),
        ("teardown_all", "request-http", ("case_1", "case_2"), True),
    ]


def test_batched_execution_tears_down_after_case_failure(tmp_path: Path) -> None:
    module_path = tmp_path / "failing_lifecycle_adapters.py"
    module_path.write_text(
        """EVENTS = []


class FailingAdapter:
    def setup_all(self, ctx):
        EVENTS.append(("setup_all", ctx.kind))

    def setup(self, ctx):
        EVENTS.append(("setup", ctx.case.name))

    def run(self, case, work_dir=None):
        EVENTS.append(("run", case.name))
        raise RuntimeError("cluster state invalid")

    def teardown(self, ctx):
        EVENTS.append(("teardown", ctx.case.name, type(ctx.error).__name__))

    def teardown_all(self, ctx):
        EVENTS.append(("teardown_all", ctx.kind))
""",
        encoding="utf-8",
    )
    sys.path.insert(0, str(tmp_path))
    import failing_lifecycle_adapters

    case = make_view_case("case_1", "Submit")
    mappings = {"Submit": AdapterMapping("Submit", "failing_lifecycle_adapters:FailingAdapter", kind="request-http")}

    try:
        execute_cases_in_batch(cases=[case], mappings=mappings, work_dir=tmp_path / "work", import_roots=[tmp_path])
    except SystemExit as exc:
        assert "cluster state invalid" in str(exc)
    else:
        raise AssertionError("expected failing case to fail batch execution")

    assert failing_lifecycle_adapters.EVENTS == [
        ("setup_all", "request-http"),
        ("setup", "case_1"),
        ("run", "case_1"),
        ("teardown", "case_1", "RuntimeError"),
        ("teardown_all", "request-http"),
    ]


def test_external_projected_state_assertion_compares_case_after_to_actual_projection(tmp_path: Path) -> None:
    module_path = tmp_path / "state_projection_adapters.py"
    module_path.write_text(
        """EVENTS = []


class SubmitAdapter:
    def run(self, case, work_dir=None):
        EVENTS.append(("run", case.name))


class RequestStateProjector:
    def observe(self, ctx):
        EVENTS.append(("observe", ctx.case.name, ctx.expected))
        return {"request": "r1", "visible_status": "completed"}
""",
        encoding="utf-8",
    )
    sys.path.insert(0, str(tmp_path))
    import state_projection_adapters

    case = make_view_case(
        "case_1",
        "Submit",
        after={"request": "r1", "visible_status": "completed"},
    )
    mappings = {
        "Submit": AdapterMapping(
            "Submit",
            "state_projection_adapters:SubmitAdapter",
            projector="state_projection_adapters:RequestStateProjector",
            kind="request-http",
        )
    }

    execute_cases_in_batch(cases=[case], mappings=mappings, work_dir=tmp_path / "work", import_roots=[tmp_path])

    assert state_projection_adapters.EVENTS == [
        ("run", "case_1"),
        ("observe", "case_1", {"request": "r1", "visible_status": "completed"}),
    ]


def test_observable_external_case_runs_projector_without_action_adapter(tmp_path: Path) -> None:
    module_path = tmp_path / "observable_projection_adapters.py"
    module_path.write_text(
        """EVENTS = []


class RequestStateProjector:
    def observe(self, ctx):
        EVENTS.append(("observe", ctx.case.name, ctx.result))
        return {"request": "r1", "visible_status": "completed"}
""",
        encoding="utf-8",
    )
    sys.path.insert(0, str(tmp_path))
    import observable_projection_adapters

    case = make_view_case(
        "observe_case",
        "ObserveStatus",
        controllability="observable",
        after={"request": "r1", "visible_status": "completed"},
    )
    mappings = {
        "ObserveStatus": AdapterMapping(
            "ObserveStatus",
            None,
            view="external",
            layer="external",
            controllability="observable",
            projector="observable_projection_adapters:RequestStateProjector",
            kind="request-http",
        )
    }

    execute_cases_in_batch(cases=[case], mappings=mappings, work_dir=tmp_path / "work", import_roots=[tmp_path])

    assert observable_projection_adapters.EVENTS == [("observe", "observe_case", None)]


def test_external_projected_state_assertion_reports_mismatch(tmp_path: Path) -> None:
    module_path = tmp_path / "mismatched_state_projection_adapters.py"
    module_path.write_text(
        """class SubmitAdapter:
    def run(self, case, work_dir=None):
        pass


class RequestStateProjector:
    def observe(self, ctx):
        return {"request": "r1", "visible_status": "pending"}
""",
        encoding="utf-8",
    )
    sys.path.insert(0, str(tmp_path))

    case = make_view_case(
        "case_1",
        "Submit",
        after={"request": "r1", "visible_status": "completed"},
    )
    mappings = {
        "Submit": AdapterMapping(
            "Submit",
            "mismatched_state_projection_adapters:SubmitAdapter",
            projector="mismatched_state_projection_adapters:RequestStateProjector",
            kind="request-http",
        )
    }

    try:
        execute_cases_in_batch(cases=[case], mappings=mappings, work_dir=tmp_path / "work", import_roots=[tmp_path])
    except SystemExit as exc:
        assert "projected state mismatch" in str(exc)
    else:
        raise AssertionError("expected projected state mismatch to fail")


def test_non_batch_generated_program_runs_projected_state_assertion(tmp_path: Path) -> None:
    package_dir = tmp_path / "external_cases"
    render_python_package(
        module="Program",
        states={"0": {"status": "pending"}, "1": {"status": "completed"}},
        edges=[Edge("0", "1", "Submit")],
        package_dir=package_dir,
        view="external",
        action_metadata={"Submit": ActionMetadata("Submit", "external", "e2e_direct", ("testgraph",))},
    )
    module_path = tmp_path / "non_batch_projection_adapters.py"
    module_path.write_text(
        """from spec_double_compiler.runtime import CaseRunResult


class SubmitAdapter:
    def run(self, case, work_dir=None):
        return CaseRunResult(output=case.output)


class RequestStateProjector:
    def observe(self, ctx):
        return {"status": "wrong"}
""",
        encoding="utf-8",
    )
    mapping = tmp_path / "bindings.toml"
    # MF-015: an external binding must declare its channel, its production
    # package, and its double|real port bindings. The adapter above imports
    # spec_double_compiler.runtime, which is the ADAPTER HARNESS rather than the
    # program under test -- the gate targets the declared production package, so
    # returning a CaseRunResult stays legal for a Test Graph adapter.
    mapping.write_text(
        """[external]
production_package = "program_under_test"

[external.port_bindings]
RequestPort = "real"

[actions.Submit]
view = "external"
channel = "http"
layer = "external"
controllability = "e2e_direct"
adapter = "non_batch_projection_adapters:SubmitAdapter"
projector = "non_batch_projection_adapters:RequestStateProjector"
kind = "request-http"
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "run_generated_case_adapters.py"),
            str(package_dir),
            "--mapping",
            str(mapping),
            "--view",
            "external",
            "--work-dir",
            str(tmp_path / "work"),
            "--import-root",
            str(tmp_path),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "projected state mismatch" in result.stdout + result.stderr


def test_external_expected_projection_can_interpolate_comparable_state(tmp_path: Path) -> None:
    module_path = tmp_path / "interpolated_state_projection_adapters.py"
    module_path.write_text(
        """def expected_visible_state(ctx):
    return {"visible_status": ctx.case.after["visible_status"]}


class SubmitAdapter:
    def run(self, case, work_dir=None):
        pass


class RequestStateProjector:
    def observe(self, ctx):
        return {"visible_status": "completed"}
""",
        encoding="utf-8",
    )
    sys.path.insert(0, str(tmp_path))

    case = make_view_case(
        "case_1",
        "Submit",
        after={"request": "r1", "visible_status": "completed", "internal_counter": 7},
    )
    mappings = {
        "Submit": AdapterMapping(
            "Submit",
            "interpolated_state_projection_adapters:SubmitAdapter",
            expected_projection="interpolated_state_projection_adapters:expected_visible_state",
            projector="interpolated_state_projection_adapters:RequestStateProjector",
            kind="request-http",
        )
    }

    execute_cases_in_batch(cases=[case], mappings=mappings, work_dir=tmp_path / "work", import_roots=[tmp_path])


if __name__ == "__main__":
    test_adapter_mapping_prefers_toml_order_for_fine_labels()
    test_adapter_accepts_case_uses_can_run()
    test_assert_case_result_compares_semantic_projection()
