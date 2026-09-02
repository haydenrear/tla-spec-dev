"""The agent-integration harness has to be trustworthy without spending an agent.

`examples/agent_integration/` dispatches real Claude sessions: a full run costs
real money and up to ninety minutes, so it cannot be a suite test. What CAN be a
suite test is every property the harness's conclusions rest on, and those are
the properties that, if they silently broke, would make a run report a clean
result over a measurement that never happened.

Three of them matter most:

* **the ask must not leak the answer.** A role's `ask` names no flag, file or
  verb; what the agent has to discover is the measurement. An ask that drifts
  into naming `tla-spec-dev --spec-root specs open ticket` has measured the
  agent's reading comprehension, not the toolchain's ergonomics.
* **the done_check must not be reachable from the ask.** An agent that can infer
  the predicate can satisfy the predicate.
* **binding a home must remove the OTHER homes.** `runtime_requirements.md` is
  explicit that this is the part hand-exporting forgets, and this harness
  hand-exports on purpose (see its README). A launch that merely prepends leaves
  the operator's wrappers reachable, and a wrapper resolved from the wrong home
  is a different toolchain wearing the right name.
"""

from __future__ import annotations

import importlib.util
import os
import tomllib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = REPO_ROOT / "examples" / "agent_integration"
HARNESS = EXAMPLE / "run_agent_integration.py"
ROLES = EXAMPLE / "roles.toml"


def _harness():
    spec = importlib.util.spec_from_file_location("agent_integration_harness", HARNESS)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _roles() -> list[dict]:
    return tomllib.loads(ROLES.read_text(encoding="utf-8"))["role"]


def test_both_seats_are_declared() -> None:
    """Two roles, not two runs of one thing. A missing seat is a silent halving."""
    ids = {r["id"] for r in _roles()}
    assert ids == {"epic", "ticket"}, f"expected both seats, got {sorted(ids)}"


#: Things an ask must never contain. Every one of these is either the answer or
#: half of it: a verb the agent is supposed to find, a path it is supposed to
#: discover, or a flag whose absence is itself a measured failure mode.
LEAKS = (
    "tla-spec-dev",
    "--spec-root",
    "--actions-metadata",
    "ticket_plan.yaml",
    "specs/program_model",
    "specs/desired_program_model",
    "specs/.history",
    "scaffold",
    "SELF-IMPROVEMENT-MATRIX",
)


@pytest.mark.parametrize("role", _roles(), ids=lambda r: r["id"])
def test_the_ask_does_not_name_what_the_agent_must_discover(role: dict) -> None:
    ask = role["ask"].lower()
    leaked = [token for token in LEAKS if token.lower() in ask]
    assert not leaked, (
        f"role {role['id']}'s ask names {leaked}, which is what it is supposed to "
        "measure the agent finding. An ask that supplies the answer has measured "
        "nothing."
    )


@pytest.mark.parametrize("role", _roles(), ids=lambda r: r["id"])
def test_the_done_check_is_not_reachable_from_the_ask(role: dict) -> None:
    """An agent that knows the check can satisfy the check without doing the work.

    Compared on the check's PATH-LIKE tokens rather than on whole lines: the
    predicate is shell, and an accidental shared word like `test` or `find`
    proves nothing either way.
    """
    ask = role["ask"].lower()
    paths = {
        token.strip("'\"")
        for token in role["done_check"].split()
        if "/" in token and not token.startswith("-")
    }
    leaked = sorted(p for p in paths if p.lower() in ask)
    assert not leaked, f"role {role['id']}'s ask reveals its own done_check: {leaked}"


@pytest.mark.parametrize("role", _roles(), ids=lambda r: r["id"])
def test_every_role_prices_its_prediction_before_the_round(role: dict) -> None:
    """A prediction recorded after the fact is not a prediction.

    This is the PRICE record kind: declared before, measured after. The field is
    required so a round cannot quietly become a description of whatever happened.
    """
    assert role.get("predicts", "").strip(), f"role {role['id']} predicts nothing"


def test_binding_a_home_removes_every_other_home_from_path(monkeypatch) -> None:
    """The part hand-exporting forgets, asserted rather than trusted."""
    harness = _harness()
    other = "/Users/somebody/.skill-manager/bin/cli"
    monkeypatch.setenv("PATH", os.pathsep.join([other, "/usr/bin", "/bin"]))
    home = Path("/tmp/a-home/.skill-manager")

    env, note = harness.bind_home_env(home)
    parts = env["PATH"].split(os.pathsep)

    assert parts[0] == str(home / "bin" / "cli"), "this home's bin must come first"
    assert other not in parts, (
        "another home's bin survived the bind. `runtime_requirements.md` calls "
        "this exact omission out: prepending is not enough, the other homes have "
        "to go, or a wrapper resolves from the wrong home."
    )
    assert env["SKILL_MANAGER_HOME"] == str(home)
    assert "Not logged in" in note, "the launch note must carry the finding it stands on"


def test_a_failed_call_is_a_defect_only_when_it_invoked_the_toolchain() -> None:
    """The first run reported seven tool errors and six were the agent's own shell.

    False positives are how an instrument gets switched off, so the count the
    harness leads with is classified -- by the COMMAND, never by the message.
    """
    harness = _harness()
    toolchain = {"input": {"command": "tla-spec-dev --spec-root specs close ticket X"}}
    shell = {"input": {"command": "cat a.md; cat b.md; cat missing.md"}}
    assert harness.classify_error(toolchain) == "toolchain"
    assert harness.classify_error(shell) == "shell"


def test_the_attribution_probe_is_silent_on_an_empty_transcript() -> None:
    """No attribution found in nothing is absence of evidence, not evidence of it.

    The probe answers a yes/no about SHAPE. It must say `no` for an empty run --
    a probe that reports `any_attribution_shape` for a transcript with no
    content would turn every failed dispatch into a passing E-09 check.
    """
    harness = _harness()
    empty = harness.attribution_probe({"narration": "", "final": {}})
    assert empty["any_attribution_shape"] is False

    named = harness.attribution_probe(
        {"narration": "this sat under UNMODELED/yaml-parser", "final": {}}
    )
    assert named["named_unmodeled_bin"] == ["UNMODELED/yaml-parser"]

    action = harness.attribution_probe(
        {"narration": "", "final": {"result": "the regression is inside TlaSpecDevCli.CloseTicket"}}
    )
    assert "TlaSpecDevCli.CloseTicket" in action["action_shaped_mentions"]


def test_the_harvest_pairs_an_error_back_to_the_call_that_made_it(tmp_path) -> None:
    """The agent's summary is not evidence; the pairing is.

    A tool_result carries only a `tool_use_id`, so an unpaired harvest reports
    "something failed" with no command -- which is unactionable, and worse,
    indistinguishable from a harness that lost the call.
    """
    harness = _harness()
    stream = tmp_path / "stream.jsonl"
    stream.write_text(
        "\n".join(
            [
                '{"type":"assistant","message":{"content":[{"type":"tool_use","id":"t1",'
                '"name":"Bash","input":{"command":"tla-spec-dev close ticket X"}}]}}',
                '{"type":"user","message":{"content":[{"type":"tool_result","tool_use_id":"t1",'
                '"is_error":true,"content":"ERROR: ticket X is already closed"}]}}',
                '{"type":"result","subtype":"success","num_turns":2,"total_cost_usd":0.5,'
                '"result":"done"}',
            ]
        ),
        encoding="utf-8",
    )
    got = harness.harvest(stream)
    assert got["tool_error_count"] == 1
    assert got["toolchain_error_count"] == 1
    only = got["tool_errors"][0]
    assert only["tool"] == "Bash"
    assert "close ticket X" in str(only["input"])
    assert "already closed" in str(only["error"])
    assert got["final"]["total_cost_usd"] == 0.5


def test_a_missing_stream_is_reported_as_unparsed_not_as_zero_errors(tmp_path) -> None:
    """Zero errors and no transcript must not look the same.

    This project has shipped that exact false pass before: `blind_dispatch.check`
    returned PASS for an empty file and for `Error: Invalid API key` alike, and
    the fix was to refuse a subject that is not a report. A dispatch that never
    started has no errors, and calling that a clean run is the same mistake.
    """
    harness = _harness()
    got = harness.harvest(tmp_path / "nothing.jsonl")
    assert got["parsed"] is False
    assert "tool_error_count" not in got


def _git(cwd: Path, *args: str) -> None:
    import subprocess

    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _repo_with_the_plan_on_another_branch(tmp_path: Path) -> Path:
    """A repository shaped the way `git-epic-workflow` actually leaves one.

    The epic agent works on `epic/<slug>` in its own worktree. The default
    branch carries the accepted baseline and NOT the plan.
    """
    repo = tmp_path / "project"
    (repo / "specs" / "program_model").mkdir(parents=True)
    (repo / "specs" / "program_model" / "Core.tla").write_text("---- MODULE Core ----\n====\n")
    _git(repo.parent, "init", "-q", "-b", "main", str(repo))
    _git(repo, "config", "user.email", "t@t.invalid")
    _git(repo, "config", "user.name", "t")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "baseline")

    _git(repo, "checkout", "-q", "-b", "epic/shortlink-spec")
    plan = repo / "specs" / "desired_program_model"
    plan.mkdir(parents=True)
    (plan / "ticket_plan.yaml").write_text(
        "version: 1\ntickets:\n  - id: SL-1\n    status: open\n", encoding="utf-8"
    )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "plan")
    _git(repo, "checkout", "-q", "main")
    return repo


def test_the_epic_check_looks_on_every_branch_not_just_this_one(tmp_path) -> None:
    """H-01. Round 1 called a complete plan a FAIL because it was on another ref.

    The epic agent produced a validating `ticket_plan.yaml`, three tickets, an
    epic branch and a worktree -- everything `git-epic-workflow` asks for -- and
    this check reported FAIL because it looked only at the working directory.

    **A measurement taken on the wrong fixture is not a refutation; it is a void
    run**, which is the same conclusion round 2 reached about `T1`, and the
    harness owns the error both times. So this asserts the check asks the
    question the workflow answers.
    """
    import subprocess

    repo = _repo_with_the_plan_on_another_branch(tmp_path)
    epic = next(r for r in _roles() if r["id"] == "epic")
    proc = subprocess.run(
        ["bash", "-c", epic["done_check"].strip()], cwd=repo, text=True, capture_output=True
    )
    assert proc.returncode == 0, (
        "the plan is on `epic/shortlink-spec` and the check could not see it:\n"
        f"{proc.stdout}\n{proc.stderr}"
    )
    assert "epic/shortlink-spec" in proc.stdout, (
        "the check must SAY where it found the plan; a bare exit 0 leaves a "
        "reader unable to tell a real pass from a check that stopped looking"
    )


def test_the_check_still_fails_when_nothing_was_planned(tmp_path) -> None:
    """Guard the guard: branch-awareness must not turn the check into a pass.

    Widening a predicate is how a green stops meaning anything. This is the
    negative control for the fix above, and it is the reason the fix is
    trustworthy at all.
    """
    import subprocess

    repo = tmp_path / "bare"
    (repo / "specs" / "program_model").mkdir(parents=True)
    _git(repo.parent, "init", "-q", "-b", "main", str(repo))
    _git(repo, "config", "user.email", "t@t.invalid")
    _git(repo, "config", "user.name", "t")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "--allow-empty", "-m", "nothing planned")

    for role in _roles():
        proc = subprocess.run(
            ["bash", "-c", role["done_check"].strip()], cwd=repo, text=True, capture_output=True
        )
        assert proc.returncode != 0, (
            f"role {role['id']}'s done_check passed on a repository where no agent "
            f"did anything:\n{proc.stdout}"
        )


def test_the_ticket_worktree_branches_from_wherever_the_plan_is(tmp_path) -> None:
    """The other half of H-01: a ticket agent must be handed the plan.

    Round 1 branched the ticket worktree from `main` while the plan sat on
    `epic/shortlink-spec`. Any refusal the ticket agent then hit would have been
    the harness's doing, and would have been recorded against the toolchain.
    """
    harness = _harness()
    repo = _repo_with_the_plan_on_another_branch(tmp_path)
    assert harness._ref_carrying_the_plan(repo) == "epic/shortlink-spec"


def test_no_plan_anywhere_falls_back_rather_than_crashing(tmp_path) -> None:
    """A round where the epic seat produced nothing must still measure the ticket seat.

    Returning HEAD keeps the ticket agent's own behaviour as the thing being
    observed. Raising here would convert a finding about the epic seat into a
    harness crash that reports neither.
    """
    harness = _harness()
    repo = tmp_path / "empty"
    repo.mkdir()
    _git(repo.parent, "init", "-q", "-b", "main", str(repo))
    _git(repo, "config", "user.email", "t@t.invalid")
    _git(repo, "config", "user.name", "t")
    _git(repo, "commit", "-q", "--allow-empty", "-m", "empty")
    assert harness._ref_carrying_the_plan(repo) == "HEAD"


def test_cleanup_removes_the_home_clones_and_nothing_the_agents_wrote(tmp_path) -> None:
    """Two 700MB clones per run, and nothing in the evidence refers to them.

    Left behind, a weekly round costs a gigabyte and a half of disk. Removed
    carelessly, it costs the run. So the cleanup is asserted on both halves at
    once: every `.skill-manager` under the run root goes, and everything else
    stays exactly where the agents left it.
    """
    harness = _harness()
    (tmp_path / "project" / ".skill-manager" / "bin").mkdir(parents=True)
    (tmp_path / "ticket-worktree" / ".skill-manager").mkdir(parents=True)
    (tmp_path / "project" / "shortlink.py").write_text("# the agent's work\n")
    (tmp_path / "project" / "specs").mkdir()

    removed = harness._drop_home_clones(tmp_path)

    assert len(removed) == 2, f"expected both homes, removed {removed}"
    assert not (tmp_path / "project" / ".skill-manager").exists()
    assert not (tmp_path / "ticket-worktree" / ".skill-manager").exists()
    assert (tmp_path / "project" / "shortlink.py").is_file(), "the agent's work was deleted"
    assert (tmp_path / "project" / "specs").is_dir(), "the agent's spec tree was deleted"


def test_cleanup_will_not_follow_a_symlink_out_of_the_run(tmp_path) -> None:
    """A cleanup that can wander is worse than the disk it saves.

    `rglob` cannot leave the root on its own, but a `.skill-manager` SYMLINK
    inside the workspace pointing at the operator's real home is a plausible
    accident — a copied worktree, a hand-made shortcut — and `rmtree` through it
    would take the home this machine works from.
    """
    harness = _harness()
    outside = tmp_path / "outside" / ".skill-manager"
    (outside / "skills").mkdir(parents=True)
    run_root = tmp_path / "run"
    (run_root / "project").mkdir(parents=True)
    (run_root / "project" / ".skill-manager").symlink_to(outside, target_is_directory=True)

    removed = harness._drop_home_clones(run_root)

    # ASSERTED ON THE RETURN VALUE, not just on the survivor. `shutil.rmtree`
    # refuses a symlink and `ignore_errors=True` swallows that refusal, so
    # `outside` survives whether or not the guard exists -- checking only that
    # it survived is a test that passes vacuously, which is the shape this
    # repository has been caught by three times. The guard's observable effect
    # is that the link is SKIPPED rather than attempted.
    assert removed == [], f"the cleanup tried to remove a home outside the run: {removed}"
    assert outside.is_dir(), "the cleanup followed a symlink out of the run root"
    assert (outside / "skills").is_dir()
