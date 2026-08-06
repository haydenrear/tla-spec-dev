"""The deferment backlog is bookkeeping about the work, not part of the model.

Found finalizing the meta-orchestrator `live-stream-evals` epic, whose
`deferred_findings.yaml` held 29 settled findings at close.

`_semantic_files` classifies every `.tla`/`.cfg`/`.yaml`/`.yml` under a model
directory as part of the program model unless it is named in `PLANNING_FILES`.
`deferred_findings.yaml` was not named, so the git-epic-workflow deferment
backlog (`references/deferment.md`) counted as specification. It lives in
`desired_program_model/` and nowhere else, which made both promotion directions
destructive:

  current -> desired_program_model   the backlog is "a file the source no longer
                                     has", so promotion DELETES it. The whole
                                     ledger, at the moment the epic is being
                                     closed on the strength of it.

  desired_program_model -> program_model   (`--accept-new`) the backlog is
                                     copied into the promoted program model, as
                                     though the list of things the epic decided
                                     NOT to do were part of the program's
                                     specification.

Neither is announced as anything but an ordinary promoted file.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.close_tickets import (  # noqa: E402
    PLANNING_FILES,
    promote_semantic_files,
    validate_equivalent,
)

BACKLOG = """\
findings:
  - id: ESC-001
    disposition: carried-out-of-epic
    summary: something the epic decided not to fix
"""


def _model_dir(root: Path, name: str, *, backlog: bool = False) -> Path:
    d = root / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "Core.tla").write_text("---- MODULE Core ----\n====\n", encoding="utf-8")
    if backlog:
        (d / "deferred_findings.yaml").write_text(BACKLOG, encoding="utf-8")
    return d


def test_the_backlog_is_classified_as_planning() -> None:
    assert "deferred_findings.yaml" in PLANNING_FILES


def test_promotion_does_not_delete_the_backlog_from_the_destination(
    tmp_path: Path,
) -> None:
    """The destructive direction, and the one that would have bitten.

    `current/` never holds the backlog, so promoting current onto
    `desired_program_model/` used to remove it as an extra file.
    """
    src = _model_dir(tmp_path, "current")
    dst = _model_dir(tmp_path, "desired_program_model", backlog=True)

    log = promote_semantic_files(src, dst)

    assert (dst / "deferred_findings.yaml").is_file(), "the backlog was deleted"
    assert (dst / "deferred_findings.yaml").read_text(encoding="utf-8") == BACKLOG
    assert not any("deferred_findings" in line for line in log), log


def test_promotion_does_not_copy_the_backlog_into_the_program_model(
    tmp_path: Path,
) -> None:
    """The `--accept-new` direction.

    A promoted program model states what the program IS. A list of findings the
    epic chose not to act on is a fact about the project, and belongs to the
    epic's records rather than to the specification.
    """
    src = _model_dir(tmp_path, "desired_program_model", backlog=True)
    dst = _model_dir(tmp_path, "program_model")

    promote_semantic_files(src, dst)

    assert not (dst / "deferred_findings.yaml").exists()


def test_a_differing_backlog_does_not_block_closeout(tmp_path: Path) -> None:
    """Convergence is about the model. The backlog is expected to differ."""
    left = _model_dir(tmp_path, "program_model", backlog=True)
    right = _model_dir(tmp_path, "desired_program_model", backlog=True)
    (right / "deferred_findings.yaml").write_text(
        BACKLOG.replace("ESC-001", "ESC-002"), encoding="utf-8"
    )

    assert validate_equivalent(left, right) == []


def test_closeout_still_compares_the_actual_model(tmp_path: Path) -> None:
    """The negative control.

    Excluding the backlog must not become excluding everything, or 'the models
    converged' would be a claim nothing checks.
    """
    left = _model_dir(tmp_path, "program_model", backlog=True)
    right = _model_dir(tmp_path, "desired_program_model", backlog=True)
    (right / "Core.tla").write_text(
        "---- MODULE Core ----\nDIVERGED == TRUE\n====\n", encoding="utf-8"
    )

    errors = validate_equivalent(left, right)
    assert any("Core.tla" in e for e in errors), errors
