"""Promotion re-roots binding module references instead of copying them.

DEF-002, reported from the meta-orchestrator integration repo (#94).

`promote_semantic_files` copies `desired_program_model/` onto BOTH `current/`
and `program_model/`. A module reference inside a binding map names the tree it
lives in, so one of those two destinations always got a reference to a tree it
is not. The whole-workflow close then removes `current/`, turning the wrong half
into a reference to a package that no longer exists.

Measured in the field before the fix: 88 references across two constituents,
every one naming `specs.current.adapters` from inside a promoted
`program_model/` tree whose `current/` sibling had been deleted by the same
close. Nothing failed, because the node that would have imported them was
blocked for an unrelated reason. A binding that is never resolved cannot fail to
resolve -- which is why this needs a test at the promotion seam rather than a
downstream import check.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.close_tickets import (  # noqa: E402
    promote_semantic_files,
    reroot_module_prefixes,
    validate_equivalent,
)

BINDINGS = """\
external:
  production_package: src.thing
actions:
  DoThing:
    view: external
    adapter: specs.current.adapters:ThingAdapter
    projector: specs.current.adapters:ThingProjector
    assertion: specs.current.adapters:ProjectedStateAssertion
"""

BARE_BINDINGS = """\
actions:
  DoThing:
    adapter: adapters:ThingAdapter
"""


def _tree(root: Path, name: str, bindings: str | None = None) -> Path:
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "Core.tla").write_text("---- MODULE Core ----\n====\n", encoding="utf-8")
    if bindings is not None:
        (d / "testgraph_bindings.yml").write_text(bindings, encoding="utf-8")
    return d


# ---------------------------------------------------------------------------
# The unit
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "dst_name, expected",
    [
        ("program_model", "specs.program_model.adapters"),
        ("current", "specs.current.adapters"),
    ],
)
def test_reroot_targets_the_destination_tree(dst_name: str, expected: str) -> None:
    out, _ = reroot_module_prefixes(BINDINGS, dst_name)
    assert expected in out
    assert len([l for l in out.splitlines() if expected in l]) == 3


def test_reroot_counts_only_references_that_moved() -> None:
    """A reference already naming the destination is not a change.

    Without this the promote log would announce work on every close, including
    the ones where nothing needed rewriting, and the count would stop being
    evidence of anything.
    """
    _, moved = reroot_module_prefixes(BINDINGS, "program_model")
    assert moved == 3
    already, moved_again = reroot_module_prefixes(BINDINGS, "current")
    assert moved_again == 0
    assert already == BINDINGS


def test_bare_module_names_are_left_alone() -> None:
    """The form that cannot rot. Promotion must not invent a prefix for it."""
    out, moved = reroot_module_prefixes(BARE_BINDINGS, "program_model")
    assert out == BARE_BINDINGS
    assert moved == 0


# ---------------------------------------------------------------------------
# The seam
# ---------------------------------------------------------------------------


def test_promoting_into_program_model_reroots_and_into_current_does_not(
    tmp_path: Path,
) -> None:
    """THE DEFECT, as a round trip through the real promotion.

    One source tree, two destinations, and the reference must come out naming a
    DIFFERENT tree in each -- which a byte copy can never do.
    """
    src = _tree(tmp_path, "desired_program_model", BINDINGS)
    program = _tree(tmp_path, "program_model")
    current = _tree(tmp_path, "current")

    log = promote_semantic_files(src, program)
    promoted = (program / "testgraph_bindings.yml").read_text(encoding="utf-8")
    assert "specs.program_model.adapters" in promoted
    assert "specs.current." not in promoted
    assert any("re-rooted 3 module reference(s)" in line for line in log)

    promote_semantic_files(src, current)
    kept = (current / "testgraph_bindings.yml").read_text(encoding="utf-8")
    assert "specs.current.adapters" in kept


def test_a_promoted_reference_survives_the_deletion_of_current(tmp_path: Path) -> None:
    """The consequence, not just the substitution.

    `--remove-active` deletes `current/`. The promoted tree is what remains, and
    every module it names must still be on disk afterwards. This is the
    assertion the field defect would have failed.
    """
    src = _tree(tmp_path, "desired_program_model", BINDINGS)
    program = _tree(tmp_path, "program_model")
    (program / "adapters.py").write_text("class ThingAdapter: ...\n", encoding="utf-8")
    promote_semantic_files(src, program)

    import shutil

    shutil.rmtree(tmp_path / "current", ignore_errors=True)

    for line in (program / "testgraph_bindings.yml").read_text(encoding="utf-8").splitlines():
        if ":" not in line or "adapters:" not in line:
            continue
        module = line.split(":")[1].strip()
        if not module.startswith("specs."):
            continue
        # `tmp_path` stands in for `<repo>/specs`, so specs.program_model.adapters
        # resolves to <tmp_path>/program_model/adapters.py.
        target = tmp_path.joinpath(*module.split(".")[1:]).with_suffix(".py")
        assert target.is_file(), f"{module} names a file that does not exist: {target}"


# ---------------------------------------------------------------------------
# The negative control: closeout must still see REAL divergence
# ---------------------------------------------------------------------------


def test_closeout_treats_a_rerooted_binding_as_equivalent(tmp_path: Path) -> None:
    """Re-rooting must not make a correct promotion look like a divergence.

    Without this the fix would trade a dangling reference for a permanently
    un-closeable workflow.
    """
    src = _tree(tmp_path, "desired_program_model", BINDINGS)
    program = _tree(tmp_path, "program_model")
    promote_semantic_files(src, program)
    assert validate_equivalent(program, src, label="desired_program_model") == []


def test_closeout_still_catches_a_real_edit_to_a_binding(tmp_path: Path) -> None:
    """The half that makes the test above mean something.

    If the comparison ignored the whole file rather than only the tree prefix,
    'equivalent' would be vacuous and a genuinely diverged binding would promote
    silently.
    """
    src = _tree(tmp_path, "desired_program_model", BINDINGS)
    program = _tree(tmp_path, "program_model")
    promote_semantic_files(src, program)

    (program / "testgraph_bindings.yml").write_text(
        BINDINGS.replace("ThingAdapter", "SomeOtherAdapter").replace(
            "specs.current.", "specs.program_model."
        ),
        encoding="utf-8",
    )
    errors = validate_equivalent(program, src, label="desired_program_model")
    assert any("testgraph_bindings.yml" in e for e in errors), errors
