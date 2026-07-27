"""CM-01: the `case_modules:` manifest block and the coverage aggregation report.

The report is advisory by construction. The tests below pin that: uncovered
actions are named and the exit code is 0, and "declared but not generated" stays
distinct from "generated zero cases", because a declaration is an intention and
this report counts cases.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import case_modules
from scripts.extract_spec_manifest import parse_simple_yaml


MANIFEST = """module: Shop

case_modules:
  Aspect_HappyPath:
    extends: External
    view: external
    form: slice
    actions:
      - SubmitCreateAccount
      - SubmitCheckout
  Aspect_Resubmit:
    extends: External
    view: external
    form: given
    actions:
      - SubmitDuplicateCheckout
    claim: >-
      Resubmission does not depend on cart contents, so the aspect starts from
      an asserted pre-state instead of enumerating a path to one.
"""


def write_manifest(tmp_path: Path, text: str = MANIFEST) -> Path:
    path = tmp_path / "spec_manifest.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_declarations_carry_form_scope_and_claim(tmp_path: Path) -> None:
    declarations = case_modules.declarations_from_manifest(write_manifest(tmp_path))

    assert sorted(declarations) == ["Aspect_HappyPath", "Aspect_Resubmit"]
    happy = declarations["Aspect_HappyPath"]
    assert happy.extends == "External"
    assert happy.form == "slice"
    assert happy.actions == ("SubmitCreateAccount", "SubmitCheckout")
    assert happy.claim is None
    assert declarations["Aspect_Resubmit"].claim.startswith("Resubmission does not depend")


def test_a_given_without_a_recorded_claim_is_a_schema_error() -> None:
    manifest = parse_simple_yaml(
        "case_modules:\n"
        "  Aspect_Resubmit:\n"
        "    extends: External\n"
        "    form: given\n"
        "    actions: [SubmitDuplicateCheckout]\n"
    )

    errors = case_modules.validate_case_modules(manifest)

    assert len(errors) == 1
    assert "claim" in errors[0] and "unreviewable" in errors[0]


def test_missing_extends_and_actions_are_both_reported() -> None:
    manifest = parse_simple_yaml("case_modules:\n  Aspect:\n    form: slice\n")

    errors = case_modules.validate_case_modules(manifest)

    assert any("`extends:`" in error for error in errors)
    assert any("`actions:`" in error for error in errors)


def test_a_manifest_without_the_block_is_not_a_problem() -> None:
    assert case_modules.validate_case_modules({"module": "Shop"}) == []
    assert case_modules.load_declarations({"module": "Shop"}) == {}


def test_a_malformed_block_warns_and_never_refuses_a_generation(tmp_path: Path, capsys) -> None:
    path = write_manifest(tmp_path, "case_modules:\n  Aspect:\n    form: slice\n")

    declaration = case_modules.declaration_for(path, "Aspect", warn_stream=sys.stderr)

    assert declaration is None
    assert "unusable" in capsys.readouterr().err


def make_corpus(
    tmp_path: Path,
    module: str,
    counts: dict[str, int],
    declared_view_actions: list[str],
    declaration: case_modules.CaseModuleDeclaration | None,
) -> Path:
    package = tmp_path / f"{module}_cases"
    package.mkdir(parents=True, exist_ok=True)
    case_modules.write_coverage_record(
        package,
        case_modules.coverage_record(
            module=module,
            view="external",
            action_counts=counts,
            declared_view_actions=declared_view_actions,
            declaration=declaration,
            source=str(package),
        ),
    )
    return package


VIEW_ACTIONS = [
    "SubmitCreateAccount",
    "SubmitCheckout",
    "SubmitDuplicateCheckout",
    "RunFulfillmentWorker",
]


def build(tmp_path: Path, packages: list[Path]) -> case_modules.CoverageReport:
    return case_modules.build_report(
        manifest_path=write_manifest(tmp_path),
        corpora=[case_modules.read_coverage_record(path) for path in packages],
        view="external",
        view_actions=VIEW_ACTIONS,
    )


def test_report_names_the_action_no_module_enters(tmp_path: Path) -> None:
    declarations = case_modules.declarations_from_manifest(write_manifest(tmp_path))
    happy = make_corpus(
        tmp_path,
        "Aspect_HappyPath",
        {"SubmitCreateAccount": 2, "SubmitCheckout": 52},
        VIEW_ACTIONS,
        declarations["Aspect_HappyPath"],
    )
    resubmit = make_corpus(
        tmp_path,
        "Aspect_Resubmit",
        {"SubmitDuplicateCheckout": 4},
        VIEW_ACTIONS,
        declarations["Aspect_Resubmit"],
    )

    report = build(tmp_path, [happy, resubmit])

    assert report.uncovered_actions == ["RunFulfillmentWorker"]
    assert report.entered_by("SubmitCheckout") == ["Aspect_HappyPath"]
    rendered = case_modules.render_report(report)
    assert "RunFulfillmentWorker (declared in no module's scope)" in rendered
    assert "UNMEASURED" in rendered  # the view's own corpus was not supplied


def test_the_views_own_corpus_covers_what_no_module_enters(tmp_path: Path) -> None:
    declarations = case_modules.declarations_from_manifest(write_manifest(tmp_path))
    happy = make_corpus(
        tmp_path,
        "Aspect_HappyPath",
        {"SubmitCreateAccount": 2, "SubmitCheckout": 52},
        VIEW_ACTIONS,
        declarations["Aspect_HappyPath"],
    )
    view = make_corpus(
        tmp_path,
        "External",
        {name: 4 for name in VIEW_ACTIONS},
        VIEW_ACTIONS,
        None,
    )

    report = build(tmp_path, [happy, view])

    assert report.uncovered_actions == []
    assert report.view_count("RunFulfillmentWorker") == 4
    assert report.unmeasured_modules == ["Aspect_Resubmit"]


def test_a_declared_but_ungenerated_module_covers_nothing(tmp_path: Path) -> None:
    declarations = case_modules.declarations_from_manifest(write_manifest(tmp_path))
    happy = make_corpus(
        tmp_path,
        "Aspect_HappyPath",
        {"SubmitCreateAccount": 2, "SubmitCheckout": 52},
        VIEW_ACTIONS,
        declarations["Aspect_HappyPath"],
    )

    report = build(tmp_path, [happy])

    assert report.unmeasured_modules == ["Aspect_Resubmit"]
    assert "SubmitDuplicateCheckout" in report.uncovered_actions
    rendered = case_modules.render_report(report)
    assert "declared in the scope of Aspect_Resubmit, which was not measured" in rendered


def test_declaration_drift_is_reported_when_a_module_leaves_its_scope(tmp_path: Path) -> None:
    declarations = case_modules.declarations_from_manifest(write_manifest(tmp_path))
    drifted = make_corpus(
        tmp_path,
        "Aspect_HappyPath",
        {"SubmitCreateAccount": 2, "SubmitCheckout": 52, "RunFulfillmentWorker": 9},
        VIEW_ACTIONS,
        declarations["Aspect_HappyPath"],
    )

    rendered = case_modules.render_report(build(tmp_path, [drifted]))

    assert "declaration drift" in rendered
    assert "RunFulfillmentWorker outside its `actions:` scope" in rendered


def test_the_report_exits_zero_even_with_uncovered_actions(tmp_path: Path, capsys) -> None:
    declarations = case_modules.declarations_from_manifest(write_manifest(tmp_path))
    happy = make_corpus(
        tmp_path,
        "Aspect_HappyPath",
        {"SubmitCreateAccount": 2},
        VIEW_ACTIONS,
        declarations["Aspect_HappyPath"],
    )
    out = tmp_path / "report.json"

    exit_code = case_modules.main(
        [
            "coverage",
            "--manifest",
            str(tmp_path / "spec_manifest.yaml"),
            "--corpus",
            str(happy),
            "--view",
            "external",
            "--json",
            str(out),
        ]
    )

    assert exit_code == 0
    captured = capsys.readouterr().out
    assert "UNCOVERED:" in captured
    assert "gates nothing" in captured
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["uncovered_actions"]
    assert payload["gates"].startswith("none")


def test_a_corpus_without_a_coverage_record_is_could_not_measure(tmp_path: Path) -> None:
    write_manifest(tmp_path)
    empty = tmp_path / "empty_cases"
    empty.mkdir()

    exit_code = case_modules.main(
        ["coverage", "--manifest", str(tmp_path / "spec_manifest.yaml"), "--corpus", str(empty)]
    )

    assert exit_code == 2


def test_validate_subcommand_reports_each_declaration(tmp_path: Path, capsys) -> None:
    write_manifest(tmp_path)

    exit_code = case_modules.main(["validate", "--manifest", str(tmp_path / "spec_manifest.yaml")])

    assert exit_code == 0
    out = capsys.readouterr().out
    assert "Aspect_HappyPath: slice of External, 2 action(s)" in out
    assert "Aspect_Resubmit: given of External, 1 action(s), claim recorded" in out


def test_the_shipped_example_declares_its_case_modules() -> None:
    manifest = ROOT / "examples/distributed_history/specs/program_model/spec_manifest.yaml"

    declarations = case_modules.declarations_from_manifest(manifest)

    assert sorted(declarations) == [
        "Scenario_CheckoutHappyPath",
        "Scenario_IdempotentResubmit",
        "Scenario_RejectedRequests",
    ]
    given = declarations["Scenario_IdempotentResubmit"]
    assert given.form == "given"
    assert given.claim and "independent of the reachable" in given.claim
