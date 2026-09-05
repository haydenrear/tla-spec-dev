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
    assert paths, (
        f"role {role['id']}'s done_check names no path-like token, so this "
        "comparison has nothing to compare and would pass whatever the ask "
        "said. Four other tests in this file carry a non-vacuity guard; this "
        "is that guard."
    )
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
    # No `kind` any more: which calls touched the toolchain is answered by the
    # invocation log, which observes, rather than by reading this command back.
    assert "toolchain_error_count" not in got
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


#: The scaffold placeholders the epic `done_check` refuses. Kept here AND in
#: `roles.toml`, with `test_the_scaffold_still_emits_the_placeholders_the_check_refuses`
#: asserting the scaffold still emits them -- so a rename in
#: `new_ticket_workflow.ticket_plan()` fails a test rather than quietly turning
#: the predicate back into one that accepts a template.
SCAFFOLD_PLACEHOLDERS = (
    "ReplaceWithDesiredAction",
    "replace_with_state_field",
    "Replace with implementation surfaces",
)


def test_the_scaffold_still_emits_the_placeholders_the_check_refuses() -> None:
    """Derived from the scaffold, not retyped from memory of it.

    If `ticket_plan()` renames a placeholder, the epic predicate stops rejecting
    templates and starts passing on two scaffold verbs again -- silently, and in
    exactly the way it already did once. This is the guard on that.
    """
    import sys

    sys.path.insert(0, str(REPO_ROOT))
    try:
        from scripts.new_ticket_workflow import ticket_plan  # type: ignore[import-not-found]
    finally:
        sys.path.pop(0)

    template = ticket_plan("SL-1", "A title", "Shortlink")
    missing = [p for p in SCAFFOLD_PLACEHOLDERS if p not in template]
    assert not missing, (
        f"the scaffold no longer emits {missing}, so the epic done_check's "
        "template rejection is now partly inert. Update both this list and "
        "examples/agent_integration/roles.toml."
    )

    epic = next(r for r in _roles() if r["id"] == "epic")
    absent = [p for p in SCAFFOLD_PLACEHOLDERS if p not in epic["done_check"]]
    assert not absent, f"the epic done_check does not refuse {absent}"


def test_the_epic_check_refuses_a_plan_that_is_still_the_scaffold_template(tmp_path) -> None:
    """Two scaffold verbs and zero thought used to be a PASS.

    `tla-spec-dev scaffold workflow` emits a `ticket_plan.yaml` that already
    contains `tickets:` and `- id: <ticket>`, so the first version of this
    predicate -- a grep for a list item -- returned exit 0 on a plan that was
    100% placeholders. **That was the epic seat's only pass/fail signal**, and
    the role's own `predicts` field says the thing worth watching is whether the
    agent finds the plan half at all.

    The template is generated here rather than pasted, so this control tracks
    the scaffold instead of a snapshot of it.
    """
    import subprocess
    import sys

    sys.path.insert(0, str(REPO_ROOT))
    try:
        from scripts.new_ticket_workflow import ticket_plan  # type: ignore[import-not-found]
    finally:
        sys.path.pop(0)

    repo = tmp_path / "scaffolded"
    (repo / "specs" / "program_model").mkdir(parents=True)
    plan_dir = repo / "specs" / "desired_program_model"
    plan_dir.mkdir(parents=True)
    (plan_dir / "ticket_plan.yaml").write_text(
        ticket_plan("SL-1", "Reserve a short code", "Shortlink"), encoding="utf-8"
    )
    _git(repo.parent, "init", "-q", "-b", "main", str(repo))
    _git(repo, "config", "user.email", "t@t.invalid")
    _git(repo, "config", "user.name", "t")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "scaffold only")

    epic = next(r for r in _roles() if r["id"] == "epic")
    proc = subprocess.run(
        ["bash", "-c", epic["done_check"].strip()], cwd=repo, text=True, capture_output=True
    )
    assert proc.returncode != 0, (
        "the epic done_check PASSED on the shipped scaffold template -- the seat "
        f"has no pass/fail signal:\n{proc.stdout}"
    )
    assert "placeholder" in proc.stdout, (
        "the check refused without saying why; a reader cannot tell a template "
        f"rejection from a missing file:\n{proc.stdout}"
    )


#: State-bearing concepts that would each need real machinery in the fixture --
#: a field, a parameter, a comparison. Narrow on purpose: this is a guard on one
#: demonstrated failure, not a general docstring checker, and it says so.
FIXTURE_CONCEPTS = ("expir", "ttl", "clock", "deadline", "timestamp", "timeout")

#: Everything after this marker is the fixture explaining its own history, and
#: it necessarily names the concept it got wrong.
FIXTURE_CORRECTION_MARKER = "THIS DOCSTRING IS PART OF THE MEASUREMENT"


def test_the_fixture_docstring_promises_nothing_the_fixture_lacks() -> None:
    """The fixture's description IS part of the experiment, and it lied once.

    `shortlink.py` opened *"A link shortener with expiry and a reservation
    window ... a reservation must be claimed before it expires."* **There is no
    expiry in that file** -- no timestamp, no clock, no deadline check. The epic
    agent of round 001 read it, believed it, and built a three-ticket epic
    around implementing "the reservation window the module docstring promises."

    The example exists to see whether an agent finds the trace-only `release`
    property WITHOUT being told where to look. A docstring naming a property the
    program does not have is not a neutral fixture; it is a different
    experiment, run by accident -- and nothing else in the harness can see it.
    `done_check` asks only whether a plan file exists, and `fixture_still_green`
    passes because the agent never touched the module.
    """
    source = (
        REPO_ROOT / "examples/agent_integration/fixture/shortlink.py"
    ).read_text(encoding="utf-8")
    marker = source.find(FIXTURE_CORRECTION_MARKER)
    assert marker > 0, (
        "the fixture's correction marker is gone, so this test cannot tell a "
        "promise from an explanation of a past promise"
    )
    promise, explanation = source[:marker], source[marker:]

    body_start = source.find('"""', source.find('"""') + 3) + 3
    code = source[body_start:].lower()

    leaked = [c for c in FIXTURE_CONCEPTS if c in promise.lower() and c not in code]
    assert not leaked, (
        f"the fixture's opening description names {leaked}, and the code "
        "implements none of it. That is the round-001 defect exactly: the "
        "docstring is what an agent reads first, so it steers the measurement."
    )
    # Non-vacuity: the guard must be looking at a real description, and the
    # explanation below the marker must still be there to be excluded.
    assert len(promise) > 200, "the fixture's description is gone; nothing is guarded"
    assert any(c in explanation.lower() for c in FIXTURE_CONCEPTS), (
        "the record of what went wrong has been edited out of the fixture, and "
        "with it the only reason this test is here"
    )


def test_the_record_does_not_leak_what_the_gitignore_excludes_transcripts_for() -> None:
    """The file that travels must not carry what the file that stays was excluded for.

    `.gitignore` excludes `stream.jsonl` because it *"carries the operator's
    absolute paths, session ids and home layout"*. `RESULT.json` carried the
    same thing — ten occurrences of `/Users/<operator>/` in round 001 across
    `workspace_root`, `home`, `cwd`, `claude_bin` and `preflight.source_home`.
    A stated reason that the neighbouring file violates is not a partial reason;
    it is an untrue one.
    """
    harness = _harness()
    committed = sorted(
        (REPO_ROOT / "examples/agent_integration/evidence/runs").glob("*/RESULT.json")
    )
    assert committed, "no committed RESULT.json to check"
    home = str(Path.home())
    for path in committed:
        text = path.read_text(encoding="utf-8")
        assert home not in text, (
            f"{path.relative_to(REPO_ROOT)} embeds the operator's home path, "
            "which is the reason `.gitignore` gives for excluding the transcripts"
        )
    # Non-vacuity: the redactor must actually be doing something, or these files
    # could be clean because nothing ever wrote a path into them.
    assert harness._redact({"p": f"{home}/x"}) == {"p": "~/x"}


def test_a_timeout_takes_the_whole_process_tree() -> None:
    """`proc.kill()` kills `claude` and nothing it spawned.

    TLC's JVM, a gradle daemon, the fixture's HTTP server: all reparented, all
    still running after the harness prints `timeout`. **The next round then
    inherits a machine the last one did not clean up**, which is a measurement
    of the previous round wearing this one's run id.

    Asserted on a real process tree rather than by reading: a shell that spawns
    a child which outlives it, killed through the group, and the grandchild must
    be gone.
    """
    import os
    import signal
    import subprocess as sp
    import time

    harness = _harness()
    marker = Path(os.environ.get("TMPDIR", "/tmp")) / f"kill-tree-probe-{os.getpid()}"
    marker.unlink(missing_ok=True)
    # The grandchild writes the marker only if it is still alive after the kill.
    child = sp.Popen(
        ["bash", "-c", f"(sleep 2; touch {marker}) & sleep 30"],
        start_new_session=True,
        stdout=sp.DEVNULL,
        stderr=sp.DEVNULL,
    )
    try:
        time.sleep(0.3)
        harness._kill_tree(child)
        time.sleep(3)
        assert not marker.exists(), (
            "a grandchild of the killed process survived and kept working; a "
            "timed-out round leaves its JVMs and servers behind"
        )
    finally:
        marker.unlink(missing_ok=True)
        try:
            os.killpg(os.getpgid(child.pid), signal.SIGKILL)
        except (ProcessLookupError, OSError):
            pass


def test_the_stream_shape_fields_do_not_claim_to_be_turn_counts(tmp_path) -> None:
    """Round 001 carried two turn counts in one file, disagreeing by 50%.

    `assistant_turns: 118` sat beside the result event's `num_turns: 77`,
    because the stream emits one `assistant` event per content BLOCK. Distinct
    message ids give 28 — a third number. None is wrong; they count different
    things, and only one of them is a turn.

    So nothing in the harvest is named for turns any more. `final.num_turns` is
    the agent's own count and is authoritative when a result event exists; these
    two describe raw stream shape, which is what a reader has when it does not.
    """
    harness = _harness()
    stream = tmp_path / "stream.jsonl"
    stream.write_text(
        "\n".join(
            [
                '{"type":"assistant","message":{"id":"m1","content":[{"type":"text","text":"a"}]}}',
                '{"type":"assistant","message":{"id":"m1","content":[{"type":"tool_use","id":"t1",'
                '"name":"Bash","input":{"command":"true"}}]}}',
                '{"type":"assistant","message":{"id":"m2","content":[{"type":"text","text":"b"}]}}',
                '{"type":"result","subtype":"success","num_turns":2,"result":"done"}',
            ]
        ),
        encoding="utf-8",
    )
    got = harness.harvest(stream)
    assert "assistant_turns" not in got, "a field named for turns is back"
    assert got["assistant_events"] == 3, "the raw event count is what it says"
    assert got["assistant_messages"] == 2, "two distinct message ids"
    assert got["final"]["num_turns"] == 2, "the agent's own count is preserved"




# ---------------------------------------------------------------------------
# Observation replaced inference. These are the tests that class needs.
# ---------------------------------------------------------------------------


def test_a_shim_records_the_call_and_preserves_the_exit_status(tmp_path) -> None:
    """The whole replacement, exercised against a real binary and a real shell.

    The classifier it replaces was wrong twice in two rounds, both times
    reporting a defect where there was a DESCRIPTION of one. This cannot be:
    a call either went through the shim or it did not.

    The exit status matters as much as the record. A shim that logs and then
    swallows a non-zero status would make every toolchain refusal look like a
    success to the agent running under it -- the harness would be CAUSING green.
    """
    import os
    import subprocess

    harness = _harness()
    home = tmp_path / "home"
    (home / "bin" / "cli").mkdir(parents=True)
    real = home / "bin" / "cli" / "tla-spec-dev"
    real.write_text('#!/bin/sh\necho "ran: $*"\nexit 3\n', encoding="utf-8")
    real.chmod(0o755)

    shim_dir, log = tmp_path / "shims", tmp_path / "invocations.log"
    watching = harness.install_invocation_shims(home, shim_dir)
    assert "tla-spec-dev" in watching

    env, _ = harness.bind_home_env(home, shim_dir, log)
    assert env["PATH"].split(os.pathsep)[0] == str(shim_dir), (
        "the shim directory is not first on PATH, so the real binary answers "
        "and nothing is recorded"
    )

    proc = subprocess.run(
        ["bash", "-c", "tla-spec-dev --spec-root specs close ticket X"],
        env=env, text=True, capture_output=True,
    )
    assert proc.returncode == 3, "the shim did not preserve the real exit status"
    assert "ran: --spec-root specs close ticket X" in proc.stdout

    recorded = harness.read_invocations(log)
    assert len(recorded) == 1, recorded
    assert recorded[0]["tool"] == "tla-spec-dev"
    assert recorded[0]["exit"] == 3
    assert recorded[0]["argv"] == ["--spec-root", "specs", "close", "ticket", "X"]


def test_mentioning_the_toolchain_records_nothing(tmp_path) -> None:
    """The two defects this replaced, as one input that must now produce zero.

    `H-05` was a failed `cat` of a skill's files counted as running the skill.
    `H-11` was a line inside a `cat <<'YAML'` body -- prose in which the agent
    was WRITING DOWN a finding about `tla-spec-dev` -- counted as invoking it.
    Both are here, and both must record nothing, because nothing ran.
    """
    import subprocess

    harness = _harness()
    home = tmp_path / "home"
    (home / "bin" / "cli").mkdir(parents=True)
    real = home / "bin" / "cli" / "tla-spec-dev"
    real.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    real.chmod(0o755)

    shim_dir, log = tmp_path / "shims", tmp_path / "invocations.log"
    harness.install_invocation_shims(home, shim_dir)
    env, _ = harness.bind_home_env(home, shim_dir, log)

    script = (
        "S=/some/.skill-manager/skills/spec-double-compiler\n"
        "cat $S/references/typical_workflow.md 2>/dev/null\n"
        "cat > /dev/null <<'YAML'\n"
        "  .skill-manager/bin/cli/tla-spec-dev runs a bare python3 from PATH\n"
        "  tla-spec-dev --spec-root specs close ticket X\n"
        "YAML\n"
    )
    subprocess.run(["bash", "-c", script], env=env, text=True, capture_output=True)

    assert harness.read_invocations(log) == [], (
        "something was recorded for a run in which the toolchain was only "
        "MENTIONED -- the false-positive class is back"
    )


def test_a_malformed_record_is_reported_not_dropped(tmp_path) -> None:
    """A run with a broken shim must not read as a run that used nothing.

    Dropping the line would make those two indistinguishable, and one of them
    is success. `SS-02`: an absent input is never a PASS.
    """
    harness = _harness()
    log = tmp_path / "invocations.log"
    log.write_text("garbage-with-no-separators\n", encoding="utf-8")
    recorded = harness.read_invocations(log)
    assert len(recorded) == 1 and "malformed" in recorded[0]


def test_no_log_and_an_empty_log_are_both_empty_but_the_run_says_which(tmp_path) -> None:
    """An absent log is a run that recorded nothing; the record must show it.

    `dispatch` writes `invocation_log` into the result whether or not anything
    landed there, so a reader can tell "the agent used no toolchain" from "the
    shims were never installed".
    """
    harness = _harness()
    assert harness.read_invocations(tmp_path / "nothing.log") == []
    (tmp_path / "empty.log").write_text("", encoding="utf-8")
    assert harness.read_invocations(tmp_path / "empty.log") == []


def test_the_shim_list_is_not_empty() -> None:
    """Guard the guard: shimming nothing observes nothing, silently."""
    harness = _harness()
    assert harness.SHIMMED, "no binary is shimmed; every run would record zero"
    assert "tla-spec-dev" in harness.SHIMMED
