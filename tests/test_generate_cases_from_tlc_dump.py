from pathlib import Path
import sys
import importlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.generate_cases_from_tlc_dump import (
    ActionMetadata,
    Edge,
    labels_for_case,
    load_action_metadata,
    parse_tlc_function,
    parse_state_label,
    parse_tlc_value,
    py_repr,
    render_python_package,
)


def test_parse_set_keeps_sequence_members_intact() -> None:
    assert parse_tlc_value("{<<1,2>>, <<3,4>>}") == frozenset({(1, 2), (3, 4)})


def test_parse_set_parses_record_members_structurally() -> None:
    assert parse_tlc_value("{[a |-> 1, b |-> 2], [a |-> 3, b |-> 4]}") == frozenset(
        {
            frozenset({("a", 1), ("b", 2)}),
            frozenset({("a", 3), ("b", 4)}),
        }
    )


def test_parse_state_label_keeps_multiline_record_values() -> None:
    assert parse_state_label(
        '/\\ lastExternalAction = [ name |-> "Submit",\\n'
        '  params |-> [account |-> "acct-1", sku |-> "sku-1"] ]\\n'
        '/\\ status = "ok"'
    ) == {
        "lastExternalAction": {
            "name": "Submit",
            "params": {"account": "acct-1", "sku": "sku-1"},
        },
        "status": "ok",
    }


def test_parse_function_ignores_nested_function_separators() -> None:
    assert parse_tlc_function('("outer" :> ("left" :> 1 @@ "right" :> 2) @@ "tail" :> <<3,4>>)') == {
        "outer": {"left": 1, "right": 2},
        "tail": (3, 4),
    }


def test_parse_set_can_contain_function_members() -> None:
    assert parse_tlc_value('{("a" :> 1 @@ "b" :> <<2,3>>)}') == frozenset(
        {frozenset({("a", 1), ("b", (2, 3))})}
    )


def test_py_repr_handles_nested_set_members_deterministically() -> None:
    assert py_repr(frozenset({(3, 4), (1, 2)})) == "frozenset([(1, 2), (3, 4)])"


def test_labels_for_case_adds_labeler_output_after_action() -> None:
    labels = labels_for_case(
        before={"items": frozenset()},
        action="Create",
        after={"items": frozenset({"a"})},
        changes={"items": {"before": frozenset(), "after": frozenset({"a"})}},
        labelers=[lambda before, action, after, changed: ["non_empty", action]],
    )

    assert labels == ["Create", "non_empty"]


def import_generated_cases(tmp_path: Path, package: str):
    for name in list(sys.modules):
        if name == package or name.startswith(f"{package}."):
            del sys.modules[name]
    sys.path.insert(0, str(tmp_path))
    return importlib.import_module(f"{package}.cases")


def tiny_state_graph() -> tuple[dict[str, dict[str, object]], list[Edge]]:
    states = {
        "0": {"status": "none"},
        "1": {"status": "pending"},
        "2": {"status": "visible"},
        "3": {"status": "hidden"},
    }
    edges = [
        Edge(source="0", target="1", action="AcceptRequest"),
        Edge(source="1", target="2", action="Submit"),
        Edge(source="2", target="3", action="HiddenWorkerProgress"),
    ]
    return states, edges


def test_internal_generation_emits_only_spec_unit_internal_actions(tmp_path: Path) -> None:
    states, edges = tiny_state_graph()
    render_python_package(
        module="Program",
        states=states,
        edges=edges,
        package_dir=tmp_path / "internal_cases",
        view="internal",
        action_metadata={
            "AcceptRequest": ActionMetadata("AcceptRequest", "internal", "unit_direct", ("spec_unit",)),
            "Submit": ActionMetadata("Submit", "external", "e2e_direct", ("testgraph",)),
            "HiddenWorkerProgress": ActionMetadata("HiddenWorkerProgress", "internal", "hidden", ()),
        },
    )

    cases_module = import_generated_cases(tmp_path, "internal_cases")

    assert [case.input.action for case in cases_module.CASES] == ["AcceptRequest"]
    case = cases_module.CASES[0]
    assert case.schema_version == "tla-testgraph.trace.v1"
    assert case.view == "internal"
    assert case.layer == "internal"
    assert case.controllability == "unit_direct"
    assert case.generates == frozenset({"spec_unit"})


def test_external_generation_emits_only_testgraph_external_actions(tmp_path: Path) -> None:
    states, edges = tiny_state_graph()
    render_python_package(
        module="Program",
        states=states,
        edges=edges,
        package_dir=tmp_path / "external_cases",
        view="external",
        action_metadata={
            "AcceptRequest": ActionMetadata("AcceptRequest", "internal", "unit_direct", ("spec_unit",)),
            "Submit": ActionMetadata("Submit", "external", "e2e_direct", ("testgraph",), ("smoke",)),
            "HiddenWorkerProgress": ActionMetadata("HiddenWorkerProgress", "internal", "hidden", ()),
        },
    )

    cases_module = import_generated_cases(tmp_path, "external_cases")

    assert [case.input.action for case in cases_module.CASES] == ["Submit"]
    case = cases_module.CASES[0]
    assert case.view == "external"
    assert case.layer == "external"
    assert case.controllability == "e2e_direct"
    assert case.generates == frozenset({"testgraph"})
    assert case.tags == frozenset({"smoke"})


def test_generation_derives_action_params_from_last_action_marker(tmp_path: Path) -> None:
    states = {
        "0": {"lastExternalAction": {"name": "Init", "params": ()}, "status": "none"},
        "1": {
            "lastExternalAction": {
                "name": "Submit",
                "params": {"account": "acct-1", "sku": "sku-1"},
            },
            "status": "visible",
        },
    }
    render_python_package(
        module="Program",
        states=states,
        edges=[Edge(source="0", target="1", action="Submit")],
        package_dir=tmp_path / "external_cases",
        view="external",
        action_metadata={"Submit": ActionMetadata("Submit", "external", "e2e_direct", ("testgraph",))},
    )

    cases_module = import_generated_cases(tmp_path, "external_cases")

    assert cases_module.CASES[0].input.params == {"account": "acct-1", "sku": "sku-1"}


def test_generation_uses_projectors_and_projected_dedupe(tmp_path: Path) -> None:
    states = {
        "0": {"lastExternalAction": {"name": "Init", "params": ()}, "raw": 1, "status": "empty"},
        "1": {"lastExternalAction": {"name": "Submit", "params": {"id": "r1"}}, "raw": 2, "status": "done"},
        "2": {"lastExternalAction": {"name": "Init", "params": ()}, "raw": 3, "status": "empty"},
        "3": {"lastExternalAction": {"name": "Submit", "params": {"id": "r1"}}, "raw": 4, "status": "done"},
    }

    def state_projector(state):
        return {"status": state["status"]}

    def output_projector(**kwargs):
        return {"accepted": kwargs["action"] == "Submit"}

    render_python_package(
        module="Program",
        states=states,
        edges=[Edge(source="0", target="1", action="Submit"), Edge(source="2", target="3", action="Submit")],
        package_dir=tmp_path / "external_cases",
        view="external",
        action_metadata={"Submit": ActionMetadata("Submit", "external", "e2e_direct", ("testgraph",))},
        state_projector=state_projector,
        output_projector=output_projector,
        dedupe="projected",
    )

    cases_module = import_generated_cases(tmp_path, "external_cases")

    assert len(cases_module.CASES) == 1
    assert cases_module.CASES[0].before == {"status": "empty"}
    assert cases_module.CASES[0].after == {"status": "done"}
    assert cases_module.CASES[0].output == {"accepted": True}


def test_legacy_generation_defaults_to_internal_view_without_filtering(tmp_path: Path) -> None:
    states, edges = tiny_state_graph()
    render_python_package(
        module="Program",
        states=states,
        edges=edges,
        package_dir=tmp_path / "legacy_cases",
    )

    cases_module = import_generated_cases(tmp_path, "legacy_cases")

    assert [case.input.action for case in cases_module.CASES] == [
        "AcceptRequest",
        "Submit",
        "HiddenWorkerProgress",
    ]
    assert {case.view for case in cases_module.CASES} == {"internal"}


def test_load_action_metadata_from_actions_yaml(tmp_path: Path) -> None:
    path = tmp_path / "actions.yml"
    path.write_text(
        """actions:
  Submit:
    layer: external
    controllability: e2e_direct
    generates:
      - testgraph
    tags:
      - smoke
""",
        encoding="utf-8",
    )

    metadata = load_action_metadata(path)

    assert metadata["Submit"] == ActionMetadata(
        name="Submit",
        layer="external",
        controllability="e2e_direct",
        generates=("testgraph",),
        tags=("smoke",),
    )


if __name__ == "__main__":
    test_parse_set_keeps_sequence_members_intact()
    test_parse_set_parses_record_members_structurally()
    test_parse_state_label_keeps_multiline_record_values()
    test_parse_function_ignores_nested_function_separators()
    test_parse_set_can_contain_function_members()
    test_py_repr_handles_nested_set_members_deterministically()
    test_labels_for_case_adds_labeler_output_after_action()
