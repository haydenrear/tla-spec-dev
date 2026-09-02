"""A ticket that edits its adapters must actually run them.

`open ticket` copies `case_adapters.toml` and `testgraph_bindings.yml` verbatim
into `specs/tickets/<id>/{current,desired}`. If those bindings name an adapter
module by a **view-qualified** dotted path — `specs.program_model.adapters:X` —
the name is resolved from the PROJECT ROOT and therefore means the accepted
baseline's adapters no matter which view was selected.

So a ticket that edits its own `adapters.py` **runs green without ever executing
it**: the corpus is the ticket's and the adapters are the baseline's. That is
the worst shape of green this project collects — not a missing test, but a
passing one that reports a validated change nothing ran.

Found by a real ticket agent, in `examples/agent_integration` round 001. It hit
the defect while implementing SL-1, filed it against the epic it was working as
`DEF-001` (severity major, with a reproduction and a blast radius), and its
suggested fix named this scaffold: *"consider the same in the tla-spec-dev
ticket scaffold so seeded bindings never point at another view."*

A bare `adapters:X` resolves against the SELECTED spec directory, which both
loaders put on the import path — `default_import_roots_for` adds the spec dir,
`enforce_external_channels` adds the bindings file's own directory. One
condition, asserted below because it is the half that would rot silently:
`default_import_roots_for` is skipped when `--import-root` is passed
explicitly, so a caller stating its own roots must include the spec directory.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

#: Any dotted prefix naming a specific spec TREE. It is the `specs.<tree>.`
#: shape that is wrong, not the word `program_model`: `specs.current.adapters`
#: and `specs.desired_program_model.adapters` fail the same way, and a rule
#: written against one literal would miss the other two.
VIEW_QUALIFIED = re.compile(r"\bspecs\.[A-Za-z0-9_]+\.(adapters|internal_adapters|providers)\s*:")


def _onboard():
    path = REPO_ROOT / "scripts" / "onboard_program_model.py"
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        spec = importlib.util.spec_from_file_location("onboard_program_model", path)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


def _binding_values(text: str) -> list[str]:
    """Only the VALUES of binding keys, never prose.

    The scaffold's own comments explain the hazard by quoting the wrong form,
    and a rule that scanned the whole file would flag the explanation of the
    defect as the defect. Keys are matched exactly, so a comment line — which
    begins with `#` — is never a value.
    """
    keys = ("adapter", "projector", "expected_projection", "assertion", "provider")
    values: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("#"):
            continue
        if any(line.startswith(f"{key} =") or line.startswith(f"{key}:") for key in keys):
            values.append(line)
    return values


@pytest.mark.parametrize(
    "template",
    ["case_adapters_toml", "testgraph_bindings_yml"],
)
def test_the_scaffold_never_seeds_a_view_qualified_adapter_module(template: str) -> None:
    onboard = _onboard()
    text = getattr(onboard, template)()
    offenders = [line for line in _binding_values(text) if VIEW_QUALIFIED.search(line)]
    assert not offenders, (
        f"{template}() seeds bindings that name another view's adapter module:\n  "
        + "\n  ".join(offenders)
        + "\n`open ticket` copies these verbatim, so a ticket's own adapters.py is "
        "never imported and the ticket goes green without running the change it made."
    )


@pytest.mark.parametrize("template", ["case_adapters_toml", "testgraph_bindings_yml"])
def test_the_scaffold_still_binds_something(template: str) -> None:
    """Guard the guard: a template that stopped emitting bindings would pass above."""
    onboard = _onboard()
    text = getattr(onboard, template)()
    assert _binding_values(text), f"{template}() emits no binding values at all"


def test_a_bare_name_resolves_against_the_selected_spec_directory() -> None:
    """The property the bare names depend on, asserted rather than assumed.

    If `default_import_roots_for` ever stopped adding the spec directory, every
    scaffolded project would break at once and the failure would look like a
    user error in their mapping.
    """
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    try:
        from run_generated_case_adapters import (  # type: ignore[import-not-found]
            default_import_roots_for,
        )
    finally:
        sys.path.pop(0)

    spec_dir = REPO_ROOT / "examples" / "distributed_history" / "specs" / "program_model"
    roots = default_import_roots_for(spec_dir)
    assert spec_dir in roots, (
        "the selected spec directory is not an import root, so a bare "
        "`adapters:X` binding cannot resolve to the view's own adapters"
    )
    # And the project root, so a project that DOES qualify still resolves.
    assert spec_dir.parents[1] in roots, (
        "the project root left the import roots; view-qualified bindings in "
        "existing projects would stop resolving"
    )
