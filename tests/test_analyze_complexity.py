"""`analyze complexity` measures the model and ADVISES against the thresholds.

The load-bearing properties, in order of how much damage their absence has
already caused this repository:

1. The suggested move is a RECOMMENDATION and is never auto-applied.
2. Projected reductions are labeled projected, never presented as findings.
3. A generated-states drop at constant distinct states is reported as a RED
   FLAG, because the distinct-state gate is structurally blind to a deleted
   self-loop (MF-020).
4. MF-036: complexity is advisory, not a gate. A model over a threshold gets a
   WARNING that names the component/variable/action and RECOMMENDS a concrete
   move -- it exits 0 and case generation still proceeds. The command exits
   nonzero ONLY when it cannot analyze the model at all (an unresolved
   hierarchy); "I could not measure this" is an error, "this is complex" is a
   finding.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest  # noqa: E402

from scripts.analyze_complexity import (  # noqa: E402
    EXIT_BUDGET_EXCEEDED,
    EXIT_PASS,
    UnresolvedExtendsError,
    UnsupportedModuleConstructError,
    analyze,
    compare_tlc_reports,
    gate_report,
    main,
    extract_actions,
    interaction_graph,
    parse_cfg_constants,
    parse_definitions,
    parse_tlc_report,
    resolve_module,
    strip_frame_conditions,
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
    1,179,648 / 32 * 6 = 221,184.

    MF-014 then added `corpus_gate` (3 values) as the case-cap hard gate,
    tripling it again: 221,184 * 3 = 663,552. That growth is deliberate --
    an unrepresented gate is not a gate -- and stays inside
    `max_state_space_bound` 1,000,000.

    MF-025 then collapsed the per-ticket lifecycle -- active_tickets,
    closed_tickets and ticket_phase -- into `ticket_state \\in [Tickets -> 0..5]`,
    replacing an 8 * 8 * 64 = 4,096 factor with 6^3 = 216:
    663,552 / 4096 * 216 = 34,992, a factor of 18.96. Reachable states and
    depth were measured unchanged at 9,011 and 24 across that change, so the
    drop is representation, not deleted behavior.

    MF-013 then added `effect_conformance` as the effect-conformance hard
    gate. It was 4-valued, unlike its 3-valued predecessors -- "clean", "gaps"
    and "dead_surface" are distinct findings with distinct remedies and
    distinct CLI next-steps -- so it multiplied the bound by 4:
    34,992 * 4 = 139,968. Same reasoning as MF-014: an unrepresented gate is
    not a gate. Depth was measured unchanged at 24 across the change.

    MF-027 then made that same variable 5-valued by adding "unobservable":
    the effect sandbox observes the in-process CPython runtime only, and a
    target it cannot see must FAIL rather than report clean. That verdict
    selects a distinct `result.next` and a distinct CLI exit path, so leaving
    it unrepresented would make the model blind to a real outcome of a modeled
    command -- which is precisely what the verdict itself exists to report.
    The factor goes 4 -> 5: 34,992 * 5 = 174,960, still well inside
    `max_state_space_bound` 1,000,000. Depth measured unchanged at 24 again,
    and no variable or action was added (still 8 variables), so the whole
    delta is this one domain.

    MF-016 then added `kill_test` as the mutation kill-test gate -- oracle 4,
    the value floor that keeps every cost cap above it honest. It is 4-valued:
    "unknown", "pass", "below_floor", and "incomplete_catalog". The last two
    are kept apart for the same reason MF-013 kept "gaps" apart from
    "dead_surface" -- different findings with different remedies (refine the
    model at the surviving mutant's variable vs. seed a fault for an uncovered
    boundary) and distinct `result.next` strings. All three non-"unknown"
    values were confirmed individually reachable by TLC before the domain was
    fixed at four, so the domain represents the reachable set exactly.
    The factor is 4: 174,960 * 4 = 699,840, still inside
    `max_state_space_bound` 1,000,000. Measured alongside: 8 -> 9 variables,
    depth 24 -> 25, and TLC 1,067,828 -> 5,619,356 generated / 49,875 ->
    231,621 distinct (46.3% of the negotiated max_distinct_states 500,000).

    Asserting the current figure AND its relationship to each recorded
    predecessor keeps the calibration meaningful across every promotion.
    """
    tla = REPO_ROOT / "specs" / "current" / "TlaSpecDevCli.tla"
    cfg = REPO_ROOT / "specs" / "current" / "MC.cfg"
    if not tla.is_file():
        return
    result = analyze(tla, cfg, None)
    assert result.bound == 699_840
    # Divide out the MF-016 4-valued kill-test gate...
    pre_mf016 = result.bound // 4
    assert pre_mf016 == 174_960
    # ...then the MF-027 5-valued effect gate to recover the MF-025 figure...
    pre_mf013 = pre_mf016 // 5
    assert pre_mf013 == 34_992
    # ...undo the MF-025 lifecycle collapse to recover the MF-014 figure...
    pre_mf025 = pre_mf013 // 216 * 4096
    assert pre_mf025 == 663_552
    # ...divide out the MF-014 case-cap gate to recover the MF-022 figure...
    assert pre_mf025 // 3 == 221_184
    # ...undo the MF-022 collapse to recover the MF-011 figure...
    assert pre_mf025 // 3 // 6 * 32 == 1_179_648
    # ...and divide out the 3-valued complexity gate for the MF-020 figure.
    assert (pre_mf025 // 3 // 6 * 32) // 3 == 393_216
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


# ---------------------------------------------------------------------------
# Frame-condition fix (MF-036): `v' = v` is UNCHANGED, not a touch
# ---------------------------------------------------------------------------


def test_strip_frame_conditions_removes_exact_v_prime_equals_v() -> None:
    body = "status' = status + 1 /\\ v1' = v1 /\\ v2' = v2"
    stripped = strip_frame_conditions(body, ["status", "v1", "v2"])
    # The genuine write-that-reads survives; the two frame conditions are gone.
    assert "status' = status + 1" in stripped
    assert "v1' = v1" not in stripped
    assert "v2' = v2" not in stripped


def test_strip_frame_conditions_keeps_genuine_writes_that_read() -> None:
    # `v' = v + 1` and `v' = v \cup {x}` genuinely read the old value: never strip.
    body = "a' = a + 1 /\\ b' = b \\cup {x}"
    stripped = strip_frame_conditions(body, ["a", "b"])
    assert "a' = a + 1" in stripped
    assert "b' = b \\cup {x}" in stripped


def test_frame_condition_variable_is_not_counted_as_touched() -> None:
    """A variable left UNCHANGED by `v' = v` is NOT touched by that action."""
    module = (
        "---- MODULE Frame ----\n"
        "VARIABLES status, v1, v2\n"
        "Act == status' = status + 1 /\\ v1' = v1 /\\ v2' = v2\n"
        "====\n"
    )
    defs = parse_definitions(module)
    actions = extract_actions(defs, ["status", "v1", "v2"])
    act = {a.name: a for a in actions}["Act"]
    # Only `status` is genuinely written/read; the two frame conditions vanish.
    assert act.writes == {"status"}
    assert "v1" not in act.touched
    assert "v2" not in act.touched


def test_god_object_frame_conditions_drop_from_10_of_10_to_real_coupling() -> None:
    """The probe: five vars, ten commands, each touching only two.

    Every command frames the three variables it does not use with `v' = v`.
    Counting those as touches (the bug) reports all five variables coupled to all
    ten commands -- a fully dense 10/10 god-state. The fix reveals the real
    coupling: only the shared `status` is touched by all ten; the four domain
    variables drop to their true 2-or-3-of-10.
    """
    variables = ["status", "v1", "v2", "v3", "v4"]
    lines = []
    domain_for = ["v1", "v1", "v1", "v2", "v2", "v2", "v3", "v3", "v4", "v4"]
    for i, dom in enumerate(domain_for, start=1):
        others = [v for v in ("v1", "v2", "v3", "v4") if v != dom]
        frame = " /\\ ".join(f"{o}' = {o}" for o in others)
        lines.append(
            f"Cmd{i:02d} == status' = (status + 1) % 3 /\\ {dom}' = ({dom} + 1) % 3 /\\ {frame}"
        )
    module = "---- MODULE God ----\nVARIABLES status, v1, v2, v3, v4\n" + "\n".join(lines) + "\n====\n"
    defs = parse_definitions(module)

    # With the fix applied (the shipped behavior): real coupling.
    fixed = extract_actions(defs, variables)
    touched_counts = {v: sum(1 for a in fixed if v in a.touched) for v in variables}
    assert touched_counts["status"] == 10
    assert touched_counts["v1"] == 3
    assert touched_counts["v2"] == 3
    assert touched_counts["v3"] == 2
    assert touched_counts["v4"] == 2

    # Contrast with the pre-fix behavior (frame conditions counted as touches):
    # every variable reported touched by all ten commands.
    def unfixed_actions():
        from scripts.analyze_complexity import (
            Action,
            primed_references,
            references,
            strip_unchanged,
        )

        out = []
        for d in defs:
            b = strip_unchanged(d.body)
            w = {v for v in variables if primed_references(b, v)}
            if not w:
                continue
            r = {v for v in variables if references(b, v)}
            out.append(Action(name=d.name, reads=r, writes=w, body=b))
        return out

    before = unfixed_actions()
    before_counts = {v: sum(1 for a in before if v in a.touched) for v in variables}
    assert before_counts == {"status": 10, "v1": 10, "v2": 10, "v3": 10, "v4": 10}

    # The fix de-densifies the R/W interaction graph: the frame-condition bug
    # coupled every pair of variables (a complete graph, C(5,2)=10 edges); the
    # real coupling is a star around `status` (4 edges).
    edges_before = interaction_graph(before, variables)
    edges_after = interaction_graph(fixed, variables)
    assert len(edges_before) == 10
    assert len(edges_after) == 4


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
    latching chain remains, and the bound still factors through the projected
    figure -- which is also the check that the analyzer's projection was honest.

    MF-014 later multiplied the bound by 3 by adding `corpus_gate`, so the
    projected 221,184 is asserted as a FACTOR rather than as the total. Gates
    added after the collapse do not invalidate it; a change to the setup-phase
    factor itself would still break this test.
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
    # MF-025: the per-ticket lifecycle is one ordinal now.
    assert "ticket_state" in result.variables
    for removed in ("active_tickets", "closed_tickets", "ticket_phase"):
        assert removed not in result.variables
    # The collapse consumed the chain it was derived from.
    assert not [c for c in result.chains if len(c.members) == 5]
    # MF-013 later multiplied the bound by 4 (effect_conformance), MF-027 took
    # that factor to 5 by adding the "unobservable" verdict, MF-016 multiplied
    # by a further 4 (kill_test), and MF-025 divided the bound by 4096/216 (the
    # per-ticket lifecycle collapse), so undo all of them
    # before checking the setup-phase factor. A change to the setup-phase
    # factor itself would still break this.
    pre_mf025 = result.bound // 4 // 5 // 216 * 4096
    # The figure MF-011 projected, still present as a factor of the bound
    # after MF-014's corpus_gate tripled it.
    assert pre_mf025 % 221_184 == 0
    assert pre_mf025 // 221_184 == 3  # corpus_gate, the only later addition


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
# Complexity thresholds -- advisory, not blocking (MF-036)
# ---------------------------------------------------------------------------


def test_clean_within_budget(tmp_path: Path) -> None:
    tla, cfg, manifest = write_small_model(tmp_path, GENEROUS_BUDGETS)
    result = analyze(tla, cfg, manifest)
    assert result.gate_passed
    assert result.warnings == []
    assert result.violations == []
    assert main([str(tla), str(cfg), "--manifest", str(manifest)]) == EXIT_PASS


def test_over_threshold_warns_but_still_exits_zero(tmp_path: Path) -> None:
    """MF-036: over threshold is a WARNING, never a promotion block.

    The scan raises warnings, but `analyze complexity` still exits 0 -- a
    complex model is a finding, not a failure.
    """
    tla, cfg, manifest = write_small_model(tmp_path, TIGHT_BUDGETS)
    result = analyze(tla, cfg, manifest)
    assert not result.gate_passed
    assert result.warnings, "an over-threshold model must raise advisory warnings"
    joined = " ".join(result.violations)
    # MF-022: the STATIC bound is compared against max_state_space_bound, not
    # against max_distinct_states, which caps actual reachable states.
    assert "max_state_space_bound" in joined
    # The exit code is EXIT_PASS despite the warnings -- complexity never blocks.
    assert main([str(tla), str(cfg), "--manifest", str(manifest)]) == EXIT_PASS


def test_every_warning_names_a_target_and_recommends_a_move(tmp_path: Path) -> None:
    """A warning must name the component/variable/action AND recommend a move."""
    tla, cfg, manifest = write_small_model(tmp_path, TIGHT_BUDGETS)
    result = analyze(tla, cfg, manifest)
    assert result.warnings
    for warning in result.warnings:
        assert warning.finding.strip()
        assert warning.recommendation.strip()
        # A concrete move, not just a threshold restatement.
        assert "consider" in warning.recommendation.lower()


def test_component_size_thresholds_are_reported_independently(tmp_path: Path) -> None:
    tla, cfg, manifest = write_small_model(tmp_path, TIGHT_BUDGETS)
    findings = " ".join(analyze(tla, cfg, manifest).violations)
    assert "max_component_variables" in findings or "max_component_actions" in findings


def test_gate_report_names_the_dominant_dimensions_and_recommends(tmp_path: Path) -> None:
    tla, cfg, manifest = write_small_model(tmp_path, TIGHT_BUDGETS)
    clean, message = gate_report(tla, cfg, manifest)
    assert clean is False
    assert "ADVISORY WARNINGS" in message
    assert "recommendation:" in message
    assert "Dominant dimensions" in message
    # It must NOT tell the caller to refuse -- generation always proceeds now.
    assert "REFUSING" not in message


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


def test_case_generation_advises_above_the_threshold_but_does_not_refuse(tmp_path: Path) -> None:
    """MF-036: over threshold, generation PRINTS the warnings and proceeds.

    It never refuses -- complexity is advisory. TLC may be unavailable in this
    environment, so the property under test is the advisory decision (no
    refusal, no nonzero-for-complexity), not whether TLC then runs.
    """
    result = run_generation(tmp_path)
    assert "ADVISORY WARNINGS" in result.stderr
    assert "recommendation:" in result.stderr
    assert "Proceeding with case generation" in result.stderr
    # The old refusal and its override flag are gone entirely.
    assert "REFUSING to generate cases" not in result.stderr
    assert "allow-over-budget" not in result.stderr


def test_case_generation_has_no_over_budget_override_flag(tmp_path: Path) -> None:
    """The override existed only to bypass the gate; there is no gate to bypass."""
    result = run_generation(tmp_path, "--allow-over-budget")
    # argparse rejects the removed flag: this is a usage error, not a bypass.
    assert result.returncode != 0
    assert "unrecognized arguments" in result.stderr or "allow-over-budget" in result.stderr


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


# ---------------------------------------------------------------------------
# EXTENDS resolution (MF-030)
# ---------------------------------------------------------------------------
#
# The analyzer used to read one .tla file and stop at EXTENDS, so a decomposed
# model was scored on only the declarations literally present in that file.
# Because missing variables only ever shrink the product bound, the error was
# never conservative: the gate failed toward PASS. These tests measure a
# decomposed model where the EXTENDED module contributes a BOUNDED variable, so
# the fix is proved by the bound MOVING -- not merely by the model parsing.

# A base module that carries the bound. `tick` is constrained by TypeInvariant
# (cardinality 4); the extending module inherits both `tick` and TypeInvariant
# through EXTENDS. This mirrors MF-023's Internal/External split, where the
# extending view adds an unconstrained channel variable and inherits the whole
# of the bounded constraint from the module it extends.
BASE_COUNTER_TLA = """---------------------------- MODULE Counter ----------------------------
EXTENDS Naturals

VARIABLES tick

CounterInit == tick = 0

Bump ==
  /\\ tick < 3
  /\\ tick' = tick + 1

TypeInvariant == tick \\in 0..3
=============================================================================
"""

# The extending view. `emitted` is an unconstrained channel variable, exactly
# like MF-023's `lastCommand`/`result`: it adds ZERO to the bound, so the bound
# a correct resolver reports comes ENTIRELY from the extended module.
CHANNEL_TLA = """---------------------------- MODULE Channel ----------------------------
EXTENDS Counter

VARIABLES emitted

ChannelInit ==
  /\\ CounterInit
  /\\ emitted = "none"

Emit ==
  /\\ Bump
  /\\ emitted' = "bumped"

Next == Emit

TypeInvariantWholeModel ==
  /\\ TypeInvariant
  /\\ emitted \\in {"none", "bumped"}

Spec == ChannelInit /\\ [][Next]_<< tick, emitted >>
=============================================================================
"""

CHANNEL_CFG = """SPECIFICATION Spec

INVARIANTS
  TypeInvariant
"""


def write_decomposed_model(tmp_path: Path) -> tuple[Path, Path]:
    (tmp_path / "Counter.tla").write_text(BASE_COUNTER_TLA, encoding="utf-8")
    channel = tmp_path / "Channel.tla"
    channel.write_text(CHANNEL_TLA, encoding="utf-8")
    cfg = tmp_path / "MC.cfg"
    cfg.write_text(CHANNEL_CFG, encoding="utf-8")
    return channel, cfg


def test_extends_is_followed_and_the_bound_reflects_all_variables(tmp_path: Path) -> None:
    r"""The MF-030 regression. Measures the EXTENDING module, `Channel`.

    PRE-FIX behavior (analyzer reads Channel.tla only):
      * variables == ['emitted']              -- the 1 declared in this file
      * TypeInvariant is absent (it lives in  -- so nothing is bounded
        the extended Counter)
      * bound == 1                            -- product of 0 bounded dimensions
      * `Bump` is not an action               -- it is defined in Counter

    POST-FIX behavior (EXTENDS Counter followed):
      * variables == ['tick', 'emitted']      -- unioned across the hierarchy
      * TypeInvariant inherited from Counter  -- bounds `tick` at cardinality 4
      * bound == 4                            -- entirely from the extended module
      * `Bump` is an action                   -- its declaration is included

    Every assertion below is one PRE-FIX would fail: the bound moves 1 -> 4, the
    extended variable and the extended action appear. That is what makes this a
    regression rather than a test that passes both before and after.
    """
    channel, cfg = write_decomposed_model(tmp_path)
    result = analyze(channel, cfg, None)

    # All variables from the whole hierarchy, not just this file's.
    assert set(result.variables) == {"tick", "emitted"}

    # The bound reflects the extended module's bounded variable. Pre-fix this
    # was 1 (the extending file carries no TypeInvariant of its own).
    assert result.bound == 4
    cardinalities = {d.variable: d.cardinality for d in result.dimensions}
    assert cardinalities["tick"] == 4
    # The channel variable stays honestly unbounded and adds nothing -- so the
    # whole of the bound provably came from across the EXTENDS edge.
    assert "emitted" in result.unbounded

    # The extended module's action is included in the dimension-bearing content.
    assert "Bump" in {a.name for a in result.actions}


def test_resolve_module_unions_a_three_level_hierarchy(tmp_path: Path) -> None:
    """Core <- Internal <- External, the shape SKILL.md mandates."""
    (tmp_path / "Root.tla").write_text(
        "---- MODULE Root ----\nEXTENDS Naturals\nVARIABLES a\n"
        "TypeInvariant == a \\in 0..1\n====\n",
        encoding="utf-8",
    )
    (tmp_path / "Mid.tla").write_text(
        "---- MODULE Mid ----\nEXTENDS Root\nVARIABLES b\n"
        "MidInv == b \\in 0..1\n====\n",
        encoding="utf-8",
    )
    (tmp_path / "Leaf.tla").write_text(
        "---- MODULE Leaf ----\nEXTENDS Mid\nVARIABLES c\n"
        "LeafInv == c \\in 0..1\n====\n",
        encoding="utf-8",
    )
    resolved = resolve_module(tmp_path / "Leaf.tla")
    assert resolved.root == "Leaf"
    assert resolved.modules == ["Root", "Mid", "Leaf"]
    assert set(resolved.variables) == {"a", "b", "c"}
    # TypeInvariant, defined only in Root, is reachable from the leaf's view.
    assert "TypeInvariant" in {d.name for d in resolved.defs}


def test_extends_of_standard_library_modules_needs_no_file(tmp_path: Path) -> None:
    """EXTENDS Naturals/FiniteSets/TLC must not demand a Naturals.tla."""
    tla = tmp_path / "Solo.tla"
    tla.write_text(
        "---- MODULE Solo ----\nEXTENDS Naturals, FiniteSets, TLC\n"
        "VARIABLES n\nTypeInvariant == n \\in 0..2\n====\n",
        encoding="utf-8",
    )
    resolved = resolve_module(tla)
    assert resolved.variables == ["n"]
    assert resolved.modules == ["Solo"]


# --- Fail-closed on constructs the resolver cannot model --------------------


def test_instance_fails_closed_rather_than_under_reporting(tmp_path: Path) -> None:
    (tmp_path / "Base.tla").write_text(
        "---- MODULE Base ----\nEXTENDS Naturals\nVARIABLES x\n"
        "TypeInvariant == x \\in 0..3\n====\n",
        encoding="utf-8",
    )
    tla = tmp_path / "UsesInstance.tla"
    tla.write_text(
        "---- MODULE UsesInstance ----\nEXTENDS Naturals\nVARIABLES y\n"
        "B == INSTANCE Base\nTypeInvariant == y \\in 0..3\n====\n",
        encoding="utf-8",
    )
    with pytest.raises(UnsupportedModuleConstructError, match="INSTANCE"):
        resolve_module(tla)


def test_local_fails_closed_rather_than_under_reporting(tmp_path: Path) -> None:
    tla = tmp_path / "UsesLocal.tla"
    tla.write_text(
        "---- MODULE UsesLocal ----\nEXTENDS Naturals\nVARIABLES w\n"
        "LOCAL Helper == 1\nTypeInvariant == w \\in 0..3\n====\n",
        encoding="utf-8",
    )
    with pytest.raises(UnsupportedModuleConstructError, match="LOCAL"):
        resolve_module(tla)


def test_missing_extended_module_fails_closed(tmp_path: Path) -> None:
    tla = tmp_path / "Orphan.tla"
    tla.write_text(
        "---- MODULE Orphan ----\nEXTENDS Naturals, Missing\nVARIABLES z\n"
        "TypeInvariant == z \\in 0..3\n====\n",
        encoding="utf-8",
    )
    with pytest.raises(UnresolvedExtendsError, match="Missing"):
        resolve_module(tla)


def test_gate_report_fails_closed_on_an_unresolvable_hierarchy(tmp_path: Path) -> None:
    """The gate must REFUSE, not score the fragment it can read."""
    tla = tmp_path / "Orphan.tla"
    tla.write_text(
        "---- MODULE Orphan ----\nEXTENDS Naturals, Missing\nVARIABLES z\n"
        "TypeInvariant == z \\in 0..3\n====\n",
        encoding="utf-8",
    )
    cfg = tmp_path / "MC.cfg"
    cfg.write_text("SPECIFICATION Spec\nINVARIANTS TypeInvariant\n", encoding="utf-8")
    passed, message = gate_report(tla, cfg, None)
    assert passed is False
    assert "could not be resolved" in message
    assert "Missing" in message


def test_cli_fails_closed_nonzero_on_an_unresolvable_hierarchy(tmp_path: Path) -> None:
    tla = tmp_path / "UsesInstance.tla"
    tla.write_text(
        "---- MODULE UsesInstance ----\nEXTENDS Naturals\nVARIABLES y\n"
        "B == INSTANCE Base\nTypeInvariant == y \\in 0..3\n====\n",
        encoding="utf-8",
    )
    cfg = tmp_path / "MC.cfg"
    cfg.write_text("SPECIFICATION Spec\nINVARIANTS TypeInvariant\n", encoding="utf-8")
    assert main([str(tla), str(cfg)]) == EXIT_BUDGET_EXCEEDED
