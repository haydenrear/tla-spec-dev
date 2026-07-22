"""CD-03: self-configured, composable fitness functions over the descriptor.

The load-bearing properties:

1. NO built-in rules -- with nothing configured, the scanner attaches no
   fitness report and prints no fitness section.
2. Rules compose with and/or/not over the descriptor's PUBLISHED facts, and
   a rule whose condition does not hold FIRES with a leaf-level trace.
3. Three-valued honesty: comparing against an unmeasurable fact (e.g. an
   UNKNOWN bound) yields status "unknown", never a silent pass or fail.
4. Advisory: any number of firings -- or a completely broken rules file --
   leaves the exit code at EXIT_PASS. Firings report, never block.
5. Persistence is per-project: the manifest's `fitness_functions:` block and a
   sibling `fitness_functions.yaml` both load, and both are named as sources.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest  # noqa: E402

from scripts.analyze_complexity import EXIT_PASS, analyze, main, render_text  # noqa: E402
from scripts.fitness_functions import (  # noqa: E402
    FACT_DOCS,
    FitnessRule,
    RuleError,
    evaluate_node,
    evaluate_rules,
    extract_facts,
    load_rules,
    run_fitness,
)

from tests.test_analyze_complexity import write_small_model  # noqa: E402


# ---------------------------------------------------------------------------
# Facts extraction from the descriptor payload
# ---------------------------------------------------------------------------


DESCRIPTOR = {
    "measured": {
        "dimensions": [
            {"variable": "started", "domain": "BOOLEAN", "cardinality": 2, "note": ""},
            {"variable": "finished", "domain": "BOOLEAN", "cardinality": 2, "note": ""},
            {"variable": "count", "domain": "0..2", "cardinality": 3, "note": ""},
            {"variable": "log", "domain": None, "cardinality": None, "note": "unconstrained"},
        ],
        "state_space_upper_bound": 12,
        "state_space_bound_known": True,
        "actions": [
            {"name": "Start", "reads": ["started"], "writes": ["started"]},
            {"name": "Finish", "reads": ["finished", "started"], "writes": ["finished"]},
            {"name": "Bump", "reads": ["count", "started"], "writes": ["count"]},
        ],
        "modularity": 0.25,
        "components": [["count", "finished", "started"], ["log"]],
        "port_crossing_actions": {},
        "dense_rows": {"started": 3},
        "dense_columns": [],
        "unread_by_invariant": ["log"],
        "unjustified_variables": None,
    },
}


def test_extract_facts_flattens_the_published_descriptor() -> None:
    facts = extract_facts(DESCRIPTOR)
    assert facts["bound"] == 12
    assert facts["bound_known"] is True
    assert facts["modularity"] == 0.25
    assert facts["component_count"] == 2
    assert facts["max_component_variables"] == 3
    # All three actions touch the {count, finished, started} component.
    assert facts["max_component_actions"] == 3
    assert facts["action_count"] == 3
    assert facts["variable_count"] == 4
    assert facts["god_state_count"] == 1
    assert facts["unread_by_invariant_count"] == 1
    # No justification table -> UNKNOWN, not zero.
    assert facts["unjustified_count"] is None
    assert facts["variable_domain"]["count"] == 3
    # An unconstrained variable's domain is UNKNOWN, not a convenient number.
    assert facts["variable_domain"]["log"] is None


# ---------------------------------------------------------------------------
# Leaf predicates and and/or/not composition
# ---------------------------------------------------------------------------


FACTS = extract_facts(DESCRIPTOR)


@pytest.mark.parametrize(
    ("op", "value", "expected"),
    [("<", 100, True), ("<=", 12, True), (">", 12, False), (">=", 13, False), ("==", 12, True), ("!=", 12, False)],
)
def test_every_comparison_op(op: str, value: int, expected: bool) -> None:
    holds, notes = evaluate_node({"fact": "bound", "op": op, "value": value}, FACTS)
    assert holds is expected
    assert len(notes) == 1 and "bound=12" in notes[0]


def test_variable_domain_is_the_parameterized_fact() -> None:
    holds, notes = evaluate_node(
        {"fact": "variable_domain", "var": "count", "op": "<=", "value": 3}, FACTS
    )
    assert holds is True
    assert "variable_domain(count)=3" in notes[0]


def test_no_god_state_is_expressible() -> None:
    holds, _ = evaluate_node({"fact": "god_state_count", "op": "==", "value": 0}, FACTS)
    assert holds is False  # `started` is a dense row in this descriptor.


def test_and_or_not_compose() -> None:
    true_leaf = {"fact": "bound", "op": "<", "value": 100}
    false_leaf = {"fact": "god_state_count", "op": "==", "value": 0}
    assert evaluate_node({"all": [true_leaf, false_leaf]}, FACTS)[0] is False
    assert evaluate_node({"any": [true_leaf, false_leaf]}, FACTS)[0] is True
    assert evaluate_node({"not": false_leaf}, FACTS)[0] is True
    nested = {"all": [true_leaf, {"any": [false_leaf, {"not": false_leaf}]}]}
    holds, notes = evaluate_node(nested, FACTS)
    assert holds is True
    # The trace names every leaf comparison encountered.
    assert len(notes) == 3


def test_unknown_fact_value_is_three_valued_not_a_silent_pass_or_fail() -> None:
    # `bound` UNKNOWN (the CD-01 F3 explicit-unknown case).
    facts = dict(FACTS, bound=None)
    holds, notes = evaluate_node({"fact": "bound", "op": "<", "value": 100}, facts)
    assert holds is None
    assert "UNKNOWN" in notes[0]
    # Kleene composition: unknown AND true -> unknown; unknown OR true -> true;
    # NOT unknown -> unknown.
    true_leaf = {"fact": "modularity", "op": ">=", "value": 0.1}
    unknown_leaf = {"fact": "bound", "op": "<", "value": 100}
    assert evaluate_node({"all": [unknown_leaf, true_leaf]}, facts)[0] is None
    assert evaluate_node({"any": [unknown_leaf, true_leaf]}, facts)[0] is True
    assert evaluate_node({"not": unknown_leaf}, facts)[0] is None
    # variable_domain of an unconstrained variable is likewise unknown.
    holds, _ = evaluate_node(
        {"fact": "variable_domain", "var": "log", "op": "<=", "value": 5}, FACTS
    )
    assert holds is None


@pytest.mark.parametrize(
    "node",
    [
        {"fact": "no_such_fact", "op": "<", "value": 1},
        {"fact": "bound", "op": "~", "value": 1},
        {"fact": "bound", "op": "<"},
        {"fact": "variable_domain", "op": "<", "value": 1},  # missing var:
        {"fact": "variable_domain", "var": "nope", "op": "<", "value": 1},
        {"all": []},
        {"nope": 1},
        {"all": [{"fact": "bound", "op": "<", "value": 1}], "extra": True},
        "not-a-mapping",
    ],
)
def test_malformed_nodes_raise_rule_error_with_a_named_cause(node: object) -> None:
    with pytest.raises(RuleError):
        evaluate_node(node, FACTS)


def test_rule_error_names_the_known_facts() -> None:
    with pytest.raises(RuleError) as exc:
        evaluate_node({"fact": "boundd", "op": "<", "value": 1}, FACTS)
    for fact in FACT_DOCS:
        assert fact in str(exc.value)


# ---------------------------------------------------------------------------
# Rule evaluation statuses
# ---------------------------------------------------------------------------


def test_evaluate_rules_maps_statuses_and_never_raises_on_invalid() -> None:
    rules = [
        FitnessRule("holds-rule", {"fact": "bound", "op": "<", "value": 100}),
        FitnessRule("fired-rule", {"fact": "god_state_count", "op": "==", "value": 0}),
        FitnessRule("unknown-rule", {"fact": "unjustified_count", "op": "==", "value": 0}),
        FitnessRule("invalid-rule", {"fact": "nope", "op": "<", "value": 1}),
    ]
    report = evaluate_rules(rules, FACTS, sources=["spec_manifest.yaml"])
    by_name = {r.name: r for r in report.results}
    assert by_name["holds-rule"].status == "holds"
    assert by_name["fired-rule"].status == "fired"
    assert by_name["unknown-rule"].status == "unknown"
    assert by_name["invalid-rule"].status == "invalid"
    assert [r.name for r in report.fired] == ["fired-rule"]
    assert by_name["fired-rule"].detail == "god_state_count=1 == 0 is FALSE"


# ---------------------------------------------------------------------------
# Per-project persistence: manifest block and sibling rules file
# ---------------------------------------------------------------------------


def test_no_configuration_means_no_rules_no_sources_no_errors(tmp_path: Path) -> None:
    """Ships with NO built-in rules."""
    rules, sources, errors = load_rules(None, tmp_path)
    assert (rules, sources, errors) == ([], [], [])
    assert run_fitness(None, tmp_path, DESCRIPTOR) is None
    assert run_fitness({"module": "Small"}, None, DESCRIPTOR) is None


def test_rules_load_from_manifest_and_rules_file_and_both_are_sources(
    tmp_path: Path,
) -> None:
    manifest = {
        "fitness_functions": [
            {"name": "from-manifest", "rule": {"fact": "bound", "op": "<", "value": 100}}
        ]
    }
    rules_file = tmp_path / "fitness_functions.yaml"
    rules_file.write_text(
        "fitness_functions:\n"
        "  - name: from-file\n"
        "    description: keep it modular\n"
        "    rule:\n"
        "      all:\n"
        "        - {fact: modularity, op: '>=', value: 0.1}\n"
        "        - {fact: god_state_count, op: ==, value: 0}\n",
        encoding="utf-8",
    )
    rules, sources, errors = load_rules(manifest, tmp_path)
    assert errors == []
    assert [r.name for r in rules] == ["from-manifest", "from-file"]
    assert rules[1].description == "keep it modular"
    assert len(sources) == 2 and str(rules_file) in sources


def test_json_rules_file_needs_only_the_standard_library(tmp_path: Path) -> None:
    """fitness_functions.json is the dependency-free persistence path: the CLI
    may run under a bare python3 with no PyYAML installed."""
    (tmp_path / "fitness_functions.json").write_text(
        json.dumps(
            {
                "fitness_functions": [
                    {
                        "name": "from-json",
                        "rule": {"fact": "bound", "op": "<", "value": 100},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    rules, sources, errors = load_rules(None, tmp_path)
    assert errors == []
    assert [r.name for r in rules] == ["from-json"]
    assert sources == [str(tmp_path / "fitness_functions.json")]


def test_broken_configuration_is_an_advisory_error_never_a_raise(tmp_path: Path) -> None:
    rules_file = tmp_path / "fitness_functions.yaml"
    rules_file.write_text("fitness_functions: {not: [a list\n", encoding="utf-8")
    rules, _, errors = load_rules({"fitness_functions": "not-a-list"}, tmp_path)
    assert rules == []
    assert len(errors) == 2  # one per broken source, each named
    report = run_fitness({"fitness_functions": "not-a-list"}, tmp_path, DESCRIPTOR)
    assert report is not None and report.errors and report.results == []


# ---------------------------------------------------------------------------
# End to end through the scanner: notification is advisory, exit unchanged
# ---------------------------------------------------------------------------


TWO_RULES_YAML = """# Written by the project's agent -- these persist with the project.
fitness_functions:
  - name: no-god-state-and-modular
    description: keep state decomposed; no variable touched by most actions
    rule:
      all:
        - {fact: god_state_count, op: ==, value: 0}
        - {fact: modularity, op: '>=', value: 0.1}
  - name: state-space-in-check
    description: bound stays small and every count-like domain stays tiny
    rule:
      all:
        - {fact: bound, op: '<', value: 100}
        - {fact: variable_domain, var: count, op: '<=', value: 4}
"""


def test_scan_with_no_rules_attaches_no_fitness_section(tmp_path: Path) -> None:
    tla, cfg, _ = write_small_model(tmp_path)
    analysis = analyze(tla, cfg, None)
    assert analysis.fitness is None
    assert "Fitness functions" not in render_text(analysis)


def test_scan_surfaces_one_firing_of_two_composed_rules(tmp_path: Path) -> None:
    """The CD-03 worked-example shape: two composed rules, one fires later."""
    tla, cfg, _ = write_small_model(tmp_path)
    (tmp_path / "fitness_functions.yaml").write_text(TWO_RULES_YAML, encoding="utf-8")
    analysis = analyze(tla, cfg, None)
    assert analysis.fitness is not None
    by_name = {r.name: r for r in analysis.fitness.results}
    # `started` is touched by all 3 actions -> god state -> the rule fires.
    assert by_name["no-god-state-and-modular"].status == "fired"
    # bound = 2*2*3 = 12 < 100 and |domain(count)| = 3 <= 4 -> holds.
    assert by_name["state-space-in-check"].status == "holds"
    text = render_text(analysis)
    assert "FIRED: no-god-state-and-modular" in text
    assert "god_state_count=1 == 0 is FALSE" in text
    assert "holds: state-space-in-check" in text
    assert "NOTIFICATION" in text


def test_manifest_carried_rules_reach_the_scan(tmp_path: Path) -> None:
    manifest_text = (
        "module: Small\n"
        "fitness_functions:\n"
        "  - name: bound-small\n"
        "    rule: {fact: bound, op: '<', value: 5}\n"
    )
    tla, cfg, manifest = write_small_model(tmp_path, manifest_text)
    analysis = analyze(tla, cfg, manifest)
    assert analysis.fitness is not None
    assert [r.name for r in analysis.fitness.fired] == ["bound-small"]


def test_manifest_rules_without_pyyaml_surface_config_error_not_invalid(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """VAL-01: manifest-embedded rules under a bare python3 (no PyYAML).

    The fallback manifest parser mangles flow-style rule leaves into garbage
    keys, so validating them surfaced a misleading
    "INVALID: ... got keys ['{fact']". The documented behavior is an advisory
    CONFIG ERROR naming the missing PyYAML dependency and the
    fitness_functions.json (standard-library) alternative -- with the exit
    code unchanged.
    """
    manifest_text = (
        "module: Small\n"
        "fitness_functions:\n"
        "  - name: bound-small\n"
        "    rule: {fact: bound, op: '<=', value: 2000}\n"
    )
    tla, cfg, manifest = write_small_model(tmp_path, manifest_text)
    assert manifest is not None
    # Simulate PyYAML absence: None in sys.modules makes `import yaml` raise
    # ImportError, which routes the manifest through the fallback parser.
    monkeypatch.setitem(sys.modules, "yaml", None)

    assert main([str(tla), str(cfg), "--manifest", str(manifest)]) == EXIT_PASS
    out = capsys.readouterr().out
    assert "CONFIG ERROR" in out
    assert "PyYAML" in out
    assert "fitness_functions.json" in out
    assert "INVALID" not in out
    assert "'{fact'" not in out


def test_firings_are_advisory_exit_code_unchanged(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    tla, cfg, _ = write_small_model(tmp_path)
    (tmp_path / "fitness_functions.yaml").write_text(TWO_RULES_YAML, encoding="utf-8")
    assert main([str(tla), str(cfg)]) == EXIT_PASS
    out = capsys.readouterr().out
    assert "FIRED: no-god-state-and-modular" in out


def test_broken_rules_file_is_advisory_exit_code_unchanged(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    tla, cfg, _ = write_small_model(tmp_path)
    (tmp_path / "fitness_functions.yaml").write_text("{{{{not yaml", encoding="utf-8")
    assert main([str(tla), str(cfg)]) == EXIT_PASS
    assert "CONFIG ERROR" in capsys.readouterr().out


def test_json_payload_carries_the_fitness_report(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    tla, cfg, _ = write_small_model(tmp_path)
    (tmp_path / "fitness_functions.yaml").write_text(TWO_RULES_YAML, encoding="utf-8")
    assert main([str(tla), str(cfg), "--format", "json"]) == EXIT_PASS
    payload = json.loads(capsys.readouterr().out)
    fitness = payload["fitness"]
    assert fitness["blocks_promotion"] is False
    assert fitness["fired"] == ["no-god-state-and-modular"]
    statuses = {r["name"]: r["status"] for r in fitness["results"]}
    assert statuses == {
        "no-god-state-and-modular": "fired",
        "state-space-in-check": "holds",
    }


def test_json_payload_fitness_is_null_when_nothing_is_configured(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    tla, cfg, _ = write_small_model(tmp_path)
    assert main([str(tla), str(cfg), "--format", "json"]) == EXIT_PASS
    payload = json.loads(capsys.readouterr().out)
    assert payload["fitness"] is None
