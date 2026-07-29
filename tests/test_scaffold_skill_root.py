"""The scaffolded modules must find THIS checkout's skill, not the operator's.

A scaffolded `adapters.py` / `providers.py` imports `spec_double_compiler`.
Under `tla-spec-dev` that import already works — the CLI puts the installed
skill on `PYTHONPATH`. A Test Graph node, a bare `pytest`, or an IDE imports
the same file with none of that, so the module has to find the skill itself.

Every repository onboarded so far hand-patched that with
`Path.home() / ".skill-manager"`, which silently defeats a per-checkout home:
a project home (`<repo>/.skill-manager`) and a worktree home
(`<worktree>/.skill-manager`) are real copies, and reaching past them to
`~/.skill-manager` loads a different build of the skill than the checkout was
resolved against — one that, from a worktree, another agent may be editing.

These tests execute the EMITTED bytes rather than a re-implementation of the
resolution order, and they assert WHICH home answered rather than merely that
the import succeeded. An exit-code-only test passes on both homes.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.scaffold_spec import parse_views, scaffold


def _plant_skill(home: Path, marker: str) -> Path:
    """Make `home` a Skill Manager home holding a labelled spec-double-compiler."""
    pkg = home / "skills" / "spec-double-compiler" / "spec_double_compiler"
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "runtime.py").write_text(
        f'MARKER = {marker!r}\n'
        "\n"
        "class CaseRunResult:\n"
        "    def __init__(self, output=None, after=None):\n"
        "        self.output = output\n"
        "        self.after = after\n"
        "\n"
        "class EffectProviderContext:\n"
        "    pass\n",
        encoding="utf-8",
    )
    return home


# Loads the scaffolded module by path — the way a Test Graph node does — then
# reports which home the transitively imported skill came from.
_PROBE = """
import importlib.util, json, sys
spec = importlib.util.spec_from_file_location("scaffolded_under_test", sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
import spec_double_compiler.runtime as runtime
print(json.dumps({"marker": runtime.MARKER, "file": runtime.__file__}))
"""


@pytest.fixture()
def planted(tmp_path: Path) -> dict[str, Path]:
    """A project checkout with its own home, plus a decoy home at $HOME.

    The decoy is a SIBLING of the project, never an ancestor, so the upward
    walk cannot reach it by accident — only `Path.home()` can.
    """
    project = tmp_path / "project"
    (project / "specs").mkdir(parents=True)
    _plant_skill(project / ".skill-manager", "project-home")

    user_home = tmp_path / "operator"
    user_home.mkdir()
    _plant_skill(user_home / ".skill-manager", "global-home")

    target = scaffold("request-flow", project / "specs", parse_views("internal,external"))
    return {"project": project, "user_home": user_home, "target": target}


def _run(module: Path, *, user_home: Path, bound_home: Path | None = None,
         explicit: Path | None = None,
         pythonpath: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = {
        k: v
        for k, v in os.environ.items()
        # Inherit none of these three: each one, left in place, would let a test
        # pass without exercising the resolver. `pythonpath=` puts PYTHONPATH
        # back DELIBERATELY — leaving it always-stripped is what hid the bug that
        # the resolution order was void whenever the module was already
        # importable.
        if k not in {"PYTHONPATH", "SKILL_MANAGER_HOME", "SPEC_DOUBLE_COMPILER_HOME"}
    }
    env["HOME"] = str(user_home)          # Path.home() honours $HOME on POSIX
    if bound_home is not None:
        env["SKILL_MANAGER_HOME"] = str(bound_home)
    if explicit is not None:
        env["SPEC_DOUBLE_COMPILER_HOME"] = str(explicit)
    if pythonpath is not None:
        env["PYTHONPATH"] = str(pythonpath)
    return subprocess.run(
        [sys.executable, "-c", _PROBE, str(module)],
        capture_output=True, text=True, env=env, cwd=str(module.parent),
    )


def _skill_root(home: Path) -> Path:
    """The importable root inside a home — what PYTHONPATH would name."""
    return home / "skills" / "spec-double-compiler"


@pytest.mark.parametrize("module_name", ["adapters.py", "providers.py"])
def test_bound_project_home_wins_over_the_operators_global_home(
    planted: dict[str, Path], module_name: str
) -> None:
    """SKILL_MANAGER_HOME beats Path.home(). This is the epic's whole point.

    Both homes hold a working `spec_double_compiler`, so an import-succeeds
    assertion passes either way. Only the marker says which one answered.
    """
    result = _run(
        planted["target"] / module_name,
        user_home=planted["user_home"],
        bound_home=planted["project"] / ".skill-manager",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["marker"] == "project-home", (
        f"{module_name} resolved the skill from {payload['file']}"
    )
    assert str(planted["user_home"]) not in payload["file"]


@pytest.mark.parametrize("module_name", ["adapters.py", "providers.py"])
def test_a_bare_shell_still_finds_the_enclosing_checkouts_home(
    planted: dict[str, Path], module_name: str
) -> None:
    """No env exported at all — the bare-shell case that issue #50 was about.

    The upward walk from the module's own path must reach
    `<project>/.skill-manager` before `Path.home()`. Without it, running a
    scaffolded node by hand reads the global home while every launch shim
    reads the project one, and the two disagree silently.
    """
    result = _run(planted["target"] / module_name, user_home=planted["user_home"])
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["marker"] == "project-home", (
        f"{module_name} resolved the skill from {payload['file']}"
    )


@pytest.mark.parametrize("module_name", ["adapters.py", "providers.py"])
def test_the_global_home_is_still_reachable_when_nothing_else_answers(
    planted: dict[str, Path], module_name: str
) -> None:
    """The negative control: without it, "project home wins" could just mean
    "the global home is never consulted", and a resolver that only ever looked
    at the project home would pass the two tests above."""
    (planted["project"] / ".skill-manager").rename(planted["project"] / ".skill-manager-off")
    result = _run(planted["target"] / module_name, user_home=planted["user_home"])
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["marker"] == "global-home"


@pytest.mark.parametrize("module_name", ["adapters.py", "providers.py"])
def test_the_bound_home_wins_over_an_inherited_pythonpath(
    planted: dict[str, Path], module_name: str
) -> None:
    """The precedence must hold when the module is ALREADY importable.

    `tla-spec-dev` hands the skill over on PYTHONPATH, so this is not an exotic
    environment — it is the documented one. While the resolver lived inside
    `except ModuleNotFoundError`, none of the four candidates was consulted here
    and the operator's global home won: measured exit 0, marker "global-home",
    empty stderr. Every other test in this file passed throughout, because they
    stripped PYTHONPATH unconditionally.
    """
    result = _run(
        planted["target"] / module_name,
        user_home=planted["user_home"],
        bound_home=planted["project"] / ".skill-manager",
        pythonpath=_skill_root(planted["user_home"] / ".skill-manager"),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["marker"] == "project-home", (
        f"{module_name} resolved the skill from {payload['file']}"
    )


@pytest.mark.parametrize("module_name", ["adapters.py", "providers.py"])
def test_an_inherited_pythonpath_answers_only_when_no_home_does(
    planted: dict[str, Path], module_name: str
) -> None:
    """Negative control for the rule above.

    Without it, "the bound home wins over PYTHONPATH" would also be satisfied by
    a resolver that ignores PYTHONPATH entirely and cannot fall back to it — a
    strictly worse module that passes the same assertion.
    """
    (planted["project"] / ".skill-manager").rename(planted["project"] / ".skill-manager-off")
    (planted["user_home"] / ".skill-manager").rename(planted["user_home"] / ".skill-manager-off")
    result = _run(
        planted["target"] / module_name,
        user_home=planted["user_home"],
        pythonpath=_skill_root(planted["user_home"] / ".skill-manager-off"),
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert payload["marker"] == "global-home"
    assert ".skill-manager-off" in payload["file"]


@pytest.mark.parametrize("module_name", ["adapters.py", "providers.py"])
def test_a_wrong_explicit_override_refuses_even_when_the_module_is_importable(
    planted: dict[str, Path], module_name: str
) -> None:
    """A misdirected override must refuse, not be bypassed by an inherited path.

    This is the same failure as the previous test in a sharper form: the refusal
    lived inside `except ModuleNotFoundError`, so a satisfied PYTHONPATH meant
    the override was never even looked at. Measured before the fix: exit 0,
    marker "global-home", empty stderr, with SPEC_DOUBLE_COMPILER_HOME pointing
    at a directory that does not exist.
    """
    result = _run(
        planted["target"] / module_name,
        user_home=planted["user_home"],
        bound_home=planted["project"] / ".skill-manager",
        explicit=planted["project"] / "nowhere-at-all",
        pythonpath=_skill_root(planted["user_home"] / ".skill-manager"),
    )
    assert result.returncode != 0
    assert "SPEC_DOUBLE_COMPILER_HOME" in result.stderr
    assert "global-home" not in result.stdout


@pytest.mark.parametrize("module_name", ["adapters.py", "providers.py"])
def test_an_explicit_override_that_is_wrong_refuses_instead_of_falling_through(
    planted: dict[str, Path], module_name: str
) -> None:
    """A misdirected override must not resolve to the global home.

    Falling through would answer "which skill did I load?" with
    `~/.skill-manager` while the operator believes they redirected it — the
    fail-open shape this resolution order exists to remove.
    """
    result = _run(
        planted["target"] / module_name,
        user_home=planted["user_home"],
        explicit=planted["project"] / "nowhere",
    )
    assert result.returncode != 0
    assert "SPEC_DOUBLE_COMPILER_HOME" in result.stderr
    assert "global-home" not in result.stdout
