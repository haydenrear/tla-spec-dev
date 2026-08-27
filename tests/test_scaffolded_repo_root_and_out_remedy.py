"""#299 and #301: the scaffolded root is found by search, and --out names its remedy."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from spec_paths import SpecTreePathError, resolve_spec_tree_out  # noqa: E402


def _scaffolded_source() -> str:
    text = (REPO_ROOT / "scripts" / "onboard_program_model.py").read_text(encoding="utf-8")
    marker = "SPEC_DIR = Path(__file__).resolve().parents[1]"
    assert marker in text, "the scaffolded spec-unit test template moved"
    return text


def test_scaffold_does_not_resolve_the_repo_root_by_counting_parents() -> None:
    """#299. `REPO_ROOT = SPEC_ROOT.parent` is off by one in a ticket workspace.

    It is correct at `specs/current/tests` (`specs` -> repo root) and WRONG at
    `specs/tickets/<id>/current/tests`, where it lands on `specs/tickets`. The
    batch runner was then given `--import-root specs/tickets` and the adapter
    module every `case_adapters.toml` entry names was unimportable -- so NO
    ticket-local corpus could import its own adapters, in every repository
    using this scaffold.
    """
    text = _scaffolded_source()
    assert "REPO_ROOT = SPEC_ROOT.parent\n" not in text, (
        "the scaffold is emitting the depth-counting form again; it is off by "
        "one at ticket depth and silently breaks ticket-local corpora"
    )
    assert "def _repo_root()" in text


def test_the_scaffolded_root_search_works_at_both_depths(tmp_path: Path) -> None:
    """The property counting cannot have: one expression, two depths.

    Built as real directories rather than asserted about, because the whole
    defect was that the expression looked right at the depth its author tested.
    """
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    markers = (".git", "pyproject.toml", "Cargo.toml", "go.mod", "package.json")

    def resolve(spec_dir: Path) -> Path:
        for candidate in [spec_dir, *spec_dir.parents]:
            if any((candidate / marker).exists() for marker in markers):
                return candidate
        return spec_dir.parent.parent

    project_depth = repo / "specs" / "current"
    ticket_depth = repo / "specs" / "tickets" / "TK-01" / "current"
    for path in (project_depth, ticket_depth):
        (path / "tests").mkdir(parents=True)

    assert resolve(project_depth) == repo
    assert resolve(ticket_depth) == repo, (
        "the ticket-depth case is the one the depth-counting form got wrong"
    )
    # And the form it replaced, shown failing at exactly one of the two.
    assert project_depth.parent.parent == repo
    assert ticket_depth.parent.parent != repo


def test_the_out_refusal_names_a_valid_shape_and_a_remedy() -> None:
    """#301. The constraint was right; the error did not say what to do.

    It landed with no migration path, and the failure surfaced as a Test Graph
    node error rather than as version skew -- an epic ran with no working
    external-view graph and nobody noticed. Finding it took considerably longer
    than fixing it, and the fix was two lines.
    """
    with pytest.raises(SpecTreePathError) as caught:
        resolve_spec_tree_out(
            Path("/tmp/build/validation-reports/run-1/generated"),
            Path("/tmp/project/specs"),
        )

    message = str(caught.value)
    assert "specs/generated/<consumer>/<run-id>" in message, "no example of a VALID path"
    assert "REMEDY:" in message, "the remedy is not named"
    assert "specs/generated/testgraph/<run-id>" in message, (
        "the Test Graph case is the one that actually broke, and it is the one "
        "a reader arrives here from"
    )


def test_a_path_under_specs_is_still_accepted() -> None:
    """Guard the guard: an error message test must not mask a broken constraint."""
    resolved = resolve_spec_tree_out(Path("generated/testgraph/r1"), Path("/tmp/project/specs"))
    assert "specs" in resolved.parts
