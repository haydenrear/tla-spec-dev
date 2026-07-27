"""MF-029: action-parameter recovery, with a negative control per action.

THE TRAP THIS FILE EXISTS TO PREVENT
------------------------------------
MF-028's spike defaulted ``spec_root`` from ``case.after`` and then "checked"
the result against ``case.after``. The check could not fail, so it passed
vacuously. It was caught only because a negative control that SHOULD have
failed, passed.

So every action here gets two things:

1. a POSITIVE test, deriving the expected parameter by hand from the
   before-state and the transition -- never from the field being checked; and
2. a NEGATIVE CONTROL, a deliberately wrong expectation that MUST make the
   check fail.

``test_every_negative_control_actually_fails`` then executes every negative
control and asserts each one raises. A check that cannot fail is not a check,
and that test is what proves these can. It is the regression guard, and if it
ever goes green-by-vacuity the whole file is worthless.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from infer_action_params import (  # noqa: E402
    EXCEPT_INDEX,
    GUARD_PINNED,
    UNCHECKED,
    UNRECOVERABLE,
    WRITTEN_THROUGH,
    build_recipes,
    build_recipes_from_path,
    infer_params,
    render_audit,
)

# The live model is specs/current while a ticket workflow is open, and the
# accepted specs/program_model baseline once the workflow has closed (a
# promoted default-branch tree has no current/). The two are reconciled
# identical at every close, so either is the real repository model.
_CURRENT = REPO_ROOT / "specs" / "current" / "TlaSpecDevCli.tla"
LIVE_MODEL = _CURRENT if _CURRENT.exists() else REPO_ROOT / "specs" / "program_model" / "TlaSpecDevCli.tla"

# Every parameterisable action label of TlaSpecDevCli, exhaustively. The issue
# said "thirteen"; the module defined FOURTEEN (plus Stutter, which produces no
# edge under [][Next]_vars), and AC-01 added AnalyzeArchitecture for FIFTEEN.
# Auditing the superset is the honest reading of "audit all the labels".
ALL_ACTIONS = (
    "BuildSkillCli",
    "InstallLocalCli",
    "ScaffoldProject",
    "RecordBudgets",
    "ScaffoldWorkflow",
    "OpenTicket",
    "UpdateTicketDesired",
    "UpdateTicketCurrent",
    "AnalyzeComplexity",
    "AnalyzeCorpus",
    "AnalyzeArchitecture",
    "RunEffectConformance",
    "RunKillTest",
    "RunSpecUnitTests",
    "CloseTicket",
)


@pytest.fixture(scope="module")
def recipes():
    return build_recipes_from_path(LIVE_MODEL)


# ---------------------------------------------------------------------------
# State-pair fixtures, written by hand from the model's own guards.
# ---------------------------------------------------------------------------

TICKETS = ("cli_entrypoint", "cli_workflow", "cli_validation")


def state(
    *,
    setup_phase: int,
    spec_root: str,
    ticket_state: dict[str, int] | None = None,
    last_command: str = "Init",
    complexity_gate: str = "unknown",
    corpus_gate: str = "unknown",
    effect_conformance: str = "unknown",
    kill_test: str = "unknown",
    architecture_scan: str = "unknown",
) -> dict:
    base = {ticket: 0 for ticket in TICKETS}
    base.update(ticket_state or {})
    return {
        "setup_phase": setup_phase,
        "spec_root": spec_root,
        "ticket_state": base,
        "lastCommand": last_command,
        "result": {"accepted": True, "reason": "NoReason", "next": "x"},
        "complexity_gate": complexity_gate,
        "corpus_gate": corpus_gate,
        "effect_conformance": effect_conformance,
        "kill_test": kill_test,
        "architecture_scan": architecture_scan,
    }


def pair(action: str) -> tuple[dict, dict]:
    """One legitimate before/after state pair per action label."""
    if action == "BuildSkillCli":
        return (
            state(setup_phase=0, spec_root="NoRoot"),
            state(setup_phase=1, spec_root="NoRoot", last_command="BuildSkillCli"),
        )
    if action == "InstallLocalCli":
        return (
            state(setup_phase=1, spec_root="NoRoot"),
            state(setup_phase=2, spec_root="NoRoot", last_command="InstallLocalCli"),
        )
    if action == "ScaffoldProject":
        # NOTE: before.spec_root is NoRoot. The argument is NOT in the
        # before-state at all -- it only becomes visible because the action
        # writes it through. That is why this action is the trap case.
        return (
            state(setup_phase=2, spec_root="NoRoot"),
            state(setup_phase=3, spec_root="custom_specs"),
        )
    if action == "RecordBudgets":
        return (
            state(setup_phase=3, spec_root="custom_specs"),
            state(setup_phase=4, spec_root="custom_specs"),
        )
    if action == "ScaffoldWorkflow":
        return (
            state(setup_phase=4, spec_root="custom_specs"),
            state(setup_phase=5, spec_root="custom_specs"),
        )
    if action == "OpenTicket":
        return (
            state(setup_phase=5, spec_root="custom_specs"),
            state(setup_phase=5, spec_root="custom_specs", ticket_state={"cli_workflow": 1}),
        )
    if action == "UpdateTicketDesired":
        return (
            state(setup_phase=5, spec_root="custom_specs", ticket_state={"cli_validation": 1}),
            state(setup_phase=5, spec_root="custom_specs", ticket_state={"cli_validation": 2}),
        )
    if action == "UpdateTicketCurrent":
        return (
            state(setup_phase=5, spec_root="custom_specs", ticket_state={"cli_entrypoint": 2}),
            state(setup_phase=5, spec_root="custom_specs", ticket_state={"cli_entrypoint": 3}),
        )
    if action == "AnalyzeComplexity":
        return (
            state(setup_phase=4, spec_root="default_specs"),
            state(setup_phase=4, spec_root="default_specs", complexity_gate="pass"),
        )
    if action == "AnalyzeCorpus":
        return (
            state(setup_phase=4, spec_root="default_specs"),
            state(setup_phase=4, spec_root="default_specs", corpus_gate="pass"),
        )
    if action == "AnalyzeArchitecture":
        return (
            state(setup_phase=4, spec_root="default_specs"),
            state(
                setup_phase=4,
                spec_root="default_specs",
                architecture_scan="unmappable",
            ),
        )
    if action == "RunEffectConformance":
        return (
            state(setup_phase=4, spec_root="default_specs"),
            state(setup_phase=4, spec_root="default_specs", effect_conformance="clean"),
        )
    if action == "RunKillTest":
        return (
            state(setup_phase=4, spec_root="default_specs"),
            state(setup_phase=4, spec_root="default_specs", kill_test="pass"),
        )
    if action == "RunSpecUnitTests":
        return (
            state(
                setup_phase=5,
                spec_root="custom_specs",
                ticket_state={"cli_workflow": 3},
                complexity_gate="pass",
            ),
            state(
                setup_phase=5,
                spec_root="custom_specs",
                ticket_state={"cli_workflow": 4},
                complexity_gate="pass",
                corpus_gate="pass",
                effect_conformance="clean",
            ),
        )
    if action == "CloseTicket":
        return (
            state(setup_phase=5, spec_root="default_specs", ticket_state={"cli_validation": 4}),
            state(setup_phase=5, spec_root="default_specs", ticket_state={"cli_validation": 5}),
        )
    raise AssertionError(f"no fixture for {action}")


# Expected arguments, derived BY HAND from the before-state and the transition.
# Compare each against pair() above: none of these is copied out of a field the
# test then goes on to check.
EXPECTED = {
    "BuildSkillCli": {},
    "InstallLocalCli": {},
    "ScaffoldProject": {"root": "custom_specs"},
    "RecordBudgets": {"root": "custom_specs"},
    "ScaffoldWorkflow": {"root": "custom_specs"},
    "OpenTicket": {"root": "custom_specs", "ticket": "cli_workflow"},
    "UpdateTicketDesired": {"ticket": "cli_validation"},
    "UpdateTicketCurrent": {"ticket": "cli_entrypoint"},
    "AnalyzeComplexity": {"root": "default_specs"},
    "AnalyzeCorpus": {"root": "default_specs"},
    "AnalyzeArchitecture": {"root": "default_specs"},
    "RunEffectConformance": {"root": "default_specs"},
    "RunKillTest": {"root": "default_specs"},
    # CD-09 (G2): the `override` parameter left the model with the withdrawn
    # blocking gate -- RunSpecUnitTests is (root, ticket) now.
    "RunSpecUnitTests": {
        "root": "custom_specs",
        "ticket": "cli_workflow",
    },
    "CloseTicket": {"root": "default_specs", "ticket": "cli_validation"},
}

# A deliberately WRONG expectation per action. Each must make the check fail.
NEGATIVE_CONTROLS = {
    # Nullary actions: claiming any argument at all must fail.
    "BuildSkillCli": {"root": "default_specs"},
    "InstallLocalCli": {"ticket": "cli_workflow"},
    # written-through: the other root in SpecRoots.
    "ScaffoldProject": {"root": "default_specs"},
    # guard-pinned: swap the root.
    "RecordBudgets": {"root": "default_specs"},
    "ScaffoldWorkflow": {"root": "default_specs"},
    "AnalyzeComplexity": {"root": "custom_specs"},
    "AnalyzeCorpus": {"root": "custom_specs"},
    "AnalyzeArchitecture": {"root": "custom_specs"},
    "RunEffectConformance": {"root": "custom_specs"},
    "RunKillTest": {"root": "custom_specs"},
    # except-index: name a ticket that did not change.
    "OpenTicket": {"root": "custom_specs", "ticket": "cli_entrypoint"},
    "UpdateTicketDesired": {"ticket": "cli_workflow"},
    "UpdateTicketCurrent": {"ticket": "cli_validation"},
    "CloseTicket": {"root": "default_specs", "ticket": "cli_entrypoint"},
    # CD-09: `override` no longer exists on this action, so claiming it is
    # claiming a phantom argument -- the check must fail rather than ignore
    # the extra key.
    "RunSpecUnitTests": {
        "root": "custom_specs",
        "ticket": "cli_workflow",
        "override": True,
    },
}


def check_params(recipes, action, expected) -> None:
    """The check under test. Raises AssertionError when the arguments differ."""
    before, after = pair(action)
    actual = infer_params(action, before, after, recipes)
    assert actual == expected, f"{action}: recovered {actual!r}, expected {expected!r}"


# ---------------------------------------------------------------------------
# Positive tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("action", ALL_ACTIONS)
def test_params_recovered_from_state_pair(recipes, action):
    check_params(recipes, action, EXPECTED[action])


# ---------------------------------------------------------------------------
# Negative controls -- the point of the file
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("action", ALL_ACTIONS)
def test_every_negative_control_actually_fails(recipes, action):
    """Every deliberately wrong expectation must make the check FAIL.

    If any of these stops raising, parameter recovery has become vacuous and
    the corpus is back to proving reachability only.
    """
    wrong = NEGATIVE_CONTROLS[action]
    assert wrong != EXPECTED[action], f"{action}: negative control is not actually wrong"
    with pytest.raises(AssertionError):
        check_params(recipes, action, wrong)


def test_negative_controls_cover_every_action():
    assert set(NEGATIVE_CONTROLS) == set(ALL_ACTIONS)
    assert set(EXPECTED) == set(ALL_ACTIONS)


# ---------------------------------------------------------------------------
# Anti-tautology tests: recovery must READ the state pair.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "action,variable",
    [
        ("RecordBudgets", "spec_root"),
        ("ScaffoldWorkflow", "spec_root"),
        ("AnalyzeComplexity", "spec_root"),
        ("AnalyzeCorpus", "spec_root"),
        ("RunEffectConformance", "spec_root"),
        ("RunKillTest", "spec_root"),
        ("OpenTicket", "spec_root"),
        ("CloseTicket", "spec_root"),
        ("RunSpecUnitTests", "spec_root"),
    ],
)
def test_guard_pinned_root_tracks_the_before_state(recipes, action, variable):
    """Perturbing the BEFORE state must move the recovered argument.

    This is what MF-028's spike lacked. A recovery that ignored the state and
    returned a constant would pass the positive test and fail here.
    """
    before, after = pair(action)
    original = infer_params(action, before, after, recipes)["root"]

    perturbed_before = dict(before)
    perturbed_before[variable] = "a_different_root"
    perturbed_after = dict(after)
    perturbed_after[variable] = "a_different_root"
    moved = infer_params(action, perturbed_before, perturbed_after, recipes)["root"]

    assert moved == "a_different_root"
    assert moved != original


@pytest.mark.parametrize(
    "action",
    [
        "RecordBudgets",
        "ScaffoldWorkflow",
        "AnalyzeComplexity",
        "AnalyzeCorpus",
        "RunEffectConformance",
        "RunKillTest",
        "OpenTicket",
        "CloseTicket",
        "RunSpecUnitTests",
    ],
)
def test_guard_pinned_reads_the_before_state_not_the_after_state(recipes, action):
    """Discriminate before-derivation from after-derivation. THE TRAP TEST.

    Every guard-pinned action leaves `spec_root` UNCHANGED, so in any state pair
    the model can actually produce, before and after agree -- and a recovery
    that wrongly read the AFTER state would return the identical value and pass
    every other test in this file. That mutation genuinely survived the suite
    until this test existed.

    So this test feeds a state pair the model would never emit, where the two
    disagree, purely to force the distinction. The guard is `root = spec_root`
    on the UNPRIMED variable, so the answer must be the BEFORE value. This is
    the difference between recovering a parameter and reading it back off the
    thing you are about to check.
    """
    before, after = pair(action)
    before = dict(before)
    after = dict(after)
    before["spec_root"] = "root_before"
    after["spec_root"] = "root_after"

    recovered = infer_params(action, before, after, recipes)["root"]
    assert recovered == "root_before", (
        f"{action}: guard-pinned recovery must read the before-state; "
        f"got {recovered!r}, which is the after-state value"
    )
    assert recovered != "root_after"


@pytest.mark.parametrize(
    "action,changed_ticket",
    [
        ("OpenTicket", "cli_workflow"),
        ("UpdateTicketDesired", "cli_validation"),
        ("UpdateTicketCurrent", "cli_entrypoint"),
        ("CloseTicket", "cli_validation"),
        ("RunSpecUnitTests", "cli_workflow"),
    ],
)
def test_except_index_tracks_which_entry_changed(recipes, action, changed_ticket):
    """The recovered ticket must be the index that actually differs."""
    before, after = pair(action)
    assert infer_params(action, before, after, recipes)["ticket"] == changed_ticket

    # Move the change to a different index; the recovered argument must follow.
    other = next(t for t in TICKETS if t != changed_ticket)
    swapped_before = dict(before)
    swapped_after = dict(after)
    swapped_before["ticket_state"] = {
        other: before["ticket_state"][changed_ticket],
        **{t: before["ticket_state"][t] for t in TICKETS if t != other},
    }
    swapped_before["ticket_state"][changed_ticket] = before["ticket_state"][other]
    swapped_after["ticket_state"] = dict(swapped_before["ticket_state"])
    swapped_after["ticket_state"][other] = after["ticket_state"][changed_ticket]

    assert infer_params(action, swapped_before, swapped_after, recipes)["ticket"] == other


def test_scaffold_project_root_is_not_in_the_before_state(recipes):
    """The written-through case, stated explicitly.

    `root` is recovered from `spec_root'`. It is therefore legitimate to
    recover, and ILLEGITIMATE to then check `spec_root` in the after-state
    against it -- that comparison is the MF-028 tautology. The recipe reports
    the field as unavailable so a consumer cannot make that mistake silently.
    """
    before, after = pair("ScaffoldProject")
    assert before["spec_root"] == "NoRoot"  # the argument is genuinely absent here
    recovered = infer_params("ScaffoldProject", before, after, recipes)["root"]
    assert recovered == after["spec_root"]
    assert recipes["ScaffoldProject"].unavailable_checks == ("spec_root",)


def test_only_written_through_actions_block_a_check(recipes):
    """No guard-pinned or except-index action sacrifices an after-state field."""
    blocking = {
        action: recipe.unavailable_checks
        for action, recipe in recipes.items()
        if recipe.unavailable_checks
    }
    assert blocking == {"ScaffoldProject": ("spec_root",)}


# ---------------------------------------------------------------------------
# UNCHECKED is never fabricated and never permissive.
# ---------------------------------------------------------------------------


def test_override_is_gone_from_the_model_not_inferred(recipes):
    """CD-09 (G2): the withdrawn --allow-over-budget override left the model.

    The parameter list is parsed from the module source, so this is a
    regression against the blocking gate quietly returning: RunSpecUnitTests
    must infer exactly (root, ticket) and nothing may fabricate an `override`.
    """
    before, after = pair("RunSpecUnitTests")
    params = infer_params("RunSpecUnitTests", before, after, recipes)
    assert "override" not in params
    assert set(params) == {"root", "ticket"}


@pytest.mark.parametrize("value", [True, False, None, 0, "", "TRUE", "override"])
def test_unchecked_never_equals_a_concrete_value(value):
    assert UNCHECKED != value
    assert value != UNCHECKED
    assert not (UNCHECKED == value)


def test_unchecked_equals_only_itself():
    from infer_action_params import Unchecked

    assert UNCHECKED == UNCHECKED
    assert UNCHECKED == Unchecked()  # singleton
    assert repr(UNCHECKED) == "UNCHECKED"


def test_except_index_returns_unchecked_when_nothing_changed(recipes):
    """RunSpecUnitTests on a failing gate leaves ticket_state unchanged.

    The model's `ticket_state' = IF ... THEN [... EXCEPT ![ticket] ...] ELSE
    ticket_state` means the EXCEPT branch is not always taken. On the ELSE edge
    the ticket argument is genuinely not determined by the state pair, so it
    must come back UNCHECKED rather than guessed -- and the case is still a
    case.
    """
    before = state(
        setup_phase=5,
        spec_root="custom_specs",
        ticket_state={"cli_workflow": 3},
        complexity_gate="pass",
    )
    after = state(
        setup_phase=5,
        spec_root="custom_specs",
        ticket_state={"cli_workflow": 3},  # unchanged: gate failed
        complexity_gate="pass",
        corpus_gate="fail",
        effect_conformance="clean",
    )
    params = infer_params("RunSpecUnitTests", before, after, recipes)
    assert params["ticket"] is UNCHECKED
    assert params["root"] == "custom_specs"  # still recovered, guard-pinned


def test_ambiguous_multi_index_diff_is_unchecked(recipes):
    """Two changed indices do not justify picking one."""
    before = state(setup_phase=5, spec_root="custom_specs")
    after = state(
        setup_phase=5,
        spec_root="custom_specs",
        ticket_state={"cli_workflow": 1, "cli_entrypoint": 1},
    )
    assert infer_params("OpenTicket", before, after, recipes)["ticket"] is UNCHECKED


# ---------------------------------------------------------------------------
# The audit itself
# ---------------------------------------------------------------------------


def test_audit_covers_every_action(recipes):
    audit = render_audit(recipes)
    for action in ALL_ACTIONS:
        assert f"`{action}`" in audit, f"{action} missing from the audit"
    # CD-09: no parameter anywhere in the model is unrecoverable any more --
    # `override`, the one UNCHECKED parameter, left with the withdrawn gate.
    assert "override" not in audit


def test_mechanism_classification_matches_the_model(recipes):
    def mechanism(action, param):
        return next(p.mechanism for p in recipes[action].params if p.name == param)

    assert mechanism("ScaffoldProject", "root") == WRITTEN_THROUGH
    assert mechanism("OpenTicket", "root") == GUARD_PINNED
    assert mechanism("OpenTicket", "ticket") == EXCEPT_INDEX
    assert mechanism("CloseTicket", "root") == GUARD_PINNED
    assert mechanism("CloseTicket", "ticket") == EXCEPT_INDEX
    assert recipes["BuildSkillCli"].params == ()
    assert recipes["InstallLocalCli"].params == ()


def test_all_fifteen_action_labels_are_audited(recipes):
    """Completeness: every Next disjunct appears, none is silently skipped.

    AC-01 added the fifteenth, AnalyzeArchitecture.
    """
    audited = set(recipes) - {"Stutter"}
    assert audited == set(ALL_ACTIONS), f"unaudited: {audited ^ set(ALL_ACTIONS)}"


# ---------------------------------------------------------------------------
# Revertibility and inertness
# ---------------------------------------------------------------------------


def test_inference_is_off_without_recipes():
    """Passing no recipes restores the old params={} behavior exactly."""
    before, after = pair("OpenTicket")
    assert infer_params("OpenTicket", before, after, None) == {}
    assert infer_params("OpenTicket", before, after, {}) == {}


def test_unknown_action_yields_no_params(recipes):
    before, after = pair("OpenTicket")
    assert infer_params("NotAnAction", before, after, recipes) == {}


def test_module_without_parameters_produces_empty_recipes():
    source = """
VARIABLES x

Init == x = 0

Tick ==
  /\\ x' = x + 1
"""
    recipes = build_recipes(source)
    assert recipes["Tick"].params == ()
    assert recipes["Tick"].fully_recoverable
