"""THE PIN, PINNED. SI-14.

Before this, every eval run resolved its toolchain from the operator's live
home at whatever `main` pointed to that day, and **zero runs recorded the
toolchain version they ran against**. A score that moved could not be
attributed to the change that was supposed to move it.

These read configuration and cost nothing, in the shape
`test_agent_integration_harness.py` already uses for the eval suite: each one
goes red if a later edit walks back a property that was paid for once.

WHAT IS DELIBERATELY NOT ASSERTED HERE: that a *case* loads the pinned unit
through `plugins:`. It cannot today, and the reason is measured rather than
assumed -- see `test_the_suite_does_not_wire_plugins_into_a_hooked_case`.
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
EVAL_SUITE = ROOT / "evals"
LOCK = EVAL_SUITE / "lib" / "toolchain.lock.toml"
TOOLCHAIN = EVAL_SUITE / "lib" / "toolchain.py"
RUNNER = EVAL_SUITE / "run.sh"
SHIM = EVAL_SUITE / "bin" / "skill-manager"

HEX40 = re.compile(r"^[0-9a-f]{40}$")


def _units() -> dict:
    sys.path.insert(0, str(TOOLCHAIN.parent))
    import importlib.util

    spec = importlib.util.spec_from_file_location("si14_toolchain", TOOLCHAIN)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.units()


def test_the_lock_exists_and_is_in_the_repository() -> None:
    """The harness clause: the ref must appear in the REPOSITORY, not only in a
    run log. A pin that lives in a log is a description of one run."""
    assert LOCK.is_file(), (
        "no evals/lib/toolchain.lock.toml: the toolchain is again whatever the "
        "operator's home happens to hold"
    )


def test_every_pinned_unit_names_a_commit_and_never_a_branch() -> None:
    """A branch is the thing the pin exists to stop depending on.

    Measured 2026-09-19: the home's `skt` said `gitRef main, gitHash 286a3694`,
    and `main` had by then moved to `0f380781`. Five days, two different
    toolchains, one name.
    """
    units = _units()
    # NON-VACUITY: an empty lock must not pass this test by having nothing to fail.
    assert units, "the lock declares no units"
    assert len(units) >= 2, f"expected the lock to pin skt and skill-manager, got {sorted(units)}"
    for name, spec in units.items():
        assert HEX40.match(spec["commit"]), (
            f"unit {name} is pinned at {spec['commit']!r}, which is not a 40-character "
            "commit sha"
        )
        assert spec["origin"], f"unit {name} declares no origin"


def test_the_two_units_this_epic_runs_against_are_the_ones_pinned() -> None:
    units = _units()
    assert "skt" in units, "skt is not pinned; it is the unit the loop resolves from the home"
    assert "skill-manager" in units, (
        "skill-manager is not pinned; evals are supposed to run against the CLI from "
        "its epic/self-improvement-substrate branch, not the brew install"
    )


def test_the_skill_manager_shim_refuses_instead_of_falling_through(tmp_path) -> None:
    """THE REFUSAL, EXECUTED -- not grepped.

    A shim that silently execs the installed CLI when the checkout is missing
    restores the defect it exists to prevent, and does it invisibly: the run
    still scores, against code nobody is reviewing.
    """
    assert SHIM.is_file() and os.access(SHIM, os.X_OK), "no executable evals/bin/skill-manager"

    # A checkout-shaped directory with no materialised toolchain in it.
    fake = tmp_path / "evals" / "bin"
    fake.mkdir(parents=True)
    (fake / "skill-manager").write_bytes(SHIM.read_bytes())
    (fake / "skill-manager").chmod(0o755)

    proc = subprocess.run(
        [str(fake / "skill-manager"), "--version"],
        text=True, capture_output=True, timeout=120,
    )
    assert proc.returncode == 127, (
        "the shim did not refuse when nothing was materialised; it fell through "
        f"to something (rc={proc.returncode}, out={proc.stdout[:200]!r})"
    )
    assert "refusing to fall through" in proc.stderr.lower(), proc.stderr
    assert not proc.stdout.strip(), (
        "the shim wrote to stdout, which corrupts the output of the command it "
        "stands in for"
    )


def test_the_runner_consults_the_lock_and_records_what_it_used() -> None:
    """`run.sh` is the only channel: `execution.env` refuses everything but
    `EVAL_*`, so the operator's shell is where a toolchain decision can be
    made at all."""
    text = RUNNER.read_text(encoding="utf-8")
    assert "toolchain.py" in text, "the runner never materialises the pin"
    assert "toolchain.lock.toml" in text or "toolchain.py" in text
    assert "RECORD.json" in text, (
        "the runner does not stage the run record where the SessionStart hook "
        "can print it into the trace, so a score is again unattached to a toolchain"
    )


def test_the_view_excludes_the_materialised_toolchain() -> None:
    """The cache is 11,481 entries for skill-manager alone and the view's
    ceiling is 20,000. A view that swallowed the cache would be refused by the
    CLI with a message about plugin directory size, which reads as a repository
    problem rather than as this."""
    text = RUNNER.read_text(encoding="utf-8")
    assert "--exclude='./.toolchain'" in text, (
        "the staged view does not exclude the toolchain cache"
    )


def test_the_cache_is_not_inside_the_eval_dir() -> None:
    """MEASURED THE HARD WAY, by this file's own sweep going red.

    The cache lived at `evals/.toolchain` for one iteration. Case discovery is a
    recursive glob over the eval dir, and the materialised skill-manager carries
    **56 `case.yaml` files of its own** under `specs/evals/harness/evals/`. All
    56 were discovered as this suite's cases. They would have scored and billed
    as ours, with nothing in the report marking them as somebody else's.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location("si14_toolchain_cache", TOOLCHAIN)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    cache = pathlib.Path(module.DEFAULT_CACHE).resolve()
    assert EVAL_SUITE.resolve() not in cache.parents and cache != EVAL_SUITE.resolve(), (
        f"the toolchain cache {cache} is inside the eval dir {EVAL_SUITE}, so every "
        "case.yaml a materialised unit ships becomes one of this suite's cases"
    )


def test_the_suite_does_not_wire_plugins_into_a_hooked_case() -> None:
    """MEASURED, 2026-09-19, Claude Code 2.1.276, four runs, $0.26.

    A case that declares `plugins:` LOSES THE TARGET PLUGIN'S HOOKS, and still
    scores. Two cases in one probe plugin, identical but for the key:

        si14-target-noplug    hook fired   2 of 2 runs   score 1.00
        si14-target-withplug  hook fired   0 of 2 runs   score 1.00

    Both printed `Plugin under test: "p3"` AND `Plugin under test: "skt"`, so
    the target resolves -- its SessionStart hook simply does not run.

    This suite places every fixture from `lib/place.sh`, a SessionStart hook. So
    a `plugins:` entry added to any case here would hand the agent an EMPTY
    workspace and score it 0, reported as a skill failure. That is the exact
    direction this project says an instrument may not fail in, which is why the
    pinned unit is staged and recorded but not loaded through `plugins:` yet.
    """
    offenders = []
    cases = [
        c for c in sorted(EVAL_SUITE.rglob("case.yaml"))
        # Committed cases only. A materialised unit's own suite is not ours to
        # police -- and if one ever lands inside the eval dir again,
        # `test_the_cache_is_not_inside_the_eval_dir` is what says so.
        if not any(part.startswith(".") for part in c.relative_to(EVAL_SUITE).parts)
    ]
    assert cases, "NON-VACUITY: the sweep found no committed cases at all"
    for case in cases:
        text = case.read_text(encoding="utf-8")
        if re.search(r"^\s*plugins:", text, re.M):
            offenders.append(str(case.relative_to(ROOT)))
    assert not offenders, (
        "these cases declare `plugins:`, which silently disables the SessionStart "
        f"hook that places their fixture: {offenders}"
    )


def test_the_lock_is_reachable_by_the_runner_without_network(tmp_path) -> None:
    """`print-ref` reads the pin only. A run that cannot reach the network
    should still be able to say which toolchain it was SUPPOSED to use."""
    proc = subprocess.run(
        [sys.executable, str(TOOLCHAIN), "print-ref", "--unit", "skt"],
        text=True, capture_output=True, timeout=120, cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    assert HEX40.match(proc.stdout.strip()), proc.stdout


def test_a_lock_pinning_a_branch_is_refused(tmp_path) -> None:
    """The guard, executed. A lock naming `main` must not load."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("si14_toolchain_guard", TOOLCHAIN)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    bad = {"units": {"skt": {"origin": "https://example.invalid/x.git", "commit": "main"}}}
    with pytest.raises(SystemExit) as caught:
        module.units(bad)
    assert "not a 40-character commit sha" in str(caught.value)

    empty: dict = {"units": {}}
    with pytest.raises(SystemExit) as caught_empty:
        module.units(empty)
    assert "declares no units" in str(caught_empty.value)
