from dataclasses import dataclass
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.run_generated_case_adapters import AdapterMapping, adapter_for_case, validate_adapter_capabilities
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


if __name__ == "__main__":
    test_adapter_mapping_prefers_toml_order_for_fine_labels()
    test_adapter_accepts_case_uses_can_run()
    test_assert_case_result_compares_semantic_projection()

