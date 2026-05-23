from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.generate_cases_from_tlc_dump import labels_for_case, parse_tlc_function, parse_tlc_value, py_repr


def test_parse_set_keeps_sequence_members_intact() -> None:
    assert parse_tlc_value("{<<1,2>>, <<3,4>>}") == frozenset({(1, 2), (3, 4)})


def test_parse_set_keeps_record_members_intact() -> None:
    assert parse_tlc_value("{[a |-> 1, b |-> 2], [a |-> 3, b |-> 4]}") == frozenset(
        {"[a |-> 1, b |-> 2]", "[a |-> 3, b |-> 4]"}
    )


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


if __name__ == "__main__":
    test_parse_set_keeps_sequence_members_intact()
    test_parse_set_keeps_record_members_intact()
    test_parse_function_ignores_nested_function_separators()
    test_parse_set_can_contain_function_members()
    test_py_repr_handles_nested_set_members_deterministically()
    test_labels_for_case_adds_labeler_output_after_action()
