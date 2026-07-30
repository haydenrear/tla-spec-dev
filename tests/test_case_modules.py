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


# --------------------------------------------------------------------------
# RP-03 / EV-02-DF-02: a case module generates from where the docs put it
# --------------------------------------------------------------------------


def build_split_layout(tmp_path: Path) -> tuple[Path, Path]:
    """The documented layout: a view in program_model/, a case module beside it.

    Returns ``(case module .tla, view .tla)``.
    """
    view_dir = tmp_path / "specs" / "program_model"
    module_dir = tmp_path / "specs" / "case_modules"
    view_dir.mkdir(parents=True)
    module_dir.mkdir(parents=True)
    (view_dir / "Pipeline.tla").write_text(
        "---- MODULE Pipeline ----\n"
        "EXTENDS Naturals, FiniteSets\n"
        "CONSTANTS Items\n"
        "VARIABLES inbox, done\n"
        "vars == << inbox, done >>\n"
        "Init ==\n"
        "  /\\ inbox = Items\n"
        "  /\\ done = {}\n"
        "Accept(i) ==\n"
        "  /\\ i \\in inbox\n"
        "  /\\ inbox' = inbox \\ {i}\n"
        "  /\\ done' = done \\cup {i}\n"
        "Next == \\E i \\in inbox : Accept(i)\n"
        "====\n",
        encoding="utf-8",
    )
    (view_dir / "spec_manifest.yaml").write_text(MANIFEST, encoding="utf-8")
    (module_dir / "Scenario_Accept.tla").write_text(
        "---- MODULE Scenario_Accept ----\n"
        "EXTENDS Pipeline\n"
        "AcceptNext == \\E i \\in inbox : Accept(i)\n"
        "AcceptSpec == Init /\\ [][AcceptNext]_vars\n"
        "====\n",
        encoding="utf-8",
    )
    return module_dir / "Scenario_Accept.tla", view_dir / "Pipeline.tla"


def test_a_case_module_resolves_its_view_from_a_sibling_directory(tmp_path: Path) -> None:
    """EV-02-DF-02, the acceptance property: reproducible IN PLACE, no copying."""
    module, view = build_split_layout(tmp_path)

    search_path = case_modules.resolve_search_path(module)

    assert not search_path.is_self_contained
    assert search_path.directories == (module.parent, view.parent)
    assert dict(search_path.resolved) == {"Pipeline": view}
    assert "Pipeline" in search_path.describe()


def test_the_search_path_reaches_tlc_as_the_tla_library_property(tmp_path: Path) -> None:
    module, view = build_split_layout(tmp_path)

    env = case_modules.tlc_environment(case_modules.resolve_search_path(module), {})

    option = env["JAVA_TOOL_OPTIONS"]
    assert option.startswith(f"-D{case_modules.TLA_LIBRARY_PROPERTY}=")
    assert str(view.parent) in option


def test_a_self_contained_module_sets_no_java_options(tmp_path: Path) -> None:
    """The common case must be byte-identical to before: no property, no JVM noise."""
    (tmp_path / "Solo.tla").write_text(
        "---- MODULE Solo ----\nEXTENDS Naturals\nVARIABLES x\nInit == x = 0\n====\n",
        encoding="utf-8",
    )

    search_path = case_modules.resolve_search_path(tmp_path / "Solo.tla")

    assert search_path.is_self_contained
    assert case_modules.tlc_environment(search_path, {}) == {}


def test_an_unresolvable_extends_names_the_module_and_every_directory(tmp_path: Path) -> None:
    module, _ = build_split_layout(tmp_path)
    module.write_text(
        "---- MODULE Scenario_Accept ----\nEXTENDS Nowhere\n====\n", encoding="utf-8"
    )

    with pytest.raises(case_modules.ModuleSearchError) as error:
        case_modules.resolve_search_path(module)

    message = str(error.value)
    assert "EXTENDS Nowhere" in message
    assert "Nowhere.tla is in none of the directories" in message
    assert str(module.parent) in message
    assert "--module-path" in message
    # It must not be the old symptom: a TLC AbortException the caller has to read.
    assert "AbortException" not in message


def test_two_siblings_defining_the_same_module_is_an_error_not_a_coin_flip(
    tmp_path: Path,
) -> None:
    module, view = build_split_layout(tmp_path)
    twin = tmp_path / "specs" / "desired_program_model"
    twin.mkdir()
    (twin / "Pipeline.tla").write_text(view.read_text(encoding="utf-8"), encoding="utf-8")

    with pytest.raises(case_modules.ModuleSearchError) as error:
        case_modules.resolve_search_path(module)

    message = str(error.value)
    assert "more than one directory" in message
    assert str(twin) in message and str(view.parent) in message


def test_an_explicit_module_path_wins_over_the_ambiguous_siblings(tmp_path: Path) -> None:
    module, view = build_split_layout(tmp_path)
    twin = tmp_path / "specs" / "desired_program_model"
    twin.mkdir()
    (twin / "Pipeline.tla").write_text(view.read_text(encoding="utf-8"), encoding="utf-8")

    search_path = case_modules.resolve_search_path(module, [view.parent])

    assert dict(search_path.resolved) == {"Pipeline": view}


def test_a_module_beside_the_case_module_wins_over_a_sibling(tmp_path: Path) -> None:
    module, view = build_split_layout(tmp_path)
    local = module.parent / "Pipeline.tla"
    local.write_text(view.read_text(encoding="utf-8"), encoding="utf-8")

    search_path = case_modules.resolve_search_path(module)

    assert search_path.is_self_contained
    assert dict(search_path.resolved) == {"Pipeline": local}


def test_the_manifest_is_found_along_the_search_path_not_beside_the_module(
    tmp_path: Path,
) -> None:
    """A case module has no manifest of its own; the VIEW's manifest governs it."""
    module, view = build_split_layout(tmp_path)
    search_path = case_modules.resolve_search_path(module)

    resolved = case_modules.resolve_manifest_path(module.parent, search_path)

    assert resolved == view.parent / "spec_manifest.yaml"
    assert resolved.is_file()


def test_the_hierarchy_is_ordered_base_module_first(tmp_path: Path) -> None:
    """Recipes and any other text union must read base modules before extenders."""
    module, view = build_split_layout(tmp_path)

    search_path = case_modules.resolve_search_path(module)

    assert search_path.files_base_first == (view, module)


def test_the_shipped_internal_fixture_generates_from_its_documented_location() -> None:
    """The ex4 modules live in specs/case_modules/ and must resolve from there."""
    fixture = ROOT / "examples/validation/ex4_pipeline_coherent"
    module = fixture / "specs/case_modules/Scenario_DeliveryPath.tla"

    search_path = case_modules.resolve_search_path(module)

    assert dict(search_path.resolved) == {
        "Pipeline": fixture / "specs/program_model/Pipeline.tla"
    }
    assert case_modules.resolve_manifest_path(module.parent, search_path) == (
        fixture / "specs/program_model/spec_manifest.yaml"
    )


# --------------------------------------------------------------------------
# RP-03: the generator side of the same defect
# --------------------------------------------------------------------------


def test_the_complexity_scanner_reads_the_same_search_path(tmp_path: Path) -> None:
    """The scan and the corpus must never resolve EXTENDS to different files."""
    from scripts.analyze_complexity import UnresolvedExtendsError, resolve_module

    module, view = build_split_layout(tmp_path)
    search_path = case_modules.resolve_search_path(module)

    with pytest.raises(UnresolvedExtendsError):
        resolve_module(module)

    resolved = resolve_module(module, search_path=list(search_path.directories))

    assert resolved.variables == ["inbox", "done"]
    assert "Pipeline" in resolved.modules


def test_param_recipes_come_from_the_whole_hierarchy(tmp_path: Path) -> None:
    """A case module declares no actions; reading only its text recovers nothing.

    Measured on ex4 before the fix: the view's corpus recovered 330/330 arguments
    and its two case modules recovered 0/50 and 0/6, so the adapters refused the
    case-module corpora outright with ``no usable argument for `i```.
    """
    from scripts.generate_cases_from_tlc_dump import build_recipes_for_hierarchy

    module, _ = build_split_layout(tmp_path)
    search_path = case_modules.resolve_search_path(module)

    assert build_recipes_for_hierarchy(module, None) == {}
    assert "Accept" in build_recipes_for_hierarchy(module, search_path)


def test_a_relative_out_says_where_it_landed(tmp_path: Path, capsys, monkeypatch) -> None:
    """EV-02: `--out generated` silently created a directory in the spec dir."""
    from scripts.generate_cases_from_tlc_dump import report_out_resolution

    spec_dir = tmp_path / "specs" / "program_model"
    spec_dir.mkdir(parents=True)
    monkeypatch.chdir(tmp_path)

    report_out_resolution(Path("generated"), spec_dir / "generated", spec_dir)

    out = capsys.readouterr().out
    assert "resolved to" in out and str(spec_dir / "generated") in out
    assert "SPEC DIRECTORY" in out

    capsys.readouterr()
    report_out_resolution(
        Path("generated"), (tmp_path / "generated").resolve(), spec_dir
    )
    assert capsys.readouterr().out == ""


def test_generation_refuses_before_tlc_when_a_module_is_missing(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """The failure arrives BEFORE the JVM starts, so it is not behind TLC's stack."""
    import scripts.generate_cases_from_tlc_dump as generator

    module, _ = build_split_layout(tmp_path)
    module.write_text(
        "---- MODULE Scenario_Accept ----\nEXTENDS Nowhere\n====\n", encoding="utf-8"
    )
    (module.parent / "Scenario_Accept.cfg").write_text(
        "SPECIFICATION AcceptSpec\n", encoding="utf-8"
    )

    def explode(*args, **kwargs):  # pragma: no cover - must never be reached
        raise AssertionError("TLC was started for a hierarchy that cannot resolve")

    monkeypatch.setattr(generator, "run_tlc_dump", explode)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "generate_cases_from_tlc_dump.py",
            str(module),
            str(module.parent / "Scenario_Accept.cfg"),
            "--out",
            str(tmp_path / "out"),
            "--view",
            "internal",
        ],
    )

    with pytest.raises(SystemExit) as exit_info:
        generator.main()

    assert "EXTENDS Nowhere" in str(exit_info.value)
    assert "--module-path" in str(exit_info.value)
