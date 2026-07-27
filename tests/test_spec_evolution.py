"""CM-F1: the model the complexity ledger measures is declared, not discovered.

Every test here fails on the pre-CM-01 behavior, which located the measured
model as the alphabetically first ``*.tla`` excluding ``MC*`` and paired it with
``MC.cfg`` or the alphabetically first ``*.cfg``. On a Core/Internal/External
baseline that resolved to ``Core.tla`` + ``External.cfg`` and the ledger
reported ``bound = None, modularity = 0.0`` for a module with no variables and
no actions -- a measurement of nothing that looked like a measurement.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import complexity_ledger
from scripts.spec_evolution import (
    ModelSelectionError,
    find_model_files,
    record_complexity_ledger,
    select_model_files,
    validate_model_pair,
)
from conftest import write_ticket_ledger_input


CORE = """---- MODULE Core ----
EXTENDS Naturals, FiniteSets

CONSTANTS Accounts

Status == {"none", "accepted"}
====
"""

INTERNAL = """---- MODULE Internal ----
EXTENDS Core

VARIABLES accounts
InternalVars == << accounts >>
InternalInit == accounts = {}
CreateAccount(a) == accounts' = accounts \\cup {a}
InternalNext == \\E a \\in Accounts : CreateAccount(a)
InternalInvariant == accounts \\subseteq Accounts
InternalSpec == InternalInit /\\ [][InternalNext]_InternalVars
====
"""

EXTERNAL = """---- MODULE External ----
EXTENDS Internal

CONSTANTS Clients

VARIABLES responses
ExternalVars == << accounts, responses >>
ExternalInit == InternalInit /\\ responses = [c \\in Clients |-> 0]
SubmitCreateAccount(c, a) ==
  /\\ CreateAccount(a)
  /\\ responses' = [responses EXCEPT ![c] = 1]
ExternalNext == \\E c \\in Clients, a \\in Accounts : SubmitCreateAccount(c, a)
Invariant == InternalInvariant
Spec == ExternalInit /\\ [][ExternalNext]_ExternalVars
====
"""

EXTERNAL_CFG = """SPECIFICATION Spec
INVARIANT Invariant
CONSTANTS
  Clients = {"client-1"}
  Accounts = {"acct-1"}
"""

INTERNAL_CFG = """SPECIFICATION InternalSpec
INVARIANT InternalInvariant
CONSTANTS
  Accounts = {"acct-1"}
"""


def three_module_baseline(directory: Path, *, manifest: str | None = None) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "Core.tla").write_text(CORE, encoding="utf-8")
    (directory / "Internal.tla").write_text(INTERNAL, encoding="utf-8")
    (directory / "External.tla").write_text(EXTERNAL, encoding="utf-8")
    (directory / "Internal.cfg").write_text(INTERNAL_CFG, encoding="utf-8")
    (directory / "External.cfg").write_text(EXTERNAL_CFG, encoding="utf-8")
    if manifest is not None:
        (directory / "spec_manifest.yaml").write_text(manifest, encoding="utf-8")
    return directory


def test_three_module_baseline_measures_the_outermost_view_not_core(tmp_path: Path) -> None:
    """The regression test for the shipped defect.

    Pre-fix this returned Core.tla + External.cfg, because "Core" sorts first
    and MC.cfg does not exist.
    """
    model_dir = three_module_baseline(tmp_path / "current")

    selection = select_model_files(model_dir)

    assert selection is not None
    assert selection.tla.name == "External.tla"
    assert selection.cfg.name == "External.cfg"
    assert validate_model_pair(selection) == []


def test_three_module_baseline_ledger_metrics_are_not_empty(tmp_path: Path) -> None:
    """The consequence: the ledger measured a module with nothing in it."""
    model_dir = three_module_baseline(tmp_path / "current")

    pre_fix = complexity_ledger.collect_metrics(
        model_dir / "Core.tla", model_dir / "External.cfg", None, None
    )
    assert pre_fix["variables"] == 0
    assert pre_fix["actions"] == 0
    assert pre_fix["bound"] is None

    selection = select_model_files(model_dir)
    measured = complexity_ledger.collect_metrics(
        selection.tla, selection.cfg, selection.manifest, None
    )
    assert measured["variables"] == 2
    assert measured["actions"] == 1


def test_case_module_in_the_directory_does_not_change_what_is_measured(tmp_path: Path) -> None:
    """A case module sorting before Core silently became the measured model."""
    model_dir = three_module_baseline(tmp_path / "current")
    (model_dir / "Aspect_Checkout.tla").write_text(
        "---- MODULE Aspect_Checkout ----\nEXTENDS External\n"
        "AspectNext == \\E c \\in Clients, a \\in Accounts : SubmitCreateAccount(c, a)\n"
        "AspectSpec == ExternalInit /\\ [][AspectNext]_ExternalVars\n====\n",
        encoding="utf-8",
    )
    (model_dir / "Aspect_Checkout.cfg").write_text(
        EXTERNAL_CFG.replace("SPECIFICATION Spec", "SPECIFICATION AspectSpec"), encoding="utf-8"
    )

    selection = select_model_files(model_dir)

    assert selection.tla.name == "External.tla"
    assert selection.cfg.name == "External.cfg"


def test_declared_model_block_wins_over_every_convention(tmp_path: Path) -> None:
    model_dir = three_module_baseline(
        tmp_path / "current",
        manifest="module: Whatever\nmodel:\n  tla: Internal.tla\n  cfg: Internal.cfg\n",
    )

    selection = select_model_files(model_dir)

    assert (selection.tla.name, selection.cfg.name) == ("Internal.tla", "Internal.cfg")
    assert selection.source == "declared in spec_manifest.yaml"
    assert validate_model_pair(selection) == []


def test_mismatched_pair_is_named_never_silently_measured(tmp_path: Path) -> None:
    model_dir = three_module_baseline(
        tmp_path / "current",
        manifest="module: Program\nmodel:\n  tla: Core.tla\n  cfg: External.cfg\n",
    )

    problems = validate_model_pair(select_model_files(model_dir))

    joined = "\n".join(problems)
    assert "SPECIFICATION Spec" in joined
    assert "INVARIANT Invariant" in joined
    assert "CONSTANT Clients" in joined


def test_declared_model_that_is_not_there_is_an_error(tmp_path: Path) -> None:
    model_dir = three_module_baseline(
        tmp_path / "current",
        manifest="module: Program\nmodel:\n  tla: Missing.tla\n  cfg: External.cfg\n",
    )

    with pytest.raises(ModelSelectionError) as error:
        select_model_files(model_dir)

    assert "Missing.tla" in str(error.value)


def test_half_declared_model_is_an_error(tmp_path: Path) -> None:
    model_dir = three_module_baseline(
        tmp_path / "current", manifest="module: Program\nmodel:\n  tla: External.tla\n"
    )

    with pytest.raises(ModelSelectionError):
        select_model_files(model_dir)


def test_ambiguous_directory_refuses_instead_of_picking_alphabetically(tmp_path: Path) -> None:
    model_dir = tmp_path / "current"
    model_dir.mkdir(parents=True)
    (model_dir / "Alpha.tla").write_text("---- MODULE Alpha ----\n====\n", encoding="utf-8")
    (model_dir / "Beta.tla").write_text("---- MODULE Beta ----\n====\n", encoding="utf-8")
    (model_dir / "MC.cfg").write_text("SPECIFICATION Spec\n", encoding="utf-8")

    with pytest.raises(ModelSelectionError) as error:
        select_model_files(model_dir)

    assert "Alpha.tla" in str(error.value) and "Beta.tla" in str(error.value)


def test_legacy_single_module_layout_is_unchanged(tmp_path: Path) -> None:
    model_dir = tmp_path / "current"
    model_dir.mkdir(parents=True)
    (model_dir / "Program.tla").write_text(
        "---- MODULE Program ----\nVARIABLE x\nInit == x = 0\nNext == x' = x\n"
        "Spec == Init /\\ [][Next]_x\n====\n",
        encoding="utf-8",
    )
    (model_dir / "MC.cfg").write_text("SPECIFICATION Spec\n", encoding="utf-8")
    (model_dir / "spec_manifest.yaml").write_text("module: Program\n", encoding="utf-8")

    located = find_model_files(model_dir)

    assert located is not None
    tla_path, cfg_path, manifest_path = located
    assert (tla_path.name, cfg_path.name) == ("Program.tla", "MC.cfg")
    assert manifest_path is not None


def test_empty_directory_still_reports_absence_rather_than_raising(tmp_path: Path) -> None:
    model_dir = tmp_path / "current"
    model_dir.mkdir(parents=True)

    assert select_model_files(model_dir) is None
    assert find_model_files(model_dir) is None
    assert find_model_files(tmp_path / "nope") is None


def test_close_refuses_to_record_a_ledger_entry_for_a_mismatched_pair(tmp_path: Path) -> None:
    """"I could not measure this" -- and nothing is appended to the ledger."""
    specs_dir = tmp_path / "specs"
    active_dir = specs_dir / "tickets" / "T-1"
    model_dir = three_module_baseline(
        active_dir / "current",
        manifest="module: Program\nmodel:\n  tla: Core.tla\n  cfg: External.cfg\n",
    )
    input_path = write_ticket_ledger_input(active_dir)

    with pytest.raises(SystemExit) as error:
        record_complexity_ledger(
            specs_dir,
            scope="ticket",
            scope_id="T-1",
            workflow="fixture",
            model_dir=model_dir,
            input_path=input_path,
        )

    message = str(error.value)
    assert "could not measure" in message
    assert "Core.tla + External.cfg" in message
    assert not complexity_ledger.ledger_path(specs_dir).exists()


def test_close_records_the_declared_model_it_measured(tmp_path: Path, capsys) -> None:
    specs_dir = tmp_path / "specs"
    active_dir = specs_dir / "tickets" / "T-1"
    model_dir = three_module_baseline(active_dir / "current", manifest="module: Program\n")
    input_path = write_ticket_ledger_input(active_dir)

    record = record_complexity_ledger(
        specs_dir,
        scope="ticket",
        scope_id="T-1",
        workflow="fixture",
        model_dir=model_dir,
        input_path=input_path,
    )

    assert "External.tla + External.cfg" in capsys.readouterr().out
    assert record["metrics"]["variables"] == 2
    assert record["metrics"]["actions"] == 1
