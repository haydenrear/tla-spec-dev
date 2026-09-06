"""`specs/current` is not permanent, and two shipped commands assumed it was.

`close_tickets.py` removes `specs/current` and `specs/desired_program_model` at
workflow close -- the documented end of the desired/current loop. Between epics
neither directory exists, which is the state `main` is supposed to be in.

`tla-spec-dev run spec-unit-tests` and `run effect-conformance` both resolved
the project spec directory as `specs/current` unconditionally, so closing an
epic took both commands down with it:

    ERROR: no spec-unit pytest tests or generated case packages found for .../specs/current
    ERROR: no effect declarations found in specs/current.

`new_ticket_workflow.project_current_source` has carried the fallback for as
long as the close has removed the directory. These pin that the other two now
do too, on a tree with no `current` -- which no other test in this suite
constructs.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _module(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO_ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    import sys

    sys.modules[name] = module  # @dataclass reads sys.modules[cls.__module__]
    spec.loader.exec_module(module)
    return module


def _tree(root: Path, *, with_current: bool) -> Path:
    specs = root / "specs"
    (specs / "program_model").mkdir(parents=True)
    if with_current:
        (specs / "current").mkdir()
    return specs


def test_spec_unit_targets_fall_back_to_the_promoted_model(tmp_path) -> None:
    cli = _module("tla_spec_dev")
    closed = _tree(tmp_path / "closed", with_current=False)
    assert cli.project_spec_dir(closed).name == "program_model"

    open_workflow = _tree(tmp_path / "open", with_current=True)
    assert cli.project_spec_dir(open_workflow).name == "current", (
        "an OPEN workflow must still resolve to current, or a ticket's work is "
        "graded against the promoted model instead of the one it is changing"
    )


def test_effect_conformance_falls_back_to_the_promoted_model(tmp_path) -> None:
    report = _module("effect_conformance_report")

    import argparse

    closed = _tree(tmp_path / "closed", with_current=False)
    args = argparse.Namespace(target=None, spec_root=str(closed), ticket=None)
    assert report.resolve_spec_dir(args).name == "program_model"

    open_workflow = _tree(tmp_path / "open", with_current=True)
    args = argparse.Namespace(target=None, spec_root=str(open_workflow), ticket=None)
    assert report.resolve_spec_dir(args).name == "current"
