"""`analyze complexity` measures the model and gates it against the budgets.

The load-bearing properties, in order of how much damage their absence has
already caused this repository:

1. The suggested move is a RECOMMENDATION and is never auto-applied.
2. Projected reductions are labeled projected, never presented as findings.
3. A generated-states drop at constant distinct states is reported as a RED
   FLAG, because the distinct-state gate is structurally blind to a deleted
   self-loop (MF-020).
4. The budget gate exits nonzero, and case generation refuses above it unless
   explicitly overridden.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.analyze_complexity import (  # noqa: E402
    EXIT_BUDGET_EXCEEDED,
    EXIT_PASS,
    analyze,
    compare_tlc_reports,
    gate_report,
    main,
    parse_cfg_constants,
    parse_tlc_report,
    suggest_move,
)

# A deliberately small, tractable model: two latching booleans in a chain and
# one bounded counter.
SMALL_TLA = """---------------------------- MODULE Small ----------------------------
EXTENDS Naturals

CONSTANTS Items

VARIABLES started, finished, count

vars == << started, finished, count >>

Init ==
  /\\ started = FALSE
  /\\ finished = FALSE
  /\\ count = 0

Start ==
  /\\ ~started
  /\\ started' = TRUE
  /\\ UNCHANGED << finished, count >>

Finish ==
  /\\ started
  /\\ ~finished
  /\\ finished' = TRUE
  /\\ UNCHANGED << started, count >>

Bump ==
  /\\ started
  /\\ count < 2
  /\\ count' = count + 1
  /\\ UNCHANGED << started, finished >>

Next == Start \\/ Finish \\/ Bump

TypeInvariant ==
  /\\ started \\in BOOLEAN
  /\\ finished \\in BOOLEAN
  /\\ count \\in 0..2

Spec == Init /\\ [][Next]_vars
=============================================================================
"""

SMALL_CFG = """SPECIFICATION Spec

CONSTANTS
  Items = {a, b}

INVARIANTS
  TypeInvariant
"""


def write_small_model(tmp_path: Path, budgets: str = "") -> tuple[Path, Path, Path | None]:
    tla = tmp_path / "Small.tla"
    cfg = tmp_path / "MC.cfg"
    tla.write_text(SMALL_TLA, encoding="utf-8")
    cfg.write_text(SMALL_CFG, encoding="utf-8")
    manifest: Path | None = None
    if budgets:
        manifest = tmp_path / "spec_manifest.yaml"
        manifest.write_text(budgets, encoding="utf-8")
    return tla, cfg, manifest


GENEROUS_BUDGETS = """module: Small
budgets:
  max_distinct_states: 50000
  max_state_space_bound: 1000000
  max_component_variables: 6
  max_component_actions: 8
"""

TIGHT_BUDGETS = """module: Small
budgets:
  max_distinct_states: 4
  max_state_space_bound: 4
  max_component_variables: 2
  max_component_actions: 1
"""


# ---------------------------------------------------------------------------
# Dimension table and state-space bound
# ---------------------------------------------------------------------------


def test_dimension_table_and_bound_are_the_product_of_domains(tmp_path: Path) -> None:
    tla, cfg, _ = write_small_model(tmp_path)
    result = analyze(tla, cfg, None)
    cardinalities = {d.variable: d.cardinality for d in result.dimensions}
    assert cardinalities == {"started": 2, "finished": 2, "count": 3}
    assert result.bound == 2 * 2 * 3


def test_variables_unconstrained_by_type_invariant_are_excluded_not_guessed(
    tmp_path: Path,
) -> None:
    """An unknown domain must stay unknown; inventing one fakes the metric."""
    tla = tmp_path / "Small.tla"
    tla.write_text(SMALL_TLA.replace("  /\\ count \\in 0..2\n", ""), encoding="utf-8")
    cfg = tmp_path / "MC.cfg"
    cfg.write_text(SMALL_CFG, encoding="utf-8")
    result = analyze(tla, cfg, None)
    assert "count" in result.unbounded
    assert result.bound == 4
    note = next(d.note for d in result.dimensions if d.variable == "count")
    assert "unconstrained" in note


def test_repository_own_model_reproduces_the_recorded_state_space_bound() -> None:
    r"""Calibration against the figures this epic has actually recorded.

    MF-020 recorded 393,216 for the 11-variable shape:
    2*2*3*2*2*2 * 2^3 * 4^3 * 2^3 = 393,216.

    MF-011 then added `complexity_gate` (3 values), making the bound exactly
    3x that: 1,179,648.

    MF-022 then collapsed the five setup booleans into `setup_phase \in 0..5`,
    replacing a 2^5 = 32 factor with a factor of 6:
    1,179,648 / 32 * 6 = 221,184. Asserting the current figure AND its
    relationship to each recorded predecessor keeps the calibration meaningful
    across every promotion.
    """
    tla = REPO_ROOT / "specs" / "current" / "TlaSpecDevCli.tla"
    cfg = REPO_ROOT / "specs" / "current" / "MC.cfg"
    if not tla.is_file():
        return
    result = analyze(tla, cfg, None)
    assert result.bound == 221_184
    # Undo the MF-022 collapse to recover the MF-011 figure...
    assert result.bound // 6 * 32 == 1_179_648
    # ...and divide out the 3-valued gate to recover the MF-020 figure.
    assert (result.bound // 6 * 32) // 3 == 393_216
    assert set(result.unbounded) == {"lastCommand", "result"}


def test_cfg_constant_sets_drive_cardinality() -> None:
    constants = parse_cfg_constants(SMALL_CFG)
    assert constants["Items"] == ["a", "b"]


# ---------------------------------------------------------------------------
# Read/write matrix and modularity
# ---------------------------------------------------------------------------


def test_read_write_matrix_separates_reads_writes_and_unchanged(tmp_path: Path) -> None:
    tla, cfg, _ = write_small_model(tmp_path)
    result = analyze(tla, cfg, None)
    by_name = {a.name: a for a in result.actions}
    assert set(by_name) == {"Start", "Finish", "Bump"}
    # Bump reads started and count, writes count, and leaves finished alone.
    assert by_name["Bump"].writes == {"count"}
    assert by_name["Bump"].reads == {"started", "count"}
    assert "finished" not in by_name["Bump"].touched


def test_modularity_is_deterministic_for_the_same_model(tmp_path: Path) -> None:
    tla, cfg, _ = write_small_model(tmp_path)
    first = analyze(tla, cfg, None)
    second = analyze(tla, cfg, None)
    assert first.modularity_score == second.modularity_score
    assert [sorted(c) for c in first.communities] == [sorted(c) for c in second.communities]


# ---------------------------------------------------------------------------
# Abstraction candidates -- the ordinal collapse
# ---------------------------------------------------------------------------


def test_latching_booleans_in_a_guard_chain_are_surfaced_as_an_ordinal_collapse(
    tmp_path: Path,
) -> None:
    """`Finish` requires `started`, so the two booleans admit 3 of 4 combinations."""
    tla, cfg, _ = write_small_model(tmp_path)
    result = analyze(tla, cfg, None)
    assert len(result.chains) == 1
    assert set(result.chains[0].members) == {"started", "finished"}
    assert result.chains[0].combinations_declared == 4
    assert result.chains[0].combinations_reachable == 3


def test_repository_own_model_has_landed_the_setup_phase_collapse() -> None:
    """MF-022 applied the reduction MF-011's analyzer found on its own.

    MF-011's analyzer derived, from the model alone, that the five setup
    booleans were pinned into a total order by their own action guards so that
    32 declared combinations admitted only 6, and projected the collapse would
    take the declared bound 1,179,648 -> 221,184. MF-022 applied it. This test
    now guards the landed state: the ordinal is present, no five-member
    latching chain remains, and the bound is exactly the projected figure --
    which is also the check that the analyzer's projection was honest.
    """
    tla = REPO_ROOT / "specs" / "current" / "TlaSpecDevCli.tla"
    cfg = REPO_ROOT / "specs" / "current" / "MC.cfg"
    if not tla.is_file():
        return
    result = analyze(tla, cfg, None)
    assert "setup_phase" in result.variables
    for removed in (
        "cli_built",
        "cli_installed",
        "project_scaffolded",
        "budgets_recorded",
        "workflow_scaffolded",
    ):
        assert removed not in result.variables
    # The collapse consumed the chain it was derived from.
    assert not [c for c in result.chains if len(c.members) == 5]
    # Exactly the figure MF-011 projected before the move was applied.
    assert result.bound == 221_184


# ---------------------------------------------------------------------------
# Suggested move -- recommendation, never verdict
# ---------------------------------------------------------------------------


def test_suggested_move_is_labeled_a_recommendation_requiring_approval(
    tmp_path: Path,
) -> None:
    tla, cfg, _ = write_small_model(tmp_path)
    suggestion = suggest_move(analyze(tla, cfg, None))
    assert suggestion["move"] in {"ABSTRACT", "DECOMPOSE", "REFACTOR"}
    assert "RECOMMENDATION" in suggestion["status"]
    assert "USER APPROVAL" in suggestion["status"]
    assert "NOT AUTO-APPLIED" in suggestion["status"]


def test_suggested_move_separates_measured_evidence_from_projected_gain(
    tmp_path: Path,
) -> None:
    """MF-020: a projected figure presented as a finding propagated a bad number."""
    tla, cfg, _ = write_small_model(tmp_path)
    suggestion = suggest_move(analyze(tla, cfg, None))
    assert "evidence_measured" in suggestion
    assert "gain_projected" in suggestion
    assert suggestion["evidence_measured"]


def test_text_output_carries_the_measured_projected_legend_and_the_self_loop_warning(
    tmp_path: Path, capsys
) -> None:
    tla, cfg, _ = write_small_model(tmp_path, GENEROUS_BUDGETS)
    main([str(tla), str(cfg), "--manifest", str(tmp_path / "spec_manifest.yaml")])
    out = capsys.readouterr().out
    assert "[MEASURED]" in out
    assert "[PROJECTED]" in out
    assert "RED FLAG" in out
    assert "not a verdict" in out


# ---------------------------------------------------------------------------
# Justification linkage / dead weight
# ---------------------------------------------------------------------------


def test_dead_weight_flagged_only_when_a_justification_table_is_present(
    tmp_path: Path,
) -> None:
    tla, cfg, _ = write_small_model(tmp_path)
    assert analyze(tla, cfg, None).unjustified is None

    manifest = tmp_path / "spec_manifest.yaml"
    manifest.write_text(
        "module: Small\n"
        "justification:\n"
        "  started:\n"
        "    invariants: [TypeInvariant]\n"
        "    effects: []\n"
        "    kill_tests: []\n"
        "  finished:\n"
        "    invariants: []\n"
        "    effects: []\n"
        "    kill_tests: []\n",
        encoding="utf-8",
    )
    result = analyze(tla, cfg, manifest)
    # `finished` has an empty linkage, `count` is absent entirely.
    assert result.unjustified == ["finished", "count"]


def test_a_fully_linked_table_flags_nothing(tmp_path: Path) -> None:
    tla, cfg, _ = write_small_model(tmp_path)
    manifest = tmp_path / "spec_manifest.yaml"
    manifest.write_text(
        "module: Small\n"
        "justification:\n"
        "  started:\n    invariants: [TypeInvariant]\n"
        "  finished:\n    effects: [DoneSignal]\n"
        "  count:\n    kill_tests: [drop_bump]\n",
        encoding="utf-8",
    )
    assert analyze(tla, cfg, manifest).unjustified == []


# ---------------------------------------------------------------------------
# Budget gate
# ---------------------------------------------------------------------------


def test_gate_passes_within_budget(tmp_path: Path) -> None:
    tla, cfg, manifest = write_small_model(tmp_path, GENEROUS_BUDGETS)
    result = analyze(tla, cfg, manifest)
    assert result.gate_passed
    assert result.violations == []
    assert main([str(tla), str(cfg), "--manifest", str(manifest)]) == EXIT_PASS


def test_gate_fails_and_exits_nonzero_over_budget(tmp_path: Path) -> None:
    tla, cfg, manifest = write_small_model(tmp_path, TIGHT_BUDGETS)
    result = analyze(tla, cfg, manifest)
    assert not result.gate_passed
    joined = " ".join(result.violations)
    # MF-022: the STATIC bound is gated against max_state_space_bound, not
    # against max_distinct_states, which caps actual reachable states.
    assert "max_state_space_bound" in joined
    assert main([str(tla), str(cfg), "--manifest", str(manifest)]) == EXIT_BUDGET_EXCEEDED


def test_component_size_budgets_are_enforced_independently(tmp_path: Path) -> None:
    tla, cfg, manifest = write_small_model(tmp_path, TIGHT_BUDGETS)
    violations = " ".join(analyze(tla, cfg, manifest).violations)
    assert "max_component_variables" in violations or "max_component_actions" in violations


def test_gate_report_names_the_dominant_dimensions_on_failure(tmp_path: Path) -> None:
    tla, cfg, manifest = write_small_model(tmp_path, TIGHT_BUDGETS)
    passed, message = gate_report(tla, cfg, manifest)
    assert passed is False
    assert "Dominant dimensions" in message
    assert "count" in message


def test_evidence_can_be_written_into_a_results_directory(tmp_path: Path) -> None:
    tla, cfg, manifest = write_small_model(tmp_path, GENEROUS_BUDGETS)
    out = tmp_path / "results" / "complexity.txt"
    main([str(tla), str(cfg), "--manifest", str(manifest), "--out", str(out)])
    assert out.is_file()
    assert "Dimension table" in out.read_text(encoding="utf-8")


def test_json_output_marks_projections_unverified(tmp_path: Path, capsys) -> None:
    import json

    tla, cfg, manifest = write_small_model(tmp_path, GENEROUS_BUDGETS)
    main([str(tla), str(cfg), "--manifest", str(manifest), "--format", "json"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["projected"]["verified"] is False
    assert "RED FLAG" in payload["projected"]["caveat"]
    assert payload["suggested_move"]["status"].startswith("RECOMMENDATION")


# ---------------------------------------------------------------------------
# The self-loop blindness check (MF-020 finding 1)
# ---------------------------------------------------------------------------


def test_tlc_report_parsing() -> None:
    report = parse_tlc_report(
        "3664 states generated, 919 distinct states found, 0 states left on queue.\n"
        "The depth of the complete state graph search is 21.\n"
    )
    assert (report.generated, report.distinct, report.depth) == (3664, 919, 21)


def test_generated_drop_at_constant_distinct_states_is_a_red_flag() -> None:
    """The exact MF-020 signature: -13.1% generated at identical 919/21."""
    baseline = parse_tlc_report(
        "3664 states generated, 919 distinct states found.\n"
        "The depth of the complete state graph search is 21.\n"
    )
    current = parse_tlc_report(
        "3185 states generated, 919 distinct states found.\n"
        "The depth of the complete state graph search is 21.\n"
    )
    findings = compare_tlc_reports(baseline, current)
    assert findings[0]["level"] == "RED FLAG"
    assert "self-loop" in findings[0]["message"]
    assert "transition" in findings[0]["message"]


def test_a_drop_accompanied_by_fewer_distinct_states_is_not_a_red_flag() -> None:
    baseline = parse_tlc_report(
        "3664 states generated, 919 distinct states found.\n"
        "The depth of the complete state graph search is 21.\n"
    )
    current = parse_tlc_report(
        "2000 states generated, 700 distinct states found.\n"
        "The depth of the complete state graph search is 19.\n"
    )
    findings = compare_tlc_reports(baseline, current)
    assert findings[0]["level"] == "INFO"


def test_unchanged_run_reports_no_self_loop_signature() -> None:
    report = parse_tlc_report(
        "3664 states generated, 919 distinct states found.\n"
        "The depth of the complete state graph search is 21.\n"
    )
    findings = compare_tlc_reports(report, report)
    assert findings[0]["level"] == "OK"


# ---------------------------------------------------------------------------
# Case generation refusal
# ---------------------------------------------------------------------------


def run_generation(tmp_path: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    tla, cfg, _ = write_small_model(tmp_path, TIGHT_BUDGETS)
    return subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "generate_cases_from_tlc_dump.py"),
            str(tla),
            str(cfg),
            "--out",
            str(tmp_path / "generated"),
            *extra,
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_case_generation_refuses_above_the_gate_without_running_tlc(tmp_path: Path) -> None:
    result = run_generation(tmp_path)
    assert result.returncode != 0
    assert "complexity gate FAIL" in result.stderr
    assert "REFUSING to generate cases" in result.stderr
    assert "Dominant dimensions" in result.stderr
    # The refusal must happen instead of a TLC run, not after one.
    assert "states generated" not in result.stdout


def test_case_generation_proceeds_with_the_explicit_override(tmp_path: Path) -> None:
    result = run_generation(tmp_path, "--allow-over-budget")
    # TLC may be unavailable in some environments; the gate decision is the
    # property under test, not TLC itself.
    assert "PROCEEDING ANYWAY -- overridden by --allow-over-budget" in result.stderr
    assert "REFUSING to generate cases" not in result.stderr


# ---------------------------------------------------------------------------
# CLI surface
# ---------------------------------------------------------------------------


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "tla_spec_dev.py"), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_analyze_complexity_is_reachable_through_the_cli(tmp_path: Path) -> None:
    tla, cfg, manifest = write_small_model(tmp_path, GENEROUS_BUDGETS)
    result = run_cli("analyze", "complexity", str(tla), str(cfg), "--manifest", str(manifest))
    assert result.returncode == EXIT_PASS, result.stderr
    assert "Dimension table" in result.stdout
    assert "SUGGESTED MOVE" in result.stdout


def test_analyze_parent_command_reports_the_next_step() -> None:
    result = run_cli("analyze")
    assert result.returncode == 2
    assert "analyze complexity" in result.stderr


def test_cfg_defaults_to_mc_cfg_beside_the_module(tmp_path: Path) -> None:
    tla, _, manifest = write_small_model(tmp_path, GENEROUS_BUDGETS)
    result = run_cli("analyze", "complexity", str(tla), "--manifest", str(manifest))
    assert result.returncode == EXIT_PASS, result.stderr
