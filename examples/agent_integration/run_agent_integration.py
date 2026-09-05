#!/usr/bin/env python3
"""Run the two agent roles this workflow actually has, as real agents.

Every other example in this repository validates the toolchain by calling it.
This one validates the toolchain by **giving it to an agent and watching**, which
is the only way to see the defect class the rest cannot: a rule that is written
down but unreachable from the path an agent walks. E-09 was exactly that -- the
whole bug-attribution apparatus existed, was correct, and was invisible, because
nothing in the always-loaded entry point referred to it. No unit test can be red
for that. An agent can.

Two roles, and they are not two runs of one thing:

  epic     project tier. Owns the plan, dispatches tickets, never implements.
           Sole writer of the self-improvement matrix.
  ticket   worktree tier. Takes one ticket out of a plan it did not write,
           implements it, closes it, and is expected to attribute what it hit.

Each gets a **full Skill Manager home of its own**, cloned at its own tier, with
`skt` loaded so its status report is injected the way it is in a real session.
That is not ceremony: `tlc2`, `jinja2` and `tla-spec-dev` are per-home wrappers
with an absolute path baked into the body (references/runtime_requirements.md),
so an agent run against the operator's PATH is running a different toolchain
than the one under test.

The launch is bound BY HAND rather than through `skill-manager exec`, which the
reference recommends, because `exec` starts an unauthenticated session -- see
`LAUNCH_NOTE`, which carries the measurement. (`pytest` is a declared CLI
dependency of this skill and is not in any home's `bin/cli`; the tests are run
the way README.md documents, through `uv run`.)

WHAT THIS MEASURES, and it is deliberately not the agent's opinion of itself:

  * `done_check`  -- a shell predicate over the workspace, run by the harness,
                     never shown to the agent and never named in the ask.
  * tool errors   -- every `is_error` tool result in the transcript, paired back
                     to the command that produced it. This is the bug harvest.
                     A refusal an agent recovered from silently is still a
                     refusal, and the agent's summary will not mention it.
  * fixture tests -- green before, and re-run after. An agent that modeled the
                     program by breaking it has not modeled it.
  * workspace git -- what actually landed, versus what the agent says landed.

The workspace lives OUTSIDE this repository. Agents write, and a harness that
lets them write into the checkout under test is measuring a moving target.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EXAMPLE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = EXAMPLE_ROOT.parents[1]
FIXTURE = EXAMPLE_ROOT / "fixture"
ROLES_TOML = EXAMPLE_ROOT / "roles.toml"
EVIDENCE_ROOT = EXAMPLE_ROOT / "evidence" / "runs"
DEFAULT_SOURCE_HOME = Path.home() / ".skill-manager"

# Tier -> where that tier's home lives, from references/runtime_requirements.md.
# Both are `.skill-manager` beside the tree; the difference is which tree.
TIER_HOME_DIRNAME = ".skill-manager"


def _load_roles() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Parse roles.toml. tomllib is stdlib from 3.11; this repo requires newer."""
    import tomllib

    data = tomllib.loads(ROLES_TOML.read_text(encoding="utf-8"))
    defaults = data.get("defaults", {})
    roles = data.get("role", [])
    if not roles:
        raise SystemExit(f"ERROR: {ROLES_TOML} declares no [[role]]")
    return defaults, roles


def _run(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    timeout: float | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess:
    proc = subprocess.run(
        command, cwd=cwd, env=env, text=True, capture_output=True, timeout=timeout
    )
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"command failed ({proc.returncode}): {' '.join(command)}\n"
            f"--- stdout ---\n{proc.stdout}\n--- stderr ---\n{proc.stderr}"
        )
    return proc


def _default_run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rev = subprocess.run(
        ["git", "rev-parse", "--short=12", "HEAD"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    ).stdout.strip()
    return f"{stamp}-{rev or 'nogit'}"


# ---------------------------------------------------------------------------
# Preflight. Every one of these is a REASON THE RUN IS NOT A MEASUREMENT, so
# each is refused up front rather than discovered as a confusing agent failure
# twenty minutes in.
# ---------------------------------------------------------------------------
def preflight(source_home: Path) -> dict[str, Any]:
    report: dict[str, Any] = {}
    for tool in ("claude", "skill-manager", "git"):
        found = shutil.which(tool)
        report[tool] = found
        if not found:
            raise SystemExit(f"ERROR: {tool} is not on PATH; this harness dispatches real agents")

    if not source_home.is_dir():
        raise SystemExit(f"ERROR: source home {source_home} does not exist")
    report["source_home"] = str(source_home)

    proc = _run(
        ["skill-manager", "home", "describe", "--home", str(source_home), "--json"],
        cwd=REPO_ROOT,
        check=False,
    )
    if proc.returncode == 0:
        try:
            descriptor = json.loads(proc.stdout)
        except json.JSONDecodeError:
            report["source_home_descriptor"] = {"raw": proc.stdout[:2000]}
        else:
            # The fields that decide whether a run is comparable to another run.
            # The full descriptor is a snapshot of every installed unit -- machine
            # state, not a finding, and the bulk of what made this record leak the
            # operator's home layout.
            report["source_home_descriptor"] = {
                key: descriptor.get(key)
                for key in ("tier", "policy", "cliVersion", "unitCount")
                if key in descriptor
            }
            units = descriptor.get("units")
            if isinstance(units, list):
                report["source_home_descriptor"]["units"] = len(units)
    else:
        report["source_home_descriptor"] = {"error": proc.stderr[:2000]}

    # A fixture that is already red measures nothing downstream.
    fixture_proc = _run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(FIXTURE), "-t", str(FIXTURE)],
        cwd=FIXTURE,
        check=False,
    )
    report["fixture_green_before"] = fixture_proc.returncode == 0
    if fixture_proc.returncode != 0:
        raise SystemExit(
            "ERROR: the fixture's own tests are red BEFORE any agent ran:\n"
            f"{fixture_proc.stderr[-4000:]}"
        )
    return report



PLAN_PATH = "specs/desired_program_model/ticket_plan.yaml"


def _ref_carrying_the_plan(workspace: Path, default: str = "HEAD") -> str:
    """The ref a ticket agent should branch from: whichever one has the plan.

    Prefers a branch whose name looks like an epic branch, because that is the
    convention `git-epic-workflow` establishes and the one an epic agent will
    have followed. Falls back to `default` so a run where no plan was produced
    still proceeds and the ticket agent's own behaviour is what gets measured.
    """
    refs = subprocess.run(
        ["git", "for-each-ref", "--format=%(refname:short)", "refs/heads"],
        cwd=workspace, text=True, capture_output=True,
    ).stdout.split()
    carrying = [
        ref
        for ref in refs
        if subprocess.run(
            ["git", "cat-file", "-e", f"{ref}:{PLAN_PATH}"],
            cwd=workspace, capture_output=True,
        ).returncode == 0
    ]
    if not carrying:
        return default
    for ref in carrying:
        if ref.startswith("epic/"):
            return ref
    return carrying[0]


# ---------------------------------------------------------------------------
# Workspace
# ---------------------------------------------------------------------------
def build_workspace(root: Path) -> Path:
    """A fresh git repository holding the fixture and nothing else."""
    workspace = root / "project"
    workspace.mkdir(parents=True)
    for item in sorted(FIXTURE.iterdir()):
        if item.name == "__pycache__":
            continue
        shutil.copy2(item, workspace / item.name)
    (workspace / ".gitignore").write_text(
        # The home is a real 700MB tree. It is gitignored at every tier by
        # design (runtime_requirements.md); committing it here would also make
        # the ticket worktree checkout take minutes.
        ".skill-manager/\n__pycache__/\n*.pyc\n",
        encoding="utf-8",
    )
    (workspace / "README.md").write_text(
        "# shortlink\n\n"
        "A link shortener with reservations, claims, releases and resolution.\n"
        "`shortlink.py` is the program. `test_shortlink.py` is what currently\n"
        "holds it up.\n",
        encoding="utf-8",
    )
    _run(["git", "init", "-q", "-b", "main"], cwd=workspace)
    _run(["git", "config", "user.email", "harness@tla-spec-dev.invalid"], cwd=workspace)
    _run(["git", "config", "user.name", "agent-integration harness"], cwd=workspace)
    _run(["git", "add", "-A"], cwd=workspace)
    _run(
        ["git", "commit", "-q", "-m", "shortlink: the program, and the tests that hold it up"],
        cwd=workspace,
    )
    return workspace


def clone_home(source: Path, dest: Path) -> dict[str, Any]:
    """A full home per tier. `home clone` skips cache/ and re-anchors state."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    proc = _run(
        [
            "skill-manager", "home", "clone",
            "--from", str(source),
            "--to", str(dest),
            "--json",
        ],
        cwd=REPO_ROOT,
        check=False,
        timeout=1800,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"home clone {source} -> {dest} failed:\n{proc.stderr}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"raw": proc.stdout[:4000]}


# ---------------------------------------------------------------------------
# Binding a launch to a home
# ---------------------------------------------------------------------------
LAUNCH_NOTE = """\
LAUNCH STYLE: hand-bound, NOT `skill-manager exec`, and that is a finding
rather than a preference.

references/runtime_requirements.md says to launch through the home's
`bin/launch/{claude,codex,gemini}` shims or `skill-manager exec`, because those
put the home's bin/ first and strip other homes' bin/ -- "the part
hand-exporting always misses". This harness measured that path and it does not
start a session:

    $ skill-manager exec --home ~/.skill-manager -- claude -p "say OK"
    Not logged in - Please run /login          (terminal_reason: api_error)

That is the ROOT home, whose CLAUDE_CONFIG_DIR resolves to the operator's own
~/.claude, so it is not the per-home config redirect. The same prompt run
without `exec` completes normally, and completes normally again with
SKILL_MANAGER_HOME and PATH bound to the same home by hand. Measured on
skill-manager 0.25.1 / claude 2.1.258 with keychain OAuth; an ANTHROPIC_API_KEY
launch passes its key through the environment and would not see this.

So the binding here is done explicitly, and it does the one thing the docs warn
hand-exporting forgets: every OTHER home's bin/ is removed from PATH, not just
this home's prepended. What is bound:

    SKILL_MANAGER_HOME  -> this tier's home
    PATH                -> this home's bin/cli and bin/mcp first, every other
                           home's bin removed
    CLAUDE_CONFIG_DIR   -> LEFT ALONE. Redirecting it is what `exec` does and
                           it is also what leaves the launch unauthenticated.

What that costs, stated rather than glossed: `tla-spec-dev`, `tlc2`, `pytest`
and `jinja2` come from THIS home (the wrappers with its absolute path baked in,
which is the isolation runtime_requirements.md actually argues for), while the
skill and plugin BYTES come from the operator's agent config. skt therefore
loads, and its `skt status` report is produced by this home's `skt`.\
"""


def bind_home_env(home: Path) -> tuple[dict[str, str], str]:
    """Environment for a launch bound to `home`. See LAUNCH_NOTE."""
    env = dict(os.environ)
    env["SKILL_MANAGER_HOME"] = str(home)
    # Strip EVERY home's bin, including the operator's, then prepend this one.
    # A launch that merely prepends leaves the previous home's wrappers
    # reachable, and a wrapper resolved from the wrong home is a different
    # toolchain wearing the right name.
    kept = [
        part
        for part in os.environ.get("PATH", "").split(os.pathsep)
        if part and f"{os.sep}.skill-manager{os.sep}" not in part + os.sep
    ]
    env["PATH"] = os.pathsep.join(
        [str(home / "bin" / "cli"), str(home / "bin" / "mcp"), *kept]
    )
    # The harness's own session must not be inherited as the agent's session.
    for leak in ("CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_CHILD_SESSION"):
        env.pop(leak, None)
    return env, LAUNCH_NOTE


def _drop_home_clones(ws_root: Path) -> list[str]:
    """Remove the cloned Skill Manager homes, leaving everything the agents wrote.

    Only directories named exactly `.skill-manager` INSIDE the run's own
    workspace root are removed, and the root is resolved first: a cleanup that
    can wander is worse than a gigabyte of disk.
    """
    root = ws_root.resolve()
    removed: list[str] = []
    for home in sorted(root.rglob(TIER_HOME_DIRNAME)):
        if not home.is_dir():
            continue
        if root not in home.resolve().parents:
            # REACHABLE, and `test_cleanup_will_not_follow_a_symlink_out_of_the_run`
            # reaches it: a `.skill-manager` SYMLINK inside the workspace names a
            # path outside the root, and `rglob` will hand it to us.
            continue
        shutil.rmtree(home, ignore_errors=True)
        removed.append(str(home))
    return removed


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------
def dispatch(
    *,
    role: dict[str, Any],
    defaults: dict[str, Any],
    cwd: Path,
    home: Path,
    out_dir: Path,
) -> dict[str, Any]:
    """Run one real agent, streaming its transcript to disk as it goes.

    `stream-json` rather than `json`: the FINAL message is the agent's account
    of itself, and the agent's account of itself is exactly the thing this
    harness must not trust. The stream carries every tool call and every tool
    error, including the ones the agent worked around without mentioning.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    ask = str(role["ask"]).strip()
    (out_dir / "ask.txt").write_text(ask + "\n", encoding="utf-8")
    budget = float(role.get("budget_seconds", defaults.get("budget_seconds", 1500)))
    mode = str(role.get("permission_mode", defaults.get("permission_mode", "bypassPermissions")))

    env, launch_note = bind_home_env(home)
    claude_bin = shutil.which("claude", path=env["PATH"]) or "claude"
    command = [
        claude_bin,
        "-p", ask,
        "--permission-mode", mode,
        "--output-format", "stream-json",
        "--verbose",
    ]
    (out_dir / "command.txt").write_text(
        " ".join(command) + "\n\n" + launch_note + "\n", encoding="utf-8"
    )

    started = time.perf_counter()
    status = "ok"
    with (out_dir / "stream.jsonl").open("w", encoding="utf-8") as stream, (
        out_dir / "stderr.txt"
    ).open("w", encoding="utf-8") as errfile:
        # OWN SESSION, so a timeout can take the whole tree. `proc.kill()`
        # kills `claude` and nothing it spawned: TLC's JVM, a gradle daemon, the
        # fixture's HTTP server are reparented and keep running, and the next
        # round inherits a machine the last one did not clean up. A harness that
        # reports `timeout` while leaving a JVM holding the port is measuring
        # the previous round.
        proc = subprocess.Popen(
            command, cwd=cwd, env=env, stdout=stream, stderr=errfile, text=True,
            start_new_session=True,
        )
        try:
            returncode = proc.wait(timeout=budget)
        except subprocess.TimeoutExpired:
            _kill_tree(proc)
            returncode = -9
            status = "timeout"
    duration = time.perf_counter() - started

    return {
        "role": role["id"],
        "tier": role.get("tier"),
        "home": str(home),
        "launch_style": "hand-bound",
        "launch_note": launch_note,
        "claude_bin": claude_bin,
        "cwd": str(cwd),
        "status": status,
        "returncode": returncode,
        "duration_seconds": round(duration, 3),
        "budget_seconds": budget,
        "permission_mode": mode,
    }



def _kill_tree(proc: "subprocess.Popen[str]") -> None:
    """SIGKILL the process GROUP, falling back to the process itself.

    `start_new_session=True` makes the child a group leader, so its pid is the
    group id and one `killpg` reaches everything it spawned. The fallback
    matters on the race where the child has already exited: `killpg` then raises
    `ProcessLookupError`, and a harness that dies in its own cleanup loses the
    transcript of the round it was cleaning up after.
    """
    import signal

    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        proc.kill()
    try:
        proc.wait(timeout=30)
    except subprocess.TimeoutExpired:  # pragma: no cover - the group refused to die
        pass


# ---------------------------------------------------------------------------
# Harvest -- the part that finds bugs
# ---------------------------------------------------------------------------
def harvest(stream_path: Path) -> dict[str, Any]:
    """Pair every failed tool result back to the call that produced it.

    The agent's own summary is not evidence of what went wrong: an agent that
    hit three refusals and recovered reports a success. These pairs are what the
    refusals actually were, in the agent's own working order.
    """
    calls: dict[str, dict[str, Any]] = {}
    errors: list[dict[str, Any]] = []
    text_blocks: list[str] = []
    final: dict[str, Any] = {}
    message_ids: set[str] = set()
    events = 0

    if not stream_path.is_file():
        return {"parsed": False, "reason": "no stream file"}

    for line in stream_path.read_text(errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        etype = event.get("type")
        if etype == "assistant":
            # NOT A TURN COUNT, and it used to be labelled as one. The stream
            # emits an `assistant` event per content BLOCK, so round 001
            # recorded `assistant_turns: 118` beside the result event's
            # `num_turns: 77` -- two turn counts in one file disagreeing by 50%,
            # which is worse than having neither. Distinct message ids give 28,
            # a third number; none of the three is wrong, they count different
            # things.
            #
            # So nothing here claims to be the turn count. `final.num_turns` is
            # the agent's own, and it is authoritative when the run produced a
            # result event. These two are raw stream shape, useful precisely
            # when it did not -- a timeout has no result event and these are all
            # a reader gets.
            events += 1
            message_ids.add(event.get("message", {}).get("id") or f"anon-{events}")
            for block in event.get("message", {}).get("content", []) or []:
                if block.get("type") == "tool_use":
                    calls[block.get("id", "")] = {
                        "tool": block.get("name"),
                        "input": block.get("input"),
                    }
                elif block.get("type") == "text":
                    text_blocks.append(block.get("text", ""))
        elif etype == "user":
            for block in event.get("message", {}).get("content", []) or []:
                if not isinstance(block, dict) or block.get("type") != "tool_result":
                    continue
                if not block.get("is_error"):
                    continue
                call = calls.get(block.get("tool_use_id", ""), {})
                content = block.get("content")
                if isinstance(content, list):
                    content = "\n".join(
                        c.get("text", "") for c in content if isinstance(c, dict)
                    )
                # CLASSIFY BEFORE TRIMMING. `_trim` turns a long input dict
                # into JSON text, and a classifier handed text instead of a
                # command sees no executable and reports `shell` -- silently
                # clean, for every long command, which is the exact direction
                # this instrument must not fail in.
                record = {
                    "tool": call.get("tool"),
                    "kind": classify_error({"input": call.get("input")}),
                    "input": _trim(call.get("input")),
                    "error": _trim(content, 4000),
                }
                errors.append(record)
        elif etype == "result":
            final = {
                "subtype": event.get("subtype"),
                "is_error": event.get("is_error"),
                "num_turns": event.get("num_turns"),
                "duration_ms": event.get("duration_ms"),
                "total_cost_usd": event.get("total_cost_usd"),
                "usage": event.get("usage"),
                "result": _trim(event.get("result"), 20000),
            }

    toolchain = [e for e in errors if e["kind"] == "toolchain"]

    return {
        "parsed": True,
        "assistant_events": events,
        "assistant_messages": len(message_ids),
        "tool_calls": len(calls),
        "tool_errors": errors,
        "tool_error_count": len(errors),
        "toolchain_error_count": len(toolchain),
        "shell_error_count": len(errors) - len(toolchain),
        "final": final,
        "narration": _trim("\n\n".join(text_blocks), 20000),
    }


# What counts as INVOKING the toolchain, decided from the EXECUTABLE.
#
# The first version matched these as substrings anywhere in the command blob,
# and on this repository's own committed evidence that was **75% wrong**: three
# of the epic seat's four "toolchain" errors were
# `E=.skill-manager/skills/...; cat $E/a; cat $E/b` -- a failed `cat` whose PATH
# happened to contain `.skill-manager`. Exactly the shape the classifier exists
# to exclude, counted as the thing it exists to find, in the number the harness
# prints and leads with.
#
# Worse, the unit test passed anyway: its negative input was
# `cat a.md; cat b.md; cat missing.md`, a cat chain with no toolchain-shaped
# path in it. **The real failing input was sitting in the repository as
# committed evidence and was not used.** It is used now.
#
# So a command is split into segments and each segment's executable is
# identified. A path that is merely an ARGUMENT is not an invocation.
TOOLCHAIN_EXECUTABLES = {
    "tla-spec-dev",
    "tla_spec_dev.py",
    "tlc2",
    "skt",
    "skill-manager",
    "gradlew",
}

#: Scripts of this repository that ARE the toolchain, by basename.
TOOLCHAIN_SCRIPTS = {
    "generate_cases_from_tlc_dump.py",
    "run_generated_case_adapters.py",
    "export_testgraph_cases.py",
    "new_ticket_workflow.py",
    "close_tickets.py",
    "analyze_complexity.py",
    "corpus_diagnostics.py",
    "scaffold_spec.py",
    "onboard_program_model.py",
    "generate_python.py",
    "spec_paths.py",
}

#: An interpreter runs whatever it is handed; the script is the executable.
INTERPRETERS = {"python", "python3", "python3.14", "uv", "bash", "sh", "env"}

_SEGMENT = re.compile(r"[;&|]{1,2}|\n")
_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
#: `cat > f <<'YAML'` ... `YAML`. Everything between is DATA, not shell.
_HEREDOC = re.compile(r"<<-?\s*[\"\']?([A-Za-z_][A-Za-z0-9_]*)[\"\']?")


def _strip_heredocs(command: str) -> str:
    """Remove heredoc BODIES before looking for executables.

    Round 002 flagged a ticket-seat error as `toolchain` because a line inside a
    `cat > deferred_findings.yaml <<'YAML'` body began with
    `.skill-manager/bin/cli/tla-spec-dev runs a bare python3 from PATH` -- prose
    the agent was WRITING DOWN, in a finding it had just made, read by this
    classifier as a command it had run. The seat's real toolchain-error count
    for that round is zero.

    That is the over-claiming shape twice over: first `skill-manager` matched as
    a substring anywhere, and when that was fixed to match on the executable,
    heredoc text still reached the executable position. **Both times the
    instrument reported a defect where there was documentation of one.**
    """
    out: list[str] = []
    terminator: str | None = None
    for line in command.splitlines():
        if terminator is not None:
            if line.strip() == terminator:
                terminator = None
            continue
        out.append(line)
        found = _HEREDOC.search(line)
        if found:
            terminator = found.group(1)
    return "\n".join(out)


def _executables(command: str) -> list[str]:
    """The executable of each segment of a shell command.

    Leading `VAR=value` assignments and interpreters are stepped over, so
    `E=/x; python3 /a/b/gen.py --out ...` yields `gen.py` and
    `E=/x; cat $E/f` yields `cat`.
    """
    found: list[str] = []
    for segment in _SEGMENT.split(_strip_heredocs(command)):
        tokens = segment.strip().split()
        while tokens and (_ASSIGNMENT.match(tokens[0]) or tokens[0] in {"then", "do", "!", "("}):
            tokens = tokens[1:]
        while tokens and tokens[0] in INTERPRETERS:
            # Step past the interpreter and its own flags to the script it runs.
            tokens = tokens[1:]
            while tokens and tokens[0].startswith("-"):
                tokens = tokens[1:]
                # `uv run --with pytest python ...`: values follow some flags.
                if tokens and not tokens[0].startswith("-") and tokens[0] not in INTERPRETERS:
                    break
        if tokens:
            found.append(tokens[0].rstrip("'\"").split("/")[-1])
    return found


def classify_error(entry: dict[str, Any]) -> str:
    """`toolchain` if the failing call INVOKED the thing under test, else `shell`.

    Classified by what was executed, never by what appears in the text. A rule
    that reads the output drifts toward matching the findings already known,
    which is MF-020 with extra steps; a rule that reads any substring of the
    command counts a `cat` of a skill's file as running the skill.
    """
    payload = entry.get("input") or {}
    if isinstance(payload, str):
        # A harvested record read back from RESULT.json: `_trim` may have turned
        # the input into JSON text, and a re-classification of committed
        # evidence has to be able to read it. Falling through to "shell" here
        # would make every past round look clean, which is a false PASS in the
        # one direction this instrument must never fail.
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            payload = {"command": payload}
    command = payload.get("command") if isinstance(payload, dict) else None
    if not isinstance(command, str):
        # A non-Bash tool (Read, Edit, ...) is never a toolchain invocation.
        return "shell"
    for executable in _executables(command):
        if executable in TOOLCHAIN_EXECUTABLES or executable in TOOLCHAIN_SCRIPTS:
            return "toolchain"
        # A script belonging to another installed unit -- `.../skills/<unit>/
        # scripts/<x>.py` -- is that unit's surface, and running it is an
        # invocation of the toolchain even though the file is not ours.
        if executable.endswith(".py") and re.search(
            r"skills/[^/\s]+/scripts/[^/\s]*" + re.escape(executable), command
        ):
            return "toolchain"
    return "shell"


def _trim(value: Any, limit: int = 1200) -> Any:
    if value is None:
        return None
    text = value if isinstance(value, str) else json.dumps(value, default=str)
    if len(text) <= limit:
        return value if isinstance(value, str) else text
    return text[:limit] + f"\n... [{len(text) - limit} more chars]"



def _redact(value: Any) -> Any:
    """Replace the operator's home prefix with `~`, everywhere, recursively.

    `.gitignore` excludes the transcripts because they *"carry the operator's
    absolute paths, session ids and home layout"*. RESULT.json carried the same
    thing -- `workspace_root`, `home`, `cwd`, `claude_bin`,
    `preflight.source_home` -- ten occurrences of `/Users/<operator>/` in round
    001. **The file that travels was leaking what the file that stays was
    excluded for**, which makes the stated reason untrue rather than merely
    incomplete.

    `~` rather than deletion: a reader still needs to see that the workspace was
    outside the repository and which tier a home was, and a redacted path that
    keeps its shape says both.
    """
    home = str(Path.home())
    if isinstance(value, str):
        return value.replace(home, "~")
    if isinstance(value, dict):
        return {k: _redact(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact(v) for v in value]
    return value


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------
def run_done_check(check: str, cwd: Path, out_dir: Path) -> dict[str, Any]:
    script = check.strip()
    proc = subprocess.run(["bash", "-c", script], cwd=cwd, text=True, capture_output=True)
    (out_dir / "done_check.txt").write_text(
        f"$ {script}\nexit={proc.returncode}\n{proc.stdout}\n{proc.stderr}\n",
        encoding="utf-8",
    )
    return {"passed": proc.returncode == 0, "exit": proc.returncode, "script": script}


def fixture_still_green(cwd: Path) -> dict[str, Any]:
    """The program the agent was modeling must still work.

    Run with the harness interpreter from the workspace -- the agent may have
    introduced a venv, and a green under a venv the harness cannot see is not
    the property being asserted here.
    """
    if not (cwd / "test_shortlink.py").is_file():
        return {"ran": False, "reason": "test_shortlink.py is gone from the workspace"}
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "test_shortlink", "-v"],
        cwd=cwd,
        text=True,
        capture_output=True,
    )
    return {
        "ran": True,
        "passed": proc.returncode == 0,
        "output": _trim(proc.stdout + proc.stderr, 4000),
    }


def workspace_state(cwd: Path) -> dict[str, Any]:
    def git(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=cwd, text=True, capture_output=True
        ).stdout.strip()

    def shell(script: str, limit: int = 4000) -> Any:
        return _trim(
            subprocess.run(
                ["bash", "-c", script], cwd=cwd, text=True, capture_output=True
            ).stdout,
            limit,
        )

    return {
        "status": _trim(git("status", "--porcelain"), 8000),
        "log": _trim(git("log", "--oneline", "-20"), 4000),
        "spec_tree": shell("find specs -maxdepth 3 2>/dev/null | sort | head -80", 6000),
        # HARNESS-SIDE COUNTS, because the numbers a write-up quotes must have a
        # source that is not the agent's closing message. Round 001's report
        # ("13 Internal and 13 mirrored External actions", "112 spec-unit cases",
        # "111 distinct states") was true -- confirmed afterwards by reading the
        # workspace off disk -- but at the time its only source was the
        # transcript, which `dispatch()`'s own docstring says is the one thing
        # this harness must not trust. Every count below is read from a file the
        # agent left behind, not from what it said about them.
        "declared_actions": shell(
            "grep -cE '^  [A-Za-z][A-Za-z0-9_]*:' specs/program_model/actions.yml 2>/dev/null",
            200,
        ),
        "generated_cases": shell(
            "for f in $(find specs/generated -name cases.py 2>/dev/null); do "
            "printf '%s %s\\n' \"$(grep -c 'StateGraphCase(' $f)\" \"$f\"; done",
            2000,
        ),
        "exported_traces": shell(
            "find specs/generated -path '*traces/*.json' 2>/dev/null | wc -l", 200
        ),
        "results": shell(
            "for f in $(find specs -path '*results*' -name '*.txt' 2>/dev/null | head -12); do "
            "printf '\\n--- %s\\n' \"$f\"; tail -3 \"$f\"; done",
            8000,
        ),
    }


# ---------------------------------------------------------------------------
# The attribution probe -- E-09's regression, asked of a real transcript
# ---------------------------------------------------------------------------
ACTION_RE = re.compile(r"\b[A-Z][A-Za-z0-9_]*\.[A-Z][A-Za-z0-9_]*\b")


def attribution_probe(harvested: dict[str, Any]) -> dict[str, Any]:
    """Did the closing agent name a TLA+ action or an UNMODELED bin?

    SKILL.md step 13 tells a closing agent to name `<Module>.<Action>` or
    `UNMODELED/<bin>`. This does NOT check that the naming is correct -- fitting
    a recogniser to a known answer is MF-020 and this project has refused it
    three times. It checks only whether the SHAPE the instruction asks for
    appears anywhere in what the agent produced.

    **A ZERO IS `UNDECIDED`, NOT A FAILURE**, and the first version of this
    docstring said otherwise. Round 001 read zero in both seats and the obvious
    conclusion -- E-09 recurring, the instruction written and not reached -- did
    not survive reading step 13, every clause of which is scoped to regressions
    and to cases the agent wrote. **The ticket agent hit zero regressions, so
    the anchor clause asked for nothing and producing nothing was correct.**
    Reporting that as a finding would have been this instrument over-claiming
    on its first run, which is the failure mode the whole harness is built to
    avoid in others.

    So the caveat travels with the number, in the result, rather than living in
    whoever last read the code.
    """
    blob = "\n".join(
        str(x)
        for x in (harvested.get("narration"), (harvested.get("final") or {}).get("result"))
        if x
    )
    bins = re.findall(r"UNMODELED/[A-Za-z0-9_.-]+", blob)
    actions = [a for a in ACTION_RE.findall(blob) if not a.startswith(("Path.", "Self."))]
    return {
        "named_unmodeled_bin": sorted(set(bins)),
        "action_shaped_mentions": sorted(set(actions))[:40],
        "any_attribution_shape": bool(bins or actions),
        "reading": (
            "A zero here is UNDECIDED, never a failure. SKILL.md step 13 scopes "
            "its anchor clause to regressions and to cases the agent wrote, so a "
            "round with no regressions correctly produces no anchor. Read this "
            "against what the agent actually hit before concluding anything."
        ),
    }


# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fresh-evidence", action="store_true",
        help="Required acknowledgement that a new, non-overwriting evidence run is created.",
    )
    parser.add_argument("--run-id")
    parser.add_argument(
        "--role", action="append", choices=["epic", "ticket"],
        help="Run a subset. Default: both, in order -- the ticket agent needs the epic's plan.",
    )
    parser.add_argument("--source-home", type=Path, default=DEFAULT_SOURCE_HOME)
    parser.add_argument(
        "--workspace-root", type=Path,
        help="Where the agents work. Defaults to a temp dir OUTSIDE this repository.",
    )
    parser.add_argument(
        "--keep-homes", dest="keep_homes", action="store_true",
        help="Keep the cloned Skill Manager homes (~700MB each). They are removed "
             "by default; the workspace itself is ALWAYS kept.",
    )
    parser.add_argument(
        "--budget-seconds", type=float,
        help="Override every role's wall-clock budget. Use a small value to smoke-test "
             "the plumbing against a real agent without paying for a full round.",
    )
    parser.add_argument(
        "--plumbing-only", action="store_true",
        help="Build homes and workspace, skip the agent dispatch. Verifies the harness "
             "without spending a real agent.",
    )
    args = parser.parse_args()

    if not args.fresh_evidence:
        parser.error("--fresh-evidence is required; runs never overwrite prior evidence")

    run_id = args.run_id or _default_run_id()
    evidence = EVIDENCE_ROOT / run_id
    if evidence.exists():
        raise SystemExit(f"refusing to overwrite evidence {evidence}")

    # PREFLIGHT FIRST, THEN CLAIM THE RUN ID. The directory used to be created
    # here, so a refused preflight -- no `claude` on PATH, a red fixture -- left
    # an empty `evidence/runs/<id>/` behind and BURNED that id: the same
    # `--run-id` then hit "refusing to overwrite evidence" on the next attempt,
    # and the operator had to invent a new name because of a failure that
    # produced nothing.
    preflight_report = preflight(args.source_home)
    evidence.mkdir(parents=True)

    defaults, roles = _load_roles()
    wanted = args.role or ["epic", "ticket"]
    selected = [r for r in roles if r["id"] in wanted]
    selected.sort(key=lambda r: wanted.index(r["id"]))

    result: dict[str, Any] = {
        "schema_version": 1,
        "run_id": run_id,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "repo_commit": subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True, capture_output=True
        ).stdout.strip(),
        "roles": {},
        "plumbing_only": args.plumbing_only,
    }
    result["preflight"] = preflight_report

    ws_root = args.workspace_root or Path(
        tempfile.mkdtemp(prefix=f"agent-integration-{run_id}-")
    )
    ws_root.mkdir(parents=True, exist_ok=True)
    result["workspace_root"] = str(ws_root)
    print(f"workspace: {ws_root}", flush=True)
    print(f"evidence:  {evidence}", flush=True)

    started = time.perf_counter()
    try:
        workspace = build_workspace(ws_root)
        epic_home = workspace / TIER_HOME_DIRNAME

        for role in selected:
            role_dir = evidence / role["id"]
            role_dir.mkdir(parents=True, exist_ok=True)

            if role["id"] == "epic":
                cwd = workspace
                print("cloning project-tier home ...", flush=True)
                clone_report = clone_home(args.source_home, epic_home)
                home = epic_home
            else:
                # The ticket agent must receive the plan as a colleague would:
                # committed, on a branch, in its own worktree with its own home.
                _run(["git", "add", "-A"], cwd=workspace)
                commit = subprocess.run(
                    ["git", "commit", "-q", "-m", "epic: the plan, as the epic agent left it"],
                    cwd=workspace, text=True, capture_output=True,
                )
                result["roles"].setdefault("epic", {})["handoff_commit_rc"] = commit.returncode
                # H-01, the second half: BRANCH FROM WHERE THE PLAN IS.
                #
                # Round 1 branched the ticket worktree from `main` while the epic
                # agent's plan sat on `epic/shortlink-spec` -- which is where
                # `git-epic-workflow` tells an epic agent to put it. The ticket
                # agent was handed a repository whose plan was on a ref it had
                # not been pointed at, and any refusal that followed would have
                # been the harness's doing, not the toolchain's.
                base = _ref_carrying_the_plan(workspace)
                result["roles"]["epic"]["handoff_ref"] = base
                wt = ws_root / "ticket-worktree"
                _run(
                    ["git", "worktree", "add", "-q", "-b", "ticket-work", str(wt), base],
                    cwd=workspace,
                )
                cwd = wt
                print("cloning worktree-tier home ...", flush=True)
                source = epic_home if epic_home.is_dir() else args.source_home
                clone_report = clone_home(source, wt / TIER_HOME_DIRNAME)
                home = wt / TIER_HOME_DIRNAME

            entry: dict[str, Any] = result["roles"].setdefault(role["id"], {})
            entry["clone"] = clone_report
            if args.budget_seconds:
                role = {**role, "budget_seconds": args.budget_seconds}
            entry["ask"] = str(role["ask"]).strip()
            entry["predicts"] = str(role.get("predicts", "")).strip()

            if args.plumbing_only:
                entry["dispatch"] = {"status": "skipped", "reason": "--plumbing-only"}
            else:
                budget = role.get("budget_seconds", defaults.get("budget_seconds"))
                print(f"dispatching {role['id']} agent (budget {budget}s) ...", flush=True)
                entry["dispatch"] = dispatch(
                    role=role, defaults=defaults, cwd=cwd, home=home, out_dir=role_dir
                )
                entry["harvest"] = harvest(role_dir / "stream.jsonl")
                entry["attribution_probe"] = attribution_probe(entry["harvest"])

            entry["done_check"] = run_done_check(str(role["done_check"]), cwd, role_dir)
            entry["fixture"] = fixture_still_green(cwd)
            entry["workspace"] = workspace_state(cwd)
            # Written after EVERY role, not only in the outer finally. A run
            # that dies during the second seat used to leave no RESULT.json at
            # all, discarding a completed first seat that cost real money.
            (evidence / "RESULT.json").write_text(
                json.dumps(_redact(result), indent=2, default=str) + "\n",
                encoding="utf-8",
            )
            print(
                f"  {role['id']}: done_check="
                f"{'PASS' if entry['done_check']['passed'] else 'FAIL'}"
                f" toolchain_errors={entry.get('harvest', {}).get('toolchain_error_count', 'n/a')}"
                f" shell_errors={entry.get('harvest', {}).get('shell_error_count', 'n/a')}",
                flush=True,
            )
    finally:
        # A home clone is ~700MB and there are two per run. Left behind, a
        # weekly round costs a gigabyte and a half of disk that nothing in the
        # evidence refers to -- the homes are reproducible from the source home,
        # and what a reader needs is the workspace and RESULT.json. So they go
        # unless asked for. The AGENTS' WORK IS NEVER TOUCHED.
        if not args.keep_homes:
            result["reclaimed_homes"] = _drop_home_clones(ws_root)
        result["duration_seconds"] = round(time.perf_counter() - started, 3)
        result["finished_utc"] = datetime.now(timezone.utc).isoformat()
        (evidence / "RESULT.json").write_text(
            json.dumps(_redact(result), indent=2, default=str) + "\n", encoding="utf-8"
        )
        kept = "with its homes" if args.keep_homes else "homes reclaimed"
        print(f"workspace kept at {ws_root} ({kept}; delete when done)", flush=True)

    # ONLY THE SEATS THAT RAN. The ticket branch writes a `handoff_commit_rc`
    # into the epic entry, which created an `epic` row with no `done_check` --
    # so `--role ticket` alone reported `failed_roles: ["epic"]` and exited 1
    # even when the ticket seat passed. A harness that misreports a seat it was
    # not asked to run is worse than one that cannot run a subset.
    ran = {r["id"] for r in selected}
    failures = [
        rid for rid, entry in result["roles"].items()
        if rid in ran and not entry.get("done_check", {}).get("passed")
    ]
    print(json.dumps({"result": str(evidence / "RESULT.json"), "failed_roles": failures}))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
